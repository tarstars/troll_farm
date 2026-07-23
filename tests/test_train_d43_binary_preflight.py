import numpy as np
import torch

from cgauto.rl_macro_env import BRANCHES
from cgauto.train_d43_binary_preflight import (
    ACTOR_FEATURES,
    CRITIC_FEATURES,
    BinaryActorCritic,
    actor_parameter_count,
    construct_binary_state,
    critic_parameter_count,
    normalize_eligible_advantages,
)


def test_binary_actor_is_d40_deterministic_with_frozen_counts():
    torch.manual_seed(4310)
    model = BinaryActorCritic()
    actor = torch.randn(7, ACTOR_FEATURES)
    critic = torch.randn(7, CRITIC_FEATURES)
    selected, _, _, _, logits = model.action_and_value(actor, critic, deterministic=True)
    assert selected.tolist() == [0] * 7
    np.testing.assert_allclose(torch.sigmoid(logits).detach().numpy(), 0.25)
    assert actor_parameter_count(model) == 1249
    assert critic_parameter_count(model) == 8897


def test_constructed_state_has_exact_layout_and_eligibility():
    features = np.zeros((2, 3, 44), dtype=np.float32)
    features[:, :, 0] = 1
    features[0, :, 1] = 50 / 300
    features[1, :, 1] = 150 / 300
    features[:, :, 17:] = np.arange(27, dtype=np.float32)
    counts = np.asarray([3, 2])
    ranks = np.asarray([[0, 1, 2], [1, 0, 65535]], dtype=np.uint16)
    residual = np.asarray([[0, 0.25, -1], [0.25, 0, -1]], dtype=np.float32)
    branches = np.asarray([BRANCHES.index("rate"), BRANCHES.index("rate")])
    actor, critic, eligible, rank_zero, rank_one, gap = construct_binary_state(
        features, counts, ranks, residual, branches
    )
    assert actor.shape == (2, ACTOR_FEATURES)
    assert critic.shape == (2, CRITIC_FEATURES)
    assert eligible.tolist() == [True, False]
    assert rank_zero.tolist() == [0, 1]
    assert rank_one.tolist() == [1, 0]
    np.testing.assert_allclose(gap, [0.25, 0.25])


def test_actor_advantages_normalize_only_eligible_rows():
    advantage = np.asarray([[1, 100], [3, 200]], dtype=np.float32)
    eligible = np.asarray([[True, False], [True, False]])
    result = normalize_eligible_advantages(advantage, eligible)
    np.testing.assert_allclose(result[eligible], [-1, 1])
    np.testing.assert_array_equal(result[~eligible], 0)
