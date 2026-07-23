#!/usr/bin/env python3
"""Resolve D119's coarse gate-offset interval on the retired D121 panel."""

from __future__ import annotations

import json
from pathlib import Path

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import evaluate_d119a_held_coverage_repair as repair
from cgauto import evaluate_d120a_policy_sealed_absolute_information as d120
from cgauto import analyze_d121a_d119_retrospective_grid as d121
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d124a-d119-fine-gate-calibration-protocol-2026-07-22.md"
LOCK = BASE / "d124a-d119-fine-gate-calibration-lock.json"
OUTPUT = BASE / "d124a-d119-fine-gate-calibration-result.json"

OFFSETS = tuple(value / 100.0 for value in range(-50, 1, 5))


def candidate_id(seed: int, offset: float) -> str:
    return f"{seed}:{offset:+.2f}"


def prepare_policy(panel: dict, model: d117.FactorizedController) -> tuple:
    dataset = d118.soft_value_dataset(panel)
    ranks = d115.model_logits(model.ranker, panel["x"])
    gate_values = d117.state_gate_logits(model, dataset)
    gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
    return ranks, gate_by_root


def policy_metrics(panel: dict, prepared: tuple, offset: float) -> dict:
    ranks, gate_by_root = prepared
    return d117.factorized_policy_metrics(panel, ranks, gate_by_root, offset)


def block_stability_gates(block_metrics: dict[str, dict]) -> dict[str, bool]:
    return {
        "all_five_block_means_nonnegative": all(
            metrics["mean_margin_delta"] >= 0.0
            for metrics in block_metrics.values()
        )
    }


def descriptively_feasible(
    model_gates: dict[str, bool],
    fit_policy_gates: dict[str, bool],
    aggregate_gates: dict[str, bool],
    stability_gates: dict[str, bool],
) -> bool:
    return all(
        all(gates.values())
        for gates in (
            model_gates,
            fit_policy_gates,
            aggregate_gates,
            stability_gates,
        )
    )


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    frozen_fit = json.loads(d119.FIT_OUTPUT.read_text())
    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    _, training, _, models = d119.train_models_and_grid(train)
    expected_hashes = {
        item["seed"]: item["model_hash"] for item in frozen_fit["training"]
    }
    actual_hashes = {item["seed"]: item["model_hash"] for item in training}
    if actual_hashes != expected_hashes:
        raise RuntimeError("D124 did not reproduce the frozen D119 model hashes")

    aggregate = repair.combined_panel(repair.MAX_BLOCKS, d120.ELAPSED, lock)
    d120.enrich_panel(aggregate)
    control_crop = d123.control_crop_rate(aggregate)

    block_panels = {}
    for spec in d121.BLOCK_SPECS:
        panel = d114.panel(
            spec["arms"],
            spec["baselines"],
            spec["start"],
            repair.BLOCK_MAPS,
            spec["elapsed"],
        )
        block_panels[spec["label"]] = panel

    results = []
    grid_index = 0
    for summary in training:
        seed = summary["seed"]
        model = models[seed]
        model_gates = d118.model_fit_gates(summary)
        train_prepared = prepare_policy(train, model)
        aggregate_prepared = prepare_policy(aggregate, model)
        block_prepared = {
            label: prepare_policy(panel, model)
            for label, panel in block_panels.items()
        }
        for offset in OFFSETS:
            fit_metrics = policy_metrics(train, train_prepared, offset)
            fit_gates = d118.fit_policy_gates(fit_metrics)
            aggregate_metrics = policy_metrics(
                aggregate, aggregate_prepared, offset
            )
            aggregate_gates = d123.relative_held_gates(
                aggregate_metrics, control_crop
            )
            blocks = {
                label: d121.compact_metrics(
                    policy_metrics(block_panels[label], prepared, offset)
                )
                for label, prepared in block_prepared.items()
            }
            stability = block_stability_gates(blocks)
            feasible = descriptively_feasible(
                model_gates, fit_gates, aggregate_gates, stability
            )
            results.append(
                {
                    "id": candidate_id(seed, offset),
                    "grid_index": grid_index,
                    "seed": seed,
                    "gate_offset": offset,
                    "model_hash": summary["model_hash"],
                    "model_fit_gates": model_gates,
                    "fit_policy_metrics": fit_metrics,
                    "fit_policy_gates": fit_gates,
                    "aggregate_metrics": aggregate_metrics,
                    "relative_aggregate_gates": aggregate_gates,
                    "block_metrics": blocks,
                    "block_stability_gates": stability,
                    "descriptively_feasible": feasible,
                }
            )
            grid_index += 1

    feasible = [item for item in results if item["descriptively_feasible"]]
    descriptive_best = (
        max(
            feasible,
            key=lambda item: d115.selection_key(
                {
                    "metrics": item["aggregate_metrics"],
                    "grid_index": item["grid_index"],
                }
            ),
        )
        if feasible
        else None
    )
    feasible_offsets_by_seed = {
        str(seed): [
            item["gate_offset"]
            for item in feasible
            if item["seed"] == seed
        ]
        for seed in d119.SEEDS
    }

    arms_paths, baseline_paths = repair.input_paths(repair.MAX_BLOCKS)
    result = {
        "schema": "troll-farm-d124a-d119-fine-gate-calibration-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "scope": "retrospective calibration diagnostic only; no qualification authority",
        "models_reproduced": actual_hashes == expected_hashes,
        "offsets": list(OFFSETS),
        "training": training,
        "aggregate": {
            "maps": d120.MAPS,
            "tasks": d120.TASKS,
            "control_crop_rate": control_crop,
        },
        "grid": {
            "candidates": len(results),
            "descriptively_feasible": len(feasible),
            "feasible_offsets_by_seed": feasible_offsets_by_seed,
            "descriptive_best": descriptive_best,
            "results": results,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (
                d119.FIT_OUTPUT,
                d119.TRAIN_ARMS,
                d119.TRAIN_BASELINES,
                d121.OUTPUT,
                d123.OUTPUT,
                *arms_paths,
                *baseline_paths,
            )
        },
        "decision": (
            "design_prospective_training_only_gate_calibration_rule"
            if feasible
            else "close_fixed_offset_calibration_for_d119"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
