from bot.main import (PLANT_COOLDOWN, MAX_SIZE, MAX_FRUITS, ITEM_INDEX,
                      ITEM_NAMES, training_cost, bfs_distances)
from sim.state import SimUnit, SimPlant

WATER_BOOST = {"PLUM": 5, "LEMON": 5, "APPLE": 7, "BANANA": 2}
WOOD_POINTS = 4


def _growth_cd(game, p):
    cd = PLANT_COOLDOWN[p.type]
    if any(abs(p.x - wx) + abs(p.y - wy) == 1 for wx, wy in game.water):
        cd -= WATER_BOOST[p.type]
    return cd


def tick_plants(game):
    for p in game.plants:
        if p.cooldown > 0:
            p.cooldown -= 1
        if p.cooldown == 0 and p.health > 0:
            if p.size < MAX_SIZE:
                p.size += 1
                p.cooldown = _growth_cd(game, p)
            elif p.fruits < MAX_FRUITS:
                p.fruits += 1
                p.cooldown = _growth_cd(game, p)


def recompute_scores(game):
    for p in (0, 1):
        inv = game.inventories[p]
        game.scores[p] = sum(inv[0:4]) + WOOD_POINTS * inv[ITEM_INDEX["WOOD"]]


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


def _plant_at(game, cell):
    for p in game.plants:
        if p.pos == cell:
            return p
    return None


def _near_shack(game, unit):
    sx, sy = game.shacks[unit.player]
    return abs(unit.x - sx) + abs(unit.y - sy) <= 1


def apply_harvest(game, unit_ids):
    by_id = {u.id: u for u in game.units}
    cells = {}
    for uid in unit_ids:
        u = by_id.get(uid)
        if u is None:
            continue
        plant = _plant_at(game, u.pos)
        if plant is not None and plant.fruits > 0:
            cells.setdefault(u.pos, []).append(u)
    for cell, trolls in cells.items():
        plant = _plant_at(game, cell)
        idx = ITEM_INDEX[plant.type]
        for i in range(1, MAX_FRUITS + 1):
            if plant.fruits == 0:
                break
            for u in trolls:
                if u.hp >= i and u.total < u.cc:
                    u.carry[idx] += 1
                    if plant.fruits > 0:
                        plant.fruits -= 1


def apply_drop(game, unit_ids):
    by_id = {u.id: u for u in game.units}
    for uid in unit_ids:
        u = by_id.get(uid)
        if u is None or not _near_shack(game, u):
            continue
        for i in range(6):
            game.inventories[u.player][i] += u.carry[i]
            u.carry[i] = 0


def apply_pick(game, picks):
    by_id = {u.id: u for u in game.units}
    for uid, type_name in picks:
        u = by_id.get(uid)
        if u is None or not _near_shack(game, u) or u.free <= 0:
            continue
        idx = ITEM_INDEX[type_name]
        if game.inventories[u.player][idx] > 0:
            game.inventories[u.player][idx] -= 1
            u.carry[idx] += 1


def apply_plant(game, plants):
    by_id = {u.id: u for u in game.units}
    for uid, type_name in plants:
        u = by_id.get(uid)
        if u is None or u.pos not in game.walkable or _plant_at(game, u.pos):
            continue
        idx = ITEM_INDEX[type_name]
        if u.carry[idx] > 0:
            u.carry[idx] -= 1
            game.plants.append(SimPlant(type_name, u.x, u.y, 0, 6, 0, 0))


def apply_train(game, player, talents):
    n = sum(1 for u in game.units if u.player == player)
    cost = training_cost(n, talents)
    inv = game.inventories[player]
    # IRON (slot 4) is only charged in Bronze (iron terrain present), mirroring
    # the referee's `if league >= 3` guard.
    pay = (0, 1, 2, 3, 4, 5) if game.iron else (0, 1, 2, 3, 5)
    if any(inv[i] < cost[i] for i in pay):
        return
    if any(u.pos == game.shacks[player] for u in game.units):
        return
    for i in pay:
        inv[i] -= cost[i]
    sx, sy = game.shacks[player]
    game.units.append(SimUnit(game.next_id, player, sx, sy,
                             talents[0], talents[1], talents[2], talents[3], [0]*6))
    game.next_id += 1


def apply_chop(game, unit_ids):
    by_id = {u.id: u for u in game.units}
    cells = {}
    for uid in unit_ids:
        u = by_id.get(uid)
        if u is None or u.chop == 0:
            continue
        plant = _plant_at(game, u.pos)
        if plant is not None:
            cells.setdefault(u.pos, []).append(u)
    dead = []
    for cell, choppers in cells.items():
        plant = _plant_at(game, cell)
        for u in choppers:
            plant.health = max(plant.health - u.chop, 0)
        if plant.health <= 0:
            remaining = plant.size
            i = 0
            while i < plant.size and remaining > 0:   # last wood can duplicate
                for u in choppers:
                    if u.free > 0:
                        u.carry[ITEM_INDEX["WOOD"]] += 1
                        remaining -= 1
                i += 1
            dead.append(plant)
    game.plants = [p for p in game.plants if p not in dead]


def apply_mine(game, unit_ids):
    by_id = {u.id: u for u in game.units}
    for uid in unit_ids:
        u = by_id.get(uid)
        if u is None or u.chop == 0 or u.free <= 0:
            continue
        if any(abs(u.x - ix) + abs(u.y - iy) == 1 for ix, iy in game.iron):
            for _ in range(min(u.chop, u.free)):
                u.carry[ITEM_INDEX["IRON"]] += 1


def _parse(cmds):
    p = {"move": {}, "harvest": [], "plant": [], "chop": [], "pick": [],
         "train": [], "drop": [], "mine": []}
    used = set()
    for raw in cmds:
        parts = raw.strip().split()
        if not parts:
            continue
        verb = parts[0].upper()
        if verb in ("MSG", "WAIT"):
            continue
        if verb == "TRAIN":
            p["train"].append((int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
            continue
        uid = int(parts[1])
        if uid in used:
            continue
        used.add(uid)
        if verb == "MOVE":
            p["move"][uid] = (int(parts[2]), int(parts[3]))
        elif verb == "HARVEST":
            p["harvest"].append(uid)
        elif verb == "DROP":
            p["drop"].append(uid)
        elif verb == "CHOP":
            p["chop"].append(uid)
        elif verb == "MINE":
            p["mine"].append(uid)
        elif verb == "PLANT":
            p["plant"].append((uid, parts[2].upper()))
        elif verb == "PICK":
            p["pick"].append((uid, parts[2].upper()))
    return p


def step(game, cmds0, cmds1):
    a, b = _parse(cmds0), _parse(cmds1)
    # Referee priority order: MOVE 1, HARVEST 2, PLANT 3, CHOP 4, PICK 5,
    # TRAIN 6, DROP 7, MINE 8 — then plants tick, scores recompute, turn++.
    apply_moves(game, {**a["move"], **b["move"]})
    apply_harvest(game, a["harvest"] + b["harvest"])
    apply_plant(game, a["plant"] + b["plant"])
    apply_chop(game, a["chop"] + b["chop"])
    apply_pick(game, a["pick"] + b["pick"])
    for player, parsed in ((0, a), (1, b)):
        for talents in parsed["train"]:
            apply_train(game, player, talents)
    apply_drop(game, a["drop"] + b["drop"])
    apply_mine(game, a["mine"] + b["mine"])
    tick_plants(game)
    recompute_scores(game)
    game.turn += 1
