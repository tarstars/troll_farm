#!/usr/bin/env python3
"""Precision-first forest distillation of the shared-state terminal rollout teacher."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import random

from cgauto.norxondor_research_rollout_study import atomic_write
from cgauto.norxondor_shared_state_distillation import (
    actual_evaluation,
    feature_rows,
    key,
    teacher_choice,
)
from cgauto.norxondor_shared_state_selector_study import read_rows, scenarios
from cgauto.rollout_selector_distillation import confusion, weighted_gini


MODEL_FEATURE_PREFIXES = ("compatible_", "mismatch_")
MODEL_SUMMARY_FEATURES = {
    "compatible_count",
    "minimum_mismatch",
    "second_mismatch",
    "mismatch_gap",
}


def deployable_feature_rows(groups: list[list[dict]]) -> dict[tuple, dict[str, float]]:
    rows = feature_rows(groups)
    return {
        item: {
            name: value
            for name, value in features.items()
            if name not in MODEL_SUMMARY_FEATURES
            and not name.startswith(MODEL_FEATURE_PREFIXES)
        }
        for item, features in rows.items()
    }


def candidate_thresholds(values: list[float], rng: random.Random) -> list[float]:
    unique = sorted(set(values))
    if len(unique) < 2:
        return []
    indexes = list(range(len(unique) - 1))
    if len(indexes) > 8:
        indexes = sorted(rng.sample(indexes, 8))
    return [(unique[index] + unique[index + 1]) / 2 for index in indexes]


def fit_extra_tree(
    keys: list[tuple],
    features: dict[tuple, dict[str, float]],
    labels: dict[tuple, bool],
    rng: random.Random,
    *,
    max_depth: int,
    min_leaf: int,
    negative_weight: float,
    max_features: int,
    depth: int = 0,
) -> dict:
    positive = sum(labels[item] for item in keys)
    negative = len(keys) - positive
    leaf = {
        "feature": None,
        "prediction": positive > negative_weight * negative,
        "positive": positive,
        "negative": negative,
    }
    if (
        depth >= max_depth
        or positive == 0
        or negative == 0
        or len(keys) < 2 * min_leaf
    ):
        return leaf
    names = sorted(next(iter(features.values())))
    sampled = rng.sample(names, min(max_features, len(names)))
    best = None
    for name in sampled:
        thresholds = candidate_thresholds([features[item][name] for item in keys], rng)
        for threshold in thresholds:
            left = [item for item in keys if features[item][name] <= threshold]
            if len(left) < min_leaf or len(keys) - len(left) < min_leaf:
                continue
            left_positive = sum(labels[item] for item in left)
            left_negative = len(left) - left_positive
            right_positive = positive - left_positive
            right_negative = negative - left_negative
            impurity = weighted_gini(
                left_positive, left_negative, negative_weight
            ) + weighted_gini(right_positive, right_negative, negative_weight)
            candidate = (impurity, name, threshold, left)
            if best is None or candidate[:3] < best[:3]:
                best = candidate
    if best is None:
        return leaf
    _, name, threshold, left = best
    left_counts = Counter(left)
    remaining = left_counts.copy()
    right = []
    for item in keys:
        if remaining[item]:
            remaining[item] -= 1
        else:
            right.append(item)
    return {
        "feature": name,
        "threshold": threshold,
        "positive": positive,
        "negative": negative,
        "left": fit_extra_tree(
            left,
            features,
            labels,
            rng,
            max_depth=max_depth,
            min_leaf=min_leaf,
            negative_weight=negative_weight,
            max_features=max_features,
            depth=depth + 1,
        ),
        "right": fit_extra_tree(
            right,
            features,
            labels,
            rng,
            max_depth=max_depth,
            min_leaf=min_leaf,
            negative_weight=negative_weight,
            max_features=max_features,
            depth=depth + 1,
        ),
    }


def seed_bootstrap(keys: list[tuple], rng: random.Random) -> list[tuple]:
    seeds = sorted({item[0] for item in keys})
    by_seed = {seed: [item for item in keys if item[0] == seed] for seed in seeds}
    sampled = [rng.choice(seeds) for _ in seeds]
    return [item for seed in sampled for item in by_seed[seed]]


def fit_forest(keys, features, labels, config, random_seed=6553250) -> list[dict]:
    rng = random.Random(random_seed)
    forest = []
    for _ in range(config["trees"]):
        forest.append(
            fit_extra_tree(
                seed_bootstrap(keys, rng),
                features,
                labels,
                rng,
                max_depth=config["max_depth"],
                min_leaf=config["min_leaf"],
                negative_weight=config["negative_weight"],
                max_features=config["max_features"],
            )
        )
    return forest


def tree_predict(tree: dict, row: dict[str, float]) -> bool:
    while tree["feature"] is not None:
        tree = tree["left"] if row[tree["feature"]] <= tree["threshold"] else tree["right"]
    return tree["prediction"]


def forest_score(forest: list[dict], row: dict[str, float]) -> float:
    return sum(tree_predict(tree, row) for tree in forest) / len(forest)


def blocked_scores(keys, features, labels, config) -> dict[tuple, float]:
    seeds = sorted({item[0] for item in keys})
    seed_fold = {seed: index % 5 for index, seed in enumerate(seeds)}
    scores = {}
    for fold in range(5):
        train = [item for item in keys if seed_fold[item[0]] != fold]
        held = [item for item in keys if seed_fold[item[0]] == fold]
        forest = fit_forest(train, features, labels, config, 6553250 + fold)
        scores.update({item: forest_score(forest, features[item]) for item in held})
    return scores


def node_count(tree: dict) -> int:
    if tree["feature"] is None:
        return 1
    return 1 + node_count(tree["left"]) + node_count(tree["right"])


def used_features(tree: dict) -> set[str]:
    if tree["feature"] is None:
        return set()
    return {tree["feature"]} | used_features(tree["left"]) | used_features(tree["right"])


def tree_expression(tree: dict) -> str:
    if tree["feature"] is None:
        return "1" if tree["prediction"] else "0"
    return (
        f"if f.{tree['feature']}<={tree['threshold']:.6g}"
        f"{{{tree_expression(tree['left'])}}}else{{{tree_expression(tree['right'])}}}"
    )


def forest_expression(forest: list[dict], threshold: float) -> str:
    needed = math.floor(threshold * len(forest)) + 1
    return "+".join(f"({tree_expression(tree)})" for tree in forest) + f">={needed}"


def choose_config(keys, features, labels) -> tuple[dict | None, list[dict]]:
    reports = []
    base_configs = [
        {
            "trees": trees,
            "max_depth": depth,
            "min_leaf": min_leaf,
            "negative_weight": negative_weight,
            "max_features": max_features,
        }
        for trees in (16, 32)
        for depth in (4, 5, 6)
        for min_leaf in (4, 8)
        for negative_weight in (1.0, 2.0, 4.0)
        for max_features in (12, 24)
    ]
    minimum_true_positives = max(1, round(0.05 * len(keys)))
    for config in base_configs:
        scores = blocked_scores(keys, features, labels, config)
        for threshold in (0.5, 0.6, 0.7, 0.8, 0.9):
            predictions = {item: scores[item] >= threshold for item in keys}
            report = confusion(labels, predictions)
            reports.append(
                {
                    "config": {**config, "vote_threshold": threshold},
                    "cross_validation": report,
                    "eligible": report["precision"] >= 0.90
                    and report["true_positive"] >= minimum_true_positives,
                }
            )
    reports.sort(
        key=lambda report: (
            report["eligible"],
            report["cross_validation"]["recall"],
            report["cross_validation"]["f0_5"],
            report["cross_validation"]["precision"],
            -report["config"]["trees"],
            -report["config"]["max_depth"],
        ),
        reverse=True,
    )
    return (reports[0]["config"] if reports[0]["eligible"] else None), reports


def analyze(rows: list[dict]) -> dict:
    groups = [group for group in scenarios(rows) if group[0]["decision_turn"] == 3]
    keys = [key(group) for group in groups]
    features = deployable_feature_rows(groups)
    labels = {key(group): teacher_choice(group) for group in groups}
    config, reports = choose_config(keys, features, labels)
    if config:
        forest_config = {name: value for name, value in config.items() if name != "vote_threshold"}
        forest = fit_forest(keys, features, labels, forest_config)
        predictions = {
            item: forest_score(forest, features[item]) >= config["vote_threshold"]
            for item in keys
        }
        expression = forest_expression(forest, config["vote_threshold"])
        nodes = sum(node_count(tree) for tree in forest)
        used = sorted(set().union(*(used_features(tree) for tree in forest)))
        actual = actual_evaluation(groups, predictions)
    else:
        forest = None
        predictions = None
        expression = None
        nodes = None
        used = []
        actual = None
    return {
        "schema": 1,
        "scope": (
            "fivefold blocked-seed precision-first ExtraTrees-style distillation of the frozen "
            "turn-three terminal teacher; excludes model compatibility/mismatch features so an "
            "eventual implementation needs only map and directly observed opponent stats"
        ),
        "cells": len(keys),
        "seeds": len({item[0] for item in keys}),
        "positive_teacher_cells": sum(labels.values()),
        "feature_count": len(next(iter(features.values()))),
        "selected_config": config,
        "selected_cross_validation": reports[0]["cross_validation"] if config else None,
        "eligible_configurations": sum(report["eligible"] for report in reports),
        "top_configurations": reports[:20],
        "forest": forest,
        "node_count": nodes,
        "used_features": used,
        "rust_expression": expression,
        "estimated_expression_bytes": len(expression) if expression else None,
        "training_actual": actual,
        "research_gate": {
            "requirements": [
                "blocked-seed precision at least 90%",
                "blocked-seed true positives at least 5% of cells",
                "features exclude embedded opponent models and terminal outcomes",
            ],
            "passed": config is not None,
        },
        "decision": {
            "authorize_new_validation_block": config is not None,
            "build_online_prototype": False,
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = [row for path in args.input for row in read_rows(path)]
    payload = analyze(rows)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        key: payload[key]
        for key in (
            "cells",
            "positive_teacher_cells",
            "feature_count",
            "selected_config",
            "selected_cross_validation",
            "eligible_configurations",
            "node_count",
            "used_features",
            "estimated_expression_bytes",
            "training_actual",
            "research_gate",
            "decision",
        )
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
