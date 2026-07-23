#!/usr/bin/env python3
"""Validate D42 continuations and run the single frozen grouped selector."""

from __future__ import annotations

import csv
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256
from cgauto.train_d41g_linear_value_filter import delta_stats, grouped_means, threshold_for_share
from cgauto.train_d41h_relu_value_filter import (
    fit_relu,
    fits_bit_exact,
    maximum_raw_parity_error,
    raw_parameters,
    raw_predict,
    standardized_predict,
)


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d42-context-complete-continuation-protocol-2026-07-21.md"
MANIFEST = ANALYSIS / "d42-context-manifest-9773000-9773063.tsv"
ROWS = ANALYSIS / "d42-context-results-9773000-9773063.tsv"
AA_A = ANALYSIS / "d42-context-aa-a-128.tsv"
AA_B = ANALYSIS / "d42-context-aa-b-128.tsv"
OUTPUT = ANALYSIS / "d42-context-discovery-result.json"
WEIGHTS = ANALYSIS / "d42-context-selector-weights.npz"
RESIDENT = ROOT / "cgauto" / "submissions" / "candidate-agent6553250-preseed-orchard-coverage-slim.min.rs"

EXPECTED_PROTOCOL_SHA256 = "3f0e0a0ac6b80ac3ef9716dd576b77aeec5b902e78dc73d59a4dc11a66afc95b"
EXPECTED_MANIFEST_SHA256 = "6d7a09bcba26b3cc9a65e583d3b48699704a0dcab545a1d631404b0a13ffba3f"
EXPECTED_ROWS_SHA256 = "fd7525314a272b6ce3b9b22788f46af08e7841ff8452b6eea4b17352f951a7a4"
EXPECTED_CANONICAL_AA_SHA256 = "33527b343a95316fc9f4904363090e4dcd679a6fbad52a858762677f0436e064"
EXPECTED_RESIDENT_SHA256 = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
SEED_BASE = 9_773_000
FEATURES = 194
ROWS_EXPECTED = 1087
FOLDS = 8
WIDTH = 8
WEIGHT_DECAY = 0.01
TARGET = "positive_bce"
SHARE = 0.50
FULL_SEED = 4_218
SCALARS = FEATURES * WIDTH + WIDTH + WIDTH + 1 + 1


