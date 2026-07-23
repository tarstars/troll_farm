#!/usr/bin/env python3
"""Analyze D68a's consumed bill-capitalization portfolio gate."""

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
PROTOCOL = ANALYSIS / "d68a-bill-capitalization-portfolio-protocol-2026-07-21.md"
RUNNER = REPO / "rust/src/bin/d68_bill_capitalization_portfolio.rs"
D66_CONTROL = ANALYSIS / "d66a-consumed-source-net-surplus-a-9830002-9830014.tsv"
D67_PREFIX = ANALYSIS / "d67a-source-cell-survival-oracle-a.tsv"
SEEDS = (9_830_002, 9_830_014)
POLICIES = ("d40_control", "bill_portfolio")
FRUITS = ("plum", "lemon", "apple", "banana")
PREFIX_FIELDS = (
    "prefix_turn",
    "prefix_state_hash",
    "prefix_action_hash",
    "prefix_bootstrap_mask",
    "prefix_bank",
    "prefix_carry",
    "prefix_ripe",
)
VIOLATION_FIELDS = (
    "formula_violations",
    "carry_before_plant_violations",
    "affordable_plant_violations",
    "harvest_target_violations",
    "interventions_after_worker_two",
    "finite_state_failures",
)


def mean(values: list[int | float | bool]) -> float:
    return sum(values) / len(values) if values else 0.0


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader), reader.fieldnames or []


def task_key(row: dict[str, str]) -> tuple[int, int]:
    return int(row["map_seed"]), int(row["seat"])


def row_key(row: dict[str, str]) -> tuple[str, int, int]:
    seed, seat = task_key(row)
    return row["policy"], seed, seat


def expected_keys() -> set[tuple[str, int, int]]:
    return {
        (policy, seed, seat)
        for policy in POLICIES
        for seed in SEEDS
        for seat in (0, 1)
    }


def int_value(row: dict[str, str], field: str) -> int:
    return int(row[field])


def task_pass(row: dict[str, str]) -> bool:
    """Recompute the frozen consumed mechanism gate for one treatment task."""

    mechanical = sum(
        int_value(row, field)
        for field in (
            "invalid_direct_commands",
            "provenance_failures",
            "deposit_prediction_failures",
            *VIOLATION_FIELDS,
        )
    )
    return (
        row["policy"] == "bill_portfolio"
        and int_value(row, "prefix_seen") == 1
        and int_value(row, "own_workers") >= 2
        and int_value(row, "first_worker_two_turn") >= 0
        and int_value(row, "forced_harvest_deposits") >= 1
        and int_value(row, "missing_bank_progress") > 0
        and int_value(row, "own_created_crops") > 0
        and int_value(row, "max_workers") <= 3
        and mechanical == 0
    )


def control_reference() -> dict[tuple[int, int], dict[str, str]]:
    rows, _ = read_rows(D66_CONTROL)
    return {
        task_key(row): row
        for row in rows
        if row["policy"] == "d40_control"
    }


def prefix_reference() -> dict[tuple[int, int], dict[str, str]]:
    rows, _ = read_rows(D67_PREFIX)
    result: dict[tuple[int, int], dict[str, str]] = {}
    for row in rows:
        result.setdefault(task_key(row), row)
    return result


def species_flow(row: dict[str, str]) -> dict[str, dict[str, int]]:
    return {
        fruit: {
            "source_investments": int_value(row, f"source_transactions_{fruit}"),
            "forced_harvest_jobs": int_value(row, f"forced_harvest_jobs_{fruit}"),
            "successful_harvest_deposits": int_value(
                row, f"forced_harvest_deposits_{fruit}"
            ),
            "deposited_units": int_value(row, f"forced_harvest_units_{fruit}"),
            "experimental_net_units": int_value(row, f"forced_harvest_units_{fruit}")
            - int_value(row, f"source_transactions_{fruit}"),
            "max_bank": int_value(row, f"max_bank_{fruit}"),
            "live_sources_peak": int_value(row, f"live_sources_peak_{fruit}"),
            "target_sources_peak": int_value(row, f"target_sources_peak_{fruit}"),
        }
        for fruit in FRUITS
    }


