#!/usr/bin/env python3
"""Validate the frozen D48a complete-policy economic-bonus surface."""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d48a-economic-bonus-surface-protocol-2026-07-21.md"
POLICIES = ANALYSIS / "d48a-economic-bonus-surface-policies.tsv"
RUN_A = ANALYSIS / "d48a-economic-bonus-surface-a-9670000-9670003.tsv"
RUN_B = ANALYSIS / "d48a-economic-bonus-surface-b-9670000-9670003.tsv"
D40_REFERENCE = ANALYSIS / "d40-macro-work-conserving-preflight-a-9670000-9670015.tsv"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d48_bonus_surface.rs"
GENERATOR_SOURCE = ROOT / "cgauto" / "make_d48a_bonus_surface.py"
OUTPUT = ANALYSIS / "d48a-economic-bonus-surface-result.json"

EXPECTED_PROTOCOL_SHA256 = "4f3691dbc83cd9c0791719791de6518bb884034fabc59bc67fe151ff0a57580e"
EXPECTED_POLICIES_SHA256 = "8d6f1aaff77a3a4fb2c7bd5d71307a19895b05f2fab1d0166241200d2e8fe2d6"
EXPECTED_D40_REFERENCE_SHA256 = "653dee375b1922bd43b74e6e9aa1b27503d8017350f3b8dcf3baed197827b8a5"
EXPECTED_ENV_SOURCE_SHA256 = "6e59965b6d020e9eb51cf41d0a12b72addf0cd776bf7c67a93ef055783788044"
EXPECTED_PRIOR_SOURCE_SHA256 = "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
EXPECTED_RUNNER_SOURCE_SHA256 = "776fb39aaf7b57f1b1a826af7dd19235464007383e2f99716b6f26055d6c4343"
EXPECTED_GENERATOR_SOURCE_SHA256 = "bdd9faefac5572f9719020666d4d339a4a8c68410167d3a748a557576833e17a"

MAP_START = 9_670_000
MAP_STOP = 9_670_004
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
LABELS = (
    "anchor",
    "provenance_zero",
    "provenance_double",
    "renew_zero",
    "renew_double",
    "bank_zero",
    "bank_double",
)
COORDINATES = ("provenance", "renew", "bank")
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


def summarize(
    rows: list[dict[str, str]], anchor: dict[tuple[int, int, str], dict[str, str]]
) -> dict:
    margins = [int(row["margin"]) for row in rows]
    changes = sum(
        row["action_hash"] != anchor[task_key(row)]["action_hash"] for row in rows
    )
    return {
        "tasks": len(rows),
        "mean_margin": float(statistics.mean(margins)),
        "mean_own_score": float(
            statistics.mean(int(row["own_score"]) for row in rows)
        ),
        "mean_opponent_score": float(
            statistics.mean(int(row["opponent_score"]) for row in rows)
        ),
        "changed_action_hash_tasks": changes,
        "changed_action_hash_rate": changes / len(rows),
        "worker_two_rate": statistics.mean(
            int(row["own_workers"]) >= 2 for row in rows
        ),
        "worker_three_rate": statistics.mean(
            int(row["own_workers"]) >= 3 for row in rows
        ),
        "crop_rate": statistics.mean(
            int(row["own_created_crops"]) > 0 for row in rows
        ),
    }


def surface_metrics(summaries: dict[str, dict]) -> dict:
    anchor_mean = summaries["anchor"]["mean_margin"]
    perturbations = {name: summaries[name] for name in LABELS if name != "anchor"}
    active = [
        name
        for name, row in perturbations.items()
        if 0.05 <= row["changed_action_hash_rate"] <= 0.95
    ]
    safe = [
        name
        for name, row in perturbations.items()
        if row["worker_two_rate"] >= 0.90
        and row["worker_three_rate"] >= 0.50
        and row["crop_rate"] >= 0.60
    ]
    coordinate_activation = {
        coordinate: any(
            f"{coordinate}_{suffix}" in active for suffix in ("zero", "double")
        )
        for coordinate in COORDINATES
    }
    pair_differences = {
        coordinate: abs(
            summaries[f"{coordinate}_zero"]["mean_margin"]
            - summaries[f"{coordinate}_double"]["mean_margin"]
        )
        for coordinate in COORDINATES
    }
    means = [row["mean_margin"] for row in perturbations.values()]
    return {
        "anchor_mean_margin": anchor_mean,
        "perturbation_mean_minimum": min(means),
        "perturbation_mean_maximum": max(means),
        "perturbation_mean_range": max(means) - min(means),
        "perturbations_above_anchor": sum(value > anchor_mean for value in means),
        "perturbations_below_anchor": sum(value < anchor_mean for value in means),
        "active_perturbations": active,
        "safe_perturbations": safe,
        "coordinate_activation": coordinate_activation,
        "pair_mean_margin_differences": pair_differences,
        "directional_pairs_at_least_2": sum(
            value >= 2 for value in pair_differences.values()
        ),
    }