def canonical_hash(path: Path, limit: int | None = None) -> str:
    digest = hashlib.sha256()
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        fields = [field for field in reader.fieldnames or () if field != "elapsed_us"]
        digest.update(("\t".join(fields) + "\n").encode())
        for index, row in enumerate(reader):
            if limit is not None and index >= limit:
                break
            digest.update(("\t".join(row[field] for field in fields) + "\n").encode())
    return digest.hexdigest()


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def load_rows(path: Path, manifest: list[dict[str, str]]) -> tuple[dict[str, np.ndarray], dict]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        rows = list(reader)
        fields = reader.fieldnames or []
    feature_names = [f"feature_{index:03}" for index in range(FEATURES)]
    expected_prefix = list(manifest[0]) + [
        "baseline_own_score",
        "baseline_opponent_score",
        "baseline_margin",
        "baseline_own_workers",
        "baseline_opponent_workers",
        "baseline_own_created_crops",
        "baseline_successful_trains",
        "baseline_invalidated_jobs",
        "baseline_invalid_direct_commands",
        "baseline_provenance_failures",
        "baseline_deposit_prediction_failures",
        "baseline_action_hash",
        "baseline_state_hash",
        "treatment_own_score",
        "treatment_opponent_score",
        "treatment_margin",
        "treatment_own_workers",
        "treatment_opponent_workers",
        "treatment_own_created_crops",
        "treatment_successful_trains",
        "treatment_invalidated_jobs",
        "treatment_invalid_direct_commands",
        "treatment_provenance_failures",
        "treatment_deposit_prediction_failures",
        "treatment_action_hash",
        "treatment_state_hash",
        "own_score_delta",
        "opponent_score_delta",
        "margin_delta",
        "elapsed_us",
    ]
    if fields != expected_prefix + feature_names:
        raise RuntimeError("unexpected D42 result schema")
    if len(rows) != ROWS_EXPECTED or len(manifest) != ROWS_EXPECTED:
        raise RuntimeError("unexpected D42 row count")

    features = np.empty((len(rows), FEATURES), dtype=np.float32)
    baseline_by_task: dict[tuple[str, str, str], tuple[str, ...]] = {}
    integrity_failures = 0
    identity_failures = 0
    arithmetic_failures = 0
    for index, (row, expected) in enumerate(zip(rows, manifest)):
        for name in expected:
            if name == "residual_gap":
                if abs(float(row[name]) - float(expected[name])) > 1e-6:
                    identity_failures += 1
            elif row[name] != expected[name]:
                identity_failures += 1
        features[index] = [float(row[name]) for name in feature_names]
        if (
            int(row["baseline_invalid_direct_commands"])
            or int(row["baseline_provenance_failures"])
            or int(row["baseline_deposit_prediction_failures"])
            or int(row["treatment_invalid_direct_commands"])
            or int(row["treatment_provenance_failures"])
            or int(row["treatment_deposit_prediction_failures"])
            or int(row["baseline_own_workers"]) > 3
            or int(row["treatment_own_workers"]) > 3
        ):
            integrity_failures += 1
        own_delta = int(row["treatment_own_score"]) - int(row["baseline_own_score"])
        opponent_delta = int(row["treatment_opponent_score"]) - int(
            row["baseline_opponent_score"]
        )
        margin_delta = own_delta - opponent_delta
        if (
            own_delta != int(row["own_score_delta"])
            or opponent_delta != int(row["opponent_score_delta"])
            or margin_delta != int(row["margin_delta"])
        ):
            arithmetic_failures += 1
        task = (row["map_seed"], row["seat"], row["opponent_index"])
        baseline = tuple(row[name] for name in expected_prefix[17:30])
        if task in baseline_by_task and baseline_by_task[task] != baseline:
            integrity_failures += 1
        baseline_by_task[task] = baseline
    if not np.isfinite(features).all():
        integrity_failures += 1
    if identity_failures or integrity_failures or arithmetic_failures:
        raise RuntimeError(
            "D42 validation failed: "
            f"identity={identity_failures}, integrity={integrity_failures}, "
            f"arithmetic={arithmetic_failures}"
        )

    data = {
        "features": features,
        "margin_delta": np.asarray([int(row["margin_delta"]) for row in rows], dtype=np.float32),
        "map_seed": np.asarray([int(row["map_seed"]) for row in rows], dtype=np.int64),
        "fold": np.asarray(
            [(int(row["map_seed"]) - SEED_BASE) % FOLDS for row in rows], dtype=np.int8
        ),
        "opponent": np.asarray([int(row["opponent_index"]) for row in rows], dtype=np.int8),
        "phase": np.asarray([0 if row["phase"] == "early" else 1 for row in rows], dtype=np.int8),
        "residual_gap": np.asarray([float(row["residual_gap"]) for row in rows], dtype=np.float32),
        "sample_id": np.asarray([int(row["sample_id"]) for row in rows], dtype=np.int32),
    }
    if set(data["fold"].tolist()) != set(range(FOLDS)):
        raise RuntimeError("D42 missing grouped fold")
    if not np.array_equal(data["sample_id"], np.arange(ROWS_EXPECTED)):
        raise RuntimeError("D42 sample order mismatch")
    audit = {
        "rows": len(rows),
        "features": FEATURES,
        "finite": True,
        "identity_failures": identity_failures,
        "integrity_failures": integrity_failures,
        "arithmetic_failures": arithmetic_failures,
        "unique_tasks": len(baseline_by_task),
        "folds": FOLDS,
    }
    return data, audit


