#!/usr/bin/env python3
"""NumPy/ctypes wrapper for active-opponent Curriculum Level 5."""

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
from cgauto.rl_level2_env import LEVEL2_RECIPE_NAMES, LEVEL2_TARGETS, level2_recipe
from cgauto.rl_level3_env import LEVEL3_SCORE_GAIN
from cgauto.rl_level4_env import Level4VecEnv, summarize_rows


@dataclass(frozen=True)
class Level5StepInfo:
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
    opponent_scores: np.ndarray
    opponent_workers: np.ndarray
    opponent_created_crops: np.ndarray
    opponent_renewable_harvests: np.ndarray
    opponent_crop_destructions: np.ndarray
    opponent_training_turns: np.ndarray
    opponent_funding_deposits: np.ndarray
    opponent_second_worker_productive_actions: np.ndarray
    opponent_funded_training_events: np.ndarray
    opponent_third_worker_training_turns: np.ndarray
    opponent_third_worker_productive_actions: np.ndarray


class Level5VecEnv(Level4VecEnv):
    """Auto-reset Level-4 task against one deterministic active opponent."""

    ffi_prefix = "tf_level5"

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
        if self._obs_size() != OBS_SIZE:
            raise RuntimeError("Rust/Python observation-size mismatch")
        if self._action_size() != ACTION_SIZE:
            raise RuntimeError("Rust/Python action-size mismatch")
        if self._recipe_count() != len(LEVEL2_TARGETS):
            raise RuntimeError("Rust/Python recipe-count mismatch")
        self._handle = self._create(
            self.num_envs, ctypes.c_uint64(seed_base), max_turns
        )
        if not self._handle:
            raise RuntimeError("Rust Level-5 allocation failed")

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
        self._opponent_scores = np.empty(self.num_envs, dtype=np.int16)
        self._opponent_workers = np.empty(self.num_envs, dtype=np.uint8)
        self._opponent_created_crops = np.empty(self.num_envs, dtype=np.uint8)
        self._opponent_renewable_harvests = np.empty(self.num_envs, dtype=np.uint8)
        self._opponent_crop_destructions = np.empty(self.num_envs, dtype=np.uint8)
        self._opponent_training_turns = np.empty(self.num_envs, dtype=np.uint16)
        self._opponent_funding_deposits = np.empty(self.num_envs, dtype=np.uint8)
        self._opponent_second_worker_productive_actions = np.empty(
            self.num_envs, dtype=np.uint16
        )
        self._opponent_funded_training_events = np.empty(
            self.num_envs, dtype=np.uint8
        )
        self._opponent_third_worker_training_turns = np.empty(
            self.num_envs, dtype=np.uint16
        )
        self._opponent_third_worker_productive_actions = np.empty(
            self.num_envs, dtype=np.uint16
        )
        self._closed = False
        self.observe()

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        self._obs_size = getattr(self._lib, f"{self.ffi_prefix}_obs_size")
        self._action_size = getattr(self._lib, f"{self.ffi_prefix}_action_size")
        self._recipe_count = getattr(self._lib, f"{self.ffi_prefix}_recipe_count")
        self._create = getattr(self._lib, f"{self.ffi_prefix}_create")
        self._destroy = getattr(self._lib, f"{self.ffi_prefix}_destroy")
        self._observe = getattr(self._lib, f"{self.ffi_prefix}_observe")
        self._teacher_actions = getattr(
            self._lib, f"{self.ffi_prefix}_teacher_actions"
        )
        self._step = getattr(self._lib, f"{self.ffi_prefix}_step")
        self._obs_size.restype = ctypes.c_size_t
        self._action_size.restype = ctypes.c_size_t
        self._recipe_count.restype = ctypes.c_size_t
        self._create.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_uint16,
        ]
        self._create.restype = void
        self._destroy.argtypes = [void]
        self._destroy.restype = None
        self._observe.argtypes = [void, void, void]
        self._observe.restype = ctypes.c_int32
        self._teacher_actions.argtypes = [void, void]
        self._teacher_actions.restype = ctypes.c_int32
        self._step.argtypes = [void] * 29
        self._step.restype = ctypes.c_int32

    def observe(self) -> tuple[np.ndarray, np.ndarray]:
        status = self._observe(
            self._handle, self._ptr(self.obs), self._ptr(self.masks)
        )
        if status != 0:
            raise RuntimeError(f"tf_level5_observe failed with {status}")
        return self.obs, self.masks

    def teacher_actions(self) -> np.ndarray:
        actions = np.empty(self.num_envs, dtype=np.int32)
        status = self._teacher_actions(self._handle, self._ptr(actions))
        if status != 0:
            raise RuntimeError(f"tf_level5_teacher_actions failed with {status}")
        return actions

    def step(
        self, actions: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, Level5StepInfo]:
        actions = np.ascontiguousarray(actions, dtype=np.int32)
        if actions.shape != (self.num_envs,):
            raise ValueError(f"expected actions shape {(self.num_envs,)}, got {actions.shape}")
        status = self._step(
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
            self._ptr(self._opponent_scores),
            self._ptr(self._opponent_workers),
            self._ptr(self._opponent_created_crops),
            self._ptr(self._opponent_renewable_harvests),
            self._ptr(self._opponent_crop_destructions),
            self._ptr(self._opponent_training_turns),
            self._ptr(self._opponent_funding_deposits),
            self._ptr(self._opponent_second_worker_productive_actions),
            self._ptr(self._opponent_funded_training_events),
            self._ptr(self._opponent_third_worker_training_turns),
            self._ptr(self._opponent_third_worker_productive_actions),
        )
        if status != 0:
            raise RuntimeError(f"tf_level5_step failed with {status}")
        info = Level5StepInfo(
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
            opponent_scores=self._opponent_scores.copy(),
            opponent_workers=self._opponent_workers.copy(),
            opponent_created_crops=self._opponent_created_crops.copy(),
            opponent_renewable_harvests=self._opponent_renewable_harvests.copy(),
            opponent_crop_destructions=self._opponent_crop_destructions.copy(),
            opponent_training_turns=self._opponent_training_turns.copy(),
            opponent_funding_deposits=self._opponent_funding_deposits.copy(),
            opponent_second_worker_productive_actions=(
                self._opponent_second_worker_productive_actions.copy()
            ),
            opponent_funded_training_events=(
                self._opponent_funded_training_events.copy()
            ),
            opponent_third_worker_training_turns=(
                self._opponent_third_worker_training_turns.copy()
            ),
            opponent_third_worker_productive_actions=(
                self._opponent_third_worker_productive_actions.copy()
            ),
        )
        return self.obs, self.masks, self.rewards.copy(), info

    def close(self) -> None:
        if not self._closed:
            self._destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "Level5VecEnv":
        return self


