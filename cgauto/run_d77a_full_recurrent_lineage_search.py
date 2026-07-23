#!/usr/bin/env python3
"""Run D77's frozen full-recurrent actual-policy lineage search."""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402
from cgauto.rl_batch_option_env import OPPONENTS  # noqa: E402
from cgauto.run_d76a_recurrent_readout_cem import (  # noqa: E402
    ACTIONS,
    FEATURES,
    HIDDEN,
    PARAMETERS,
    ROOT,
    RUNNER,
    RUNNER_SOURCE,
    UNLOCKED_ACTION_FIELDS,
    read_tsv,
    validate_matrix,
)


ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d77a-full-recurrent-lineage-search-protocol-2026-07-21.md"
SEARCH_LOG = ANALYSIS / "d77a-full-recurrent-lineage-search.json"
SELECTION_POPULATION = ANALYSIS / "d77a-selection-population.tsv"
SELECTION_ROWS = ANALYSIS / "d77a-selection-rows.tsv"
SELECTION_TIME = ANALYSIS / "d77a-selection-time.txt"
CHAMPION_POPULATION = ANALYSIS / "d77a-champion.tsv"
VALIDATION_POPULATION = ANALYSIS / "d77a-validation-population.tsv"
EVALUATION_A = ANALYSIS / "d77a-evaluation-a.tsv"
EVALUATION_B = ANALYSIS / "d77a-evaluation-b.tsv"
EVALUATION_TIME_A = ANALYSIS / "d77a-evaluation-a-time.txt"
EVALUATION_TIME_B = ANALYSIS / "d77a-evaluation-b-time.txt"

WX_END = HIDDEN * FEATURES
WH_END = WX_END + HIDDEN * HIDDEN
BH_END = WH_END + HIDDEN
WO_END = BH_END + ACTIONS * HIDDEN
BO_END = WO_END + ACTIONS
assert BO_END == PARAMETERS == 1_072

FROZEN = {
    "seed": 7_701,
    "generations": 10,
    "population": 32,
    "survivors": 8,
    "children_per_survivor": 3,
    "maps_per_generation": 4,
    "search_seed_base": 9_816_000,
    "selection_seed_base": 9_816_040,
    "selection_maps": 8,
    "validation_seed_base": 9_817_000,
    "validation_maps": 16,
    "threads": 20,
    "worker_three_relative_floor": 0.05,
    "input_mutation_sigma": 0.02,
    "recurrent_mutation_sigma": 0.02,
    "hidden_bias_mutation_sigma": 0.02,
    "output_mutation_sigma": 0.10,
    "output_bias_mutation_sigma": 0.05,
}


