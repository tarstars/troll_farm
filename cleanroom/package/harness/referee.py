#!/usr/bin/env python3
"""A referee for this game, and a runner that plays two programs against each other.

Written from RULES.md. Reads a frozen map from `maps/`, starts two bots as child
processes, speaks the protocol of RULES section 13 to each of them, applies both
sides' commands under the rules, and reports the result.

It is a faithful implementation of the rules with two deliberate differences,
both documented in RULES.md and both stated again here so you never mistake a
harness artefact for a rule:

  * equal-best movement ties are broken by the lexicographically smallest cell,
    where the real referee breaks them randomly (RULES section 4);
  * the time limit is measured but, by default, not enforced as a loss --
    `--enforce-time` turns enforcement on (the third strike loses, as on the
    platform; RULES section 12).

Usage
    python3 referee.py --maps maps --p0 ./champion --p1 "python3 mybot.py"
    python3 referee.py --maps maps --p0 ./champion --p1 ./mybot --both-seats --json out.json
    python3 referee.py --p0 ./champion --p1 ./mybot --both-seats --trace turns.jsonl

Pass `--both-seats` for anything you intend to draw a conclusion from: the map is
symmetric but the seats are not identical.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import shlex
import subprocess
import sys
import threading
import time
from collections import deque

ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
INDEX = {name: i for i, name in enumerate(ITEMS)}
WOOD = INDEX["WOOD"]
IRON = INDEX["IRON"]
MAX_SIZE, MAX_FRUITS, WOOD_POINTS = 4, 3, 4
BASE_COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
HEALTH = {"PLUM": (4, 2), "LEMON": (4, 2), "APPLE": (8, 3), "BANANA": (2, 1)}
NEIGHBOURS = ((0, 1), (1, 0), (0, -1), (-1, 0))
PRIORITY = ("MOVE", "HARVEST", "PLANT", "CHOP", "PICK", "TRAIN", "DROP", "MINE")
STRIKES_TO_LOSE = 3


def tree_health(kind, size):
    base, slope = HEALTH[kind]
    return base + slope * size


def item_name(token):
    """The item an argument names: a name, or its number 0..5 as the platform accepts."""
    token = token.upper()
    if token in INDEX:
        return token
    if token.isdigit() and int(token) < len(ITEMS):
        return ITEMS[int(token)]
    return None


class Illegal(Exception):
    """A command the referee refuses. Fatal ones end the match."""


# ---------------------------------------------------------------- game state

class Game:
    def __init__(self, spec):
        self.width, self.height = spec["width"], spec["height"]
        self.rows = list(spec["rows"])
        self.walkable = {(x, y) for y, row in enumerate(self.rows)
                         for x, ch in enumerate(row) if ch == "."}
        self.water = {(x, y) for y, row in enumerate(self.rows)
                      for x, ch in enumerate(row) if ch == "~"}
        self.iron = {(x, y) for y, row in enumerate(self.rows)
                     for x, ch in enumerate(row) if ch == "+"}
        self.shacks = [None, None]
        for y, row in enumerate(self.rows):
            for x, ch in enumerate(row):
                if ch in "01":
                    self.shacks[int(ch)] = (x, y)
        self.inventories = [list(inv) for inv in spec["inventories"]]
        self.trees = [dict(t) for t in spec["trees"]]
        self.units = [dict(u) | {"carry": [0] * 6} for u in spec["trolls"]]
        self.next_id = max(u["id"] for u in self.units) + 1
        self.turn = 0
        self.scores = [0, 0]
        self.countdown = 0
        self.recompute()

    # -- helpers
    def unit(self, uid):
        for u in self.units:
            if u["id"] == uid:
                return u
        return None

    def tree_at(self, cell):
        for t in self.trees:
            if (t["x"], t["y"]) == cell:
                return t
        return None

    def free(self, u):
        return u["cc"] - sum(u["carry"])

    def near_shack(self, u):
        sx, sy = self.shacks[u["player"]]
        return abs(u["x"] - sx) + abs(u["y"] - sy) <= 1

    def recompute(self):
        for p in (0, 1):
            inv = self.inventories[p]
            self.scores[p] = sum(inv[:4]) + WOOD_POINTS * inv[WOOD]

    def distances(self, sources):
        dist = {s: 0 for s in sources}
        queue_ = deque(sources)
        while queue_:
            cell = queue_.popleft()
            for dx, dy in NEIGHBOURS:
                nxt = (cell[0] + dx, cell[1] + dy)
                if nxt in dist or nxt not in self.walkable:
                    continue
                dist[nxt] = dist[cell] + 1
                queue_.append(nxt)
        return dist

    def next_cell(self, start, target, speed):
        src = self.distances([start])
        if src.get(target, 1 << 30) <= speed:
            return target
        if target in src:
            tdist = self.distances([target])
        else:
            if not src:
                return start
            best = min(abs(target[0] - c[0]) + abs(target[1] - c[1]) for c in src)
            goals = [c for c in src
                     if abs(target[0] - c[0]) + abs(target[1] - c[1]) == best]
            tdist = self.distances(goals)
        reach = [c for c, d in src.items() if d <= speed and c in tdist]
        if not reach:
            return start
        best = min(tdist[c] for c in reach)
        return min(c for c in reach if tdist[c] == best)

    def snapshot(self):
        """The state as both bots see it at the start of a turn (for --trace)."""
        return {"inventories": [list(inv) for inv in self.inventories],
                "trees": [dict(t) for t in self.trees],
                "trolls": [{k: (list(v) if isinstance(v, list) else v) for k, v in u.items()}
                           for u in self.units]}

    # -- the eight tasks, in priority order
    def apply_moves(self, intents):
        for player in (0, 1):
            mine = [u for u in self.units if u["player"] == player]
            target = {}
            for u in mine:
                want = intents.get(u["id"])
                target[u["id"]] = (self.next_cell((u["x"], u["y"]), want, u["ms"])
                                   if want else (u["x"], u["y"]))
            occupied = {(u["x"], u["y"]) for u in mine}
            movers = sorted([u["id"] for u in mine
                             if target[u["id"]] != (self.unit(u["id"])["x"],
                                                    self.unit(u["id"])["y"])],
                            reverse=True)
            forcing = False
            progress = True
            while progress and movers:
                progress = False
                freq = {}
                for uid in movers:
                    freq[target[uid]] = freq.get(target[uid], 0) + 1
                moved = []
                for uid in movers:
                    cell = target[uid]
                    u = self.unit(uid)
                    if (forcing or freq[cell] == 1) and cell not in occupied:
                        occupied.discard((u["x"], u["y"]))
                        occupied.add(cell)
                        u["x"], u["y"] = cell
                        moved.append(uid)
                        progress, forcing = True, False
                movers = [m for m in movers if m not in moved]
                if progress:
                    continue
                at = {(self.unit(m)["x"], self.unit(m)["y"]): m for m in movers}
                cycled = False
                for start in list(movers):
                    path = [start]
                    while True:
                        nxt = at.get(target[path[-1]])
                        if nxt is None:
                            break
                        if nxt == path[0]:
                            for uid in path:
                                self.unit(uid)["x"], self.unit(uid)["y"] = target[uid]
                            movers = [m for m in movers if m not in path]
                            progress = cycled = True
                            break
                        if nxt in path:
                            break
                        path.append(nxt)
                    if cycled:
                        break
                if not cycled and not forcing:
                    forcing, progress = True, True

    def apply_harvest(self, ids):
        cells = {}
        for uid in ids:
            u = self.unit(uid)
            if not u:
                continue
            tree = self.tree_at((u["x"], u["y"]))
            if tree and tree["fruits"] > 0:
                cells.setdefault((u["x"], u["y"]), []).append(uid)
        for cell, uids in cells.items():
            tree = self.tree_at(cell)
            idx = INDEX[tree["type"]]
            for round_ in range(1, MAX_FRUITS + 1):
                if tree["fruits"] == 0:
                    break
                for uid in uids:
                    u = self.unit(uid)
                    if u["hp"] >= round_ and self.free(u) > 0:
                        u["carry"][idx] += 1
                        if tree["fruits"] > 0:
                            tree["fruits"] -= 1

    def apply_plant(self, wants):
        by_cell = {}
        for uid, kind in wants:
            u = self.unit(uid)
            if not u:
                continue
            cell = (u["x"], u["y"])
            if cell not in self.walkable or self.tree_at(cell):
                continue
            if u["carry"][INDEX[kind]] <= 0:
                continue
            by_cell.setdefault(cell, []).append((uid, kind))
        for cell, entries in by_cell.items():
            kinds = {k for _, k in entries}
            if len(kinds) != 1:
                continue
            kind = entries[0][1]
            for uid, _ in entries:
                self.unit(uid)["carry"][INDEX[kind]] -= 1
            self.trees.append({"type": kind, "x": cell[0], "y": cell[1], "size": 0,
                               "health": tree_health(kind, 0), "fruits": 0, "cooldown": 0})

    def apply_chop(self, ids, standing=None):
        """CHOP acts only on trees in `standing` -- the cells that held a tree before
        this turn's PLANTs (RULES section 10). None means every tree."""
        cells = {}
        for uid in ids:
            u = self.unit(uid)
            if not u or u["chop"] <= 0:
                continue
            cell = (u["x"], u["y"])
            if standing is not None and cell not in standing:
                continue
            if self.tree_at(cell):
                cells.setdefault(cell, []).append(uid)
        for cell, uids in cells.items():
            tree = self.tree_at(cell)
            for uid in uids:
                tree["health"] = max(0, tree["health"] - self.unit(uid)["chop"])
            if tree["health"] > 0:
                continue
            remaining = tree["size"]
            for _ in range(tree["size"]):
                if remaining <= 0:
                    break
                for uid in uids:
                    u = self.unit(uid)
                    if self.free(u) > 0:
                        u["carry"][WOOD] += 1
                        remaining -= 1
            self.trees.remove(tree)

    def apply_pick(self, wants):
        for uid, kind in wants:
            u = self.unit(uid)
            if not u or not self.near_shack(u) or self.free(u) <= 0:
                continue
            idx = INDEX[kind]
            if self.inventories[u["player"]][idx] > 0:
                self.inventories[u["player"]][idx] -= 1
                u["carry"][idx] += 1

    def talents_legal(self, talents):
        """RULES section 8: speed 1..cells, carry 0..1000, harvest 0..3, chop 0..20."""
        ms, cc, hp, chop = talents
        return (1 <= ms <= self.width * self.height and 0 <= cc <= 1000
                and 0 <= hp <= MAX_FRUITS and 0 <= chop <= 20)

    def apply_train(self, player, talents):
        if not self.talents_legal(talents):
            return                        # non-fatal: the bundle is refused
        have = sum(1 for u in self.units if u["player"] == player)
        ms, cc, hp, chop = talents
        cost = [0] * 6
        cost[0], cost[1] = have + ms * ms, have + cc * cc
        cost[2], cost[IRON] = have + hp * hp, have + chop * chop
        pay = range(6) if self.iron else [0, 1, 2, 3, 5]
        inv = self.inventories[player]
        if any(inv[i] < cost[i] for i in pay):
            return
        shack = self.shacks[player]
        if any((u["x"], u["y"]) == shack for u in self.units):
            return
        for i in pay:
            inv[i] -= cost[i]
        self.units.append({"id": self.next_id, "player": player, "x": shack[0],
                           "y": shack[1], "ms": ms, "cc": cc, "hp": hp,
                           "chop": chop, "carry": [0] * 6})
        self.next_id += 1

    def apply_drop(self, ids):
        for uid in ids:
            u = self.unit(uid)
            if not u or not self.near_shack(u):
                continue
            for i in range(6):
                self.inventories[u["player"]][i] += u["carry"][i]
            u["carry"] = [0] * 6

    def apply_mine(self, ids):
        for uid in ids:
            u = self.unit(uid)
            if not u or u["chop"] <= 0 or self.free(u) <= 0:
                continue
            if any(abs(u["x"] - ix) + abs(u["y"] - iy) == 1 for ix, iy in self.iron):
                u["carry"][IRON] += min(u["chop"], self.free(u))

    def tick_trees(self):
        for tree in self.trees:
            if tree["cooldown"] > 0:
                tree["cooldown"] -= 1
            if tree["cooldown"] != 0 or tree["health"] <= 0:
                continue
            grew = False
            if tree["size"] < MAX_SIZE:
                tree["size"] += 1
                tree["health"] += HEALTH[tree["type"]][1]
                grew = True
            elif tree["fruits"] < MAX_FRUITS:
                tree["fruits"] += 1
                grew = True
            if not grew:
                continue
            cooldown = BASE_COOLDOWN[tree["type"]]
            if any(abs(tree["x"] - wx) + abs(tree["y"] - wy) == 1
                   for wx, wy in self.water):
                cooldown -= WATER_BOOST[tree["type"]]
            tree["cooldown"] = cooldown

    def apply_turn(self, parsed):
        """Apply both seats' parsed commands in the referee's fixed verb order
        (RULES section 10), then tick the trees and recompute the scores."""
        self.apply_moves({**parsed[0]["MOVE"], **parsed[1]["MOVE"]})
        self.apply_harvest(parsed[0]["HARVEST"] + parsed[1]["HARVEST"])
        standing = {(t["x"], t["y"]) for t in self.trees}
        self.apply_plant(parsed[0]["PLANT"] + parsed[1]["PLANT"])
        self.apply_chop(parsed[0]["CHOP"] + parsed[1]["CHOP"], standing)
        self.apply_pick(parsed[0]["PICK"] + parsed[1]["PICK"])
        for seat in (0, 1):
            for talents in parsed[seat]["TRAIN"]:
                self.apply_train(seat, talents)
        self.apply_drop(parsed[0]["DROP"] + parsed[1]["DROP"])
        self.apply_mine(parsed[0]["MINE"] + parsed[1]["MINE"])
        self.tick_trees()
        self.recompute()

    def ended(self):
        """RULES section 11. Returns (ended, why)."""
        if self.trees:
            self.countdown = 0
            for u in self.units:
                if not self.tree_at((u["x"], u["y"])):
                    continue
                home = self.distances([self.shacks[u["player"]]]).get((u["x"], u["y"]), 9999)
                self.countdown = max(self.countdown, home // max(u["ms"], 1) + 6)
            return False, None
        self.countdown -= 1
        if self.countdown <= 0:
            return True, "the clock after the last tree ran out"
        stuck = [True, True]
        for u in self.units:
            if sum(u["carry"][:4]) + u["carry"][WOOD] > 0:
                stuck[u["player"]] = False
        for p in (0, 1):
            if any(v > 0 for v in self.inventories[p][:4]):
                stuck[p] = False
        if stuck[0] and stuck[1]:
            return True, "both players have nothing left"
        for p in (0, 1):
            if stuck[p] and self.scores[p] < self.scores[1 - p]:
                return True, "player %d is stuck and behind" % p
        return False, None


# ---------------------------------------------------------------- protocol

def initial_text(game, seat):
    swap = str.maketrans({"0": "1", "1": "0"})
    rows = [r.translate(swap) for r in game.rows] if seat == 1 else list(game.rows)
    return "\n".join(["%d %d" % (game.width, game.height)] + rows) + "\n"


def turn_text(game, seat):
    lines = [" ".join(str(v) for v in game.inventories[seat]),
             " ".join(str(v) for v in game.inventories[1 - seat]),
             str(len(game.trees))]
    for t in sorted(game.trees, key=lambda t: (t["y"], t["x"])):
        lines.append("%s %d %d %d %d %d %d" % (t["type"], t["x"], t["y"], t["size"],
                                               t["health"], t["fruits"], t["cooldown"]))
    lines.append(str(len(game.units)))
    for u in sorted(game.units, key=lambda u: u["id"]):
        lines.append("%d %d %d %d %d %d %d %d %s"
                     % (u["id"], 0 if u["player"] == seat else 1, u["x"], u["y"],
                        u["ms"], u["cc"], u["hp"], u["chop"],
                        " ".join(str(c) for c in u["carry"])))
    return "\n".join(lines) + "\n"


def parse(line, game, seat):
    """Split one seat's output. Raises Illegal on a fatal command."""
    out = {verb: [] for verb in PRIORITY}
    moves, used = {}, set()
    for chunk in line.replace("\n", ";").split(";"):
        parts = chunk.split()
        if not parts:
            continue
        verb = parts[0].upper()
        if verb in ("MSG", "WAIT"):
            continue
        if verb == "TRAIN":
            if len(parts) < 5:
                raise Illegal("TRAIN with %d arguments" % (len(parts) - 1))
            out["TRAIN"].append(tuple(int(p) for p in parts[1:5]))
            continue
        if verb not in PRIORITY:
            raise Illegal("unknown command %r" % verb)
        if len(parts) < 2:
            raise Illegal("%s with no troll id" % verb)
        try:
            uid = int(parts[1])
        except ValueError:
            raise Illegal("%s with a non-numeric troll id %r" % (verb, parts[1]))
        if uid in used:
            continue
        used.add(uid)
        unit = game.unit(uid)
        if unit is None or unit["player"] != seat:
            continue                      # non-fatal: skipped
        if verb == "MOVE":
            if len(parts) < 4:
                raise Illegal("MOVE with no target")
            moves[uid] = (int(parts[2]), int(parts[3]))
        elif verb in ("PLANT", "PICK"):
            kind = item_name(parts[2]) if len(parts) >= 3 else None
            if kind is None:
                raise Illegal("%s with a bad item %r" % (verb, parts[2:3]))
            if verb == "PLANT" and kind in ("IRON", "WOOD"):
                continue                  # non-fatal: only fruit can be planted (RULES 9)
            out[verb].append((uid, kind))
        else:
            out[verb].append(uid)
    out["MOVE"] = moves
    return out


class Bot:
    """A bot as a child process. A reader thread feeds its lines through a queue so
    that a bot which never answers costs `wall` seconds, not the whole run."""

    def __init__(self, command, name, wall=5.0):
        self.name, self.command, self.wall = name, command, wall
        self.process = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                        text=True, bufsize=1)
        self.lines = queue.Queue()
        self.reader = threading.Thread(target=self._pump, daemon=True)
        self.reader.start()
        self.times = []

    def _pump(self):
        try:
            while True:
                line = self.process.stdout.readline()
                if line == "":
                    break
                self.lines.put(line)
        except (ValueError, OSError):
            pass
        self.lines.put(None)

    def ask(self, payload, limit):
        start = time.monotonic()
        try:
            self.process.stdin.write(payload)
            self.process.stdin.flush()
        except (BrokenPipeError, ValueError, OSError):
            raise Illegal("%s stopped responding" % self.name)
        try:
            line = self.lines.get(timeout=self.wall)
        except queue.Empty:
            raise Illegal("%s gave no answer within %.0f s" % (self.name, self.wall))
        elapsed = (time.monotonic() - start) * 1000.0
        self.times.append(elapsed)
        if line is None:
            raise Illegal("%s closed its output" % self.name)
        return line.strip(), elapsed, elapsed > limit

    def close(self):
        try:
            self.process.stdin.close()
        except Exception:
            pass
        try:
            self.process.wait(timeout=2)
        except Exception:
            self.process.kill()


