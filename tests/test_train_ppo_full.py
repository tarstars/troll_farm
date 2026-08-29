"""Tests for the Phase-3 PPO trainer (`local_claude_1/nn-bot/train_ppo_full.py`).

Everything runs on `local_claude_1/nn-bot/fake_full_env.py`, so no Rust library and no data file
is needed. The four things pinned here are the four the card cares about: the discount inside a
turn, which head the loss uses, the checkpoint format, and the clone anchor.
"""

from __future__ import annotations

import dataclasses
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

from cgauto.train_level1_ppo import (  # noqa: E402
    PLAN_ACTION_SIZE,
    PLAN_ATTRIBUTE_SCALES,
    PLAN_BANK_PLANES,
    PlanCandidateScorer,
    SpatialActorCritic,
    plan_index,
    plan_index_is_legal,
    plan_talents,
)


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


# ------------------------------------------------- the 400-plan vocabulary (card amendment 8)


def test_the_plan_index_formula_round_trips_over_all_400_entries() -> None:
    """Every talent set in the vocabulary maps to its own index and back."""

    assert PLAN_ACTION_SIZE == 400
    seen = {}
    for speed in range(1, 5):
        for carry in range(1, 6):
            for harvest in range(0, 4):
                for chop in range(0, 5):
                    index = plan_index(speed, carry, harvest, chop)
                    assert 0 <= index < PLAN_ACTION_SIZE
                    assert index not in seen
                    seen[index] = (speed, carry, harvest, chop)
                    assert plan_talents(index) == (speed, carry, harvest, chop)
    assert len(seen) == PLAN_ACTION_SIZE
    assert seen[0] == (1, 1, 0, 0)          # entry 0 = "train nothing"
    assert plan_talents(399) == (4, 5, 3, 4)
    # The fake environment must decode identically, or the two drift apart.
    for index in range(PLAN_ACTION_SIZE):
        assert fake.plan_talents(index) == plan_talents(index)


def test_the_plan_mask_has_exactly_one_rule() -> None:
    """Entry 0 is always legal, and so is every other entry (amendment 8, second completion).

    `harvest > carry` was delineate's own restriction, not the game's, and Bubaptik breaks it in
    44 of its 425 purchases; `harvest 0 and chop 0` is legal in the game though no teacher ever
    bought it. Affordability never masks. Only the global unit cap can mask, and it leaves
    entry 0.
    """

    assert plan_index_is_legal(0)
    for index in range(PLAN_ACTION_SIZE):
        assert plan_index_is_legal(index) is True
        assert fake.plan_is_legal(index) is True
    assert not plan_index_is_legal(PLAN_ACTION_SIZE)
    assert not plan_index_is_legal(-1)
    assert len(fake.LEGAL_PLANS) == PLAN_ACTION_SIZE
    # Two entries the old rules refused, both legal now.
    assert plan_index_is_legal(plan_index(2, 1, 3, 1))      # harvest > carry
    assert plan_index_is_legal(plan_index(3, 2, 0, 0))      # harvest 0 and chop 0
    # A plan nobody can pay for is still legal.
    assert plan_index_is_legal(plan_index(4, 5, 3, 4))


def test_the_fake_environment_masks_every_plan_until_the_unit_cap() -> None:
    with fake.FakeFullVecEnv(2, 3, None, {"secure_orchard": 1.0}) as env:
        assert env.plan_masks.sum(axis=1).tolist() == [PLAN_ACTION_SIZE, PLAN_ACTION_SIZE]
        env._slots[0]["trolls"] = env.max_trolls
        env._write_slot(0, env._slots[0])
        assert env.plan_masks[0].sum() == 1 and env.plan_masks[0, 0] == 1


