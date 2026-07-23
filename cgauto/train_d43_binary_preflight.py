#!/usr/bin/env python3
"""Run the frozen D43 binary closed-loop PPO mechanical preflight."""

from __future__ import annotations

import collections
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions.bernoulli import Bernoulli
from torch.nn import functional as F

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.rl_macro_env import (
    BRANCHES,
    CANDIDATE_FEATURES,
    DEFAULT_LIBRARY,
    MAX_CANDIDATES,
    MacroVecEnv,
)
from cgauto.train_d41c_residual_ppo import (
    ExactPriorResidualActorCritic,
    compute_advantages,
    episode_summary,
    layer_init,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d43-binary-closed-loop-preflight-protocol-2026-07-21.md"
RECOVERY_PROTOCOL = ANALYSIS / "d43-preflight-serialization-recovery-protocol-2026-07-21.md"
ELIGIBILITY_CHECKPOINT = ANALYSIS / "d41c-residual-ppo-seed411-final.pt"
OUTPUT = ANALYSIS / "d43-binary-closed-loop-preflight-result.json"
CHECKPOINT = ANALYSIS / "d43-binary-closed-loop-preflight-final.pt"
RECOVERY_REFERENCE = ANALYSIS / "d43-binary-closed-loop-preflight-first-complete.pt"

EXPECTED_PROTOCOL_SHA256 = "20c544d6c454d8966b4a5c32b54f844af04c03b41f059462566b5cd363eaec28"
EXPECTED_RECOVERY_PROTOCOL_SHA256 = "5564c628cdd59f634e8dc8804c8573c02466ea06f373bb5d29bef93b599c04af"
EXPECTED_LIBRARY_SHA256 = "5839a7b888f2772e54a293a66ed5b186df378d5b8514f43a200898c8eef70173"
EXPECTED_CHECKPOINT_SHA256 = "1de76fc5751b2c41d3795d4d15cf3a56155ccdba5dbe69872fa29f890371671a"
EXPECTED_RECOVERY_REFERENCE_SHA256 = "ae25f7a889ffe74a203bccefdc1140bd5d436091d63f0342612a5ec02550b469"

ACTOR_FEATURES = 154
CRITIC_FEATURES = 17 + 2 * CANDIDATE_FEATURES
ACTOR_WIDTH = 8
INITIAL_ALTERNATIVE_PROBABILITY = 0.25
FROZEN = {
    "model_seed": 4_310,
    "train_seed_base": 9_776_000,
    "num_envs": 64,
    "rollout_steps": 64,
    "total_transitions": 131_072,
    "update_epochs": 4,
    "minibatch_size": 1_024,
    "learning_rate": 2.5e-4,
    "adam_epsilon": 1e-5,
    "gamma": 1.0,
    "gae_lambda": 0.95,
    "clip_coef": 0.10,
    "value_coef": 0.5,
    "entropy_coef": 0.001,
    "max_grad_norm": 0.5,
    "target_kl": 0.02,
    "threads": 20,
}


class BinaryActorCritic(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.actor_hidden = layer_init(nn.Linear(ACTOR_FEATURES, ACTOR_WIDTH))
        self.actor_output = nn.Linear(ACTOR_WIDTH, 1)
        nn.init.zeros_(self.actor_output.weight)
        nn.init.constant_(
            self.actor_output.bias,
            math.log(
                INITIAL_ALTERNATIVE_PROBABILITY
                / (1.0 - INITIAL_ALTERNATIVE_PROBABILITY)
            ),
        )
        self.critic = nn.Sequential(
            layer_init(nn.Linear(CRITIC_FEATURES, 64)),
            nn.ReLU(),
            layer_init(nn.Linear(64, 32)),
            nn.ReLU(),
            layer_init(nn.Linear(32, 1), std=1.0),
        )

    def actor_parameters(self) -> list[nn.Parameter]:
        return list(self.actor_hidden.parameters()) + list(self.actor_output.parameters())

    def actor_logits(self, features: torch.Tensor) -> torch.Tensor:
        return self.actor_output(F.relu(self.actor_hidden(features.float()))).squeeze(-1)

    def action_and_value(
        self,
        actor_features: torch.Tensor,
        critic_features: torch.Tensor,
        action: torch.Tensor | None = None,
        *,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        logits = self.actor_logits(actor_features)
        distribution = Bernoulli(logits=logits)
        if action is None:
            action = (logits >= 0).float() if deterministic else distribution.sample()
        else:
            action = action.float()
        value = self.critic(critic_features.float()).squeeze(-1)
        return action.long(), distribution.log_prob(action), distribution.entropy(), value, logits


def actor_parameter_count(model: BinaryActorCritic) -> int:
    return sum(parameter.numel() for parameter in model.actor_parameters())


def critic_parameter_count(model: BinaryActorCritic) -> int:
    return sum(parameter.numel() for parameter in model.critic.parameters())


def construct_binary_state(
    features: np.ndarray,
    counts: np.ndarray,
    prior_ranks: np.ndarray,
    residual: np.ndarray,
    branches: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    features = np.asarray(features, dtype=np.float32)
    counts = np.asarray(counts, dtype=np.int64)
    prior_ranks = np.asarray(prior_ranks)
    residual = np.asarray(residual, dtype=np.float32)
    batch, width, feature_count = features.shape
    if feature_count != CANDIDATE_FEATURES:
        raise ValueError("D43 candidate feature width")
    legal = np.arange(width)[None, :] < counts[:, None]
    rank_zero = np.argmax(prior_ranks == 0, axis=1)
    rank_one = np.argmax(prior_ranks == 1, axis=1)
    has_rank_one = np.any((prior_ranks == 1) & legal, axis=1)
    rows = np.arange(batch)
    gap = residual[rows, rank_one] - residual[rows, rank_zero]
    candidate = features[:, :, 17:44]
    mean = (candidate * legal[:, :, None]).sum(axis=1) / counts[:, None].clip(min=1)
    maximum = np.where(legal[:, :, None], candidate, -np.inf).max(axis=1)
    actor = np.concatenate(
        (
            features[rows, rank_zero, :17],
            features[rows, rank_zero, 17:44],
            features[rows, rank_one, 17:44],
            features[rows, rank_one, 17:44] - features[rows, rank_zero, 17:44],
            mean,
            maximum,
            gap[:, None],
            (counts / MAX_CANDIDATES)[:, None],
        ),
        axis=1,
    ).astype(np.float32)
    full_mean = (features * legal[:, :, None]).sum(axis=1) / counts[:, None].clip(min=1)
    full_maximum = np.where(legal[:, :, None], features, -np.inf).max(axis=1)
    critic = np.concatenate(
        (features[rows, rank_zero, :17], full_mean, full_maximum), axis=1
    ).astype(np.float32)
    turn = np.rint(features[rows, rank_zero, 1] * 300).astype(np.int32)
    phase = (turn < 100) | (turn >= 200)
    eligible = (
        has_rank_one
        & (np.asarray(branches) == BRANCHES.index("rate"))
        & phase
        & (gap >= 0.200)
        & (gap <= 0.340)
    )
    if actor.shape != (batch, ACTOR_FEATURES) or critic.shape != (batch, CRITIC_FEATURES):
        raise RuntimeError("D43 constructed feature shape")
    if not np.isfinite(actor).all() or not np.isfinite(critic).all():
        raise RuntimeError("nonfinite D43 constructed feature")
    return actor, critic, eligible, rank_zero, rank_one, gap


@torch.inference_mode()
def observe(
    env: MacroVecEnv, eligibility_model: ExactPriorResidualActorCritic
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    maximum = int(env.counts.max())
    features = env.features[:, :maximum]
    residual = eligibility_model.actor_output(
        F.relu(eligibility_model.actor_hidden(torch.from_numpy(features)))
    ).squeeze(-1).numpy()
    return construct_binary_state(
        features,
        env.counts,
        env.prior_ranks[:, :maximum],
        residual,
        env.branches,
    )


def normalize_eligible_advantages(advantages: np.ndarray, eligible: np.ndarray) -> np.ndarray:
    output = np.zeros_like(advantages, dtype=np.float32)
    values = advantages[eligible]
    if len(values):
        output[eligible] = (values - values.mean()) / (values.std() + 1e-8)
    return output


def finite_list(values: list[float]) -> bool:
    return bool(values) and bool(np.isfinite(np.asarray(values)).all())


def main() -> None:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (RECOVERY_PROTOCOL, EXPECTED_RECOVERY_PROTOCOL_SHA256),
        (Path(DEFAULT_LIBRARY), EXPECTED_LIBRARY_SHA256),
        (ELIGIBILITY_CHECKPOINT, EXPECTED_CHECKPOINT_SHA256),
        (RECOVERY_REFERENCE, EXPECTED_RECOVERY_REFERENCE_SHA256),
    ):
        if not path.exists():
            raise SystemExit(f"missing D43 prerequisite: {path}")
        if sha256(path) != expected:
            raise SystemExit(f"D43 prerequisite hash mismatch: {path}")
    if OUTPUT.exists() or CHECKPOINT.exists():
        raise SystemExit("refusing to overwrite D43 preflight artifacts")

    batch_size = FROZEN["num_envs"] * FROZEN["rollout_steps"]
    updates = FROZEN["total_transitions"] // batch_size
    if batch_size != 4_096 or updates != 32 or FROZEN["total_transitions"] % batch_size:
        raise SystemExit("D43 frozen transition geometry mismatch")

    torch.manual_seed(FROZEN["model_seed"])
    np.random.seed(FROZEN["model_seed"])
    torch.set_num_threads(FROZEN["threads"])
    torch.set_num_interop_threads(4)
    eligibility_saved = torch.load(
        ELIGIBILITY_CHECKPOINT, map_location="cpu", weights_only=False
    )
    eligibility_model = ExactPriorResidualActorCritic()
    eligibility_model.load_state_dict(eligibility_saved["model"], strict=True)
    eligibility_model.eval()
    model = BinaryActorCritic()
    if actor_parameter_count(model) != 1_249 or critic_parameter_count(model) != 8_897:
        raise SystemExit("D43 model parameter count drift")
    optimizer = torch.optim.Adam(
        model.parameters(), lr=FROZEN["learning_rate"], eps=FROZEN["adam_epsilon"]
    )
    rng = np.random.default_rng(FROZEN["model_seed"])
    initial_actor = torch.cat(
        [parameter.detach().flatten().clone() for parameter in model.actor_parameters()]
    )

    shape = (FROZEN["rollout_steps"], FROZEN["num_envs"])
    actor_buffer = np.empty((*shape, ACTOR_FEATURES), dtype=np.float32)
    critic_buffer = np.empty((*shape, CRITIC_FEATURES), dtype=np.float32)
    eligible_buffer = np.empty(shape, dtype=bool)
    action_buffer = np.empty(shape, dtype=np.int8)
    logprob_buffer = np.empty(shape, dtype=np.float32)
    reward_buffer = np.empty(shape, dtype=np.float32)
    done_buffer = np.empty(shape, dtype=np.float32)
    value_buffer = np.empty(shape, dtype=np.float32)

    global_step = 0
    eligible_states = sampled_alternatives = noneligible_deviations = illegal_actions = 0
    maximum_reward_identity_error = 0.0
    all_episodes: list[dict] = []
    probe_parts: list[np.ndarray] = []
    probe_rows = 0
    logs = []
    all_policy_losses: list[float] = []
    all_value_losses: list[float] = []
    all_kls: list[float] = []
    all_clip_fractions: list[float] = []

    with MacroVecEnv(FROZEN["num_envs"], FROZEN["train_seed_base"]) as env:
        actor_features, critic_features, eligible, rank_zero, rank_one, _ = observe(
            env, eligibility_model
        )
        with torch.inference_mode():
            initial_binary, *_ = model.action_and_value(
                torch.from_numpy(actor_features),
                torch.from_numpy(critic_features),
                deterministic=True,
            )
        if np.any(initial_binary.numpy()) or not np.array_equal(
            rank_zero, env.teacher_indices.astype(np.int64)
        ):
            raise RuntimeError("D43 deterministic initialization is not exact D40")

        slot_returns = np.zeros(FROZEN["num_envs"], dtype=np.float64)
        for update in range(1, updates + 1):
            update_started = time.perf_counter()
            update_eligible = update_alternatives = 0
            update_episodes = []
            for step in range(FROZEN["rollout_steps"]):
                actor_features, critic_features, eligible, rank_zero, rank_one, _ = observe(
                    env, eligibility_model
                )
                if not np.array_equal(rank_zero, env.teacher_indices.astype(np.int64)):
                    raise RuntimeError("D43 exact-prior rank-zero drift")
                actor_buffer[step] = actor_features
                critic_buffer[step] = critic_features
                eligible_buffer[step] = eligible
                if probe_rows < 512 and np.any(eligible):
                    take = actor_features[eligible][: 512 - probe_rows].copy()
                    probe_parts.append(take)
                    probe_rows += len(take)
                with torch.inference_mode():
                    binary, logprob, _, value, _ = model.action_and_value(
                        torch.from_numpy(actor_features), torch.from_numpy(critic_features)
                    )
                binary_np = binary.numpy().astype(np.int8)
                binary_np[~eligible] = 0
                selected = np.where(binary_np == 1, rank_one, rank_zero)
                illegal = selected >= env.counts
                illegal_actions += int(illegal.sum())
                if illegal.any():
                    raise RuntimeError("D43 sampled illegal candidate index")
                current_alternatives = int(np.count_nonzero(binary_np[eligible]))
                current_noneligible = int(np.count_nonzero(binary_np[~eligible]))
                update_eligible += int(eligible.sum())
                update_alternatives += current_alternatives
                eligible_states += int(eligible.sum())
                sampled_alternatives += current_alternatives
                noneligible_deviations += current_noneligible
                action_buffer[step] = binary_np
                logprob_buffer[step] = logprob.numpy()
                value_buffer[step] = value.numpy()

                task_before = env.task_indices.copy()
                action_ids = env.actions[np.arange(FROZEN["num_envs"]), selected]
                _, _, _, rewards, info = env.step(action_ids)
                if not np.isfinite(rewards).all():
                    raise RuntimeError("nonfinite D43 environment reward")
                reward_buffer[step] = rewards
                done_buffer[step] = np.asarray(
                    [terminal is not None for terminal in info.terminals], dtype=np.float32
                )
                slot_returns += rewards.astype(np.float64)
                global_step += FROZEN["num_envs"]
                for slot, terminal in enumerate(info.terminals):
                    if terminal is None:
                        continue
                    if terminal["task_index"] != int(task_before[slot]):
                        raise RuntimeError("D43 terminal task drift")
                    identity_error = float(
                        abs(100.0 * slot_returns[slot] - terminal["margin"])
                    )
                    maximum_reward_identity_error = max(
                        maximum_reward_identity_error, identity_error
                    )
                    if identity_error > 1e-4:
                        raise RuntimeError(f"D43 reward identity failure: {identity_error}")
                    if (
                        terminal["invalid_direct_commands"]
                        or terminal["provenance_failures"]
                        or terminal["deposit_prediction_failures"]
                        or terminal["own_workers"] > 3
                    ):
                        raise RuntimeError(f"D43 terminal integrity failure: {terminal}")
                    episode = {**terminal, "reward_identity_error": identity_error}
                    update_episodes.append(episode)
                    all_episodes.append(episode)
                    slot_returns[slot] = 0.0

            actor_features, critic_features, *_ = observe(env, eligibility_model)
            with torch.inference_mode():
                _, _, _, next_value, _ = model.action_and_value(
                    torch.from_numpy(actor_features), torch.from_numpy(critic_features)
                )
            advantages = compute_advantages(
                reward_buffer,
                done_buffer,
                value_buffer,
                next_value.numpy(),
                gamma=FROZEN["gamma"],
                gae_lambda=FROZEN["gae_lambda"],
            )
            returns = advantages + value_buffer
            actor_advantages = normalize_eligible_advantages(advantages, eligible_buffer)

            flat_actor = actor_buffer.reshape(batch_size, ACTOR_FEATURES)
            flat_critic = critic_buffer.reshape(batch_size, CRITIC_FEATURES)
            flat_eligible = eligible_buffer.reshape(batch_size)
            flat_actions = action_buffer.reshape(batch_size)
            flat_logprobs = logprob_buffer.reshape(batch_size)
            flat_actor_advantages = actor_advantages.reshape(batch_size)
            flat_returns = returns.reshape(batch_size)
            indexes = np.arange(batch_size)
            policy_losses = []
            value_losses = []
            entropies = []
            approx_kls = []
            clip_fractions = []
            epochs_run = 0
            for epoch in range(FROZEN["update_epochs"]):
                rng.shuffle(indexes)
                epoch_kls = []
                for start in range(0, batch_size, FROZEN["minibatch_size"]):
                    minibatch = indexes[start : start + FROZEN["minibatch_size"]]
                    mb_actor = torch.from_numpy(flat_actor[minibatch])
                    mb_critic = torch.from_numpy(flat_critic[minibatch])
                    mb_actions = torch.from_numpy(flat_actions[minibatch])
                    _, new_logprob, entropy, new_value, _ = model.action_and_value(
                        mb_actor, mb_critic, action=mb_actions
                    )
                    mask_np = flat_eligible[minibatch]
                    mask = torch.from_numpy(mask_np)
                    if mask.any():
                        log_ratio = new_logprob[mask] - torch.from_numpy(
                            flat_logprobs[minibatch][mask_np]
                        )
                        ratio = log_ratio.exp()
                        advantage = torch.from_numpy(
                            flat_actor_advantages[minibatch][mask_np]
                        )
                        unclipped = -advantage * ratio
                        clipped = -advantage * ratio.clamp(
                            1.0 - FROZEN["clip_coef"], 1.0 + FROZEN["clip_coef"]
                        )
                        policy_loss = torch.maximum(unclipped, clipped).mean()
                        entropy_loss = entropy[mask].mean()
                        with torch.no_grad():
                            approx_kl = ((ratio - 1.0) - log_ratio).mean()
                            clip_fraction = (
                                (ratio - 1.0).abs() > FROZEN["clip_coef"]
                            ).float().mean()
                        approx_kls.append(float(approx_kl))
                        epoch_kls.append(float(approx_kl))
                        clip_fractions.append(float(clip_fraction))
                    else:
                        policy_loss = new_value.sum() * 0.0
                        entropy_loss = new_value.sum() * 0.0
                    value_loss = 0.5 * F.mse_loss(
                        new_value, torch.from_numpy(flat_returns[minibatch])
                    )
                    loss = (
                        policy_loss
                        + FROZEN["value_coef"] * value_loss
                        - FROZEN["entropy_coef"] * entropy_loss
                    )
                    if not torch.isfinite(loss):
                        raise RuntimeError("nonfinite D43 PPO loss")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), FROZEN["max_grad_norm"])
                    optimizer.step()
                    policy_losses.append(float(policy_loss.detach()))
                    value_losses.append(float(value_loss.detach()))
                    entropies.append(float(entropy_loss.detach()))
                epochs_run = epoch + 1
                if epoch_kls and np.mean(epoch_kls) > FROZEN["target_kl"]:
                    break
            all_policy_losses.extend(policy_losses)
            all_value_losses.extend(value_losses)
            all_kls.extend(approx_kls)
            all_clip_fractions.extend(clip_fractions)
            update_log = {
                "update": update,
                "global_step": global_step,
                "eligible_states": update_eligible,
                "sampled_alternatives": update_alternatives,
                "alternative_rate": (
                    update_alternatives / update_eligible if update_eligible else 0.0
                ),
                "episodes": episode_summary(update_episodes),
                "policy_loss": float(np.mean(policy_losses)),
                "value_loss": float(np.mean(value_losses)),
                "eligible_entropy": float(np.mean(entropies)),
                "eligible_approx_kl": float(np.mean(approx_kls)) if approx_kls else 0.0,
                "eligible_clip_fraction": (
                    float(np.mean(clip_fractions)) if clip_fractions else 0.0
                ),
                "epochs_run": epochs_run,
                "update_seconds": time.perf_counter() - update_started,
            }
            logs.append(update_log)
            if update == 1 or update % 4 == 0 or update == updates:
                print(json.dumps({"event": "update", **update_log}, sort_keys=True), flush=True)

    wall_seconds = time.perf_counter() - started_wall
    cpu_seconds = time.process_time() - started_cpu
    final_actor = torch.cat(
        [parameter.detach().flatten() for parameter in model.actor_parameters()]
    )
    actor_drift = float(torch.linalg.vector_norm(final_actor - initial_actor))
    probe = np.concatenate(probe_parts)[:512]
    with torch.inference_mode():
        probe_probabilities = torch.sigmoid(model.actor_logits(torch.from_numpy(probe))).numpy()
    probe_mean = float(probe_probabilities.mean())
    probe_std = float(probe_probabilities.std())
    probe_deterministic_alternatives = int(np.count_nonzero(probe_probabilities >= 0.5))
    alternative_rate = sampled_alternatives / eligible_states if eligible_states else 0.0
    effective_cores = cpu_seconds / wall_seconds
    throughput = global_step / wall_seconds
    losses_finite = (
        finite_list(all_policy_losses)
        and finite_list(all_value_losses)
        and finite_list(all_kls)
        and finite_list(all_clip_fractions)
    )
    gates = {
        "exact_transition_budget": global_step == FROZEN["total_transitions"],
        "at_least_1000_eligible_states": eligible_states >= 1_000,
        "at_least_200_sampled_alternatives": sampled_alternatives >= 200,
        "alternative_rate_between_15_and_35pct": 0.15 <= alternative_rate <= 0.35,
        "zero_noneligible_deviations": noneligible_deviations == 0,
        "zero_illegal_actions": illegal_actions == 0,
        "reward_identity": maximum_reward_identity_error <= 1e-4,
        "at_least_512_complete_episodes": len(all_episodes) >= 512,
        "actor_l2_drift_at_least_001": actor_drift >= 0.01,
        "probe_mean_moves_at_least_0005": abs(probe_mean - 0.25) >= 0.005,
        "probe_std_at_least_0005": probe_std >= 0.005,
        "losses_finite": losses_finite,
        "effective_cpu_at_least_12": effective_cores >= 12,
        "throughput_at_least_400": throughput >= 400,
    }
    reference = torch.load(RECOVERY_REFERENCE, map_location="cpu", weights_only=False)
    current_state = model.state_dict()
    recovery_checkpoint_bit_exact = (
        reference.get("config") == FROZEN
        and reference.get("model", {}).keys() == current_state.keys()
        and all(
            torch.equal(reference["model"][name], current_state[name])
            for name in current_state
        )
    )
    gates["recovery_checkpoint_bit_exact"] = recovery_checkpoint_bit_exact
    gates = {name: bool(value) for name, value in gates.items()}
    torch.save(
        {
            "model": model.state_dict(),
            "config": FROZEN,
            "actor_parameters": actor_parameter_count(model),
            "critic_parameters": critic_parameter_count(model),
        },
        CHECKPOINT,
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "recovery_protocol": str(RECOVERY_PROTOCOL),
        "recovery_protocol_sha256": sha256(RECOVERY_PROTOCOL),
        "recovery_reference": str(RECOVERY_REFERENCE),
        "recovery_reference_sha256": sha256(RECOVERY_REFERENCE),
        "recovery_checkpoint_bit_exact": recovery_checkpoint_bit_exact,
        "environment_library_sha256": sha256(Path(DEFAULT_LIBRARY)),
        "eligibility_checkpoint_sha256": sha256(ELIGIBILITY_CHECKPOINT),
        "config": FROZEN,
        "actor_features": ACTOR_FEATURES,
        "critic_features": CRITIC_FEATURES,
        "actor_parameters": actor_parameter_count(model),
        "critic_parameters": critic_parameter_count(model),
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "training": {
            "global_step": global_step,
            "updates": updates,
            "eligible_states": eligible_states,
            "sampled_alternatives": sampled_alternatives,
            "alternative_rate": alternative_rate,
            "noneligible_deviations": noneligible_deviations,
            "illegal_actions": illegal_actions,
            "episodes": episode_summary(all_episodes),
            "maximum_reward_identity_error": maximum_reward_identity_error,
            "actor_l2_drift": actor_drift,
            "wall_seconds": wall_seconds,
            "cpu_seconds": cpu_seconds,
            "effective_cpu_cores": effective_cores,
            "transitions_per_second": throughput,
            "logs": logs,
        },
        "probe": {
            "rows": len(probe),
            "initial_mean_probability": INITIAL_ALTERNATIVE_PROBABILITY,
            "final_mean_probability": probe_mean,
            "final_probability_std": probe_std,
            "final_minimum_probability": float(probe_probabilities.min()),
            "final_maximum_probability": float(probe_probabilities.max()),
            "deterministic_alternatives": probe_deterministic_alternatives,
        },
        "gates": gates,
        "pass": all(gates.values()),
        "scope": "D43 mechanical preflight only; no long training, development, or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "event": "result",
                "output": str(OUTPUT),
                "pass": report["pass"],
                "gates": gates,
                "training": {key: value for key, value in report["training"].items() if key != "logs"},
                "probe": report["probe"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
