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


def choose_action(state):
    """Pick this turn's command for our troll."""
    troll = state.my_troll

    # Carrying: bank it. DROP if next to shack, else walk toward shack.
    if troll.carried >= troll.carry_capacity:
        if _is_adjacent(troll.pos, state.my_shack):
            return f"DROP {troll.id}"
        return f"MOVE {troll.id} {state.my_shack[0]} {state.my_shack[1]}"

    # Empty-handed: if standing on a tree that has fruit, grab it now.
    for tree in state.trees:
        if tree.pos == troll.pos and tree.fruits > 0:
            return f"HARVEST {troll.id}"

    # Otherwise pick the tree with the cheapest round trip:
    #   walk to tree + wait for it to ripen + carry back to the shack.
    walkable = state.walkable
    tdist = bfs_distances(walkable, [troll.pos])
    shack_adj = [n for n in _ortho_neighbors(state.my_shack) if n in walkable]
    sdist = bfs_distances(walkable, shack_adj)

    best_key = None
    best_target = None
    for tree in state.trees:
        if tree.pos not in tdist or tree.pos not in sdist:
            continue  # unreachable, or can't get back to the shack
        walk = tdist[tree.pos]
        ripe = _ticks_until_ripe(tree, walk)
        if ripe is None:
            continue
        cost = ripe + sdist[tree.pos]  # turns to hold a fruit + turns to bank it
        key = (cost, walk)             # tie-break: nearer tree
        if best_key is None or key < best_key:
            best_key = key
            best_target = tree

    if best_target is None:
        return "WAIT"
    if best_target.pos == troll.pos:
        return "WAIT"  # camping a not-yet-ripe target
    return f"MOVE {troll.id} {best_target.x} {best_target.y}"


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