def test_the_per_candidate_head_is_under_two_thousand_weights() -> None:
    scorer = PlanCandidateScorer(width=16)
    count = sum(parameter.numel() for parameter in scorer.parameters())
    assert count < 2000
    # One shared scorer over 399 candidates plus entry 0's own bias -- not a flat 400-way layer.
    assert count < 0.05 * (64 * PLAN_ACTION_SIZE)
    assert scorer.feature_size == 16 + 4 + 4 + 4 + 1 + 1
    model = SpatialActorCritic(plan_head=True)
    logits = model.forward_with_plan(torch.zeros((2, 104, 11, 22), dtype=torch.uint8))[1]
    assert logits.shape == (2, PLAN_ACTION_SIZE)


def _crafted_observation(
    banks: tuple[int, int, int, int],
    trolls: int,
    target: tuple[int, int, int, int] | None,
    height: int = 9,
    width: int = 18,
    iron: bool = True,
) -> np.ndarray:
    """One observation with only the planes the plan head reads filled in."""

    obs = np.zeros((1, 104, 11, 22), dtype=np.uint8)
    obs[0, 0, :height, :width] = 255
    if iron:
        obs[0, 4, height // 2, width // 2] = 255       # plane 4: one iron cell on the map
    for offset, amount in enumerate(banks):
        obs[0, PLAN_BANK_PLANES[offset], :height, :width] = fake.quantize(amount, 64.0)
    obs[0, 57, :height, :width] = fake.quantize(trolls, 12.0)
    if target is not None:
        obs[0, 59, :height, :width] = 255
        for offset, (value, scale) in enumerate(zip(target, PLAN_ATTRIBUTE_SCALES)):
            obs[0, 60 + offset, :height, :width] = fake.quantize(value, scale)
    return obs


def test_the_cost_deficit_and_flag_features_match_a_hand_computation() -> None:
    """A crafted board: bank (10, 3, 40, 5), two trolls, current target (2, 3, 1, 2).

    By hand, for candidate (2, 3, 1, 2):
      cost  = 2 + attribute^2       -> plum 2+4=6, lemon 2+9=11, apple 2+1=3, iron 2+4=6
      deficit = max(cost - bank, 0) -> plum 0, lemon 8, apple 0, iron 1     -> not affordable
    and for candidate (1, 1, 0, 1):
      cost -> 3, 3, 2, 3 ; deficit -> 0, 0, 0, 0                            -> affordable
    """

    banks = (10, 3, 40, 5)
    trolls = 2
    target = (2, 3, 1, 2)
    model = SpatialActorCritic(plan_head=True)
    diagnostics = model.plan_diagnostics(
        torch.from_numpy(_crafted_observation(banks, trolls, target))
    )

    def dequantized(value: float, scale: float) -> float:
        """What the network can actually read back: one byte, then the scale again."""

        return fake.quantize(value, scale) / 255.0 * scale

    bank_hat = [dequantized(amount, 64.0) for amount in banks]
    trolls_hat = dequantized(trolls, 12.0)

    assert diagnostics["banks"][0].tolist() == pytest.approx(bank_hat, abs=1e-4)
    assert diagnostics["banks"][0].tolist() == pytest.approx(list(banks), abs=0.15)
    assert float(diagnostics["troll_count"][0]) == pytest.approx(trolls_hat, abs=1e-4)
    assert diagnostics["target"][0].tolist() == pytest.approx(list(target), abs=0.02)
    assert float(diagnostics["has_target"][0]) == pytest.approx(1.0)

    def by_hand(candidate: tuple[int, int, int, int]) -> tuple[list[float], list[float]]:
        cost = [trolls_hat + attribute**2 for attribute in candidate]
        deficit = [max(c - b, 0.0) for c, b in zip(cost, bank_hat)]
        return cost, deficit

    # Candidate index -> row in the scorer's table (entry 0 is not scored).
    row = plan_index(*target) - 1
    cost, deficit = by_hand(target)
    assert cost == pytest.approx([6, 11, 3, 6], abs=0.03)
    assert deficit == pytest.approx([0, 8, 0, 1], abs=0.06)
    assert diagnostics["cost"][0, row].tolist() == pytest.approx(cost, abs=1e-4)
    assert diagnostics["deficit"][0, row].tolist() == pytest.approx(deficit, abs=1e-4)
    assert float(diagnostics["affordable"][0, row]) == 0.0
    assert float(diagnostics["matches"][0, row]) == 1.0

    cheap = plan_index(1, 1, 0, 1) - 1
    cost, deficit = by_hand((1, 1, 0, 1))
    assert cost == pytest.approx([3, 3, 2, 3], abs=0.03)
    assert deficit == pytest.approx([0, 0, 0, 0], abs=1e-9)
    assert diagnostics["cost"][0, cheap].tolist() == pytest.approx(cost, abs=1e-4)
    assert diagnostics["deficit"][0, cheap].tolist() == pytest.approx(deficit, abs=1e-4)
    assert float(diagnostics["affordable"][0, cheap]) == 1.0
    assert float(diagnostics["matches"][0, cheap]) == 0.0

    # Exactly one candidate is the current target, and only when the target flag is on.
    assert float(diagnostics["matches"][0].sum()) == 1.0
    without = model.plan_diagnostics(
        torch.from_numpy(_crafted_observation(banks, trolls, None))
    )
    assert float(without["matches"][0].sum()) == 0.0


def test_an_iron_free_map_waives_the_iron_cost_and_deficit() -> None:
    """Two boards alike but for one iron cell (plane 4).

    On the iron board the candidate (3, 3, 2, 4) costs iron `1 + 16 = 17` against a bank of 0, so
    it has an iron deficit and is not affordable. On the iron-free board chop can never be paid
    for in iron at all, so the iron cost and deficit are zero and affordability ignores them.
    """

    banks = (40, 40, 40, 0)
    trolls = 1
    model = SpatialActorCritic(plan_head=True)
    candidate = (3, 3, 2, 4)
    row = plan_index(*candidate) - 1

    with_iron = model.plan_diagnostics(
        torch.from_numpy(_crafted_observation(banks, trolls, None, iron=True))
    )
    without_iron = model.plan_diagnostics(
        torch.from_numpy(_crafted_observation(banks, trolls, None, iron=False))
    )

    assert float(with_iron["has_iron"][0]) == 1.0
    assert float(without_iron["has_iron"][0]) == 0.0

    trolls_hat = fake.quantize(trolls, 12.0) / 255.0 * 12.0
    assert float(with_iron["cost"][0, row, 3]) == pytest.approx(trolls_hat + 16, abs=1e-4)
    assert float(with_iron["deficit"][0, row, 3]) == pytest.approx(trolls_hat + 16, abs=1e-4)
    assert float(with_iron["affordable"][0, row]) == 0.0

    assert float(without_iron["cost"][0, row, 3]) == 0.0
    assert float(without_iron["deficit"][0, row, 3]) == 0.0
    assert float(without_iron["affordable"][0, row]) == 1.0

    # The other three resources are untouched by the waiver.
    assert with_iron["cost"][0, row, :3].tolist() == pytest.approx(
        without_iron["cost"][0, row, :3].tolist(), abs=1e-6
    )
    # Every candidate's iron column is zero on the iron-free board, not just this one.
    assert float(without_iron["cost"][0, :, 3].abs().max()) == 0.0
    assert float(without_iron["deficit"][0, :, 3].abs().max()) == 0.0


def test_the_match_column_starts_at_exactly_zero_and_ppo_then_trains_it() -> None:
    """A clone never sees "matches the standing target" set, so that column starts at zero.

    Then the clone's first PPO plan phase scores the candidates identically whether or not a
    target is standing, instead of being kicked by a weight nobody ever trained. The scorer is
    exercised on its own here, with one fixed pooled vector: the shared convolution trunk also
    reads planes 59-63, so this is the only place the invariance can be stated exactly.
    """

    torch.manual_seed(41)
    scorer = PlanCandidateScorer(width=16)
    match_column = scorer.mlp[0].weight[:, scorer.match_feature_index]
    assert torch.equal(match_column, torch.zeros_like(match_column))
    # Every other column keeps its ordinary orthogonal initialisation.
    other = scorer.mlp[0].weight[:, : scorer.match_feature_index].detach()
    assert float(other.abs().sum()) > 0.0

    banks, trolls, target = (10, 10, 10, 10), 2, (2, 4, 1, 3)
    scaled_none = torch.from_numpy(_crafted_observation(banks, trolls, None)).float() / 255.0
    scaled_target = torch.from_numpy(_crafted_observation(banks, trolls, target)).float() / 255.0
    valid = scaled_none[:, :1]
    assert torch.equal(valid, scaled_target[:, :1])
    pooled = torch.randn(1, 16)

    absent = scorer(pooled, scaled_none, valid)
    present = scorer(pooled, scaled_target, valid)
    assert torch.equal(absent, present)          # byte-identical at init

    # One gradient step gives the column a value, and the two part company.
    optimizer = torch.optim.SGD(scorer.parameters(), lr=0.5)
    optimizer.zero_grad(set_to_none=True)
    (-scorer(pooled, scaled_target, valid)[0, plan_index(*target)]).backward()
    optimizer.step()
    trained = scorer.mlp[0].weight[:, scorer.match_feature_index].detach()
    assert float(trained.abs().sum()) > 0.0
    assert not torch.equal(
        scorer(pooled, scaled_none, valid), scorer(pooled, scaled_target, valid)
    )


def test_no_candidate_matches_a_target_that_is_none() -> None:
    """Plane 59 at zero means "no standing target", and then the matches column is all zero.

    This is what keeps behaviour cloning honest: a plan row carries `standing_plan = 0` and zeroed
    planes 59-71, because the previous turn's hindsight label equals the current one between
    purchases and feeding it back would leak the label.
    """

    model = SpatialActorCritic(plan_head=True)
    absent = model.plan_diagnostics(
        torch.from_numpy(_crafted_observation((10, 10, 10, 10), 2, None))
    )
    assert float(absent["has_target"][0]) == 0.0
    assert float(absent["matches"][0].sum()) == 0.0
    assert float(absent["matches"][0].max()) == 0.0

    # Even (1, 1, 0, 0) -- the talents a zeroed target would decode to -- matches nothing,
    # and the flag stays off however the talent planes read.
    leaked = _crafted_observation((10, 10, 10, 10), 2, (1, 1, 0, 0))
    leaked[0, 59] = 0                                  # talents present, the flag off
    still_absent = model.plan_diagnostics(torch.from_numpy(leaked))
    assert float(still_absent["matches"][0].sum()) == 0.0

    # With the flag on, exactly one candidate matches.
    present = model.plan_diagnostics(
        torch.from_numpy(_crafted_observation((10, 10, 10, 10), 2, (2, 4, 1, 3)))
    )
    assert float(present["matches"][0].sum()) == 1.0
    assert float(present["matches"][0, plan_index(2, 4, 1, 3) - 1]) == 1.0


def test_the_plan_head_reacts_to_the_bank_it_reads() -> None:
    """Same trunk, different bank -> different plan logits, so the features really are used."""

    torch.manual_seed(31)
    model = SpatialActorCritic(plan_head=True)
    poor = model.forward_with_plan(
        torch.from_numpy(_crafted_observation((0, 0, 0, 0), 3, None))
    )[1]
    rich = model.forward_with_plan(
        torch.from_numpy(_crafted_observation((60, 60, 60, 60), 3, None))
    )[1]
    assert not torch.allclose(poor, rich)
    # entry 0 is a bare learned bias, so the bank cannot move it
    assert float(poor[0, 0].detach()) == pytest.approx(float(rich[0, 0].detach()))


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


def test_build_legal_keeps_the_plan_mask_below_400_and_zero_above() -> None:
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

    Proved by construction: `combined_logits` writes the plan head's 400 numbers into columns
    0..399 of the PLAN rows and leaves the TROLL rows untouched.
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
        "plan.null_bias",
        "plan.mlp.0.weight",
        "plan.mlp.0.bias",
        "plan.mlp.2.weight",
        "plan.mlp.2.bias",
    }
    # The candidate tables are constants, so they stay out of the checkpoint.
    assert with_plan["plan.mlp.0.weight"].shape == (32, 30)
    assert with_plan["plan.mlp.2.weight"].shape == (1, 32)
    assert with_plan["plan.null_bias"].shape == (1,)


