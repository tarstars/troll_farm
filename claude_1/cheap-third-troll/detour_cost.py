#!/usr/bin/env python3
"""The cost of the smallest dedicated detour, costed on each game's own board.

From the exact state right after the second troll is trained (the reconstructor's post-TRAIN snapshot), a greedy trip
model collects a bill's shortfall: the collector walks (BFS over grass, one cell a turn at speed 1, two at speed 2) to the
nearest tree of a needed kind that carries fruit, HARVESTs one (only a troll with harvest power can - the champion's
trained troll has none, so fruit is the starter's job), walks back to the shack's nearest neighbour cell, DROPs, and
repeats; iron is mined from a cell orthogonally adjacent to an iron cell (MINE takes min(chop, free carry)). A tree's
fruit supply follows the referee's tick (`Plant.tick`): the cooldown counts down, and at zero a tree below size 4 grows
a size, else below 3 fruits it gains a fruit, then the cooldown resets to the type's base (PLUM/LEMON 8, APPLE 9, BANANA 6)
less the water bonus (5/5/7/2) when a water cell touches the tree; so a trip can target a tree that will have regrown by
the time the collector arrives (the model waits there if it must). Opponents' harvests and fellings are not modelled. Two collector plans are costed for every bill:
  * `starter_all`  - the starter (1/1/1/1) collects everything, one item a trip;
  * `split`        - the starter collects the fruit, the trained troll mines the iron (two a trip when chop >= 2).
The model is calibrated against the champion's own opening: from the turn-1 state, the same greedy walk for the second
troll's actual shortfall is compared with the turn the champion really trained (203 games with a non-zero shortfall).

Usage: python3 detour_cost.py --raw DIR --agent ID --out JSON
"""
from __future__ import annotations
import argparse, json, sys, collections
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "local_claude_1" / "reconstructions" / "fits"))
import reconstruct as R  # noqa: E402

BILLS = {"1/1/0/1": (1, 1, 0, 1), "1/2/0/1": (1, 2, 0, 1), "2/1/0/1": (2, 1, 0, 1), "1/1/0/2": (1, 1, 0, 2),
         "1/2/0/2": (1, 2, 0, 2), "2/2/0/2": (2, 2, 0, 2)}
KIND_IDX = {"PLUM": 0, "LEMON": 1, "APPLE": 2, "BANANA": 3}


def cost(n, t):
    s, c, h, k = t
    return [n + s * s, n + c * c, n + h * h, 0, n + k * k, 0]


def bfs(rows, sources, w, h):
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


class Board:
    def __init__(self, rows, w, h, shack):
        self.rows, self.w, self.h, self.shack = rows, w, h, shack
        self.iron_adj = set()
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == "+":
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h and rows[ny][nx] not in "~#+01":
                            self.iron_adj.add((nx, ny))
        self.d_shack = bfs(rows, [shack], w, h)     # shack neighbour cells are at 1
        self._cache = {}

    def dist_from(self, c):
        if c not in self._cache:
            self._cache[c] = bfs(self.rows, [c], self.w, self.h)
        return self._cache[c]


