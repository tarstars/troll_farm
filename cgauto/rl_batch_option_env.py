#!/usr/bin/env python3
"""NumPy/ctypes wrapper for the D62 semi-Markov batch-option environment."""

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
BATCH_OPTION_FEATURES = 56
BATCH_OPTION_ACTIONS = 4
BATCH_OPTION_MODES = ("balanced", "harvest", "renew", "fell")
OPPONENTS = (
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
    "script_boss",
    "silver_boss",
)
TASKS_PER_MAP = 2 * len(OPPONENTS)


class _Terminal(ctypes.Structure):
    _fields_ = [
        ("done", ctypes.c_uint8),
        ("seat", ctypes.c_uint8),
        ("opponent", ctypes.c_uint8),
        ("own_workers", ctypes.c_uint8),
        ("map_seed", ctypes.c_int64),
        ("task_index", ctypes.c_uint64),
        ("own_score", ctypes.c_int32),
        ("opponent_score", ctypes.c_int32),
        ("successful_trains", ctypes.c_uint8),
        ("_padding", ctypes.c_uint8),
        ("own_created_crops", ctypes.c_uint16),
        ("invalid_direct_commands", ctypes.c_uint16),
        ("provenance_failures", ctypes.c_uint16),
        ("deposit_prediction_failures", ctypes.c_uint16),
        ("invalidated_jobs", ctypes.c_uint16),
        ("action_hash", ctypes.c_uint64),
        ("state_hash", ctypes.c_uint64),
    ]


@dataclass(frozen=True)
class BatchOptionStepInfo:
    terminals: tuple[dict | None, ...]


