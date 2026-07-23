#!/usr/bin/env python3
"""Validate and summarize the frozen D39 shack-evacuation macro preflight."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cgauto.analyze_d37_macro_preflight import OPPONENTS, key, mean, sha256, summarize
from cgauto.analyze_d38_macro_deficit_preflight import read_rows, validate_rows


def paired_advantages(left_rows: list[dict], right_rows: list[dict]) -> list[int]:
    left = {key(row): row for row in left_rows}
    right = {key(row): row for row in right_rows}
    if set(left) != set(right):
        return []
    return [left[task]["margin"] - right[task]["margin"] for task in sorted(left)]


def paired_summary(values: list[int]) -> dict:
    return {
        "cells": len(values),
        "mean_margin_advantage": mean(values),
        "positive": sum(value > 0 for value in values),
        "zero": sum(value == 0 for value in values),
        "negative": sum(value < 0 for value in values),
    }


def analyze(
    evacuation_rows: list[dict],
    deficit_rows: list[dict],
    random_rows: list[dict],
    *,
    repeat_verified: bool,
    expected_seeds: set[int],
    opponents: tuple[str, ...] = OPPONENTS,
) -> dict:
    evacuation_integrity = validate_rows(
        evacuation_rows,
        policy="evacuation",
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
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
    evacuation = summarize(evacuation_rows)
    deficit = summarize(deficit_rows)
    random = summarize(random_rows)
    versus_deficit = paired_advantages(evacuation_rows, deficit_rows)
    versus_random = paired_advantages(evacuation_rows, random_rows)

    evacuation_by_key = {key(row): row for row in evacuation_rows}
    random_by_key = {key(row): row for row in random_rows}
    family_values: dict[str, list[int]] = {opponent: [] for opponent in opponents}
    if set(evacuation_by_key) == set(random_by_key):
        for task in sorted(evacuation_by_key):
            family_values[task[2]].append(
                evacuation_by_key[task]["margin"] - random_by_key[task]["margin"]
            )
    family_advantages = {
        opponent: mean(values) for opponent, values in sorted(family_values.items())
    }
    nonnegative_families = sum(value >= 0 for value in family_advantages.values())
    minimum_family_advantage = min(family_advantages.values(), default=0.0)
    worker_two_improvement = evacuation["worker_two_rate"] - deficit["worker_two_rate"]
    gates = {
        "evacuation_integrity": evacuation_integrity["complete"],
        "deficit_ablation_integrity": deficit_integrity["complete"],
        "random_integrity": random_integrity["complete"],
        "evacuation_repeat_byte_identical": repeat_verified,
        "margin_advantage_over_random_at_least_50": mean(versus_random) >= 50.0,
        "margin_advantage_over_deficit_at_least_50": mean(versus_deficit) >= 50.0,
        "worker_two_rate_at_least_90pct": evacuation["worker_two_rate"] >= 0.90,
        "worker_two_improvement_over_deficit_at_least_40pp": worker_two_improvement >= 0.40,
        "worker_three_rate_at_least_15pct": evacuation["worker_three_rate"] >= 0.15,
        "crop_rate_at_least_60pct": evacuation["renewable_crop_rate"] >= 0.60,
        "median_nonidle_jobs_at_least_4": evacuation["median_nonidle_jobs"] >= 4,
        "at_least_6_nonnegative_opponent_families": nonnegative_families >= 6,
        "no_opponent_family_below_minus_10": minimum_family_advantage >= -10.0,
    }
    passed = all(gates.values())
    return {
        "protocol": "D39 shack-evacuation TRAIN-deficit macro teacher preflight",
        "decision": (
            "open_behavior_learning_protocol"
            if passed
            else "close_evacuation_deficit_teacher"
        ),
        "preflight_pass": passed,
        "integrity": {
            "evacuation": evacuation_integrity,
            "deficit_ablation": deficit_integrity,
            "random": random_integrity,
            "repeat_verified": repeat_verified,
        },
        "evacuation": evacuation,
        "deficit_ablation": deficit,
        "random": random,
        "paired_vs_deficit": paired_summary(versus_deficit),
        "paired_vs_random": paired_summary(versus_random),
        "worker_two_improvement_over_deficit": worker_two_improvement,
        "opponent_family_advantages_vs_random": family_advantages,
        "nonnegative_opponent_families": nonnegative_families,
        "minimum_opponent_family_advantage": minimum_family_advantage,
        "gates": gates,
        "failed_gates": [name for name, value in gates.items() if not value],
    }


def main() -> int:
    base = Path(__file__).resolve().parents[1] / "data" / "analysis" / "live-agent-6553250"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--evacuation-a",
        type=Path,
        default=base / "d39-macro-evacuation-preflight-a-9650000-9650015.tsv",
    )
    parser.add_argument(
        "--evacuation-b",
        type=Path,
        default=base / "d39-macro-evacuation-preflight-b-9650000-9650015.tsv",
    )
    parser.add_argument(
        "--deficit",
        type=Path,
        default=base / "d39-macro-deficit-ablation-9650000-9650015.tsv",
    )
    parser.add_argument(
        "--random",
        type=Path,
        default=base / "d39-macro-random-preflight-9650000-9650015.tsv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "d39-shack-evacuation-preflight-2026-07-21.json",
    )
    args = parser.parse_args()
    report = analyze(
        read_rows(args.evacuation_a),
        read_rows(args.deficit),
        read_rows(args.random),
        repeat_verified=sha256(args.evacuation_a) == sha256(args.evacuation_b),
        expected_seeds=set(range(9_650_000, 9_650_016)),
    )
    report["provenance"] = {
        "evacuation_a": {
            "path": str(args.evacuation_a),
            "sha256": sha256(args.evacuation_a),
        },
        "evacuation_b": {
            "path": str(args.evacuation_b),
            "sha256": sha256(args.evacuation_b),
        },
        "deficit": {"path": str(args.deficit), "sha256": sha256(args.deficit)},
        "random": {"path": str(args.random), "sha256": sha256(args.random)},
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "preflight_pass": report["preflight_pass"],
                "margin_vs_random": report["paired_vs_random"][
                    "mean_margin_advantage"
                ],
                "margin_vs_deficit": report["paired_vs_deficit"][
                    "mean_margin_advantage"
                ],
                "worker_two_rate": report["evacuation"]["worker_two_rate"],
                "worker_three_rate": report["evacuation"]["worker_three_rate"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
