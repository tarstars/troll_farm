#!/usr/bin/env python3
"""Write the frozen outcome-blind D45a 32-parameter perturbation catalog."""

from __future__ import annotations

import csv
from pathlib import Path

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d45a-complete-policy-rate-search-surface-protocol-2026-07-21.md"
OUTPUT = ANALYSIS / "d45a-rate-search-surface-parameters.tsv"
EXPECTED_PROTOCOL_SHA256 = "185d99a54b9d9283c43301f7ca104b3367d80addcf8ea2671b07c3a7fc8660ab"
PARAMETERS = 32

# Frozen semantic coordinate, amplitude pairs. Feature layout is documented in the protocol.
DIRECTIONS = (
    ("bank", 1, 0.05),
    ("fell", 2, 0.05),
    ("harvest", 3, 0.05),
    ("renew", 4, 0.05),
    ("mine", 5, 0.05),
    ("opponent_owner", 12, 0.05),
    ("turn_renew", 24, 0.10),
    ("workers_fell", 28, 0.10),
)


def catalog() -> list[tuple[str, list[float]]]:
    rows = [("zero", [0.0] * PARAMETERS)]
    for label, coordinate, amplitude in DIRECTIONS:
        for suffix, sign in (("plus", 1.0), ("minus", -1.0)):
            values = [0.0] * PARAMETERS
            values[coordinate] = sign * amplitude
            rows.append((f"{label}_{suffix}", values))
    return rows


def main() -> None:
    if not PROTOCOL.exists() or sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise SystemExit("D45a protocol missing or changed")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D45a parameter catalog")
    fields = ["genome", *(f"param_{index:02}" for index in range(PARAMETERS))]
    with OUTPUT.open("x", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(fields)
        for label, values in catalog():
            writer.writerow([label, *(f"{value:.9f}" for value in values)])
    print(f"{OUTPUT}\t{sha256(OUTPUT)}")


if __name__ == "__main__":
    main()
