#!/usr/bin/env python3
"""ctypes wrapper for the D170a sequential option-policy environment.

Vectorized batch over `rust/src/rl_d170a_option_policy_env.rs`'s
`tf_d170a_*` FFI. Each slot plays one (map_seed, seat, opponent) task;
at each armable state (one of the 13 D169a arms) the caller supplies
KEEP (0) or INVOKE (1); budget is one activation per game (enforced
Rust-side). `step()` always advances every slot by exactly one decision
(or straight to terminal, for slots with no pending decision left this
game); finished slots auto-reset to the next deterministic per-slot task
in the same (seed_base, map_pool) stream, so exhaustive panel coverage
is driven by `terminal.task_index` (see `d108`/`d158`'s own
`evaluate_policy` convention), not simple episode counting.
"""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY = ROOT / "rust" / "target" / "release" / "libtroll_farm.so"

STATE_FEATURES = 64
DECISION_FEATURES = 17
INPUT_FEATURES = STATE_FEATURES + DECISION_FEATURES
ARMS = 13
ACTIONS = 2
KEEP = 0
INVOKE = 1

# arm_catalog()[1..14] order, frozen (see the Rust module's D170A_DECISION_FEATURES doc).
ARM_LABELS = (
    "opt_return",
    "opt_fruit_t072",
    "opt_fruit_t104",
    "opt_fruit_t136",
    "opt_fruit_trig",
    "opt_iron_t072",
    "opt_iron_t104",
    "opt_iron_t136",
    "opt_iron_trig",
    "opt_protect_t072",
    "opt_protect_t104",
    "opt_protect_t136",
    "opt_protect_trig",
)
assert len(ARM_LABELS) == ARMS


def arm_label(chosen_arm: int) -> str:
    """`chosen_arm` is 0 (never invoked) or 1..ARMS (arm_catalog index)."""
    return "control" if chosen_arm == 0 else ARM_LABELS[chosen_arm - 1]


@dataclass(frozen=True)
class D170aTerminal:
    task_index: int
    map_seed: int
    seat: int
    opponent: int
    own_score: int
    opponent_score: int
    margin: int
    control_margin: int
    control_own_score: int
    paired_margin: int
    chosen_arm: int
    decisions_seen: int
    budget_used: bool
    own_workers: int
    max_own_workers: int
    own_created_crops: int
    opponent_created_crops: int
    provenance_failures: int
    purity_violations: int
    invalid_direct_commands: int
    action_hash: int
    state_hash: int
    turn: int

    @property
    def chosen_arm_label(self) -> str:
        return arm_label(self.chosen_arm)

    @property
    def own_score_delta(self) -> int:
        return self.own_score - self.control_own_score


_STEP_ARGS = 29


