from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from cgauto.rl_full_env import (
    ACTION_SIZE,
    DEFAULT_LIBRARY,
    OPPONENTS,
    PHASE_PLAN,
    PHASE_TROLL,
    FullVecEnv,
    RandomFrozenOpponent,
    random_legal_actions,
    replay_and_verify,
)


TEST_LIBRARY = Path(os.environ.get("TF_FULL_TEST_LIBRARY", DEFAULT_LIBRARY))
pytestmark = pytest.mark.skipif(
    not TEST_LIBRARY.exists(), reason="release Rust full-environment library missing"
)


def _env(
    num_envs: int,
    seed: int,
    weights: dict[str, float] | None = None,
    *,
    frozen: RandomFrozenOpponent | None = None,
) -> FullVecEnv:
    return FullVecEnv(
        num_envs,
        seed,
        opponent_weights=weights,
        frozen_opponent=frozen,
        library=TEST_LIBRARY,
    )


def test_shapes_phase_masks_and_atomic_invalid_action() -> None:
    with _env(4, 100, {"script_boss": 1.0}) as env:
        assert env.obs.shape == (4, 104, 11, 22)
        assert env.masks.shape == (4, 13, 11, 22)
        assert env.plan_masks.shape == (4, 144)
        assert np.all(env.phase == PHASE_PLAN)
        assert np.all(env.plan_masks[:, 0] == 1)
        assert not env.masks.any()

        before = env.obs.copy()
        with pytest.raises(RuntimeError, match="-4"):
            env.step(np.full(4, 144, dtype=np.int32))
        np.testing.assert_array_equal(env.obs, before)
        assert np.all(env.phase == PHASE_PLAN)

        transitions, info = env.step(np.zeros(4, dtype=np.int32))
        assert not len(transitions.actions)
        assert not info.turn_completed.any()
        assert np.all(env.phase == PHASE_TROLL)
        flat = env.masks.reshape(4, ACTION_SIZE)
        assert flat.any(axis=1).all()


def test_identical_batches_are_deterministic() -> None:
    rng = np.random.default_rng(51)
    weights = {name: 1.0 for name in OPPONENTS[:-1]}
    with _env(4, 777, weights) as left, _env(4, 777, weights) as right:
        for _ in range(24):
            np.testing.assert_array_equal(left.obs, right.obs)
            np.testing.assert_array_equal(left.masks, right.masks)
            np.testing.assert_array_equal(left.plan_masks, right.plan_masks)
            actions = random_legal_actions(left, rng)
            left_transitions, left_info = left.step(actions)
            right_transitions, right_info = right.step(actions)
            np.testing.assert_array_equal(left_transitions.actions, right_transitions.actions)
            np.testing.assert_array_equal(left_transitions.rewards, right_transitions.rewards)
            np.testing.assert_array_equal(left_info.turn_completed, right_info.turn_completed)
            np.testing.assert_array_equal(left_info.dones, right_info.dones)


def test_python_frozen_opponent_completes_and_credits_only_learner_steps() -> None:
    rng = np.random.default_rng(61)
    frozen = RandomFrozenOpponent(62)
    with _env(6, 800, {"python_frozen": 1.0}, frozen=frozen) as env:
        transitions, info = env.step(random_legal_actions(env, rng))
        assert not info.turn_completed.any()
        transitions, info = env.step(random_legal_actions(env, rng))
        assert np.all(info.turn_completed == 1)
        assert np.all(info.reward_credit_count == 2)
        assert len(transitions.actions) == 12
        assert set(transitions.slots.tolist()) == set(range(6))


def test_ten_thousand_random_masked_learner_actions_are_accepted() -> None:
    rng = np.random.default_rng(65)
    frozen = RandomFrozenOpponent(66)
    accepted = 0
    with _env(20, 850, {"python_frozen": 1.0}, frozen=frozen) as env:
        while accepted < 10_000:
            actions = random_legal_actions(env, rng)
            plan_slots = env.phase == PHASE_PLAN
            troll_slots = env.phase == PHASE_TROLL
            assert np.all(
                env.plan_masks[np.flatnonzero(plan_slots), actions[plan_slots]] == 1
            )
            flat = env.masks.reshape(20, ACTION_SIZE)
            assert np.all(flat[np.flatnonzero(troll_slots), actions[troll_slots]] == 1)
            env.step(actions)
            accepted += int(plan_slots.sum() + troll_slots.sum())
    assert accepted >= 10_000


def test_completed_replay_matches_python_simulator_each_turn() -> None:
    rng = np.random.default_rng(71)
    with _env(1, 900, {"script_boss": 1.0}) as env:
        for _ in range(2_000):
            _, info = env.step(random_legal_actions(env, rng))
            if info.dones[0]:
                assert info.illegal_commands[0] == 0
                replay = env.take_replay(0)
                assert replay is not None
                assert replay_and_verify(replay) == int(info.state_hash[0])
                break
        else:
            pytest.fail("full-game episode did not terminate")


def test_two_hundred_no_train_self_play_replays_match_python_simulator() -> None:
    class NoTrainFrozen(RandomFrozenOpponent):
        def __call__(self, *args: np.ndarray) -> np.ndarray:
            actions = super().__call__(*args)
            phases = args[3]
            actions[phases == PHASE_PLAN] = 0
            return actions

    rng = np.random.default_rng(81)
    completed = 0
    with _env(
        20,
        1_100,
        {"python_frozen": 1.0},
        frozen=NoTrainFrozen(82),
    ) as env:
        while completed < 200:
            actions = random_legal_actions(env, rng)
            actions[env.phase == PHASE_PLAN] = 0
            _, info = env.step(actions)
            for slot in np.flatnonzero(info.dones):
                assert info.illegal_commands[slot] == 0
                replay = env.take_replay(int(slot))
                assert replay is not None
                assert replay_and_verify(replay) == int(info.state_hash[slot])
                completed += 1
    assert completed == 200
