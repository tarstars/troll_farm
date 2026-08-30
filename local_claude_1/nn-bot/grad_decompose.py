#!/usr/bin/env python3
"""Where each of PPO's four objectives pushes the network -- and what the value term alone does.

Card: `coordination/tasks/20260829-nn-bot-way-b.md`.
Charter: `coordination/messages/local_claude_1/20260830T210000Z-20260829-nn-bot-way-b-gradient-handoff.md`.
Falsifier named by chatgpt_1 in `chatgpt_1/nn-way-b/shared-critic-trunk-audit-2026-08-30.md` and
`chatgpt_1/nn-way-b/shared-trunk-value-gradient-audit-2026-08-30.md`.

Plain words for the owner
-------------------------
The bot is one small network with a shared body (the *trunk*: `stem` and `tower`, the convolution
layers that look at the board) and three readers on top of it: the per-cell head that gives a
troll its command, the plan head that picks the turn's training recipe, and the value head that
answers "how good is this position?".

PPO's update adds four things together and takes one step:

    policy loss  -  entropy_coef * entropy  +  value_coef * value loss  +  anchor_coef * anchor KL

The audit's claim is that the third term is not innocent. The value head reads the trunk, so
teaching the value head necessarily pushes the trunk, and the trunk is what the two action heads
read. After the critic warm-up ends there is no `detach()` anywhere on that path, so every step
that improves the value estimate also, silently, moves the commands. If the value target is hard
to fit -- and the runs report exactly that -- the push is large and in no particular direction.

This program measures that instead of arguing about it. It collects one honest minibatch the way
the trainer collects one (same environment, same masks, same temperature-1 sampling, same
advantage estimator), then:

1. backpropagates **each objective separately** on that one minibatch and reports how big its
   gradient is in every part of the network, plus the *cosine* between each objective's push on
   the trunk and the policy objective's push on the trunk -- 1.0 means "pushing the same way",
   0 means "unrelated", a negative number means "pulling against it";
2. reports the global-clip scale the combined gradient would receive (PPO shrinks the whole
   gradient when it is longer than `--max-grad-norm`), so a norm can be read as a real step size;
3. runs the counterfactual: takes a **copy** of the checkpoint, applies one optimizer step of the
   value objective **alone** at the run's actor learning rate, and counts, on a fixed set of
   observations from the same minibatch, how many commands and how many plan choices the network
   would now decide differently, and by how much its logits moved.

Nothing here trains, submits, or touches the platform, and the checkpoint on disk is never
written to.

What "one optimizer step" means (read this before quoting number 3)
-------------------------------------------------------------------
Adam's step size does not scale with the gradient: with fresh moment estimates a first step is
about `lr * sign(gradient)` for every weight, however small the gradient is. That overstates a
mid-run step. The run's real step uses the moments Adam had accumulated over hundreds of updates,
and those are saved inside the checkpoint (`"optimizer"`). So the counterfactual is reported in up
to three variants and the honest one is named first:

* `adam-resumed` -- Adam restored from the checkpoint's own optimizer state. This is the step the
  run would actually have taken. Reported whenever the checkpoint carries optimizer state.
* `adam-fresh` -- Adam from zero moments: the scale-free upper reading.
* `sgd` -- plain `lr * gradient`: the lower reading, and the one that is proportional to the
  gradient norms in part 1.

All three use the actor group's learning rate `--learning-rate * --actor-lr-scale` for everything
that is not `critic.*`, exactly as `build_optimizer` does in the trainer, and all three clip the
value-only gradient with `--max-grad-norm` first, as the update does.

Flags
-----
The instrument takes **the trainer's own argument parser** and adds a few of its own, so a run's
command line can be pasted in verbatim and the measurement is made under that run's settings.
`--initial-checkpoint` is the checkpoint under test; `--anchor-checkpoint` is the clone.
Training-only flags (`--checkpoint-every`, `--gate-*`, `--total-turn-steps`, ...) are accepted and
ignored; `--rollout-steps`, `--num-envs` and `--minibatch-size` decide the minibatch.

Example (the fake environment, no Rust library and no data file needed):

    PYTHONPATH=. /home/tarstars/venvs/nn-bot/bin/python local_claude_1/nn-bot/grad_decompose.py \
        --env fake --num-envs 8 --rollout-steps 16 --minibatch-size 64 \
        --initial-checkpoint local_claude_1/nn-bot/checkpoints/clone.pt \
        --anchor-checkpoint local_claude_1/nn-bot/checkpoints/clone.pt \
        --label clone --out /tmp/grad-clone.json
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions.categorical import Categorical

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cgauto.train_level1_ppo import explained_variance, sha256  # noqa: E402


def load_trainer():
    """`train_ppo_full.py` from the neighbouring file (the directory name has a hyphen in it, so
    it is not an importable package -- the module is loaded by path, as the tests do)."""

    path = Path(__file__).resolve().parent / "train_ppo_full.py"
    spec = importlib.util.spec_from_file_location("nn_bot_train_ppo_full", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


tpf = load_trainer()

#: Every network function is the trainer's own object, not a copy of its source. If the trainer
#: changes how observations enter the network -- the plan-target masking, the two-head row, the
#: masking of illegal actions -- this instrument changes with it. `test_grad_decompose.py` pins
#: that these are the same objects.
combined_logits = tpf.combined_logits
masked_logits = tpf.masked_logits
mask_plan_target_planes = tpf.mask_plan_target_planes
anchor_kl = tpf.anchor_kl
build_legal = tpf.build_legal
compute_gae = tpf.compute_gae
build_optimizer = tpf.build_optimizer

PHASE_PLAN = tpf.PHASE_PLAN
PHASE_TROLL = tpf.PHASE_TROLL
PHASE_EXTERNAL_WAIT = tpf.PHASE_EXTERNAL_WAIT
PLAN_SIZE = tpf.PLAN_SIZE

#: The five parts of the network, by the first component of a parameter's name. `stem` and
#: `tower` together are the shared trunk; `actor` is the per-cell command head, `plan` the
#: 400-wide plan scorer, `critic` the value head.
PARAMETER_GROUPS = ("stem", "tower", "actor", "plan", "critic")
TRUNK_GROUPS = ("stem", "tower")

#: The four terms the update adds together, in the order they appear in the loss.
OBJECTIVES = ("policy", "entropy", "value", "anchor")


# --------------------------------------------------------------------------- small vector maths


def group_of(name: str) -> str:
    """`"tower.1.conv.weight" -> "tower"`. The trainer's own module names, first component."""

    return name.split(".", 1)[0]


