#!/usr/bin/env python3
"""Command taxonomy for the LIVE submission's recent arena battles.

Fetches the last finished arena games, joins opponent Gold rank/score, then counts
per-player stdout command types from gameResult frames. This is read-only and is
intended to explain where wins/losses differ before designing the next candidate.

Usage:
  battle_taxonomy.py [max_games=80] [lo_rank=0] [hi_rank=1000000]
"""
import json
import re
import statistics
import sys
import urllib.request
from collections import Counter

TSH = "77167730956ef53402472b3c52474908f5b73026"
USERID = 1302251
PID = "spring-challenge-2026-troll-farm"
BASE = "https://www.codingame.com/services/"
SESSION = "/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"

COMMANDS = ("TRAIN", "MOVE", "CHOP", "HARVEST", "DROP", "PLANT", "PICK", "MINE", "WAIT")
PHASES = (
    ("t001-075", 1, 75),
    ("t076-150", 76, 150),
    ("t151-225", 151, 225),
    ("t226-300", 226, 300),
)


def cookie():
    parts = []
    for line in open(SESSION):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            value = value.strip()
            if value and "PASTE" not in value:
                parts.append(f"{name.strip()}={value}")
    return "; ".join(parts)


COOKIE = cookie()


def call(service, payload):
    req = urllib.request.Request(
        BASE + service,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Cookie": COOKIE},
    )
    return json.load(urllib.request.urlopen(req))


def split_stdout(stdout):
    for raw in re.split(r"[;\n]+", stdout or ""):
        cmd = raw.strip()
        if cmd:
            yield cmd


def command_counts(frames, player_index):
    counts = Counter()
    for frame in frames:
        if frame.get("agentId") != player_index or "stdout" not in frame:
            continue
        for cmd in split_stdout(frame.get("stdout")):
            op = cmd.split()[0]
            if op == "MSG":
                continue
            counts[op] += 1
    return counts


def phase_name(turn):
    for name, lo, hi in PHASES:
        if lo <= turn <= hi:
            return name
    return PHASES[-1][0]


def phase_command_counts(frames, player_index):
    counts = {name: Counter() for name, _, _ in PHASES}
    turn = 0
    for frame in frames:
        if frame.get("agentId") != player_index or "stdout" not in frame:
            continue
        turn += 1
        bucket = counts[phase_name(turn)]
        for cmd in split_stdout(frame.get("stdout")):
            op = cmd.split()[0]
            if op == "MSG":
                continue
            bucket[op] += 1
    return counts


def final_wood(frames, player_index):
    for frame in reversed(frames):
        view = frame.get("view") or ""
        match = re.search(r'"inputmodule":"([^"]+)"', view)
        if not match:
            continue
        lines = match.group(1).split("\\n")
        if len(lines) <= player_index:
            continue
        parts = lines[player_index].split()
        if len(parts) > 5:
            return int(parts[5])
    return None


def avg(rows, field):
    vals = [field(row) for row in rows]
    vals = [v for v in vals if v is not None]
    return statistics.mean(vals) if vals else None


def fmt(v, digits=1):
    return "n/a" if v is None else f"{v:.{digits}f}"


def print_command_table(title, rows):
    if not rows:
        print(f"\n== {title}: no games ==")
        return
    wins = sum(1 for row in rows if row["won"])
    print(
        f"\n== {title}: {wins}/{len(rows)} wins | "
        f"score {fmt(avg(rows, lambda r: r['my_score']), 0)}-"
        f"{fmt(avg(rows, lambda r: r['opp_score']), 0)} | "
        f"wood {fmt(avg(rows, lambda r: r['my_wood']), 1)}-"
        f"{fmt(avg(rows, lambda r: r['opp_wood']), 1)} =="
    )
    print(f"{'cmd':<8} {'us':>8} {'opp':>8} {'opp-us':>8}")
    for cmd in COMMANDS:
        us = avg(rows, lambda r, c=cmd: r["my_cmds"].get(c, 0))
        opp = avg(rows, lambda r, c=cmd: r["opp_cmds"].get(c, 0))
        print(f"{cmd:<8} {fmt(us, 1):>8} {fmt(opp, 1):>8} {fmt(opp - us, 1):>8}")


