#!/usr/bin/env python3
"""Analyze D35c paired generic/provenance-aware bundle upper bounds."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d35b_factorized_joint_bundle_oracle import (
    CHECKPOINTS,
    OPPONENTS,
    parse_plan_key,
    robust_summary,
)


DEFAULT_SEEDS = (*range(9_300_000, 9_300_010), *range(9_300_040, 9_300_050))
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
    "generic_plan_count",
    "competitive_plan_count",
    "competitive_target_count",
    "opponent_target_count",
    "ambiguous_target_count",
    "has_competitive_target",
    "has_opponent_fell",
    "has_opponent_renew_or_harvest",
    "attribution_cell_mismatch",
    "root_natural_plants",
    "root_own_plants",
    "root_opponent_plants",
    "root_ambiguous_plants",
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
    "attribution_failures",
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


def root_key(row: dict) -> tuple[int, int, str, int]:
    return row["seed"], row["seat"], row["opponent"], row["checkpoint"]


def task_key(row: dict) -> tuple[int, int, str]:
    return row["seed"], row["seat"], row["opponent"]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def clustered_summary(rows: list[dict], field: str) -> dict:
    by_seed = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row[field])
    return robust_summary(
        statistics.mean(values) for _, values in sorted(by_seed.items())
    )


def negative_mass(values) -> int:
    return sum(max(-value, 0) for value in values)


def validate_manifest(rows: list[dict], expected_seeds: tuple[int, ...]) -> tuple:
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
    malformed_roots = 0
    attribution_failures = 0
    inconsistent_scores = 0
    invalid_turns = 0
    eligible_roots = set()
    references = {}
    zero_root_tasks = []
    for task, values in grouped.items():
        row = values[0]
        checkpoints = row["captured_checkpoints"]
        root_turns = row["root_turns"]
        malformed_roots += int(
            row["root_count"] != len(checkpoints)
            or len(checkpoints) != len(root_turns)
            or len(checkpoints) != len(set(checkpoints))
            or any(checkpoint not in CHECKPOINTS for checkpoint in checkpoints)
            or any(
                turn < checkpoint or turn > 300
                for checkpoint, turn in zip(checkpoints, root_turns)
            )
        )
        eligible_roots.update((*task, checkpoint) for checkpoint in checkpoints)
        attribution_failures += row["attribution_failures"]
        inconsistent_scores += int(
            row["farm_margin"]
            != row["farm_own_score"] - row["farm_opponent_score"]
            or row["resident_margin"]
            != row["resident_own_score"] - row["resident_opponent_score"]
        )
        invalid_turns += int(
            not 2 <= row["farm_terminal_turn"] <= 301
            or not 2 <= row["resident_terminal_turn"] <= 301
        )
        if row["root_count"] == 0:
            zero_root_tasks.append(
                {
                    "seed": task[0],
                    "seat": task[1],
                    "opponent": task[2],
                    "farm_workers": row["farm_own_workers"],
                    "farm_terminal_turn": row["farm_terminal_turn"],
                }
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
        and attribution_failures == 0
        and inconsistent_scores == 0
        and invalid_turns == 0
    )
    report = {
        "expected_tasks": len(expected_tasks),
        "actual_tasks": len(actual_tasks),
        "missing_tasks": len(expected_tasks - actual_tasks),
        "unexpected_tasks": len(actual_tasks - expected_tasks),
        "duplicate_tasks": duplicate_tasks,
        "nominal_roots": len(expected_tasks) * len(CHECKPOINTS),
        "eligible_roots": len(eligible_roots),
        "ineligible_roots": len(expected_tasks) * len(CHECKPOINTS)
        - len(eligible_roots),
        "malformed_root_lists": malformed_roots,
        "attribution_failures": attribution_failures,
        "inconsistent_scores": inconsistent_scores,
        "invalid_terminal_turns": invalid_turns,
        "zero_root_tasks": zero_root_tasks,
        "complete": complete,
    }
    return report, eligible_roots, references


def plan_error(row: dict) -> str | None:
    if row["option"] == 0:
        if (
            row["catalog"] != "control"
            or row["plan_key"] != "control"
            or row["role_tuple"] != "control"
            or row["target_owners"] != "none+none"
        ):
            return "control_encoding"
        return None
    if row["catalog"] not in {"generic", "competitive"}:
        return "catalog"
    try:
        jobs, train = parse_plan_key(row["plan_key"])
    except (TypeError, ValueError):
        return "parse"
    if train != "none" or len(jobs) != 2:
        return "shape_or_train"
    roles = [job["role"] for job in jobs]
    owners = row["target_owners"].split("+")
    if "+".join(roles) != row["role_tuple"] or len(owners) != 2:
        return "role_or_owner_tuple"
    if any(owner not in {"none", "natural", "own", "opponent", "ambiguous"} for owner in owners):
        return "owner_label"
    acquisitions = [
        job["target"]
        for job in jobs
        if job["target"] is not None
        and job["role"] in {"fell_bank", "harvest_bank", "renew", "mine_bank"}
    ]
    if len(acquisitions) != len(set(acquisitions)):
        return "acquisition_collision"
    planting = [job["plant_cell"] for job in jobs if job["plant_cell"] is not None]
    if len(planting) != len(set(planting)):
        return "plant_collision"
    competitive = sum(owner in {"opponent", "ambiguous"} for owner in owners)
    opponent = owners.count("opponent")
    ambiguous = owners.count("ambiguous")
    if (
        row["competitive_target_count"] != competitive
        or row["opponent_target_count"] != opponent
        or row["ambiguous_target_count"] != ambiguous
    ):
        return "target_counts"
    if row["catalog"] == "competitive" and competitive == 0:
        return "empty_competitive_extension"
    return None


def delta_consistent(row: dict) -> bool:
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


def validate_rows(
    rows: list[dict],
    expected_roots: set[tuple[int, int, str, int]],
    manifest_report: dict,
    manifest_references: dict,
    repeat_rows_verified: bool,
    repeat_manifests_verified: bool,
) -> tuple[dict, dict]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[root_key(row)].append(row)
    actual_roots = set(grouped)
    duplicate_options = 0
    duplicate_keys = 0
    bad_controls = 0
    option_grid_errors = 0
    plan_count_errors = 0
    catalog_count_errors = 0
    plan_limit_errors = 0
    metadata_errors = 0
    reference_errors = 0
    manifest_reference_errors = 0
    control_identity_errors = 0
    plan_errors = Counter()
    flag_errors = 0
    owner_count_errors = 0
    invalid_turns = 0

    for key, branches in grouped.items():
        options = [row["option"] for row in branches]
        keys = [row["plan_key"] for row in branches]
        duplicate_options += len(options) - len(set(options))
        duplicate_keys += len(keys) - len(set(keys))
        controls = [row for row in branches if row["option"] == 0]
        if len(controls) != 1:
            bad_controls += 1
            continue
        control = controls[0]
        if set(options) != set(range(control["root_plan_count"] + 1)):
            option_grid_errors += 1
        if len(branches) != control["root_plan_count"] + 1:
            plan_count_errors += 1
        generic = [row for row in branches if row["catalog"] == "generic"]
        competitive = [row for row in branches if row["catalog"] == "competitive"]
        if (
            len(generic) != control["generic_plan_count"]
            or len(competitive) != control["competitive_plan_count"]
            or len(generic) + len(competitive) != control["root_plan_count"]
        ):
            catalog_count_errors += 1
        if len(generic) > 96 or len(competitive) > 64:
            plan_limit_errors += 1
        metadata = {
            (
                row["root_turn"],
                row["root_plan_count"],
                row["generic_plan_count"],
                row["competitive_plan_count"],
                row["has_competitive_target"],
                row["has_opponent_fell"],
                row["has_opponent_renew_or_harvest"],
                row["attribution_cell_mismatch"],
                row["root_natural_plants"],
                row["root_own_plants"],
                row["root_opponent_plants"],
                row["root_ambiguous_plants"],
            )
            for row in branches
        }
        metadata_errors += int(len(metadata) != 1)
        farm_refs = {
            (
                row["farm_own_score"],
                row["farm_opponent_score"],
                row["farm_margin"],
                row["farm_own_wood"],
                row["farm_opponent_wood"],
                row["farm_terminal_turn"],
            )
            for row in branches
        }
        resident_refs = {
            (
                row["resident_own_score"],
                row["resident_opponent_score"],
                row["resident_margin"],
                row["resident_own_wood"],
                row["resident_opponent_wood"],
            )
            for row in branches
        }
        reference_errors += int(len(farm_refs) != 1) + int(len(resident_refs) != 1)
        expected = manifest_references.get(key[:3])
        if expected is None:
            manifest_reference_errors += 1
        else:
            farm = next(iter(farm_refs))
            resident = next(iter(resident_refs))
            manifest_reference_errors += int(
                (farm[0], farm[1], farm[2], farm[5]) != expected["farm"]
            )
            manifest_reference_errors += int(
                (resident[0], resident[1], resident[2]) != expected["resident"]
            )
        control_terminal = (
            control["own_score"],
            control["opponent_score"],
            control["margin"],
            control["own_wood"],
            control["opponent_wood"],
            control["terminal_turn"],
        )
        control_identity_errors += int(control_terminal != next(iter(farm_refs)))
        for row in branches:
            error = plan_error(row)
            if error is not None:
                plan_errors[error] += 1
            invalid_turns += int(
                row["root_turn"] < row["checkpoint"]
                or row["root_turn"] > 300
                or not row["root_turn"] <= row["bundle_end_turn"] <= 301
                or not 2 <= row["terminal_turn"] <= 301
                or (
                    row["option"] > 0
                    and row["root_turn"] + row["predicted_eta"] > 300
                )
            )
        noncontrol = [row for row in branches if row["option"] > 0]
        observed_flags = (
            int(any(row["competitive_target_count"] > 0 for row in noncontrol)),
            int(
                any(
                    any(
                        role == "fell_bank" and owner == "opponent"
                        for role, owner in zip(
                            row["role_tuple"].split("+"),
                            row["target_owners"].split("+"),
                        )
                    )
                    for row in noncontrol
                )
            ),
            int(
                any(
                    any(
                        role in {"harvest_bank", "renew"}
                        and owner == "opponent"
                        for role, owner in zip(
                            row["role_tuple"].split("+"),
                            row["target_owners"].split("+"),
                        )
                    )
                    for row in noncontrol
                )
            ),
        )
        recorded_flags = (
            control["has_competitive_target"],
            control["has_opponent_fell"],
            control["has_opponent_renew_or_harvest"],
        )
        flag_errors += int(observed_flags != recorded_flags)
        owner_count_errors += int(
            sum(
                control[field]
                for field in (
                    "root_natural_plants",
                    "root_own_plants",
                    "root_opponent_plants",
                    "root_ambiguous_plants",
                )
            )
            <= 0
        )

    controls = [row for row in rows if row["option"] == 0]
    generic_rows = [row for row in rows if row["catalog"] == "generic"]
    competitive_rows = [row for row in rows if row["catalog"] == "competitive"]
    direct_failures = sum(row["invalid_direct_commands"] for row in rows)
    attribution_mismatches = sum(row["attribution_cell_mismatch"] for row in controls)
    train_successes = sum(row["train_success"] for row in rows)
    above_three = sum(row["max_own_workers"] > 3 for row in rows)
    delta_errors = sum(not delta_consistent(row) for row in rows)
    failed_identity_rows = sum(not row["control_identity_match"] for row in rows)
    competitive_roots = sum(row["has_competitive_target"] for row in controls)
    opponent_fell_roots = sum(row["has_opponent_fell"] for row in controls)
    opponent_renew_roots = sum(
        row["has_opponent_renew_or_harvest"] for row in controls
    )
    scale_gate = len(actual_roots) >= 240 and len(rows) - len(controls) >= 10_000
    support_gate = (
        competitive_roots >= 80
        and len(competitive_rows) >= 5_000
        and opponent_fell_roots >= 20
        and opponent_renew_roots >= 20
    )
    structural_complete = (
        actual_roots == expected_roots
        and duplicate_options == 0
        and duplicate_keys == 0
        and bad_controls == 0
        and option_grid_errors == 0
        and plan_count_errors == 0
        and catalog_count_errors == 0
        and plan_limit_errors == 0
        and metadata_errors == 0
        and reference_errors == 0
        and manifest_reference_errors == 0
        and control_identity_errors == 0
        and not plan_errors
        and flag_errors == 0
        and owner_count_errors == 0
        and invalid_turns == 0
        and direct_failures == 0
        and attribution_mismatches == 0
        and train_successes == 0
        and above_three == 0
        and delta_errors == 0
        and failed_identity_rows == 0
    )
    integrity = {
        "expected_roots": len(expected_roots),
        "actual_roots": len(actual_roots),
        "missing_roots": len(expected_roots - actual_roots),
        "unexpected_roots": len(actual_roots - expected_roots),
        "actual_rows": len(rows),
        "control_rows": len(controls),
        "generic_rows": len(generic_rows),
        "competitive_rows": len(competitive_rows),
        "duplicate_options": duplicate_options,
        "duplicate_plan_keys": duplicate_keys,
        "bad_controls": bad_controls,
        "option_grid_errors": option_grid_errors,
        "plan_count_errors": plan_count_errors,
        "catalog_count_errors": catalog_count_errors,
        "plan_limit_errors": plan_limit_errors,
        "metadata_errors": metadata_errors,
        "reference_errors": reference_errors,
        "manifest_reference_errors": manifest_reference_errors,
        "control_identity_errors": control_identity_errors,
        "plan_errors": dict(plan_errors),
        "flag_errors": flag_errors,
        "owner_count_errors": owner_count_errors,
        "invalid_turns": invalid_turns,
        "invalid_direct_commands": direct_failures,
        "attribution_cell_mismatches": attribution_mismatches,
        "train_successes": train_successes,
        "branches_above_three_workers": above_three,
        "inconsistent_delta_rows": delta_errors,
        "failed_control_identity_rows": failed_identity_rows,
        "competitive_target_roots": competitive_roots,
        "opponent_fell_roots": opponent_fell_roots,
        "opponent_renew_or_harvest_roots": opponent_renew_roots,
        "repeat_rows_verified": repeat_rows_verified,
        "repeat_manifests_verified": repeat_manifests_verified,
        "scale_gate": scale_gate,
        "support_gate": support_gate,
        "structural_complete": structural_complete,
        "manifest_complete": manifest_report["complete"],
    }
    integrity["complete"] = (
        structural_complete
        and manifest_report["complete"]
        and repeat_rows_verified
        and repeat_manifests_verified
        and scale_gate
        and support_gate
    )
    return integrity, dict(grouped)


def oracle_order(row: dict) -> tuple:
    return (
        -row["margin"],
        0 if row["option"] == 0 else 1,
        row["overridden_actions"],
        row["plan_key"],
    )


def select_oracle(rows: list[dict]) -> dict:
    return min(rows, key=oracle_order)


def tail_summary(margins: list[int]) -> dict:
    return {
        "n": len(margins),
        "catastrophes": sum(value <= -100 for value in margins),
        "catastrophe_frequency": sum(value <= -100 for value in margins)
        / len(margins),
        "negative_margin_mass": negative_mass(margins),
    }


def oracle_metrics(rows: list[dict]) -> dict:
    return {
        "margin_gain_vs_farm": clustered_summary(rows, "margin_delta_farm"),
        "own_score_delta_vs_farm": clustered_summary(
            rows, "own_score_delta_farm"
        ),
        "opponent_score_delta_vs_farm": clustered_summary(
            rows, "opponent_score_delta_farm"
        ),
        "own_score_delta_vs_resident": clustered_summary(
            rows, "own_score_delta_resident"
        ),
        "opponent_score_delta_vs_resident": clustered_summary(
            rows, "opponent_score_delta_resident"
        ),
        "absolute_margin": clustered_summary(rows, "margin"),
        "absolute_own_score": clustered_summary(rows, "own_score"),
        "absolute_opponent_score": clustered_summary(rows, "opponent_score"),
    }


def analyze_oracles(grouped: dict) -> dict:
    controls = []
    generic = []
    enriched = []
    increments = []
    for key, branches in sorted(grouped.items()):
        control = next(row for row in branches if row["option"] == 0)
        generic_choice = select_oracle(
            [control, *(row for row in branches if row["catalog"] == "generic")]
        )
        enriched_choice = select_oracle(branches)
        controls.append(control)
        generic.append(generic_choice)
        enriched.append(enriched_choice)
        increments.append(
            {
                "seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "checkpoint": key[3],
                "margin_delta": enriched_choice["margin"] - generic_choice["margin"],
                "own_score_delta": enriched_choice["own_score"]
                - generic_choice["own_score"],
                "opponent_score_delta": enriched_choice["opponent_score"]
                - generic_choice["opponent_score"],
            }
        )
    selected_competitive = [
        row for row in enriched if row["catalog"] == "competitive"
    ]
    opponent_means = {
        opponent: statistics.mean(
            row["margin_delta_farm"]
            for row in enriched
            if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    comp_role_counts = Counter(row["role_tuple"] for row in selected_competitive)
    comp_owner_counts = Counter(row["target_owners"] for row in selected_competitive)
    selected_families = sorted({row["opponent"] for row in selected_competitive})
    exclusive_opponent_targets = sum(
        row["opponent_target_count"] for row in selected_competitive
    )
    farm_tail = tail_summary([row["farm_margin"] for row in controls])
    generic_tail = tail_summary([row["margin"] for row in generic])
    enriched_tail = tail_summary([row["margin"] for row in enriched])
    generic_metrics = oracle_metrics(generic)
    enriched_metrics = oracle_metrics(enriched)
    incremental = {
        "margin": clustered_summary(increments, "margin_delta"),
        "own_score": clustered_summary(increments, "own_score_delta"),
        "opponent_score": clustered_summary(increments, "opponent_score_delta"),
    }
    gates = {
        "competitive_selected_at_least_15pct": len(selected_competitive)
        / len(enriched)
        >= 0.15,
        "competitive_selected_at_least_40_roots": len(selected_competitive) >= 40,
        "enriched_margin_gain_at_least_20": enriched_metrics[
            "margin_gain_vs_farm"
        ]["mean"]
        >= 20,
        "enriched_own_score_delta_at_least_minus_20": enriched_metrics[
            "own_score_delta_vs_farm"
        ]["mean"]
        >= -20,
        "enriched_opponent_score_delta_at_most_minus_20": enriched_metrics[
            "opponent_score_delta_vs_farm"
        ]["mean"]
        <= -20,
        "enriched_own_advantage_vs_resident_at_least_68": enriched_metrics[
            "own_score_delta_vs_resident"
        ]["mean"]
        >= 68,
        "enriched_opponent_excess_vs_resident_at_most_65": enriched_metrics[
            "opponent_score_delta_vs_resident"
        ]["mean"]
        <= 65,
        "incremental_opponent_score_at_most_minus_10": incremental[
            "opponent_score"
        ]["mean"]
        <= -10,
        "incremental_margin_nonnegative": incremental["margin"]["mean"] >= 0,
        "all_opponent_margin_means_nonnegative": all(
            value >= 0 for value in opponent_means.values()
        ),
        "six_opponent_margin_means_at_least_10": sum(
            value >= 10 for value in opponent_means.values()
        )
        >= 6,
        "competitive_selection_spans_four_opponents": len(selected_families) >= 4,
        "competitive_selection_spans_two_roles": len(comp_role_counts) >= 2,
        "at_least_10_exclusive_opponent_targets_selected": exclusive_opponent_targets
        >= 10,
        "catastrophe_frequency_not_above_farm_or_generic": enriched_tail[
            "catastrophe_frequency"
        ]
        <= min(
            farm_tail["catastrophe_frequency"],
            generic_tail["catastrophe_frequency"],
        ),
        "negative_mass_not_above_farm_or_generic": enriched_tail[
            "negative_margin_mass"
        ]
        <= min(
            farm_tail["negative_margin_mass"],
            generic_tail["negative_margin_mass"],
        ),
    }
    return {
        "roots": len(enriched),
        "generic": generic_metrics,
        "enriched": enriched_metrics,
        "incremental_enriched_vs_generic": incremental,
        "competitive_selected_roots": len(selected_competitive),
        "competitive_selected_fraction": len(selected_competitive) / len(enriched),
        "competitive_selected_opponent_families": selected_families,
        "competitive_selected_role_counts": dict(sorted(comp_role_counts.items())),
        "competitive_selected_owner_tuple_counts": dict(
            sorted(comp_owner_counts.items())
        ),
        "exclusive_opponent_targets_selected": exclusive_opponent_targets,
        "ambiguous_targets_selected": sum(
            row["ambiguous_target_count"] for row in selected_competitive
        ),
        "opponent_mean_enriched_margin_gains": opponent_means,
        "opponents_at_least_10": sum(
            value >= 10 for value in opponent_means.values()
        ),
        "tail": {
            "catastrophe_threshold": -100,
            "farm": farm_tail,
            "generic": generic_tail,
            "enriched": enriched_tail,
        },
        "gates": gates,
        "passes_all_gates": all(gates.values()),
        "selections": [
            {
                "seed": row["seed"],
                "seat": row["seat"],
                "opponent": row["opponent"],
                "checkpoint": row["checkpoint"],
                "catalog": row["catalog"],
                "plan_key": row["plan_key"],
                "role_tuple": row["role_tuple"],
                "target_owners": row["target_owners"],
                "margin_delta_farm": row["margin_delta_farm"],
                "own_score_delta_farm": row["own_score_delta_farm"],
                "opponent_score_delta_farm": row["opponent_score_delta_farm"],
            }
            for row in enriched
        ],
    }


def analyze(
    rows: list[dict],
    manifest_rows: list[dict],
    expected_seeds: tuple[int, ...] = DEFAULT_SEEDS,
    repeat_rows_verified: bool = True,
    repeat_manifests_verified: bool = True,
) -> dict:
    manifest_report, expected_roots, references = validate_manifest(
        manifest_rows, expected_seeds
    )
    integrity, grouped = validate_rows(
        rows,
        expected_roots,
        manifest_report,
        references,
        repeat_rows_verified,
        repeat_manifests_verified,
    )
    report = {
        "protocol": "D35c provenance-aware competitive-bundle oracle",
        "expected_seeds": list(expected_seeds),
        "manifest": manifest_report,
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
    oracles = analyze_oracles(grouped)
    report.update(
        {
            "oracles": oracles,
            "confirmation_authorized": oracles["passes_all_gates"],
            "decision": (
                "open_sealed_confirmation"
                if oracles["passes_all_gates"]
                else "reject_provenance_extension_advance_repeated_control"
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
        default=[
            base / "d35c-development-9300000-9300009.tsv",
            base / "d35c-development-9300040-9300049.tsv",
        ],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=base / "d35c-provenance-competitive-development-2026-07-20.json",
    )
    parser.add_argument(
        "--integrity-repeat-a",
        type=Path,
        default=base / "d35c-integrity-repeat-a-9300000.tsv",
    )
    parser.add_argument(
        "--integrity-repeat-b",
        type=Path,
        default=base / "d35c-integrity-repeat-b-9300000.tsv",
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
                "competitive_selected_fraction": report.get("oracles", {}).get(
                    "competitive_selected_fraction"
                ),
                "enriched_margin_gain": report.get("oracles", {})
                .get("enriched", {})
                .get("margin_gain_vs_farm", {})
                .get("mean"),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
