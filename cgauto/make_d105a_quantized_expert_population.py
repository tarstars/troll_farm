#!/usr/bin/env python3
"""Quantize D98's 64 four-use experts with one positive scale per expert."""

from __future__ import annotations

import argparse
import csv
import struct
from pathlib import Path


FEATURES = 153
EXPERTS = 64
ALLOWED_BITS = (4, 6, 8)


def f32(text: str) -> float:
    return struct.unpack("<f", struct.pack("<f", float(text)))[0]


def quantize(weights: list[float], bits: int) -> list[int]:
    if bits not in ALLOWED_BITS:
        raise ValueError(f"unsupported bit width: {bits}")
    if len(weights) != FEATURES:
        raise ValueError(f"expected {FEATURES} weights, got {len(weights)}")
    qmax = (1 << (bits - 1)) - 1
    maximum = max(abs(weight) for weight in weights)
    if maximum == 0:
        return [0] * FEATURES
    scale = maximum / qmax
    return [max(-qmax, min(qmax, round(weight / scale))) for weight in weights]


def build_population(source: Path, target: Path, bits: int) -> dict:
    with source.open(newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise RuntimeError("D105a source population has no header")
        rows = [row for row in reader if row["kind"] == "four"]
    expected_fields = ["policy", "kind", "budget"] + [
        f"param_{index:03}" for index in range(FEATURES)
    ]
    if fieldnames != expected_fields:
        raise RuntimeError("D105a source population schema mismatch")
    if [row["policy"] for row in rows] != [f"four_{index:02}" for index in range(EXPERTS)]:
        raise RuntimeError("D105a source expert ordering mismatch")

    qmax = (1 << (bits - 1)) - 1
    quantized_rows = []
    saturated = 0
    nonzero = 0
    for row in rows:
        weights = [f32(row[f"param_{index:03}"]) for index in range(FEATURES)]
        values = quantize(weights, bits)
        saturated += sum(abs(value) == qmax for value in values)
        nonzero += sum(value != 0 for value in values)
        quantized_rows.append(
            {
                "policy": row["policy"],
                "kind": "four",
                "budget": "4",
                **{
                    f"param_{index:03}": str(value)
                    for index, value in enumerate(values)
                },
            }
        )

    with target.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=expected_fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(quantized_rows)

    coefficients = EXPERTS * FEATURES
    raw_packed_bytes = (coefficients * bits + 7) // 8
    base85_bytes = ((raw_packed_bytes + 3) // 4) * 5
    return {
        "bits": bits,
        "experts": EXPERTS,
        "features": FEATURES,
        "coefficients": coefficients,
        "qmin": -qmax,
        "qmax": qmax,
        "saturated_coefficients": saturated,
        "nonzero_coefficients": nonzero,
        "raw_packed_bytes": raw_packed_bytes,
        "base85_payload_bytes": base85_bytes,
        "tsv_bytes": target.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    parser.add_argument("bits", type=int, choices=ALLOWED_BITS)
    args = parser.parse_args()
    print(build_population(args.source, args.target, args.bits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
