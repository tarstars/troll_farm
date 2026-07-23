#!/usr/bin/env python3
"""Distill Norxondor's episode intent lookup into a compact categorical tree."""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import statistics

from cgauto.norxondor_intent_state_machine_study import episode_rows
from cgauto.norxondor_navigation_intent_study import extract_game
from cgauto.norxondor_research_rollout_study import atomic_write
from cgauto.top_policy_objective_study import classification_summary


FEATURE_SETS = {
    "core7": (
        "phase",
        "role",
        "carry_class",
        "full",
        "bank_distance",
        "on_cell",
        "previous_action",
    ),
    "role9": (
        "phase",
        "ordinal",
        "role",
        "carry_class",
        "full",
        "bank_distance",
        "on_cell",
        "unit_count",
        "previous_action",
    ),
    "all14": (
        "phase",
        "ordinal",
        "role",
        "carry_class",
        "full",
        "bank_distance",
        "on_cell",
        "unit_count",
        "score_bucket",
        "nearest_ripe",
        "nearest_tree",
        "nearest_iron",
        "cheap_train_affordable",
        "previous_action",
    ),
}


def majority(labels: list[str]) -> str:
    counts = Counter(labels)
    return min(counts, key=lambda label: (-counts[label], label))


def gini(labels: list[str]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    total = len(labels)
    return 1 - sum((count / total) ** 2 for count in counts.values())


def fit_tree(
    rows: list[dict],
    features: tuple[str, ...],
    max_depth: int,
    min_leaf: int,
    depth: int = 0,
) -> dict:
    labels = [row["label"] for row in rows]
    node = {
        "label": majority(labels),
        "rows": len(rows),
        "counts": dict(sorted(Counter(labels).items())),
    }
    if depth >= max_depth or len(set(labels)) == 1 or len(rows) < 2 * min_leaf:
        return node
    parent = gini(labels)
    best = None
    for feature in features:
        for value in sorted({row["features"][feature] for row in rows}):
            left = [row for row in rows if row["features"][feature] == value]
            if len(left) < min_leaf or len(rows) - len(left) < min_leaf:
                continue
            right = [row for row in rows if row["features"][feature] != value]
            impurity = (len(left) * gini([row["label"] for row in left])) + (
                len(right) * gini([row["label"] for row in right])
            )
            gain = parent - impurity / len(rows)
            candidate = (gain, feature, value, left, right)
            if best is None or candidate[:3] > best[:3]:
                best = candidate
    if best is None or best[0] <= 0:
        return node
    _, feature, value, left, right = best
    left_tree = fit_tree(left, features, max_depth, min_leaf, depth + 1)
    right_tree = fit_tree(right, features, max_depth, min_leaf, depth + 1)
    if (
        "feature" not in left_tree
        and "feature" not in right_tree
        and left_tree["label"] == right_tree["label"]
    ):
        return node
    node.update(
        {
            "feature": feature,
            "value": value,
            "left": left_tree,
            "right": right_tree,
        }
    )
    return node


def predict(tree: dict, row: dict) -> str:
    while "feature" in tree:
        tree = (
            tree["left"]
            if row["features"][tree["feature"]] == tree["value"]
            else tree["right"]
        )
    return tree["label"]


def node_count(tree: dict) -> int:
    if "feature" not in tree:
        return 1
    return 1 + node_count(tree["left"]) + node_count(tree["right"])


def tree_expression(tree: dict) -> str:
    if "feature" not in tree:
        return tree["label"]
    value = json.dumps(tree["value"], ensure_ascii=True)
    return (
        f"if {tree['feature']}=={value}{{{tree_expression(tree['left'])}}}"
        f"else{{{tree_expression(tree['right'])}}}"
    )


def configurations() -> list[dict]:
    return [
        {
            "feature_set": feature_set,
            "max_depth": max_depth,
            "min_leaf": min_leaf,
        }
        for feature_set in FEATURE_SETS
        for max_depth in (4, 6, 8, 10)
        for min_leaf in (5, 15, 30)
    ]


def evaluate_config(payload: tuple[list[dict], dict]) -> dict:
    rows, config = payload
    features = FEATURE_SETS[config["feature_set"]]
    actual = []
    predicted = []
    folds = []
    held_trees = []
    for fold in range(5):
        training = [row for row in rows if row["game_fold"] != fold]
        held = [row for row in rows if row["game_fold"] == fold]
        tree = fit_tree(
            training,
            features,
            config["max_depth"],
            config["min_leaf"],
        )
        predictions = [predict(tree, row) for row in held]
        report = classification_summary([row["label"] for row in held], predictions)
        folds.append(
            {
                "fold": fold,
                "training_games": len({row["game_id"] for row in training}),
                "held_games": len({row["game_id"] for row in held}),
                "episodes": len(held),
                "accuracy": report["accuracy"],
                "macro_f1": report["macro_f1"],
                "nodes": node_count(tree),
                "expression_bytes": len(tree_expression(tree)),
            }
        )
        actual.extend(row["label"] for row in held)
        predicted.extend(predictions)
        held_trees.append(tree)
    report = classification_summary(actual, predicted)
    report.update(
        {
            "folds": folds,
            "worst_fold_accuracy": min(fold["accuracy"] for fold in folds),
            "worst_fold_macro_f1": min(fold["macro_f1"] for fold in folds),
            "mean_nodes": statistics.mean(fold["nodes"] for fold in folds),
            "maximum_nodes": max(fold["nodes"] for fold in folds),
            "maximum_expression_bytes": max(
                fold["expression_bytes"] for fold in folds
            ),
        }
    )
    passed = bool(
        report["accuracy"] >= 0.70
        and report["macro_f1"] >= 0.48
        and report["worst_fold_accuracy"] >= 0.67
        and report["worst_fold_macro_f1"] >= 0.44
        and report["maximum_nodes"] <= 127
        and report["maximum_expression_bytes"] <= 20_000
    )
    return {"config": config, "held_game": report, "gate_passed": passed}


def rank(report: dict) -> tuple:
    held = report["held_game"]
    return (
        report["gate_passed"],
        held["worst_fold_accuracy"],
        held["accuracy"],
        held["macro_f1"],
        -held["maximum_expression_bytes"],
    )


def analyze(rows: list[dict], jobs: int) -> dict:
    configs = configurations()
    payloads = [(rows, config) for config in configs]
    if jobs == 1:
        reports = [evaluate_config(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=min(jobs, len(payloads))) as pool:
            reports = list(pool.map(evaluate_config, payloads))
    reports.sort(key=rank, reverse=True)
    eligible = [report for report in reports if report["gate_passed"]]
    selected = eligible[0] if eligible else None
    tree = None
    expression = None
    if selected:
        config = selected["config"]
        tree = fit_tree(
            rows,
            FEATURE_SETS[config["feature_set"]],
            config["max_depth"],
            config["min_leaf"],
        )
        expression = tree_expression(tree)
    return {
        "schema": 1,
        "scope": (
            "compact categorical intent tree on consumed Norxondor replay episodes; fivefold "
            "whole-game exclusion; future action supplies labels only"
        ),
        "games": len({row["game_id"] for row in rows}),
        "episodes": len(rows),
        "labels": dict(sorted(Counter(row["label"] for row in rows).items())),
        "configuration_count": len(configs),
        "gate": {
            "minimum_accuracy": 0.70,
            "minimum_macro_f1": 0.48,
            "minimum_worst_fold_accuracy": 0.67,
            "minimum_worst_fold_macro_f1": 0.44,
            "maximum_nodes": 127,
            "maximum_expression_bytes": 20_000,
        },
        "eligible_configurations": len(eligible),
        "selected": selected,
        "top_configurations": reports[:10],
        "tree": tree,
        "node_count": node_count(tree) if tree else None,
        "rust_expression": expression,
        "estimated_expression_bytes": len(expression) if expression else None,
        "decision": {
            "authorize_native_research_controller": selected is not None,
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(os.cpu_count() or 1, 10))
    args = parser.parse_args()
    analysis = json.loads(args.analysis.read_text())
    occurrences = [
        row for row in analysis["occurrences"] if row["agent_id"] == args.agent_id
    ]
    occurrences.sort(key=lambda row: row["game_id"])
    analyzed = []
    for index, occurrence in enumerate(occurrences, 1):
        analyzed.append(extract_game(occurrence))
        if index % 10 == 0 or index == len(occurrences):
            print(f"decoded {index}/{len(occurrences)} games", flush=True)
    episodes = episode_rows([row for game in analyzed for row in game["rows"]])
    payload = analyze(episodes, max(args.jobs, 1))
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps({key: payload[key] for key in (
        "games", "episodes", "eligible_configurations", "selected", "node_count",
        "estimated_expression_bytes", "decision"
    )}, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
