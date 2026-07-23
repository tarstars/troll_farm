#!/usr/bin/env python3
"""Train D108a's frozen recurrent masked q6 PPO signal candidate."""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time

import numpy as np
import torch
from torch import nn
from torch.distributions.categorical import Categorical
from torch.nn import functional as F

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto.rl_macro_env import OPPONENTS  # noqa: E402
from cgauto.rl_q6_proposal_env import (  # noqa: E402
    DEFAULT_EXPERTS,
    DEFAULT_LIBRARY,
    Q6_ACTIONS,
    Q6_ACTION_FEATURES,
    Q6_STATE_FEATURES,
    Q6ProposalVecEnv,
)
from cgauto.train_d41c_residual_ppo import compute_advantages, layer_init  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d108a-recurrent-masked-q6-ppo-protocol-2026-07-22.md"
PARITY = BASE / "d108a-q6-proposal-environment-parity.json"
OUTPUT = BASE / "d108a-recurrent-masked-q6-ppo-result.json"
CHECKPOINT = BASE / "d108a-recurrent-masked-q6-ppo-final.pt"
EVALUATION_A = BASE / "d108a-recurrent-masked-q6-ppo-evaluation-a.tsv"
EVALUATION_B = BASE / "d108a-recurrent-masked-q6-ppo-evaluation-b.tsv"
EXPECTED_HASHES = {
    PROTOCOL: "4e78b80167421f7a0a3ae8489511cbf60bb0d3babb868255fc96878a303b2ddb",
    PARITY: "92c6cda4049885ec54fc27f155c5be148cade5fb69c145bdd7f1a38670299818",
    ROOT / "cgauto/rl_q6_proposal_env.py": "8f102e1eca5a1bcc49ea932170b100eacea5848d7af097c0b21689229dc68911",
    ROOT / "rust/src/rl_q6_proposal.rs": "739fa02c00d92ba271f7a7a15fca893f18fffa258c02ba39c4a4cb08eaba2af1",
    Path(DEFAULT_EXPERTS): "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8",
    Path(DEFAULT_LIBRARY): "90284b35574e78740bdd1b1f81ea6ba5fdf03265a5ef029f1667a676748835cf",
}

