#!/usr/bin/env python3
"""Run the deterministic 8-seed, both-seat E7a motion smoke.

This is a fast engineering discriminator, not an Arena-value claim.  It compares a
candidate with the exact live E7a source on identical generated maps and opponent code.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import tempfile


REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.e4_orchard_mother_tie_audit import compile_runtime_shim  # noqa: E402
from cgauto.e5_ripeness_wait_audit import policy_match  # noqa: E402
from cgauto.idle_harvest_study import compile_source  # noqa: E402
from cgauto.offline_policy_league import OPPONENT_SOURCES  # noqa: E402


BASELINE = (
    REPO
    / "cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_train(trace: list[dict]) -> dict | None:
    for turn in trace:
        for command in turn["commands"]:
            fields = command.split()
            if fields and fields[0] == "TRAIN":
                return {
                    "turn": int(turn["turn"]),
                    "spec": [int(value) for value in fields[1:5]],
                }
    return None


def longest_period2_target_run(trace: list[dict]) -> int:
    """Measure consecutive ABAB MOVE targets for each unit."""

    moves: dict[int, list[tuple[int, tuple[int, int]]]] = defaultdict(list)
    for turn in trace:
        for unit_id, command in turn["by_unit"].items():
            fields = command.split()
            if fields and fields[0] == "MOVE":
                moves[int(unit_id)].append(
                    (int(turn["turn"]), (int(fields[2]), int(fields[3])))
                )
    longest = 0
    for sequence in moves.values():
        run = 0
        previous_turn = None
        previous = None
        two_back = None
        for turn, target in sequence:
            consecutive = previous_turn is not None and turn == previous_turn + 1
            if consecutive and two_back == target and previous != target:
                run += 1
            elif consecutive and previous != target:
                run = 2
            else:
                run = 1
            longest = max(longest, run)
            previous_turn, two_back, previous = turn, previous, target
    return longest


def mean(rows: list[dict], key: str) -> float:
    return statistics.mean(float(row[key]) for row in rows)


def evaluate(candidate: Path, seeds: range) -> dict:
    with tempfile.TemporaryDirectory(prefix="e7a-half-motion-") as temporary:
        directory = Path(temporary)
        baseline_binary = directory / "baseline"
        candidate_binary = directory / "candidate"
        opponent_binary = directory / "motion"
        compile_source(BASELINE, baseline_binary, "e7a_half_motion_baseline")
        compile_source(candidate, candidate_binary, "e7a_half_motion_candidate")
        compile_source(
            OPPONENT_SOURCES["motion"], opponent_binary, "e7a_half_motion_opponent"
        )
        os.environ["LD_PRELOAD"] = str(compile_runtime_shim(directory))

        rows = []
        for seed in seeds:
            for seat in (0, 1):
                baseline = policy_match(
                    seed, baseline_binary, opponent_binary, seat, False
                )
                alternate = policy_match(
                    seed, candidate_binary, opponent_binary, seat, False
                )
                rows.append(
                    {
                        "seed": seed,
                        "seat": seat,
                        "baseline_margin": baseline["margin"],
                        "candidate_margin": alternate["margin"],
                        "margin_delta": alternate["margin"] - baseline["margin"],
                        "baseline_policy_score": baseline["policy_score"],
                        "candidate_policy_score": alternate["policy_score"],
                        "baseline_opponent_score": baseline["opponent_score"],
                        "candidate_opponent_score": alternate["opponent_score"],
                        "baseline_wood": baseline["policy_wood"],
                        "candidate_wood": alternate["policy_wood"],
                        "baseline_catastrophe": baseline["margin"] <= -100,
                        "candidate_catastrophe": alternate["margin"] <= -100,
                        "baseline_period2": longest_period2_target_run(
                            baseline["policy_trace"]
                        ),
                        "candidate_period2": longest_period2_target_run(
                            alternate["policy_trace"]
                        ),
                        "baseline_first_train": first_train(baseline["policy_trace"]),
                        "candidate_first_train": first_train(alternate["policy_trace"]),
                    }
                )

    deltas = [int(row["margin_delta"]) for row in rows]
    return {
        "schema": "e7a-half-size-motion-smoke-v1",
        "evidence_boundary": "engineering discriminator; not an Arena predictor",
        "baseline": {
            "path": str(BASELINE.relative_to(REPO)),
            "bytes": BASELINE.stat().st_size,
            "sha256": sha256(BASELINE),
        },
        "candidate": {
            "path": str(candidate.relative_to(REPO)),
            "bytes": candidate.stat().st_size,
            "sha256": sha256(candidate),
        },
        "opponent": {
            "name": "motion",
            "path": str(OPPONENT_SOURCES["motion"].relative_to(REPO)),
            "sha256": sha256(OPPONENT_SOURCES["motion"]),
        },
        "seeds": list(seeds),
        "games": len(rows),
        "summary": {
            "mean_margin_delta": statistics.mean(deltas),
            "median_margin_delta": statistics.median(deltas),
            "minimum_margin_delta": min(deltas),
            "maximum_margin_delta": max(deltas),
            "seat_mean_margin_delta": {
                str(seat): statistics.mean(
                    row["margin_delta"] for row in rows if row["seat"] == seat
                )
                for seat in (0, 1)
            },
            "mean_policy_score": {
                "baseline": mean(rows, "baseline_policy_score"),
                "candidate": mean(rows, "candidate_policy_score"),
            },
            "mean_opponent_score": {
                "baseline": mean(rows, "baseline_opponent_score"),
                "candidate": mean(rows, "candidate_opponent_score"),
            },
            "mean_policy_wood": {
                "baseline": mean(rows, "baseline_wood"),
                "candidate": mean(rows, "candidate_wood"),
            },
            "catastrophes": {
                "baseline": sum(row["baseline_catastrophe"] for row in rows),
                "candidate": sum(row["candidate_catastrophe"] for row in rows),
            },
            "maximum_period2_target_run": {
                "baseline": max(row["baseline_period2"] for row in rows),
                "candidate": max(row["candidate_period2"] for row in rows),
            },
            "same_first_train": sum(
                row["baseline_first_train"] == row["candidate_first_train"]
                for row in rows
            ),
        },
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--seed-count", type=int, default=8)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    candidate = arguments.candidate.resolve()
    if arguments.seed_count <= 0:
        parser.error("--seed-count must be positive")
    result = evaluate(candidate, range(arguments.seed_count))
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
