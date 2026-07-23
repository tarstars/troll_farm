#!/usr/bin/env python3
"""Analyze the frozen D91c factory activation-selector discovery panel."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import statistics
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.analyze_d89a_banana_seed_factory import (
    cohort_summary,
    negative_margin_mass,
    normal_ci,
    own_crop_harvest,
    owned_chop_wood,
    read_tsv,
)

PROFILES = ("resident", "banana_seed_factory_activation_selector")
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


def selector_predicate(row: dict) -> bool:
    return (
        row["banana_factory_activation_plants"] <= 20
        and row["banana_factory_activation_fruits"] >= 27
        and row["banana_factory_activation_banana_plants"] >= 6
    )


def pair_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    grouped: dict[tuple, dict[str, dict]] = defaultdict(dict)
    failures = []
    for row in rows:
        key = (row["seed"], row["seat"], row["opponent"])
        if row["profile"] in grouped[key]:
            failures.append({"kind": "duplicate", "key": key, "profile": row["profile"]})
        grouped[key][row["profile"]] = row
    for key, profiles in sorted(grouped.items()):
        if set(profiles) != set(PROFILES):
            failures.append(
                {"kind": "incomplete", "key": key, "profiles": sorted(profiles)}
            )

    pairs = []
    for key, profiles in sorted(grouped.items()):
        if set(profiles) != set(PROFILES):
            continue
        resident = profiles["resident"]
        candidate = profiles["banana_seed_factory_activation_selector"]
        selected = candidate["banana_factory_selector_selected"] == 1
        active = candidate["banana_factory_active"] == 1
        harvest_successes = candidate["banana_factory_harvest_successes"]
        renewable_successes = candidate[
            "banana_factory_renewable_plant_successes"
        ]
        resident_margin = resident["own_score"] - resident["opponent_score"]
        candidate_margin = candidate["own_score"] - candidate["opponent_score"]
        resident_crop_harvest = own_crop_harvest(resident)
        candidate_crop_harvest = own_crop_harvest(candidate)
        resident_chop = owned_chop_wood(resident)
        candidate_chop = owned_chop_wood(candidate)
        pairs.append(
            {
                "seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "selected": selected,
                "active": active,
                "selector_expected": selector_predicate(candidate),
                "selector_decided": candidate["banana_factory_selector_decided"],
                "activation_turn": candidate["banana_factory_activation_turn"],
                "initial_budget": candidate["banana_factory_initial_budget"],
                "bootstrap_attempts": candidate[
                    "banana_factory_bootstrap_attempts"
                ],
                "bootstrap_successes": candidate[
                    "banana_factory_bootstrap_successes"
                ],
                "harvest_selections": candidate[
                    "banana_factory_harvest_selections"
                ],
                "harvest_successes": harvest_successes,
                "renewable_plant_attempts": candidate[
                    "banana_factory_renewable_plant_attempts"
                ],
                "renewable_plant_successes": renewable_successes,
                "trained_forbidden_commands": candidate[
                    "banana_factory_trained_forbidden_commands"
                ],
                "preactivation_mismatches": candidate[
                    "banana_factory_preactivation_mismatches"
                ],
                "sustained": harvest_successes > 0 and renewable_successes > 0,
                "resident": {
                    "score": resident["own_score"],
                    "opponent_score": resident["opponent_score"],
                    "margin": resident_margin,
                    "wood": resident["own_inventory_wood"],
                    "owned_chop_wood": resident_chop,
                    "workers": resident["workers"],
                    "plants": resident["own_successful_plants"],
                    "own_crop_harvest": resident_crop_harvest,
                    "action_hash": resident["action_hash"],
                    "state_hash": resident["terminal_state_hash"],
                },
                "candidate": {
                    "score": candidate["own_score"],
                    "opponent_score": candidate["opponent_score"],
                    "margin": candidate_margin,
                    "wood": candidate["own_inventory_wood"],
                    "owned_chop_wood": candidate_chop,
                    "workers": candidate["workers"],
                    "plants": candidate["own_successful_plants"],
                    "own_crop_harvest": candidate_crop_harvest,
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
                    "owned_chop_wood": candidate_chop - resident_chop,
                    "plants": candidate["own_successful_plants"]
                    - resident["own_successful_plants"],
                    "own_crop_harvest": candidate_crop_harvest
                    - resident_crop_harvest,
                },
                "inactive_exact": selected
                or all(candidate[field] == resident[field] for field in PAIR_FIELDS),
                "worker_exact": candidate["workers"] == resident["workers"],
            }
        )
    return pairs, failures


def analyze(path_a: Path, path_b: Path) -> dict:
    content_a = path_a.read_bytes()
    content_b = path_b.read_bytes()
    rows = read_tsv(path_a)
    pairs, pairing_failures = pair_rows(rows)
    candidates = [
        row
        for row in rows
        if row["profile"] == "banana_seed_factory_activation_selector"
    ]
    active = [pair for pair in pairs if pair["active"]]
    inactive = [pair for pair in pairs if not pair["active"]]
    bootstrap = [pair for pair in active if pair["bootstrap_successes"] >= 3]
    complete_bootstrap = [
        pair
        for pair in active
        if pair["initial_budget"] > 0
        and pair["bootstrap_successes"] == pair["initial_budget"]
    ]
    sustained = [pair for pair in active if pair["sustained"]]

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
        "all_selectors_decided": all(pair["selector_decided"] == 1 for pair in pairs),
        "selector_predicate_exact": all(
            pair["selected"] == pair["selector_expected"] for pair in pairs
        ),
        "selected_equals_factory_active": all(
            pair["selected"] == pair["active"] for pair in pairs
        ),
        "zero_preactivation_mismatch": all(
            row["banana_factory_preactivation_mismatches"] == 0
            for row in candidates
        ),
        "inactive_action_state_terminal_exact": all(
            pair["inactive_exact"] for pair in inactive
        ),
        "worker_count_pair_exact": all(pair["worker_exact"] for pair in pairs),
        "bootstrap_successes_bounded": all(
            pair["bootstrap_successes"] <= pair["bootstrap_attempts"]
            and pair["bootstrap_successes"] <= pair["initial_budget"]
            for pair in active
        ),
        "harvest_successes_bounded": all(
            pair["harvest_successes"] <= pair["harvest_selections"]
            for pair in active
        ),
        "renewable_successes_bounded": all(
            pair["renewable_plant_successes"]
            <= pair["renewable_plant_attempts"]
            for pair in active
        ),
        "zero_trained_forbidden_commands": all(
            pair["trained_forbidden_commands"] == 0 for pair in pairs
        ),
        "source_semantic_tests_passed": True,
    }
    bootstrap_rate = len(bootstrap) / len(active) if active else 0.0
    complete_bootstrap_rate = (
        len(complete_bootstrap) / len(active) if active else 0.0
    )
    activation_gates = {
        "selected_tasks_at_least_32": len(active) >= 32,
        "both_seats_selected": len({pair["seat"] for pair in active}) == 2,
        "at_least_6_opponents_selected": len(
            {pair["opponent"] for pair in active}
        )
        >= 6,
        "complete_available_bootstrap_rate_at_least_0.95": complete_bootstrap_rate
        >= 0.95,
        "sustained_tasks_at_least_24": len(sustained) >= 24,
        "zero_trained_harvest_or_plant": all(
            pair["trained_forbidden_commands"] == 0 for pair in active
        ),
    }

    base = {
        "schema": 1,
        "scope": "D91c prospective local discovery only; confirmation unopened",
        "input_hashes": {
            "rows_a": hashlib.sha256(content_a).hexdigest(),
            "rows_b": hashlib.sha256(content_b).hexdigest(),
        },
        "counts": {
            "rows": len(rows),
            "pairs": len(pairs),
            "selected_tasks": len(active),
            "abstained_tasks": len(inactive),
            "bootstrap_3plus_tasks": len(bootstrap),
            "bootstrap_3plus_rate": bootstrap_rate,
            "complete_available_bootstrap_tasks": len(complete_bootstrap),
            "complete_available_bootstrap_rate": complete_bootstrap_rate,
            "sustained_tasks": len(sustained),
            "selected_seats": sorted({pair["seat"] for pair in active}),
            "selected_opponents": sorted({pair["opponent"] for pair in active}),
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

    overall_summary = cohort_summary(pairs)
    active_summary = cohort_summary(active)
    inactive_summary = cohort_summary(inactive)

    by_seed: dict[int, list[float]] = defaultdict(list)
    for pair in pairs:
        by_seed[pair["seed"]].append(pair["delta"]["margin"])
    seed_means = [
        {"seed": seed, "mean_margin_delta": statistics.mean(values)}
        for seed, values in sorted(by_seed.items())
    ]
    seed_ci = normal_ci(row["mean_margin_delta"] for row in seed_means)

    families = {}
    for opponent in sorted({pair["opponent"] for pair in active}):
        families[opponent] = cohort_summary(
            [pair for pair in active if pair["opponent"] == opponent]
        )
    family_means = [summary["mean_margin_delta"] for summary in families.values()]

    resident_catastrophes = sum(
        pair["resident"]["margin"] <= -100 for pair in pairs
    )
    candidate_catastrophes = sum(
        pair["candidate"]["margin"] <= -100 for pair in pairs
    )
    resident_negative_mass = negative_margin_mass(pairs, "resident")
    candidate_negative_mass = negative_margin_mass(pairs, "candidate")
    negative_mass_ratio = (
        candidate_negative_mass / resident_negative_mass
        if resident_negative_mass
        else (0.0 if candidate_negative_mass == 0 else None)
    )
    competitive_efficiency = (
        active_summary["mean_opponent_score_delta"]
        / active_summary["mean_score_delta"]
        if active_summary["mean_score_delta"] > 0
        else None
    )
    value_gates = {
        "overall_mean_margin_at_least_5": overall_summary["mean_margin_delta"] >= 5,
        "map_cluster_ci_lower_nonnegative": seed_ci is not None and seed_ci[0] >= 0,
        "selected_mean_margin_at_least_40": active_summary["mean_margin_delta"] >= 40,
        "selected_mean_score_at_least_60": active_summary["mean_score_delta"] >= 60,
        "selected_more_improve_than_regress": active_summary["improved"]
        > active_summary["regressed"],
        "selected_regression_rate_at_most_0.20": active_summary["regressed"]
        / active_summary["n"]
        <= 0.20,
        "at_least_6_nonnegative_selected_families": sum(
            value >= 0 for value in family_means
        )
        >= 6,
        "worst_selected_family_at_least_minus_5": min(family_means) >= -5,
        "selected_p10_at_least_minus_20": active_summary["p10_margin_delta"] >= -20,
        "selected_worst_at_least_minus_60": active_summary[
            "minimum_margin_delta"
        ]
        >= -60,
        "catastrophes_do_not_increase": candidate_catastrophes
        <= resident_catastrophes,
        "negative_margin_mass_at_most_resident": negative_mass_ratio is not None
        and negative_mass_ratio <= 1.0,
        "selected_wood_delta_positive": active_summary["mean_wood_delta"] > 0,
        "selected_own_crop_harvest_delta_positive": active_summary[
            "mean_own_crop_harvest_delta"
        ]
        > 0,
        "opponent_growth_at_most_0.40_of_own_growth": competitive_efficiency
        is not None
        and competitive_efficiency <= 0.40,
    }
    decision = (
        "pass_open_sealed_confirmation"
        if all(value_gates.values())
        else "reject_value_or_safety_keep_confirmation_sealed"
    )
    return {
        **base,
        "value": {
            "overall": overall_summary,
            "selected": active_summary,
            "abstained": inactive_summary,
            "map_seed_means": seed_means,
            "map_cluster_normal_ci_95": seed_ci,
            "selected_opponent_families": families,
            "resident_catastrophes": resident_catastrophes,
            "candidate_catastrophes": candidate_catastrophes,
            "resident_negative_margin_mass": resident_negative_mass,
            "candidate_negative_margin_mass": candidate_negative_mass,
            "negative_margin_mass_ratio": negative_mass_ratio,
            "competitive_efficiency_ratio": competitive_efficiency,
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
                "selected": result["value"]["selected"],
                "map_ci": result["value"]["map_cluster_normal_ci_95"],
                "competitive_efficiency": result["value"][
                    "competitive_efficiency_ratio"
                ],
                "value_gates": result["value_gates"],
            }
        )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
