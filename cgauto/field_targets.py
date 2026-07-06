#!/usr/bin/env python3
"""List FIELD-GATE opponents: Gold players around/above our rank, with agentIds.

Why: 2026-07-06 proved the boss gate alone is insufficient — v1.23.0-seedloop had the
best-ever boss numbers and cratered vs the arena field (205 @ 15.6). Economy changes must
also be gated against real field opponents:
    collect_debug_games.py <dbg.min.rs> <agentId> 2      # per opponent from this list

Usage: field_targets.py [lo_rank] [hi_rank]    (Gold localRank band, default 95 140)
"""
import json, sys, urllib.request

TSH = "77167730956ef53402472b3c52474908f5b73026"
PID = "spring-challenge-2026-troll-farm"


def cookie():
    cks = []
    for line in open("/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            n, v = line.split("=", 1)
            if v.strip() and "PASTE" not in v.strip():
                cks.append(f"{n.strip()}={v.strip()}")
    return "; ".join(cks)


def main():
    lo = int(sys.argv[1]) if len(sys.argv) > 1 else 95
    hi = int(sys.argv[2]) if len(sys.argv) > 2 else 140
    req = urllib.request.Request(
        "https://www.codingame.com/services/Leaderboards/getFilteredPuzzleLeaderboard",
        data=json.dumps([PID, TSH, "global", {"active": False, "column": "", "filter": ""}]).encode(),
        headers={"Content-Type": "application/json", "Cookie": cookie()})
    js = json.load(urllib.request.urlopen(req))
    rows = []
    for u in js.get("users", []):
        lg = u.get("league") or {}
        # Gold room = divisionCount-2 (Legend is the last); identify by our own row's division
        if u.get("pseudo") == "tass":
            gold_div = lg.get("divisionIndex")
    for u in js.get("users", []):
        lg = u.get("league") or {}
        if lg.get("divisionIndex") == gold_div and lo <= u.get("localRank", 10**9) <= hi:
            rows.append((u["localRank"], u.get("score", 0), u.get("pseudo", "?"),
                         u.get("agentId"), u.get("programmingLanguage", "?")))
    rows.sort()
    print(f"Gold divisionIndex={gold_div}, localRank {lo}-{hi}: {len(rows)} players")
    for r, s, p, a, l in rows:
        print(f"  rank {r:3}  score {s:5.1f}  agentId {a:<9}  {l:<12} {p}")


if __name__ == "__main__":
    main()
