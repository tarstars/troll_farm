#!/usr/bin/env python3
"""Write a compact integrity manifest for the ignored raw replay corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent
RAW = DATA / "raw"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(generated_on: str) -> dict:
    files = []
    aggregate = hashlib.sha256()
    total_bytes = 0
    for path in sorted((RAW / "games").glob("*.json")):
        size = path.stat().st_size
        digest = sha256_file(path)
        relative = path.relative_to(DATA).as_posix()
        files.append({"path": relative, "bytes": size, "sha256": digest})
        aggregate.update(f"{relative}\0{size}\0{digest}\n".encode())
        total_bytes += size

    metadata = {}
    for name in ("leaderboard.json", "players.json", "fetch_log.json"):
        path = RAW / name
        if path.exists():
            metadata[name] = {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }

    return {
        "schema": 1,
        "generated_on": generated_on,
        "raw_games": {
            "count": len(files),
            "bytes": total_bytes,
            "aggregate_sha256": aggregate.hexdigest(),
            "files": files,
        },
        "metadata": metadata,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DATA / "processed" / "corpus_manifest.json",
    )
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()
    manifest = build_manifest(args.date)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=1) + "\n")
    games = manifest["raw_games"]
    print(
        f"manifested {games['count']} games / {games['bytes']} bytes -> {args.output}"
    )
    print(f"aggregate sha256 {games['aggregate_sha256']}")


if __name__ == "__main__":
    main()
