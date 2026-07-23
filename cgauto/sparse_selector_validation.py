#!/usr/bin/env python3
"""Combine a sparse activation manifest with active-map option outcomes."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.offline_policy_league import robust_summary  # noqa: E402


def seed_outcomes(
    league: dict, policy: str, opponents: tuple[str, ...]
) -> tuple[dict[int, float], dict[int, dict[str, float]]]:
    cells = {}
    for row in league["rows"]:
        if row["policy"] != policy or row["opponent"] not in opponents:
            continue
        key = (row["seed"], row["opponent"])
        if key in cells:
            raise ValueError(f"duplicate active outcome cell {key}")
        cells[key] = row["delta_vs_live_margin"]
    seeds = sorted({seed for seed, _ in cells})
    by_opponent = {
        seed: {opponent: cells[(seed, opponent)] for opponent in opponents}
        for seed in seeds
    }
    means = {seed: statistics.mean(by_opponent[seed].values()) for seed in seeds}
    return means, by_opponent


def subset_summary(
    seeds: list[int],
    means: dict[int, float],
    by_opponent: dict[int, dict[str, float]],
    opponents: tuple[str, ...],
    active_side_counts: dict[int, int],
) -> dict:
    values = [means[seed] for seed in seeds]
    opponent_means = {
        opponent: statistics.mean(by_opponent[seed][opponent] for seed in seeds)
        for opponent in opponents
    }
    cells = [by_opponent[seed][opponent] for seed in seeds for opponent in opponents]
    leave_one_out = [
        statistics.mean(value for index, value in enumerate(values) if index != removed)
        for removed in range(len(values))
    ] if len(values) > 1 else values
    return {
        "seed_count": len(seeds),
        "seed_summary": robust_summary(values),
        "cell_summary_nonindependent": robust_summary(cells),
        "opponent_means": opponent_means,
        "worst_opponent_mean": min(opponent_means.values()),
        "leave_one_seed_out_minimum_mean": min(leave_one_out),
        "active_side_count_distribution": dict(
            sorted(Counter(active_side_counts[seed] for seed in seeds).items())
        ),
        "seeds": [
            {
                "seed": seed,
                "active_sides": active_side_counts[seed],
                "mean_delta": means[seed],
                "opponent_deltas": by_opponent[seed],
            }
            for seed in seeds
        ],
    }


def full_registry_summary(
    registry_seeds: list[int],
    active_means: dict[int, float],
    active_by_opponent: dict[int, dict[str, float]],
    opponents: tuple[str, ...],
) -> dict:
    values = [active_means.get(seed, 0.0) for seed in registry_seeds]
    opponent_means = {
        opponent: statistics.mean(
            active_by_opponent.get(seed, {}).get(opponent, 0.0)
            for seed in registry_seeds
        )
        for opponent in opponents
    }
    return {
        "seed_summary": robust_summary(values),
        "opponent_means": opponent_means,
        "worst_opponent_mean": min(opponent_means.values()),
        "activation_count": len(active_means),
        "activation_rate": len(active_means) / len(registry_seeds),
    }


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--league", type=Path, required=True)
    parser.add_argument("--activation-scan", type=Path, required=True)
    parser.add_argument("--policy", default="frozenhp0")
    parser.add_argument("--exclude-opponents", default="motion")
    parser.add_argument("--fit-max-seed", type=int, default=59)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    league = json.loads(args.league.read_text())
    scan = json.loads(args.activation_scan.read_text())
    excluded = {name for name in args.exclude_opponents.split(",") if name}
    opponents = tuple(sorted(set(league["opponents"]) - excluded))
    means, by_opponent = seed_outcomes(league, args.policy, opponents)
    active_seeds = scan["aggregate"]["active_seeds"]
    if set(active_seeds) != set(means):
        raise SystemExit("league seeds do not equal the activation manifest")
    active_side_counts = Counter(
        seed for seed, _ in scan["aggregate"]["active_sides"]
    )
    fitting = [seed for seed in active_seeds if seed <= args.fit_max_seed]
    extension = [seed for seed in active_seeds if seed > args.fit_max_seed]
    registry_seeds = scan["seed_values"]
    result = {
        "schema": 1,
        "scope": (
            "frozen sparse rule on reused discovery seeds; deterministic opponents only; "
            "structural zeros restored for inactive maps"
        ),
        "league": str(args.league),
        "activation_scan": str(args.activation_scan),
        "policy": args.policy,
        "opponents": opponents,
        "excluded_opponents": sorted(excluded),
        "fit_max_seed": args.fit_max_seed,
        "activation": scan["aggregate"],
        "fitting_block_active": subset_summary(
            fitting, means, by_opponent, opponents, active_side_counts
        ),
        "post_fit_extension_active": subset_summary(
            extension, means, by_opponent, opponents, active_side_counts
        ),
        "all_active": subset_summary(
            active_seeds, means, by_opponent, opponents, active_side_counts
        ),
        "full_registry": full_registry_summary(
            registry_seeds, means, by_opponent, opponents
        ),
    }
    extension_result = result["post_fit_extension_active"]
    result["roadmap_diagnostics"] = {
        "positive_extension_mean": extension_result["seed_summary"]["mean"] > 0,
        "positive_extension_trimmed_mean": (
            extension_result["seed_summary"]["trimmed_5pct_mean"] > 0
        ),
        "nonnegative_extension_worst_opponent": (
            extension_result["worst_opponent_mean"] >= 0
        ),
        "positive_full_registry_mean": (
            result["full_registry"]["seed_summary"]["mean"] > 0
        ),
    }
    save(args.output, result)
    print(
        json.dumps(
            {
                "activation": result["activation"],
                "fitting": result["fitting_block_active"],
                "extension": result["post_fit_extension_active"],
                "all_active": result["all_active"],
                "full_registry": result["full_registry"],
                "roadmap_diagnostics": result["roadmap_diagnostics"],
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
