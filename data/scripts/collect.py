#!/usr/bin/env python3
"""Collect CodinGame Spring Challenge 2026 (Troll Farm) game replays.

Pure stdlib. Public CodinGame services, no auth required.
Polite: sleeps SLEEP seconds between requests, 20 s timeout per request.
Idempotent: already-downloaded replays are skipped, so re-running extends
the dataset (new battles) without refetching.

Usage:
    python3 data/scripts/collect.py            # full collection
    python3 data/scripts/collect.py --no-fetch # only refresh leaderboard/battles

Outputs (relative to data/):
    raw/leaderboard.json          full leaderboard snapshot (top 1000)
    raw/players.json              selected players manifest (tass + top Legend/Gold)
    raw/battles/<agentId>.json    battle lists per selected agent
    raw/games/<gameId>.json       raw replays (gameResult/findByGameId)
    raw/fetch_log.json            per-gameId fetch status incl. failures
"""
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE = "https://www.codingame.com/services"
DATA = Path(__file__).resolve().parent.parent
RAW = DATA / "raw"
SLEEP = 0.35          # s between requests (be nice)
TIMEOUT = 20          # s per request
OUR_PSEUDO = "tass"
TOP_N = 15            # top players per league
GAMES_PER_PLAYER = 5  # recent finished games per top player
LEAGUE_NAMES = {0: "Wood2", 1: "Wood1", 2: "Bronze", 3: "Silver", 4: "Gold", 5: "Legend"}


def post(service: str, body) -> object:
    req = urllib.request.Request(
        f"{BASE}/{service}",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode())


def main(fetch_games: bool = True) -> None:
    (RAW / "games").mkdir(parents=True, exist_ok=True)
    (RAW / "battles").mkdir(parents=True, exist_ok=True)

    # 1. Leaderboard ---------------------------------------------------------
    lb = post(
        "Leaderboards/getFilteredPuzzleLeaderboard",
        ["spring-challenge-2026-troll-farm", None, "global",
         {"active": False, "column": "", "filter": ""}],
    )
    (RAW / "leaderboard.json").write_text(json.dumps(lb))
    users = lb["users"]
    print(f"leaderboard: {len(users)} users", flush=True)

    def li(u):
        return u.get("league", {}).get("divisionIndex")

    ours = [u for u in users if u.get("pseudo") == OUR_PSEUDO]
    legend = [u for u in users if li(u) == 5][:TOP_N]
    gold = [u for u in users if li(u) == 4][:TOP_N]
    selected = {}
    for group, us in (("ours", ours), ("legend_top", legend), ("gold_top", gold)):
        for u in us:
            selected[u["agentId"]] = {
                "pseudo": u["pseudo"],
                "agentId": u["agentId"],
                "userId": u.get("codingamer", {}).get("userId"),
                "group": group,
                "leagueIndex": li(u),
                "league": LEAGUE_NAMES.get(li(u)),
                "globalRank": u.get("rank"),
                "score": u.get("score"),
            }
    (RAW / "players.json").write_text(json.dumps(selected, indent=1))
    print(f"selected {len(selected)} players "
          f"(ours={len(ours)}, legend={len(legend)}, gold={len(gold)})", flush=True)

    # 2. Battle lists --------------------------------------------------------
    want = {}  # gameId -> source agentId
    for aid, meta in selected.items():
        time.sleep(SLEEP)
        try:
            battles = post("gamesPlayersRanking/findLastBattlesByAgentId", [aid, None])
        except Exception as e:  # noqa: BLE001
            print(f"battles FAILED agent {aid} ({meta['pseudo']}): {e}", flush=True)
            continue
        (RAW / "battles" / f"{aid}.json").write_text(json.dumps(battles))
        done = sorted((b for b in battles if b.get("done") and b.get("gameId")),
                      key=lambda b: -b["gameId"])
        keep = done if meta["group"] == "ours" else done[:GAMES_PER_PLAYER]
        for b in keep:
            want.setdefault(b["gameId"], aid)
        print(f"battles {meta['pseudo']:<22} ({meta['group']}): "
              f"{len(done)} done, keeping {len(keep)}", flush=True)

    print(f"total unique games wanted: {len(want)}", flush=True)
    if not fetch_games:
        return

    # 3. Replays -------------------------------------------------------------
    log_path = RAW / "fetch_log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {}
    ok = fail = skip = 0
    for i, (gid, src) in enumerate(sorted(want.items())):
        out = RAW / "games" / f"{gid}.json"
        if out.exists():
            skip += 1
            continue
        time.sleep(SLEEP)
        try:
            replay = post("gameResult/findByGameId", [gid, None])
            if not isinstance(replay, dict) or "frames" not in replay:
                raise ValueError(f"unexpected shape: {str(replay)[:120]}")
            out.write_text(json.dumps(replay))
            log[str(gid)] = {"status": "ok", "source_agent": src,
                             "frames": len(replay["frames"])}
            ok += 1
        except Exception as e:  # noqa: BLE001
            log[str(gid)] = {"status": "fail", "source_agent": src, "error": str(e)[:300]}
            fail += 1
            print(f"replay FAILED {gid}: {e}", flush=True)
        if (ok + fail) % 25 == 0:
            log_path.write_text(json.dumps(log, indent=0))
            print(f"progress {i + 1}/{len(want)} ok={ok} fail={fail} skip={skip}",
                  flush=True)
    log_path.write_text(json.dumps(log, indent=0))
    print(f"DONE ok={ok} fail={fail} skipped_existing={skip} "
          f"total_files={len(list((RAW / 'games').glob('*.json')))}", flush=True)


if __name__ == "__main__":
    main(fetch_games="--no-fetch" not in sys.argv)
