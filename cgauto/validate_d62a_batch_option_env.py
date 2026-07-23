#!/usr/bin/env python3
"""Validate the D62 batch-option ABI against frozen D61 terminal references."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from cgauto.rl_batch_option_env import (
    BATCH_OPTION_ACTIONS,
    BATCH_OPTION_MODES,
    DEFAULT_LIBRARY,
    TASKS_PER_MAP,
    BatchOptionVecEnv,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d62a-batch-option-ppo-mechanical-preflight-protocol-2026-07-21.md"
AMENDMENT = ANALYSIS / "d62a-balanced-reference-amendment-2026-07-21.md"
GENERATOR = ROOT / "cgauto" / "make_d62a_balanced_reference_population.py"
WRAPPER = ROOT / "cgauto" / "rl_batch_option_env.py"
RUST_ENV = ROOT / "rust" / "src" / "rl_batch_option.rs"
D61_RUNNER = ROOT / "rust" / "src" / "bin" / "d61_batch_option_population.rs"
SOURCE_POPULATION = ANALYSIS / "d61a-renewable-safe-batch-option-population.tsv"
REFERENCE_POPULATION = ANALYSIS / "d62a-balanced-reference-population.tsv"
CORRECTED_MATRIX = (
    ANALYSIS
    / "d61a-renewable-safe-batch-option-population-corrected-a-9801000-9801007.tsv"
)
BALANCED_MATRIX = ANALYSIS / "d62a-balanced-reference-matrix-9801000.tsv"
OUTPUT = ANALYSIS / "d62a-batch-option-environment-parity.json"

EXPECTED_HASHES = {
    PROTOCOL: "e59c5eb06d8a8742de6017226c7ed79378b17bc7db512f6e70f021d04992d4cb",
    AMENDMENT: "ff34a05920e25b4777bbc11424affb61607b00b93815ae93051113e6a311a41d",
    GENERATOR: "e06ce4038bb649fe5383fd754f08535f02ccb6890837a70861fbcdd539efb893",
    WRAPPER: "f5248c0daa14456431092b7c6b0c2f620c2dffd3909f65e28d75538deddb4018",
    RUST_ENV: "dc476cdccd5076a9f6837190a60e53941db59ce80e94fc528df98b30d3e3dde3",
    D61_RUNNER: "fecc96da988436176e3ee35802deaef9ec5c4cdee0e6c9929422b28516a06ba5",
    SOURCE_POPULATION: "e7021ac2ef7e99a7f89dbe700473674f451c186e837d51046712036443790f5f",
    REFERENCE_POPULATION: "1ceffcfb3fec7bde85cb10db4041831eba6f4e72e6aa2c200e22001c7a10e3b8",
    CORRECTED_MATRIX: "957f9d332cf0b1c15d1027b0a01250321f427eacb00da86a7d618f6da071e485",
    BALANCED_MATRIX: "e58501488df46edbdc77b3b2caf5409aafe43fa1deab14212aa17e2e20883ae7",
    Path(DEFAULT_LIBRARY): "0b2dbc8d23f67f975e584f9b7f6e69f91dc13397dca8a24fe54aa262e760b0f7",
}
SEED_BASE = 9_801_000
TERMINAL_FIELDS = (
    "own_score",
    "opponent_score",
    "own_workers",
    "own_created_crops",
    "action_hash",
    "state_hash",
)
REFERENCE_POLICIES = {
    "balanced": "d62_zero_linear_balanced_reference",
    "harvest": "safe_harvest",
    "renew": "safe_renew",
    "fell": "safe_fell",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_reference(mode: str) -> dict[tuple[int, int, str], dict[str, int]]:
    path = BALANCED_MATRIX if mode == "balanced" else CORRECTED_MATRIX
    policy = REFERENCE_POLICIES[mode]
    rows: dict[tuple[int, int, str], dict[str, int]] = {}
    with path.open(newline="") as source:
        for row in csv.DictReader(source, delimiter="\t"):
            if int(row["map_seed"]) != SEED_BASE or row["policy"] != policy:
                continue
            key = (int(row["map_seed"]), int(row["seat"]), row["opponent"])
            if key in rows:
                raise RuntimeError(f"duplicate D61 parity row: {mode} {key}")
            rows[key] = {field: int(row[field]) for field in TERMINAL_FIELDS}
    if len(rows) != TASKS_PER_MAP:
        raise RuntimeError(
            f"expected {TASKS_PER_MAP} D61 {mode} rows, found {len(rows)}"
        )
    return rows


def run_mode(mode_index: int) -> dict:
    mode = BATCH_OPTION_MODES[mode_index]
    completed: dict[int, dict] = {}
    slot_returns = np.zeros(TASKS_PER_MAP, dtype=np.float64)
    transitions = unlocked = selected_nonbalanced = 0
    maximum_identity_error = 0.0
    with BatchOptionVecEnv(TASKS_PER_MAP, SEED_BASE) as env:
        for _ in range(1_000):
            selected = np.where(env.masks[:, mode_index] == 1, mode_index, 0).astype(
                np.int32
            )
            unlocked += int(np.count_nonzero(env.masks.sum(axis=1) == BATCH_OPTION_ACTIONS))
            selected_nonbalanced += int(np.count_nonzero(selected))
            _, _, rewards, info = env.step(selected)
            transitions += TASKS_PER_MAP
            slot_returns += rewards.astype(np.float64)
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                identity_error = abs(
                    100.0 * slot_returns[slot] - float(terminal["margin"])
                )
                maximum_identity_error = max(maximum_identity_error, identity_error)
                slot_returns[slot] = 0.0
                task_index = int(terminal["task_index"])
                if task_index < TASKS_PER_MAP:
                    if task_index in completed:
                        raise RuntimeError(f"duplicate original D62 task {task_index}")
                    completed[task_index] = {
                        **terminal,
                        "reward_identity_error": identity_error,
                    }
            if len(completed) == TASKS_PER_MAP:
                break
        else:
            raise RuntimeError(f"D62 {mode} reference run exceeded step guard")
    return {
        "mode": mode,
        "transitions": transitions,
        "unlocked": unlocked,
        "selected_nonbalanced": selected_nonbalanced,
        "maximum_reward_identity_error": maximum_identity_error,
        "terminals": [completed[index] for index in range(TASKS_PER_MAP)],
    }


def terminal_key(terminal: dict) -> tuple[int, int, str]:
    return (
        int(terminal["map_seed"]),
        int(terminal["seat"]),
        str(terminal["opponent"]),
    )


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"refusing to overwrite {OUTPUT}")
    hashes = {}
    for path, expected in EXPECTED_HASHES.items():
        if not path.exists():
            raise SystemExit(f"missing D62 parity prerequisite: {path}")
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"D62 parity prerequisite hash mismatch: {path}")
        hashes[str(path)] = actual

    references = {mode: load_reference(mode) for mode in BATCH_OPTION_MODES}
    runs_a = [run_mode(index) for index in range(BATCH_OPTION_ACTIONS)]
    runs_b = [run_mode(index) for index in range(BATCH_OPTION_ACTIONS)]
    mismatches = []
    repeat_mismatches = []
    comparisons = 0
    maximum_identity_error = 0.0
    for run_a, run_b in zip(runs_a, runs_b, strict=True):
        mode = run_a["mode"]
        maximum_identity_error = max(
            maximum_identity_error,
            float(run_a["maximum_reward_identity_error"]),
            float(run_b["maximum_reward_identity_error"]),
        )
        for terminal_a, terminal_b in zip(
            run_a["terminals"], run_b["terminals"], strict=True
        ):
            key = terminal_key(terminal_a)
            if key != terminal_key(terminal_b):
                repeat_mismatches.append(
                    {"mode": mode, "key_a": key, "key_b": terminal_key(terminal_b)}
                )
                continue
            repeat_fields = {
                field: (terminal_a[field], terminal_b[field])
                for field in TERMINAL_FIELDS
                if terminal_a[field] != terminal_b[field]
            }
            if repeat_fields:
                repeat_mismatches.append(
                    {"mode": mode, "key": key, "fields": repeat_fields}
                )
            expected = references[mode].get(key)
            if expected is None:
                mismatches.append({"mode": mode, "key": key, "missing_reference": True})
                continue
            comparisons += 1
            fields = {
                field: {"actual": terminal_a[field], "expected": expected[field]}
                for field in TERMINAL_FIELDS
                if terminal_a[field] != expected[field]
            }
            if fields:
                mismatches.append({"mode": mode, "key": key, "fields": fields})

    gates = {
        "64_mode_task_comparisons": comparisons == 4 * TASKS_PER_MAP,
        "exact_d61_terminal_parity": not mismatches,
        "repeat_terminal_bit_exact": not repeat_mismatches,
        "reward_identity_below_1e4": maximum_identity_error < 1.0e-4,
        "all_four_modes_exercised": [run["mode"] for run in runs_a]
        == list(BATCH_OPTION_MODES),
    }
    report = {
        "protocol": str(PROTOCOL),
        "amendment": str(AMENDMENT),
        "hashes": hashes,
        "seed_base": SEED_BASE,
        "tasks": TASKS_PER_MAP,
        "mode_task_comparisons": comparisons,
        "maximum_reward_identity_error": maximum_identity_error,
        "runs_a": runs_a,
        "runs_b": runs_b,
        "mismatches": mismatches,
        "repeat_mismatches": repeat_mismatches,
        "gates": {name: bool(value) for name, value in gates.items()},
        "pass": all(gates.values()),
        "scope": "D62 mechanical parity only; no policy value or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "pass": report["pass"],
                "mode_task_comparisons": comparisons,
                "maximum_reward_identity_error": maximum_identity_error,
                "mismatches": len(mismatches),
                "repeat_mismatches": len(repeat_mismatches),
                "gates": report["gates"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
