#!/usr/bin/env python3
"""Validate deterministic D147 selected-trajectory feature replays."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
import math
from pathlib import Path

from cgauto import collect_d147a_selected_trajectory_features as d147


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d147a-selected-trajectory-feature-replay-protocol-2026-07-22.md"
CANDIDATE_A = BASE / "d147a-selected-trajectory-candidates-a.tsv"
CANDIDATE_B = BASE / "d147a-selected-trajectory-candidates-b.tsv"
REPLAY_A = BASE / "d147a-selected-trajectory-replays-a.tsv"
REPLAY_B = BASE / "d147a-selected-trajectory-replays-b.tsv"
OUTPUT = BASE / "d147a-selected-trajectory-feature-replay-result.json"

LOCKED_SHA256 = {
    d147.MANIFEST: "88b5e08ec55eae0bc54cacd285af7235b6dfb78181c525a069857be52bc9cf4e",
    d147.REFERENCE: "cbeb74ff83a1b9f29d79ad9d58c495d84ea33537665ab076943a95c31e679ba3",
    ROOT / "cgauto" / "collect_d147a_selected_trajectory_features.py":
        "a9fd01e3e3e1f65b94503723d73fdbf811e6e61a5e133845f656b0e69a2c222d",
    ROOT / "tests" / "test_collect_d147a_selected_trajectory_features.py":
        "42de3adb92c2fba817edb28c55a7cd611583c5868ea8ca7563a09c2335ba5cc0",
    PROTOCOL: "a17dd008f3d062d9e34008026f9b31904219447492ef165c2b0f5b4b5f33673b",
}


def verify_locks() -> dict:
    mismatches = {}
    for path, expected in LOCKED_SHA256.items():
        actual = d147.sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[str(path.relative_to(ROOT))] = {
                "expected": expected,
                "actual": actual,
            }
    return {"mismatches": mismatches, "pass": not mismatches}


def candidate_integrity(rows: list[dict[str, str]], fields: list[str]) -> dict:
    feature_fields = d147.STATE_FIELDS + d147.ACTION_FIELDS
    groups: dict[tuple[int, int], list[dict[str, str]]] = defaultdict(list)
    nonfinite_values = 0
    parse_failures = 0
    for row in rows:
        groups[(int(row["scenario"]), int(row["boundary"]))].append(row)
        for field in feature_fields:
            try:
                if not math.isfinite(float(row[field])):
                    nonfinite_values += 1
            except (KeyError, TypeError, ValueError):
                parse_failures += 1

    metadata_fields = (
        "scenario",
        "map_seed",
        "seat",
        "opponent",
        "reference_task_index",
        "replica",
        "boundary",
        "stage",
        "chosen_slot",
        "legal_candidates",
    )
    failures = Counter()
    stage_counts = Counter()
    chosen_decisions = 0
    for group in groups.values():
        first = group[0]
        legal = int(first["legal_candidates"])
        candidates = [int(row["candidate_slot"]) for row in group]
        chosen = [row for row in group if int(row["chosen"]) == 1]
        if len(group) != legal:
            failures["legal_count"] += 1
        if len(candidates) != len(set(candidates)):
            failures["duplicate_candidate"] += 1
        if 0 not in candidates:
            failures["missing_control"] += 1
        if int(first["chosen_slot"]) not in candidates:
            failures["missing_chosen"] += 1
        if len(chosen) != 1:
            failures["chosen_count"] += 1
        else:
            chosen_decisions += 1
            selected = chosen[0]
            stage = selected["stage"]
            stage_counts[stage] += 1
            slot = int(selected["candidate_slot"])
            if slot != int(selected["chosen_slot"]):
                failures["chosen_slot_mismatch"] += 1
            if stage.startswith("wait_") and slot != 0:
                failures["wait_noncontrol"] += 1
            if stage in {"first", "second"} and slot == 0:
                failures["selected_control"] += 1
            if slot != 0 and not any(
                float(selected[field]) != 0.0 for field in d147.ACTION_FIELDS
            ):
                failures["selected_action_all_zero"] += 1
        state = tuple(first[field] for field in d147.STATE_FIELDS)
        metadata = tuple(first[field] for field in metadata_fields)
        if any(tuple(row[field] for field in d147.STATE_FIELDS) != state for row in group):
            failures["state_inconsistent"] += 1
        if any(tuple(row[field] for field in metadata_fields) != metadata for row in group):
            failures["metadata_inconsistent"] += 1
        controls = [row for row in group if int(row["candidate_slot"]) == 0]
        if len(controls) != 1 or any(
            float(row[field]) != 0.0
            for row in controls
            for field in d147.ACTION_FIELDS
        ):
            failures["control_action_nonzero"] += 1

    return {
        "rows": len(rows),
        "columns": len(fields),
        "state_feature_columns": len(d147.STATE_FIELDS),
        "action_feature_columns": len(d147.ACTION_FIELDS),
        "feature_columns": len(feature_fields),
        "schema_exact": fields == list(d147.CANDIDATE_FIELDS),
        "decision_groups": len(groups),
        "chosen_decisions": chosen_decisions,
        "stage_counts": dict(sorted(stage_counts.items())),
        "parse_failures": parse_failures,
        "nonfinite_values": nonfinite_values,
        "group_failures": dict(sorted(failures.items())),
        "pass": (
            fields == list(d147.CANDIDATE_FIELDS)
            and parse_failures == 0
            and nonfinite_values == 0
            and not failures
        ),
    }


def replay_integrity(rows: list[dict[str, str]], fields: list[str]) -> dict:
    manifest, _ = d147.read_table(d147.MANIFEST)
    reference, _ = d147.read_table(d147.REFERENCE)
    manifest_by_task = {d147.task_key(row): row for row in manifest}
    reference_by_key = {
        (d147.task_key(row), int(row["replica"])): row for row in reference
    }
    failures = Counter()
    seen = set()
    safety_totals = Counter()
    environmental_invalidated_jobs = 0
    for row in rows:
        task = d147.task_key(row)
        if task in seen:
            failures["duplicate_task"] += 1
        seen.add(task)
        selected = manifest_by_task.get(task)
        if selected is None:
            failures["unselected_task"] += 1
            continue
        reference_row = reference_by_key.get((task, int(row["replica"])))
        if reference_row is None:
            failures["missing_reference"] += 1
            continue
        for own_field, manifest_field in (
            ("first_boundary", "first_boundary"),
            ("first_slot", "first_slot"),
            ("second_boundary", "second_boundary"),
            ("second_slot", "second_slot"),
        ):
            if row[own_field] != selected[manifest_field]:
                failures["manifest_action_mismatch"] += 1
        for field in d147.TERMINAL_FIELDS:
            if row[field] != reference_row[field]:
                failures["terminal_mismatch"] += 1
        for field in (
            "invalid_direct_commands",
            "provenance_failures",
            "deposit_prediction_failures",
        ):
            safety_totals[field] += int(row[field])
        environmental_invalidated_jobs += int(row["invalidated_jobs"])
    missing = set(manifest_by_task) - seen
    return {
        "rows": len(rows),
        "schema_exact": fields == list(d147.REPLAY_FIELDS),
        "unique_tasks": len(seen),
        "missing_selected_tasks": len(missing),
        "failures": dict(sorted(failures.items())),
        "safety_totals": dict(sorted(safety_totals.items())),
        "environmental_invalidated_jobs": environmental_invalidated_jobs,
        "pass": (
            fields == list(d147.REPLAY_FIELDS)
            and len(rows) == 57
            and len(seen) == 57
            and not missing
            and not failures
            and not any(safety_totals.values())
        ),
    }


def artifact(path: Path) -> dict:
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": path.stat().st_size,
        "sha256": d147.sha256(path),
    }


def main() -> int:
    locks = verify_locks()
    candidate_a = artifact(CANDIDATE_A)
    candidate_b = artifact(CANDIDATE_B)
    replay_a = artifact(REPLAY_A)
    replay_b = artifact(REPLAY_B)
    candidate_rows, candidate_fields = d147.read_table(CANDIDATE_A)
    replay_rows, replay_fields = d147.read_table(REPLAY_A)
    candidates = candidate_integrity(candidate_rows, candidate_fields)
    replays = replay_integrity(replay_rows, replay_fields)
    gates = {
        "locked_inputs_exact": locks["pass"],
        "candidate_repeats_byte_exact": candidate_a["sha256"] == candidate_b["sha256"],
        "replay_repeats_byte_exact": replay_a["sha256"] == replay_b["sha256"],
        "candidate_schema_and_values_valid": candidates["pass"],
        "exactly_153_decision_groups": candidates["decision_groups"] == 153
        and candidates["chosen_decisions"] == 153,
        "exactly_57_first_and_second_actions": candidates["stage_counts"].get("first") == 57
        and candidates["stage_counts"].get("second") == 57,
        "all_57_terminals_exact_and_safe": replays["pass"],
    }
    passed = all(gates.values())
    result = {
        "schema": "troll-farm-d147a-selected-trajectory-feature-replay-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "locks": locks,
        "artifacts": {
            "candidate-a": candidate_a,
            "candidate-b": candidate_b,
            "replay-a": replay_a,
            "replay-b": replay_b,
        },
        "candidate_integrity": candidates,
        "replay_integrity": replays,
        "gates": gates,
        "pass": passed,
        "decision": (
            "open_d148_new_map_64_priority_joint_two_stage_corpus"
            if passed
            else "repair_d147_feature_replay_interface"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
