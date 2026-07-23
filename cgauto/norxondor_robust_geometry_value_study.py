#!/usr/bin/env python3
"""Learn a map-only selector for lower-quartile-positive worker-three outcomes."""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import json
import os
from pathlib import Path
import statistics

import numpy as np

from cgauto.norxondor_research_rollout_study import atomic_write
from cgauto.norxondor_value_model_study import (
    fit_forest,
    forest_expression,
    forest_scores,
    node_count,
    policy_evaluation,
    read_rows,
    seed_folds,
    used_feature_indexes,
)
from cgauto.rollout_selector_distillation import confusion, turn_one_features
from sim.mapgen import generate_bronze


def group_rows(rows: list[dict]) -> list[list[dict]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["seed"], row["seat"])].append(row)
    result = []
    for key, group in sorted(grouped.items()):
        opponents = {row["actual_opponent"] for row in group}
        if len(group) != 8 or len(opponents) != 8:
            raise ValueError(f"incomplete opponent grid for {key}")
        result.append(group)
    return result


def lower_quartile_positive(group: list[dict]) -> bool:
    margins = sorted(row["margin_delta"] for row in group)
    return margins[1] > 0


def map_matrix(groups: list[list[dict]]) -> tuple[np.ndarray, list[str]]:
    feature_rows = [
        turn_one_features(generate_bronze(group[0]["seed"]), group[0]["seat"])
        for group in groups
    ]
    names = sorted(feature_rows[0])
    matrix = np.asarray(
        [[features[name] for name in names] for features in feature_rows],
        dtype=np.float64,
    )
    varying = np.ptp(matrix, axis=0) > 0
    return matrix[:, varying], [name for name, keep in zip(names, varying) if keep]


def configuration_grid() -> list[dict]:
    shared = {"negative_weight": 1.0, "thresholds_per_feature": 4}
    return [
        {**shared, "trees": 16, "max_depth": 2, "min_leaf": 4, "max_features": 16},
        {**shared, "trees": 16, "max_depth": 3, "min_leaf": 4, "max_features": 16},
        {**shared, "trees": 16, "max_depth": 4, "min_leaf": 4, "max_features": 16},
        {**shared, "trees": 32, "max_depth": 2, "min_leaf": 4, "max_features": 16},
        {**shared, "trees": 32, "max_depth": 3, "min_leaf": 4, "max_features": 16},
        {**shared, "trees": 32, "max_depth": 4, "min_leaf": 4, "max_features": 16},
        {**shared, "trees": 32, "max_depth": 3, "min_leaf": 2, "max_features": 24},
        {**shared, "trees": 32, "max_depth": 4, "min_leaf": 2, "max_features": 24},
        {**shared, "trees": 64, "max_depth": 3, "min_leaf": 4, "max_features": 24},
        {**shared, "trees": 64, "max_depth": 4, "min_leaf": 2, "max_features": 32},
    ]


def expanded_predictions(
    rows: list[dict], groups: list[list[dict]], group_predictions: np.ndarray
) -> np.ndarray:
    selected = {
        (group[0]["seed"], group[0]["seat"]): bool(prediction)
        for group, prediction in zip(groups, group_predictions)
    }
    return np.asarray(
        [selected[(row["seed"], row["seat"])] for row in rows], dtype=bool
    )


def report_threshold(
    rows: list[dict],
    groups: list[list[dict]],
    labels: np.ndarray,
    scores: np.ndarray,
    threshold: float,
) -> dict:
    predictions = scores >= threshold
    truth = {index: bool(value) for index, value in enumerate(labels)}
    predicted = {index: bool(value) for index, value in enumerate(predictions)}
    classification = confusion(truth, predicted)
    expanded = expanded_predictions(rows, groups, predictions)
    selected = int(np.count_nonzero(expanded))
    positive = int(
        sum(
            row["margin_delta"] > 0 and bool(choose)
            for row, choose in zip(rows, expanded)
        )
    )
    actual_precision = float(positive / selected) if selected else 1.0
    policy = policy_evaluation(rows, expanded)
    return {
        "threshold": threshold,
        "group_classification": classification,
        "actual_selection_precision": actual_precision,
        "policy": policy,
        "gate_passed": bool(
            policy["selection_rate"] >= 0.05
            and actual_precision >= 0.90
            and policy["gate_passed"]
        ),
    }


def rank(report: dict) -> tuple:
    return (
        report["gate_passed"],
        report["policy"]["selection_rate"] >= 0.05,
        report["actual_selection_precision"],
        report["group_classification"]["f0_5"],
        report["policy"]["margin_delta_vs_resident"]["mean"],
    )


