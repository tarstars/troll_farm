#!/usr/bin/env python3
"""Evaluate a small turn-one option selector with blocked nested validation."""

from __future__ import annotations

import argparse
from collections import Counter
import itertools
import json
import math
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.offline_policy_league import robust_summary  # noqa: E402


BANK_FEATURES = (
    "initial_plum",
    "initial_lemon",
    "initial_apple",
    "initial_iron",
    "affordable_movement",
    "affordable_carry",
    "affordable_harvest",
    "affordable_chop",
    "max_bank_cell_122",
)

GEOMETRY_FEATURES = BANK_FEATURES + (
    "tree_count",
    "ripe_tree_count",
    "initial_fruit_total",
    "water_adjacent_tree_count",
    "mean_nearest_shack_tree_distance",
    "max_nearest_shack_tree_distance",
    "shack_manhattan_distance",
    "plum_tree_count",
    "lemon_tree_count",
    "apple_tree_count",
    "banana_tree_count",
    "plum_fruit_count",
    "lemon_fruit_count",
    "apple_fruit_count",
    "banana_fruit_count",
)


def max_affordable_level(inventory: int, cap: int = 3) -> int:
    available = max(inventory - 1, 0)
    level = 0
    while level < cap and (level + 1) ** 2 <= available:
        level += 1
    return max(level, 1)


def selector_features(payload: dict) -> dict[int, dict[str, float]]:
    features = {}
    for raw_seed, raw_row in payload["map_features"].items():
        row = dict(raw_row)
        row["affordable_movement"] = max_affordable_level(row["initial_plum"])
        row["affordable_carry"] = max_affordable_level(row["initial_lemon"])
        row["affordable_harvest"] = max_affordable_level(row["initial_apple"])
        row["affordable_chop"] = max_affordable_level(row["initial_iron"])
        row["max_bank_cell_122"] = float(
            row["affordable_movement"] == 1
            and row["affordable_carry"] == 2
            and row["affordable_harvest"] == 2
        )
        features[int(raw_seed)] = row
    return features


def option_outcomes(
    payload: dict, option: str, opponents: tuple[str, ...]
) -> tuple[dict[int, float], dict[int, dict[str, float]]]:
    grouped = {}
    for row in payload["rows"]:
        if row["policy"] != option or row["opponent"] not in opponents:
            continue
        key = (row["seed"], row["opponent"])
        if key in grouped:
            raise ValueError(f"duplicate option cell {key}")
        grouped[key] = row["delta_vs_live_margin"]
    seeds = sorted({seed for seed, _ in grouped})
    by_opponent = {
        seed: {opponent: grouped[(seed, opponent)] for opponent in opponents}
        for seed in seeds
    }
    outcomes = {
        seed: statistics.mean(by_opponent[seed].values()) for seed in seeds
    }
    return outcomes, by_opponent


