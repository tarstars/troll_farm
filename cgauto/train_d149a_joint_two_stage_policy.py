#!/usr/bin/env python3
"""Train a slim winner-conditioned controller on D149 structural examples."""

from __future__ import annotations

from collections import Counter

import numpy as np
import torch
from torch.nn import functional

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d135a_winner_conditioned_action_gate_q6 as d135


RANK_EPOCHS = 60
GATE_EPOCHS = 80
BATCH_SIZE = 128
LEARNING_RATE = 1.0e-3
WEIGHT_DECAY = 1.0e-4
CPU_THREADS = 20
PROPOSAL_NORMALIZER = 64.0


def subset(dataset: dict, indices: np.ndarray) -> dict:
    indices = np.asarray(indices, dtype=np.int64)
    return {
        key: value[indices]
        for key, value in dataset.items()
        if key
        in {
            "action_features",
            "valid",
            "candidate_slots",
            "state_features",
            "rank_targets",
            "gate_targets",
            "folds",
        }
    } | {
        "tasks": [dataset["tasks"][index] for index in indices],
        "stages": [dataset["stages"][index] for index in indices],
    }


def tensors(dataset: dict) -> dict:
    return {
        "actions": torch.from_numpy(np.asarray(dataset["action_features"], dtype=np.float32)),
        "valid": torch.from_numpy(np.asarray(dataset["valid"], dtype=np.bool_)),
        "states": torch.from_numpy(np.asarray(dataset["state_features"], dtype=np.float32)),
        "rank_targets": torch.from_numpy(np.asarray(dataset["rank_targets"], dtype=np.int64)),
        "gate_targets": torch.from_numpy(np.asarray(dataset["gate_targets"], dtype=np.bool_)),
    }


def train_ranker(
    dataset: dict,
    seed: int,
    *,
    epochs: int = RANK_EPOCHS,
    batch_size: int = BATCH_SIZE,
) -> tuple[d115.CompactActClassifier, dict]:
    data = tensors(dataset)
    trainable = torch.nonzero(
        data["rank_targets"] >= 0, as_tuple=False
    ).squeeze(1)
    if not len(trainable):
        raise ValueError("D149 ranker requires active action groups")
    torch.manual_seed(seed)
    ranker = d115.CompactActClassifier()
    optimizer = torch.optim.Adam(
        ranker.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
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
            logits = d117.proposal_logits(
                ranker, data["actions"][indices], data["valid"][indices]
            )
            loss = functional.cross_entropy(logits, data["rank_targets"][indices])
            loss.backward()
            optimizer.step()
            total += float(loss.detach()) * len(indices)
            seen += len(indices)
        losses.append(total / seen)
    ranker.eval()
    with torch.no_grad():
        logits = d117.proposal_logits(
            ranker, data["actions"][trainable], data["valid"][trainable]
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
    ranker: d115.CompactActClassifier, dataset: dict
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    data = tensors(dataset)
    with torch.no_grad():
        logits = d117.proposal_logits(ranker, data["actions"], data["valid"])
        selected = logits.argmax(dim=1)
        roots = torch.arange(len(selected))
        chosen_actions = data["actions"][roots, selected]
        embedding = torch.relu(ranker.hidden(chosen_actions))
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
                counts.float() / PROPOSAL_NORMALIZER,
            ),
            dim=1,
        )
        context = torch.cat((data["states"], embedding, confidence), dim=1)
    if context.shape != (len(selected), d135.GATE_INPUTS):
        raise RuntimeError("D149 winner context shape drift")
    if not bool(torch.isfinite(context).all()):
        raise RuntimeError("D149 winner context is nonfinite")
    return context, selected, logits


def class_balanced_task_weights(tasks: list, targets: np.ndarray) -> np.ndarray:
    targets = np.asarray(targets, dtype=np.bool_)
    if not targets.any() or targets.all():
        raise ValueError("D149 gate requires act and wait groups")
    counts = Counter(tasks)
    weights = np.asarray([1.0 / counts[task] for task in tasks], dtype=np.float64)
    for label in (False, True):
        mask = targets == label
        weights[mask] *= 0.5 / weights[mask].sum()
    if not np.isclose(weights[targets].sum(), 0.5) or not np.isclose(
        weights[~targets].sum(), 0.5
    ):
        raise RuntimeError("D149 gate class balance drift")
    return weights.astype(np.float32)


def train_gate(
    ranker: d115.CompactActClassifier,
    dataset: dict,
    seed: int,
    *,
    epochs: int = GATE_EPOCHS,
    batch_size: int = BATCH_SIZE,
) -> tuple[d135.WinnerController, dict]:
    ranker.requires_grad_(False)
    ranker_hash = d115.canonical_model_hash(ranker)
    torch.manual_seed(seed)
    model = d135.WinnerController(ranker)
    if d115.parameter_count(model) != 6_786:
        raise RuntimeError("D149 parameter budget drift")
    context, _, _ = winner_context(model.ranker, dataset)
    targets = torch.from_numpy(np.asarray(dataset["gate_targets"], dtype=np.float32))
    weights = torch.from_numpy(
        class_balanced_task_weights(dataset["tasks"], dataset["gate_targets"])
    )
    optimizer = torch.optim.Adam(
        model.gate.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
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
        raise RuntimeError("D149 gate training changed its ranker")
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


def structural_metrics(model: d135.WinnerController, dataset: dict) -> dict:
    data = tensors(dataset)
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
    rank_epochs: int = RANK_EPOCHS,
    gate_epochs: int = GATE_EPOCHS,
    threads: int = CPU_THREADS,
) -> tuple[d135.WinnerController, dict]:
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
