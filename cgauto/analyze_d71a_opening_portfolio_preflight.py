#!/usr/bin/env python3
"""Analyze D71's mechanics-only closed-loop opening portfolio panels."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d71a-closed-loop-opening-portfolio-environment-protocol-2026-07-21.md"
RUNNER = REPO / "rust/src/bin/d71_opening_portfolio_preflight.rs"
MACRO = REPO / "rust/src/rl_macro.rs"
BATCH = REPO / "rust/src/rl_batch_option.rs"
ENVIRONMENT = REPO / "rust/src/rl_opening_portfolio.rs"
REFERENCE = ANALYSIS / "d62a-balanced-reference-matrix-9801000.tsv"
PROBES = ("balanced", "seed_plum", "seed_lemon", "seed_apple", "seed_banana", "cyclic")
SPECIES = ("plum", "lemon", "apple", "banana")
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
ACTION_FIELDS = (
    "action_balanced",
    "action_harvest",
    "action_renew",
    "action_fell",
    "action_seed_plum",
    "action_seed_lemon",
    "action_seed_apple",
    "action_seed_banana",
)
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "finite_feature_failures",
    "legal_mask_failures",
    "source_assignment_failures",
    "boundary_failures",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def parse_elapsed(value: str) -> float:
    fields = value.strip().split(":")
    if len(fields) == 2:
        return int(fields[0]) * 60 + float(fields[1])
    if len(fields) == 3:
        return int(fields[0]) * 3600 + int(fields[1]) * 60 + float(fields[2])
    return float(value)


def parse_timing(path: Path) -> dict:
    text = path.read_text()

    def field(label: str) -> str:
        match = re.search(rf"^\s*{re.escape(label)}:\s*(.+?)\s*$", text, re.MULTILINE)
        if not match:
            raise ValueError(f"timing sidecar lacks {label!r}: {path}")
        return match.group(1)

    user = float(field("User time (seconds)"))
    system = float(field("System time (seconds)"))
    elapsed = parse_elapsed(field("Elapsed (wall clock) time (h:mm:ss or m:ss)"))
    percent = float(field("Percent of CPU this job got").rstrip("%"))
    return {
        "user_seconds": user,
        "system_seconds": system,
        "elapsed_seconds": elapsed,
        "reported_cpu_percent": percent,
        "effective_cpu_cores": (user + system) / elapsed,
        "maximum_resident_kib": int(field("Maximum resident set size (kbytes)")),
    }


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def validate_anchor(anchor: list[dict[str, str]], reference: list[dict[str, str]]) -> dict:
    expected = [
        row for row in reference if row["policy"] == "d62_zero_linear_balanced_reference"
    ]
    expected_by_key = {task_key(row): row for row in expected}
    actual_by_key = {task_key(row): row for row in anchor}
    fields = (
        "turn",
        "own_score",
        "opponent_score",
        "own_workers",
        "opponent_workers",
        "successful_trains",
        "own_created_crops",
        "opponent_created_crops",
        "ambiguous_created_crops",
        "action_hash",
        "state_hash",
    )
    differences = []
    for key in sorted(set(expected_by_key) | set(actual_by_key)):
        expected_row = expected_by_key.get(key)
        actual_row = actual_by_key.get(key)
        if expected_row is None or actual_row is None:
            differences.append({"task": list(key), "field": "row", "expected": bool(expected_row), "actual": bool(actual_row)})
            continue
        for field in fields:
            if expected_row[field] != actual_row[field]:
                differences.append(
                    {
                        "task": list(key),
                        "field": field,
                        "expected": expected_row[field],
                        "actual": actual_row[field],
                    }
                )
    return {
        "reference_rows": len(expected),
        "actual_rows": len(anchor),
        "task_identity_exact": set(actual_by_key) == set(expected_by_key),
        "field_differences": differences,
        "pass": len(expected) == 16 and len(anchor) == 16 and not differences,
    }


def validate_grid(rows: list[dict[str, str]]) -> dict:
    expected = {
        (probe, seed, seat, opponent)
        for probe in PROBES
        for seed in range(9_803_000, 9_803_032)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    actual = {
        (row["probe"], int(row["map_seed"]), int(row["seat"]), row["opponent"])
        for row in rows
    }
    failures = {field: sum(int(row[field]) for row in rows) for field in FAILURE_FIELDS}
    option_count_failures = sum(
        int(row["boundary_decisions"])
        != sum(int(row[field]) for field in ACTION_FIELDS)
        for row in rows
    )
    source_count_failures = 0
    for row in rows:
        for species in SPECIES:
            source_count_failures += int(
                int(row[f"attempt_{species}"]) != int(row[f"action_seed_{species}"])
                or int(row[f"created_{species}"]) > int(row[f"attempt_{species}"])
            )
    return {
        "rows": len(rows),
        "complete_grid": actual == expected and len(rows) == len(expected),
        "duplicate_rows": len(rows) - len(actual),
        "failure_totals": failures,
        "option_count_failures": option_count_failures,
        "source_count_failures": source_count_failures,
        "maximum_reward_identity_error": max(
            (float(row["reward_identity_error"]) for row in rows), default=0.0
        ),
        "maximum_boundary_decisions": max(
            (int(row["boundary_decisions"]) for row in rows), default=0
        ),
        "environmental_invalidated_jobs": sum(
            int(row["invalidated_jobs"]) for row in rows
        ),
    }


def probe_summary(rows: list[dict[str, str]]) -> dict:
    result = {}
    for probe in PROBES:
        selected = [row for row in rows if row["probe"] == probe]
        result[probe] = {
            "tasks": len(selected),
            "crop_creating_tasks": sum(int(row["own_created_crops"]) > 0 for row in selected),
            "crop_creation_rate": (
                sum(int(row["own_created_crops"]) > 0 for row in selected) / len(selected)
                if selected
                else None
            ),
            "two_source_attempt_tasks": sum(
                sum(int(row[f"attempt_{species}"]) for species in SPECIES) >= 2
                for row in selected
            ),
            "ended_generation_tasks": sum(
                int(row["ended_own_generations"]) > 0 for row in selected
            ),
            "source_retry_after_death_tasks": sum(
                int(row["source_attempts_after_death"]) > 0 for row in selected
            ),
            "action_counts": {
                field.removeprefix("action_"): sum(int(row[field]) for row in selected)
                for field in ACTION_FIELDS
            },
            "source_attempts": {
                species: sum(int(row[f"attempt_{species}"]) for row in selected)
                for species in SPECIES
            },
            "source_creations": {
                species: sum(int(row[f"created_{species}"]) for row in selected)
                for species in SPECIES
            },
            "renewable_receipt_units": sum(
                int(row["renewable_receipts"]) for row in selected
            ),
            "reinvested_generations": sum(
                int(row["reinvested_generations"]) for row in selected
            ),
        }
    return result


def build_report(
    anchor_path: Path,
    grid_a_path: Path,
    grid_b_path: Path,
    time_a_path: Path,
    time_b_path: Path,
) -> dict:
    anchor = read_tsv(anchor_path)
    reference = read_tsv(REFERENCE)
    rows = read_tsv(grid_a_path)
    anchor_integrity = validate_anchor(anchor, reference)
    grid_integrity = validate_grid(rows)
    repeat_exact = grid_a_path.read_bytes() == grid_b_path.read_bytes()
    timings = [parse_timing(time_a_path), parse_timing(time_b_path)]
    transitions = sum(int(row["boundary_decisions"]) for row in rows)
    for timing in timings:
        timing["boundary_transitions"] = transitions
        timing["boundary_transitions_per_second"] = transitions / timing["elapsed_seconds"]
    probes = probe_summary(rows)
    source_assignments = {
        species: sum(int(row[f"attempt_{species}"]) for row in rows)
        for species in SPECIES
    }
    source_creations = {
        species: sum(int(row[f"created_{species}"]) for row in rows)
        for species in SPECIES
    }
    action_counts = {
        field.removeprefix("action_"): sum(int(row[field]) for row in rows)
        for field in ACTION_FIELDS
    }
    pre_crop = sum(int(row["pre_crop_boundaries"]) for row in rows)
    pre_crop_two = sum(int(row["pre_crop_two_seed_legal"]) for row in rows)
    cyclic = probes["cyclic"]

    checks = {
        "exact_anchor_parity": anchor_integrity["pass"],
        "complete_repeat_byte_identical_grid": (
            grid_integrity["complete_grid"] and repeat_exact
        ),
        "zero_mechanical_failures": (
            all(value == 0 for value in grid_integrity["failure_totals"].values())
            and grid_integrity["option_count_failures"] == 0
            and grid_integrity["source_count_failures"] == 0
            and grid_integrity["maximum_reward_identity_error"] < 1e-4
        ),
        "each_species_assigned_and_created_at_least_100": all(
            source_assignments[species] >= 100 and source_creations[species] >= 100
            for species in SPECIES
        ),
        "species_probe_crop_rate_at_least_0_99_and_cyclic_1_00": (
            all(probes[f"seed_{species}"]["crop_creation_rate"] >= 0.99 for species in SPECIES)
            and probes["cyclic"]["crop_creation_rate"] == 1.0
        ),
        "cyclic_recurrence_and_death_retry": (
            cyclic["two_source_attempt_tasks"] >= 256
            and cyclic["ended_generation_tasks"] >= 32
            and cyclic["source_retry_after_death_tasks"] >= 16
        ),
        "mask_and_pre_crop_source_coverage": (
            pre_crop > 0
            and pre_crop_two / pre_crop >= 0.50
            and grid_integrity["failure_totals"]["legal_mask_failures"] == 0
        ),
        "all_actions_and_boundary_limit": (
            all(value > 0 for value in action_counts.values())
            and grid_integrity["maximum_boundary_decisions"] <= 5_000
        ),
        "throughput_and_cpu": (
            min(row["boundary_transitions_per_second"] for row in timings) >= 400
            and min(row["effective_cpu_cores"] for row in timings) >= 12
        ),
    }
    passed = all(checks.values())
    return {
        "schema": "troll-farm-d71a-opening-portfolio-preflight-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": (
            "mechanics-only closed-loop opening portfolio representation; scores used only "
            "for exact anchor equality and never aggregated by probe"
        ),
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "runner": sha256_file(RUNNER),
            "macro_environment": sha256_file(MACRO),
            "batch_environment": sha256_file(BATCH),
            "opening_environment": sha256_file(ENVIRONMENT),
            "d62_reference": sha256_file(REFERENCE),
            "anchor": sha256_file(anchor_path),
            "grid_a": sha256_file(grid_a_path),
            "grid_b": sha256_file(grid_b_path),
            "time_a": sha256_file(time_a_path),
            "time_b": sha256_file(time_b_path),
            "analyzer": sha256_file(Path(__file__)),
        },
        "integrity": {
            "anchor": anchor_integrity,
            "grid": grid_integrity,
            "repeat_byte_identical": repeat_exact,
            "timings": timings,
            "pass": passed,
        },
        "representation": {
            "boundary_transitions": transitions,
            "action_counts": action_counts,
            "source_assignments": source_assignments,
            "source_creations": source_creations,
            "pre_crop_boundaries": pre_crop,
            "pre_crop_two_seed_legal": pre_crop_two,
            "pre_crop_two_seed_legal_rate": pre_crop_two / pre_crop if pre_crop else None,
            "probes": probes,
        },
        "gates": checks,
        "decision": {
            "status": "pass" if passed else "fail",
            "next_experiment": (
                "recurrent_random_policy_upper_bound_population"
                if passed
                else "repair_or_close_opening_portfolio_environment"
            ),
            "analyze_probe_value": False,
            "train_ppo": False,
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anchor", type=Path, required=True)
    parser.add_argument("--grid-a", type=Path, required=True)
    parser.add_argument("--grid-b", type=Path, required=True)
    parser.add_argument("--time-a", type=Path, required=True)
    parser.add_argument("--time-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(
        args.anchor, args.grid_a, args.grid_b, args.time_a, args.time_b
    )
    atomic_write_new(args.output, report)
    print(
        json.dumps(
            {
                "integrity": report["integrity"],
                "gates": report["gates"],
                "decision": report["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
