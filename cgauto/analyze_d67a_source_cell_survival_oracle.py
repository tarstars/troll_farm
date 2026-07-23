#!/usr/bin/env python3
"""Analyze D67a's exhaustive consumed source-cell survival oracle."""

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
PROTOCOL = ANALYSIS / "d67a-source-cell-survival-oracle-protocol-2026-07-21.md"
RUNNER = REPO / "rust/src/bin/d67_source_cell_survival_oracle.rs"
SEEDS = (9_830_002, 9_830_014)
EXPECTED_COUNTS = {
    (9_830_002, 0): 23,
    (9_830_002, 1): 23,
    (9_830_014, 0): 21,
    (9_830_014, 1): 21,
}
PREFIX_FIELDS = (
    "missing_species",
    "prefix_turn",
    "prefix_state_hash",
    "prefix_action_hash",
    "prefix_bootstrap_mask",
    "prefix_bank",
    "prefix_carry",
    "prefix_ripe",
    "candidate_count",
)


def mean(values: list[int | float | bool]) -> float:
    return sum(values) / len(values) if values else 0.0


def read_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader), reader.fieldnames or []


def task_key(row: dict[str, str]) -> tuple[int, int]:
    return int(row["map_seed"]), int(row["seat"])


def recompute_success(row: dict[str, str]) -> bool:
    return (
        int(row["pick_commands"]) == 1
        and int(row["plant_commands"]) == 1
        and int(row["harvest_commands"]) == 2
        and int(row["drop_commands"]) == 1
        and int(row["bank_delta"]) == 1
        and int(row["invalidated_delta"]) == 0
        and int(row["invalid_direct_delta"]) == 0
        and int(row["provenance_delta"]) == 0
        and int(row["deposit_prediction_delta"]) == 0
    )


def summarize(rows: list[dict[str, str]]) -> dict:
    ordered = sorted(rows, key=lambda row: int(row["target_rank"]))
    viable = [row for row in ordered if int(row["success"])]
    default = next(row for row in ordered if int(row["original_target"]))
    harvest_counts = Counter(int(row["harvest_commands"]) for row in ordered)
    return {
        "candidate_cells": len(ordered),
        "viable_cells": len(viable),
        "viable_rate": len(viable) / len(ordered),
        "harvest_command_counts": {
            str(count): amount for count, amount in sorted(harvest_counts.items())
        },
        "two_fruit_drops": sum(int(row["drop_commands"]) for row in ordered),
        "invalidated_leases": sum(int(row["invalidated_delta"]) > 0 for row in ordered),
        "roots_present_after": sum(int(row["root_present_after"]) for row in ordered),
        "mean_wait_commands": mean([int(row["wait_commands"]) for row in ordered]),
        "mean_duration_turns": mean([int(row["duration_turns"]) for row in ordered]),
        "default_target": {
            "cell": [int(default["target_x"]), int(default["target_y"])],
            "success": bool(int(default["success"])),
            "harvest_commands": int(default["harvest_commands"]),
            "drop_commands": int(default["drop_commands"]),
            "duration_turns": int(default["duration_turns"]),
        },
        "viable_targets": [
            {
                "rank": int(row["target_rank"]),
                "cell": [int(row["target_x"]), int(row["target_y"])],
                "safety_margin": int(row["safety_margin"]),
                "wet": bool(int(row["wet"])),
            }
            for row in viable
        ],
    }


