#!/usr/bin/env python3
"""Run D73's frozen four-mode recurrent PPO signal preflight."""

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
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new  # noqa: E402
from cgauto.rl_batch_option_env import DEFAULT_LIBRARY, OPPONENTS  # noqa: E402
from cgauto.rl_opening_recurrent_env import (  # noqa: E402
    OPENING_RECURRENT_ACTIONS,
    OPENING_RECURRENT_FEATURES,
    OPENING_RECURRENT_MODES,
    OpeningRecurrentVecEnv,
)
from cgauto.train_d41c_residual_ppo import compute_advantages, layer_init  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d73a-four-mode-recurrent-ppo-signal-protocol-2026-07-21.md"
PARITY = ANALYSIS / "d73a-opening-recurrent-environment-parity.json"
WRAPPER = ROOT / "cgauto/rl_opening_recurrent_env.py"
VALIDATOR = ROOT / "cgauto/validate_d73a_opening_recurrent_env.py"
RUST_ENV = ROOT / "rust/src/rl_opening_portfolio.rs"
LIBRARY = Path(DEFAULT_LIBRARY)
OUTPUT = ANALYSIS / "d73a-four-mode-recurrent-ppo-signal-result.json"
CHECKPOINT = ANALYSIS / "d73a-four-mode-recurrent-ppo-final.pt"
EVALUATION_A = ANALYSIS / "d73a-four-mode-recurrent-ppo-evaluation-a.tsv"
EVALUATION_B = ANALYSIS / "d73a-four-mode-recurrent-ppo-evaluation-b.tsv"

