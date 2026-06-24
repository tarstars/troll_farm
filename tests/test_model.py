from bot.main import Troll, Tree, State, ITEM_INDEX, TOTAL_TURNS


def test_troll_carry_totals_and_free_capacity():
    t = Troll(id=3, x=2, y=5, movement_speed=2, carry_capacity=4,
              harvest_power=3, carry=[1, 0, 2, 0, 0, 0])
    assert t.pos == (2, 5)
    assert t.total_carried == 3
    assert t.free_capacity == 1


def test_item_index_and_turn_constant():
    assert ITEM_INDEX["BANANA"] == 3
    assert TOTAL_TURNS == 300


def test_state_holds_both_sides():
    s = State(walkable={(0, 0)}, my_shack=(0, 0), opp_shack=(15, 7),
              my_inventory=[2, 2, 2, 2, 0, 0], opp_inventory=[3, 3, 3, 3, 0, 0],
              trees=[], my_trolls=[], opp_trolls=[], turn=1)
    assert s.opp_shack == (15, 7)
    assert s.my_inventory[0] == 2
