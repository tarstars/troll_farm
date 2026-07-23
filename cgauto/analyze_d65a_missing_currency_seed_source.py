#!/usr/bin/env python3
"""Analyze D65a's consumed source-repair gate and, only if eligible, fresh repeats."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d65a-missing-currency-seed-source-protocol-2026-07-21.md"
RUNNER = REPO / "rust/src/bin/d65_missing_currency_seed_source.rs"
D64_BASELINE = ANALYSIS / "d64a-field-gated-late-capitalization-a-9830000-9830015.tsv"
CONSUMED_SEEDS = (9_830_002, 9_830_014)
FRESH_START_SEED = 9_831_000
FRESH_MAPS = 32
POLICIES = ("d40_control", "seed_source_repair")
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
FRUITS = ("plum", "lemon", "apple", "banana")
ACTION_FIELDS = (
    "train_none",
    "train_producer",
    "train_chopper",
    "idle",
    "bank",
    "fell_bank",
    "harvest_bank",
    "renew",
    "mine_bank",
)
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "bootstrap_failures",
    "source_job_failures",
    "finite_state_failures",
)
CONTROL_PARITY_FIELDS = (
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
    "own_workers",
    "opponent_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "selected_decisions",
    "selected_jobs",
    "selected_nonidle_jobs",
    "selected_renew_jobs",
    "own_created_crops",
    "opponent_created_crops",
    "ambiguous_created_crops",
    "action_hash",
    "state_hash",
    "terminal_live_own_plants",
    *ACTION_FIELDS,
)
MISSING_SPECIES = {
    9_830_002: "lemon",
    9_830_014: "plum",
}


def read_matrix(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader), reader.fieldnames or []


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def mean(values: list[int | float | bool]) -> float:
    return sum(values) / len(values) if values else 0.0


def index_rows(
    rows: list[dict[str, str]],
) -> dict[str, dict[tuple[int, int, str], dict[str, str]]]:
    indexed = {policy: {} for policy in POLICIES}
    for row in rows:
        policy = row["policy"]
        if policy not in indexed:
            raise ValueError(f"unexpected D65 policy {policy!r}")
        key = task_key(row)
        if key in indexed[policy]:
            raise ValueError(f"duplicate D65 task {policy} {key}")
        indexed[policy][key] = row
    return indexed


def consumed_expected_keys() -> set[tuple[int, int, str]]:
    return {(seed, seat, "resident") for seed in CONSUMED_SEEDS for seat in (0, 1)}


def fresh_expected_keys() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(FRESH_START_SEED, FRESH_START_SEED + FRESH_MAPS)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }


def d64_consumed_controls() -> dict[tuple[int, int, str], dict[str, str]]:
    rows, _ = read_matrix(D64_BASELINE)
    return {
        task_key(row): row
        for row in rows
        if row["policy"] == "d40_control"
        and row["opponent"] == "resident"
        and int(row["map_seed"]) in CONSUMED_SEEDS
    }


def summarize(rows: list[dict[str, str]]) -> dict:
    return {
        "tasks": len(rows),
        "mean_own_score": mean([int(row["own_score"]) for row in rows]),
        "mean_opponent_score": mean([int(row["opponent_score"]) for row in rows]),
        "mean_margin": mean([int(row["margin"]) for row in rows]),
        "worker_two_rate": mean([int(row["own_workers"]) >= 2 for row in rows]),
        "crop_rate": mean([int(row["own_created_crops"]) > 0 for row in rows]),
        "catastrophic_losses": sum(int(row["margin"]) <= -100 for row in rows),
        "activations": sum(int(row["activations"]) for row in rows),
        "activation_species": {
            fruit: sum(int(row[f"activation_{fruit}"]) for row in rows)
            for fruit in FRUITS
        },
    }


def paired_delta(
    repair: dict[tuple[int, int, str], dict[str, str]],
    control: dict[tuple[int, int, str], dict[str, str]],
    keys: list[tuple[int, int, str]],
) -> dict:
    return {
        "tasks": len(keys),
        "mean_own_score_delta": mean(
            [int(repair[key]["own_score"]) - int(control[key]["own_score"]) for key in keys]
        ),
        "mean_opponent_score_delta": mean(
            [
                int(repair[key]["opponent_score"])
                - int(control[key]["opponent_score"])
                for key in keys
            ]
        ),
        "mean_margin_delta": mean(
            [int(repair[key]["margin"]) - int(control[key]["margin"]) for key in keys]
        ),
        "strict_margin_improvements": sum(
            int(repair[key]["margin"]) > int(control[key]["margin"]) for key in keys
        ),
        "strict_margin_regressions": sum(
            int(repair[key]["margin"]) < int(control[key]["margin"]) for key in keys
        ),
    }


def consumed_report(rows: list[dict[str, str]], fields: list[str]) -> dict:
    required = {
        "scope",
        "map_seed",
        "seat",
        "opponent",
        "policy",
        "own_workers",
        "own_created_crops",
        "activations",
        "bootstrap_after_worker_two",
        "max_workers",
        *FAILURE_FIELDS,
        *ACTION_FIELDS,
        *CONTROL_PARITY_FIELDS,
        *(f"activation_{fruit}" for fruit in FRUITS),
    }
    if not required.issubset(fields):
        raise ValueError(f"D65 consumed header missing {sorted(required - set(fields))}")
    indexed = index_rows(rows)
    expected = consumed_expected_keys()
    complete = (
        len(rows) == 2 * len(expected)
        and all(set(indexed[policy]) == expected for policy in POLICIES)
        and all(row["scope"] == "consumed" for row in rows)
    )
    baseline = d64_consumed_controls()
    control_parity_mismatches: dict[str, list[str]] = {}
    for key in sorted(expected):
        differences = [
            field
            for field in CONTROL_PARITY_FIELDS
            if indexed["d40_control"][key][field] != baseline[key][field]
        ]
        if differences:
            control_parity_mismatches[f"{key[0]}:{key[1]}:{key[2]}"] = differences

    repair = indexed["seed_source_repair"]
    worker_two_failures = [
        f"{key[0]}:{key[1]}:{key[2]}"
        for key in sorted(expected)
        if int(repair[key]["own_workers"]) < 2
    ]
    missing_species_failures = [
        f"{key[0]}:{key[1]}:{key[2]}"
        for key in sorted(expected)
        if int(repair[key][f"activation_{MISSING_SPECIES[key[0]]}"]) < 1
    ]
    mechanical_failure_total = sum(
        int(row[field]) for row in rows for field in FAILURE_FIELDS
    )
    reward_identity_failures = sum(
        float(row["reward_identity_error"]) >= 1e-4 for row in rows
    )
    action_accounting_failures = sum(
        sum(int(row[field]) for field in ACTION_FIELDS) != int(row["selected_decisions"])
        for row in rows
    )
    crop_failures = [
        f"{key[0]}:{key[1]}:{key[2]}"
        for key in sorted(expected)
        if int(repair[key]["own_created_crops"]) < 1
    ]
    integrity_pass = (
        complete
        and not control_parity_mismatches
        and mechanical_failure_total == 0
        and reward_identity_failures == 0
        and action_accounting_failures == 0
    )
    recovery_pass = (
        integrity_pass
        and not worker_two_failures
        and not missing_species_failures
        and not crop_failures
    )
    keys = sorted(expected)
    return {
        "integrity": {
            "rows": len(rows),
            "expected_rows": 8,
            "complete_grid": complete,
            "control_parity_mismatch_count": len(control_parity_mismatches),
            "control_parity_mismatches": control_parity_mismatches,
            "mechanical_failure_total": mechanical_failure_total,
            "reward_identity_failures": reward_identity_failures,
            "action_accounting_failures": action_accounting_failures,
        },
        "recovery": {
            "worker_two_failures": worker_two_failures,
            "missing_species_failures": missing_species_failures,
            "crop_failures": crop_failures,
            "repair_bootstrap_after_worker_two": sum(
                int(repair[key]["bootstrap_after_worker_two"]) for key in keys
            ),
            "repair_max_workers": max(int(repair[key]["max_workers"]) for key in keys),
            "pass": recovery_pass,
        },
        "summaries": {
            policy: summarize([indexed[policy][key] for key in keys]) for policy in POLICIES
        },
        "paired_repair_vs_control": paired_delta(
            repair, indexed["d40_control"], keys
        ),
        "pass": recovery_pass,
    }


def build_report(consumed: Path) -> dict:
    rows, fields = read_matrix(consumed)
    consumed_gate = consumed_report(rows, fields)
    passed = consumed_gate["pass"]
    return {
        "schema": "troll-farm-d65a-missing-currency-seed-source-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consumed repair gate only; fresh value forbidden after recovery failure",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "runner": sha256_file(RUNNER),
            "analyzer": sha256_file(Path(__file__)),
            "consumed_matrix": sha256_file(consumed),
            "d64_baseline_matrix": sha256_file(D64_BASELINE),
        },
        "consumed": consumed_gate,
        "fresh": {
            "status": "eligible_not_run" if passed else "forbidden_by_protocol",
            "matrices_run": 0,
        },
        "decision": {
            "status": "consumed_recovery_pass" if passed else "closed_consumed_recovery_failure",
            "run_fresh": passed,
            "next_experiment": (
                "fresh_d65_repeated_value_gate"
                if passed
                else "missing_species_source_survival_audit"
            ),
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def analyze(consumed: Path, output: Path) -> dict:
    report = build_report(consumed)
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consumed", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = analyze(args.consumed, args.output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
