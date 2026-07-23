#!/usr/bin/env python3
"""Write the frozen outcome-blind D79a spatial job-scorer population."""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d79a-spatial-target-job-population-protocol-2026-07-21.md"
OUTPUT = ANALYSIS / "d79a-spatial-job-population.tsv"
EXPECTED_PROTOCOL_SHA256 = "fbbc571ceaaa705ebb004c16af4f73907c16f644a235d82a744e73590a1509b4"

SEED = 7_901
RANDOM_POLICIES = 32
SHARED_FEATURES = 46
CANDIDATE_FEATURES = 44
JOB_CONTEXT_FEATURES = 16
JOB_FEATURES = CANDIDATE_FEATURES + JOB_CONTEXT_FEATURES
HIDDEN = 8
PARAMETERS = (
    HIDDEN * SHARED_FEATURES
    + HIDDEN
    + HIDDEN * JOB_FEATURES
    + HIDDEN
    + HIDDEN
    + JOB_CONTEXT_FEATURES
    + 1
)


def random_parameters(rng: np.random.Generator) -> np.ndarray:
    """Draw one policy in the exact frozen serialization order."""

    parts = (
        rng.normal(0.0, 1.0 / np.sqrt(SHARED_FEATURES), (HIDDEN, SHARED_FEATURES)),
        rng.normal(0.0, 0.10, HIDDEN),
        rng.normal(0.0, 1.0 / np.sqrt(JOB_FEATURES), (HIDDEN, JOB_FEATURES)),
        rng.normal(0.0, 0.10, HIDDEN),
        rng.normal(0.0, 1.0 / np.sqrt(HIDDEN), HIDDEN),
        rng.normal(0.0, 0.25, JOB_CONTEXT_FEATURES),
        rng.normal(0.0, 0.10, 1),
    )
    values = np.concatenate([part.reshape(-1) for part in parts])
    assert values.shape == (PARAMETERS,)
    return np.round(values, 8)


def population() -> list[tuple[str, np.ndarray]]:
    rng = np.random.Generator(np.random.PCG64(SEED))
    rows = [("zero", np.zeros(PARAMETERS, dtype=np.float64))]
    rows.extend(
        (f"random_{index:02d}", random_parameters(rng))
        for index in range(RANDOM_POLICIES)
    )
    return rows


def main() -> None:
    if not PROTOCOL.exists() or sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise SystemExit("D79a protocol missing or changed")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D79a population")
    fields = ["policy", *(f"param_{index:03d}" for index in range(PARAMETERS))]
    with OUTPUT.open("x", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(fields)
        for label, values in population():
            writer.writerow([label, *(f"{value:.8f}" for value in values)])
    print(f"{OUTPUT}\t{sha256(OUTPUT)}")


if __name__ == "__main__":
    main()
