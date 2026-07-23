#!/usr/bin/env python3
"""Audit D76's recurrent-readout CEM search and prospective validation."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402
from cgauto.analyze_d71a_opening_portfolio_preflight import parse_timing  # noqa: E402
from cgauto.run_d76a_recurrent_readout_cem import (  # noqa: E402
    ACTIONS,
    ACTION_FIELDS,
    ANALYSIS,
    EVALUATION_A,
    EVALUATION_B,
    EVALUATION_TIME_A,
    EVALUATION_TIME_B,
    FINAL_POPULATION,
    FROZEN,
    PARAMETERS,
    PROTOCOL,
    READOUT_PARAMETERS,
    RESERVOIR_PARAMETERS,
    ROOT,
    RUNNER,
    RUNNER_SOURCE,
    SEARCH_LOG,
    UNLOCKED_ACTION_FIELDS,
    VALIDATION_POPULATION,
    expected_task_keys,
    fixed_reservoir,
    full_parameters,
    policy_objectives,
    population_readouts,
    rank_labels,
    read_tsv,
    sha256_array,
    update_distribution,
    validate_matrix,
)


ORCHESTRATOR = ROOT / "cgauto/run_d76a_recurrent_readout_cem.py"
RESULT = ANALYSIS / "d76a-recurrent-readout-cem-result.json"
TOTAL_TIME = ANALYSIS / "d76a-recurrent-readout-cem-total-time.txt"
ANCHOR_FIELDS = (
    "turn",
    "own_score",
    "opponent_score",
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
    "unlocked_decisions",
    *UNLOCKED_ACTION_FIELDS,
)


def read_population(path: Path) -> tuple[tuple[str, ...], list[tuple[str, np.ndarray]]]:
    with path.open(newline="") as source:
        reader = csv.reader(source, delimiter="\t")
        rows = list(reader)
    header = tuple(rows[0]) if rows else ()
    parsed = []
    for row in rows[1:]:
        parsed.append((row[0], np.asarray([float(value) for value in row[1:]], dtype=np.float32)))
    return header, parsed


def population_integrity(
    path: Path,
    expected: list[tuple[str, np.ndarray]],
    reservoir: np.ndarray,
) -> dict:
    header, actual = read_population(path)
    expected_header = ("policy", *(f"param_{index:04}" for index in range(PARAMETERS)))
    labels_exact = [label for label, _ in actual] == [label for label, _ in expected]
    finite = all(np.isfinite(values).all() for _, values in actual)
    geometry = all(values.shape == (PARAMETERS,) for _, values in actual)
    serialized_reservoir = full_parameters(
        reservoir, np.zeros(READOUT_PARAMETERS, dtype=np.float32)
    )[:RESERVOIR_PARAMETERS]
    reservoir_exact = all(
        np.array_equal(values[:RESERVOIR_PARAMETERS], serialized_reservoir)
        for _, values in actual
    )
    parameter_exact = len(actual) == len(expected) and all(
        actual_label == expected_label
        and np.array_equal(actual_values, full_parameters(reservoir, expected_readout))
        for (actual_label, actual_values), (expected_label, expected_readout) in zip(
            actual, expected, strict=True
        )
    )
    return {
        "rows": len(actual),
        "header_exact": header == expected_header,
        "labels_exact": labels_exact,
        "finite": finite,
        "geometry_exact": geometry,
        "reservoir_exact": reservoir_exact,
        "parameters_exact": parameter_exact,
        "pass": (
            header == expected_header
            and labels_exact
            and finite
            and geometry
            and reservoir_exact
            and parameter_exact
        ),
    }


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def anchor_summary(rows: list[dict[str, str]]) -> dict:
    grouped = {
        policy: {task_key(row): row for row in rows if row["policy"] == policy}
        for policy in ("balanced", "initial")
    }
    identities_exact = set(grouped["balanced"]) == set(grouped["initial"])
    mismatches = 0
    if identities_exact:
        mismatches = sum(
            any(
                grouped["balanced"][key][field] != grouped["initial"][key][field]
                for field in ANCHOR_FIELDS
            )
            for key in grouped["balanced"]
        )
    return {
        "tasks": len(grouped["balanced"]),
        "identities_exact": identities_exact,
        "field_mismatches": mismatches,
        "pass": identities_exact and mismatches == 0,
    }


def distribution(values: list[int]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(array.mean()),
        "minimum": float(array.min()),
        "p01": float(np.quantile(array, 0.01)),
        "p10": float(np.quantile(array, 0.10)),
        "median": float(np.median(array)),
        "p90": float(np.quantile(array, 0.90)),
        "p99": float(np.quantile(array, 0.99)),
        "maximum": float(array.max()),
        "positive_rate": float(np.mean(array > 0)),
        "tie_rate": float(np.mean(array == 0)),
        "negative_rate": float(np.mean(array < 0)),
    }


def validation_summary(rows: list[dict[str, str]]) -> dict:
    grouped = {
        policy: {task_key(row): row for row in rows if row["policy"] == policy}
        for policy in ("balanced", "final")
    }
    baseline = grouped["balanced"]
    final = grouped["final"]
    if set(baseline) != set(final):
        raise ValueError("D76 validation identity mismatch")
    deltas = [int(final[key]["margin"]) - int(baseline[key]["margin"]) for key in baseline]
    own = [int(final[key]["own_score"]) - int(baseline[key]["own_score"]) for key in baseline]
    opponent = [
        int(final[key]["opponent_score"]) - int(baseline[key]["opponent_score"])
        for key in baseline
    ]
    unlocked = sum(int(row["unlocked_decisions"]) for row in final.values())
    action_counts = [sum(int(row[field]) for row in final.values()) for field in UNLOCKED_ACTION_FIELDS]
    by_opponent = {
        family: statistics.fmean(
            int(final[key]["margin"]) - int(baseline[key]["margin"])
            for key in baseline
            if key[2] == family
        )
        for family in sorted({key[2] for key in baseline})
    }
    by_seat = {
        str(seat): statistics.fmean(
            int(final[key]["margin"]) - int(baseline[key]["margin"])
            for key in baseline
            if key[1] == seat
        )
        for seat in (0, 1)
    }
    return {
        "tasks": len(baseline),
        "margin_delta": distribution(deltas),
        "mean_own_score_delta": statistics.fmean(own),
        "mean_opponent_score_delta": statistics.fmean(opponent),
        "opponent_mean_margin_delta": by_opponent,
        "positive_opponent_families": sum(value > 0 for value in by_opponent.values()),
        "seat_mean_margin_delta": by_seat,
        "worker_three_rate": statistics.fmean(
            int(row["own_workers"]) >= 3 for row in final.values()
        ),
        "crop_creation_rate": statistics.fmean(
            int(row["own_created_crops"]) > 0 for row in final.values()
        ),
        "unlocked_decisions": unlocked,
        "unlocked_action_counts": action_counts,
        "unlocked_action_rates": [count / unlocked for count in action_counts],
        "nonbalanced_rate": sum(action_counts[1:]) / unlocked,
        "distinct_nonbalanced_modes": sum(count > 0 for count in action_counts[1:]),
        "maximum_hidden_abs": max(float(row["maximum_hidden_abs"]) for row in final.values()),
    }


def audit_search(search: dict) -> dict:
    reservoir = fixed_reservoir()
    reservoir_hash_exact = search.get("reservoir_hash") == sha256_array(reservoir)
    rng = np.random.Generator(np.random.PCG64(FROZEN["search_seed"]))
    mean = np.zeros(READOUT_PARAMETERS, dtype=np.float64)
    std = np.concatenate(
        (
            np.full(ACTIONS * 12, FROZEN["weight_initial_std"]),
            np.full(ACTIONS, FROZEN["bias_initial_std"]),
        )
    ).astype(np.float64)
    generations = []
    all_pass = reservoir_hash_exact and len(search.get("generations", [])) == FROZEN["generations"]
    for generation, logged in enumerate(search.get("generations", []), start=1):
        population_path = ANALYSIS / f"d76a-generation-{generation:02d}-population.tsv"
        rows_path = ANALYSIS / f"d76a-generation-{generation:02d}-rows.tsv"
        timing_path = ANALYSIS / f"d76a-generation-{generation:02d}-time.txt"
        summary_path = ANALYSIS / f"d76a-generation-{generation:02d}-summary.json"
        expected_population = population_readouts(mean, std, rng, generation)
        pop_integrity = population_integrity(population_path, expected_population, reservoir)
        labels = [label for label, _ in expected_population]
        _, rows = read_tsv(rows_path)
        seed_base = FROZEN["search_seed_base"] + (generation - 1) * FROZEN[
            "maps_per_generation"
        ]
        matrix_integrity = validate_matrix(
            rows, labels, seed_base, FROZEN["maps_per_generation"]
        )
        objectives = policy_objectives(rows, labels)
        ranking = rank_labels(objectives)
        elites = ranking[: FROZEN["elites"]]
        readouts = {label: values.astype(np.float64) for label, values in expected_population}
        expected_mean, expected_std = update_distribution(mean, std, readouts, elites)
        logged_summary = json.loads(summary_path.read_text())
        hashes_exact = (
            logged.get("population") == sha256_file(population_path)
            and logged.get("rows") == sha256_file(rows_path)
            and logged.get("timing") == sha256_file(timing_path)
            and logged.get("summary") == sha256_file(summary_path)
        )
        updates_exact = (
            logged.get("generation") == generation
            and logged.get("seed_base") == seed_base
            and logged.get("ranking") == ranking
            and logged.get("elites") == elites
            and np.array_equal(np.asarray(logged.get("mean_after")), expected_mean)
            and np.array_equal(np.asarray(logged.get("std_after")), expected_std)
            and logged.get("mean_after_hash") == sha256_array(expected_mean)
            and logged.get("std_after_hash") == sha256_array(expected_std)
            and logged_summary.get("ranking") == ranking
            and logged_summary.get("elites") == elites
        )
        timing = parse_timing(timing_path)
        passed = pop_integrity["pass"] and matrix_integrity["pass"] and hashes_exact and updates_exact
        generations.append(
            {
                "generation": generation,
                "population": pop_integrity,
                "matrix": matrix_integrity,
                "hashes_exact": hashes_exact,
                "updates_exact": updates_exact,
                "mean_l2": float(np.linalg.norm(expected_mean)),
                "std_mean": float(expected_std.mean()),
                "best": {"label": ranking[0], **objectives[ranking[0]]},
                "mean_member": objectives[f"g{generation:02d}_mean"],
                "timing": timing,
                "pass": passed,
            }
        )
        all_pass &= passed
        mean, std = expected_mean, expected_std
    final_exact = (
        search.get("final_mean_hash") == sha256_array(mean)
        and np.array_equal(np.asarray(search.get("final_mean")), mean.astype(np.float32))
        and search.get("final_std_hash") == sha256_array(std)
        and np.array_equal(np.asarray(search.get("final_std")), std)
    )
    all_pass &= final_exact
    return {
        "reservoir_hash_exact": reservoir_hash_exact,
        "generations": generations,
        "final_distribution_exact": final_exact,
        "final_mean": mean.tolist(),
        "final_std": std.tolist(),
        "final_mean_l2": float(np.linalg.norm(mean)),
        "pass": all_pass,
    }


def build_report() -> dict:
    search = json.loads(SEARCH_LOG.read_text())
    search_audit = audit_search(search)
    reservoir = fixed_reservoir()
    final_mean = np.asarray(search_audit["final_mean"], dtype=np.float32)
    final_population_integrity = population_integrity(
        FINAL_POPULATION, [("final", final_mean)], reservoir
    )
    validation_population_integrity = population_integrity(
        VALIDATION_POPULATION,
        [("initial", np.zeros(READOUT_PARAMETERS, dtype=np.float32)), ("final", final_mean)],
        reservoir,
    )
    search_metadata_exact = (
        search.get("protocol") == sha256_file(PROTOCOL)
        and search.get("orchestrator") == sha256_file(ORCHESTRATOR)
        and search.get("runner_source") == sha256_file(RUNNER_SOURCE)
        and search.get("runner_binary") == sha256_file(RUNNER)
        and search.get("final_population") == sha256_file(FINAL_POPULATION)
        and search.get("validation_population") == sha256_file(VALIDATION_POPULATION)
    )
    _, evaluation_a = read_tsv(EVALUATION_A)
    _, evaluation_b = read_tsv(EVALUATION_B)
    matrix_a = validate_matrix(
        evaluation_a,
        ["initial", "final"],
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    matrix_b = validate_matrix(
        evaluation_b,
        ["initial", "final"],
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    repeat_exact = EVALUATION_A.read_bytes() == EVALUATION_B.read_bytes()
    anchor = anchor_summary(evaluation_a)
    validation = validation_summary(evaluation_a)
    mechanics_pass = (
        search_audit["pass"]
        and search_metadata_exact
        and final_population_integrity["pass"]
        and validation_population_integrity["pass"]
        and matrix_a["pass"]
        and matrix_b["pass"]
    )
    activity_gates = {
        "ten_complete_search_matrices": (
            len(search_audit["generations"]) == 10
            and all(row["matrix"]["rows"] == 2_176 for row in search_audit["generations"])
        ),
        "search_population_and_updates_exact": search_audit["pass"],
        "zero_search_and_validation_mechanical_failures": mechanics_pass,
        "validation_repeat_and_initial_anchor_exact": repeat_exact and anchor["pass"],
        "final_readout_l2_at_least_point5": search_audit["final_mean_l2"] >= 0.50,
        "validation_nonbalanced_rate_at_least_20pct": validation["nonbalanced_rate"] >= 0.20,
        "at_least_two_nonbalanced_modes": validation["distinct_nonbalanced_modes"] >= 2,
    }
    value_gates = {
        "mean_margin_delta_at_least_5": validation["margin_delta"]["mean"] >= 5,
        "strict_improvement_at_least_55pct": validation["margin_delta"]["positive_rate"] >= 0.55,
        "six_positive_and_every_opponent_at_least_minus5": (
            validation["positive_opponent_families"] >= 6
            and all(value >= -5 for value in validation["opponent_mean_margin_delta"].values())
        ),
        "mean_own_score_delta_at_least_minus10": validation["mean_own_score_delta"] >= -10,
        "p10_margin_delta_at_least_minus60": validation["margin_delta"]["p10"] >= -60,
        "worker_three_at_least_90pct": validation["worker_three_rate"] >= 0.90,
        "crop_creation_exactly_100pct": validation["crop_creation_rate"] == 1.0,
    }
    activity_pass = all(activity_gates.values())
    value_pass = all(value_gates.values())
    if not mechanics_pass:
        status = "search_mechanics_failure"
        next_experiment = "repair_only_then_repeat_unchanged"
    elif not activity_pass:
        status = "recurrent_readout_activity_failure"
        next_experiment = "evolved_recurrent_representation_or_new_controller"
    elif not value_pass:
        status = "prospective_fixed_policy_value_failure"
        next_experiment = "evolved_recurrent_representation_or_new_controller"
    else:
        status = "local_fixed_policy_pass"
        next_experiment = "d77_layered_fresh_field_qualification"
    return {
        "schema": "troll-farm-d76a-recurrent-readout-cem-result-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "whole-policy fixed-reservoir recurrent-readout CEM and validation",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "orchestrator": sha256_file(ORCHESTRATOR),
            "analyzer": sha256_file(Path(__file__)),
            "runner_source": sha256_file(RUNNER_SOURCE),
            "search_log": sha256_file(SEARCH_LOG),
            "final_population": sha256_file(FINAL_POPULATION),
            "validation_population": sha256_file(VALIDATION_POPULATION),
            "evaluation_a": sha256_file(EVALUATION_A),
            "evaluation_b": sha256_file(EVALUATION_B),
            "evaluation_time_a": sha256_file(EVALUATION_TIME_A),
            "evaluation_time_b": sha256_file(EVALUATION_TIME_B),
            "total_time": sha256_file(TOTAL_TIME),
        },
        "search": search_audit,
        "search_artifacts": {
            "metadata_exact": search_metadata_exact,
            "final_population": final_population_integrity,
            "validation_population": validation_population_integrity,
            "pass": (
                search_metadata_exact
                and final_population_integrity["pass"]
                and validation_population_integrity["pass"]
            ),
        },
        "validation_integrity": {
            "matrix_a": matrix_a,
            "matrix_b": matrix_b,
            "repeat_byte_exact": repeat_exact,
            "initial_anchor": anchor,
            "timings": [
                parse_timing(EVALUATION_TIME_A),
                parse_timing(EVALUATION_TIME_B),
            ],
            "total_timing": parse_timing(TOTAL_TIME),
            "pass": mechanics_pass and repeat_exact and anchor["pass"],
        },
        "validation": validation,
        "gates": {
            "activity": activity_gates,
            "value": value_gates,
            "activity_pass": activity_pass,
            "value_pass": value_pass,
            "full_pass": mechanics_pass and activity_pass and value_pass,
        },
        "decision": {
            "status": status,
            "next_experiment": next_experiment,
            "local_candidate_input": status == "local_fixed_policy_pass",
            "construct_submission": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RESULT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report()
    atomic_write_new(args.output, report)
    print(
        json.dumps(
            {
                "validation_integrity": report["validation_integrity"],
                "validation": report["validation"],
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
