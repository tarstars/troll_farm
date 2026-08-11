"""Tests for the B3 daily packer (task `20260811-s3-collector-v2`).

Two properties carry the weight:

  ROUND-TRIP  — what comes out of a pack is byte-identical to the file that went in. The
                corpus is irreplaceable (B1 measured that already-collected games stop
                resolving), so a lossy packer is an unrecoverable error, not a bug to fix
                later.
  DETERMINISM — identical input produces identical pack bytes. Without it, the append-only
                layout cannot distinguish "the same day re-packed" from "a different day's
                data", and no digest comparison means anything.

Determinism is tested against the real failure mode: gzip stamps the current time into its
header, so the same games packed a second later would differ.
`test_compressed_bytes_carry_no_timestamp` pins the fix at the byte level rather than trusting
the round-trip to notice.

Every codec-dependent value comes from `packer` (`CODEC`, `PACK_EXTENSION`, `CONTENT_TYPE`,
`MAGIC`) rather than being written as gzip. Hard-coding gzip is what made seven tests fail the
moment `zstandard` was installed — raised by codex_1 and fixed here — so the suite is run in
both environments:

Run: `uvx pytest claude_1/collector-v2/tests -q` and, to prove codec independence,
`uvx --with zstandard pytest claude_1/collector-v2/tests -q`.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import packer  # noqa: E402
from packer import (  # noqa: E402
    manifest_key_for,
    pack_day,
    pack_key_for,
    read_manifest,
    read_pack,
)

DATE = "2026-08-11"


def write_games(directory: Path, bodies: dict[int, str]) -> list[Path]:
    paths = []
    for game_id, body in bodies.items():
        path = directory / f"{game_id}.json"
        path.write_text(body, encoding="utf-8")
        paths.append(path)
    return paths


@pytest.fixture
def games(tmp_path) -> list[Path]:
    return write_games(tmp_path, {
        898550181: json.dumps({"gameId": 898550181, "frames": [{"a": 1}]}),
        898096416: json.dumps({"gameId": 898096416, "agents": [{"pseudo": "tass"}]}),
        # non-ASCII must survive verbatim: the platform returns unicode nicknames
        898058061: json.dumps({"gameId": 898058061, "pseudo": "тролль"}, ensure_ascii=False),
    })


def test_round_trip_is_byte_identical(games):
    pack = pack_day(DATE, games)
    records = {record["game_id"]: record for record in read_pack(pack.pack_bytes)}
    assert len(records) == len(games)
    for path in games:
        original = path.read_bytes()
        record = records[int(path.stem)]
        assert record["raw"].encode("utf-8") == original
        assert record["sha256"] == hashlib.sha256(original).hexdigest()
        assert record["size"] == len(original)


def test_pack_is_deterministic(games, tmp_path):
    first = pack_day(DATE, games)
    # re-read from different path objects and a shuffled order: neither may matter
    shuffled = list(reversed([Path(str(p)) for p in games]))
    second = pack_day(DATE, shuffled)
    assert first.pack_bytes == second.pack_bytes
    assert first.pack_sha256 == second.pack_sha256
    assert first.manifest_text == second.manifest_text


def test_compressed_bytes_carry_no_timestamp(games):
    """The concrete determinism hazard, checked per codec rather than assuming gzip.

    gzip stamps the current time into bytes 4-8 of its header, which is why `mtime=0` is
    pinned. zstd has no such field. Written this way because assuming gzip is what broke
    seven tests the moment `zstandard` was installed.
    """
    pack = pack_day(DATE, games)
    assert pack.pack_bytes[:len(packer.MAGIC)] == packer.MAGIC
    if packer.CODEC == "gzip":
        assert pack.pack_bytes[4:8] == b"\x00\x00\x00\x00", "gzip mtime must be pinned to 0"


def test_no_timestamp_inside_the_pack(games):
    """The date belongs in the object name, not the payload."""
    body = packer.decompress(pack_day(DATE, games).pack_bytes).decode("utf-8")
    for record in (json.loads(line) for line in body.splitlines()):
        assert set(record) == {"game_id", "sha256", "size", "raw"}


def test_manifest_matches_part_a_line_schema(games):
    """Backfill and daily manifests must be readable by one reader.

    Part A (`data/scripts/pack_games.py`) writes exactly these four keys per line.
    """
    pack = pack_day(DATE, games)
    rows = read_manifest(pack.manifest_text)
    assert len(rows) == len(games)
    for row in rows:
        assert set(row) == {"game_id", "sha256", "size", "pack"}
        assert row["pack"] == pack.pack_key
    assert [row["game_id"] for row in rows] == sorted(int(p.stem) for p in games)


def test_pack_line_is_byte_identical_to_part_a_encoding(tmp_path):
    """Pins the pack line's exact bytes, not just its parsed content.

    Round-trip and determinism both survive a change of key order or of `ensure_ascii`, so
    neither notices divergence from Part A's encoding — the P3 and P4 mutants proved that by
    surviving. Part A (`data/scripts/pack_games.py`) writes each line as
    `json.dumps(..., ensure_ascii=False, sort_keys=True)`, so the keys come out in sorted
    order (game_id, raw, sha256, size) and non-ASCII stays literal.
    """
    body = '{"gameId": 1, "pseudo": "тролль"}'
    (tmp_path / "42.json").write_text(body, encoding="utf-8")
    raw = body.encode("utf-8")

    pack = pack_day(DATE, [tmp_path / "42.json"])
    line = packer.decompress(pack.pack_bytes).decode("utf-8").rstrip("\n")

    expected = json.dumps(
        {"game_id": 42, "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw),
         "raw": body},
        ensure_ascii=False, sort_keys=True)
    assert line == expected
    assert list(json.loads(line)) == ["game_id", "raw", "sha256", "size"], "keys not sorted"
    assert "тролль" in line, "non-ASCII must stay literal, as Part A writes it"
    assert "\\u0442" not in line


def test_manifest_digests_agree_with_pack(games):
    pack = pack_day(DATE, games)
    packed = {record["game_id"]: record["sha256"] for record in read_pack(pack.pack_bytes)}
    for row in read_manifest(pack.manifest_text):
        assert packed[row["game_id"]] == row["sha256"]


def test_ids_are_sorted_numerically_not_lexically(tmp_path):
    """'1000' sorts before '999' as text; game ids are numbers."""
    files = write_games(tmp_path, {999: "{}", 1000: "{}", 98: "{}"})
    pack = pack_day(DATE, files)
    assert pack.game_ids == [98, 999, 1000]
    assert [row["game_id"] for row in read_manifest(pack.manifest_text)] == [98, 999, 1000]


def test_keys_follow_the_plan_layout():
    assert pack_key_for(DATE) == f"games/raw/daily/{DATE}{packer.PACK_EXTENSION}"
    assert manifest_key_for(DATE) == f"games/manifest/daily-{DATE}.jsonl"


def test_rerun_keys_never_collide_with_the_first_run():
    first_pack, first_manifest = pack_key_for(DATE), manifest_key_for(DATE)
    keys = {first_pack, first_manifest}
    for rerun in (1, 2, 3):
        pack, manifest = pack_key_for(DATE, rerun), manifest_key_for(DATE, rerun)
        assert pack not in keys and manifest not in keys
        assert f"rerun-{rerun}" in pack and f"rerun-{rerun}" in manifest
        keys.update({pack, manifest})


def test_extension_names_the_actual_codec():
    """The plan is explicit that the extension must match the content, so it is derived."""
    assert packer.CODEC in {"gzip", "zstd"}
    expected = ".jsonl.gz" if packer.CODEC == "gzip" else ".jsonl.zst"
    assert packer.PACK_EXTENSION == expected
    assert pack_key_for(DATE).endswith(expected)
    assert pack_day(DATE, []).pack_bytes[:len(packer.MAGIC)] == packer.MAGIC
    assert packer.CONTENT_TYPE == (
        "application/gzip" if packer.CODEC == "gzip" else "application/zstd")


def test_bad_date_is_refused():
    for bad in ["2026-8-11", "20260811", "2026-08-11T00:00:00Z", "yesterday", ""]:
        with pytest.raises(ValueError):
            pack_key_for(bad)
        with pytest.raises(ValueError):
            manifest_key_for(bad)


def test_duplicate_game_ids_are_refused(tmp_path):
    """Two directories can both hold 898550181.json; packing both would double-count it."""
    one = tmp_path / "a"
    two = tmp_path / "b"
    one.mkdir()
    two.mkdir()
    files = write_games(one, {898550181: "{}"}) + write_games(two, {898550181: "{}"})
    with pytest.raises(ValueError, match="duplicate"):
        pack_day(DATE, files)


def test_corrupt_pack_is_detected_not_returned(games):
    """A pack whose recorded digest disagrees with its own payload must raise."""
    pack = pack_day(DATE, games)
    body = packer.decompress(pack.pack_bytes).decode("utf-8").splitlines()
    tampered = json.loads(body[0])
    tampered["raw"] = tampered["raw"].replace("1", "2", 1)
    body[0] = json.dumps(tampered, ensure_ascii=False, sort_keys=True)
    blob = packer.compress(("\n".join(body) + "\n").encode("utf-8"))
    with pytest.raises(ValueError, match="sha256 mismatch"):
        read_pack(blob)


def test_empty_day_produces_an_empty_pack_not_a_crash(tmp_path):
    """A day with no games is normal (platform quiet, collector run early); it must not raise."""
    pack = pack_day(DATE, [])
    assert pack.game_ids == []
    assert pack.manifest_text == ""
    assert read_pack(pack.pack_bytes) == []