EXPECTED_HASHES = {
    PROTOCOL: "3a277b41072a9a22c49a72315f51760f248091d9b84adbc63d21c27e666bab13",
    PARITY: "815e228e10308458073879edfed4abbdab03b3d6b8ab1ce13947980e263d145c",
    WRAPPER: "4e38680dfd024406772791d5577b2aff16f219168649d653eedf7f1d64224b50",
    VALIDATOR: "b5c55b20833660e5c97e7d35f7af47ec0967c967b18948eef2da6efb507344fc",
    RUST_ENV: "a83be1de2de000679da1e4216ebf87875ee84ad0c0b41fa165f2c7d3497c2e45",
    LIBRARY: "223b8bd49960cfaea7f0f5a6ad1541fd4bf61ba87a460036f8437473e8206d17",
}
HIDDEN = 12
ACTOR_PARAMETERS = (
    HIDDEN * OPENING_RECURRENT_FEATURES
    + HIDDEN * HIDDEN
    + HIDDEN
    + OPENING_RECURRENT_ACTIONS * HIDDEN
    + OPENING_RECURRENT_ACTIONS
)
CRITIC_PARAMETERS = 6_785
FROZEN = {
    "model_seed": 7_301,
    "train_seed_base": 9_810_000,
    "evaluation_seed_base": 9_811_000,
    "evaluation_maps": 16,
    "num_envs": 64,
    "rollout_steps": 64,
    "total_transitions": 131_072,
    "update_epochs": 4,
    "minibatch_sequences": 16,
    "learning_rate": 2.5e-4,
    "adam_epsilon": 1e-5,
    "gamma": 1.0,
    "gae_lambda": 0.95,
    "clip_coef": 0.15,
    "entropy_coef": 0.01,
    "value_coef": 0.5,
    "max_grad_norm": 0.5,
    "target_kl": 0.02,
    "threads": 20,
    "probe_rows": 512,
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
    "action_balanced",
    "action_harvest",
    "action_renew",
    "action_fell",
    "unlocked_decisions",
    "unlocked_balanced",
    "unlocked_harvest",
    "unlocked_renew",
    "unlocked_fell",
    "option_hash",
    "maximum_hidden_abs",
    "reward_identity_error",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def actor_arrays(seed: int = FROZEN["model_seed"]) -> tuple[np.ndarray, ...]:
    rng = np.random.Generator(np.random.PCG64(seed))
    wx = rng.normal(0.0, 0.35, size=(HIDDEN, OPENING_RECURRENT_FEATURES))
    raw = rng.normal(size=(HIDDEN, HIDDEN))
    q, r = np.linalg.qr(raw)
    signs = np.where(np.diag(r) < 0, -1.0, 1.0)
    wh = q * signs
    wh *= 0.70
    bh = rng.normal(0.0, 0.10, size=HIDDEN)
    wo = rng.normal(0.0, 0.50, size=(OPENING_RECURRENT_ACTIONS, HIDDEN))
    bo = rng.normal(0.0, 0.15, size=OPENING_RECURRENT_ACTIONS)
    return tuple(np.round(array, 8).astype(np.float32) for array in (wx, wh, bh, wo, bo))


class RecurrentActorCritic(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.actor_input = nn.Linear(OPENING_RECURRENT_FEATURES, HIDDEN)
        self.actor_recurrent = nn.Linear(HIDDEN, HIDDEN, bias=False)
        self.actor_output = nn.Linear(HIDDEN, OPENING_RECURRENT_ACTIONS)
        self.critic = nn.Sequential(
            layer_init(nn.Linear(OPENING_RECURRENT_FEATURES, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 32)),
            nn.Tanh(),
            layer_init(nn.Linear(32, 1), std=1.0),
        )
        wx, wh, bh, wo, bo = actor_arrays()
        with torch.no_grad():
            self.actor_input.weight.copy_(torch.from_numpy(wx))
            self.actor_input.bias.copy_(torch.from_numpy(bh))
            self.actor_recurrent.weight.copy_(torch.from_numpy(wh))
            self.actor_output.weight.copy_(torch.from_numpy(wo))
            self.actor_output.bias.copy_(torch.from_numpy(bo))

    def actor_parameters(self) -> list[nn.Parameter]:
        return [
            *self.actor_input.parameters(),
            *self.actor_recurrent.parameters(),
            *self.actor_output.parameters(),
        ]

    def actor_hidden(self, features: torch.Tensor, hidden: torch.Tensor) -> torch.Tensor:
        return torch.tanh(self.actor_input(features.float()) + self.actor_recurrent(hidden))

    def action_and_value(
        self,
        features: torch.Tensor,
        masks: torch.Tensor,
        hidden: torch.Tensor,
        action: torch.Tensor | None = None,
        *,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        next_hidden = self.actor_hidden(features, hidden)
        logits = self.actor_output(next_hidden)
        masked_logits = logits.masked_fill(~masks.bool(), -1.0e30)
        distribution = Categorical(logits=masked_logits)
        if action is None:
            action = masked_logits.argmax(dim=-1) if deterministic else distribution.sample()
        value = self.critic(features.float()).squeeze(-1)
        return (
            action.long(),
            distribution.log_prob(action.long()),
            distribution.entropy(),
            value,
            next_hidden,
            masked_logits,
        )

    def sequence_statistics(
        self,
        features: torch.Tensor,
        masks: torch.Tensor,
        actions: torch.Tensor,
        dones: torch.Tensor,
        initial_hidden: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        hidden = initial_hidden
        logprobs = []
        entropies = []
        values = []
        for step in range(features.shape[0]):
            _, logprob, entropy, value, hidden, _ = self.action_and_value(
                features[step], masks[step], hidden, action=actions[step]
            )
            logprobs.append(logprob)
            entropies.append(entropy)
            values.append(value)
            hidden = hidden * (1.0 - dones[step]).unsqueeze(-1)
        return torch.stack(logprobs), torch.stack(entropies), torch.stack(values)


def parameter_count(parameters: list[nn.Parameter]) -> int:
    return sum(parameter.numel() for parameter in parameters)


def clone_state(model: nn.Module) -> dict[str, torch.Tensor]:
    return {name: value.detach().clone() for name, value in model.state_dict().items()}


def finite_list(values: list[float]) -> bool:
    return bool(values) and bool(np.isfinite(np.asarray(values)).all())


def summarize_episodes(rows: list[dict]) -> dict:
    if not rows:
        return {"episodes": 0}
    return {
        "episodes": len(rows),
        "mean_margin": float(np.mean([row["margin"] for row in rows])),
        "mean_own_score": float(np.mean([row["own_score"] for row in rows])),
        "mean_opponent_score": float(np.mean([row["opponent_score"] for row in rows])),
        "worker_three_rate": float(np.mean([row["own_workers"] >= 3 for row in rows])),
        "crop_rate": float(np.mean([row["own_created_crops"] > 0 for row in rows])),
        "maximum_reward_identity_error": float(
            max(row["reward_identity_error"] for row in rows)
        ),
        "mechanical_failures": {
            field: int(sum(row[field] for row in rows))
            for field in (
                "invalid_direct_commands",
                "provenance_failures",
                "deposit_prediction_failures",
            )
        },
        "invalidated_jobs": int(sum(row["invalidated_jobs"] for row in rows)),
    }


def update_digest(digest: hashlib._Hash, row: dict) -> None:
    fields = (
        "task_index",
        "map_seed",
        "seat",
        "opponent",
        "own_score",
        "opponent_score",
        "own_workers",
        "successful_trains",
        "own_created_crops",
        "action_hash",
        "state_hash",
    )
    digest.update(json.dumps([row[field] for field in fields], separators=(",", ":")).encode())
    digest.update(b"\n")


def mix_option_hash(value: np.uint64, decision: int, action: int) -> np.uint64:
    current = int(value)
    for item in (decision, action):
        for byte in int(item).to_bytes(8, "little", signed=False):
            current ^= byte
            current = (current * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return np.uint64(current)


@torch.inference_mode()
def evaluate_policy(
    label: str,
    model: RecurrentActorCritic | None,
) -> list[dict]:
    total_tasks = FROZEN["evaluation_maps"] * 2 * len(OPPONENTS)
    num_envs = FROZEN["num_envs"]
    completed: dict[int, dict] = {}
    hidden = torch.zeros((num_envs, HIDDEN), dtype=torch.float32)
    slot_returns = np.zeros(num_envs, dtype=np.float64)
    action_counts = np.zeros((num_envs, OPENING_RECURRENT_ACTIONS), dtype=np.int64)
    unlocked_counts = np.zeros((num_envs, OPENING_RECURRENT_ACTIONS), dtype=np.int64)
    option_hashes = np.full(num_envs, np.uint64(0xCBF29CE484222325), dtype=np.uint64)
    maximum_hidden = np.zeros(num_envs, dtype=np.float32)
    with OpeningRecurrentVecEnv(num_envs, FROZEN["evaluation_seed_base"]) as env:
        for _ in range(5_000):
            masks = env.masks.copy()
            if model is None:
                actions = np.zeros(num_envs, dtype=np.int32)
                next_hidden = hidden
            else:
                action, _, _, _, next_hidden, _ = model.action_and_value(
                    torch.from_numpy(env.features),
                    torch.from_numpy(masks),
                    hidden,
                    deterministic=True,
                )
                actions = action.numpy().astype(np.int32)
            rows = np.arange(num_envs)
            if np.any(masks[rows, actions] != 1):
                raise RuntimeError(f"D73 {label} selected an illegal evaluation action")
            unlocked = masks.sum(axis=1) == OPENING_RECURRENT_ACTIONS
            for slot, action in enumerate(actions):
                action_counts[slot, action] += 1
                if unlocked[slot]:
                    unlocked_counts[slot, action] += 1
                option_hashes[slot] = mix_option_hash(
                    option_hashes[slot], int(action_counts[slot].sum()), int(action)
                )
            if model is not None:
                maximum_hidden = np.maximum(
                    maximum_hidden,
                    next_hidden.abs().amax(dim=1).numpy(),
                )
            _, _, rewards, info = env.step(actions)
            slot_returns += rewards.astype(np.float64)
            done = np.asarray(
                [terminal is not None for terminal in info.terminals], dtype=bool
            )
            for slot, terminal in enumerate(info.terminals):
                if terminal is None:
                    continue
                identity_error = float(
                    abs(100.0 * slot_returns[slot] - terminal["margin"])
                )
                task_index = terminal["task_index"]
                if task_index < total_tasks:
                    if task_index in completed:
                        raise RuntimeError(f"duplicate D73 evaluation task {task_index}")
                    completed[task_index] = {
                        "policy": label,
                        **terminal,
                        "boundary_decisions": int(action_counts[slot].sum()),
                        **{
                            f"action_{mode}": int(action_counts[slot, index])
                            for index, mode in enumerate(OPENING_RECURRENT_MODES)
                        },
                        "unlocked_decisions": int(unlocked_counts[slot].sum()),
                        **{
                            f"unlocked_{mode}": int(unlocked_counts[slot, index])
                            for index, mode in enumerate(OPENING_RECURRENT_MODES)
                        },
                        "option_hash": int(option_hashes[slot]),
                        "maximum_hidden_abs": float(maximum_hidden[slot]),
                        "reward_identity_error": identity_error,
                    }
                slot_returns[slot] = 0.0
                action_counts[slot].fill(0)
                unlocked_counts[slot].fill(0)
                option_hashes[slot] = np.uint64(0xCBF29CE484222325)
                maximum_hidden[slot] = 0.0
            if np.any(done):
                next_hidden = next_hidden.clone()
                next_hidden[torch.from_numpy(done)] = 0.0
            hidden = next_hidden
            if len(completed) == total_tasks:
                break
        else:
            raise RuntimeError(f"D73 {label} evaluation exceeded decision guard")
    return [completed[index] for index in range(total_tasks)]


def write_evaluation(path: Path, rows: list[dict]) -> None:
    with path.open("x", newline="") as target:
        writer = csv.DictWriter(
            target, fieldnames=EVALUATION_FIELDS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            output = dict(row)
            output["reward_identity_error"] = f"{row['reward_identity_error']:.8f}"
            output["maximum_hidden_abs"] = f"{row['maximum_hidden_abs']:.8f}"
            writer.writerow({field: output[field] for field in EVALUATION_FIELDS})


def evaluation_summary(rows: list[dict], policy: str) -> dict:
    selected = [row for row in rows if row["policy"] == policy]
    unlocked = sum(row["unlocked_decisions"] for row in selected)
    unlocked_actions = {
        mode: sum(row[f"unlocked_{mode}"] for row in selected)
        for mode in OPENING_RECURRENT_MODES
    }
    return {
        "tasks": len(selected),
        "mean_margin": statistics.fmean(row["margin"] for row in selected),
        "mean_own_score": statistics.fmean(row["own_score"] for row in selected),
        "mean_opponent_score": statistics.fmean(row["opponent_score"] for row in selected),
        "crop_tasks": sum(row["own_created_crops"] > 0 for row in selected),
        "worker_three_tasks": sum(row["own_workers"] >= 3 for row in selected),
        "worker_three_rate": sum(row["own_workers"] >= 3 for row in selected)
        / len(selected),
        "unlocked_decisions": unlocked,
        "unlocked_action_counts": unlocked_actions,
        "unlocked_nonbalanced_rate": (
            sum(unlocked_actions[mode] for mode in OPENING_RECURRENT_MODES[1:])
            / unlocked
        ),
        "used_unlocked_modes": sum(value > 0 for value in unlocked_actions.values()),
        "mechanical_failures": {
            field: sum(row[field] for row in selected)
            for field in (
                "invalid_direct_commands",
                "provenance_failures",
                "deposit_prediction_failures",
            )
        },
        "maximum_reward_identity_error": max(
            row["reward_identity_error"] for row in selected
        ),
    }


def paired_comparison(rows: list[dict], candidate: str, baseline: str) -> dict:
    left = {row["task_index"]: row for row in rows if row["policy"] == candidate}
    right = {row["task_index"]: row for row in rows if row["policy"] == baseline}
    keys = sorted(set(left) & set(right))
    margin = [left[key]["margin"] - right[key]["margin"] for key in keys]
    own = [left[key]["own_score"] - right[key]["own_score"] for key in keys]
    opponent = [
        left[key]["opponent_score"] - right[key]["opponent_score"] for key in keys
    ]
    family = {}
    for name in OPPONENTS:
        values = [
            left[key]["margin"] - right[key]["margin"]
            for key in keys
            if left[key]["opponent"] == name
        ]
        family[name] = statistics.fmean(values)
    return {
        "candidate_tasks": len(left),
        "baseline_tasks": len(right),
        "identity_exact": set(left) == set(right),
        "mean_margin_delta": statistics.fmean(margin),
        "strict_improvement_tasks": sum(value > 0 for value in margin),
        "strict_improvement_rate": sum(value > 0 for value in margin) / len(margin),
        "ties": sum(value == 0 for value in margin),
        "regressions": sum(value < 0 for value in margin),
        "mean_own_score_delta": statistics.fmean(own),
        "mean_opponent_score_delta": statistics.fmean(opponent),
        "opponent_mean_margin_delta": family,
        "positive_opponent_families": sum(value > 0 for value in family.values()),
    }


def train() -> tuple[
    RecurrentActorCritic,
    dict[str, torch.Tensor],
    dict,
    dict,
]:
    batch_size = FROZEN["num_envs"] * FROZEN["rollout_steps"]
    updates = FROZEN["total_transitions"] // batch_size
    if batch_size != 4_096 or updates != 32 or FROZEN["total_transitions"] % batch_size:
        raise RuntimeError("D73 frozen transition geometry mismatch")
    torch.manual_seed(FROZEN["model_seed"])
    np.random.seed(FROZEN["model_seed"])
    model = RecurrentActorCritic()
    if parameter_count(model.actor_parameters()) != ACTOR_PARAMETERS:
        raise RuntimeError("D73 actor parameter count drift")
    if parameter_count(list(model.critic.parameters())) != CRITIC_PARAMETERS:
        raise RuntimeError("D73 critic parameter count drift")
    initial_state = clone_state(model)
    initial_actor = torch.cat(
        [parameter.detach().flatten().clone() for parameter in model.actor_parameters()]
    )
    optimizer = torch.optim.Adam(
        model.parameters(), lr=FROZEN["learning_rate"], eps=FROZEN["adam_epsilon"]
    )
    rng = np.random.default_rng(FROZEN["model_seed"])

    shape = (FROZEN["rollout_steps"], FROZEN["num_envs"])
    feature_buffer = np.empty((*shape, OPENING_RECURRENT_FEATURES), dtype=np.float32)
    mask_buffer = np.empty((*shape, OPENING_RECURRENT_ACTIONS), dtype=np.uint8)
    action_buffer = np.empty(shape, dtype=np.int64)
    logprob_buffer = np.empty(shape, dtype=np.float32)
    reward_buffer = np.empty(shape, dtype=np.float32)
    done_buffer = np.empty(shape, dtype=np.float32)
    value_buffer = np.empty(shape, dtype=np.float32)

    global_step = unlocked_transitions = illegal_actions = 0
    unlocked_action_counts = np.zeros(OPENING_RECURRENT_ACTIONS, dtype=np.int64)
    all_episodes: list[dict] = []
    terminal_digest = hashlib.sha256()
    logs = []
    losses: dict[str, list[float]] = collections.defaultdict(list)
    parameter_nonfinite_events = 0
    probe_features: list[np.ndarray] = []
    probe_hidden: list[np.ndarray] = []
    probe_masks: list[np.ndarray] = []
    probe_seen: set[bytes] = set()
    initial_probe_actions: np.ndarray | None = None
    hidden = torch.zeros((FROZEN["num_envs"], HIDDEN), dtype=torch.float32)
    started_wall = time.perf_counter()
    started_cpu = time.process_time()

    with OpeningRecurrentVecEnv(FROZEN["num_envs"], FROZEN["train_seed_base"]) as env:
        slot_returns = np.zeros(FROZEN["num_envs"], dtype=np.float64)
        for update in range(1, updates + 1):
            update_started = time.perf_counter()
            rollout_initial_hidden = hidden.detach().numpy().copy()
            update_episodes = []
            update_actions = np.zeros(OPENING_RECURRENT_ACTIONS, dtype=np.int64)
            for step in range(FROZEN["rollout_steps"]):
                features = env.features.copy()
                masks = env.masks.copy()
                feature_buffer[step] = features
                mask_buffer[step] = masks
                unlocked = masks.sum(axis=1) == OPENING_RECURRENT_ACTIONS
                if update == 1 and len(probe_features) < FROZEN["probe_rows"]:
                    incoming = hidden.numpy()
                    for slot in np.flatnonzero(unlocked):
                        key = features[slot].tobytes() + incoming[slot].tobytes()
                        if key in probe_seen:
                            continue
                        probe_seen.add(key)
                        probe_features.append(features[slot].copy())
                        probe_hidden.append(incoming[slot].copy())
                        probe_masks.append(masks[slot].copy())
                        if len(probe_features) == FROZEN["probe_rows"]:
                            break
                with torch.inference_mode():
                    action, logprob, _, value, next_hidden, _ = model.action_and_value(
                        torch.from_numpy(features),
                        torch.from_numpy(masks),
                        hidden,
                    )
                actions = action.numpy().astype(np.int64)
                rows = np.arange(FROZEN["num_envs"])
                illegal = masks[rows, actions] != 1
                illegal_actions += int(np.count_nonzero(illegal))
                if np.any(illegal):
                    raise RuntimeError("D73 sampled an illegal action")
                unlocked_transitions += int(np.count_nonzero(unlocked))
                for mode in range(OPENING_RECURRENT_ACTIONS):
                    count = int(np.count_nonzero(unlocked & (actions == mode)))
                    unlocked_action_counts[mode] += count
                    update_actions[mode] += count
                action_buffer[step] = actions
                logprob_buffer[step] = logprob.numpy()
                value_buffer[step] = value.numpy()
                _, _, rewards, info = env.step(actions.astype(np.int32))
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
                    identity_error = float(
                        abs(100.0 * slot_returns[slot] - terminal["margin"])
                    )
                    if identity_error >= 1.0e-4:
                        raise RuntimeError(f"D73 reward identity failure: {identity_error}")
                    episode = {**terminal, "reward_identity_error": identity_error}
                    update_digest(terminal_digest, episode)
                    update_episodes.append(episode)
                    all_episodes.append(episode)
                    slot_returns[slot] = 0.0
                next_hidden = next_hidden * torch.from_numpy(1.0 - done).unsqueeze(-1)
                hidden = next_hidden

            if update == 1:
                if len(probe_features) != FROZEN["probe_rows"]:
                    raise RuntimeError("D73 first rollout lacks 512 distinct unlocked probes")
                with torch.inference_mode():
                    initial_probe_actions = model.action_and_value(
                        torch.from_numpy(np.stack(probe_features)),
                        torch.from_numpy(np.stack(probe_masks)),
                        torch.from_numpy(np.stack(probe_hidden)),
                        deterministic=True,
                    )[0].numpy()

            with torch.inference_mode():
                next_value = model.critic(torch.from_numpy(env.features)).squeeze(-1).numpy()
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
            epoch_count = 0
            update_metrics: dict[str, list[float]] = collections.defaultdict(list)
            for epoch in range(FROZEN["update_epochs"]):
                rng.shuffle(sequence_indices)
                epoch_kls = []
                for start in range(0, FROZEN["num_envs"], FROZEN["minibatch_sequences"]):
                    indexes = sequence_indices[
                        start : start + FROZEN["minibatch_sequences"]
                    ]
                    new_logprob, entropy, new_value = model.sequence_statistics(
                        torch.from_numpy(feature_buffer[:, indexes]),
                        torch.from_numpy(mask_buffer[:, indexes]),
                        torch.from_numpy(action_buffer[:, indexes]),
                        torch.from_numpy(done_buffer[:, indexes]),
                        torch.from_numpy(rollout_initial_hidden[indexes]),
                    )
                    old_logprob = torch.from_numpy(logprob_buffer[:, indexes])
                    log_ratio = new_logprob - old_logprob
                    ratio = log_ratio.exp()
                    advantage = torch.from_numpy(normalized[:, indexes])
                    unclipped = -advantage * ratio
                    clipped = -advantage * ratio.clamp(
                        1.0 - FROZEN["clip_coef"], 1.0 + FROZEN["clip_coef"]
                    )
                    policy_loss = torch.maximum(unclipped, clipped).mean()
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
                        raise RuntimeError("non-finite D73 PPO loss")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    gradient_norm = nn.utils.clip_grad_norm_(
                        model.parameters(), FROZEN["max_grad_norm"]
                    )
                    if not torch.isfinite(gradient_norm):
                        raise RuntimeError("non-finite D73 gradient")
                    optimizer.step()
                    with torch.no_grad():
                        approx_kl = ((ratio - 1.0) - log_ratio).mean()
                        clip_fraction = (
                            (ratio - 1.0).abs() > FROZEN["clip_coef"]
                        ).float().mean()
                    values = {
                        "policy_loss": float(policy_loss.detach()),
                        "value_loss": float(value_loss.detach()),
                        "entropy": float(entropy_mean.detach()),
                        "approx_kl": float(approx_kl),
                        "clip_fraction": float(clip_fraction),
                        "gradient_norm": float(gradient_norm),
                    }
                    for name, value in values.items():
                        update_metrics[name].append(value)
                        losses[name].append(value)
                    epoch_kls.append(float(approx_kl))
                epoch_count = epoch + 1
                if epoch_kls and float(np.mean(epoch_kls)) > FROZEN["target_kl"]:
                    break
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                parameter_nonfinite_events += 1
                raise RuntimeError("non-finite D73 model parameter")
            update_log = {
                "update": update,
                "global_step": global_step,
                "unlocked_action_counts": update_actions.tolist(),
                "episodes": summarize_episodes(update_episodes),
                **{
                    name: float(np.mean(values))
                    for name, values in update_metrics.items()
                },
                "epochs_run": epoch_count,
                "update_seconds": time.perf_counter() - update_started,
            }
            logs.append(update_log)
            if update == 1 or update % 4 == 0 or update == updates:
                print(json.dumps({"event": "update", **update_log}, sort_keys=True), flush=True)

    wall_seconds = time.perf_counter() - started_wall
    cpu_seconds = time.process_time() - started_cpu
    if initial_probe_actions is None:
        raise RuntimeError("D73 initial probe missing")
    with torch.inference_mode():
        final_probe_actions = model.action_and_value(
            torch.from_numpy(np.stack(probe_features)),
            torch.from_numpy(np.stack(probe_masks)),
            torch.from_numpy(np.stack(probe_hidden)),
            deterministic=True,
        )[0].numpy()
    final_actor = torch.cat(
        [parameter.detach().flatten() for parameter in model.actor_parameters()]
    )
    probe = {
        "rows": len(probe_features),
        "initial_action_counts": np.bincount(
            initial_probe_actions, minlength=OPENING_RECURRENT_ACTIONS
        ).tolist(),
        "final_action_counts": np.bincount(
            final_probe_actions, minlength=OPENING_RECURRENT_ACTIONS
        ).tolist(),
        "changed_actions": int(np.count_nonzero(initial_probe_actions != final_probe_actions)),
        "final_distinct_modes": int(len(set(final_probe_actions.tolist()))),
        "actor_l2_drift": float(torch.linalg.vector_norm(final_actor - initial_actor)),
    }
    episode_summary = summarize_episodes(all_episodes)
    training = {
        "global_step": global_step,
        "updates": len(logs),
        "unlocked_transitions": unlocked_transitions,
        "unlocked_action_counts": unlocked_action_counts.tolist(),
        "unlocked_action_rates": (unlocked_action_counts / unlocked_transitions).tolist(),
        "illegal_actions": illegal_actions,
        "parameter_nonfinite_events": parameter_nonfinite_events,
        "episodes": episode_summary,
        "terminal_stream_sha256": terminal_digest.hexdigest(),
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "effective_cpu_cores": cpu_seconds / wall_seconds,
        "transitions_per_second": global_step / wall_seconds,
        "losses": {
            name: {
                "mean": float(np.mean(values)),
                "maximum": float(np.max(values)),
                "finite": finite_list(values),
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
    prerequisite_hashes = {}
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"D73 prerequisite hash mismatch: {path}: {actual}")
        prerequisite_hashes[str(path)] = actual
    parity = json.loads(PARITY.read_text())
    if not parity.get("pass") or parity.get("comparisons") != 64:
        raise SystemExit("D73 opening-recurrent parity is not valid")

    os.environ["RAYON_NUM_THREADS"] = str(FROZEN["threads"])
    torch.set_num_threads(FROZEN["threads"])
    torch.set_num_interop_threads(4)
    model, initial_state, training, probe = train()
    torch.save(
        {
            "model": model.state_dict(),
            "config": FROZEN,
            "features": OPENING_RECURRENT_FEATURES,
            "hidden": HIDDEN,
            "modes": OPENING_RECURRENT_MODES,
            "actor_parameters": ACTOR_PARAMETERS,
            "critic_parameters": CRITIC_PARAMETERS,
        },
        CHECKPOINT,
    )
    checkpoints = sorted(ANALYSIS.glob("d73a-four-mode-recurrent-ppo*.pt"))

    initial_model = RecurrentActorCritic()
    initial_model.load_state_dict(initial_state)
    rows_a = [
        *evaluate_policy("balanced", None),
        *evaluate_policy("initial", initial_model),
        *evaluate_policy("final", model),
    ]
    rows_b = [
        *evaluate_policy("balanced", None),
        *evaluate_policy("initial", initial_model),
        *evaluate_policy("final", model),
    ]
    write_evaluation(EVALUATION_A, rows_a)
    write_evaluation(EVALUATION_B, rows_b)
    repeat_exact = EVALUATION_A.read_bytes() == EVALUATION_B.read_bytes()

    summaries = {
        policy: evaluation_summary(rows_a, policy)
        for policy in ("balanced", "initial", "final")
    }
    versus_balanced = paired_comparison(rows_a, "final", "balanced")
    versus_initial = paired_comparison(rows_a, "final", "initial")
    training_failures = training["episodes"]["mechanical_failures"]
    final_summary = summaries["final"]
    final_failures = final_summary["mechanical_failures"]
    action_rates = training["unlocked_action_rates"]
    mechanics_gates = {
        "exact_budget_and_updates": (
            training["global_step"] == FROZEN["total_transitions"]
            and training["updates"] == 32
        ),
        "final_only_checkpoint": checkpoints == [CHECKPOINT],
        "parity_pass": bool(parity["pass"]),
        "finite_losses_and_parameters": (
            all(row["finite"] for row in training["losses"].values())
            and training["parameter_nonfinite_events"] == 0
        ),
        "zero_illegal_actions": training["illegal_actions"] == 0,
        "at_least_1500_episodes": training["episodes"]["episodes"] >= 1_500,
        "training_reward_identity_below_1e4": (
            training["episodes"]["maximum_reward_identity_error"] < 1.0e-4
        ),
        "training_zero_mechanical_failures": all(
            value == 0 for value in training_failures.values()
        ),
        "all_actions_at_least_2pct_unlocked": min(action_rates) >= 0.02,
        "evaluation_complete": all(summary["tasks"] == 256 for summary in summaries.values()),
        "evaluation_repeat_byte_exact": repeat_exact,
        "evaluation_reward_identity_below_1e4": (
            max(summary["maximum_reward_identity_error"] for summary in summaries.values())
            < 1.0e-4
        ),
        "evaluation_zero_mechanical_failures": all(
            value == 0 for value in final_failures.values()
        ),
        "throughput_at_least_400": training["transitions_per_second"] >= 400,
        "effective_cpu_at_least_12": training["effective_cpu_cores"] >= 12,
    }
    signal_gates = {
        "probe_at_least_64_actions_change": probe["changed_actions"] >= 64,
        "probe_at_least_three_final_modes": probe["final_distinct_modes"] >= 3,
        "actor_l2_drift_at_least_010": probe["actor_l2_drift"] >= 0.10,
        "final_uses_at_least_three_modes": final_summary["used_unlocked_modes"] >= 3,
        "final_nonbalanced_at_least_25pct_unlocked": (
            final_summary["unlocked_nonbalanced_rate"] >= 0.25
        ),
    }
    safety_gates = {
        "final_crop_exactly_256": final_summary["crop_tasks"] == 256,
        "final_worker_three_at_least_90pct": final_summary["worker_three_rate"] >= 0.90,
    }
    value_gates = {
        "mean_margin_at_least_5_above_balanced": versus_balanced["mean_margin_delta"] >= 5,
        "mean_margin_at_least_5_above_initial": versus_initial["mean_margin_delta"] >= 5,
        "strict_improvement_at_least_45pct": (
            versus_balanced["strict_improvement_rate"] >= 0.45
        ),
        "every_opponent_at_least_minus5": all(
            value >= -5 for value in versus_balanced["opponent_mean_margin_delta"].values()
        ),
        "at_least_six_positive_opponents": versus_balanced["positive_opponent_families"] >= 6,
        "own_nonnegative_or_opponent_nonpositive": (
            versus_balanced["mean_own_score_delta"] >= 0
            or versus_balanced["mean_opponent_score_delta"] <= 0
        ),
    }
    mechanics_pass = all(mechanics_gates.values())
    signal_pass = all(signal_gates.values())
    safety_pass = all(safety_gates.values())
    value_pass = all(value_gates.values())
    full_pass = mechanics_pass and signal_pass and safety_pass and value_pass
    if not mechanics_pass:
        status = "mechanics_integrity_failure"
        next_experiment = "repair_only_then_repeat_unchanged"
    elif not signal_pass:
        status = "optimization_signal_failure"
        next_experiment = "paired_online_option_values"
    elif not safety_pass or not value_pass:
        status = "fixed_policy_value_or_safety_failure"
        next_experiment = "paired_online_option_values"
    else:
        status = "full_pass"
        next_experiment = "longer_recurrent_ppo_with_separate_held_map_qualification"

    report = {
        "schema": "troll-farm-d73a-four-mode-recurrent-ppo-signal-v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "scope": "short recurrent PPO signal and prospective fixed-policy value preflight",
        "inputs": {
            "prerequisite_hashes": prerequisite_hashes,
            "trainer": sha256(Path(__file__)),
            "checkpoint": sha256(CHECKPOINT),
            "evaluation_a": sha256(EVALUATION_A),
            "evaluation_b": sha256(EVALUATION_B),
        },
        "config": FROZEN,
        "model": {
            "features": OPENING_RECURRENT_FEATURES,
            "actions": OPENING_RECURRENT_ACTIONS,
            "hidden": HIDDEN,
            "actor_parameters": ACTOR_PARAMETERS,
            "critic_parameters": CRITIC_PARAMETERS,
        },
        "training": training,
        "probe": probe,
        "evaluation": {
            "repeat_byte_exact": repeat_exact,
            "summaries": summaries,
            "final_versus_balanced": versus_balanced,
            "final_versus_initial": versus_initial,
        },
        "gates": {
            "mechanics": mechanics_gates,
            "signal": signal_gates,
            "safety": safety_gates,
            "value": value_gates,
            "mechanics_pass": mechanics_pass,
            "signal_pass": signal_pass,
            "safety_pass": safety_pass,
            "value_pass": value_pass,
            "full_pass": full_pass,
        },
        "decision": {
            "status": status,
            "next_experiment": next_experiment,
            "checkpoint_is_candidate": False,
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }
    atomic_write_new(OUTPUT, report)
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "gates": report["gates"],
                "probe": probe,
                "evaluation": report["evaluation"],
                "decision": report["decision"],
            },
            indent=2,
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
