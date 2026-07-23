#!/usr/bin/env python3
"""Generate the frozen D96 factorized per-worker residual population."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
import tempfile

import numpy as np


REPO = Path(__file__).resolve().parent.parent
DEFAULT_D61 = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d61a-renewable-safe-batch-option-population.tsv"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "d96a-factorized-worker-option-population.tsv"
)
SEED = 9601
MODES = 4
WORKER_FEATURES = 53
PARAMETERS = MODES * WORKER_FEATURES
POLICIES = 64


def read_linear_labels(path: Path) -> list[str]:
    with path.open(newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    labels = [row["policy"] for row in rows if row["kind"] == "linear"]
    expected = [f"linear_{index:02d}" for index in range(POLICIES)]
    if labels != expected:
        raise ValueError(f"D61 linear population mismatch: {labels}")
    return labels


def population(path: Path = DEFAULT_D61) -> list[dict]:
    bases = read_linear_labels(path)
    rng = np.random.Generator(np.random.PCG64(SEED))
    rows = []
    zeros = np.zeros((MODES, WORKER_FEATURES), dtype=np.float64)
    for index, base in enumerate(bases):
        draws = rng.normal(0.0, 0.25, size=(WORKER_FEATURES, MODES))
        draws -= draws.mean(axis=1, keepdims=True)
        residual = np.round(draws.T, 8)
        for kind, weights in (("factor_zero", zeros), ("factor_random", residual)):
            rows.append(
                {
                    "policy": f"{kind}_{index:02d}",
                    "kind": kind,
                    "base": base,
                    "parameters": weights.reshape(-1).tolist(),
                }
            )
    return rows


def render(rows: list[dict]) -> str:
    header = ["policy", "kind", "base"] + [
        f"param_{index:03d}" for index in range(PARAMETERS)
    ]
    lines = ["\t".join(header)]
    for row in rows:
        values = [row["policy"], row["kind"], row["base"]]
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
    parser.add_argument("--d61-population", type=Path, default=DEFAULT_D61)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = render(population(args.d61_population))
    if args.check:
        if not args.output.exists() or args.output.read_text() != content:
            raise SystemExit(f"D96 population mismatch: {args.output}")
    else:
        atomic_write(args.output, content)
    print(f"D96 population: {POLICIES * 2} policies, {PARAMETERS} residual weights each")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
