#!/usr/bin/env python3
"""Validate and analyze D163's resident-native resource-control factorial."""

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
ARTIFACT_BASE = (
    ROOT / "artifacts" / "experiments" / "d163a-resource-control-components"
)
PROTOCOL = (
    BASE / "d163a-resident-resource-control-components-protocol-2026-07-23.md"
)
LOCK = BASE / "d163a-resident-resource-control-components-lock.json"
D161 = BASE / "d161a-resident-d40-panel-jobs20-9844136-9844199.tsv"
RUN_A = ARTIFACT_BASE / "d163a-resource-control-components-jobs1-9844144-9844151.tsv"
RUN_B = ARTIFACT_BASE / "d163a-resource-control-components-jobs20-9844144-9844151.tsv"
RUNNER = ROOT / "rust" / "src" / "bin" / "d163_resident_resource_control_components.rs"
BUILD_SCRIPT = ROOT / "rust" / "build.rs"
OUTPUT = BASE / "d163a-resident-resource-control-components-result.json"

START_SEED = 9_844_144
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
HORIZON = 32
COMPONENTS = {
    "fruit": 1,
    "iron": 2,
    "protection": 4,
}
MASK_LABELS = {
    1: "fruit",
    2: "iron",
    3: "fruit_iron",
    4: "protection",
    5: "fruit_protection",
    6: "iron_protection",
    7: "fruit_iron_protection",
}


def catalog() -> list[dict]:
    policies = [
        {
            "index": 0,
            "label": "resident",
            "mask": 0,
            "fruit": 0,
            "iron": 0,
            "protection": 0,
            "start": -1,
            "horizon": 0,
        }
    ]
    for start in MARKS:
        for mask in range(1, 8):
            policies.append(
                {
                    "index": len(policies),
                    "label": f"{MASK_LABELS[mask]}_t{start:03}_h032",
                    "mask": mask,
                    "fruit": int(bool(mask & COMPONENTS["fruit"])),
                    "iron": int(bool(mask & COMPONENTS["iron"])),
                    "protection": int(bool(mask & COMPONENTS["protection"])),
                    "start": start,
                    "horizon": HORIZON,
                }
            )
    return policies


EXPECTED_FIELDS = (
    "map_seed",
    "seat",
    "opponent_index",
    "opponent",
    "policy_index",
    "policy",
    "component_mask",
    "fruit_routing",
    "iron_routing",
    "protection",
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
    "aborted",
    "option_overrides",
    "fruit_overrides",
    "iron_overrides",
    "protected_commands",
    "move_commands",
    "bank_commands",
    "fruit_bank_commands",
    "iron_bank_commands",
    "harvest_commands",
    "mine_commands",
    "resident_train_commands",
    "controller_train_commands",
    "suppressed_train_commands",
    "initial_bank_deficit",
    "closest_bank_deficit",
    "option_command_failures",
    "workforce_exit_events",
    "horizon_violations",
    "restart_violations",
)
FLOAT_FIELDS = (
    "own_return",
    "opponent_return",
    "margin_return",
    "reward_identity_error",
)
INT_FIELDS = tuple(field for field in EXPECTED_FIELDS if field not in FLOAT_FIELDS and field not in ("opponent", "policy"))

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
    "horizon_violations",
    "restart_violations",
)
WORKFORCE_FIELDS = ("successful_trains", "own_workers", "max_own_workers")


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


def label_for(start: int, mask: int) -> str:
    if mask == 0:
        return "resident"
    return f"{MASK_LABELS[mask]}_t{start:03}_h032"


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
    expected = {
        (*key, policy["label"])
        for key in expected_tasks()
        for policy in policies
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
            or row["component_mask"] != policy["mask"]
            or row["fruit_routing"] != policy["fruit"]
            or row["iron_routing"] != policy["iron"]
            or row["protection"] != policy["protection"]
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
                        {
                            "task": key,
                            "field": field,
                            "d163": current[field],
                            "d161": prior[field],
                        }
                    )
        for field in PARITY_FLOAT_FIELDS:
            if not math.isclose(
                float(current[field]),
                float(prior[field]),
                rel_tol=0.0,
                abs_tol=1e-7,
            ):
                mismatches[field] += 1
                if len(samples) < 10:
                    samples.append(
                        {
                            "task": key,
                            "field": field,
                            "d163": current[field],
                            "d161": prior[field],
                        }
                    )
    return {
        "tasks": len(reference),
        "mismatches": dict(sorted(mismatches.items())),
        "samples": samples,
        "pass": len(reference) == len(expected) and not mismatches,
    }


