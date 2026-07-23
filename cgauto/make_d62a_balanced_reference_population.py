#!/usr/bin/env python3
"""Create the frozen zero-linear D61 population used for D62 balanced parity."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "data" / "analysis" / "live-agent-6553250"
SOURCE = ANALYSIS / "d61a-renewable-safe-batch-option-population.tsv"
TARGET = ANALYSIS / "d62a-balanced-reference-population.tsv"

EXPECTED_SOURCE_SHA256 = (
    "e7021ac2ef7e99a7f89dbe700473674f451c186e837d51046712036443790f5f"
)
SOURCE_LABEL = "linear_00"
TARGET_LABEL = "d62_zero_linear_balanced_reference"
PARAMETERS = 224


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("D62 balanced-reference source population hash mismatch")
    if TARGET.exists():
        raise SystemExit(f"refusing to overwrite {TARGET}")

    lines = SOURCE.read_text().splitlines()
    if len(lines) != 70:
        raise SystemExit(f"expected header plus 69 policies, found {len(lines)} lines")
    changed = 0
    output = [lines[0]]
    for line in lines[1:]:
        fields = line.split("\t")
        if len(fields) != PARAMETERS + 2:
            raise SystemExit(f"invalid population width for {fields[0]!r}")
        if fields[0] == SOURCE_LABEL:
            if fields[1] != "linear":
                raise SystemExit("D62 balanced reference source is not linear")
            fields = [TARGET_LABEL, "linear", *(["0.00000000"] * PARAMETERS)]
            changed += 1
        output.append("\t".join(fields))
    if changed != 1:
        raise SystemExit(f"expected exactly one {SOURCE_LABEL!r} row, found {changed}")

    with TARGET.open("x") as target:
        target.write("\n".join(output) + "\n")
    print(f"wrote {TARGET} sha256={sha256(TARGET)}")


if __name__ == "__main__":
    main()
