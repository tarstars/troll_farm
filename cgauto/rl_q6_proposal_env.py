#!/usr/bin/env python3
"""NumPy/ctypes wrapper for D108's masked q6 proposal environment."""

from __future__ import annotations

import csv
import ctypes
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cgauto.rl_macro_env import DEFAULT_LIBRARY, OPPONENTS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERTS = (
    ROOT
    / "data"
    / "analysis"
    / "live-agent-6553250"
    / "d105a-q6-expert-population.tsv"
)
Q6_EXPERTS = 64
Q6_EXPERT_FEATURES = 153
Q6_ACTIONS = 65
Q6_ACTION_FEATURES = 379
Q6_STATE_FEATURES = 64
Q6_INTERVENTION_BUDGET = 4


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
        ("baseline_own_score", ctypes.c_int32),
        ("baseline_opponent_score", ctypes.c_int32),
        ("successful_trains", ctypes.c_uint8),
        ("intervention_batches", ctypes.c_uint8),
        ("boundary_decisions", ctypes.c_uint16),
        ("joint_batches", ctypes.c_uint16),
        ("noncontrol_assignments", ctypes.c_uint16),
        ("own_created_crops", ctypes.c_uint16),
        ("invalid_direct_commands", ctypes.c_uint16),
        ("provenance_failures", ctypes.c_uint16),
        ("deposit_prediction_failures", ctypes.c_uint16),
        ("invalidated_jobs", ctypes.c_uint16),
        ("action_hash", ctypes.c_uint64),
        ("state_hash", ctypes.c_uint64),
    ]


@dataclass(frozen=True)
class Q6ProposalStepInfo:
    terminals: tuple[dict | None, ...]


def load_experts(path: Path | str = DEFAULT_EXPERTS) -> np.ndarray:
    path = Path(path)
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        expected = ["policy", "kind", "budget"] + [
            f"param_{index:03d}" for index in range(Q6_EXPERT_FEATURES)
        ]
        if list(reader.fieldnames or ()) != expected:
            raise RuntimeError("q6 expert population schema mismatch")
        rows = [row for row in reader if row["kind"] == "four"]
    if [row["policy"] for row in rows] != [f"four_{index:02d}" for index in range(Q6_EXPERTS)]:
        raise RuntimeError("q6 expert population ordering mismatch")
    if any(int(row["budget"]) != 4 for row in rows):
        raise RuntimeError("q6 expert population budget mismatch")
    result = np.asarray(
        [
            [float(row[f"param_{index:03d}"]) for index in range(Q6_EXPERT_FEATURES)]
            for row in rows
        ],
        dtype=np.float32,
    )
    if result.shape != (Q6_EXPERTS, Q6_EXPERT_FEATURES) or not np.isfinite(result).all():
        raise RuntimeError("invalid q6 expert matrix")
    return np.ascontiguousarray(result)


