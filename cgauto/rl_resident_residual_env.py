#!/usr/bin/env python3
"""NumPy/ctypes wrapper for the exact resident residual environment."""

from __future__ import annotations

import argparse
import ctypes
from dataclasses import dataclass
import json
from pathlib import Path
import sys
import time

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.rl_level1_env import DEFAULT_LIBRARY, random_legal_actions

OBS_CHANNELS = 137
OBS_HEIGHT = 11
OBS_WIDTH = 22
OBS_SIZE = OBS_CHANNELS * OBS_HEIGHT * OBS_WIDTH
ACTION_PLANES = 13
ACTION_SIZE = ACTION_PLANES * OBS_HEIGHT * OBS_WIDTH
OPPONENTS = (
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
)


@dataclass(frozen=True)
class ResidentResidualStepInfo:
    dones: np.ndarray
    turns: np.ndarray
    returns: np.ndarray
    scenario_seeds: np.ndarray
    map_seeds: np.ndarray
    seats: np.ndarray
    opponents: np.ndarray
    margins: np.ndarray
    wood_edges: np.ndarray
    workers: np.ndarray
    opponent_workers: np.ndarray
    overrides: np.ndarray
    residual_attempts: np.ndarray
    rejected_actions: np.ndarray


class ResidentResidualVecEnv:
    def __init__(
        self,
        num_envs: int,
        seed_base: int,
        *,
        max_turns: int = 300,
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
                f"missing {self.library_path}; build the release Rust library"
            )
        self._lib = ctypes.CDLL(str(self.library_path))
        self._configure_abi()
        if self._lib.tf_resident_residual_obs_size() != OBS_SIZE:
            raise RuntimeError("Rust/Python residual observation-size mismatch")
        if self._lib.tf_resident_residual_action_size() != ACTION_SIZE:
            raise RuntimeError("Rust/Python residual action-size mismatch")
        self._handle = self._lib.tf_resident_residual_create(
            self.num_envs, ctypes.c_uint64(seed_base), max_turns
        )
        if not self._handle:
            raise RuntimeError("Rust resident-residual allocation failed")

        self.obs = np.empty(
            (self.num_envs, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.masks = np.empty(
            (self.num_envs, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
        )
        self.rewards = np.empty(self.num_envs, dtype=np.float32)
        self._dones = np.empty(self.num_envs, dtype=np.uint8)
        self._turns = np.empty(self.num_envs, dtype=np.uint16)
        self._returns = np.empty(self.num_envs, dtype=np.float32)
        self._scenario_seeds = np.empty(self.num_envs, dtype=np.uint64)
        self._map_seeds = np.empty(self.num_envs, dtype=np.uint64)
        self._seats = np.empty(self.num_envs, dtype=np.uint8)
        self._opponents = np.empty(self.num_envs, dtype=np.uint8)
        self._margins = np.empty(self.num_envs, dtype=np.int32)
        self._wood_edges = np.empty(self.num_envs, dtype=np.int32)
        self._workers = np.empty(self.num_envs, dtype=np.uint8)
        self._opponent_workers = np.empty(self.num_envs, dtype=np.uint8)
        self._overrides = np.empty(self.num_envs, dtype=np.uint16)
        self._residual_attempts = np.empty(self.num_envs, dtype=np.uint16)
        self._rejected_actions = np.empty(self.num_envs, dtype=np.uint16)
        self._closed = False
        self.observe()

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        self._lib.tf_resident_residual_obs_size.restype = ctypes.c_size_t
        self._lib.tf_resident_residual_action_size.restype = ctypes.c_size_t
        self._lib.tf_resident_residual_create.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_uint16,
        ]
        self._lib.tf_resident_residual_create.restype = void
        self._lib.tf_resident_residual_destroy.argtypes = [void]
        self._lib.tf_resident_residual_destroy.restype = None
        self._lib.tf_resident_residual_observe.argtypes = [void, void, void]
        self._lib.tf_resident_residual_observe.restype = ctypes.c_int32
        self._lib.tf_resident_residual_keep_actions.argtypes = [void, void]
        self._lib.tf_resident_residual_keep_actions.restype = ctypes.c_int32
        self._lib.tf_resident_residual_step.argtypes = [void] * 19
        self._lib.tf_resident_residual_step.restype = ctypes.c_int32

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def observe(self) -> tuple[np.ndarray, np.ndarray]:
        status = self._lib.tf_resident_residual_observe(
            self._handle, self._ptr(self.obs), self._ptr(self.masks)
        )
        if status != 0:
            raise RuntimeError(f"tf_resident_residual_observe failed with {status}")
        return self.obs, self.masks

    def keep_actions(self) -> np.ndarray:
        actions = np.empty(self.num_envs, dtype=np.int32)
        status = self._lib.tf_resident_residual_keep_actions(
            self._handle, self._ptr(actions)
        )
        if status != 0:
            raise RuntimeError(f"tf_resident_residual_keep_actions failed with {status}")
        return actions

    def step(
        self, actions: np.ndarray
    ) -> tuple[
        np.ndarray,
        np.ndarray,
        np.ndarray,
        ResidentResidualStepInfo,
    ]:
        actions = np.ascontiguousarray(actions, dtype=np.int32)
        if actions.shape != (self.num_envs,):
            raise ValueError(
                f"expected actions shape {(self.num_envs,)}, got {actions.shape}"
            )
        status = self._lib.tf_resident_residual_step(
            self._handle,
            self._ptr(actions),
            self._ptr(self.obs),
            self._ptr(self.masks),
            self._ptr(self.rewards),
            self._ptr(self._dones),
            self._ptr(self._turns),
            self._ptr(self._returns),
            self._ptr(self._scenario_seeds),
            self._ptr(self._map_seeds),
            self._ptr(self._seats),
            self._ptr(self._opponents),
            self._ptr(self._margins),
            self._ptr(self._wood_edges),
            self._ptr(self._workers),
            self._ptr(self._opponent_workers),
            self._ptr(self._overrides),
            self._ptr(self._residual_attempts),
            self._ptr(self._rejected_actions),
        )
        if status != 0:
            raise RuntimeError(f"tf_resident_residual_step failed with {status}")
        info = ResidentResidualStepInfo(
            dones=self._dones.copy(),
            turns=self._turns.copy(),
            returns=self._returns.copy(),
            scenario_seeds=self._scenario_seeds.copy(),
            map_seeds=self._map_seeds.copy(),
            seats=self._seats.copy(),
            opponents=self._opponents.copy(),
            margins=self._margins.copy(),
            wood_edges=self._wood_edges.copy(),
            workers=self._workers.copy(),
            opponent_workers=self._opponent_workers.copy(),
            overrides=self._overrides.copy(),
            residual_attempts=self._residual_attempts.copy(),
            rejected_actions=self._rejected_actions.copy(),
        )
        return self.obs, self.masks, self.rewards.copy(), info

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_resident_residual_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "ResidentResidualVecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True) is False:
            self.close()


def run_policy(
    policy: str,
    *,
    scenarios: int,
    num_envs: int,
    seed_base: int,
    random_seed: int = 71421,
    max_turns: int = 300,
) -> dict:
    if scenarios <= 0:
        raise ValueError("scenarios must be positive")
    rng = np.random.default_rng(random_seed)
    stop = seed_base + scenarios
    completed: dict[int, dict] = {}
    transitions = 0
    legal_min = ACTION_SIZE
    legal_max = 0
    keep_missing = 0
    start = time.perf_counter()
    with ResidentResidualVecEnv(
        num_envs, seed_base, max_turns=max_turns
    ) as env:
        while len(completed) < scenarios:
            keep = env.keep_actions()
            flat_masks = env.masks.reshape(num_envs, -1)
            legal_counts = flat_masks.sum(axis=1)
            legal_min = min(legal_min, int(legal_counts.min()))
            legal_max = max(legal_max, int(legal_counts.max()))
            keep_missing += int(
                sum(flat_masks[index, keep[index]] == 0 for index in range(num_envs))
            )
            if policy == "keep":
                actions = keep
            elif policy == "random":
                actions = random_legal_actions(env.masks, rng)
            else:
                raise ValueError(policy)
            _, _, _, info = env.step(actions)
            transitions += num_envs
            for index in np.flatnonzero(info.dones):
                scenario = int(info.scenario_seeds[index])
                if seed_base <= scenario < stop:
                    completed[scenario] = {
                        "scenario": scenario,
                        "map_seed": int(info.map_seeds[index]),
                        "seat": int(info.seats[index]),
                        "opponent_id": int(info.opponents[index]),
                        "opponent": OPPONENTS[int(info.opponents[index])],
                        "turn": int(info.turns[index]),
                        "return": float(info.returns[index]),
                        "margin": int(info.margins[index]),
                        "wood_edge": int(info.wood_edges[index]),
                        "workers": int(info.workers[index]),
                        "opponent_workers": int(info.opponent_workers[index]),
                        "overrides": int(info.overrides[index]),
                        "residual_attempts": int(info.residual_attempts[index]),
                        "rejected_actions": int(info.rejected_actions[index]),
                    }
    elapsed = time.perf_counter() - start
    rows = [completed[scenario] for scenario in range(seed_base, stop)]
    return {
        "schema": 1,
        "policy": policy,
        "seed_base": seed_base,
        "seed_stop_exclusive": stop,
        "scenarios": scenarios,
        "num_envs": num_envs,
        "max_turns": max_turns,
        "random_seed": random_seed if policy == "random" else None,
        "transitions": transitions,
        "elapsed_seconds": elapsed,
        "transitions_per_second": transitions / elapsed,
        "mask_legal_min": legal_min,
        "mask_legal_max": legal_max,
        "keep_missing_observations": keep_missing,
        "mean_margin": float(np.mean([row["margin"] for row in rows])),
        "mean_wood_edge": float(np.mean([row["wood_edge"] for row in rows])),
        "override_episode_rate": float(np.mean([row["overrides"] > 0 for row in rows])),
        "residual_attempt_episode_rate": float(
            np.mean([row["residual_attempts"] > 0 for row in rows])
        ),
        "rejected_actions": int(sum(row["rejected_actions"] for row in rows)),
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=("keep", "random"), required=True)
    parser.add_argument("--scenarios", type=int, default=240)
    parser.add_argument("--num-envs", type=int, default=24)
    parser.add_argument("--seed-base", type=int, default=0)
    parser.add_argument("--random-seed", type=int, default=71421)
    parser.add_argument("--max-turns", type=int, default=300)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_policy(
        args.policy,
        scenarios=args.scenarios,
        num_envs=args.num_envs,
        seed_base=args.seed_base,
        random_seed=args.random_seed,
        max_turns=args.max_turns,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
