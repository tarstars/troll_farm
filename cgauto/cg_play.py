#!/usr/bin/env python3
"""Run CONTROLLED games via CodinGame's TestSession/play ("Play my code") — no ladder
wait. Plays a FIXED opponent repeatedly and reports win-rate + avg wood (ours & opp).

Why: ladder wood reads are confounded by placement (a fresh agent plays weak opponents,
so both bank low wood). This plays the SAME strong opponent every game → clean signal.

Opponent selection (SOLVED 2026-07-05): pass a specific player's agentId as the opponent.
`multi.agentsIds = [-1, <agentId>]` where -1 = our IDE code (player 0) and <agentId> = a
frozen snapshot of that player's submitted bot. A valid agentId yields a real 2-player game
with scores; an invalid one yields an empty game (that's how we proved it's consumed).
agentId -2 = random matchmaking. The arena Boss is NOT exposed as a selectable agentId by
any endpoint we found, so we use a strong fixed top-Gold player as a Boss-5 proxy instead.
agentIds below were pulled from our Gold ladder battle history; they're stable until that
player resubmits (which just means: pick another from --list).

Usage:
  cg_play.py <code.min.rs> [n_games] [opponent]
     opponent = a nickname from the registry, a raw agentId (int), or "random" (-2).
     default = RunninglVlan (our most-faced Gold opponent).
  cg_play.py --list          # show the known-opponent registry
"""
import sys, json, urllib.request, urllib.error, re, statistics, time

PID = "spring-challenge-2026-troll-farm"
TSH = "77167730956ef53402472b3c52474908f5b73026"  # our test session handle
SESSION = "/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"

# Known strong, FIXED opponents (agentId = frozen snapshot of that player's bot), pulled
# from our Gold ladder battle history 2026-07-05. All are strong/elite CG players → good
# Boss-5-strength proxies. Find more with cgauto/cg_battles helper or the battles endpoint.
OPPONENTS = {
    "runninglvlan": 6481102,  # most-faced (x9) — DEFAULT
    "darkhorse64":  6480808,  # elite (validated: real game)
    "homnibus":     6479641,
    "biz1":         6481132,
    "msmits":       6481223,
    "nep7un":       6481112,
    "wazemo":       6527338,
    "nmahoude":     6480842,
    "eagleast":     6480801,
    "pbou":         6536593,
    "random":       -2,       # CG matchmaking (varies game-to-game)
}
DEFAULT_OPP = OPPONENTS["runninglvlan"]


def cookie():
    ck = []
    for line in open(SESSION):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            n, v = line.split("=", 1); n, v = n.strip(), v.strip()
            if v and "PASTE" not in v:
                ck.append(f"{n}={v}")
    return "; ".join(ck)
COOKIE = cookie()


def call(svc, m, payload, timeout=90):
    r = urllib.request.urlopen(urllib.request.Request(
        f"https://www.codingame.com/services/{svc}/{m}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Cookie": COOKIE, "User-Agent": "Mozilla/5.0"}),
        timeout=timeout)
    return r.status, r.read().decode()


def resolve_opp(tok):
    """nickname | 'random' | raw agentId int -> agentId."""
    t = str(tok).strip().lower()
    if t in OPPONENTS:
        return OPPONENTS[t]
    return int(tok)


def final_wood(frames, idx):
    """Wood banked by player `idx` at the last frame. inputmodule = '<p0>\\n<p1>' where each
    line is 'plum lemon apple banana iron wood' (wood = field 5)."""
    for f in reversed(frames):
        m = re.search(r'"inputmodule":"([^"]+)"', f.get("view") or "")
        if m:
            lines = m.group(1).split("\\n")
            if len(lines) > idx:
                parts = lines[idx].split()
                if len(parts) > 5:
                    try:
                        return int(parts[5])
                    except ValueError:
                        return None
    return None


def play(code, opp, retries=3):
    """One controlled game vs agentId `opp`. Returns parsed dict or None. Retries transient
    failures and degenerate games (empty scores = opponent agent failed to load)."""
    body = {"code": code, "programmingLanguageId": "Rust",
            "multi": {"agentsIds": [-1, opp], "gameOptions": ""}}
    for attempt in range(retries):
        try:
            st, raw = call("TestSession", "play", [TSH, body])
            if st == 200:
                js = json.loads(raw)
                if js.get("scores"):           # non-empty => a real, completed game
                    return js
                reason = "degenerate (empty scores)"
            else:
                reason = f"HTTP {st}: {raw[:120]}"
        except urllib.error.HTTPError as e:
            reason = f"HTTPError {e.code}: {e.read().decode()[:120]}"
        except Exception as e:
            reason = f"{type(e).__name__}: {str(e)[:120]}"
        if attempt < retries - 1:
            print(f"    retry {attempt+1}/{retries} ({reason})", flush=True)
            time.sleep(3)
    print(f"    FAILED after {retries} tries ({reason})", flush=True)
    return None


def main():
    if not sys.argv[1:] or sys.argv[1] in ("-h", "--help"):
        print(__doc__); return
    if sys.argv[1] == "--list":
        print("known opponents (agentId = frozen bot snapshot):")
        for k, v in OPPONENTS.items():
            print(f"  {k:<14} {v}")
        print(f"default = {DEFAULT_OPP} (runninglvlan)")
        return

    code = open(sys.argv[1]).read()
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    opp = resolve_opp(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_OPP
    opp_name = next((k for k, v in OPPONENTS.items() if v == opp), str(opp))

    print(f"code={sys.argv[1].split('/')[-1]}  opponent={opp_name} (agentId {opp})  games={n}\n", flush=True)
    wins = 0; played = 0; woods = []; oppwoods = []; my_scores = []; opp_scores = []
    for i in range(n):
        r = play(code, opp)
        if not r:
            print(f"  game {i+1}/{n}: (no result)", flush=True)
            continue
        played += 1
        won = r["ranks"][0] == 0            # our code is always player index 0
        wins += won
        ms, os_ = r["scores"][0], r["scores"][1]
        my_scores.append(ms); opp_scores.append(os_)
        w = final_wood(r["frames"], 0); ow = final_wood(r["frames"], 1)
        if w is not None: woods.append(w)
        if ow is not None: oppwoods.append(ow)
        print(f"  game {i+1}/{n}: {'W' if won else 'L'}  score {ms:.0f}-{os_:.0f}  "
              f"wood {w}-{ow}  gameId={r['gameId']}", flush=True)

    if played:
        wr = 100 * wins / played
        woodline = (f"our wood {statistics.mean(woods):.0f}" if woods else "our wood n/a")
        owoodline = (f"opp wood {statistics.mean(oppwoods):.0f}" if oppwoods else "opp wood n/a")
        print(f"\n== vs {opp_name}: {wins}/{played} wins ({wr:.0f}%) | {woodline} | {owoodline} "
              f"| our score {statistics.mean(my_scores):.0f} ==", flush=True)
    else:
        print("\n== no games completed ==", flush=True)


if __name__ == "__main__":
    main()
