#!/usr/bin/env python3
"""Analyze the D35d greedy repeated job-boundary oracle."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d35b_factorized_joint_bundle_oracle import (
    OPPONENTS,
    robust_summary,
)
from cgauto.analyze_d35c_provenance_competitive_bundle_oracle import plan_error


DEFAULT_SEEDS = tuple(range(9_400_000, 9_400_008))
MAX_NONCONTROL_EPOCHS = 4
LAST_EPOCH_TURN = 220
INTEGER_FIELDS = (
    "seed",
    "seat",
    "epoch",
    "epoch_turn",
    "option",
    "selected",
    "predicted_eta",
    "predicted_reward",
    "rate_score",
    "competitive_target_count",
    "opponent_target_count",
    "ambiguous_target_count",
    "rollout_overridden_actions",
    "rollout_invalid_direct_commands",
    "rollout_train_success",
    "rollout_max_own_workers",
    "rollout_bundle_end_turn",
    "rollout_own_score",
    "rollout_opponent_score",
    "rollout_margin",
    "rollout_own_wood",
    "rollout_opponent_wood",
    "rollout_own_workers",
    "rollout_opponent_workers",
    "rollout_terminal_turn",
    "root_plan_count",
    "generic_plan_count",
    "competitive_plan_count",
    "root_natural_plants",
    "root_own_plants",
    "root_opponent_plants",
    "root_ambiguous_plants",
    "attribution_cell_mismatch",
    "history_mismatch",
    "executed_end_turn",
    "execution_overridden_actions",
    "execution_invalid_direct_commands",
    "execution_terminal",
    "execution_prefix_match",
    "selected_rollout_replay_match",
    "one_shot_own_score",
    "one_shot_opponent_score",
    "one_shot_margin",
    "one_shot_own_wood",
    "one_shot_opponent_wood",
    "one_shot_own_workers",
    "one_shot_opponent_workers",
    "one_shot_terminal_turn",
    "selected_noncontrol_epochs",
    "selected_competitive_epochs",
    "selection_mismatches",
    "replay_mismatches",
    "strict_advance_failures",
    "execution_prefix_mismatches",
    "repeated_own_score",
    "repeated_opponent_score",
    "repeated_margin",
    "repeated_own_wood",
    "repeated_opponent_wood",
    "repeated_own_workers",
    "repeated_opponent_workers",
    "repeated_terminal_turn",
    "repeated_attribution_failures",
    "repeated_history_mismatch",
    "repeated_max_own_workers",
    "repeated_terminal_hash",
    "farm_own_score",
    "farm_opponent_score",
    "farm_margin",
    "farm_own_wood",
    "farm_opponent_wood",
    "farm_own_workers",
    "farm_opponent_workers",
    "farm_terminal_turn",
    "resident_own_score",
    "resident_opponent_score",
    "resident_margin",
    "resident_own_wood",
    "resident_opponent_wood",
    "resident_own_workers",
    "resident_opponent_workers",
    "resident_terminal_turn",
    "repeated_margin_delta_farm",
    "repeated_own_score_delta_farm",
    "repeated_opponent_score_delta_farm",
    "repeated_margin_delta_resident",
    "repeated_own_score_delta_resident",
    "repeated_opponent_score_delta_resident",
    "repeated_margin_delta_one_shot",
    "repeated_own_score_delta_one_shot",
    "repeated_opponent_score_delta_one_shot",
    "one_shot_margin_delta_farm",
    "one_shot_own_score_delta_farm",
    "one_shot_opponent_score_delta_farm",
    "one_shot_margin_delta_resident",
    "one_shot_own_score_delta_resident",
    "one_shot_opponent_score_delta_resident",
)
MANIFEST_INTEGER_FIELDS = (
    "seed",
    "seat",
    "eligible",
    "start_turn",
    "prefix_attribution_failures",
    "farm_attribution_failures",
    "start_history_mismatch",
    "start_cell_mismatch",
    "farm_max_own_workers",
    "farm_own_score",
    "farm_opponent_score",
    "farm_margin",
    "farm_own_wood",
    "farm_opponent_wood",
    "farm_own_workers",
    "farm_opponent_workers",
    "farm_terminal_turn",
    "resident_own_score",
    "resident_opponent_score",
    "resident_margin",
    "resident_own_wood",
    "resident_opponent_wood",
    "resident_own_workers",
    "resident_opponent_workers",
    "resident_terminal_turn",
)


def read_rows(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            missing = set(INTEGER_FIELDS) - set(reader.fieldnames or ())
            if missing:
                raise ValueError(f"{path}: missing integer fields {sorted(missing)}")
            for row in reader:
                for field in INTEGER_FIELDS:
                    row[field] = int(row[field])
                rows.append(row)
    return rows


def read_manifests(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        with path.open(newline="") as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            missing = set(MANIFEST_INTEGER_FIELDS) - set(reader.fieldnames or ())
            if missing:
                raise ValueError(f"{path}: missing manifest fields {sorted(missing)}")
            for row in reader:
                for field in MANIFEST_INTEGER_FIELDS:
                    row[field] = int(row[field])
                rows.append(row)
    return rows


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def task_key(row: dict) -> tuple[int, int, str]:
    return row["seed"], row["seat"], row["opponent"]


def epoch_key(row: dict) -> tuple[int, int, str, int]:
    return *task_key(row), row["epoch"]


def outcome_tuple(row: dict, prefix: str) -> tuple[int, ...]:
    return tuple(
        row[f"{prefix}_{field}"]
        for field in (
            "own_score",
            "opponent_score",
            "margin",
            "own_wood",
            "opponent_wood",
            "own_workers",
            "opponent_workers",
            "terminal_turn",
        )
    )


def validate_manifest(
    rows: list[dict], expected_seeds: tuple[int, ...]
) -> tuple[dict, set[tuple[int, int, str]], dict]:
    expected_tasks = {
        (seed, seat, opponent)
        for seed in expected_seeds
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    grouped = defaultdict(list)
    for row in rows:
        grouped[task_key(row)].append(row)
    actual_tasks = set(grouped)
    duplicate_tasks = sum(len(values) - 1 for values in grouped.values())
    malformed_eligibility = 0
    attribution_failures = 0
    state_mismatches = 0
    score_errors = 0
    invalid_terminal_turns = 0
    branches_above_three = 0
    eligible_tasks = set()
    references = {}
    for task, values in grouped.items():
        row = values[0]
        eligible = row["eligible"] == 1
        malformed_eligibility += int(
            row["eligible"] not in {0, 1}
            or (eligible and not 50 <= row["start_turn"] <= 300)
            or (not eligible and row["start_turn"] != -1)
        )
        if eligible:
            eligible_tasks.add(task)
        attribution_failures += (
            row["prefix_attribution_failures"]
            + row["farm_attribution_failures"]
        )
        state_mismatches += row["start_history_mismatch"] + row["start_cell_mismatch"]
        score_errors += int(
            row["farm_margin"]
            != row["farm_own_score"] - row["farm_opponent_score"]
            or row["resident_margin"]
            != row["resident_own_score"] - row["resident_opponent_score"]
        )
        invalid_terminal_turns += int(
            not 2 <= row["farm_terminal_turn"] <= 301
            or not 2 <= row["resident_terminal_turn"] <= 301
        )
        branches_above_three += int(row["farm_max_own_workers"] > 3)
        references[task] = {
            "start_turn": row["start_turn"],
            "farm": outcome_tuple(row, "farm"),
            "resident": outcome_tuple(row, "resident"),
        }
    eligible_floor = len(eligible_tasks) >= 100
    complete = (
        actual_tasks == expected_tasks
        and duplicate_tasks == 0
        and malformed_eligibility == 0
        and attribution_failures == 0
        and state_mismatches == 0
        and score_errors == 0
        and invalid_terminal_turns == 0
        and branches_above_three == 0
        and eligible_floor
    )
    report = {
        "expected_tasks": len(expected_tasks),
        "actual_tasks": len(actual_tasks),
        "missing_tasks": len(expected_tasks - actual_tasks),
        "unexpected_tasks": len(actual_tasks - expected_tasks),
        "duplicate_tasks": duplicate_tasks,
        "eligible_tasks": len(eligible_tasks),
        "ineligible_tasks": len(expected_tasks) - len(eligible_tasks),
        "eligible_floor_at_least_100": eligible_floor,
        "malformed_eligibility_rows": malformed_eligibility,
        "attribution_failures": attribution_failures,
        "start_state_mismatches": state_mismatches,
        "score_errors": score_errors,
        "invalid_terminal_turns": invalid_terminal_turns,
        "branches_above_three_workers": branches_above_three,
        "complete": complete,
    }
    return report, eligible_tasks, references


def rollout_order(row: dict) -> tuple:
    return (
        -row["rollout_margin"],
        0 if row["option"] == 0 else 1,
        row["rollout_overridden_actions"],
        row["plan_key"],
    )


def select_rollout(rows: list[dict]) -> dict:
    return min(rows, key=rollout_order)


def delta_consistent(row: dict) -> bool:
    return (
        row["rollout_margin"]
        == row["rollout_own_score"] - row["rollout_opponent_score"]
        and row["one_shot_margin"]
        == row["one_shot_own_score"] - row["one_shot_opponent_score"]
        and row["repeated_margin"]
        == row["repeated_own_score"] - row["repeated_opponent_score"]
        and row["farm_margin"]
        == row["farm_own_score"] - row["farm_opponent_score"]
        and row["resident_margin"]
        == row["resident_own_score"] - row["resident_opponent_score"]
        and row["repeated_margin_delta_farm"]
        == row["repeated_margin"] - row["farm_margin"]
        and row["repeated_own_score_delta_farm"]
        == row["repeated_own_score"] - row["farm_own_score"]
        and row["repeated_opponent_score_delta_farm"]
        == row["repeated_opponent_score"] - row["farm_opponent_score"]
        and row["repeated_margin_delta_resident"]
        == row["repeated_margin"] - row["resident_margin"]
        and row["repeated_own_score_delta_resident"]
        == row["repeated_own_score"] - row["resident_own_score"]
        and row["repeated_opponent_score_delta_resident"]
        == row["repeated_opponent_score"] - row["resident_opponent_score"]
        and row["repeated_margin_delta_one_shot"]
        == row["repeated_margin"] - row["one_shot_margin"]
        and row["repeated_own_score_delta_one_shot"]
        == row["repeated_own_score"] - row["one_shot_own_score"]
        and row["repeated_opponent_score_delta_one_shot"]
        == row["repeated_opponent_score"] - row["one_shot_opponent_score"]
        and row["one_shot_margin_delta_farm"]
        == row["one_shot_margin"] - row["farm_margin"]
        and row["one_shot_own_score_delta_farm"]
        == row["one_shot_own_score"] - row["farm_own_score"]
        and row["one_shot_opponent_score_delta_farm"]
        == row["one_shot_opponent_score"] - row["farm_opponent_score"]
        and row["one_shot_margin_delta_resident"]
        == row["one_shot_margin"] - row["resident_margin"]
        and row["one_shot_own_score_delta_resident"]
        == row["one_shot_own_score"] - row["resident_own_score"]
        and row["one_shot_opponent_score_delta_resident"]
        == row["one_shot_opponent_score"] - row["resident_opponent_score"]
    )


def validate_rows(
    rows: list[dict],
    eligible_tasks: set[tuple[int, int, str]],
    references: dict,
    manifest_complete: bool,
    repeat_rows_verified: bool,
    repeat_manifests_verified: bool,
) -> tuple[dict, dict, list[dict]]:
    tasks = defaultdict(list)
    epochs = defaultdict(list)
    for row in rows:
        tasks[task_key(row)].append(row)
        epochs[epoch_key(row)].append(row)
    actual_tasks = set(tasks)
    duplicate_options = 0
    duplicate_plan_keys = 0
    bad_controls = 0
    bad_selections = 0
    option_grid_errors = 0
    catalog_count_errors = 0
    plan_limit_errors = 0
    plan_errors = Counter()
    metadata_errors = 0
    epoch_sequence_errors = 0
    epoch_chain_errors = 0
    reference_errors = 0
    one_shot_errors = 0
    final_consistency_errors = 0
    stop_reason_errors = 0
    execution_prefix_errors = 0
    replay_errors = 0
    strict_advance_errors = 0
    invalid_direct_commands = 0
    train_successes = 0
    attribution_mismatches = 0
    history_mismatches = 0
    branches_above_three = 0
    invalid_turns = 0
    delta_errors = 0
    recorded_error_counters = 0
    terminal_hash_errors = 0
    task_summaries = []

    for task, task_rows in sorted(tasks.items()):
        representative = task_rows[0]
        epoch_numbers = sorted({row["epoch"] for row in task_rows})
        epoch_sequence_errors += int(epoch_numbers != list(range(len(epoch_numbers))))
        final_fields = {
            (
                row["one_shot_catalog"],
                row["one_shot_key"],
                outcome_tuple(row, "one_shot"),
                row["selected_noncontrol_epochs"],
                row["selected_competitive_epochs"],
                row["stop_reason"],
                row["selection_mismatches"],
                row["replay_mismatches"],
                row["strict_advance_failures"],
                row["execution_prefix_mismatches"],
                outcome_tuple(row, "repeated"),
                row["repeated_attribution_failures"],
                row["repeated_history_mismatch"],
                row["repeated_max_own_workers"],
                row["repeated_terminal_hash"],
                outcome_tuple(row, "farm"),
                outcome_tuple(row, "resident"),
            )
            for row in task_rows
        }
        final_consistency_errors += int(len(final_fields) != 1)
        expected = references.get(task)
        if expected is None:
            reference_errors += 1
        else:
            reference_errors += int(
                outcome_tuple(representative, "farm") != expected["farm"]
                or outcome_tuple(representative, "resident") != expected["resident"]
                or representative["epoch_turn"] != expected["start_turn"]
            )
        recorded_error_counters += int(
            representative["selection_mismatches"] != 0
            or representative["replay_mismatches"] != 0
            or representative["strict_advance_failures"] != 0
            or representative["execution_prefix_mismatches"] != 0
        )
        attribution_mismatches += representative["repeated_attribution_failures"]
        history_mismatches += representative["repeated_history_mismatch"]
        branches_above_three += int(representative["repeated_max_own_workers"] > 3)
        terminal_hash_errors += int(representative["repeated_terminal_hash"] <= 0)

        selected_rows = []
        previous_selected = None
        first_selected = None
        for epoch in epoch_numbers:
            branches = epochs[(*task, epoch)]
            options = [row["option"] for row in branches]
            keys = [row["plan_key"] for row in branches]
            duplicate_options += len(options) - len(set(options))
            duplicate_plan_keys += len(keys) - len(set(keys))
            controls = [row for row in branches if row["option"] == 0]
            selected = [row for row in branches if row["selected"] == 1]
            bad_controls += int(len(controls) != 1)
            bad_selections += int(len(selected) != 1)
            if len(controls) != 1 or len(selected) != 1:
                continue
            control = controls[0]
            chosen = selected[0]
            selected_rows.append(chosen)
            first_selected = first_selected or chosen
            bad_selections += int(chosen is not select_rollout(branches))
            option_grid_errors += int(
                set(options) != set(range(control["root_plan_count"] + 1))
                or len(branches) != control["root_plan_count"] + 1
            )
            generic = sum(row["catalog"] == "generic" for row in branches)
            competitive = sum(row["catalog"] == "competitive" for row in branches)
            catalog_count_errors += int(
                generic != control["generic_plan_count"]
                or competitive != control["competitive_plan_count"]
                or generic + competitive != control["root_plan_count"]
            )
            plan_limit_errors += int(generic > 96 or competitive > 64)
            metadata_errors += int(
                len(
                    {
                        (
                            row["epoch_turn"],
                            row["root_plan_count"],
                            row["generic_plan_count"],
                            row["competitive_plan_count"],
                            row["root_natural_plants"],
                            row["root_own_plants"],
                            row["root_opponent_plants"],
                            row["root_ambiguous_plants"],
                            row["attribution_cell_mismatch"],
                            row["history_mismatch"],
                        )
                        for row in branches
                    }
                )
                != 1
            )
            attribution_mismatches += control["attribution_cell_mismatch"]
            history_mismatches += control["history_mismatch"]
            if previous_selected is not None:
                epoch_chain_errors += int(
                    previous_selected["option"] == 0
                    or control["epoch_turn"] != previous_selected["executed_end_turn"]
                )
            previous_selected = chosen

            for row in branches:
                error = plan_error(row)
                if error is not None:
                    plan_errors[error] += 1
                invalid_direct_commands += row["rollout_invalid_direct_commands"]
                train_successes += row["rollout_train_success"]
                branches_above_three += int(row["rollout_max_own_workers"] > 3)
                invalid_turns += int(
                    not 50 <= row["epoch_turn"] <= LAST_EPOCH_TURN
                    or not row["epoch_turn"]
                    <= row["rollout_bundle_end_turn"]
                    <= 301
                    or not 2 <= row["rollout_terminal_turn"] <= 301
                    or (
                        row["option"] > 0
                        and row["epoch_turn"] + row["predicted_eta"] > 300
                    )
                )
                delta_errors += int(not delta_consistent(row))

            invalid_direct_commands += chosen["execution_invalid_direct_commands"]
            execution_prefix_errors += int(
                chosen["execution_prefix_match"] != 1
                or chosen["executed_end_turn"] != chosen["rollout_bundle_end_turn"]
                or chosen["execution_statuses"] != chosen["rollout_statuses"]
                or chosen["execution_overridden_actions"]
                != chosen["rollout_overridden_actions"]
                or chosen["execution_invalid_direct_commands"]
                != chosen["rollout_invalid_direct_commands"]
            )
            replay_errors += int(chosen["selected_rollout_replay_match"] != 1)
            if chosen["option"] == 0:
                strict_advance_errors += int(
                    chosen["executed_end_turn"] != chosen["epoch_turn"]
                    or chosen["rollout_bundle_end_turn"] != chosen["epoch_turn"]
                )
            else:
                strict_advance_errors += int(
                    chosen["executed_end_turn"] <= chosen["epoch_turn"]
                    and chosen["execution_terminal"] == 0
                )

        if not selected_rows:
            continue
        first_control = next(
            row for row in epochs[(*task, 0)] if row["option"] == 0
        )
        one_shot_errors += int(
            outcome_tuple(first_control, "rollout")
            != outcome_tuple(representative, "farm")
            or outcome_tuple(first_selected, "rollout")
            != outcome_tuple(representative, "one_shot")
            or first_selected["catalog"] != representative["one_shot_catalog"]
            or first_selected["plan_key"] != representative["one_shot_key"]
        )
        selected_noncontrol = [row for row in selected_rows if row["option"] > 0]
        selected_competitive = [
            row for row in selected_noncontrol if row["catalog"] == "competitive"
        ]
        final_consistency_errors += int(
            len(selected_noncontrol) != representative["selected_noncontrol_epochs"]
            or len(selected_competitive)
            != representative["selected_competitive_epochs"]
            or outcome_tuple(selected_rows[-1], "rollout")
            != outcome_tuple(representative, "repeated")
        )
        reason = representative["stop_reason"]
        last = selected_rows[-1]
        stop_reason_errors += int(
            reason not in {"control", "terminal", "epoch_cap", "turn_cutoff"}
            or (
                reason == "control"
                and (last["option"] != 0 or last["execution_terminal"] != 0)
            )
            or (
                reason == "terminal"
                and (last["option"] == 0 or last["execution_terminal"] != 1)
            )
            or (
                reason == "epoch_cap"
                and len(selected_noncontrol) != MAX_NONCONTROL_EPOCHS
            )
            or (
                reason == "turn_cutoff"
                and (
                    last["option"] == 0
                    or last["executed_end_turn"] <= LAST_EPOCH_TURN
                )
            )
        )
        task_summaries.append(representative)

    tasks_with_two_noncontrol = sum(
        row["selected_noncontrol_epochs"] >= 2 for row in task_summaries
    )
    scale_gate = len(rows) >= 5_000
    repeated_support_gate = tasks_with_two_noncontrol >= 30
    structural_complete = (
        actual_tasks == eligible_tasks
        and duplicate_options == 0
        and duplicate_plan_keys == 0
        and bad_controls == 0
        and bad_selections == 0
        and option_grid_errors == 0
        and catalog_count_errors == 0
        and plan_limit_errors == 0
        and not plan_errors
        and metadata_errors == 0
        and epoch_sequence_errors == 0
        and epoch_chain_errors == 0
        and reference_errors == 0
        and one_shot_errors == 0
        and final_consistency_errors == 0
        and stop_reason_errors == 0
        and execution_prefix_errors == 0
        and replay_errors == 0
        and strict_advance_errors == 0
        and invalid_direct_commands == 0
        and train_successes == 0
        and attribution_mismatches == 0
        and history_mismatches == 0
        and branches_above_three == 0
        and invalid_turns == 0
        and delta_errors == 0
        and recorded_error_counters == 0
        and terminal_hash_errors == 0
    )
    integrity = {
        "eligible_tasks": len(eligible_tasks),
        "actual_tasks_with_rows": len(actual_tasks),
        "missing_eligible_tasks": len(eligible_tasks - actual_tasks),
        "unexpected_tasks": len(actual_tasks - eligible_tasks),
        "actual_option_rollouts": len(rows),
        "actual_epochs": len(epochs),
        "tasks_with_two_or_more_noncontrol_epochs": tasks_with_two_noncontrol,
        "duplicate_options": duplicate_options,
        "duplicate_plan_keys": duplicate_plan_keys,
        "bad_controls": bad_controls,
        "bad_selections": bad_selections,
        "option_grid_errors": option_grid_errors,
        "catalog_count_errors": catalog_count_errors,
        "plan_limit_errors": plan_limit_errors,
        "plan_errors": dict(plan_errors),
        "metadata_errors": metadata_errors,
        "epoch_sequence_errors": epoch_sequence_errors,
        "epoch_chain_errors": epoch_chain_errors,
        "reference_errors": reference_errors,
        "one_shot_errors": one_shot_errors,
        "final_consistency_errors": final_consistency_errors,
        "stop_reason_errors": stop_reason_errors,
        "execution_prefix_errors": execution_prefix_errors,
        "selected_rollout_replay_errors": replay_errors,
        "strict_advance_errors": strict_advance_errors,
        "invalid_direct_commands": invalid_direct_commands,
        "train_successes": train_successes,
        "attribution_mismatches": attribution_mismatches,
        "history_mismatches": history_mismatches,
        "branches_above_three_workers": branches_above_three,
        "invalid_turns": invalid_turns,
        "delta_errors": delta_errors,
        "recorded_error_counters": recorded_error_counters,
        "terminal_hash_errors": terminal_hash_errors,
        "repeat_rows_verified": repeat_rows_verified,
        "repeat_manifests_verified": repeat_manifests_verified,
        "option_rollout_floor_at_least_5000": scale_gate,
        "multi_epoch_task_floor_at_least_30": repeated_support_gate,
        "structural_complete": structural_complete,
        "manifest_complete": manifest_complete,
    }
    integrity["complete"] = (
        structural_complete
        and manifest_complete
        and repeat_rows_verified
        and repeat_manifests_verified
        and scale_gate
        and repeated_support_gate
    )
    return integrity, dict(epochs), task_summaries


def clustered_summary(rows: list[dict], field: str) -> dict:
    by_seed = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row[field])
    return robust_summary(
        statistics.mean(values) for _, values in sorted(by_seed.items())
    )


def tail_summary(values: list[int]) -> dict:
    return {
        "n": len(values),
        "catastrophes": sum(value <= -100 for value in values),
        "catastrophe_frequency": sum(value <= -100 for value in values)
        / len(values),
        "negative_margin_mass": sum(max(-value, 0) for value in values),
    }


def analyze_value(epochs: dict, tasks: list[dict]) -> dict:
    metrics = {
        "margin_gain_vs_farm": clustered_summary(
            tasks, "repeated_margin_delta_farm"
        ),
        "own_score_delta_vs_farm": clustered_summary(
            tasks, "repeated_own_score_delta_farm"
        ),
        "opponent_score_delta_vs_farm": clustered_summary(
            tasks, "repeated_opponent_score_delta_farm"
        ),
        "own_score_delta_vs_resident": clustered_summary(
            tasks, "repeated_own_score_delta_resident"
        ),
        "opponent_score_delta_vs_resident": clustered_summary(
            tasks, "repeated_opponent_score_delta_resident"
        ),
        "margin_delta_vs_one_shot": clustered_summary(
            tasks, "repeated_margin_delta_one_shot"
        ),
        "own_score_delta_vs_one_shot": clustered_summary(
            tasks, "repeated_own_score_delta_one_shot"
        ),
        "opponent_score_delta_vs_one_shot": clustered_summary(
            tasks, "repeated_opponent_score_delta_one_shot"
        ),
        "absolute_margin": clustered_summary(tasks, "repeated_margin"),
        "absolute_own_score": clustered_summary(tasks, "repeated_own_score"),
        "absolute_opponent_score": clustered_summary(
            tasks, "repeated_opponent_score"
        ),
    }
    selected = [
        row
        for branches in epochs.values()
        for row in branches
        if row["selected"] == 1
    ]
    selected_noncontrol = [row for row in selected if row["option"] > 0]
    selected_competitive = [
        row for row in selected_noncontrol if row["catalog"] == "competitive"
    ]
    multi_epoch_tasks = sum(row["selected_noncontrol_epochs"] >= 2 for row in tasks)
    multi_epoch_fraction = multi_epoch_tasks / len(tasks)
    opponent_means = {
        opponent: statistics.mean(
            row["repeated_margin_delta_farm"]
            for row in tasks
            if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    selected_families = sorted({row["opponent"] for row in selected_competitive})
    selected_epochs = sorted({row["epoch"] for row in selected_competitive})
    local_epoch_deltas = []
    for key, branches in sorted(epochs.items()):
        control = next(row for row in branches if row["option"] == 0)
        choice = next(row for row in branches if row["selected"] == 1)
        local_epoch_deltas.append(
            {
                "seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "epoch": key[3],
                "selected_noncontrol": int(choice["option"] > 0),
                "catalog": choice["catalog"],
                "margin_delta_control": choice["rollout_margin"]
                - control["rollout_margin"],
                "own_score_delta_control": choice["rollout_own_score"]
                - control["rollout_own_score"],
                "opponent_score_delta_control": choice["rollout_opponent_score"]
                - control["rollout_opponent_score"],
            }
        )
    epoch_mechanism = {}
    for epoch in sorted({row["epoch"] for row in local_epoch_deltas}):
        values = [row for row in local_epoch_deltas if row["epoch"] == epoch]
        noncontrol = [row for row in values if row["selected_noncontrol"]]
        epoch_mechanism[str(epoch)] = {
            "tasks": len(values),
            "noncontrol_selected": len(noncontrol),
            "noncontrol_fraction": len(noncontrol) / len(values),
            "margin_delta_control": robust_summary(
                row["margin_delta_control"] for row in values
            ),
            "own_score_delta_control": robust_summary(
                row["own_score_delta_control"] for row in values
            ),
            "opponent_score_delta_control": robust_summary(
                row["opponent_score_delta_control"] for row in values
            ),
        }

    farm_tail = tail_summary([row["farm_margin"] for row in tasks])
    one_shot_tail = tail_summary([row["one_shot_margin"] for row in tasks])
    repeated_tail = tail_summary([row["repeated_margin"] for row in tasks])
    gates = {
        "two_epochs_in_at_least_25pct": multi_epoch_fraction >= 0.25,
        "margin_gain_vs_farm_at_least_30": metrics["margin_gain_vs_farm"][
            "mean"
        ]
        >= 30,
        "own_score_delta_vs_farm_at_least_minus_20": metrics[
            "own_score_delta_vs_farm"
        ]["mean"]
        >= -20,
        "opponent_score_delta_vs_farm_at_most_minus_20": metrics[
            "opponent_score_delta_vs_farm"
        ]["mean"]
        <= -20,
        "own_score_advantage_vs_resident_at_least_68": metrics[
            "own_score_delta_vs_resident"
        ]["mean"]
        >= 68,
        "opponent_score_excess_vs_resident_at_most_65": metrics[
            "opponent_score_delta_vs_resident"
        ]["mean"]
        <= 65,
        "opponent_score_delta_vs_one_shot_at_most_minus_6": metrics[
            "opponent_score_delta_vs_one_shot"
        ]["mean"]
        <= -6,
        "margin_delta_vs_one_shot_nonnegative": metrics[
            "margin_delta_vs_one_shot"
        ]["mean"]
        >= 0,
        "all_opponent_margin_means_nonnegative": all(
            value >= 0 for value in opponent_means.values()
        ),
        "six_opponent_margin_means_at_least_10": sum(
            value >= 10 for value in opponent_means.values()
        )
        >= 6,
        "competitive_targets_span_four_opponents": len(selected_families) >= 4,
        "competitive_targets_span_two_epochs": len(selected_epochs) >= 2,
        "catastrophe_frequency_not_above_farm_or_one_shot": repeated_tail[
            "catastrophe_frequency"
        ]
        <= min(
            farm_tail["catastrophe_frequency"],
            one_shot_tail["catastrophe_frequency"],
        ),
        "negative_mass_not_above_farm_or_one_shot": repeated_tail[
            "negative_margin_mass"
        ]
        <= min(
            farm_tail["negative_margin_mass"],
            one_shot_tail["negative_margin_mass"],
        ),
    }
    return {
        "eligible_tasks": len(tasks),
        "multi_epoch_tasks": multi_epoch_tasks,
        "multi_epoch_fraction": multi_epoch_fraction,
        "selected_noncontrol_epoch_count": len(selected_noncontrol),
        "selected_competitive_epoch_count": len(selected_competitive),
        "selected_epoch_count_distribution": dict(
            sorted(Counter(row["selected_noncontrol_epochs"] for row in tasks).items())
        ),
        "stop_reason_counts": dict(sorted(Counter(row["stop_reason"] for row in tasks).items())),
        "selected_catalog_counts": dict(
            sorted(Counter(row["catalog"] for row in selected_noncontrol).items())
        ),
        "selected_role_counts": dict(
            sorted(Counter(row["role_tuple"] for row in selected_noncontrol).items())
        ),
        "selected_owner_tuple_counts": dict(
            sorted(Counter(row["target_owners"] for row in selected_noncontrol).items())
        ),
        "selected_competitive_opponent_families": selected_families,
        "selected_competitive_epochs": selected_epochs,
        "selected_exclusive_opponent_targets": sum(
            row["opponent_target_count"] for row in selected_competitive
        ),
        "metrics": metrics,
        "opponent_mean_margin_gains": opponent_means,
        "opponents_at_least_10": sum(value >= 10 for value in opponent_means.values()),
        "epoch_mechanism": epoch_mechanism,
        "tail": {
            "catastrophe_threshold": -100,
            "farm": farm_tail,
            "one_shot": one_shot_tail,
            "repeated": repeated_tail,
        },
        "gates": gates,
        "passes_all_gates": all(gates.values()),
        "selections": [
            {
                "seed": row["seed"],
                "seat": row["seat"],
                "opponent": row["opponent"],
                "epoch": row["epoch"],
                "epoch_turn": row["epoch_turn"],
                "catalog": row["catalog"],
                "plan_key": row["plan_key"],
                "role_tuple": row["role_tuple"],
                "target_owners": row["target_owners"],
                "local_margin_delta_control": next(
                    value["margin_delta_control"]
                    for value in local_epoch_deltas
                    if (
                        value["seed"],
                        value["seat"],
                        value["opponent"],
                        value["epoch"],
                    )
                    == (
                        row["seed"],
                        row["seat"],
                        row["opponent"],
                        row["epoch"],
                    )
                ),
            }
            for row in selected_noncontrol
        ],
    }


def analyze(
    rows: list[dict],
    manifest_rows: list[dict],
    expected_seeds: tuple[int, ...] = DEFAULT_SEEDS,
    repeat_rows_verified: bool = True,
    repeat_manifests_verified: bool = True,
) -> dict:
    manifest, eligible_tasks, references = validate_manifest(
        manifest_rows, expected_seeds
    )
    integrity, epochs, tasks = validate_rows(
        rows,
        eligible_tasks,
        references,
        manifest["complete"],
        repeat_rows_verified,
        repeat_manifests_verified,
    )
    report = {
        "protocol": "D35d greedy repeated job-boundary oracle",
        "expected_seeds": list(expected_seeds),
        "manifest": manifest,
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
    value = analyze_value(epochs, tasks)
    report.update(
        {
            "repeated_oracle": value,
            "confirmation_authorized": value["passes_all_gates"],
            "decision": (
                "open_sealed_confirmation_export_scheduler_dataset"
                if value["passes_all_gates"]
                else "reject_repeated_productive_farm_advance_resident_joint_objective"
            ),
        }
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path("data/analysis/live-agent-6553250")
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        default=[base / "d35d-repeated-job-boundary-development-9400000-9400007.tsv"],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "d35d-repeated-job-boundary-development-2026-07-21.json",
    )
    parser.add_argument(
        "--integrity-repeat-a",
        type=Path,
        default=base / "d35d-integrity-repeat-a-9400000.tsv",
    )
    parser.add_argument(
        "--integrity-repeat-b",
        type=Path,
        default=base / "d35d-integrity-repeat-b-9400000.tsv",
    )
    args = parser.parse_args()
    if not args.inputs:
        parser.error("at least one development input is required")

    manifests = [Path(f"{path}.scenarios.tsv") for path in args.inputs]
    repeat_a_manifest = Path(f"{args.integrity_repeat_a}.scenarios.tsv")
    repeat_b_manifest = Path(f"{args.integrity_repeat_b}.scenarios.tsv")
    repeat_a_sha = sha256(args.integrity_repeat_a)
    repeat_b_sha = sha256(args.integrity_repeat_b)
    repeat_a_manifest_sha = sha256(repeat_a_manifest)
    repeat_b_manifest_sha = sha256(repeat_b_manifest)
    report = analyze(
        read_rows(args.inputs),
        read_manifests(manifests),
        repeat_rows_verified=repeat_a_sha == repeat_b_sha,
        repeat_manifests_verified=repeat_a_manifest_sha == repeat_b_manifest_sha,
    )
    report["provenance"] = {
        "inputs": [
            {"path": str(path), "sha256": sha256(path)} for path in args.inputs
        ],
        "manifests": [
            {"path": str(path), "sha256": sha256(path)} for path in manifests
        ],
        "integrity_repeat_a": {
            "path": str(args.integrity_repeat_a),
            "sha256": repeat_a_sha,
            "manifest_path": str(repeat_a_manifest),
            "manifest_sha256": repeat_a_manifest_sha,
        },
        "integrity_repeat_b": {
            "path": str(args.integrity_repeat_b),
            "sha256": repeat_b_sha,
            "manifest_path": str(repeat_b_manifest),
            "manifest_sha256": repeat_b_manifest_sha,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "integrity": report["integrity"]["complete"],
                "confirmation_authorized": report["confirmation_authorized"],
                "multi_epoch_fraction": report.get("repeated_oracle", {}).get(
                    "multi_epoch_fraction"
                ),
                "margin_gain": report.get("repeated_oracle", {})
                .get("metrics", {})
                .get("margin_gain_vs_farm", {})
                .get("mean"),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
