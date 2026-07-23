#!/usr/bin/env python3
"""Run D154's frozen conditional-value representation ablation."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import gc
import json
import multiprocessing
from pathlib import Path
import statistics

import numpy as np

from cgauto import analyze_d153b_oof_confidence_abstention as d153b
from cgauto import build_d153a_conditional_value_dataset as dataset_builder
from cgauto import run_d153a_conditional_value_selection as d153a
from cgauto import train_d153a_conditional_value_policy as d153_trainer
from cgauto import train_d154a_conditional_value_representations as trainer


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d154a-conditional-value-representation-ablation-protocol-2026-07-23.md"
LOCK = BASE / "d154a-conditional-value-representation-ablation-lock.json"
SELECTION_A = BASE / "d154a-conditional-value-representation-ablation-selection-a.json"
SELECTION_B = BASE / "d154a-conditional-value-representation-ablation-selection-b.json"
OUTPUT = BASE / "d154a-conditional-value-representation-ablation-result.json"

_DATASET = None


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = d153a.sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D154 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": d153a.sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def load_dataset() -> tuple[dict, dict]:
    dataset, structural = d153a.load_dataset()
    if dataset["summary"] != dataset_builder.padded_dataset(
        dataset_builder.conditional_examples()[0]
    )["summary"]:
        raise RuntimeError("D154 repeated dataset construction drift")
    return dataset, structural


def _fold_seed_worker(held_fold: int, seed: int) -> list[dict]:
    if _DATASET is None:
        raise RuntimeError("D154 fork worker lacks its read-only dataset")
    folds = np.asarray(_DATASET["folds"])
    train_indices = np.flatnonzero(folds != held_fold)
    held_indices = np.flatnonzero(folds == held_fold)
    training = d153_trainer.subset(_DATASET, train_indices)
    held = d153_trainer.subset(_DATASET, held_indices)
    results = []
    for representation in trainer.REPRESENTATIONS:
        model, training_summary = trainer.train_model(
            training,
            representation,
            seed,
            threads=d153a.THREADS_PER_WORKER,
        )
        held_scores = trainer.predict_margin_values(model, held, representation)
        held_selected = held_scores.argmax(axis=1)
        held_counts = d153b.counts_from_selected(
            held, held_scores, held_selected
        )
        training_scores = trainer.predict_margin_values(
            model, training, representation
        )
        training_selected = training_scores.argmax(axis=1)
        training_counts = d153b.counts_from_selected(
            training, training_scores, training_selected
        )
        results.append(
            {
                "representation": representation.name,
                "held_fold": held_fold,
                "seed": seed,
                "training_groups": len(train_indices),
                "held_groups": len(held_indices),
                "model_hash": training_summary["model_hash"],
                "training": training_summary,
                "training_metrics": d153a.metric_view(training_counts),
                "held_counts": held_counts,
                "held_metrics": d153a.metric_view(held_counts),
            }
        )
        del model, held_scores, training_scores
        gc.collect()
    del training, held
    gc.collect()
    return results


def candidate_key(candidate: dict) -> tuple:
    metrics = candidate["held_metrics"]
    return (
        min(
            fold["held_metrics"]["mean_selected_value"]
            for fold in candidate["folds"]
        ),
        metrics["worst_family_mean_value"],
        metrics["mean_selected_value"],
        metrics["oracle_value_capture"],
        metrics["within_ten_rate"],
        -metrics["harmful_negative_rate"],
        -candidate["seed"],
        -list(trainer.BY_NAME).index(candidate["representation"]),
    )


def run_selection() -> dict:
    global _DATASET
    lock = verify_lock()
    parent = json.loads(d153b.OUTPUT.read_text())
    if parent["decision"] != "close_scalar_confidence_abstention_for_compact_snapshot_scorer":
        raise RuntimeError("D153b did not authorize D154")
    _DATASET, structural = load_dataset()
    context = multiprocessing.get_context("fork")
    jobs = [
        (held_fold, seed)
        for held_fold in range(d153a.FOLDS)
        for seed in d153a.SEEDS
    ]
    try:
        with ProcessPoolExecutor(
            max_workers=d153a.WORKERS, mp_context=context
        ) as executor:
            futures = [executor.submit(_fold_seed_worker, *job) for job in jobs]
            rows = [row for future in futures for row in future.result()]
    finally:
        _DATASET = None
        gc.collect()

    candidates = []
    representations = []
    for representation in trainer.REPRESENTATIONS:
        representation_candidates = []
        for seed in d153a.SEEDS:
            folds = sorted(
                (
                    row
                    for row in rows
                    if row["representation"] == representation.name
                    and row["seed"] == seed
                ),
                key=lambda row: row["held_fold"],
            )
            if [row["held_fold"] for row in folds] != list(range(d153a.FOLDS)):
                raise RuntimeError("D154 cell lacks an exact fold set")
            counts = d153a.merge_counts([row["held_counts"] for row in folds])
            metrics = d153a.metric_view(counts)
            gate_folds = [
                {"metrics": row["held_metrics"]} for row in folds
            ]
            gates = d153a.held_gates(metrics, gate_folds)
            candidate = {
                "representation": representation.name,
                "inputs": representation.inputs,
                "parameters": representation.parameters,
                "seed": seed,
                "folds": folds,
                "held_counts": counts,
                "held_metrics": metrics,
                "held_gates": gates,
                "eligible": all(gates.values()),
            }
            candidates.append(candidate)
            representation_candidates.append(candidate)
        representations.append(
            {
                "representation": representation.name,
                "inputs": representation.inputs,
                "parameters": representation.parameters,
                "eligible_seeds": sum(
                    row["eligible"] for row in representation_candidates
                ),
                "median_mean_selected_value": statistics.median(
                    row["held_metrics"]["mean_selected_value"]
                    for row in representation_candidates
                ),
                "median_harmful_negative_rate": statistics.median(
                    row["held_metrics"]["harmful_negative_rate"]
                    for row in representation_candidates
                ),
                "median_sign_balanced_accuracy": statistics.median(
                    row["held_metrics"]["sign_balanced_accuracy"]
                    for row in representation_candidates
                ),
                "best_seed": max(
                    representation_candidates, key=candidate_key
                )["seed"],
            }
        )
    eligible = [candidate for candidate in candidates if candidate["eligible"]]
    selected = max(eligible, key=candidate_key) if eligible else None
    return {
        "schema": "troll-farm-d154a-conditional-value-representation-ablation-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent_d153b": {
            "path": str(d153b.OUTPUT.relative_to(ROOT)),
            "sha256": d153a.sha256(d153b.OUTPUT),
            "decision": parent["decision"],
        },
        "architecture": {
            "hidden": 16,
            "epochs": d153_trainer.EPOCHS,
            "batch_size": d153_trainer.BATCH_SIZE,
            "learning_rate": d153_trainer.LEARNING_RATE,
            "weight_decay": d153_trainer.WEIGHT_DECAY,
            "seeds": d153a.SEEDS,
            "folds": d153a.FOLDS,
            "workers": d153a.WORKERS,
            "threads_per_worker": d153a.THREADS_PER_WORKER,
            "fits": len(rows),
        },
        "dataset": structural,
        "representation_summary": representations,
        "candidates": candidates,
        "eligible_cells": len(eligible),
        "selected": selected,
        "decision": "repeat_behavioral_selection",
    }


def save_selection(path: Path) -> dict:
    if path.exists():
        raise FileExistsError(path)
    result = run_selection()
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def behavior_signature(payload: dict) -> list[dict]:
    return [
        {
            "representation": row["representation"],
            "seed": row["seed"],
            "held_counts": row["held_counts"],
            "held_gates": row["held_gates"],
            "eligible": row["eligible"],
            "fold_counts": [fold["held_counts"] for fold in row["folds"]],
        }
        for row in payload["candidates"]
    ]


def finalize() -> dict:
    lock = verify_lock()
    selection_a = json.loads(SELECTION_A.read_text())
    selection_b = json.loads(SELECTION_B.read_text())
    behavior_exact = behavior_signature(selection_a) == behavior_signature(selection_b)
    reference = json.loads(d153a.SELECTION_A.read_text())
    reference_by_seed = {
        row["seed"]: row["held_counts"] for row in reference["candidates"]
    }
    full_reproduction = {
        str(row["seed"]): row["held_counts"] == reference_by_seed[row["seed"]]
        for row in selection_a["candidates"]
        if row["representation"] == "full443"
    }
    hashes_a = {
        (row["representation"], row["seed"], fold["held_fold"]): fold["model_hash"]
        for row in selection_a["candidates"]
        for fold in row["folds"]
    }
    hashes_b = {
        (row["representation"], row["seed"], fold["held_fold"]): fold["model_hash"]
        for row in selection_b["candidates"]
        for fold in row["folds"]
    }
    differing_hashes = sum(hashes_a[key] != hashes_b[key] for key in hashes_a)
    integrity = {
        "behavior_exact_repeat": behavior_exact,
        "all_full443_seeds_reproduce_d153a": all(full_reproduction.values()),
        "exactly_192_fits_per_replica": len(hashes_a) == len(hashes_b) == 192,
    }
    selected = selection_a["selected"] if all(integrity.values()) else None
    passed = selected is not None
    result = {
        "schema": "troll-farm-d154a-conditional-value-representation-ablation-result-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "selection_a": {
            "path": str(SELECTION_A.relative_to(ROOT)),
            "sha256": d153a.sha256(SELECTION_A),
        },
        "selection_b": {
            "path": str(SELECTION_B.relative_to(ROOT)),
            "sha256": d153a.sha256(SELECTION_B),
        },
        "integrity": integrity,
        "full443_reproduction": full_reproduction,
        "differing_model_hashes": differing_hashes,
        "representation_summary": selection_a["representation_summary"],
        "eligible_cells": selection_a["eligible_cells"],
        "selected": selected,
        "pass": passed,
        "decision": (
            "open_fresh_nonreserved_representation_confirmation"
            if passed
            else "close_fixed_semantic_slice_compact_value_models"
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
