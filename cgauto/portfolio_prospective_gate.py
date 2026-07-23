#!/usr/bin/env python3
"""Run the locked 300-seed prospective gate for the banana-5 portfolio."""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import statistics
import sys
import tempfile

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.offline_policy_league import (  # noqa: E402
    aggregate,
    attach_live_deltas,
    map_features,
    OPPONENT_SOURCES,
    paired_row,
    robust_summary,
    source_sha256,
)
from cgauto.portfolio_candidate_study import compare_branch_row  # noqa: E402
from sim.mapgen import generate_bronze  # noqa: E402

LIVE = REPO / "cgauto/submissions/agent-6553250-yamo-orchard-live.min.rs"
CANDIDATE = (
    REPO / "cgauto/submissions/candidate-agent6553250-banana5-stack-portfolio.min.rs"
)
CANDIDATE_SHA256 = "96ef33e77c10281510f0f3ee5ceef912bb6cf27e3b463276b8257aa6e9a234db"
DETERMINISTIC_OPPONENTS = (
    "taskplan",
    "race",
    "yield",
    "ringfix3",
    "chopharvest",
)
SEED_START = 10_000
SEEDS = 300
THRESHOLD = 5


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def protocol(candidate: Path, jobs: int) -> dict:
    return {
        "seed_start": SEED_START,
        "seeds": SEEDS,
        "threshold": THRESHOLD,
        "jobs": jobs,
        "candidate_sha256": source_sha256(candidate),
        "live_sha256": source_sha256(LIVE),
        "opponents": {
            name: source_sha256(OPPONENT_SOURCES[name])
            for name in DETERMINISTIC_OPPONENTS
        },
    }


def same_outcome_protocol(first: dict, second: dict) -> bool:
    """Worker count changes runtime only; every outcome-defining field must match."""

    return (
        {key: value for key, value in first.items() if key != "jobs"}
        == {key: value for key, value in second.items() if key != "jobs"}
    )


def branch_seed_values(rows: list[dict], branch_seeds: set[int]) -> list[float]:
    grouped = {}
    for row in rows:
        if row["policy"] == "portfolio" and row["seed"] in branch_seeds:
            grouped.setdefault(row["seed"], []).append(row["delta_vs_live_margin"])
    return [statistics.mean(grouped[seed]) for seed in sorted(grouped)]


def branch_summary(rows: list[dict], branch_seeds: set[int]) -> dict:
    values = branch_seed_values(rows, branch_seeds)
    summary = robust_summary(values)
    summary["mean_without_largest"] = (
        statistics.mean(sorted(values)[:-1]) if len(values) > 1 else None
    )
    return summary


def opponent_summaries(rows: list[dict], branch_seeds: set[int]) -> dict:
    return {
        opponent: robust_summary(
            row["delta_vs_live_margin"]
            for row in rows
            if row["policy"] == "portfolio"
            and row["opponent"] == opponent
            and row["seed"] in branch_seeds
        )
        for opponent in DETERMINISTIC_OPPONENTS
    }


def high_branch_equivalence(rows: list[dict], high_seeds: set[int]) -> dict:
    live = {
        (row["seed"], row["opponent"]): row
        for row in rows
        if row["policy"] == "live" and row["seed"] in high_seeds
    }
    mismatches = []
    cells = 0
    for row in rows:
        if row["policy"] != "portfolio" or row["seed"] not in high_seeds:
            continue
        cells += 1
        fields = compare_branch_row(row, live[(row["seed"], row["opponent"])])
        if fields:
            mismatches.append(
                {
                    "seed": row["seed"],
                    "opponent": row["opponent"],
                    "mismatch_fields": fields,
                }
            )
    return {
        "cells": cells,
        "exact_cells": cells - len(mismatches),
        "mismatch_cells": len(mismatches),
        "passed": not mismatches,
        "mismatches": mismatches[:20],
    }


