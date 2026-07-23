from cgauto.analyze_d85a_field_defensive_salvage import (
    choose_harvester,
    choose_joint_chopper,
    replace_unit_command,
)


def unit(unit_id: int, *, hp: int, chop: int, cc: int, carry: list[int]) -> dict:
    return {
        "id": unit_id,
        "player": 0,
        "x": 3,
        "y": 4,
        "ms": 1,
        "cc": cc,
        "hp": hp,
        "chop": chop,
        "carry": carry,
    }


def test_command_replacement_preserves_train_and_other_slots() -> None:
    units = [
        unit(3, hp=1, chop=1, cc=2, carry=[0] * 6),
        unit(8, hp=1, chop=1, cc=2, carry=[0] * 6),
    ]
    commands = ["TRAIN 2 2 0 2", "MOVE 3 9 9", "WAIT"]
    assert replace_unit_command(commands, units, 8, "HARVEST 8") == [
        "TRAIN 2 2 0 2",
        "MOVE 3 9 9",
        "HARVEST 8",
    ]


def test_harvester_prefers_immediate_capacity_then_small_id() -> None:
    plant = {"fruits": 3}
    units = [
        unit(9, hp=2, chop=0, cc=2, carry=[1, 0, 0, 0, 0, 0]),
        unit(4, hp=2, chop=0, cc=2, carry=[0] * 6),
        unit(2, hp=2, chop=0, cc=2, carry=[0] * 6),
    ]
    assert choose_harvester(units, plant)["id"] == 2


def test_joint_chop_requires_visible_lethality_and_no_harvest() -> None:
    units = [
        unit(7, hp=0, chop=2, cc=2, carry=[0] * 6),
        unit(3, hp=0, chop=3, cc=2, carry=[0] * 6),
    ]
    assert choose_joint_chopper(units, {"health": 4}, 3, False) is None
    assert choose_joint_chopper(units, {"health": 3}, 3, True) is None
    assert choose_joint_chopper(units, {"health": 3}, 3, False)["id"] == 3
