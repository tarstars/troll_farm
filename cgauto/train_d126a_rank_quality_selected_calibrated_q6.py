#!/usr/bin/env python3
"""Select D125-calibrated models by proposal quality and validate one freshly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d126a-rank-quality-selected-calibrated-q6-protocol-2026-07-22.md"
FIT_LOCK = BASE / "d126a-rank-quality-selected-calibrated-q6-fit-lock.json"
FIT_OUTPUT = BASE / "d126a-rank-quality-selected-calibrated-q6-fit-result.json"
SELECTION_LOCK = BASE / "d126a-rank-quality-selected-calibrated-q6-selection-lock.json"
VALIDATION_ARMS = BASE / "d126a-q6-validation-arms-9843780-9843795.tsv"
VALIDATION_BASELINES = BASE / "d126a-q6-validation-baselines-9843780-9843795.tsv"
CHECKPOINT = BASE / "d126a-rank-quality-selected-calibrated-q6.pt"
OUTPUT = BASE / "d126a-rank-quality-selected-calibrated-q6-result.json"

VALIDATION_START = 9_843_780
VALIDATION_MAPS = 16
VALIDATION_TASKS = 256


def rank_quality_key(candidate: dict, summary_by_seed: dict[int, dict]) -> tuple:
    summary = summary_by_seed[candidate["seed"]]
    return (
        summary["train_mean_proposal_regret"],
        -summary["train_within_10_rate"],
        candidate["seed"],
    )


def fit_only() -> dict:
    lock = d117.verify_manifest(FIT_LOCK)
    frozen_fit = json.loads(d119.FIT_OUTPUT.read_text())
    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    dataset, training, _, models = d119.train_models_and_grid(train)
    expected_hashes = {
        item["seed"]: item["model_hash"] for item in frozen_fit["training"]
    }
    actual_hashes = {item["seed"]: item["model_hash"] for item in training}
    if expected_hashes != actual_hashes:
        raise RuntimeError("D126 did not reproduce the frozen D119 models")

    candidates = [
        d125.calibrated_candidate(
            train, dataset, models[item["seed"]], item, index
        )
        for index, item in enumerate(training)
    ]
    eligible = [item for item in candidates if item["fit_eligible"]]
    summary_by_seed = {item["seed"]: item for item in training}
    selected = (
        min(eligible, key=lambda item: rank_quality_key(item, summary_by_seed))
        if eligible
        else None
    )
    result = {
        "schema": "troll-farm-d126a-rank-quality-selected-calibrated-q6-fit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "fit_lock": lock,
        "isolated_change": "select eligible calibrated seed by proposal regret",
        "selection_key": [
            "minimum train mean proposal regret",
            "maximum train within-ten rate",
            "minimum fixed seed",
        ],
        "models_reproduced": expected_hashes == actual_hashes,
        "training": training,
        "candidates": candidates,
        "eligible": len(eligible),
        "selected": selected,
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (
                d119.FIT_OUTPUT,
                d119.TRAIN_ARMS,
                d119.TRAIN_BASELINES,
                d125.FIT_OUTPUT,
            )
        },
        "decision": (
            "freeze_rank_quality_selected_controller_before_fresh_validation"
            if selected is not None
            else "close_rank_quality_selection_at_fit_gate"
        ),
    }
    FIT_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def checkpoint_payload(
    model: d117.FactorizedController, selected: dict
) -> dict:
    return {
        "schema": "troll-farm-d126a-rank-quality-selected-calibrated-q6-checkpoint-v1",
        "parameters": 6_626,
        "epochs": d119.EPOCHS,
        "soft_value_temperature": d118.TEMPERATURE,
        "target_fit_activity": d125.TARGET_ACTIVITY,
        "seed": selected["seed"],
        "gate_offset": selected["gate_offset"],
        "model_hash": selected["model_hash"],
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def validate(validation_elapsed: float) -> dict:
    selection_lock = d117.verify_manifest(SELECTION_LOCK)
    fit = json.loads(FIT_OUTPUT.read_text())
    selected = fit.get("selected")
    if fit.get("decision") != "freeze_rank_quality_selected_controller_before_fresh_validation":
        raise RuntimeError("D126 fit did not authorize fresh validation")
    if not selected or not selected["fit_eligible"]:
        raise RuntimeError("D126 has no eligible calibrated controller")

    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    dataset, training, _, models = d119.train_models_and_grid(train)
    summary = next(item for item in training if item["seed"] == selected["seed"])
    reproduced = d125.calibrated_candidate(
        train,
        dataset,
        models[selected["seed"]],
        summary,
        selected["grid_index"],
    )
    if reproduced != selected:
        raise RuntimeError("D126 selected calibrated controller did not reproduce")

    validation = d114.panel(
        VALIDATION_ARMS,
        VALIDATION_BASELINES,
        VALIDATION_START,
        VALIDATION_MAPS,
        validation_elapsed,
    )
    mechanics = d125.policy_evaluation_mechanics(validation["mechanics"])
    metrics = None
    gates = None
    passed = False
    if mechanics["pass"]:
        model = models[selected["seed"]]
        validation_dataset = d118.soft_value_dataset(validation)
        ranks = d115.model_logits(model.ranker, validation["x"])
        gate_values = d117.state_gate_logits(model, validation_dataset)
        gate_by_root = dict(
            zip(validation_dataset["root_order"], gate_values, strict=True)
        )
        metrics = d117.factorized_policy_metrics(
            validation, ranks, gate_by_root, selected["gate_offset"]
        )
        gates = d125.validation_gates(
            metrics, d123.control_crop_rate(validation)
        )
        passed = all(gates.values())

    checkpoint = None
    if passed:
        model = models[selected["seed"]]
        torch.save(checkpoint_payload(model, selected), CHECKPOINT)
        checkpoint = {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "sha256": d119.sha256(CHECKPOINT),
            "bytes": CHECKPOINT.stat().st_size,
            "model_hash": selected["model_hash"],
        }
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D126 checkpoint exists without validation pass")

    result = {
        "schema": "troll-farm-d126a-rank-quality-selected-calibrated-q6-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "selection_lock": selection_lock,
        "fit_result": {
            "path": str(FIT_OUTPUT.relative_to(ROOT)),
            "sha256": d119.sha256(FIT_OUTPUT),
            "selected": selected,
        },
        "fresh_validation": {
            "seeds": f"{VALIDATION_START}--{VALIDATION_START + VALIDATION_MAPS - 1}",
            "maps": VALIDATION_MAPS,
            "tasks": VALIDATION_TASKS,
            "elapsed_seconds": validation_elapsed,
            "mechanics": mechanics,
            "teacher_signal_descriptive_only": validation["teacher"],
            "metrics": metrics,
            "gates": gates,
            "pass": passed,
        },
        "checkpoint": checkpoint,
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (VALIDATION_ARMS, VALIDATION_BASELINES)
        },
        "decision": (
            "open_quantized_rust_parity_and_separate_untouched_confirmation"
            if passed
            else "repair_collector_mechanics_only"
            if not mechanics["pass"]
            else "close_rank_quality_selected_controller_without_tuning"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("fit")
    validation = subparsers.add_parser("validate")
    validation.add_argument("--validation-elapsed", type=float, required=True)
    args = parser.parse_args()
    result = fit_only() if args.command == "fit" else validate(args.validation_elapsed)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
