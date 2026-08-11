#!/usr/bin/env python3
"""Daily packer for collector v2 — task `20260811-s3-collector-v2`, B3.

Packs one day's fetched game files into a single object plus a manifest, in the SAME line
schemas Part A's `data/scripts/pack_games.py` uses for the backfill, so the two populations
can be read by one reader:

  pack      `games/raw/daily/YYYY-MM-DD.jsonl.gz`   line: {"game_id","sha256","size","raw"}
  manifest  `games/manifest/daily-YYYY-MM-DD.jsonl` line: {"game_id","sha256","size","pack"}

Determinism is a property of the bytes, not a hope: ids are sorted numerically, JSON keys are
sorted, `ensure_ascii=False` matches Part A, and the gzip header's mtime is pinned to 0. There
is no timestamp anywhere inside a pack — the date is in the object name, which is the only
place it can live without making identical input produce different bytes.

Compression: `zstandard` is not installed on this VM, so packs are gzip and named `.jsonl.gz`.
The extension is derived from the codec actually used, never hard-coded, because the plan is
explicit that the extension must name the truth.

Re-runs never overwrite: `daily-YYYY-MM-DD.rerun-N` keys are produced by `rerun_key`, matching
the plan's B4 requirement.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path

DAILY_PREFIX = "games/raw/daily"
MANIFEST_PREFIX = "games/manifest"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

try:  # pragma: no cover - absent on this VM; the branch is pinned by a test with a stub
    import zstandard  # noqa: F401

    CODEC = "zstd"
    PACK_EXTENSION = ".jsonl.zst"
except ImportError:
    CODEC = "gzip"
    PACK_EXTENSION = ".jsonl.gz"


@dataclass(frozen=True)
class Pack:
    date: str
    pack_key: str
    manifest_key: str
    pack_bytes: bytes
    manifest_text: str
    game_ids: list[int]
    codec: str

    @property
    def pack_sha256(self) -> str:
        return hashlib.sha256(self.pack_bytes).hexdigest()

    @property
    def manifest_sha256(self) -> str:
        return hashlib.sha256(self.manifest_text.encode()).hexdigest()


def compress(payload: bytes) -> bytes:
    """Deterministic compression. gzip's mtime is pinned so identical input == identical bytes."""
    if CODEC == "gzip":
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb", mtime=0) as handle:
            handle.write(payload)
        return buffer.getvalue()
    import zstandard  # pragma: no cover - not reachable on this VM

    return zstandard.ZstdCompressor(level=10).compress(payload)


def decompress(blob: bytes) -> bytes:
    if CODEC == "gzip":
        return gzip.decompress(blob)
    import zstandard  # pragma: no cover

    return zstandard.ZstdDecompressor().decompress(blob)


def pack_key_for(date: str, rerun: int = 0) -> str:
    if not DATE_RE.match(date):
        raise ValueError(f"date must be YYYY-MM-DD, got {date!r}")
    stem = date if rerun == 0 else f"{date}.rerun-{rerun}"
    return f"{DAILY_PREFIX}/{stem}{PACK_EXTENSION}"


def manifest_key_for(date: str, rerun: int = 0) -> str:
    if not DATE_RE.match(date):
        raise ValueError(f"date must be YYYY-MM-DD, got {date!r}")
    stem = date if rerun == 0 else f"{date}.rerun-{rerun}"
    return f"{MANIFEST_PREFIX}/daily-{stem}.jsonl"


def pack_day(date: str, game_files: list[Path] | list[str], *, rerun: int = 0) -> Pack:
    """Pack the given game files for one date. Input order is irrelevant — ids are sorted.

    Files are read as bytes and embedded verbatim as text, exactly as Part A does: the corpus
    is the platform's own JSON, and re-serialising it here would silently change what we
    archived.
    """
    paths = sorted((Path(p) for p in game_files), key=lambda p: int(p.stem))
    ids = [int(p.stem) for p in paths]
    if len(set(ids)) != len(ids):
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(f"duplicate game ids in input: {duplicates}")

    pack_key = pack_key_for(date, rerun)
    lines: list[bytes] = []
    manifest_lines: list[str] = []
    for path in paths:
        raw = path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        game_id = int(path.stem)
        lines.append(json.dumps(
            {"game_id": game_id, "sha256": digest, "size": len(raw),
             "raw": raw.decode("utf-8")},
            ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n")
        manifest_lines.append(json.dumps(
            {"game_id": game_id, "sha256": digest, "size": len(raw), "pack": pack_key},
            sort_keys=True))

    return Pack(
        date=date,
        pack_key=pack_key,
        manifest_key=manifest_key_for(date, rerun),
        pack_bytes=compress(b"".join(lines)),
        manifest_text=("\n".join(manifest_lines) + "\n") if manifest_lines else "",
        game_ids=ids,
        codec=CODEC,
    )


def read_pack(blob: bytes) -> list[dict]:
    """Inverse of `pack_day`'s pack body, with each embedded game re-verified against its own
    recorded sha256. A pack that decompresses but whose contents do not hash correctly is
    corrupt, and silently returning it would defeat the point of storing the digest."""
    records = []
    for number, line in enumerate(decompress(blob).decode("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = json.loads(line)
        raw = record["raw"].encode("utf-8")
        actual = hashlib.sha256(raw).hexdigest()
        if actual != record["sha256"]:
            raise ValueError(
                f"pack line {number} (game {record.get('game_id')}): sha256 mismatch, "
                f"recorded {record['sha256']}, actual {actual}")
        if len(raw) != record["size"]:
            raise ValueError(
                f"pack line {number} (game {record.get('game_id')}): size mismatch, "
                f"recorded {record['size']}, actual {len(raw)}")
        records.append(record)
    return records


def read_manifest(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="pack one day of games (B3)")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--games-dir", required=True, help="directory of <game_id>.json files")
    ap.add_argument("--out-dir", required=True, help="where to write pack + manifest locally")
    ap.add_argument("--rerun", type=int, default=0)
    args = ap.parse_args(argv)

    files = sorted(Path(args.games_dir).glob("*.json"))
    pack = pack_day(args.date, files, rerun=args.rerun)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / Path(pack.pack_key).name).write_bytes(pack.pack_bytes)
    (out / Path(pack.manifest_key).name).write_text(pack.manifest_text)
    print(json.dumps({
        "date": pack.date, "codec": pack.codec, "games": len(pack.game_ids),
        "pack_key": pack.pack_key, "pack_sha256": pack.pack_sha256,
        "pack_bytes": len(pack.pack_bytes),
        "manifest_key": pack.manifest_key, "manifest_sha256": pack.manifest_sha256,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
