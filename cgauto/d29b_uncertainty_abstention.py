#!/usr/bin/env python3
"""Evaluate the sole D29b int8 controller with a strict +4 activation threshold."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import struct

import numpy as np

from cgauto.d29_spatial_option_critic import (
    build_dataset,
    configure_torch,
    evaluate_policy,
    load_checkpoint,
    predict_model,
    prediction_hash,
    read_labels,
    read_scalars,
    read_spatial,
)


THRESHOLD = np.float32(4.0)
EXPECTED_CHECKPOINT_SHA256 = (
    "9d4ef336880ac2ae57e868f05cb99646f94bb2e92a7d1aedd0ad1a22d12b33ba"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_predictions(
    path: Path, data: dict, raw_predictions: np.ndarray, activation_scores: np.ndarray
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(
            (
                "seed",
                "seat",
                "opponent",
                "raw_prediction_f32_hex",
                "raw_prediction",
                "activation_score_f32_hex",
                "activation_score",
                "switch",
                "target",
                "resident_margin",
                "option_margin",
            )
        )
        for index, key in enumerate(data["keys"]):
            raw = np.float32(raw_predictions[index])
            score = np.float32(activation_scores[index])
            writer.writerow(
                (
                    *key,
                    struct.pack("<f", raw).hex(),
                    repr(float(raw)),
                    struct.pack("<f", score).hex(),
                    repr(float(score)),
                    int(score > 0),
                    int(data["target"][index]),
                    int(data["resident_margin"][index]),
                    int(data["option_margin"][index]),
                )
            )
    temporary.replace(path)


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=1) + "\n")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "confirmation"), required=True)
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--seed-count", type=int, required=True)
    parser.add_argument("--spatial", type=Path, required=True)
    parser.add_argument("--scalar", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--repeat-predictions", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    checkpoint_sha = sha256(args.checkpoint)
    if checkpoint_sha != EXPECTED_CHECKPOINT_SHA256:
        raise SystemExit(
            f"D29b checkpoint differs: {checkpoint_sha} != {EXPECTED_CHECKPOINT_SHA256}"
        )
    if args.mode == "confirmation" and args.seed_count != 120:
        raise SystemExit("D29b confirmation requires exactly 120 maps")
    if args.repeat_predictions:
        if args.repeat_predictions.resolve() == args.predictions.resolve():
            raise SystemExit("D29b repeat and current prediction paths must differ")
        if not args.repeat_predictions.is_file():
            raise SystemExit("D29b repeat prediction reference does not exist")

    configure_torch()
    spatial, spatial_checks = read_spatial(args.spatial)
    scalars, feature_names = read_scalars(args.scalar)
    labels = read_labels([args.labels])
    data, integrity = build_dataset(
        spatial,
        scalars,
        labels,
        feature_names,
        args.seed_start,
        args.seed_count,
        spatial_checks,
    )
    if not integrity["complete"]:
        raise SystemExit("D29b integrity failed")
    model, metadata, _ = load_checkpoint(args.checkpoint, feature_names)
    raw_predictions = predict_model(
        model, metadata, data, np.arange(len(data["keys"]))
    ).astype(np.float32, copy=False)
    activation_scores = (raw_predictions - THRESHOLD).astype(np.float32, copy=False)
    decisions = activation_scores > 0
    if not np.isfinite(raw_predictions).all():
        raise SystemExit("D29b produced non-finite predictions")
    digest = prediction_hash(raw_predictions, decisions)
    save_predictions(args.predictions, data, raw_predictions, activation_scores)
    repeat_exact = (
        args.predictions.read_bytes() == args.repeat_predictions.read_bytes()
        if args.repeat_predictions
        else None
    )

    evaluation = None
    if args.mode == "confirmation":
        evaluation = evaluate_policy(
            data,
            activation_scores,
            args.seed_start,
            block_size=20,
            block_count=6,
            precision_floor=0.75,
        )
        base_passed = evaluation["passed"]
        evaluation["base_passed"] = base_passed
        evaluation["raw_prediction"] = {
            "mean": float(raw_predictions.mean()),
            "standard_deviation": float(raw_predictions.std()),
            "minimum": float(raw_predictions.min()),
            "maximum": float(raw_predictions.max()),
        }
        evaluation["reproducibility"] = {
            "reference_path": (
                str(args.repeat_predictions) if args.repeat_predictions else None
            ),
            "prediction_artifact_byte_identical": repeat_exact,
        }
        evaluation["gates"]["repeat_predictions_exact"] = repeat_exact is True
        evaluation["passed"] = all(evaluation["gates"].values())
    else:
        base_passed = integrity["complete"]

    passed = (
        integrity["complete"]
        and (repeat_exact is True)
        and (evaluation is None or evaluation["passed"])
    )
    payload = {
        "schema": 1,
        "scope": "D29b frozen +4 int8 abstention controller; no Rust integration, candidate, submission, or Arena action",
        "mode": args.mode,
        "seed_start": args.seed_start,
        "seed_count": args.seed_count,
        "threshold": float(THRESHOLD),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": checkpoint_sha,
        "sources": {
            "spatial": str(args.spatial),
            "scalar": str(args.scalar),
            "labels": str(args.labels),
        },
        "integrity": integrity,
        "prediction_hash": digest,
        "predictions": str(args.predictions),
        "repeat_predictions": (
            str(args.repeat_predictions) if args.repeat_predictions else None
        ),
        "repeat_prediction_byte_identical": repeat_exact,
        "switches": int(decisions.sum()),
        "switch_rate": float(decisions.mean()),
        "evaluation": evaluation,
        "passed": passed,
        "decision": {
            "await_exact_rerun": base_passed and repeat_exact is None,
            "open_rust_kernel": passed and args.mode == "confirmation",
            "build_submission_candidate": False,
            "authorize_arena": False,
        },
    }
    save_json(args.output, payload)
    print(
        json.dumps(
            {
                "mode": args.mode,
                "integrity_complete": integrity["complete"],
                "prediction_hash": digest,
                "switches": payload["switches"],
                "switch_rate": payload["switch_rate"],
                "repeat_prediction_byte_identical": repeat_exact,
                "evaluation": evaluation,
                "passed": passed,
                "decision": payload["decision"],
            },
            indent=1,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
