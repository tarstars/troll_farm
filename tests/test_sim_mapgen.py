from sim.mapgen import generate
from bot.main import bfs_distances


def test_generate_is_deterministic_and_symmetric():
    a = generate(42)
    b = generate(42)
    assert [u.pos for u in a.units] == [u.pos for u in b.units]
    assert [p.pos for p in a.plants] == [p.pos for p in b.plants]
    assert a.width == 16 and a.height == 8
    s0, s1 = a.shacks
    assert s1 == (a.width - 1 - s0[0], a.height - 1 - s0[1])
    assert s0[0] < a.width // 2


def test_generate_has_starting_inventory_and_fruit():
    g = generate(7)
    assert all(2 <= g.inventories[0][i] <= 10 for i in range(4))
    assert any(p.fruits > 0 for p in g.plants)
    # all walkable cells reachable from a shack neighbour
    nbrs = [(g.shacks[0][0]+dx, g.shacks[0][1]+dy)
            for dx, dy in ((0,1),(1,0),(0,-1),(-1,0))]
    dist = bfs_distances(g.walkable, [n for n in nbrs if n in g.walkable])
    assert all(c in dist for c in g.walkable)
