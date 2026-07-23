#!/usr/bin/env python3
"""Analyze D34 complete-controller transfer on exact official maps."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import statistics


CONTROLLERS = (
    "resident",
    "private2",
    "ownership2",
    "prefruit2",
    "gold_adaptive",
    "separated_denial",
    "hybrid3",
    "accumulate4",
    "norx3",
)
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
RICH_OPPONENTS = ("gold_adaptive", "norx_native_three", "legend_balanced")
DENIAL_PARENTS = {
    "prefruit2": "private2",
    "separated_denial": "gold_adaptive",
}
INTEGER_FIELDS = (
    "seed",
    "seat",
    "width",
    "height",
    "initial_plants",
    "final_turn",
    "margin",
    "my_score",
    "opponent_score",
    *(f"my_inv{index}" for index in range(6)),
    *(f"opponent_inv{index}" for index in range(6)),
    "my_workers",
    "opponent_workers",
    "max_my_workers",
    "max_opponent_workers",
    "first_my_third_worker_turn",
    "first_opponent_third_worker_turn",
    *(f"my_{verb}" for verb in ("train", "move", "chop", "harvest", "drop", "pick", "plant", "mine")),
    *(f"opponent_{verb}" for verb in ("train", "move", "chop", "harvest", "drop", "pick", "plant", "mine")),
    "my_successful_plants",
    "opponent_successful_plants",
    "ambiguous_plants",
    "max_plants",
    "terminal_plants",
    "my_command_hash",
    "opponent_command_hash",
)


def robust_summary(values) -> dict:
    values = list(values)
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "trimmed_5pct_mean": None,
            "standard_deviation": None,
            "standard_error": None,
            "ci95_normal": [None, None],
            "wins": 0,
            "ties": 0,
            "losses": 0,
            "minimum": None,
            "maximum": None,
        }
    ordered = sorted(values)
    trim = math.floor(0.05 * len(ordered))
    trimmed = ordered[trim : len(ordered) - trim] if trim else ordered
    mean = statistics.mean(values)
    sd = statistics.stdev(values) if len(values) > 1 else 0.0
    se = sd / math.sqrt(len(values))
    return {
        "n": len(values),
        "mean": mean,
        "median": statistics.median(values),
        "trimmed_5pct_mean": statistics.mean(trimmed),
        "standard_deviation": sd,
        "standard_error": se,
        "ci95_normal": [mean - 1.96 * se, mean + 1.96 * se],
        "wins": sum(value > 0 for value in values),
        "ties": sum(value == 0 for value in values),
        "losses": sum(value < 0 for value in values),
        "minimum": ordered[0],
        "maximum": ordered[-1],
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


def row_key(row: dict) -> tuple[int, int, str]:
    return row["seed"], row["seat"], row["opponent"]


def validate_grid(rows: list[dict], seed_start: int, seed_count: int) -> tuple[dict, dict]:
    expected_seeds = set(range(seed_start, seed_start + seed_count))
    expected_keys = {
        (seed, seat, opponent, controller)
        for seed in expected_seeds
        for seat in (0, 1)
        for opponent in OPPONENTS
        for controller in CONTROLLERS
    }
    grouped: dict[tuple[int, int, str], dict[str, dict]] = defaultdict(dict)
    duplicates = []
    actual_keys = set()
    for row in rows:
        key = (*row_key(row), row["controller"])
        if key in actual_keys:
            duplicates.append(key)
        actual_keys.add(key)
        grouped[row_key(row)][row["controller"]] = row

    map_fields_consistent = True
    map_signatures = defaultdict(set)
    for row in rows:
        map_signatures[row["seed"]].add(
            (row["width"], row["height"], row["initial_plants"])
        )
    map_fields_consistent = all(len(values) == 1 for values in map_signatures.values())
    expected_controller_set = set(CONTROLLERS)
    bad_controller_sets = {
        str(key): sorted(set(branches) ^ expected_controller_set)
        for key, branches in grouped.items()
        if set(branches) != expected_controller_set
    }
    ambiguous_plants = sum(row["ambiguous_plants"] for row in rows)
    invalid_dimensions = sum(
        not (8 <= row["height"] <= 11 and row["width"] == 2 * row["height"])
        for row in rows
    )
    invalid_turns = sum(not (2 <= row["final_turn"] <= 301) for row in rows)
    integrity = {
        "expected_rows": len(expected_keys),
        "actual_rows": len(rows),
        "missing_rows": len(expected_keys - actual_keys),
        "unexpected_rows": len(actual_keys - expected_keys),
        "duplicate_rows": len(duplicates),
        "expected_scenarios": seed_count * 2 * len(OPPONENTS),
        "actual_scenarios": len(grouped),
        "bad_controller_sets": bad_controller_sets,
        "map_fields_consistent_within_seed": map_fields_consistent,
        "ambiguous_plants": ambiguous_plants,
        "ambiguous_plants_reported_separately": True,
        "invalid_dimensions": invalid_dimensions,
        "invalid_terminal_turns": invalid_turns,
        "seeds": sorted({row["seed"] for row in rows}),
        "controllers": sorted({row["controller"] for row in rows}),
        "opponents": sorted({row["opponent"] for row in rows}),
        "seats": sorted({row["seat"] for row in rows}),
    }
    integrity["complete"] = (
        integrity["actual_rows"] == integrity["expected_rows"]
        and integrity["missing_rows"] == 0
        and integrity["unexpected_rows"] == 0
        and integrity["duplicate_rows"] == 0
        and integrity["actual_scenarios"] == integrity["expected_scenarios"]
        and not bad_controller_sets
        and map_fields_consistent
        and invalid_dimensions == 0
        and invalid_turns == 0
        and integrity["controllers"] == sorted(CONTROLLERS)
        and integrity["opponents"] == sorted(OPPONENTS)
        and integrity["seats"] == [0, 1]
    )
    return integrity, dict(grouped)


def clustered_summary(rows: list[dict], field: str) -> dict:
    by_seed = defaultdict(list)
    for row in rows:
        by_seed[row["seed"]].append(row[field])
    return robust_summary(statistics.mean(values) for _, values in sorted(by_seed.items()))


def negative_mass(values) -> int:
    return sum(max(-value, 0) for value in values)


def pearson(left, right) -> float | None:
    left = list(left)
    right = list(right)
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = statistics.mean(left)
    right_mean = statistics.mean(right)
    numerator = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left, right)
    )
    left_scale = math.sqrt(sum((value - left_mean) ** 2 for value in left))
    right_scale = math.sqrt(sum((value - right_mean) ** 2 for value in right))
    if left_scale == 0 or right_scale == 0:
        return None
    return numerator / (left_scale * right_scale)


def controller_analysis(
    grouped: dict[tuple[int, int, str], dict[str, dict]], controller: str
) -> dict:
    pairs = []
    for (seed, seat, opponent), branches in sorted(grouped.items()):
        control = branches["resident"]
        candidate = branches[controller]
        pairs.append(
            {
                "seed": seed,
                "seat": seat,
                "opponent": opponent,
                "height": candidate["height"],
                "initial_plants": candidate["initial_plants"],
                "control_margin": control["margin"],
                "candidate_margin": candidate["margin"],
                "margin_delta": candidate["margin"] - control["margin"],
                "my_score_delta": candidate["my_score"] - control["my_score"],
                "opponent_score_delta": candidate["opponent_score"]
                - control["opponent_score"],
                "my_wood_delta": candidate["my_inv5"] - control["my_inv5"],
                "opponent_wood_delta": candidate["opponent_inv5"]
                - control["opponent_inv5"],
                "my_successful_plants_delta": candidate["my_successful_plants"]
                - control["my_successful_plants"],
                "opponent_successful_plants_delta": candidate[
                    "opponent_successful_plants"
                ]
                - control["opponent_successful_plants"],
                "max_my_workers_delta": candidate["max_my_workers"]
                - control["max_my_workers"],
                "candidate_max_workers": candidate["max_my_workers"],
                "candidate_my_score": candidate["my_score"],
                "candidate_opponent_score": candidate["opponent_score"],
                "candidate_my_wood": candidate["my_inv5"],
                "candidate_opponent_wood": candidate["opponent_inv5"],
                "candidate_plants": candidate["my_successful_plants"],
                "candidate_opponent_plants": candidate["opponent_successful_plants"],
                "candidate_final_turn": candidate["final_turn"],
                "candidate_chops": candidate["my_chop"],
                "candidate_harvests": candidate["my_harvest"],
                "candidate_train": candidate["my_train"],
            }
        )

    opponent_margin = {
        opponent: statistics.mean(
            row["margin_delta"] for row in pairs if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    opponent_score = {
        opponent: statistics.mean(
            row["opponent_score_delta"]
            for row in pairs
            if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    rich = [row for row in pairs if row["opponent"] in RICH_OPPONENTS]
    by_seed = defaultdict(list)
    for row in pairs:
        by_seed[row["seed"]].append(row)
    seed_geometry = [
        {
            "seed": seed,
            "height": values[0]["height"],
            "initial_plants": values[0]["initial_plants"],
            "margin_delta": statistics.mean(row["margin_delta"] for row in values),
            "own_score_delta": statistics.mean(row["my_score_delta"] for row in values),
            "opponent_score_delta": statistics.mean(
                row["opponent_score_delta"] for row in values
            ),
        }
        for seed, values in sorted(by_seed.items())
    ]
    control_margins = [row["control_margin"] for row in pairs]
    candidate_margins = [row["candidate_margin"] for row in pairs]
    margin = clustered_summary(pairs, "margin_delta")
    own_score = clustered_summary(pairs, "my_score_delta")
    opponent_score_summary = clustered_summary(pairs, "opponent_score_delta")
    tail = {
        "control_catastrophes": sum(value <= -100 for value in control_margins),
        "candidate_catastrophes": sum(value <= -100 for value in candidate_margins),
        "control_catastrophe_frequency": sum(value <= -100 for value in control_margins)
        / len(pairs),
        "candidate_catastrophe_frequency": sum(value <= -100 for value in candidate_margins)
        / len(pairs),
        "control_negative_margin_mass": negative_mass(control_margins),
        "candidate_negative_margin_mass": negative_mass(candidate_margins),
    }
    gates = {
        "complete_grid": len(pairs) == len(grouped),
        "mean_margin_delta_at_least_10": margin["mean"] >= 10,
        "margin_ci_lower_nonnegative": margin["ci95_normal"][0] >= 0,
        "own_score_delta_at_least_25": own_score["mean"] >= 25,
        "opponent_score_delta_at_most_5": opponent_score_summary["mean"] <= 5,
        "at_least_six_nonnegative_opponents": sum(
            value >= 0 for value in opponent_margin.values()
        )
        >= 6,
        "worst_opponent_at_least_minus_10": min(opponent_margin.values()) >= -10,
        "rich_margin_nonnegative": statistics.mean(
            row["margin_delta"] for row in rich
        )
        >= 0,
        "rich_opponent_score_delta_at_most_10": statistics.mean(
            row["opponent_score_delta"] for row in rich
        )
        <= 10,
        "catastrophe_frequency_not_increased": tail[
            "candidate_catastrophe_frequency"
        ]
        <= tail["control_catastrophe_frequency"],
        "negative_mass_not_increased": tail["candidate_negative_margin_mass"]
        <= tail["control_negative_margin_mass"],
    }
    return {
        "controller": controller,
        "cells": len(pairs),
        "seeds": len({row["seed"] for row in pairs}),
        "absolute": {
            "margin": clustered_summary(pairs, "candidate_margin"),
            "own_score": clustered_summary(pairs, "candidate_my_score"),
            "opponent_score": clustered_summary(pairs, "candidate_opponent_score"),
            "own_wood": clustered_summary(pairs, "candidate_my_wood"),
            "opponent_wood": clustered_summary(pairs, "candidate_opponent_wood"),
            "successful_plants": clustered_summary(pairs, "candidate_plants"),
            "opponent_successful_plants": clustered_summary(
                pairs, "candidate_opponent_plants"
            ),
            "maximum_workers": clustered_summary(pairs, "candidate_max_workers"),
            "final_turn": clustered_summary(pairs, "candidate_final_turn"),
            "chop_commands": clustered_summary(pairs, "candidate_chops"),
            "harvest_commands": clustered_summary(pairs, "candidate_harvests"),
            "train_commands": clustered_summary(pairs, "candidate_train"),
        },
        "paired_vs_resident": {
            "margin": margin,
            "own_score": own_score,
            "opponent_score": opponent_score_summary,
            "own_wood": clustered_summary(pairs, "my_wood_delta"),
            "opponent_wood": clustered_summary(pairs, "opponent_wood_delta"),
            "successful_plants": clustered_summary(
                pairs, "my_successful_plants_delta"
            ),
            "opponent_successful_plants": clustered_summary(
                pairs, "opponent_successful_plants_delta"
            ),
            "maximum_workers": clustered_summary(pairs, "max_my_workers_delta"),
        },
        "opponent_mean_margin_deltas": opponent_margin,
        "opponent_mean_score_deltas": opponent_score,
        "seat_mean_margin_deltas": {
            str(seat): statistics.mean(
                row["margin_delta"] for row in pairs if row["seat"] == seat
            )
            for seat in (0, 1)
        },
        "geometry": {
            "height_mean_margin_deltas": {
                str(height): statistics.mean(
                    row["margin_delta"] for row in pairs if row["height"] == height
                )
                for height in sorted({row["height"] for row in pairs})
            },
            "initial_plant_count_mean_margin_deltas": {
                str(count): statistics.mean(
                    row["margin_delta"]
                    for row in pairs
                    if row["initial_plants"] == count
                )
                for count in sorted({row["initial_plants"] for row in pairs})
            },
            "seed_correlation_height_with_margin_delta": pearson(
                (row["height"] for row in seed_geometry),
                (row["margin_delta"] for row in seed_geometry),
            ),
            "seed_correlation_initial_plants_with_margin_delta": pearson(
                (row["initial_plants"] for row in seed_geometry),
                (row["margin_delta"] for row in seed_geometry),
            ),
        },
        "nonnegative_opponent_means": sum(
            value >= 0 for value in opponent_margin.values()
        ),
        "worst_opponent": min(opponent_margin, key=opponent_margin.get),
        "worst_opponent_mean_margin_delta": min(opponent_margin.values()),
        "rich_block": {
            "cells": len(rich),
            "mean_margin_delta": statistics.mean(row["margin_delta"] for row in rich),
            "mean_own_score_delta": statistics.mean(
                row["my_score_delta"] for row in rich
            ),
            "mean_opponent_score_delta": statistics.mean(
                row["opponent_score_delta"] for row in rich
            ),
        },
        "tail": tail,
        "gates": gates,
        "passes_all_promotion_gates": controller != "resident" and all(gates.values()),
    }


def pareto_frontier(analyses: dict[str, dict]) -> list[str]:
    points = {
        label: (
            result["paired_vs_resident"]["own_score"]["mean"],
            result["paired_vs_resident"]["opponent_score"]["mean"],
        )
        for label, result in analyses.items()
    }
    frontier = []
    for label, (own, opponent) in points.items():
        dominated = any(
            other != label
            and other_own >= own
            and other_opponent <= opponent
            and (other_own > own or other_opponent < opponent)
            for other, (other_own, other_opponent) in points.items()
        )
        if not dominated:
            frontier.append(label)
    return sorted(frontier)


def denial_parent_comparisons(analyses: dict[str, dict]) -> dict:
    comparisons = {}
    for child, parent in DENIAL_PARENTS.items():
        child_own = analyses[child]["paired_vs_resident"]["own_score"]["mean"]
        parent_own = analyses[parent]["paired_vs_resident"]["own_score"]["mean"]
        child_opponent = analyses[child]["paired_vs_resident"]["opponent_score"]["mean"]
        parent_opponent = analyses[parent]["paired_vs_resident"]["opponent_score"]["mean"]
        child_opponent_wood = analyses[child]["paired_vs_resident"]["opponent_wood"]["mean"]
        parent_opponent_wood = analyses[parent]["paired_vs_resident"]["opponent_wood"]["mean"]
        child_opponent_plants = analyses[child]["paired_vs_resident"][
            "opponent_successful_plants"
        ]["mean"]
        parent_opponent_plants = analyses[parent]["paired_vs_resident"][
            "opponent_successful_plants"
        ]["mean"]
        comparisons[child] = {
            "parent": parent,
            "own_score_delta_child_minus_parent": child_own - parent_own,
            "opponent_score_delta_child_minus_parent": child_opponent - parent_opponent,
            "opponent_score_reduction_from_parent": parent_opponent - child_opponent,
            "opponent_wood_delta_child_minus_parent": child_opponent_wood
            - parent_opponent_wood,
            "opponent_successful_plants_delta_child_minus_parent": child_opponent_plants
            - parent_opponent_plants,
            "parent_own_score_gain_vs_resident": parent_own,
            "child_own_score_gain_vs_resident": child_own,
            "retained_parent_own_score_gain_fraction": (
                child_own / parent_own if parent_own > 0 else None
            ),
        }
    return comparisons


def representation_decision(
    analyses: dict[str, dict], frontier: list[str], denial: dict
) -> dict:
    productive = [
        label
        for label, result in analyses.items()
        if label != "resident"
        and result["paired_vs_resident"]["own_score"]["mean"] >= 25
    ]
    destructive_denial = [
        label
        for label, result in denial.items()
        if result["opponent_score_reduction_from_parent"] >= 10
        and result["retained_parent_own_score_gain_fraction"] is not None
        and result["retained_parent_own_score_gain_fraction"] < 0.5
    ]
    preserved_denial = [
        label
        for label, result in denial.items()
        if result["retained_parent_own_score_gain_fraction"] is not None
        and result["retained_parent_own_score_gain_fraction"] >= 0.5
        and analyses[label]["paired_vs_resident"]["opponent_score"]["mean"] <= 10
    ]
    resident_dominant = frontier == ["resident"]
    if productive and destructive_denial:
        selected = "coherent_joint_production_suppression_scheduler"
        reason = (
            "Productive families clear the own-score mechanism floor, while denial wrappers "
            "buy opponent suppression only by discarding more than half of their parent's "
            "production gain."
        )
    elif preserved_denial:
        selected = "fresh_optimizer_over_whole_denial_family_grammar"
        reason = (
            "A whole denial family retains at least half of its productive parent's gain and "
            "comes within five points of the opponent-score gate."
        )
    elif not productive:
        selected = "reopen_first_move_and_recipe_selection"
        reason = "No complete productive family adds the preregistered 25 own-score points."
    elif resident_dominant:
        selected = "resident_state_residual_value_only"
        reason = "The resident is production/suppression Pareto-dominant."
    else:
        selected = "coherent_joint_production_suppression_scheduler"
        reason = (
            "Productive value exists, but no frozen family preserves resident suppression; the "
            "remaining degree of freedom is a jointly optimized complete scheduler."
        )
    return {
        "selected_representation": selected,
        "reason": reason,
        "productive_families": productive,
        "destructive_denial_witnesses": destructive_denial,
        "preserved_denial_witnesses": preserved_denial,
        "resident_pareto_dominant": resident_dominant,
    }


def analyze(rows: list[dict], seed_start: int, seed_count: int) -> dict:
    integrity, grouped = validate_grid(rows, seed_start, seed_count)
    if not integrity["complete"]:
        return {
            "protocol": "D34 official-map complete-architecture transfer census",
            "integrity": integrity,
            "decision": "invalid_incomplete_grid",
        }
    analyses = {
        controller: controller_analysis(grouped, controller)
        for controller in CONTROLLERS
    }
    frontier = pareto_frontier(analyses)
    denial = denial_parent_comparisons(analyses)
    passers = [
        controller
        for controller in CONTROLLERS
        if analyses[controller]["passes_all_promotion_gates"]
    ]
    return {
        "protocol": "D34 official-map complete-architecture transfer census",
        "seed_start": seed_start,
        "seed_count": seed_count,
        "integrity": integrity,
        "controllers": analyses,
        "production_suppression_pareto_frontier": frontier,
        "denial_parent_comparisons": denial,
        "development_passers": passers,
        "confirmation_authorized": bool(passers),
        "representation_decision": representation_decision(analyses, frontier, denial),
        "decision": (
            "open_confirmation_for_best_passing_frozen_witness"
            if passers
            else "close_frozen_witnesses_and_advance_selected_representation"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=Path(
            "data/analysis/live-agent-6553250/"
            "d34-official-architecture-development-9100000-9100059.tsv"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "data/analysis/live-agent-6553250/"
            "d34-official-architecture-development-2026-07-20.json"
        ),
    )
    parser.add_argument("--seed-start", type=int, default=9_100_000)
    parser.add_argument("--seed-count", type=int, default=60)
    args = parser.parse_args()

    report = analyze(read_rows(args.input), args.seed_start, args.seed_count)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "decision": report["decision"],
        "integrity": report["integrity"]["complete"],
        "passers": report.get("development_passers", []),
        "frontier": report.get("production_suppression_pareto_frontier", []),
        "representation": report.get("representation_decision", {}).get(
            "selected_representation"
        ),
    }, sort_keys=True))
    return 0 if report["integrity"]["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
