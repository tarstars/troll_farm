#!/usr/bin/env python3
"""Fit a compact, precision-first value model from exact two-branch outcomes."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import json
import math
import os
from pathlib import Path
import re
import statistics

import numpy as np

from cgauto.norxondor_research_rollout_study import atomic_write, summary
from cgauto.rollout_selector_distillation import confusion
from cgauto.rollout_selector_distillation import turn_one_features
from sim.mapgen import generate_bronze


OUTCOME_FIELDS = {
    "resident_margin",
    "three_worker_margin",
    "margin_delta",
    "resident_score",
    "three_worker_score",
    "score_delta",
    "resident_workers",
    "three_worker_workers",
    "branch_elapsed_us",
}
OPPONENT_FAMILIES = (
    ("compact_gold", "gold_elite"),
    ("gold_adaptive",),
    ("mybot",),
    ("printer_bot",),
    ("sched_bot",),
    ("script_boss",),
    ("silver_boss",),
)


def trajectory_field_names(fieldnames: list[str]) -> list[str]:
    return [name for name in fieldnames if re.fullmatch(r"s\d+_.+", name)]


def read_rows(path: Path) -> tuple[list[dict], list[str]]:
    rows = []
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError("dataset has no header")
        trajectory_fields = trajectory_field_names(reader.fieldnames)
        for row in reader:
            parsed = {
                "seed": int(row["seed"]),
                "seat": int(row["seat"]),
                "decision_turn": int(row["decision_turn"]),
                "actual_opponent": row["actual_opponent"],
            }
            parsed.update({name: int(row[name]) for name in trajectory_fields})
            parsed.update({name: int(row[name]) for name in OUTCOME_FIELDS})
            rows.append(parsed)
    return rows, trajectory_fields


def row_key(row: dict) -> tuple[int, int, str]:
    return row["seed"], row["seat"], row["actual_opponent"]


def trajectory_features(row: dict, trajectory_fields: list[str]) -> dict[str, float]:
    features = {name: row[name] for name in trajectory_fields}
    snapshots = sorted(
        {int(name[1 : name.index("_")]) for name in trajectory_fields}
    )
    if snapshots != list(range(snapshots[-1] + 1)):
        raise ValueError("trajectory snapshots are not contiguous from zero")
    suffixes = [name.removeprefix("s0_") for name in trajectory_fields if name.startswith("s0_")]
    for suffix in suffixes:
        for previous, current in zip(snapshots, snapshots[1:]):
            features[f"d{current}{previous}_{suffix}"] = (
                row[f"s{current}_{suffix}"] - row[f"s{previous}_{suffix}"]
            )
        if snapshots[-1] > 1:
            features[f"d{snapshots[-1]}0_{suffix}"] = (
                row[f"s{snapshots[-1]}_{suffix}"] - row[f"s0_{suffix}"]
            )
    return features


def feature_matrix(
    rows: list[dict], trajectory_fields: list[str]
) -> tuple[np.ndarray, list[str]]:
    map_cache = {}
    feature_rows = []
    for row in rows:
        cache_key = row["seed"], row["seat"]
        if cache_key not in map_cache:
            map_cache[cache_key] = {
                f"map_{name}": value
                for name, value in turn_one_features(
                    generate_bronze(row["seed"]), row["seat"]
                ).items()
            }
        features = dict(map_cache[cache_key])
        features.update(trajectory_features(row, trajectory_fields))
        feature_rows.append(features)
    names = sorted(feature_rows[0])
    matrix = np.asarray(
        [[features[name] for name in names] for features in feature_rows],
        dtype=np.float64,
    )
    varying = np.ptp(matrix, axis=0) > 0
    return matrix[:, varying], [name for name, keep in zip(names, varying) if keep]


def weighted_gini(labels: np.ndarray, negative_weight: float) -> float:
    positive = int(np.count_nonzero(labels))
    negative = len(labels) - positive
    positive_weight = float(positive)
    negative_total = negative_weight * negative
    total = positive_weight + negative_total
    if total == 0:
        return 0.0
    probability = positive_weight / total
    return total * 2 * probability * (1 - probability)


def leaf_node(labels: np.ndarray) -> dict:
    positive = int(np.count_nonzero(labels))
    return {
        "feature": None,
        "score": (positive + 1) / (len(labels) + 2),
        "positive": positive,
        "negative": len(labels) - positive,
    }


def fit_extra_tree(
    matrix: np.ndarray,
    labels: np.ndarray,
    indexes: np.ndarray,
    rng: np.random.Generator,
    config: dict,
    depth: int = 0,
) -> dict:
    node_labels = labels[indexes]
    leaf = leaf_node(node_labels)
    if (
        depth >= config["max_depth"]
        or leaf["positive"] == 0
        or leaf["negative"] == 0
        or len(indexes) < 2 * config["min_leaf"]
    ):
        return leaf
    feature_count = matrix.shape[1]
    sampled = rng.choice(
        feature_count,
        size=min(config["max_features"], feature_count),
        replace=False,
    )
    best = None
    for feature in sampled:
        values = matrix[indexes, feature]
        unique = np.unique(values)
        if len(unique) < 2:
            continue
        gap_indexes = rng.choice(
            len(unique) - 1,
            size=min(config["thresholds_per_feature"], len(unique) - 1),
            replace=False,
        )
        for gap in gap_indexes:
            threshold = float((unique[gap] + unique[gap + 1]) / 2)
            left_mask = values <= threshold
            left_count = int(np.count_nonzero(left_mask))
            if (
                left_count < config["min_leaf"]
                or len(indexes) - left_count < config["min_leaf"]
            ):
                continue
            impurity = weighted_gini(
                node_labels[left_mask], config["negative_weight"]
            ) + weighted_gini(node_labels[~left_mask], config["negative_weight"])
            candidate = (impurity, int(feature), threshold, left_mask)
            if best is None or candidate[:3] < best[:3]:
                best = candidate
    if best is None:
        return leaf
    _, feature, threshold, left_mask = best
    return {
        "feature": feature,
        "threshold": threshold,
        "positive": leaf["positive"],
        "negative": leaf["negative"],
        "left": fit_extra_tree(
            matrix, labels, indexes[left_mask], rng, config, depth + 1
        ),
        "right": fit_extra_tree(
            matrix, labels, indexes[~left_mask], rng, config, depth + 1
        ),
    }


def seed_bootstrap(
    indexes: np.ndarray, seeds: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    unique = np.unique(seeds[indexes])
    sampled = rng.choice(unique, size=len(unique), replace=True)
    by_seed = {seed: indexes[seeds[indexes] == seed] for seed in unique}
    return np.concatenate([by_seed[seed] for seed in sampled])


def fit_forest(
    matrix: np.ndarray,
    labels: np.ndarray,
    seeds: np.ndarray,
    indexes: np.ndarray,
    config: dict,
    random_seed: int,
) -> list[dict]:
    rng = np.random.default_rng(random_seed)
    return [
        fit_extra_tree(
            matrix,
            labels,
            seed_bootstrap(indexes, seeds, rng),
            rng,
            config,
        )
        for _ in range(config["trees"])
    ]


def predict_tree(tree: dict, matrix: np.ndarray, indexes: np.ndarray, output: np.ndarray) -> None:
    if tree["feature"] is None:
        output[indexes] = tree["score"]
        return
    mask = matrix[indexes, tree["feature"]] <= tree["threshold"]
    predict_tree(tree["left"], matrix, indexes[mask], output)
    predict_tree(tree["right"], matrix, indexes[~mask], output)


def forest_scores(forest: list[dict], matrix: np.ndarray, indexes: np.ndarray) -> np.ndarray:
    scores = np.zeros(matrix.shape[0], dtype=np.float64)
    for tree in forest:
        tree_scores = np.zeros(matrix.shape[0], dtype=np.float64)
        predict_tree(tree, matrix, indexes, tree_scores)
        scores[indexes] += tree_scores[indexes]
    scores[indexes] /= len(forest)
    return scores


def seed_folds(seeds: np.ndarray, fold_count: int = 5) -> list[np.ndarray]:
    unique = np.unique(seeds)
    return [
        np.isin(
            seeds,
            unique[
                math.floor(fold * len(unique) / fold_count) : math.floor(
                    (fold + 1) * len(unique) / fold_count
                )
            ],
        )
        for fold in range(fold_count)
    ]


def opponent_family_folds(opponents: np.ndarray) -> list[np.ndarray]:
    return [np.isin(opponents, family) for family in OPPONENT_FAMILIES]


def cross_validated_scores(
    matrix: np.ndarray,
    labels: np.ndarray,
    seeds: np.ndarray,
    folds: list[np.ndarray],
    config: dict,
    random_seed: int,
) -> np.ndarray:
    scores = np.zeros(len(labels), dtype=np.float64)
    covered = np.zeros(len(labels), dtype=bool)
    for fold, held_mask in enumerate(folds):
        train = np.flatnonzero(~held_mask)
        held = np.flatnonzero(held_mask)
        forest = fit_forest(
            matrix, labels, seeds, train, config, random_seed + fold * 10_000
        )
        scores += forest_scores(forest, matrix, held)
        covered[held] = True
    if not np.all(covered):
        raise ValueError("cross-validation folds do not cover every row")
    return scores


def policy_evaluation(rows: list[dict], predictions: np.ndarray) -> dict:
    margin_deltas = [row["margin_delta"] if selected else 0 for row, selected in zip(rows, predictions)]
    score_deltas = [row["score_delta"] if selected else 0 for row, selected in zip(rows, predictions)]
    by_opponent = {
        opponent: statistics.mean(
            row["margin_delta"] if selected else 0
            for row, selected in zip(rows, predictions)
            if row["actual_opponent"] == opponent
        )
        for opponent in sorted({row["actual_opponent"] for row in rows})
    }
    report = {
        "selected_cells": int(np.count_nonzero(predictions)),
        "selection_rate": float(np.mean(predictions)),
        "margin_delta_vs_resident": summary(margin_deltas),
        "score_delta_vs_resident": summary(score_deltas),
        "opponent_mean_margin_deltas": by_opponent,
        "nonnegative_opponents": sum(value >= 0 for value in by_opponent.values()),
        "worst_opponent_mean_margin_delta": min(by_opponent.values()),
    }
    report["gate_passed"] = (
        report["selection_rate"] >= 0.05
        and report["margin_delta_vs_resident"]["mean"] >= 2
        and report["score_delta_vs_resident"]["mean"] >= 2
        and report["nonnegative_opponents"] >= 5
        and report["worst_opponent_mean_margin_delta"] >= -5
    )
    return report


def score_report(
    rows: list[dict], labels: np.ndarray, scores: np.ndarray, threshold: float
) -> dict:
    predictions = scores >= threshold
    truth = {index: bool(value) for index, value in enumerate(labels)}
    predicted = {index: bool(value) for index, value in enumerate(predictions)}
    classification = confusion(truth, predicted)
    classification_by_opponent = {}
    for opponent in sorted({row["actual_opponent"] for row in rows}):
        indexes = [
            index
            for index, row in enumerate(rows)
            if row["actual_opponent"] == opponent
        ]
        classification_by_opponent[opponent] = confusion(
            {index: truth[index] for index in indexes},
            {index: predicted[index] for index in indexes},
        )
    policy = policy_evaluation(rows, predictions)
    return {
        "threshold": threshold,
        "classification": classification,
        "classification_by_opponent": classification_by_opponent,
        "policy": policy,
        "gate_passed": (
            classification["precision"] >= 0.90
            and policy["selection_rate"] >= 0.05
            and policy["gate_passed"]
        ),
    }


def configuration_grid(name: str = "compact") -> list[dict]:
    shared = {"thresholds_per_feature": 2}
    if name == "compact":
        return [
            {**shared, "trees": 8, "max_depth": 3, "min_leaf": 16, "negative_weight": 1.0, "max_features": 32},
            {**shared, "trees": 8, "max_depth": 4, "min_leaf": 16, "negative_weight": 1.0, "max_features": 32},
            {**shared, "trees": 8, "max_depth": 5, "min_leaf": 16, "negative_weight": 1.0, "max_features": 32},
            {**shared, "trees": 16, "max_depth": 3, "min_leaf": 16, "negative_weight": 1.0, "max_features": 32},
            {**shared, "trees": 16, "max_depth": 4, "min_leaf": 16, "negative_weight": 1.0, "max_features": 32},
            {**shared, "trees": 16, "max_depth": 5, "min_leaf": 16, "negative_weight": 1.0, "max_features": 32},
            {**shared, "trees": 16, "max_depth": 4, "min_leaf": 8, "negative_weight": 1.0, "max_features": 32},
            {**shared, "trees": 16, "max_depth": 4, "min_leaf": 32, "negative_weight": 1.0, "max_features": 32},
            {**shared, "trees": 16, "max_depth": 4, "min_leaf": 16, "negative_weight": 2.0, "max_features": 32},
            {**shared, "trees": 16, "max_depth": 4, "min_leaf": 16, "negative_weight": 1.0, "max_features": 64},
        ]
    if name == "expanded":
        shared = {"thresholds_per_feature": 4, "negative_weight": 1.0}
        return [
            {**shared, "trees": 32, "max_depth": 4, "min_leaf": 16, "max_features": 64, "training_margin_floor": 0, "require_positive_score": False},
            {**shared, "trees": 32, "max_depth": 5, "min_leaf": 16, "max_features": 64, "training_margin_floor": 0, "require_positive_score": False},
            {**shared, "trees": 64, "max_depth": 4, "min_leaf": 16, "max_features": 64, "training_margin_floor": 0, "require_positive_score": False},
            {**shared, "trees": 64, "max_depth": 5, "min_leaf": 16, "max_features": 64, "training_margin_floor": 0, "require_positive_score": False},
            {**shared, "trees": 32, "max_depth": 5, "min_leaf": 8, "max_features": 96, "training_margin_floor": 10, "require_positive_score": False},
            {**shared, "trees": 64, "max_depth": 5, "min_leaf": 8, "max_features": 96, "training_margin_floor": 10, "require_positive_score": False},
            {**shared, "trees": 32, "max_depth": 5, "min_leaf": 8, "max_features": 96, "training_margin_floor": 20, "require_positive_score": False},
            {**shared, "trees": 64, "max_depth": 5, "min_leaf": 8, "max_features": 96, "training_margin_floor": 20, "require_positive_score": False},
            {**shared, "trees": 32, "max_depth": 5, "min_leaf": 8, "max_features": 96, "training_margin_floor": 0, "require_positive_score": True},
            {**shared, "trees": 64, "max_depth": 5, "min_leaf": 8, "max_features": 96, "training_margin_floor": 10, "require_positive_score": True},
        ]
    raise ValueError(f"unknown configuration grid {name!r}")


def candidate_rank(report: dict) -> tuple:
    seed = report["seed_cv"]
    opponent = report["opponent_family_cv"]
    coverage = min(seed["policy"]["selection_rate"], opponent["policy"]["selection_rate"])
    precision = min(
        seed["classification"]["precision"], opponent["classification"]["precision"]
    )
    return (
        report["gate_passed"],
        coverage >= 0.05,
        precision,
        min(seed["classification"]["f0_5"], opponent["classification"]["f0_5"]),
        min(
            seed["policy"]["margin_delta_vs_resident"]["mean"],
            opponent["policy"]["margin_delta_vs_resident"]["mean"],
        ),
        -report["config"]["trees"],
        -report["config"]["max_depth"],
    )


def evaluate_config(payload: tuple) -> dict:
    matrix, labels, margins, score_deltas, seeds, opponents, rows, config, index = payload
    training_margin_floor = config.get("training_margin_floor", 0)
    fit_labels = margins > training_margin_floor
    if config.get("require_positive_score", False):
        fit_labels &= score_deltas > 0
    seed_scores = cross_validated_scores(
        matrix, fit_labels, seeds, seed_folds(seeds), config, 6_553_250 + index * 101
    )
    opponent_scores = cross_validated_scores(
        matrix,
        fit_labels,
        seeds,
        opponent_family_folds(opponents),
        config,
        7_553_250 + index * 101,
    )
    candidates = []
    for threshold in np.arange(0.30, 0.951, 0.05):
        seed_report = score_report(rows, labels, seed_scores, float(threshold))
        opponent_report = score_report(rows, labels, opponent_scores, float(threshold))
        candidate = {
            "config": config,
            "threshold": float(threshold),
            "seed_cv": seed_report,
            "opponent_family_cv": opponent_report,
            "gate_passed": seed_report["gate_passed"] and opponent_report["gate_passed"],
        }
        candidates.append(candidate)
    candidates.sort(key=candidate_rank, reverse=True)
    return {"config": config, "best": candidates[0], "threshold_reports": candidates}


def node_count(tree: dict) -> int:
    if tree["feature"] is None:
        return 1
    return 1 + node_count(tree["left"]) + node_count(tree["right"])


def used_feature_indexes(tree: dict) -> set[int]:
    if tree["feature"] is None:
        return set()
    return {tree["feature"]} | used_feature_indexes(tree["left"]) | used_feature_indexes(tree["right"])


def tree_expression(tree: dict, feature_names: list[str]) -> str:
    if tree["feature"] is None:
        return f"{tree['score']:.6g}"
    feature = feature_names[tree["feature"]]
    return (
        f"if f.{feature}<={tree['threshold']:.6g}"
        f"{{{tree_expression(tree['left'], feature_names)}}}"
        f"else{{{tree_expression(tree['right'], feature_names)}}}"
    )


def forest_expression(
    forest: list[dict], feature_names: list[str], threshold: float
) -> str:
    terms = "+".join(f"({tree_expression(tree, feature_names)})" for tree in forest)
    return f"({terms})/{len(forest)}.0>={threshold:.6g}"


def analyze(
    rows: list[dict], trajectory_fields: list[str], jobs: int, grid: str = "compact"
) -> dict:
    keys = [row_key(row) for row in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("dataset contains duplicate cells")
    decision_turns = sorted({row["decision_turn"] for row in rows})
    if len(decision_turns) != 1:
        raise ValueError("value model expects one decision turn per study")
    matrix, feature_names = feature_matrix(rows, trajectory_fields)
    labels = np.asarray([row["margin_delta"] > 0 for row in rows], dtype=bool)
    margins = np.asarray([row["margin_delta"] for row in rows], dtype=np.float64)
    score_deltas = np.asarray([row["score_delta"] for row in rows], dtype=np.float64)
    seeds = np.asarray([row["seed"] for row in rows], dtype=np.int64)
    opponents = np.asarray([row["actual_opponent"] for row in rows], dtype=object)
    configs = configuration_grid(grid)
    payloads = [
        (
            matrix,
            labels,
            margins,
            score_deltas,
            seeds,
            opponents,
            rows,
            config,
            index,
        )
        for index, config in enumerate(configs)
    ]
    if jobs == 1:
        reports = [evaluate_config(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=min(jobs, len(payloads))) as pool:
            reports = list(pool.map(evaluate_config, payloads))
    reports.sort(key=lambda report: candidate_rank(report["best"]), reverse=True)
    eligible = [report for report in reports if report["best"]["gate_passed"]]
    selected_report = eligible[0] if eligible else None

    forest = None
    expression = None
    used_features = []
    nodes = None
    training = None
    if selected_report:
        config = selected_report["config"]
        threshold = selected_report["best"]["threshold"]
        fit_labels = margins > config.get("training_margin_floor", 0)
        if config.get("require_positive_score", False):
            fit_labels &= score_deltas > 0
        forest = fit_forest(
            matrix,
            fit_labels,
            seeds,
            np.arange(len(rows)),
            config,
            8_553_250,
        )
        full_scores = forest_scores(forest, matrix, np.arange(len(rows)))
        training = score_report(rows, labels, full_scores, threshold)
        used_indexes = sorted(
            set().union(*(used_feature_indexes(tree) for tree in forest))
        )
        used_features = [feature_names[index] for index in used_indexes]
        nodes = sum(node_count(tree) for tree in forest)
        expression = forest_expression(forest, feature_names, threshold)
    oracle = policy_evaluation(rows, labels)
    return {
        "schema": 1,
        "scope": (
            "precision-first compact ExtraTrees-style value model on exact resident-versus-"
            "worker-three terminal outcomes; features are initial map geometry and directly "
            "observable turn-one-to-turn-three trajectories, never opponent identity"
        ),
        "cells": len(rows),
        "seeds": len(set(seeds.tolist())),
        "decision_turn": decision_turns[0],
        "opponents": sorted(set(opponents.tolist())),
        "positive_cells": int(np.count_nonzero(labels)),
        "trajectory_feature_count": len(trajectory_fields),
        "varying_feature_count": len(feature_names),
        "configuration_count": len(configs),
        "configuration_grid": grid,
        "eligible_configurations": len(eligible),
        "selected": selected_report,
        "top_configurations": reports,
        "positive_cell_oracle": oracle,
        "forest": forest,
        "node_count": nodes,
        "used_features": used_features,
        "rust_expression": expression,
        "estimated_expression_bytes": len(expression) if expression else None,
        "training_fit": training,
        "research_gate": {
            "requirements": [
                "both contiguous blocked-seed and leave-one-opponent-family-out precision at least 90%",
                "both cross-validated selection rates at least 5%",
                "both cross-validated complete-policy gates pass",
                "features exclude opponent identity and embedded opponent models",
            ],
            "passed": selected_report is not None,
        },
        "decision": {
            "freeze_for_new_validation": selected_report is not None,
            "build_online_prototype": False,
            "build_submission_candidate": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(os.cpu_count() or 1, 10))
    parser.add_argument("--grid", choices=("compact", "expanded"), default="compact")
    args = parser.parse_args()
    rows, trajectory_fields = read_rows(args.input)
    payload = analyze(rows, trajectory_fields, max(args.jobs, 1), args.grid)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    compact = {
        key: payload[key]
        for key in (
            "cells",
            "seeds",
            "positive_cells",
            "varying_feature_count",
            "eligible_configurations",
            "selected",
            "positive_cell_oracle",
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
