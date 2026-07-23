#!/usr/bin/env python3
"""Analyze D26 bounded ownership-farm production pulses."""

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
INTEGER_FIELDS = (
    "seed",
    "seat",
    "reached_cut",
    "exit_turn",
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
    "farm_turns",
    "restart_turns",
    "farm_train_commands",
    "farm_plant_commands",
    "restart_train_commands",
    "restart_plant_commands",
    "command_hash",
)
ROOT_FIELDS = (
    "root_turn",
    "root_my_score",
    "root_opponent_score",
    "root_my_wood",
    "root_opponent_wood",
    "root_my_workers",
    "root_opponent_workers",
    "root_plants",
)
CONTROL_REFERENCE_FIELDS = (
    "reached_cut",
    *ROOT_FIELDS,
    "final_turn",
    "margin",
    "my_score",
    "opponent_score",
    "my_wood",
    "opponent_wood",
    "my_workers",
    "opponent_workers",
    "max_my_workers",
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
        reader = csv.DictReader(stream, delimiter="\t")
        missing = set(INTEGER_FIELDS) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path}: missing fields: {', '.join(sorted(missing))}")
        for row in reader:
            for field in INTEGER_FIELDS:
                row[field] = int(row[field])
            rows.append(row)
    return rows


def scenario_key(row: dict) -> tuple[int, int, str]:
    return row["seed"], row["seat"], row["opponent"]


def group_rows(rows: list[dict]) -> dict[tuple, dict[str, dict]]:
    grouped: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for row in rows:
        key = scenario_key(row)
        if row["option"] in grouped[key]:
            raise ValueError(f"duplicate row for {key} / {row['option']}")
        grouped[key][row["option"]] = row
    return dict(grouped)


def parse_csv_list(value: str, cast=int) -> tuple:
    return tuple(cast(item) for item in value.split(",") if item)


