#!/usr/bin/env python3
"""Cut a smaller map file out of the big one, by keeping every k-th line.

Plain words for the owner
-------------------------
`data/processed/maps.jsonl` is the whole map corpus: one map per line, 26,850 lines, 60 megabytes.
Every line is self-contained, so a smaller corpus is simply a subset of the lines. When the
training job is shipped to the cluster the whole 60 megabytes would have to be uploaded and stored
in Cypress (the cluster's file tree), which is wasteful for a run that will visit each map many
times anyway. `--every 5` keeps map 0, 5, 10, ... -- one fifth of the corpus, about 12 megabytes,
spread evenly over the whole file rather than taken from the front, so the slice is not biased
towards whatever ordering the corpus happens to have.

Use
---
    python3 local_claude_1/nn-bot/cut_maps.py --every 5 --output /tmp/maps-every5.jsonl
    python3 local_claude_1/nn-bot/cut_maps.py --every 1 --output /tmp/maps-full.jsonl   # a copy

`--every 1` keeps everything, which is the honest way to say "the full file" without a second
code path.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: Where the full corpus lives. The worktrees do not each carry a 60 MB copy, so the main
#: checkout is the fallback.
MAIN_CHECKOUT_MAPS = Path("/home/tarstars/prj/troll_farm/data/processed/maps.jsonl")


def default_maps_source() -> Path:
    """The full corpus: this worktree's copy when it has one, the main checkout's otherwise."""

    local = ROOT / "data" / "processed" / "maps.jsonl"
    return local if local.is_file() else MAIN_CHECKOUT_MAPS


def cut_maps(
    source: Path | str,
    destination: Path | str,
    *,
    every: int = 5,
    limit: int | None = None,
) -> dict:
    """Write every `every`-th line of `source` into `destination`.

    Line 0 is always kept, so `--every 1` is a faithful copy. Blank lines (a trailing newline at
    the end of the file, for instance) are skipped and do not consume a slot in the counting, so
    the output never contains an empty record. `limit`, when given, stops after that many kept
    lines.

    Returns a small record: how many lines were read, how many were kept, and the byte size of the
    result -- the numbers the launcher prints in its manifest.
    """

    every = int(every)
    if every < 1:
        raise ValueError("--every must be at least 1")
    source = Path(source)
    destination = Path(destination)
    if not source.is_file():
        raise FileNotFoundError(source)
    destination.parent.mkdir(parents=True, exist_ok=True)

    read = 0
    kept = 0
    with source.open("r", encoding="utf-8") as lines, destination.open(
        "w", encoding="utf-8"
    ) as output:
        for line in lines:
            if not line.strip():
                continue
            index = read
            read += 1
            if index % every:
                continue
            output.write(line if line.endswith("\n") else line + "\n")
            kept += 1
            if limit is not None and kept >= limit:
                break
    return {
        "source": str(source),
        "destination": str(destination),
        "every": every,
        "limit": limit,
        "lines_read": read,
        "lines_kept": kept,
        "source_bytes": source.stat().st_size,
        "destination_bytes": destination.stat().st_size,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=None, help="the full corpus (default: see the module)")
    parser.add_argument("--output", required=True)
    parser.add_argument("--every", type=int, default=5, help="keep one line in every k; 1 = all")
    parser.add_argument("--limit", type=int, default=None, help="stop after this many kept maps")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    source = Path(args.input) if args.input else default_maps_source()
    result = cut_maps(source, Path(args.output), every=args.every, limit=args.limit)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