def contiguous_blocks(seeds: list[int], count: int) -> dict[int, int]:
    if not 3 <= count <= len(seeds):
        raise ValueError("block count must be between three and the number of seeds")
    ordered = sorted(seeds)
    return {
        seed: min(index * count // len(ordered), count - 1)
        for index, seed in enumerate(ordered)
    }


def weighted_delta(value: float, loss_weight: float) -> float:
    return value if value >= 0 else loss_weight * value


def leaf_select(seeds: list[int], outcomes: dict[int, float], loss_weight: float) -> bool:
    return statistics.mean(weighted_delta(outcomes[seed], loss_weight) for seed in seeds) > 0


def predict(model: dict, feature_row: dict[str, float]) -> bool:
    if model["feature"] is None:
        return model["left_select"]
    if feature_row[model["feature"]] <= model["threshold"]:
        return model["left_select"]
    return model["right_select"]


def fit_stump(
    train_seeds: list[int],
    features: dict[int, dict[str, float]],
    outcomes: dict[int, float],
    feature_names: tuple[str, ...],
    min_leaf_fraction: float,
    loss_weight: float,
) -> dict:
    min_leaf = max(3, math.ceil(min_leaf_fraction * len(train_seeds)))
    global_select = leaf_select(train_seeds, outcomes, loss_weight)
    candidates = [
        {
            "feature": None,
            "threshold": None,
            "left_select": global_select,
            "right_select": global_select,
            "left_n": len(train_seeds),
            "right_n": 0,
        }
    ]
    for feature in feature_names:
        values = sorted({features[seed][feature] for seed in train_seeds})
        for left_value, right_value in zip(values, values[1:]):
            threshold = (left_value + right_value) / 2
            left = [
                seed for seed in train_seeds if features[seed][feature] <= threshold
            ]
            right = [seed for seed in train_seeds if seed not in set(left)]
            if min(len(left), len(right)) < min_leaf:
                continue
            left_select = leaf_select(left, outcomes, loss_weight)
            right_select = leaf_select(right, outcomes, loss_weight)
            if left_select == right_select:
                continue
            candidates.append(
                {
                    "feature": feature,
                    "threshold": threshold,
                    "left_select": left_select,
                    "right_select": right_select,
                    "left_n": len(left),
                    "right_n": len(right),
                }
            )
    for model in candidates:
        selected = [
            outcomes[seed] if predict(model, features[seed]) else 0.0
            for seed in train_seeds
        ]
        model["train_mean"] = statistics.mean(selected)
        model["train_weighted_mean"] = statistics.mean(
            weighted_delta(value, loss_weight) for value in selected
        )
        model["train_worst_decile"] = robust_summary(selected)["worst_decile_mean"]
        model["train_activations"] = sum(
            predict(model, features[seed]) for seed in train_seeds
        )
    candidates.sort(
        key=lambda model: (
            model["train_weighted_mean"],
            model["train_mean"],
            model["train_worst_decile"],
            -model["train_activations"],
            model["feature"] is None,
            model["feature"] or "",
        ),
        reverse=True,
    )
    return candidates[0]


def evaluate_predictions(
    seeds: list[int],
    predictions: dict[int, bool],
    outcomes: dict[int, float],
    by_opponent: dict[int, dict[str, float]],
    opponents: tuple[str, ...],
) -> dict:
    values = [outcomes[seed] if predictions[seed] else 0.0 for seed in seeds]
    opponent_means = {
        opponent: statistics.mean(
            by_opponent[seed][opponent] if predictions[seed] else 0.0
            for seed in seeds
        )
        for opponent in opponents
    }
    leave_one_out = [
        statistics.mean(value for index, value in enumerate(values) if index != removed)
        for removed in range(len(values))
    ]
    return {
        "summary": robust_summary(values),
        "activation_count": sum(predictions.values()),
        "activation_rate": statistics.mean(predictions.values()),
        "activated_summary": robust_summary(
            outcomes[seed] for seed in seeds if predictions[seed]
        ),
        "opponent_means": opponent_means,
        "worst_opponent_mean": min(opponent_means.values()),
        "leave_one_seed_out_minimum_mean": min(leave_one_out),
        "selected_seeds": [seed for seed in seeds if predictions[seed]],
    }


def config_grid() -> list[dict]:
    return [
        {
            "feature_set": feature_set,
            "min_leaf_fraction": min_leaf,
            "loss_weight": loss_weight,
        }
        for feature_set, min_leaf, loss_weight in itertools.product(
            ("bank", "bank_geometry"),
            (0.10, 0.20, 0.30),
            (1.0, 1.5, 2.0),
        )
    ]


def names_for_config(config: dict) -> tuple[str, ...]:
    return BANK_FEATURES if config["feature_set"] == "bank" else GEOMETRY_FEATURES


def select_config(
    seeds: list[int],
    blocks: dict[int, int],
    features: dict[int, dict[str, float]],
    outcomes: dict[int, float],
    by_opponent: dict[int, dict[str, float]],
    opponents: tuple[str, ...],
) -> tuple[dict, list[dict]]:
    block_ids = sorted({blocks[seed] for seed in seeds})
    results = []
    for config in config_grid():
        predictions = {}
        for held in block_ids:
            inner_test = [seed for seed in seeds if blocks[seed] == held]
            inner_train = [seed for seed in seeds if blocks[seed] != held]
            if not inner_train or not inner_test:
                continue
            model = fit_stump(
                inner_train,
                features,
                outcomes,
                names_for_config(config),
                config["min_leaf_fraction"],
                config["loss_weight"],
            )
            predictions.update(
                {seed: predict(model, features[seed]) for seed in inner_test}
            )
        evaluation = evaluate_predictions(
            seeds, predictions, outcomes, by_opponent, opponents
        )
        selected_values = [
            outcomes[seed] if predictions[seed] else 0.0 for seed in seeds
        ]
        result = dict(config)
        result.update(
            {
                "validation_mean": evaluation["summary"]["mean"],
                "validation_weighted_mean": statistics.mean(
                    weighted_delta(value, config["loss_weight"])
                    for value in selected_values
                ),
                "validation_worst_decile": evaluation["summary"][
                    "worst_decile_mean"
                ],
                "validation_worst_opponent": evaluation["worst_opponent_mean"],
                "validation_activations": evaluation["activation_count"],
            }
        )
        results.append(result)
    results.sort(
        key=lambda row: (
            row["validation_weighted_mean"],
            row["validation_worst_opponent"],
            row["validation_mean"],
            row["validation_worst_decile"],
            row["feature_set"] == "bank",
            row["min_leaf_fraction"],
            row["loss_weight"],
        ),
        reverse=True,
    )
    return results[0], results


def nested_blocked_selector(
    seeds: list[int],
    block_count: int,
    features: dict[int, dict[str, float]],
    outcomes: dict[int, float],
    by_opponent: dict[int, dict[str, float]],
    opponents: tuple[str, ...],
) -> dict:
    blocks = contiguous_blocks(seeds, block_count)
    predictions = {}
    folds = []
    for outer_block in range(block_count):
        outer_test = [seed for seed in seeds if blocks[seed] == outer_block]
        outer_train = [seed for seed in seeds if blocks[seed] != outer_block]
        config, _ = select_config(
            outer_train,
            blocks,
            features,
            outcomes,
            by_opponent,
            opponents,
        )
        model = fit_stump(
            outer_train,
            features,
            outcomes,
            names_for_config(config),
            config["min_leaf_fraction"],
            config["loss_weight"],
        )
        fold_predictions = {
            seed: predict(model, features[seed]) for seed in outer_test
        }
        predictions.update(fold_predictions)
        folds.append(
            {
                "outer_block": outer_block,
                "train_seeds": outer_train,
                "test_seeds": outer_test,
                "config": config,
                "model": model,
                "selected_test_seeds": [
                    seed for seed in outer_test if fold_predictions[seed]
                ],
            }
        )
    final_config, config_ranking = select_config(
        seeds, blocks, features, outcomes, by_opponent, opponents
    )
    final_model = fit_stump(
        seeds,
        features,
        outcomes,
        names_for_config(final_config),
        final_config["min_leaf_fraction"],
        final_config["loss_weight"],
    )
    return {
        "evaluation": evaluate_predictions(
            seeds, predictions, outcomes, by_opponent, opponents
        ),
        "predictions": {str(seed): predictions[seed] for seed in seeds},
        "folds": folds,
        "final_config": final_config,
        "final_model": final_model,
        "config_ranking": config_ranking,
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--option", default="adaptivehp0")
    parser.add_argument("--exclude-opponents", default="motion")
    parser.add_argument("--blocks", type=int, default=6)
    parser.add_argument("--frozen-active-seeds", default="4,44")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text())
    excluded = {name for name in args.exclude_opponents.split(",") if name}
    opponents = tuple(sorted(set(payload["opponents"]) - excluded))
    outcomes, by_opponent = option_outcomes(payload, args.option, opponents)
    features = selector_features(payload)
    seeds = sorted(outcomes)
    if set(seeds) != set(features):
        raise SystemExit("feature and outcome seed registries differ")
    frozen_seeds = {
        int(value) for value in args.frozen_active_seeds.split(",") if value.strip()
    }
    unknown = frozen_seeds - set(seeds)
    if unknown:
        raise SystemExit(f"frozen active seeds are outside the registry: {sorted(unknown)}")

    never = {seed: False for seed in seeds}
    always = {seed: True for seed in seeds}
    oracle = {seed: outcomes[seed] > 0 for seed in seeds}
    frozen = {seed: seed in frozen_seeds for seed in seeds}
    nested = nested_blocked_selector(
        seeds, args.blocks, features, outcomes, by_opponent, opponents
    )

    leave_one_opponent_out = {}
    for held in opponents:
        training_opponents = tuple(name for name in opponents if name != held)
        training_outcomes = {
            seed: statistics.mean(
                by_opponent[seed][name] for name in training_opponents
            )
            for seed in seeds
        }
        trained = nested_blocked_selector(
            seeds,
            args.blocks,
            features,
            training_outcomes,
            by_opponent,
            training_opponents,
        )
        predictions = {
            seed: trained["predictions"][str(seed)] for seed in seeds
        }
        leave_one_opponent_out[held] = {
            "selected_seed_count": sum(predictions.values()),
            "held_opponent_mean": statistics.mean(
                by_opponent[seed][held] if predictions[seed] else 0.0
                for seed in seeds
            ),
            "frozen_rule_held_opponent_mean": statistics.mean(
                by_opponent[seed][held] if frozen[seed] else 0.0
                for seed in seeds
            ),
        }

    oracle_evaluation = evaluate_predictions(
        seeds, oracle, outcomes, by_opponent, opponents
    )
    result = {
        "schema": 1,
        "scope": (
            "60 reused discovery seeds; seed-clustered outcomes; deterministic opponents; "
            "six contiguous outer blocks with inner blocked configuration selection"
        ),
        "source": str(args.input),
        "option": args.option,
        "opponents": opponents,
        "excluded_opponents": sorted(excluded),
        "seeds": seeds,
        "blocks": args.blocks,
        "feature_sets": {
            "bank": BANK_FEATURES,
            "bank_geometry": GEOMETRY_FEATURES,
        },
        "always_control": evaluate_predictions(
            seeds, never, outcomes, by_opponent, opponents
        ),
        "always_option": evaluate_predictions(
            seeds, always, outcomes, by_opponent, opponents
        ),
        "hindsight_oracle": oracle_evaluation,
        "frozen_sparse_rule": evaluate_predictions(
            seeds, frozen, outcomes, by_opponent, opponents
        ),
        "nested_selector": nested,
        "oracle_fraction_captured": (
            nested["evaluation"]["summary"]["mean"]
            / oracle_evaluation["summary"]["mean"]
            if oracle_evaluation["summary"]["mean"] > 0
            else None
        ),
        "leave_one_opponent_out": leave_one_opponent_out,
        "turn_2_4_update": {
            "status": "not_evaluated",
            "reason": "the full-information league contains no opponent-opening feature stream",
        },
    }
    save(args.output, result)
    print(
        json.dumps(
            {
                "always_option": result["always_option"],
                "oracle": result["hindsight_oracle"],
                "frozen": result["frozen_sparse_rule"],
                "nested": nested["evaluation"],
                "oracle_fraction_captured": result["oracle_fraction_captured"],
                "final_config": nested["final_config"],
                "final_model": nested["final_model"],
                "leave_one_opponent_out": leave_one_opponent_out,
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
