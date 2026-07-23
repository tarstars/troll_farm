#!/usr/bin/env python3
"""Train D119 with an equal-root positive-vs-nonpositive pairwise loss."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as functional

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
PROTOCOL = BASE / "d130a-cross-sign-pairwise-soft-ranker-protocol-2026-07-22.md"
LOCK = BASE / "d130a-cross-sign-pairwise-soft-ranker-lock.json"
OUTPUT = BASE / "d130a-cross-sign-pairwise-soft-ranker-result.json"

SEEDS = (13001, 13002, 13003, 13004)
PAIRWISE_LOSS_COEFFICIENT = 1.0


def cross_sign_pairwise_loss(
    raw_logits: torch.Tensor,
    proposal_values: torch.Tensor,
    valid: torch.Tensor,
) -> torch.Tensor:
    positive = valid & (proposal_values > 0.0)
    nonpositive = valid & (proposal_values <= 0.0)
    pairs = positive[:, :, None] & nonpositive[:, None, :]
    counts = pairs.sum(dim=(1, 2))
    eligible = counts > 0
    if not bool(eligible.any()):
        return raw_logits.sum() * 0.0
    differences = raw_logits[:, :, None] - raw_logits[:, None, :]
    losses = functional.softplus(-differences)
    per_root = (losses * pairs).sum(dim=(1, 2))[eligible] / counts[eligible]
    result = per_root.mean()
    assert result.ndim == 0 and bool(torch.isfinite(result))
    return result


def cross_sign_metrics(
    raw_logits: torch.Tensor,
    proposal_values: torch.Tensor,
    valid: torch.Tensor,
) -> dict[str, float | int]:
    positive = valid & (proposal_values > 0.0)
    nonpositive = valid & (proposal_values <= 0.0)
    pairs = positive[:, :, None] & nonpositive[:, None, :]
    counts = pairs.sum(dim=(1, 2))
    eligible = counts > 0
    differences = raw_logits[:, :, None] - raw_logits[:, None, :]
    correct = ((differences > 0.0) & pairs).sum(dim=(1, 2))
    pair_accuracy = (correct[eligible].float() / counts[eligible]).mean()
    winners = raw_logits.masked_fill(~valid, float("-inf")).argmax(dim=1)
    winning_values = proposal_values.gather(1, winners[:, None]).squeeze(1)
    return {
        "train_mixed_sign_roots": int(eligible.sum()),
        "train_cross_sign_pairs": int(counts.sum()),
        "train_cross_sign_pair_accuracy": float(pair_accuracy),
        "train_cross_sign_winner_positive_rate": float(
            (winning_values[eligible] > 0.0).float().mean()
        ),
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
    for _ in range(d119.EPOCHS):
        order = generator.permutation(len(act_targets))
        sums = {"total": 0.0, "rank": 0.0, "gate": 0.0, "pairwise": 0.0}
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
            pairwise_loss = cross_sign_pairwise_loss(
                raw, values[indices], valid[indices]
            )
            loss = (
                rank_loss
                + gate_loss
                + PAIRWISE_LOSS_COEFFICIENT * pairwise_loss
            )
            loss.backward()
            optimizer.step()
            count = len(indices)
            for name, item in (
                ("total", loss),
                ("rank", rank_loss),
                ("gate", gate_loss),
                ("pairwise", pairwise_loss),
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
        final_pairwise = float(cross_sign_pairwise_loss(raw, values, valid))
        rank_predictions = ranks.argmax(dim=1)
        selected_values = values.gather(1, rank_predictions[:, None]).squeeze(1)
        best_values = values.max(dim=1).values
        regrets = best_values - selected_values
        gate_predictions = gate > 0.0
        gate_act_recall = float(gate_predictions[act_targets].float().mean())
        gate_wait_recall = float((~gate_predictions[~act_targets]).float().mean())
        pair_metrics = cross_sign_metrics(raw, values, valid)
    summary = {
        "seed": seed,
        "epochs": d119.EPOCHS,
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
        "final_cross_sign_pairwise_loss": final_pairwise,
        "train_mean_proposal_regret": float(regrets.mean()),
        "train_median_proposal_regret": float(regrets.median()),
        "train_exact_best_rate": float((regrets == 0.0).float().mean()),
        "train_within_5_rate": float((regrets <= 5.0).float().mean()),
        "train_within_10_rate": float((regrets <= 10.0).float().mean()),
        "train_within_20_rate": float((regrets <= 20.0).float().mean()),
        "train_gate_act_recall": gate_act_recall,
        "train_gate_wait_recall": gate_wait_recall,
        "train_gate_balanced_accuracy": (
            gate_act_recall + gate_wait_recall
        ) / 2.0,
        **pair_metrics,
    }
    return model, summary


def model_gates(summary: dict) -> dict[str, bool]:
    gates = d118.model_fit_gates(summary)
    gates.update(
        {
            "cross_sign_pair_accuracy_at_least_70pct": (
                summary["train_cross_sign_pair_accuracy"] >= 0.70
            ),
            "cross_sign_winner_positive_rate_at_least_50pct": (
                summary["train_cross_sign_winner_positive_rate"] >= 0.50
            ),
        }
    )
    return gates


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
        ranks = d115.model_logits(model.ranker, train["x"])
        gate_values = d117.state_gate_logits(model, dataset)
        gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
        offset, calibration = d125.activity_calibrated_offset(
            list(train["baseline_by_task"]), dataset["root_order"], gate_values
        )
        metrics = d117.factorized_policy_metrics(
            train, ranks, gate_by_root, offset
        )
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

    d126_result = json.loads(d126.OUTPUT.read_text())
    development = d114.panel(
        d126.VALIDATION_ARMS,
        d126.VALIDATION_BASELINES,
        d126.VALIDATION_START,
        d126.VALIDATION_MAPS,
        d126_result["fresh_validation"]["elapsed_seconds"],
    )
    development_metrics = None
    development_gates = None
    development_pass = False
    if selected is not None:
        model = models[selected["seed"]]
        development_dataset = d118.soft_value_dataset(development)
        ranks = d115.model_logits(model.ranker, development["x"])
        gates = d117.state_gate_logits(model, development_dataset)
        gate_by_root = dict(
            zip(development_dataset["root_order"], gates, strict=True)
        )
        development_metrics = d117.factorized_policy_metrics(
            development,
            ranks,
            gate_by_root,
            selected["gate_offset"],
        )
        development_gates = d125.validation_gates(
            development_metrics, d123.control_crop_rate(development)
        )
        development_pass = all(development_gates.values())

    result = {
        "schema": "troll-farm-d130a-cross-sign-pairwise-soft-ranker-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "qualification_authority": False,
        "isolated_change": "coefficient-1 equal-root cross-sign pairwise logistic loss",
        "architecture": {
            "parameters": 6_626,
            "epochs": d119.EPOCHS,
            "soft_value_temperature": d118.TEMPERATURE,
            "pairwise_loss_coefficient": PAIRWISE_LOSS_COEFFICIENT,
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
            "freeze_fresh_d130_validation_protocol"
            if development_pass
            else "close_cross_sign_pairwise_without_fresh_simulation"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
