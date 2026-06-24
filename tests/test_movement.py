"""Tests for collision-aware movement helpers."""
from bot.main import bfs_within, landing_cell, orchard_targets, State, Tree, Troll


def _state(walkable, shack, trees):
    return State(walkable=walkable, my_shack=shack, opp_shack=(15, 7),
                 my_inventory=[0]*6, opp_inventory=[0]*6, trees=trees,
                 my_trolls=[], opp_trolls=[], turn=1)


def grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


def test_bfs_within_reaches_only_cells_in_range():
    w = grid(5, 5)
    d = bfs_within(w, (2, 2), 1)
    assert d[(2, 2)] == 0
    assert set(d) == {(2, 2), (2, 3), (3, 2), (2, 1), (1, 2)}
    d2 = bfs_within(w, (2, 2), 2)
    assert d2[(0, 2)] == 2 and (3, 3) in d2


def test_bfs_within_seeds_unwalkable_start():
    # a troll on its (unwalkable) shack must still expand to walkable neighbours
    w = grid(4, 1, blocked=[(0, 0)])
    d = bfs_within(w, (0, 0), 1)
    assert d[(0, 0)] == 0 and d[(1, 0)] == 1


def test_landing_cell_steps_toward_goal():
    w = grid(6, 1, blocked=[(0, 0)])
    goal_dist = {(5, 0): 0, (4, 0): 1, (3, 0): 2, (2, 0): 3, (1, 0): 4}
    # speed 1 from (2,0): best reachable toward goal is (3,0)
    assert landing_cell(w, (2, 0), goal_dist, 1, set()) == (3, 0)
    # speed 2 lands two steps closer
    assert landing_cell(w, (2, 0), goal_dist, 2, set()) == (4, 0)


def test_landing_cell_avoids_claimed_cell():
    w = grid(6, 1, blocked=[(0, 0)])
    goal_dist = {(5, 0): 0, (4, 0): 1, (3, 0): 2, (2, 0): 3, (1, 0): 4}
    # (3,0) is the natural step but it's claimed -> stay put (no better unclaimed cell at speed 1)
    assert landing_cell(w, (2, 0), goal_dist, 1, {(3, 0)}) == (2, 0)


def test_landing_cell_picks_alternative_when_forward_claimed():
    # two ways forward; the closer one is claimed, take the other
    w = grid(3, 3)
    goal_dist = {(2, 0): 0, (1, 0): 1, (2, 1): 1, (1, 1): 2, (0, 0): 2}
    # from (1,1) toward (2,0): neighbours (1,0) d1 and (2,1) d1; claim (1,0) -> pick (2,1)
    assert landing_cell(w, (1, 1), goal_dist, 1, {(1, 0)}) == (2, 1)


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