class Q6ProposalVecEnv:
    """Auto-reset paired-return environments with dynamic q6 proposal masks."""

    def __init__(
        self,
        num_envs: int,
        seed_base: int,
        *,
        map_pool: int,
        library: Path | str = DEFAULT_LIBRARY,
        experts: Path | str = DEFAULT_EXPERTS,
    ) -> None:
        if num_envs <= 0:
            raise ValueError("num_envs must be positive")
        if seed_base == 0:
            raise ValueError("official map seed base must be nonzero")
        if map_pool <= 0:
            raise ValueError("map_pool must be positive")
        self.num_envs = int(num_envs)
        self.seed_base = int(seed_base)
        self.map_pool = int(map_pool)
        self.library_path = Path(library)
        if not self.library_path.exists():
            raise FileNotFoundError(
                f"missing {self.library_path}; run cargo build "
                "--manifest-path rust/Cargo.toml --release --lib"
            )
        self.expert_weights = load_experts(experts)
        self._lib = ctypes.CDLL(str(self.library_path))
        self._configure_abi()
        expected = {
            "tf_q6_state_features": Q6_STATE_FEATURES,
            "tf_q6_actions": Q6_ACTIONS,
            "tf_q6_action_features": Q6_ACTION_FEATURES,
            "tf_q6_expert_features": Q6_EXPERT_FEATURES,
            "tf_q6_terminal_size": ctypes.sizeof(_Terminal),
        }
        for name, value in expected.items():
            if getattr(self._lib, name)() != value:
                raise RuntimeError(f"Rust/Python q6 ABI mismatch: {name}")
        self._handle = self._lib.tf_q6_create(
            self.num_envs,
            self.seed_base,
            self.map_pool,
            self._ptr(self.expert_weights),
            self.expert_weights.size,
        )
        if not self._handle:
            raise RuntimeError("Rust q6 proposal environment allocation failed")

        self.state_features = np.empty(
            (self.num_envs, Q6_STATE_FEATURES), dtype=np.float32
        )
        self.action_features = np.empty(
            (self.num_envs, Q6_ACTIONS, Q6_ACTION_FEATURES), dtype=np.float32
        )
        self.masks = np.empty((self.num_envs, Q6_ACTIONS), dtype=np.uint8)
        self.rewards = np.empty(self.num_envs, dtype=np.float32)
        self._terminals = (_Terminal * self.num_envs)()
        self.task_indices = np.arange(self.num_envs, dtype=np.uint64)
        self._next_task_index = self.num_envs
        self._closed = False
        self.observe()

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        for name in (
            "tf_q6_state_features",
            "tf_q6_actions",
            "tf_q6_action_features",
            "tf_q6_expert_features",
            "tf_q6_terminal_size",
        ):
            getattr(self._lib, name).restype = ctypes.c_size_t
        self._lib.tf_q6_create.argtypes = [
            ctypes.c_size_t,
            ctypes.c_int64,
            ctypes.c_size_t,
            void,
            ctypes.c_size_t,
        ]
        self._lib.tf_q6_create.restype = void
        self._lib.tf_q6_destroy.argtypes = [void]
        self._lib.tf_q6_destroy.restype = None
        self._lib.tf_q6_observe.argtypes = [void] * 4
        self._lib.tf_q6_observe.restype = ctypes.c_int32
        self._lib.tf_q6_step.argtypes = [void] * 7
        self._lib.tf_q6_step.restype = ctypes.c_int32

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def _terminal_ptr(self) -> ctypes.c_void_p:
        return ctypes.cast(self._terminals, ctypes.c_void_p)

    def _validate_observation(self) -> None:
        if not np.isfinite(self.state_features).all():
            raise RuntimeError("non-finite q6 state feature")
        if not np.isfinite(self.action_features).all():
            raise RuntimeError("non-finite q6 action feature")
        if not np.all((self.masks == 0) | (self.masks == 1)):
            raise RuntimeError("non-binary q6 action mask")
        if not np.all(self.masks[:, 0] == 1):
            raise RuntimeError("q6 exact-control action must always be legal")
        if np.any(self.action_features[:, 0] != 0.0):
            raise RuntimeError("q6 exact-control action must be the zero feature vector")
        if np.any(self.action_features[self.masks == 0] != 0.0):
            raise RuntimeError("masked q6 action contains nonzero features")
        for slot in range(self.num_envs):
            for action in np.flatnonzero(self.masks[slot, 1:]) + 1:
                # The action index is one plus the smallest endorsing expert.
                if self.action_features[slot, action, 45 + action - 1] != 1.0:
                    raise RuntimeError("q6 representative endorsement mismatch")

    def observe(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        status = self._lib.tf_q6_observe(
            self._handle,
            self._ptr(self.state_features),
            self._ptr(self.action_features),
            self._ptr(self.masks),
        )
        if status != 0:
            raise RuntimeError(f"tf_q6_observe failed with {status}")
        self._validate_observation()
        return self.state_features, self.action_features, self.masks

    def step(
        self, selected_actions: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Q6ProposalStepInfo]:
        selected_actions = np.ascontiguousarray(selected_actions, dtype=np.int32)
        if selected_actions.shape != (self.num_envs,):
            raise ValueError(
                f"expected selected action shape {(self.num_envs,)}, got {selected_actions.shape}"
            )
        if np.any(selected_actions < 0) or np.any(selected_actions >= Q6_ACTIONS):
            raise ValueError("q6 action index outside [0, 65)")
        rows = np.arange(self.num_envs)
        if np.any(self.masks[rows, selected_actions] != 1):
            raise ValueError("selected a masked q6 proposal")
        task_before = self.task_indices.copy()
        status = self._lib.tf_q6_step(
            self._handle,
            self._ptr(selected_actions),
            self._ptr(self.state_features),
            self._ptr(self.action_features),
            self._ptr(self.masks),
            self._ptr(self.rewards),
            self._terminal_ptr(),
        )
        if status != 0:
            raise RuntimeError(f"tf_q6_step failed with {status}")
        if not np.isfinite(self.rewards).all():
            raise RuntimeError("non-finite q6 paired reward")
        self._validate_observation()
        terminals: list[dict | None] = []
        for index, terminal in enumerate(self._terminals):
            if not terminal.done:
                terminals.append(None)
                continue
            if int(terminal.task_index) != int(task_before[index]):
                raise RuntimeError("Rust/Python q6 task-index drift")
            opponent = int(terminal.opponent)
            if opponent >= len(OPPONENTS):
                raise RuntimeError("unknown q6 opponent identifier")
            baseline_margin = int(terminal.baseline_own_score - terminal.baseline_opponent_score)
            margin = int(terminal.own_score - terminal.opponent_score)
            terminals.append(
                {
                    "task_index": int(terminal.task_index),
                    "map_seed": int(terminal.map_seed),
                    "seat": int(terminal.seat),
                    "opponent": OPPONENTS[opponent],
                    "own_score": int(terminal.own_score),
                    "opponent_score": int(terminal.opponent_score),
                    "margin": margin,
                    "baseline_own_score": int(terminal.baseline_own_score),
                    "baseline_opponent_score": int(terminal.baseline_opponent_score),
                    "baseline_margin": baseline_margin,
                    "margin_delta": margin - baseline_margin,
                    "own_workers": int(terminal.own_workers),
                    "successful_trains": int(terminal.successful_trains),
                    "intervention_batches": int(terminal.intervention_batches),
                    "boundary_decisions": int(terminal.boundary_decisions),
                    "joint_batches": int(terminal.joint_batches),
                    "noncontrol_assignments": int(terminal.noncontrol_assignments),
                    "own_created_crops": int(terminal.own_created_crops),
                    "invalid_direct_commands": int(terminal.invalid_direct_commands),
                    "provenance_failures": int(terminal.provenance_failures),
                    "deposit_prediction_failures": int(terminal.deposit_prediction_failures),
                    "invalidated_jobs": int(terminal.invalidated_jobs),
                    "action_hash": int(terminal.action_hash),
                    "state_hash": int(terminal.state_hash),
                }
            )
            self.task_indices[index] = self._next_task_index
            self._next_task_index += 1
        return (
            self.state_features,
            self.action_features,
            self.masks,
            self.rewards.copy(),
            Q6ProposalStepInfo(tuple(terminals)),
        )

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_q6_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "Q6ProposalVecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True) is False:
            self.close()
