#!/usr/bin/env python3
"""Fetch one exact CodinGame agent/submission replay set outside collector-owned roots."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


BASE = "https://www.codingame.com/services"
TIMEOUT_SECONDS = 20
SLEEP_SECONDS = 0.35
MAX_ATTEMPTS = 3


def post(service: str, body: object) -> object:
    request = urllib.request.Request(
        f"{BASE}/{service}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def post_with_retry(service: str, body: object) -> object:
    error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return post(service, body)
        except (OSError, ValueError, urllib.error.URLError) as caught:
            error = caught
            if attempt != MAX_ATTEMPTS:
                time.sleep(attempt)
    raise RuntimeError(f"{service} failed after {MAX_ATTEMPTS} attempts: {error}")


def target_battles(
    rows: object, *, agent_id: int, submission_id: int, expected_count: int
) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError("battle response is not a list")
    selected: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or not row.get("done") or not row.get("gameId"):
            continue
        targets = [
            player
            for player in row.get("players") or []
            if int(player.get("playerAgentId", -1)) == agent_id
        ]
        if len(targets) != 1:
            raise ValueError(f"game {row.get('gameId')} has {len(targets)} target rows")
        if int(targets[0].get("submissionId", -1)) != submission_id:
            raise ValueError(
                f"game {row['gameId']} has target submission "
                f"{targets[0].get('submissionId')} != {submission_id}"
            )
        selected.append(row)
    if len(selected) != expected_count:
        raise ValueError(f"expected {expected_count} finished games, found {len(selected)}")
    game_ids = [int(row["gameId"]) for row in selected]
    if len(game_ids) != len(set(game_ids)):
        raise ValueError("battle response contains duplicate game IDs")
    return sorted(selected, key=lambda row: int(row["gameId"]))


def validate_replay(payload: object, *, game_id: int, agent_id: int) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"game {game_id} replay is not an object")
    if int(payload.get("gameId", -1)) != game_id:
        raise ValueError(f"game {game_id} replay ID mismatch")
    targets = [
        agent
        for agent in payload.get("agents") or []
        if int(agent.get("agentId", -1)) == agent_id
    ]
    if len(targets) != 1:
        raise ValueError(f"game {game_id} replay has {len(targets)} target agents")
    frames = payload.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError(f"game {game_id} replay has no frames")
    return payload


def write_json_atomic(path: Path, value: object) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    temporary.replace(path)


def fetch(
    *, agent_id: int, submission_id: int, expected_count: int, output_root: Path
) -> dict[str, int]:
    output_root.mkdir(parents=True, exist_ok=True)
    games_root = output_root / "games"
    games_root.mkdir(parents=True, exist_ok=True)

    rows = post_with_retry("gamesPlayersRanking/findLastBattlesByAgentId", [agent_id, None])
    battles = target_battles(
        rows,
        agent_id=agent_id,
        submission_id=submission_id,
        expected_count=expected_count,
    )
    battle_path = output_root / f"battles-agent{agent_id}-submission{submission_id}.json"
    write_json_atomic(battle_path, battles)

    fetched = skipped = 0
    for offset, row in enumerate(battles, start=1):
        game_id = int(row["gameId"])
        destination = games_root / f"{game_id}.json"
        if destination.exists():
            existing = json.loads(destination.read_text(encoding="utf-8"))
            validate_replay(existing, game_id=game_id, agent_id=agent_id)
            skipped += 1
        else:
            time.sleep(SLEEP_SECONDS)
            payload = post_with_retry("gameResult/findByGameId", [game_id, None])
            write_json_atomic(
                destination,
                validate_replay(payload, game_id=game_id, agent_id=agent_id),
            )
            fetched += 1
        if offset % 20 == 0 or offset == len(battles):
            print(
                f"progress {offset}/{len(battles)} fetched={fetched} skipped={skipped}",
                flush=True,
            )

    files = list(games_root.glob("*.json"))
    if len(files) != expected_count:
        raise ValueError(
            f"expected exactly {expected_count} replay files in scoped root, found {len(files)}"
        )
    return {"games": len(battles), "fetched": fetched, "skipped": skipped}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-id", type=int, required=True)
    parser.add_argument("--submission-id", type=int, required=True)
    parser.add_argument("--expected-count", type=int, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = fetch(
        agent_id=args.agent_id,
        submission_id=args.submission_id,
        expected_count=args.expected_count,
        output_root=args.output_root,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
