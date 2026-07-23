#!/usr/bin/env python3
"""Analyze the D36 resident-anchored constrained repeated joint oracle."""

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


DEFAULT_SEEDS = tuple(range(9_500_000, 9_500_008))
OPPONENT_EXCESS_CEILING = 65
MAX_NONCONTROL_EPOCHS = 4
LAST_EPOCH_TURN = 220
INTEGER_FIELDS = (
    "seed",
    "seat",
    "epoch",
    "epoch_turn",
    "option",
    "feasible",
    "selected",
    "unconstrained_selected",
    "predicted_eta",
    "predicted_reward",
    "rate_score",
    "competitive_target_count",
    "opponent_target_count",
    "ambiguous_target_count",
    "rollout_overridden_actions",
    "rollout_invalid_direct_commands",
    "rollout_bundle_end_turn",
    "rollout_execution_terminal",
    "rollout_own_score",
    "rollout_opponent_score",
    "rollout_margin",
    "rollout_own_wood",
    "rollout_opponent_wood",
    "rollout_own_workers",
    "rollout_opponent_workers",
    "rollout_terminal_turn",
    "rollout_attribution_failures",
    "rollout_history_mismatch",
    "rollout_cell_mismatch",
    "rollout_max_own_workers",
    "rollout_terminal_hash",
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
    "one_shot_terminal_hash",
    "unconstrained_own_score",
    "unconstrained_opponent_score",
    "unconstrained_margin",
    "unconstrained_own_wood",
    "unconstrained_opponent_wood",
    "unconstrained_own_workers",
    "unconstrained_opponent_workers",
    "unconstrained_terminal_turn",
    "unconstrained_terminal_hash",
    "selected_noncontrol_epochs",
    "selected_competitive_epochs",
    "infeasible_selection_failures",
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
    "repeated_cell_mismatch",
    "repeated_max_own_workers",
    "repeated_terminal_hash",
    "resident_own_score",
    "resident_opponent_score",
    "resident_margin",
    "resident_own_wood",
    "resident_opponent_wood",
    "resident_own_workers",
    "resident_opponent_workers",
    "resident_terminal_turn",
    "resident_terminal_hash",
    "repeated_margin_delta_resident",
    "repeated_own_score_delta_resident",
    "repeated_opponent_score_delta_resident",
    "one_shot_margin_delta_resident",
    "one_shot_own_score_delta_resident",
    "one_shot_opponent_score_delta_resident",
    "repeated_margin_delta_one_shot",
    "repeated_own_score_delta_one_shot",
    "repeated_opponent_score_delta_one_shot",
    "unconstrained_margin_delta_resident",
    "unconstrained_own_score_delta_resident",
    "unconstrained_opponent_score_delta_resident",
    "repeated_opponent_excess",
    "one_shot_opponent_excess",
    "unconstrained_opponent_excess",
    "opponent_excess_ceiling",
)
MANIFEST_INTEGER_FIELDS = (
    "seed",
    "seat",
    "eligible",
    "start_turn",
    "prefix_attribution_failures",
    "start_history_mismatch",
    "start_cell_mismatch",
    "independent_resident_match",
    "resident_own_score",
    "resident_opponent_score",
    "resident_margin",
    "resident_own_wood",
    "resident_opponent_wood",
    "resident_own_workers",
    "resident_opponent_workers",
    "resident_terminal_turn",
    "resident_attribution_failures",
    "resident_history_mismatch",
    "resident_cell_mismatch",
    "resident_max_own_workers",
    "resident_terminal_hash",
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
    eligible_tasks = set()
    malformed_eligibility = 0
    integrity_failures = 0
    score_errors = 0
    invalid_turns = 0
    above_three = 0
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
        integrity_failures += (
            row["prefix_attribution_failures"]
            + row["start_history_mismatch"]
            + row["start_cell_mismatch"]
            + row["resident_attribution_failures"]
            + row["resident_history_mismatch"]
            + row["resident_cell_mismatch"]
            + int(row["independent_resident_match"] != 1)
            + int(row["resident_terminal_hash"] <= 0)
        )
        score_errors += int(
            row["resident_margin"]
            != row["resident_own_score"] - row["resident_opponent_score"]
        )
        invalid_turns += int(not 2 <= row["resident_terminal_turn"] <= 301)
        above_three += int(row["resident_max_own_workers"] > 3)
        references[task] = {
            "start_turn": row["start_turn"],
            "resident": outcome_tuple(row, "resident"),
            "resident_terminal_hash": row["resident_terminal_hash"],
        }
    eligible_floor = len(eligible_tasks) >= 100
    complete = (
        actual_tasks == expected_tasks
        and duplicate_tasks == 0
        and malformed_eligibility == 0
        and integrity_failures == 0
        and score_errors == 0
        and invalid_turns == 0
        and above_three == 0
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
        "integrity_failures": integrity_failures,
        "score_errors": score_errors,
        "invalid_terminal_turns": invalid_turns,
        "branches_above_three_workers": above_three,
        "complete": complete,
    }
    return report, eligible_tasks, references


def constrained_order(row: dict) -> tuple:
    return (
        0 if row["feasible"] else 1,
        -row["rollout_own_score"],
        row["rollout_opponent_score"],
        0 if row["option"] == 0 else 1,
        row["rollout_overridden_actions"],
        row["plan_key"],
    )


def select_constrained(rows: list[dict]) -> dict:
    return min(rows, key=constrained_order)


def unconstrained_order(row: dict) -> tuple:
    return (
        -row["rollout_margin"],
        0 if row["option"] == 0 else 1,
        row["rollout_overridden_actions"],
        row["plan_key"],
    )


def select_unconstrained(rows: list[dict]) -> dict:
    return min(rows, key=unconstrained_order)


def delta_consistent(row: dict) -> bool:
    return (
        row["rollout_margin"]
        == row["rollout_own_score"] - row["rollout_opponent_score"]
        and row["one_shot_margin"]
        == row["one_shot_own_score"] - row["one_shot_opponent_score"]
        and row["unconstrained_margin"]
        == row["unconstrained_own_score"] - row["unconstrained_opponent_score"]
        and row["repeated_margin"]
        == row["repeated_own_score"] - row["repeated_opponent_score"]
        and row["resident_margin"]
        == row["resident_own_score"] - row["resident_opponent_score"]
        and row["repeated_margin_delta_resident"]
        == row["repeated_margin"] - row["resident_margin"]
        and row["repeated_own_score_delta_resident"]
        == row["repeated_own_score"] - row["resident_own_score"]
        and row["repeated_opponent_score_delta_resident"]
        == row["repeated_opponent_score"] - row["resident_opponent_score"]
        and row["one_shot_margin_delta_resident"]
        == row["one_shot_margin"] - row["resident_margin"]
        and row["one_shot_own_score_delta_resident"]
        == row["one_shot_own_score"] - row["resident_own_score"]
        and row["one_shot_opponent_score_delta_resident"]
        == row["one_shot_opponent_score"] - row["resident_opponent_score"]
        and row["repeated_margin_delta_one_shot"]
        == row["repeated_margin"] - row["one_shot_margin"]
        and row["repeated_own_score_delta_one_shot"]
        == row["repeated_own_score"] - row["one_shot_own_score"]
        and row["repeated_opponent_score_delta_one_shot"]
        == row["repeated_opponent_score"] - row["one_shot_opponent_score"]
        and row["unconstrained_margin_delta_resident"]
        == row["unconstrained_margin"] - row["resident_margin"]
        and row["unconstrained_own_score_delta_resident"]
        == row["unconstrained_own_score"] - row["resident_own_score"]
        and row["unconstrained_opponent_score_delta_resident"]
        == row["unconstrained_opponent_score"] - row["resident_opponent_score"]
        and row["repeated_opponent_excess"]
        == row["repeated_opponent_score"] - row["resident_opponent_score"]
        and row["one_shot_opponent_excess"]
        == row["one_shot_opponent_score"] - row["resident_opponent_score"]
        and row["unconstrained_opponent_excess"]
        == row["unconstrained_opponent_score"] - row["resident_opponent_score"]
        and row["opponent_excess_ceiling"] == OPPONENT_EXCESS_CEILING
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
    counters = Counter()
    plan_errors = Counter()
    task_summaries = []

    for task, task_rows in sorted(tasks.items()):
        representative = task_rows[0]
        epoch_numbers = sorted({row["epoch"] for row in task_rows})
        counters["epoch_sequence_errors"] += int(
            epoch_numbers != list(range(len(epoch_numbers)))
        )
        final_signatures = {
            (
                row["one_shot_catalog"],
                row["one_shot_key"],
                outcome_tuple(row, "one_shot"),
                row["one_shot_terminal_hash"],
                row["unconstrained_catalog"],
                row["unconstrained_key"],
                outcome_tuple(row, "unconstrained"),
                row["unconstrained_terminal_hash"],
                row["selected_noncontrol_epochs"],
                row["selected_competitive_epochs"],
                row["stop_reason"],
                row["infeasible_selection_failures"],
                row["replay_mismatches"],
                row["strict_advance_failures"],
                row["execution_prefix_mismatches"],
                outcome_tuple(row, "repeated"),
                row["repeated_terminal_hash"],
                row["repeated_attribution_failures"],
                row["repeated_history_mismatch"],
                row["repeated_cell_mismatch"],
                row["repeated_max_own_workers"],
                outcome_tuple(row, "resident"),
                row["resident_terminal_hash"],
            )
            for row in task_rows
        }
        counters["final_consistency_errors"] += int(len(final_signatures) != 1)
        expected = references.get(task)
        if expected is None:
            counters["reference_errors"] += 1
        else:
            counters["reference_errors"] += int(
                outcome_tuple(representative, "resident")
                != expected["resident"]
                or representative["resident_terminal_hash"]
                != expected["resident_terminal_hash"]
                or representative["epoch_turn"] != expected["start_turn"]
            )
        counters["recorded_error_counters"] += int(
            representative["infeasible_selection_failures"] != 0
            or representative["replay_mismatches"] != 0
            or representative["strict_advance_failures"] != 0
            or representative["execution_prefix_mismatches"] != 0
        )
        counters["rollout_integrity_errors"] += (
            representative["repeated_attribution_failures"]
            + representative["repeated_history_mismatch"]
            + representative["repeated_cell_mismatch"]
            + int(representative["repeated_terminal_hash"] <= 0)
        )
        counters["branches_above_three_workers"] += int(
            representative["repeated_max_own_workers"] > 3
        )
        counters["constraint_errors"] += int(
            representative["repeated_opponent_excess"]
            > OPPONENT_EXCESS_CEILING
        )

        selected_rows = []
        prior_selected = None
        first_selected = None
        first_unconstrained = None
        for epoch in epoch_numbers:
            branches = epochs[(*task, epoch)]
            options = [row["option"] for row in branches]
            keys = [row["plan_key"] for row in branches]
            counters["duplicate_options"] += len(options) - len(set(options))
            counters["duplicate_plan_keys"] += len(keys) - len(set(keys))
            controls = [row for row in branches if row["option"] == 0]
            selected = [row for row in branches if row["selected"] == 1]
            unconstrained_selected = [
                row for row in branches if row["unconstrained_selected"] == 1
            ]
            counters["bad_controls"] += int(len(controls) != 1)
            counters["bad_selections"] += int(len(selected) != 1)
            counters["unconstrained_selection_errors"] += int(
                (epoch == 0 and len(unconstrained_selected) != 1)
                or (epoch > 0 and len(unconstrained_selected) != 0)
            )
            if len(controls) != 1 or len(selected) != 1:
                continue
            control = controls[0]
            chosen = selected[0]
            selected_rows.append(chosen)
            first_selected = first_selected or chosen
            if epoch == 0 and len(unconstrained_selected) == 1:
                first_unconstrained = unconstrained_selected[0]
                counters["unconstrained_selection_errors"] += int(
                    first_unconstrained is not select_unconstrained(branches)
                )
            counters["bad_selections"] += int(
                chosen is not select_constrained(branches)
            )
            counters["constraint_errors"] += int(not chosen["feasible"])
            counters["option_grid_errors"] += int(
                set(options) != set(range(control["root_plan_count"] + 1))
                or len(branches) != control["root_plan_count"] + 1
            )
            generic = sum(row["catalog"] == "generic" for row in branches)
            competitive = sum(row["catalog"] == "competitive" for row in branches)
            counters["catalog_count_errors"] += int(
                generic != control["generic_plan_count"]
                or competitive != control["competitive_plan_count"]
                or generic + competitive != control["root_plan_count"]
            )
            counters["plan_limit_errors"] += int(generic > 96 or competitive > 64)
            counters["metadata_errors"] += int(
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
            counters["root_integrity_errors"] += (
                control["attribution_cell_mismatch"] + control["history_mismatch"]
            )
            if prior_selected is not None:
                counters["epoch_chain_errors"] += int(
                    prior_selected["option"] == 0
                    or control["epoch_turn"]
                    != prior_selected["executed_end_turn"]
                )
            prior_selected = chosen

            for row in branches:
                error = plan_error(row)
                if error is not None:
                    plan_errors[error] += 1
                expected_feasible = (
                    row["rollout_opponent_score"] - row["resident_opponent_score"]
                    <= OPPONENT_EXCESS_CEILING
                )
                counters["constraint_errors"] += int(
                    row["feasible"] not in {0, 1}
                    or bool(row["feasible"]) != expected_feasible
                    or row["opponent_excess_ceiling"]
                    != OPPONENT_EXCESS_CEILING
                )
                counters["invalid_direct_commands"] += row[
                    "rollout_invalid_direct_commands"
                ]
                counters["rollout_integrity_errors"] += (
                    row["rollout_attribution_failures"]
                    + row["rollout_history_mismatch"]
                    + row["rollout_cell_mismatch"]
                    + int(row["rollout_terminal_hash"] <= 0)
                )
                counters["branches_above_three_workers"] += int(
                    row["rollout_max_own_workers"] > 3
                )
                counters["invalid_turns"] += int(
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
                counters["delta_errors"] += int(not delta_consistent(row))

            counters["invalid_direct_commands"] += chosen[
                "execution_invalid_direct_commands"
            ]
            counters["execution_prefix_errors"] += int(
                chosen["execution_prefix_match"] != 1
                or chosen["executed_end_turn"]
                != chosen["rollout_bundle_end_turn"]
                or chosen["execution_statuses"] != chosen["rollout_statuses"]
                or chosen["execution_overridden_actions"]
                != chosen["rollout_overridden_actions"]
                or chosen["execution_invalid_direct_commands"]
                != chosen["rollout_invalid_direct_commands"]
                or chosen["execution_terminal"]
                != chosen["rollout_execution_terminal"]
            )
            counters["replay_errors"] += int(
                chosen["selected_rollout_replay_match"] != 1
            )
            if chosen["option"] == 0:
                counters["strict_advance_errors"] += int(
                    chosen["executed_end_turn"] != chosen["epoch_turn"]
                    or chosen["rollout_bundle_end_turn"]
                    != chosen["epoch_turn"]
                )
            else:
                counters["strict_advance_errors"] += int(
                    chosen["executed_end_turn"] <= chosen["epoch_turn"]
                    and chosen["execution_terminal"] == 0
                )

        if not selected_rows or first_unconstrained is None:
            continue
        first_control = next(
            row for row in epochs[(*task, 0)] if row["option"] == 0
        )
        counters["first_root_identity_errors"] += int(
            outcome_tuple(first_control, "rollout")
            != outcome_tuple(representative, "resident")
            or first_control["rollout_terminal_hash"]
            != representative["resident_terminal_hash"]
            or outcome_tuple(first_selected, "rollout")
            != outcome_tuple(representative, "one_shot")
            or first_selected["rollout_terminal_hash"]
            != representative["one_shot_terminal_hash"]
            or first_selected["catalog"] != representative["one_shot_catalog"]
            or first_selected["plan_key"] != representative["one_shot_key"]
            or outcome_tuple(first_unconstrained, "rollout")
            != outcome_tuple(representative, "unconstrained")
            or first_unconstrained["rollout_terminal_hash"]
            != representative["unconstrained_terminal_hash"]
            or first_unconstrained["catalog"]
            != representative["unconstrained_catalog"]
            or first_unconstrained["plan_key"]
            != representative["unconstrained_key"]
        )
        selected_noncontrol = [row for row in selected_rows if row["option"] > 0]
        selected_competitive = [
            row for row in selected_noncontrol if row["catalog"] == "competitive"
        ]
        counters["final_consistency_errors"] += int(
            len(selected_noncontrol)
            != representative["selected_noncontrol_epochs"]
            or len(selected_competitive)
            != representative["selected_competitive_epochs"]
            or outcome_tuple(selected_rows[-1], "rollout")
            != outcome_tuple(representative, "repeated")
            or selected_rows[-1]["rollout_terminal_hash"]
            != representative["repeated_terminal_hash"]
        )
        reason = representative["stop_reason"]
        last = selected_rows[-1]
        counters["stop_reason_errors"] += int(
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

    tasks_with_two = sum(
        row["selected_noncontrol_epochs"] >= 2 for row in task_summaries
    )
    scale_gate = len(rows) >= 5_000
    repeated_support_gate = tasks_with_two >= 25
    error_names = (
        "duplicate_options",
        "duplicate_plan_keys",
        "bad_controls",
        "bad_selections",
        "unconstrained_selection_errors",
        "option_grid_errors",
        "catalog_count_errors",
        "plan_limit_errors",
        "metadata_errors",
        "epoch_sequence_errors",
        "epoch_chain_errors",
        "reference_errors",
        "root_integrity_errors",
        "rollout_integrity_errors",
        "first_root_identity_errors",
        "final_consistency_errors",
        "stop_reason_errors",
        "execution_prefix_errors",
        "replay_errors",
        "strict_advance_errors",
        "invalid_direct_commands",
        "branches_above_three_workers",
        "invalid_turns",
        "delta_errors",
        "recorded_error_counters",
        "constraint_errors",
    )
    structural_complete = (
        actual_tasks == eligible_tasks
        and not plan_errors
        and all(counters[name] == 0 for name in error_names)
    )
    integrity = {
        "eligible_tasks": len(eligible_tasks),
        "actual_tasks_with_rows": len(actual_tasks),
        "missing_eligible_tasks": len(eligible_tasks - actual_tasks),
        "unexpected_tasks": len(actual_tasks - eligible_tasks),
        "actual_option_rollouts": len(rows),
        "actual_epochs": len(epochs),
        "tasks_with_two_or_more_noncontrol_epochs": tasks_with_two,
        **{name: counters[name] for name in error_names},
        "plan_errors": dict(plan_errors),
        "repeat_rows_verified": repeat_rows_verified,
        "repeat_manifests_verified": repeat_manifests_verified,
        "option_rollout_floor_at_least_5000": scale_gate,
        "multi_epoch_task_floor_at_least_25": repeated_support_gate,
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
        "margin_gain_vs_resident": clustered_summary(
            tasks, "repeated_margin_delta_resident"
        ),
        "own_score_gain_vs_resident": clustered_summary(
            tasks, "repeated_own_score_delta_resident"
        ),
        "opponent_score_excess_vs_resident": clustered_summary(
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
        "one_shot_margin_gain_vs_resident": clustered_summary(
            tasks, "one_shot_margin_delta_resident"
        ),
        "one_shot_own_score_gain_vs_resident": clustered_summary(
            tasks, "one_shot_own_score_delta_resident"
        ),
        "one_shot_opponent_excess_vs_resident": clustered_summary(
            tasks, "one_shot_opponent_score_delta_resident"
        ),
        "unconstrained_margin_gain_vs_resident": clustered_summary(
            tasks, "unconstrained_margin_delta_resident"
        ),
        "unconstrained_own_score_gain_vs_resident": clustered_summary(
            tasks, "unconstrained_own_score_delta_resident"
        ),
        "unconstrained_opponent_excess_vs_resident": clustered_summary(
            tasks, "unconstrained_opponent_score_delta_resident"
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
    noncontrol_tasks = sum(row["selected_noncontrol_epochs"] > 0 for row in tasks)
    multi_epoch_tasks = sum(row["selected_noncontrol_epochs"] >= 2 for row in tasks)
    noncontrol_fraction = noncontrol_tasks / len(tasks)
    multi_epoch_fraction = multi_epoch_tasks / len(tasks)
    own_family_means = {
        opponent: statistics.mean(
            row["repeated_own_score_delta_resident"]
            for row in tasks
            if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    margin_family_means = {
        opponent: statistics.mean(
            row["repeated_margin_delta_resident"]
            for row in tasks
            if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    selected_families = sorted({row["opponent"] for row in selected_competitive})
    selected_epochs = sorted({row["epoch"] for row in selected_competitive})
    unconstrained_infeasible = sum(
        row["unconstrained_opponent_excess"] > OPPONENT_EXCESS_CEILING
        for row in tasks
    )
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
                "own_score_delta_control": choice["rollout_own_score"]
                - control["rollout_own_score"],
                "opponent_score_delta_control": choice["rollout_opponent_score"]
                - control["rollout_opponent_score"],
                "margin_delta_control": choice["rollout_margin"]
                - control["rollout_margin"],
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
            "own_score_delta_control": robust_summary(
                row["own_score_delta_control"] for row in values
            ),
            "opponent_score_delta_control": robust_summary(
                row["opponent_score_delta_control"] for row in values
            ),
            "margin_delta_control": robust_summary(
                row["margin_delta_control"] for row in values
            ),
        }

    resident_tail = tail_summary([row["resident_margin"] for row in tasks])
    one_shot_tail = tail_summary([row["one_shot_margin"] for row in tasks])
    repeated_tail = tail_summary([row["repeated_margin"] for row in tasks])
    gates = {
        "noncontrol_selected_in_at_least_25pct": noncontrol_fraction >= 0.25,
        "two_epochs_in_at_least_15pct": multi_epoch_fraction >= 0.15,
        "own_score_gain_vs_resident_at_least_68": metrics[
            "own_score_gain_vs_resident"
        ]["mean"]
        >= 68,
        "opponent_score_excess_vs_resident_at_most_65": metrics[
            "opponent_score_excess_vs_resident"
        ]["mean"]
        <= 65,
        "margin_gain_vs_resident_at_least_25": metrics[
            "margin_gain_vs_resident"
        ]["mean"]
        >= 25,
        "all_opponent_own_score_means_nonnegative": all(
            value >= 0 for value in own_family_means.values()
        ),
        "six_opponent_own_score_means_at_least_50": sum(
            value >= 50 for value in own_family_means.values()
        )
        >= 6,
        "all_opponent_margin_means_nonnegative": all(
            value >= 0 for value in margin_family_means.values()
        ),
        "six_opponent_margin_means_at_least_15": sum(
            value >= 15 for value in margin_family_means.values()
        )
        >= 6,
        "repetition_adds_at_least_5_own_score": metrics[
            "own_score_delta_vs_one_shot"
        ]["mean"]
        >= 5,
        "repetition_margin_nonnegative": metrics["margin_delta_vs_one_shot"][
            "mean"
        ]
        >= 0,
        "competitive_targets_span_four_opponents": len(selected_families) >= 4,
        "competitive_targets_span_two_epochs": len(selected_epochs) >= 2,
        "catastrophe_frequency_not_above_resident_or_one_shot": repeated_tail[
            "catastrophe_frequency"
        ]
        <= min(
            resident_tail["catastrophe_frequency"],
            one_shot_tail["catastrophe_frequency"],
        ),
        "negative_mass_not_above_resident_or_one_shot": repeated_tail[
            "negative_margin_mass"
        ]
        <= min(
            resident_tail["negative_margin_mass"],
            one_shot_tail["negative_margin_mass"],
        ),
    }
    return {
        "eligible_tasks": len(tasks),
        "noncontrol_tasks": noncontrol_tasks,
        "noncontrol_fraction": noncontrol_fraction,
        "multi_epoch_tasks": multi_epoch_tasks,
        "multi_epoch_fraction": multi_epoch_fraction,
        "selected_noncontrol_epoch_count": len(selected_noncontrol),
        "selected_competitive_epoch_count": len(selected_competitive),
        "selected_epoch_count_distribution": dict(
            sorted(Counter(row["selected_noncontrol_epochs"] for row in tasks).items())
        ),
        "stop_reason_counts": dict(
            sorted(Counter(row["stop_reason"] for row in tasks).items())
        ),
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
        "unconstrained_first_root_infeasible_tasks": unconstrained_infeasible,
        "unconstrained_first_root_infeasible_fraction": unconstrained_infeasible
        / len(tasks),
        "metrics": metrics,
        "opponent_own_score_means": own_family_means,
        "opponent_margin_means": margin_family_means,
        "opponents_own_at_least_50": sum(
            value >= 50 for value in own_family_means.values()
        ),
        "opponents_margin_at_least_15": sum(
            value >= 15 for value in margin_family_means.values()
        ),
        "epoch_mechanism": epoch_mechanism,
        "tail": {
            "catastrophe_threshold": -100,
            "resident": resident_tail,
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
        "protocol": "D36 resident-anchored constrained joint oracle",
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
            "resident_constrained_oracle": value,
            "confirmation_authorized": value["passes_all_gates"],
            "decision": (
                "open_sealed_confirmation_export_constraint_scheduler_dataset"
                if value["passes_all_gates"]
                else "reject_resident_overlay_advance_complete_learned_controller"
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
        default=[base / "d36-resident-constrained-development-9500000-9500007.tsv"],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "d36-resident-constrained-development-2026-07-21.json",
    )
    parser.add_argument(
        "--integrity-repeat-a",
        type=Path,
        default=base / "d36-integrity-repeat-a-9500000.tsv",
    )
    parser.add_argument(
        "--integrity-repeat-b",
        type=Path,
        default=base / "d36-integrity-repeat-b-9500000.tsv",
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
                "own_score_gain": report.get("resident_constrained_oracle", {})
                .get("metrics", {})
                .get("own_score_gain_vs_resident", {})
                .get("mean"),
                "margin_gain": report.get("resident_constrained_oracle", {})
                .get("metrics", {})
                .get("margin_gain_vs_resident", {})
                .get("mean"),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
