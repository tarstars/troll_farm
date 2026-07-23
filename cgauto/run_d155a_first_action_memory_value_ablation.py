#!/usr/bin/env python3
"""Run D155's frozen first-action-memory value ablation."""

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
from cgauto import build_d155a_first_action_memory_dataset as dataset_builder
from cgauto import run_d153a_conditional_value_selection as d153a
from cgauto import run_d154a_conditional_value_representation_ablation as d154a
from cgauto import train_d155a_first_action_memory_value_models as trainer


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d155a-first-action-memory-value-ablation-protocol-2026-07-23.md"
LOCK = BASE / "d155a-first-action-memory-value-ablation-lock.json"
SELECTION_A = BASE / "d155a-first-action-memory-value-ablation-selection-a.json"
SELECTION_B = BASE / "d155a-first-action-memory-value-ablation-selection-b.json"
OUTPUT = BASE / "d155a-first-action-memory-value-ablation-result.json"

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
        raise RuntimeError(f"D155 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": d153a.sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def load_dataset() -> tuple[dict, dict]:
    examples, structural = dataset_builder.memory_examples()
    dataset = dataset_builder.padded_dataset(examples)
    expected = {
        "groups": 909,
        "actions": 16_228,
        "active_groups": 388,
        "first_action_groups": 909,
        "nonzero_first_slots": 909,
    }
    if any(structural[name] != value for name, value in expected.items()):
        raise RuntimeError(f"D155 memory dataset drift: {structural!r}")
    if set(np.unique(dataset["folds"])) != set(range(d153a.FOLDS)):
        raise RuntimeError("D155 fold set drift")
    for value in dataset.values():
        if isinstance(value, np.ndarray):
            value.flags.writeable = False
    return dataset, structural


def _fold_seed_worker(held_fold: int, seed: int) -> list[dict]:
    if _DATASET is None:
        raise RuntimeError("D155 fork worker lacks its read-only dataset")
    folds = np.asarray(_DATASET["folds"])
    train_indices = np.flatnonzero(folds != held_fold)
    held_indices = np.flatnonzero(folds == held_fold)
    training = trainer.subset(_DATASET, train_indices)
    held = trainer.subset(_DATASET, held_indices)
    results = []
    for architecture in trainer.ARCHITECTURES:
        model, training_summary = trainer.train_model(
            training,
            architecture,
            seed,
            threads=d153a.THREADS_PER_WORKER,
        )
        held_scores = trainer.predict_margin_values(model, held, architecture)
        held_selected = held_scores.argmax(axis=1)
        held_counts = d153b.counts_from_selected(held, held_scores, held_selected)
        training_scores = trainer.predict_margin_values(
            model, training, architecture
        )
        training_selected = training_scores.argmax(axis=1)
        training_counts = d153b.counts_from_selected(
            training, training_scores, training_selected
        )
        results.append(
            {
                "architecture": architecture.name,
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
        -list(trainer.BY_NAME).index(candidate["architecture"]),
    )


def run_selection() -> dict:
    global _DATASET
    lock = verify_lock()
    parent = json.loads(d154a.OUTPUT.read_text())
    if parent["decision"] != "close_fixed_semantic_slice_compact_value_models":
        raise RuntimeError("D154a did not authorize D155")
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
    architecture_summary = []
    for architecture in trainer.ARCHITECTURES:
        architecture_candidates = []
        for seed in d153a.SEEDS:
            folds = sorted(
                (
                    row
                    for row in rows
                    if row["architecture"] == architecture.name
                    and row["seed"] == seed
                ),
                key=lambda row: row["held_fold"],
            )
            if [row["held_fold"] for row in folds] != list(range(d153a.FOLDS)):
                raise RuntimeError("D155 cell lacks an exact fold set")
            counts = d153a.merge_counts([row["held_counts"] for row in folds])
            metrics = d153a.metric_view(counts)
            gates = d153a.held_gates(
                metrics, [{"metrics": row["held_metrics"]} for row in folds]
            )
            candidate = {
                "architecture": architecture.name,
                "kind": architecture.kind,
                "context_inputs": architecture.context_inputs,
                "action_inputs": architecture.action_inputs,
                "parameters": architecture.parameters,
                "seed": seed,
                "folds": folds,
                "held_counts": counts,
                "held_metrics": metrics,
                "held_gates": gates,
                "eligible": all(gates.values()),
            }
            candidates.append(candidate)
            architecture_candidates.append(candidate)
        architecture_summary.append(
            {
                "architecture": architecture.name,
                "kind": architecture.kind,
                "parameters": architecture.parameters,
                "eligible_seeds": sum(row["eligible"] for row in architecture_candidates),
                "median_mean_selected_value": statistics.median(
                    row["held_metrics"]["mean_selected_value"]
                    for row in architecture_candidates
                ),
                "median_harmful_negative_rate": statistics.median(
                    row["held_metrics"]["harmful_negative_rate"]
                    for row in architecture_candidates
                ),
                "median_sign_balanced_accuracy": statistics.median(
                    row["held_metrics"]["sign_balanced_accuracy"]
                    for row in architecture_candidates
                ),
                "best_seed": max(architecture_candidates, key=candidate_key)["seed"],
            }
        )
    eligible = [candidate for candidate in candidates if candidate["eligible"]]
    selected = max(eligible, key=candidate_key) if eligible else None
    return {
        "schema": "troll-farm-d155a-first-action-memory-value-ablation-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent_d154a": {
            "path": str(d154a.OUTPUT.relative_to(ROOT)),
            "sha256": d153a.sha256(d154a.OUTPUT),
            "decision": parent["decision"],
        },
        "architecture": {
            "hidden": 16,
            "epochs": 80,
            "batch_size": 64,
            "seeds": d153a.SEEDS,
            "folds": d153a.FOLDS,
            "workers": d153a.WORKERS,
            "threads_per_worker": d153a.THREADS_PER_WORKER,
            "fits": len(rows),
        },
        "dataset": structural,
        "architecture_summary": architecture_summary,
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
            "architecture": row["architecture"],
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
    reference = json.loads(d154a.SELECTION_A.read_text())
    reference_by_seed = {
        row["seed"]: row["held_counts"]
        for row in reference["candidates"]
        if row["representation"] == "semantic_context115"
    }
    snapshot_reproduction = {
        str(row["seed"]): row["held_counts"] == reference_by_seed[row["seed"]]
        for row in selection_a["candidates"]
        if row["architecture"] == "snapshot_compact"
    }
    hashes_a = {
        (row["architecture"], row["seed"], fold["held_fold"]): fold["model_hash"]
        for row in selection_a["candidates"]
        for fold in row["folds"]
    }
    hashes_b = {
        (row["architecture"], row["seed"], fold["held_fold"]): fold["model_hash"]
        for row in selection_b["candidates"]
        for fold in row["folds"]
    }
    differing_hashes = sum(hashes_a[key] != hashes_b[key] for key in hashes_a)
    integrity = {
        "behavior_exact_repeat": behavior_exact,
        "all_snapshot_seeds_reproduce_d154a": all(snapshot_reproduction.values()),
        "exactly_160_fits_per_replica": len(hashes_a) == len(hashes_b) == 160,
    }
    selected = selection_a["selected"] if all(integrity.values()) else None
    passed = selected is not None
    result = {
        "schema": "troll-farm-d155a-first-action-memory-value-ablation-result-v1",
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
        "snapshot_reproduction": snapshot_reproduction,
        "differing_model_hashes": differing_hashes,
        "architecture_summary": selection_a["architecture_summary"],
        "eligible_cells": selection_a["eligible_cells"],
        "selected": selected,
        "pass": passed,
        "decision": (
            "open_fresh_nonreserved_first_memory_confirmation"
            if passed
            else "close_static_first_action_memory_value_models"
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
