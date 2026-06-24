import random
from bot.main import PLANT_COOLDOWN, bfs_distances, MAX_SIZE, MAX_FRUITS
from sim.state import GameState, SimUnit, SimPlant
from sim.engine import tick_plants

WIDTH, HEIGHT = 16, 8
FRUITS = ["PLUM", "LEMON", "APPLE", "BANANA"]


def _mirror(cell):
    return (WIDTH - 1 - cell[0], HEIGHT - 1 - cell[1])


def _all_reachable(walkable, shack):
    nbrs = [(shack[0]+dx, shack[1]+dy) for dx, dy in ((0,1),(1,0),(0,-1),(-1,0))]
    dist = bfs_distances(walkable, [n for n in nbrs if n in walkable])
    return all(c in dist for c in walkable)


def generate(seed):
    rnd = random.Random(seed)
    while True:
        cells = {(x, y) for x in range(WIDTH) for y in range(HEIGHT)}
        s0 = (rnd.randrange(WIDTH // 2), rnd.randrange(HEIGHT))
        s1 = _mirror(s0)
        if s1 == s0:
            continue
        walkable = cells - {s0, s1}
        if not _all_reachable(walkable, s0):
            continue

        inv0 = [rnd.randint(2, 10) for _ in range(4)] + [0, 0]
        inv1 = list(inv0)  # symmetric start

        plants = []
        used = {s0, s1}
        for ftype in FRUITS:
            for _ in range(rnd.randint(1, 3)):
                free = list(walkable - used)
                if not free:
                    break
                cell = rnd.choice(free)
                mirror = _mirror(cell)
                if mirror in used or mirror == cell:
                    continue
                used.add(cell)
                used.add(mirror)
                base = PLANT_COOLDOWN[ftype]
                ticks = rnd.randint(1, base * (MAX_SIZE + MAX_FRUITS))
                for cpos in (cell, mirror):
                    p = SimPlant(ftype, cpos[0], cpos[1], 0, 6, 0, 0)
                    plants.append(p)
                # age both identically
                tmp = GameState(WIDTH, HEIGHT, walkable, [s0, s1], [inv0, inv1],
                                [], plants[-2:], [0, 0], 1, 2)
                for _ in range(ticks):
                    tick_plants(tmp)

        units = [SimUnit(0, 0, s0[0], s0[1], 1, 1, 1, 0, [0]*6),
                 SimUnit(1, 1, s1[0], s1[1], 1, 1, 1, 0, [0]*6)]
        game = GameState(WIDTH, HEIGHT, walkable, [s0, s1], [inv0, inv1],
                         units, plants, [0, 0], 1, 2)
        if any(p.fruits > 0 for p in game.plants):
            return game
