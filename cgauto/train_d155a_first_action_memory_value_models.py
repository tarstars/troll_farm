#!/usr/bin/env python3
"""Train D155's concatenated and bilinear first-action-memory scorers."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
import torch
from torch import nn

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d153a_conditional_value_policy as d153
from cgauto import train_d154a_conditional_value_representations as d154


COMPACT_INDICES = tuple(range(45)) + d154.CONTEXT_INDICES


@dataclass(frozen=True)
class Architecture:
    name: str
    kind: str
    action_indices: tuple[int, ...]
    include_first: bool

    @property
    def action_inputs(self) -> int:
        return len(self.action_indices)

    @property
    def context_inputs(self) -> int:
        return d153.STATE_FEATURES + (
            self.action_inputs if self.include_first else 0
        )

    @property
    def parameters(self) -> int:
        if self.kind == "concat":
            inputs = self.context_inputs + self.action_inputs
            return inputs * d153.HIDDEN + d153.HIDDEN + d153.HIDDEN + 1
        if self.kind == "bilinear":
            return (
                self.context_inputs * d153.HIDDEN
                + d153.HIDDEN
                + self.action_inputs * d153.HIDDEN
                + d153.HIDDEN
            )
        raise RuntimeError(f"unknown D155 architecture kind: {self.kind}")


ARCHITECTURES = (
    Architecture("snapshot_compact", "concat", COMPACT_INDICES, False),
    Architecture("history_concat_compact", "concat", COMPACT_INDICES, True),
    Architecture("history_bilinear_compact", "bilinear", COMPACT_INDICES, True),
    Architecture("history_concat_full", "concat", tuple(range(379)), True),
    Architecture("history_bilinear_full", "bilinear", tuple(range(379)), True),
)
BY_NAME = {architecture.name: architecture for architecture in ARCHITECTURES}


class ConcatScorer(nn.Module):
    def __init__(self, inputs: int) -> None:
        super().__init__()
        self.inputs = inputs
        self.hidden = nn.Linear(inputs, d153.HIDDEN)
        self.output = nn.Linear(d153.HIDDEN, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(torch.relu(self.hidden(features))).squeeze(-1)


class BilinearScorer(nn.Module):
    def __init__(self, context_inputs: int, action_inputs: int) -> None:
        super().__init__()
        self.context_inputs = context_inputs
        self.action_inputs = action_inputs
        self.context = nn.Linear(context_inputs, d153.HIDDEN)
        self.action = nn.Linear(action_inputs, d153.HIDDEN)

    def forward(
        self, context: torch.Tensor, actions: torch.Tensor
    ) -> torch.Tensor:
        context_embedding = torch.relu(self.context(context))[:, None, :]
        action_embedding = torch.relu(
            self.action(actions.reshape(-1, self.action_inputs))
        ).reshape(*actions.shape[:2], d153.HIDDEN)
        return (context_embedding * action_embedding).sum(dim=2) / math.sqrt(
            d153.HIDDEN
        )


def subset(dataset: dict, indices: np.ndarray) -> dict:
    indices = np.asarray(indices, dtype=np.int64)
    result = d153.subset(dataset, indices)
    for key in ("first_action_features", "first_state_features", "first_slots"):
        result[key] = dataset[key][indices]
    return result


def prepared_features(dataset: dict, architecture: Architecture) -> dict[str, np.ndarray]:
    states = np.asarray(dataset["state_features"], dtype=np.float32)
    actions = np.asarray(dataset["action_features"], dtype=np.float32)[
        :, :, architecture.action_indices
    ]
    context_parts = [states]
    if architecture.include_first:
        first = np.asarray(dataset["first_action_features"], dtype=np.float32)[
            :, architecture.action_indices
        ]
        context_parts.append(first)
    context = np.ascontiguousarray(np.concatenate(context_parts, axis=1))
    actions = np.ascontiguousarray(actions)
    if context.shape != (len(states), architecture.context_inputs):
        raise RuntimeError("D155 context feature shape drift")
    if actions.shape != (
        len(states),
        dataset["action_features"].shape[1],
        architecture.action_inputs,
    ):
        raise RuntimeError("D155 action feature shape drift")
    if architecture.kind == "concat":
        expanded = np.broadcast_to(
            context[:, None, :], (*actions.shape[:2], architecture.context_inputs)
        )
        features = np.ascontiguousarray(
            np.concatenate((expanded, actions), axis=2), dtype=np.float32
        )
        return {"features": features}
    return {"context": context, "actions": actions}


def make_model(architecture: Architecture) -> nn.Module:
    if architecture.kind == "concat":
        return ConcatScorer(architecture.context_inputs + architecture.action_inputs)
    return BilinearScorer(architecture.context_inputs, architecture.action_inputs)


def raw_scores(model: nn.Module, prepared: dict[str, torch.Tensor]) -> torch.Tensor:
    if isinstance(model, ConcatScorer):
        features = prepared["features"]
        return model(features.reshape(-1, model.inputs)).reshape(features.shape[:2])
    if isinstance(model, BilinearScorer):
        return model(prepared["context"], prepared["actions"])
    raise TypeError(f"unsupported D155 model: {type(model)!r}")


def relative_scores(model: nn.Module, prepared: dict[str, torch.Tensor]) -> torch.Tensor:
    raw = raw_scores(model, prepared)
    relative = raw - raw[:, :1]
    if not bool(torch.all(relative[:, 0] == 0.0)):
        raise RuntimeError("D155 relative control score is not exact zero")
    return relative


def tensor_features(prepared: dict[str, np.ndarray]) -> dict[str, torch.Tensor]:
    return {key: torch.from_numpy(value) for key, value in prepared.items()}


def batch_features(
    prepared: dict[str, torch.Tensor], indices: torch.Tensor
) -> dict[str, torch.Tensor]:
    return {key: value[indices] for key, value in prepared.items()}


def predict_margin_values(model: nn.Module, dataset: dict, architecture: Architecture) -> np.ndarray:
    prepared = tensor_features(prepared_features(dataset, architecture))
    valid = torch.from_numpy(np.asarray(dataset["valid"], dtype=np.bool_))
    model.eval()
    with torch.no_grad():
        scores = relative_scores(model, prepared)
        scores = scores.masked_fill(~valid, float("-inf")) * d153.MARGIN_SCALE
    result = scores.detach().cpu().numpy().astype(np.float32, copy=False)
    mask = np.asarray(dataset["valid"], dtype=np.bool_)
    if not np.isfinite(result[mask]).all() or not np.all(result[:, 0] == 0.0):
        raise RuntimeError("D155 predicted values are invalid")
    return result


def train_model(
    dataset: dict,
    architecture: Architecture,
    seed: int,
    *,
    epochs: int = d153.EPOCHS,
    batch_size: int = d153.BATCH_SIZE,
    threads: int = d153.CPU_THREADS,
) -> tuple[nn.Module, dict]:
    d115.configure_torch(threads)
    prepared = tensor_features(prepared_features(dataset, architecture))
    valid = torch.from_numpy(np.asarray(dataset["valid"], dtype=np.bool_))
    targets = torch.from_numpy(
        np.asarray(dataset["target_values"], dtype=np.float32) / d153.MARGIN_SCALE
    )
    torch.manual_seed(seed)
    model = make_model(architecture)
    if d115.parameter_count(model) != architecture.parameters:
        raise RuntimeError("D155 architecture parameter budget drift")
    optimizer = torch.optim.Adam(
        model.parameters(), lr=d153.LEARNING_RATE, weight_decay=d153.WEIGHT_DECAY
    )
    generator = np.random.Generator(np.random.PCG64(seed))
    losses = []
    rank_losses = []
    regression_losses = []
    model.train()
    for _ in range(epochs):
        order = generator.permutation(len(targets))
        totals = np.zeros(3, dtype=np.float64)
        seen = 0
        for start in range(0, len(order), batch_size):
            indices = torch.from_numpy(order[start : start + batch_size])
            optimizer.zero_grad(set_to_none=True)
            relative = relative_scores(model, batch_features(prepared, indices))
            combined, rank, regression = d153.grouped_losses(
                relative, targets[indices], valid[indices]
            )
            combined.backward()
            optimizer.step()
            count = len(indices)
            totals += np.asarray(
                [float(combined.detach()), float(rank.detach()), float(regression.detach())]
            ) * count
            seen += count
        losses.append(float(totals[0] / seen))
        rank_losses.append(float(totals[1] / seen))
        regression_losses.append(float(totals[2] / seen))
    model.eval()
    with torch.no_grad():
        relative = relative_scores(model, prepared)
        final, final_rank, final_regression = d153.grouped_losses(
            relative, targets, valid
        )
    return model, {
        "architecture": architecture.name,
        "kind": architecture.kind,
        "context_inputs": architecture.context_inputs,
        "action_inputs": architecture.action_inputs,
        "parameters": d115.parameter_count(model),
        "seed": seed,
        "epochs": epochs,
        "batch_size": batch_size,
        "cpu_threads": threads,
        "model_hash": d115.canonical_model_hash(model),
        "first_epoch_loss": losses[0],
        "last_epoch_loss": losses[-1],
        "first_epoch_rank_loss": rank_losses[0],
        "last_epoch_rank_loss": rank_losses[-1],
        "first_epoch_regression_loss": regression_losses[0],
        "last_epoch_regression_loss": regression_losses[-1],
        "final_full_loss": float(final),
        "final_full_rank_loss": float(final_rank),
        "final_full_regression_loss": float(final_regression),
    }
