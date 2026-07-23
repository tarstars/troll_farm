#!/usr/bin/env python3
"""Run the locked repeated-motion follow-up for the banana-5 portfolio."""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ProcessPoolExecutor
import copy
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.offline_policy_league import (  # noqa: E402
    map_features,
    OPPONENT_SOURCES,
    paired_row,
    robust_summary,
    source_sha256,
)
from cgauto.portfolio_prospective_gate import (  # noqa: E402
    CANDIDATE,
    CANDIDATE_SHA256,
    LIVE,
    save,
    same_outcome_protocol,
    SEED_START,
    SEEDS,
    THRESHOLD,
)
from sim.mapgen import generate_bronze  # noqa: E402

MOTION = OPPONENT_SOURCES["motion"]
REPETITIONS = 5


def motion_row(
    seed: int,
    initial,
    policy_name: str,
    repetition: int,
    policy: Path,
    opponent: Path,
) -> dict:
    row = paired_row(
        seed,
        copy.deepcopy(initial),
        policy_name,
        "motion",
        policy,
        opponent,
    )
    row["repetition"] = repetition
    return row


def protocol(candidate: Path, jobs: int) -> dict:
    return {
        "seed_start": SEED_START,
        "seeds": SEEDS,
        "threshold": THRESHOLD,
        "repetitions": REPETITIONS,
        "jobs": jobs,
        "candidate_sha256": source_sha256(candidate),
        "live_sha256": source_sha256(LIVE),
        "motion_sha256": source_sha256(MOTION),
    }


def seed_results(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[int, str], list[float]] = {}
    for row in rows:
        grouped.setdefault((row["seed"], row["policy"]), []).append(
            row["paired_margin"]
        )
    seeds = sorted({seed for seed, _policy in grouped})
    results = []
    for seed in seeds:
        live = grouped[(seed, "live")]
        portfolio = grouped[(seed, "portfolio")]
        if len(live) != REPETITIONS or len(portfolio) != REPETITIONS:
            raise ValueError(f"seed {seed} does not have {REPETITIONS} repetitions per policy")
        live_mean = statistics.mean(live)
        portfolio_mean = statistics.mean(portfolio)
        results.append(
            {
                "seed": seed,
                "live_repetition_margins": live,
                "portfolio_repetition_margins": portfolio,
                "live_mean_margin": live_mean,
                "portfolio_mean_margin": portfolio_mean,
                "delta_vs_live_margin": portfolio_mean - live_mean,
                "live_repetition_sd": statistics.stdev(live),
                "portfolio_repetition_sd": statistics.stdev(portfolio),
            }
        )
    return results


def branch_summary(results: list[dict], seeds: set[int]) -> dict:
    values = [
        row["delta_vs_live_margin"] for row in results if row["seed"] in seeds
    ]
    summary = robust_summary(values)
    summary["mean_without_largest"] = (
        statistics.mean(sorted(values)[:-1]) if len(values) > 1 else None
    )
    return summary


def null_adjusted_difference(low: dict, high: dict) -> dict:
    difference = low["mean"] - high["mean"]
    standard_error = math.sqrt(
        low["standard_deviation"] ** 2 / low["n"]
        + high["standard_deviation"] ** 2 / high["n"]
    )
    return {
        "mean_difference": difference,
        "standard_error": standard_error,
        "ci95_normal": [
            difference - 1.96 * standard_error,
            difference + 1.96 * standard_error,
        ],
    }


