#!/usr/bin/env python3
"""Select and freshly validate D119 with a training-only activity quantile."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d125a-fit-activity-calibrated-q6-protocol-2026-07-22.md"
FIT_LOCK = BASE / "d125a-fit-activity-calibrated-q6-fit-lock.json"
FIT_OUTPUT = BASE / "d125a-fit-activity-calibrated-q6-fit-result.json"
SELECTION_LOCK = BASE / "d125a-fit-activity-calibrated-q6-selection-lock.json"
VALIDATION_ARMS = BASE / "d125a-q6-validation-arms-9843780-9843795.tsv"
VALIDATION_BASELINES = BASE / "d125a-q6-validation-baselines-9843780-9843795.tsv"
CHECKPOINT = BASE / "d125a-fit-activity-calibrated-q6.pt"
OUTPUT = BASE / "d125a-fit-activity-calibrated-q6-result.json"

TARGET_ACTIVITY = 0.84
VALIDATION_START = 9_843_780
VALIDATION_MAPS = 16
VALIDATION_TASKS = 256


def activity_calibrated_offset(
    tasks: list,
    root_order: list,
    gate_values: np.ndarray,
    target_activity: float = TARGET_ACTIVITY,
) -> tuple[float, dict]:
    if len(root_order) != len(gate_values):
        raise ValueError("root order and gate values differ")
    maximum_by_task = {task: float("-inf") for task in tasks}
    for root, value in zip(root_order, gate_values, strict=True):
        task = root[0]
        if task not in maximum_by_task:
            raise ValueError(f"unknown root task: {task!r}")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("nonfinite gate logit")
        maximum_by_task[task] = max(maximum_by_task[task], value)

    target_active = round(target_activity * len(tasks))
    ordered = sorted(maximum_by_task.values(), reverse=True)
    if not 0 < target_active < len(ordered):
        raise ValueError("target activity does not define an interior quantile")
    active_floor = ordered[target_active - 1]
    inactive_ceiling = ordered[target_active]
    if not math.isfinite(active_floor) or not math.isfinite(inactive_ceiling):
        raise ValueError("insufficient supported tasks for activity calibration")
    if not active_floor > inactive_ceiling:
        raise ValueError("gate quantile boundary is tied")
    offset = (active_floor + inactive_ceiling) / 2.0
    achieved = sum(value > offset for value in maximum_by_task.values())
    if achieved != target_active:
        raise RuntimeError("activity calibration did not hit the target count")
    return offset, {
        "target_activity": target_activity,
        "tasks": len(tasks),
        "target_active_tasks": target_active,
        "achieved_active_tasks": achieved,
        "achieved_activity": achieved / len(tasks),
        "active_floor_logit": active_floor,
        "inactive_ceiling_logit": inactive_ceiling,
        "offset": offset,
    }


def calibrated_candidate(
    train: dict,
    dataset: dict,
    model: d117.FactorizedController,
    summary: dict,
    grid_index: int,
) -> dict:
    ranks = d115.model_logits(model.ranker, train["x"])
    gate_values = d117.state_gate_logits(model, dataset)
    gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
    offset, calibration = activity_calibrated_offset(
        list(train["baseline_by_task"]), dataset["root_order"], gate_values
    )
    metrics = d117.factorized_policy_metrics(train, ranks, gate_by_root, offset)
    if metrics["intervention_rate"] != calibration["achieved_activity"]:
        raise RuntimeError("closed-loop fit activity differs from calibration")
    structural = d118.model_fit_gates(summary)
    policy = d118.fit_policy_gates(metrics)
    return {
        "grid_index": grid_index,
        "seed": summary["seed"],
        "model_hash": summary["model_hash"],
        "gate_offset": offset,
        "calibration": calibration,
        "model_fit_gates": structural,
        "fit_policy_metrics": metrics,
        "fit_policy_gates": policy,
        "fit_eligible": all(structural.values()) and all(policy.values()),
    }


def fit_only() -> dict:
    lock = d117.verify_manifest(FIT_LOCK)
    frozen_fit = json.loads(d119.FIT_OUTPUT.read_text())
    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    dataset, training, _, models = d119.train_models_and_grid(train)
    expected_hashes = {
        item["seed"]: item["model_hash"] for item in frozen_fit["training"]
    }
    actual_hashes = {item["seed"]: item["model_hash"] for item in training}
    if expected_hashes != actual_hashes:
        raise RuntimeError("D125 did not reproduce the frozen D119 models")

    candidates = [
        calibrated_candidate(train, dataset, models[item["seed"]], item, index)
        for index, item in enumerate(training)
    ]
    eligible = [item for item in candidates if item["fit_eligible"]]
    selected = (
        max(
            eligible,
            key=lambda item: d115.selection_key(
                {
                    "metrics": item["fit_policy_metrics"],
                    "grid_index": item["grid_index"],
                }
            ),
        )
        if eligible
        else None
    )
    result = {
        "schema": "troll-farm-d125a-fit-activity-calibrated-q6-fit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "fit_lock": lock,
        "calibration_rule": {
            "target_activity": TARGET_ACTIVITY,
            "target_active_tasks": round(TARGET_ACTIVITY * VALIDATION_TASKS),
            "threshold": "midpoint between descending per-task maximum logits 215 and 216",
        },
        "models_reproduced": expected_hashes == actual_hashes,
        "training": training,
        "candidates": candidates,
        "eligible": len(eligible),
        "selected": selected,
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (d119.FIT_OUTPUT, d119.TRAIN_ARMS, d119.TRAIN_BASELINES)
        },
        "decision": (
            "freeze_selected_calibrated_controller_before_fresh_validation"
            if selected is not None
            else "close_training_only_calibration_at_fit_gate"
        ),
    }
    FIT_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def policy_evaluation_mechanics(mechanics: dict) -> dict:
    informational = {
        "supported_tasks_at_least_90pct",
        "at_least_600_roots",
        "at_least_6000_arms",
    }
    gates = {
        name: passed
        for name, passed in mechanics["gates"].items()
        if name not in informational
    }
    gates["exactly_256_policy_tasks"] = (
        mechanics["details"]["tasks"] == VALIDATION_TASKS
    )
    return {
        "gates": gates,
        "informational": {
            name: mechanics["gates"][name]
            for name in informational
        },
        "details": mechanics["details"],
        "pass": all(gates.values()),
    }


def validation_gates(metrics: dict, control_crop: float) -> dict[str, bool]:
    gates = d123.relative_held_gates(metrics, control_crop)
    gates["both_folds_nonnegative"] = (
        min(metrics["fold_mean_margin_delta"].values()) >= 0.0
    )
    return gates


def checkpoint_payload(
    model: d117.FactorizedController, selected: dict
) -> dict:
    return {
        "schema": "troll-farm-d125a-fit-activity-calibrated-q6-checkpoint-v1",
        "parameters": 6_626,
        "epochs": d119.EPOCHS,
        "soft_value_temperature": d118.TEMPERATURE,
        "target_fit_activity": TARGET_ACTIVITY,
        "seed": selected["seed"],
        "gate_offset": selected["gate_offset"],
        "model_hash": selected["model_hash"],
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def validate(validation_elapsed: float) -> dict:
    selection_lock = d117.verify_manifest(SELECTION_LOCK)
    fit = json.loads(FIT_OUTPUT.read_text())
    selected = fit.get("selected")
    if fit.get("decision") != "freeze_selected_calibrated_controller_before_fresh_validation":
        raise RuntimeError("D125 fit did not authorize fresh validation")
    if not selected or not selected["fit_eligible"]:
        raise RuntimeError("D125 has no eligible calibrated controller")

    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    dataset, training, _, models = d119.train_models_and_grid(train)
    reproduced = calibrated_candidate(
        train,
        dataset,
        models[selected["seed"]],
        next(item for item in training if item["seed"] == selected["seed"]),
        selected["grid_index"],
    )
    if reproduced != selected:
        raise RuntimeError("D125 selected calibrated controller did not reproduce")

    validation = d114.panel(
        VALIDATION_ARMS,
        VALIDATION_BASELINES,
        VALIDATION_START,
        VALIDATION_MAPS,
        validation_elapsed,
    )
    mechanics = policy_evaluation_mechanics(validation["mechanics"])
    metrics = None
    gates = None
    passed = False
    if mechanics["pass"]:
        model = models[selected["seed"]]
        validation_dataset = d118.soft_value_dataset(validation)
        ranks = d115.model_logits(model.ranker, validation["x"])
        gate_values = d117.state_gate_logits(model, validation_dataset)
        gate_by_root = dict(
            zip(validation_dataset["root_order"], gate_values, strict=True)
        )
        metrics = d117.factorized_policy_metrics(
            validation, ranks, gate_by_root, selected["gate_offset"]
        )
        control_crop = d123.control_crop_rate(validation)
        gates = validation_gates(metrics, control_crop)
        passed = all(gates.values())

    checkpoint = None
    if passed:
        model = models[selected["seed"]]
        torch.save(checkpoint_payload(model, selected), CHECKPOINT)
        checkpoint = {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "sha256": d119.sha256(CHECKPOINT),
            "bytes": CHECKPOINT.stat().st_size,
            "model_hash": selected["model_hash"],
        }
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D125 checkpoint exists without validation pass")

    result = {
        "schema": "troll-farm-d125a-fit-activity-calibrated-q6-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "selection_lock": selection_lock,
        "fit_result": {
            "path": str(FIT_OUTPUT.relative_to(ROOT)),
            "sha256": d119.sha256(FIT_OUTPUT),
            "selected": selected,
        },
        "fresh_validation": {
            "seeds": f"{VALIDATION_START}--{VALIDATION_START + VALIDATION_MAPS - 1}",
            "maps": VALIDATION_MAPS,
            "tasks": VALIDATION_TASKS,
            "elapsed_seconds": validation_elapsed,
            "mechanics": mechanics,
            "teacher_signal_descriptive_only": validation["teacher"],
            "metrics": metrics,
            "gates": gates,
            "pass": passed,
        },
        "checkpoint": checkpoint,
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (VALIDATION_ARMS, VALIDATION_BASELINES)
        },
        "decision": (
            "open_quantized_rust_parity_and_separate_untouched_confirmation"
            if passed
            else "repair_collector_mechanics_only"
            if not mechanics["pass"]
            else "close_calibrated_controller_without_validation_tuning"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("fit")
    validation = subparsers.add_parser("validate")
    validation.add_argument("--validation-elapsed", type=float, required=True)
    args = parser.parse_args()
    result = fit_only() if args.command == "fit" else validate(args.validation_elapsed)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