def play(spec, commands, max_turns=300, enforce_time=False, wall=5.0, trace=None):
    game = Game(spec)
    bots = [Bot(commands[0], "player 0", wall), Bot(commands[1], "player 1", wall)]
    result = {"map": spec["map_id"], "turns": 0, "loser": None, "reason": None,
              "overruns": [0, 0]}
    try:
        first = [initial_text(game, 0), initial_text(game, 1)]
        for turn in range(1, max_turns + 1):
            game.turn = turn
            parsed = [None, None]
            lines = ["", ""]
            before = game.snapshot() if trace else None
            for seat in (0, 1):
                payload = (first[seat] if turn == 1 else "") + turn_text(game, seat)
                limit = 1000.0 if turn == 1 else 50.0
                try:
                    line, _, over = bots[seat].ask(payload, limit)
                    lines[seat] = line
                    if over:
                        result["overruns"][seat] += 1
                        if enforce_time and result["overruns"][seat] >= STRIKES_TO_LOSE:
                            raise Illegal("player %d ran out of time (strike %d)"
                                          % (seat, result["overruns"][seat]))
                    parsed[seat] = parse(line, game, seat)
                except Illegal as exc:
                    result.update(loser=seat, reason=str(exc), turns=turn)
                    if trace:
                        trace.write(json.dumps({"map": spec["map_id"], "turn": turn,
                                                "state": before, "commands": lines,
                                                "fatal": str(exc)}) + "\n")
                    return finish(game, result)
            if trace:
                trace.write(json.dumps({"map": spec["map_id"], "turn": turn,
                                        "state": before, "commands": lines}) + "\n")
            game.apply_turn(parsed)
            result["turns"] = turn
            over, why = game.ended()
            if over:
                result["reason"] = why
                break
        else:
            result["reason"] = "turn %d" % max_turns
        return finish(game, result)
    finally:
        for bot in bots:
            bot.close()


