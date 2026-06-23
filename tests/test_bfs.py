"""Tests for BFS distance field over walkable cells (mirrors Board.getDistances)."""
from bot.main import bfs_distances


def _grid_3x3(blocked=()):
    return {(x, y) for x in range(3) for y in range(3)} - set(blocked)


def test_distances_from_single_source():
    walkable = _grid_3x3()
    dist = bfs_distances(walkable, [(0, 0)])
    assert dist[(0, 0)] == 0
    assert dist[(0, 2)] == 2
    assert dist[(1, 1)] == 2
    assert dist[(2, 2)] == 4


def test_blocked_cell_is_unreachable_and_routes_around():
    # block (1, 0); (2, 0) must be reached the long way round
    walkable = _grid_3x3(blocked=[(1, 0)])
    dist = bfs_distances(walkable, [(0, 0)])
    assert (1, 0) not in dist
    assert dist[(2, 0)] == 4  # (0,0)->(0,1)->(1,1)->(2,1)->(2,0)


def test_multi_source_takes_minimum_distance():
    walkable = _grid_3x3()
    dist = bfs_distances(walkable, [(0, 0), (2, 2)])
    assert dist[(2, 2)] == 0
    assert dist[(1, 1)] == 2  # equidistant from both sources
    assert dist[(2, 1)] == 1  # adjacent to (2,2)
