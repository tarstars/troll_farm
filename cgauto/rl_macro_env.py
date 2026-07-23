#!/usr/bin/env python3
"""NumPy/ctypes wrapper for the D40 complete-macro candidate environment."""

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
MAX_CANDIDATES = 768
CANDIDATE_FEATURES = 44
BRANCHES = ("train", "deficit", "evacuation", "rate")
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
class MacroStepInfo:
    terminals: tuple[dict | None, ...]


class MacroVecEnv:
    """Auto-reset complete-macro environments with variable legal candidate sets."""

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
        if self._lib.tf_macro_max_candidates() != MAX_CANDIDATES:
            raise RuntimeError("Rust/Python maximum-candidate mismatch")
        if self._lib.tf_macro_candidate_features() != CANDIDATE_FEATURES:
            raise RuntimeError("Rust/Python candidate-feature mismatch")
        if self._lib.tf_macro_terminal_size() != ctypes.sizeof(_Terminal):
            raise RuntimeError(
                "Rust/Python terminal layout mismatch: "
                f"Rust={self._lib.tf_macro_terminal_size()} "
                f"Python={ctypes.sizeof(_Terminal)}"
            )
        self._handle = self._lib.tf_macro_create(self.num_envs, self.seed_base)
        if not self._handle:
            raise RuntimeError("Rust macro environment allocation failed")

        self.actions = np.empty((self.num_envs, MAX_CANDIDATES), dtype=np.int32)
        self.features = np.empty(
            (self.num_envs, MAX_CANDIDATES, CANDIDATE_FEATURES), dtype=np.float32
        )
        self.counts = np.empty(self.num_envs, dtype=np.uint16)
        self.teacher_indices = np.empty(self.num_envs, dtype=np.uint16)
        self.branches = np.empty(self.num_envs, dtype=np.uint8)
        self.prior_ranks = np.empty(
            (self.num_envs, MAX_CANDIDATES), dtype=np.uint16
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
            "tf_macro_max_candidates",
            "tf_macro_candidate_features",
            "tf_macro_terminal_size",
        ):
            getattr(self._lib, name).restype = ctypes.c_size_t
        self._lib.tf_macro_create.argtypes = [ctypes.c_size_t, ctypes.c_int64]
        self._lib.tf_macro_create.restype = void
        self._lib.tf_macro_destroy.argtypes = [void]
        self._lib.tf_macro_destroy.restype = None
        self._lib.tf_macro_observe.argtypes = [void] * 7
        self._lib.tf_macro_observe.restype = ctypes.c_int32
        self._lib.tf_macro_step.argtypes = [void] * 10
        self._lib.tf_macro_step.restype = ctypes.c_int32

    @staticmethod
    def _ptr(array: np.ndarray) -> ctypes.c_void_p:
        if not array.flags.c_contiguous:
            raise ValueError("FFI arrays must be C-contiguous")
        return ctypes.c_void_p(array.ctypes.data)

    def _terminal_ptr(self) -> ctypes.c_void_p:
        return ctypes.cast(self._terminals, ctypes.c_void_p)

    def observe(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        status = self._lib.tf_macro_observe(
            self._handle,
            self._ptr(self.actions),
            self._ptr(self.features),
            self._ptr(self.counts),
            self._ptr(self.teacher_indices),
            self._ptr(self.branches),
            self._ptr(self.prior_ranks),
        )
        if status != 0:
            raise RuntimeError(f"tf_macro_observe failed with {status}")
        self._validate_observation()
        return self.actions, self.features, self.counts, self.teacher_indices

    def _validate_observation(self) -> None:
        if np.any(self.counts == 0) or np.any(self.counts > MAX_CANDIDATES):
            raise RuntimeError(f"invalid candidate counts: {self.counts}")
        if np.any(self.teacher_indices >= self.counts):
            raise RuntimeError("illegal D40 teacher candidate index")
        if np.any(self.branches >= len(BRANCHES)):
            raise RuntimeError("invalid D40 branch identifier")
        if not np.isfinite(self.features).all():
            raise RuntimeError("non-finite macro candidate feature")
        for index, count in enumerate(self.counts):
            count = int(count)
            legal = self.actions[index, :count]
            if len(np.unique(legal)) != count or np.any(legal < 0):
                raise RuntimeError(f"invalid legal action IDs in slot {index}")
            if np.any(self.actions[index, count:] != -1):
                raise RuntimeError(f"nonempty candidate padding in slot {index}")
            ranks = self.prior_ranks[index, :count]
            if not np.array_equal(np.sort(ranks), np.arange(count, dtype=np.uint16)):
                raise RuntimeError(f"invalid exact-prior rank permutation in slot {index}")
            if self.prior_ranks[index, int(self.teacher_indices[index])] != 0:
                raise RuntimeError(f"exact-prior rank zero disagrees with D40 in slot {index}")
            if np.any(self.prior_ranks[index, count:] != np.iinfo(np.uint16).max):
                raise RuntimeError(f"nonempty exact-prior rank padding in slot {index}")

    def teacher_actions(self) -> np.ndarray:
        return self.actions[
            np.arange(self.num_envs), self.teacher_indices.astype(np.int64)
        ].copy()

    def step(
        self, selected_actions: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, MacroStepInfo]:
        selected_actions = np.ascontiguousarray(selected_actions, dtype=np.int32)
        if selected_actions.shape != (self.num_envs,):
            raise ValueError(
                f"expected selected action shape {(self.num_envs,)}, "
                f"got {selected_actions.shape}"
            )
        status = self._lib.tf_macro_step(
            self._handle,
            self._ptr(selected_actions),
            self._ptr(self.actions),
            self._ptr(self.features),
            self._ptr(self.counts),
            self._ptr(self.teacher_indices),
            self._ptr(self.branches),
            self._ptr(self.prior_ranks),
            self._ptr(self.rewards),
            self._terminal_ptr(),
        )
        if status != 0:
            raise RuntimeError(f"tf_macro_step failed with {status}")
        self._validate_observation()
        terminals = []
        for index, terminal in enumerate(self._terminals):
            if not terminal.done:
                terminals.append(None)
                continue
            if int(terminal.task_index) != int(self.task_indices[index]):
                raise RuntimeError("Rust/Python macro task-index drift")
            terminals.append(
                {
                    "task_index": int(terminal.task_index),
                    "map_seed": int(terminal.map_seed),
                    "seat": int(terminal.seat),
                    "opponent": OPPONENTS[int(terminal.opponent)],
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
            self.actions,
            self.features,
            self.counts,
            self.rewards.copy(),
            MacroStepInfo(tuple(terminals)),
        )

    def close(self) -> None:
        if not self._closed:
            self._lib.tf_macro_destroy(self._handle)
            self._closed = True

    def __enter__(self) -> "MacroVecEnv":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def __del__(self) -> None:
        if getattr(self, "_closed", True) is False:
            self.close()


def random_legal_actions(env: MacroVecEnv, rng: np.random.Generator) -> np.ndarray:
    selected = np.empty(env.num_envs, dtype=np.int32)
    for index, count in enumerate(env.counts):
        selected[index] = env.actions[index, rng.integers(int(count))]
    return selected


def run_policy(
    policy: str,
    *,
    maps: int,
    num_envs: int,
    seed_base: int,
    random_seed: int = 0,
) -> dict:
    if maps <= 0:
        raise ValueError("maps must be positive")
    target_tasks = maps * TASKS_PER_MAP
    completed: dict[int, dict] = {}
    decisions = 0
    rng = np.random.default_rng(random_seed)
    started = time.perf_counter()
    with MacroVecEnv(num_envs, seed_base) as env:
        while len(completed) < target_tasks:
            if policy == "teacher":
                selected = env.teacher_actions()
            elif policy == "random":
                selected = random_legal_actions(env, rng)
            else:
                raise ValueError(policy)
            _, _, _, _, info = env.step(selected)
            decisions += num_envs
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed[terminal["task_index"]] = terminal
    elapsed = time.perf_counter() - started
    rows = [completed[index] for index in range(target_tasks)]
    return {
        "policy": policy,
        "seed_base": seed_base,
        "seed_stop_exclusive": seed_base + maps,
        "maps": maps,
        "tasks": target_tasks,
        "num_envs": num_envs,
        "decisions": decisions,
        "elapsed_seconds": elapsed,
        "decisions_per_second": decisions / elapsed,
        "mean_own_score": float(np.mean([row["own_score"] for row in rows])),
        "mean_opponent_score": float(
            np.mean([row["opponent_score"] for row in rows])
        ),
        "mean_margin": float(np.mean([row["margin"] for row in rows])),
        "worker_two_rate": float(np.mean([row["own_workers"] >= 2 for row in rows])),
        "worker_three_rate": float(
            np.mean([row["own_workers"] >= 3 for row in rows])
        ),
        "crop_rate": float(
            np.mean([row["own_created_crops"] > 0 for row in rows])
        ),
        "invalid_direct_commands": sum(
            row["invalid_direct_commands"] for row in rows
        ),
        "provenance_failures": sum(row["provenance_failures"] for row in rows),
        "deposit_prediction_failures": sum(
            row["deposit_prediction_failures"] for row in rows
        ),
        "episodes_detail": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", choices=("teacher", "random"), default="teacher")
    parser.add_argument("--maps", type=int, default=2)
    parser.add_argument("--num-envs", type=int, default=16)
    parser.add_argument("--seed-base", type=int, default=9_711_000)
    parser.add_argument("--random-seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_policy(
        args.policy,
        maps=args.maps,
        num_envs=args.num_envs,
        seed_base=args.seed_base,
        random_seed=args.random_seed,
    )
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n")
    print(
        json.dumps(
            {key: value for key, value in report.items() if key != "episodes_detail"},
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
