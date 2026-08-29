#!/usr/bin/env python3
"""profile_bot.py -- behaviour profile of one Troll Farm player, measured from the corpus.

Usage
  python3 profile_bot.py --player delineate                       # all agent ids of that pseudo
  python3 profile_bot.py --player Bubaptik --agent 6568138        # one id of that pseudo
  python3 profile_bot.py --agent 6665150 --label tass             # explicit id(s), label for the files
  python3 profile_bot.py --compare a.json b.json ...              # side-by-side table of finished profiles
Options: --out DIR (default: this file's directory), --limit N (first N games, for tests),
         --summary FILE (plain-words text pasted at the top of the .md), --data DIR.

Data (all read-only, main checkout /home/tarstars/prj/troll_farm/data):
  processed/games.jsonl          game selection, map, initial trees/trolls, scores, referee tallies
  raw/games/<gameId>.json        the replay: both players' commands per turn, the referee's per-turn
                                 summaries ("troll 3 moved to (10, 5)", "planted a PLUM", "damaged a
                                 tree", "harvested 2 LEMONs", "[failed] ...") and the viewer diff
                                 (new trolls with talents, new trees with cell/type, tree health/stage,
                                 death = health 0).  Positions and effects are therefore EXACT.
  processed/turns.jsonl.gz       commands only; used for a game whose raw replay is missing.  Then a
                                 troll's position is SIMULATED from its MOVE targets (BFS over grass,
                                 deterministic tie-break) and trees are tracked from PLANT commands with
                                 a crude health model (no growth) -- positions agree with the exact path
                                 for step-wise movers, but tree origin/type at a chop comes out 'none'
                                 for about half the chops; flagged in the output (position_source).
  Validation (2026-08-28): on the raw path, per-game wood / successful plants / iron / trolls agree with
  the referee tallies stored in games.jsonl for 848/848 seat-games of the four top players.
  processed/maps.jsonl           map by hash; used only if a game record carries no map.

Output: <out>/<label>.json (every number) and <out>/<label>.md (tables, n everywhere).
"""
import argparse
import glob
import gzip
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict, deque

DATA_DEFAULT = "/home/tarstars/prj/troll_farm/data"
ITEMS = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"]
FRUITS = ITEMS[:4]
TYPE36 = {0: "PLUM", 1: "LEMON", 2: "APPLE", 3: "BANANA"}
VERBS = ("MOVE", "HARVEST", "CHOP", "DROP", "MINE", "PLANT", "PICK", "TRAIN", "WAIT", "MSG")
UNIT_VERBS = ("MOVE", "HARVEST", "CHOP", "DROP", "MINE", "PLANT", "PICK")
ACTION_VERBS = ("HARVEST", "CHOP", "DROP", "MINE", "PLANT", "PICK")
LETTER = {"MOVE": "M", "HARVEST": "H", "CHOP": "C", "DROP": "D", "MINE": "I", "PLANT": "P",
          "PICK": "K", "TRAIN": "T", "WAIT": "W", "MSG": "", "OTHER": "?"}
TALENT_NAMES = ("speed", "carry", "harvest", "chop")
MAX_SIZE = 4
HEALTH_BASE = {"PLUM": 4, "LEMON": 4, "APPLE": 8, "BANANA": 2}
HEALTH_SLOPE = {"PLUM": 2, "LEMON": 2, "APPLE": 3, "BANANA": 1}
BUCKET = 10          # turns per bucket in the timelines
ENDGAME = 30         # "last 30 turns"
OPENING = 30         # "first 30 turns"


# ----------------------------------------------------------------------------- helpers

def b36(c):
    return int(c, 36)


def stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    xs = sorted(xs)
    q = statistics.quantiles(xs, n=4) if len(xs) >= 2 else [xs[0], xs[0], xs[0]]
    return {"n": len(xs), "mean": round(statistics.fmean(xs), 2), "median": statistics.median(xs),
            "p25": q[0], "p75": q[2], "min": xs[0], "max": xs[-1]}


def share_table(counter, total=None, top=None):
    total = total if total is not None else sum(counter.values())
    rows = counter.most_common(top)
    return [{"key": (list(k) if isinstance(k, tuple) else k), "n": n,
             "share": (round(n / total, 3) if total else None)} for k, n in rows]


def bucket_of(turn):
    return (turn - 1) // BUCKET


def phase_of(turn):
    return "early(1-100)" if turn <= 100 else ("mid(101-200)" if turn <= 200 else "late(201-300)")


# ----------------------------------------------------------------------------- command parsing
# identical rules to scripts/extract_turns.py so that the raw and the turns.jsonl.gz paths agree

def parse_command(cmd):
    parts = cmd.split()
    verb = parts[0].upper()
    if verb == "MSG":
        return {"verb": "MSG", "unit": None, "args": [], "msg": cmd.split(None, 1)[1] if len(parts) > 1 else ""}
    unit, args = None, parts[1:]
    if verb in UNIT_VERBS and args and args[0].lstrip("-").isdigit():
        unit = int(args[0])
        args = args[1:]
    return {"verb": verb if verb in VERBS else "OTHER", "unit": unit, "args": args}


def parse_stdout(so):
    out = []
    for chunk in so.replace("\n", ";").split(";"):
        chunk = chunk.strip()
        if chunk:
            out.append(parse_command(chunk))
    return out


# ----------------------------------------------------------------------------- raw replay parsing

RE_LINE = re.compile(r"^\$([01]):?\s*(.*)$")
RE_MOVED = re.compile(r"troll (\d+) moved to \((\d+), (\d+)\)")
RE_DAMAGED = re.compile(r"troll (\d+) damaged a tree")
RE_DROPPED = re.compile(r"troll (\d+) dropped (\d+) items? to the shack")
RE_COLLECTED = re.compile(r"troll (\d+) collected (\d+) (WOOD|IRON)")
RE_PLANTED = re.compile(r"troll (\d+) planted a (\w+)")
RE_HARVESTED = re.compile(r"troll (\d+) harvested (\d+) (PLUM|LEMON|APPLE|BANANA)")
RE_PICKED = re.compile(r"troll (\d+) picked (\d+) (\w+)")
RE_FAILED_UNIT = re.compile(r"[Tt]roll (\d+)")

FAIL_KINDS = [("can't move", "move_blocked"), ("no fruits", "harvest_no_fruit"), ("already used", "unit_reused"),
              ("cell blocked", "train_cell_blocked"), ("can't afford", "train_unaffordable"),
              ("not at a plant", "not_at_a_plant"), ("can't pick", "pick_out_of_stock"),
              ("does not exist", "no_such_troll")]


def parse_summary(text):
    """-> list of events {p, kind, unit, n, item, x, y}."""
    ev = []
    for line in text.split("\n"):
        if not line:
            continue
        m = RE_LINE.match(line)
        if not m:
            continue
        p, msg = int(m.group(1)), m.group(2)
        if msg.startswith("[failed]"):
            kind = "failed_other"
            for needle, k in FAIL_KINDS:
                if needle in msg:
                    kind = k
                    break
            mu = RE_FAILED_UNIT.search(msg)
            ev.append({"p": p, "kind": "failed", "sub": kind, "unit": int(mu.group(1)) if mu else None})
            continue
        if "exceeded the time limit" in msg or msg.strip() == "timeout":
            ev.append({"p": p, "kind": "timeout"})
            continue
        mm = RE_MOVED.search(msg)
        if mm:
            ev.append({"p": p, "kind": "moved", "unit": int(mm.group(1)), "x": int(mm.group(2)), "y": int(mm.group(3))})
            continue
        mm = RE_DAMAGED.search(msg)
        if mm:
            ev.append({"p": p, "kind": "damaged", "unit": int(mm.group(1))})
            continue
        mm = RE_DROPPED.search(msg)
        if mm:
            ev.append({"p": p, "kind": "dropped", "unit": int(mm.group(1)), "n": int(mm.group(2))})
            continue
        mm = RE_COLLECTED.search(msg)
        if mm:
            ev.append({"p": p, "kind": "collected", "unit": int(mm.group(1)), "n": int(mm.group(2)), "item": mm.group(3)})
            continue
        mm = RE_PLANTED.search(msg)
        if mm:
            ev.append({"p": p, "kind": "planted", "unit": int(mm.group(1)), "item": mm.group(2).upper()})
            continue
        mm = RE_HARVESTED.search(msg)
        if mm:
            ev.append({"p": p, "kind": "harvested", "unit": int(mm.group(1)), "n": int(mm.group(2)), "item": mm.group(3)})
            continue
        mm = RE_PICKED.search(msg)
        if mm:
            ev.append({"p": p, "kind": "picked", "unit": int(mm.group(1)), "n": int(mm.group(2)), "item": mm.group(3).upper()})
            continue
        if "trained a troll" in msg:
            ev.append({"p": p, "kind": "trained"})
            continue
        ev.append({"p": p, "kind": "other", "text": msg})
    return ev


def parse_diff(text):
    """-> list of (entity_id, kind, payload); kind in P (new tree), W (new troll), U (update)."""
    out = []
    for ent in text.split(";"):
        toks = ent.split()
        if len(toks) < 2:
            continue
        try:
            eid = int(toks[0])
        except ValueError:
            continue
        i = 1
        upd = {}
        while i < len(toks):
            tok = toks[i]
            if tok == "P" and i + 1 < len(toks) and len(toks[i + 1]) == 7:
                v = toks[i + 1]
                out.append((eid, "P", {"x": b36(v[0]), "y": b36(v[1]), "type": TYPE36.get(b36(v[2]), "?"),
                                       "stage": b36(v[3]), "cd": b36(v[4]), "health": b36(v[5]), "cd_eff": b36(v[6])}))
                i += 2
                continue
            if tok == "W" and i + 1 < len(toks) and len(toks[i + 1]) == 8:
                v = toks[i + 1]
                out.append((eid, "W", {"id": b36(v[0]), "x": b36(v[1]), "y": b36(v[2]), "player": b36(v[3]),
                                       "ms": b36(v[4]), "cc": b36(v[5]), "hp": b36(v[6]), "chop": b36(v[7])}))
                i += 2
                continue
            if len(tok) == 2 and tok[0] in "xyhsc":
                upd[tok[0]] = b36(tok[1])
            elif len(tok) == 2 and tok[0].isdigit():
                upd["carry"] = (b36(tok[0]), b36(tok[1]))
            i += 1
        if upd:
            out.append((eid, "U", upd))
    return out


