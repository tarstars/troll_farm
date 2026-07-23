#!/usr/bin/env python3
"""Cross-validate option selection across held-out opponent continuations."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.offline_policy_league import robust_summary  # noqa: E402


def outcome_matrix(
    payload: dict, policy: str, opponents: tuple[str, ...]
) -> tuple[list[int], dict[int, dict[str, float]]]:
    cells = {}
    for row in payload["rows"]:
        if row["policy"] != policy or row["opponent"] not in opponents:
            continue
        key = (row["seed"], row["opponent"])
        if key in cells:
            raise ValueError(f"duplicate option cell {key}")
        cells[key] = row["delta_vs_live_margin"]
    seeds = sorted({seed for seed, _ in cells})
    matrix = {
        seed: {opponent: cells[(seed, opponent)] for opponent in opponents}
        for seed in seeds
    }
    return seeds, matrix


def select_from_rollouts(values: list[float], rule: str, threshold: float) -> bool:
    if rule == "positive-mean":
        return statistics.mean(values) > threshold
    if rule == "unanimous-positive":
        return all(value > threshold for value in values)
    raise ValueError(f"unknown rollout rule {rule}")


def held_out_evaluation(
    seeds: list[int],
    matrix: dict[int, dict[str, float]],
    opponents: tuple[str, ...],
    rule: str,
    threshold: float = 0.0,
) -> dict:
    per_seed = {seed: [] for seed in seeds}
    held_rows = []
    for held in opponents:
        rollout_opponents = tuple(name for name in opponents if name != held)
        selected = 0
        values = []
        for seed in seeds:
            use_option = select_from_rollouts(
                [matrix[seed][name] for name in rollout_opponents], rule, threshold
            )
            selected += use_option
            value = matrix[seed][held] if use_option else 0.0
            values.append(value)
            per_seed[seed].append(value)
        held_rows.append(
            {
                "held_opponent": held,
                "rollout_opponents": rollout_opponents,
                "selected_seed_count": selected,
                "summary": robust_summary(values),
            }
        )
    seed_values = {
        seed: statistics.mean(per_seed[seed]) for seed in seeds
    }
    return {
        "rule": rule,
        "threshold": threshold,
        "rollout_opponents_per_decision": len(opponents) - 1,
        "full_terminal_games_per_decision": 2 * (len(opponents) - 1),
        "seed_clustered_summary": robust_summary(seed_values.values()),
        "selected_seed_count": sum(value != 0 for value in seed_values.values()),
        "held_opponents": held_rows,
        "worst_held_opponent_mean": min(
            row["summary"]["mean"] for row in held_rows
        ),
        "seed_values": [
            {"seed": seed, "cross_fitted_delta": seed_values[seed]}
            for seed in seeds
            if seed_values[seed] != 0
        ],
    }


def budget_curve(
    seeds: list[int],
    matrix: dict[int, dict[str, float]],
    opponents: tuple[str, ...],
    rule: str,
    threshold: float = 0.0,
) -> list[dict]:
    rows = []
    for budget in range(1, len(opponents)):
        configurations = []
        for rollout_opponents in itertools.combinations(opponents, budget):
            held = tuple(name for name in opponents if name not in rollout_opponents)
            seed_values = []
            selected = 0
            for seed in seeds:
                use_option = select_from_rollouts(
                    [matrix[seed][name] for name in rollout_opponents],
                    rule,
                    threshold,
                )
                selected += use_option
                seed_values.append(
                    statistics.mean(matrix[seed][name] for name in held)
                    if use_option
                    else 0.0
                )
            configurations.append(
                {
                    "rollout_opponents": rollout_opponents,
                    "held_opponents": held,
                    "selected_seed_count": selected,
                    "summary": robust_summary(seed_values),
                }
            )
        means = [row["summary"]["mean"] for row in configurations]
        worst_deciles = [
            row["summary"]["worst_decile_mean"] for row in configurations
        ]
        rows.append(
            {
                "rollout_opponent_count": budget,
                "full_terminal_games_per_decision": 2 * budget,
                "configuration_count": len(configurations),
                "configuration_mean_delta": robust_summary(means),
                "worst_configuration_mean": min(means),
                "best_configuration_mean": max(means),
                "worst_configuration_worst_decile": min(worst_deciles),
                "configurations": configurations,
            }
        )
    return rows


def hindsight_oracle(
    seeds: list[int], matrix: dict[int, dict[str, float]], opponents: tuple[str, ...]
) -> dict:
    values = []
    for seed in seeds:
        option_value = statistics.mean(matrix[seed].values())
        values.append(max(option_value, 0.0))
    return robust_summary(values)


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--policy", default="adaptivehp0")
    parser.add_argument("--exclude-opponents", default="motion")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text())
    excluded = {name for name in args.exclude_opponents.split(",") if name}
    opponents = tuple(sorted(set(payload["opponents"]) - excluded))
    seeds, matrix = outcome_matrix(payload, args.policy, opponents)
    oracle = hindsight_oracle(seeds, matrix, opponents)
    mean_selector = held_out_evaluation(
        seeds, matrix, opponents, "positive-mean"
    )
    unanimous_selector = held_out_evaluation(
        seeds, matrix, opponents, "unanimous-positive"
    )
    result = {
        "schema": 1,
        "scope": (
            "60 reused discovery maps; terminal option/control deltas; one opponent policy "
            "held out from each selection; seed-clustered summaries"
        ),
        "source": str(args.input),
        "policy": args.policy,
        "opponents": opponents,
        "excluded_opponents": sorted(excluded),
        "seeds": seeds,
        "hindsight_oracle": oracle,
        "positive_mean_selector": mean_selector,
        "unanimous_positive_selector": unanimous_selector,
        "unanimous_oracle_fraction": (
            unanimous_selector["seed_clustered_summary"]["mean"] / oracle["mean"]
            if oracle["mean"] > 0
            else None
        ),
        "positive_mean_budget_curve": budget_curve(
            seeds, matrix, opponents, "positive-mean"
        ),
        "unanimous_positive_budget_curve": budget_curve(
            seeds, matrix, opponents, "unanimous-positive"
        ),
        "interpretation_limit": (
            "The selector sees exact terminal outcomes under rollout continuations.  This is an "
            "offline option-level oracle and cross-continuation test, not a latency-feasible "
            "live implementation or an untouched-map estimate."
        ),
    }
    save(args.output, result)
    print(
        json.dumps(
            {
                "oracle": oracle,
                "positive_mean": mean_selector,
                "unanimous_positive": unanimous_selector,
                "unanimous_oracle_fraction": result["unanimous_oracle_fraction"],
                "unanimous_budget_curve": [
                    {
                        key: row[key]
                        for key in (
                            "rollout_opponent_count",
                            "full_terminal_games_per_decision",
                            "worst_configuration_mean",
                            "best_configuration_mean",
                            "worst_configuration_worst_decile",
                        )
                    }
                    for row in result["unanimous_positive_budget_curve"]
                ],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
