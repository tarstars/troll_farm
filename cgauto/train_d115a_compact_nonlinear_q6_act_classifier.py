#!/usr/bin/env python3
"""Train and validate the frozen D115a compact nonlinear q6 act classifier."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as functional

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d115a-compact-nonlinear-q6-act-classifier-protocol-2026-07-22.md"
FROZEN_INPUTS = (
    BASE
    / "d115a-compact-nonlinear-q6-act-classifier-repair1-selection-frozen-inputs.json"
)
TRAIN_ARMS = BASE / "d114a-q6-train-arms-9843300-9843315.tsv"
TRAIN_BASELINES = BASE / "d114a-q6-train-baselines-9843300-9843315.tsv"
VALIDATION_ARMS = BASE / "d115a-q6-validation-repair1-arms-9843610-9843619.tsv"
VALIDATION_BASELINES = (
    BASE / "d115a-q6-validation-repair1-baselines-9843610-9843619.tsv"
)
CHECKPOINT = BASE / "d115a-compact-nonlinear-q6-act-classifier-repair1.pt"
OUTPUT = BASE / "d115a-compact-nonlinear-q6-act-classifier-repair1-result.json"

TRAIN_START = 9_843_300
TRAIN_MAPS = 16
TRAIN_ELAPSED = 855.033
VALIDATION_START = 9_843_610
VALIDATION_MAPS = 10
FEATURES = 379
HIDDEN = 16
SEEDS = (11501, 11502, 11503, 11504)
OFFSETS = (-1.0, 0.0, 0.5, 1.0, 1.5, 2.0)
EPOCHS = 40
BATCH_SIZE = 1024
LEARNING_RATE = 1.0e-3
WEIGHT_DECAY = 1.0e-4
CPU_THREADS = 20


class CompactActClassifier(nn.Module):
    """The prospectively bounded 379 -> 16 ReLU -> 1 D115 model."""

    def __init__(self) -> None:
        super().__init__()
        self.hidden = nn.Linear(FEATURES, HIDDEN)
        self.output = nn.Linear(HIDDEN, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(torch.relu(self.hidden(features))).squeeze(-1)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_inputs() -> dict:
    payload = json.loads(FROZEN_INPUTS.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    return {
        "manifest_sha256": sha256(FROZEN_INPUTS),
        "declared": payload,
        "mismatches": mismatches,
        "pass": not mismatches,
    }


def configure_torch(threads: int = CPU_THREADS) -> None:
    torch.set_num_threads(threads)
    try:
        torch.set_num_interop_threads(threads)
    except RuntimeError:
        # PyTorch permits setting inter-op threads only before parallel work starts.
        # Repeated unit-test calls are still deterministic with the established value.
        pass
    torch.use_deterministic_algorithms(True)


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters())


def class_balanced_root_weights(
    root_keys: list,
    targets: np.ndarray,
) -> tuple[np.ndarray, dict]:
    """Give every root equal mass, then split global mass equally by class."""
    labels = np.asarray(targets > 0.0, dtype=np.bool_)
    if not labels.any() or labels.all():
        raise ValueError("D115 training requires both positive and nonpositive arms")
    counts = Counter(root_keys)
    root_weights = np.asarray(
        [1.0 / counts[key] for key in root_keys],
        dtype=np.float64,
    )
    negative_mass = float(root_weights[~labels].sum())
    positive_mass = float(root_weights[labels].sum())
    weights = root_weights.copy()
    weights[~labels] *= 0.5 / negative_mass
    weights[labels] *= 0.5 / positive_mass
    assert np.isclose(weights[~labels].sum(), 0.5, atol=1.0e-12)
    assert np.isclose(weights[labels].sum(), 0.5, atol=1.0e-12)
    return weights.astype(np.float32), {
        "arms": len(labels),
        "roots": len(counts),
        "positive_arms": int(labels.sum()),
        "nonpositive_arms": int((~labels).sum()),
        "positive_arm_rate": float(labels.mean()),
        "unbalanced_positive_root_mass": positive_mass,
        "unbalanced_nonpositive_root_mass": negative_mass,
        "balanced_positive_mass": float(weights[labels].sum()),
        "balanced_nonpositive_mass": float(weights[~labels].sum()),
    }


def canonical_model_hash(model: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, tensor in model.state_dict().items():
        array = tensor.detach().cpu().contiguous().numpy().astype("<f4", copy=False)
        digest.update(name.encode("utf-8") + b"\0")
        digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode("ascii"))
        digest.update(b"\0")
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def train_model(
    x: np.ndarray,
    y: np.ndarray,
    root_keys: list,
    seed: int,
    *,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    threads: int = CPU_THREADS,
) -> tuple[CompactActClassifier, dict]:
    configure_torch(threads)
    torch.manual_seed(seed)
    model = CompactActClassifier()
    assert parameter_count(model) == 6_097
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )
    sample_weights, balance = class_balanced_root_weights(root_keys, y)
    features = torch.from_numpy(np.asarray(x, dtype=np.float32))
    labels = torch.from_numpy(np.asarray(y > 0.0, dtype=np.float32))
    weights = torch.from_numpy(sample_weights)
    generator = np.random.Generator(np.random.PCG64(seed))
    epoch_losses = []
    model.train()
    for _ in range(epochs):
        order = generator.permutation(len(features))
        weighted_loss = 0.0
        observed_weight = 0.0
        for start in range(0, len(order), batch_size):
            indices = torch.from_numpy(order[start : start + batch_size])
            batch_features = features[indices]
            batch_labels = labels[indices]
            batch_weights = weights[indices]
            optimizer.zero_grad(set_to_none=True)
            logits = model(batch_features)
            losses = functional.binary_cross_entropy_with_logits(
                logits,
                batch_labels,
                reduction="none",
            )
            denominator = batch_weights.sum()
            loss = (losses * batch_weights).sum() / denominator
            loss.backward()
            optimizer.step()
            weighted_loss += float((losses.detach() * batch_weights).sum())
            observed_weight += float(denominator)
        epoch_losses.append(weighted_loss / observed_weight)
    model.eval()
    with torch.no_grad():
        logits = model(features)
        final_losses = functional.binary_cross_entropy_with_logits(
            logits,
            labels,
            reduction="none",
        )
        final_loss = float((final_losses * weights).sum() / weights.sum())
        predictions = logits > 0.0
        positive_recall = float(predictions[labels.bool()].float().mean())
        negative_recall = float((~predictions[~labels.bool()]).float().mean())
    summary = {
        "seed": seed,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": LEARNING_RATE,
        "weight_decay": WEIGHT_DECAY,
        "cpu_threads": threads,
        "parameters": parameter_count(model),
        "model_hash": canonical_model_hash(model),
        "first_epoch_streaming_loss": epoch_losses[0],
        "last_epoch_streaming_loss": epoch_losses[-1],
        "final_full_weighted_loss": final_loss,
        "train_positive_recall_at_zero": positive_recall,
        "train_nonpositive_recall_at_zero": negative_recall,
        "balance": balance,
    }
    return model, summary


def model_logits(model: nn.Module, x: np.ndarray) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        result = model(torch.from_numpy(np.asarray(x, dtype=np.float32)))
    logits = result.detach().cpu().numpy().astype(np.float32, copy=False)
    assert logits.shape == (len(x),) and np.isfinite(logits).all()
    return logits


def policy_metrics(data: dict, logits: np.ndarray, offset: float) -> dict:
    """Evaluate exact first-positive semantics from dense one-use continuations."""
    score_by_key = {
        d112.arm_key(row): float(score)
        for row, score in zip(data["arms"], logits, strict=True)
    }
    selected = []
    positive_ties = 0
    for task, control in data["baseline_by_task"].items():
        choice = None
        for boundary in range(int(control["boundary_count"])):
            rows = data["arms_by_root"][(task, boundary)]
            scores = [score_by_key[d112.arm_key(row)] for row in rows]
            best_score = max(scores)
            if best_score - offset <= 0.0:
                continue
            winners = [index for index, score in enumerate(scores) if score == best_score]
            positive_ties += int(len(winners) > 1)
            choice = rows[winners[0]]
            break
        outcome = choice or control
        selected.append(
            {
                "opponent": task[2],
                "map_seed": task[0],
                "margin": d112.margin(outcome) - d112.margin(control),
                "own": int(outcome["own_score"]) - int(control["own_score"]),
                "rival": int(outcome["opponent_score"])
                - int(control["opponent_score"]),
                "intervened": choice is not None,
                "crop": int(outcome["own_created_crops"]) > 0,
                "worker_three": int(outcome["own_workers"]) >= 3,
                "control_worker_three": int(control["own_workers"]) >= 3,
            }
        )
    family = {
        opponent: d112.mean(
            row["margin"] for row in selected if row["opponent"] == opponent
        )
        for opponent in d112.OPPONENTS
    }
    folds = {
        str(fold): d112.mean(
            row["margin"]
            for row in selected
            if (row["map_seed"] - data["start"]) % 2 == fold
        )
        for fold in range(2)
    }
    return {
        "tasks": len(selected),
        "mean_margin_delta": d112.mean(row["margin"] for row in selected),
        "strict_improvement_rate": d112.mean(row["margin"] > 0 for row in selected),
        "mean_own_score_delta": d112.mean(row["own"] for row in selected),
        "mean_opponent_score_delta": d112.mean(row["rival"] for row in selected),
        "family_mean_margin_delta": family,
        "positive_families": sum(value > 0 for value in family.values()),
        "worst_family": min(family.values()),
        "fold_mean_margin_delta": folds,
        "intervention_rate": d112.mean(row["intervened"] for row in selected),
        "crop_rate": d112.mean(row["crop"] for row in selected),
        "worker_three_rate": d112.mean(row["worker_three"] for row in selected),
        "control_worker_three_rate": d112.mean(
            row["control_worker_three"] for row in selected
        ),
        "positive_score_ties": positive_ties,
    }


def admission(metrics: dict) -> dict[str, bool]:
    return d114.admission(metrics)


def selection_key(candidate: dict) -> tuple:
    metrics = candidate["metrics"]
    return (
        min(metrics["fold_mean_margin_delta"].values()),
        metrics["worst_family"],
        metrics["mean_margin_delta"],
        metrics["strict_improvement_rate"],
        -metrics["intervention_rate"],
        -candidate["grid_index"],
    )


def checkpoint_payload(model: nn.Module, selected: dict) -> dict:
    return {
        "schema": "troll-farm-d115a-compact-act-classifier-checkpoint-v1",
        "features": FEATURES,
        "hidden": HIDDEN,
        "parameters": parameter_count(model),
        "seed": selected["seed"],
        "logit_offset": selected["logit_offset"],
        "model_hash": canonical_model_hash(model),
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validation-elapsed", type=float, required=True)
    args = parser.parse_args()
    frozen = verify_frozen_inputs()
    train = d114.panel(
        TRAIN_ARMS,
        TRAIN_BASELINES,
        TRAIN_START,
        TRAIN_MAPS,
        TRAIN_ELAPSED,
    )
    validation = d114.panel(
        VALIDATION_ARMS,
        VALIDATION_BASELINES,
        VALIDATION_START,
        VALIDATION_MAPS,
        args.validation_elapsed,
    )
    mechanics_pass = (
        frozen["pass"]
        and train["mechanics"]["pass"]
        and validation["mechanics"]["pass"]
    )
    training = []
    candidates = []
    models = {}
    if mechanics_pass:
        grid_index = 0
        for seed in SEEDS:
            model, train_summary = train_model(
                train["x"],
                train["y"],
                train["root_keys"],
                seed,
            )
            training.append(train_summary)
            models[seed] = model
            logits = model_logits(model, validation["x"])
            for offset in OFFSETS:
                metrics = policy_metrics(validation, logits, offset)
                gates = admission(metrics)
                candidates.append(
                    {
                        "grid_index": grid_index,
                        "seed": seed,
                        "logit_offset": offset,
                        "model_hash": train_summary["model_hash"],
                        "metrics": metrics,
                        "admission": gates,
                        "admitted": all(gates.values()),
                    }
                )
                grid_index += 1
    admitted = [candidate for candidate in candidates if candidate["admitted"]]
    selected = max(admitted, key=selection_key) if admitted else None
    checkpoint = None
    if selected is not None:
        selected_model = models[selected["seed"]]
        torch.save(checkpoint_payload(selected_model, selected), CHECKPOINT)
        checkpoint = {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "sha256": sha256(CHECKPOINT),
            "model_hash": canonical_model_hash(selected_model),
            "bytes": CHECKPOINT.stat().st_size,
        }
    elif CHECKPOINT.exists():
        raise RuntimeError(
            "stale D115 checkpoint exists despite no admitted validation candidate"
        )
    result = {
        "schema": "troll-farm-d115a-compact-nonlinear-q6-act-classifier-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "frozen_inputs": frozen,
        "architecture": {
            "features": FEATURES,
            "hidden_relu_units": HIDDEN,
            "outputs": 1,
            "parameters": 6_097,
            "float32_parameter_bytes": 6_097 * 4,
            "int8_parameter_bytes_before_encoding": 6_097,
        },
        "collection_mechanics": {
            "train": train["mechanics"],
            "validation": validation["mechanics"],
            "pass": mechanics_pass,
        },
        "teacher": {
            "train": train["teacher"],
            "validation": validation["teacher"],
        },
        "training": training,
        "grid": {
            "seeds": SEEDS,
            "logit_offsets": OFFSETS,
            "candidates": len(candidates),
            "admitted": len(admitted),
            "results": candidates,
        },
        "selected": selected,
        "checkpoint": checkpoint,
        "artifacts": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (
                TRAIN_ARMS,
                TRAIN_BASELINES,
                VALIDATION_ARMS,
                VALIDATION_BASELINES,
            )
        },
        "decision": (
            "open_conditional_dense_held_qualification"
            if selected is not None
            else "repair_only"
            if not mechanics_pass
            else "close_compact_nonlinear_without_held"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
