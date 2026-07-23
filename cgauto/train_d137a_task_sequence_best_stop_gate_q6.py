#!/usr/bin/env python3
"""Train D137a's task-sequence best-stop gate on D133 blocks."""

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
from cgauto import analyze_d136a_d135_all_pair_transfer as d136


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d137a-task-sequence-best-stop-gate-q6-protocol-2026-07-22.md"
LOCK = BASE / "d137a-task-sequence-best-stop-gate-q6-lock.json"
SELECTION_A = BASE / "d137a-task-sequence-best-stop-gate-q6-selection-a.json"
SELECTION_B = BASE / "d137a-task-sequence-best-stop-gate-q6-selection-b.json"
CHECKPOINT = BASE / "d137a-task-sequence-best-stop-gate-q6.pt"
OUTPUT = BASE / "d137a-task-sequence-best-stop-gate-q6-result.json"

SEED_PAIRS = ((13_401, 13_701), (13_402, 13_702), (13_403, 13_703), (13_404, 13_704))
BLOCKS = 4
GATE_EPOCHS = 80
TASK_BATCH_SIZE = 128
WORKERS = 4


def sha256(path: Path) -> str:
    return d117.sha256(path)


def verify_lock() -> dict:
    result = d117.verify_manifest(LOCK)
    if not result["pass"]:
        raise RuntimeError(f"D137 lock mismatch: {result['mismatches']!r}")
    return result


def sequence_dataset(
    ranker: d115.CompactActClassifier, dataset: dict
) -> dict:
    root_features, _, selected_values, _ = d135.winner_context(ranker, dataset)
    task_order = list(dict.fromkeys(root[0] for root in dataset["root_order"]))
    indices_by_task = {
        task: [
            index
            for index, root in enumerate(dataset["root_order"])
            if root[0] == task
        ]
        for task in task_order
    }
    maximum_roots = max(len(indices) for indices in indices_by_task.values())
    tasks = len(task_order)
    features = torch.zeros(
        (tasks, maximum_roots, d135.GATE_INPUTS), dtype=torch.float32
    )
    values = torch.full(
        (tasks, maximum_roots), float("-inf"), dtype=torch.float32
    )
    valid = torch.zeros((tasks, maximum_roots), dtype=torch.bool)
    hard_stop_targets = torch.zeros((tasks, maximum_roots), dtype=torch.bool)
    root_positions = torch.full(
        (tasks, maximum_roots), -1, dtype=torch.int64
    )
    positive_tasks = 0
    for task_index, task in enumerate(task_order):
        indices = indices_by_task[task]
        count = len(indices)
        tensor_indices = torch.tensor(indices, dtype=torch.int64)
        features[task_index, :count] = root_features[tensor_indices]
        values[task_index, :count] = selected_values[tensor_indices]
        valid[task_index, :count] = True
        root_positions[task_index, :count] = tensor_indices
        best = int(values[task_index, :count].argmax())
        if float(values[task_index, best]) > 0.0:
            hard_stop_targets[task_index, best] = True
            positive_tasks += 1

    augmented_values = torch.cat((values, torch.zeros((tasks, 1))), dim=1)
    augmented_valid = torch.cat((valid, torch.ones((tasks, 1), dtype=torch.bool)), dim=1)
    maximum = augmented_values.max(dim=1, keepdim=True).values
    soft_stop_targets = torch.softmax(
        (augmented_values - maximum) / d118.TEMPERATURE, dim=1
    )
    if not bool(torch.isfinite(soft_stop_targets).all()):
        raise RuntimeError("D137 soft stop targets are nonfinite")
    if not torch.allclose(
        soft_stop_targets.sum(dim=1), torch.ones(tasks), atol=1.0e-6
    ):
        raise RuntimeError("D137 soft stop targets lost unit mass")
    return {
        "features": features,
        "values": values,
        "valid": valid,
        "augmented_valid": augmented_valid,
        "soft_stop_targets": soft_stop_targets,
        "hard_stop_targets": hard_stop_targets,
        "root_positions": root_positions,
        "task_order": task_order,
        "summary": {
            "supported_tasks": tasks,
            "positive_stop_tasks": positive_tasks,
            "positive_stop_task_rate": positive_tasks / tasks,
            "roots": int(valid.sum()),
            "maximum_roots_per_task": maximum_roots,
            "hard_positive_roots": int(hard_stop_targets.sum()),
            "mean_soft_stop_entropy": float(
                -(
                    soft_stop_targets
                    * soft_stop_targets.clamp_min(1.0e-30).log()
                ).sum(dim=1).mean()
            ),
        },
    }


