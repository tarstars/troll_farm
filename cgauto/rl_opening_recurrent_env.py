#!/usr/bin/env python3
"""NumPy/ctypes wrapper for D73's four-mode 72-feature recurrent environment."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cgauto.rl_batch_option_env import DEFAULT_LIBRARY, OPPONENTS


OPENING_RECURRENT_FEATURES = 72
OPENING_RECURRENT_ACTIONS = 4
OPENING_RECURRENT_MODES = ("balanced", "harvest", "renew", "fell")


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
class OpeningRecurrentStepInfo:
    terminals: tuple[dict | None, ...]


class OpeningRecurrentVecEnv:
    """Auto-reset D71 lifecycle observations with four ordinary batch options."""

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
        if self._lib.tf_opening_recurrent_features() != OPENING_RECURRENT_FEATURES:
            raise RuntimeError("Rust/Python opening-recurrent feature-width mismatch")
        if self._lib.tf_opening_recurrent_actions() != OPENING_RECURRENT_ACTIONS:
            raise RuntimeError("Rust/Python opening-recurrent action-width mismatch")
        if self._lib.tf_opening_recurrent_terminal_size() != ctypes.sizeof(_Terminal):
            raise RuntimeError("Rust/Python opening-recurrent terminal layout mismatch")
        self._handle = self._lib.tf_opening_recurrent_create(
            self.num_envs, self.seed_base
        )
        if not self._handle:
            raise RuntimeError("Rust opening-recurrent environment allocation failed")

        self.features = np.empty(
            (self.num_envs, OPENING_RECURRENT_FEATURES), dtype=np.float32
        )
        self.masks = np.empty(
            (self.num_envs, OPENING_RECURRENT_ACTIONS), dtype=np.uint8
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
            "tf_opening_recurrent_features",
            "tf_opening_recurrent_actions",
            "tf_opening_recurrent_terminal_size",
        ):
            getattr(self._lib, name).restype = ctypes.c_size_t
        self._lib.tf_opening_recurrent_create.argtypes = [
            ctypes.c_size_t,
            ctypes.c_int64,
        ]
        self._lib.tf_opening_recurrent_create.restype = void
        self._lib.tf_opening_recurrent_destroy.argtypes = [void]
        self._lib.tf_opening_recurrent_destroy.restype = None
        self._lib.tf_opening_recurrent_observe.argtypes = [void, void, void]
        self._lib.tf_opening_recurrent_observe.restype = ctypes.c_int32
        self._lib.tf_opening_recurrent_step.argtypes = [void] * 6
        self._lib.tf_opening_recurrent_step.restype = ctypes.c_int32

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def _terminal_ptr(self) -> ctypes.c_void_p:
        return ctypes.cast(self._terminals, ctypes.c_void_p)

    def _validate_observation(self) -> None:
        if self.features.shape != (
            self.num_envs,
            OPENING_RECURRENT_FEATURES,
        ):
            raise RuntimeError("opening-recurrent feature shape drift")
        if not np.isfinite(self.features).all():
            raise RuntimeError("non-finite opening-recurrent feature")
        if not np.all((self.masks == 0) | (self.masks == 1)):
            raise RuntimeError("non-binary opening-recurrent legal mask")
        if not np.all(self.masks[:, 0] == 1):
            raise RuntimeError("balanced opening-recurrent option must remain legal")
        legal_counts = self.masks.sum(axis=1)
        if not np.all((legal_counts == 1) | (legal_counts == 4)):
            raise RuntimeError("unexpected partial opening-recurrent legal mask")
        locked = legal_counts == 1
        if np.any(self.features[locked, 39] != 0.0):
            raise RuntimeError("locked opening-recurrent state reports a live own crop")
        if np.any(self.features[~locked, 39] != 1.0):
            raise RuntimeError("unlocked opening-recurrent state lacks a live own crop")
        if np.any(self.features[:, 56:64] != 0.0):
            raise RuntimeError("ordinary recurrent ABI reports explicit source activity")
        if np.any(self.features[:, 69] != 0.0) or np.any(
            self.features[:, 71] != 0.0
        ):
            raise RuntimeError("ordinary recurrent ABI reports source state")
        if np.any(self.features[:, 70] != 1.0):
            raise RuntimeError("ordinary recurrent ABI reports a source-action timestamp")

    def observe(self) -> tuple[np.ndarray, np.ndarray]:
        status = self._lib.tf_opening_recurrent_observe(
            self._handle, self._ptr(self.features), self._ptr(self.masks)
        )
        if status != 0:
            raise RuntimeError(f"tf_opening_recurrent_observe failed with {status}")
        self._validate_observation()
        return self.features, self.masks

    def step(
        self, selected_modes: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, OpeningRecurrentStepInfo]:
        selected_modes = np.ascontiguousarray(selected_modes, dtype=np.int32)
        if selected_modes.shape != (self.num_envs,):
            raise ValueError(
                f"expected selected mode shape {(self.num_envs,)}, "
                f"got {selected_modes.shape}"
            )
        if np.any(selected_modes < 0) or np.any(
            selected_modes >= OPENING_RECURRENT_ACTIONS
        ):
            raise ValueError("opening-recurrent mode index outside [0, 4)")
        rows = np.arange(self.num_envs)
        if np.any(self.masks[rows, selected_modes] != 1):
            raise ValueError("selected an illegal/masked opening-recurrent option")

        task_before = self.task_indices.copy()
        status = self._lib.tf_opening_recurrent_step(
            self._handle,
            self._ptr(selected_modes),
            self._ptr(self.features),
            self._ptr(self.masks),
            self._ptr(self.rewards),
            self._terminal_ptr(),
        )
        if status != 0:
            raise RuntimeError(f"tf_opening_recurrent_step failed with {status}")
        if not np.isfinite(self.rewards).all():
            raise RuntimeError("non-finite opening-recurrent reward")
        self._validate_observation()

        terminals: list[dict | None] = []
        for index, terminal in enumerate(self._terminals):
            if not terminal.done:
                terminals.append(None)
                continue
            if int(terminal.task_index) != int(task_before[index]):
                raise RuntimeError("Rust/Python opening-recurrent task-index drift")
            opponent = int(terminal.opponent)
            if opponent >= len(OPPONENTS):
                raise RuntimeError("unknown opening-recurrent opponent identifier")
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
            OpeningRecurrentStepInfo(tuple(terminals)),
        )

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_opening_recurrent_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "OpeningRecurrentVecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if hasattr(self, "_closed"):
            self.close()
