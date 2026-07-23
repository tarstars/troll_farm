#!/usr/bin/env python3
"""Select a task-balanced variant of D140's best-stop controller."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import gc
import json
import multiprocessing
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126
from cgauto import train_d134a_block_transfer_selected_soft_value_q6 as d134
from cgauto import train_d135a_winner_conditioned_action_gate_q6 as d135
from cgauto import train_d137a_task_sequence_best_stop_gate_q6 as d137
from cgauto import train_d138a_best_stop_plus3pp_calibration_q6 as d138
from cgauto import train_d140a_eight_block_best_stop_selection as d140


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d141a-task-balanced-best-stop-selection-protocol-2026-07-22.md"
LOCK = BASE / "d141a-task-balanced-best-stop-selection-lock.json"
SELECTION_A = BASE / "d141a-task-balanced-best-stop-selection-a.json"
SELECTION_B = BASE / "d141a-task-balanced-best-stop-selection-b.json"
CHECKPOINT = BASE / "d141a-task-balanced-best-stop-selection.pt"
OUTPUT = BASE / "d141a-task-balanced-best-stop-selection-result.json"

BLOCKS = d140.BLOCKS
WORKERS = d140.WORKERS

_FOLD_TRAINING = None
_FOLD_TASKS = None
_FOLD_HELD_PANEL = None
_FOLD_HELD_DATASET = None
_FOLD_HELD_BLOCK = None


def sha256(path: Path) -> str:
    return d117.sha256(path)


def verify_lock() -> dict:
    result = d117.verify_manifest(LOCK)
    if not result["pass"]:
        raise RuntimeError(f"D141 lock mismatch: {result['mismatches']!r}")
    return result


def task_balanced_hard_stop_losses(
    logits: torch.Tensor,
    valid: torch.Tensor,
    targets: torch.Tensor,
) -> torch.Tensor:
    """Return one class-balanced hard-stop loss per task."""
    if logits.shape != valid.shape or logits.shape != targets.shape:
        raise ValueError("D141 hard-stop tensors must have identical shapes")
    if logits.ndim != 2 or logits.shape[0] == 0:
        raise ValueError("D141 hard-stop loss requires a nonempty task matrix")
    if bool((targets & ~valid).any()):
        raise ValueError("D141 hard-stop target lies outside valid roots")
    positive_counts = targets.sum(dim=1)
    if bool((positive_counts > 1).any()):
        raise ValueError("D141 permits at most one positive root per task")
    negative = valid & ~targets
    negative_counts = negative.sum(dim=1)
    wait_tasks = positive_counts == 0
    if bool((wait_tasks & (negative_counts == 0)).any()):
        raise ValueError("D141 wait task has no valid negative root")

    element = functional.binary_cross_entropy_with_logits(
        logits, targets.float(), reduction="none"
    )
    positive_loss = (element * targets).sum(dim=1)
    negative_loss = (element * negative).sum(dim=1) / negative_counts.clamp_min(1)
    positive_tasks = positive_counts == 1
    has_negative = negative_counts > 0
    task_loss = negative_loss
    balanced = 0.5 * (positive_loss + negative_loss)
    task_loss = torch.where(positive_tasks & has_negative, balanced, task_loss)
    task_loss = torch.where(positive_tasks & ~has_negative, positive_loss, task_loss)
    return task_loss


def sequence_losses(
    model: d135.WinnerController,
    sequence: dict,
    indices: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    logits = model.gate(sequence["features"][indices])
    valid = sequence["valid"][indices]
    targets = sequence["hard_stop_targets"][indices]
    masked = logits.masked_fill(~valid, float("-inf"))
    augmented = torch.cat((masked, torch.zeros((len(indices), 1))), dim=1)
    soft_loss = d118.soft_cross_entropy(
        augmented,
        sequence["soft_stop_targets"][indices],
        sequence["augmented_valid"][indices],
    )
    hard_loss = task_balanced_hard_stop_losses(logits, valid, targets).mean()
    return soft_loss, hard_loss


def train_task_balanced_controller(
    dataset: dict, ranker_seed: int, gate_seed: int
) -> tuple[d135.WinnerController, dict]:
    base_model, ranker_training = d119.train_long_model(dataset, ranker_seed)
    ranker = base_model.ranker
    del base_model
    ranker_hash_before = d115.canonical_model_hash(ranker)
    ranker.requires_grad_(False)
    torch.manual_seed(gate_seed)
    model = d135.WinnerController(ranker)
    if d115.parameter_count(model) != 6_786:
        raise RuntimeError("D141 parameter budget changed")
    sequence = d137.sequence_dataset(model.ranker, dataset)
    optimizer = torch.optim.Adam(
        model.gate.parameters(),
        lr=d118.LEARNING_RATE,
        weight_decay=d118.WEIGHT_DECAY,
    )
    generator = np.random.Generator(np.random.PCG64(gate_seed))
    epoch_losses = []
    model.gate.train()
    for _ in range(d137.GATE_EPOCHS):
        order = generator.permutation(len(sequence["task_order"]))
        soft_sum = 0.0
        hard_sum = 0.0
        tasks_seen = 0
        for start in range(0, len(order), d137.TASK_BATCH_SIZE):
            indices = torch.from_numpy(order[start : start + d137.TASK_BATCH_SIZE])
            optimizer.zero_grad(set_to_none=True)
            soft_loss, hard_loss = sequence_losses(model, sequence, indices)
            loss = soft_loss + hard_loss
            loss.backward()
            optimizer.step()
            count = len(indices)
            soft_sum += float(soft_loss.detach()) * count
            hard_sum += float(hard_loss.detach()) * count
            tasks_seen += count
        epoch_losses.append(
            {
                "soft_stop": soft_sum / tasks_seen,
                "task_balanced_hard_stop": hard_sum / tasks_seen,
                "total": (soft_sum + hard_sum) / tasks_seen,
            }
        )
    model.eval()
    all_indices = torch.arange(len(sequence["task_order"]))
    with torch.no_grad():
        final_soft, final_hard = sequence_losses(model, sequence, all_indices)
    ranker_hash_after = d115.canonical_model_hash(model.ranker)
    if ranker_hash_before != ranker_hash_after:
        raise RuntimeError("D141 sequence training changed the frozen ranker")
    return model, {
        "ranker_seed": ranker_seed,
        "gate_seed": gate_seed,
        "ranker_hash": ranker_hash_after,
        "model_hash": d115.canonical_model_hash(model),
        "parameters": d115.parameter_count(model),
        "ranker_training": ranker_training,
        "gate_epochs": d137.GATE_EPOCHS,
        "task_batch_size": d137.TASK_BATCH_SIZE,
        "gate_learning_rate": d118.LEARNING_RATE,
        "gate_weight_decay": d118.WEIGHT_DECAY,
        "gate_cpu_threads": 1,
        "sequence": sequence["summary"],
        "hard_stop_normalization": "equal-task-equal-positive-negative-class-mass",
        "first_epoch_loss": epoch_losses[0],
        "last_epoch_loss": epoch_losses[-1],
        "final_soft_stop_cross_entropy": float(final_soft),
        "final_task_balanced_hard_stop_binary_cross_entropy": float(final_hard),
    }


def sequence_structural_metrics(
    model: d135.WinnerController, dataset: dict
) -> dict:
    sequence = d137.sequence_dataset(model.ranker, dataset)
    tasks = len(sequence["task_order"])
    with torch.no_grad():
        logits = model.gate(sequence["features"])
        masked = logits.masked_fill(~sequence["valid"], float("-inf"))
        augmented = torch.cat((masked, torch.zeros((tasks, 1))), dim=1)
        predicted = augmented.argmax(dim=1)
        target = sequence["soft_stop_targets"].argmax(dim=1)
        target_wait = target == sequence["valid"].shape[1]
        predicted_wait = predicted == sequence["valid"].shape[1]
        positive_recall = float((~predicted_wait[~target_wait]).float().mean())
        wait_recall = float(predicted_wait[target_wait].float().mean())
        soft_loss, hard_loss = sequence_losses(
            model, sequence, torch.arange(tasks)
        )
    result = dict(sequence["summary"])
    result.update(
        {
            "task_choice_accuracy_at_zero": float((predicted == target).float().mean()),
            "positive_task_recall_at_zero": positive_recall,
            "wait_task_recall_at_zero": wait_recall,
            "task_balanced_accuracy_at_zero": (positive_recall + wait_recall) / 2.0,
            "soft_stop_cross_entropy": float(soft_loss),
            "task_balanced_hard_stop_binary_cross_entropy": float(hard_loss),
        }
    )
    return result


def _seed_worker(ranker_seed: int, gate_seed: int) -> dict:
    if any(
        value is None
        for value in (
            _FOLD_TRAINING,
            _FOLD_TASKS,
            _FOLD_HELD_PANEL,
            _FOLD_HELD_DATASET,
            _FOLD_HELD_BLOCK,
        )
    ):
        raise RuntimeError("D141 fork worker lacks its read-only fold context")
    model, training_summary = train_task_balanced_controller(
        _FOLD_TRAINING, ranker_seed, gate_seed
    )
    base_target = training_summary["sequence"]["positive_stop_tasks"]
    target_active = d138.boosted_target(len(_FOLD_TASKS), base_target)
    training_gate = d135.winner_gate_logits(model, _FOLD_TRAINING)
    offset, calibration = d137.count_calibrated_offset(
        _FOLD_TASKS,
        _FOLD_TRAINING["root_order"],
        training_gate,
        target_active,
    )
    calibration["base_positive_stop_tasks"] = base_target
    calibration["extra_active_tasks"] = target_active - base_target
    ranks = d115.model_logits(model.ranker, _FOLD_HELD_PANEL["x"])
    held_gate = d135.winner_gate_logits(model, _FOLD_HELD_DATASET)
    gate_by_root = dict(
        zip(_FOLD_HELD_DATASET["root_order"], held_gate, strict=True)
    )
    metrics = d117.factorized_policy_metrics(
        _FOLD_HELD_PANEL, ranks, gate_by_root, offset
    )
    metrics["control_crop_rate"] = d123.control_crop_rate(_FOLD_HELD_PANEL)
    return {
        "held_block": _FOLD_HELD_BLOCK,
        "seed": ranker_seed,
        "ranker_seed": ranker_seed,
        "gate_seed": gate_seed,
        "model_hash": training_summary["model_hash"],
        "gate_offset": offset,
        "calibration": calibration,
        "training": training_summary,
        "held_structural_metrics": sequence_structural_metrics(
            model, _FOLD_HELD_DATASET
        ),
        "held_policy_metrics": metrics,
    }


def run_fold(descriptors: list[dict], held_block: int) -> list[dict]:
    global _FOLD_TRAINING, _FOLD_TASKS, _FOLD_HELD_PANEL
    global _FOLD_HELD_DATASET, _FOLD_HELD_BLOCK

    training_descriptors = [
        item for item in descriptors if int(item["block_id"]) != held_block
    ]
    _FOLD_TRAINING, _FOLD_TASKS = d134.load_training_data(training_descriptors)
    _FOLD_HELD_PANEL = d134.load_panel(descriptors[held_block])
    _FOLD_HELD_DATASET = d118.soft_value_dataset(_FOLD_HELD_PANEL)
    _FOLD_HELD_BLOCK = held_block
    context = multiprocessing.get_context("fork")
    try:
        with ProcessPoolExecutor(max_workers=WORKERS, mp_context=context) as executor:
            futures = [
                executor.submit(_seed_worker, ranker_seed, gate_seed)
                for ranker_seed, gate_seed in d137.SEED_PAIRS
            ]
            return sorted(
                (future.result() for future in futures), key=lambda row: row["seed"]
            )
    finally:
        _FOLD_TRAINING = None
        _FOLD_TASKS = None
        _FOLD_HELD_PANEL = None
        _FOLD_HELD_DATASET = None
        _FOLD_HELD_BLOCK = None
        gc.collect()


def run_selection() -> dict:
    lock = verify_lock()
    d140.verify_lock()
    d138.verify_lock()
    d135.verify_lock()
    d133_result, d139_result, descriptors = d140.corpus_descriptors()
    rows_by_seed = {ranker_seed: [] for ranker_seed, _ in d137.SEED_PAIRS}
    for held_block in range(BLOCKS):
        for row in run_fold(descriptors, held_block):
            rows_by_seed[row["seed"]].append(row)

    candidates = []
    for ranker_seed, gate_seed in d137.SEED_PAIRS:
        pooled = d140.aggregate_policy_metrics(rows_by_seed[ranker_seed])
        gates = d140.held_policy_gates(pooled)
        candidates.append(
            {
                "seed": ranker_seed,
                "ranker_seed": ranker_seed,
                "gate_seed": gate_seed,
                "folds": rows_by_seed[ranker_seed],
                "held_policy_metrics": pooled,
                "held_policy_gates": gates,
                "eligible": all(gates.values()),
            }
        )
    eligible = [candidate for candidate in candidates if candidate["eligible"]]
    selected = max(eligible, key=d137.selection_key) if eligible else None
    return {
        "schema": "troll-farm-d141a-task-balanced-best-stop-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d140_result": {
            "path": str(d140.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d140.OUTPUT),
            "decision": json.loads(d140.OUTPUT.read_text())["decision"],
        },
        "d133_result": {
            "path": str(d134.D133_RESULT.relative_to(ROOT)),
            "sha256": sha256(d134.D133_RESULT),
            "decision": d133_result["decision"],
        },
        "d139_result": {
            "path": str(d140.d139.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d140.d139.OUTPUT),
            "decision": d139_result["decision"],
        },
        "architecture": {
            "parameters": 6_786,
            "ranker_epochs": d119.EPOCHS,
            "gate_epochs": d137.GATE_EPOCHS,
            "soft_stop_temperature": d118.TEMPERATURE,
            "hard_stop_normalization": "equal-task-equal-positive-negative-class-mass",
            "extra_training_activity": d138.EXTRA_ACTIVITY,
            "blocks": BLOCKS,
            "seed_pairs": d137.SEED_PAIRS,
            "workers": WORKERS,
            "process_start_method": "fork",
            "read_only_parent_fold_context": True,
            "torch_threads_per_worker": 1,
        },
        "candidates": candidates,
        "eligible": len(eligible),
        "selected": selected,
        "decision": (
            "repeat_exact_selection"
            if selected is not None
            else "close_task_balanced_best_stop_on_transfer"
        ),
    }


def checkpoint_payload(
    model: d135.WinnerController, selected: dict, offset: float
) -> dict:
    return {
        "schema": "troll-farm-d141a-task-balanced-best-stop-checkpoint-v1",
        "parameters": 6_786,
        "ranker_epochs": d119.EPOCHS,
        "gate_epochs": d137.GATE_EPOCHS,
        "soft_stop_temperature": d118.TEMPERATURE,
        "hard_stop_normalization": "equal-task-equal-positive-negative-class-mass",
        "extra_training_activity": d138.EXTRA_ACTIVITY,
        "training_blocks": BLOCKS,
        "ranker_seed": selected["ranker_seed"],
        "gate_seed": selected["gate_seed"],
        "gate_offset": offset,
        "model_hash": d115.canonical_model_hash(model),
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def finalize() -> dict:
    lock = verify_lock()
    d140.verify_lock()
    d138.verify_lock()
    d135.verify_lock()
    exact_repeat = SELECTION_A.read_bytes() == SELECTION_B.read_bytes()
    selection = json.loads(SELECTION_A.read_text())
    selected = selection.get("selected") if exact_repeat else None
    full_fit = None
    veto = None
    checkpoint = None
    if selected is not None and selected["eligible"]:
        _, _, descriptors = d140.corpus_descriptors()
        training, training_tasks = d134.load_training_data(descriptors)
        model, training_summary = train_task_balanced_controller(
            training, selected["ranker_seed"], selected["gate_seed"]
        )
        base_target = training_summary["sequence"]["positive_stop_tasks"]
        target_active = d138.boosted_target(len(training_tasks), base_target)
        training_gate = d135.winner_gate_logits(model, training)
        offset, calibration = d137.count_calibrated_offset(
            training_tasks,
            training["root_order"],
            training_gate,
            target_active,
        )
        calibration["base_positive_stop_tasks"] = base_target
        calibration["extra_active_tasks"] = target_active - base_target
        full_fit = {
            "training": training_summary,
            "gate_offset": offset,
            "calibration": calibration,
        }
        d126_result = json.loads(d126.OUTPUT.read_text())
        validation = d114.panel(
            d126.VALIDATION_ARMS,
            d126.VALIDATION_BASELINES,
            d126.VALIDATION_START,
            d126.VALIDATION_MAPS,
            float(d126_result["fresh_validation"]["elapsed_seconds"]),
        )
        validation_dataset = d118.soft_value_dataset(validation)
        ranks = d115.model_logits(model.ranker, validation["x"])
        gate_values = d135.winner_gate_logits(model, validation_dataset)
        gate_by_root = dict(
            zip(validation_dataset["root_order"], gate_values, strict=True)
        )
        metrics = d117.factorized_policy_metrics(
            validation, ranks, gate_by_root, offset
        )
        gates = d125.validation_gates(metrics, d123.control_crop_rate(validation))
        veto = {
            "authority": "consumed-panel-veto-only",
            "structural_metrics": sequence_structural_metrics(
                model, validation_dataset
            ),
            "metrics": metrics,
            "gates": gates,
            "pass": all(gates.values()),
        }
        if veto["pass"]:
            torch.save(checkpoint_payload(model, selected, offset), CHECKPOINT)
            checkpoint = {
                "path": str(CHECKPOINT.relative_to(ROOT)),
                "sha256": sha256(CHECKPOINT),
                "bytes": CHECKPOINT.stat().st_size,
                "model_hash": training_summary["model_hash"],
            }
        elif CHECKPOINT.exists():
            raise RuntimeError("stale D141 checkpoint exists after veto failure")
        del training, training_tasks, validation, validation_dataset, model
        gc.collect()
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D141 checkpoint exists without repeated selection")

    passed = bool(exact_repeat and selected and veto and veto["pass"])
    result = {
        "schema": "troll-farm-d141a-task-balanced-best-stop-result-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "selection_repeat": {
            "byte_exact": exact_repeat,
            "a_sha256": sha256(SELECTION_A),
            "b_sha256": sha256(SELECTION_B),
            "selected": selected,
        },
        "full_fit": full_fit,
        "consumed_d126_veto": veto,
        "checkpoint": checkpoint,
        "full_pass": passed,
        "decision": (
            "open_final_untouched_9843800_9843815_validation"
            if passed
            else "close_task_balanced_best_stop_on_transfer"
            if selected is None
            else "close_d141_on_consumed_panel_veto"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("select-a", "select-b", "finalize"))
    args = parser.parse_args()
    if args.command == "finalize":
        finalize()
        return 0
    result = run_selection()
    target = SELECTION_A if args.command == "select-a" else SELECTION_B
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