def mechanics(rows: list[dict], indexed: Mapping[tuple, dict]) -> dict:
    arms = catalog()[1:]
    arm_rows = {
        policy["label"]: [
            indexed[(*key, policy["label"])] for key in sorted(expected_tasks())
        ]
        for policy in arms
    }
    failures = {
        field: sum(row[field] for row in rows) for field in FAILURE_FIELDS
    }
    prefix_errors = 0
    lifecycle_errors = 0
    workforce_mismatches = Counter()
    purity_errors = Counter()
    terminal_before_close = 0
    arm_summaries = {}
    component_exercise_rows = Counter()
    component_enabled_rows = Counter()

    for policy in arms:
        policy_rows = arm_rows[policy["label"]]
        start = policy["start"]
        for row in policy_rows:
            resident = indexed[(*task(row), "resident")]
            prefix_errors += int(
                row[f"prefix{start}_captured"] != 1
                or resident[f"prefix{start}_captured"] != 1
                or row[f"prefix{start}_action_hash"]
                != resident[f"prefix{start}_action_hash"]
                or row[f"prefix{start}_state_hash"]
                != resident[f"prefix{start}_state_hash"]
            )
            activated = bool(row["activated"])
            terminal_before_close += int(activated and not bool(row["aborted"]))
            lifecycle_errors += int(
                (activated and row["activation_turn"] != start)
                or (activated and row["deadline"] != start + HORIZON)
                or row["active_turns"] > HORIZON
            )
            for field in WORKFORCE_FIELDS:
                workforce_mismatches[field] += int(row[field] != resident[field])
            if not policy["fruit"]:
                purity_errors["fruit"] += int(
                    row["fruit_overrides"]
                    or row["fruit_bank_commands"]
                    or row["harvest_commands"]
                )
            if not policy["iron"]:
                purity_errors["iron"] += int(
                    row["iron_overrides"]
                    or row["iron_bank_commands"]
                    or row["mine_commands"]
                )
            if not policy["protection"]:
                purity_errors["protection"] += int(row["protected_commands"] != 0)
            for name, enabled, field in (
                ("fruit", policy["fruit"], "fruit_overrides"),
                ("iron", policy["iron"], "iron_overrides"),
                ("protection", policy["protection"], "protected_commands"),
            ):
                if enabled:
                    component_enabled_rows[name] += 1
                    component_exercise_rows[name] += int(row[field] > 0)

        arm_summaries[policy["label"]] = {
            "tasks": len(policy_rows),
            "activation_tasks": sum(row["activated"] for row in policy_rows),
            "activation_rate": mean(row["activated"] for row in policy_rows),
            "action_distinct_tasks": sum(
                row["action_hash"] != indexed[(*task(row), "resident")]["action_hash"]
                for row in policy_rows
            ),
            "mean_active_turns": mean(row["active_turns"] for row in policy_rows),
            "mean_option_overrides": mean(row["option_overrides"] for row in policy_rows),
            "mean_fruit_overrides": mean(row["fruit_overrides"] for row in policy_rows),
            "mean_iron_overrides": mean(row["iron_overrides"] for row in policy_rows),
            "mean_protected_commands": mean(
                row["protected_commands"] for row in policy_rows
            ),
            "mean_initial_bank_deficit": mean(
                row["initial_bank_deficit"]
                for row in policy_rows
                if row["activated"]
            ),
            "mean_closest_bank_deficit": mean(
                row["closest_bank_deficit"]
                for row in policy_rows
                if row["activated"]
            ),
        }

    exercise_rates = {
        name: component_exercise_rows[name] / component_enabled_rows[name]
        for name in COMPONENTS
    }
    gates = {
        "zero_mechanical_failures": not any(failures.values()),
        "all_preactivation_prefixes_exact": prefix_errors == 0,
        "all_lifecycles_bounded": lifecycle_errors == 0,
        "all_arms_activate_at_least_90pct": all(
            view["activation_rate"] >= 0.90 for view in arm_summaries.values()
        ),
        "controller_never_synthesizes_train": sum(
            row["controller_train_commands"] for row in rows
        )
        == 0,
        "controller_never_suppresses_train": sum(
            row["suppressed_train_commands"] for row in rows
        )
        == 0,
        "workforce_exactly_matches_resident": not any(workforce_mismatches.values()),
        "component_purity_exact": not any(purity_errors.values()),
        "each_component_exercised_at_least_5pct": all(
            rate >= 0.05 for rate in exercise_rates.values()
        ),
    }
    return {
        "failures": failures,
        "prefix_errors": prefix_errors,
        "lifecycle_errors": lifecycle_errors,
        "terminal_before_close_rows": terminal_before_close,
        "workforce_mismatches": dict(sorted(workforce_mismatches.items())),
        "purity_errors": dict(sorted(purity_errors.items())),
        "component_enabled_rows": dict(sorted(component_enabled_rows.items())),
        "component_exercise_rows": dict(sorted(component_exercise_rows.items())),
        "component_exercise_rates": exercise_rates,
        "arms": arm_summaries,
        "gates": gates,
        "pass": all(gates.values()),
    }


