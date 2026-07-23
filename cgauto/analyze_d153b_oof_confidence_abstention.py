#!/usr/bin/env python3
"""Analyze whether D153 out-of-fold confidence supports safe abstention."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import export_d153b_oof_confidence_scores as exporter
from cgauto import run_d153a_conditional_value_selection as d153a
from cgauto import train_d153a_conditional_value_policy as trainer


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
OUTPUT = BASE / "d153b-oof-confidence-abstention-diagnostic-result.json"
THRESHOLDS = (0.0, 2.0, 5.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0)
MAX_SCORE_DRIFT = 1.0e-4


def score_key(row: dict) -> tuple[int, int, int, str, int]:
    return (
        int(row["seed"]),
        int(row["map_seed"]),
        int(row["seat"]),
        str(row["opponent"]),
        int(row["candidate_slot"]),
    )


def read_scores(path: Path) -> dict[tuple[int, int, int, str, int], dict]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if list(reader.fieldnames or ()) != list(exporter.SCORE_FIELDS):
            raise RuntimeError("D153b score schema drift")
        rows = list(reader)
    result = {score_key(row): row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError("D153b duplicate score key")
    return result


def score_matrices(rows: dict, dataset: dict) -> dict[int, np.ndarray]:
    shape = np.asarray(dataset["valid"]).shape
    matrices = {seed: np.full(shape, -np.inf, dtype=np.float64) for seed in d153a.SEEDS}
    task_indices = {task: index for index, task in enumerate(dataset["tasks"])}
    expected = set()
    for group, task in enumerate(dataset["tasks"]):
        fold = int(dataset["folds"][group])
        count = int(dataset["valid"][group].sum())
        slots = dataset["candidate_slots"][group, :count]
        for action, slot in enumerate(slots):
            for seed in d153a.SEEDS:
                key = (seed, int(task[0]), int(task[1]), str(task[2]), int(slot))
                expected.add(key)
                row = rows.get(key)
                if row is None:
                    raise RuntimeError(f"D153b missing score: {key!r}")
                if int(row["held_fold"]) != fold:
                    raise RuntimeError("D153b held-fold annotation drift")
                if int(row["target_active"]) != int(dataset["target_active"][group]):
                    raise RuntimeError("D153b target-active annotation drift")
                if int(row["exact_value"]) != int(dataset["target_values"][group, action]):
                    raise RuntimeError("D153b exact target drift")
                matrices[seed][group, action] = float(row["predicted_value"])
    if expected != set(rows):
        raise RuntimeError(
            f"D153b score key set drift: expected={len(expected)} actual={len(rows)}"
        )
    if len(task_indices) != len(dataset["tasks"]):
        raise RuntimeError("D153b duplicate dataset task")
    valid = np.asarray(dataset["valid"], dtype=np.bool_)
    for matrix in matrices.values():
        if not np.isfinite(matrix[valid]).all() or not np.all(matrix[:, 0] == 0.0):
            raise RuntimeError("D153b invalid relative score matrix")
    return matrices


def selected_actions(scores: np.ndarray, valid: np.ndarray, threshold: float) -> np.ndarray:
    eligible = np.asarray(valid, dtype=np.bool_).copy()
    eligible[:, 0] = False
    noncontrol = scores.copy()
    noncontrol[~eligible] = -np.inf
    best = noncontrol.argmax(axis=1)
    roots = np.arange(len(best))
    clears_threshold = noncontrol[roots, best] >= threshold
    if threshold == 0.0:
        # Slot zero occurs first and therefore wins an exact zero-score tie in
        # D153's stable argmax over control plus noncontrol actions.
        clears_threshold &= noncontrol[roots, best] > 0.0
    return np.where(clears_threshold, best, 0)


def counts_from_selected(dataset: dict, scores: np.ndarray, selected: np.ndarray) -> dict:
    valid = np.asarray(dataset["valid"], dtype=np.bool_)
    targets = np.asarray(dataset["target_values"], dtype=np.float32)
    roots = np.arange(len(selected))
    oracle_scores = targets.copy()
    oracle_scores[~valid] = -np.inf
    oracle = oracle_scores.argmax(axis=1)
    selected_values = targets[roots, selected]
    oracle_values = targets[roots, oracle]
    regrets = oracle_values - selected_values
    workers = np.asarray(dataset["terminal_own_workers"])
    crops = np.asarray(dataset["terminal_own_created_crops"])
    selected_workers = workers[roots, selected]
    selected_crops = crops[roots, selected]
    noncontrol = valid.copy()
    noncontrol[:, 0] = False
    positive_truth = (targets > 0.0) & noncontrol
    nonpositive_truth = (targets <= 0.0) & noncontrol
    positive_prediction = scores > 0.0
    family_value_sum = {name: 0 for name in d112.OPPONENTS}
    family_groups = {name: 0 for name in d112.OPPONENTS}
    for opponent, value in zip(dataset["opponents"], selected_values, strict=True):
        family_value_sum[opponent] += int(value)
        family_groups[opponent] += 1
    return {
        "groups": len(selected),
        "selected_value_sum": int(selected_values.sum()),
        "oracle_value_sum": int(oracle_values.sum()),
        "oracle_regret_sum": int(regrets.sum()),
        "strict_positive_selections": int((selected_values > 0.0).sum()),
        "harmful_negative_selections": int((selected_values < 0.0).sum()),
        "within_ten_of_oracle": int((regrets <= 10.0).sum()),
        "selected_control": int((selected == 0).sum()),
        "new_crop_failures": int(
            ((crops[:, 0] > 0) & (selected_crops == 0)).sum()
        ),
        "control_worker_three": int((workers[:, 0] >= 3).sum()),
        "selected_worker_three": int((selected_workers >= 3).sum()),
        "sign_positive_actions": int(positive_truth.sum()),
        "sign_positive_correct": int((positive_prediction & positive_truth).sum()),
        "sign_nonpositive_actions": int(nonpositive_truth.sum()),
        "sign_nonpositive_correct": int(
            ((~positive_prediction) & nonpositive_truth).sum()
        ),
        "family_value_sum": family_value_sum,
        "family_groups": family_groups,
    }


def subset_selected(dataset: dict, indices: np.ndarray, selected: np.ndarray) -> tuple[dict, np.ndarray]:
    return trainer.subset(dataset, indices), np.asarray(selected)[indices]


def diagnostic_gates(metrics: dict, fold_means: dict[str, float]) -> dict[str, bool]:
    noncontrol_rate = 1.0 - metrics["selected_control_rate"]
    return {
        "noncontrol_selection_rate_at_least_10pct": noncontrol_rate >= 0.10,
        "mean_selected_value_at_least_5": metrics["mean_selected_value"] >= 5.0,
        "harmful_negative_rate_at_most_15pct": metrics[
            "harmful_negative_rate"
        ]
        <= 0.15,
        "oracle_value_capture_at_least_15pct": metrics[
            "oracle_value_capture"
        ]
        >= 0.15,
        "every_fold_mean_nonnegative": min(fold_means.values()) >= 0.0,
        "at_least_six_positive_families": metrics["positive_families"] >= 6,
        "worst_family_at_least_minus_2": metrics[
            "worst_family_mean_value"
        ]
        >= -2.0,
        "zero_new_crop_failures": metrics["new_crop_failures"] == 0,
        "worker_three_within_5pp": metrics["selected_worker_three_rate"]
        >= metrics["control_worker_three_rate"] - 0.05,
    }


def evaluate_source(name: str, scores: np.ndarray, dataset: dict) -> dict:
    valid = np.asarray(dataset["valid"], dtype=np.bool_)
    thresholds = []
    for threshold in THRESHOLDS:
        selected = selected_actions(scores, valid, threshold)
        counts = counts_from_selected(dataset, scores, selected)
        metrics = d153a.metric_view(counts)
        fold_means = {}
        for fold in range(d153a.FOLDS):
            indices = np.flatnonzero(np.asarray(dataset["folds"]) == fold)
            held, held_selected = subset_selected(dataset, indices, selected)
            held_scores = scores[indices]
            held_counts = counts_from_selected(held, held_scores, held_selected)
            fold_means[str(fold)] = d153a.metric_view(held_counts)[
                "mean_selected_value"
            ]
        gates = diagnostic_gates(metrics, fold_means)
        thresholds.append(
            {
                "threshold": threshold,
                "selected_slots": dataset["candidate_slots"][
                    np.arange(len(selected)), selected
                ].astype(int).tolist(),
                "counts": counts,
                "metrics": metrics,
                "fold_mean_selected_value": fold_means,
                "gates": gates,
                "supported": all(gates.values()),
            }
        )
    return {"source": name, "thresholds": thresholds}


def calibration_deciles(scores: np.ndarray, dataset: dict) -> list[dict]:
    valid = np.asarray(dataset["valid"], dtype=np.bool_)
    noncontrol = scores.copy()
    eligible = valid.copy()
    eligible[:, 0] = False
    noncontrol[~eligible] = -np.inf
    best = noncontrol.argmax(axis=1)
    roots = np.arange(len(best))
    predicted = noncontrol[roots, best]
    exact = np.asarray(dataset["target_values"])[roots, best]
    order = np.argsort(predicted, kind="stable")
    rows = []
    for decile, indices in enumerate(np.array_split(order, 10)):
        rows.append(
            {
                "decile_low_to_high": decile,
                "groups": len(indices),
                "minimum_predicted_value": float(predicted[indices].min()),
                "maximum_predicted_value": float(predicted[indices].max()),
                "mean_predicted_value": float(predicted[indices].mean()),
                "mean_exact_value": float(exact[indices].mean()),
                "strict_positive_rate": float((exact[indices] > 0.0).mean()),
                "harmful_negative_rate": float((exact[indices] < 0.0).mean()),
            }
        )
    return rows


def main() -> int:
    lock = exporter.verify_lock()
    parent = json.loads(d153a.OUTPUT.read_text())
    metadata_a = json.loads(exporter.METADATA_A.read_text())
    metadata_b = json.loads(exporter.METADATA_B.read_text())
    for metadata, score_path in (
        (metadata_a, exporter.SCORES_A),
        (metadata_b, exporter.SCORES_B),
    ):
        if metadata["scores"]["sha256"] != d153a.sha256(score_path):
            raise RuntimeError("D153b score export changed after metadata write")
    dataset, structural = d153a.load_dataset()
    rows_a = read_scores(exporter.SCORES_A)
    rows_b = read_scores(exporter.SCORES_B)
    matrices_a = score_matrices(rows_a, dataset)
    matrices_b = score_matrices(rows_b, dataset)
    valid = np.asarray(dataset["valid"], dtype=np.bool_)
    maximum_score_drift = max(
        float(np.max(np.abs(matrices_a[seed][valid] - matrices_b[seed][valid])))
        for seed in d153a.SEEDS
    )
    ensemble_a = np.zeros_like(next(iter(matrices_a.values())))
    ensemble_b = np.zeros_like(ensemble_a)
    for seed in d153a.SEEDS:
        ensemble_a[valid] += matrices_a[seed][valid] / len(d153a.SEEDS)
        ensemble_b[valid] += matrices_b[seed][valid] / len(d153a.SEEDS)
    ensemble_a[~valid] = -np.inf
    ensemble_b[~valid] = -np.inf
    sources_a = {f"seed_{seed}": matrices_a[seed] for seed in d153a.SEEDS}
    sources_a["four_seed_mean"] = ensemble_a
    sources_b = {f"seed_{seed}": matrices_b[seed] for seed in d153a.SEEDS}
    sources_b["four_seed_mean"] = ensemble_b
    evaluations = [
        evaluate_source(name, scores, dataset) for name, scores in sources_a.items()
    ]
    evaluations_b = {
        row["source"]: row
        for row in (
            evaluate_source(name, scores, dataset)
            for name, scores in sources_b.items()
        )
    }
    policy_parity_errors = 0
    for source in evaluations:
        repeated = evaluations_b[source["source"]]
        for row_a, row_b in zip(
            source["thresholds"], repeated["thresholds"], strict=True
        ):
            policy_parity_errors += int(
                row_a["selected_slots"] != row_b["selected_slots"]
            )
            row_a.pop("selected_slots")
            row_b.pop("selected_slots")

    zero_reproduction = {}
    selection_a = json.loads(d153a.SELECTION_A.read_text())
    by_seed = {row["seed"]: row for row in selection_a["candidates"]}
    for source in evaluations:
        if not source["source"].startswith("seed_"):
            continue
        seed = int(source["source"].split("_")[1])
        zero = source["thresholds"][0]
        zero_reproduction[str(seed)] = zero["counts"] == by_seed[seed]["held_counts"]

    supported = [
        {"source": source["source"], **row}
        for source in evaluations
        for row in source["thresholds"]
        if row["supported"]
    ]
    integrity_gates = {
        "parent_d153a_closed": parent["decision"]
        == "close_d153_compact_conditional_value_policy",
        "exactly_64912_rows_per_export": len(rows_a) == len(rows_b) == 64_912,
        "exact_action_key_sets": set(rows_a) == set(rows_b),
        "score_drift_at_most_1e_4": maximum_score_drift <= MAX_SCORE_DRIFT,
        "zero_threshold_policy_parity_errors": policy_parity_errors == 0,
        "all_individual_threshold_zero_policies_reproduce_d153a": all(
            zero_reproduction.values()
        ),
    }
    passed = all(integrity_gates.values()) and bool(supported)
    top_scores = ensemble_a.copy()
    top_scores[~valid] = -np.inf
    best_noncontrol = top_scores.copy()
    best_noncontrol[:, 0] = -np.inf
    best_indices = best_noncontrol.argmax(axis=1)
    roots = np.arange(len(best_indices))
    confidence = best_noncontrol[roots, best_indices]
    exact = np.asarray(dataset["target_values"])[roots, best_indices]
    correlation = float(np.corrcoef(confidence, exact)[0, 1])
    if not math.isfinite(correlation):
        raise RuntimeError("D153b confidence correlation is nonfinite")
    result = {
        "schema": "troll-farm-d153b-oof-confidence-abstention-diagnostic-v1",
        "protocol": str(exporter.PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent_d153a": {
            "path": str(d153a.OUTPUT.relative_to(ROOT)),
            "sha256": d153a.sha256(d153a.OUTPUT),
            "decision": parent["decision"],
        },
        "exports": {
            "a": metadata_a["scores"],
            "b": metadata_b["scores"],
            "maximum_absolute_score_drift": maximum_score_drift,
            "differing_model_hashes": sum(
                fit_a["model_hash"] != fit_b["model_hash"]
                for fit_a, fit_b in zip(
                    metadata_a["fits"], metadata_b["fits"], strict=True
                )
            ),
            "policy_parity_errors": policy_parity_errors,
        },
        "dataset": structural,
        "thresholds": THRESHOLDS,
        "individual_zero_reproduction": zero_reproduction,
        "evaluations": evaluations,
        "ensemble_top_score_exact_value_correlation": correlation,
        "ensemble_rank_decile_calibration": calibration_deciles(
            ensemble_a, dataset
        ),
        "supported_pairs": supported,
        "integrity_gates": integrity_gates,
        "pass": passed,
        "decision": (
            "open_nested_abstention_calibration_crossfit"
            if passed
            else "close_scalar_confidence_abstention_for_compact_snapshot_scorer"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