def expected_tasks() -> set[tuple[int, int, str]]:
    return {
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in OPPONENTS
    }


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (POLICIES, EXPECTED_POLICIES_SHA256),
        (D40_REFERENCE, EXPECTED_D40_REFERENCE_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
        (GENERATOR_SOURCE, EXPECTED_GENERATOR_SOURCE_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D48a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D48a repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D48a result")

    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    if RUN_A.read_bytes() != RUN_B.read_bytes():
        raise RuntimeError("D48a repeat matrices are not byte-identical")
    if fields_a != fields_b or len(rows_a) != len(LABELS) * TASKS:
        raise RuntimeError("D48a matrix schema or size mismatch")
    if set(row["policy"] for row in rows_a) != set(LABELS):
        raise RuntimeError("D48a policy coverage mismatch")
    by_policy = {
        label: sorted(
            [row for row in rows_a if row["policy"] == label], key=task_key
        )
        for label in LABELS
    }
    tasks = expected_tasks()
    if any({task_key(row) for row in rows} != tasks for rows in by_policy.values()):
        raise RuntimeError("D48a incomplete policy grid")

    integrity_failures = 0
    for row in rows_a:
        integrity_failures += (
            int(row["invalid_direct_commands"])
            + int(row["provenance_failures"])
            + int(row["deposit_prediction_failures"])
            + int(int(row["own_workers"]) > 3)
            + int(float(row["reward_identity_error"]) > 1.0e-4)
            + int(
                sum(int(row[name]) for name in ACTION_PLANES)
                != int(row["selected_decisions"])
            )
            + int(
                not all(
                    math.isfinite(float(row[name]))
                    for name in ("own_return", "opponent_return", "margin_return")
                )
            )
        )
    if integrity_failures:
        raise RuntimeError(f"D48a integrity failures: {integrity_failures}")

    reference, reference_fields = read_table(D40_REFERENCE)
    reference = sorted(
        [row for row in reference if MAP_START <= int(row["map_seed"]) < MAP_STOP],
        key=task_key,
    )
    if len(reference) != TASKS:
        raise RuntimeError("D48a D40 prefix size mismatch")
    comparable = [name for name in reference_fields if name != "policy"]
    if [
        name for name in fields_a if name not in ("policy", "reward_identity_error")
    ] != comparable:
        raise RuntimeError("D48a/D40 comparable schema mismatch")
    parity_failures = []
    for expected, actual in zip(reference, by_policy["anchor"]):
        for name in comparable:
            if expected[name] != actual[name]:
                parity_failures.append(
                    (task_key(actual), name, expected[name], actual[name])
                )
    if parity_failures:
        raise RuntimeError(f"D48a anchor/D40 parity failure: {parity_failures[:3]}")

    anchor = {task_key(row): row for row in by_policy["anchor"]}
    summaries = {
        label: summarize(rows, anchor) for label, rows in by_policy.items()
    }
    metrics = surface_metrics(summaries)
    gates = {
        "complete_byte_identical_7x64_repeats": True,
        "anchor_exact_d40_prefix_parity": True,
        "zero_integrity_failures": integrity_failures == 0,
        "each_coordinate_has_active_direction": all(
            metrics["coordinate_activation"].values()
        ),
        "at_least_4_active_perturbations": len(metrics["active_perturbations"])
        >= 4,
        "mean_margin_range_at_least_15": metrics["perturbation_mean_range"] >= 15,
        "means_both_above_and_below_anchor": metrics["perturbations_above_anchor"]
        >= 1
        and metrics["perturbations_below_anchor"] >= 1,
        "at_least_4_safe_perturbations": len(metrics["safe_perturbations"]) >= 4,
        "at_least_2_directional_pairs": metrics["directional_pairs_at_least_2"]
        >= 2,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "policies": str(POLICIES),
            "policies_sha256": sha256(POLICIES),
            "run_a": str(RUN_A),
            "run_a_sha256": sha256(RUN_A),
            "run_b": str(RUN_B),
            "run_b_sha256": sha256(RUN_B),
            "d40_reference": str(D40_REFERENCE),
            "d40_reference_sha256": sha256(D40_REFERENCE),
            "runner_source_sha256": sha256(RUNNER_SOURCE),
            "generator_source_sha256": sha256(GENERATOR_SOURCE),
        },
        "audit": {
            "policies": len(LABELS),
            "tasks_per_policy": TASKS,
            "rows": len(rows_a),
            "repeat_byte_identical": True,
            "anchor_parity_failures": len(parity_failures),
            "integrity_failures": integrity_failures,
        },
        "summaries": summaries,
        "surface": metrics,
        "gates": gates,
        "pass": all(gates.values()),
        "scope": "consumed-map formula-surface preflight only; no arm selection or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
