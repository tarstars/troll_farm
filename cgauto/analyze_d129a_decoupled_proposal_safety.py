#!/usr/bin/env python3
"""Retrospectively compare decoupled proposal-safety compositions."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d129a-decoupled-proposal-safety-composition-protocol-2026-07-22.md"
LOCK = BASE / "d129a-decoupled-proposal-safety-composition-lock.json"
OUTPUT = BASE / "d129a-decoupled-proposal-safety-composition-result.json"

RANK_SEED = 11903
RANK_MODEL_HASH = "476669bc4624a85b870cb31baba450dfcf7d98699365369edf4f8ebacd31ef43"
SAFETY_SEEDS = (12901, 12902, 12903, 12904)
SPECIFICITY_TARGETS = (0.70, 0.80, 0.90, 0.95, 0.98)
COMPOSITIONS = ("winner_veto", "filter_rank", "safety_rerank")


def safety_threshold(
    logits: np.ndarray,
    values: np.ndarray,
    target_nonpositive_recall: float,
) -> tuple[float, dict]:
    """Calibrate strict approval to reject a target share of nonpositive arms."""
    scores = np.asarray(logits, dtype=np.float32)
    advantages = np.asarray(values, dtype=np.float32)
    if scores.shape != advantages.shape or scores.ndim != 1:
        raise ValueError("safety logits and values must be equal one-dimensional arrays")
    positive = advantages > 0.0
    nonpositive = ~positive
    if not positive.any() or not nonpositive.any():
        raise ValueError("safety calibration requires both classes")
    count = int(nonpositive.sum())
    reject = math.ceil(target_nonpositive_recall * count)
    if not 0 < reject <= count:
        raise ValueError("specificity target does not define a threshold")
    negative_scores = scores[nonpositive]
    threshold = float(np.partition(negative_scores, reject - 1)[reject - 1])
    approved = scores > threshold
    approved_count = int(approved.sum())
    true_positive = int((approved & positive).sum())
    return threshold, {
        "target_nonpositive_recall": target_nonpositive_recall,
        "threshold": threshold,
        "positive_arms": int(positive.sum()),
        "nonpositive_arms": count,
        "approved_arms": approved_count,
        "approval_rate": approved_count / len(scores),
        "positive_recall": true_positive / int(positive.sum()),
        "nonpositive_recall": float((~approved[nonpositive]).mean()),
        "approved_precision": true_positive / approved_count if approved_count else 0.0,
    }


def select_root_row(
    rows: list[dict],
    rank_by_arm: dict,
    safety_by_arm: dict,
    safety_offset: float,
    composition: str,
) -> dict | None:
    if composition not in COMPOSITIONS:
        raise ValueError(f"unknown composition: {composition}")
    if composition == "winner_veto":
        winner = max(rows, key=lambda row: rank_by_arm[d112.arm_key(row)])
        return (
            winner
            if safety_by_arm[d112.arm_key(winner)] > safety_offset
            else None
        )
    approved = [
        row
        for row in rows
        if safety_by_arm[d112.arm_key(row)] > safety_offset
    ]
    if not approved:
        return None
    scorer = rank_by_arm if composition == "filter_rank" else safety_by_arm
    return max(approved, key=lambda row: scorer[d112.arm_key(row)])


def composed_policy_metrics(
    data: dict,
    rank_logits: np.ndarray,
    gate_by_root: dict,
    gate_offset: float,
    safety_logits: np.ndarray,
    safety_offset: float,
    composition: str,
) -> dict:
    rank_by_arm = {
        d112.arm_key(row): float(score)
        for row, score in zip(data["arms"], rank_logits, strict=True)
    }
    safety_by_arm = {
        d112.arm_key(row): float(score)
        for row, score in zip(data["arms"], safety_logits, strict=True)
    }
    selected = []
    for task, control in data["baseline_by_task"].items():
        choice = None
        for boundary in range(int(control["boundary_count"])):
            root = (task, boundary)
            if gate_by_root[root] - gate_offset <= 0.0:
                continue
            choice = select_root_row(
                data["arms_by_root"][root],
                rank_by_arm,
                safety_by_arm,
                safety_offset,
                composition,
            )
            if choice is not None:
                break
        outcome = choice or control
        margin = d112.margin(outcome) - d112.margin(control)
        selected.append(
            {
                "opponent": task[2],
                "map_seed": task[0],
                "margin": margin,
                "own": int(outcome["own_score"]) - int(control["own_score"]),
                "rival": int(outcome["opponent_score"])
                - int(control["opponent_score"]),
                "intervened": choice is not None,
                "crop": int(outcome["own_created_crops"]) > 0,
                "worker_three": int(outcome["own_workers"]) >= 3,
                "control_worker_three": int(control["own_workers"]) >= 3,
            }
        )
    family = {
        opponent: d112.mean(
            row["margin"] for row in selected if row["opponent"] == opponent
        )
        for opponent in d112.OPPONENTS
    }
    folds = {
        str(fold): d112.mean(
            row["margin"]
            for row in selected
            if (row["map_seed"] - data["start"]) % 2 == fold
        )
        for fold in range(2)
    }
    interventions = [row for row in selected if row["intervened"]]
    negative = [row for row in interventions if row["margin"] < 0]
    positive = [row for row in interventions if row["margin"] > 0]
    return {
        "tasks": len(selected),
        "mean_margin_delta": d112.mean(row["margin"] for row in selected),
        "strict_improvement_rate": d112.mean(row["margin"] > 0 for row in selected),
        "mean_own_score_delta": d112.mean(row["own"] for row in selected),
        "mean_opponent_score_delta": d112.mean(row["rival"] for row in selected),
        "family_mean_margin_delta": family,
        "positive_families": sum(value > 0 for value in family.values()),
        "worst_family": min(family.values()),
        "fold_mean_margin_delta": folds,
        "intervention_rate": d112.mean(row["intervened"] for row in selected),
        "crop_rate": d112.mean(row["crop"] for row in selected),
        "worker_three_rate": d112.mean(row["worker_three"] for row in selected),
        "control_worker_three_rate": d112.mean(
            row["control_worker_three"] for row in selected
        ),
        "positive_score_ties": 0,
        "interventions": len(interventions),
        "positive_interventions": len(positive),
        "negative_interventions": len(negative),
        "negative_margin_sum": sum(row["margin"] for row in negative),
        "positive_margin_sum": sum(row["margin"] for row in positive),
    }


def aggregate_cells(cells: list[dict]) -> list[dict]:
    aggregates = []
    for composition in COMPOSITIONS:
        for target in SPECIFICITY_TARGETS:
            group = [
                cell
                for cell in cells
                if cell["composition"] == composition
                and cell["target_nonpositive_recall"] == target
            ]
            assert len(group) == len(SAFETY_SEEDS)
            development = [cell["development_metrics"] for cell in group]
            fit = [cell["fit_metrics"] for cell in group]
            aggregates.append(
                {
                    "composition": composition,
                    "target_nonpositive_recall": target,
                    "fit_passes": sum(cell["fit_pass"] for cell in group),
                    "development_passes": sum(
                        cell["development_descriptive_pass"] for cell in group
                    ),
                    "fit_mean_minimum": min(
                        metrics["mean_margin_delta"] for metrics in fit
                    ),
                    "fit_mean_average": d112.mean(
                        metrics["mean_margin_delta"] for metrics in fit
                    ),
                    "development_mean_minimum": min(
                        metrics["mean_margin_delta"] for metrics in development
                    ),
                    "development_mean_average": d112.mean(
                        metrics["mean_margin_delta"] for metrics in development
                    ),
                    "development_strict_average": d112.mean(
                        metrics["strict_improvement_rate"] for metrics in development
                    ),
                    "development_activity_average": d112.mean(
                        metrics["intervention_rate"] for metrics in development
                    ),
                    "development_family_floor_minimum": min(
                        metrics["worst_family"] for metrics in development
                    ),
                    "development_family_floor_average": d112.mean(
                        metrics["worst_family"] for metrics in development
                    ),
                    "development_negative_interventions_average": d112.mean(
                        metrics["negative_interventions"] for metrics in development
                    ),
                }
            )
    return aggregates


def aggregate_key(item: dict) -> tuple:
    return (
        item["development_passes"],
        item["fit_passes"],
        item["development_family_floor_minimum"],
        item["development_mean_minimum"],
        item["development_mean_average"],
        -SPECIFICITY_TARGETS.index(item["target_nonpositive_recall"]),
        -COMPOSITIONS.index(item["composition"]),
    )


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    d126_result = json.loads(d126.OUTPUT.read_text())
    selected = d126_result["fit_result"]["selected"]
    if selected["seed"] != RANK_SEED or selected["model_hash"] != RANK_MODEL_HASH:
        raise RuntimeError("D129 expected the fixed D126 seed11903 controller")

    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    train_dataset = d118.soft_value_dataset(train)
    rank_model, rank_summary = d119.train_long_model(train_dataset, RANK_SEED)
    if rank_summary["model_hash"] != RANK_MODEL_HASH:
        raise RuntimeError("D129 did not reproduce the fixed D126 rank model")

    development = d114.panel(
        d126.VALIDATION_ARMS,
        d126.VALIDATION_BASELINES,
        d126.VALIDATION_START,
        d126.VALIDATION_MAPS,
        d126_result["fresh_validation"]["elapsed_seconds"],
    )
    development_dataset = d118.soft_value_dataset(development)
    train_ranks = d115.model_logits(rank_model.ranker, train["x"])
    development_ranks = d115.model_logits(rank_model.ranker, development["x"])
    train_gates = dict(
        zip(
            train_dataset["root_order"],
            d117.state_gate_logits(rank_model, train_dataset),
            strict=True,
        )
    )
    development_gates = dict(
        zip(
            development_dataset["root_order"],
            d117.state_gate_logits(rank_model, development_dataset),
            strict=True,
        )
    )
    gate_offset = float(selected["gate_offset"])
    original_train = d117.factorized_policy_metrics(
        train, train_ranks, train_gates, gate_offset
    )
    original_development = d117.factorized_policy_metrics(
        development, development_ranks, development_gates, gate_offset
    )

    safety_training = []
    cells = []
    for seed in SAFETY_SEEDS:
        safety_model, summary = d115.train_model(
            train["x"],
            train["y"],
            train["root_keys"],
            seed,
            epochs=d115.EPOCHS,
            batch_size=d115.BATCH_SIZE,
            threads=1,
        )
        train_safety = d115.model_logits(safety_model, train["x"])
        development_safety = d115.model_logits(safety_model, development["x"])
        calibrations = []
        for target in SPECIFICITY_TARGETS:
            threshold, calibration = safety_threshold(
                train_safety, train["y"], target
            )
            calibrations.append(calibration)
            for composition in COMPOSITIONS:
                fit_metrics = composed_policy_metrics(
                    train,
                    train_ranks,
                    train_gates,
                    gate_offset,
                    train_safety,
                    threshold,
                    composition,
                )
                development_metrics = composed_policy_metrics(
                    development,
                    development_ranks,
                    development_gates,
                    gate_offset,
                    development_safety,
                    threshold,
                    composition,
                )
                fit_gates = d118.fit_policy_gates(fit_metrics)
                validation_gates = d125.validation_gates(
                    development_metrics,
                    d123.control_crop_rate(development),
                )
                cells.append(
                    {
                        "safety_seed": seed,
                        "safety_model_hash": summary["model_hash"],
                        "target_nonpositive_recall": target,
                        "safety_offset": threshold,
                        "composition": composition,
                        "fit_metrics": fit_metrics,
                        "fit_gates": fit_gates,
                        "fit_pass": all(fit_gates.values()),
                        "development_metrics": development_metrics,
                        "development_gates": validation_gates,
                        "development_descriptive_pass": all(
                            validation_gates.values()
                        ),
                    }
                )
        safety_training.append(
            {
                **summary,
                "threshold_calibrations": calibrations,
            }
        )

    aggregates = aggregate_cells(cells)
    best = max(aggregates, key=aggregate_key)
    result = {
        "schema": "troll-farm-d129a-decoupled-proposal-safety-composition-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "qualification_authority": False,
        "fixed_rank_controller": {
            "seed": RANK_SEED,
            "model_hash": rank_summary["model_hash"],
            "gate_offset": gate_offset,
            "parameters": rank_summary["parameters"],
            "training_summary": rank_summary,
        },
        "safety_architecture": {
            "features": d115.FEATURES,
            "hidden": d115.HIDDEN,
            "parameters": 6_097,
            "combined_parameters": 12_723,
            "epochs": d115.EPOCHS,
            "batch_size": d115.BATCH_SIZE,
            "training_threads": 1,
        },
        "matrix": {
            "safety_seeds": SAFETY_SEEDS,
            "target_nonpositive_recalls": SPECIFICITY_TARGETS,
            "compositions": COMPOSITIONS,
            "cells": len(cells),
        },
        "original_d126_controller": {
            "fit_metrics": original_train,
            "development_metrics": original_development,
        },
        "safety_training": safety_training,
        "results": cells,
        "cross_seed_aggregates": aggregates,
        "descriptive_best_stable_cell": best,
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (
                d119.TRAIN_ARMS,
                d119.TRAIN_BASELINES,
                d126.OUTPUT,
                d126.VALIDATION_ARMS,
                d126.VALIDATION_BASELINES,
            )
        },
        "decision": "retrospective_only_choose_one_prospective_d130_composition",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
