#!/usr/bin/env python3
"""The cheap third troll, step 1 (the read) - the per-game facts, from the champion of record's two collected
ladder batches replayed through the fits' exact reconstructor (referee diff as authority, engine as the mirror):

  * batch 41202036 (agent 6667789, `local_claude_1/denial-ablation/games-41202036/`), 160 games;
  * batch 41230202 (agent 6689203, `local_claude_1/ladder-queue/games-41230202/`), 160 games.

Per game it records: the starting draw; the turn the second troll is trained and its talents; the bank before and
after that TRAIN; every bill's deficit (plum/lemon/apple/iron, n = 2, iron waived on an iron-free map as the referee
does) at the post-TRAIN bank and at every later turn (the minimum, and when); items banked by kind per window;
fruit and iron standing within one step of each own troll's cell in turns 20-150 (the pickups that cost a turn), with
the troll's hands and its distance from the shack; wood banked per troll by talents (both seats) per phase; the map's
wood: felled by each side, standing at the end, the turn the last tree fell.

Usage: python3 replay_read.py --raw DIR --agent ID --out JSON    (one batch per call; ~0.2 s a game)
"""
from __future__ import annotations
import argparse, json, sys, collections
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "local_claude_1" / "reconstructions" / "fits"))
import reconstruct as R  # noqa: E402

KINDS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
BILLS = {  # third troll talents (speed, carry, harvest, chop)
    "1/1/0/1": (1, 1, 0, 1), "1/2/0/1": (1, 2, 0, 1), "2/1/0/1": (2, 1, 0, 1), "1/1/0/2": (1, 1, 0, 2),
    "1/2/0/2": (1, 2, 0, 2), "2/2/0/2": (2, 2, 0, 2), "2/3/0/3": (2, 3, 0, 3),
}
PHASES = (("p1_100", 1, 100), ("p101_200", 101, 200), ("p201_250", 201, 250), ("p251_300", 251, 300))
CHECKPOINTS = (50, 100, 150, 200, 250, 300)


def cost(n, t):
    s, c, h, k = t
    return [n + s * s, n + c * c, n + h * h, 0, n + k * k, 0]


def deficit(inv, bill, has_iron):
    """Items short of the bill, by kind (plum, lemon, apple, iron); iron is not charged on an iron-free map."""
    d = [max(0, bill[i] - inv[i]) for i in (0, 1, 2)]
    d.append(max(0, bill[4] - inv[4]) if has_iron else 0)
    return d


def phase_of(t):
    for n, lo, hi in PHASES:
        if lo <= t <= hi:
            return n
    return "p301"


def bfs_from(rows, sources):
    """BFS distance over walkable (grass/tree) cells from a set of source cells (which need not be walkable)."""
    w, h = len(rows[0]), len(rows)
    dist = {}
    q = collections.deque()
    for s in sources:
        dist[s] = 0
        q.append(s)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in dist and rows[ny][nx] not in "~#+01":
                dist[(nx, ny)] = dist[(x, y)] + 1
                q.append((nx, ny))
    return dist


