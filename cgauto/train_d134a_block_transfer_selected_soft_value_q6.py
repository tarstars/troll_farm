#!/usr/bin/env python3
"""Select the unchanged D119 controller by D133 leave-one-block-out transfer."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path

import numpy as np
import torch

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d133b_q6_support_semantics as d133b
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d134a-block-transfer-selected-soft-value-q6-protocol-2026-07-22.md"
LOCK = BASE / "d134a-block-transfer-selected-soft-value-q6-lock.json"
D133_RESULT = BASE / "d133b-q6-support-semantics-repair-result.json"
D133_ARTIFACT_RESULT = BASE / "d133a-yt-q6-independent-block-corpus-result.json"
SELECTION_A = BASE / "d134a-block-transfer-selected-soft-value-q6-selection-a.json"
SELECTION_B = BASE / "d134a-block-transfer-selected-soft-value-q6-selection-b.json"
CHECKPOINT = BASE / "d134a-block-transfer-selected-soft-value-q6.pt"
OUTPUT = BASE / "d134a-block-transfer-selected-soft-value-q6-result.json"

SEEDS = (13_401, 13_402, 13_403, 13_404)
BLOCKS = 4
TARGET_ACTIVITY = 0.84


def sha256(path: Path) -> str:
    return d117.sha256(path)


def verify_lock() -> dict:
    return d117.verify_manifest(LOCK)


def d133_blocks() -> tuple[dict, list[dict]]:
    result = json.loads(D133_RESULT.read_text())
    if not result.get("full_pass"):
        raise RuntimeError("D133 did not authorize D134 training")
    artifact_result = json.loads(D133_ARTIFACT_RESULT.read_text())
    blocks = sorted(
        artifact_result["blocks"], key=lambda item: int(item["block_id"])
    )
    if [int(item["block_id"]) for item in blocks] != list(range(BLOCKS)):
        raise RuntimeError("D133 result lacks the four prescribed blocks")
    repaired_blocks = sorted(
        result["blocks"], key=lambda item: int(item["block_id"])
    )
    for artifact, repaired in zip(blocks, repaired_blocks, strict=True):
        if (
            int(artifact["block_id"]),
            artifact["artifacts"],
        ) != (
            int(repaired["block_id"]),
            repaired["artifacts"],
        ):
            raise RuntimeError("D133 repair changed a frozen corpus artifact")
    return result, blocks


def load_panel(descriptor: dict) -> dict:
    panel = d114.panel(
        Path(descriptor["artifacts"]["arms"]["path"]),
        Path(descriptor["artifacts"]["baselines"]["path"]),
        int(descriptor["start_seed"]),
        int(descriptor["maps"]),
        float(descriptor["active_seconds_sum"]),
    )
    repaired_mechanics = d133b.exact_mechanics_without_support_gate(
        panel["mechanics"]
    )
    if not repaired_mechanics["pass"]:
        raise RuntimeError(f"D134 block {descriptor['block_id']} mechanics changed")
    return panel


def _pad(tensor: torch.Tensor, proposals: int, value: float | bool) -> torch.Tensor:
    if tensor.shape[1] == proposals:
        return tensor
    shape = list(tensor.shape)
    shape[1] = proposals - tensor.shape[1]
    padding = torch.full(shape, value, dtype=tensor.dtype)
    return torch.cat((tensor, padding), dim=1)


def merge_soft_datasets(datasets: list[dict]) -> dict:
    if not datasets:
        raise ValueError("D134 requires at least one soft-value dataset")
    proposals = max(int(item["action_features"].shape[1]) for item in datasets)
    actions = torch.cat(
        [_pad(item["action_features"], proposals, 0.0) for item in datasets]
    )
    valid = torch.cat([_pad(item["valid"], proposals, False) for item in datasets])
    values = torch.cat(
        [_pad(item["proposal_values"], proposals, float("-inf")) for item in datasets]
    )
    targets = torch.cat(
        [_pad(item["soft_rank_targets"], proposals, 0.0) for item in datasets]
    )
    states = torch.cat([item["state_features"] for item in datasets])
    act_targets = torch.cat([item["act_targets"] for item in datasets])
    root_order = [root for item in datasets for root in item["root_order"]]
    if len(set(root_order)) != len(root_order):
        raise RuntimeError("D134 merged blocks contain duplicate roots")
    if not torch.allclose(targets.sum(1), torch.ones(len(targets)), atol=1.0e-6):
        raise RuntimeError("D134 padded soft targets lost unit mass")
    return {
        "action_features": actions,
        "valid": valid,
        "state_features": states,
        "act_targets": act_targets,
        "proposal_values": values,
        "soft_rank_targets": targets,
        "root_order": root_order,
        "summary": {
            "blocks": len(datasets),
            "roots": len(root_order),
            "arms": int(valid.sum()),
            "maximum_proposals": proposals,
            "target_act_roots": int(act_targets.sum()),
            "target_wait_roots": int((~act_targets).sum()),
            "target_act_root_rate": float(act_targets.float().mean()),
            "soft_value_temperature": d118.TEMPERATURE,
        },
    }


def load_training_data(descriptors: list[dict]) -> tuple[dict, list]:
    datasets = []
    tasks = []
    for descriptor in descriptors:
        panel = load_panel(descriptor)
        tasks.extend(panel["baseline_by_task"])
        datasets.append(d118.soft_value_dataset(panel))
        del panel
        gc.collect()
    return merge_soft_datasets(datasets), tasks


def structural_metrics(model: d117.FactorizedController, dataset: dict) -> dict:
    model.eval()
    with torch.no_grad():
        ranks = d117.proposal_logits(
            model.ranker, dataset["action_features"], dataset["valid"]
        )
        gate = model.gate(dataset["state_features"])
        selected = ranks.argmax(dim=1)
        selected_values = dataset["proposal_values"].gather(
            1, selected[:, None]
        ).squeeze(1)
        best_values = dataset["proposal_values"].max(dim=1).values
        regrets = best_values - selected_values
        act = dataset["act_targets"]
        predicted_act = gate > 0.0
        act_recall = float(predicted_act[act].float().mean())
        wait_recall = float((~predicted_act[~act]).float().mean())
    return {
        "roots": len(regrets),
        "mean_proposal_regret": float(regrets.mean()),
        "within_10_rate": float((regrets <= 10.0).float().mean()),
        "gate_act_recall_at_zero": act_recall,
        "gate_wait_recall_at_zero": wait_recall,
        "gate_balanced_accuracy_at_zero": (act_recall + wait_recall) / 2.0,
    }


def aggregate_policy_metrics(folds: list[dict]) -> dict:
    if not folds:
        raise ValueError("D134 cannot aggregate zero folds")
    tasks = sum(item["tasks"] for item in folds)

    def weighted(field: str) -> float:
        return sum(item[field] * item["tasks"] for item in folds) / tasks

    family = {
        opponent: sum(item["family_mean_margin_delta"][opponent] for item in folds)
        / len(folds)
        for opponent in d112.OPPONENTS
    }
    return {
        "tasks": tasks,
        "mean_margin_delta": weighted("mean_margin_delta"),
        "strict_improvement_rate": weighted("strict_improvement_rate"),
        "mean_own_score_delta": weighted("mean_own_score_delta"),
        "mean_opponent_score_delta": weighted("mean_opponent_score_delta"),
        "family_mean_margin_delta": family,
        "positive_families": sum(value > 0 for value in family.values()),
        "worst_family": min(family.values()),
        "block_mean_margin_delta": {
            str(index): item["mean_margin_delta"] for index, item in enumerate(folds)
        },
        "intervention_rate": weighted("intervention_rate"),
        "crop_rate": weighted("crop_rate"),
        "control_crop_rate": weighted("control_crop_rate"),
        "worker_three_rate": weighted("worker_three_rate"),
        "control_worker_three_rate": weighted("control_worker_three_rate"),
        "positive_score_ties": sum(item["positive_score_ties"] for item in folds),
    }


def held_policy_gates(metrics: dict) -> dict[str, bool]:
    return {
        "pooled_mean_at_least_2": metrics["mean_margin_delta"] >= 2.0,
        "pooled_strict_at_least_40pct": metrics["strict_improvement_rate"] >= 0.40,
        "every_block_nonnegative": min(metrics["block_mean_margin_delta"].values())
        >= 0.0,
        "worst_family_at_least_minus3": metrics["worst_family"] >= -3.0,
        "six_positive_families": metrics["positive_families"] >= 6,
        "own_nonnegative_or_opponent_nonpositive": (
            metrics["mean_own_score_delta"] >= 0.0
            or metrics["mean_opponent_score_delta"] <= 0.0
        ),
        "activity_10_to_85pct": 0.10 <= metrics["intervention_rate"] <= 0.85,
        "crop_not_below_control": metrics["crop_rate"]
        >= metrics["control_crop_rate"],
        "worker_three_within_5pp": metrics["worker_three_rate"]
        >= metrics["control_worker_three_rate"] - 0.05,
    }


def selection_key(candidate: dict) -> tuple:
    metrics = candidate["held_policy_metrics"]
    return (
        min(metrics["block_mean_margin_delta"].values()),
        metrics["worst_family"],
        metrics["mean_margin_delta"],
        metrics["strict_improvement_rate"],
        -metrics["intervention_rate"],
        -candidate["seed"],
    )


def run_selection() -> dict:
    lock = verify_lock()
    d133_result, descriptors = d133_blocks()
    rows_by_seed = {seed: [] for seed in SEEDS}
    for held_block in range(BLOCKS):
        training_descriptors = [
            item for item in descriptors if int(item["block_id"]) != held_block
        ]
        training, training_tasks = load_training_data(training_descriptors)
        held_panel = load_panel(descriptors[held_block])
        held_dataset = d118.soft_value_dataset(held_panel)
        for seed in SEEDS:
            model, training_summary = d119.train_long_model(training, seed)
            training_gate = d117.state_gate_logits(model, training)
            offset, calibration = d125.activity_calibrated_offset(
                training_tasks,
                training["root_order"],
                training_gate,
                target_activity=TARGET_ACTIVITY,
            )
            ranks = d115.model_logits(model.ranker, held_panel["x"])
            held_gate = d117.state_gate_logits(model, held_dataset)
            gate_by_root = dict(
                zip(held_dataset["root_order"], held_gate, strict=True)
            )
            metrics = d117.factorized_policy_metrics(
                held_panel, ranks, gate_by_root, offset
            )
            metrics["control_crop_rate"] = d123.control_crop_rate(held_panel)
            rows_by_seed[seed].append(
                {
                    "held_block": held_block,
                    "seed": seed,
                    "model_hash": training_summary["model_hash"],
                    "gate_offset": offset,
                    "calibration": calibration,
                    "training": training_summary,
                    "held_structural_metrics": structural_metrics(
                        model, held_dataset
                    ),
                    "held_policy_metrics": metrics,
                }
            )
            del model
            gc.collect()
        del training, training_tasks, held_panel, held_dataset
        gc.collect()

    candidates = []
    for seed in SEEDS:
        pooled = aggregate_policy_metrics(
            [row["held_policy_metrics"] for row in rows_by_seed[seed]]
        )
        gates = held_policy_gates(pooled)
        candidates.append(
            {
                "seed": seed,
                "folds": rows_by_seed[seed],
                "held_policy_metrics": pooled,
                "held_policy_gates": gates,
                "eligible": all(gates.values()),
            }
        )
    eligible = [candidate for candidate in candidates if candidate["eligible"]]
    selected = max(eligible, key=selection_key) if eligible else None
    return {
        "schema": "troll-farm-d134a-block-transfer-selection-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d133_result": {
            "path": str(D133_RESULT.relative_to(ROOT)),
            "sha256": sha256(D133_RESULT),
            "decision": d133_result["decision"],
        },
        "d133_artifact_result": {
            "path": str(D133_ARTIFACT_RESULT.relative_to(ROOT)),
            "sha256": sha256(D133_ARTIFACT_RESULT),
        },
        "architecture": {
            "parameters": 6_626,
            "epochs": d119.EPOCHS,
            "soft_value_temperature": d118.TEMPERATURE,
            "target_training_activity": TARGET_ACTIVITY,
            "seeds": SEEDS,
        },
        "candidates": candidates,
        "eligible": len(eligible),
        "selected": selected,
        "decision": (
            "repeat_exact_selection"
            if selected is not None
            else "close_unchanged_d119_abstraction_on_block_transfer"
        ),
    }


def checkpoint_payload(
    model: d117.FactorizedController, selected: dict, offset: float
) -> dict:
    return {
        "schema": "troll-farm-d134a-block-transfer-soft-value-q6-checkpoint-v1",
        "parameters": 6_626,
        "epochs": d119.EPOCHS,
        "soft_value_temperature": d118.TEMPERATURE,
        "target_training_activity": TARGET_ACTIVITY,
        "seed": selected["seed"],
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
        _, descriptors = d133_blocks()
        training, training_tasks = load_training_data(descriptors)
        model, training_summary = d119.train_long_model(training, selected["seed"])
        training_gate = d117.state_gate_logits(model, training)
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
        elapsed = float(d126_result["fresh_validation"]["elapsed_seconds"])
        validation = d114.panel(
            d126.VALIDATION_ARMS,
            d126.VALIDATION_BASELINES,
            d126.VALIDATION_START,
            d126.VALIDATION_MAPS,
            elapsed,
        )
        validation_dataset = d118.soft_value_dataset(validation)
        ranks = d115.model_logits(model.ranker, validation["x"])
        gate_values = d117.state_gate_logits(model, validation_dataset)
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
            raise RuntimeError("stale D134 checkpoint exists after veto failure")
        del training, training_tasks, validation, validation_dataset, model
        gc.collect()
    elif CHECKPOINT.exists():
        raise RuntimeError("stale D134 checkpoint exists without repeated selection")

    passed = bool(exact_repeat and selected and veto and veto["pass"])
    result = {
        "schema": "troll-farm-d134a-block-transfer-selected-soft-value-q6-v1",
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
            else "close_unchanged_d119_abstraction_on_block_transfer"
            if selected is None
            else "close_d134_on_consumed_panel_veto"
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
