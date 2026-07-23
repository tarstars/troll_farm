#!/usr/bin/env python3
"""Train D135a's winner-conditioned action-aware gate on D133 blocks."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import gc
import json
import multiprocessing
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126
from cgauto import train_d134a_block_transfer_selected_soft_value_q6 as d134


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d135a-winner-conditioned-action-gate-q6-protocol-2026-07-22.md"
LOCK = BASE / "d135a-winner-conditioned-action-gate-q6-lock.json"
SELECTION_A = BASE / "d135a-winner-conditioned-action-gate-q6-selection-a.json"
SELECTION_B = BASE / "d135a-winner-conditioned-action-gate-q6-selection-b.json"
CHECKPOINT = BASE / "d135a-winner-conditioned-action-gate-q6.pt"
OUTPUT = BASE / "d135a-winner-conditioned-action-gate-q6-result.json"

SEED_PAIRS = ((13_401, 13_501), (13_402, 13_502), (13_403, 13_503), (13_404, 13_504))
BLOCKS = 4
STATE_FEATURES = 64
WINNER_EMBEDDING = 16
CONFIDENCE_FEATURES = 4
GATE_INPUTS = STATE_FEATURES + WINNER_EMBEDDING + CONFIDENCE_FEATURES
GATE_HIDDEN = 8
GATE_EPOCHS = 80
ROOT_BATCH_SIZE = 128
TARGET_ACTIVITY = 0.80
MAXIMUM_PROPOSALS = 26.0
WORKERS = 4


class WinnerGate(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.hidden = nn.Linear(GATE_INPUTS, GATE_HIDDEN)
        self.output = nn.Linear(GATE_HIDDEN, 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.output(torch.relu(self.hidden(features))).squeeze(-1)


class WinnerController(nn.Module):
    def __init__(self, ranker: d115.CompactActClassifier) -> None:
        super().__init__()
        self.ranker = ranker
        self.gate = WinnerGate()


def sha256(path: Path) -> str:
    return d117.sha256(path)


def verify_lock() -> dict:
    result = d117.verify_manifest(LOCK)
    if not result["pass"]:
        raise RuntimeError(f"D135 lock mismatch: {result['mismatches']!r}")
    return result


def winner_context(
    ranker: d115.CompactActClassifier, dataset: dict
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    actions = dataset["action_features"]
    valid = dataset["valid"]
    if bool((valid.sum(dim=1) < 2).any()):
        raise ValueError("D135 confidence features require at least two proposals")
    with torch.no_grad():
        ranks = d117.proposal_logits(ranker, actions, valid)
        selected = ranks.argmax(dim=1)
        root_indices = torch.arange(len(selected))
        selected_actions = actions[root_indices, selected]
        winner_embedding = torch.relu(ranker.hidden(selected_actions))
        top_two = ranks.topk(2, dim=1).values
        winner = top_two[:, 0]
        confidence = torch.stack(
            (
                winner,
                winner - top_two[:, 1],
                winner - torch.logsumexp(ranks, dim=1),
                valid.sum(dim=1).float() / MAXIMUM_PROPOSALS,
            ),
            dim=1,
        )
        features = torch.cat(
            (dataset["state_features"], winner_embedding, confidence), dim=1
        )
        selected_values = dataset["proposal_values"].gather(
            1, selected[:, None]
        ).squeeze(1)
        targets = selected_values > 0.0
    if features.shape != (len(selected), GATE_INPUTS):
        raise RuntimeError("D135 winner context has the wrong shape")
    if not bool(torch.isfinite(features).all()):
        raise RuntimeError("D135 winner context is nonfinite")
    return features, targets, selected_values, selected


def winner_gate_logits(model: WinnerController, dataset: dict) -> np.ndarray:
    model.eval()
    features, _, _, _ = winner_context(model.ranker, dataset)
    with torch.no_grad():
        logits = model.gate(features)
    result = logits.detach().cpu().numpy().astype(np.float32, copy=False)
    if result.shape != (len(dataset["root_order"]),) or not np.isfinite(result).all():
        raise RuntimeError("D135 gate logits are invalid")
    return result


def _binary_metrics(logits: torch.Tensor, targets: torch.Tensor) -> dict:
    predicted = logits > 0.0
    positive_recall = float(predicted[targets].float().mean())
    nonpositive_recall = float((~predicted[~targets]).float().mean())
    return {
        "positive_recall_at_zero": positive_recall,
        "nonpositive_recall_at_zero": nonpositive_recall,
        "balanced_accuracy_at_zero": (positive_recall + nonpositive_recall) / 2.0,
    }


def train_winner_controller(
    dataset: dict, ranker_seed: int, gate_seed: int
) -> tuple[WinnerController, dict]:
    base_model, ranker_training = d119.train_long_model(dataset, ranker_seed)
    ranker = base_model.ranker
    del base_model
    ranker_hash_before = d115.canonical_model_hash(ranker)
    ranker.requires_grad_(False)

    torch.manual_seed(gate_seed)
    model = WinnerController(ranker)
    if d115.parameter_count(model) != 6_786:
        raise RuntimeError("D135 parameter budget changed")
    features, targets, selected_values, _ = winner_context(model.ranker, dataset)
    optimizer = torch.optim.Adam(
        model.gate.parameters(),
        lr=d118.LEARNING_RATE,
        weight_decay=d118.WEIGHT_DECAY,
    )
    generator = np.random.Generator(np.random.PCG64(gate_seed))
    epoch_losses = []
    model.gate.train()
    for _ in range(GATE_EPOCHS):
        order = generator.permutation(len(targets))
        loss_sum = 0.0
        roots_seen = 0
        for start in range(0, len(order), ROOT_BATCH_SIZE):
            indices = torch.from_numpy(order[start : start + ROOT_BATCH_SIZE])
            optimizer.zero_grad(set_to_none=True)
            logits = model.gate(features[indices])
            loss = functional.binary_cross_entropy_with_logits(
                logits, targets[indices].float()
            )
            loss.backward()
            optimizer.step()
            count = len(indices)
            loss_sum += float(loss.detach()) * count
            roots_seen += count
        epoch_losses.append(loss_sum / roots_seen)

    model.eval()
    with torch.no_grad():
        logits = model.gate(features)
        final_loss = float(
            functional.binary_cross_entropy_with_logits(logits, targets.float())
        )
    ranker_hash_after = d115.canonical_model_hash(model.ranker)
    if ranker_hash_before != ranker_hash_after:
        raise RuntimeError("D135 action-gate training changed the frozen ranker")
    return model, {
        "ranker_seed": ranker_seed,
        "gate_seed": gate_seed,
        "ranker_hash": ranker_hash_after,
        "model_hash": d115.canonical_model_hash(model),
        "parameters": d115.parameter_count(model),
        "ranker_training": ranker_training,
        "gate_epochs": GATE_EPOCHS,
        "gate_root_batch_size": ROOT_BATCH_SIZE,
        "gate_learning_rate": d118.LEARNING_RATE,
        "gate_weight_decay": d118.WEIGHT_DECAY,
        "gate_cpu_threads": 1,
        "winner_positive_roots": int(targets.sum()),
        "winner_nonpositive_roots": int((~targets).sum()),
        "winner_positive_rate": float(targets.float().mean()),
        "winner_value_mean": float(selected_values.mean()),
        "winner_value_nonpositive_rate": float((selected_values <= 0.0).float().mean()),
        "first_epoch_gate_loss": epoch_losses[0],
        "last_epoch_gate_loss": epoch_losses[-1],
        "final_gate_binary_cross_entropy": final_loss,
        **_binary_metrics(logits, targets),
    }


def structural_metrics(model: WinnerController, dataset: dict) -> dict:
    features, targets, selected_values, _ = winner_context(model.ranker, dataset)
    with torch.no_grad():
        logits = model.gate(features)
    best_values = dataset["proposal_values"].max(dim=1).values
    regrets = best_values - selected_values
    return {
        "roots": len(targets),
        "winner_positive_rate": float(targets.float().mean()),
        "winner_value_mean": float(selected_values.mean()),
        "mean_proposal_regret": float(regrets.mean()),
        "within_10_rate": float((regrets <= 10.0).float().mean()),
        **_binary_metrics(logits, targets),
    }


def fold_worker(
    held_block: int,
    training_descriptors: list[dict],
    held_descriptor: dict,
    ranker_seed: int,
    gate_seed: int,
) -> dict:
    training, training_tasks = d134.load_training_data(training_descriptors)
    held_panel = d134.load_panel(held_descriptor)
    held_dataset = d118.soft_value_dataset(held_panel)
    model, training_summary = train_winner_controller(
        training, ranker_seed, gate_seed
    )
    training_gate = winner_gate_logits(model, training)
    offset, calibration = d125.activity_calibrated_offset(
        training_tasks,
        training["root_order"],
        training_gate,
        target_activity=TARGET_ACTIVITY,
    )
    ranks = d115.model_logits(model.ranker, held_panel["x"])
    held_gate = winner_gate_logits(model, held_dataset)
    gate_by_root = dict(zip(held_dataset["root_order"], held_gate, strict=True))
    metrics = d117.factorized_policy_metrics(
        held_panel, ranks, gate_by_root, offset
    )
    metrics["control_crop_rate"] = d123.control_crop_rate(held_panel)
    result = {
        "held_block": held_block,
        "seed": ranker_seed,
        "ranker_seed": ranker_seed,
        "gate_seed": gate_seed,
        "model_hash": training_summary["model_hash"],
        "gate_offset": offset,
        "calibration": calibration,
        "training": training_summary,
        "held_structural_metrics": structural_metrics(model, held_dataset),
        "held_policy_metrics": metrics,
    }
    del training, training_tasks, held_panel, held_dataset, model
    gc.collect()
    return result


def aggregate_policy_metrics(folds: list[dict]) -> dict:
    ordered = sorted(folds, key=lambda row: int(row["held_block"]))
    metrics = d134.aggregate_policy_metrics(
        [row["held_policy_metrics"] for row in ordered]
    )
    metrics["block_intervention_rate"] = {
        str(row["held_block"]): row["held_policy_metrics"]["intervention_rate"]
        for row in ordered
    }
    return metrics


def held_policy_gates(metrics: dict) -> dict[str, bool]:
    gates = d134.held_policy_gates(metrics)
    gates["every_block_activity_10_to_85pct"] = all(
        0.10 <= value <= 0.85
        for value in metrics["block_intervention_rate"].values()
    )
    return gates


def selection_key(candidate: dict) -> tuple:
    metrics = candidate["held_policy_metrics"]
    return (
        min(metrics["block_mean_margin_delta"].values()),
        metrics["worst_family"],
        metrics["mean_margin_delta"],
        metrics["strict_improvement_rate"],
        -metrics["intervention_rate"],
        -candidate["ranker_seed"],
    )


def run_selection() -> dict:
    lock = verify_lock()
    d133_result, descriptors = d134.d133_blocks()
    rows_by_seed = {ranker_seed: [] for ranker_seed, _ in SEED_PAIRS}
    context = multiprocessing.get_context("spawn")
    for held_block in range(BLOCKS):
        training_descriptors = [
            item for item in descriptors if int(item["block_id"]) != held_block
        ]
        with ProcessPoolExecutor(
            max_workers=WORKERS, mp_context=context
        ) as executor:
            futures = [
                executor.submit(
                    fold_worker,
                    held_block,
                    training_descriptors,
                    descriptors[held_block],
                    ranker_seed,
                    gate_seed,
                )
                for ranker_seed, gate_seed in SEED_PAIRS
            ]
            rows = sorted(
                (future.result() for future in futures), key=lambda row: row["seed"]
            )
        for row in rows:
            rows_by_seed[row["seed"]].append(row)

    candidates = []
    for ranker_seed, gate_seed in SEED_PAIRS:
        pooled = aggregate_policy_metrics(rows_by_seed[ranker_seed])
        gates = held_policy_gates(pooled)
        candidates.append(
            {
                "seed": ranker_seed,
                "ranker_seed": ranker_seed,
                "gate_seed": gate_seed,
                "folds": rows_by_seed[ranker_seed],
                "held_policy_metrics": pooled,
                "held_policy_gates": gates,
                "eligible": all(gates.values()),
            }
        )
    eligible = [candidate for candidate in candidates if candidate["eligible"]]
    selected = max(eligible, key=selection_key) if eligible else None
    return {
        "schema": "troll-farm-d135a-winner-conditioned-action-gate-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d133_result": {
            "path": str(d134.D133_RESULT.relative_to(ROOT)),
            "sha256": sha256(d134.D133_RESULT),
            "decision": d133_result["decision"],
        },
        "d134_result": {
            "path": str(d134.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d134.OUTPUT),
            "decision": json.loads(d134.OUTPUT.read_text())["decision"],
        },
        "architecture": {
            "parameters": 6_786,
            "ranker_epochs": d119.EPOCHS,
            "gate_epochs": GATE_EPOCHS,
            "soft_value_temperature": d118.TEMPERATURE,
            "target_training_activity": TARGET_ACTIVITY,
            "seed_pairs": SEED_PAIRS,
            "workers": WORKERS,
            "torch_threads_per_worker": 1,
        },
        "candidates": candidates,
        "eligible": len(eligible),
        "selected": selected,
        "decision": (
            "repeat_exact_selection"
            if selected is not None
            else "close_winner_conditioned_action_gate_on_block_transfer"
        ),
    }


def checkpoint_payload(
    model: WinnerController, selected: dict, offset: float
) -> dict:
    return {
        "schema": "troll-farm-d135a-winner-conditioned-action-gate-q6-checkpoint-v1",
        "parameters": 6_786,
        "ranker_epochs": d119.EPOCHS,
        "gate_epochs": GATE_EPOCHS,
        "soft_value_temperature": d118.TEMPERATURE,
        "target_training_activity": TARGET_ACTIVITY,
        "ranker_seed": selected["ranker_seed"],
        "gate_seed": selected["gate_seed"],
        "gate_offset": offset,
        "model_hash": d115.canonical_model_hash(model),
        "state_dict": {
            name: tensor.detach().cpu().contiguous()
            for name, tensor in model.state_dict().items()
        },
    }


def finalize() -> dict:
    lock = verify_lock()
    exact_repeat = SELECTION_A.read_bytes() == SELECTION_B.read_bytes()
    selection = json.loads(SELECTION_A.read_text())
    selected = selection.get("selected") if exact_repeat else None
    full_fit = None
    veto = None
    checkpoint = None
    if selected is not None and selected["eligible"]:
        _, descriptors = d134.d133_blocks()
        training, training_tasks = d134.load_training_data(descriptors)
        model, training_summary = train_winner_controller(
            training, selected["ranker_seed"], selected["gate_seed"]
        )
        training_gate = winner_gate_logits(model, training)
        offset, calibration = d125.activity_calibrated_offset(
            training_tasks,
            training["root_order"],
            training_gate,
            target_activity=TARGET_ACTIVITY,
        )
        full_fit = {
            "training": training_summary,
            "gate_offset": offset,
            "calibration": calibration,
        }
        d126_result = json.loads(d126.OUTPUT.read_text())
        validation = d114.panel(
            d126.VALIDATION_ARMS,
            d126.VALIDATION_BASELINES,
            d126.VALIDATION_START,
            d126.VALIDATION_MAPS,
            float(d126_result["fresh_validation"]["elapsed_seconds"]),
        )
        validation_dataset = d118.soft_value_dataset(validation)
        ranks = d115.model_logits(model.ranker, validation["x"])
        gate_values = winner_gate_logits(model, validation_dataset)
        gate_by_root = dict(
            zip(validation_dataset["root_order"], gate_values, strict=True)
        )
        metrics = d117.factorized_policy_metrics(
            validation, ranks, gate_by_root, offset
        )
        gates = d125.validation_gates(
            metrics, d123.control_crop_rate(validation)
        )
        veto = {
            "authority": "consumed-panel-veto-only",
            "structural_metrics": structural_metrics(model, validation_dataset),
            "metrics": metrics,
            "gates": gates,
            "pass": all(gates.values()),
        }
        if veto["pass"]:
            torch.save(checkpoint_payload(model, selected, offset), CHECKPOINT)
            checkpoint = {
                "path": str(CHECKPOINT.relative_to(ROOT)),
                "sha256": sha256(CHECKPOINT),
                "bytes": CHECKPOINT.stat().st_size,
                "model_hash": training_summary["model_hash"],
            }
        elif CHECKPOINT.exists():
            raise RuntimeError("stale D135 checkpoint exists after veto failure")
        del training, training_tasks, validation, validation_dataset, model
        gc.collect()
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D135 checkpoint exists without repeated selection")

    passed = bool(exact_repeat and selected and veto and veto["pass"])
    result = {
        "schema": "troll-farm-d135a-winner-conditioned-action-gate-q6-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "selection_repeat": {
            "byte_exact": exact_repeat,
            "a_sha256": sha256(SELECTION_A),
            "b_sha256": sha256(SELECTION_B),
            "selected": selected,
        },
        "full_fit": full_fit,
        "consumed_d126_veto": veto,
        "checkpoint": checkpoint,
        "full_pass": passed,
        "decision": (
            "open_final_untouched_9843800_9843815_validation"
            if passed
            else "close_winner_conditioned_action_gate_on_block_transfer"
            if selected is None
            else "close_d135_on_consumed_panel_veto"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("select-a", "select-b", "finalize"))
    args = parser.parse_args()
    if args.command == "finalize":
        finalize()
        return 0
    result = run_selection()
    target = SELECTION_A if args.command == "select-a" else SELECTION_B
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
