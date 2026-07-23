#!/usr/bin/env python3
"""Validate the frozen D45a complete-policy rate-search surface preflight."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d45a-complete-policy-rate-search-surface-protocol-2026-07-21.md"
PARAMETERS = ANALYSIS / "d45a-rate-search-surface-parameters.tsv"
RUN_A = ANALYSIS / "d45a-rate-search-surface-a-9670000-9670003.tsv"
RUN_B = ANALYSIS / "d45a-rate-search-surface-b-9670000-9670003.tsv"
D40_REFERENCE = ANALYSIS / "d40-macro-work-conserving-preflight-a-9670000-9670015.tsv"
D40_RESULT = ANALYSIS / "d40-work-conserving-preflight-2026-07-21.json"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d45_rate_surface.rs"
GENERATOR_SOURCE = ROOT / "cgauto" / "make_d45a_rate_surface.py"
OUTPUT = ANALYSIS / "d45a-complete-policy-rate-search-surface-result.json"

EXPECTED_PROTOCOL_SHA256 = "185d99a54b9d9283c43301f7ca104b3367d80addcf8ea2671b07c3a7fc8660ab"
EXPECTED_PARAMETERS_SHA256 = "be42c39ba3cb16ba9c9538b84611272172efc6f8e737947506e65b7ccf93409e"
EXPECTED_D40_REFERENCE_SHA256 = "653dee375b1922bd43b74e6e9aa1b27503d8017350f3b8dcf3baed197827b8a5"
EXPECTED_D40_RESULT_SHA256 = "dab4bb75f7ad2af8a8e4d69828dd6b80954d897c7e03cfd089ef8a2edc012c65"
EXPECTED_ENV_SOURCE_SHA256 = "6e59965b6d020e9eb51cf41d0a12b72addf0cd776bf7c67a93ef055783788044"
EXPECTED_PRIOR_SOURCE_SHA256 = "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
EXPECTED_RUNNER_SOURCE_SHA256 = "d8686e96926deeb205df8f40014ce54ced81a126ca18fcc040a4c1c3097ff5de"
EXPECTED_GENERATOR_SOURCE_SHA256 = "4527dd1cb8895d661f82c140823badf9646c7cc3a7b8fae962347897e1d5384b"
MAP_START = 9_670_000
MAP_STOP = 9_670_004
GENOMES = 17
TASKS = 64

PAIRS = (
    "bank",
    "fell",
    "harvest",
    "renew",
    "mine",
    "opponent_owner",
    "turn_renew",
    "workers_fell",
)


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = list(reader.fieldnames or ())
    return rows, fields


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), row["opponent"]


def summarize(rows: list[dict[str, str]], zero: dict[tuple[int, int, str], dict[str, str]]) -> dict:
    margins = np.asarray([int(row["margin"]) for row in rows], dtype=np.float64)
    action_changes = sum(
        row["action_hash"] != zero[task_key(row)]["action_hash"] for row in rows
    )
    return {
        "tasks": len(rows),
        "mean_margin": float(margins.mean()),
        "mean_own_score": float(np.mean([int(row["own_score"]) for row in rows])),
        "mean_opponent_score": float(
            np.mean([int(row["opponent_score"]) for row in rows])
        ),
        "worker_two_rate": float(np.mean([int(row["own_workers"]) >= 2 for row in rows])),
        "worker_three_rate": float(
            np.mean([int(row["own_workers"]) >= 3 for row in rows])
        ),
        "crop_rate": float(
            np.mean([int(row["own_created_crops"]) > 0 for row in rows])
        ),
        "changed_action_hash_tasks": int(action_changes),
        "changed_action_hash_rate": action_changes / len(rows),
    }


def gate_metrics(summaries: dict[str, dict]) -> dict:
    zero_mean = summaries["zero"]["mean_margin"]
    perturbations = {name: row for name, row in summaries.items() if name != "zero"}
    means = [row["mean_margin"] for row in perturbations.values()]
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
    pair_differences = {
        name: abs(
            summaries[f"{name}_plus"]["mean_margin"]
            - summaries[f"{name}_minus"]["mean_margin"]
        )
        for name in PAIRS
    }
    return {
        "zero_mean_margin": zero_mean,
        "perturbation_mean_minimum": min(means),
        "perturbation_mean_maximum": max(means),
        "perturbation_mean_range": max(means) - min(means),
        "perturbations_above_zero": sum(value > zero_mean for value in means),
        "perturbations_below_zero": sum(value < zero_mean for value in means),
        "active_perturbations": active,
        "safe_perturbations": safe,
        "pair_mean_margin_differences": pair_differences,
        "directional_pairs_at_least_2": sum(
            value >= 2 for value in pair_differences.values()
        ),
    }


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (PARAMETERS, EXPECTED_PARAMETERS_SHA256),
        (D40_REFERENCE, EXPECTED_D40_REFERENCE_SHA256),
        (D40_RESULT, EXPECTED_D40_RESULT_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
        (GENERATOR_SOURCE, EXPECTED_GENERATOR_SOURCE_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D45a prerequisite missing or changed: {path}")
    if not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D45a repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D45a result")

    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    if RUN_A.read_bytes() != RUN_B.read_bytes():
        raise RuntimeError("D45a repeat matrices are not byte-identical")
    if fields_a != fields_b or len(rows_a) != GENOMES * TASKS:
        raise RuntimeError("D45a matrix schema or size mismatch")
    labels = sorted(set(row["genome"] for row in rows_a))
    if len(labels) != GENOMES or "zero" not in labels:
        raise RuntimeError("D45a genome coverage mismatch")
    expected_tasks = {
        (seed, seat, opponent)
        for seed in range(MAP_START, MAP_STOP)
        for seat in range(2)
        for opponent in sorted(set(row["opponent"] for row in rows_a))
    }
    if len(expected_tasks) != TASKS:
        raise RuntimeError("D45a opponent coverage mismatch")
    by_genome = {
        label: sorted(
            [row for row in rows_a if row["genome"] == label], key=task_key
        )
        for label in labels
    }
    if any({task_key(row) for row in rows} != expected_tasks for rows in by_genome.values()):
        raise RuntimeError("D45a incomplete genome grid")

    integrity_failures = sum(
        int(row["invalid_direct_commands"])
        + int(row["provenance_failures"])
        + int(row["deposit_prediction_failures"])
        + int(int(row["own_workers"]) > 3)
        for row in rows_a
    )
    if integrity_failures:
        raise RuntimeError(f"D45a integrity failures: {integrity_failures}")

    reference, reference_fields = read_table(D40_REFERENCE)
    reference = sorted(
        [row for row in reference if MAP_START <= int(row["map_seed"]) < MAP_STOP],
        key=task_key,
    )
    if len(reference) != TASKS:
        raise RuntimeError("D45a D40 prefix size mismatch")
    common = [name for name in reference_fields if name != "policy"]
    if [name for name in fields_a if name != "genome"] != common:
        raise RuntimeError("D45a/D40 comparable schema mismatch")
    parity_failures = []
    for expected, actual in zip(reference, by_genome["zero"]):
        for name in common:
            if expected[name] != actual[name]:
                parity_failures.append((task_key(actual), name, expected[name], actual[name]))
    if parity_failures:
        raise RuntimeError(f"D45a zero/D40 parity failure: {parity_failures[:3]}")

    zero = {task_key(row): row for row in by_genome["zero"]}
    summaries = {label: summarize(rows, zero) for label, rows in by_genome.items()}
    metrics = gate_metrics(summaries)
    gates = {
        "complete_byte_identical_17x64_repeats": True,
        "zero_exact_d40_prefix_parity": True,
        "zero_integrity_failures": integrity_failures == 0,
        "at_least_12_active_perturbations": len(metrics["active_perturbations"]) >= 12,
        "mean_margin_range_at_least_15": metrics["perturbation_mean_range"] >= 15,
        "means_both_above_and_below_zero": metrics["perturbations_above_zero"] >= 1
        and metrics["perturbations_below_zero"] >= 1,
        "at_least_8_safe_perturbations": len(metrics["safe_perturbations"]) >= 8,
        "at_least_4_directional_pairs": metrics["directional_pairs_at_least_2"] >= 4,
    }
    gates = {name: bool(value) for name, value in gates.items()}
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "parameters": str(PARAMETERS),
            "parameters_sha256": sha256(PARAMETERS),
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
            "genomes": GENOMES,
            "tasks_per_genome": TASKS,
            "rows": len(rows_a),
            "repeat_byte_identical": True,
            "zero_parity_failures": len(parity_failures),
            "integrity_failures": integrity_failures,
        },
        "summaries": summaries,
        "surface": metrics,
        "gates": gates,
        "pass": all(gates.values()),
        "scope": "consumed-map search-surface preflight only; no parameter selection or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