def flat_vector(gradients: dict[str, torch.Tensor], names: list[str]) -> torch.Tensor:
    """The named gradients laid end to end, in `named_parameters` order."""

    if not names:
        return torch.zeros(0)
    return torch.cat([gradients[name].reshape(-1) for name in names])


def cosine(left: torch.Tensor, right: torch.Tensor) -> float | None:
    """The cosine between two vectors, or `None` when either has no length at all.

    `None` rather than 0.0 on purpose: a zero gradient has no direction, and reporting 0 would
    read as "orthogonal", which is a claim about direction.
    """

    left_norm = float(left.norm())
    right_norm = float(right.norm())
    if left_norm == 0.0 or right_norm == 0.0:
        return None
    return float(torch.dot(left, right) / (left_norm * right_norm))


def clip_scale(total_norm: float, max_norm: float) -> float:
    """The factor `nn.utils.clip_grad_norm_` would multiply every gradient by.

    Torch computes `max_norm / (total_norm + 1e-6)` and applies it only when it is below 1, so a
    gradient shorter than the limit is left exactly as it is.
    """

    if max_norm <= 0:
        return 1.0
    return float(min(1.0, max_norm / (total_norm + 1e-6)))


def gradients_of(model: nn.Module, loss: torch.Tensor) -> dict[str, torch.Tensor]:
    """One backward pass for one objective: `{parameter name: gradient}`, zeros where unused.

    `torch.autograd.grad` is used instead of `loss.backward()` so that nothing is accumulated
    into `.grad` -- the four objectives never contaminate each other, and the live model is left
    exactly as it was found.
    """

    named = [(name, p) for name, p in model.named_parameters() if p.requires_grad]
    raw = torch.autograd.grad(
        loss, [p for _, p in named], retain_graph=True, allow_unused=True
    )
    return {
        name: (torch.zeros_like(p) if grad is None else grad.detach())
        for (name, p), grad in zip(named, raw)
    }


