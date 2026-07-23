#!/usr/bin/env python3
"""Test whether in-process continuation models transfer to the frozen option league.

The Rust rollout harness consumes exact Python-generated maps and emits terminal
control/option deltas for both seats.  This script joins those predictions to
the already-computed frozen-opponent outcomes; it does not run or tune an arena
submission.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.offline_policy_league import robust_summary  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

EXPECTED_MODELS = ("gold_elite", "sched_bot", "mybot", "silver_boss")


def grid_rows(game) -> list[str]:
    rows = []
    for y in range(game.height):
        row = []
        for x in range(game.width):
            cell = (x, y)
            if cell == game.shacks[0]:
                row.append("0")
            elif cell == game.shacks[1]:
                row.append("1")
            elif cell in game.iron:
                row.append("+")
            elif cell in game.water:
                row.append("~")
            elif cell in game.walkable:
                row.append(".")
            else:
                row.append("#")
        rows.append("".join(row))
    return rows


def protocol_record(seed: int, game) -> str:
    lines = [f"SEED {seed}", f"{game.width} {game.height}", *grid_rows(game)]
    lines.extend(" ".join(map(str, inventory)) for inventory in game.inventories)
    lines.append(str(len(game.plants)))
    lines.extend(
        f"{plant.type} {plant.x} {plant.y} {plant.size} {plant.health} "
        f"{plant.fruits} {plant.cooldown}"
        for plant in game.plants
    )
    lines.append(str(len(game.units)))
    lines.extend(
        " ".join(
            map(
                str,
                (
                    unit.id,
                    unit.player,
                    unit.x,
                    unit.y,
                    unit.ms,
                    unit.cc,
                    unit.hp,
                    unit.chop,
                    *unit.carry,
                ),
            )
        )
        for unit in game.units
    )
    return "\n".join(lines) + "\n"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def export_maps(seeds: list[int], path: Path) -> None:
    atomic_write(
        path,
        "".join(protocol_record(seed, generate_bronze(seed)) for seed in seeds),
    )


def league_outcomes(
    paths: list[Path], policy: str, excluded_opponents: set[str]
) -> tuple[list[int], tuple[str, ...], dict[tuple[int, int], dict[str, float]]]:
    cells: dict[tuple[int, str, str], dict] = {}
    opponents = set()
    for path in paths:
        payload = json.loads(path.read_text())
        opponents.update(set(payload["opponents"]) - excluded_opponents)
        for row in payload["rows"]:
            if row["opponent"] in excluded_opponents or row["policy"] not in {
                "live",
                policy,
            }:
                continue
            key = (row["seed"], row["opponent"], row["policy"])
            if key in cells:
                raise ValueError(f"duplicate league row {key}")
            cells[key] = row
    ordered_opponents = tuple(sorted(opponents))
    seeds = sorted({seed for seed, _, _ in cells})
    outcomes = {}
    for seed in seeds:
        for seat in (0, 1):
            outcomes[(seed, seat)] = {}
            for opponent in ordered_opponents:
                option = cells[(seed, opponent, policy)]["seat_margins"][seat]
                control = cells[(seed, opponent, "live")]["seat_margins"][seat]
                outcomes[(seed, seat)][opponent] = option - control
    return seeds, ordered_opponents, outcomes


def read_rollouts(
    path: Path,
) -> dict[tuple[int, int], dict[str, float]]:
    values: dict[tuple[int, int], dict[str, float]] = {}
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            key = (int(row["seed"]), int(row["seat"]))
            model = row["model"]
            if model in values.setdefault(key, {}):
                raise ValueError(f"duplicate rollout row {key + (model,)}")
            values[key][model] = float(row["delta"])
    for key, models in values.items():
        if tuple(sorted(models)) != tuple(sorted(EXPECTED_MODELS)):
            raise ValueError(f"unexpected models for {key}: {sorted(models)}")
    return values


def pearson(first: list[float], second: list[float]) -> float | None:
    if len(first) != len(second) or len(first) < 2:
        return None
    first_mean = statistics.mean(first)
    second_mean = statistics.mean(second)
    numerator = sum(
        (left - first_mean) * (right - second_mean)
        for left, right in zip(first, second, strict=True)
    )
    first_scale = sum((value - first_mean) ** 2 for value in first)
    second_scale = sum((value - second_mean) ** 2 for value in second)
    denominator = math.sqrt(first_scale * second_scale)
    return numerator / denominator if denominator else None


def choose(values: dict[str, float], rule: str, threshold: float) -> bool:
    if rule == "unanimous-positive":
        return all(value > threshold for value in values.values())
    if rule == "positive-mean":
        return statistics.mean(values.values()) > threshold
    if rule in values:
        return values[rule] > threshold
    raise ValueError(f"unknown selector rule {rule}")


def evaluate_selector(
    seeds: list[int],
    opponents: tuple[str, ...],
    outcomes: dict[tuple[int, int], dict[str, float]],
    rollouts: dict[tuple[int, int], dict[str, float]],
    rule: str,
    threshold: float = 0.0,
) -> dict:
    selected = {
        key: choose(rollouts[key], rule, threshold)
        for key in sorted(outcomes)
    }
    cell_actual = {
        key: statistics.mean(outcomes[key].values()) if selected[key] else 0.0
        for key in selected
    }
    seed_actual = {
        seed: statistics.mean(cell_actual[(seed, seat)] for seat in (0, 1))
        for seed in seeds
    }
    by_opponent = {}
    for opponent in opponents:
        opponent_seed_values = [
            statistics.mean(
                outcomes[(seed, seat)][opponent]
                if selected[(seed, seat)]
                else 0.0
                for seat in (0, 1)
            )
            for seed in seeds
        ]
        by_opponent[opponent] = robust_summary(opponent_seed_values)
    selected_rows = [
        {
            "seed": seed,
            "seat": seat,
            "rollout_deltas": rollouts[(seed, seat)],
            "rollout_mean": statistics.mean(rollouts[(seed, seat)].values()),
            "actual_mean_delta": statistics.mean(outcomes[(seed, seat)].values()),
            "actual_opponent_deltas": outcomes[(seed, seat)],
        }
        for seed, seat in selected
        if selected[(seed, seat)]
    ]
    return {
        "rule": rule,
        "threshold": threshold,
        "selected_cell_count": len(selected_rows),
        "selected_seed_count": len({row["seed"] for row in selected_rows}),
        "seed_clustered_summary": robust_summary(seed_actual.values()),
        "seat_cell_summary": robust_summary(cell_actual.values()),
        "worst_opponent_mean": min(
            summary["mean"] for summary in by_opponent.values()
        ),
        "by_opponent": by_opponent,
        "selected_cells": selected_rows,
    }


def prediction_diagnostics(
    outcomes: dict[tuple[int, int], dict[str, float]],
    rollouts: dict[tuple[int, int], dict[str, float]],
) -> dict:
    keys = sorted(outcomes)
    actual = [statistics.mean(outcomes[key].values()) for key in keys]
    model_reports = {}
    for model in EXPECTED_MODELS:
        predicted = [rollouts[key][model] for key in keys]
        model_reports[model] = {
            "delta_summary": robust_summary(predicted),
            "pearson_with_actual_delta": pearson(predicted, actual),
            "sign_agreement": statistics.mean(
                (prediction > 0) == (truth > 0)
                for prediction, truth in zip(predicted, actual, strict=True)
            ),
        }
    predicted_mean = [statistics.mean(rollouts[key].values()) for key in keys]
    return {
        "actual_option_delta": robust_summary(actual),
        "ensemble_mean_delta": robust_summary(predicted_mean),
        "ensemble_mean_pearson_with_actual_delta": pearson(predicted_mean, actual),
        "ensemble_mean_sign_agreement": statistics.mean(
            (prediction > 0) == (truth > 0)
            for prediction, truth in zip(predicted_mean, actual, strict=True)
        ),
        "models": model_reports,
    }


def study(
    league_paths: list[Path],
    rollouts_path: Path,
    policy: str,
    excluded_opponents: set[str],
) -> dict:
    seeds, opponents, outcomes = league_outcomes(
        league_paths, policy, excluded_opponents
    )
    rollouts = read_rollouts(rollouts_path)
    missing = sorted(set(outcomes) - set(rollouts))
    if missing:
        raise ValueError(f"rollout/league cell mismatch; missing={missing}")
    ignored_rollout_cells = sorted(set(rollouts) - set(outcomes))
    rollouts = {key: rollouts[key] for key in outcomes}
    selectors = {
        rule: evaluate_selector(
            seeds, opponents, outcomes, rollouts, rule
        )
        for rule in (*EXPECTED_MODELS, "positive-mean", "unanimous-positive")
    }
    selectors["gold-margin-30"] = evaluate_selector(
        seeds,
        opponents,
        outcomes,
        rollouts,
        "gold_elite",
        30.0,
    )
    threshold_curve = [
        evaluate_selector(
            seeds,
            opponents,
            outcomes,
            rollouts,
            "unanimous-positive",
            threshold,
        )
        for threshold in (0.0, 2.0, 5.0, 10.0, 20.0)
    ]
    oracle_values = {
        key: max(statistics.mean(values.values()), 0.0)
        for key, values in outcomes.items()
    }
    oracle_seed_values = [
        statistics.mean(oracle_values[(seed, seat)] for seat in (0, 1))
        for seed in seeds
    ]
    return {
        "schema": 1,
        "scope": (
            "exact Python league maps; exact promoted Yamo control and global immediate "
            "max-bank harvest-0 option; four in-process Rust continuation models; both seats"
        ),
        "league_sources": [str(path) for path in league_paths],
        "rollout_source": str(rollouts_path),
        "policy": policy,
        "excluded_opponents": sorted(excluded_opponents),
        "seeds": seeds,
        "opponents": opponents,
        "rollout_models": EXPECTED_MODELS,
        "ignored_rollout_cell_count": len(ignored_rollout_cells),
        "terminal_games_per_live_decision": 2 * len(EXPECTED_MODELS),
        "prediction_diagnostics": prediction_diagnostics(outcomes, rollouts),
        "seat_hindsight_oracle": robust_summary(oracle_seed_values),
        "selectors": selectors,
        "gold_margin_threshold_curve_discovery_only": [
            evaluate_selector(
                seeds,
                opponents,
                outcomes,
                rollouts,
                "gold_elite",
                threshold,
            )
            for threshold in (0.0, 5.0, 10.0, 20.0, 30.0, 50.0, 75.0, 100.0)
        ],
        "unanimous_threshold_curve_discovery_only": threshold_curve,
        "interpretation_limit": (
            "The local models are a transfer diagnostic, not yet a byte-budgeted live "
            "ensemble. Thresholds beyond zero are post-hoc discovery on these reused maps."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--league", type=Path, action="append", default=[])
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--seed-count", type=int)
    parser.add_argument("--policy", default="adaptivehp0")
    parser.add_argument("--exclude-opponents", default="motion")
    parser.add_argument("--export-maps", type=Path)
    parser.add_argument("--rollouts", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    excluded = {value for value in args.exclude_opponents.split(",") if value}
    if args.seed_count is not None:
        if args.seed_count <= 0 or args.seed_start < 0:
            raise SystemExit("--seed-start must be nonnegative and --seed-count positive")
        seeds = list(range(args.seed_start, args.seed_start + args.seed_count))
    elif args.league:
        seeds, _, _ = league_outcomes(args.league, args.policy, excluded)
    else:
        seeds = []
    if args.export_maps:
        if not seeds:
            raise SystemExit("--export-maps needs --league or --seed-count")
        export_maps(seeds, args.export_maps)
        print(f"exported {len(seeds)} exact Python maps to {args.export_maps}")
    if args.rollouts:
        if not args.league:
            raise SystemExit("--rollouts requires at least one --league")
        if not args.output:
            raise SystemExit("--output is required with --rollouts")
        result = study(
            args.league, args.rollouts, args.policy, excluded
        )
        atomic_write(args.output, json.dumps(result, indent=1) + "\n")
        compact = {
            "diagnostics": result["prediction_diagnostics"],
            "seat_hindsight_oracle": result["seat_hindsight_oracle"],
            "selectors": {
                name: {
                    "selected_cell_count": report["selected_cell_count"],
                    "selected_seed_count": report["selected_seed_count"],
                    "seed_clustered_summary": report["seed_clustered_summary"],
                    "worst_opponent_mean": report["worst_opponent_mean"],
                }
                for name, report in result["selectors"].items()
            },
            "threshold_curve": [
                {
                    "threshold": report["threshold"],
                    "selected_cell_count": report["selected_cell_count"],
                    "mean": report["seed_clustered_summary"]["mean"],
                    "losses": report["seed_clustered_summary"]["losses"],
                    "minimum": report["seed_clustered_summary"]["minimum"],
                    "worst_opponent_mean": report["worst_opponent_mean"],
                }
                for report in result["unanimous_threshold_curve_discovery_only"]
            ],
        }
        print(json.dumps(compact, indent=1))
        print(f"saved {args.output}")
    if not args.export_maps and not args.rollouts:
        raise SystemExit("select --export-maps and/or --rollouts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
