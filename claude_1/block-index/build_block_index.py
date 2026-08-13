#!/usr/bin/env python3
"""Build the code-block index: which block lives in which bot artifact.

Two layers, deliberately separated:

  * curated (`blocks.json`, hand-authored): what a block IS — purpose, class,
    locating anchors, and any measured cost/coverage/live value with citations;
  * derived (this script): WHERE each block is, resolved by matching anchors
    against every bot source, so presence can never drift out of date. Rebuild
    it instead of editing it.

Presence is reported as present / absent / partial. `partial` is the useful
signal: it marks an artifact where a block was half-removed or is mid-migration,
which is exactly what a re-assembly experiment needs to know before combining
sources.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def resolve(text: str, anchors: list[str]) -> tuple[str, dict[str, int]]:
    counts = {a: text.count(a) for a in anchors}
    hits = sum(1 for c in counts.values() if c)
    if hits == 0:
        return "absent", counts
    if hits == len(anchors):
        return "present", counts
    return "partial", counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--definitions", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True,
                        help="repository root to scan for bot sources")
    parser.add_argument("--glob", action="append", required=True,
                        help="repo-relative glob of bot sources; repeatable")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    args = parser.parse_args()

    definitions = json.loads(args.definitions.read_text())
    blocks = definitions["blocks"]

    sources = []
    for pattern in args.glob:
        sources.extend(sorted(args.root.glob(pattern)))
    sources = sorted({s for s in sources if s.is_file()})

    artifacts, matrix = {}, {}
    for path in sources:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        key = str(path.relative_to(args.root))
        artifacts[key] = {"bytes": len(raw), "sha256": digest(raw)}
        matrix[key] = {}
        for block in blocks:
            state, counts = resolve(text, block["anchors"])
            matrix[key][block["id"]] = {"state": state, "anchor_counts": counts}

    index = {
        "schema": "troll-farm-block-index-v1",
        "artifacts_scanned": len(artifacts),
        "blocks_defined": len(blocks),
        "artifacts": artifacts,
        "presence": matrix,
    }
    args.index.parent.mkdir(parents=True, exist_ok=True)
    args.index.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Code block index (generated — do not edit)",
        "",
        f"Generated from `{args.definitions.name}` over {len(artifacts)} bot sources. "
        "Rebuild with `build_block_index.py`; the curated layer is `blocks.json`.",
        "",
        "## Blocks",
        "",
        "| Block | Class | Present in | Partial | Measured cost | Live value |",
        "|---|---|---:|---:|---|---|",
    ]
    for block in blocks:
        present = sum(1 for a in matrix if matrix[a][block["id"]]["state"] == "present")
        partial = sum(1 for a in matrix if matrix[a][block["id"]]["state"] == "partial")
        measured = block.get("measured", {})
        cost = (f'{measured["source_cost_bytes"]:,} B'
                if "source_cost_bytes" in measured else "—")
        value = measured.get("live_value", "—")
        lines.append(
            f'| **{block["title"]}** (`{block["id"]}`) | {block["class"]} | '
            f'{present} | {partial} | {cost} | {value} |'
        )
    lines += ["", "## What each block does", ""]
    for block in blocks:
        lines += [f'### {block["title"]} — `{block["id"]}`', "",
                  block["purpose"], "",
                  f'- class: {block["class"]}',
                  f'- anchors: {", ".join("`" + a + "`" for a in block["anchors"])}']
        measured = block.get("measured", {})
        for field in ("source_cost_bytes", "source_cost_percent", "activation_rate",
                      "coverage", "live_value", "note"):
            if field in measured:
                lines.append(f"- {field.replace('_', ' ')}: {measured[field]}")
        for citation in measured.get("evidence", []):
            lines.append(f"- evidence: `{citation}`")
        lines.append("")
    args.markdown.write_text("\n".join(lines) + "\n")

    print(json.dumps({
        "artifacts_scanned": len(artifacts),
        "blocks": len(blocks),
        "index": str(args.index),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