def analyse(path, our_agent):
    gid = int(Path(path).stem)
    r = R.Reconstructor(gid)
    states = r.run(keep_states=True)
    if our_agent == 0:   # any-seat mode (the wider replay set, used only for the per-troll talent table)
        our_agent = r.replay["agents"][0]["agentId"]
    ours = next(a["index"] for a in r.replay["agents"] if a["agentId"] == our_agent)
    theirs = 1 - ours
    rows = r.map["rows"]
    w, h = r.map["w"], r.map["h"]
    shack = None
    iron_cells = set()
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == str(ours):
                shack = (x, y)
            if ch == "+":
                iron_cells.add((x, y))
    has_iron = bool(iron_cells)
    d_shack = bfs_from(rows, [shack])          # distance to the shack (adjacent cell = 1)
    d_iron = bfs_from(rows, iron_cells) if has_iron else {}   # distance to a cell adjacent to iron = 1

    def neigh(c):
        x, y = c
        out = [(x, y)]
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                out.append((nx, ny))
        return out

    out = dict(gameId=gid, our_seat=ours, opp_agent=next(a["agentId"] for a in r.replay["agents"] if a["agentId"] != our_agent),
               opp_name=next((a.get("codingamer") or {}).get("pseudo") for a in r.replay["agents"] if a["agentId"] != our_agent),
               n_turns=r.n_turns, has_iron=has_iron, map_w=w, map_h=h, mismatch=dict(r.mismatch),
               start_inv=list(states[0]["inv"][ours]), final_inv=list(states[-1]["inv"][ours]),
               final_inv_opp=list(states[-1]["inv"][theirs]), final_scores=list(r.replay["scores"]))
    # nearest fruited tree of each kind from the shack at turn 1 (the opening's geography)
    st0 = states[0]
    near0 = {}
    for p in st0["plants"]:
        if p["fruits"] > 0:
            dd = d_shack.get((p["x"], p["y"]))
            if dd is not None:
                near0[p["type"]] = min(near0.get(p["type"], 999), dd)
    out["nearest_fruit_from_shack_t1"] = near0
    out["nearest_iron_from_shack"] = min((d_shack.get(c) for c in (cc for ic in iron_cells for cc in neigh(ic) if cc not in iron_cells) if d_shack.get(c) is not None), default=None) if has_iron else None

    # per-turn walk
    train_turn = None
    second = None
    third_train_turn = None
    banked = collections.defaultdict(lambda: [0] * 6)   # window -> items banked by kind (positive bank deltas)
    banked_opening = [0] * 6
    seeds_used = [0] * 6          # bank decreases after the TRAIN turn (PICK takes a seed from the bank)
    late_verbs = collections.Counter()   # our PLANT/PICK/CHOP counts after the TRAIN turn
    unit_wood = {}       # uid -> dict(talents, player, born, wood, first_turn, wood_by_phase, turns_by_phase)
    encounters = collections.Counter()
    enc_trees = collections.defaultdict(set)
    deficits_min = {b: None for b in BILLS}
    deficits_at = {}
    bank_at = {}
    opp_roster_at = {}
    felled = {"ours": 0, "theirs": 0, "both": 0, "none": 0}   # wood units at fellings, by chopper side
    fell_events = []      # (turn, side, size) for every felling
    opening_verbs = collections.Counter()
    last_tree_fall = None
    pre_roster = None
    for t in range(1, r.n_turns + 1):
        pre, post = states[t - 1], states[t]
        c0, c1 = r.commands(t)
        cmds = c0 if ours == 0 else c1
        drop_units = set()
        for c in cmds:
            p = c.split()
            if p and p[0].upper() == "DROP" and len(p) > 1 and p[1].lstrip("-").isdigit():
                drop_units.add(int(p[1]))
        own_pre = [u for u in pre["units"] if u["player"] == ours]
        if train_turn is None:
            for c in cmds:
                pc = c.split()
                if pc:
                    opening_verbs[pc[0].upper()] += 1
        own_post = [u for u in post["units"] if u["player"] == ours]
        if train_turn is None and len(own_post) >= 2 and len(own_pre) == 1:
            train_turn = t
            new = [u for u in own_post if u["id"] not in {v["id"] for v in own_pre}][0]
            second = (new["ms"], new["cc"], new["hp"], new["chop"])
            out["bank_pre_train"] = list(pre["inv"][ours])
            out["bank_post_train"] = list(post["inv"][ours])
            out["train_turn"] = t
            out["second_troll"] = "%d/%d/%d/%d" % second
            out["second_cost"] = cost(1, second)
        if train_turn is not None and third_train_turn is None and len(own_post) >= 3:
            third_train_turn = t
        if train_turn is not None and t > train_turn:
            for c in cmds:
                pc = c.split()
                if pc and pc[0].upper() in ("PLANT", "PICK"):
                    late_verbs[pc[0].upper()] += 1
            for k in range(6):
                dlt = post["inv"][ours][k] - pre["inv"][ours][k]
                if dlt < 0:
                    seeds_used[k] -= dlt
        # bank deltas (only DROP raises the bank; TRAIN/PICK lower it)
        for k in range(6):
            dlt = post["inv"][ours][k] - pre["inv"][ours][k]
            if dlt > 0:
                if train_turn is None or t <= train_turn:
                    banked_opening[k] += dlt
                else:
                    banked[phase_of(t)][k] += dlt
                    banked["after_train"][k] += dlt
        # bill deficits after the second troll exists
        if train_turn is not None and t >= train_turn:
            inv = post["inv"][ours]
            for b, tal in BILLS.items():
                d = sum(deficit(inv, cost(2, tal), has_iron))
                if deficits_min[b] is None or d < deficits_min[b][0]:
                    deficits_min[b] = (d, t)
        if t in CHECKPOINTS or (train_turn is not None and t == train_turn):
            bank_at[str(t)] = list(post["inv"][ours])
            deficits_at[str(t)] = {b: deficit(post["inv"][ours], cost(2, tal), has_iron) for b, tal in BILLS.items()}
            opp_roster_at[str(t)] = sum(1 for u in post["units"] if u["player"] == theirs)
        # per-troll wood banked (a DROP that lowers the wood carry), both seats
        post_by_id = {u["id"]: u for u in post["units"]}
        for u in pre["units"]:
            rec = unit_wood.get(u["id"])
            if rec is None:
                rec = unit_wood[u["id"]] = dict(talents="%d/%d/%d/%d" % (u["ms"], u["cc"], u["hp"], u["chop"]),
                                               side="ours" if u["player"] == ours else "theirs", born=t, wood=0,
                                               fruit=0, iron=0, turns=0, wood_by_phase=collections.Counter(),
                                               turns_by_phase=collections.Counter())
            rec["turns"] += 1
            rec["turns_by_phase"][phase_of(t)] += 1
            v = post_by_id.get(u["id"])
            if v is not None:
                dw = u["carry"][5] - v["carry"][5]
                if dw > 0:
                    rec["wood"] += dw
                    rec["wood_by_phase"][phase_of(t)] += dw
                df = sum(u["carry"][i] - v["carry"][i] for i in range(4))
                di = u["carry"][4] - v["carry"][4]
                if df > 0 and u["id"] in drop_units and u["player"] == ours:
                    rec["fruit"] += df
                if di > 0 and u["id"] in drop_units and u["player"] == ours:
                    rec["iron"] += di
        # fellings: a plant present pre and absent post -> its size in wood, credited to the side(s) chopping there
        post_pl = {(p["x"], p["y"]) for p in post["plants"]}
        chop_cells = {"ours": set(), "theirs": set()}
        for seat, cl in ((0, c0), (1, c1)):
            by_id = {u["id"]: u for u in pre["units"] if u["player"] == seat}
            for c in cl:
                p = c.split()
                if p and p[0].upper() == "CHOP" and len(p) > 1 and p[1].lstrip("-").isdigit() and int(p[1]) in by_id:
                    uu = by_id[int(p[1])]
                    chop_cells["ours" if seat == ours else "theirs"].add((uu["x"], uu["y"]))
        for p in pre["plants"]:
            c = (p["x"], p["y"])
            if c not in post_pl:
                last_tree_fall = t
                o, th = c in chop_cells["ours"], c in chop_cells["theirs"]
                side = "both" if (o and th) else "ours" if o else "theirs" if th else "none"
                felled[side] += p["size"]
                fell_events.append((t, side, p["size"]))
        # what the trolls pass, turns 20-150: fruit and iron within one step of each own troll's cell
        if 20 <= t <= 150:
            fruited = {}
            for p in pre["plants"]:
                if p["fruits"] > 0:
                    fruited[(p["x"], p["y"])] = (p["type"], p["fruits"])
            for u in own_pre:
                c = (u["x"], u["y"])
                hands = sum(u["carry"])
                role = "starter" if u["hp"] > 0 else "trained"
                empty = "empty" if hands == 0 else "full"
                seen_kind = set()
                for nc in neigh(c):
                    if nc in fruited:
                        kind = fruited[nc][0]
                        seen_kind.add(kind)
                        enc_trees[(role, kind)].add(nc)
                for kind in seen_kind:
                    encounters[(role, empty, kind)] += 1
                    encounters[(role, empty, kind, "dshack_le3" if d_shack.get(c, 99) <= 3 else "dshack_gt3")] += 1
                if has_iron and u["chop"] > 0 and any(nc in iron_cells for nc in neigh(c)[1:]):
                    encounters[(role, empty, "IRON")] += 1
                encounters[(role, empty, "troll_turns")] += 1
    out.update(train_turn=train_turn, second_troll=out.get("second_troll"), third_train_turn=third_train_turn,
               banked_opening=banked_opening, banked={k: v for k, v in banked.items()},
               deficits_min={b: v for b, v in deficits_min.items()}, deficits_at=deficits_at, bank_at=bank_at,
               opp_roster_at=opp_roster_at, felled=felled, fell_events=fell_events, opening_verbs=dict(opening_verbs),
               last_tree_fall=last_tree_fall, seeds_used=seeds_used, late_verbs=dict(late_verbs),
               standing_size_units_end=sum(p["size"] for p in states[-1]["plants"]),
               standing_trees_end=len(states[-1]["plants"]),
               units=[dict(id=k, **{kk: (dict(vv) if isinstance(vv, collections.Counter) else vv) for kk, vv in v.items()})
                      for k, v in unit_wood.items()],
               encounters={"|".join(k): v for k, v in encounters.items()},
               encounter_trees={"|".join(k): len(v) for k, v in enc_trees.items()},
               d_shack_mean_walkable=sum(d_shack.values()) / max(1, len(d_shack)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--agent", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    R.RAW = Path(a.raw)
    games = sorted(Path(a.raw).glob("*.json"))
    if a.limit:
        games = games[: a.limit]
    res = []
    for i, g in enumerate(games):
        res.append(analyse(g, a.agent))
        if (i + 1) % 40 == 0:
            print(f"{i + 1}/{len(games)}", file=sys.stderr)
    json.dump({"raw": a.raw, "agent": a.agent, "games": res}, open(a.out, "w"), indent=1, sort_keys=True)
    print(f"wrote {a.out}: {len(res)} games")


if __name__ == "__main__":
    main()
