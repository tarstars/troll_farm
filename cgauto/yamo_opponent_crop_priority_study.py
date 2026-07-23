#!/usr/bin/env python3
"""Evaluate the frozen Yamo opponent-crop priority experiment.

The Rust sweep emits one paired control/candidate row for every
seed/seat/opponent/profile cell.  This module applies the prospectively frozen
Phase 17 gates without inspecting or retuning individual seeds.
"""

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
    "bonus",
    "eta_limit",
    "start_turn",
    "minimum_seen",
    "control_margin",
    "candidate_margin",
    "margin_delta",
    "control_score",
    "candidate_score",
    "score_delta",
    "control_opponent_score",
    "candidate_opponent_score",
    "opponent_score_delta",
    "control_wood",
    "candidate_wood",
    "wood_delta",
    "control_opponent_wood",
    "candidate_opponent_wood",
    "opponent_wood_delta",
    "control_workers",
    "candidate_workers",
    "control_terminal_turn",
    "candidate_terminal_turn",
    "crops_seen",
    "crop_priority_selections",
    "first_crop_priority_turn",
    "crops_alive",
    "divergence_turns",
    "first_divergence_turn",
)

GATE = {
    "minimum_activated_cells": 48,
    "minimum_mean_margin_delta": 2,
    "strictly_positive_trimmed_5pct_mean_margin_delta": True,
    "minimum_mean_score_delta": -2,
    "maximum_mean_opponent_score_delta": -4,
    "minimum_nonnegative_opponents": 6,
    "minimum_worst_opponent_mean_margin_delta": -5,
}


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def trimmed_mean(values: list[int], fraction: float = 0.05) -> float:
    if not values:
        raise ValueError("cannot summarize an empty value list")
    ordered = sorted(values)
    trim = math.floor(fraction * len(ordered))
    kept = ordered[trim : len(ordered) - trim] if trim else ordered
    return statistics.mean(kept)


def distribution(values: list[int]) -> dict:
    if not values:
        raise ValueError("cannot summarize an empty value list")
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "trimmed_5pct_mean": trimmed_mean(values),
        "standard_deviation": statistics.stdev(values) if len(values) > 1 else 0,
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
        "minimum": min(values),
        "maximum": max(values),
    }


def _mean(rows: list[dict], field: str) -> float:
    return statistics.mean(row[field] for row in rows)


