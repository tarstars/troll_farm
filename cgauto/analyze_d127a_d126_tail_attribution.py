#!/usr/bin/env python3
"""Diagnose D126's consumed-panel family tail and calibration frontier."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import fit_d114a_supervised_one_use_q6_linear_scorer as d114
from cgauto import train_d115a_compact_nonlinear_q6_act_classifier as d115
from cgauto import train_d117a_factorized_q6_ranker_state_gate as d117
from cgauto import train_d118a_soft_value_q6_ranker_state_gate as d118
from cgauto import train_d119a_long_fit_soft_value_q6 as d119
from cgauto import analyze_d122a_d119_crop_failure_trace as d122
from cgauto import train_d123a_task_balanced_soft_value_q6 as d123
from cgauto import train_d125a_fit_activity_calibrated_q6 as d125
from cgauto import train_d126a_rank_quality_selected_calibrated_q6 as d126


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d127a-d126-tail-attribution-protocol-2026-07-22.md"
LOCK = BASE / "d127a-d126-tail-attribution-repair1-lock.json"
OUTPUT = BASE / "d127a-d126-tail-attribution-result.json"

SWEEP_OFFSETS = tuple(value / 100.0 for value in range(-10, 51, 5))


def loss_attribution(
    chosen_delta: int, best_root_delta: int, skip_delta: int
) -> str | None:
    if chosen_delta >= 0:
        return None
    if best_root_delta > 0:
        return "proposal_ranking_error"
    if skip_delta > 0:
        return "act_wait_timing_error"
    return "should_abstain_to_control"


def choose(
    data: dict,
    rank_by_arm: dict,
    gate_by_root: dict,
    offset: float,
    *,
    skip_root: tuple | None = None,
):
    for task, control in data["baseline_by_task"].items():
        yield task, control, choose_for_task(
            data,
            task,
            control,
            rank_by_arm,
            gate_by_root,
            offset,
            skip_root=skip_root,
        )


def choose_for_task(
    data: dict,
    task: tuple,
    control: dict,
    rank_by_arm: dict,
    gate_by_root: dict,
    offset: float,
    *,
    skip_root: tuple | None = None,
):
    for boundary in range(int(control["boundary_count"])):
        root = (task, boundary)
        if root == skip_root or gate_by_root[root] - offset <= 0.0:
            continue
        rows = data["arms_by_root"][root]
        best_score = max(rank_by_arm[d112.arm_key(row)] for row in rows)
        return next(
            row for row in rows if rank_by_arm[d112.arm_key(row)] == best_score
        )
    return None


def loss_group_summary(records: list[dict], field: str) -> dict:
    grouped = defaultdict(list)
    for record in records:
        grouped[str(record[field])].append(record["chosen"]["margin_delta"])
    return {
        label: {
            "tasks": len(values),
            "total_margin_delta": sum(values),
            "mean_margin_delta": sum(values) / len(values),
            "minimum_margin_delta": min(values),
        }
        for label, values in sorted(grouped.items())
    }


def trace_losses(data: dict, model: d117.FactorizedController, offset: float) -> dict:
    dataset = d118.soft_value_dataset(data)
    rank_logits = d115.model_logits(model.ranker, data["x"])
    gate_logits = d117.state_gate_logits(model, dataset)
    rank_by_arm = {
        d112.arm_key(row): float(score)
        for row, score in zip(data["arms"], rank_logits, strict=True)
    }
    gate_by_root = dict(zip(dataset["root_order"], gate_logits, strict=True))

    records = []
    interventions = 0
    for task, control, selected in choose(
        data, rank_by_arm, gate_by_root, offset
    ):
        if selected is None:
            continue
        interventions += 1
        chosen_delta = d112.margin(selected) - d112.margin(control)
        if chosen_delta >= 0:
            continue
        root = (task, int(selected["boundary_index"]))
        rows = data["arms_by_root"][root]
        exact_best = max(rows, key=lambda row: d112.tie_key(row, control))
        skipped = choose_for_task(
            data,
            task,
            control,
            rank_by_arm,
            gate_by_root,
            offset,
            skip_root=root,
        )
        skip_outcome = skipped or control
        skip_delta = d112.margin(skip_outcome) - d112.margin(control)
        best_root_delta = d112.margin(exact_best) - d112.margin(control)
        record = {
            "task": d122.task_id(task),
            "map_seed": task[0],
            "seat": task[1],
            "opponent": task[2],
            "root_turn": int(selected["root_turn"]),
            "turn_bin": (int(selected["root_turn"]) // 50) * 50,
            "kind": int(selected["kind"]),
            "first_job_kind": int(selected["first_job_kind"]),
            "second_job_kind": int(selected["second_job_kind"]),
            "first_owner": int(selected["first_owner"]),
            "second_owner": int(selected["second_owner"]),
            "attribution": loss_attribution(
                chosen_delta, best_root_delta, skip_delta
            ),
            "chosen": d122.choice_summary(
                selected,
                control,
                rank_by_arm[d112.arm_key(selected)],
                float(gate_by_root[root]),
            ),
            "exact_best_same_root": d122.choice_summary(
                exact_best,
                control,
                rank_by_arm[d112.arm_key(exact_best)],
                float(gate_by_root[root]),
            ),
            "skip_chosen_root": (
                d122.choice_summary(
                    skipped,
                    control,
                    rank_by_arm[d112.arm_key(skipped)],
                    float(gate_by_root[(task, int(skipped["boundary_index"]))]),
                )
                if skipped is not None
                else None
            ),
            "skip_margin_delta": skip_delta,
        }
        records.append(record)

    records.sort(key=lambda item: (item["chosen"]["margin_delta"], item["task"]))
    attribution = Counter(record["attribution"] for record in records)
    losses_by_opponent = loss_group_summary(records, "opponent")
    result = {
        "interventions": interventions,
        "negative_interventions": len(records),
        "negative_margin_sum": sum(
            record["chosen"]["margin_delta"] for record in records
        ),
        "attribution_counts": dict(sorted(attribution.items())),
        "by_opponent": losses_by_opponent,
        "by_turn_bin": loss_group_summary(records, "turn_bin"),
        "by_kind": loss_group_summary(records, "kind"),
        "by_first_job_kind": loss_group_summary(records, "first_job_kind"),
        "by_second_job_kind": loss_group_summary(records, "second_job_kind"),
        "records": records,
    }
    return result


def evaluate() -> dict:
    lock = d117.verify_manifest(LOCK)
    d126_result = json.loads(d126.OUTPUT.read_text())
    selected = d126_result["fit_result"]["selected"]
    if selected["seed"] != 11903:
        raise RuntimeError("D127 expected D126 seed11903")

    train = d114.panel(
        d119.TRAIN_ARMS,
        d119.TRAIN_BASELINES,
        d119.TRAIN_START,
        d119.TRAIN_MAPS,
        d119.TRAIN_ELAPSED,
    )
    _, training, _, models = d119.train_models_and_grid(train)
    summary = next(item for item in training if item["seed"] == selected["seed"])
    if summary["model_hash"] != selected["model_hash"]:
        raise RuntimeError("D127 did not reproduce selected D126 model")
    model = models[selected["seed"]]

    panel = d114.panel(
        d126.VALIDATION_ARMS,
        d126.VALIDATION_BASELINES,
        d126.VALIDATION_START,
        d126.VALIDATION_MAPS,
        d126_result["fresh_validation"]["elapsed_seconds"],
    )
    dataset = d118.soft_value_dataset(panel)
    train_dataset = d118.soft_value_dataset(train)
    panel_ranks = d115.model_logits(model.ranker, panel["x"])
    train_ranks = d115.model_logits(model.ranker, train["x"])
    panel_gates = dict(
        zip(
            dataset["root_order"],
            d117.state_gate_logits(model, dataset),
            strict=True,
        )
    )
    train_gates = dict(
        zip(
            train_dataset["root_order"],
            d117.state_gate_logits(model, train_dataset),
            strict=True,
        )
    )
    control_crop = d123.control_crop_rate(panel)

    sweep = []
    for offset in SWEEP_OFFSETS:
        fit_metrics = d117.factorized_policy_metrics(
            train, train_ranks, train_gates, offset
        )
        metrics = d117.factorized_policy_metrics(
            panel, panel_ranks, panel_gates, offset
        )
        gates = d125.validation_gates(metrics, control_crop)
        sweep.append(
            {
                "gate_offset": offset,
                "fit_activity": fit_metrics["intervention_rate"],
                "fit_metrics": fit_metrics,
                "validation_metrics": metrics,
                "validation_gates": gates,
                "descriptive_pass": all(gates.values()),
            }
        )
    passes = [item for item in sweep if item["descriptive_pass"]]
    trace = trace_losses(panel, model, selected["gate_offset"])

    result = {
        "schema": "troll-farm-d127a-d126-tail-attribution-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "scope": "consumed-panel diagnosis only; terminal-label attribution is nondeployable",
        "selected_d126": {
            "seed": selected["seed"],
            "model_hash": selected["model_hash"],
            "gate_offset": selected["gate_offset"],
        },
        "threshold_sweep": {
            "offsets": list(SWEEP_OFFSETS),
            "candidates": len(sweep),
            "descriptive_passes": len(passes),
            "passes": passes,
            "results": sweep,
        },
        "loss_trace": trace,
        "artifacts": {
            str(path.relative_to(ROOT)): d119.sha256(path)
            for path in (
                d126.FIT_OUTPUT,
                d126.OUTPUT,
                d126.VALIDATION_ARMS,
                d126.VALIDATION_BASELINES,
            )
        },
        "decision": (
            "design_new_training_only_lower_activity_calibration"
            if passes
            else "design_observable_tail_safety_rule"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> None:
    print(json.dumps(evaluate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
