from __future__ import annotations

from cgauto.secure_orchard_conversion_audit import (
    command_for_unit,
    event_detail,
    event_is_admissible,
    summarize,
)


def state(*, carried: int, banked: int) -> dict:
    return {
        "inventories": [[0, 0, banked, 0, 0, 0], [0] * 6],
        "units": [
            {
                "id": 7,
                "player": 0,
                "x": 2,
                "y": 3,
                "carry": [0, 0, carried, 0, 0, 0],
            }
        ],
        "plants": [
            {
                "type": "APPLE",
                "x": 2,
                "y": 3,
                "fruits": 2,
                "health": 20,
            }
        ],
    }


def test_events_are_admissible_only_before_first_command_mismatch() -> None:
    assert event_is_admissible(20, None)
    assert event_is_admissible(19, 20)
    assert not event_is_admissible(20, 20)
    assert not event_is_admissible(21, 20)


def test_command_for_unit_ignores_messages_and_checks_unit_id() -> None:
    line = "MSG hi;DROP 7;CHOP 9"
    assert command_for_unit(line, 7, "DROP")
    assert not command_for_unit(line, 9, "DROP")


def test_event_detail_confirms_harvest_and_next_turn_bank() -> None:
    stream = {
        "seat": 0,
        "turns": 2,
        "recorded": ["HARVEST 7", "DROP 7"],
        "states": [
            state(carried=0, banked=0),
            state(carried=1, banked=0),
            state(carried=0, banked=1),
        ],
    }
    detail = event_detail(
        {"kind": "orchard_force", "turn": 1, "unit": 7, "commands": "HARVEST 7"},
        stream,
    )
    assert detail["mother_is_ripe_apple"]
    assert detail["successful_apple_amount"] == 1
    assert detail["banked_next_turn"]


def test_summary_retains_complete_activation_distribution() -> None:
    base = {
        "margin": 10,
        "admissible_forced_harvests": 0,
        "post_seed_replacement_forces": 0,
        "final": {
            "apple": 0,
            "wood": 10,
            "successful_plants": 2,
            "opponent_crops": 3,
            "opponent_crop_wood": 4,
        },
    }
    active = {
        **base,
        "margin": -100,
        "admissible_forced_harvests": 3,
        "post_seed_replacement_forces": 2,
        "final": {**base["final"], "apple": 3},
    }
    report = summarize([base, active])
    assert report["activated_games"] == 1
    assert report["sustained_after_seed_replacement_games"] == 1
    assert report["forced_harvest_count_distribution"] == [3]
    assert report["activated_mean_margin"] == -100
