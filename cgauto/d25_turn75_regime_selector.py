#!/usr/bin/env python3
"""Fit and cross-validate the frozen D25 observable turn-75 value selector."""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics

import numpy as np


OPPONENTS = (
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
)
KEY_FIELDS = ("seed", "seat", "opponent")
META_FIELDS = {*KEY_FIELDS, "reached_cut"}
BUFFERS = (0.0, 10.0, 20.0, 30.0, 40.0)


def robust_summary(values) -> dict:
    values = list(float(value) for value in values)
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "trimmed_5pct_mean": None,
            "standard_deviation": None,
            "standard_error": None,
            "ci95_normal": [None, None],
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "minimum": None,
            "maximum": None,
        }
    ordered = sorted(values)
    trim = math.floor(0.05 * len(ordered))
    trimmed = ordered[trim : len(ordered) - trim] if trim else ordered
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    se = sd / math.sqrt(len(values))
    return {
        "n": len(values),
        "mean": mean,
        "median": statistics.median(values),
        "trimmed_5pct_mean": statistics.mean(trimmed),
        "standard_deviation": sd,
        "standard_error": se,
        "ci95_normal": [mean - 1.96 * se, mean + 1.96 * se],
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
        "minimum": ordered[0],
        "maximum": ordered[-1],
    }


def row_key(row: dict) -> tuple[int, int, str]:
    return row["seed"], row["seat"], row["opponent"]


def read_features(path: Path) -> tuple[list[dict], list[str]]:
    rows = []
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError("feature dataset has no header")
        feature_names = [name for name in reader.fieldnames if name not in META_FIELDS]
        for raw in reader:
            row = {
                "seed": int(raw["seed"]),
                "seat": int(raw["seat"]),
                "opponent": raw["opponent"],
                "reached_cut": int(raw["reached_cut"]),
                "features": {name: int(raw[name]) for name in feature_names},
            }
            rows.append(row)
    return rows, feature_names


def read_label_paths(paths: list[Path]) -> dict[tuple[int, int, str], dict]:
    grouped: dict[tuple[int, int, str], dict[str, dict]] = defaultdict(dict)
    integer_fields = (
        "seed",
        "seat",
        "decision_turn",
        "reached_cut",
        "root_my_score",
        "root_opponent_score",
        "root_my_wood",
        "root_opponent_wood",
        "root_my_workers",
        "root_opponent_workers",
        "root_plants",
        "margin",
        "my_score",
        "opponent_score",
    )
    for path in paths:
        with path.open(newline="") as stream:
            for raw in csv.DictReader(stream, delimiter="\t"):
                if int(raw["decision_turn"]) != 75 or raw["option"] not in {
                    "resident",
                    "ownership2",
                }:
                    continue
                row = dict(raw)
                for field in integer_fields:
                    row[field] = int(row[field])
                key = row_key(row)
                if row["option"] in grouped[key]:
                    raise ValueError(f"duplicate label branch {key} / {row['option']}")
                grouped[key][row["option"]] = row
    labels = {}
    for key, branches in grouped.items():
        if set(branches) != {"resident", "ownership2"}:
            raise ValueError(f"incomplete label branches for {key}")
        control = branches["resident"]
        option = branches["ownership2"]
        labels[key] = {
            "reached_cut": control["reached_cut"],
            "root_my_score": control["root_my_score"],
            "root_opponent_score": control["root_opponent_score"],
            "root_my_wood": control["root_my_wood"],
            "root_opponent_wood": control["root_opponent_wood"],
            "root_my_workers": control["root_my_workers"],
            "root_opponent_workers": control["root_opponent_workers"],
            "root_plants": control["root_plants"],
            "resident_margin": control["margin"],
            "option_margin": option["margin"],
            "margin_delta": option["margin"] - control["margin"],
            "score_delta": option["my_score"] - control["my_score"],
            "opponent_score_delta": option["opponent_score"]
            - control["opponent_score"],
        }
    return labels


