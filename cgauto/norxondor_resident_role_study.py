#!/usr/bin/env python3
"""Summarize funded resident-role counterfactuals under complete-policy gates."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import statistics

from cgauto.norxondor_research_rollout_study import atomic_write


INTEGER_FIELDS = (
    "seed",
    "seat",
    "decision_turn",
    "resident_margin",
    "policy_margin",
    "margin_delta",
    "resident_score",
    "policy_score",
    "score_delta",
    "resident_workers",
    "policy_workers",
    "scenario_elapsed_us",
)

OPTIONAL_INTEGER_FIELDS = (
    "resident_second_worker_turn",
    "policy_second_worker_turn",
    "resident_third_worker_turn",
    "policy_third_worker_turn",
)


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            for field in OPTIONAL_INTEGER_FIELDS:
                if field in row:
                    row[field] = int(row[field])
            rows.append(row)
    return rows


def _mean(rows: list[dict], field: str) -> float:
    return statistics.mean(row[field] for row in rows)


def _turn_summary(rows: list[dict], field: str) -> dict | None:
    if field not in rows[0]:
        return None
    successful = [row[field] for row in rows if row[field] >= 0]
    return {
        "observed_rate": len(successful) / len(rows),
        "mean": statistics.mean(successful) if successful else None,
        "median": statistics.median(successful) if successful else None,
        "minimum": min(successful) if successful else None,
        "maximum": max(successful) if successful else None,
    }


def summarize_policy(rows: list[dict]) -> dict:
    by_opponent = defaultdict(list)
    for row in rows:
        by_opponent[row["actual_opponent"]].append(row)
    opponent_reports = {
        opponent: {
            "scenarios": len(group),
            "margin_delta": _mean(group, "margin_delta"),
            "score_delta": _mean(group, "score_delta"),
            "policy_margin": _mean(group, "policy_margin"),
            "policy_score": _mean(group, "policy_score"),
        }
        for opponent, group in sorted(by_opponent.items())
    }
    margin_means = [report["margin_delta"] for report in opponent_reports.values()]
    nonnegative = sum(value >= 0 for value in margin_means)
    margin_delta = _mean(rows, "margin_delta")
    score_delta = _mean(rows, "score_delta")
    mean_workers = _mean(rows, "policy_workers")
    three_worker_rate = statistics.mean(row["policy_workers"] >= 3 for row in rows)
    worst_opponent = min(margin_means)
    gate_passed = bool(
        margin_delta >= 2
        and score_delta >= 2
        and mean_workers >= 2.5
        and nonnegative >= 5
        and worst_opponent >= -5
    )
    return {
        "scenarios": len(rows),
        "margin_delta": margin_delta,
        "score_delta": score_delta,
        "policy_margin": _mean(rows, "policy_margin"),
        "policy_score": _mean(rows, "policy_score"),
        "mean_workers": mean_workers,
        "three_worker_rate": three_worker_rate,
        "second_worker_turn": _turn_summary(rows, "policy_second_worker_turn"),
        "third_worker_turn": _turn_summary(rows, "policy_third_worker_turn"),
        "positive_cell_rate": statistics.mean(row["margin_delta"] > 0 for row in rows),
        "nonnegative_opponents": nonnegative,
        "worst_opponent_margin_delta": worst_opponent,
        "opponents": opponent_reports,
        "gate_passed": gate_passed,
    }


def _rank(item: tuple[str, dict]) -> tuple:
    name, report = item
    return (
        report["gate_passed"],
        report["worst_opponent_margin_delta"],
        report["nonnegative_opponents"],
        report["margin_delta"],
        report["score_delta"],
        name,
    )


def analyze(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("role sweep has no rows")
    keys = {
        (row["seed"], row["seat"], row["actual_opponent"], row["policy"])
        for row in rows
    }
    if len(keys) != len(rows):
        raise ValueError("role sweep contains duplicate scenario-policy rows")

    policies = defaultdict(list)
    scenario_grid = defaultdict(set)
    for row in rows:
        policies[row["policy"]].append(row)
        scenario_grid[row["policy"]].add(
            (row["seed"], row["seat"], row["actual_opponent"])
        )
    expected = next(iter(scenario_grid.values()))
    incomplete = [name for name, grid in scenario_grid.items() if grid != expected]
    if incomplete:
        raise ValueError(f"policies have different scenario grids: {sorted(incomplete)}")

    reports = {
        name: summarize_policy(group) for name, group in sorted(policies.items())
    }
    ranking = [name for name, _ in sorted(reports.items(), key=_rank, reverse=True)]
    eligible = [name for name in ranking if reports[name]["gate_passed"]]
    return {
        "schema": 1,
        "scope": (
            "turn-three resident-prefix research policies evaluated by exact terminal outcomes "
            "on consumed discovery seeds"
        ),
        "rows": len(rows),
        "scenarios": len(expected),
        "seeds": sorted({row["seed"] for row in rows}),
        "opponents": sorted({row["actual_opponent"] for row in rows}),
        "policy_count": len(reports),
        "gate": {
            "minimum_margin_delta": 2,
            "minimum_score_delta": 2,
            "minimum_mean_workers": 2.5,
            "minimum_nonnegative_opponents": 5,
            "minimum_worst_opponent_margin_delta": -5,
        },
        "eligible_policies": eligible,
        "ranking": ranking,
        "policies": reports,
        "decision": {
            "expand_discovery": bool(eligible),
            "build_submission_candidate": False,
            "reason": (
                "one or more smoke policies clear every discovery gate"
                if eligible
                else "no post-funding role policy clears the worst-opponent gate"
            ),
        },
    }


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