def summarize_profile(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("profile has no rows")
    parameter_fields = ("bonus", "eta_limit", "start_turn", "minimum_seen")
    parameters = {
        field: next(iter({row[field] for row in rows})) for field in parameter_fields
    }
    if any(len({row[field] for row in rows}) != 1 for field in parameter_fields):
        raise ValueError("profile parameters change within the scenario grid")

    by_opponent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_opponent[row["opponent"]].append(row)
    opponent_reports = {
        opponent: {
            "scenarios": len(group),
            "mean_margin_delta": _mean(group, "margin_delta"),
            "mean_score_delta": _mean(group, "score_delta"),
            "mean_opponent_score_delta": _mean(group, "opponent_score_delta"),
            "activated_cells": sum(row["divergence_turns"] > 0 for row in group),
        }
        for opponent, group in sorted(by_opponent.items())
    }
    opponent_margin_means = [
        report["mean_margin_delta"] for report in opponent_reports.values()
    ]
    margin = distribution([row["margin_delta"] for row in rows])
    activated_cells = sum(row["divergence_turns"] > 0 for row in rows)
    score_delta = _mean(rows, "score_delta")
    opponent_score_delta = _mean(rows, "opponent_score_delta")
    nonnegative_opponents = sum(value >= 0 for value in opponent_margin_means)
    worst_opponent = min(opponent_margin_means)
    checks = {
        "activated_cells": activated_cells >= GATE["minimum_activated_cells"],
        "mean_margin_delta": margin["mean"] >= GATE["minimum_mean_margin_delta"],
        "trimmed_margin_delta": margin["trimmed_5pct_mean"] > 0,
        "mean_score_delta": score_delta >= GATE["minimum_mean_score_delta"],
        "mean_opponent_score_delta": opponent_score_delta
        <= GATE["maximum_mean_opponent_score_delta"],
        "nonnegative_opponents": nonnegative_opponents
        >= GATE["minimum_nonnegative_opponents"],
        "worst_opponent": worst_opponent
        >= GATE["minimum_worst_opponent_mean_margin_delta"],
    }
    first_priority_turns = [
        row["first_crop_priority_turn"]
        for row in rows
        if row["first_crop_priority_turn"] >= 0
    ]
    first_divergence_turns = [
        row["first_divergence_turn"]
        for row in rows
        if row["first_divergence_turn"] >= 0
    ]
    return {
        "parameters": parameters,
        "scenarios": len(rows),
        "activated_cells": activated_cells,
        "activation_rate": activated_cells / len(rows),
        "margin_delta": margin,
        "mean_score_delta": score_delta,
        "mean_opponent_score_delta": opponent_score_delta,
        "mean_wood_delta": _mean(rows, "wood_delta"),
        "mean_opponent_wood_delta": _mean(rows, "opponent_wood_delta"),
        "mean_candidate_score": _mean(rows, "candidate_score"),
        "mean_candidate_opponent_score": _mean(rows, "candidate_opponent_score"),
        "mean_crops_seen": _mean(rows, "crops_seen"),
        "mean_crop_priority_selections": _mean(rows, "crop_priority_selections"),
        "first_crop_priority_turn": {
            "observations": len(first_priority_turns),
            "mean": statistics.mean(first_priority_turns)
            if first_priority_turns
            else None,
            "median": statistics.median(first_priority_turns)
            if first_priority_turns
            else None,
        },
        "first_divergence_turn": {
            "observations": len(first_divergence_turns),
            "mean": statistics.mean(first_divergence_turns)
            if first_divergence_turns
            else None,
            "median": statistics.median(first_divergence_turns)
            if first_divergence_turns
            else None,
        },
        "nonnegative_opponents": nonnegative_opponents,
        "worst_opponent_mean_margin_delta": worst_opponent,
        "opponents": opponent_reports,
        "gate_checks": checks,
        "gate_passed": all(checks.values()),
    }


def selection_key(item: tuple[str, dict]) -> tuple:
    """Prospective tiebreak: robustness, central effects, then weaker treatment."""

    label, report = item
    parameters = report["parameters"]
    return (
        report["worst_opponent_mean_margin_delta"],
        report["margin_delta"]["trimmed_5pct_mean"],
        report["margin_delta"]["mean"],
        report["mean_score_delta"],
        -parameters["bonus"],
        -parameters["eta_limit"],
        label,
    )


def analyze(rows: list[dict], phase: str = "discovery") -> dict:
    if not rows:
        raise ValueError("crop-priority sweep has no rows")
    identities = {
        (row["seed"], row["seat"], row["opponent"], row["profile"])
        for row in rows
    }
    if len(identities) != len(rows):
        raise ValueError("crop-priority sweep contains duplicate scenario-profile rows")

    grouped: dict[str, list[dict]] = defaultdict(list)
    grids: dict[str, set[tuple]] = defaultdict(set)
    controls: dict[tuple, set[tuple]] = defaultdict(set)
    for row in rows:
        scenario = (row["seed"], row["seat"], row["opponent"])
        grouped[row["profile"]].append(row)
        grids[row["profile"]].add(scenario)
        controls[scenario].add(
            (
                row["control_margin"],
                row["control_score"],
                row["control_opponent_score"],
                row["control_wood"],
                row["control_opponent_wood"],
                row["control_workers"],
                row["control_terminal_turn"],
            )
        )
    expected_grid = next(iter(grids.values()))
    incomplete = [label for label, grid in grids.items() if grid != expected_grid]
    if incomplete:
        raise ValueError(f"profiles have different scenario grids: {sorted(incomplete)}")
    inconsistent_controls = [scenario for scenario, values in controls.items() if len(values) != 1]
    if inconsistent_controls:
        raise ValueError("control outcome changes between profiles for a scenario")

    reports = {
        label: summarize_profile(group) for label, group in sorted(grouped.items())
    }
    ranked = sorted(reports.items(), key=selection_key, reverse=True)
    eligible = [label for label, report in ranked if report["gate_passed"]]
    selected = eligible[0] if eligible else None
    seeds = sorted({row["seed"] for row in rows})
    return {
        "schema": 1,
        "phase": phase,
        "scope": (
            "research-only provenance-aware priority for reachable opponent-created crops; "
            "paired against the unchanged resident on the same seed, seat, and opponent"
        ),
        "rows": len(rows),
        "scenarios": len(expected_grid),
        "seed_range": [min(seeds), max(seeds)],
        "seeds": seeds,
        "opponents": sorted({row["opponent"] for row in rows}),
        "profile_count": len(reports),
        "prospective_gate": GATE,
        "selection_order": [
            "worst opponent mean margin delta",
            "five-percent-trimmed mean margin delta",
            "raw mean margin delta",
            "mean own-score delta",
            "lower bonus",
            "lower ETA limit",
        ],
        "ranking": [label for label, _ in ranked],
        "eligible_profiles": eligible,
        "selected_profile": selected,
        "profiles": reports,
        "decision": {
            "run_unchanged_replication": phase == "discovery" and selected is not None,
            "research_gate_passed": selected is not None,
            "build_submission_candidate": False,
            "reason": (
                "the selected profile clears every frozen gate"
                if selected is not None
                else "no profile clears every frozen complete-policy gate"
            ),
        },
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
    parser.add_argument("--phase", choices=("discovery", "replication"), default="discovery")
    args = parser.parse_args()
    payload = analyze(read_rows(args.input), phase=args.phase)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
