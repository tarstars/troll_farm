#!/usr/bin/env python3
"""Validate D73's 72-feature ordinary ABI against the exact D62 ABI."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.rl_batch_option_env import (
    BATCH_OPTION_ACTIONS,
    BatchOptionVecEnv,
    DEFAULT_LIBRARY,
    TASKS_PER_MAP,
)
from cgauto.rl_opening_recurrent_env import OpeningRecurrentVecEnv


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
OUTPUT = ANALYSIS / "d73a-opening-recurrent-environment-parity.json"
SEED_BASE = 9_810_999
TERMINAL_FIELDS = (
    "map_seed",
    "seat",
    "opponent",
    "own_score",
    "opponent_score",
    "own_workers",
    "successful_trains",
    "own_created_crops",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "invalidated_jobs",
    "action_hash",
    "state_hash",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(env_type: type, mode: int) -> dict[int, dict]:
    completed: dict[int, dict] = {}
    slot_returns = np.zeros(TASKS_PER_MAP, dtype=np.float64)
    with env_type(TASKS_PER_MAP, SEED_BASE) as env:
        for _ in range(1_000):
            actions = np.where(env.masks[:, mode] == 1, mode, 0).astype(np.int32)
            _, _, rewards, info = env.step(actions)
            slot_returns += rewards.astype(np.float64)
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                identity_error = float(
                    abs(100.0 * slot_returns[slot] - terminal["margin"])
                )
                slot_returns[slot] = 0.0
                if terminal["task_index"] < TASKS_PER_MAP:
                    completed[terminal["task_index"]] = {
                        **terminal,
                        "reward_identity_error": identity_error,
                    }
            if len(completed) == TASKS_PER_MAP:
                break
        else:
            raise RuntimeError("D73 parity run exceeded step guard")
    return completed


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    comparisons = 0
    differences = []
    repeat_differences = []
    maximum_identity_error = 0.0
    for mode in range(BATCH_OPTION_ACTIONS):
        expected = run(BatchOptionVecEnv, mode)
        actual_a = run(OpeningRecurrentVecEnv, mode)
        actual_b = run(OpeningRecurrentVecEnv, mode)
        for task_index in range(TASKS_PER_MAP):
            left = expected[task_index]
            right = actual_a[task_index]
            repeat = actual_b[task_index]
            comparisons += 1
            maximum_identity_error = max(
                maximum_identity_error,
                left["reward_identity_error"],
                right["reward_identity_error"],
                repeat["reward_identity_error"],
            )
            changed = {
                field: [left[field], right[field]]
                for field in TERMINAL_FIELDS
                if left[field] != right[field]
            }
            if changed:
                differences.append(
                    {"mode": mode, "task_index": task_index, "fields": changed}
                )
            repeated = {
                field: [right[field], repeat[field]]
                for field in TERMINAL_FIELDS
                if right[field] != repeat[field]
            }
            if repeated:
                repeat_differences.append(
                    {"mode": mode, "task_index": task_index, "fields": repeated}
                )
    gates = {
        "64_mode_task_comparisons": comparisons == 64,
        "exact_d62_terminal_parity": not differences,
        "repeat_terminal_exact": not repeat_differences,
        "reward_identity_below_1e4": maximum_identity_error < 1.0e-4,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    report = {
        "schema": "troll-farm-d73a-opening-recurrent-parity-v1",
        "seed_base": SEED_BASE,
        "comparisons": comparisons,
        "maximum_reward_identity_error": float(maximum_identity_error),
        "differences": differences,
        "repeat_differences": repeat_differences,
        "gates": gates,
        "pass": all(gates.values()),
        "hashes": {
            "library": sha256(Path(DEFAULT_LIBRARY)),
            "validator": sha256(Path(__file__)),
            "wrapper": sha256(ROOT / "cgauto/rl_opening_recurrent_env.py"),
            "opening_environment": sha256(ROOT / "rust/src/rl_opening_portfolio.rs"),
        },
        "scope": "mechanics parity only; seed excluded from training and value",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": str(OUTPUT), **report}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
