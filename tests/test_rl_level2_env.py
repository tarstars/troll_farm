from __future__ import annotations

import numpy as np

from cgauto.rl_level1_env import ACTION_SIZE, random_legal_actions
from cgauto.rl_level2_env import (
    LEVEL2_TARGETS,
    Level2VecEnv,
    level2_recipe,
    run_policy,
)


def test_recipe_assignment_covers_catalog_and_is_stable() -> None:
    assignments = [level2_recipe(seed) for seed in range(200)]
    assert {recipe_id for recipe_id, _ in assignments} == set(range(len(LEVEL2_TARGETS)))
    assert all(target == LEVEL2_TARGETS[recipe_id] for recipe_id, target in assignments)


def test_level2_teacher_is_legal_and_observation_exposes_recipe() -> None:
    with Level2VecEnv(8, 100) as env:
        assert env.obs.shape == (8, 104, 11, 22)
        assert env.masks.shape == (8, 13, 11, 22)
        actions = env.teacher_actions()
        assert np.all(env.masks.reshape(8, ACTION_SIZE)[np.arange(8), actions] == 1)
        for slot, seed in enumerate(range(100, 108)):
            _, target = level2_recipe(seed)
            encoded = [round(255 * value / 4) for value in target]
            assert env.obs[slot, 86:90, 0, 0].tolist() == encoded


def test_level2_batches_and_terminal_metadata_are_deterministic() -> None:
    with Level2VecEnv(4, 700) as left, Level2VecEnv(4, 700) as right:
        for _ in range(50):
            assert np.array_equal(left.obs, right.obs)
            assert np.array_equal(left.masks, right.masks)
            actions = left.teacher_actions()
            assert np.array_equal(actions, right.teacher_actions())
            _, _, rewards_left, info_left = left.step(actions)
            _, _, rewards_right, info_right = right.step(actions)
            assert np.array_equal(rewards_left, rewards_right)
            assert np.array_equal(info_left.dones, info_right.dones)
            assert np.array_equal(info_left.recipe_ids, info_right.recipe_ids)
            assert np.array_equal(info_left.targets, info_right.targets)


def test_level2_random_sampler_uses_mask() -> None:
    rng = np.random.default_rng(61)
    with Level2VecEnv(8, 900) as env:
        actions = random_legal_actions(env.masks, rng)
        assert np.all(env.masks.reshape(8, ACTION_SIZE)[np.arange(8), actions] == 1)


def test_level2_policy_collects_exact_seed_interval_and_recipe_metadata() -> None:
    result = run_policy("teacher", episodes=17, num_envs=3, seed_base=12_000)
    assert [row["seed"] for row in result["episodes_detail"]] == list(
        range(12_000, 12_017)
    )
    for row in result["episodes_detail"]:
        recipe_id, target = level2_recipe(row["seed"])
        assert row["recipe_id"] == recipe_id
        assert row["target"] == list(target)
