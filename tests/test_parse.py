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


def test_parse_turn_collects_all_trolls_and_inventories():
    walkable = {(x, y) for x in range(16) for y in range(8)} - {(5, 3), (10, 4)}
    lines = [
        "2 3 4 5 0 0",                      # my inventory
        "1 1 1 1 0 0",                      # opponent inventory
        "1",                                 # tree count
        "PLUM 6 1 4 4 2 5",
        "3",                                 # troll count
        "0 0 5 3 1 1 1 0 0 0 0 0 0 0",       # my troll, on my shack
        "2 0 6 1 2 4 3 0 1 0 1 0 0 0",       # my troll, carrying plum+apple=2
        "1 1 10 4 1 1 1 0 0 0 0 0 0 0",      # opponent troll
    ]
    state = parse_turn(iter(lines), walkable, my_shack=(5, 3),
                       opp_shack=(10, 4), turn=7)
    assert state.turn == 7
    assert state.my_inventory == [2, 3, 4, 5, 0, 0]
    assert state.opp_inventory == [1, 1, 1, 1, 0, 0]
    assert [t.id for t in state.my_trolls] == [0, 2]
    assert [t.id for t in state.opp_trolls] == [1]
    second = state.my_trolls[1]
    assert second.carry == [1, 0, 1, 0, 0, 0]
    assert second.total_carried == 2
    assert second.carry_capacity == 4
    assert state.trees == [Tree("PLUM", 6, 1, 4, 4, 2, 5)]