def test_the_fake_environment_has_the_frozen_full_env_surface() -> None:
    with fake.FakeFullVecEnv(4, 0, None, {"secure_orchard": 1.0}) as env:
        assert env.obs.shape == (4, 104, 11, 22) and env.obs.dtype == np.uint8
        assert env.masks.shape == (4, 13, 11, 22) and env.masks.dtype == np.uint8
        assert env.plan_masks.shape == (4, 400) and env.plan_masks.dtype == np.uint8
        assert env.plan_masks.sum(axis=1).min() >= 1
        assert env.phase.shape == (4,) and env.phase.dtype == np.int32
        assert env.seat_view.shape == (4,) and env.seat_view.dtype == np.int32
        assert env.active_troll.shape == (4,) and env.active_troll.dtype == np.int32
        assert (env.phase == fake.PHASE_PLAN).all()
        assert (env.active_troll == -1).all()

        rng = np.random.default_rng(0)
        seen_boundaries = 0
        for _ in range(200):
            actions = fake.random_legal_actions(env, rng)
            # Card amendment (9): step() returns exactly two things.
            rewards, info = env.step(actions)
            assert rewards.shape == (4,) and rewards.dtype == np.float32
            completed = info.turn_completed
            # The card's rule: reward only where the turn executed.
            assert not (rewards[completed == 0] != 0).any()
            seen_boundaries += int((completed > 0).sum())
            assert (env.phase != fake.PHASE_EXTERNAL_WAIT).all()
        assert seen_boundaries > 0