def walk_turns(d, speed):
    return -(-d // speed)   # ceil


def trips(board, start, plants, need, speed, carry, chop, can_harvest):
    """Greedy: collect `need` (dict kind->count, 'IRON' allowed) from `start`; returns (turns, log) or (None, why)."""
    need = dict(need)
    pos = start
    turns = 0
    log = []
    for tree in (t for ts in plants.values() for t in ts):
        tree.taken = 0
    while any(v > 0 for v in need.values()):
        d = board.dist_from(pos)
        best = None   # (arrival time incl. wait, kind, cell, tree)
        for kind, n in need.items():
            if n <= 0:
                continue
            if kind == "IRON":
                if chop <= 0:
                    return None, "no chop power for iron"
                for c in board.iron_adj:
                    if c in d:
                        arr = turns + walk_turns(d[c], speed)
                        if best is None or arr < best[0]:
                            best = (arr, kind, c, None)
            else:
                if not can_harvest:
                    return None, "no harvest power for fruit"
                for tree in plants.get(kind, []):
                    c = tree.cell
                    if c in d:
                        arr = tree.ready_at(turns + walk_turns(d[c], speed))
                        if arr is not None and (best is None or arr < best[0]):
                            best = (arr, kind, c, tree)
        if best is None:
            return None, "nothing reachable"
        arr, kind, c, tree = best
        dd = d[c]
        turns = arr
        pos = c
        if kind == "IRON":
            got = min(chop, carry, need[kind])
            turns += 1
            need[kind] -= got
        else:
            turns += 1          # HARVEST one (harvest power 1)
            tree.taken += 1
            need[kind] -= 1
        # back to the shack and drop
        dsh = board.d_shack.get(pos)
        if dsh is None:
            return None, "shack unreachable"
        turns += walk_turns(dsh - 1, speed) + 1
        log.append((kind, dd, dsh))
        # the drop cell: the shack neighbour on the way; approximate the next start as the nearest shack neighbour
        pos = min((cc for cc in board.d_shack if board.d_shack[cc] == 1), key=lambda cc: board.dist_from(pos).get(cc, 999))
    return turns, log


BASE_CD = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
WATER_BONUS = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}


def near_water(rows, x, y):
    w, h = len(rows[0]), len(rows)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and rows[ny][nx] == "~":
            return True
    return False


class Tree:
    """Fruit available at time tau (turns from the snapshot), by the referee's tick rule, less what the model took."""

    def __init__(self, p, rows):
        self.cell = (p["x"], p["y"])
        self.kind = p["type"]
        self.size, self.fruits0, self.cd0 = p["size"], p["fruits"], p["cooldown"]
        self.cd = BASE_CD[self.kind] - (WATER_BONUS[self.kind] if near_water(rows, p["x"], p["y"]) else 0)
        self.taken = 0

    def fruits_at(self, tau):
        if tau < self.cd0:
            ticks = 0
        else:
            ticks = 1 + (tau - self.cd0) // max(1, self.cd)
        grow = max(0, 4 - self.size)
        fruit_ticks = max(0, ticks - grow)
        return min(3, self.fruits0 + fruit_ticks) - self.taken

    def ready_at(self, tau):
        """Earliest time >= tau with a fruit available, or None within 300 turns."""
        for t in range(tau, tau + 300):
            if self.fruits_at(t) > 0:
                return t
        return None


def plants_of(state, rows):
    out = collections.defaultdict(list)
    for p in state["plants"]:
        out[p["type"]].append(Tree(p, rows))
    return out


