#!/usr/bin/env python3
"""Summarize the frozen consumed-seed harvest-on-contact prototype."""

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


INTEGER_FIELDS = (
    "seed",
    "seat",
    "resident_margin",
    "b100_margin",
    "harvest_margin",
    "b100_resident_margin_delta",
    "harvest_resident_margin_delta",
    "harvest_b100_margin_delta",
    "resident_score",
    "b100_score",
    "harvest_score",
    "b100_resident_score_delta",
    "harvest_resident_score_delta",
    "harvest_b100_score_delta",
    "resident_opponent_score",
    "b100_opponent_score",
    "harvest_opponent_score",
    "b100_resident_opponent_score_delta",
    "harvest_resident_opponent_score_delta",
    "harvest_b100_opponent_score_delta",
    "resident_wood",
    "b100_wood",
    "harvest_wood",
    "b100_resident_wood_delta",
    "harvest_resident_wood_delta",
    "harvest_b100_wood_delta",
    "resident_opponent_wood",
    "b100_opponent_wood",
    "harvest_opponent_wood",
    "b100_resident_opponent_wood_delta",
    "harvest_resident_opponent_wood_delta",
    "harvest_b100_opponent_wood_delta",
    "resident_terminal_turn",
    "b100_terminal_turn",
    "harvest_terminal_turn",
    "b100_crops_seen",
    "b100_priority_selections",
    "b100_resident_divergence_turns",
    "b100_resident_first_divergence_turn",
    "harvest_crops_seen",
    "harvest_priority_selections",
    "harvest_rewrites",
    "harvest_b100_divergence_turns",
    "harvest_b100_first_divergence_turn",
)

GATE = {
    "minimum_activated_cells": 80,
    "minimum_harvest_rewrites": 100,
    "minimum_activated_opponents": 8,
    "strictly_positive_mean_margin_delta": True,
    "strictly_positive_trimmed_5pct_mean_margin_delta": True,
    "minimum_favorable_to_unfavorable_ratio": 1.0,
    "strictly_positive_seed_mean_margin_delta": True,
    "strictly_positive_trimmed_seed_mean_margin_delta": True,
    "minimum_mean_score_delta": 0,
    "minimum_mean_wood_delta": 0,
    "maximum_mean_opponent_score_delta": 0,
    "minimum_nonnegative_opponents": 6,
    "minimum_worst_opponent_mean_margin_delta": -2,
}


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def trimmed_mean(values: list[float], fraction: float = 0.05) -> float:
    if not values:
        raise ValueError("cannot trim an empty sample")
    ordered = sorted(values)
    trim = math.floor(fraction * len(ordered))
    kept = ordered[trim : len(ordered) - trim] if trim else ordered
    return statistics.mean(kept)


def distribution(values: list[float]) -> dict:
    if not values:
        raise ValueError("cannot summarize an empty sample")
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "trimmed_5pct_mean": trimmed_mean(values),
        "standard_deviation": statistics.stdev(values) if len(values) > 1 else 0,
        "positive": sum(value > 0 for value in values),
        "zero": sum(value == 0 for value in values),
        "negative": sum(value < 0 for value in values),
        "minimum": min(values),
        "maximum": max(values),
    }


def mean(rows: list[dict], field: str) -> float:
    return statistics.mean(row[field] for row in rows)


def comparison(rows: list[dict], prefix: str) -> dict:
    margin_field = f"{prefix}_margin_delta"
    score_field = f"{prefix}_score_delta"
    opponent_score_field = f"{prefix}_opponent_score_delta"
    wood_field = f"{prefix}_wood_delta"
    opponent_wood_field = f"{prefix}_opponent_wood_delta"
    return {
        "margin_delta": distribution([row[margin_field] for row in rows]),
        "mean_score_delta": mean(rows, score_field),
        "mean_opponent_score_delta": mean(rows, opponent_score_field),
        "mean_wood_delta": mean(rows, wood_field),
        "mean_opponent_wood_delta": mean(rows, opponent_wood_field),
    }


