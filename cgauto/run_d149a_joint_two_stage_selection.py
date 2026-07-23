#!/usr/bin/env python3
"""Run D149's frozen eight-fold selection and deterministic full fit."""

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

from cgauto import analyze_d148b_priority_joint_support_semantics as d148b
from cgauto import build_d149a_joint_two_stage_dataset as dataset_builder
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d149a_joint_two_stage_policy as trainer
from cgauto import yt_d148_priority_joint_teacher as yt_d148


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d149a-joint-two-stage-crossfit-protocol-2026-07-23.md"
LOCK = BASE / "d149a-joint-two-stage-crossfit-lock.json"
SELECTION_A = BASE / "d149a-joint-two-stage-crossfit-selection-a.json"
SELECTION_B = BASE / "d149a-joint-two-stage-crossfit-selection-b.json"
CHECKPOINT = BASE / "d149a-joint-two-stage-policy.pt"
OUTPUT = BASE / "d149a-joint-two-stage-crossfit-result.json"

SEED_PAIRS = (
    (14_901, 14_951),
    (14_902, 14_952),
    (14_903, 14_953),
    (14_904, 14_954),
)
FOLDS = 8
WORKERS = 10
THREADS_PER_WORKER = 2
FULL_FIT_THREADS = 20

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
        raise RuntimeError(f"D149 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def load_dataset() -> tuple[dict, dict]:
    examples, structural = dataset_builder.structural_examples()
    dataset = dataset_builder.padded_dataset(examples)
    expected = {
        "target_tasks": 909,
        "active_tasks": 388,
        "inactive_tasks": 521,
        "raw_groups": 2508,
        "included_groups": 1654,
        "excluded_off_policy_groups": 854,
        "gate_act_groups": 776,
        "gate_wait_groups": 878,
        "rank_groups": 776,
    }
    if any(structural[name] != value for name, value in expected.items()):
        raise RuntimeError(f"D149 structural dataset drift: {structural!r}")
    if set(np.unique(dataset["folds"])) != set(range(FOLDS)):
        raise RuntimeError("D149 fold set drift")
    for value in dataset.values():
        if isinstance(value, np.ndarray):
            value.flags.writeable = False
    return dataset, structural


def prediction_counts(model, dataset: dict) -> dict:
    data = trainer.tensors(dataset)
    context, selected, _ = trainer.winner_context(model.ranker, dataset)
    with torch.no_grad():
        gate_logits = model.gate(context)
    predicted_act = gate_logits > 0.0
    rank_mask = data["rank_targets"] >= 0
    rank_correct = selected == data["rank_targets"]
    valid_counts = data["valid"].sum(dim=1)

    counts = {
        "groups": len(dataset["tasks"]),
        "rank_groups": int(rank_mask.sum()),
        "rank_correct": int((rank_correct & rank_mask).sum()),
        "rank_chance_sum": float((1.0 / valid_counts[rank_mask].float()).sum()),
        "first_rank_groups": 0,
        "first_rank_correct": 0,
        "first_rank_chance_sum": 0.0,
        "second_rank_groups": 0,
        "second_rank_correct": 0,
        "second_rank_chance_sum": 0.0,
        "act_groups": int(data["gate_targets"].sum()),
        "act_correct": int((predicted_act & data["gate_targets"]).sum()),
        "wait_groups": int((~data["gate_targets"]).sum()),
        "wait_correct": int((~predicted_act & ~data["gate_targets"]).sum()),
        "first_joint_correct": 0,
        "second_joint_correct": 0,
        "active_tasks": 0,
        "both_actions_exact_tasks": 0,
        "full_logged_exact_active_tasks": 0,
        "inactive_tasks": 0,
        "inactive_no_false_act_tasks": 0,
    }

    by_task = {}
    for index, task in enumerate(dataset["tasks"]):
        stage = dataset["stages"][index]
        target = bool(data["gate_targets"][index])
        item = {
            "stage": stage,
            "target": target,
            "predicted_act": bool(predicted_act[index]),
            "rank_correct": bool(rank_correct[index]) if target else None,
        }
        by_task.setdefault(task, []).append(item)
        if target and stage in {"first", "second"}:
            prefix = f"{stage}_rank"
            counts[f"{prefix}_groups"] += 1
            counts[f"{prefix}_correct"] += int(rank_correct[index])
            counts[f"{prefix}_chance_sum"] += 1.0 / int(valid_counts[index])
            counts[f"{stage}_joint_correct"] += int(
                predicted_act[index] and rank_correct[index]
            )

    for rows in by_task.values():
        act_rows = [row for row in rows if row["target"]]
        if act_rows:
            if len(act_rows) != 2 or {row["stage"] for row in act_rows} != {
                "first",
                "second",
            }:
                raise RuntimeError("D149 active task lacks its two action targets")
            counts["active_tasks"] += 1
            both = all(row["predicted_act"] and row["rank_correct"] for row in act_rows)
            counts["both_actions_exact_tasks"] += int(both)
            full = all(
                row["predicted_act"] == row["target"]
                and (not row["target"] or row["rank_correct"])
                for row in rows
            )
            counts["full_logged_exact_active_tasks"] += int(full)
        else:
            counts["inactive_tasks"] += 1
            counts["inactive_no_false_act_tasks"] += int(
                all(not row["predicted_act"] for row in rows)
            )
    return counts


def metric_view(counts: dict) -> dict:
    def rate(numerator: str, denominator: str) -> float:
        value = int(counts[denominator])
        return float(counts[numerator]) / value if value else 0.0

    rank_accuracy = rate("rank_correct", "rank_groups")
    rank_chance = float(counts["rank_chance_sum"]) / int(counts["rank_groups"])
    act_recall = rate("act_correct", "act_groups")
    wait_recall = rate("wait_correct", "wait_groups")
    result = {
        **counts,
        "rank_accuracy": rank_accuracy,
        "rank_random_baseline": rank_chance,
        "rank_lift": rank_accuracy / rank_chance,
        "first_rank_accuracy": rate("first_rank_correct", "first_rank_groups"),
        "first_rank_random_baseline": float(counts["first_rank_chance_sum"])
        / int(counts["first_rank_groups"]),
        "second_rank_accuracy": rate("second_rank_correct", "second_rank_groups"),
        "second_rank_random_baseline": float(counts["second_rank_chance_sum"])
        / int(counts["second_rank_groups"]),
        "gate_act_recall": act_recall,
        "gate_wait_recall": wait_recall,
        "gate_balanced_accuracy": (act_recall + wait_recall) / 2.0,
        "first_joint_act_rank_rate": rate("first_joint_correct", "first_rank_groups"),
        "second_joint_act_rank_rate": rate(
            "second_joint_correct", "second_rank_groups"
        ),
        "both_actions_exact_rate": rate(
            "both_actions_exact_tasks", "active_tasks"
        ),
        "full_logged_exact_active_rate": rate(
            "full_logged_exact_active_tasks", "active_tasks"
        ),
        "inactive_no_false_act_rate": rate(
            "inactive_no_false_act_tasks", "inactive_tasks"
        ),
    }
    result["first_rank_lift"] = (
        result["first_rank_accuracy"] / result["first_rank_random_baseline"]
    )
    result["second_rank_lift"] = (
        result["second_rank_accuracy"] / result["second_rank_random_baseline"]
    )
    if not all(
        math.isfinite(value)
        for value in result.values()
        if isinstance(value, float)
    ):
        raise RuntimeError("D149 structural metric is nonfinite")
    return result


def merge_counts(items: list[dict]) -> dict:
    if not items:
        raise ValueError("D149 cannot merge no held counts")
    keys = set(items[0])
    if any(set(item) != keys for item in items):
        raise RuntimeError("D149 held count schema drift")
    return {key: sum(item[key] for item in items) for key in sorted(keys)}


def held_gates(metrics: dict, folds: list[dict]) -> dict[str, bool]:
    return {
        "rank_accuracy_at_least_15pct": metrics["rank_accuracy"] >= 0.15,
        "first_rank_accuracy_at_least_12pct": metrics["first_rank_accuracy"] >= 0.12,
        "second_rank_accuracy_at_least_12pct": metrics["second_rank_accuracy"] >= 0.12,
        "rank_lift_at_least_2x_random": metrics["rank_lift"] >= 2.0,
        "gate_balanced_accuracy_at_least_58pct": metrics[
            "gate_balanced_accuracy"
        ]
        >= 0.58,
        "gate_act_recall_at_least_50pct": metrics["gate_act_recall"] >= 0.50,
        "gate_wait_recall_at_least_50pct": metrics["gate_wait_recall"] >= 0.50,
        "every_fold_gate_balanced_at_least_50pct": all(
            fold["metrics"]["gate_balanced_accuracy"] >= 0.50 for fold in folds
        ),
        "at_least_seven_folds_rank_above_random": sum(
            fold["metrics"]["rank_accuracy"]
            > fold["metrics"]["rank_random_baseline"]
            for fold in folds
        )
        >= 7,
        "first_joint_act_rank_at_least_8pct": metrics[
            "first_joint_act_rank_rate"
        ]
        >= 0.08,
        "second_joint_act_rank_at_least_8pct": metrics[
            "second_joint_act_rank_rate"
        ]
        >= 0.08,
        "both_actions_exact_at_least_1_5pct": metrics[
            "both_actions_exact_rate"
        ]
        >= 0.015,
        "inactive_no_false_act_at_least_25pct": metrics[
            "inactive_no_false_act_rate"
        ]
        >= 0.25,
    }


def _fold_seed_worker(held_fold: int, rank_seed: int, gate_seed: int) -> dict:
    if _DATASET is None:
        raise RuntimeError("D149 fork worker lacks its read-only dataset")
    folds = np.asarray(_DATASET["folds"])
    train_indices = np.flatnonzero(folds != held_fold)
    held_indices = np.flatnonzero(folds == held_fold)
    training = trainer.subset(_DATASET, train_indices)
    held = trainer.subset(_DATASET, held_indices)
    model, training_summary = trainer.train_model(
        training,
        rank_seed,
        gate_seed,
        threads=THREADS_PER_WORKER,
    )
    counts = prediction_counts(model, held)
    result = {
        "held_fold": held_fold,
        "rank_seed": rank_seed,
        "gate_seed": gate_seed,
        "training_groups": len(train_indices),
        "held_groups": len(held_indices),
        "model_hash": training_summary["gate"]["model_hash"],
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
        min(fold["metrics"]["gate_balanced_accuracy"] for fold in candidate["folds"]),
        min(metrics["first_rank_lift"], metrics["second_rank_lift"]),
        metrics["rank_accuracy"],
        metrics["gate_balanced_accuracy"],
        metrics["both_actions_exact_rate"],
        -candidate["rank_seed"],
    )


def run_selection() -> dict:
    global _DATASET
    lock = verify_lock()
    parent = json.loads(d148b.OUTPUT.read_text())
    if parent["decision"] != "open_d149_grouped_joint_two_stage_policy_fit":
        raise RuntimeError("D148b did not authorize D149")
    _DATASET, structural = load_dataset()
    context = multiprocessing.get_context("fork")
    jobs = [
        (held, rank_seed, gate_seed)
        for held in range(FOLDS)
        for rank_seed, gate_seed in SEED_PAIRS
    ]
    try:
        with ProcessPoolExecutor(max_workers=WORKERS, mp_context=context) as executor:
            futures = [executor.submit(_fold_seed_worker, *job) for job in jobs]
            rows = [future.result() for future in futures]
    finally:
        _DATASET = None
        gc.collect()

    candidates = []
    for rank_seed, gate_seed in SEED_PAIRS:
        folds = sorted(
            (row for row in rows if row["rank_seed"] == rank_seed),
            key=lambda row: row["held_fold"],
        )
        if [row["held_fold"] for row in folds] != list(range(FOLDS)):
            raise RuntimeError("D149 selection lacks an exact fold set")
        counts = merge_counts([row["counts"] for row in folds])
        metrics = metric_view(counts)
        gates = held_gates(metrics, folds)
        candidates.append(
            {
                "rank_seed": rank_seed,
                "gate_seed": gate_seed,
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
        "schema": "troll-farm-d149a-joint-two-stage-crossfit-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d148b": {
            "path": str(d148b.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d148b.OUTPUT),
            "decision": parent["decision"],
        },
        "architecture": {
            "parameters": 6_786,
            "rank_epochs": trainer.RANK_EPOCHS,
            "gate_epochs": trainer.GATE_EPOCHS,
            "batch_size": trainer.BATCH_SIZE,
            "learning_rate": trainer.LEARNING_RATE,
            "weight_decay": trainer.WEIGHT_DECAY,
            "gate_threshold": 0.0,
            "folds": FOLDS,
            "seed_pairs": SEED_PAIRS,
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
            else "close_d149_supervised_joint_controller_on_crossfit"
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
        "schema": "troll-farm-d149a-joint-two-stage-policy-checkpoint-v1",
        "parameters": d115.parameter_count(model),
        "rank_seed": selected["rank_seed"],
        "gate_seed": selected["gate_seed"],
        "model_hash": d115.canonical_model_hash(model),
        "gate_threshold": 0.0,
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
        model_a, training_a = trainer.train_model(
            dataset,
            int(selected["rank_seed"]),
            int(selected["gate_seed"]),
            threads=FULL_FIT_THREADS,
        )
        model_b, training_b = trainer.train_model(
            dataset,
            int(selected["rank_seed"]),
            int(selected["gate_seed"]),
            threads=FULL_FIT_THREADS,
        )
        hash_a = d115.canonical_model_hash(model_a)
        hash_b = d115.canonical_model_hash(model_b)
        full_repeat = hash_a == hash_b and training_a == training_b
        parameter_pass = d115.parameter_count(model_a) == 6_786
        finite_pass = all(
            bool(torch.isfinite(parameter).all()) for parameter in model_a.parameters()
        )
        if not (full_repeat and parameter_pass and finite_pass):
            raise RuntimeError("D149 deterministic full-fit gate failed")
        if CHECKPOINT.exists():
            raise FileExistsError(CHECKPOINT)
        torch.save(checkpoint_payload(model_a, selected, training_a), CHECKPOINT)
        full_fit = {
            "rank_seed": selected["rank_seed"],
            "gate_seed": selected["gate_seed"],
            "model_hash_a": hash_a,
            "model_hash_b": hash_b,
            "exact_model_and_summary_repeat": full_repeat,
            "parameters": d115.parameter_count(model_a),
            "finite_parameters": finite_pass,
            "training": training_a,
            "structural": trainer.structural_metrics(model_a, dataset),
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
        "schema": "troll-farm-d149a-joint-two-stage-crossfit-result-v1",
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
            "open_separately_frozen_d150_reserved_panel_validation"
            if passed
            else "close_d149_supervised_joint_controller_on_crossfit"
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
