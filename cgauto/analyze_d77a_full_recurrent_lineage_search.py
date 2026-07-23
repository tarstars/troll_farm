#!/usr/bin/env python3
"""Audit D77's full recurrent lineage search and prospective champion."""

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
    ACTION_FIELDS,
    PARAMETERS,
    ROOT,
    RUNNER,
    RUNNER_SOURCE,
    UNLOCKED_ACTION_FIELDS,
    read_tsv,
    validate_matrix,
)
from cgauto.run_d77a_full_recurrent_lineage_search import (  # noqa: E402
    ANALYSIS,
    CHAMPION_POPULATION,
    EVALUATION_A,
    EVALUATION_B,
    EVALUATION_TIME_A,
    EVALUATION_TIME_B,
    FROZEN,
    PROTOCOL,
    SEARCH_LOG,
    SELECTION_POPULATION,
    SELECTION_ROWS,
    SELECTION_TIME,
    VALIDATION_POPULATION,
    lineage_objectives,
    mutate,
    normalized_vector,
    random_network,
    rank_labels,
    vector_hash,
)


ORCHESTRATOR = ROOT / "cgauto/run_d77a_full_recurrent_lineage_search.py"
RESULT = ANALYSIS / "d77a-full-recurrent-lineage-result.json"
TOTAL_TIME = ANALYSIS / "d77a-full-recurrent-lineage-total-time.txt"
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
        rows = list(csv.reader(source, delimiter="\t"))
    header = tuple(rows[0]) if rows else ()
    return header, [
        (row[0], np.asarray([float(value) for value in row[1:]], dtype=np.float32))
        for row in rows[1:]
    ]