def evaluate_followup(low: dict, high: dict, adjusted: dict) -> dict:
    directional_checks = {
        "low_mean_positive": low["mean"] > 0,
        "low_trimmed_mean_positive": low["trimmed_5pct_mean"] > 0,
        "low_mean_without_largest_positive": low["mean_without_largest"] > 0,
        "low_wins_exceed_losses": low["wins"] > low["losses"],
        "low_mean_exceeds_high_null_mean": low["mean"] > high["mean"],
    }
    directional_support = all(directional_checks.values())
    strong_check = adjusted["ci95_normal"][0] > 0
    strong_support = directional_support and strong_check
    return {
        "directional_checks": directional_checks,
        "directional_support": directional_support,
        "strong_check": {
            "low_minus_high_ci95_lower_positive": strong_check,
        },
        "strong_support": strong_support,
        "decision": (
            "strong_stochastic_support"
            if strong_support
            else "directional_stochastic_support"
            if directional_support
            else "no_stochastic_support"
        ),
        "promotion_effect": "none; deterministic worst-decile gate remains failed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--jobs", type=int, default=16)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-motion-followup-2026-07-16.json",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-motion-followup-2026-07-16.checkpoint.json",
    )
    args = parser.parse_args()
    if not 1 <= args.jobs <= 20:
        raise SystemExit("--jobs must be between 1 and 20")
    actual_sha = hashlib.sha256(args.candidate.read_bytes()).hexdigest()
    if actual_sha != CANDIDATE_SHA256:
        raise SystemExit(f"candidate checksum changed: {actual_sha}")

    frozen_protocol = protocol(args.candidate, args.jobs)
    seeds = list(range(SEED_START, SEED_START + SEEDS))
    games = {seed: generate_bronze(seed) for seed in seeds}
    features = {seed: map_features(game) for seed, game in games.items()}
    expected_keys = {
        (seed, policy, repetition)
        for seed in seeds
        for policy in ("live", "portfolio")
        for repetition in range(REPETITIONS)
    }
    rows = []
    worker_history = [args.jobs]
    if args.checkpoint.exists():
        checkpoint = json.loads(args.checkpoint.read_text())
        if not same_outcome_protocol(checkpoint["protocol"], frozen_protocol):
            raise SystemExit("checkpoint protocol differs from the frozen protocol")
        rows = checkpoint["rows"]
        worker_history = checkpoint.get(
            "worker_history", [checkpoint["protocol"]["jobs"]]
        )
        if worker_history[-1] != args.jobs:
            worker_history.append(args.jobs)
        print(f"resuming from {len(rows)}/{len(expected_keys)} paired cells", flush=True)
    completed_keys = {
        (row["seed"], row["policy"], row["repetition"]) for row in rows
    }
    if not completed_keys <= expected_keys:
        raise SystemExit("checkpoint contains cells outside the frozen protocol")

    with tempfile.TemporaryDirectory(prefix="portfolio-motion-followup-") as directory:
        temp = Path(directory)
        binaries = {}
        for index, (name, source) in enumerate(
            (("live", LIVE), ("portfolio", args.candidate), ("motion", MOTION))
        ):
            binary = temp / name
            compile_source(source, binary, f"motion_followup_{index}_{name}")
            binaries[name] = binary
        print("compiled 3 frozen sources", flush=True)
        tasks = sorted(expected_keys - completed_keys)
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    motion_row,
                    seed,
                    games[seed],
                    policy,
                    repetition,
                    binaries[policy],
                    binaries["motion"],
                ): (seed, policy, repetition)
                for seed, policy, repetition in tasks
            }
            for future in as_completed(futures):
                rows.append(future.result())
                completed = len(rows)
                if completed % 25 == 0 or completed == len(expected_keys):
                    print(f"completed {completed}/{len(expected_keys)} paired cells", flush=True)
                if completed % 50 == 0:
                    save(
                        args.checkpoint,
                        {
                            "protocol": frozen_protocol,
                            "worker_history": worker_history,
                            "rows": rows,
                        },
                    )

    rows.sort(key=lambda row: (row["seed"], row["policy"], row["repetition"]))
    results = seed_results(rows)
    low_seeds = {
        seed for seed, row in features.items() if row["banana_fruit_count"] <= THRESHOLD
    }
    high_seeds = set(seeds) - low_seeds
    low = branch_summary(results, low_seeds)
    high = branch_summary(results, high_seeds)
    adjusted = null_adjusted_difference(low, high)
    evaluation = evaluate_followup(low, high, adjusted)
    result = {
        "schema": 1,
        "scope": "locked repeated stochastic-motion follow-up; not a promotion gate",
        "protocol_document": "docs/portfolio-motion-followup-2026-07-16.md",
        "protocol": frozen_protocol,
        "worker_history": worker_history,
        "candidate": {
            "path": str(args.candidate.relative_to(REPO)),
            "sha256": actual_sha,
        },
        "branch_seed_counts": {"low_banana": len(low_seeds), "high_banana": len(high_seeds)},
        "low_banana_seed_summary": low,
        "high_banana_exact_live_null_summary": high,
        "low_minus_high_null_adjusted": adjusted,
        "evaluation": evaluation,
        "map_features": {str(seed): features[seed] for seed in seeds},
        "seed_results": results,
        "rows": rows,
    }
    save(args.output, result)
    if args.checkpoint.exists():
        args.checkpoint.unlink()
    print(
        json.dumps(
            {
                "branch_seed_counts": result["branch_seed_counts"],
                "low_banana_seed_summary": low,
                "high_banana_exact_live_null_summary": high,
                "low_minus_high_null_adjusted": adjusted,
                "evaluation": evaluation,
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
