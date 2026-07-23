#!/usr/bin/env python3
"""NumPy/ctypes wrapper for the Rust curriculum Level-1 vector environment."""

from __future__ import annotations

import argparse
import ctypes
import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY = ROOT / "rust" / "target" / "release" / "libtroll_farm.so"
OBS_CHANNELS = 104
OBS_HEIGHT = 11
OBS_WIDTH = 22
ACTION_PLANES = 13
OBS_SIZE = OBS_CHANNELS * OBS_HEIGHT * OBS_WIDTH
ACTION_SIZE = ACTION_PLANES * OBS_HEIGHT * OBS_WIDTH


@dataclass(frozen=True)
class StepInfo:
    """Terminal metadata; zero-filled entries correspond to unfinished slots."""

    dones: np.ndarray
    successes: np.ndarray
    turns: np.ndarray
    returns: np.ndarray
    seeds: np.ndarray
    heights: np.ndarray
    initial_deficits: np.ndarray


class Level1VecEnv:
    """Batched auto-reset environment backed by one persistent Rust allocation."""

    def __init__(
        self,
        num_envs: int,
        seed_base: int,
        *,
        max_turns: int = 180,
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
        if self._lib.tf_level1_obs_size() != OBS_SIZE:
            raise RuntimeError("Rust/Python observation-size mismatch")
        if self._lib.tf_level1_action_size() != ACTION_SIZE:
            raise RuntimeError("Rust/Python action-size mismatch")
        self._handle = self._lib.tf_level1_create(
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
        self._initial_deficits = np.empty(self.num_envs, dtype=np.uint8)
        self._closed = False
        self.observe()

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        self._lib.tf_level1_obs_size.restype = ctypes.c_size_t
        self._lib.tf_level1_action_size.restype = ctypes.c_size_t
        self._lib.tf_level1_create.argtypes = [
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_uint16,
        ]
        self._lib.tf_level1_create.restype = void
        self._lib.tf_level1_destroy.argtypes = [void]
        self._lib.tf_level1_destroy.restype = None
        self._lib.tf_level1_observe.argtypes = [void, void, void]
        self._lib.tf_level1_observe.restype = ctypes.c_int32
        self._lib.tf_level1_teacher_actions.argtypes = [void, void]
        self._lib.tf_level1_teacher_actions.restype = ctypes.c_int32
        self._lib.tf_level1_step.argtypes = [void] * 12
        self._lib.tf_level1_step.restype = ctypes.c_int32

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def observe(self) -> tuple[np.ndarray, np.ndarray]:
        status = self._lib.tf_level1_observe(
            self._handle, self._ptr(self.obs), self._ptr(self.masks)
        )
        if status != 0:
            raise RuntimeError(f"tf_level1_observe failed with {status}")
        return self.obs, self.masks

    def teacher_actions(self) -> np.ndarray:
        actions = np.empty(self.num_envs, dtype=np.int32)
        status = self._lib.tf_level1_teacher_actions(
            self._handle, self._ptr(actions)
        )
        if status != 0:
            raise RuntimeError(f"tf_level1_teacher_actions failed with {status}")
        return actions

    def step(self, actions: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, StepInfo]:
        actions = np.ascontiguousarray(actions, dtype=np.int32)
        if actions.shape != (self.num_envs,):
            raise ValueError(f"expected actions shape {(self.num_envs,)}, got {actions.shape}")
        status = self._lib.tf_level1_step(
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
            self._ptr(self._initial_deficits),
        )
        if status != 0:
            raise RuntimeError(f"tf_level1_step failed with {status}")
        info = StepInfo(
            dones=self._dones.copy(),
            successes=self._successes.copy(),
            turns=self._turns.copy(),
            returns=self._returns.copy(),
            seeds=self._seeds.copy(),
            heights=self._heights.copy(),
            initial_deficits=self._initial_deficits.copy(),
        )
        return self.obs, self.masks, self.rewards.copy(), info

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_level1_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "Level1VecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True) is False:
            self.close()


def random_legal_actions(masks: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Uniformly sample one legal flattened action per environment."""

    flat = masks.reshape(masks.shape[0], -1)
    out = np.empty(flat.shape[0], dtype=np.int32)
    for index, row in enumerate(flat):
        legal = np.flatnonzero(row)
        if not len(legal):
            raise RuntimeError(f"empty action mask in slot {index}")
        out[index] = legal[rng.integers(len(legal))]
    return out


def run_policy(
    policy: str,
    *,
    episodes: int,
    num_envs: int,
    seed_base: int,
    random_seed: int = 0,
) -> dict:
    rng = np.random.default_rng(random_seed)
    target_stop = seed_base + episodes
    completed: dict[int, dict] = {}
    transitions = 0
    start = time.perf_counter()
    with Level1VecEnv(num_envs, seed_base) as env:
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
                    completed[seed] = {
                        "seed": seed,
                        "success": bool(info.successes[index]),
                        "turns": int(info.turns[index]),
                        "return": float(info.returns[index]),
                        "height": int(info.heights[index]),
                        "initial_deficit": int(info.initial_deficits[index]),
                    }
    elapsed = time.perf_counter() - start
    rows = [completed[seed] for seed in range(seed_base, target_stop)]
    successes = [row for row in rows if row["success"]]
    by_height = {}
    for height in sorted({row["height"] for row in rows}):
        bucket = [row for row in rows if row["height"] == height]
        by_height[str(height)] = {
            "episodes": len(bucket),
            "success_rate": sum(row["success"] for row in bucket) / len(bucket),
        }
    return {
        "policy": policy,
        "seed_base": seed_base,
        "seed_stop_exclusive": target_stop,
        "exact_seed_interval": True,
        "episodes": episodes,
        "num_envs": num_envs,
        "successes": len(successes),
        "success_rate": len(successes) / episodes,
        "median_success_turn": (
            float(np.median([row["turns"] for row in successes])) if successes else None
        ),
        "transitions": transitions,
        "elapsed_seconds": elapsed,
        "transitions_per_second": transitions / elapsed,
        "by_height": by_height,
        "episodes_detail": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=("teacher", "random"), default="teacher")
    parser.add_argument("--episodes", type=int, default=1000)
    parser.add_argument("--num-envs", type=int, default=64)
    parser.add_argument("--seed-base", type=int, default=2_000_000)
    parser.add_argument("--random-seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_policy(
        args.policy,
        episodes=args.episodes,
        num_envs=args.num_envs,
        seed_base=args.seed_base,
        random_seed=args.random_seed,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n")
    summary = {key: value for key, value in result.items() if key != "episodes_detail"}
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
