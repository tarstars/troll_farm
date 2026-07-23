#!/usr/bin/env python3
"""Validate and summarize the frozen D37 complete-macro preflight."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics


OPPONENTS = (
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
    "script_boss",
    "silver_boss",
)

INTEGER_FIELDS = (
    "map_seed",
    "seat",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_workers",
    "opponent_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "selected_decisions",
    "selected_jobs",
    "selected_nonidle_jobs",
    "selected_renew_jobs",
    "own_created_crops",
    "opponent_created_crops",
    "ambiguous_created_crops",
    "action_hash",
    "state_hash",
    "train_none",
    "train_producer",
    "train_chopper",
    "idle",
    "bank",
    "fell_bank",
    "harvest_bank",
    "renew",
    "mine_bank",
)

FLOAT_FIELDS = ("own_return", "opponent_return", "margin_return")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field in INTEGER_FIELDS:
            row[field] = int(row[field])
        for field in FLOAT_FIELDS:
            row[field] = float(row[field])
    return rows


def mean(values: list[float | int]) -> float:
    return float(statistics.fmean(values)) if values else 0.0


def key(row: dict) -> tuple[int, int, str]:
    return row["map_seed"], row["seat"], row["opponent"]


def validate_rows(
    rows: list[dict],
    *,
    policy: str,
    expected_seeds: set[int],
    opponents: tuple[str, ...] = OPPONENTS,
) -> dict:
    expected = {
        (seed, seat, opponent)
        for seed in expected_seeds
        for seat in (0, 1)
        for opponent in opponents
    }
    actual = [key(row) for row in rows]
    return_errors = 0
    for row in rows:
        return_errors += int(abs(100.0 * row["own_return"] - row["own_score"]) > 1e-4)
        return_errors += int(
            abs(100.0 * row["opponent_return"] - row["opponent_score"]) > 1e-4
        )
        return_errors += int(
            abs(
                100.0 * row["margin_return"]
                - (row["own_score"] - row["opponent_score"])
            )
            > 1e-4
        )
    counters = {
        "rows": len(rows),
        "expected_rows": len(expected),
        "unexpected_policy_rows": sum(row["policy"] != policy for row in rows),
        "duplicate_keys": len(actual) - len(set(actual)),
        "missing_keys": len(expected - set(actual)),
        "unexpected_keys": len(set(actual) - expected),
        "margin_identity_errors": sum(
            row["margin"] != row["own_score"] - row["opponent_score"] for row in rows
        ),
        "return_identity_errors": return_errors,
        "invalid_direct_commands": sum(row["invalid_direct_commands"] for row in rows),
        "provenance_failures": sum(row["provenance_failures"] for row in rows),
        "worker_cap_errors": sum(row["own_workers"] > 3 for row in rows),
        "empty_decision_episodes": sum(row["selected_decisions"] == 0 for row in rows),
        "action_count_errors": sum(
            sum(
                row[field]
                for field in (
                    "train_none",
                    "train_producer",
                    "train_chopper",
                    "idle",
                    "bank",
                    "fell_bank",
                    "harvest_bank",
                    "renew",
                    "mine_bank",
                )
            )
            != row["selected_decisions"]
            for row in rows
        ),
    }
    counters["complete"] = all(
        value == 0
        for name, value in counters.items()
        if name
        not in {
            "rows",
            "expected_rows",
            "complete",
        }
    ) and counters["rows"] == counters["expected_rows"]
    return counters


def summarize(rows: list[dict]) -> dict:
    by_opponent: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_opponent[row["opponent"]].append(row)
    margins = [row["margin"] for row in rows]
    action_fields = (
        "train_none",
        "train_producer",
        "train_chopper",
        "idle",
        "bank",
        "fell_bank",
        "harvest_bank",
        "renew",
        "mine_bank",
    )
    return {
        "episodes": len(rows),
        "mean_own_score": mean([row["own_score"] for row in rows]),
        "mean_opponent_score": mean([row["opponent_score"] for row in rows]),
        "mean_margin": mean(margins),
        "worker_two_rate": mean([row["own_workers"] >= 2 for row in rows]),
        "worker_three_rate": mean([row["own_workers"] >= 3 for row in rows]),
        "renewable_crop_rate": mean([row["own_created_crops"] > 0 for row in rows]),
        "renew_selection_rate": mean([row["selected_renew_jobs"] > 0 for row in rows]),
        "median_nonidle_jobs": float(
            statistics.median(row["selected_nonidle_jobs"] for row in rows)
        ),
        "mean_decisions": mean([row["selected_decisions"] for row in rows]),
        "mean_nonidle_jobs": mean([row["selected_nonidle_jobs"] for row in rows]),
        "completed_jobs": sum(row["completed_jobs"] for row in rows),
        "invalidated_jobs": sum(row["invalidated_jobs"] for row in rows),
        "catastrophes": sum(value <= -100 for value in margins),
        "catastrophe_rate": mean([value <= -100 for value in margins]),
        "negative_margin_mass": sum(-value for value in margins if value < 0),
        "actions": {field: sum(row[field] for row in rows) for field in action_fields},
        "by_opponent": {
            opponent: {
                "episodes": len(bucket),
                "mean_own_score": mean([row["own_score"] for row in bucket]),
                "mean_opponent_score": mean(
                    [row["opponent_score"] for row in bucket]
                ),
                "mean_margin": mean([row["margin"] for row in bucket]),
                "worker_two_rate": mean([row["own_workers"] >= 2 for row in bucket]),
                "worker_three_rate": mean(
                    [row["own_workers"] >= 3 for row in bucket]
                ),
            }
            for opponent, bucket in sorted(by_opponent.items())
        },
    }


def analyze(
    heuristic_rows: list[dict],
    random_rows: list[dict],
    *,
    repeat_verified: bool,
    expected_seeds: set[int],
    opponents: tuple[str, ...] = OPPONENTS,
) -> dict:
    heuristic_integrity = validate_rows(
        heuristic_rows,
        policy="heuristic",
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
    random_integrity = validate_rows(
        random_rows,
        policy="random",
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
    heuristic = summarize(heuristic_rows)
    random = summarize(random_rows)
    paired = []
    heuristic_by_key = {key(row): row for row in heuristic_rows}
    random_by_key = {key(row): row for row in random_rows}
    if set(heuristic_by_key) == set(random_by_key):
        for task in sorted(heuristic_by_key):
            left = heuristic_by_key[task]
            right = random_by_key[task]
            paired.append(left["margin"] - right["margin"])
    margin_advantage = mean(paired)
    gates = {
        "heuristic_integrity": heuristic_integrity["complete"],
        "random_integrity": random_integrity["complete"],
        "heuristic_repeat_byte_identical": repeat_verified,
        "heuristic_margin_advantage_at_least_50": margin_advantage >= 50.0,
        "heuristic_crop_rate_at_least_60pct": heuristic["renewable_crop_rate"] >= 0.60,
        "heuristic_worker_two_rate_at_least_80pct": heuristic["worker_two_rate"] >= 0.80,
        "heuristic_worker_three_rate_at_least_15pct": heuristic["worker_three_rate"] >= 0.15,
        "heuristic_median_nonidle_jobs_at_least_4": heuristic["median_nonidle_jobs"]
        >= 4,
    }
    passed = all(gates.values())
    return {
        "protocol": "D37 complete factorized macro PPO preflight",
        "decision": (
            "open_behavior_initialization" if passed else "reject_initializer_before_learning"
        ),
        "preflight_pass": passed,
        "integrity": {
            "heuristic": heuristic_integrity,
            "random": random_integrity,
            "repeat_verified": repeat_verified,
        },
        "heuristic": heuristic,
        "random": random,
        "paired": {
            "cells": len(paired),
            "mean_margin_advantage": margin_advantage,
            "positive": sum(value > 0 for value in paired),
            "zero": sum(value == 0 for value in paired),
            "negative": sum(value < 0 for value in paired),
        },
        "gates": gates,
        "failed_gates": [name for name, value in gates.items() if not value],
    }


def main() -> int:
    base = Path(__file__).resolve().parents[1] / "data" / "analysis" / "live-agent-6553250"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--heuristic-a",
        type=Path,
        default=base / "d37-macro-heuristic-preflight-a-9600000-9600015.tsv",
    )
    parser.add_argument(
        "--heuristic-b",
        type=Path,
        default=base / "d37-macro-heuristic-preflight-b-9600000-9600015.tsv",
    )
    parser.add_argument(
        "--random",
        type=Path,
        default=base / "d37-macro-random-preflight-9600000-9600015.tsv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "d37-macro-preflight-2026-07-21.json",
    )
    args = parser.parse_args()
    report = analyze(
        read_rows(args.heuristic_a),
        read_rows(args.random),
        repeat_verified=sha256(args.heuristic_a) == sha256(args.heuristic_b),
        expected_seeds=set(range(9_600_000, 9_600_016)),
    )
    report["provenance"] = {
        "heuristic_a": {"path": str(args.heuristic_a), "sha256": sha256(args.heuristic_a)},
        "heuristic_b": {"path": str(args.heuristic_b), "sha256": sha256(args.heuristic_b)},
        "random": {"path": str(args.random), "sha256": sha256(args.random)},
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "preflight_pass": report["preflight_pass"],
                "margin_advantage": report["paired"]["mean_margin_advantage"],
                "worker_two_rate": report["heuristic"]["worker_two_rate"],
                "worker_three_rate": report["heuristic"]["worker_three_rate"],
                "crop_rate": report["heuristic"]["renewable_crop_rate"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
