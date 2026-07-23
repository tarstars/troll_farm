#!/usr/bin/env python3
"""Analyze D110a discovery and repeated held one-use q6 population runs."""

from __future__ import annotations

from collections import Counter
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cgauto import make_d110a_antithetic_q6_linear_population as generator


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = BASE / "d110a-robust-one-use-q6-linear-population-protocol-2026-07-22.md"
GENERATOR = ROOT / "cgauto/make_d110a_antithetic_q6_linear_population.py"
RUNNER = ROOT / "rust/src/bin/d107_q6_proposal_controller_population.rs"
BINARY = ROOT / "rust/target/release/d107_q6_proposal_controller_population"
EXPERTS = BASE / "d105a-q6-expert-population.tsv"
POPULATION = BASE / "d110a-antithetic-q6-linear-population.tsv"
D107_RESULT = BASE / "d107a-q6-bounded-online-controller-preflight-result.json"
D109_RESULT = BASE / "d109a-duration-only-recurrent-q6-ppo-result.json"
DISCOVERY_ROWS = BASE / "d110a-q6-linear-discovery-rows-9838000-9838015.tsv"
DISCOVERY_BASELINES = BASE / "d110a-q6-linear-discovery-baselines-9838000-9838015.tsv"
DISCOVERY_RESULT = BASE / "d110a-robust-one-use-q6-linear-discovery-result.json"
SELECTED_POPULATION = BASE / "d110a-selected-one-use-q6-linear-population.tsv"
HELD_ROWS_A = BASE / "d110a-q6-linear-held-a-9839000-9839031.tsv"
HELD_ROWS_B = BASE / "d110a-q6-linear-held-b-9839000-9839031.tsv"
HELD_BASELINES_A = BASE / "d110a-q6-linear-held-baselines-a-9839000-9839031.tsv"
HELD_BASELINES_B = BASE / "d110a-q6-linear-held-baselines-b-9839000-9839031.tsv"
OUTPUT = BASE / "d110a-robust-one-use-q6-linear-population-result.json"

EXPECTED_HASHES: dict[Path, str] = {
    PROTOCOL: "2703434c1f10316feada795af5f32fd1fab2d2969ff97f6471a1c1f2e3ce5bc1",
    GENERATOR: "13cbe478d2d725a25608d1a2e5dd6089a89ca0d1dc9ed4927857228af62d41f5",
    RUNNER: "2bd7e3c5628cf048af61082aba848bb6ea6f66d3967e4ee056823679693d0514",
    BINARY: "96030ca2ab75e7b98b74942863b9b4c53124790bf62bf7c6946ab546e3a78547",
    EXPERTS: "87c6ed7d018983b72bcc158b6de0aafd6174873d180fb5f3af51f787f3c03fd8",
    POPULATION: "d68eb48e5c091c02472b33c2b6d251dd3bc37dce34a1e06f41908c3e45f6aabb",
    D107_RESULT: "8ab7ca603686cf4bf26e6026429f7df57fc395242bdb4d8606a10c1b28c989c2",
    D109_RESULT: "22ebe0a9bf3f992e0ed88d92cbbbf1e4b7a8fb1ed635e8d8737a804eeb469e1f",
}