# -------------------------------- the step contract and the generation id (amendments 8 and 9)


def test_step_returns_exactly_rewards_and_the_named_record() -> None:
    """`rewards, info = env.step(actions)`, with `info` carrying exactly the ruled fields."""

    expected = {
        "dones",
        "wins",
        "episode_turns",
        "episode_returns",
        "episode_seeds",
        "map_indices",
        "opponent_ids",
        "score_own",
        "score_opp",
        "trained_specs",
        "trained_turns",
        "trained_count",
        "trained_overflow",
        "illegal_commands",
        "action_hash",
        "state_hash",
        "turn_completed",
    }
    assert {field.name for field in dataclasses.fields(fake.FullStepInfo)} == expected
    assert dataclasses.is_dataclass(fake.FullStepInfo)
    assert fake.FullStepInfo.__dataclass_params__.frozen

    rng = np.random.default_rng(1)
    with fake.FakeFullVecEnv(3, 5, None, {"secure_orchard": 1.0}) as env:
        returned = env.step(fake.random_legal_actions(env, rng))
        assert isinstance(returned, tuple) and len(returned) == 2
        rewards, info = returned
        assert rewards.shape == (3,) and rewards.dtype == np.float32
        assert isinstance(info, fake.FullStepInfo)
        dtypes = {
            "dones": np.uint8,
            "wins": np.uint8,
            "episode_turns": np.uint16,
            "episode_returns": np.float32,
            "episode_seeds": np.uint64,
            "map_indices": np.uint32,
            "opponent_ids": np.uint8,
            "score_own": np.int32,
            "score_opp": np.int32,
            "trained_specs": np.int8,
            "trained_turns": np.uint16,
            "trained_count": np.uint8,
            "trained_overflow": np.uint8,
            "illegal_commands": np.uint16,
            "action_hash": np.uint64,
            "state_hash": np.uint64,
            "turn_completed": np.uint8,
        }
        for name, dtype in dtypes.items():
            array = getattr(info, name)
            assert array.dtype == dtype, name
            assert array.shape[0] == 3, name
        assert info.trained_specs.shape == (3, 4, 4)
        assert info.trained_turns.shape == (3, 4)


