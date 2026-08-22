from cgauto.h7_action_contention_census import (
    harvest_awards,
    move_target,
    ticked_plant,
    wood_awards,
)


def unit(unit_id, *, hp=1, cc=3, carried=0):
    return {
        "id": unit_id,
        "hp": hp,
        "cc": cc,
        "carry": [carried, 0, 0, 0, 0, 0],
    }


def test_last_fruit_duplicates_with_two_legal_harvesters():
    gains, remaining = harvest_awards(1, [(0, unit(0)), (1, unit(1))])
    assert gains == {0: 1, 1: 1}
    assert remaining == 0


def test_harvest_rounds_respect_power_and_capacity():
    gains, remaining = harvest_awards(
        3, [(0, unit(0, hp=3, cc=1)), (1, unit(1, hp=2, cc=3))]
    )
    assert gains == {0: 1, 1: 2}
    assert remaining == 0


def test_last_wood_duplicates():
    gains, remaining = wood_awards(1, [(0, unit(0)), (1, unit(1))])
    assert gains == {0: 1, 1: 1}
    assert remaining == -1


def test_wood_capacity_limits_award():
    full = unit(0, cc=1, carried=1)
    gains, remaining = wood_awards(2, [(0, full), (1, unit(1))])
    assert gains == {0: 0, 1: 2}
    assert remaining == 0


def test_mature_harvest_can_regenerate_on_same_tick():
    plant = {
        "type": "PLUM",
        "size": 4,
        "health": 12,
        "fruits": 0,
        "cooldown": 0,
    }
    assert ticked_plant(plant)["fruits"] == 1


def test_growth_tick_preserves_damage_and_adds_health_slope():
    plant = {
        "type": "APPLE",
        "size": 2,
        "health": 7,
        "fruits": 0,
        "cooldown": 1,
    }
    assert ticked_plant(plant, health=5) == {
        "size": 3,
        "health": 8,
        "fruits": 0,
    }


def test_move_target_parser_is_exact():
    assert move_target("MOVE 7 12 9") == (12, 9)
    assert move_target("WAIT") is None
