#!/usr/bin/env python3
"""Collect and analyze public recent battles for the current Troll Farm top 15.

The collector is read-only: it calls only leaderboard, last-battle-list, and game-result
services.  It never submits code or starts a TestSession game.  Raw replay responses are
processed in memory; checked-in outputs contain only sanitized identifiers and compact
derived measurements.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto import battle_taxonomy as arena  # noqa: E402


DEFAULT_INVENTORY = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "top15-public-battle-inventory-2026-08-02.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250"
    / "top15-public-battle-audit-2026-08-02.json"
)
TOP_N = 15


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=False)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def leaderboard_top15() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = arena.call(
        "Leaderboards/getFilteredPuzzleLeaderboard",
        [
            arena.PID,
            arena.TSH,
            "global",
            {"active": False, "column": "", "filter": ""},
        ],
    )
    users = sorted(
        payload.get("users") or [],
        key=lambda row: int(row.get("rank") or 10**9),
    )
    rows = []
    for user in users[:TOP_N]:
        league = user.get("league") or {}
        rows.append(
            {
                "rank": int(user.get("rank")),
                "league_local_rank": int(user.get("localRank") or user.get("rank")),
                "score": float(user.get("score")),
                "agent_id": int(user.get("agentId")),
                "pseudo": str(user.get("pseudo")),
                "language": user.get("programmingLanguage"),
                "league_division": league.get("divisionIndex"),
                "creation_time": user.get("creationTime"),
                "update_time": user.get("updateTime"),
            }
        )
    if len(rows) != TOP_N or len({row["agent_id"] for row in rows}) != TOP_N:
        raise ValueError(f"expected {TOP_N} unique top identities, got {len(rows)}")
    if [row["rank"] for row in rows] != list(range(1, TOP_N + 1)):
        raise ValueError("global leaderboard ranks 1..15 are not contiguous")
    return rows, {
        "ranked_users": int(payload.get("count") or len(users)),
        "filtered_users": int(payload.get("filteredCount") or len(users)),
        "response_sha256": digest(payload),
    }


def sanitize_battle(battle: dict[str, Any], listed_agent_id: int) -> dict[str, Any]:
    players = []
    for player in battle.get("players") or []:
        players.append(
            {
                "agent_id": int(player.get("playerAgentId") or -1),
                "submission_id": (
                    int(player["submissionId"])
                    if player.get("submissionId") is not None
                    else None
                ),
                "position": int(player.get("position") or 0),
                "pseudo": player.get("nickname"),
            }
        )
    game_id = int(battle.get("gameId") or 0)
    if not game_id:
        raise ValueError("battle row lacks gameId")
    if not any(player["agent_id"] == listed_agent_id for player in players):
        raise ValueError(
            f"game {game_id} list for {listed_agent_id} does not contain that agent"
        )
    return {
        "game_id": game_id,
        "done": bool(battle.get("done")),
        "players": sorted(players, key=lambda row: row["position"]),
    }


def collect_inventory(jobs: int) -> dict[str, Any]:
    top, leaderboard = leaderboard_top15()

    def list_one(row: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
        agent_id = int(row["agent_id"])
        battles = arena.call(
            "gamesPlayersRanking/findLastBattlesByAgentId", [agent_id, None]
        )
        sanitized = [sanitize_battle(battle, agent_id) for battle in battles]
        return agent_id, sanitized

    with ThreadPoolExecutor(max_workers=min(jobs, TOP_N)) as executor:
        listed = dict(executor.map(list_one, top))

    unique: dict[int, dict[str, Any]] = {}
    agents = []
    for row in top:
        agent_id = int(row["agent_id"])
        battles = listed[agent_id]
        done = [battle for battle in battles if battle["done"]]
        for battle in done:
            game_id = int(battle["game_id"])
            prior = unique.get(game_id)
            if prior is not None and prior != battle:
                raise ValueError(f"inconsistent duplicate metadata for game {game_id}")
            unique[game_id] = battle
        submissions = {}
        for battle in done:
            player = next(
                player
                for player in battle["players"]
                if player["agent_id"] == agent_id
            )
            key = str(player["submission_id"])
            submissions[key] = submissions.get(key, 0) + 1
        agents.append(
            {
                **row,
                "listed": len(battles),
                "finished": len(done),
                "submission_id_counts": dict(sorted(submissions.items())),
                "game_ids": [battle["game_id"] for battle in done],
            }
        )
    compact_games = [unique[game_id] for game_id in sorted(unique)]
    return {
        "schema": "troll-farm-top15-public-battle-inventory-v1",
        "task_id": "20260802-top15-public-battle-audit",
        "generated_at_utc": utc_now(),
        "scope": (
            "public current top-15 leaderboard and every finished row returned by each "
            "exact agent's recent-battle endpoint"
        ),
        "read_only_services": [
            "Leaderboards/getFilteredPuzzleLeaderboard",
            "gamesPlayersRanking/findLastBattlesByAgentId",
        ],
        "leaderboard": leaderboard,
        "agents": agents,
        "counts": {
            "top_agents": len(agents),
            "listed_finished_occurrences": sum(row["finished"] for row in agents),
            "unique_finished_games": len(compact_games),
            "duplicate_occurrences": sum(row["finished"] for row in agents)
            - len(compact_games),
        },
        "games": compact_games,
    }


def validate_inventory(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "troll-farm-top15-public-battle-inventory-v1":
        raise ValueError("unrecognized inventory schema")
    agents = payload.get("agents") or []
    if len(agents) != TOP_N or len({row["agent_id"] for row in agents}) != TOP_N:
        raise ValueError("inventory does not contain 15 unique agents")
    game_ids = [int(row["game_id"]) for row in payload.get("games") or []]
    if game_ids != sorted(set(game_ids)):
        raise ValueError("inventory game ids are not sorted and unique")
    if len(game_ids) != int(payload["counts"]["unique_finished_games"]):
        raise ValueError("inventory unique-game count mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--jobs", type=int, default=12)
    parser.add_argument(
        "--inventory-only",
        action="store_true",
        help="capture leaderboard and battle-list metadata without fetching replays",
    )
    parser.add_argument(
        "--validate-inventory",
        action="store_true",
        help="validate an existing inventory without network access",
    )
    args = parser.parse_args()
    if not 1 <= args.jobs <= 24:
        raise SystemExit("--jobs must be between 1 and 24")
    if args.validate_inventory:
        payload = json.loads(args.inventory.read_text())
        validate_inventory(payload)
        print(json.dumps({"inventory": str(args.inventory), "status": "ok"}))
        return 0
    inventory = collect_inventory(args.jobs)
    validate_inventory(inventory)
    atomic_json(args.inventory, inventory)
    print(
        json.dumps(
            {
                "inventory": str(args.inventory),
                "leaderboard_sha256": inventory["leaderboard"]["response_sha256"],
                **inventory["counts"],
            },
            sort_keys=True,
        )
    )
    if args.inventory_only:
        return 0
    raise SystemExit(
        "full replay analysis is not yet implemented; use --inventory-only for phase 1"
    )


if __name__ == "__main__":
    raise SystemExit(main())