def sequence_losses(
    model: d135.WinnerController, sequence: dict, indices: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    logits = model.gate(sequence["features"][indices])
    valid = sequence["valid"][indices]
    masked = logits.masked_fill(~valid, float("-inf"))
    augmented = torch.cat((masked, torch.zeros((len(indices), 1))), dim=1)
    soft_loss = d118.soft_cross_entropy(
        augmented,
        sequence["soft_stop_targets"][indices],
        sequence["augmented_valid"][indices],
    )
    hard_loss = functional.binary_cross_entropy_with_logits(
        logits[valid], sequence["hard_stop_targets"][indices][valid].float()
    )
    return soft_loss, hard_loss


def train_sequence_controller(
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
        raise RuntimeError("D137 parameter budget changed")
    sequence = sequence_dataset(model.ranker, dataset)
    optimizer = torch.optim.Adam(
        model.gate.parameters(),
        lr=d118.LEARNING_RATE,
        weight_decay=d118.WEIGHT_DECAY,
    )
    generator = np.random.Generator(np.random.PCG64(gate_seed))
    epoch_losses = []
    model.gate.train()
    for _ in range(GATE_EPOCHS):
        order = generator.permutation(len(sequence["task_order"]))
        soft_sum = 0.0
        hard_sum = 0.0
        tasks_seen = 0
        for start in range(0, len(order), TASK_BATCH_SIZE):
            indices = torch.from_numpy(order[start : start + TASK_BATCH_SIZE])
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
                "hard_stop": hard_sum / tasks_seen,
                "total": (soft_sum + hard_sum) / tasks_seen,
            }
        )
    model.eval()
    all_indices = torch.arange(len(sequence["task_order"]))
    with torch.no_grad():
        final_soft, final_hard = sequence_losses(model, sequence, all_indices)
    ranker_hash_after = d115.canonical_model_hash(model.ranker)
    if ranker_hash_before != ranker_hash_after:
        raise RuntimeError("D137 sequence training changed the frozen ranker")
    return model, {
        "ranker_seed": ranker_seed,
        "gate_seed": gate_seed,
        "ranker_hash": ranker_hash_after,
        "model_hash": d115.canonical_model_hash(model),
        "parameters": d115.parameter_count(model),
        "ranker_training": ranker_training,
        "gate_epochs": GATE_EPOCHS,
        "task_batch_size": TASK_BATCH_SIZE,
        "gate_learning_rate": d118.LEARNING_RATE,
        "gate_weight_decay": d118.WEIGHT_DECAY,
        "gate_cpu_threads": 1,
        "sequence": sequence["summary"],
        "first_epoch_loss": epoch_losses[0],
        "last_epoch_loss": epoch_losses[-1],
        "final_soft_stop_cross_entropy": float(final_soft),
        "final_hard_stop_binary_cross_entropy": float(final_hard),
    }


def sequence_structural_metrics(
    model: d135.WinnerController, dataset: dict
) -> dict:
    sequence = sequence_dataset(model.ranker, dataset)
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
            "hard_stop_binary_cross_entropy": float(hard_loss),
        }
    )
    return result


def count_calibrated_offset(
    tasks: list,
    root_order: list,
    gate_values: np.ndarray,
    target_active_tasks: int,
) -> tuple[float, dict]:
    offset, calibration = d125.activity_calibrated_offset(
        tasks,
        root_order,
        gate_values,
        target_activity=target_active_tasks / len(tasks),
    )
    if calibration["target_active_tasks"] != target_active_tasks:
        raise RuntimeError("D137 count calibration changed its target")
    calibration["authority"] = "training-selected-winner-positive-task-count"
    return offset, calibration


def fold_worker(
    held_block: int,
    training_descriptors: list[dict],
    held_descriptor: dict,
    ranker_seed: int,
    gate_seed: int,
) -> dict:
    training, training_tasks = d134.load_training_data(training_descriptors)
    held_panel = d134.load_panel(held_descriptor)
    held_dataset = d118.soft_value_dataset(held_panel)
    model, training_summary = train_sequence_controller(
        training, ranker_seed, gate_seed
    )
    training_gate = d135.winner_gate_logits(model, training)
    target_active = training_summary["sequence"]["positive_stop_tasks"]
    offset, calibration = count_calibrated_offset(
        training_tasks, training["root_order"], training_gate, target_active
    )
    ranks = d115.model_logits(model.ranker, held_panel["x"])
    held_gate = d135.winner_gate_logits(model, held_dataset)
    gate_by_root = dict(zip(held_dataset["root_order"], held_gate, strict=True))
    metrics = d117.factorized_policy_metrics(
        held_panel, ranks, gate_by_root, offset
    )
    metrics["control_crop_rate"] = d123.control_crop_rate(held_panel)
    result = {
        "held_block": held_block,
        "seed": ranker_seed,
        "ranker_seed": ranker_seed,
        "gate_seed": gate_seed,
        "model_hash": training_summary["model_hash"],
        "gate_offset": offset,
        "calibration": calibration,
        "training": training_summary,
        "held_structural_metrics": sequence_structural_metrics(
            model, held_dataset
        ),
        "held_policy_metrics": metrics,
    }
    del training, training_tasks, held_panel, held_dataset, model
    gc.collect()
    return result


def aggregate_policy_metrics(folds: list[dict]) -> dict:
    ordered = sorted(folds, key=lambda row: int(row["held_block"]))
    metrics = d134.aggregate_policy_metrics(
        [row["held_policy_metrics"] for row in ordered]
    )
    metrics["block_intervention_rate"] = {
        str(row["held_block"]): row["held_policy_metrics"]["intervention_rate"]
        for row in ordered
    }
    return metrics


