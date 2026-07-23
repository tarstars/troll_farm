#!/usr/bin/env python3
"""Interpret exact D151 conditional-second returns under frozen D152 gates."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import statistics

from cgauto import analyze_d151a_conditional_second_corpus as d151
from cgauto import analyze_d148a_priority_joint_teacher as d148
from cgauto import build_d149a_joint_two_stage_dataset as d149
from cgauto import run_d151a_conditional_second_counterfactual as runner
from cgauto import yt_d151_conditional_second_corpus as yt_d151


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d152a-conditional-second-value-analysis-protocol-2026-07-23.md"
LOCK = BASE / "d152a-conditional-second-value-analysis-lock.json"
OUTPUT = BASE / "d152a-conditional-second-value-analysis-result.json"
LABELS = BASE / "d152a-exact-conditional-second-values-9844136-9844199.tsv"
NEAR_TIE_MARGIN = 5

LABEL_FIELDS = (
    "map_seed",
    "seat",
    "opponent",
    "eight_map_fold",
    "target_active",
    "first_boundary",
    "first_slot",
    "second_boundary",
    "candidate_slot",
    "terminal_margin",
    "control_margin",
    "conditional_value",
    "positive_value",
    "near_optimal",
    "original_selected",
    "oracle_selected",
)


def sha256(path: Path) -> str:
    return yt_d151.sha256(path)


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D152 lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def margin(row: dict) -> int:
    return int(row["margin"])


def action_key(row: dict) -> tuple:
    return (
        margin(row),
        int(row["own_score"]),
        -int(row["opponent_score"]),
        -int(row["second_slot"]),
    )


def task_key(row: dict) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def interpret_task(rows: list[dict], target: dict) -> tuple[dict, list[dict]]:
    controls = [row for row in rows if int(row["second_slot"]) == 0]
    noncontrols = [row for row in rows if int(row["second_slot"]) != 0]
    if len(controls) != 1 or not noncontrols:
        raise RuntimeError("D152 task lacks control/noncontrol actions")
    control = controls[0]
    best_noncontrol = max(noncontrols, key=action_key)
    combined = best_noncontrol if margin(best_noncontrol) > margin(control) else control
    original_slot = int(rows[0]["selected_second_slot"])
    original = [row for row in rows if int(row["second_slot"]) == original_slot]
    if len(original) != 1:
        raise RuntimeError("D152 original selected action multiplicity drift")
    original = original[0]
    best_margin = margin(combined)
    active = bool(int(target["target_active"]))
    key = task_key(control)
    values = {
        int(row["second_slot"]): margin(row) - margin(control) for row in rows
    }
    nonselected_near_tie = any(
        slot != original_slot and value >= best_margin - margin(control) - NEAR_TIE_MARGIN
        for slot, value in values.items()
    )
    labels = [
        {
            "map_seed": key[0],
            "seat": key[1],
            "opponent": key[2],
            "eight_map_fold": (key[0] - yt_d151.START_SEED) // yt_d151.MAPS_PER_SHARD,
            "target_active": int(active),
            "first_boundary": int(row["first_boundary"]),
            "first_slot": int(row["first_slot"]),
            "second_boundary": int(row["second_boundary"]),
            "candidate_slot": int(row["second_slot"]),
            "terminal_margin": margin(row),
            "control_margin": margin(control),
            "conditional_value": margin(row) - margin(control),
            "positive_value": int(margin(row) > margin(control)),
            "near_optimal": int(margin(row) >= best_margin - NEAR_TIE_MARGIN),
            "original_selected": int(int(row["second_slot"]) == original_slot),
            "oracle_selected": int(row is combined),
        }
        for row in rows
    ]
    summary = {
        "task": key,
        "opponent": key[2],
        "block": (key[0] - yt_d151.START_SEED) // 16,
        "active": active,
        "control_margin": margin(control),
        "combined_margin": margin(combined),
        "gain": margin(combined) - margin(control),
        "strict": margin(combined) > margin(control),
        "own_gain": int(combined["own_score"]) - int(control["own_score"]),
        "opponent_delta": int(combined["opponent_score"])
        - int(control["opponent_score"]),
        "new_crop_failure": int(control["own_created_crops"]) > 0
        and int(combined["own_created_crops"]) == 0,
        "control_worker_three": int(control["own_workers"]) >= 3,
        "combined_worker_three": int(combined["own_workers"]) >= 3,
        "oracle_slot": int(combined["second_slot"]),
        "original_slot": original_slot,
        "original_exact_best": int(original["second_slot"])
        == int(combined["second_slot"]),
        "original_within_five": margin(original) >= best_margin - NEAR_TIE_MARGIN,
        "nonselected_near_tie": nonselected_near_tie,
        "positive_noncontrol_actions": sum(
            margin(row) > margin(control) for row in noncontrols
        ),
        "near_optimal_actions": sum(
            margin(row) >= best_margin - NEAR_TIE_MARGIN for row in rows
        ),
        "increment_over_original_sequence": best_margin - int(target["sequence_margin"]),
        "increment_over_exact_one_use": best_margin - int(target["one_use_margin"]),
    }
    return summary, labels


def view(items: list[dict]) -> dict:
    if not items:
        raise ValueError("D152 cannot summarize no tasks")
    return {
        "tasks": len(items),
        "mean_gain_over_first_only": statistics.mean(row["gain"] for row in items),
        "strict_tasks": sum(row["strict"] for row in items),
        "strict_rate": statistics.mean(row["strict"] for row in items),
        "mean_own_score_gain": statistics.mean(row["own_gain"] for row in items),
        "mean_opponent_score_delta": statistics.mean(
            row["opponent_delta"] for row in items
        ),
        "new_crop_failures": sum(row["new_crop_failure"] for row in items),
        "control_worker_three_rate": statistics.mean(
            row["control_worker_three"] for row in items
        ),
        "combined_worker_three_rate": statistics.mean(
            row["combined_worker_three"] for row in items
        ),
        "original_exact_best_rate": statistics.mean(
            row["original_exact_best"] for row in items
        ),
        "original_within_five_rate": statistics.mean(
            row["original_within_five"] for row in items
        ),
        "nonselected_near_tie_rate": statistics.mean(
            row["nonselected_near_tie"] for row in items
        ),
        "two_or_more_positive_actions_rate": statistics.mean(
            row["positive_noncontrol_actions"] >= 2 for row in items
        ),
        "mean_increment_over_original_sequence": statistics.mean(
            row["increment_over_original_sequence"] for row in items
        ),
        "mean_increment_over_exact_one_use": statistics.mean(
            row["increment_over_exact_one_use"] for row in items
        ),
    }


def write_or_verify_labels(rows: list[dict]) -> dict:
    if LABELS.exists():
        existing, fields = d151.read_table(LABELS)
        normalized = [{field: str(row[field]) for field in LABEL_FIELDS} for row in rows]
        if fields != list(LABEL_FIELDS) or existing != normalized:
            raise RuntimeError("existing D152 labels disagree with frozen analysis")
        disposition = "verified_existing"
    else:
        with LABELS.open("x", newline="") as target:
            writer = csv.DictWriter(
                target,
                fieldnames=LABEL_FIELDS,
                delimiter="\t",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        disposition = "created"
    return {
        "path": str(LABELS),
        "rows": len(rows),
        "bytes": LABELS.stat().st_size,
        "sha256": sha256(LABELS),
        "disposition": disposition,
    }


def main() -> int:
    lock = verify_lock()
    parent = json.loads(d151.OUTPUT.read_text())
    if parent["decision"] != "open_separately_frozen_d152_value_near_tie_analysis":
        raise RuntimeError("D151 did not authorize D152 value interpretation")
    download = json.loads(yt_d151.DOWNLOAD_RECORD.read_text())
    rows, fields = d151.read_table(Path(download["outputs"]["a"]["path"]))
    if fields != list(runner.OUTPUT_FIELDS):
        raise RuntimeError("D152 branch schema drift")
    targets = d149.load_targets()
    grouped = defaultdict(list)
    for row in rows:
        grouped[task_key(row)].append(row)
    tasks = []
    labels = []
    for key in sorted(grouped):
        summary, task_labels = interpret_task(grouped[key], targets[key])
        tasks.append(summary)
        labels.extend(task_labels)
    all_view = view(tasks)
    active_tasks = [row for row in tasks if row["active"]]
    active_view = view(active_tasks)
    blocks = {
        str(block): view([row for row in active_tasks if row["block"] == block])
        for block in range(4)
    }
    family = {
        opponent: statistics.mean(
            row["gain"] for row in active_tasks if row["opponent"] == opponent
        )
        for opponent in d148.d112.OPPONENTS
    }
    active_view["family_mean_gain"] = family
    active_view["positive_families"] = sum(value > 0 for value in family.values())
    active_view["worst_family_gain"] = min(family.values())
    noncontrol_values = [
        int(row["conditional_value"])
        for row in labels
        if int(row["candidate_slot"]) != 0
    ]
    value_counts = Counter(
        "positive" if value > 0 else "negative" if value < 0 else "zero"
        for value in noncontrol_values
    )
    richness = {
        "noncontrol_action_values": len(noncontrol_values),
        "value_counts": dict(sorted(value_counts.items())),
        "value_mean": statistics.mean(noncontrol_values),
        "value_population_standard_deviation": statistics.pstdev(noncontrol_values),
        "states_with_nonselected_near_tie": sum(
            row["nonselected_near_tie"] for row in tasks
        ),
        "nonselected_near_tie_rate": all_view["nonselected_near_tie_rate"],
        "states_with_two_or_more_positive_actions": sum(
            row["positive_noncontrol_actions"] >= 2 for row in tasks
        ),
        "two_or_more_positive_actions_rate": all_view[
            "two_or_more_positive_actions_rate"
        ],
    }
    gates = {
        "d151_mechanics_passed": parent["pass"],
        "exactly_909_states": len(tasks) == 909,
        "exactly_388_active_states": len(active_tasks) == 388,
        "active_mean_gain_at_least_5": active_view["mean_gain_over_first_only"] >= 5.0,
        "active_strict_at_least_50pct": active_view["strict_rate"] >= 0.50,
        "all_four_active_blocks_positive": all(
            block["mean_gain_over_first_only"] > 0 for block in blocks.values()
        ),
        "at_least_six_positive_families": active_view["positive_families"] >= 6,
        "worst_family_nonnegative": active_view["worst_family_gain"] >= 0.0,
        "zero_new_crop_failures": active_view["new_crop_failures"] == 0,
        "worker_three_within_5pp": active_view["combined_worker_three_rate"]
        >= active_view["control_worker_three_rate"] - 0.05,
        "all_state_mean_gain_at_least_2": all_view["mean_gain_over_first_only"] >= 2.0,
        "all_state_strict_at_least_25pct": all_view["strict_rate"] >= 0.25,
        "nonselected_near_tie_at_least_20pct": richness[
            "nonselected_near_tie_rate"
        ]
        >= 0.20,
        "two_positive_actions_at_least_20pct": richness[
            "two_or_more_positive_actions_rate"
        ]
        >= 0.20,
        "value_stddev_at_least_5": richness[
            "value_population_standard_deviation"
        ]
        >= 5.0,
    }
    passed = all(gates.values())
    label_artifact = write_or_verify_labels(labels) if passed else None
    result = {
        "schema": "troll-farm-d152a-conditional-second-value-analysis-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "parent_d151": {
            "path": str(d151.OUTPUT.relative_to(ROOT)),
            "sha256": sha256(d151.OUTPUT),
            "decision": parent["decision"],
        },
        "all_states": all_view,
        "active_states": active_view,
        "active_blocks": blocks,
        "target_richness": richness,
        "gates": gates,
        "pass": passed,
        "labels": label_artifact,
        "decision": (
            "open_grouped_conditional_value_crossfit"
            if passed
            else "close_conditional_second_distillation"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
