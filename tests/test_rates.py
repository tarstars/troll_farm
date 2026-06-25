from bot.main import (State, Tree, estimate_rates, INF, _has_iron, ITEM_INDEX,
                      gatherer_rate, chopper_wood_rate, chopper_iron_rate, Rates)


def _line_map():
    # walkable strip y=0, x=0..5; shack at (0,0)-adjacent gathering from (1,0)
    walkable = {(x, 0) for x in range(6)}
    return walkable


def test_fruit_supply_counts_reachable_trees_by_cooldown():
    walkable = _line_map()
    # PLUM tree (cooldown 8) at (3,0): reachable; APPLE (cooldown 9) at (5,0)
    trees = [Tree("PLUM", 3, 0, 1, 6, 0, 0), Tree("APPLE", 5, 0, 1, 6, 0, 0)]
    st = State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
               my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
               my_trolls=[], opp_trolls=[], turn=1)
    r = estimate_rates(st)
    assert abs(r.fruit_supply[ITEM_INDEX["PLUM"]] - 1/8) < 1e-9
    assert abs(r.fruit_supply[ITEM_INDEX["APPLE"]] - 1/9) < 1e-9
    assert r.fruit_supply[ITEM_INDEX["LEMON"]] == 0.0
    assert r.iron_dist == INF
    assert _has_iron(r) is False


def test_unreachable_tree_excluded_and_iron_distance():
    walkable = _line_map()
    trees = [Tree("PLUM", 3, 0, 1, 6, 0, 0), Tree("LEMON", 9, 9, 1, 6, 0, 0)]
    st = State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
               my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
               my_trolls=[], opp_trolls=[], turn=1,
               iron_cells=frozenset({(3, 1)}))   # approached from (3,0)
    r = estimate_rates(st)
    assert r.fruit_supply[ITEM_INDEX["LEMON"]] == 0.0   # (9,9) unreachable
    # doorstep (1,0) seeded at 0 -> (3,0) is 2 steps away
    assert r.iron_dist == 2
    assert _has_iron(r) is True


def test_gatherer_rate_increases_with_capacity_and_speed():
    r = Rates([0.5, 0, 0, 0], mean_dist=4.0, mean_tree_size=2.0,
              mean_tree_health=6.0, iron_dist=INF)
    slow = gatherer_rate(r, (1, 1, 1, 0))
    big = gatherer_rate(r, (1, 3, 1, 0))
    fast = gatherer_rate(r, (2, 1, 1, 0))
    assert big > slow and fast > slow
    # cc=1, ms=1, mean_dist=4 -> cycle = 2*4/1 + 1 = 9 -> 1/9
    assert abs(slow - 1/9) < 1e-9


def test_chopper_rates_zero_without_chop_or_iron():
    r = Rates([0, 0, 0, 0], 4.0, 2.0, 6.0, iron_dist=INF)
    assert chopper_wood_rate(r, (1, 2, 0, 0)) == 0.0       # chop 0
    assert chopper_iron_rate(r, (1, 2, 0, 3)) == 0.0       # no iron on map
    assert chopper_wood_rate(r, (1, 2, 0, 3)) > 0.0
    r2 = Rates([0, 0, 0, 0], 4.0, 2.0, 6.0, iron_dist=2.0)
    assert chopper_iron_rate(r2, (1, 2, 0, 3)) > 0.0
