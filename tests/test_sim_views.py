# tests/test_sim_views.py
from sim.state import from_ascii, SimUnit, SimPlant
from sim.views import build_view


def test_build_view_maps_state_for_player_zero():
    g = from_ascii(["....", "0..1"])
    g.units = [SimUnit(0, 0, 1, 1, 2, 3, 1, 0, [1, 0, 0, 0, 0, 0]),
               SimUnit(7, 1, 2, 1, 1, 1, 1, 0, [0]*6)]
    g.plants = [SimPlant("PLUM", 0, 0, 4, 4, 2, 5)]
    g.inventories = [[4, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0]]
    g.turn = 6
    v = build_view(g, 0)
    assert v.my_shack == (0, 1) and v.opp_shack == (3, 1)
    assert v.my_inventory == [4, 0, 0, 0, 0, 0]
    assert [t.id for t in v.my_trolls] == [0] and [t.id for t in v.opp_trolls] == [7]
    assert v.my_trolls[0].carry_capacity == 3 and v.my_trolls[0].carry == [1, 0, 0, 0, 0, 0]
    assert v.trees[0].pos == (0, 0) and v.turn == 6


def test_build_view_for_player_one_swaps_sides():
    g = from_ascii(["....", "0..1"])
    g.inventories = [[4, 0, 0, 0, 0, 0], [1, 1, 1, 1, 0, 0]]
    v = build_view(g, 1)
    assert v.my_shack == (3, 1) and v.opp_shack == (0, 1)
    assert v.my_inventory == [1, 1, 1, 1, 0, 0]
