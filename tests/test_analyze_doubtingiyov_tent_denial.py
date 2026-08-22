from cgauto.analyze_doubtingiyov_tent_denial import (
    target_cell,
    training_cost,
    trigger_band,
)


def test_trigger_band_boundaries():
    assert trigger_band(0) == "zero"
    assert trigger_band(1) == "one_or_two"
    assert trigger_band(2) == "one_or_two"
    assert trigger_band(3) == "more_than_two"


def test_target_cell_resolves_move_and_local_actions():
    unit = {"x": 7, "y": 6}

    assert target_cell("MOVE 3 8 7", unit) == (8, 7)
    assert target_cell("CHOP 3", unit) == (7, 6)
    assert target_cell("HARVEST 3", unit) == (7, 6)
    assert target_cell("WAIT", unit) is None


def test_training_cost_uses_current_worker_count():
    assert training_cost(2, (1, 2, 3, 1)) == [3, 6, 11, 0, 3, 0]
