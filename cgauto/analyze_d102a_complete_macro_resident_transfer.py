#!/usr/bin/env python3
"""Validate and analyze frozen D102a exact-D40 versus resident transfer rows."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d102a-complete-macro-resident-transfer-protocol-2026-07-22.md"
RUNNER = ROOT / "rust" / "src" / "bin" / "d102_complete_macro_resident_transfer.rs"
D40_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
RESIDENT_SOURCE = ROOT / "rust" / "src" / "bin" / "yamo_orchard_live.rs"

START_SEED = 9_824_100
MAP_COUNT = 32
POLICIES = ("d40", "resident")
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

FROZEN_SHA256 = {
    D40_SOURCE: "1e3af47fe25184790763a7dbf11818944c583794303bb986f1db28708179a2e5",
    RESIDENT_SOURCE: "5ab7cbc03ce6df022023f40c9afa605e676ce2b006496350590aa2c2e25e9449",
    RUNNER: "3caa71e7077db212e67ed566af9cdf099d587112e9659f369f1e7df58770a319",
    PROTOCOL: "7511833d3b6122296fb27e81b55f10a2d1a4b52edd61f2f19a491f5478158d53",
}

INT_FIELDS = (
    "map_seed",
    "seat",
    "opponent_index",
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_workers",
    "opponent_workers",
    "max_own_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "own_created_crops",
    "opponent_created_crops",
    "joint_created_crops",
    "ambiguous_created_crops",
    "own_owned_crop_harvest_units",
    "own_reinvested_crops",
    "action_hash",
    "state_hash",
)
FLOAT_FIELDS = (
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else 0.0


def rate(rows: Iterable[dict], predicate) -> float:
    rows = list(rows)
    return mean(predicate(row) for row in rows)


def read_rows(path: Path) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    for row in rows:
        for field in INT_FIELDS:
            row[field] = int(row[field])
        for field in FLOAT_FIELDS:
            row[field] = float(row[field])
    return rows


def task_key(row: dict) -> tuple[int, int, str]:
    return row["map_seed"], row["seat"], row["opponent"]


def row_key(row: dict) -> tuple[int, int, str, str]:
    return (*task_key(row), row["policy"])


def expected_keys() -> set[tuple[int, int, str, str]]:
    return {
        (seed, seat, opponent, policy)
        for seed in range(START_SEED, START_SEED + MAP_COUNT)
        for seat in range(2)
        for opponent in OPPONENTS
        for policy in POLICIES
    }


def validate_grid(rows: list[dict]) -> dict:
    keys = [row_key(row) for row in rows]
    key_set = set(keys)
    expected = expected_keys()
    opponent_index_errors = [
        row_key(row)
        for row in rows
        if not 0 <= row["opponent_index"] < len(OPPONENTS)
        or OPPONENTS[row["opponent_index"]] != row["opponent"]
    ]
    return {
        "rows": len(rows),
        "expected_rows": len(expected),
        "unique_keys": len(key_set),
        "duplicate_rows": len(keys) - len(key_set),
        "missing_rows": len(expected - key_set),
        "unexpected_rows": len(key_set - expected),
        "opponent_index_errors": len(opponent_index_errors),
        "complete": (
            len(rows) == len(expected)
            and len(key_set) == len(expected)
            and key_set == expected
            and not opponent_index_errors
        ),
    }


def summarize_policy(rows: list[dict]) -> dict:
    return {
        "episodes": len(rows),
        "mean_own_score": mean(row["own_score"] for row in rows),
        "mean_opponent_score": mean(row["opponent_score"] for row in rows),
        "mean_margin": mean(row["margin"] for row in rows),
        "negative_margin_rate": rate(rows, lambda row: row["margin"] < 0),
        "catastrophic_margin_rate": rate(rows, lambda row: row["margin"] <= -100),
        "mean_final_workers": mean(row["own_workers"] for row in rows),
        "worker_three_rate": rate(rows, lambda row: row["max_own_workers"] >= 3),
        "exactly_two_final_workers_rate": rate(
            rows, lambda row: row["own_workers"] == 2
        ),
        "own_crop_creation_rate": rate(
            rows, lambda row: row["own_created_crops"] > 0
        ),
        "own_crop_harvest_rate": rate(
            rows, lambda row: row["own_owned_crop_harvest_units"] > 0
        ),
        "own_crop_reinvestment_rate": rate(
            rows, lambda row: row["own_reinvested_crops"] > 0
        ),
        "mean_own_created_crops": mean(row["own_created_crops"] for row in rows),
        "mean_joint_created_crops": mean(row["joint_created_crops"] for row in rows),
        "mean_own_crop_harvest_units": mean(
            row["own_owned_crop_harvest_units"] for row in rows
        ),
        "mean_own_reinvested_crops": mean(
            row["own_reinvested_crops"] for row in rows
        ),
        "mean_invalidated_jobs": mean(row["invalidated_jobs"] for row in rows),
        "mean_terminal_turn": mean(row["turn"] for row in rows),
    }


def quantiles(values: list[float]) -> dict:
    ordered = sorted(values)
    if not ordered:
        return {}

    def nearest(fraction: float) -> float:
        index = round(fraction * (len(ordered) - 1))
        return ordered[index]

    return {
        "minimum": ordered[0],
        "p10": nearest(0.10),
        "p25": nearest(0.25),
        "median": nearest(0.50),
        "p75": nearest(0.75),
        "p90": nearest(0.90),
        "maximum": ordered[-1],
    }


def analyze(rows_a: list[dict], rows_b: list[dict], repeat_identical: bool) -> dict:
    grid_a = validate_grid(rows_a)
    grid_b = validate_grid(rows_b)
    rows = rows_a
    indexed = {row_key(row): row for row in rows}
    by_policy = {
        policy: [row for row in rows if row["policy"] == policy]
        for policy in POLICIES
    }
    summaries = {
        policy: summarize_policy(policy_rows)
        for policy, policy_rows in by_policy.items()
    }

    terminal_clean = all(
        row["done"] == 1
        and row["turn"] <= 301
        and row["margin"] == row["own_score"] - row["opponent_score"]
        and abs(row["own_return"] - row["own_score"] / 100.0) <= 1e-6
        and abs(row["opponent_return"] - row["opponent_score"] / 100.0) <= 1e-6
        and abs(row["margin_return"] - row["margin"] / 100.0) <= 1e-6
        and row["reward_identity_error"] <= 1e-6
        for row in rows
    )
    provenance_clean = all(
        row["provenance_failures"] == 0
        and row["ambiguous_created_crops"] == 0
        for row in rows
    )
    d40_command_clean = all(
        row["invalid_direct_commands"] == 0
        and row["deposit_prediction_failures"] == 0
        for row in by_policy["d40"]
    )
    source_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in FROZEN_SHA256}
    source_hashes_frozen = all(
        source_hashes[str(path.relative_to(ROOT))] == expected
        for path, expected in FROZEN_SHA256.items()
    )
    runner_text = RUNNER.read_text()
    exact_controller_calls = (
        "run_work_conserving_deficit_heuristic()" in runner_text
        and "SecureOrchardBot::new()" in runner_text
        and "ours.commands(&resident_view(&game, task.seat))" in runner_text
    )

    integrity_gates = {
        "run_a_exact_grid": grid_a["complete"],
        "run_b_exact_grid": grid_b["complete"],
        "one_and_twenty_worker_runs_byte_identical": repeat_identical,
        "all_terminal_and_reward_identities_exact": terminal_clean,
        "zero_provenance_and_ambiguous_birth_failures": provenance_clean,
        "d40_zero_invalid_commands_and_deposit_failures": d40_command_clean,
        "frozen_source_hashes_match": source_hashes_frozen,
        "runner_calls_exact_frozen_controllers": exact_controller_calls,
    }

    d40 = summaries["d40"]
    resident = summaries["resident"]
    mechanism_gates = {
        "d40_own_crop_creation_rate_at_least_98pct": d40[
            "own_crop_creation_rate"
        ]
        >= 0.98,
        "d40_own_crop_harvest_rate_at_least_75pct": d40[
            "own_crop_harvest_rate"
        ]
        >= 0.75,
        "d40_own_crop_reinvestment_rate_at_least_50pct": d40[
            "own_crop_reinvestment_rate"
        ]
        >= 0.50,
        "d40_worker_three_rate_at_least_85pct": d40["worker_three_rate"] >= 0.85,
        "d40_mean_final_workforce_at_least_2_80": d40["mean_final_workers"] >= 2.80,
        "d40_harvest_rate_gain_at_least_50pp": d40["own_crop_harvest_rate"]
        - resident["own_crop_harvest_rate"]
        >= 0.50,
        "d40_mean_workforce_gain_at_least_0_70": d40["mean_final_workers"]
        - resident["mean_final_workers"]
        >= 0.70,
        "resident_own_crop_creation_rate_at_least_98pct": resident[
            "own_crop_creation_rate"
        ]
        >= 0.98,
        "resident_exactly_two_workers_rate_at_least_90pct": resident[
            "exactly_two_final_workers_rate"
        ]
        >= 0.90,
    }

    deltas = []
    family_deltas: dict[str, list[int]] = defaultdict(list)
    map_deltas: dict[int, list[int]] = defaultdict(list)
    seat_deltas: dict[int, list[int]] = defaultdict(list)
    for seed in range(START_SEED, START_SEED + MAP_COUNT):
        for seat in range(2):
            for opponent in OPPONENTS:
                d40_row = indexed[(seed, seat, opponent, "d40")]
                resident_row = indexed[(seed, seat, opponent, "resident")]
                margin_delta = d40_row["margin"] - resident_row["margin"]
                row = {
                    "map_seed": seed,
                    "seat": seat,
                    "opponent": opponent,
                    "margin_delta": margin_delta,
                    "own_score_delta": d40_row["own_score"]
                    - resident_row["own_score"],
                    "opponent_score_delta": d40_row["opponent_score"]
                    - resident_row["opponent_score"],
                }
                deltas.append(row)
                family_deltas[opponent].append(margin_delta)
                map_deltas[seed].append(margin_delta)
                seat_deltas[seat].append(margin_delta)

    margin_deltas = [row["margin_delta"] for row in deltas]
    own_deltas = [row["own_score_delta"] for row in deltas]
    opponent_score_deltas = [row["opponent_score_delta"] for row in deltas]
    ordered = sorted(margin_deltas)
    trim = math.floor(0.05 * len(ordered))
    trimmed = ordered[trim : len(ordered) - trim]
    worst_count = math.ceil(0.10 * len(ordered))
    worst_decile = ordered[:worst_count]
    map_means = [mean(values) for _, values in sorted(map_deltas.items())]
    clustered_lower = mean(map_means) - 1.96 * statistics.stdev(map_means) / math.sqrt(
        len(map_means)
    )
    family_means = {
        opponent: mean(family_deltas[opponent]) for opponent in OPPONENTS
    }
    positive_families = sum(value > 0 for value in family_means.values())
    paired = {
        "tasks": len(deltas),
        "mean_margin_delta": mean(margin_deltas),
        "trimmed_5pct_mean_margin_delta": mean(trimmed),
        "map_clustered_95pct_lower_bound": clustered_lower,
        "map_mean_delta_sd": statistics.stdev(map_means),
        "mean_own_score_delta": mean(own_deltas),
        "mean_opponent_score_delta": mean(opponent_score_deltas),
        "strict_improvement_rate": mean(value > 0 for value in margin_deltas),
        "tie_rate": mean(value == 0 for value in margin_deltas),
        "strict_regression_rate": mean(value < 0 for value in margin_deltas),
        "worst_10pct_mean_margin_delta": mean(worst_decile),
        "margin_delta_quantiles": quantiles(margin_deltas),
        "opponent_family_mean_margin_deltas": family_means,
        "positive_opponent_families": positive_families,
        "worst_opponent_family_mean_margin_delta": min(family_means.values()),
        "seat_mean_margin_deltas": {
            str(seat): mean(values) for seat, values in sorted(seat_deltas.items())
        },
        "map_mean_margin_delta_quantiles": quantiles(map_means),
    }
    value_gates = {
        "mean_margin_delta_at_least_15": paired["mean_margin_delta"] >= 15.0,
        "trimmed_mean_margin_delta_at_least_10": paired[
            "trimmed_5pct_mean_margin_delta"
        ]
        >= 10.0,
        "map_clustered_95pct_lower_bound_above_zero": paired[
            "map_clustered_95pct_lower_bound"
        ]
        > 0.0,
        "at_least_six_positive_opponent_families": positive_families >= 6,
        "worst_opponent_family_at_least_minus_5": paired[
            "worst_opponent_family_mean_margin_delta"
        ]
        >= -5.0,
        "mean_own_score_delta_at_least_20": paired["mean_own_score_delta"] >= 20.0,
        "mean_opponent_score_delta_at_most_10": paired[
            "mean_opponent_score_delta"
        ]
        <= 10.0,
        "strict_improvement_rate_at_least_55pct": paired[
            "strict_improvement_rate"
        ]
        >= 0.55,
        "strict_regression_rate_at_most_35pct": paired["strict_regression_rate"]
        <= 0.35,
        "worst_decile_mean_at_least_minus_10": paired[
            "worst_10pct_mean_margin_delta"
        ]
        >= -10.0,
        "negative_margin_rate_increase_at_most_2pp": d40["negative_margin_rate"]
        - resident["negative_margin_rate"]
        <= 0.02,
        "catastrophic_margin_rate_increase_at_most_2pp": d40[
            "catastrophic_margin_rate"
        ]
        - resident["catastrophic_margin_rate"]
        <= 0.02,
    }

    integrity_pass = all(integrity_gates.values())
    mechanism_pass = all(mechanism_gates.values())
    value_pass = all(value_gates.values())
    if not integrity_pass:
        decision = "repair_measurement_and_rerun_frozen_panel"
    elif mechanism_pass and value_pass:
        decision = "open_d102b_compact_source_deployment_feasibility"
    elif mechanism_pass:
        decision = "retain_d40_as_role_transition_teacher_do_not_package"
    else:
        decision = "close_d40_as_top3_architecture_design_role_persistent_controller"

    by_opponent = {}
    for opponent in OPPONENTS:
        by_opponent[opponent] = {
            policy: summarize_policy(
                [
                    row
                    for row in by_policy[policy]
                    if row["opponent"] == opponent
                ]
            )
            for policy in POLICIES
        }
        by_opponent[opponent]["paired_mean_margin_delta"] = family_means[opponent]

    all_gates = {**integrity_gates, **mechanism_gates, **value_gates}
    return {
        "protocol": "D102a complete-macro resident transfer audit",
        "decision": decision,
        "pass": integrity_pass and mechanism_pass and value_pass,
        "integrity_pass": integrity_pass,
        "mechanism_pass": mechanism_pass,
        "value_pass": value_pass,
        "integrity": {
            "run_a": grid_a,
            "run_b": grid_b,
            "repeat_byte_identical": repeat_identical,
            "source_hashes": source_hashes,
        },
        "summaries": summaries,
        "paired": paired,
        "by_opponent": by_opponent,
        "gates": {
            "integrity": integrity_gates,
            "mechanism": mechanism_gates,
            "value_and_robustness": value_gates,
        },
        "failed_gates": [name for name, passed in all_gates.items() if not passed],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-a",
        type=Path,
        default=BASE
        / "d102a-complete-macro-resident-transfer-a-jobs1-9824100-9824131.tsv",
    )
    parser.add_argument(
        "--run-b",
        type=Path,
        default=BASE
        / "d102a-complete-macro-resident-transfer-b-jobs20-9824100-9824131.tsv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=BASE / "d102a-complete-macro-resident-transfer-result.json",
    )
    args = parser.parse_args()
    report = analyze(
        read_rows(args.run_a),
        read_rows(args.run_b),
        repeat_identical=sha256(args.run_a) == sha256(args.run_b),
    )
    report["provenance"] = {
        "run_a": {"path": str(args.run_a), "sha256": sha256(args.run_a)},
        "run_b": {"path": str(args.run_b), "sha256": sha256(args.run_b)},
        "protocol": {"path": str(PROTOCOL), "sha256": sha256(PROTOCOL)},
        "runner": {"path": str(RUNNER), "sha256": sha256(RUNNER)},
        "analyzer": {"path": str(Path(__file__)), "sha256": sha256(Path(__file__))},
        "execution_seconds": {"jobs_1": 112.387, "jobs_20": 112.770},
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "integrity_pass": report["integrity_pass"],
                "mechanism_pass": report["mechanism_pass"],
                "value_pass": report["value_pass"],
                "mean_margin_delta": report["paired"]["mean_margin_delta"],
                "d40_harvest_rate": report["summaries"]["d40"][
                    "own_crop_harvest_rate"
                ],
                "resident_harvest_rate": report["summaries"]["resident"][
                    "own_crop_harvest_rate"
                ],
                "failed_gates": report["failed_gates"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