class Level5ForagerVecEnv(Level5VecEnv):
    """Level-4 task against the deterministic no-growth natural forager."""

    ffi_prefix = "tf_level5_forager"


class Level5RecoveryVecEnv(Level5VecEnv):
    """Complete active opponent with deterministic pre-crop site recovery."""

    ffi_prefix = "tf_level5_recovery"


class Level5PlanterVecEnv(Level5VecEnv):
    """One-worker opponent that establishes and harvests a renewable crop."""

    ffi_prefix = "tf_level5_planter"


class Level5ReaperVecEnv(Level5VecEnv):
    """Regenerative planter plus one confirmed player-crop destruction."""

    ffi_prefix = "tf_level5_reaper"


class Level5FundedPairVecEnv(Level5VecEnv):
    """Naturally funded standard chopper plus deterministic two-role economy."""

    ffi_prefix = "tf_level5_funded_pair"


class Level5FundedTrioVecEnv(Level5VecEnv):
    """Two fresh funding epochs followed by a capped three-role economy."""

    ffi_prefix = "tf_level5_funded_trio"


class Level5SustainedTrioVecEnv(Level5VecEnv):
    """Funded trio with success delayed until the fixed turn-120 gate."""

    ffi_prefix = "tf_level5_funded_trio_sustained"


