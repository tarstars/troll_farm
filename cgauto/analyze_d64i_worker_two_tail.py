#!/usr/bin/env python3
"""Classify the exact D64 worker-two safety tail from frozen D40 traces."""

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
PROTOCOL = ANALYSIS / "d64i-worker-two-tail-audit-protocol-2026-07-21.md"
RUNNER = REPO / "rust/src/bin/d64_worker_two_tail_audit.rs"
SEEDS = (9_830_002, 9_830_014)
RESOURCES = ("plum", "lemon", "apple", "banana", "iron", "wood")


def vector(value: str) -> list[int]:
    result = [int(item) for item in value.split(",")]
    if len(result) != 6:
        raise ValueError(f"expected six-vector, got {value!r}")
    return result


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def classify(rows: list[dict[str, str]]) -> str:
    if any(
        int(row["bank_deficit_total"]) == 0
        and int(row["shack_occupied"]) == 0
        for row in rows
    ):
        return "transaction_or_shack"
    if any(int(row["bank_carry_deficit_total"]) == 0 for row in rows):
        return "deposit_materialization"
    if any(int(row["bank_carry_ripe_deficit_total"]) == 0 for row in rows):
        return "ripe_acquisition"
    if all(int(row["bank_carry_ripe_deficit_total"]) > 0 for row in rows):
        return "source_availability"
    return "unexplained"


