#!/usr/bin/env python3
"""Train D118a's soft-value proposal ranker and factorized state gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as functional

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d118a-soft-value-q6-ranker-state-gate-protocol-2026-07-22.md"
FROZEN_INPUTS = BASE / "d118a-soft-value-q6-ranker-state-gate-frozen-inputs.json"
FIT_OUTPUT = BASE / "d118a-soft-value-q6-ranker-state-gate-fit-result.json"
SELECTION_LOCK = BASE / "d118a-soft-value-q6-ranker-state-gate-selection-lock.json"
TRAIN_ARMS = d117.TRAIN_ARMS
TRAIN_BASELINES = d117.TRAIN_BASELINES
VALIDATION_ARMS = BASE / "d118a-q6-validation-arms-9843670-9843685.tsv"
VALIDATION_BASELINES = BASE / "d118a-q6-validation-baselines-9843670-9843685.tsv"
CHECKPOINT = BASE / "d118a-soft-value-q6-ranker-state-gate.pt"
OUTPUT = BASE / "d118a-soft-value-q6-ranker-state-gate-result.json"

TRAIN_START = d117.TRAIN_START
TRAIN_MAPS = d117.TRAIN_MAPS
TRAIN_ELAPSED = d117.TRAIN_ELAPSED
VALIDATION_START = 9_843_670
VALIDATION_MAPS = 16
TEMPERATURE = 10.0
SEEDS = (11801, 11802, 11803, 11804)
OFFSETS = d117.OFFSETS
EPOCHS = 40
ROOT_BATCH_SIZE = 128
LEARNING_RATE = 1.0e-3
WEIGHT_DECAY = 1.0e-4
TRAIN_THREADS = 1


def sha256(path: Path) -> str:
    return d117.sha256(path)


def soft_value_dataset(data: dict) -> dict:
    dataset = d117.factorized_dataset(data)
    roots = len(dataset["root_order"])
    proposals = dataset["action_features"].shape[1]
    values = np.full((roots, proposals), -np.inf, dtype=np.float32)
    index_by_arm = {
        d112.arm_key(row): index for index, row in enumerate(data["arms"])
    }
    for root_index, root in enumerate(dataset["root_order"]):
        rows = data["arms_by_root"][root]
        indices = [index_by_arm[d112.arm_key(row)] for row in rows]
        values[root_index, : len(rows)] = data["y"][indices].astype(np.float32)
    value_tensor = torch.from_numpy(values)
    maximum = value_tensor.max(dim=1, keepdim=True).values
    centered = (value_tensor - maximum) / TEMPERATURE
    target_probabilities = torch.softmax(centered, dim=1)
    assert torch.isfinite(target_probabilities).all()
    assert torch.allclose(
        target_probabilities.sum(dim=1),
        torch.ones(roots),
        atol=1.0e-6,
    )
    dataset["proposal_values"] = value_tensor
    dataset["soft_rank_targets"] = target_probabilities
    dataset["summary"].update(
        {
            "soft_value_temperature": TEMPERATURE,
            "mean_target_entropy": float(
                (-(target_probabilities * target_probabilities.clamp_min(1e-30).log()).sum(1)).mean()
            ),
        }
    )
    return dataset


def soft_cross_entropy(
    logits: torch.Tensor,
    targets: torch.Tensor,
    valid: torch.Tensor,
) -> torch.Tensor:
    log_probabilities = torch.log_softmax(logits, dim=1)
    finite_log_probabilities = torch.where(
        valid,
        log_probabilities,
        torch.zeros_like(log_probabilities),
    )
    return -(targets * finite_log_probabilities).sum(dim=1).mean()


def train_soft_value_model(
    dataset: dict,
    seed: int,
    *,
    epochs: int = EPOCHS,
    root_batch_size: int = ROOT_BATCH_SIZE,
    threads: int = TRAIN_THREADS,
) -> tuple[d117.FactorizedController, dict]:
    d115.configure_torch(threads)
    torch.manual_seed(seed)
    model = d117.FactorizedController()
    assert d115.parameter_count(model) == 6_626
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )
    actions = dataset["action_features"]
    valid = dataset["valid"]
    states = dataset["state_features"]
    soft_targets = dataset["soft_rank_targets"]
    act_targets = dataset["act_targets"]
    generator = np.random.Generator(np.random.PCG64(seed))
    epoch_losses = []
    model.train()
    for _ in range(epochs):
        order = generator.permutation(len(act_targets))
        total_sum = 0.0
        rank_sum = 0.0
        gate_sum = 0.0
        roots_seen = 0
        for start in range(0, len(order), root_batch_size):
            indices = torch.from_numpy(order[start : start + root_batch_size])
            optimizer.zero_grad(set_to_none=True)
            ranks = d117.proposal_logits(model.ranker, actions[indices], valid[indices])
            gate = model.gate(states[indices])
            rank_loss = soft_cross_entropy(
                ranks,
                soft_targets[indices],
                valid[indices],
            )
            gate_loss = functional.binary_cross_entropy_with_logits(
                gate,
                act_targets[indices].float(),
            )
            loss = rank_loss + gate_loss
            loss.backward()
            optimizer.step()
            count = len(indices)
            total_sum += float(loss.detach()) * count
            rank_sum += float(rank_loss.detach()) * count
            gate_sum += float(gate_loss.detach()) * count
            roots_seen += count
        epoch_losses.append(
            {
                "total": total_sum / roots_seen,
                "rank": rank_sum / roots_seen,
                "gate": gate_sum / roots_seen,
            }
        )
    model.eval()
    with torch.no_grad():
        ranks = d117.proposal_logits(model.ranker, actions, valid)
        gate = model.gate(states)
        final_rank_loss = float(soft_cross_entropy(ranks, soft_targets, valid))
        final_gate_loss = float(
            functional.binary_cross_entropy_with_logits(gate, act_targets.float())
        )
        rank_predictions = ranks.argmax(dim=1)
        selected_values = dataset["proposal_values"].gather(
            1, rank_predictions[:, None]
        ).squeeze(1)
        best_values = dataset["proposal_values"].max(dim=1).values
        regrets = best_values - selected_values
        gate_predictions = gate > 0.0
        act_recall = float(gate_predictions[act_targets].float().mean())
        wait_recall = float((~gate_predictions[~act_targets]).float().mean())
    return model, {
        "seed": seed,
        "epochs": epochs,
        "root_batch_size": root_batch_size,
        "learning_rate": LEARNING_RATE,
        "weight_decay": WEIGHT_DECAY,
        "cpu_threads": threads,
        "parameters": d115.parameter_count(model),
        "model_hash": d115.canonical_model_hash(model),
        "first_epoch_streaming_loss": epoch_losses[0],
        "last_epoch_streaming_loss": epoch_losses[-1],
        "final_soft_rank_cross_entropy": final_rank_loss,
        "final_gate_binary_cross_entropy": final_gate_loss,
        "train_mean_proposal_regret": float(regrets.mean()),
        "train_median_proposal_regret": float(regrets.median()),
        "train_exact_best_rate": float((regrets == 0.0).float().mean()),
        "train_within_5_rate": float((regrets <= 5.0).float().mean()),
        "train_within_10_rate": float((regrets <= 10.0).float().mean()),
        "train_within_20_rate": float((regrets <= 20.0).float().mean()),
        "train_gate_act_recall": act_recall,
        "train_gate_wait_recall": wait_recall,
        "train_gate_balanced_accuracy": (act_recall + wait_recall) / 2.0,
    }


def model_fit_gates(summary: dict) -> dict[str, bool]:
    return {
        "mean_proposal_regret_at_most_18": (
            summary["train_mean_proposal_regret"] <= 18.0
        ),
        "within_10_rate_at_least_45pct": summary["train_within_10_rate"] >= 0.45,
        "gate_balanced_accuracy_at_least_60pct": (
            summary["train_gate_balanced_accuracy"] >= 0.60
        ),
        "gate_act_recall_at_least_50pct": summary["train_gate_act_recall"] >= 0.50,
        "gate_wait_recall_at_least_50pct": summary["train_gate_wait_recall"] >= 0.50,
    }


def fit_policy_gates(metrics: dict) -> dict[str, bool]:
    return {
        "mean_at_least_3": metrics["mean_margin_delta"] >= 3.0,
        "strict_at_least_30pct": metrics["strict_improvement_rate"] >= 0.30,
        "both_folds_nonnegative": min(metrics["fold_mean_margin_delta"].values()) >= 0.0,
        "worst_family_at_least_minus3": metrics["worst_family"] >= -3.0,
        "six_positive_families": metrics["positive_families"] >= 6,
        "activity_10_to_85pct": 0.10 <= metrics["intervention_rate"] <= 0.85,
        "crop_100pct": metrics["crop_rate"] == 1.0,
        "worker_three_within_5pp": (
            metrics["worker_three_rate"]
            >= metrics["control_worker_three_rate"] - 0.05
        ),
    }


def train_models_and_grid(train: dict) -> tuple[dict, list, list, dict]:
    dataset = soft_value_dataset(train)
    summaries = []
    candidates = []
    models = {}
    grid_index = 0
    for seed in SEEDS:
        model, summary = train_soft_value_model(dataset, seed)
        summaries.append(summary)
        models[seed] = model
        ranks = d115.model_logits(model.ranker, train["x"])
        gate_values = d117.state_gate_logits(model, dataset)
        gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
        structural = model_fit_gates(summary)
        for offset in OFFSETS:
            metrics = d117.factorized_policy_metrics(train, ranks, gate_by_root, offset)
            policy = fit_policy_gates(metrics)
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
        "schema": "troll-farm-d118a-soft-value-ranker-state-gate-checkpoint-v1",
        "action_features": d115.FEATURES,
        "state_features": d117.STATE_FEATURES,
        "rank_hidden": d115.HIDDEN,
        "gate_hidden": d117.GATE_HIDDEN,
        "parameters": d115.parameter_count(model),
        "soft_value_temperature": TEMPERATURE,
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
        "schema": "troll-farm-d118a-soft-value-q6-fit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "frozen_inputs": frozen,
        "train_mechanics": train["mechanics"],
        "train_teacher": train["teacher"],
        "training_data": dataset["summary"] if dataset is not None else None,
        "training": summaries,
        "fit_grid": {
            "seeds": SEEDS,
            "gate_offsets": OFFSETS,
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
            else "close_soft_value_model_at_fit_gate"
        ),
    }
    FIT_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def validate(validation_elapsed: float) -> None:
    frozen = d117.verify_manifest(FROZEN_INPUTS)
    selection_lock = d117.verify_manifest(SELECTION_LOCK)
    fit = json.loads(FIT_OUTPUT.read_text())
    if fit["decision"] != "open_fresh_validation_collection_after_exact_repeat":
        raise RuntimeError("D118 fit gate did not authorize validation")
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
            raise RuntimeError("D118 fit model hashes are not reproducible")
        validation_dataset = soft_value_dataset(validation)
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
        raise RuntimeError("stale D118 checkpoint exists without validation admission")
    result = {
        "schema": "troll-farm-d118a-soft-value-q6-ranker-state-gate-v1",
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
            "action_features": d115.FEATURES,
            "state_features": d117.STATE_FEATURES,
            "parameters": 6_626,
            "soft_value_temperature": TEMPERATURE,
            "training_threads": TRAIN_THREADS,
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
            else "close_soft_value_model_without_held"
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
