from __future__ import annotations

import numpy as np
import pytest

from cgauto.rl_level1_env import (
    ACTION_SIZE,
    DEFAULT_LIBRARY,
    OBS_HEIGHT,
    OBS_SIZE,
    OBS_WIDTH,
)
from cgauto.rl_level2_env import LEVEL2_TARGETS, level2_recipe
from cgauto.rl_level3_env import Level3VecEnv
from cgauto.rl_level4_env import LEVEL3_SCORE_GAIN, Level4VecEnv, run_policy


pytestmark = pytest.mark.skipif(not DEFAULT_LIBRARY.exists(), reason="release Rust library missing")
OBS_CELLS = OBS_HEIGHT * OBS_WIDTH


def test_level4_shapes_masks_recipe_observation_and_teacher_legality() -> None:
    with Level4VecEnv(16, 0) as env:
        assert env.obs.size == 16 * OBS_SIZE
        assert env.masks.reshape(16, ACTION_SIZE).any(axis=1).all()
        for index in range(16):
            _, target = level2_recipe(index)
            encoded = [round(255 * value / 4) for value in target]
            assert [int(env.obs[index, 86 + offset, 0, 0]) for offset in range(4)] == encoded
        for _ in range(100):
            actions = env.teacher_actions()
            flat = env.masks.reshape(16, ACTION_SIZE)
            assert np.all(flat[np.arange(16), actions] == 1)
            env.step(actions)


def test_level4_batches_are_deterministic() -> None:
    with Level4VecEnv(8, 77) as left, Level4VecEnv(8, 77) as right:
        for _ in range(160):
            left_actions = left.teacher_actions()
            right_actions = right.teacher_actions()
            np.testing.assert_array_equal(left_actions, right_actions)
            left_step = left.step(left_actions)
            right_step = right.step(right_actions)
            for left_value, right_value in zip(left_step[:3], right_step[:3]):
                np.testing.assert_array_equal(left_value, right_value)
            np.testing.assert_array_equal(left_step[3].dones, right_step[3].dones)
            np.testing.assert_array_equal(left_step[3].seeds, right_step[3].seeds)
            np.testing.assert_array_equal(left_step[3].recipe_ids, right_step[3].recipe_ids)
            np.testing.assert_array_equal(left_step[3].targets, right_step[3].targets)


def test_level4_terminal_metadata_covers_exact_recipe_catalog() -> None:
    result = run_policy("teacher", episodes=200, num_envs=20, seed_base=0)
    assert result["success_rate"] >= 0.98
    assert result["created_crop_rate"] >= 0.98
    assert result["renewable_harvest_rate"] >= 0.98
    assert result["median_score_gain"] >= LEVEL3_SCORE_GAIN
    assert set(result["by_recipe"]) == {str(index) for index in range(len(LEVEL2_TARGETS))}
    for row in result["episodes_detail"]:
        recipe_id, target = level2_recipe(row["seed"])
        assert row["recipe_id"] == recipe_id
        assert row["target"] == list(target)


def test_fixed_level3_path_still_uses_constant_target_channels() -> None:
    expected = [round(255 * value / 4) for value in (2, 2, 0, 2)]
    with Level3VecEnv(4, 31) as env:
        for index in range(4):
            observed = [
                int(env.obs[index].reshape(104, OBS_CELLS)[86 + offset, 0])
                for offset in range(4)
            ]
            assert observed == expected
