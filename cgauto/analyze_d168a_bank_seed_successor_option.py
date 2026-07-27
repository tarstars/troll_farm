#!/usr/bin/env python3
"""Validate and analyze D168a's bounded BANK_SEED successor option
(ARM_A post-return, ARM_B pre-carry) over the exact resident."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import tempfile
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
ARTIFACT_BASE = ROOT / "artifacts" / "experiments" / "d168a-bank-seed-successor-option"
PROTOCOL = BASE / "d168a-bank-seed-successor-option-protocol-2026-07-27.md"
LOCK = BASE / "d168a-bank-seed-successor-option-lock.json"
D161 = BASE / "d161a-resident-d40-panel-jobs20-9844136-9844199.tsv"
D167A_LOCAL = (
    ROOT
    / "artifacts"
    / "experiments"
    / "d167a-successor-acquisition-path"
    / "d167a-local-summary-jobs20-9844136-9844199.tsv"
)
RUN_A = ARTIFACT_BASE / "d168a-jobs1-9844136-9844199.tsv"
RUN_B = ARTIFACT_BASE / "d168a-jobs20-9844136-9844199.tsv"
RUNNER = ROOT / "rust" / "src" / "bin" / "d168a_bank_seed_successor_option.rs"
BUILD_SCRIPT = ROOT / "rust" / "build.rs"
OUTPUT = BASE / "d168a-bank-seed-successor-option-result.json"

START_SEED = 9_844_136
MAP_COUNT = 64
RESERVED_START_SEED = 9_844_200
POLICIES = ("control", "arm_a_post_return", "arm_b_pre_carry")
ARMS = ("arm_a_post_return", "arm_b_pre_carry")
HORIZONS = {"arm_a_post_return": 24, "arm_b_pre_carry": 32}
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
    "map_seed", "seat", "opponent_index", "opponent", "policy_index", "policy",
    "done", "turn", "own_score", "opponent_score", "margin", "own_return",
    "opponent_return", "margin_return", "reward_identity_error", "own_workers",
    "opponent_workers", "max_own_workers", "successful_trains", "completed_jobs",
    "invalidated_jobs", "invalid_direct_commands", "provenance_failures",
    "deposit_prediction_failures", "own_created_crops", "opponent_created_crops",
    "joint_created_crops", "ambiguous_created_crops", "own_owned_crop_harvest_units",
    "own_reinvested_crops", "action_hash", "state_hash", "entry_captured",
    "entry_turn", "entry_unit_id", "generic_return_captured", "generic_return_turn",
    "generic_return_verb", "purity_violations", "gate_bank_ok", "gate_carry_ok",
    "activated", "activation_turn", "deadline", "committed", "committed_turn",
    "aborted", "abort_reason", "species_picked", "species_planted", "plant_cell_x",
    "plant_cell_y", "chop_cell_x", "chop_cell_y", "move_commands", "pick_commands",
    "chop_commands", "plant_commands", "hold_commands", "pick_attempts",
    "pick_successes", "plant_attempts", "plant_successes", "chop_attempts",
    "chop_successes", "vocabulary_violations", "active_turns",
)
STRING_FIELDS = ("opponent", "policy", "abort_reason", "species_picked", "species_planted")
FLOAT_FIELDS = ("own_return", "opponent_return", "margin_return", "reward_identity_error")
INT_FIELDS = tuple(
    field for field in EXPECTED_FIELDS if field not in FLOAT_FIELDS and field not in STRING_FIELDS
)
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "ambiguous_created_crops",
    "purity_violations",
    "vocabulary_violations",
)
D161_PARITY_FIELDS = (
    "done", "turn", "own_score", "opponent_score", "margin", "own_return",
    "opponent_return", "margin_return", "reward_identity_error", "own_workers",
    "opponent_workers", "max_own_workers", "successful_trains",
    "own_created_crops", "opponent_created_crops", "joint_created_crops",
    "ambiguous_created_crops", "own_owned_crop_harvest_units",
    "own_reinvested_crops", "action_hash", "state_hash",
)
GAME_RELEVANT_FIELDS = (
    "done", "turn", "own_score", "opponent_score", "own_return", "opponent_return",
    "margin_return", "own_workers", "opponent_workers", "max_own_workers",
    "successful_trains", "own_created_crops", "opponent_created_crops",
    "joint_created_crops", "ambiguous_created_crops", "own_owned_crop_harvest_units",
    "action_hash", "state_hash", "entry_captured", "entry_turn", "entry_unit_id",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
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


def mean(values: Iterable[float]) -> float:
    selected = list(values)
    return statistics.fmean(selected) if selected else 0.0


def ratio(numerator: int | float, denominator: int | float) -> float:
    return numerator / denominator if denominator else 0.0


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


def normal_interval_by_map(rows: Iterable[Mapping[str, object]], field: str) -> list[float] | None:
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
    if lock.get("schema") != "troll-farm-d168a-bank-seed-successor-option-lock-v1":
        raise ValueError("unknown D168a lock schema")
    mismatches = {}
    for relative, expected in lock["files"].items():
        path = ROOT / relative
        actual = sha256(path) if path.is_file() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    return {"lock": lock, "mismatches": mismatches, "pass": not mismatches}


def read_d161_resident() -> dict[tuple[int, int, str], dict]:
    with D161.open(newline="") as source:
        rows = [row for row in csv.DictReader(source, delimiter="\t") if row["policy"] == "resident"]
    return {(int(row["map_seed"]), int(row["seat"]), row["opponent"]): row for row in rows}


def read_d167a_local() -> dict[tuple[int, int, str], dict]:
    with D167A_LOCAL.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    return {(int(row["map_seed"]), int(row["seat"]), row["opponent"]): row for row in rows}


def d161_parity(control_rows: list[dict]) -> dict:
    reference = read_d161_resident()
    mismatches = []
    for row in control_rows:
        ref = reference.get(task(row))
        if ref is None:
            mismatches.append({"task": task(row), "field": "missing"})
            continue
        for field in D161_PARITY_FIELDS:
            actual = row[field]
            expected = ref[field]
            if field in FLOAT_FIELDS:
                if not math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=1e-7):
                    mismatches.append({"task": task(row), "field": field, "expected": expected, "actual": actual})
                    break
            elif str(actual) != str(expected):
                mismatches.append({"task": task(row), "field": field, "expected": expected, "actual": actual})
                break
    return {"tasks": len(control_rows), "mismatches": mismatches[:20], "mismatch_count": len(mismatches), "pass": not mismatches}


def d166_d167_cross_check(control_rows: list[dict]) -> dict:
    reference = read_d167a_local()
    mismatches = []
    entries = 0
    natural_plant_returns = 0
    for row in control_rows:
        ref = reference.get(task(row))
        if ref is None:
            mismatches.append({"task": task(row), "field": "missing"})
            continue
        if int(row["entry_captured"]) != int(ref["entry_captured"]):
            mismatches.append({"task": task(row), "field": "entry_captured", "expected": ref["entry_captured"], "actual": row["entry_captured"]})
            continue
        if row["entry_captured"]:
            entries += 1
            if int(row["entry_turn"]) != int(ref["entry_turn"]) or int(row["entry_unit_id"]) != int(ref["selected_unit_id"]):
                mismatches.append({
                    "task": task(row), "field": "entry_detail",
                    "expected": (ref["entry_turn"], ref["selected_unit_id"]),
                    "actual": (row["entry_turn"], row["entry_unit_id"]),
                })
            if int(row["generic_return_captured"]) != int(ref["natural_return"]):
                mismatches.append({"task": task(row), "field": "generic_return_captured", "expected": ref["natural_return"], "actual": row["generic_return_captured"]})
            elif row["generic_return_captured"]:
                if int(row["generic_return_turn"]) != int(ref["natural_return_turn"]):
                    mismatches.append({"task": task(row), "field": "generic_return_turn", "expected": ref["natural_return_turn"], "actual": row["generic_return_turn"]})
                if row["generic_return_verb"] == 1 and ref["natural_return_verb"] == "PLANT":
                    natural_plant_returns += 1
                elif (row["generic_return_verb"] == 1) != (ref["natural_return_verb"] == "PLANT"):
                    mismatches.append({"task": task(row), "field": "generic_return_verb", "expected": ref["natural_return_verb"], "actual": row["generic_return_verb"]})
    return {
        "entries": entries,
        "natural_plant_returns": natural_plant_returns,
        "expected_entries": 237,
        "expected_natural_plant_returns": 135,
        "mismatches": mismatches[:20],
        "mismatch_count": len(mismatches),
        "pass": not mismatches and entries == 237 and natural_plant_returns == 135,
    }


def entry_event_cross_policy(indexed: dict[tuple, dict]) -> dict:
    mismatches = []
    for key in sorted(expected_tasks()):
        control = indexed[(*key, "control")]
        for arm in ARMS:
            arm_row = indexed[(*key, arm)]
            if int(control["entry_captured"]) != int(arm_row["entry_captured"]):
                mismatches.append({"task": key, "policy": arm, "field": "entry_captured"})
                continue
            if control["entry_captured"] and (
                control["entry_turn"] != arm_row["entry_turn"]
                or control["entry_unit_id"] != arm_row["entry_unit_id"]
            ):
                mismatches.append({"task": key, "policy": arm, "field": "entry_detail"})
    return {"mismatches": mismatches[:20], "mismatch_count": len(mismatches), "pass": not mismatches}


def inactive_task_parity(indexed: dict[tuple, dict]) -> dict:
    mismatches = []
    checked = 0
    for key in sorted(expected_tasks()):
        control = indexed[(*key, "control")]
        for arm in ARMS:
            arm_row = indexed[(*key, arm)]
            if arm_row["activated"]:
                continue
            checked += 1
            for field in GAME_RELEVANT_FIELDS:
                if control[field] != arm_row[field]:
                    mismatches.append({"task": key, "policy": arm, "field": field, "control": control[field], "arm": arm_row[field]})
                    break
    return {"tasks_checked": checked, "mismatches": mismatches[:20], "mismatch_count": len(mismatches), "pass": not mismatches}


def outcome_margin(row: Mapping[str, object]) -> int:
    return int(row["own_score"]) - int(row["opponent_score"])


def tail_summary(rows: list[dict]) -> dict:
    margins = [outcome_margin(row) for row in rows]
    return {
        "catastrophe_count": sum(value <= -100 for value in margins),
        "negative_margin_mass": sum(max(-value, 0) for value in margins),
    }


def mechanism_gate(indexed: dict[tuple, dict], arm: str) -> dict:
    active = [indexed[(*key, arm)] for key in sorted(expected_tasks()) if indexed[(*key, arm)]["activated"]]
    seats = sorted({int(row["seat"]) for row in active})
    families = sorted({row["opponent"] for row in active})
    gates = {
        "at_least_32_activations": len(active) >= 32,
        "both_seats": seats == [0, 1],
        "at_least_six_families": len(families) >= 6,
    }
    return {
        "activated_tasks": len(active),
        "activation_rate": ratio(len(active), len(expected_tasks())),
        "activation_seats": seats,
        "activation_families": families,
        "family_count": len(families),
        "gates": gates,
        "pass": all(gates.values()),
    }


def value_gate(indexed: dict[tuple, dict], arm: str) -> dict:
    all_tasks = sorted(expected_tasks())
    active_deltas = []
    itt_deltas = []
    by_family_active: dict[str, list[float]] = defaultdict(list)
    for key in all_tasks:
        control = indexed[(*key, "control")]
        arm_row = indexed[(*key, arm)]
        margin_delta = outcome_margin(arm_row) - outcome_margin(control)
        own_delta = int(arm_row["own_score"]) - int(control["own_score"])
        itt_deltas.append({"margin": margin_delta, "own": own_delta, "map_seed": key[0]})
        if arm_row["activated"]:
            row = {"margin": margin_delta, "own": own_delta, "map_seed": key[0], "opponent": key[2]}
            active_deltas.append(row)
            by_family_active[key[2]].append(margin_delta)

    control_rows = [indexed[(*key, "control")] for key in all_tasks]
    arm_rows = [indexed[(*key, arm)] for key in all_tasks]
    control_tail = tail_summary(control_rows)
    arm_tail = tail_summary(arm_rows)

    family_means = {family: mean(values) for family, values in sorted(by_family_active.items())}
    worst_family = min(family_means.values()) if family_means else None

    mean_margin_active = mean(row["margin"] for row in active_deltas)
    mean_own_active = mean(row["own"] for row in active_deltas)
    ci = normal_interval_by_map(active_deltas, "margin") if active_deltas else None

    gates = {
        "mean_paired_margin_at_least_2": mean_margin_active >= 2.0 if active_deltas else False,
        "mean_own_score_delta_at_least_neg_0_5": mean_own_active >= -0.5 if active_deltas else False,
        "worst_family_margin_at_least_0": (worst_family is not None and worst_family >= 0.0),
        "catastrophes_not_above_control": arm_tail["catastrophe_count"] <= control_tail["catastrophe_count"],
        "negative_margin_mass_within_1_10x_control": (
            arm_tail["negative_margin_mass"] <= 1.10 * control_tail["negative_margin_mass"]
            if control_tail["negative_margin_mass"] > 0
            else arm_tail["negative_margin_mass"] == 0
        ),
    }
    return {
        "activated_tasks": len(active_deltas),
        "mean_paired_margin_active": mean_margin_active,
        "map_clustered_95pct_ci_active": ci,
        "mean_own_score_delta_active": mean_own_active,
        "mean_opponent_score_delta_active": mean(
            int(indexed[(*key, arm)]["opponent_score"]) - int(indexed[(*key, "control")]["opponent_score"])
            for key in all_tasks
            if indexed[(*key, arm)]["activated"]
        ) if active_deltas else 0.0,
        "family_mean_margin_active": family_means,
        "worst_family_margin_active": worst_family,
        "intention_to_treat_mean_margin": mean(row["margin"] for row in itt_deltas),
        "intention_to_treat_map_clustered_95pct_ci": normal_interval_by_map(itt_deltas, "margin"),
        "control_tail": control_tail,
        "arm_tail": arm_tail,
        "strict_improvements_active": sum(row["margin"] > 0 for row in active_deltas),
        "strict_regressions_active": sum(row["margin"] < 0 for row in active_deltas),
        "ties_active": sum(row["margin"] == 0 for row in active_deltas),
        "gates": gates,
        "pass": all(gates.values()),
    }


def analyze(rows_a: list[dict], fields_a: tuple, rows_b: list[dict], fields_b: tuple, lock_result: dict,
            *, jobs1_wall_seconds: float | None = None, jobs20_wall_seconds: float | None = None) -> dict:
    expected = expected_tasks()
    expected_keys = {(*key, policy) for key in expected for policy in POLICIES}
    rows = rows_b
    indexed = {row_key(row): row for row in rows}
    control_rows = [row for row in rows if row["policy"] == "control"]

    parity = d161_parity(control_rows)
    cross_check = d166_d167_cross_check(control_rows)
    entry_cross = entry_event_cross_policy(indexed)
    inactive_parity = inactive_task_parity(indexed)

    integrity = {
        "schema_exact": fields_a == EXPECTED_FIELDS and fields_b == EXPECTED_FIELDS,
        "row_count_exact": len(rows_a) == 3072 and len(rows_b) == 3072,
        "unique_rows_exact": (
            len({row_key(row) for row in rows_a}) == len(rows_a)
            and len({row_key(row) for row in rows_b}) == len(rows_b)
        ),
        "task_policy_matrix_exact": (
            {row_key(row) for row in rows_a} == expected_keys
            and {row_key(row) for row in rows_b} == expected_keys
        ),
        "jobs1_and_jobs20_byte_identical": RUN_A.read_bytes() == RUN_B.read_bytes(),
        "reserved_maps_excluded": START_SEED + MAP_COUNT <= RESERVED_START_SEED,
        "control_reproduces_d161": parity["pass"],
        "control_reproduces_d166_d167_entry_facts": cross_check["pass"],
        "entry_event_identical_across_policies": entry_cross["pass"],
        "inactive_tasks_byte_exact_vs_control": inactive_parity["pass"],
        "all_games_done": all(row["done"] == 1 for row in rows),
        "reward_identity_exact": all(row["reward_identity_error"] <= 1e-6 for row in rows),
        "zero_failure_telemetry": all(row[field] == 0 for row in rows for field in FAILURE_FIELDS),
        "zero_ambiguous_crops": all(row["ambiguous_created_crops"] == 0 for row in rows),
        "episode_bounds_exact": all(
            row["active_turns"] <= HORIZONS[row["policy"]] + 1
            for row in rows
            if row["policy"] in ARMS and row["activated"]
        ),
        "no_double_commit_and_abort": all(
            not (row["committed"] and row["aborted"]) for row in rows if row["policy"] in ARMS
        ),
        "control_never_activates": all(row["activated"] == 0 for row in control_rows),
    }
    integrity_pass = all(integrity.values())

    mechanism = {arm: mechanism_gate(indexed, arm) for arm in ARMS}
    value = {arm: (value_gate(indexed, arm) if (integrity_pass and mechanism[arm]["pass"]) else None) for arm in ARMS}

    arm_pass = {}
    for arm in ARMS:
        if not integrity_pass:
            arm_pass[arm] = None
        elif not mechanism[arm]["pass"]:
            arm_pass[arm] = False
        else:
            arm_pass[arm] = bool(value[arm]["pass"])

    if not integrity_pass:
        verdict = "repair_integrity_before_interpretation"
    elif any(arm_pass[arm] for arm in ARMS):
        qualified = [arm for arm in ARMS if arm_pass[arm]]
        verdict = f"qualified: {', '.join(qualified)} (record only; no candidate/Arena authorized)"
    else:
        verdict = "close_hand_written_successor_controllers; BANK_SEED survives only as a rollout-valued option"

    return {
        "schema": "troll-farm-d168a-bank-seed-successor-option-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "lock": lock_result,
        "input_hashes": {
            "protocol": sha256(PROTOCOL),
            "lock": sha256(LOCK),
            "runner": sha256(RUNNER),
            "build_script": sha256(BUILD_SCRIPT),
            "d161_resident_panel": sha256(D161),
            "d167a_local_summary": sha256(D167A_LOCAL),
            "jobs1": sha256(RUN_A),
            "jobs20": sha256(RUN_B),
        },
        "runs": {
            "jobs1": {"path": str(RUN_A.relative_to(ROOT)), "rows": len(rows_a), "wall_seconds": jobs1_wall_seconds},
            "jobs20": {"path": str(RUN_B.relative_to(ROOT)), "rows": len(rows_b), "wall_seconds": jobs20_wall_seconds},
            "speedup": (jobs1_wall_seconds / jobs20_wall_seconds if jobs1_wall_seconds and jobs20_wall_seconds else None),
        },
        "integrity": integrity,
        "integrity_pass": integrity_pass,
        "d161_parity": parity,
        "d166_d167_cross_check": cross_check,
        "entry_event_cross_policy": entry_cross,
        "inactive_task_parity": inactive_parity,
        "mechanism": mechanism,
        "value": value,
        "arm_pass": arm_pass,
        "verdict": verdict,
    }


def run(output: Path = OUTPUT, *, jobs1_wall_seconds: float | None = None, jobs20_wall_seconds: float | None = None) -> dict:
    lock_result = verify_lock()
    rows_a, fields_a = read_rows(RUN_A)
    rows_b, fields_b = read_rows(RUN_B)
    result = analyze(rows_a, fields_a, rows_b, fields_b, lock_result,
                      jobs1_wall_seconds=jobs1_wall_seconds, jobs20_wall_seconds=jobs20_wall_seconds)
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
    result = run(args.output, jobs1_wall_seconds=args.jobs1_wall_seconds, jobs20_wall_seconds=args.jobs20_wall_seconds)
    print(json.dumps({
        "integrity_pass": result["integrity_pass"],
        "mechanism": {arm: result["mechanism"][arm]["pass"] for arm in ARMS},
        "arm_pass": result["arm_pass"],
        "verdict": result["verdict"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
