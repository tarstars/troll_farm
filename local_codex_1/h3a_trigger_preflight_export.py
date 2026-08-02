#!/usr/bin/env python3
"""Export the exact open H3a preflight replays as a compact sanitized package."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


CURRENT_AGENT_ID = 6589709
EXPECTED_MEMBERSHIP_SHA256 = (
    "e4e4923446b6449dca35999fc83e6883cdc78b24fa4f2d17b957e394c1068883"
)
CATASTROPHE_IDS = (
    897780891,
    897781216,
    897781413,
    897781719,
    897781840,
    897781987,
    897782076,
    897782213,
    897782302,
    897782366,
)
MATCHED_WIN_IDS = (
    897782128,
    897782246,
    897781650,
    897781674,
    897782379,
    897782201,
    897782068,
)
GAME_IDS = CATASTROPHE_IDS + MATCHED_WIN_IDS
FRAME_FIELDS = (
    "agentId",
    "keyframe",
    "gameInformation",
    "stdout",
    "summary",
    "view",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compact_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def load_membership(path: Path) -> dict[int, dict[str, str]]:
    if sha256_file(path) != EXPECTED_MEMBERSHIP_SHA256:
        raise ValueError(f"membership CSV hash mismatch: {path}")
    wanted = set(GAME_IDS)
    rows: dict[int, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            game_id = int(row["game_id"])
            if game_id not in wanted:
                continue
            if int(row["agent_id"]) != CURRENT_AGENT_ID:
                continue
            if row["current_new_game"] != "1" or row["is_current"] != "1":
                raise ValueError(f"game {game_id} is not a current-new open row")
            if game_id in rows:
                raise ValueError(f"duplicate current-side membership row: {game_id}")
            rows[game_id] = row
    missing = sorted(wanted - rows.keys())
    if missing:
        raise ValueError(f"membership CSV lacks exact game ids: {missing}")
    return rows


def sanitized_agent(agent: dict[str, Any]) -> dict[str, Any]:
    codingamer = agent.get("codingamer") or {}
    return {
        "agent_id": int(agent["agentId"]),
        "arena_score": agent.get("score"),
        "index": int(agent["index"]),
        "name": codingamer.get("pseudo"),
        "valid": bool(agent.get("valid", False)),
    }


def sanitize_game(raw: dict[str, Any], cohort: str) -> dict[str, Any]:
    game_id = int(raw["gameId"])
    agents = [sanitized_agent(agent) for agent in raw["agents"]]
    current = [agent for agent in agents if agent["agent_id"] == CURRENT_AGENT_ID]
    if len(current) != 1:
        raise ValueError(f"game {game_id} has {len(current)} current-agent rows")
    current_seat = current[0]["index"]
    scores = [int(score) for score in raw["scores"]]
    if len(scores) != 2 or current_seat not in (0, 1):
        raise ValueError(f"game {game_id} has unexpected score/seat shape")
    frames = []
    for frame in raw["frames"]:
        frames.append({key: frame[key] for key in FRAME_FIELDS if key in frame})
    if not frames:
        raise ValueError(f"game {game_id} has no frames")
    return {
        "agents": agents,
        "cohort": cohort,
        "current_agent_id": CURRENT_AGENT_ID,
        "current_seat": current_seat,
        "final_margin": scores[current_seat] - scores[1 - current_seat],
        "frames": frames,
        "game_id": game_id,
        "ranks": raw["ranks"],
        "referee_input": raw["refereeInput"],
        "schema_version": 1,
        "scores": scores,
    }


def validate_no_private_presentation_fields(data: bytes) -> None:
    forbidden = (b'"userId"', b'"avatar"', b'"tooltips"')
    found = [token.decode("ascii") for token in forbidden if token in data]
    if found:
        raise ValueError(f"sanitized payload contains forbidden fields: {found}")


def export_package(
    raw_root: Path,
    membership_csv: Path,
    output_prefix: Path,
    created_utc: str,
) -> tuple[Path, Path]:
    membership = load_membership(membership_csv)
    lines: list[bytes] = []
    game_manifest: list[dict[str, Any]] = []
    raw_total_bytes = 0
    category = {game_id: "catastrophe" for game_id in CATASTROPHE_IDS}
    category.update({game_id: "matched_win" for game_id in MATCHED_WIN_IDS})

    for game_id in GAME_IDS:
        raw_path = raw_root / f"{game_id}.json"
        if not raw_path.is_file():
            raise FileNotFoundError(raw_path)
        raw_bytes = raw_path.read_bytes()
        raw_total_bytes += len(raw_bytes)
        raw = json.loads(raw_bytes)
        if int(raw.get("gameId", -1)) != game_id:
            raise ValueError(f"game id mismatch in {raw_path}")
        sanitized = sanitize_game(raw, category[game_id])
        row = membership[game_id]
        csv_margin = int(float(row["margin"]))
        if sanitized["final_margin"] != csv_margin:
            raise ValueError(
                f"game {game_id} margin mismatch: raw={sanitized['final_margin']} "
                f"csv={csv_margin}"
            )
        line = compact_json(sanitized)
        validate_no_private_presentation_fields(line)
        lines.append(line)
        game_manifest.append(
            {
                "agent_ids": [agent["agent_id"] for agent in sanitized["agents"]],
                "cohort": category[game_id],
                "current_seat": sanitized["current_seat"],
                "exported_frames": len(sanitized["frames"]),
                "final_margin": sanitized["final_margin"],
                "game_id": game_id,
                "logical_raw_path": f"data/raw/games/{game_id}.json",
                "raw_bytes": len(raw_bytes),
                "raw_sha256": sha256_bytes(raw_bytes),
                "split": row["split"],
                "turns": int(row["turns"]),
            }
        )

    jsonl = b"\n".join(lines) + b"\n"
    validate_no_private_presentation_fields(jsonl)
    compressed = gzip.compress(jsonl, compresslevel=9, mtime=0)
    games_path = output_prefix.with_suffix(".games.jsonl.gz")
    manifest_path = output_prefix.with_suffix(".manifest.json")
    atomic_write(games_path, compressed)

    manifest = {
        "cohorts": {
            "catastrophe": list(CATASTROPHE_IDS),
            "matched_win": list(MATCHED_WIN_IDS),
        },
        "created_utc": created_utc,
        "current_agent_id": CURRENT_AGENT_ID,
        "exact_ids_only": True,
        "files": {
            games_path.name: {
                "bytes": len(compressed),
                "compression": "gzip; deterministic mtime=0",
                "jsonl_uncompressed_bytes": len(jsonl),
                "rows": len(lines),
                "sha256": sha256_bytes(compressed),
                "uncompressed_sha256": sha256_bytes(jsonl),
            }
        },
        "games": game_manifest,
        "membership_csv": {
            "logical_path": (
                "data/analysis/live-agent-6553250/"
                "top-player-new-games-shared-2026-08-02.sides.csv"
            ),
            "sha256": EXPECTED_MEMBERSHIP_SHA256,
        },
        "omitted_raw_fields": [
            "agents[].codingamer.userId",
            "agents[].codingamer.avatar",
            "metadata",
            "tooltips",
        ],
        "raw_total_bytes": raw_total_bytes,
        "schema": (
            "One JSON object per exact game. Public referee input and ordered frames are "
            "preserved; agent identity is reduced to index, agentId, pseudonym, arena "
            "score, and validity."
        ),
        "schema_version": 1,
        "sealed_data_included": False,
        "source_logical_root": "data/raw/games",
        "task_id": "20260802-h3a-conditioned-value-unblock",
    }
    manifest_bytes = json.dumps(
        manifest,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8") + b"\n"
    atomic_write(manifest_path, manifest_bytes)

    decoded = gzip.decompress(games_path.read_bytes())
    if decoded != jsonl:
        raise ValueError("gzip round-trip mismatch")
    decoded_ids = [json.loads(line)["game_id"] for line in decoded.splitlines()]
    if decoded_ids != list(GAME_IDS):
        raise ValueError("exported JSONL order or membership mismatch")
    return games_path, manifest_path


def self_test() -> None:
    raw = {
        "agents": [
            {
                "agentId": CURRENT_AGENT_ID,
                "codingamer": {"avatar": 7, "pseudo": "tass", "userId": 9},
                "index": 0,
                "score": 23.1,
                "valid": True,
            },
            {
                "agentId": 4,
                "codingamer": {"avatar": 8, "pseudo": "peer", "userId": 10},
                "index": 1,
                "score": 25.0,
                "valid": True,
            },
        ],
        "frames": [{"agentId": 0, "stdout": "WAIT", "tooltips": ["omit"]}],
        "gameId": 1,
        "ranks": [0, 1],
        "refereeInput": "seed",
        "scores": [3, 2],
        "tooltips": ["omit"],
    }
    sanitized = sanitize_game(raw, "synthetic")
    encoded = compact_json(sanitized)
    validate_no_private_presentation_fields(encoded)
    assert sanitized["final_margin"] == 1
    assert sanitized["frames"] == [{"agentId": 0, "stdout": "WAIT"}]
    assert gzip.decompress(gzip.compress(encoded, mtime=0)) == encoded
    print("self-test: ok")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-root", type=Path)
    parser.add_argument("--membership-csv", type=Path)
    parser.add_argument("--output-prefix", type=Path)
    parser.add_argument("--created-utc")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.self_test:
        self_test()
        return
    required = (args.raw_root, args.membership_csv, args.output_prefix, args.created_utc)
    if any(value is None for value in required):
        raise SystemExit(
            "--raw-root, --membership-csv, --output-prefix and --created-utc are required"
        )
    games_path, manifest_path = export_package(
        args.raw_root,
        args.membership_csv,
        args.output_prefix,
        args.created_utc,
    )
    print(games_path)
    print(manifest_path)


if __name__ == "__main__":
    main()
