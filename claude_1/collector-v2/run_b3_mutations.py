#!/usr/bin/env python3
"""Mutation drive for the B3 daily packer (task `20260811-s3-collector-v2`).

The packer makes two load-bearing claims — the round-trip is lossless and the bytes are
deterministic — and both are the kind that stay silently false for a long time. Each mutant
below is a way one of them could break in production: a stamped gzip header, a lexical id
sort, a digest taken over the wrong bytes, an overwrite-inviting rerun key.

Mechanics and exit-status semantics live in `mutation_runner.py`
(0 all caught · 1 control not green · 2 survivors · 3 incomplete).

Usage: python3 claude_1/collector-v2/run_b3_mutations.py --out <results.json>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mutation_runner import run_drive  # noqa: E402

HERE = Path(__file__).resolve().parent
TARGET = HERE / "packer.py"
TESTS = HERE / "tests"

MUTANTS = [
    ("P1-gzip-stamps-mtime",
     "lets gzip write the current time into the header, so identical input differs by run",
     'with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as handle:',
     'with gzip.GzipFile(fileobj=buffer, mode="wb") as handle:'),
    ("P2-lexical-id-sort",
     "sorts game ids as text, so 1000 precedes 999 and pack order depends on id width",
     'paths = sorted((Path(p) for p in game_files), key=lambda p: int(p.stem))',
     'paths = sorted((Path(p) for p in game_files), key=lambda p: p.stem)'),
    ("P3-unsorted-json-keys",
     "drops sort_keys from pack lines, so byte output depends on dict insertion order",
     '            ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\\n")',
     '            ensure_ascii=False).encode("utf-8") + b"\\n")'),
    ("P4-ascii-escaping",
     "escapes non-ASCII, diverging from Part A's pack encoding for unicode nicknames",
     '            ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\\n")',
     '            ensure_ascii=True, sort_keys=True).encode("utf-8") + b"\\n")'),
    ("P5-digest-over-decoded-text",
     "hashes the decoded string's default encoding rather than the file's exact bytes",
     '        digest = hashlib.sha256(raw).hexdigest()',
     '        digest = hashlib.sha256(raw.decode("utf-8").encode("utf-16")).hexdigest()'),
    ("P6-size-from-characters",
     "records character count instead of byte length, wrong for every non-ASCII game",
     '             "raw": raw.decode("utf-8")},',
     '             "raw": raw.decode("utf-8"), "size": len(raw.decode("utf-8"))},'),
    ("P7-rerun-key-collides",
     "ignores the rerun counter, so a re-run overwrites the original day's object",
     '    stem = date if rerun == 0 else f"{date}.rerun-{rerun}"\n    return f"{DAILY_PREFIX}/{stem}{PACK_EXTENSION}"',
     '    stem = date\n    return f"{DAILY_PREFIX}/{stem}{PACK_EXTENSION}"'),
    ("P8-manifest-schema-drift",
     "renames the manifest's game_id field, breaking the shared backfill/daily reader",
     '            {"game_id": game_id, "sha256": digest, "size": len(raw), "pack": pack_key},',
     '            {"gameId": game_id, "sha256": digest, "size": len(raw), "pack": pack_key},'),
    ("P9-corrupt-pack-accepted",
     "returns pack records without checking them against their own recorded digest",
     '        if actual != record["sha256"]:',
     '        if False and actual != record["sha256"]:'),
    ("P10-duplicate-ids-accepted",
     "packs the same game id twice instead of refusing the input",
     '    if len(set(ids)) != len(ids):',
     '    if False and len(set(ids)) != len(ids):'),
    ("P11-loose-date-accepted",
     "accepts any date string, so a malformed date silently names an object",
     '    if not DATE_RE.match(date):\n        raise ValueError(f"date must be YYYY-MM-DD, got {date!r}")\n    stem = date if rerun == 0 else f"{date}.rerun-{rerun}"\n    return f"{DAILY_PREFIX}/{stem}{PACK_EXTENSION}"',
     '    stem = date if rerun == 0 else f"{date}.rerun-{rerun}"\n    return f"{DAILY_PREFIX}/{stem}{PACK_EXTENSION}"'),
    # A mutant on the zstd branch's CONTENT_TYPE was considered and rejected for the same
    # reason as the original P12: that branch cannot execute in this drive's environment, so
    # the mutant would be inert. The reachable equivalent is C4b in the collector drive, and
    # the codec-independence of the suite is proven by running it under `--with zstandard`.
    # P12 originally mutated the zstd branch's extension. It survived because that branch is
    # unreachable on this VM — `zstandard` is not installed — so the mutant was INERT, not
    # uncaught. An inert mutant proves nothing about the tests, so it is aimed at the branch
    # that actually executes here: the gzip fallback, mislabelled as zstd.
    ("P12-extension-lies-about-codec",
     "names gzip packs '.jsonl.zst', so the extension misdescribes the bytes",
     '    PACK_EXTENSION = ".jsonl.gz"',
     '    PACK_EXTENSION = ".jsonl.zst"'),
]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B3 mutation drive")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    return run_drive(drive="b3-packer-mutations", target=TARGET, tests=TESTS,
                     mutants=MUTANTS, out=Path(args.out))


if __name__ == "__main__":
    sys.exit(main())