def discovery_metrics(data: dict[str, np.ndarray], scores: np.ndarray, threshold: float) -> dict:
    selected = scores >= threshold
    margin = data["margin_delta"].astype(np.float64)
    overall = delta_stats(margin[selected])
    below = int(np.count_nonzero(selected & (data["residual_gap"] < 0.280)))
    phase_means = grouped_means(margin, data["phase"], selected)
    fold_means = grouped_means(margin, data["fold"], selected)
    opponent_means = grouped_means(margin, data["opponent"], selected)
    gates = {
        "at_least_400_rows": overall["samples"] >= 400,
        "at_least_160_below_0280": below >= 160,
        "mean_at_least_12": overall["mean"] >= 12,
        "normal_95_low_above_8": overall["normal_95_low"] > 8,
        "positive_rate_at_least_65pct": overall["positive_rate"] >= 0.65,
        "negative_rate_at_most_27pct": overall["negative_rate"] <= 0.27,
        "phase_means": set(phase_means) == {"0", "1"}
        and phase_means["0"] >= 14
        and phase_means["1"] >= 5,
        "all_eight_fold_means_positive": len(fold_means) == 8
        and min(fold_means.values()) > 0,
        "opponent_breadth": len(opponent_means) == 8
        and sum(value > 0 for value in opponent_means.values()) >= 6
        and min(opponent_means.values()) >= -10,
    }
    return {
        "threshold": threshold,
        "selected_rows": int(selected.sum()),
        "selected_share": float(selected.mean()),
        "below_0280": below,
        "margin": overall,
        "phase_means": phase_means,
        "fold_means": fold_means,
        "opponent_means": opponent_means,
        "gates": gates,
        "pass": all(gates.values()),
    }