def load_raw(path):
    """-> (init_entities, turns) where turns = [{t, cmds:{0:[],1:[]}, events, diff, inv}]"""
    with open(path) as fh:
        d = json.load(fh)
    frames = d["frames"]
    view0 = frames[0].get("view") or ""
    j0 = json.loads(view0.split("\n", 1)[1]) if "{" in view0 else {"frame": {}}
    init = parse_diff(j0.get("frame", {}).get("diff", ""))
    turns = []
    pending = {0: [], 1: []}
    t = 1
    for f in frames[1:]:
        a, so = f.get("agentId"), f.get("stdout")
        if so is not None and a in (0, 1):
            pending[a].append(so)
        if f.get("keyframe"):
            view = f.get("view") or ""
            j = json.loads(view.split("\n", 1)[1]) if "{" in view else {}
            lines = (j.get("inputmodule") or "").split("\n")
            inv = [[int(v) for v in ln.split()] for ln in lines] if len(lines) == 2 else None
            turns.append({"t": t,
                          "cmds": {p: parse_stdout("\n".join(pending[p])) for p in (0, 1)},
                          "events": parse_summary(f.get("summary") or ""),
                          "diff": parse_diff(j.get("diff") or ""),
                          "inv": inv})
            pending = {0: [], 1: []}
            t += 1
    return init, turns


# ----------------------------------------------------------------------------- map

class Board:
    def __init__(self, rows, shacks, water, iron):
        self.h, self.w = len(rows), len(rows[0])
        self.walk = {(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == "."}
        self.shack = [tuple(shacks["p0"]), tuple(shacks["p1"])]
        self.water = {tuple(c) for c in water}
        self.iron = {tuple(c) for c in iron}
        self.dshack = [self.bfs(self.shack[0]), self.bfs(self.shack[1])]
        self._cache = {}

    @staticmethod
    def nbrs(c):
        x, y = c
        return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))

    def bfs(self, src):
        dist = {src: 0}
        q = deque([src])
        while q:
            c = q.popleft()
            d = dist[c] + 1
            for n in self.nbrs(c):
                if n in self.walk and n not in dist:
                    dist[n] = d
                    q.append(n)
        return dist

    def dist_from(self, src):
        d = self._cache.get(src)
        if d is None:
            d = self._cache[src] = self.bfs(src)
        return d

    def water_adj(self, c):
        return any(n in self.water for n in self.nbrs(c))

    def iron_adj(self, c):
        return any(n in self.iron for n in self.nbrs(c))

    def shack_adj(self, c, p):
        return any(n == self.shack[p] for n in self.nbrs(c))

    def own_half(self, c, p):
        return (c[0] < self.w / 2) if p == 0 else (c[0] >= self.w / 2)

    def next_cell(self, cur, target, speed):
        """Referee movement rule with a deterministic tie-break (fallback path only)."""
        sd = self.dist_from(cur)
        if target in sd and sd[target] <= speed:
            return target
        if target not in sd:
            best = min(abs(target[0] - c[0]) + abs(target[1] - c[1]) for c in sd)
            goals = [c for c in sd if abs(target[0] - c[0]) + abs(target[1] - c[1]) == best]
            td = {}
            for g in goals:
                for c, dd in self.dist_from(g).items():
                    if c not in td or dd < td[c]:
                        td[c] = dd
        else:
            td = self.dist_from(target)
        in_range = [c for c, dd in sd.items() if dd <= speed and c in td and c in self.walk]
        if not in_range:
            return cur
        bestd = min(td[c] for c in in_range)
        return min(c for c in in_range if td[c] == bestd)


# ----------------------------------------------------------------------------- per-game replay

class Unit:
    __slots__ = ("id", "player", "x", "y", "ms", "cc", "hp", "chop", "born", "idx")

    def __init__(self, id, player, x, y, ms, cc, hp, chop, born, idx):
        self.id, self.player, self.x, self.y = id, player, x, y
        self.ms, self.cc, self.hp, self.chop = ms, cc, hp, chop
        self.born, self.idx = born, idx

    @property
    def pos(self):
        return (self.x, self.y)


class Tree:
    __slots__ = ("cell", "type", "planter", "planted", "stage", "health", "alive", "died")

    def __init__(self, cell, type_, planter, planted, stage, health):
        self.cell, self.type, self.planter, self.planted = cell, type_, planter, planted
        self.stage, self.health, self.alive, self.died = stage, health, True, None

    @property
    def size(self):
        return min(self.stage, MAX_SIZE)


def origin_of(tree, seat):
    if tree is None:
        return "none"
    if tree.planter is None:
        return "wild"
    return "own" if tree.planter == seat else "opp"