def describe_gradient(
    model: nn.Module,
    gradients: dict[str, torch.Tensor],
    reference_trunk: torch.Tensor | None,
) -> dict:
    """Norms per part of the network, the trunk's share, and the cosine against a reference."""

    names = [name for name, p in model.named_parameters() if p.requires_grad]
    per_group: dict[str, list[str]] = {group: [] for group in PARAMETER_GROUPS}
    for name in names:
        per_group.setdefault(group_of(name), []).append(name)

    total = flat_vector(gradients, names)
    trunk = flat_vector(
        gradients, [name for name in names if group_of(name) in TRUNK_GROUPS]
    )
    total_norm = float(total.norm())
    report = {
        "grad_norm_total": total_norm,
        "grad_norm_trunk": float(trunk.norm()),
        "trunk_share_of_norm": (
            float(trunk.norm()) / total_norm if total_norm > 0 else None
        ),
        "groups": {
            group: float(flat_vector(gradients, group_names).norm())
            for group, group_names in per_group.items()
        },
        "trunk_cosine_with_policy": (
            None if reference_trunk is None else cosine(trunk, reference_trunk)
        ),
    }
    return report


# --------------------------------------------------------------------------- the minibatch


def collect_minibatch(args, model, device, rng) -> dict:
    """One update's rollout, collected the way the trainer collects it, cut to one minibatch.

    Every piece of this is a trainer function: `make_env` builds the environment (the real one
    when the Rust library is there, `fake_full_env.py` otherwise), `build_legal` builds the
    3,146-wide mask row, `combined_logits` puts the observation through the plan-target masking
    and the two heads, the action is a temperature-1 `Categorical.sample()` exactly as the
    learner plays, and `compute_gae` turns the rewards into advantages with the card's per-turn
    discount and trace. Only the loop is written here.

    The minibatch is the first `--minibatch-size` rows of one shuffle of the rollout, with the
    per-minibatch advantage normalisation the update applies.
    """

    frozen = tpf.FrozenOpponent(model, device)
    env = tpf.make_env(args, frozen)
    buffer = tpf.RolloutBuffer(args.rollout_steps, args.num_envs)
    turns_completed = 0
    try:
        for step_index in range(args.rollout_steps):
            phase_np = np.asarray(env.phase)
            if (phase_np == PHASE_EXTERNAL_WAIT).any():
                raise RuntimeError(
                    "phase 2 EXTERNAL_WAIT reached the instrument; the environment is supposed "
                    "to drive the python_frozen opponent itself"
                )
            legal_np = build_legal(
                np.asarray(env.masks), np.asarray(env.plan_masks), phase_np
            )
            if not legal_np.any(axis=1).all():
                raise RuntimeError("a mini-step arrived with an empty action mask")

            np.copyto(buffer.obs[step_index], env.obs)
            buffer.legal[step_index] = legal_np
            buffer.phase[step_index] = phase_np

            observations = torch.from_numpy(np.ascontiguousarray(env.obs)).to(device)
            phase_t = torch.from_numpy(phase_np.astype(np.int64)).to(device)
            legal_t = torch.from_numpy(legal_np).to(device).bool()
            with torch.no_grad():
                logits, values = combined_logits(model, observations, phase_t)
                distribution = Categorical(logits=masked_logits(logits, legal_t))
                actions = distribution.sample()
                logprobs = distribution.log_prob(actions)

            actions_np = actions.cpu().numpy().astype(np.int64)
            buffer.actions[step_index] = actions_np
            buffer.logprobs[step_index] = logprobs.cpu().numpy()
            buffer.values[step_index] = values.cpu().numpy()

            rewards, info = env.step(actions_np.astype(np.int32, copy=False))
            rewards = np.asarray(rewards, dtype=np.float32)
            completed = info.turn_completed
            if args.reward_credit == "executing":
                rewards = np.where(completed > 0, rewards, np.float32(0.0))
            buffer.rewards[step_index] = rewards * args.reward_scale
            buffer.dones[step_index] = info.dones.astype(np.float32)
            buffer.turn_boundary[step_index] = completed
            turns_completed += int((completed > 0).sum())

        phase_np = np.asarray(env.phase)
        with torch.no_grad():
            _, bootstrap = combined_logits(
                model,
                torch.from_numpy(np.ascontiguousarray(env.obs)).to(device),
                torch.from_numpy(phase_np.astype(np.int64)).to(device),
            )
    finally:
        close = getattr(env, "close", None)
        if callable(close):
            close()

    advantages, returns = compute_gae(
        buffer.rewards,
        buffer.values,
        buffer.dones,
        buffer.turn_boundary,
        bootstrap.cpu().numpy(),
        args.gamma,
        args.gae_lambda,
    )
    flat = buffer.flat()
    flat_advantages = advantages.reshape(buffer.size)
    flat_returns = returns.reshape(buffer.size)

    indices = np.arange(buffer.size)
    rng.shuffle(indices)
    rows = indices[: min(args.minibatch_size, buffer.size)]

    mb_advantages = torch.from_numpy(flat_advantages[rows]).to(device)
    normalised = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)
    batch = {
        "obs": torch.from_numpy(flat["obs"][rows]).to(device),
        "legal": torch.from_numpy(flat["legal"][rows]).to(device).bool(),
        "phase": torch.from_numpy(flat["phase"][rows]).to(device),
        "actions": torch.from_numpy(flat["actions"][rows]).to(device),
        "old_logprobs": torch.from_numpy(flat["logprobs"][rows]).to(device),
        "advantages": normalised,
        "returns": torch.from_numpy(flat_returns[rows]).to(device),
    }
    summary = {
        "rollout_steps": int(args.rollout_steps),
        "num_envs": int(args.num_envs),
        "rollout_rows": int(buffer.size),
        "minibatch_rows": int(len(rows)),
        "plan_rows": int((batch["phase"] == PHASE_PLAN).sum()),
        "troll_rows": int((batch["phase"] == PHASE_TROLL).sum()),
        "turns_completed": turns_completed,
        "turn_boundary_rows": int(buffer.turn_boundary.reshape(buffer.size)[rows].sum()),
        "reward_rows_nonzero": int((buffer.rewards.reshape(buffer.size)[rows] != 0).sum()),
        "advantage_mean_raw": float(mb_advantages.mean()),
        "advantage_std_raw": float(mb_advantages.std()),
        "return_mean": float(batch["returns"].mean()),
        "return_std": float(batch["returns"].std()),
        "value_mean": float(torch.from_numpy(flat["values"][rows]).mean()),
        "explained_variance_rollout": explained_variance(flat["values"], flat_returns),
    }
    return {"batch": batch, "summary": summary}


