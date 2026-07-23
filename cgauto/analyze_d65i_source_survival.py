#!/usr/bin/env python3
"""Analyze the repeated D65i planted-source lifecycle trace."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
ANALYSIS = REPO / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d65i-source-survival-audit-protocol-2026-07-21.md"
RUNNER = REPO / "rust/src/bin/d65_source_survival_audit.rs"
D65_MATRIX = ANALYSIS / "d65a-consumed-recovery-final-9830002-9830014.tsv"
SEEDS = (9_830_002, 9_830_014)
FRUITS = ("plum", "lemon", "apple", "banana")
MISSING_SPECIES = {9_830_002: "lemon", 9_830_014: "plum"}
TERMINAL_PARITY_FIELDS = (
    "own_workers",
    "own_score",
    "opponent_score",
    "margin",
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
    "action_hash",
    "state_hash",
)


def vector(value: str) -> list[int]:
    result = [int(item) for item in value.split(",")]
    if len(result) not in (4, 6):
        raise ValueError(f"unexpected D65i vector {value!r}")
    return result


def parse_source_states(value: str) -> dict[tuple[str, int, int], dict[str, int | str | bool]]:
    result: dict[tuple[str, int, int], dict[str, int | str | bool]] = {}
    if not value:
        return result
    for encoded in value.split(";"):
        head, present, actual, owner, size, health, fruits, cooldown = encoded.split(":")
        expected, cell = head.split("@")
        x, y = (int(item) for item in cell.split(","))
        result[(expected, x, y)] = {
            "present": bool(int(present)),
            "actual": actual,
            "owner": owner,
            "size": int(size),
            "health": int(health),
            "fruits": int(fruits),
            "cooldown": int(cooldown),
        }
    return result


def expected_source(state: dict[str, int | str | bool], expected: str) -> bool:
    return bool(state["present"]) and state["actual"] == expected and state["owner"] == "own"


def task_key(row: dict[str, str]) -> tuple[int, int, str]:
    return int(row["map_seed"]), int(row["seat"]), "resident"


def d65_repairs() -> dict[tuple[int, int, str], dict[str, str]]:
    with D65_MATRIX.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {
        task_key(row): row
        for row in rows
        if row["policy"] == "seed_source_repair"
    }


def lifecycle(
    rows: list[dict[str, str]], root: tuple[str, int, int], train_turn: int | None
) -> dict:
    expected, x, y = root
    kind = FRUITS.index(expected)
    observations = []
    for row in rows:
        state = parse_source_states(row["sources_after"]).get(root)
        if state is not None:
            observations.append((row, state))
    own_observations = [
        (row, state)
        for row, state in observations
        if expected_source(state, expected)
    ]
    first_present_turn = (
        min(int(row["turn_after"]) for row, _ in own_observations)
        if own_observations
        else None
    )
    ripe = [(row, state) for row, state in own_observations if int(state["fruits"]) > 0]
    first_ripe_turn = min((int(row["turn_after"]) for row, _ in ripe), default=None)
    max_fruits = max((int(state["fruits"]) for _, state in own_observations), default=0)
    first_loss_turn = None
    previously_present = False
    for row, state in observations:
        present = expected_source(state, expected)
        if previously_present and not present:
            first_loss_turn = int(row["turn_after"])
            break
        previously_present = present

    events = []
    previous_invalidated = 0
    for row in rows:
        before = parse_source_states(row["sources_before"]).get(root)
        invalidated = int(row["invalidated_jobs"])
        invalidated_delta = invalidated - previous_invalidated
        previous_invalidated = invalidated
        if (
            row["job_target"] == f"{x},{y}"
            and before is not None
            and expected_source(before, expected)
        ):
            bank_before = vector(row["bank_before"])[kind]
            bank_after = vector(row["bank_after"])[kind]
            after = parse_source_states(row["sources_after"]).get(root)
            events.append(
                {
                    "turn_before": int(row["turn_before"]),
                    "turn_after": int(row["turn_after"]),
                    "job_kind": row["job_kind"],
                    "job_fruit": row["job_fruit"],
                    "bank_delta": bank_after - bank_before,
                    "invalidated_delta": invalidated_delta,
                    "root_lost": after is None or not expected_source(after, expected),
                    "own_species_count_delta": (
                        vector(row["own_plants_after"])[kind]
                        - vector(row["own_plants_before"])[kind]
                    ),
                }
            )
    deposited = sum(max(0, event["bank_delta"]) for event in events)
    deposited_before_train = sum(
        max(0, event["bank_delta"])
        for event in events
        if train_turn is None or event["turn_after"] <= train_turn
    )
    terminal_workers = int(rows[-1]["own_workers"])
    if terminal_workers >= 2 and deposited_before_train > 0:
        classification = "capitalized"
    elif first_ripe_turn is None:
        classification = "destroyed_before_ripe"
    elif not events:
        classification = "ripe_but_unselected"
    elif any(
        event["invalidated_delta"] > 0 and event["bank_delta"] <= 0 for event in events
    ):
        classification = "selected_then_invalidated_or_contested"
    elif any(
        event["job_kind"] == "renew"
        and event["bank_delta"] <= 0
        and event["own_species_count_delta"] > 0
        for event in events
    ):
        classification = "reinvested"
    elif deposited > 0:
        classification = "deposited_but_incomplete"
    else:
        classification = "other"
    return {
        "expected_species": expected,
        "cell": [x, y],
        "first_present_turn": first_present_turn,
        "first_ripe_turn": first_ripe_turn,
        "max_root_fruits": max_fruits,
        "first_loss_turn": first_loss_turn,
        "present_as_expected_at_terminal": bool(
            own_observations
            and expected_source(own_observations[-1][1], expected)
            and own_observations[-1][0] is rows[-1]
        ),
        "root_target_events": events,
        "deposited_currency": deposited,
        "deposited_before_train": deposited_before_train,
        "classification": classification,
    }


def summarize_task(rows: list[dict[str, str]]) -> dict:
    ordered = sorted(rows, key=lambda row: int(row["decision"]))
    train_turn = None
    previous_trains = 0
    for row in ordered:
        trains = int(row["successful_trains"])
        if trains > previous_trains and train_turn is None:
            train_turn = int(row["turn_after"])
        previous_trains = trains
    roots = []
    for row in ordered:
        if row["event"] != "bootstrap":
            continue
        x, y = (int(item) for item in row["bootstrap_target"].split(","))
        roots.append((row["bootstrap_fruit"], x, y))
    root_reports = [lifecycle(ordered, root, train_turn) for root in roots]
    missing = MISSING_SPECIES[int(ordered[0]["map_seed"])]
    missing_roots = [root for root in root_reports if root["expected_species"] == missing]
    return {
        "decisions": len(ordered),
        "terminal_workers": int(ordered[-1]["own_workers"]),
        "successful_trains": int(ordered[-1]["successful_trains"]),
        "first_train_turn": train_turn,
        "terminal_bank": vector(ordered[-1]["bank_after"]),
        "terminal_own_plants": vector(ordered[-1]["own_plants_after"]),
        "terminal_own_ripe": vector(ordered[-1]["own_ripe_after"]),
        "source_roots": root_reports,
        "missing_species": missing,
        "missing_species_deposited_before_train": sum(
            root["deposited_before_train"] for root in missing_roots
        ),
        "missing_species_root_classifications": [
            root["classification"] for root in missing_roots
        ],
    }


def validate(rows: list[dict[str, str]]) -> tuple[dict, dict[tuple[int, int, str], list[dict[str, str]]]]:
    groups: dict[tuple[int, int, str], list[dict[str, str]]] = {}
    for row in rows:
        groups.setdefault(task_key(row), []).append(row)
    expected = {(seed, seat, "resident") for seed in SEEDS for seat in (0, 1)}
    baseline = d65_repairs()
    index_failures = 0
    chain_failures = 0
    action_accounting_failures = 0
    terminal_parity: dict[str, list[str]] = {}
    mechanical_failures = 0
    trace_hash_failures = 0
    for key, task_rows in groups.items():
        ordered = sorted(task_rows, key=lambda row: int(row["decision"]))
        index_failures += int(
            [int(row["decision"]) for row in ordered]
            != list(range(1, len(ordered) + 1))
        )
        chain_failures += sum(
            previous["state_hash_after"] != current["state_hash_before"]
            for previous, current in zip(ordered, ordered[1:])
        )
        action_accounting_failures += int(
            int(ordered[-1]["selected_decisions"]) != len(ordered)
        )
        trace_hashes = [row["trace_hash"] for row in ordered]
        trace_hash_failures += int(len(trace_hashes) != len(set(trace_hashes)))
        final = ordered[-1]
        differences = [
            field
            for field in TERMINAL_PARITY_FIELDS
            if final["state_hash_after" if field == "state_hash" else field]
            != baseline[key][field]
        ]
        if differences:
            terminal_parity[f"{key[0]}:{key[1]}:{key[2]}"] = differences
        mechanical_failures += sum(
            int(final[field])
            for field in (
                "invalid_direct_commands",
                "provenance_failures",
                "deposit_prediction_failures",
            )
        )
    return (
        {
            "tasks": len(groups),
            "rows": len(rows),
            "complete_grid": set(groups) == expected,
            "decision_index_failures": index_failures,
            "state_chain_failures": chain_failures,
            "action_accounting_failures": action_accounting_failures,
            "trace_hash_failures": trace_hash_failures,
            "terminal_parity_mismatch_count": len(terminal_parity),
            "terminal_parity_mismatches": terminal_parity,
            "mechanical_failure_total": mechanical_failures,
        },
        groups,
    )


def build_report(matrix_a: Path, matrix_b: Path) -> dict:
    if matrix_a.read_bytes() != matrix_b.read_bytes():
        raise ValueError("D65i repeated traces differ")
    with matrix_a.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    integrity, groups = validate(rows)
    integrity["repeat_byte_identical"] = True
    tasks = {
        f"{seed}:{seat}:resident": summarize_task(task_rows)
        for (seed, seat, _), task_rows in sorted(groups.items())
    }
    failed = [tasks[f"9830002:{seat}:resident"] for seat in (0, 1)]
    successful = [tasks[f"9830014:{seat}:resident"] for seat in (0, 1)]
    failed_classes = Counter(
        classification
        for task in failed
        for classification in task["missing_species_root_classifications"]
    )
    successful_classes = Counter(
        classification
        for task in successful
        for classification in task["missing_species_root_classifications"]
    )
    failed_zero_deposit = sum(
        task["missing_species_deposited_before_train"] == 0 for task in failed
    )
    successful_positive_deposit = sum(
        task["missing_species_deposited_before_train"] > 0 for task in successful
    )
    integrity_pass = integrity["complete_grid"] and integrity["repeat_byte_identical"] and all(
        integrity[field] == 0
        for field in (
            "decision_index_failures",
            "state_chain_failures",
            "action_accounting_failures",
            "trace_hash_failures",
            "terminal_parity_mismatch_count",
            "mechanical_failure_total",
        )
    )
    discriminator_pass = failed_zero_deposit == 2 and successful_positive_deposit == 2
    return {
        "schema": "troll-farm-d65i-source-survival-audit-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "consumed D65 lifecycle diagnosis only; no value or candidate claim",
        "inputs": {
            "protocol": sha256_file(PROTOCOL),
            "runner": sha256_file(RUNNER),
            "analyzer": sha256_file(Path(__file__)),
            "d65_matrix": sha256_file(D65_MATRIX),
            "matrix_a": sha256_file(matrix_a),
            "matrix_b": sha256_file(matrix_b),
        },
        "integrity": integrity,
        "tasks": tasks,
        "missing_species_discriminator": {
            "failed_zero_deposit_tasks": failed_zero_deposit,
            "failed_tasks": 2,
            "failed_root_classifications": dict(sorted(failed_classes.items())),
            "successful_positive_deposit_tasks": successful_positive_deposit,
            "successful_tasks": 2,
            "successful_root_classifications": dict(sorted(successful_classes.items())),
            "pass": discriminator_pass,
        },
        "decision": {
            "status": "diagnosed" if integrity_pass and discriminator_pass else "invalid",
            "mechanism": (
                "missing_species_source_removed_before_first_deposit"
                if integrity_pass and discriminator_pass
                else "unresolved"
            ),
            "next_experiment": (
                "atomic_source_to_first_deposit_lease"
                if integrity_pass and discriminator_pass
                else "source_trace_integrity_or_broader_capitalization_audit"
            ),
            "construct_candidate": False,
            "open_fresh_d65": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def analyze(matrix_a: Path, matrix_b: Path, output: Path) -> dict:
    report = build_report(matrix_a, matrix_b)
    atomic_write_new(output, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix_a", type=Path)
    parser.add_argument("matrix_b", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = analyze(args.matrix_a, args.matrix_b, args.output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
