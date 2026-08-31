"""Tests for the independent critic calibration (`local_claude_1/nn-bot/critic_calibration.py`).

Everything runs on `local_claude_1/nn-bot/fake_full_env.py`, so no Rust library, no checkpoint and
no data file is needed. What is pinned here is what the reading will lean on:

1. the realized return-to-go is the trainer's own discounting -- reward once per turn, no discount
   inside a turn, nothing bootstrapped -- checked against a hand-computed case;
2. the statistics are the statistics: a perfect predictor scores slope 1, intercept 0,
   correlation 1, explained variance 1, and a constant predictor scores an explained variance of
   0 with no slope at all;
3. only complete episodes are measured, and the rows thrown away are counted;
4. the slices partition the rows -- every row is in exactly one bucket of every slice;
5. the network is the trainer's own, is never trained, and the checkpoint file is never written;
6. `--decoding argmax` is reproducible under a fixed seed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"


def _load(name: str, filename: str):
    path = NN_BOT / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cc = _load("critic_calibration_under_test", "critic_calibration.py")
tpf = cc.tpf

from cgauto.train_level1_ppo import sha256  # noqa: E402


def _argv(extra: list[str] | None = None) -> list[str]:
    argv = [
        "--env", "fake",
        "--num-envs", "4",
        "--episodes", "4",
        "--threads", "2",
        "--seed", "77",
        "--maps", "/nonexistent/maps.jsonl",
        "--opponent-weights", '{"secure_orchard": 1, "python_frozen": 1}',
    ]
    return argv + (extra or [])


def _measure(extra: list[str] | None = None) -> dict:
    return cc.measure(cc.build_parser().parse_args(_argv(extra)))


@pytest.fixture(scope="module")
def report() -> dict:
    return cc.measure(cc.build_parser().parse_args(_argv(["--per-episode"])))


# ------------------------------------------------------- 1. the instrument is the trainer's code


def test_the_network_and_reward_functions_are_the_trainer_s_own() -> None:
    assert Path(tpf.__file__).resolve() == (NN_BOT / "train_ppo_full.py").resolve()
    assert cc.combined_logits is tpf.combined_logits
    assert cc.masked_logits is tpf.masked_logits
    assert cc.build_legal is tpf.build_legal
    assert cc.rollout_actions is tpf.rollout_actions


def test_the_report_records_which_trainer_it_measured(report: dict) -> None:
    assert report["event"] == "critic-calibration"
    assert report["instrument"]["train_ppo_full_sha256"] == sha256(NN_BOT / "train_ppo_full.py")
    assert report["instrument"]["critic_calibration_sha256"] == sha256(
        NN_BOT / "critic_calibration.py"
    )


# --------------------------------------------------------------- 2. the realized return-to-go


def test_the_return_to_go_discounts_only_across_turn_boundaries() -> None:
    """Three mini-steps of one turn, then a second turn: the trainer's asymmetry, by hand.

    Rewards land on the executing mini-step (rows 2 and 4 here). Inside a turn no time passes, so
    the plan row and the troll rows of a turn all carry that turn's whole reward; across a turn
    boundary the following return is discounted once.
    """

    rewards = np.array([0.0, 0.0, 1.0, 0.0, 2.0])
    boundary = np.array([0, 0, 1, 0, 1])
    gamma = 0.5
    out = cc.returns_to_go(rewards, boundary, gamma)

    assert out[4] == pytest.approx(2.0)
    assert out[3] == pytest.approx(2.0)              # same turn as row 4, no discount
    assert out[2] == pytest.approx(1.0 + 0.5 * 2.0)  # its own reward, plus the next turn discounted
    assert out[1] == pytest.approx(2.0)
    assert out[0] == pytest.approx(2.0)
    # nothing is bootstrapped: the last turn's return is exactly its own reward
    assert cc.returns_to_go(np.array([5.0]), np.array([1]), 0.9)[0] == pytest.approx(5.0)


def test_the_undiscounted_return_is_the_plain_sum() -> None:
    rewards = np.array([1.0, 2.0, 3.0])
    boundary = np.array([1, 1, 1])
    assert list(cc.returns_to_go(rewards, boundary, 1.0)) == [6.0, 5.0, 3.0]


# --------------------------------------------------------------------------- 3. the statistics


def test_a_perfect_predictor_scores_perfectly() -> None:
    realized = np.array([-1.0, 0.0, 0.5, 2.0, 3.0])
    stats = cc.calibration(realized, realized)
    assert stats["slope"] == pytest.approx(1.0)
    assert stats["intercept"] == pytest.approx(0.0)
    assert stats["correlation"] == pytest.approx(1.0)
    assert stats["explained_variance"] == pytest.approx(1.0)
    assert stats["bias_predicted_minus_realized"] == pytest.approx(0.0)
    assert stats["root_mean_square_error"] == pytest.approx(0.0)


def test_a_constant_predictor_has_no_slope_and_explains_nothing() -> None:
    """The mean of the outcome is the baseline: explained variance 0, and no slope exists."""

    realized = np.array([-1.0, 0.0, 1.0, 2.0])
    stats = cc.calibration(np.full(4, realized.mean()), realized)
    assert stats["slope"] is None
    assert stats["correlation"] is None
    assert stats["explained_variance"] == pytest.approx(0.0)
    assert stats["bias_predicted_minus_realized"] == pytest.approx(0.0)


def test_a_halved_prediction_is_reported_as_a_scale_error() -> None:
    realized = np.array([-2.0, 0.0, 2.0, 4.0])
    stats = cc.calibration(realized / 2.0, realized)
    assert stats["slope"] == pytest.approx(2.0)        # the outcome moves twice as fast
    assert stats["correlation"] == pytest.approx(1.0)  # but the ranking is perfect
    assert stats["explained_variance"] < 1.0           # and the scale error is punished
    assert cc.calibration(np.zeros(0), np.zeros(0)) == {"rows": 0}


def test_the_turn_buckets_are_half_open_bands() -> None:
    edges = [0, 10, 25]
    assert cc.bucket_label(0, edges) == "0-9"
    assert cc.bucket_label(9, edges) == "0-9"
    assert cc.bucket_label(10, edges) == "10-24"
    assert cc.bucket_label(24, edges) == "10-24"
    assert cc.bucket_label(25, edges) == "25+"
    assert cc.bucket_label(9999, edges) == "25+"


# ------------------------------------------------------------ 4. what was measured, and on what


def test_only_complete_episodes_are_measured_and_the_rest_are_counted(report: dict) -> None:
    collection = report["collection"]
    assert collection["episodes_completed"] == collection["episodes_requested"] == 4
    assert collection["hit_mini_step_cap"] is False
    assert collection["rows"] == sum(row["rows"] for row in report["episodes"])
    # the slots still mid-game when the fourth episode ended contributed nothing but are declared
    assert collection["unfinished_rows_discarded"] > 0
    for episode in report["episodes"]:
        assert episode["turns"] > 0
        assert episode["illegal"] == 0


def test_the_mini_step_cap_stops_collection_and_says_so() -> None:
    report = _measure(["--episodes", "1000", "--max-mini-steps", "20"])
    assert report["collection"]["hit_mini_step_cap"] is True
    assert report["collection"]["mini_steps"] == 20


def test_every_slice_partitions_the_rows(report: dict) -> None:
    total = report["collection"]["rows"]
    assert total > 0
    for name, section in report["calibration"]["slices"].items():
        assert section["slice"] == name
        assert sum(group["rows"] for group in section["groups"].values()) == total
    assert report["calibration"]["overall"]["rows"] == total
    assert set(report["calibration"]["slices"]["seat"]["groups"]) <= {"0", "1"}
    assert set(report["calibration"]["slices"]["row_class"]["groups"]) <= {"plan", "troll"}


def test_every_row_of_one_turn_carries_the_same_realized_return() -> None:
    """Inside a turn there is no discount and one reward, so a turn's rows share their outcome.

    Which is what makes the `row_class` slice informative: the plan row and the troll rows of a
    turn are judged against the *same* future, so a difference between the two classes is a
    difference in the critic's predictions, not in what happened. (The class *means* still differ,
    because a turn has one plan row and as many troll rows as the side has trolls.)
    """

    args = cc.build_parser().parse_args(_argv())
    device = torch.device("cpu")
    model, _ = tpf.load_policy(None, device)
    model.eval()
    rows = cc.play(args, model, device)["rows"]

    seen = {}
    for episode, turn, realized in zip(rows["episode"], rows["turn"], rows["realized"]):
        key = (int(episode), int(turn))
        if key in seen:
            assert realized == pytest.approx(seen[key])
        else:
            seen[key] = realized
    assert len(seen) > 10  # the games really did run


# ------------------------------------------------ 5. nothing is trained and nothing is written to


def test_the_measurement_never_trains_and_leaves_the_checkpoint_alone(tmp_path) -> None:
    from cgauto.train_level1_ppo import SpatialActorCritic  # noqa: PLC0415

    model = SpatialActorCritic(plan_head=True)
    path = tmp_path / "checkpoint.pt"
    torch.save(
        {
            "model": model.state_dict(),
            "config": {"plan_vocab_version": tpf.PLAN_VOCAB_VERSION},
            "global_step": 0,
        },
        path,
    )
    digest = sha256(path)

    report = _measure(["--initial-checkpoint", str(path)])

    assert report["checkpoint_sha256"] == digest
    assert sha256(path) == digest
    after, _ = tpf.load_policy(str(path), torch.device("cpu"))
    for name, parameter in after.named_parameters():
        assert torch.equal(parameter.detach(), model.state_dict()[name])


# ------------------------------------------------------------------- 6. reproducible, and usable


def test_argmax_decoding_repeats_exactly_under_the_same_seed() -> None:
    first = _measure(["--decoding", "argmax"])
    again = _measure(["--decoding", "argmax"])
    assert first["calibration"]["overall"] == again["calibration"]["overall"]
    assert first["collection"]["rows"] == again["collection"]["rows"]


def test_a_different_seed_plays_different_games() -> None:
    first = _measure(["--decoding", "argmax"])
    other = _measure(["--decoding", "argmax", "--seed", "9"])
    assert first["collection"]["mean_margin"] != other["collection"]["mean_margin"]


def test_main_writes_the_report_where_it_is_told(tmp_path, capsys) -> None:
    out = tmp_path / "deep" / "calibration.json"
    report = cc.main(_argv(["--out", str(out), "--label", "smoke"]))
    written = json.loads(out.read_text())
    assert written["label"] == "smoke"
    assert written["calibration"]["overall"]["rows"] == report["collection"]["rows"]
    printed = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert printed["event"] == "critic-calibration"


def test_the_rejection_count_is_named_for_what_the_environment_counts(report: dict) -> None:
    """The 08-31 anomaly: 222 "illegal_commands" in one scope-decoded game.

    The environment's counter adds up referee rejections from *both* seats, and against a linked
    opponent it charges a MOVE whose unit did not reach the predicted cell -- a cross-seat
    collision does that with neither side doing anything illegal. The learned side cannot emit an
    unmasked command at all. So the report must not offer a field called `illegal_commands` for a
    reader to quote as this network's fault.
    """

    collection = report["collection"]
    assert "illegal_commands" not in collection
    assert collection["referee_rejections_either_seat"] == 0
    assert collection["episodes_with_referee_rejections"] == 0
    assert "both seats" in collection["referee_rejections_note"]
    assert collection["referee_rejections_either_seat"] == sum(
        episode["illegal"] for episode in report["episodes"]
    )
