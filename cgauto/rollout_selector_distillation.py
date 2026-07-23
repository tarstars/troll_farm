#!/usr/bin/env python3
"""Distill the frozen CompactGold rollout guard into turn-one map features."""

from __future__ import annotations

import argparse
from collections import deque
import csv
import json
import math
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.local_model_rollout_transfer import (  # noqa: E402
    atomic_write,
    league_outcomes,
)
from cgauto.offline_policy_league import robust_summary  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

KINDS = ("PLUM", "LEMON", "APPLE", "BANANA")


def bfs(walkable: set[tuple[int, int]], sources) -> dict[tuple[int, int], int]:
    distance = {}
    queue = deque()
    for cell in sources:
        if cell in walkable and cell not in distance:
            distance[cell] = 0
            queue.append(cell)
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            cell = (x + dx, y + dy)
            if cell in walkable and cell not in distance:
                distance[cell] = distance[(x, y)] + 1
                queue.append(cell)
    return distance


def neighbors(cell: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    x, y = cell
    return ((x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y))


def max_level(inventory: int) -> int:
    available = max(inventory - 1, 0)
    level = 0
    while level < 3 and (level + 1) ** 2 <= available:
        level += 1
    return max(level, 1)


def safe_min(values, default: float = 99.0) -> float:
    values = list(values)
    return min(values) if values else default


def safe_mean(values, default: float = 99.0) -> float:
    values = list(values)
    return statistics.mean(values) if values else default


def turn_one_features(game, seat: int) -> dict[str, float]:
    own = seat
    enemy = 1 - seat
    own_shack = game.shacks[own]
    enemy_shack = game.shacks[enemy]
    own_doors = [cell for cell in neighbors(own_shack) if cell in game.walkable]
    enemy_doors = [cell for cell in neighbors(enemy_shack) if cell in game.walkable]
    own_distance = bfs(game.walkable, own_doors)
    enemy_distance = bfs(game.walkable, enemy_doors)
    features: dict[str, float] = {
        "tree_count": len(game.plants),
        "ripe_tree_count": sum(plant.fruits > 0 for plant in game.plants),
        "fruit_total": sum(plant.fruits for plant in game.plants),
        "shack_manhattan": abs(own_shack[0] - enemy_shack[0])
        + abs(own_shack[1] - enemy_shack[1]),
        "own_door_count": len(own_doors),
        "enemy_door_count": len(enemy_doors),
        "water_count": len(game.water),
        "iron_count": len(game.iron),
    }
    for item, name in enumerate(("plum", "lemon", "apple", "banana", "iron")):
        own_value = game.inventories[own][item]
        enemy_value = game.inventories[enemy][item]
        features[f"own_{name}"] = own_value
        features[f"enemy_{name}"] = enemy_value
        features[f"delta_{name}"] = own_value - enemy_value
        if item in (0, 1, 2, 4):
            features[f"level_{name}"] = max_level(own_value)
    features["option_cost"] = sum(
        1 + features[f"level_{name}"] ** 2
        for name in ("plum", "lemon", "iron")
    ) + 1

    for kind in KINDS:
        prefix = kind.lower()
        plants = [plant for plant in game.plants if plant.type == kind]
        own_distances = [own_distance.get(plant.pos, 99) for plant in plants]
        enemy_distances = [enemy_distance.get(plant.pos, 99) for plant in plants]
        ripe = [plant for plant in plants if plant.fruits > 0]
        features[f"{prefix}_count"] = len(plants)
        features[f"{prefix}_ripe"] = len(ripe)
        features[f"{prefix}_fruit"] = sum(plant.fruits for plant in plants)
        features[f"{prefix}_own_min"] = safe_min(own_distances)
        features[f"{prefix}_own_mean"] = safe_mean(own_distances)
        features[f"{prefix}_enemy_min"] = safe_min(enemy_distances)
        features[f"{prefix}_enemy_mean"] = safe_mean(enemy_distances)
        features[f"{prefix}_ripe_own_min"] = safe_min(
            own_distance.get(plant.pos, 99) for plant in ripe
        )
        features[f"{prefix}_own_half"] = sum(
            own_distance.get(plant.pos, 99) <= enemy_distance.get(plant.pos, 99)
            for plant in plants
        )
        features[f"{prefix}_near3"] = sum(
            own_distance.get(plant.pos, 99) <= 3 for plant in plants
        )
        features[f"{prefix}_near6"] = sum(
            own_distance.get(plant.pos, 99) <= 6 for plant in plants
        )
        features[f"{prefix}_water_adjacent"] = sum(
            any(abs(plant.x - x) + abs(plant.y - y) == 1 for x, y in game.water)
            for plant in plants
        )

    all_own = [own_distance.get(plant.pos, 99) for plant in game.plants]
    all_enemy = [enemy_distance.get(plant.pos, 99) for plant in game.plants]
    features["tree_own_min"] = safe_min(all_own)
    features["tree_own_mean"] = safe_mean(all_own)
    features["tree_own_max"] = max(all_own, default=99)
    features["tree_enemy_mean"] = safe_mean(all_enemy)
    features["tree_own_half"] = sum(
        left <= right for left, right in zip(all_own, all_enemy, strict=True)
    )
    features["tree_distance_advantage"] = sum(
        right - left for left, right in zip(all_own, all_enemy, strict=True)
    )
    features["water_adjacent_tree_count"] = sum(
        any(abs(plant.x - x) + abs(plant.y - y) == 1 for x, y in game.water)
        for plant in game.plants
    )
    features["own_water_door_count"] = sum(
        any(abs(cell[0] - x) + abs(cell[1] - y) == 1 for x, y in game.water)
        for cell in own_doors
    )
    features["empty_water_door_count"] = sum(
        not any(plant.pos == cell for plant in game.plants)
        and any(abs(cell[0] - x) + abs(cell[1] - y) == 1 for x, y in game.water)
        for cell in own_doors
    )
    features["orchard_candidate_count"] = sum(
        not any(plant.pos == cell for plant in game.plants)
        and any(abs(cell[0] - x) + abs(cell[1] - y) == 1 for x, y in game.water)
        and enemy_distance.get(cell, 99) >= 11
        for cell in own_doors
    )
    features["iron_own_min"] = safe_min(
        own_distance.get(cell, 99)
        for iron in game.iron
        for cell in neighbors(iron)
        if cell in game.walkable
    )
    features["iron_enemy_min"] = safe_min(
        enemy_distance.get(cell, 99)
        for iron in game.iron
        for cell in neighbors(iron)
        if cell in game.walkable
    )
    return features


def read_labels(paths: list[Path], threshold: float) -> dict[tuple[int, int], float]:
    labels = {}
    for path in paths:
        with path.open(newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                if row["model"] not in {"compact_gold", "gold_elite"}:
                    continue
                key = (int(row["seed"]), int(row["seat"]))
                if key in labels:
                    raise ValueError(f"duplicate rollout label {key}")
                labels[key] = float(row["delta"])
    return labels


def weighted_gini(positive: int, negative: int, negative_weight: float) -> float:
    positive_weight = positive
    negative_total = negative_weight * negative
    total = positive_weight + negative_total
    if total == 0:
        return 0.0
    probability = positive_weight / total
    return total * 2 * probability * (1 - probability)


def fit_tree(
    keys: list[tuple[int, int]],
    features: dict[tuple[int, int], dict[str, float]],
    labels: dict[tuple[int, int], bool],
    max_depth: int,
    min_leaf: int,
    negative_weight: float,
    min_positive_leaf: int = 2,
    depth: int = 0,
) -> dict:
    positive = sum(labels[key] for key in keys)
    negative = len(keys) - positive
    predict_positive = (
        positive >= min_positive_leaf and positive > negative_weight * negative
    )
    leaf = {
        "feature": None,
        "prediction": predict_positive,
        "positive": positive,
        "negative": negative,
    }
    if depth >= max_depth or positive == 0 or negative == 0 or len(keys) < 2 * min_leaf:
        return leaf
    parent_impurity = weighted_gini(positive, negative, negative_weight)
    best = None
    for feature in sorted(next(iter(features.values()))):
        ordered = sorted(keys, key=lambda key: (features[key][feature], key))
        left_positive = 0
        left_negative = 0
        for index in range(len(ordered) - 1):
            key = ordered[index]
            if labels[key]:
                left_positive += 1
            else:
                left_negative += 1
            if index + 1 < min_leaf or len(ordered) - index - 1 < min_leaf:
                continue
            left_value = features[key][feature]
            right_value = features[ordered[index + 1]][feature]
            if left_value == right_value:
                continue
            right_positive = positive - left_positive
            right_negative = negative - left_negative
            impurity = weighted_gini(
                left_positive, left_negative, negative_weight
            ) + weighted_gini(right_positive, right_negative, negative_weight)
            gain = parent_impurity - impurity
            candidate = (gain, feature, (left_value + right_value) / 2, index)
            if best is None or candidate[:3] > best[:3]:
                best = candidate
    if best is None or best[0] <= 0:
        return leaf
    _, feature, threshold, split_index = best
    ordered = sorted(keys, key=lambda key: (features[key][feature], key))
    left = ordered[: split_index + 1]
    right = ordered[split_index + 1 :]
    return {
        "feature": feature,
        "threshold": threshold,
        "positive": positive,
        "negative": negative,
        "left": fit_tree(
            left,
            features,
            labels,
            max_depth,
            min_leaf,
            negative_weight,
            min_positive_leaf,
            depth + 1,
        ),
        "right": fit_tree(
            right,
            features,
            labels,
            max_depth,
            min_leaf,
            negative_weight,
            min_positive_leaf,
            depth + 1,
        ),
    }


def predict(tree: dict, row: dict[str, float]) -> bool:
    while tree["feature"] is not None:
        tree = tree["left"] if row[tree["feature"]] <= tree["threshold"] else tree["right"]
    return tree["prediction"]


def confusion(truth: dict, predictions: dict) -> dict:
    tp = sum(truth[key] and predictions[key] for key in truth)
    fp = sum(not truth[key] and predictions[key] for key in truth)
    fn = sum(truth[key] and not predictions[key] for key in truth)
    tn = len(truth) - tp - fp - fn
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    beta = 0.5
    f_beta = (
        (1 + beta**2) * precision * recall / (beta**2 * precision + recall)
        if precision + recall
        else 0.0
    )
    return {
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "true_negative": tn,
        "precision": precision,
        "recall": recall,
        "f0_5": f_beta,
    }


def leaf_count(tree: dict) -> int:
    if tree["feature"] is None:
        return 1
    return leaf_count(tree["left"]) + leaf_count(tree["right"])


def blocked_cross_validation(keys, features, labels, config, block_count=10) -> dict:
    seeds = sorted({seed for seed, _ in keys})
    seed_block = {
        seed: min(index * block_count // len(seeds), block_count - 1)
        for index, seed in enumerate(seeds)
    }
    predictions = {}
    for block in range(block_count):
        train = [key for key in keys if seed_block[key[0]] != block]
        test = [key for key in keys if seed_block[key[0]] == block]
        tree = fit_tree(train, features, labels, **config)
        predictions.update({key: predict(tree, features[key]) for key in test})
    return confusion(labels, predictions)


def choose_config(keys, features, labels) -> tuple[dict, list[dict]]:
    reports = []
    for max_depth in (2, 3, 4, 5):
        for min_leaf in (4, 8, 16):
            for negative_weight in (2.0, 4.0, 8.0, 12.0):
                config = {
                    "max_depth": max_depth,
                    "min_leaf": min_leaf,
                    "negative_weight": negative_weight,
                }
                report = blocked_cross_validation(keys, features, labels, config)
                reports.append({"config": config, "cross_validation": report})
    reports.sort(
        key=lambda report: (
            report["cross_validation"]["f0_5"],
            report["cross_validation"]["precision"],
            report["cross_validation"]["recall"],
            -report["config"]["max_depth"],
            report["config"]["min_leaf"],
            report["config"]["negative_weight"],
        ),
        reverse=True,
    )
    return reports[0]["config"], reports


def actual_evaluation(
    seeds,
    opponents,
    outcomes,
    predictions: dict[tuple[int, int], bool],
) -> dict:
    seed_values = []
    for seed in seeds:
        seed_values.append(
            statistics.mean(
                statistics.mean(outcomes[(seed, seat)].values())
                if predictions[(seed, seat)]
                else 0.0
                for seat in (0, 1)
            )
        )
    opponent_means = {
        opponent: statistics.mean(
            statistics.mean(
                outcomes[(seed, seat)][opponent]
                if predictions[(seed, seat)]
                else 0.0
                for seat in (0, 1)
            )
            for seed in seeds
        )
        for opponent in opponents
    }
    return {
        "selected_cell_count": sum(predictions.values()),
        "selected_cells": [
            {"seed": seed, "seat": seat}
            for seed, seat in sorted(predictions)
            if predictions[(seed, seat)]
        ],
        "seed_clustered_summary": robust_summary(seed_values),
        "opponent_means": opponent_means,
        "worst_opponent_mean": min(opponent_means.values()),
    }


def rust_expression(tree: dict) -> str:
    if tree["feature"] is None:
        return "true" if tree["prediction"] else "false"
    left = rust_expression(tree["left"])
    right = rust_expression(tree["right"])
    return (
        f"if f.{tree['feature']}<={tree['threshold']:.6g}"
        f"{{{left}}}else{{{right}}}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-rollouts", type=Path, action="append", required=True)
    parser.add_argument("--test-rollouts", type=Path, required=True)
    parser.add_argument("--test-league", type=Path, required=True)
    parser.add_argument("--policy", default="adaptivehp0")
    parser.add_argument("--threshold", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    train_deltas = read_labels(args.train_rollouts, args.threshold)
    test_deltas = read_labels([args.test_rollouts], args.threshold)
    overlap = set(train_deltas) & set(test_deltas)
    if overlap:
        raise SystemExit(f"train/test rollout overlap: {sorted(overlap)[:5]}")
    all_keys = sorted(set(train_deltas) | set(test_deltas))
    features = {
        key: turn_one_features(generate_bronze(key[0]), key[1]) for key in all_keys
    }
    train_truth = {key: value > args.threshold for key, value in train_deltas.items()}
    test_truth = {key: value > args.threshold for key, value in test_deltas.items()}
    config, config_reports = choose_config(
        sorted(train_truth), features, train_truth
    )
    tree = fit_tree(sorted(train_truth), features, train_truth, **config)
    train_predictions = {
        key: predict(tree, features[key]) for key in train_truth
    }
    test_predictions = {
        key: predict(tree, features[key]) for key in test_truth
    }
    seeds, opponents, outcomes = league_outcomes(
        [args.test_league], args.policy, {"motion"}
    )
    if set(test_predictions) != set(outcomes):
        raise SystemExit("test rollouts do not match test league cells")
    direct_predictions = {key: truth for key, truth in test_truth.items()}
    payload = {
        "schema": 1,
        "scope": (
            "blocked-CV distillation of the frozen CompactGold >30 rollout decision; "
            "test seeds excluded from training labels and model selection"
        ),
        "threshold": args.threshold,
        "train_rollouts": [str(path) for path in args.train_rollouts],
        "test_rollouts": str(args.test_rollouts),
        "test_league": str(args.test_league),
        "training_cells": len(train_truth),
        "training_positive_cells": sum(train_truth.values()),
        "test_cells": len(test_truth),
        "test_positive_cells": sum(test_truth.values()),
        "selected_config": config,
        "selected_config_cross_validation": config_reports[0]["cross_validation"],
        "config_reports": config_reports,
        "tree": tree,
        "leaf_count": leaf_count(tree),
        "rust_expression": rust_expression(tree),
        "fit_confusion": confusion(train_truth, train_predictions),
        "test_imitation_confusion": confusion(test_truth, test_predictions),
        "test_actual_distilled": actual_evaluation(
            seeds, opponents, outcomes, test_predictions
        ),
        "test_actual_direct_rollout": actual_evaluation(
            seeds, opponents, outcomes, direct_predictions
        ),
        "interpretation_limit": (
            "The tree imitates a local rollout guard. Its test outcome is offline evidence, "
            "not an arena estimate; no post-test tree or threshold tuning is permitted."
        ),
    }
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(
        json.dumps(
            {
                key: payload[key]
                for key in (
                    "training_cells",
                    "training_positive_cells",
                    "test_cells",
                    "test_positive_cells",
                    "selected_config",
                    "selected_config_cross_validation",
                    "leaf_count",
                    "rust_expression",
                    "fit_confusion",
                    "test_imitation_confusion",
                    "test_actual_distilled",
                    "test_actual_direct_rollout",
                )
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
