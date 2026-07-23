#!/usr/bin/env python3
"""Analyze the frozen persistent resident-local job-bundle oracle."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import json
import os
from pathlib import Path
import statistics
import tempfile


OPPONENTS = {
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
}
CHECKPOINTS = {50, 100, 150}
JOB_KINDS = {"bank", "fell_bank", "harvest_bank"}
INTEGER_FIELDS = (
    "seed",
    "seat",
    "checkpoint",
    "root_turn",
    "option",
    "unit_id",
    "target_x",
    "target_y",
    "predicted_eta",
    "predicted_reward",
    "overridden_actions",
    "job_end_turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_wood",
    "opponent_wood",
    "terminal_turn",
    "margin_delta",
    "own_score_delta",
    "opponent_score_delta",
    "own_wood_delta",
    "control_own_score",
    "control_opponent_score",
    "control_margin",
    "control_own_wood",
    "control_opponent_wood",
    "control_terminal_turn",
    "baseline_identity_match",
)
CONTROL_FIELDS = (
    "control_own_score",
    "control_opponent_score",
    "control_margin",
    "control_own_wood",
    "control_opponent_wood",
    "control_terminal_turn",
)


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def task_key(row: dict) -> tuple:
    return row["seed"], row["seat"], row["opponent"]


def root_key(row: dict) -> tuple:
    return task_key(row) + (row["checkpoint"], row["root_turn"])


def select_option(options: list[dict]) -> dict:
    """Choose maximum terminal margin; the lower option wins ties, including control."""
    return max(options, key=lambda row: (row["margin_delta"], -row["option"]))


def lower_quantile(values: list[int], fraction: float) -> int:
    ordered = sorted(values)
    return ordered[int((len(ordered) - 1) * fraction)]


def integrity_report(rows: list[dict], repeat_exact: bool | None) -> dict:
    violations: list[dict | str] = []
    expected_tasks = {
        (seed, seat, opponent)
        for seed in range(10)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    actual_tasks = {task_key(row) for row in rows}
    if actual_tasks != expected_tasks:
        violations.append(
            {
                "task_grid": {
                    "missing": sorted(expected_tasks - actual_tasks),
                    "unexpected": sorted(actual_tasks - expected_tasks),
                }
            }
        )

    identities = [root_key(row) + (row["option"],) for row in rows]
    if len(identities) != len(set(identities)):
        violations.append("duplicate root-option rows")

    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[root_key(row)].append(row)
    for key, options in sorted(grouped.items()):
        checkpoint = key[-2]
        root_turn = key[-1]
        if checkpoint not in CHECKPOINTS or root_turn < checkpoint:
            violations.append({"root_timing": key})
        option_ids = sorted(row["option"] for row in options)
        if option_ids != list(range(len(option_ids))):
            violations.append({"option_sequence": [key, option_ids]})
            continue
        control = next(row for row in options if row["option"] == 0)
        if control["job_kind"] != "control" or control["status"] != "control":
            violations.append({"control_label": key})
        if any(control[field] != 0 for field in (
            "margin_delta",
            "own_score_delta",
            "opponent_score_delta",
            "own_wood_delta",
        )):
            violations.append({"control_delta": key})
        expected_control = tuple(control[field] for field in CONTROL_FIELDS)
        for row in options:
            if row["baseline_identity_match"] != 1:
                violations.append({"baseline_identity": root_key(row)})
            if tuple(row[field] for field in CONTROL_FIELDS) != expected_control:
                violations.append({"inconsistent_control": root_key(row)})
            if row["margin"] != row["own_score"] - row["opponent_score"]:
                violations.append({"terminal_margin": root_key(row) + (row["option"],)})
            if row["margin_delta"] != row["margin"] - row["control_margin"]:
                violations.append({"margin_delta": root_key(row) + (row["option"],)})
            if row["own_score_delta"] != row["own_score"] - row["control_own_score"]:
                violations.append({"own_score_delta": root_key(row) + (row["option"],)})
            if row["opponent_score_delta"] != (
                row["opponent_score"] - row["control_opponent_score"]
            ):
                violations.append({"opponent_score_delta": root_key(row) + (row["option"],)})
            if row["own_wood_delta"] != row["own_wood"] - row["control_own_wood"]:
                violations.append({"own_wood_delta": root_key(row) + (row["option"],)})
            if row["option"] > 0 and row["job_kind"] not in JOB_KINDS:
                violations.append({"job_kind": root_key(row) + (row["option"],)})

    controls_by_task: dict[tuple, set[tuple]] = defaultdict(set)
    for row in rows:
        if row["option"] == 0:
            controls_by_task[task_key(row)].add(tuple(row[field] for field in CONTROL_FIELDS))
    if any(len(outcomes) != 1 for outcomes in controls_by_task.values()):
        violations.append("checkpoint controls disagree within a resident game")

    checks = {
        "frozen_task_grid": actual_tasks == expected_tasks,
        "unique_root_options": len(identities) == len(set(identities)),
        "root_and_option_invariants": not violations,
        "repeat_run_byte_identity": repeat_exact is True,
    }
    return {
        "checks": checks,
        "violations": violations[:100],
        "violation_count": len(violations),
        "passed": all(checks.values()) and not violations,
    }


def gate_report(summary: dict, integrity: bool) -> dict:
    kind_counts = summary["selected_job_kinds"]
    family_means = summary["opponent_mean_oracle_margin_delta"]
    checks = {
        "integrity": integrity,
        "root_breadth": summary["roots"] >= 240,
        "option_breadth": summary["noncontrol_options"] >= 2400,
        "noncontrol_selection_rate": summary["selected_noncontrol_rate"] >= 0.10,
        "overall_oracle_delta": summary["mean_oracle_margin_delta"] >= 8.0,
        "selected_root_delta": summary["mean_selected_root_margin_delta"] is not None
        and summary["mean_selected_root_margin_delta"] >= 20.0,
        "job_kind_breadth": sum(count >= 10 for count in kind_counts.values()) >= 2,
        "opponent_breadth": sum(value >= 3.0 for value in family_means.values()) >= 6,
        "weakest_opponent": min(family_means.values()) >= 0.0,
    }
    return {"checks": checks, "passed": all(checks.values())}


def analyze(rows: list[dict], repeat_exact: bool | None = None) -> dict:
    integrity = integrity_report(rows, repeat_exact)
    grouped: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[root_key(row)].append(row)
    if not grouped:
        raise ValueError("oracle input is empty")

    selected = [select_option(options) for _, options in sorted(grouped.items())]
    selected_noncontrol = [row for row in selected if row["option"] > 0]
    noncontrol = [row for row in rows if row["option"] > 0]
    opponent_deltas = {
        opponent: statistics.mean(
            row["margin_delta"] for row in selected if row["opponent"] == opponent
        )
        for opponent in sorted(OPPONENTS)
    }
    checkpoint_deltas = {
        str(checkpoint): statistics.mean(
            row["margin_delta"] for row in selected if row["checkpoint"] == checkpoint
        )
        for checkpoint in sorted(CHECKPOINTS)
    }
    kind_counts = Counter(row["job_kind"] for row in selected_noncontrol)
    status_counts = Counter(row["status"] for row in noncontrol)
    option_counts = [len(options) - 1 for options in grouped.values()]
    oracle_deltas = [row["margin_delta"] for row in selected]
    selected_deltas = [row["margin_delta"] for row in selected_noncontrol]
    kind_metrics = {
        kind: {
            "roots": len(kind_rows),
            "mean_margin_delta": statistics.mean(
                row["margin_delta"] for row in kind_rows
            ),
            "mean_own_score_delta": statistics.mean(
                row["own_score_delta"] for row in kind_rows
            ),
            "mean_opponent_score_delta": statistics.mean(
                row["opponent_score_delta"] for row in kind_rows
            ),
            "completed": sum(row["status"] == "completed" for row in kind_rows),
        }
        for kind in sorted(JOB_KINDS)
        if (kind_rows := [row for row in selected_noncontrol if row["job_kind"] == kind])
    }
    checkpoint_metrics = {}
    for checkpoint in sorted(CHECKPOINTS):
        checkpoint_rows = [row for row in selected if row["checkpoint"] == checkpoint]
        checkpoint_selected = [row for row in checkpoint_rows if row["option"] > 0]
        checkpoint_metrics[str(checkpoint)] = {
            "roots": len(checkpoint_rows),
            "selected_noncontrol_roots": len(checkpoint_selected),
            "selected_noncontrol_rate": len(checkpoint_selected) / len(checkpoint_rows),
            "mean_oracle_margin_delta": statistics.mean(
                row["margin_delta"] for row in checkpoint_rows
            ),
            "mean_selected_root_margin_delta": (
                statistics.mean(row["margin_delta"] for row in checkpoint_selected)
                if checkpoint_selected
                else None
            ),
        }
    score_mechanisms = Counter()
    for row in selected_noncontrol:
        if row["own_score_delta"] > 0 and row["opponent_score_delta"] < 0:
            score_mechanisms["own_gain_and_opponent_suppression"] += 1
        elif row["own_score_delta"] > 0:
            score_mechanisms["own_gain_only"] += 1
        elif row["opponent_score_delta"] < 0:
            score_mechanisms["opponent_suppression_only"] += 1
        else:
            score_mechanisms["other"] += 1
    summary = {
        "resident_games": len({task_key(row) for row in rows}),
        "roots": len(grouped),
        "rows": len(rows),
        "noncontrol_options": len(noncontrol),
        "noncontrol_options_per_root": {
            "minimum": min(option_counts),
            "mean": statistics.mean(option_counts),
            "maximum": max(option_counts),
        },
        "selected_noncontrol_roots": len(selected_noncontrol),
        "selected_noncontrol_rate": len(selected_noncontrol) / len(selected),
        "mean_oracle_margin_delta": statistics.mean(oracle_deltas),
        "oracle_margin_delta_distribution": {
            "minimum": min(oracle_deltas),
            "median": statistics.median(oracle_deltas),
            "p75": lower_quantile(oracle_deltas, 0.75),
            "p90": lower_quantile(oracle_deltas, 0.90),
            "maximum": max(oracle_deltas),
        },
        "mean_selected_root_margin_delta": (
            statistics.mean(selected_deltas)
            if selected_noncontrol
            else None
        ),
        "selected_root_margin_delta_distribution": (
            {
                "minimum": min(selected_deltas),
                "median": statistics.median(selected_deltas),
                "p75": lower_quantile(selected_deltas, 0.75),
                "p90": lower_quantile(selected_deltas, 0.90),
                "maximum": max(selected_deltas),
            }
            if selected_deltas
            else None
        ),
        "mean_selected_own_score_delta": (
            statistics.mean(row["own_score_delta"] for row in selected_noncontrol)
            if selected_noncontrol
            else None
        ),
        "mean_selected_opponent_score_delta": (
            statistics.mean(row["opponent_score_delta"] for row in selected_noncontrol)
            if selected_noncontrol
            else None
        ),
        "selected_job_kinds": {
            kind: kind_counts.get(kind, 0) for kind in sorted(JOB_KINDS)
        },
        "selected_job_kind_metrics": kind_metrics,
        "selected_status_counts": dict(
            sorted(Counter(row["status"] for row in selected_noncontrol).items())
        ),
        "selected_score_mechanisms": dict(sorted(score_mechanisms.items())),
        "selected_with_negative_own_score": sum(
            row["own_score_delta"] < 0 for row in selected_noncontrol
        ),
        "opponent_mean_oracle_margin_delta": opponent_deltas,
        "checkpoint_mean_oracle_margin_delta": checkpoint_deltas,
        "checkpoint_metrics": checkpoint_metrics,
        "seat_mean_oracle_margin_delta": {
            str(seat): statistics.mean(
                row["margin_delta"] for row in selected if row["seat"] == seat
            )
            for seat in (0, 1)
        },
        "seed_mean_oracle_margin_delta": {
            str(seed): statistics.mean(
                row["margin_delta"] for row in selected if row["seed"] == seed
            )
            for seed in range(10)
        },
        "job_status_counts": dict(sorted(status_counts.items())),
        "completed_noncontrol_options": status_counts.get("completed", 0),
        "completed_noncontrol_rate": status_counts.get("completed", 0) / len(noncontrol),
    }
    examples = sorted(
        selected_noncontrol,
        key=lambda row: (-row["margin_delta"], root_key(row), row["option"]),
    )[:20]
    summary["largest_selected_examples"] = [
        {
            "seed": row["seed"],
            "seat": row["seat"],
            "opponent": row["opponent"],
            "checkpoint": row["checkpoint"],
            "root_turn": row["root_turn"],
            "job_kind": row["job_kind"],
            "unit_id": row["unit_id"],
            "target": [row["target_x"], row["target_y"]],
            "margin_delta": row["margin_delta"],
            "own_score_delta": row["own_score_delta"],
            "opponent_score_delta": row["opponent_score_delta"],
            "status": row["status"],
        }
        for row in examples
    ]
    gate = gate_report(summary, integrity["passed"])
    return {
        "schema": 1,
        "experiment": "persistent_resident_local_job_bundle_oracle",
        "summary": summary,
        "integrity": integrity,
        "frozen_gate": gate,
        "passed": gate["passed"],
        "decision": (
            "authorize larger consumed-data teacher and production/training grammar"
            if gate["passed"]
            else "close resident-local one-job target redirection"
        ),
    }


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, dir=path.parent, text=True)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--repeat", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repeat_exact = args.input.read_bytes() == args.repeat.read_bytes()
    payload = analyze(read_rows(args.input), repeat_exact)
    atomic_write(args.output, json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    print(f"saved {args.output}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