# --------------------------------------------------------------------------- the four objectives


def objective_losses(model, anchor, anchor_has_plan, batch, args, anchor_coef) -> dict:
    """The four terms of the update's loss, each with its coefficient already applied.

    One forward pass feeds all four, exactly as the update's single `loss.backward()` does, so
    the four gradients measured here are the four pieces that combined gradient is made of --
    `linearity_check` in the report proves it, by comparing their sum with the gradient of the
    sum.
    """

    logits, new_value = combined_logits(model, batch["obs"], batch["phase"])
    policy_masked = masked_logits(logits, batch["legal"])
    distribution = Categorical(logits=policy_masked)
    new_logprob = distribution.log_prob(batch["actions"])
    entropy = distribution.entropy()

    log_ratio = new_logprob - batch["old_logprobs"]
    ratio = log_ratio.exp()
    policy_loss = torch.maximum(
        -batch["advantages"] * ratio,
        -batch["advantages"] * ratio.clamp(1.0 - args.clip_coef, 1.0 + args.clip_coef),
    ).mean()
    value_loss = 0.5 * (new_value - batch["returns"]).pow(2).mean()
    entropy_loss = entropy.mean()

    terms = {
        "policy": (policy_loss, 1.0, float(policy_loss.detach())),
        "entropy": (
            -args.entropy_coef * entropy_loss,
            float(args.entropy_coef),
            float(entropy_loss.detach()),
        ),
        "value": (
            args.value_coef * value_loss,
            float(args.value_coef),
            float(value_loss.detach()),
        ),
    }

    anchor_agreement = None
    if anchor is not None and anchor_coef != 0.0:
        keep = (
            torch.ones_like(batch["phase"], dtype=torch.bool)
            if anchor_has_plan
            else (batch["phase"] == PHASE_TROLL)
        )
        if bool(keep.any()):
            with torch.no_grad():
                anchor_logits, _ = combined_logits(
                    anchor, batch["obs"][keep], batch["phase"][keep]
                )
                anchor_masked = masked_logits(anchor_logits, batch["legal"][keep])
            kl, agreement = anchor_kl(
                policy_masked[keep], anchor_masked, batch["legal"][keep]
            )
            terms["anchor"] = (anchor_coef * kl, float(anchor_coef), float(kl.detach()))
            anchor_agreement = float(agreement.detach())

    diagnostics = {
        "policy_loss": float(policy_loss.detach()),
        "value_loss": float(value_loss.detach()),
        "entropy": float(entropy_loss.detach()),
        "approx_kl": float(((ratio - 1.0) - log_ratio).mean().detach()),
        "clip_fraction": float(
            ((ratio - 1.0).abs() > args.clip_coef).float().mean().detach()
        ),
        "anchor_agreement": anchor_agreement,
        "value_prediction_mean": float(new_value.mean().detach()),
    }
    return {"terms": terms, "diagnostics": diagnostics}


