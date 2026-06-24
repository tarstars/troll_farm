from sim.state import GameState, SimPlant, SimUnit, from_ascii
from sim.engine import (tick_plants, recompute_scores, next_cell, apply_moves,
                        apply_harvest, apply_drop, apply_pick, apply_plant,
                        apply_train)


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


def test_harvest_takes_one_fruit_for_capacity_one_troll():
    g = from_ascii(["0....1"])
    g.units = [SimUnit(0, 0, 1, 0, 1, 1, 1, 0, [0]*6)]
    g.plants = [SimPlant("PLUM", 1, 0, 4, 4, 3, 5)]
    apply_harvest(g, [0])
    assert g.units[0].carry[0] == 1 and g.plants[0].fruits == 2


def test_last_fruit_duplicates_across_two_trolls():
    g = from_ascii(["0....1"])
    g.units = [SimUnit(0, 0, 1, 0, 1, 1, 1, 0, [0]*6),
               SimUnit(9, 1, 1, 0, 1, 1, 1, 0, [0]*6)]  # enemy on same cell
    g.plants = [SimPlant("PLUM", 1, 0, 4, 4, 1, 5)]      # only 1 fruit
    apply_harvest(g, [0, 9])
    assert g.units[0].carry[0] == 1 and g.units[1].carry[0] == 1   # both got one
    assert g.plants[0].fruits == 0


def test_drop_moves_carry_to_inventory_when_next_to_shack():
    g = from_ascii(["0....1"])
    g.units = [SimUnit(0, 0, 1, 0, 1, 9, 1, 0, [2, 0, 1, 0, 0, 0])]
    apply_drop(g, [0])
    assert g.inventories[0][0] == 2 and g.inventories[0][2] == 1
    assert g.units[0].total == 0


def test_train_costs_and_spawns_on_shack():
    g = from_ascii(["0....1"])
    g.units = [g.units[0]]                          # keep only player-0 unit
    g.next_id = 1
    g.units[0].x, g.units[0].y = 2, 0       # move existing unit off the shack
    g.inventories[0] = [5, 5, 5, 5, 0, 0]
    apply_train(g, 0, (1, 1, 1, 0))         # n=1 -> cost 2/2/2
    assert g.inventories[0][:3] == [3, 3, 3]
    spawned = [u for u in g.units if u.id == 1]
    assert spawned and spawned[0].pos == g.shacks[0]


def test_train_blocked_when_shack_occupied():
    g = from_ascii(["0....1"])                # unit 0 still on the shack
    g.inventories[0] = [5, 5, 5, 5, 0, 0]
    apply_train(g, 0, (1, 1, 1, 0))
    assert len(g.units) == 2                  # no new unit
