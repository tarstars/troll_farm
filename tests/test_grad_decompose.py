"""Tests for the gradient instrument (`local_claude_1/nn-bot/grad_decompose.py`).

Everything runs on `local_claude_1/nn-bot/fake_full_env.py`, so no Rust library, no checkpoint
and no data file is needed. What is pinned here is what the write-up will lean on:

1. the instrument puts observations through the trainer's own functions, so it cannot drift from
   the trainer's behaviour without this test failing;
2. the value objective's gradient really does reach the shared trunk and really does not reach
   the two action heads directly -- the mechanism chatgpt_1's audit names;
3. the four per-objective gradients sum to the gradient of the combined loss, which is what makes
   them a decomposition of the trainer's step rather than four unrelated numbers;
4. the clip scale is torch's own arithmetic and the cosine is a cosine;
5. the counterfactual steps a copy: the measured network and the checkpoint file come out
   unchanged, and with a zero learning rate nothing moves at all.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[1]
NN_BOT = ROOT / "local_claude_1" / "nn-bot"


def _load(name: str, filename: str):
    path = NN_BOT / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


gd = _load("grad_decompose_under_test", "grad_decompose.py")

#: The trainer module the instrument itself loaded -- deliberately not a second load of the same
#: file, because the point of the identity test below is that there is only ever one.
tpf = gd.tpf

from cgauto.train_level1_ppo import sha256  # noqa: E402


def _argv(extra: list[str] | None = None) -> list[str]:
    """A measurement small enough for a test and large enough to have both row classes."""

    argv = [
        "--env",
        "fake",
        "--num-envs",
        "8",
        "--rollout-steps",
        "16",
        "--minibatch-size",
        "64",
        "--threads",
        "2",
        "--seed",
        "77",
        "--counterfactual-observations",
        "64",
        "--maps",
        "/nonexistent/maps.jsonl",
        "--opponent-weights",
        '{"secure_orchard": 1, "python_frozen": 1}',
    ]
    return argv + (extra or [])


def _measure(extra: list[str] | None = None) -> dict:
    args = gd.build_parser().parse_args(_argv(extra))
    return gd.measure(args)


@pytest.fixture(scope="module")
def report() -> dict:
    return _measure()


# ------------------------------------------------------- 1. the instrument is the trainer's code


def test_the_network_functions_are_the_trainer_s_own_objects() -> None:
    """Not copies of its source: the same function objects.

    If the trainer changes how an observation enters the network -- the plan-target masking, the
    two-head logit row, the masking of illegal actions, the advantage estimator -- the instrument
    changes with it, and a measurement cannot quietly describe a different network from the one
    that trains.
    """

    assert Path(tpf.__file__).resolve() == (NN_BOT / "train_ppo_full.py").resolve()
    assert gd.combined_logits is tpf.combined_logits
    assert gd.masked_logits is tpf.masked_logits
    assert gd.mask_plan_target_planes is tpf.mask_plan_target_planes
    assert gd.anchor_kl is tpf.anchor_kl
    assert gd.build_legal is tpf.build_legal
    assert gd.compute_gae is tpf.compute_gae
    assert gd.build_optimizer is tpf.build_optimizer


def test_the_report_records_which_trainer_it_measured(report: dict) -> None:
    assert report["instrument"]["train_ppo_full_sha256"] == sha256(
        NN_BOT / "train_ppo_full.py"
    )
    assert report["instrument"]["grad_decompose_sha256"] == sha256(
        NN_BOT / "grad_decompose.py"
    )
    assert report["instrument"]["plan_target_memory"] == tpf.PLAN_TARGET_MEMORY
    assert report["instrument"]["plan_vocab_version"] == tpf.PLAN_VOCAB_VERSION


# ------------------------------------------------------------- 2. where the value gradient goes


def test_the_value_objective_reaches_the_trunk_and_not_the_action_heads(report: dict) -> None:
    """The audited mechanism, measured.

    `value_coef * value_loss` is differentiated on its own. Its gradient is non-zero on the value
    head (`critic.*`) and on the shared trunk (`stem.*`, `tower.*`) -- and exactly zero on the
    per-cell head and the plan head, which sit downstream of the trunk and are not on the value
    path. That is the whole point: the value term cannot touch the heads' own weights, so any
    effect it has on the bot's commands travels through the trunk.
    """

    value = report["objectives"]["value"]
    assert value["groups"]["critic"] > 0
    assert value["groups"]["stem"] > 0
    assert value["groups"]["tower"] > 0
    assert value["groups"]["actor"] == 0.0
    assert value["groups"]["plan"] == 0.0
    assert value["grad_norm_trunk"] > 0
    assert 0.0 < value["trunk_share_of_norm"] <= 1.0


def test_the_policy_objective_is_its_own_reference_direction(report: dict) -> None:
    """The cosine of the policy objective's trunk gradient with itself is 1."""

    assert report["objectives"]["policy"]["trunk_cosine_with_policy"] == pytest.approx(
        1.0, abs=1e-5
    )


