"""Tests for the lever-pricing instrument.

Step 5 of the recovery programme must choose between levers that all claim to put more real
signal inside the credit window. The instrument prices two of them offline, before either costs
cluster time, by re-cutting ONE collected rollout: the reward split is re-measured by replaying
the same actions under a different (wood_shaping, end_wood), and the rollout length is
re-measured by cutting the same buffer into shorter windows.

The windowing is the part that can silently lie: if a shortened window kept the rollout's final
bootstrap instead of the value of the step just past its own edge, every short window would be
handed the long window's information and the measurement would understate exactly the effect it
exists to measure.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "claude_1" / "nn-bot" / "lever_price.py"

spec = importlib.util.spec_from_file_location("lever_price", MODULE)
lever_price = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = lever_price
spec.loader.exec_module(lever_price)


def test_window_bootstrap_is_the_value_of_the_step_after_the_window():
    """Each cut bootstraps from the stored value just past its edge; only the last cut uses
    the rollout's own recorded next_value."""

    values = np.array([[1.0], [2.0], [3.0], [4.0]], dtype=np.float32)
    final_next_value = np.array([9.0], dtype=np.float32)

    cuts = lever_price.window_cuts(
        window=2, values=values, final_next_value=final_next_value
    )

    assert [(cut.start, cut.stop) for cut in cuts] == [(0, 2), (2, 4)]
    np.testing.assert_allclose(cuts[0].next_value, [3.0])
    np.testing.assert_allclose(cuts[1].next_value, [9.0])


def test_window_that_does_not_divide_the_buffer_is_refused():
    """A ragged final window would be both shorter and wrongly bootstrapped, which would bias
    the very comparison the instrument exists to make."""

    values = np.arange(5, dtype=np.float32).reshape(5, 1)
    final_next_value = np.array([9.0], dtype=np.float32)

    try:
        lever_price.window_cuts(
            window=2, values=values, final_next_value=final_next_value
        )
    except ValueError as error:
        assert "divide" in str(error)
    else:
        raise AssertionError("expected a ValueError for a window that does not divide 5")


def _terminal_only_rollout():
    """Four turns, one env, all PLAN rows; the only reward is paid at the ending on the last."""

    ones = np.ones((4, 1), dtype=np.float32)
    return lever_price.Rollout(
        rewards=np.array([[0.0], [0.0], [0.0], [10.0]], dtype=np.float32),
        values=ones.copy(),
        dones=np.array([[0], [0], [0], [1]], dtype=np.float32),
        turn_boundary=ones.copy(),
        phase=np.zeros((4, 1), dtype=np.int64),
        final_next_value=np.zeros(1, dtype=np.float32),
    )


def test_a_shorter_window_sees_less_of_a_reward_paid_at_the_ending():
    """The mechanism the whole measurement rests on: when the reward arrives only at the
    ending, rows more than a window away from it are taught by the critic instead. Cutting the
    same trajectory shorter must therefore lower the observed-reward share."""

    rollout = _terminal_only_rollout()

    whole = lever_price.price_window(rollout, window=4, gamma=1.0, gae_lambda=1.0)
    halved = lever_price.price_window(rollout, window=2, gamma=1.0, gae_lambda=1.0)

    assert whole["plan"]["observed_reward_share"] > halved["plan"]["observed_reward_share"]
    assert whole["plan"]["terminal_traced_fraction"] == 1.0
    assert halved["plan"]["terminal_traced_fraction"] == 0.5


def _first_legal(env):
    """Deterministic, network-free decisions: the lowest-index legal action, zero values.

    The dynamics, not the policy, are what this fixture needs to hold still.
    """

    trainer = lever_price.load_trainer()
    phase = np.asarray(env.phase)
    legal = trainer.build_legal(
        np.asarray(env.masks), np.asarray(env.plan_masks), phase
    )
    actions = np.full(env.num_envs, -1, dtype=np.int32)
    for index in range(env.num_envs):
        if phase[index] == trainer.PHASE_EXTERNAL_WAIT:
            continue
        allowed = np.flatnonzero(legal[index])
        actions[index] = int(allowed[0])
    return actions, np.zeros(env.num_envs, dtype=np.float32)


def _env(wood_shaping, end_wood):
    from cgauto.rl_full_env import FullVecEnv

    return FullVecEnv(
        2,
        4242,
        ROOT / "local_claude_1" / "nn-bot" / "maps-slice-1000.jsonl",
        {"champion_exact": 1.0},
        wood_shaping=wood_shaping,
        end_wood=end_wood,
    )