def main() -> None:
    started = time.monotonic()
    for path, expected in (
        (PROTOCOL, EXPECTED_PROTOCOL_SHA256),
        (MANIFEST, EXPECTED_MANIFEST_SHA256),
        (ROWS, EXPECTED_ROWS_SHA256),
        (RESIDENT, EXPECTED_RESIDENT_SHA256),
    ):
        if not path.exists():
            raise SystemExit(f"missing D42 prerequisite: {path}")
        if sha256(path) != expected:
            raise SystemExit(f"D42 prerequisite hash mismatch: {path}")
    if OUTPUT.exists() or WEIGHTS.exists():
        raise SystemExit("refusing to overwrite D42 discovery artifacts")
    aa_a = canonical_hash(AA_A)
    aa_b = canonical_hash(AA_B)
    full_prefix = canonical_hash(ROWS, limit=128)
    if {aa_a, aa_b, full_prefix} != {EXPECTED_CANONICAL_AA_SHA256}:
        raise SystemExit("D42 A/A or full-prefix mismatch")

    manifest = read_manifest(MANIFEST)
    data, audit = load_rows(ROWS, manifest)
    oof = np.empty(ROWS_EXPECTED, dtype=np.float32)
    fold_parity = []
    fold_losses = []
    for fold in range(FOLDS):
        train = data["fold"] != fold
        held = ~train
        fitted = fit_relu(
            data["features"][train],
            data["margin_delta"][train],
            target_name=TARGET,
            width=WIDTH,
            weight_decay=WEIGHT_DECAY,
            seed=4_210 + fold,
        )
        oof[held] = standardized_predict(fitted, data["features"][held])
        fold_parity.append(maximum_raw_parity_error(fitted, data["features"][held]))
        fold_losses.append(fitted["final_loss"])
    threshold = threshold_for_share(oof, SHARE)
    discovery = discovery_metrics(data, oof, threshold)

    full = None
    repeat_exact = None
    raw_parity = None
    production_threshold = None
    source_estimate = None
    if discovery["pass"]:
        arguments = {
            "target_name": TARGET,
            "width": WIDTH,
            "weight_decay": WEIGHT_DECAY,
            "seed": FULL_SEED,
        }
        first = fit_relu(data["features"], data["margin_delta"], **arguments)
        second = fit_relu(data["features"], data["margin_delta"], **arguments)
        repeat_exact = fits_bit_exact(first, second)
        raw = raw_parameters(first)
        full_scores = standardized_predict(first, data["features"])
        raw_parity = maximum_raw_parity_error(first, data["features"])
        production_threshold = threshold_for_share(full_scores, discovery["selected_share"])
        np.savez(
            WEIGHTS,
            input_weight=raw["input_weight"],
            input_bias=raw["input_bias"],
            output_weight=raw["output_weight"],
            output_bias=raw["output_bias"],
            threshold=np.asarray(production_threshold, dtype=np.float32),
            residual_gap_min=np.asarray(0.200, dtype=np.float32),
            residual_gap_max=np.asarray(0.340, dtype=np.float32),
        )
        resident_bytes = RESIDENT.stat().st_size
        source_estimate = {
            "resident_bytes": resident_bytes,
            "available_bytes": 100_000 - resident_bytes,
            "model_scalars": SCALARS,
            "packed_f32_literal_bytes_upper_estimate": SCALARS * 12,
            "context_and_inference_logic_bytes_allowance": 12_000,
            "estimated_total_bytes": resident_bytes + SCALARS * 12 + 12_000,
            "maximum_average_bytes_per_scalar_with_no_new_logic": (
                100_000 - resident_bytes
            ) / SCALARS,
            "parameter_count_pass": SCALARS == 1_570,
            "estimated_source_below_100000": resident_bytes + SCALARS * 12 + 12_000
            < 100_000,
        }
        full = {
            "seed": FULL_SEED,
            "repeat_bit_exact": repeat_exact,
            "raw_prediction_parity_error": raw_parity,
            "production_threshold": production_threshold,
            "training_metrics": discovery_metrics(data, full_scores, production_threshold),
            "raw_training_score_parity": float(
                np.max(np.abs(full_scores - raw_predict(raw, data["features"])))
            ),
        }

    pass_for_external = bool(
        discovery["pass"]
        and repeat_exact
        and raw_parity is not None
        and raw_parity <= 1e-5
        and SCALARS == 1_570
        and source_estimate is not None
        and source_estimate["estimated_source_below_100000"]
    )
    report = {
        "protocol": str(PROTOCOL),
        "protocol_sha256": sha256(PROTOCOL),
        "inputs": {
            "manifest": str(MANIFEST),
            "manifest_sha256": sha256(MANIFEST),
            "rows": str(ROWS),
            "rows_sha256": sha256(ROWS),
            "aa_a_sha256": sha256(AA_A),
            "aa_b_sha256": sha256(AA_B),
            "canonical_aa_sha256": aa_a,
            "canonical_full_prefix_sha256": full_prefix,
            "resident_sha256": sha256(RESIDENT),
        },
        "audit": audit,
        "model": {
            "features": FEATURES,
            "width": WIDTH,
            "target": TARGET,
            "weight_decay": WEIGHT_DECAY,
            "epochs": 600,
            "learning_rate": 0.01,
            "share": SHARE,
            "folds": FOLDS,
            "maximum_fold_raw_parity_error": max(fold_parity),
            "mean_fold_final_loss": float(np.mean(fold_losses)),
            "scalars_including_threshold": SCALARS,
        },
        "discovery": discovery,
        "full_fit": full,
        "source_estimate": source_estimate,
        "weights": str(WEIGHTS) if WEIGHTS.exists() else None,
        "weights_sha256": sha256(WEIGHTS) if WEIGHTS.exists() else None,
        "pass_for_external_replication": pass_for_external,
        "external_bank_opened": False,
        "wall_seconds": time.monotonic() - started,
        "scope": "fresh D42 grouped discovery only; no external outcome or platform action",
    }
    OUTPUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "output": str(OUTPUT),
                "pass_for_external_replication": pass_for_external,
                "discovery": discovery,
                "full_fit": full,
                "weights_sha256": report["weights_sha256"],
                "wall_seconds": report["wall_seconds"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
