#!/usr/bin/env python3
"""Analyze integrity, discovery, and confirmation ownership-aware farm panels."""

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


PROFILES = {"resident", "lean_m2c2h0k2", "ownership_aware"}
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
)
COMPARISON_FIELDS = (
    "margin",
    "own_score",
    "opponent_score",
    "own_inventory_wood",
    "opponent_inventory_wood",
    "own_from_opponent",
    "opponent_from_opponent",
)
INACTIVE_IDENTITY_FIELDS = COMPARISON_FIELDS + (
    "workers",
    "terminal_turn",
    "own_successful_plants",
    "opponent_successful_plants",
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


def trimmed_mean(values: list[int], fraction: float = 0.05) -> float:
    ordered = sorted(values)
    trim = math.floor(len(ordered) * fraction)
    kept = ordered[trim : len(ordered) - trim] if trim else ordered
    return statistics.mean(kept)


def identity(row: dict) -> tuple[int, int, str]:
    return row["seed"], row["seat"], row["opponent"]


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


def activation_diagnostic(
    aware: list[dict], farm: list[dict], resident: list[dict]
) -> dict:
    """Decompose how much of the farm/resident gap an active override recovers."""

    aware_map = {identity(row): row for row in aware}
    farm_map = {identity(row): row for row in farm}
    resident_map = {identity(row): row for row in resident}
    if aware_map.keys() != farm_map.keys() or aware_map.keys() != resident_map.keys():
        raise ValueError("activation diagnostic profiles have different grids")

    def summarize_keys(keys: list[tuple[int, int, str]]) -> dict:
        active = [key for key in keys if aware_map[key]["activation_turns"] > 0]
        inactive = [key for key in keys if aware_map[key]["activation_turns"] == 0]
        aware_farm_margin = statistics.mean(
            aware_map[key]["margin"] - farm_map[key]["margin"] for key in keys
        )
        recovery_need = statistics.mean(
            resident_map[key]["margin"] - farm_map[key]["margin"] for key in keys
        )
        active_margin = (
            statistics.mean(
                aware_map[key]["margin"] - farm_map[key]["margin"] for key in active
            )
            if active
            else None
        )
        return {
            "cells": len(keys),
            "activated_cells": len(active),
            "activation_rate": len(active) / len(keys),
            "mean_activation_turns": statistics.mean(
                aware_map[key]["activation_turns"] for key in keys
            ),
            "median_first_activation_turn_when_active": (
                statistics.median(
                    aware_map[key]["first_activation_turn"] for key in active
                )
                if active
                else None
            ),
            "mean_margin_delta_vs_farm": aware_farm_margin,
            "mean_margin_delta_vs_farm_when_active": active_margin,
            "mean_own_score_delta_vs_farm": statistics.mean(
                aware_map[key]["own_score"] - farm_map[key]["own_score"] for key in keys
            ),
            "mean_opponent_score_delta_vs_farm": statistics.mean(
                aware_map[key]["opponent_score"] - farm_map[key]["opponent_score"]
                for key in keys
            ),
            "mean_opponent_successful_plants_delta_vs_farm": statistics.mean(
                aware_map[key]["opponent_successful_plants"]
                - farm_map[key]["opponent_successful_plants"]
                for key in keys
            ),
            "resident_opponent_successful_plants_advantage_over_farm": statistics.mean(
                farm_map[key]["opponent_successful_plants"]
                - resident_map[key]["opponent_successful_plants"]
                for key in keys
            ),
            "mean_own_opponent_crop_wood_delta_vs_farm": statistics.mean(
                aware_map[key]["own_from_opponent"]
                - farm_map[key]["own_from_opponent"]
                for key in keys
            ),
            "mean_opponent_self_crop_wood_delta_vs_farm": statistics.mean(
                aware_map[key]["opponent_from_opponent"]
                - farm_map[key]["opponent_from_opponent"]
                for key in keys
            ),
            "resident_margin_advantage_over_farm": recovery_need,
            "fraction_of_resident_advantage_recovered": (
                aware_farm_margin / recovery_need if recovery_need > 0 else None
            ),
            "inactive_cells_exactly_equal_farm": all(
                all(
                    aware_map[key][field] == farm_map[key][field]
                    for field in INACTIVE_IDENTITY_FIELDS
                )
                for key in inactive
            ),
        }

    keys = sorted(aware_map)
    opponents = sorted({key[2] for key in keys})
    return {
        "overall": summarize_keys(keys),
        "opponents": {
            opponent: summarize_keys([key for key in keys if key[2] == opponent])
            for opponent in opponents
        },
    }


def summarize(rows: list[dict]) -> dict:
    by_opponent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_opponent[row["opponent"]].append(row)
    total_chop = sum(row["total_chop_wood"] for row in rows)
    assigned = sum(row["assigned_chop_wood"] for row in rows)
    return {
        "scenarios": len(rows),
        "mean_score": statistics.mean(row["own_score"] for row in rows),
        "mean_opponent_score": statistics.mean(row["opponent_score"] for row in rows),
        "mean_margin": statistics.mean(row["margin"] for row in rows),
        "mean_inventory_wood": statistics.mean(row["own_inventory_wood"] for row in rows),
        "mean_opponent_inventory_wood": statistics.mean(
            row["opponent_inventory_wood"] for row in rows
        ),
        "mean_workers": statistics.mean(row["workers"] for row in rows),
        "activated_cells": sum(row["activation_turns"] > 0 for row in rows),
        "mean_activation_turns": statistics.mean(row["activation_turns"] for row in rows),
        "mean_opponent_crops_seen": statistics.mean(
            row["opponent_crops_seen"] for row in rows
        ),
        "provenance_assignment_rate": assigned / total_chop if total_chop else None,
        "ambiguous_births": sum(row["ambiguous_births"] for row in rows),
        "base_command_mismatches": sum(row["base_command_mismatches"] for row in rows),
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
            opponent: {
                "scenarios": len(group),
                "mean_margin": statistics.mean(row["margin"] for row in group),
                "mean_score": statistics.mean(row["own_score"] for row in group),
                "mean_opponent_score": statistics.mean(
                    row["opponent_score"] for row in group
                ),
                "activated_cells": sum(row["activation_turns"] > 0 for row in group),
            }
            for opponent, group in sorted(by_opponent.items())
        },
    }


