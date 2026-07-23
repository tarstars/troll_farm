#!/usr/bin/env python3
"""Select D142's dual gate with a deterministic exact-tie boundary."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import gc
import hashlib
import json
import math
import multiprocessing
from pathlib import Path

import numpy as np
import torch

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126
from cgauto import train_d134a_block_transfer_selected_soft_value_q6 as d134
from cgauto import train_d135a_winner_conditioned_action_gate_q6 as d135
from cgauto import train_d137a_task_sequence_best_stop_gate_q6 as d137
from cgauto import train_d138a_best_stop_plus3pp_calibration_q6 as d138
from cgauto import train_d140a_eight_block_best_stop_selection as d140
from cgauto import train_d141a_task_balanced_best_stop_selection as d141
from cgauto import train_d142a_shared_ranker_dual_gate_selection as d142


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d142b-tie-stable-dual-gate-selection-protocol-2026-07-22.md"
LOCK = BASE / "d142b-tie-stable-dual-gate-selection-lock.json"
SELECTION_A = BASE / "d142b-tie-stable-dual-gate-selection-a.json"
SELECTION_B = BASE / "d142b-tie-stable-dual-gate-selection-b.json"
CHECKPOINT = BASE / "d142b-tie-stable-dual-gate-selection.pt"
OUTPUT = BASE / "d142b-tie-stable-dual-gate-selection-result.json"

BLOCKS = d142.BLOCKS
WORKERS = d142.WORKERS
POLICY_OFFSET = 0.5

_FOLD_TRAINING = None
_FOLD_TASKS = None
_FOLD_HELD_PANEL = None
_FOLD_HELD_DATASET = None
_FOLD_HELD_BLOCK = None
_FOLD_EXPECTED_HASHES = None


def sha256(path: Path) -> str:
    return d117.sha256(path)


def verify_lock() -> dict:
    result = d117.verify_manifest(LOCK)
    if not result["pass"]:
        raise RuntimeError(f"D142b lock mismatch: {result['mismatches']!r}")
    return result


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"D142b task key contains non-JSON value {value!r}")


def stable_task_priority(task: tuple) -> str:
    encoded = json.dumps(
        task,
        separators=(",", ":"),
        ensure_ascii=True,
        default=_json_default,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def tie_stable_count_boundary(
    tasks: list,
    root_order: list,
    gate_values: np.ndarray,
    target_active_tasks: int,
) -> dict:
    if len(root_order) != len(gate_values):
        raise ValueError("D142b root order and gate values differ")
    maximum_by_task = {task: float("-inf") for task in tasks}
    for root, value in zip(root_order, gate_values, strict=True):
        task = root[0]
        if task not in maximum_by_task:
            raise ValueError(f"D142b encountered unknown root task {task!r}")
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("D142b gate logit is nonfinite")
        maximum_by_task[task] = max(maximum_by_task[task], value)
    if not 0 < target_active_tasks < len(tasks):
        raise ValueError("D142b target count must be interior")
    priorities = {task: stable_task_priority(task) for task in tasks}
    if len(set(priorities.values())) != len(priorities):
        raise RuntimeError("D142b task priority collision")
    ordered = sorted(
        (
            (maximum_by_task[task], priorities[task], task)
            for task in tasks
        ),
        reverse=True,
    )
    active_floor = ordered[target_active_tasks - 1]
    inactive_ceiling = ordered[target_active_tasks]
    if not math.isfinite(active_floor[0]) or not math.isfinite(inactive_ceiling[0]):
        raise ValueError("D142b has insufficient supported tasks")
    cutoff = active_floor[:2]
    achieved = sum(
        (maximum_by_task[task], priorities[task]) >= cutoff for task in tasks
    )
    if achieved != target_active_tasks:
        raise RuntimeError("D142b tie-stable boundary missed its target count")
    return {
        "authority": "training-selected-winner-positive-task-count",
        "representation": "inclusive-logit-stable-task-sha256-pair",
        "priority": "sha256-compact-json-task-key",
        "tasks": len(tasks),
        "target_active_tasks": target_active_tasks,
        "achieved_active_tasks": achieved,
        "target_activity": target_active_tasks / len(tasks),
        "achieved_activity": achieved / len(tasks),
        "active_floor_logit": active_floor[0],
        "active_floor_priority": active_floor[1],
        "inactive_ceiling_logit": inactive_ceiling[0],
        "inactive_ceiling_priority": inactive_ceiling[1],
        "numeric_boundary_tied": active_floor[0] == inactive_ceiling[0],
        "cutoff_logit": cutoff[0],
        "cutoff_priority": cutoff[1],
        "policy_gate_offset": POLICY_OFFSET,
    }


def binary_gate_by_root(
    root_order: list,
    gate_values: np.ndarray,
    calibration: dict,
) -> dict:
    if len(root_order) != len(gate_values):
        raise ValueError("D142b root order and gate values differ")
    cutoff = (
        float(calibration["cutoff_logit"]),
        str(calibration["cutoff_priority"]),
    )
    result = {}
    for root, value in zip(root_order, gate_values, strict=True):
        pair = (float(value), stable_task_priority(root[0]))
        result[root] = 1.0 if pair >= cutoff else 0.0
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
            _FOLD_EXPECTED_HASHES,
        )
    ):
        raise RuntimeError("D142b fork worker lacks its read-only fold context")
    model, training_summary = d142.train_dual_controller(
        _FOLD_TRAINING,
        ranker_seed,
        gate_seed,
        _FOLD_EXPECTED_HASHES[ranker_seed],
    )
    base_target = training_summary["sequence"]["positive_stop_tasks"]
    target_active = d138.boosted_target(len(_FOLD_TASKS), base_target)
    training_gate = d142.dual_gate_logits(model, _FOLD_TRAINING)
    calibration = tie_stable_count_boundary(
        _FOLD_TASKS,
        _FOLD_TRAINING["root_order"],
        training_gate,
        target_active,
    )
    calibration["base_positive_stop_tasks"] = base_target
    calibration["extra_active_tasks"] = target_active - base_target
    ranks = d115.model_logits(model.ranker, _FOLD_HELD_PANEL["x"])
    held_gate = d142.dual_gate_logits(model, _FOLD_HELD_DATASET)
    gate_by_root = binary_gate_by_root(
        _FOLD_HELD_DATASET["root_order"], held_gate, calibration
    )
    metrics = d117.factorized_policy_metrics(
        _FOLD_HELD_PANEL, ranks, gate_by_root, POLICY_OFFSET
    )
    metrics["control_crop_rate"] = d123.control_crop_rate(_FOLD_HELD_PANEL)
    return {
        "held_block": _FOLD_HELD_BLOCK,
        "seed": ranker_seed,
        "ranker_seed": ranker_seed,
        "gate_seed": gate_seed,
        "model_hash": training_summary["model_hash"],
        "gate_offset": POLICY_OFFSET,
        "calibration": calibration,
        "training": training_summary,
        "held_structural_metrics": d142.dual_structural_metrics(
            model, _FOLD_HELD_DATASET
        ),
        "held_policy_metrics": metrics,
    }


def run_fold(descriptors: list[dict], held_block: int) -> list[dict]:
    global _FOLD_TRAINING, _FOLD_TASKS, _FOLD_HELD_PANEL
    global _FOLD_HELD_DATASET, _FOLD_HELD_BLOCK, _FOLD_EXPECTED_HASHES

    training_descriptors = [
        item for item in descriptors if int(item["block_id"]) != held_block
    ]
    _FOLD_TRAINING, _FOLD_TASKS = d134.load_training_data(training_descriptors)
    _FOLD_HELD_PANEL = d134.load_panel(descriptors[held_block])
    _FOLD_HELD_DATASET = d118.soft_value_dataset(_FOLD_HELD_PANEL)
    _FOLD_HELD_BLOCK = held_block
    matrix = d142.expected_component_hashes()
    _FOLD_EXPECTED_HASHES = {
        seed: matrix[(held_block, seed)] for seed, _ in d137.SEED_PAIRS
    }
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
        _FOLD_EXPECTED_HASHES = None
        gc.collect()


def run_selection() -> dict:
    lock = verify_lock()
    d142.verify_lock()
    d141.verify_lock()
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
        "schema": "troll-farm-d142b-tie-stable-dual-gate-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d142a_preflight": {
            "lock": str(d142.LOCK.relative_to(ROOT)),
            "lock_sha256": sha256(d142.LOCK),
            "selection_artifact_emitted": False,
            "failure": "gate quantile boundary is tied",
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
            "parameters": d142.PARAMETERS,
            "shared_ranker": True,
            "gates": 2,
            "gate_logit_composition": "arithmetic-mean-50-50",
            "activity_boundary": "inclusive-logit-stable-task-sha256-pair",
            "policy_gate_offset": POLICY_OFFSET,
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
            else "close_tie_stable_dual_gate_on_transfer"
        ),
    }


def checkpoint_payload(
    model: d142.DualGateController, selected: dict, calibration: dict
) -> dict:
    return {
        "schema": "troll-farm-d142b-tie-stable-dual-gate-checkpoint-v1",
        "parameters": d142.PARAMETERS,
        "shared_ranker": True,
        "gate_logit_composition": "arithmetic-mean-50-50",
        "activity_boundary": calibration,
        "policy_gate_offset": POLICY_OFFSET,
        "extra_training_activity": d138.EXTRA_ACTIVITY,
        "training_blocks": BLOCKS,
        "ranker_seed": selected["ranker_seed"],
        "gate_seed": selected["gate_seed"],
        "model_hash": d115.canonical_model_hash(model),
        "component_hashes": {
            "root_weighted": d142.component_hash(model.ranker, model.root_gate),
            "task_balanced": d142.component_hash(model.ranker, model.task_gate),
        },
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def finalize() -> dict:
    lock = verify_lock()
    d142.verify_lock()
    d141.verify_lock()
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
        model, training_summary = d142.train_dual_controller(
            training, selected["ranker_seed"], selected["gate_seed"]
        )
        base_target = training_summary["sequence"]["positive_stop_tasks"]
        target_active = d138.boosted_target(len(training_tasks), base_target)
        training_gate = d142.dual_gate_logits(model, training)
        calibration = tie_stable_count_boundary(
            training_tasks,
            training["root_order"],
            training_gate,
            target_active,
        )
        calibration["base_positive_stop_tasks"] = base_target
        calibration["extra_active_tasks"] = target_active - base_target
        full_fit = {"training": training_summary, "calibration": calibration}
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
        gate_values = d142.dual_gate_logits(model, validation_dataset)
        gate_by_root = binary_gate_by_root(
            validation_dataset["root_order"], gate_values, calibration
        )
        metrics = d117.factorized_policy_metrics(
            validation, ranks, gate_by_root, POLICY_OFFSET
        )
        gates = d125.validation_gates(metrics, d123.control_crop_rate(validation))
        veto = {
            "authority": "consumed-panel-veto-only",
            "structural_metrics": d142.dual_structural_metrics(
                model, validation_dataset
            ),
            "metrics": metrics,
            "gates": gates,
            "pass": all(gates.values()),
        }
        if veto["pass"]:
            torch.save(checkpoint_payload(model, selected, calibration), CHECKPOINT)
            checkpoint = {
                "path": str(CHECKPOINT.relative_to(ROOT)),
                "sha256": sha256(CHECKPOINT),
                "bytes": CHECKPOINT.stat().st_size,
                "model_hash": training_summary["model_hash"],
            }
        elif CHECKPOINT.exists():
            raise RuntimeError("stale D142b checkpoint exists after veto failure")
        del training, training_tasks, validation, validation_dataset, model
        gc.collect()
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D142b checkpoint exists without repeated selection")

    passed = bool(exact_repeat and selected and veto and veto["pass"])
    result = {
        "schema": "troll-farm-d142b-tie-stable-dual-gate-result-v1",
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
            else "close_tie_stable_dual_gate_on_transfer"
            if selected is None
            else "close_d142b_on_consumed_panel_veto"
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