DISCOVERY_START = 9_838_000
DISCOVERY_MAPS = 16
HELD_START = 9_839_000
HELD_MAPS = 32
OPPONENTS = (
    "resident",
    "compact_gold",
    "gold_adaptive",
    "silver_boss",
    "legend_balanced",
    "norx_native_three",
    "script_boss",
    "mybot",
)
TASK_FIELDS = ("map_seed", "seat", "opponent")
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
)
JOB_FIELDS = ("concrete_fell", "concrete_harvest", "concrete_renew", "concrete_mine")
OWNER_FIELDS = ("owner_natural", "owner_own", "owner_opponent", "owner_ambiguous")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def expected_tasks(start: int, maps: int) -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(start, start + maps)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def mean(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def counter_violations(rows: list[dict[str, str]]) -> list[str]:
    violations = []
    for row in rows:
        interventions = int(row["intervention_batches"])
        joint = int(row["joint_batches"])
        first = int(row["single_first_batches"])
        second = int(row["single_second_batches"])
        nonkeep = int(row["nonkeep_assignments"])
        proposals = int(row["proposal_occurrences"])
        eligible = int(row["eligible_batches"])
        supporters = int(row["supporter_occurrences"])
        valid = (
            interventions <= int(row["budget"])
            and joint + first + second == interventions
            and nonkeep == 2 * joint + first + second
            and sum(int(row[field]) for field in JOB_FIELDS) == nonkeep
            and sum(int(row[field]) for field in OWNER_FIELDS) <= nonkeep
            and proposals == 64 * eligible
            and supporters == proposals
            and (row["kind"] != "zero" or interventions == 0)
        )
        if not valid:
            violations.append(
                f"{row['policy']}:{row['map_seed']}:{row['seat']}:{row['opponent']}"
            )
    return violations


def validate_grid(
    rows: list[dict[str, str]],
    baselines: list[dict[str, str]],
    tasks: set[tuple[int, int, str]],
    policies: set[str],
) -> dict:
    grid = Counter((row["policy"], task_key(row)) for row in rows)
    baseline_by_task = {task_key(row): row for row in baselines}
    complete = (
        len(rows) == len(tasks) * len(policies)
        and len(baselines) == len(tasks)
        and set(grid) == {(policy, task) for policy in policies for task in tasks}
        and all(value == 1 for value in grid.values())
        and set(baseline_by_task) == tasks
    )
    baseline_fields = tuple(baselines[0].keys())[3:] if baselines else ()
    zero_rows = [row for row in rows if row["policy"] == "zero_control"]
    zero_exact = len(zero_rows) == len(tasks) and all(
        all(row[field] == baseline_by_task[task_key(row)][field] for field in baseline_fields)
        for row in zero_rows
    )
    maximum_reward_error = max(
        (abs(float(row["reward_identity_error"])) for row in rows), default=math.inf
    )
    failures = {field: sum(int(row[field]) for row in rows) for field in FAILURE_FIELDS}
    return {
        "complete": complete,
        "zero_exact": zero_exact,
        "finite": all(
            math.isfinite(float(row[field]))
            for row in rows
            for field in ("own_return", "opponent_return", "margin_return", "reward_identity_error")
        ),
        "maximum_reward_identity_error": maximum_reward_error,
        "mechanical_failures": failures,
        "counter_violations": counter_violations(rows),
    }


def policy_metrics(
    rows: list[dict[str, str]],
    baselines: list[dict[str, str]],
    policy: str,
    discovery_start: int | None = None,
) -> dict:
    baseline = {task_key(row): row for row in baselines}
    selected = [row for row in rows if row["policy"] == policy]
    enriched = []
    for row in selected:
        control = baseline[task_key(row)]
        enriched.append(
            {
                "map_seed": int(row["map_seed"]),
                "opponent": row["opponent"],
                "margin": int(row["margin"]) - int(control["margin"]),
                "own": int(row["own_score"]) - int(control["own_score"]),
                "rival": int(row["opponent_score"]) - int(control["opponent_score"]),
                "intervened": int(row["intervention_batches"]) > 0,
                "crop": int(row["own_created_crops"]) > 0,
                "worker_three": int(row["own_workers"]) >= 3,
            }
        )
    families = {
        opponent: mean(item["margin"] for item in enriched if item["opponent"] == opponent)
        for opponent in OPPONENTS
    }
    result = {
        "tasks": len(enriched),
        "mean_margin_delta": mean(item["margin"] for item in enriched),
        "strict_improvement_rate": mean(item["margin"] > 0 for item in enriched),
        "mean_own_score_delta": mean(item["own"] for item in enriched),
        "mean_opponent_score_delta": mean(item["rival"] for item in enriched),
        "family_mean_margin_delta": families,
        "positive_families": sum(value > 0 for value in families.values()),
        "worst_family": min(families.values()),
        "intervention_rate": mean(item["intervened"] for item in enriched),
        "crop_rate": mean(item["crop"] for item in enriched),
        "worker_three_rate": mean(item["worker_three"] for item in enriched),
    }
    if discovery_start is not None:
        result["fold_mean_margin_delta"] = {
            str(fold): mean(
                item["margin"]
                for item in enriched
                if (item["map_seed"] - discovery_start) % 2 == fold
            )
            for fold in range(2)
        }
    return result


def discovery_admission(metrics: dict, control_worker_rate: float) -> dict[str, bool]:
    folds = metrics["fold_mean_margin_delta"]
    return {
        "mean_at_least_1_5": metrics["mean_margin_delta"] >= 1.5,
        "strict_at_least_30pct": metrics["strict_improvement_rate"] >= 0.30,
        "both_fold_means_nonnegative": min(folds.values()) >= 0.0,
        "worst_family_at_least_minus5": metrics["worst_family"] >= -5.0,
        "five_positive_families": metrics["positive_families"] >= 5,
        "own_nonnegative_or_opponent_nonpositive": (
            metrics["mean_own_score_delta"] >= 0.0
            or metrics["mean_opponent_score_delta"] <= 0.0
        ),
        "activity_10_to_85pct": 0.10 <= metrics["intervention_rate"] <= 0.85,
        "crop_100pct": metrics["crop_rate"] == 1.0,
        "worker_three_within_5pp": metrics["worker_three_rate"] >= control_worker_rate - 0.05,
    }


def selected_population(original: list[dict], selected_index: int) -> list[dict]:
    order = [selected_index] + [index for index in range(generator.CONTROLLERS) if index != selected_index]
    result = [dict(original[0])]
    for new_index, old_index in enumerate(order):
        parameters = list(original[1 + 2 * old_index]["parameters"])
        for kind, budget in (("one", 1), ("four", 4)):
            result.append(
                {
                    "policy": f"{kind}_{new_index:02d}",
                    "kind": kind,
                    "budget": budget,
                    "parameters": parameters,
                }
            )
    return result


def analyze_discovery() -> dict:
    if DISCOVERY_RESULT.exists() or SELECTED_POPULATION.exists():
        raise SystemExit("refusing to overwrite D110a discovery outputs")
    hashes = {str(path.relative_to(ROOT)): sha256(path) for path in EXPECTED_HASHES}
    hash_integrity = all(sha256(path) == expected for path, expected in EXPECTED_HASHES.items())
    generated = generator.population()
    generator.validate(generated)
    population_exact = POPULATION.read_text() == generator.render(generated)
    rows, _ = read_table(DISCOVERY_ROWS)
    baselines, _ = read_table(DISCOVERY_BASELINES)
    tasks = expected_tasks(DISCOVERY_START, DISCOVERY_MAPS)
    policies = {"zero_control"} | {
        f"{kind}_{index:02d}"
        for kind in ("one", "four")
        for index in range(generator.CONTROLLERS)
    }
    integrity = validate_grid(rows, baselines, tasks, policies)
    control_worker_rate = mean(int(row["own_workers"]) >= 3 for row in baselines)
    metrics = {
        f"one_{index:02d}": policy_metrics(
            rows, baselines, f"one_{index:02d}", DISCOVERY_START
        )
        for index in range(generator.CONTROLLERS)
    }
    gates = {
        policy: discovery_admission(value, control_worker_rate)
        for policy, value in metrics.items()
    }
    mechanics_pass = (
        hash_integrity
        and population_exact
        and integrity["complete"]
        and integrity["zero_exact"]
        and integrity["finite"]
        and integrity["maximum_reward_identity_error"] < 1.0e-4
        and not any(integrity["mechanical_failures"].values())
        and not integrity["counter_violations"]
    )
    admitted = [policy for policy, values in gates.items() if all(values.values())]
    selected = None
    selected_metrics = None
    selected_gates = None
    if mechanics_pass and admitted:
        selected = max(
            admitted,
            key=lambda policy: (
                min(metrics[policy]["fold_mean_margin_delta"].values()),
                metrics[policy]["worst_family"],
                metrics[policy]["mean_margin_delta"],
                metrics[policy]["strict_improvement_rate"],
                -int(policy.split("_")[1]),
            ),
        )
        selected_metrics = metrics[selected]
        selected_gates = gates[selected]
        selected_index = int(selected.split("_")[1])
        SELECTED_POPULATION.write_text(
            generator.render(selected_population(generated, selected_index))
        )
    result = {
        "schema": "troll-farm-d110a-robust-one-use-q6-linear-discovery-v1",
        "inputs": {
            **hashes,
            "discovery_rows": sha256(DISCOVERY_ROWS),
            "discovery_baselines": sha256(DISCOVERY_BASELINES),
            "analyzer": sha256(Path(__file__)),
        },
        "integrity": integrity,
        "mechanics_pass": mechanics_pass,
        "control_worker_three_rate": control_worker_rate,
        "controllers": metrics,
        "admission_gates": gates,
        "admitted": admitted,
        "selected_source_policy": selected,
        "selected_metrics": selected_metrics,
        "selected_gates": selected_gates,
        "selected_population_hash": sha256(SELECTED_POPULATION) if selected else None,
        "decision": "open_repeated_held" if selected else "close_one_use_random_population",
    }
    DISCOVERY_RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def held_value_gates(metrics: dict, control_worker_rate: float) -> dict[str, bool]:
    return {
        "mean_at_least_2": metrics["mean_margin_delta"] >= 2.0,
        "strict_at_least_40pct": metrics["strict_improvement_rate"] >= 0.40,
        "worst_family_at_least_minus3": metrics["worst_family"] >= -3.0,
        "six_positive_families": metrics["positive_families"] >= 6,
        "own_nonnegative_or_opponent_nonpositive": (
            metrics["mean_own_score_delta"] >= 0.0
            or metrics["mean_opponent_score_delta"] <= 0.0
        ),
        "activity_10_to_85pct": 0.10 <= metrics["intervention_rate"] <= 0.85,
        "crop_100pct": metrics["crop_rate"] == 1.0,
        "worker_three_within_5pp": metrics["worker_three_rate"] >= control_worker_rate - 0.05,
    }


def analyze_held() -> dict:
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D110a final output")
    discovery = json.loads(DISCOVERY_RESULT.read_text())
    if discovery["decision"] != "open_repeated_held":
        raise SystemExit("D110a discovery did not authorize held evaluation")
    if sha256(SELECTED_POPULATION) != discovery["selected_population_hash"]:
        raise SystemExit("D110a selected population hash mismatch")
    rows_a, header_a = read_table(HELD_ROWS_A)
    rows_b, header_b = read_table(HELD_ROWS_B)
    baselines_a, baseline_header_a = read_table(HELD_BASELINES_A)
    baselines_b, baseline_header_b = read_table(HELD_BASELINES_B)
    tasks = expected_tasks(HELD_START, HELD_MAPS)
    policies = {"zero_control", "one_00"}
    integrity_a = validate_grid(rows_a, baselines_a, tasks, policies)
    integrity_b = validate_grid(rows_b, baselines_b, tasks, policies)
    repeat_exact = (
        header_a == header_b
        and baseline_header_a == baseline_header_b
        and HELD_ROWS_A.read_bytes() == HELD_ROWS_B.read_bytes()
        and HELD_BASELINES_A.read_bytes() == HELD_BASELINES_B.read_bytes()
    )
    control_worker_rate = mean(int(row["own_workers"]) >= 3 for row in baselines_a)
    metrics = policy_metrics(rows_a, baselines_a, "one_00")
    value_gates = held_value_gates(metrics, control_worker_rate)
    mechanics_pass = all(
        item["complete"]
        and item["zero_exact"]
        and item["finite"]
        and item["maximum_reward_identity_error"] < 1.0e-4
        and not any(item["mechanical_failures"].values())
        and not item["counter_violations"]
        for item in (integrity_a, integrity_b)
    ) and repeat_exact
    full_pass = mechanics_pass and all(value_gates.values())
    result = {
        "schema": "troll-farm-d110a-robust-one-use-q6-linear-population-v1",
        "inputs": {
            "protocol": sha256(PROTOCOL),
            "discovery_result": sha256(DISCOVERY_RESULT),
            "selected_population": sha256(SELECTED_POPULATION),
            "held_rows_a": sha256(HELD_ROWS_A),
            "held_rows_b": sha256(HELD_ROWS_B),
            "held_baselines_a": sha256(HELD_BASELINES_A),
            "held_baselines_b": sha256(HELD_BASELINES_B),
            "analyzer": sha256(Path(__file__)),
        },
        "discovery_selected_source_policy": discovery["selected_source_policy"],
        "discovery_selected_metrics": discovery["selected_metrics"],
        "held": {
            "integrity_a": integrity_a,
            "integrity_b": integrity_b,
            "repeat_exact": repeat_exact,
            "control_worker_three_rate": control_worker_rate,
            "metrics": metrics,
            "value_gates": value_gates,
        },
        "mechanics_pass": mechanics_pass,
        "full_pass": full_pass,
        "decision": (
            "open_deployable_reconstruction_and_confirmation"
            if full_pass
            else "close_one_use_random_population"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("discovery", "held"))
    args = parser.parse_args()
    result = analyze_discovery() if args.phase == "discovery" else analyze_held()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
