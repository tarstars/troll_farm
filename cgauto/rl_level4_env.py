#!/usr/bin/env python3
"""NumPy/ctypes wrapper for randomized-recipe renewable Curriculum Level 4."""

from __future__ import annotations

import argparse
import ctypes
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cgauto.rl_level1_env import (
    ACTION_PLANES,
    ACTION_SIZE,
    DEFAULT_LIBRARY,
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_SIZE,
    OBS_WIDTH,
    random_legal_actions,
)
from cgauto.rl_level2_env import (
    LEVEL2_RECIPE_NAMES,
    LEVEL2_TARGETS,
    level2_recipe,
)
from cgauto.rl_level3_env import LEVEL3_SCORE_GAIN


@dataclass(frozen=True)
class Level4StepInfo:
    """Terminal metadata; unfinished vector slots are zero-filled."""

    dones: np.ndarray
    successes: np.ndarray
    turns: np.ndarray
    returns: np.ndarray
    seeds: np.ndarray
    heights: np.ndarray
    initial_total_deficits: np.ndarray
    training_turns: np.ndarray
    score_gains: np.ndarray
    renewable_harvests: np.ndarray
    created_crops: np.ndarray
    recipe_ids: np.ndarray
    targets: np.ndarray


class Level4VecEnv:
    """Auto-reset randomized-recipe environment with sequential joint decisions."""

    def __init__(
        self,
        num_envs: int,
        seed_base: int,
        *,
        max_turns: int = 240,
        library: Path | str = DEFAULT_LIBRARY,
    ) -> None:
        if num_envs <= 0:
            raise ValueError("num_envs must be positive")
        if not 0 < max_turns <= np.iinfo(np.uint16).max:
            raise ValueError("max_turns must fit uint16")
        self.num_envs = int(num_envs)
        self.library_path = Path(library)
        if not self.library_path.exists():
            raise FileNotFoundError(
                f"missing {self.library_path}; run "
                "cargo build --manifest-path rust/Cargo.toml --release --lib"
            )
        self._lib = ctypes.CDLL(str(self.library_path))
        self._configure_abi()
        if self._lib.tf_level4_obs_size() != OBS_SIZE:
            raise RuntimeError("Rust/Python observation-size mismatch")
        if self._lib.tf_level4_action_size() != ACTION_SIZE:
            raise RuntimeError("Rust/Python action-size mismatch")
        if self._lib.tf_level4_recipe_count() != len(LEVEL2_TARGETS):
            raise RuntimeError("Rust/Python recipe-count mismatch")
        self._handle = self._lib.tf_level4_create(
            self.num_envs, ctypes.c_uint64(seed_base), max_turns
        )
        if not self._handle:
            raise RuntimeError("Rust Level-4 allocation failed")

        self.obs = np.empty(
            (self.num_envs, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.masks = np.empty(
            (self.num_envs, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.rewards = np.empty(self.num_envs, dtype=np.float32)
        self._dones = np.empty(self.num_envs, dtype=np.uint8)
        self._successes = np.empty(self.num_envs, dtype=np.uint8)
        self._turns = np.empty(self.num_envs, dtype=np.uint16)
        self._returns = np.empty(self.num_envs, dtype=np.float32)
        self._seeds = np.empty(self.num_envs, dtype=np.uint64)
        self._heights = np.empty(self.num_envs, dtype=np.uint8)
        self._initial_total_deficits = np.empty(self.num_envs, dtype=np.uint8)
        self._training_turns = np.empty(self.num_envs, dtype=np.uint16)
        self._score_gains = np.empty(self.num_envs, dtype=np.int16)
        self._renewable_harvests = np.empty(self.num_envs, dtype=np.uint8)
        self._created_crops = np.empty(self.num_envs, dtype=np.uint8)
        self._recipe_ids = np.empty(self.num_envs, dtype=np.uint8)
        self._targets = np.empty((self.num_envs, 4), dtype=np.int8)
        self._closed = False
        self.observe()

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        self._lib.tf_level4_obs_size.restype = ctypes.c_size_t
        self._lib.tf_level4_action_size.restype = ctypes.c_size_t
        self._lib.tf_level4_recipe_count.restype = ctypes.c_size_t
        self._lib.tf_level4_create.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_uint16,
        ]
        self._lib.tf_level4_create.restype = void
        self._lib.tf_level4_destroy.argtypes = [void]
        self._lib.tf_level4_destroy.restype = None
        self._lib.tf_level4_observe.argtypes = [void, void, void]
        self._lib.tf_level4_observe.restype = ctypes.c_int32
        self._lib.tf_level4_teacher_actions.argtypes = [void, void]
        self._lib.tf_level4_teacher_actions.restype = ctypes.c_int32
        self._lib.tf_level4_step.argtypes = [void] * 18
        self._lib.tf_level4_step.restype = ctypes.c_int32

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def observe(self) -> tuple[np.ndarray, np.ndarray]:
        status = self._lib.tf_level4_observe(
            self._handle, self._ptr(self.obs), self._ptr(self.masks)
        )
        if status != 0:
            raise RuntimeError(f"tf_level4_observe failed with {status}")
        return self.obs, self.masks

    def teacher_actions(self) -> np.ndarray:
        actions = np.empty(self.num_envs, dtype=np.int32)
        status = self._lib.tf_level4_teacher_actions(self._handle, self._ptr(actions))
        if status != 0:
            raise RuntimeError(f"tf_level4_teacher_actions failed with {status}")
        return actions

    def step(
        self, actions: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, Level4StepInfo]:
        actions = np.ascontiguousarray(actions, dtype=np.int32)
        if actions.shape != (self.num_envs,):
            raise ValueError(f"expected actions shape {(self.num_envs,)}, got {actions.shape}")
        status = self._lib.tf_level4_step(
            self._handle,
            self._ptr(actions),
            self._ptr(self.obs),
            self._ptr(self.masks),
            self._ptr(self.rewards),
            self._ptr(self._dones),
            self._ptr(self._successes),
            self._ptr(self._turns),
            self._ptr(self._returns),
            self._ptr(self._seeds),
            self._ptr(self._heights),
            self._ptr(self._initial_total_deficits),
            self._ptr(self._training_turns),
            self._ptr(self._score_gains),
            self._ptr(self._renewable_harvests),
            self._ptr(self._created_crops),
            self._ptr(self._recipe_ids),
            self._ptr(self._targets),
        )
        if status != 0:
            raise RuntimeError(f"tf_level4_step failed with {status}")
        info = Level4StepInfo(
            dones=self._dones.copy(),
            successes=self._successes.copy(),
            turns=self._turns.copy(),
            returns=self._returns.copy(),
            seeds=self._seeds.copy(),
            heights=self._heights.copy(),
            initial_total_deficits=self._initial_total_deficits.copy(),
            training_turns=self._training_turns.copy(),
            score_gains=self._score_gains.copy(),
            renewable_harvests=self._renewable_harvests.copy(),
            created_crops=self._created_crops.copy(),
            recipe_ids=self._recipe_ids.copy(),
            targets=self._targets.copy(),
        )
        return self.obs, self.masks, self.rewards.copy(), info

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_level4_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "Level4VecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True) is False:
            self.close()


def summarize_rows(rows: list[dict]) -> dict:
    successes = [row for row in rows if row["success"]]
    by_height = {}
    for height in sorted({row["height"] for row in rows}):
        bucket = [row for row in rows if row["height"] == height]
        count = sum(row["success"] for row in bucket)
        by_height[str(height)] = {
            "episodes": len(bucket),
            "successes": count,
            "success_rate": count / len(bucket),
        }
    by_recipe = {}
    for recipe_id, name in enumerate(LEVEL2_RECIPE_NAMES):
        bucket = [row for row in rows if row["recipe_id"] == recipe_id]
        count = sum(row["success"] for row in bucket)
        by_recipe[str(recipe_id)] = {
            "name": name,
            "target": list(LEVEL2_TARGETS[recipe_id]),
            "episodes": len(bucket),
            "successes": count,
            "success_rate": count / len(bucket) if bucket else None,
            "created_crop_rate": (
                sum(row["created_crop"] for row in bucket) / len(bucket)
                if bucket
                else None
            ),
            "renewable_harvest_rate": (
                sum(row["renewable_harvests"] > 0 for row in bucket) / len(bucket)
                if bucket
                else None
            ),
        }
    nontrivial = [row for row in rows if row["initial_total_deficit"] > 0]
    return {
        "successes": len(successes),
        "success_rate": len(successes) / len(rows),
        "median_success_turn": (
            float(np.median([row["turns"] for row in successes])) if successes else None
        ),
        "median_training_turn": (
            float(np.median([row["training_turn"] for row in rows if row["training_turn"]]))
            if any(row["training_turn"] for row in rows)
            else None
        ),
        "nontrivial_episodes": len(nontrivial),
        "nontrivial_successes": sum(row["success"] for row in nontrivial),
        "nontrivial_success_rate": (
            sum(row["success"] for row in nontrivial) / len(nontrivial)
            if nontrivial
            else None
        ),
        "height_success_floor": min(
            bucket["success_rate"] for bucket in by_height.values()
        ),
        "recipe_success_floor": min(
            bucket["success_rate"]
            for bucket in by_recipe.values()
            if bucket["episodes"]
        ),
        "created_crop_rate": sum(row["created_crop"] for row in rows) / len(rows),
        "renewable_harvest_rate": sum(
            row["renewable_harvests"] > 0 for row in rows
        )
        / len(rows),
        "median_score_gain": float(np.median([row["score_gain"] for row in rows])),
        "by_height": by_height,
        "by_recipe": by_recipe,
    }


def run_policy(
    policy: str,
    *,
    episodes: int,
    num_envs: int,
    seed_base: int,
    random_seed: int = 0,
    max_turns: int = 240,
) -> dict:
    rng = np.random.default_rng(random_seed)
    target_stop = seed_base + episodes
    completed: dict[int, dict] = {}
    transitions = 0
    start = time.perf_counter()
    with Level4VecEnv(num_envs, seed_base, max_turns=max_turns) as env:
        while len(completed) < episodes:
            if policy == "teacher":
                actions = env.teacher_actions()
            elif policy == "random":
                actions = random_legal_actions(env.masks, rng)
            else:
                raise ValueError(policy)
            _, _, _, info = env.step(actions)
            transitions += num_envs
            for index in np.flatnonzero(info.dones):
                seed = int(info.seeds[index])
                if seed_base <= seed < target_stop:
                    recipe_id = int(info.recipe_ids[index])
                    target = tuple(int(value) for value in info.targets[index])
                    expected_id, expected_target = level2_recipe(seed)
                    if (recipe_id, target) != (expected_id, expected_target):
                        raise RuntimeError(f"terminal recipe mismatch for seed {seed}")
                    completed[seed] = {
                        "seed": seed,
                        "success": bool(info.successes[index]),
                        "turns": int(info.turns[index]),
                        "return": float(info.returns[index]),
                        "height": int(info.heights[index]),
                        "initial_total_deficit": int(
                            info.initial_total_deficits[index]
                        ),
                        "training_turn": int(info.training_turns[index]),
                        "score_gain": int(info.score_gains[index]),
                        "renewable_harvests": int(info.renewable_harvests[index]),
                        "created_crop": bool(info.created_crops[index]),
                        "recipe_id": recipe_id,
                        "recipe_name": LEVEL2_RECIPE_NAMES[recipe_id],
                        "target": list(target),
                    }
    elapsed = time.perf_counter() - start
    rows = [completed[seed] for seed in range(seed_base, target_stop)]
    return {
        "curriculum_level": 4,
        "recipe_catalog": [list(target) for target in LEVEL2_TARGETS],
        "required_score_gain": LEVEL3_SCORE_GAIN,
        "policy": policy,
        "seed_base": seed_base,
        "seed_stop_exclusive": target_stop,
        "exact_seed_interval": True,
        "episodes": episodes,
        "num_envs": num_envs,
        "max_turns": max_turns,
        **summarize_rows(rows),
        "transitions": transitions,
        "elapsed_seconds": elapsed,
        "transitions_per_second": transitions / elapsed,
        "episodes_detail": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=("teacher", "random"), default="teacher")
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--num-envs", type=int, default=100)
    parser.add_argument("--seed-base", type=int, default=0)
    parser.add_argument("--random-seed", type=int, default=83)
    parser.add_argument("--max-turns", type=int, default=240)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_policy(
        args.policy,
        episodes=args.episodes,
        num_envs=args.num_envs,
        seed_base=args.seed_base,
        random_seed=args.random_seed,
        max_turns=args.max_turns,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "episodes_detail"},
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
