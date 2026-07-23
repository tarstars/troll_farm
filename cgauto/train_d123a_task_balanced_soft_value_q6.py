#!/usr/bin/env python3
"""Retrospectively test task-balanced D119 soft-value training."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as functional

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import evaluate_d119a_held_soft_value_q6 as held_eval
from cgauto import evaluate_d119a_held_coverage_repair as repair
from cgauto import evaluate_d120a_policy_sealed_absolute_information as d120
from cgauto import analyze_d121a_d119_retrospective_grid as d121


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d123a-task-balanced-soft-value-q6-protocol-2026-07-22.md"
LOCK = BASE / "d123a-task-balanced-soft-value-q6-lock.json"
OUTPUT = BASE / "d123a-task-balanced-soft-value-q6-result.json"

SEEDS = (12301, 12302, 12303, 12304)
OFFSETS = d119.OFFSETS
EPOCHS = d119.EPOCHS


def task_balanced_root_weights(root_order: list) -> torch.Tensor:
    counts = Counter(root[0] for root in root_order)
    raw = np.asarray([1.0 / counts[root[0]] for root in root_order], dtype=np.float32)
    raw /= raw.mean()
    weights = torch.from_numpy(raw)
    assert weights.shape == (len(root_order),)
    assert bool(torch.isfinite(weights).all()) and bool((weights > 0).all())
    return weights


def soft_cross_entropy_per_root(
    logits: torch.Tensor,
    targets: torch.Tensor,
    valid: torch.Tensor,
) -> torch.Tensor:
    masked = logits.masked_fill(~valid, float("-inf"))
    log_probabilities = functional.log_softmax(masked, dim=1)
    finite = torch.where(valid, log_probabilities, torch.zeros_like(log_probabilities))
    result = -(targets * finite).sum(dim=1)
    assert result.shape == (len(logits),) and bool(torch.isfinite(result).all())
    return result


def train_task_balanced_model(dataset: dict, seed: int):
    d115.configure_torch(1)
    torch.manual_seed(seed)
    model = d117.FactorizedController()
    assert d115.parameter_count(model) == 6_626
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=d118.LEARNING_RATE,
        weight_decay=d118.WEIGHT_DECAY,
    )
    actions = dataset["action_features"]
    valid = dataset["valid"]
    states = dataset["state_features"]
    soft_targets = dataset["soft_rank_targets"]
    act_targets = dataset["act_targets"]
    weights = dataset["root_weights"]
    generator = np.random.Generator(np.random.PCG64(seed))
    epoch_losses = []
    model.train()
    for _ in range(EPOCHS):
        order = generator.permutation(len(act_targets))
        total_sum = 0.0
        rank_sum = 0.0
        gate_sum = 0.0
        weight_seen = 0.0
        for start in range(0, len(order), d118.ROOT_BATCH_SIZE):
            indices = torch.from_numpy(order[start : start + d118.ROOT_BATCH_SIZE])
            batch_weights = weights[indices]
            denominator = batch_weights.sum()
            optimizer.zero_grad(set_to_none=True)
            ranks = d117.proposal_logits(model.ranker, actions[indices], valid[indices])
            gate = model.gate(states[indices])
            rank_losses = soft_cross_entropy_per_root(
                ranks,
                soft_targets[indices],
                valid[indices],
            )
            gate_losses = functional.binary_cross_entropy_with_logits(
                gate,
                act_targets[indices].float(),
                reduction="none",
            )
            rank_loss = (rank_losses * batch_weights).sum() / denominator
            gate_loss = (gate_losses * batch_weights).sum() / denominator
            loss = rank_loss + gate_loss
            loss.backward()
            optimizer.step()
            weight = float(denominator)
            total_sum += float(loss.detach()) * weight
            rank_sum += float(rank_loss.detach()) * weight
            gate_sum += float(gate_loss.detach()) * weight
            weight_seen += weight
        epoch_losses.append(
            {
                "total": total_sum / weight_seen,
                "rank": rank_sum / weight_seen,
                "gate": gate_sum / weight_seen,
            }
        )

    model.eval()
    with torch.no_grad():
        ranks = d117.proposal_logits(model.ranker, actions, valid)
        gate = model.gate(states)
        rank_losses = soft_cross_entropy_per_root(ranks, soft_targets, valid)
        gate_losses = functional.binary_cross_entropy_with_logits(
            gate,
            act_targets.float(),
            reduction="none",
        )
        final_rank_loss = float((rank_losses * weights).sum() / weights.sum())
        final_gate_loss = float((gate_losses * weights).sum() / weights.sum())
        rank_predictions = ranks.argmax(dim=1)
        selected_values = dataset["proposal_values"].gather(
            1, rank_predictions[:, None]
        ).squeeze(1)
        best_values = dataset["proposal_values"].max(dim=1).values
        regrets = best_values - selected_values
        gate_predictions = gate > 0.0
        act_recall = float(gate_predictions[act_targets].float().mean())
        wait_recall = float((~gate_predictions[~act_targets]).float().mean())
    summary = {
        "seed": seed,
        "epochs": EPOCHS,
        "root_batch_size": d118.ROOT_BATCH_SIZE,
        "learning_rate": d118.LEARNING_RATE,
        "weight_decay": d118.WEIGHT_DECAY,
        "cpu_threads": 1,
        "parameters": d115.parameter_count(model),
        "model_hash": d115.canonical_model_hash(model),
        "first_epoch_streaming_loss": epoch_losses[0],
        "last_epoch_streaming_loss": epoch_losses[-1],
        "final_weighted_soft_rank_cross_entropy": final_rank_loss,
        "final_weighted_gate_binary_cross_entropy": final_gate_loss,
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
    return model, summary


def control_crop_rate(panel: dict) -> float:
    controls = panel["baseline_by_task"].values()
    return d114.d112.mean(int(row["own_created_crops"]) > 0 for row in controls)


def relative_held_gates(metrics: dict, control_crop: float) -> dict[str, bool]:
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
        "crop_not_below_control": metrics["crop_rate"] >= control_crop,
        "worker_three_within_5pp": (
            metrics["worker_three_rate"]
            >= metrics["control_worker_three_rate"] - 0.05
        ),
    }


def panel_metrics(panel: dict, model: d117.FactorizedController, offset: float) -> dict:
    dataset = d118.soft_value_dataset(panel)
    ranks = d115.model_logits(model.ranker, panel["x"])
    gate_values = d117.state_gate_logits(model, dataset)
    gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
    return d117.factorized_policy_metrics(panel, ranks, gate_by_root, offset)


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    train_dataset = d118.soft_value_dataset(train)
    weights = task_balanced_root_weights(train_dataset["root_order"])
    train_dataset["root_weights"] = weights
    task_weight_totals = Counter()
    for root, weight in zip(train_dataset["root_order"], weights.tolist(), strict=True):
        task_weight_totals[root[0]] += weight
    weight_summary = {
        "roots": len(weights),
        "supported_tasks": len(task_weight_totals),
        "minimum_root_weight": float(weights.min()),
        "maximum_root_weight": float(weights.max()),
        "minimum_task_total_weight": min(task_weight_totals.values()),
        "maximum_task_total_weight": max(task_weight_totals.values()),
    }

    audit = repair.combined_panel(repair.MAX_BLOCKS, d120.ELAPSED, lock)
    d120.enrich_panel(audit)
    audit_control_crop = control_crop_rate(audit)
    models = {}
    training = []
    candidates = []
    grid_index = 0
    for seed in SEEDS:
        model, summary = train_task_balanced_model(train_dataset, seed)
        models[seed] = model
        training.append(summary)
        structural = d118.model_fit_gates(summary)
        for offset in OFFSETS:
            train_metrics = panel_metrics(train, model, offset)
            train_gates = d118.fit_policy_gates(train_metrics)
            audit_metrics = panel_metrics(audit, model, offset)
            audit_gates = relative_held_gates(audit_metrics, audit_control_crop)
            candidates.append(
                {
                    "id": d121.candidate_id(seed, offset),
                    "grid_index": grid_index,
                    "seed": seed,
                    "gate_offset": offset,
                    "model_hash": summary["model_hash"],
                    "model_fit_gates": structural,
                    "train_metrics": train_metrics,
                    "train_policy_gates": train_gates,
                    "audit_metrics": audit_metrics,
                    "relative_held_gates": audit_gates,
                    "retrospective_eligible": (
                        all(structural.values())
                        and all(train_gates.values())
                        and all(audit_gates.values())
                    ),
                }
            )
            grid_index += 1

    eligible = [item for item in candidates if item["retrospective_eligible"]]
    selected = max(
        eligible,
        key=lambda item: d115.selection_key(
            {"metrics": item["audit_metrics"], "grid_index": item["grid_index"]}
        ),
    ) if eligible else None

    d121_result = json.loads(d121.OUTPUT.read_text())
    d119_relative_passes = []
    for item in d121_result["grid"]["results"]:
        gates = relative_held_gates(item["metrics"], audit_control_crop)
        if all(gates.values()):
            d119_relative_passes.append(item["id"])

    result = {
        "schema": "troll-farm-d123a-task-balanced-soft-value-q6-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "isolated_change": "equal total rank/gate loss per supported task instead of per root",
        "architecture": {
            "parameters": 6_626,
            "epochs": EPOCHS,
            "soft_value_temperature": d118.TEMPERATURE,
            "training_threads": 1,
        },
        "weighting": weight_summary,
        "training": training,
        "audit": {
            "maps": d120.MAPS,
            "tasks": d120.TASKS,
            "control_crop_rate": audit_control_crop,
            "d119_relative_crop_passes": d119_relative_passes,
            "grid_candidates": len(candidates),
            "retrospective_eligible": len(eligible),
            "results": candidates,
            "selected": selected,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (
                d119.TRAIN_ARMS,
                d119.TRAIN_BASELINES,
                d121.OUTPUT,
                *repair.input_paths(repair.MAX_BLOCKS)[0],
                *repair.input_paths(repair.MAX_BLOCKS)[1],
            )
        },
        "decision": (
            "freeze_task_balanced_candidate_for_fresh_validation_protocol"
            if selected is not None
            else "close_task_balanced_objective_without_fresh_simulation"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
