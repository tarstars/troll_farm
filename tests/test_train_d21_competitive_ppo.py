from __future__ import annotations

import numpy as np

from cgauto.train_d21_competitive_ppo import FROZEN, compute_advantages


def test_frozen_pilot_geometry_and_hyperparameters():
    assert FROZEN["model_seed"] == 2107
    assert FROZEN["train_seed_base"] == 8_200_000
    assert FROZEN["num_envs"] * FROZEN["rollout_steps"] == 10_000
    assert FROZEN["total_transitions"] == 1_000_000
    assert FROZEN["gamma"] == 1.0
    assert FROZEN["entropy_coef"] == 0.005
    assert FROZEN["teacher_aux_coef"] == 0.05
    assert FROZEN["max_turns"] == 300


def test_gae_does_not_cross_terminal_auto_reset_boundary():
    rewards = np.array([[1.0], [2.0], [10.0]], dtype=np.float32)
    dones = np.array([[0.0], [1.0], [0.0]], dtype=np.float32)
    values = np.zeros_like(rewards)
    result = compute_advantages(
        rewards,
        dones,
        values,
        np.array([0.0], dtype=np.float32),
        gamma=1.0,
        gae_lambda=1.0,
    )

    np.testing.assert_allclose(result[:, 0], [3.0, 2.0, 10.0])