def held_policy_gates(metrics: dict) -> dict[str, bool]:
    gates = d134.held_policy_gates(metrics)
    gates["every_block_activity_10_to_85pct"] = all(
        0.10 <= value <= 0.85
        for value in metrics["block_intervention_rate"].values()
    )
    return gates


def selection_key(candidate: dict) -> tuple:
    metrics = candidate["held_policy_metrics"]
    return (
        metrics["worst_family"],
        min(metrics["block_mean_margin_delta"].values()),
        metrics["mean_margin_delta"],
        metrics["strict_improvement_rate"],
        -metrics["intervention_rate"],
        -candidate["ranker_seed"],
    )


def run_selection() -> dict:
    lock = verify_lock()
    d135.verify_lock()
    d133_result, descriptors = d134.d133_blocks()
    rows_by_seed = {ranker_seed: [] for ranker_seed, _ in SEED_PAIRS}
    context = multiprocessing.get_context("spawn")
    for held_block in range(BLOCKS):
        training_descriptors = [
            item for item in descriptors if int(item["block_id"]) != held_block
        ]
        with ProcessPoolExecutor(max_workers=WORKERS, mp_context=context) as executor:
            futures = [
                executor.submit(
                    fold_worker,
                    held_block,
                    training_descriptors,
                    descriptors[held_block],
                    ranker_seed,
                    gate_seed,
                )
                for ranker_seed, gate_seed in SEED_PAIRS
            ]
            rows = sorted(
                (future.result() for future in futures), key=lambda row: row["seed"]
            )
        for row in rows:
            rows_by_seed[row["seed"]].append(row)

    candidates = []
    for ranker_seed, gate_seed in SEED_PAIRS:
        pooled = aggregate_policy_metrics(rows_by_seed[ranker_seed])
        gates = held_policy_gates(pooled)
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
    selected = max(eligible, key=selection_key) if eligible else None
    return {
        "schema": "troll-farm-d137a-task-sequence-best-stop-gate-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d133_result": {
            "path": str(d134.D133_RESULT.relative_to(ROOT)),
            "sha256": sha256(d134.D133_RESULT),
            "decision": d133_result["decision"],
        },
        "d136_result": {
            "path": str(d136.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d136.OUTPUT),
            "decision": json.loads(d136.OUTPUT.read_text())["decision"],
        },
        "architecture": {
            "parameters": 6_786,
            "ranker_epochs": d119.EPOCHS,
            "gate_epochs": GATE_EPOCHS,
            "task_batch_size": TASK_BATCH_SIZE,
            "soft_stop_temperature": d118.TEMPERATURE,
            "seed_pairs": SEED_PAIRS,
            "workers": WORKERS,
            "torch_threads_per_worker": 1,
        },
        "candidates": candidates,
        "eligible": len(eligible),
        "selected": selected,
        "decision": (
            "repeat_exact_selection"
            if selected is not None
            else "close_task_sequence_best_stop_gate_on_block_transfer"
        ),
    }


def checkpoint_payload(
    model: d135.WinnerController, selected: dict, offset: float
) -> dict:
    return {
        "schema": "troll-farm-d137a-task-sequence-best-stop-gate-q6-checkpoint-v1",
        "parameters": 6_786,
        "ranker_epochs": d119.EPOCHS,
        "gate_epochs": GATE_EPOCHS,
        "soft_stop_temperature": d118.TEMPERATURE,
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
    d135.verify_lock()
    exact_repeat = SELECTION_A.read_bytes() == SELECTION_B.read_bytes()
    selection = json.loads(SELECTION_A.read_text())
    selected = selection.get("selected") if exact_repeat else None
    full_fit = None
    veto = None
    checkpoint = None
    if selected is not None and selected["eligible"]:
        _, descriptors = d134.d133_blocks()
        training, training_tasks = d134.load_training_data(descriptors)
        model, training_summary = train_sequence_controller(
            training, selected["ranker_seed"], selected["gate_seed"]
        )
        training_gate = d135.winner_gate_logits(model, training)
        target_active = training_summary["sequence"]["positive_stop_tasks"]
        offset, calibration = count_calibrated_offset(
            training_tasks,
            training["root_order"],
            training_gate,
            target_active,
        )
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
        gates = d125.validation_gates(
            metrics, d123.control_crop_rate(validation)
        )
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
            raise RuntimeError("stale D137 checkpoint exists after veto failure")
        del training, training_tasks, validation, validation_dataset, model
        gc.collect()
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D137 checkpoint exists without repeated selection")

    passed = bool(exact_repeat and selected and veto and veto["pass"])
    result = {
        "schema": "troll-farm-d137a-task-sequence-best-stop-gate-q6-v1",
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
            else "close_task_sequence_best_stop_gate_on_block_transfer"
            if selected is None
            else "close_d137_on_consumed_panel_veto"
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
