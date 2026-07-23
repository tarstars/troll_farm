#!/usr/bin/env python3
"""Collect CodinGame Spring Challenge 2026 (Troll Farm) game replays.

Pure stdlib. Public CodinGame services, no auth required.
Polite: sleeps SLEEP seconds between requests, 20 s timeout per request.
Idempotent: already-downloaded replays are skipped, so re-running extends
the dataset (new battles) without refetching.

Usage:
    python3 data/scripts/collect.py            # full collection
    python3 data/scripts/collect.py --no-fetch # only refresh leaderboard/battles
    python3 data/scripts/collect.py --agent-id 6551038 --agent-only
                                                # only this agent and its games

Outputs (relative to data/):
    raw/leaderboard.json          full leaderboard snapshot (top 1000)
    raw/players.json              selected players manifest (target + top Legend/Gold)
    raw/battles/<agentId>.json    battle lists per selected agent
    raw/games/<gameId>.json       raw replays (gameResult/findByGameId)
    raw/fetch_log.json            per-gameId fetch status incl. failures
"""
import argparse
import json
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


def selected_players(
    users: list[dict], agent_id: int | None = None, agent_only: bool = False
) -> tuple[dict[int, dict], int, int, int]:
    """Build the collection manifest without coupling an agent id to a pseudo."""

    def li(user: dict) -> int | None:
        return user.get("league", {}).get("divisionIndex")

    if agent_id is None:
        ours = [user for user in users if user.get("pseudo") == OUR_PSEUDO]
    else:
        ours = [user for user in users if user.get("agentId") == agent_id]
        if not ours:
            ours = [{"agentId": agent_id, "pseudo": f"agent-{agent_id}"}]

    legend = [] if agent_only else [user for user in users if li(user) == 5][:TOP_N]
    gold = [] if agent_only else [user for user in users if li(user) == 4][:TOP_N]
    selected: dict[int, dict] = {}
    # Add the target last so an agent that is also in a top cohort keeps the
    # "ours" scope, which captures all of its finished games.
    cohorts = (("legend_top", legend), ("gold_top", gold), ("ours", ours))
    for group, group_users in cohorts:
        for user in group_users:
            selected[user["agentId"]] = {
                "pseudo": user.get("pseudo", f"agent-{user['agentId']}"),
                "agentId": user["agentId"],
                "userId": user.get("codingamer", {}).get("userId"),
                "group": group,
                "leagueIndex": li(user),
                "league": LEAGUE_NAMES.get(li(user)),
                "globalRank": user.get("rank"),
                "score": user.get("score"),
            }
    return selected, len(ours), len(legend), len(gold)


def main(
    fetch_games: bool = True, agent_id: int | None = None, agent_only: bool = False
) -> None:
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

    selected, ours_count, legend_count, gold_count = selected_players(
        users, agent_id=agent_id, agent_only=agent_only
    )
    (RAW / "players.json").write_text(json.dumps(selected, indent=1))
    print(f"selected {len(selected)} players "
          f"(ours={ours_count}, legend={legend_count}, gold={gold_count})", flush=True)

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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="refresh the leaderboard and battle lists without fetching replays",
    )
    parser.add_argument(
        "--agent-id",
        type=int,
        help=f"collect this exact agent as ours instead of looking up pseudo {OUR_PSEUDO!r}",
    )
    parser.add_argument(
        "--agent-only",
        action="store_true",
        help="skip top Legend/Gold cohorts and collect only --agent-id",
    )
    args = parser.parse_args(argv)
    if args.agent_only and args.agent_id is None:
        parser.error("--agent-only requires --agent-id")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    main(
        fetch_games=not arguments.no_fetch,
        agent_id=arguments.agent_id,
        agent_only=arguments.agent_only,
    )