HIDDEN = 12
ACTION_EMBED = 8
FROZEN = {
    "model_seed": 10_801,
    "train_seed_base": 9_833_000,
    "train_map_pool": 64,
    "evaluation_seed_base": 9_834_000,
    "evaluation_maps": 16,
    "num_envs": 20,
    "rollout_steps": 20,
    "total_transitions": 16_000,
    "update_epochs": 3,
    "minibatch_sequences": 5,
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
EVALUATION_FIELDS = (
    "policy",
    "task_index",
    "map_seed",
    "seat",
    "opponent",
    "own_score",
    "opponent_score",
    "margin",
    "baseline_own_score",
    "baseline_opponent_score",
    "baseline_margin",
    "margin_delta",
    "own_workers",
    "successful_trains",
    "own_created_crops",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "invalidated_jobs",
    "action_hash",
    "state_hash",
    "boundary_decisions",
    "intervention_batches",
    "joint_batches",
    "noncontrol_assignments",
    "controller_decisions",
    "controller_control_actions",
    "controller_noncontrol_actions",
    "controller_distinct_representatives",
    "controller_action_hash",
    "maximum_hidden_abs",
    "reward_identity_error",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class RecurrentProposalActorCritic(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.state_input = layer_init(nn.Linear(Q6_STATE_FEATURES, HIDDEN), std=0.35)
        self.recurrent = nn.Linear(HIDDEN, HIDDEN, bias=False)
        nn.init.orthogonal_(self.recurrent.weight, 0.70)
        self.action_projection = nn.Linear(Q6_ACTION_FEATURES, ACTION_EMBED, bias=False)
        nn.init.orthogonal_(self.action_projection.weight, 0.20)
        self.query = layer_init(nn.Linear(HIDDEN, ACTION_EMBED), std=0.20)
        self.direct = nn.Linear(Q6_ACTION_FEATURES, 1, bias=False)
        nn.init.zeros_(self.direct.weight)
        self.control = nn.Linear(HIDDEN, 1)
        nn.init.zeros_(self.control.weight)
        nn.init.zeros_(self.control.bias)
        self.critic = nn.Sequential(
            layer_init(nn.Linear(Q6_STATE_FEATURES, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 32)),
            nn.Tanh(),
            layer_init(nn.Linear(32, 1), std=1.0),
        )

    def actor_parameters(self) -> list[nn.Parameter]:
        return [
            *self.state_input.parameters(),
            *self.recurrent.parameters(),
            *self.action_projection.parameters(),
            *self.query.parameters(),
            *self.direct.parameters(),
            *self.control.parameters(),
        ]

    def next_hidden(self, state: torch.Tensor, hidden: torch.Tensor) -> torch.Tensor:
        return torch.tanh(self.state_input(state.float()) + self.recurrent(hidden))

    def logits(
        self,
        action_features: torch.Tensor,
        masks: torch.Tensor,
        hidden: torch.Tensor,
    ) -> torch.Tensor:
        action_features = action_features.float()
        embedding = torch.tanh(self.action_projection(action_features))
        query = torch.tanh(self.query(hidden)).unsqueeze(-2)
        logits = (embedding * query).sum(dim=-1) / math.sqrt(ACTION_EMBED)
        logits = logits + self.direct(action_features).squeeze(-1)
        logits = logits.clone()
        logits[..., 0] = self.control(hidden).squeeze(-1)
        return logits.masked_fill(~masks.bool(), -1.0e30)

    def value(self, state: torch.Tensor) -> torch.Tensor:
        return self.critic(state.float()).squeeze(-1)

    def action_and_value(
        self,
        state: torch.Tensor,
        action_features: torch.Tensor,
        masks: torch.Tensor,
        hidden: torch.Tensor,
        action: torch.Tensor | None = None,
        *,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        next_hidden = self.next_hidden(state, hidden)
        logits = self.logits(action_features, masks, next_hidden)
        distribution = Categorical(logits=logits)
        if action is None:
            action = logits.argmax(dim=-1) if deterministic else distribution.sample()
        return (
            action.long(),
            distribution.log_prob(action.long()),
            distribution.entropy(),
            self.value(state),
            next_hidden,
            logits,
        )

    def sequence_statistics(
        self,
        state: torch.Tensor,
        action_features: torch.Tensor,
        masks: torch.Tensor,
        actions: torch.Tensor,
        dones: torch.Tensor,
        initial_hidden: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        hidden = initial_hidden
        logprobs = []
        entropies = []
        values = []
        for step in range(state.shape[0]):
            _, logprob, entropy, value, hidden, _ = self.action_and_value(
                state[step],
                action_features[step],
                masks[step],
                hidden,
                action=actions[step],
            )
            logprobs.append(logprob)
            entropies.append(entropy)
            values.append(value)
            hidden = hidden * (1.0 - dones[step]).unsqueeze(-1)
        return torch.stack(logprobs), torch.stack(entropies), torch.stack(values)


def parameter_count(parameters) -> int:
    return sum(parameter.numel() for parameter in parameters)


def mix_action_hash(value: np.uint64, decision: int, action: int) -> np.uint64:
    current = int(value)
    for item in (decision, action):
        for byte in int(item).to_bytes(8, "little", signed=False):
            current ^= byte
            current = (current * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return np.uint64(current)


def episode_summary(rows: list[dict]) -> dict:
    if not rows:
        return {"episodes": 0}
    return {
        "episodes": len(rows),
        "mean_margin_delta": float(np.mean([row["margin_delta"] for row in rows])),
        "strict_improvement_rate": float(np.mean([row["margin_delta"] > 0 for row in rows])),
        "crop_rate": float(np.mean([row["own_created_crops"] > 0 for row in rows])),
        "worker_three_rate": float(np.mean([row["own_workers"] >= 3 for row in rows])),
        "intervention_rate": float(np.mean([row["intervention_batches"] > 0 for row in rows])),
        "repeated_rate": float(np.mean([row["intervention_batches"] >= 2 for row in rows])),
        "maximum_reward_identity_error": max(row["reward_identity_error"] for row in rows),
        "mechanical_failures": {
            field: int(sum(row[field] for row in rows))
            for field in (
                "invalid_direct_commands",
                "provenance_failures",
                "deposit_prediction_failures",
            )
        },
    }


def update_terminal_digest(digest: hashlib._Hash, row: dict) -> None:
    fields = (
        "task_index",
        "map_seed",
        "seat",
        "opponent",
        "margin_delta",
        "intervention_batches",
        "action_hash",
        "state_hash",
    )
    digest.update(json.dumps([row[field] for field in fields], separators=(",", ":")).encode())
    digest.update(b"\n")


def train() -> tuple[RecurrentProposalActorCritic, dict[str, torch.Tensor], dict, dict]:
    batch_size = FROZEN["num_envs"] * FROZEN["rollout_steps"]
    updates = FROZEN["total_transitions"] // batch_size
    if batch_size != 400 or updates != 40 or FROZEN["total_transitions"] % batch_size:
        raise RuntimeError("D108a frozen transition geometry mismatch")
    torch.manual_seed(FROZEN["model_seed"])
    np.random.seed(FROZEN["model_seed"])
    model = RecurrentProposalActorCritic()
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

    hidden = torch.zeros((FROZEN["num_envs"], HIDDEN), dtype=torch.float32)
    global_step = illegal_actions = 0
    control_actions = noncontrol_actions = 0
    used_representatives: set[int] = set()
    all_episodes: list[dict] = []
    terminal_digest = hashlib.sha256()
    losses: dict[str, list[float]] = collections.defaultdict(list)
    logs = []
    probe_state = []
    probe_actions = []
    probe_masks = []
    probe_hidden = []
    probe_seen: set[bytes] = set()
    initial_probe_choices: np.ndarray | None = None
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
                illegal = masks[rows, selected] != 1
                illegal_actions += int(np.count_nonzero(illegal))
                if np.any(illegal):
                    raise RuntimeError("D108a sampled masked proposal")
                control_actions += int(np.count_nonzero(selected == 0))
                chosen_noncontrol = selected[selected > 0]
                noncontrol_actions += len(chosen_noncontrol)
                update_noncontrol += len(chosen_noncontrol)
                used_representatives.update(chosen_noncontrol.tolist())
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
                        raise RuntimeError(f"D108a paired reward identity failure: {identity_error}")
                    episode = {**terminal, "reward_identity_error": float(identity_error)}
                    update_terminal_digest(terminal_digest, episode)
                    update_episodes.append(episode)
                    all_episodes.append(episode)
                    slot_returns[slot] = 0.0
                hidden = next_hidden * torch.from_numpy(1.0 - done).unsqueeze(-1)

            if update == 1:
                if len(probe_state) != FROZEN["probe_rows"]:
                    raise RuntimeError("D108a first rollout lacks 256 distinct live probes")
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
                        raise RuntimeError("non-finite D108a PPO loss")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    gradient_norm = nn.utils.clip_grad_norm_(
                        model.parameters(), FROZEN["max_grad_norm"]
                    )
                    if not torch.isfinite(gradient_norm):
                        raise RuntimeError("non-finite D108a gradient")
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
                raise RuntimeError("non-finite D108a parameter")
            log = {
                "update": update,
                "global_step": global_step,
                "episodes": episode_summary(update_episodes),
                "noncontrol_actions": update_noncontrol,
                "epochs_run": epochs_run,
                **{name: float(np.mean(values)) for name, values in update_metrics.items()},
                "update_seconds": time.perf_counter() - update_started,
            }
            logs.append(log)
            if update == 1 or update % 5 == 0 or update == updates:
                print(json.dumps({"event": "update", **log}, sort_keys=True), flush=True)

    wall_seconds = time.perf_counter() - started_wall
    cpu_seconds = time.process_time() - started_cpu
    if initial_probe_choices is None:
        raise RuntimeError("D108a initial probe missing")
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
    return model, initial_state, {
        "global_step": global_step,
        "updates": len(logs),
        "illegal_actions": illegal_actions,
        "control_actions": control_actions,
        "noncontrol_actions": noncontrol_actions,
        "noncontrol_rate": noncontrol_actions / global_step,
        "used_representatives": sorted(used_representatives),
        "episodes": episode_summary(all_episodes),
        "terminal_stream_sha256": terminal_digest.hexdigest(),
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "effective_cpu_cores": cpu_seconds / wall_seconds,
        "transitions_per_second": global_step / wall_seconds,
        "losses": {
            name: {"mean": float(np.mean(values)), "maximum": float(np.max(values)), "finite": bool(np.isfinite(values).all())}
            for name, values in losses.items()
        },
        "logs": logs,
    }, probe


@torch.inference_mode()
def evaluate_policy(label: str, model: RecurrentProposalActorCritic | None) -> list[dict]:
    tasks = FROZEN["evaluation_maps"] * 2 * len(OPPONENTS)
    n = FROZEN["num_envs"]
    hidden = torch.zeros((n, HIDDEN), dtype=torch.float32)
    returns = np.zeros(n, dtype=np.float64)
    decisions = np.zeros(n, dtype=np.int64)
    control = np.zeros(n, dtype=np.int64)
    noncontrol = np.zeros(n, dtype=np.int64)
    action_hash = np.full(n, np.uint64(0xCBF29CE484222325), dtype=np.uint64)
    representatives = [set() for _ in range(n)]
    maximum_hidden = np.zeros(n, dtype=np.float32)
    completed: dict[int, dict] = {}
    with Q6ProposalVecEnv(
        n,
        FROZEN["evaluation_seed_base"],
        map_pool=FROZEN["evaluation_maps"],
    ) as env:
        for _ in range(256):
            if model is None:
                selected = np.zeros(n, dtype=np.int32)
                next_hidden = hidden
            else:
                action, _, _, _, next_hidden, _ = model.action_and_value(
                    torch.from_numpy(env.state_features),
                    torch.from_numpy(env.action_features),
                    torch.from_numpy(env.masks),
                    hidden,
                    deterministic=True,
                )
                selected = action.numpy().astype(np.int32)
                maximum_hidden = np.maximum(
                    maximum_hidden, next_hidden.abs().amax(dim=1).numpy()
                )
            for slot, action in enumerate(selected):
                decisions[slot] += 1
                control[slot] += action == 0
                noncontrol[slot] += action > 0
                if action > 0:
                    representatives[slot].add(int(action))
                action_hash[slot] = mix_action_hash(
                    action_hash[slot], int(decisions[slot]), int(action)
                )
            _, _, _, rewards, info = env.step(selected)
            returns += rewards
            done = np.asarray([terminal is not None for terminal in info.terminals])
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                identity_error = abs(100.0 * returns[slot] - terminal["margin_delta"])
                task_index = terminal["task_index"]
                if task_index < tasks:
                    completed[task_index] = {
                        "policy": label,
                        **terminal,
                        "controller_decisions": int(decisions[slot]),
                        "controller_control_actions": int(control[slot]),
                        "controller_noncontrol_actions": int(noncontrol[slot]),
                        "controller_distinct_representatives": len(representatives[slot]),
                        "controller_action_hash": int(action_hash[slot]),
                        "maximum_hidden_abs": float(maximum_hidden[slot]),
                        "reward_identity_error": float(identity_error),
                    }
                returns[slot] = 0.0
                decisions[slot] = control[slot] = noncontrol[slot] = 0
                representatives[slot].clear()
                action_hash[slot] = np.uint64(0xCBF29CE484222325)
                maximum_hidden[slot] = 0.0
            hidden = next_hidden.clone()
            hidden[torch.from_numpy(done)] = 0.0
            if len(completed) == tasks:
                break
        else:
            raise RuntimeError(f"D108a {label} evaluation decision guard")
    return [completed[index] for index in range(tasks)]


def write_evaluation(path: Path, rows: list[dict]) -> None:
    with path.open("x", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=EVALUATION_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            output = dict(row)
            output["maximum_hidden_abs"] = f"{row['maximum_hidden_abs']:.8f}"
            output["reward_identity_error"] = f"{row['reward_identity_error']:.8f}"
            writer.writerow({field: output[field] for field in EVALUATION_FIELDS})


def evaluation_summary(rows: list[dict], policy: str) -> dict:
    selected = [row for row in rows if row["policy"] == policy]
    families = {
        opponent: statistics.fmean(row["margin_delta"] for row in selected if row["opponent"] == opponent)
        for opponent in OPPONENTS
    }
    return {
        "tasks": len(selected),
        "mean_margin_delta": statistics.fmean(row["margin_delta"] for row in selected),
        "strict_improvement_rate": statistics.fmean(row["margin_delta"] > 0 for row in selected),
        "mean_own_score_delta": statistics.fmean(row["own_score"] - row["baseline_own_score"] for row in selected),
        "mean_opponent_score_delta": statistics.fmean(row["opponent_score"] - row["baseline_opponent_score"] for row in selected),
        "family_mean_margin_delta": families,
        "positive_families": sum(value > 0 for value in families.values()),
        "worst_family": min(families.values()),
        "crop_rate": statistics.fmean(row["own_created_crops"] > 0 for row in selected),
        "worker_three_rate": statistics.fmean(row["own_workers"] >= 3 for row in selected),
        "intervention_rate": statistics.fmean(row["intervention_batches"] > 0 for row in selected),
        "repeated_rate": statistics.fmean(row["intervention_batches"] >= 2 for row in selected),
        "mean_interventions": statistics.fmean(row["intervention_batches"] for row in selected),
        "distinct_representatives": sum(row["controller_distinct_representatives"] for row in selected),
        "maximum_reward_identity_error": max(row["reward_identity_error"] for row in selected),
        "mechanical_failures": {
            field: sum(row[field] for row in selected)
            for field in ("invalid_direct_commands", "provenance_failures", "deposit_prediction_failures")
        },
    }


def paired_final_initial(rows: list[dict]) -> dict:
    final = {row["task_index"]: row for row in rows if row["policy"] == "final"}
    initial = {row["task_index"]: row for row in rows if row["policy"] == "initial"}
    deltas = [final[index]["margin"] - initial[index]["margin"] for index in sorted(final)]
    return {
        "mean_margin_delta": statistics.fmean(deltas),
        "strict_improvement_rate": statistics.fmean(value > 0 for value in deltas),
    }


def main() -> int:
    for output in (OUTPUT, CHECKPOINT, EVALUATION_A, EVALUATION_B):
        if output.exists():
            raise SystemExit(f"refusing to overwrite {output}")
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"D108a prerequisite hash mismatch: {path}: {actual}")
    parity = json.loads(PARITY.read_text())
    if not parity.get("pass"):
        raise SystemExit("D108a environment parity is not valid")
    os.environ["RAYON_NUM_THREADS"] = str(FROZEN["threads"])
    torch.set_num_threads(FROZEN["threads"])
    torch.set_num_interop_threads(4)
    model, initial_state, training, probe = train()
    torch.save(
        {
            "model": model.state_dict(),
            "config": FROZEN,
            "state_features": Q6_STATE_FEATURES,
            "actions": Q6_ACTIONS,
            "action_features": Q6_ACTION_FEATURES,
            "hidden": HIDDEN,
            "action_embed": ACTION_EMBED,
        },
        CHECKPOINT,
    )
    initial_model = RecurrentProposalActorCritic()
    initial_model.load_state_dict(initial_state)
    rows_a = [
        *evaluate_policy("control", None),
        *evaluate_policy("initial", initial_model),
        *evaluate_policy("final", model),
    ]
    rows_b = [
        *evaluate_policy("control", None),
        *evaluate_policy("initial", initial_model),
        *evaluate_policy("final", model),
    ]
    write_evaluation(EVALUATION_A, rows_a)
    write_evaluation(EVALUATION_B, rows_b)
    repeat_exact = EVALUATION_A.read_bytes() == EVALUATION_B.read_bytes()
    summaries = {policy: evaluation_summary(rows_a, policy) for policy in ("control", "initial", "final")}
    final = summaries["final"]
    control = summaries["control"]
    final_initial = paired_final_initial(rows_a)
    mechanics_gates = {
        "exact_training_budget": training["global_step"] == 16_000 and training["updates"] == 40,
        "finite_losses": all(value["finite"] for value in training["losses"].values()),
        "zero_illegal_actions": training["illegal_actions"] == 0,
        "at_least_2500_training_episodes": training["episodes"]["episodes"] >= 2_500,
        "paired_reward_identity": training["episodes"]["maximum_reward_identity_error"] < 1.0e-4,
        "zero_training_mechanical_failures": all(value == 0 for value in training["episodes"]["mechanical_failures"].values()),
        "training_explores_32_representatives": len(training["used_representatives"]) >= 32,
        "training_noncontrol_rate_20_to_95pct": 0.20 <= training["noncontrol_rate"] <= 0.95,
        "evaluation_complete": all(summary["tasks"] == 256 for summary in summaries.values()),
        "evaluation_repeat_byte_exact": repeat_exact,
        "evaluation_reward_identity": max(summary["maximum_reward_identity_error"] for summary in summaries.values()) < 1.0e-4,
        "evaluation_zero_mechanical_failures": all(value == 0 for value in final["mechanical_failures"].values()),
        "throughput_at_least_20": training["transitions_per_second"] >= 20,
    }
    signal_gates = {
        "probe_40_actions_change": probe["changed_actions"] >= 40,
        "probe_8_final_actions": probe["final_distinct_actions"] >= 8,
        "actor_l2_drift_010": probe["actor_l2_drift"] >= 0.10,
        "final_uses_8_representatives": final["distinct_representatives"] >= 8,
        "final_intervention_rate_20_to_95pct": 0.20 <= final["intervention_rate"] <= 0.95,
        "final_repeats_10pct": final["repeated_rate"] >= 0.10,
    }
    safety_gates = {
        "final_crop_100pct": final["crop_rate"] == 1.0,
        "final_worker_three_within_5pp_control": final["worker_three_rate"] >= control["worker_three_rate"] - 0.05,
    }
    value_gates = {
        "final_mean_gain_at_least_1": final["mean_margin_delta"] >= 1.0,
        "final_strict_improvement_25pct": final["strict_improvement_rate"] >= 0.25,
        "final_worst_family_at_least_minus5": final["worst_family"] >= -5.0,
        "final_five_positive_families": final["positive_families"] >= 5,
        "final_own_nonnegative_or_opponent_nonpositive": final["mean_own_score_delta"] >= 0 or final["mean_opponent_score_delta"] <= 0,
        "final_beats_initial_by_1": final_initial["mean_margin_delta"] >= 1.0,
    }
    passes = {
        "mechanics": all(mechanics_gates.values()),
        "signal": all(signal_gates.values()),
        "safety": all(safety_gates.values()),
        "value": all(value_gates.values()),
    }
    full_pass = all(passes.values())
    result = {
        "schema": "troll-farm-d108a-recurrent-masked-q6-ppo-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "inputs": {
            "protocol": sha256(PROTOCOL),
            "parity": sha256(PARITY),
            "wrapper": sha256(ROOT / "cgauto/rl_q6_proposal_env.py"),
            "rust_env": sha256(ROOT / "rust/src/rl_q6_proposal.rs"),
            "experts": sha256(DEFAULT_EXPERTS),
            "library": sha256(DEFAULT_LIBRARY),
            "trainer": sha256(Path(__file__)),
            "checkpoint": sha256(CHECKPOINT),
            "evaluation_a": sha256(EVALUATION_A),
            "evaluation_b": sha256(EVALUATION_B),
        },
        "config": FROZEN,
        "model": {
            "hidden": HIDDEN,
            "action_embed": ACTION_EMBED,
            "actor_parameters": parameter_count(model.actor_parameters()),
            "critic_parameters": parameter_count(model.critic.parameters()),
            "total_parameters": parameter_count(model.parameters()),
        },
        "training": training,
        "probe": probe,
        "evaluation": {
            "repeat_exact": repeat_exact,
            "summaries": summaries,
            "final_versus_initial": final_initial,
        },
        "gates": {
            "mechanics": mechanics_gates,
            "signal": signal_gates,
            "safety": safety_gates,
            "value": value_gates,
            "passes": passes,
            "full_pass": full_pass,
        },
        "decision": (
            "open_d108b_longer_held_confirmation"
            if full_pass
            else "close_or_revise_d108a_from_frozen_failure_class"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"gates": result["gates"], "evaluation": result["evaluation"], "decision": result["decision"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
