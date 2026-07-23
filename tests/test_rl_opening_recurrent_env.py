"""Focused checks for D73's ordinary recurrent ABI wrapper."""

from __future__ import annotations

import numpy as np

from cgauto.rl_opening_recurrent_env import (
    OPENING_RECURRENT_ACTIONS,
    OPENING_RECURRENT_FEATURES,
    OpeningRecurrentVecEnv,
)


def test_opening_recurrent_shapes_masks_and_step() -> None:
    with OpeningRecurrentVecEnv(4, 9_810_999) as env:
        assert env.features.shape == (4, OPENING_RECURRENT_FEATURES)
        assert env.masks.shape == (4, OPENING_RECURRENT_ACTIONS)
        assert np.isfinite(env.features).all()
        assert np.all(env.masks[:, 0] == 1)
        features, masks, rewards, info = env.step(np.zeros(4, dtype=np.int32))
        assert features.shape == (4, OPENING_RECURRENT_FEATURES)
        assert masks.shape == (4, OPENING_RECURRENT_ACTIONS)
        assert rewards.shape == (4,)
        assert len(info.terminals) == 4
