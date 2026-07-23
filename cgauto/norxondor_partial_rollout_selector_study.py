#!/usr/bin/env python3
"""Compare compatible-model partial rollouts with the frozen terminal branch teacher."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import statistics

from cgauto.norxondor_research_rollout_study import atomic_write, summary
from cgauto.norxondor_shared_state_selector_study import (
    read_rows as read_terminal_rows,
    scenarios as terminal_scenarios,
)


HORIZONS = (20, 40, 80, 120, 160, 200, 240)
BASE_INTEGER_FIELDS = (
    "seed",
    "seat",
    "decision_turn",
    "prefix_mismatch",
    "exact_prefix_transitions",
    "compatible_count",
    "serial_prediction_us",
)


def read_partial_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in BASE_INTEGER_FIELDS:
                row[field] = int(row[field])
            for horizon in HORIZONS:
                for prefix in (
                    "resident_margin",
                    "three_worker_margin",
                    "margin_delta",
                    "resident_liquid",
                    "three_worker_liquid",
                    "liquid_delta",
                ):
                    field = f"{prefix}_h{horizon}"
                    row[field] = int(row[field])
            rows.append(row)
    return rows


def scenario_key(row: dict) -> tuple:
    return row["seed"], row["seat"], row["actual_opponent"]


def partial_scenarios(rows: list[dict]) -> dict[tuple, list[dict]]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[scenario_key(row)].append(row)
    for key, group in grouped.items():
        if len(group) != group[0]["compatible_count"]:
            raise ValueError(f"partial compatible grid differs for {key}")
    return grouped


def terminal_truth(rows: list[dict]) -> dict[tuple, dict]:
    truth = {}
    for group in terminal_scenarios(rows):
        if group[0]["decision_turn"] != 3:
            continue
        row = next(item for item in group if item["model"] == item["actual_opponent"])
        truth[scenario_key(row)] = row
    return truth


def terminal_teacher_mean_gain(rows: list[dict]) -> float:
    deltas = []
    for group in terminal_scenarios(rows):
        if group[0]["decision_turn"] != 3:
            continue
        maximum = max(item["exact_prefix_transitions"] for item in group)
        select = (
            min(
                item["margin_delta"]
                for item in group
                if item["exact_prefix_transitions"] == maximum
            )
            > 0
        )
        truth = next(item for item in group if item["model"] == item["actual_opponent"])
        deltas.append(truth["margin_delta"] if select else 0)
    return statistics.mean(deltas)


def aggregate(values: list[int], method: str) -> float:
    ordered = sorted(values)
    if method == "minimum":
        return ordered[0]
    if method == "lower_quartile":
        return ordered[(len(ordered) - 1) // 4]
    if method == "median":
        return statistics.median(ordered)
    if method == "mean":
        return statistics.mean(ordered)
    raise ValueError(method)


def configs() -> list[dict]:
    return [
        {
            "horizon": horizon,
            "metric": metric,
            "aggregate": method,
            "buffer": buffer,
        }
        for horizon in HORIZONS
        for metric in ("margin_delta", "liquid_delta")
        for method in ("minimum", "lower_quartile", "median", "mean")
        for buffer in (0, 2, 5, 10, 20)
    ]


def label(config: dict) -> str:
    return (
        f"h{config['horizon']}-{config['metric']}-"
        f"{config['aggregate']}-b{config['buffer']}"
    )


def evaluate(
    partial: dict[tuple, list[dict]], truth: dict[tuple, dict], config: dict
) -> dict:
    if partial.keys() != truth.keys():
        raise ValueError("partial and terminal scenario keys differ")
    deltas = []
    score_deltas = []
    by_opponent: dict[str, list[int]] = defaultdict(list)
    selected = 0
    selected_positive = 0
    selected_negative = 0
    serial_times = []
    value_field = f"{config['metric']}_h{config['horizon']}"
    for key in sorted(partial):
        rows = partial[key]
        prediction = aggregate(
            [row[value_field] for row in rows], config["aggregate"]
        )
        use_alternative = prediction > config["buffer"]
        actual = truth[key]
        delta = actual["margin_delta"] if use_alternative else 0
        score_delta = actual["score_delta"] if use_alternative else 0
        deltas.append(delta)
        score_deltas.append(score_delta)
        by_opponent[actual["actual_opponent"]].append(delta)
        selected += int(use_alternative)
        selected_positive += int(use_alternative and delta > 0)
        selected_negative += int(use_alternative and delta < 0)
        serial_times.append(rows[0]["serial_prediction_us"])
    opponent_deltas = {
        opponent: statistics.mean(values)
        for opponent, values in sorted(by_opponent.items())
    }
    report = {
        "config": config,
        "label": label(config),
        "cells": len(truth),
        "selected_cells": selected,
        "selection_rate": selected / len(truth),
        "selected_positive": selected_positive,
        "selected_negative": selected_negative,
        "selection_precision": selected_positive / selected if selected else 1.0,
        "margin_delta_vs_resident": summary(deltas),
        "score_delta_vs_resident": summary(score_deltas),
        "opponent_mean_margin_deltas": opponent_deltas,
        "nonnegative_opponents": sum(value >= 0 for value in opponent_deltas.values()),
        "worst_opponent_mean_margin_delta": min(opponent_deltas.values()),
        "serial_prediction_us": summary(serial_times),
    }
    report["complete_policy_gate"] = (
        report["selection_rate"] >= 0.05
        and report["margin_delta_vs_resident"]["mean"] >= 2
        and report["score_delta_vs_resident"]["mean"] >= 2
        and report["nonnegative_opponents"] >= 5
        and report["worst_opponent_mean_margin_delta"] >= -5
    )
    report["partial_gate"] = (
        report["complete_policy_gate"] and report["selection_precision"] >= 0.90
    )
    return report


def analyze(
    partial_rows: list[dict], train_terminal_rows: list[dict], test_terminal_rows: list[dict]
) -> dict:
    partial = partial_scenarios(partial_rows)
    train_truth = terminal_truth(train_terminal_rows)
    test_truth = terminal_truth(test_terminal_rows)
    train_partial = {key: partial[key] for key in train_truth}
    test_partial = {key: partial[key] for key in test_truth}
    if set(train_truth) & set(test_truth):
        raise ValueError("terminal train/test overlap")
    reports = [evaluate(train_partial, train_truth, config) for config in configs()]
    passing = [report for report in reports if report["partial_gate"]]
    selected = (
        max(
            passing,
            key=lambda report: (
                report["worst_opponent_mean_margin_delta"],
                report["margin_delta_vs_resident"]["mean"],
                report["score_delta_vs_resident"]["mean"],
                report["selection_precision"],
                report["label"],
            ),
        )
        if passing
        else None
    )
    validation = (
        evaluate(test_partial, test_truth, selected["config"]) if selected else None
    )
    direct_teacher_gain = terminal_teacher_mean_gain(test_terminal_rows)
    retained_fraction = (
        validation["margin_delta_vs_resident"]["mean"] / direct_teacher_gain
        if validation
        else 0
    )
    return {
        "schema": 1,
        "scope": (
            "compatible-model partial exact-engine rollouts on already-consumed terminal-teacher "
            "cells; discovery seeds 302-311 select horizon/value/aggregate/buffer once and seeds "
            "312-321 evaluate it unchanged"
        ),
        "partial_rows": len(partial_rows),
        "training_cells": len(train_truth),
        "test_cells": len(test_truth),
        "configurations": len(reports),
        "passing_discovery_configurations": len(passing),
        "selected_discovery": selected,
        "validation": validation,
        "top_discovery": sorted(
            reports,
            key=lambda report: (
                report["partial_gate"],
                report["worst_opponent_mean_margin_delta"],
                report["margin_delta_vs_resident"]["mean"],
            ),
            reverse=True,
        )[:20],
        "terminal_teacher_reference": {
            "config": "turn 3 / maximum exact-prefix set / minimum terminal margin delta > 0",
            "validation_margin_gain": direct_teacher_gain,
        },
        "retained_terminal_teacher_fraction": retained_fraction,
        "research_gate": {
            "requirements": [
                "discovery partial gate passes",
                "unchanged validation partial gate passes",
                "validation retains at least 25% of terminal teacher mean margin gain",
            ],
            "passed": (
                selected is not None
                and validation is not None
                and validation["partial_gate"]
                and retained_fraction >= 0.25
            ),
        },
        "decision": {
            "profile_online_partial_selector": False,
            "build_online_prototype": False,
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--partial", type=Path, required=True)
    parser.add_argument("--train-terminal", type=Path, required=True)
    parser.add_argument("--test-terminal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = analyze(
        read_partial_rows(args.partial),
        read_terminal_rows(args.train_terminal),
        read_terminal_rows(args.test_terminal),
    )
    payload["decision"]["profile_online_partial_selector"] = payload["research_gate"][
        "passed"
    ]
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "cells": [payload["training_cells"], payload["test_cells"]],
        "passing": payload["passing_discovery_configurations"],
        "selected": payload["selected_discovery"],
        "validation": payload["validation"],
        "retained_fraction": payload["retained_terminal_teacher_fraction"],
        "gate": payload["research_gate"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
