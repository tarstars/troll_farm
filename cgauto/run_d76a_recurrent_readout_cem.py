#!/usr/bin/env python3
"""Run D76's frozen complete-episode recurrent-readout CEM search."""

from __future__ import annotations

import collections
import csv
import hashlib
import json
import math
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


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d76a-recurrent-readout-cem-protocol-2026-07-21.md"
RUNNER_SOURCE = ROOT / "rust/src/bin/d76_recurrent_readout_population.rs"
RUNNER = ROOT / "rust/target/release/d76_recurrent_readout_population"
SEARCH_LOG = ANALYSIS / "d76a-recurrent-readout-cem-search.json"
FINAL_POPULATION = ANALYSIS / "d76a-recurrent-readout-final.tsv"
VALIDATION_POPULATION = ANALYSIS / "d76a-recurrent-readout-validation-population.tsv"
EVALUATION_A = ANALYSIS / "d76a-recurrent-readout-evaluation-a.tsv"
EVALUATION_B = ANALYSIS / "d76a-recurrent-readout-evaluation-b.tsv"
EVALUATION_TIME_A = ANALYSIS / "d76a-recurrent-readout-evaluation-a-time.txt"
EVALUATION_TIME_B = ANALYSIS / "d76a-recurrent-readout-evaluation-b-time.txt"

FEATURES = 72
HIDDEN = 12
ACTIONS = 4
RESERVOIR_PARAMETERS = HIDDEN * FEATURES + HIDDEN * HIDDEN + HIDDEN
READOUT_PARAMETERS = ACTIONS * HIDDEN + ACTIONS
PARAMETERS = RESERVOIR_PARAMETERS + READOUT_PARAMETERS
ACTION_FIELDS = ("action_balanced", "action_harvest", "action_renew", "action_fell")
UNLOCKED_ACTION_FIELDS = (
    "unlocked_balanced",
    "unlocked_harvest",
    "unlocked_renew",
    "unlocked_fell",
)
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
    "finite_feature_failures",
    "finite_recurrent_failures",
    "legal_mask_failures",
    "boundary_failures",
)
FROZEN = {
    "reservoir_seed": 7_601,
    "search_seed": 7_602,
    "generations": 10,
    "pairs": 16,
    "population": 33,
    "elites": 8,
    "maps_per_generation": 4,
    "search_seed_base": 9_814_000,
    "validation_seed_base": 9_815_000,
    "validation_maps": 16,
    "threads": 20,
    "mean_learning_rate": 0.50,
    "std_old_weight": 0.70,
    "std_elite_weight": 0.30,
    "weight_initial_std": 0.50,
    "bias_initial_std": 0.15,
    "weight_std_floor": 0.03,
    "bias_std_floor": 0.01,
    "std_ceiling": 1.50,
    "mean_clip": 4.0,
    "minimum_generation_worker_three_rate": 0.85,
}


def sha256_array(values: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(values, dtype="<f4").tobytes()).hexdigest()


def fixed_reservoir(seed: int = FROZEN["reservoir_seed"]) -> np.ndarray:
    rng = np.random.Generator(np.random.PCG64(seed))
    wx = rng.normal(0.0, 0.35, size=(HIDDEN, FEATURES))
    raw = rng.normal(size=(HIDDEN, HIDDEN))
    q, r = np.linalg.qr(raw)
    signs = np.where(np.diag(r) < 0, -1.0, 1.0)
    wh = q * signs
    wh *= 0.70
    bh = rng.normal(0.0, 0.10, size=HIDDEN)
    result = np.concatenate((wx.ravel(), wh.ravel(), bh))
    return np.round(result, 8).astype(np.float32)


def full_parameters(reservoir: np.ndarray, readout: np.ndarray) -> np.ndarray:
    values = np.concatenate((reservoir, np.asarray(readout, dtype=np.float32)))
    if values.shape != (PARAMETERS,) or not np.isfinite(values).all():
        raise ValueError("invalid D76 parameter vector")
    return np.round(values, 8).astype(np.float32)


def write_population(
    path: Path, reservoir: np.ndarray, readouts: list[tuple[str, np.ndarray]]
) -> None:
    if path.exists():
        raise FileExistsError(path)
    fields = ["policy", *(f"param_{index:04}" for index in range(PARAMETERS))]
    with path.open("x", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(fields)
        for label, readout in readouts:
            values = full_parameters(reservoir, readout)
            writer.writerow([label, *(f"{float(value):.8f}" for value in values)])


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return tuple(reader.fieldnames or ()), list(reader)


def run_matrix(
    population: Path,
    output: Path,
    timing: Path,
    seed_base: int,
    maps: int,
) -> None:
    for path in (output, timing):
        if path.exists():
            raise FileExistsError(path)
    command = [
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
    ]
    subprocess.run(command, check=True, cwd=ROOT / "rust")


def expected_task_keys(seed_base: int, maps: int) -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(seed_base, seed_base + maps)
        for seat in (0, 1)
        for opponent in OPPONENTS
    }