class Level5SustainedTrio180VecEnv(Level5VecEnv):
    """Funded trio with success delayed until the fixed turn-180 gate."""

    ffi_prefix = "tf_level5_funded_trio_sustained_180"


class Level5CropFirstSustainedTrio180VecEnv(Level5VecEnv):
    """Turn-180 funded trio that establishes renewable supply before scale."""

    ffi_prefix = "tf_level5_crop_first_funded_trio_sustained_180"


class Level5CropFirstRepeatedPressure180VecEnv(Level5VecEnv):
    """Crop-first funded trio with at most three player-crop destructions."""

    ffi_prefix = "tf_level5_crop_first_funded_trio_repeated_pressure_180"


class Level5CropFirstRepeatedPressureReacquire180VecEnv(Level5VecEnv):
    """Exact repeated-pressure task with a seed-reacquiring reference expert."""

    ffi_prefix = "tf_level5_crop_first_funded_trio_repeated_pressure_reacquire_180"


def run_policy(
    policy: str,
    *,
    episodes: int,
    num_envs: int,
    seed_base: int,
    random_seed: int = 0,
    max_turns: int = 240,
    opponent_mode: str = "complete",
) -> dict:
    rng = np.random.default_rng(random_seed)
    target_stop = seed_base + episodes
    completed: dict[int, dict] = {}
    transitions = 0
    illegal_selected_actions = 0
    start = time.perf_counter()
    env_class = {
        "complete": Level5VecEnv,
        "complete-recovery": Level5RecoveryVecEnv,
        "natural-forager": Level5ForagerVecEnv,
        "natural-planter": Level5PlanterVecEnv,
        "one-shot-reaper": Level5ReaperVecEnv,
        "funded-pair": Level5FundedPairVecEnv,
        "funded-trio": Level5FundedTrioVecEnv,
        "funded-trio-sustained": Level5SustainedTrioVecEnv,
        "funded-trio-sustained-180": Level5SustainedTrio180VecEnv,
        "crop-first-funded-trio-sustained-180": (
            Level5CropFirstSustainedTrio180VecEnv
        ),
        "crop-first-funded-trio-repeated-pressure-180": (
            Level5CropFirstRepeatedPressure180VecEnv
        ),
        "crop-first-funded-trio-repeated-pressure-reacquire-180": (
            Level5CropFirstRepeatedPressureReacquire180VecEnv
        ),
    }.get(opponent_mode)
    if env_class is None:
        raise ValueError(f"unsupported opponent mode {opponent_mode}")
    with env_class(num_envs, seed_base, max_turns=max_turns) as env:
        while len(completed) < episodes:
            if policy == "teacher":
                actions = env.teacher_actions()
            elif policy == "random":
                actions = random_legal_actions(env.masks, rng)
            else:
                raise ValueError(policy)
            flat_masks = env.masks.reshape(num_envs, ACTION_SIZE)
            illegal_selected_actions += int(
                np.count_nonzero(flat_masks[np.arange(num_envs), actions] == 0)
            )
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
                        "opponent_score": int(info.opponent_scores[index]),
                        "opponent_workers": int(info.opponent_workers[index]),
                        "opponent_created_crops": int(
                            info.opponent_created_crops[index]
                        ),
                        "opponent_renewable_harvests": int(
                            info.opponent_renewable_harvests[index]
                        ),
                        "opponent_crop_destructions": int(
                            info.opponent_crop_destructions[index]
                        ),
                        "opponent_training_turn": int(
                            info.opponent_training_turns[index]
                        ),
                        "opponent_funding_deposits": int(
                            info.opponent_funding_deposits[index]
                        ),
                        "opponent_second_worker_productive_actions": int(
                            info.opponent_second_worker_productive_actions[index]
                        ),
                        "opponent_funded_training_events": int(
                            info.opponent_funded_training_events[index]
                        ),
                        "opponent_third_worker_training_turn": int(
                            info.opponent_third_worker_training_turns[index]
                        ),
                        "opponent_third_worker_productive_actions": int(
                            info.opponent_third_worker_productive_actions[index]
                        ),
                    }
    elapsed = time.perf_counter() - start
    rows = [completed[seed] for seed in range(seed_base, target_stop)]
    material = [
        row for row in rows if row["opponent_score"] > 0 or row["opponent_workers"] > 1
    ]
    by_recipe_opponent = {}
    for recipe_id, name in enumerate(LEVEL2_RECIPE_NAMES):
        bucket = [row for row in rows if row["recipe_id"] == recipe_id]
        by_recipe_opponent[str(recipe_id)] = {
            "name": name,
            "episodes": len(bucket),
            "material_rate": (
                sum(
                    row["opponent_score"] > 0 or row["opponent_workers"] > 1
                    for row in bucket
                )
                / len(bucket)
                if bucket
                else None
            ),
            "mean_score": (
                float(np.mean([row["opponent_score"] for row in bucket]))
                if bucket
                else None
            ),
            "multiworker_rate": (
                sum(row["opponent_workers"] > 1 for row in bucket) / len(bucket)
                if bucket
                else None
            ),
        }
    return {
        "curriculum_level": 5,
        "opponent_policy": {
            "complete": "deterministic-rhea-faststate-baseline",
            "complete-recovery": "deterministic-rhea-faststate-baseline-dynamic-crop-recovery",
            "natural-forager": "deterministic-no-growth-natural-forager",
            "natural-planter": "deterministic-one-worker-natural-regenerative-planter",
            "one-shot-reaper": "deterministic-one-worker-one-shot-crop-reaper",
            "funded-pair": "deterministic-naturally-funded-two-worker-pair",
            "funded-trio": "deterministic-two-epoch-funded-three-worker-economy",
            "funded-trio-sustained": (
                "deterministic-two-epoch-funded-three-worker-economy-sustained-turn-120"
            ),
            "funded-trio-sustained-180": (
                "deterministic-two-epoch-funded-three-worker-economy-sustained-turn-180"
            ),
            "crop-first-funded-trio-sustained-180": (
                "deterministic-crop-first-funded-three-worker-economy-sustained-turn-180"
            ),
            "crop-first-funded-trio-repeated-pressure-180": (
                "deterministic-crop-first-funded-three-worker-economy-"
                "repeated-pressure-3-sustained-turn-180"
            ),
            "crop-first-funded-trio-repeated-pressure-reacquire-180": (
                "deterministic-crop-first-funded-three-worker-economy-"
                "repeated-pressure-3-seed-reacquisition-expert-turn-180"
            ),
        }[opponent_mode],
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
        "material_opponent_episodes": len(material),
        "material_opponent_rate": len(material) / len(rows),
        "mean_opponent_score": float(np.mean([row["opponent_score"] for row in rows])),
        "median_opponent_score": float(
            np.median([row["opponent_score"] for row in rows])
        ),
        "opponent_multiworker_rate": sum(
            row["opponent_workers"] > 1 for row in rows
        )
        / len(rows),
        "opponent_crop_creation_rate": sum(
            row["opponent_created_crops"] > 0 for row in rows
        )
        / len(rows),
        "opponent_renewable_harvest_rate": sum(
            row["opponent_renewable_harvests"] > 0 for row in rows
        )
        / len(rows),
        "mean_opponent_created_crops": float(
            np.mean([row["opponent_created_crops"] for row in rows])
        ),
        "mean_opponent_renewable_harvests": float(
            np.mean([row["opponent_renewable_harvests"] for row in rows])
        ),
        "opponent_crop_destruction_rate": sum(
            row["opponent_crop_destructions"] > 0 for row in rows
        )
        / len(rows),
        "opponent_crop_destruction_at_least_two_rate": sum(
            row["opponent_crop_destructions"] >= 2 for row in rows
        )
        / len(rows),
        "opponent_crop_destruction_at_least_three_rate": sum(
            row["opponent_crop_destructions"] >= 3 for row in rows
        )
        / len(rows),
        "max_opponent_crop_destructions": max(
            row["opponent_crop_destructions"] for row in rows
        ),
        "mean_opponent_crop_destructions": float(
            np.mean([row["opponent_crop_destructions"] for row in rows])
        ),
        "opponent_training_rate": sum(
            row["opponent_training_turn"] > 0 for row in rows
        )
        / len(rows),
        "median_opponent_training_turn": (
            float(
                np.median(
                    [
                        row["opponent_training_turn"]
                        for row in rows
                        if row["opponent_training_turn"] > 0
                    ]
                )
            )
            if any(row["opponent_training_turn"] > 0 for row in rows)
            else None
        ),
        "opponent_funding_receipt_rate": sum(
            row["opponent_funding_deposits"] > 0 for row in rows
        )
        / len(rows),
        "trained_with_funding_receipt_rate": (
            sum(
                row["opponent_training_turn"] > 0
                and row["opponent_funded_training_events"] >= 1
                for row in rows
            )
            / sum(row["opponent_training_turn"] > 0 for row in rows)
            if any(row["opponent_training_turn"] > 0 for row in rows)
            else None
        ),
        "opponent_second_worker_productive_rate": sum(
            row["opponent_second_worker_productive_actions"] > 0 for row in rows
        )
        / len(rows),
        "mean_opponent_second_worker_productive_actions": float(
            np.mean(
                [row["opponent_second_worker_productive_actions"] for row in rows]
            )
        ),
        "max_opponent_workers": max(row["opponent_workers"] for row in rows),
        "opponent_third_worker_training_rate": sum(
            row["opponent_third_worker_training_turn"] > 0 for row in rows
        )
        / len(rows),
        "median_opponent_third_worker_training_turn": (
            float(
                np.median(
                    [
                        row["opponent_third_worker_training_turn"]
                        for row in rows
                        if row["opponent_third_worker_training_turn"] > 0
                    ]
                )
            )
            if any(row["opponent_third_worker_training_turn"] > 0 for row in rows)
            else None
        ),
        "third_trained_with_fresh_funding_receipt_rate": (
            sum(
                row["opponent_third_worker_training_turn"] > 0
                and row["opponent_funded_training_events"] >= 2
                for row in rows
            )
            / sum(
                row["opponent_third_worker_training_turn"] > 0 for row in rows
            )
            if any(
                row["opponent_third_worker_training_turn"] > 0 for row in rows
            )
            else None
        ),
        "opponent_third_worker_productive_rate": sum(
            row["opponent_third_worker_productive_actions"] > 0 for row in rows
        )
        / len(rows),
        "mean_opponent_third_worker_productive_actions": float(
            np.mean(
                [row["opponent_third_worker_productive_actions"] for row in rows]
            )
        ),
        "mean_opponent_funded_training_events": float(
            np.mean([row["opponent_funded_training_events"] for row in rows])
        ),
        "illegal_selected_actions": illegal_selected_actions,
        "by_recipe_opponent": by_recipe_opponent,
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
    parser.add_argument("--random-seed", type=int, default=89)
    parser.add_argument("--max-turns", type=int, default=240)
    parser.add_argument(
        "--opponent-mode",
        choices=(
            "complete",
            "complete-recovery",
            "natural-forager",
            "natural-planter",
            "one-shot-reaper",
            "funded-pair",
            "funded-trio",
            "funded-trio-sustained",
            "funded-trio-sustained-180",
            "crop-first-funded-trio-sustained-180",
            "crop-first-funded-trio-repeated-pressure-180",
            "crop-first-funded-trio-repeated-pressure-reacquire-180",
        ),
        default="complete",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_policy(
        args.policy,
        episodes=args.episodes,
        num_envs=args.num_envs,
        seed_base=args.seed_base,
        random_seed=args.random_seed,
        max_turns=args.max_turns,
        opponent_mode=args.opponent_mode,
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
