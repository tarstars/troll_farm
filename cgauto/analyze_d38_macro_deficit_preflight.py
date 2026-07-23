#!/usr/bin/env python3
"""Validate and summarize the frozen D38 TRAIN-deficit macro preflight."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from cgauto.analyze_d37_macro_preflight import (
    FLOAT_FIELDS,
    INTEGER_FIELDS,
    OPPONENTS,
    key,
    mean,
    sha256,
    summarize,
    validate_rows as validate_d37_rows,
)


D38_INTEGER_FIELDS = INTEGER_FIELDS + ("deposit_prediction_failures",)


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for field in D38_INTEGER_FIELDS:
            row[field] = int(row[field])
        for field in FLOAT_FIELDS:
            row[field] = float(row[field])
    return rows


def validate_rows(
    rows: list[dict],
    *,
    policy: str,
    expected_seeds: set[int],
    opponents: tuple[str, ...] = OPPONENTS,
) -> dict:
    integrity = validate_d37_rows(
        rows,
        policy=policy,
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
    integrity["deposit_prediction_failures"] = sum(
        row["deposit_prediction_failures"] for row in rows
    )
    integrity["complete"] = (
        integrity["complete"] and integrity["deposit_prediction_failures"] == 0
    )
    return integrity


def analyze(
    deficit_rows: list[dict],
    random_rows: list[dict],
    *,
    repeat_verified: bool,
    expected_seeds: set[int],
    opponents: tuple[str, ...] = OPPONENTS,
) -> dict:
    deficit_integrity = validate_rows(
        deficit_rows,
        policy="deficit",
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
    random_integrity = validate_rows(
        random_rows,
        policy="random",
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
    deficit = summarize(deficit_rows)
    random = summarize(random_rows)
    deficit_by_key = {key(row): row for row in deficit_rows}
    random_by_key = {key(row): row for row in random_rows}
    paired: list[int] = []
    family_values: dict[str, list[int]] = {opponent: [] for opponent in opponents}
    if set(deficit_by_key) == set(random_by_key):
        for task in sorted(deficit_by_key):
            advantage = deficit_by_key[task]["margin"] - random_by_key[task]["margin"]
            paired.append(advantage)
            family_values[task[2]].append(advantage)
    family_advantages = {
        opponent: mean(values) for opponent, values in sorted(family_values.items())
    }
    nonnegative_families = sum(value >= 0 for value in family_advantages.values())
    minimum_family_advantage = min(family_advantages.values(), default=0.0)
    margin_advantage = mean(paired)
    gates = {
        "deficit_integrity": deficit_integrity["complete"],
        "random_integrity": random_integrity["complete"],
        "deficit_repeat_byte_identical": repeat_verified,
        "deficit_margin_advantage_at_least_50": margin_advantage >= 50.0,
        "deficit_crop_rate_at_least_60pct": deficit["renewable_crop_rate"] >= 0.60,
        "deficit_worker_two_rate_at_least_80pct": deficit["worker_two_rate"] >= 0.80,
        "deficit_worker_three_rate_at_least_15pct": deficit["worker_three_rate"] >= 0.15,
        "deficit_median_nonidle_jobs_at_least_4": deficit["median_nonidle_jobs"] >= 4,
        "at_least_6_nonnegative_opponent_families": nonnegative_families >= 6,
        "no_opponent_family_below_minus_10": minimum_family_advantage >= -10.0,
    }
    passed = all(gates.values())
    return {
        "protocol": "D38 TRAIN-deficit complete-macro teacher preflight",
        "decision": (
            "open_behavior_learning_protocol" if passed else "close_deficit_teacher"
        ),
        "preflight_pass": passed,
        "integrity": {
            "deficit": deficit_integrity,
            "random": random_integrity,
            "repeat_verified": repeat_verified,
        },
        "deficit": deficit,
        "random": random,
        "paired": {
            "cells": len(paired),
            "mean_margin_advantage": margin_advantage,
            "positive": sum(value > 0 for value in paired),
            "zero": sum(value == 0 for value in paired),
            "negative": sum(value < 0 for value in paired),
        },
        "opponent_family_advantages": family_advantages,
        "nonnegative_opponent_families": nonnegative_families,
        "minimum_opponent_family_advantage": minimum_family_advantage,
        "gates": gates,
        "failed_gates": [name for name, value in gates.items() if not value],
    }


def main() -> int:
    base = Path(__file__).resolve().parents[1] / "data" / "analysis" / "live-agent-6553250"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--deficit-a",
        type=Path,
        default=base / "d38-macro-deficit-preflight-a-9630000-9630015.tsv",
    )
    parser.add_argument(
        "--deficit-b",
        type=Path,
        default=base / "d38-macro-deficit-preflight-b-9630000-9630015.tsv",
    )
    parser.add_argument(
        "--random",
        type=Path,
        default=base / "d38-macro-random-preflight-9630000-9630015.tsv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "d38-macro-deficit-preflight-2026-07-21.json",
    )
    args = parser.parse_args()
    report = analyze(
        read_rows(args.deficit_a),
        read_rows(args.random),
        repeat_verified=sha256(args.deficit_a) == sha256(args.deficit_b),
        expected_seeds=set(range(9_630_000, 9_630_016)),
    )
    report["provenance"] = {
        "deficit_a": {"path": str(args.deficit_a), "sha256": sha256(args.deficit_a)},
        "deficit_b": {"path": str(args.deficit_b), "sha256": sha256(args.deficit_b)},
        "random": {"path": str(args.random), "sha256": sha256(args.random)},
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "preflight_pass": report["preflight_pass"],
                "margin_advantage": report["paired"]["mean_margin_advantage"],
                "worker_two_rate": report["deficit"]["worker_two_rate"],
                "worker_three_rate": report["deficit"]["worker_three_rate"],
                "crop_rate": report["deficit"]["renewable_crop_rate"],
                "prediction_failures": report["integrity"]["deficit"][
                    "deposit_prediction_failures"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