def decompose(model, anchor, anchor_has_plan, batch, args, anchor_coef) -> dict:
    """Part 1 and part 2: per-objective gradients, trunk cosines, and the global-clip scale."""

    computed = objective_losses(model, anchor, anchor_has_plan, batch, args, anchor_coef)
    terms = computed["terms"]

    names = [name for name, p in model.named_parameters() if p.requires_grad]
    trunk_names = [name for name in names if group_of(name) in TRUNK_GROUPS]

    gradients = {key: gradients_of(model, value[0]) for key, value in terms.items()}
    policy_trunk = flat_vector(gradients["policy"], trunk_names)

    objectives = {}
    for key in OBJECTIVES:
        if key not in gradients:
            objectives[key] = None
            continue
        report = describe_gradient(model, gradients[key], policy_trunk)
        report["coefficient"] = terms[key][1]
        report["raw_loss"] = terms[key][2]
        objectives[key] = report

    combined_loss = sum(value[0] for value in terms.values())
    combined_gradients = gradients_of(model, combined_loss)
    combined = describe_gradient(model, combined_gradients, policy_trunk)
    combined["clip_scale"] = clip_scale(
        combined["grad_norm_total"], float(args.max_grad_norm)
    )
    combined["max_grad_norm"] = float(args.max_grad_norm)

    # The proof that the four pieces above really are the pieces of the step the trainer takes:
    # gradients are linear, so their sum must equal the gradient of the summed loss.
    summed = {
        name: sum(gradients[key][name] for key in gradients) for name in names
    }
    linearity = max(
        float((summed[name] - combined_gradients[name]).abs().max()) for name in names
    )

    return {
        "objectives": objectives,
        "combined": combined,
        "linearity_check": {
            "max_abs_difference": linearity,
            "combined_grad_norm": combined["grad_norm_total"],
        },
        "diagnostics": computed["diagnostics"],
    }


def decompose_by_row_class(model, anchor, anchor_has_plan, batch, args, anchor_coef) -> dict:
    """The same decomposition restricted to the PLAN rows and to the TROLL rows separately.

    chatgpt_1's audits ask which rows the erosion lands on: the fruit-chain commands decay first,
    and the plan head and the per-cell head are trained on disjoint mini-steps. A row class with
    too few rows to normalise an advantage is reported as `null` rather than measured.
    """

    out: dict[str, dict | None] = {}
    for label, phase_value in (("plan", PHASE_PLAN), ("troll", PHASE_TROLL)):
        rows = batch["phase"] == phase_value
        count = int(rows.sum())
        if count < 2:
            out[label] = {"rows": count, "measured": False}
            continue
        subset = {key: value[rows] for key, value in batch.items()}
        part = decompose(model, anchor, anchor_has_plan, subset, args, anchor_coef)
        out[label] = {
            "rows": count,
            "measured": True,
            "objectives": part["objectives"],
            "combined": part["combined"],
        }
    return out


# --------------------------------------------------------------------------- the counterfactual


