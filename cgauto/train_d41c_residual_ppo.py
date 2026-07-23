#!/usr/bin/env python3
"""Train the single frozen D41c exact-prior residual PPO pilot."""

from __future__ import annotations

import argparse
import collections
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions.categorical import Categorical
from torch.nn import functional as F

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.evaluate_d41b_exact_prior import compare_repeats
from cgauto.rl_macro_env import (
    BRANCHES,
    CANDIDATE_FEATURES,
    DEFAULT_LIBRARY,
    MAX_CANDIDATES,
    OPPONENTS,
    TASKS_PER_MAP,
    MacroVecEnv,
)
from cgauto.train_d41a_macro_bc import read_baseline, summarize


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d41c-exact-prior-residual-ppo-protocol-2026-07-21.md"
PREFLIGHT = ANALYSIS / "d41c-rank-parallel-preflight-2026-07-21.json"
TEACHER_BASELINE = ANALYSIS / "d41c-development-teacher-9740000-9740031.tsv"
RANDOM_BASELINE = ANALYSIS / "d41c-development-random-9740000-9740031.tsv"
OUTPUT_PREFIX = ANALYSIS / "d41c-residual-ppo-seed411"

FROZEN = {
    "model_seed": 411,
    "train_seed_base": 9_730_000,
    "development_seed_base": 9_740_000,
    "development_maps": 32,
    "num_envs": 64,
    "rollout_steps": 64,
    "total_transitions": 1_048_576,
    "update_epochs": 4,
    "minibatch_size": 1_024,
    "learning_rate": 2.5e-4,
    "adam_epsilon": 1e-5,
    "gamma": 1.0,
    "gae_lambda": 0.95,
    "clip_coef": 0.10,
    "value_coef": 0.5,
    "entropy_coef": 0.001,
    "teacher_coef": 0.02,
    "max_grad_norm": 0.5,
    "target_kl": 0.01,
    "prior_temperature": 4.0,
    "threads": 20,
}


def layer_init(layer: nn.Linear, std: float = math.sqrt(2)) -> nn.Linear:
    nn.init.orthogonal_(layer.weight, std)
    nn.init.zeros_(layer.bias)
    return layer


