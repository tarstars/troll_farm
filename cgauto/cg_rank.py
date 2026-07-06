#!/usr/bin/env python3
"""Print our current Troll Farm rank / score / league AND the Legend boundary.

Read-only. Uses the `codingame` PyPI package (login via rememberMe cookie in
cg_session.txt). Replaces ad-hoc inline leaderboard scripts.

Usage:
  cg_rank.py                 # our line + Legend boundary
  cg_rank.py --top [N]       # also print the top N of the ladder (default 10)

Example:
  tass: rank 213 score 18.2 Gold | Legend needs rank<=97 score>=~26.0 (2080 ranked)
"""
import sys, json, urllib.request

PID = "spring-challenge-2026-troll-farm"
PSEUDO = "tass"
UID = 1302251
TSH = "77167730956ef53402472b3c52474908f5b73026"  # our test session handle
SESSION = "/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"


def remember_me():
    for line in open(SESSION):
        line = line.strip()
        if line.startswith("rememberMe="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no rememberMe= line in cg_session.txt")


def cookie():
    ck = []
    for line in open(SESSION):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            n, v = line.split("=", 1)
            if v.strip() and "PASTE" not in v:
                ck.append(f"{n.strip()}={v.strip()}")
    return "; ".join(ck)


def arena_room():
    """The AUTHORITATIVE arena-division-room rank (what the site shows) — the codingame
    package's global leaderboard reports a DIFFERENT scope. Returns the ranking dict or None."""
    try:
        req = urllib.request.Request(
            "https://www.codingame.com/services/Leaderboards/"
            "getUserArenaDivisionRoomRankingByTestSessionHandle",
            data=json.dumps([TSH, UID]).encode(),
            headers={"Content-Type": "application/json", "Cookie": cookie(),
                     "User-Agent": "Mozilla/5.0"})
        return json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
    except Exception as e:
        print(f"(arena-room fetch failed: {type(e).__name__})")
        return None


def main():
    # 1) AUTHORITATIVE arena-room rank (the number the site shows)
    ar = arena_room()
    if ar and isinstance(ar, dict) and "rank" in ar:
        div = {4: "Gold", 5: "Legend"}.get((ar.get("league") or {}).get("divisionIndex"), "?")
        promo = ar.get("eligibleForPromotion")
        print(f"ARENA-ROOM: {ar.get('pseudo', PSEUDO)} rank {ar['rank']}/{ar.get('total','?')} "
              f"{div} score {ar.get('score', 0):.1f} | promotable={promo} | agentId={ar.get('agentId')}")

    import codingame

    client = codingame.Client()
    client.login(remember_me_cookie=remember_me())
    lb = client.get_puzzle_leaderboard(PID)
    users = lb.users
    total = len(users)

    # our row: match by userId first (robust to pseudo changes), else pseudo
    me = next((u for u in users if getattr(u, "id", None) == UID), None)
    if me is None:
        me = next((u for u in users if (u.pseudo or "").lower() == PSEUDO.lower()), None)

    # Legend boundary. Legend occupies the top `count` ranks contiguously, but you ENTER
    # Legend by BEATING BOSS 5 — not by crossing a score threshold. So the min-Legend score
    # is polluted by freshly-promoted players whose agent then tanked (e.g. rank 97 @ -6.6).
    # The meaningful bar is the TOP non-Legend (top-of-Gold) score: the boss-5 proxy you must
    # out-compete to promote.
    legend = next((lg for lg in lb.leagues if lg.name == "Legend"), None)
    if legend:
        top_gold = max((u for u in users if not (u.league and u.league.name == "Legend")),
                       key=lambda u: u.score, default=None)
        bar = f"score>~{top_gold.score:.1f} (top Gold @rank {top_gold.rank})" if top_gold else "score ?"
        legend_str = (f"Legend = top {legend.count} ranks (beat Boss 5 to enter); "
                      f"boss bar {bar}")
    else:
        legend_str = "no Legend league found"

    if me is not None:
        lg = me.league.name if me.league else "?"
        print(f"{me.pseudo or PSEUDO}: rank {me.rank} score {me.score:.1f} {lg} "
              f"| {legend_str} ({total} ranked)")
    else:
        print(f"{PSEUDO} not found in leaderboard | {legend_str} ({total} ranked)")

    # league census (helpful context)
    if lb.leagues:
        census = "  ".join(f"{lg.name}:{lg.count}" for lg in lb.leagues)
        print(f"leagues: {census}")

    if "--top" in sys.argv:
        i = sys.argv.index("--top")
        n = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else 10
        print(f"-- top {n} --")
        for u in sorted(users, key=lambda u: u.rank)[:n]:
            lg = u.league.name if u.league else "?"
            print(f"  #{u.rank:<4} {u.score:6.2f} {lg:7} {u.pseudo}")


if __name__ == "__main__":
    main()
