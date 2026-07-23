from __future__ import annotations

import numpy as np

from cgauto.rl_level1_env import (
    ACTION_SIZE,
    Level1VecEnv,
    random_legal_actions,
    run_policy,
)


def test_teacher_actions_are_legal_and_shapes_match() -> None:
    with Level1VecEnv(4, 0) as env:
        assert env.obs.shape == (4, 104, 11, 22)
        assert env.masks.shape == (4, 13, 11, 22)
        actions = env.teacher_actions()
        legal = env.masks.reshape(4, ACTION_SIZE)[np.arange(4), actions]
        assert np.array_equal(legal, np.ones(4, dtype=np.uint8))


def test_identical_batches_are_deterministic() -> None:
    with Level1VecEnv(3, 77) as left, Level1VecEnv(3, 77) as right:
        for _ in range(25):
            assert np.array_equal(left.obs, right.obs)
            assert np.array_equal(left.masks, right.masks)
            actions = left.teacher_actions()
            assert np.array_equal(actions, right.teacher_actions())
            lo, lm, lr, li = left.step(actions)
            ro, rm, rr, ri = right.step(actions)
            assert np.array_equal(lo, ro)
            assert np.array_equal(lm, rm)
            assert np.array_equal(lr, rr)
            assert np.array_equal(li.dones, ri.dones)
            assert np.array_equal(li.successes, ri.successes)


def test_random_sampler_uses_mask() -> None:
    rng = np.random.default_rng(123)
    with Level1VecEnv(8, 100) as env:
        actions = random_legal_actions(env.masks, rng)
        assert np.all(
            env.masks.reshape(8, ACTION_SIZE)[np.arange(8), actions] == 1
        )


def test_policy_evaluation_collects_the_exact_seed_interval() -> None:
    result = run_policy("teacher", episodes=17, num_envs=3, seed_base=10_000)
    assert [row["seed"] for row in result["episodes_detail"]] == list(
        range(10_000, 10_017)
    )
