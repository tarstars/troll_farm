#!/usr/bin/env python3
"""Generate D72's immutable random recurrent-policy population."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


FEATURES = 72
HIDDEN = 12
ACTIONS = 8
POLICIES = 32
SEED = 7201


def population() -> list[dict[str, object]]:
    rng = np.random.Generator(np.random.PCG64(SEED))
    rows = []
    for index in range(POLICIES):
        wx = rng.normal(0.0, 0.35, size=(HIDDEN, FEATURES))
        raw = rng.normal(size=(HIDDEN, HIDDEN))
        q, r = np.linalg.qr(raw)
        signs = np.where(np.diag(r) < 0, -1.0, 1.0)
        wh = q * signs
        wh *= 0.70
        bh = rng.normal(0.0, 0.10, size=HIDDEN)
        wo = rng.normal(0.0, 0.50, size=(ACTIONS, HIDDEN))
        bo = rng.normal(0.0, 0.15, size=ACTIONS)
        values = np.concatenate((wx.ravel(), wh.ravel(), bh, wo.ravel(), bo))
        rows.append({"policy": f"rnn_{index:02d}", "values": values})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["policy"] + [f"param_{index:04d}" for index in range(1124)]
    if args.output.exists():
        raise FileExistsError(args.output)
    with args.output.open("x", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(fields)
        for row in population():
            values = row["values"]
            if len(values) != 1124 or not np.isfinite(values).all():
                raise ValueError("invalid D72 recurrent parameter vector")
            writer.writerow([row["policy"], *(f"{value:.8f}" for value in values)])
    print(f"wrote {POLICIES} D72 policies to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
