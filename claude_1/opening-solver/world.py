"""The opening solver's world: a real panel map, one player, the referee's rules in a fast form.

Everything here mirrors `sim/engine.py` (itself a mirror of `rust/src/game/engine.rs`) for ONE
player with no opponent.  It exists because the search needs tens of thousands of turn
transitions per map and the referee's `step` (BFS on every MOVE) costs ~0.2 ms plus 0.5 ms a
deep copy.  Nothing this model says is trusted on its own: every schedule the solver keeps is
replayed through `sim/engine.py` command by command (`replay.py`) and the two must agree to the
turn.  Where this file and the referee disagree, the referee wins and this file is the bug.

Per-turn order (engine.rs::step): MOVE, HARVEST, PLANT, CHOP, PICK, TRAIN, DROP, MINE, then the
trees tick and the turn counter advances.  One command per troll per turn (the first survives);
TRAIN is a shack-level command that may accompany a troll's command on the same turn.
"""
from __future__ import annotations

from collections import deque

TYPES = ("PLUM", "LEMON", "APPLE", "BANANA")
ITEMS = ("PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD")
IDX = {n: i for i, n in enumerate(ITEMS)}
PLUM, LEMON, APPLE, BANANA, IRON, WOOD = range(6)
PLANT_COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
HEALTH_BASE = {"PLUM": 4, "LEMON": 4, "APPLE": 8, "BANANA": 2}
HEALTH_SLOPE = {"PLUM": 2, "LEMON": 2, "APPLE": 3, "BANANA": 1}
MAX_SIZE, MAX_FRUITS = 4, 3
WOOD_POINTS = 4
ORTH = ((0, 1), (1, 0), (0, -1), (-1, 0))


def training_cost(n, talents):
    ms, cc, hp, chop = talents
    return (n + ms * ms, n + cc * cc, n + hp * hp, 0, n + chop * chop, 0)


def bfs(walkable, sources):
    """`bot.main.bfs_distances`: sources seeded at 0 regardless of walkability."""
    dist = {}
    q = deque()
    for c in sources:
        if c not in dist:
            dist[c] = 0
            q.append(c)
    while q:
        x, y = q.popleft()
        d = dist[(x, y)] + 1
        for dx, dy in ORTH:
            n = (x + dx, y + dy)
            if n in walkable and n not in dist:
                dist[n] = d
                q.append(n)
    return dist