def margin(row: Mapping[str, object]) -> int:
    return int(row["own_score"]) - int(row["opponent_score"])


def normal_interval_by_map(observations: Iterable[dict]) -> list[float]:
    by_map = defaultdict(list)
    for observation in observations:
        by_map[observation["map_seed"]].append(observation["margin"])
    map_means = [mean(group) for _, group in sorted(by_map.items())]
    center = mean(map_means)
    if len(map_means) < 2:
        return [center, center]
    half_width = 1.96 * statistics.stdev(map_means) / math.sqrt(len(map_means))
    return [center - half_width, center + half_width]


def tail(rows: Iterable[Mapping[str, object]]) -> dict:
    margins = [margin(row) for row in rows]
    return {
        "catastrophe_count": sum(value <= -100 for value in margins),
        "negative_margin_mass": sum(max(-value, 0) for value in margins),
    }


def paired_observation(
    with_row: Mapping[str, object],
    without_row: Mapping[str, object],
    *,
    start: int,
) -> dict:
    return {
        "map_seed": int(with_row["map_seed"]),
        "seat": int(with_row["seat"]),
        "opponent": str(with_row["opponent"]),
        "start": start,
        "margin": margin(with_row) - margin(without_row),
        "own": int(with_row["own_score"]) - int(without_row["own_score"]),
        "opponent_score": int(with_row["opponent_score"])
        - int(without_row["opponent_score"]),
        "crop": int(int(with_row["own_created_crops"]) > 0)
        - int(int(without_row["own_created_crops"]) > 0),
        "workforce_mismatch": any(
            int(with_row[field]) != int(without_row[field])
            for field in WORKFORCE_FIELDS
        ),
        "with_row": with_row,
        "without_row": without_row,
    }


