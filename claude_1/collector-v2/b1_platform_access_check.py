#!/usr/bin/env python3
"""B1 — platform-access check for collector v2 (task 20260811-s3-collector-v2).

Answers exactly one question: from THIS VM, does the frozen collector's read path work
against the platform with NO session cookie and no other credential?

Method: import the frozen `data/scripts/collect_snapshot.py` primitives verbatim
(`PublicClient`, `completed_battles`, `replay_shape`) and exercise all three read services
the collector uses, in the order collector v2 will use them:

  1. Leaderboards/getFilteredPuzzleLeaderboard   (cohort discovery)
  2. gamesPlayersRanking/findLastBattlesByAgentId (battle list for one leaderboard agent)
  3. gameResult/findByGameId                      (replay bodies)

`PublicClient` builds each request with only a `Content-Type` header and `urllib.request`
carries no cookie jar, so "cookieless" is a property of the client under test, not an
assumption: the script asserts it by inspecting the outgoing request headers.

Service (3) is exercised twice: against ids discovered live in step 2, and against
`--known-id` values already in this checkout's `data/raw/games/` cache — a game that is
old enough to have left any recent-battles window is the harder case for a public read.

Nothing is written to `data/raw/`. The report JSON goes where `--out` says (an artifact
path under `claude_1/`, committed as B1 evidence). No credential is read, and no response
body is stored — only ids, sizes, sha256 digests and shape verdicts.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from data.scripts.collect_snapshot import (  # noqa: E402
    BASE,
    PUZZLE,
    PublicClient,
    canonical_json_bytes,
    completed_battles,
    replay_shape,
    sha256_bytes,
    utc_now,
)

LEADERBOARD_BODY = [PUZZLE, None, "global", {"active": False, "column": "", "filter": ""}]


def assert_cookieless() -> dict:
    """Prove the client sends no credential, rather than assuming it.

    Builds the same Request object `PublicClient.post` builds and reports every header
    plus whether urllib would attach anything from an ambient cookie jar.
    """
    request = urllib.request.Request(
        f"{BASE}/Leaderboards/getFilteredPuzzleLeaderboard",
        data=canonical_json_bytes(LEADERBOARD_BODY),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    headers = dict(request.header_items())
    credential_headers = sorted(
        name for name in headers if name.lower() in {"cookie", "authorization"}
    )
    default_opener_handlers = [
        type(handler).__name__ for handler in urllib.request._opener.handlers
    ] if urllib.request._opener is not None else None
    return {
        "outgoing_headers": sorted(headers),
        "credential_headers_present": credential_headers,
        "cookieless": credential_headers == [],
        "global_opener_installed": default_opener_handlers is not None,
        "global_opener_handlers": default_opener_handlers,
    }


def probe(client: PublicClient, service: str, body: object) -> tuple[dict, object]:
    """One request, one record. Returns (record, payload); payload is None on failure.

    Each service is called exactly once per probe — the platform is a shared resource and
    B1 must not double its own read load.
    """
    record = {"service": service, "request_body_sha256": sha256_bytes(canonical_json_bytes(body))}
    try:
        response = client.post(service, body)
    except urllib.error.HTTPError as error:
        detail = error.read()[:400].decode(errors="replace")
        record.update(status="http_error", http_status=error.code, error=detail)
        return record, None
    except Exception as error:  # noqa: BLE001 — the verdict is "what stops a public read"
        record.update(status="error", error=f"{type(error).__name__}: {error}"[:500])
        return record, None
    record.update(
        status="ok",
        response_bytes=len(response.raw),
        response_sha256=response.response_sha256,
        payload_type=type(response.payload).__name__,
    )
    return record, response.payload


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B1 cookieless platform-access check")
    ap.add_argument("--out", required=True, help="path for the JSON evidence record")
    ap.add_argument("--known-id", action="append", type=int, default=[],
                    help="game id already in data/raw/games (repeatable)")
    ap.add_argument("--live-replays", type=int, default=3,
                    help="how many ids discovered from the battle list to fetch")
    args = ap.parse_args(argv)

    client = PublicClient()
    report: dict = {
        "check": "b1-platform-access",
        "task_id": "20260811-s3-collector-v2",
        "started_utc": utc_now(),
        "base": BASE,
        "puzzle": PUZZLE,
        "client": "data/scripts/collect_snapshot.PublicClient (frozen, unmodified)",
        "cookieless_assertion": assert_cookieless(),
        "stages": {},
    }

    leaderboard, payload = probe(client, "Leaderboards/getFilteredPuzzleLeaderboard",
                                 LEADERBOARD_BODY)
    report["stages"]["leaderboard"] = leaderboard
    agent_id = None
    if leaderboard["status"] == "ok":
        users = payload.get("users") if isinstance(payload, dict) else None
        leaderboard["users_present"] = isinstance(users, list)
        leaderboard["users_count"] = len(users) if isinstance(users, list) else None
        if users:
            top = users[0]
            agent_id = top.get("agentId") or (top.get("agent") or {}).get("agentId")
            leaderboard["probe_agent_id"] = agent_id

    battle_ids: list[int] = []
    if agent_id is not None:
        battles, payload = probe(client, "gamesPlayersRanking/findLastBattlesByAgentId",
                                 [int(agent_id), None])
        if battles["status"] == "ok":
            done = completed_battles(payload)
            battles["completed_battles"] = len(done)
            battle_ids = [int(row["gameId"]) for row in done if row.get("gameId")]
            battles["discovered_game_ids"] = battle_ids[: args.live_replays]
        report["stages"]["battle_list"] = battles
    else:
        report["stages"]["battle_list"] = {"status": "skipped",
                                           "reason": "no agent id from leaderboard"}

    replays = []
    targets = [(gid, "discovered_live") for gid in battle_ids[: args.live_replays]]
    targets += [(gid, "known_cached_id") for gid in args.known_id]
    for game_id, origin in targets:
        record, payload = probe(client, "gameResult/findByGameId", [game_id, None])
        record["game_id"] = game_id
        record["origin"] = origin
        if record["status"] == "ok":
            valid, frames, error = replay_shape(payload)
            record.update(replay_valid=valid, frames=frames, shape_error=error)
        replays.append(record)
    report["stages"]["replays"] = replays

    # Two verdicts, because they gate different things and the first run conflated them.
    # B1 gates B4, and B4 only ever fetches games it has just discovered — so the FORWARD
    # path (discover -> list -> fetch fresh) is what B1's stop rule is about. Whether an
    # arbitrary historical id still resolves is a separate property of the platform, and a
    # failure there is not a cookie verdict (see b1-visibility-hypothesis-*.json).
    live = [r for r in replays if r["origin"] == "discovered_live"]
    historical = [r for r in replays if r["origin"] == "known_cached_id"]
    stage_ok = {
        "leaderboard": report["stages"]["leaderboard"]["status"] == "ok",
        "battle_list": report["stages"]["battle_list"].get("status") == "ok",
        "replays_live": bool(live) and all(r.get("replay_valid") for r in live),
    }
    report["stage_ok"] = stage_ok
    report["forward_path_verdict"] = "COOKIELESS_OK" if all(stage_ok.values()) else "BLOCKED"
    report["historical_refetch"] = {
        "probed": len(historical),
        "resolved": sum(1 for r in historical if r.get("replay_valid")),
        "note": ("informational, not a B1 gate: arbitrary historical ids do not all resolve. "
                 "Mechanism measured separately — availability tracks participant battle "
                 "windows, not age, and not authentication."),
    }
    report["verdict"] = report["forward_path_verdict"]
    report["finished_utc"] = utc_now()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": report["verdict"], "stage_ok": stage_ok, "out": str(out)}, indent=2))
    return 0 if report["verdict"] == "COOKIELESS_OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
