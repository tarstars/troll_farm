from bot.main import (State, Troll, Rates, project, INF, ITEM_INDEX,
                      estimate_rates, Tree)


def _state(inv, trolls, turn=1, iron=frozenset()):
    walkable = {(x, 0) for x in range(6)}
    return State(walkable=walkable, my_shack=(0, 0), opp_shack=(5, 5),
                 my_inventory=list(inv), opp_inventory=[0]*6,
                 trees=[Tree("PLUM", 3, 0, 1, 6, 0, 0)],
                 my_trolls=list(trolls), opp_trolls=[], turn=turn, iron_cells=iron)


def _g(id, stats):
    return Troll(id=id, x=0, y=0, movement_speed=stats[0], carry_capacity=stats[1],
                 harvest_power=stats[2], carry=[0]*6, chop_power=stats[3])


def test_empty_policy_just_banks_production():
    st = _state([0]*6, [_g(0, (1, 1, 1, 0))])
    r = estimate_rates(st)
    score = project(st, [], r)
    assert score > 0          # one gatherer accrues fruit over the horizon


def test_late_investment_not_worth_it():
    # With few turns left, adding a troll (cost paid, no payback) <= just banking.
    st = _state([20, 20, 20, 0, 20, 0], [_g(0, (1, 1, 1, 0))], turn=295)
    r = estimate_rates(st)
    bank = project(st, [], r)
    invest = project(st, [(2, 2, 2, 0)], r)
    assert bank >= invest


def test_more_gatherers_help_early():
    st = _state([20, 20, 20, 0, 20, 0], [_g(0, (1, 1, 1, 0))], turn=1)
    r = estimate_rates(st)
    bank = project(st, [], r)
    invest = project(st, [(1, 1, 1, 0)], r)
    assert invest >= bank      # early expansion pays back within the horizon
