"""Tests for the Phase-3 PPO trainer (`local_claude_1/nn-bot/train_ppo_full.py`).

Everything runs on `local_claude_1/nn-bot/fake_full_env.py`, so no Rust library and no data file
is needed. The four things pinned here are the four the card cares about: the discount inside a
turn, which head the loss uses, the checkpoint format, and the clone anchor.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from torch.distributions.categorical import Categorical

ROOT = Path(__file__).resolve().parents[1]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"


def _load(name: str, filename: str):
    path = NN_BOT / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


tpf = _load("train_ppo_full_under_test", "train_ppo_full.py")
fake = _load("fake_full_env_under_test", "fake_full_env.py")

from cgauto.train_level1_ppo import SpatialActorCritic  # noqa: E402


# --------------------------------------------------------------------------- 1. the GAE returns


def test_gae_uses_discount_one_inside_a_turn_and_gamma_across_turns() -> None:
    """A hand-built buffer of two turns: turn A is one mini-step, turn B is two.

    Layout, one environment, three stored mini-steps:

        t=0  turn A, executes the turn   -> turn_boundary 1, reward rA
        t=1  turn B, the plan mini-step  -> turn_boundary 0, reward 0
        t=2  turn B, executes the turn   -> turn_boundary 1, reward rB

    So the discount from t=0 to t=1 is gamma (a turn ended), from t=1 to t=2 is exactly 1 (the
    same turn continues), and from t=2 to the bootstrap is gamma again.
    """

    gamma, lam = 0.9, 0.8
    rewards = np.array([[2.0], [0.0], [5.0]], dtype=np.float32)
    values = np.array([[1.0], [3.0], [-2.0]], dtype=np.float32)
    dones = np.zeros((3, 1), dtype=np.float32)
    boundary = np.array([[1], [0], [1]], dtype=np.uint8)
    bootstrap = np.array([7.0], dtype=np.float32)

    advantages, returns = tpf.compute_gae(
        rewards, values, dones, boundary, bootstrap, gamma, lam
    )

    delta2 = rewards[2, 0] + gamma * bootstrap[0] - values[2, 0]
    advantage2 = delta2
    delta1 = rewards[1, 0] + 1.0 * values[2, 0] - values[1, 0]
    advantage1 = delta1 + 1.0 * lam * advantage2
    delta0 = rewards[0, 0] + gamma * values[1, 0] - values[0, 0]
    advantage0 = delta0 + gamma * lam * advantage1

    assert advantages[:, 0] == pytest.approx(
        [advantage0, advantage1, advantage2], rel=1e-6
    )
    assert returns[:, 0] == pytest.approx(
        [advantage0 + 1.0, advantage1 + 3.0, advantage2 - 2.0], rel=1e-6
    )


def test_gae_cuts_the_trace_at_an_episode_end() -> None:
    """A done at t=0 must stop both the bootstrap and the trace, whatever the boundary says."""

    gamma, lam = 0.99, 0.95
    rewards = np.array([[4.0], [1.0]], dtype=np.float32)
    values = np.array([[0.5], [0.25]], dtype=np.float32)
    dones = np.array([[1.0], [0.0]], dtype=np.float32)
    boundary = np.array([[1], [1]], dtype=np.uint8)
    bootstrap = np.array([9.0], dtype=np.float32)

    advantages, _ = tpf.compute_gae(
        rewards, values, dones, boundary, bootstrap, gamma, lam
    )
    assert advantages[0, 0] == pytest.approx(4.0 - 0.5, rel=1e-6)


def test_gae_with_discount_one_everywhere_is_the_undiscounted_sum() -> None:
    """All three mini-steps inside one turn: no gamma anywhere, lambda 1 -> plain returns."""

    rewards = np.array([[1.0], [2.0], [3.0]], dtype=np.float32)
    values = np.zeros((3, 1), dtype=np.float32)
    dones = np.zeros((3, 1), dtype=np.float32)
    boundary = np.zeros((3, 1), dtype=np.uint8)
    bootstrap = np.zeros(1, dtype=np.float32)
    _, returns = tpf.compute_gae(rewards, values, dones, boundary, bootstrap, 0.5, 1.0)
    assert returns[:, 0] == pytest.approx([6.0, 5.0, 3.0], rel=1e-6)


# --------------------------------------------------------------------------- 2. the two heads


def _phase_batch(seed: int = 3):
    """Two PLAN rows and two TROLL rows with random legal masks, built by hand."""

    rng = np.random.default_rng(seed)
    phase = np.array(
        [tpf.PHASE_PLAN, tpf.PHASE_TROLL, tpf.PHASE_PLAN, tpf.PHASE_TROLL],
        dtype=np.int64,
    )
    masks = np.zeros((4, 13, 11, 22), dtype=np.uint8)
    plan_masks = np.zeros((4, tpf.PLAN_SIZE), dtype=np.uint8)
    for row in range(4):
        if phase[row] == tpf.PHASE_PLAN:
            plan_masks[row, 0] = 1
            plan_masks[row, rng.integers(1, tpf.PLAN_SIZE, size=5)] = 1
        else:
            flat = masks[row].reshape(-1)
            flat[rng.choice(flat.shape[0], size=7, replace=False)] = 1
    obs = np.zeros((4, 104, 11, 22), dtype=np.uint8)
    obs[:, 0] = 255
    return obs, masks, plan_masks, phase


def test_build_legal_keeps_the_plan_mask_below_144_and_zero_above() -> None:
    _, masks, plan_masks, phase = _phase_batch()
    legal = tpf.build_legal(masks, plan_masks, phase)
    assert legal.shape == (4, tpf.ACTION_SIZE)
    for row in range(4):
        if phase[row] == tpf.PHASE_PLAN:
            assert np.array_equal(legal[row, : tpf.PLAN_SIZE], plan_masks[row])
            assert legal[row, tpf.PLAN_SIZE :].sum() == 0
        else:
            assert np.array_equal(legal[row], masks[row].reshape(-1))


def test_the_loss_picks_the_plan_head_on_plan_steps_and_the_spatial_head_on_troll_steps() -> None:
    """The PLAN rows' logits must come from the plan head, the TROLL rows' from the per-cell head.

    Proved by construction: `combined_logits` writes the plan head's 144 numbers into columns
    0..143 of the PLAN rows and leaves the TROLL rows untouched.
    """

    torch.manual_seed(11)
    model = SpatialActorCritic(plan_head=True)
    obs, masks, plan_masks, phase = _phase_batch()
    observations = torch.from_numpy(obs)
    phase_t = torch.from_numpy(phase)

    spatial_only, _ = model(observations)
    _, plan_only, _ = model.forward_with_plan(observations)
    merged, value = tpf.combined_logits(model, observations, phase_t)

    plan_rows = phase == tpf.PHASE_PLAN
    troll_rows = phase == tpf.PHASE_TROLL
    assert torch.allclose(
        merged[plan_rows][:, : tpf.PLAN_SIZE], plan_only[plan_rows], atol=1e-6
    )
    assert not torch.allclose(
        merged[plan_rows][:, : tpf.PLAN_SIZE],
        spatial_only[plan_rows][:, : tpf.PLAN_SIZE],
        atol=1e-6,
    )
    assert torch.allclose(merged[troll_rows], spatial_only[troll_rows], atol=1e-6)
    assert value.shape == (4,)


def test_masked_logits_never_select_an_illegal_action_and_log_probs_stay_finite() -> None:
    torch.manual_seed(13)
    model = SpatialActorCritic(plan_head=True)
    obs, masks, plan_masks, phase = _phase_batch(seed=5)
    legal = tpf.build_legal(masks, plan_masks, phase)
    legal_t = torch.from_numpy(legal).bool()
    logits, _ = tpf.combined_logits(model, torch.from_numpy(obs), torch.from_numpy(phase))
    masked = tpf.masked_logits(logits, legal_t)

    distribution = Categorical(logits=masked)
    for _ in range(50):
        actions = distribution.sample()
        for row, action in enumerate(actions.tolist()):
            assert legal[row, action] == 1
    assert torch.isfinite(masked.argmax(dim=-1).float()).all()
    for row in range(4):
        assert legal[row, int(masked[row].argmax())] == 1

    # An illegal action's log-probability is a large finite negative number, never -inf, so the
    # PPO ratio and the entropy stay finite (July's finfo.min masking).
    illegal = np.array(
        [int(np.flatnonzero(legal[row] == 0)[0]) for row in range(4)], dtype=np.int64
    )
    logprob = distribution.log_prob(torch.from_numpy(illegal))
    assert torch.isfinite(logprob).all()
    assert (logprob < -1e30).all()
    assert torch.isfinite(distribution.entropy()).all()


# --------------------------------------------------------------------------- 3. the smoke run


def _fake_run_argv(tmp_path: Path, extra: list[str] | None = None) -> list[str]:
    argv = [
        "--env",
        "fake",
        "--num-envs",
        "8",
        "--rollout-steps",
        "8",
        "--total-turn-steps",
        "128",
        "--minibatch-size",
        "32",
        "--update-epochs",
        "1",
        "--threads",
        "2",
        "--seed",
        "77",
        "--checkpoint-every",
        "1",
        "--run-name",
        "smoke",
        "--output-dir",
        str(tmp_path),
        "--maps",
        str(tmp_path / "no-such-maps.jsonl"),
        "--opponent-weights",
        '{"secure_orchard": 1, "python_frozen": 1}',
        "--frozen-refresh-updates",
        "1",
    ]
    return argv + (extra or [])


def test_two_update_smoke_run_writes_a_four_key_checkpoint(tmp_path, capsys) -> None:
    summary = tpf.main(_fake_run_argv(tmp_path))
    assert summary["updates_completed"] == 2
    assert summary["turn_steps"] == 128
    assert summary["turns_completed"] > 0

    lines = [
        json.loads(line)
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("{")
    ]
    updates = [row for row in lines if row.get("event") == "update"]
    assert len(updates) == 2
    for row in updates:
        for key in (
            "policy_loss",
            "value_loss",
            "entropy",
            "approx_kl",
            "mean_episode_return",
            "mean_referee_margin",
            "win_rate",
            "turn_steps_per_second",
            "wall_seconds",
        ):
            assert key in row
        assert row["turn_steps_per_second"] > 0

    checkpoint_path = tmp_path / "smoke-update000002.pt"
    assert checkpoint_path.exists()
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    assert set(checkpoint) == {"model", "optimizer", "config", "evaluation"}
    assert (tmp_path / "smoke-training-summary.json").exists()


def test_the_plan_head_off_model_keeps_julys_state_dict_keys() -> None:
    """`SpatialActorCritic()` must still export: the D11 exporter compares key sets."""

    baseline = SpatialActorCritic()
    assert set(baseline.state_dict()) == {
        "stem.0.weight",
        "stem.0.bias",
        "tower.0.conv1.weight",
        "tower.0.conv1.bias",
        "tower.0.conv2.weight",
        "tower.0.conv2.bias",
        "tower.1.conv1.weight",
        "tower.1.conv1.bias",
        "tower.1.conv2.weight",
        "tower.1.conv2.bias",
        "tower.2.conv1.weight",
        "tower.2.conv1.bias",
        "tower.2.conv2.weight",
        "tower.2.conv2.bias",
        "tower.3.conv1.weight",
        "tower.3.conv1.bias",
        "tower.3.conv2.weight",
        "tower.3.conv2.bias",
        "actor.weight",
        "actor.bias",
        "critic.0.weight",
        "critic.0.bias",
        "critic.2.weight",
        "critic.2.bias",
    }
    assert not any(key.startswith("plan.") for key in baseline.state_dict())
    with_plan = SpatialActorCritic(plan_head=True).state_dict()
    assert set(with_plan) - set(baseline.state_dict()) == {
        "plan.0.weight",
        "plan.0.bias",
        "plan.2.weight",
        "plan.2.bias",
    }
    assert with_plan["plan.2.weight"].shape == (tpf.PLAN_SIZE, 64)
    assert with_plan["plan.0.weight"].shape == (64, 16)


def test_the_fake_environment_has_the_frozen_full_env_surface() -> None:
    with fake.FakeFullVecEnv(4, 0, None, {"secure_orchard": 1.0}) as env:
        assert env.obs.shape == (4, 104, 11, 22) and env.obs.dtype == np.uint8
        assert env.masks.shape == (4, 13, 11, 22) and env.masks.dtype == np.uint8
        assert env.plan_masks.shape == (4, 144) and env.plan_masks.dtype == np.uint8
        assert env.phase.shape == (4,) and env.phase.dtype == np.int32
        assert env.seat_view.shape == (4,) and env.seat_view.dtype == np.int32
        assert env.active_troll.shape == (4,) and env.active_troll.dtype == np.int32
        assert (env.phase == fake.PHASE_PLAN).all()
        assert (env.active_troll == -1).all()

        rng = np.random.default_rng(0)
        seen_boundaries = 0
        for _ in range(200):
            actions = fake.random_legal_actions(env, rng)
            result = env.step(actions)
            rewards, info = tpf.unpack_step(result, 4)
            assert rewards.shape == (4,)
            completed = tpf.info_field(info, "turn_completed")
            # The card's rule: reward only where the turn executed.
            assert not (rewards[completed == 0] != 0).any()
            seen_boundaries += int((completed > 0).sum())
            assert (env.phase != fake.PHASE_EXTERNAL_WAIT).all()
        assert seen_boundaries > 0


# --------------------------------------------------------------------------- 4. the clone anchor


def test_the_anchor_term_is_zero_when_the_anchor_equals_the_policy() -> None:
    torch.manual_seed(17)
    model = SpatialActorCritic(plan_head=True)
    anchor = SpatialActorCritic(plan_head=True)
    anchor.load_state_dict(model.state_dict())

    obs, masks, plan_masks, phase = _phase_batch(seed=9)
    legal = torch.from_numpy(tpf.build_legal(masks, plan_masks, phase)).bool()
    observations = torch.from_numpy(obs)
    phase_t = torch.from_numpy(phase)

    policy_logits, _ = tpf.combined_logits(model, observations, phase_t)
    anchor_logits, _ = tpf.combined_logits(anchor, observations, phase_t)
    kl, agreement = tpf.anchor_kl(
        tpf.masked_logits(policy_logits, legal),
        tpf.masked_logits(anchor_logits, legal),
        legal,
    )
    assert float(kl.detach()) == pytest.approx(0.0, abs=1e-6)
    assert float(agreement.detach()) == pytest.approx(1.0)
    assert torch.isfinite(kl)


def test_the_anchor_term_is_positive_for_a_different_network() -> None:
    torch.manual_seed(19)
    model = SpatialActorCritic(plan_head=True)
    torch.manual_seed(23)
    anchor = SpatialActorCritic(plan_head=True)

    obs, masks, plan_masks, phase = _phase_batch(seed=4)
    legal = torch.from_numpy(tpf.build_legal(masks, plan_masks, phase)).bool()
    policy_logits, _ = tpf.combined_logits(model, torch.from_numpy(obs), torch.from_numpy(phase))
    anchor_logits, _ = tpf.combined_logits(anchor, torch.from_numpy(obs), torch.from_numpy(phase))
    kl, _ = tpf.anchor_kl(
        tpf.masked_logits(policy_logits, legal),
        tpf.masked_logits(anchor_logits, legal),
        legal,
    )
    assert float(kl.detach()) > 0.0
    assert torch.isfinite(kl)


def test_the_anchor_coefficient_decays_linearly() -> None:
    args = tpf.build_parser().parse_args(
        [
            "--anchor-coef",
            "0.1",
            "--anchor-coef-final",
            "0.0",
            "--anchor-decay-steps",
            "1000",
        ]
    )
    assert tpf.anchor_coefficient(args, 0) == pytest.approx(0.1)
    assert tpf.anchor_coefficient(args, 500) == pytest.approx(0.05)
    assert tpf.anchor_coefficient(args, 1000) == pytest.approx(0.0)
    assert tpf.anchor_coefficient(args, 10_000) == pytest.approx(0.0)


def test_a_run_with_an_anchor_equal_to_the_policy_logs_a_zero_anchor_loss(
    tmp_path, capsys
) -> None:
    """End to end: start from a checkpoint and anchor on the same checkpoint.

    The first update's anchor loss must be about zero -- the anchor is the policy at step 0.
    """

    torch.manual_seed(29)
    clone = SpatialActorCritic(plan_head=True)
    clone_path = tmp_path / "clone.pt"
    torch.save({"model": clone.state_dict()}, clone_path)

    tpf.main(
        _fake_run_argv(
            tmp_path,
            [
                "--initial-checkpoint",
                str(clone_path),
                "--anchor-checkpoint",
                str(clone_path),
                "--anchor-coef",
                "0.1",
                "--total-turn-steps",
                "64",
                "--learning-rate",
                "0.0",
            ],
        )
    )
    updates = [
        json.loads(line)
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("{") and '"event": "update"' in line
    ]
    assert updates
    assert updates[0]["anchor_coef"] == pytest.approx(0.1, rel=1e-3)
    assert updates[0]["anchor_loss"] == pytest.approx(0.0, abs=1e-5)
    assert updates[0]["anchor_agreement"] == pytest.approx(1.0)


# --------------------------------------------------------------------------- the bench hook


def test_the_bench_gate_reports_unavailable_rather_than_crashing(tmp_path) -> None:
    missing = tmp_path / "no-bench.py"
    result = tpf.run_bench_gate(tmp_path / "run.pt", script=missing)
    assert result["status"] == "unavailable"
    assert "not on disk" in result["reason"]

    stub = tmp_path / "bench.py"
    stub.write_text(
        "import argparse\n"
        "p = argparse.ArgumentParser()\n"
        "p.add_argument('--maps')\n"
        "p.add_argument('--policy', choices=['random-legal'], default='random-legal')\n"
        "p.parse_args()\n"
    )
    result = tpf.run_bench_gate(tmp_path / "run.pt", script=stub)
    assert result["status"] == "unavailable"
    assert "no checkpoint flag" in result["reason"]
