#!/usr/bin/env python3
"""Generate the frozen D61 renewable-safe batch-option policy population."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = (
    ROOT
    / "data"
    / "analysis"
    / "live-agent-6553250"
    / "d61a-renewable-safe-batch-option-population.tsv"
)
FEATURES = 56
MODES = 4
PARAMETERS = FEATURES * MODES
LINEAR_POLICIES = 64
RNG_SEED = 6101


def population_rows() -> list[tuple[str, str, np.ndarray]]:
    zero = np.zeros(PARAMETERS, dtype=np.float64)
    rows = [
        ("d40_control", "control", zero.copy()),
        ("safe_balanced", "balanced", zero.copy()),
        ("safe_harvest", "harvest", zero.copy()),
        ("safe_renew", "renew", zero.copy()),
        ("safe_fell", "fell", zero.copy()),
    ]
    rng = np.random.Generator(np.random.PCG64(RNG_SEED))
    for index in range(LINEAR_POLICIES):
        weights = rng.normal(0.0, 0.5, size=(MODES, FEATURES))
        weights[:, 0] = rng.normal(0.0, 0.15, size=MODES)
        weights -= weights.mean(axis=0, keepdims=True)
        rows.append((f"linear_{index:02d}", "linear", weights.reshape(-1)))
    return rows


def render() -> str:
    target = io.StringIO(newline="")
    writer = csv.writer(target, delimiter="\t", lineterminator="\n")
    writer.writerow(
        ["policy", "kind", *(f"param_{index:03d}" for index in range(PARAMETERS))]
    )
    for policy, kind, parameters in population_rows():
        writer.writerow([policy, kind, *(f"{value:.8f}" for value in parameters)])
    return target.getvalue()


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class D61PopulationTests(unittest.TestCase):
    def test_catalog_shape_and_labels(self) -> None:
        rows = population_rows()
        self.assertEqual(len(rows), 69)
        self.assertEqual(len({row[0] for row in rows}), 69)
        self.assertEqual(sum(row[1] == "linear" for row in rows), 64)
        self.assertTrue(all(row[2].shape == (PARAMETERS,) for row in rows))

    def test_common_mode_component_is_removed(self) -> None:
        for _, kind, flat in population_rows():
            if kind != "linear":
                continue
            weights = flat.reshape(MODES, FEATURES)
            np.testing.assert_allclose(weights.mean(axis=0), 0.0, atol=1.0e-12)

    def test_render_is_deterministic(self) -> None:
        self.assertEqual(render(), render())
        self.assertEqual(len(render().splitlines()), 70)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    text = render()
    if arguments.check:
        if not arguments.output.exists() or arguments.output.read_text() != text:
            raise SystemExit(f"D61 population mismatch: {arguments.output}")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(text)
    print(f"{digest(text)}  {arguments.output}")


if __name__ == "__main__":
    main()
