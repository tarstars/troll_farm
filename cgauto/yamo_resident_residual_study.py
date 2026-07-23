#!/usr/bin/env python3
"""Summarize the frozen resident-backed residual-search smoke screen."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import statistics

from cgauto.norxondor_research_rollout_study import atomic_write


def numeric(values: list[float]) -> dict:
    if not values:
        raise ValueError("numeric summary requires values")
    mean = statistics.fmean(values)
    deviation = statistics.stdev(values) if len(values) > 1 else 0.0
    return {
        "n": len(values),
        "mean": mean,
        "median": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
        "standard_deviation": deviation,
        "standard_error": deviation / math.sqrt(len(values)),
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
    }


def percentile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[round((len(ordered) - 1) * fraction)]


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {
        "seed",
        "seat",
        "opponent",
        "margin_delta",
        "score_delta",
        "searches",
        "accepted",
        "failed_targets",
        "decision_samples_us",
    }
    if not rows or not required.issubset(rows[0]):
        raise ValueError("invalid residual-search TSV schema")
    return rows


def event_audit(rows: list[dict]) -> dict | None:
    if "accepted_events" not in rows[0]:
        return None
    events = []
    for row in rows:
        for encoded in filter(None, row["accepted_events"].split(";")):
            fields = encoded.split(",")
            if len(fields) != 18:
                raise ValueError("invalid accepted-event encoding")
            events.append(
                {
                    "turn": int(fields[0]),
                    "stats": "/".join(fields[2:6]),
                    "target_kind": fields[12],
                    "predicted_robust_delta": min(float(fields[16]), float(fields[17])),
                    "scenario_margin_delta": float(row["margin_delta"]),
                    "scenario_score_delta": float(row["score_delta"]),
                    "scenario_event_count": int(row["accepted"]),
                }
            )
    classes = {}
    for target_kind in sorted({event["target_kind"] for event in events}):
        group = [event for event in events if event["target_kind"] == target_kind]
        singleton = [event for event in group if event["scenario_event_count"] == 1]
        classes[target_kind] = {
            "events": len(group),
            "median_turn": statistics.median(event["turn"] for event in group),
            "mean_predicted_robust_delta": statistics.fmean(
                event["predicted_robust_delta"] for event in group
            ),
            "mean_scenario_margin_delta": statistics.fmean(
                event["scenario_margin_delta"] for event in group
            ),
            "mean_scenario_score_delta": statistics.fmean(
                event["scenario_score_delta"] for event in group
            ),
            "singleton_scenarios": len(singleton),
            "singleton_margin_delta": numeric(
                [event["scenario_margin_delta"] for event in singleton]
            )
            if singleton
            else None,
            "singleton_score_delta": numeric(
                [event["scenario_score_delta"] for event in singleton]
            )
            if singleton
            else None,
        }
    return {"events": len(events), "target_classes": classes}


def analyze(rows: list[dict]) -> dict:
    margin = [float(row["margin_delta"]) for row in rows]
    score = [float(row["score_delta"]) for row in rows]
    samples = [
        int(sample)
        for row in rows
        for sample in row["decision_samples_us"].split(",")
        if sample
    ]
    if not samples:
        raise ValueError("no decision timing samples")
    opponents = sorted({row["opponent"] for row in rows})
    by_opponent = {}
    for opponent in opponents:
        group = [row for row in rows if row["opponent"] == opponent]
        by_opponent[opponent] = {
            "scenarios": len(group),
            "margin_delta": numeric([float(row["margin_delta"]) for row in group]),
            "score_delta": numeric([float(row["score_delta"]) for row in group]),
            "accepted": sum(int(row["accepted"]) for row in group),
        }
    opponent_margins = [
        report["margin_delta"]["mean"] for report in by_opponent.values()
    ]
    accepted = sum(int(row["accepted"]) for row in rows)
    profiles = sorted({row.get("profile", "unspecified") for row in rows})
    minimum_accepted = 20 if profiles == ["bank_only"] else 1
    active = [row for row in rows if int(row["accepted"]) > 0]
    timing = {
        "samples": len(samples),
        "mean_us": statistics.fmean(samples),
        "median_us": percentile(samples, 0.50),
        "p95_us": percentile(samples, 0.95),
        "p99_us": percentile(samples, 0.99),
        "maximum_us": max(samples),
        "over_50ms": sum(sample > 50_000 for sample in samples),
    }
    requirements = {
        f"accepted_deviations_at_least_{minimum_accepted}": accepted >= minimum_accepted,
        "mean_margin_at_least_2": statistics.fmean(margin) >= 2,
        "mean_score_at_least_2": statistics.fmean(score) >= 2,
        "five_nonnegative_opponents": sum(value >= 0 for value in opponent_margins) >= 5,
        "worst_opponent_at_least_minus_5": min(opponent_margins) >= -5,
        "p95_at_most_45ms": timing["p95_us"] <= 45_000,
        "no_decision_over_50ms": timing["maximum_us"] <= 50_000,
    }
    algorithmic_requirements = {
        key: value
        for key, value in requirements.items()
        if key not in {"p95_at_most_45ms", "no_decision_over_50ms"}
    }
    algorithmic_passed = all(algorithmic_requirements.values())
    passed = all(requirements.values())
    return {
        "schema": 1,
        "scope": (
            "research-only exact-engine Yamo/Orchard residual MOVE search on consumed "
            "discovery seeds; both seats and eight local opponents"
        ),
        "scenarios": len(rows),
        "seeds": sorted({int(row["seed"]) for row in rows}),
        "opponents": opponents,
        "profiles": profiles,
        "margin_delta": numeric(margin),
        "score_delta": numeric(score),
        "searches": sum(int(row["searches"]) for row in rows),
        "accepted": accepted,
        "failed_targets": sum(int(row["failed_targets"]) for row in rows),
        "active_scenarios": {
            "count": len(active),
            "margin_delta": numeric([float(row["margin_delta"]) for row in active])
            if active
            else None,
            "score_delta": numeric([float(row["score_delta"]) for row in active])
            if active
            else None,
        },
        "nonnegative_opponents": sum(value >= 0 for value in opponent_margins),
        "worst_opponent_margin_delta": min(opponent_margins),
        "by_opponent": by_opponent,
        "timing": timing,
        "accepted_event_audit": event_audit(rows),
        "algorithmic_gate": {
            "requirements": algorithmic_requirements,
            "passed": algorithmic_passed,
        },
        "research_gate": {"requirements": requirements, "passed": passed},
        "decision": {
            "direct_online_profile": passed,
            "own_state_distillation": algorithmic_passed and not passed,
            "build_submission_candidate": False,
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
