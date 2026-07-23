#!/usr/bin/env python3
"""Measure frozen D29 f32 versus sole int8-dequantized deployment conversion."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
from pathlib import Path
import statistics

import numpy as np

from cgauto.d29_spatial_option_critic import (
    build_dataset,
    configure_torch,
    evaluate_policy,
    load_checkpoint,
    predict_model,
    read_labels,
    read_scalars,
    read_spatial,
    seed_cluster,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_data(
    spatial_path: Path,
    scalar_path: Path,
    label_path: Path,
    seed_start: int,
    seed_count: int,
) -> tuple[dict, dict]:
    spatial, spatial_checks = read_spatial(spatial_path)
    scalars, feature_names = read_scalars(scalar_path)
    labels = read_labels([label_path])
    data, integrity = build_dataset(
        spatial,
        scalars,
        labels,
        feature_names,
        seed_start,
        seed_count,
        spatial_checks,
    )
    if not integrity["complete"]:
        raise ValueError(f"D29a input integrity failed: {integrity}")
    return data, integrity


def partition_analysis(
    *,
    name: str,
    spatial_path: Path,
    scalar_path: Path,
    label_path: Path,
    seed_start: int,
    seed_count: int,
    block_size: int,
    precision_floor: float,
    source_checkpoint: Path,
    converted_checkpoint: Path,
) -> dict:
    data, integrity = load_data(
        spatial_path, scalar_path, label_path, seed_start, seed_count
    )
    source, source_metadata, _ = load_checkpoint(
        source_checkpoint, data["feature_names"]
    )
    converted, converted_metadata, _ = load_checkpoint(
        converted_checkpoint, data["feature_names"]
    )
    indices = np.arange(len(data["keys"]))
    source_predictions = predict_model(source, source_metadata, data, indices)
    converted_predictions = predict_model(
        converted, converted_metadata, data, indices
    )
    source_evaluation = evaluate_policy(
        data,
        source_predictions,
        seed_start,
        block_size=block_size,
        block_count=6,
        precision_floor=precision_floor,
    )
    converted_evaluation = evaluate_policy(
        data,
        converted_predictions,
        seed_start,
        block_size=block_size,
        block_count=6,
        precision_floor=precision_floor,
    )
    source_decisions = source_predictions > 0
    converted_decisions = converted_predictions > 0
    disagreement = source_decisions != converted_decisions
    source_selected = np.where(source_decisions, data["target"], 0)
    converted_selected = np.where(converted_decisions, data["target"], 0)
    source_seed_mean = statistics.mean(seed_cluster(data["keys"], source_selected))
    converted_seed_mean = statistics.mean(
        seed_cluster(data["keys"], converted_selected)
    )
    raw_error = np.abs(converted_predictions - source_predictions)
    normalized_error = raw_error / np.float32(source_metadata["target_std"])
    source_tail = source_evaluation["tail"]
    converted_tail = converted_evaluation["tail"]
    gates = {
        "finite_predictions": bool(
            np.isfinite(source_predictions).all()
            and np.isfinite(converted_predictions).all()
        ),
        "decision_disagreement_at_most_1pct": float(disagreement.mean()) <= 0.01,
        "selected_seed_mean_loss_at_most_1": (
            converted_seed_mean >= source_seed_mean - 1.0
        ),
        "catastrophic_frequency_not_above_f32": (
            converted_tail["selected_catastrophic_frequency"]
            <= source_tail["selected_catastrophic_frequency"]
        ),
        "negative_margin_mass_not_above_f32": (
            converted_tail["selected_negative_margin_mass"]
            <= source_tail["selected_negative_margin_mass"]
        ),
        "converted_retains_partition_gates": converted_evaluation["passed"],
    }
    result = {
        "name": name,
        "seed_start": seed_start,
        "seed_count": seed_count,
        "cells": len(data["keys"]),
        "integrity": integrity,
        "source_evaluation": source_evaluation,
        "converted_evaluation": converted_evaluation,
        "comparison": {
            "decision_disagreements": int(disagreement.sum()),
            "decision_disagreement_rate": float(disagreement.mean()),
            "source_switches": int(source_decisions.sum()),
            "converted_switches": int(converted_decisions.sum()),
            "source_selected_seed_mean": source_seed_mean,
            "converted_selected_seed_mean": converted_seed_mean,
            "converted_minus_source_selected_seed_mean": (
                converted_seed_mean - source_seed_mean
            ),
            "maximum_raw_prediction_absolute_error": float(raw_error.max()),
            "mean_raw_prediction_absolute_error": float(raw_error.mean()),
            "maximum_normalized_prediction_absolute_error": float(
                normalized_error.max()
            ),
            "mean_normalized_prediction_absolute_error": float(
                normalized_error.mean()
            ),
        },
        "gates": gates,
        "passed": all(gates.values()),
    }
    del data, source, converted, source_predictions, converted_predictions
    gc.collect()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-checkpoint", type=Path, required=True)
    parser.add_argument("--converted-checkpoint", type=Path, required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--repeat-payload", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repeat-manifest", type=Path, required=True)
    parser.add_argument("--verification-repeat", type=Path, required=True)
    parser.add_argument("--development-spatial", type=Path, required=True)
    parser.add_argument("--development-scalar", type=Path, required=True)
    parser.add_argument("--development-labels", type=Path, required=True)
    parser.add_argument("--confirmation-spatial", type=Path, required=True)
    parser.add_argument("--confirmation-scalar", type=Path, required=True)
    parser.add_argument("--confirmation-labels", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    configure_torch()
    reproducibility = {
        "payload_byte_identical": (
            args.payload.read_bytes() == args.repeat_payload.read_bytes()
        ),
        "manifest_byte_identical": (
            args.manifest.read_bytes() == args.repeat_manifest.read_bytes()
        ),
        "verification_checkpoint_byte_identical": (
            args.converted_checkpoint.read_bytes()
            == args.verification_repeat.read_bytes()
        ),
    }
    development = partition_analysis(
        name="development_full_checkpoint",
        spatial_path=args.development_spatial,
        scalar_path=args.development_scalar,
        label_path=args.development_labels,
        seed_start=53000,
        seed_count=600,
        block_size=100,
        precision_floor=0.78,
        source_checkpoint=args.source_checkpoint,
        converted_checkpoint=args.converted_checkpoint,
    )
    confirmation = partition_analysis(
        name="prospective_confirmation",
        spatial_path=args.confirmation_spatial,
        scalar_path=args.confirmation_scalar,
        label_path=args.confirmation_labels,
        seed_start=53600,
        seed_count=120,
        block_size=20,
        precision_floor=0.75,
        source_checkpoint=args.source_checkpoint,
        converted_checkpoint=args.converted_checkpoint,
    )
    gates = {
        "conversion_artifacts_exact_on_repeat": all(reproducibility.values()),
        "development_preserved": development["passed"],
        "confirmation_preserved": confirmation["passed"],
    }
    payload = {
        "schema": 1,
        "scope": "D29a sole int8 numerical conversion; no Rust integration, candidate, submission, or Arena action",
        "sources": {
            "source_checkpoint": str(args.source_checkpoint),
            "source_checkpoint_sha256": sha256(args.source_checkpoint),
            "converted_checkpoint": str(args.converted_checkpoint),
            "converted_checkpoint_sha256": sha256(args.converted_checkpoint),
            "payload": str(args.payload),
            "payload_sha256": sha256(args.payload),
            "manifest": str(args.manifest),
            "manifest_sha256": sha256(args.manifest),
        },
        "reproducibility": reproducibility,
        "development": development,
        "confirmation": confirmation,
        "gates": gates,
        "passed": all(gates.values()),
        "decision": {
            "open_rust_kernel": all(gates.values()),
            "build_submission_candidate": False,
            "authorize_arena": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(args.output)
    print(
        json.dumps(
            {
                "reproducibility": reproducibility,
                "development": development["comparison"],
                "confirmation": confirmation["comparison"],
                "gates": gates,
                "passed": payload["passed"],
                "decision": payload["decision"],
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