def validate_matrix(
    rows: list[dict[str, str]],
    labels: list[str],
    seed_base: int,
    maps: int,
) -> dict:
    policies = ["balanced", *labels]
    tasks = expected_task_keys(seed_base, maps)
    expected = {(policy, *task) for policy in policies for task in tasks}
    actual = []
    parse_failures = 0
    failure_totals = collections.Counter()
    action_count_failures = 0
    unlocked_count_failures = 0
    reward_errors = []
    crop_failures = 0
    family_failures = 0
    for row in rows:
        try:
            actual.append(
                (
                    row["policy"],
                    int(row["map_seed"]),
                    int(row["seat"]),
                    row["opponent"],
                )
            )
            family_failures += int(
                row["family"]
                != ("control" if row["policy"] == "balanced" else "recurrent_readout")
            )
            for field in FAILURE_FIELDS:
                failure_totals[field] += int(row[field])
            action_count_failures += int(row["boundary_decisions"]) != sum(
                int(row[field]) for field in ACTION_FIELDS
            )
            unlocked_count_failures += int(row["unlocked_decisions"]) != sum(
                int(row[field]) for field in UNLOCKED_ACTION_FIELDS
            )
            reward_errors.append(float(row["reward_identity_error"]))
            crop_failures += int(int(row["own_created_crops"]) <= 0)
            if not math.isfinite(float(row["maximum_hidden_abs"])):
                raise ValueError("non-finite hidden magnitude")
        except (KeyError, TypeError, ValueError):
            parse_failures += 1
    actual_set = set(actual)
    report = {
        "rows": len(rows),
        "expected_rows": len(expected),
        "complete_grid": len(rows) == len(expected) and actual_set == expected,
        "duplicate_rows": len(rows) - len(actual_set),
        "missing_rows": len(expected - actual_set),
        "unexpected_rows": len(actual_set - expected),
        "parse_failures": parse_failures,
        "family_failures": family_failures,
        "failure_totals": dict(failure_totals),
        "action_count_failures": action_count_failures,
        "unlocked_count_failures": unlocked_count_failures,
        "crop_failures": crop_failures,
        "maximum_reward_identity_error": max(reward_errors, default=float("inf")),
    }
    report["pass"] = (
        report["complete_grid"]
        and report["duplicate_rows"] == 0
        and parse_failures == 0
        and family_failures == 0
        and all(failure_totals.get(field, 0) == 0 for field in FAILURE_FIELDS)
        and action_count_failures == 0
        and unlocked_count_failures == 0
        and crop_failures == 0
        and report["maximum_reward_identity_error"] < 1.0e-4
    )
    return report


def policy_objectives(rows: list[dict[str, str]], labels: list[str]) -> dict[str, dict]:
    grouped: dict[str, dict[tuple[int, int, str], dict[str, str]]] = collections.defaultdict(dict)
    for row in rows:
        grouped[row["policy"]][
            (int(row["map_seed"]), int(row["seat"]), row["opponent"])
        ] = row
    baseline = grouped["balanced"]
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
        worker_three_rate = statistics.fmean(
            int(policy[key]["own_workers"]) >= 3 for key in baseline
        )
        mean_delta = statistics.fmean(deltas)
        mean_own_delta = statistics.fmean(own_deltas)
        minimum_family = min(family.values())
        p10 = float(np.quantile(np.asarray(deltas, dtype=np.float64), 0.10))
        eligible = worker_three_rate >= FROZEN["minimum_generation_worker_three_rate"]
        fitness = (
            mean_delta
            + 0.5 * minimum_family
            + 0.25 * p10
            + 0.5 * min(0.0, mean_own_delta)
            if eligible
            else float("-inf")
        )
        unlocked = sum(int(row["unlocked_decisions"]) for row in policy.values())
        actions = [sum(int(row[field]) for row in policy.values()) for field in UNLOCKED_ACTION_FIELDS]
        result[label] = {
            "eligible": eligible,
            "fitness": fitness,
            "mean_margin_delta": mean_delta,
            "minimum_opponent_family_mean_delta": minimum_family,
            "opponent_family_mean_delta": family,
            "p10_margin_delta": p10,
            "mean_own_score_delta": mean_own_delta,
            "worker_three_rate": worker_three_rate,
            "strict_improvement_rate": statistics.fmean(delta > 0 for delta in deltas),
            "unlocked_decisions": unlocked,
            "unlocked_action_counts": actions,
        }
    return result


