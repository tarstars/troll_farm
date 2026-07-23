#!/usr/bin/env python3
"""Pad D105b roots to D104's frozen 240-root audit cardinality, then strip clones."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


TARGET_ROOTS = 240
MAX_ROOT_ID = 256


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="") as source:
        reader = csv.DictReader(source, delimiter="\t")
        return list(reader), list(reader.fieldnames or ())


def encoded_table(rows: list[dict[str, str]], fields: list[str]) -> str:
    from io import StringIO

    target = StringIO()
    writer = csv.DictWriter(
        target, fieldnames=fields, delimiter="\t", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return target.getvalue()


def write_or_verify(path: Path, encoded: str) -> None:
    if path.exists():
        if path.read_text() != encoded:
            raise RuntimeError(f"D105b existing adapter output differs: {path}")
    else:
        path.write_text(encoded)


def pad_manifest(source: Path, target: Path, metadata: Path) -> dict:
    rows, fields = read_table(source)
    by_root: dict[int, list[dict[str, str]]] = {}
    for row in rows:
        by_root.setdefault(int(row["root_id"]), []).append(row)
    if not 1 <= len(by_root) <= TARGET_ROOTS:
        raise RuntimeError("D105b source root cardinality cannot be adapted")
    missing = [root_id for root_id in range(MAX_ROOT_ID) if root_id not in by_root]
    needed = TARGET_ROOTS - len(by_root)
    clone_targets = missing[:needed]
    clone_sources = sorted(by_root)[:needed]
    padded = list(rows)
    mapping = []
    for source_root, target_root in zip(clone_sources, clone_targets, strict=True):
        for row in by_root[source_root]:
            clone = dict(row)
            clone["root_id"] = str(target_root)
            clone["arm_id"] = clone["arm_id"].replace(
                f"r{source_root:04}__", f"r{target_root:04}__", 1
            )
            padded.append(clone)
        mapping.append({"source_root_id": source_root, "clone_root_id": target_root})
    padded.sort(key=lambda row: (int(row["root_id"]), row["arm_id"]))
    write_or_verify(target, encoded_table(padded, fields))
    report = {
        "schema": "troll-farm-d105b-d104-cardinality-adapter-v1",
        "source_sha256": sha256(source),
        "padded_sha256": sha256(target),
        "source_roots": len(by_root),
        "target_roots": len(by_root) + len(mapping),
        "clone_mapping": mapping,
        "outcomes_read": False,
    }
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    write_or_verify(metadata, encoded)
    return report


def strip_proposals(source_manifest: Path, raw: Path, target: Path) -> dict:
    manifest, _ = read_table(source_manifest)
    source_roots = {row["root_id"] for row in manifest}
    rows, fields = read_table(raw)
    retained = [row for row in rows if row["root_id"] in source_roots]
    expected = len(source_roots) * 64
    if len(retained) != expected:
        raise RuntimeError(
            f"D105b stripped proposal grid mismatch: {len(retained)} != {expected}"
        )
    keys = {(row["root_id"], row["expert_index"]) for row in retained}
    if len(keys) != expected:
        raise RuntimeError("D105b stripped proposal keys are not unique")
    write_or_verify(target, encoded_table(retained, fields))
    return {
        "source_roots": len(source_roots),
        "retained_rows": len(retained),
        "raw_sha256": sha256(raw),
        "stripped_sha256": sha256(target),
        "outcomes_read": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    pad = subparsers.add_parser("pad")
    pad.add_argument("--source", type=Path, required=True)
    pad.add_argument("--output", type=Path, required=True)
    pad.add_argument("--metadata", type=Path, required=True)
    strip = subparsers.add_parser("strip")
    strip.add_argument("--manifest", type=Path, required=True)
    strip.add_argument("--raw", type=Path, required=True)
    strip.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "pad":
        result = pad_manifest(args.source, args.output, args.metadata)
    else:
        result = strip_proposals(args.manifest, args.raw, args.output)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