def validate_grid(
    rows: list[dict], seed_start: int, seed_count: int, exits: tuple[int, ...]
) -> tuple[dict, dict[tuple, dict[str, dict]]]:
    expected_seeds = set(range(seed_start, seed_start + seed_count))
    expected_options = {"resident", *(f"pulse{exit_turn}" for exit_turn in exits)}
    expected_scenarios = {
        (seed, seat, opponent)
        for seed in expected_seeds
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    grouped = group_rows(rows)
    actual_scenarios = set(grouped)
    bad_branch_sets = {
        str(key): sorted(set(branches) ^ expected_options)
        for key, branches in grouped.items()
        if set(branches) != expected_options
    }
    bad_exit_labels = []
    root_consistent = True
    cut_consistent = True
    legal_terminal_shape = True
    for key, branches in grouped.items():
        values = list(branches.values())
        root_consistent &= all(
            all(row[field] == values[0][field] for field in ROOT_FIELDS)
            for row in values[1:]
        )
        cut_consistent &= all(
            row["reached_cut"] == values[0]["reached_cut"] for row in values[1:]
        )
        for label, row in branches.items():
            expected_exit = -1 if label == "resident" else int(label.removeprefix("pulse"))
            if row["exit_turn"] != expected_exit:
                bad_exit_labels.append([*key, label, row["exit_turn"]])
            legal_terminal_shape &= (
                row["root_turn"] <= row["final_turn"] <= 301
                and row["my_score"] >= 0
                and row["opponent_score"] >= 0
                and row["my_wood"] >= 0
                and row["opponent_wood"] >= 0
                and row["my_workers"] >= 0
                and row["opponent_workers"] >= 0
                and row["max_my_workers"] >= row["my_workers"]
            )
            if row["reached_cut"]:
                legal_terminal_shape &= row["root_turn"] == 75 and row["final_turn"] > 75

    integrity = {
        "expected_rows": len(expected_scenarios) * len(expected_options),
        "actual_rows": len(rows),
        "expected_scenarios": len(expected_scenarios),
        "actual_scenarios": len(grouped),
        "missing_scenarios": len(expected_scenarios - actual_scenarios),
        "unexpected_scenarios": len(actual_scenarios - expected_scenarios),
        "bad_branch_sets": bad_branch_sets,
        "bad_exit_labels": bad_exit_labels,
        "root_fields_identical_across_branches": root_consistent,
        "reached_cut_identical_across_branches": cut_consistent,
        "legal_terminal_shape": legal_terminal_shape,
        "opponents": sorted({row["opponent"] for row in rows}),
        "seeds": sorted({row["seed"] for row in rows}),
    }
    integrity["complete"] = (
        integrity["actual_rows"] == integrity["expected_rows"]
        and integrity["missing_scenarios"] == 0
        and integrity["unexpected_scenarios"] == 0
        and not bad_branch_sets
        and not bad_exit_labels
        and root_consistent
        and cut_consistent
        and legal_terminal_shape
        and integrity["opponents"] == sorted(OPPONENTS)
    )
    return integrity, grouped


def validate_control_references(
    grouped: dict[tuple, dict[str, dict]], paths: list[Path]
) -> dict:
    if not paths:
        return {
            "paths": [],
            "expected_controls": len(grouped),
            "matched_controls": None,
            "mismatches": None,
            "complete_match": None,
        }
    references = {}
    duplicate_keys = []
    for path in paths:
        with path.open(newline="") as stream:
            for raw in csv.DictReader(stream, delimiter="\t"):
                if raw.get("option") != "resident" or int(raw.get("decision_turn", 75)) != 75:
                    continue
                key = (int(raw["seed"]), int(raw["seat"]), raw["opponent"])
                if key in references:
                    duplicate_keys.append(key)
                references[key] = raw

    mismatches = []
    matched = 0
    for key, branches in grouped.items():
        reference = references.get(key)
        if reference is None:
            mismatches.append({"key": key, "field": "missing_reference"})
            continue
        control = branches["resident"]
        cell_matches = True
        for field in CONTROL_REFERENCE_FIELDS:
            expected = int(reference[field])
            if control[field] != expected:
                cell_matches = False
                mismatches.append(
                    {
                        "key": key,
                        "field": field,
                        "actual": control[field],
                        "reference": expected,
                    }
                )
        matched += cell_matches
    complete = matched == len(grouped) and not mismatches and not duplicate_keys
    return {
        "paths": [str(path) for path in paths],
        "reference_controls": len(references),
        "expected_controls": len(grouped),
        "matched_controls": matched,
        "duplicate_reference_keys": duplicate_keys,
        "mismatches": mismatches[:50],
        "mismatch_count": len(mismatches),
        "complete_match": complete,
    }


def seed_cluster(rows: list[dict], field: str) -> list[float]:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["seed"]].append(row[field])
    return [statistics.mean(values) for _, values in sorted(grouped.items())]


def negative_mass(values) -> int:
    return sum(max(-value, 0) for value in values)


