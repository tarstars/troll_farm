from sim.state import GameState, SimPlant, SimUnit, from_ascii
from sim.engine import tick_plants, recompute_scores, next_cell, apply_moves


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


def two_unit_state():
    # 6x1 corridor, shack at (0,0); two of player 0's units
    # Note: brief had "0....." — from_ascii needs both shacks; "0....1" used instead
    g = from_ascii(["0....1"])
    g.units = [SimUnit(0, 0, 2, 0, 1, 1, 1, 0, [0]*6),
               SimUnit(1, 0, 3, 0, 1, 1, 1, 0, [0]*6)]
    g.next_id = 2
    return g


def test_two_movers_take_distinct_cells():
    g = two_unit_state()
    apply_moves(g, {0: (5, 0), 1: (5, 0)})   # both want to go right
    cells = sorted(u.pos for u in g.units)
    assert cells == [(3, 0), (4, 0)] or len(set(cells)) == 2  # no overlap


def test_unit_blocked_by_stationary_teammate_stays_put():
    # unit 0 sits still on (2,0); unit 1 at (1,0) wants (2,0) -> blocked, stays
    g = two_unit_state()
    g.units[0].x, g.units[0].y = 2, 0
    g.units[1].x, g.units[1].y = 1, 0
    apply_moves(g, {1: (2, 0)})              # unit 0 issued no move
    assert g.units[0].pos == (2, 0)
    assert g.units[1].pos == (1, 0)          # could not enter occupied cell


def test_higher_id_wins_contested_cell():
    g = two_unit_state()
    g.units[0].x, g.units[0].y = 1, 0
    g.units[1].x, g.units[1].y = 3, 0
    apply_moves(g, {0: (2, 0), 1: (2, 0)})   # both want (2,0); id 1 wins
    assert g.units[1].pos == (2, 0)
    assert g.units[0].pos == (1, 0)
