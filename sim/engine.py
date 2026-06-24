from bot.main import (PLANT_COOLDOWN, MAX_SIZE, MAX_FRUITS, ITEM_INDEX,
                      ITEM_NAMES, training_cost, bfs_distances)
from sim.state import SimUnit, SimPlant


def tick_plants(game):
    base = PLANT_COOLDOWN
    for p in game.plants:
        if p.cooldown > 0:
            p.cooldown -= 1
        if p.cooldown == 0 and p.health > 0:
            if p.size < MAX_SIZE:
                p.size += 1
                p.cooldown = base[p.type]
            elif p.fruits < MAX_FRUITS:
                p.fruits += 1
                p.cooldown = base[p.type]


def recompute_scores(game):
    for p in (0, 1):
        game.scores[p] = sum(game.inventories[p][0:4])


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def next_cell(walkable, current, target, speed):
    source_dist = bfs_distances(walkable, [current])
    if target in source_dist and source_dist[target] <= speed:
        return target

    if target not in source_dist:
        # target unreachable: aim at reachable cells closest (Manhattan) to it
        best = min(_manhattan(target, c) for c in source_dist)
        goals = [c for c in source_dist if _manhattan(target, c) == best]
        target_dist = bfs_distances(walkable, goals)
    else:
        target_dist = bfs_distances(walkable, [target])

    in_range = [c for c, d in source_dist.items() if d <= speed and c in target_dist]
    best = min(target_dist[c] for c in in_range)
    return min(c for c in in_range if target_dist[c] == best)
