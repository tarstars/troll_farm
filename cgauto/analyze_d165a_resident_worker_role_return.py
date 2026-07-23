#!/usr/bin/env python3
"""Validate and analyze D165's exact-resident bounded worker-role return."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import tempfile
import os
from typing import Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
ARTIFACT_BASE = (
    ROOT / "artifacts" / "experiments" / "d165a-resident-worker-role-return"
)
PROTOCOL = BASE / "d165a-resident-worker-role-return-protocol-2026-07-23.md"
LOCK = BASE / "d165a-resident-worker-role-return-lock.json"
D161 = BASE / "d161a-resident-d40-panel-jobs20-9844136-9844199.tsv"
RUN_A = (
    ARTIFACT_BASE
    / "d165a-resident-worker-role-return-jobs1-9844136-9844199.tsv"
)
RUN_B = (
    ARTIFACT_BASE
    / "d165a-resident-worker-role-return-jobs20-9844136-9844199.tsv"
)
RUNNER = ROOT / "rust" / "src" / "bin" / "d165_resident_worker_role_return.rs"
BUILD_SCRIPT = ROOT / "rust" / "build.rs"
OUTPUT = BASE / "d165a-resident-worker-role-return-result.json"

START_SEED = 9_844_136
MAP_COUNT = 64
HORIZON = 16
POLICIES = ("resident", "producer_suppressor_return_h016")
OPPONENTS = (
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
    "script_boss",
    "silver_boss",
)

EXPECTED_FIELDS = (
    "map_seed",
    "seat",
    "opponent_index",
    "opponent",
    "policy_index",
    "policy",
    "return_horizon",
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
    "own_workers",
    "opponent_workers",
    "max_own_workers",
    "max_opponent_workers",
    "successful_trains",
    "successful_opponent_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "own_created_crops",
    "opponent_created_crops",
    "joint_created_crops",
    "ambiguous_created_crops",
    "own_owned_crop_harvest_units",
    "own_reinvested_crops",
    "action_hash",
    "state_hash",
    "resident_calls",
    "turns_played",
    "resident_call_mismatches",
    "production_events",
    "successful_production_plants",
    "successful_production_harvests",
    "opponent_crop_chops",
    "historical_producer_opponent_crop_chops",
    "remembered_live_target_opponent_crop_chops",
    "post_step_live_target_opponent_crop_chops",
    "suppression_entries",
    "eligible_entries",
    "activated",
    "activation_turn",
    "deadline",
    "first_override_turn",
    "selected_unit_id",
    "target_x",
    "target_y",
    "active_turns",
    "completed",
    "return_turn",
    "return_latency",
    "return_harvest_units",
    "aborted",
    "abort_turn",
    "abort_target_loss",
    "abort_unit_loss",
    "abort_capacity",
    "abort_incapable",
    "abort_horizon",
    "abort_terminal",
    "option_overrides",
    "protected_commands",
    "move_commands",
    "hold_commands",
    "harvest_commands",
    "generated_command_failures",
    "ownership_failures",
    "target_change_violations",
    "same_worker_target_violations",
    "controller_train_commands",
    "controller_plant_commands",
    "controller_chop_commands",
    "controller_other_commands",
    "post_exit_overrides",
    "horizon_violations",
    "restart_violations",
    "prefix_action_hash",
    "prefix_state_hash",
    "prefix_available",
    "prefix_action_match",
    "prefix_state_match",
    "resident_prefix_action_hash",
    "resident_prefix_state_hash",
    "inactive_terminal_match",
    "workforce_pair_match",
)
FLOAT_FIELDS = (
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
)
STRING_FIELDS = ("opponent", "policy")
INT_FIELDS = tuple(
    field
    for field in EXPECTED_FIELDS
    if field not in FLOAT_FIELDS and field not in STRING_FIELDS
)
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "ambiguous_created_crops",
    "resident_call_mismatches",
    "generated_command_failures",
    "ownership_failures",
    "target_change_violations",
    "same_worker_target_violations",
    "controller_train_commands",
    "controller_plant_commands",
    "controller_chop_commands",
    "controller_other_commands",
    "post_exit_overrides",
    "horizon_violations",
    "restart_violations",
)
D161_PARITY_FIELDS = (
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
    "own_workers",
    "opponent_workers",
    "max_own_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "own_created_crops",
    "opponent_created_crops",
    "joint_created_crops",
    "ambiguous_created_crops",
    "own_owned_crop_harvest_units",
    "own_reinvested_crops",
    "action_hash",
    "state_hash",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w") as target:
            json.dump(value, target, indent=2, sort_keys=True)
            target.write("\n")
            target.flush()
            os.fsync(target.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_rows(path: Path) -> tuple[list[dict], tuple[str, ...]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = tuple(reader.fieldnames or ())
    for row in rows:
        for field in INT_FIELDS:
            row[field] = int(row[field])
        for field in FLOAT_FIELDS:
            row[field] = float(row[field])
    return rows, fields


def read_d161_resident(path: Path = D161) -> dict[tuple[int, int, str], dict]:
    with path.open(newline="") as source:
        rows = [
            row
            for row in csv.DictReader(source, delimiter="\t")
            if row["policy"] == "resident"
        ]
    return {
        (int(row["map_seed"]), int(row["seat"]), row["opponent"]): row
        for row in rows
    }


def task(row: Mapping[str, object]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), str(row["opponent"])


def row_key(row: Mapping[str, object]) -> tuple[int, int, str, str]:
    return (*task(row), str(row["policy"]))


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(START_SEED, START_SEED + MAP_COUNT)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def mean(values: Iterable[float]) -> float:
    selected = list(values)
    return statistics.fmean(selected) if selected else 0.0


def ratio(numerator: int | float, denominator: int | float) -> float:
    return numerator / denominator if denominator else 0.0


def percentile(values: Iterable[float], fraction: float) -> float | None:
    selected = sorted(values)
    if not selected:
        return None
    if len(selected) == 1:
        return float(selected[0])
    position = fraction * (len(selected) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    weight = position - lower
    return float(selected[lower] * (1.0 - weight) + selected[upper] * weight)


def normal_interval_by_map(
    rows: Iterable[Mapping[str, object]], field: str
) -> list[float] | None:
    clusters: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        clusters[int(row["map_seed"])].append(float(row[field]))
    if not clusters:
        return None
    cluster_means = [statistics.fmean(values) for values in clusters.values()]
    center = statistics.fmean(cluster_means)
    if len(cluster_means) == 1:
        return [center, center]
    standard_error = statistics.stdev(cluster_means) / math.sqrt(len(cluster_means))
    return [center - 1.96 * standard_error, center + 1.96 * standard_error]


def verify_lock() -> dict:
    lock = json.loads(LOCK.read_text())
    if lock.get("schema") != "troll-farm-d165a-resident-worker-role-return-lock-v1":
        raise ValueError("unknown D165 lock schema")
    for relative, expected in lock["files"].items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"D165 frozen input differs: {relative}")
    return lock


def effect_rows(rows: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    indexed = {row_key(row): row for row in rows}
    effects = []
    for frozen_task in sorted(expected_tasks()):
        resident = indexed[(*frozen_task, POLICIES[0])]
        treatment = indexed[(*frozen_task, POLICIES[1])]
        effects.append(
            {
                "map_seed": frozen_task[0],
                "seat": frozen_task[1],
                "opponent": frozen_task[2],
                "activated": treatment["activated"],
                "completed": treatment["completed"],
                "margin_delta": treatment["margin"] - resident["margin"],
                "own_score_delta": treatment["own_score"] - resident["own_score"],
                "opponent_score_delta": (
                    treatment["opponent_score"] - resident["opponent_score"]
                ),
                "own_created_crop_delta": (
                    treatment["own_created_crops"] - resident["own_created_crops"]
                ),
                "resident_margin": resident["margin"],
                "treatment_margin": treatment["margin"],
            }
        )
    active = [row for row in effects if row["activated"]]
    completed = [row for row in effects if row["completed"]]
    return effects, active, completed


def effect_summary(rows: list[dict]) -> dict:
    margin_deltas = [row["margin_delta"] for row in rows]
    own_deltas = [row["own_score_delta"] for row in rows]
    opponent_deltas = [row["opponent_score_delta"] for row in rows]
    family = {
        opponent: mean(
            row["margin_delta"] for row in rows if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
        if any(row["opponent"] == opponent for row in rows)
    }
    seats = {
        str(seat): mean(row["margin_delta"] for row in rows if row["seat"] == seat)
        for seat in (0, 1)
        if any(row["seat"] == seat for row in rows)
    }
    return {
        "tasks": len(rows),
        "mean_margin_delta": mean(margin_deltas),
        "mean_own_score_delta": mean(own_deltas),
        "mean_opponent_score_delta": mean(opponent_deltas),
        "map_clustered_normal_95pct_interval": normal_interval_by_map(
            rows, "margin_delta"
        ),
        "strict_improvements": sum(value > 0 for value in margin_deltas),
        "strict_regressions": sum(value < 0 for value in margin_deltas),
        "ties": sum(value == 0 for value in margin_deltas),
        "p10_margin_delta": percentile(margin_deltas, 0.10),
        "median_margin_delta": percentile(margin_deltas, 0.50),
        "worst_margin_delta": min(margin_deltas) if margin_deltas else None,
        "best_margin_delta": max(margin_deltas) if margin_deltas else None,
        "family_mean_margin_delta": family,
        "seat_mean_margin_delta": seats,
    }


def tail_summary(rows: list[dict], margin_field: str) -> dict:
    margins = [int(row[margin_field]) for row in rows]
    return {
        "catastrophe_count": sum(value <= -100 for value in margins),
        "negative_margin_mass": sum(max(-value, 0) for value in margins),
    }


def count_events(rows: list[dict], field: str) -> dict:
    by_family = {
        opponent: sum(
            int(row[field]) for row in rows if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    task_by_family = {
        opponent: sum(
            int(row[field]) > 0 for row in rows if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    by_seat = {
        str(seat): sum(int(row[field]) for row in rows if row["seat"] == seat)
        for seat in (0, 1)
    }
    task_by_seat = {
        str(seat): sum(
            int(row[field]) > 0 for row in rows if row["seat"] == seat
        )
        for seat in (0, 1)
    }
    return {
        "events": sum(int(row[field]) for row in rows),
        "tasks": sum(int(row[field]) > 0 for row in rows),
        "task_rate": ratio(
            sum(int(row[field]) > 0 for row in rows),
            len(rows),
        ),
        "events_by_family": by_family,
        "tasks_by_family": task_by_family,
        "events_by_seat": by_seat,
        "tasks_by_seat": task_by_seat,
    }


def analyze(
    rows_a: list[dict],
    fields_a: tuple[str, ...],
    rows_b: list[dict],
    fields_b: tuple[str, ...],
    lock: dict,
    *,
    jobs1_wall_seconds: float | None = None,
    jobs20_wall_seconds: float | None = None,
) -> dict:
    expected = expected_tasks()
    expected_keys = {
        (*frozen_task, policy) for frozen_task in expected for policy in POLICIES
    }
    d161 = read_d161_resident()
    rows = rows_b
    indexed = {row_key(row): row for row in rows}
    resident_rows = [row for row in rows if row["policy"] == POLICIES[0]]
    treatment_rows = [row for row in rows if row["policy"] == POLICIES[1]]
    active_rows = [row for row in treatment_rows if row["activated"]]

    d161_mismatches = []
    for row in resident_rows:
        reference = d161.get(task(row))
        if reference is None:
            d161_mismatches.append({"task": task(row), "field": "missing"})
            continue
        for field in D161_PARITY_FIELDS:
            actual = str(row[field])
            if field in FLOAT_FIELDS:
                actual = f"{float(row[field]):.9f}"
            if actual != reference[field]:
                d161_mismatches.append(
                    {
                        "task": task(row),
                        "field": field,
                        "expected": reference[field],
                        "actual": actual,
                    }
                )
                break

    integrity = {
        "schema_exact": fields_a == EXPECTED_FIELDS and fields_b == EXPECTED_FIELDS,
        "row_count_exact": len(rows_a) == 2048 and len(rows_b) == 2048,
        "unique_rows_exact": (
            len({row_key(row) for row in rows_a}) == len(rows_a)
            and len({row_key(row) for row in rows_b}) == len(rows_b)
        ),
        "catalog_and_task_matrix_exact": (
            {row_key(row) for row in rows_a} == expected_keys
            and {row_key(row) for row in rows_b} == expected_keys
        ),
        "one_and_twenty_worker_bytes_identical": RUN_A.read_bytes()
        == RUN_B.read_bytes(),
        "resident_reproduces_d161": not d161_mismatches,
        "all_games_done": all(row["done"] == 1 for row in rows),
        "reward_identity_exact": all(
            row["reward_identity_error"] <= 1e-6 for row in rows
        ),
        "zero_failure_telemetry": all(
            row[field] == 0 for row in rows for field in FAILURE_FIELDS
        ),
        "inactive_treatments_exact": all(
            row["activated"] == 1 or row["inactive_terminal_match"] == 1
            for row in treatment_rows
        ),
        "active_prefixes_exact": all(
            row["prefix_available"] == 1
            and row["prefix_action_match"] == 1
            and row["prefix_state_match"] == 1
            for row in active_rows
        ),
        "resident_called_every_turn": all(
            row["resident_calls"] == row["turns_played"] for row in rows
        ),
        "controller_grammar_pure": all(
            row["controller_train_commands"] == 0
            and row["controller_plant_commands"] == 0
            and row["controller_chop_commands"] == 0
            and row["controller_other_commands"] == 0
            for row in rows
        ),
        "episode_bound_exact": all(
            row["active_turns"] <= HORIZON for row in treatment_rows
        ),
        "workforce_pairs_exact": all(
            row["workforce_pair_match"] == 1 for row in treatment_rows
        ),
        "crop_ownership_exact": all(
            row["provenance_failures"] == 0
            and row["ambiguous_created_crops"] == 0
            for row in rows
        ),
    }
    integrity_pass = all(integrity.values())

    activated = len(active_rows)
    completed_count = sum(row["completed"] for row in active_rows)
    activation_seats = sorted({row["seat"] for row in active_rows})
    activation_families = sorted({row["opponent"] for row in active_rows})
    generated = sum(row["option_overrides"] for row in active_rows)
    generated_failures = sum(
        row["generated_command_failures"] for row in active_rows
    )
    mechanism_gates = {
        "at_least_32_activations": activated >= 32,
        "both_seats": activation_seats == [0, 1],
        "at_least_six_families": len(activation_families) >= 6,
        "completion_rate_at_least_60pct": (
            ratio(completed_count, activated) >= 0.60 if activated else False
        ),
        "same_worker_and_target_exact": all(
            row["same_worker_target_violations"] == 0 for row in active_rows
        ),
        "at_least_90pct_legal_generated_commands": (
            ratio(generated - generated_failures, generated) >= 0.90
            if generated
            else False
        ),
        "zero_generated_command_failures": generated_failures == 0,
    }
    mechanism_pass = integrity_pass and all(mechanism_gates.values())

    effects, active_effects, completed_effects = effect_rows(rows)
    full_effect = effect_summary(effects)
    active_effect = effect_summary(active_effects)
    completed_effect = effect_summary(completed_effects)
    resident_tail = tail_summary(effects, "resident_margin")
    treatment_tail = tail_summary(effects, "treatment_margin")
    resident_crop_rate = ratio(
        sum(indexed[(*frozen_task, POLICIES[0])]["own_created_crops"] > 0 for frozen_task in expected),
        len(expected),
    )
    treatment_crop_rate = ratio(
        sum(indexed[(*frozen_task, POLICIES[1])]["own_created_crops"] > 0 for frozen_task in expected),
        len(expected),
    )

    diagnosis = {
        "production": {
            "events": sum(row["production_events"] for row in treatment_rows),
            "tasks": sum(row["production_events"] > 0 for row in treatment_rows),
            "task_rate": ratio(
                sum(row["production_events"] > 0 for row in treatment_rows),
                len(treatment_rows),
            ),
            "successful_plants": sum(
                row["successful_production_plants"] for row in treatment_rows
            ),
            "successful_harvests": sum(
                row["successful_production_harvests"] for row in treatment_rows
            ),
        },
        "opponent_crop_chop": count_events(treatment_rows, "opponent_crop_chops"),
        "opponent_crop_chop_by_historical_producer": count_events(
            treatment_rows, "historical_producer_opponent_crop_chops"
        ),
        "opponent_crop_chop_with_remembered_live_target": count_events(
            treatment_rows, "remembered_live_target_opponent_crop_chops"
        ),
        "opponent_crop_chop_with_post_step_live_target": count_events(
            treatment_rows, "post_step_live_target_opponent_crop_chops"
        ),
        "interpretation": (
            "The local panel exercises production and suppression broadly, and 237 tasks contain "
            "opponent-crop suppression by a worker that produced earlier. None retains the exact "
            "remembered own crop at suppression entry, so D165's stale-cell return precondition "
            "has zero support."
        ),
    }

    if not integrity_pass:
        verdict = "invalid_integrity_repair_before_interpretation"
        next_experiment = "repair D165 integrity without reading value"
    elif not mechanism_pass:
        verdict = "close_exact_live_target_return_grammar_at_support_gate"
        next_experiment = (
            "freeze a distinct producer-job successor audit: use the observable historical "
            "producer-to-suppressor transition, but define return as one current production "
            "affordance rather than a vanished cell; do not tune D165 or open new maps"
        )
    else:
        verdict = "evaluate_frozen_value_gate"
        next_experiment = "interpret the preregistered resident-relative value and safety gates"

    return {
        "schema": "troll-farm-d165a-resident-worker-role-return-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock,
        "input_hashes": {
            "protocol": sha256(PROTOCOL),
            "lock": sha256(LOCK),
            "runner": sha256(RUNNER),
            "build_script": sha256(BUILD_SCRIPT),
            "d161_resident_panel": sha256(D161),
            "jobs1": sha256(RUN_A),
            "jobs20": sha256(RUN_B),
        },
        "runs": {
            "jobs1": {
                "path": str(RUN_A.relative_to(ROOT)),
                "rows": len(rows_a),
                "wall_seconds": jobs1_wall_seconds,
            },
            "jobs20": {
                "path": str(RUN_B.relative_to(ROOT)),
                "rows": len(rows_b),
                "wall_seconds": jobs20_wall_seconds,
            },
            "speedup": (
                jobs1_wall_seconds / jobs20_wall_seconds
                if jobs1_wall_seconds and jobs20_wall_seconds
                else None
            ),
        },
        "integrity": integrity,
        "integrity_pass": integrity_pass,
        "d161_parity_mismatches": d161_mismatches[:20],
        "mechanism": {
            "activated_tasks": activated,
            "activation_rate": ratio(activated, len(treatment_rows)),
            "activation_seats": activation_seats,
            "activation_families": activation_families,
            "completed_tasks": completed_count,
            "completion_rate": ratio(completed_count, activated),
            "generated_commands": generated,
            "gates": mechanism_gates,
            "pass": mechanism_pass,
        },
        "support_diagnosis": diagnosis,
        "causal_value": {
            "interpretable": mechanism_pass,
            "not_interpreted_reason": (
                None
                if mechanism_pass
                else "the frozen mechanism-support gate fails before any intervention"
            ),
            "intention_to_treat_descriptive": full_effect,
            "active_subgroup_descriptive": active_effect,
            "completed_subgroup_descriptive": completed_effect,
            "resident_tail": resident_tail,
            "treatment_tail": treatment_tail,
            "resident_own_crop_creation_rate": resident_crop_rate,
            "treatment_own_crop_creation_rate": treatment_crop_rate,
        },
        "decision": {
            "verdict": verdict,
            "next_experiment": next_experiment,
            "construct_candidate": False,
            "arena_or_submission": False,
            "yt": False,
            "reserved_maps_opened": False,
        },
    }


def run(
    output: Path = OUTPUT,
    *,
    jobs1_wall_seconds: float | None = None,
    jobs20_wall_seconds: float | None = None,
) -> dict:
    lock = verify_lock()
    rows_a, fields_a = read_rows(RUN_A)
    rows_b, fields_b = read_rows(RUN_B)
    result = analyze(
        rows_a,
        fields_a,
        rows_b,
        fields_b,
        lock,
        jobs1_wall_seconds=jobs1_wall_seconds,
        jobs20_wall_seconds=jobs20_wall_seconds,
    )
    atomic_write(output, result)
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--jobs1-wall-seconds", type=float)
    parser.add_argument("--jobs20-wall-seconds", type=float)
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    result = run(
        args.output,
        jobs1_wall_seconds=args.jobs1_wall_seconds,
        jobs20_wall_seconds=args.jobs20_wall_seconds,
    )
    print(
        json.dumps(
            {
                "integrity_pass": result["integrity_pass"],
                "mechanism": result["mechanism"],
                "support_diagnosis": result["support_diagnosis"],
                "decision": result["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
