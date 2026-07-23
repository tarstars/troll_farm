#!/usr/bin/env python3
"""Select D138's unchanged controller on eight independent q6 blocks."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import gc
import json
import multiprocessing
from pathlib import Path

import torch

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
from cgauto import yt_d139_q6_second_independent_corpus as d139


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d140a-eight-block-best-stop-selection-protocol-2026-07-22.md"
LOCK = BASE / "d140a-eight-block-best-stop-selection-lock.json"
SELECTION_A = BASE / "d140a-eight-block-best-stop-selection-a.json"
SELECTION_B = BASE / "d140a-eight-block-best-stop-selection-b.json"
CHECKPOINT = BASE / "d140a-eight-block-best-stop-selection.pt"
OUTPUT = BASE / "d140a-eight-block-best-stop-selection-result.json"

BLOCKS = 8
WORKERS = 4

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
        raise RuntimeError(f"D140 lock mismatch: {result['mismatches']!r}")
    return result


def validate_descriptors(descriptors: list[dict]) -> list[dict]:
    ordered = sorted(descriptors, key=lambda item: int(item["block_id"]))
    if [int(item["block_id"]) for item in ordered] != list(range(BLOCKS)):
        raise RuntimeError("D140 requires global block ids 0 through 7")
    ranges = [
        (int(item["start_seed"]), int(item["start_seed"]) + int(item["maps"]) - 1)
        for item in ordered
    ]
    if any(left[1] >= right[0] for left, right in zip(ranges, ranges[1:])):
        raise RuntimeError("D140 block seed ranges overlap")
    if any(int(item["maps"]) != 16 for item in ordered):
        raise RuntimeError("D140 requires eight 16-map blocks")
    return ordered


def corpus_descriptors() -> tuple[dict, dict, list[dict]]:
    d133_result, old_blocks = d134.d133_blocks()
    d139_result = json.loads(d139.OUTPUT.read_text())
    if not d139_result.get("full_pass"):
        raise RuntimeError("D139 did not authorize eight-block selection")
    if d139_result.get("decision") != "open_frozen_eight_block_learner_selection":
        raise RuntimeError("D139 decision does not open D140")
    return d133_result, d139_result, validate_descriptors(
        list(old_blocks) + list(d139_result["blocks"])
    )


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
        raise RuntimeError("D140 fork worker lacks its read-only fold context")
    model, training_summary = d137.train_sequence_controller(
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
        "held_structural_metrics": d137.sequence_structural_metrics(
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


def run_selection() -> dict:
    lock = verify_lock()
    d138.verify_lock()
    d135.verify_lock()
    d133_result, d139_result, descriptors = corpus_descriptors()
    rows_by_seed = {ranker_seed: [] for ranker_seed, _ in d137.SEED_PAIRS}
    for held_block in range(BLOCKS):
        for row in run_fold(descriptors, held_block):
            rows_by_seed[row["seed"]].append(row)

    candidates = []
    for ranker_seed, gate_seed in d137.SEED_PAIRS:
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
    selected = max(eligible, key=d137.selection_key) if eligible else None
    return {
        "schema": "troll-farm-d140a-eight-block-best-stop-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d133_result": {
            "path": str(d134.D133_RESULT.relative_to(ROOT)),
            "sha256": sha256(d134.D133_RESULT),
            "decision": d133_result["decision"],
        },
        "d139_result": {
            "path": str(d139.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d139.OUTPUT),
            "decision": d139_result["decision"],
        },
        "architecture": {
            "parameters": 6_786,
            "ranker_epochs": d119.EPOCHS,
            "gate_epochs": d137.GATE_EPOCHS,
            "soft_stop_temperature": d118.TEMPERATURE,
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
            else "close_eight_block_best_stop_on_transfer"
        ),
    }


def checkpoint_payload(
    model: d135.WinnerController, selected: dict, offset: float
) -> dict:
    return {
        "schema": "troll-farm-d140a-eight-block-best-stop-selection-checkpoint-v1",
        "parameters": 6_786,
        "ranker_epochs": d119.EPOCHS,
        "gate_epochs": d137.GATE_EPOCHS,
        "soft_stop_temperature": d118.TEMPERATURE,
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
    d138.verify_lock()
    d135.verify_lock()
    exact_repeat = SELECTION_A.read_bytes() == SELECTION_B.read_bytes()
    selection = json.loads(SELECTION_A.read_text())
    selected = selection.get("selected") if exact_repeat else None
    full_fit = None
    veto = None
    checkpoint = None
    if selected is not None and selected["eligible"]:
        _, _, descriptors = corpus_descriptors()
        training, training_tasks = d134.load_training_data(descriptors)
        model, training_summary = d137.train_sequence_controller(
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
        gates = d125.validation_gates(
            metrics, d123.control_crop_rate(validation)
        )
        veto = {
            "authority": "consumed-panel-veto-only",
            "structural_metrics": d137.sequence_structural_metrics(
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
            raise RuntimeError("stale D140 checkpoint exists after veto failure")
        del training, training_tasks, validation, validation_dataset, model
        gc.collect()
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D140 checkpoint exists without repeated selection")

    passed = bool(exact_repeat and selected and veto and veto["pass"])
    result = {
        "schema": "troll-farm-d140a-eight-block-best-stop-selection-result-v1",
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
            else "close_eight_block_best_stop_on_transfer"
            if selected is None
            else "close_d140_on_consumed_panel_veto"
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
