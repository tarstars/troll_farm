#!/usr/bin/env python3
"""Analyze fruit provenance in the resident/farm adaptive-Gold decomposition."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import statistics


PROFILES = {"resident", "lean_m2c2h0k2"}
ORIGINS = ("natural", "ours", "opponent", "unknown")
KINDS = ("plum", "lemon", "apple", "banana")
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
INTEGER_FIELDS = BASE_FIELDS + WOOD_FIELDS + FRUIT_FIELDS


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def fruit_tree(totals: dict, collector: str, phase: str) -> dict:
    return {
        origin: {
            kind: totals[f"{collector}_{phase}_from_{origin}_{kind}"]
            for kind in KINDS
        }
        for origin in ORIGINS
    }


def assigned_fruit(totals: dict, phase: str) -> tuple[int, int]:
    fields = [
        f"{collector}_{phase}_from_{origin}_{kind}"
        for collector in ("own", "opponent")
        for origin in ORIGINS
        for kind in KINDS
    ]
    total = sum(totals[field] for field in fields)
    unknown = sum(
        totals[f"{collector}_{phase}_from_unknown_{kind}"]
        for collector in ("own", "opponent")
        for kind in KINDS
    )
    return total - unknown, total


def summarize(rows: list[dict]) -> dict:
    totals = {field: sum(row[field] for row in rows) for field in INTEGER_FIELDS[2:]}
    assigned, fruit_total = assigned_fruit(totals, "fruit")
    return {
        "scenarios": len(rows),
        "mean_score": statistics.mean(row["own_score"] for row in rows),
        "mean_opponent_score": statistics.mean(row["opponent_score"] for row in rows),
        "mean_margin": statistics.mean(row["margin"] for row in rows),
        "mean_inventory_wood": statistics.mean(
            row["own_inventory_wood"] for row in rows
        ),
        "mean_opponent_inventory_wood": statistics.mean(
            row["opponent_inventory_wood"] for row in rows
        ),
        "successful_plants": totals["own_successful_plants"],
        "opponent_successful_plants": totals["opponent_successful_plants"],
        "early_successful_plants": totals["own_early_successful_plants"],
        "opponent_early_successful_plants": totals[
            "opponent_early_successful_plants"
        ],
        "fruit_assignment_rate": assigned / fruit_total if fruit_total else None,
        "fruit": {
            collector: fruit_tree(totals, collector, "fruit")
            for collector in ("own", "opponent")
        },
        "early_fruit": {
            collector: fruit_tree(totals, collector, "early_fruit")
            for collector in ("own", "opponent")
        },
        "wood_assignment_rate": totals["assigned_chop_wood"]
        / totals["total_chop_wood"],
    }


def subtract_tree(left: dict, right: dict) -> dict:
    return {
        origin: {
            kind: left[origin][kind] - right[origin][kind] for kind in KINDS
        }
        for origin in ORIGINS
    }


def origin_totals(tree: dict) -> dict:
    return {origin: sum(tree[origin].values()) for origin in ORIGINS}


def analyze(rows: list[dict]) -> dict:
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
    resident = reports["resident"]
    farm = reports["lean_m2c2h0k2"]
    opponent_fruit_delta = subtract_tree(
        farm["fruit"]["opponent"], resident["fruit"]["opponent"]
    )
    opponent_early_delta = subtract_tree(
        farm["early_fruit"]["opponent"],
        resident["early_fruit"]["opponent"],
    )
    early_origin_delta = origin_totals(opponent_early_delta)
    total_origin_delta = origin_totals(opponent_fruit_delta)
    plant_delta = (
        farm["opponent_successful_plants"] - resident["opponent_successful_plants"]
    )
    early_plant_delta = (
        farm["opponent_early_successful_plants"]
        - resident["opponent_early_successful_plants"]
    )
    natural_early = early_origin_delta["natural"]
    material_upstream = natural_early >= 60 and early_plant_delta >= 60
    dominant_added_origin = max(total_origin_delta, key=total_origin_delta.get)
    integrity = {
        "complete_common_grid": len(rows) == 120,
        "all_games_complete": all(row["terminal_turn"] > 1 for row in rows),
        "minimum_fruit_assignment": all(
            report["fruit_assignment_rate"] is not None
            and report["fruit_assignment_rate"] >= 0.99
            for report in reports.values()
        ),
        "minimum_wood_assignment": all(
            report["wood_assignment_rate"] >= 0.95 for report in reports.values()
        ),
        "reproduces_prior_margin_delta": abs(
            (farm["mean_margin"] - resident["mean_margin"]) - (-47.93333333333333)
        )
        < 1e-9,
    }
    passed = all(integrity.values())
    return {
        "schema": 1,
        "scope": (
            "consumed-map causal fruit-provenance decomposition; no candidate outcome "
            "qualification"
        ),
        "seed_range": [0, 29],
        "scenarios_per_profile": 60,
        "profiles": reports,
        "farm_minus_resident": {
            "opponent_successful_plants": plant_delta,
            "opponent_early_successful_plants": early_plant_delta,
            "opponent_fruit_by_origin_and_kind": opponent_fruit_delta,
            "opponent_fruit_by_origin": total_origin_delta,
            "opponent_early_fruit_by_origin_and_kind": opponent_early_delta,
            "opponent_early_fruit_by_origin": early_origin_delta,
            "natural_early_fruit_per_game": natural_early / 60,
            "dominant_added_fruit_origin": dominant_added_origin,
        },
        "integrity_checks": integrity,
        "material_upstream_natural_seed_mechanism": passed and material_upstream,
        "decision": (
            "authorize fresh pre-first-harvest source-interruption experiment"
            if passed and material_upstream
            else "close natural-source interruption; continue whole-policy scheduler work"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(read_rows(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0 if all(payload["integrity_checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
