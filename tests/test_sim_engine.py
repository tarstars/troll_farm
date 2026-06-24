from sim.state import GameState, SimPlant, SimUnit, from_ascii
from sim.engine import tick_plants, recompute_scores, next_cell


def test_tick_plants_grows_then_produces():
    g = from_ascii(["....", "0..1"])
    g.plants = [SimPlant("PLUM", 1, 0, 4, 4, 2, 1)]   # full size, cd 1
    tick_plants(g)                                    # cd->0 -> +1 fruit
    p = g.plants[0]
    assert p.fruits == 3 and p.cooldown == 8


def test_tick_plants_growing_tree_increases_size_no_fruit():
    g = from_ascii(["....", "0..1"])
    g.plants = [SimPlant("BANANA", 2, 0, 2, 6, 0, 1)]
    tick_plants(g)
    assert g.plants[0].size == 3 and g.plants[0].fruits == 0


def test_recompute_scores_counts_only_fruit():
    g = from_ascii(["....", "0..1"])
    g.inventories[0] = [3, 2, 1, 4, 9, 0]   # iron/wood don't score
    recompute_scores(g)
    assert g.scores[0] == 10


def line(n, blocked=()):
    return {(x, 0) for x in range(n)} - set(blocked)


def test_next_cell_direct_when_in_range():
    w = line(6, blocked=[(0, 0)])
    assert next_cell(w, (3, 0), (5, 0), 2) == (5, 0)   # 2 away, speed 2


def test_next_cell_steps_toward_far_target():
    w = line(6, blocked=[(0, 0)])
    assert next_cell(w, (1, 0), (5, 0), 1) == (2, 0)   # one step closer


def test_next_cell_routes_to_nearest_reachable_when_unreachable():
    # target (0,0) is the shack (unwalkable); a banking troll parks adjacent
    w = line(6, blocked=[(0, 0)])
    assert next_cell(w, (3, 0), (0, 0), 1) == (2, 0)
