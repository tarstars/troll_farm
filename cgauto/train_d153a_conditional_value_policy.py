#!/usr/bin/env python3
"""Train D153's compact state-conditioned relative-value scorer."""

from __future__ import annotations

import numpy as np
import torch
from torch import nn
from torch.nn import functional

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115


STATE_FEATURES = 64
ACTION_FEATURES = 379
INPUTS = STATE_FEATURES + ACTION_FEATURES
HIDDEN = 16
PARAMETERS = 7_121
EPOCHS = 80
BATCH_SIZE = 64
LEARNING_RATE = 1.0e-3
WEIGHT_DECAY = 1.0e-4
CPU_THREADS = 20
MARGIN_SCALE = 50.0
SOFT_TARGET_TEMPERATURE_MARGIN = 10.0
SOFT_TEMPERATURE_NORMALIZED = SOFT_TARGET_TEMPERATURE_MARGIN / MARGIN_SCALE


class ConditionalValueScorer(nn.Module):
    """The frozen 443 -> 16 ReLU -> 1 D153 scorer."""

    def __init__(self) -> None:
        super().__init__()
        self.hidden = nn.Linear(INPUTS, HIDDEN)
        self.output = nn.Linear(HIDDEN, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(torch.relu(self.hidden(features))).squeeze(-1)


ARRAY_KEYS = {
    "action_features",
    "state_features",
    "valid",
    "candidate_slots",
    "target_values",
    "terminal_margins",
    "terminal_own_scores",
    "terminal_opponent_scores",
    "terminal_own_workers",
    "terminal_own_created_crops",
    "folds",
    "target_active",
}
LIST_KEYS = {"tasks", "opponents"}


def subset(dataset: dict, indices: np.ndarray) -> dict:
    indices = np.asarray(indices, dtype=np.int64)
    result = {
        key: value[indices]
        for key, value in dataset.items()
        if key in ARRAY_KEYS
    }
    result.update(
        {
            key: [dataset[key][index] for index in indices]
            for key in LIST_KEYS
            if key in dataset
        }
    )
    return result


def tensors(dataset: dict) -> dict[str, torch.Tensor]:
    return {
        "actions": torch.from_numpy(
            np.asarray(dataset["action_features"], dtype=np.float32)
        ),
        "states": torch.from_numpy(
            np.asarray(dataset["state_features"], dtype=np.float32)
        ),
        "valid": torch.from_numpy(np.asarray(dataset["valid"], dtype=np.bool_)),
        "targets": torch.from_numpy(
            np.asarray(dataset["target_values"], dtype=np.float32) / MARGIN_SCALE
        ),
    }


def scorer_inputs(actions: torch.Tensor, states: torch.Tensor) -> torch.Tensor:
    if actions.ndim != 3 or states.shape != (actions.shape[0], STATE_FEATURES):
        raise ValueError("D153 action/state shape mismatch")
    expanded = states[:, None, :].expand(-1, actions.shape[1], -1)
    result = torch.cat((expanded, actions), dim=2)
    if result.shape != (*actions.shape[:2], INPUTS):
        raise RuntimeError("D153 scorer input shape drift")
    return result


def relative_scores(
    model: ConditionalValueScorer,
    actions: torch.Tensor,
    states: torch.Tensor,
) -> torch.Tensor:
    inputs = scorer_inputs(actions, states)
    raw = model(inputs.reshape(-1, INPUTS)).reshape(inputs.shape[:2])
    relative = raw - raw[:, :1]
    if not bool(torch.all(relative[:, 0] == 0.0)):
        raise RuntimeError("D153 relative control score is not exact zero")
    return relative


def grouped_losses(
    relative: torch.Tensor,
    targets: torch.Tensor,
    valid: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    if relative.shape != targets.shape or relative.shape != valid.shape:
        raise ValueError("D153 grouped loss shape mismatch")
    temperature = SOFT_TEMPERATURE_NORMALIZED
    target_logits = (targets / temperature).masked_fill(~valid, float("-inf"))
    prediction_logits = (relative / temperature).masked_fill(
        ~valid, float("-inf")
    )
    soft_targets = torch.softmax(target_logits, dim=1)
    log_probabilities = torch.log_softmax(prediction_logits, dim=1)
    safe_log_probabilities = torch.where(
        valid, log_probabilities, torch.zeros_like(log_probabilities)
    )
    rank_by_group = -(soft_targets * safe_log_probabilities).sum(dim=1)
    raw_regression = functional.smooth_l1_loss(
        relative, targets, reduction="none"
    )
    regression_by_group = (raw_regression * valid).sum(dim=1) / valid.sum(dim=1)
    rank_loss = rank_by_group.mean()
    regression_loss = regression_by_group.mean()
    return rank_loss + regression_loss, rank_loss, regression_loss


def predict_margin_values(model: ConditionalValueScorer, dataset: dict) -> np.ndarray:
    data = tensors(dataset)
    model.eval()
    with torch.no_grad():
        scores = relative_scores(model, data["actions"], data["states"])
        scores = scores.masked_fill(~data["valid"], float("-inf")) * MARGIN_SCALE
    result = scores.detach().cpu().numpy().astype(np.float32, copy=False)
    valid = np.asarray(dataset["valid"], dtype=np.bool_)
    if not np.isfinite(result[valid]).all() or not np.all(result[:, 0] == 0.0):
        raise RuntimeError("D153 predicted values are invalid")
    return result


def structural_metrics(model: ConditionalValueScorer, dataset: dict) -> dict:
    predicted = predict_margin_values(model, dataset)
    valid = np.asarray(dataset["valid"], dtype=np.bool_)
    targets = np.asarray(dataset["target_values"], dtype=np.float32)
    selected = predicted.argmax(axis=1)
    roots = np.arange(len(selected))
    oracle = targets.copy()
    oracle[~valid] = -np.inf
    oracle_selected = oracle.argmax(axis=1)
    absolute_error = np.abs(predicted[valid] - targets[valid])
    return {
        "groups": len(selected),
        "actions": int(valid.sum()),
        "control_scores_exact_zero": int(np.sum(predicted[:, 0] == 0.0)),
        "selected_exact_oracle_rate": float(
            np.mean(selected == oracle_selected)
        ),
        "selected_mean_target_value": float(targets[roots, selected].mean()),
        "mean_absolute_action_value_error": float(absolute_error.mean()),
    }


def train_model(
    dataset: dict,
    seed: int,
    *,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    threads: int = CPU_THREADS,
) -> tuple[ConditionalValueScorer, dict]:
    d115.configure_torch(threads)
    data = tensors(dataset)
    if len(data["states"]) == 0:
        raise ValueError("D153 cannot train on an empty dataset")
    if not bool(torch.all(data["valid"][:, 0])) or not bool(
        torch.all(data["targets"][:, 0] == 0.0)
    ):
        raise RuntimeError("D153 training controls are invalid")
    torch.manual_seed(seed)
    model = ConditionalValueScorer()
    if d115.parameter_count(model) != PARAMETERS:
        raise RuntimeError("D153 parameter budget drift")
    optimizer = torch.optim.Adam(
        model.parameters(), lr=LEARNING_RATE, weight_decay=WEIGHT_DECAY
    )
    generator = np.random.Generator(np.random.PCG64(seed))
    epoch_losses = []
    epoch_rank_losses = []
    epoch_regression_losses = []
    model.train()
    for _ in range(epochs):
        order = generator.permutation(len(data["states"]))
        combined_sum = 0.0
        rank_sum = 0.0
        regression_sum = 0.0
        seen = 0
        for start in range(0, len(order), batch_size):
            indices = torch.from_numpy(order[start : start + batch_size])
            optimizer.zero_grad(set_to_none=True)
            relative = relative_scores(
                model, data["actions"][indices], data["states"][indices]
            )
            loss, rank_loss, regression_loss = grouped_losses(
                relative, data["targets"][indices], data["valid"][indices]
            )
            loss.backward()
            optimizer.step()
            count = len(indices)
            combined_sum += float(loss.detach()) * count
            rank_sum += float(rank_loss.detach()) * count
            regression_sum += float(regression_loss.detach()) * count
            seen += count
        epoch_losses.append(combined_sum / seen)
        epoch_rank_losses.append(rank_sum / seen)
        epoch_regression_losses.append(regression_sum / seen)
    model.eval()
    with torch.no_grad():
        relative = relative_scores(model, data["actions"], data["states"])
        final_loss, final_rank, final_regression = grouped_losses(
            relative, data["targets"], data["valid"]
        )
    return model, {
        "seed": seed,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": LEARNING_RATE,
        "weight_decay": WEIGHT_DECAY,
        "cpu_threads": threads,
        "groups": len(data["states"]),
        "actions": int(data["valid"].sum()),
        "parameters": d115.parameter_count(model),
        "model_hash": d115.canonical_model_hash(model),
        "first_epoch_loss": epoch_losses[0],
        "last_epoch_loss": epoch_losses[-1],
        "first_epoch_rank_loss": epoch_rank_losses[0],
        "last_epoch_rank_loss": epoch_rank_losses[-1],
        "first_epoch_regression_loss": epoch_regression_losses[0],
        "last_epoch_regression_loss": epoch_regression_losses[-1],
        "final_full_loss": float(final_loss),
        "final_full_rank_loss": float(final_rank),
        "final_full_regression_loss": float(final_regression),
        "structural": structural_metrics(model, dataset),
    }
