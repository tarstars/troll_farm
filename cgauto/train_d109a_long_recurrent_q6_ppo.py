#!/usr/bin/env python3
"""Run D109a's duration-only recurrent q6 PPO follow-up."""

from __future__ import annotations

import collections
import json
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
from cgauto.rl_macro_env import OPPONENTS  # noqa: E402
from cgauto.rl_q6_proposal_env import (  # noqa: E402
    DEFAULT_EXPERTS,
    DEFAULT_LIBRARY,
    Q6_ACTIONS,
    Q6_ACTION_FEATURES,
    Q6_STATE_FEATURES,
    Q6ProposalVecEnv,
)
from cgauto.train_d41c_residual_ppo import compute_advantages  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d109a-duration-only-recurrent-q6-ppo-protocol-2026-07-22.md"
D108_RESULT = BASE / "d108a-recurrent-masked-q6-ppo-result.json"
OUTPUT = BASE / "d109a-duration-only-recurrent-q6-ppo-result.json"
CHECKPOINT = BASE / "d109a-duration-only-recurrent-q6-ppo-final.pt"
EVALUATION_A = BASE / "d109a-duration-only-recurrent-q6-ppo-evaluation-a.tsv"
EVALUATION_B = BASE / "d109a-duration-only-recurrent-q6-ppo-evaluation-b.tsv"

FROZEN = {
    "model_seed": 10_801,
    "train_seed_base": 9_835_000,
    "train_map_pool": 128,
    "evaluation_seed_base": 9_837_000,
    "evaluation_maps": 32,
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
    "threads": 20,
    "probe_rows": 256,
}
EXPECTED_HASHES: dict[Path, str] = {
    PROTOCOL: "716e0b68ee824c3fdde5a764de1d6e388281adba1977938598f75ce66e447f68",
    D108_RESULT: "d36abd2f1610163ae2a775978cb69a59ac48658e65b174e65c3ddeccad37083c",
    ROOT / "cgauto/train_d108a_recurrent_q6_ppo.py":
        "ed4ff4d23c88a7df0152334f739d169e6254a53d4111aa5f3c7c06f274669086",
    ROOT / "cgauto/rl_q6_proposal_env.py":
        "8f102e1eca5a1bcc49ea932170b100eacea5848d7af097c0b21689229dc68911",
    ROOT / "rust/src/rl_q6_proposal.rs":
        "739fa02c00d92ba271f7a7a15fca893f18fffa258c02ba39c4a4cb08eaba2af1",
    Path(DEFAULT_EXPERTS):
        "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8",
    Path(DEFAULT_LIBRARY):
        "90284b35574e78740bdd1b1f81ea6ba5fdf03265a5ef029f1667a676748835cf",
}