def analyse(path, our_agent):
    gid = int(Path(path).stem)
    r = R.Reconstructor(gid)
    states = r.run(keep_states=True)
    ours = next(a["index"] for a in r.replay["agents"] if a["agentId"] == our_agent)
    rows, w, h = r.map["rows"], r.map["w"], r.map["h"]
    shack = next((x, y) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == str(ours))
    has_iron = any("+" in row for row in rows)
    board = Board(rows, w, h, shack)
    out = dict(gameId=gid, has_iron=has_iron)
    # locate the TRAIN turn
    train_turn = None
    for t in range(1, r.n_turns + 1):
        if sum(1 for u in states[t]["units"] if u["player"] == ours) >= 2:
            train_turn = t
            break
    out["train_turn"] = train_turn
    if train_turn is None:
        return out
    pre, post = states[train_turn - 1], states[train_turn]
    new = [u for u in post["units"] if u["player"] == ours and u["hp"] == 0]
    starter = next(u for u in post["units"] if u["player"] == ours and u["hp"] > 0)
    second = new[0]
    sec_t = (second["ms"], second["cc"], second["hp"], second["chop"])
    # calibration: from turn 1, the second troll's actual shortfall, walked by the starter from its turn-1 cell
    st1 = states[0]
    inv1 = st1["inv"][ours]
    c1 = cost(1, sec_t)
    need1 = {"PLUM": max(0, c1[0] - inv1[0]), "LEMON": max(0, c1[1] - inv1[1]), "APPLE": max(0, c1[2] - inv1[2])}
    if has_iron:
        need1["IRON"] = max(0, c1[4] - inv1[4])
    s1 = next(u for u in st1["units"] if u["player"] == ours)
    out["calib"] = dict(second="%d/%d/%d/%d" % sec_t, need=need1, items=sum(need1.values()), actual_train_turn=train_turn)
    if sum(need1.values()) > 0:
        tt, lg = trips(board, (s1["x"], s1["y"]), plants_of(st1, rows), need1, 1, 1, 1, True)
        out["calib"]["model_turns"] = tt
        out["calib"]["model_log"] = lg
    # the bills, from the post-TRAIN state
    inv = post["inv"][ours]
    out["bills"] = {}
    pl = plants_of(post, rows)
    for name, tal in BILLS.items():
        c = cost(2, tal)
        need = {"PLUM": max(0, c[0] - inv[0]), "LEMON": max(0, c[1] - inv[1]), "APPLE": max(0, c[2] - inv[2])}
        if has_iron:
            need["IRON"] = max(0, c[4] - inv[4])
        rec = dict(need=need, items=sum(need.values()))
        # starter collects everything, from where it stands after the TRAIN turn
        tt, lg = trips(board, (starter["x"], starter["y"]), pl, need, 1, 1, 1, True)
        rec["starter_all"] = tt
        rec["starter_all_log"] = lg
        # split: starter the fruit, the trained troll the iron (from the shack's neighbour; it spawns on the shack)
        fruit_need = {k: v for k, v in need.items() if k != "IRON"}
        tf, lf = trips(board, (starter["x"], starter["y"]), pl, fruit_need, 1, 1, 1, True) if sum(fruit_need.values()) else (0, [])
        iron_need = {"IRON": need.get("IRON", 0)}
        sp = min((cc for cc in board.d_shack if board.d_shack[cc] == 1), key=lambda cc: cc)
        ti, li = trips(board, sp, pl, iron_need, second["ms"], second["cc"], second["chop"], False) if iron_need["IRON"] else (0, [])
        rec["split_starter_fruit"] = tf
        rec["split_trained_iron"] = ti
        rec["split_wall"] = max(tf, ti) if (tf is not None and ti is not None) else None
        out["bills"][name] = rec
    # the other order: the cheap troll first, at turn 1 (2/2/1/2 at n = 1 - every Legend draw covers it), then the
    # champion's actual second troll at n = 2; the starter harvests the fruit, the cheap troll mines the iron
    cheap = cost(1, (1, 1, 0, 1))
    left = [inv1[k] - cheap[k] for k in range(6)]
    c2 = cost(2, sec_t)
    need2 = {"PLUM": max(0, c2[0] - left[0]), "LEMON": max(0, c2[1] - left[1]), "APPLE": max(0, c2[2] - left[2])}
    if has_iron:
        need2["IRON"] = max(0, c2[4] - left[4])
    cf = dict(cheap_affordable_t1=all(inv1[k] >= cheap[k] for k in (0, 1, 2)) and (not has_iron or inv1[4] >= cheap[4]),
              need=need2, items=sum(need2.values()))
    fruit_need = {k: v for k, v in need2.items() if k != "IRON"}
    tf, lf = trips(board, (s1["x"], s1["y"]), plants_of(st1, rows), fruit_need, 1, 1, 1, True) if sum(fruit_need.values()) else (0, [])
    sp = min((cc for cc in board.d_shack if board.d_shack[cc] == 1), key=lambda cc: cc)
    ti, li = trips(board, sp, plants_of(st1, rows), {"IRON": need2.get("IRON", 0)}, 1, 1, 1, False) if need2.get("IRON", 0) else (0, [])
    ta, la = trips(board, (s1["x"], s1["y"]), plants_of(st1, rows), need2, 1, 1, 1, True) if sum(need2.values()) else (0, [])
    cf.update(starter_fruit=tf, cheap_iron=ti, wall=max(tf, ti) if (tf is not None and ti is not None) else None, starter_all=ta)
    out["cheap_first"] = cf
    out["end_of_chopping"] = r.n_turns
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
    res = [analyse(g, a.agent) for g in games]
    json.dump({"raw": a.raw, "agent": a.agent, "games": res}, open(a.out, "w"), indent=1, sort_keys=True)
    print(f"wrote {a.out}: {len(res)} games")


if __name__ == "__main__":
    main()
