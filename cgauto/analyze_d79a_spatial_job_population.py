#!/usr/bin/env python3
"""Audit the frozen D79a spatial target/job scorer population preflight."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.make_d79a_spatial_job_population import PARAMETERS, population


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d79a-spatial-target-job-population-protocol-2026-07-21.md"
POPULATION = ANALYSIS / "d79a-spatial-job-population.tsv"
RUN_A = ANALYSIS / "d79a-spatial-job-population-a-9670000-9670003.tsv"
RUN_B = ANALYSIS / "d79a-spatial-job-population-b-9670000-9670003.tsv"
D40_REFERENCE = ANALYSIS / "d40-macro-work-conserving-preflight-a-9670000-9670015.tsv"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d79_spatial_job_population.rs"
GENERATOR_SOURCE = ROOT / "cgauto" / "make_d79a_spatial_job_population.py"
OUTPUT = ANALYSIS / "d79a-spatial-target-job-population-result.json"

EXPECTED_PROTOCOL_SHA256 = "fbbc571ceaaa705ebb004c16af4f73907c16f644a235d82a744e73590a1509b4"
EXPECTED_POPULATION_SHA256 = "19c09391398e1441dd89b2a3d94acc13ffbbff62b75e3385c0afd7389f382895"
EXPECTED_D40_REFERENCE_SHA256 = "653dee375b1922bd43b74e6e9aa1b27503d8017350f3b8dcf3baed197827b8a5"
EXPECTED_ENV_SOURCE_SHA256 = "19d54cc89051c43a4a002c595b52a6403075581125d31e4fb152f6fb3cb70ede"
EXPECTED_PRIOR_SOURCE_SHA256 = "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
EXPECTED_RUNNER_SOURCE_SHA256 = "1b4a54f07f314b71b9998c33c2e7fc4d086feb976074dafec4e641bda6fdaa8d"
EXPECTED_GENERATOR_SOURCE_SHA256 = "fb8b8be1a7f3932c78401d0e09612bbcdbd5c7e38a33dec39bdbad5ed63833ee"

MAP_START = 9_670_000
MAP_STOP = 9_670_004
POLICIES = 33
RANDOM_POLICIES = 32
TASKS = 64
NONIDLE_PLANES = ("bank", "fell_bank", "harvest_bank", "renew", "mine_bank")
FLOAT_REFERENCE_FIELDS = ("own_return", "opponent_return", "margin_return")


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = list(reader.fieldnames or ())
    return rows, fields


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def verify_population_reconstruction() -> int:
    rows, fields = read_table(POPULATION)
    expected_fields = ["policy", *(f"param_{index:03d}" for index in range(PARAMETERS))]
    if fields != expected_fields:
        raise RuntimeError("D79a population schema mismatch")
    expected = population()
    if len(rows) != len(expected):
        raise RuntimeError("D79a population size mismatch")
    mismatches = 0
    for row, (label, values) in zip(rows, expected):
        mismatches += int(row["policy"] != label)
        mismatches += sum(
            row[f"param_{index:03d}"] != f"{value:.8f}"
            for index, value in enumerate(values)
        )
    if mismatches:
        raise RuntimeError(f"D79a population reconstruction mismatches: {mismatches}")
    return mismatches


def summarize_policy(
    rows: list[dict[str, str]],
    zero: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    margins = np.asarray([int(row["margin"]) for row in rows], dtype=np.float64)
    own_scores = np.asarray([int(row["own_score"]) for row in rows], dtype=np.float64)
    opponent_scores = np.asarray(
        [int(row["opponent_score"]) for row in rows], dtype=np.float64
    )
    changes = sum(row["action_hash"] != zero[task_key(row)]["action_hash"] for row in rows)
    nonidle_planes = [
        plane for plane in NONIDLE_PLANES if sum(int(row[plane]) for row in rows) > 0
    ]
    return {
        "tasks": len(rows),
        "mean_margin": float(margins.mean()),
        "mean_own_score": float(own_scores.mean()),
        "mean_opponent_score": float(opponent_scores.mean()),
        "crop_rate": float(np.mean([int(row["own_created_crops"]) > 0 for row in rows])),
        "worker_three_rate": float(np.mean([int(row["own_workers"]) >= 3 for row in rows])),
        "changed_action_hash_tasks": int(changes),
        "changed_action_hash_rate": changes / len(rows),
        "rate_decisions": sum(int(row["rate_decisions"]) for row in rows),
        "rate_overrides": sum(int(row["rate_overrides"]) for row in rows),
        "selected_prior_rank_sum": sum(
            int(row["selected_prior_rank_sum"]) for row in rows
        ),
        "selected_prior_rank_max": max(
            int(row["selected_prior_rank_max"]) for row in rows
        ),
        "near_opponent_targets": sum(int(row["near_opponent_targets"]) for row in rows),
        "nonidle_action_planes": nonidle_planes,
        "distinct_nonidle_action_planes": len(nonidle_planes),
    }


def population_metrics(summaries: dict[str, dict]) -> dict:
    random = {name: row for name, row in summaries.items() if name != "zero"}
    zero = summaries["zero"]
    means = [row["mean_margin"] for row in random.values()]
    active_action_hash = sorted(
        name
        for name, row in random.items()
        if 0.10 <= row["changed_action_hash_rate"] <= 0.90
    )
    active_override_and_planes = sorted(
        name
        for name, row in random.items()
        if row["rate_overrides"] >= 128 and row["distinct_nonidle_action_planes"] >= 3
    )
    active_near_opponent = sorted(
        name for name, row in random.items() if row["near_opponent_targets"] >= 1
    )
    crop_safe = sorted(
        name for name, row in random.items() if row["crop_rate"] >= 0.95
    )
    worker_threshold = zero["worker_three_rate"] - 0.10
    worker_safe = sorted(
        name for name, row in random.items() if row["worker_three_rate"] >= worker_threshold
    )
    return {
        "zero_mean_margin": zero["mean_margin"],
        "zero_worker_three_rate": zero["worker_three_rate"],
        "worker_three_floor": worker_threshold,
        "random_mean_margin_minimum": min(means),
        "random_mean_margin_maximum": max(means),
        "random_mean_margin_span": max(means) - min(means),
        "random_means_above_zero": sum(mean > zero["mean_margin"] for mean in means),
        "random_means_below_zero": sum(mean < zero["mean_margin"] for mean in means),
        "active_action_hash_policies": active_action_hash,
        "active_override_and_plane_policies": active_override_and_planes,
        "active_near_opponent_policies": active_near_opponent,
        "crop_safe_policies": crop_safe,
        "worker_three_safe_policies": worker_safe,
    }


def oracle_metrics(by_policy: dict[str, list[dict[str, str]]]) -> dict:
    zero = {task_key(row): row for row in by_policy["zero"]}
    all_rows = {
        label: {task_key(row): row for row in rows} for label, rows in by_policy.items()
    }
    chosen = []
    for task in sorted(zero):
        anchor = zero[task]
        worker_floor = max(2, int(anchor["own_workers"]) - 1)
        eligible = [
            (label, rows[task])
            for label, rows in all_rows.items()
            if int(rows[task]["own_created_crops"]) > 0
            and int(rows[task]["own_workers"]) >= worker_floor
        ]
        if not eligible:
            raise RuntimeError(f"D79a oracle has no safe arm for {task}")
        label, selected = min(
            eligible,
            key=lambda item: (-int(item[1]["margin"]), item[0]),
        )
        chosen.append(
            {
                "task": task,
                "opponent": task[2],
                "policy": label,
                "margin_gain": int(selected["margin"]) - int(anchor["margin"]),
                "own_score_delta": int(selected["own_score"]) - int(anchor["own_score"]),
                "opponent_score_delta": int(selected["opponent_score"])
                - int(anchor["opponent_score"]),
            }
        )
    opponent_gains: dict[str, list[int]] = defaultdict(list)
    for row in chosen:
        opponent_gains[row["opponent"]].append(row["margin_gain"])
    return {
        "tasks": len(chosen),
        "mean_margin_gain": float(np.mean([row["margin_gain"] for row in chosen])),
        "strict_improvement_rate": float(
            np.mean([row["margin_gain"] > 0 for row in chosen])
        ),
        "mean_own_score_delta": float(
            np.mean([row["own_score_delta"] for row in chosen])
        ),
        "mean_opponent_score_delta": float(
            np.mean([row["opponent_score_delta"] for row in chosen])
        ),
        "opponent_mean_margin_gains": {
            opponent: float(np.mean(values))
            for opponent, values in sorted(opponent_gains.items())
        },
        "selected_policy_counts": dict(sorted(Counter(row["policy"] for row in chosen).items())),
    }


def gate_report(surface: dict, oracle: dict, integrity: dict) -> tuple[dict, dict, dict, str]:
    integrity_gates = {
        "complete_byte_identical_33x64_repeats": integrity["complete_repeats"],
        "exact_population_reconstruction": integrity["population_reconstruction_mismatches"] == 0,
        "zero_exact_d40_prefix_parity": integrity["zero_parity_failures"] == 0,
        "zero_mechanics_and_numeric_failures": integrity["mechanics_and_numeric_failures"] == 0,
        "zero_telemetry_consistency_failures": integrity["telemetry_consistency_failures"] == 0,
    }
    activity_gates = {
        "at_least_24_action_hash_active_policies": len(surface["active_action_hash_policies"]) >= 24,
        "at_least_24_override_and_plane_active_policies": len(
            surface["active_override_and_plane_policies"]
        )
        >= 24,
        "at_least_24_near_opponent_active_policies": len(
            surface["active_near_opponent_policies"]
        )
        >= 24,
    }
    safety_gates = {
        "at_least_24_crop_safe_policies": len(surface["crop_safe_policies"]) >= 24,
        "at_least_24_worker_three_safe_policies": len(
            surface["worker_three_safe_policies"]
        )
        >= 24,
        "random_mean_margin_span_at_least_30": surface["random_mean_margin_span"] >= 30,
        "random_means_both_above_and_below_zero": surface["random_means_above_zero"] >= 1
        and surface["random_means_below_zero"] >= 1,
    }
    opponent_gains = oracle["opponent_mean_margin_gains"]
    headroom_gates = {
        "oracle_mean_margin_gain_at_least_20": oracle["mean_margin_gain"] >= 20,
        "oracle_strict_improvement_rate_at_least_half": oracle["strict_improvement_rate"] >= 0.50,
        "oracle_own_nonnegative_or_opponent_nonpositive": oracle["mean_own_score_delta"] >= 0
        or oracle["mean_opponent_score_delta"] <= 0,
        "all_eight_opponent_family_gains_positive": len(opponent_gains) == 8
        and all(value > 0 for value in opponent_gains.values()),
    }
    groups = [integrity_gates, activity_gates, safety_gates, headroom_gates]
    groups = [{name: bool(value) for name, value in group.items()} for group in groups]
    integrity_gates, activity_gates, safety_gates, headroom_gates = groups
    if not all(integrity_gates.values()):
        decision = "integrity_failure"
    elif not all(activity_gates.values()):
        decision = "activity_failure_close_scorer_initialization"
    elif not all(safety_gates.values()):
        decision = "safety_failure_close_unconstrained_all_rate_scoring"
    elif not all(headroom_gates.values()):
        decision = "headroom_failure_close_spatial_scorer"
    else:
        decision = "pass_freeze_interface_open_d80"
    return integrity_gates, activity_gates, safety_gates, headroom_gates, decision


def main() -> None:
    prerequisites = (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (POPULATION, EXPECTED_POPULATION_SHA256),
        (D40_REFERENCE, EXPECTED_D40_REFERENCE_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
        (GENERATOR_SOURCE, EXPECTED_GENERATOR_SOURCE_SHA256),
    )
    for path, expected in prerequisites:
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D79a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D79a repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D79a result")

    reconstruction_mismatches = verify_population_reconstruction()
    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    repeats_equal = RUN_A.read_bytes() == RUN_B.read_bytes()
    labels = sorted(set(row["policy"] for row in rows_a))
    expected_labels = sorted(label for label, _ in population())
    if fields_a != fields_b or labels != expected_labels or len(rows_a) != POLICIES * TASKS:
        raise RuntimeError("D79a matrix schema, policy, or size mismatch")
    opponents = sorted(set(row["opponent"] for row in rows_a))
    expected_tasks = {
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in opponents
    }
    if len(opponents) != 8 or len(expected_tasks) != TASKS:
        raise RuntimeError("D79a task coverage mismatch")
    by_policy = {
        label: sorted(
            [row for row in rows_a if row["policy"] == label], key=task_key
        )
        for label in labels
    }
    if any({task_key(row) for row in rows} != expected_tasks for rows in by_policy.values()):
        raise RuntimeError("D79a incomplete or duplicate policy grid")

    mechanics_failures = sum(
        int(row["invalid_direct_commands"])
        + int(row["provenance_failures"])
        + int(row["deposit_prediction_failures"])
        + int(row["nonfinite_feature_failures"])
        + int(row["illegal_selection_failures"])
        + int(int(row["max_own_workers"]) > 3)
        + int(float(row["reward_identity_error"]) > 1.0e-4)
        for row in rows_a
    )
    telemetry_failures = sum(
        int(int(row["rate_overrides"]) > int(row["rate_decisions"]))
        + int(int(row["near_opponent_targets"]) > int(row["rate_decisions"]))
        + int(int(row["selected_prior_rank_sum"]) < int(row["rate_overrides"]))
        + int(int(row["selected_prior_rank_max"]) > 767)
        + int(
            sum(int(row[plane]) for plane in ("train_none", "train_producer", "train_chopper", "idle", *NONIDLE_PLANES))
            != int(row["selected_decisions"])
        )
        for row in rows_a
    )

    reference_rows, reference_fields = read_table(D40_REFERENCE)
    reference = {
        task_key(row): row
        for row in reference_rows
        if MAP_START <= int(row["map_seed"]) < MAP_STOP
    }
    if len(reference) != TASKS:
        raise RuntimeError("D79a D40 reference prefix mismatch")
    common = [field for field in reference_fields if field != "policy"]
    if any(field not in fields_a for field in common):
        raise RuntimeError("D79a is missing D40 parity fields")
    parity_failures = []
    for actual in by_policy["zero"]:
        expected = reference[task_key(actual)]
        for field in common:
            equal = (
                abs(float(expected[field]) - float(actual[field])) <= 1.0e-6
                if field in FLOAT_REFERENCE_FIELDS
                else expected[field] == actual[field]
            )
            if not equal:
                parity_failures.append(
                    (task_key(actual), field, expected[field], actual[field])
                )

    zero = {task_key(row): row for row in by_policy["zero"]}
    summaries = {
        label: summarize_policy(rows, zero) for label, rows in by_policy.items()
    }
    surface = population_metrics(summaries)
    oracle = oracle_metrics(by_policy)
    integrity = {
        "policies": len(labels),
        "tasks_per_policy": TASKS,
        "rows": len(rows_a),
        "complete_repeats": bool(repeats_equal and len(rows_b) == POLICIES * TASKS),
        "population_reconstruction_mismatches": reconstruction_mismatches,
        "zero_parity_failures": len(parity_failures),
        "zero_parity_failure_examples": parity_failures[:5],
        "mechanics_and_numeric_failures": mechanics_failures,
        "telemetry_consistency_failures": telemetry_failures,
    }
    integrity_gates, activity_gates, safety_gates, headroom_gates, decision = gate_report(
        surface, oracle, integrity
    )
    all_gates = {
        **integrity_gates,
        **activity_gates,
        **safety_gates,
        **headroom_gates,
    }
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "population": str(POPULATION),
            "population_sha256": sha256(POPULATION),
            "run_a": str(RUN_A),
            "run_a_sha256": sha256(RUN_A),
            "run_b": str(RUN_B),
            "run_b_sha256": sha256(RUN_B),
            "d40_reference": str(D40_REFERENCE),
            "d40_reference_sha256": sha256(D40_REFERENCE),
            "runner_source_sha256": sha256(RUNNER_SOURCE),
            "generator_source_sha256": sha256(GENERATOR_SOURCE),
        },
        "audit": integrity,
        "summaries": summaries,
        "surface": surface,
        "oracle": oracle,
        "gates": {
            "integrity": integrity_gates,
            "activity": activity_gates,
            "safety": safety_gates,
            "headroom": headroom_gates,
            "all": all_gates,
        },
        "pass": all(all_gates.values()),
        "decision": decision,
        "scope": "consumed-map representation preflight only; random policies are unselectable and no platform action is authorized",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
