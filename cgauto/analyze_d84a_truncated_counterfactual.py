#!/usr/bin/env python3
"""Audit D84a truncated counterfactual value and optimistic latency."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


HORIZONS = (1, 2, 4, 8, 16, 32)
ARMS = ("control", "fell", "harvest", "renew")
TIE_PRIORITY = {"control": 0, "harvest": 1, "renew": 2, "fell": 3}
VALUE_FLOOR = 5.6201171875
P95_LIMIT_US = 35_000
MAXIMUM_LIMIT_US = 45_000

ROOT_FIELDS = (
    "root_seen",
    "root_turn",
    "root_state_hash",
    "root_candidate_count",
    "arm_available",
    "arm_prior_rank",
    "arm_action_plane",
    "interventions",
)
ENDPOINT_PARITY_FIELDS = (
    "post_root_decisions",
    "endpoint_turn",
    "done",
    "own_score",
    "opponent_score",
    "margin",
    "own_liquid",
    "opponent_liquid",
    "liquid_margin",
    "own_workers",
    "opponent_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "selected_decisions",
    "selected_jobs",
    "selected_nonidle_jobs",
    "selected_renew_jobs",
    "own_created_crops",
    "opponent_created_crops",
    "ambiguous_created_crops",
    "action_hash",
    "state_hash",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return (int(row["map_seed"]), int(row["seat"]), row["opponent"])


def arm_key(row: dict[str, str]) -> tuple[int, int, str, str]:
    return (*task_key(row), row["arm"])


def endpoint_key(row: dict[str, str]) -> tuple[int, int, str, int, str]:
    return (*task_key(row), int(row["horizon"]), row["arm"])


def structural_rows(rows: Iterable[dict[str, str]]) -> list[tuple[tuple[str, str], ...]]:
    return [
        tuple((name, value) for name, value in row.items() if name != "elapsed_us")
        for row in rows
    ]


def percentile(values: Iterable[int], fraction: float) -> int:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("percentile of empty sequence")
    return ordered[max(0, math.ceil(fraction * len(ordered)) - 1)]


def choose_arm(arms: dict[str, dict[str, str]]) -> str:
    control = arms["control"]
    eligible = [control]
    eligible.extend(
        row
        for arm, row in arms.items()
        if arm != "control" and int(row["arm_available"]) == 1
    )
    best = max(
        eligible,
        key=lambda row: (int(row["liquid_margin"]), -TIE_PRIORITY[row["arm"]]),
    )
    if int(best["liquid_margin"]) <= int(control["liquid_margin"]):
        return "control"
    return best["arm"]


def mean(values: Iterable[int | float]) -> float:
    return statistics.fmean(values)


def latency_by_horizon(
    first: list[dict[str, str]], second: list[dict[str, str]]
) -> dict[int, dict[str, float | int]]:
    repeats = []
    for rows in (first, second):
        grouped: dict[tuple[int, int, str, int], dict[str, dict[str, str]]] = defaultdict(dict)
        for row in rows:
            grouped[(*task_key(row), int(row["horizon"]))][row["arm"]] = row
        aggregate = {}
        for key, arms in grouped.items():
            if int(arms["control"]["root_seen"]) == 0:
                continue
            durations = [
                int(row["elapsed_us"])
                for arm, row in arms.items()
                if arm == "control" or int(row["arm_available"]) == 1
            ]
            aggregate[key] = (sum(durations), max(durations))
        repeats.append(aggregate)

    result = {}
    for horizon in HORIZONS:
        keys = sorted(
            key
            for key in repeats[0]
            if key[-1] == horizon and key in repeats[1]
        )
        serial = [max(repeats[0][key][0], repeats[1][key][0]) for key in keys]
        ideal = [max(repeats[0][key][1], repeats[1][key][1]) for key in keys]
        result[horizon] = {
            "rooted_tasks": len(keys),
            "ideal_parallel_median_us": percentile(ideal, 0.5),
            "ideal_parallel_p95_us": percentile(ideal, 0.95),
            "ideal_parallel_maximum_us": max(ideal),
            "serial_median_us": percentile(serial, 0.5),
            "serial_p95_us": percentile(serial, 0.95),
            "serial_maximum_us": max(serial),
        }
    return result


def analyze(args: argparse.Namespace) -> dict[str, object]:
    protocol = Path(args.protocol).resolve()
    runner = Path(args.runner).resolve()
    signal_a_path = Path(args.signal_a).resolve()
    signal_b_path = Path(args.signal_b).resolve()
    latency_a_path = Path(args.latency_a).resolve()
    latency_b_path = Path(args.latency_b).resolve()
    truth_path = Path(args.truth).resolve()

    signal_a = read_tsv(signal_a_path)
    signal_b = read_tsv(signal_b_path)
    latency_a = read_tsv(latency_a_path)
    latency_b = read_tsv(latency_b_path)
    truth_rows = read_tsv(truth_path)

    signal_structural_repeat = structural_rows(signal_a) == structural_rows(signal_b)
    latency_structural_repeat = structural_rows(latency_a) == structural_rows(latency_b)
    signal_expected_rows = len(signal_a) == len(signal_b) == 512 * 4 * len(HORIZONS)
    latency_expected_rows = len(latency_a) == len(latency_b) == 128 * 4 * len(HORIZONS)

    signal_index = {endpoint_key(row): row for row in signal_a}
    truth = {arm_key(row): row for row in truth_rows}
    unique_signal_keys = len(signal_index) == len(signal_a)
    unique_truth_keys = len(truth) == len(truth_rows) == 512 * 4

    root_join_failures = 0
    missing_truth_arms = 0
    for row in signal_a:
        truth_row = truth.get(arm_key(row))
        if truth_row is None:
            missing_truth_arms += 1
            continue
        root_join_failures += int(any(row[field] != truth_row[field] for field in ROOT_FIELDS))

    mechanics_failures = sum(
        int(row[field])
        for row in signal_a
        for field in (
            "nonfinite_feature_failures",
            "illegal_selection_failures",
            "fallback_mismatch_failures",
            "invalid_direct_commands",
            "provenance_failures",
            "deposit_prediction_failures",
        )
    )
    endpoint_accounting_failures = sum(
        int(
            (int(row["root_seen"]) == 0 and int(row["post_root_decisions"]) != 0)
            or (
                int(row["root_seen"]) == 1
                and int(row["post_root_decisions"]) != int(row["horizon"])
                and int(row["done"]) == 0
            )
            or int(row["post_root_decisions"]) > int(row["horizon"])
        )
        for row in signal_a
    )

    grouped_endpoints: dict[
        tuple[int, int, str, int], dict[str, dict[str, str]]
    ] = defaultdict(dict)
    for row in signal_a:
        grouped_endpoints[(*task_key(row), int(row["horizon"]))][row["arm"]] = row
    unavailable_parity_failures = 0
    incomplete_arm_sets = 0
    for arms in grouped_endpoints.values():
        incomplete_arm_sets += int(set(arms) != set(ARMS))
        if "control" not in arms:
            continue
        control = arms["control"]
        for arm, row in arms.items():
            if arm == "control" or int(row["arm_available"]) == 1:
                continue
            unavailable_parity_failures += int(
                any(row[field] != control[field] for field in ENDPOINT_PARITY_FIELDS)
            )

    signal_subset = [row for row in signal_a if int(row["map_seed"]) < 9_914_008]
    latency_matches_signal = structural_rows(signal_subset) == structural_rows(latency_a)

    integrity_gates = {
        "complete_signal_4x512x6_repeats": signal_expected_rows,
        "complete_latency_4x128x6_repeats": latency_expected_rows,
        "signal_structural_repeat_exact": signal_structural_repeat,
        "latency_structural_repeat_exact": latency_structural_repeat,
        "latency_structure_matches_signal_subset": latency_matches_signal,
        "unique_complete_keys": unique_signal_keys and unique_truth_keys,
        "exact_d82_root_and_arm_join": root_join_failures == 0 and missing_truth_arms == 0,
        "zero_mechanics_numeric_or_fallback_failures": mechanics_failures == 0,
        "zero_endpoint_accounting_failures": endpoint_accounting_failures == 0,
        "complete_arm_sets": incomplete_arm_sets == 0,
        "unavailable_arms_match_control": unavailable_parity_failures == 0,
    }
    integrity_pass = all(integrity_gates.values())

    latency = latency_by_horizon(latency_a, latency_b)
    horizon_results: dict[str, object] = {}
    passing_horizons = []
    for horizon in HORIZONS:
        selected = []
        endpoint_turn_spreads = []
        for key, arms in grouped_endpoints.items():
            if key[-1] != horizon:
                continue
            selected_arm = choose_arm(arms)
            selected.append((key, selected_arm, arms["control"]))
            eligible = [arms["control"]] + [
                row
                for arm, row in arms.items()
                if arm != "control" and int(row["arm_available"]) == 1
            ]
            endpoint_turn_spreads.append(
                max(int(row["endpoint_turn"]) for row in eligible)
                - min(int(row["endpoint_turn"]) for row in eligible)
            )

        margin_deltas = []
        own_deltas = []
        opponent_deltas = []
        rooted_deltas = []
        family_deltas: dict[str, list[int]] = defaultdict(list)
        selected_arm_counts: Counter[str] = Counter()
        crop_successes = 0
        worker_three_successes = 0
        control_worker_three_successes = 0
        rooted_tasks = 0
        rooted_interventions = 0
        for key, selected_arm, control_endpoint in selected:
            selected_truth = truth[(*key[:3], selected_arm)]
            control_truth = truth[(*key[:3], "control")]
            margin_delta = int(selected_truth["margin"]) - int(control_truth["margin"])
            own_delta = int(selected_truth["own_score"]) - int(control_truth["own_score"])
            opponent_delta = int(selected_truth["opponent_score"]) - int(
                control_truth["opponent_score"]
            )
            margin_deltas.append(margin_delta)
            own_deltas.append(own_delta)
            opponent_deltas.append(opponent_delta)
            family_deltas[key[2]].append(margin_delta)
            selected_arm_counts[selected_arm] += 1
            crop_successes += int(int(selected_truth["own_created_crops"]) > 0)
            worker_three_successes += int(int(selected_truth["max_own_workers"]) >= 3)
            control_worker_three_successes += int(int(control_truth["max_own_workers"]) >= 3)
            if int(control_endpoint["root_seen"]) == 1:
                rooted_tasks += 1
                rooted_deltas.append(margin_delta)
                rooted_interventions += int(selected_arm != "control")

        family_means = {
            family: mean(values) for family, values in sorted(family_deltas.items())
        }
        nonnegative_families = sum(value >= 0 for value in family_means.values())
        semantic_breadth = sum(
            selected_arm_counts[arm] >= 8 for arm in ("fell", "harvest", "renew")
        )
        control_worker_three_rate = control_worker_three_successes / len(selected)
        worker_three_rate = worker_three_successes / len(selected)
        worker_three_degradation = control_worker_three_rate - worker_three_rate
        value_metrics = {
            "tasks": len(selected),
            "rooted_tasks": rooted_tasks,
            "mean_terminal_margin_gain": mean(margin_deltas),
            "oracle_capture": mean(margin_deltas) / 11.240234375,
            "rooted_strict_improvement_rate": sum(value > 0 for value in rooted_deltas)
            / rooted_tasks,
            "rooted_regression_rate": sum(value < 0 for value in rooted_deltas) / rooted_tasks,
            "mean_own_score_delta": mean(own_deltas),
            "mean_opponent_score_delta": mean(opponent_deltas),
            "opponent_family_mean_margin_gains": family_means,
            "nonnegative_opponent_families": nonnegative_families,
            "worst_opponent_family_mean": min(family_means.values()),
            "rooted_intervention_rate": rooted_interventions / rooted_tasks,
            "selected_arm_counts": dict(sorted(selected_arm_counts.items())),
            "semantic_arms_selected_at_least_eight": semantic_breadth,
            "crop_rate": crop_successes / len(selected),
            "control_worker_three_rate": control_worker_three_rate,
            "worker_three_rate": worker_three_rate,
            "worker_three_degradation": worker_three_degradation,
            "endpoint_turn_spread_mean": mean(endpoint_turn_spreads),
            "endpoint_turn_spread_maximum": max(endpoint_turn_spreads),
        }
        value_gates = {
            "mean_gain_at_least_half_d82_oracle": value_metrics[
                "mean_terminal_margin_gain"
            ]
            >= VALUE_FLOOR,
            "strict_improvement_at_least_30_percent": value_metrics[
                "rooted_strict_improvement_rate"
            ]
            >= 0.30,
            "regression_at_most_25_percent": value_metrics["rooted_regression_rate"]
            <= 0.25,
            "own_nonnegative_or_opponent_nonpositive": value_metrics[
                "mean_own_score_delta"
            ]
            >= 0
            or value_metrics["mean_opponent_score_delta"] <= 0,
            "six_nonnegative_families_and_worst_at_least_minus_2": nonnegative_families
            >= 6
            and min(family_means.values()) >= -2,
            "intervention_rate_10_to_70_percent": 0.10
            <= value_metrics["rooted_intervention_rate"]
            <= 0.70,
            "two_semantic_arms_selected_at_least_eight": semantic_breadth >= 2,
            "crop_creation_100_percent": value_metrics["crop_rate"] == 1.0,
            "worker_three_degradation_at_most_5_points": worker_three_degradation <= 0.05,
        }
        latency_metrics = latency[horizon]
        latency_gates = {
            "ideal_parallel_p95_at_most_35ms": latency_metrics[
                "ideal_parallel_p95_us"
            ]
            <= P95_LIMIT_US,
            "ideal_parallel_maximum_at_most_45ms": latency_metrics[
                "ideal_parallel_maximum_us"
            ]
            <= MAXIMUM_LIMIT_US,
        }
        value_pass = all(value_gates.values())
        latency_pass = all(latency_gates.values())
        horizon_pass = integrity_pass and value_pass and latency_pass
        if horizon_pass:
            passing_horizons.append(horizon)
        horizon_results[str(horizon)] = {
            "value": value_metrics,
            "latency": latency_metrics,
            "value_gates": value_gates,
            "latency_gates": latency_gates,
            "value_pass": value_pass,
            "latency_pass": latency_pass,
            "pass": horizon_pass,
        }

    decision = (
        "pass_freeze_shortest_horizon_open_d84b_proxy_fidelity"
        if passing_horizons
        else "reject_close_direct_online_threatened_response_monte_carlo"
    )
    return {
        "scope": (
            "consumed-map actual-opponent optimistic truncated-lookahead feasibility only; "
            "no proxy, controller, candidate, sealed map, or platform action"
        ),
        "protocol": str(protocol),
        "protocol_sha256": sha256(protocol),
        "inputs": {
            "runner": str(runner),
            "runner_sha256": sha256(runner),
            "signal_a": str(signal_a_path),
            "signal_a_sha256": sha256(signal_a_path),
            "signal_b": str(signal_b_path),
            "signal_b_sha256": sha256(signal_b_path),
            "latency_a": str(latency_a_path),
            "latency_a_sha256": sha256(latency_a_path),
            "latency_b": str(latency_b_path),
            "latency_b_sha256": sha256(latency_b_path),
            "d82_truth": str(truth_path),
            "d82_truth_sha256": sha256(truth_path),
        },
        "audit": {
            "signal_rows_per_repeat": len(signal_a),
            "latency_rows_per_repeat": len(latency_a),
            "tasks": 512,
            "rooted_tasks": sum(
                int(row["root_seen"]) == 1
                for row in signal_a
                if row["arm"] == "control" and int(row["horizon"]) == 1
            ),
            "root_join_failures": root_join_failures,
            "missing_truth_arms": missing_truth_arms,
            "mechanics_numeric_or_fallback_failures": mechanics_failures,
            "endpoint_accounting_failures": endpoint_accounting_failures,
            "incomplete_arm_sets": incomplete_arm_sets,
            "unavailable_parity_failures": unavailable_parity_failures,
        },
        "integrity_gates": integrity_gates,
        "integrity_pass": integrity_pass,
        "horizons": horizon_results,
        "passing_horizons": passing_horizons,
        "shortest_passing_horizon": min(passing_horizons) if passing_horizons else None,
        "decision": decision,
        "pass": bool(passing_horizons),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--runner", required=True)
    parser.add_argument("--signal-a", required=True)
    parser.add_argument("--signal-b", required=True)
    parser.add_argument("--latency-a", required=True)
    parser.add_argument("--latency-b", required=True)
    parser.add_argument("--truth", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = analyze(args)
    output = Path(args.output)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        f"decision={result['decision']} integrity={result['integrity_pass']} "
        f"passing_horizons={result['passing_horizons']}"
    )


if __name__ == "__main__":
    main()
