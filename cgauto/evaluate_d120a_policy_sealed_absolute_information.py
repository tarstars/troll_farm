#!/usr/bin/env python3
"""Diagnose D119's policy-sealed panel under absolute information gates."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import analyze_d113a_control_aware_dense_q6_teacher as d113
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import evaluate_d119a_held_soft_value_q6 as held_eval
from cgauto import evaluate_d119a_held_coverage_repair as repair


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d120a-policy-sealed-absolute-information-protocol-2026-07-22.md"
LOCK = BASE / "d120a-policy-sealed-absolute-information-lock.json"
OUTPUT = BASE / "d120a-policy-sealed-absolute-information-result.json"

BLOCKS = 4
MAPS = 80
TASKS = 1_280
ELAPSED = 4_035.188


def absolute_information_gates(information: dict) -> dict[str, bool]:
    return {
        "supported_tasks_at_least_1024": information["supported_tasks"] >= 1_024,
        "each_opponent_at_least_128_supported": (
            information["minimum_supported_tasks_per_opponent"] >= 128
        ),
        "each_seat_at_least_512_supported": (
            information["minimum_supported_tasks_per_seat"] >= 512
        ),
        "each_fold_at_least_512_supported": (
            information["minimum_supported_tasks_per_fold"] >= 512
        ),
        "at_least_5000_roots": information["roots"] >= 5_000,
        "each_opponent_at_least_500_roots": (
            information["minimum_roots_per_opponent"] >= 500
        ),
        "at_least_80000_arms": information["arms"] >= 80_000,
        "each_opponent_at_least_8000_arms": (
            information["minimum_arms_per_opponent"] >= 8_000
        ),
    }


def information_counts(panel: dict) -> dict:
    supported = [
        row for row in panel["baselines"] if int(row["boundary_count"]) > 0
    ]
    supported_by_opponent = Counter(row["opponent"] for row in supported)
    supported_by_seat = Counter(int(row["seat"]) for row in supported)
    supported_by_fold = Counter(
        (int(row["map_seed"]) - held_eval.HELD_START) % 2 for row in supported
    )
    roots_by_opponent = Counter(
        task[2] for task, _boundary in panel["arms_by_root"]
    )
    arms_by_opponent = Counter(row["opponent"] for row in panel["arms"])
    assert set(supported_by_opponent) == set(d112.OPPONENTS)
    assert set(supported_by_seat) == {0, 1}
    assert set(supported_by_fold) == {0, 1}
    return {
        "tasks": len(panel["baselines"]),
        "supported_tasks": len(supported),
        "supported_task_rate": len(supported) / len(panel["baselines"]),
        "supported_tasks_by_opponent": dict(sorted(supported_by_opponent.items())),
        "supported_tasks_by_seat": {
            str(key): value for key, value in sorted(supported_by_seat.items())
        },
        "supported_tasks_by_fold": {
            str(key): value for key, value in sorted(supported_by_fold.items())
        },
        "minimum_supported_tasks_per_opponent": min(
            supported_by_opponent.values()
        ),
        "minimum_supported_tasks_per_seat": min(supported_by_seat.values()),
        "minimum_supported_tasks_per_fold": min(supported_by_fold.values()),
        "roots": len(panel["arms_by_root"]),
        "roots_by_opponent": dict(sorted(roots_by_opponent.items())),
        "minimum_roots_per_opponent": min(roots_by_opponent.values()),
        "arms": len(panel["arms"]),
        "arms_by_opponent": dict(sorted(arms_by_opponent.items())),
        "minimum_arms_per_opponent": min(arms_by_opponent.values()),
    }


def absolute_mechanics(panel: dict) -> tuple[dict, dict]:
    information = information_counts(panel)
    original = panel["mechanics"]
    inherited = {
        name: passed
        for name, passed in original["gates"].items()
        if name != "supported_tasks_at_least_90pct"
    }
    gates = {**inherited, **absolute_information_gates(information)}
    mechanics = {
        "schema": "troll-farm-d120a-absolute-information-mechanics-v1",
        "details": original["details"],
        "information": information,
        "removed_fractional_gate": {
            "name": "supported_tasks_at_least_90pct",
            "observed": original["gates"]["supported_tasks_at_least_90pct"],
        },
        "gates": gates,
        "pass": all(gates.values()),
    }
    return mechanics, information


def enrich_panel(panel: dict) -> None:
    teacher, labels = d113.teacher_analysis(
        panel["arms"],
        panel["baseline_by_task"],
        panel["arms_by_root"],
    )
    label_by_key = {
        (d112.task_key(row), int(row["boundary_index"]), int(row["slot"])): row
        for row in labels
    }
    action_fields = [f"action_{index:03}" for index in range(d114.FEATURES)]
    x = np.asarray(
        [[float(row[field]) for field in action_fields] for row in panel["arms"]],
        dtype=np.float64,
    )
    y = np.asarray(
        [label_by_key[d112.arm_key(row)]["act_advantage"] for row in panel["arms"]],
        dtype=np.float64,
    )
    assert x.shape == (len(panel["arms"]), d114.FEATURES)
    assert y.shape == (len(panel["arms"]),)
    assert np.isfinite(x).all() and np.isfinite(y).all()
    assert np.array_equal(x[:, 0], np.ones(len(panel["arms"])))
    panel.update(
        {
            "teacher": teacher,
            "x": x,
            "y": y,
            "root_keys": [d112.root_key(row) for row in panel["arms"]],
        }
    )


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    validation = json.loads(held_eval.VALIDATION_RESULT.read_text())
    model, selected = held_eval.load_locked_controller(validation)
    panel = repair.combined_panel(BLOCKS, ELAPSED, lock)
    assert panel["maps"] == MAPS and len(panel["baselines"]) == TASKS
    mechanics, information = absolute_mechanics(panel)
    metrics = None
    gates = None
    if mechanics["pass"]:
        enrich_panel(panel)
        dataset = d118.soft_value_dataset(panel)
        ranks = d115.model_logits(model.ranker, panel["x"])
        gate_values = d117.state_gate_logits(model, dataset)
        gate_by_root = dict(zip(dataset["root_order"], gate_values, strict=True))
        metrics = d117.factorized_policy_metrics(
            panel,
            ranks,
            gate_by_root,
            selected["gate_offset"],
        )
        gates = held_eval.held_admission(metrics)
    policy_pass = gates is not None and all(gates.values())

    arms_paths, baseline_paths = repair.input_paths(BLOCKS)
    result = {
        "schema": "troll-farm-d120a-policy-sealed-absolute-information-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "scope": (
            "post-mechanics policy-sealed diagnostic; not a retroactive D119 held pass"
        ),
        "checkpoint": {
            "path": str(held_eval.CHECKPOINT.relative_to(ROOT)),
            "sha256": d119.sha256(held_eval.CHECKPOINT),
            "model_hash": d115.canonical_model_hash(model),
            "seed": selected["seed"],
            "gate_offset": selected["gate_offset"],
        },
        "panel": {
            "start_seed": held_eval.HELD_START,
            "end_seed": held_eval.HELD_START + MAPS - 1,
            "maps": MAPS,
            "tasks": TASKS,
            "elapsed_seconds": ELAPSED,
            "mechanics": mechanics,
            "information": information,
            "teacher_signal": panel.get("teacher"),
            "metrics": metrics,
            "admission": gates,
            "pass": policy_pass,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (*arms_paths, *baseline_paths)
        },
        "decision": (
            "open_quantized_rust_parity_and_fresh_final_confirmation"
            if policy_pass
            else "close_on_absolute_information_failure"
            if not mechanics["pass"]
            else "close_without_tuning_on_policy_diagnostic"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
