from bot.main import training_cost


def test_training_cost_matches_statement_example():
    # 2 existing trolls, TRAIN 2 3 1 0 -> 6 PLUM, 11 LEMON, 3 APPLE
    cost = training_cost(2, (2, 3, 1, 0))
    assert cost == [6, 11, 3, 0, 0, 0]


def test_training_cost_zero_stats():
    assert training_cost(0, (1, 0, 0, 0)) == [1, 0, 0, 0, 0, 0]
