#!/usr/bin/env python3
"""Analyze the frozen Stage 2A three-worker controlled field smoke panel."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import statistics


REPO = Path(__file__).resolve().parent.parent
DEFAULT_PANEL = (
    REPO / "data/panels/norxondor-three-worker-stage2a-top5-20260719.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "norxondor-three-worker-stage2a-result-2026-07-19.json"
)
OPPONENTS = {"delineate", "wala", "norxondor", "escdemon", "laconic"}
BASELINE_SHA = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
CANDIDATE_SHA = "69237902e54232cdf31ef8e8bc0e6c25066a4c152bde36479ffb8e1ee92f8377"


def mean(rows: list[dict], value) -> float:
    return statistics.mean(value(row) for row in rows)


def summarize(rows: list[dict]) -> dict:
    third_turns = [
        row["workforce"]["training_turns"][0][1]
        for row in rows
        if len(row["workforce"]["training_turns"][0]) >= 2
    ]
    return {
        "games": len(rows),
        "mean_score": mean(rows, lambda row: row["scores"][0]),
        "mean_opponent_score": mean(rows, lambda row: row["scores"][1]),
        "mean_margin": mean(rows, lambda row: row["scores"][0] - row["scores"][1]),
        "mean_wood": mean(rows, lambda row: row["wood"][0]),
        "mean_fruit": mean(rows, lambda row: row["fruit"][0]),
        "wins": sum(row["win"] for row in rows),
        "three_worker_games": sum(row["workforce"]["max"][0] >= 3 for row in rows),
        "terminal_workers": [row["workforce"]["final"][0] for row in rows],
        "third_worker_turns": third_turns,
        "median_third_worker_turn": statistics.median(third_turns) if third_turns else None,
        "diagnostics": sum((row.get("diagnostics", []) for row in rows), []),
    }


def bootstrap_delta(
    baseline: list[dict], candidate: list[dict], value, repetitions: int = 20_000
) -> dict:
    rng = random.Random(20260719)
    draws = []
    for _ in range(repetitions):
        left = [rng.choice(baseline) for _ in baseline]
        right = [rng.choice(candidate) for _ in candidate]
        draws.append(mean(right, value) - mean(left, value))
    draws.sort()
    return {
        "repetitions": repetitions,
        "p2_5": draws[int(repetitions * 0.025)],
        "median": draws[repetitions // 2],
        "p97_5": draws[int(repetitions * 0.975)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    panel = json.loads(args.panel.read_text())
    rows = panel.get("rows") or []
    by_bot = defaultdict(list)
    for row in rows:
        by_bot[row["bot"]].append(row)
    baseline = by_bot["baseline"]
    candidate = by_bot["candidate"]
    baseline_summary = summarize(baseline)
    candidate_summary = summarize(candidate)
    score_delta = candidate_summary["mean_score"] - baseline_summary["mean_score"]
    margin_delta = candidate_summary["mean_margin"] - baseline_summary["mean_margin"]

    identities = {(row["bot"], row["opponent"], row["repetition"]) for row in rows}
    expected = {
        (bot, opponent, 0) for bot in ("baseline", "candidate") for opponent in OPPONENTS
    }
    valid = (
        panel.get("status") == "complete"
        and len(rows) == 10
        and identities == expected
        and not any(row.get("diagnostics") for row in rows)
    )
    gates = {
        "ten_valid_games": valid,
        "candidate_three_workers_at_least_4_of_5": candidate_summary["three_worker_games"] >= 4,
        "candidate_mean_score_not_below_baseline": score_delta >= 0,
        "candidate_mean_margin_no_more_than_10_below_baseline": margin_delta >= -10,
    }

    per_opponent = {}
    for opponent in sorted(OPPONENTS):
        per_opponent[opponent] = {
            bot: {
                "game_id": next(row for row in by_bot[bot] if row["opponent"] == opponent)[
                    "game_id"
                ],
                "score": next(row for row in by_bot[bot] if row["opponent"] == opponent)[
                    "scores"
                ][0],
                "opponent_score": next(
                    row for row in by_bot[bot] if row["opponent"] == opponent
                )["scores"][1],
                "margin": (
                    next(row for row in by_bot[bot] if row["opponent"] == opponent)[
                        "scores"
                    ][0]
                    - next(row for row in by_bot[bot] if row["opponent"] == opponent)[
                        "scores"
                    ][1]
                ),
                "wood": next(row for row in by_bot[bot] if row["opponent"] == opponent)[
                    "wood"
                ][0],
                "workers": next(
                    row for row in by_bot[bot] if row["opponent"] == opponent
                )["workforce"]["final"][0],
                "successful_training_turns": next(
                    row for row in by_bot[bot] if row["opponent"] == opponent
                )["workforce"]["training_turns"][0],
                "training_attempts": next(
                    row for row in by_bot[bot] if row["opponent"] == opponent
                )["commands"]["train_attempts"],
            }
            for bot in ("baseline", "candidate")
        }

    reached = [row for row in candidate if row["workforce"]["max"][0] >= 3]
    missed = [row for row in candidate if row["workforce"]["max"][0] < 3]
    payload = {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "panel": str(args.panel),
        "source_integrity": {
            "baseline_expected_sha256": BASELINE_SHA,
            "candidate_expected_sha256": CANDIDATE_SHA,
            "baseline_observed_sha256": panel["sources"]["baseline"]["sha256"],
            "candidate_observed_sha256": panel["sources"]["candidate"]["sha256"],
            "pass": panel["sources"]["baseline"]["sha256"] == BASELINE_SHA
            and panel["sources"]["candidate"]["sha256"] == CANDIDATE_SHA,
        },
        "baseline": baseline_summary,
        "candidate": candidate_summary,
        "candidate_minus_baseline": {
            "mean_score": score_delta,
            "mean_opponent_score": candidate_summary["mean_opponent_score"]
            - baseline_summary["mean_opponent_score"],
            "mean_margin": margin_delta,
            "mean_wood": candidate_summary["mean_wood"] - baseline_summary["mean_wood"],
            "mean_fruit": candidate_summary["mean_fruit"] - baseline_summary["mean_fruit"],
            "wins": candidate_summary["wins"] - baseline_summary["wins"],
        },
        "unpaired_bootstrap": {
            "score_delta": bootstrap_delta(baseline, candidate, lambda row: row["scores"][0]),
            "margin_delta": bootstrap_delta(
                baseline, candidate, lambda row: row["scores"][0] - row["scores"][1]
            ),
        },
        "candidate_activation_split": {
            "reached_three": summarize(reached),
            "missed_three": summarize(missed),
        },
        "per_opponent": per_opponent,
        "gates": gates,
        "stage2a_pass": all(gates.values()),
        "stage2b_eligible": all(gates.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    return 0 if payload["stage2a_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

