#!/usr/bin/env python3
"""Run D111a's diverse actual-policy lineage search over one-use q6 controllers."""

from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cgauto import analyze_d110a_robust_one_use_q6_population as d110  # noqa: E402
from cgauto import make_d110a_antithetic_q6_linear_population as population_io  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d111a-diverse-one-use-q6-linear-lineage-protocol-2026-07-22.md"
RUNNER_SOURCE = ROOT / "rust/src/bin/d107_q6_proposal_controller_population.rs"
RUNNER = ROOT / "rust/target/release/d107_q6_proposal_controller_population"
EXPERTS = BASE / "d105a-q6-expert-population.tsv"
D110_RESULT = BASE / "d110a-robust-one-use-q6-linear-discovery-result.json"
OUTPUT = BASE / "d111a-diverse-one-use-q6-linear-lineage-result.json"

EXPECTED_HASHES: dict[Path, str] = {
    PROTOCOL: "5b2e54764a7f4c87fce599849ead935188a2e3f61b07debf382e72b7adc76721",
    RUNNER_SOURCE: "2bd7e3c5628cf048af61082aba848bb6ea6f66d3967e4ee056823679693d0514",
    RUNNER: "96030ca2ab75e7b98b74942863b9b4c53124790bf62bf7c6946ab546e3a78547",
    EXPERTS: "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8",
    D110_RESULT: "64333cf8d29743281c25be481b1470c4d817a24dd3d90dd6a7021c51d7f6321b",
    ROOT / "cgauto/analyze_d110a_robust_one_use_q6_population.py":
        "52e05c8cc1e1feeace487b6cbeaa321eb79458b3e96425ab41e4bb2f9b7ba513",
    ROOT / "cgauto/make_d110a_antithetic_q6_linear_population.py":
        "13cbe478d2d725a25608d1a2e5dd6089a89ca0d1dc9ed4927857228af62d41f5",
}

FROZEN = {
    "seed": 11_101,
    "generations": 5,
    "population": 64,
    "survivors": 8,
    "children_per_survivor": 7,
    "founder_survivor_cap": 2,
    "maps_per_generation": 4,
    "search_seed_base": 9_841_000,
    "selection_seed_base": 9_841_100,
    "selection_maps": 16,
    "held_seed_base": 9_842_000,
    "held_maps": 32,
    "threads": 20,
    "weight_sd": 0.25,
    "threshold_step": 0.15,
    "threshold_levels": 16,
    "threshold_mutation_sigma": 0.10,
    "weight_mutation_sigma": 0.025,
    "activity_min": 0.10,
    "activity_max": 0.85,
    "activity_penalty": 20.0,
    "worker_three_relative_floor": 0.05,
}
FEATURES = population_io.FEATURES
OPPONENTS = d110.OPPONENTS


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_vector(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    if values.shape != (FEATURES,) or not np.isfinite(values).all():
        raise ValueError("invalid D111a vector")
    return np.asarray([f"{float(value):.8f}" for value in values], dtype=np.float32)


def vector_hash(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype="<f4").tobytes()).hexdigest()


def founder_vector(rng: np.random.Generator, index: int) -> np.ndarray:
    values = rng.normal(0.0, FROZEN["weight_sd"], size=FEATURES)
    values[0] = -FROZEN["threshold_step"] * (1 + index % FROZEN["threshold_levels"])
    return normalized_vector(values)


