#!/usr/bin/env python3
"""Export the frozen D63b instantaneous-economy classifier for D64a Rust use."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.analyze_d61p_field_snapshot import sha256_file  # noqa: E402
from cgauto.analyze_d63a_workforce_transition import (  # noqa: E402
    fit_logistic,
    materialize_features,
    metrics,
    predict,
)
from cgauto.analyze_d63b_capitalization_ablation import (  # noqa: E402
    EXPECTED_SOURCE_SHA256,
    SOURCE,
    eligible_rows,
    family_rows,
    load_source,
)


REPO = Path(__file__).resolve().parent.parent
D63B_RESULT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d63b-capitalization-signal-ablation-2026-07-21.json"
)
PROTOCOL = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d64a-field-gated-late-capitalization-protocol-2026-07-21.md"
)
EXPECTED_D63B_SHA256 = (
    "6970d5ae2949c71f32bcade6f992d39b2f1f984c15d73b1f4593cbceaf5db059"
)
THRESHOLD = 0.5


def nearest_rank(values: np.ndarray, probability: float) -> float:
    if not len(values) or not 0.0 < probability <= 1.0:
        raise ValueError("invalid nearest-rank request")
    ordered = np.sort(values)
    index = math.ceil(probability * len(ordered)) - 1
    return float(ordered[index])


def fit_snapshot_model() -> dict:
    source = load_source(SOURCE)
    if sha256_file(D63B_RESULT) != EXPECTED_D63B_SHA256:
        raise ValueError("D63b result hash mismatch")
    d63b = json.loads(D63B_RESULT.read_text())
    rows = family_rows(eligible_rows(source), "snapshot")
    feature_names, matrix = materialize_features(rows, "features")
    labels = np.asarray([row["label"] for row in rows], dtype=int)
    discovery_indices = np.asarray(
        [index for index, row in enumerate(rows) if row["partition"] == "discovery"]
    )
    validation_indices = np.asarray(
        [index for index, row in enumerate(rows) if row["partition"] == "validation"]
    )
    discovery_x = matrix[discovery_indices]
    validation_x = matrix[validation_indices]
    discovery_y = labels[discovery_indices]
    validation_y = labels[validation_indices]
    model = fit_logistic(discovery_x, discovery_y)
    measured = {
        "discovery": metrics(discovery_y, predict(model, discovery_x)),
        "validation": metrics(validation_y, predict(model, validation_x)),
    }
    expected = d63b["models"]["snapshot"]
    parity = {}
    for split in ("discovery", "validation"):
        for key in ("roc_auc", "balanced_accuracy_at_0_5", "brier_score"):
            parity[f"{split}_{key}"] = math.isclose(
                float(measured[split][key]),
                float(expected[split][key]),
                rel_tol=0.0,
                abs_tol=1e-15,
            )
    if feature_names != expected["feature_names"] or not all(parity.values()):
        raise ValueError(f"D64 model export does not reproduce D63b: {parity}")
    validation_z = (validation_x - model["means"]) / model["scales"]
    validation_rms_z = np.sqrt(np.mean(validation_z * validation_z, axis=1))
    support_radius = nearest_rank(validation_rms_z, 0.95)
    return {
        "schema": "troll-farm-d64a-snapshot-model-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": {
            "d63a": EXPECTED_SOURCE_SHA256,
            "d63b": EXPECTED_D63B_SHA256,
            "protocol": sha256_file(PROTOCOL),
            "exporter": sha256_file(Path(__file__)),
        },
        "threshold": THRESHOLD,
        "support_radius_rms_z_p95": support_radius,
        "support_reference": {
            "rows": len(validation_x),
            "minimum": float(validation_rms_z.min()),
            "median": float(np.median(validation_rms_z)),
            "maximum": float(validation_rms_z.max()),
            "nearest_rank": "ceil(0.95*n)-1",
        },
        "fit": {
            "feature_count": len(feature_names),
            "intercept": float(model["beta"][0]),
            "converged": bool(model["converged"]),
            "iterations": int(model["iterations"]),
            "maximum_step": float(model["maximum_step"]),
            "parity": parity,
            "metrics": measured,
        },
        "features": [
            {
                "name": name,
                "mean": float(mean),
                "scale": float(scale),
                "standardized_coefficient": float(coefficient),
            }
            for name, mean, scale, coefficient in zip(
                feature_names, model["means"], model["scales"], model["beta"][1:]
            )
        ],
    }


def canonical_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"


def write_new(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        handle.write(text)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    report = fit_snapshot_model()
    rendered = canonical_json(report)
    write_new(args.output, rendered)
    print(
        json.dumps(
            {
                "features": report["fit"]["feature_count"],
                "threshold": report["threshold"],
                "support_radius": report["support_radius_rms_z_p95"],
                "sha256": hashlib.sha256(rendered.encode()).hexdigest(),
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()

