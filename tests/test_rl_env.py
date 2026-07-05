"""Smoke/invariant tests for the RL scaffold (rl/). Fast: a few short episodes."""
import numpy as np
import pytest

from rl.env import TrollFarmEnv, K, NUM_MACROS, NUM_TRAIN
from rl.opponents import opponent_names, get_opponent
from rl.policy import MLPPolicy


def test_reset_and_obs_shape():
    env = TrollFarmEnv(opponent="boss", seed_pool=[0])
    obs = env.reset(seed=0)
    assert obs.shape == (env.obs_dim,)
    assert obs.dtype == np.float32
    assert np.isfinite(obs).all()
    assert env.action_nvec.tolist() == [NUM_MACROS] * K + [NUM_TRAIN]


def test_step_runs_and_obs_finite():
    env = TrollFarmEnv(opponent="chopper", seed_pool=[1])
    env.reset(seed=0)
    rng = np.random.RandomState(0)
    for _ in range(300):
        a = np.array([rng.randint(n) for n in env.action_nvec])
        obs, r, term, trunc, info = env.step(a)
        assert np.isfinite(obs).all()
        assert isinstance(r, float)
        if term or trunc:
            break
    assert trunc and info["margin"] == info["my_score"] - info["opp_score"]


def test_reward_telescopes_to_margin_without_shaping():
    # With no shaping and unit scale, per-step reward == Δ(score margin), so the
    # episode reward sum must equal the final margin exactly.
    env = TrollFarmEnv(opponent="boss", seed_pool=[2], carry_coef=0.0, reward_scale=1.0)
    env.reset(seed=0)
    rng = np.random.RandomState(3)
    total = 0.0
    while True:
        a = np.array([rng.randint(n) for n in env.action_nvec])
        _, r, term, trunc, info = env.step(a)
        total += r
        if term or trunc:
            break
    assert total == pytest.approx(info["margin"], abs=1e-6)


def test_all_opponents_produce_commands():
    for name in opponent_names():
        env = TrollFarmEnv(opponent=name, seed_pool=[4])
        game = env.game if env.game is not None else None
        env.reset(seed=0)
        cmds = get_opponent(name)(env.game, 1)
        assert isinstance(cmds, list) and all(isinstance(c, str) for c in cmds)


def test_policy_forward_and_save_load(tmp_path):
    env = TrollFarmEnv(opponent="boss", seed_pool=[5])
    obs = env.reset(seed=0)
    pol = MLPPolicy(env.obs_dim, env.action_nvec, hidden=32, seed=0)
    rng = np.random.RandomState(0)
    a, v = pol.act(obs, rng)
    assert a.shape == (env.num_heads,)
    assert all(0 <= a[i] < env.action_nvec[i] for i in range(env.num_heads))
    p = tmp_path / "pol.npz"
    pol.save(str(p))
    pol2 = MLPPolicy.load(str(p))
    _, logits1, _ = pol.forward(obs[None])
    _, logits2, _ = pol2.forward(obs[None])
    assert np.allclose(logits1, logits2)
