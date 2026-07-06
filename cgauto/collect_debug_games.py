#!/usr/bin/env python3
"""Collect DEBUG games via TestSession/play, across different maps, and save
maps + per-turn logs + a per-game analysis. Built for studying Boss 5 (Gold→Legend
gate), but works vs any opponent.

Our submitted bot must be the DEBUG build (const DEBUG=true) so its stderr carries
  @TFMAP <w> <h> / @TFMAP <row>...      (the map, turn 1)
  @TFI  P/U ...                          (initial trees / units, turn 1)
  @TFD  <t> <myinv> <oppinv> <trolls>   (per-turn positions + inventories)
  @TFSUM t=.. me=.. opp=.. trees=.. myinv=[..] oppinv=[..] mybuilds=.. oppbuilds=..
TestSession/play returns these in frames[i]['stderr'] (player-0 = our code).

Usage:
  collect_debug_games.py <debug.min.rs> <opponent> <n_games>
     opponent = agentId int  |  -2 (matchmaking)  |  a nickname from cg_play's registry
Saves to  data/boss5_games/<opp>/game_<gameId>.{map,log}  and prints an analysis table.
"""
import sys, os, json, urllib.request, urllib.error, re, time, statistics

TSH = "77167730956ef53402472b3c52474908f5b73026"
SESSION = "/home/tarstars/prj/troll_farm/cgauto/cg_session.txt"
OUTROOT = "/home/tarstars/prj/troll_farm/data/boss5_games"


def cookie():
    ck = []
    for line in open(SESSION):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            n, v = line.split("=", 1)
            if v.strip() and "PASTE" not in v:
                ck.append(f"{n.strip()}={v.strip()}")
    return "; ".join(ck)
COOKIE = cookie()


def play(code, opp, retries=3):
    # opp == "boss" → the league BOSS (Boss 5) via playType (decoded from the IDE's
    # "Play my code" network request: agentsIds [-1,-2] + playType ["IDE_CODE","BOSS"]).
    if opp == "boss":
        multi = {"agentsIds": [-1, -2], "gameOptions": None,
                 "isSoloLeague": False, "playType": ["IDE_CODE", "BOSS"]}
    else:
        multi = {"agentsIds": [-1, opp], "gameOptions": ""}
    body = {"code": code, "programmingLanguageId": "Rust", "multi": multi}
    for att in range(retries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(
                "https://www.codingame.com/services/TestSession/play",
                data=json.dumps([TSH, body]).encode(),
                headers={"Content-Type": "application/json", "Cookie": COOKIE,
                         "User-Agent": "Mozilla/5.0"}), timeout=120)
            js = json.loads(r.read().decode())
            if js.get("scores"):
                return js
            reason = "empty scores"
        except urllib.error.HTTPError as e:
            reason = f"HTTP {e.code}"
        except Exception as e:
            reason = f"{type(e).__name__}"
        if att < retries - 1:
            time.sleep(5)
    print(f"    play failed ({reason})")
    return None


def stderr_of(js):
    """concatenate player-0 stderr across frames."""
    return "\n".join(str(fr.get("stderr", "")) for fr in js.get("frames", []))


def parse_game(js):
    """→ dict: map(list of rows), turns [(t, me, opp, mywood, oppwood, trees)],
    mybuilds, oppbuilds, train_turns {me,opp}."""
    st = stderr_of(js)
    rows = re.findall(r"@TFMAP (.+)", st)
    # first @TFMAP is 'w h'; the rest are grid rows (dedup: only the turn-1 block)
    grid = [r for r in rows if not re.fullmatch(r"\d+ \d+", r)]
    dim = next((r for r in rows if re.fullmatch(r"\d+ \d+", r)), "")
    turns = []
    for m in re.finditer(r"@TFSUM t=(\d+) me=(-?\d+) opp=(-?\d+) trees=(\d+) myinv=\[([\d,]+)\] oppinv=\[([\d,]+)\] mybuilds=(\S*) oppbuilds=(\S*)", st):
        t, me, opp, trees = int(m[1]), int(m[2]), int(m[3]), int(m[4])
        mywood = int(m[5].split(",")[5]); oppwood = int(m[6].split(",")[5])
        turns.append((t, me, opp, mywood, oppwood, trees, m[7], m[8]))
    # training turns: first turn each side shows a 2nd troll in builds
    def first_two(idx):
        for row in turns:
            if row[idx].count(":") >= 2:
                return row[0]
        return None
    return {"dim": dim, "grid": grid, "turns": turns,
            "mybuild": turns[-1][6] if turns else "?",
            "oppbuild": turns[-1][7] if turns else "?",
            "my_train": first_two(6), "opp_train": first_two(7)}


