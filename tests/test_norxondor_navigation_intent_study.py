from __future__ import annotations

from cgauto.norxondor_navigation_intent_study import (
    action_family,
    attach_next_actions,
    move_target,
)


def test_attach_next_actions_labels_move_episode_by_eventual_action() -> None:
    timeline = [
        {"turn": 1, "verb": "MOVE", "cell": (1, 1)},
        {"turn": 2, "verb": "MOVE", "cell": (2, 1)},
        {"turn": 3, "verb": "CHOP", "cell": (3, 1)},
        {"turn": 4, "verb": "MOVE", "cell": (3, 1)},
        {"turn": 5, "verb": "PLANT", "cell": (4, 1)},
    ]

    attach_next_actions(timeline)

    assert timeline[0]["intent"] == "GO_CHOP"
    assert timeline[0]["action_verb"] == "CHOP"
    assert timeline[0]["goal_cell"] == (3, 1)
    assert timeline[1]["action_turn"] == 3
    assert timeline[3]["intent"] == "GO_FARM"
    assert timeline[3]["goal_cell"] == (4, 1)


def test_wait_breaks_future_action_supervision() -> None:
    timeline = [
        {"turn": 1, "verb": "MOVE", "cell": (1, 1)},
        {"turn": 2, "verb": "WAIT", "cell": (2, 1)},
        {"turn": 3, "verb": "DROP", "cell": (2, 1)},
    ]

    attach_next_actions(timeline)

    assert timeline[0]["intent"] == "GO_END"
    assert timeline[0]["action_verb"] is None
    assert timeline[0]["goal_cell"] is None


def test_move_parser_and_farm_family() -> None:
    assert move_target("MOVE 7 3 4") == (3, 4)
    assert move_target("DROP 7") is None
    assert action_family("PICK") == "FARM"
    assert action_family("PLANT") == "FARM"
    assert action_family("CHOP") == "CHOP"