def test_the_environment_and_the_trainer_agree_on_the_plan_generation_id() -> None:
    assert fake.PLAN_VOCAB_VERSION == "v400-2026-08-29"
    with fake.FakeFullVecEnv(2, 0, None, {"secure_orchard": 1.0}) as env:
        assert env.plan_version() == tpf.PLAN_VOCAB_VERSION
        assert tpf.check_plan_version(env) == tpf.PLAN_VOCAB_VERSION

    class Stale:
        @staticmethod
        def plan_version() -> str:
            return "v144-2026-08-28"

    with pytest.raises(ValueError, match="plan vocabulary"):
        tpf.check_plan_version(Stale())
    # An environment that does not report one at all is not refused, only unrecorded.
    assert tpf.check_plan_version(object()) is None


def test_a_checkpoint_from_another_plan_vocabulary_is_refused(tmp_path) -> None:
    model = SpatialActorCritic(plan_head=True)
    good = tmp_path / "good.pt"
    torch.save(
        {"model": model.state_dict(), "config": {"plan_vocab_version": tpf.PLAN_VOCAB_VERSION}},
        good,
    )
    tpf.load_policy(str(good), torch.device("cpu"))
    tpf.load_anchor(str(good), torch.device("cpu"))

    stale = tmp_path / "stale.pt"
    torch.save(
        {"model": model.state_dict(), "config": {"plan_vocab_version": "v144-2026-08-28"}}, stale
    )
    with pytest.raises(ValueError, match="v144-2026-08-28"):
        tpf.load_policy(str(stale), torch.device("cpu"))
    with pytest.raises(ValueError, match="v144-2026-08-28"):
        tpf.load_anchor(str(stale), torch.device("cpu"))

    nameless = tmp_path / "nameless.pt"
    torch.save({"model": model.state_dict()}, nameless)
    with pytest.raises(ValueError, match="no 'plan_vocab_version'"):
        tpf.load_policy(str(nameless), torch.device("cpu"))

    # A July checkpoint has no plan head at all: allowed, the plan head starts fresh.
    july = tmp_path / "july.pt"
    torch.save({"model": SpatialActorCritic().state_dict()}, july)
    restored, _ = tpf.load_policy(str(july), torch.device("cpu"))
    assert restored.plan_head


