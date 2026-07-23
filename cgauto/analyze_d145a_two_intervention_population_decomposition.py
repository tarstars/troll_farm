#!/usr/bin/env python3
"""Decompose D144's two-use oracle by sample budget, partition, and move."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import statistics

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112
from cgauto import yt_d144_two_intervention_mc as d144


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d145a-two-intervention-population-decomposition-protocol-2026-07-22.md"
LOCK = BASE / "d145a-two-intervention-population-decomposition-lock.json"
D144B_RESULT = BASE / "d144b-two-intervention-support-semantics-result.json"
OUTPUT = BASE / "d145a-two-intervention-population-decomposition-result.json"
MANIFEST = BASE / "d145a-selected-two-intervention-trajectories.tsv"

FIRST_DOUBLE_REPLICA = 17
DOUBLE_REPLICAS = 111
PREFIX_COUNTS = (8, 16, 32, 64, 111)


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = d144.sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D145 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": d144.sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def _task(row: dict[str, str]) -> tuple[int, int, str]:
    return d144._task(row)


def _arm_key(row: dict[str, str]) -> tuple[tuple[int, int, str], int, int]:
    return _task(row), int(row["boundary_index"]), int(row["slot"])


def population_view(
    mc_rows: list[dict[str, str]],
    arms: list[dict[str, str]],
    baseline_by_task: dict[tuple[int, int, str], dict[str, str]],
    replicas: set[int],
) -> dict:
    selected = [
        row
        for row in mc_rows
        if row["mode"] == "double" and int(row["replica"]) in replicas
    ]
    result = d144._incremental_oracle(selected, arms, baseline_by_task)
    result["replicas"] = sorted(replicas)
    result["replica_count"] = len(replicas)
    result["episode_rows"] = len(selected)
    result["executed_two_rows"] = sum(
        int(row["intervention_batches"]) == 2 for row in selected
    )
    return result


def selected_trajectory_decomposition(
    mc_rows: list[dict[str, str]],
    arms: list[dict[str, str]],
    baseline_by_task: dict[tuple[int, int, str], dict[str, str]],
) -> tuple[dict, list[dict[str, object]]]:
    arms_by_task: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    arms_by_key = {}
    doubles_by_task: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in arms:
        arms_by_task[_task(row)].append(row)
        arms_by_key[_arm_key(row)] = row
    for row in mc_rows:
        if row["mode"] == "double" and int(row["intervention_batches"]) == 2:
            doubles_by_task[_task(row)].append(row)

    selected = []
    for task in sorted(baseline_by_task):
        control = baseline_by_task[task]
        one_rows = arms_by_task.get(task, [])
        best_one = (
            max(one_rows, key=lambda row: d112.tie_key(row, control))
            if one_rows
            else control
        )
        if d144._margin(best_one) <= d144._margin(control):
            best_one = control
        double_rows = doubles_by_task.get(task, [])
        if not double_rows:
            continue
        best_double = max(
            double_rows,
            key=lambda row: d144._outcome_key(
                row, control, int(row["replica"])
            ),
        )
        if d144._margin(best_double) <= d144._margin(best_one):
            continue
        first_key = (
            task,
            int(best_double["first_selected_boundary"]),
            int(best_double["first_selected_slot"]),
        )
        first_arm = arms_by_key.get(first_key)
        if first_arm is None:
            raise RuntimeError(f"D145 selected first arm missing: {first_key!r}")
        best_one_key = _arm_key(best_one) if best_one is not control else None
        control_margin = d144._margin(control)
        one_gain = d144._margin(best_one) - control_margin
        first_gain = d144._margin(first_arm) - control_margin
        sequence_gain = d144._margin(best_double) - control_margin
        selected.append(
            {
                "map_seed": task[0],
                "seat": task[1],
                "opponent": task[2],
                "replica": int(best_double["replica"]),
                "first_boundary": int(best_double["first_selected_boundary"]),
                "second_boundary": int(best_double["second_selected_boundary"]),
                "boundary_gap": int(best_double["second_selected_boundary"])
                - int(best_double["first_selected_boundary"]),
                "first_slot": int(best_double["first_selected_slot"]),
                "second_slot": int(best_double["second_selected_slot"]),
                "first_kind": int(first_arm["kind"]),
                "one_use_gain": one_gain,
                "first_alone_gain": first_gain,
                "sequence_gain": sequence_gain,
                "sequence_increment_over_one": sequence_gain - one_gain,
                "second_lift_over_same_first": sequence_gain - first_gain,
                "first_alone_positive": int(first_gain > 0),
                "first_matches_one_use_oracle": int(first_key == best_one_key),
                "same_representative_slot": int(
                    int(best_double["first_selected_slot"])
                    == int(best_double["second_selected_slot"])
                ),
                "selection_hash": int(best_double["selection_hash"]),
            }
        )
    second_lifts = [int(row["second_lift_over_same_first"]) for row in selected]
    increments = [int(row["sequence_increment_over_one"]) for row in selected]
    summary = {
        "selected_trajectories": len(selected),
        "first_alone_positive_rate": d112.mean(
            row["first_alone_positive"] for row in selected
        ),
        "first_matches_one_use_oracle_rate": d112.mean(
            row["first_matches_one_use_oracle"] for row in selected
        ),
        "same_representative_slot_rate": d112.mean(
            row["same_representative_slot"] for row in selected
        ),
        "mean_one_use_gain": d112.mean(row["one_use_gain"] for row in selected),
        "mean_first_alone_gain": d112.mean(
            row["first_alone_gain"] for row in selected
        ),
        "mean_sequence_gain": d112.mean(row["sequence_gain"] for row in selected),
        "mean_sequence_increment_over_one": d112.mean(increments),
        "minimum_sequence_increment_over_one": min(increments),
        "mean_second_lift_over_same_first": d112.mean(second_lifts),
        "minimum_second_lift_over_same_first": min(second_lifts),
        "median_second_lift_over_same_first": statistics.median(second_lifts),
        "first_boundary_counts": dict(
            sorted(Counter(row["first_boundary"] for row in selected).items())
        ),
        "second_boundary_counts": dict(
            sorted(Counter(row["second_boundary"] for row in selected).items())
        ),
        "boundary_gap_counts": dict(
            sorted(Counter(row["boundary_gap"] for row in selected).items())
        ),
        "first_kind_counts": dict(
            sorted(Counter(row["first_kind"] for row in selected).items())
        ),
        "selected_replica_counts": dict(
            sorted(Counter(row["replica"] for row in selected).items())
        ),
    }
    return summary, selected


def write_manifest(rows: list[dict[str, object]]) -> None:
    with MANIFEST.open("x", newline="") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=list(rows[0]),
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    lock = verify_lock()
    parent = json.loads(D144B_RESULT.read_text())
    if not parent["full_pass"] or parent["decision"] != (
        "open_two_intervention_trajectory_teacher_and_policy_fit"
    ):
        raise RuntimeError("D145 requires the frozen D144b full pass")
    for summary in parent["artifacts"].values():
        path = Path(summary["path"])
        if d144.sha256(path) != summary["sha256"]:
            raise RuntimeError(f"D145 frozen artifact changed: {path}")

    mc_rows, _ = d144._read_table(Path(parent["artifacts"]["mc-a"]["path"]))
    arms, _ = d144._read_table(Path(parent["artifacts"]["arms"]["path"]))
    baselines, _ = d144._read_table(Path(parent["artifacts"]["baselines"]["path"]))
    baseline_by_task = {_task(row): row for row in baselines}
    prefix_views = {}
    for count in PREFIX_COUNTS:
        replicas = set(range(FIRST_DOUBLE_REPLICA, FIRST_DOUBLE_REPLICA + count))
        prefix_views[str(count)] = population_view(
            mc_rows, arms, baseline_by_task, replicas
        )
    partition_views = {
        name: population_view(mc_rows, arms, baseline_by_task, replicas)
        for name, replicas in {
            "even": {
                replica
                for replica in range(
                    FIRST_DOUBLE_REPLICA,
                    FIRST_DOUBLE_REPLICA + DOUBLE_REPLICAS,
                )
                if (replica - FIRST_DOUBLE_REPLICA) % 2 == 0
            },
            "odd": {
                replica
                for replica in range(
                    FIRST_DOUBLE_REPLICA,
                    FIRST_DOUBLE_REPLICA + DOUBLE_REPLICAS,
                )
                if (replica - FIRST_DOUBLE_REPLICA) % 2 == 1
            },
        }.items()
    }
    full_summary = prefix_views[str(DOUBLE_REPLICAS)]["summary"]
    parent_summary = parent["incremental_oracle"]["summary"]
    for field in (
        "mean_increment_beyond_one_use",
        "strict_increment_rate",
        "strict_increment_tasks",
        "positive_families",
        "worst_family_increment",
    ):
        if full_summary[field] != parent_summary[field]:
            raise RuntimeError(f"D145 full-population reproduction failed: {field}")
    final_mean = full_summary["mean_increment_beyond_one_use"]
    saturation = {
        count: prefix_views[str(count)]["summary"][
            "mean_increment_beyond_one_use"
        ]
        / final_mean
        for count in PREFIX_COUNTS
    }
    budget_80 = next(
        (count for count in PREFIX_COUNTS if saturation[count] >= 0.80),
        None,
    )
    trajectory_summary, selected = selected_trajectory_decomposition(
        mc_rows, arms, baseline_by_task
    )
    if len(selected) != parent_summary["strict_increment_tasks"]:
        raise RuntimeError("D145 selected trajectory count drift")
    write_manifest(selected)

    partition_summaries = [view["summary"] for view in partition_views.values()]
    gates = {
        "both_partitions_increment_at_least_2": min(
            item["mean_increment_beyond_one_use"] for item in partition_summaries
        )
        >= 2.0,
        "both_partitions_strict_at_least_25pct": min(
            item["strict_increment_rate"] for item in partition_summaries
        )
        >= 0.25,
        "both_partitions_at_least_six_positive_families": min(
            item["positive_families"] for item in partition_summaries
        )
        >= 6,
        "64_replicas_capture_at_least_80pct_final_mean": saturation[64] >= 0.80,
        "selected_second_lift_mean_at_least_5": trajectory_summary[
            "mean_second_lift_over_same_first"
        ]
        >= 5.0,
        "every_selected_sequence_beats_same_first": trajectory_summary[
            "minimum_second_lift_over_same_first"
        ]
        > 0,
    }
    robust = all(gates.values())
    greedy_compatible = (
        trajectory_summary["first_matches_one_use_oracle_rate"] >= 0.50
    )
    result = {
        "schema": "troll-farm-d145a-two-intervention-population-decomposition-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent": {
            "path": str(D144B_RESULT.relative_to(ROOT)),
            "sha256": d144.sha256(D144B_RESULT),
            "decision": parent["decision"],
        },
        "prefix_views": prefix_views,
        "partition_views": partition_views,
        "saturation_fraction_of_111_replica_mean": saturation,
        "smallest_prefix_at_least_80pct": budget_80,
        "trajectory_decomposition": trajectory_summary,
        "selected_manifest": {
            "path": str(MANIFEST.relative_to(ROOT)),
            "rows": len(selected),
            "sha256": d144.sha256(MANIFEST),
        },
        "gates": gates,
        "pass": robust,
        "greedy_first_stage_compatible": greedy_compatible,
        "decision": (
            "scale_breadth_at_64_double_replicas_and_fit_second_stage_residual"
            if robust and greedy_compatible
            else "scale_breadth_at_64_double_replicas_and_fit_joint_two_stage_policy"
            if robust
            else "increase_per_task_search_before_trajectory_teacher"
            if all(
                gate
                for name, gate in gates.items()
                if name != "64_replicas_capture_at_least_80pct_final_mean"
            )
            else "do_not_scale_current_two_intervention_sampler"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
