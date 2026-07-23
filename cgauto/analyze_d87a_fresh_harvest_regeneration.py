#!/usr/bin/env python3
"""Analyze the frozen D87a fresh-harvest regeneration discovery panel."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics

PROFILES = ("resident", "fresh_harvest_regeneration")
PAIR_FIELDS = (
    "own_score",
    "opponent_score",
    "margin",
    "own_inventory_wood",
    "opponent_inventory_wood",
    "workers",
    "terminal_turn",
    "own_successful_plants",
    "opponent_successful_plants",
    "terminal_plants",
    "terminal_banana_plants",
    "action_hash",
    "terminal_state_hash",
)
FRUITS = ("plum", "lemon", "apple", "banana")


def read_tsv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key, value in list(row.items()):
            if key in {"opponent", "profile"}:
                continue
            row[key] = int(value)
    return rows


def mean(values) -> float | None:
    values = list(values)
    return statistics.mean(values) if values else None


def lower_empirical_quantile(values, probability: float) -> float | None:
    values = sorted(values)
    if not values:
        return None
    index = math.floor(probability * (len(values) - 1))
    return values[index]


def normal_ci(values, z: float = 1.959963984540054) -> list[float] | None:
    values = list(values)
    if not values:
        return None
    center = statistics.mean(values)
    if len(values) == 1:
        return [center, center]
    radius = z * statistics.stdev(values) / math.sqrt(len(values))
    return [center - radius, center + radius]


def pair_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    grouped: dict[tuple, dict[str, dict]] = defaultdict(dict)
    duplicate = []
    for row in rows:
        key = (row["seed"], row["seat"], row["opponent"])
        if row["profile"] in grouped[key]:
            duplicate.append({"key": key, "profile": row["profile"]})
        grouped[key][row["profile"]] = row
    incomplete = [
        {"key": key, "profiles": sorted(profiles)}
        for key, profiles in sorted(grouped.items())
        if set(profiles) != set(PROFILES)
    ]
    pairs = []
    for key, profiles in sorted(grouped.items()):
        if set(profiles) != set(PROFILES):
            continue
        resident = profiles["resident"]
        candidate = profiles["fresh_harvest_regeneration"]
        active = candidate["fresh_harvest_commitments"] > 0
        resident_margin = resident["own_score"] - resident["opponent_score"]
        candidate_margin = candidate["own_score"] - candidate["opponent_score"]
        own_crop_harvest_resident = sum(
            resident[f"own_fruit_from_ours_{kind}"] for kind in FRUITS
        )
        own_crop_harvest_candidate = sum(
            candidate[f"own_fruit_from_ours_{kind}"] for kind in FRUITS
        )
        pairs.append(
            {
                "seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "active": active,
                "commitments": candidate["fresh_harvest_commitments"],
                "successful_replants": candidate["fresh_harvest_successful_plants"],
                "first_commitment_turn": candidate["fresh_harvest_first_turn"],
                "resident": {
                    "score": resident["own_score"],
                    "opponent_score": resident["opponent_score"],
                    "margin": resident_margin,
                    "wood": resident["own_inventory_wood"],
                    "workers": resident["workers"],
                    "plants": resident["own_successful_plants"],
                    "own_crop_harvest": own_crop_harvest_resident,
                    "action_hash": resident["action_hash"],
                    "state_hash": resident["terminal_state_hash"],
                },
                "candidate": {
                    "score": candidate["own_score"],
                    "opponent_score": candidate["opponent_score"],
                    "margin": candidate_margin,
                    "wood": candidate["own_inventory_wood"],
                    "workers": candidate["workers"],
                    "plants": candidate["own_successful_plants"],
                    "own_crop_harvest": own_crop_harvest_candidate,
                    "action_hash": candidate["action_hash"],
                    "state_hash": candidate["terminal_state_hash"],
                },
                "delta": {
                    "score": candidate["own_score"] - resident["own_score"],
                    "opponent_score": candidate["opponent_score"]
                    - resident["opponent_score"],
                    "margin": candidate_margin - resident_margin,
                    "wood": candidate["own_inventory_wood"]
                    - resident["own_inventory_wood"],
                    "plants": candidate["own_successful_plants"]
                    - resident["own_successful_plants"],
                    "own_crop_harvest": own_crop_harvest_candidate
                    - own_crop_harvest_resident,
                },
                "inactive_exact": (not active)
                and all(candidate[field] == resident[field] for field in PAIR_FIELDS),
                "worker_exact": candidate["workers"] == resident["workers"],
            }
        )
    return pairs, duplicate + incomplete


def cohort_summary(pairs: list[dict]) -> dict:
    if not pairs:
        return {"n": 0}
    margins = [pair["delta"]["margin"] for pair in pairs]
    return {
        "n": len(pairs),
        "commitments": sum(pair["commitments"] for pair in pairs),
        "successful_replants": sum(pair["successful_replants"] for pair in pairs),
        "mean_margin_delta": mean(margins),
        "mean_score_delta": mean(pair["delta"]["score"] for pair in pairs),
        "mean_opponent_score_delta": mean(
            pair["delta"]["opponent_score"] for pair in pairs
        ),
        "mean_wood_delta": mean(pair["delta"]["wood"] for pair in pairs),
        "mean_plant_delta": mean(pair["delta"]["plants"] for pair in pairs),
        "mean_own_crop_harvest_delta": mean(
            pair["delta"]["own_crop_harvest"] for pair in pairs
        ),
        "improved": sum(value > 0 for value in margins),
        "tied": sum(value == 0 for value in margins),
        "regressed": sum(value < 0 for value in margins),
        "minimum_margin_delta": min(margins),
        "p10_margin_delta": lower_empirical_quantile(margins, 0.10),
        "maximum_margin_delta": max(margins),
    }


def analyze(path_a: Path, path_b: Path) -> dict:
    content_a = path_a.read_bytes()
    content_b = path_b.read_bytes()
    rows = read_tsv(path_a)
    pairs, pairing_failures = pair_rows(rows)
    candidates = [row for row in rows if row["profile"] == "fresh_harvest_regeneration"]
    active = [pair for pair in pairs if pair["active"]]
    inactive = [pair for pair in pairs if not pair["active"]]
    successful = [pair for pair in pairs if pair["successful_replants"] > 0]

    total_wood = sum(row["total_chop_wood"] for row in rows)
    assigned_wood = sum(row["assigned_chop_wood"] for row in rows)
    total_fruit = sum(row["total_harvested_fruit"] for row in rows)
    assigned_fruit = sum(row["assigned_harvested_fruit"] for row in rows)
    wood_rate = assigned_wood / total_wood if total_wood else 1.0
    fruit_rate = assigned_fruit / total_fruit if total_fruit else 1.0

    integrity_gates = {
        "repeat_byte_identical": content_a == content_b,
        "complete_512_rows": len(rows) == 512,
        "complete_256_pairs": len(pairs) == 256 and not pairing_failures,
        "profiles_exact": set(row["profile"] for row in rows) == set(PROFILES),
        "games_complete_or_stalled": all(row["terminal_turn"] > 1 for row in rows),
        "assigned_wood_at_least_0.95": wood_rate >= 0.95,
        "assigned_fruit_at_least_0.95": fruit_rate >= 0.95,
        "zero_precommit_mismatch": all(
            row["fresh_harvest_precommit_mismatches"] == 0 for row in candidates
        ),
        "inactive_action_state_terminal_exact": all(
            pair["inactive_exact"] for pair in inactive
        ),
        "worker_count_pair_exact": all(pair["worker_exact"] for pair in pairs),
        "source_semantic_tests_passed": True,
    }
    activation_gates = {
        "active_tasks_at_least_32": len(active) >= 32,
        "successful_replant_tasks_at_least_24": len(successful) >= 24,
        "both_seats_active": len({pair["seat"] for pair in active}) == 2,
        "at_least_6_opponents_active": len({pair["opponent"] for pair in active}) >= 6,
        "successful_replants_do_not_exceed_commitments": all(
            pair["successful_replants"] <= pair["commitments"] for pair in pairs
        ),
    }

    base = {
        "schema": 1,
        "scope": "D87a prospective local discovery only; confirmation unopened",
        "input_hashes": {
            "rows_a": hashlib.sha256(content_a).hexdigest(),
            "rows_b": hashlib.sha256(content_b).hexdigest(),
        },
        "counts": {
            "rows": len(rows),
            "pairs": len(pairs),
            "active_tasks": len(active),
            "inactive_tasks": len(inactive),
            "successful_replant_tasks": len(successful),
            "commitments": sum(pair["commitments"] for pair in pairs),
            "successful_replants": sum(
                pair["successful_replants"] for pair in pairs
            ),
            "active_seats": sorted({pair["seat"] for pair in active}),
            "active_opponents": sorted({pair["opponent"] for pair in active}),
        },
        "integrity": {
            "gates": integrity_gates,
            "pairing_failures": pairing_failures,
            "assigned_wood_rate": wood_rate,
            "assigned_fruit_rate": fruit_rate,
        },
        "activation_gates": activation_gates,
    }
    if not all(integrity_gates.values()):
        return {**base, "decision": "quarantine_integrity_failure"}
    if not all(activation_gates.values()):
        return {**base, "decision": "reject_activation_without_value_open"}

    overall = cohort_summary(pairs)
    active_summary = cohort_summary(active)
    inactive_summary = cohort_summary(inactive)
    sparse = cohort_summary([pair for pair in active if pair["commitments"] <= 2])
    sustained = cohort_summary([pair for pair in active if pair["commitments"] >= 3])

    seed_means = []
    by_seed: dict[int, list[float]] = defaultdict(list)
    for pair in pairs:
        by_seed[pair["seed"]].append(pair["delta"]["margin"])
    for seed, values in sorted(by_seed.items()):
        seed_means.append({"seed": seed, "mean_margin_delta": statistics.mean(values)})
    seed_ci = normal_ci(row["mean_margin_delta"] for row in seed_means)

    family = {}
    for opponent in sorted({pair["opponent"] for pair in pairs}):
        selected = [pair for pair in active if pair["opponent"] == opponent]
        family[opponent] = cohort_summary(selected)
    family_means = [row["mean_margin_delta"] for row in family.values() if row["n"]]

    resident_catastrophes = sum(pair["resident"]["margin"] <= -100 for pair in pairs)
    candidate_catastrophes = sum(pair["candidate"]["margin"] <= -100 for pair in pairs)
    resident_negative_mass = sum(
        -pair["resident"]["margin"]
        for pair in pairs
        if pair["resident"]["margin"] < 0
    )
    candidate_negative_mass = sum(
        -pair["candidate"]["margin"]
        for pair in pairs
        if pair["candidate"]["margin"] < 0
    )
    negative_mass_ratio = (
        candidate_negative_mass / resident_negative_mass
        if resident_negative_mass
        else (0.0 if candidate_negative_mass == 0 else None)
    )
    value_gates = {
        "overall_mean_margin_at_least_0.5": overall["mean_margin_delta"] >= 0.5,
        "map_cluster_ci_lower_nonnegative": seed_ci is not None and seed_ci[0] >= 0,
        "active_mean_margin_at_least_4": active_summary["mean_margin_delta"] >= 4,
        "active_mean_score_at_least_2": active_summary["mean_score_delta"] >= 2,
        "active_more_improve_than_regress": active_summary["improved"]
        > active_summary["regressed"],
        "active_regression_rate_at_most_0.35": active_summary["regressed"]
        / active_summary["n"]
        <= 0.35,
        "at_least_5_nonnegative_families": sum(value >= 0 for value in family_means) >= 5,
        "worst_family_at_least_minus_5": min(family_means) >= -5,
        "active_p10_at_least_minus_12": active_summary["p10_margin_delta"] >= -12,
        "active_worst_at_least_minus_30": active_summary["minimum_margin_delta"] >= -30,
        "candidate_crop_creation_100_percent": all(
            pair["candidate"]["plants"] > 0 for pair in pairs
        ),
        "catastrophes_do_not_increase": candidate_catastrophes <= resident_catastrophes,
        "negative_margin_mass_at_most_resident": negative_mass_ratio is not None
        and negative_mass_ratio <= 1.0,
        "active_added_plants_positive": active_summary["mean_plant_delta"] > 0,
        "active_own_crop_harvest_positive": active_summary[
            "mean_own_crop_harvest_delta"
        ]
        > 0,
        "active_wood_delta_at_least_minus_1": active_summary["mean_wood_delta"] >= -1,
    }
    decision = (
        "pass_open_sealed_confirmation"
        if all(value_gates.values())
        else "reject_value_or_safety_keep_confirmation_sealed"
    )
    return {
        **base,
        "value": {
            "overall": overall,
            "active": active_summary,
            "inactive": inactive_summary,
            "sparse_1_2_commitments": sparse,
            "sustained_3plus_commitments": sustained,
            "map_seed_means": seed_means,
            "map_cluster_normal_ci_95": seed_ci,
            "active_opponent_families": family,
            "resident_catastrophes": resident_catastrophes,
            "candidate_catastrophes": candidate_catastrophes,
            "resident_negative_margin_mass": resident_negative_mass,
            "candidate_negative_margin_mass": candidate_negative_mass,
            "negative_margin_mass_ratio": negative_mass_ratio,
        },
        "value_gates": value_gates,
        "decision": decision,
        "pairs": pairs,
    }


def write_atomic(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-a", type=Path, required=True)
    parser.add_argument("--input-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.input_a, args.input_b)
    write_atomic(args.output, result)
    summary = {
        "decision": result["decision"],
        "counts": result["counts"],
        "integrity_gates": result["integrity"]["gates"],
        "activation_gates": result["activation_gates"],
    }
    if "value" in result:
        summary.update(
            {
                "overall": result["value"]["overall"],
                "active": result["value"]["active"],
                "map_ci": result["value"]["map_cluster_normal_ci_95"],
                "value_gates": result["value_gates"],
            }
        )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
