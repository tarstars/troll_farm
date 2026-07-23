#!/usr/bin/env python3
"""Repair only D144's two-intervention task-availability denominator."""

from __future__ import annotations

import json
from pathlib import Path

from cgauto import yt_d144_two_intervention_mc as d144


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d144b-two-intervention-support-semantics-protocol-2026-07-22.md"
LOCK = BASE / "d144b-two-intervention-support-semantics-lock.json"
D144_RESULT = BASE / "d144a-two-intervention-mc-pilot-result.json"
OUTPUT = BASE / "d144b-two-intervention-support-semantics-result.json"


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = d144.sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    if mismatches:
        raise RuntimeError(f"D144b lock mismatch: {mismatches!r}")
    return {
        "manifest_sha256": d144.sha256(LOCK),
        "mismatches": mismatches,
        "pass": True,
    }


def repaired_support_mechanics(
    original: dict,
    mc_rows: list[dict[str, str]],
    baselines: list[dict[str, str]],
) -> dict:
    mc_gates = original["mechanics"]["mc"]["gates"]
    coverage_gate = "at_least_95pct_tasks_have_sampled_two_interventions"
    failed_mc_gates = sorted(name for name, passed in mc_gates.items() if not passed)
    baseline_by_task = {d144._task(row): row for row in baselines}
    supported = {
        d144._task(row) for row in baselines if int(row["boundary_count"]) > 0
    }
    unsupported = set(baseline_by_task) - supported
    sampled_two = {
        d144._task(row)
        for row in mc_rows
        if row["mode"] == "double" and int(row["intervention_batches"]) == 2
    }
    unsupported_rows = [row for row in mc_rows if d144._task(row) in unsupported]
    terminal_fields = (
        "own_score",
        "opponent_score",
        "margin",
        "own_workers",
        "successful_trains",
        "own_created_crops",
        "invalid_direct_commands",
        "provenance_failures",
        "deposit_prediction_failures",
        "action_hash",
        "state_hash",
    )
    forced_control_errors = []
    for row in unsupported_rows:
        baseline = baseline_by_task[d144._task(row)]
        if (
            int(row["intervention_batches"]) != 0
            or int(row["margin_delta"]) != 0
            or any(str(row[field]) != str(baseline[field]) for field in terminal_fields)
        ):
            forced_control_errors.append(int(row["task_index"]))
    inherited_other_gates = {
        name: passed for name, passed in mc_gates.items() if name != coverage_gate
    }
    gates = {
        "d144_infrastructure_passed": original["infrastructure"]["pass"],
        "exact_one_use_mechanics_passed": original["mechanics"]["exact_one_use"][
            "pass"
        ],
        "only_failed_mc_gate_was_raw_task_coverage": failed_mc_gates
        == [coverage_gate],
        "all_other_mc_gates_passed": all(inherited_other_gates.values()),
        "baseline_grid_is_complete": len(baseline_by_task) == len(baselines) == 128,
        "at_least_one_supported_task": bool(supported),
        "every_supported_task_has_two_intervention_sample": sampled_two == supported,
        "unsupported_tasks_are_exact_forced_control": not forced_control_errors,
        "raw_two_use_coverage_equals_q6_support_rate": (
            len(sampled_two) / len(baselines) == len(supported) / len(baselines)
        ),
    }
    return {
        "removed_gate": coverage_gate,
        "failed_original_mc_gates": failed_mc_gates,
        "inherited_other_mc_gates": inherited_other_gates,
        "gates": gates,
        "pass": all(gates.values()),
        "details": {
            "tasks": len(baselines),
            "supported_tasks": len(supported),
            "unsupported_forced_control_tasks": len(unsupported),
            "supported_task_rate": len(supported) / len(baselines),
            "tasks_with_two_intervention_sample": len(sampled_two),
            "supported_task_two_use_coverage": (
                len(sampled_two & supported) / len(supported) if supported else 0.0
            ),
            "unsupported_episode_rows": len(unsupported_rows),
            "forced_control_error_samples": forced_control_errors[:10],
        },
    }


def main() -> int:
    lock = verify_lock()
    original = json.loads(D144_RESULT.read_text())
    if original["decision"] != "repair_d144_infrastructure_or_mechanics_only":
        raise RuntimeError("D144a is not at its frozen mechanics-repair boundary")
    if original["incremental_oracle"].get("not_interpreted") != (
        "D144 infrastructure/mechanics failure"
    ):
        raise RuntimeError("D144a target value was already interpreted")
    for summary in original["artifacts"].values():
        path = Path(summary["path"])
        if d144.sha256(path) != summary["sha256"]:
            raise RuntimeError(f"D144b frozen artifact changed: {path}")

    mc_rows, _ = d144._read_table(Path(original["artifacts"]["mc-a"]["path"]))
    arms, _ = d144._read_table(Path(original["artifacts"]["arms"]["path"]))
    baselines, _ = d144._read_table(
        Path(original["artifacts"]["baselines"]["path"])
    )
    repair = repaired_support_mechanics(original, mc_rows, baselines)
    baseline_by_task = {d144._task(row): row for row in baselines}
    oracle = (
        d144._incremental_oracle(mc_rows, arms, baseline_by_task)
        if repair["pass"]
        else {
            "signal_pass": False,
            "safety_pass": False,
            "not_interpreted": "D144b support-semantics repair failed",
        }
    )
    full_pass = repair["pass"] and oracle["signal_pass"] and oracle["safety_pass"]
    result = {
        "schema": "troll-farm-d144b-two-intervention-support-semantics-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "original_d144": {
            "path": str(D144_RESULT.relative_to(ROOT)),
            "sha256": d144.sha256(D144_RESULT),
            "decision": original["decision"],
        },
        "repair": repair,
        "exact_one_use_teacher": original["exact_one_use_teacher"],
        "incremental_oracle": oracle,
        "artifacts": original["artifacts"],
        "full_pass": full_pass,
        "decision": (
            "open_two_intervention_trajectory_teacher_and_policy_fit"
            if full_pass
            else "close_this_two_intervention_mc_population"
            if repair["pass"]
            else "close_d144_after_support_semantics_repair_failure"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
