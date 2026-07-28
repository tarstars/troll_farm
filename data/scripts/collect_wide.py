#!/usr/bin/env python3
"""Daily wide-lens D61p replay collection driver (B0.4, authorized 2026-07-28).

Self-contained production driver for the widened passive collection lens validated in the
2026-07-28 one-shot run: resident (full battle history) + Legend leaderboard ranks
``[rank_lo, rank_hi]`` (default 1-50), each with its FULL visible battle window (no
recent-10 cap). It imports and reuses ``data/scripts/collect_snapshot.py``'s request/cache
primitives (``PublicClient``, ``battle_has_visible_boss``, ``completed_battles``,
``replay_shape``, ``store_cache_immutable``, the atomic ``write_new_*``/``write_final_manifest``
helpers, ...) verbatim and never edits that frozen file. Every replay body still lands,
deduplicated, in the single shared immutable ``data/raw/games/<gameId>.json`` cache, so this
driver and the plain default collector can never disagree about what a game's canonical body
is. Output is a self-contained snapshot directory using the same
``troll-farm-d61p-snapshot-v1`` manifest schema, so ``data/scripts/parse_snapshot.py`` (also
unmodified) can QA it, followed by a full cumulative rebuild via ``data/scripts/parse.py``
(also unmodified).

Known pitfall fixed here (found in the 2026-07-28 ad hoc run): the resident's own
leaderboard rank can fall inside ``[rank_lo, rank_hi]``. Rather than adding it twice under
different group tags (which silently overwrote the resident's provenance in that run — see
the ledger), the resident is selected once, up front, and explicitly excluded from the rank
slice below.

Reliability: every network POST goes through a bounded-retry wrapper (default 3 attempts,
linear backoff) for transient errors (DNS, timeout, TLS, 5xx). HTTP 422/429 is treated as a
hard stop: no retry, no ``manifest.json`` is published for the in-flight snapshot (so
``parse_snapshot.py`` will never see it as complete), and the process exits nonzero. Because
every replay body is written exactly once into the shared immutable cache and battle lists
are always re-fetched fresh, re-running after any failure (including a hard stop) is safe and
does no partial-state damage.

Network execution is intentionally separate from TestSession, Arena comparison, and
submission: this module only ever calls read-only public JSON services (leaderboard, battle
list, replay-by-id).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
import urllib.error
from collections.abc import Callable
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from data.scripts.collect_snapshot import (
    DEFAULT_RAW,
    DEFAULT_RESIDENT_AGENT_ID,
    MIN_REQUEST_INTERVAL_SECONDS,
    PUZZLE,
    REQUEST_TIMEOUT_SECONDS,
    SNAPSHOT_RE,
    TOP_LEGEND,
    ApiResponse,
    Client,
    PublicClient,
    battle_has_visible_boss,
    canonical_json_bytes,
    collections_counter,
    completed_battles,
    league_index,
    replay_shape,
    sha256_bytes,
    sha256_file,
    source_rank,
    store_cache_immutable,
    utc_now,
    write_final_manifest,
    write_new_bytes,
    write_new_json,
)
from data.scripts.parse import main as parse_main
from data.scripts.parse_snapshot import parse_snapshot

RANK_LO = 1
RANK_HI = 50
MAX_REQUEST_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 2.0
HARD_STOP_HTTP_CODES = frozenset({422, 429})
LOG_FILENAME = "collect_wide.log"


class HardStop(Exception):
    """Raised on HTTP 422/429; callers must abort without publishing a manifest."""

    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def default_snapshot_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ-d61p-wide")


def make_requester(
    client: Client,
    request_log: list[dict],
    *,
    timestamp: Callable[[], str] = utc_now,
    max_attempts: int = MAX_REQUEST_ATTEMPTS,
    backoff_seconds: float = RETRY_BACKOFF_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
) -> Callable[[str, object, dict], ApiResponse]:
    """Build a request() closure: bounded retry on transient errors, immediate HardStop on 422/429.

    Every physical attempt (success or failure) gets its own row in ``request_log``, so the
    audit trail reflects exactly what happened over the wire.
    """

    def request(service: str, body: object, context: dict) -> ApiResponse:
        request_sha256 = sha256_bytes(canonical_json_bytes(body))
        last_error: Exception | None = None
        for attempt in range(1, max_attempts + 1):
            requested_at = timestamp()
            try:
                response = client.post(service, body)
            except urllib.error.HTTPError as error:
                request_log.append(
                    {
                        "service": service,
                        "request_body_sha256": request_sha256,
                        "response_sha256": None,
                        "requested_at_utc": requested_at,
                        "status": "failed",
                        "attempt": attempt,
                        "context": context,
                        "error": f"HTTPError {error.code}: {error.reason}"[:500],
                    }
                )
                if error.code in HARD_STOP_HTTP_CODES:
                    raise HardStop(
                        error.code, f"{service} -> HTTP {error.code}: {error.reason}"
                    ) from error
                last_error = error
            except Exception as error:  # noqa: BLE001 - retry transient network errors
                request_log.append(
                    {
                        "service": service,
                        "request_body_sha256": request_sha256,
                        "response_sha256": None,
                        "requested_at_utc": requested_at,
                        "status": "failed",
                        "attempt": attempt,
                        "context": context,
                        "error": str(error)[:500],
                    }
                )
                last_error = error
            else:
                request_log.append(
                    {
                        "service": service,
                        "request_body_sha256": request_sha256,
                        "response_sha256": response.response_sha256,
                        "requested_at_utc": requested_at,
                        "status": "ok",
                        "attempt": attempt,
                        "context": context,
                    }
                )
                return response
            if attempt < max_attempts:
                sleep(backoff_seconds * attempt)
        assert last_error is not None
        raise last_error

    return request


def _player_row(user: dict, groups: list[str], legend_order: int | None) -> dict:
    agent_id = int(user["agentId"])
    return {
        "agent_id": agent_id,
        "pseudo": user.get("pseudo", f"agent-{agent_id}"),
        "user_id": (user.get("codingamer") or {}).get("userId"),
        "league_index": league_index(user),
        "global_rank": user.get("rank"),
        "local_rank": user.get("localRank"),
        "source_rank": source_rank(user),
        "score": user.get("score"),
        "groups": list(groups),
        "legend_order": legend_order,
    }


def select_wide_players(
    users: list[dict],
    resident_agent_id: int,
    rank_lo: int,
    rank_hi: int,
    top_legend_cutoff: int = TOP_LEGEND,
) -> list[dict]:
    """Resident (once, full window) + Legend ranks ``[rank_lo, rank_hi]``.

    The resident is always selected first and is explicitly excluded from the rank slice
    below — the known pitfall from the 2026-07-28 ad hoc run (resident rank 43 fell inside
    [21, 50]; a second pass silently overwrote its ``sources`` group tag because ``wanted``
    is keyed by agent_id). Excluding it here means it is only ever added once, so that bug
    class cannot recur.
    """

    legends = [user for user in users if league_index(user) == 5]
    window = legends[rank_lo - 1 : rank_hi]

    resident_user = next(
        (user for user in users if int(user.get("agentId", -1)) == resident_agent_id),
        None,
    )
    if resident_user is None:
        resident_user = {
            "agentId": resident_agent_id,
            "pseudo": f"agent-{resident_agent_id}",
            "codingamer": {},
            "league": {},
        }
    players = [_player_row(resident_user, ["resident"], None)]

    for order, user in enumerate(window, start=rank_lo):
        agent_id = int(user["agentId"])
        if agent_id == resident_agent_id:
            continue
        group = "legend_top20" if order <= top_legend_cutoff else "legend_21_50"
        players.append(_player_row(user, [group], order))

    return players


def collect_wide(
    *,
    raw_root: Path = DEFAULT_RAW,
    snapshot_id: str | None = None,
    resident_agent_id: int = DEFAULT_RESIDENT_AGENT_ID,
    rank_lo: int = RANK_LO,
    rank_hi: int = RANK_HI,
    client: Client | None = None,
    timestamp: Callable[[], str] = utc_now,
    max_attempts: int = MAX_REQUEST_ATTEMPTS,
    backoff_seconds: float = RETRY_BACKOFF_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
) -> Path:
    snapshot_id = snapshot_id or default_snapshot_id()
    if not SNAPSHOT_RE.fullmatch(snapshot_id):
        raise ValueError(f"unsafe snapshot id: {snapshot_id!r}")
    raw_root = Path(raw_root)
    resident_agent_id = int(resident_agent_id)
    snapshot = raw_root / "snapshots" / snapshot_id
    snapshot.mkdir(parents=True, exist_ok=False)
    (snapshot / "battles").mkdir()
    games_cache = raw_root / "games"
    games_cache.mkdir(parents=True, exist_ok=True)
    client = client or PublicClient()

    request_log: list[dict] = []
    failures: list[dict] = []
    request = make_requester(
        client,
        request_log,
        timestamp=timestamp,
        max_attempts=max_attempts,
        backoff_seconds=backoff_seconds,
        sleep=sleep,
    )

    try:
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

        players = select_wide_players(users, resident_agent_id, rank_lo, rank_hi)
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
            except HardStop:
                raise
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
            # Wide lens: every player's FULL visible window, no recent-10 cap.
            for battle in done:
                game_id = int(battle["gameId"])
                boss_visible = battle_has_visible_boss(battle)
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
                wanted_game["sources"][agent] for agent in sorted(wanted_game["sources"])
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
            except HardStop:
                raise
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
    except HardStop as stop:
        # Preserve everything collected so far as non-finalized: no manifest.json is
        # published, so parse_snapshot.py will never treat this directory as a complete,
        # QA-able snapshot. The shared games/ cache only ever received whole, validated
        # replay bodies, so no partial-state damage is possible here either.
        requests_path = snapshot / "requests.json"
        failures_path = snapshot / "failures.json"
        write_new_json(requests_path, request_log)
        write_new_json(failures_path, failures)
        write_new_json(
            snapshot / "HARD_STOP.json",
            {
                "code": stop.code,
                "message": str(stop),
                "requests_issued": len(request_log),
            },
        )
        raise

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
            "recent_games_per_legend": None,
            "minimum_request_interval_seconds": MIN_REQUEST_INTERVAL_SECONDS,
            "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "sampling_uses_outcomes": False,
            "driver": "data/scripts/collect_wide.py",
            "widen_policy": "resident=all, legend_ranks=full_window (no recent-10 cap)",
            "widen_rank_window": [rank_lo, rank_hi],
        },
        "leaderboard": {
            "users": len(users),
            "response_sha256": leaderboard.response_sha256,
        },
        "players": players,
        "counts": {
            "selected_agents": len(players),
            "legend_rows_selected": len(players) - 1,
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
        raise RuntimeError("D61p wide snapshot has unclassified wanted games")
    write_final_manifest(snapshot / "manifest.json", manifest)
    return snapshot


def _append_log_line(log_path: Path, *, status: str, fields: dict[str, Any]) -> None:
    parts = " ".join(f"{key}={value}" for key, value in fields.items())
    line = f"{utc_now()} status={status}" + (f" {parts}" if parts else "")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a") as handle:
        handle.write(line + "\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot-id",
        help="immutable directory name; default is current UTC timestamp plus -d61p-wide",
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
    parser.add_argument("--rank-lo", type=int, default=RANK_LO)
    parser.add_argument("--rank-hi", type=int, default=RANK_HI)
    parser.add_argument("--max-attempts", type=int, default=MAX_REQUEST_ATTEMPTS)
    parser.add_argument(
        "--retry-backoff-seconds", type=float, default=RETRY_BACKOFF_SECONDS
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    raw_root = Path(args.raw_root)
    log_path = raw_root / LOG_FILENAME

    try:
        snapshot = collect_wide(
            raw_root=raw_root,
            snapshot_id=args.snapshot_id,
            resident_agent_id=args.resident_agent_id,
            rank_lo=args.rank_lo,
            rank_hi=args.rank_hi,
            max_attempts=args.max_attempts,
            backoff_seconds=args.retry_backoff_seconds,
        )
    except HardStop as stop:
        _append_log_line(log_path, status="hard_stop", fields={"code": stop.code, "message": str(stop)})
        print(
            json.dumps(
                {"status": "hard_stop", "code": stop.code, "message": str(stop)},
                sort_keys=True,
            )
        )
        sys.exit(3)
    except Exception as error:  # noqa: BLE001 - cron must log before it dies
        _append_log_line(
            log_path, status="error", fields={"error": f"{type(error).__name__}: {error}"[:500]}
        )
        print(
            json.dumps(
                {"status": "error", "error": f"{type(error).__name__}: {error}"[:500]},
                sort_keys=True,
            )
        )
        raise

    manifest = json.loads((snapshot / "manifest.json").read_text())
    game_statuses = manifest["counts"]["game_statuses"]
    new_games = game_statuses.get("fetched", 0) + game_statuses.get("already_present_race", 0)

    try:
        processed = parse_snapshot(snapshot)
        qa = json.loads((processed / "qa.json").read_text())
        qa_pass = bool(qa["pass"])
    except Exception as error:  # noqa: BLE001
        _append_log_line(
            log_path,
            status="qa_error",
            fields={
                "snapshot": snapshot.name,
                "new_games": new_games,
                "error": f"{type(error).__name__}: {error}"[:500],
            },
        )
        print(
            json.dumps(
                {
                    "status": "qa_error",
                    "snapshot": str(snapshot),
                    "error": f"{type(error).__name__}: {error}"[:500],
                },
                sort_keys=True,
            )
        )
        raise

    try:
        parse_main()  # rebuilds data/processed/{games.jsonl,maps.jsonl,stats.json} from raw/games/
        stats = json.loads((raw_root.parent / "processed" / "stats.json").read_text())
        cumulative = stats["games_parsed"]
    except Exception as error:  # noqa: BLE001
        _append_log_line(
            log_path,
            status="rebuild_error",
            fields={
                "snapshot": snapshot.name,
                "new_games": new_games,
                "qa_pass": qa_pass,
                "error": f"{type(error).__name__}: {error}"[:500],
            },
        )
        print(
            json.dumps(
                {
                    "status": "rebuild_error",
                    "snapshot": str(snapshot),
                    "error": f"{type(error).__name__}: {error}"[:500],
                },
                sort_keys=True,
            )
        )
        raise

    _append_log_line(
        log_path,
        status="ok",
        fields={
            "snapshot": snapshot.name,
            "new_games": new_games,
            "cumulative": cumulative,
            "qa_pass": str(qa_pass).lower(),
        },
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "snapshot": str(snapshot),
                "new_games": new_games,
                "cumulative": cumulative,
                "qa_pass": qa_pass,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
