#!/usr/bin/env python3
"""Train D119 with absolute proposal-value anchoring and a zero-value shield."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as functional

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d128a-absolute-value-anchored-soft-ranker-protocol-2026-07-22.md"
LOCK = BASE / "d128a-absolute-value-anchored-soft-ranker-repair1-lock.json"
OUTPUT = BASE / "d128a-absolute-value-anchored-soft-ranker-result.json"

SEEDS = (12801, 12802, 12803, 12804)
EPOCHS = d119.EPOCHS
VALUE_SCALE = d118.TEMPERATURE
VALUE_LOSS_COEFFICIENT = 1.0


def root_balanced_value_loss(
    raw_logits: torch.Tensor,
    proposal_values: torch.Tensor,
    valid: torch.Tensor,
) -> torch.Tensor:
    targets = torch.where(
        valid,
        proposal_values / VALUE_SCALE,
        torch.zeros_like(proposal_values),
    )
    losses = functional.smooth_l1_loss(
        raw_logits, targets, reduction="none", beta=1.0
    )
    per_root = (losses * valid).sum(dim=1) / valid.sum(dim=1)
    result = per_root.mean()
    assert result.ndim == 0 and bool(torch.isfinite(result))
    return result


def absolute_value_metrics(
    rank_logits: torch.Tensor, dataset: dict
) -> dict[str, float]:
    predicted_positions = rank_logits.argmax(dim=1)
    predicted_logits = rank_logits.gather(
        1, predicted_positions[:, None]
    ).squeeze(1)
    selected_values = dataset["proposal_values"].gather(
        1, predicted_positions[:, None]
    ).squeeze(1)
    best_values = dataset["proposal_values"].max(dim=1).values
    regrets = best_values - selected_values
    target_act = best_values > 0.0
    predicted_act = predicted_logits > 0.0
    act_recall = float(predicted_act[target_act].float().mean())
    wait_recall = float((~predicted_act[~target_act]).float().mean())
    return {
        "train_mean_proposal_regret": float(regrets.mean()),
        "train_median_proposal_regret": float(regrets.median()),
        "train_exact_best_rate": float((regrets == 0.0).float().mean()),
        "train_within_5_rate": float((regrets <= 5.0).float().mean()),
        "train_within_10_rate": float((regrets <= 10.0).float().mean()),
        "train_within_20_rate": float((regrets <= 20.0).float().mean()),
        "train_value_sign_act_recall": act_recall,
        "train_value_sign_wait_recall": wait_recall,
        "train_value_sign_balanced_accuracy": (act_recall + wait_recall) / 2.0,
        "train_predicted_positive_root_rate": float(predicted_act.float().mean()),
        "train_selected_positive_value_rate": float((selected_values > 0.0).float().mean()),
    }


def train_model(dataset: dict, seed: int):
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
    values = dataset["proposal_values"]
    act_targets = dataset["act_targets"]
    generator = np.random.Generator(np.random.PCG64(seed))
    epoch_losses = []
    model.train()
    for _ in range(EPOCHS):
        order = generator.permutation(len(act_targets))
        sums = {"total": 0.0, "rank": 0.0, "gate": 0.0, "value": 0.0}
        roots_seen = 0
        for start in range(0, len(order), d118.ROOT_BATCH_SIZE):
            indices = torch.from_numpy(order[start : start + d118.ROOT_BATCH_SIZE])
            optimizer.zero_grad(set_to_none=True)
            shape = actions[indices].shape
            raw = model.ranker(actions[indices].reshape(-1, shape[-1])).reshape(
                shape[0], shape[1]
            )
            ranks = raw.masked_fill(~valid[indices], float("-inf"))
            gate = model.gate(states[indices])
            rank_loss = d123.soft_cross_entropy_per_root(
                ranks, soft_targets[indices], valid[indices]
            ).mean()
            gate_loss = functional.binary_cross_entropy_with_logits(
                gate, act_targets[indices].float()
            )
            value_loss = root_balanced_value_loss(
                raw, values[indices], valid[indices]
            )
            loss = rank_loss + gate_loss + VALUE_LOSS_COEFFICIENT * value_loss
            loss.backward()
            optimizer.step()
            count = len(indices)
            for name, item in (
                ("total", loss),
                ("rank", rank_loss),
                ("gate", gate_loss),
                ("value", value_loss),
            ):
                sums[name] += float(item.detach()) * count
            roots_seen += count
        epoch_losses.append(
            {name: value / roots_seen for name, value in sums.items()}
        )

    model.eval()
    with torch.no_grad():
        raw = model.ranker(actions.reshape(-1, actions.shape[-1])).reshape(
            actions.shape[0], actions.shape[1]
        )
        ranks = raw.masked_fill(~valid, float("-inf"))
        gate = model.gate(states)
        final_rank = float(
            d123.soft_cross_entropy_per_root(ranks, soft_targets, valid).mean()
        )
        final_gate = float(
            functional.binary_cross_entropy_with_logits(
                gate, act_targets.float()
            )
        )
        final_value = float(root_balanced_value_loss(raw, values, valid))
        gate_predictions = gate > 0.0
        gate_act_recall = float(gate_predictions[act_targets].float().mean())
        gate_wait_recall = float((~gate_predictions[~act_targets]).float().mean())
        value_metrics = absolute_value_metrics(ranks, dataset)
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
        "final_soft_rank_cross_entropy": final_rank,
        "final_gate_binary_cross_entropy": final_gate,
        "final_root_balanced_smooth_l1": final_value,
        "train_gate_act_recall": gate_act_recall,
        "train_gate_wait_recall": gate_wait_recall,
        "train_gate_balanced_accuracy": (
            gate_act_recall + gate_wait_recall
        ) / 2.0,
        **value_metrics,
    }
    return model, summary


def model_gates(summary: dict) -> dict[str, bool]:
    gates = d118.model_fit_gates(summary)
    gates.update(
        {
            "value_sign_balanced_accuracy_at_least_60pct": (
                summary["train_value_sign_balanced_accuracy"] >= 0.60
            ),
            "value_sign_act_recall_at_least_50pct": (
                summary["train_value_sign_act_recall"] >= 0.50
            ),
            "value_sign_wait_recall_at_least_50pct": (
                summary["train_value_sign_wait_recall"] >= 0.50
            ),
        }
    )
    return gates


def value_shielded_policy_metrics(
    data: dict,
    model: d117.FactorizedController,
    offset: float,
) -> dict:
    dataset = d118.soft_value_dataset(data)
    ranks = d115.model_logits(model.ranker, data["x"])
    rank_by_arm = {
        d112.arm_key(row): float(score)
        for row, score in zip(data["arms"], ranks, strict=True)
    }
    gates = d117.state_gate_logits(model, dataset)
    gate_by_root = {}
    for root, gate in zip(dataset["root_order"], gates, strict=True):
        best_prediction = max(
            rank_by_arm[d112.arm_key(row)] for row in data["arms_by_root"][root]
        )
        gate_by_root[root] = float(gate) if best_prediction > 0.0 else float("-inf")
    return d117.factorized_policy_metrics(data, ranks, gate_by_root, offset)


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    dataset = d118.soft_value_dataset(train)
    training = []
    models = {}
    candidates = []
    for index, seed in enumerate(SEEDS):
        model, summary = train_model(dataset, seed)
        models[seed] = model
        training.append(summary)
        gate_values = d117.state_gate_logits(model, dataset)
        offset, calibration = d125.activity_calibrated_offset(
            list(train["baseline_by_task"]), dataset["root_order"], gate_values
        )
        metrics = value_shielded_policy_metrics(train, model, offset)
        structural = model_gates(summary)
        policy = d118.fit_policy_gates(metrics)
        candidates.append(
            {
                "grid_index": index,
                "seed": seed,
                "model_hash": summary["model_hash"],
                "gate_offset": offset,
                "state_gate_calibration": calibration,
                "model_fit_gates": structural,
                "fit_policy_metrics": metrics,
                "fit_policy_gates": policy,
                "fit_eligible": all(structural.values()) and all(policy.values()),
            }
        )

    eligible = [item for item in candidates if item["fit_eligible"]]
    summary_by_seed = {item["seed"]: item for item in training}
    selected = (
        min(eligible, key=lambda item: d126.rank_quality_key(item, summary_by_seed))
        if eligible
        else None
    )

    development = d114.panel(
        d126.VALIDATION_ARMS,
        d126.VALIDATION_BASELINES,
        d126.VALIDATION_START,
        d126.VALIDATION_MAPS,
        json.loads(d126.OUTPUT.read_text())["fresh_validation"]["elapsed_seconds"],
    )
    development_metrics = None
    development_gates = None
    development_pass = False
    if selected is not None:
        development_metrics = value_shielded_policy_metrics(
            development, models[selected["seed"]], selected["gate_offset"]
        )
        development_gates = d125.validation_gates(
            development_metrics, d123.control_crop_rate(development)
        )
        development_pass = all(development_gates.values())

    result = {
        "schema": "troll-farm-d128a-absolute-value-anchored-soft-ranker-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "isolated_change": "root-balanced smooth-L1 absolute value anchor plus zero-value shield",
        "architecture": {
            "parameters": 6_626,
            "epochs": EPOCHS,
            "soft_value_temperature": d118.TEMPERATURE,
            "value_target_scale": VALUE_SCALE,
            "value_loss_coefficient": VALUE_LOSS_COEFFICIENT,
            "training_threads": 1,
        },
        "training": training,
        "fit": {
            "candidates": candidates,
            "eligible": len(eligible),
            "selected": selected,
        },
        "consumed_d126_development": {
            "qualification_authority": False,
            "metrics": development_metrics,
            "gates": development_gates,
            "pass": development_pass,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (
                d119.TRAIN_ARMS,
                d119.TRAIN_BASELINES,
                d126.OUTPUT,
                d126.VALIDATION_ARMS,
                d126.VALIDATION_BASELINES,
            )
        },
        "decision": (
            "freeze_fresh_d128_validation_protocol"
            if development_pass
            else "close_absolute_value_anchor_without_fresh_simulation"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
