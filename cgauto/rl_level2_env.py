#!/usr/bin/env python3
"""NumPy/ctypes wrapper for randomized-recipe curriculum Level 2."""

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


LEVEL2_RECIPE_NAMES = (
    "cheap-planter",
    "compact-farmer",
    "balanced-producer",
    "harvest-producer",
    "level1-anchor",
    "lean-chopper",
    "standard-chopper",
    "hybrid-chopper",
)
LEVEL2_TARGETS = (
    (1, 1, 1, 1),
    (1, 2, 1, 1),
    (2, 2, 1, 1),
    (2, 2, 2, 1),
    (1, 3, 0, 1),
    (1, 2, 0, 2),
    (2, 2, 0, 2),
    (2, 3, 1, 2),
)
RECIPE_XOR = 0x4C32726563697065
MASK64 = (1 << 64) - 1


def level2_recipe(seed: int) -> tuple[int, tuple[int, int, int, int]]:
    """Mirror the frozen Rust SplitMix64 recipe assignment."""

    value = (int(seed) ^ RECIPE_XOR) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    value ^= value >> 31
    recipe_id = value % len(LEVEL2_TARGETS)
    return recipe_id, LEVEL2_TARGETS[recipe_id]


@dataclass(frozen=True)
class Level2StepInfo:
    """Terminal metadata; zero-filled entries correspond to unfinished slots."""

    dones: np.ndarray
    successes: np.ndarray
    turns: np.ndarray
    returns: np.ndarray
    seeds: np.ndarray
    heights: np.ndarray
    recipe_ids: np.ndarray
    initial_total_deficits: np.ndarray
    targets: np.ndarray


class Level2VecEnv:
    """Batched auto-reset environment with a deterministic random recipe per seed."""

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
        if self._lib.tf_level2_obs_size() != OBS_SIZE:
            raise RuntimeError("Rust/Python observation-size mismatch")
        if self._lib.tf_level2_action_size() != ACTION_SIZE:
            raise RuntimeError("Rust/Python action-size mismatch")
        if self._lib.tf_level2_recipe_count() != len(LEVEL2_TARGETS):
            raise RuntimeError("Rust/Python recipe-count mismatch")
        self._handle = self._lib.tf_level2_create(
            self.num_envs, ctypes.c_uint64(seed_base), max_turns
        )
        if not self._handle:
            raise RuntimeError("Rust environment allocation failed")

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
        self._recipe_ids = np.empty(self.num_envs, dtype=np.uint8)
        self._initial_total_deficits = np.empty(self.num_envs, dtype=np.uint8)
        self._targets = np.empty((self.num_envs, 4), dtype=np.int8)
        self._closed = False
        self.observe()

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        self._lib.tf_level2_obs_size.restype = ctypes.c_size_t
        self._lib.tf_level2_action_size.restype = ctypes.c_size_t
        self._lib.tf_level2_recipe_count.restype = ctypes.c_size_t
        self._lib.tf_level2_create.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_uint16,
        ]
        self._lib.tf_level2_create.restype = void
        self._lib.tf_level2_destroy.argtypes = [void]
        self._lib.tf_level2_destroy.restype = None
        self._lib.tf_level2_observe.argtypes = [void, void, void]
        self._lib.tf_level2_observe.restype = ctypes.c_int32
        self._lib.tf_level2_teacher_actions.argtypes = [void, void]
        self._lib.tf_level2_teacher_actions.restype = ctypes.c_int32
        self._lib.tf_level2_step.argtypes = [void] * 14
        self._lib.tf_level2_step.restype = ctypes.c_int32

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def observe(self) -> tuple[np.ndarray, np.ndarray]:
        status = self._lib.tf_level2_observe(
            self._handle, self._ptr(self.obs), self._ptr(self.masks)
        )
        if status != 0:
            raise RuntimeError(f"tf_level2_observe failed with {status}")
        return self.obs, self.masks

    def teacher_actions(self) -> np.ndarray:
        actions = np.empty(self.num_envs, dtype=np.int32)
        status = self._lib.tf_level2_teacher_actions(self._handle, self._ptr(actions))
        if status != 0:
            raise RuntimeError(f"tf_level2_teacher_actions failed with {status}")
        return actions

    def step(
        self, actions: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, Level2StepInfo]:
        actions = np.ascontiguousarray(actions, dtype=np.int32)
        if actions.shape != (self.num_envs,):
            raise ValueError(f"expected actions shape {(self.num_envs,)}, got {actions.shape}")
        status = self._lib.tf_level2_step(
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
            self._ptr(self._recipe_ids),
            self._ptr(self._initial_total_deficits),
            self._ptr(self._targets),
        )
        if status != 0:
            raise RuntimeError(f"tf_level2_step failed with {status}")
        info = Level2StepInfo(
            dones=self._dones.copy(),
            successes=self._successes.copy(),
            turns=self._turns.copy(),
            returns=self._returns.copy(),
            seeds=self._seeds.copy(),
            heights=self._heights.copy(),
            recipe_ids=self._recipe_ids.copy(),
            initial_total_deficits=self._initial_total_deficits.copy(),
            targets=self._targets.copy(),
        )
        return self.obs, self.masks, self.rewards.copy(), info

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_level2_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "Level2VecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True) is False:
            self.close()


def summarize_rows(rows: list[dict]) -> dict:
    successes = [row for row in rows if row["success"]]
    by_recipe: dict[str, dict] = {}
    for recipe_id, name in enumerate(LEVEL2_RECIPE_NAMES):
        bucket = [row for row in rows if row["recipe_id"] == recipe_id]
        count = sum(row["success"] for row in bucket)
        by_recipe[str(recipe_id)] = {
            "name": name,
            "target": list(LEVEL2_TARGETS[recipe_id]),
            "episodes": len(bucket),
            "successes": count,
            "success_rate": count / len(bucket) if bucket else None,
            "median_success_turn": (
                float(np.median([row["turns"] for row in bucket if row["success"]]))
                if count
                else None
            ),
        }
    by_height = {}
    for height in sorted({row["height"] for row in rows}):
        bucket = [row for row in rows if row["height"] == height]
        count = sum(row["success"] for row in bucket)
        by_height[str(height)] = {
            "episodes": len(bucket),
            "successes": count,
            "success_rate": count / len(bucket),
        }
    nontrivial = [row for row in rows if row["initial_total_deficit"] > 0]
    return {
        "successes": len(successes),
        "success_rate": len(successes) / len(rows),
        "median_success_turn": (
            float(np.median([row["turns"] for row in successes])) if successes else None
        ),
        "nontrivial_episodes": len(nontrivial),
        "nontrivial_successes": sum(row["success"] for row in nontrivial),
        "nontrivial_success_rate": (
            sum(row["success"] for row in nontrivial) / len(nontrivial)
            if nontrivial
            else None
        ),
        "by_recipe": by_recipe,
        "by_height": by_height,
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
    with Level2VecEnv(num_envs, seed_base, max_turns=max_turns) as env:
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
                        "recipe_id": recipe_id,
                        "recipe_name": LEVEL2_RECIPE_NAMES[recipe_id],
                        "target": list(target),
                        "initial_total_deficit": int(info.initial_total_deficits[index]),
                    }
    elapsed = time.perf_counter() - start
    rows = [completed[seed] for seed in range(seed_base, target_stop)]
    return {
        "curriculum_level": 2,
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
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--num-envs", type=int, default=100)
    parser.add_argument("--seed-base", type=int, default=2_003_000)
    parser.add_argument("--random-seed", type=int, default=61)
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
    summary = {key: value for key, value in result.items() if key != "episodes_detail"}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