def profile_game(game, board, turns, init_entities, seats, raw):
    """Replay one game; return one behaviour record per profiled seat."""
    units = {}
    idx_count = [0, 0]
    for u in game["trolls0"]:
        units[u["id"]] = Unit(u["id"], u["player"], u["x"], u["y"], u["ms"], u["cc"], u["hp"], u["chop"], 0, idx_count[u["player"]])
        idx_count[u["player"]] += 1
    trees = {}       # entity id (raw) or synthetic id -> Tree
    by_cell = {}     # cell -> live Tree
    if raw:
        for eid, kind, pl in init_entities:
            if kind == "P":
                tr = Tree((pl["x"], pl["y"]), pl["type"], None, 0, pl["stage"], pl["health"])
                trees[eid] = tr
                by_cell[tr.cell] = tr
    else:
        for i, tr0 in enumerate(game["map"]["trees0"]):
            tr = Tree((tr0["x"], tr0["y"]), tr0["type"], None, 0, tr0.get("stage", tr0["size"] + tr0["fruits"]), tr0["health"])
            trees[("init", i)] = tr
            by_cell[tr.cell] = tr
    next_uid = max(units) + 1
    n_turns = len(turns)

    recs = {}
    for s in seats:
        recs[s] = {
            "seat": s, "trains": [], "units": {}, "verbs": Counter(), "verbs_bucket": defaultdict(Counter),
            "opening_start_troll": [], "opening_all": [], "firsts": {}, "plants": [], "picks": Counter(),
            "harvests": [], "chops": [], "mines": [], "drops": [], "moves": [], "move_kind": Counter(),
            "iron": 0, "wood": 0, "fruit_harvested": Counter(), "failed": Counter(), "endgame": Counter(),
            "endgame_units": Counter(), "msgs": Counter(), "kills": 0, "timeouts": 0, "reuse": 0,
            "chop_by_phase_origin": Counter(), "harv_by_phase_origin": Counter(), "wood_events": [],
            "unit_first_cmd": {},
        }

    for tr in turns:
        t = tr["t"]
        ev = tr["events"] if raw else []
        pre = {uid: u.pos for uid, u in units.items()}
        # ---- 1. moves (exact from the referee's summary, else simulated)
        if raw:
            for e in ev:
                if e["kind"] == "moved" and e["unit"] in units:
                    units[e["unit"]].x, units[e["unit"]].y = e["x"], e["y"]
        else:
            for p in (0, 1):
                for c in tr["cmds"][p]:
                    if c["verb"] == "MOVE" and c["unit"] in units and units[c["unit"]].player == p and len(c["args"]) >= 2:
                        try:
                            tgt = (int(c["args"][0]), int(c["args"][1]))
                        except ValueError:
                            continue
                        u = units[c["unit"]]
                        u.x, u.y = board.next_cell(u.pos, tgt, u.ms)
        # events indexed for the seat analysis
        ev_by_unit = defaultdict(list)
        for e in ev:
            if e.get("unit") is not None:
                ev_by_unit[(e["p"], e["unit"], e["kind"])].append(e)
        damaged_cells = set()
        for e in ev:
            if e["kind"] == "damaged" and e["unit"] in units:
                damaged_cells.add((e["p"], units[e["unit"]].pos))
        # ---- 2. the profiled seats' commands
        for s in seats:
            r = recs[s]
            cmds = tr["cmds"][s]
            turn_letters = []
            start_letter = "-"
            used = set()
            for c in cmds:
                v = c["verb"]
                if v == "MSG":
                    r["msgs"][re.sub(r"\d+", "N", c.get("msg", ""))[:60]] += 1
                    continue
                r["verbs"][v] += 1
                r["verbs_bucket"][bucket_of(t)][v] += 1
                if t > n_turns - ENDGAME:
                    r["endgame"][v] += 1
                turn_letters.append(LETTER.get(v, "?"))
                uid = c["unit"]
                u = units.get(uid) if uid is not None else None
                if u is not None and u.player != s:
                    u = None
                if v == "TRAIN":
                    tal = tuple(int(a) for a in c["args"][:4]) if len(c["args"]) >= 4 and all(a.lstrip("-").isdigit() for a in c["args"][:4]) else None
                    n_before = sum(1 for x in units.values() if x.player == s)
                    r["trains"].append({"turn": t, "talents": tal, "n_before": n_before, "ok": None})
                    r["firsts"].setdefault("TRAIN", t)
                    continue
                if u is None:
                    continue
                if uid in used:
                    r["reuse"] += 1
                used.add(uid)
                ur = r["units"].setdefault(uid, {"idx": u.idx, "talents": (u.ms, u.cc, u.hp, u.chop), "born": u.born, "verbs": Counter(), "first_cmd": t})
                ur["verbs"][v] += 1
                if t > n_turns - ENDGAME:
                    r["endgame_units"][u.idx] += 1
                if u.idx == 0:
                    start_letter = LETTER.get(v, "?")
                cell = u.pos
                d_own = board.dshack[s].get(cell)
                d_opp = board.dshack[1 - s].get(cell)
                tree = by_cell.get(cell)
                if v == "MOVE":
                    if len(c["args"]) >= 2 and all(a.lstrip("-").isdigit() for a in c["args"][:2]):
                        tgt = (int(c["args"][0]), int(c["args"][1]))
                        src = pre[uid]
                        dd = board.dist_from(src).get(tgt)
                        ttree = by_cell.get(tgt)
                        if tgt == board.shack[s]:
                            kind = "own_shack_cell"
                        elif tgt == board.shack[1 - s]:
                            kind = "opp_shack_cell"
                        elif ttree is not None:
                            kind = "tree_" + origin_of(ttree, s)
                        elif board.shack_adj(tgt, s):
                            kind = "own_shack_adjacent"
                        elif board.shack_adj(tgt, 1 - s):
                            kind = "opp_shack_adjacent"
                        elif board.iron_adj(tgt):
                            kind = "iron_adjacent"
                        elif tgt not in board.walk:
                            kind = "unwalkable_other"
                        else:
                            kind = "other_grass"
                        r["moves"].append((t, dd, u.ms, kind, tgt == src))
                        r["move_kind"][kind] += 1
                    continue
                if v == "HARVEST":
                    hev = ev_by_unit.get((s, uid, "harvested"), [])
                    n_fruit = sum(e["n"] for e in hev)
                    ftype = hev[0]["item"] if hev else (tree.type if tree else None)
                    r["harvests"].append((t, origin_of(tree, s), ftype, n_fruit, d_own, d_opp))
                    r["harv_by_phase_origin"][(phase_of(t), origin_of(tree, s))] += 1
                    if n_fruit and ftype:
                        r["fruit_harvested"][ftype] += n_fruit
                    if "HARVEST" not in r["firsts"]:
                        r["firsts"]["HARVEST"] = (t, ftype, origin_of(tree, s))
                    continue
                if v == "CHOP":
                    landed = (s, cell) in damaged_cells if raw else (tree is not None)
                    near = "own" if (d_own is not None and d_opp is not None and d_own < d_opp) else ("opp" if (d_own is not None and d_opp is not None and d_opp < d_own) else "equal")
                    r["chops"].append((t, origin_of(tree, s), tree.type if tree else None, tree.size if tree else None,
                                       d_own, d_opp, near, u.chop, landed, board.own_half(cell, s), tree.stage if tree else None))
                    r["chop_by_phase_origin"][(phase_of(t), origin_of(tree, s))] += 1
                    if "CHOP" not in r["firsts"]:
                        r["firsts"]["CHOP"] = (t, tree.type if tree else None, origin_of(tree, s))
                    if not raw and tree is not None:
                        tree.health -= u.chop
                        if tree.health <= 0:
                            tree.alive, tree.died = False, t
                            by_cell.pop(cell, None)
                            r["kills"] += 1
                    continue
                if v == "PLANT":
                    ptype = c["args"][0].upper() if c["args"] else None
                    ok = bool(ev_by_unit.get((s, uid, "planted"))) if raw else (tree is None and cell in board.walk)
                    r["plants"].append((t, ptype, ok, d_own, d_opp, board.water_adj(cell), board.own_half(cell, s), cell))
                    if "PLANT" not in r["firsts"]:
                        r["firsts"]["PLANT"] = (t, ptype)
                    if not raw and ok and ptype in HEALTH_BASE:
                        ntree = Tree(cell, ptype, s, t, 0, HEALTH_BASE[ptype])
                        trees[("cmd", t, s, cell)] = ntree
                        by_cell[cell] = ntree
                    continue
                if v == "MINE":
                    got = sum(e["n"] for e in ev_by_unit.get((s, uid, "collected"), []) if e["item"] == "IRON") if raw else (u.chop if board.iron_adj(cell) else 0)
                    r["mines"].append((t, got, board.iron_adj(cell)))
                    r["iron"] += got
                    r["firsts"].setdefault("MINE", t)
                    continue
                if v == "PICK":
                    r["picks"][c["args"][0].upper() if c["args"] else "?"] += 1
                    continue
                if v == "DROP":
                    n_items = sum(e["n"] for e in ev_by_unit.get((s, uid, "dropped"), [])) if raw else None
                    r["drops"].append((t, n_items))
                    r["firsts"].setdefault("DROP", t)
                    continue
            if t <= OPENING:
                r["opening_start_troll"].append(start_letter)
                r["opening_all"].append("".join(sorted(x for x in turn_letters if x)) or "-")
            # seat-level events: failures, timeouts, wood, trained
            for e in ev:
                if e["p"] != s:
                    continue
                if e["kind"] == "failed":
                    r["failed"][e["sub"]] += 1
                elif e["kind"] == "timeout":
                    r["timeouts"] += 1
                elif e["kind"] == "collected" and e["item"] == "WOOD":
                    r["wood"] += e["n"]
                    r["wood_events"].append((t, e["n"]))
        # ---- 3. new trolls, new trees, tree updates (raw); fallback bookkeeping otherwise
        if raw:
            trained_now = defaultdict(list)
            for eid, kind, pl in tr["diff"]:
                if kind == "W":
                    p = pl["player"]
                    nu = Unit(pl["id"], p, pl["x"], pl["y"], pl["ms"], pl["cc"], pl["hp"], pl["chop"], t, idx_count[p])
                    idx_count[p] += 1
                    units[pl["id"]] = nu
                    trained_now[p].append(nu)
            for eid, kind, pl in tr["diff"]:
                if kind == "P":
                    cell = (pl["x"], pl["y"])
                    planter = None
                    for e in ev:
                        if e["kind"] == "planted" and e["unit"] in units and units[e["unit"]].pos == cell:
                            planter = e["p"]
                            break
                    ntree = Tree(cell, pl["type"], planter, t, pl["stage"], pl["health"])
                    old = by_cell.get(cell)
                    if old is not None and old.alive and eid not in trees:
                        old.alive, old.died = False, t
                    trees[eid] = ntree
                    by_cell[cell] = ntree
            for eid, kind, pl in tr["diff"]:
                if kind == "U" and eid in trees:
                    tree = trees[eid]
                    if "s" in pl:
                        tree.stage = pl["s"]
                    if "h" in pl:
                        tree.health = pl["h"]
                        if pl["h"] == 0 and tree.alive:
                            tree.alive, tree.died = False, t
                            if by_cell.get(tree.cell) is tree:
                                del by_cell[tree.cell]
                            for s in seats:
                                if (s, tree.cell) in damaged_cells:
                                    recs[s]["kills"] += 1
            # mark TRAIN commands of this turn as ok / failed, attach the created unit's talents
            for s in seats:
                mine = [x for x in recs[s]["trains"] if x["turn"] == t]
                made = trained_now.get(s, [])
                for i, x in enumerate(mine):
                    if i < len(made):
                        x["ok"] = True
                        x["unit"] = made[i].id
                        x["talents_actual"] = (made[i].ms, made[i].cc, made[i].hp, made[i].chop)
                    else:
                        x["ok"] = False
        else:
            for p in (0, 1):
                for c in tr["cmds"][p]:
                    if c["verb"] == "TRAIN" and len(c["args"]) >= 4 and all(a.lstrip("-").isdigit() for a in c["args"][:4]):
                        tal = [int(a) for a in c["args"][:4]]
                        nu = Unit(next_uid, p, board.shack[p][0], board.shack[p][1], *tal, t, idx_count[p])
                        idx_count[p] += 1
                        units[next_uid] = nu
                        next_uid += 1
                        if p in seats:
                            for x in recs[p]["trains"]:
                                if x["turn"] == t and x["ok"] is None:
                                    x["ok"] = True
                                    x["unit"] = nu.id
                                    x["talents_actual"] = tuple(tal)
                                    break
                # opponent's chops in fallback mode: damage trees so origins stay roughly right
                if p not in seats:
                    for c in tr["cmds"][p]:
                        if c["verb"] == "CHOP" and c["unit"] in units and units[c["unit"]].player == p:
                            tree = by_cell.get(units[c["unit"]].pos)
                            if tree is not None:
                                tree.health -= units[c["unit"]].chop
                                if tree.health <= 0:
                                    tree.alive, tree.died = False, t
                                    by_cell.pop(tree.cell, None)
                        elif c["verb"] == "PLANT" and c["unit"] in units and units[c["unit"]].player == p and c["args"]:
                            cell = units[c["unit"]].pos
                            if cell not in by_cell and cell in board.walk and c["args"][0].upper() in HEALTH_BASE:
                                ntree = Tree(cell, c["args"][0].upper(), p, t, 0, HEALTH_BASE[c["args"][0].upper()])
                                trees[("cmd", t, p, cell)] = ntree
                                by_cell[cell] = ntree

    # ---- game-level closing numbers
    out = []
    for s in seats:
        r = recs[s]
        r["n_turns"] = n_turns
        r["trolls_end"] = sum(1 for u in units.values() if u.player == s)
        r["opp_trolls_end"] = sum(1 for u in units.values() if u.player == 1 - s)
        r["trees_end"] = Counter(origin_of(tr_, s) for tr_ in by_cell.values())
        r["trees_end_total"] = len(by_cell)
        r["opp_units_talents"] = [(u.ms, u.cc, u.hp, u.chop) for u in units.values() if u.player == 1 - s and u.idx > 0]
        out.append(r)
    return out


