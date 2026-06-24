def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


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
