#!/usr/bin/env python3
"""Audit the prospective D80a one-shot contested-crop intervention."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d80a-one-shot-contested-crop-intervention-protocol-2026-07-21.md"
RUN_A = ANALYSIS / "d80a-one-shot-contested-crop-a-9910000-9910015.tsv"
RUN_B = ANALYSIS / "d80a-one-shot-contested-crop-b-9910000-9910015.tsv"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d80_one_shot_contested_crop.rs"
OUTPUT = ANALYSIS / "d80a-one-shot-contested-crop-result.json"

EXPECTED_PROTOCOL_SHA256 = "4c9670bfcddcbf2f7c39740c7db2c18daea12aefce4345bca42f99fb43c7f58e"
EXPECTED_ENV_SOURCE_SHA256 = "19d54cc89051c43a4a002c595b52a6403075581125d31e4fb152f6fb3cb70ede"
EXPECTED_PRIOR_SOURCE_SHA256 = "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
EXPECTED_RUNNER_SOURCE_SHA256 = "11c1807772f5062a0301785b3ddcb08fd8b1f20f46ae443a6a7a206f0ff36456"

MAP_START = 9_910_000
MAP_STOP = 9_910_016
TASKS = 256
ROWS = 512
ACTION_PLANES = (
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
INTERVENTION_FIELDS = {
    "policy",
    "eligible_boundaries",
    "interventions",
    "challenger_rank",
    "challenger_plane",
    "nonfinite_feature_failures",
    "illegal_selection_failures",
    "fallback_mismatch_failures",
}


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = list(reader.fieldnames or ())
    return rows, fields


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def normal_low(values: list[float]) -> float:
    array = np.asarray(values, dtype=np.float64)
    if len(array) < 2:
        return float("-inf")
    return float(array.mean() - 1.96 * array.std(ddof=1) / np.sqrt(len(array)))


def activation_metrics(
    control: dict[tuple[int, int, str], dict[str, str]],
    candidate: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    active = [row for row in candidate.values() if int(row["interventions"]) == 1]
    changed = [
        row
        for task, row in candidate.items()
        if row["action_hash"] != control[task]["action_hash"]
    ]
    return {
        "intervention_tasks": len(active),
        "changed_action_hash_tasks": len(changed),
        "changed_action_hash_rate": len(changed) / len(candidate),
        "active_seats": sorted({int(row["seat"]) for row in active}),
        "active_opponents": sorted({row["opponent"] for row in active}),
        "challenger_ranks": sorted({int(row["challenger_rank"]) for row in active}),
        "challenger_planes": sorted({int(row["challenger_plane"]) for row in active}),
    }


def stage_a_gates(audit: dict, activation: dict) -> dict[str, bool]:
    gates = {
        "complete_byte_identical_2x256_repeats": audit["complete_repeats"],
        "zero_mechanics_and_numeric_failures": audit["mechanics_and_numeric_failures"] == 0,
        "zero_intervention_accounting_failures": audit["intervention_accounting_failures"] == 0,
        "nonintervention_exact_parity": audit["nonintervention_parity_failures"] == 0,
        "intervention_equals_changed_task_count": activation["intervention_tasks"]
        == activation["changed_action_hash_tasks"],
        "intervention_tasks_between_32_and_230": 32
        <= activation["intervention_tasks"]
        <= 230,
        "changed_task_rate_between_10_and_90_percent": 0.10
        <= activation["changed_action_hash_rate"]
        <= 0.90,
        "both_seats_and_six_opponents_active": activation["active_seats"] == [0, 1]
        and len(activation["active_opponents"]) >= 6,
        "two_challenger_ranks_and_planes_active": len(activation["challenger_ranks"]) >= 2
        and len(activation["challenger_planes"]) >= 2,
    }
    return {name: bool(value) for name, value in gates.items()}


def paired_value_metrics(
    control: dict[tuple[int, int, str], dict[str, str]],
    candidate: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    active_tasks = [
        task for task, row in candidate.items() if int(row["interventions"]) == 1
    ]
    active_deltas = [
        int(candidate[task]["margin"]) - int(control[task]["margin"])
        for task in active_tasks
    ]
    own_deltas = [
        int(candidate[task]["own_score"]) - int(control[task]["own_score"])
        for task in active_tasks
    ]
    opponent_deltas = [
        int(candidate[task]["opponent_score"])
        - int(control[task]["opponent_score"])
        for task in active_tasks
    ]
    map_deltas: dict[int, list[int]] = defaultdict(list)
    family_deltas: dict[str, list[int]] = defaultdict(list)
    for task, delta in zip(active_tasks, active_deltas):
        map_deltas[task[0]].append(delta)
        family_deltas[task[2]].append(delta)
    map_means = [float(np.mean(values)) for _, values in sorted(map_deltas.items())]
    all_deltas = [
        int(candidate[task]["margin"]) - int(control[task]["margin"])
        for task in sorted(candidate)
    ]
    control_crop_rate = float(
        np.mean([int(row["own_created_crops"]) > 0 for row in control.values()])
    )
    candidate_crop_rate = float(
        np.mean([int(row["own_created_crops"]) > 0 for row in candidate.values()])
    )
    control_worker_three = float(
        np.mean([int(row["own_workers"]) >= 3 for row in control.values()])
    )
    candidate_worker_three = float(
        np.mean([int(row["own_workers"]) >= 3 for row in candidate.values()])
    )
    control_catastrophes = sum(int(row["margin"]) <= -100 for row in control.values())
    candidate_catastrophes = sum(
        int(row["margin"]) <= -100 for row in candidate.values()
    )
    control_negative_mass = sum(max(0, -int(row["margin"])) for row in control.values())
    candidate_negative_mass = sum(
        max(0, -int(row["margin"])) for row in candidate.values()
    )
    return {
        "active_tasks": len(active_tasks),
        "active_mean_margin_delta": float(np.mean(active_deltas)),
        "active_map_cluster_normal_95_low": normal_low(map_means),
        "active_map_clusters": len(map_means),
        "overall_mean_margin_delta": float(np.mean(all_deltas)),
        "active_strict_improvement_rate": float(np.mean([delta > 0 for delta in active_deltas])),
        "active_regression_rate": float(np.mean([delta < 0 for delta in active_deltas])),
        "active_mean_own_score_delta": float(np.mean(own_deltas)),
        "active_mean_opponent_score_delta": float(np.mean(opponent_deltas)),
        "active_opponent_family_mean_margin_deltas": {
            family: float(np.mean(values))
            for family, values in sorted(family_deltas.items())
        },
        "control_crop_rate": control_crop_rate,
        "candidate_crop_rate": candidate_crop_rate,
        "control_worker_three_rate": control_worker_three,
        "candidate_worker_three_rate": candidate_worker_three,
        "worker_three_degradation": control_worker_three - candidate_worker_three,
        "control_catastrophes": control_catastrophes,
        "candidate_catastrophes": candidate_catastrophes,
        "control_negative_margin_mass": control_negative_mass,
        "candidate_negative_margin_mass": candidate_negative_mass,
    }


def stage_b_gates(value: dict) -> dict[str, bool]:
    family = value["active_opponent_family_mean_margin_deltas"]
    gates = {
        "active_mean_margin_delta_at_least_4": value["active_mean_margin_delta"] >= 4,
        "active_map_cluster_lower_bound_positive": value[
            "active_map_cluster_normal_95_low"
        ]
        > 0,
        "overall_mean_margin_delta_at_least_1": value["overall_mean_margin_delta"] >= 1,
        "active_strict_improvement_at_least_55_percent": value[
            "active_strict_improvement_rate"
        ]
        >= 0.55,
        "active_regression_at_most_35_percent": value["active_regression_rate"] <= 0.35,
        "active_own_delta_at_least_minus_5": value["active_mean_own_score_delta"] >= -5,
        "active_opponent_delta_at_most_2": value["active_mean_opponent_score_delta"] <= 2,
        "six_nonnegative_families_and_worst_at_least_minus_15": sum(
            delta >= 0 for delta in family.values()
        )
        >= 6
        and min(family.values()) >= -15,
        "candidate_crop_creation_100_percent": value["candidate_crop_rate"] == 1.0,
        "worker_three_degradation_at_most_5_points": value["worker_three_degradation"] <= 0.05,
        "catastrophe_increase_at_most_2": value["candidate_catastrophes"]
        <= value["control_catastrophes"] + 2,
        "negative_margin_mass_at_most_105_percent": value[
            "candidate_negative_margin_mass"
        ]
        <= 1.05 * value["control_negative_margin_mass"],
    }
    return {name: bool(result) for name, result in gates.items()}


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D80a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D80a repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D80a result")

    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    repeats_equal = RUN_A.read_bytes() == RUN_B.read_bytes()
    if fields_a != fields_b or len(rows_a) != ROWS or len(rows_b) != ROWS:
        raise RuntimeError("D80a repeat schema or size mismatch")
    labels = sorted(set(row["policy"] for row in rows_a))
    opponents = sorted(set(row["opponent"] for row in rows_a))
    expected_tasks = {
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in opponents
    }
    if labels != ["candidate", "control"] or len(opponents) != 8 or len(expected_tasks) != TASKS:
        raise RuntimeError("D80a policy or task coverage mismatch")
    by_policy = {
        label: {task_key(row): row for row in rows_a if row["policy"] == label}
        for label in labels
    }
    if any(set(rows) != expected_tasks for rows in by_policy.values()):
        raise RuntimeError("D80a incomplete or duplicate task grid")
    control = by_policy["control"]
    candidate = by_policy["candidate"]

    mechanics_failures = sum(
        int(row["invalid_direct_commands"])
        + int(row["provenance_failures"])
        + int(row["deposit_prediction_failures"])
        + int(row["nonfinite_feature_failures"])
        + int(row["illegal_selection_failures"])
        + int(row["fallback_mismatch_failures"])
        + int(int(row["max_own_workers"]) > 3)
        + int(float(row["reward_identity_error"]) > 1.0e-4)
        + int(sum(int(row[plane]) for plane in ACTION_PLANES) != int(row["selected_decisions"]))
        for row in rows_a
    )
    accounting_failures = 0
    for row in rows_a:
        interventions = int(row["interventions"])
        eligible = int(row["eligible_boundaries"])
        rank = int(row["challenger_rank"])
        plane = int(row["challenger_plane"])
        accounting_failures += int(interventions not in (0, 1))
        accounting_failures += int(eligible != interventions)
        accounting_failures += int(
            (interventions == 0 and (rank != -1 or plane != -1))
            or (interventions == 1 and (rank not in (1, 2, 3) or plane not in (5, 6, 7)))
        )
        if row["policy"] == "control":
            accounting_failures += eligible + interventions

    parity_fields = [field for field in fields_a if field not in INTERVENTION_FIELDS]
    parity_failures = []
    for task, row in candidate.items():
        if int(row["interventions"]) != 0:
            continue
        for field in parity_fields:
            if row[field] != control[task][field]:
                parity_failures.append((task, field, control[task][field], row[field]))

    audit = {
        "rows": len(rows_a),
        "tasks": TASKS,
        "complete_repeats": bool(repeats_equal),
        "mechanics_and_numeric_failures": mechanics_failures,
        "intervention_accounting_failures": accounting_failures,
        "nonintervention_parity_failures": len(parity_failures),
        "nonintervention_parity_failure_examples": parity_failures[:5],
    }
    activation = activation_metrics(control, candidate)
    stage_a = stage_a_gates(audit, activation)
    stage_a_pass = all(stage_a.values())
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "run_a": str(RUN_A),
            "run_a_sha256": sha256(RUN_A),
            "run_b": str(RUN_B),
            "run_b_sha256": sha256(RUN_B),
            "runner_source_sha256": sha256(RUNNER_SOURCE),
        },
        "audit": audit,
        "activation": activation,
        "stage_a_gates": stage_a,
        "stage_a_pass": stage_a_pass,
        "scope": "prospective local mechanism test only; no candidate or platform authorization",
    }
    if not stage_a_pass:
        report.update(
            {
                "value_opened": False,
                "stage_b_gates": None,
                "stage_b_pass": False,
                "pass": False,
                "decision": "stage_a_failure_close_one_shot_contested_top_four",
            }
        )
    else:
        value = paired_value_metrics(control, candidate)
        stage_b = stage_b_gates(value)
        stage_b_pass = all(stage_b.values())
        report.update(
            {
                "value_opened": True,
                "value": value,
                "stage_b_gates": stage_b,
                "stage_b_pass": stage_b_pass,
                "pass": stage_b_pass,
                "decision": (
                    "pass_freeze_sparse_interface_open_d81_bounded_value_controller"
                    if stage_b_pass
                    else "stage_b_failure_close_fixed_intervention_open_bounded_rollout_discriminator"
                ),
            }
        )
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
