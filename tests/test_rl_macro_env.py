from __future__ import annotations

import numpy as np

from cgauto.rl_macro_env import (
    CANDIDATE_FEATURES,
    MAX_CANDIDATES,
    MacroVecEnv,
    random_legal_actions,
)


def test_macro_shapes_and_teacher_indices_are_legal() -> None:
    with MacroVecEnv(4, 9_710_000) as env:
        assert env.actions.shape == (4, MAX_CANDIDATES)
        assert env.features.shape == (4, MAX_CANDIDATES, CANDIDATE_FEATURES)
        assert env.counts.shape == (4,)
        assert env.teacher_indices.shape == (4,)
        assert env.prior_ranks.shape == (4, MAX_CANDIDATES)
        assert np.all(env.teacher_indices < env.counts)
        assert np.all(
            env.prior_ranks[np.arange(4), env.teacher_indices.astype(np.int64)] == 0
        )
        selected = env.teacher_actions()
        assert np.array_equal(
            selected,
            env.actions[np.arange(4), env.teacher_indices.astype(np.int64)],
        )


def test_macro_batches_are_feature_and_transition_deterministic() -> None:
    with MacroVecEnv(3, 9_710_100) as left, MacroVecEnv(3, 9_710_100) as right:
        for _ in range(20):
            assert np.array_equal(left.actions, right.actions)
            assert np.array_equal(left.features, right.features)
            assert np.array_equal(left.counts, right.counts)
            assert np.array_equal(left.teacher_indices, right.teacher_indices)
            assert np.array_equal(left.branches, right.branches)
            assert np.array_equal(left.prior_ranks, right.prior_ranks)
            selected = left.teacher_actions()
            assert np.array_equal(selected, right.teacher_actions())
            *_, left_rewards, left_info = left.step(selected)
            *_, right_rewards, right_info = right.step(selected)
            assert np.array_equal(left_rewards, right_rewards)
            assert left_info == right_info


def test_random_macro_actions_are_legal_candidates() -> None:
    rng = np.random.default_rng(41)
    with MacroVecEnv(8, 9_710_200) as env:
        selected = random_legal_actions(env, rng)
        for index, action in enumerate(selected):
            assert action in env.actions[index, : env.counts[index]]
