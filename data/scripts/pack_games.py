#!/usr/bin/env python3
"""Deterministically pack the raw game corpus for S3 backfill (spec Phase 1, plan A3).

Read-only over data/raw/games/. Packs of 1,000 games sorted by numeric id:
  <out>/packs/pack-%06d.jsonl.gz      one line per game:
      {"game_id", "sha256", "size", "raw"}   (raw = the file's exact text)
  <out>/manifests/backfill-%06d.jsonl one line per game:
      {"game_id", "sha256", "size", "pack"}
gzip mtime is pinned to 0 so identical input yields identical pack bytes.
A summary JSON (counts, pack sha256s) is written to <out>/summary.json.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path

CHUNK = 1000


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", default="data/raw/games")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    games_dir = Path(a.games)
    out = Path(a.out)
    (out / "packs").mkdir(parents=True, exist_ok=True)
    (out / "manifests").mkdir(parents=True, exist_ok=True)

    ids = sorted(int(p.stem) for p in games_dir.glob("*.json"))
    packs = []
    for n, start in enumerate(range(0, len(ids), CHUNK)):
        chunk = ids[start:start + CHUNK]
        pack_name = f"pack-{n:06d}.jsonl.gz"
        manifest_lines = []
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
            for gid in chunk:
                raw = (games_dir / f"{gid}.json").read_bytes()
                digest = hashlib.sha256(raw).hexdigest()
                line = json.dumps(
                    {"game_id": gid, "sha256": digest, "size": len(raw),
                     "raw": raw.decode("utf-8")},
                    ensure_ascii=False, sort_keys=True)
                gz.write(line.encode("utf-8") + b"\n")
                manifest_lines.append(json.dumps(
                    {"game_id": gid, "sha256": digest, "size": len(raw),
                     "pack": f"games/raw/backfill/{pack_name}"},
                    sort_keys=True))
        data = buf.getvalue()
        (out / "packs" / pack_name).write_bytes(data)
        (out / "manifests" / f"backfill-{n:06d}.jsonl").write_text(
            "\n".join(manifest_lines) + "\n")
        packs.append({"pack": pack_name, "games": len(chunk),
                      "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest()})
        print(f"{pack_name}: {len(chunk)} games, {len(data):,} bytes")

    summary = {"total_games": len(ids), "packs": packs}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    print(f"TOTAL: {len(ids)} games in {len(packs)} packs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
