#!/usr/bin/env python3
"""Analyze D74's paired same-state ordinary-option continuations."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
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
PROTOCOL = ANALYSIS / "d74a-paired-online-option-value-protocol-2026-07-21.md"
MANIFEST = ANALYSIS / "d74a-option-value-manifest.tsv"
MANIFEST_SUMMARY = ANALYSIS / "d74a-option-value-manifest-summary.json"
GENERATOR = ROOT / "cgauto/make_d74a_option_value_manifest.py"
RUNNER = ROOT / "rust/src/bin/d74_paired_option_values.rs"
MODES = ("balanced", "harvest", "renew", "fell")
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
    return {
        "rows": len(rows),
        "parse_failures": parse_failures,
        "feature_hash_failures": hash_failures,
        "unique_identities": len(identities),
        "sample_ids_exact": sorted(int(row["sample_id"]) for row in rows)
        == list(range(len(rows))),
        "partition_counts": dict(sorted(partitions.items())),
        "strata_exact": set(strata) == expected_strata
        and all(strata[key] == 6 for key in expected_strata),
        "summary_pass": bool(summary.get("pass")),
        "summary_manifest_hash_exact": summary.get("manifest") == sha256_file(MANIFEST),
        "pass": (
            len(rows) == 576
            and parse_failures == 0
            and hash_failures == 0
            and len(identities) == len(rows)
            and sorted(int(row["sample_id"]) for row in rows) == list(range(len(rows)))
            and partitions == Counter({"discovery": 288, "validation": 288})
            and set(strata) == expected_strata
            and all(strata[key] == 6 for key in expected_strata)
            and bool(summary.get("pass"))
            and summary.get("manifest") == sha256_file(MANIFEST)
        ),
    }


def validate_results(
    rows: list[dict[str, str]], manifest: list[dict[str, str]]
) -> dict:
    manifest_by_id = {int(row["sample_id"]): row for row in manifest}
    expected_baseline_tasks = len(
        {
            (int(row["map_seed"]), int(row["seat"]), row["opponent"])
            for row in manifest
        }
    )
    expected = {(sample_id, mode) for sample_id in manifest_by_id for mode in range(4)}
    actual = set()
    parse_failures = 0
    identity_failures = 0
    failure_totals = Counter()
    reward_errors = []
    crop_failures = 0
    baseline_task_values: dict[tuple[int, int, str], set[tuple[str, ...]]] = defaultdict(set)
    for row in rows:
        try:
            sample_id = int(row["sample_id"])
            mode = int(row["mode_index"])
            actual.add((sample_id, mode))
            source = manifest_by_id[sample_id]
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
                or row["mode"] != MODES[mode]
            )
            for field in FAILURE_FIELDS:
                failure_totals[field] += int(row[field])
            reward_errors.append(float(row["reward_identity_error"]))
            crop_failures += int(int(row["own_created_crops"]) <= 0)
            if mode == 0:
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
        and all(report["failure_totals"].get(field, 0) == 0 for field in FAILURE_FIELDS)
        and report["crop_failures"] == 0
        and report["maximum_reward_identity_error"] < 1.0e-4
        and report["baseline_task_consistency_failures"] == 0
        and report["baseline_tasks"] == report["expected_baseline_tasks"]
    )


def quantiles(values: list[int]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "p10": float(np.quantile(array, 0.10)),
        "p90": float(np.quantile(array, 0.90)),
        "positive_rate": float(np.mean(array > 0)),
        "tie_rate": float(np.mean(array == 0)),
        "negative_rate": float(np.mean(array < 0)),
    }


def paired_dataset(
    rows: list[dict[str, str]], manifest: list[dict[str, str]]
) -> list[dict]:
    manifest_by_id = {int(row["sample_id"]): row for row in manifest}
    grouped: dict[int, dict[int, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        grouped[int(row["sample_id"])][int(row["mode_index"])] = row
    dataset = []
    for sample_id in sorted(grouped):
        modes = grouped[sample_id]
        baseline = modes[0]
        advantages = []
        own_deltas = []
        opponent_deltas = []
        for mode in range(4):
            advantages.append(int(modes[mode]["margin"]) - int(baseline["margin"]))
            own_deltas.append(int(modes[mode]["own_score"]) - int(baseline["own_score"]))
            opponent_deltas.append(
                int(modes[mode]["opponent_score"]) - int(baseline["opponent_score"])
            )
        best = min(
            range(4),
            key=lambda mode: (
                -int(modes[mode]["margin"]),
                -int(modes[mode]["own_score"]),
                int(modes[mode]["opponent_score"]),
                mode,
            ),
        )
        source = manifest_by_id[sample_id]
        dataset.append(
            {
                "sample_id": sample_id,
                "partition": source["partition"],
                "opponent": source["opponent"],
                "seat": int(source["seat"]),
                "phase": source["phase"],
                "turn": int(source["turn"]),
                "features": feature_vector(source).astype(np.float64),
                "advantages": np.asarray(advantages, dtype=np.float64),
                "own_deltas": np.asarray(own_deltas, dtype=np.float64),
                "opponent_deltas": np.asarray(opponent_deltas, dtype=np.float64),
                "oracle_mode": best,
                "oracle_advantage": advantages[best],
                "oracle_own_delta": own_deltas[best],
                "oracle_opponent_delta": opponent_deltas[best],
            }
        )
    return dataset


def headroom_summary(dataset: list[dict]) -> dict:
    oracle = [row["oracle_advantage"] for row in dataset]
    counts = Counter(MODES[row["oracle_mode"]] for row in dataset)
    by_opponent = {
        opponent: statistics.fmean(
            row["oracle_advantage"] for row in dataset if row["opponent"] == opponent
        )
        for opponent in OPPONENTS
    }
    by_partition = {
        partition: quantiles(
            [row["oracle_advantage"] for row in dataset if row["partition"] == partition]
        )
        for partition in ("discovery", "validation")
    }
    by_phase = {
        phase: quantiles(
            [row["oracle_advantage"] for row in dataset if row["phase"] == phase]
        )
        for phase in ("early", "middle", "late")
    }
    action_advantages = {
        MODES[mode]: quantiles([int(row["advantages"][mode]) for row in dataset])
        for mode in range(4)
    }
    return {
        "states": len(dataset),
        "oracle": quantiles(oracle),
        "oracle_mode_counts": {mode: counts.get(mode, 0) for mode in MODES},
        "mean_oracle_own_score_delta": statistics.fmean(
            row["oracle_own_delta"] for row in dataset
        ),
        "mean_oracle_opponent_score_delta": statistics.fmean(
            row["oracle_opponent_delta"] for row in dataset
        ),
        "opponent_mean_oracle_advantage": by_opponent,
        "partition_oracle": by_partition,
        "phase_oracle": by_phase,
        "action_advantages": action_advantages,
    }


def fit_ridge(
    features: np.ndarray, targets: np.ndarray, alpha: float = 10.0
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = features.mean(axis=0)
    scale = features.std(axis=0)
    scale = np.where(scale == 0.0, 1.0, scale)
    standardized = (features - mean) / scale
    design = np.concatenate((np.ones((len(features), 1)), standardized), axis=1)
    penalty = np.eye(design.shape[1], dtype=np.float64) * alpha
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(design.T @ design + penalty, design.T @ targets)
    return coefficients, mean, scale


def predict_ridge(
    features: np.ndarray,
    coefficients: np.ndarray,
    mean: np.ndarray,
    scale: np.ndarray,
) -> np.ndarray:
    standardized = (features - mean) / scale
    design = np.concatenate((np.ones((len(features), 1)), standardized), axis=1)
    return design @ coefficients


def selected_modes(predictions: np.ndarray) -> np.ndarray:
    alternatives = predictions.argmax(axis=1)
    values = predictions[np.arange(len(predictions)), alternatives]
    return np.where(values > 0.0, alternatives + 1, 0)


def ranker_summary(dataset: list[dict], predictions: np.ndarray) -> dict:
    modes = selected_modes(predictions)
    advantages = np.asarray(
        [row["advantages"][mode] for row, mode in zip(dataset, modes, strict=True)],
        dtype=np.float64,
    )
    activated = modes > 0
    action_counts = Counter(MODES[int(mode)] for mode in modes)
    oracle_mean = statistics.fmean(row["oracle_advantage"] for row in dataset)
    by_opponent = {
        opponent: float(
            np.mean(
                [
                    advantage
                    for row, advantage in zip(dataset, advantages, strict=True)
                    if row["opponent"] == opponent
                ]
            )
        )
        for opponent in OPPONENTS
    }
    return {
        "states": len(dataset),
        "activation_tasks": int(activated.sum()),
        "activation_rate": float(activated.mean()),
        "selected_action_counts": {mode: action_counts.get(mode, 0) for mode in MODES},
        "selected_nonbalanced_modes": sum(
            action_counts.get(mode, 0) > 0 for mode in MODES[1:]
        ),
        "mean_realized_advantage": float(advantages.mean()),
        "median_realized_advantage": float(np.median(advantages)),
        "strict_improvement_rate_all": float(np.mean(advantages > 0)),
        "activated_positive_rate": (
            float(np.mean(advantages[activated] > 0)) if activated.any() else None
        ),
        "activated_negative_rate": (
            float(np.mean(advantages[activated] < 0)) if activated.any() else None
        ),
        "opponent_mean_advantage": by_opponent,
        "positive_opponent_families": sum(value > 0 for value in by_opponent.values()),
        "oracle_mean_advantage": oracle_mean,
        "oracle_value_capture": float(advantages.mean() / oracle_mean) if oracle_mean > 0 else None,
    }


def quarantined(inputs: dict, integrity: dict) -> dict:
    return {
        "schema": "troll-farm-d74a-paired-option-values-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "paired one-boundary ordinary-option value and grouped ridge learnability",
        "inputs": inputs,
        "integrity": integrity,
        "headroom": None,
        "ranker": None,
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
    integrity_pass = (
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
        "pass": integrity_pass,
    }
    if not integrity_pass:
        return quarantined(inputs, integrity)

    for timing in timings:
        timing["continuations"] = len(rows_a)
        timing["continuations_per_second"] = len(rows_a) / timing["elapsed_seconds"]
    dataset = paired_dataset(rows_a, manifest)
    headroom = headroom_summary(dataset)
    discovery = [row for row in dataset if row["partition"] == "discovery"]
    validation = [row for row in dataset if row["partition"] == "validation"]
    x_discovery = np.stack([row["features"] for row in discovery])
    y_discovery = np.stack([row["advantages"][1:] for row in discovery])
    x_validation = np.stack([row["features"] for row in validation])
    coefficients, mean, scale = fit_ridge(x_discovery, y_discovery, alpha=10.0)
    discovery_predictions = predict_ridge(x_discovery, coefficients, mean, scale)
    validation_predictions = predict_ridge(x_validation, coefficients, mean, scale)
    discovery_ranker = ranker_summary(discovery, discovery_predictions)
    validation_ranker = ranker_summary(validation, validation_predictions)

    nonbalanced_counts = [headroom["oracle_mode_counts"][mode] for mode in MODES[1:]]
    headroom_gates = {
        "at_least_480_states": headroom["states"] >= 480,
        "mean_oracle_advantage_at_least_5": headroom["oracle"]["mean"] >= 5,
        "strict_oracle_improvement_at_least_55pct": headroom["oracle"]["positive_rate"] >= 0.55,
        "every_opponent_oracle_at_least_1": all(
            value >= 1 for value in headroom["opponent_mean_oracle_advantage"].values()
        ),
        "two_nonbalanced_modes_best_at_least_24": sum(value >= 24 for value in nonbalanced_counts)
        >= 2,
        "own_nonnegative_or_opponent_nonpositive": (
            headroom["mean_oracle_own_score_delta"] >= 0
            or headroom["mean_oracle_opponent_score_delta"] <= 0
        ),
    }
    ranker_gates = {
        "activation_between_20_and_80pct": (
            0.20 <= validation_ranker["activation_rate"] <= 0.80
        ),
        "mean_realized_advantage_at_least_2": (
            validation_ranker["mean_realized_advantage"] >= 2
        ),
        "activated_positive_rate_at_least_55pct": (
            validation_ranker["activated_positive_rate"] is not None
            and validation_ranker["activated_positive_rate"] >= 0.55
        ),
        "at_least_two_nonbalanced_modes": (
            validation_ranker["selected_nonbalanced_modes"] >= 2
        ),
        "every_opponent_at_least_minus3": all(
            value >= -3 for value in validation_ranker["opponent_mean_advantage"].values()
        ),
        "at_least_six_positive_opponents": (
            validation_ranker["positive_opponent_families"] >= 6
        ),
        "capture_at_least_25pct_oracle": validation_ranker["oracle_value_capture"] >= 0.25,
    }
    headroom_pass = all(headroom_gates.values())
    ranker_pass = all(ranker_gates.values())
    if headroom_pass and ranker_pass:
        status = "headroom_and_grouped_ranker_pass"
        next_experiment = "d75_disjoint_prospective_complete_policy"
    elif headroom_pass:
        status = "headroom_pass_ranker_failure"
        next_experiment = "bounded_recurrent_value_or_direct_lookahead_preflight"
    else:
        status = "one_deviation_headroom_failure"
        next_experiment = "multi_batch_option_sequences"
    return {
        "schema": "troll-farm-d74a-paired-option-values-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "paired one-boundary ordinary-option value and grouped ridge learnability",
        "inputs": inputs,
        "integrity": integrity,
        "headroom": headroom,
        "ranker": {
            "alpha": 10.0,
            "features": 72,
            "targets": ["harvest", "renew", "fell"],
            "discovery": discovery_ranker,
            "validation": validation_ranker,
            "feature_mean": mean.tolist(),
            "feature_scale": scale.tolist(),
            "coefficients_intercept_then_features": coefficients.tolist(),
        },
        "gates": {
            "integrity": True,
            "headroom": headroom_gates,
            "ranker": ranker_gates,
            "headroom_pass": headroom_pass,
            "ranker_pass": ranker_pass,
            "full_pass": headroom_pass and ranker_pass,
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
                "headroom": report["headroom"],
                "ranker": report["ranker"],
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
