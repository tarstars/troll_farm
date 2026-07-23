#!/usr/bin/env python3
"""Short PPO signal trainer for the exact resident-aware residual environment."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
import torch
from torch import nn
from torch.distributions.categorical import Categorical

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.rl_resident_residual_env import (  # noqa: E402
    ACTION_PLANES,
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_WIDTH,
    OPPONENTS,
    ResidentResidualVecEnv,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def layer_init(layer: nn.Module, std: float = math.sqrt(2), bias: float = 0.0) -> nn.Module:
    nn.init.orthogonal_(layer.weight, std)
    if layer.bias is not None:
        nn.init.constant_(layer.bias, bias)
    return layer


class ResidualBlock(nn.Module):
    def __init__(self, width: int) -> None:
        super().__init__()
        self.conv1 = layer_init(nn.Conv2d(width, width, 3, padding=1))
        self.conv2 = layer_init(nn.Conv2d(width, width, 3, padding=1), std=1.0)
        self.activation = nn.ReLU(inplace=True)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        hidden = self.activation(self.conv1(inputs))
        return self.activation(inputs + self.conv2(hidden))


class ResidentResidualActorCritic(nn.Module):
    def __init__(
        self,
        *,
        width: int = 8,
        blocks: int = 2,
        keep_bias: float = 0.5,
    ) -> None:
        super().__init__()
        self.width = width
        self.blocks = blocks
        self.keep_bias = keep_bias
        self.stem = nn.Sequential(
            layer_init(nn.Conv2d(OBS_CHANNELS, width, 3, padding=1)),
            nn.ReLU(inplace=True),
        )
        self.tower = nn.Sequential(*(ResidualBlock(width) for _ in range(blocks)))
        self.actor = layer_init(nn.Conv2d(width, ACTION_PLANES, 1), std=0.01)
        with torch.no_grad():
            self.actor.bias.zero_()
            self.actor.bias[0] = keep_bias
        self.critic = nn.Sequential(
            layer_init(nn.Linear(width, 32)),
            nn.Tanh(),
            layer_init(nn.Linear(32, 1), std=1.0),
        )

    def forward(self, observations: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        observations = observations.float() * (1.0 / 255.0)
        valid = observations[:, :1]
        hidden = self.tower(self.stem(observations))
        logits = self.actor(hidden).flatten(1)
        pooled = (hidden * valid).sum(dim=(2, 3)) / valid.sum(dim=(2, 3)).clamp_min(1.0)
        return logits, self.critic(pooled).squeeze(-1)

    def action_and_value(
        self,
        observations: torch.Tensor,
        masks: torch.Tensor,
        action: torch.Tensor | None = None,
        *,
        deterministic: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        logits, value = self(observations)
        legal = masks.reshape(masks.shape[0], -1).bool()
        masked_logits = logits.masked_fill(~legal, torch.finfo(logits.dtype).min)
        distribution = Categorical(logits=masked_logits)
        if action is None:
            action = masked_logits.argmax(dim=1) if deterministic else distribution.sample()
        return action, distribution.log_prob(action), distribution.entropy(), value


@torch.inference_mode()
def evaluate(
    model: ResidentResidualActorCritic,
    *,
    seed_base: int,
    scenarios: int,
    num_envs: int,
    max_turns: int,
) -> dict:
    model.eval()
    device = next(model.parameters()).device
    stop = seed_base + scenarios
    completed: dict[int, dict] = {}
    transitions = 0
    started = time.perf_counter()
    with ResidentResidualVecEnv(num_envs, seed_base, max_turns=max_turns) as env:
        while len(completed) < scenarios:
            actions, _, _, _ = model.action_and_value(
                torch.from_numpy(env.obs).to(device),
                torch.from_numpy(env.masks).to(device),
                deterministic=True,
            )
            _, _, _, info = env.step(actions.cpu().numpy().astype(np.int32, copy=False))
            transitions += num_envs
            for index in np.flatnonzero(info.dones):
                scenario = int(info.scenario_seeds[index])
                if seed_base <= scenario < stop:
                    completed[scenario] = {
                        "scenario": scenario,
                        "map_seed": int(info.map_seeds[index]),
                        "seat": int(info.seats[index]),
                        "opponent_id": int(info.opponents[index]),
                        "opponent": OPPONENTS[int(info.opponents[index])],
                        "turn": int(info.turns[index]),
                        "return": float(info.returns[index]),
                        "margin": int(info.margins[index]),
                        "wood_edge": int(info.wood_edges[index]),
                        "workers": int(info.workers[index]),
                        "opponent_workers": int(info.opponent_workers[index]),
                        "overrides": int(info.overrides[index]),
                        "residual_attempts": int(info.residual_attempts[index]),
                        "rejected_actions": int(info.rejected_actions[index]),
                    }
    elapsed = time.perf_counter() - started
    rows = [completed[scenario] for scenario in range(seed_base, stop)]
    return {
        "seed_base": seed_base,
        "seed_stop_exclusive": stop,
        "scenarios": scenarios,
        "transitions": transitions,
        "elapsed_seconds": elapsed,
        "transitions_per_second": transitions / elapsed,
        "mean_margin": float(np.mean([row["margin"] for row in rows])),
        "mean_wood_edge": float(np.mean([row["wood_edge"] for row in rows])),
        "override_episode_rate": float(np.mean([row["overrides"] > 0 for row in rows])),
        "mean_overrides": float(np.mean([row["overrides"] for row in rows])),
        "changed_action_episode_rate": float(
            np.mean([row["residual_attempts"] > 0 for row in rows])
        ),
        "rejected_actions": int(sum(row["rejected_actions"] for row in rows)),
        "rows": rows,
    }


def explained_variance(prediction: np.ndarray, target: np.ndarray) -> float:
    variance = np.var(target)
    if variance == 0:
        return float("nan")
    return float(1.0 - np.var(target - prediction) / variance)


def train(args: argparse.Namespace) -> dict:
    batch_size = args.num_envs * args.rollout_steps
    if args.total_transitions % batch_size:
        raise ValueError("total transitions must be divisible by rollout batch")
    if batch_size % args.minibatch_size:
        raise ValueError("rollout batch must be divisible by minibatch size")
    torch.manual_seed(args.model_seed)
    np.random.seed(args.model_seed)
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(2, args.threads))
    rng = np.random.default_rng(args.model_seed)
    device = torch.device(args.device)
    model = ResidentResidualActorCritic(
        width=args.width,
        blocks=args.blocks,
        keep_bias=args.keep_bias,
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, eps=1e-5)

    observations = np.empty(
        (
            args.rollout_steps,
            args.num_envs,
            OBS_CHANNELS,
            OBS_HEIGHT,
            OBS_WIDTH,
        ),
        dtype=np.uint8,
    )
    masks = np.empty(
        (
            args.rollout_steps,
            args.num_envs,
            ACTION_PLANES,
            OBS_HEIGHT,
            OBS_WIDTH,
        ),
        dtype=np.uint8,
    )
    actions = np.empty((args.rollout_steps, args.num_envs), dtype=np.int64)
    logprobs = np.empty((args.rollout_steps, args.num_envs), dtype=np.float32)
    rewards = np.empty((args.rollout_steps, args.num_envs), dtype=np.float32)
    dones = np.empty((args.rollout_steps, args.num_envs), dtype=np.float32)
    values = np.empty((args.rollout_steps, args.num_envs), dtype=np.float32)

    logs = []
    episodes = []
    total_updates = args.total_transitions // batch_size
    global_step = 0
    wall_started = time.perf_counter()
    with ResidentResidualVecEnv(
        args.num_envs, args.train_seed_base, max_turns=args.max_turns
    ) as env:
        with torch.no_grad():
            deterministic, _, _, _ = model.action_and_value(
                torch.from_numpy(env.obs).to(device),
                torch.from_numpy(env.masks).to(device),
                deterministic=True,
            )
        initial_keep_rate = float(
            np.mean(deterministic.cpu().numpy() == env.keep_actions())
        )
        if initial_keep_rate != 1.0:
            raise RuntimeError("deterministic initialization is not all KEEP")

        for update in range(1, total_updates + 1):
            update_started = time.perf_counter()
            rollout_started = update_started
            for step_index in range(args.rollout_steps):
                np.copyto(observations[step_index], env.obs)
                np.copyto(masks[step_index], env.masks)
                with torch.no_grad():
                    chosen, logprob, _, value = model.action_and_value(
                        torch.from_numpy(env.obs).to(device),
                        torch.from_numpy(env.masks).to(device),
                    )
                chosen_np = chosen.cpu().numpy()
                actions[step_index] = chosen_np
                logprobs[step_index] = logprob.cpu().numpy()
                values[step_index] = value.cpu().numpy()
                _, _, step_rewards, info = env.step(
                    chosen_np.astype(np.int32, copy=False)
                )
                rewards[step_index] = step_rewards
                dones[step_index] = info.dones
                global_step += args.num_envs
                for index in np.flatnonzero(info.dones):
                    episodes.append(
                        {
                            "scenario": int(info.scenario_seeds[index]),
                            "margin": int(info.margins[index]),
                            "return": float(info.returns[index]),
                            "overrides": int(info.overrides[index]),
                            "residual_attempts": int(info.residual_attempts[index]),
                        }
                    )
            rollout_elapsed = time.perf_counter() - rollout_started

            with torch.no_grad():
                _, next_value = model(torch.from_numpy(env.obs).to(device))
            next_value_np = next_value.cpu().numpy()
            advantages = np.zeros_like(rewards)
            last_advantage = np.zeros(args.num_envs, dtype=np.float32)
            for step_index in reversed(range(args.rollout_steps)):
                next_nonterminal = 1.0 - dones[step_index]
                next_values = (
                    next_value_np
                    if step_index == args.rollout_steps - 1
                    else values[step_index + 1]
                )
                delta = (
                    rewards[step_index]
                    + args.gamma * next_values * next_nonterminal
                    - values[step_index]
                )
                last_advantage = (
                    delta
                    + args.gamma
                    * args.gae_lambda
                    * next_nonterminal
                    * last_advantage
                )
                advantages[step_index] = last_advantage
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
            indices = np.arange(batch_size)
            clip_fractions = []
            approx_kl = 0.0
            policy_loss_value = value_loss_value = entropy_value = 0.0
            for _ in range(args.update_epochs):
                rng.shuffle(indices)
                for start in range(0, batch_size, args.minibatch_size):
                    minibatch = indices[start : start + args.minibatch_size]
                    mb_obs = torch.from_numpy(flat_observations[minibatch]).to(device)
                    mb_masks = torch.from_numpy(flat_masks[minibatch]).to(device)
                    mb_actions = torch.from_numpy(flat_actions[minibatch]).to(device)
                    _, new_logprob, entropy, new_value = model.action_and_value(
                        mb_obs, mb_masks, mb_actions
                    )
                    log_ratio = new_logprob - torch.from_numpy(
                        flat_logprobs[minibatch]
                    ).to(device)
                    ratio = log_ratio.exp()
                    with torch.no_grad():
                        approx_kl = float(((ratio - 1.0) - log_ratio).mean())
                        clip_fractions.append(
                            float(
                                ((ratio - 1.0).abs() > args.clip_coef)
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
                    policy_loss = torch.maximum(
                        -mb_advantages * ratio,
                        -mb_advantages
                        * ratio.clamp(1.0 - args.clip_coef, 1.0 + args.clip_coef),
                    ).mean()
                    value_loss = 0.5 * (
                        new_value
                        - torch.from_numpy(flat_returns[minibatch]).to(device)
                    ).pow(2).mean()
                    entropy_loss = entropy.mean()
                    loss = (
                        policy_loss
                        + args.value_coef * value_loss
                        - args.entropy_coef * entropy_loss
                    )
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
                    optimizer.step()
                    policy_loss_value = float(policy_loss.detach())
                    value_loss_value = float(value_loss.detach())
                    entropy_value = float(entropy_loss.detach())
                if args.target_kl > 0 and approx_kl > args.target_kl:
                    break

            recent = episodes[-256:]
            log = {
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
                "mean_overrides_recent": (
                    float(np.mean([row["overrides"] for row in recent]))
                    if recent
                    else None
                ),
                "policy_loss": policy_loss_value,
                "value_loss": value_loss_value,
                "entropy": entropy_value,
                "approx_kl": approx_kl,
                "clip_fraction": float(np.mean(clip_fractions)),
                "explained_variance": explained_variance(flat_values, flat_returns),
            }
            logs.append(log)
            if update == 1 or update % 8 == 0 or update == total_updates:
                print(json.dumps({"event": "update", **log}, sort_keys=True), flush=True)

    evaluation = evaluate(
        model,
        seed_base=args.eval_seed_base,
        scenarios=args.eval_scenarios,
        num_envs=args.num_envs,
        max_turns=args.max_turns,
    )
    config = vars(args).copy()
    config.update(
        {
            "batch_size": batch_size,
            "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
            "initial_deterministic_keep_rate": initial_keep_rate,
            "protocol_sha256": sha256(Path(args.protocol)),
            "environment_sha256": sha256(
                REPO / "rust/src/rl_resident_residual.rs"
            ),
        }
    )
    result = {
        "schema": 1,
        "config": config,
        "wall_seconds": time.perf_counter() - wall_started,
        "training_episodes": len(episodes),
        "training_recent": episodes[-256:],
        "logs": logs,
        "evaluation": evaluation,
    }
    prefix = Path(args.output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = prefix.with_suffix(".pt")
    output = prefix.with_suffix(".json")
    torch.save(
        {
            "schema": 1,
            "model": model.state_dict(),
            "config": config,
            "evaluation": {key: value for key, value in evaluation.items() if key != "rows"},
        },
        checkpoint,
    )
    result["checkpoint"] = str(checkpoint)
    result["checkpoint_sha256"] = sha256(checkpoint)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "event": "complete",
                "output": str(output),
                "checkpoint": str(checkpoint),
                "evaluation": {key: value for key, value in evaluation.items() if key != "rows"},
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-prefix", required=True)
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--model-seed", type=int, required=True)
    parser.add_argument("--keep-bias", type=float, required=True)
    parser.add_argument("--train-seed-base", type=int, default=120_000)
    parser.add_argument("--eval-seed-base", type=int, default=240_000)
    parser.add_argument("--eval-scenarios", type=int, default=240)
    parser.add_argument("--num-envs", type=int, default=32)
    parser.add_argument("--rollout-steps", type=int, default=64)
    parser.add_argument("--total-transitions", type=int, default=131_072)
    parser.add_argument("--max-turns", type=int, default=300)
    parser.add_argument("--width", type=int, default=8)
    parser.add_argument("--blocks", type=int, default=2)
    parser.add_argument("--update-epochs", type=int, default=3)
    parser.add_argument("--minibatch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=2.5e-4)
    parser.add_argument("--gamma", type=float, default=0.999)
    parser.add_argument("--gae-lambda", type=float, default=0.98)
    parser.add_argument("--clip-coef", type=float, default=0.2)
    parser.add_argument("--entropy-coef", type=float, default=0.002)
    parser.add_argument("--value-coef", type=float, default=0.5)
    parser.add_argument("--max-grad-norm", type=float, default=0.5)
    parser.add_argument("--target-kl", type=float, default=0.03)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--device", choices=("cpu",), default="cpu")
    args = parser.parse_args()
    train(args)


if __name__ == "__main__":
    main()

