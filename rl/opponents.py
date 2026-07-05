"""Fixed scripted opponents for the RL env (player 1).

Each opponent is a callable ``fn(game, player) -> list[str]`` returning engine
command strings. The default is ``boss`` — the trivial greedy fruit-harvester
from ``sim/boss.py`` (never chops wood, so an agent that learns to bank wood at
4 pts/unit can clearly out-score it). Stronger opponents are provided for tougher
benchmarks:

    boss      sim.boss.boss_decide          trivial greedy harvester (weak)
    chopper   local greedy chopper          harvests + fells wood + trains a cc2 chopper
    heuristic bot.main.decide               the full hand-written economy bot (hard)
    idle      always WAIT                    sanity floor
"""

import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from sim.boss import boss_decide
from bot.main import training_cost


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def idle_decide(game, player):
    return ["WAIT"]


def greedy_chopper_decide(game, player):
    """A simple but complete opponent: harvest fruit when handy, otherwise fell
    the nearest tree for wood, bank when full, and train one cc2 chopper early.
    Middle difficulty — actually banks wood, unlike the trivial boss."""
    shack = game.shacks[player]
    mine = sorted((u for u in game.units if u.player == player), key=lambda u: u.id)
    inv = game.inventories[player]
    n = len(mine)
    cmds = ["MSG chop chop"]
    reserved = set()
    for u in mine:
        if u.total >= u.cc:                                  # full -> bank
            cmds.append(f"DROP {u.id}" if _dist(u.pos, shack) == 1
                        else f"MOVE {u.id} {shack[0]} {shack[1]}")
            continue
        here = next((p for p in game.plants if p.pos == u.pos), None)
        if here is not None and here.fruits > 0 and u.hp >= 1:  # harvest underfoot
            cmds.append(f"HARVEST {u.id}")
            continue
        if here is not None and u.chop > 0:                    # chop underfoot
            cmds.append(f"CHOP {u.id}")
            continue
        targets = [p for p in game.plants if p.pos not in reserved]
        if targets:
            t = min(targets, key=lambda p: _dist(u.pos, p.pos))
            reserved.add(t.pos)
            cmds.append(f"MOVE {u.id} {t.x} {t.y}")
        elif u.total > 0:
            cmds.append(f"DROP {u.id}" if _dist(u.pos, shack) == 1
                        else f"MOVE {u.id} {shack[0]} {shack[1]}")
    if n < 2 and not any(u.pos == shack for u in mine):
        spec = (2, 2, 0, 2)
        cost = training_cost(n, spec)
        pay = (0, 1, 2, 3, 4, 5) if game.iron else (0, 1, 2, 3, 5)
        if all(inv[i] >= cost[i] for i in pay):
            cmds.append(f"TRAIN {spec[0]} {spec[1]} {spec[2]} {spec[3]}")
    return cmds


def heuristic_decide(game, player):
    # Lazy import: bot.main.decide operates on a per-player View.
    from sim.views import build_view
    from bot.main import decide, PARAMS
    return decide(build_view(game, player), PARAMS)


_REGISTRY = {
    "boss": boss_decide,
    "chopper": greedy_chopper_decide,
    "heuristic": heuristic_decide,
    "idle": idle_decide,
}


def get_opponent(name):
    if callable(name):
        return name
    if name not in _REGISTRY:
        raise KeyError(f"unknown opponent {name!r}; choices: {sorted(_REGISTRY)}")
    return _REGISTRY[name]


def opponent_names():
    return sorted(_REGISTRY)