def old_reference_parity(rows: list[dict], reference: Path) -> dict:
    selected = {}
    with reference.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            if row["genome"] == "lean_m2c2h0k2":
                selected[(int(row["seed"]), int(row["seat"]), row["opponent"])] = row
    mismatches = []
    for row in rows:
        if row["profile"] not in {"resident", "lean_m2c2h0k2"}:
            continue
        old = selected.get(identity(row))
        if old is None:
            mismatches.append({"identity": identity(row), "reason": "missing reference"})
            continue
        prefix = "resident" if row["profile"] == "resident" else "candidate"
        mapping = {
            "margin": f"{prefix}_margin",
            "own_score": f"{prefix}_score",
            "opponent_score": f"{prefix}_opponent_score",
            "own_inventory_wood": f"{prefix}_wood",
            "opponent_inventory_wood": f"{prefix}_opponent_wood",
            "workers": f"{prefix}_workers",
            "terminal_turn": f"{prefix}_terminal_turn",
        }
        changed = {
            field: [row[field], int(old[old_field])]
            for field, old_field in mapping.items()
            if row[field] != int(old[old_field])
        }
        if changed:
            mismatches.append(
                {"identity": identity(row), "profile": row["profile"], "changed": changed}
            )
    return {
        "reference_rows": len(selected),
        "comparisons": sum(row["profile"] in {"resident", "lean_m2c2h0k2"} for row in rows),
        "mismatches": mismatches,
        "passed": len(selected) == 480 and not mismatches,
    }


