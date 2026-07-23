#!/usr/bin/env python3
"""Run the frozen D62a batch-option PPO mechanical preflight."""

from __future__ import annotations

import collections
import hashlib
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions.categorical import Categorical
from torch.nn import functional as F

from cgauto.rl_batch_option_env import (
    BATCH_OPTION_ACTIONS,
    BATCH_OPTION_FEATURES,
    BATCH_OPTION_MODES,
    DEFAULT_LIBRARY,
    BatchOptionVecEnv,
)
from cgauto.train_d41c_residual_ppo import compute_advantages, layer_init


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d62a-batch-option-ppo-mechanical-preflight-protocol-2026-07-21.md"
AMENDMENT = ANALYSIS / "d62a-balanced-reference-amendment-2026-07-21.md"
PARITY = ANALYSIS / "d62a-batch-option-environment-parity.json"
PARITY_VALIDATOR = ROOT / "cgauto" / "validate_d62a_batch_option_env.py"
WRAPPER = ROOT / "cgauto" / "rl_batch_option_env.py"
RUST_ENV = ROOT / "rust" / "src" / "rl_batch_option.rs"
RUST_LIB = ROOT / "rust" / "src" / "lib.rs"
OUTPUT = ANALYSIS / "d62a-batch-option-ppo-mechanical-preflight-result.json"
CHECKPOINT = ANALYSIS / "d62a-batch-option-ppo-mechanical-preflight-final.pt"

EXPECTED_HASHES = {
    PROTOCOL: "e59c5eb06d8a8742de6017226c7ed79378b17bc7db512f6e70f021d04992d4cb",
    AMENDMENT: "ff34a05920e25b4777bbc11424affb61607b00b93815ae93051113e6a311a41d",
    PARITY: "dd44181094a534a17feb2352a6ffa315110046ea34cf192db20f0eb5344e7c56",
    PARITY_VALIDATOR: "e7abedeb0ca17513b9764c031627344c45dd2893dfd1aaf1942b668efe82e660",
    WRAPPER: "f5248c0daa14456431092b7c6b0c2f620c2dffd3909f65e28d75538deddb4018",
    RUST_ENV: "dc476cdccd5076a9f6837190a60e53941db59ce80e94fc528df98b30d3e3dde3",
    RUST_LIB: "fe995766f3712ee468ef4ff45f6dfd1c8cf5cc94732302e3ccb2114728d3f64f",
    Path(DEFAULT_LIBRARY): "0b2dbc8d23f67f975e584f9b7f6e69f91dc13397dca8a24fe54aa262e760b0f7",
}

