#!/usr/bin/env python3
"""Trace D119's retrospective crop failures without selecting a repaired policy."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import evaluate_d119a_held_soft_value_q6 as held_eval
from cgauto import evaluate_d119a_held_coverage_repair as repair
from cgauto import evaluate_d120a_policy_sealed_absolute_information as d120
from cgauto import analyze_d121a_d119_retrospective_grid as d121


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d122a-d119-crop-failure-trace-protocol-2026-07-22.md"
LOCK = BASE / "d122a-d119-crop-failure-trace-repair1-lock.json"
OUTPUT = BASE / "d122a-d119-crop-failure-trace-result.json"

FOCUS = (
    (11901, 0.0),
    (11903, -1.0),
    (11903, -0.5),
    (11903, 0.0),
    (11904, 0.0),
)
STATE_FEATURE_LABELS = {
    "state_001_turn_at_batch": 1,
    "state_002_own_workers": 2,
    "state_003_opponent_workers": 3,
    "state_004_own_score": 4,
    "state_005_opponent_score": 5,
    "state_006_margin": 6,
    "state_031_natural_live_crops": 31,
    "state_032_own_live_crops": 32,
    "state_033_opponent_live_crops": 33,
    "state_034_ambiguous_live_crops": 34,
    "state_035_natural_fruit": 35,
    "state_036_own_fruit": 36,
    "state_037_opponent_fruit": 37,
    "state_038_ambiguous_fruit": 38,
    "state_039_has_own_live_crop": 39,
    "state_040_has_opponent_live_crop": 40,
    "state_048_completed_batches": 48,
    "state_052_water_fraction": 52,
    "state_053_walkable_fraction": 53,
    "state_054_own_hp": 54,
    "state_055_own_chop": 55,
    "state_056_turn_at_boundary": 56,
    "state_057_boundary_count": 57,
    "state_058_live_own_crops": 58,
    "state_059_remaining_intervention_budget": 59,
}


def task_id(task: tuple[int, int, str]) -> str:
    return f"{task[0]}:{task[1]}:{task[2]}"


def observable_state(row: dict) -> dict:
    return {
        label: float(row[f"state_{index:03}"])
        for label, index in STATE_FEATURE_LABELS.items()
    }


def choice_summary(row: dict, control: dict, rank_score: float, gate_score: float) -> dict:
    return {
        "boundary_index": int(row["boundary_index"]),
        "turn": int(row["turn"]),
        "root_state_hash": row["root_state_hash"],
        "slot": int(row["slot"]),
        "kind": int(row["kind"]),
        "nonteacher": int(row["nonteacher"]),
        "first_action": int(row["first_action"]),
        "second_action": int(row["second_action"]),
        "first_job_kind": int(row["first_job_kind"]),
        "second_job_kind": int(row["second_job_kind"]),
        "first_owner": int(row["first_owner"]),
        "second_owner": int(row["second_owner"]),
        "first_prior_rank": int(row["first_prior_rank"]),
        "second_prior_rank": int(row["second_prior_rank"]),
        "supporter_count": int(row["supporter_count"]),
        "rank_score": rank_score,
        "gate_score": gate_score,
        "margin_delta": d112.margin(row) - d112.margin(control),
        "own_score_delta": int(row["own_score"]) - int(control["own_score"]),
        "opponent_score_delta": (
            int(row["opponent_score"]) - int(control["opponent_score"])
        ),
        "baseline_own_created_crops": int(control["own_created_crops"]),
        "outcome_own_created_crops": int(row["own_created_crops"]),
        "baseline_own_workers": int(control["own_workers"]),
        "outcome_own_workers": int(row["own_workers"]),
        "observable_state": observable_state(row),
    }


def trace_policy(data: dict, model: d117.FactorizedController, offset: float) -> dict:
    dataset = d118.soft_value_dataset(data)
    rank_logits = d115.model_logits(model.ranker, data["x"])
    gate_logits = d117.state_gate_logits(model, dataset)
    rank_by_arm = {
        d112.arm_key(row): float(score)
        for row, score in zip(data["arms"], rank_logits, strict=True)
    }
    gate_by_root = dict(zip(dataset["root_order"], gate_logits, strict=True))
    traces = {}
    crop_failures = {}
    for task, control in data["baseline_by_task"].items():
        choice = None
        choice_rank = None
        choice_gate = None
        for boundary in range(int(control["boundary_count"])):
            root = (task, boundary)
            gate_score = float(gate_by_root[root])
            if gate_score - offset <= 0.0:
                continue
            rows = data["arms_by_root"][root]
            scores = [rank_by_arm[d112.arm_key(row)] for row in rows]
            best_score = max(scores)
            winner = next(index for index, score in enumerate(scores) if score == best_score)
            choice = rows[winner]
            choice_rank = best_score
            choice_gate = gate_score
            break
        outcome = choice or control
        record = {
            "task": task_id(task),
            "map_seed": task[0],
            "seat": task[1],
            "opponent": task[2],
            "intervened": choice is not None,
            "crop": int(outcome["own_created_crops"]) > 0,
            "choice": (
                choice_summary(choice, control, choice_rank, choice_gate)
                if choice is not None
                else None
            ),
        }
        traces[task_id(task)] = record
        if not record["crop"]:
            crop_failures[task_id(task)] = record
    return {
        "traces": traces,
        "crop_failures": crop_failures,
        "rank_by_arm": rank_by_arm,
        "gate_by_root": gate_by_root,
    }


def safe_alternatives(
    data: dict,
    failure: dict,
    rank_by_arm: dict,
    control: dict,
) -> dict:
    choice = failure["choice"]
    if choice is None:
        return {
            "applicable": False,
            "reason": "forced_control_crop_failure_without_intervention",
            "proposal_count": 0,
            "unsafe_proposals": 0,
            "safe_proposals": 0,
            "top_safe_by_model": [],
            "best_safe_by_exact_margin": None,
        }
    task = (failure["map_seed"], failure["seat"], failure["opponent"])
    root = (task, choice["boundary_index"])
    rows = data["arms_by_root"][root]
    safe = [row for row in rows if int(row["own_created_crops"]) > 0]
    ranked = sorted(
        safe,
        key=lambda row: rank_by_arm[d112.arm_key(row)],
        reverse=True,
    )
    oracle = max(safe, key=lambda row: d112.tie_key(row, control)) if safe else None
    return {
        "applicable": True,
        "reason": None,
        "proposal_count": len(rows),
        "unsafe_proposals": sum(int(row["own_created_crops"]) <= 0 for row in rows),
        "safe_proposals": len(safe),
        "top_safe_by_model": [
            choice_summary(
                row,
                control,
                rank_by_arm[d112.arm_key(row)],
                choice["gate_score"],
            )
            for row in ranked[:5]
        ],
        "best_safe_by_exact_margin": (
            choice_summary(
                oracle,
                control,
                rank_by_arm[d112.arm_key(oracle)],
                choice["gate_score"],
            )
            if oracle is not None
            else None
        ),
    }


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    fit = json.loads(d119.FIT_OUTPUT.read_text())
    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    _, training, _, models = d119.train_models_and_grid(train)
    expected = {item["seed"]: item["model_hash"] for item in fit["training"]}
    actual = {item["seed"]: item["model_hash"] for item in training}
    if actual != expected:
        raise RuntimeError("D122 did not reproduce D119 model hashes")

    aggregate = repair.combined_panel(repair.MAX_BLOCKS, d120.ELAPSED, lock)
    d120.enrich_panel(aggregate)
    traces = {}
    failure_frequency = Counter()
    failure_policies = defaultdict(list)
    for seed in d119.SEEDS:
        for offset in d119.OFFSETS:
            identifier = d121.candidate_id(seed, offset)
            traced = trace_policy(aggregate, models[seed], offset)
            traces[identifier] = traced
            for task in traced["crop_failures"]:
                failure_frequency[task] += 1
                failure_policies[task].append(identifier)

    unique_failure_tasks = sorted(failure_frequency)
    details = {}
    for identifier in unique_failure_tasks:
        sample = next(
            traced["crop_failures"][identifier]
            for traced in traces.values()
            if identifier in traced["crop_failures"]
        )
        task = (sample["map_seed"], sample["seat"], sample["opponent"])
        control = aggregate["baseline_by_task"][task]
        per_policy = {}
        for policy in failure_policies[identifier]:
            failure = traces[policy]["crop_failures"][identifier]
            per_policy[policy] = {
                "choice": failure["choice"],
                "safe_alternatives": safe_alternatives(
                    aggregate,
                    failure,
                    traces[policy]["rank_by_arm"],
                    control,
                ),
            }
        details[identifier] = {
            "map_seed": sample["map_seed"],
            "seat": sample["seat"],
            "opponent": sample["opponent"],
            "policies_failing": failure_frequency[identifier],
            "policy_ids": sorted(failure_policies[identifier]),
            "baseline": {
                "own_score": int(control["own_score"]),
                "opponent_score": int(control["opponent_score"]),
                "own_created_crops": int(control["own_created_crops"]),
                "own_workers": int(control["own_workers"]),
                "boundary_count": int(control["boundary_count"]),
            },
            "per_policy": per_policy,
        }

    summaries = {}
    for identifier, traced in traces.items():
        summaries[identifier] = {
            "crop_failures": len(traced["crop_failures"]),
            "failure_tasks": sorted(traced["crop_failures"]),
        }
    focus = {
        d121.candidate_id(seed, offset): summaries[d121.candidate_id(seed, offset)]
        for seed, offset in FOCUS
    }

    arms_paths, baseline_paths = repair.input_paths(repair.MAX_BLOCKS)
    result = {
        "schema": "troll-farm-d122a-d119-crop-failure-trace-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "scope": "retrospective attribution only; safe alternatives use terminal labels",
        "models_reproduced": actual == expected,
        "grid": {
            "candidates": len(traces),
            "policy_failure_summary": summaries,
            "focus": focus,
        },
        "failure_tasks": {
            "unique": len(unique_failure_tasks),
            "frequency": dict(sorted(failure_frequency.items())),
            "details": details,
        },
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (d119.FIT_OUTPUT, *arms_paths, *baseline_paths)
        },
        "decision": "generate_prospective_crop_safety_hypothesis_only",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
