#!/usr/bin/env python3
"""Analyze D72's frozen recurrent opening-portfolio population."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402
from cgauto.analyze_d71a_opening_portfolio_preflight import parse_timing  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d72a-recurrent-opening-portfolio-population-protocol-2026-07-21.md"
RUNNER = REPO / "rust/src/bin/d72_recurrent_opening_population.rs"
GENERATOR = REPO / "cgauto/make_d72a_recurrent_population.py"
MACRO = REPO / "rust/src/rl_macro.rs"
BATCH = REPO / "rust/src/rl_batch_option.rs"
ENVIRONMENT = REPO / "rust/src/rl_opening_portfolio.rs"

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
SPECIES = ("plum", "lemon", "apple", "banana")
ACTION_FIELDS = (
    "action_balanced",
    "action_harvest",
    "action_renew",
    "action_fell",
    "action_seed_plum",
    "action_seed_lemon",
    "action_seed_apple",
    "action_seed_banana",
)
SOURCE_ACTION_FIELDS = ACTION_FIELDS[4:]
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "finite_feature_failures",
    "finite_recurrent_failures",
    "legal_mask_failures",
    "source_assignment_failures",
    "boundary_failures",
)
EXPECTED_FIELDS = (
    "policy",
    "family",
    "map_seed",
    "seat",
    "opponent",
    "turn",
    "own_score",
    "opponent_score",
    "margin",
    "own_workers",
    "opponent_workers",
    "successful_trains",
    "completed_jobs",
    "invalidated_jobs",
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "selected_decisions",
    "selected_jobs",
    "selected_nonidle_jobs",
    "selected_renew_jobs",
    "own_created_crops",
    "opponent_created_crops",
    "ambiguous_created_crops",
    "own_owned_crop_harvest_units",
    "own_reinvested_crops",
    "action_hash",
    "state_hash",
    "boundary_decisions",
    *ACTION_FIELDS,
    *(f"attempt_{species}" for species in SPECIES),
    *(f"created_{species}" for species in SPECIES),
    "renewable_receipts",
    "ended_own_generations",
    "reinvested_generations",
    "live_own_generations",
    "repeated_source_attempts",
    "source_attempts_after_death",
    "in_flight_boundaries",
    "pre_crop_boundaries",
    "pre_crop_two_seed_legal",
    "finite_feature_failures",
    "finite_recurrent_failures",
    "legal_mask_failures",
    "source_assignment_failures",
    "boundary_failures",
    "reward_identity_error",
    "recurrent_hash",
    "maximum_hidden_abs",
)
INTEGER_FIELDS = tuple(
    field
    for field in EXPECTED_FIELDS
    if field
    not in {
        "policy",
        "family",
        "opponent",
        "reward_identity_error",
        "maximum_hidden_abs",
    }
)


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        return tuple(reader.fieldnames or ()), rows


def expected_policies() -> dict[str, str]:
    result = {"balanced": "control", "cyclic": "control"}
    result.update({f"ordinary_rnn_{index:02}": "ordinary_rnn" for index in range(32)})
    result.update({f"portfolio_rnn_{index:02}": "portfolio_rnn" for index in range(32)})
    return result


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def validate_population(path: Path) -> dict:
    header, rows = read_tsv(path)
    expected_header = ("policy", *(f"param_{index:04}" for index in range(1_124)))
    expected_labels = [f"rnn_{index:02}" for index in range(32)]
    finite = True
    parse_failures = 0
    for row in rows:
        try:
            finite &= all(math.isfinite(float(row[field])) for field in header[1:])
        except (KeyError, TypeError, ValueError):
            parse_failures += 1
    return {
        "rows": len(rows),
        "header_exact": header == expected_header,
        "labels_exact": [row.get("policy") for row in rows] == expected_labels,
        "finite_parameters": finite,
        "parse_failures": parse_failures,
        "pass": (
            header == expected_header
            and len(rows) == 32
            and [row.get("policy") for row in rows] == expected_labels
            and finite
            and parse_failures == 0
        ),
    }


def validate_grid(header: tuple[str, ...], rows: list[dict[str, str]]) -> dict:
    policies = expected_policies()
    expected = {
        (policy, seed, seat, opponent)
        for policy in policies
        for seed in range(9_804_000, 9_804_008)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }
    parse_failures = 0
    actual: list[tuple[str, int, int, str]] = []
    for row in rows:
        try:
            actual.append((row["policy"], *task_key(row)))
            for field in INTEGER_FIELDS:
                int(row[field])
            float(row["reward_identity_error"])
            float(row["maximum_hidden_abs"])
        except (KeyError, TypeError, ValueError):
            parse_failures += 1
    actual_set = set(actual)
    family_failures = sum(
        row.get("family") != policies.get(row.get("policy", "")) for row in rows
    )
    failures = {}
    option_count_failures = 0
    source_count_failures = 0
    ordinary_source_actions = 0
    ordinary_source_attempts = 0
    ordinary_source_creations = 0
    reward_errors: list[float] = []
    hidden_magnitudes: list[float] = []
    if parse_failures == 0 and header == EXPECTED_FIELDS:
        failures = {field: sum(int(row[field]) for row in rows) for field in FAILURE_FIELDS}
        for row in rows:
            option_count_failures += int(row["boundary_decisions"]) != sum(
                int(row[field]) for field in ACTION_FIELDS
            )
            for species in SPECIES:
                attempts = int(row[f"attempt_{species}"])
                actions = int(row[f"action_seed_{species}"])
                creations = int(row[f"created_{species}"])
                source_count_failures += int(attempts != actions or creations > attempts)
            if row["family"] == "ordinary_rnn":
                ordinary_source_actions += sum(int(row[field]) for field in SOURCE_ACTION_FIELDS)
                ordinary_source_attempts += sum(
                    int(row[f"attempt_{species}"]) for species in SPECIES
                )
                ordinary_source_creations += sum(
                    int(row[f"created_{species}"]) for species in SPECIES
                )
            reward_errors.append(float(row["reward_identity_error"]))
            hidden_magnitudes.append(float(row["maximum_hidden_abs"]))
    return {
        "rows": len(rows),
        "header_exact": header == EXPECTED_FIELDS,
        "complete_grid": len(rows) == len(expected) and actual_set == expected,
        "duplicate_rows": len(actual) - len(actual_set),
        "missing_rows": len(expected - actual_set),
        "unexpected_rows": len(actual_set - expected),
        "parse_failures": parse_failures,
        "family_failures": family_failures,
        "failure_totals": failures,
        "option_count_failures": option_count_failures,
        "source_count_failures": source_count_failures,
        "ordinary_source_actions": ordinary_source_actions,
        "ordinary_source_attempts": ordinary_source_attempts,
        "ordinary_source_creations": ordinary_source_creations,
        "maximum_reward_identity_error": max(reward_errors, default=float("inf")),
        "maximum_hidden_abs": max(hidden_magnitudes, default=float("inf")),
        "environmental_invalidated_jobs": (
            sum(int(row["invalidated_jobs"]) for row in rows)
            if parse_failures == 0 and header == EXPECTED_FIELDS
            else None
        ),
    }


def grid_integrity_pass(report: dict) -> bool:
    return (
        report["header_exact"]
        and report["complete_grid"]
        and report["duplicate_rows"] == 0
        and report["parse_failures"] == 0
        and report["family_failures"] == 0
        and report["failure_totals"]
        and all(value == 0 for value in report["failure_totals"].values())
        and report["option_count_failures"] == 0
        and report["source_count_failures"] == 0
        and report["ordinary_source_actions"] == 0
        and report["ordinary_source_attempts"] == 0
        and report["ordinary_source_creations"] == 0
        and report["maximum_reward_identity_error"] < 1e-4
        and report["maximum_hidden_abs"] <= 1.0
    )


def policy_summary(rows: list[dict[str, str]], family: str) -> dict[str, dict]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["family"] == family:
            grouped[row["policy"]].append(row)
    result = {}
    for policy, selected in sorted(grouped.items()):
        actions = {field.removeprefix("action_"): sum(int(row[field]) for row in selected) for field in ACTION_FIELDS}
        source_tasks = sum(
            any(int(row[field]) > 0 for field in SOURCE_ACTION_FIELDS) for row in selected
        )
        result[policy] = {
            "tasks": len(selected),
            "mean_margin": statistics.fmean(int(row["margin"]) for row in selected),
            "mean_own_score": statistics.fmean(int(row["own_score"]) for row in selected),
            "mean_opponent_score": statistics.fmean(int(row["opponent_score"]) for row in selected),
            "crop_tasks": sum(int(row["own_created_crops"]) > 0 for row in selected),
            "worker_three_tasks": sum(int(row["own_workers"]) >= 3 for row in selected),
            "source_action_tasks": source_tasks,
            "source_action_task_rate": source_tasks / len(selected),
            "used_actions": sum(value > 0 for value in actions.values()),
            "action_counts": actions,
        }
    return result


def crop_safe_oracle(
    rows: list[dict[str, str]], family: str
) -> dict[tuple[int, int, str], dict[str, str]]:
    grouped: dict[tuple[int, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["family"] == family and int(row["own_created_crops"]) > 0:
            grouped[task_key(row)].append(row)
    return {
        task: min(
            candidates,
            key=lambda row: (
                -int(row["margin"]),
                -int(row["own_score"]),
                int(row["opponent_score"]),
                row["policy"],
            ),
        )
        for task, candidates in grouped.items()
    }


def compare_selections(
    candidate: dict[tuple[int, int, str], dict[str, str]],
    baseline: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    common = sorted(set(candidate) & set(baseline))
    margin_delta = [
        int(candidate[key]["margin"]) - int(baseline[key]["margin"]) for key in common
    ]
    own_delta = [
        int(candidate[key]["own_score"]) - int(baseline[key]["own_score"]) for key in common
    ]
    opponent_delta = [
        int(candidate[key]["opponent_score"]) - int(baseline[key]["opponent_score"])
        for key in common
    ]
    by_opponent = {}
    for opponent in OPPONENTS:
        values = [margin_delta[index] for index, key in enumerate(common) if key[2] == opponent]
        by_opponent[opponent] = statistics.fmean(values) if values else None
    return {
        "candidate_tasks": len(candidate),
        "baseline_tasks": len(baseline),
        "common_tasks": len(common),
        "identity_exact": set(candidate) == set(baseline),
        "mean_margin_delta": statistics.fmean(margin_delta) if margin_delta else None,
        "strict_improvement_tasks": sum(value > 0 for value in margin_delta),
        "strict_improvement_rate": (
            sum(value > 0 for value in margin_delta) / len(margin_delta)
            if margin_delta
            else None
        ),
        "tie_tasks": sum(value == 0 for value in margin_delta),
        "regression_tasks": sum(value < 0 for value in margin_delta),
        "mean_own_score_delta": statistics.fmean(own_delta) if own_delta else None,
        "mean_opponent_score_delta": (
            statistics.fmean(opponent_delta) if opponent_delta else None
        ),
        "opponent_mean_margin_delta": by_opponent,
    }


def control_selection(rows: list[dict[str, str]], label: str) -> dict:
    return {task_key(row): row for row in rows if row["policy"] == label}


def selection_summary(selection: dict[tuple[int, int, str], dict[str, str]]) -> dict:
    rows = list(selection.values())
    source_rows = [
        row for row in rows if any(int(row[field]) > 0 for field in SOURCE_ACTION_FIELDS)
    ]
    policy_counts = Counter(row["policy"] for row in rows)
    source_policy_counts = Counter(row["policy"] for row in source_rows)
    species_counts = {
        species: sum(int(row[f"action_seed_{species}"]) for row in source_rows)
        for species in SPECIES
    }
    return {
        "tasks": len(rows),
        "mean_margin": statistics.fmean(int(row["margin"]) for row in rows),
        "mean_own_score": statistics.fmean(int(row["own_score"]) for row in rows),
        "mean_opponent_score": statistics.fmean(int(row["opponent_score"]) for row in rows),
        "crop_tasks": sum(int(row["own_created_crops"]) > 0 for row in rows),
        "worker_three_tasks": sum(int(row["own_workers"]) >= 3 for row in rows),
        "worker_three_rate": sum(int(row["own_workers"]) >= 3 for row in rows) / len(rows),
        "source_action_tasks": len(source_rows),
        "selected_policy_counts": dict(sorted(policy_counts.items())),
        "source_policy_counts": dict(sorted(source_policy_counts.items())),
        "source_species_action_counts": species_counts,
        "source_species_used": sum(value > 0 for value in species_counts.values()),
    }


def quarantined_report(inputs: dict, integrity: dict) -> dict:
    return {
        "schema": "troll-farm-d72a-recurrent-opening-population-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consumed recurrent random-function-class and explicit-source-action ablation",
        "inputs": inputs,
        "integrity": integrity,
        "activity": None,
        "oracles": None,
        "gates": {"integrity": False},
        "decision": {
            "status": "integrity_failure",
            "next_experiment": "repair_only_then_repeat_unchanged",
            "aggregate_outcomes": False,
            "train_ppo": False,
            "construct_candidate": False,
            "platform_action": False,
        },
    }


def build_report(
    population_path: Path,
    grid_a_path: Path,
    grid_b_path: Path,
    time_a_path: Path,
    time_b_path: Path,
) -> dict:
    header_a, rows_a = read_tsv(grid_a_path)
    header_b, rows_b = read_tsv(grid_b_path)
    population = validate_population(population_path)
    grid_a = validate_grid(header_a, rows_a)
    grid_b = validate_grid(header_b, rows_b)
    repeat_exact = grid_a_path.read_bytes() == grid_b_path.read_bytes()
    timings = [parse_timing(time_a_path), parse_timing(time_b_path)]
    inputs = {
        "protocol": sha256_file(PROTOCOL),
        "runner": sha256_file(RUNNER),
        "generator": sha256_file(GENERATOR),
        "macro_environment": sha256_file(MACRO),
        "batch_environment": sha256_file(BATCH),
        "opening_environment": sha256_file(ENVIRONMENT),
        "population": sha256_file(population_path),
        "grid_a": sha256_file(grid_a_path),
        "grid_b": sha256_file(grid_b_path),
        "time_a": sha256_file(time_a_path),
        "time_b": sha256_file(time_b_path),
        "analyzer": sha256_file(Path(__file__)),
    }
    integrity_pass = (
        population["pass"]
        and grid_integrity_pass(grid_a)
        and grid_integrity_pass(grid_b)
        and repeat_exact
    )
    integrity = {
        "population": population,
        "grid_a": grid_a,
        "grid_b": grid_b,
        "repeat_byte_identical": repeat_exact,
        "timings": timings,
        "pass": integrity_pass,
    }
    if not integrity_pass:
        return quarantined_report(inputs, integrity)

    transitions = sum(int(row["boundary_decisions"]) for row in rows_a)
    for timing in timings:
        timing["boundary_transitions"] = transitions
        timing["boundary_transitions_per_second"] = transitions / timing["elapsed_seconds"]

    portfolio_policies = policy_summary(rows_a, "portfolio_rnn")
    ordinary_policies = policy_summary(rows_a, "ordinary_rnn")
    portfolio_actions = {
        field.removeprefix("action_"): sum(
            int(row[field]) for row in rows_a if row["family"] == "portfolio_rnn"
        )
        for field in ACTION_FIELDS
    }
    mean_margins = [row["mean_margin"] for row in portfolio_policies.values()]
    activity = {
        "boundary_transitions": transitions,
        "portfolio_policies": portfolio_policies,
        "ordinary_policies": ordinary_policies,
        "portfolio_action_counts": portfolio_actions,
        "portfolio_policies_using_at_least_four_actions": sum(
            row["used_actions"] >= 4 for row in portfolio_policies.values()
        ),
        "portfolio_policies_source_in_at_least_quarter_tasks": sum(
            row["source_action_task_rate"] >= 0.25 for row in portfolio_policies.values()
        ),
        "portfolio_policies_crop_every_task": sum(
            row["crop_tasks"] == 128 for row in portfolio_policies.values()
        ),
        "portfolio_mean_margin_min": min(mean_margins),
        "portfolio_mean_margin_max": max(mean_margins),
        "portfolio_mean_margin_span": max(mean_margins) - min(mean_margins),
    }

    portfolio_oracle = crop_safe_oracle(rows_a, "portfolio_rnn")
    ordinary_oracle = crop_safe_oracle(rows_a, "ordinary_rnn")
    balanced = control_selection(rows_a, "balanced")
    cyclic = control_selection(rows_a, "cyclic")
    portfolio_selection = selection_summary(portfolio_oracle)
    ordinary_selection = selection_summary(ordinary_oracle)
    balanced_selection = selection_summary(balanced)
    cyclic_selection = selection_summary(cyclic)
    versus_balanced = compare_selections(portfolio_oracle, balanced)
    versus_ordinary = compare_selections(portfolio_oracle, ordinary_oracle)

    activity_gates = {
        "at_least_24_policies_use_four_actions": (
            activity["portfolio_policies_using_at_least_four_actions"] >= 24
        ),
        "at_least_24_policies_source_quarter_tasks": (
            activity["portfolio_policies_source_in_at_least_quarter_tasks"] >= 24
        ),
        "every_action_at_least_256": all(value >= 256 for value in portfolio_actions.values()),
        "at_least_24_policies_crop_every_task": (
            activity["portfolio_policies_crop_every_task"] >= 24
        ),
        "mean_margin_span_at_least_30": activity["portfolio_mean_margin_span"] >= 30,
    }
    balanced_gates = {
        "complete_crop_safe_oracle": (
            portfolio_selection["tasks"] == balanced_selection["tasks"] == 128
            and versus_balanced["identity_exact"]
        ),
        "mean_margin_gain_at_least_30": versus_balanced["mean_margin_delta"] >= 30,
        "strict_improvement_at_least_70_percent": (
            versus_balanced["strict_improvement_rate"] >= 0.70
        ),
        "every_opponent_gain_at_least_10": all(
            value >= 10 for value in versus_balanced["opponent_mean_margin_delta"].values()
        ),
        "own_nonnegative_and_opponent_nonpositive": (
            versus_balanced["mean_own_score_delta"] >= 0
            and versus_balanced["mean_opponent_score_delta"] <= 0
        ),
        "worker_three_at_least_85_percent": portfolio_selection["worker_three_rate"] >= 0.85,
        "crop_creation_exactly_100_percent": portfolio_selection["crop_tasks"] == 128,
    }
    ordinary_gates = {
        "complete_matched_crop_safe_oracles": (
            portfolio_selection["tasks"] == ordinary_selection["tasks"] == 128
            and versus_ordinary["identity_exact"]
        ),
        "mean_margin_gain_at_least_8": versus_ordinary["mean_margin_delta"] >= 8,
        "strict_improvement_at_least_40_percent": (
            versus_ordinary["strict_improvement_rate"] >= 0.40
        ),
        "own_nonnegative_or_opponent_nonpositive": (
            versus_ordinary["mean_own_score_delta"] >= 0
            or versus_ordinary["mean_opponent_score_delta"] <= 0
        ),
        "source_actions_in_at_least_32_winners": portfolio_selection["source_action_tasks"] >= 32,
        "source_winners_span_at_least_8_policies": (
            len(portfolio_selection["source_policy_counts"]) >= 8
        ),
        "source_winners_span_at_least_3_species": portfolio_selection["source_species_used"] >= 3,
        "every_opponent_gain_nonnegative": all(
            value >= 0 for value in versus_ordinary["opponent_mean_margin_delta"].values()
        ),
    }
    activity_pass = all(activity_gates.values())
    balanced_pass = all(balanced_gates.values())
    ordinary_pass = all(ordinary_gates.values())
    full_pass = activity_pass and balanced_pass and ordinary_pass
    if full_pass:
        status = "full_pass"
        next_experiment = "short_recurrent_optimization_signal_preflight"
    elif activity_pass and balanced_pass:
        status = "explicit_action_ablation_failure"
        next_experiment = "retain_recurrent_ordinary_options_close_explicit_seed_actions"
    else:
        status = "function_class_headroom_failure"
        next_experiment = "paired_online_option_values"
    return {
        "schema": "troll-farm-d72a-recurrent-opening-population-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consumed recurrent random-function-class and explicit-source-action ablation",
        "inputs": inputs,
        "integrity": integrity,
        "activity": activity,
        "oracles": {
            "portfolio": portfolio_selection,
            "ordinary": ordinary_selection,
            "balanced": balanced_selection,
            "cyclic": cyclic_selection,
            "portfolio_versus_balanced": versus_balanced,
            "portfolio_versus_ordinary": versus_ordinary,
        },
        "gates": {
            "integrity": True,
            "activity": activity_gates,
            "portfolio_versus_balanced": balanced_gates,
            "portfolio_versus_ordinary": ordinary_gates,
            "activity_pass": activity_pass,
            "portfolio_versus_balanced_pass": balanced_pass,
            "portfolio_versus_ordinary_pass": ordinary_pass,
            "full_pass": full_pass,
        },
        "decision": {
            "status": status,
            "next_experiment": next_experiment,
            "oracle_selects_candidate": False,
            "train_ppo": False,
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--grid-a", type=Path, required=True)
    parser.add_argument("--grid-b", type=Path, required=True)
    parser.add_argument("--time-a", type=Path, required=True)
    parser.add_argument("--time-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(
        args.population, args.grid_a, args.grid_b, args.time_a, args.time_b
    )
    atomic_write_new(args.output, report)
    print(
        json.dumps(
            {
                "integrity": report["integrity"],
                "gates": report["gates"],
                "decision": report["decision"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
