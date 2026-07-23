"""Focused unit tests for D73's recurrent actor and paired analysis."""

from __future__ import annotations

import numpy as np
import torch
from torch.distributions.categorical import Categorical

from cgauto.train_d73a_recurrent_ppo import (
    ACTOR_PARAMETERS,
    HIDDEN,
    OPENING_RECURRENT_ACTIONS,
    OPENING_RECURRENT_FEATURES,
    RecurrentActorCritic,
    actor_arrays,
    parameter_count,
)


def test_actor_initialization_is_reproducible_and_finite() -> None:
    left = actor_arrays()
    right = actor_arrays()
    assert all(np.array_equal(a, b) for a, b in zip(left, right, strict=True))
    assert all(np.isfinite(array).all() for array in left)
    model = RecurrentActorCritic()
    assert parameter_count(model.actor_parameters()) == ACTOR_PARAMETERS == 1_072


def test_sequence_resets_hidden_after_terminal() -> None:
    torch.manual_seed(7301)
    model = RecurrentActorCritic()
    features = torch.zeros((2, 1, OPENING_RECURRENT_FEATURES))
    masks = torch.ones((2, 1, OPENING_RECURRENT_ACTIONS), dtype=torch.uint8)
    actions = torch.zeros((2, 1), dtype=torch.int64)
    dones = torch.tensor([[1.0], [0.0]])
    initial = torch.ones((1, HIDDEN))
    logprob, entropy, value = model.sequence_statistics(
        features, masks, actions, dones, initial
    )
    assert logprob.shape == entropy.shape == value.shape == (2, 1)
    with torch.inference_mode():
        expected_hidden = model.actor_hidden(features[1], torch.zeros((1, HIDDEN)))
        expected_logits = model.actor_output(expected_hidden)
        expected = Categorical(logits=expected_logits).log_prob(actions[1])
    assert torch.allclose(logprob[1], expected)
