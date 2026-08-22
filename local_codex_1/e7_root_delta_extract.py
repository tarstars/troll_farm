#!/usr/bin/env python3
"""Publish the trace-free E7 root/opponent delta table from a locked output.

This utility only extracts already-computed values.  It refuses unknown inputs,
verifies the complete original E7 integrity contract, and does not fit or run a
policy.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import tempfile


REPO = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "e7a-root-delta-pricing-input-2026-08-02.csv"
)
EXPECTED_SOURCE_HASHES = {
    "e7-type-to-cut-j8.json": (
        "18648731768f0756c787ddc52fe83a547213e60e2f35e993b80d2fd45c7fea14"
    ),
    "e7-type-to-cut-j1.json": (
        "288cd0a0d21dcf2437553b94dba936878f32ac3fe3380d38901476ec7aa26ca8"
    ),
}
EXPECTED_NORMALIZED_HASH = (
    "c7a9d614ca607227b1dfb9649783a034212b4446cf5838250768695dff0044a5"
)
EXPECTED_ROW_HASHES = {
    "value_rows_sha256": (
        "d3f3687945983c4809518388a0269db97d8a50c6ba6917fc12c63ef418410c76"
    ),
    "geometry_rows_sha256": (
        "cf22b763f5fa738a8bd31ac6f4eabc79c58a4a79c4572e696579d3c91a64461a"
    ),
    "divergence_rows_sha256": (
        "220e4b7f0d790ca8bd5f04dca5ef9a2e61a76c9a5ad4b430cfaf95703e4c4e02"
    ),
    "oracle_rows_sha256": (
        "0ed6247f419c986e45a8fcbf78a6102a63c1ae9876f8e1befdcba4ce4949dba1"
    ),
}
COLUMNS = (
    "seed",
    "opponent",
    "control_species",
    "delta_paired_margin",
    "delta_seat_margins",
    "delta_policy_score",
    "delta_opponent_score",
    "delta_paired_wood_edge",
)
COLUMN_TYPES = {
    "seed": "integer",
    "opponent": "string",
    "control_species": "string enum: LEMON|PLUM",
    "delta_paired_margin": "finite number",
    "delta_seat_margins": "JSON array of two finite numbers",
    "delta_policy_score": "finite number",
    "delta_opponent_score": "finite number",
    "delta_paired_wood_edge": "finite number",
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def rows_sha256(rows: list[dict]) -> str:
    return sha256_bytes(canonical_bytes(rows))


def verify_and_extract(source: Path) -> tuple[list[dict], dict]:
    expected_source_hash = EXPECTED_SOURCE_HASHES.get(source.name)
    if expected_source_hash is None:
        raise ValueError(f"unrecognized locked E7 input name: {source.name}")

    source_bytes = source.read_bytes()
    source_hash = sha256_bytes(source_bytes)
    if source_hash != expected_source_hash:
        raise ValueError(
            f"source SHA-256 mismatch: expected {expected_source_hash}, got {source_hash}"
        )

    payload = json.loads(source_bytes)
    normalized = copy.deepcopy(payload)
    normalized.pop("jobs", None)
    normalized_hash = sha256_bytes(canonical_bytes(normalized))
    if normalized_hash != EXPECTED_NORMALIZED_HASH:
        raise ValueError(
            "normalized payload SHA-256 mismatch: "
            f"expected {EXPECTED_NORMALIZED_HASH}, got {normalized_hash}"
        )

    value_rows = payload.get("value_rows")
    geometry_rows = payload.get("geometry", {}).get("rows")
    oracle_rows = payload.get("oracle_rows")
    if not all(isinstance(rows, list) for rows in (value_rows, geometry_rows, oracle_rows)):
        raise ValueError("locked E7 payload is missing a required row collection")
    divergence_rows = [
        {
            "seed": row["seed"],
            "opponent": row["opponent"],
            "seat_activated": row["seat_activated"],
            "divergences": [seat["divergence"] for seat in row["seats"]],
        }
        for row in value_rows
    ]
    actual_row_hashes = {
        "value_rows_sha256": rows_sha256(value_rows),
        "geometry_rows_sha256": rows_sha256(geometry_rows),
        "divergence_rows_sha256": rows_sha256(divergence_rows),
        "oracle_rows_sha256": rows_sha256(oracle_rows),
    }
    if actual_row_hashes != EXPECTED_ROW_HASHES:
        raise ValueError(
            "original row hash mismatch: "
            + json.dumps(actual_row_hashes, sort_keys=True)
        )
    if payload.get("hashes") != EXPECTED_ROW_HASHES:
        raise ValueError("payload-declared row hashes do not match the locked contract")

    compact_rows = []
    for row in value_rows:
        compact = {column: row[column] for column in COLUMNS}
        if not isinstance(compact["seed"], int):
            raise ValueError("seed must be an integer")
        if compact["control_species"] not in ("LEMON", "PLUM"):
            raise ValueError("control_species is outside the locked binary action space")
        if not isinstance(compact["delta_seat_margins"], list) or len(
            compact["delta_seat_margins"]
        ) != 2:
            raise ValueError("delta_seat_margins must contain exactly two seats")
        compact_rows.append(compact)

    compact_rows.sort(key=lambda row: (row["seed"], row["opponent"]))
    keys = [(row["seed"], row["opponent"]) for row in compact_rows]
    if len(compact_rows) != 360 or len(set(keys)) != 360:
        raise ValueError("expected exactly 360 unique seed/opponent rows")

    provenance = {
        "source_path": str(source),
        "source_sha256": source_hash,
        "source_jobs": payload.get("jobs"),
        "normalized_payload_sha256": normalized_hash,
        "original_row_hashes": actual_row_hashes,
    }
    return compact_rows, provenance


def csv_bytes(rows: list[dict]) -> bytes:
    with tempfile.TemporaryFile(mode="w+", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            rendered = dict(row)
            rendered["delta_seat_margins"] = json.dumps(
                row["delta_seat_margins"], separators=(",", ":")
            )
            writer.writerow(rendered)
        handle.seek(0)
        return handle.read().encode("utf-8")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def repo_display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO.resolve()))
    except ValueError:
        return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path("/tmp/e7-type-to-cut-j8.json")
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    output = args.output.resolve()
    manifest_path = (
        args.manifest.resolve()
        if args.manifest
        else output.with_suffix(".manifest.json")
    )
    rows, provenance = verify_and_extract(args.input.resolve())
    rendered_csv = csv_bytes(rows)
    manifest = {
        "schema": 1,
        "task": "20260802-initial-state-sector-policy-audit",
        "purpose": "trace-free no-fit input for frozen E7a sector pricing",
        "source": provenance,
        "table": {
            "path": repo_display_path(output),
            "format": "CSV; delta_seat_margins is compact JSON",
            "row_count": len(rows),
            "columns": list(COLUMNS),
            "column_contract": COLUMN_TYPES,
            "sorted_by": ["seed", "opponent"],
            "sorted_rows_sha256": rows_sha256(rows),
            "csv_sha256": sha256_bytes(rendered_csv),
        },
        "constraints": {
            "fit_performed": False,
            "simulation_performed": False,
            "trace_or_command_streams_published": False,
            "frozen_rule_changed": False,
        },
    }
    atomic_write(output, rendered_csv)
    atomic_write(
        manifest_path,
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    print(f"wrote {len(rows)} rows to {output}")
    print(f"manifest {manifest_path}")
    print(f"sorted rows SHA-256 {manifest['table']['sorted_rows_sha256']}")


if __name__ == "__main__":
    main()
