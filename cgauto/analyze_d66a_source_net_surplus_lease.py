#!/usr/bin/env python3
"""Analyze D66a's repeated consumed source net-surplus lease gate."""

from __future__ import annotations

import argparse
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
PROTOCOL = ANALYSIS / "d66a-source-net-surplus-lease-protocol-2026-07-21.md"
RUNNER = REPO / "rust/src/bin/d66_source_net_surplus_lease.rs"
D64_BASELINE = ANALYSIS / "d64a-field-gated-late-capitalization-a-9830000-9830015.tsv"
SEEDS = (9_830_002, 9_830_014)
POLICIES = ("d40_control", "source_surplus_lease")
FRUITS = ("plum", "lemon", "apple", "banana")
MISSING_SPECIES = {9_830_002: "lemon", 9_830_014: "plum"}
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


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader), reader.fieldnames or []


def key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def mean(values: list[int | float | bool]) -> float:
    return sum(values) / len(values) if values else 0.0


def index(rows: list[dict[str, str]]) -> dict[str, dict[tuple[int, int, str], dict[str, str]]]:
    result = {policy: {} for policy in POLICIES}
    for row in rows:
        policy = row["policy"]
        if policy not in result:
            raise ValueError(f"unexpected D66 policy {policy!r}")
        task = key(row)
        if task in result[policy]:
            raise ValueError(f"duplicate D66 task {policy} {task}")
        result[policy][task] = row
    return result


def expected_keys() -> set[tuple[int, int, str]]:
    return {(seed, seat, "resident") for seed in SEEDS for seat in (0, 1)}


def historical_controls() -> dict[tuple[int, int, str], dict[str, str]]:
    rows, _ = read_rows(D64_BASELINE)
    return {
        key(row): row
        for row in rows
        if row["policy"] == "d40_control"
        and row["opponent"] == "resident"
        and int(row["map_seed"]) in SEEDS
    }


def summary(rows: list[dict[str, str]]) -> dict:
    return {
        "tasks": len(rows),
        "mean_own_score": mean([int(row["own_score"]) for row in rows]),
        "mean_opponent_score": mean([int(row["opponent_score"]) for row in rows]),
        "mean_margin": mean([int(row["margin"]) for row in rows]),
        "worker_two_rate": mean([int(row["own_workers"]) >= 2 for row in rows]),
        "crop_rate": mean([int(row["own_created_crops"]) > 0 for row in rows]),
        "catastrophic_losses": sum(int(row["margin"]) <= -100 for row in rows),
        "activations": sum(int(row["activations"]) for row in rows),
        "commands": {
            command: sum(int(row[f"{command}_commands"]) for row in rows)
            for command in ("pick", "plant", "harvest", "drop", "wait")
        },
        "lease_failures": sum(int(row["lease_failures"]) for row in rows),
        "bootstrap_failures": sum(int(row["bootstrap_failures"]) for row in rows),
        "mean_lease_duration_turns": mean(
            [
                int(row["duration_turns"]) / int(row["activations"])
                for row in rows
                if int(row["activations"]) > 0
            ]
        ),
    }


def paired(
    lease: dict[tuple[int, int, str], dict[str, str]],
    control: dict[tuple[int, int, str], dict[str, str]],
    keys: list[tuple[int, int, str]],
) -> dict:
    return {
        "tasks": len(keys),
        "mean_own_score_delta": mean(
            [int(lease[item]["own_score"]) - int(control[item]["own_score"]) for item in keys]
        ),
        "mean_opponent_score_delta": mean(
            [
                int(lease[item]["opponent_score"])
                - int(control[item]["opponent_score"])
                for item in keys
            ]
        ),
        "mean_margin_delta": mean(
            [int(lease[item]["margin"]) - int(control[item]["margin"]) for item in keys]
        ),
        "strict_margin_improvements": sum(
            int(lease[item]["margin"]) > int(control[item]["margin"]) for item in keys
        ),
        "strict_margin_regressions": sum(
            int(lease[item]["margin"]) < int(control[item]["margin"]) for item in keys
        ),
    }


