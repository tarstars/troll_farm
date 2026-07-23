#!/usr/bin/env python3
"""Validate the frozen D47 persistent-producer development conjunction."""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d47-persistent-producer-role-protocol-2026-07-21.md"
ACTIVATION = ANALYSIS / "d47a-persistent-producer-activation-result.json"
CONTROL = ANALYSIS / "d47b-d40-development-control-9783000-9783031.tsv"
RUN_A = ANALYSIS / "d47b-persistent-producer-development-a-9783000-9783031.tsv"
RUN_B = ANALYSIS / "d47b-persistent-producer-development-b-9783000-9783031.tsv"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d47_persistent_producer.rs"
OUTPUT = ANALYSIS / "d47b-persistent-producer-development-result.json"

EXPECTED_PROTOCOL_SHA256 = "d26bcdcaada549fd904090611f1ee358f1ce4934ca8e3c5932c6c6db4e1af3b2"
EXPECTED_ACTIVATION_SHA256 = "59e9f49b58d80b4592d84d113b4a5eb25f536a91a195cbcb6e36a772c60383b5"
EXPECTED_ENV_SOURCE_SHA256 = "6e59965b6d020e9eb51cf41d0a12b72addf0cd776bf7c67a93ef055783788044"
EXPECTED_PRIOR_SOURCE_SHA256 = "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
EXPECTED_RUNNER_SOURCE_SHA256 = "aea0248247d8ebffd38a4d1d168f66b1c6455db63224f0f8d1157d73528deed9"

MAP_START = 9_783_000
MAP_STOP = 9_783_032
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
TASKS = (MAP_STOP - MAP_START) * 2 * len(OPPONENTS)
ACTION_PLANES = (
    "train_none",
    "train_producer",
    "train_chopper",
    "idle",
    "bank",
    "fell_bank",
    "harvest_bank",
    "renew",
    "mine_bank",
)


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = list(reader.fieldnames or ())
    return rows, fields


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def mean(values: list[float] | list[int]) -> float:
    return float(statistics.mean(values))


def trimmed_mean(values: list[int], fraction: float = 0.05) -> float:
    ordered = sorted(values)
    trim = math.floor(len(ordered) * fraction)
    retained = ordered[trim : len(ordered) - trim] if trim else ordered
    return mean(retained)


def normal_lower_bound(values: list[float], z: float = 1.96) -> float:
    center = mean(values)
    if len(values) < 2:
        return center
    return center - z * statistics.stdev(values) / math.sqrt(len(values))


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def validate_grid(
    rows: list[dict[str, str]], fields: list[str], policy: str
) -> dict[tuple[int, int, str], dict[str, str]]:
    if not fields or len(rows) != TASKS:
        raise RuntimeError(f"D47b {policy} schema or size mismatch")
    keys = [task_key(row) for row in rows]
    if len(set(keys)) != len(keys) or set(keys) != expected_tasks():
        raise RuntimeError(f"D47b {policy} task grid mismatch")
    if any(row["policy"] != policy for row in rows):
        raise RuntimeError(f"D47b {policy} policy label mismatch")
    return {task_key(row): row for row in rows}


def row_integrity_failures(row: dict[str, str], *, candidate: bool) -> int:
    failures = (
        int(row["invalid_direct_commands"])
        + int(row["provenance_failures"])
        + int(row["deposit_prediction_failures"])
        + int(int(row["own_workers"]) > 3)
        + int(float(row["reward_identity_error"]) > 1.0e-4)
        + int(
            sum(int(row[name]) for name in ACTION_PLANES)
            != int(row["selected_decisions"])
        )
    )
    eligible = int(row["role_eligible"])
    overrides = int(row["role_overrides"])
    role_failures = int(row["role_integrity_failures"])
    if candidate:
        failures += role_failures + int(overrides > eligible)
    else:
        failures += eligible + overrides + role_failures
    return failures


def development_metrics(
    candidate: list[dict[str, str]],
    control: dict[tuple[int, int, str], dict[str, str]],
) -> dict:
    margin_deltas: list[int] = []
    own_deltas: list[int] = []
    opponent_deltas: list[int] = []
    seed_deltas: dict[int, list[int]] = defaultdict(list)
    family_deltas: dict[str, list[int]] = defaultdict(list)
    changed = 0
    for row in candidate:
        baseline = control[task_key(row)]
        margin_delta = int(row["margin"]) - int(baseline["margin"])
        margin_deltas.append(margin_delta)
        own_deltas.append(int(row["own_score"]) - int(baseline["own_score"]))
        opponent_deltas.append(
            int(row["opponent_score"]) - int(baseline["opponent_score"])
        )
        seed_deltas[int(row["map_seed"])].append(margin_delta)
        family_deltas[row["opponent"]].append(margin_delta)
        changed += row["action_hash"] != baseline["action_hash"]
    seed_means = [mean(seed_deltas[seed]) for seed in sorted(seed_deltas)]
    family_means = {
        opponent: mean(family_deltas[opponent]) for opponent in OPPONENTS
    }
    candidate_margins = [int(row["margin"]) for row in candidate]
    control_margins = [int(row["margin"]) for row in control.values()]
    return {
        "tasks": len(candidate),
        "role_eligible_decisions": sum(
            int(row["role_eligible"]) for row in candidate
        ),
        "role_overrides": sum(int(row["role_overrides"]) for row in candidate),
        "changed_action_hash_tasks": changed,
        "changed_action_hash_rate": changed / len(candidate),
        "paired_mean_margin_delta": mean(margin_deltas),
        "paired_trimmed_5pct_margin_delta": trimmed_mean(margin_deltas),
        "map_seed_mean_margin_deltas": seed_means,
        "map_seed_normal_95pct_lower_bound": normal_lower_bound(seed_means),
        "paired_mean_own_score_delta": mean(own_deltas),
        "paired_mean_opponent_score_delta": mean(opponent_deltas),
        "opponent_family_mean_margin_deltas": family_means,
        "positive_opponent_families": sum(value > 0 for value in family_means.values()),
        "worst_opponent_family_mean_margin_delta": min(family_means.values()),
        "worker_two_rate": mean([int(row["own_workers"]) >= 2 for row in candidate]),
        "worker_three_rate": mean([int(row["own_workers"]) >= 3 for row in candidate]),
        "crop_rate": mean([int(row["own_created_crops"]) > 0 for row in candidate]),
        "candidate_catastrophes": sum(value <= -100 for value in candidate_margins),
        "control_catastrophes": sum(value <= -100 for value in control_margins),
        "candidate_negative_margin_mass": sum(
            max(-value, 0) for value in candidate_margins
        ),
        "control_negative_margin_mass": sum(max(-value, 0) for value in control_margins),
    }


