#!/usr/bin/env python3
"""Validate D151's replicated conditional-second corpus without interpreting value."""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path

from cgauto import run_d144a_two_intervention_mc_pilot as d144
from cgauto import run_d151a_conditional_second_counterfactual as runner
from cgauto import yt_d151_conditional_second_corpus as yt_d151


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
LOCK = BASE / "d151a-conditional-second-corpus-analysis-lock.json"
OUTPUT = BASE / "d151a-conditional-second-counterfactual-corpus-result.json"
D148_REPLAYS = (
    BASE
    / "yt"
    / "d148a-priority-joint-teacher-corpus"
    / "d148a-replays-9844136-9844199.tsv"
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
        raise RuntimeError(f"D151 analysis lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def task(row: dict) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def load_plan() -> dict:
    with yt_d151.PLAN.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        if list(reader.fieldnames or ()) != list(runner.PLAN_FIELDS):
            raise RuntimeError("D151 analysis plan schema drift")
        rows = list(reader)
    result = {task(row): {**row, "slots": runner.parse_slots(row["legal_second_slots"])} for row in rows}
    if len(result) != 909 or len(result) != len(rows):
        raise RuntimeError("D151 analysis plan task drift")
    return result


def row_errors(row: dict, plan: dict) -> Counter:
    errors = Counter()
    slots = plan["slots"]
    branch = int(row["branch_ordinal"])
    second_slot = int(row["second_slot"])
    expected_selection_hash = d144.update_selection_hash(
        0, int(plan["first_boundary"]), int(plan["first_slot"])
    )
    if second_slot:
        expected_selection_hash = d144.update_selection_hash(
            expected_selection_hash, int(plan["second_boundary"]), second_slot
        )
    checks = {
        "branch_index": 0 <= branch < len(slots) and slots[branch] == second_slot,
        "scenario": int(row["scenario"]) == int(plan["scenario"]),
        "source_replica": int(row["source_replica"]) == int(plan["source_replica"]),
        "first_boundary": int(row["first_boundary"]) == int(plan["first_boundary"]),
        "first_slot": int(row["first_slot"]) == int(plan["first_slot"]),
        "second_boundary": int(row["second_boundary"]) == int(plan["second_boundary"]),
        "selected_second_slot": int(row["selected_second_slot"])
        == int(plan["selected_second_slot"]),
        "target_active": int(row["target_active"]) == int(plan["target_active"]),
        "selection_hash": int(row["selection_hash"]) == expected_selection_hash,
        "margin_arithmetic": int(row["margin"])
        == int(row["own_score"]) - int(row["opponent_score"]),
        "baseline_arithmetic": int(row["baseline_margin"])
        == int(row["baseline_own_score"]) - int(row["baseline_opponent_score"]),
        "delta_arithmetic": int(row["margin_delta"])
        == int(row["margin"]) - int(row["baseline_margin"]),
        "intervention_count": int(row["intervention_batches"])
        == 1 + int(second_slot != 0),
    }
    for name, passed in checks.items():
        errors[name] += int(not passed)
    return errors


def main() -> int:
    lock = verify_lock()
    download = json.loads(yt_d151.DOWNLOAD_RECORD.read_text())
    outputs = download["outputs"]
    for summary in outputs.values():
        path = Path(summary["path"])
        if sha256(path) != summary["sha256"]:
            raise RuntimeError(f"D151 downloaded artifact changed: {path}")
    a_path = Path(outputs["a"]["path"])
    b_path = Path(outputs["b"]["path"])
    rows, fields = read_table(a_path)
    plan = load_plan()
    reference_rows, _ = read_table(D148_REPLAYS)
    reference = {task(row): row for row in reference_rows}
    by_task = defaultdict(list)
    errors = Counter()
    failures = Counter()
    selected_parity_errors = 0
    selected_rows = 0
    for row in rows:
        key = task(row)
        planned = plan.get(key)
        if planned is None:
            errors["unknown_task"] += 1
            continue
        by_task[key].append(row)
        errors.update(row_errors(row, planned))
        for field in (
            "invalid_direct_commands",
            "provenance_failures",
            "deposit_prediction_failures",
        ):
            failures[field] += int(row[field])
        if int(row["second_slot"]) == int(planned["selected_second_slot"]):
            selected_rows += 1
            expected = reference.get(key)
            if expected is None or any(
                str(row[field]) != str(expected[field])
                for field in runner.TERMINAL_FIELDS
            ):
                selected_parity_errors += 1

    task_set_errors = 0
    duplicate_slots = 0
    for key, planned in plan.items():
        task_rows = by_task.get(key, [])
        slots = [int(row["second_slot"]) for row in task_rows]
        if set(slots) != set(planned["slots"]):
            task_set_errors += 1
        duplicate_slots += len(slots) - len(set(slots))
    metadata = download["mapper_metadata"]
    gates = {
        "operation_completed": download["operation"]["state"] == "completed",
        "exactly_16_mapper_metadata_rows": len(metadata) == 16,
        "all_shards_used_16_threads": all(int(row["threads"]) == 16 for row in metadata),
        "all_shards_within_1200_seconds": all(
            float(row["elapsed_seconds"]) <= yt_d151.MAX_ACTIVE_SECONDS
            for row in metadata
        ),
        "replicas_byte_identical": download["byte_identical"]
        and a_path.read_bytes() == b_path.read_bytes(),
        "schema_exact": fields == list(runner.OUTPUT_FIELDS),
        "exactly_16228_rows": len(rows) == yt_d151.EXPECTED_ROWS,
        "exactly_909_tasks": len(by_task) == 909,
        "exact_plan_slot_sets": task_set_errors == 0,
        "zero_duplicate_task_slots": duplicate_slots == 0,
        "all_909_feature_hashes_verified_per_replica": all(
            sum(
                int(row["runner"]["feature_hashes_verified"])
                for row in metadata
                if row["replica"] == replica
            )
            == 909
            for replica in ("a", "b")
        ),
        "zero_semantic_or_arithmetic_errors": not any(errors.values()),
        "exactly_909_selected_rows": selected_rows == 909,
        "selected_terminals_exactly_reproduce_d148": selected_parity_errors == 0,
        "zero_integrity_failures": not any(failures.values()),
    }
    passed = all(gates.values())
    result = {
        "schema": "troll-farm-d151a-conditional-second-counterfactual-corpus-v1",
        "protocol": str(yt_d151.PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "operation": download["operation"],
        "artifacts": outputs,
        "rows": len(rows),
        "tasks": len(by_task),
        "control_second_branches": sum(int(row["second_slot"]) == 0 for row in rows),
        "noncontrol_second_branches": sum(int(row["second_slot"]) != 0 for row in rows),
        "active_target_branches": sum(int(row["target_active"]) for row in rows),
        "environmental_invalidated_jobs": sum(int(row["invalidated_jobs"]) for row in rows),
        "semantic_errors": dict(sorted(errors.items())),
        "task_slot_set_errors": task_set_errors,
        "duplicate_task_slots": duplicate_slots,
        "selected_parity_errors": selected_parity_errors,
        "integrity_failures": dict(sorted(failures.items())),
        "metadata": metadata,
        "gates": gates,
        "pass": passed,
        "decision": (
            "open_separately_frozen_d152_value_near_tie_analysis"
            if passed
            else "repair_d151_infrastructure_or_mechanics_only"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
