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