def summarize_component(
    name: str,
    observations: list[dict],
    exercise_rate: float,
) -> dict:
    by_family = defaultdict(list)
    by_seat = defaultdict(list)
    by_start = defaultdict(list)
    for observation in observations:
        by_family[observation["opponent"]].append(observation["margin"])
        by_seat[observation["seat"]].append(observation["margin"])
        by_start[observation["start"]].append(observation["margin"])
    family_means = {
        opponent: mean(by_family[opponent]) for opponent in OPPONENTS
    }
    seat_means = {str(seat): mean(by_seat[seat]) for seat in range(2)}
    start_means = {str(start): mean(by_start[start]) for start in MARKS}
    with_rows = [observation["with_row"] for observation in observations]
    without_rows = [observation["without_row"] for observation in observations]
    with_tail = tail(with_rows)
    without_tail = tail(without_rows)
    interval = normal_interval_by_map(observations)
    summary = {
        "component": name,
        "paired_observations": len(observations),
        "mean_margin_effect": mean(item["margin"] for item in observations),
        "mean_own_score_effect": mean(item["own"] for item in observations),
        "mean_opponent_score_effect": mean(
            item["opponent_score"] for item in observations
        ),
        "map_clustered_normal_95pct_interval": interval,
        "family_mean_margin_effects": family_means,
        "positive_families": sum(value > 0 for value in family_means.values()),
        "worst_family_mean_effect": min(family_means.values()),
        "seat_mean_margin_effects": seat_means,
        "start_mean_margin_effects": start_means,
        "positive_starts": sum(value > 0 for value in start_means.values()),
        "crop_creation_rate_effect": mean(item["crop"] for item in observations),
        "without_component_tail": without_tail,
        "with_component_tail": with_tail,
        "workforce_pair_mismatches": sum(
            item["workforce_mismatch"] for item in observations
        ),
        "treatment_exercise_rate": exercise_rate,
    }
    gates = {
        "mean_margin_effect_at_least_2": summary["mean_margin_effect"] >= 2.0,
        "map_clustered_95pct_lower_bound_above_zero": interval[0] > 0.0,
        "at_least_six_positive_families": summary["positive_families"] >= 6,
        "worst_family_at_least_minus_4": summary["worst_family_mean_effect"] >= -4.0,
        "both_seats_positive": all(value > 0 for value in seat_means.values()),
        "at_least_two_positive_starts": summary["positive_starts"] >= 2,
        "own_nonnegative_or_opponent_nonpositive": (
            summary["mean_own_score_effect"] >= 0.0
            or summary["mean_opponent_score_effect"] <= 0.0
        ),
        "crop_creation_within_2pp": summary["crop_creation_rate_effect"] >= -0.02,
        "catastrophe_count_not_increased": (
            with_tail["catastrophe_count"] <= without_tail["catastrophe_count"]
        ),
        "negative_margin_mass_not_increased": (
            with_tail["negative_margin_mass"]
            <= without_tail["negative_margin_mass"]
        ),
        "workforce_exact": summary["workforce_pair_mismatches"] == 0,
        "treatment_exercise_rate_at_least_5pct": exercise_rate >= 0.05,
    }
    summary["gates"] = gates
    summary["pass"] = all(gates.values())
    return summary


def factorial_components(
    indexed: Mapping[tuple, dict],
    exercise_rates: Mapping[str, float],
) -> dict:
    results = {}
    for name, bit in COMPONENTS.items():
        observations = []
        for key in sorted(expected_tasks()):
            for start in MARKS:
                for base_mask in range(8):
                    if base_mask & bit:
                        continue
                    without = indexed[(*key, label_for(start, base_mask))]
                    with_component = indexed[(*key, label_for(start, base_mask | bit))]
                    observations.append(
                        paired_observation(
                            with_component,
                            without,
                            start=start,
                        )
                    )
        results[name] = summarize_component(
            name,
            observations,
            exercise_rates.get(name, 0.0),
        )
    return results


