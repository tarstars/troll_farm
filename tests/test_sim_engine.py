from sim.state import GameState, SimPlant, SimUnit, from_ascii
from sim.engine import tick_plants, recompute_scores


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
