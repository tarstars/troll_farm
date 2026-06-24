from sim.state import from_ascii, SimUnit


def test_from_ascii_sets_walkable_shacks_and_spawns_units():
    g = from_ascii(["....", "0..1"])
    assert g.width == 4 and g.height == 2
    assert g.shacks == [(0, 1), (3, 1)]
    assert (0, 1) not in g.walkable and (3, 1) not in g.walkable
    assert (0, 0) in g.walkable
    assert [(u.player, u.pos) for u in g.units] == [(0, (0, 1)), (1, (3, 1))]
    assert g.turn == 1 and g.next_id == 2
    assert g.inventories == [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]


def test_simunit_capacity_helpers():
    u = SimUnit(0, 0, 1, 1, 1, 4, 2, 0, [1, 0, 1, 0, 0, 0])
    assert u.pos == (1, 1) and u.total == 2 and u.free == 2
