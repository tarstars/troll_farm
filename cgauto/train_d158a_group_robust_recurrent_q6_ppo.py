#!/usr/bin/env python3
"""Train one frozen D158a recurrent-q6 objective variant."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto import train_d108a_recurrent_q6_ppo as d108  # noqa: E402
from cgauto import train_d109a_long_recurrent_q6_ppo as d109  # noqa: E402
from cgauto.rl_macro_env import OPPONENTS  # noqa: E402
from cgauto.rl_q6_proposal_env import (  # noqa: E402
    DEFAULT_EXPERTS,
    DEFAULT_LIBRARY,
    Q6_ACTIONS,
    Q6_ACTION_FEATURES,
    Q6_STATE_FEATURES,
    Q6ProposalVecEnv,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d158a-group-robust-recurrent-q6-ppo-protocol-2026-07-23.md"
LOCK = BASE / "d158a-group-robust-recurrent-q6-ppo-lock.json"

VARIANT_ORDER = (
    "pooled_margin",
    "capped_margin",
    "own_protected",
    "group_dro_own",
)
OBJECTIVES = {
    "pooled_margin": {
        "positive_cap": None,
        "own_loss_penalty": 0.0,
        "group_dro": False,
    },
    "capped_margin": {
        "positive_cap": 40.0,
        "own_loss_penalty": 0.0,
        "group_dro": False,
    },
    "own_protected": {
        "positive_cap": 40.0,
        "own_loss_penalty": 0.5,
        "group_dro": False,
    },
    "group_dro_own": {
        "positive_cap": 40.0,
        "own_loss_penalty": 0.5,
        "group_dro": True,
    },
}
FROZEN = {
    "model_seed": 15_801,
    "train_seed_base": 9_845_000,
    "train_map_pool": 128,
    "evaluation_seed_base": 9_845_200,
    "evaluation_maps": 32,
    "confirmation_seed_base": 9_845_300,
    "confirmation_maps": 64,
    "num_envs": 60,
    "rollout_steps": 20,
    "total_transitions": 64_800,
    "update_epochs": 3,
    "minibatch_sequences": 10,
    "learning_rate": 3.0e-4,
    "adam_epsilon": 1.0e-5,
    "gamma": 1.0,
    "gae_lambda": 0.95,
    "clip_coef": 0.20,
    "entropy_coef": 0.02,
    "value_coef": 0.5,
    "max_grad_norm": 0.5,
    "target_kl": 0.03,
    "threads": 5,
    "probe_rows": 256,
    "group_ema_alpha": 0.20,
    "group_temperature": 20.0,
    "group_exponent_clip": 1.5,
    "group_weight_min": 0.5,
    "group_weight_max": 2.0,
}
OPPONENT_INDEX = {name: index for index, name in enumerate(OPPONENTS)}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def output_paths(variant: str) -> dict[str, Path]:
    if variant not in OBJECTIVES:
        raise ValueError(f"unknown D158a variant: {variant}")
    stem = f"d158a-group-robust-recurrent-q6-ppo-{variant}"
    return {
        "result": BASE / f"{stem}-result.json",
        "checkpoint": BASE / f"{stem}-final.pt",
        "evaluation_a": BASE / f"{stem}-evaluation-a.tsv",
        "evaluation_b": BASE / f"{stem}-evaluation-b.tsv",
    }


def validate_lock() -> dict:
    lock = json.loads(LOCK.read_text())
    for relative, expected in lock["sha256"].items():
        path = ROOT / relative
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"D158a lock mismatch: {relative}: {actual}")
    return lock


def family_weights(ema: np.ndarray, initialized: np.ndarray) -> np.ndarray:
    if ema.shape != (len(OPPONENTS),) or initialized.shape != ema.shape:
        raise ValueError("D158a family state shape mismatch")
    if not initialized.all():
        return np.ones_like(ema, dtype=np.float64)
    centered = ema - float(ema.mean())
    exponent = np.clip(
        -centered / FROZEN["group_temperature"],
        -FROZEN["group_exponent_clip"],
        FROZEN["group_exponent_clip"],
    )
    weights = np.exp(exponent)
    weights = np.clip(
        weights,
        FROZEN["group_weight_min"],
        FROZEN["group_weight_max"],
    )
    weights /= float(weights.mean())
    if not np.isfinite(weights).all() or abs(float(weights.mean()) - 1.0) > 1.0e-12:
        raise RuntimeError("D158a invalid family weights")
    return weights


def update_family_ema(
    ema: np.ndarray, initialized: np.ndarray, episodes: list[dict]
) -> None:
    alpha = FROZEN["group_ema_alpha"]
    for opponent, index in OPPONENT_INDEX.items():
        values = [row["margin_delta"] for row in episodes if row["opponent"] == opponent]
        if not values:
            continue
        mean = float(np.mean(values))
        if initialized[index]:
            ema[index] = (1.0 - alpha) * ema[index] + alpha * mean
        else:
            ema[index] = mean
            initialized[index] = True


def objective_return(terminal: dict, variant: str, weights: np.ndarray) -> float:
    spec = OBJECTIVES[variant]
    margin = float(terminal["margin_delta"])
    if spec["positive_cap"] is not None:
        margin = min(margin, float(spec["positive_cap"]))
    own_delta = float(terminal["own_score"] - terminal["baseline_own_score"])
    shaped = margin + float(spec["own_loss_penalty"]) * min(own_delta, 0.0)
    weight = 1.0
    if spec["group_dro"]:
        weight = float(weights[OPPONENT_INDEX[terminal["opponent"]]])
    result = weight * shaped / 100.0
    if not math.isfinite(result):
        raise RuntimeError("D158a non-finite objective return")
    return result


def objective_summary(rows: list[dict]) -> dict:
    if not rows:
        return {"episodes": 0}
    by_family = {
        opponent: {
            "episodes": sum(row["opponent"] == opponent for row in rows),
            "mean_margin_delta": float(
                np.mean([row["margin_delta"] for row in rows if row["opponent"] == opponent])
            ),
            "mean_objective_return": float(
                np.mean([row["objective_return"] for row in rows if row["opponent"] == opponent])
            ),
        }
        for opponent in OPPONENTS
    }
    return {
        **d108.episode_summary(rows),
        "mean_own_score_delta": float(
            np.mean([row["own_score"] - row["baseline_own_score"] for row in rows])
        ),
        "mean_opponent_score_delta": float(
            np.mean(
                [row["opponent_score"] - row["baseline_opponent_score"] for row in rows]
            )
        ),
        "mean_objective_return": float(np.mean([row["objective_return"] for row in rows])),
        "maximum_objective_identity_error": max(
            row["objective_identity_error"] for row in rows
        ),
        "family": by_family,
    }


def train_variant(
    variant: str,
) -> tuple[d108.RecurrentProposalActorCritic, dict[str, torch.Tensor], dict, dict]:
    if variant not in OBJECTIVES:
        raise ValueError(f"unknown D158a variant: {variant}")
    batch_size = FROZEN["num_envs"] * FROZEN["rollout_steps"]
    updates = FROZEN["total_transitions"] // batch_size
    if batch_size != 1_200 or updates != 54 or FROZEN["total_transitions"] % batch_size:
        raise RuntimeError("D158a frozen transition geometry mismatch")

    torch.manual_seed(FROZEN["model_seed"])
    np.random.seed(FROZEN["model_seed"])
    model = d108.RecurrentProposalActorCritic()
    initial_state = {name: value.detach().clone() for name, value in model.state_dict().items()}
    initial_actor = torch.cat(
        [parameter.detach().flatten() for parameter in model.actor_parameters()]
    )
    optimizer = torch.optim.Adam(
        model.parameters(), lr=FROZEN["learning_rate"], eps=FROZEN["adam_epsilon"]
    )
    rng = np.random.default_rng(FROZEN["model_seed"])

    shape = (FROZEN["rollout_steps"], FROZEN["num_envs"])
    state_buffer = np.empty((*shape, Q6_STATE_FEATURES), dtype=np.float32)
    proposal_buffer = np.empty((*shape, Q6_ACTIONS, Q6_ACTION_FEATURES), dtype=np.float32)
    mask_buffer = np.empty((*shape, Q6_ACTIONS), dtype=np.uint8)
    action_buffer = np.empty(shape, dtype=np.int64)
    logprob_buffer = np.empty(shape, dtype=np.float32)
    reward_buffer = np.empty(shape, dtype=np.float32)
    done_buffer = np.empty(shape, dtype=np.float32)
    value_buffer = np.empty(shape, dtype=np.float32)

    hidden = torch.zeros((FROZEN["num_envs"], d108.HIDDEN), dtype=torch.float32)
    global_step = illegal_actions = control_actions = noncontrol_actions = 0
    used_representatives: set[int] = set()
    all_episodes: list[dict] = []
    losses: dict[str, list[float]] = collections.defaultdict(list)
    logs = []
    probe_state: list[np.ndarray] = []
    probe_actions: list[np.ndarray] = []
    probe_masks: list[np.ndarray] = []
    probe_hidden: list[np.ndarray] = []
    probe_seen: set[bytes] = set()
    initial_probe_choices: np.ndarray | None = None
    terminal_digest = hashlib.sha256()
    raw_slot_returns = np.zeros(FROZEN["num_envs"], dtype=np.float64)
    objective_slot_returns = np.zeros(FROZEN["num_envs"], dtype=np.float64)
    family_ema = np.zeros(len(OPPONENTS), dtype=np.float64)
    family_initialized = np.zeros(len(OPPONENTS), dtype=np.bool_)
    started_wall = time.perf_counter()
    started_cpu = time.process_time()

    with Q6ProposalVecEnv(
        FROZEN["num_envs"], FROZEN["train_seed_base"], map_pool=FROZEN["train_map_pool"]
    ) as env:
        for update in range(1, updates + 1):
            update_started = time.perf_counter()
            rollout_initial_hidden = hidden.detach().numpy().copy()
            update_episodes: list[dict] = []
            update_noncontrol = 0
            rollout_weights = (
                family_weights(family_ema, family_initialized)
                if OBJECTIVES[variant]["group_dro"]
                else np.ones(len(OPPONENTS), dtype=np.float64)
            )
            for step in range(FROZEN["rollout_steps"]):
                state = env.state_features.copy()
                proposals = env.action_features.copy()
                masks = env.masks.copy()
                state_buffer[step] = state
                proposal_buffer[step] = proposals
                mask_buffer[step] = masks
                if update == 1 and len(probe_state) < FROZEN["probe_rows"]:
                    incoming = hidden.numpy()
                    for slot in np.flatnonzero(masks.sum(axis=1) > 1):
                        key = state[slot].tobytes() + masks[slot].tobytes()
                        if key in probe_seen:
                            continue
                        probe_seen.add(key)
                        probe_state.append(state[slot].copy())
                        probe_actions.append(proposals[slot].copy())
                        probe_masks.append(masks[slot].copy())
                        probe_hidden.append(incoming[slot].copy())
                        if len(probe_state) == FROZEN["probe_rows"]:
                            break
                with torch.inference_mode():
                    action, logprob, _, value, next_hidden, _ = model.action_and_value(
                        torch.from_numpy(state),
                        torch.from_numpy(proposals),
                        torch.from_numpy(masks),
                        hidden,
                    )
                selected = action.numpy().astype(np.int64)
                rows = np.arange(FROZEN["num_envs"])
                illegal_actions += int(np.count_nonzero(masks[rows, selected] != 1))
                if illegal_actions:
                    raise RuntimeError("D158a sampled masked proposal")
                control_actions += int(np.count_nonzero(selected == 0))
                chosen = selected[selected > 0]
                noncontrol_actions += len(chosen)
                update_noncontrol += len(chosen)
                used_representatives.update(chosen.tolist())
                action_buffer[step] = selected
                logprob_buffer[step] = logprob.numpy()
                value_buffer[step] = value.numpy()

                _, _, _, raw_rewards, info = env.step(selected.astype(np.int32))
                rewards = raw_rewards.astype(np.float64)
                raw_slot_returns += raw_rewards.astype(np.float64)
                done = np.asarray(
                    [terminal is not None for terminal in info.terminals], dtype=np.float32
                )
                for slot, terminal in enumerate(info.terminals):
                    if terminal is None:
                        if raw_rewards[slot] != 0.0:
                            raise RuntimeError("D158a nonterminal raw reward is nonzero")
                        continue
                    raw_identity = abs(100.0 * raw_slot_returns[slot] - terminal["margin_delta"])
                    if raw_identity >= 1.0e-4:
                        raise RuntimeError(f"D158a paired reward identity failure: {raw_identity}")
                    shaped = objective_return(terminal, variant, rollout_weights)
                    rewards[slot] = shaped
                    objective_slot_returns[slot] += shaped
                    objective_identity = abs(objective_slot_returns[slot] - shaped)
                    if objective_identity >= 1.0e-7:
                        raise RuntimeError("D158a objective return identity failure")
                    episode = {
                        **terminal,
                        "reward_identity_error": float(raw_identity),
                        "objective_return": float(shaped),
                        "objective_identity_error": float(objective_identity),
                        "family_weight": float(
                            rollout_weights[OPPONENT_INDEX[terminal["opponent"]]]
                        ),
                    }
                    d108.update_terminal_digest(terminal_digest, episode)
                    terminal_digest.update(
                        f"{episode['objective_return']:.12g}\n".encode("ascii")
                    )
                    update_episodes.append(episode)
                    all_episodes.append(episode)
                    raw_slot_returns[slot] = 0.0
                    objective_slot_returns[slot] = 0.0
                reward_buffer[step] = rewards.astype(np.float32)
                done_buffer[step] = done
                global_step += FROZEN["num_envs"]
                hidden = next_hidden * torch.from_numpy(1.0 - done).unsqueeze(-1)

            if update == 1:
                if len(probe_state) != FROZEN["probe_rows"]:
                    raise RuntimeError("D158a first rollout lacks 256 distinct live probes")
                with torch.inference_mode():
                    initial_probe_choices = model.action_and_value(
                        torch.from_numpy(np.stack(probe_state)),
                        torch.from_numpy(np.stack(probe_actions)),
                        torch.from_numpy(np.stack(probe_masks)),
                        torch.from_numpy(np.stack(probe_hidden)),
                        deterministic=True,
                    )[0].numpy()

            if OBJECTIVES[variant]["group_dro"]:
                update_family_ema(family_ema, family_initialized, update_episodes)
            with torch.inference_mode():
                next_value = model.value(torch.from_numpy(env.state_features)).numpy()
            advantages = d109.compute_advantages(
                reward_buffer,
                done_buffer,
                value_buffer,
                next_value,
                gamma=FROZEN["gamma"],
                gae_lambda=FROZEN["gae_lambda"],
            )
            returns = advantages + value_buffer
            normalized = (advantages - advantages.mean()) / (advantages.std() + 1.0e-8)
            sequence_indices = np.arange(FROZEN["num_envs"])
            update_metrics: dict[str, list[float]] = collections.defaultdict(list)
            epochs_run = 0
            for epoch in range(FROZEN["update_epochs"]):
                rng.shuffle(sequence_indices)
                epoch_kls = []
                for start in range(0, FROZEN["num_envs"], FROZEN["minibatch_sequences"]):
                    indexes = sequence_indices[start : start + FROZEN["minibatch_sequences"]]
                    new_logprob, entropy, new_value = model.sequence_statistics(
                        torch.from_numpy(state_buffer[:, indexes]),
                        torch.from_numpy(proposal_buffer[:, indexes]),
                        torch.from_numpy(mask_buffer[:, indexes]),
                        torch.from_numpy(action_buffer[:, indexes]),
                        torch.from_numpy(done_buffer[:, indexes]),
                        torch.from_numpy(rollout_initial_hidden[indexes]),
                    )
                    old_logprob = torch.from_numpy(logprob_buffer[:, indexes])
                    log_ratio = new_logprob - old_logprob
                    ratio = log_ratio.exp()
                    advantage = torch.from_numpy(normalized[:, indexes])
                    policy_loss = torch.maximum(
                        -advantage * ratio,
                        -advantage
                        * ratio.clamp(1.0 - FROZEN["clip_coef"], 1.0 + FROZEN["clip_coef"]),
                    ).mean()
                    entropy_mean = entropy.mean()
                    value_loss = 0.5 * F.mse_loss(
                        new_value, torch.from_numpy(returns[:, indexes])
                    )
                    loss = (
                        policy_loss
                        + FROZEN["value_coef"] * value_loss
                        - FROZEN["entropy_coef"] * entropy_mean
                    )
                    if not torch.isfinite(loss):
                        raise RuntimeError("non-finite D158a PPO loss")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    gradient_norm = nn.utils.clip_grad_norm_(
                        model.parameters(), FROZEN["max_grad_norm"]
                    )
                    if not torch.isfinite(gradient_norm):
                        raise RuntimeError("non-finite D158a gradient")
                    optimizer.step()
                    with torch.no_grad():
                        approx_kl = ((ratio - 1.0) - log_ratio).mean()
                        clip_fraction = (
                            (ratio - 1.0).abs() > FROZEN["clip_coef"]
                        ).float().mean()
                    metrics = {
                        "policy_loss": float(policy_loss.detach()),
                        "value_loss": float(value_loss.detach()),
                        "entropy": float(entropy_mean.detach()),
                        "approx_kl": float(approx_kl),
                        "clip_fraction": float(clip_fraction),
                        "gradient_norm": float(gradient_norm),
                    }
                    for name, metric in metrics.items():
                        update_metrics[name].append(metric)
                        losses[name].append(metric)
                    epoch_kls.append(float(approx_kl))
                epochs_run = epoch + 1
                if epoch_kls and float(np.mean(epoch_kls)) > FROZEN["target_kl"]:
                    break
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError("non-finite D158a parameter")
            log = {
                "update": update,
                "global_step": global_step,
                "episodes": objective_summary(update_episodes),
                "noncontrol_actions": update_noncontrol,
                "epochs_run": epochs_run,
                "family_ema": {
                    opponent: float(family_ema[index])
                    for index, opponent in enumerate(OPPONENTS)
                },
                "next_family_weights": {
                    opponent: float(weight)
                    for opponent, weight in zip(
                        OPPONENTS, family_weights(family_ema, family_initialized)
                    )
                },
                **{name: float(np.mean(values)) for name, values in update_metrics.items()},
                "update_seconds": time.perf_counter() - update_started,
            }
            logs.append(log)
            if update == 1 or update % 6 == 0 or update == updates:
                print(
                    json.dumps({"event": "update", "variant": variant, **log}, sort_keys=True),
                    flush=True,
                )

    wall_seconds = time.perf_counter() - started_wall
    cpu_seconds = time.process_time() - started_cpu
    if initial_probe_choices is None:
        raise RuntimeError("D158a initial probe missing")
    with torch.inference_mode():
        final_probe_choices = model.action_and_value(
            torch.from_numpy(np.stack(probe_state)),
            torch.from_numpy(np.stack(probe_actions)),
            torch.from_numpy(np.stack(probe_masks)),
            torch.from_numpy(np.stack(probe_hidden)),
            deterministic=True,
        )[0].numpy()
    final_actor = torch.cat(
        [parameter.detach().flatten() for parameter in model.actor_parameters()]
    )
    probe = {
        "rows": len(probe_state),
        "initial_control": int(np.count_nonzero(initial_probe_choices == 0)),
        "final_control": int(np.count_nonzero(final_probe_choices == 0)),
        "initial_distinct_actions": len(set(initial_probe_choices.tolist())),
        "final_distinct_actions": len(set(final_probe_choices.tolist())),
        "changed_actions": int(np.count_nonzero(initial_probe_choices != final_probe_choices)),
        "actor_l2_drift": float(torch.linalg.vector_norm(final_actor - initial_actor)),
    }
    training = {
        "global_step": global_step,
        "updates": len(logs),
        "illegal_actions": illegal_actions,
        "control_actions": control_actions,
        "noncontrol_actions": noncontrol_actions,
        "noncontrol_rate": noncontrol_actions / global_step,
        "used_representatives": sorted(used_representatives),
        "episodes": objective_summary(all_episodes),
        "terminal_stream_sha256": terminal_digest.hexdigest(),
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "effective_cpu_cores": cpu_seconds / wall_seconds,
        "transitions_per_second": global_step / wall_seconds,
        "final_family_ema": {
            opponent: float(family_ema[index]) for index, opponent in enumerate(OPPONENTS)
        },
        "final_family_weights": {
            opponent: float(weight)
            for opponent, weight in zip(OPPONENTS, family_weights(family_ema, family_initialized))
        },
        "losses": {
            name: {
                "mean": float(np.mean(values)),
                "maximum": float(np.max(values)),
                "finite": bool(np.isfinite(values).all()),
            }
            for name, values in losses.items()
        },
        "logs": logs,
    }
    return model, initial_state, training, probe


def development_gates(training: dict, probe: dict, summaries: dict, repeat_exact: bool) -> dict:
    final = summaries["final"]
    control = summaries["control"]
    initial = summaries["initial"]
    return {
        "mechanics": {
            "exact_training_budget": training["global_step"] == FROZEN["total_transitions"],
            "finite_losses": all(value["finite"] for value in training["losses"].values()),
            "zero_illegal_actions": training["illegal_actions"] == 0,
            "at_least_10000_training_episodes": training["episodes"]["episodes"] >= 10_000,
            "raw_reward_identity": training["episodes"]["maximum_reward_identity_error"] < 1e-4,
            "objective_identity": training["episodes"]["maximum_objective_identity_error"] < 1e-7,
            "zero_training_failures": all(
                value == 0 for value in training["episodes"]["mechanical_failures"].values()
            ),
            "evaluation_complete": all(summary["tasks"] == 512 for summary in summaries.values()),
            "evaluation_repeat_exact": repeat_exact,
            "evaluation_reward_identity": max(
                summary["maximum_reward_identity_error"] for summary in summaries.values()
            ) < 1e-4,
            "evaluation_zero_failures": all(
                value == 0 for value in final["mechanical_failures"].values()
            ),
        },
        "signal": {
            "probe_40_actions_change": probe["changed_actions"] >= 40,
            "probe_8_final_actions": probe["final_distinct_actions"] >= 8,
            "actor_l2_drift_010": probe["actor_l2_drift"] >= 0.10,
            "final_uses_8_representatives": final["distinct_representatives"] >= 8,
            "final_intervention_10_to_95pct": 0.10 <= final["intervention_rate"] <= 0.95,
        },
        "safety": {
            "final_crop_100pct": final["crop_rate"] == 1.0,
            "final_worker_three_within_5pp": final["worker_three_rate"]
            >= control["worker_three_rate"] - 0.05,
        },
        "value": {
            "final_mean_gain_at_least_1": final["mean_margin_delta"] >= 1.0,
            "final_strict_improvement_35pct": final["strict_improvement_rate"] >= 0.35,
            "final_six_positive_families": final["positive_families"] >= 6,
            "final_worst_family_at_least_minus3": final["worst_family"] >= -3.0,
            "final_own_score_at_least_minus1": final["mean_own_score_delta"] >= -1.0,
            "final_beats_initial_by_5": final["mean_margin_delta"]
            - initial["mean_margin_delta"]
            >= 5.0,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", required=True, choices=VARIANT_ORDER)
    args = parser.parse_args(argv)
    paths = output_paths(args.variant)
    for path in paths.values():
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
    lock = validate_lock()
    os.environ["RAYON_NUM_THREADS"] = str(FROZEN["threads"])
    torch.set_num_threads(FROZEN["threads"])
    torch.set_num_interop_threads(1)
    d108.FROZEN = FROZEN
    model, initial_state, training, probe = train_variant(args.variant)
    torch.save(
        {
            "model": model.state_dict(),
            "config": FROZEN,
            "variant": args.variant,
            "objective": OBJECTIVES[args.variant],
            "state_features": Q6_STATE_FEATURES,
            "actions": Q6_ACTIONS,
            "action_features": Q6_ACTION_FEATURES,
            "hidden": d108.HIDDEN,
            "action_embed": d108.ACTION_EMBED,
        },
        paths["checkpoint"],
    )
    initial_model = d108.RecurrentProposalActorCritic()
    initial_model.load_state_dict(initial_state)
    rows_a = [
        *d108.evaluate_policy("control", None),
        *d108.evaluate_policy("initial", initial_model),
        *d108.evaluate_policy("final", model),
    ]
    rows_b = [
        *d108.evaluate_policy("control", None),
        *d108.evaluate_policy("initial", initial_model),
        *d108.evaluate_policy("final", model),
    ]
    d108.write_evaluation(paths["evaluation_a"], rows_a)
    d108.write_evaluation(paths["evaluation_b"], rows_b)
    repeat_exact = paths["evaluation_a"].read_bytes() == paths["evaluation_b"].read_bytes()
    summaries = {
        policy: d108.evaluation_summary(rows_a, policy)
        for policy in ("control", "initial", "final")
    }
    gates = development_gates(training, probe, summaries, repeat_exact)
    passes = {name: all(values.values()) for name, values in gates.items()}
    eligible = all(passes.values())
    result = {
        "schema": "troll-farm-d158a-group-robust-recurrent-q6-ppo-variant-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "variant": args.variant,
        "objective": OBJECTIVES[args.variant],
        "config": FROZEN,
        "inputs": {
            "lock": sha256(LOCK),
            "protocol": sha256(PROTOCOL),
            "trainer": sha256(Path(__file__)),
            "checkpoint": sha256(paths["checkpoint"]),
            "evaluation_a": sha256(paths["evaluation_a"]),
            "evaluation_b": sha256(paths["evaluation_b"]),
            "locked_inputs": lock["sha256"],
        },
        "model": {
            "actor_parameters": d108.parameter_count(model.actor_parameters()),
            "critic_parameters": d108.parameter_count(model.critic.parameters()),
            "total_parameters": d108.parameter_count(model.parameters()),
        },
        "training": training,
        "probe": probe,
        "evaluation": {"repeat_exact": repeat_exact, "summaries": summaries},
        "gates": {**gates, "passes": passes},
        "eligible": eligible,
        "decision": "development_admissible" if eligible else "development_fail",
    }
    paths["result"].write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"variant": args.variant, "eligible": eligible, "passes": passes}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