def analyze(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("harvest-on-contact study has no rows")
    identities = {(row["seed"], row["seat"], row["opponent"]) for row in rows}
    if len(identities) != len(rows):
        raise ValueError("duplicate seed/seat/opponent cells")

    primary = comparison(rows, "harvest_b100")
    active_rows = [row for row in rows if row["harvest_b100_divergence_turns"] > 0]
    active_opponents = {row["opponent"] for row in active_rows}
    rewrites = sum(row["harvest_rewrites"] for row in rows)

    by_seed: dict[int, list[int]] = defaultdict(list)
    by_opponent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row["harvest_b100_margin_delta"])
        by_opponent[row["opponent"]].append(row)
    seed_means = [statistics.mean(by_seed[seed]) for seed in sorted(by_seed)]
    seed_distribution = distribution(seed_means)
    opponent_reports = {
        opponent: {
            "scenarios": len(group),
            "activated_cells": sum(
                row["harvest_b100_divergence_turns"] > 0 for row in group
            ),
            "harvest_rewrites": sum(row["harvest_rewrites"] for row in group),
            "mean_margin_delta": mean(group, "harvest_b100_margin_delta"),
            "mean_score_delta": mean(group, "harvest_b100_score_delta"),
            "mean_opponent_score_delta": mean(
                group, "harvest_b100_opponent_score_delta"
            ),
            "mean_wood_delta": mean(group, "harvest_b100_wood_delta"),
        }
        for opponent, group in sorted(by_opponent.items())
    }
    opponent_margins = [
        report["mean_margin_delta"] for report in opponent_reports.values()
    ]
    nonnegative_opponents = sum(value >= 0 for value in opponent_margins)
    worst_opponent = min(opponent_margins)
    margin = primary["margin_delta"]
    favorable_ratio = (
        margin["positive"] / margin["negative"]
        if margin["negative"]
        else math.inf
    )
    checks = {
        "activated_cells": len(active_rows) >= GATE["minimum_activated_cells"],
        "harvest_rewrites": rewrites >= GATE["minimum_harvest_rewrites"],
        "activated_opponents": len(active_opponents)
        >= GATE["minimum_activated_opponents"],
        "mean_margin_delta": margin["mean"] > 0,
        "trimmed_margin_delta": margin["trimmed_5pct_mean"] > 0,
        "favorable_to_unfavorable": favorable_ratio
        >= GATE["minimum_favorable_to_unfavorable_ratio"],
        "seed_mean_margin_delta": seed_distribution["mean"] > 0,
        "trimmed_seed_mean_margin_delta": seed_distribution["trimmed_5pct_mean"] > 0,
        "mean_score_delta": primary["mean_score_delta"]
        >= GATE["minimum_mean_score_delta"],
        "mean_wood_delta": primary["mean_wood_delta"]
        >= GATE["minimum_mean_wood_delta"],
        "mean_opponent_score_delta": primary["mean_opponent_score_delta"]
        <= GATE["maximum_mean_opponent_score_delta"],
        "nonnegative_opponents": nonnegative_opponents
        >= GATE["minimum_nonnegative_opponents"],
        "worst_opponent": worst_opponent
        >= GATE["minimum_worst_opponent_mean_margin_delta"],
    }
    first_turns = [
        row["harvest_b100_first_divergence_turn"]
        for row in active_rows
        if row["harvest_b100_first_divergence_turn"] >= 0
    ]
    seeds = sorted(by_seed)
    return {
        "schema": 1,
        "scope": (
            "consumed generated seeds only; paired complete-policy comparison; "
            "never candidate-qualification evidence"
        ),
        "rows": len(rows),
        "seed_range": [min(seeds), max(seeds)],
        "seed_count": len(seeds),
        "opponents": sorted(by_opponent),
        "primary_comparison": "harvest_contact_minus_b100_e6",
        "prospective_gate": GATE,
        "activation": {
            "cells": len(active_rows),
            "rate": len(active_rows) / len(rows),
            "opponents": len(active_opponents),
            "harvest_rewrites": rewrites,
            "mean_rewrites_per_active_cell": rewrites / len(active_rows)
            if active_rows
            else 0,
            "first_divergence_turn": distribution(first_turns) if first_turns else None,
        },
        "harvest_minus_b100": primary,
        "seed_mean_margin_delta": seed_distribution,
        "opponent_reports": opponent_reports,
        "nonnegative_opponents": nonnegative_opponents,
        "worst_opponent_mean_margin_delta": worst_opponent,
        "favorable_to_unfavorable_ratio": favorable_ratio,
        "b100_minus_resident": comparison(rows, "b100_resident"),
        "harvest_minus_resident": comparison(rows, "harvest_resident"),
        "gate_checks": checks,
        "gate_passed": all(checks.values()),
        "decision": (
            "write a separate prospective protocol; no fresh execution authorized"
            if all(checks.values())
            else "close the one-action harvest-on-contact residual without retuning"
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