def analyze_exit(grouped: dict[tuple, dict[str, dict]], exit_turn: int) -> dict:
    label = f"pulse{exit_turn}"
    pairs = []
    for key, branches in grouped.items():
        control = branches["resident"]
        candidate = branches[label]
        pairs.append(
            {
                "seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "reached_cut": bool(control["reached_cut"]),
                "control_margin": control["margin"],
                "candidate_margin": candidate["margin"],
                "margin_delta": candidate["margin"] - control["margin"],
                "my_score_delta": candidate["my_score"] - control["my_score"],
                "opponent_score_delta": candidate["opponent_score"]
                - control["opponent_score"],
                "my_wood_delta": candidate["my_wood"] - control["my_wood"],
                "opponent_wood_delta": candidate["opponent_wood"]
                - control["opponent_wood"],
                "control_max_workers": control["max_my_workers"],
                "candidate_max_workers": candidate["max_my_workers"],
                "candidate_final_workers": candidate["my_workers"],
                "farm_turns": candidate["farm_turns"],
                "restart_turns": candidate["restart_turns"],
                "farm_train_commands": candidate["farm_train_commands"],
                "farm_plant_commands": candidate["farm_plant_commands"],
                "restart_train_commands": candidate["restart_train_commands"],
                "restart_plant_commands": candidate["restart_plant_commands"],
                "command_diff": candidate["command_hash"] != control["command_hash"],
            }
        )

    reached = [row for row in pairs if row["reached_cut"]]
    margin_summary = robust_summary(seed_cluster(pairs, "margin_delta"))
    score_summary = robust_summary(seed_cluster(pairs, "my_score_delta"))
    opponent_means = {
        opponent: statistics.mean(
            row["margin_delta"] for row in pairs if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    catastrophic_control = [row for row in pairs if row["control_margin"] <= -100]
    control_catastrophes = sum(row["control_margin"] <= -100 for row in pairs)
    candidate_catastrophes = sum(row["candidate_margin"] <= -100 for row in pairs)
    control_mass = negative_mass(row["control_margin"] for row in pairs)
    candidate_mass = negative_mass(row["candidate_margin"] for row in pairs)
    mass_ratio = candidate_mass / control_mass if control_mass else (0.0 if not candidate_mass else None)
    both_phases = sum(row["farm_turns"] > 0 and row["restart_turns"] > 0 for row in reached)
    both_phase_rate = both_phases / len(reached) if reached else 0.0

    report = {
        "exit_turn": exit_turn,
        "scheduled_farm_turns": exit_turn - 75,
        "cells": len(pairs),
        "seeds": margin_summary["n"],
        "reached_cut_cells": len(reached),
        "reached_cut_rate": len(reached) / len(pairs),
        "command_difference_rate_on_reached": (
            sum(row["command_diff"] for row in reached) / len(reached) if reached else 0.0
        ),
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
            "candidate_to_control_negative_mass_ratio": mass_ratio,
        },
        "phase_execution": {
            "cells_executing_both_phases": both_phases,
            "both_phase_rate": both_phase_rate,
            "mean_farm_turns": statistics.mean(row["farm_turns"] for row in reached),
            "mean_restart_turns": statistics.mean(row["restart_turns"] for row in reached),
            "full_scheduled_farm_rate": sum(
                row["farm_turns"] == exit_turn - 75 for row in reached
            )
            / len(reached),
        },
        "actions": {
            field: robust_summary(row[field] for row in reached)
            for field in (
                "farm_train_commands",
                "farm_plant_commands",
                "restart_train_commands",
                "restart_plant_commands",
            )
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
        },
    }
    report["gates"] = {
        "mean_margin_at_least_5": margin_summary["mean"] >= 5,
        "trimmed_margin_at_least_3": margin_summary["trimmed_5pct_mean"] >= 3,
        "ci95_lower_above_zero": margin_summary["ci95_normal"][0] > 0,
        "own_score_at_least_5": score_summary["mean"] >= 5,
        "six_of_eight_opponents_nonnegative": report["nonnegative_opponent_means"] >= 6,
        "worst_opponent_at_least_minus_5": report["worst_opponent_mean_delta"] >= -5,
        "positive_control_catastrophe_delta": bool(catastrophic_control)
        and report["control_catastrophic_cell_margin_delta"]["mean"] > 0,
        "catastrophic_frequency_not_higher": candidate_catastrophes <= control_catastrophes,
        "negative_margin_mass_not_higher": candidate_mass <= control_mass,
        "both_phases_execute_at_least_95pct": both_phase_rate >= 0.95,
    }
    report["passed"] = all(report["gates"].values())
    return report


def discovery_choice(reports: list[dict]) -> dict | None:
    passing = [report for report in reports if report["passed"]]
    if not passing:
        return None

    def key(report: dict):
        ratio = report["tail"]["candidate_to_control_negative_mass_ratio"]
        return (
            -report["worst_opponent_mean_delta"],
            math.inf if ratio is None else ratio,
            -report["seed_clustered_margin_delta"]["mean"],
            report["exit_turn"],
        )

    return min(passing, key=key)


def save(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--mode", choices=("smoke", "discovery", "confirmation"), required=True
    )
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--seed-count", type=int, required=True)
    parser.add_argument("--exits", default="100,125,150")
    parser.add_argument("--repeat", type=Path)
    parser.add_argument("--control-reference", type=Path, action="append", default=[])
    args = parser.parse_args()

    exits = parse_csv_list(args.exits)
    if not exits or len(set(exits)) != len(exits):
        raise SystemExit("--exits must contain unique values")
    if args.mode == "confirmation" and len(exits) != 1:
        raise SystemExit("confirmation requires exactly one frozen exit")

    rows = read_rows(args.input)
    integrity, grouped = validate_grid(rows, args.seed_start, args.seed_count, exits)
    if args.repeat:
        integrity["repeat_path"] = str(args.repeat)
        integrity["repeat_byte_identical"] = args.input.read_bytes() == args.repeat.read_bytes()
    else:
        integrity["repeat_path"] = None
        integrity["repeat_byte_identical"] = None
    control_reference = validate_control_references(grouped, args.control_reference)
    integrity["control_reference"] = control_reference

    reports = [analyze_exit(grouped, exit_turn) for exit_turn in exits]
    activation = {
        str(report["exit_turn"]): {
            "reached_cut_cells": report["reached_cut_cells"],
            "difference_rate": report["command_difference_rate_on_reached"],
            "passes_20pct": report["command_difference_rate_on_reached"] >= 0.20,
        }
        for report in reports
    }
    integrity["all_exits_pass_20pct_activation"] = all(
        item["passes_20pct"] for item in activation.values()
    )
    integrity["readiness_passed"] = (
        integrity["complete"]
        and integrity["all_exits_pass_20pct_activation"]
        and (args.mode != "smoke" or integrity["repeat_byte_identical"] is True)
        and (
            control_reference["complete_match"] is not False
        )
    )

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
                    "exit_turn": selected["exit_turn"],
                    "passed": selected["passed"],
                }
                if selected
                else None
            ),
        }
    else:
        report = reports[0]
        decision = {
            "deployment_feasibility_authorized": integrity["readiness_passed"]
            and report["passed"],
            "selected": {
                "exit_turn": report["exit_turn"],
                "confirmation_passed": report["passed"],
            },
        }

    payload = {
        "schema": 1,
        "scope": (
            "exact generated-map common-state terminal continuations; bounded ownership2 pulse "
            "followed by a cold visible-state resident restart; no Arena or submission action"
        ),
        "mode": args.mode,
        "source": str(args.input),
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "exits": exits,
        "opponents": OPPONENTS,
        "integrity": integrity,
        "activation": activation,
        "exits_analysis": reports,
        "decision": decision,
    }
    save(args.output, payload)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "integrity": integrity,
                "activation": activation,
                "reports": [
                    {
                        "exit_turn": report["exit_turn"],
                        "mean": report["seed_clustered_margin_delta"]["mean"],
                        "trimmed": report["seed_clustered_margin_delta"][
                            "trimmed_5pct_mean"
                        ],
                        "ci": report["seed_clustered_margin_delta"]["ci95_normal"],
                        "own_score": report["seed_clustered_own_score_delta"]["mean"],
                        "worst_opponent": report["worst_opponent_mean_delta"],
                        "negative_mass_ratio": report["tail"][
                            "candidate_to_control_negative_mass_ratio"
                        ],
                        "passed": report["passed"],
                        "failed_gates": [
                            name for name, passed in report["gates"].items() if not passed
                        ],
                    }
                    for report in reports
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
