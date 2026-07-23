#!/usr/bin/env python3
"""Train and prospectively evaluate the compact spatial curriculum policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.distributions.categorical import Categorical
from torch.nn import functional as F

from cgauto.rl_level1_env import (
    ACTION_PLANES,
    ACTION_SIZE,
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_WIDTH,
    Level1VecEnv,
)
from cgauto.rl_level2_env import LEVEL2_RECIPE_NAMES, LEVEL2_TARGETS, Level2VecEnv
from cgauto.rl_level3_env import LEVEL3_SCORE_GAIN, LEVEL3_TARGET, Level3VecEnv
from cgauto.rl_level4_env import Level4VecEnv
from cgauto.rl_level5_env import (
    Level5CropFirstRepeatedPressure180VecEnv,
    Level5CropFirstRepeatedPressureReacquire180VecEnv,
    Level5CropFirstSustainedTrio180VecEnv,
    Level5FundedPairVecEnv,
    Level5FundedTrioVecEnv,
    Level5ForagerVecEnv,
    Level5PlanterVecEnv,
    Level5ReaperVecEnv,
    Level5RecoveryVecEnv,
    Level5SustainedTrio180VecEnv,
    Level5SustainedTrioVecEnv,
    Level5VecEnv,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "curriculum-ppo-level1-protocol-2026-07-19.md"
RANDOM_BASELINE = ANALYSIS / "curriculum-level1-random-2000000-2000999-exact.json"
TEACHER_BASELINE = ANALYSIS / "curriculum-level1-teacher-2000000-2000999-exact.json"

LEVEL5_OPPONENT_ENVS = {
    "complete": Level5VecEnv,
    "complete-recovery": Level5RecoveryVecEnv,
    "natural-forager": Level5ForagerVecEnv,
    "natural-planter": Level5PlanterVecEnv,
    "one-shot-reaper": Level5ReaperVecEnv,
    "funded-pair": Level5FundedPairVecEnv,
    "funded-trio": Level5FundedTrioVecEnv,
    "funded-trio-sustained": Level5SustainedTrioVecEnv,
    "funded-trio-sustained-180": Level5SustainedTrio180VecEnv,
    "crop-first-funded-trio-sustained-180": Level5CropFirstSustainedTrio180VecEnv,
    "crop-first-funded-trio-repeated-pressure-180": (
        Level5CropFirstRepeatedPressure180VecEnv
    ),
    "crop-first-funded-trio-repeated-pressure-reacquire-180": (
        Level5CropFirstRepeatedPressureReacquire180VecEnv
    ),
}
LEVEL5_OPPONENT_MODES = tuple(LEVEL5_OPPONENT_ENVS)


def level5_env_class(opponent_mode: str):
    try:
        return LEVEL5_OPPONENT_ENVS[opponent_mode]
    except KeyError as error:
        raise ValueError(f"unsupported Level-5 opponent mode {opponent_mode}") from error


def resolve_device(name: str) -> torch.device:
    device = torch.device(name)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise SystemExit("--device cuda requires an available CUDA device")
    return device


def save_model_weights_npz(model: nn.Module, path: Path) -> None:
    arrays = {
        name: tensor.detach().cpu().numpy()
        for name, tensor in model.state_dict().items()
    }
    np.savez(path, **arrays)


def load_model_weights_npz(model: nn.Module, path: Path) -> None:
    expected = model.state_dict()
    with np.load(path, allow_pickle=False) as archive:
        if set(archive.files) != set(expected):
            missing = sorted(set(expected) - set(archive.files))
            extra = sorted(set(archive.files) - set(expected))
            raise ValueError(
                f"model-weight archive key mismatch: missing={missing}, extra={extra}"
            )
        state = {
            name: torch.from_numpy(archive[name].copy())
            for name in expected
        }
    model.load_state_dict(state, strict=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


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


class SpatialActorCritic(nn.Module):
    def __init__(self, width: int = 16, blocks: int = 4) -> None:
        super().__init__()
        self.width = width
        self.blocks = blocks
        self.stem = nn.Sequential(
            layer_init(nn.Conv2d(OBS_CHANNELS, width, 3, padding=1)),
            nn.ReLU(inplace=True),
        )
        self.tower = nn.Sequential(*(ResidualBlock(width) for _ in range(blocks)))
        self.actor = layer_init(nn.Conv2d(width, ACTION_PLANES, 1), std=0.01)
        self.critic = nn.Sequential(
            layer_init(nn.Linear(width, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 1), std=1.0),
        )

    def forward(self, observations: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        if observations.dtype != torch.float32:
            observations = observations.float()
        observations = observations * (1.0 / 255.0)
        valid = observations[:, :1]
        hidden = self.tower(self.stem(observations))
        logits = self.actor(hidden).flatten(1)
        pooled = (hidden * valid).sum(dim=(2, 3)) / valid.sum(dim=(2, 3)).clamp_min(1.0)
        value = self.critic(pooled).squeeze(-1)
        return logits, value

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


@dataclass
class Evaluation:
    seed_base: int
    seed_stop_exclusive: int
    exact_seed_interval: bool
    episodes: int
    successes: int
    success_rate: float
    median_success_turn: float | None
    transitions: int
    elapsed_seconds: float
    transitions_per_second: float
    by_height: dict[str, dict]
    by_recipe: dict[str, dict] | None
    target: list[int] | None
    required_score_gain: int | None
    created_crop_rate: float | None
    renewable_harvest_rate: float | None
    median_training_turn: float | None
    median_score_gain: float | None
    material_opponent_rate: float | None
    mean_opponent_score: float | None
    median_opponent_score: float | None
    opponent_multiworker_rate: float | None
    opponent_crop_creation_rate: float | None
    opponent_renewable_harvest_rate: float | None
    mean_opponent_created_crops: float | None
    mean_opponent_renewable_harvests: float | None
    opponent_crop_destruction_rate: float | None
    opponent_crop_destruction_at_least_two_rate: float | None
    opponent_crop_destruction_at_least_three_rate: float | None
    max_opponent_crop_destructions: int | None
    mean_opponent_crop_destructions: float | None
    opponent_training_rate: float | None
    median_opponent_training_turn: float | None
    opponent_funding_receipt_rate: float | None
    trained_with_funding_receipt_rate: float | None
    opponent_second_worker_productive_rate: float | None
    mean_opponent_second_worker_productive_actions: float | None
    max_opponent_workers: int | None
    opponent_third_worker_training_rate: float | None
    median_opponent_third_worker_training_turn: float | None
    third_trained_with_fresh_funding_receipt_rate: float | None
    opponent_third_worker_productive_rate: float | None
    mean_opponent_third_worker_productive_actions: float | None
    mean_opponent_funded_training_events: float | None
    rows: list[dict]


@torch.inference_mode()
def evaluate(
    model: SpatialActorCritic,
    *,
    seed_base: int,
    episodes: int,
    num_envs: int,
    curriculum_level: int = 1,
    max_turns: int | None = None,
    level5_opponent_mode: str = "natural-forager",
) -> Evaluation:
    model.eval()
    device = next(model.parameters()).device
    target_stop = seed_base + episodes
    completed: dict[int, dict] = {}
    transitions = 0
    start = time.perf_counter()
    if curriculum_level == 1:
        env_context = Level1VecEnv(
            num_envs, seed_base, max_turns=max_turns or 180
        )
    elif curriculum_level == 2:
        env_context = Level2VecEnv(
            num_envs, seed_base, max_turns=max_turns or 240
        )
    elif curriculum_level == 3:
        env_context = Level3VecEnv(
            num_envs, seed_base, max_turns=max_turns or 240
        )
    elif curriculum_level == 4:
        env_context = Level4VecEnv(
            num_envs, seed_base, max_turns=max_turns or 240
        )
    elif curriculum_level == 5:
        env_class = level5_env_class(level5_opponent_mode)
        env_context = env_class(
            num_envs, seed_base, max_turns=max_turns or 240
        )
    else:
        raise ValueError(f"unsupported curriculum level {curriculum_level}")
    with env_context as env:
        while len(completed) < episodes:
            observations = torch.from_numpy(env.obs).to(device)
            masks = torch.from_numpy(env.masks).to(device)
            actions, _, _, _ = model.action_and_value(
                observations, masks, deterministic=True
            )
            _, _, _, info = env.step(
                actions.cpu().numpy().astype(np.int32, copy=False)
            )
            transitions += num_envs
            for index in np.flatnonzero(info.dones):
                seed = int(info.seeds[index])
                if seed_base <= seed < target_stop:
                    row = {
                        "seed": seed,
                        "success": bool(info.successes[index]),
                        "turns": int(info.turns[index]),
                        "return": float(info.returns[index]),
                        "height": int(info.heights[index]),
                    }
                    if curriculum_level == 1:
                        row["initial_deficit"] = int(info.initial_deficits[index])
                    elif curriculum_level == 2:
                        recipe_id = int(info.recipe_ids[index])
                        row.update(
                            {
                                "initial_deficit": int(
                                    info.initial_total_deficits[index]
                                ),
                                "initial_total_deficit": int(
                                    info.initial_total_deficits[index]
                                ),
                                "recipe_id": recipe_id,
                                "recipe_name": LEVEL2_RECIPE_NAMES[recipe_id],
                                "target": [
                                    int(value) for value in info.targets[index]
                                ],
                            }
                        )
                    else:
                        row.update(
                            {
                                "initial_deficit": int(
                                    info.initial_total_deficits[index]
                                ),
                                "initial_total_deficit": int(
                                    info.initial_total_deficits[index]
                                ),
                                "target": (
                                    list(LEVEL3_TARGET)
                                    if curriculum_level == 3
                                    else [int(value) for value in info.targets[index]]
                                ),
                                "training_turn": int(info.training_turns[index]),
                                "score_gain": int(info.score_gains[index]),
                                "renewable_harvests": int(
                                    info.renewable_harvests[index]
                                ),
                                "created_crop": bool(info.created_crops[index]),
                            }
                        )
                        if curriculum_level in (4, 5):
                            recipe_id = int(info.recipe_ids[index])
                            row["recipe_id"] = recipe_id
                            row["recipe_name"] = LEVEL2_RECIPE_NAMES[recipe_id]
                        if curriculum_level == 5:
                            row["opponent_score"] = int(info.opponent_scores[index])
                            row["opponent_workers"] = int(info.opponent_workers[index])
                            row["opponent_created_crops"] = int(
                                info.opponent_created_crops[index]
                            )
                            row["opponent_renewable_harvests"] = int(
                                info.opponent_renewable_harvests[index]
                            )
                            row["opponent_crop_destructions"] = int(
                                info.opponent_crop_destructions[index]
                            )
                            row["opponent_training_turn"] = int(
                                info.opponent_training_turns[index]
                            )
                            row["opponent_funding_deposits"] = int(
                                info.opponent_funding_deposits[index]
                            )
                            row["opponent_second_worker_productive_actions"] = int(
                                info.opponent_second_worker_productive_actions[index]
                            )
                            row["opponent_funded_training_events"] = int(
                                info.opponent_funded_training_events[index]
                            )
                            row["opponent_third_worker_training_turn"] = int(
                                info.opponent_third_worker_training_turns[index]
                            )
                            row["opponent_third_worker_productive_actions"] = int(
                                info.opponent_third_worker_productive_actions[index]
                            )
                    completed[seed] = row
    elapsed = time.perf_counter() - start
    rows = [completed[seed] for seed in range(seed_base, target_stop)]
    successful = [row for row in rows if row["success"]]
    by_height = {}
    for height in sorted({row["height"] for row in rows}):
        bucket = [row for row in rows if row["height"] == height]
        by_height[str(height)] = {
            "episodes": len(bucket),
            "successes": sum(row["success"] for row in bucket),
            "success_rate": sum(row["success"] for row in bucket) / len(bucket),
        }
    by_recipe = None
    if curriculum_level in (2, 4, 5):
        by_recipe = {}
        for recipe_id, name in enumerate(LEVEL2_RECIPE_NAMES):
            bucket = [row for row in rows if row["recipe_id"] == recipe_id]
            successes = sum(row["success"] for row in bucket)
            by_recipe[str(recipe_id)] = {
                "name": name,
                "target": list(LEVEL2_TARGETS[recipe_id]),
                "episodes": len(bucket),
                "successes": successes,
                "success_rate": successes / len(bucket) if bucket else None,
            }
    created_crop_rate = None
    renewable_harvest_rate = None
    median_training_turn = None
    median_score_gain = None
    if curriculum_level in (3, 4, 5):
        created_crop_rate = sum(row["created_crop"] for row in rows) / len(rows)
        renewable_harvest_rate = sum(
            row["renewable_harvests"] > 0 for row in rows
        ) / len(rows)
        training_turns = [row["training_turn"] for row in rows if row["training_turn"]]
        median_training_turn = (
            float(np.median(training_turns)) if training_turns else None
        )
        median_score_gain = float(np.median([row["score_gain"] for row in rows]))
    material_opponent_rate = None
    mean_opponent_score = None
    median_opponent_score = None
    opponent_multiworker_rate = None
    opponent_crop_creation_rate = None
    opponent_renewable_harvest_rate = None
    mean_opponent_created_crops = None
    mean_opponent_renewable_harvests = None
    opponent_crop_destruction_rate = None
    opponent_crop_destruction_at_least_two_rate = None
    opponent_crop_destruction_at_least_three_rate = None
    max_opponent_crop_destructions = None
    mean_opponent_crop_destructions = None
    opponent_training_rate = None
    median_opponent_training_turn = None
    opponent_funding_receipt_rate = None
    trained_with_funding_receipt_rate = None
    opponent_second_worker_productive_rate = None
    mean_opponent_second_worker_productive_actions = None
    max_opponent_workers = None
    opponent_third_worker_training_rate = None
    median_opponent_third_worker_training_turn = None
    third_trained_with_fresh_funding_receipt_rate = None
    opponent_third_worker_productive_rate = None
    mean_opponent_third_worker_productive_actions = None
    mean_opponent_funded_training_events = None
    if curriculum_level == 5:
        opponent_scores = [row["opponent_score"] for row in rows]
        material_opponent_rate = sum(
            row["opponent_score"] > 0 or row["opponent_workers"] > 1 for row in rows
        ) / len(rows)
        mean_opponent_score = float(np.mean(opponent_scores))
        median_opponent_score = float(np.median(opponent_scores))
        opponent_multiworker_rate = sum(
            row["opponent_workers"] > 1 for row in rows
        ) / len(rows)
        opponent_crop_creation_rate = sum(
            row["opponent_created_crops"] > 0 for row in rows
        ) / len(rows)
        opponent_renewable_harvest_rate = sum(
            row["opponent_renewable_harvests"] > 0 for row in rows
        ) / len(rows)
        mean_opponent_created_crops = float(
            np.mean([row["opponent_created_crops"] for row in rows])
        )
        mean_opponent_renewable_harvests = float(
            np.mean([row["opponent_renewable_harvests"] for row in rows])
        )
        opponent_crop_destruction_rate = sum(
            row["opponent_crop_destructions"] > 0 for row in rows
        ) / len(rows)
        opponent_crop_destruction_at_least_two_rate = sum(
            row["opponent_crop_destructions"] >= 2 for row in rows
        ) / len(rows)
        opponent_crop_destruction_at_least_three_rate = sum(
            row["opponent_crop_destructions"] >= 3 for row in rows
        ) / len(rows)
        max_opponent_crop_destructions = max(
            row["opponent_crop_destructions"] for row in rows
        )
        mean_opponent_crop_destructions = float(
            np.mean([row["opponent_crop_destructions"] for row in rows])
        )
        trained = [row for row in rows if row["opponent_training_turn"] > 0]
        opponent_training_rate = len(trained) / len(rows)
        median_opponent_training_turn = (
            float(np.median([row["opponent_training_turn"] for row in trained]))
            if trained
            else None
        )
        opponent_funding_receipt_rate = sum(
            row["opponent_funding_deposits"] > 0 for row in rows
        ) / len(rows)
        trained_with_funding_receipt_rate = (
            sum(row["opponent_funded_training_events"] >= 1 for row in trained)
            / len(trained)
            if trained
            else None
        )
        opponent_second_worker_productive_rate = sum(
            row["opponent_second_worker_productive_actions"] > 0 for row in rows
        ) / len(rows)
        mean_opponent_second_worker_productive_actions = float(
            np.mean(
                [row["opponent_second_worker_productive_actions"] for row in rows]
            )
        )
        max_opponent_workers = max(row["opponent_workers"] for row in rows)
        third_trained = [
            row for row in rows if row["opponent_third_worker_training_turn"] > 0
        ]
        opponent_third_worker_training_rate = len(third_trained) / len(rows)
        median_opponent_third_worker_training_turn = (
            float(
                np.median(
                    [row["opponent_third_worker_training_turn"] for row in third_trained]
                )
            )
            if third_trained
            else None
        )
        third_trained_with_fresh_funding_receipt_rate = (
            sum(
                row["opponent_funded_training_events"] >= 2
                for row in third_trained
            )
            / len(third_trained)
            if third_trained
            else None
        )
        opponent_third_worker_productive_rate = sum(
            row["opponent_third_worker_productive_actions"] > 0 for row in rows
        ) / len(rows)
        mean_opponent_third_worker_productive_actions = float(
            np.mean(
                [row["opponent_third_worker_productive_actions"] for row in rows]
            )
        )
        mean_opponent_funded_training_events = float(
            np.mean([row["opponent_funded_training_events"] for row in rows])
        )
    model.train()
    return Evaluation(
        seed_base=seed_base,
        seed_stop_exclusive=target_stop,
        exact_seed_interval=True,
        episodes=episodes,
        successes=len(successful),
        success_rate=len(successful) / episodes,
        median_success_turn=(
            float(np.median([row["turns"] for row in successful]))
            if successful
            else None
        ),
        transitions=transitions,
        elapsed_seconds=elapsed,
        transitions_per_second=transitions / elapsed,
        by_height=by_height,
        by_recipe=by_recipe,
        target=list(LEVEL3_TARGET) if curriculum_level == 3 else None,
        required_score_gain=(
            LEVEL3_SCORE_GAIN if curriculum_level in (3, 4, 5) else None
        ),
        created_crop_rate=created_crop_rate,
        renewable_harvest_rate=renewable_harvest_rate,
        median_training_turn=median_training_turn,
        median_score_gain=median_score_gain,
        material_opponent_rate=material_opponent_rate,
        mean_opponent_score=mean_opponent_score,
        median_opponent_score=median_opponent_score,
        opponent_multiworker_rate=opponent_multiworker_rate,
        opponent_crop_creation_rate=opponent_crop_creation_rate,
        opponent_renewable_harvest_rate=opponent_renewable_harvest_rate,
        mean_opponent_created_crops=mean_opponent_created_crops,
        mean_opponent_renewable_harvests=mean_opponent_renewable_harvests,
        opponent_crop_destruction_rate=opponent_crop_destruction_rate,
        opponent_crop_destruction_at_least_two_rate=(
            opponent_crop_destruction_at_least_two_rate
        ),
        opponent_crop_destruction_at_least_three_rate=(
            opponent_crop_destruction_at_least_three_rate
        ),
        max_opponent_crop_destructions=max_opponent_crop_destructions,
        mean_opponent_crop_destructions=mean_opponent_crop_destructions,
        opponent_training_rate=opponent_training_rate,
        median_opponent_training_turn=median_opponent_training_turn,
        opponent_funding_receipt_rate=opponent_funding_receipt_rate,
        trained_with_funding_receipt_rate=trained_with_funding_receipt_rate,
        opponent_second_worker_productive_rate=opponent_second_worker_productive_rate,
        mean_opponent_second_worker_productive_actions=(
            mean_opponent_second_worker_productive_actions
        ),
        max_opponent_workers=max_opponent_workers,
        opponent_third_worker_training_rate=opponent_third_worker_training_rate,
        median_opponent_third_worker_training_turn=(
            median_opponent_third_worker_training_turn
        ),
        third_trained_with_fresh_funding_receipt_rate=(
            third_trained_with_fresh_funding_receipt_rate
        ),
        opponent_third_worker_productive_rate=opponent_third_worker_productive_rate,
        mean_opponent_third_worker_productive_actions=(
            mean_opponent_third_worker_productive_actions
        ),
        mean_opponent_funded_training_events=mean_opponent_funded_training_events,
        rows=rows,
    )


def paired_teacher_turn_delta(evaluation: Evaluation, teacher: dict) -> float | None:
    learned = {row["seed"]: row for row in evaluation.rows if row["success"]}
    reference = {
        row["seed"]: row for row in teacher["episodes_detail"] if row["success"]
    }
    shared = sorted(set(learned) & set(reference))
    if not shared:
        return None
    return float(
        np.median([learned[seed]["turns"] - reference[seed]["turns"] for seed in shared])
    )


def level5_mechanism_gate(evaluation: Evaluation) -> bool:
    """Preserve the recurrent D11 opponent interaction while training the actor."""

    return (
        evaluation.opponent_training_rate is not None
        and evaluation.opponent_training_rate >= 0.98
        and evaluation.opponent_third_worker_training_rate is not None
        and evaluation.opponent_third_worker_training_rate >= 0.85
        and evaluation.trained_with_funding_receipt_rate == 1.0
        and evaluation.third_trained_with_fresh_funding_receipt_rate == 1.0
        and evaluation.opponent_second_worker_productive_rate is not None
        and evaluation.opponent_second_worker_productive_rate >= 0.98
        and evaluation.opponent_third_worker_productive_rate is not None
        and evaluation.opponent_third_worker_productive_rate >= 0.80
        and evaluation.opponent_crop_creation_rate is not None
        and evaluation.opponent_crop_creation_rate >= 0.95
        and evaluation.opponent_renewable_harvest_rate is not None
        and evaluation.opponent_renewable_harvest_rate >= 0.80
        and evaluation.opponent_crop_destruction_rate is not None
        and evaluation.opponent_crop_destruction_rate >= 0.95
        and evaluation.opponent_crop_destruction_at_least_two_rate is not None
        and evaluation.opponent_crop_destruction_at_least_two_rate >= 0.85
        and evaluation.opponent_crop_destruction_at_least_three_rate is not None
        and evaluation.opponent_crop_destruction_at_least_three_rate >= 0.70
        and evaluation.max_opponent_workers is not None
        and evaluation.max_opponent_workers <= 3
        and evaluation.max_opponent_crop_destructions is not None
        and evaluation.max_opponent_crop_destructions <= 3
    )


def validate_evaluation_baseline(
    baseline: dict, *, label: str, seed_base: int, episodes: int
) -> None:
    if (
        baseline.get("exact_seed_interval") is not True
        or baseline.get("seed_base") != seed_base
        or baseline.get("seed_stop_exclusive") != seed_base + episodes
        or baseline.get("episodes") != episodes
    ):
        raise SystemExit(
            f"{label} baseline must cover the exact learned-evaluation seed interval"
        )


def write_evaluation(path: Path, evaluation: Evaluation, extra: dict) -> None:
    payload = {**asdict(evaluation), **extra}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def explained_variance(prediction: np.ndarray, target: np.ndarray) -> float:
    variance = np.var(target)
    if variance == 0:
        return float("nan")
    return float(1.0 - np.var(target - prediction) / variance)


def legal_teacher_auxiliary_loss(
    masked_logits: torch.Tensor,
    legal: torch.Tensor,
    teacher_actions: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Cross-entropy on teacher commands defined in the learner's current state.

    A scripted teacher can encounter off-teacher states where its preferred recovery
    command is not legal.  Such rows have no valid supervised target and must not feed
    the finite-minimum mask value into cross-entropy.
    """

    teacher_legal = legal.gather(1, teacher_actions[:, None]).squeeze(1)
    if not teacher_legal.any():
        zero = masked_logits.sum() * 0.0
        return zero, zero.detach(), teacher_legal
    valid_logits = masked_logits[teacher_legal]
    valid_actions = teacher_actions[teacher_legal]
    loss = F.cross_entropy(valid_logits, valid_actions)
    accuracy = (valid_logits.argmax(dim=1) == valid_actions).float().mean()
    return loss, accuracy, teacher_legal


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curriculum-level", type=int, choices=(1, 2, 3, 4, 5), default=1)
    parser.add_argument("--run-name", default="run1")
    parser.add_argument("--model-seed", type=int, default=7301)
    parser.add_argument("--train-seed-base", type=int, default=1_000_000)
    parser.add_argument("--eval-seed-base", type=int, default=2_000_000)
    parser.add_argument("--num-envs", type=int, default=100)
    parser.add_argument("--rollout-steps", type=int, default=100)
    parser.add_argument("--total-transitions", type=int, default=1_000_000)
    parser.add_argument("--stage-a-transitions", type=int, default=250_000)
    parser.add_argument("--eval-episodes", type=int, default=1000)
    parser.add_argument("--max-turns", type=int)
    parser.add_argument("--update-epochs", type=int, default=4)
    parser.add_argument("--minibatch-size", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=2.5e-4)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--gae-lambda", type=float, default=0.95)
    parser.add_argument("--clip-coef", type=float, default=0.2)
    parser.add_argument("--entropy-coef", type=float, default=0.01)
    parser.add_argument("--value-coef", type=float, default=0.5)
    parser.add_argument("--reward-scale", type=float, default=0.01)
    parser.add_argument("--max-grad-norm", type=float, default=0.5)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--target-kl", type=float, default=0.03)
    parser.add_argument("--no-stage-a-stop", action="store_true")
    parser.add_argument("--initial-checkpoint")
    parser.add_argument("--initial-weights-npz")
    parser.add_argument(
        "--level5-opponent-mode",
        choices=LEVEL5_OPPONENT_MODES,
        default="natural-forager",
    )
    parser.add_argument(
        "--gate-profile",
        choices=("scratch", "bc", "level2", "level3", "level4", "level5"),
        default="scratch",
    )
    parser.add_argument("--protocol", default=str(PROTOCOL))
    parser.add_argument("--random-baseline", default=str(RANDOM_BASELINE))
    parser.add_argument("--teacher-baseline", default=str(TEACHER_BASELINE))
    parser.add_argument("--teacher-aux-coef", type=float, default=0.0)
    args = parser.parse_args()
    if args.max_turns is None:
        args.max_turns = 240 if args.curriculum_level in (2, 3, 4, 5) else 180
    if args.gate_profile == "level2" and args.curriculum_level != 2:
        raise SystemExit("the level2 gate profile requires --curriculum-level 2")
    if args.gate_profile == "level3" and args.curriculum_level != 3:
        raise SystemExit("the level3 gate profile requires --curriculum-level 3")
    if args.gate_profile == "level4" and args.curriculum_level != 4:
        raise SystemExit("the level4 gate profile requires --curriculum-level 4")
    if args.gate_profile == "level5" and args.curriculum_level != 5:
        raise SystemExit("the level5 gate profile requires --curriculum-level 5")
    protocol_path = Path(args.protocol)
    random_baseline_path = Path(args.random_baseline)
    teacher_baseline_path = Path(args.teacher_baseline)

    batch_size = args.num_envs * args.rollout_steps
    if args.total_transitions % batch_size:
        raise SystemExit("total transitions must be divisible by vector rollout batch")
    if args.stage_a_transitions % batch_size:
        raise SystemExit("Stage A transitions must be divisible by vector rollout batch")
    if batch_size % args.minibatch_size:
        raise SystemExit("rollout batch must be divisible by minibatch size")
    if args.teacher_aux_coef < 0:
        raise SystemExit("teacher auxiliary coefficient must be nonnegative")
    if args.initial_checkpoint and args.initial_weights_npz:
        raise SystemExit(
            "choose only one of --initial-checkpoint and --initial-weights-npz"
        )
    if (
        not protocol_path.exists()
        or not random_baseline_path.exists()
        or not teacher_baseline_path.exists()
    ):
        raise SystemExit("frozen protocol and baseline artifacts must exist before training")

    torch.manual_seed(args.model_seed)
    np.random.seed(args.model_seed)
    device = resolve_device(args.device)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(args.model_seed)
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(4, args.threads))
    torch.backends.mkldnn.enabled = True
    rng = np.random.default_rng(args.model_seed)

    random_baseline = json.loads(random_baseline_path.read_text())
    teacher_baseline = json.loads(teacher_baseline_path.read_text())
    validate_evaluation_baseline(
        random_baseline,
        label="random",
        seed_base=args.eval_seed_base,
        episodes=args.eval_episodes,
    )
    validate_evaluation_baseline(
        teacher_baseline,
        label="teacher",
        seed_base=args.eval_seed_base,
        episodes=args.eval_episodes,
    )
    model = SpatialActorCritic()
    initial_checkpoint_sha256 = None
    initial_weights_npz_sha256 = None
    if args.initial_checkpoint:
        initial_path = Path(args.initial_checkpoint)
        saved = torch.load(initial_path, map_location="cpu", weights_only=False)
        model.load_state_dict(saved["model"])
        initial_checkpoint_sha256 = sha256(initial_path)
    if args.initial_weights_npz:
        initial_weights_path = Path(args.initial_weights_npz)
        if not initial_weights_path.exists():
            raise SystemExit(
                f"initial model-weight archive does not exist: {initial_weights_path}"
            )
        load_model_weights_npz(model, initial_weights_path)
        initial_weights_npz_sha256 = sha256(initial_weights_path)
    model.to(device)
    parameter_count = sum(parameter.numel() for parameter in model.parameters())
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, eps=1e-5)

    observation_buffer = np.empty(
        (
            args.rollout_steps,
            args.num_envs,
            OBS_CHANNELS,
            OBS_HEIGHT,
            OBS_WIDTH,
        ),
        dtype=np.uint8,
    )
    mask_buffer = np.empty(
        (
            args.rollout_steps,
            args.num_envs,
            ACTION_PLANES,
            OBS_HEIGHT,
            OBS_WIDTH,
        ),
        dtype=np.uint8,
    )
    action_buffer = np.empty((args.rollout_steps, args.num_envs), dtype=np.int64)
    logprob_buffer = np.empty((args.rollout_steps, args.num_envs), dtype=np.float32)
    reward_buffer = np.empty((args.rollout_steps, args.num_envs), dtype=np.float32)
    done_buffer = np.empty((args.rollout_steps, args.num_envs), dtype=np.float32)
    value_buffer = np.empty((args.rollout_steps, args.num_envs), dtype=np.float32)
    teacher_action_buffer = (
        np.empty((args.rollout_steps, args.num_envs), dtype=np.int64)
        if args.teacher_aux_coef > 0
        else None
    )

    total_updates = args.total_transitions // batch_size
    stage_a_update = args.stage_a_transitions // batch_size
    global_step = 0
    start_wall = time.perf_counter()
    start_cpu = time.process_time()
    episode_window: list[dict] = []
    logs: list[dict] = []
    evaluations: list[dict] = []
    stage_a_passed: bool | None = None
    stage_b_passed: bool | None = None
    output_prefix = ANALYSIS / f"curriculum-level{args.curriculum_level}-{args.run_name}"

    config = {
        **vars(args),
        "batch_size": batch_size,
        "parameter_count": parameter_count,
        "torch_version": torch.__version__,
        "protocol_sha256": sha256(protocol_path),
        "random_baseline_sha256": sha256(random_baseline_path),
        "teacher_baseline_sha256": sha256(teacher_baseline_path),
        "initial_checkpoint_sha256": initial_checkpoint_sha256,
        "initial_weights_npz_sha256": initial_weights_npz_sha256,
        "teacher_aux_invalid_label_policy": "skip_undefined_off_teacher_targets",
        "resolved_device": str(device),
        "cuda_device_name": (
            torch.cuda.get_device_name(device) if device.type == "cuda" else None
        ),
    }
    print(json.dumps({"event": "start", **config}, sort_keys=True), flush=True)

    env_class = {
        1: Level1VecEnv,
        2: Level2VecEnv,
        3: Level3VecEnv,
        4: Level4VecEnv,
        5: level5_env_class(args.level5_opponent_mode),
    }[args.curriculum_level]
    with env_class(
        args.num_envs, args.train_seed_base, max_turns=args.max_turns
    ) as env:
        for update in range(1, total_updates + 1):
            update_start = time.perf_counter()
            rollout_start = update_start
            for step_index in range(args.rollout_steps):
                np.copyto(observation_buffer[step_index], env.obs)
                np.copyto(mask_buffer[step_index], env.masks)
                if teacher_action_buffer is not None:
                    teacher_action_buffer[step_index] = env.teacher_actions()
                with torch.no_grad():
                    actions, logprobs, _, values = model.action_and_value(
                        torch.from_numpy(env.obs).to(device),
                        torch.from_numpy(env.masks).to(device),
                    )
                actions_np = actions.cpu().numpy()
                action_buffer[step_index] = actions_np
                logprob_buffer[step_index] = logprobs.cpu().numpy()
                value_buffer[step_index] = values.cpu().numpy()
                _, _, rewards, info = env.step(actions_np.astype(np.int32, copy=False))
                reward_buffer[step_index] = rewards * args.reward_scale
                done_buffer[step_index] = info.dones
                global_step += args.num_envs
                for index in np.flatnonzero(info.dones):
                    row = {
                        "success": int(info.successes[index]),
                        "turns": int(info.turns[index]),
                        "return": float(info.returns[index]),
                        "height": int(info.heights[index]),
                    }
                    if args.curriculum_level == 1:
                        row["initial_deficit"] = int(info.initial_deficits[index])
                    elif args.curriculum_level == 2:
                        row["initial_deficit"] = int(
                            info.initial_total_deficits[index]
                        )
                        row["recipe_id"] = int(info.recipe_ids[index])
                    else:
                        row["initial_deficit"] = int(
                            info.initial_total_deficits[index]
                        )
                        row["created_crop"] = bool(info.created_crops[index])
                        row["renewable_harvests"] = int(
                            info.renewable_harvests[index]
                        )
                        row["training_turn"] = int(info.training_turns[index])
                        row["score_gain"] = int(info.score_gains[index])
                        if args.curriculum_level in (4, 5):
                            row["recipe_id"] = int(info.recipe_ids[index])
                        if args.curriculum_level == 5:
                            row["opponent_score"] = int(info.opponent_scores[index])
                            row["opponent_workers"] = int(info.opponent_workers[index])
                    episode_window.append(row)
            rollout_elapsed = time.perf_counter() - rollout_start

            with torch.no_grad():
                _, next_value = model(torch.from_numpy(env.obs).to(device))
            next_value_np = next_value.cpu().numpy()
            advantages = np.zeros_like(reward_buffer)
            last_advantage = np.zeros(args.num_envs, dtype=np.float32)
            for step_index in reversed(range(args.rollout_steps)):
                next_nonterminal = 1.0 - done_buffer[step_index]
                next_values = (
                    next_value_np
                    if step_index == args.rollout_steps - 1
                    else value_buffer[step_index + 1]
                )
                delta = (
                    reward_buffer[step_index]
                    + args.gamma * next_values * next_nonterminal
                    - value_buffer[step_index]
                )
                last_advantage = (
                    delta
                    + args.gamma
                    * args.gae_lambda
                    * next_nonterminal
                    * last_advantage
                )
                advantages[step_index] = last_advantage
            returns = advantages + value_buffer

            flat_observations = observation_buffer.reshape(
                batch_size, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH
            )
            flat_masks = mask_buffer.reshape(
                batch_size, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH
            )
            flat_actions = action_buffer.reshape(batch_size)
            flat_logprobs = logprob_buffer.reshape(batch_size)
            flat_advantages = advantages.reshape(batch_size)
            flat_returns = returns.reshape(batch_size)
            flat_values = value_buffer.reshape(batch_size)
            flat_teacher_actions = (
                teacher_action_buffer.reshape(batch_size)
                if teacher_action_buffer is not None
                else None
            )
            teacher_legal_rate = None
            teacher_invalid_labels = None
            if flat_teacher_actions is not None:
                teacher_rows = np.arange(batch_size)
                teacher_legal_labels = flat_masks.reshape(batch_size, -1)[
                    teacher_rows, flat_teacher_actions
                ] != 0
                teacher_invalid_labels = int((~teacher_legal_labels).sum())
                teacher_legal_rate = float(teacher_legal_labels.mean())
            indices = np.arange(batch_size)
            clip_fractions: list[float] = []
            approx_kl = 0.0
            policy_loss_value = value_loss_value = entropy_value = 0.0
            teacher_loss_value = teacher_accuracy_value = None
            epochs_run = 0
            for epoch in range(args.update_epochs):
                rng.shuffle(indices)
                for start in range(0, batch_size, args.minibatch_size):
                    minibatch = indices[start : start + args.minibatch_size]
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
                            float(((ratio - 1.0).abs() > args.clip_coef).float().mean())
                        )

                    mb_advantages = torch.from_numpy(
                        flat_advantages[minibatch]
                    ).to(device)
                    mb_advantages = (mb_advantages - mb_advantages.mean()) / (
                        mb_advantages.std() + 1e-8
                    )
                    policy_loss_1 = -mb_advantages * ratio
                    policy_loss_2 = -mb_advantages * ratio.clamp(
                        1.0 - args.clip_coef, 1.0 + args.clip_coef
                    )
                    policy_loss = torch.maximum(policy_loss_1, policy_loss_2).mean()
                    value_loss = 0.5 * (
                        new_value
                        - torch.from_numpy(flat_returns[minibatch]).to(device)
                    ).pow(2).mean()
                    entropy_loss = entropy.mean()
                    loss = (
                        policy_loss
                        - args.entropy_coef * entropy_loss
                        + args.value_coef * value_loss
                    )
                    if flat_teacher_actions is not None:
                        mb_teacher_actions = torch.from_numpy(
                            flat_teacher_actions[minibatch]
                        ).to(device)
                        teacher_loss, teacher_accuracy, _ = legal_teacher_auxiliary_loss(
                            masked_logits,
                            legal,
                            mb_teacher_actions,
                        )
                        loss = loss + args.teacher_aux_coef * teacher_loss
                        teacher_loss_value = float(teacher_loss.detach())
                        teacher_accuracy_value = float(teacher_accuracy.detach())
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)
                    optimizer.step()
                    policy_loss_value = float(policy_loss.detach())
                    value_loss_value = float(value_loss.detach())
                    entropy_value = float(entropy_loss.detach())
                epochs_run = epoch + 1
                if args.target_kl > 0 and approx_kl > args.target_kl:
                    break

            fraction = update / total_updates
            optimizer.param_groups[0]["lr"] = args.learning_rate * (1.0 - fraction)
            update_elapsed = time.perf_counter() - update_start
            recent = episode_window[-1000:]
            log = {
                "event": "update",
                "update": update,
                "global_step": global_step,
                "rollout_sps": batch_size / rollout_elapsed,
                "update_sps": batch_size / update_elapsed,
                "episodes_recent": len(recent),
                "success_rate_recent": (
                    sum(row["success"] for row in recent) / len(recent) if recent else None
                ),
                "median_turn_recent": (
                    float(np.median([row["turns"] for row in recent if row["success"]]))
                    if any(row["success"] for row in recent)
                    else None
                ),
                "mean_return_recent": (
                    float(np.mean([row["return"] for row in recent])) if recent else None
                ),
                "policy_loss": policy_loss_value,
                "value_loss": value_loss_value,
                "entropy": entropy_value,
                "teacher_loss": teacher_loss_value,
                "teacher_accuracy": teacher_accuracy_value,
                "teacher_legal_rate": teacher_legal_rate,
                "teacher_invalid_labels": teacher_invalid_labels,
                "approx_kl": approx_kl,
                "clip_fraction": float(np.mean(clip_fractions)),
                "explained_variance": explained_variance(flat_values, flat_returns),
                "epochs_run": epochs_run,
                "learning_rate": optimizer.param_groups[0]["lr"],
            }
            logs.append(log)
            print(json.dumps(log, sort_keys=True), flush=True)

            if update in (stage_a_update, total_updates):
                evaluation = evaluate(
                    model,
                    seed_base=args.eval_seed_base,
                    episodes=args.eval_episodes,
                    num_envs=args.num_envs,
                    curriculum_level=args.curriculum_level,
                    max_turns=args.max_turns,
                    level5_opponent_mode=args.level5_opponent_mode,
                )
                teacher_delta = paired_teacher_turn_delta(evaluation, teacher_baseline)
                nontrivial = [
                    row for row in evaluation.rows if row["initial_deficit"] > 0
                ]
                nontrivial_success_rate = (
                    sum(row["success"] for row in nontrivial) / len(nontrivial)
                )
                height_floor = min(
                    bucket["success_rate"] for bucket in evaluation.by_height.values()
                )
                recipe_floor = (
                    min(
                        bucket["success_rate"]
                        for bucket in (evaluation.by_recipe or {}).values()
                        if bucket["episodes"]
                    )
                    if evaluation.by_recipe
                    else None
                )
                created_crop_rate = evaluation.created_crop_rate
                renewable_harvest_rate = evaluation.renewable_harvest_rate
                if update == stage_a_update:
                    if args.gate_profile == "level5":
                        gate = (
                            evaluation.success_rate >= 0.85
                            and nontrivial_success_rate >= 0.82
                            and recipe_floor is not None
                            and recipe_floor >= 0.75
                            and height_floor >= 0.78
                            and created_crop_rate is not None
                            and created_crop_rate >= 0.80
                            and renewable_harvest_rate is not None
                            and renewable_harvest_rate >= 0.90
                            and teacher_delta is not None
                            and teacher_delta <= 35.0
                            and level5_mechanism_gate(evaluation)
                        )
                    elif args.gate_profile == "level4":
                        gate = (
                            evaluation.success_rate >= 0.60
                            and nontrivial_success_rate >= 0.55
                            and recipe_floor is not None
                            and recipe_floor >= 0.45
                            and height_floor >= 0.50
                            and created_crop_rate is not None
                            and created_crop_rate >= 0.65
                            and renewable_harvest_rate is not None
                            and renewable_harvest_rate >= 0.55
                            and teacher_delta is not None
                            and teacher_delta <= 55.0
                        )
                    elif args.gate_profile == "level3":
                        gate = (
                            evaluation.success_rate >= 0.65
                            and nontrivial_success_rate >= 0.60
                            and height_floor >= 0.55
                            and created_crop_rate is not None
                            and created_crop_rate >= 0.70
                            and renewable_harvest_rate is not None
                            and renewable_harvest_rate >= 0.60
                            and teacher_delta is not None
                            and teacher_delta <= 45.0
                        )
                    elif args.gate_profile == "level2":
                        gate = (
                            evaluation.success_rate >= 0.70
                            and nontrivial_success_rate >= 0.65
                            and recipe_floor is not None
                            and recipe_floor >= 0.60
                            and height_floor >= 0.55
                            and teacher_delta is not None
                            and teacher_delta <= 30.0
                        )
                    elif args.gate_profile == "bc":
                        gate = (
                            evaluation.success_rate >= 0.70
                            and nontrivial_success_rate >= 0.65
                            and height_floor >= 0.55
                            and teacher_delta is not None
                            and teacher_delta <= 25.0
                        )
                    else:
                        gate = (
                            evaluation.success_rate >= 0.40
                            and evaluation.success_rate
                            >= random_baseline["success_rate"] + 0.20
                        )
                    stage_a_passed = gate
                    gate_name = {
                        "level2": "L2A",
                        "level3": "L3A",
                        "level4": "L4A",
                        "level5": "L5A",
                    }.get(args.gate_profile, "L1A")
                else:
                    if args.gate_profile == "level5":
                        gate = (
                            evaluation.success_rate >= 0.90
                            and nontrivial_success_rate >= 0.88
                            and recipe_floor is not None
                            and recipe_floor >= 0.82
                            and height_floor >= 0.85
                            and created_crop_rate is not None
                            and created_crop_rate >= 0.90
                            and renewable_harvest_rate is not None
                            and renewable_harvest_rate >= 0.95
                            and teacher_delta is not None
                            and teacher_delta <= 30.0
                            and level5_mechanism_gate(evaluation)
                        )
                    elif args.gate_profile == "level4":
                        gate = (
                            evaluation.success_rate >= 0.88
                            and nontrivial_success_rate >= 0.83
                            and recipe_floor is not None
                            and recipe_floor >= 0.75
                            and height_floor >= 0.75
                            and created_crop_rate is not None
                            and created_crop_rate >= 0.90
                            and renewable_harvest_rate is not None
                            and renewable_harvest_rate >= 0.87
                            and evaluation.success_rate
                            >= random_baseline["success_rate"] + 0.50
                            and teacher_delta is not None
                            and teacher_delta <= 35.0
                        )
                    elif args.gate_profile == "level3":
                        gate = (
                            evaluation.success_rate >= 0.90
                            and nontrivial_success_rate >= 0.85
                            and height_floor >= 0.80
                            and created_crop_rate is not None
                            and created_crop_rate >= 0.92
                            and renewable_harvest_rate is not None
                            and renewable_harvest_rate >= 0.90
                            and evaluation.success_rate
                            >= random_baseline["success_rate"] + 0.50
                            and teacher_delta is not None
                            and teacher_delta <= 30.0
                        )
                    elif args.gate_profile == "level2":
                        gate = (
                            evaluation.success_rate >= 0.90
                            and nontrivial_success_rate >= 0.85
                            and recipe_floor is not None
                            and recipe_floor >= 0.80
                            and height_floor >= 0.80
                            and evaluation.success_rate
                            >= random_baseline["success_rate"] + 0.40
                            and teacher_delta is not None
                            and teacher_delta <= 20.0
                        )
                    elif args.gate_profile == "bc":
                        gate = (
                            evaluation.success_rate >= 0.85
                            and nontrivial_success_rate >= 0.80
                            and teacher_delta is not None
                            and teacher_delta <= 15.0
                            and height_floor >= 0.75
                        )
                    else:
                        gate = (
                            evaluation.success_rate >= 0.70
                            and evaluation.success_rate
                            >= random_baseline["success_rate"] + 0.30
                            and teacher_delta is not None
                            and teacher_delta <= 25.0
                            and height_floor >= 0.55
                        )
                    stage_b_passed = gate
                    gate_name = {
                        "level2": "L2B",
                        "level3": "L3B",
                        "level4": "L4B",
                        "level5": "L5B",
                    }.get(args.gate_profile, "L1B")
                evaluation_extra = {
                    "gate": gate_name,
                    "gate_passed": gate,
                    "global_step": global_step,
                    "random_success_rate": random_baseline["success_rate"],
                    "teacher_success_rate": teacher_baseline["success_rate"],
                    "nontrivial_success_rate": nontrivial_success_rate,
                    "paired_teacher_median_turn_delta": teacher_delta,
                    "height_success_floor": height_floor,
                    "recipe_success_floor": recipe_floor,
                    "created_crop_rate": created_crop_rate,
                    "renewable_harvest_rate": renewable_harvest_rate,
                    "median_training_turn": evaluation.median_training_turn,
                    "median_score_gain": evaluation.median_score_gain,
                    "level5_mechanism_gate": (
                        level5_mechanism_gate(evaluation)
                        if args.curriculum_level == 5
                        else None
                    ),
                }
                evaluation_path = Path(
                    f"{output_prefix}-{gate_name.lower()}-evaluation.json"
                )
                write_evaluation(evaluation_path, evaluation, evaluation_extra)
                evaluations.append(
                    {
                        **{key: value for key, value in asdict(evaluation).items() if key != "rows"},
                        **evaluation_extra,
                        "path": str(evaluation_path.relative_to(ROOT)),
                    }
                )
                checkpoint = {
                    "model": model.state_dict(),
                    "optimizer": optimizer.state_dict(),
                    "config": config,
                    "global_step": global_step,
                    "evaluation": evaluations[-1],
                }
                torch.save(checkpoint, Path(f"{output_prefix}-{gate_name.lower()}.pt"))
                print(
                    json.dumps({"event": "evaluation", **evaluations[-1]}, sort_keys=True),
                    flush=True,
                )
                if (
                    gate_name in ("L1A", "L2A", "L3A", "L4A", "L5A")
                    and not gate
                    and not args.no_stage_a_stop
                ):
                    break

    elapsed_wall = time.perf_counter() - start_wall
    elapsed_cpu = time.process_time() - start_cpu
    aggregate_cpu_percent = 100.0 * elapsed_cpu / elapsed_wall / max(os.cpu_count() or 1, 1)
    summary = {
        "run_name": args.run_name,
        "config": config,
        "global_step": global_step,
        "updates_completed": len(logs),
        "elapsed_wall_seconds": elapsed_wall,
        "elapsed_cpu_seconds": elapsed_cpu,
        "aggregate_host_cpu_percent": aggregate_cpu_percent,
        "overall_transitions_per_second": global_step / elapsed_wall,
        "stage_a_passed": stage_a_passed,
        "stage_b_passed": stage_b_passed,
        "teacher_aux_label_stats": (
            {
                "labels": batch_size * len(logs),
                "invalid_labels": sum(
                    row["teacher_invalid_labels"] or 0 for row in logs
                ),
                "legal_rate": 1.0
                - sum(row["teacher_invalid_labels"] or 0 for row in logs)
                / (batch_size * len(logs)),
            }
            if teacher_action_buffer is not None and logs
            else None
        ),
        "evaluations": evaluations,
        "logs": logs,
    }
    summary_path = Path(f"{output_prefix}-training-summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"event": "complete", **summary}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