def test_the_run_records_the_generation_id_in_its_checkpoint(tmp_path) -> None:
    tpf.main(_fake_run_argv(tmp_path))
    checkpoint = torch.load(
        tmp_path / "smoke-update000002.pt", map_location="cpu", weights_only=False
    )
    assert checkpoint["config"]["plan_vocab_version"] == tpf.PLAN_VOCAB_VERSION
    assert checkpoint["config"]["plan_action_size"] == PLAN_ACTION_SIZE
    assert checkpoint["config"]["environment_plan_version"] == tpf.PLAN_VOCAB_VERSION


# ---------------------------------------------------- the standing target (amendment 8, memory)


def test_the_standing_target_survives_into_the_next_plan_phase() -> None:
    """At a plan phase the target planes must show the plan chosen on the previous turn.

    Zero at the start of a game; the newly chosen plan right after the plan decision; the same
    plan again at the next plan phase, until a TRAIN buys it.
    """

    with fake.FakeFullVecEnv(1, 11, None, {"secure_orchard": 1.0}) as env:
        assert env.phase[0] == fake.PHASE_PLAN
        assert env.obs[0, 59:72].sum() == 0          # nothing standing at the start of a game

        legal = np.flatnonzero(env.plan_masks[0])
        chosen = int(next(index for index in legal if index != 0))
        env.step(np.array([chosen], dtype=np.int32))

        talents = fake.plan_talents(chosen)
        expected = [
            fake.quantize(value, scale)
            for value, scale in zip(talents, fake.PLAN_ATTRIBUTE_SCALES)
        ]
        assert env.phase[0] == fake.PHASE_TROLL
        assert env.obs[0, 59, 0, 0] == 255           # the newly selected plan is on show
        assert [int(env.obs[0, 60 + i, 0, 0]) for i in range(4)] == expected

        rng = np.random.default_rng(0)
        while env.phase[0] != fake.PHASE_PLAN:
            env.step(fake.random_legal_actions(env, rng))

        # The next plan phase: the same plan is still standing (unless a TRAIN bought it).
        standing = env.obs[0, 59, 0, 0]
        if standing:
            assert [int(env.obs[0, 60 + i, 0, 0]) for i in range(4)] == expected
            assert env.obs[0, 64:68].max() > 0       # its costs are shown too
        else:
            assert env.obs[0, 59:72].sum() == 0      # cleared, so the TRAIN succeeded

        # Over a longer run the standing target is nonzero at plan phases at least sometimes,
        # so the scorer's "matches the standing target" feature is not always off.
        nonzero_at_plan = 0
        for _ in range(400):
            if env.phase[0] == fake.PHASE_PLAN and env.obs[0, 59, 0, 0]:
                nonzero_at_plan += 1
            env.step(fake.random_legal_actions(env, rng))
        assert nonzero_at_plan > 0