INITIAL_PROBABILITIES = np.asarray([0.85, 0.05, 0.05, 0.05], dtype=np.float32)
FROZEN = {
    "model_seed": 6_201,
    "train_seed_base": 9_802_000,
    "num_envs": 64,
    "rollout_steps": 64,
    "total_transitions": 131_072,
    "update_epochs": 4,
    "minibatch_size": 1_024,
    "learning_rate": 2.5e-4,
    "adam_epsilon": 1e-5,
    "gamma": 1.0,
    "gae_lambda": 0.95,
    "clip_coef": 0.15,
    "entropy_coef": 0.005,
    "value_coef": 0.5,
    "max_grad_norm": 0.5,
    "target_kl": 0.02,
    "threads": 20,
    "probe_rows": 512,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class BatchOptionActorCritic(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.actor_hidden = layer_init(nn.Linear(BATCH_OPTION_FEATURES, 16))
        self.actor_output = nn.Linear(16, BATCH_OPTION_ACTIONS)
        nn.init.zeros_(self.actor_output.weight)
        with torch.no_grad():
            self.actor_output.bias.copy_(torch.log(torch.from_numpy(INITIAL_PROBABILITIES)))
        self.critic = nn.Sequential(
            layer_init(nn.Linear(BATCH_OPTION_FEATURES, 64)),
            nn.ReLU(),
            layer_init(nn.Linear(64, 32)),
            nn.ReLU(),
            layer_init(nn.Linear(32, 1), std=1.0),
        )

    def actor_parameters(self) -> list[nn.Parameter]:
        return list(self.actor_hidden.parameters()) + list(self.actor_output.parameters())

    def actor_logits(self, features: torch.Tensor) -> torch.Tensor:
        return self.actor_output(F.relu(self.actor_hidden(features.float())))

    def action_and_value(
        self,
        features: torch.Tensor,
        masks: torch.Tensor,
        action: torch.Tensor | None = None,
        *,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        logits = self.actor_logits(features)
        legal = masks.bool()
        masked_logits = logits.masked_fill(~legal, -1.0e30)
        distribution = Categorical(logits=masked_logits)
        if action is None:
            action = masked_logits.argmax(dim=1) if deterministic else distribution.sample()
        value = self.critic(features.float()).squeeze(-1)
        return (
            action.long(),
            distribution.log_prob(action.long()),
            distribution.entropy(),
            value,
            masked_logits,
        )

    @torch.inference_mode()
    def probabilities(self, features: np.ndarray, masks: np.ndarray) -> np.ndarray:
        logits = self.actor_logits(torch.from_numpy(features))
        legal = torch.from_numpy(masks).bool()
        return torch.softmax(logits.masked_fill(~legal, -1.0e30), dim=1).numpy()


def actor_parameter_count(model: BatchOptionActorCritic) -> int:
    return sum(parameter.numel() for parameter in model.actor_parameters())


def critic_parameter_count(model: BatchOptionActorCritic) -> int:
    return sum(parameter.numel() for parameter in model.critic.parameters())


def finite_list(values: list[float]) -> bool:
    return bool(values) and bool(np.isfinite(np.asarray(values)).all())


def summarize_episodes(rows: list[dict]) -> dict:
    if not rows:
        return {"episodes": 0}
    opponents = collections.Counter(row["opponent"] for row in rows)
    return {
        "episodes": len(rows),
        "mean_margin": float(np.mean([row["margin"] for row in rows])),
        "mean_own_score": float(np.mean([row["own_score"] for row in rows])),
        "mean_opponent_score": float(np.mean([row["opponent_score"] for row in rows])),
        "worker_two_rate": float(np.mean([row["own_workers"] >= 2 for row in rows])),
        "worker_three_rate": float(np.mean([row["own_workers"] >= 3 for row in rows])),
        "crop_rate": float(np.mean([row["own_created_crops"] > 0 for row in rows])),
        "minimum_created_crops": int(min(row["own_created_crops"] for row in rows)),
        "maximum_workers": int(max(row["own_workers"] for row in rows)),
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
        "opponents": dict(sorted(opponents.items())),
    }


def update_terminal_digest(digest: hashlib._Hash, terminal: dict) -> None:
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
        "invalid_direct_commands",
        "provenance_failures",
        "deposit_prediction_failures",
        "invalidated_jobs",
        "action_hash",
        "state_hash",
    )
    payload = [terminal[field] for field in fields]
    digest.update(json.dumps(payload, separators=(",", ":")).encode())
    digest.update(b"\n")


def main() -> None:
    if OUTPUT.exists() or CHECKPOINT.exists():
        raise SystemExit("refusing to overwrite D62a preflight artifacts")
    prerequisite_hashes = {}
    for path, expected in EXPECTED_HASHES.items():
        if not path.exists():
            raise SystemExit(f"missing D62a prerequisite: {path}")
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"D62a prerequisite hash mismatch: {path}")
        prerequisite_hashes[str(path)] = actual
    parity = json.loads(PARITY.read_text())
    if not parity.get("pass") or parity.get("mode_task_comparisons") != 64:
        raise SystemExit("D62a frozen environment parity did not pass")

    batch_size = FROZEN["num_envs"] * FROZEN["rollout_steps"]
    updates = FROZEN["total_transitions"] // batch_size
    if batch_size != 4_096 or updates != 32 or FROZEN["total_transitions"] % batch_size:
        raise SystemExit("D62a frozen transition geometry mismatch")

    os.environ["RAYON_NUM_THREADS"] = str(FROZEN["threads"])
    torch.manual_seed(FROZEN["model_seed"])
    np.random.seed(FROZEN["model_seed"])
    torch.set_num_threads(FROZEN["threads"])
    torch.set_num_interop_threads(4)
    model = BatchOptionActorCritic()
    if actor_parameter_count(model) != 980 or critic_parameter_count(model) != 5_761:
        raise SystemExit("D62a model parameter count drift")
    optimizer = torch.optim.Adam(
        model.parameters(), lr=FROZEN["learning_rate"], eps=FROZEN["adam_epsilon"]
    )
    rng = np.random.default_rng(FROZEN["model_seed"])
    initial_actor = torch.cat(
        [parameter.detach().flatten().clone() for parameter in model.actor_parameters()]
    )

    shape = (FROZEN["rollout_steps"], FROZEN["num_envs"])
    feature_buffer = np.empty((*shape, BATCH_OPTION_FEATURES), dtype=np.float32)
    mask_buffer = np.empty((*shape, BATCH_OPTION_ACTIONS), dtype=np.uint8)
    action_buffer = np.empty(shape, dtype=np.int64)
    logprob_buffer = np.empty(shape, dtype=np.float32)
    reward_buffer = np.empty(shape, dtype=np.float32)
    done_buffer = np.empty(shape, dtype=np.float32)
    value_buffer = np.empty(shape, dtype=np.float32)

    global_step = unlocked_transitions = sampled_nonbalanced = illegal_actions = 0
    all_episodes: list[dict] = []
    terminal_digest = hashlib.sha256()
    probe_rows: list[np.ndarray] = []
    probe_seen: set[bytes] = set()
    initial_probe_probabilities: np.ndarray | None = None
    logs = []
    all_policy_losses: list[float] = []
    all_value_losses: list[float] = []
    all_entropies: list[float] = []
    all_kls: list[float] = []
    all_clip_fractions: list[float] = []
    all_gradient_norms: list[float] = []
    parameter_nonfinite_events = 0
    training_started_wall = time.perf_counter()
    training_started_cpu = time.process_time()

    with BatchOptionVecEnv(FROZEN["num_envs"], FROZEN["train_seed_base"]) as env:
        initial_actions, *_ = model.action_and_value(
            torch.from_numpy(env.features),
            torch.from_numpy(env.masks),
            deterministic=True,
        )
        if np.any(initial_actions.numpy() != 0):
            raise RuntimeError("D62a deterministic initialization is not balanced")
        unlocked_initial = env.masks.sum(axis=1) == BATCH_OPTION_ACTIONS
        if np.any(unlocked_initial):
            initial_probabilities = model.probabilities(
                env.features[unlocked_initial], env.masks[unlocked_initial]
            )
            if not np.allclose(
                initial_probabilities,
                INITIAL_PROBABILITIES[None, :],
                rtol=0.0,
                atol=1.0e-6,
            ):
                raise RuntimeError("D62a initial unlocked probability drift")

        slot_returns = np.zeros(FROZEN["num_envs"], dtype=np.float64)
        for update in range(1, updates + 1):
            update_started = time.perf_counter()
            update_unlocked = update_nonbalanced = 0
            update_episodes = []
            for step in range(FROZEN["rollout_steps"]):
                features = env.features
                masks = env.masks
                feature_buffer[step] = features
                mask_buffer[step] = masks
                unlocked = masks.sum(axis=1) == BATCH_OPTION_ACTIONS
                if update == 1 and len(probe_rows) < FROZEN["probe_rows"]:
                    for row in features[unlocked]:
                        key = row.tobytes()
                        if key in probe_seen:
                            continue
                        probe_seen.add(key)
                        probe_rows.append(row.copy())
                        if len(probe_rows) == FROZEN["probe_rows"]:
                            break

                with torch.inference_mode():
                    action, logprob, _, value, _ = model.action_and_value(
                        torch.from_numpy(features), torch.from_numpy(masks)
                    )
                actions = action.numpy().astype(np.int64)
                rows = np.arange(FROZEN["num_envs"])
                illegal = masks[rows, actions] != 1
                illegal_actions += int(np.count_nonzero(illegal))
                if np.any(illegal):
                    raise RuntimeError("D62a sampled an illegal batch option")
                current_unlocked = int(np.count_nonzero(unlocked))
                current_nonbalanced = int(np.count_nonzero(actions))
                unlocked_transitions += current_unlocked
                sampled_nonbalanced += current_nonbalanced
                update_unlocked += current_unlocked
                update_nonbalanced += current_nonbalanced
                action_buffer[step] = actions
                logprob_buffer[step] = logprob.numpy()
                value_buffer[step] = value.numpy()

                _, _, rewards, info = env.step(actions.astype(np.int32))
                reward_buffer[step] = rewards
                done_buffer[step] = np.asarray(
                    [terminal is not None for terminal in info.terminals], dtype=np.float32
                )
                slot_returns += rewards.astype(np.float64)
                global_step += FROZEN["num_envs"]
                for slot, terminal in enumerate(info.terminals):
                    if terminal is None:
                        continue
                    identity_error = abs(
                        100.0 * slot_returns[slot] - float(terminal["margin"])
                    )
                    if identity_error > 1.0e-4:
                        raise RuntimeError(
                            f"D62a reward identity failure: {identity_error}"
                        )
                    episode = {**terminal, "reward_identity_error": identity_error}
                    update_terminal_digest(terminal_digest, episode)
                    update_episodes.append(episode)
                    all_episodes.append(episode)
                    slot_returns[slot] = 0.0

            if update == 1:
                if len(probe_rows) != FROZEN["probe_rows"]:
                    raise RuntimeError(
                        "D62a first rollout did not contain 512 distinct unlocked states"
                    )
                probe = np.stack(probe_rows)
                probe_masks = np.ones(
                    (FROZEN["probe_rows"], BATCH_OPTION_ACTIONS), dtype=np.uint8
                )
                initial_probe_probabilities = model.probabilities(probe, probe_masks)
                if not np.allclose(
                    initial_probe_probabilities,
                    INITIAL_PROBABILITIES[None, :],
                    rtol=0.0,
                    atol=1.0e-6,
                ):
                    raise RuntimeError("D62a frozen probe was not captured before optimization")

            with torch.inference_mode():
                _, _, _, next_value, _ = model.action_and_value(
                    torch.from_numpy(env.features), torch.from_numpy(env.masks)
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
                advantages.std() + 1.0e-8
            )

            flat_features = feature_buffer.reshape(batch_size, BATCH_OPTION_FEATURES)
            flat_masks = mask_buffer.reshape(batch_size, BATCH_OPTION_ACTIONS)
            flat_actions = action_buffer.reshape(batch_size)
            flat_logprobs = logprob_buffer.reshape(batch_size)
            flat_advantages = normalized_advantages.reshape(batch_size)
            flat_returns = returns.reshape(batch_size)
            indexes = np.arange(batch_size)
            policy_losses = []
            value_losses = []
            entropies = []
            approx_kls = []
            clip_fractions = []
            gradient_norms = []
            epochs_run = 0
            for epoch in range(FROZEN["update_epochs"]):
                rng.shuffle(indexes)
                epoch_kls = []
                for start in range(0, batch_size, FROZEN["minibatch_size"]):
                    minibatch = indexes[start : start + FROZEN["minibatch_size"]]
                    _, new_logprob, entropy, new_value, _ = model.action_and_value(
                        torch.from_numpy(flat_features[minibatch]),
                        torch.from_numpy(flat_masks[minibatch]),
                        action=torch.from_numpy(flat_actions[minibatch]),
                    )
                    old_logprob = torch.from_numpy(flat_logprobs[minibatch])
                    log_ratio = new_logprob - old_logprob
                    ratio = log_ratio.exp()
                    advantage = torch.from_numpy(flat_advantages[minibatch])
                    unclipped = -advantage * ratio
                    clipped = -advantage * ratio.clamp(
                        1.0 - FROZEN["clip_coef"], 1.0 + FROZEN["clip_coef"]
                    )
                    policy_loss = torch.maximum(unclipped, clipped).mean()
                    entropy_loss = entropy.mean()
                    value_loss = 0.5 * F.mse_loss(
                        new_value, torch.from_numpy(flat_returns[minibatch])
                    )
                    loss = (
                        policy_loss
                        + FROZEN["value_coef"] * value_loss
                        - FROZEN["entropy_coef"] * entropy_loss
                    )
                    if not torch.isfinite(loss):
                        raise RuntimeError("non-finite D62a PPO loss")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    gradient_norm = nn.utils.clip_grad_norm_(
                        model.parameters(), FROZEN["max_grad_norm"]
                    )
                    if not torch.isfinite(gradient_norm):
                        raise RuntimeError("non-finite D62a gradient norm")
                    optimizer.step()
                    with torch.no_grad():
                        approx_kl = ((ratio - 1.0) - log_ratio).mean()
                        clip_fraction = (
                            (ratio - 1.0).abs() > FROZEN["clip_coef"]
                        ).float().mean()
                    policy_losses.append(float(policy_loss.detach()))
                    value_losses.append(float(value_loss.detach()))
                    entropies.append(float(entropy_loss.detach()))
                    approx_kls.append(float(approx_kl))
                    epoch_kls.append(float(approx_kl))
                    clip_fractions.append(float(clip_fraction))
                    gradient_norms.append(float(gradient_norm))
                epochs_run = epoch + 1
                if epoch_kls and float(np.mean(epoch_kls)) > FROZEN["target_kl"]:
                    break
            if not all(torch.isfinite(parameter).all() for parameter in model.parameters()):
                parameter_nonfinite_events += 1
                raise RuntimeError("non-finite D62a model parameter")
            all_policy_losses.extend(policy_losses)
            all_value_losses.extend(value_losses)
            all_entropies.extend(entropies)
            all_kls.extend(approx_kls)
            all_clip_fractions.extend(clip_fractions)
            all_gradient_norms.extend(gradient_norms)
            update_log = {
                "update": update,
                "global_step": global_step,
                "unlocked_transitions": update_unlocked,
                "sampled_nonbalanced": update_nonbalanced,
                "nonbalanced_transition_rate": update_nonbalanced / batch_size,
                "nonbalanced_unlocked_rate": (
                    update_nonbalanced / update_unlocked if update_unlocked else 0.0
                ),
                "episodes": summarize_episodes(update_episodes),
                "policy_loss": float(np.mean(policy_losses)),
                "value_loss": float(np.mean(value_losses)),
                "entropy": float(np.mean(entropies)),
                "approx_kl": float(np.mean(approx_kls)),
                "maximum_approx_kl": float(np.max(approx_kls)),
                "clip_fraction": float(np.mean(clip_fractions)),
                "gradient_norm": float(np.mean(gradient_norms)),
                "epochs_run": epochs_run,
                "update_seconds": time.perf_counter() - update_started,
            }
            logs.append(update_log)
            if update == 1 or update % 4 == 0 or update == updates:
                print(json.dumps({"event": "update", **update_log}, sort_keys=True), flush=True)

    wall_seconds = time.perf_counter() - training_started_wall
    cpu_seconds = time.process_time() - training_started_cpu
    if initial_probe_probabilities is None:
        raise RuntimeError("D62a probe initialization was not captured")
    probe = np.stack(probe_rows)
    probe_masks = np.ones((FROZEN["probe_rows"], BATCH_OPTION_ACTIONS), dtype=np.uint8)
    final_probe_probabilities = model.probabilities(probe, probe_masks)
    initial_nonbalanced = initial_probe_probabilities[:, 1:].sum(axis=1)
    final_nonbalanced = final_probe_probabilities[:, 1:].sum(axis=1)
    final_deterministic = final_probe_probabilities.argmax(axis=1)
    deterministic_nonbalanced = int(np.count_nonzero(final_deterministic))
    distinct_nonbalanced_modes = sorted(
        {
            BATCH_OPTION_MODES[int(mode)]
            for mode in final_deterministic
            if int(mode) != 0
        }
    )
    mean_nonbalanced_change = float(
        final_nonbalanced.mean() - initial_nonbalanced.mean()
    )
    final_nonbalanced_std = float(final_nonbalanced.std())
    final_actor = torch.cat(
        [parameter.detach().flatten() for parameter in model.actor_parameters()]
    )
    actor_drift = float(torch.linalg.vector_norm(final_actor - initial_actor))
    episode_summary = summarize_episodes(all_episodes)
    mechanical_failures = episode_summary["mechanical_failures"]
    unlocked_rate = unlocked_transitions / global_step
    nonbalanced_rate = sampled_nonbalanced / global_step
    throughput = global_step / wall_seconds
    effective_cores = cpu_seconds / wall_seconds
    losses_finite = all(
        finite_list(values)
        for values in (
            all_policy_losses,
            all_value_losses,
            all_entropies,
            all_kls,
            all_clip_fractions,
            all_gradient_norms,
        )
    )

    torch.save(
        {
            "model": model.state_dict(),
            "config": FROZEN,
            "feature_count": BATCH_OPTION_FEATURES,
            "modes": BATCH_OPTION_MODES,
            "actor_parameters": actor_parameter_count(model),
            "critic_parameters": critic_parameter_count(model),
        },
        CHECKPOINT,
    )
    checkpoint_files = sorted(ANALYSIS.glob("d62a-batch-option-ppo*.pt"))
    gates = {
        "exact_transition_and_update_budget": global_step == FROZEN["total_transitions"]
        and len(logs) == updates,
        "final_only_checkpoint": checkpoint_files == [CHECKPOINT],
        "constant_policy_d61_parity": bool(parity["pass"]),
        "unlocked_transition_rate_at_least_20pct": unlocked_rate >= 0.20,
        "sampled_nonbalanced_rate_at_least_5pct": nonbalanced_rate >= 0.05,
        "zero_illegal_actions": illegal_actions == 0,
        "finite_losses_gradients_and_parameters": losses_finite
        and parameter_nonfinite_events == 0,
        "at_least_1500_episodes": len(all_episodes) >= 1_500,
        "reward_identity_below_1e4": episode_summary["maximum_reward_identity_error"]
        < 1.0e-4,
        "actor_l2_drift_at_least_005": actor_drift >= 0.05,
        "all_episodes_create_crop": episode_summary["crop_rate"] == 1.0,
        "worker_three_rate_at_least_85pct": episode_summary["worker_three_rate"]
        >= 0.85,
        "zero_mechanical_failures": all(value == 0 for value in mechanical_failures.values()),
        "probe_mean_nonbalanced_changes_at_least_002": abs(mean_nonbalanced_change)
        >= 0.02,
        "probe_nonbalanced_std_at_least_001": final_nonbalanced_std >= 0.01,
        "probe_at_least_16_deterministic_nonbalanced": deterministic_nonbalanced >= 16,
        "probe_at_least_two_distinct_nonbalanced_modes": len(distinct_nonbalanced_modes)
        >= 2,
        "throughput_at_least_400": throughput >= 400.0,
        "effective_cpu_at_least_12": effective_cores >= 12.0,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    report = {
        "protocol": str(PROTOCOL),
        "amendment": str(AMENDMENT),
        "trainer": str(Path(__file__).resolve()),
        "trainer_sha256": sha256(Path(__file__).resolve()),
        "prerequisite_hashes": prerequisite_hashes,
        "config": FROZEN,
        "actor_parameters": actor_parameter_count(model),
        "critic_parameters": critic_parameter_count(model),
        "checkpoint": str(CHECKPOINT),
        "checkpoint_sha256": sha256(CHECKPOINT),
        "training": {
            "global_step": global_step,
            "updates": len(logs),
            "unlocked_transitions": unlocked_transitions,
            "unlocked_transition_rate": unlocked_rate,
            "sampled_nonbalanced": sampled_nonbalanced,
            "sampled_nonbalanced_transition_rate": nonbalanced_rate,
            "sampled_nonbalanced_unlocked_rate": (
                sampled_nonbalanced / unlocked_transitions
                if unlocked_transitions
                else 0.0
            ),
            "illegal_actions": illegal_actions,
            "parameter_nonfinite_events": parameter_nonfinite_events,
            "actor_l2_drift": actor_drift,
            "episodes": episode_summary,
            "terminal_stream_sha256": terminal_digest.hexdigest(),
            "wall_seconds": wall_seconds,
            "cpu_seconds": cpu_seconds,
            "effective_cpu_cores": effective_cores,
            "transitions_per_second": throughput,
            "losses": {
                "policy_mean": float(np.mean(all_policy_losses)),
                "value_mean": float(np.mean(all_value_losses)),
                "entropy_mean": float(np.mean(all_entropies)),
                "approx_kl_mean": float(np.mean(all_kls)),
                "approx_kl_maximum": float(np.max(all_kls)),
                "clip_fraction_mean": float(np.mean(all_clip_fractions)),
                "gradient_norm_mean": float(np.mean(all_gradient_norms)),
                "gradient_norm_maximum": float(np.max(all_gradient_norms)),
            },
            "logs": logs,
        },
        "probe": {
            "rows": len(probe),
            "initial_mean_probabilities": initial_probe_probabilities.mean(axis=0).tolist(),
            "final_mean_probabilities": final_probe_probabilities.mean(axis=0).tolist(),
            "initial_mean_nonbalanced_probability": float(initial_nonbalanced.mean()),
            "final_mean_nonbalanced_probability": float(final_nonbalanced.mean()),
            "mean_nonbalanced_probability_change": mean_nonbalanced_change,
            "final_nonbalanced_probability_std": final_nonbalanced_std,
            "final_nonbalanced_probability_minimum": float(final_nonbalanced.min()),
            "final_nonbalanced_probability_maximum": float(final_nonbalanced.max()),
            "deterministic_action_counts": {
                mode: int(np.count_nonzero(final_deterministic == index))
                for index, mode in enumerate(BATCH_OPTION_MODES)
            },
            "deterministic_nonbalanced": deterministic_nonbalanced,
            "distinct_nonbalanced_modes": distinct_nonbalanced_modes,
        },
        "gates": gates,
        "pass": all(gates.values()),
        "scope": "D62a mechanical learning-signal preflight only; no value selection, candidate, or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "event": "result",
                "output": str(OUTPUT),
                "checkpoint": str(CHECKPOINT),
                "pass": report["pass"],
                "gates": gates,
                "training": {
                    key: value
                    for key, value in report["training"].items()
                    if key not in {"logs", "losses"}
                },
                "probe": report["probe"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