def normalized_vector(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (PARAMETERS,) or not np.isfinite(array).all():
        raise ValueError("invalid D77 parameter vector")
    return np.asarray([f"{float(value):.8f}" for value in array], dtype=np.float32)


def vector_hash(values: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(values, dtype="<f4").tobytes()).hexdigest()


def random_network(rng: np.random.Generator, *, zero_readout: bool = False) -> np.ndarray:
    wx = rng.normal(0.0, 0.35, size=(HIDDEN, FEATURES))
    raw = rng.normal(size=(HIDDEN, HIDDEN))
    q, r = np.linalg.qr(raw)
    signs = np.where(np.diag(r) < 0, -1.0, 1.0)
    wh = q * signs * 0.70
    bh = rng.normal(0.0, 0.10, size=HIDDEN)
    wo = rng.normal(0.0, 0.50, size=(ACTIONS, HIDDEN))
    bo = rng.normal(0.0, 0.15, size=ACTIONS)
    if zero_readout:
        wo.fill(0.0)
        bo.fill(0.0)
    return normalized_vector(np.concatenate((wx.ravel(), wh.ravel(), bh, wo.ravel(), bo)))


def mutate(parent: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    sigma = np.empty(PARAMETERS, dtype=np.float64)
    sigma[:WX_END] = FROZEN["input_mutation_sigma"]
    sigma[WX_END:WH_END] = FROZEN["recurrent_mutation_sigma"]
    sigma[WH_END:BH_END] = FROZEN["hidden_bias_mutation_sigma"]
    sigma[BH_END:WO_END] = FROZEN["output_mutation_sigma"]
    sigma[WO_END:BO_END] = FROZEN["output_bias_mutation_sigma"]
    child = parent.astype(np.float64) + rng.normal(size=PARAMETERS) * sigma
    child[:WX_END] = np.clip(child[:WX_END], -3.0, 3.0)
    child[WX_END:WH_END] = np.clip(child[WX_END:WH_END], -1.5, 1.5)
    child[WH_END:BH_END] = np.clip(child[WH_END:BH_END], -2.0, 2.0)
    child[BH_END:WO_END] = np.clip(child[BH_END:WO_END], -3.0, 3.0)
    child[WO_END:BO_END] = np.clip(child[WO_END:BO_END], -2.0, 2.0)
    return normalized_vector(child)


def write_full_population(path: Path, population: list[tuple[str, np.ndarray]]) -> None:
    if path.exists():
        raise FileExistsError(path)
    fields = ["policy", *(f"param_{index:04}" for index in range(PARAMETERS))]
    with path.open("x", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(fields)
        for label, values in population:
            normalized = normalized_vector(values)
            writer.writerow([label, *(f"{float(value):.8f}" for value in normalized)])


def run_matrix(
    population: Path, output: Path, timing: Path, seed_base: int, maps: int
) -> None:
    for path in (output, timing):
        if path.exists():
            raise FileExistsError(path)
    subprocess.run(
        [
            "/usr/bin/time",
            "-v",
            "-o",
            str(timing),
            str(RUNNER),
            str(population),
            str(output),
            str(seed_base),
            str(maps),
            str(FROZEN["threads"]),
            "ordinary",
        ],
        check=True,
        cwd=ROOT / "rust",
    )


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def lineage_objectives(rows: list[dict[str, str]], labels: list[str]) -> dict[str, dict]:
    grouped: dict[str, dict[tuple[int, int, str], dict[str, str]]] = collections.defaultdict(dict)
    for row in rows:
        grouped[row["policy"]][task_key(row)] = row
    baseline = grouped["balanced"]
    balanced_worker_three = statistics.fmean(
        int(row["own_workers"]) >= 3 for row in baseline.values()
    )
    result = {}
    for label in labels:
        policy = grouped[label]
        deltas = [int(policy[key]["margin"]) - int(baseline[key]["margin"]) for key in baseline]
        own_deltas = [
            int(policy[key]["own_score"]) - int(baseline[key]["own_score"]) for key in baseline
        ]
        family = {
            opponent: statistics.fmean(
                int(policy[key]["margin"]) - int(baseline[key]["margin"])
                for key in baseline
                if key[2] == opponent
            )
            for opponent in OPPONENTS
        }
        worker_three = statistics.fmean(
            int(row["own_workers"]) >= 3 for row in policy.values()
        )
        mean_delta = statistics.fmean(deltas)
        mean_own = statistics.fmean(own_deltas)
        minimum_family = min(family.values())
        p10 = float(np.quantile(np.asarray(deltas, dtype=np.float64), 0.10))
        fitness = (
            mean_delta
            + 0.5 * minimum_family
            + 0.25 * p10
            + 0.5 * min(0.0, mean_own)
        )
        eligible = worker_three + FROZEN["worker_three_relative_floor"] >= balanced_worker_three
        unlocked = sum(int(row["unlocked_decisions"]) for row in policy.values())
        actions = [sum(int(row[field]) for row in policy.values()) for field in UNLOCKED_ACTION_FIELDS]
        result[label] = {
            "eligible": eligible,
            "fitness": fitness,
            "mean_margin_delta": mean_delta,
            "minimum_opponent_family_mean_delta": minimum_family,
            "opponent_family_mean_delta": family,
            "p10_margin_delta": p10,
            "mean_own_score_delta": mean_own,
            "worker_three_rate": worker_three,
            "balanced_worker_three_rate": balanced_worker_three,
            "strict_improvement_rate": statistics.fmean(delta > 0 for delta in deltas),
            "unlocked_decisions": unlocked,
            "unlocked_action_counts": actions,
        }
    return result


def rank_labels(objectives: dict[str, dict]) -> list[str]:
    return sorted(
        objectives,
        key=lambda label: (
            not objectives[label]["eligible"],
            -objectives[label]["fitness"],
            -objectives[label]["minimum_opponent_family_mean_delta"],
            -objectives[label]["mean_margin_delta"],
            -objectives[label]["p10_margin_delta"],
            label,
        ),
    )


def safe_json(value):
    if isinstance(value, dict):
        return {str(key): safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def main() -> int:
    final_artifacts = (
        SEARCH_LOG,
        SELECTION_POPULATION,
        SELECTION_ROWS,
        SELECTION_TIME,
        CHAMPION_POPULATION,
        VALIDATION_POPULATION,
        EVALUATION_A,
        EVALUATION_B,
        EVALUATION_TIME_A,
        EVALUATION_TIME_B,
    )
    if any(path.exists() for path in final_artifacts):
        raise SystemExit("refusing to overwrite D77 artifacts")
    if not RUNNER.is_file() or not os.access(RUNNER, os.X_OK):
        raise SystemExit(f"missing D77 runner: {RUNNER}")

    rng = np.random.Generator(np.random.PCG64(FROZEN["seed"]))
    vectors: dict[str, np.ndarray] = {}
    lineage: dict[str, dict] = {}
    current = []
    next_id = 0
    for founder in range(FROZEN["population"]):
        label = f"l{next_id:04d}"
        next_id += 1
        values = random_network(rng, zero_readout=founder == 0)
        vectors[label] = values
        lineage[label] = {"parent": None, "founder": label, "birth_generation": 1}
        current.append(label)
    founder_zero = current[0]
    generations = []

    for generation in range(1, FROZEN["generations"] + 1):
        population_path = ANALYSIS / f"d77a-generation-{generation:02d}-population.tsv"
        rows_path = ANALYSIS / f"d77a-generation-{generation:02d}-rows.tsv"
        timing_path = ANALYSIS / f"d77a-generation-{generation:02d}-time.txt"
        summary_path = ANALYSIS / f"d77a-generation-{generation:02d}-summary.json"
        for path in (population_path, rows_path, timing_path, summary_path):
            if path.exists():
                raise FileExistsError(path)
        population = [(label, vectors[label]) for label in current]
        write_full_population(population_path, population)
        seed_base = FROZEN["search_seed_base"] + (generation - 1) * FROZEN[
            "maps_per_generation"
        ]
        run_matrix(
            population_path,
            rows_path,
            timing_path,
            seed_base,
            FROZEN["maps_per_generation"],
        )
        _, rows = read_tsv(rows_path)
        integrity = validate_matrix(
            rows, current, seed_base, FROZEN["maps_per_generation"]
        )
        if not integrity["pass"]:
            raise RuntimeError(f"D77 generation {generation} integrity failure: {integrity}")
        objectives = lineage_objectives(rows, current)
        ranking = rank_labels(objectives)
        survivors = ranking[: FROZEN["survivors"]]
        report = {
            "generation": generation,
            "seed_base": seed_base,
            "population": sha256_file(population_path),
            "rows": sha256_file(rows_path),
            "timing": sha256_file(timing_path),
            "labels": current,
            "parameter_hashes": {label: vector_hash(vectors[label]) for label in current},
            "lineage": {label: lineage[label] for label in current},
            "integrity": integrity,
            "objectives": objectives,
            "ranking": ranking,
            "survivors": survivors,
            "rng_state_after_evaluation": safe_json(rng.bit_generator.state),
        }
        atomic_write_new(summary_path, report)
        generations.append({**report, "summary": sha256_file(summary_path)})
        print(
            json.dumps(
                {
                    "event": "generation",
                    "generation": generation,
                    "best": {"label": ranking[0], **objectives[ranking[0]]},
                    "survivors": survivors,
                    "founders": len({lineage[label]["founder"] for label in survivors}),
                },
                sort_keys=True,
            ),
            flush=True,
        )
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
        if len(next_population) != FROZEN["population"]:
            raise RuntimeError("D77 next-population geometry drift")
        current = next_population

    selection = [(label, vectors[label]) for label in current]
    write_full_population(SELECTION_POPULATION, selection)
    run_matrix(
        SELECTION_POPULATION,
        SELECTION_ROWS,
        SELECTION_TIME,
        FROZEN["selection_seed_base"],
        FROZEN["selection_maps"],
    )
    _, selection_rows = read_tsv(SELECTION_ROWS)
    selection_integrity = validate_matrix(
        selection_rows,
        current,
        FROZEN["selection_seed_base"],
        FROZEN["selection_maps"],
    )
    if not selection_integrity["pass"]:
        raise RuntimeError("D77 selection integrity failure")
    selection_objectives = lineage_objectives(selection_rows, current)
    selection_ranking = rank_labels(selection_objectives)
    champion = selection_ranking[0]

    write_full_population(CHAMPION_POPULATION, [(champion, vectors[champion])])
    write_full_population(
        VALIDATION_POPULATION,
        [("founder_zero", vectors[founder_zero]), ("champion", vectors[champion])],
    )
    run_matrix(
        VALIDATION_POPULATION,
        EVALUATION_A,
        EVALUATION_TIME_A,
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    run_matrix(
        VALIDATION_POPULATION,
        EVALUATION_B,
        EVALUATION_TIME_B,
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    _, evaluation_a = read_tsv(EVALUATION_A)
    _, evaluation_b = read_tsv(EVALUATION_B)
    validation_integrity_a = validate_matrix(
        evaluation_a,
        ["founder_zero", "champion"],
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    validation_integrity_b = validate_matrix(
        evaluation_b,
        ["founder_zero", "champion"],
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    repeat_exact = EVALUATION_A.read_bytes() == EVALUATION_B.read_bytes()
    if not validation_integrity_a["pass"] or not validation_integrity_b["pass"] or not repeat_exact:
        raise RuntimeError("D77 validation integrity/repeat failure")

    report = {
        "schema": "troll-farm-d77a-full-recurrent-lineage-search-v1",
        "protocol": sha256_file(PROTOCOL),
        "orchestrator": sha256_file(Path(__file__)),
        "runner_source": sha256_file(RUNNER_SOURCE),
        "runner_binary": sha256_file(RUNNER),
        "frozen": FROZEN,
        "founder_zero": founder_zero,
        "founder_zero_hash": vector_hash(vectors[founder_zero]),
        "generations": generations,
        "lineage": lineage,
        "selection_population": sha256_file(SELECTION_POPULATION),
        "selection_rows": sha256_file(SELECTION_ROWS),
        "selection_time": sha256_file(SELECTION_TIME),
        "selection_integrity": selection_integrity,
        "selection_objectives": selection_objectives,
        "selection_ranking": selection_ranking,
        "champion": champion,
        "champion_hash": vector_hash(vectors[champion]),
        "champion_population": sha256_file(CHAMPION_POPULATION),
        "validation_population": sha256_file(VALIDATION_POPULATION),
        "evaluation_a": sha256_file(EVALUATION_A),
        "evaluation_b": sha256_file(EVALUATION_B),
        "evaluation_time_a": sha256_file(EVALUATION_TIME_A),
        "evaluation_time_b": sha256_file(EVALUATION_TIME_B),
        "evaluation_repeat_byte_exact": repeat_exact,
        "validation_integrity_a": validation_integrity_a,
        "validation_integrity_b": validation_integrity_b,
        "rng_state_final": safe_json(rng.bit_generator.state),
    }
    atomic_write_new(SEARCH_LOG, report)
    print(
        json.dumps(
            {
                "event": "complete",
                "champion": champion,
                "champion_hash": report["champion_hash"],
                "selection": selection_objectives[champion],
                "search_log": sha256_file(SEARCH_LOG),
                "evaluation_repeat_byte_exact": repeat_exact,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
