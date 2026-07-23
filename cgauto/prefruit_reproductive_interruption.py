#!/usr/bin/env python3
"""Analyze frozen pre-fruit reproductive-interruption panels."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import math
import os
from pathlib import Path
import statistics
import tempfile


PROFILES = {"resident", "lean_m2c2h0k2", "prefruit_interruption"}
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
INTEGER_FIELDS = (
    "seed",
    "seat",
    "own_score",
    "opponent_score",
    "margin",
    "own_inventory_wood",
    "opponent_inventory_wood",
    "workers",
    "terminal_turn",
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
    "opponent_crops_seen",
    "active_opponent_crops",
    "activation_turns",
    "first_activation_turn",
    "base_command_mismatches",
    "selected_targets",
    "targets_disappeared_before_fruit",
    "targets_fruited_after_selection",
    "copied_move",
    "copied_chop",
    "copied_drop",
    "copied_mine",
    "copied_pick",
    "copied_harvest",
    "copied_plant",
)
COMPARISON_FIELDS = (
    "margin",
    "own_score",
    "opponent_score",
    "own_inventory_wood",
    "opponent_inventory_wood",
    "own_successful_plants",
    "opponent_successful_plants",
    "own_from_opponent",
    "opponent_from_opponent",
)
OUTCOME_IDENTITY_FIELDS = (
    "own_score",
    "opponent_score",
    "margin",
    "own_inventory_wood",
    "opponent_inventory_wood",
    "workers",
    "terminal_turn",
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


def identity(row: dict) -> tuple[int, int, str]:
    return row["seed"], row["seat"], row["opponent"]


def trimmed_mean(values: list[int], fraction: float = 0.05) -> float:
    ordered = sorted(values)
    trim = math.floor(len(ordered) * fraction)
    kept = ordered[trim : len(ordered) - trim] if trim else ordered
    return statistics.mean(kept)


def compare(left: list[dict], right: list[dict]) -> dict:
    left_map = {identity(row): row for row in left}
    right_map = {identity(row): row for row in right}
    if left_map.keys() != right_map.keys():
        raise ValueError("comparison profiles have different grids")
    deltas = {
        field: [left_map[key][field] - right_map[key][field] for key in sorted(left_map)]
        for field in COMPARISON_FIELDS
    }
    margin = deltas["margin"]
    return {
        "scenarios": len(margin),
        "mean_margin_delta": statistics.mean(margin),
        "trimmed_5pct_mean_margin_delta": trimmed_mean(margin),
        "median_margin_delta": statistics.median(margin),
        "minimum_margin_delta": min(margin),
        "maximum_margin_delta": max(margin),
        **{
            f"mean_{field}_delta": statistics.mean(values)
            for field, values in deltas.items()
            if field != "margin"
        },
    }


def summarize(rows: list[dict]) -> dict:
    by_opponent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_opponent[row["opponent"]].append(row)
    total_chop = sum(row["total_chop_wood"] for row in rows)
    assigned_chop = sum(row["assigned_chop_wood"] for row in rows)

    def group_summary(group: list[dict]) -> dict:
        active = [row for row in group if row["activation_turns"] > 0]
        return {
            "scenarios": len(group),
            "mean_score": statistics.mean(row["own_score"] for row in group),
            "mean_opponent_score": statistics.mean(
                row["opponent_score"] for row in group
            ),
            "mean_margin": statistics.mean(row["margin"] for row in group),
            "activated_cells": len(active),
            "mean_activation_turns": statistics.mean(
                row["activation_turns"] for row in group
            ),
            "median_first_activation_turn_when_active": (
                statistics.median(row["first_activation_turn"] for row in active)
                if active
                else None
            ),
            "selected_targets": sum(row["selected_targets"] for row in group),
            "targets_disappeared_before_fruit": sum(
                row["targets_disappeared_before_fruit"] for row in group
            ),
            "targets_fruited_after_selection": sum(
                row["targets_fruited_after_selection"] for row in group
            ),
        }

    report = group_summary(rows)
    report.update(
        {
            "mean_inventory_wood": statistics.mean(
                row["own_inventory_wood"] for row in rows
            ),
            "mean_opponent_inventory_wood": statistics.mean(
                row["opponent_inventory_wood"] for row in rows
            ),
            "mean_workers": statistics.mean(row["workers"] for row in rows),
            "mean_opponent_crops_seen": statistics.mean(
                row["opponent_crops_seen"] for row in rows
            ),
            "provenance_assignment_rate": (
                assigned_chop / total_chop if total_chop else None
            ),
            "ambiguous_births": sum(row["ambiguous_births"] for row in rows),
            "base_command_mismatches": sum(
                row["base_command_mismatches"] for row in rows
            ),
            "wood": {
                field: sum(row[field] for row in rows)
                for field in (
                    "own_from_natural",
                    "own_from_ours",
                    "own_from_opponent",
                    "own_from_unknown",
                    "opponent_from_natural",
                    "opponent_from_ours",
                    "opponent_from_opponent",
                    "opponent_from_unknown",
                )
            },
            "opponents": {
                opponent: group_summary(group)
                for opponent, group in sorted(by_opponent.items())
            },
        }
    )
    return report


def inactive_identity(candidate: list[dict], farm: list[dict]) -> dict:
    candidate_map = {identity(row): row for row in candidate}
    farm_map = {identity(row): row for row in farm}
    if candidate_map.keys() != farm_map.keys():
        raise ValueError("inactive comparison profiles have different grids")
    inactive = [
        key for key, row in candidate_map.items() if row["activation_turns"] == 0
    ]
    mismatches = [
        {
            "identity": key,
            "fields": {
                field: [candidate_map[key][field], farm_map[key][field]]
                for field in OUTCOME_IDENTITY_FIELDS
                if candidate_map[key][field] != farm_map[key][field]
            },
        }
        for key in sorted(inactive)
        if any(
            candidate_map[key][field] != farm_map[key][field]
            for field in OUTCOME_IDENTITY_FIELDS
        )
    ]
    return {
        "inactive_cells": len(inactive),
        "mismatches": mismatches,
        "passed": not mismatches,
    }


def activation_diagnostic(
    candidate: list[dict], farm: list[dict], resident: list[dict]
) -> dict:
    candidate_map = {identity(row): row for row in candidate}
    farm_map = {identity(row): row for row in farm}
    resident_map = {identity(row): row for row in resident}
    if (
        candidate_map.keys() != farm_map.keys()
        or candidate_map.keys() != resident_map.keys()
    ):
        raise ValueError("activation diagnostic profiles have different grids")

    def one(keys: list[tuple[int, int, str]]) -> dict:
        active = [key for key in keys if candidate_map[key]["activation_turns"] > 0]
        candidate_gain = statistics.mean(
            candidate_map[key]["margin"] - farm_map[key]["margin"] for key in keys
        )
        resident_need = statistics.mean(
            resident_map[key]["margin"] - farm_map[key]["margin"] for key in keys
        )
        return {
            "cells": len(keys),
            "activated_cells": len(active),
            "activation_rate": len(active) / len(keys),
            "mean_margin_delta_vs_farm": candidate_gain,
            "mean_margin_delta_vs_farm_when_active": (
                statistics.mean(
                    candidate_map[key]["margin"] - farm_map[key]["margin"]
                    for key in active
                )
                if active
                else None
            ),
            "mean_opponent_score_delta_vs_farm": statistics.mean(
                candidate_map[key]["opponent_score"]
                - farm_map[key]["opponent_score"]
                for key in keys
            ),
            "mean_opponent_successful_plants_delta_vs_farm": statistics.mean(
                candidate_map[key]["opponent_successful_plants"]
                - farm_map[key]["opponent_successful_plants"]
                for key in keys
            ),
            "mean_opponent_self_crop_wood_delta_vs_farm": statistics.mean(
                candidate_map[key]["opponent_from_opponent"]
                - farm_map[key]["opponent_from_opponent"]
                for key in keys
            ),
            "resident_margin_advantage_over_farm": resident_need,
            "fraction_of_resident_advantage_recovered": (
                candidate_gain / resident_need if resident_need > 0 else None
            ),
        }

    keys = sorted(candidate_map)
    return {
        "overall": one(keys),
        "opponents": {
            opponent: one([key for key in keys if key[2] == opponent])
            for opponent in sorted(OPPONENTS)
        },
    }


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
        "discovery": range(1900, 1960),
        "confirmation": range(1960, 2020),
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

    candidate = grouped["prefruit_interruption"]
    farm = grouped["lean_m2c2h0k2"]
    resident = grouped["resident"]
    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    inactive = inactive_identity(candidate, farm)
    integrity = {
        "complete_grid": len(rows) == len(expected) * 3,
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "provenance_assignment": all(
            report["provenance_assignment_rate"] is not None
            and report["provenance_assignment_rate"] >= 0.95
            for report in reports.values()
        ),
        "same_build_farm_shadow_parity": (
            reports["prefruit_interruption"]["base_command_mismatches"] == 0
        ),
        "inactive_cells_exactly_equal_farm": inactive["passed"],
    }
    candidate_resident = compare(candidate, resident)
    candidate_farm = compare(candidate, farm)
    base = {
        "schema": 1,
        "phase": phase,
        "profiles": reports,
        "prefruit_minus_resident": candidate_resident,
        "prefruit_minus_farm": candidate_farm,
        "inactive_identity": inactive,
        "integrity_checks": integrity,
    }
    if phase == "integrity":
        integrity["repeat_run_identity"] = repeat_exact is True
        passed = all(integrity.values())
        return {
            **base,
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
    adaptive_farm = [row for row in farm if row["opponent"] == "gold_adaptive"]
    adaptive_resident = [
        row for row in resident if row["opponent"] == "gold_adaptive"
    ]
    adaptive_vs_farm = compare(adaptive_candidate, adaptive_farm)
    adaptive_vs_resident = compare(adaptive_candidate, adaptive_resident)
    nonnegative = sum(delta >= 0 for delta in opponent_deltas.values())
    worst = min(opponent_deltas.values())
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
        "activation_overall": reports["prefruit_interruption"]["activated_cells"]
        >= 200,
        "activation_adaptive_gold": reports["prefruit_interruption"]["opponents"][
            "gold_adaptive"
        ]["activated_cells"]
        >= 30,
        "targets_disappeared_before_fruit": reports["prefruit_interruption"][
            "targets_disappeared_before_fruit"
        ]
        >= 30,
        "adaptive_opponent_score_suppression": adaptive_vs_farm[
            "mean_opponent_score_delta"
        ]
        <= -50,
        "adaptive_opponent_plant_suppression": adaptive_vs_farm[
            "mean_opponent_successful_plants_delta"
        ]
        <= -10,
        "adaptive_opponent_self_crop_wood_suppression": adaptive_vs_farm[
            "mean_opponent_from_opponent_delta"
        ]
        <= -20,
        "adaptive_own_score_preservation": adaptive_vs_farm["mean_own_score_delta"]
        >= -40,
    }
    passed = all(checks.values())
    return {
        **base,
        "opponent_mean_margin_deltas": opponent_deltas,
        "nonnegative_opponents": nonnegative,
        "worst_opponent_mean_margin_delta": worst,
        "adaptive_gold": {
            "prefruit_minus_resident": adaptive_vs_resident,
            "prefruit_minus_farm": adaptive_vs_farm,
        },
        "activation_diagnostic": activation_diagnostic(candidate, farm, resident),
        "gate_checks": checks,
        "passed": passed,
        "decision": (
            "open unchanged confirmation"
            if phase == "discovery" and passed
            else "qualify for packaging and field-prefix audit"
            if phase == "confirmation" and passed
            else "close pre-fruit reproductive interruption without tuning"
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