def min_vector(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    values = [vector(row[field]) for row in rows]
    return {
        resource: min(row[index] for row in values)
        for index, resource in enumerate(RESOURCES)
    }


def max_vector(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    values = [vector(row[field]) for row in rows]
    return {
        resource: max(row[index] for row in values)
        for index, resource in enumerate(RESOURCES)
    }


def summarize_trace(rows: list[dict[str, str]]) -> dict:
    ordered = sorted(rows, key=lambda row: int(row["decision"]))
    initial_deficit = vector(ordered[0]["bank_deficit"])
    missing = [RESOURCES[index] for index, amount in enumerate(initial_deficit) if amount > 0]
    last_available_turn = {}
    for resource in missing:
        index = RESOURCES.index(resource)
        available_turns = [
            int(row["turn_before"])
            for row in ordered
            if vector(row["carry"])[index] > 0
            or vector(row["ripe"])[index] > 0
            or vector(row["bank"])[index] >= (5 if index in (0, 1) else 2)
        ]
        last_available_turn[resource] = max(available_turns) if available_turns else None
    return {
        "decisions": len(ordered),
        "endpoint_turn": int(ordered[-1]["turn_after"]),
        "endpoint_done": bool(int(ordered[-1]["done"])),
        "created_worker_two": any(int(row["created_worker_two"]) for row in ordered),
        "endpoint_workers": int(ordered[-1]["workers_after"]),
        "classification": classify(ordered),
        "initial_missing_resources": missing,
        "minimum_bank_deficit": min_vector(ordered, "bank_deficit"),
        "minimum_bank_carry_deficit": min_vector(ordered, "bank_carry_deficit"),
        "minimum_bank_carry_ripe_deficit": min_vector(
            ordered, "bank_carry_ripe_deficit"
        ),
        "maximum_bank": max_vector(ordered, "bank"),
        "maximum_carry": max_vector(ordered, "carry"),
        "maximum_ripe": max_vector(ordered, "ripe"),
        "maximum_plant_counts": max_vector(ordered, "plant_counts"),
        "maximum_plant_fruits": max_vector(ordered, "plant_fruits"),
        "last_missing_resource_available_turn": last_available_turn,
        "branch_counts": dict(sorted(Counter(row["branch"] for row in ordered).items())),
        "job_counts": dict(sorted(Counter(row["job_kind"] for row in ordered).items())),
        "job_fruit_counts": dict(
            sorted(Counter(row["job_fruit"] for row in ordered).items())
        ),
        "ripe_cover_decisions": sum(
            int(row["bank_carry_ripe_deficit_total"]) == 0 for row in ordered
        ),
        "carry_cover_decisions": sum(
            int(row["bank_carry_deficit_total"]) == 0 for row in ordered
        ),
        "bank_cover_clear_decisions": sum(
            int(row["bank_deficit_total"]) == 0
            and int(row["shack_occupied"]) == 0
            for row in ordered
        ),
        "terminal_failures": {
            field: int(ordered[-1][field])
            for field in (
                "invalid_direct_commands",
                "provenance_failures",
                "deposit_prediction_failures",
            )
        },
    }


def validate(rows: list[dict[str, str]]) -> tuple[dict, dict[tuple[int, int, str], list[dict]]]:
    groups: dict[tuple[int, int, str], list[dict]] = {}
    for row in rows:
        groups.setdefault(task_key(row), []).append(row)
    expected = {
        (seed, seat, opponent)
        for seed in SEEDS
        for seat in (0, 1)
        for opponent in ("resident", "gold_adaptive")
    }
    if set(groups) != expected:
        raise ValueError("D64i trace grid differs from frozen cohort")
    chain_failures = 0
    index_failures = 0
    trace_hash_failures = 0
    mechanical_failures = 0
    for task_rows in groups.values():
        ordered = sorted(task_rows, key=lambda row: int(row["decision"]))
        index_failures += int(
            [int(row["decision"]) for row in ordered] != list(range(1, len(ordered) + 1))
        )
        for previous, current in zip(ordered, ordered[1:]):
            chain_failures += int(
                previous["state_hash_after"] != current["state_hash_before"]
                or previous["turn_after"] != current["turn_before"]
            )
        hashes = [int(row["trace_hash"]) for row in ordered]
        trace_hash_failures += int(len(hashes) != len(set(hashes)))
        mechanical_failures += sum(
            int(row[field])
            for row in ordered
            for field in (
                "invalid_direct_commands",
                "provenance_failures",
                "deposit_prediction_failures",
            )
        )
    target_keys = [key for key in sorted(groups) if key[2] == "resident"]
    control_keys = [key for key in sorted(groups) if key[2] == "gold_adaptive"]
    target_contract_failures = sum(
        not bool(int(sorted(groups[key], key=lambda row: int(row["decision"]))[-1]["done"]))
        or any(int(row["created_worker_two"]) for row in groups[key])
        for key in target_keys
    )
    control_contract_failures = sum(
        not any(int(row["created_worker_two"]) for row in groups[key]) for key in control_keys
    )
    return (
        {
            "tasks": len(groups),
            "rows": len(rows),
            "complete_grid": set(groups) == expected,
            "decision_index_failures": index_failures,
            "state_turn_chain_failures": chain_failures,
            "trace_hash_failures": trace_hash_failures,
            "mechanical_failure_total": mechanical_failures,
            "target_contract_failures": target_contract_failures,
            "control_contract_failures": control_contract_failures,
        },
        groups,
    )


def build_report(matrix_a: Path, matrix_b: Path, rows: list[dict[str, str]]) -> dict:
    integrity, groups = validate(rows)
    integrity["repeat_byte_identical"] = matrix_a.read_bytes() == matrix_b.read_bytes()
    traces = {
        f"{seed}:{seat}:{opponent}": summarize_trace(task_rows)
        for (seed, seat, opponent), task_rows in sorted(groups.items())
    }
    target_classes = Counter(
        traces[f"{seed}:{seat}:resident"]["classification"]
        for seed in SEEDS
        for seat in (0, 1)
    )
    uniform = len(target_classes) == 1
    classification = next(iter(target_classes)) if uniform else "mixed"
    next_experiment = {
        "ripe_acquisition": "protect_ripe_missing_train_currency_until_deposit",
        "deposit_materialization": "bill_preserving_bank_deposit_lease",
        "source_availability": "missing_resource_source_access_repair",
        "transaction_or_shack": "train_execution_or_evacuation_repair",
        "mixed": "broader_worker_two_state_machine_repair",
        "unexplained": "broader_worker_two_state_machine_repair",
    }[classification]
    passed_integrity = (
        integrity["repeat_byte_identical"]
        and integrity["complete_grid"]
        and all(
            integrity[field] == 0
            for field in (
                "decision_index_failures",
                "state_turn_chain_failures",
                "trace_hash_failures",
                "mechanical_failure_total",
                "target_contract_failures",
                "control_contract_failures",
            )
        )
    )
    return {
        "schema": "troll-farm-d64i-worker-two-tail-audit-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consumed-task D40 safety diagnosis only; no value or candidate claim",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "runner": sha256_file(RUNNER),
            "matrix_a": sha256_file(matrix_a),
            "matrix_b": sha256_file(matrix_b),
            "analyzer": sha256_file(Path(__file__)),
        },
        "integrity": integrity,
        "traces": traces,
        "target_classification": {
            "counts": dict(sorted(target_classes.items())),
            "uniform": uniform,
            "classification": classification,
        },
        "decision": {
            "status": "diagnosed" if passed_integrity else "invalid",
            "next_experiment": next_experiment if passed_integrity else "repair_audit_integrity",
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def analyze(matrix_a: Path, matrix_b: Path, output: Path) -> dict:
    if matrix_a.read_bytes() != matrix_b.read_bytes():
        raise ValueError("D64i repeats differ")
    with matrix_a.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    report = build_report(matrix_a, matrix_b, rows)
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
    print(
        json.dumps(
            {
                "status": report["decision"]["status"],
                "classification": report["target_classification"],
                "next": report["decision"]["next_experiment"],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

