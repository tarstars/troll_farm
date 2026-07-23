#!/usr/bin/env python3
"""Train the frozen D116a root-wise q6 proposal-versus-WAIT scorer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as functional

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d116a-rootwise-q6-proposal-wait-choice-protocol-2026-07-22.md"
FROZEN_INPUTS = BASE / "d116a-rootwise-q6-proposal-wait-choice-repair1-frozen-inputs.json"
TRAIN_ARMS = BASE / "d114a-q6-train-arms-9843300-9843315.tsv"
TRAIN_BASELINES = BASE / "d114a-q6-train-baselines-9843300-9843315.tsv"
VALIDATION_ARMS = BASE / "d116a-q6-validation-repair1-arms-9843650-9843665.tsv"
VALIDATION_BASELINES = BASE / "d116a-q6-validation-repair1-baselines-9843650-9843665.tsv"
CHECKPOINT = BASE / "d116a-rootwise-q6-proposal-wait-choice-repair1.pt"
OUTPUT = BASE / "d116a-rootwise-q6-proposal-wait-choice-repair1-result.json"

TRAIN_START = 9_843_300
TRAIN_MAPS = 16
TRAIN_ELAPSED = 855.033
VALIDATION_START = 9_843_650
VALIDATION_MAPS = 16
SEEDS = (11601, 11602, 11603, 11604)
OFFSETS = d115.OFFSETS
EPOCHS = 40
ROOT_BATCH_SIZE = 128
LEARNING_RATE = 1.0e-3
WEIGHT_DECAY = 1.0e-4
CPU_THREADS = 20


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


def root_choice_dataset(data: dict) -> dict:
    """Pack variable proposal sets and exact DP choices into padded complete roots."""
    root_order = list(dict.fromkeys(data["root_keys"]))
    maximum_proposals = max(len(data["arms_by_root"][root]) for root in root_order)
    features = np.zeros(
        (len(root_order), maximum_proposals, d115.FEATURES),
        dtype=np.float32,
    )
    valid = np.zeros((len(root_order), maximum_proposals), dtype=np.bool_)
    targets = np.zeros(len(root_order), dtype=np.int64)
    index_by_arm = {
        d112.arm_key(row): index for index, row in enumerate(data["arms"])
    }
    target_advantages = []
    proposal_counts = []
    for root_index, root in enumerate(root_order):
        task, _ = root
        control = data["baseline_by_task"][task]
        rows = data["arms_by_root"][root]
        indices = [index_by_arm[d112.arm_key(row)] for row in rows]
        count = len(indices)
        proposal_counts.append(count)
        features[root_index, :count] = data["x"][indices].astype(np.float32)
        valid[root_index, :count] = True
        best = max(rows, key=lambda row: d112.tie_key(row, control))
        best_position = next(
            index for index, row in enumerate(rows) if d112.arm_key(row) == d112.arm_key(best)
        )
        best_advantage = float(data["y"][indices[best_position]])
        assert np.isclose(best_advantage, max(data["y"][indices]))
        target_advantages.append(best_advantage)
        if best_advantage > 0.0:
            targets[root_index] = best_position + 1
    act = targets > 0
    return {
        "features": torch.from_numpy(features),
        "valid": torch.from_numpy(valid),
        "targets": torch.from_numpy(targets),
        "root_order": root_order,
        "summary": {
            "roots": len(root_order),
            "arms": int(valid.sum()),
            "maximum_proposals": maximum_proposals,
            "minimum_proposals": min(proposal_counts),
            "mean_proposals": float(np.mean(proposal_counts)),
            "target_act_roots": int(act.sum()),
            "target_wait_roots": int((~act).sum()),
            "target_act_root_rate": float(act.mean()),
            "target_advantage_minimum": min(target_advantages),
            "target_advantage_maximum": max(target_advantages),
        },
    }


def choice_logits(
    model: d115.CompactActClassifier,
    features: torch.Tensor,
    valid: torch.Tensor,
) -> torch.Tensor:
    roots, proposals, width = features.shape
    assert width == d115.FEATURES
    proposal_logits = model(features.reshape(roots * proposals, width)).reshape(
        roots, proposals
    )
    proposal_logits = proposal_logits.masked_fill(~valid, float("-inf"))
    wait_logits = torch.zeros(
        (roots, 1),
        dtype=proposal_logits.dtype,
        device=proposal_logits.device,
    )
    return torch.cat((wait_logits, proposal_logits), dim=1)


def train_choice_model(
    dataset: dict,
    seed: int,
    *,
    epochs: int = EPOCHS,
    root_batch_size: int = ROOT_BATCH_SIZE,
    threads: int = CPU_THREADS,
) -> tuple[d115.CompactActClassifier, dict]:
    d115.configure_torch(threads)
    torch.manual_seed(seed)
    model = d115.CompactActClassifier()
    assert d115.parameter_count(model) == 6_097
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )
    features = dataset["features"]
    valid = dataset["valid"]
    targets = dataset["targets"]
    generator = np.random.Generator(np.random.PCG64(seed))
    epoch_losses = []
    model.train()
    for _ in range(epochs):
        order = generator.permutation(len(targets))
        loss_sum = 0.0
        roots_seen = 0
        for start in range(0, len(order), root_batch_size):
            indices = torch.from_numpy(order[start : start + root_batch_size])
            optimizer.zero_grad(set_to_none=True)
            logits = choice_logits(model, features[indices], valid[indices])
            loss = functional.cross_entropy(logits, targets[indices])
            loss.backward()
            optimizer.step()
            count = len(indices)
            loss_sum += float(loss.detach()) * count
            roots_seen += count
        epoch_losses.append(loss_sum / roots_seen)
    model.eval()
    with torch.no_grad():
        logits = choice_logits(model, features, valid)
        final_loss = float(functional.cross_entropy(logits, targets))
        predictions = logits.argmax(dim=1)
        target_act = targets > 0
        predicted_act = predictions > 0
        exact_choice_accuracy = float((predictions == targets).float().mean())
        act_wait_accuracy = float((predicted_act == target_act).float().mean())
        wait_recall = float((~predicted_act[~target_act]).float().mean())
        proposal_choice_accuracy = float(
            (predictions[target_act] == targets[target_act]).float().mean()
        )
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
        "final_full_root_cross_entropy": final_loss,
        "train_exact_choice_accuracy": exact_choice_accuracy,
        "train_act_wait_accuracy": act_wait_accuracy,
        "train_wait_recall": wait_recall,
        "train_proposal_choice_accuracy_on_act_roots": proposal_choice_accuracy,
    }


def checkpoint_payload(model: d115.CompactActClassifier, selected: dict) -> dict:
    return {
        "schema": "troll-farm-d116a-rootwise-proposal-wait-checkpoint-v1",
        "features": d115.FEATURES,
        "hidden": d115.HIDDEN,
        "parameters": d115.parameter_count(model),
        "wait_logit": 0.0,
        "seed": selected["seed"],
        "logit_offset": selected["logit_offset"],
        "model_hash": d115.canonical_model_hash(model),
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
    dataset = None
    training = []
    candidates = []
    models = {}
    if mechanics_pass:
        dataset = root_choice_dataset(train)
        grid_index = 0
        for seed in SEEDS:
            model, train_summary = train_choice_model(dataset, seed)
            training.append(train_summary)
            models[seed] = model
            logits = d115.model_logits(model, validation["x"])
            for offset in OFFSETS:
                metrics = d115.policy_metrics(validation, logits, offset)
                gates = d115.admission(metrics)
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
    selected = max(admitted, key=d115.selection_key) if admitted else None
    checkpoint = None
    if selected is not None:
        selected_model = models[selected["seed"]]
        torch.save(checkpoint_payload(selected_model, selected), CHECKPOINT)
        checkpoint = {
            "path": str(CHECKPOINT.relative_to(ROOT)),
            "sha256": sha256(CHECKPOINT),
            "model_hash": d115.canonical_model_hash(selected_model),
            "bytes": CHECKPOINT.stat().st_size,
        }
    elif CHECKPOINT.exists():
        raise RuntimeError(
            "stale D116 checkpoint exists despite no admitted validation candidate"
        )
    result = {
        "schema": "troll-farm-d116a-rootwise-q6-proposal-wait-choice-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "frozen_inputs": frozen,
        "architecture": {
            "features": d115.FEATURES,
            "hidden_relu_units": d115.HIDDEN,
            "outputs": 1,
            "parameters": 6_097,
            "wait_logit": 0.0,
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
        "root_choice_training_data": dataset["summary"] if dataset is not None else None,
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
            else "close_rootwise_choice_without_held"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