def test_the_scorer_sees_the_standing_target_the_fake_environment_shows() -> None:
    """Causal, in the fake environment: choose a plan, and the scorer sees exactly that one.

    This is PPO's case -- the standing target is the environment's own state, the policy's
    previous choice. Nothing here is synthesized from a label.
    """

    model = SpatialActorCritic(plan_head=True)
    with fake.FakeFullVecEnv(1, 21, None, {"secure_orchard": 1.0}) as env:
        # Before any plan is chosen there is no standing target at all.
        assert float(model.plan_diagnostics(torch.from_numpy(env.obs.copy()))["matches"].sum()) == 0.0

        legal = np.flatnonzero(env.plan_masks[0])
        chosen = int(next(index for index in legal if index != 0))
        env.step(np.array([chosen], dtype=np.int32))
        diagnostics = model.plan_diagnostics(torch.from_numpy(env.obs.copy()))
        assert float(diagnostics["matches"][0].sum()) == 1.0
        assert float(diagnostics["matches"][0, chosen - 1]) == 1.0

        # And a different plan on the next turn moves the flag with it.
        rng = np.random.default_rng(2)
        while env.phase[0] != fake.PHASE_PLAN:
            env.step(fake.random_legal_actions(env, rng))
        other = int(next(index for index in np.flatnonzero(env.plan_masks[0]) if index not in (0, chosen)))
        env.step(np.array([other], dtype=np.int32))
        moved = model.plan_diagnostics(torch.from_numpy(env.obs.copy()))
        assert float(moved["matches"][0, other - 1]) == 1.0
        assert float(moved["matches"][0, chosen - 1]) == 0.0


def test_choosing_train_nothing_leaves_no_standing_target() -> None:
    """Entry 0 zeroes planes 59-71, so the matches column is empty -- in the fake too."""

    model = SpatialActorCritic(plan_head=True)
    with fake.FakeFullVecEnv(1, 31, None, {"secure_orchard": 1.0}) as env:
        env.step(np.array([0], dtype=np.int32))
        assert env.obs[0, 59:72].sum() == 0
        diagnostics = model.plan_diagnostics(torch.from_numpy(env.obs.copy()))
        assert float(diagnostics["has_target"][0]) == 0.0
        assert float(diagnostics["matches"][0].sum()) == 0.0


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
    torch.save(
        {
            "model": clone.state_dict(),
            "config": {"plan_vocab_version": tpf.PLAN_VOCAB_VERSION},
        },
        clone_path,
    )

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
