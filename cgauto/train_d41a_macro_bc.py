#!/usr/bin/env python3
"""Behavior-clone and closed-loop evaluate the frozen D40 macro teacher."""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from cgauto.rl_macro_env import (
    BRANCHES,
    CANDIDATE_FEATURES,
    OPPONENTS,
    TASKS_PER_MAP,
    MacroVecEnv,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d41a-complete-macro-behavior-cloning-protocol-2026-07-21.md"
TEACHER_BASELINE = ANALYSIS / "d41a-development-teacher-9711000-9711031.tsv"
RANDOM_BASELINE = ANALYSIS / "d41a-development-random-9711000-9711031.tsv"
CELLS = 11 * 22
MODEL_SEEDS = (401, 402, 403)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


class CandidateScorer(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(CANDIDATE_FEATURES, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.network(features.float()).squeeze(-1)


def masked_scores(
    model: CandidateScorer, features: torch.Tensor, counts: torch.Tensor
) -> torch.Tensor:
    scores = model(features)
    candidate = torch.arange(scores.shape[1], device=scores.device)
    return scores.masked_fill(candidate[None, :] >= counts[:, None], -1e30)


def read_baseline(
    path: Path,
    expected_policy: str,
    *,
    seed_base: int = 9_711_000,
    maps: int = 32,
) -> list[dict]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    if len(rows) != maps * TASKS_PER_MAP:
        raise SystemExit(
            f"baseline must contain {maps * TASKS_PER_MAP} rows: {path}"
        )
    converted = []
    for row in rows:
        if row["policy"] != expected_policy:
            raise SystemExit(f"unexpected policy in {path}: {row['policy']}")
        converted.append(
            {
                "map_seed": int(row["map_seed"]),
                "seat": int(row["seat"]),
                "opponent": row["opponent"],
                "own_score": int(row["own_score"]),
                "opponent_score": int(row["opponent_score"]),
                "margin": int(row["margin"]),
                "own_workers": int(row["own_workers"]),
                "own_created_crops": int(row["own_created_crops"]),
                "invalid_direct_commands": int(row["invalid_direct_commands"]),
                "provenance_failures": int(row["provenance_failures"]),
                "deposit_prediction_failures": int(
                    row["deposit_prediction_failures"]
                ),
                "action_hash": int(row["action_hash"]),
                "state_hash": int(row["state_hash"]),
            }
        )
    expected = {
        (seed, seat, opponent)
        for seed in range(seed_base, seed_base + maps)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    if {(row["map_seed"], row["seat"], row["opponent"]) for row in converted} != expected:
        raise SystemExit(f"baseline grid mismatch: {path}")
    return converted


def feature_stream_hash(seed_base: int, decisions: int, num_envs: int) -> str:
    digest = hashlib.sha256()
    seen = 0
    with MacroVecEnv(num_envs, seed_base) as env:
        while seen < decisions:
            take = min(num_envs, decisions - seen)
            for index in range(take):
                count = int(env.counts[index])
                digest.update(env.actions[index, :count].tobytes())
                digest.update(env.features[index, :count].tobytes())
                digest.update(env.counts[index].tobytes())
                digest.update(env.teacher_indices[index].tobytes())
                digest.update(env.branches[index].tobytes())
            env.step(env.teacher_actions())
            seen += take
    return digest.hexdigest()


def collect_chunk(
    env: MacroVecEnv, samples: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
    if samples % env.num_envs:
        raise ValueError("chunk samples must be divisible by num_envs")
    rows: list[np.ndarray] = []
    labels: list[int] = []
    branches: list[int] = []
    planes: list[int] = []
    counts: list[int] = []
    started = time.perf_counter()
    while len(rows) < samples:
        teacher_actions = env.teacher_actions()
        for index in range(env.num_envs):
            count = int(env.counts[index])
            rows.append(env.features[index, :count].copy())
            labels.append(int(env.teacher_indices[index]))
            branches.append(int(env.branches[index]))
            planes.append(int(teacher_actions[index]) // CELLS)
            counts.append(count)
        env.step(teacher_actions)
    maximum = max(counts)
    packed = np.zeros((samples, maximum, CANDIDATE_FEATURES), dtype=np.float32)
    for index, row in enumerate(rows):
        packed[index, : row.shape[0]] = row
    return (
        packed,
        np.asarray(counts, dtype=np.int64),
        np.asarray(labels, dtype=np.int64),
        np.asarray(branches, dtype=np.int64),
        {
            "samples": samples,
            "mean_candidates": float(np.mean(counts)),
            "max_candidates": maximum,
            "collect_seconds": time.perf_counter() - started,
            "label_planes": dict(collections.Counter(planes)),
        },
    )


def train_chunk(
    model: CandidateScorer,
    optimizer: torch.optim.Optimizer,
    rng: np.random.Generator,
    features: np.ndarray,
    counts: np.ndarray,
    labels: np.ndarray,
    *,
    epochs: int,
    minibatch_size: int,
) -> dict:
    model.train()
    indexes = np.arange(len(labels))
    losses: list[float] = []
    accuracies: list[float] = []
    started = time.perf_counter()
    for _ in range(epochs):
        rng.shuffle(indexes)
        for start in range(0, len(indexes), minibatch_size):
            selected = indexes[start : start + minibatch_size]
            selected_features = torch.from_numpy(features[selected])
            selected_counts = torch.from_numpy(counts[selected])
            selected_labels = torch.from_numpy(labels[selected])
            scores = masked_scores(model, selected_features, selected_counts)
            loss = F.cross_entropy(scores, selected_labels)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            losses.append(float(loss.detach()))
            accuracies.append(
                float((scores.argmax(dim=1) == selected_labels).float().mean())
            )
    return {
        "loss": float(np.mean(losses)),
        "accuracy": float(np.mean(accuracies)),
        "train_seconds": time.perf_counter() - started,
    }


def macro_f1(expected: list[int], predicted: list[int]) -> float:
    scores = []
    for label in range(9):
        tp = sum(a == label and b == label for a, b in zip(expected, predicted))
        fp = sum(a != label and b == label for a, b in zip(expected, predicted))
        fn = sum(a == label and b != label for a, b in zip(expected, predicted))
        scores.append(2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 1.0)
    return float(np.mean(scores))


@torch.inference_mode()
def teacher_forced_validation(
    models: dict[int, CandidateScorer], *, seed_base: int, maps: int, num_envs: int
) -> dict[int, dict]:
    target_tasks = maps * TASKS_PER_MAP
    state = {
        seed: {
            "total": 0,
            "correct": 0,
            "branch_total": [0] * len(BRANCHES),
            "branch_correct": [0] * len(BRANCHES),
            "expected_planes": [],
            "predicted_planes": [],
        }
        for seed in models
    }
    completed: set[int] = set()
    with MacroVecEnv(num_envs, seed_base) as env:
        while len(completed) < target_tasks:
            active = np.flatnonzero(env.task_indices < target_tasks)
            maximum = int(env.counts[active].max())
            feature_tensor = torch.from_numpy(env.features[active, :maximum])
            count_tensor = torch.from_numpy(env.counts[active].astype(np.int64))
            labels = env.teacher_indices[active].astype(np.int64)
            teacher_actions = env.teacher_actions()
            expected_planes = (teacher_actions[active] // CELLS).tolist()
            for seed, model in models.items():
                model.eval()
                predicted = (
                    masked_scores(model, feature_tensor, count_tensor)
                    .argmax(dim=1)
                    .cpu()
                    .numpy()
                )
                correct = predicted == labels
                payload = state[seed]
                payload["total"] += len(active)
                payload["correct"] += int(correct.sum())
                for position, branch in enumerate(env.branches[active]):
                    payload["branch_total"][int(branch)] += 1
                    payload["branch_correct"][int(branch)] += int(correct[position])
                predicted_actions = env.actions[active, predicted]
                payload["expected_planes"].extend(expected_planes)
                payload["predicted_planes"].extend((predicted_actions // CELLS).tolist())
            _, _, _, _, info = env.step(teacher_actions)
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed.add(terminal["task_index"])
    output = {}
    for seed, payload in state.items():
        branch_accuracy = {
            BRANCHES[index]: (
                payload["branch_correct"][index] / payload["branch_total"][index]
                if payload["branch_total"][index]
                else 1.0
            )
            for index in range(len(BRANCHES))
        }
        output[seed] = {
            "decisions": payload["total"],
            "accuracy": payload["correct"] / payload["total"],
            "branch_accuracy": branch_accuracy,
            "minimum_branch_accuracy": min(branch_accuracy.values()),
            "action_plane_macro_f1": macro_f1(
                payload["expected_planes"], payload["predicted_planes"]
            ),
        }
        output[seed]["pass"] = (
            output[seed]["accuracy"] >= 0.99
            and output[seed]["minimum_branch_accuracy"] >= 0.97
            and output[seed]["action_plane_macro_f1"] >= 0.95
        )
    return output


@torch.inference_mode()
def evaluate_closed_loop(
    model: CandidateScorer, *, seed_base: int, maps: int, num_envs: int
) -> list[dict]:
    model.eval()
    target_tasks = maps * TASKS_PER_MAP
    completed: dict[int, dict] = {}
    with MacroVecEnv(num_envs, seed_base) as env:
        while len(completed) < target_tasks:
            maximum = int(env.counts.max())
            scores = masked_scores(
                model,
                torch.from_numpy(env.features[:, :maximum]),
                torch.from_numpy(env.counts.astype(np.int64)),
            )
            selected_indices = scores.argmax(dim=1).cpu().numpy()
            selected_actions = env.actions[np.arange(num_envs), selected_indices]
            _, _, _, _, info = env.step(selected_actions)
            for terminal in info.terminals:
                if terminal is not None and terminal["task_index"] < target_tasks:
                    completed[terminal["task_index"]] = terminal
    return [completed[index] for index in range(target_tasks)]


def summarize(rows: list[dict]) -> dict:
    by_opponent: dict[str, list[dict]] = collections.defaultdict(list)
    for row in rows:
        by_opponent[row["opponent"]].append(row)
    return {
        "episodes": len(rows),
        "mean_own_score": float(np.mean([row["own_score"] for row in rows])),
        "mean_opponent_score": float(
            np.mean([row["opponent_score"] for row in rows])
        ),
        "mean_margin": float(np.mean([row["margin"] for row in rows])),
        "worker_two_rate": float(np.mean([row["own_workers"] >= 2 for row in rows])),
        "worker_three_rate": float(
            np.mean([row["own_workers"] >= 3 for row in rows])
        ),
        "crop_rate": float(np.mean([row["own_created_crops"] > 0 for row in rows])),
        "invalid_direct_commands": sum(
            row["invalid_direct_commands"] for row in rows
        ),
        "provenance_failures": sum(row["provenance_failures"] for row in rows),
        "deposit_prediction_failures": sum(
            row["deposit_prediction_failures"] for row in rows
        ),
        "by_opponent": {
            opponent: {
                "mean_margin": float(np.mean([row["margin"] for row in bucket])),
                "worker_three_rate": float(
                    np.mean([row["own_workers"] >= 3 for row in bucket])
                ),
            }
            for opponent, bucket in sorted(by_opponent.items())
        },
    }


def closed_loop_gate(
    learned_rows: list[dict], teacher_rows: list[dict], random_rows: list[dict]
) -> dict:
    learned = summarize(learned_rows)
    teacher = summarize(teacher_rows)
    random = summarize(random_rows)
    family_teacher_gaps = {
        opponent: learned["by_opponent"][opponent]["mean_margin"]
        - teacher["by_opponent"][opponent]["mean_margin"]
        for opponent in OPPONENTS
    }
    family_random_gains = {
        opponent: learned["by_opponent"][opponent]["mean_margin"]
        - random["by_opponent"][opponent]["mean_margin"]
        for opponent in OPPONENTS
    }
    gates = {
        "margin_within_20_of_teacher": learned["mean_margin"]
        >= teacher["mean_margin"] - 20,
        "margin_at_least_100_above_random": learned["mean_margin"]
        >= random["mean_margin"] + 100,
        "worker_two_at_least_90pct": learned["worker_two_rate"] >= 0.90,
        "worker_three_at_least_80pct": learned["worker_three_rate"] >= 0.80,
        "crop_at_least_90pct": learned["crop_rate"] >= 0.90,
        "family_teacher_gap_at_least_minus_35": min(family_teacher_gaps.values())
        >= -35,
        "family_random_gain_at_least_40": min(family_random_gains.values()) >= 40,
        "integrity": learned["invalid_direct_commands"] == 0
        and learned["provenance_failures"] == 0
        and learned["deposit_prediction_failures"] == 0,
    }
    return {
        "learned": learned,
        "teacher": teacher,
        "random": random,
        "family_teacher_gaps": family_teacher_gaps,
        "family_random_gains": family_random_gains,
        "gates": gates,
        "pass": all(gates.values()),
    }


def save_weights(model: CandidateScorer, path: Path) -> None:
    np.savez(
        path,
        **{
            name: tensor.detach().cpu().numpy()
            for name, tensor in model.state_dict().items()
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=500_000)
    parser.add_argument("--num-envs", type=int, default=16)
    parser.add_argument("--chunk-size", type=int, default=4_096)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--minibatch-size", type=int, default=2_048)
    parser.add_argument("--threads", type=int, default=20)
    parser.add_argument("--train-seed-base", type=int, default=9_700_000)
    parser.add_argument("--validation-seed-base", type=int, default=9_710_000)
    parser.add_argument("--development-seed-base", type=int, default=9_711_000)
    parser.add_argument("--validation-maps", type=int, default=32)
    parser.add_argument("--development-maps", type=int, default=32)
    parser.add_argument("--output-prefix", default="d41a-macro-bc")
    args = parser.parse_args()
    if args.samples % args.num_envs or args.chunk_size % args.num_envs:
        raise SystemExit("samples and chunk size must be divisible by num_envs")
    if not PROTOCOL.exists() or not TEACHER_BASELINE.exists() or not RANDOM_BASELINE.exists():
        raise SystemExit("frozen D41a protocol and development baselines are required")
    if args.development_seed_base != 9_711_000 or args.development_maps != 32:
        raise SystemExit("development interval must match frozen baselines")

    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(min(4, args.threads))
    models = {}
    optimizers = {}
    rngs = {}
    for seed in MODEL_SEEDS:
        torch.manual_seed(seed)
        models[seed] = CandidateScorer()
        optimizers[seed] = torch.optim.Adam(models[seed].parameters(), lr=1e-3)
        rngs[seed] = np.random.default_rng(seed)
    parameter_count = sum(parameter.numel() for parameter in models[MODEL_SEEDS[0]].parameters())
    if parameter_count != 1_985:
        raise SystemExit(f"unexpected D41a parameter count: {parameter_count}")

    teacher_rows = read_baseline(TEACHER_BASELINE, "work_conserving")
    random_rows = read_baseline(RANDOM_BASELINE, "random")
    feature_hash_a = feature_stream_hash(args.train_seed_base, 4_096, args.num_envs)
    feature_hash_b = feature_stream_hash(args.train_seed_base, 4_096, args.num_envs)
    if feature_hash_a != feature_hash_b:
        raise SystemExit("D41a feature A/A hash mismatch")

    started = time.perf_counter()
    logs = []
    consumed = 0
    with MacroVecEnv(args.num_envs, args.train_seed_base) as env:
        while consumed < args.samples:
            chunk_samples = min(args.chunk_size, args.samples - consumed)
            features, counts, labels, _branches, collection = collect_chunk(
                env, chunk_samples
            )
            consumed += chunk_samples
            progress = consumed / args.samples
            learning_rate = 1e-4 + (1e-3 - 1e-4) * 0.5 * (
                1.0 + math.cos(math.pi * progress)
            )
            training = {}
            for seed in MODEL_SEEDS:
                optimizers[seed].param_groups[0]["lr"] = learning_rate
                training[seed] = train_chunk(
                    models[seed],
                    optimizers[seed],
                    rngs[seed],
                    features,
                    counts,
                    labels,
                    epochs=args.epochs,
                    minibatch_size=args.minibatch_size,
                )
            log = {
                "chunk": len(logs) + 1,
                "samples": consumed,
                "learning_rate": learning_rate,
                "collection": collection,
                "training": training,
            }
            logs.append(log)
            if len(logs) == 1 or len(logs) % 10 == 0 or consumed == args.samples:
                print(json.dumps({"event": "chunk", **log}, sort_keys=True), flush=True)
            del features, counts, labels

    validation = teacher_forced_validation(
        models,
        seed_base=args.validation_seed_base,
        maps=args.validation_maps,
        num_envs=args.num_envs,
    )
    development = {}
    for seed in MODEL_SEEDS:
        checkpoint = ANALYSIS / f"{args.output_prefix}-seed{seed}.pt"
        weights = ANALYSIS / f"{args.output_prefix}-seed{seed}-weights.npz"
        torch.save(
            {
                "model": models[seed].state_dict(),
                "model_seed": seed,
                "features": CANDIDATE_FEATURES,
                "parameter_count": parameter_count,
            },
            checkpoint,
        )
        save_weights(models[seed], weights)
        if validation[seed]["pass"]:
            first = evaluate_closed_loop(
                models[seed],
                seed_base=args.development_seed_base,
                maps=args.development_maps,
                num_envs=args.num_envs,
            )
            gate = closed_loop_gate(first, teacher_rows, random_rows)
            deterministic = False
            if gate["pass"]:
                repeat = evaluate_closed_loop(
                    models[seed],
                    seed_base=args.development_seed_base,
                    maps=args.development_maps,
                    num_envs=args.num_envs,
                )
                deterministic = all(
                    (left["action_hash"], left["state_hash"])
                    == (right["action_hash"], right["state_hash"])
                    for left, right in zip(first, repeat)
                )
            development[seed] = {
                **gate,
                "deterministic_repeat": deterministic,
                "pass": gate["pass"] and deterministic,
                "episodes_detail": first,
            }
        else:
            development[seed] = {
                "pass": False,
                "deterministic_repeat": False,
                "skipped": "teacher_forced_validation_failed",
            }

    passing = [
        seed
        for seed in MODEL_SEEDS
        if validation[seed]["pass"] and development[seed]["pass"]
    ]
    selected_seed = min(passing) if len(passing) >= 2 else None
    float_weight_bytes = parameter_count * 4
    int8_weight_bytes = parameter_count
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "teacher_baseline": str(TEACHER_BASELINE),
        "teacher_baseline_sha256": sha256(TEACHER_BASELINE),
        "random_baseline": str(RANDOM_BASELINE),
        "random_baseline_sha256": sha256(RANDOM_BASELINE),
        "config": vars(args),
        "model_seeds": list(MODEL_SEEDS),
        "parameter_count": parameter_count,
        "float_weight_bytes": float_weight_bytes,
        "int8_weight_bytes": int8_weight_bytes,
        "feature_hash_a": feature_hash_a,
        "feature_hash_b": feature_hash_b,
        "feature_repeat_verified": feature_hash_a == feature_hash_b,
        "logs": logs,
        "validation": validation,
        "development": development,
        "passing_model_seeds": passing,
        "selected_seed": selected_seed,
        "learning_gate_without_kernel": len(passing) >= 2
        and parameter_count <= 2_000
        and float_weight_bytes <= 8 * 1024
        and int8_weight_bytes <= 2 * 1024,
        "elapsed_seconds": time.perf_counter() - started,
    }
    output = ANALYSIS / f"{args.output_prefix}-result.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "event": "result",
                "output": str(output),
                "passing_model_seeds": passing,
                "selected_seed": selected_seed,
                "validation": validation,
                "development_pass": {
                    seed: development[seed]["pass"] for seed in MODEL_SEEDS
                },
                "elapsed_seconds": report["elapsed_seconds"],
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