def test_every_reported_objective_carries_its_coefficient(report: dict) -> None:
    assert report["objectives"]["policy"]["coefficient"] == 1.0
    assert report["objectives"]["value"]["coefficient"] == pytest.approx(0.5)
    assert report["objectives"]["entropy"]["coefficient"] == pytest.approx(0.01)


def test_the_anchor_objective_appears_only_with_an_anchor(report: dict, tmp_path) -> None:
    assert report["objectives"]["anchor"] is None  # no --anchor-checkpoint above

    checkpoint = _smoke_checkpoint(tmp_path)
    with_anchor = _measure(
        ["--anchor-checkpoint", str(checkpoint), "--anchor-turn-steps", "0"]
    )
    assert with_anchor["anchor_coefficient"] == pytest.approx(0.1)
    anchor = with_anchor["objectives"]["anchor"]
    assert anchor is not None
    assert anchor["coefficient"] == pytest.approx(0.1)
    # The anchor pulls the two heads back towards the clone, so its gradient lands on them.
    assert anchor["grad_norm_total"] > 0


# ------------------------------------------------- 3. the four pieces are pieces of the real step


def test_the_objectives_sum_to_the_gradient_of_the_combined_loss(report: dict) -> None:
    """Gradients are linear, so a decomposition that is honest must add back up.

    This is what licenses reading the four rows of the report as "the parts of the update's one
    backward pass" rather than four separately interesting numbers.
    """

    check = report["linearity_check"]
    assert check["max_abs_difference"] < 1e-5
    assert check["max_abs_difference"] < 1e-3 * max(check["combined_grad_norm"], 1e-6)


def test_the_row_class_split_measures_both_kinds_of_mini_step(report: dict) -> None:
    split = report["by_row_class"]
    assert split["plan"]["measured"] and split["troll"]["measured"]
    assert split["plan"]["rows"] + split["troll"]["rows"] == report["minibatch"]["minibatch_rows"]
    # A PLAN row trains the plan head and a TROLL row the per-cell head; the policy gradient
    # therefore lands on one head or the other, never on both.
    assert split["plan"]["objectives"]["policy"]["groups"]["actor"] == 0.0
    assert split["troll"]["objectives"]["policy"]["groups"]["plan"] == 0.0
    # But the value term is in the trunk on both kinds of row.
    for label in ("plan", "troll"):
        assert split[label]["objectives"]["value"]["grad_norm_trunk"] > 0


# --------------------------------------------------------------- 4. the small arithmetic is right


def test_the_cosine_is_one_against_itself_and_minus_one_when_flipped() -> None:
    vector = torch.tensor([1.0, -2.0, 3.0])
    assert gd.cosine(vector, vector) == pytest.approx(1.0)
    assert gd.cosine(vector, -vector) == pytest.approx(-1.0)
    assert gd.cosine(torch.tensor([1.0, 0.0]), torch.tensor([0.0, 1.0])) == pytest.approx(0.0)
    # A gradient of length zero has no direction; the report says so rather than saying
    # "orthogonal".
    assert gd.cosine(torch.zeros(3), vector) is None


def test_the_clip_scale_is_the_factor_torch_would_apply() -> None:
    for max_norm, seed in ((0.5, 0), (0.5, 1), (10.0, 2)):
        torch.manual_seed(seed)
        model = nn.Linear(8, 4)
        loss = model(torch.randn(16, 8)).pow(2).mean()
        loss.backward()
        before = [p.grad.detach().clone() for p in model.parameters()]
        total = float(nn.utils.clip_grad_norm_(model.parameters(), max_norm))
        after = [p.grad.detach().clone() for p in model.parameters()]
        scale = gd.clip_scale(total, max_norm)
        for old, new in zip(before, after):
            assert torch.allclose(old * scale, new, atol=1e-6)


def test_a_gradient_shorter_than_the_limit_is_not_shrunk() -> None:
    assert gd.clip_scale(0.1, 0.5) == 1.0
    assert gd.clip_scale(1.0, 0.5) == pytest.approx(0.5, rel=1e-5)


def test_the_group_of_a_parameter_is_its_module(report: dict) -> None:
    assert gd.group_of("tower.1.conv.weight") == "tower"
    assert gd.group_of("critic.0.bias") == "critic"
    assert set(report["objectives"]["value"]["groups"]) == set(gd.PARAMETER_GROUPS)


# ------------------------------------------------------------------------ 5. the counterfactual


