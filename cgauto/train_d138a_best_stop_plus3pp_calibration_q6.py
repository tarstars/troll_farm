#!/usr/bin/env python3
"""Run D137's best-stop gate with a fixed +3pp training calibration."""

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


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d138a-best-stop-plus3pp-calibration-q6-protocol-2026-07-22.md"
LOCK = BASE / "d138a-best-stop-plus3pp-calibration-q6-lock.json"
SELECTION_A = BASE / "d138a-best-stop-plus3pp-calibration-q6-selection-a.json"
SELECTION_B = BASE / "d138a-best-stop-plus3pp-calibration-q6-selection-b.json"
CHECKPOINT = BASE / "d138a-best-stop-plus3pp-calibration-q6.pt"
OUTPUT = BASE / "d138a-best-stop-plus3pp-calibration-q6-result.json"

EXTRA_ACTIVITY = 0.03


def sha256(path: Path) -> str:
    return d117.sha256(path)


def verify_lock() -> dict:
    result = d117.verify_manifest(LOCK)
    if not result["pass"]:
        raise RuntimeError(f"D138 lock mismatch: {result['mismatches']!r}")
    return result


def boosted_target(tasks: int, positive_stop_tasks: int) -> int:
    target = positive_stop_tasks + round(EXTRA_ACTIVITY * tasks)
    if not 0 < target < tasks:
        raise ValueError("D138 boosted activity is not an interior count")
    return target


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
    model, training_summary = d137.train_sequence_controller(
        training, ranker_seed, gate_seed
    )
    base_target = training_summary["sequence"]["positive_stop_tasks"]
    target_active = boosted_target(len(training_tasks), base_target)
    training_gate = d135.winner_gate_logits(model, training)
    offset, calibration = d137.count_calibrated_offset(
        training_tasks, training["root_order"], training_gate, target_active
    )
    calibration["base_positive_stop_tasks"] = base_target
    calibration["extra_active_tasks"] = target_active - base_target
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
        "held_structural_metrics": d137.sequence_structural_metrics(
            model, held_dataset
        ),
        "held_policy_metrics": metrics,
    }
    del training, training_tasks, held_panel, held_dataset, model
    gc.collect()
    return result


def run_selection() -> dict:
    lock = verify_lock()
    d137.verify_lock()
    d135.verify_lock()
    d133_result, descriptors = d134.d133_blocks()
    rows_by_seed = {ranker_seed: [] for ranker_seed, _ in d137.SEED_PAIRS}
    context = multiprocessing.get_context("spawn")
    for held_block in range(d137.BLOCKS):
        training_descriptors = [
            item for item in descriptors if int(item["block_id"]) != held_block
        ]
        with ProcessPoolExecutor(
            max_workers=d137.WORKERS, mp_context=context
        ) as executor:
            futures = [
                executor.submit(
                    fold_worker,
                    held_block,
                    training_descriptors,
                    descriptors[held_block],
                    ranker_seed,
                    gate_seed,
                )
                for ranker_seed, gate_seed in d137.SEED_PAIRS
            ]
            rows = sorted(
                (future.result() for future in futures), key=lambda row: row["seed"]
            )
        for row in rows:
            rows_by_seed[row["seed"]].append(row)

    candidates = []
    for ranker_seed, gate_seed in d137.SEED_PAIRS:
        pooled = d137.aggregate_policy_metrics(rows_by_seed[ranker_seed])
        gates = d137.held_policy_gates(pooled)
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
        "schema": "troll-farm-d138a-best-stop-plus3pp-calibration-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d133_result": {
            "path": str(d134.D133_RESULT.relative_to(ROOT)),
            "sha256": sha256(d134.D133_RESULT),
            "decision": d133_result["decision"],
        },
        "d137_result": {
            "path": str(d137.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d137.OUTPUT),
            "decision": json.loads(d137.OUTPUT.read_text())["decision"],
        },
        "architecture": {
            "parameters": 6_786,
            "ranker_epochs": d119.EPOCHS,
            "gate_epochs": d137.GATE_EPOCHS,
            "soft_stop_temperature": d118.TEMPERATURE,
            "extra_training_activity": EXTRA_ACTIVITY,
            "seed_pairs": d137.SEED_PAIRS,
            "workers": d137.WORKERS,
            "torch_threads_per_worker": 1,
        },
        "candidates": candidates,
        "eligible": len(eligible),
        "selected": selected,
        "decision": (
            "repeat_exact_selection"
            if selected is not None
            else "close_plus3pp_calibration_on_block_transfer"
        ),
    }


def checkpoint_payload(
    model: d135.WinnerController, selected: dict, offset: float
) -> dict:
    return {
        "schema": "troll-farm-d138a-best-stop-plus3pp-calibration-q6-checkpoint-v1",
        "parameters": 6_786,
        "ranker_epochs": d119.EPOCHS,
        "gate_epochs": d137.GATE_EPOCHS,
        "soft_stop_temperature": d118.TEMPERATURE,
        "extra_training_activity": EXTRA_ACTIVITY,
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
    d137.verify_lock()
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
        model, training_summary = d137.train_sequence_controller(
            training, selected["ranker_seed"], selected["gate_seed"]
        )
        base_target = training_summary["sequence"]["positive_stop_tasks"]
        target_active = boosted_target(len(training_tasks), base_target)
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
            raise RuntimeError("stale D138 checkpoint exists after veto failure")
        del training, training_tasks, validation, validation_dataset, model
        gc.collect()
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D138 checkpoint exists without repeated selection")

    passed = bool(exact_repeat and selected and veto and veto["pass"])
    result = {
        "schema": "troll-farm-d138a-best-stop-plus3pp-calibration-q6-v1",
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
            else "close_plus3pp_calibration_on_block_transfer"
            if selected is None
            else "close_d138_on_consumed_panel_veto"
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
