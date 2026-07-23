from __future__ import annotations

import torch

from cgauto.rl_resident_residual_env import ACTION_SIZE, OBS_CHANNELS
from cgauto.train_resident_residual_ppo import ResidentResidualActorCritic


def test_compact_actor_shape_and_keep_bias():
    model = ResidentResidualActorCritic(width=8, blocks=2, keep_bias=0.5)
    observations = torch.zeros((2, OBS_CHANNELS, 11, 22), dtype=torch.uint8)
    observations[:, 0] = 255
    masks = torch.zeros((2, 13, 11, 22), dtype=torch.uint8)
    keep = 3 * 22 + 4
    masks[:, 0, 3, 4] = 1
    masks[:, 2, 3, 4] = 1
    actions, _, _, values = model.action_and_value(
        observations, masks, deterministic=True
    )

    assert actions.tolist() == [keep, keep]
    assert values.shape == (2,)
    assert model(observations)[0].shape == (2, ACTION_SIZE)
    assert sum(parameter.numel() for parameter in model.parameters()) < 20_000