def test_a_zero_learning_rate_counterfactual_moves_nothing() -> None:
    """The control: with no step there is no change, so a non-zero change is the step's doing."""

    still = _measure(["--learning-rate", "0"])
    for variant in ("adam-fresh", "sgd"):
        row = still["counterfactual"][variant]
        assert row["available"]
        assert row["spatial_argmax_changed"] == 0
        assert row["plan_argmax_changed"] == 0
        assert row["max_abs_logit_shift"] == 0.0
        assert row["mean_abs_value_shift"] == 0.0


def test_a_value_only_step_moves_the_action_logits(report: dict) -> None:
    """With the run's own learning rate the value term alone moves both heads' logits.

    Only the size of the move is asserted to be non-zero here -- how big it is, and whether it
    flips decisions, is the measurement, not a property a test may fix.
    """

    row = report["counterfactual"]["adam-fresh"]
    assert row["available"]
    assert row["observations"] == 64
    assert row["mean_abs_logit_shift_spatial"] > 0
    assert row["mean_abs_logit_shift_plan"] > 0
    assert row["mean_abs_value_shift"] > 0
    assert row["spatial_argmax_changed"] >= 0
    assert row["spatial_rows"] + row["plan_rows"] == row["observations"]


def test_the_measurement_leaves_the_network_and_the_checkpoint_alone(tmp_path) -> None:
    """The counterfactual steps a deep copy, and nothing is ever written back to the file."""

    checkpoint = _smoke_checkpoint(tmp_path)
    digest = sha256(checkpoint)
    args = gd.build_parser().parse_args(
        _argv(["--initial-checkpoint", str(checkpoint), "--anchor-turn-steps", "0"])
    )
    model, _ = tpf.load_policy(str(checkpoint), torch.device("cpu"))
    before = {name: p.detach().clone() for name, p in model.named_parameters()}

    gd.measure(args)

    assert sha256(checkpoint) == digest
    after, _ = tpf.load_policy(str(checkpoint), torch.device("cpu"))
    for name, parameter in after.named_parameters():
        assert torch.equal(parameter.detach(), before[name])


def test_the_resumed_variant_uses_the_checkpoint_s_own_optimizer_moments(tmp_path) -> None:
    """`adam-resumed` is the honest step; it is reported when, and only when, it can be taken."""

    without = _measure()
    assert without["optimizer_state_available"] is False
    assert without["counterfactual"]["adam-resumed"]["available"] is False

    checkpoint = _smoke_checkpoint(tmp_path)
    with_state = _measure(
        ["--initial-checkpoint", str(checkpoint), "--anchor-turn-steps", "0"]
    )
    assert with_state["optimizer_state_available"] is True
    resumed = with_state["counterfactual"]["adam-resumed"]
    assert resumed["available"] is True
    # Adam with accumulated moments does not take the same step as Adam from zero.
    fresh = with_state["counterfactual"]["adam-fresh"]
    assert resumed["max_abs_logit_shift"] != fresh["max_abs_logit_shift"]


# --------------------------------------------------------------------- 6. the report as a whole


def test_the_report_carries_every_documented_section(report: dict) -> None:
    assert report["event"] == "grad-decompose"
    for key in (
        "label",
        "checkpoint",
        "instrument",
        "config",
        "minibatch",
        "diagnostics",
        "objectives",
        "combined",
        "linearity_check",
        "by_row_class",
        "counterfactual",
        "timing",
    ):
        assert key in report
    assert set(report["objectives"]) == set(gd.OBJECTIVES)
    assert report["combined"]["clip_scale"] <= 1.0
    assert report["minibatch"]["minibatch_rows"] == 64
    assert report["minibatch"]["plan_rows"] + report["minibatch"]["troll_rows"] == 64
    assert json.dumps(report, sort_keys=True, default=str)


def test_the_same_seed_gives_the_same_measurement() -> None:
    """Nothing in the instrument is left to chance except the seed the caller passes."""

    first = _measure()
    second = _measure()
    for row in (first, second):
        row.pop("timing")
    assert json.dumps(first, sort_keys=True, default=str) == json.dumps(
        second, sort_keys=True, default=str
    )


def test_a_different_seed_gives_a_different_minibatch() -> None:
    other = _measure(["--seed", "78"])
    base = _measure()
    assert other["minibatch"]["value_mean"] != base["minibatch"]["value_mean"]


def test_main_writes_the_report_where_it_is_told(tmp_path, capsys) -> None:
    out = tmp_path / "nested" / "grad.json"
    report = gd.main(_argv(["--out", str(out), "--label", "smoke"]))
    assert report["label"] == "smoke"
    written = json.loads(out.read_text())
    assert written["objectives"]["value"]["groups"]["critic"] > 0
    printed = [
        json.loads(line)
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("{")
    ]
    assert any(row.get("event") == "grad-decompose" for row in printed)