def counterfactual_value_step(
    model, batch, args, variant: str, optimizer_state: dict | None, rows: int
) -> dict:
    """Part 3: one optimizer step of the value objective alone, on a copy of the network.

    The copy is what is stepped; the caller's model is never touched. The step is the trainer's:
    two parameter groups from `build_optimizer`, so everything that is not `critic.*` moves at
    `--learning-rate * --actor-lr-scale`, and the gradient is clipped with `--max-grad-norm`
    first. Then, on `rows` fixed observations taken from the head of the same minibatch, we ask
    the before and after networks what they would do.

    What is counted:

    * `spatial_argmax_changed` -- TROLL rows whose chosen command changed. This is the number the
      audit is about: a value-only step, and the bot gives a different order.
    * `plan_argmax_changed` -- PLAN rows whose chosen training recipe changed.
    * `mean_abs_logit_shift` -- the average size of the move in the head's logits over the legal
      actions only, per head. Illegal entries are masked to a constant and cannot move.
    """

    copy_model = copy.deepcopy(model)
    optimizer = build_optimizer(copy_model, args.learning_rate, args.actor_lr_scale)
    if variant == "sgd":
        critic_parameters, policy_parameters = tpf.split_parameters(copy_model)
        optimizer = torch.optim.SGD(
            [
                {
                    "params": policy_parameters,
                    "lr": float(args.learning_rate) * float(args.actor_lr_scale),
                },
                {"params": critic_parameters, "lr": float(args.learning_rate)},
            ]
        )
    elif variant == "adam-resumed":
        if optimizer_state is None:
            return {"available": False, "reason": "the checkpoint carries no optimizer state"}
        optimizer.load_state_dict(optimizer_state)

    fixed = {key: value[:rows] for key, value in batch.items()}

    with torch.no_grad():
        before_logits, before_value = combined_logits(
            copy_model, fixed["obs"], fixed["phase"]
        )
        before_masked = masked_logits(before_logits, fixed["legal"])
        before_choice = before_masked.argmax(dim=-1)

    _, new_value = combined_logits(copy_model, batch["obs"], batch["phase"])
    loss = args.value_coef * 0.5 * (new_value - batch["returns"]).pow(2).mean()
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    applied_norm = float(
        nn.utils.clip_grad_norm_(copy_model.parameters(), args.max_grad_norm)
    )
    optimizer.step()

    with torch.no_grad():
        after_logits, after_value = combined_logits(
            copy_model, fixed["obs"], fixed["phase"]
        )
        after_masked = masked_logits(after_logits, fixed["legal"])
        after_choice = after_masked.argmax(dim=-1)

    changed = before_choice != after_choice
    plan_rows = fixed["phase"] == PHASE_PLAN
    troll_rows = fixed["phase"] == PHASE_TROLL
    shift = (after_logits - before_logits).abs()
    legal = fixed["legal"]

    def mean_shift(rows_mask: torch.Tensor, columns: slice) -> float | None:
        if not bool(rows_mask.any()):
            return None
        window = shift[rows_mask][:, columns]
        window_legal = legal[rows_mask][:, columns]
        if not bool(window_legal.any()):
            return None
        return float(window[window_legal].mean())

    return {
        "available": True,
        "variant": variant,
        "observations": int(fixed["obs"].shape[0]),
        "value_loss_before_step": float(loss.detach()) / max(float(args.value_coef), 1e-12),
        "grad_norm_before_clip": applied_norm,
        "clip_scale_applied": clip_scale(applied_norm, float(args.max_grad_norm)),
        "actor_learning_rate": float(args.learning_rate) * float(args.actor_lr_scale),
        "critic_learning_rate": float(args.learning_rate),
        "spatial_rows": int(troll_rows.sum()),
        "spatial_argmax_changed": int((changed & troll_rows).sum()),
        "spatial_argmax_changed_fraction": (
            float((changed & troll_rows).sum() / troll_rows.sum())
            if bool(troll_rows.any())
            else None
        ),
        "plan_rows": int(plan_rows.sum()),
        "plan_argmax_changed": int((changed & plan_rows).sum()),
        "plan_argmax_changed_fraction": (
            float((changed & plan_rows).sum() / plan_rows.sum())
            if bool(plan_rows.any())
            else None
        ),
        "mean_abs_logit_shift_spatial": mean_shift(troll_rows, slice(None)),
        "mean_abs_logit_shift_plan": mean_shift(plan_rows, slice(0, PLAN_SIZE)),
        "mean_abs_value_shift": float((after_value - before_value).abs().mean()),
        "max_abs_logit_shift": float(shift.max()),
    }