# ----------------------------------------------------------------------------- aggregation

def aggregate(label, agent_ids, games_meta, per_game, mode_counts, notes):
    G = len(per_game)
    A = {"player": label, "agent_ids": sorted(agent_ids), "n_games": G,
         "position_source": mode_counts, "notes": notes}
    if G == 0:
        return A

    # (9) results -------------------------------------------------------------
    wins = [g["win"] for g in per_game]
    A["results"] = {
        "n": G, "win_rate": round(sum(wins) / G, 3),
        "score": stats([g["score"] for g in per_game]), "opp_score": stats([g["opp_score"] for g in per_game]),
        "score_margin": stats([g["score"] - g["opp_score"] for g in per_game]),
        "fruit_points": stats([g["fruit_pts"] for g in per_game if g["fruit_pts"] is not None]),
        "wood_points": stats([g["wood_pts"] for g in per_game if g["wood_pts"] is not None]),
        "wood_share_of_score": round(sum(g["wood_pts"] or 0 for g in per_game) / max(1, sum(g["score"] for g in per_game)), 3),
        "final_inventory_mean": [round(statistics.fmean(g["final_inv"][i] for g in per_game if g["final_inv"]), 2) for i in range(6)] if any(g["final_inv"] for g in per_game) else None,
        "early_end_games": sum(1 for g in per_game if g["n_turns"] < 300),
        "n_turns": stats([g["n_turns"] for g in per_game]),
        "seat0_games": sum(1 for g in per_game if g["seat"] == 0),
        "timeouts_total": sum(g["timeouts"] for g in per_game),
    }
    by_opp = defaultdict(list)
    for g in per_game:
        by_opp[min(g["opp_trolls"], 5)].append(g)
    A["results"]["by_opponent_troll_count"] = {
        (str(k) if k < 5 else "5+"): {"n": len(v), "win_rate": round(sum(x["win"] for x in v) / len(v), 3),
                                      "mean_score": round(statistics.fmean(x["score"] for x in v), 1),
                                      "mean_opp_score": round(statistics.fmean(x["opp_score"] for x in v), 1)}
        for k, v in sorted(by_opp.items())}
    by_own = defaultdict(list)
    for g in per_game:
        by_own[min(g["trolls"], 5)].append(g)
    A["results"]["by_own_troll_count"] = {
        (str(k) if k < 5 else "5+"): {"n": len(v), "win_rate": round(sum(x["win"] for x in v) / len(v), 3),
                                      "mean_score": round(statistics.fmean(x["score"] for x in v), 1)}
        for k, v in sorted(by_own.items())}
    by_arena = defaultdict(list)
    for g in per_game:
        a = g["opp_arena"]
        k = "unknown" if a is None else ("<20" if a < 20 else ("20-25" if a < 25 else ("25-28" if a < 28 else ">=28")))
        by_arena[k].append(g)
    A["results"]["by_opponent_arena_score"] = {
        k: {"n": len(v), "win_rate": round(sum(x["win"] for x in v) / len(v), 3),
            "mean_score": round(statistics.fmean(x["score"] for x in v), 1)} for k, v in sorted(by_arena.items())}
    opp_names = Counter(g["opp_name"] for g in per_game)
    A["results"]["top_opponents"] = share_table(opp_names, top=12)

    # (1) training ladder ------------------------------------------------------
    ladder = {}
    trained_counts = Counter()
    fail_train = 0
    train_cmds = 0
    for g in per_game:
        oks = [x for x in g["trains"] if x["ok"]]
        trained_counts[len(oks)] += 1
        train_cmds += len(g["trains"])
        fail_train += sum(1 for x in g["trains"] if x["ok"] is False)
        for k, x in enumerate(oks, start=1):
            L = ladder.setdefault(k, {"turns": [], "talents": Counter(), "marg": {n: Counter() for n in TALENT_NAMES}, "n_before": Counter()})
            L["turns"].append(x["turn"])
            tal = x.get("talents_actual") or x["talents"]
            L["talents"][tal] += 1
            for nm, v in zip(TALENT_NAMES, tal):
                L["marg"][nm][v] += 1
    A["training"] = {
        "train_commands_total": train_cmds, "train_commands_failed": fail_train,
        "trolls_trained_per_game": {str(k): {"n": n, "share": round(n / G, 3)} for k, n in sorted(trained_counts.items())},
        "trolls_at_end": stats([g["trolls"] for g in per_game]),
        "ladder": {}}
    for k in sorted(ladder):
        L = ladder[k]
        A["training"]["ladder"][f"troll_{k + 1}"] = {
            "games": len(L["turns"]), "share_of_games": round(len(L["turns"]) / G, 3),
            "turn": stats(L["turns"]),
            "turn_hist": {b: n for b, n in sorted(Counter(min((t - 1) // 25 * 25 + 1, 276) for t in L["turns"]).items())},
            "talents_top": share_table(L["talents"], top=8),
            "talent_marginals": {nm: {str(v): n for v, n in sorted(c.items())} for nm, c in L["marg"].items()},
        }
    opp_tal = Counter()
    for g in per_game:
        for tal in g["opp_units_talents"]:
            opp_tal[tal] += 1
    A["training"]["opponent_trained_talents_top"] = share_table(opp_tal, top=6)

    # (2) opening ------------------------------------------------------------------
    pat10 = Counter("".join(g["opening_start_troll"][:10]) for g in per_game)
    pat20 = Counter("".join(g["opening_start_troll"][:20]) for g in per_game)
    patall10 = Counter(" ".join(g["opening_all"][:10]) for g in per_game)
    verb_by_turn = defaultdict(Counter)
    for g in per_game:
        for i, letters in enumerate(g["opening_all"], start=1):
            for ch in letters:
                if ch != "-":
                    verb_by_turn[i][ch] += 1
    firsts = defaultdict(Counter)
    first_turns = defaultdict(list)
    for g in per_game:
        f = g["firsts"]
        if "HARVEST" in f:
            firsts["first_harvest_type"][f["HARVEST"][1] or "?"] += 1
            firsts["first_harvest_origin"][f["HARVEST"][2]] += 1
            first_turns["HARVEST"].append(f["HARVEST"][0])
        if "PLANT" in f:
            firsts["first_plant_type"][f["PLANT"][1] or "?"] += 1
            first_turns["PLANT"].append(f["PLANT"][0])
        if "CHOP" in f:
            firsts["first_chop_type"][f["CHOP"][1] or "?"] += 1
            firsts["first_chop_origin"][f["CHOP"][2]] += 1
            first_turns["CHOP"].append(f["CHOP"][0])
        for v in ("MINE", "TRAIN", "DROP"):
            if v in f:
                first_turns[v].append(f[v])
        firsts["first_action_verb_of_start_troll"][next((ch for ch in g["opening_start_troll"] if ch not in "-M"), "none")] += 1
    A["opening"] = {
        "letters": {"M": "MOVE", "H": "HARVEST", "C": "CHOP", "P": "PLANT", "K": "PICK", "D": "DROP", "I": "MINE", "T": "TRAIN", "W": "WAIT", "-": "no command for that troll"},
        "start_troll_turns_1_10_top": share_table(pat10, top=12),
        "start_troll_turns_1_20_top": share_table(pat20, top=8),
        "all_trolls_turns_1_10_top": share_table(patall10, top=8),
        "verb_share_by_turn_1_30": {str(t): {ch: round(n / G, 2) for ch, n in sorted(c.items())} for t, c in sorted(verb_by_turn.items())},
        "first_turn": {v: stats(xs) for v, xs in first_turns.items()},
        "games_with": {v: len(xs) for v, xs in first_turns.items()},
        **{k: share_table(c) for k, c in firsts.items()},
    }
    A["messages_top"] = share_table(sum((g["msgs"] for g in per_game), Counter()), top=10)

    # (3) planting ------------------------------------------------------------------
    plants = [p for g in per_game for p in g["plants"]]
    picks = sum((g["picks"] for g in per_game), Counter())
    okp = [p for p in plants if p[2]]
    A["planting"] = {
        "plant_commands_per_game": stats([len(g["plants"]) for g in per_game]),
        "successful_plants_per_game": stats([sum(1 for p in g["plants"] if p[2]) for g in per_game]),
        "success_rate": round(len(okp) / len(plants), 3) if plants else None,
        "by_type": share_table(Counter(p[1] for p in okp)),
        "picks_by_type": share_table(picks),
        "by_bucket_per_game": {str(b * BUCKET + 1) + "-" + str((b + 1) * BUCKET): round(n / G, 2) for b, n in sorted(Counter(bucket_of(p[0]) for p in okp).items())},
        "by_phase": share_table(Counter(phase_of(p[0]) for p in okp)),
        "dist_to_own_shack": stats([p[3] for p in okp]),
        "dist_to_own_shack_hist": {str(k): n for k, n in sorted(Counter(min(p[3], 12) if p[3] is not None else -1 for p in okp).items())},
        "dist_to_opp_shack": stats([p[4] for p in okp]),
        "water_adjacent_share": round(sum(1 for p in okp if p[5]) / len(okp), 3) if okp else None,
        "water_adjacent_share_by_type": {ty: round(sum(1 for p in okp if p[5] and p[1] == ty) / max(1, sum(1 for p in okp if p[1] == ty)), 3) for ty in FRUITS},
        "own_half_share": round(sum(1 for p in okp if p[6]) / len(okp), 3) if okp else None,
        "nearer_own_shack_share": round(sum(1 for p in okp if p[3] is not None and p[4] is not None and p[3] < p[4]) / len(okp), 3) if okp else None,
        "type_by_phase": {ph: share_table(Counter(p[1] for p in okp if phase_of(p[0]) == ph)) for ph in ("early(1-100)", "mid(101-200)", "late(201-300)")},
        "dist_to_own_shack_by_type": {ty: stats([p[3] for p in okp if p[1] == ty]) for ty in FRUITS},
        "n": len(okp),
    }

    # (4) harvesting ----------------------------------------------------------------
    H = [h for g in per_game for h in g["harvests"]]
    fruit = sum((g["fruit_harvested"] for g in per_game), Counter())
    A["harvesting"] = {
        "harvest_commands_per_game": stats([len(g["harvests"]) for g in per_game]),
        "fruits_harvested_per_game": stats([sum(g["fruit_harvested"].values()) for g in per_game]),
        "fruits_per_harvest_command": round(sum(fruit.values()) / len(H), 3) if H else None,
        "empty_harvest_commands_share": round(sum(1 for h in H if h[3] == 0) / len(H), 3) if H else None,
        "by_tree_origin": share_table(Counter(h[1] for h in H)),
        "by_fruit_type": share_table(Counter(h[2] or "?" for h in H)),
        "fruits_by_type": share_table(fruit),
        "by_bucket_per_game": {str(b * BUCKET + 1) + "-" + str((b + 1) * BUCKET): round(n / G, 2) for b, n in sorted(Counter(bucket_of(h[0]) for h in H).items())},
        "origin_by_phase": {ph: share_table(Counter(h[1] for h in H if phase_of(h[0]) == ph)) for ph in ("early(1-100)", "mid(101-200)", "late(201-300)")},
        "dist_to_own_shack": stats([h[4] for h in H]),
        "n": len(H),
    }

    # (5) chopping ------------------------------------------------------------------
    C = [c for g in per_game for c in g["chops"]]
    A["chopping"] = {
        "chop_commands_per_game": stats([len(g["chops"]) for g in per_game]),
        "chops_landed_per_game": stats([sum(1 for c in g["chops"] if c[8]) for g in per_game]),
        "trees_felled_per_game": stats([g["kills"] for g in per_game]),
        "wood_collected_per_game": stats([g["wood"] for g in per_game]),
        "by_bucket_per_game": {str(b * BUCKET + 1) + "-" + str((b + 1) * BUCKET): round(n / G, 2) for b, n in sorted(Counter(bucket_of(c[0]) for c in C).items())},
        "by_tree_origin": share_table(Counter(c[1] for c in C)),
        "origin_by_phase": {ph: share_table(Counter(c[1] for c in C if phase_of(c[0]) == ph)) for ph in ("early(1-100)", "mid(101-200)", "late(201-300)")},
        "by_tree_type": share_table(Counter(c[2] or "?" for c in C)),
        "type_by_phase": {ph: share_table(Counter(c[2] or "?" for c in C if phase_of(c[0]) == ph)) for ph in ("early(1-100)", "mid(101-200)", "late(201-300)")},
        "by_tree_size": share_table(Counter(str(c[3]) if c[3] is not None else "?" for c in C)),
        "tree_fruits_at_chop": share_table(Counter(str(max(0, c[10] - MAX_SIZE)) if c[10] is not None else "?" for c in C)),
        "nearer_shack": share_table(Counter(c[6] for c in C)),
        "own_half_share": round(sum(1 for c in C if c[9]) / len(C), 3) if C else None,
        "dist_to_own_shack": stats([c[4] for c in C]),
        "dist_to_opp_shack": stats([c[5] for c in C]),
        "by_chop_power": share_table(Counter(str(c[7]) for c in C)),
        "first_wood_turn": stats([g["wood_events"][0][0] for g in per_game if g["wood_events"]]),
        "wood_by_phase": {ph: sum(n for g in per_game for t, n in g["wood_events"] if phase_of(t) == ph) for ph in ("early(1-100)", "mid(101-200)", "late(201-300)")},
        "n": len(C),
    }

    # (6) mining ----------------------------------------------------------------------
    M = [m for g in per_game for m in g["mines"]]
    A["mining"] = {
        "mine_commands_per_game": stats([len(g["mines"]) for g in per_game]),
        "iron_collected_per_game": stats([g["iron"] for g in per_game]),
        "games_with_mine": sum(1 for g in per_game if g["mines"]),
        "iron_per_mine_command": round(sum(m[1] for m in M) / len(M), 3) if M else None,
        "by_bucket_per_game": {str(b * BUCKET + 1) + "-" + str((b + 1) * BUCKET): round(n / G, 2) for b, n in sorted(Counter(bucket_of(m[0]) for m in M).items())},
        "first_mine_turn": stats([g["firsts"]["MINE"] for g in per_game if "MINE" in g["firsts"]]),
        "n": len(M),
    }

    # (7) unit roles --------------------------------------------------------------------
    roles = {}
    for g in per_game:
        for uid, ur in g["units"].items():
            R = roles.setdefault(ur["idx"], {"games": 0, "verbs": Counter(), "talents": Counter(), "cmds": []})
            R["games"] += 1
            R["verbs"] += ur["verbs"]
            R["talents"][ur["talents"]] += 1
            R["cmds"].append(sum(ur["verbs"].values()))
    A["unit_roles"] = {}
    for idx in sorted(roles):
        R = roles[idx]
        tot = sum(R["verbs"].values())
        A["unit_roles"][("start_troll" if idx == 0 else f"trained_{idx}")] = {
            "games": R["games"], "commands_per_game": stats(R["cmds"]),
            "verb_mix": {v: round(n / tot, 3) for v, n in R["verbs"].most_common()},
            "talents_top": share_table(R["talents"], top=4),
        }

    # (8) endgame -----------------------------------------------------------------------
    end = sum((g["endgame"] for g in per_game), Counter())
    allv = sum((g["verbs"] for g in per_game), Counter())
    tot_end, tot_all = sum(end.values()), sum(allv.values())
    last_drop = [max((d[0] for d in g["drops"]), default=None) for g in per_game]
    A["endgame"] = {
        "verb_mix_last_30_turns": {v: round(n / tot_end, 3) for v, n in end.most_common()} if tot_end else {},
        "verb_mix_whole_game": {v: round(n / tot_all, 3) for v, n in allv.most_common()} if tot_all else {},
        "commands_per_game_last_30": round(tot_end / G, 1),
        "last_30_per_game": {"plants": round(sum(1 for g in per_game for p in g["plants"] if p[0] > g["n_turns"] - ENDGAME) / G, 2),
                             "chops": round(sum(1 for g in per_game for c in g["chops"] if c[0] > g["n_turns"] - ENDGAME) / G, 2),
                             "harvests": round(sum(1 for g in per_game for h in g["harvests"] if h[0] > g["n_turns"] - ENDGAME) / G, 2),
                             "drops": round(sum(1 for g in per_game for d in g["drops"] if d[0] > g["n_turns"] - ENDGAME) / G, 2),
                             "wood": round(sum(n for g in per_game for t, n in g["wood_events"] if t > g["n_turns"] - ENDGAME) / G, 2)},
        "last_drop_turn": stats(last_drop),
        "turns_from_last_drop_to_end": stats([g["n_turns"] - d for g, d in zip(per_game, last_drop) if d is not None]),
        "trees_alive_at_end_per_game": {k: round(sum(g["trees_end"].get(k, 0) for g in per_game) / G, 2) for k in ("own", "wild", "opp")},
        "games_ending_with_no_trees": sum(1 for g in per_game if g["trees_end_total"] == 0),
    }
    A["verbs_per_game"] = {v: round(n / G, 1) for v, n in allv.most_common()}
    A["verbs_by_bucket_per_game"] = {str(b * BUCKET + 1) + "-" + str((b + 1) * BUCKET): {v: round(n / G, 2) for v, n in sorted(c.items())}
                                     for b, c in sorted(sum_buckets(per_game).items())}
    A["drops"] = {"drop_commands_per_game": stats([len(g["drops"]) for g in per_game]),
                  "items_per_drop": stats([d[1] for g in per_game for d in g["drops"] if d[1] is not None])}
    A["referee_failures_per_game"] = {k: round(n / G, 2) for k, n in sum((g["failed"] for g in per_game), Counter()).most_common()}

    # (10) movement ------------------------------------------------------------------------
    MV = [m for g in per_game for m in g["moves"]]
    dists = [m[1] for m in MV if m[1] is not None]
    A["movement"] = {
        "move_commands_per_game": stats([len(g["moves"]) for g in per_game]),
        "target_bfs_distance": stats(dists),
        "target_bfs_distance_hist": {str(k): n for k, n in sorted(Counter(min(d, 15) for d in dists).items())},
        "target_unreachable_share": round(sum(1 for m in MV if m[1] is None) / len(MV), 3) if MV else None,
        "target_equals_current_cell_share": round(sum(1 for m in MV if m[4]) / len(MV), 3) if MV else None,
        "turns_to_arrive": stats([-(-d // max(1, m[2])) for m, d in ((m, m[1]) for m in MV) if d is not None]),
        "target_kind": share_table(sum((g["move_kind"] for g in per_game), Counter())),
        "n": len(MV),
    }

    # per-game one-liners ---------------------------------------------------------------------
    A["games"] = [{"gameId": g["gameId"], "seat": g["seat"], "opp": g["opp_name"], "opp_id": g["opp_id"], "opp_arena": g["opp_arena"],
                   "turns": g["n_turns"], "win": g["win"], "score": g["score"], "opp_score": g["opp_score"],
                   "fruit_pts": g["fruit_pts"], "wood_pts": g["wood_pts"], "trolls": g["trolls"], "opp_trolls": g["opp_trolls"],
                   "plants": sum(1 for p in g["plants"] if p[2]), "chops": len(g["chops"]), "harvests": len(g["harvests"]),
                   "mines": len(g["mines"]), "iron": g["iron"], "wood": g["wood"],
                   "train_turns": [x["turn"] for x in g["trains"] if x["ok"]], "source": g["source"]} for g in per_game]
    return A


def sum_buckets(per_game):
    acc = defaultdict(Counter)
    for g in per_game:
        for b, c in g["verbs_bucket"].items():
            acc[b] += c
    return acc


# ----------------------------------------------------------------------------- markdown

def md_table(headers, rows):
    out = ["| " + " | ".join(str(h) for h in headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def fmt_stats(s):
    if not s or s.get("n", 0) == 0:
        return "n=0"
    return f"mean {s['mean']}, median {s['median']}, p25-p75 {s['p25']}-{s['p75']}, min-max {s['min']}-{s['max']} (n={s['n']})"


def fmt_share_rows(rows, keyname="value"):
    return md_table([keyname, "n", "share"], [[(" ".join(map(str, r["key"])) if isinstance(r["key"], list) else r["key"]), r["n"], r["share"]] for r in rows])


def render_md(A, summary_text):
    L = []
    G = A["n_games"]
    L.append(f"# Behaviour profile: {A['player']} (agent ids {', '.join(map(str, A['agent_ids']))}; {G} games)\n")
    L.append("## Summary (plain words)\n")
    L.append(summary_text.strip() + "\n" if summary_text else "_(summary to be written after the cross-player comparison)_\n")
    L.append("## How to read this\n")
    L.append("Every table is measured over this player's games in the corpus (`n` = the number of games or events behind the row). "
             "Positions and effects come from the referee's own per-turn log inside each replay (exact troll positions after every move, "
             "which tree was planted/damaged/harvested), so 'own-planted / wild / opponent-planted' and 'tree type at the time of the chop' are exact "
             "for games read from a raw replay. For a game read from `turns.jsonl.gz` only (no raw replay), positions are simulated from MOVE targets and marked approximate. "
             f"Position source for this profile: {json.dumps(A['position_source'])}.\n")
    if A.get("notes"):
        L.append("Notes: " + " ".join(A["notes"]) + "\n")
    if G == 0:
        return "\n".join(L)
    R = A["results"]
    L.append("## 9. Results and score composition\n")
    L.append(md_table(["measure", "value"], [
        ["games", R["n"]], ["win rate", R["win_rate"]], ["seat 0 games", R["seat0_games"]],
        ["final score", fmt_stats(R["score"])], ["opponent final score", fmt_stats(R["opp_score"])],
        ["score margin", fmt_stats(R["score_margin"])],
        ["fruit points (banked fruit)", fmt_stats(R["fruit_points"])], ["wood points (4 x banked wood)", fmt_stats(R["wood_points"])],
        ["wood share of all points", R["wood_share_of_score"]],
        ["final inventory mean (plum, lemon, apple, banana, iron, wood)", R["final_inventory_mean"]],
        ["games ending before turn 300", R["early_end_games"]], ["turns per game", fmt_stats(R["n_turns"])],
        ["timeout strikes (total)", R["timeouts_total"]]]))
    L.append("\nBy the opponent's troll count at the end:\n")
    L.append(md_table(["opponent trolls", "n", "win rate", "mean score", "mean opp score"],
                      [[k, v["n"], v["win_rate"], v["mean_score"], v["mean_opp_score"]] for k, v in R["by_opponent_troll_count"].items()]))
    L.append("\nBy own troll count at the end:\n")
    L.append(md_table(["own trolls", "n", "win rate", "mean score"], [[k, v["n"], v["win_rate"], v["mean_score"]] for k, v in R["by_own_troll_count"].items()]))
    L.append("\nBy the opponent's arena score (their ladder rating in the corpus record):\n")
    L.append(md_table(["opponent arena score", "n", "win rate", "mean score"], [[k, v["n"], v["win_rate"], v["mean_score"]] for k, v in R["by_opponent_arena_score"].items()]))
    L.append("\nMost frequent opponents:\n")
    L.append(fmt_share_rows(R["top_opponents"], "opponent"))

    T = A["training"]
    L.append("\n## 1. Training ladder (TRAIN = buy a new troll; talents = speed carry harvest chop)\n")
    L.append(md_table(["measure", "value"], [
        ["TRAIN commands total / failed", f"{T['train_commands_total']} / {T['train_commands_failed']}"],
        ["trolls at the end", fmt_stats(T["trolls_at_end"])],
        ["trolls trained per game", ", ".join(f"{k}: {v['n']} games ({v['share']})" for k, v in T["trolls_trained_per_game"].items())]]))
    for name, Lk in T["ladder"].items():
        L.append(f"\n**{name}** (the {'first' if name == 'troll_2' else 'second' if name == 'troll_3' else 'third' if name == 'troll_4' else name.split('_')[1] + 'th-1'} troll bought): "
                 f"in {Lk['games']} games ({Lk['share_of_games']} of games); turn {fmt_stats(Lk['turn'])}; "
                 f"turn histogram (25-turn bins, start turn: n) {Lk['turn_hist']}\n")
        L.append(fmt_share_rows(Lk["talents_top"], "talents (speed carry harvest chop)"))
        L.append("\nmarginals: " + "; ".join(f"{nm}: {d}" for nm, d in Lk["talent_marginals"].items()) + "\n")
    L.append("Opponents' trained talents (for contrast):\n")
    L.append(fmt_share_rows(T["opponent_trained_talents_top"], "talents"))

    O = A["opening"]
    L.append("\n## 2. Opening (turns 1-30)\n")
    L.append("Letters: " + ", ".join(f"{k}={v}" for k, v in O["letters"].items()) + ".\n")
    L.append("Starting troll, one letter per turn, turns 1-10 (most common patterns):\n")
    L.append(fmt_share_rows(O["start_troll_turns_1_10_top"], "pattern"))
    L.append("\nStarting troll, turns 1-20:\n")
    L.append(fmt_share_rows(O["start_troll_turns_1_20_top"], "pattern"))
    L.append("\nAll trolls together, turns 1-10 (letters of one turn joined, turns separated by spaces):\n")
    L.append(fmt_share_rows(O["all_trolls_turns_1_10_top"], "pattern"))
    L.append("\nFirst occurrences (turn of the first command of that kind; games with it):\n")
    L.append(md_table(["verb", "games with it", "turn"], [[v, O["games_with"].get(v), fmt_stats(O["first_turn"][v])] for v in O["first_turn"]]))
    for k in ("first_action_verb_of_start_troll", "first_harvest_type", "first_harvest_origin", "first_plant_type", "first_chop_type", "first_chop_origin"):
        if k in O:
            L.append(f"\n{k.replace('_', ' ')}:\n")
            L.append(fmt_share_rows(O[k]))
    L.append("\nVerb share by turn, turns 1-30 (commands per game, by letter):\n")
    L.append(md_table(["turn"] + list("MHCPKDITW"), [[t] + [d.get(ch, "") for ch in "MHCPKDITW"] for t, d in O["verb_share_by_turn_1_30"].items()]))
    L.append("\nMost common MSG texts (digits replaced by N):\n")
    L.append(fmt_share_rows(A["messages_top"], "message"))

    P = A["planting"]
    L.append("\n## 3. Planting\n")
    L.append(md_table(["measure", "value"], [
        ["PLANT commands per game", fmt_stats(P["plant_commands_per_game"])],
        ["successful plants per game", fmt_stats(P["successful_plants_per_game"])],
        ["success rate of PLANT commands", P["success_rate"]],
        ["distance (BFS over grass) from own shack", fmt_stats(P["dist_to_own_shack"])],
        ["distance hist (cells: n; 12 = 12 or more)", P["dist_to_own_shack_hist"]],
        ["distance from opponent shack", fmt_stats(P["dist_to_opp_shack"])],
        ["planted next to water", P["water_adjacent_share"]], ["next to water, by type", P["water_adjacent_share_by_type"]],
        ["planted on own half of the map", P["own_half_share"]], ["planted nearer own shack than opponent's", P["nearer_own_shack_share"]],
        ["plants per game by 10-turn bucket", P["by_bucket_per_game"]]]))
    L.append("\nBy type (successful plants):\n")
    L.append(fmt_share_rows(P["by_type"], "type"))
    L.append("\nSeeds picked at the shack (PICK commands) by type:\n")
    L.append(fmt_share_rows(P["picks_by_type"], "type"))
    L.append("\nType by phase:\n")
    L.append(md_table(["phase"] + FRUITS, [[ph] + [next((r["share"] for r in rows if r["key"] == ty), 0) for ty in FRUITS] for ph, rows in P["type_by_phase"].items()]))
    L.append("\nDistance from own shack by type: " + "; ".join(f"{ty}: {fmt_stats(s)}" for ty, s in P["dist_to_own_shack_by_type"].items()) + "\n")

    Hh = A["harvesting"]
    L.append("## 4. Harvesting\n")
    L.append(md_table(["measure", "value"], [
        ["HARVEST commands per game", fmt_stats(Hh["harvest_commands_per_game"])],
        ["fruits harvested per game (referee count)", fmt_stats(Hh["fruits_harvested_per_game"])],
        ["fruits per HARVEST command", Hh["fruits_per_harvest_command"]], ["HARVEST commands that took nothing", Hh["empty_harvest_commands_share"]],
        ["distance from own shack of the harvested cell", fmt_stats(Hh["dist_to_own_shack"])],
        ["harvests per game by 10-turn bucket", Hh["by_bucket_per_game"]]]))
    L.append("\nBy the tree's origin (own-planted / wild / planted by the opponent):\n")
    L.append(fmt_share_rows(Hh["by_tree_origin"], "origin"))
    L.append("\nOrigin by phase:\n")
    L.append(md_table(["phase", "own", "wild", "opp", "none"], [[ph] + [next((r["share"] for r in rows if r["key"] == o), 0) for o in ("own", "wild", "opp", "none")] for ph, rows in Hh["origin_by_phase"].items()]))
    L.append("\nFruits harvested by type:\n")
    L.append(fmt_share_rows(Hh["fruits_by_type"], "type"))

    Cc = A["chopping"]
    L.append("\n## 5. Chopping\n")
    L.append(md_table(["measure", "value"], [
        ["CHOP commands per game", fmt_stats(Cc["chop_commands_per_game"])],
        ["chops that landed per game", fmt_stats(Cc["chops_landed_per_game"])],
        ["trees felled per game (this player struck the killing turn)", fmt_stats(Cc["trees_felled_per_game"])],
        ["wood collected per game", fmt_stats(Cc["wood_collected_per_game"])],
        ["turn of the first wood", fmt_stats(Cc["first_wood_turn"])], ["wood by phase (total over games)", Cc["wood_by_phase"]],
        ["chops per game by 10-turn bucket", Cc["by_bucket_per_game"]],
        ["chopped on own half of the map", Cc["own_half_share"]],
        ["distance from own shack", fmt_stats(Cc["dist_to_own_shack"])], ["distance from opponent shack", fmt_stats(Cc["dist_to_opp_shack"])]]))
    L.append("\nBy the tree's origin:\n")
    L.append(fmt_share_rows(Cc["by_tree_origin"], "origin"))
    L.append("\nOrigin by phase:\n")
    L.append(md_table(["phase", "own", "wild", "opp", "none"], [[ph] + [next((r["share"] for r in rows if r["key"] == o), 0) for o in ("own", "wild", "opp", "none")] for ph, rows in Cc["origin_by_phase"].items()]))
    L.append("\nNearer to whose shack (BFS distance):\n")
    L.append(fmt_share_rows(Cc["nearer_shack"], "nearer"))
    L.append("\nTree type at the time of the chop:\n")
    L.append(fmt_share_rows(Cc["by_tree_type"], "type"))
    L.append("\nType by phase:\n")
    L.append(md_table(["phase"] + FRUITS + ["?"], [[ph] + [next((r["share"] for r in rows if r["key"] == ty), 0) for ty in FRUITS + ["?"]] for ph, rows in Cc["type_by_phase"].items()]))
    L.append("\nTree size at the chop:\n")
    L.append(fmt_share_rows(Cc["by_tree_size"], "size"))
    L.append("\nFruits on the tree at the chop:\n")
    L.append(fmt_share_rows(Cc["tree_fruits_at_chop"], "fruits"))
    L.append("\nChop power of the chopping troll:\n")
    L.append(fmt_share_rows(Cc["by_chop_power"], "chop power"))

    Mm = A["mining"]
    L.append("\n## 6. Mining\n")
    L.append(md_table(["measure", "value"], [
        ["MINE commands per game", fmt_stats(Mm["mine_commands_per_game"])], ["iron collected per game", fmt_stats(Mm["iron_collected_per_game"])],
        ["games with at least one MINE", Mm["games_with_mine"]], ["iron per MINE command", Mm["iron_per_mine_command"]],
        ["turn of the first MINE", fmt_stats(Mm["first_mine_turn"])], ["mines per game by 10-turn bucket", Mm["by_bucket_per_game"]]]))

    L.append("\n## 7. Unit roles (verb mix per troll, in creation order)\n")
    rows = []
    for name, U in A["unit_roles"].items():
        rows.append([name, U["games"], fmt_stats(U["commands_per_game"]), ", ".join(f"{v} {s}" for v, s in U["verb_mix"].items()),
                     "; ".join(f"{' '.join(map(str, r['key']))} ({r['n']})" for r in U["talents_top"])])
    L.append(md_table(["troll", "games", "commands per game", "verb mix", "talents (n)"], rows))

    E = A["endgame"]
    L.append("\n## 8. Endgame (last 30 turns)\n")
    L.append(md_table(["measure", "value"], [
        ["verb mix, last 30 turns", E["verb_mix_last_30_turns"]], ["verb mix, whole game", E["verb_mix_whole_game"]],
        ["commands per game in the last 30 turns", E["commands_per_game_last_30"]], ["per game in the last 30 turns", E["last_30_per_game"]],
        ["turn of the last DROP", fmt_stats(E["last_drop_turn"])], ["turns from the last DROP to the end", fmt_stats(E["turns_from_last_drop_to_end"])],
        ["trees alive at the end per game (own / wild / opp)", E["trees_alive_at_end_per_game"]], ["games ending with no tree on the map", E["games_ending_with_no_trees"]]]))
    L.append("\nCommands per game by verb: " + json.dumps(A["verbs_per_game"]) + "\n")
    L.append("Commands per game by 10-turn bucket:\n")
    vb = A["verbs_by_bucket_per_game"]
    vs = ["MOVE", "HARVEST", "CHOP", "PLANT", "PICK", "DROP", "MINE", "TRAIN", "WAIT"]
    L.append(md_table(["turns"] + vs, [[b] + [d.get(v, "") for v in vs] for b, d in vb.items()]))
    L.append("\nDROP: " + fmt_stats(A["drops"]["drop_commands_per_game"]) + " commands per game; items per drop " + fmt_stats(A["drops"]["items_per_drop"]) + "\n")
    L.append("Referee-reported failures per game: " + json.dumps(A["referee_failures_per_game"]) + "\n")

    Mv = A["movement"]
    L.append("## 10. Movement\n")
    L.append(md_table(["measure", "value"], [
        ["MOVE commands per game", fmt_stats(Mv["move_commands_per_game"])],
        ["BFS distance from the troll's cell to the MOVE target", fmt_stats(Mv["target_bfs_distance"])],
        ["distance histogram (15 = 15 or more)", Mv["target_bfs_distance_hist"]],
        ["turns needed to arrive (distance / speed, rounded up)", fmt_stats(Mv["turns_to_arrive"])],
        ["target unreachable (water, rock, a shack cell)", Mv["target_unreachable_share"]], ["target = the troll's current cell", Mv["target_equals_current_cell_share"]]]))
    L.append("\nWhat the MOVE target is:\n")
    L.append(fmt_share_rows(Mv["target_kind"], "target"))
    L.append("\n## What the corpus cannot tell\n")
    L.append("- Why a decision was taken: no bot state, no evaluation, no stderr. Only commands and the referee's outcomes are recorded.\n"
             "- A troll's carried inventory between DROPs (the viewer shows one item at a time); carry is inferred only through referee events.\n"
             "- Whether a MOVE was re-targeted before arrival is visible, but the intended destination of a multi-turn walk is not.\n"
             "- Tree fruit counts and cooldowns are followed through the viewer diff (stage = size + fruits); the stage shown at a chop is the state after that turn's tick.\n"
             "- Games of this agent id only; earlier or later versions of the same player's bot may differ.\n")
    return "\n".join(L)


# ----------------------------------------------------------------------------- compare mode

def compare(paths, out_path):
    profs = [json.load(open(p)) for p in paths]
    names = [p["player"] for p in profs]

    def g(p, *keys, default=""):
        cur = p
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                return default
        return cur

    def lad(p, k, what):
        Lk = g(p, "training", "ladder", k, default=None)
        if not Lk:
            return "-"
        if what == "turn":
            return f"{Lk['turn'].get('median', '-')} (n={Lk['games']}, {Lk['share_of_games']})"
        return "; ".join(f"{' '.join(map(str, r['key']))} {r['share']}" for r in Lk["talents_top"][:3])

    rows = [
        ["games", *[p["n_games"] for p in profs]],
        ["win rate", *[g(p, "results", "win_rate") for p in profs]],
        ["mean score", *[g(p, "results", "score", "mean") for p in profs]],
        ["mean opponent score", *[g(p, "results", "opp_score", "mean") for p in profs]],
        ["wood share of points", *[g(p, "results", "wood_share_of_score") for p in profs]],
        ["fruit points mean", *[g(p, "results", "fruit_points", "mean") for p in profs]],
        ["wood points mean", *[g(p, "results", "wood_points", "mean") for p in profs]],
        ["trolls at end (mean)", *[g(p, "training", "trolls_at_end", "mean") for p in profs]],
        ["troll 2: median turn (games, share)", *[lad(p, "troll_2", "turn") for p in profs]],
        ["troll 2: top talents", *[lad(p, "troll_2", "tal") for p in profs]],
        ["troll 3: median turn (games, share)", *[lad(p, "troll_3", "turn") for p in profs]],
        ["troll 3: top talents", *[lad(p, "troll_3", "tal") for p in profs]],
        ["troll 4: median turn (games, share)", *[lad(p, "troll_4", "turn") for p in profs]],
        ["troll 4: top talents", *[lad(p, "troll_4", "tal") for p in profs]],
        ["first MINE turn (median)", *[g(p, "mining", "first_mine_turn", "median") for p in profs]],
        ["MINE per game", *[g(p, "mining", "mine_commands_per_game", "mean") for p in profs]],
        ["iron per game", *[g(p, "mining", "iron_collected_per_game", "mean") for p in profs]],
        ["plants per game (ok)", *[g(p, "planting", "successful_plants_per_game", "mean") for p in profs]],
        ["plant types", *["; ".join(f"{r['key']} {r['share']}" for r in g(p, "planting", "by_type", default=[])) for p in profs]],
        ["plant dist from own shack (median)", *[g(p, "planting", "dist_to_own_shack", "median") for p in profs]],
        ["plant next to water", *[g(p, "planting", "water_adjacent_share") for p in profs]],
        ["plant on own half", *[g(p, "planting", "own_half_share") for p in profs]],
        ["harvest cmds per game", *[g(p, "harvesting", "harvest_commands_per_game", "mean") for p in profs]],
        ["fruits harvested per game", *[g(p, "harvesting", "fruits_harvested_per_game", "mean") for p in profs]],
        ["harvest origin", *["; ".join(f"{r['key']} {r['share']}" for r in g(p, "harvesting", "by_tree_origin", default=[])) for p in profs]],
        ["chop cmds per game", *[g(p, "chopping", "chop_commands_per_game", "mean") for p in profs]],
        ["wood per game", *[g(p, "chopping", "wood_collected_per_game", "mean") for p in profs]],
        ["first wood turn (median)", *[g(p, "chopping", "first_wood_turn", "median") for p in profs]],
        ["chop origin", *["; ".join(f"{r['key']} {r['share']}" for r in g(p, "chopping", "by_tree_origin", default=[])) for p in profs]],
        ["chop nearer shack", *["; ".join(f"{r['key']} {r['share']}" for r in g(p, "chopping", "nearer_shack", default=[])) for p in profs]],
        ["chop tree type", *["; ".join(f"{r['key']} {r['share']}" for r in g(p, "chopping", "by_tree_type", default=[])) for p in profs]],
        ["chop tree size", *["; ".join(f"{r['key']} {r['share']}" for r in g(p, "chopping", "by_tree_size", default=[])) for p in profs]],
        ["chops early/mid/late per game", *[" / ".join(str(round(sum(v for b, v in g(p, "chopping", "by_bucket_per_game", default={}).items() if lo <= int(b.split('-')[0]) <= hi), 1)) for lo, hi in ((1, 91), (101, 191), (201, 291))) for p in profs]],
        ["plants early/mid/late per game", *[" / ".join(str(round(sum(v for b, v in g(p, "planting", "by_bucket_per_game", default={}).items() if lo <= int(b.split('-')[0]) <= hi), 1)) for lo, hi in ((1, 91), (101, 191), (201, 291))) for p in profs]],
        ["MOVE per game", *[g(p, "movement", "move_commands_per_game", "mean") for p in profs]],
        ["MOVE target distance (mean)", *[g(p, "movement", "target_bfs_distance", "mean") for p in profs]],
        ["endgame verb mix (last 30)", *[json.dumps(g(p, "endgame", "verb_mix_last_30_turns", default={})) for p in profs]],
        ["last DROP turn (median)", *[g(p, "endgame", "last_drop_turn", "median") for p in profs]],
        ["trees alive at end own/wild/opp", *[json.dumps(g(p, "endgame", "trees_alive_at_end_per_game", default={})) for p in profs]],
        ["DROP per game", *[g(p, "drops", "drop_commands_per_game", "mean") for p in profs]],
        ["items per DROP", *[g(p, "drops", "items_per_drop", "mean") for p in profs]],
        ["start-troll opening 1-10 (top)", *[(g(p, "opening", "start_troll_turns_1_10_top", default=[{}]) or [{}])[0].get("key", "") for p in profs]],
    ]
    text = "# Side-by-side comparison of the behaviour profiles\n\n" + md_table(["measure"] + names, rows) + "\n"
    with open(out_path, "w") as fh:
        fh.write(text)
    print(f"wrote {out_path}")


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--player", help="pseudo (player name) as it appears in games.jsonl")
    ap.add_argument("--agent", help="comma-separated agent ids (restricts --player, or stands alone)")
    ap.add_argument("--label", help="file label (default: player name or agent id)")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--data", default=DATA_DEFAULT)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--summary", help="text file whose content is placed under 'Summary' in the .md")
    ap.add_argument("--compare", nargs="*", help="profile .json files to compare side by side")
    ap.add_argument("--compare-out", default=None)
    ap.add_argument("--render-only", action="store_true", help="re-render <out>/<label>.md from the existing .json (no replaying)")
    args = ap.parse_args()

    if args.compare:
        compare(args.compare, args.compare_out or os.path.join(args.out, "COMPARISON.md"))
        return
    if args.render_only:
        label = args.label or args.player
        A = json.load(open(os.path.join(args.out, f"{label}.json")))
        summary = open(args.summary).read() if args.summary and os.path.exists(args.summary) else ""
        with open(os.path.join(args.out, f"{label}.md"), "w") as fh:
            fh.write(render_md(A, summary))
        print(f"re-rendered {label}.md", file=sys.stderr)
        return
    if not args.player and not args.agent:
        ap.error("--player and/or --agent required")
    agent_ids = {int(a) for a in args.agent.split(",")} if args.agent else None
    label = args.label or args.player or "_".join(sorted(map(str, agent_ids)))

    # 1. select games
    games = []
    all_ids_of_player = Counter()
    with open(os.path.join(args.data, "processed", "games.jsonl")) as fh:
        for line in fh:
            g = json.loads(line)
            seats = []
            for p in g["players"]:
                if args.player and p["name"] == args.player:
                    all_ids_of_player[p["agentId"]] += 1
                match = (agent_ids is not None and p["agentId"] in agent_ids) or (agent_ids is None and args.player and p["name"] == args.player)
                if match:
                    seats.append(p["index"])
            if seats:
                games.append((g, seats))
    if args.limit:
        games = games[:args.limit]
    used_ids = {g["players"][s]["agentId"] for g, seats in games for s in seats}
    notes = []
    if args.player and len(all_ids_of_player) > 1:
        notes.append(f"Pseudo {args.player} appears under {len(all_ids_of_player)} agent ids in games.jsonl "
                     f"(id: games) {dict(sorted(all_ids_of_player.items(), key=lambda kv: -kv[1]))}; this profile uses {sorted(used_ids)}.")
    print(f"{label}: {len(games)} games selected (agent ids {sorted(used_ids)})", file=sys.stderr)

    # 2. which games have a raw replay; load turns.jsonl.gz only for the rest
    raw_dir = os.path.join(args.data, "raw", "games")
    need_turns = {g["gameId"] for g, _ in games if not os.path.exists(os.path.join(raw_dir, f"{g['gameId']}.json"))}
    turns_cmds = defaultdict(lambda: defaultdict(lambda: {0: [], 1: []}))   # gid -> turn -> seat -> cmds
    if need_turns:
        print(f"  {len(need_turns)} games without raw replay -> reading turns.jsonl.gz (positions simulated)", file=sys.stderr)
        with gzip.open(os.path.join(args.data, "processed", "turns.jsonl.gz"), "rt") as fh:
            for line in fh:
                gid = int(line[10:line.index(",")])
                if gid in need_turns:
                    r = json.loads(line)
                    turns_cmds[gid][r["turn"]][r["seat"]] = [dict(c, msg=(r.get("msg") or "")) if c["verb"] == "MSG" else c for c in r["cmds"]]
    maps_by_hash = {}
    if any("map" not in g or not g["map"].get("rows") for g, _ in games):
        with open(os.path.join(args.data, "processed", "maps.jsonl")) as fh:
            for line in fh:
                m = json.loads(line)
                maps_by_hash[m["map_hash"]] = m

    # 3. replay every game
    per_game = []
    mode_counts = Counter()
    for i, (g, seats) in enumerate(games):
        gid = g["gameId"]
        mp = g.get("map") if g.get("map", {}).get("rows") else maps_by_hash.get(g["map_hash"])
        board = Board(mp["rows"], mp["shacks"], mp.get("water") or mp.get("water_cells") or [], mp.get("iron") or mp.get("iron_cells") or [])
        raw_path = os.path.join(raw_dir, f"{gid}.json")
        if os.path.exists(raw_path):
            init, turns = load_raw(raw_path)
            raw = True
            mode_counts["raw_replay_exact_positions"] += 1
        else:
            tc = turns_cmds.get(gid)
            if not tc:
                mode_counts["no_data"] += 1
                continue
            turns = [{"t": t, "cmds": tc[t], "events": [], "diff": [], "inv": None} for t in sorted(tc)]
            init = []
            raw = False
            mode_counts["turns_jsonl_simulated_positions"] += 1
        recs = profile_game(g, board, turns, init, seats, raw)
        for r in recs:
            s = r["seat"]
            pp = g["per_player"].get(str(s), {})
            fin = pp.get("final_inv")
            r.update({
                "gameId": gid, "source": "raw" if raw else "turns",
                "opp_name": g["players"][1 - s]["name"], "opp_id": g["players"][1 - s]["agentId"], "opp_arena": g["players"][1 - s].get("arenaScore"),
                "score": g["scores"][s], "opp_score": g["scores"][1 - s],
                "win": 1.0 if g["ranks"][s] < g["ranks"][1 - s] else (0.5 if g["ranks"][s] == g["ranks"][1 - s] else 0.0),
                "final_inv": fin, "fruit_pts": (sum(fin[:4]) if fin else None), "wood_pts": (4 * fin[5] if fin else None),
                "trolls": r["trolls_end"], "opp_trolls": r["opp_trolls_end"],
            })
            per_game.append(r)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(games)} games", file=sys.stderr)

    A = aggregate(label, used_ids, games, per_game, dict(mode_counts), notes)
    os.makedirs(args.out, exist_ok=True)
    jpath = os.path.join(args.out, f"{label}.json")
    with open(jpath, "w") as fh:
        json.dump(A, fh, indent=1, default=lambda o: list(o) if isinstance(o, (set, tuple)) else str(o))
    summary = open(args.summary).read() if args.summary and os.path.exists(args.summary) else ""
    mpath = os.path.join(args.out, f"{label}.md")
    with open(mpath, "w") as fh:
        fh.write(render_md(A, summary))
    print(f"wrote {jpath} and {mpath} ({len(per_game)} seat-games)", file=sys.stderr)


if __name__ == "__main__":
    main()
