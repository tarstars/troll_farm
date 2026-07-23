#!/usr/bin/env python3
"""Generate D107a's frozen paired q6 proposal-controller population."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import tempfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "analysis"
    / "live-agent-6553250"
    / "d107a-q6-proposal-controller-population.tsv"
)
SEED = 10_701
FEATURES = 379
RANDOM_CONTROLLERS = 64
WEIGHT_SD = 0.25
THRESHOLD_STEP = 0.15
THRESHOLD_LEVELS = 16


def population() -> list[dict]:
    rng = np.random.Generator(np.random.PCG64(SEED))
    rows = [
        {
            "policy": "zero_control",
            "kind": "zero",
            "budget": 4,
            "parameters": [0.0] * FEATURES,
        }
    ]
    weights = np.round(
        rng.normal(0.0, WEIGHT_SD, size=(RANDOM_CONTROLLERS, FEATURES)), 8
    )
    for index, vector in enumerate(weights):
        # Feature zero is exactly the noncontrol indicator after control subtraction.
        # This deterministic ladder supplies abstention thresholds without outcomes.
        vector[0] = -THRESHOLD_STEP * (1 + index % THRESHOLD_LEVELS)
        parameters = vector.tolist()
        for kind, budget in (("one", 1), ("four", 4)):
            rows.append(
                {
                    "policy": f"{kind}_{index:02d}",
                    "kind": kind,
                    "budget": budget,
                    "parameters": parameters,
                }
            )
    return rows


def validate(rows: list[dict]) -> None:
    if len(rows) != 1 + 2 * RANDOM_CONTROLLERS:
        raise ValueError("D107a population size mismatch")
    if any(len(row["parameters"]) != FEATURES for row in rows):
        raise ValueError("D107a parameter count mismatch")
    if any(not np.isfinite(row["parameters"]).all() for row in rows):
        raise ValueError("D107a nonfinite parameter")
    if any(rows[0]["parameters"]):
        raise ValueError("D107a zero control is nonzero")
    for index in range(RANDOM_CONTROLLERS):
        one = rows[1 + 2 * index]
        four = rows[2 + 2 * index]
        if one["parameters"] != four["parameters"]:
            raise ValueError(f"D107a matched pair mismatch: {index}")
        if (one["budget"], four["budget"]) != (1, 4):
            raise ValueError(f"D107a matched budget mismatch: {index}")
        expected_threshold = -THRESHOLD_STEP * (1 + index % THRESHOLD_LEVELS)
        if one["parameters"][0] != expected_threshold:
            raise ValueError(f"D107a threshold ladder mismatch: {index}")


def render(rows: list[dict]) -> str:
    header = ["policy", "kind", "budget"] + [
        f"param_{index:03d}" for index in range(FEATURES)
    ]
    lines = ["\t".join(header)]
    for row in rows:
        values = [row["policy"], row["kind"], str(row["budget"])]
        values.extend(f"{value:.8f}" for value in row["parameters"])
        lines.append("\t".join(values))
    return "\n".join(lines) + "\n"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = population()
    validate(rows)
    content = render(rows)
    if args.check:
        if not args.output.exists() or args.output.read_text() != content:
            raise SystemExit(f"D107a population mismatch: {args.output}")
    else:
        atomic_write(args.output, content)
    print(f"D107a population: {len(rows)} policies, {FEATURES} weights each")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
