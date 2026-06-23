"""Tests for parsing CodinGame input into walkable grid and per-turn State."""
from bot.main import parse_grid, parse_turn, Tree


def test_parse_grid_marks_grass_walkable_and_locates_shacks():
    # char at column x of row y is cell (x, y). '.' grass, '0' my shack, '1' opp.
    grid_lines = ["....", "0..1", "...."]
    walkable, my_shack, opp_shack = parse_grid(grid_lines)
    assert my_shack == (0, 1)
    assert opp_shack == (3, 1)
    assert (0, 1) not in walkable   # shack cells are not walkable
    assert (3, 1) not in walkable
    assert (0, 0) in walkable
    assert (1, 1) in walkable
    assert len(walkable) == 4 * 3 - 2


def test_parse_turn_builds_state_with_trees_and_my_troll():
    walkable = {(x, y) for x in range(4) for y in range(3)} - {(0, 1)}
    lines = [
        "0 0 0 0 0 0",            # my inventory
        "0 0 0 0 0 0",            # opponent inventory
        "1",                       # tree count
        "PLUM 2 0 4 4 2 5",        # type x y size health fruits cooldown
        "2",                       # troll count
        "0 0 1 1 1 1 1 0 0 0 0 0 0 0",   # my troll id0 at (1,1), carrying nothing
        "9 1 3 2 1 1 1 0 0 1 0 0 0 0",   # opponent troll (player 1), ignored
    ]
    state = parse_turn(iter(lines), walkable, my_shack=(0, 1))
    assert state.my_shack == (0, 1)
    assert state.trees == [Tree("PLUM", 2, 0, 4, 4, 2, 5)]
    assert state.my_troll.id == 0
    assert state.my_troll.pos == (1, 1)
    assert state.my_troll.carry_capacity == 1
    assert state.my_troll.carried == 0


def test_parse_turn_sums_carried_items():
    walkable = {(x, y) for x in range(4) for y in range(3)}
    lines = [
        "0 0 0 0 0 0",
        "0 0 0 0 0 0",
        "0",
        "1",
        "0 0 1 1 1 2 1 0 1 0 1 0 0 0",   # carries plum=1, apple=1 -> total 2
    ]
    state = parse_turn(iter(lines), walkable, my_shack=(0, 1))
    assert state.my_troll.carried == 2
