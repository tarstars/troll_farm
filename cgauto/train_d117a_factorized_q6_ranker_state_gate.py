#!/usr/bin/env python3
"""Train D117a's factorized proposal ranker and root-state act/wait gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as functional

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d117a-factorized-q6-ranker-state-gate-protocol-2026-07-22.md"
FROZEN_INPUTS = BASE / "d117a-factorized-q6-ranker-state-gate-frozen-inputs.json"
FIT_OUTPUT = BASE / "d117a-factorized-q6-ranker-state-gate-fit-result.json"
SELECTION_LOCK = BASE / "d117a-factorized-q6-ranker-state-gate-selection-lock.json"
TRAIN_ARMS = BASE / "d114a-q6-train-arms-9843300-9843315.tsv"
TRAIN_BASELINES = BASE / "d114a-q6-train-baselines-9843300-9843315.tsv"
VALIDATION_ARMS = BASE / "d117a-q6-validation-arms-9843670-9843685.tsv"
VALIDATION_BASELINES = BASE / "d117a-q6-validation-baselines-9843670-9843685.tsv"
CHECKPOINT = BASE / "d117a-factorized-q6-ranker-state-gate.pt"
OUTPUT = BASE / "d117a-factorized-q6-ranker-state-gate-result.json"

TRAIN_START = 9_843_300
TRAIN_MAPS = 16
TRAIN_ELAPSED = 855.033
VALIDATION_START = 9_843_670
VALIDATION_MAPS = 16
STATE_FEATURES = 64
GATE_HIDDEN = 8
SEEDS = (11701, 11702, 11703, 11704)
OFFSETS = (-1.0, -0.5, 0.0, 0.5, 1.0, 1.5)
EPOCHS = 40
ROOT_BATCH_SIZE = 128
LEARNING_RATE = 1.0e-3
WEIGHT_DECAY = 1.0e-4
CPU_THREADS = 20


class StateGate(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.hidden = nn.Linear(STATE_FEATURES, GATE_HIDDEN)
        self.output = nn.Linear(GATE_HIDDEN, 1)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.output(torch.relu(self.hidden(state))).squeeze(-1)


class FactorizedController(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.ranker = d115.CompactActClassifier()
        self.gate = StateGate()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_manifest(path: Path) -> dict:
    payload = json.loads(path.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        target = ROOT / relative
        actual = sha256(target) if target.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    return {
        "path": str(path.relative_to(ROOT)),
        "manifest_sha256": sha256(path),
        "declared": payload,
        "mismatches": mismatches,
        "pass": not mismatches,
    }


def factorized_dataset(data: dict) -> dict:
    root_order = list(dict.fromkeys(data["root_keys"]))
    maximum_proposals = max(len(data["arms_by_root"][root]) for root in root_order)
    action_features = np.zeros(
        (len(root_order), maximum_proposals, d115.FEATURES),
        dtype=np.float32,
    )
    valid = np.zeros((len(root_order), maximum_proposals), dtype=np.bool_)
    state_features = np.zeros((len(root_order), STATE_FEATURES), dtype=np.float32)
    rank_targets = np.zeros(len(root_order), dtype=np.int64)
    act_targets = np.zeros(len(root_order), dtype=np.bool_)
    state_fields = [f"state_{index:03}" for index in range(STATE_FEATURES)]
    index_by_arm = {
        d112.arm_key(row): index for index, row in enumerate(data["arms"])
    }
    proposal_counts = []
    target_advantages = []
    for root_index, root in enumerate(root_order):
        task, _ = root
        control = data["baseline_by_task"][task]
        rows = data["arms_by_root"][root]
        indices = [index_by_arm[d112.arm_key(row)] for row in rows]
        count = len(indices)
        proposal_counts.append(count)
        action_features[root_index, :count] = data["x"][indices].astype(np.float32)
        valid[root_index, :count] = True
        states = np.asarray(
            [[float(row[field]) for field in state_fields] for row in rows],
            dtype=np.float32,
        )
        assert np.array_equal(states, np.repeat(states[:1], count, axis=0))
        state_features[root_index] = states[0]
        best = max(rows, key=lambda row: d112.tie_key(row, control))
        best_position = next(
            index for index, row in enumerate(rows) if d112.arm_key(row) == d112.arm_key(best)
        )
        best_advantage = float(data["y"][indices[best_position]])
        assert np.isclose(best_advantage, max(data["y"][indices]))
        rank_targets[root_index] = best_position
        act_targets[root_index] = best_advantage > 0.0
        target_advantages.append(best_advantage)
    return {
        "action_features": torch.from_numpy(action_features),
        "valid": torch.from_numpy(valid),
        "state_features": torch.from_numpy(state_features),
        "rank_targets": torch.from_numpy(rank_targets),
        "act_targets": torch.from_numpy(act_targets),
        "root_order": root_order,
        "summary": {
            "roots": len(root_order),
            "arms": int(valid.sum()),
            "maximum_proposals": maximum_proposals,
            "minimum_proposals": min(proposal_counts),
            "mean_proposals": float(np.mean(proposal_counts)),
            "target_act_roots": int(act_targets.sum()),
            "target_wait_roots": int((~act_targets).sum()),
            "target_act_root_rate": float(act_targets.mean()),
            "target_advantage_minimum": min(target_advantages),
            "target_advantage_maximum": max(target_advantages),
        },
    }


def proposal_logits(
    ranker: d115.CompactActClassifier,
    features: torch.Tensor,
    valid: torch.Tensor,
) -> torch.Tensor:
    roots, proposals, width = features.shape
    assert width == d115.FEATURES
    logits = ranker(features.reshape(roots * proposals, width)).reshape(roots, proposals)
    return logits.masked_fill(~valid, float("-inf"))


def train_factorized_model(
    dataset: dict,
    seed: int,
    *,
    epochs: int = EPOCHS,
    root_batch_size: int = ROOT_BATCH_SIZE,
    threads: int = CPU_THREADS,
) -> tuple[FactorizedController, dict]:
    d115.configure_torch(threads)
    torch.manual_seed(seed)
    model = FactorizedController()
    assert d115.parameter_count(model) == 6_626
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )
    actions = dataset["action_features"]
    valid = dataset["valid"]
    states = dataset["state_features"]
    rank_targets = dataset["rank_targets"]
    act_targets = dataset["act_targets"]
    generator = np.random.Generator(np.random.PCG64(seed))
    epoch_losses = []
    model.train()
    for _ in range(epochs):
        order = generator.permutation(len(rank_targets))
        total_sum = 0.0
        rank_sum = 0.0
        gate_sum = 0.0
        roots_seen = 0
        for start in range(0, len(order), root_batch_size):
            indices = torch.from_numpy(order[start : start + root_batch_size])
            optimizer.zero_grad(set_to_none=True)
            ranks = proposal_logits(model.ranker, actions[indices], valid[indices])
            gate = model.gate(states[indices])
            rank_loss = functional.cross_entropy(ranks, rank_targets[indices])
            gate_loss = functional.binary_cross_entropy_with_logits(
                gate,
                act_targets[indices].float(),
            )
            loss = rank_loss + gate_loss
            loss.backward()
            optimizer.step()
            count = len(indices)
            total_sum += float(loss.detach()) * count
            rank_sum += float(rank_loss.detach()) * count
            gate_sum += float(gate_loss.detach()) * count
            roots_seen += count
        epoch_losses.append(
            {
                "total": total_sum / roots_seen,
                "rank": rank_sum / roots_seen,
                "gate": gate_sum / roots_seen,
            }
        )
    model.eval()
    with torch.no_grad():
        ranks = proposal_logits(model.ranker, actions, valid)
        gate = model.gate(states)
        final_rank_loss = float(functional.cross_entropy(ranks, rank_targets))
        final_gate_loss = float(
            functional.binary_cross_entropy_with_logits(gate, act_targets.float())
        )
        rank_predictions = ranks.argmax(dim=1)
        gate_predictions = gate > 0.0
        rank_accuracy = float((rank_predictions == rank_targets).float().mean())
        rank_act_accuracy = float(
            (rank_predictions[act_targets] == rank_targets[act_targets]).float().mean()
        )
        act_recall = float(gate_predictions[act_targets].float().mean())
        wait_recall = float((~gate_predictions[~act_targets]).float().mean())
    return model, {
        "seed": seed,
        "epochs": epochs,
        "root_batch_size": root_batch_size,
        "learning_rate": LEARNING_RATE,
        "weight_decay": WEIGHT_DECAY,
        "cpu_threads": threads,
        "parameters": d115.parameter_count(model),
        "model_hash": d115.canonical_model_hash(model),
        "first_epoch_streaming_loss": epoch_losses[0],
        "last_epoch_streaming_loss": epoch_losses[-1],
        "final_rank_cross_entropy": final_rank_loss,
        "final_gate_binary_cross_entropy": final_gate_loss,
        "train_rank_top1_accuracy": rank_accuracy,
        "train_rank_top1_accuracy_on_act_roots": rank_act_accuracy,
        "train_gate_act_recall": act_recall,
        "train_gate_wait_recall": wait_recall,
        "train_gate_balanced_accuracy": (act_recall + wait_recall) / 2.0,
    }


def state_gate_logits(model: FactorizedController, dataset: dict) -> np.ndarray:
    model.eval()
    with torch.no_grad():
        logits = model.gate(dataset["state_features"])
    result = logits.detach().cpu().numpy().astype(np.float32, copy=False)
    assert result.shape == (len(dataset["root_order"]),) and np.isfinite(result).all()
    return result


def factorized_policy_metrics(
    data: dict,
    rank_logits: np.ndarray,
    gate_by_root: dict,
    offset: float,
) -> dict:
    rank_by_arm = {
        d112.arm_key(row): float(score)
        for row, score in zip(data["arms"], rank_logits, strict=True)
    }
    selected = []
    positive_ties = 0
    for task, control in data["baseline_by_task"].items():
        choice = None
        for boundary in range(int(control["boundary_count"])):
            root = (task, boundary)
            if gate_by_root[root] - offset <= 0.0:
                continue
            rows = data["arms_by_root"][root]
            scores = [rank_by_arm[d112.arm_key(row)] for row in rows]
            best_score = max(scores)
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


def model_fit_gates(summary: dict) -> dict[str, bool]:
    return {
        "rank_top1_at_least_20pct": summary["train_rank_top1_accuracy"] >= 0.20,
        "act_root_rank_top1_at_least_20pct": (
            summary["train_rank_top1_accuracy_on_act_roots"] >= 0.20
        ),
        "gate_balanced_accuracy_at_least_60pct": (
            summary["train_gate_balanced_accuracy"] >= 0.60
        ),
        "gate_act_recall_at_least_50pct": summary["train_gate_act_recall"] >= 0.50,
        "gate_wait_recall_at_least_50pct": summary["train_gate_wait_recall"] >= 0.50,
    }


def fit_policy_gates(metrics: dict) -> dict[str, bool]:
    return {
        "mean_at_least_2": metrics["mean_margin_delta"] >= 2.0,
        "strict_at_least_20pct": metrics["strict_improvement_rate"] >= 0.20,
        "both_folds_nonnegative": min(metrics["fold_mean_margin_delta"].values()) >= 0.0,
        "worst_family_at_least_minus3": metrics["worst_family"] >= -3.0,
        "six_positive_families": metrics["positive_families"] >= 6,
        "activity_10_to_85pct": 0.10 <= metrics["intervention_rate"] <= 0.85,
        "crop_100pct": metrics["crop_rate"] == 1.0,
        "worker_three_within_5pp": (
            metrics["worker_three_rate"]
            >= metrics["control_worker_three_rate"] - 0.05
        ),
    }


def train_models_and_grid(train: dict) -> tuple[dict, list, list, dict]:
    dataset = factorized_dataset(train)
    summaries = []
    candidates = []
    models = {}
    grid_index = 0
    for seed in SEEDS:
        model, summary = train_factorized_model(dataset, seed)
        summaries.append(summary)
        models[seed] = model
        ranks = d115.model_logits(model.ranker, train["x"])
        gate_values = state_gate_logits(model, dataset)
        gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
        structural = model_fit_gates(summary)
        for offset in OFFSETS:
            metrics = factorized_policy_metrics(train, ranks, gate_by_root, offset)
            policy = fit_policy_gates(metrics)
            candidates.append(
                {
                    "grid_index": grid_index,
                    "seed": seed,
                    "gate_offset": offset,
                    "model_hash": summary["model_hash"],
                    "model_fit_gates": structural,
                    "fit_policy_metrics": metrics,
                    "fit_policy_gates": policy,
                    "fit_eligible": all(structural.values()) and all(policy.values()),
                }
            )
            grid_index += 1
    return dataset, summaries, candidates, models


def checkpoint_payload(model: FactorizedController, selected: dict) -> dict:
    return {
        "schema": "troll-farm-d117a-factorized-ranker-state-gate-checkpoint-v1",
        "action_features": d115.FEATURES,
        "state_features": STATE_FEATURES,
        "rank_hidden": d115.HIDDEN,
        "gate_hidden": GATE_HIDDEN,
        "parameters": d115.parameter_count(model),
        "seed": selected["seed"],
        "gate_offset": selected["gate_offset"],
        "model_hash": d115.canonical_model_hash(model),
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def fit_only() -> None:
    frozen = verify_manifest(FROZEN_INPUTS)
    train = d114.panel(
        TRAIN_ARMS,
        TRAIN_BASELINES,
        TRAIN_START,
        TRAIN_MAPS,
        TRAIN_ELAPSED,
    )
    dataset = None
    summaries = []
    candidates = []
    if frozen["pass"] and train["mechanics"]["pass"]:
        dataset, summaries, candidates, _ = train_models_and_grid(train)
    eligible = [candidate for candidate in candidates if candidate["fit_eligible"]]
    result = {
        "schema": "troll-farm-d117a-factorized-q6-fit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "frozen_inputs": frozen,
        "train_mechanics": train["mechanics"],
        "train_teacher": train["teacher"],
        "training_data": dataset["summary"] if dataset is not None else None,
        "training": summaries,
        "fit_grid": {
            "seeds": SEEDS,
            "gate_offsets": OFFSETS,
            "candidates": len(candidates),
            "eligible": len(eligible),
            "results": candidates,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (TRAIN_ARMS, TRAIN_BASELINES)
        },
        "decision": (
            "open_fresh_validation_collection"
            if eligible
            else "repair_only"
            if not (frozen["pass"] and train["mechanics"]["pass"])
            else "close_factorized_model_at_fit_gate"
        ),
    }
    FIT_OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def validate(validation_elapsed: float) -> None:
    frozen = verify_manifest(FROZEN_INPUTS)
    selection_lock = verify_manifest(SELECTION_LOCK)
    fit = json.loads(FIT_OUTPUT.read_text())
    if fit["decision"] != "open_fresh_validation_collection":
        raise RuntimeError("D117 fit gate did not authorize validation")
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
        validation_elapsed,
    )
    mechanics_pass = (
        frozen["pass"]
        and selection_lock["pass"]
        and train["mechanics"]["pass"]
        and validation["mechanics"]["pass"]
    )
    summaries = []
    candidates = []
    models = {}
    reproducible = False
    if mechanics_pass:
        train_dataset, summaries, _, models = train_models_and_grid(train)
        expected_hashes = {
            item["seed"]: item["model_hash"] for item in fit["training"]
        }
        actual_hashes = {item["seed"]: item["model_hash"] for item in summaries}
        reproducible = expected_hashes == actual_hashes
        if not reproducible:
            raise RuntimeError("D117 fit model hashes are not reproducible")
        validation_dataset = factorized_dataset(validation)
        grid_index = 0
        for seed in SEEDS:
            model = models[seed]
            ranks = d115.model_logits(model.ranker, validation["x"])
            gate_values = state_gate_logits(model, validation_dataset)
            gate_by_root = dict(
                zip(validation_dataset["root_order"], gate_values, strict=True)
            )
            for offset in OFFSETS:
                metrics = factorized_policy_metrics(
                    validation,
                    ranks,
                    gate_by_root,
                    offset,
                )
                gates = d115.admission(metrics)
                candidates.append(
                    {
                        "grid_index": grid_index,
                        "seed": seed,
                        "gate_offset": offset,
                        "model_hash": actual_hashes[seed],
                        "metrics": metrics,
                        "admission": gates,
                        "admitted": all(gates.values()),
                    }
                )
                grid_index += 1
    admitted = [candidate for candidate in candidates if candidate["admitted"]]
    selected = max(admitted, key=d115.selection_key) if admitted else None
    checkpoint = None
    if selected is not None:
        model = models[selected["seed"]]
        torch.save(checkpoint_payload(model, selected), CHECKPOINT)
        checkpoint = {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "sha256": sha256(CHECKPOINT),
            "model_hash": d115.canonical_model_hash(model),
            "bytes": CHECKPOINT.stat().st_size,
        }
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D117 checkpoint exists without validation admission")
    result = {
        "schema": "troll-farm-d117a-factorized-q6-ranker-state-gate-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "frozen_inputs": frozen,
        "selection_lock": selection_lock,
        "fit_result": {
            "path": str(FIT_OUTPUT.relative_to(ROOT)),
            "sha256": sha256(FIT_OUTPUT),
            "decision": fit["decision"],
            "eligible": fit["fit_grid"]["eligible"],
        },
        "architecture": {
            "action_features": d115.FEATURES,
            "rank_hidden_relu_units": d115.HIDDEN,
            "state_features": STATE_FEATURES,
            "gate_hidden_relu_units": GATE_HIDDEN,
            "parameters": 6_626,
            "float32_parameter_bytes": 6_626 * 4,
            "int8_parameter_bytes_before_encoding": 6_626,
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
        "fit_models_reproduced": reproducible,
        "training": summaries,
        "grid": {
            "seeds": SEEDS,
            "gate_offsets": OFFSETS,
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
            else "close_factorized_model_without_held"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fit-only", action="store_true")
    group.add_argument("--validation-elapsed", type=float)
    args = parser.parse_args()
    if args.fit_only:
        fit_only()
    else:
        validate(args.validation_elapsed)


if __name__ == "__main__":
    main()
