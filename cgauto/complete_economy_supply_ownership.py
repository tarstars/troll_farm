#!/usr/bin/env python3
"""Analyze the frozen complete-economy supply-ownership diagnostic."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import os
from pathlib import Path
import statistics
import tempfile


PROFILES = {"resident", "lean_m2c2h0k2"}
INTEGER_FIELDS = (
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


def mean(rows: list[dict], field: str) -> float:
    return statistics.mean(row[field] for row in rows)


def summarize(rows: list[dict]) -> dict:
    totals = {field: sum(row[field] for row in rows) for field in INTEGER_FIELDS[2:]}
    return {
        "scenarios": len(rows),
        "mean_score": mean(rows, "own_score"),
        "mean_opponent_score": mean(rows, "opponent_score"),
        "mean_margin": mean(rows, "margin"),
        "mean_inventory_wood": mean(rows, "own_inventory_wood"),
        "mean_opponent_inventory_wood": mean(rows, "opponent_inventory_wood"),
        "mean_successful_plants": mean(rows, "own_successful_plants"),
        "mean_opponent_successful_plants": mean(rows, "opponent_successful_plants"),
        "total_chop_wood": totals["total_chop_wood"],
        "assigned_chop_wood": totals["assigned_chop_wood"],
        "assignment_rate": totals["assigned_chop_wood"] / totals["total_chop_wood"]
        if totals["total_chop_wood"]
        else None,
        "ambiguous_births": totals["ambiguous_births"],
        "wood_by_collector_and_origin": {
            "ours": {
                "natural": totals["own_from_natural"],
                "ours": totals["own_from_ours"],
                "opponent": totals["own_from_opponent"],
                "unknown": totals["own_from_unknown"],
            },
            "opponent": {
                "natural": totals["opponent_from_natural"],
                "ours": totals["opponent_from_ours"],
                "opponent": totals["opponent_from_opponent"],
                "unknown": totals["opponent_from_unknown"],
            },
        },
    }


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
    if any({(row["seed"], row["seat"]) for row in group} != expected for group in grouped.values()):
        raise ValueError("input is not the frozen 0--29 both-seat grid")
    reports = {profile: summarize(group) for profile, group in sorted(grouped.items())}
    resident = reports["resident"]
    farm = reports["lean_m2c2h0k2"]
    resident_opp = resident["wood_by_collector_and_origin"]["opponent"]
    farm_opp = farm["wood_by_collector_and_origin"]["opponent"]
    origins = ("natural", "ours", "opponent", "unknown")
    opponent_increase = {
        origin: farm_opp[origin] - resident_opp[origin] for origin in origins
    }
    total_increase = sum(opponent_increase.values())
    our_crop_increment = opponent_increase["ours"]
    induced_share_from_our_crops = (
        our_crop_increment / total_increase if total_increase > 0 else None
    )
    farm_ours_crop_wood = (
        farm["wood_by_collector_and_origin"]["ours"]["ours"] + farm_opp["ours"]
    )
    rival_capture_share = (
        farm_opp["ours"] / farm_ours_crop_wood if farm_ours_crop_wood else None
    )
    integrity = {
        "complete_common_grid": len(rows) == 120,
        "completed_games": all(row["terminal_turn"] > 1 for row in rows),
        "minimum_provenance_assignment": all(
            report["assignment_rate"] is not None
            and report["assignment_rate"] >= 0.95
            for report in reports.values()
        ),
        "no_ambiguous_births": all(
            report["ambiguous_births"] == 0 for report in reports.values()
        ),
    }
    branch_checks = {
        "farm_induced_opponent_wood_from_our_crops": induced_share_from_our_crops
        is not None
        and induced_share_from_our_crops >= 0.50,
        "opponent_capture_share_of_our_farm": rival_capture_share is not None
        and rival_capture_share >= 0.20,
    }
    direct_capture = all(integrity.values()) and all(branch_checks.values())
    dominant_origin = max(opponent_increase, key=opponent_increase.get)
    return {
        "schema": 1,
        "scope": "consumed-map provenance diagnostic; not candidate outcome qualification",
        "seed_range": [0, 29],
        "scenarios_per_profile": 60,
        "profiles": reports,
        "farm_minus_resident": {
            "mean_margin": farm["mean_margin"] - resident["mean_margin"],
            "mean_score": farm["mean_score"] - resident["mean_score"],
            "mean_opponent_score": farm["mean_opponent_score"]
            - resident["mean_opponent_score"],
            "mean_inventory_wood": farm["mean_inventory_wood"]
            - resident["mean_inventory_wood"],
            "mean_opponent_inventory_wood": farm["mean_opponent_inventory_wood"]
            - resident["mean_opponent_inventory_wood"],
            "opponent_chop_wood_increase_by_origin": opponent_increase,
            "total_opponent_chop_wood_increase": total_increase,
            "our_crop_component_of_increase": our_crop_increment,
            "our_crop_share_of_increase": induced_share_from_our_crops,
            "opponent_capture_share_of_farm_controller_crops": rival_capture_share,
            "dominant_increase_origin": dominant_origin,
        },
        "integrity_gates": integrity,
        "direct_capture_checks": branch_checks,
        "direct_supply_capture": direct_capture,
        "decision": (
            "design a path-private supply grammar"
            if direct_capture
            else "close private placement as primary cause; design opponent-relative throttling/liquidation"
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
    args = parser.parse_args()
    payload = analyze(read_rows(args.input))
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
