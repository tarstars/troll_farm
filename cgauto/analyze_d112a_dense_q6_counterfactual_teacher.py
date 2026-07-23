#!/usr/bin/env python3
"""Validate and analyze D112a's dense offline q6 counterfactual teacher."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import statistics


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d112a-dense-q6-counterfactual-teacher-protocol-2026-07-22.md"
FROZEN_INPUTS = BASE / "d112a-dense-q6-counterfactual-teacher-repair1-frozen-inputs.json"
PRE_REPAIR_ARMS_A = BASE / "d112a-q6-dense-counterfactual-arms-a-9843100-9843107.tsv"
PRE_REPAIR_BASELINES_A = BASE / "d112a-q6-dense-counterfactual-baselines-a-9843100-9843107.tsv"
ARMS_A = BASE / "d112a-q6-dense-counterfactual-arms-r1-a-9843100-9843107.tsv"
ARMS_B = BASE / "d112a-q6-dense-counterfactual-arms-r1-b-9843100-9843107.tsv"
BASELINES_A = BASE / "d112a-q6-dense-counterfactual-baselines-r1-a-9843100-9843107.tsv"
BASELINES_B = BASE / "d112a-q6-dense-counterfactual-baselines-r1-b-9843100-9843107.tsv"
LABELS = BASE / "d112a-q6-dense-act-wait-labels-9843100-9843107.tsv"
OUTPUT = BASE / "d112a-dense-q6-counterfactual-teacher-result.json"

START_SEED = 9_843_100
MAPS = 8
OPPONENTS = (
    "resident",
    "compact_gold",
    "gold_adaptive",
    "silver_boss",
    "legend_balanced",
    "norx_native_three",
    "script_boss",
    "mybot",
)
TASK_FIELDS = ("map_seed", "seat", "opponent")
STATE_FIELDS = tuple(f"state_{index:03}" for index in range(64))
ACTION_FIELDS = tuple(f"action_{index:03}" for index in range(379))
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def root_key(row: dict[str, str]) -> tuple[tuple[int, int, str], int]:
    return task_key(row), int(row["boundary_index"])


def arm_key(row: dict[str, str]) -> tuple[tuple[int, int, str], int, int]:
    return task_key(row), int(row["boundary_index"]), int(row["slot"])


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(START_SEED, START_SEED + MAPS)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def margin(row: dict[str, str]) -> int:
    return int(row["own_score"]) - int(row["opponent_score"])


def reward_identity_error(row: dict[str, str]) -> float:
    return max(
        abs(float(row["own_return"]) - int(row["own_score"]) / 100.0),
        abs(float(row["opponent_return"]) - int(row["opponent_score"]) / 100.0),
        abs(float(row["margin_return"]) - margin(row) / 100.0),
    )


def verify_frozen_inputs() -> dict:
    payload = json.loads(FROZEN_INPUTS.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    return {
        "manifest_sha256": sha256(FROZEN_INPUTS),
        "declared": payload,
        "mismatches": mismatches,
        "pass": not mismatches,
    }


def mechanics(
    arms: list[dict[str, str]],
    baselines: list[dict[str, str]],
    fields: list[str],
    repeated_exact: bool,
    elapsed_a: float,
    elapsed_b: float,
    frozen: dict,
) -> tuple[dict, dict[tuple[int, int, str], dict[str, str]], dict]:
    tasks = expected_tasks()
    baseline_counts = Counter(task_key(row) for row in baselines)
    baseline_by_task = {task_key(row): row for row in baselines}
    arm_counts = Counter(arm_key(row) for row in arms)
    arms_by_root: dict[tuple[tuple[int, int, str], int], list[dict[str, str]]] = defaultdict(list)
    for row in arms:
        arms_by_root[root_key(row)].append(row)

    expected_roots = {
        (task, boundary)
        for task, row in baseline_by_task.items()
        for boundary in range(int(row["boundary_count"]))
    }
    root_errors = []
    feature_errors = []
    accounting_errors = []
    paired_errors = []
    maximum_paired_error = 0.0
    maximum_reward_error = max(
        [reward_identity_error(row) for row in baselines]
        + [reward_identity_error(row) for row in arms],
        default=math.inf,
    )
    finite_features = True
    nonzero_actions = True
    expert_hashes = {row["expert_bank_hash"] for row in baselines + arms}

    for key, rows in arms_by_root.items():
        task, boundary = key
        if task not in baseline_by_task:
            root_errors.append(f"unexpected-task:{task}:{boundary}")
            continue
        first = rows[0]
        proposal_count = int(first["proposal_count"])
        shared_fields = (
            "baseline_boundary_count",
            "decision_ordinal",
            "root_turn",
            "root_state_hash",
            "proposal_count",
        ) + STATE_FIELDS
        consistent = all(
            all(row[field] == first[field] for field in shared_fields) for row in rows
        )
        slots = [int(row["slot"]) for row in rows]
        action_pairs = {(int(row["first_action"]), int(row["second_action"])) for row in rows}
        valid = (
            consistent
            and int(first["baseline_boundary_count"])
            == int(baseline_by_task[task]["boundary_count"])
            and boundary < int(first["baseline_boundary_count"])
            and len(rows) == proposal_count - 1
            and len(set(slots)) == len(rows)
            and all(1 <= slot < 65 for slot in slots)
            and len(action_pairs) == len(rows)
        )
        if not valid:
            root_errors.append(f"{task}:{boundary}")

        for row in rows:
            try:
                state = [float(row[field]) for field in STATE_FIELDS]
                action = [float(row[field]) for field in ACTION_FIELDS]
            except (KeyError, ValueError):
                finite_features = False
                feature_errors.append(f"parse:{arm_key(row)}")
                continue
            if not all(math.isfinite(value) for value in state + action):
                finite_features = False
                feature_errors.append(f"finite:{arm_key(row)}")
            if not any(value != 0.0 for value in action):
                nonzero_actions = False
                feature_errors.append(f"zero:{arm_key(row)}")

            kind = int(row["kind"])
            nonteacher = int(row["nonteacher"])
            first_teacher = int(row["first_teacher"])
            second_teacher = int(row["second_teacher"])
            accounting_ok = (
                int(row["intervention_batches"]) == 1
                and kind in (1, 2, 3)
                and nonteacher == (2 if kind == 3 else 1)
                and nonteacher == 2 - first_teacher - second_teacher
                and int(row["noncontrol_assignments"]) == nonteacher
                and int(row["joint_batches"]) == int(kind == 3)
            )
            if not accounting_ok:
                accounting_errors.append(str(arm_key(row)))

            control = baseline_by_task[task]
            expected_gain = (margin(row) - margin(control)) / 100.0
            error = abs(float(row["paired_gain"]) - expected_gain)
            maximum_paired_error = max(maximum_paired_error, error)
            if error > 1e-6:
                paired_errors.append(str(arm_key(row)))

    mechanical_failures = {
        field: sum(int(row[field]) for row in arms) for field in FAILURE_FIELDS
    }
    throughput_a = len(arms) / elapsed_a if elapsed_a > 0 else 0.0
    throughput_b = len(arms) / elapsed_b if elapsed_b > 0 else 0.0
    expected_headers = set(TASK_FIELDS + STATE_FIELDS + ACTION_FIELDS)
    gates = {
        "frozen_inputs_exact": frozen["pass"],
        "prescribed_baseline_grid": (
            len(baselines) == len(tasks)
            and set(baseline_counts) == tasks
            and all(count == 1 for count in baseline_counts.values())
        ),
        "at_least_one_boundary_per_task": (
            set(baseline_by_task) == tasks
            and all(int(row["boundary_count"]) >= 1 for row in baselines)
        ),
        "at_least_6000_arms": len(arms) >= 6_000,
        "complete_unique_arm_grid": (
            set(arms_by_root) == expected_roots
            and not root_errors
            and len(arm_counts) == len(arms)
            and all(count == 1 for count in arm_counts.values())
        ),
        "feature_schema_and_finiteness": (
            expected_headers <= set(fields) and finite_features and not feature_errors
        ),
        "nonzero_control_relative_actions": nonzero_actions,
        "paired_gain_exact": maximum_paired_error <= 1e-6 and not paired_errors,
        "reward_identity_below_1e_4": maximum_reward_error < 1e-4,
        "single_intervention_accounting": not accounting_errors,
        "zero_mechanical_failures": all(value == 0 for value in mechanical_failures.values()),
        "repeated_outputs_byte_exact": repeated_exact,
        "both_runs_at_least_12_arms_per_second": min(throughput_a, throughput_b) >= 12.0,
        "single_expert_bank_hash": len(expert_hashes) == 1,
    }
    details = {
        "tasks": len(tasks),
        "baselines": len(baselines),
        "roots": len(arms_by_root),
        "arms": len(arms),
        "minimum_boundaries_per_task": min(
            (int(row["boundary_count"]) for row in baselines), default=0
        ),
        "maximum_boundaries_per_task": max(
            (int(row["boundary_count"]) for row in baselines), default=0
        ),
        "minimum_proposals_per_root": min(
            (int(rows[0]["proposal_count"]) for rows in arms_by_root.values()), default=0
        ),
        "maximum_proposals_per_root": max(
            (int(rows[0]["proposal_count"]) for rows in arms_by_root.values()), default=0
        ),
        "maximum_paired_gain_error": maximum_paired_error,
        "maximum_reward_identity_error": maximum_reward_error,
        "mechanical_failures": mechanical_failures,
        "throughput_arms_per_second": {"a": throughput_a, "b": throughput_b},
        "expert_bank_hashes": sorted(expert_hashes),
        "error_samples": {
            "root": root_errors[:10],
            "feature": feature_errors[:10],
            "accounting": accounting_errors[:10],
            "paired": paired_errors[:10],
        },
    }
    return {"gates": gates, "pass": all(gates.values()), "details": details}, baseline_by_task, arms_by_root


def tie_key(row: dict[str, str], control: dict[str, str]) -> tuple[int, int, int, int]:
    return (
        margin(row) - margin(control),
        int(row["own_score"]) - int(control["own_score"]),
        -(int(row["opponent_score"]) - int(control["opponent_score"])),
        -int(row["slot"]),
    )


def teacher_analysis(
    arms: list[dict[str, str]],
    baseline_by_task: dict[tuple[int, int, str], dict[str, str]],
    arms_by_root: dict[tuple[tuple[int, int, str], int], list[dict[str, str]]],
) -> tuple[dict, list[dict[str, object]]]:
    arms_by_task: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in arms:
        arms_by_task[task_key(row)].append(row)

    labels_by_key: dict[tuple[tuple[int, int, str], int, int], dict[str, object]] = {}
    act_roots = 0
    total_roots = 0
    advantages = []
    best_now_values = []
    for task in sorted(baseline_by_task):
        control = baseline_by_task[task]
        future = 0
        boundary_count = int(control["boundary_count"])
        for boundary in reversed(range(boundary_count)):
            rows = arms_by_root[(task, boundary)]
            best = max(rows, key=lambda row: tie_key(row, control))
            best_now = margin(best) - margin(control)
            act_now = best_now > future
            act_roots += int(act_now)
            total_roots += 1
            best_now_values.append(best_now)
            for row in rows:
                immediate = margin(row) - margin(control)
                advantage = immediate - future
                advantages.append(advantage)
                labels_by_key[arm_key(row)] = {
                    "immediate_margin_gain": immediate,
                    "wait_margin_value": future,
                    "act_advantage": advantage,
                    "best_now_gain": best_now,
                    "value_before": max(future, best_now),
                    "act_now_optimal": int(act_now),
                    "best_arm_at_boundary": int(row is best),
                    "teacher_take_arm": int(act_now and row is best),
                }
            future = max(future, best_now)

    enriched = []
    oracle_keys = set()
    first_boundary_values = []
    for task, control in baseline_by_task.items():
        rows = arms_by_task[task]
        best = max(rows, key=lambda row: tie_key(row, control))
        gain = margin(best) - margin(control)
        selected = best if gain > 0 else control
        if gain > 0:
            oracle_keys.add(arm_key(best))
        first_rows = arms_by_root[(task, 0)]
        first_gain = max(margin(row) - margin(control) for row in first_rows)
        first_boundary_values.append(max(0, first_gain))
        enriched.append(
            {
                "task": task,
                "opponent": task[2],
                "gain": max(0, gain),
                "strict": gain > 0,
                "own": int(selected["own_score"]) - int(control["own_score"]),
                "opponent_delta": int(selected["opponent_score"])
                - int(control["opponent_score"]),
                "crop": int(selected["own_created_crops"]) > 0,
                "worker_three": int(selected["own_workers"]) >= 3,
                "control_worker_three": int(control["own_workers"]) >= 3,
                "boundary": int(best["boundary_index"]) if gain > 0 else None,
                "kind": int(best["kind"]) if gain > 0 else 0,
            }
        )

    family_means = {
        opponent: mean(item["gain"] for item in enriched if item["opponent"] == opponent)
        for opponent in OPPONENTS
    }
    oracle = {
        "tasks": len(enriched),
        "mean_margin_gain": mean(item["gain"] for item in enriched),
        "strict_improvement_rate": mean(item["strict"] for item in enriched),
        "mean_own_score_gain": mean(item["own"] for item in enriched),
        "mean_opponent_score_delta": mean(item["opponent_delta"] for item in enriched),
        "family_mean_margin_gain": family_means,
        "positive_families": sum(value > 0 for value in family_means.values()),
        "worst_family": min(family_means.values()),
        "intervention_rate": mean(item["strict"] for item in enriched),
        "mean_selected_boundary": mean(
            item["boundary"] for item in enriched if item["boundary"] is not None
        ),
        "selected_kind_counts": dict(Counter(item["kind"] for item in enriched)),
        "first_boundary_oracle_mean_gain": mean(first_boundary_values),
        "later_boundary_increment": mean(item["gain"] for item in enriched)
        - mean(first_boundary_values),
        "crop_rate": mean(item["crop"] for item in enriched),
        "worker_three_rate": mean(item["worker_three"] for item in enriched),
        "control_worker_three_rate": mean(
            item["control_worker_three"] for item in enriched
        ),
    }
    positives = sum(value > 0 for value in advantages)
    negatives = sum(value < 0 for value in advantages)
    zeros = len(advantages) - positives - negatives
    dp = {
        "roots": total_roots,
        "arms": len(advantages),
        "act_now_roots": act_roots,
        "wait_roots": total_roots - act_roots,
        "act_now_root_rate": act_roots / total_roots,
        "positive_arm_advantages": positives,
        "negative_arm_advantages": negatives,
        "zero_arm_advantages": zeros,
        "positive_arm_advantage_rate": positives / len(advantages),
        "negative_arm_advantage_rate": negatives / len(advantages),
        "target_mean": mean(advantages),
        "target_standard_deviation": statistics.pstdev(advantages),
        "target_minimum": min(advantages),
        "target_maximum": max(advantages),
        "best_now_mean": mean(best_now_values),
    }
    signal_gates = {
        "oracle_mean_at_least_20": oracle["mean_margin_gain"] >= 20.0,
        "oracle_strict_at_least_75pct": oracle["strict_improvement_rate"] >= 0.75,
        "at_least_seven_positive_families": oracle["positive_families"] >= 7,
        "worst_family_at_least_8": oracle["worst_family"] >= 8.0,
        "own_nonnegative_or_opponent_nonpositive": (
            oracle["mean_own_score_gain"] >= 0.0
            or oracle["mean_opponent_score_delta"] <= 0.0
        ),
        "act_now_roots_5_to_90pct": 0.05 <= dp["act_now_root_rate"] <= 0.90,
        "positive_arm_targets_1_to_50pct": (
            0.01 <= dp["positive_arm_advantage_rate"] <= 0.50
        ),
        "negative_arm_targets_at_least_40pct": (
            dp["negative_arm_advantage_rate"] >= 0.40
        ),
        "target_stddev_at_least_5": dp["target_standard_deviation"] >= 5.0,
    }
    safety_gates = {
        "oracle_crop_100pct": oracle["crop_rate"] == 1.0,
        "oracle_worker_three_within_5pp": (
            oracle["worker_three_rate"] >= oracle["control_worker_three_rate"] - 0.05
        ),
    }

    label_rows = []
    for row in arms:
        values = labels_by_key[arm_key(row)]
        label_rows.append(
            {
                "map_seed": int(row["map_seed"]),
                "seat": int(row["seat"]),
                "opponent": row["opponent"],
                "boundary_index": int(row["boundary_index"]),
                "slot": int(row["slot"]),
                **values,
                "task_oracle_arm": int(arm_key(row) in oracle_keys),
            }
        )
    return {
        "oracle": oracle,
        "backward_dp": dp,
        "signal_gates": signal_gates,
        "signal_pass": all(signal_gates.values()),
        "safety_gates": safety_gates,
        "safety_pass": all(safety_gates.values()),
    }, label_rows


def write_labels(path: Path, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0])
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, delimiter="\t", fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    payload = target.getvalue()
    if path.exists():
        assert path.read_text() == payload, "D112 labels changed on repeated analysis"
    else:
        path.write_text(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elapsed-a", type=float, required=True)
    parser.add_argument("--elapsed-b", type=float, required=True)
    args = parser.parse_args()

    repeated = {
        "arms": ARMS_A.read_bytes() == ARMS_B.read_bytes(),
        "baselines": BASELINES_A.read_bytes() == BASELINES_B.read_bytes(),
        "pre_repair_arms_semantic": PRE_REPAIR_ARMS_A.read_bytes() == ARMS_A.read_bytes(),
        "pre_repair_baselines_semantic": (
            PRE_REPAIR_BASELINES_A.read_bytes() == BASELINES_A.read_bytes()
        ),
    }
    arms, fields = read_table(ARMS_A)
    baselines, _ = read_table(BASELINES_A)
    frozen = verify_frozen_inputs()
    mechanical, baseline_by_task, arms_by_root = mechanics(
        arms,
        baselines,
        fields,
        all(repeated.values()),
        args.elapsed_a,
        args.elapsed_b,
        frozen,
    )
    if mechanical["pass"]:
        teacher, label_rows = teacher_analysis(arms, baseline_by_task, arms_by_root)
        write_labels(LABELS, label_rows)
    else:
        teacher = {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "mechanics failure",
        }
        label_rows = []

    full_pass = mechanical["pass"] and teacher["signal_pass"] and teacher["safety_pass"]
    result = {
        "schema": "troll-farm-d112a-dense-q6-counterfactual-teacher-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "panel": {
            "start_seed": START_SEED,
            "maps": MAPS,
            "tasks": len(expected_tasks()),
            "smoke_seed_excluded": 9_843_000,
        },
        "timing_seconds": {"a": args.elapsed_a, "b": args.elapsed_b},
        "repeated_byte_exact": repeated,
        "frozen_inputs": frozen,
        "mechanics": mechanical,
        "teacher": teacher,
        "labels": {
            "path": str(LABELS.relative_to(ROOT)) if label_rows else None,
            "rows": len(label_rows),
            "sha256": sha256(LABELS) if label_rows else None,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (
                PRE_REPAIR_ARMS_A,
                PRE_REPAIR_BASELINES_A,
                ARMS_A,
                ARMS_B,
                BASELINES_A,
                BASELINES_B,
            )
        },
        "full_pass": full_pass,
        "decision": (
            "open_d112b_new_map_scorer_fit"
            if full_pass
            else "repair_only"
            if not mechanical["pass"]
            else "close_dense_one_use_teacher"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