class Map:
    """Static geometry of one panel record for ONE seat, with every distance precomputed."""

    def __init__(self, rec, seat=0):
        self.rows = tuple(rec["rows"])
        self.w, self.h = len(self.rows[0]), len(self.rows)
        self.walk, self.iron, self.water, self.rock = set(), set(), set(), set()
        shacks = [None, None]
        for y, row in enumerate(self.rows):
            for x, ch in enumerate(row):
                c = (x, y)
                if ch == "0":
                    shacks[0] = c
                elif ch == "1":
                    shacks[1] = c
                elif ch == "+":
                    self.iron.add(c)
                elif ch == "~":
                    self.water.add(c)
                elif ch == "#":
                    self.rock.add(c)
                else:
                    self.walk.add(c)
        self.seat = seat
        self.shack = shacks[seat]
        self.opp_shack = shacks[1 - seat]
        self.has_iron = bool(self.iron)
        # distance tables from every walkable cell and from the shack (a troll spawns there)
        self.dist = {c: bfs(self.walk, [c]) for c in self.walk}
        self.dist[self.shack] = bfs(self.walk, [self.shack])
        self.reach = set(self.dist[self.shack]) - {self.shack}      # walkable cells a troll can use
        self.doors = sorted(c for c in self.reach if abs(c[0] - self.shack[0]) + abs(c[1] - self.shack[1]) <= 1)
        self.near_water = {c: any((c[0] + dx, c[1] + dy) in self.water for dx, dy in ORTH) for c in self.walk}
        self.near_iron = {c: any((c[0] + dx, c[1] + dy) in self.iron for dx, dy in ORTH) for c in self.walk}
        self.mine_cells = sorted(c for c in self.reach if self.near_iron[c])
        # in_range[speed][cell]: cells within `speed` BFS steps, sorted (engine.next_cell tie-break)
        self.in_range = {}
        for speed in (1, 2, 3, 4):
            table = {}
            for c, d in self.dist.items():
                table[c] = sorted(k for k, v in d.items() if v <= speed and k in self.walk)
            self.in_range[speed] = table

    def d(self, a, b):
        """Walking distance a -> b (both walkable, or a the shack); 9999 if unreachable."""
        return self.dist[a].get(b, 9999)

    def eff_cd(self, kind, cell):
        return PLANT_COOLDOWN[kind] - (WATER_BOOST[kind] if self.near_water.get(cell) else 0)

    def next_cell(self, cur, target, speed):
        """engine.next_cell for a reachable walkable target."""
        dt = self.dist[target]
        if cur in dt and dt[cur] <= speed:
            return target
        best, best_c = None, None
        for c in self.in_range[min(speed, 4)][cur]:
            v = dt.get(c)
            if v is None:
                continue
            if best is None or v < best:
                best, best_c = v, c
        return best_c if best_c is not None else cur

    def nearest_door(self, cur):
        return min(self.doors, key=lambda c: (self.d(cur, c), c))

    def nearest_mine_cell(self, cur):
        if not self.mine_cells:
            return None
        return min(self.mine_cells, key=lambda c: (self.d(cur, c), c))


class Unit:
    __slots__ = ("id", "x", "y", "ms", "cc", "hp", "chop", "carry", "task")

    def __init__(self, uid, x, y, ms, cc, hp, chop, carry=None, task=None):
        self.id, self.x, self.y = uid, x, y
        self.ms, self.cc, self.hp, self.chop = ms, cc, hp, chop
        self.carry = carry if carry is not None else [0] * 6
        self.task = task

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def total(self):
        return sum(self.carry)

    @property
    def free(self):
        return self.cc - sum(self.carry)

    def copy(self):
        return Unit(self.id, self.x, self.y, self.ms, self.cc, self.hp, self.chop,
                    list(self.carry), self.task.copy() if self.task is not None else None)


class Plant:
    __slots__ = ("kind", "size", "health", "fruits", "cd", "own")

    def __init__(self, kind, size, health, fruits, cd, own=False):
        self.kind, self.size, self.health, self.fruits, self.cd, self.own = kind, size, health, fruits, cd, own

    def copy(self):
        return Plant(self.kind, self.size, self.health, self.fruits, self.cd, self.own)


