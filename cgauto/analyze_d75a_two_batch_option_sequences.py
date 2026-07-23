#!/usr/bin/env python3
"""Analyze D75's paired two-batch ordinary-option sequence audit."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import atomic_write_new, sha256_file  # noqa: E402
from cgauto.analyze_d71a_opening_portfolio_preflight import parse_timing  # noqa: E402
from cgauto.rl_batch_option_env import OPPONENTS  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data/analysis/live-agent-6553250"
PROTOCOL = ANALYSIS / "d75a-two-batch-option-sequence-protocol-2026-07-21.md"
MANIFEST = ANALYSIS / "d75a-option-sequence-manifest.tsv"
MANIFEST_SUMMARY = ANALYSIS / "d75a-option-sequence-manifest-summary.json"
GENERATOR = ROOT / "cgauto/make_d75a_option_sequence_manifest.py"
RUNNER = ROOT / "rust/src/bin/d75_two_batch_option_sequences.rs"
MODES = ("balanced", "harvest", "renew", "fell")
SEQUENCE_LABELS = tuple(f"{first}>{second}" for first in MODES for second in MODES)
PREFIX_SEQUENCES = tuple(range(0, 16, 4))
FEATURE_FIELDS = tuple(f"feature_{index:02}" for index in range(72))
FAILURE_FIELDS = (
    "invalid_direct_commands",
    "provenance_failures",
    "deposit_prediction_failures",
)
TERMINAL_IDENTITY_FIELDS = (
    "terminal_turn",
    "own_score",
    "opponent_score",
    "own_workers",
    "opponent_workers",
    "successful_trains",
    "own_created_crops",
    "opponent_created_crops",
    "ambiguous_created_crops",
    "action_hash",
    "state_hash",
)


def read_tsv(path: Path) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        return tuple(reader.fieldnames or ()), rows


def feature_vector(row: dict[str, str]) -> np.ndarray:
    return np.asarray([float(row[field]) for field in FEATURE_FIELDS], dtype="<f4")


def validate_manifest(rows: list[dict[str, str]], summary: dict) -> dict:
    parse_failures = 0
    hash_failures = 0
    identities = set()
    partitions = Counter()
    strata = Counter()
    horizon_failures = 0
    for row in rows:
        try:
            sample_id = int(row["sample_id"])
            identity = (
                int(row["map_seed"]),
                int(row["seat"]),
                int(row["opponent_index"]),
                int(row["decision_ordinal"]),
            )
            values = feature_vector(row)
            if not np.isfinite(values).all():
                raise ValueError("non-finite feature")
            digest = hashlib.sha256(values.tobytes()).hexdigest()
            hash_failures += int(digest != row["feature_hash"])
            horizon_failures += int(int(row["turn"]) >= 300)
            identities.add(identity)
            partitions[row["partition"]] += 1
            strata[(row["partition"], row["opponent"], int(row["seat"]), row["phase"])] += 1
            if sample_id < 0:
                raise ValueError("negative sample ID")
        except (KeyError, TypeError, ValueError):
            parse_failures += 1
    expected_strata = {
        (partition, opponent, seat, phase)
        for partition in ("discovery", "validation")
        for opponent in OPPONENTS
        for seat in (0, 1)
        for phase in ("early", "middle", "late")
    }
    sample_ids_exact = sorted(int(row["sample_id"]) for row in rows) == list(range(len(rows)))
    passed = (
        len(rows) == 576
        and parse_failures == 0
        and hash_failures == 0
        and horizon_failures == 0
        and len(identities) == len(rows)
        and sample_ids_exact
        and partitions == Counter({"discovery": 288, "validation": 288})
        and set(strata) == expected_strata
        and all(strata[key] == 6 for key in expected_strata)
        and bool(summary.get("pass"))
        and summary.get("manifest") == sha256_file(MANIFEST)
    )
    return {
        "rows": len(rows),
        "parse_failures": parse_failures,
        "feature_hash_failures": hash_failures,
        "horizon_failures": horizon_failures,
        "unique_identities": len(identities),
        "sample_ids_exact": sample_ids_exact,
        "partition_counts": dict(sorted(partitions.items())),
        "strata_exact": set(strata) == expected_strata
        and all(strata[key] == 6 for key in expected_strata),
        "summary_pass": bool(summary.get("pass")),
        "summary_manifest_hash_exact": summary.get("manifest") == sha256_file(MANIFEST),
        "pass": passed,
    }


def validate_results(rows: list[dict[str, str]], manifest: list[dict[str, str]]) -> dict:
    manifest_by_id = {int(row["sample_id"]): row for row in manifest}
    expected = {(sample_id, sequence) for sample_id in manifest_by_id for sequence in range(16)}
    expected_baseline_tasks = len(
        {
            (int(row["map_seed"]), int(row["seat"]), row["opponent"])
            for row in manifest
        }
    )
    actual = set()
    parse_failures = 0
    identity_failures = 0
    sequence_accounting_failures = 0
    second_reach_failures = 0
    second_feature_failures = 0
    second_turn_failures = 0
    second_execution_failures = 0
    failure_totals = Counter()
    second_requested = Counter()
    second_executed = Counter()
    second_illegal = Counter()
    reward_errors = []
    crop_failures = 0
    baseline_task_values: dict[tuple[int, int, str], set[tuple[str, ...]]] = defaultdict(set)
    for row in rows:
        try:
            sample_id = int(row["sample_id"])
            sequence = int(row["sequence_index"])
            actual.add((sample_id, sequence))
            source = manifest_by_id[sample_id]
            first = sequence // 4
            second = sequence % 4
            reached = int(row["second_reached"])
            legal = int(row["second_legal"])
            executed = int(row["second_executed"])
            second_requested[MODES[second]] += 1
            identity_failures += int(
                row["partition"] != source["partition"]
                or row["map_seed"] != source["map_seed"]
                or row["task_index"] != source["task_index"]
                or row["seat"] != source["seat"]
                or row["opponent_index"] != source["opponent_index"]
                or row["opponent"] != source["opponent"]
                or row["decision_ordinal"] != source["decision_ordinal"]
                or row["decision_turn"] != source["turn"]
                or row["phase"] != source["phase"]
                or row["feature_hash"] != source["feature_hash"]
            )
            sequence_accounting_failures += int(
                row["sequence"] != SEQUENCE_LABELS[sequence]
                or int(row["first_mode"]) != first
                or int(row["second_requested"]) != second
            )
            second_reach_failures += int(reached != 1)
            second_feature_failures += int(int(row["second_features_finite"]) != reached)
            second_turn_failures += int(
                reached == 1 and int(row["second_turn"]) <= int(row["decision_turn"])
            )
            expected_executed = second if legal else 0
            second_execution_failures += int(
                reached == 1
                and (
                    executed != expected_executed
                    or (second == 0 and legal != 1)
                    or legal not in (0, 1)
                )
            )
            if reached == 1:
                second_executed[MODES[executed]] += 1
                if legal == 0:
                    second_illegal[MODES[second]] += 1
            for field in FAILURE_FIELDS:
                failure_totals[field] += int(row[field])
            reward_errors.append(float(row["reward_identity_error"]))
            crop_failures += int(int(row["own_created_crops"]) <= 0)
            if sequence == 0:
                key = (int(row["map_seed"]), int(row["seat"]), row["opponent"])
                baseline_task_values[key].add(tuple(row[field] for field in TERMINAL_IDENTITY_FIELDS))
        except (IndexError, KeyError, TypeError, ValueError):
            parse_failures += 1
    return {
        "rows": len(rows),
        "complete_grid": len(rows) == len(expected) and actual == expected,
        "duplicate_rows": len(rows) - len(actual),
        "missing_rows": len(expected - actual),
        "unexpected_rows": len(actual - expected),
        "parse_failures": parse_failures,
        "identity_failures": identity_failures,
        "sequence_accounting_failures": sequence_accounting_failures,
        "second_reach_failures": second_reach_failures,
        "second_feature_failures": second_feature_failures,
        "second_turn_failures": second_turn_failures,
        "second_execution_failures": second_execution_failures,
        "second_requested_counts": dict(second_requested),
        "second_executed_counts": dict(second_executed),
        "second_illegal_counts": dict(second_illegal),
        "failure_totals": dict(failure_totals),
        "crop_failures": crop_failures,
        "maximum_reward_identity_error": max(reward_errors, default=float("inf")),
        "baseline_task_consistency_failures": sum(
            len(values) != 1 for values in baseline_task_values.values()
        ),
        "baseline_tasks": len(baseline_task_values),
        "expected_baseline_tasks": expected_baseline_tasks,
        "environmental_invalidated_jobs": (
            sum(int(row["invalidated_jobs"]) for row in rows) if parse_failures == 0 else None
        ),
    }


def result_integrity_pass(report: dict) -> bool:
    return (
        report["complete_grid"]
        and report["duplicate_rows"] == 0
        and report["parse_failures"] == 0
        and report["identity_failures"] == 0
        and report["sequence_accounting_failures"] == 0
        and report["second_reach_failures"] == 0
        and report["second_feature_failures"] == 0
        and report["second_turn_failures"] == 0
        and report["second_execution_failures"] == 0
        and all(report["failure_totals"].get(field, 0) == 0 for field in FAILURE_FIELDS)
        and report["crop_failures"] == 0
        and report["maximum_reward_identity_error"] < 1.0e-4
        and report["baseline_task_consistency_failures"] == 0
        and report["baseline_tasks"] == report["expected_baseline_tasks"]
        and all(report["second_executed_counts"].get(mode, 0) >= 2_000 for mode in MODES)
    )


def quantiles(values: list[int] | list[float]) -> dict[str, float]:
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


def outcome_key(row: dict[str, str], sequence: int) -> tuple[int, int, int, int, int]:
    return (
        -int(row["margin"]),
        -int(row["own_score"]),
        int(row["opponent_score"]),
        int(sequence not in PREFIX_SEQUENCES),
        sequence,
    )


def choose_best(rows: dict[int, dict[str, str]], choices: tuple[int, ...]) -> int:
    return min(choices, key=lambda sequence: outcome_key(rows[sequence], sequence))


def paired_dataset(rows: list[dict[str, str]], manifest: list[dict[str, str]]) -> list[dict]:
    manifest_by_id = {int(row["sample_id"]): row for row in manifest}
    grouped: dict[int, dict[int, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        grouped[int(row["sample_id"])][int(row["sequence_index"])] = row
    dataset = []
    for sample_id in sorted(grouped):
        sequences = grouped[sample_id]
        control = sequences[0]
        full = choose_best(sequences, tuple(range(16)))
        prefix = choose_best(sequences, PREFIX_SEQUENCES)
        source = manifest_by_id[sample_id]

        def deltas(selected: int, baseline: int) -> tuple[int, int, int, int]:
            chosen = sequences[selected]
            anchor = sequences[baseline]
            return (
                int(chosen["margin"]) - int(anchor["margin"]),
                int(chosen["own_score"]) - int(anchor["own_score"]),
                int(chosen["opponent_score"]) - int(anchor["opponent_score"]),
                int(chosen["own_workers"]) - int(anchor["own_workers"]),
            )

        full_delta = deltas(full, 0)
        prefix_delta = deltas(prefix, 0)
        incremental_delta = deltas(full, prefix)
        dataset.append(
            {
                "sample_id": sample_id,
                "partition": source["partition"],
                "opponent": source["opponent"],
                "phase": source["phase"],
                "sequences": sequences,
                "control": control,
                "full_sequence": full,
                "prefix_sequence": prefix,
                "full_delta": full_delta,
                "prefix_delta": prefix_delta,
                "incremental_delta": incremental_delta,
            }
        )
    return dataset


def comparison_summary(dataset: list[dict], kind: str) -> dict:
    sequence_field = "full_sequence" if kind == "full" else "prefix_sequence"
    delta_field = f"{kind}_delta"
    advantages = [row[delta_field][0] for row in dataset]
    own_deltas = [row[delta_field][1] for row in dataset]
    opponent_deltas = [row[delta_field][2] for row in dataset]
    worker_deltas = [row[delta_field][3] for row in dataset]
    selected = Counter(SEQUENCE_LABELS[row[sequence_field]] for row in dataset)
    strict_selected = Counter(
        SEQUENCE_LABELS[row[sequence_field]]
        for row in dataset
        if row[delta_field][0] > 0
    )
    return {
        "states": len(dataset),
        "advantage": quantiles(advantages),
        "mean_own_score_delta": statistics.fmean(own_deltas),
        "mean_opponent_score_delta": statistics.fmean(opponent_deltas),
        "worker_delta_counts": dict(sorted(Counter(worker_deltas).items())),
        "selected_sequence_counts": {
            label: selected.get(label, 0) for label in SEQUENCE_LABELS
        },
        "strict_selected_sequence_counts": {
            label: strict_selected.get(label, 0) for label in SEQUENCE_LABELS
        },
        "opponent_mean_advantage": {
            opponent: statistics.fmean(
                row[delta_field][0] for row in dataset if row["opponent"] == opponent
            )
            for opponent in OPPONENTS
        },
        "phase_mean_advantage": {
            phase: statistics.fmean(
                row[delta_field][0] for row in dataset if row["phase"] == phase
            )
            for phase in ("early", "middle", "late")
        },
        "worker_three_rate": statistics.fmean(
            int(row["sequences"][row[sequence_field]]["own_workers"]) >= 3
            for row in dataset
        ),
        "crop_creation_rate": statistics.fmean(
            int(row["sequences"][row[sequence_field]]["own_created_crops"]) > 0
            for row in dataset
        ),
    }


def incremental_summary(dataset: list[dict]) -> dict:
    advantages = [row["incremental_delta"][0] for row in dataset]
    own_deltas = [row["incremental_delta"][1] for row in dataset]
    opponent_deltas = [row["incremental_delta"][2] for row in dataset]
    worker_deltas = [row["incremental_delta"][3] for row in dataset]
    strict = [row for row in dataset if row["incremental_delta"][0] > 0]
    sequences = Counter(SEQUENCE_LABELS[row["full_sequence"]] for row in strict)
    second_modes = Counter(MODES[row["full_sequence"] % 4] for row in strict)
    return {
        "states": len(dataset),
        "advantage": quantiles(advantages),
        "mean_own_score_delta": statistics.fmean(own_deltas),
        "mean_opponent_score_delta": statistics.fmean(opponent_deltas),
        "worker_delta_counts": dict(sorted(Counter(worker_deltas).items())),
        "strict_selected_sequence_counts": {
            label: sequences.get(label, 0) for label in SEQUENCE_LABELS
        },
        "strict_selected_second_mode_counts": {
            mode: second_modes.get(mode, 0) for mode in MODES
        },
        "opponent_mean_advantage": {
            opponent: statistics.fmean(
                row["incremental_delta"][0]
                for row in dataset
                if row["opponent"] == opponent
            )
            for opponent in OPPONENTS
        },
        "phase_mean_advantage": {
            phase: statistics.fmean(
                row["incremental_delta"][0]
                for row in dataset
                if row["phase"] == phase
            )
            for phase in ("early", "middle", "late")
        },
    }


def sequence_summary(dataset: list[dict]) -> dict:
    result = {}
    for sequence, label in enumerate(SEQUENCE_LABELS):
        advantages = []
        own_deltas = []
        opponent_deltas = []
        worker_deltas = []
        for row in dataset:
            selected = row["sequences"][sequence]
            control = row["control"]
            advantages.append(int(selected["margin"]) - int(control["margin"]))
            own_deltas.append(int(selected["own_score"]) - int(control["own_score"]))
            opponent_deltas.append(
                int(selected["opponent_score"]) - int(control["opponent_score"])
            )
            worker_deltas.append(int(selected["own_workers"]) - int(control["own_workers"]))
        result[label] = {
            "advantage": quantiles(advantages),
            "mean_own_score_delta": statistics.fmean(own_deltas),
            "mean_opponent_score_delta": statistics.fmean(opponent_deltas),
            "worker_delta_counts": dict(sorted(Counter(worker_deltas).items())),
        }
    return result


def activity_summary(dataset: list[dict], result_report: dict) -> dict:
    hash_change_counts = {}
    mean_margins = {}
    for sequence, label in enumerate(SEQUENCE_LABELS):
        mean_margins[label] = statistics.fmean(
            int(row["sequences"][sequence]["margin"]) for row in dataset
        )
        if sequence % 4 != 0:
            prefix = sequence - sequence % 4
            hash_change_counts[label] = sum(
                row["sequences"][sequence]["action_hash"]
                != row["sequences"][prefix]["action_hash"]
                for row in dataset
            )
    active_nonprefix = sum(value >= 58 for value in hash_change_counts.values())
    span = max(mean_margins.values()) - min(mean_margins.values())
    gates = {
        "every_sequence_reaches_second_boundary": result_report["second_reach_failures"] == 0,
        "all_second_modes_execute_at_least_2000": all(
            result_report["second_executed_counts"].get(mode, 0) >= 2_000 for mode in MODES
        ),
        "eight_nonprefix_sequences_change_at_least_10pct": active_nonprefix >= 8,
        "sequence_mean_margin_span_at_least_15": span >= 15,
    }
    return {
        "second_requested_counts": result_report["second_requested_counts"],
        "second_executed_counts": result_report["second_executed_counts"],
        "second_illegal_counts": result_report["second_illegal_counts"],
        "nonprefix_action_hash_change_counts": hash_change_counts,
        "active_nonprefix_sequences": active_nonprefix,
        "sequence_mean_margins": mean_margins,
        "sequence_mean_margin_span": span,
        "gates": gates,
        "pass": all(gates.values()),
    }


def quarantined(inputs: dict, integrity: dict) -> dict:
    return {
        "schema": "troll-farm-d75a-two-batch-option-sequences-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "paired two-batch ordinary-option sequence headroom",
        "inputs": inputs,
        "integrity": integrity,
        "activity": None,
        "sequence_results": None,
        "full_oracle": None,
        "prefix_oracle": None,
        "incremental_oracle": None,
        "gates": {"integrity": False},
        "decision": {
            "status": "integrity_failure",
            "next_experiment": "repair_only_then_repeat_unchanged",
            "construct_candidate": False,
            "platform_action": False,
        },
    }


def build_report(
    rows_a_path: Path,
    rows_b_path: Path,
    time_a_path: Path,
    time_b_path: Path,
) -> dict:
    _, manifest = read_tsv(MANIFEST)
    summary = json.loads(MANIFEST_SUMMARY.read_text())
    _, rows_a = read_tsv(rows_a_path)
    _, rows_b = read_tsv(rows_b_path)
    manifest_integrity = validate_manifest(manifest, summary)
    result_a = validate_results(rows_a, manifest)
    result_b = validate_results(rows_b, manifest)
    repeat_exact = rows_a_path.read_bytes() == rows_b_path.read_bytes()
    timings = [parse_timing(time_a_path), parse_timing(time_b_path)]
    inputs = {
        "protocol": sha256_file(PROTOCOL),
        "manifest": sha256_file(MANIFEST),
        "manifest_summary": sha256_file(MANIFEST_SUMMARY),
        "generator": sha256_file(GENERATOR),
        "runner": sha256_file(RUNNER),
        "rows_a": sha256_file(rows_a_path),
        "rows_b": sha256_file(rows_b_path),
        "time_a": sha256_file(time_a_path),
        "time_b": sha256_file(time_b_path),
        "analyzer": sha256_file(Path(__file__)),
    }
    base_integrity_pass = (
        manifest_integrity["pass"]
        and result_integrity_pass(result_a)
        and result_integrity_pass(result_b)
        and repeat_exact
    )
    integrity = {
        "manifest": manifest_integrity,
        "results_a": result_a,
        "results_b": result_b,
        "repeat_byte_exact": repeat_exact,
        "timings": timings,
        "base_pass": base_integrity_pass,
    }
    if not base_integrity_pass:
        integrity["pass"] = False
        return quarantined(inputs, integrity)

    for timing in timings:
        timing["continuations"] = len(rows_a)
        timing["continuations_per_second"] = len(rows_a) / timing["elapsed_seconds"]
    dataset = paired_dataset(rows_a, manifest)
    activity = activity_summary(dataset, result_a)
    integrity["pass"] = activity["pass"]
    if not activity["pass"]:
        report = quarantined(inputs, integrity)
        report["activity"] = activity
        return report

    sequences = sequence_summary(dataset)
    full = comparison_summary(dataset, "full")
    prefix = comparison_summary(dataset, "prefix")
    incremental = incremental_summary(dataset)
    nonprefix_strict_counts = [
        full["strict_selected_sequence_counts"][SEQUENCE_LABELS[sequence]]
        for sequence in range(16)
        if sequence not in PREFIX_SEQUENCES
    ]
    full_gates = {
        "mean_advantage_at_least_10": full["advantage"]["mean"] >= 10,
        "strict_improvement_at_least_55pct": full["advantage"]["positive_rate"] >= 0.55,
        "every_opponent_at_least_3": all(
            value >= 3 for value in full["opponent_mean_advantage"].values()
        ),
        "three_nonprefix_sequences_win_at_least_12": sum(
            count >= 12 for count in nonprefix_strict_counts
        )
        >= 3,
        "own_nonnegative_or_opponent_nonpositive": (
            full["mean_own_score_delta"] >= 0 or full["mean_opponent_score_delta"] <= 0
        ),
        "worker_three_at_least_85pct": full["worker_three_rate"] >= 0.85,
        "crop_creation_exactly_100pct": full["crop_creation_rate"] == 1.0,
    }
    strict_second_counts = incremental["strict_selected_second_mode_counts"]
    incremental_gates = {
        "mean_increment_at_least_3": incremental["advantage"]["mean"] >= 3,
        "strict_increment_at_least_25pct": incremental["advantage"]["positive_rate"] >= 0.25,
        "every_opponent_increment_at_least_point5": all(
            value >= 0.5 for value in incremental["opponent_mean_advantage"].values()
        ),
        "two_nonbalanced_second_modes_selected_at_least_12": sum(
            strict_second_counts[mode] >= 12 for mode in MODES[1:]
        )
        >= 2,
        "own_nonnegative_or_opponent_nonpositive": (
            incremental["mean_own_score_delta"] >= 0
            or incremental["mean_opponent_score_delta"] <= 0
        ),
    }
    full_pass = all(full_gates.values())
    incremental_pass = all(incremental_gates.values())
    if full_pass and incremental_pass:
        status = "full_and_incremental_sequence_headroom_pass"
        next_experiment = "d76_grouped_sequence_value_learner"
    elif full_pass:
        status = "full_headroom_pass_increment_failure"
        next_experiment = "different_adaptive_horizon_or_history_representation"
    else:
        status = "two_batch_sequence_headroom_failure"
        next_experiment = "whole_policy_search_new_controller_representation"
    return {
        "schema": "troll-farm-d75a-two-batch-option-sequences-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "paired two-batch ordinary-option sequence headroom",
        "inputs": inputs,
        "integrity": integrity,
        "activity": activity,
        "sequence_results": sequences,
        "full_oracle": full,
        "prefix_oracle": prefix,
        "incremental_oracle": incremental,
        "gates": {
            "integrity": True,
            "full_headroom": full_gates,
            "incremental_headroom": incremental_gates,
            "full_headroom_pass": full_pass,
            "incremental_headroom_pass": incremental_pass,
            "full_pass": full_pass and incremental_pass,
        },
        "decision": {
            "status": status,
            "next_experiment": next_experiment,
            "construct_candidate": False,
            "open_confirmation": False,
            "platform_action": False,
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows-a", type=Path, required=True)
    parser.add_argument("--rows-b", type=Path, required=True)
    parser.add_argument("--time-a", type=Path, required=True)
    parser.add_argument("--time-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args.rows_a, args.rows_b, args.time_a, args.time_b)
    atomic_write_new(args.output, report)
    print(
        json.dumps(
            {
                "integrity": report["integrity"],
                "activity": report["activity"],
                "full_oracle": report["full_oracle"],
                "prefix_oracle": report["prefix_oracle"],
                "incremental_oracle": report["incremental_oracle"],
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