def summarize_task(
    control: dict[str, str], treatment: dict[str, str]
) -> dict[str, object]:
    return {
        "control_margin": int_value(control, "margin"),
        "portfolio_margin": int_value(treatment, "margin"),
        "paired_margin_delta": int_value(treatment, "margin")
        - int_value(control, "margin"),
        "control_workers": int_value(control, "own_workers"),
        "portfolio_workers": int_value(treatment, "own_workers"),
        "first_worker_two_turn": int_value(treatment, "first_worker_two_turn"),
        "first_bill_affordable_turn": int_value(treatment, "first_bill_affordable_turn"),
        "prefix_missing_bank": int_value(treatment, "prefix_missing_bank"),
        "max_missing_bank": int_value(treatment, "max_missing_bank"),
        "missing_bank_progress": int_value(treatment, "missing_bank_progress"),
        "interventions": int_value(treatment, "interventions"),
        "source_transactions": int_value(treatment, "source_transactions"),
        "forced_harvest_jobs": int_value(treatment, "forced_harvest_jobs"),
        "forced_harvest_deposits": int_value(treatment, "forced_harvest_deposits"),
        "threat_peak": int_value(treatment, "threat_peak"),
        "species_flow": species_flow(treatment),
        "mechanism_pass": task_pass(treatment),
    }