# --------------------------------------------------------------------------------- the fixture


def _smoke_checkpoint(tmp_path: Path) -> Path:
    """A real checkpoint -- weights, optimizer moments, config -- from a two-update fake run."""

    output = tmp_path / "runs"
    tpf.main(
        [
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
            "5",
            "--checkpoint-every",
            "1",
            "--run-name",
            "gradsmoke",
            "--output-dir",
            str(output),
            "--maps",
            str(tmp_path / "no-such-maps.jsonl"),
            "--opponent-weights",
            '{"secure_orchard": 1, "python_frozen": 1}',
        ]
    )
    return output / "gradsmoke-latest.pt"


# ------------------------------------------------- 7. measuring under the run's own settings


def test_the_checkpoint_s_own_settings_can_be_taken_as_defaults(tmp_path) -> None:
    """`--from-checkpoint-config`: a gradient measured under the wrong coefficients is a
    measurement of a run nobody made, so the run's own flags come out of its checkpoint."""

    checkpoint = _smoke_checkpoint(tmp_path)
    args = gd.parse_args(
        _argv(["--initial-checkpoint", str(checkpoint), "--from-checkpoint-config"])
    )
    assert args.config_source.startswith("checkpoint config")
    assert "gamma" in args.config_taken_from_checkpoint
    assert "value_coef" in args.config_taken_from_checkpoint
    # The run wrote its own seed and env into the config; the measurement inherits them.
    assert args.seed == 77  # the command line still wins over the checkpoint's 5
    assert args.env == "fake"

    plain = gd.parse_args(_argv())
    assert plain.config_source == "command line"


def test_from_checkpoint_config_refuses_without_a_checkpoint() -> None:
    with pytest.raises(SystemExit):
        gd.parse_args(_argv(["--from-checkpoint-config"]))


# ----------------------------------------- 7. chatgpt_1's review of 2026-08-30: the three repairs


