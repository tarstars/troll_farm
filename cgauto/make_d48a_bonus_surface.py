#!/usr/bin/env python3
"""Write the frozen D48a economic-bonus perturbation catalog."""

from __future__ import annotations

import csv
from pathlib import Path

from cgauto.analyze_d41a_macro_bc import sha256


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
PROTOCOL = ANALYSIS / "d48a-economic-bonus-surface-protocol-2026-07-21.md"
OUTPUT = ANALYSIS / "d48a-economic-bonus-surface-policies.tsv"
EXPECTED_PROTOCOL_SHA256 = "4f3691dbc83cd9c0791719791de6518bb884034fabc59bc67fe151ff0a57580e"


def catalog() -> list[tuple[str, float, float, float]]:
    return [
        ("anchor", 1.0, 1.0, 1.0),
        ("provenance_zero", 0.0, 1.0, 1.0),
        ("provenance_double", 2.0, 1.0, 1.0),
        ("renew_zero", 1.0, 0.0, 1.0),
        ("renew_double", 1.0, 2.0, 1.0),
        ("bank_zero", 1.0, 1.0, 0.0),
        ("bank_double", 1.0, 1.0, 2.0),
    ]


def main() -> None:
    if not PROTOCOL.exists() or sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise SystemExit("D48a protocol missing or changed")
    if OUTPUT.exists():
        raise SystemExit("refusing to overwrite D48a policy catalog")
    with OUTPUT.open("x", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(("policy", "provenance_scale", "renew_scale", "bank_scale"))
        for label, provenance, renew, bank in catalog():
            writer.writerow(
                (label, f"{provenance:.6f}", f"{renew:.6f}", f"{bank:.6f}")
            )
    print(f"{OUTPUT}\t{sha256(OUTPUT)}")


if __name__ == "__main__":
    main()