def evaluate_gate(low: dict, high_equivalence: dict, opponents: dict) -> dict:
    research_checks = {
        "high_branch_exact": high_equivalence["passed"],
        "low_mean_positive": low["mean"] > 0,
        "low_trimmed_mean_positive": low["trimmed_5pct_mean"] > 0,
        "low_mean_without_largest_positive": low["mean_without_largest"] > 0,
        "low_wins_exceed_losses": low["wins"] > low["losses"],
        "every_opponent_mean_nonnegative": all(
            summary["mean"] >= 0 for summary in opponents.values()
        ),
    }
    research_passed = all(research_checks.values())
    promotion_checks = {
        "low_ci95_lower_positive": low["ci95_normal"][0] > 0,
        "low_worst_decile_nonnegative": low["worst_decile_mean"] >= 0,
    }
    promotion_ready = research_passed and all(promotion_checks.values())
    return {
        "research_checks": research_checks,
        "research_passed": research_passed,
        "promotion_checks": promotion_checks,
        "promotion_ready": promotion_ready,
        "decision": (
            "promotion_ready_pending_healthy_arena_control"
            if promotion_ready
            else "retain_as_research_candidate"
            if research_passed
            else "reject"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-prospective-gate-2026-07-16.json",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-prospective-gate-2026-07-16.checkpoint.json",
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
        (seed, policy, opponent)
        for seed in seeds
        for policy in ("live", "portfolio")
        for opponent in DETERMINISTIC_OPPONENTS
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
        (row["seed"], row["policy"], row["opponent"]) for row in rows
    }
    if not completed_keys <= expected_keys:
        raise SystemExit("checkpoint contains cells outside the frozen protocol")

    with tempfile.TemporaryDirectory(prefix="portfolio-prospective-gate-") as directory:
        temp = Path(directory)
        sources = {"live": LIVE, "portfolio": args.candidate}
        sources.update(
            {name: OPPONENT_SOURCES[name] for name in DETERMINISTIC_OPPONENTS}
        )
        binaries = {}
        for index, (name, source) in enumerate(sources.items()):
            binary = temp / name
            compile_source(source, binary, f"prospective_{index}_{name}")
            binaries[name] = binary
        print(f"compiled {len(binaries)} frozen sources", flush=True)
        tasks = sorted(expected_keys - completed_keys)
        # Each match spends most of its time in the Python referee loop.  Processes are
        # required here: threads overlap bot pipe I/O but the GIL serializes referee work.
        with ProcessPoolExecutor(max_workers=args.jobs) as executor:
            futures = {
                executor.submit(
                    paired_row,
                    seed,
                    games[seed],
                    policy,
                    opponent,
                    binaries[policy],
                    binaries[opponent],
                ): (seed, policy, opponent)
                for seed, policy, opponent in tasks
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

    rows.sort(key=lambda row: (row["seed"], row["policy"], row["opponent"]))
    attach_live_deltas(rows)
    low_seeds = {
        seed for seed, row in features.items() if row["banana_fruit_count"] <= THRESHOLD
    }
    high_seeds = set(seeds) - low_seeds
    low = branch_summary(rows, low_seeds)
    high = branch_summary(rows, high_seeds)
    per_opponent = opponent_summaries(rows, low_seeds)
    equivalence = high_branch_equivalence(rows, high_seeds)
    gate = evaluate_gate(low, equivalence, per_opponent)
    result = {
        "schema": 1,
        "scope": "locked prospective scarcity-gate validation; no refitting",
        "protocol_document": "docs/archive/legend/portfolio-prospective-gate-2026-07-16.md",
        "protocol": frozen_protocol,
        "worker_history": worker_history,
        "candidate": {
            "path": str(args.candidate.relative_to(REPO)),
            "sha256": actual_sha,
        },
        "branch_seed_counts": {"low_banana": len(low_seeds), "high_banana": len(high_seeds)},
        "low_banana_seed_summary": low,
        "high_banana_seed_summary": high,
        "low_banana_by_opponent": per_opponent,
        "high_banana_equivalence": equivalence,
        "gate": gate,
        "aggregate": aggregate(rows),
        "map_features": {str(seed): features[seed] for seed in seeds},
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
                "low_banana_opponent_means": {
                    name: summary["mean"] for name, summary in per_opponent.items()
                },
                "high_banana_equivalence": equivalence,
                "gate": gate,
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
