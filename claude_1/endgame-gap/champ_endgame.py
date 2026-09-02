#!/usr/bin/env python3
"""Track E, deliverables 1-3 on the champion's side: the 160 collected ladder games of the champion of
record (submission 41202036, agent 6667789; `local_claude_1/denial-ablation/games-41202036/`), replayed
through the fits' exact reconstructor (`local_claude_1/reconstructions/fits/reconstruct.py`, referee
diff as authority) so every turn has positions, carries, trees and inventories.

Per game and seat (ours = the replay's agent 6667789; theirs = the opponent):
  * the command mix by phase (verbs per turn, roster per turn from the state);
  * for turns 251-300, per own troll per turn, what it does: HARVEST on a cell, CHOP, DROP, PLANT/PICK/
    MINE, MOVE (and whether the MOVE oscillates: same cell as two turns ago), or NO COMMAND (WAIT/idle),
    with the idle case split by whether any usable tree is reachable (BFS over non-water, non-rock cells:
    fruit on a tree for a harvester with free capacity, or a living tree for a chopper);
  * score at turns 250 and 300 for both seats (score = fruit in the shack + 4 x wood), so the last fifty
    turns' gain can be split by who led at turn 250.
The replays are read from a scratch copy (`--raw`), written by the caller from the jsonl.gz; nothing is
copied into the worktree.
"""
from __future__ import annotations
import argparse, json, os, sys, collections
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]            # the worktree root (has sim/)
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "local_claude_1" / "reconstructions" / "fits"))
import reconstruct as R                                   # noqa: E402

PHASES = (("p1_100", 1, 100), ("p101_200", 101, 200), ("p201_250", 201, 250), ("p251_300", 251, 300))
VERBS = ("MOVE", "HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE", "TRAIN")
OUR_AGENT = 6667789


def phase_of(t):
    for n, lo, hi in PHASES:
        if lo <= t <= hi:
            return n


def score(inv):
    return inv[0] + inv[1] + inv[2] + inv[3] + 4 * inv[5]


def parse_cmds(cmds):
    """split_cmds output -> list of (verb, unit or None, args)."""
    out = []
    for c in cmds:
        toks = c.split()
        if not toks:
            continue
        v = toks[0].upper()
        if v == "MSG" or v == "WAIT":
            out.append((v, None, toks[1:]))
        elif v == "TRAIN":
            out.append((v, None, toks[1:]))
        elif len(toks) >= 2 and toks[1].lstrip("-").isdigit():
            out.append((v, int(toks[1]), toks[2:]))
        else:
            out.append((v, None, toks[1:]))
    return out


def reachable(rows, start):
    w, h = len(rows[0]), len(rows)
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen and rows[ny][nx] not in "~#+":
                seen.add((nx, ny))
                stack.append((nx, ny))
    return seen


