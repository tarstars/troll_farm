"""CodinGame Spring Challenge 2026 - Troll Farm bot (Wood league).

Single-file submission: paste this whole file into the CodinGame IDE.
Pure logic lives at module level so it can be unit-tested; the game loop runs
only under `if __name__ == "__main__"`.
"""
from collections import deque
from dataclasses import dataclass

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


def training_cost(n, talents):
    """Per-item resource cost to TRAIN a troll with `talents` given `n` own trolls.

    PLUM<-movementSpeed, LEMON<-carryCapacity, APPLE<-harvestPower; cost = n + stat².
    chopPower (talents[3]) costs IRON only in league 3+, so 0 here.
    """
    ms, cc, hp, _chop = talents
    cost = [0, 0, 0, 0, 0, 0]
    cost[ITEM_INDEX["PLUM"]] = n + ms * ms
    cost[ITEM_INDEX["LEMON"]] = n + cc * cc
    cost[ITEM_INDEX["APPLE"]] = n + hp * hp
    return cost


def _is_adjacent(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1


def _ortho_neighbors(cell):
    x, y = cell
    return [(x + dx, y + dy) for dx, dy in _NEIGHBORS]


# How far ahead to look for a tree to become ripe (game lasts 100 turns in Wood).
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
        key = (ripe + return_dist[tree.pos], walk)
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


PARAMS = {
    "topup_radius": 4,        # keep gathering across trees within this many steps
    "max_trolls": 5,          # cap on own troll count
    "train_specs": [(2, 3, 3, 0)],   # preferred (ms, cc, hp, chop), most-wanted first
    "min_turns_left_to_train": 25,   # stop training near the end
    "score_reserve": 0,       # min banked total to keep after a train
    "plant_enabled": False,   # orchard off until tuned (Plan 2)
    "plant_type": "BANANA",
    "orchard_cells": [],      # empty => planting effectively off until tuned
    "max_orchard": 4,
}


def _occupied_cells(state):
    return {t.pos for t in state.my_trolls} | {t.pos for t in state.opp_trolls}


def planting_commands(state, params, used_ids):
    if not params.get("plant_enabled") or not params.get("orchard_cells"):
        return []
    seed = params["plant_type"]
    seed_idx = ITEM_INDEX[seed]
    tree_cells = {t.pos for t in state.trees}
    # target cells still needing a tree
    open_cells = [c for c in params["orchard_cells"]
                  if c in state.walkable and c not in tree_cells]
    if not open_cells or len(tree_cells & set(params["orchard_cells"])) >= params["max_orchard"]:
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
    for spec in params["train_specs"]:
        cost = training_cost(n, spec)
        if all(state.my_inventory[i] >= cost[i] for i in range(6)):
            if banked - sum(cost) >= params["score_reserve"]:
                return f"TRAIN {spec[0]} {spec[1]} {spec[2]} {spec[3]}"
    return None


def decide(state, params):
    commands = []
    used_ids = set()
    plant_cmds = planting_commands(state, params, used_ids)
    for c in plant_cmds:
        used_ids.add(int(c.split()[1]))
    commands.extend(plant_cmds)

    shack_adj = [n for n in _ortho_neighbors(state.my_shack) if n in state.walkable]
    return_dist = bfs_distances(state.walkable, shack_adj)
    reserved = set()
    for troll in sorted(state.my_trolls, key=lambda t: t.id):
        if troll.id in used_ids:
            continue
        dist_t = bfs_distances(state.walkable, [troll.pos])
        cmd, reserved_pos = gather_command(state, troll, reserved, dist_t,
                                           return_dist, params)
        if reserved_pos is not None:
            reserved.add(reserved_pos)
        commands.append(cmd)

    train = training_command(state, params)
    if train is not None:
        commands.append(train)

    if not commands:
        commands = ["WAIT"]
    return commands


def parse_grid(grid_lines):
    """Parse the initial map. Returns (walkable_set, my_shack, opp_shack).

    Cell (x, y) is column x of row y. '.' = walkable grass; '0'/'1' = shacks
    (not walkable). Tree/iron/etc. terrain appears in later leagues.
    """
    walkable = set()
    my_shack = None
    opp_shack = None
    for y, line in enumerate(grid_lines):
        for x, ch in enumerate(line):
            if ch == "0":
                my_shack = (x, y)
            elif ch == "1":
                opp_shack = (x, y)
            else:
                walkable.add((x, y))
    return walkable, my_shack, opp_shack


def parse_turn(lines, walkable, my_shack, opp_shack, turn):
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
                      carry=f[8:14])
        if f[1] == 0:
            my_trolls.append(troll)
        else:
            opp_trolls.append(troll)
    return State(walkable=walkable, my_shack=my_shack, opp_shack=opp_shack,
                 my_inventory=my_inventory, opp_inventory=opp_inventory,
                 trees=trees, my_trolls=my_trolls, opp_trolls=opp_trolls,
                 turn=turn)


def main():
    """Game loop: read the map once, then act every turn."""
    width, height = (int(v) for v in input().split())
    grid_lines = [input() for _ in range(height)]
    walkable, my_shack, _opp_shack = parse_grid(grid_lines)

    def line_reader():
        while True:
            yield input()

    lines = line_reader()
    try:
        while True:
            state = parse_turn(lines, walkable, my_shack)
            print(choose_action(state), flush=True)
    except EOFError:
        pass


if __name__ == "__main__":
    main()
