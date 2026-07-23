#!/usr/bin/env python3
"""Audit D148 population-return support on replayed candidate states."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import statistics

from cgauto import analyze_d148b_priority_joint_support_semantics as d148b
from cgauto import build_d149a_joint_two_stage_dataset as d149_data
from cgauto import yt_d148_priority_joint_teacher as yt_d148


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d150a-population-value-support-audit-protocol-2026-07-23.md"
LOCK = BASE / "d150a-population-value-support-audit-lock.json"
OUTPUT = BASE / "d150a-population-value-support-audit-result.json"
NEAR_TIE_MARGIN = 5


def sha256(path: Path) -> str:
    return yt_d148.sha256(path)


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D150 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def task_key(row: dict) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def join_population_rows(
    stage: str,
    boundary: int,
    manifest: dict,
    population_rows: list[dict],
) -> tuple[list[dict], str]:
    paired = [
        row
        for row in population_rows
        if row["mode"] == "double" and int(row["intervention_batches"]) == 2
    ]
    if stage in {"wait_before_first", "first"}:
        return [
            row
            for row in paired
            if int(row["first_selected_boundary"]) == boundary
        ], "first_selected_slot"
    if stage in {"wait_before_second", "second"}:
        return [
            row
            for row in paired
            if int(row["first_selected_boundary"]) == int(manifest["first_boundary"])
            and int(row["first_selected_slot"]) == int(manifest["first_slot"])
            and int(row["second_selected_boundary"]) == boundary
        ], "second_selected_slot"
    raise ValueError(f"unknown D150 candidate stage: {stage}")


def group_support(
    key: tuple,
    candidates: list[dict],
    manifest: dict,
    population_rows: list[dict],
    active: bool,
) -> dict:
    stage = str(candidates[0]["stage"])
    boundary = int(candidates[0]["boundary"])
    legal = {
        int(row["candidate_slot"])
        for row in candidates
        if int(row["candidate_slot"]) > 0
    }
    joined, slot_field = join_population_rows(
        stage, boundary, manifest, population_rows
    )
    by_slot = defaultdict(list)
    for row in joined:
        by_slot[int(row[slot_field])].append(int(row["margin"]))
    unknown = sorted(set(by_slot) - legal)
    observed = sorted(set(by_slot) & legal)
    selected_stage = stage in {"first", "second"}
    selected_slot = int(candidates[0]["chosen_slot"]) if selected_stage else 0
    selected_observed = not selected_stage or selected_slot in observed
    maxima = {slot: max(by_slot[slot]) for slot in observed}
    means = {
        slot: sum(by_slot[slot]) / len(by_slot[slot]) for slot in observed
    }
    if maxima:
        group_maximum = max(maxima.values())
        near_tie = [
            slot
            for slot, value in maxima.items()
            if value >= group_maximum - NEAR_TIE_MARGIN
        ]
        nonselected_near_tie = any(slot != selected_slot for slot in near_tie)
    else:
        group_maximum = None
        near_tie = []
        nonselected_near_tie = False
    return {
        "map_seed": key[0],
        "seat": key[1],
        "opponent": key[2],
        "boundary": boundary,
        "stage": stage,
        "active_target": active,
        "selected_stage": selected_stage,
        "selected_slot": selected_slot,
        "legal_actions": len(legal),
        "joined_episodes": len(joined),
        "observed_actions": len(observed),
        "action_coverage": len(observed) / len(legal),
        "episodes_per_observed_action_mean": (
            len(joined) / len(observed) if observed else 0.0
        ),
        "selected_action_observed": selected_observed,
        "unknown_joined_slots": unknown,
        "observed_slot_max_margin": {str(slot): maxima[slot] for slot in observed},
        "observed_slot_mean_margin": {str(slot): means[slot] for slot in observed},
        "observed_slot_episodes": {
            str(slot): len(by_slot[slot]) for slot in observed
        },
        "group_maximum_margin": group_maximum,
        "near_tie_slots": near_tie,
        "nonselected_near_tie": nonselected_near_tie,
    }


def support_view(groups: list[dict]) -> dict:
    if not groups:
        return {
            "groups": 0,
            "joined_episodes": 0,
            "selected_actions_observed": 0,
            "groups_at_least_two_actions": 0,
            "groups_at_least_four_actions": 0,
            "median_action_coverage": 0.0,
            "mean_action_coverage": 0.0,
            "nonselected_near_tie_groups": 0,
            "nonselected_near_tie_rate": 0.0,
        }
    selected = [row for row in groups if row["selected_stage"]]
    return {
        "groups": len(groups),
        "joined_episodes": sum(row["joined_episodes"] for row in groups),
        "observed_actions": sum(row["observed_actions"] for row in groups),
        "selected_actions_observed": sum(
            row["selected_action_observed"] for row in selected
        ),
        "groups_at_least_two_actions": sum(
            row["observed_actions"] >= 2 for row in groups
        ),
        "groups_at_least_four_actions": sum(
            row["observed_actions"] >= 4 for row in groups
        ),
        "median_action_coverage": statistics.median(
            row["action_coverage"] for row in groups
        ),
        "mean_action_coverage": statistics.mean(
            row["action_coverage"] for row in groups
        ),
        "minimum_action_coverage": min(row["action_coverage"] for row in groups),
        "maximum_action_coverage": max(row["action_coverage"] for row in groups),
        "nonselected_near_tie_groups": sum(
            row["nonselected_near_tie"] for row in selected
        ),
        "nonselected_near_tie_rate": (
            statistics.mean(row["nonselected_near_tie"] for row in selected)
            if selected
            else 0.0
        ),
    }


def main() -> int:
    lock = verify_lock()
    parent = json.loads(d148b.OUTPUT.read_text())
    if parent["decision"] != "open_d149_grouped_joint_two_stage_policy_fit":
        raise RuntimeError("D148b does not authorize D150 evidence reuse")
    outputs = json.loads(yt_d148.DOWNLOAD_RECORD.read_text())["outputs"]
    population, population_fields = d148b.d148.read_table(
        Path(outputs["population"]["path"])
    )
    manifests, manifest_fields = d148b.d148.read_table(
        Path(outputs["manifest"]["path"])
    )
    targets = d149_data.load_targets()
    population_by_task = defaultdict(list)
    for row in population:
        population_by_task[task_key(row)].append(row)
    manifest_by_task = {task_key(row): row for row in manifests}
    duplicate_manifests = len(manifest_by_task) != len(manifests)
    records = []
    stage_counts = Counter()
    for key, candidates in d149_data.iter_candidate_groups():
        task = key[:3]
        if task not in manifest_by_task or task not in targets:
            raise RuntimeError(f"D150 candidate task lacks manifest/target: {task!r}")
        record = group_support(
            key,
            candidates,
            manifest_by_task[task],
            population_by_task[task],
            bool(int(targets[task]["target_active"])),
        )
        records.append(record)
        stage_counts[record["stage"]] += 1

    active_selected = [
        row for row in records if row["active_target"] and row["selected_stage"]
    ]
    active_first = [row for row in active_selected if row["stage"] == "first"]
    active_second = [row for row in active_selected if row["stage"] == "second"]
    first_view = support_view(active_first)
    second_view = support_view(active_second)
    selected_view = support_view(active_selected)
    mechanics_gates = {
        "d148b_parent_passed": parent["full_pass"],
        "population_schema_exact": population_fields
        == list(d148b.d148.runner.POPULATION_FIELDS),
        "exactly_66560_population_rows": len(population) == 66_560,
        "manifest_schema_exact": manifest_fields
        == list(d148b.d148.runner.MANIFEST_FIELDS),
        "exactly_909_unique_manifests": len(manifests) == 909
        and not duplicate_manifests,
        "exactly_2508_candidate_groups": len(records) == 2_508,
        "exact_stage_counts": dict(sorted(stage_counts.items()))
        == {
            "first": 909,
            "second": 909,
            "wait_before_first": 109,
            "wait_before_second": 581,
        },
        "zero_unknown_joined_slots": not any(
            row["unknown_joined_slots"] for row in records
        ),
        "exactly_776_active_selected_groups": len(active_selected) == 776,
    }
    support_gates = {
        "all_776_selected_actions_observed": selected_view[
            "selected_actions_observed"
        ]
        == 776,
        "first_groups_75pct_at_least_four_actions": first_view[
            "groups_at_least_four_actions"
        ]
        / len(active_first)
        >= 0.75,
        "second_groups_50pct_at_least_two_actions": second_view[
            "groups_at_least_two_actions"
        ]
        / len(active_second)
        >= 0.50,
        "first_median_action_coverage_at_least_25pct": first_view[
            "median_action_coverage"
        ]
        >= 0.25,
        "second_median_action_coverage_at_least_10pct": second_view[
            "median_action_coverage"
        ]
        >= 0.10,
        "at_least_4000_selected_first_joined_episodes": first_view[
            "joined_episodes"
        ]
        >= 4_000,
        "at_least_800_selected_second_joined_episodes": second_view[
            "joined_episodes"
        ]
        >= 800,
        "nonselected_near_tie_at_least_20pct": selected_view[
            "nonselected_near_tie_rate"
        ]
        >= 0.20,
    }
    mechanics_pass = all(mechanics_gates.values())
    support_pass = mechanics_pass and all(support_gates.values())
    result = {
        "schema": "troll-farm-d150a-population-value-support-audit-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent_d148b": {
            "path": str(d148b.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d148b.OUTPUT),
            "decision": parent["decision"],
        },
        "mechanics_gates": mechanics_gates,
        "mechanics_pass": mechanics_pass,
        "support": {
            "active_first": first_view,
            "active_second": second_view,
            "active_selected": selected_view,
            "all_groups": support_view(records),
        },
        "support_gates": support_gates,
        "support_pass": support_pass,
        "groups": records,
        "decision": (
            "open_d150b_population_value_near_tie_learning"
            if support_pass
            else "collect_conditional_second_counterfactual_replays"
            if mechanics_pass
            and all(
                support_gates[name]
                for name in (
                    "first_groups_75pct_at_least_four_actions",
                    "first_median_action_coverage_at_least_25pct",
                    "at_least_4000_selected_first_joined_episodes",
                )
            )
            else "redesign_joint_population_allocation"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
