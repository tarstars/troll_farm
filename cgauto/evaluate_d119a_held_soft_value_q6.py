#!/usr/bin/env python3
"""Evaluate D119a's locked controller once on its untouched dense held panel."""

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


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d119a-held-soft-value-q6-protocol-2026-07-22.md"
HELD_LOCK = BASE / "d119a-held-soft-value-q6-lock.json"
VALIDATION_RESULT = BASE / "d119a-long-fit-soft-value-q6-result.json"
CHECKPOINT = BASE / "d119a-long-fit-soft-value-q6.pt"
HELD_ARMS = BASE / "d119a-q6-held-arms-9843700-9843715.tsv"
HELD_BASELINES = BASE / "d119a-q6-held-baselines-9843700-9843715.tsv"
OUTPUT = BASE / "d119a-held-soft-value-q6-result.json"

HELD_START = 9_843_700
HELD_MAPS = 16
HELD_TASKS = 256


def held_admission(metrics: dict) -> dict[str, bool]:
    """Apply the frozen D117--D119 held gates without selection or tuning."""
    return {
        "mean_at_least_2": metrics["mean_margin_delta"] >= 2.0,
        "strict_at_least_40pct": metrics["strict_improvement_rate"] >= 0.40,
        "worst_family_at_least_minus3": metrics["worst_family"] >= -3.0,
        "six_positive_families": metrics["positive_families"] >= 6,
        "own_nonnegative_or_opponent_nonpositive": (
            metrics["mean_own_score_delta"] >= 0.0
            or metrics["mean_opponent_score_delta"] <= 0.0
        ),
        "activity_10_to_85pct": 0.10 <= metrics["intervention_rate"] <= 0.85,
        "crop_100pct": metrics["crop_rate"] == 1.0,
        "worker_three_within_5pp": (
            metrics["worker_three_rate"]
            >= metrics["control_worker_three_rate"] - 0.05
        ),
    }


def load_locked_controller(validation: dict) -> tuple[d117.FactorizedController, dict]:
    selected = validation.get("selected")
    checkpoint_record = validation.get("checkpoint")
    if validation.get("decision") != "open_conditional_dense_held_qualification":
        raise RuntimeError("D119 validation did not authorize held qualification")
    if not selected or not selected.get("admitted") or not checkpoint_record:
        raise RuntimeError("D119 validation has no admitted locked checkpoint")
    if checkpoint_record["path"] != str(CHECKPOINT.relative_to(ROOT)):
        raise RuntimeError("D119 checkpoint path does not match the held contract")
    if d119.sha256(CHECKPOINT) != checkpoint_record["sha256"]:
        raise RuntimeError("D119 checkpoint bytes do not match validation")

    payload = torch.load(CHECKPOINT, map_location="cpu", weights_only=False)
    expected = {
        "schema": "troll-farm-d119a-long-fit-soft-value-q6-checkpoint-v1",
        "parameters": 6_626,
        "epochs": d119.EPOCHS,
        "soft_value_temperature": d118.TEMPERATURE,
        "seed": selected["seed"],
        "gate_offset": selected["gate_offset"],
        "model_hash": selected["model_hash"],
    }
    actual = {key: payload.get(key) for key in expected}
    if actual != expected:
        raise RuntimeError(f"D119 checkpoint metadata mismatch: {actual!r}")

    model = d117.FactorizedController()
    model.load_state_dict(payload["state_dict"], strict=True)
    model.eval()
    model_hash = d115.canonical_model_hash(model)
    if model_hash != selected["model_hash"]:
        raise RuntimeError("D119 checkpoint tensors do not match the selected model hash")
    return model, selected


def evaluate(held_elapsed: float) -> dict:
    held_lock = d117.verify_manifest(HELD_LOCK)
    validation = json.loads(VALIDATION_RESULT.read_text())
    model, selected = load_locked_controller(validation)
    held = d114.panel(
        HELD_ARMS,
        HELD_BASELINES,
        HELD_START,
        HELD_MAPS,
        held_elapsed,
    )
    mechanics_pass = (
        held_lock["pass"]
        and held["mechanics"]["pass"]
        and held["mechanics"]["details"]["tasks"] == HELD_TASKS
    )
    metrics = None
    gates = None
    if mechanics_pass:
        dataset = d118.soft_value_dataset(held)
        ranks = d115.model_logits(model.ranker, held["x"])
        gate_values = d117.state_gate_logits(model, dataset)
        gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
        metrics = d117.factorized_policy_metrics(
            held,
            ranks,
            gate_by_root,
            selected["gate_offset"],
        )
        gates = held_admission(metrics)

    passed = mechanics_pass and gates is not None and all(gates.values())
    result = {
        "schema": "troll-farm-d119a-held-soft-value-q6-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "held_lock": held_lock,
        "validation_result": {
            "path": str(VALIDATION_RESULT.relative_to(ROOT)),
            "sha256": d119.sha256(VALIDATION_RESULT),
            "decision": validation["decision"],
        },
        "checkpoint": {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "sha256": d119.sha256(CHECKPOINT),
            "model_hash": d115.canonical_model_hash(model),
            "seed": selected["seed"],
            "gate_offset": selected["gate_offset"],
            "bytes": CHECKPOINT.stat().st_size,
        },
        "held_panel": {
            "seeds": f"{HELD_START}--{HELD_START + HELD_MAPS - 1}",
            "maps": HELD_MAPS,
            "tasks": HELD_TASKS,
            "elapsed_seconds": held_elapsed,
            "mechanics": held["mechanics"],
            "teacher_signal": held["teacher"],
            "metrics": metrics,
            "admission": gates,
            "pass": passed,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (HELD_ARMS, HELD_BASELINES)
        },
        "decision": (
            "open_quantized_rust_parity_and_final_untouched_confirmation"
            if passed
            else "repair_held_coverage_only"
            if not mechanics_pass
            else "close_without_tuning_on_held"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--held-elapsed", type=float, required=True)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.held_elapsed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