def main():
    code = open(sys.argv[1]).read()
    opp_tok = sys.argv[2] if len(sys.argv) > 2 else "-2"
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    if opp_tok.lower() == "boss":
        opp = "boss"
    else:
        try:
            opp = int(opp_tok)
        except ValueError:
            # allow nicknames from cg_play's registry
            sys.path.insert(0, os.path.dirname(__file__))
            from cg_play import OPPONENTS
            opp = OPPONENTS[opp_tok.lower()]
    outdir = os.path.join(OUTROOT, str(opp))
    os.makedirs(outdir, exist_ok=True)
    print(f"collecting {n} DEBUG games vs agent {opp} → {outdir}\n")

    rows = []
    for i in range(n):
        js = play(code, opp)
        if not js:
            print(f"  game {i+1}/{n}: (failed)"); continue
        gid = js.get("gameId")
        g = parse_game(js)
        won = js["ranks"][0] == 0
        fw = g["turns"][-1] if g["turns"] else None
        mywood = fw[3] if fw else "?"; oppwood = fw[4] if fw else "?"
        # save artifacts
        with open(os.path.join(outdir, f"game_{gid}.map"), "w") as f:
            f.write(g["dim"] + "\n" + "\n".join(g["grid"]) + "\n")
        with open(os.path.join(outdir, f"game_{gid}.log"), "w") as f:
            f.write(f"# gameId {gid}  {'WIN' if won else 'LOSS'}  scores {js['scores']}\n")
            f.write(f"# mybuild {g['mybuild']}  oppbuild {g['oppbuild']}  my_train t{g['my_train']}  opp_train t{g['opp_train']}\n")
            f.write("# t  me  opp  mywood  oppwood  trees\n")
            for r in g["turns"]:
                f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[5]}\n")
        # raw per-frame stderr (preserves @TFMOVE/@TFMAP/@TFD for motion_analyze.py)
        with open(os.path.join(outdir, f"game_{gid}.raw"), "w") as f:
            f.write(stderr_of(js))
        # wood ramp snapshots
        ramp = {t: (mw, ow) for (t, _, _, mw, ow, _, _, _) in g["turns"]}
        snap = lambda t: ramp.get(t, ("-", "-"))
        rows.append((gid, won, mywood, oppwood, g["oppbuild"], g["opp_train"], g["my_train"]))
        print(f"  game {i+1}/{n} {gid}: {'W' if won else 'L'}  wood {mywood}-{oppwood}  "
              f"oppbuild={g['oppbuild']}  opp_train=t{g['opp_train']} my_train=t{g['my_train']}  "
              f"| ramp t75{snap(75)} t150{snap(150)} t225{snap(225)} t300{snap(300)}")
        time.sleep(3)

    if rows:
        wins = sum(r[1] for r in rows)
        mw = statistics.mean(r[2] for r in rows if isinstance(r[2], int))
        ow = statistics.mean(r[3] for r in rows if isinstance(r[3], int))
        builds = {}
        for r in rows:
            builds[r[4]] = builds.get(r[4], 0) + 1
        print(f"\n== {wins}/{len(rows)} wins | our wood {mw:.0f} | opp wood {ow:.0f} ==")
        print(f"   opponent builds seen: {builds}")
        print(f"   artifacts in {outdir}/")


if __name__ == "__main__":
    main()
