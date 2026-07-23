#!/usr/bin/env python3
"""Combine disjoint generic live-variant study shards and recompute their aggregate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.live_variant_study import aggregate, save


def combine(payloads: list[dict]) -> dict:
    if not payloads:
        raise ValueError("at least one study payload is required")
    sources = payloads[0]["sources"]
    if any(payload["sources"] != sources for payload in payloads[1:]):
        raise ValueError("study shards use different sources")
    rows = [row for payload in payloads for row in payload["rows"]]
    seeds = [row["seed"] for row in rows]
    if len(seeds) != len(set(seeds)):
        raise ValueError("study shards overlap in seed rows")
    rows.sort(key=lambda row: row["seed"])
    return {
        "schema": 1,
        "scope": "combined paired local self-harm check; not an arena predictor",
        "sources": sources,
        "seed_start": min(seeds) if seeds else 0,
        "seeds": len(rows),
        "parts": [
            {"seed_start": payload["seed_start"], "seeds": payload["seeds"]}
            for payload in payloads
        ],
        "aggregate": aggregate(rows),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = combine([json.loads(path.read_text()) for path in args.inputs])
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1))
    print(f"saved {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
