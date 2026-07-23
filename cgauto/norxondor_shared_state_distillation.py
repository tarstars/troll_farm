#!/usr/bin/env python3
"""Distill the validated turn-three Monte Carlo macro selector into cheap features."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics

from cgauto.norxondor_shared_state_selector_study import read_rows, scenarios
from cgauto.rollout_selector_distillation import (
    confusion,
    fit_tree,
    leaf_count,
    predict,
    rust_expression,
    turn_one_features,
)
from cgauto.norxondor_research_rollout_study import atomic_write, summary
from sim.mapgen import generate_bronze


MODEL_NAMES = (
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
)


def key(group: list[dict]) -> tuple[int, int, str]:
    row = group[0]
    return row["seed"], row["seat"], row["actual_opponent"]


def teacher_choice(group: list[dict]) -> bool:
    maximum = max(row["exact_prefix_transitions"] for row in group)
    return (
        min(
            row["margin_delta"]
            for row in group
            if row["exact_prefix_transitions"] == maximum
        )
        > 0
    )


def feature_rows(groups: list[list[dict]]) -> dict[tuple, dict[str, float]]:
    initial_cache = {}
    result = {}
    for group in groups:
        row = group[0]
        cache_key = (row["seed"], row["seat"])
        if cache_key not in initial_cache:
            initial_cache[cache_key] = turn_one_features(
                generate_bronze(row["seed"]), row["seat"]
            )
        features = dict(initial_cache[cache_key])
        maximum = max(item["exact_prefix_transitions"] for item in group)
        mismatches = sorted(item["prefix_mismatch"] for item in group)
        features.update(
            {
                "root_opponent_workers": row["root_opponent_workers"],
                "root_opponent_ms": row["root_opponent_ms"],
                "root_opponent_cc": row["root_opponent_cc"],
                "root_opponent_hp": row["root_opponent_hp"],
                "root_opponent_chop": row["root_opponent_chop"],
                "compatible_count": sum(
                    item["exact_prefix_transitions"] == maximum for item in group
                ),
                "minimum_mismatch": mismatches[0],
                "second_mismatch": mismatches[1],
                "mismatch_gap": mismatches[1] - mismatches[0],
            }
        )
        by_model = {item["model"]: item for item in group}
        for model in MODEL_NAMES:
            item = by_model[model]
            features[f"compatible_{model}"] = int(
                item["exact_prefix_transitions"] == maximum
            )
            features[f"mismatch_{model}"] = item["prefix_mismatch"]
        result[key(group)] = features
    return result


def blocked_cross_validation(keys, features, labels, config) -> dict:
    predictions = {}
    seeds = sorted({item[0] for item in keys})
    seed_fold = {seed: index % 5 for index, seed in enumerate(seeds)}
    for fold in range(5):
        train = [item for item in keys if seed_fold[item[0]] != fold]
        held = [item for item in keys if seed_fold[item[0]] == fold]
        tree = fit_tree(train, features, labels, **config)
        predictions.update({item: predict(tree, features[item]) for item in held})
    return confusion(labels, predictions)


def choose_config(keys, features, labels) -> tuple[dict, list[dict]]:
    reports = []
    for max_depth in (3, 4, 5):
        for min_leaf in (8, 16):
            for negative_weight in (8.0, 12.0, 16.0, 24.0, 32.0):
                for min_positive_leaf in (2, 4):
                    config = {
                        "max_depth": max_depth,
                        "min_leaf": min_leaf,
                        "negative_weight": negative_weight,
                        "min_positive_leaf": min_positive_leaf,
                    }
                    report = blocked_cross_validation(keys, features, labels, config)
                    reports.append({"config": config, "cross_validation": report})
    minimum_true_positives = max(1, round(0.05 * len(keys)))
    reports.sort(
        key=lambda report: (
            report["cross_validation"]["precision"] >= 0.90
            and report["cross_validation"]["true_positive"] >= minimum_true_positives,
            report["cross_validation"]["recall"],
            report["cross_validation"]["f0_5"],
            report["cross_validation"]["precision"],
            -report["config"]["max_depth"],
            report["config"]["min_leaf"],
            report["config"]["negative_weight"],
        ),
        reverse=True,
    )
    return reports[0]["config"], reports


def actual_evaluation(
    groups: list[list[dict]], predictions: dict[tuple, bool]
) -> dict:
    deltas = []
    score_deltas = []
    by_opponent: dict[str, list[int]] = defaultdict(list)
    selected_positive = 0
    selected_negative = 0
    for group in groups:
        scenario = key(group)
        truth = next(row for row in group if row["model"] == row["actual_opponent"])
        selected = predictions[scenario]
        delta = truth["margin_delta"] if selected else 0
        score_delta = truth["score_delta"] if selected else 0
        deltas.append(delta)
        score_deltas.append(score_delta)
        by_opponent[truth["actual_opponent"]].append(delta)
        selected_positive += int(selected and delta > 0)
        selected_negative += int(selected and delta < 0)
    opponent_deltas = {
        opponent: statistics.mean(values)
        for opponent, values in sorted(by_opponent.items())
    }
    report = {
        "cells": len(groups),
        "selected_cells": sum(predictions.values()),
        "selection_rate": sum(predictions.values()) / len(groups),
        "selected_positive": selected_positive,
        "selected_negative": selected_negative,
        "selection_precision": (
            selected_positive / sum(predictions.values())
            if sum(predictions.values())
            else 1.0
        ),
        "margin_delta_vs_resident": summary(deltas),
        "score_delta_vs_resident": summary(score_deltas),
        "opponent_mean_margin_deltas": opponent_deltas,
        "nonnegative_opponents": sum(value >= 0 for value in opponent_deltas.values()),
        "worst_opponent_mean_margin_delta": min(opponent_deltas.values()),
    }
    report["gate_passed"] = (
        report["selection_rate"] >= 0.05
        and report["margin_delta_vs_resident"]["mean"] >= 2
        and report["score_delta_vs_resident"]["mean"] >= 2
        and report["nonnegative_opponents"] >= 5
        and report["worst_opponent_mean_margin_delta"] >= -5
    )
    return report


def analyze(train_rows: list[dict], test_rows: list[dict]) -> dict:
    train_groups = [group for group in scenarios(train_rows) if group[0]["decision_turn"] == 3]
    test_groups = [group for group in scenarios(test_rows) if group[0]["decision_turn"] == 3]
    train_keys = [key(group) for group in train_groups]
    test_keys = [key(group) for group in test_groups]
    if {item[0] for item in train_keys} & {item[0] for item in test_keys}:
        raise ValueError("training and test seeds overlap")
    features = feature_rows(train_groups + test_groups)
    train_labels = {key(group): teacher_choice(group) for group in train_groups}
    test_labels = {key(group): teacher_choice(group) for group in test_groups}
    config, config_reports = choose_config(train_keys, features, train_labels)
    tree = fit_tree(train_keys, features, train_labels, **config)
    train_predictions = {item: predict(tree, features[item]) for item in train_keys}
    test_predictions = {item: predict(tree, features[item]) for item in test_keys}
    train_teacher = {item: train_labels[item] for item in train_keys}
    test_teacher = {item: test_labels[item] for item in test_keys}
    direct_test = actual_evaluation(test_groups, test_teacher)
    distilled_test = actual_evaluation(test_groups, test_predictions)
    return {
        "schema": 1,
        "scope": (
            "blocked-seed-CV distillation of the frozen turn-three exact-compatible minimax "
            "terminal-rollout teacher; features contain initial map geometry and observable prefix "
            "transition compatibility, never actual opponent identity or terminal outcome"
        ),
        "training_seeds": sorted({item[0] for item in train_keys}),
        "test_seeds": sorted({item[0] for item in test_keys}),
        "training_cells": len(train_keys),
        "test_cells": len(test_keys),
        "feature_count": len(next(iter(features.values()))),
        "selected_config": config,
        "selected_config_cross_validation": config_reports[0]["cross_validation"],
        "config_reports": config_reports,
        "tree": tree,
        "leaf_count": leaf_count(tree),
        "rust_expression": rust_expression(tree),
        "training_imitation": confusion(train_teacher, train_predictions),
        "test_imitation": confusion(test_teacher, test_predictions),
        "training_actual_distilled": actual_evaluation(train_groups, train_predictions),
        "test_actual_distilled": distilled_test,
        "test_actual_direct_teacher": direct_test,
        "research_gate": {
            "requirements": [
                "test distilled complete-policy gate passes unchanged",
                "test imitation precision at least 90%",
                "distilled mean margin retains at least 25% of direct teacher gain",
            ],
            "passed": (
                distilled_test["gate_passed"]
                and confusion(test_teacher, test_predictions)["precision"] >= 0.90
                and distilled_test["margin_delta_vs_resident"]["mean"]
                >= 0.25 * direct_test["margin_delta_vs_resident"]["mean"]
            ),
        },
        "decision": {
            "build_online_distilled_prototype": False,
            "reason": (
                "Set true only after the frozen test gate passes; this report does not alter the "
                "resident or authorize candidate packaging."
            ),
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, required=True, action="append")
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    train_rows = [row for path in args.train for row in read_rows(path)]
    payload = analyze(train_rows, read_rows(args.test))
    payload["decision"]["build_online_distilled_prototype"] = payload["research_gate"][
        "passed"
    ]
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        "cells": [payload["training_cells"], payload["test_cells"]],
        "features": payload["feature_count"],
        "config": payload["selected_config"],
        "cross_validation": payload["selected_config_cross_validation"],
        "leaves": payload["leaf_count"],
        "expression": payload["rust_expression"],
        "test_imitation": payload["test_imitation"],
        "test_distilled": payload["test_actual_distilled"],
        "test_teacher": payload["test_actual_direct_teacher"],
        "gate": payload["research_gate"],
        "decision": payload["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
