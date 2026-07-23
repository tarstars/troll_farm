#!/usr/bin/env python3
"""Validate and summarize the frozen D40 work-conserving macro preflight."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cgauto.analyze_d37_macro_preflight import OPPONENTS, key, mean, sha256, summarize
from cgauto.analyze_d38_macro_deficit_preflight import read_rows, validate_rows
from cgauto.analyze_d39_shack_evacuation_preflight import paired_advantages, paired_summary


def analyze(
    work_rows: list[dict],
    evacuation_rows: list[dict],
    random_rows: list[dict],
    *,
    repeat_verified: bool,
    expected_seeds: set[int],
    opponents: tuple[str, ...] = OPPONENTS,
) -> dict:
    work_integrity = validate_rows(
        work_rows,
        policy="work_conserving",
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
    evacuation_integrity = validate_rows(
        evacuation_rows,
        policy="evacuation",
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
    random_integrity = validate_rows(
        random_rows,
        policy="random",
        expected_seeds=expected_seeds,
        opponents=opponents,
    )
    work = summarize(work_rows)
    evacuation = summarize(evacuation_rows)
    random = summarize(random_rows)
    versus_evacuation = paired_advantages(work_rows, evacuation_rows)
    versus_random = paired_advantages(work_rows, random_rows)

    work_by_key = {key(row): row for row in work_rows}
    random_by_key = {key(row): row for row in random_rows}
    family_values: dict[str, list[int]] = {opponent: [] for opponent in opponents}
    if set(work_by_key) == set(random_by_key):
        for task in sorted(work_by_key):
            family_values[task[2]].append(
                work_by_key[task]["margin"] - random_by_key[task]["margin"]
            )
    family_advantages = {
        opponent: mean(values) for opponent, values in sorted(family_values.items())
    }
    nonnegative_families = sum(value >= 0 for value in family_advantages.values())
    minimum_family_advantage = min(family_advantages.values(), default=0.0)
    worker_three_improvement = work["worker_three_rate"] - evacuation["worker_three_rate"]
    work_idle = work["actions"]["idle"]
    evacuation_idle = evacuation["actions"]["idle"]
    gates = {
        "work_conserving_integrity": work_integrity["complete"],
        "evacuation_ablation_integrity": evacuation_integrity["complete"],
        "random_integrity": random_integrity["complete"],
        "work_conserving_repeat_byte_identical": repeat_verified,
        "margin_advantage_over_random_at_least_50": mean(versus_random) >= 50.0,
        "margin_advantage_over_evacuation_at_least_20": mean(versus_evacuation) >= 20.0,
        "worker_two_rate_at_least_90pct": work["worker_two_rate"] >= 0.90,
        "worker_three_rate_at_least_50pct": work["worker_three_rate"] >= 0.50,
        "worker_three_improvement_over_evacuation_at_least_15pp": worker_three_improvement
        >= 0.15,
        "idle_at_most_half_evacuation": work_idle <= 0.5 * evacuation_idle,
        "crop_rate_at_least_60pct": work["renewable_crop_rate"] >= 0.60,
        "median_nonidle_jobs_at_least_4": work["median_nonidle_jobs"] >= 4,
        "at_least_6_nonnegative_opponent_families": nonnegative_families >= 6,
        "no_opponent_family_below_minus_10": minimum_family_advantage >= -10.0,
    }
    passed = all(gates.values())
    return {
        "protocol": "D40 work-conserving deficit macro teacher preflight",
        "decision": (
            "open_behavior_learning_protocol"
            if passed
            else "close_work_conserving_teacher"
        ),
        "preflight_pass": passed,
        "integrity": {
            "work_conserving": work_integrity,
            "evacuation_ablation": evacuation_integrity,
            "random": random_integrity,
            "repeat_verified": repeat_verified,
        },
        "work_conserving": work,
        "evacuation_ablation": evacuation,
        "random": random,
        "paired_vs_evacuation": paired_summary(versus_evacuation),
        "paired_vs_random": paired_summary(versus_random),
        "worker_three_improvement_over_evacuation": worker_three_improvement,
        "idle_ratio_vs_evacuation": work_idle / evacuation_idle if evacuation_idle else 0.0,
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
        "--work-a",
        type=Path,
        default=base / "d40-macro-work-conserving-preflight-a-9670000-9670015.tsv",
    )
    parser.add_argument(
        "--work-b",
        type=Path,
        default=base / "d40-macro-work-conserving-preflight-b-9670000-9670015.tsv",
    )
    parser.add_argument(
        "--evacuation",
        type=Path,
        default=base / "d40-macro-evacuation-ablation-9670000-9670015.tsv",
    )
    parser.add_argument(
        "--random",
        type=Path,
        default=base / "d40-macro-random-preflight-9670000-9670015.tsv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "d40-work-conserving-preflight-2026-07-21.json",
    )
    args = parser.parse_args()
    report = analyze(
        read_rows(args.work_a),
        read_rows(args.evacuation),
        read_rows(args.random),
        repeat_verified=sha256(args.work_a) == sha256(args.work_b),
        expected_seeds=set(range(9_670_000, 9_670_016)),
    )
    report["provenance"] = {
        "work_a": {"path": str(args.work_a), "sha256": sha256(args.work_a)},
        "work_b": {"path": str(args.work_b), "sha256": sha256(args.work_b)},
        "evacuation": {
            "path": str(args.evacuation),
            "sha256": sha256(args.evacuation),
        },
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
                "margin_vs_evacuation": report["paired_vs_evacuation"][
                    "mean_margin_advantage"
                ],
                "worker_two_rate": report["work_conserving"]["worker_two_rate"],
                "worker_three_rate": report["work_conserving"]["worker_three_rate"],
                "idle_ratio": report["idle_ratio_vs_evacuation"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
