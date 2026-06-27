"""Surgical movement deconfliction (v0.7.4): trolls that would step into the same
cell get distinct next-cells, while non-colliding movers are untouched. The naive
whole-fleet 1-step rewrite halved the score; this only touches the ~4% that jam."""
from bot.main import deconflict_collisions, State, Troll


def _state(trolls):
    walkable = {(x, y) for x in range(5) for y in range(3)}
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(4, 2),
                 my_inventory=[0]*6, opp_inventory=[0]*6, trees=[],
                 my_trolls=list(trolls), opp_trolls=[], turn=5)


def test_two_trolls_into_same_cell_get_distinct_next_cells():
    a = Troll(0, 1, 1, 1, 1, 1, [0]*6)   # at (1,1)
    b = Troll(1, 3, 1, 1, 1, 1, [0]*6)   # at (3,1)
    out = deconflict_collisions(_state([a, b]), {0: (2, 1), 1: (2, 1)})
    assert out[0] != out[1]              # no longer both heading to (2,1)
    assert (2, 1) in out.values()        # one of them still advances


def test_no_override_when_no_collision():
    a = Troll(0, 1, 1, 1, 1, 1, [0]*6)
    b = Troll(1, 3, 1, 1, 1, 1, [0]*6)
    # heading to clearly distinct cells -> nothing to deconflict
    assert deconflict_collisions(_state([a, b]), {0: (0, 1), 1: (4, 1)}) == {}


def test_mover_blocked_by_stationary_teammate_is_rerouted():
    mover = Troll(0, 1, 1, 1, 1, 1, [0]*6)         # at (1,1), wants to pass (2,1)
    parked = Troll(1, 2, 1, 1, 1, 1, [0]*6)        # stationary at (2,1)
    out = deconflict_collisions(_state([mover, parked]), {0: (3, 1)})  # only mover moves
    assert out and out[0] != (2, 1)                # not stepping onto the teammate
