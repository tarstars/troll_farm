#!/usr/bin/env python3
"""Collect an immutable D61p public-platform replay snapshot.

This entry point never writes the mutable ``raw/leaderboard.json``, ``players.json``,
``fetch_log.json``, or ``raw/battles/*.json`` manifests. It writes acquisition metadata below a
new ``raw/snapshots/<snapshot-id>/`` directory and adds only previously absent replay bodies to the
shared immutable ``raw/games/<gameId>.json`` cache.

Network execution is intentionally separate from TestSession, Arena comparison, and submission.
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import hashlib
import json
import os
import re
import tempfile
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol


BASE = "https://www.codingame.com/services"
PUZZLE = "spring-challenge-2026-troll-farm"
DATA = Path(__file__).resolve().parent.parent
DEFAULT_RAW = DATA / "raw"
DEFAULT_RESIDENT_AGENT_ID = 6_561_795
TOP_LEGEND = 20
RECENT_PER_LEGEND = 10
MIN_REQUEST_INTERVAL_SECONDS = 0.35
REQUEST_TIMEOUT_SECONDS = 20
SNAPSHOT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def default_snapshot_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ-d61p")


@dataclasses.dataclass(frozen=True)
class ApiResponse:
    payload: object
    raw: bytes
    response_sha256: str

    @classmethod
    def from_payload(cls, payload: object) -> "ApiResponse":
        raw = canonical_json_bytes(payload)
        return cls(payload=payload, raw=raw, response_sha256=sha256_bytes(raw))


class Client(Protocol):
    def post(self, service: str, body: object) -> ApiResponse: ...


class PublicClient:
    """Rate-limited, unauthenticated CodinGame JSON service client."""

    def __init__(
        self,
        *,
        request_interval: float = MIN_REQUEST_INTERVAL_SECONDS,
        timeout: int = REQUEST_TIMEOUT_SECONDS,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
        urlopen: Callable[..., Any] = urllib.request.urlopen,
    ) -> None:
        if request_interval < MIN_REQUEST_INTERVAL_SECONDS:
            raise ValueError(
                f"request interval must be at least {MIN_REQUEST_INTERVAL_SECONDS} seconds"
            )
        if timeout < REQUEST_TIMEOUT_SECONDS:
            raise ValueError(f"timeout must be at least {REQUEST_TIMEOUT_SECONDS} seconds")
        self.request_interval = float(request_interval)
        self.timeout = int(timeout)
        self._monotonic = monotonic
        self._sleep = sleep
        self._urlopen = urlopen
        self._last_request_at: float | None = None

    def _pace(self) -> None:
        now = self._monotonic()
        if self._last_request_at is not None:
            remaining = self.request_interval - (now - self._last_request_at)
            if remaining > 0:
                self._sleep(remaining)
                now = self._monotonic()
        self._last_request_at = now

    def post(self, service: str, body: object) -> ApiResponse:
        request_body = canonical_json_bytes(body)
        request = urllib.request.Request(
            f"{BASE}/{service}",
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        self._pace()
        with self._urlopen(request, timeout=self.timeout) as response:
            raw = response.read()
        payload = json.loads(raw.decode())
        return ApiResponse(
            payload=payload,
            raw=raw,
            response_sha256=sha256_bytes(raw),
        )


def league_index(user: dict) -> int | None:
    return (user.get("league") or {}).get("divisionIndex")


def source_rank(user: dict) -> int | None:
    value = user.get("localRank")
    if value is None:
        value = user.get("rank")
    return int(value) if value is not None else None


def select_players(
    users: list[dict], resident_agent_id: int = DEFAULT_RESIDENT_AGENT_ID
) -> list[dict]:
    """Select the resident and first twenty Legend rows without outcome conditioning."""

    legends = [user for user in users if league_index(user) == 5][:TOP_LEGEND]
    by_agent: dict[int, dict] = {}

    def add(user: dict, group: str, legend_order: int | None = None) -> None:
        agent_id = int(user["agentId"])
        row = by_agent.setdefault(
            agent_id,
            {
                "agent_id": agent_id,
                "pseudo": user.get("pseudo", f"agent-{agent_id}"),
                "user_id": (user.get("codingamer") or {}).get("userId"),
                "league_index": league_index(user),
                "global_rank": user.get("rank"),
                "local_rank": user.get("localRank"),
                "source_rank": source_rank(user),
                "score": user.get("score"),
                "groups": [],
                "legend_order": legend_order,
            },
        )
        if group not in row["groups"]:
            row["groups"].append(group)
        if legend_order is not None:
            row["legend_order"] = legend_order

    for order, user in enumerate(legends, start=1):
        add(user, "legend_top20", order)

    resident = next(
        (user for user in users if int(user.get("agentId", -1)) == resident_agent_id),
        None,
    )
    if resident is None:
        resident = {
            "agentId": resident_agent_id,
            "pseudo": f"agent-{resident_agent_id}",
            "codingamer": {},
            "league": {},
        }
    add(resident, "resident")

    # Stable request order: resident first, then leaderboard Legend order.
    return sorted(
        by_agent.values(),
        key=lambda row: (
            0 if "resident" in row["groups"] else 1,
            row["legend_order"] if row["legend_order"] is not None else 10**9,
            row["agent_id"],
        ),
    )


def battle_has_visible_boss(battle: dict) -> bool:
    for key, value in battle.items():
        if "boss" in str(key).lower() and bool(value):
            return True
    for player in battle.get("players") or []:
        if player.get("isBoss") or player.get("boss"):
            return True
        names = (
            player.get("nickname"),
            player.get("pseudo"),
            player.get("name"),
        )
        if any("boss" in str(name).lower() for name in names if name is not None):
            return True
    return False


def completed_battles(rows: object) -> list[dict]:
    if not isinstance(rows, list):
        raise ValueError("battle-list response is not a list")
    done = [row for row in rows if row.get("done") and row.get("gameId") is not None]
    return sorted(done, key=lambda row: -int(row["gameId"]))


def replay_shape(payload: object) -> tuple[bool, int | None, str | None]:
    if not isinstance(payload, dict):
        return False, None, "replay response is not an object"
    frames = payload.get("frames")
    if not isinstance(frames, list) or not frames:
        return False, None, "replay response has no nonempty frames list"
    return True, len(frames), None


def write_new_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        target.write(content)


def write_new_json(path: Path, value: object) -> None:
    content = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    write_new_bytes(path, content)


def write_final_manifest(path: Path, value: object) -> None:
    """Atomically publish a manifest without permitting replacement."""

    if path.exists():
        raise FileExistsError(path)
    content = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    temporary = path.with_name(f".{path.name}.tmp")
    write_new_bytes(temporary, content)
    if path.exists():
        temporary.unlink(missing_ok=True)
        raise FileExistsError(path)
    os.link(temporary, path)
    temporary.unlink()


def store_cache_immutable(path: Path, content: bytes) -> bool:
    """Atomically create a replay cache file; return False if another body already exists."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as target:
            target.write(content)
            target.flush()
            os.fsync(target.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            return False
        return True
    finally:
        temporary.unlink(missing_ok=True)


def collect_snapshot(
    *,
    raw_root: Path = DEFAULT_RAW,
    snapshot_id: str | None = None,
    resident_agent_id: int = DEFAULT_RESIDENT_AGENT_ID,
    client: Client | None = None,
    timestamp: Callable[[], str] = utc_now,
) -> Path:
    snapshot_id = snapshot_id or default_snapshot_id()
    if not SNAPSHOT_RE.fullmatch(snapshot_id):
        raise ValueError(f"unsafe snapshot id: {snapshot_id!r}")
    raw_root = Path(raw_root)
    snapshot = raw_root / "snapshots" / snapshot_id
    snapshot.mkdir(parents=True, exist_ok=False)
    (snapshot / "battles").mkdir()
    games_cache = raw_root / "games"
    games_cache.mkdir(parents=True, exist_ok=True)
    client = client or PublicClient()

    request_log: list[dict] = []
    failures: list[dict] = []

    def request(service: str, body: object, context: dict) -> ApiResponse:
        requested_at = timestamp()
        request_sha256 = sha256_bytes(canonical_json_bytes(body))
        try:
            response = client.post(service, body)
        except Exception as error:  # noqa: BLE001 - acquisition must preserve failures
            request_log.append(
                {
                    "service": service,
                    "request_body_sha256": request_sha256,
                    "response_sha256": None,
                    "requested_at_utc": requested_at,
                    "status": "failed",
                    "context": context,
                    "error": str(error)[:500],
                }
            )
            raise
        request_log.append(
            {
                "service": service,
                "request_body_sha256": request_sha256,
                "response_sha256": response.response_sha256,
                "requested_at_utc": requested_at,
                "status": "ok",
                "context": context,
            }
        )
        return response

    leaderboard_service = "Leaderboards/getFilteredPuzzleLeaderboard"
    leaderboard_body = [
        PUZZLE,
        None,
        "global",
        {"active": False, "column": "", "filter": ""},
    ]
    leaderboard = request(leaderboard_service, leaderboard_body, {"stage": "leaderboard"})
    if not isinstance(leaderboard.payload, dict) or not isinstance(
        leaderboard.payload.get("users"), list
    ):
        raise ValueError("leaderboard response has no users list")
    write_new_bytes(snapshot / "leaderboard.json", leaderboard.raw)
    users = leaderboard.payload["users"]
    players = select_players(users, resident_agent_id)
    write_new_json(snapshot / "players.json", players)

    wanted: dict[int, dict] = {}
    battle_files: list[Path] = []
    battle_successes = 0
    for player in players:
        agent_id = int(player["agent_id"])
        service = "gamesPlayersRanking/findLastBattlesByAgentId"
        body = [agent_id, None]
        context = {
            "stage": "battle_list",
            "source_agent": agent_id,
            "source_rank": player["source_rank"],
            "groups": player["groups"],
        }
        try:
            response = request(service, body, context)
            done = completed_battles(response.payload)
        except Exception as error:  # noqa: BLE001 - preserve and continue cohort
            failures.append(
                {
                    "stage": "battle_list",
                    "source_agent": agent_id,
                    "source_rank": player["source_rank"],
                    "error": str(error)[:500],
                }
            )
            continue
        battle_path = snapshot / "battles" / f"{agent_id}.json"
        write_new_bytes(battle_path, response.raw)
        battle_files.append(battle_path)
        battle_successes += 1
        resident = "resident" in player["groups"]
        recent_ids = {int(row["gameId"]) for row in done[:RECENT_PER_LEGEND]}
        for battle in done:
            game_id = int(battle["gameId"])
            boss_visible = battle_has_visible_boss(battle)
            if not resident and game_id not in recent_ids and not boss_visible:
                continue
            game = wanted.setdefault(
                game_id,
                {"game_id": game_id, "boss_visible": False, "sources": {}},
            )
            game["boss_visible"] = bool(game["boss_visible"] or boss_visible)
            game["sources"][agent_id] = {
                "agent_id": agent_id,
                "source_rank": player["source_rank"],
                "groups": player["groups"],
            }

    game_records = []
    for game_id in sorted(wanted):
        wanted_game = wanted[game_id]
        sources = [
            wanted_game["sources"][agent]
            for agent in sorted(wanted_game["sources"])
        ]
        body = [game_id, None]
        request_sha256 = sha256_bytes(canonical_json_bytes(body))
        cache_path = games_cache / f"{game_id}.json"
        base_record = {
            "game_id": game_id,
            "service": "gameResult/findByGameId",
            "request_body_sha256": request_sha256,
            "classified_at_utc": timestamp(),
            "boss_visible": bool(wanted_game["boss_visible"]),
            "sources": sources,
            "cache_file": str(cache_path.relative_to(raw_root)),
        }
        if cache_path.exists():
            raw = cache_path.read_bytes()
            try:
                payload = json.loads(raw.decode())
                valid, frames, error = replay_shape(payload)
            except Exception as exception:  # noqa: BLE001
                valid, frames, error = False, None, str(exception)
            if valid:
                game_records.append(
                    {
                        **base_record,
                        "status": "already_present",
                        "response_sha256": sha256_bytes(raw),
                        "frames": frames,
                    }
                )
            else:
                failure = {
                    "stage": "replay_cache",
                    "game_id": game_id,
                    "error": f"immutable existing cache is invalid: {error}"[:500],
                }
                failures.append(failure)
                game_records.append(
                    {
                        **base_record,
                        "status": "failed_existing_invalid",
                        "response_sha256": sha256_bytes(raw),
                        "frames": None,
                        "error": failure["error"],
                    }
                )
            continue

        context = {
            "stage": "replay",
            "game_id": game_id,
            "source_agents": [source["agent_id"] for source in sources],
            "source_ranks": [source["source_rank"] for source in sources],
        }
        try:
            response = request("gameResult/findByGameId", body, context)
            valid, frames, error = replay_shape(response.payload)
            if not valid:
                raise ValueError(error)
            created = store_cache_immutable(cache_path, response.raw)
            if created:
                status = "fetched"
                response_sha256 = response.response_sha256
            else:
                cached = cache_path.read_bytes()
                cached_payload = json.loads(cached.decode())
                cached_valid, frames, cached_error = replay_shape(cached_payload)
                if not cached_valid:
                    raise ValueError(
                        f"concurrent immutable cache is invalid: {cached_error}"
                    )
                status = "already_present_race"
                response_sha256 = sha256_bytes(cached)
            game_records.append(
                {
                    **base_record,
                    "status": status,
                    "response_sha256": response_sha256,
                    "fetched_response_sha256": response.response_sha256,
                    "frames": frames,
                }
            )
        except Exception as error:  # noqa: BLE001 - classify every wanted game
            failure = {
                "stage": "replay",
                "game_id": game_id,
                "sources": sources,
                "error": str(error)[:500],
            }
            failures.append(failure)
            game_records.append(
                {
                    **base_record,
                    "status": "failed",
                    "response_sha256": None,
                    "frames": None,
                    "error": failure["error"],
                }
            )

    requests_path = snapshot / "requests.json"
    failures_path = snapshot / "failures.json"
    games_path = snapshot / "games.json"
    write_new_json(requests_path, request_log)
    write_new_json(failures_path, failures)
    write_new_json(games_path, game_records)

    status_counts = dict(
        sorted(collections_counter(record["status"] for record in game_records).items())
    )
    file_paths = [
        snapshot / "leaderboard.json",
        snapshot / "players.json",
        requests_path,
        failures_path,
        games_path,
        *battle_files,
    ]
    manifest = {
        "schema": "troll-farm-d61p-snapshot-v1",
        "snapshot_id": snapshot_id,
        "completed_at_utc": timestamp(),
        "complete": True,
        "all_wanted_games_classified": len(game_records) == len(wanted),
        "config": {
            "puzzle": PUZZLE,
            "resident_agent_id": resident_agent_id,
            "top_legend": TOP_LEGEND,
            "recent_games_per_legend": RECENT_PER_LEGEND,
            "minimum_request_interval_seconds": MIN_REQUEST_INTERVAL_SECONDS,
            "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "sampling_uses_outcomes": False,
        },
        "leaderboard": {
            "users": len(users),
            "response_sha256": leaderboard.response_sha256,
        },
        "players": players,
        "counts": {
            "selected_agents": len(players),
            "legend_rows_selected": min(
                TOP_LEGEND, sum(league_index(user) == 5 for user in users)
            ),
            "battle_lists_fetched": battle_successes,
            "battle_lists_failed": len(players) - battle_successes,
            "unique_games_wanted": len(wanted),
            "boss_visible_games": sum(record["boss_visible"] for record in game_records),
            "game_statuses": status_counts,
            "failures": len(failures),
            "requests": len(request_log),
        },
        "files": {
            str(path.relative_to(snapshot)): {
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in sorted(file_paths)
        },
    }
    if not manifest["all_wanted_games_classified"]:
        raise RuntimeError("D61p snapshot has unclassified wanted games")
    write_final_manifest(snapshot / "manifest.json", manifest)
    return snapshot


def collections_counter(values: Any) -> dict[Any, int]:
    result: dict[Any, int] = {}
    for value in values:
        result[value] = result.get(value, 0) + 1
    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot-id",
        help="immutable directory name; default is current UTC timestamp plus -d61p",
    )
    parser.add_argument(
        "--resident-agent-id",
        type=int,
        default=DEFAULT_RESIDENT_AGENT_ID,
        help="stable resident agent whose complete visible battle list is retained",
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        default=DEFAULT_RAW,
        help="raw corpus root containing snapshots/ and immutable games/ cache",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    snapshot = collect_snapshot(
        raw_root=args.raw_root,
        snapshot_id=args.snapshot_id,
        resident_agent_id=args.resident_agent_id,
    )
    manifest = json.loads((snapshot / "manifest.json").read_text())
    print(
        json.dumps(
            {
                "snapshot": str(snapshot),
                "complete": manifest["complete"],
                "counts": manifest["counts"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