class D170aVecEnv:
    """Auto-reset vectorized batch of D170a sequential decision episodes."""

    def __init__(
        self,
        num_envs: int,
        seed_base: int,
        map_pool: int,
        *,
        library: Path | str = DEFAULT_LIBRARY,
    ) -> None:
        if num_envs <= 0:
            raise ValueError("num_envs must be positive")
        if seed_base <= 0:
            raise ValueError("seed_base must be positive")
        if map_pool <= 0:
            raise ValueError("map_pool must be positive")
        self.num_envs = int(num_envs)
        self.seed_base = int(seed_base)
        self.map_pool = int(map_pool)
        self.library_path = Path(library)
        if not self.library_path.exists():
            raise FileNotFoundError(
                f"missing {self.library_path}; run "
                "cargo build --manifest-path rust/Cargo.toml --release --lib"
            )
        self._lib = ctypes.CDLL(str(self.library_path))
        self._configure_abi()
        if self._state_features() != STATE_FEATURES:
            raise RuntimeError("Rust/Python D170a state-feature mismatch")
        if self._decision_features() != DECISION_FEATURES:
            raise RuntimeError("Rust/Python D170a decision-feature mismatch")
        if self._input_features() != INPUT_FEATURES:
            raise RuntimeError("Rust/Python D170a input-feature mismatch")
        if self._arms() != ARMS:
            raise RuntimeError("Rust/Python D170a arm-count mismatch")
        if self._actions() != ACTIONS:
            raise RuntimeError("Rust/Python D170a action-count mismatch")
        self._handle = self._create(
            self.num_envs, ctypes.c_int64(self.seed_base), self.map_pool
        )
        if not self._handle:
            raise RuntimeError("Rust D170a allocation failed")

        n = self.num_envs
        self.inputs = np.empty((n, INPUT_FEATURES), dtype=np.float32)
        self.pending = np.empty(n, dtype=np.uint8)
        self.rewards = np.empty(n, dtype=np.float32)
        self._dones = np.empty(n, dtype=np.uint8)
        self._task_indices = np.empty(n, dtype=np.uint64)
        self._map_seeds = np.empty(n, dtype=np.int64)
        self._seats = np.empty(n, dtype=np.uint8)
        self._opponents = np.empty(n, dtype=np.uint8)
        self._own_scores = np.empty(n, dtype=np.int32)
        self._opponent_scores = np.empty(n, dtype=np.int32)
        self._margins = np.empty(n, dtype=np.int32)
        self._control_margins = np.empty(n, dtype=np.int32)
        self._control_own_scores = np.empty(n, dtype=np.int32)
        self._paired_margins = np.empty(n, dtype=np.int32)
        self._chosen_arms = np.empty(n, dtype=np.int32)
        self._decisions_seen = np.empty(n, dtype=np.uint32)
        self._budget_used = np.empty(n, dtype=np.uint8)
        self._own_workers = np.empty(n, dtype=np.uint8)
        self._max_own_workers = np.empty(n, dtype=np.uint8)
        self._own_created_crops = np.empty(n, dtype=np.uint32)
        self._opponent_created_crops = np.empty(n, dtype=np.uint32)
        self._provenance_failures = np.empty(n, dtype=np.uint32)
        self._purity_violations = np.empty(n, dtype=np.uint32)
        self._invalid_direct_commands = np.empty(n, dtype=np.uint32)
        self._action_hashes = np.empty(n, dtype=np.uint64)
        self._state_hashes = np.empty(n, dtype=np.uint64)
        self._turns = np.empty(n, dtype=np.uint16)
        self._closed = False
        self.observe()

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def _configure_abi(self) -> None:
        void = ctypes.c_void_p
        lib = self._lib
        self._state_features = lib.tf_d170a_state_features
        self._decision_features = lib.tf_d170a_decision_features
        self._input_features = lib.tf_d170a_input_features
        self._arms = lib.tf_d170a_arms
        self._actions = lib.tf_d170a_actions
        for fn in (
            self._state_features,
            self._decision_features,
            self._input_features,
            self._arms,
            self._actions,
        ):
            fn.restype = ctypes.c_size_t
        self._create = lib.tf_d170a_create
        self._create.argtypes = [ctypes.c_size_t, ctypes.c_int64, ctypes.c_size_t]
        self._create.restype = void
        self._destroy = lib.tf_d170a_destroy
        self._destroy.argtypes = [void]
        self._destroy.restype = None
        self._observe = lib.tf_d170a_observe
        self._observe.argtypes = [void, void, void]
        self._observe.restype = ctypes.c_int32
        self._step = lib.tf_d170a_step
        self._step.argtypes = [void] * _STEP_ARGS
        self._step.restype = ctypes.c_int32

    def observe(self) -> tuple[np.ndarray, np.ndarray]:
        status = self._observe(self._handle, self._ptr(self.inputs), self._ptr(self.pending))
        if status != 0:
            raise RuntimeError(f"tf_d170a_observe failed with {status}")
        return self.inputs, self.pending

    def step(
        self, actions: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list["D170aTerminal | None"]]:
        actions = np.ascontiguousarray(actions, dtype=np.int32)
        if actions.shape != (self.num_envs,):
            raise ValueError(f"expected actions shape {(self.num_envs,)}, got {actions.shape}")
        status = self._step(
            self._handle,
            self._ptr(actions),
            self._ptr(self.inputs),
            self._ptr(self.pending),
            self._ptr(self.rewards),
            self._ptr(self._dones),
            self._ptr(self._task_indices),
            self._ptr(self._map_seeds),
            self._ptr(self._seats),
            self._ptr(self._opponents),
            self._ptr(self._own_scores),
            self._ptr(self._opponent_scores),
            self._ptr(self._margins),
            self._ptr(self._control_margins),
            self._ptr(self._control_own_scores),
            self._ptr(self._paired_margins),
            self._ptr(self._chosen_arms),
            self._ptr(self._decisions_seen),
            self._ptr(self._budget_used),
            self._ptr(self._own_workers),
            self._ptr(self._max_own_workers),
            self._ptr(self._own_created_crops),
            self._ptr(self._opponent_created_crops),
            self._ptr(self._provenance_failures),
            self._ptr(self._purity_violations),
            self._ptr(self._invalid_direct_commands),
            self._ptr(self._action_hashes),
            self._ptr(self._state_hashes),
            self._ptr(self._turns),
        )
        if status != 0:
            raise RuntimeError(f"tf_d170a_step failed with {status}")
        terminals: list[D170aTerminal | None] = []
        for i in range(self.num_envs):
            if not self._dones[i]:
                terminals.append(None)
                continue
            terminals.append(
                D170aTerminal(
                    task_index=int(self._task_indices[i]),
                    map_seed=int(self._map_seeds[i]),
                    seat=int(self._seats[i]),
                    opponent=int(self._opponents[i]),
                    own_score=int(self._own_scores[i]),
                    opponent_score=int(self._opponent_scores[i]),
                    margin=int(self._margins[i]),
                    control_margin=int(self._control_margins[i]),
                    control_own_score=int(self._control_own_scores[i]),
                    paired_margin=int(self._paired_margins[i]),
                    chosen_arm=int(self._chosen_arms[i]),
                    decisions_seen=int(self._decisions_seen[i]),
                    budget_used=bool(self._budget_used[i]),
                    own_workers=int(self._own_workers[i]),
                    max_own_workers=int(self._max_own_workers[i]),
                    own_created_crops=int(self._own_created_crops[i]),
                    opponent_created_crops=int(self._opponent_created_crops[i]),
                    provenance_failures=int(self._provenance_failures[i]),
                    purity_violations=int(self._purity_violations[i]),
                    invalid_direct_commands=int(self._invalid_direct_commands[i]),
                    action_hash=int(self._action_hashes[i]),
                    state_hash=int(self._state_hashes[i]),
                    turn=int(self._turns[i]),
                )
            )
        return self.inputs, self.pending, self.rewards.copy(), self._dones.copy(), terminals

    def close(self) -> None:
        if not self._closed:
            self._destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "D170aVecEnv":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
