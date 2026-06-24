from bot.main import State, Troll, Tree


def _troll(u):
    return Troll(id=u.id, x=u.x, y=u.y, movement_speed=u.ms,
                 carry_capacity=u.cc, harvest_power=u.hp, carry=list(u.carry),
                 chop_power=u.chop)


def build_view(game, player):
    opp = 1 - player
    trees = [Tree(p.type, p.x, p.y, p.size, p.health, p.fruits, p.cooldown)
             for p in game.plants]
    my = [_troll(u) for u in game.units if u.player == player]
    their = [_troll(u) for u in game.units if u.player == opp]
    return State(walkable=set(game.walkable), my_shack=game.shacks[player],
                 opp_shack=game.shacks[opp], my_inventory=list(game.inventories[player]),
                 opp_inventory=list(game.inventories[opp]), trees=trees,
                 my_trolls=my, opp_trolls=their, turn=game.turn,
                 iron_cells=frozenset(game.iron), water_cells=frozenset(game.water))
