"""CodinGame Spring Challenge 2026 - Troll Farm bot.

Single-file submission: paste this whole file into the CodinGame IDE.
Pure logic lives at module level so it can be unit-tested; the game loop runs
only under `if __name__ == "__main__"`.
"""
from collections import deque
from dataclasses import dataclass

# Bump on each submitted change; emitted as `MSG v<VERSION>` on turn 1 so the
# running build is identifiable in the replay.
VERSION = "0.6.1"

# Base growth cooldown per tree type (referee Constants.PLANT_COOLDOWN, no water in Wood).
PLANT_COOLDOWN = {"PLUM": 8, "LEMON": 8, "APPLE": 9, "BANANA": 6}
MAX_SIZE = 4
MAX_FRUITS = 3

# Item constants for multi-troll data model
ITEM_NAMES = ["PLUM", "LEMON", "APPLE", "BANANA", "IRON", "WOOD"]
ITEM_INDEX = {name: i for i, name in enumerate(ITEM_NAMES)}
TOTAL_TURNS = 300


def predict_fruits(plant_type, size, fruits, cooldown, ticks):
    """Fruit count after `ticks` referee ticks, mirroring Plant.tick (no water).

    Each tick: cooldown decrements; when it reaches 0 the tree grows a size
    (until MAX_SIZE) or, if full size, produces a fruit (until MAX_FRUITS),
    then cooldown resets to the type's base.
    """
    base = PLANT_COOLDOWN[plant_type]
    for _ in range(ticks):
        if cooldown > 0:
            cooldown -= 1
        if cooldown == 0:
            if size < MAX_SIZE:
                size += 1
                cooldown = base
            elif fruits < MAX_FRUITS:
                fruits += 1
                cooldown = base
    return fruits


_NEIGHBORS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def bfs_distances(walkable, sources):
    """Breadth-first distance (in steps) from `sources` over `walkable` cells.

    `walkable` is a set of (x, y) cells; `sources` an iterable of (x, y).
    Returns {(x, y): distance}; unreachable cells are absent. Mirrors
    Board.getDistances: each source is seeded at distance 0 *regardless of
    walkability* (a troll spawns on its non-walkable shack), and only walkable
    neighbours are traversable.
    """
    dist = {}
    queue = deque()
    for cell in sources:
        if cell not in dist:
            dist[cell] = 0
            queue.append(cell)
    while queue:
        x, y = queue.popleft()
        for dx, dy in _NEIGHBORS:
            n = (x + dx, y + dy)
            if n in walkable and n not in dist:
                dist[n] = dist[(x, y)] + 1
                queue.append(n)
    return dist


@dataclass
class Troll:
    id: int
    x: int
    y: int
    movement_speed: int
    carry_capacity: int
    harvest_power: int
    carry: list  # counts per item index (length 6)
    chop_power: int = 0

    @property
    def pos(self):
        return (self.x, self.y)

    @property
    def total_carried(self):
        return sum(self.carry)

    @property
    def free_capacity(self):
        return self.carry_capacity - self.total_carried


@dataclass
class Tree:
    type: str
    x: int
    y: int
    size: int
    health: int
    fruits: int
    cooldown: int

    @property
    def pos(self):
        return (self.x, self.y)


@dataclass
class State:
    walkable: set
    my_shack: tuple
    opp_shack: tuple
    my_inventory: list   # counts per item index (length 6)
    opp_inventory: list
    trees: list
    my_trolls: list
    opp_trolls: list
    turn: int
    iron_cells: frozenset = frozenset()    # IRON terrain cells (mine from adjacent)
    water_cells: frozenset = frozenset()   # WATER cells (trees nearby grow faster)