def population_integrity(path: Path, expected: list[tuple[str, np.ndarray]]) -> dict:
    header, actual = read_population(path)
    expected_header = ("policy", *(f"param_{index:04}" for index in range(PARAMETERS)))
    labels_exact = [label for label, _ in actual] == [label for label, _ in expected]
    finite = all(values.shape == (PARAMETERS,) and np.isfinite(values).all() for _, values in actual)
    vectors_exact = len(actual) == len(expected) and all(
        actual_label == expected_label
        and np.array_equal(actual_values, normalized_vector(expected_values))
        for (actual_label, actual_values), (expected_label, expected_values) in zip(
            actual, expected, strict=True
        )
    )
    return {
        "rows": len(actual),
        "header_exact": header == expected_header,
        "labels_exact": labels_exact,
        "finite_and_geometry_exact": finite,
        "vectors_exact": vectors_exact,
        "pass": header == expected_header and labels_exact and finite and vectors_exact,
    }


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def anchor_summary(rows: list[dict[str, str]]) -> dict:
    balanced = {task_key(row): row for row in rows if row["policy"] == "balanced"}
    founder = {task_key(row): row for row in rows if row["policy"] == "founder_zero"}
    identities_exact = set(balanced) == set(founder)
    mismatches = 0
    if identities_exact:
        mismatches = sum(
            any(balanced[key][field] != founder[key][field] for field in ANCHOR_FIELDS)
            for key in balanced
        )
    return {
        "tasks": len(balanced),
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
    balanced = {task_key(row): row for row in rows if row["policy"] == "balanced"}
    champion = {task_key(row): row for row in rows if row["policy"] == "champion"}
    if set(balanced) != set(champion):
        raise ValueError("D77 validation identities differ")
    deltas = [int(champion[key]["margin"]) - int(balanced[key]["margin"]) for key in balanced]
    own = [int(champion[key]["own_score"]) - int(balanced[key]["own_score"]) for key in balanced]
    opponent = [
        int(champion[key]["opponent_score"]) - int(balanced[key]["opponent_score"])
        for key in balanced
    ]
    family = {
        opponent_name: statistics.fmean(
            int(champion[key]["margin"]) - int(balanced[key]["margin"])
            for key in balanced
            if key[2] == opponent_name
        )
        for opponent_name in sorted({key[2] for key in balanced})
    }
    seat = {
        str(index): statistics.fmean(
            int(champion[key]["margin"]) - int(balanced[key]["margin"])
            for key in balanced
            if key[1] == index
        )
        for index in (0, 1)
    }
    balanced_worker = statistics.fmean(
        int(row["own_workers"]) >= 3 for row in balanced.values()
    )
    champion_worker = statistics.fmean(
        int(row["own_workers"]) >= 3 for row in champion.values()
    )
    unlocked = sum(int(row["unlocked_decisions"]) for row in champion.values())
    actions = [
        sum(int(row[field]) for row in champion.values()) for field in UNLOCKED_ACTION_FIELDS
    ]
    return {
        "tasks": len(balanced),
        "margin_delta": distribution(deltas),
        "mean_own_score_delta": statistics.fmean(own),
        "mean_opponent_score_delta": statistics.fmean(opponent),
        "opponent_mean_margin_delta": family,
        "positive_opponent_families": sum(value > 0 for value in family.values()),
        "seat_mean_margin_delta": seat,
        "balanced_worker_three_rate": balanced_worker,
        "champion_worker_three_rate": champion_worker,
        "worker_three_degradation": balanced_worker - champion_worker,
        "crop_creation_rate": statistics.fmean(
            int(row["own_created_crops"]) > 0 for row in champion.values()
        ),
        "unlocked_decisions": unlocked,
        "unlocked_action_counts": actions,
        "unlocked_action_rates": [count / unlocked for count in actions],
        "nonbalanced_rate": sum(actions[1:]) / unlocked,
        "distinct_nonbalanced_modes": sum(count > 0 for count in actions[1:]),
        "maximum_hidden_abs": max(float(row["maximum_hidden_abs"]) for row in champion.values()),
    }


def lineage_depth(label: str, lineage: dict[str, dict]) -> int:
    depth = 0
    current = label
    while lineage[current]["parent"] is not None:
        current = lineage[current]["parent"]
        depth += 1
        if depth > FROZEN["generations"]:
            raise ValueError("D77 lineage cycle")
    return depth


def audit_search(search: dict) -> dict:
    rng = np.random.Generator(np.random.PCG64(FROZEN["seed"]))
    vectors: dict[str, np.ndarray] = {}
    lineage: dict[str, dict] = {}
    current = []
    next_id = 0
    for founder in range(FROZEN["population"]):
        label = f"l{next_id:04d}"
        next_id += 1
        vectors[label] = random_network(rng, zero_readout=founder == 0)
        lineage[label] = {"parent": None, "founder": label, "birth_generation": 1}
        current.append(label)
    founder_zero = current[0]
    generations = []
    all_pass = len(search.get("generations", [])) == FROZEN["generations"]
    mutation_survivors = []
    for generation, logged in enumerate(search.get("generations", []), start=1):
        population_path = ANALYSIS / f"d77a-generation-{generation:02d}-population.tsv"
        rows_path = ANALYSIS / f"d77a-generation-{generation:02d}-rows.tsv"
        timing_path = ANALYSIS / f"d77a-generation-{generation:02d}-time.txt"
        summary_path = ANALYSIS / f"d77a-generation-{generation:02d}-summary.json"
        expected_population = [(label, vectors[label]) for label in current]
        population = population_integrity(population_path, expected_population)
        _, rows = read_tsv(rows_path)
        seed_base = FROZEN["search_seed_base"] + (generation - 1) * FROZEN[
            "maps_per_generation"
        ]
        matrix = validate_matrix(rows, current, seed_base, FROZEN["maps_per_generation"])
        objectives = lineage_objectives(rows, current)
        ranking = rank_labels(objectives)
        survivors = ranking[: FROZEN["survivors"]]
        logged_summary = json.loads(summary_path.read_text())
        hashes_exact = (
            logged.get("population") == sha256_file(population_path)
            and logged.get("rows") == sha256_file(rows_path)
            and logged.get("timing") == sha256_file(timing_path)
            and logged.get("summary") == sha256_file(summary_path)
        )
        lineage_exact = (
            logged.get("labels") == current
            and logged.get("lineage") == {label: lineage[label] for label in current}
            and logged.get("parameter_hashes")
            == {label: vector_hash(vectors[label]) for label in current}
        )
        selection_exact = (
            logged.get("ranking") == ranking
            and logged.get("survivors") == survivors
            and logged_summary.get("ranking") == ranking
            and logged_summary.get("survivors") == survivors
        )
        passed = population["pass"] and matrix["pass"] and hashes_exact and lineage_exact and selection_exact
        generations.append(
            {
                "generation": generation,
                "population": population,
                "matrix": matrix,
                "hashes_exact": hashes_exact,
                "lineage_exact": lineage_exact,
                "selection_exact": selection_exact,
                "best": {"label": ranking[0], **objectives[ranking[0]]},
                "survivor_founders": len({lineage[label]["founder"] for label in survivors}),
                "survivor_depths": [lineage_depth(label, lineage) for label in survivors],
                "timing": parse_timing(timing_path),
                "pass": passed,
            }
        )
        mutation_survivors.append(sum(lineage[label]["parent"] is not None for label in survivors))
        all_pass &= passed
        if generation == FROZEN["generations"]:
            current = survivors
            break
        next_population = list(survivors)
        for parent in survivors:
            for _ in range(FROZEN["children_per_survivor"]):
                label = f"l{next_id:04d}"
                next_id += 1
                vectors[label] = mutate(vectors[parent], rng)
                lineage[label] = {
                    "parent": parent,
                    "founder": lineage[parent]["founder"],
                    "birth_generation": generation + 1,
                }
                next_population.append(label)
        current = next_population

    selection_expected = [(label, vectors[label]) for label in current]
    selection_population = population_integrity(SELECTION_POPULATION, selection_expected)
    _, selection_rows = read_tsv(SELECTION_ROWS)
    selection_matrix = validate_matrix(
        selection_rows,
        current,
        FROZEN["selection_seed_base"],
        FROZEN["selection_maps"],
    )
    selection_objectives = lineage_objectives(selection_rows, current)
    selection_ranking = rank_labels(selection_objectives)
    champion = selection_ranking[0]
    selection_exact = (
        search.get("selection_population") == sha256_file(SELECTION_POPULATION)
        and search.get("selection_rows") == sha256_file(SELECTION_ROWS)
        and search.get("selection_time") == sha256_file(SELECTION_TIME)
        and search.get("selection_ranking") == selection_ranking
        and search.get("champion") == champion
        and search.get("champion_hash") == vector_hash(vectors[champion])
    )
    champion_population = population_integrity(
        CHAMPION_POPULATION, [(champion, vectors[champion])]
    )
    validation_population = population_integrity(
        VALIDATION_POPULATION,
        [("founder_zero", vectors[founder_zero]), ("champion", vectors[champion])],
    )
    metadata_exact = (
        search.get("protocol") == sha256_file(PROTOCOL)
        and search.get("orchestrator") == sha256_file(ORCHESTRATOR)
        and search.get("runner_source") == sha256_file(RUNNER_SOURCE)
        and search.get("runner_binary") == sha256_file(RUNNER)
    )
    all_pass &= (
        selection_population["pass"]
        and selection_matrix["pass"]
        and selection_exact
        and champion_population["pass"]
        and validation_population["pass"]
        and metadata_exact
    )
    return {
        "generations": generations,
        "mutation_survivors_per_generation": mutation_survivors,
        "selection_population": selection_population,
        "selection_matrix": selection_matrix,
        "selection_exact": selection_exact,
        "selection_objectives": selection_objectives,
        "selection_ranking": selection_ranking,
        "champion": champion,
        "champion_hash": vector_hash(vectors[champion]),
        "champion_depth": lineage_depth(champion, lineage),
        "champion_founder": lineage[champion]["founder"],
        "champion_population": champion_population,
        "validation_population": validation_population,
        "metadata_exact": metadata_exact,
        "selection_timing": parse_timing(SELECTION_TIME),
        "pass": all_pass,
    }


def build_report() -> dict:
    search = json.loads(SEARCH_LOG.read_text())
    audit = audit_search(search)
    _, evaluation_a = read_tsv(EVALUATION_A)
    _, evaluation_b = read_tsv(EVALUATION_B)
    matrix_a = validate_matrix(
        evaluation_a,
        ["founder_zero", "champion"],
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    matrix_b = validate_matrix(
        evaluation_b,
        ["founder_zero", "champion"],
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    repeat_exact = EVALUATION_A.read_bytes() == EVALUATION_B.read_bytes()
    anchor = anchor_summary(evaluation_a)
    validation = validation_summary(evaluation_a)
    champion_selection = audit["selection_objectives"][audit["champion"]]
    mechanics_pass = audit["pass"] and matrix_a["pass"] and matrix_b["pass"]
    activity_gates = {
        "ten_generation_and_selection_matrices_complete": (
            len(audit["generations"]) == 10
            and all(row["matrix"]["rows"] == 2_112 for row in audit["generations"])
            and audit["selection_matrix"]["rows"] == 1_152
        ),
        "lineage_mutation_selection_and_hashes_exact": audit["pass"],
        "zero_mechanical_failures": mechanics_pass,
        "founder_anchor_and_repeat_exact": anchor["pass"] and repeat_exact,
        "champion_selection_fitness_at_least_2": (
            champion_selection["eligible"] and champion_selection["fitness"] >= 2
        ),
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
        "worker_three_absolute_and_relative": (
            validation["champion_worker_three_rate"] >= 0.85
            and validation["worker_three_degradation"] <= 0.05
        ),
        "crop_creation_exactly_100pct": validation["crop_creation_rate"] == 1.0,
    }
    activity_pass = all(activity_gates.values())
    value_pass = all(value_gates.values())
    if not mechanics_pass:
        status = "search_mechanics_failure"
        next_experiment = "repair_only_then_repeat_unchanged"
    elif not activity_pass:
        status = "full_recurrent_lineage_activity_failure"
        next_experiment = "new_controller_representation"
    elif not value_pass:
        status = "prospective_champion_value_failure"
        next_experiment = "new_controller_representation"
    else:
        status = "local_champion_pass"
        next_experiment = "layered_fresh_field_qualification"
    return {
        "schema": "troll-farm-d77a-full-recurrent-lineage-result-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "full recurrent actual-policy lineage search and champion validation",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "orchestrator": sha256_file(ORCHESTRATOR),
            "analyzer": sha256_file(Path(__file__)),
            "runner_source": sha256_file(RUNNER_SOURCE),
            "search_log": sha256_file(SEARCH_LOG),
            "champion_population": sha256_file(CHAMPION_POPULATION),
            "evaluation_a": sha256_file(EVALUATION_A),
            "evaluation_b": sha256_file(EVALUATION_B),
            "evaluation_time_a": sha256_file(EVALUATION_TIME_A),
            "evaluation_time_b": sha256_file(EVALUATION_TIME_B),
            "total_time": sha256_file(TOTAL_TIME),
        },
        "search": audit,
        "validation_integrity": {
            "matrix_a": matrix_a,
            "matrix_b": matrix_b,
            "repeat_byte_exact": repeat_exact,
            "founder_anchor": anchor,
            "timings": [parse_timing(EVALUATION_TIME_A), parse_timing(EVALUATION_TIME_B)],
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
            "local_candidate_input": status == "local_champion_pass",
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
                "champion": {
                    "label": report["search"]["champion"],
                    "selection": report["search"]["selection_objectives"][
                        report["search"]["champion"]
                    ],
                },
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