def train_long() -> tuple[d108.RecurrentProposalActorCritic, dict[str, torch.Tensor], dict, dict]:
    batch_size = FROZEN["num_envs"] * FROZEN["rollout_steps"]
    updates = FROZEN["total_transitions"] // batch_size
    if batch_size != 1_200 or updates != 54 or FROZEN["total_transitions"] % batch_size:
        raise RuntimeError("D109a frozen transition geometry mismatch")
    torch.manual_seed(FROZEN["model_seed"])
    np.random.seed(FROZEN["model_seed"])
    model = d108.RecurrentProposalActorCritic()
    initial_state = {name: value.detach().clone() for name, value in model.state_dict().items()}
    initial_actor = torch.cat([parameter.detach().flatten() for parameter in model.actor_parameters()])
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
    terminal_digest = __import__("hashlib").sha256()
    started_wall = time.perf_counter()
    started_cpu = time.process_time()

    with Q6ProposalVecEnv(
        FROZEN["num_envs"],
        FROZEN["train_seed_base"],
        map_pool=FROZEN["train_map_pool"],
    ) as env:
        slot_returns = np.zeros(FROZEN["num_envs"], dtype=np.float64)
        for update in range(1, updates + 1):
            update_started = time.perf_counter()
            rollout_initial_hidden = hidden.detach().numpy().copy()
            update_episodes = []
            update_noncontrol = 0
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
                    raise RuntimeError("D109a sampled masked proposal")
                control_actions += int(np.count_nonzero(selected == 0))
                chosen = selected[selected > 0]
                noncontrol_actions += len(chosen)
                update_noncontrol += len(chosen)
                used_representatives.update(chosen.tolist())
                action_buffer[step] = selected
                logprob_buffer[step] = logprob.numpy()
                value_buffer[step] = value.numpy()
                _, _, _, rewards, info = env.step(selected.astype(np.int32))
                reward_buffer[step] = rewards
                done = np.asarray(
                    [terminal is not None for terminal in info.terminals], dtype=np.float32
                )
                done_buffer[step] = done
                slot_returns += rewards.astype(np.float64)
                global_step += FROZEN["num_envs"]
                for slot, terminal in enumerate(info.terminals):
                    if terminal is None:
                        continue
                    identity_error = abs(100.0 * slot_returns[slot] - terminal["margin_delta"])
                    if identity_error >= 1.0e-4:
                        raise RuntimeError(f"D109a paired reward identity failure: {identity_error}")
                    episode = {**terminal, "reward_identity_error": float(identity_error)}
                    d108.update_terminal_digest(terminal_digest, episode)
                    update_episodes.append(episode)
                    all_episodes.append(episode)
                    slot_returns[slot] = 0.0
                hidden = next_hidden * torch.from_numpy(1.0 - done).unsqueeze(-1)

            if update == 1:
                if len(probe_state) != FROZEN["probe_rows"]:
                    raise RuntimeError("D109a first rollout lacks 256 distinct live probes")
                with torch.inference_mode():
                    initial_probe_choices = model.action_and_value(
                        torch.from_numpy(np.stack(probe_state)),
                        torch.from_numpy(np.stack(probe_actions)),
                        torch.from_numpy(np.stack(probe_masks)),
                        torch.from_numpy(np.stack(probe_hidden)),
                        deterministic=True,
                    )[0].numpy()
            with torch.inference_mode():
                next_value = model.value(torch.from_numpy(env.state_features)).numpy()
            advantages = compute_advantages(
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
                        raise RuntimeError("non-finite D109a PPO loss")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    gradient_norm = nn.utils.clip_grad_norm_(
                        model.parameters(), FROZEN["max_grad_norm"]
                    )
                    if not torch.isfinite(gradient_norm):
                        raise RuntimeError("non-finite D109a gradient")
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
                    for name, value in metrics.items():
                        update_metrics[name].append(value)
                        losses[name].append(value)
                    epoch_kls.append(float(approx_kl))
                epochs_run = epoch + 1
                if epoch_kls and float(np.mean(epoch_kls)) > FROZEN["target_kl"]:
                    break
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                raise RuntimeError("non-finite D109a parameter")
            log = {
                "update": update,
                "global_step": global_step,
                "episodes": d108.episode_summary(update_episodes),
                "noncontrol_actions": update_noncontrol,
                "epochs_run": epochs_run,
                **{name: float(np.mean(values)) for name, values in update_metrics.items()},
                "update_seconds": time.perf_counter() - update_started,
            }
            logs.append(log)
            if update == 1 or update % 6 == 0 or update == updates:
                print(json.dumps({"event": "update", **log}, sort_keys=True), flush=True)

    wall_seconds = time.perf_counter() - started_wall
    cpu_seconds = time.process_time() - started_cpu
    if initial_probe_choices is None:
        raise RuntimeError("D109a initial probe missing")
    with torch.inference_mode():
        final_probe_choices = model.action_and_value(
            torch.from_numpy(np.stack(probe_state)),
            torch.from_numpy(np.stack(probe_actions)),
            torch.from_numpy(np.stack(probe_masks)),
            torch.from_numpy(np.stack(probe_hidden)),
            deterministic=True,
        )[0].numpy()
    final_actor = torch.cat([parameter.detach().flatten() for parameter in model.actor_parameters()])
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
        "episodes": d108.episode_summary(all_episodes),
        "terminal_stream_sha256": terminal_digest.hexdigest(),
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "effective_cpu_cores": cpu_seconds / wall_seconds,
        "transitions_per_second": global_step / wall_seconds,
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


def main() -> int:
    for output in (OUTPUT, CHECKPOINT, EVALUATION_A, EVALUATION_B):
        if output.exists():
            raise SystemExit(f"refusing to overwrite {output}")
    for path, expected in EXPECTED_HASHES.items():
        actual = d108.sha256(path)
        if actual != expected:
            raise SystemExit(f"D109a prerequisite hash mismatch: {path}: {actual}")
    d108.FROZEN = FROZEN
    os.environ["RAYON_NUM_THREADS"] = str(FROZEN["threads"])
    torch.set_num_threads(FROZEN["threads"])
    torch.set_num_interop_threads(4)
    model, initial_state, training, probe = train_long()
    torch.save(
        {
            "model": model.state_dict(),
            "config": FROZEN,
            "state_features": Q6_STATE_FEATURES,
            "actions": Q6_ACTIONS,
            "action_features": Q6_ACTION_FEATURES,
            "hidden": d108.HIDDEN,
            "action_embed": d108.ACTION_EMBED,
        },
        CHECKPOINT,
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
    d108.write_evaluation(EVALUATION_A, rows_a)
    d108.write_evaluation(EVALUATION_B, rows_b)
    repeat_exact = EVALUATION_A.read_bytes() == EVALUATION_B.read_bytes()
    summaries = {
        policy: d108.evaluation_summary(rows_a, policy)
        for policy in ("control", "initial", "final")
    }
    final = summaries["final"]
    control = summaries["control"]
    final_initial = d108.paired_final_initial(rows_a)
    mechanics = {
        "exact_training_budget": training["global_step"] == 64_800 and training["updates"] == 54,
        "finite_losses": all(value["finite"] for value in training["losses"].values()),
        "zero_illegal_actions": training["illegal_actions"] == 0,
        "at_least_10000_training_episodes": training["episodes"]["episodes"] >= 10_000,
        "paired_reward_identity": training["episodes"]["maximum_reward_identity_error"] < 1.0e-4,
        "zero_training_mechanical_failures": all(value == 0 for value in training["episodes"]["mechanical_failures"].values()),
        "training_explores_48_representatives": len(training["used_representatives"]) >= 48,
        "training_noncontrol_rate_10_to_95pct": 0.10 <= training["noncontrol_rate"] <= 0.95,
        "evaluation_complete": all(summary["tasks"] == 512 for summary in summaries.values()),
        "evaluation_repeat_byte_exact": repeat_exact,
        "evaluation_reward_identity": max(summary["maximum_reward_identity_error"] for summary in summaries.values()) < 1.0e-4,
        "evaluation_zero_mechanical_failures": all(value == 0 for value in final["mechanical_failures"].values()),
        "throughput_at_least_30": training["transitions_per_second"] >= 30,
    }
    signal = {
        "probe_40_actions_change": probe["changed_actions"] >= 40,
        "probe_8_final_actions": probe["final_distinct_actions"] >= 8,
        "actor_l2_drift_010": probe["actor_l2_drift"] >= 0.10,
        "final_uses_8_representatives": final["distinct_representatives"] >= 8,
        "final_intervention_rate_10_to_90pct": 0.10 <= final["intervention_rate"] <= 0.90,
        "final_repeats_10pct": final["repeated_rate"] >= 0.10,
    }
    safety = {
        "final_crop_100pct": final["crop_rate"] == 1.0,
        "final_worker_three_within_5pp_control": final["worker_three_rate"] >= control["worker_three_rate"] - 0.05,
    }
    value = {
        "final_mean_gain_at_least_2": final["mean_margin_delta"] >= 2.0,
        "final_strict_improvement_40pct": final["strict_improvement_rate"] >= 0.40,
        "final_worst_family_at_least_minus3": final["worst_family"] >= -3.0,
        "final_six_positive_families": final["positive_families"] >= 6,
        "final_own_nonnegative_or_opponent_nonpositive": final["mean_own_score_delta"] >= 0 or final["mean_opponent_score_delta"] <= 0,
        "final_beats_initial_by_5": final_initial["mean_margin_delta"] >= 5.0,
    }
    passes = {
        "mechanics": all(mechanics.values()),
        "signal": all(signal.values()),
        "safety": all(safety.values()),
        "value": all(value.values()),
    }
    full_pass = all(passes.values())
    result = {
        "schema": "troll-farm-d109a-duration-only-recurrent-q6-ppo-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inputs": {
            "protocol": d108.sha256(PROTOCOL),
            "d108_result": d108.sha256(D108_RESULT),
            "wrapper": d108.sha256(ROOT / "cgauto/rl_q6_proposal_env.py"),
            "rust_env": d108.sha256(ROOT / "rust/src/rl_q6_proposal.rs"),
            "experts": d108.sha256(Path(DEFAULT_EXPERTS)),
            "library": d108.sha256(Path(DEFAULT_LIBRARY)),
            "trainer": d108.sha256(Path(__file__)),
            "checkpoint": d108.sha256(CHECKPOINT),
            "evaluation_a": d108.sha256(EVALUATION_A),
            "evaluation_b": d108.sha256(EVALUATION_B),
        },
        "config": FROZEN,
        "model": {
            "actor_parameters": d108.parameter_count(model.actor_parameters()),
            "critic_parameters": d108.parameter_count(model.critic.parameters()),
            "total_parameters": d108.parameter_count(model.parameters()),
        },
        "training": training,
        "probe": probe,
        "evaluation": {
            "repeat_exact": repeat_exact,
            "summaries": summaries,
            "final_versus_initial": final_initial,
        },
        "gates": {
            "mechanics": mechanics,
            "signal": signal,
            "safety": safety,
            "value": value,
            "passes": passes,
            "full_pass": full_pass,
        },
        "decision": (
            "open_d109b_deployable_size_and_confirmation"
            if full_pass
            else "close_duration_only_recurrent_q6"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gates": result["gates"], "evaluation": result["evaluation"], "decision": result["decision"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
