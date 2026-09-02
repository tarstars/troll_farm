#!/usr/bin/env python3
"""Draw the head-to-head panel: N map records with their start inventories, from a corpus, by seed.

Plain words for the owner
-------------------------
The panel is a fixed list of real maps, chosen once by a seeded shuffle and written to a file
whose sha256 goes on the task card BEFORE the first candidate plays on it. Every candidate then
meets the same maps with the same start inventories, so two candidates' results are paired.
The start inventory is drawn as `smoke.py` draws it (2..10 of each fruit and of iron, no wood),
because the corpus records carry the board and the trees but not the inventories of the games
they came from.

The record format is `smoke.py --write-records` (one JSON object a line: `rec`, `draw`,
`profile`), so the bench, the smoke and this panel all read the same file.

Use
---
    python3 claude_1/h2h-panel/make_panel.py --corpus /data/scratch/maps-host-corpus-0901-31088.jsonl \
        --count 200 --seed 1 --out claude_1/h2h-panel/panel-200-seed1.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
#: the pinned corpus (on the laptop; copied to /data/scratch on the VM) and the slice on `main`
PINNED_CORPUS = Path("/home/tarstars/nn-data/maps-host-corpus-0901-31088.jsonl")
SLICE_ON_MAIN = REPO / "local_claude_1" / "nn-bot" / "maps-slice-1000.jsonl"
REQUIRED = ("map_hash", "rows", "shacks", "trees0")


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw_panel(records: list[dict], count: int, seed: int) -> list[dict]:
    """Shuffle with `seed`, keep the first `count` distinct maps, draw the inventories in order."""
    rng = random.Random(seed)
    pool = list(records)
    rng.shuffle(pool)
    seen, chosen = set(), []
    for rec in pool:
        if rec["map_hash"] in seen:
            continue
        seen.add(rec["map_hash"])
        chosen.append(rec)
        if len(chosen) == count:
            break
    if len(chosen) < count:
        raise SystemExit(f"the corpus has only {len(chosen)} distinct maps, {count} asked")
    out = []
    for rec in chosen:
        missing = [k for k in REQUIRED if k not in rec]
        if missing:
            raise SystemExit(f"map {rec.get('map_hash')} lacks {missing}")
        draw = [rng.randint(2, 10) for _ in range(5)] + [0]   # plum lemon apple banana iron wood
        out.append({"rec": rec, "draw": draw, "profile": "h2h"})
    return out


def write_panel(corpus: Path, out: Path, count: int, seed: int) -> dict:
    records = [json.loads(line) for line in corpus.read_text().splitlines() if line.strip()]
    panel = draw_panel(records, count, seed)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as fh:
        for item in panel:
            fh.write(json.dumps(item, separators=(",", ":"), sort_keys=True) + "\n")
    digest = sha_file(out)
    (out.parent / (out.name + ".sha256")).write_text(f"{digest}  {out.name}\n")
    manifest = {
        "corpus": str(corpus), "corpus_sha256": sha_file(corpus), "corpus_maps": len(records),
        "count": count, "seed": seed, "panel": str(out.relative_to(REPO)) if out.is_relative_to(REPO) else str(out),
        "panel_sha256": digest,
        "map_hashes_sha256": hashlib.sha256("\n".join(i["rec"]["map_hash"] for i in panel).encode()).hexdigest(),
        "draw_rule": "smoke.py: [randint(2,10)]*5 + [0] from the same seeded rng after the shuffle",
    }
    (out.parent / (out.stem + ".manifest.json")).write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--corpus", type=Path, default=PINNED_CORPUS if PINNED_CORPUS.exists() else SLICE_ON_MAIN)
    ap.add_argument("--count", type=int, default=200)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", type=Path, default=HERE / "panel-200-seed1.jsonl")
    args = ap.parse_args()
    manifest = write_panel(args.corpus, args.out, args.count, args.seed)
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
