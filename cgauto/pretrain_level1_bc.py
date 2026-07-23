#!/usr/bin/env python3
"""Behavior-clone a deterministic compact-policy curriculum teacher."""

from __future__ import annotations

import argparse
import collections
import json
import math
import os
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from cgauto.rl_level1_env import (
    ACTION_PLANES,
    OBS_CHANNELS,
    OBS_HEIGHT,
    OBS_WIDTH,
    Level1VecEnv,
)
from cgauto.rl_level2_env import Level2VecEnv
from cgauto.rl_level3_env import Level3VecEnv
from cgauto.rl_level4_env import Level4VecEnv
from cgauto.train_level1_ppo import (
    ANALYSIS,
    LEVEL5_OPPONENT_MODES,
    SpatialActorCritic,
    evaluate,
    level5_env_class,
    level5_mechanism_gate,
    paired_teacher_turn_delta,
    sha256,
    validate_evaluation_baseline,
)


PROTOCOL = ANALYSIS / "curriculum-level1-bfs-bc-protocol-2026-07-19.md"
DEBUG_TEACHER = ANALYSIS / "curriculum-level1-v2-teacher-debug5000-5999-exact.json"
CELLS = OBS_HEIGHT * OBS_WIDTH


def masked_cross_entropy(
    model: SpatialActorCritic,
    observations: torch.Tensor,
    masks: torch.Tensor,
    labels: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    logits, _ = model(observations)
    legal = masks.reshape(masks.shape[0], -1).bool()
    masked_logits = logits.masked_fill(~legal, torch.finfo(logits.dtype).min)
    loss = F.cross_entropy(masked_logits, labels)
    accuracy = (masked_logits.argmax(dim=1) == labels).float().mean()
    return loss, accuracy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--curriculum-level", type=int, choices=(1, 2, 3, 4, 5), default=1
    )
    parser.add_argument("--run-name", default="bc-debug")
    parser.add_argument("--model-seed", type=int, default=41)
    parser.add_argument("--train-seed-base", type=int, default=0)
    parser.add_argument("--eval-seed-base", type=int, default=5000)
    parser.add_argument("--samples", type=int, default=100_000)
    parser.add_argument("--num-envs", type=int, default=100)
    parser.add_argument("--chunk-steps", type=int, default=10)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--minibatch-size", type=int, default=1000)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--final-learning-rate", type=float, default=1e-4)
    parser.add_argument("--eval-episodes", type=int, default=1000)
    parser.add_argument("--max-turns", type=int)
    parser.add_argument("--threads", type=int, default=14)
    parser.add_argument("--protocol", default=str(PROTOCOL))
    parser.add_argument("--teacher-baseline", default=str(DEBUG_TEACHER))
    parser.add_argument("--initial-checkpoint")
    parser.add_argument(
        "--level5-opponent-mode",
        choices=LEVEL5_OPPONENT_MODES,
        default="natural-forager",
    )
    args = parser.parse_args()
    if args.max_turns is None:
        args.max_turns = 240 if args.curriculum_level in (2, 3, 4, 5) else 180
    protocol_path = Path(args.protocol)
    teacher_baseline_path = Path(args.teacher_baseline)

    chunk_size = args.num_envs * args.chunk_steps
    if args.samples % chunk_size:
        raise SystemExit("samples must be divisible by num_envs * chunk_steps")
    if chunk_size % args.minibatch_size:
        raise SystemExit("chunk size must be divisible by minibatch size")
    if not protocol_path.exists() or not teacher_baseline_path.exists():
        raise SystemExit("frozen protocol and exact teacher control are required")
    teacher_baseline = json.loads(teacher_baseline_path.read_text())
    validate_evaluation_baseline(
        teacher_baseline,
        label="teacher",
        seed_base=args.eval_seed_base,
        episodes=args.eval_episodes,
    )

    torch.manual_seed(args.model_seed)
    np.random.seed(args.model_seed)
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(4, args.threads))
    rng = np.random.default_rng(args.model_seed)
    model = SpatialActorCritic()
    initial_checkpoint_sha256 = None
    if args.initial_checkpoint:
        initial_path = Path(args.initial_checkpoint)
        if not initial_path.exists():
            raise SystemExit(f"initial checkpoint does not exist: {initial_path}")
        saved = torch.load(initial_path, map_location="cpu", weights_only=False)
        model.load_state_dict(saved["model"])
        initial_checkpoint_sha256 = sha256(initial_path)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate, eps=1e-5)
    chunks = args.samples // chunk_size
    observations = np.empty(
        (chunk_size, OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
    )
    masks = np.empty(
        (chunk_size, ACTION_PLANES, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8
    )
    labels = np.empty(chunk_size, dtype=np.int64)
    label_planes = collections.Counter()
    logs: list[dict] = []
    teacher_episodes = collections.Counter()
    start_wall = time.perf_counter()
    start_cpu = time.process_time()

    config = {
        **vars(args),
        "chunk_size": chunk_size,
        "chunks": chunks,
        "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "torch_version": torch.__version__,
        "protocol_sha256": sha256(protocol_path),
        "teacher_baseline_sha256": sha256(teacher_baseline_path),
        "initial_checkpoint_sha256": initial_checkpoint_sha256,
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
        for chunk in range(chunks):
            collect_start = time.perf_counter()
            for step in range(args.chunk_steps):
                offset = step * args.num_envs
                observations[offset : offset + args.num_envs] = env.obs
                masks[offset : offset + args.num_envs] = env.masks
                teacher_actions = env.teacher_actions().astype(np.int64)
                labels[offset : offset + args.num_envs] = teacher_actions
                label_planes.update((teacher_actions // CELLS).tolist())
                _, _, _, info = env.step(
                    teacher_actions.astype(np.int32, copy=False)
                )
                for index in np.flatnonzero(info.dones):
                    teacher_episodes["episodes"] += 1
                    teacher_episodes["successes"] += int(info.successes[index])
            collect_elapsed = time.perf_counter() - collect_start

            progress = (chunk + 1) / chunks
            learning_rate = args.final_learning_rate + (
                args.learning_rate - args.final_learning_rate
            ) * 0.5 * (1.0 + math.cos(math.pi * progress))
            optimizer.param_groups[0]["lr"] = learning_rate
            indices = np.arange(chunk_size)
            losses: list[float] = []
            accuracies: list[float] = []
            train_start = time.perf_counter()
            for _ in range(args.epochs):
                rng.shuffle(indices)
                for start in range(0, chunk_size, args.minibatch_size):
                    selected = indices[start : start + args.minibatch_size]
                    loss, accuracy = masked_cross_entropy(
                        model,
                        torch.from_numpy(observations[selected]),
                        torch.from_numpy(masks[selected]),
                        torch.from_numpy(labels[selected]),
                    )
                    optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                    losses.append(float(loss.detach()))
                    accuracies.append(float(accuracy.detach()))
            train_elapsed = time.perf_counter() - train_start
            log = {
                "event": "chunk",
                "chunk": chunk + 1,
                "samples": (chunk + 1) * chunk_size,
                "loss": float(np.mean(losses)),
                "accuracy": float(np.mean(accuracies)),
                "learning_rate": learning_rate,
                "collect_sps": chunk_size / collect_elapsed,
                "train_samples_per_second": args.epochs * chunk_size / train_elapsed,
            }
            logs.append(log)
            if chunk == 0 or (chunk + 1) % 10 == 0 or chunk + 1 == chunks:
                print(json.dumps(log, sort_keys=True), flush=True)

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
    nontrivial = [row for row in evaluation.rows if row["initial_deficit"] > 0]
    nontrivial_success_rate = sum(row["success"] for row in nontrivial) / len(nontrivial)
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
    if args.curriculum_level == 5:
        functional_gate = (
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
            and all(
                not row["success"] or row["turns"] >= 180
                for row in evaluation.rows
            )
            and level5_mechanism_gate(evaluation)
        )
    elif args.curriculum_level == 4:
        functional_gate = (
            evaluation.success_rate >= 0.70
            and nontrivial_success_rate >= 0.65
            and recipe_floor is not None
            and recipe_floor >= 0.55
            and height_floor >= 0.60
            and created_crop_rate is not None
            and created_crop_rate >= 0.75
            and renewable_harvest_rate is not None
            and renewable_harvest_rate >= 0.65
            and teacher_delta is not None
            and teacher_delta <= 45.0
        )
    elif args.curriculum_level == 3:
        functional_gate = (
            evaluation.success_rate >= 0.75
            and nontrivial_success_rate >= 0.70
            and height_floor >= 0.65
            and created_crop_rate is not None
            and created_crop_rate >= 0.80
            and renewable_harvest_rate is not None
            and renewable_harvest_rate >= 0.70
            and teacher_delta is not None
            and teacher_delta <= 35.0
        )
    elif args.curriculum_level == 2:
        functional_gate = (
            evaluation.success_rate >= 0.80
            and nontrivial_success_rate >= 0.75
            and recipe_floor is not None
            and recipe_floor >= 0.70
            and height_floor >= 0.65
            and teacher_delta is not None
            and teacher_delta <= 20.0
        )
    else:
        functional_gate = (
            evaluation.success_rate >= 0.80
            and nontrivial_success_rate >= 0.75
            and height_floor >= 0.65
            and teacher_delta is not None
            and teacher_delta <= 15.0
        )
    output_prefix = ANALYSIS / f"curriculum-level{args.curriculum_level}-{args.run_name}"
    checkpoint_path = Path(f"{output_prefix}.pt")
    torch.save(
        {
            "model": model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "config": config,
            "evaluation": {
                "success_rate": evaluation.success_rate,
                "nontrivial_success_rate": nontrivial_success_rate,
                "height_floor": height_floor,
                "recipe_floor": recipe_floor,
                "created_crop_rate": created_crop_rate,
                "renewable_harvest_rate": renewable_harvest_rate,
                "median_training_turn": evaluation.median_training_turn,
                "median_score_gain": evaluation.median_score_gain,
                "paired_teacher_median_turn_delta": teacher_delta,
                "functional_gate": functional_gate,
                "level5_mechanism_gate": (
                    level5_mechanism_gate(evaluation)
                    if args.curriculum_level == 5
                    else None
                ),
            },
        },
        checkpoint_path,
    )
    evaluation_path = Path(f"{output_prefix}-evaluation.json")
    evaluation_payload = {
        **evaluation.__dict__,
        "nontrivial_success_rate": nontrivial_success_rate,
        "height_floor": height_floor,
        "recipe_floor": recipe_floor,
        "created_crop_rate": created_crop_rate,
        "renewable_harvest_rate": renewable_harvest_rate,
        "median_training_turn": evaluation.median_training_turn,
        "median_score_gain": evaluation.median_score_gain,
        "paired_teacher_median_turn_delta": teacher_delta,
        "functional_gate": functional_gate,
        "level5_mechanism_gate": (
            level5_mechanism_gate(evaluation)
            if args.curriculum_level == 5
            else None
        ),
    }
    evaluation_path.write_text(json.dumps(evaluation_payload, indent=2, sort_keys=True) + "\n")

    elapsed_wall = time.perf_counter() - start_wall
    elapsed_cpu = time.process_time() - start_cpu
    summary = {
        "config": config,
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sha256(checkpoint_path),
        "evaluation": {
            "path": str(evaluation_path),
            "success_rate": evaluation.success_rate,
            "median_success_turn": evaluation.median_success_turn,
            "nontrivial_success_rate": nontrivial_success_rate,
            "height_floor": height_floor,
            "recipe_floor": recipe_floor,
            "created_crop_rate": created_crop_rate,
            "renewable_harvest_rate": renewable_harvest_rate,
            "median_training_turn": evaluation.median_training_turn,
            "median_score_gain": evaluation.median_score_gain,
            "paired_teacher_median_turn_delta": teacher_delta,
            "functional_gate": functional_gate,
            "level5_mechanism_gate": (
                level5_mechanism_gate(evaluation)
                if args.curriculum_level == 5
                else None
            ),
        },
        "label_planes": {str(key): value for key, value in sorted(label_planes.items())},
        "teacher_generation": dict(teacher_episodes),
        "elapsed_wall_seconds": elapsed_wall,
        "elapsed_cpu_seconds": elapsed_cpu,
        "aggregate_host_cpu_percent": 100.0
        * elapsed_cpu
        / elapsed_wall
        / max(os.cpu_count() or 1, 1),
        "logs": logs,
    }
    summary_path = Path(f"{output_prefix}-summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"event": "complete", **summary}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
