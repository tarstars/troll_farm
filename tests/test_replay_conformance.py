"""Pure tests for replay/simulator transition classification."""

import copy

from cgauto.replay_conformance import (
    action_commands,
    classify_transition,
    effective_chop_unit_ids,
)
from cgauto.idle_harvest_study import fixed_fixture


def test_identical_transition_is_exact() -> None:
    game = fixed_fixture()

    assert classify_transition(game, copy.deepcopy(game)) == ("exact", [])


def test_position_only_difference_is_rng_only() -> None:
    predicted = fixed_fixture()
    official = copy.deepcopy(predicted)
    official.units[0].x += 1

    assert classify_transition(predicted, official) == (
        "movement_rng_only",
        ["unit_position"],
    )


def test_inventory_difference_is_material() -> None:
    predicted = fixed_fixture()
    official = copy.deepcopy(predicted)
    official.inventories[0][0] += 1
    official.scores[0] += 1

    classification, differences = classify_transition(predicted, official)

    assert classification == "material_mismatch"
    assert differences == ["inventories", "scores"]


def test_numeric_plant_kind_is_normalized() -> None:
    assert action_commands("PICK 0 1;PLANT 0 3") == [
        "PICK 0 LEMON",
        "PLANT 0 BANANA",
    ]


def test_only_first_command_per_unit_can_be_an_effective_chop() -> None:
    commands = ["MOVE 0 3 4", "CHOP 0", "CHOP 2", "MOVE 2 1 1"]

    assert effective_chop_unit_ids(commands) == [2]