def prepare(
    feature_rows: list[dict], feature_names: list[str], labels: dict
) -> tuple[list[dict], np.ndarray, list[str], dict]:
    rows = sorted(feature_rows, key=row_key)
    keys = [row_key(row) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate feature keys")
    if set(keys) != set(labels):
        raise ValueError(
            f"feature/label key mismatch: {len(set(keys) - set(labels))} feature-only, "
            f"{len(set(labels) - set(keys))} label-only"
        )
    expected = 120 * 2 * len(OPPONENTS)
    root_mismatches = []
    assembled = []
    root_pairs = (
        ("reached_cut", "reached_cut"),
        ("t75_my_score", "root_my_score"),
        ("t75_opponent_score", "root_opponent_score"),
        ("t75_my_inv_wood", "root_my_wood"),
        ("t75_opponent_inv_wood", "root_opponent_wood"),
        ("t75_my_workers", "root_my_workers"),
        ("t75_opponent_workers", "root_opponent_workers"),
        ("t75_plants", "root_plants"),
    )
    for feature_row in rows:
        key = row_key(feature_row)
        label = labels[key]
        for feature, target in root_pairs:
            actual = (
                feature_row[feature]
                if feature == "reached_cut"
                else feature_row["features"][feature]
            )
            if actual != label[target]:
                root_mismatches.append((key, feature, actual, label[target]))
        assembled.append({**feature_row, **label})
    matrix = np.asarray(
        [
            [row["features"][name] for name in feature_names]
            for row in assembled
        ],
        dtype=np.float64,
    )
    finite = bool(np.all(np.isfinite(matrix)))
    varying = np.ptp(matrix, axis=0) > 0
    matrix = matrix[:, varying]
    varying_names = [
        name for name, keep in zip(feature_names, varying, strict=True) if keep
    ]
    seeds = sorted({row["seed"] for row in assembled})
    opponents = sorted({row["opponent"] for row in assembled})
    forbidden_present = sorted(
        set(varying_names) & {"seed", "seat", "opponent", "opponent_index", "agent_id"}
    )
    integrity = {
        "expected_rows": expected,
        "rows": len(assembled),
        "unique_keys": len(set(keys)),
        "seeds": len(seeds),
        "seed_minimum": min(seeds),
        "seed_maximum": max(seeds),
        "opponents": opponents,
        "input_feature_count": len(feature_names),
        "varying_feature_count": len(varying_names),
        "finite_features": finite,
        "forbidden_identity_features": forbidden_present,
        "root_mismatch_count": len(root_mismatches),
        "root_mismatch_examples": root_mismatches[:5],
        "all_reached_cut": all(row["reached_cut"] for row in assembled),
    }
    integrity["passed"] = (
        len(assembled) == expected
        and len(set(keys)) == expected
        and len(seeds) == 120
        and opponents == sorted(OPPONENTS)
        and finite
        and not forbidden_present
        and not root_mismatches
        and integrity["all_reached_cut"]
    )
    return assembled, matrix, varying_names, integrity


def model_configs() -> list[dict]:
    configs = [
        {"family": "ridge", "alpha": float(alpha), "label": f"ridge_a{alpha}"}
        for alpha in (1, 10, 100)
    ]
    for family in ("random_forest", "extra_trees"):
        for depth in (2, 3, 4):
            for min_leaf in (20, 40, 80):
                configs.append(
                    {
                        "family": family,
                        "trees": 256,
                        "max_depth": depth,
                        "min_leaf": min_leaf,
                        "label": f"{family}_d{depth}_l{min_leaf}",
                    }
                )
    return configs


def blocked_seed_folds(seeds: np.ndarray) -> list[np.ndarray]:
    unique = np.unique(seeds)
    if len(unique) != 120:
        raise ValueError("blocked folds require exactly 120 seeds")
    return [np.isin(seeds, unique[start : start + 20]) for start in range(0, 120, 20)]


def opponent_folds(opponents: np.ndarray) -> list[np.ndarray]:
    return [opponents == opponent for opponent in OPPONENTS]


def ridge_predict(
    matrix: np.ndarray,
    targets: np.ndarray,
    train: np.ndarray,
    held: np.ndarray,
    alpha: float,
) -> np.ndarray:
    x_train = matrix[train]
    mean = x_train.mean(axis=0)
    scale = x_train.std(axis=0)
    scale[scale == 0] = 1.0
    standardized = (x_train - mean) / scale
    target_mean = targets[train].mean()
    centered = targets[train] - target_mean
    gram = standardized.T @ standardized
    gram.flat[:: gram.shape[0] + 1] += alpha
    try:
        coefficient = np.linalg.solve(gram, standardized.T @ centered)
    except np.linalg.LinAlgError:
        coefficient = np.linalg.lstsq(gram, standardized.T @ centered, rcond=None)[0]
    return target_mean + ((matrix[held] - mean) / scale) @ coefficient


def seed_bootstrap(indexes: np.ndarray, seeds: np.ndarray, rng) -> np.ndarray:
    unique = np.unique(seeds[indexes])
    sampled = rng.choice(unique, size=len(unique), replace=True)
    by_seed = {seed: indexes[seeds[indexes] == seed] for seed in unique}
    return np.concatenate([by_seed[seed] for seed in sampled])


def regression_leaf(targets: np.ndarray, indexes: np.ndarray) -> dict:
    values = targets[indexes]
    return {
        "feature": None,
        "prediction": float(values.mean()),
        "samples": int(len(indexes)),
    }


def candidate_positions(values: np.ndarray, min_leaf: int) -> np.ndarray:
    if len(values) < 2 * min_leaf:
        return np.empty(0, dtype=np.int64)
    return np.flatnonzero(values[:-1] < values[1:]) + 1


def fit_regression_tree(
    matrix: np.ndarray,
    targets: np.ndarray,
    indexes: np.ndarray,
    rng,
    config: dict,
    depth: int = 0,
) -> dict:
    leaf = regression_leaf(targets, indexes)
    if depth >= config["max_depth"] or len(indexes) < 2 * config["min_leaf"]:
        return leaf
    feature_count = matrix.shape[1]
    max_features = min(math.ceil(math.sqrt(feature_count)), feature_count)
    sampled_features = rng.choice(feature_count, size=max_features, replace=False)
    best = None
    for raw_feature in sampled_features:
        feature = int(raw_feature)
        values = matrix[indexes, feature]
        order = np.argsort(values, kind="mergesort")
        sorted_values = values[order]
        sorted_targets = targets[indexes[order]]
        positions = candidate_positions(sorted_values, config["min_leaf"])
        positions = positions[
            (positions >= config["min_leaf"])
            & (positions <= len(indexes) - config["min_leaf"])
        ]
        if not len(positions):
            continue
        if config["family"] == "extra_trees":
            positions = np.asarray([rng.choice(positions)])
        elif len(positions) > 16:
            choices = np.linspace(0, len(positions) - 1, 16).round().astype(int)
            positions = positions[np.unique(choices)]
        cumulative = np.cumsum(sorted_targets)
        cumulative_square = np.cumsum(sorted_targets * sorted_targets)
        total = cumulative[-1]
        total_square = cumulative_square[-1]
        left_n = positions.astype(np.float64)
        right_n = len(indexes) - left_n
        left_sum = cumulative[positions - 1]
        left_square = cumulative_square[positions - 1]
        right_sum = total - left_sum
        right_square = total_square - left_square
        loss = (
            left_square
            - left_sum * left_sum / left_n
            + right_square
            - right_sum * right_sum / right_n
        )
        choice = int(np.argmin(loss))
        position = int(positions[choice])
        threshold = float((sorted_values[position - 1] + sorted_values[position]) / 2)
        candidate = (float(loss[choice]), feature, threshold)
        if best is None or candidate < best:
            best = candidate
    if best is None:
        return leaf
    _, feature, threshold = best
    left_mask = matrix[indexes, feature] <= threshold
    if (
        np.count_nonzero(left_mask) < config["min_leaf"]
        or np.count_nonzero(~left_mask) < config["min_leaf"]
    ):
        return leaf
    return {
        "feature": feature,
        "threshold": threshold,
        "prediction": leaf["prediction"],
        "samples": leaf["samples"],
        "left": fit_regression_tree(
            matrix, targets, indexes[left_mask], rng, config, depth + 1
        ),
        "right": fit_regression_tree(
            matrix, targets, indexes[~left_mask], rng, config, depth + 1
        ),
    }


def tree_predict(tree: dict, matrix: np.ndarray, indexes: np.ndarray, output) -> None:
    if tree["feature"] is None:
        output[indexes] = tree["prediction"]
        return
    mask = matrix[indexes, tree["feature"]] <= tree["threshold"]
    tree_predict(tree["left"], matrix, indexes[mask], output)
    tree_predict(tree["right"], matrix, indexes[~mask], output)


def forest_predict_fold(
    matrix: np.ndarray,
    targets: np.ndarray,
    seeds: np.ndarray,
    train: np.ndarray,
    held: np.ndarray,
    config: dict,
    random_seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(random_seed)
    prediction = np.zeros(len(held), dtype=np.float64)
    for _ in range(config["trees"]):
        tree = fit_regression_tree(
            matrix,
            targets,
            seed_bootstrap(train, seeds, rng),
            rng,
            config,
        )
        tree_output = np.zeros(matrix.shape[0], dtype=np.float64)
        tree_predict(tree, matrix, held, tree_output)
        prediction += tree_output[held]
    return prediction / config["trees"]


def cross_validated_predictions(
    matrix: np.ndarray,
    targets: np.ndarray,
    seeds: np.ndarray,
    folds: list[np.ndarray],
    config: dict,
    scheme_offset: int,
) -> np.ndarray:
    predictions = np.zeros(len(targets), dtype=np.float64)
    covered = np.zeros(len(targets), dtype=bool)
    for fold_index, held_mask in enumerate(folds):
        train = np.flatnonzero(~held_mask)
        held = np.flatnonzero(held_mask)
        if config["family"] == "ridge":
            values = ridge_predict(
                matrix, targets, train, held, config["alpha"]
            )
        else:
            values = forest_predict_fold(
                matrix,
                targets,
                seeds,
                train,
                held,
                config,
                2501 + scheme_offset + fold_index * 100_003,
            )
        predictions[held] = values
        covered[held] = True
    if not np.all(covered):
        raise ValueError("cross-validation does not cover every row")
    return predictions


def seed_cluster(values: np.ndarray, seeds: np.ndarray) -> list[float]:
    return [float(values[seeds == seed].mean()) for seed in np.unique(seeds)]


def prediction_hash(values: np.ndarray) -> str:
    return hashlib.sha256(values.astype("<f8", copy=False).tobytes()).hexdigest()


def evaluate_policy(
    rows: list[dict], predictions: np.ndarray, buffer: float
) -> dict:
    selected = predictions > buffer
    deltas = np.asarray([row["margin_delta"] for row in rows], dtype=np.float64)
    score_deltas = np.asarray([row["score_delta"] for row in rows], dtype=np.float64)
    resident_margins = np.asarray(
        [row["resident_margin"] for row in rows], dtype=np.float64
    )
    option_margins = np.asarray(
        [row["option_margin"] for row in rows], dtype=np.float64
    )
    seeds = np.asarray([row["seed"] for row in rows], dtype=np.int64)
    opponents = np.asarray([row["opponent"] for row in rows], dtype=object)
    policy_deltas = np.where(selected, deltas, 0.0)
    policy_score_deltas = np.where(selected, score_deltas, 0.0)
    policy_margins = np.where(selected, option_margins, resident_margins)
    selected_count = int(np.count_nonzero(selected))
    positive_selected = int(np.count_nonzero(selected & (deltas > 0)))
    precision = positive_selected / selected_count if selected_count else 1.0
    seed_summary = robust_summary(seed_cluster(policy_deltas, seeds))
    score_summary = robust_summary(seed_cluster(policy_score_deltas, seeds))
    opponent_means = {
        opponent: float(policy_deltas[opponents == opponent].mean())
        for opponent in OPPONENTS
    }
    control_catastrophes = int(np.count_nonzero(resident_margins <= -100))
    policy_catastrophes = int(np.count_nonzero(policy_margins <= -100))
    control_mass = float(np.maximum(-resident_margins, 0).sum())
    policy_mass = float(np.maximum(-policy_margins, 0).sum())
    oracle_deltas = np.maximum(deltas, 0)
    oracle_mean = robust_summary(seed_cluster(oracle_deltas, seeds))["mean"]
    oracle_fraction = seed_summary["mean"] / oracle_mean if oracle_mean > 0 else None
    report = {
        "buffer": buffer,
        "prediction_hash": prediction_hash(predictions),
        "selected_cells": selected_count,
        "selection_rate": float(selected.mean()),
        "selected_positive": positive_selected,
        "selected_negative": int(np.count_nonzero(selected & (deltas < 0))),
        "selected_ties": int(np.count_nonzero(selected & (deltas == 0))),
        "precision": precision,
        "seed_clustered_margin_delta": seed_summary,
        "seed_clustered_own_score_delta": score_summary,
        "opponent_mean_margin_deltas": opponent_means,
        "nonnegative_opponent_means": sum(value >= 0 for value in opponent_means.values()),
        "worst_opponent": min(opponent_means, key=opponent_means.get),
        "worst_opponent_mean_delta": min(opponent_means.values()),
        "tail": {
            "control_catastrophic_frequency": control_catastrophes / len(rows),
            "selected_policy_catastrophic_frequency": policy_catastrophes / len(rows),
            "control_negative_margin_mass": control_mass,
            "selected_policy_negative_margin_mass": policy_mass,
            "negative_mass_ratio": policy_mass / control_mass if control_mass else None,
        },
        "positive_cell_oracle_seed_clustered_mean": oracle_mean,
        "oracle_fraction": oracle_fraction,
    }
    report["gates"] = {
        "selection_rate_5_to_60pct": 0.05 <= report["selection_rate"] <= 0.60,
        "precision_at_least_75pct": precision >= 0.75,
        "mean_margin_at_least_5": seed_summary["mean"] >= 5,
        "trimmed_margin_at_least_3": seed_summary["trimmed_5pct_mean"] >= 3,
        "ci_lower_above_zero": seed_summary["ci95_normal"][0] > 0,
        "six_of_eight_opponents_nonnegative": report["nonnegative_opponent_means"] >= 6,
        "worst_opponent_at_least_minus_5": report["worst_opponent_mean_delta"] >= -5,
        "catastrophic_frequency_not_higher": policy_catastrophes <= control_catastrophes,
        "negative_margin_mass_not_higher": policy_mass <= control_mass,
        "oracle_fraction_at_least_20pct": oracle_fraction is not None
        and oracle_fraction >= 0.20,
    }
    report["passed"] = all(report["gates"].values())
    return report


def complexity_key(config: dict) -> tuple:
    if config["family"] == "ridge":
        return (0, 0, 0, config["label"])
    return (
        config["max_depth"],
        -config["min_leaf"],
        0 if config["family"] == "extra_trees" else 1,
        config["label"],
    )


def candidate_rank(report: dict) -> tuple:
    blocked = report["blocked_seed_cv"]
    family = report["held_opponent_family_cv"]
    return (
        report["passed"],
        min(
            blocked["worst_opponent_mean_delta"],
            family["worst_opponent_mean_delta"],
        ),
        min(
            blocked["seed_clustered_margin_delta"]["mean"],
            family["seed_clustered_margin_delta"]["mean"],
        ),
        -max(blocked["selection_rate"], family["selection_rate"]),
        tuple(-value if isinstance(value, (int, float)) else value for value in complexity_key(report["config"])),
        report["buffer"],
        report["label"],
    )


def evaluate_config(payload) -> dict:
    matrix, targets, seeds, opponents, rows, config, config_index = payload
    blocked_predictions = cross_validated_predictions(
        matrix,
        targets,
        seeds,
        blocked_seed_folds(seeds),
        config,
        config_index * 1_000_003,
    )
    family_predictions = cross_validated_predictions(
        matrix,
        targets,
        seeds,
        opponent_folds(opponents),
        config,
        50_000_000 + config_index * 1_000_003,
    )
    reports = []
    for buffer in BUFFERS:
        blocked = evaluate_policy(rows, blocked_predictions, buffer)
        family = evaluate_policy(rows, family_predictions, buffer)
        reports.append(
            {
                "label": f"{config['label']}_b{int(buffer)}",
                "config": config,
                "buffer": buffer,
                "blocked_seed_cv": blocked,
                "held_opponent_family_cv": family,
                "passed": blocked["passed"] and family["passed"],
            }
        )
    reports.sort(key=candidate_rank, reverse=True)
    return {"config": config, "best": reports[0], "buffers": reports}


def fit_full_model(
    matrix: np.ndarray,
    targets: np.ndarray,
    seeds: np.ndarray,
    config: dict,
) -> dict:
    indexes = np.arange(len(targets))
    if config["family"] == "ridge":
        mean = matrix.mean(axis=0)
        scale = matrix.std(axis=0)
        scale[scale == 0] = 1.0
        standardized = (matrix - mean) / scale
        target_mean = targets.mean()
        gram = standardized.T @ standardized
        gram.flat[:: gram.shape[0] + 1] += config["alpha"]
        coefficient = np.linalg.solve(
            gram, standardized.T @ (targets - target_mean)
        )
        return {
            "family": "ridge",
            "alpha": config["alpha"],
            "feature_mean": mean.tolist(),
            "feature_scale": scale.tolist(),
            "target_mean": float(target_mean),
            "coefficient": coefficient.tolist(),
        }
    rng = np.random.default_rng(2501 + 900_000_000)
    trees = [
        fit_regression_tree(
            matrix,
            targets,
            seed_bootstrap(indexes, seeds, rng),
            rng,
            config,
        )
        for _ in range(config["trees"])
    ]
    return {"family": config["family"], "config": config, "trees": trees}


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--labels", type=Path, action="append", required=True)
    parser.add_argument("--smoke", type=Path, required=True)
    parser.add_argument("--smoke-repeat", type=Path, required=True)
    parser.add_argument("--jobs", type=int, default=min(os.cpu_count() or 1, 20))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    feature_rows, feature_names = read_features(args.features)
    labels = read_label_paths(args.labels)
    rows, matrix, varying_names, integrity = prepare(
        feature_rows, feature_names, labels
    )
    smoke_identical = args.smoke.read_bytes() == args.smoke_repeat.read_bytes()
    integrity["smoke_byte_identical"] = smoke_identical
    integrity["passed"] &= smoke_identical
    if not integrity["passed"]:
        payload = {
            "schema": 1,
            "integrity": integrity,
            "decision": {"fit_models": False, "open_prospective": False},
        }
        save(args.output, payload)
        print(json.dumps(payload, indent=1))
        return 1

    targets = np.asarray([row["margin_delta"] for row in rows], dtype=np.float64)
    seeds = np.asarray([row["seed"] for row in rows], dtype=np.int64)
    opponents = np.asarray([row["opponent"] for row in rows], dtype=object)
    configs = model_configs()
    payloads = [
        (matrix, targets, seeds, opponents, rows, config, index)
        for index, config in enumerate(configs)
    ]
    if args.jobs == 1:
        reports = [evaluate_config(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(max_workers=min(args.jobs, len(payloads))) as pool:
            reports = list(pool.map(evaluate_config, payloads))
    candidates = [candidate for report in reports for candidate in report["buffers"]]
    candidates.sort(key=candidate_rank, reverse=True)
    passing = [candidate for candidate in candidates if candidate["passed"]]
    selected = passing[0] if passing else None

    shuffle = list(reversed(feature_rows))
    shuffled_rows, shuffled_matrix, shuffled_names, shuffled_integrity = prepare(
        shuffle, feature_names, labels
    )
    structural_shuffle_equal = (
        [row_key(row) for row in rows] == [row_key(row) for row in shuffled_rows]
        and varying_names == shuffled_names
        and np.array_equal(matrix, shuffled_matrix)
        and np.array_equal(
            targets,
            np.asarray(
                [row["margin_delta"] for row in shuffled_rows], dtype=np.float64
            ),
        )
        and shuffled_integrity["passed"]
    )
    shuffle_prediction_equal = None
    full_model = None
    if selected:
        selected_index = configs.index(selected["config"])
        repeated = evaluate_config(
            (
                shuffled_matrix,
                targets,
                seeds,
                opponents,
                shuffled_rows,
                selected["config"],
                selected_index,
            )
        )
        matching = next(
            item for item in repeated["buffers"] if item["buffer"] == selected["buffer"]
        )
        shuffle_prediction_equal = all(
            selected[scheme]["prediction_hash"] == matching[scheme]["prediction_hash"]
            for scheme in ("blocked_seed_cv", "held_opponent_family_cv")
        ) and selected["passed"] == matching["passed"]
        full_model = fit_full_model(matrix, targets, seeds, selected["config"])
    integrity["row_order_structurally_identical"] = structural_shuffle_equal
    integrity["selected_oof_predictions_shuffle_identical"] = shuffle_prediction_equal
    integrity["passed"] &= structural_shuffle_equal and (
        shuffle_prediction_equal is not False
    )

    oracle = evaluate_policy(rows, targets, 0)
    result = {
        "schema": 1,
        "scope": (
            "D25 development-only observable turn-75 resident/ownership2 value selector; "
            "blocked-map and held-opponent-family out-of-fold evaluation"
        ),
        "features": str(args.features),
        "labels": [str(path) for path in args.labels],
        "integrity": integrity,
        "cells": len(rows),
        "seeds": len(np.unique(seeds)),
        "feature_count": len(varying_names),
        "feature_names": varying_names,
        "positive_cells": int(np.count_nonzero(targets > 0)),
        "positive_cell_rate": float(np.mean(targets > 0)),
        "model_configurations": len(configs),
        "model_buffer_configurations": len(candidates),
        "passing_configurations": len(passing),
        "selected": selected,
        "top_configurations": candidates[:20],
        "positive_cell_oracle": oracle,
        "full_model": full_model,
        "decision": {
            "open_prospective_seeds_50120_50179": integrity["passed"]
            and selected is not None,
            "build_candidate": False,
            "submit": False,
        },
    }
    save(args.output, result)
    compact = {
        "integrity": integrity,
        "cells": result["cells"],
        "feature_count": result["feature_count"],
        "positive_cells": result["positive_cells"],
        "configurations": result["model_buffer_configurations"],
        "passing": result["passing_configurations"],
        "selected": selected,
        "oracle_mean": oracle["seed_clustered_margin_delta"]["mean"],
        "decision": result["decision"],
    }
    print(json.dumps(compact, indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
