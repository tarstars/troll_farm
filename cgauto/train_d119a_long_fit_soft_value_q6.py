#!/usr/bin/env python3
"""Run D119a: D118's soft-value factorized model with 80 fit epochs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d119a-long-fit-soft-value-q6-protocol-2026-07-22.md"
FROZEN_INPUTS = BASE / "d119a-long-fit-soft-value-q6-frozen-inputs.json"
FIT_OUTPUT = BASE / "d119a-long-fit-soft-value-q6-fit-result.json"
SELECTION_LOCK = BASE / "d119a-long-fit-soft-value-q6-selection-lock.json"
TRAIN_ARMS = d118.TRAIN_ARMS
TRAIN_BASELINES = d118.TRAIN_BASELINES
VALIDATION_ARMS = BASE / "d119a-q6-validation-arms-9843670-9843685.tsv"
VALIDATION_BASELINES = BASE / "d119a-q6-validation-baselines-9843670-9843685.tsv"
CHECKPOINT = BASE / "d119a-long-fit-soft-value-q6.pt"
OUTPUT = BASE / "d119a-long-fit-soft-value-q6-result.json"

TRAIN_START = d118.TRAIN_START
TRAIN_MAPS = d118.TRAIN_MAPS
TRAIN_ELAPSED = d118.TRAIN_ELAPSED
VALIDATION_START = d118.VALIDATION_START
VALIDATION_MAPS = d118.VALIDATION_MAPS
SEEDS = (11901, 11902, 11903, 11904)
OFFSETS = d118.OFFSETS
EPOCHS = 80


def sha256(path: Path) -> str:
    return d117.sha256(path)


def train_long_model(dataset: dict, seed: int, *, epochs: int = EPOCHS):
    return d118.train_soft_value_model(dataset, seed, epochs=epochs)


def train_models_and_grid(train: dict) -> tuple[dict, list, list, dict]:
    dataset = d118.soft_value_dataset(train)
    summaries = []
    candidates = []
    models = {}
    grid_index = 0
    for seed in SEEDS:
        model, summary = train_long_model(dataset, seed)
        summaries.append(summary)
        models[seed] = model
        ranks = d115.model_logits(model.ranker, train["x"])
        gate_values = d117.state_gate_logits(model, dataset)
        gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
        structural = d118.model_fit_gates(summary)
        for offset in OFFSETS:
            metrics = d117.factorized_policy_metrics(train, ranks, gate_by_root, offset)
            policy = d118.fit_policy_gates(metrics)
            candidates.append(
                {
                    "grid_index": grid_index,
                    "seed": seed,
                    "gate_offset": offset,
                    "model_hash": summary["model_hash"],
                    "model_fit_gates": structural,
                    "fit_policy_metrics": metrics,
                    "fit_policy_gates": policy,
                    "fit_eligible": all(structural.values()) and all(policy.values()),
                }
            )
            grid_index += 1
    return dataset, summaries, candidates, models


def checkpoint_payload(model: d117.FactorizedController, selected: dict) -> dict:
    return {
        "schema": "troll-farm-d119a-long-fit-soft-value-q6-checkpoint-v1",
        "parameters": d115.parameter_count(model),
        "epochs": EPOCHS,
        "soft_value_temperature": d118.TEMPERATURE,
        "seed": selected["seed"],
        "gate_offset": selected["gate_offset"],
        "model_hash": d115.canonical_model_hash(model),
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def fit_only() -> None:
    frozen = d117.verify_manifest(FROZEN_INPUTS)
    train = d114.panel(
        TRAIN_ARMS,
        TRAIN_BASELINES,
        TRAIN_START,
        TRAIN_MAPS,
        TRAIN_ELAPSED,
    )
    dataset = None
    summaries = []
    candidates = []
    if frozen["pass"] and train["mechanics"]["pass"]:
        dataset, summaries, candidates, _ = train_models_and_grid(train)
    eligible = [candidate for candidate in candidates if candidate["fit_eligible"]]
    result = {
        "schema": "troll-farm-d119a-long-fit-soft-value-q6-fit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "frozen_inputs": frozen,
        "train_mechanics": train["mechanics"],
        "train_teacher": train["teacher"],
        "training_data": dataset["summary"] if dataset is not None else None,
        "training": summaries,
        "fit_grid": {
            "seeds": SEEDS,
            "gate_offsets": OFFSETS,
            "epochs": EPOCHS,
            "candidates": len(candidates),
            "eligible": len(eligible),
            "results": candidates,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (TRAIN_ARMS, TRAIN_BASELINES)
        },
        "decision": (
            "open_fresh_validation_collection_after_exact_repeat"
            if eligible
            else "repair_only"
            if not (frozen["pass"] and train["mechanics"]["pass"])
            else "close_long_fit_model_at_fit_gate"
        ),
    }
    FIT_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def validate(validation_elapsed: float) -> None:
    frozen = d117.verify_manifest(FROZEN_INPUTS)
    selection_lock = d117.verify_manifest(SELECTION_LOCK)
    fit = json.loads(FIT_OUTPUT.read_text())
    if fit["decision"] != "open_fresh_validation_collection_after_exact_repeat":
        raise RuntimeError("D119 fit gate did not authorize validation")
    train = d114.panel(
        TRAIN_ARMS,
        TRAIN_BASELINES,
        TRAIN_START,
        TRAIN_MAPS,
        TRAIN_ELAPSED,
    )
    validation = d114.panel(
        VALIDATION_ARMS,
        VALIDATION_BASELINES,
        VALIDATION_START,
        VALIDATION_MAPS,
        validation_elapsed,
    )
    mechanics_pass = (
        frozen["pass"]
        and selection_lock["pass"]
        and train["mechanics"]["pass"]
        and validation["mechanics"]["pass"]
    )
    summaries = []
    candidates = []
    models = {}
    reproduced = False
    if mechanics_pass:
        _, summaries, _, models = train_models_and_grid(train)
        expected = {item["seed"]: item["model_hash"] for item in fit["training"]}
        actual = {item["seed"]: item["model_hash"] for item in summaries}
        reproduced = expected == actual
        if not reproduced:
            raise RuntimeError("D119 fit model hashes are not reproducible")
        validation_dataset = d118.soft_value_dataset(validation)
        grid_index = 0
        for seed in SEEDS:
            model = models[seed]
            ranks = d115.model_logits(model.ranker, validation["x"])
            gate_values = d117.state_gate_logits(model, validation_dataset)
            gate_by_root = dict(
                zip(validation_dataset["root_order"], gate_values, strict=True)
            )
            for offset in OFFSETS:
                metrics = d117.factorized_policy_metrics(
                    validation,
                    ranks,
                    gate_by_root,
                    offset,
                )
                gates = d115.admission(metrics)
                candidates.append(
                    {
                        "grid_index": grid_index,
                        "seed": seed,
                        "gate_offset": offset,
                        "model_hash": actual[seed],
                        "metrics": metrics,
                        "admission": gates,
                        "admitted": all(gates.values()),
                    }
                )
                grid_index += 1
    admitted = [candidate for candidate in candidates if candidate["admitted"]]
    selected = max(admitted, key=d115.selection_key) if admitted else None
    checkpoint = None
    if selected is not None:
        model = models[selected["seed"]]
        torch.save(checkpoint_payload(model, selected), CHECKPOINT)
        checkpoint = {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "sha256": sha256(CHECKPOINT),
            "model_hash": d115.canonical_model_hash(model),
            "bytes": CHECKPOINT.stat().st_size,
        }
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D119 checkpoint exists without validation admission")
    result = {
        "schema": "troll-farm-d119a-long-fit-soft-value-q6-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "frozen_inputs": frozen,
        "selection_lock": selection_lock,
        "fit_result": {
            "path": str(FIT_OUTPUT.relative_to(ROOT)),
            "sha256": sha256(FIT_OUTPUT),
            "decision": fit["decision"],
            "eligible": fit["fit_grid"]["eligible"],
        },
        "architecture": {
            "parameters": 6_626,
            "epochs": EPOCHS,
            "soft_value_temperature": d118.TEMPERATURE,
            "training_threads": d118.TRAIN_THREADS,
        },
        "collection_mechanics": {
            "train": train["mechanics"],
            "validation": validation["mechanics"],
            "pass": mechanics_pass,
        },
        "teacher": {
            "train": train["teacher"],
            "validation": validation["teacher"],
        },
        "fit_models_reproduced": reproduced,
        "training": summaries,
        "grid": {
            "seeds": SEEDS,
            "gate_offsets": OFFSETS,
            "candidates": len(candidates),
            "admitted": len(admitted),
            "results": candidates,
        },
        "selected": selected,
        "checkpoint": checkpoint,
        "artifacts": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (
                TRAIN_ARMS,
                TRAIN_BASELINES,
                VALIDATION_ARMS,
                VALIDATION_BASELINES,
            )
        },
        "decision": (
            "open_conditional_dense_held_qualification"
            if selected is not None
            else "repair_only"
            if not mechanics_pass
            else "close_long_fit_model_without_held"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fit-only", action="store_true")
    group.add_argument("--validation-elapsed", type=float)
    args = parser.parse_args()
    if args.fit_only:
        fit_only()
    else:
        validate(args.validation_elapsed)


if __name__ == "__main__":
    main()