def test_the_wood_split_leaves_the_game_itself_alone():
    """The split is priced by replaying one action sequence under another split, which is only
    sound if the split is an output of the game and not an input to it: the same seed and the
    same actions must give the same game. (That the rewards then differ needs a policy that
    actually earns wood, so it is asserted on the clone in the measurement, not here.)"""

    steps = 24
    with _env(0.0, 4.0) as paid_at_the_end:
        end_only = lever_price.collect(paid_at_the_end, _first_legal, steps)
    with _env(2.0, 2.0) as paid_as_it_goes:
        split = lever_price.collect(paid_as_it_goes, _first_legal, steps)

    np.testing.assert_array_equal(end_only.state_hash, split.state_hash)
    np.testing.assert_array_equal(end_only.actions, split.actions)
    np.testing.assert_array_equal(end_only.rollout.dones, split.rollout.dones)
    np.testing.assert_array_equal(
        end_only.rollout.turn_boundary, split.rollout.turn_boundary
    )


class _ScriptedEnv:
    """A two-mini-step turn whose reward is reported on both mini-steps.

    The real environment reports a turn's reward against mini-steps that did not execute the
    turn; the trainer's default `--reward-credit executing` drops those. This fake exists to
    hold that rule still, because a collector that forgot it would inflate the observed-reward
    share -- the exact number the instrument is built to report.
    """

    def __init__(self, rewards, turn_completed):
        self.num_envs = 1
        self._rewards = rewards
        self._turn_completed = turn_completed
        self._step = 0
        self.phase = np.array([1], dtype=np.int32)

    def step(self, actions):
        import types

        index = self._step
        self._step += 1
        info = types.SimpleNamespace(
            dones=np.zeros(1, dtype=np.float32),
            turn_completed=np.array([self._turn_completed[index]], dtype=np.float32),
            state_hash=np.zeros(1, dtype=np.uint64),
        )
        return np.array([self._rewards[index]], dtype=np.float32), info


def test_reward_is_kept_only_on_the_mini_step_that_executed_the_turn():
    """`--reward-credit executing`, the trainer's default and the setting every run of record
    used. The within-turn trace factor of 1.0 carries the reward to the turn's other mini-steps
    anyway, so keeping the raw copies would double-count them."""

    env = _ScriptedEnv(rewards=[5.0, 7.0], turn_completed=[0.0, 1.0])

    collected = lever_price.collect(
        env, lambda _: (np.zeros(1, dtype=np.int32), np.zeros(1, dtype=np.float32)), 2
    )

    np.testing.assert_allclose(collected.rollout.rewards, [[0.0], [7.0]])


CLONE = ROOT / "local_claude_1" / "nn-bot" / "results" / "clone-2026-08-30-a" / "clone-pilot.pt"


def test_the_clone_decides_only_legal_actions():
    """The measurement is collected by the clone itself. An illegal action would be counted by
    the environment and quietly change the game the levers are being priced on."""

    trainer = lever_price.load_trainer()
    decide = lever_price.clone_decider(CLONE, train_scope="plan-critic", seed=11)

    with _env(0.0, 4.0) as env:
        for _ in range(6):
            phase = np.asarray(env.phase)
            legal = trainer.build_legal(
                np.asarray(env.masks), np.asarray(env.plan_masks), phase
            )
            actions, values = decide(env)
            assert values.shape == (env.num_envs,)
            for index in range(env.num_envs):
                assert legal[index][actions[index]] == 1
            env.step(np.asarray(actions, dtype=np.int32))


def test_replaying_the_recorded_actions_reproduces_the_same_game_and_rewards():
    """The counterfactual splits are priced by replaying one recorded action sequence, so replay
    must be exact: same seed, same actions, same split must give back what was collected."""

    steps = 20
    with _env(0.0, 4.0) as first:
        collected = lever_price.collect(first, _first_legal, steps)
    with _env(0.0, 4.0) as again:
        replayed = lever_price.replay(again, collected.actions)

    np.testing.assert_array_equal(replayed.state_hash, collected.state_hash)
    np.testing.assert_allclose(replayed.rewards, collected.rollout.rewards)
    np.testing.assert_array_equal(replayed.turn_boundary, collected.rollout.turn_boundary)


def test_pricing_skips_the_burn_in_and_measures_only_the_tail():
    """Freshly built environments all sit at turn 0, so the first stretch of a collection is not
    a representative sample of a training run's rollouts. Pricing must read the tail only, and
    read it exactly as if the tail had been collected alone."""

    rollout = _terminal_only_rollout()
    tail = lever_price.Rollout(
        rewards=rollout.rewards[2:],
        values=rollout.values[2:],
        dones=rollout.dones[2:],
        turn_boundary=rollout.turn_boundary[2:],
        phase=rollout.phase[2:],
        final_next_value=rollout.final_next_value,
    )

    priced = lever_price.price_tail(rollout, burn_in=2, window=2, gamma=1.0, gae_lambda=1.0)
    directly = lever_price.price_window(tail, window=2, gamma=1.0, gae_lambda=1.0)

    assert priced == directly
