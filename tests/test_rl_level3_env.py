from __future__ import annotations

import numpy as np
import pytest

from cgauto.rl_level1_env import ACTION_SIZE, OBS_SIZE, DEFAULT_LIBRARY
from cgauto.rl_level3_env import LEVEL3_SCORE_GAIN, Level3VecEnv, run_policy


pytestmark = pytest.mark.skipif(not DEFAULT_LIBRARY.exists(), reason="release Rust library missing")


def test_level3_shapes_masks_and_teacher_legality() -> None:
    with Level3VecEnv(8, 0) as env:
        assert env.obs.size == 8 * OBS_SIZE
        assert env.masks.reshape(8, ACTION_SIZE).any(axis=1).all()
        for _ in range(80):
            actions = env.teacher_actions()
            flat = env.masks.reshape(8, ACTION_SIZE)
            assert np.all(flat[np.arange(8), actions] == 1)
            env.step(actions)


def test_level3_batches_are_deterministic() -> None:
    with Level3VecEnv(4, 77) as left, Level3VecEnv(4, 77) as right:
        for _ in range(120):
            left_actions = left.teacher_actions()
            right_actions = right.teacher_actions()
            np.testing.assert_array_equal(left_actions, right_actions)
            left_step = left.step(left_actions)
            right_step = right.step(right_actions)
            for left_value, right_value in zip(left_step[:3], right_step[:3]):
                np.testing.assert_array_equal(left_value, right_value)
            np.testing.assert_array_equal(left_step[3].dones, right_step[3].dones)
            np.testing.assert_array_equal(left_step[3].seeds, right_step[3].seeds)


def test_level3_teacher_closes_renewable_loop_on_debug_bank() -> None:
    result = run_policy("teacher", episodes=100, num_envs=20, seed_base=0)
    assert result["success_rate"] >= 0.97
    assert result["created_crop_rate"] >= 0.97
    assert result["renewable_harvest_rate"] >= 0.97
    assert result["median_score_gain"] >= LEVEL3_SCORE_GAIN