# --------------------------------------------------------------------------- the run


def build_parser() -> argparse.ArgumentParser:
    """The trainer's parser, plus this instrument's own flags.

    Reusing it is deliberate: the measurement must be made under the run's settings, and a run's
    command line can then be pasted in unchanged. `--initial-checkpoint` names the checkpoint
    under test.
    """

    parser = tpf.build_parser()
    parser.description = (
        "per-objective gradient decomposition and the value-only counterfactual step "
        "(card 20260829-nn-bot-way-b, chatgpt_1's shared-trunk falsifier)"
    )
    group = parser.add_argument_group("the instrument")
    group.add_argument(
        "--label", default=None, help="a name for this measurement in the report, e.g. 'ppo-h-500'"
    )
    group.add_argument("--out", default=None, help="write the JSON report here as well as to stdout")
    group.add_argument(
        "--counterfactual-observations",
        type=int,
        default=512,
        help="how many rows from the head of the minibatch the value-only step is judged on",
    )
    group.add_argument(
        "--counterfactual-variants",
        default="adam-resumed,adam-fresh,sgd",
        help="comma-separated; 'adam-resumed' uses the checkpoint's own optimizer moments",
    )
    group.add_argument(
        "--anchor-turn-steps",
        type=int,
        default=-1,
        help="the run's turn_steps, which decides the decayed anchor coefficient; -1 reads it "
        "from the checkpoint's evaluation record",
    )
    group.add_argument(
        "--from-checkpoint-config",
        action="store_true",
        default=False,
        help="take every training flag from the checkpoint's own saved config, so the "
        "measurement is made under the settings the run actually used; anything given "
        "explicitly on the command line still wins",
    )
    group.add_argument(
        "--no-row-class-split",
        dest="row_class_split",
        action="store_false",
        default=True,
        help="skip the separate PLAN-row and TROLL-row decomposition",
    )
    return parser


#: Flags that describe this measurement, not the run, and are therefore never taken from a
#: checkpoint's saved config.
NOT_FROM_CONFIG = frozenset(
    {
        "initial_checkpoint",
        "from_checkpoint_config",
        "label",
        "out",
        "counterfactual_observations",
        "counterfactual_variants",
        "anchor_turn_steps",
        "row_class_split",
        "device",
        "threads",
        "output_dir",
        "run_name",
        "total_turn_steps",
        "checkpoint_every",
        "gate_every",
        "gate_games",
        "gate_maps",
        "gate_bot",
        "update_epochs",
        "episode_window",
    }
)


def parse_args(argv: list[str] | None = None):
    """The command line, optionally with the checkpoint's own run settings underneath it.

    A gradient measured under the wrong `--gamma`, `--value-coef` or `--actor-lr-scale` is a
    measurement of a run nobody made. With `--from-checkpoint-config` the checkpoint's saved
    config becomes the defaults and the command line is parsed a second time on top of them, so
    an explicitly given flag still wins and the report records which settings came from where.
    """

    parser = build_parser()
    args = parser.parse_args(argv)
    args.config_source = "command line"
    if not args.from_checkpoint_config:
        return args
    if not args.initial_checkpoint:
        raise SystemExit("--from-checkpoint-config needs --initial-checkpoint")
    checkpoint = torch.load(
        Path(args.initial_checkpoint), map_location="cpu", weights_only=False
    )
    config = checkpoint.get("config") if isinstance(checkpoint, dict) else None
    if not isinstance(config, dict):
        raise SystemExit(
            f"checkpoint {args.initial_checkpoint} carries no 'config' to take settings from"
        )
    known = set(vars(args))
    taken = {
        key: value
        for key, value in config.items()
        if key in known and key not in NOT_FROM_CONFIG
    }
    parser.set_defaults(**taken)
    args = parser.parse_args(argv)
    args.config_source = "checkpoint config, overridden by the command line"
    args.config_taken_from_checkpoint = sorted(taken)
    return args