class ExactPriorResidualActorCritic(nn.Module):
    def __init__(self, prior_temperature: float = 4.0) -> None:
        super().__init__()
        self.prior_temperature = float(prior_temperature)
        self.actor_hidden = layer_init(nn.Linear(CANDIDATE_FEATURES, 16))
        self.actor_output = nn.Linear(16, 1)
        nn.init.zeros_(self.actor_output.weight)
        nn.init.zeros_(self.actor_output.bias)
        self.critic = nn.Sequential(
            layer_init(nn.Linear(17 + 2 * CANDIDATE_FEATURES, 64)),
            nn.ReLU(),
            layer_init(nn.Linear(64, 32)),
            nn.ReLU(),
            layer_init(nn.Linear(32, 1), std=1.0),
        )

    def actor_parameters(self) -> list[nn.Parameter]:
        return list(self.actor_hidden.parameters()) + list(self.actor_output.parameters())

    def forward(
        self,
        features: torch.Tensor,
        counts: torch.Tensor,
        prior_ranks: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        features = features.float()
        counts = counts.long()
        candidate = torch.arange(features.shape[1], device=features.device)
        legal = candidate[None, :] < counts[:, None]
        residual = self.actor_output(F.relu(self.actor_hidden(features))).squeeze(-1)
        logits = -self.prior_temperature * prior_ranks.float() + residual
        logits = logits.masked_fill(~legal, -1e30)

        weights = legal.unsqueeze(-1).float()
        mean = (features * weights).sum(dim=1) / counts[:, None].clamp_min(1).float()
        maximum = features.masked_fill(~legal.unsqueeze(-1), -1e30).max(dim=1).values
        critic_input = torch.cat((features[:, 0, :17], mean, maximum), dim=1)
        value = self.critic(critic_input).squeeze(-1)
        return logits, value

    def action_and_value(
        self,
        features: torch.Tensor,
        counts: torch.Tensor,
        prior_ranks: torch.Tensor,
        action: torch.Tensor | None = None,
        *,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        logits, value = self(features, counts, prior_ranks)
        distribution = Categorical(logits=logits)
        if action is None:
            action = logits.argmax(dim=1) if deterministic else distribution.sample()
        return action, distribution.log_prob(action), distribution.entropy(), value, logits


def actor_parameter_count(model: ExactPriorResidualActorCritic) -> int:
    return sum(parameter.numel() for parameter in model.actor_parameters())


def critic_parameter_count(model: ExactPriorResidualActorCritic) -> int:
    return sum(parameter.numel() for parameter in model.critic.parameters())


def compute_advantages(
    rewards: np.ndarray,
    dones: np.ndarray,
    values: np.ndarray,
    next_values: np.ndarray,
    *,
    gamma: float,
    gae_lambda: float,
) -> np.ndarray:
    advantages = np.zeros_like(rewards, dtype=np.float32)
    last = np.zeros(rewards.shape[1], dtype=np.float32)
    for step in reversed(range(rewards.shape[0])):
        nonterminal = 1.0 - dones[step]
        following = next_values if step == len(rewards) - 1 else values[step + 1]
        delta = rewards[step] + gamma * following * nonterminal - values[step]
        last = delta + gamma * gae_lambda * nonterminal * last
        advantages[step] = last
    return advantages


def pack_observations(
    feature_steps: list[np.ndarray], rank_steps: list[np.ndarray]
) -> tuple[np.ndarray, np.ndarray]:
    if not feature_steps or len(feature_steps) != len(rank_steps):
        raise ValueError("feature/rank rollout steps must be nonempty and aligned")
    steps = len(feature_steps)
    num_envs = feature_steps[0].shape[0]
    maximum = max(array.shape[1] for array in feature_steps)
    features = np.zeros(
        (steps, num_envs, maximum, CANDIDATE_FEATURES), dtype=np.float32
    )
    ranks = np.full((steps, num_envs, maximum), np.iinfo(np.uint16).max, dtype=np.uint16)
    for step, (feature, rank) in enumerate(zip(feature_steps, rank_steps)):
        width = feature.shape[1]
        if rank.shape != (num_envs, width):
            raise ValueError("rank rollout shape mismatch")
        features[step, :, :width] = feature
        ranks[step, :, :width] = rank
    return features, ranks


def explained_variance(prediction: np.ndarray, target: np.ndarray) -> float:
    variance = float(np.var(target))
    if variance == 0.0:
        return float("nan")
    return float(1.0 - np.var(target - prediction) / variance)


def episode_summary(rows: list[dict]) -> dict:
    if not rows:
        return {"episodes": 0}
    return {
        "episodes": len(rows),
        "mean_margin": float(np.mean([row["margin"] for row in rows])),
        "mean_own_score": float(np.mean([row["own_score"] for row in rows])),
        "worker_two_rate": float(np.mean([row["own_workers"] >= 2 for row in rows])),
        "worker_three_rate": float(np.mean([row["own_workers"] >= 3 for row in rows])),
        "crop_rate": float(np.mean([row["own_created_crops"] > 0 for row in rows])),
        "maximum_reward_identity_error": max(
            row["reward_identity_error"] for row in rows
        ),
    }


@torch.inference_mode()
def evaluate(
    model: ExactPriorResidualActorCritic,
    *,
    seed_base: int,
    maps: int,
    num_envs: int,
) -> dict:
    model.eval()
    target_tasks = maps * TASKS_PER_MAP
    completed: dict[int, dict] = {}
    decisions = disagreements = illegal = 0
    branch_total: collections.Counter[int] = collections.Counter()
    branch_disagreements: collections.Counter[int] = collections.Counter()
    started = time.perf_counter()
    rounds = 0
    with MacroVecEnv(num_envs, seed_base) as env:
        while len(completed) < target_tasks:
            rounds += 1
            if rounds > 20_000:
                raise RuntimeError("D41c evaluation decision loop")
            maximum = int(env.counts.max())
            selected, _, _, _, _ = model.action_and_value(
                torch.from_numpy(env.features[:, :maximum]),
                torch.from_numpy(env.counts.astype(np.int64)),
                torch.from_numpy(env.prior_ranks[:, :maximum].astype(np.int64)),
                deterministic=True,
            )
            indices = selected.cpu().numpy()
            if np.any(indices >= env.counts):
                illegal += int(np.count_nonzero(indices >= env.counts))
            active = env.task_indices < target_tasks
            for slot in np.flatnonzero(active):
                branch = int(env.branches[slot])
                changed = int(indices[slot] != int(env.teacher_indices[slot]))
                branch_total[branch] += 1
                branch_disagreements[branch] += changed
                disagreements += changed
                decisions += 1
            actions = env.actions[np.arange(num_envs), indices]
            _, _, _, _, info = env.step(actions)
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed[terminal["task_index"]] = terminal
    rows = [completed[index] for index in range(target_tasks)]
    summary = summarize(rows)
    summary["maximum_workers"] = max(row["own_workers"] for row in rows)
    summary["illegal_argmaxes"] = illegal
    return {
        "seed_base": seed_base,
        "maps": maps,
        "episodes": target_tasks,
        "rounds": rounds,
        "decisions": decisions,
        "disagreements": disagreements,
        "disagreement_rate": disagreements / decisions,
        "branches": {
            BRANCHES[index]: {
                "decisions": branch_total[index],
                "disagreements": branch_disagreements[index],
                "disagreement_rate": (
                    branch_disagreements[index] / branch_total[index]
                    if branch_total[index]
                    else 0.0
                ),
            }
            for index in range(len(BRANCHES))
        },
        "summary": summary,
        "elapsed_seconds": time.perf_counter() - started,
        "episodes_detail": rows,
    }


def development_gate(learned: dict, teacher_rows: list[dict], random_rows: list[dict]) -> dict:
    learned_summary = learned["summary"]
    teacher = summarize(teacher_rows)
    random = summarize(random_rows)
    teacher_deltas = {
        opponent: learned_summary["by_opponent"][opponent]["mean_margin"]
        - teacher["by_opponent"][opponent]["mean_margin"]
        for opponent in OPPONENTS
    }
    random_gains = {
        opponent: learned_summary["by_opponent"][opponent]["mean_margin"]
        - random["by_opponent"][opponent]["mean_margin"]
        for opponent in OPPONENTS
    }
    gates = {
        "margin_at_least_5_above_d40": learned_summary["mean_margin"]
        >= teacher["mean_margin"] + 5,
        "margin_at_least_150_above_random": learned_summary["mean_margin"]
        >= random["mean_margin"] + 150,
        "at_least_five_families_improve": sum(value > 0 for value in teacher_deltas.values())
        >= 5,
        "no_family_below_minus_15": min(teacher_deltas.values()) >= -15,
        "own_score_within_5_of_d40": learned_summary["mean_own_score"]
        >= teacher["mean_own_score"] - 5,
        "worker_two_at_least_95pct": learned_summary["worker_two_rate"] >= 0.95,
        "worker_three_at_least_88pct": learned_summary["worker_three_rate"] >= 0.88,
        "crop_at_least_97pct": learned_summary["crop_rate"] >= 0.97,
        "integrity": learned_summary["invalid_direct_commands"] == 0
        and learned_summary["provenance_failures"] == 0
        and learned_summary["deposit_prediction_failures"] == 0
        and learned_summary["illegal_argmaxes"] == 0
        and learned_summary["maximum_workers"] <= 3,
        "bounded_nonzero_disagreement": 0 < learned["disagreement_rate"] <= 0.15,
    }
    return {
        "learned": learned_summary,
        "teacher": teacher,
        "random": random,
        "teacher_family_deltas": teacher_deltas,
        "random_family_gains": random_gains,
        "gates_without_repeat": gates,
        "pass_without_repeat": all(gates.values()),
    }


def save_actor_weights(model: ExactPriorResidualActorCritic, path: Path) -> None:
    np.savez(
        path,
        actor_hidden_weight=model.actor_hidden.weight.detach().cpu().numpy(),
        actor_hidden_bias=model.actor_hidden.bias.detach().cpu().numpy(),
        actor_output_weight=model.actor_output.weight.detach().cpu().numpy(),
        actor_output_bias=model.actor_output.bias.detach().cpu().numpy(),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", type=Path, default=OUTPUT_PREFIX)
    args = parser.parse_args()
    checkpoint_path = Path(f"{args.output_prefix}-final.pt")
    weights_path = Path(f"{args.output_prefix}-actor-weights.npz")
    result_path = Path(f"{args.output_prefix}-result.json")
    if any(path.exists() for path in (checkpoint_path, weights_path, result_path)):
        raise SystemExit("refusing to overwrite D41c artifacts")
    for required in (PROTOCOL, PREFLIGHT, TEACHER_BASELINE, RANDOM_BASELINE, Path(DEFAULT_LIBRARY)):
        if not required.exists():
            raise SystemExit(f"missing D41c prerequisite: {required}")
    preflight = json.loads(PREFLIGHT.read_text())
    if preflight.get("pass") is not True or preflight.get("chosen_num_envs") != FROZEN["num_envs"]:
        raise SystemExit("D41c rank/parallel preflight did not select frozen width 64")
    if preflight["protocol_sha256"] != sha256(PROTOCOL):
        raise SystemExit("D41c protocol changed after infrastructure preflight")
    if preflight["library_sha256"] != sha256(Path(DEFAULT_LIBRARY)):
        raise SystemExit("D41c environment library changed after infrastructure preflight")
    teacher_rows = read_baseline(
        TEACHER_BASELINE,
        "work_conserving",
        seed_base=FROZEN["development_seed_base"],
        maps=FROZEN["development_maps"],
    )
    random_rows = read_baseline(
        RANDOM_BASELINE,
        "random",
        seed_base=FROZEN["development_seed_base"],
        maps=FROZEN["development_maps"],
    )

    batch_size = FROZEN["num_envs"] * FROZEN["rollout_steps"]
    if batch_size != 4_096:
        raise SystemExit("D41c batch must contain 4,096 transitions")
    if FROZEN["total_transitions"] % batch_size:
        raise SystemExit("D41c transition geometry mismatch")
    if batch_size % FROZEN["minibatch_size"]:
        raise SystemExit("D41c minibatch geometry mismatch")
    total_updates = FROZEN["total_transitions"] // batch_size
    if total_updates != 256:
        raise SystemExit("D41c must contain 256 updates")

    torch.manual_seed(FROZEN["model_seed"])
    np.random.seed(FROZEN["model_seed"])
    torch.set_num_threads(FROZEN["threads"])
    torch.set_num_interop_threads(4)
    model = ExactPriorResidualActorCritic(FROZEN["prior_temperature"])
    if actor_parameter_count(model) != 737 or critic_parameter_count(model) != 8_897:
        raise SystemExit("D41c model parameter count drift")
    optimizer = torch.optim.Adam(
        model.parameters(), lr=FROZEN["learning_rate"], eps=FROZEN["adam_epsilon"]
    )
    rng = np.random.default_rng(FROZEN["model_seed"])
    initial_actor = torch.cat(
        [parameter.detach().flatten().clone() for parameter in model.actor_parameters()]
    )

    actions_buffer = np.empty(
        (FROZEN["rollout_steps"], FROZEN["num_envs"]), dtype=np.int64
    )
    logprob_buffer = np.empty_like(actions_buffer, dtype=np.float32)
    reward_buffer = np.empty_like(actions_buffer, dtype=np.float32)
    done_buffer = np.empty_like(actions_buffer, dtype=np.float32)
    value_buffer = np.empty_like(actions_buffer, dtype=np.float32)
    count_buffer = np.empty_like(actions_buffer, dtype=np.uint16)
    teacher_buffer = np.empty_like(actions_buffer, dtype=np.int64)

    logs = []
    all_episodes: list[dict] = []
    rank_histogram: collections.Counter[int] = collections.Counter()
    branch_histogram: collections.Counter[int] = collections.Counter()
    sampled_disagreements = 0
    global_step = 0
    illegal_actions = 0
    started_wall = time.perf_counter()
    started_cpu = time.process_time()

    with MacroVecEnv(FROZEN["num_envs"], FROZEN["train_seed_base"]) as env:
        maximum = int(env.counts.max())
        with torch.inference_mode():
            initial_action, _, _, _, _ = model.action_and_value(
                torch.from_numpy(env.features[:, :maximum]),
                torch.from_numpy(env.counts.astype(np.int64)),
                torch.from_numpy(env.prior_ranks[:, :maximum].astype(np.int64)),
                deterministic=True,
            )
        if not np.array_equal(initial_action.numpy(), env.teacher_indices.astype(np.int64)):
            raise RuntimeError("D41c deterministic initialization is not exact D40")

        slot_returns = np.zeros(FROZEN["num_envs"], dtype=np.float64)
        for update in range(1, total_updates + 1):
            update_started = time.perf_counter()
            feature_steps: list[np.ndarray] = []
            rank_steps: list[np.ndarray] = []
            update_episodes: list[dict] = []
            update_rank_histogram: collections.Counter[int] = collections.Counter()
            update_branch_histogram: collections.Counter[int] = collections.Counter()
            update_disagreements = 0
            rollout_started = time.perf_counter()

            for step in range(FROZEN["rollout_steps"]):
                maximum = int(env.counts.max())
                feature_steps.append(env.features[:, :maximum].copy())
                rank_steps.append(env.prior_ranks[:, :maximum].copy())
                count_buffer[step] = env.counts
                teacher_buffer[step] = env.teacher_indices
                with torch.inference_mode():
                    selected, logprob, _, value, _ = model.action_and_value(
                        torch.from_numpy(feature_steps[-1]),
                        torch.from_numpy(env.counts.astype(np.int64)),
                        torch.from_numpy(rank_steps[-1].astype(np.int64)),
                    )
                selected_np = selected.numpy()
                illegal = selected_np >= env.counts
                illegal_actions += int(illegal.sum())
                if illegal.any():
                    raise RuntimeError("D41c sampled illegal candidate index")
                selected_ranks = env.prior_ranks[
                    np.arange(FROZEN["num_envs"]), selected_np
                ].astype(np.int64)
                for rank in selected_ranks:
                    update_rank_histogram[int(rank)] += 1
                    rank_histogram[int(rank)] += 1
                changed = selected_np != env.teacher_indices.astype(np.int64)
                for branch in env.branches:
                    update_branch_histogram[int(branch)] += 1
                    branch_histogram[int(branch)] += 1
                update_disagreements += int(changed.sum())
                sampled_disagreements += int(changed.sum())

                actions_buffer[step] = selected_np
                logprob_buffer[step] = logprob.numpy()
                value_buffer[step] = value.numpy()
                task_before = env.task_indices.copy()
                action_ids = env.actions[np.arange(FROZEN["num_envs"]), selected_np]
                _, _, _, rewards, info = env.step(action_ids)
                if not np.isfinite(rewards).all():
                    raise RuntimeError("non-finite D41c environment reward")
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
                        raise RuntimeError("D41c terminal task drift")
                    identity_error = abs(100.0 * slot_returns[slot] - terminal["margin"])
                    if identity_error > 1e-4:
                        raise RuntimeError(f"D41c reward identity failure: {identity_error}")
                    if (
                        terminal["invalid_direct_commands"]
                        or terminal["provenance_failures"]
                        or terminal["deposit_prediction_failures"]
                        or terminal["own_workers"] > 3
                    ):
                        raise RuntimeError(f"D41c terminal integrity failure: {terminal}")
                    episode = {**terminal, "reward_identity_error": identity_error}
                    update_episodes.append(episode)
                    all_episodes.append(episode)
                    slot_returns[slot] = 0.0

            rollout_elapsed = time.perf_counter() - rollout_started
            packed_features, packed_ranks = pack_observations(feature_steps, rank_steps)
            del feature_steps, rank_steps
            maximum = int(env.counts.max())
            with torch.inference_mode():
                _, next_value = model(
                    torch.from_numpy(env.features[:, :maximum]),
                    torch.from_numpy(env.counts.astype(np.int64)),
                    torch.from_numpy(env.prior_ranks[:, :maximum].astype(np.int64)),
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
            normalized_advantages = (advantages - advantages.mean()) / (
                advantages.std() + 1e-8
            )

            flat_features = packed_features.reshape(
                batch_size, packed_features.shape[2], CANDIDATE_FEATURES
            )
            flat_ranks = packed_ranks.reshape(batch_size, packed_ranks.shape[2])
            flat_counts = count_buffer.reshape(batch_size).astype(np.int64)
            flat_actions = actions_buffer.reshape(batch_size)
            flat_logprobs = logprob_buffer.reshape(batch_size)
            flat_advantages = normalized_advantages.reshape(batch_size)
            flat_returns = returns.reshape(batch_size)
            flat_values = value_buffer.reshape(batch_size)
            flat_teacher = teacher_buffer.reshape(batch_size)

            if total_updates == 1:
                learning_rate = 0.0
            else:
                learning_rate = FROZEN["learning_rate"] * (
                    1.0 - (update - 1) / (total_updates - 1)
                )
            optimizer.param_groups[0]["lr"] = learning_rate
            indexes = np.arange(batch_size)
            policy_losses = []
            value_losses = []
            entropies = []
            teacher_losses = []
            teacher_accuracies = []
            approx_kls = []
            clip_fractions = []
            epochs_run = 0

            for epoch in range(FROZEN["update_epochs"]):
                rng.shuffle(indexes)
                epoch_kls = []
                for start in range(0, batch_size, FROZEN["minibatch_size"]):
                    minibatch = indexes[start : start + FROZEN["minibatch_size"]]
                    width = int(flat_counts[minibatch].max())
                    mb_features = torch.from_numpy(flat_features[minibatch, :width])
                    mb_ranks = torch.from_numpy(
                        flat_ranks[minibatch, :width].astype(np.int64)
                    )
                    mb_counts = torch.from_numpy(flat_counts[minibatch])
                    mb_actions = torch.from_numpy(flat_actions[minibatch])
                    _, new_logprob, entropy, new_value, logits = model.action_and_value(
                        mb_features, mb_counts, mb_ranks, action=mb_actions
                    )
                    log_ratio = new_logprob - torch.from_numpy(flat_logprobs[minibatch])
                    ratio = log_ratio.exp()
                    mb_advantage = torch.from_numpy(flat_advantages[minibatch])
                    unclipped = -mb_advantage * ratio
                    clipped = -mb_advantage * ratio.clamp(
                        1.0 - FROZEN["clip_coef"], 1.0 + FROZEN["clip_coef"]
                    )
                    policy_loss = torch.maximum(unclipped, clipped).mean()
                    value_loss = 0.5 * F.mse_loss(
                        new_value, torch.from_numpy(flat_returns[minibatch])
                    )
                    teacher_targets = torch.from_numpy(flat_teacher[minibatch])
                    teacher_loss = F.cross_entropy(logits, teacher_targets)
                    entropy_loss = entropy.mean()
                    loss = (
                        policy_loss
                        + FROZEN["value_coef"] * value_loss
                        - FROZEN["entropy_coef"] * entropy_loss
                        + FROZEN["teacher_coef"] * teacher_loss
                    )
                    if not torch.isfinite(loss):
                        raise RuntimeError("non-finite D41c PPO loss")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), FROZEN["max_grad_norm"])
                    optimizer.step()

                    with torch.no_grad():
                        approx_kl = ((ratio - 1.0) - log_ratio).mean()
                        clip_fraction = (
                            (ratio - 1.0).abs() > FROZEN["clip_coef"]
                        ).float().mean()
                    policy_losses.append(float(policy_loss.detach()))
                    value_losses.append(float(value_loss.detach()))
                    entropies.append(float(entropy_loss.detach()))
                    teacher_losses.append(float(teacher_loss.detach()))
                    teacher_accuracies.append(
                        float((logits.argmax(dim=1) == teacher_targets).float().mean())
                    )
                    approx_kls.append(float(approx_kl))
                    epoch_kls.append(float(approx_kl))
                    clip_fractions.append(float(clip_fraction))
                epochs_run = epoch + 1
                if np.mean(epoch_kls) > FROZEN["target_kl"]:
                    break

            update_log = {
                "update": update,
                "global_step": global_step,
                "learning_rate": learning_rate,
                "rollout_seconds": rollout_elapsed,
                "update_seconds": time.perf_counter() - update_started,
                "rollout_candidate_width": int(packed_features.shape[2]),
                "sampled_disagreement_rate": update_disagreements / batch_size,
                "sampled_rank_histogram": {
                    str(rank): count for rank, count in sorted(update_rank_histogram.items())
                },
                "branch_histogram": {
                    BRANCHES[branch]: count
                    for branch, count in sorted(update_branch_histogram.items())
                },
                "episodes": episode_summary(update_episodes),
                "policy_loss": float(np.mean(policy_losses)),
                "value_loss": float(np.mean(value_losses)),
                "entropy": float(np.mean(entropies)),
                "teacher_loss": float(np.mean(teacher_losses)),
                "teacher_accuracy": float(np.mean(teacher_accuracies)),
                "approx_kl": float(np.mean(approx_kls)),
                "clip_fraction": float(np.mean(clip_fractions)),
                "epochs_run": epochs_run,
                "explained_variance": explained_variance(flat_values, flat_returns),
            }
            logs.append(update_log)
            if update == 1 or update % 10 == 0 or update == total_updates:
                print(json.dumps({"event": "update", **update_log}, sort_keys=True), flush=True)
            del packed_features, packed_ranks, flat_features, flat_ranks

    training_wall = time.perf_counter() - started_wall
    training_cpu = time.process_time() - started_cpu
    final_actor = torch.cat(
        [parameter.detach().flatten() for parameter in model.actor_parameters()]
    )
    actor_drift = float(torch.linalg.vector_norm(final_actor - initial_actor))
    actor_initial_norm = float(torch.linalg.vector_norm(initial_actor))
    torch.save(
        {
            "model": model.state_dict(),
            "config": FROZEN,
            "actor_parameters": actor_parameter_count(model),
            "critic_parameters": critic_parameter_count(model),
        },
        checkpoint_path,
    )
    save_actor_weights(model, weights_path)

    first = evaluate(
        model,
        seed_base=FROZEN["development_seed_base"],
        maps=FROZEN["development_maps"],
        num_envs=FROZEN["num_envs"],
    )
    gate = development_gate(first, teacher_rows, random_rows)
    repeat = None
    repeat_exact = False
    if gate["pass_without_repeat"]:
        repeat = evaluate(
            model,
            seed_base=FROZEN["development_seed_base"],
            maps=FROZEN["development_maps"],
            num_envs=FROZEN["num_envs"],
        )
        repeat_exact = compare_repeats(
            first["episodes_detail"], repeat["episodes_detail"]
        )["exact"]
    gates = {**gate["gates_without_repeat"], "deterministic_repeat": repeat_exact}
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "preflight": str(PREFLIGHT),
        "preflight_sha256": sha256(PREFLIGHT),
        "teacher_baseline": str(TEACHER_BASELINE),
        "teacher_baseline_sha256": sha256(TEACHER_BASELINE),
        "random_baseline": str(RANDOM_BASELINE),
        "random_baseline_sha256": sha256(RANDOM_BASELINE),
        "library_sha256": sha256(Path(DEFAULT_LIBRARY)),
        "config": FROZEN,
        "actor_parameters": actor_parameter_count(model),
        "critic_parameters": critic_parameter_count(model),
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sha256(checkpoint_path),
        "actor_weights": str(weights_path),
        "actor_weights_sha256": sha256(weights_path),
        "training": {
            "global_step": global_step,
            "updates": total_updates,
            "illegal_actions": illegal_actions,
            "sampled_disagreements": sampled_disagreements,
            "sampled_disagreement_rate": sampled_disagreements / global_step,
            "sampled_rank_histogram": {
                str(rank): count for rank, count in sorted(rank_histogram.items())
            },
            "branch_histogram": {
                BRANCHES[branch]: count
                for branch, count in sorted(branch_histogram.items())
            },
            "episodes": episode_summary(all_episodes),
            "wall_seconds": training_wall,
            "cpu_seconds": training_cpu,
            "effective_cpu_cores": training_cpu / training_wall,
            "transitions_per_second": global_step / training_wall,
            "actor_l2_drift": actor_drift,
            "actor_initial_l2_norm": actor_initial_norm,
            "logs": logs,
        },
        "development": {
            **gate,
            "first": first,
            "repeat": repeat,
            "repeat_exact": repeat_exact,
        },
        "gates": gates,
        "pass": all(gates.values()),
    }
    result_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "event": "result",
                "result": str(result_path),
                "pass": report["pass"],
                "gates": gates,
                "training": {
                    key: value for key, value in report["training"].items() if key != "logs"
                },
                "development": {
                    "learned": gate["learned"],
                    "teacher_family_deltas": gate["teacher_family_deltas"],
                    "disagreement_rate": first["disagreement_rate"],
                    "repeat_exact": repeat_exact,
                },
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