def analyse(game_path):
    gid = int(Path(game_path).stem)
    r = R.Reconstructor(gid)
    states = r.run(keep_states=True)
    ours = next(a["index"] for a in r.replay["agents"] if a["agentId"] == OUR_AGENT)
    rows = r.map["rows"]
    out = {"gameId": gid, "our_seat": ours, "opp_agent": next(a["agentId"] for a in r.replay["agents"] if a["agentId"] != OUR_AGENT),
           "n_turns": r.n_turns, "mix": {}, "late": collections.Counter(), "examples": [], "score": {}}
    # states[t-1] is the pre-turn state of turn t (states appended before step)
    pos_hist = collections.defaultdict(list)   # unit -> [(t, (x,y))]
    for t in range(1, r.n_turns + 1):
        st = states[t - 1]
        c0, c1 = r.commands(t)
        for seat, cmds in ((0, c0), (1, c1)):
            who = "ours" if seat == ours else "theirs"
            ph = phase_of(t)
            m = out["mix"].setdefault(who, {}).setdefault(ph, collections.Counter())
            parsed = parse_cmds(cmds)
            units = [u for u in st["units"] if u["player"] == seat]
            m["turns"] += 1
            m["roster"] += len(units)
            cmd_by_unit = {}
            for v, uid, args in parsed:
                if v in VERBS:
                    m[v] += 1
                if uid is not None:
                    cmd_by_unit[uid] = (v, args)
            m["active_units"] += len(cmd_by_unit)
            if not cmd_by_unit:
                m["noop_turns"] += 1
            if who == "ours":
                for u in units:
                    pos_hist[u["id"]].append((t, (u["x"], u["y"])))
            if who == "ours" and t >= 251:
                for u in units:
                    v, args = cmd_by_unit.get(u["id"], ("NONE", []))
                    key = v
                    if v == "MOVE":
                        h = pos_hist[u["id"]]
                        if len(h) >= 3 and h[-1][1] == h[-3][1] and h[-1][1] != h[-2][1]:
                            key = "MOVE_oscillating"
                    if v == "NONE":
                        reach = reachable(rows, (u["x"], u["y"]))
                        free = u["cc"] - sum(u["carry"])
                        usable = False
                        for p in st["plants"]:
                            if (p["x"], p["y"]) not in reach or p["health"] <= 0:
                                continue
                            if (u["hp"] > 0 and free > 0 and p["fruits"] > 0) or (u["chop"] > 0 and free > 0):
                                usable = True
                                break
                        key = "NONE_usable_tree_reachable" if usable else "NONE_nothing_usable"
                        if not usable and sum(u["carry"]) > 0:
                            key = "NONE_carrying_not_banked"
                    out["late"][key] += 1
                    if key in ("MOVE_oscillating", "NONE_usable_tree_reachable", "NONE_nothing_usable", "NONE_carrying_not_banked") and len(out["examples"]) < 6:
                        out["examples"].append({"turn": t, "unit": u["id"], "cell": [u["x"], u["y"]], "what": key,
                                                "carry": u["carry"], "talents": [u["ms"], u["cc"], u["hp"], u["chop"]]})
    for t in (250, 300):
        if t <= r.n_turns:
            st = states[t - 1] if t < r.n_turns else None
        # score after turn t = inventories after step t; the reconstructor's post-run game holds the final
    # scores at turn 250 (pre-turn state of turn 251) and final
    s250 = states[250] if len(states) > 250 else states[-1]
    final = r.snapshot(r.n_turns + 1)
    out["score"] = {"ours_250": score(s250["inv"][ours]), "theirs_250": score(s250["inv"][1 - ours]),
                    "ours_end": score(final["inv"][ours]), "theirs_end": score(final["inv"][1 - ours]),
                    "ours_ladder": r.agents[ours]["score"], "theirs_ladder": r.agents[1 - ours]["score"]}
    out["mismatch"] = dict(r.mismatch)
    out["late"] = dict(out["late"])
    for who in out["mix"]:
        for ph in out["mix"][who]:
            out["mix"][who][ph] = dict(out["mix"][who][ph])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="/data/scratch/claude1-champ-41202036")
    ap.add_argument("--out", default="claude_1/endgame-gap/champ-endgame.json")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    R.RAW = Path(a.raw)
    games = sorted(Path(a.raw).glob("*.json"))
    if a.limit:
        games = games[: a.limit]
    res = []
    for i, g in enumerate(games, 1):
        try:
            res.append(analyse(g))
        except Exception as e:  # keep going, report at the end
            res.append({"gameId": int(g.stem), "error": repr(e)})
        if i % 20 == 0:
            print(f"{i}/{len(games)}", flush=True)
    json.dump({"raw": a.raw, "games": res}, open(a.out, "w"), indent=1, sort_keys=True)
    ok = [g for g in res if "error" not in g]
    print("games", len(res), "ok", len(ok), "errors", [g["gameId"] for g in res if "error" in g][:5])
    agg = collections.defaultdict(collections.Counter)
    late = collections.Counter()
    for g in ok:
        for who in g["mix"]:
            for ph, m in g["mix"][who].items():
                agg[(who, ph)].update(m)
                agg[(who, ph)]["games"] += 1
        late.update(g["late"])
    for (who, ph), m in sorted(agg.items()):
        t = m["turns"]
        print(f"{who:6s} {ph:9s} games {m['games']:4d} turns {t:6d} roster/turn {m['roster']/t:.2f} active/turn {m['active_units']/t:.2f} "
              f"noop {m['noop_turns']/t:.3f} | " + " ".join(f"{v[:4]} {m[v]/t:.2f}" for v in VERBS) + f" | MOVE/game {m['MOVE']/m['games']:.1f}")
    tot = sum(late.values())
    print("late troll-turns (ours, 251-300):", tot)
    for k, v in late.most_common():
        print(f"  {k:28s} {v:6d} {v/tot:6.1%}")
    led = [g for g in ok if g["score"]["ours_250"] > g["score"]["theirs_250"]]
    trailed = [g for g in ok if g["score"]["ours_250"] <= g["score"]["theirs_250"]]
    for name, grp in (("led at 250", led), ("trailed/tied at 250", trailed), ("all", ok)):
        if not grp:
            continue
        og = sum(g["score"]["ours_end"] - g["score"]["ours_250"] for g in grp) / len(grp)
        tg = sum(g["score"]["theirs_end"] - g["score"]["theirs_250"] for g in grp) / len(grp)
        wins = sum(1 for g in grp if g["score"]["ours_end"] > g["score"]["theirs_end"])
        print(f"{name:20s} n {len(grp):3d}  our gain 251-300 {og:6.1f}  their gain {tg:6.1f}  our final wins {wins}")


if __name__ == "__main__":
    main()
