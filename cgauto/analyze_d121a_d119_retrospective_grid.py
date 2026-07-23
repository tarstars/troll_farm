#!/usr/bin/env python3
"""Retrospectively audit D119's frozen grid after qualification has closed."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import evaluate_d119a_held_soft_value_q6 as held_eval
from cgauto import evaluate_d119a_held_coverage_repair as repair
from cgauto import evaluate_d120a_policy_sealed_absolute_information as d120


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d121a-d119-retrospective-grid-protocol-2026-07-22.md"
LOCK = BASE / "d121a-d119-retrospective-grid-lock.json"
OUTPUT = BASE / "d121a-d119-retrospective-grid-result.json"

BLOCK_SPECS = (
    {
        "label": "held0",
        "start": held_eval.HELD_START,
        "arms": held_eval.HELD_ARMS,
        "baselines": held_eval.HELD_BASELINES,
        "elapsed": 551.521,
    },
    *(
        {
            "label": f"repair{block['index']}",
            "start": block["start"],
            "arms": block["arms"],
            "baselines": block["baselines"],
            "elapsed": elapsed,
        }
        for block, elapsed in zip(
            repair.REPAIR_BLOCKS,
            (741.878, 1_137.416, 725.064, 879.309),
            strict=True,
        )
    ),
)


def candidate_id(seed: int, offset: float) -> str:
    return f"{seed}:{offset:+.1f}"


def pearson(left: list[float], right: list[float]) -> float:
    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)
    assert a.shape == b.shape and a.ndim == 1 and len(a) >= 2
    if float(a.std()) == 0.0 or float(b.std()) == 0.0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def compact_metrics(metrics: dict) -> dict:
    return {
        "mean_margin_delta": metrics["mean_margin_delta"],
        "strict_improvement_rate": metrics["strict_improvement_rate"],
        "mean_own_score_delta": metrics["mean_own_score_delta"],
        "mean_opponent_score_delta": metrics["mean_opponent_score_delta"],
        "positive_families": metrics["positive_families"],
        "worst_family": metrics["worst_family"],
        "intervention_rate": metrics["intervention_rate"],
        "crop_rate": metrics["crop_rate"],
        "worker_three_rate": metrics["worker_three_rate"],
        "control_worker_three_rate": metrics["control_worker_three_rate"],
    }


def evaluate_grid(panel: dict, models: dict) -> list[dict]:
    dataset = d118.soft_value_dataset(panel)
    results = []
    grid_index = 0
    for seed in d119.SEEDS:
        model = models[seed]
        ranks = d115.model_logits(model.ranker, panel["x"])
        gate_values = d117.state_gate_logits(model, dataset)
        gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
        for offset in d119.OFFSETS:
            metrics = d117.factorized_policy_metrics(
                panel,
                ranks,
                gate_by_root,
                offset,
            )
            gates = held_eval.held_admission(metrics)
            results.append(
                {
                    "id": candidate_id(seed, offset),
                    "grid_index": grid_index,
                    "seed": seed,
                    "gate_offset": offset,
                    "model_hash": d115.canonical_model_hash(model),
                    "metrics": metrics,
                    "descriptive_held_gates": gates,
                    "descriptive_held_pass": all(gates.values()),
                }
            )
            grid_index += 1
    return results


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    fit = json.loads(d119.FIT_OUTPUT.read_text())
    validation = json.loads(held_eval.VALIDATION_RESULT.read_text())
    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    _, training, _, models = d119.train_models_and_grid(train)
    expected_hashes = {item["seed"]: item["model_hash"] for item in fit["training"]}
    actual_hashes = {item["seed"]: item["model_hash"] for item in training}
    if expected_hashes != actual_hashes:
        raise RuntimeError("D121 did not reproduce the frozen D119 model hashes")

    aggregate = repair.combined_panel(repair.MAX_BLOCKS, d120.ELAPSED, lock)
    d120.enrich_panel(aggregate)
    aggregate_grid = evaluate_grid(aggregate, models)
    aggregate_by_id = {item["id"]: item for item in aggregate_grid}

    block_grids = {}
    block_mechanics = {}
    for spec in BLOCK_SPECS:
        panel = d114.panel(
            spec["arms"],
            spec["baselines"],
            spec["start"],
            repair.BLOCK_MAPS,
            spec["elapsed"],
        )
        block_mechanics[spec["label"]] = panel["mechanics"]
        block_grids[spec["label"]] = {
            item["id"]: compact_metrics(item["metrics"])
            for item in evaluate_grid(panel, models)
        }

    validation_by_id = {
        candidate_id(item["seed"], item["gate_offset"]): item
        for item in validation["grid"]["results"]
    }
    if set(validation_by_id) != set(aggregate_by_id):
        raise RuntimeError("D121 validation and aggregate candidate grids differ")

    metric_names = (
        "mean_margin_delta",
        "strict_improvement_rate",
        "worst_family",
        "intervention_rate",
    )
    correlations = {
        name: pearson(
            [validation_by_id[item["id"]]["metrics"][name] for item in aggregate_grid],
            [item["metrics"][name] for item in aggregate_grid],
        )
        for name in metric_names
    }

    locked_id = candidate_id(
        validation["selected"]["seed"], validation["selected"]["gate_offset"]
    )
    locked = aggregate_by_id[locked_id]
    mean_order = sorted(
        aggregate_grid,
        key=lambda item: item["metrics"]["mean_margin_delta"],
        reverse=True,
    )
    robust_order = sorted(aggregate_grid, key=d115.selection_key, reverse=True)
    descriptive_passes = [
        item for item in aggregate_grid if item["descriptive_held_pass"]
    ]
    best_descriptive = (
        max(descriptive_passes, key=d115.selection_key) if descriptive_passes else None
    )
    locked_blocks = {
        label: grid[locked_id] for label, grid in block_grids.items()
    }
    locked_block_means = [
        metrics["mean_margin_delta"] for metrics in locked_blocks.values()
    ]

    candidates = []
    for item in aggregate_grid:
        identifier = item["id"]
        candidates.append(
            {
                **item,
                "validation_metrics": validation_by_id[identifier]["metrics"],
                "validation_admitted": validation_by_id[identifier]["admitted"],
                "block_metrics": {
                    label: grid[identifier] for label, grid in block_grids.items()
                },
            }
        )

    arms_paths, baseline_paths = repair.input_paths(repair.MAX_BLOCKS)
    result = {
        "schema": "troll-farm-d121a-d119-retrospective-grid-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "scope": "retrospective hypothesis-generation only; no qualification authority",
        "models_reproduced": actual_hashes == expected_hashes,
        "training": training,
        "aggregate_mechanics": aggregate["mechanics"],
        "block_mechanics": block_mechanics,
        "grid": {
            "candidates": len(candidates),
            "descriptive_held_passes": len(descriptive_passes),
            "validation_to_aggregate_pearson": correlations,
            "results": candidates,
        },
        "locked_candidate": {
            "id": locked_id,
            "aggregate": locked,
            "blocks": locked_blocks,
            "block_mean_summary": {
                "mean": float(np.mean(locked_block_means)),
                "standard_deviation": float(np.std(locked_block_means)),
                "minimum": min(locked_block_means),
                "maximum": max(locked_block_means),
            },
            "mean_rank_of_24": mean_order.index(locked) + 1,
            "robust_rank_of_24": robust_order.index(locked) + 1,
        },
        "descriptive_frontier": {
            "best_mean": mean_order[0],
            "best_robust": robust_order[0],
            "best_descriptive_held_pass": best_descriptive,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (
                d119.FIT_OUTPUT,
                held_eval.VALIDATION_RESULT,
                held_eval.CHECKPOINT,
                *arms_paths,
                *baseline_paths,
            )
        },
        "decision": "retrospective_only_generate_next_model_hypothesis",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
