#!/usr/bin/env python3
"""Validate and analyze D162's bounded resident-native capital-option pilot."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
from typing import Iterable, Mapping

from cgauto import analyze_d112a_dense_q6_counterfactual_teacher as d112


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d162a-resident-native-capital-option-protocol-2026-07-23.md"
LOCK = BASE / "d162a-resident-native-capital-option-lock.json"
D161 = BASE / "d161a-resident-d40-panel-jobs20-9844136-9844199.tsv"
RUN_A = BASE / "d162a-resident-native-capital-option-jobs1-9844136-9844143.tsv"
RUN_B = BASE / "d162a-resident-native-capital-option-jobs20-9844136-9844143.tsv"
RUNNER = ROOT / "rust" / "src" / "bin" / "d162_resident_native_capital_option.rs"
OUTPUT = BASE / "d162a-resident-native-capital-option-result.json"

START_SEED = 9_844_136
MAP_COUNT = 8
RESERVED_START_SEED = 9_844_200
OPPONENTS = tuple(d112.OPPONENTS)
RUNNER_OPPONENTS = (
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
    "script_boss",
    "silver_boss",
)
MARKS = (72, 104, 136)
SPECS = (
    ("minimal_1101", (1, 1, 0, 1)),
    ("balanced_2202", (2, 2, 0, 2)),
)
HORIZONS = (32, 64)


def catalog() -> list[dict]:
    policies = [
        {
            "index": 0,
            "label": "resident",
            "stats": (-1, -1, -1, -1),
            "start": -1,
            "horizon": 0,
        }
    ]
    for name, stats in SPECS:
        for start in MARKS:
            for horizon in HORIZONS:
                policies.append(
                    {
                        "index": len(policies),
                        "label": f"{name}_t{start:03}_h{horizon:03}",
                        "stats": stats,
                        "start": start,
                        "horizon": horizon,
                    }
                )
    return policies


INT_FIELDS = (
    "map_seed",
    "seat",
    "opponent_index",
    "policy_index",
    "option_ms",
    "option_cc",
    "option_hp",
    "option_chop",
    "option_start",
    "option_horizon",
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
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
    "prefix72_captured",
    "prefix72_action_hash",
    "prefix72_state_hash",
    "prefix104_captured",
    "prefix104_action_hash",
    "prefix104_state_hash",
    "prefix136_captured",
    "prefix136_action_hash",
    "prefix136_state_hash",
    "activated",
    "activation_turn",
    "deadline",
    "active_turns",
    "committed",
    "aborted",
    "option_overrides",
    "protected_commands",
    "move_commands",
    "bank_commands",
    "harvest_commands",
    "mine_commands",
    "train_attempts",
    "train_successes",
    "trained_turn",
    "initial_bank_deficit",
    "closest_bank_deficit",
    "option_command_failures",
    "affordability_violations",
    "transaction_failures",
    "worker_cap_violations",
    "horizon_violations",
    "restart_violations",
)
FLOAT_FIELDS = (
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
)
EXPECTED_FIELDS = (
    "map_seed",
    "seat",
    "opponent_index",
    "opponent",
    "policy_index",
    "policy",
    "option_ms",
    "option_cc",
    "option_hp",
    "option_chop",
    "option_start",
    "option_horizon",
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
    "prefix72_captured",
    "prefix72_action_hash",
    "prefix72_state_hash",
    "prefix104_captured",
    "prefix104_action_hash",
    "prefix104_state_hash",
    "prefix136_captured",
    "prefix136_action_hash",
    "prefix136_state_hash",
    "activated",
    "activation_turn",
    "deadline",
    "active_turns",
    "committed",
    "aborted",
    "option_overrides",
    "protected_commands",
    "move_commands",
    "bank_commands",
    "harvest_commands",
    "mine_commands",
    "train_attempts",
    "train_successes",
    "trained_turn",
    "initial_bank_deficit",
    "closest_bank_deficit",
    "option_command_failures",
    "affordability_violations",
    "transaction_failures",
    "worker_cap_violations",
    "horizon_violations",
    "restart_violations",
)

PARITY_INT_FIELDS = (
    "done",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
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
PARITY_FLOAT_FIELDS = ("own_return", "opponent_return", "margin_return")
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "ambiguous_created_crops",
    "option_command_failures",
    "affordability_violations",
    "transaction_failures",
    "worker_cap_violations",
    "horizon_violations",
    "restart_violations",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return statistics.fmean(values) if values else 0.0


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


def read_rows(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = list(reader.fieldnames or ())
    for row in rows:
        for field in INT_FIELDS:
            row[field] = int(row[field])
        for field in FLOAT_FIELDS:
            row[field] = float(row[field])
    return rows, fields


def verify_lock() -> dict:
    payload = json.loads(LOCK.read_text())
    mismatches = {}
    for relative, expected in payload["sha256"].items():
        path = ROOT / relative
        actual = sha256(path) if path.exists() else None
        if actual != expected:
            mismatches[relative] = {"expected": expected, "actual": actual}
    return {
        "path": str(LOCK.relative_to(ROOT)),
        "sha256": sha256(LOCK),
        "declared": payload,
        "mismatches": mismatches,
        "pass": not mismatches,
    }


def validate_grid(rows: list[dict], fields: list[str]) -> tuple[dict, dict]:
    policies = catalog()
    labels = [policy["label"] for policy in policies]
    expected = {
        (*key, label) for key in expected_tasks() for label in labels
    }
    keys = [row_key(row) for row in rows]
    indexed = {row_key(row): row for row in rows}
    catalog_errors = 0
    opponent_errors = 0
    for row in rows:
        index = row["policy_index"]
        if not 0 <= index < len(policies):
            catalog_errors += 1
            continue
        policy = policies[index]
        catalog_errors += int(
            row["policy"] != policy["label"]
            or tuple(row[field] for field in ("option_ms", "option_cc", "option_hp", "option_chop"))
            != policy["stats"]
            or row["option_start"] != policy["start"]
            or row["option_horizon"] != policy["horizon"]
        )
        opponent_errors += int(
            not 0 <= row["opponent_index"] < len(RUNNER_OPPONENTS)
            or RUNNER_OPPONENTS[row["opponent_index"]] != row["opponent"]
        )
    reward_errors = sum(
        row["margin"] != row["own_score"] - row["opponent_score"]
        or max(
            abs(row["own_return"] - row["own_score"] / 100.0),
            abs(row["opponent_return"] - row["opponent_score"] / 100.0),
            abs(row["margin_return"] - row["margin"] / 100.0),
            abs(row["reward_identity_error"]),
        )
        > 1e-6
        for row in rows
    )
    summary = {
        "rows": len(rows),
        "expected_rows": len(expected),
        "columns": len(fields),
        "schema_exact": fields == list(EXPECTED_FIELDS),
        "unique_keys": len(indexed),
        "duplicate_rows": len(keys) - len(set(keys)),
        "missing_rows": len(expected - set(keys)),
        "unexpected_rows": len(set(keys) - expected),
        "catalog_errors": catalog_errors,
        "opponent_index_errors": opponent_errors,
        "unfinished_rows": sum(not row["done"] for row in rows),
        "reward_identity_errors": reward_errors,
    }
    summary["pass"] = (
        summary["schema_exact"]
        and len(rows) == len(expected)
        and set(keys) == expected
        and len(keys) == len(set(keys))
        and not catalog_errors
        and not opponent_errors
        and not summary["unfinished_rows"]
        and not reward_errors
    )
    return summary, indexed


def resident_parity(indexed: Mapping[tuple, dict]) -> dict:
    with D161.open(newline="") as source:
        d161_rows = list(csv.DictReader(source, delimiter="\t"))
    expected = expected_tasks()
    reference = {
        task(row): row
        for row in d161_rows
        if row["policy"] == "resident" and task(row) in expected
    }
    mismatches = Counter()
    samples = []
    for key in sorted(expected):
        current = indexed.get((*key, "resident"))
        prior = reference.get(key)
        if current is None or prior is None:
            mismatches["missing_task"] += 1
            continue
        for field in PARITY_INT_FIELDS:
            if int(current[field]) != int(prior[field]):
                mismatches[field] += 1
                if len(samples) < 10:
                    samples.append(
                        {"task": key, "field": field, "d162": current[field], "d161": prior[field]}
                    )
        for field in PARITY_FLOAT_FIELDS:
            if not math.isclose(
                float(current[field]), float(prior[field]), rel_tol=0.0, abs_tol=1e-7
            ):
                mismatches[field] += 1
                if len(samples) < 10:
                    samples.append(
                        {"task": key, "field": field, "d162": current[field], "d161": prior[field]}
                    )
    return {
        "tasks": len(reference),
        "mismatches": dict(sorted(mismatches.items())),
        "samples": samples,
        "pass": len(reference) == len(expected) and not mismatches,
    }


def mechanics(rows: list[dict], indexed: Mapping[tuple, dict]) -> dict:
    arms = [policy for policy in catalog() if policy["index"]]
    arm_rows = {policy["label"]: [] for policy in arms}
    for row in rows:
        if row["policy"] != "resident":
            arm_rows[row["policy"]].append(row)
    failures = {
        field: sum(row[field] for row in rows) for field in FAILURE_FIELDS
    }
    prefix_errors = 0
    prefix_samples = []
    lifecycle_errors = 0
    terminal_before_option_close = 0
    for policy in arms:
        mark = policy["start"]
        for row in arm_rows[policy["label"]]:
            control = indexed[(*task(row), "resident")]
            captured = row[f"prefix{mark}_captured"] == control[f"prefix{mark}_captured"] == 1
            exact = (
                row[f"prefix{mark}_action_hash"] == control[f"prefix{mark}_action_hash"]
                and row[f"prefix{mark}_state_hash"] == control[f"prefix{mark}_state_hash"]
            )
            if not captured or not exact:
                prefix_errors += 1
                if len(prefix_samples) < 10:
                    prefix_samples.append(
                        {"task": task(row), "policy": row["policy"], "captured": captured, "exact": exact}
                    )
            activated = bool(row["activated"])
            trained = row["train_successes"] == 1
            terminal_before_option_close += int(
                activated and not trained and not bool(row["aborted"])
            )
            lifecycle_errors += int(
                (activated and row["activation_turn"] != policy["start"])
                or (activated and row["deadline"] != policy["start"] + policy["horizon"])
                or row["active_turns"] > policy["horizon"]
                or row["train_attempts"] != row["train_successes"]
                or bool(row["committed"]) != trained
                or (trained and row["max_own_workers"] != 3)
                or (bool(row["aborted"]) and trained)
            )

    arm_summaries = {}
    successful_seats = set()
    successful_families = set()
    for policy in arms:
        policy_rows = arm_rows[policy["label"]]
        successes = [row for row in policy_rows if row["train_successes"]]
        successful_seats.update(row["seat"] for row in successes)
        successful_families.update(row["opponent"] for row in successes)
        arm_summaries[policy["label"]] = {
            "tasks": len(policy_rows),
            "activation_tasks": sum(row["activated"] for row in policy_rows),
            "activation_rate": mean(row["activated"] for row in policy_rows),
            "action_distinct_tasks": sum(
                row["action_hash"] != indexed[(*task(row), "resident")]["action_hash"]
                for row in policy_rows
            ),
            "mean_active_turns": mean(row["active_turns"] for row in policy_rows),
            "mean_initial_bank_deficit": mean(
                row["initial_bank_deficit"] for row in policy_rows if row["activated"]
            ),
            "mean_closest_bank_deficit": mean(
                row["closest_bank_deficit"] for row in policy_rows if row["activated"]
            ),
            "minimum_closest_bank_deficit": min(
                (row["closest_bank_deficit"] for row in policy_rows if row["activated"]),
                default=None,
            ),
            "train_success_tasks": len(successes),
            "train_success_rate": len(successes) / len(policy_rows),
            "mean_option_overrides": mean(row["option_overrides"] for row in policy_rows),
            "mean_protected_commands": mean(row["protected_commands"] for row in policy_rows),
        }
    active_arms = sum(view["activation_rate"] >= 0.90 for view in arm_summaries.values())
    training_arms = sum(view["train_success_rate"] >= 0.10 for view in arm_summaries.values())
    gates = {
        "zero_mechanical_failures": not any(failures.values()),
        "all_preactivation_prefixes_exact": not prefix_errors,
        "all_option_lifecycles_exact": not lifecycle_errors,
        "at_least_ten_arms_activate_90pct": active_arms >= 10,
        "at_least_four_arms_train_10pct": training_arms >= 4,
        "successful_training_both_seats": successful_seats == {0, 1},
        "successful_training_at_least_six_families": len(successful_families) >= 6,
        "no_task_exceeds_three_workers": max(row["max_own_workers"] for row in rows) <= 3,
    }
    return {
        "failures": failures,
        "prefix_errors": prefix_errors,
        "prefix_error_samples": prefix_samples,
        "lifecycle_errors": lifecycle_errors,
        "terminal_before_option_close_rows": terminal_before_option_close,
        "arms_activating_at_least_90pct": active_arms,
        "arms_training_at_least_10pct": training_arms,
        "successful_training_seats": sorted(successful_seats),
        "successful_training_families": sorted(successful_families),
        "arms": arm_summaries,
        "gates": gates,
        "pass": all(gates.values()),
    }


def outcome_margin(row: Mapping[str, object]) -> int:
    return int(row["own_score"]) - int(row["opponent_score"])


def select_envelope(indexed: Mapping[tuple, dict]) -> tuple[dict, dict]:
    selected = {}
    selection_counts = Counter()
    ineligible_crop_rows = 0
    for key in sorted(expected_tasks()):
        resident = indexed[(*key, "resident")]
        best = resident
        for policy in catalog()[1:]:
            candidate = indexed[(*key, policy["label"])]
            crop_safe = not (
                resident["own_created_crops"] > 0 and candidate["own_created_crops"] == 0
            )
            if not crop_safe:
                ineligible_crop_rows += 1
                continue
            if outcome_margin(candidate) > outcome_margin(best):
                best = candidate
        selected[key] = best
        selection_counts[best["policy"]] += 1
    return selected, {
        "selection_counts": dict(sorted(selection_counts.items())),
        "ineligible_crop_rows": ineligible_crop_rows,
    }


def tail(rows: Iterable[Mapping[str, object]]) -> dict:
    margins = [outcome_margin(row) for row in rows]
    return {
        "catastrophe_count": sum(value <= -100 for value in margins),
        "negative_margin_mass": sum(max(-value, 0) for value in margins),
    }


def capacity_metrics(indexed: Mapping[tuple, dict]) -> dict:
    selected, selection = select_envelope(indexed)
    residents = {key: indexed[(*key, "resident")] for key in expected_tasks()}
    deltas = []
    by_map = defaultdict(list)
    by_family = defaultdict(list)
    by_seat = defaultdict(list)
    by_block = defaultdict(list)
    for key in sorted(expected_tasks()):
        resident = residents[key]
        candidate = selected[key]
        row = {
            "margin": outcome_margin(candidate) - outcome_margin(resident),
            "own": candidate["own_score"] - resident["own_score"],
            "opponent": candidate["opponent_score"] - resident["opponent_score"],
        }
        deltas.append(row)
        by_map[key[0]].append(row)
        by_family[key[2]].append(row)
        by_seat[key[1]].append(row)
        by_block[(key[0] - START_SEED) // 2].append(row)
    map_means = [mean(row["margin"] for row in group) for _, group in sorted(by_map.items())]
    map_sd = statistics.stdev(map_means)
    half_width = 1.96 * map_sd / math.sqrt(len(map_means))
    family_means = {
        opponent: mean(row["margin"] for row in by_family[opponent])
        for opponent in OPPONENTS
    }
    seat_means = {
        str(seat): mean(row["margin"] for row in by_seat[seat]) for seat in range(2)
    }
    block_means = {
        str(block): mean(row["margin"] for row in by_block[block]) for block in range(4)
    }
    resident_tail = tail(residents.values())
    selected_tail = tail(selected.values())
    resident_crop_rate = mean(row["own_created_crops"] > 0 for row in residents.values())
    selected_crop_rate = mean(row["own_created_crops"] > 0 for row in selected.values())
    individual_arms = {}
    for policy in catalog()[1:]:
        policy_rows = [indexed[(*key, policy["label"])] for key in sorted(expected_tasks())]
        arm_deltas = [
            outcome_margin(row) - outcome_margin(residents[task(row)]) for row in policy_rows
        ]
        individual_arms[policy["label"]] = {
            "mean_margin_delta": mean(arm_deltas),
            "strict_wins": sum(value > 0 for value in arm_deltas),
            "ties": sum(value == 0 for value in arm_deltas),
            "regressions": sum(value < 0 for value in arm_deltas),
        }
    delta = {
        "tasks": len(deltas),
        "mean_margin_delta": mean(row["margin"] for row in deltas),
        "median_margin_delta": statistics.median(row["margin"] for row in deltas),
        "mean_own_score_delta": mean(row["own"] for row in deltas),
        "mean_opponent_score_delta": mean(row["opponent"] for row in deltas),
        "strict_improvement_tasks": sum(row["margin"] > 0 for row in deltas),
        "strict_improvement_rate": mean(row["margin"] > 0 for row in deltas),
        "tie_tasks": sum(row["margin"] == 0 for row in deltas),
        "strict_regression_tasks": sum(row["margin"] < 0 for row in deltas),
        "map_clustered_normal_95pct_interval": [
            mean(map_means) - half_width,
            mean(map_means) + half_width,
        ],
        "map_mean_delta_sd": map_sd,
    }
    summary = {
        "selection": selection,
        "delta": delta,
        "family_mean_margin_deltas": family_means,
        "positive_families": sum(value > 0 for value in family_means.values()),
        "worst_family_mean_margin_delta": min(family_means.values()),
        "seat_mean_margin_deltas": seat_means,
        "block_mean_margin_deltas": block_means,
        "positive_blocks": sum(value > 0 for value in block_means.values()),
        "resident_crop_creation_rate": resident_crop_rate,
        "selected_crop_creation_rate": selected_crop_rate,
        "selected_worker_three_rate": mean(
            row["max_own_workers"] >= 3 for row in selected.values()
        ),
        "resident_tail": resident_tail,
        "selected_tail": selected_tail,
        "individual_arms": individual_arms,
        "arms_with_at_least_four_strict_wins": sum(
            view["strict_wins"] >= 4 for view in individual_arms.values()
        ),
    }
    gates = {
        "mean_margin_gain_at_least_8": delta["mean_margin_delta"] >= 8.0,
        "strict_improvement_rate_at_least_25pct": delta["strict_improvement_rate"] >= 0.25,
        "map_clustered_95pct_lower_bound_above_zero": delta[
            "map_clustered_normal_95pct_interval"
        ][0]
        > 0.0,
        "at_least_six_positive_families": summary["positive_families"] >= 6,
        "all_family_means_nonnegative": summary["worst_family_mean_margin_delta"] >= 0.0,
        "both_seats_positive": all(value > 0 for value in seat_means.values()),
        "at_least_three_positive_blocks": summary["positive_blocks"] >= 3,
        "own_nonnegative_or_opponent_nonpositive": (
            delta["mean_own_score_delta"] >= 0.0
            or delta["mean_opponent_score_delta"] <= 0.0
        ),
        "crop_creation_within_2pp": selected_crop_rate >= resident_crop_rate - 0.02,
        "catastrophe_count_not_increased": selected_tail["catastrophe_count"]
        <= resident_tail["catastrophe_count"],
        "negative_margin_mass_not_increased": selected_tail["negative_margin_mass"]
        <= resident_tail["negative_margin_mass"],
        "selected_worker_three_rate_at_least_10pct": summary["selected_worker_three_rate"]
        >= 0.10,
        "at_least_four_arms_have_four_strict_wins": summary[
            "arms_with_at_least_four_strict_wins"
        ]
        >= 4,
    }
    summary["gates"] = gates
    summary["pass"] = all(gates.values())
    return summary


def analyze(run_a: Path, run_b: Path) -> dict:
    lock = verify_lock()
    repeated_exact = run_a.read_bytes() == run_b.read_bytes()
    rows_a, fields_a = read_rows(run_a)
    rows_b, fields_b = read_rows(run_b)
    grid_a, index_a = validate_grid(rows_a, fields_a)
    grid_b, _ = validate_grid(rows_b, fields_b)
    parity = resident_parity(index_a)
    mechanism = mechanics(rows_a, index_a)
    capacity = capacity_metrics(index_a)
    integrity_gates = {
        "frozen_lock_matches": lock["pass"],
        "jobs1_and_jobs20_byte_identical": repeated_exact,
        "jobs1_grid_exact": grid_a["pass"],
        "jobs20_grid_exact": grid_b["pass"],
        "resident_reproduces_d161": parity["pass"],
        "reserved_maps_excluded": START_SEED + MAP_COUNT <= RESERVED_START_SEED,
    }
    integrity_pass = all(integrity_gates.values())
    full_pass = integrity_pass and mechanism["pass"] and capacity["pass"]
    decision = (
        "repair_d162_measurement_before_interpretation"
        if not integrity_pass
        else "close_exact_one_lane_reserve_interface_on_mechanics"
        if not mechanism["pass"]
        else "open_d162b_remaining_consumed_map_expansion"
        if capacity["pass"]
        else "close_exact_one_lane_reserve_interface_on_resident_relative_capacity"
    )
    return {
        "schema": "troll-farm-d162a-resident-native-capital-option-v1",
        "protocol": str(PROTOCOL.relative_to(ROOT)),
        "canonical_yt_root": "//home/delivery_ml/research/tarstars/troll_farm",
        "panel": {
            "start_seed": START_SEED,
            "maps": MAP_COUNT,
            "tasks": len(expected_tasks()),
            "policies": len(catalog()),
            "rows_per_run": len(expected_tasks()) * len(catalog()),
            "platform_requests": 0,
            "yt_requests": 0,
        },
        "lock": lock,
        "inputs": {
            "jobs1": {"path": str(run_a), "sha256": sha256(run_a)},
            "jobs20": {"path": str(run_b), "sha256": sha256(run_b)},
            "runner": {"path": str(RUNNER.relative_to(ROOT)), "sha256": sha256(RUNNER)},
        },
        "catalog": catalog(),
        "runner_validation": {"jobs1": grid_a, "jobs20": grid_b},
        "resident_parity": parity,
        "integrity": {"gates": integrity_gates, "pass": integrity_pass},
        "mechanism": mechanism,
        "capacity": capacity,
        "pass": full_pass,
        "decision": decision,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-a", type=Path, default=RUN_A)
    parser.add_argument("--run-b", type=Path, default=RUN_B)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = analyze(args.run_a, args.run_b)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
