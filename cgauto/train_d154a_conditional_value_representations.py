#!/usr/bin/env python3
"""Train D154's frozen semantic representation ablations."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch
from torch import nn

from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d153a_conditional_value_policy as d153


CONTEXT_INDICES = (109, 154, 199, 244, 289, 334)


@dataclass(frozen=True)
class Representation:
    name: str
    include_state: bool
    action_indices: tuple[int, ...]

    @property
    def inputs(self) -> int:
        return (d153.STATE_FEATURES if self.include_state else 0) + len(
            self.action_indices
        )

    @property
    def parameters(self) -> int:
        return self.inputs * d153.HIDDEN + d153.HIDDEN + d153.HIDDEN + 1


REPRESENTATIONS = (
    Representation("full443", True, tuple(range(379))),
    Representation(
        "no_expert_ids379", True, tuple(range(45)) + tuple(range(109, 379))
    ),
    Representation(
        "semantic_context115", True, tuple(range(45)) + CONTEXT_INDICES
    ),
    Representation("semantic109", True, tuple(range(45))),
    Representation("semantic_supporters173", True, tuple(range(109))),
    Representation(
        "action_semantic_context51", False, tuple(range(45)) + CONTEXT_INDICES
    ),
)
BY_NAME = {representation.name: representation for representation in REPRESENTATIONS}


class RelativeValueScorer(nn.Module):
    def __init__(self, inputs: int) -> None:
        super().__init__()
        self.inputs = inputs
        self.hidden = nn.Linear(inputs, d153.HIDDEN)
        self.output = nn.Linear(d153.HIDDEN, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(torch.relu(self.hidden(features))).squeeze(-1)


def represented_features(dataset: dict, representation: Representation) -> np.ndarray:
    actions = np.asarray(dataset["action_features"], dtype=np.float32)
    selected = actions[:, :, representation.action_indices]
    if representation.include_state:
        states = np.asarray(dataset["state_features"], dtype=np.float32)
        expanded = np.broadcast_to(states[:, None, :], (*actions.shape[:2], 64))
        selected = np.concatenate((expanded, selected), axis=2)
    result = np.ascontiguousarray(selected, dtype=np.float32)
    if result.shape != (*actions.shape[:2], representation.inputs):
        raise RuntimeError("D154 represented feature shape drift")
    if not np.isfinite(result).all():
        raise RuntimeError("D154 represented features are nonfinite")
    return result


def relative_scores(model: RelativeValueScorer, features: torch.Tensor) -> torch.Tensor:
    raw = model(features.reshape(-1, model.inputs)).reshape(features.shape[:2])
    relative = raw - raw[:, :1]
    if not bool(torch.all(relative[:, 0] == 0.0)):
        raise RuntimeError("D154 relative control score is not exact zero")
    return relative


def predict_margin_values(
    model: RelativeValueScorer,
    dataset: dict,
    representation: Representation,
) -> np.ndarray:
    features = torch.from_numpy(represented_features(dataset, representation))
    valid = torch.from_numpy(np.asarray(dataset["valid"], dtype=np.bool_))
    model.eval()
    with torch.no_grad():
        scores = relative_scores(model, features)
        scores = scores.masked_fill(~valid, float("-inf")) * d153.MARGIN_SCALE
    result = scores.detach().cpu().numpy().astype(np.float32, copy=False)
    mask = np.asarray(dataset["valid"], dtype=np.bool_)
    if not np.isfinite(result[mask]).all() or not np.all(result[:, 0] == 0.0):
        raise RuntimeError("D154 predicted values are invalid")
    return result


def train_model(
    dataset: dict,
    representation: Representation,
    seed: int,
    *,
    epochs: int = d153.EPOCHS,
    batch_size: int = d153.BATCH_SIZE,
    threads: int = d153.CPU_THREADS,
) -> tuple[RelativeValueScorer, dict]:
    d115.configure_torch(threads)
    features = torch.from_numpy(represented_features(dataset, representation))
    valid = torch.from_numpy(np.asarray(dataset["valid"], dtype=np.bool_))
    targets = torch.from_numpy(
        np.asarray(dataset["target_values"], dtype=np.float32) / d153.MARGIN_SCALE
    )
    if len(features) == 0 or not bool(torch.all(valid[:, 0])) or not bool(
        torch.all(targets[:, 0] == 0.0)
    ):
        raise RuntimeError("D154 training dataset/control drift")
    torch.manual_seed(seed)
    model = RelativeValueScorer(representation.inputs)
    if d115.parameter_count(model) != representation.parameters:
        raise RuntimeError("D154 representation parameter budget drift")
    optimizer = torch.optim.Adam(
        model.parameters(), lr=d153.LEARNING_RATE, weight_decay=d153.WEIGHT_DECAY
    )
    generator = np.random.Generator(np.random.PCG64(seed))
    losses = []
    rank_losses = []
    regression_losses = []
    model.train()
    for _ in range(epochs):
        order = generator.permutation(len(features))
        totals = np.zeros(3, dtype=np.float64)
        seen = 0
        for start in range(0, len(order), batch_size):
            indices = torch.from_numpy(order[start : start + batch_size])
            optimizer.zero_grad(set_to_none=True)
            relative = relative_scores(model, features[indices])
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
        relative = relative_scores(model, features)
        final, final_rank, final_regression = d153.grouped_losses(
            relative, targets, valid
        )
    return model, {
        "representation": representation.name,
        "inputs": representation.inputs,
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
