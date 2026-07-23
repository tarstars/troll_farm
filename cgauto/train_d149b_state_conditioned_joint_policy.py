#!/usr/bin/env python3
"""Train D149b's minimally state-conditioned two-stage controller."""

from __future__ import annotations

import numpy as np
import torch
from torch import nn
from torch.nn import functional

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d135a_winner_conditioned_action_gate_q6 as d135
from cgauto import train_d149a_joint_two_stage_policy as d149a


STATE_FEATURES = 64
ACTION_FEATURES = 379
RANK_INPUTS = STATE_FEATURES + ACTION_FEATURES
RANK_HIDDEN = 16
PARAMETERS = 7_810


class StateConditionedRanker(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.hidden = nn.Linear(RANK_INPUTS, RANK_HIDDEN)
        self.output = nn.Linear(RANK_HIDDEN, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(torch.relu(self.hidden(features))).squeeze(-1)


class StateWinnerController(nn.Module):
    def __init__(self, ranker: StateConditionedRanker) -> None:
        super().__init__()
        self.ranker = ranker
        self.gate = d135.WinnerGate()


def proposal_inputs(
    actions: torch.Tensor, states: torch.Tensor
) -> torch.Tensor:
    if actions.ndim != 3 or states.shape != (actions.shape[0], STATE_FEATURES):
        raise ValueError("D149b action/state shape mismatch")
    expanded = states[:, None, :].expand(-1, actions.shape[1], -1)
    result = torch.cat((expanded, actions), dim=2)
    if result.shape != (*actions.shape[:2], RANK_INPUTS):
        raise RuntimeError("D149b concatenated proposal shape drift")
    return result


def proposal_logits(
    ranker: StateConditionedRanker,
    actions: torch.Tensor,
    states: torch.Tensor,
    valid: torch.Tensor,
) -> torch.Tensor:
    features = proposal_inputs(actions, states)
    logits = ranker(features.reshape(-1, RANK_INPUTS)).reshape(features.shape[:2])
    return logits.masked_fill(~valid, float("-inf"))


def train_ranker(
    dataset: dict,
    seed: int,
    *,
    epochs: int = d149a.RANK_EPOCHS,
    batch_size: int = d149a.BATCH_SIZE,
) -> tuple[StateConditionedRanker, dict]:
    data = d149a.tensors(dataset)
    trainable = torch.nonzero(data["rank_targets"] >= 0, as_tuple=False).squeeze(1)
    if not len(trainable):
        raise ValueError("D149b ranker requires active action groups")
    torch.manual_seed(seed)
    ranker = StateConditionedRanker()
    optimizer = torch.optim.Adam(
        ranker.parameters(),
        lr=d149a.LEARNING_RATE,
        weight_decay=d149a.WEIGHT_DECAY,
    )
    generator = np.random.Generator(np.random.PCG64(seed))
    losses = []
    ranker.train()
    for _ in range(epochs):
        order = trainable[torch.from_numpy(generator.permutation(len(trainable)))]
        total = 0.0
        seen = 0
        for start in range(0, len(order), batch_size):
            indices = order[start : start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            logits = proposal_logits(
                ranker,
                data["actions"][indices],
                data["states"][indices],
                data["valid"][indices],
            )
            loss = functional.cross_entropy(logits, data["rank_targets"][indices])
            loss.backward()
            optimizer.step()
            total += float(loss.detach()) * len(indices)
            seen += len(indices)
        losses.append(total / seen)
    ranker.eval()
    with torch.no_grad():
        logits = proposal_logits(
            ranker,
            data["actions"][trainable],
            data["states"][trainable],
            data["valid"][trainable],
        )
        predicted = logits.argmax(dim=1)
        targets = data["rank_targets"][trainable]
    return ranker, {
        "seed": seed,
        "epochs": epochs,
        "groups": len(trainable),
        "first_epoch_loss": losses[0],
        "last_epoch_loss": losses[-1],
        "accuracy": float((predicted == targets).float().mean()),
        "model_hash": d115.canonical_model_hash(ranker),
        "parameters": d115.parameter_count(ranker),
    }


def winner_context(
    ranker: StateConditionedRanker, dataset: dict
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    data = d149a.tensors(dataset)
    with torch.no_grad():
        inputs = proposal_inputs(data["actions"], data["states"])
        logits = ranker(inputs.reshape(-1, RANK_INPUTS)).reshape(inputs.shape[:2])
        logits = logits.masked_fill(~data["valid"], float("-inf"))
        selected = logits.argmax(dim=1)
        roots = torch.arange(len(selected))
        chosen_inputs = inputs[roots, selected]
        embedding = torch.relu(ranker.hidden(chosen_inputs))
        winner = logits[roots, selected]
        counts = data["valid"].sum(dim=1)
        second = winner.clone()
        multiple = counts >= 2
        if bool(multiple.any()):
            second[multiple] = logits[multiple].topk(2, dim=1).values[:, 1]
        confidence = torch.stack(
            (
                winner,
                winner - second,
                winner - torch.logsumexp(logits, dim=1),
                counts.float() / d149a.PROPOSAL_NORMALIZER,
            ),
            dim=1,
        )
        context = torch.cat((data["states"], embedding, confidence), dim=1)
    if context.shape != (len(selected), d135.GATE_INPUTS):
        raise RuntimeError("D149b winner context shape drift")
    if not bool(torch.isfinite(context).all()):
        raise RuntimeError("D149b winner context is nonfinite")
    return context, selected, logits


def train_gate(
    ranker: StateConditionedRanker,
    dataset: dict,
    seed: int,
    *,
    epochs: int = d149a.GATE_EPOCHS,
    batch_size: int = d149a.BATCH_SIZE,
) -> tuple[StateWinnerController, dict]:
    ranker.requires_grad_(False)
    ranker_hash = d115.canonical_model_hash(ranker)
    torch.manual_seed(seed)
    model = StateWinnerController(ranker)
    if d115.parameter_count(model) != PARAMETERS:
        raise RuntimeError("D149b parameter budget drift")
    context, _, _ = winner_context(model.ranker, dataset)
    targets = torch.from_numpy(
        np.asarray(dataset["gate_targets"], dtype=np.float32)
    )
    weights = torch.from_numpy(
        d149a.class_balanced_task_weights(
            dataset["tasks"], dataset["gate_targets"]
        )
    )
    optimizer = torch.optim.Adam(
        model.gate.parameters(),
        lr=d149a.LEARNING_RATE,
        weight_decay=d149a.WEIGHT_DECAY,
    )
    generator = np.random.Generator(np.random.PCG64(seed))
    losses = []
    model.gate.train()
    for _ in range(epochs):
        order = torch.from_numpy(generator.permutation(len(targets)))
        weighted = 0.0
        mass = 0.0
        for start in range(0, len(order), batch_size):
            indices = order[start : start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            logits = model.gate(context[indices])
            raw = functional.binary_cross_entropy_with_logits(
                logits, targets[indices], reduction="none"
            )
            denominator = weights[indices].sum()
            loss = (raw * weights[indices]).sum() / denominator
            loss.backward()
            optimizer.step()
            weighted += float((raw.detach() * weights[indices]).sum())
            mass += float(denominator)
        losses.append(weighted / mass)
    model.eval()
    with torch.no_grad():
        logits = model.gate(context)
        predicted = logits > 0.0
        truth = targets.bool()
        act_recall = float(predicted[truth].float().mean())
        wait_recall = float((~predicted[~truth]).float().mean())
    if d115.canonical_model_hash(model.ranker) != ranker_hash:
        raise RuntimeError("D149b gate training changed its ranker")
    return model, {
        "seed": seed,
        "epochs": epochs,
        "groups": len(targets),
        "first_epoch_loss": losses[0],
        "last_epoch_loss": losses[-1],
        "act_recall_at_zero": act_recall,
        "wait_recall_at_zero": wait_recall,
        "balanced_accuracy_at_zero": (act_recall + wait_recall) / 2.0,
        "model_hash": d115.canonical_model_hash(model),
        "parameters": d115.parameter_count(model),
    }


def structural_metrics(model: StateWinnerController, dataset: dict) -> dict:
    data = d149a.tensors(dataset)
    context, selected, _ = winner_context(model.ranker, dataset)
    with torch.no_grad():
        gate_logits = model.gate(context)
    rank_mask = data["rank_targets"] >= 0
    truth = data["gate_targets"]
    predicted_act = gate_logits > 0.0
    result = {
        "groups": len(truth),
        "rank_groups": int(rank_mask.sum()),
        "rank_accuracy": float(
            (selected[rank_mask] == data["rank_targets"][rank_mask]).float().mean()
        ),
        "gate_act_recall_at_zero": float(predicted_act[truth].float().mean()),
        "gate_wait_recall_at_zero": float((~predicted_act[~truth]).float().mean()),
    }
    result["gate_balanced_accuracy_at_zero"] = (
        result["gate_act_recall_at_zero"] + result["gate_wait_recall_at_zero"]
    ) / 2.0
    for stage in ("first", "second"):
        mask = torch.tensor(
            [name == stage for name in dataset["stages"]], dtype=torch.bool
        ) & rank_mask
        result[f"{stage}_rank_accuracy"] = float(
            (selected[mask] == data["rank_targets"][mask]).float().mean()
        )
    return result


def train_model(
    dataset: dict,
    rank_seed: int,
    gate_seed: int,
    *,
    rank_epochs: int = d149a.RANK_EPOCHS,
    gate_epochs: int = d149a.GATE_EPOCHS,
    threads: int = d149a.CPU_THREADS,
) -> tuple[StateWinnerController, dict]:
    d115.configure_torch(threads)
    ranker, rank_summary = train_ranker(
        dataset, rank_seed, epochs=rank_epochs
    )
    model, gate_summary = train_gate(
        ranker, dataset, gate_seed, epochs=gate_epochs
    )
    return model, {
        "ranker": rank_summary,
        "gate": gate_summary,
        "structural": structural_metrics(model, dataset),
    }
