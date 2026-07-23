#!/usr/bin/env python3
"""Analyze D28 resident-state retention at the frozen turn-150 handoff."""

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
ALL_OPTIONS = ("resident", "farm", "cold", "paused", "shadow")
HANDOFF_OPTIONS = ("farm", "cold", "paused", "shadow")
TEST_OPTIONS = ("paused", "shadow")
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
    "handoff_turn",
    "handoff_my_score",
    "handoff_opponent_score",
    "handoff_my_wood",
    "handoff_opponent_wood",
    "handoff_my_workers",
    "handoff_opponent_workers",
    "handoff_plants",
    "farm_prefix_hash",
    "shadow_turns",
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
HANDOFF_FIELDS = (
    "handoff_turn",
    "handoff_my_score",
    "handoff_opponent_score",
    "handoff_my_wood",
    "handoff_opponent_wood",
    "handoff_my_workers",
    "handoff_opponent_workers",
    "handoff_plants",
    "farm_prefix_hash",
)
REFERENCE_FIELDS = (
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
        return {"n": 0, "mean": None, "ci95_normal": [None, None]}
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


def parse_options(value: str) -> tuple[str, ...]:
    options = tuple(item for item in value.split(",") if item)
    if not options or len(set(options)) != len(options):
        raise ValueError("options must be nonempty and unique")
    unknown = sorted(set(options) - set(ALL_OPTIONS))
    if unknown:
        raise ValueError("unknown options: " + ", ".join(unknown))
    return options


def validate_grid(
    rows: list[dict], seed_start: int, seed_count: int, options: tuple[str, ...]
) -> tuple[dict, dict[tuple, dict[str, dict]]]:
    expected_scenarios = {
        (seed, seat, opponent)
        for seed in range(seed_start, seed_start + seed_count)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    expected_options = set(options)
    grouped = group_rows(rows)
    bad_branch_sets = {
        str(key): sorted(set(branches) ^ expected_options)
        for key, branches in grouped.items()
        if set(branches) != expected_options
    }
    root_consistent = True
    cut_consistent = True
    handoff_consistent = True
    exit_labels_valid = True
    telemetry_valid = True
    terminal_shape_valid = True
    for branches in grouped.values():
        values = list(branches.values())
        root_consistent &= all(
            all(row[field] == values[0][field] for field in ROOT_FIELDS)
            for row in values[1:]
        )
        cut_consistent &= all(
            row["reached_cut"] == values[0]["reached_cut"] for row in values[1:]
        )
        handoff_rows = [branches[name] for name in HANDOFF_OPTIONS if name in branches]
        if len(handoff_rows) > 1:
            handoff_consistent &= all(
                all(row[field] == handoff_rows[0][field] for field in HANDOFF_FIELDS)
                for row in handoff_rows[1:]
            )
        for label, row in branches.items():
            exit_labels_valid &= row["exit_turn"] == (
                150 if label in ("cold", "paused", "shadow") else -1
            )
            terminal_shape_valid &= (
                row["root_turn"] <= row["final_turn"] <= 301
                and row["my_score"] >= 0
                and row["opponent_score"] >= 0
                and row["my_wood"] >= 0
                and row["opponent_wood"] >= 0
                and row["max_my_workers"] >= row["my_workers"]
            )
            if label in HANDOFF_OPTIONS and row["reached_cut"]:
                telemetry_valid &= row["handoff_turn"] == 150
            if label == "resident":
                telemetry_valid &= row["handoff_turn"] == -1 and row["farm_prefix_hash"] == 0
            if label == "shadow":
                telemetry_valid &= row["shadow_turns"] == 75
            else:
                telemetry_valid &= row["shadow_turns"] == 0

    integrity = {
        "expected_rows": len(expected_scenarios) * len(options),
        "actual_rows": len(rows),
        "expected_scenarios": len(expected_scenarios),
        "actual_scenarios": len(grouped),
        "missing_scenarios": len(expected_scenarios - set(grouped)),
        "unexpected_scenarios": len(set(grouped) - expected_scenarios),
        "bad_branch_sets": bad_branch_sets,
        "root_fields_identical": root_consistent,
        "reached_cut_identical": cut_consistent,
        "turn150_state_and_farm_hash_identical": handoff_consistent,
        "exit_labels_valid": exit_labels_valid,
        "phase_telemetry_valid": telemetry_valid,
        "legal_terminal_shape": terminal_shape_valid,
        "opponents": sorted({row["opponent"] for row in rows}),
        "seeds": sorted({row["seed"] for row in rows}),
    }
    integrity["complete"] = (
        integrity["actual_rows"] == integrity["expected_rows"]
        and integrity["actual_scenarios"] == len(expected_scenarios)
        and not integrity["missing_scenarios"]
        and not integrity["unexpected_scenarios"]
        and not bad_branch_sets
        and root_consistent
        and cut_consistent
        and handoff_consistent
        and exit_labels_valid
        and telemetry_valid
        and terminal_shape_valid
        and integrity["opponents"] == sorted(OPPONENTS)
    )
    return integrity, grouped


def read_reference(paths: list[Path], source: str) -> dict[tuple, dict[str, dict]]:
    indexed: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for path in paths:
        with path.open(newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                if source == "d24" and int(row["decision_turn"]) != 75:
                    continue
                mapping = (
                    {"resident": "resident", "ownership2": "farm"}
                    if source == "d24"
                    else {"resident": "resident", "pulse150": "cold"}
                )
                target = mapping.get(row["option"])
                if target is None:
                    continue
                key = (int(row["seed"]), int(row["seat"]), row["opponent"])
                if target in indexed[key]:
                    raise ValueError(f"duplicate {source} reference: {key} / {target}")
                indexed[key][target] = row
    return dict(indexed)


def validate_references(
    grouped: dict[tuple, dict[str, dict]], d24_paths: list[Path], d26_paths: list[Path]
) -> dict:
    if not d24_paths and not d26_paths:
        return {"paths": [], "checks": None, "mismatches": None, "complete_match": None}
    sources = []
    if d24_paths:
        sources.append(("d24", read_reference(d24_paths, "d24"), ("resident", "farm")))
    if d26_paths:
        sources.append(("d26", read_reference(d26_paths, "d26"), ("resident", "cold")))
    checks = 0
    mismatches = []
    for source, reference, targets in sources:
        for key, branches in grouped.items():
            for target in targets:
                if target not in branches:
                    continue
                raw = reference.get(key, {}).get(target)
                if raw is None:
                    mismatches.append({"source": source, "key": key, "option": target, "field": "missing"})
                    continue
                checks += 1
                for field in REFERENCE_FIELDS:
                    if branches[target][field] != int(raw[field]):
                        mismatches.append(
                            {
                                "source": source,
                                "key": key,
                                "option": target,
                                "field": field,
                                "actual": branches[target][field],
                                "reference": int(raw[field]),
                            }
                        )
    expected_checks = sum(
        sum(target in branches for target in targets)
        for _, _, targets in sources
        for branches in grouped.values()
    )
    return {
        "paths": [str(path) for path in [*d24_paths, *d26_paths]],
        "checks": checks,
        "expected_checks": expected_checks,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:50],
        "complete_match": checks == expected_checks and not mismatches,
    }


def seed_cluster(rows: list[dict], field: str) -> list[float]:
    grouped: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        grouped[row["seed"]].append(row[field])
    return [statistics.mean(values) for _, values in sorted(grouped.items())]


def negative_mass(values) -> int:
    return sum(max(-value, 0) for value in values)


def analyze_option(
    grouped: dict[tuple, dict[str, dict]], option: str, require_cold: bool
) -> dict:
    pairs = []
    for key, branches in grouped.items():
        resident = branches["resident"]
        candidate = branches[option]
        cold = branches.get("cold")
        pairs.append(
            {
                "seed": key[0],
                "seat": key[1],
                "opponent": key[2],
                "resident_margin": resident["margin"],
                "candidate_margin": candidate["margin"],
                "margin_delta": candidate["margin"] - resident["margin"],
                "my_score_delta": candidate["my_score"] - resident["my_score"],
                "opponent_score_delta": candidate["opponent_score"] - resident["opponent_score"],
                "my_wood_delta": candidate["my_wood"] - resident["my_wood"],
                "opponent_wood_delta": candidate["opponent_wood"] - resident["opponent_wood"],
                "cold_margin_delta": (
                    candidate["margin"] - cold["margin"] if cold is not None else None
                ),
                "command_diff_cold": (
                    candidate["command_hash"] != cold["command_hash"] if cold is not None else None
                ),
                "command_diff_resident": candidate["command_hash"] != resident["command_hash"],
                "farm_turns": candidate["farm_turns"],
                "restart_turns": candidate["restart_turns"],
                "farm_train_commands": candidate["farm_train_commands"],
                "farm_plant_commands": candidate["farm_plant_commands"],
                "restart_train_commands": candidate["restart_train_commands"],
                "restart_plant_commands": candidate["restart_plant_commands"],
                "resident_max_workers": resident["max_my_workers"],
                "candidate_max_workers": candidate["max_my_workers"],
            }
        )

    margin = robust_summary(seed_cluster(pairs, "margin_delta"))
    own_score = robust_summary(seed_cluster(pairs, "my_score_delta"))
    cold_margin = (
        robust_summary(seed_cluster(pairs, "cold_margin_delta")) if require_cold else None
    )
    opponent_means = {
        opponent: statistics.mean(
            row["margin_delta"] for row in pairs if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    catastrophic_control = [row for row in pairs if row["resident_margin"] <= -100]
    resident_catastrophes = sum(row["resident_margin"] <= -100 for row in pairs)
    candidate_catastrophes = sum(row["candidate_margin"] <= -100 for row in pairs)
    resident_mass = negative_mass(row["resident_margin"] for row in pairs)
    candidate_mass = negative_mass(row["candidate_margin"] for row in pairs)
    both_phase_rate = sum(
        row["farm_turns"] > 0 and row["restart_turns"] > 0 for row in pairs
    ) / len(pairs)
    report = {
        "option": option,
        "cells": len(pairs),
        "seeds": margin["n"],
        "against_resident": {
            "seed_clustered_margin_delta": margin,
            "seed_clustered_own_score_delta": own_score,
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
            "resident_catastrophic_cells": len(catastrophic_control),
            "resident_catastrophic_cell_margin_delta": robust_summary(
                row["margin_delta"] for row in catastrophic_control
            ),
        },
        "against_cold": (
            {
                "seed_clustered_margin_delta": cold_margin,
                "command_difference_rate": sum(row["command_diff_cold"] for row in pairs)
                / len(pairs),
            }
            if require_cold
            else None
        ),
        "against_resident_command_difference_rate": sum(
            row["command_diff_resident"] for row in pairs
        )
        / len(pairs),
        "tail": {
            "resident_catastrophic_frequency": resident_catastrophes / len(pairs),
            "candidate_catastrophic_frequency": candidate_catastrophes / len(pairs),
            "resident_negative_margin_mass": resident_mass,
            "candidate_negative_margin_mass": candidate_mass,
            "candidate_to_resident_negative_mass_ratio": candidate_mass / resident_mass,
        },
        "phase_execution": {
            "both_phase_rate": both_phase_rate,
            "mean_farm_turns": statistics.mean(row["farm_turns"] for row in pairs),
            "mean_restart_turns": statistics.mean(row["restart_turns"] for row in pairs),
        },
        "actions": {
            field: robust_summary(row[field] for row in pairs)
            for field in (
                "farm_train_commands",
                "farm_plant_commands",
                "restart_train_commands",
                "restart_plant_commands",
            )
        },
        "workforce": {
            "resident_mean_max_workers": statistics.mean(
                row["resident_max_workers"] for row in pairs
            ),
            "candidate_mean_max_workers": statistics.mean(
                row["candidate_max_workers"] for row in pairs
            ),
        },
    }
    resident_part = report["against_resident"]
    gates = {
        "mean_margin_at_least_5": margin["mean"] >= 5,
        "trimmed_margin_at_least_3": margin["trimmed_5pct_mean"] >= 3,
        "ci95_lower_above_zero": margin["ci95_normal"][0] > 0,
        "own_score_at_least_5": own_score["mean"] >= 5,
        "six_of_eight_opponents_nonnegative": resident_part["nonnegative_opponent_means"] >= 6,
        "worst_opponent_at_least_minus_5": resident_part["worst_opponent_mean_delta"] >= -5,
        "positive_resident_catastrophe_delta": bool(catastrophic_control)
        and resident_part["resident_catastrophic_cell_margin_delta"]["mean"] > 0,
        "catastrophic_frequency_not_higher": candidate_catastrophes <= resident_catastrophes,
        "negative_margin_mass_not_higher": candidate_mass <= resident_mass,
        "both_phases_execute_at_least_95pct": both_phase_rate >= 0.95,
    }
    if require_cold:
        gates["cold_improvement_at_least_10"] = cold_margin["mean"] >= 10
        gates["cold_improvement_ci95_lower_above_zero"] = cold_margin["ci95_normal"][0] > 0
    report["gates"] = gates
    report["passed"] = all(gates.values())
    return report


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
        "--mode", choices=("smoke", "development", "confirmation"), required=True
    )
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--seed-count", type=int, required=True)
    parser.add_argument("--options", default=",".join(ALL_OPTIONS))
    parser.add_argument("--repeat", type=Path)
    parser.add_argument("--d24-reference", type=Path, action="append", default=[])
    parser.add_argument("--d26-reference", type=Path, action="append", default=[])
    args = parser.parse_args()

    options = parse_options(args.options)
    if "resident" not in options:
        raise SystemExit("resident control is required")
    test_options = tuple(option for option in TEST_OPTIONS if option in options)
    if args.mode != "confirmation" and ("cold" not in options or set(test_options) != set(TEST_OPTIONS)):
        raise SystemExit("smoke/development require cold, paused, and shadow")
    if args.mode == "confirmation" and set(options) != {"resident", "paused"}:
        raise SystemExit("confirmation requires exactly resident,paused")

    rows = read_rows(args.input)
    integrity, grouped = validate_grid(rows, args.seed_start, args.seed_count, options)
    if args.repeat:
        integrity["repeat_path"] = str(args.repeat)
        integrity["repeat_byte_identical"] = args.input.read_bytes() == args.repeat.read_bytes()
    else:
        integrity["repeat_path"] = None
        integrity["repeat_byte_identical"] = None
    references = validate_references(grouped, args.d24_reference, args.d26_reference)
    integrity["reference_parity"] = references

    require_cold = args.mode != "confirmation"
    reports = [analyze_option(grouped, option, require_cold) for option in test_options]
    activation = {
        report["option"]: {
            "difference_rate": (
                report["against_cold"]["command_difference_rate"]
                if require_cold
                else report["against_resident_command_difference_rate"]
            ),
            "reference": "cold" if require_cold else "resident",
        }
        for report in reports
    }
    for value in activation.values():
        value["passes_20pct"] = value["difference_rate"] >= 0.20
    integrity["all_test_options_pass_20pct_activation"] = all(
        value["passes_20pct"] for value in activation.values()
    )
    integrity["readiness_passed"] = (
        integrity["complete"]
        and integrity["all_test_options_pass_20pct_activation"]
        and (args.mode != "smoke" or integrity["repeat_byte_identical"] is True)
        and references["complete_match"] is not False
    )

    by_option = {report["option"]: report for report in reports}
    if args.mode == "smoke":
        decision = {
            "open_development": integrity["readiness_passed"],
            "select_from_smoke_outcomes": False,
        }
    elif args.mode == "development":
        paused_passed = by_option["paused"]["passed"]
        shadow_passed = by_option["shadow"]["passed"]
        decision = {
            "open_paused_confirmation": integrity["readiness_passed"] and paused_passed,
            "build_actual_command_observer": (
                integrity["readiness_passed"] and not paused_passed and shadow_passed
            ),
            "close_basic_state_retention": not paused_passed and not shadow_passed,
            "paused_passed": paused_passed,
            "shadow_passed": shadow_passed,
        }
    else:
        paused_passed = by_option["paused"]["passed"]
        decision = {
            "deployment_feasibility_authorized": integrity["readiness_passed"] and paused_passed,
            "paused_confirmation_passed": paused_passed,
        }

    payload = {
        "schema": 1,
        "scope": "exact common-state resident handoff-state test at frozen turn 150; no Arena or submission action",
        "mode": args.mode,
        "source": str(args.input),
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "options": options,
        "opponents": OPPONENTS,
        "integrity": integrity,
        "activation": activation,
        "options_analysis": reports,
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
                        "option": report["option"],
                        "resident_mean": report["against_resident"][
                            "seed_clustered_margin_delta"
                        ]["mean"],
                        "resident_ci": report["against_resident"][
                            "seed_clustered_margin_delta"
                        ]["ci95_normal"],
                        "cold_mean": (
                            report["against_cold"]["seed_clustered_margin_delta"]["mean"]
                            if report["against_cold"]
                            else None
                        ),
                        "cold_ci": (
                            report["against_cold"]["seed_clustered_margin_delta"][
                                "ci95_normal"
                            ]
                            if report["against_cold"]
                            else None
                        ),
                        "own_score": report["against_resident"][
                            "seed_clustered_own_score_delta"
                        ]["mean"],
                        "worst_opponent": report["against_resident"][
                            "worst_opponent_mean_delta"
                        ],
                        "negative_mass_ratio": report["tail"][
                            "candidate_to_resident_negative_mass_ratio"
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