def rank_labels(objectives: dict[str, dict]) -> list[str]:
    return sorted(
        objectives,
        key=lambda label: (
            -objectives[label]["fitness"],
            -objectives[label]["minimum_opponent_family_mean_delta"],
            -objectives[label]["mean_margin_delta"],
            label,
        ),
    )


def population_readouts(
    mean: np.ndarray, std: np.ndarray, rng: np.random.Generator, generation: int
) -> list[tuple[str, np.ndarray]]:
    if mean.shape != (READOUT_PARAMETERS,) or std.shape != (READOUT_PARAMETERS,):
        raise ValueError("D76 CEM shape drift")
    rows = [(f"g{generation:02d}_mean", np.round(mean, 8).astype(np.float32))]
    noises = rng.standard_normal((FROZEN["pairs"], READOUT_PARAMETERS))
    for index, noise in enumerate(noises):
        rows.append(
            (
                f"g{generation:02d}_p{index:02d}",
                np.round(mean + std * noise, 8).astype(np.float32),
            )
        )
        rows.append(
            (
                f"g{generation:02d}_m{index:02d}",
                np.round(mean - std * noise, 8).astype(np.float32),
            )
        )
    if len(rows) != FROZEN["population"]:
        raise RuntimeError("D76 population size drift")
    return rows


def update_distribution(
    mean: np.ndarray,
    std: np.ndarray,
    readouts: dict[str, np.ndarray],
    elites: list[str],
) -> tuple[np.ndarray, np.ndarray]:
    values = np.stack([readouts[label] for label in elites]).astype(np.float64)
    elite_mean = values.mean(axis=0)
    elite_std = values.std(axis=0)
    new_mean = (1.0 - FROZEN["mean_learning_rate"]) * mean + FROZEN[
        "mean_learning_rate"
    ] * elite_mean
    new_mean = np.clip(new_mean, -FROZEN["mean_clip"], FROZEN["mean_clip"])
    floor = np.concatenate(
        (
            np.full(ACTIONS * HIDDEN, FROZEN["weight_std_floor"]),
            np.full(ACTIONS, FROZEN["bias_std_floor"]),
        )
    )
    new_std = FROZEN["std_old_weight"] * std + FROZEN["std_elite_weight"] * elite_std
    new_std = np.clip(new_std, floor, FROZEN["std_ceiling"])
    return np.round(new_mean, 8), np.round(new_std, 8)


