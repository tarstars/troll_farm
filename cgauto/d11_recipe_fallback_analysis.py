#!/usr/bin/env python3
"""Analyze the frozen D11 recipe-7-to-recipe-6 deadline sweep."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.d11_recipe_catalog_analysis import summary  # noqa: E402

RECIPE6 = (2, 2, 0, 2)
RECIPE7 = (2, 3, 1, 2)
NUMERIC_FIELDS = {
    "seed",
    "seat",
    "recipe",
    "fallback_turn",
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
    "trained_ms",
    "trained_cc",
    "trained_hp",
    "trained_chop",
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


def read_tsv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field in NUMERIC_FIELDS & row.keys():
            row[field] = int(row[field])
    return rows


def grouped_mean(rows: list[dict], key_fields: tuple[str, ...], value) -> dict:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in key_fields)].append(value(row))
    return {key: statistics.mean(values) for key, values in groups.items()}


def validate(fallback: list[dict], controls: list[dict]) -> tuple[list[int], list[str], list[int]]:
    if not fallback:
        raise ValueError("fallback sweep is empty")
    seeds = sorted({row["seed"] for row in fallback})
    opponents = sorted({row["opponent"] for row in fallback})
    deadlines = sorted({row["fallback_turn"] for row in fallback})
    expected = {
        (seed, seat, opponent, deadline)
        for seed in seeds
        for seat in range(2)
        for opponent in opponents
        for deadline in deadlines
    }
    observed = {
        (row["seed"], row["seat"], row["opponent"], row["fallback_turn"])
        for row in fallback
    }
    if expected != observed or len(fallback) != len(expected):
        raise ValueError(
            f"incomplete fallback sweep: rows={len(fallback)}, expected={len(expected)}"
        )
    if any(row["recipe"] != 7 or row["fallback_turn"] <= 0 for row in fallback):
        raise ValueError("fallback rows must start from recipe 7 and use a positive deadline")

    control_index = {
        (row["seed"], row["seat"], row["opponent"], row["recipe"]): row
        for row in controls
        if row["recipe"] in (6, 7)
    }
    required_controls = {
        (seed, seat, opponent, recipe)
        for seed in seeds
        for seat in range(2)
        for opponent in opponents
        for recipe in (6, 7)
    }
    if set(control_index) != required_controls:
        raise ValueError("fixed recipe controls do not exactly cover the fallback cells")
    return seeds, opponents, deadlines


def analyze(fallback: list[dict], controls: list[dict], fallback_path: Path, control_path: Path) -> dict:
    seeds, opponents, deadlines = validate(fallback, controls)
    control = {
        (row["seed"], row["seat"], row["opponent"], row["recipe"]): row
        for row in controls
        if row["recipe"] in (6, 7)
    }
    failure_keys = {
        (seed, seat, opponent)
        for seed in seeds
        for seat in range(2)
        for opponent in opponents
        if control[(seed, seat, opponent, 7)]["workers"] < 2
    }
    success_keys = {
        (seed, seat, opponent)
        for seed in seeds
        for seat in range(2)
        for opponent in opponents
        if control[(seed, seat, opponent, 7)]["workers"] >= 2
    }

    control_map_margin = grouped_mean(
        [row for row in controls if row["recipe"] in (6, 7)],
        ("seed", "recipe"),
        lambda row: row["margin"],
    )
    controls_summary = {}
    for recipe in (6, 7):
        recipe_rows = [row for row in controls if row["recipe"] == recipe]
        controls_summary[str(recipe)] = {
            "game_margin": summary(row["margin"] for row in recipe_rows),
            "map_balanced_margin": summary(
                control_map_margin[(seed, recipe)] for seed in seeds
            ),
            "training_completion": {
                "completed": sum(row["workers"] >= 2 for row in recipe_rows),
                "games": len(recipe_rows),
                "rate": statistics.mean(row["workers"] >= 2 for row in recipe_rows),
            },
        }

    per_deadline = {}
    eligible = []
    for deadline in deadlines:
        rows = [row for row in fallback if row["fallback_turn"] == deadline]
        map_margin = grouped_mean(rows, ("seed",), lambda row: row["margin"])
        delta6 = []
        delta7 = []
        failure_delta6 = []
        failure_delta7 = []
        success_delta6 = []
        success_delta7 = []
        for row in rows:
            key = (row["seed"], row["seat"], row["opponent"])
            d6 = row["margin"] - control[(*key, 6)]["margin"]
            d7 = row["margin"] - control[(*key, 7)]["margin"]
            delta6.append(d6)
            delta7.append(d7)
            if key in failure_keys:
                failure_delta6.append(d6)
                failure_delta7.append(d7)
            else:
                success_delta6.append(d6)
                success_delta7.append(d7)
        map_delta6 = [
            map_margin[(seed,)] - control_map_margin[(seed, 6)] for seed in seeds
        ]
        map_delta7 = [
            map_margin[(seed,)] - control_map_margin[(seed, 7)] for seed in seeds
        ]
        opponent_delta6 = {}
        opponent_delta7 = {}
        for opponent in opponents:
            opponent_rows = [row for row in rows if row["opponent"] == opponent]
            opponent_delta6[opponent] = statistics.mean(
                row["margin"]
                - control[(row["seed"], row["seat"], opponent, 6)]["margin"]
                for row in opponent_rows
            )
            opponent_delta7[opponent] = statistics.mean(
                row["margin"]
                - control[(row["seed"], row["seat"], opponent, 7)]["margin"]
                for row in opponent_rows
            )
        final_specs = Counter(
            (
                row["trained_ms"],
                row["trained_cc"],
                row["trained_hp"],
                row["trained_chop"],
            )
            if row["workers"] >= 2
            else None
            for row in rows
        )
        completed = sum(row["workers"] >= 2 for row in rows)
        result = {
            "deadline": deadline,
            "game_margin": summary(row["margin"] for row in rows),
            "map_balanced_margin": summary(map_margin.values()),
            "cell_margin_delta_vs_recipe6": summary(delta6),
            "cell_margin_delta_vs_recipe7": summary(delta7),
            "map_balanced_margin_delta_vs_recipe6": summary(map_delta6),
            "map_balanced_margin_delta_vs_recipe7": summary(map_delta7),
            "opponent_mean_delta_vs_recipe6": opponent_delta6,
            "opponent_mean_delta_vs_recipe7": opponent_delta7,
            "worst_opponent_mean_delta_vs_recipe6": min(opponent_delta6.values()),
            "training_completion": {
                "completed": completed,
                "games": len(rows),
                "rate": completed / len(rows),
            },
            "final_worker_specs": {
                ("none" if spec is None else "/".join(map(str, spec))): count
                for spec, count in sorted(
                    final_specs.items(), key=lambda item: str(item[0])
                )
            },
            "fallback_activation_rate": final_specs[RECIPE6] / len(rows),
            "known_recipe7_failure_cells": {
                "n": len(failure_delta6),
                "delta_vs_recipe6": summary(failure_delta6),
                "delta_vs_recipe7": summary(failure_delta7),
            },
            "known_recipe7_success_cells": {
                "n": len(success_delta6),
                "delta_vs_recipe6": summary(success_delta6),
                "delta_vs_recipe7": summary(success_delta7),
            },
        }
        gates = {
            "all_games_train": completed == len(rows),
            "map_delta_vs_recipe6_at_least_5": summary(map_delta6)["mean"] >= 5,
            "worst_opponent_delta_vs_recipe6_at_least_minus5": min(
                opponent_delta6.values()
            )
            >= -5,
            "not_below_fixed_recipe7": summary(map_delta7)["mean"] >= 0,
            "positive_delta_vs_recipe6_in_failure_cells": summary(failure_delta6)[
                "mean"
            ]
            > 0,
            "positive_delta_vs_recipe6_in_success_cells": summary(success_delta6)[
                "mean"
            ]
            > 0,
        }
        result["gates"] = gates
        result["eligible"] = all(gates.values())
        if result["eligible"]:
            eligible.append(deadline)
        per_deadline[str(deadline)] = result

    selected = None
    if eligible:
        maximum = max(
            per_deadline[str(deadline)]["map_balanced_margin"]["mean"]
            for deadline in eligible
        )
        selected = min(
            deadline
            for deadline in eligible
            if per_deadline[str(deadline)]["map_balanced_margin"]["mean"]
            >= maximum - 1
        )

    return {
        "schema": 1,
        "scope": (
            "D11 recipe-7 to recipe-6 fixed-turn fallback development sweep on reused "
            "seeds; exact paired engine outcomes; not Arena-calibrated"
        ),
        "source": {
            "fallback_rows": str(fallback_path),
            "fallback_rows_sha256": sha256(fallback_path),
            "fixed_controls": str(control_path),
            "fixed_controls_sha256": sha256(control_path),
            "analyzer": str(Path(__file__).relative_to(REPO)),
            "analyzer_sha256": sha256(Path(__file__)),
        },
        "design": {
            "seeds": seeds,
            "opponents": opponents,
            "seats": [0, 1],
            "deadlines": deadlines,
            "games": len(fallback),
            "complete": True,
            "known_recipe7_failure_cells": len(failure_keys),
            "known_recipe7_success_cells": len(success_keys),
        },
        "fixed_controls": controls_summary,
        "per_deadline": per_deadline,
        "selection": {
            "eligible_deadlines": eligible,
            "selected_deadline": selected,
            "rule": (
                "all six frozen gates; maximize map-balanced margin; among deadlines "
                "within one point of maximum select earliest"
            ),
            "authorization": (
                "development selection only; any selected deadline requires a frozen "
                "disjoint prospective protocol"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fallback_rows", type=Path)
    parser.add_argument("fixed_controls", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = analyze(
        read_tsv(args.fallback_rows),
        read_tsv(args.fixed_controls),
        args.fallback_rows,
        args.fixed_controls,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "games": result["design"]["games"],
                "eligible_deadlines": result["selection"]["eligible_deadlines"],
                "selected_deadline": result["selection"]["selected_deadline"],
                "ranking": [
                    {
                        "deadline": int(deadline),
                        "mean_margin": values["map_balanced_margin"]["mean"],
                        "delta_vs_recipe6": values[
                            "map_balanced_margin_delta_vs_recipe6"
                        ]["mean"],
                        "delta_vs_recipe7": values[
                            "map_balanced_margin_delta_vs_recipe7"
                        ]["mean"],
                        "training_rate": values["training_completion"]["rate"],
                        "eligible": values["eligible"],
                    }
                    for deadline, values in result["per_deadline"].items()
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
