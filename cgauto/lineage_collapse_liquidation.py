#!/usr/bin/env python3
"""Analyze frozen lineage-collapse liquidation panels."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import os
from pathlib import Path
import statistics
import tempfile

try:
    from cgauto.prefruit_reproductive_interruption import (
        INTEGER_FIELDS as BASE_INTEGER_FIELDS,
        compare,
        identity,
        summarize as base_summarize,
        trimmed_mean,
    )
except ModuleNotFoundError:  # Direct `python3 cgauto/<script>.py` execution.
    from prefruit_reproductive_interruption import (  # type: ignore[no-redef]
        INTEGER_FIELDS as BASE_INTEGER_FIELDS,
        compare,
        identity,
        summarize as base_summarize,
        trimmed_mean,
    )


PROFILES = {"resident", "adaptive_density", "lineage_collapse_liquidation"}
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
EXTRA_INTEGER_FIELDS = (
    "capacity_ready_turns",
    "capacity_separation_violations",
    "entry_state_violations",
    "forbidden_post_entry_commands",
    "post_entry_commands",
    "lineage_recovery_turns",
    "entry_banked_banana",
    "entry_carried_banana",
    "entry_crop_banana_fruits",
    "entry_opponent_banana_crops",
    "entry_own_score",
    "entry_opponent_score",
    "entry_margin",
    "terminal_plants",
    "terminal_banana_plants",
)
INTEGER_FIELDS = BASE_INTEGER_FIELDS + EXTRA_INTEGER_FIELDS
EXACT_OUTCOME_FIELDS = (
    "own_score",
    "opponent_score",
    "margin",
    "own_inventory_wood",
    "opponent_inventory_wood",
    "workers",
    "terminal_turn",
    "terminal_plants",
    "terminal_banana_plants",
    "own_successful_plants",
    "opponent_successful_plants",
    "ambiguous_births",
    "total_chop_wood",
    "assigned_chop_wood",
    "own_from_natural",
    "own_from_ours",
    "own_from_opponent",
    "own_from_unknown",
    "opponent_from_natural",
    "opponent_from_ours",
    "opponent_from_opponent",
    "opponent_from_unknown",
)


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def inactive_identity(candidate: list[dict], resident: list[dict]) -> dict:
    candidate_map = {identity(row): row for row in candidate}
    resident_map = {identity(row): row for row in resident}
    if candidate_map.keys() != resident_map.keys():
        raise ValueError("inactive comparison profiles have different grids")
    inactive = [
        key for key, row in candidate_map.items() if row["activation_turns"] == 0
    ]
    mismatches = []
    for key in sorted(inactive):
        fields = {
            field: [candidate_map[key][field], resident_map[key][field]]
            for field in EXACT_OUTCOME_FIELDS
            if candidate_map[key][field] != resident_map[key][field]
        }
        if fields:
            mismatches.append({"identity": key, "fields": fields})
    return {
        "inactive_cells": len(inactive),
        "mismatches": mismatches,
        "passed": not mismatches,
    }


def summarize(rows: list[dict]) -> dict:
    report = base_summarize(rows)
    active = [row for row in rows if row["activation_turns"] > 0]
    report.update(
        {
            "entry_state_violations": sum(
                row["entry_state_violations"] for row in rows
            ),
            "forbidden_post_entry_commands": sum(
                row["forbidden_post_entry_commands"] for row in rows
            ),
            "post_entry_commands": sum(row["post_entry_commands"] for row in rows),
            "lineage_recovery_turns": sum(
                row["lineage_recovery_turns"] for row in rows
            ),
            "recovery_cells": sum(
                row["lineage_recovery_turns"] > 0 for row in rows
            ),
            "mean_terminal_plants": statistics.mean(
                row["terminal_plants"] for row in rows
            ),
            "mean_terminal_banana_plants": statistics.mean(
                row["terminal_banana_plants"] for row in rows
            ),
            "mean_entry_margin_when_active": (
                statistics.mean(row["entry_margin"] for row in active)
                if active
                else None
            ),
            "median_entry_turn_when_active": (
                statistics.median(row["first_activation_turn"] for row in active)
                if active
                else None
            ),
        }
    )
    for opponent, group in defaultdict(list, {
        name: [row for row in rows if row["opponent"] == name]
        for name in {row["opponent"] for row in rows}
    }).items():
        active_group = [row for row in group if row["activation_turns"] > 0]
        report["opponents"][opponent].update(
            {
                "lineage_recovery_turns": sum(
                    row["lineage_recovery_turns"] for row in group
                ),
                "recovery_cells": sum(
                    row["lineage_recovery_turns"] > 0 for row in group
                ),
                "mean_entry_margin_when_active": (
                    statistics.mean(row["entry_margin"] for row in active_group)
                    if active_group
                    else None
                ),
            }
        )
    return report


def integrity_checks(
    rows: list[dict], reports: dict, candidate: list[dict], resident: list[dict]
) -> tuple[dict, dict]:
    inactive = inactive_identity(candidate, resident)
    active = [row for row in candidate if row["activation_turns"] > 0]
    checks = {
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "provenance_assignment": all(
            report["provenance_assignment_rate"] is not None
            and report["provenance_assignment_rate"] >= 0.95
            for report in reports.values()
        ),
        "resident_shadow_parity": (
            reports["lineage_collapse_liquidation"]["base_command_mismatches"] == 0
        ),
        "entry_state_exact": all(
            row["first_activation_turn"] > 100
            and row["opponent_crops_seen"] > 0
            and row["entry_banked_banana"] == 0
            and row["entry_carried_banana"] == 0
            and row["entry_crop_banana_fruits"] == 0
            and row["entry_opponent_banana_crops"] == 0
            and row["entry_state_violations"] == 0
            for row in active
        ),
        "persistent_after_entry": all(
            row["activation_turns"]
            == row["terminal_turn"] - row["first_activation_turn"]
            for row in active
        ),
        "no_forbidden_post_entry_commands": all(
            row["forbidden_post_entry_commands"] == 0
            and row["copied_mine"] == 0
            and row["copied_pick"] == 0
            and row["copied_harvest"] == 0
            and row["copied_plant"] == 0
            for row in candidate
        ),
        "post_entry_command_accounting": all(
            row["post_entry_commands"]
            == row["copied_move"] + row["copied_chop"] + row["copied_drop"]
            for row in candidate
        ),
        "inactive_cells_exactly_equal_resident": inactive["passed"],
    }
    return checks, inactive


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
        "discovery": range(2140, 2200),
        "confirmation": range(2200, 2260),
    }[phase]
    expected_opponents = {"gold_adaptive"} if phase == "integrity" else OPPONENTS
    expected = {
        (seed, seat, opponent)
        for seed in expected_range
        for seat in (0, 1)
        for opponent in expected_opponents
    }
    grids = [{identity(row) for row in group} for group in grouped.values()]
    if any(grid != expected for grid in grids):
        raise ValueError("input is not the frozen complete grid")

    candidate = grouped["lineage_collapse_liquidation"]
    resident = grouped["resident"]
    adaptive = grouped["adaptive_density"]
    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    integrity, inactive = integrity_checks(rows, reports, candidate, resident)
    integrity["complete_grid"] = len(rows) == len(expected) * 3
    candidate_resident = compare(candidate, resident)
    candidate_adaptive = compare(candidate, adaptive)
    margin_deltas = [
        left["margin"] - right["margin"]
        for left, right in zip(
            sorted(candidate, key=identity), sorted(resident, key=identity), strict=True
        )
    ]
    payload = {
        "schema": 1,
        "phase": phase,
        "profiles": reports,
        "lineage_collapse_minus_resident": candidate_resident,
        "lineage_collapse_minus_adaptive_context": candidate_adaptive,
        "trimmed_10pct_mean_margin_delta": trimmed_mean(margin_deltas, 0.10),
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
    adaptive_resident = [
        row for row in resident if row["opponent"] == "gold_adaptive"
    ]
    adaptive_delta = compare(adaptive_candidate, adaptive_resident)
    positive = sum(delta > 0 for delta in opponent_deltas.values())
    worst = min(opponent_deltas.values())
    confirmation = phase == "confirmation"
    checks = {
        "integrity": all(integrity.values()),
        "mean_margin": candidate_resident["mean_margin_delta"]
        >= (2.0 if confirmation else 3.0),
        "trimmed_10pct_margin": payload["trimmed_10pct_mean_margin_delta"] >= 0,
        "opponent_breadth": positive >= 5,
        "worst_opponent": worst >= -12.0,
        "adaptive_gold_margin": adaptive_delta["mean_margin_delta"]
        >= (3.0 if confirmation else 5.0),
        "adaptive_opponent_score_suppression": adaptive_delta[
            "mean_opponent_score_delta"
        ]
        <= -5.0,
        "adaptive_own_score_preservation": adaptive_delta["mean_own_score_delta"]
        >= -10.0,
        "adaptive_activation_breadth": reports["lineage_collapse_liquidation"][
            "opponents"
        ]["gold_adaptive"]["activated_cells"]
        >= (25 if confirmation else 30),
    }
    passed = all(checks.values())
    return {
        **payload,
        "opponent_mean_margin_deltas": opponent_deltas,
        "positive_opponents": positive,
        "worst_opponent_mean_margin_delta": worst,
        "adaptive_gold": {
            "lineage_collapse_minus_resident": adaptive_delta,
            "activated_cells": reports["lineage_collapse_liquidation"][
                "opponents"
            ]["gold_adaptive"]["activated_cells"],
        },
        "gate_checks": checks,
        "passed": passed,
        "decision": (
            "open unchanged confirmation"
            if phase == "discovery" and passed
            else "qualify for source integration and arena-transfer audit"
            if phase == "confirmation" and passed
            else "close lineage-collapse liquidation without tuning"
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