def read_optimizer_state(path: str | None) -> tuple[dict | None, int | None]:
    """The checkpoint's saved Adam moments and its recorded `turn_steps`, if it has them."""

    if not path:
        return None, None
    checkpoint = torch.load(Path(path), map_location="cpu", weights_only=False)
    if not isinstance(checkpoint, dict):
        return None, None
    state = checkpoint.get("optimizer")
    evaluation = checkpoint.get("evaluation")
    turn_steps = (
        int(evaluation["turn_steps"])
        if isinstance(evaluation, dict) and evaluation.get("turn_steps") is not None
        else None
    )
    return state, turn_steps


def measure(args) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed % (2**32))
    torch.set_num_threads(max(1, args.threads))
    device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requires an available CUDA device")
    rng = np.random.default_rng(args.seed)
    started = time.perf_counter()

    model, initial_sha = tpf.load_policy(args.initial_checkpoint, device)
    model.train()
    optimizer_state, checkpoint_turn_steps = read_optimizer_state(args.initial_checkpoint)

    anchor = anchor_sha = None
    anchor_has_plan = False
    if args.anchor_checkpoint:
        anchor, anchor_sha, anchor_has_plan = tpf.load_anchor(args.anchor_checkpoint, device)

    turn_steps = (
        int(args.anchor_turn_steps)
        if args.anchor_turn_steps >= 0
        else int(checkpoint_turn_steps or 0)
    )
    anchor_coef = tpf.anchor_coefficient(args, turn_steps) if anchor is not None else 0.0

    collected = collect_minibatch(args, model, device, rng)
    collect_seconds = time.perf_counter() - started
    batch = collected["batch"]

    parts = decompose(model, anchor, anchor_has_plan, batch, args, anchor_coef)
    by_row_class = (
        decompose_by_row_class(model, anchor, anchor_has_plan, batch, args, anchor_coef)
        if args.row_class_split
        else None
    )

    rows = min(int(args.counterfactual_observations), int(batch["obs"].shape[0]))
    counterfactual = {}
    for variant in [v.strip() for v in args.counterfactual_variants.split(",") if v.strip()]:
        counterfactual[variant] = counterfactual_value_step(
            model, batch, args, variant, optimizer_state, rows
        )

    report = {
        "event": "grad-decompose",
        "label": args.label or (Path(args.initial_checkpoint).stem if args.initial_checkpoint else "fresh"),
        "checkpoint": args.initial_checkpoint,
        "checkpoint_sha256": initial_sha,
        "anchor_checkpoint": args.anchor_checkpoint,
        "anchor_checkpoint_sha256": anchor_sha,
        "anchor_has_plan_head": anchor_has_plan,
        "anchor_coefficient": anchor_coef,
        "anchor_turn_steps": turn_steps,
        "optimizer_state_available": optimizer_state is not None,
        "config_source": getattr(args, "config_source", "command line"),
        "config_taken_from_checkpoint": getattr(args, "config_taken_from_checkpoint", []),
        "instrument": {
            "grad_decompose_sha256": sha256(Path(__file__).resolve()),
            "train_ppo_full_sha256": sha256(Path(tpf.__file__).resolve()),
            "torch_version": torch.__version__,
            "plan_target_memory": tpf.PLAN_TARGET_MEMORY,
            "plan_vocab_version": tpf.PLAN_VOCAB_VERSION,
        },
        "config": {
            key: value
            for key, value in sorted(vars(args).items())
            if key
            not in ("checkpoint_every", "gate_every", "gate_games", "gate_maps", "gate_bot")
            and key not in ("config_source", "config_taken_from_checkpoint")
        },
        "minibatch": collected["summary"],
        "diagnostics": parts["diagnostics"],
        "objectives": parts["objectives"],
        "combined": parts["combined"],
        "linearity_check": parts["linearity_check"],
        "by_row_class": by_row_class,
        "counterfactual": counterfactual,
        "timing": {
            "collect_seconds": collect_seconds,
            "total_seconds": time.perf_counter() - started,
        },
    }

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    return report


def main(argv: list[str] | None = None) -> dict:
    args = parse_args(argv)
    report = measure(args)
    print(json.dumps(report, sort_keys=True, default=str), flush=True)
    return report


if __name__ == "__main__":
    main()
