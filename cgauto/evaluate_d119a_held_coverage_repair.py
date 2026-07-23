#!/usr/bin/env python3
"""Mechanically repair D119a held coverage without changing or searching its policy."""

from __future__ import annotations

import argparse
import json
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


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d119a-held-coverage-repair-protocol-2026-07-22.md"
REPAIR_LOCK = BASE / "d119a-held-coverage-repair-lock.json"
OUTPUT = BASE / "d119a-held-coverage-repair-result.json"

BLOCK_MAPS = 16
MAX_BLOCKS = 4
REPAIR_BLOCKS = tuple(
    {
        "index": index,
        "start": held_eval.HELD_START + held_eval.HELD_MAPS + (index - 1) * BLOCK_MAPS,
    }
    for index in range(1, MAX_BLOCKS + 1)
)
for block in REPAIR_BLOCKS:
    end = block["start"] + BLOCK_MAPS - 1
    block["arms"] = BASE / (
        f"d119a-q6-held-repair{block['index']}-arms-{block['start']}-{end}.tsv"
    )
    block["baselines"] = BASE / (
        f"d119a-q6-held-repair{block['index']}-baselines-{block['start']}-{end}.tsv"
    )


def input_paths(blocks: int) -> tuple[list[Path], list[Path]]:
    if not 1 <= blocks <= MAX_BLOCKS:
        raise ValueError(f"blocks must be from 1 through {MAX_BLOCKS}")
    selected = REPAIR_BLOCKS[:blocks]
    return (
        [held_eval.HELD_ARMS, *(block["arms"] for block in selected)],
        [held_eval.HELD_BASELINES, *(block["baselines"] for block in selected)],
    )


def combined_panel(blocks: int, elapsed: float, frozen: dict) -> dict:
    """Read contiguous blocks and defer reward analysis until mechanics passes."""
    arms_paths, baseline_paths = input_paths(blocks)
    arms = []
    baselines = []
    fields = None
    for arms_path, baselines_path in zip(arms_paths, baseline_paths, strict=True):
        block_arms, block_fields = d114.read_table(arms_path)
        block_baselines, baseline_fields = d114.read_table(baselines_path)
        if fields is None:
            fields = block_fields
        elif block_fields != fields:
            raise RuntimeError(f"arm schema changed in {arms_path}")
        if not baseline_fields:
            raise RuntimeError(f"missing baseline schema in {baselines_path}")
        arms.extend(block_arms)
        baselines.extend(block_baselines)
    assert fields is not None

    maps = held_eval.HELD_MAPS + blocks * BLOCK_MAPS
    d113.START_SEED = held_eval.HELD_START
    d113.MAPS = maps
    mechanics, baseline_by_task, arms_by_root = d113.zero_aware_mechanics(
        arms,
        baselines,
        fields,
        elapsed,
        frozen,
    )
    result = {
        "arms": arms,
        "baselines": baselines,
        "baseline_by_task": baseline_by_task,
        "arms_by_root": arms_by_root,
        "mechanics": mechanics,
        "start": held_eval.HELD_START,
        "maps": maps,
    }
    if not mechanics["pass"]:
        return result

    teacher, labels = d113.teacher_analysis(arms, baseline_by_task, arms_by_root)
    label_by_key = {
        (d112.task_key(row), int(row["boundary_index"]), int(row["slot"])): row
        for row in labels
    }
    action_fields = [f"action_{index:03}" for index in range(d114.FEATURES)]
    x = np.asarray(
        [[float(row[field]) for field in action_fields] for row in arms],
        dtype=np.float64,
    )
    y = np.asarray(
        [label_by_key[d112.arm_key(row)]["act_advantage"] for row in arms],
        dtype=np.float64,
    )
    root_keys = [d112.root_key(row) for row in arms]
    assert x.shape == (len(arms), d114.FEATURES)
    assert y.shape == (len(arms),)
    assert np.isfinite(x).all() and np.isfinite(y).all()
    assert np.array_equal(x[:, 0], np.ones(len(arms)))
    result.update({"teacher": teacher, "x": x, "y": y, "root_keys": root_keys})
    return result


def coverage_only_failure(mechanics: dict) -> bool:
    gates = mechanics["gates"]
    return (
        not gates["supported_tasks_at_least_90pct"]
        and all(
            passed
            for name, passed in gates.items()
            if name != "supported_tasks_at_least_90pct"
        )
    )


def repair_decision(mechanics: dict, policy_pass: bool | None, blocks: int) -> str:
    if mechanics["pass"]:
        return (
            "open_quantized_rust_parity_and_final_untouched_confirmation"
            if policy_pass
            else "close_without_tuning_on_held"
        )
    if coverage_only_failure(mechanics) and blocks < MAX_BLOCKS:
        return "collect_next_frozen_coverage_block_only"
    if coverage_only_failure(mechanics):
        return "close_after_exhausting_frozen_coverage_repair"
    return "close_on_noncoverage_mechanics_failure"


def evaluate(blocks: int, elapsed: float) -> dict:
    repair_lock = d117.verify_manifest(REPAIR_LOCK)
    validation = json.loads(held_eval.VALIDATION_RESULT.read_text())
    model, selected = held_eval.load_locked_controller(validation)
    panel = combined_panel(blocks, elapsed, repair_lock)
    metrics = None
    gates = None
    policy_pass = None
    if panel["mechanics"]["pass"]:
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
        policy_pass = all(gates.values())

    arms_paths, baseline_paths = input_paths(blocks)
    decision = repair_decision(panel["mechanics"], policy_pass, blocks)
    next_block = REPAIR_BLOCKS[blocks] if decision.startswith("collect_next") else None
    result = {
        "schema": "troll-farm-d119a-held-coverage-repair-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "repair_lock": repair_lock,
        "checkpoint": {
            "path": str(held_eval.CHECKPOINT.relative_to(ROOT)),
            "sha256": d119.sha256(held_eval.CHECKPOINT),
            "model_hash": d115.canonical_model_hash(model),
            "seed": selected["seed"],
            "gate_offset": selected["gate_offset"],
        },
        "panel": {
            "blocks": blocks,
            "start_seed": held_eval.HELD_START,
            "end_seed": held_eval.HELD_START + panel["maps"] - 1,
            "maps": panel["maps"],
            "tasks": panel["maps"] * 16,
            "elapsed_seconds": elapsed,
            "mechanics": panel["mechanics"],
            "reward_analysis_deferred_until_mechanics_pass": not panel["mechanics"]["pass"],
            "teacher_signal": panel.get("teacher"),
            "metrics": metrics,
            "admission": gates,
            "pass": policy_pass is True,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (*arms_paths, *baseline_paths)
        },
        "next_block": (
            {
                "index": next_block["index"],
                "start": next_block["start"],
                "maps": BLOCK_MAPS,
                "arms": str(next_block["arms"].relative_to(ROOT)),
                "baselines": str(next_block["baselines"].relative_to(ROOT)),
            }
            if next_block is not None
            else None
        ),
        "decision": decision,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blocks", type=int, required=True)
    parser.add_argument("--elapsed", type=float, required=True)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.blocks, args.elapsed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
