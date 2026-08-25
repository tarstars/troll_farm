#!/usr/bin/env python3
"""B3 verification against the real corpus (task `20260811-s3-collector-v2`).

The unit tests use small fixtures. This runs the same packer over every real game body in
this checkout's `data/raw/games/` — real sizes, real unicode nicknames, real platform JSON —
and checks the two claims that matter on the actual data rather than on a fixture:

  round-trip   every game comes back byte-for-byte identical to the file that went in
  determinism  packing the same input twice produces identical pack bytes

Read-only over `data/raw/games/`; writes one JSON evidence record at `--out` and nothing else.
No network, no bucket writes — uploading is B4.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from packer import pack_day, read_manifest, read_pack  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B3 real-corpus verification")
    ap.add_argument("--out", required=True)
    ap.add_argument("--games-dir", default=str(REPO / "data/raw/games"))
    ap.add_argument("--date", default="2026-08-11")
    args = ap.parse_args(argv)

    files = sorted(Path(args.games_dir).glob("*.json"), key=lambda p: int(p.stem))
    originals = {int(p.stem): p.read_bytes() for p in files}

    first = pack_day(args.date, files)
    second = pack_day(args.date, list(reversed(files)))

    records = {r["game_id"]: r for r in read_pack(first.pack_bytes)}
    mismatched = [gid for gid, raw in originals.items()
                  if gid not in records or records[gid]["raw"].encode("utf-8") != raw]
    manifest = read_manifest(first.manifest_text)
    manifest_ids = [row["game_id"] for row in manifest]
    manifest_digests_agree = all(
        row["sha256"] == hashlib.sha256(originals[row["game_id"]]).hexdigest()
        for row in manifest)

    total_raw = sum(len(raw) for raw in originals.values())
    report = {
        "check": "b3-real-corpus-verification",
        "task_id": "20260811-s3-collector-v2",
        "games_dir": str(Path(args.games_dir).relative_to(REPO)),
        "games": len(files),
        "codec": first.codec,
        "pack_key": first.pack_key,
        "manifest_key": first.manifest_key,
        "pack_sha256": first.pack_sha256,
        "pack_bytes": len(first.pack_bytes),
        "raw_bytes": total_raw,
        "compression_ratio": round(len(first.pack_bytes) / total_raw, 4) if total_raw else None,
        "round_trip_byte_identical": not mismatched,
        "round_trip_mismatches": mismatched[:20],
        "deterministic_across_runs": first.pack_bytes == second.pack_bytes,
        "input_order_irrelevant": first.pack_sha256 == second.pack_sha256,
        "manifest_rows": len(manifest),
        "manifest_ids_sorted": manifest_ids == sorted(manifest_ids),
        "manifest_covers_every_game": sorted(manifest_ids) == sorted(originals),
        "manifest_digests_agree": manifest_digests_agree,
        "largest_game_bytes": max(map(len, originals.values())) if originals else 0,
        "non_ascii_games": sum(1 for raw in originals.values()
                               if any(byte > 0x7F for byte in raw)),
    }
    checks = ["round_trip_byte_identical", "deterministic_across_runs",
              "input_order_irrelevant", "manifest_ids_sorted",
              "manifest_covers_every_game", "manifest_digests_agree"]
    failed = [name for name in checks if not report[name]]
    report["failed_checks"] = failed
    report["verdict"] = "B3_VERIFIED" if not failed else "B3_FAILED"

    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: report[k] for k in
                      ("verdict", "games", "codec", "pack_bytes", "raw_bytes",
                       "compression_ratio", "non_ascii_games", "failed_checks")}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
