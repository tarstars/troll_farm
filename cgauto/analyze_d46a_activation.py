#!/usr/bin/env python3
"""Validate the frozen D46a persistent-chopper activation audit.

The seed bank is quarantined from value analysis.  This analyzer intentionally
uses terminal rows only for mechanical integrity and action-hash activation;
scores and margins are neither summarized nor compared.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d46-persistent-chopper-role-protocol-2026-07-21.md"
AMENDMENT = ANALYSIS / "d46a-seed-quarantine-and-activation-amendment-2026-07-21.md"
CONTROL = ANALYSIS / "d46a-d40-activation-control-9778000-9778031.tsv"
RUN_A = ANALYSIS / "d46a-persistent-chopper-activation-a-9778000-9778031.tsv"
RUN_B = ANALYSIS / "d46a-persistent-chopper-activation-b-9778000-9778031.tsv"
ENV_SOURCE = ROOT / "rust" / "src" / "rl_macro.rs"
PRIOR_SOURCE = ROOT / "rust" / "src" / "d41b_prior_kernel.rs"
RUNNER_SOURCE = ROOT / "rust" / "src" / "bin" / "d46_persistent_chopper.rs"
OUTPUT = ANALYSIS / "d46a-persistent-chopper-activation-result.json"

EXPECTED_PROTOCOL_SHA256 = "eca41e6e85edcea6ee0aa0e7d5bed3bb1cb6ef327ecc471c7b148fc1748a8d53"
EXPECTED_AMENDMENT_SHA256 = "c3834dd7b56194fe57a98e21c354d36ce925857fb9891966ca9fc414e085b139"
EXPECTED_ENV_SOURCE_SHA256 = "6e59965b6d020e9eb51cf41d0a12b72addf0cd776bf7c67a93ef055783788044"
EXPECTED_PRIOR_SOURCE_SHA256 = "632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62"
EXPECTED_RUNNER_SOURCE_SHA256 = "d48e5066cbdcdefd33df1e43034163b37bd2811c70a300588958a9ffcef716f4"

MAP_START = 9_778_000
MAP_STOP = 9_778_032
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


def activation_metrics(
    candidate: list[dict[str, str]],
    control: dict[tuple[int, int, str], dict[str, str]],
) -> dict[str, int | float]:
    eligible = sum(int(row["role_eligible"]) for row in candidate)
    overrides = sum(int(row["role_overrides"]) for row in candidate)
    changed = sum(
        row["action_hash"] != control[task_key(row)]["action_hash"]
        for row in candidate
    )
    return {
        "tasks": len(candidate),
        "role_eligible_decisions": eligible,
        "role_overrides": overrides,
        "changed_action_hash_tasks": changed,
        "changed_action_hash_rate": changed / len(candidate),
    }


def activation_gates(
    metrics: dict[str, int | float],
    *,
    repeat_byte_identical: bool,
    integrity_failures: int,
) -> dict[str, bool]:
    changed_rate = float(metrics["changed_action_hash_rate"])
    return {
        "complete_exact_deterministic_repeat": repeat_byte_identical
        and int(metrics["tasks"]) == TASKS,
        "zero_integrity_failures": integrity_failures == 0,
        "at_least_512_role_eligible_decisions": int(
            metrics["role_eligible_decisions"]
        )
        >= 512,
        "at_least_256_role_overrides": int(metrics["role_overrides"]) >= 256,
        "changed_action_hash_tasks_between_20_and_90_percent": (
            0.20 <= changed_rate <= 0.90
        ),
    }


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
        raise RuntimeError(f"D46a {policy} schema or size mismatch")
    keys = [task_key(row) for row in rows]
    if len(set(keys)) != len(keys) or set(keys) != expected_tasks():
        raise RuntimeError(f"D46a {policy} task grid mismatch")
    if any(row["policy"] != policy for row in rows):
        raise RuntimeError(f"D46a {policy} policy label mismatch")
    return {task_key(row): row for row in rows}


def row_integrity_failures(row: dict[str, str], *, candidate: bool) -> int:
    failures = (
        int(row["invalid_direct_commands"])
        + int(row["provenance_failures"])
        + int(row["deposit_prediction_failures"])
        + int(int(row["own_workers"]) > 3)
        + int(float(row["reward_identity_error"]) > 1.0e-4)
        + int(sum(int(row[name]) for name in ACTION_PLANES) != int(row["selected_decisions"]))
    )
    eligible = int(row["role_eligible"])
    overrides = int(row["role_overrides"])
    role_failures = int(row["role_integrity_failures"])
    if candidate:
        failures += role_failures + int(overrides > eligible)
    else:
        failures += eligible + overrides + role_failures
    return failures


def main() -> None:
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (AMENDMENT, EXPECTED_AMENDMENT_SHA256),
        (ENV_SOURCE, EXPECTED_ENV_SOURCE_SHA256),
        (PRIOR_SOURCE, EXPECTED_PRIOR_SOURCE_SHA256),
        (RUNNER_SOURCE, EXPECTED_RUNNER_SOURCE_SHA256),
    ):
        if not path.exists() or sha256(path) != expected:
            raise SystemExit(f"D46a prerequisite missing or changed: {path}")
    if not CONTROL.exists() or not RUN_A.exists() or not RUN_B.exists():
        raise SystemExit("missing D46a control or repeat matrix")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D46a result")

    control_rows, control_fields = read_table(CONTROL)
    rows_a, fields_a = read_table(RUN_A)
    rows_b, fields_b = read_table(RUN_B)
    if control_fields != fields_a or fields_a != fields_b:
        raise RuntimeError("D46a matrix schema mismatch")
    control = validate_grid(control_rows, control_fields, "d40")
    validate_grid(rows_a, fields_a, "persistent_chopper")
    validate_grid(rows_b, fields_b, "persistent_chopper")

    repeat_byte_identical = RUN_A.read_bytes() == RUN_B.read_bytes()
    integrity_failures = sum(
        row_integrity_failures(row, candidate=False) for row in control_rows
    ) + sum(row_integrity_failures(row, candidate=True) for row in rows_a)
    metrics = activation_metrics(rows_a, control)
    gates = activation_gates(
        metrics,
        repeat_byte_identical=repeat_byte_identical,
        integrity_failures=integrity_failures,
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "amendment": str(AMENDMENT),
        "amendment_sha256": sha256(AMENDMENT),
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
            "outcome_fields_ignored": True,
        },
        "activation": metrics,
        "gates": gates,
        "pass": all(gates.values()),
        "scope": (
            "quarantined activation/integrity audit only; scores and margins ignored; "
            "no policy selection or platform action"
        ),
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
