from bot.main import training_cost

def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# Strong-troll specs the gatherer boss trains, most-wanted first. (2,2,2,2) is the
# fast balanced troll the real winner used; fallbacks stay affordable.
_GATH_SPECS = [(2, 2, 2, 2), (1, 2, 2, 0), (1, 1, 1, 0)]


def gatherer_boss_decide(game, player):
    """A competent FRUIT-economy opponent (no chopping): expands to strong, fast
    balanced trolls and harvests aggressively with distinct tree targets. Models
    the gatherer strategy that beats our chop-committed bot, so we can measure the
    chop-vs-gather/expansion balance against a real threat (not just the weak boss).
    """
    shack = game.shacks[player]
    mine = sorted((u for u in game.units if u.player == player), key=lambda u: u.id)
    inv = game.inventories[player]
    n = len(mine)
    cmds = ["MSG Out-gather you"]
    reserved = set()                       # distinct tree targets per troll
    fruited = [p for p in game.plants if p.fruits > 0]
    for u in mine:
        on_tree = [p for p in game.plants if p.pos == u.pos and p.fruits > 0]
        if on_tree and u.total < u.cc:                 # harvest underfoot
            cmds.append(f"HARVEST {u.id}")
            continue
        if u.total >= u.cc or (u.total > 0 and not fruited):   # bank when full / idle-carrying
            cmds.append(f"DROP {u.id}" if _dist(u.pos, shack) == 1
                        else f"MOVE {u.id} {shack[0]} {shack[1]}")
            continue
        avail = [p for p in fruited if p.pos not in reserved]
        if avail:
            t = min(avail, key=lambda p: _dist(u.pos, p.pos))
            reserved.add(t.pos)
            cmds.append(f"HARVEST {u.id}" if u.pos == t.pos
                        else f"MOVE {u.id} {t.x} {t.y}")
        elif u.total > 0:
            cmds.append(f"DROP {u.id}" if _dist(u.pos, shack) == 1
                        else f"MOVE {u.id} {shack[0]} {shack[1]}")
    # Expand to strong balanced trolls when affordable (and shack not occupied).
    if n < 4 and not any(u.pos == shack for u in mine):
        pay = (0, 1, 2, 4) if game.iron else (0, 1, 2)
        for spec in _GATH_SPECS:
            cost = training_cost(n, spec)
            if all(inv[i] >= cost[i] for i in pay):
                cmds.append(f"TRAIN {spec[0]} {spec[1]} {spec[2]} {spec[3]}")
                break
    return cmds


def boss_decide(game, player):
    shack = game.shacks[player]
    mine = [u for u in game.units if u.player == player]
    fruited = [p for p in game.plants if p.fruits > 0]
    cmds = ["MSG Eat your vegetables!"]
    for u in mine:
        if u.total >= u.cc:
            if _dist(u.pos, shack) == 1:
                cmds.append(f"DROP {u.id}")
            else:
                cmds.append(f"MOVE {u.id} {shack[0]} {shack[1]}")
            continue
        if not fruited:
            continue
        nearest = min(_dist(u.pos, p.pos) for p in fruited)
        pool = [p for p in fruited if _dist(u.pos, p.pos) > nearest] or fruited
        target = min(pool, key=lambda p: _dist(u.pos, p.pos))
        if u.pos == target.pos:
            cmds.append(f"HARVEST {u.id}")
        else:
            cmds.append(f"MOVE {u.id} {target.x} {target.y}")
    if len(mine) < 2:
        cmds.append("TRAIN 1 1 1 0")
    return cmds