def print_phase_gap_table(title, rows):
    if not rows:
        return
    print(f"\n== {title}: opponent minus us by phase ==")
    cmds = ("TRAIN", "CHOP", "HARVEST", "DROP", "PICK", "MINE", "PLANT", "MOVE", "WAIT")
    for phase, _, _ in PHASES:
        print(f"\n{phase}")
        print(f"{'cmd':<8} {'us':>8} {'opp':>8} {'opp-us':>8}")
        for cmd in cmds:
            us = avg(rows, lambda r, p=phase, c=cmd: r["my_phase_cmds"][p].get(c, 0))
            opp = avg(rows, lambda r, p=phase, c=cmd: r["opp_phase_cmds"][p].get(c, 0))
            print(f"{cmd:<8} {fmt(us, 1):>8} {fmt(opp, 1):>8} {fmt(opp - us, 1):>8}")


def main():
    max_games = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    lo_rank = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    hi_rank = int(sys.argv[3]) if len(sys.argv) > 3 else 1_000_000

    battles = call("gamesPlayersRanking/findLastBattlesByTestSessionHandle", [TSH, None])
    done = [b for b in battles if b.get("done")][:max_games]

    leaderboard = call(
        "Leaderboards/getFilteredPuzzleLeaderboard",
        [PID, TSH, "global", {"active": False, "column": "", "filter": ""}],
    )
    rank_of = {
        user.get("pseudo"): (user.get("localRank"), user.get("score", 0.0))
        for user in leaderboard.get("users", [])
    }

    rows = []
    for battle in done:
        game_id = battle["gameId"]
        try:
            game = call("gameResult/findByGameId", [game_id, USERID])
        except Exception as exc:
            print(f"game {game_id}: fetch failed ({exc})")
            continue

        agents = game.get("agents") or []
        scores = game.get("scores") or []
        ranks = game.get("ranks") or []
        me = next(
            (
                idx
                for idx, agent in enumerate(agents)
                if (agent.get("codingamer") or {}).get("userId") == USERID
            ),
            None,
        )
        if me is None or len(scores) < 2:
            continue
        opp = 1 - me
        opp_name = (agents[opp].get("codingamer") or {}).get("pseudo", "?")
        opp_rank, opp_score = rank_of.get(opp_name, (None, None))
        if opp_rank is None or not (lo_rank <= opp_rank < hi_rank):
            continue

        my_score, their_score = scores[me], scores[opp]
        won = ranks[me] == 0 if ranks else my_score > their_score
        rows.append(
            {
                "game_id": game_id,
                "won": won,
                "my_score": my_score,
                "opp_score": their_score,
                "opp_name": opp_name,
                "opp_rank": opp_rank,
                "opp_ladder_score": opp_score,
                "my_cmds": command_counts(game.get("frames") or [], me),
                "opp_cmds": command_counts(game.get("frames") or [], opp),
                "my_phase_cmds": phase_command_counts(game.get("frames") or [], me),
                "opp_phase_cmds": phase_command_counts(game.get("frames") or [], opp),
                "my_wood": final_wood(game.get("frames") or [], me),
                "opp_wood": final_wood(game.get("frames") or [], opp),
            }
        )

    print(
        f"battles listed: {len(battles)} | analyzed: {len(rows)} finished "
        f"with opponent rank in [{lo_rank}, {hi_rank})"
    )
    print_command_table("all selected", rows)
    print_command_table("wins", [row for row in rows if row["won"]])
    losses = [row for row in rows if not row["won"]]
    print_command_table("losses", losses)
    print_phase_gap_table("losses", losses)

    if losses:
        print("\nLosses by margin:")
        for row in sorted(losses, key=lambda r: r["my_score"] - r["opp_score"])[:12]:
            print(
                f"  {row['my_score']:.0f}-{row['opp_score']:.0f} "
                f"({row['my_score'] - row['opp_score']:+.0f}) "
                f"rank {row['opp_rank']} {row['opp_name']} game {row['game_id']}"
            )


if __name__ == "__main__":
    main()
