#!/usr/bin/env python3
"""Generate the frozen D100 D98-anchored pair-residual population."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import tempfile

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
DEFAULT_PARENT = ANALYSIS / "d98a-bounded-whole-game-joint-assignment-population.tsv"
DEFAULT_OUTPUT = ANALYSIS / "d100a-d98-anchored-pair-residual-population.tsv"
SEED = 10001
PARENT_FEATURES = 153
RESIDUAL_FEATURES = 342
RANDOM_POLICIES = 64


def read_parents(path: Path) -> list[list[float]]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    by_policy = {row["policy"]: row for row in rows}
    parameter_fields = [f"param_{index:03d}" for index in range(PARENT_FEATURES)]
    parents = []
    for index in range(RANDOM_POLICIES):
        one = by_policy[f"one_{index:02d}"]
        four = by_policy[f"four_{index:02d}"]
        one_weights = [float(one[field]) for field in parameter_fields]
        four_weights = [float(four[field]) for field in parameter_fields]
        if one_weights != four_weights:
            raise ValueError(f"D100 D98 parent pair mismatch: {index}")
        parents.append(four_weights)
    return parents


def population(parent_path: Path = DEFAULT_PARENT) -> list[dict]:
    parents = read_parents(parent_path)
    rng = np.random.Generator(np.random.PCG64(SEED))
    residuals = np.round(
        rng.normal(0.0, 0.25, size=(RANDOM_POLICIES, RESIDUAL_FEATURES)), 8
    )
    rows = [
        {
            "policy": "d40_control",
            "kind": "control",
            "parent": "none",
            "parent_budget": 0,
            "residual_budget": 0,
            "parent_parameters": [0.0] * PARENT_FEATURES,
            "residual_parameters": [0.0] * RESIDUAL_FEATURES,
        }
    ]
    for index, parent_parameters in enumerate(parents):
        common = {
            "parent": f"four_{index:02d}",
            "parent_budget": 4,
        }
        rows.extend(
            [
                {
                    "policy": f"parent_{index:02d}",
                    "kind": "parent",
                    "residual_budget": 0,
                    "parent_parameters": parent_parameters,
                    "residual_parameters": [0.0] * RESIDUAL_FEATURES,
                    **common,
                },
                {
                    "policy": f"zero_{index:02d}",
                    "kind": "zero_residual",
                    "residual_budget": 1,
                    "parent_parameters": parent_parameters,
                    "residual_parameters": [0.0] * RESIDUAL_FEATURES,
                    **common,
                },
                {
                    "policy": f"random_{index:02d}",
                    "kind": "random_residual",
                    "residual_budget": 1,
                    "parent_parameters": parent_parameters,
                    "residual_parameters": residuals[index].tolist(),
                    **common,
                },
            ]
        )
    return rows


def render(rows: list[dict]) -> str:
    header = ["policy", "kind", "parent", "parent_budget", "residual_budget"]
    header.extend(f"parent_{index:03d}" for index in range(PARENT_FEATURES))
    header.extend(f"residual_{index:03d}" for index in range(RESIDUAL_FEATURES))
    lines = ["\t".join(header)]
    for row in rows:
        values = [
            row["policy"],
            row["kind"],
            row["parent"],
            str(row["parent_budget"]),
            str(row["residual_budget"]),
        ]
        values.extend(f"{value:.8f}" for value in row["parent_parameters"])
        values.extend(f"{value:.8f}" for value in row["residual_parameters"])
        lines.append("\t".join(values))
    return "\n".join(lines) + "\n"


def validate(rows: list[dict]) -> None:
    if len(rows) != 1 + 3 * RANDOM_POLICIES:
        raise ValueError("D100 population size mismatch")
    if any(len(row["parent_parameters"]) != PARENT_FEATURES for row in rows):
        raise ValueError("D100 parent parameter count mismatch")
    if any(len(row["residual_parameters"]) != RESIDUAL_FEATURES for row in rows):
        raise ValueError("D100 residual parameter count mismatch")
    if any(not np.isfinite(row["parent_parameters"]).all() for row in rows):
        raise ValueError("D100 nonfinite parent parameter")
    if any(not np.isfinite(row["residual_parameters"]).all() for row in rows):
        raise ValueError("D100 nonfinite residual parameter")
    for index in range(RANDOM_POLICIES):
        parent, zero, random = rows[1 + 3 * index : 4 + 3 * index]
        if not (
            parent["parent_parameters"]
            == zero["parent_parameters"]
            == random["parent_parameters"]
        ):
            raise ValueError(f"D100 parent triplet mismatch: {index}")
        if any(parent["residual_parameters"]) or any(zero["residual_parameters"]):
            raise ValueError(f"D100 nonzero control residual: {index}")
        if (parent["residual_budget"], zero["residual_budget"], random["residual_budget"]) != (
            0,
            1,
            1,
        ):
            raise ValueError(f"D100 residual budget mismatch: {index}")


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
    parser.add_argument("--parent", type=Path, default=DEFAULT_PARENT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows = population(args.parent)
    validate(rows)
    content = render(rows)
    if args.check:
        if not args.output.exists() or args.output.read_text() != content:
            raise SystemExit(f"D100 population mismatch: {args.output}")
    else:
        atomic_write(args.output, content)
    print(
        f"D100 population: {len(rows)} policies, "
        f"{PARENT_FEATURES} parent + {RESIDUAL_FEATURES} residual weights"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