def interaction_effects(indexed: Mapping[tuple, dict]) -> dict:
    two_way = {}
    bits = list(COMPONENTS.items())
    for left_index, (left_name, left_bit) in enumerate(bits):
        for right_name, right_bit in bits[left_index + 1 :]:
            other_bit = 7 ^ left_bit ^ right_bit
            observations = []
            for key in sorted(expected_tasks()):
                for start in MARKS:
                    for other_enabled in (0, other_bit):
                        row_00 = indexed[(*key, label_for(start, other_enabled))]
                        row_10 = indexed[
                            (*key, label_for(start, other_enabled | left_bit))
                        ]
                        row_01 = indexed[
                            (*key, label_for(start, other_enabled | right_bit))
                        ]
                        row_11 = indexed[
                            (
                                *key,
                                label_for(
                                    start,
                                    other_enabled | left_bit | right_bit,
                                ),
                            )
                        ]
                        observations.append(
                            {
                                "map_seed": key[0],
                                "seat": key[1],
                                "opponent": key[2],
                                "start": start,
                                "margin": margin(row_11)
                                - margin(row_10)
                                - margin(row_01)
                                + margin(row_00),
                            }
                        )
            two_way[f"{left_name}_x_{right_name}"] = {
                "observations": len(observations),
                "mean_margin_interaction": mean(
                    item["margin"] for item in observations
                ),
                "map_clustered_normal_95pct_interval": normal_interval_by_map(
                    observations
                ),
            }

    observations = []
    for key in sorted(expected_tasks()):
        for start in MARKS:
            values = {
                mask: margin(indexed[(*key, label_for(start, mask))])
                for mask in range(8)
            }
            effect = (
                values[7]
                - values[6]
                - values[5]
                - values[3]
                + values[4]
                + values[2]
                + values[1]
                - values[0]
            )
            observations.append(
                {
                    "map_seed": key[0],
                    "seat": key[1],
                    "opponent": key[2],
                    "start": start,
                    "margin": effect,
                }
            )
    return {
        "two_way": two_way,
        "three_way": {
            "observations": len(observations),
            "mean_margin_interaction": mean(
                item["margin"] for item in observations
            ),
            "map_clustered_normal_95pct_interval": normal_interval_by_map(
                observations
            ),
        },
    }


def fixed_arm_metrics(indexed: Mapping[tuple, dict]) -> dict:
    residents = {
        key: indexed[(*key, "resident")] for key in sorted(expected_tasks())
    }
    resident_crop_rate = mean(
        row["own_created_crops"] > 0 for row in residents.values()
    )
    resident_tail = tail(residents.values())
    results = {}
    for policy in catalog()[1:]:
        rows = [
            indexed[(*key, policy["label"])] for key in sorted(expected_tasks())
        ]
        observations = [
            paired_observation(row, residents[task(row)], start=policy["start"])
            for row in rows
        ]
        by_family = defaultdict(list)
        by_seat = defaultdict(list)
        for observation in observations:
            by_family[observation["opponent"]].append(observation["margin"])
            by_seat[observation["seat"]].append(observation["margin"])
        family_means = {
            opponent: mean(by_family[opponent]) for opponent in OPPONENTS
        }
        seat_means = {str(seat): mean(by_seat[seat]) for seat in range(2)}
        arm_tail = tail(rows)
        deltas = [item["margin"] for item in observations]
        interval = normal_interval_by_map(observations)
        arm_crop_rate = mean(row["own_created_crops"] > 0 for row in rows)
        summary = {
            "mask": policy["mask"],
            "start": policy["start"],
            "mean_margin_delta": mean(deltas),
            "mean_own_score_delta": mean(item["own"] for item in observations),
            "mean_opponent_score_delta": mean(
                item["opponent_score"] for item in observations
            ),
            "map_clustered_normal_95pct_interval": interval,
            "strict_improvements": sum(value > 0 for value in deltas),
            "ties": sum(value == 0 for value in deltas),
            "strict_regressions": sum(value < 0 for value in deltas),
            "family_mean_margin_deltas": family_means,
            "positive_families": sum(value > 0 for value in family_means.values()),
            "seat_mean_margin_deltas": seat_means,
            "resident_crop_creation_rate": resident_crop_rate,
            "arm_crop_creation_rate": arm_crop_rate,
            "resident_tail": resident_tail,
            "arm_tail": arm_tail,
            "workforce_mismatches": sum(
                item["workforce_mismatch"] for item in observations
            ),
        }
        gates = {
            "mean_margin_gain_at_least_4": summary["mean_margin_delta"] >= 4.0,
            "map_clustered_95pct_lower_bound_above_zero": interval[0] > 0.0,
            "improvements_at_least_regressions": (
                summary["strict_improvements"] >= summary["strict_regressions"]
            ),
            "at_least_six_positive_families": summary["positive_families"] >= 6,
            "both_seats_nonnegative": all(
                value >= 0 for value in seat_means.values()
            ),
            "crop_creation_within_2pp": (
                arm_crop_rate >= resident_crop_rate - 0.02
            ),
            "catastrophe_count_not_increased": (
                arm_tail["catastrophe_count"]
                <= resident_tail["catastrophe_count"]
            ),
            "negative_margin_mass_not_increased": (
                arm_tail["negative_margin_mass"]
                <= resident_tail["negative_margin_mass"]
            ),
            "workforce_exact": summary["workforce_mismatches"] == 0,
        }
        summary["gates"] = gates
        summary["pass"] = all(gates.values())
        results[policy["label"]] = summary
    return results


