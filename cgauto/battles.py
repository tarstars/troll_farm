#!/usr/bin/env python3
"""Download + analyze the LIVE submission's arena battles (LAST BATTLES, via REST).

For the current test session: fetches the battle list, pulls each game's result, joins
opponents with the Gold leaderboard (their localRank/score), and reports W/L, margins,
and the band breakdown — i.e. WHO beats the current bot and by how much.

Usage: battles.py [max_games=30]
"""
import json, sys, urllib.request

TSH = "77167730956ef53402472b3c52474908f5b73026"
USERID = 1302251
PID = "spring-challenge-2026-troll-farm"
BASE = "https://www.codingame.com/services/"


def cookie():
    cks = []
    for line in open("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            n, v = line.split("=", 1)
            if v.strip() and "PASTE" not in v.strip():
                cks.append(f"{n.strip()}={v.strip()}")
    return "; ".join(cks)


COOKIE = cookie()


def call(svc, payload):
    req = urllib.request.Request(
        BASE + svc, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Cookie": COOKIE})
    return json.load(urllib.request.urlopen(req))


def main():
    maxg = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    battles = call("gamesPlayersRanking/findLastBattlesByTestSessionHandle", [TSH, None])
    done = [b for b in battles if b.get("done")][:maxg]
    print(f"battles listed: {len(battles)} (analyzing {len(done)} finished)")

    # leaderboard join: pseudo -> (localRank, score)
    lb = call("Leaderboards/getFilteredPuzzleLeaderboard",
              [PID, TSH, "global", {"active": False, "column": "", "filter": ""}])
    rank_of = {u.get("pseudo"): (u.get("localRank"), u.get("score", 0.0))
               for u in lb.get("users", [])}

    rows = []
    for b in done:
        gid = b["gameId"]
        try:
            g = call("gameResult/findByGameId", [gid, None])
        except Exception as e:
            print(f"  game {gid}: fetch failed ({e})"); continue
        agents = g.get("agents") or []
        ranks = g.get("ranks") or []
        scores = g.get("scores") or []
        me_idx = next((i for i, a in enumerate(agents)
                       if (a.get("codingamer") or {}).get("userId") == USERID), None)
        if me_idx is None or len(scores) < 2:
            continue
        opp_idx = 1 - me_idx
        opp = (agents[opp_idx].get("codingamer") or {}).get("pseudo", "?")
        my_s, opp_s = scores[me_idx], scores[opp_idx]
        won = ranks[me_idx] == 0 if ranks else my_s > opp_s
        orank, oscore = rank_of.get(opp, (None, None))
        rows.append((won, my_s, opp_s, opp, orank, oscore, gid))

    if not rows:
        print("no parsable games"); return
    wins = sum(1 for r in rows if r[0])
    print(f"\n== {wins}/{len(rows)} wins | avg score {sum(r[1] for r in rows)/len(rows):.0f}"
          f" vs {sum(r[2] for r in rows)/len(rows):.0f} ==")
    print(f"{'W/L':3} {'my':>4} {'opp':>4} {'margin':>7}  {'oppRank':>7} {'oppScr':>6}  opponent / gameId")
    for won, ms, os_, opp, orank, oscore, gid in rows:
        print(f"{'W' if won else 'L':3} {ms:4.0f} {os_:4.0f} {ms-os_:+7.0f}  "
              f"{orank if orank is not None else '?':>7} "
              f"{f'{oscore:.1f}' if oscore is not None else '?':>6}  {opp}  {gid}")
    # band breakdown
    bands = [(0, 100), (100, 150), (150, 250), (250, 10**9)]
    print("\nby opponent Gold rank band:")
    for lo, hi in bands:
        sel = [r for r in rows if r[4] is not None and lo <= r[4] < hi]
        if sel:
            w = sum(1 for r in sel if r[0])
            print(f"  rank {lo:>3}-{hi if hi < 10**9 else '…':>3}: {w}/{len(sel)} wins"
                  f"  (avg margin {sum(r[1]-r[2] for r in sel)/len(sel):+.0f})")
    unranked = [r for r in rows if r[4] is None]
    if unranked:
        w = sum(1 for r in unranked if r[0])
        print(f"  not in top-1000 list: {w}/{len(unranked)} wins")


if __name__ == "__main__":
    main()