def _clone_style_checkpoint(tmp_path: Path) -> Path:
    """A checkpoint saved the way `train_clone.py` saves one: Adam over `model.parameters()`.

    That is **one** parameter group. The PPO optimizer has two (actor and critic at different
    learning rates), which is why the clone has no resumable PPO step -- blocker 1 of the review.
    """

    from cgauto.train_level1_ppo import SpatialActorCritic  # noqa: PLC0415

    model = SpatialActorCritic(plan_head=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss = sum(p.square().sum() for p in model.parameters())
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    optimizer.step()  # so the saved state carries real moments, not an empty dict

    path = tmp_path / "clone.pt"
    torch.save(
        {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "config": {"plan_vocab_version": tpf.PLAN_VOCAB_VERSION},
            "global_step": 1,
        },
        path,
    )
    return path


def test_a_one_group_clone_optimizer_is_refused_and_the_measurement_survives(tmp_path) -> None:
    """Blocker 1: the clone's optimizer state cannot be loaded, and must not end the run.

    Before the repair, `load_state_dict` raised on the layout mismatch and the whole clone
    measurement died before writing any JSON. Now the mismatch is a structured result and the
    variants that do not need the saved state are measured as usual.
    """

    checkpoint = _clone_style_checkpoint(tmp_path)
    report = _measure(
        ["--initial-checkpoint", str(checkpoint), "--anchor-turn-steps", "0"]
    )

    assert report["optimizer_state_available"] is True  # it has one; it just does not fit
    compatibility = report["resumed_optimizer"]
    assert compatibility["compatible"] is False
    assert "incompatible" in compatibility["reason"]
    assert compatibility["checkpoint_groups"] == [len(list(_parameters(checkpoint)))]
    assert len(compatibility["ppo_groups"]) == 2

    for section in ("counterfactual", "next_update"):
        assert report[section]["adam-resumed"]["available"] is False
        assert "incompatible" in report[section]["adam-resumed"]["reason"]
    # everything that does not need the saved moments still produced a number
    assert report["counterfactual"]["adam-fresh"]["available"] is True
    assert report["counterfactual"]["sgd"]["available"] is True
    assert report["next_update"]["adam-fresh"]["available"] is True


def _parameters(checkpoint: Path):
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    return saved["optimizer"]["param_groups"][0]["params"]


def test_the_reported_learning_rates_are_the_optimizer_s_own(tmp_path) -> None:
    """The review's fourth correction: a resumed step uses the *saved* (annealed) rates."""

    checkpoint = _smoke_checkpoint(tmp_path)
    saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
    for group in saved["optimizer"]["param_groups"]:
        group["lr"] = 3.0e-7  # as if a long linear anneal had brought it down here
    torch.save(saved, checkpoint)

    report = _measure(
        [
            "--initial-checkpoint",
            str(checkpoint),
            "--anchor-turn-steps",
            "0",
            "--learning-rate",
            "0.00025",
        ]
    )
    resumed = report["next_update"]["adam-resumed"]["arms"]["full"]
    assert resumed["effective_learning_rates"]["actor"] == pytest.approx(3.0e-7)
    assert resumed["effective_learning_rates"]["critic"] == pytest.approx(3.0e-7)
    assert resumed["configured_critic_learning_rate"] == pytest.approx(0.00025)
    # the fresh-Adam arm was never given saved rates, so it uses the configured ones
    fresh = report["next_update"]["adam-fresh"]["arms"]["full"]
    assert fresh["effective_learning_rates"]["critic"] == pytest.approx(0.00025)


def test_full_and_no_value_differ_only_by_the_value_term(report: dict) -> None:
    """Blocker 2: the causal counterfactual is FULL against the same update without V."""

    arms = report["next_update"]["adam-fresh"]["arms"]
    assert arms["full"]["terms_included"] == ["policy", "entropy", "value"]
    assert arms["no_value"]["terms_included"] == ["policy", "entropy"]
    assert arms["full"]["value_path"] == "shared"
    assert arms["full_detached_value"]["value_path"] == "detached"
    # both arms saw the identical rows and the identical loss values for the shared terms
    for key in ("policy", "entropy"):
        assert arms["full"]["loss_terms"][key] == arms["no_value"]["loss_terms"][key]
    comparison = report["next_update"]["adam-fresh"]["comparisons"]["full_vs_no_value"]
    assert comparison["observations"] == report["census"]["rows"]
    assert comparison["max_abs_logit_shift"] > 0


def test_with_no_value_coefficient_full_and_no_value_are_the_same_step() -> None:
    """The closed-form case: delete the value term's weight and the two arms must coincide.

    If `full_vs_no_value` reported movement here, it would be measuring something other than the
    value term -- a different shuffle, a different seed, an accumulated gradient.
    """

    report = _measure(["--value-coef", "0", "--next-update-variants", "adam-fresh"])
    comparison = report["next_update"]["adam-fresh"]["comparisons"]["full_vs_no_value"]
    assert comparison["spatial_argmax_changed"] == 0
    assert comparison["plan_argmax_changed"] == 0
    assert comparison["max_abs_logit_shift"] == pytest.approx(0.0, abs=1e-9)
    assert comparison["mean_abs_value_shift"] == pytest.approx(0.0, abs=1e-9)


def test_the_detached_value_path_keeps_the_value_gradient_out_of_the_trunk() -> None:
    """The structural control: with `pooled.detach()` the value loss reaches `critic.*` only."""

    args = gd.build_parser().parse_args(_argv())
    device = torch.device("cpu")
    model, _ = tpf.load_policy(None, device)
    model.train()
    rng = __import__("numpy").random.default_rng(args.seed)
    batch = gd.collect_minibatch(args, model, device, rng)["batch"]

    for path, expect_trunk in (("shared", True), ("detached", False)):
        terms = gd.objective_losses(model, None, False, batch, args, 0.0, value_path=path)
        gradients = gd.gradients_of(model, terms["terms"]["value"][0])
        trunk = gd.flat_vector(
            gradients,
            [n for n, p in model.named_parameters() if gd.group_of(n) in gd.TRUNK_GROUPS],
        )
        critic = gd.flat_vector(
            gradients, [n for n, _ in model.named_parameters() if n.startswith("critic.")]
        )
        assert float(critic.norm()) > 0
        assert (float(trunk.norm()) > 0) is expect_trunk


def test_the_census_is_deterministic_and_covers_both_row_classes(report: dict) -> None:
    """Blocker 3: one fixed set of positions, drawn the same way every time."""

    census = report["census"]
    assert census["census_version"] == gd.CENSUS_VERSION
    assert census["rows"] == census["plan_rows"] + census["troll_rows"]
    assert census["plan_rows"] > 0 and census["troll_rows"] > 0
    assert census["distinct_environments"] == 8
    assert census["distinct_rollout_steps"] == 16
    again = _measure()
    assert again["census"]["sha256"] == census["sha256"]


def test_a_saved_census_is_the_one_that_is_used(tmp_path) -> None:
    """`--census-out` then `--census-in`: the second run judges on the first run's positions."""

    path = tmp_path / "census.npz"
    first = _measure(["--census-out", str(path)])
    assert path.exists()

    # a different seed collects a different rollout, so its own census would differ ...
    own = _measure(["--seed", "9"])
    assert own["census"]["sha256"] != first["census"]["sha256"]
    # ... but with the file it is judged on the first run's positions
    borrowed = _measure(["--seed", "9", "--census-in", str(path)])
    assert borrowed["census"]["sha256"] == first["census"]["sha256"]
    assert borrowed["census"]["loaded_from"] == str(path)
    assert borrowed["next_update"]["adam-fresh"]["census"]["sha256"] == first["census"]["sha256"]
    assert borrowed["counterfactual"]["sgd"]["census_sha256"] == first["census"]["sha256"]
    # the minibatch the step is taken on is still this run's own, on-policy
    assert borrowed["minibatch"]["advantage_mean_raw"] != first["minibatch"]["advantage_mean_raw"]


def test_an_edited_census_is_refused(tmp_path) -> None:
    """A census that no longer matches its digest is not silently measured on."""

    import numpy as np  # noqa: PLC0415

    path = tmp_path / "census.npz"
    _measure(["--census-out", str(path)])
    with np.load(path, allow_pickle=False) as data:
        arrays = {key: data[key] for key in data.files}
    arrays["phase"] = arrays["phase"][::-1].copy()
    np.savez_compressed(path, **arrays)

    with pytest.raises(SystemExit, match="does not match its recorded sha256"):
        gd.load_census(str(path))


def test_the_census_split_follows_the_rollout_s_own_proportions() -> None:
    """`stratified_rows` is proportional, deterministic and never asks for more than it has."""

    import numpy as np  # noqa: PLC0415

    phase = np.array([tpf.PHASE_PLAN] * 20 + [tpf.PHASE_TROLL] * 80, dtype=np.int64)
    rows = gd.stratified_rows(phase, 50)
    assert len(rows) == 50
    assert list(rows) == sorted(set(rows.tolist()))
    assert int((phase[rows] == tpf.PHASE_PLAN).sum()) == 10
    assert list(gd.stratified_rows(phase, 50)) == list(rows)
    assert len(gd.stratified_rows(phase, 1000)) == 100
    assert len(gd.stratified_rows(phase, 0)) == 0

# ------------------------------- the shared-clip coupling between the two policy-identical arms


def test_the_two_arms_with_identical_policy_gradients_are_compared(report: dict) -> None:
    """`no_value` and `full_detached_value` differ by a term that reaches `critic.*` only.

    Their policy gradients are identical before the clip. The trainer clips one global norm over
    policy and critic parameters together, so they are not identical after it -- and the report
    has to name that channel and put its size next to the effect it produces.
    """

    for variant, block in report["next_update"].items():
        if not block.get("available"):
            continue
        coupling = block["shared_clip_coupling"]
        assert set(coupling["arms"]) == {"no_value", "full_detached_value"}
        assert "sound" not in block, "an equality verdict on these two arms is not a soundness flag"
        if not coupling["available"]:
            continue
        assert set(coupling["clip_scale_applied"]) == {"no_value", "full_detached_value"}
        assert coupling["arms_coincide"] is (
            coupling["policy_max_abs_parameter_difference"] == 0.0
        )
        assert "full_detached_value_vs_no_value" in block["comparisons"]


def test_the_coupling_travels_only_through_the_clip_multiplier(tmp_path) -> None:
    """The claim, executed: fix one clip multiplier for every arm and the two arms coincide.

    This is the proof that the shared global clip is the whole channel between `no_value` and
    `full_detached_value`. With each arm clipped by its own multiplier they may come apart; with
    the FULL arm's multiplier fixed for all of them the difference is exactly zero, because no
    other route from the critic's objective to a policy parameter exists in this arm pair.
    """

    checkpoint = _smoke_checkpoint(tmp_path)
    report = _measure(
        [
            "--initial-checkpoint",
            str(checkpoint),
            "--anchor-turn-steps",
            "0",
            "--next-update-variants",
            "adam-resumed,adam-resumed+common-clip",
        ]
    )
    resumed = report["next_update"]["adam-resumed"]
    fixed = report["next_update"]["adam-resumed+common-clip"]
    if not resumed.get("available") or not fixed.get("available"):
        pytest.skip("this checkpoint's optimizer state does not resume")

    assert fixed["optimizer_variant"] == "adam-resumed"
    assert fixed["common_clip_scale"] is not None
    closed = fixed["shared_clip_coupling"]
    assert closed["clip_channel_closed"] is True
    assert closed["policy_max_abs_parameter_difference"] == 0.0
    assert closed["arms_coincide"] is True
    assert closed["plan_argmax_changed"] == 0
    assert closed["spatial_argmax_changed"] == 0

    open_channel = resumed["shared_clip_coupling"]
    assert open_channel["clip_channel_closed"] is False or (
        open_channel["clip_scale_relative_difference"] == 0.0
    )
    # whatever its size, it is on the record as a coupling rather than as noise
    assert isinstance(open_channel["policy_max_abs_parameter_difference"], float)
    assert isinstance(open_channel["clip_scale_relative_difference"], float)


def _resumed_state(args):
    """A model and a genuinely accumulated Adam state, three real updates in."""

    device = torch.device("cpu")
    model, _ = tpf.load_policy(None, device)
    model.train()
    rng = __import__("numpy").random.default_rng(args.seed)
    collected = gd.collect_minibatch(args, model, device, rng)
    batch = collected["batch"]
    census = gd.build_census(collected["rollout"], int(args.counterfactual_observations), {})
    fixed = gd.census_tensors(census, device)
    fixed["sha256"] = census["meta"]["sha256"]
    fixed["source"] = "this test's own rollout"

    optimizer = tpf.build_optimizer(model, args.learning_rate, args.actor_lr_scale)
    for _ in range(3):
        terms = gd.objective_losses(model, None, False, batch, args, 0.0, value_path="shared")
        loss = sum(terms["terms"][key][0] for key in ("policy", "entropy", "value"))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
        optimizer.step()
    return model, batch, fixed, optimizer.state_dict()


def _two_arms(model, batch, args, fixed, state):
    models, read, arms = {}, {}, {}
    for arm in ("no_value", "full_detached_value"):
        stepped, info = gd.stepped_copy(
            model, None, False, batch, args, 0.0, "adam-resumed", state, arm
        )
        assert info["available"] and info["resumed_optimizer_state"]
        models[arm], read[arm], arms[arm] = stepped, gd.read_out(stepped, fixed), info
    return gd.shared_clip_coupling(models, read, fixed, arms)


def test_an_arm_does_not_consume_the_optimizer_state_the_next_arm_needs() -> None:
    """The defect this instrument had: every arm must resume from the state the run saved.

    `Optimizer.load_state_dict` casts the saved moments to the parameters' dtype and device, and
    when they already match, the cast hands back the *same tensors*. One arm's step then advances
    the caller's `exp_avg`, `exp_avg_sq` and `step` in place, and the arms that follow resume from
    a state one and two updates further on -- so they are no longer counterfactuals of the same
    checkpoint, and the difference between them is arm order, not the terms in their loss.
    """

    args = gd.build_parser().parse_args(_argv())
    model, batch, fixed, state = _resumed_state(args)
    key = sorted(state["state"])[0]
    before = {
        field: state["state"][key][field].clone()
        for field in ("exp_avg", "exp_avg_sq", "step")
    }

    gd.stepped_copy(model, None, False, batch, args, 0.0, "adam-resumed", state, "no_value")

    for field, saved in before.items():
        assert torch.equal(saved, state["state"][key][field]), f"an arm advanced the saved {field}"


def test_the_arms_do_not_depend_on_the_order_they_are_run_in() -> None:
    """The consequence of the fix, stated as the property a reader cares about."""

    args = gd.build_parser().parse_args(_argv())
    model, batch, fixed, state = _resumed_state(args)

    stepped: dict[str, dict] = {}
    for order in (("no_value", "full_detached_value"), ("full_detached_value", "no_value")):
        for arm in order:
            model_after, _ = gd.stepped_copy(
                model, None, False, batch, args, 0.0, "adam-resumed", state, arm
            )
            parameters = {name: p.detach().clone() for name, p in model_after.named_parameters()}
            if arm in stepped:
                assert all(
                    torch.equal(stepped[arm][name], value) for name, value in parameters.items()
                ), f"{arm} moved when only the order around it changed"
            stepped[arm] = parameters


def test_the_two_arms_coincide_exactly_when_the_clip_does_not_bind() -> None:
    """With no clip multiplier to differ, nothing connects the critic term to a policy parameter.

    This is the arithmetic that the shared global clip -- and only the shared global clip -- takes
    away: `full_detached_value`'s gradient reaches `critic.*`, `critic.*` produces no action
    logit, so with both arms scaled the same the policy parameters must land bit for bit together.
    """

    args = gd.build_parser().parse_args(_argv())
    model, batch, fixed, state = _resumed_state(args)
    args.max_grad_norm = 1e9  # far above any gradient here: the clip cannot bind
    coupling = _two_arms(model, batch, args, fixed, state)
    assert coupling["clip_active"] is False
    assert coupling["clip_scale_relative_difference"] == 0.0
    assert coupling["policy_max_abs_parameter_difference"] == 0.0
    assert coupling["plan_argmax_changed"] == 0
    assert coupling["spatial_argmax_changed"] == 0


def test_the_coupling_measure_is_not_inert() -> None:
    """The negative control: make the clip bind, and the two arms have to come apart.

    The critic gradient enters the one global norm, so the two arms are scaled by different
    multipliers, and that difference reaches every policy parameter. If this test ever stops
    seeing a difference, the measure has stopped measuring the coupling it is named for.
    """

    args = gd.build_parser().parse_args(_argv())
    model, batch, fixed, state = _resumed_state(args)
    args.max_grad_norm = 1e-3  # far below the gradient here: the clip binds in both arms
    coupling = _two_arms(model, batch, args, fixed, state)
    assert coupling["available"] is True
    assert coupling["clip_active"] is True
    assert coupling["clip_scale_relative_difference"] > 0.0
    assert coupling["policy_max_abs_parameter_difference"] > 0.0
    assert coupling["arms_coincide"] is False
    assert coupling["clip_channel_closed"] is False


def test_an_unknown_variant_suffix_is_an_error() -> None:
    """`+common-clip` is the only suffix; anything else is refused rather than ignored."""

    assert gd.parse_next_update_variant("adam-resumed") == ("adam-resumed", False)
    assert gd.parse_next_update_variant("adam-resumed+common-clip") == ("adam-resumed", True)
    with pytest.raises(ValueError):
        gd.parse_next_update_variant("adam-resumed+no-clip")


# ---------------------------------------- the decision-margin measure and the minibatch replication


def test_every_comparison_carries_a_decision_margin(report: dict) -> None:
    """An argmax flip sees nothing until a decision changes hands; the margin is the continuous
    version, and chatgpt_1's 08:40Z point is that a verdict must not rest on flips alone."""

    for block in report["next_update"].values():
        if not block.get("available"):
            continue
        for name, comparison in block["comparisons"].items():
            margin = comparison["decision_margin"]
            assert set(margin) == {"plan", "spatial"}, name
            for row_class in margin.values():
                if row_class is None:
                    continue
                assert row_class["median_margin_before"] >= 0.0
                for field in (
                    "fraction_margin_shrank_10_percent",
                    "fraction_margin_shrank_25_percent",
                    "fraction_margin_shrank_50_percent",
                    "fraction_margin_crossed",
                ):
                    assert 0.0 <= row_class[field] <= 1.0
                assert (
                    row_class["fraction_margin_shrank_50_percent"]
                    <= row_class["fraction_margin_shrank_25_percent"]
                    <= row_class["fraction_margin_shrank_10_percent"]
                )


def test_a_network_compared_with_itself_has_moved_no_margin() -> None:
    """The measure's zero: nothing changed, so nothing came closer to flipping."""

    args = gd.build_parser().parse_args(_argv())
    device = torch.device("cpu")
    model, _ = tpf.load_policy(None, device)
    model.train()
    rng = __import__("numpy").random.default_rng(args.seed)
    collected = gd.collect_minibatch(args, model, device, rng)
    census = gd.build_census(collected["rollout"], int(args.counterfactual_observations), {})
    fixed = gd.census_tensors(census, device)
    read = gd.read_out(model, fixed)

    margin = gd.difference(read, read, fixed)["decision_margin"]
    for row_class in margin.values():
        if row_class is None:
            continue
        assert row_class["mean_margin_change"] == 0.0
        assert row_class["fraction_margin_shrank_10_percent"] == 0.0
        assert row_class["fraction_margin_crossed"] == 0.0


def test_a_second_minibatch_seed_is_a_different_draw_of_the_same_rollout() -> None:
    """The replication: same update, other rows. A conclusion that holds only for the rows this
    update happened to draw is not a conclusion."""

    report = _measure(["--minibatch-seeds", "2", "--next-update-variants", "adam-fresh"])
    assert report["minibatch"]["minibatch_seeds"] == 2
    selections = report["minibatch"]["selections"]
    assert [s["minibatch_index"] for s in selections] == [0, 1]
    assert report["minibatch"]["rollout_rows"] == report["config"]["num_envs"] * report["config"][
        "rollout_steps"
    ]

    replications = report["next_update_replications"]
    assert len(replications) == 1
    assert replications[0]["minibatch_index"] == 1
    replicated = replications[0]["variants"]["adam-fresh"]
    primary = report["next_update"]["adam-fresh"]
    assert set(replicated["comparisons"]) == set(primary["comparisons"])
    # a different draw of the same rollout: the same shape, its own numbers
    assert replicated["census"]["sha256"] == primary["census"]["sha256"]


def test_one_minibatch_seed_leaves_the_report_as_it_was(report: dict) -> None:
    """The default is unchanged: one selection, no replications, the old fields in place."""

    assert report["minibatch"]["minibatch_seeds"] == 1
    assert report["next_update_replications"] == []
    assert report["minibatch"]["minibatch_rows"] > 0
    assert report["minibatch"]["selections"][0]["minibatch_rows"] == report["minibatch"][
        "minibatch_rows"
    ]