def analyze(
    rows: list[dict],
    phase: str,
    reference: Path | None = None,
    repeat_exact: bool | None = None,
) -> dict:
    unique = [(identity(row), row["profile"]) for row in rows]
    if len(unique) != len(set(unique)):
        raise ValueError("duplicate scenario-profile rows")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["profile"]].append(row)
    if set(grouped) != PROFILES:
        raise ValueError(f"expected profiles {sorted(PROFILES)}")
    grids = [{identity(row) for row in group} for group in grouped.values()]
    if any(grid != grids[0] for grid in grids[1:]):
        raise ValueError("profiles have different grids")
    expected_range = {
        "integrity": range(0, 30),
        "discovery": range(1660, 1720),
        "confirmation": range(1720, 1780),
    }[phase]
    expected = {
        (seed, seat, opponent)
        for seed in expected_range
        for seat in (0, 1)
        for opponent in {
            "compact_gold",
            "gold_adaptive",
            "gold_elite",
            "mybot",
            "printer_bot",
            "sched_bot",
            "script_boss",
            "silver_boss",
        }
    }
    if grids[0] != expected:
        raise ValueError("input is not the frozen complete grid")
    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    aware_resident = compare(grouped["ownership_aware"], grouped["resident"])
    aware_farm = compare(grouped["ownership_aware"], grouped["lean_m2c2h0k2"])
    integrity = {
        "complete_grid": len(rows) == len(expected) * 3,
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "provenance_assignment": all(
            report["provenance_assignment_rate"] is not None
            and report["provenance_assignment_rate"] >= 0.95
            for report in reports.values()
        ),
    }
    parity = old_reference_parity(rows, reference) if reference else None
    if phase == "integrity":
        integrity["same_build_farm_shadow_parity"] = (
            reports["ownership_aware"]["base_command_mismatches"] == 0
        )
        integrity["repeat_run_identity"] = repeat_exact is True
        return {
            "schema": 1,
            "phase": phase,
            "profiles": reports,
            "ownership_aware_minus_resident": aware_resident,
            "ownership_aware_minus_farm": aware_farm,
            "historical_reference_parity_informational": parity,
            "integrity_checks": integrity,
            "passed": all(integrity.values()),
            "decision": "open frozen discovery" if all(integrity.values()) else "repair implementation",
        }

    opponent_deltas = {
        opponent: compare(
            [row for row in grouped["ownership_aware"] if row["opponent"] == opponent],
            [row for row in grouped["resident"] if row["opponent"] == opponent],
        )["mean_margin_delta"]
        for opponent in reports["ownership_aware"]["opponents"]
    }
    adaptive_aware = [
        row for row in grouped["ownership_aware"] if row["opponent"] == "gold_adaptive"
    ]
    adaptive_farm = [
        row for row in grouped["lean_m2c2h0k2"] if row["opponent"] == "gold_adaptive"
    ]
    adaptive_resident = [
        row for row in grouped["resident"] if row["opponent"] == "gold_adaptive"
    ]
    adaptive_vs_farm = compare(adaptive_aware, adaptive_farm)
    adaptive_vs_resident = compare(adaptive_aware, adaptive_resident)
    nonnegative = sum(value >= 0 for value in opponent_deltas.values())
    worst = min(opponent_deltas.values())
    mean_floor = 10 if phase == "confirmation" else 10
    trim_floor = 10 if phase == "confirmation" else 5
    checks = {
        "integrity": all(integrity.values()),
        "mean_margin": aware_resident["mean_margin_delta"] >= mean_floor,
        "trimmed_margin": aware_resident["trimmed_5pct_mean_margin_delta"] >= trim_floor,
        "own_score": aware_resident["mean_own_score_delta"] >= 50,
        "own_wood": aware_resident["mean_own_inventory_wood_delta"] >= 10,
        "opponent_breadth": nonnegative >= 6,
        "worst_opponent": worst >= -5,
        "adaptive_gold_margin": adaptive_vs_resident["mean_margin_delta"] >= 0,
        "activation_overall": reports["ownership_aware"]["activated_cells"] >= 200,
        "activation_adaptive_gold": reports["ownership_aware"]["opponents"][
            "gold_adaptive"
        ]["activated_cells"]
        >= 30,
        "adaptive_opponent_score_suppression": adaptive_vs_farm[
            "mean_opponent_score_delta"
        ]
        <= -25,
        "adaptive_own_score_preservation": adaptive_vs_farm["mean_own_score_delta"]
        >= -50,
    }
    passed = all(checks.values())
    return {
        "schema": 1,
        "phase": phase,
        "profiles": reports,
        "ownership_aware_minus_resident": aware_resident,
        "ownership_aware_minus_farm": aware_farm,
        "opponent_mean_margin_deltas": opponent_deltas,
        "nonnegative_opponents": nonnegative,
        "worst_opponent_mean_margin_delta": worst,
        "adaptive_gold": {
            "ownership_aware_minus_resident": adaptive_vs_resident,
            "ownership_aware_minus_farm": adaptive_vs_farm,
        },
        "activation_diagnostic": activation_diagnostic(
            grouped["ownership_aware"], grouped["lean_m2c2h0k2"], grouped["resident"]
        ),
        "integrity_checks": integrity,
        "gate_checks": checks,
        "passed": passed,
        "decision": (
            "open unchanged confirmation"
            if phase == "discovery" and passed
            else "qualify for packaging and field-prefix audit"
            if phase == "confirmation" and passed
            else "close race-conditioned ownership-aware farm without tuning"
        ),
    }


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("integrity", "discovery", "confirmation"), required=True)
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--repeat", type=Path)
    args = parser.parse_args()
    repeat_exact = (
        args.repeat.read_bytes() == args.input.read_bytes() if args.repeat else None
    )
    payload = analyze(read_rows(args.input), args.phase, args.reference, repeat_exact)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
