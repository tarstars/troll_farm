#!/usr/bin/env python3
"""Run the locked prospective gate for the banana-5 geometry/live portfolio."""

from __future__ import annotations

import argparse
from concurrent.futures import as_completed, ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
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
    source_sha256,
)
from cgauto.portfolio_candidate_study import compare_branch_row  # noqa: E402
from cgauto.portfolio_prospective_gate import (  # noqa: E402
    branch_summary,
    DETERMINISTIC_OPPONENTS,
    high_branch_equivalence,
    opponent_summaries,
    save,
    same_outcome_protocol,
)
from sim.mapgen import generate_bronze  # noqa: E402

SUBMISSIONS = REPO / "cgauto/submissions"
LIVE = SUBMISSIONS / "agent-6553250-yamo-orchard-live.min.rs"
CANDIDATE = SUBMISSIONS / "candidate-agent6553250-banana5-geometry-portfolio.min.rs"
GEOMETRY = SUBMISSIONS / "candidate-agent6553250-secure-orchard-coverage.min.rs"
CANDIDATE_SHA256 = "781f35a07cd31f5b344381c0d7e1174f0e655e8076bb3084a4d5b115b5879afe"
GEOMETRY_SHA256 = "3e045b7b09f49b2f707382e769f81e779b4d2a6762fa193915ebd938d8e0bea7"
SEED_START = 10_300
SEEDS = 300
THRESHOLD = 5


def protocol(jobs: int) -> dict:
    return {
        "seed_start": SEED_START,
        "seeds": SEEDS,
        "threshold": THRESHOLD,
        "jobs": jobs,
        "candidate_sha256": source_sha256(CANDIDATE),
        "geometry_sha256": source_sha256(GEOMETRY),
        "live_sha256": source_sha256(LIVE),
        "opponents": {
            name: source_sha256(OPPONENT_SOURCES[name])
            for name in DETERMINISTIC_OPPONENTS
        },
    }


def low_branch_equivalence(rows: list[dict], low_seeds: set[int]) -> dict:
    reference = {
        (row["seed"], row["opponent"]): row
        for row in rows
        if row["policy"] == "geometry" and row["seed"] in low_seeds
    }
    mismatches = []
    cells = 0
    for row in rows:
        if row["policy"] != "portfolio" or row["seed"] not in low_seeds:
            continue
        cells += 1
        fields = compare_branch_row(row, reference[(row["seed"], row["opponent"])])
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


def evaluate_gate(low: dict, high_equivalence: dict, low_equivalence: dict, opponents: dict) -> dict:
    research_checks = {
        "high_branch_exact_live": high_equivalence["passed"],
        "low_branch_exact_geometry": low_equivalence["passed"],
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
    parser.add_argument("--jobs", type=int, default=16)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-geometry-prospective-gate-2026-07-16.json",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=REPO
        / "data/analysis/live-agent-6553250/portfolio-geometry-prospective-gate-2026-07-16.checkpoint.json",
    )
    args = parser.parse_args()
    if not 1 <= args.jobs <= 20:
        raise SystemExit("--jobs must be between 1 and 20")
    for name, path, expected in (
        ("candidate", CANDIDATE, CANDIDATE_SHA256),
        ("geometry", GEOMETRY, GEOMETRY_SHA256),
    ):
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"{name} checksum changed: {actual}")

    frozen_protocol = protocol(args.jobs)
    seeds = list(range(SEED_START, SEED_START + SEEDS))
    games = {seed: generate_bronze(seed) for seed in seeds}
    features = {seed: map_features(game) for seed, game in games.items()}
    low_seeds = {
        seed for seed, row in features.items() if row["banana_fruit_count"] <= THRESHOLD
    }
    high_seeds = set(seeds) - low_seeds
    expected_keys = {
        (seed, policy, opponent)
        for seed in seeds
        for policy in ("live", "portfolio")
        for opponent in DETERMINISTIC_OPPONENTS
    }
    expected_keys.update(
        (seed, "geometry", opponent)
        for seed in low_seeds
        for opponent in DETERMINISTIC_OPPONENTS
    )
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
    completed_keys = {(row["seed"], row["policy"], row["opponent"]) for row in rows}
    if not completed_keys <= expected_keys:
        raise SystemExit("checkpoint contains cells outside the frozen protocol")

    with tempfile.TemporaryDirectory(prefix="portfolio-geometry-gate-") as directory:
        temp = Path(directory)
        sources = {"live": LIVE, "portfolio": CANDIDATE, "geometry": GEOMETRY}
        sources.update(
            {name: OPPONENT_SOURCES[name] for name in DETERMINISTIC_OPPONENTS}
        )
        binaries = {}
        for index, (name, source) in enumerate(sources.items()):
            binary = temp / name
            compile_source(source, binary, f"geometry_gate_{index}_{name}")
            binaries[name] = binary
        print(f"compiled {len(binaries)} frozen sources", flush=True)
        tasks = sorted(expected_keys - completed_keys)
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
    low = branch_summary(rows, low_seeds)
    high = branch_summary(rows, high_seeds)
    per_opponent = opponent_summaries(rows, low_seeds)
    high_equivalence = high_branch_equivalence(rows, high_seeds)
    low_equivalence = low_branch_equivalence(rows, low_seeds)
    gate = evaluate_gate(low, high_equivalence, low_equivalence, per_opponent)
    result = {
        "schema": 1,
        "scope": "locked second-iteration prospective geometry gate; no refitting",
        "protocol_document": "docs/portfolio-geometry-prospective-gate-2026-07-16.md",
        "protocol": frozen_protocol,
        "worker_history": worker_history,
        "candidate": {
            "path": str(CANDIDATE.relative_to(REPO)),
            "sha256": CANDIDATE_SHA256,
        },
        "branch_seed_counts": {"low_banana": len(low_seeds), "high_banana": len(high_seeds)},
        "low_banana_seed_summary": low,
        "high_banana_seed_summary": high,
        "low_banana_by_opponent": per_opponent,
        "high_banana_equivalence": high_equivalence,
        "low_banana_equivalence": low_equivalence,
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
                "high_banana_equivalence": high_equivalence,
                "low_banana_equivalence": low_equivalence,
                "gate": gate,
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