class BatchOptionVecEnv:
    """Auto-reset vector environment with four masked batch options."""

    def __init__(
        self,
        num_envs: int,
        seed_base: int,
        *,
        library: Path | str = DEFAULT_LIBRARY,
    ) -> None:
        if num_envs <= 0:
            raise ValueError("num_envs must be positive")
        if seed_base == 0:
            raise ValueError("official map seed base must be nonzero")
        self.num_envs = int(num_envs)
        self.seed_base = int(seed_base)
        self.library_path = Path(library)
        if not self.library_path.exists():
            raise FileNotFoundError(
                f"missing {self.library_path}; run cargo build "
                "--manifest-path rust/Cargo.toml --release --lib"
            )
        self._lib = ctypes.CDLL(str(self.library_path))
        self._configure_abi()
        if self._lib.tf_batch_option_features() != BATCH_OPTION_FEATURES:
            raise RuntimeError("Rust/Python batch-option feature-width mismatch")
        if self._lib.tf_batch_option_actions() != BATCH_OPTION_ACTIONS:
            raise RuntimeError("Rust/Python batch-option action-width mismatch")
        if self._lib.tf_batch_option_terminal_size() != ctypes.sizeof(_Terminal):
            raise RuntimeError(
                "Rust/Python batch-option terminal layout mismatch: "
                f"Rust={self._lib.tf_batch_option_terminal_size()} "
                f"Python={ctypes.sizeof(_Terminal)}"
            )
        self._handle = self._lib.tf_batch_option_create(
            self.num_envs, self.seed_base
        )
        if not self._handle:
            raise RuntimeError("Rust batch-option environment allocation failed")

        self.features = np.empty(
            (self.num_envs, BATCH_OPTION_FEATURES), dtype=np.float32
        )
        self.masks = np.empty(
            (self.num_envs, BATCH_OPTION_ACTIONS), dtype=np.uint8
        )
        self.rewards = np.empty(self.num_envs, dtype=np.float32)
        self._terminals = (_Terminal * self.num_envs)()
        self.task_indices = np.arange(self.num_envs, dtype=np.uint64)
        self._next_task_index = self.num_envs
        self._closed = False
        self.observe()

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        for name in (
            "tf_batch_option_features",
            "tf_batch_option_actions",
            "tf_batch_option_terminal_size",
        ):
            getattr(self._lib, name).restype = ctypes.c_size_t
        self._lib.tf_batch_option_create.argtypes = [ctypes.c_size_t, ctypes.c_int64]
        self._lib.tf_batch_option_create.restype = void
        self._lib.tf_batch_option_destroy.argtypes = [void]
        self._lib.tf_batch_option_destroy.restype = None
        self._lib.tf_batch_option_observe.argtypes = [void, void, void]
        self._lib.tf_batch_option_observe.restype = ctypes.c_int32
        self._lib.tf_batch_option_step.argtypes = [void] * 6
        self._lib.tf_batch_option_step.restype = ctypes.c_int32

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def _terminal_ptr(self) -> ctypes.c_void_p:
        return ctypes.cast(self._terminals, ctypes.c_void_p)

    def _validate_observation(self) -> None:
        if self.features.shape != (self.num_envs, BATCH_OPTION_FEATURES):
            raise RuntimeError("batch-option feature shape drift")
        if not np.isfinite(self.features).all():
            raise RuntimeError("non-finite batch-option feature")
        if not np.all((self.masks == 0) | (self.masks == 1)):
            raise RuntimeError("non-binary batch-option legal mask")
        if not np.all(self.masks[:, 0] == 1):
            raise RuntimeError("balanced batch option must always be legal")
        legal_counts = self.masks.sum(axis=1)
        if not np.all((legal_counts == 1) | (legal_counts == BATCH_OPTION_ACTIONS)):
            raise RuntimeError("unexpected partial batch-option legal mask")
        locked = legal_counts == 1
        if np.any(self.features[locked, 39] != 0.0):
            raise RuntimeError("locked option state reports a live own crop")
        if np.any(self.features[~locked, 39] != 1.0):
            raise RuntimeError("unlocked option state lacks a live own crop")

    def observe(self) -> tuple[np.ndarray, np.ndarray]:
        status = self._lib.tf_batch_option_observe(
            self._handle, self._ptr(self.features), self._ptr(self.masks)
        )
        if status != 0:
            raise RuntimeError(f"tf_batch_option_observe failed with {status}")
        self._validate_observation()
        return self.features, self.masks

    def step(
        self, selected_modes: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, BatchOptionStepInfo]:
        selected_modes = np.ascontiguousarray(selected_modes, dtype=np.int32)
        if selected_modes.shape != (self.num_envs,):
            raise ValueError(
                f"expected selected mode shape {(self.num_envs,)}, "
                f"got {selected_modes.shape}"
            )
        if np.any(selected_modes < 0) or np.any(
            selected_modes >= BATCH_OPTION_ACTIONS
        ):
            raise ValueError("batch-option mode index outside [0, 4)")
        rows = np.arange(self.num_envs)
        if np.any(self.masks[rows, selected_modes] != 1):
            raise ValueError("selected an illegal/masked batch option")

        task_before = self.task_indices.copy()
        status = self._lib.tf_batch_option_step(
            self._handle,
            self._ptr(selected_modes),
            self._ptr(self.features),
            self._ptr(self.masks),
            self._ptr(self.rewards),
            self._terminal_ptr(),
        )
        if status != 0:
            raise RuntimeError(f"tf_batch_option_step failed with {status}")
        if not np.isfinite(self.rewards).all():
            raise RuntimeError("non-finite batch-option reward")
        self._validate_observation()

        terminals: list[dict | None] = []
        for index, terminal in enumerate(self._terminals):
            if not terminal.done:
                terminals.append(None)
                continue
            if int(terminal.task_index) != int(task_before[index]):
                raise RuntimeError("Rust/Python batch-option task-index drift")
            opponent = int(terminal.opponent)
            if opponent >= len(OPPONENTS):
                raise RuntimeError("unknown batch-option opponent identifier")
            terminals.append(
                {
                    "task_index": int(terminal.task_index),
                    "map_seed": int(terminal.map_seed),
                    "seat": int(terminal.seat),
                    "opponent": OPPONENTS[opponent],
                    "own_score": int(terminal.own_score),
                    "opponent_score": int(terminal.opponent_score),
                    "margin": int(terminal.own_score - terminal.opponent_score),
                    "own_workers": int(terminal.own_workers),
                    "successful_trains": int(terminal.successful_trains),
                    "own_created_crops": int(terminal.own_created_crops),
                    "invalid_direct_commands": int(terminal.invalid_direct_commands),
                    "provenance_failures": int(terminal.provenance_failures),
                    "deposit_prediction_failures": int(
                        terminal.deposit_prediction_failures
                    ),
                    "invalidated_jobs": int(terminal.invalidated_jobs),
                    "action_hash": int(terminal.action_hash),
                    "state_hash": int(terminal.state_hash),
                }
            )
            self.task_indices[index] = self._next_task_index
            self._next_task_index += 1
        return (
            self.features,
            self.masks,
            self.rewards.copy(),
            BatchOptionStepInfo(tuple(terminals)),
        )

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_batch_option_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "BatchOptionVecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if hasattr(self, "_closed"):
            self.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envs", type=int, default=64)
    parser.add_argument("--steps", type=int, default=256)
    parser.add_argument("--seed-base", type=int, default=9_802_000)
    args = parser.parse_args()

    started = time.perf_counter()
    transitions = episodes = unlocked = alternatives = 0
    with BatchOptionVecEnv(args.envs, args.seed_base) as env:
        rng = np.random.default_rng(6201)
        slot_returns = np.zeros(args.envs, dtype=np.float64)
        maximum_identity_error = 0.0
        for _ in range(args.steps):
            legal_counts = env.masks.sum(axis=1)
            modes = np.zeros(args.envs, dtype=np.int32)
            for slot in np.flatnonzero(legal_counts == BATCH_OPTION_ACTIONS):
                modes[slot] = rng.integers(BATCH_OPTION_ACTIONS)
            unlocked += int(np.count_nonzero(legal_counts == BATCH_OPTION_ACTIONS))
            alternatives += int(np.count_nonzero(modes))
            _, _, rewards, info = env.step(modes)
            slot_returns += rewards
            transitions += args.envs
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                episodes += 1
                maximum_identity_error = max(
                    maximum_identity_error,
                    abs(100.0 * slot_returns[slot] - terminal["margin"]),
                )
                slot_returns[slot] = 0.0
    seconds = time.perf_counter() - started
    print(
        json.dumps(
            {
                "transitions": transitions,
                "episodes": episodes,
                "unlocked": unlocked,
                "alternatives": alternatives,
                "maximum_reward_identity_error": maximum_identity_error,
                "seconds": seconds,
                "transitions_per_second": transitions / seconds,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