def development_gates(
    metrics: dict, *, repeat_byte_identical: bool, integrity_failures: int
) -> dict[str, bool]:
    return {
        "complete_exact_deterministic_repeat": repeat_byte_identical
        and metrics["tasks"] == TASKS,
        "zero_integrity_failures": integrity_failures == 0,
        "changed_action_hash_tasks_between_20_and_90_percent": (
            0.20 <= metrics["changed_action_hash_rate"] <= 0.90
        ),
        "at_least_1024_role_eligible_decisions": metrics["role_eligible_decisions"]
        >= 1_024,
        "at_least_512_role_overrides": metrics["role_overrides"] >= 512,
        "paired_mean_margin_gain_at_least_8": metrics["paired_mean_margin_delta"] >= 8,
        "trimmed_mean_margin_gain_at_least_5": metrics[
            "paired_trimmed_5pct_margin_delta"
        ]
        >= 5,
        "map_seed_normal_lower_bound_above_3": metrics[
            "map_seed_normal_95pct_lower_bound"
        ]
        > 3,
        "mean_own_score_delta_at_least_3": metrics["paired_mean_own_score_delta"] >= 3,
        "mean_opponent_score_delta_at_most_0": metrics[
            "paired_mean_opponent_score_delta"
        ]
        <= 0,
        "at_least_6_positive_opponent_families": metrics[
            "positive_opponent_families"
        ]
        >= 6,
        "worst_opponent_family_at_least_minus_8": metrics[
            "worst_opponent_family_mean_margin_delta"
        ]
        >= -8,
        "worker_two_rate_at_least_95pct": metrics["worker_two_rate"] >= 0.95,
        "worker_three_rate_at_least_88pct": metrics["worker_three_rate"] >= 0.88,
        "crop_rate_at_least_97pct": metrics["crop_rate"] >= 0.97,
        "catastrophes_not_increased": metrics["candidate_catastrophes"]
        <= metrics["control_catastrophes"],
        "negative_margin_mass_not_increased": metrics[
            "candidate_negative_margin_mass"
        ]
        <= metrics["control_negative_margin_mass"],
    }


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (ACTIVATION, EXPECTED_ACTIVATION_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D47b prerequisite missing or changed: {path}")
    activation = json.loads(ACTIVATION.read_text())
    if not activation.get("pass") or not activation.get("audit", {}).get(
        "outcome_fields_ignored"
    ):
        raise SystemExit("D47a did not authorize development")
    if not CONTROL.exists() or not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D47b control or repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D47b result")

    control_rows, control_fields = read_table(CONTROL)
    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    if control_fields != fields_a or fields_a != fields_b:
        raise RuntimeError("D47b matrix schema mismatch")
    control = validate_grid(control_rows, control_fields, "d40")
    validate_grid(rows_a, fields_a, "persistent_producer")
    validate_grid(rows_b, fields_b, "persistent_producer")

    repeat_byte_identical = RUN_A.read_bytes() == RUN_B.read_bytes()
    integrity_failures = sum(
        row_integrity_failures(row, candidate=False) for row in control_rows
    ) + sum(row_integrity_failures(row, candidate=True) for row in rows_a)
    metrics = development_metrics(rows_a, control)
    gates = development_gates(
        metrics,
        repeat_byte_identical=repeat_byte_identical,
        integrity_failures=integrity_failures,
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "activation_result_sha256": sha256(ACTIVATION),
        "inputs": {
            "control": str(CONTROL),
            "control_sha256": sha256(CONTROL),
            "run_a": str(RUN_A),
            "run_a_sha256": sha256(RUN_A),
            "run_b": str(RUN_B),
            "run_b_sha256": sha256(RUN_B),
            "environment_source_sha256": sha256(ENV_SOURCE),
            "prior_source_sha256": sha256(PRIOR_SOURCE),
            "runner_source_sha256": sha256(RUNNER_SOURCE),
        },
        "audit": {
            "tasks_per_arm": TASKS,
            "repeat_byte_identical": repeat_byte_identical,
            "integrity_failures": integrity_failures,
            "trim_fraction_each_tail": 0.05,
            "normal_lower_bound_z": 1.96,
            "normal_lower_bound_unit": "32 map-seed means",
        },
        "development": metrics,
        "gates": gates,
        "failed_gates": [name for name, passed in gates.items() if not passed],
        "pass": all(gates.values()),
        "scope": "fresh D47 complete-policy development; confirmation and platform remain gated",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
