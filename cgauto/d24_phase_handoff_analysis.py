#!/usr/bin/env python3
"""Analyze exact common-state complete-policy handoffs for D24."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import statistics


OPPONENTS = (
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
)
ALL_OPTIONS = ("private2", "ownership2", "hybrid3", "accumulate4", "norx3")
INTEGER_FIELDS = (
    "seed",
    "seat",
    "decision_turn",
    "reached_cut",
    "root_turn",
    "root_my_score",
    "root_opponent_score",
    "root_my_wood",
    "root_opponent_wood",
    "root_my_workers",
    "root_opponent_workers",
    "root_plants",
    "final_turn",
    "margin",
    "my_score",
    "opponent_score",
    "my_wood",
    "opponent_wood",
    "my_workers",
    "opponent_workers",
    "max_my_workers",
    "third_worker_turn",
    "train_commands",
    "plant_commands",
    "command_hash",
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
        for row in csv.DictReader(stream, delimiter="\t"):
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def scenario_key(row: dict) -> tuple[int, int, int, str]:
    return row["seed"], row["seat"], row["decision_turn"], row["opponent"]


def group_rows(rows: list[dict]) -> dict[tuple, dict[str, dict]]:
    grouped: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        key = scenario_key(row)
        if row["option"] in grouped[key]:
            raise ValueError(f"duplicate row for {key} / {row['option']}")
        grouped[key][row["option"]] = row
    return dict(grouped)


def parse_csv_list(value: str, cast=str) -> tuple:
    return tuple(cast(item) for item in value.split(",") if item)


def validate_grid(
    rows: list[dict],
    seed_start: int,
    seed_count: int,
    turns: tuple[int, ...],
    options: tuple[str, ...],
) -> tuple[dict, dict[tuple, dict[str, dict]]]:
    expected_seeds = set(range(seed_start, seed_start + seed_count))
    expected_branches = {"resident", *options}
    expected_scenarios = {
        (seed, seat, turn, opponent)
        for seed in expected_seeds
        for seat in (0, 1)
        for turn in turns
        for opponent in OPPONENTS
    }
    grouped = group_rows(rows)
    actual_scenarios = set(grouped)
    bad_branch_sets = {
        str(key): sorted(set(branches) ^ expected_branches)
        for key, branches in grouped.items()
        if set(branches) != expected_branches
    }
    root_consistent = True
    cut_consistent = True
    root_fields = (
        "root_turn",
        "root_my_score",
        "root_opponent_score",
        "root_my_wood",
        "root_opponent_wood",
        "root_my_workers",
        "root_opponent_workers",
        "root_plants",
    )
    for branches in grouped.values():
        values = list(branches.values())
        root_consistent &= all(
            all(row[field] == values[0][field] for field in root_fields)
            for row in values[1:]
        )
        cut_consistent &= all(
            row["reached_cut"] == values[0]["reached_cut"] for row in values[1:]
        )
    integrity = {
        "expected_rows": len(expected_scenarios) * len(expected_branches),
        "actual_rows": len(rows),
        "expected_scenarios": len(expected_scenarios),
        "actual_scenarios": len(grouped),
        "missing_scenarios": len(expected_scenarios - actual_scenarios),
        "unexpected_scenarios": len(actual_scenarios - expected_scenarios),
        "bad_branch_sets": bad_branch_sets,
        "root_fields_identical_across_branches": root_consistent,
        "reached_cut_identical_across_branches": cut_consistent,
        "opponents": sorted({row["opponent"] for row in rows}),
        "seeds": sorted({row["seed"] for row in rows}),
        "turns": sorted({row["decision_turn"] for row in rows}),
    }
    integrity["complete"] = (
        integrity["actual_rows"] == integrity["expected_rows"]
        and integrity["missing_scenarios"] == 0
        and integrity["unexpected_scenarios"] == 0
        and not bad_branch_sets
        and root_consistent
        and cut_consistent
        and integrity["opponents"] == sorted(OPPONENTS)
    )
    return integrity, grouped


def seed_cluster(rows: list[dict], field: str) -> list[float]:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["seed"]].append(row[field])
    return [statistics.mean(values) for _, values in sorted(grouped.items())]


def negative_mass(rows: list[dict]) -> float:
    return sum(max(-row["margin"], 0) for row in rows)


def analyze_combination(
    grouped: dict[tuple, dict[str, dict]], option: str, decision_turn: int
) -> dict:
    pairs = []
    for key, branches in grouped.items():
        if key[2] != decision_turn:
            continue
        control = branches["resident"]
        candidate = branches[option]
        row = {
            "seed": key[0],
            "seat": key[1],
            "opponent": key[3],
            "reached_cut": control["reached_cut"],
            "control_margin": control["margin"],
            "margin": candidate["margin"],
            "margin_delta": candidate["margin"] - control["margin"],
            "my_score_delta": candidate["my_score"] - control["my_score"],
            "opponent_score_delta": candidate["opponent_score"]
            - control["opponent_score"],
            "my_wood_delta": candidate["my_wood"] - control["my_wood"],
            "opponent_wood_delta": candidate["opponent_wood"]
            - control["opponent_wood"],
            "control_margin_value": control["margin"],
            "candidate_margin_value": candidate["margin"],
            "control_max_workers": control["max_my_workers"],
            "candidate_max_workers": candidate["max_my_workers"],
            "candidate_final_workers": candidate["my_workers"],
            "candidate_third_worker_turn": candidate["third_worker_turn"],
            "command_diff": candidate["command_hash"] != control["command_hash"],
        }
        pairs.append(row)

    seed_margin = seed_cluster(pairs, "margin_delta")
    seed_score = seed_cluster(pairs, "my_score_delta")
    opponent_means = {
        opponent: statistics.mean(
            row["margin_delta"] for row in pairs if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    catastrophic_control = [row for row in pairs if row["control_margin"] <= -100]
    control_rows = [
        {"margin": row["control_margin_value"]} for row in pairs
    ]
    candidate_rows = [
        {"margin": row["candidate_margin_value"]} for row in pairs
    ]
    control_catastrophes = sum(row["margin"] <= -100 for row in control_rows)
    candidate_catastrophes = sum(row["margin"] <= -100 for row in candidate_rows)
    control_mass = negative_mass(control_rows)
    candidate_mass = negative_mass(candidate_rows)
    reached = [row for row in pairs if row["reached_cut"]]
    third_turns = [
        row["candidate_third_worker_turn"]
        for row in reached
        if row["candidate_third_worker_turn"] >= 0
    ]
    margin_summary = robust_summary(seed_margin)
    score_summary = robust_summary(seed_score)
    report = {
        "option": option,
        "decision_turn": decision_turn,
        "cells": len(pairs),
        "seeds": len(seed_margin),
        "reached_cut_cells": len(reached),
        "reached_cut_rate": len(reached) / len(pairs),
        "command_difference_rate": sum(row["command_diff"] for row in pairs)
        / len(pairs),
        "seed_clustered_margin_delta": margin_summary,
        "seed_clustered_own_score_delta": score_summary,
        "cell_margin_delta": robust_summary(row["margin_delta"] for row in pairs),
        "cell_opponent_score_delta": robust_summary(
            row["opponent_score_delta"] for row in pairs
        ),
        "cell_own_wood_delta": robust_summary(row["my_wood_delta"] for row in pairs),
        "cell_opponent_wood_delta": robust_summary(
            row["opponent_wood_delta"] for row in pairs
        ),
        "opponent_mean_margin_deltas": opponent_means,
        "nonnegative_opponent_means": sum(value >= 0 for value in opponent_means.values()),
        "worst_opponent": min(opponent_means, key=opponent_means.get),
        "worst_opponent_mean_delta": min(opponent_means.values()),
        "control_catastrophic_cells": len(catastrophic_control),
        "control_catastrophic_cell_margin_delta": robust_summary(
            row["margin_delta"] for row in catastrophic_control
        ),
        "tail": {
            "control_catastrophic_frequency": control_catastrophes / len(pairs),
            "candidate_catastrophic_frequency": candidate_catastrophes / len(pairs),
            "control_negative_margin_mass": control_mass,
            "candidate_negative_margin_mass": candidate_mass,
            "candidate_to_control_negative_mass_ratio": (
                candidate_mass / control_mass if control_mass else None
            ),
        },
        "workforce": {
            "control_mean_max_workers": statistics.mean(
                row["control_max_workers"] for row in pairs
            ),
            "candidate_mean_max_workers": statistics.mean(
                row["candidate_max_workers"] for row in pairs
            ),
            "candidate_mean_final_workers": statistics.mean(
                row["candidate_final_workers"] for row in pairs
            ),
            "candidate_cells_reaching_three_workers": len(third_turns),
            "candidate_median_third_worker_turn": (
                statistics.median(third_turns) if third_turns else None
            ),
        },
    }
    report["gates"] = {
        "mean_margin_at_least_5": margin_summary["mean"] >= 5,
        "trimmed_margin_at_least_2": margin_summary["trimmed_5pct_mean"] >= 2,
        "own_score_at_least_5": score_summary["mean"] >= 5,
        "six_of_eight_opponents_nonnegative": report["nonnegative_opponent_means"] >= 6,
        "worst_opponent_at_least_minus_5": report["worst_opponent_mean_delta"] >= -5,
        "positive_control_catastrophe_delta": bool(catastrophic_control)
        and report["control_catastrophic_cell_margin_delta"]["mean"] > 0,
        "catastrophic_frequency_not_higher": candidate_catastrophes <= control_catastrophes,
        "negative_margin_mass_not_higher": candidate_mass <= control_mass,
        "discovery_ci_lower_above_minus_2": margin_summary["ci95_normal"][0] > -2,
        "confirmation_ci_lower_above_zero": margin_summary["ci95_normal"][0] > 0,
    }
    report["discovery_passed"] = all(
        value
        for name, value in report["gates"].items()
        if name != "confirmation_ci_lower_above_zero"
    )
    report["confirmation_passed"] = report["discovery_passed"] and report["gates"][
        "confirmation_ci_lower_above_zero"
    ]
    return report


def discovery_choice(reports: list[dict]) -> dict | None:
    passing = [report for report in reports if report["discovery_passed"]]
    if not passing:
        return None
    return sorted(
        passing,
        key=lambda report: (
            -report["worst_opponent_mean_delta"],
            report["tail"]["candidate_catastrophic_frequency"],
            -report["seed_clustered_margin_delta"]["mean"],
            -report["decision_turn"],
            report["option"],
        ),
    )[0]


def activation_summary(
    grouped: dict[tuple, dict[str, dict]], options: tuple[str, ...]
) -> dict:
    result = {}
    for option in options:
        comparisons = [
            branches[option]["command_hash"] != branches["resident"]["command_hash"]
            for branches in grouped.values()
        ]
        result[option] = {
            "scenario_cut_cells": len(comparisons),
            "different_command_streams": sum(comparisons),
            "difference_rate": sum(comparisons) / len(comparisons),
            "passes_20pct": sum(comparisons) / len(comparisons) >= 0.20,
        }
    return result


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("smoke", "discovery", "confirmation"), required=True)
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--seed-count", type=int, required=True)
    parser.add_argument("--turns", default="75,100,125,150")
    parser.add_argument("--options", default=",".join(ALL_OPTIONS))
    parser.add_argument("--repeat", type=Path)
    args = parser.parse_args()

    turns = parse_csv_list(args.turns, int)
    options = parse_csv_list(args.options)
    if len(set(turns)) != len(turns) or not turns:
        raise SystemExit("--turns must contain unique values")
    if len(set(options)) != len(options) or not options:
        raise SystemExit("--options must contain unique values")
    unknown = sorted(set(options) - set(ALL_OPTIONS))
    if unknown:
        raise SystemExit("unknown options: " + ", ".join(unknown))

    rows = read_rows(args.input)
    integrity, grouped = validate_grid(
        rows, args.seed_start, args.seed_count, turns, options
    )
    if args.repeat:
        integrity["repeat_path"] = str(args.repeat)
        integrity["repeat_byte_identical"] = (
            args.input.read_bytes() == args.repeat.read_bytes()
        )
    else:
        integrity["repeat_path"] = None
        integrity["repeat_byte_identical"] = None
    activation = activation_summary(grouped, options)
    integrity["all_options_pass_20pct_activation"] = all(
        report["passes_20pct"] for report in activation.values()
    )
    integrity["readiness_passed"] = (
        integrity["complete"]
        and integrity["all_options_pass_20pct_activation"]
        and (args.mode != "smoke" or integrity["repeat_byte_identical"] is True)
    )

    reports = [
        analyze_combination(grouped, option, turn)
        for option in options
        for turn in turns
    ]
    selected = discovery_choice(reports) if args.mode == "discovery" else None
    if args.mode == "smoke":
        decision = {
            "open_discovery": integrity["readiness_passed"],
            "select_from_smoke_outcomes": False,
            "selected": None,
        }
    elif args.mode == "discovery":
        decision = {
            "open_confirmation": integrity["readiness_passed"] and selected is not None,
            "selected": (
                {
                    "option": selected["option"],
                    "decision_turn": selected["decision_turn"],
                    "discovery_passed": selected["discovery_passed"],
                }
                if selected
                else None
            ),
        }
    else:
        if len(reports) != 1:
            raise SystemExit("confirmation requires exactly one option and one decision turn")
        decision = {
            "deployment_feasibility_authorized": integrity["readiness_passed"]
            and reports[0]["confirmation_passed"],
            "selected": {
                "option": reports[0]["option"],
                "decision_turn": reports[0]["decision_turn"],
                "confirmation_passed": reports[0]["confirmation_passed"],
            },
        }

    payload = {
        "schema": 1,
        "scope": (
            "exact generated-map common-state terminal continuations; complete resident control "
            "and cold-start whole-side macro policies; no Arena or submission action"
        ),
        "mode": args.mode,
        "source": str(args.input),
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "decision_turns": turns,
        "options": options,
        "opponents": OPPONENTS,
        "integrity": integrity,
        "activation": activation,
        "combinations": reports,
        "decision": decision,
    }
    save(args.output, payload)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "integrity": integrity,
                "activation": activation,
                "passing_combinations": [
                    {
                        "option": report["option"],
                        "turn": report["decision_turn"],
                        "mean": report["seed_clustered_margin_delta"]["mean"],
                        "ci": report["seed_clustered_margin_delta"]["ci95_normal"],
                        "worst_opponent": report["worst_opponent_mean_delta"],
                    }
                    for report in reports
                    if report["discovery_passed"]
                ],
                "decision": decision,
            },
            indent=1,
        )
    )
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
