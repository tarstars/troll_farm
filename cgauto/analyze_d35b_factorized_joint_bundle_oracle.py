#!/usr/bin/env python3
"""Analyze the D35b official-map factorized joint-bundle hindsight oracle."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics


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
CHECKPOINTS = (50, 100)
TRAIN_GOALS = ("none", "producer_2211", "chopper_2202")
TARGETED_ROLES = {"fell_bank", "harvest_bank", "renew", "mine_bank"}
INTEGER_FIELDS = (
    "seed",
    "seat",
    "checkpoint",
    "root_turn",
    "option",
    "predicted_eta",
    "predicted_reward",
    "rate_score",
    "overridden_actions",
    "invalid_direct_commands",
    "train_success",
    "max_own_workers",
    "bundle_end_turn",
    "root_plan_count",
    "has_renew",
    "has_fell",
    "has_mine",
    "has_train_goal",
    "own_score",
    "opponent_score",
    "margin",
    "own_wood",
    "opponent_wood",
    "own_workers",
    "opponent_workers",
    "terminal_turn",
    "farm_own_score",
    "farm_opponent_score",
    "farm_margin",
    "farm_own_wood",
    "farm_opponent_wood",
    "farm_terminal_turn",
    "margin_delta_farm",
    "own_score_delta_farm",
    "opponent_score_delta_farm",
    "resident_own_score",
    "resident_opponent_score",
    "resident_margin",
    "resident_own_wood",
    "resident_opponent_wood",
    "margin_delta_resident",
    "own_score_delta_resident",
    "opponent_score_delta_resident",
    "control_identity_match",
)
MANIFEST_INTEGER_FIELDS = (
    "seed",
    "seat",
    "root_count",
    "farm_own_score",
    "farm_opponent_score",
    "farm_margin",
    "farm_own_workers",
    "farm_opponent_workers",
    "farm_terminal_turn",
    "resident_own_score",
    "resident_opponent_score",
    "resident_margin",
    "resident_own_workers",
    "resident_opponent_workers",
    "resident_terminal_turn",
)


def robust_summary(values) -> dict:
    values = list(values)
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "standard_deviation": None,
            "standard_error": None,
            "ci95_normal": [None, None],
            "minimum": None,
            "maximum": None,
            "positive": 0,
            "zero": 0,
            "negative": 0,
        }
    mean = statistics.mean(values)
    deviation = statistics.stdev(values) if len(values) > 1 else 0.0
    error = deviation / math.sqrt(len(values))
    return {
        "n": len(values),
        "mean": mean,
        "median": statistics.median(values),
        "standard_deviation": deviation,
        "standard_error": error,
        "ci95_normal": [mean - 1.96 * error, mean + 1.96 * error],
        "minimum": min(values),
        "maximum": max(values),
        "positive": sum(value > 0 for value in values),
        "zero": sum(value == 0 for value in values),
        "negative": sum(value < 0 for value in values),
    }


def read_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        missing = set(INTEGER_FIELDS) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"missing integer fields: {sorted(missing)}")
        for row in reader:
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def read_scenario_manifest(path: Path) -> list[dict]:
    rows = []
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        missing = set(MANIFEST_INTEGER_FIELDS) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"missing manifest integer fields: {sorted(missing)}")
        for row in reader:
            for field in MANIFEST_INTEGER_FIELDS:
                row[field] = int(row[field])
            row["captured_checkpoints"] = [
                int(value)
                for value in row["captured_checkpoints"].split(",")
                if value
            ]
            row["root_turns"] = [
                int(value) for value in row["root_turns"].split(",") if value
            ]
            rows.append(row)
    return rows


def validate_scenario_manifest(
    rows: list[dict], seed_start: int, seed_count: int
) -> tuple[dict, set[tuple[int, int, str, int]], dict]:
    expected_tasks = {
        (seed, seat, opponent)
        for seed in range(seed_start, seed_start + seed_count)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["seed"], row["seat"], row["opponent"])].append(row)
    actual_tasks = set(grouped)
    duplicate_tasks = sum(len(entries) - 1 for entries in grouped.values())
    malformed_roots = 0
    inconsistent_scores = 0
    invalid_terminal_turns = 0
    eligible_roots = set()
    references = {}
    zero_root_tasks = []
    for task, entries in grouped.items():
        row = entries[0]
        checkpoints = row["captured_checkpoints"]
        root_turns = row["root_turns"]
        if (
            row["root_count"] != len(checkpoints)
            or len(checkpoints) != len(root_turns)
            or len(checkpoints) != len(set(checkpoints))
            or any(checkpoint not in CHECKPOINTS for checkpoint in checkpoints)
            or any(
                turn < checkpoint or turn > 300
                for checkpoint, turn in zip(checkpoints, root_turns)
            )
        ):
            malformed_roots += 1
        for checkpoint in checkpoints:
            eligible_roots.add((*task, checkpoint))
        if row["root_count"] == 0:
            zero_root_tasks.append(
                {
                    "seed": task[0],
                    "seat": task[1],
                    "opponent": task[2],
                    "farm_own_workers": row["farm_own_workers"],
                    "farm_terminal_turn": row["farm_terminal_turn"],
                }
            )
        inconsistent_scores += int(
            row["farm_margin"]
            != row["farm_own_score"] - row["farm_opponent_score"]
            or row["resident_margin"]
            != row["resident_own_score"] - row["resident_opponent_score"]
        )
        invalid_terminal_turns += int(
            not 2 <= row["farm_terminal_turn"] <= 301
            or not 2 <= row["resident_terminal_turn"] <= 301
        )
        references[task] = {
            "farm": (
                row["farm_own_score"],
                row["farm_opponent_score"],
                row["farm_margin"],
                row["farm_terminal_turn"],
            ),
            "resident": (
                row["resident_own_score"],
                row["resident_opponent_score"],
                row["resident_margin"],
            ),
        }
    complete = (
        actual_tasks == expected_tasks
        and duplicate_tasks == 0
        and malformed_roots == 0
        and inconsistent_scores == 0
        and invalid_terminal_turns == 0
    )
    report = {
        "provided": True,
        "expected_tasks": len(expected_tasks),
        "actual_tasks": len(actual_tasks),
        "missing_tasks": len(expected_tasks - actual_tasks),
        "unexpected_tasks": len(actual_tasks - expected_tasks),
        "duplicate_tasks": duplicate_tasks,
        "eligible_roots": len(eligible_roots),
        "nominal_roots": len(expected_tasks) * len(CHECKPOINTS),
        "ineligible_roots": len(expected_tasks) * len(CHECKPOINTS)
        - len(eligible_roots),
        "malformed_root_lists": malformed_roots,
        "inconsistent_scores": inconsistent_scores,
        "invalid_terminal_turns": invalid_terminal_turns,
        "zero_root_tasks": zero_root_tasks,
        "complete": complete,
    }
    return report, eligible_roots, references


def root_key(row: dict) -> tuple[int, int, str, int]:
    return row["seed"], row["seat"], row["opponent"], row["checkpoint"]


def parse_cell(value: str) -> tuple[int, int] | None:
    if value == "-":
        return None
    fields = value.split(",")
    if len(fields) != 2:
        raise ValueError(f"invalid cell {value!r}")
    return int(fields[0]), int(fields[1])


def parse_plan_key(key: str) -> tuple[list[dict], str]:
    try:
        unit_key, train_goal = key.rsplit("|train=", 1)
    except ValueError as error:
        raise ValueError(f"missing train suffix in {key!r}") from error
    jobs = []
    for encoded in unit_key.split("+"):
        fields = encoded.split(":")
        if len(fields) != 5:
            raise ValueError(f"invalid job key {encoded!r}")
        role, unit_id, target, plant_cell, fruit_kind = fields
        jobs.append(
            {
                "role": role,
                "unit_id": int(unit_id),
                "target": parse_cell(target),
                "plant_cell": parse_cell(plant_cell),
                "fruit_kind": None if fruit_kind == "-" else int(fruit_kind),
            }
        )
    return jobs, train_goal


def plan_key_error(row: dict) -> str | None:
    if row["option"] == 0:
        return None if row["plan_key"] == "control" else "control_key"
    try:
        jobs, train_goal = parse_plan_key(row["plan_key"])
    except (TypeError, ValueError):
        return "parse"
    if len(jobs) != 2 or len({job["unit_id"] for job in jobs}) != 2:
        return "factor_count"
    if train_goal != row["train_goal"] or train_goal not in TRAIN_GOALS:
        return "train_suffix"
    if "+".join(job["role"] for job in jobs) != row["role_tuple"]:
        return "role_tuple"
    acquisitions = [
        job["target"]
        for job in jobs
        if job["role"] in TARGETED_ROLES and job["target"] is not None
    ]
    if len(acquisitions) != len(set(acquisitions)):
        return "acquisition_collision"
    planting = [job["plant_cell"] for job in jobs if job["plant_cell"] is not None]
    if len(planting) != len(set(planting)):
        return "plant_collision"
    return None


def reference_signature(row: dict, prefix: str) -> tuple[int, ...]:
    if prefix == "farm":
        fields = (
            "farm_own_score",
            "farm_opponent_score",
            "farm_margin",
            "farm_own_wood",
            "farm_opponent_wood",
            "farm_terminal_turn",
        )
    elif prefix == "resident":
        fields = (
            "resident_own_score",
            "resident_opponent_score",
            "resident_margin",
            "resident_own_wood",
            "resident_opponent_wood",
        )
    else:
        raise ValueError(prefix)
    return tuple(row[field] for field in fields)


def delta_fields_consistent(row: dict) -> bool:
    return (
        row["margin"] == row["own_score"] - row["opponent_score"]
        and row["farm_margin"]
        == row["farm_own_score"] - row["farm_opponent_score"]
        and row["resident_margin"]
        == row["resident_own_score"] - row["resident_opponent_score"]
        and row["margin_delta_farm"] == row["margin"] - row["farm_margin"]
        and row["own_score_delta_farm"]
        == row["own_score"] - row["farm_own_score"]
        and row["opponent_score_delta_farm"]
        == row["opponent_score"] - row["farm_opponent_score"]
        and row["margin_delta_resident"]
        == row["margin"] - row["resident_margin"]
        and row["own_score_delta_resident"]
        == row["own_score"] - row["resident_own_score"]
        and row["opponent_score_delta_resident"]
        == row["opponent_score"] - row["resident_opponent_score"]
    )


def crossing_errors(rows: list[dict]) -> int:
    groups = defaultdict(list)
    for row in rows:
        if row["option"] == 0:
            continue
        try:
            unit_key, _ = row["plan_key"].rsplit("|train=", 1)
        except ValueError:
            continue
        groups[unit_key].append(row)
    errors = 0
    for unit_key, variants in groups.items():
        goals = {row["train_goal"] for row in variants}
        roles = variants[0]["role_tuple"]
        expected = (
            {"producer_2211", "chopper_2202"}
            if roles == "keep+keep"
            else set(TRAIN_GOALS)
        )
        if goals != expected or len(variants) != len(expected):
            errors += 1
        invariant = {
            (
                row["role_tuple"],
                row["predicted_eta"],
                row["predicted_reward"],
                row["rate_score"],
            )
            for row in variants
        }
        if len(invariant) != 1:
            errors += 1
        if not unit_key:
            errors += 1
    return errors


def validate_grid(
    rows: list[dict],
    seed_start: int,
    seed_count: int,
    repeat_identity_verified: bool,
    expected_roots_override: set[tuple[int, int, str, int]] | None = None,
    manifest_complete: bool = True,
    manifest_references: dict | None = None,
) -> tuple[dict, dict[tuple[int, int, str, int], list[dict]]]:
    nominal_roots = {
        (seed, seat, opponent, checkpoint)
        for seed in range(seed_start, seed_start + seed_count)
        for seat in (0, 1)
        for opponent in OPPONENTS
        for checkpoint in CHECKPOINTS
    }
    expected_roots = (
        nominal_roots
        if expected_roots_override is None
        else set(expected_roots_override)
    )
    grouped = defaultdict(list)
    for row in rows:
        grouped[root_key(row)].append(row)
    actual_roots = set(grouped)

    duplicate_options = 0
    duplicate_plan_keys = 0
    missing_controls = 0
    noncontiguous_options = 0
    plan_count_mismatches = 0
    plan_limit_violations = 0
    root_metadata_mismatches = 0
    reference_mismatches = 0
    control_outcome_mismatches = 0
    plan_key_errors = Counter()
    crossing_error_count = 0
    role_flag_mismatches = 0
    invalid_root_turns = 0
    invalid_terminal_turns = 0
    invalid_bundle_turns = 0
    invalid_predicted_completion = 0

    for key, branches in grouped.items():
        options = [row["option"] for row in branches]
        keys = [row["plan_key"] for row in branches]
        duplicate_options += len(options) - len(set(options))
        duplicate_plan_keys += len(keys) - len(set(keys))
        controls = [row for row in branches if row["option"] == 0]
        if len(controls) != 1:
            missing_controls += 1
            continue
        control = controls[0]
        expected_options = set(range(control["root_plan_count"] + 1))
        if set(options) != expected_options:
            noncontiguous_options += 1
        if len(branches) != control["root_plan_count"] + 1:
            plan_count_mismatches += 1
        if control["root_plan_count"] > 288:
            plan_limit_violations += 1

        metadata = {
            (
                row["root_turn"],
                row["root_plan_count"],
                row["has_renew"],
                row["has_fell"],
                row["has_mine"],
                row["has_train_goal"],
                row["control_identity_match"],
            )
            for row in branches
        }
        if len(metadata) != 1:
            root_metadata_mismatches += 1
        if len({reference_signature(row, "farm") for row in branches}) != 1:
            reference_mismatches += 1
        if len({reference_signature(row, "resident") for row in branches}) != 1:
            reference_mismatches += 1
        control_terminal = (
            control["own_score"],
            control["opponent_score"],
            control["margin"],
            control["own_wood"],
            control["opponent_wood"],
            control["terminal_turn"],
        )
        if control_terminal != reference_signature(control, "farm"):
            control_outcome_mismatches += 1

        for row in branches:
            error = plan_key_error(row)
            if error is not None:
                plan_key_errors[error] += 1
            if row["root_turn"] < row["checkpoint"] or row["root_turn"] > 300:
                invalid_root_turns += 1
            if not 2 <= row["terminal_turn"] <= 301:
                invalid_terminal_turns += 1
            if not row["root_turn"] <= row["bundle_end_turn"] <= 301:
                invalid_bundle_turns += 1
            if (
                row["option"] > 0
                and row["root_turn"] + row["predicted_eta"] > 300
            ):
                invalid_predicted_completion += 1
        crossing_error_count += crossing_errors(branches)

        role_rows = [row for row in branches if row["option"] > 0]
        observed_flags = (
            int(any("renew" in row["role_tuple"].split("+") for row in role_rows)),
            int(any("fell_bank" in row["role_tuple"].split("+") for row in role_rows)),
            int(any("mine_bank" in row["role_tuple"].split("+") for row in role_rows)),
            int(any(row["train_goal"] != "none" for row in role_rows)),
        )
        recorded_flags = (
            control["has_renew"],
            control["has_fell"],
            control["has_mine"],
            control["has_train_goal"],
        )
        role_flag_mismatches += int(observed_flags != recorded_flags)

    scenario_references = defaultdict(lambda: {"farm": set(), "resident": set()})
    for row in rows:
        scenario = row["seed"], row["seat"], row["opponent"]
        scenario_references[scenario]["farm"].add(reference_signature(row, "farm"))
        scenario_references[scenario]["resident"].add(
            reference_signature(row, "resident")
        )
    inconsistent_scenario_references = sum(
        len(signatures["farm"]) != 1 or len(signatures["resident"]) != 1
        for signatures in scenario_references.values()
    )
    manifest_reference_mismatches = 0
    if manifest_references is not None:
        for scenario, signatures in scenario_references.items():
            expected = manifest_references.get(scenario)
            if expected is None:
                manifest_reference_mismatches += 1
                continue
            farm = next(iter(signatures["farm"]))
            resident = next(iter(signatures["resident"]))
            manifest_reference_mismatches += int(
                (farm[0], farm[1], farm[2], farm[5]) != expected["farm"]
            )
            manifest_reference_mismatches += int(
                (resident[0], resident[1], resident[2]) != expected["resident"]
            )

    control_rows = [row for row in rows if row["option"] == 0]
    noncontrol_rows = [row for row in rows if row["option"] > 0]
    renew_roots = sum(row["has_renew"] for row in control_rows)
    fell_roots = sum(row["has_fell"] for row in control_rows)
    feasible_train_roots = {
        root_key(row) for row in noncontrol_rows if row["train_success"]
    }
    mine_or_train_roots = sum(
        row["has_mine"] or root_key(row) in feasible_train_roots
        for row in control_rows
    )
    invalid_direct_commands = sum(row["invalid_direct_commands"] for row in rows)
    train_above_three = sum(row["max_own_workers"] > 3 for row in rows)
    impossible_train_status = sum(
        row["train_success"]
        and (row["train_goal"] == "none" or row["max_own_workers"] != 3)
        for row in rows
    )
    inconsistent_deltas = sum(not delta_fields_consistent(row) for row in rows)
    failed_identity_rows = sum(not row["control_identity_match"] for row in rows)

    expected_root_count = len(expected_roots)
    scale_gate = len(actual_roots) >= 240 and len(noncontrol_rows) >= 10_000
    support_gate = renew_roots >= 40 and fell_roots >= 80 and mine_or_train_roots >= 120
    structural_complete = (
        actual_roots == expected_roots
        and len(grouped) == expected_root_count
        and duplicate_options == 0
        and duplicate_plan_keys == 0
        and missing_controls == 0
        and noncontiguous_options == 0
        and plan_count_mismatches == 0
        and plan_limit_violations == 0
        and root_metadata_mismatches == 0
        and reference_mismatches == 0
        and control_outcome_mismatches == 0
        and not plan_key_errors
        and crossing_error_count == 0
        and role_flag_mismatches == 0
        and inconsistent_scenario_references == 0
        and manifest_reference_mismatches == 0
        and invalid_root_turns == 0
        and invalid_terminal_turns == 0
        and invalid_bundle_turns == 0
        and invalid_predicted_completion == 0
        and invalid_direct_commands == 0
        and train_above_three == 0
        and impossible_train_status == 0
        and inconsistent_deltas == 0
        and failed_identity_rows == 0
    )
    integrity = {
        "expected_roots": expected_root_count,
        "nominal_roots": len(nominal_roots),
        "actual_roots": len(actual_roots),
        "missing_roots": len(expected_roots - actual_roots),
        "unexpected_roots": len(actual_roots - expected_roots),
        "actual_rows": len(rows),
        "control_rows": len(control_rows),
        "noncontrol_rows": len(noncontrol_rows),
        "duplicate_options": duplicate_options,
        "duplicate_plan_keys": duplicate_plan_keys,
        "missing_or_duplicate_controls": missing_controls,
        "noncontiguous_option_roots": noncontiguous_options,
        "plan_count_mismatch_roots": plan_count_mismatches,
        "plan_limit_violations": plan_limit_violations,
        "root_metadata_mismatches": root_metadata_mismatches,
        "reference_mismatches": reference_mismatches,
        "control_outcome_mismatches": control_outcome_mismatches,
        "plan_key_errors": dict(plan_key_errors),
        "train_crossing_errors": crossing_error_count,
        "role_flag_mismatches": role_flag_mismatches,
        "inconsistent_scenario_references": inconsistent_scenario_references,
        "manifest_reference_mismatches": manifest_reference_mismatches,
        "invalid_root_turns": invalid_root_turns,
        "invalid_terminal_turns": invalid_terminal_turns,
        "invalid_bundle_turns": invalid_bundle_turns,
        "invalid_predicted_completion": invalid_predicted_completion,
        "invalid_direct_commands": invalid_direct_commands,
        "train_above_three_workers": train_above_three,
        "impossible_train_status_rows": impossible_train_status,
        "inconsistent_delta_rows": inconsistent_deltas,
        "failed_control_identity_rows": failed_identity_rows,
        "repeat_identity_verified": repeat_identity_verified,
        "manifest_complete": manifest_complete,
        "renew_roots": renew_roots,
        "fell_roots": fell_roots,
        "mine_roots": sum(row["has_mine"] for row in control_rows),
        "feasible_train_roots": len(feasible_train_roots),
        "mine_or_feasible_train_roots": mine_or_train_roots,
        "scale_gate": scale_gate,
        "support_gate": support_gate,
        "structural_complete": structural_complete,
        "seeds": sorted({row["seed"] for row in rows}),
        "seats": sorted({row["seat"] for row in rows}),
        "opponents": sorted({row["opponent"] for row in rows}),
    }
    integrity["complete"] = (
        structural_complete
        and repeat_identity_verified
        and manifest_complete
        and scale_gate
        and support_gate
    )
    return integrity, dict(grouped)


def oracle_order(row: dict) -> tuple:
    """Ascending key implementing the frozen maximum-margin tie break."""

    return (
        -row["margin"],
        0 if row["option"] == 0 else 1,
        row["overridden_actions"],
        0 if row["train_goal"] == "none" else 1,
        row["plan_key"],
    )


def select_oracle(branches: list[dict]) -> dict:
    return min(branches, key=oracle_order)


def clustered_summary(rows: list[dict], field: str) -> dict:
    by_seed = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row[field])
    return robust_summary(
        statistics.mean(values) for _, values in sorted(by_seed.items())
    )


def negative_margin_mass(values) -> int:
    return sum(max(-value, 0) for value in values)


def mean_by(rows: list[dict], key: str, value: str) -> dict[str, float]:
    groups = defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row[value])
    return {
        label: statistics.mean(values) for label, values in sorted(groups.items())
    }


def status_counts(rows: list[dict]) -> dict[str, int]:
    counts = Counter()
    for row in rows:
        for encoded in row["statuses"].split(","):
            if not encoded:
                continue
            _, separator, status = encoded.partition(":")
            counts[status if separator else encoded] += 1
    return dict(sorted(counts.items()))


def grouped_selected_metrics(rows: list[dict], key: str) -> dict[str, dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[str(row[key])].append(row)
    return {
        label: {
            "n": len(values),
            "mean_margin_delta_farm": statistics.mean(
                row["margin_delta_farm"] for row in values
            ),
            "mean_own_score_delta_farm": statistics.mean(
                row["own_score_delta_farm"] for row in values
            ),
            "mean_opponent_score_delta_farm": statistics.mean(
                row["opponent_score_delta_farm"] for row in values
            ),
            "mean_overridden_actions": statistics.mean(
                row["overridden_actions"] for row in values
            ),
        }
        for label, values in sorted(groups.items())
    }


def role_presence_metrics(rows: list[dict]) -> dict[str, dict]:
    groups = defaultdict(list)
    for row in rows:
        for role in set(row["role_tuple"].split("+")):
            groups[role].append(row)
    return {
        role: {
            "n": len(values),
            "mean_margin_delta_farm": statistics.mean(
                row["margin_delta_farm"] for row in values
            ),
            "mean_own_score_delta_farm": statistics.mean(
                row["own_score_delta_farm"] for row in values
            ),
            "mean_opponent_score_delta_farm": statistics.mean(
                row["opponent_score_delta_farm"] for row in values
            ),
        }
        for role, values in sorted(groups.items())
    }


def oracle_analysis(grouped: dict[tuple[int, int, str, int], list[dict]]) -> dict:
    selected = []
    controls = []
    for key, branches in sorted(grouped.items()):
        choice = dict(select_oracle(branches))
        choice["root_key"] = list(key)
        selected.append(choice)
        controls.append(next(row for row in branches if row["option"] == 0))

    changed = [row for row in selected if row["option"] != 0]
    role_counts = Counter(row["role_tuple"] for row in changed)
    opponent_gains = {
        opponent: statistics.mean(
            row["margin_delta_farm"]
            for row in selected
            if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    selected_gain = robust_summary(row["margin_delta_farm"] for row in changed)
    margin_gain = clustered_summary(selected, "margin_delta_farm")
    own_delta = clustered_summary(selected, "own_score_delta_farm")
    opponent_delta = clustered_summary(selected, "opponent_score_delta_farm")
    own_vs_resident = clustered_summary(selected, "own_score_delta_resident")
    opponent_vs_resident = clustered_summary(
        selected, "opponent_score_delta_resident"
    )

    control_margins = [row["farm_margin"] for row in controls]
    oracle_margins = [row["margin"] for row in selected]
    tail = {
        "catastrophe_threshold": -100,
        "farm_catastrophes": sum(value <= -100 for value in control_margins),
        "oracle_catastrophes": sum(value <= -100 for value in oracle_margins),
        "farm_catastrophe_frequency": sum(value <= -100 for value in control_margins)
        / len(control_margins),
        "oracle_catastrophe_frequency": sum(value <= -100 for value in oracle_margins)
        / len(oracle_margins),
        "farm_negative_margin_mass": negative_margin_mass(control_margins),
        "oracle_negative_margin_mass": negative_margin_mass(oracle_margins),
    }
    broad_roles = {role: count for role, count in role_counts.items() if count >= 10}
    gates = {
        "noncontrol_selected_at_least_25pct": len(changed) / len(selected) >= 0.25,
        "mean_margin_gain_at_least_20": margin_gain["mean"] >= 20,
        "selected_mean_gain_at_least_35": selected_gain["mean"] is not None
        and selected_gain["mean"] >= 35,
        "selected_median_gain_at_least_15": selected_gain["median"] is not None
        and selected_gain["median"] >= 15,
        "mean_own_score_delta_at_least_minus_20": own_delta["mean"] >= -20,
        "mean_opponent_score_delta_at_most_minus_20": opponent_delta["mean"] <= -20,
        "own_score_advantage_vs_resident_at_least_68": own_vs_resident["mean"]
        >= 68,
        "opponent_score_excess_vs_resident_at_most_65": opponent_vs_resident[
            "mean"
        ]
        <= 65,
        "all_opponent_mean_gains_nonnegative": all(
            value >= 0 for value in opponent_gains.values()
        ),
        "six_opponent_mean_gains_at_least_10": sum(
            value >= 10 for value in opponent_gains.values()
        )
        >= 6,
        "two_role_tuples_selected_at_least_10_times": len(broad_roles) >= 2,
        "catastrophe_frequency_not_increased": tail["oracle_catastrophe_frequency"]
        <= tail["farm_catastrophe_frequency"],
        "negative_margin_mass_not_increased": tail["oracle_negative_margin_mass"]
        <= tail["farm_negative_margin_mass"],
    }

    return {
        "roots": len(selected),
        "selected_noncontrol_roots": len(changed),
        "selected_noncontrol_fraction": len(changed) / len(selected),
        "margin_gain_vs_farm_seed_clustered": margin_gain,
        "margin_gain_vs_farm_per_root": robust_summary(
            row["margin_delta_farm"] for row in selected
        ),
        "selected_root_margin_gain": selected_gain,
        "own_score_delta_vs_farm_seed_clustered": own_delta,
        "opponent_score_delta_vs_farm_seed_clustered": opponent_delta,
        "own_score_delta_vs_resident_seed_clustered": own_vs_resident,
        "opponent_score_delta_vs_resident_seed_clustered": opponent_vs_resident,
        "absolute_oracle": {
            "margin": clustered_summary(selected, "margin"),
            "own_score": clustered_summary(selected, "own_score"),
            "opponent_score": clustered_summary(selected, "opponent_score"),
            "own_wood": clustered_summary(selected, "own_wood"),
            "opponent_wood": clustered_summary(selected, "opponent_wood"),
            "own_workers": clustered_summary(selected, "own_workers"),
        },
        "farm_control": {
            "margin": clustered_summary(controls, "farm_margin"),
            "own_score": clustered_summary(controls, "farm_own_score"),
            "opponent_score": clustered_summary(controls, "farm_opponent_score"),
        },
        "opponent_mean_margin_gains": opponent_gains,
        "opponents_at_least_10": sum(
            value >= 10 for value in opponent_gains.values()
        ),
        "seat_mean_margin_gains": mean_by(selected, "seat", "margin_delta_farm"),
        "checkpoint_mean_margin_gains": mean_by(
            selected, "checkpoint", "margin_delta_farm"
        ),
        "selected_role_tuple_counts": dict(sorted(role_counts.items())),
        "selected_role_tuple_metrics": grouped_selected_metrics(
            changed, "role_tuple"
        ),
        "selected_role_presence_metrics": role_presence_metrics(changed),
        "role_tuples_selected_at_least_10_times": broad_roles,
        "selected_train_goal_counts": dict(
            sorted(Counter(row["train_goal"] for row in changed).items())
        ),
        "selected_train_successes": sum(row["train_success"] for row in changed),
        "selected_status_counts": status_counts(changed),
        "selected_checkpoint_metrics": grouped_selected_metrics(
            changed, "checkpoint"
        ),
        "selected_opponent_metrics": grouped_selected_metrics(changed, "opponent"),
        "mean_selected_overridden_actions": (
            statistics.mean(row["overridden_actions"] for row in changed)
            if changed
            else None
        ),
        "tail": tail,
        "gates": gates,
        "passes_all_representation_gates": all(gates.values()),
        "selections": [
            {
                "seed": row["seed"],
                "seat": row["seat"],
                "opponent": row["opponent"],
                "checkpoint": row["checkpoint"],
                "option": row["option"],
                "plan_key": row["plan_key"],
                "role_tuple": row["role_tuple"],
                "train_goal": row["train_goal"],
                "margin_delta_farm": row["margin_delta_farm"],
                "own_score_delta_farm": row["own_score_delta_farm"],
                "opponent_score_delta_farm": row["opponent_score_delta_farm"],
                "overridden_actions": row["overridden_actions"],
                "train_success": row["train_success"],
            }
            for row in selected
        ],
    }


def analyze(
    rows: list[dict],
    seed_start: int,
    seed_count: int,
    repeat_identity_verified: bool = True,
    scenario_manifest_rows: list[dict] | None = None,
) -> dict:
    if scenario_manifest_rows is None:
        manifest_report = {"provided": False, "complete": True}
        expected_roots = None
        manifest_references = None
    else:
        manifest_report, expected_roots, manifest_references = (
            validate_scenario_manifest(
                scenario_manifest_rows, seed_start, seed_count
            )
        )
    integrity, grouped = validate_grid(
        rows,
        seed_start,
        seed_count,
        repeat_identity_verified,
        expected_roots_override=expected_roots,
        manifest_complete=manifest_report["complete"],
        manifest_references=manifest_references,
    )
    report = {
        "protocol": "D35b factorized joint persistent-bundle oracle",
        "seed_start": seed_start,
        "seed_count": seed_count,
        "scenario_manifest": manifest_report,
        "integrity": integrity,
    }
    if not integrity["complete"]:
        report.update(
            {
                "confirmation_authorized": False,
                "decision": "invalid_integrity_do_not_select_outcomes",
            }
        )
        return report
    oracle = oracle_analysis(grouped)
    passed = oracle["passes_all_representation_gates"]
    report.update(
        {
            "oracle": oracle,
            "confirmation_authorized": passed,
            "decision": (
                "open_sealed_confirmation"
                if passed
                else "reject_bundle_grammar_leave_confirmation_sealed"
            ),
        }
    )
    return report


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path("data/analysis/live-agent-6553250")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=base / "d35b-factorized-joint-bundle-development-9200000-9200009.tsv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "d35b-factorized-joint-bundle-development-2026-07-20.json",
    )
    parser.add_argument(
        "--integrity-repeat-a",
        type=Path,
        default=base / "d35b-integrity-repeat-a-9200000.tsv",
    )
    parser.add_argument(
        "--integrity-repeat-b",
        type=Path,
        default=base / "d35b-integrity-repeat-b-9200000.tsv",
    )
    parser.add_argument(
        "--scenario-manifest",
        type=Path,
        help="runner task/root manifest (defaults to INPUT.scenarios.tsv)",
    )
    parser.add_argument("--seed-start", type=int, default=9_200_000)
    parser.add_argument("--seed-count", type=int, default=10)
    args = parser.parse_args()

    repeat_a_sha = sha256(args.integrity_repeat_a)
    repeat_b_sha = sha256(args.integrity_repeat_b)
    repeat_identity = repeat_a_sha == repeat_b_sha
    scenario_manifest = args.scenario_manifest or Path(
        f"{args.input}.scenarios.tsv"
    )
    report = analyze(
        read_rows(args.input),
        args.seed_start,
        args.seed_count,
        repeat_identity_verified=repeat_identity,
        scenario_manifest_rows=read_scenario_manifest(scenario_manifest),
    )
    report["provenance"] = {
        "input": str(args.input),
        "input_sha256": sha256(args.input),
        "integrity_repeat_a": str(args.integrity_repeat_a),
        "integrity_repeat_a_sha256": repeat_a_sha,
        "integrity_repeat_b": str(args.integrity_repeat_b),
        "integrity_repeat_b_sha256": repeat_b_sha,
        "scenario_manifest": str(scenario_manifest),
        "scenario_manifest_sha256": sha256(scenario_manifest),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "integrity": report["integrity"]["complete"],
                "confirmation_authorized": report["confirmation_authorized"],
                "selected_noncontrol_fraction": report.get("oracle", {}).get(
                    "selected_noncontrol_fraction"
                ),
                "mean_margin_gain": report.get("oracle", {})
                .get("margin_gain_vs_farm_seed_clustered", {})
                .get("mean"),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
