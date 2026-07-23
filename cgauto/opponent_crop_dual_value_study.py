#!/usr/bin/env python3
"""Apply the frozen fresh-map safety gate to opponent-crop dual-value scoring."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.yamo_opponent_crop_priority_study import read_rows, trimmed_mean


DUAL = "dual_value_e6"
FLAT = "b100_e6"
EXPECTED_OPPONENTS = {
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
}
GATE = {
    "minimum_mean_margin_delta": -2.0,
    "minimum_trimmed_5pct_mean_margin_delta": -2.0,
    "minimum_mean_score_delta": -2.0,
    "minimum_mean_wood_delta": -1.0,
    "minimum_opponents_above_floor": 6,
    "opponent_mean_margin_floor": -5.0,
    "minimum_worst_opponent_mean_margin_delta": -15.0,
}


def mean(rows: list[dict], field: str) -> float:
    return statistics.mean(row[field] for row in rows)


def summarize(rows: list[dict]) -> dict:
    by_opponent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_opponent[row["opponent"]].append(row)
    margin = [row["margin_delta"] for row in rows]
    opponents = {
        name: {
            "scenarios": len(group),
            "mean_margin_delta": mean(group, "margin_delta"),
            "mean_score_delta": mean(group, "score_delta"),
            "mean_wood_delta": mean(group, "wood_delta"),
            "activated_cells": sum(row["divergence_turns"] > 0 for row in group),
        }
        for name, group in sorted(by_opponent.items())
    }
    return {
        "scenarios": len(rows),
        "activated_cells": sum(row["divergence_turns"] > 0 for row in rows),
        "mean_margin_delta": statistics.mean(margin),
        "trimmed_5pct_mean_margin_delta": trimmed_mean(margin),
        "median_margin_delta": statistics.median(margin),
        "minimum_margin_delta": min(margin),
        "maximum_margin_delta": max(margin),
        "mean_score_delta": mean(rows, "score_delta"),
        "mean_opponent_score_delta": mean(rows, "opponent_score_delta"),
        "mean_wood_delta": mean(rows, "wood_delta"),
        "mean_opponent_wood_delta": mean(rows, "opponent_wood_delta"),
        "mean_divergence_turns": mean(rows, "divergence_turns"),
        "opponents": opponents,
    }


def paired_comparison(dual: list[dict], flat: list[dict]) -> dict:
    identity = lambda row: (row["seed"], row["seat"], row["opponent"])
    left = {identity(row): row for row in dual}
    right = {identity(row): row for row in flat}
    if left.keys() != right.keys():
        raise ValueError("dual and flat profiles have different scenario grids")
    deltas = []
    for key in sorted(left):
        dual_row, flat_row = left[key], right[key]
        deltas.append(
            {
                "margin": dual_row["candidate_margin"] - flat_row["candidate_margin"],
                "score": dual_row["candidate_score"] - flat_row["candidate_score"],
                "opponent_score": dual_row["candidate_opponent_score"]
                - flat_row["candidate_opponent_score"],
                "wood": dual_row["candidate_wood"] - flat_row["candidate_wood"],
                "opponent_wood": dual_row["candidate_opponent_wood"]
                - flat_row["candidate_opponent_wood"],
            }
        )
    margin = [row["margin"] for row in deltas]
    return {
        "scenarios": len(deltas),
        "mean_margin_delta": statistics.mean(margin),
        "trimmed_5pct_mean_margin_delta": trimmed_mean(margin),
        "median_margin_delta": statistics.median(margin),
        "dual_better": sum(value > 0 for value in margin),
        "equal": sum(value == 0 for value in margin),
        "dual_worse": sum(value < 0 for value in margin),
        "mean_score_delta": statistics.mean(row["score"] for row in deltas),
        "mean_opponent_score_delta": statistics.mean(
            row["opponent_score"] for row in deltas
        ),
        "mean_wood_delta": statistics.mean(row["wood"] for row in deltas),
        "mean_opponent_wood_delta": statistics.mean(
            row["opponent_wood"] for row in deltas
        ),
    }


def analyze(rows: list[dict]) -> dict:
    identities = [
        (row["seed"], row["seat"], row["opponent"], row["profile"])
        for row in rows
    ]
    if len(identities) != len(set(identities)):
        raise ValueError("duplicate scenario-profile rows")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["profile"]].append(row)
    if set(grouped) != {DUAL, FLAT}:
        raise ValueError(f"expected exactly {DUAL} and {FLAT}")
    scenarios = {
        (row["seed"], row["seat"], row["opponent"]) for row in grouped[DUAL]
    }
    expected = {
        (seed, seat, opponent)
        for seed in range(1600, 1660)
        for seat in (0, 1)
        for opponent in EXPECTED_OPPONENTS
    }
    if scenarios != expected:
        raise ValueError("input is not the frozen 1600--1659 complete scenario grid")
    dual = summarize(grouped[DUAL])
    flat = summarize(grouped[FLAT])
    opponent_means = [
        report["mean_margin_delta"] for report in dual["opponents"].values()
    ]
    opponents_above_floor = sum(
        value >= GATE["opponent_mean_margin_floor"] for value in opponent_means
    )
    worst = min(opponent_means)
    checks = {
        "mean_margin": dual["mean_margin_delta"]
        >= GATE["minimum_mean_margin_delta"],
        "trimmed_margin": dual["trimmed_5pct_mean_margin_delta"]
        >= GATE["minimum_trimmed_5pct_mean_margin_delta"],
        "own_score": dual["mean_score_delta"] >= GATE["minimum_mean_score_delta"],
        "own_wood": dual["mean_wood_delta"] >= GATE["minimum_mean_wood_delta"],
        "opponent_breadth": opponents_above_floor
        >= GATE["minimum_opponents_above_floor"],
        "worst_opponent": worst
        >= GATE["minimum_worst_opponent_mean_margin_delta"],
    }
    return {
        "schema": 1,
        "scope": "fresh generated-map safety rejection gate; not field-value evidence",
        "seed_range": [1600, 1659],
        "scenarios_per_profile": len(scenarios),
        "profiles": {DUAL: dual, FLAT: flat},
        "dual_minus_flat": paired_comparison(grouped[DUAL], grouped[FLAT]),
        "prospective_gate": GATE,
        "opponents_above_floor": opponents_above_floor,
        "worst_opponent_mean_margin_delta": worst,
        "gate_checks": checks,
        "gate_passed": all(checks.values()),
        "decision": (
            "continue to official-prefix mechanism audit"
            if all(checks.values())
            else "close dual-value scoring without tuning"
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
    return 0 if payload["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
