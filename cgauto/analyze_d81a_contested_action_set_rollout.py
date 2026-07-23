#!/usr/bin/env python3
"""Audit the D81a one-boundary contested action-set rollout upper bound."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d81a-one-boundary-contested-action-set-rollout-protocol-2026-07-21.md"
RUN_A = ANALYSIS / "d81a-contested-action-set-rollout-a-9912000-9912015.tsv"
RUN_B = ANALYSIS / "d81a-contested-action-set-rollout-b-9912000-9912015.tsv"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d81_contested_action_set_rollout.rs"
OUTPUT = ANALYSIS / "d81a-contested-action-set-rollout-result.json"

EXPECTED_PROTOCOL_SHA256 = "72cd1ecea06583f1d757ffb47f37f63d23c93df90b800dcd66ce2c378765a2fc"
EXPECTED_ENV_SOURCE_SHA256 = "19d54cc89051c43a4a002c595b52a6403075581125d31e4fb152f6fb3cb70ede"
EXPECTED_PRIOR_SOURCE_SHA256 = "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
EXPECTED_RUNNER_SOURCE_SHA256 = "48996296fc6bea54a83469cd4d45c123532344e919ea6d574991ff3aa3aa00ff"

MAP_START = 9_912_000
MAP_STOP = 9_912_016
TASKS = 256
ARMS = ("control", "rank_1", "rank_2", "rank_3")
ROWS = TASKS * len(ARMS)
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
ARM_METADATA_FIELDS = {
    "arm",
    "root_seen",
    "root_turn",
    "root_state_hash",
    "root_candidate_count",
    "arm_available",
    "arm_rank",
    "arm_action_plane",
    "interventions",
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


def support_metrics(by_arm: dict[str, dict[tuple[int, int, str], dict[str, str]]]) -> dict:
    control = by_arm["control"]
    rooted = [task for task, row in control.items() if int(row["root_seen"]) == 1]
    available = [
        row
        for arm in ARMS[1:]
        for row in by_arm[arm].values()
        if int(row["arm_available"]) == 1
    ]
    return {
        "rooted_tasks": len(rooted),
        "available_noncontrol_arms": len(available),
        "availability_by_rank": {
            arm: sum(int(row["arm_available"]) for row in by_arm[arm].values())
            for arm in ARMS[1:]
        },
        "available_seats": sorted({int(row["seat"]) for row in available}),
        "available_opponents": sorted({row["opponent"] for row in available}),
        "available_action_planes": sorted(
            {int(row["arm_action_plane"]) for row in available}
        ),
    }


def support_gates(audit: dict, support: dict) -> dict[str, bool]:
    gates = {
        "complete_byte_identical_4x256_repeats": audit["complete_repeats"],
        "zero_mechanics_and_numeric_failures": audit["mechanics_and_numeric_failures"] == 0,
        "zero_root_identity_failures": audit["root_identity_failures"] == 0,
        "zero_arm_accounting_failures": audit["arm_accounting_failures"] == 0,
        "unavailable_arm_exact_control_parity": audit["unavailable_parity_failures"] == 0,
        "available_arm_intervention_changes_hash": audit["available_hash_failures"] == 0,
        "at_least_224_rooted_tasks": support["rooted_tasks"] >= 224,
        "at_least_400_available_noncontrol_arms": support[
            "available_noncontrol_arms"
        ]
        >= 400,
        "each_rank_available_at_least_64": all(
            count >= 64 for count in support["availability_by_rank"].values()
        ),
        "both_seats_all_opponents_two_planes": support["available_seats"] == [0, 1]
        and len(support["available_opponents"]) == 8
        and len(support["available_action_planes"]) >= 2,
    }
    return {name: bool(value) for name, value in gates.items()}


def arm_summaries(
    by_arm: dict[str, dict[tuple[int, int, str], dict[str, str]]]
) -> dict[str, dict]:
    control = by_arm["control"]
    result = {}
    for arm in ARMS:
        rows = by_arm[arm]
        deltas = [
            int(rows[task]["margin"]) - int(control[task]["margin"])
            for task in sorted(control)
        ]
        available = sum(int(row["arm_available"]) for row in rows.values())
        result[arm] = {
            "tasks": len(rows),
            "available_tasks": available,
            "mean_margin": float(np.mean([int(row["margin"]) for row in rows.values()])),
            "mean_margin_delta": float(np.mean(deltas)),
            "strict_improvements": sum(delta > 0 for delta in deltas),
            "regressions": sum(delta < 0 for delta in deltas),
            "crop_rate": float(
                np.mean([int(row["own_created_crops"]) > 0 for row in rows.values()])
            ),
            "worker_three_rate": float(
                np.mean([int(row["own_workers"]) >= 3 for row in rows.values()])
            ),
        }
    return result


def safe_oracle_metrics(
    by_arm: dict[str, dict[tuple[int, int, str], dict[str, str]]]
) -> dict:
    control = by_arm["control"]
    chosen = []
    no_safe = 0
    for task in sorted(control):
        anchor = control[task]
        worker_floor = max(2, int(anchor["own_workers"]) - 1)
        eligible = []
        for priority, arm in enumerate(ARMS):
            row = by_arm[arm][task]
            available = arm == "control" or int(row["arm_available"]) == 1
            safe = (
                available
                and int(row["own_created_crops"]) > 0
                and int(row["own_workers"]) >= worker_floor
            )
            if safe:
                eligible.append((priority, arm, row))
        if not eligible:
            no_safe += 1
            continue
        priority, arm, row = min(
            eligible,
            key=lambda item: (-int(item[2]["margin"]), item[0]),
        )
        del priority
        chosen.append(
            {
                "task": task,
                "arm": arm,
                "row": row,
                "rooted": int(anchor["root_seen"]) == 1,
                "margin_gain": int(row["margin"]) - int(anchor["margin"]),
                "own_score_delta": int(row["own_score"]) - int(anchor["own_score"]),
                "opponent_score_delta": int(row["opponent_score"])
                - int(anchor["opponent_score"]),
            }
        )
    rooted = [row for row in chosen if row["rooted"]]
    family: dict[str, list[int]] = defaultdict(list)
    for row in chosen:
        family[row["task"][2]].append(row["margin_gain"])
    control_worker_three = float(
        np.mean([int(row["own_workers"]) >= 3 for row in control.values()])
    )
    oracle_worker_three = float(
        np.mean([int(row["row"]["own_workers"]) >= 3 for row in chosen])
    )
    strict_counts = Counter(
        row["arm"]
        for row in chosen
        if row["arm"] != "control" and row["margin_gain"] > 0
    )
    return {
        "tasks": len(chosen),
        "no_safe_tasks": no_safe,
        "mean_margin_gain": float(np.mean([row["margin_gain"] for row in chosen])),
        "rooted_strict_improvement_rate": float(
            np.mean([row["margin_gain"] > 0 for row in rooted])
        ),
        "strictly_improved_rooted_tasks": sum(row["margin_gain"] > 0 for row in rooted),
        "rooted_tasks": len(rooted),
        "mean_own_score_delta": float(
            np.mean([row["own_score_delta"] for row in chosen])
        ),
        "mean_opponent_score_delta": float(
            np.mean([row["opponent_score_delta"] for row in chosen])
        ),
        "opponent_family_mean_margin_gains": {
            opponent: float(np.mean(values))
            for opponent, values in sorted(family.items())
        },
        "selected_arm_counts": dict(sorted(Counter(row["arm"] for row in chosen).items())),
        "strict_noncontrol_selection_counts": dict(sorted(strict_counts.items())),
        "crop_rate": float(
            np.mean([int(row["row"]["own_created_crops"]) > 0 for row in chosen])
        ),
        "control_worker_three_rate": control_worker_three,
        "worker_three_rate": oracle_worker_three,
        "worker_three_degradation": control_worker_three - oracle_worker_three,
    }


def oracle_gates(oracle: dict) -> dict[str, bool]:
    family = oracle["opponent_family_mean_margin_gains"]
    selected = oracle["strict_noncontrol_selection_counts"]
    gates = {
        "oracle_mean_margin_gain_at_least_10": oracle["mean_margin_gain"] >= 10,
        "oracle_strictly_improves_half_of_rooted_tasks": oracle[
            "rooted_strict_improvement_rate"
        ]
        >= 0.50,
        "oracle_own_nonnegative_or_opponent_nonpositive": oracle["mean_own_score_delta"] >= 0
        or oracle["mean_opponent_score_delta"] <= 0,
        "all_family_gains_positive_and_worst_at_least_3": len(family) == 8
        and all(value > 0 for value in family.values())
        and min(family.values()) >= 3,
        "two_strict_noncontrol_ranks_selected_at_least_8": sum(
            count >= 8 for count in selected.values()
        )
        >= 2,
        "oracle_crop_creation_100_percent": oracle["crop_rate"] == 1.0,
        "oracle_worker_three_degradation_at_most_5_points": oracle[
            "worker_three_degradation"
        ]
        <= 0.05,
        "control_and_safe_arm_available_every_task": oracle["tasks"] == TASKS
        and oracle["no_safe_tasks"] == 0,
    }
    return {name: bool(value) for name, value in gates.items()}


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D81a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D81a repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D81a result")

    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    repeats_equal = RUN_A.read_bytes() == RUN_B.read_bytes()
    if fields_a != fields_b or len(rows_a) != ROWS or len(rows_b) != ROWS:
        raise RuntimeError("D81a repeat schema or size mismatch")
    labels = sorted(set(row["arm"] for row in rows_a))
    opponents = sorted(set(row["opponent"] for row in rows_a))
    expected_tasks = {
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in opponents
    }
    if labels != sorted(ARMS) or len(opponents) != 8 or len(expected_tasks) != TASKS:
        raise RuntimeError("D81a arm or task coverage mismatch")
    by_arm = {
        arm: {task_key(row): row for row in rows_a if row["arm"] == arm}
        for arm in ARMS
    }
    if any(set(rows) != expected_tasks for rows in by_arm.values()):
        raise RuntimeError("D81a incomplete or duplicate arm grid")

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
    root_identity_failures = 0
    for task in expected_tasks:
        identities = {
            (
                by_arm[arm][task]["root_seen"],
                by_arm[arm][task]["root_turn"],
                by_arm[arm][task]["root_state_hash"],
                by_arm[arm][task]["root_candidate_count"],
            )
            for arm in ARMS
        }
        root_identity_failures += int(len(identities) != 1)

    accounting_failures = 0
    for row in rows_a:
        arm = row["arm"]
        root_seen = int(row["root_seen"])
        available = int(row["arm_available"])
        rank = int(row["arm_rank"])
        plane = int(row["arm_action_plane"])
        interventions = int(row["interventions"])
        expected_rank = ARMS.index(arm)
        accounting_failures += int(root_seen not in (0, 1))
        if root_seen == 0:
            accounting_failures += int(
                int(row["root_turn"]) != -1
                or int(row["root_state_hash"]) != 0
                or int(row["root_candidate_count"]) != 0
                or available != 0
                or rank != -1
                or plane != -1
                or interventions != 0
            )
        elif arm == "control":
            accounting_failures += int(
                available != 1
                or rank != 0
                or plane not in range(3, 9)
                or interventions != 0
            )
        else:
            accounting_failures += int(rank != expected_rank or available not in (0, 1))
            accounting_failures += int(
                (available == 0 and (plane != -1 or interventions != 0))
                or (available == 1 and (plane not in (5, 6, 7) or interventions != 1))
            )

    parity_fields = [field for field in fields_a if field not in ARM_METADATA_FIELDS]
    unavailable_parity = []
    available_hash_failures = 0
    control = by_arm["control"]
    for arm in ARMS[1:]:
        for task, row in by_arm[arm].items():
            if int(row["arm_available"]) == 0:
                for field in parity_fields:
                    if row[field] != control[task][field]:
                        unavailable_parity.append(
                            (arm, task, field, control[task][field], row[field])
                        )
            else:
                available_hash_failures += int(
                    row["action_hash"] == control[task]["action_hash"]
                )

    audit = {
        "rows": len(rows_a),
        "tasks": TASKS,
        "arms": len(ARMS),
        "complete_repeats": bool(repeats_equal),
        "mechanics_and_numeric_failures": mechanics_failures,
        "root_identity_failures": root_identity_failures,
        "arm_accounting_failures": accounting_failures,
        "unavailable_parity_failures": len(unavailable_parity),
        "unavailable_parity_failure_examples": unavailable_parity[:5],
        "available_hash_failures": available_hash_failures,
    }
    support = support_metrics(by_arm)
    support_checks = support_gates(audit, support)
    support_pass = all(support_checks.values())
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
        "support": support,
        "support_gates": support_checks,
        "support_pass": support_pass,
        "scope": "exact one-boundary rollout upper bound only; no arm or oracle policy is selectable",
    }
    if not support_pass:
        report.update(
            {
                "value_opened": False,
                "oracle_gates": None,
                "pass": False,
                "decision": "support_failure_close_contested_top_four_vocabulary",
            }
        )
    else:
        summaries = arm_summaries(by_arm)
        oracle = safe_oracle_metrics(by_arm)
        value_checks = oracle_gates(oracle)
        passed = all(value_checks.values())
        report.update(
            {
                "value_opened": True,
                "arm_summaries": summaries,
                "oracle": oracle,
                "oracle_gates": value_checks,
                "pass": passed,
                "decision": (
                    "pass_open_d82_bounded_monte_carlo_value_controller"
                    if passed
                    else "headroom_failure_close_contested_top_four_action_search"
                ),
            }
        )
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
