#!/usr/bin/env python3
"""Analyze frozen capacity-separated reproductive-denial panels."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import os
from pathlib import Path
import tempfile

try:
    from cgauto.prefruit_reproductive_interruption import (
        INTEGER_FIELDS as BASE_INTEGER_FIELDS,
        activation_diagnostic,
        compare,
        identity,
        inactive_identity,
        summarize as base_summarize,
    )
except ModuleNotFoundError:  # Direct `python3 cgauto/<script>.py` execution.
    from prefruit_reproductive_interruption import (  # type: ignore[no-redef]
        INTEGER_FIELDS as BASE_INTEGER_FIELDS,
        activation_diagnostic,
        compare,
        identity,
        inactive_identity,
        summarize as base_summarize,
    )


PROFILES = {"resident", "adaptive_density", "capacity_separated_denial"}
OPPONENTS = {
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
}
INTEGER_FIELDS = BASE_INTEGER_FIELDS + (
    "capacity_ready_turns",
    "capacity_separation_violations",
)


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def summarize(rows: list[dict]) -> dict:
    report = base_summarize(rows)
    report["capacity_ready_turns"] = sum(
        row["capacity_ready_turns"] for row in rows
    )
    report["capacity_separation_violations"] = sum(
        row["capacity_separation_violations"] for row in rows
    )
    report["activated_without_capacity_cells"] = sum(
        row["activation_turns"] > 0 and row["capacity_ready_turns"] == 0
        for row in rows
    )
    by_opponent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_opponent[row["opponent"]].append(row)
    for opponent, group in by_opponent.items():
        report["opponents"][opponent].update(
            {
                "capacity_ready_cells": sum(
                    row["capacity_ready_turns"] > 0 for row in group
                ),
                "capacity_ready_turns": sum(
                    row["capacity_ready_turns"] for row in group
                ),
                "capacity_separation_violations": sum(
                    row["capacity_separation_violations"] for row in group
                ),
            }
        )
    return report


def analyze(
    rows: list[dict], phase: str, repeat_exact: bool | None = None
) -> dict:
    unique = [(identity(row), row["profile"]) for row in rows]
    if len(unique) != len(set(unique)):
        raise ValueError("duplicate scenario-profile rows")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["profile"]].append(row)
    if set(grouped) != PROFILES:
        raise ValueError(f"expected profiles {sorted(PROFILES)}")
    expected_range = {
        "integrity": range(0, 30),
        "discovery": range(2020, 2080),
        "confirmation": range(2080, 2140),
    }[phase]
    expected = {
        (seed, seat, opponent)
        for seed in expected_range
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    grids = [{identity(row) for row in group} for group in grouped.values()]
    if any(grid != expected for grid in grids):
        raise ValueError("input is not the frozen complete grid")

    candidate = grouped["capacity_separated_denial"]
    base = grouped["adaptive_density"]
    resident = grouped["resident"]
    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    inactive = inactive_identity(candidate, base)
    integrity = {
        "complete_grid": len(rows) == len(expected) * 3,
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "provenance_assignment": all(
            report["provenance_assignment_rate"] is not None
            and report["provenance_assignment_rate"] >= 0.95
            for report in reports.values()
        ),
        "same_build_base_shadow_parity": (
            reports["capacity_separated_denial"]["base_command_mismatches"] == 0
        ),
        "zero_capacity_separation_violations": (
            reports["capacity_separated_denial"][
                "capacity_separation_violations"
            ]
            == 0
        ),
        "every_activation_has_separate_capacity": (
            reports["capacity_separated_denial"][
                "activated_without_capacity_cells"
            ]
            == 0
        ),
        "inactive_cells_exactly_equal_base": inactive["passed"],
    }
    candidate_resident = compare(candidate, resident)
    candidate_base = compare(candidate, base)
    payload = {
        "schema": 1,
        "phase": phase,
        "profiles": reports,
        "capacity_separated_minus_resident": candidate_resident,
        "capacity_separated_minus_adaptive_base": candidate_base,
        "inactive_identity": inactive,
        "integrity_checks": integrity,
    }
    if phase == "integrity":
        integrity["repeat_run_identity"] = repeat_exact is True
        passed = all(integrity.values())
        return {
            **payload,
            "passed": passed,
            "decision": "open frozen discovery" if passed else "repair implementation",
        }

    opponent_deltas = {
        opponent: compare(
            [row for row in candidate if row["opponent"] == opponent],
            [row for row in resident if row["opponent"] == opponent],
        )["mean_margin_delta"]
        for opponent in sorted(OPPONENTS)
    }
    adaptive_candidate = [
        row for row in candidate if row["opponent"] == "gold_adaptive"
    ]
    adaptive_base = [row for row in base if row["opponent"] == "gold_adaptive"]
    adaptive_resident = [
        row for row in resident if row["opponent"] == "gold_adaptive"
    ]
    adaptive_vs_base = compare(adaptive_candidate, adaptive_base)
    adaptive_vs_resident = compare(adaptive_candidate, adaptive_resident)
    nonnegative = sum(delta >= 0 for delta in opponent_deltas.values())
    worst = min(opponent_deltas.values())
    candidate_report = reports["capacity_separated_denial"]
    checks = {
        "integrity": all(integrity.values()),
        "mean_margin": candidate_resident["mean_margin_delta"] >= 10,
        "trimmed_margin": candidate_resident[
            "trimmed_5pct_mean_margin_delta"
        ]
        >= (10 if phase == "confirmation" else 5),
        "own_score": candidate_resident["mean_own_score_delta"] >= 50,
        "own_wood": candidate_resident["mean_own_inventory_wood_delta"] >= 10,
        "opponent_breadth": nonnegative >= 6,
        "worst_opponent": worst >= -5,
        "adaptive_gold_margin": adaptive_vs_resident["mean_margin_delta"] >= 0,
        "activation_overall": candidate_report["activated_cells"] >= 100,
        "activation_adaptive_gold": candidate_report["opponents"]["gold_adaptive"][
            "activated_cells"
        ]
        >= 30,
        "targets_disappeared_before_fruit": candidate_report[
            "targets_disappeared_before_fruit"
        ]
        >= 30,
        "capacity_ready_for_every_activation": candidate_report[
            "activated_without_capacity_cells"
        ]
        == 0,
        "adaptive_opponent_score_suppression": adaptive_vs_base[
            "mean_opponent_score_delta"
        ]
        <= -50,
        "adaptive_opponent_plant_suppression": adaptive_vs_base[
            "mean_opponent_successful_plants_delta"
        ]
        <= -10,
        "adaptive_opponent_self_crop_wood_suppression": adaptive_vs_base[
            "mean_opponent_from_opponent_delta"
        ]
        <= -20,
        "adaptive_own_score_preservation": adaptive_vs_base["mean_own_score_delta"]
        >= -30,
    }
    passed = all(checks.values())
    return {
        **payload,
        "opponent_mean_margin_deltas": opponent_deltas,
        "nonnegative_opponents": nonnegative,
        "worst_opponent_mean_margin_delta": worst,
        "adaptive_gold": {
            "capacity_separated_minus_resident": adaptive_vs_resident,
            "capacity_separated_minus_adaptive_base": adaptive_vs_base,
        },
        "activation_diagnostic": activation_diagnostic(candidate, base, resident),
        "gate_checks": checks,
        "passed": passed,
        "decision": (
            "open unchanged confirmation"
            if phase == "discovery" and passed
            else "qualify for packaging and field-prefix audit"
            if phase == "confirmation" and passed
            else "close capacity-separated reproductive denial without tuning"
        ),
    }


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name, dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--phase", choices=("integrity", "discovery", "confirmation"), required=True
    )
    parser.add_argument("--repeat", type=Path)
    args = parser.parse_args()
    repeat_exact = (
        args.repeat.read_bytes() == args.input.read_bytes() if args.repeat else None
    )
    payload = analyze(read_rows(args.input), args.phase, repeat_exact)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
