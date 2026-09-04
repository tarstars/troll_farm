#!/usr/bin/env python3
"""Audit current authoritative Git trees for literal seeds in a proposed range."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from typing import BinaryIO


DECIMAL_TOKEN = re.compile(rb"(?<![0-9A-Za-z])([0-9][0-9_]{8,})(?![0-9A-Za-z])")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def refs(prefix: str) -> list[tuple[str, str]]:
    output = subprocess.check_output(
        ["git", "for-each-ref", "--format=%(refname) %(objectname)", prefix], text=True
    )
    values = [tuple(line.split()) for line in output.splitlines() if line.strip()]
    if not values:
        raise RuntimeError(f"no refs under {prefix}")
    return [(name, commit) for name, commit in values]


def tree_blobs(ref_values: list[tuple[str, str]]) -> dict[str, list[tuple[str, str]]]:
    blobs: dict[str, list[tuple[str, str]]] = {}
    for ref, _ in ref_values:
        raw = subprocess.check_output(["git", "ls-tree", "-r", "-z", ref])
        for entry in raw.split(b"\0"):
            if not entry:
                continue
            metadata, path = entry.split(b"\t", 1)
            _mode, kind, oid = metadata.decode().split()
            if kind != "blob":
                continue
            locations = blobs.setdefault(oid, [])
            if len(locations) < 8:
                locations.append((ref, path.decode(errors="replace")))
    return blobs


def read_batch_header(stream: BinaryIO) -> tuple[str, int]:
    line = stream.readline()
    if not line:
        raise RuntimeError("git cat-file --batch ended early")
    fields = line.decode().strip().split()
    if len(fields) != 3 or fields[1] != "blob":
        raise RuntimeError(f"unexpected cat-file response: {line!r}")
    return fields[0], int(fields[2])


def scan(
    blobs: dict[str, list[tuple[str, str]]], seed_start: int, seed_stop_exclusive: int
) -> tuple[int, int, list[dict]]:
    process = subprocess.Popen(
        ["git", "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    assert process.stdin is not None and process.stdout is not None
    total_bytes = 0
    hits: list[dict] = []
    try:
        for oid in sorted(blobs):
            process.stdin.write(oid.encode() + b"\n")
            process.stdin.flush()
            returned_oid, size = read_batch_header(process.stdout)
            if returned_oid != oid:
                raise RuntimeError("cat-file returned a different object")
            content = process.stdout.read(size)
            if len(content) != size or process.stdout.read(1) != b"\n":
                raise RuntimeError("short cat-file object")
            total_bytes += size
            for match in DECIMAL_TOKEN.finditer(content):
                token = match.group(1).replace(b"_", b"")
                try:
                    value = int(token)
                except ValueError:
                    continue
                if seed_start <= value < seed_stop_exclusive:
                    hits.append(
                        {
                            "value": value,
                            "blob": oid,
                            "byte_offset": match.start(1),
                            "locations": [
                                {"ref": ref, "path": path} for ref, path in blobs[oid]
                            ],
                        }
                    )
                    if len(hits) >= 100:
                        return len(blobs), total_bytes, hits
    finally:
        process.stdin.close()
        process.wait()
    return len(blobs), total_bytes, hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref-prefix", default="refs/remotes/origin")
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--seed-stop-exclusive", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.seed_stop_exclusive <= args.seed_start:
        parser.error("seed range must be non-empty")
    ref_values = refs(args.ref_prefix)
    blobs = tree_blobs(ref_values)
    blob_count, byte_count, hits = scan(blobs, args.seed_start, args.seed_stop_exclusive)
    report = {
        "schema_version": 1,
        "created_utc": utc_now(),
        "claim_scope": (
            "literal decimal seed tokens in every blob at each current authoritative remote tip; "
            "this does not prove the platform never generated an identical map geometry"
        ),
        "ref_prefix": args.ref_prefix,
        "refs": [{"ref": ref, "commit": commit} for ref, commit in ref_values],
        "seed_start": args.seed_start,
        "seed_stop_exclusive": args.seed_stop_exclusive,
        "population_size": args.seed_stop_exclusive - args.seed_start,
        "unique_blobs_scanned": blob_count,
        "uncompressed_blob_bytes_scanned": byte_count,
        "hit_count": len(hits),
        "hits": hits,
        "verdict": "NO_LITERAL_PRIOR_USE_FOUND" if not hits else "RANGE_NOT_FRESH",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        f"refs={len(ref_values)} unique_blobs={blob_count} bytes={byte_count} "
        f"hits={len(hits)} verdict={report['verdict']}"
    )
    return 0 if not hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
