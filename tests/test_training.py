from bot.main import training_cost, training_command, State, Troll, Tree


def test_training_cost_matches_statement_example():
    # 2 existing trolls, TRAIN 2 3 1 0 -> 6 PLUM, 11 LEMON, 3 APPLE
    cost = training_cost(2, (2, 3, 1, 0))
    assert cost == [6, 11, 3, 0, 0, 0]


def test_training_cost_zero_stats():
    assert training_cost(0, (1, 0, 0, 0)) == [1, 0, 0, 0, 0, 0]


def _state(turn, my_trolls, inv):
    return State(walkable={(0, 1)}, my_shack=(0, 0), opp_shack=(15, 7),
                 my_inventory=inv, opp_inventory=[0]*6, trees=[],
                 my_trolls=my_trolls, opp_trolls=[], turn=turn)


def _params(**over):
    p = {"max_trolls": 3, "train_specs": [(1, 1, 1, 0)],
         "min_turns_left_to_train": 25, "score_reserve": 0}
    p.update(over)
    return p


def test_trains_first_affordable_spec_when_resources_allow():
    troll = Troll(0, 1, 1, 1, 1, 1, [0]*6)            # off the shack
    st = _state(1, [troll], [5, 5, 5, 5, 0, 0])
    assert training_command(st, _params()) == "TRAIN 1 1 1 0"


def test_no_train_when_cannot_afford():
    troll = Troll(0, 1, 1, 1, 1, 1, [0]*6)
    st = _state(1, [troll], [0, 0, 0, 0, 0, 0])
    assert training_command(st, _params()) is None


def test_no_train_when_shack_occupied():
    troll = Troll(0, 0, 0, 1, 1, 1, [0]*6)            # sitting on the shack
    st = _state(1, [troll], [5, 5, 5, 5, 0, 0])
    assert training_command(st, _params()) is None


def test_no_train_when_at_cap_or_near_end():
    troll = Troll(0, 1, 1, 1, 1, 1, [0]*6)
    at_cap = _state(1, [troll], [5, 5, 5, 5, 0, 0])
    assert training_command(at_cap, _params(max_trolls=1)) is None
    near_end = _state(290, [troll], [5, 5, 5, 5, 0, 0])
    assert training_command(near_end, _params()) is None


def test_score_reserve_blocks_overspending():
    troll = Troll(0, 1, 1, 1, 1, 1, [0]*6)
    # cost of (1,1,1) at n=1 is 2/2/2; inventory 2/2/2/3 totals 9, spend 6 -> 3 left
    st = _state(1, [troll], [2, 2, 2, 3, 0, 0])
    assert training_command(st, _params(score_reserve=5)) is None
    assert training_command(st, _params(score_reserve=3)) == "TRAIN 1 1 1 0"
