#!/usr/bin/env python3
"""Select a resident/worker-three branch from shared-state opponent-model rollouts."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
from pathlib import Path
import statistics

from cgauto.norxondor_research_rollout_study import atomic_write, summary


INTEGER_FIELDS = (
    "seed",
    "seat",
    "decision_turn",
    "root_opponent_workers",
    "root_opponent_ms",
    "root_opponent_cc",
    "root_opponent_hp",
    "root_opponent_chop",
    "prefix_mismatch",
    "exact_prefix_transitions",
    "prefix_transitions",
    "resident_margin",
    "three_worker_margin",
    "margin_delta",
    "resident_score",
    "three_worker_score",
    "score_delta",
    "resident_workers",
    "three_worker_workers",
    "serial_prediction_us",
)


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def scenario_key(row: dict) -> tuple:
    return (
        row["seed"],
        row["seat"],
        row["decision_turn"],
        row["actual_opponent"],
    )


def scenarios(rows: list[dict]) -> list[list[dict]]:
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[scenario_key(row)].append(row)
    result = []
    for key, group in sorted(grouped.items()):
        models = {row["model"] for row in group}
        if len(group) != len(models) or not any(
            row["model"] == row["actual_opponent"] for row in group
        ):
            raise ValueError(f"incomplete or duplicate model grid for {key}")
        result.append(group)
    return result


def compatible(group: list[dict], method: str) -> list[dict]:
    if method == "all":
        return group
    if method == "max_exact":
        maximum = max(row["exact_prefix_transitions"] for row in group)
        return [row for row in group if row["exact_prefix_transitions"] == maximum]
    if method.startswith("band"):
        band = int(method.removeprefix("band"))
        minimum = min(row["prefix_mismatch"] for row in group)
        return [row for row in group if row["prefix_mismatch"] <= minimum + band]
    raise ValueError(f"unknown conditioning method {method!r}")


def aggregate(values: list[int], method: str) -> float:
    ordered = sorted(values)
    if method == "mean":
        return statistics.mean(ordered)
    if method == "median":
        return statistics.median(ordered)
    if method == "minimum":
        return ordered[0]
    if method == "lower_quartile":
        return ordered[(len(ordered) - 1) // 4]
    raise ValueError(f"unknown aggregate {method!r}")


def config_label(config: dict) -> str:
    return (
        f"t{config['decision_turn']}-{config['conditioning']}-"
        f"{config['metric']}-{config['aggregate']}-b{config['buffer']}"
    )


def evaluate(groups: list[list[dict]], config: dict) -> dict:
    selected_groups = [
        group for group in groups if group[0]["decision_turn"] == config["decision_turn"]
    ]
    if not selected_groups:
        raise ValueError(f"decision turn {config['decision_turn']} is absent")
    chosen_deltas = []
    chosen_score_deltas = []
    chosen_margins = []
    chosen_scores = []
    compatible_counts = []
    actual_in_compatible = 0
    selected_alternative = 0
    selected_positive = 0
    selected_negative = 0
    correct = 0
    by_opponent: dict[str, list[int]] = defaultdict(list)
    by_opponent_score: dict[str, list[int]] = defaultdict(list)
    serial_us = []
    for group in selected_groups:
        truth = next(row for row in group if row["model"] == row["actual_opponent"])
        candidates = compatible(group, config["conditioning"])
        compatible_counts.append(len(candidates))
        actual_in_compatible += int(
            any(row["model"] == truth["actual_opponent"] for row in candidates)
        )
        predicted = aggregate(
            [row[config["metric"]] for row in candidates], config["aggregate"]
        )
        use_alternative = predicted > config["buffer"]
        truth_positive = truth["margin_delta"] > 0
        correct += int(use_alternative == truth_positive)
        delta = truth["margin_delta"] if use_alternative else 0
        score_delta = truth["score_delta"] if use_alternative else 0
        chosen_deltas.append(delta)
        chosen_score_deltas.append(score_delta)
        chosen_margins.append(truth["resident_margin"] + delta)
        chosen_scores.append(truth["resident_score"] + score_delta)
        by_opponent[truth["actual_opponent"]].append(delta)
        by_opponent_score[truth["actual_opponent"]].append(score_delta)
        selected_alternative += int(use_alternative)
        selected_positive += int(use_alternative and truth["margin_delta"] > 0)
        selected_negative += int(use_alternative and truth["margin_delta"] < 0)
        serial_us.append(truth["serial_prediction_us"])

    opponent_deltas = {
        opponent: statistics.mean(values)
        for opponent, values in sorted(by_opponent.items())
    }
    opponent_score_deltas = {
        opponent: statistics.mean(values)
        for opponent, values in sorted(by_opponent_score.items())
    }
    cells = len(selected_groups)
    result = {
        "config": config,
        "label": config_label(config),
        "cells": cells,
        "selected_alternative": selected_alternative,
        "selection_rate": selected_alternative / cells,
        "selected_positive": selected_positive,
        "selected_negative": selected_negative,
        "selection_precision": (
            selected_positive / selected_alternative if selected_alternative else 1.0
        ),
        "oracle_classification_accuracy": correct / cells,
        "margin_delta_vs_resident": summary(chosen_deltas),
        "score_delta_vs_resident": summary(chosen_score_deltas),
        "selected_margin": summary(chosen_margins),
        "selected_score": summary(chosen_scores),
        "opponent_mean_margin_deltas": opponent_deltas,
        "opponent_mean_score_deltas": opponent_score_deltas,
        "nonnegative_opponent_margin_deltas": sum(
            value >= 0 for value in opponent_deltas.values()
        ),
        "worst_opponent_mean_margin_delta": min(opponent_deltas.values()),
        "mean_compatible_models": statistics.mean(compatible_counts),
        "actual_model_compatible_rate": actual_in_compatible / cells,
        "serial_prediction_us": summary(serial_us),
    }
    result["gate_passed"] = (
        result["selection_rate"] >= 0.05
        and result["margin_delta_vs_resident"]["mean"] >= 2
        and result["score_delta_vs_resident"]["mean"] >= 2
        and result["nonnegative_opponent_margin_deltas"] >= 5
        and result["worst_opponent_mean_margin_delta"] >= -5
    )
    return result


def baseline(groups: list[list[dict]], decision_turn: int, always_alternative: bool) -> dict:
    chosen = []
    score = []
    by_opponent: dict[str, list[int]] = defaultdict(list)
    for group in groups:
        if group[0]["decision_turn"] != decision_turn:
            continue
        truth = next(row for row in group if row["model"] == row["actual_opponent"])
        if always_alternative:
            delta = truth["margin_delta"]
            score_delta = truth["score_delta"]
        else:
            delta = max(0, truth["margin_delta"])
            score_delta = truth["score_delta"] if truth["margin_delta"] > 0 else 0
        chosen.append(delta)
        score.append(score_delta)
        by_opponent[truth["actual_opponent"]].append(delta)
    return {
        "margin_delta": summary(chosen),
        "score_delta": summary(score),
        "opponent_mean_margin_deltas": {
            opponent: statistics.mean(values)
            for opponent, values in sorted(by_opponent.items())
        },
    }


def configurations(decision_turns: list[int]) -> list[dict]:
    return [
        {
            "decision_turn": turn,
            "conditioning": conditioning,
            "metric": metric,
            "aggregate": aggregation,
            "buffer": buffer,
        }
        for turn in decision_turns
        for conditioning in ("all", "max_exact", "band0", "band250", "band1000")
        for metric in ("margin_delta", "score_delta")
        for aggregation in ("mean", "median", "lower_quartile", "minimum")
        for buffer in (0, 5, 10, 20)
    ]


def analyze(rows: list[dict], frozen_config: dict | None = None) -> dict:
    groups = scenarios(rows)
    turns = sorted({group[0]["decision_turn"] for group in groups})
    models = sorted({row["model"] for row in rows})
    if frozen_config is None:
        reports = [evaluate(groups, config) for config in configurations(turns)]
        passing = [report for report in reports if report["gate_passed"]]
        selected = (
            max(
                passing,
                key=lambda report: (
                    report["worst_opponent_mean_margin_delta"],
                    report["margin_delta_vs_resident"]["mean"],
                    report["score_delta_vs_resident"]["mean"],
                    -report["selection_rate"],
                    report["label"],
                ),
            )
            if passing
            else None
        )
        top = sorted(
            reports,
            key=lambda report: (
                report["gate_passed"],
                report["worst_opponent_mean_margin_delta"],
                report["margin_delta_vs_resident"]["mean"],
            ),
            reverse=True,
        )[:20]
        mode = "discovery"
    else:
        selected = evaluate(groups, frozen_config)
        reports = [selected]
        top = [selected]
        mode = "validation"

    return {
        "schema": 1,
        "mode": mode,
        "scope": (
            "exact-engine generated-map shared-resident-prefix study; actual opponent labels are "
            "used only for evaluation, while selector conditioning uses replayed observable state "
            "transition mismatch and complete terminal macro-option rollouts"
        ),
        "rows": len(rows),
        "scenarios": len(groups),
        "seeds": len({row["seed"] for row in rows}),
        "decision_turns": turns,
        "models": models,
        "baselines": {
            str(turn): {
                "always_three_worker": baseline(groups, turn, True),
                "cell_oracle": baseline(groups, turn, False),
            }
            for turn in turns
        },
        "research_gate": {
            "requirements": [
                "alternative selected in at least 5% of cells",
                "mean paired margin and score gains at least 2",
                "at least five of eight opponent mean margin deltas nonnegative",
                "worst opponent mean margin delta at least -5",
            ],
            "passing_configurations": sum(report["gate_passed"] for report in reports),
            "passed": selected is not None and selected["gate_passed"],
        },
        "selected": selected,
        "top_configurations": top,
        "decision": {
            "freeze_for_validation": mode == "discovery" and selected is not None,
            "build_online_prototype": False,
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frozen-study", type=Path)
    args = parser.parse_args()
    frozen = None
    if args.frozen_study:
        frozen_payload = json.loads(args.frozen_study.read_text())
        frozen = frozen_payload["selected"]["config"]
    payload = analyze(read_rows(args.input), frozen)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "mode": payload["mode"],
        "scenarios": payload["scenarios"],
        "baselines": {
            turn: {
                "always_three": report["always_three_worker"]["margin_delta"]["mean"],
                "oracle": report["cell_oracle"]["margin_delta"]["mean"],
            }
            for turn, report in payload["baselines"].items()
        },
        "gate": payload["research_gate"],
        "selected": (
            {
                "label": payload["selected"]["label"],
                "selection_rate": payload["selected"]["selection_rate"],
                "margin_gain": payload["selected"]["margin_delta_vs_resident"]["mean"],
                "score_gain": payload["selected"]["score_delta_vs_resident"]["mean"],
                "worst_opponent": payload["selected"][
                    "worst_opponent_mean_margin_delta"
                ],
                "opponent_deltas": payload["selected"][
                    "opponent_mean_margin_deltas"
                ],
            }
            if payload["selected"]
            else None
        ),
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
