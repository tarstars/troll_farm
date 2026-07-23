#!/usr/bin/env python3
"""Analyze the frozen resident-chopper component-swap experiment."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import statistics
import tempfile

try:
    from cgauto.ownership_aware_complete_economy import (
        compare,
        identity,
        read_rows,
        summarize,
    )
except ModuleNotFoundError:  # direct execution from the repository root
    from ownership_aware_complete_economy import compare, identity, read_rows, summarize


PROFILES = {"resident", "lean_m2c2h0k2", "resident_chopper_hybrid"}
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
COPIED_FIELDS = (
    "copied_move",
    "copied_chop",
    "copied_drop",
    "copied_mine",
    "copied_pick",
    "copied_harvest",
    "copied_plant",
)


def load_rows(path: Path) -> list[dict]:
    rows = read_rows(path)
    for row in rows:
        for field in COPIED_FIELDS:
            row[field] = int(row[field])
    return rows


def paired_mean(left: list[dict], right: list[dict], field: str) -> float:
    left_map = {identity(row): row for row in left}
    right_map = {identity(row): row for row in right}
    if left_map.keys() != right_map.keys():
        raise ValueError("paired profiles have different grids")
    return statistics.mean(left_map[key][field] - right_map[key][field] for key in left_map)


def analyze(rows: list[dict], phase: str, repeat_exact: bool | None = None) -> dict:
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
    seed_range = {
        "integrity": range(0, 30),
        "discovery": range(1780, 1840),
        "confirmation": range(1840, 1900),
    }[phase]
    expected = {
        (seed, seat, opponent)
        for seed in seed_range
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    if grids[0] != expected:
        raise ValueError("input is not the frozen complete grid")

    hybrid = grouped["resident_chopper_hybrid"]
    farm = grouped["lean_m2c2h0k2"]
    resident = grouped["resident"]
    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    hybrid_resident = compare(hybrid, resident)
    hybrid_farm = compare(hybrid, farm)
    integrity = {
        "complete_grid": len(rows) == len(expected) * 3,
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "provenance_assignment": all(
            report["provenance_assignment_rate"] is not None
            and report["provenance_assignment_rate"] >= 0.95
            for report in reports.values()
        ),
        "same_build_farm_shadow_parity": reports["resident_chopper_hybrid"][
            "base_command_mismatches"
        ]
        == 0,
    }
    activated = sum(row["activation_turns"] > 0 for row in hybrid)
    if phase == "integrity":
        integrity["substituted_cells"] = activated >= 400
        integrity["repeat_run_identity"] = repeat_exact is True
        passed = all(integrity.values())
        return {
            "schema": 1,
            "phase": phase,
            "profiles": reports,
            "hybrid_minus_resident": hybrid_resident,
            "hybrid_minus_farm": hybrid_farm,
            "hybrid_telemetry": {
                "activated_cells": activated,
                "mean_substitution_turns": statistics.mean(
                    row["activation_turns"] for row in hybrid
                ),
                "copied_verbs": {
                    field.removeprefix("copied_"): sum(row[field] for row in hybrid)
                    for field in COPIED_FIELDS
                },
            },
            "integrity_checks": integrity,
            "passed": passed,
            "decision": "open frozen discovery" if passed else "repair implementation",
        }

    opponent_deltas = {
        opponent: compare(
            [row for row in hybrid if row["opponent"] == opponent],
            [row for row in resident if row["opponent"] == opponent],
        )["mean_margin_delta"]
        for opponent in sorted(OPPONENTS)
    }
    adaptive_hybrid = [row for row in hybrid if row["opponent"] == "gold_adaptive"]
    adaptive_farm = [row for row in farm if row["opponent"] == "gold_adaptive"]
    adaptive_resident = [row for row in resident if row["opponent"] == "gold_adaptive"]
    adaptive_vs_farm = compare(adaptive_hybrid, adaptive_farm)
    adaptive_vs_resident = compare(adaptive_hybrid, adaptive_resident)
    adaptive_plant_delta = paired_mean(
        adaptive_hybrid, adaptive_farm, "opponent_successful_plants"
    )
    adaptive_self_crop_delta = paired_mean(
        adaptive_hybrid, adaptive_farm, "opponent_from_opponent"
    )
    mean_floor = 10
    trim_floor = 10 if phase == "confirmation" else 5
    checks = {
        "integrity": all(integrity.values()),
        "mean_margin": hybrid_resident["mean_margin_delta"] >= mean_floor,
        "trimmed_margin": hybrid_resident["trimmed_5pct_mean_margin_delta"] >= trim_floor,
        "own_score": hybrid_resident["mean_own_score_delta"] >= 50,
        "own_wood": hybrid_resident["mean_own_inventory_wood_delta"] >= 10,
        "opponent_breadth": sum(value >= 0 for value in opponent_deltas.values()) >= 6,
        "worst_opponent": min(opponent_deltas.values()) >= -5,
        "adaptive_gold_margin": adaptive_vs_resident["mean_margin_delta"] >= 0,
        "adaptive_own_score_preservation": adaptive_vs_farm["mean_own_score_delta"] >= -30,
        "adaptive_opponent_score_suppression": adaptive_vs_farm[
            "mean_opponent_score_delta"
        ]
        <= -50,
        "adaptive_plant_suppression": adaptive_plant_delta <= -10,
        "adaptive_self_crop_wood_suppression": adaptive_self_crop_delta <= -20,
    }
    passed = all(checks.values())
    return {
        "schema": 1,
        "phase": phase,
        "profiles": reports,
        "hybrid_minus_resident": hybrid_resident,
        "hybrid_minus_farm": hybrid_farm,
        "opponent_mean_margin_deltas": opponent_deltas,
        "adaptive_gold": {
            "hybrid_minus_resident": adaptive_vs_resident,
            "hybrid_minus_farm": adaptive_vs_farm,
            "mean_opponent_successful_plants_delta_vs_farm": adaptive_plant_delta,
            "mean_opponent_self_crop_wood_delta_vs_farm": adaptive_self_crop_delta,
        },
        "hybrid_telemetry": {
            "activated_cells": activated,
            "adaptive_activated_cells": sum(
                row["activation_turns"] > 0 for row in adaptive_hybrid
            ),
            "mean_substitution_turns": statistics.mean(
                row["activation_turns"] for row in hybrid
            ),
            "copied_verbs": {
                field.removeprefix("copied_"): sum(row[field] for row in hybrid)
                for field in COPIED_FIELDS
            },
        },
        "integrity_checks": integrity,
        "gate_checks": checks,
        "passed": passed,
        "decision": (
            "open unchanged confirmation"
            if phase == "discovery" and passed
            else "qualify for distillation and field-prefix audit"
            if phase == "confirmation" and passed
            else "close resident chopper-layer swap without tuning"
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
    parser.add_argument("--repeat", type=Path)
    args = parser.parse_args()
    repeat_exact = args.input.read_bytes() == args.repeat.read_bytes() if args.repeat else None
    payload = analyze(load_rows(args.input), args.phase, repeat_exact)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