class State:
    """One player's world at the START of `turn` (the state block the referee emits before C_t)."""

    __slots__ = ("m", "turn", "inv", "units", "plants", "next_id", "log", "trains")

    def __init__(self, m: Map, draw, trees0):
        self.m = m
        self.turn = 1
        self.inv = list(draw)
        s = m.shack
        # the referee numbers units 0 (seat 0) and 1 (seat 1); the next spawn is 2 either way
        self.units = [Unit(m.seat, s[0], s[1], 1, 1, 1, 1)]
        self.next_id = 2
        self.plants = {}
        for t in trees0:
            self.plants[(t["x"], t["y"])] = Plant(t["type"], t["size"], t["health"], t["fruits"], t["cur_cd"])
        self.log = []        # per turn: list of command strings (what the referee is fed)
        self.trains = []     # (turn, talents, unit id)

    def copy(self):
        s = State.__new__(State)
        s.m, s.turn, s.inv, s.next_id = self.m, self.turn, list(self.inv), self.next_id
        s.units = [u.copy() for u in self.units]
        s.plants = {c: p.copy() for c, p in self.plants.items()}
        s.log = list(self.log)
        s.trains = list(self.trains)
        return s

    @property
    def score(self):
        return sum(self.inv[0:4]) + WOOD_POINTS * self.inv[WOOD]

    def chop_sum(self):
        return sum(u.chop for u in self.units)

    def affordable(self, talents, inv=None):
        inv = self.inv if inv is None else inv
        cost = training_cost(len(self.units), talents)
        pay = (0, 1, 2, 4) if self.m.has_iron else (0, 1, 2)
        return all(inv[i] >= cost[i] for i in pay)

    def shack_free(self):
        return not any(u.pos == self.m.shack for u in self.units)

    # ---------------------------------------------------------------- the turn transition
    def step(self, cmds, train=None):
        """Apply one turn.  `cmds`: {uid: (verb, arg)} with verb in MOVE/HARVEST/PLANT/CHOP/PICK/
        DROP/MINE/WAIT; MOVE's arg is the target cell, PLANT/PICK's the kind.  `train`: talents or
        None.  Records the referee command line in `self.log`."""
        m = self.m
        by_id = {u.id: u for u in self.units}
        line = []
        # 1 MOVE (one player: engine.apply_moves for this player's units)
        moves = {}
        for uid, (verb, arg) in cmds.items():
            u = by_id[uid]
            if verb == "MOVE":
                moves[uid] = arg
                line.append(f"MOVE {uid} {arg[0]} {arg[1]}")
            elif verb == "WAIT":
                line.append(f"WAIT {uid}")
            elif verb in ("PLANT", "PICK"):
                line.append(f"{verb} {uid} {arg}")
            else:
                line.append(f"{verb} {uid}")
        if moves:
            self._apply_moves(moves)
        # 2 HARVEST
        cells = {}
        for uid, (verb, _) in cmds.items():
            if verb == "HARVEST":
                u = by_id[uid]
                p = self.plants.get(u.pos)
                if p is not None and p.fruits > 0:
                    cells.setdefault(u.pos, []).append(u)
        for cell, trolls in cells.items():
            p = self.plants[cell]
            idx = IDX[p.kind]
            for i in range(1, MAX_FRUITS + 1):
                if p.fruits == 0:
                    break
                for u in trolls:
                    if u.hp >= i and u.total < u.cc:
                        u.carry[idx] += 1
                        if p.fruits > 0:
                            p.fruits -= 1
        # 3 PLANT (snapshot of choppable cells first)
        choppable = set(self.plants)
        intents = {}
        for uid, (verb, arg) in cmds.items():
            if verb == "PLANT":
                u = by_id[uid]
                if u.pos in m.walk and u.pos not in self.plants and u.carry[IDX[arg]] > 0:
                    intents.setdefault(u.pos, []).append((u, arg))
        for pos, entries in intents.items():
            if len({e[1] for e in entries}) != 1:
                continue
            kind = entries[0][1]
            for u, _ in entries:
                u.carry[IDX[kind]] -= 1
            self.plants[pos] = Plant(kind, 0, HEALTH_BASE[kind], 0, 0, own=True)
        # 4 CHOP
        cells = {}
        for uid, (verb, _) in cmds.items():
            if verb == "CHOP":
                u = by_id[uid]
                if u.chop > 0 and u.pos in choppable and u.pos in self.plants:
                    cells.setdefault(u.pos, []).append(u)
        for cell, choppers in cells.items():
            p = self.plants[cell]
            for u in choppers:
                p.health = max(p.health - u.chop, 0)
            if p.health <= 0:
                remaining = p.size
                i = 0
                while i < p.size and remaining > 0:
                    for u in choppers:
                        if u.free > 0:
                            u.carry[WOOD] += 1
                            remaining -= 1
                    i += 1
                del self.plants[cell]
        # 5 PICK
        for uid, (verb, arg) in cmds.items():
            if verb == "PICK":
                u = by_id[uid]
                if self._near_shack(u) and u.free > 0 and self.inv[IDX[arg]] > 0:
                    self.inv[IDX[arg]] -= 1
                    u.carry[IDX[arg]] += 1
        # 6 TRAIN
        if train is not None:
            line.append("TRAIN %d %d %d %d" % tuple(train))
            if self.affordable(train) and self.shack_free():
                cost = training_cost(len(self.units), train)
                pay = (0, 1, 2, 4) if m.has_iron else (0, 1, 2)
                for i in pay:
                    self.inv[i] -= cost[i]
                nu = Unit(self.next_id, m.shack[0], m.shack[1], train[0], train[1], train[2], train[3])
                self.units.append(nu)
                self.trains.append((self.turn, tuple(train), self.next_id))
                self.next_id += 1
        # 7 DROP
        for uid, (verb, _) in cmds.items():
            if verb == "DROP":
                u = by_id[uid]
                if self._near_shack(u):
                    for i in range(6):
                        self.inv[i] += u.carry[i]
                        u.carry[i] = 0
        # 8 MINE
        for uid, (verb, _) in cmds.items():
            if verb == "MINE":
                u = by_id[uid]
                if u.chop > 0 and u.free > 0 and m.near_iron.get(u.pos):
                    u.carry[IRON] += min(u.chop, u.free)
        # tick
        for cell, p in self.plants.items():
            if p.cd > 0:
                p.cd -= 1
            if p.cd == 0 and p.health > 0:
                if p.size < MAX_SIZE:
                    p.size += 1
                    p.health += HEALTH_SLOPE[p.kind]
                    p.cd = m.eff_cd(p.kind, cell)
                elif p.fruits < MAX_FRUITS:
                    p.fruits += 1
                    p.cd = m.eff_cd(p.kind, cell)
        self.log.append(line)
        self.turn += 1

    def _near_shack(self, u):
        s = self.m.shack
        return abs(u.x - s[0]) + abs(u.y - s[1]) <= 1

    def _apply_moves(self, intents):
        """engine.apply_moves for one player: contested cells go to the highest id; chains and
        circular swaps resolve; a blocked mover stays."""
        m = self.m
        units = self.units
        target = {}
        for u in units:
            target[u.id] = m.next_cell(u.pos, intents[u.id], u.ms) if u.id in intents else u.pos
        occupied = {u.pos for u in units}
        movers = [u for u in units if target[u.id] != u.pos]
        movers.sort(key=lambda u: -u.id)
        progress, resolve_blocking = True, False
        while progress:
            progress = False
            freq = {}
            for u in movers:
                freq[target[u.id]] = freq.get(target[u.id], 0) + 1
            for u in list(movers):
                cell = target[u.id]
                if (resolve_blocking or freq[cell] == 1) and cell not in occupied:
                    occupied.discard(u.pos)
                    occupied.add(cell)
                    u.x, u.y = cell
                    movers.remove(u)
                    progress = True
                    resolve_blocking = False
            if progress:
                continue
            pos_to_unit = {u.pos: u for u in movers}
            for start in list(movers):
                path = [start]
                while True:
                    nxt = pos_to_unit.get(target[path[-1].id])
                    if nxt is None:
                        break
                    if nxt is path[0]:
                        for u in path:
                            u.x, u.y = target[u.id]
                            movers.remove(u)
                        progress = True
                        break
                    if nxt in path:
                        break
                    path.append(nxt)
                if progress:
                    break
            if not progress and not resolve_blocking:
                resolve_blocking = True
                progress = True


def load_panel(path, limit=0):
    import json
    out = []
    with open(path) as fh:
        for line in fh:
            if not line.strip():
                continue
            out.append(json.loads(line))
            if limit and len(out) >= limit:
                break
    return out


def make_state(item, seat=0):
    m = Map(item["rec"], seat)
    s = State(m, item["draw"], item["rec"]["trees0"])
    for t in item["rec"]["trees0"]:
        assert m.eff_cd(t["type"], (t["x"], t["y"])) == t["cd_eff"], ("cd_eff disagrees", t)
    return s
