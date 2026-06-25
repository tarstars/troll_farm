from bot.main import (State, Troll, Tree, search_policy, candidate_policies,
                      ITEM_INDEX)


def _state(inv, turn=1, trees=None, iron=frozenset(), walkable=None):
    walkable = walkable or {(x, 0) for x in range(6)}
    troll = Troll(id=0, x=0, y=0, movement_speed=1, carry_capacity=1,
                  harvest_power=1, carry=[0]*6, chop_power=1)
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
                 my_inventory=list(inv), opp_inventory=[0]*6,
                 trees=trees if trees is not None else [Tree("LEMON", 3, 0, 1, 6, 0, 0)],
                 my_trolls=[troll], opp_trolls=[], turn=turn, iron_cells=iron)


def test_no_plum_supply_means_no_movement_training():
    # Only LEMON trees reachable -> PLUM supply 0 -> any movement-stat (ms>1)
    # spec is unfundable; the chosen plan's training must not demand PLUM we
    # cannot supply. We assert: no scheduled spec needs ms>1.
    st = _state([5, 5, 5, 0, 5, 0], trees=[Tree("LEMON", 3, 0, 1, 6, 0, 0)])
    plan = search_policy(st)
    if plan.train is not None:
        assert plan.train[0] == 1      # movement speed stays 1 (no PLUM needed beyond n)


def test_late_game_stops_investing():
    st = _state([20, 20, 20, 0, 20, 0], turn=296)
    plan = search_policy(st)
    assert plan.train is None


def test_forced_policy_is_obeyed():
    st = _state([20, 20, 20, 0, 20, 0])
    plan = search_policy(st, {"forced_policy": [(2, 2, 2, 0)]})
    assert plan.train == (2, 2, 2, 0)


def test_candidates_include_empty_and_chopper():
    cands = candidate_policies()
    assert [] in cands
    assert any(spec[3] >= 2 for pol in cands for spec in pol)
