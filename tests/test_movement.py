"""Tests for orchard target selection."""
from bot.main import orchard_targets, State, Tree


def _state(walkable, shack, trees):
    return State(walkable=walkable, my_shack=shack, opp_shack=(15, 7),
                 my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
                 my_trolls=[], opp_trolls=[], turn=1)


def grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


def test_orchard_targets_picks_nearest_empty_cells_excluding_trees():
    w = grid(4, 4, blocked=[(0, 0)])          # shack at (0,0), unwalkable
    trees = [Tree("PLUM", 1, 0, 4, 4, 2, 5)]  # tree occupies (1,0)
    targets = orchard_targets(_state(w, (0, 0), trees), {"max_orchard": 2})
    assert (1, 0) not in targets              # occupied cells are skipped
    assert len(targets) == 2
    assert targets[0] == (0, 1)               # the closest empty cell to the shack


def test_orchard_targets_respects_max_orchard():
    w = grid(4, 4, blocked=[(0, 0)])
    targets = orchard_targets(_state(w, (0, 0), []), {"max_orchard": 3})
    assert len(targets) == 3
