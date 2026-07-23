#!/usr/bin/env python3
"""Generate D110a's outcome-blind antithetic linear q6 controller population."""

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
    / "d110a-antithetic-q6-linear-population.tsv"
)
SEED = 11_001
FEATURES = 379
DIRECTIONS = 32
CONTROLLERS = 2 * DIRECTIONS
WEIGHT_SD = 0.25
THRESHOLD_STEP = 0.15
THRESHOLD_LEVELS = 16


def population() -> list[dict]:
    rng = np.random.Generator(np.random.PCG64(SEED))
    directions = np.round(
        rng.normal(0.0, WEIGHT_SD, size=(DIRECTIONS, FEATURES)), 8
    )
    weights = np.concatenate((directions, -directions), axis=0)
    rows = [
        {
            "policy": "zero_control",
            "kind": "zero",
            "budget": 4,
            "parameters": [0.0] * FEATURES,
        }
    ]
    for index, vector in enumerate(weights):
        vector = vector.copy()
        # Feature zero is one for every noncontrol proposal after control subtraction.
        # Keep an identical outcome-blind abstention ladder on both antithetic halves.
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
    if len(rows) != 1 + 2 * CONTROLLERS:
        raise ValueError("D110a population size mismatch")
    if rows[0]["policy"] != "zero_control" or any(rows[0]["parameters"]):
        raise ValueError("D110a zero controller mismatch")
    for index in range(CONTROLLERS):
        one = rows[1 + 2 * index]
        four = rows[2 + 2 * index]
        if one["policy"] != f"one_{index:02d}" or four["policy"] != f"four_{index:02d}":
            raise ValueError("D110a controller labels mismatch")
        if one["parameters"] != four["parameters"] or (one["budget"], four["budget"]) != (1, 4):
            raise ValueError("D110a paired controller mismatch")
        expected = -THRESHOLD_STEP * (1 + index % THRESHOLD_LEVELS)
        if one["parameters"][0] != expected:
            raise ValueError("D110a threshold ladder mismatch")
        if len(one["parameters"]) != FEATURES or not np.isfinite(one["parameters"]).all():
            raise ValueError("D110a invalid controller parameters")
    for index in range(DIRECTIONS):
        positive = np.asarray(rows[1 + 2 * index]["parameters"])
        negative = np.asarray(rows[1 + 2 * (index + DIRECTIONS)]["parameters"])
        np.testing.assert_array_equal(positive[1:], -negative[1:])


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
            raise SystemExit(f"D110a population mismatch: {args.output}")
    else:
        atomic_write(args.output, content)
    print(f"D110a population: {len(rows)} policies, {FEATURES} weights each")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
