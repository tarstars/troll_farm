#!/usr/bin/env python3
"""Summarize paired full-game outcomes from ``d11_recipe_catalog``.

The independent unit for the primary comparison is a map seed.  Seats and
opponents are averaged before recipe ranking; game-level and opponent-level
views are retained as diagnostics.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Iterable

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from sim.mapgen import generate_bronze  # noqa: E402

RECIPES = {
    0: (1, 1, 1, 1),
    1: (1, 2, 1, 1),
    2: (2, 2, 1, 1),
    3: (2, 2, 2, 1),
    4: (1, 3, 0, 1),
    5: (1, 2, 0, 2),
    6: (2, 2, 0, 2),
    7: (2, 3, 1, 2),
}
BASELINE_RECIPE = 6
INTEGER_FIELDS = {
    "seed",
    "seat",
    "recipe",
    "ms",
    "cc",
    "hp",
    "chop",
    "score",
    "opponent_score",
    "margin",
    "wood",
    "opponent_wood",
    "wood_edge",
    "terminal_turn",
    "workers",
    "opponent_workers",
    "train_commands",
    "plant_commands",
    "harvest_commands",
    "chop_commands",
    "drop_commands",
    "move_commands",
    "elapsed_us",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field in INTEGER_FIELDS:
            row[field] = int(row[field])
    return rows


def summary(values: Iterable[float]) -> dict:
    values = list(values)
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "standard_deviation": None,
            "standard_error": None,
            "ci95_normal": [None, None],
            "worst_decile_mean": None,
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "minimum": None,
            "maximum": None,
        }
    ordered = sorted(values)
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    se = sd / math.sqrt(len(values))
    worst_n = max(1, math.ceil(len(values) * 0.1))
    return {
        "n": len(values),
        "mean": mean,
        "median": statistics.median(values),
        "standard_deviation": sd,
        "standard_error": se,
        "ci95_normal": [mean - 1.96 * se, mean + 1.96 * se],
        "worst_decile_mean": statistics.mean(ordered[:worst_n]),
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
        "minimum": ordered[0],
        "maximum": ordered[-1],
    }


def mean_by(rows: list[dict], key_fields: tuple[str, ...], value: str) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in key_fields)].append(row[value])
    return {key: statistics.mean(values) for key, values in groups.items()}


def static_features(seed: int) -> dict:
    game = generate_bronze(seed)
    type_counts = Counter(plant.type for plant in game.plants)
    fruit_counts = Counter()
    for plant in game.plants:
        fruit_counts[plant.type] += plant.fruits
    nearest_shack_distances = [
        min(abs(plant.x - shack[0]) + abs(plant.y - shack[1]) for shack in game.shacks)
        for plant in game.plants
    ]
    features = {
        "tree_count": len(game.plants),
        "ripe_tree_count": sum(plant.fruits > 0 for plant in game.plants),
        "initial_fruit_total": sum(plant.fruits for plant in game.plants),
        "mean_nearest_shack_tree_distance": (
            statistics.mean(nearest_shack_distances)
            if nearest_shack_distances
            else 0.0
        ),
        "max_nearest_shack_tree_distance": max(nearest_shack_distances, default=0),
        "shack_manhattan_distance": abs(game.shacks[0][0] - game.shacks[1][0])
        + abs(game.shacks[0][1] - game.shacks[1][1]),
        "walkable_count": len(game.walkable),
        "initial_plum": game.inventories[0][0],
        "initial_lemon": game.inventories[0][1],
        "initial_apple": game.inventories[0][2],
        "initial_banana": game.inventories[0][3],
        "initial_iron": game.inventories[0][4],
    }
    for kind in ("PLUM", "LEMON", "APPLE", "BANANA"):
        features[f"{kind.lower()}_tree_count"] = type_counts[kind]
        features[f"{kind.lower()}_fruit_count"] = fruit_counts[kind]
    return features


def validate(rows: list[dict]) -> tuple[list[int], list[str]]:
    if not rows:
        raise ValueError("catalog is empty")
    seeds = sorted({row["seed"] for row in rows})
    opponents = sorted({row["opponent"] for row in rows})
    expected = {
        (seed, seat, opponent, recipe)
        for seed in seeds
        for seat in range(2)
        for opponent in opponents
        for recipe in RECIPES
    }
    observed = {
        (row["seed"], row["seat"], row["opponent"], row["recipe"])
        for row in rows
    }
    if expected != observed or len(rows) != len(expected):
        missing = sorted(expected - observed)[:10]
        extra = sorted(observed - expected)[:10]
        raise ValueError(
            f"incomplete/non-unique catalog: rows={len(rows)}, expected={len(expected)}, "
            f"missing={missing}, extra={extra}"
        )
    for row in rows:
        recipe = row["recipe"]
        if recipe not in RECIPES:
            raise ValueError(f"unknown recipe {recipe}")
        if tuple(row[field] for field in ("ms", "cc", "hp", "chop")) != RECIPES[
            recipe
        ]:
            raise ValueError(f"recipe/spec mismatch in {row}")
    return seeds, opponents


def analyze(rows: list[dict], input_path: Path) -> dict:
    seeds, opponents = validate(rows)
    by_cell = {
        (row["seed"], row["seat"], row["opponent"], row["recipe"]): row
        for row in rows
    }
    map_margin = mean_by(rows, ("seed", "recipe"), "margin")
    seat_map_margin = mean_by(rows, ("seed", "seat", "recipe"), "margin")
    best_fixed = max(
        RECIPES,
        key=lambda recipe: (
            statistics.mean(map_margin[(seed, recipe)] for seed in seeds),
            -recipe,
        ),
    )

    per_recipe = {}
    for recipe, spec in RECIPES.items():
        recipe_rows = [row for row in rows if row["recipe"] == recipe]
        cell_margin_deltas = []
        cell_wood_deltas = []
        for row in recipe_rows:
            baseline = by_cell[
                (row["seed"], row["seat"], row["opponent"], BASELINE_RECIPE)
            ]
            cell_margin_deltas.append(row["margin"] - baseline["margin"])
            cell_wood_deltas.append(row["wood_edge"] - baseline["wood_edge"])
        map_deltas = [
            map_margin[(seed, recipe)] - map_margin[(seed, BASELINE_RECIPE)]
            for seed in seeds
        ]
        opponent_delta = {}
        for opponent in opponents:
            opponent_rows = [
                row for row in recipe_rows if row["opponent"] == opponent
            ]
            opponent_delta[opponent] = statistics.mean(
                row["margin"]
                - by_cell[
                    (
                        row["seed"],
                        row["seat"],
                        row["opponent"],
                        BASELINE_RECIPE,
                    )
                ]["margin"]
                for row in opponent_rows
            )
        per_recipe[str(recipe)] = {
            "spec": list(spec),
            "game_margin": summary(row["margin"] for row in recipe_rows),
            "game_wood_edge": summary(row["wood_edge"] for row in recipe_rows),
            "cell_margin_delta_vs_recipe6": summary(cell_margin_deltas),
            "cell_wood_delta_vs_recipe6": summary(cell_wood_deltas),
            "map_balanced_margin": summary(
                map_margin[(seed, recipe)] for seed in seeds
            ),
            "map_balanced_margin_delta_vs_recipe6": summary(map_deltas),
            "opponent_mean_margin_delta_vs_recipe6": opponent_delta,
            "worst_opponent_mean_margin_delta_vs_recipe6": min(
                opponent_delta.values()
            ),
            "training_completion": {
                "completed": sum(row["workers"] >= 2 for row in recipe_rows),
                "games": len(recipe_rows),
                "rate": statistics.mean(row["workers"] >= 2 for row in recipe_rows),
                "train_commands": summary(
                    row["train_commands"] for row in recipe_rows
                ),
            },
            "mean_action_commands": {
                field: statistics.mean(row[field] for row in recipe_rows)
                for field in (
                    "plant_commands",
                    "harvest_commands",
                    "chop_commands",
                    "drop_commands",
                    "move_commands",
                )
            },
        }

    map_oracle_rows = []
    for seed in seeds:
        winner = max(
            RECIPES,
            key=lambda recipe: (map_margin[(seed, recipe)], -recipe),
        )
        fixed_value = map_margin[(seed, best_fixed)]
        map_oracle_rows.append(
            {
                "seed": seed,
                "selected_recipe": winner,
                "selected_margin": map_margin[(seed, winner)],
                "best_fixed_margin": fixed_value,
                "gain_vs_best_fixed": map_margin[(seed, winner)] - fixed_value,
                "features": static_features(seed),
            }
        )

    seat_map_oracle_rows = []
    for seed in seeds:
        for seat in range(2):
            winner = max(
                RECIPES,
                key=lambda recipe: (seat_map_margin[(seed, seat, recipe)], -recipe),
            )
            seat_map_oracle_rows.append(
                {
                    "seed": seed,
                    "seat": seat,
                    "selected_recipe": winner,
                    "gain_vs_best_fixed": seat_map_margin[(seed, seat, winner)]
                    - seat_map_margin[(seed, seat, best_fixed)],
                }
            )

    cell_oracle_rows = []
    complete_pair_gains = []
    for seed in seeds:
        for seat in range(2):
            for opponent in opponents:
                winner = max(
                    RECIPES,
                    key=lambda recipe: (
                        by_cell[(seed, seat, opponent, recipe)]["margin"],
                        -recipe,
                    ),
                )
                selected = by_cell[(seed, seat, opponent, winner)]
                fixed = by_cell[(seed, seat, opponent, best_fixed)]
                gain = selected["margin"] - fixed["margin"]
                if selected["workers"] >= 2 and fixed["workers"] >= 2:
                    complete_pair_gains.append(gain)
                cell_oracle_rows.append(
                    {
                        "seed": seed,
                        "seat": seat,
                        "opponent": opponent,
                        "selected_recipe": winner,
                        "gain_vs_best_fixed": gain,
                        "both_completed_training": selected["workers"] >= 2
                        and fixed["workers"] >= 2,
                    }
                )

    map_selection_counts = Counter(
        row["selected_recipe"] for row in map_oracle_rows
    )
    repeated_map_winners = {
        str(recipe): count
        for recipe, count in sorted(map_selection_counts.items())
        if count >= 2
    }
    best = per_recipe[str(best_fixed)]
    fixed_hypothesis_passes = (
        best_fixed != BASELINE_RECIPE
        and best["map_balanced_margin_delta_vs_recipe6"]["mean"] > 0
        and best["worst_opponent_mean_margin_delta_vs_recipe6"] >= -5
        and best["training_completion"]["rate"] >= 0.95
    )
    map_oracle_gain = summary(
        row["gain_vs_best_fixed"] for row in map_oracle_rows
    )
    selector_hypothesis_passes = (
        map_oracle_gain["mean"] >= 5
        and len(repeated_map_winners) >= 2
        and summary(complete_pair_gains)["mean"] >= 5
    )

    return {
        "schema": 1,
        "scope": (
            "paired exact-engine D11 fixed-recipe development catalog; map seed is the "
            "primary independent unit; reused local maps; not Arena-calibrated"
        ),
        "source": {
            "input": str(input_path),
            "input_sha256": sha256(input_path),
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "design": {
            "seeds": seeds,
            "opponents": opponents,
            "seats": [0, 1],
            "recipes": {str(key): list(value) for key, value in RECIPES.items()},
            "games": len(rows),
            "expected_games": len(seeds) * len(opponents) * 2 * len(RECIPES),
            "complete": True,
        },
        "best_fixed_recipe": best_fixed,
        "per_recipe": per_recipe,
        "map_oracle": {
            "gain_vs_best_fixed": map_oracle_gain,
            "selection_counts": dict(sorted(map_selection_counts.items())),
            "repeated_winners": repeated_map_winners,
            "rows": map_oracle_rows,
        },
        "seat_map_oracle": {
            "gain_vs_best_fixed": summary(
                row["gain_vs_best_fixed"] for row in seat_map_oracle_rows
            ),
            "selection_counts": dict(
                sorted(
                    Counter(
                        row["selected_recipe"] for row in seat_map_oracle_rows
                    ).items()
                )
            ),
            "rows": seat_map_oracle_rows,
        },
        "cell_oracle": {
            "gain_vs_best_fixed": summary(
                row["gain_vs_best_fixed"] for row in cell_oracle_rows
            ),
            "selection_counts": dict(
                sorted(
                    Counter(row["selected_recipe"] for row in cell_oracle_rows).items()
                )
            ),
            "training_complete_pair_gain": summary(complete_pair_gains),
            "rows": cell_oracle_rows,
        },
        "development_decision": {
            "fixed_recipe_hypothesis_passes": fixed_hypothesis_passes,
            "map_selector_hypothesis_passes": selector_hypothesis_passes,
            "rules": {
                "fixed": (
                    "non-recipe6 best fixed; positive map-balanced delta; worst opponent "
                    "delta >= -5; training completion >= 95%"
                ),
                "selector": (
                    "map oracle gain >= 5; at least two recipes win >=2 maps; gain among "
                    "training-complete pairs >= 5"
                ),
            },
            "authorization": (
                "development evidence only; freeze a disjoint prospective protocol before "
                "candidate construction or any Arena action"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    rows = read_rows(args.input)
    result = analyze(rows, args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    decision = result["development_decision"]
    print(
        json.dumps(
            {
                "games": result["design"]["games"],
                "best_fixed_recipe": result["best_fixed_recipe"],
                "best_fixed_delta_vs_recipe6": result["per_recipe"][
                    str(result["best_fixed_recipe"])
                ]["map_balanced_margin_delta_vs_recipe6"]["mean"],
                "map_oracle_gain": result["map_oracle"]["gain_vs_best_fixed"][
                    "mean"
                ],
                "map_oracle_selection_counts": result["map_oracle"][
                    "selection_counts"
                ],
                "fixed_recipe_hypothesis_passes": decision[
                    "fixed_recipe_hypothesis_passes"
                ],
                "map_selector_hypothesis_passes": decision[
                    "map_selector_hypothesis_passes"
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