def build_report(matrix_a: Path, matrix_b: Path) -> dict:
    repeated = matrix_a.read_bytes() == matrix_b.read_bytes()
    if not repeated:
        raise ValueError("D68 repeats differ")
    rows, fields = read_rows(matrix_a)
    required = {
        "map_seed",
        "seat",
        "policy",
        "margin",
        "action_hash",
        "state_hash",
        "reward_identity_error",
        "source_transactions",
        "source_pick_commands",
        "source_plant_commands",
        "forced_harvest_jobs",
        "forced_harvest_deposits",
        "forced_harvest_failures",
        "first_worker_two_turn",
        "max_workers",
        "missing_bank_progress",
        "prefix_seen",
        *PREFIX_FIELDS,
        *VIOLATION_FIELDS,
    }
    for fruit in FRUITS:
        required.update(
            {
                f"source_transactions_{fruit}",
                f"forced_harvest_jobs_{fruit}",
                f"forced_harvest_deposits_{fruit}",
                f"forced_harvest_units_{fruit}",
                f"max_bank_{fruit}",
                f"live_sources_peak_{fruit}",
                f"target_sources_peak_{fruit}",
            }
        )
    if not required.issubset(fields):
        raise ValueError(f"D68 header missing {sorted(required - set(fields))}")
    keyed = {row_key(row): row for row in rows}
    duplicate_rows = len(rows) - len(keyed)
    complete_grid = set(keyed) == expected_keys()

    d66 = control_reference()
    control_parity_failures = 0
    for seed in SEEDS:
        for seat in (0, 1):
            actual = keyed.get(("d40_control", seed, seat))
            reference = d66.get((seed, seat))
            if actual is None or reference is None:
                control_parity_failures += 1
                continue
            control_parity_failures += int(
                any(
                    actual[field] != reference[field]
                    for field in (
                        "turn",
                        "own_score",
                        "opponent_score",
                        "own_workers",
                        "successful_trains",
                        "action_hash",
                        "state_hash",
                    )
                )
            )

    d67 = prefix_reference()
    prefix_parity_failures = 0
    for seed in SEEDS:
        for seat in (0, 1):
            actual = keyed.get(("bill_portfolio", seed, seat))
            reference = d67.get((seed, seat))
            if actual is None or reference is None:
                prefix_parity_failures += 1
                continue
            prefix_parity_failures += int(actual["prefix_seen"] != "1")
            prefix_parity_failures += int(actual["missing_species"] != reference["missing_species"])
            prefix_parity_failures += sum(
                actual[field] != reference[field] for field in PREFIX_FIELDS
            )

    mechanical_failure_total = sum(
        int_value(row, field)
        for row in rows
        for field in (
            "invalid_direct_commands",
            "provenance_failures",
            "deposit_prediction_failures",
        )
    )
    policy_violation_total = sum(
        int_value(row, field) for row in rows for field in VIOLATION_FIELDS
    )
    reward_identity_failures = sum(
        float(row["reward_identity_error"]) > 1e-5 for row in rows
    )
    source_command_accounting_failures = sum(
        int_value(row, "source_transactions") != int_value(row, "source_pick_commands")
        or int_value(row, "source_transactions") != int_value(row, "source_plant_commands")
        or int_value(row, "source_transactions")
        != sum(int_value(row, f"source_transactions_{fruit}") for fruit in FRUITS)
        for row in rows
    )
    harvest_accounting_failures = sum(
        int_value(row, "forced_harvest_jobs")
        != sum(int_value(row, f"forced_harvest_jobs_{fruit}") for fruit in FRUITS)
        or int_value(row, "forced_harvest_deposits")
        != sum(int_value(row, f"forced_harvest_deposits_{fruit}") for fruit in FRUITS)
        or int_value(row, "forced_harvest_jobs")
        != int_value(row, "forced_harvest_deposits")
        + int_value(row, "forced_harvest_failures")
        for row in rows
    )
    worker_cap_failures = sum(int_value(row, "max_workers") > 3 for row in rows)
    action_accounting_failures = sum(
        sum(int_value(row, field) for field in (
            "train_none",
            "train_producer",
            "train_chopper",
            "idle",
            "bank",
            "fell_bank",
            "harvest_bank",
            "renew",
            "mine_bank",
        ))
        != int_value(row, "selected_decisions")
        for row in rows
    )
    integrity = {
        "repeat_byte_identical": repeated,
        "rows": len(rows),
        "complete_grid": complete_grid,
        "duplicate_rows": duplicate_rows,
        "control_parity_failures": control_parity_failures,
        "prefix_parity_failures": prefix_parity_failures,
        "mechanical_failure_total": mechanical_failure_total,
        "policy_violation_total": policy_violation_total,
        "reward_identity_failures": reward_identity_failures,
        "source_command_accounting_failures": source_command_accounting_failures,
        "harvest_accounting_failures": harvest_accounting_failures,
        "worker_cap_failures": worker_cap_failures,
        "action_accounting_failures": action_accounting_failures,
    }
    integrity_pass = complete_grid and duplicate_rows == 0 and all(
        integrity[field] == 0
        for field in (
            "control_parity_failures",
            "prefix_parity_failures",
            "mechanical_failure_total",
            "policy_violation_total",
            "reward_identity_failures",
            "source_command_accounting_failures",
            "harvest_accounting_failures",
            "worker_cap_failures",
            "action_accounting_failures",
        )
    )

    tasks: dict[str, dict[str, object]] = {}
    for seed in SEEDS:
        for seat in (0, 1):
            control = keyed[("d40_control", seed, seat)]
            treatment = keyed[("bill_portfolio", seed, seat)]
            tasks[f"{seed}:{seat}:resident"] = summarize_task(control, treatment)
    passes = {task: bool(summary["mechanism_pass"]) for task, summary in tasks.items()}
    all_pass = integrity_pass and all(passes.values())
    failed_seed_pass = all(passes[f"9830002:{seat}:resident"] for seat in (0, 1))
    treatment_rows = [
        keyed[("bill_portfolio", seed, seat)] for seed in SEEDS for seat in (0, 1)
    ]
    paired_deltas = [int(tasks[task]["paired_margin_delta"]) for task in sorted(tasks)]
    return {
        "schema": "troll-farm-d68a-bill-capitalization-portfolio-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consumed bill-capitalization mechanism only; no fresh value or candidate claim",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "runner": sha256_file(RUNNER),
            "analyzer": sha256_file(Path(__file__)),
            "matrix_a": sha256_file(matrix_a),
            "matrix_b": sha256_file(matrix_b),
            "d66_control": sha256_file(D66_CONTROL),
            "d67_prefix": sha256_file(D67_PREFIX),
        },
        "integrity": integrity,
        "tasks": tasks,
        "aggregate": {
            "mechanism_passes": sum(passes.values()),
            "mechanism_tasks": len(passes),
            "worker_two_tasks": sum(int_value(row, "own_workers") >= 2 for row in treatment_rows),
            "portfolio_closed_tasks": sum(
                int_value(row, "portfolio_closed") for row in treatment_rows
            ),
            "source_transactions": sum(
                int_value(row, "source_transactions") for row in treatment_rows
            ),
            "forced_harvest_jobs": sum(
                int_value(row, "forced_harvest_jobs") for row in treatment_rows
            ),
            "forced_harvest_deposits": sum(
                int_value(row, "forced_harvest_deposits") for row in treatment_rows
            ),
            "paired_margin_deltas": paired_deltas,
            "mean_paired_margin_delta": mean(paired_deltas),
        },
        "gate": {
            "integrity_pass": integrity_pass,
            "failed_seed_pass": failed_seed_pass,
            "all_tasks_pass": all_pass,
            "per_task": passes,
        },
        "decision": {
            "status": "consumed_gate_passed" if all_pass else "consumed_gate_failed",
            "next_experiment": (
                "fresh_d40_value_and_robustness"
                if all_pass
                else "whole_game_opening_architecture_and_capitalization_timing"
            ),
            "open_fresh_value": all_pass,
            "construct_candidate": False,
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
