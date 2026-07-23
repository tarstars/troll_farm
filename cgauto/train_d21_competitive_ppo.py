#!/usr/bin/env python3
"""Run the single frozen D21 full-game margin PPO pilot."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
import time

import numpy as np
import torch
from torch import nn
from torch.distributions.categorical import Categorical

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.rl_level1_env import (  # noqa: E402
    ACTION_PLANES,
    ACTION_SIZE,
    DEFAULT_LIBRARY,
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_WIDTH,
)
from cgauto.rl_level6_env import Level6VecEnv  # noqa: E402
from cgauto.train_level1_ppo import (  # noqa: E402
    SpatialActorCritic,
    explained_variance,
    legal_teacher_auxiliary_loss,
    resolve_device,
    sha256,
)


ANALYSIS = REPO / "data" / "analysis" / "live-agent-6553250"
INITIAL_CHECKPOINT = (
    ANALYSIS / "curriculum-level5-seed-reacquisition-d11-ppo-final-local-l5b.pt"
)
PROTOCOL = ANALYSIS / "d21-competitive-closed-loop-preflight-protocol-2026-07-20.md"
PREFLIGHT_GATE = ANALYSIS / "d21-competitive-preflight-gate-2026-07-20.json"
OUTPUT_PREFIX = ANALYSIS / "d21-competitive-ppo-pilot-seed2107"
INITIAL_CHECKPOINT_SHA256 = (
    "44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6"
)

FROZEN = {
    "model_seed": 2107,
    "train_seed_base": 8_200_000,
    "num_envs": 100,
    "rollout_steps": 100,
    "total_transitions": 1_000_000,
    "update_epochs": 4,
    "minibatch_size": 1_000,
    "learning_rate": 2.5e-4,
    "gamma": 1.0,
    "gae_lambda": 0.95,
    "clip_coef": 0.2,
    "entropy_coef": 0.005,
    "value_coef": 0.5,
    "reward_scale": 1.0,
    "max_grad_norm": 0.5,
    "target_kl": 0.03,
    "teacher_aux_coef": 0.05,
    "max_turns": 300,
}


def compute_advantages(
    rewards: np.ndarray,
    dones: np.ndarray,
    values: np.ndarray,
    next_values: np.ndarray,
    *,
    gamma: float,
    gae_lambda: float,
) -> np.ndarray:
    """Compute vectorized GAE while respecting auto-reset episode boundaries."""

    advantages = np.zeros_like(rewards, dtype=np.float32)
    last_advantage = np.zeros(rewards.shape[1], dtype=np.float32)
    for step_index in reversed(range(rewards.shape[0])):
        next_nonterminal = 1.0 - dones[step_index]
        following_values = (
            next_values if step_index == rewards.shape[0] - 1 else values[step_index + 1]
        )
        delta = (
            rewards[step_index]
            + gamma * following_values * next_nonterminal
            - values[step_index]
        )
        last_advantage = (
            delta
            + gamma * gae_lambda * next_nonterminal * last_advantage
        )
        advantages[step_index] = last_advantage
    return advantages


def validate_prerequisites(
    initial_checkpoint: Path,
    protocol: Path,
    preflight_gate: Path,
) -> dict:
    for label, path in (
        ("initial checkpoint", initial_checkpoint),
        ("protocol", protocol),
        ("preflight gate", preflight_gate),
        ("release environment library", Path(DEFAULT_LIBRARY)),
    ):
        if not path.exists():
            raise SystemExit(f"missing {label}: {path}")
    if sha256(initial_checkpoint) != INITIAL_CHECKPOINT_SHA256:
        raise SystemExit("D21 initial checkpoint hash mismatch")
    gate = json.loads(preflight_gate.read_text())
    if gate.get("preflight_pass") is not True or not all(gate.get("gates", {}).values()):
        raise SystemExit("D21 frozen preflight did not pass")
    if gate.get("source", {}).get("protocol_sha256") != sha256(protocol):
        raise SystemExit("D21 preflight/protocol hash mismatch")
    return gate


def episode_summary(rows: list[dict]) -> dict:
    if not rows:
        return {"episodes": 0}
    margins = [row["margin"] for row in rows]
    return {
        "episodes": len(rows),
        "seed_min": min(row["seed"] for row in rows),
        "seed_max": max(row["seed"] for row in rows),
        "wins": sum(margin > 0 for margin in margins),
        "ties": sum(margin == 0 for margin in margins),
        "losses": sum(margin < 0 for margin in margins),
        "mean_margin": float(np.mean(margins)),
        "mean_return": float(np.mean([row["return"] for row in rows])),
        "training_completion_rate": sum(row["training_completed"] for row in rows)
        / len(rows),
        "crop_creation_rate": sum(row["created_crop"] for row in rows) / len(rows),
        "renewable_harvest_rate": sum(
            row["renewable_harvests"] > 0 for row in rows
        )
        / len(rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial-checkpoint", type=Path, default=INITIAL_CHECKPOINT)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL)
    parser.add_argument("--preflight-gate", type=Path, default=PREFLIGHT_GATE)
    parser.add_argument("--output-prefix", type=Path, default=OUTPUT_PREFIX)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args()
    if args.threads <= 0:
        raise SystemExit("threads must be positive")

    checkpoint_path = Path(f"{args.output_prefix}-final.pt")
    summary_path = Path(f"{args.output_prefix}-training-summary.json")
    if checkpoint_path.exists() or summary_path.exists():
        raise SystemExit("refusing to overwrite an existing D21 pilot artifact")
    args.output_prefix.parent.mkdir(parents=True, exist_ok=True)
    gate = validate_prerequisites(
        args.initial_checkpoint,
        args.protocol,
        args.preflight_gate,
    )

    batch_size = FROZEN["num_envs"] * FROZEN["rollout_steps"]
    if batch_size != 10_000 or FROZEN["total_transitions"] % batch_size:
        raise SystemExit("frozen D21 batch geometry mismatch")
    if batch_size % FROZEN["minibatch_size"]:
        raise SystemExit("frozen D21 minibatch geometry mismatch")
    total_updates = FROZEN["total_transitions"] // batch_size

    torch.manual_seed(FROZEN["model_seed"])
    np.random.seed(FROZEN["model_seed"])
    device = resolve_device(args.device)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(FROZEN["model_seed"])
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(4, args.threads))
    torch.backends.mkldnn.enabled = True
    rng = np.random.default_rng(FROZEN["model_seed"])

    saved = torch.load(args.initial_checkpoint, map_location="cpu", weights_only=False)
    model = SpatialActorCritic()
    model.load_state_dict(saved["model"], strict=True)
    model.to(device)
    optimizer = torch.optim.Adam(
        model.parameters(), lr=FROZEN["learning_rate"], eps=1e-5
    )

    observations = np.empty(
        (
            FROZEN["rollout_steps"],
            FROZEN["num_envs"],
            OBS_CHANNELS,
            OBS_HEIGHT,
            OBS_WIDTH,
        ),
        dtype=np.uint8,
    )
    masks = np.empty(
        (
            FROZEN["rollout_steps"],
            FROZEN["num_envs"],
            ACTION_PLANES,
            OBS_HEIGHT,
            OBS_WIDTH,
        ),
        dtype=np.uint8,
    )
    actions = np.empty(
        (FROZEN["rollout_steps"], FROZEN["num_envs"]), dtype=np.int64
    )
    logprobs = np.empty_like(actions, dtype=np.float32)
    rewards = np.empty_like(actions, dtype=np.float32)
    dones = np.empty_like(actions, dtype=np.float32)
    values = np.empty_like(actions, dtype=np.float32)
    teacher_actions = np.empty_like(actions, dtype=np.int64)

    config = {
        **FROZEN,
        "batch_size": batch_size,
        "total_updates": total_updates,
        "threads": args.threads,
        "device": args.device,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "torch_version": torch.__version__,
        "initial_checkpoint": str(args.initial_checkpoint),
        "initial_checkpoint_sha256": sha256(args.initial_checkpoint),
        "protocol": str(args.protocol),
        "protocol_sha256": sha256(args.protocol),
        "preflight_gate": str(args.preflight_gate),
        "preflight_gate_sha256": sha256(args.preflight_gate),
        "preflight_pass": gate["preflight_pass"],
        "environment_library": str(DEFAULT_LIBRARY),
        "environment_library_sha256": sha256(Path(DEFAULT_LIBRARY)),
        "trainer": str(Path(__file__).relative_to(REPO)),
        "teacher_aux_invalid_label_policy": "skip_undefined_off_teacher_targets",
        "intermediate_evaluations": 0,
    }
    print(json.dumps({"event": "start", **config}, sort_keys=True), flush=True)

    global_step = 0
    illegal_actor_actions = 0
    invalid_teacher_labels = 0
    teacher_labels = 0
    episode_rows: list[dict] = []
    logs: list[dict] = []
    started_wall = time.perf_counter()
    started_cpu = time.process_time()

    with Level6VecEnv(
        FROZEN["num_envs"],
        FROZEN["train_seed_base"],
        max_turns=FROZEN["max_turns"],
    ) as env:
        for update in range(1, total_updates + 1):
            update_started = time.perf_counter()
            rollout_started = update_started
            for step_index in range(FROZEN["rollout_steps"]):
                np.copyto(observations[step_index], env.obs)
                np.copyto(masks[step_index], env.masks)
                teacher_actions[step_index] = env.teacher_actions()
                with torch.no_grad():
                    selected, selected_logprob, _, selected_value = (
                        model.action_and_value(
                            torch.from_numpy(env.obs).to(device),
                            torch.from_numpy(env.masks).to(device),
                        )
                    )
                selected_np = selected.cpu().numpy()
                flat_legal = env.masks.reshape(FROZEN["num_envs"], ACTION_SIZE)
                illegal_actor_actions += int(
                    np.count_nonzero(
                        flat_legal[np.arange(FROZEN["num_envs"]), selected_np] == 0
                    )
                )
                actions[step_index] = selected_np
                logprobs[step_index] = selected_logprob.cpu().numpy()
                values[step_index] = selected_value.cpu().numpy()
                _, _, step_rewards, info = env.step(
                    selected_np.astype(np.int32, copy=False)
                )
                if not np.isfinite(step_rewards).all():
                    raise RuntimeError("non-finite D21 environment reward")
                rewards[step_index] = step_rewards * FROZEN["reward_scale"]
                dones[step_index] = info.dones
                global_step += FROZEN["num_envs"]
                for index in np.flatnonzero(info.dones):
                    own_score = int(info.score_gains[index])
                    opponent_score = int(info.opponent_scores[index])
                    episode_rows.append(
                        {
                            "seed": int(info.seeds[index]),
                            "turn": int(info.turns[index]),
                            "return": float(info.returns[index]),
                            "own_score": own_score,
                            "opponent_score": opponent_score,
                            "margin": own_score - opponent_score,
                            "training_completed": int(info.training_turns[index]) > 0,
                            "created_crop": bool(info.created_crops[index]),
                            "renewable_harvests": int(info.renewable_harvests[index]),
                        }
                    )
            rollout_elapsed = time.perf_counter() - rollout_started

            with torch.no_grad():
                _, next_value = model(torch.from_numpy(env.obs).to(device))
            advantages = compute_advantages(
                rewards,
                dones,
                values,
                next_value.cpu().numpy(),
                gamma=FROZEN["gamma"],
                gae_lambda=FROZEN["gae_lambda"],
            )
            returns = advantages + values

            flat_observations = observations.reshape(
                batch_size, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH
            )
            flat_masks = masks.reshape(
                batch_size, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH
            )
            flat_actions = actions.reshape(batch_size)
            flat_logprobs = logprobs.reshape(batch_size)
            flat_advantages = advantages.reshape(batch_size)
            flat_returns = returns.reshape(batch_size)
            flat_values = values.reshape(batch_size)
            flat_teacher_actions = teacher_actions.reshape(batch_size)
            teacher_legal = flat_masks.reshape(batch_size, -1)[
                np.arange(batch_size), flat_teacher_actions
            ] != 0
            invalid_teacher_labels += int((~teacher_legal).sum())
            teacher_labels += batch_size

            indices = np.arange(batch_size)
            clip_fractions: list[float] = []
            approx_kl = 0.0
            policy_loss_value = 0.0
            value_loss_value = 0.0
            entropy_value = 0.0
            teacher_loss_value = 0.0
            teacher_accuracy_value = 0.0
            epochs_run = 0
            for epoch in range(FROZEN["update_epochs"]):
                rng.shuffle(indices)
                for start in range(0, batch_size, FROZEN["minibatch_size"]):
                    minibatch = indices[start : start + FROZEN["minibatch_size"]]
                    mb_observations = torch.from_numpy(
                        flat_observations[minibatch]
                    ).to(device)
                    mb_masks = torch.from_numpy(flat_masks[minibatch]).to(device)
                    mb_actions = torch.from_numpy(flat_actions[minibatch]).to(device)
                    logits, new_value = model(mb_observations)
                    legal = mb_masks.reshape(mb_masks.shape[0], -1).bool()
                    masked_logits = logits.masked_fill(
                        ~legal, torch.finfo(logits.dtype).min
                    )
                    distribution = Categorical(logits=masked_logits)
                    new_logprob = distribution.log_prob(mb_actions)
                    entropy = distribution.entropy()
                    log_ratio = new_logprob - torch.from_numpy(
                        flat_logprobs[minibatch]
                    ).to(device)
                    ratio = log_ratio.exp()
                    with torch.no_grad():
                        approx_kl = float(((ratio - 1.0) - log_ratio).mean())
                        clip_fractions.append(
                            float(
                                ((ratio - 1.0).abs() > FROZEN["clip_coef"])
                                .float()
                                .mean()
                            )
                        )

                    mb_advantages = torch.from_numpy(
                        flat_advantages[minibatch]
                    ).to(device)
                    mb_advantages = (mb_advantages - mb_advantages.mean()) / (
                        mb_advantages.std() + 1e-8
                    )
                    policy_loss_1 = -mb_advantages * ratio
                    policy_loss_2 = -mb_advantages * ratio.clamp(
                        1.0 - FROZEN["clip_coef"], 1.0 + FROZEN["clip_coef"]
                    )
                    policy_loss = torch.maximum(
                        policy_loss_1, policy_loss_2
                    ).mean()
                    value_loss = 0.5 * (
                        new_value
                        - torch.from_numpy(flat_returns[minibatch]).to(device)
                    ).pow(2).mean()
                    entropy_loss = entropy.mean()
                    mb_teacher_actions = torch.from_numpy(
                        flat_teacher_actions[minibatch]
                    ).to(device)
                    teacher_loss, teacher_accuracy, _ = (
                        legal_teacher_auxiliary_loss(
                            masked_logits,
                            legal,
                            mb_teacher_actions,
                        )
                    )
                    loss = (
                        policy_loss
                        - FROZEN["entropy_coef"] * entropy_loss
                        + FROZEN["value_coef"] * value_loss
                        + FROZEN["teacher_aux_coef"] * teacher_loss
                    )
                    if not torch.isfinite(loss):
                        raise RuntimeError("non-finite D21 PPO loss")
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    nn.utils.clip_grad_norm_(
                        model.parameters(), FROZEN["max_grad_norm"]
                    )
                    optimizer.step()
                    policy_loss_value = float(policy_loss.detach())
                    value_loss_value = float(value_loss.detach())
                    entropy_value = float(entropy_loss.detach())
                    teacher_loss_value = float(teacher_loss.detach())
                    teacher_accuracy_value = float(teacher_accuracy.detach())
                epochs_run = epoch + 1
                if FROZEN["target_kl"] > 0 and approx_kl > FROZEN["target_kl"]:
                    break

            if not all(
                torch.isfinite(parameter).all().item() for parameter in model.parameters()
            ):
                raise RuntimeError("non-finite D21 model parameter")
            fraction = update / total_updates
            optimizer.param_groups[0]["lr"] = FROZEN["learning_rate"] * (
                1.0 - fraction
            )
            recent = episode_rows[-1000:]
            log = {
                "event": "update",
                "update": update,
                "global_step": global_step,
                "rollout_sps": batch_size / rollout_elapsed,
                "update_sps": batch_size / (time.perf_counter() - update_started),
                "episodes_recent": len(recent),
                "mean_margin_recent": (
                    float(np.mean([row["margin"] for row in recent]))
                    if recent
                    else None
                ),
                "mean_return_recent": (
                    float(np.mean([row["return"] for row in recent]))
                    if recent
                    else None
                ),
                "policy_loss": policy_loss_value,
                "value_loss": value_loss_value,
                "entropy": entropy_value,
                "teacher_loss": teacher_loss_value,
                "teacher_accuracy": teacher_accuracy_value,
                "teacher_legal_rate_batch": float(teacher_legal.mean()),
                "approx_kl": approx_kl,
                "clip_fraction": float(np.mean(clip_fractions)),
                "explained_variance": explained_variance(flat_values, flat_returns),
                "epochs_run": epochs_run,
                "learning_rate": optimizer.param_groups[0]["lr"],
            }
            logs.append(log)
            print(json.dumps(log, sort_keys=True), flush=True)

    elapsed_wall = time.perf_counter() - started_wall
    elapsed_cpu = time.process_time() - started_cpu
    if global_step != FROZEN["total_transitions"]:
        raise RuntimeError("D21 pilot transition count mismatch")
    checkpoint = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "config": config,
        "global_step": global_step,
        "training_episode_summary": episode_summary(episode_rows),
        "final_log": logs[-1],
    }
    torch.save(checkpoint, checkpoint_path)
    summary = {
        "schema": 1,
        "scope": (
            "single frozen D21 local 1M-transition PPO pilot; no intermediate "
            "validation and no candidate or Arena authorization"
        ),
        "config": config,
        "global_step": global_step,
        "updates_completed": len(logs),
        "elapsed_wall_seconds": elapsed_wall,
        "elapsed_cpu_seconds": elapsed_cpu,
        "aggregate_host_cpu_percent": (
            100.0
            * elapsed_cpu
            / elapsed_wall
            / max(os.cpu_count() or 1, 1)
        ),
        "overall_transitions_per_second": global_step / elapsed_wall,
        "illegal_actor_actions": illegal_actor_actions,
        "teacher_auxiliary": {
            "labels": teacher_labels,
            "invalid_labels": invalid_teacher_labels,
            "legal_rate": 1.0 - invalid_teacher_labels / teacher_labels,
        },
        "training_episodes": episode_summary(episode_rows),
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sha256(checkpoint_path),
        "logs": logs,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "event": "complete",
                "checkpoint": str(checkpoint_path),
                "checkpoint_sha256": summary["checkpoint_sha256"],
                "global_step": global_step,
                "elapsed_wall_seconds": elapsed_wall,
                "transitions_per_second": summary["overall_transitions_per_second"],
                "illegal_actor_actions": illegal_actor_actions,
                "teacher_auxiliary": summary["teacher_auxiliary"],
                "training_episodes": summary["training_episodes"],
                "summary": str(summary_path),
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
