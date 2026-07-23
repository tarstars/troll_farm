#!/usr/bin/env python3
"""Analyze consumed-map reproductive stock flow and lineage bottlenecks."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import statistics


PROFILES = {"resident", "lean_m2c2h0k2", "adaptive_density"}
ORIGINS = ("natural", "ours", "opponent", "unknown")
KINDS = ("plum", "lemon", "apple", "banana")
PHASES = (
    ("1_100", 1, 100),
    ("101_150", 101, 150),
    ("151_200", 151, 200),
    ("201_250", 201, 250),
    ("251_300", 251, 300),
)
CHECKPOINTS = (100, 150, 200, 250, 300)
CHECKPOINT_FIELDS = (
    "recorded",
    "opponent_score",
    "opponent_wood",
    "opponent_workers",
    "opponent_successful_plants",
    "banked_banana",
    "carried_banana",
    "opponent_banana_crops",
    "opponent_unfruited_banana_crops",
    "opponent_crop_banana_fruits",
    "natural_banana_fruits",
    "our_crop_banana_fruits",
)
BASE_FIELDS = (
    "seed",
    "seat",
    "own_score",
    "opponent_score",
    "margin",
    "own_inventory_wood",
    "opponent_inventory_wood",
    "terminal_turn",
    "own_successful_plants",
    "opponent_successful_plants",
    "own_early_successful_plants",
    "opponent_early_successful_plants",
    "ambiguous_births",
    "total_chop_wood",
    "assigned_chop_wood",
)
WOOD_FIELDS = tuple(
    f"{collector}_from_{origin}"
    for collector in ("own", "opponent")
    for origin in ORIGINS
)
FRUIT_FIELDS = tuple(
    f"{collector}_{phase}_from_{origin}_{kind}"
    for phase in ("fruit", "early_fruit")
    for collector in ("own", "opponent")
    for origin in ORIGINS
    for kind in KINDS
)
PHASE_FIELDS = tuple(
    f"{collector}_successful_plants_{phase}"
    for collector in ("own", "opponent")
    for phase, _, _ in PHASES
)
FLOW_FIELDS = (
    "post100_exposure_turns",
    "zero_immediate_seed_turns",
    "zero_owned_seed_turns",
    "lineage_absent_turns",
    "low_redundancy_turns",
    "max_zero_owned_streak",
    "minimum_immediate_seeds",
    "minimum_owned_seed_stock",
)
SNAPSHOT_FIELDS = tuple(
    f"t{checkpoint}_{field}"
    for checkpoint in CHECKPOINTS
    for field in CHECKPOINT_FIELDS
)
INTEGER_FIELDS = (
    BASE_FIELDS
    + WOOD_FIELDS
    + FRUIT_FIELDS
    + PHASE_FIELDS
    + FLOW_FIELDS
    + SNAPSHOT_FIELDS
)


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def phase_exposure(row: dict, start: int, end: int) -> int:
    last_resolved = row["terminal_turn"] - 1
    return max(0, min(end, last_resolved) - start + 1)


def assignment_rates(rows: list[dict]) -> tuple[float, float]:
    total_wood = sum(row["total_chop_wood"] for row in rows)
    assigned_wood = sum(row["assigned_chop_wood"] for row in rows)
    total_fruit = sum(
        row[f"{collector}_fruit_from_{origin}_{kind}"]
        for row in rows
        for collector in ("own", "opponent")
        for origin in ORIGINS
        for kind in KINDS
    )
    unknown_fruit = sum(
        row[f"{collector}_fruit_from_unknown_{kind}"]
        for row in rows
        for collector in ("own", "opponent")
        for kind in KINDS
    )
    return (
        assigned_wood / total_wood if total_wood else 1.0,
        (total_fruit - unknown_fruit) / total_fruit if total_fruit else 1.0,
    )


def checkpoint_summary(rows: list[dict], checkpoint: int) -> dict:
    recorded = [row for row in rows if row[f"t{checkpoint}_recorded"]]
    fields = CHECKPOINT_FIELDS[1:]
    return {
        "recorded_games": len(recorded),
        "means": {
            field: statistics.mean(row[f"t{checkpoint}_{field}"] for row in recorded)
            if recorded
            else None
            for field in fields
        },
        "medians": {
            field: statistics.median(row[f"t{checkpoint}_{field}"] for row in recorded)
            if recorded
            else None
            for field in fields
        },
        "zero_owned_seed_games": sum(
            row[f"t{checkpoint}_banked_banana"]
            + row[f"t{checkpoint}_carried_banana"]
            + row[f"t{checkpoint}_opponent_crop_banana_fruits"]
            == 0
            for row in recorded
        ),
        "lineage_absent_games": sum(
            row[f"t{checkpoint}_banked_banana"]
            + row[f"t{checkpoint}_carried_banana"]
            + row[f"t{checkpoint}_opponent_crop_banana_fruits"]
            == 0
            and row[f"t{checkpoint}_opponent_banana_crops"] == 0
            for row in recorded
        ),
    }


def summarize(rows: list[dict]) -> dict:
    exposure = sum(row["post100_exposure_turns"] for row in rows)
    wood_rate, fruit_rate = assignment_rates(rows)
    flow_totals = {
        field: sum(row[field] for row in rows)
        for field in (
            "zero_immediate_seed_turns",
            "zero_owned_seed_turns",
            "lineage_absent_turns",
            "low_redundancy_turns",
        )
    }
    phase = {}
    for label, start, end in PHASES:
        phase_exposed = sum(phase_exposure(row, start, end) for row in rows)
        plants = sum(row[f"opponent_successful_plants_{label}"] for row in rows)
        phase[label] = {
            "exposure_turns": phase_exposed,
            "opponent_successful_plants": plants,
            "plants_per_exposed_turn": plants / phase_exposed if phase_exposed else None,
        }
    return {
        "games": len(rows),
        "mean_terminal_turn": statistics.mean(row["terminal_turn"] for row in rows),
        "median_terminal_turn": statistics.median(row["terminal_turn"] for row in rows),
        "turn_limit_games": sum(row["terminal_turn"] == 301 for row in rows),
        "post100_exposure_turns": exposure,
        "flow_turns": flow_totals,
        "flow_rates": {
            field.removesuffix("_turns"): total / exposure if exposure else None
            for field, total in flow_totals.items()
        },
        "games_with_zero_owned_streak_at_least_5": sum(
            row["max_zero_owned_streak"] >= 5 for row in rows
        ),
        "games_with_lineage_absence": sum(
            row["lineage_absent_turns"] > 0 for row in rows
        ),
        "mean_max_zero_owned_streak": statistics.mean(
            row["max_zero_owned_streak"] for row in rows
        ),
        "minimum_owned_seed_stock_distribution": {
            "mean": statistics.mean(row["minimum_owned_seed_stock"] for row in rows),
            "median": statistics.median(
                row["minimum_owned_seed_stock"] for row in rows
            ),
            "zero_games": sum(row["minimum_owned_seed_stock"] == 0 for row in rows),
        },
        "mean_opponent_score": statistics.mean(row["opponent_score"] for row in rows),
        "mean_opponent_wood": statistics.mean(
            row["opponent_inventory_wood"] for row in rows
        ),
        "opponent_successful_plants": sum(
            row["opponent_successful_plants"] for row in rows
        ),
        "wood_assignment_rate": wood_rate,
        "fruit_assignment_rate": fruit_rate,
        "phase_planting": phase,
        "checkpoints": {
            str(checkpoint): checkpoint_summary(rows, checkpoint)
            for checkpoint in CHECKPOINTS
        },
    }


def integrity_checks(rows: list[dict], reports: dict, repeat_exact: bool | None) -> dict:
    phase_sums = all(
        sum(row[f"own_successful_plants_{label}"] for label, _, _ in PHASES)
        == row["own_successful_plants"]
        and sum(
            row[f"opponent_successful_plants_{label}"] for label, _, _ in PHASES
        )
        == row["opponent_successful_plants"]
        for row in rows
    )
    checkpoint_presence = all(
        bool(row[f"t{checkpoint}_recorded"])
        == (row["terminal_turn"] > checkpoint)
        for row in rows
        for checkpoint in CHECKPOINTS
    )
    monotone = True
    for row in rows:
        values = [
            row[f"t{checkpoint}_opponent_successful_plants"]
            for checkpoint in CHECKPOINTS
            if row[f"t{checkpoint}_recorded"]
        ]
        monotone &= values == sorted(values)
    checks = {
        "complete_grid": len(rows) == 180,
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "phase_counts_sum_to_totals": phase_sums,
        "checkpoint_presence_matches_terminal_exposure": checkpoint_presence,
        "checkpoint_plants_are_monotone": monotone,
        "fruit_assignment_at_least_99pct": all(
            report["fruit_assignment_rate"] >= 0.99 for report in reports.values()
        ),
        "wood_assignment_at_least_95pct": all(
            report["wood_assignment_rate"] >= 0.95 for report in reports.values()
        ),
        "repeat_run_identity": repeat_exact is True,
    }
    return checks


def analyze(rows: list[dict], repeat_exact: bool | None = None) -> dict:
    identities = [(row["seed"], row["seat"], row["profile"]) for row in rows]
    if len(identities) != len(set(identities)):
        raise ValueError("duplicate scenario-profile rows")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["profile"]].append(row)
    if set(grouped) != PROFILES:
        raise ValueError(f"expected profiles {sorted(PROFILES)}")
    expected = {(seed, seat) for seed in range(30) for seat in (0, 1)}
    if any(
        {(row["seed"], row["seat"]) for row in group} != expected
        for group in grouped.values()
    ):
        raise ValueError("input is not the frozen 0--29 both-seat grid")

    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    integrity = integrity_checks(rows, reports, repeat_exact)
    resident = reports["resident"]
    farms = [reports["lean_m2c2h0k2"], reports["adaptive_density"]]
    zero_rate = resident["flow_rates"]["zero_owned_seed"]
    absent_rate = resident["flow_rates"]["lineage_absent"]
    seed_checks = {
        "resident_zero_owned_seed_rate_at_least_15pct": zero_rate >= 0.15,
        "resident_streak_breadth_at_least_30_games": resident[
            "games_with_zero_owned_streak_at_least_5"
        ]
        >= 30,
        "resident_zero_owned_rate_10pp_above_both_farms": all(
            zero_rate - farm["flow_rates"]["zero_owned_seed"] >= 0.10
            for farm in farms
        ),
    }
    absence_checks = {
        "resident_lineage_absent_rate_at_least_5pct": absent_rate >= 0.05,
        "resident_absence_breadth_at_least_20_games": resident[
            "games_with_lineage_absence"
        ]
        >= 20,
        "resident_absence_rate_3pp_above_both_farms": all(
            absent_rate - farm["flow_rates"]["lineage_absent"] >= 0.03
            for farm in farms
        ),
    }
    integrity_passed = all(integrity.values())
    seed_boundary = integrity_passed and all(seed_checks.values())
    absence_boundary = integrity_passed and all(absence_checks.values())
    return {
        "schema": 1,
        "scope": "consumed-map adaptive-Gold reproductive stock-flow diagnostic",
        "seed_range": [0, 29],
        "profiles": reports,
        "integrity_checks": integrity,
        "seed_depletion_boundary_checks": seed_checks,
        "lineage_absence_boundary_checks": absence_checks,
        "material_seed_depletion_boundary": seed_boundary,
        "material_lineage_absence_boundary": absence_boundary,
        "decision": (
            "authorize one stock-state whole-scheduler experiment"
            if seed_boundary or absence_boundary
            else "close direct reproductive denial; prioritize production and terminal policy"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repeat", type=Path)
    args = parser.parse_args()
    repeat_exact = (
        args.repeat.read_bytes() == args.input.read_bytes() if args.repeat else None
    )
    payload = analyze(read_rows(args.input), repeat_exact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0 if all(payload["integrity_checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

