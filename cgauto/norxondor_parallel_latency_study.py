#!/usr/bin/env python3
"""Summarize the inner-parallel latency of the frozen 240-turn macro selector."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import statistics

from cgauto.norxondor_research_rollout_study import atomic_write


INTEGER_FIELDS = (
    "seed",
    "seat",
    "decision_turn",
    "compatible_count",
    "maximum_exact_prefix_transitions",
    "compatibility_us",
    "parallel_rollout_us",
    "total_prediction_us",
    "branch_elapsed_sum_us",
    "slowest_branch_us",
    "selected",
)


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            row["predicted_liquid_delta"] = float(row["predicted_liquid_delta"])
            rows.append(row)
    return rows


def percentile(values: list[int], probability: float) -> int:
    if not values:
        raise ValueError("latency sample is empty")
    if not 0 < probability <= 1:
        raise ValueError("probability must be in (0, 1]")
    ordered = sorted(values)
    return ordered[math.ceil(probability * len(ordered)) - 1]


def latency_summary(values: list[int]) -> dict:
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "p95": percentile(values, 0.95),
        "minimum": min(values),
        "maximum": max(values),
    }


def analyze(rows: list[dict], budget_us: int = 50_000) -> dict:
    if not rows:
        raise ValueError("profile has no rows")
    keys = {(row["seed"], row["seat"], row["actual_opponent"]) for row in rows}
    if len(keys) != len(rows):
        raise ValueError("profile contains duplicate scenarios")
    total = [row["total_prediction_us"] for row in rows]
    compatible_counts = sorted({row["compatible_count"] for row in rows})
    by_compatible_count = {
        str(count): latency_summary(
            [
                row["total_prediction_us"]
                for row in rows
                if row["compatible_count"] == count
            ]
        )
        for count in compatible_counts
    }
    speedups = [
        row["branch_elapsed_sum_us"] / row["parallel_rollout_us"]
        for row in rows
    ]
    total_summary = latency_summary(total)
    within_budget = sum(value <= budget_us for value in total)
    return {
        "schema": 1,
        "scope": (
            "naive inner-parallel execution of both frozen 240-turn branches for every maximum-"
            "exact-prefix-compatible opponent model; consumed discovery seeds only"
        ),
        "scenarios": len(rows),
        "seed_range": [min(row["seed"] for row in rows), max(row["seed"] for row in rows)],
        "decision_turn": sorted({row["decision_turn"] for row in rows}),
        "compatible_model_count": latency_summary(
            [row["compatible_count"] for row in rows]
        ),
        "compatibility_us": latency_summary([row["compatibility_us"] for row in rows]),
        "parallel_rollout_us": latency_summary(
            [row["parallel_rollout_us"] for row in rows]
        ),
        "total_prediction_us": total_summary,
        "branch_elapsed_sum_us": latency_summary(
            [row["branch_elapsed_sum_us"] for row in rows]
        ),
        "slowest_branch_us": latency_summary(
            [row["slowest_branch_us"] for row in rows]
        ),
        "parallel_speedup": {
            "mean": statistics.mean(speedups),
            "median": statistics.median(speedups),
        },
        "total_prediction_by_compatible_count": by_compatible_count,
        "selected_scenarios": sum(row["selected"] for row in rows),
        "latency_gate": {
            "budget_us": budget_us,
            "within_budget": within_budget,
            "within_budget_rate": within_budget / len(rows),
            "p95_us": total_summary["p95"],
            "passed": total_summary["p95"] <= budget_us,
        },
        "decision": {
            "build_online_rollout_selector": False,
            "reason": "p95 inner-parallel prediction time exceeds the 50 ms turn budget",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--budget-us", type=int, default=50_000)
    args = parser.parse_args()
    payload = analyze(read_rows(args.input), args.budget_us)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
