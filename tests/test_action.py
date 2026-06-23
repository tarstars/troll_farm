"""Tests for the per-turn decision: choose_action(state) -> command string."""
from bot.main import choose_action, State, Troll, Tree


def full_grid(w, h, blocked=()):
    return {(x, y) for x in range(w) for y in range(h)} - set(blocked)


def test_drops_when_carrying_and_adjacent_to_shack():
    # shack at (0,0) unwalkable; troll at (0,1) carrying 1, capacity 1 -> DROP
    walkable = full_grid(4, 4, blocked=[(0, 0)])
    troll = Troll(id=0, x=0, y=1, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carried=1)
    state = State(walkable=walkable, my_shack=(0, 0), trees=[], my_troll=troll)
    assert choose_action(state) == "DROP 0"


def test_moves_toward_shack_when_carrying_and_far():
    walkable = full_grid(4, 4, blocked=[(0, 0)])
    troll = Troll(id=0, x=3, y=3, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carried=1)
    state = State(walkable=walkable, my_shack=(0, 0), trees=[], my_troll=troll)
    assert choose_action(state) == "MOVE 0 0 0"


def test_harvests_when_standing_on_a_fruited_tree():
    walkable = full_grid(4, 4, blocked=[(0, 0)])
    tree = Tree(type="PLUM", x=2, y=2, size=4, health=4, fruits=2, cooldown=5)
    troll = Troll(id=0, x=2, y=2, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carried=0)
    state = State(walkable=walkable, my_shack=(0, 0), trees=[tree], my_troll=troll)
    assert choose_action(state) == "HARVEST 0"


def test_prefers_tree_with_smaller_round_trip():
    # Both trees equidistant to walk to (1 step) and both ripe, but tree A is
    # much closer to the shack for the return leg -> pick A.
    walkable = full_grid(8, 2, blocked=[(0, 0)])
    troll = Troll(id=0, x=4, y=0, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carried=0)
    near = Tree(type="PLUM", x=3, y=0, size=4, health=4, fruits=1, cooldown=5)
    far = Tree(type="PLUM", x=5, y=0, size=4, health=4, fruits=1, cooldown=5)
    state = State(walkable=walkable, my_shack=(0, 0), trees=[near, far],
                  my_troll=troll)
    assert choose_action(state) == "MOVE 0 3 0"


def test_prefers_ripe_tree_over_one_that_ripens_far_in_future():
    # Symmetric layout (mirror about x=2): equal walk and equal return, so
    # ripeness is the only differentiator. A is ripe, B won't fruit for ages.
    walkable = full_grid(5, 3, blocked=[(2, 0)])
    troll = Troll(id=0, x=2, y=2, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carried=0)
    ripe = Tree(type="PLUM", x=1, y=1, size=4, health=4, fruits=1, cooldown=5)
    unripe = Tree(type="APPLE", x=3, y=1, size=4, health=20, fruits=0, cooldown=9)
    state = State(walkable=walkable, my_shack=(2, 0), trees=[ripe, unripe],
                  my_troll=troll)
    assert choose_action(state) == "MOVE 0 1 1"


def test_moves_toward_soonest_ripening_tree_when_none_ripe_now():
    # Don't idle: no fruit anywhere yet, head to the tree that ripens soonest.
    walkable = full_grid(8, 2, blocked=[(0, 0)])
    troll = Troll(id=0, x=4, y=0, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carried=0)
    soon = Tree(type="BANANA", x=3, y=0, size=4, health=6, fruits=0, cooldown=2)
    late = Tree(type="APPLE", x=5, y=0, size=4, health=20, fruits=0, cooldown=9)
    state = State(walkable=walkable, my_shack=(0, 0), trees=[soon, late],
                  my_troll=troll)
    assert choose_action(state) == "MOVE 0 3 0"


def test_camps_when_standing_on_chosen_unripe_tree():
    # Standing on the best target but it has no fruit yet -> WAIT (not MOVE to self).
    walkable = full_grid(6, 2, blocked=[(0, 0)])
    troll = Troll(id=0, x=2, y=0, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carried=0)
    here = Tree(type="BANANA", x=2, y=0, size=4, health=6, fruits=0, cooldown=2)
    state = State(walkable=walkable, my_shack=(0, 0), trees=[here], my_troll=troll)
    assert choose_action(state) == "WAIT"


def test_waits_when_no_trees_reachable():
    walkable = full_grid(4, 4, blocked=[(0, 0)])
    troll = Troll(id=0, x=2, y=2, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carried=0)
    state = State(walkable=walkable, my_shack=(0, 0), trees=[], my_troll=troll)
    assert choose_action(state) == "WAIT"