def mutate(parent: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    child = parent.astype(np.float64).copy()
    child[0] += rng.normal(0.0, FROZEN["threshold_mutation_sigma"])
    child[1:] += rng.normal(0.0, FROZEN["weight_mutation_sigma"], size=FEATURES - 1)
    child[0] = np.clip(child[0], -3.0, 0.0)
    child[1:] = np.clip(child[1:], -1.5, 1.5)
    return normalized_vector(child)


def runner_population(labels: list[str], vectors: dict[str, np.ndarray]) -> list[dict]:
    if len(labels) > FROZEN["population"] or not labels:
        raise ValueError("invalid D111a runner population")
    padded = list(labels) + [labels[0]] * (FROZEN["population"] - len(labels))
    rows = [
        {
            "policy": "zero_control",
            "kind": "zero",
            "budget": 4,
            "parameters": [0.0] * FEATURES,
        }
    ]
    for index, label in enumerate(padded):
        parameters = vectors[label].tolist()
        for kind, budget in (("one", 1), ("four", 4)):
            rows.append(
                {
                    "policy": f"{kind}_{index:02d}",
                    "kind": kind,
                    "budget": budget,
                    "parameters": parameters,
                }
            )
    return rows


def write_population(path: Path, labels: list[str], vectors: dict[str, np.ndarray]) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.write_text(population_io.render(runner_population(labels, vectors)))


def run_matrix(
    population: Path,
    rows: Path,
    baselines: Path,
    seed_base: int,
    maps: int,
    controller_limit: int | None = None,
) -> dict:
    for path in (rows, baselines):
        if path.exists():
            raise FileExistsError(path)
    command = [
        str(RUNNER),
        str(EXPERTS),
        str(population),
        str(seed_base),
        str(maps),
        str(rows),
        str(baselines),
        str(FROZEN["threads"]),
    ]
    if controller_limit is not None:
        command.append(str(controller_limit))
    started = time.perf_counter()
    subprocess.run(command, cwd=ROOT, check=True)
    return {
        "wall_seconds": time.perf_counter() - started,
        "rows": sha256(rows),
        "baselines": sha256(baselines),
    }


def task_deltas(
    rows: list[dict[str, str]], baselines: list[dict[str, str]], policy: str
) -> list[int]:
    baseline = {d110.task_key(row): row for row in baselines}
    return [
        int(row["margin"]) - int(baseline[d110.task_key(row)]["margin"])
        for row in rows
        if row["policy"] == policy
    ]


def objective(
    metrics: dict, deltas: list[int], control_worker_rate: float
) -> dict:
    p10 = float(np.quantile(np.asarray(deltas, dtype=np.float64), 0.10))
    upper = max(0.0, metrics["intervention_rate"] - FROZEN["activity_max"])
    lower = max(0.0, FROZEN["activity_min"] - metrics["intervention_rate"])
    activity_penalty = FROZEN["activity_penalty"] * (upper + lower)
    fitness = (
        metrics["mean_margin_delta"]
        + 0.5 * metrics["worst_family"]
        + 0.25 * p10
        + 0.5 * min(0.0, metrics["mean_own_score_delta"])
        - activity_penalty
    )
    safe = (
        metrics["crop_rate"] == 1.0
        and metrics["worker_three_rate"]
        >= control_worker_rate - FROZEN["worker_three_relative_floor"]
    )
    return {
        "eligible": safe,
        "fitness": fitness,
        "p10_margin_delta": p10,
        "activity_penalty": activity_penalty,
        **metrics,
    }


def rank_labels(objectives: dict[str, dict]) -> list[str]:
    return sorted(
        objectives,
        key=lambda label: (
            not objectives[label]["eligible"],
            -objectives[label]["fitness"],
            -objectives[label]["worst_family"],
            -objectives[label]["mean_margin_delta"],
            abs(objectives[label]["intervention_rate"] - 0.50),
            label,
        ),
    )


def diverse_survivors(
    ranking: list[str], lineage: dict[str, dict], objectives: dict[str, dict]
) -> list[str]:
    result = []
    counts: dict[str, int] = defaultdict(int)
    for label in ranking:
        if not objectives[label]["eligible"]:
            continue
        founder = lineage[label]["founder"]
        if counts[founder] >= FROZEN["founder_survivor_cap"]:
            continue
        result.append(label)
        counts[founder] += 1
        if len(result) == FROZEN["survivors"]:
            return result
    raise RuntimeError("D111a cannot fill diverse safe survivors")


def matrix_analysis(
    rows_path: Path,
    baselines_path: Path,
    seed_base: int,
    maps: int,
    labels: list[str],
    *,
    selection_folds: bool = False,
) -> tuple[dict, dict[str, dict], list[dict[str, str]], list[dict[str, str]]]:
    rows, _ = d110.read_table(rows_path)
    baselines, _ = d110.read_table(baselines_path)
    tasks = d110.expected_tasks(seed_base, maps)
    policy_names = {"zero_control"} | {
        f"{kind}_{index:02d}"
        for kind in ("one", "four")
        for index in range(len(labels))
    }
    integrity = d110.validate_grid(rows, baselines, tasks, policy_names)
    mechanics_pass = (
        integrity["complete"]
        and integrity["zero_exact"]
        and integrity["finite"]
        and integrity["maximum_reward_identity_error"] < 1.0e-4
        and not any(integrity["mechanical_failures"].values())
        and not integrity["counter_violations"]
    )
    if not mechanics_pass:
        raise RuntimeError(f"D111a matrix integrity failure: {integrity}")
    control_worker_rate = d110.mean(int(row["own_workers"]) >= 3 for row in baselines)
    objectives = {}
    for index, label in enumerate(labels):
        policy = f"one_{index:02d}"
        metrics = d110.policy_metrics(
            rows, baselines, policy, seed_base if selection_folds else None
        )
        objectives[label] = objective(
            metrics, task_deltas(rows, baselines, policy), control_worker_rate
        )
    return (
        {"mechanics_pass": mechanics_pass, "integrity": integrity, "control_worker_rate": control_worker_rate},
        objectives,
        rows,
        baselines,
    )


def safe_json(value):
    if isinstance(value, dict):
        return {str(key): safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    return value


def main() -> int:
    if OUTPUT.exists() or any(BASE.glob("d111a-generation-*-population.tsv")):
        raise SystemExit("refusing to overwrite D111a artifacts")
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise SystemExit(f"D111a prerequisite hash mismatch: {path}: {actual}")
    if not RUNNER.is_file() or not os.access(RUNNER, os.X_OK):
        raise SystemExit("D111a runner is not executable")

    rng = np.random.Generator(np.random.PCG64(FROZEN["seed"]))
    vectors: dict[str, np.ndarray] = {}
    lineage: dict[str, dict] = {}
    current = []
    next_id = 0
    for index in range(FROZEN["population"]):
        label = f"l{next_id:04d}"
        next_id += 1
        vectors[label] = founder_vector(rng, index)
        lineage[label] = {"parent": None, "founder": label, "birth_generation": 1}
        current.append(label)
    generations = []

    for generation in range(1, FROZEN["generations"] + 1):
        stem = BASE / f"d111a-generation-{generation:02d}"
        population_path = Path(str(stem) + "-population.tsv")
        rows_path = Path(str(stem) + "-rows.tsv")
        baselines_path = Path(str(stem) + "-baselines.tsv")
        summary_path = Path(str(stem) + "-summary.json")
        write_population(population_path, current, vectors)
        seed_base = FROZEN["search_seed_base"] + (generation - 1) * FROZEN["maps_per_generation"]
        execution = run_matrix(
            population_path, rows_path, baselines_path, seed_base, FROZEN["maps_per_generation"]
        )
        integrity, objectives, _, _ = matrix_analysis(
            rows_path, baselines_path, seed_base, FROZEN["maps_per_generation"], current
        )
        ranking = rank_labels(objectives)
        survivors = diverse_survivors(ranking, lineage, objectives)
        report = {
            "generation": generation,
            "seed_base": seed_base,
            "population_hash": sha256(population_path),
            "execution": execution,
            "labels": current,
            "parameter_hashes": {label: vector_hash(vectors[label]) for label in current},
            "lineage": {label: lineage[label] for label in current},
            "integrity": integrity,
            "objectives": objectives,
            "ranking": ranking,
            "survivors": survivors,
        }
        summary_path.write_text(json.dumps(safe_json(report), indent=2, sort_keys=True) + "\n")
        report["summary_hash"] = sha256(summary_path)
        generations.append(report)
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
            raise RuntimeError("D111a population geometry drift")
        current = next_population

    selection_population = BASE / "d111a-selection-population.tsv"
    selection_rows = BASE / "d111a-selection-rows.tsv"
    selection_baselines = BASE / "d111a-selection-baselines.tsv"
    write_population(selection_population, current, vectors)
    selection_execution = run_matrix(
        selection_population,
        selection_rows,
        selection_baselines,
        FROZEN["selection_seed_base"],
        FROZEN["selection_maps"],
        1 + 2 * len(current),
    )
    selection_integrity, selection_objectives, _, selection_control = matrix_analysis(
        selection_rows,
        selection_baselines,
        FROZEN["selection_seed_base"],
        FROZEN["selection_maps"],
        current,
        selection_folds=True,
    )
    control_worker_rate = d110.mean(int(row["own_workers"]) >= 3 for row in selection_control)
    admission = {
        label: d110.discovery_admission(metrics, control_worker_rate)
        for label, metrics in selection_objectives.items()
    }
    admitted = [label for label, gates in admission.items() if all(gates.values())]
    selection_ranking = [label for label in rank_labels(selection_objectives) if label in admitted]
    champion = selection_ranking[0] if selection_ranking else None

    result = {
        "schema": "troll-farm-d111a-diverse-one-use-q6-linear-lineage-v1",
        "inputs": {
            "protocol": sha256(PROTOCOL),
            "orchestrator": sha256(Path(__file__)),
            "runner_source": sha256(RUNNER_SOURCE),
            "runner_binary": sha256(RUNNER),
            "experts": sha256(EXPERTS),
            "d110_result": sha256(D110_RESULT),
        },
        "frozen": FROZEN,
        "generations": generations,
        "lineage": lineage,
        "selection": {
            "population": sha256(selection_population),
            "execution": selection_execution,
            "integrity": selection_integrity,
            "objectives": selection_objectives,
            "admission": admission,
            "admitted": admitted,
            "ranking": selection_ranking,
            "champion": champion,
            "champion_hash": vector_hash(vectors[champion]) if champion else None,
        },
    }
    if champion is None:
        result["decision"] = "close_diverse_one_use_lineage_before_held"
        OUTPUT.write_text(json.dumps(safe_json(result), indent=2, sort_keys=True) + "\n")
        print(json.dumps({"event": "complete", "decision": result["decision"]}, sort_keys=True))
        return 0

    champion_population = BASE / "d111a-champion-population.tsv"
    held_rows_a = BASE / "d111a-held-a-rows.tsv"
    held_rows_b = BASE / "d111a-held-b-rows.tsv"
    held_baselines_a = BASE / "d111a-held-a-baselines.tsv"
    held_baselines_b = BASE / "d111a-held-b-baselines.tsv"
    write_population(champion_population, [champion], vectors)
    held_execution_a = run_matrix(
        champion_population,
        held_rows_a,
        held_baselines_a,
        FROZEN["held_seed_base"],
        FROZEN["held_maps"],
        3,
    )
    held_execution_b = run_matrix(
        champion_population,
        held_rows_b,
        held_baselines_b,
        FROZEN["held_seed_base"],
        FROZEN["held_maps"],
        3,
    )
    held_integrity_a, held_objectives, _, held_control = matrix_analysis(
        held_rows_a,
        held_baselines_a,
        FROZEN["held_seed_base"],
        FROZEN["held_maps"],
        [champion],
    )
    held_integrity_b, _, _, _ = matrix_analysis(
        held_rows_b,
        held_baselines_b,
        FROZEN["held_seed_base"],
        FROZEN["held_maps"],
        [champion],
    )
    held_metrics = held_objectives[champion]
    held_control_worker_rate = d110.mean(int(row["own_workers"]) >= 3 for row in held_control)
    held_gates = d110.held_value_gates(held_metrics, held_control_worker_rate)
    repeat_exact = (
        held_rows_a.read_bytes() == held_rows_b.read_bytes()
        and held_baselines_a.read_bytes() == held_baselines_b.read_bytes()
    )
    full_pass = repeat_exact and all(held_gates.values())
    result["held"] = {
        "champion_population": sha256(champion_population),
        "execution_a": held_execution_a,
        "execution_b": held_execution_b,
        "rows_a": sha256(held_rows_a),
        "rows_b": sha256(held_rows_b),
        "baselines_a": sha256(held_baselines_a),
        "baselines_b": sha256(held_baselines_b),
        "integrity_a": held_integrity_a,
        "integrity_b": held_integrity_b,
        "repeat_exact": repeat_exact,
        "metrics": held_metrics,
        "gates": held_gates,
        "full_pass": full_pass,
    }
    result["decision"] = (
        "open_deployable_reconstruction_and_confirmation"
        if full_pass
        else "close_diverse_one_use_lineage"
    )
    OUTPUT.write_text(json.dumps(safe_json(result), indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "event": "complete",
                "champion": champion,
                "held": held_metrics,
                "gates": held_gates,
                "decision": result["decision"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
