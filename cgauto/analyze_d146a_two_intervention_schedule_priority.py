#!/usr/bin/env python3
"""Test outcome-blind schedule concentration on D144's frozen MC population."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path

from cgauto import analyze_d145a_two_intervention_population_decomposition as d145
from cgauto import yt_d144_two_intervention_mc as d144


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d146a-two-intervention-schedule-priority-protocol-2026-07-22.md"
LOCK = BASE / "d146a-two-intervention-schedule-priority-lock.json"
D144B_RESULT = BASE / "d144b-two-intervention-support-semantics-result.json"
D145_RESULT = BASE / "d145a-two-intervention-population-decomposition-result.json"
OUTPUT = BASE / "d146a-two-intervention-schedule-priority-result.json"


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = d144.sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D146 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": d144.sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def schedule_class(row: dict[str, str]) -> str:
    first = int(row["scheduled_first_boundary"])
    gap = int(row["scheduled_second_boundary"]) - first
    if first == 0 and gap == 1:
        return "early_immediate"
    if first == 0:
        return "early_delayed"
    if gap == 1:
        return "later_immediate"
    return "later_delayed"


def schedule_priority(row: dict[str, str]) -> tuple[int, int, int, int]:
    first = int(row["scheduled_first_boundary"])
    gap = int(row["scheduled_second_boundary"]) - first
    order = {
        "early_immediate": 0,
        "early_delayed": 1,
        "later_immediate": 2,
        "later_delayed": 3,
    }[schedule_class(row)]
    return order, first, gap, int(row["replica"])


def priority_sample(
    mc_rows: list[dict[str, str]], budget: int
) -> list[dict[str, str]]:
    grouped: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in mc_rows:
        if row["mode"] == "double":
            grouped[d144._task(row)].append(row)
    selected = []
    for task in sorted(grouped):
        rows = sorted(grouped[task], key=schedule_priority)
        if len(rows) != d145.DOUBLE_REPLICAS or budget > len(rows):
            raise RuntimeError(f"D146 double population drift for {task!r}")
        selected.extend(rows[:budget])
    return selected


def rows_view(
    rows: list[dict[str, str]],
    arms: list[dict[str, str]],
    baseline_by_task: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    oracle = d144._incremental_oracle(rows, arms, baseline_by_task)
    oracle["episode_rows"] = len(rows)
    oracle["executed_two_rows"] = sum(
        int(row["intervention_batches"]) == 2 for row in rows
    )
    oracle["schedule_class_counts"] = dict(
        sorted(Counter(schedule_class(row) for row in rows).items())
    )
    return oracle


def main() -> int:
    lock = verify_lock()
    d144b = json.loads(D144B_RESULT.read_text())
    d145_result = json.loads(D145_RESULT.read_text())
    if d145_result["decision"] != "increase_per_task_search_before_trajectory_teacher":
        raise RuntimeError("D146 requires D145's frozen unsaturated-population decision")
    for path in (D144B_RESULT, D145_RESULT):
        expected = json.loads(LOCK.read_text())["sha256"][str(path.relative_to(ROOT))]
        if d144.sha256(path) != expected:
            raise RuntimeError(f"D146 parent changed: {path}")
    for summary in d144b["artifacts"].values():
        path = Path(summary["path"])
        if d144.sha256(path) != summary["sha256"]:
            raise RuntimeError(f"D146 artifact changed: {path}")

    mc_rows, _ = d144._read_table(Path(d144b["artifacts"]["mc-a"]["path"]))
    arms, _ = d144._read_table(Path(d144b["artifacts"]["arms"]["path"]))
    baselines, _ = d144._read_table(Path(d144b["artifacts"]["baselines"]["path"]))
    baseline_by_task = {d144._task(row): row for row in baselines}
    priority_views = {
        str(budget): rows_view(
            priority_sample(mc_rows, budget), arms, baseline_by_task
        )
        for budget in (32, 64)
    }
    class_rows = defaultdict(list)
    for row in mc_rows:
        if row["mode"] == "double":
            class_rows[schedule_class(row)].append(row)
    class_views = {
        name: rows_view(rows, arms, baseline_by_task)
        for name, rows in sorted(class_rows.items())
    }

    full_mean = d145_result["prefix_views"]["111"]["summary"][
        "mean_increment_beyond_one_use"
    ]
    uniform32 = d145_result["prefix_views"]["32"]["summary"]
    uniform64 = d145_result["prefix_views"]["64"]["summary"]
    priority32 = priority_views["32"]["summary"]
    priority64 = priority_views["64"]["summary"]
    comparisons = {
        "priority32_mean_minus_uniform32": priority32[
            "mean_increment_beyond_one_use"
        ]
        - uniform32["mean_increment_beyond_one_use"],
        "priority32_strict_minus_uniform32": priority32["strict_increment_rate"]
        - uniform32["strict_increment_rate"],
        "priority64_mean_minus_uniform64": priority64[
            "mean_increment_beyond_one_use"
        ]
        - uniform64["mean_increment_beyond_one_use"],
        "priority64_strict_minus_uniform64": priority64["strict_increment_rate"]
        - uniform64["strict_increment_rate"],
        "priority64_fraction_of_full_mean": priority64[
            "mean_increment_beyond_one_use"
        ]
        / full_mean,
    }
    gates = {
        "priority32_adds_at_least_0_5_vs_uniform32": comparisons[
            "priority32_mean_minus_uniform32"
        ]
        >= 0.5,
        "priority32_strict_not_below_uniform32": comparisons[
            "priority32_strict_minus_uniform32"
        ]
        >= 0.0,
        "priority32_at_least_six_positive_families": priority32[
            "positive_families"
        ]
        >= 6,
        "priority64_retains_at_least_80pct_full_mean": comparisons[
            "priority64_fraction_of_full_mean"
        ]
        >= 0.80,
        "priority64_mean_not_below_uniform64": comparisons[
            "priority64_mean_minus_uniform64"
        ]
        >= 0.0,
        "priority64_strict_not_below_uniform64": comparisons[
            "priority64_strict_minus_uniform64"
        ]
        >= 0.0,
    }
    small_budget_pass = all(list(gates.values())[:3])
    full_pass = all(gates.values())
    result = {
        "schema": "troll-farm-d146a-two-intervention-schedule-priority-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parents": {
            str(D144B_RESULT.relative_to(ROOT)): d144.sha256(D144B_RESULT),
            str(D145_RESULT.relative_to(ROOT)): d144.sha256(D145_RESULT),
        },
        "priority_views": priority_views,
        "schedule_class_views": class_views,
        "uniform_references": {"32": uniform32, "64": uniform64},
        "comparisons": comparisons,
        "gates": gates,
        "pass": full_pass,
        "decision": (
            "scale_breadth_at_64_schedule_priority_for_joint_two_stage_teacher"
            if full_pass
            else "launch_new_boundary_concentrated_population_before_scaling"
            if small_budget_pass
            else "retain_uniform_deeper_search_before_scaling"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
