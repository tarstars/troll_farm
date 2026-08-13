#!/usr/bin/env python3
"""Export one exact agent/submission replay queue as a sanitized deterministic corpus."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
from typing import Any


FORBIDDEN_KEYS = frozenset(
    {"avatar", "publicHandle", "testSessionHandle", "userId", "user_id"}
)
REPLAY_KEYS = ("gameId", "refereeInput", "scores", "ranks", "tooltips", "frames")


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def assert_private_keys_absent(value: Any) -> None:
    if isinstance(value, dict):
        forbidden = FORBIDDEN_KEYS.intersection(value)
        if forbidden:
            raise ValueError(f"private keys survived sanitization: {sorted(forbidden)}")
        for child in value.values():
            assert_private_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            assert_private_keys_absent(child)


def sanitize_replay(payload: dict[str, Any]) -> dict[str, Any]:
    replay = {key: payload.get(key) for key in REPLAY_KEYS}
    replay["agents"] = [
        {
            "index": int(agent["index"]),
            "agentId": int(agent["agentId"]),
            "score": agent.get("score"),
            "valid": agent.get("valid"),
            "codingamer": {"pseudo": f"PLAYER_{int(agent['index'])}"},
        }
        for agent in sorted(payload.get("agents") or [], key=lambda row: int(row["index"]))
    ]
    assert_private_keys_absent(replay)
    return replay


def sanitize_battle(row: dict[str, Any]) -> dict[str, Any]:
    players = [
        {
            "agent_id": int(player["playerAgentId"]),
            "submission_id": int(player["submissionId"]),
            "position": int(player["position"]),
            "pseudo": f"PLAYER_{int(player['position'])}",
        }
        for player in sorted(row.get("players") or [], key=lambda item: int(item["position"]))
    ]
    battle = {"game_id": int(row["gameId"]), "done": bool(row["done"]), "players": players}
    assert_private_keys_absent(battle)
    return battle


def export_corpus(
    *,
    agent_id: int,
    submission_id: int,
    battle_list: Path,
    raw_root: Path,
    output_dir: Path,
    observed_at_utc: str,
) -> dict[str, Any]:
    rows = json.loads(battle_list.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError("battle list is empty or not a list")

    selected: list[tuple[int, dict[str, Any], dict[str, Any], Path]] = []
    for row in rows:
        if not row.get("done") or not row.get("gameId"):
            continue
        target = [
            player
            for player in row.get("players") or []
            if int(player.get("playerAgentId", -1)) == agent_id
        ]
        if len(target) != 1:
            raise ValueError(f"game {row.get('gameId')} has {len(target)} target players")
        if int(target[0].get("submissionId", -1)) != submission_id:
            raise ValueError(
                f"game {row['gameId']} target submission {target[0].get('submissionId')} "
                f"!= {submission_id}"
            )
        game_id = int(row["gameId"])
        source = raw_root / f"{game_id}.json"
        payload = json.loads(source.read_text(encoding="utf-8"))
        if int(payload.get("gameId", -1)) != game_id:
            raise ValueError(f"game id mismatch in {source}")
        agents = [
            agent
            for agent in payload.get("agents") or []
            if int(agent.get("agentId", -1)) == agent_id
        ]
        if len(agents) != 1:
            raise ValueError(f"game {game_id} replay has {len(agents)} target agents")
        selected.append((game_id, sanitize_battle(row), sanitize_replay(payload), source))

    selected.sort(key=lambda item: item[0])
    game_ids = [item[0] for item in selected]
    if len(game_ids) != len(set(game_ids)):
        raise ValueError("duplicate game ids in battle list")

    output_dir.mkdir(parents=True, exist_ok=True)
    package_name = f"games-agent{agent_id}-submission{submission_id}.jsonl.gz"
    index_name = f"battle-index-agent{agent_id}-submission{submission_id}.json"
    package_path = output_dir / package_name
    index_path = output_dir / index_name

    replay_lines = [canonical(item[2]) + b"\n" for item in selected]
    with package_path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as gz:
            for line in replay_lines:
                gz.write(line)
    index_path.write_bytes(canonical([item[1] for item in selected]) + b"\n")

    games = []
    for (game_id, battle, replay, source), replay_line in zip(selected, replay_lines):
        opponent = next(
            player for player in battle["players"] if player["agent_id"] != agent_id
        )
        target = next(player for player in battle["players"] if player["agent_id"] == agent_id)
        target_index = next(
            agent["index"] for agent in replay["agents"] if agent["agentId"] == agent_id
        )
        games.append(
            {
                "game_id": game_id,
                "source_sha256": digest_file(source),
                "export_line_sha256": digest(replay_line),
                "target_position": target["position"],
                "target_index": target_index,
                "opponent_agent_id": opponent["agent_id"],
                "opponent_submission_id": opponent["submission_id"],
            }
        )

    manifest = {
        "schema": "troll-farm-sanitized-agent-replays-v1",
        "observed_at_utc": observed_at_utc,
        "agent_id": agent_id,
        "submission_id": submission_id,
        "game_count": len(games),
        "game_id_min": min(game_ids),
        "game_id_max": max(game_ids),
        "source_battle_list": str(battle_list),
        "source_battle_list_sha256": digest_file(battle_list),
        "source_raw_root": str(raw_root),
        "source_raw_bytes": sum(item[3].stat().st_size for item in selected),
        "package": package_name,
        "package_bytes": package_path.stat().st_size,
        "package_sha256": digest_file(package_path),
        "battle_index": index_name,
        "battle_index_bytes": index_path.stat().st_size,
        "battle_index_sha256": digest_file(index_path),
        "privacy": {
            "pseudonyms": "replaced with PLAYER_<position>",
            "removed_keys": sorted(FORBIDDEN_KEYS),
            "retained_identifiers": ["game_id", "agent_id", "submission_id"],
            "structural_private_key_scan": "PASS",
        },
        "games": games,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--submission-id", type=int, required=True)
    parser.add_argument("--battle-list", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--observed-at-utc", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = export_corpus(
        agent_id=args.agent_id,
        submission_id=args.submission_id,
        battle_list=args.battle_list,
        raw_root=args.raw_root,
        output_dir=args.output_dir,
        observed_at_utc=args.observed_at_utc,
    )
    print(json.dumps({key: manifest[key] for key in ("game_count", "package_bytes", "package_sha256")}, indent=2))


if __name__ == "__main__":
    main()