def evaluate_config(payload: tuple) -> dict:
    matrix, labels, seeds, rows, groups, config, index = payload
    scores = np.zeros(len(groups), dtype=np.float64)
    for fold, held_mask in enumerate(seed_folds(seeds)):
        train = np.flatnonzero(~held_mask)
        held = np.flatnonzero(held_mask)
        forest = fit_forest(
            matrix,
            labels,
            seeds,
            train,
            config,
            9_553_250 + index * 101 + fold * 10_000,
        )
        scores += forest_scores(forest, matrix, held)
    reports = [
        report_threshold(rows, groups, labels, scores, float(threshold))
        for threshold in np.arange(0.10, 0.951, 0.05)
    ]
    reports.sort(key=rank, reverse=True)
    return {"config": config, "best": reports[0], "threshold_reports": reports}


def analyze(rows: list[dict], jobs: int) -> dict:
    groups = group_rows(rows)
    matrix, feature_names = map_matrix(groups)
    labels = np.asarray([lower_quartile_positive(group) for group in groups], dtype=bool)
    seeds = np.asarray([group[0]["seed"] for group in groups], dtype=np.int64)
    configs = configuration_grid()
    payloads = [
        (matrix, labels, seeds, rows, groups, config, index)
        for index, config in enumerate(configs)
    ]
    if jobs == 1:
        reports = [evaluate_config(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=min(jobs, len(payloads))) as pool:
            reports = list(pool.map(evaluate_config, payloads))
    reports.sort(key=lambda report: rank(report["best"]), reverse=True)
    eligible = [report for report in reports if report["best"]["gate_passed"]]
    selected = eligible[0] if eligible else None

    oracle_predictions = expanded_predictions(rows, groups, labels)
    oracle_selected = int(np.count_nonzero(oracle_predictions))
    oracle_positive = int(
        sum(
            row["margin_delta"] > 0 and bool(choose)
            for row, choose in zip(rows, oracle_predictions)
        )
    )
    oracle = {
        "positive_groups": int(np.count_nonzero(labels)),
        "actual_selection_precision": float(oracle_positive / oracle_selected),
        "policy": policy_evaluation(rows, oracle_predictions),
    }

    forest = None
    expression = None
    used_features = []
    nodes = None
    training = None
    if selected:
        config = selected["config"]
        threshold = selected["best"]["threshold"]
        forest = fit_forest(
            matrix,
            labels,
            seeds,
            np.arange(len(groups)),
            config,
            10_553_250,
        )
        full_scores = forest_scores(forest, matrix, np.arange(len(groups)))
        training = report_threshold(rows, groups, labels, full_scores, threshold)
        used_indexes = sorted(
            set().union(*(used_feature_indexes(tree) for tree in forest))
        )
        used_features = [feature_names[index] for index in used_indexes]
        nodes = sum(node_count(tree) for tree in forest)
        expression = forest_expression(forest, feature_names, threshold)
    return {
        "schema": 1,
        "scope": (
            "map-only precision-first classifier of seed-seat cells whose second-worst exact "
            "worker-three margin is positive across all eight local opponents"
        ),
        "cells": len(rows),
        "map_seat_groups": len(groups),
        "seeds": len(set(seeds.tolist())),
        "feature_count": len(feature_names),
        "configuration_count": len(configs),
        "lower_quartile_oracle": oracle,
        "eligible_configurations": len(eligible),
        "selected": selected,
        "top_configurations": reports,
        "forest": forest,
        "node_count": nodes,
        "used_features": used_features,
        "rust_expression": expression,
        "estimated_expression_bytes": len(expression) if expression else None,
        "training_fit": training,
        "research_gate": {
            "requirements": [
                "contiguous blocked-seed actual selection precision at least 90%",
                "blocked-seed selection rate at least 5%",
                "blocked-seed complete-policy gate passes",
                "features contain map geometry only",
            ],
            "passed": selected is not None,
        },
        "decision": {
            "freeze_for_new_validation": selected is not None,
            "build_online_prototype": False,
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(os.cpu_count() or 1, 10))
    args = parser.parse_args()
    rows, _ = read_rows(args.input)
    payload = analyze(rows, max(args.jobs, 1))
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        key: payload[key]
        for key in (
            "cells",
            "map_seat_groups",
            "feature_count",
            "lower_quartile_oracle",
            "eligible_configurations",
            "selected",
            "node_count",
            "used_features",
            "estimated_expression_bytes",
            "research_gate",
            "decision",
        )
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