def training_cost(n, talents):
    """Per-item resource cost to TRAIN a troll with `talents` given `n` own trolls.

    PLUM<-movementSpeed, LEMON<-carryCapacity, APPLE<-harvestPower,
    IRON<-chopPower; cost = n + stat². (In Bronze every troll costs n+chop² IRON;
    callers ignore the IRON slot in pre-Bronze leagues where iron isn't charged.)
    """
    ms, cc, hp, chop = talents
    cost = [0, 0, 0, 0, 0, 0]
    cost[ITEM_INDEX["PLUM"]] = n + ms * ms
    cost[ITEM_INDEX["LEMON"]] = n + cc * cc
    cost[ITEM_INDEX["APPLE"]] = n + hp * hp
    cost[ITEM_INDEX["IRON"]] = n + chop * chop
    return cost


def _is_adjacent(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


def _ortho_neighbors(cell):
    x, y = cell
    return [(x + dx, y + dy) for dx, dy in _NEIGHBORS]


# How far ahead to look for a tree to become ripe (league-2 game is 300 turns, 120 is a generous look-ahead).
RIPEN_HORIZON = 120


def _ticks_until_ripe(tree, min_offset):
    """Smallest tick offset >= min_offset at which `tree` will hold >=1 fruit.

    Returns None if it stays fruitless within RIPEN_HORIZON.
    """
    for offset in range(min_offset, RIPEN_HORIZON + 1):
        if predict_fruits(tree.type, tree.size, tree.fruits, tree.cooldown, offset) > 0:
            return offset
    return None


def best_tree(state, troll, reserved, dist_t, return_dist, params):
    best = None
    best_key = None
    for tree in state.trees:
        if tree.pos in reserved:
            continue
        if tree.pos not in dist_t or tree.pos not in return_dist:
            continue
        walk = dist_t[tree.pos]
        ripe = _ticks_until_ripe(tree, walk)
        if ripe is None:
            continue
        # Prefer trees that already have fruit on arrival (wait == 0) over
        # camping an unripe one: idling on a slow tree wastes turns another
        # fruited tree could fill. Tie-break by round trip, then nearness.
        wait = ripe - walk
        key = (wait, ripe + return_dist[tree.pos], walk)
        if best_key is None or key < best_key:
            best_key = key
            best = tree
    return best


def _bank_command(troll, state):
    if _is_adjacent(troll.pos, state.my_shack):
        return f"DROP {troll.id}"
    return f"MOVE {troll.id} {state.my_shack[0]} {state.my_shack[1]}"


def gather_command(state, troll, reserved, dist_t, return_dist, params):
    # 1. Opportunistic harvest: standing on a fruited tree with room.
    if troll.free_capacity > 0:
        for tree in state.trees:
            if tree.pos == troll.pos and tree.fruits > 0:
                return f"HARVEST {troll.id}", tree.pos

    target = best_tree(state, troll, reserved, dist_t, return_dist, params)

    # 2. Carrying: bank unless a worthwhile top-up tree is within radius.
    if troll.total_carried > 0:
        if (troll.free_capacity == 0 or target is None
                or dist_t.get(target.pos, 1 << 30) > params["topup_radius"]):
            return _bank_command(troll, state), None

    # 3. Head for the target tree (or wait/camp).
    if target is None:
        return "WAIT", None
    if target.pos == troll.pos:
        return "WAIT", None  # camping a not-yet-ripe target
    return f"MOVE {troll.id} {target.x} {target.y}", target.pos


def _best_chop_target(state, troll, reserved, dist_t):
    """Tree for a chopper to fell: nearest the ENEMY shack first (deny them
    fruit + collect 4-pt wood), then nearest us, then biggest. None if none."""
    best = None
    best_key = None
    ox, oy = state.opp_shack
    for tree in state.trees:
        if tree.pos in reserved or tree.pos not in dist_t:
            continue
        d_enemy = abs(tree.x - ox) + abs(tree.y - oy)
        key = (d_enemy, dist_t[tree.pos], -tree.size)
        if best_key is None or key < best_key:
            best_key = key
            best = tree
    return best


def chop_command(state, troll, reserved, dist_t, params):
    """A chopper (chop_power>0): mine iron when next to it, fell trees near the
    enemy camp for wood, and carry the wood home. Returns (command, reserved_pos).
    """
    # Mine iron when next to it, but only until we have enough banked to fund
    # training -- otherwise a chopper that spawns by iron mines forever and never
    # chops. Iron still being carried counts toward the target.
    iron_have = state.my_inventory[ITEM_INDEX["IRON"]] + troll.carry[ITEM_INDEX["IRON"]]
    if troll.free_capacity > 0 and iron_have < params.get("iron_target", 18):
        for cell in state.iron_cells:
            if _is_adjacent(troll.pos, cell):
                return f"MINE {troll.id}", None

    target = _best_chop_target(state, troll, reserved, dist_t)

    # Carry resources home when full or out of chop targets.
    if troll.total_carried > 0 and (troll.free_capacity == 0 or target is None):
        if _is_adjacent(troll.pos, state.my_shack):
            return f"DROP {troll.id}", None
        return f"MOVE {troll.id} {state.my_shack[0]} {state.my_shack[1]}", None

    # Standing on a tree -> chop it.
    for tree in state.trees:
        if tree.pos == troll.pos:
            return f"CHOP {troll.id}", tree.pos

    if target is None:
        # nothing to chop yet: advance toward the enemy camp to find trees.
        return f"MOVE {troll.id} {state.opp_shack[0]} {state.opp_shack[1]}", None
    return f"MOVE {troll.id} {target.x} {target.y}", target.pos


PARAMS = {
    "topup_radius": 4,        # keep gathering across trees within this many steps
    "max_trolls": 5,          # cap on own troll count
    # (ms, cc, hp, chop), most-wanted first; the last is a guaranteed-affordable
    # fallback (cost n+1 each) so training reliably fires from the 2..10 starting hand.
    "train_specs": [(2, 2, 2, 0), (1, 1, 1, 0)],
    # Bronze: chopper troll (ms, cc, hp, chop). Trained once when we have none,
    # most-wanted first with affordable fallbacks. Works near the enemy camp.
    "chopper_specs": [(2, 4, 0, 3), (1, 3, 0, 2), (1, 2, 0, 2)],
    "max_choppers": 1,
    "iron_target": 18,      # chopper mines iron until this much is banked, then chops
    "min_turns_left_to_train": 25,   # stop training near the end
    "score_reserve": 0,       # min banked total to keep after a train
    "plant_enabled": True,    # build a small near-shack orchard
    "plant_type": "BANANA",   # fastest cooldown (6) -> matures soonest
    "orchard_cells": [],      # filled by decide() with the empty footprint cells
    "max_orchard": 3,         # orchard footprint size (nearest cells to the shack)
}


def planting_commands(state, params, used_ids):
    if not params.get("plant_enabled") or not params.get("orchard_cells"):
        return []
    seed = params["plant_type"]
    seed_idx = ITEM_INDEX[seed]
    tree_cells = {t.pos for t in state.trees}
    # target cells still needing a tree
    open_cells = [c for c in params["orchard_cells"]
                  if c in state.walkable and c not in tree_cells]
    if not open_cells:
        return []
    for troll in sorted(state.my_trolls, key=lambda t: t.id):
        if troll.id in used_ids:
            continue
        carrying_seed = troll.carry[seed_idx] > 0
        if not carrying_seed and troll.total_carried > 0:
            continue  # busy carrying real fruit; let it gather/bank
        if carrying_seed:
            if troll.pos in open_cells:
                return [f"PLANT {troll.id} {seed}"]
            dist = bfs_distances(state.walkable, [troll.pos])
            reachable = [c for c in open_cells if c in dist]
            if reachable:
                tgt = min(reachable, key=lambda c: dist[c])
                return [f"MOVE {troll.id} {tgt[0]} {tgt[1]}"]
            return []
        # need a seed: pick one if we have it banked and we're at the shack
        if state.my_inventory[seed_idx] > 0 and _is_adjacent(troll.pos, state.my_shack):
            return [f"PICK {troll.id} {seed}"]
    return []


def training_command(state, params):
    """Return a TRAIN command string if conditions allow, else None."""
    n = len(state.my_trolls)
    if n >= params["max_trolls"]:
        return None
    if TOTAL_TURNS - state.turn <= params["min_turns_left_to_train"]:
        return None
    if any(t.pos == state.my_shack for t in state.my_trolls):
        return None  # shack cell occupied; TRAIN would be rejected
    banked = sum(state.my_inventory[:4])
    league3 = bool(state.iron_cells)        # iron terrain => Bronze (iron is charged)
    pay_idx = (0, 1, 2, 4) if league3 else (0, 1, 2)
    # In Bronze, train a chopper first (once) so we can fell trees for wood.
    choppers = sum(1 for t in state.my_trolls if t.chop_power >= 2)
    specs = []
    if league3 and choppers < params.get("max_choppers", 0):
        specs += list(params["chopper_specs"])
    specs += list(params["train_specs"])
    for spec in specs:
        cost = training_cost(n, spec)
        if all(state.my_inventory[i] >= cost[i] for i in pay_idx):
            if banked - sum(cost[:4]) >= params["score_reserve"]:
                return f"TRAIN {spec[0]} {spec[1]} {spec[2]} {spec[3]}"
    return None


def decide(state, params):
    walkable = state.walkable
    shack_adj = [n for n in _ortho_neighbors(state.my_shack) if n in walkable]
    return_dist = bfs_distances(walkable, shack_adj)

    commands_by_id = {}
    used_ids = set()
    reserved = set()   # shared tree reservations (choppers + gatherers)

    # Choppers (chop_power > 0) act first: mine iron when next to it and fell
    # trees near the ENEMY camp for 4-pt wood, denying the opponent their close
    # trees without touching our own fruit sources.
    for troll in sorted(state.my_trolls, key=lambda t: t.id):
        if troll.chop_power >= 2:
            dist_t = bfs_distances(walkable, [troll.pos])
            cmd, reserved_pos = chop_command(state, troll, reserved, dist_t, params)
            if reserved_pos is not None:
                reserved.add(reserved_pos)
            commands_by_id[troll.id] = cmd
            used_ids.add(troll.id)

    # Orchard planting claims one troll. The orchard is a small fixed FOOTPRINT
    # -- the nearest `max_orchard` walkable cells to the shack. We plant on the
    # empty ones until the footprint is full of trees. Counting only trees in the
    # footprint (not a broad radius) keeps planting bounded yet reliably active,
    # even when the map already scattered trees elsewhere near the shack.
    if params.get("plant_enabled"):
        tree_cells = {t.pos for t in state.trees}
        footprint = sorted(return_dist, key=lambda c: (return_dist[c], c))
        footprint = footprint[:params["max_orchard"]]
        empty_slots = [c for c in footprint if c not in tree_cells]
        if empty_slots:
            pparams = dict(params)
            pparams["orchard_cells"] = empty_slots
            for c in planting_commands(state, pparams, used_ids):
                tid = int(c.split()[1])
                used_ids.add(tid)
                commands_by_id[tid] = c

    # Gathering for the remaining (non-chopper) trolls, sharing the reservations.
    for troll in sorted(state.my_trolls, key=lambda t: t.id):
        if troll.id in used_ids:
            continue
        dist_t = bfs_distances(walkable, [troll.pos])
        cmd, reserved_pos = gather_command(state, troll, reserved, dist_t,
                                           return_dist, params)
        if reserved_pos is not None:
            reserved.add(reserved_pos)
        commands_by_id[troll.id] = cmd

    # Spread banking trolls across distinct shack-adjacent drop cells so they
    # don't funnel onto one cell and block each other. Tree-bound trolls already
    # have distinct targets via reservations. We emit FINAL targets and let the
    # referee step the trolls -- this avoids the earlier next-step "landing"
    # logic that could wedge a troll forever under the referee's random tie-break.
    sx, sy = state.my_shack
    bankers = sorted(tid for tid, c in commands_by_id.items()
                     if c == f"MOVE {tid} {sx} {sy}")
    for i, tid in enumerate(bankers):
        cell = shack_adj[i % len(shack_adj)] if shack_adj else state.my_shack
        commands_by_id[tid] = f"MOVE {tid} {cell[0]} {cell[1]}"

    commands = []
    if state.turn == 1:
        commands.append(f"MSG v{VERSION}")
    commands.extend(commands_by_id[tid] for tid in sorted(commands_by_id))

    train = training_command(state, params)
    if train is not None:
        commands.append(train)

    if not commands:
        commands = ["WAIT"]
    return commands


def parse_grid(grid_lines):
    """Parse the initial map. Returns (walkable, my_shack, opp_shack, iron, water).

    Cell (x, y) is column x of row y. '.' grass (walkable), '0'/'1' shacks,
    '~' water, '#' rock, '+' iron. Only GRASS is walkable; iron and water cells
    are returned separately (Bronze: mine iron, trees fruit faster near water).
    """
    walkable = set()
    iron = set()
    water = set()
    my_shack = None
    opp_shack = None
    for y, line in enumerate(grid_lines):
        for x, ch in enumerate(line):
            if ch == "0":
                my_shack = (x, y)
            elif ch == "1":
                opp_shack = (x, y)
            elif ch == ".":
                walkable.add((x, y))
            elif ch == "+":
                iron.add((x, y))
            elif ch == "~":
                water.add((x, y))
    return walkable, my_shack, opp_shack, frozenset(iron), frozenset(water)


def parse_turn(lines, walkable, my_shack, opp_shack, turn,
               iron_cells=frozenset(), water_cells=frozenset()):
    """Build a State for this turn from an iterator of input lines."""
    my_inventory = [int(v) for v in next(lines).split()]
    opp_inventory = [int(v) for v in next(lines).split()]
    tree_count = int(next(lines))
    trees = []
    for _ in range(tree_count):
        t = next(lines).split()
        trees.append(Tree(t[0], int(t[1]), int(t[2]), int(t[3]),
                          int(t[4]), int(t[5]), int(t[6])))
    troll_count = int(next(lines))
    my_trolls = []
    opp_trolls = []
    for _ in range(troll_count):
        f = [int(v) for v in next(lines).split()]
        troll = Troll(id=f[0], x=f[2], y=f[3], movement_speed=f[4],
                      carry_capacity=f[5], harvest_power=f[6],
                      carry=f[8:14], chop_power=f[7])
        if f[1] == 0:
            my_trolls.append(troll)
        else:
            opp_trolls.append(troll)
    return State(walkable=walkable, my_shack=my_shack, opp_shack=opp_shack,
                 my_inventory=my_inventory, opp_inventory=opp_inventory,
                 trees=trees, my_trolls=my_trolls, opp_trolls=opp_trolls,
                 turn=turn, iron_cells=iron_cells, water_cells=water_cells)


def main():
    """Game loop: read the map once, then act every turn."""
    width, height = (int(v) for v in input().split())
    grid_lines = [input() for _ in range(height)]
    walkable, my_shack, opp_shack, iron_cells, water_cells = parse_grid(grid_lines)

    def line_reader():
        while True:
            yield input()

    lines = line_reader()
    turn = 0
    try:
        while True:
            turn += 1
            state = parse_turn(lines, walkable, my_shack, opp_shack, turn,
                               iron_cells, water_cells)
            print(";".join(decide(state, PARAMS)), flush=True)
    except EOFError:
        pass


if __name__ == "__main__":
    main()
