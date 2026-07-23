#!/usr/bin/env python3
"""Audit transfer for every frozen D130 seed on consumed D126 data."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126
from cgauto import train_d130a_cross_sign_pairwise_soft_ranker as d130


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d131a-d130-all-seed-transfer-audit-protocol-2026-07-22.md"
LOCK = BASE / "d131a-d130-all-seed-transfer-audit-lock.json"
OUTPUT = BASE / "d131a-d130-all-seed-transfer-audit-result.json"


def pearson(left: list[float], right: list[float]) -> float | None:
    x = np.asarray(left, dtype=np.float64)
    y = np.asarray(right, dtype=np.float64)
    if x.shape != y.shape or x.ndim != 1 or len(x) < 2:
        raise ValueError("correlation inputs must be equal vectors")
    if float(x.std()) == 0.0 or float(y.std()) == 0.0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    d130_result = json.loads(d130.OUTPUT.read_text())
    frozen_training = {item["seed"]: item for item in d130_result["training"]}
    frozen_candidates = {
        item["seed"]: item for item in d130_result["fit"]["candidates"]
    }

    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    train_dataset = d118.soft_value_dataset(train)
    d126_result = json.loads(d126.OUTPUT.read_text())
    development = d114.panel(
        d126.VALIDATION_ARMS,
        d126.VALIDATION_BASELINES,
        d126.VALIDATION_START,
        d126.VALIDATION_MAPS,
        d126_result["fresh_validation"]["elapsed_seconds"],
    )
    development_dataset = d118.soft_value_dataset(development)
    rows = []
    for seed in d130.SEEDS:
        model, summary = d130.train_model(train_dataset, seed)
        frozen_summary = frozen_training[seed]
        if summary != frozen_summary:
            raise RuntimeError(f"D131 did not reproduce D130 training seed {seed}")
        gate_values = d117.state_gate_logits(model, train_dataset)
        offset, calibration = d125.activity_calibrated_offset(
            list(train["baseline_by_task"]),
            train_dataset["root_order"],
            gate_values,
        )
        frozen = frozen_candidates[seed]
        if offset != frozen["gate_offset"] or calibration != frozen["state_gate_calibration"]:
            raise RuntimeError(f"D131 did not reproduce D130 offset seed {seed}")
        ranks = d115.model_logits(model.ranker, development["x"])
        gates = d117.state_gate_logits(model, development_dataset)
        gate_by_root = dict(
            zip(development_dataset["root_order"], gates, strict=True)
        )
        metrics = d117.factorized_policy_metrics(
            development, ranks, gate_by_root, offset
        )
        validation_gates = d125.validation_gates(
            metrics, d123.control_crop_rate(development)
        )
        rows.append(
            {
                "seed": seed,
                "selected_by_d130": seed
                == d130_result["fit"]["selected"]["seed"],
                "fit_eligible": frozen["fit_eligible"],
                "model_hash": summary["model_hash"],
                "gate_offset": offset,
                "fit_metrics": frozen["fit_policy_metrics"],
                "training_metrics": {
                    "mean_proposal_regret": summary["train_mean_proposal_regret"],
                    "within_10_rate": summary["train_within_10_rate"],
                    "cross_sign_pair_accuracy": summary[
                        "train_cross_sign_pair_accuracy"
                    ],
                    "cross_sign_winner_positive_rate": summary[
                        "train_cross_sign_winner_positive_rate"
                    ],
                },
                "development_metrics": metrics,
                "development_gates": validation_gates,
                "development_descriptive_pass": all(validation_gates.values()),
            }
        )

    fit_mean = [row["fit_metrics"]["mean_margin_delta"] for row in rows]
    fit_floor = [row["fit_metrics"]["worst_family"] for row in rows]
    regret = [row["training_metrics"]["mean_proposal_regret"] for row in rows]
    pair_accuracy = [
        row["training_metrics"]["cross_sign_pair_accuracy"] for row in rows
    ]
    winner_positive = [
        row["training_metrics"]["cross_sign_winner_positive_rate"] for row in rows
    ]
    development_mean = [
        row["development_metrics"]["mean_margin_delta"] for row in rows
    ]
    development_floor = [
        row["development_metrics"]["worst_family"] for row in rows
    ]
    correlations = {
        "fit_mean_vs_development_mean": pearson(fit_mean, development_mean),
        "fit_floor_vs_development_floor": pearson(fit_floor, development_floor),
        "proposal_regret_vs_development_mean": pearson(regret, development_mean),
        "pair_accuracy_vs_development_mean": pearson(
            pair_accuracy, development_mean
        ),
        "positive_winner_rate_vs_development_mean": pearson(
            winner_positive, development_mean
        ),
    }
    result = {
        "schema": "troll-farm-d131a-d130-all-seed-transfer-audit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "qualification_authority": False,
        "models_reproduced": True,
        "rows": rows,
        "descriptive_passes": sum(
            row["development_descriptive_pass"] for row in rows
        ),
        "correlations": correlations,
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (
                d130.OUTPUT,
                d119.TRAIN_ARMS,
                d119.TRAIN_BASELINES,
                d126.OUTPUT,
                d126.VALIDATION_ARMS,
                d126.VALIDATION_BASELINES,
            )
        },
        "decision": "diagnose_pairwise_objective_vs_selector_only",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
