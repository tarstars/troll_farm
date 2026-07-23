#!/usr/bin/env python3
"""Audit every frozen D135 seed pair on consumed D126 evidence."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import multiprocessing
from pathlib import Path

import numpy as np

from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126
from cgauto import train_d134a_block_transfer_selected_soft_value_q6 as d134
from cgauto import train_d135a_winner_conditioned_action_gate_q6 as d135


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d136a-d135-all-pair-transfer-audit-protocol-2026-07-22.md"
LOCK = BASE / "d136a-d135-all-pair-transfer-audit-lock.json"
AUDIT_A = BASE / "d136a-d135-all-pair-transfer-audit-a.json"
AUDIT_B = BASE / "d136a-d135-all-pair-transfer-audit-b.json"
OUTPUT = BASE / "d136a-d135-all-pair-transfer-audit-result.json"


def sha256(path: Path) -> str:
    return d117.sha256(path)


def verify_lock() -> dict:
    result = d117.verify_manifest(LOCK)
    if not result["pass"]:
        raise RuntimeError(f"D136 lock mismatch: {result['mismatches']!r}")
    return result


def audit_pair(ranker_seed: int, gate_seed: int, held: dict) -> dict:
    _, descriptors = d134.d133_blocks()
    training, training_tasks = d134.load_training_data(descriptors)
    model, training_summary = d135.train_winner_controller(
        training, ranker_seed, gate_seed
    )
    training_gate = d135.winner_gate_logits(model, training)
    offset, calibration = d125.activity_calibrated_offset(
        training_tasks,
        training["root_order"],
        training_gate,
        target_activity=d135.TARGET_ACTIVITY,
    )
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
    gate_values = d135.winner_gate_logits(model, validation_dataset)
    gate_by_root = dict(
        zip(validation_dataset["root_order"], gate_values, strict=True)
    )
    metrics = d117.factorized_policy_metrics(
        validation, ranks, gate_by_root, offset
    )
    gates = d125.validation_gates(metrics, d123.control_crop_rate(validation))
    return {
        "ranker_seed": ranker_seed,
        "gate_seed": gate_seed,
        "model_hash": training_summary["model_hash"],
        "training": training_summary,
        "gate_offset": offset,
        "calibration": calibration,
        "held_selection": {
            "eligible": held["eligible"],
            "mean_margin_delta": held["held_policy_metrics"]["mean_margin_delta"],
            "strict_improvement_rate": held["held_policy_metrics"][
                "strict_improvement_rate"
            ],
            "worst_block": min(
                held["held_policy_metrics"]["block_mean_margin_delta"].values()
            ),
            "worst_family": held["held_policy_metrics"]["worst_family"],
            "activity": held["held_policy_metrics"]["intervention_rate"],
            "failed_gates": [
                name for name, passed in held["held_policy_gates"].items() if not passed
            ],
        },
        "d126_structural_metrics": d135.structural_metrics(
            model, validation_dataset
        ),
        "d126_metrics": metrics,
        "d126_gates": gates,
        "d126_pass": all(gates.values()),
    }


def run_audit() -> dict:
    lock = verify_lock()
    d135.verify_lock()
    selection = json.loads(d135.SELECTION_A.read_text())
    held_by_seed = {
        int(candidate["ranker_seed"]): candidate
        for candidate in selection["candidates"]
    }
    context = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(
        max_workers=d135.WORKERS, mp_context=context
    ) as executor:
        futures = [
            executor.submit(
                audit_pair,
                ranker_seed,
                gate_seed,
                held_by_seed[ranker_seed],
            )
            for ranker_seed, gate_seed in d135.SEED_PAIRS
        ]
        pairs = sorted(
            (future.result() for future in futures),
            key=lambda row: row["ranker_seed"],
        )
    return {
        "schema": "troll-farm-d136a-d135-all-pair-transfer-audit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "d135_result": {
            "path": str(d135.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d135.OUTPUT),
            "decision": json.loads(d135.OUTPUT.read_text())["decision"],
        },
        "authority": "retrospective-diagnostic-only-no-qualification",
        "pairs": pairs,
    }


def pearson(rows: list[dict], held_field: str, d126_field: str) -> float:
    x = np.asarray(
        [row["held_selection"][held_field] for row in rows], dtype=np.float64
    )
    y = np.asarray([row["d126_metrics"][d126_field] for row in rows], dtype=np.float64)
    return float(np.corrcoef(x, y)[0, 1])


def finalize() -> dict:
    lock = verify_lock()
    d135.verify_lock()
    exact = AUDIT_A.read_bytes() == AUDIT_B.read_bytes()
    audit = json.loads(AUDIT_A.read_text())
    pairs = audit["pairs"] if exact else []
    passing = [row for row in pairs if row["d126_pass"]]
    correlations = (
        {
            "held_mean_vs_d126_mean": pearson(
                pairs, "mean_margin_delta", "mean_margin_delta"
            ),
            "held_worst_block_vs_d126_mean": pearson(
                pairs, "worst_block", "mean_margin_delta"
            ),
            "held_worst_family_vs_d126_mean": pearson(
                pairs, "worst_family", "mean_margin_delta"
            ),
            "held_activity_vs_d126_mean": pearson(
                pairs, "activity", "mean_margin_delta"
            ),
        }
        if exact
        else None
    )
    result = {
        "schema": "troll-farm-d136a-d135-all-pair-transfer-audit-result-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "exact_repeat": {
            "byte_exact": exact,
            "a_sha256": sha256(AUDIT_A),
            "b_sha256": sha256(AUDIT_B),
        },
        "authority": "retrospective-diagnostic-only-no-qualification",
        "pairs": pairs,
        "passing_pairs": len(passing),
        "correlations": correlations,
        "decision": (
            "repair_d135_selector_prospectively_without_rescuing_pair"
            if exact and passing
            else "close_d135_winner_conditioned_bce_gate_abstraction"
            if exact
            else "repair_audit_reproducibility_only"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit-a", "audit-b", "finalize"))
    args = parser.parse_args()
    if args.command == "finalize":
        finalize()
        return 0
    result = run_audit()
    target = AUDIT_A if args.command == "audit-a" else AUDIT_B
    target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