def json_safe(value):
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def main() -> int:
    required_absent = (
        SEARCH_LOG,
        FINAL_POPULATION,
        VALIDATION_POPULATION,
        EVALUATION_A,
        EVALUATION_B,
        EVALUATION_TIME_A,
        EVALUATION_TIME_B,
    )
    if any(path.exists() for path in required_absent):
        raise SystemExit("refusing to overwrite D76 final artifacts")
    if not RUNNER.is_file() or not os.access(RUNNER, os.X_OK):
        raise SystemExit(f"missing executable D76 runner: {RUNNER}")
    if PARAMETERS != 1_072 or READOUT_PARAMETERS != 52:
        raise RuntimeError("D76 frozen geometry mismatch")

    reservoir = fixed_reservoir()
    mean = np.zeros(READOUT_PARAMETERS, dtype=np.float64)
    std = np.concatenate(
        (
            np.full(ACTIONS * HIDDEN, FROZEN["weight_initial_std"]),
            np.full(ACTIONS, FROZEN["bias_initial_std"]),
        )
    ).astype(np.float64)
    rng = np.random.Generator(np.random.PCG64(FROZEN["search_seed"]))
    generations = []
    all_mechanics_pass = True

    for generation in range(1, FROZEN["generations"] + 1):
        population_path = ANALYSIS / f"d76a-generation-{generation:02d}-population.tsv"
        rows_path = ANALYSIS / f"d76a-generation-{generation:02d}-rows.tsv"
        timing_path = ANALYSIS / f"d76a-generation-{generation:02d}-time.txt"
        summary_path = ANALYSIS / f"d76a-generation-{generation:02d}-summary.json"
        for path in (population_path, rows_path, timing_path, summary_path):
            if path.exists():
                raise FileExistsError(path)
        population = population_readouts(mean, std, rng, generation)
        readouts = {label: values.astype(np.float64) for label, values in population}
        write_population(population_path, reservoir, population)
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
        labels = [label for label, _ in population]
        integrity = validate_matrix(
            rows, labels, seed_base, FROZEN["maps_per_generation"]
        )
        if not integrity["pass"]:
            raise RuntimeError(f"D76 generation {generation} integrity failure: {integrity}")
        objectives = policy_objectives(rows, labels)
        ranking = rank_labels(objectives)
        elites = ranking[: FROZEN["elites"]]
        mean_before = mean.copy()
        std_before = std.copy()
        mean, std = update_distribution(mean, std, readouts, elites)
        report = {
            "generation": generation,
            "seed_base": seed_base,
            "maps": FROZEN["maps_per_generation"],
            "population": sha256_file(population_path),
            "rows": sha256_file(rows_path),
            "timing": sha256_file(timing_path),
            "integrity": integrity,
            "mean_before_hash": sha256_array(mean_before),
            "std_before_hash": sha256_array(std_before),
            "ranking": ranking,
            "elites": elites,
            "objectives": objectives,
            "mean_after": mean.tolist(),
            "std_after": std.tolist(),
            "mean_after_hash": sha256_array(mean),
            "std_after_hash": sha256_array(std),
            "rng_state_after": json_safe(rng.bit_generator.state),
        }
        atomic_write_new(summary_path, report)
        generations.append({**report, "summary": sha256_file(summary_path)})
        all_mechanics_pass &= integrity["pass"]
        print(
            json.dumps(
                {
                    "event": "generation",
                    "generation": generation,
                    "elite_fitness": [objectives[label]["fitness"] for label in elites],
                    "mean_member": objectives[f"g{generation:02d}_mean"],
                    "best": {"label": ranking[0], **objectives[ranking[0]]},
                    "mean_after_l2": float(np.linalg.norm(mean)),
                    "std_mean": float(std.mean()),
                },
                sort_keys=True,
            ),
            flush=True,
        )

    final_readout = np.round(mean, 8).astype(np.float32)
    zero_readout = np.zeros(READOUT_PARAMETERS, dtype=np.float32)
    write_population(FINAL_POPULATION, reservoir, [("final", final_readout)])
    write_population(
        VALIDATION_POPULATION,
        reservoir,
        [("initial", zero_readout), ("final", final_readout)],
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
        ["initial", "final"],
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    validation_integrity_b = validate_matrix(
        evaluation_b,
        ["initial", "final"],
        FROZEN["validation_seed_base"],
        FROZEN["validation_maps"],
    )
    repeat_exact = EVALUATION_A.read_bytes() == EVALUATION_B.read_bytes()
    if not validation_integrity_a["pass"] or not validation_integrity_b["pass"] or not repeat_exact:
        raise RuntimeError("D76 validation integrity/repeat failure")

    report = {
        "schema": "troll-farm-d76a-recurrent-readout-cem-search-v1",
        "protocol": sha256_file(PROTOCOL),
        "orchestrator": sha256_file(Path(__file__)),
        "runner_source": sha256_file(RUNNER_SOURCE),
        "runner_binary": sha256_file(RUNNER),
        "frozen": FROZEN,
        "geometry": {
            "features": FEATURES,
            "hidden": HIDDEN,
            "actions": ACTIONS,
            "reservoir_parameters": RESERVOIR_PARAMETERS,
            "readout_parameters": READOUT_PARAMETERS,
            "total_parameters": PARAMETERS,
        },
        "reservoir_hash": sha256_array(reservoir),
        "initial_mean_hash": sha256_array(np.zeros(READOUT_PARAMETERS)),
        "final_mean": final_readout.tolist(),
        "final_mean_hash": sha256_array(final_readout),
        "final_mean_l2": float(np.linalg.norm(final_readout)),
        "final_std": std.tolist(),
        "final_std_hash": sha256_array(std),
        "generations": generations,
        "all_search_mechanics_pass": all_mechanics_pass,
        "final_population": sha256_file(FINAL_POPULATION),
        "validation_population": sha256_file(VALIDATION_POPULATION),
        "evaluation_a": sha256_file(EVALUATION_A),
        "evaluation_b": sha256_file(EVALUATION_B),
        "evaluation_time_a": sha256_file(EVALUATION_TIME_A),
        "evaluation_time_b": sha256_file(EVALUATION_TIME_B),
        "evaluation_repeat_byte_exact": repeat_exact,
        "validation_integrity_a": validation_integrity_a,
        "validation_integrity_b": validation_integrity_b,
    }
    atomic_write_new(SEARCH_LOG, report)
    print(
        json.dumps(
            {
                "event": "complete",
                "search_log": sha256_file(SEARCH_LOG),
                "final_mean_l2": report["final_mean_l2"],
                "evaluation_repeat_byte_exact": repeat_exact,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