def build_report(matrix_a: Path, matrix_b: Path) -> dict:
    repeated = matrix_a.read_bytes() == matrix_b.read_bytes()
    if not repeated:
        raise ValueError("D66 consumed repeats differ")
    rows, fields = read_rows(matrix_a)
    required = {
        "map_seed",
        "seat",
        "opponent",
        "policy",
        "activations",
        "lease_failures",
        "bootstrap_failures",
        "lease_after_worker_two",
        "max_workers",
        *CONTROL_PARITY_FIELDS,
        *(f"activation_{fruit}" for fruit in FRUITS),
        *(f"{command}_commands" for command in ("pick", "plant", "harvest", "drop", "wait")),
    }
    if not required.issubset(fields):
        raise ValueError(f"D66 header missing {sorted(required - set(fields))}")
    indexed = index(rows)
    expected = expected_keys()
    complete = len(rows) == 8 and all(set(indexed[p]) == expected for p in POLICIES)
    historical = historical_controls()
    parity_mismatches = {}
    for item in sorted(expected):
        differences = [
            field
            for field in CONTROL_PARITY_FIELDS
            if indexed["d40_control"][item][field] != historical[item][field]
        ]
        if differences:
            parity_mismatches[f"{item[0]}:{item[1]}:{item[2]}"] = differences
    lease = indexed["source_surplus_lease"]
    worker_two_failures = [
        f"{item[0]}:{item[1]}:{item[2]}"
        for item in sorted(expected)
        if int(lease[item]["own_workers"]) < 2
    ]
    missing_species_failures = [
        f"{item[0]}:{item[1]}:{item[2]}"
        for item in sorted(expected)
        if int(lease[item][f"activation_{MISSING_SPECIES[item[0]]}"]) < 1
    ]
    exact_lease_failures = sum(int(lease[item]["lease_failures"]) for item in expected)
    successful_two_fruit_drops = sum(
        int(lease[item]["drop_commands"]) for item in expected
    )
    mechanical_failure_total = sum(
        int(row[field])
        for row in rows
        for field in (
            "invalid_direct_commands",
            "provenance_failures",
            "deposit_prediction_failures",
            "finite_state_failures",
        )
    )
    reward_identity_failures = sum(
        float(row["reward_identity_error"]) >= 1e-4 for row in rows
    )
    action_accounting_failures = sum(
        sum(int(row[field]) for field in ACTION_FIELDS) != int(row["selected_decisions"])
        for row in rows
    )
    crop_failures = [
        f"{item[0]}:{item[1]}:{item[2]}"
        for item in sorted(expected)
        if int(lease[item]["own_created_crops"]) < 1
    ]
    integrity_pass = (
        complete
        and not parity_mismatches
        and mechanical_failure_total == 0
        and reward_identity_failures == 0
        and action_accounting_failures == 0
    )
    recovery_pass = (
        integrity_pass
        and not worker_two_failures
        and not missing_species_failures
        and not crop_failures
        and exact_lease_failures == 0
        and successful_two_fruit_drops
        == sum(int(lease[item]["activations"]) for item in expected)
    )
    keys = sorted(expected)
    return {
        "schema": "troll-farm-d66a-source-net-surplus-lease-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consumed recovery gate only; fresh value forbidden after failure",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "runner": sha256_file(RUNNER),
            "analyzer": sha256_file(Path(__file__)),
            "matrix_a": sha256_file(matrix_a),
            "matrix_b": sha256_file(matrix_b),
            "d64_baseline": sha256_file(D64_BASELINE),
        },
        "integrity": {
            "repeat_byte_identical": repeated,
            "rows": len(rows),
            "expected_rows": 8,
            "complete_grid": complete,
            "control_parity_mismatch_count": len(parity_mismatches),
            "control_parity_mismatches": parity_mismatches,
            "mechanical_failure_total": mechanical_failure_total,
            "reward_identity_failures": reward_identity_failures,
            "action_accounting_failures": action_accounting_failures,
        },
        "recovery": {
            "worker_two_failures": worker_two_failures,
            "missing_species_activation_failures": missing_species_failures,
            "crop_failures": crop_failures,
            "lease_failures": exact_lease_failures,
            "successful_two_fruit_drops": successful_two_fruit_drops,
            "bootstrap_failures": sum(
                int(lease[item]["bootstrap_failures"]) for item in expected
            ),
            "lease_after_worker_two": sum(
                int(lease[item]["lease_after_worker_two"]) for item in expected
            ),
            "max_workers": max(int(lease[item]["max_workers"]) for item in expected),
            "pass": recovery_pass,
        },
        "summaries": {
            policy: summary([indexed[policy][item] for item in keys]) for policy in POLICIES
        },
        "paired_lease_vs_control": paired(lease, indexed["d40_control"], keys),
        "fresh": {"status": "eligible_not_run" if recovery_pass else "forbidden_by_protocol"},
        "decision": {
            "status": "consumed_recovery_pass" if recovery_pass else "closed_consumed_recovery_failure",
            "next_experiment": (
                "fresh_d66_repeated_value_gate"
                if recovery_pass
                else "multi_source_bill_capitalization_state_machine"
            ),
            "construct_candidate": False,
            "open_fresh": recovery_pass,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def analyze(matrix_a: Path, matrix_b: Path, output: Path) -> dict:
    report = build_report(matrix_a, matrix_b)
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix_a", type=Path)
    parser.add_argument("matrix_b", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = analyze(args.matrix_a, args.matrix_b, args.output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
