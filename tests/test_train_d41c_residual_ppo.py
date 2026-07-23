from __future__ import annotations

import numpy as np
import torch

from cgauto.train_d41c_residual_ppo import (
    ExactPriorResidualActorCritic,
    actor_parameter_count,
    compute_advantages,
    critic_parameter_count,
    pack_observations,
)


def test_zero_residual_argmax_is_rank_zero_and_sizes_are_frozen() -> None:
    torch.manual_seed(411)
    model = ExactPriorResidualActorCritic()
    features = torch.randn(3, 5, 44)
    counts = torch.tensor([5, 3, 4])
    ranks = torch.tensor([[2, 0, 1, 3, 4], [1, 2, 0, 65535, 65535], [3, 2, 1, 0, 65535]])
    selected, *_ = model.action_and_value(features, counts, ranks, deterministic=True)
    assert selected.tolist() == [1, 2, 3]
    assert actor_parameter_count(model) == 737
    assert critic_parameter_count(model) == 8_897


def test_advantages_stop_at_auto_reset_boundary() -> None:
    rewards = np.array([[1.0], [2.0], [4.0]], dtype=np.float32)
    dones = np.array([[0.0], [1.0], [0.0]], dtype=np.float32)
    values = np.zeros_like(rewards)
    result = compute_advantages(
        rewards, dones, values, np.array([0.0], dtype=np.float32), gamma=1.0, gae_lambda=1.0
    )
    assert result[:, 0].tolist() == [3.0, 2.0, 4.0]


def test_rollout_packing_preserves_variable_candidate_widths() -> None:
    first = np.ones((2, 3, 44), dtype=np.float32)
    second = np.full((2, 5, 44), 2.0, dtype=np.float32)
    first_ranks = np.tile(np.arange(3, dtype=np.uint16), (2, 1))
    second_ranks = np.tile(np.arange(5, dtype=np.uint16), (2, 1))
    features, ranks = pack_observations(
        [first, second], [first_ranks, second_ranks]
    )
    assert features.shape == (2, 2, 5, 44)
    assert ranks.shape == (2, 2, 5)
    assert np.all(features[0, :, 3:] == 0)
    assert np.all(ranks[0, :, 3:] == np.iinfo(np.uint16).max)