def analyze(run_a: Path, run_b: Path) -> dict:
    lock = verify_lock()
    repeated_exact = run_a.read_bytes() == run_b.read_bytes()
    rows_a, fields_a = read_rows(run_a)
    rows_b, fields_b = read_rows(run_b)
    grid_a, index_a = validate_grid(rows_a, fields_a)
    grid_b, _ = validate_grid(rows_b, fields_b)
    parity = resident_parity(index_a)
    mechanism = mechanics(rows_a, index_a)
    components = factorial_components(
        index_a,
        mechanism["component_exercise_rates"],
    )
    interactions = interaction_effects(index_a)
    fixed_arms = fixed_arm_metrics(index_a)
    integrity_gates = {
        "frozen_lock_matches": lock["pass"],
        "jobs1_and_jobs20_byte_identical": repeated_exact,
        "jobs1_grid_exact": grid_a["pass"],
        "jobs20_grid_exact": grid_b["pass"],
        "resident_reproduces_d161": parity["pass"],
        "d162_panel_disjoint": START_SEED >= 9_844_144,
        "reserved_maps_excluded": START_SEED + MAP_COUNT <= RESERVED_START_SEED,
    }
    integrity_pass = all(integrity_gates.values())
    passing_components = [
        name for name, summary in components.items() if summary["pass"]
    ]
    passing_fixed_arms = [
        label for label, summary in fixed_arms.items() if summary["pass"]
    ]
    eligible_fixed_arms = [
        label
        for label in passing_fixed_arms
        if any(
            fixed_arms[label]["mask"] & COMPONENTS[name]
            for name in passing_components
        )
    ]
    continuation_open = (
        integrity_pass
        and mechanism["pass"]
        and bool(passing_components)
        and bool(eligible_fixed_arms)
    )
    if not integrity_pass:
        decision = "repair_d163_measurement_before_interpretation"
    elif not mechanism["pass"]:
        decision = "close_d163_causal_interpretation_on_mechanism"
    elif not passing_components:
        decision = "close_fixed_shadow_reserve_grammar_no_causal_component"
    elif not eligible_fixed_arms:
        decision = "retain_causal_component_for_state_gated_followup"
    else:
        decision = "open_d163b_held_consumed_panel_validation"
    return {
        "schema": "troll-farm-d163a-resident-resource-control-components-v1",
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
            "runner": {
                "path": str(RUNNER.relative_to(ROOT)),
                "sha256": sha256(RUNNER),
            },
            "build_script": {
                "path": str(BUILD_SCRIPT.relative_to(ROOT)),
                "sha256": sha256(BUILD_SCRIPT),
            },
        },
        "catalog": catalog(),
        "runner_validation": {"jobs1": grid_a, "jobs20": grid_b},
        "resident_parity": parity,
        "integrity": {"gates": integrity_gates, "pass": integrity_pass},
        "mechanism": mechanism,
        "components": components,
        "interactions": interactions,
        "fixed_arms": fixed_arms,
        "passing_components": passing_components,
        "passing_fixed_arms": passing_fixed_arms,
        "eligible_fixed_arms": eligible_fixed_arms,
        "pass": continuation_open,
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
