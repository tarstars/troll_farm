#!/usr/bin/env python3
"""Run D153's frozen grouped value cross-fit and deterministic full fit."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import gc
import json
import math
import multiprocessing
from pathlib import Path

import numpy as np
import torch

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d152a_conditional_second_value as d152
from cgauto import build_d153a_conditional_value_dataset as dataset_builder
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d153a_conditional_value_policy as trainer
from cgauto import yt_d148_priority_joint_teacher as yt_d148


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d153a-conditional-value-policy-crossfit-protocol-2026-07-23.md"
LOCK = BASE / "d153a-conditional-value-policy-crossfit-lock.json"
SELECTION_A = BASE / "d153a-conditional-value-policy-crossfit-selection-a.json"
SELECTION_B = BASE / "d153a-conditional-value-policy-crossfit-selection-b.json"
CHECKPOINT = BASE / "d153a-conditional-value-policy.pt"
OUTPUT = BASE / "d153a-conditional-value-policy-crossfit-result.json"

SEEDS = (15_301, 15_302, 15_303, 15_304)
FOLDS = 8
WORKERS = 10
THREADS_PER_WORKER = 2
FULL_FIT_THREADS = 20

SCALAR_COUNT_KEYS = (
    "groups",
    "selected_value_sum",
    "oracle_value_sum",
    "oracle_regret_sum",
    "strict_positive_selections",
    "harmful_negative_selections",
    "within_ten_of_oracle",
    "selected_control",
    "new_crop_failures",
    "control_worker_three",
    "selected_worker_three",
    "sign_positive_actions",
    "sign_positive_correct",
    "sign_nonpositive_actions",
    "sign_nonpositive_correct",
)

_DATASET = None


def sha256(path: Path) -> str:
    return yt_d148.sha256(path)


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D153 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def load_dataset() -> tuple[dict, dict]:
    examples, structural = dataset_builder.conditional_examples()
    dataset = dataset_builder.padded_dataset(examples)
    expected = {
        "groups": 909,
        "actions": 16_228,
        "noncontrol_actions": 15_319,
        "active_groups": 388,
        "inactive_groups": 521,
        "minimum_legal_actions": 4,
        "maximum_legal_actions": 28,
    }
    if any(structural[name] != value for name, value in expected.items()):
        raise RuntimeError(f"D153 structural dataset drift: {structural!r}")
    if set(np.unique(dataset["folds"])) != set(range(FOLDS)):
        raise RuntimeError("D153 fold set drift")
    if set(dataset["opponents"]) != set(d112.OPPONENTS):
        raise RuntimeError("D153 opponent family set drift")
    for value in dataset.values():
        if isinstance(value, np.ndarray):
            value.flags.writeable = False
    return dataset, structural


def prediction_counts(model: trainer.ConditionalValueScorer, dataset: dict) -> dict:
    predicted = trainer.predict_margin_values(model, dataset)
    valid = np.asarray(dataset["valid"], dtype=np.bool_)
    targets = np.asarray(dataset["target_values"], dtype=np.float32)
    if not np.all(valid[:, 0]) or not np.all(targets[:, 0] == 0.0):
        raise RuntimeError("D153 evaluation control drift")
    selected = predicted.argmax(axis=1)
    oracle_scores = targets.copy()
    oracle_scores[~valid] = -np.inf
    oracle = oracle_scores.argmax(axis=1)
    roots = np.arange(len(selected))
    selected_values = targets[roots, selected]
    oracle_values = targets[roots, oracle]
    regrets = oracle_values - selected_values
    if np.any(regrets < 0):
        raise RuntimeError("D153 exact oracle regret is negative")

    workers = np.asarray(dataset["terminal_own_workers"])
    crops = np.asarray(dataset["terminal_own_created_crops"])
    control_crops = crops[:, 0]
    selected_crops = crops[roots, selected]
    control_workers = workers[:, 0]
    selected_workers = workers[roots, selected]

    noncontrol = valid.copy()
    noncontrol[:, 0] = False
    positive_truth = (targets > 0.0) & noncontrol
    nonpositive_truth = (targets <= 0.0) & noncontrol
    positive_prediction = predicted > 0.0
    family_value_sum = {name: 0 for name in d112.OPPONENTS}
    family_groups = {name: 0 for name in d112.OPPONENTS}
    for opponent, value in zip(dataset["opponents"], selected_values, strict=True):
        family_value_sum[opponent] += int(value)
        family_groups[opponent] += 1
    counts = {
        "groups": len(selected),
        "selected_value_sum": int(selected_values.sum()),
        "oracle_value_sum": int(oracle_values.sum()),
        "oracle_regret_sum": int(regrets.sum()),
        "strict_positive_selections": int((selected_values > 0.0).sum()),
        "harmful_negative_selections": int((selected_values < 0.0).sum()),
        "within_ten_of_oracle": int((regrets <= 10.0).sum()),
        "selected_control": int((selected == 0).sum()),
        "new_crop_failures": int(
            ((control_crops > 0) & (selected_crops == 0)).sum()
        ),
        "control_worker_three": int((control_workers >= 3).sum()),
        "selected_worker_three": int((selected_workers >= 3).sum()),
        "sign_positive_actions": int(positive_truth.sum()),
        "sign_positive_correct": int(
            (positive_prediction & positive_truth).sum()
        ),
        "sign_nonpositive_actions": int(nonpositive_truth.sum()),
        "sign_nonpositive_correct": int(
            ((~positive_prediction) & nonpositive_truth).sum()
        ),
        "family_value_sum": family_value_sum,
        "family_groups": family_groups,
    }
    return counts


def metric_view(counts: dict) -> dict:
    groups = int(counts["groups"])
    if not groups:
        raise ValueError("D153 cannot summarize zero groups")

    def rate(numerator: str, denominator: str = "groups") -> float:
        total = int(counts[denominator])
        return float(counts[numerator]) / total if total else 0.0

    family_means = {
        name: float(counts["family_value_sum"][name])
        / int(counts["family_groups"][name])
        for name in d112.OPPONENTS
        if int(counts["family_groups"][name])
    }
    if set(family_means) != set(d112.OPPONENTS):
        raise RuntimeError("D153 metric view lacks an opponent family")
    positive_recall = rate("sign_positive_correct", "sign_positive_actions")
    nonpositive_recall = rate(
        "sign_nonpositive_correct", "sign_nonpositive_actions"
    )
    oracle_sum = int(counts["oracle_value_sum"])
    result = {
        **counts,
        "mean_selected_value": float(counts["selected_value_sum"]) / groups,
        "strict_positive_rate": rate("strict_positive_selections"),
        "harmful_negative_rate": rate("harmful_negative_selections"),
        "oracle_value_capture": (
            float(counts["selected_value_sum"]) / oracle_sum if oracle_sum else 0.0
        ),
        "mean_oracle_regret": float(counts["oracle_regret_sum"]) / groups,
        "within_ten_rate": rate("within_ten_of_oracle"),
        "selected_control_rate": rate("selected_control"),
        "sign_positive_recall": positive_recall,
        "sign_nonpositive_recall": nonpositive_recall,
        "sign_balanced_accuracy": (positive_recall + nonpositive_recall) / 2.0,
        "control_worker_three_rate": rate("control_worker_three"),
        "selected_worker_three_rate": rate("selected_worker_three"),
        "family_mean_selected_value": family_means,
        "positive_families": sum(value > 0.0 for value in family_means.values()),
        "worst_family_mean_value": min(family_means.values()),
    }
    if not all(
        math.isfinite(value)
        for value in result.values()
        if isinstance(value, float)
    ):
        raise RuntimeError("D153 metric is nonfinite")
    return result


def merge_counts(items: list[dict]) -> dict:
    if not items:
        raise ValueError("D153 cannot merge no held counts")
    expected = set(SCALAR_COUNT_KEYS) | {"family_value_sum", "family_groups"}
    if any(set(item) != expected for item in items):
        raise RuntimeError("D153 held count schema drift")
    result = {
        key: sum(int(item[key]) for item in items) for key in SCALAR_COUNT_KEYS
    }
    for nested in ("family_value_sum", "family_groups"):
        result[nested] = {
            family: sum(int(item[nested][family]) for item in items)
            for family in d112.OPPONENTS
        }
    return result


def held_gates(metrics: dict, folds: list[dict]) -> dict[str, bool]:
    return {
        "mean_selected_value_at_least_5": metrics["mean_selected_value"] >= 5.0,
        "strict_positive_rate_at_least_30pct": metrics[
            "strict_positive_rate"
        ]
        >= 0.30,
        "harmful_negative_rate_at_most_15pct": metrics[
            "harmful_negative_rate"
        ]
        <= 0.15,
        "oracle_value_capture_at_least_15pct": metrics[
            "oracle_value_capture"
        ]
        >= 0.15,
        "mean_oracle_regret_at_most_26": metrics["mean_oracle_regret"] <= 26.0,
        "within_ten_rate_at_least_20pct": metrics["within_ten_rate"] >= 0.20,
        "every_fold_mean_nonnegative": all(
            fold["metrics"]["mean_selected_value"] >= 0.0 for fold in folds
        ),
        "at_least_six_positive_families": metrics["positive_families"] >= 6,
        "worst_family_at_least_minus_2": metrics[
            "worst_family_mean_value"
        ]
        >= -2.0,
        "sign_balanced_accuracy_at_least_60pct": metrics[
            "sign_balanced_accuracy"
        ]
        >= 0.60,
        "zero_new_crop_failures": metrics["new_crop_failures"] == 0,
        "worker_three_within_5pp": metrics["selected_worker_three_rate"]
        >= metrics["control_worker_three_rate"] - 0.05,
    }


def _fold_seed_worker(held_fold: int, seed: int) -> dict:
    if _DATASET is None:
        raise RuntimeError("D153 fork worker lacks its read-only dataset")
    folds = np.asarray(_DATASET["folds"])
    train_indices = np.flatnonzero(folds != held_fold)
    held_indices = np.flatnonzero(folds == held_fold)
    training = trainer.subset(_DATASET, train_indices)
    held = trainer.subset(_DATASET, held_indices)
    model, training_summary = trainer.train_model(
        training, seed, threads=THREADS_PER_WORKER
    )
    counts = prediction_counts(model, held)
    result = {
        "held_fold": held_fold,
        "seed": seed,
        "training_groups": len(train_indices),
        "held_groups": len(held_indices),
        "model_hash": training_summary["model_hash"],
        "training": training_summary,
        "counts": counts,
        "metrics": metric_view(counts),
    }
    del training, held, model
    gc.collect()
    return result


def selection_key(candidate: dict) -> tuple:
    metrics = candidate["held_metrics"]
    return (
        min(fold["metrics"]["mean_selected_value"] for fold in candidate["folds"]),
        metrics["worst_family_mean_value"],
        metrics["mean_selected_value"],
        metrics["oracle_value_capture"],
        metrics["within_ten_rate"],
        -metrics["harmful_negative_rate"],
        -candidate["seed"],
    )


def run_selection() -> dict:
    global _DATASET
    lock = verify_lock()
    parent = json.loads(d152.OUTPUT.read_text())
    if parent["decision"] != "open_grouped_conditional_value_crossfit":
        raise RuntimeError("D152 did not authorize D153")
    _DATASET, structural = load_dataset()
    context = multiprocessing.get_context("fork")
    jobs = [(held, seed) for held in range(FOLDS) for seed in SEEDS]
    try:
        with ProcessPoolExecutor(max_workers=WORKERS, mp_context=context) as executor:
            futures = [executor.submit(_fold_seed_worker, *job) for job in jobs]
            rows = [future.result() for future in futures]
    finally:
        _DATASET = None
        gc.collect()

    candidates = []
    for seed in SEEDS:
        folds = sorted(
            (row for row in rows if row["seed"] == seed),
            key=lambda row: row["held_fold"],
        )
        if [row["held_fold"] for row in folds] != list(range(FOLDS)):
            raise RuntimeError("D153 selection lacks an exact fold set")
        counts = merge_counts([row["counts"] for row in folds])
        metrics = metric_view(counts)
        gates = held_gates(metrics, folds)
        candidates.append(
            {
                "seed": seed,
                "folds": folds,
                "held_counts": counts,
                "held_metrics": metrics,
                "held_gates": gates,
                "eligible": all(gates.values()),
            }
        )
    eligible = [candidate for candidate in candidates if candidate["eligible"]]
    selected = max(eligible, key=selection_key) if eligible else None
    return {
        "schema": "troll-farm-d153a-conditional-value-crossfit-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d152": {
            "path": str(d152.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d152.OUTPUT),
            "decision": parent["decision"],
        },
        "architecture": {
            "model": "state64+action379 -> 16 ReLU -> 1, relative to slot zero",
            "parameters": trainer.PARAMETERS,
            "epochs": trainer.EPOCHS,
            "batch_size": trainer.BATCH_SIZE,
            "learning_rate": trainer.LEARNING_RATE,
            "weight_decay": trainer.WEIGHT_DECAY,
            "margin_scale": trainer.MARGIN_SCALE,
            "soft_target_temperature_margin": trainer.SOFT_TARGET_TEMPERATURE_MARGIN,
            "loss": "equal group-soft-cross-entropy plus group-mean Smooth-L1",
            "folds": FOLDS,
            "seeds": SEEDS,
            "workers": WORKERS,
            "threads_per_worker": THREADS_PER_WORKER,
            "process_start_method": "fork",
        },
        "dataset": structural,
        "candidates": candidates,
        "eligible": len(eligible),
        "selected": selected,
        "decision": (
            "repeat_exact_selection"
            if selected is not None
            else "close_d153_compact_conditional_value_policy"
        ),
    }


def save_selection(path: Path) -> dict:
    if path.exists():
        raise FileExistsError(path)
    result = run_selection()
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def checkpoint_payload(model, selected: dict, training: dict) -> dict:
    return {
        "schema": "troll-farm-d153a-conditional-value-policy-checkpoint-v1",
        "parameters": d115.parameter_count(model),
        "seed": selected["seed"],
        "model_hash": d115.canonical_model_hash(model),
        "margin_scale": trainer.MARGIN_SCALE,
        "control_slot": 0,
        "training": training,
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def finalize() -> dict:
    lock = verify_lock()
    exact_repeat = (
        SELECTION_A.exists()
        and SELECTION_B.exists()
        and SELECTION_A.read_bytes() == SELECTION_B.read_bytes()
    )
    selection = json.loads(SELECTION_A.read_text()) if SELECTION_A.exists() else {}
    selected = selection.get("selected") if exact_repeat else None
    if selected is not None:
        dataset, structural = load_dataset()
        seed = int(selected["seed"])
        model_a, training_a = trainer.train_model(
            dataset, seed, threads=FULL_FIT_THREADS
        )
        model_b, training_b = trainer.train_model(
            dataset, seed, threads=FULL_FIT_THREADS
        )
        hash_a = d115.canonical_model_hash(model_a)
        hash_b = d115.canonical_model_hash(model_b)
        full_repeat = hash_a == hash_b and training_a == training_b
        parameter_pass = d115.parameter_count(model_a) == trainer.PARAMETERS
        finite_pass = all(
            bool(torch.isfinite(parameter).all()) for parameter in model_a.parameters()
        )
        if not (full_repeat and parameter_pass and finite_pass):
            raise RuntimeError("D153 deterministic full-fit gate failed")
        if CHECKPOINT.exists():
            raise FileExistsError(CHECKPOINT)
        torch.save(checkpoint_payload(model_a, selected, training_a), CHECKPOINT)
        counts = prediction_counts(model_a, dataset)
        full_fit = {
            "seed": seed,
            "model_hash_a": hash_a,
            "model_hash_b": hash_b,
            "exact_model_and_summary_repeat": full_repeat,
            "parameters": d115.parameter_count(model_a),
            "finite_parameters": finite_pass,
            "training": training_a,
            "in_sample_counts": counts,
            "in_sample_metrics": metric_view(counts),
            "dataset": structural,
        }
        checkpoint = {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "bytes": CHECKPOINT.stat().st_size,
            "sha256": sha256(CHECKPOINT),
            "model_hash": hash_a,
        }
    else:
        full_fit = None
        checkpoint = None
    passed = selected is not None and full_fit is not None
    result = {
        "schema": "troll-farm-d153a-conditional-value-policy-crossfit-result-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "selection_a": {
            "path": str(SELECTION_A.relative_to(ROOT)),
            "sha256": sha256(SELECTION_A) if SELECTION_A.exists() else None,
        },
        "selection_b": {
            "path": str(SELECTION_B.relative_to(ROOT)),
            "sha256": sha256(SELECTION_B) if SELECTION_B.exists() else None,
        },
        "selection_exact_repeat": exact_repeat,
        "selected": selected,
        "full_fit": full_fit,
        "checkpoint": checkpoint,
        "pass": passed,
        "decision": (
            "open_d154_first_stage_value_construction"
            if passed
            else "close_d153_compact_conditional_value_policy"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("selection-a", "selection-b", "finalize"))
    args = parser.parse_args()
    if args.mode == "selection-a":
        save_selection(SELECTION_A)
    elif args.mode == "selection-b":
        save_selection(SELECTION_B)
    else:
        finalize()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