def finish(game, result):
    result["scores"] = list(game.scores)
    result["shacks"] = [list(inv) for inv in game.inventories]
    result["trees_left"] = len(game.trees)
    result["trolls"] = [sum(1 for u in game.units if u["player"] == p) for p in (0, 1)]
    if result["loser"] is not None:
        result["winner"] = 1 - result["loser"]
    elif game.scores[0] == game.scores[1]:
        result["winner"] = None
    else:
        result["winner"] = 0 if game.scores[0] > game.scores[1] else 1
    return result


def main():
    ap = argparse.ArgumentParser(description="play two bots against each other")
    ap.add_argument("--maps", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                   "maps"))
    ap.add_argument("--p0", required=True, help="command line for player 0")
    ap.add_argument("--p1", required=True, help="command line for player 1")
    ap.add_argument("--both-seats", action="store_true",
                    help="play every map twice, swapping the seats")
    ap.add_argument("--limit", type=int, default=0, help="use only the first N maps")
    ap.add_argument("--turns", type=int, default=300)
    ap.add_argument("--enforce-time", action="store_true",
                    help="the third strike loses the match, as on the platform")
    ap.add_argument("--wall", type=float, default=5.0,
                    help="seconds a bot may stay silent before it loses the match (default 5)")
    ap.add_argument("--trace", help="write one JSON line per turn (state + both command lines)")
    ap.add_argument("--json", help="write every match result here")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(args.maps) if f.endswith(".json"))
    if args.limit:
        files = files[:args.limit]
    trace = open(args.trace, "w") if args.trace else None
    matches, wins, illegal = [], [0, 0], 0
    try:
        for name in files:
            with open(os.path.join(args.maps, name)) as handle:
                spec = json.load(handle)
            arrangements = [(args.p0, args.p1, 0)]
            if args.both_seats:
                arrangements.append((args.p1, args.p0, 1))
            for left, right, p0_seat in arrangements:
                r = play(spec, (left, right), args.turns, args.enforce_time, args.wall, trace)
                r["p0_is"] = "candidate" if p0_seat else "reference"
                # normalise: seat of the FIRST command line given on the argv
                ours = 0 if p0_seat == 0 else 1
                r["first_program_seat"] = ours
                r["first_program_score"] = r["scores"][ours]
                r["second_program_score"] = r["scores"][1 - ours]
                if r["loser"] is not None:
                    illegal += 1
                if r["winner"] is not None:
                    wins[0 if r["winner"] == ours else 1] += 1
                matches.append(r)
                print("%-14s seat %d  %4d : %-4d  %-3s  %d turns  %s"
                      % (spec["map_id"], ours, r["first_program_score"],
                         r["second_program_score"],
                         "win" if r["winner"] == ours else ("draw" if r["winner"] is None
                                                            else "loss"),
                         r["turns"], r["reason"]))
    finally:
        if trace:
            trace.close()
    total = len(matches)
    played = wins[0] + wins[1]
    print("\n%d matches, %d wins for the first program, %d for the second, "
          "%d draws, %d ended on an illegal command, a crash or a timeout"
          % (total, wins[0], wins[1], total - played, illegal))
    if total:
        margins = [m["first_program_score"] - m["second_program_score"] for m in matches]
        print("mean margin %+.1f  (first program minus second)"
              % (sum(margins) / len(margins)))
    if args.json:
        with open(args.json, "w") as handle:
            json.dump(matches, handle, indent=1)
        print("wrote %s" % args.json)
    return 1 if illegal else 0


if __name__ == "__main__":
    sys.exit(main())