def build_report(matrix_a: Path, matrix_b: Path) -> dict:
    repeated = matrix_a.read_bytes() == matrix_b.read_bytes()
    if not repeated:
        raise ValueError("D67 repeats differ")
    rows, fields = read_rows(matrix_a)
    required = {
        "map_seed",
        "seat",
        "target_rank",
        "target_x",
        "target_y",
        "original_target",
        "success",
        *PREFIX_FIELDS,
    }
    if not required.issubset(fields):
        raise ValueError(f"D67 header missing {sorted(required - set(fields))}")
    groups: dict[tuple[int, int], list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(task_key(row), []).append(row)
    expected_tasks = set(EXPECTED_COUNTS)
    count_failures = 0
    rank_failures = 0
    cell_duplicate_failures = 0
    prefix_mismatches = 0
    original_target_failures = 0
    command_setup_failures = 0
    mechanical_failures = 0
    success_accounting_failures = 0
    trace_hash_failures = 0
    for task, task_rows in groups.items():
        ordered = sorted(task_rows, key=lambda row: int(row["target_rank"]))
        count_failures += int(len(ordered) != EXPECTED_COUNTS.get(task, -1))
        rank_failures += int(
            [int(row["target_rank"]) for row in ordered] != list(range(len(ordered)))
        )
        cell_duplicate_failures += int(
            len({(row["target_x"], row["target_y"]) for row in ordered}) != len(ordered)
        )
        for field in PREFIX_FIELDS:
            prefix_mismatches += int(len({row[field] for row in ordered}) != 1)
        original_target_failures += int(
            sum(int(row["original_target"]) for row in ordered) != 1
            or ordered[0]["original_target"] != "1"
        )
        command_setup_failures += sum(
            int(row["pick_commands"]) != 1 or int(row["plant_commands"]) != 1
            for row in ordered
        )
        mechanical_failures += sum(
            int(row[field])
            for row in ordered
            for field in (
                "invalid_direct_delta",
                "provenance_delta",
                "deposit_prediction_delta",
            )
        )
        success_accounting_failures += sum(
            bool(int(row["success"])) != recompute_success(row) for row in ordered
        )
        trace_hashes = [row["trace_hash"] for row in ordered]
        trace_hash_failures += int(len(trace_hashes) != len(set(trace_hashes)))
    integrity = {
        "repeat_byte_identical": repeated,
        "tasks": len(groups),
        "rows": len(rows),
        "complete_grid": set(groups) == expected_tasks,
        "candidate_count_failures": count_failures,
        "rank_failures": rank_failures,
        "cell_duplicate_failures": cell_duplicate_failures,
        "prefix_mismatches": prefix_mismatches,
        "original_target_failures": original_target_failures,
        "command_setup_failures": command_setup_failures,
        "mechanical_failure_total": mechanical_failures,
        "success_accounting_failures": success_accounting_failures,
        "trace_hash_failures": trace_hash_failures,
    }
    summaries = {
        f"{seed}:{seat}:resident": summarize(task_rows)
        for (seed, seat), task_rows in sorted(groups.items())
    }
    failed_viable = {
        f"9830002:{seat}:resident": summaries[f"9830002:{seat}:resident"]["viable_cells"]
        for seat in (0, 1)
    }
    all_viable = sum(item["viable_cells"] for item in summaries.values())
    harvest_zero = [row for row in rows if int(row["harvest_commands"]) == 0]
    harvest_one = [row for row in rows if int(row["harvest_commands"]) == 1]
    integrity_pass = integrity["complete_grid"] and all(
        integrity[field] == 0
        for field in (
            "candidate_count_failures",
            "rank_failures",
            "cell_duplicate_failures",
            "prefix_mismatches",
            "original_target_failures",
            "command_setup_failures",
            "mechanical_failure_total",
            "success_accounting_failures",
            "trace_hash_failures",
        )
    )
    placement_closed = integrity_pass and any(value == 0 for value in failed_viable.values())
    return {
        "schema": "troll-farm-d67a-source-cell-survival-oracle-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consumed exhaustive placement feasibility only; no selector or value claim",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "runner": sha256_file(RUNNER),
            "analyzer": sha256_file(Path(__file__)),
            "matrix_a": sha256_file(matrix_a),
            "matrix_b": sha256_file(matrix_b),
        },
        "integrity": integrity,
        "tasks": summaries,
        "aggregate": {
            "candidate_cells": len(rows),
            "viable_cells": all_viable,
            "two_fruit_drops": sum(int(row["drop_commands"]) for row in rows),
            "invalidated_leases": sum(int(row["invalidated_delta"]) > 0 for row in rows),
            "roots_present_after": sum(int(row["root_present_after"]) for row in rows),
            "harvest_zero_cells": len(harvest_zero),
            "harvest_one_cells": len(harvest_one),
            "harvest_zero_mean_safety_margin": mean(
                [int(row["safety_margin"]) for row in harvest_zero]
            ),
            "harvest_one_mean_safety_margin": mean(
                [int(row["safety_margin"]) for row in harvest_one]
            ),
            "harvest_zero_wet_rate": mean([int(row["wet"]) for row in harvest_zero]),
            "harvest_one_wet_rate": mean([int(row["wet"]) for row in harvest_one]),
        },
        "failed_seat_viable_cells": failed_viable,
        "decision": {
            "status": "placement_closed" if placement_closed else "placement_feasible_or_invalid",
            "next_experiment": (
                "multi_source_bill_capitalization_state_machine"
                if placement_closed
                else "fresh_result_blind_geometry_survival_family"
            ),
            "select_cell_rule": False,
            "construct_candidate": False,
            "open_fresh_value": False,
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
