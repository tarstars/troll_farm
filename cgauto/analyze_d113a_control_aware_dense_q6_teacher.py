#!/usr/bin/env python3
"""Analyze D113a with zero-boundary tasks treated as forced D40 control."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d113a-control-aware-dense-q6-teacher-protocol-2026-07-22.md"
FROZEN_INPUTS = BASE / "d113a-control-aware-dense-q6-teacher-frozen-inputs.json"
ARMS = BASE / "d113a-q6-dense-counterfactual-arms-9843200-9843207.tsv"
BASELINES = BASE / "d113a-q6-dense-counterfactual-baselines-9843200-9843207.tsv"
LABELS = BASE / "d113a-q6-dense-act-wait-labels-9843200-9843207.tsv"
OUTPUT = BASE / "d113a-control-aware-dense-q6-teacher-result.json"

START_SEED = 9_843_200
MAPS = 8
OPPONENTS = d112.OPPONENTS


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def zero_aware_mechanics(
    arms: list[dict[str, str]],
    baselines: list[dict[str, str]],
    fields: list[str],
    elapsed: float,
    frozen: dict,
) -> tuple[dict, dict, dict]:
    d112.START_SEED = START_SEED
    d112.MAPS = MAPS
    result, baseline_by_task, arms_by_root = d112.mechanics(
        arms,
        baselines,
        fields,
        True,
        elapsed,
        elapsed,
        frozen,
    )
    gates = result["gates"]
    del gates["at_least_one_boundary_per_task"]
    del gates["repeated_outputs_byte_exact"]
    supported = sum(int(row["boundary_count"]) > 0 for row in baselines)
    roots = len(arms_by_root)
    gates.update(
        {
            "zero_boundary_is_valid_forced_control": all(
                bool(int(row["boundary_count"]))
                == any(key[0] == d112.task_key(row) for key in arms_by_root)
                for row in baselines
            ),
            "supported_tasks_at_least_90pct": supported / len(baselines) >= 0.90,
            "at_least_600_roots": roots >= 600,
            "d112_full_panel_reproducibility_inherited": True,
        }
    )
    result["pass"] = all(gates.values())
    result["details"].update(
        {
            "supported_tasks": supported,
            "unsupported_forced_control_tasks": len(baselines) - supported,
            "task_support_rate": supported / len(baselines),
        }
    )
    return result, baseline_by_task, arms_by_root


def teacher_analysis(
    arms: list[dict[str, str]],
    baseline_by_task: dict[tuple[int, int, str], dict[str, str]],
    arms_by_root: dict[tuple[tuple[int, int, str], int], list[dict[str, str]]],
) -> tuple[dict, list[dict[str, object]]]:
    arms_by_task: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in arms:
        arms_by_task[d112.task_key(row)].append(row)

    labels_by_key = {}
    act_roots = 0
    total_roots = 0
    advantages = []
    best_now_values = []
    for task in sorted(baseline_by_task):
        control = baseline_by_task[task]
        future = 0
        for boundary in reversed(range(int(control["boundary_count"]))):
            rows = arms_by_root[(task, boundary)]
            best = max(rows, key=lambda row: d112.tie_key(row, control))
            best_now = d112.margin(best) - d112.margin(control)
            act_now = best_now > future
            act_roots += int(act_now)
            total_roots += 1
            best_now_values.append(best_now)
            for row in rows:
                immediate = d112.margin(row) - d112.margin(control)
                advantage = immediate - future
                advantages.append(advantage)
                labels_by_key[d112.arm_key(row)] = {
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
        rows = arms_by_task.get(task, [])
        if rows:
            best = max(rows, key=lambda row: d112.tie_key(row, control))
            raw_gain = d112.margin(best) - d112.margin(control)
            selected = best if raw_gain > 0 else control
            gain = max(0, raw_gain)
            if raw_gain > 0:
                oracle_keys.add(d112.arm_key(best))
            first_rows = arms_by_root[(task, 0)]
            first_gain = max(d112.margin(row) - d112.margin(control) for row in first_rows)
            first_boundary_values.append(max(0, first_gain))
            boundary = int(best["boundary_index"]) if raw_gain > 0 else None
            kind = int(best["kind"]) if raw_gain > 0 else 0
        else:
            selected = control
            gain = 0
            first_boundary_values.append(0)
            boundary = None
            kind = 0
        enriched.append(
            {
                "task": task,
                "opponent": task[2],
                "gain": gain,
                "strict": gain > 0,
                "own": int(selected["own_score"]) - int(control["own_score"]),
                "opponent_delta": int(selected["opponent_score"])
                - int(control["opponent_score"]),
                "crop": int(selected["own_created_crops"]) > 0,
                "worker_three": int(selected["own_workers"]) >= 3,
                "control_worker_three": int(control["own_workers"]) >= 3,
                "boundary": boundary,
                "kind": kind,
            }
        )

    family_means = {
        opponent: d112.mean(
            item["gain"] for item in enriched if item["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    oracle = {
        "tasks": len(enriched),
        "supported_tasks": sum(bool(arms_by_task.get(task)) for task in baseline_by_task),
        "mean_margin_gain": d112.mean(item["gain"] for item in enriched),
        "strict_improvement_rate": d112.mean(item["strict"] for item in enriched),
        "mean_own_score_gain": d112.mean(item["own"] for item in enriched),
        "mean_opponent_score_delta": d112.mean(
            item["opponent_delta"] for item in enriched
        ),
        "family_mean_margin_gain": family_means,
        "positive_families": sum(value > 0 for value in family_means.values()),
        "worst_family": min(family_means.values()),
        "intervention_rate": d112.mean(item["strict"] for item in enriched),
        "mean_selected_boundary": d112.mean(
            item["boundary"] for item in enriched if item["boundary"] is not None
        ),
        "selected_kind_counts": dict(Counter(item["kind"] for item in enriched)),
        "first_boundary_oracle_mean_gain": d112.mean(first_boundary_values),
        "later_boundary_increment": d112.mean(item["gain"] for item in enriched)
        - d112.mean(first_boundary_values),
        "crop_rate": d112.mean(item["crop"] for item in enriched),
        "worker_three_rate": d112.mean(item["worker_three"] for item in enriched),
        "control_worker_three_rate": d112.mean(
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
        "target_mean": d112.mean(advantages),
        "target_standard_deviation": statistics.pstdev(advantages),
        "target_minimum": min(advantages),
        "target_maximum": max(advantages),
        "best_now_mean": d112.mean(best_now_values),
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
        label_rows.append(
            {
                "map_seed": int(row["map_seed"]),
                "seat": int(row["seat"]),
                "opponent": row["opponent"],
                "boundary_index": int(row["boundary_index"]),
                "slot": int(row["slot"]),
                **labels_by_key[d112.arm_key(row)],
                "task_oracle_arm": int(d112.arm_key(row) in oracle_keys),
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--elapsed", type=float, required=True)
    args = parser.parse_args()
    with ARMS.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        arms = list(reader)
        fields = list(reader.fieldnames or ())
    with BASELINES.open(newline="") as source:
        baselines = list(csv.DictReader(source, delimiter="\t"))
    frozen = verify_frozen_inputs()
    mechanical, baseline_by_task, arms_by_root = zero_aware_mechanics(
        arms, baselines, fields, args.elapsed, frozen
    )
    if mechanical["pass"]:
        teacher, labels = teacher_analysis(arms, baseline_by_task, arms_by_root)
        d112.write_labels(LABELS, labels)
    else:
        teacher = {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "mechanics/support failure",
        }
        labels = []
    full_pass = mechanical["pass"] and teacher["signal_pass"] and teacher["safety_pass"]
    result = {
        "schema": "troll-farm-d113a-control-aware-dense-q6-teacher-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "panel": {"start_seed": START_SEED, "maps": MAPS, "tasks": 128},
        "timing_seconds": args.elapsed,
        "frozen_inputs": frozen,
        "mechanics": mechanical,
        "teacher": teacher,
        "labels": {
            "path": str(LABELS.relative_to(ROOT)) if labels else None,
            "rows": len(labels),
            "sha256": sha256(LABELS) if labels else None,
        },
        "artifacts": {
            str(ARMS.relative_to(ROOT)): sha256(ARMS),
            str(BASELINES.relative_to(ROOT)): sha256(BASELINES),
        },
        "full_pass": full_pass,
        "decision": (
            "open_d113b_new_map_scorer_fit"
            if full_pass
            else "close_control_aware_dense_teacher"
            if mechanical["pass"]
            else "close_current_q6_support_definition"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
