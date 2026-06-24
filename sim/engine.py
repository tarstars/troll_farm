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


def apply_moves(game, intents):
    by_id = {u.id: u for u in game.units}
    for player in (0, 1):
        units = [u for u in game.units if u.player == player]
        # desired final cell for each unit (movers via next_cell, others stay)
        target = {}
        for u in units:
            if u.id in intents:
                target[u.id] = next_cell(game.walkable, u.pos, intents[u.id], u.ms)
            else:
                target[u.id] = u.pos
        occupied = {u.pos for u in units}
        # drop non-movers (cell already occupied and unchanged)
        movers = [u for u in units if target[u.id] != u.pos]
        # process by descending id so the highest id wins a contested cell
        movers.sort(key=lambda u: -u.id)
        progress = True
        resolve_blocking = False
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
            # circular swaps: follow target -> occupant chains looking for a loop
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
    _ = by_id  # (kept for readability; not otherwise needed)
