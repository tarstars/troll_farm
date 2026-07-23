from __future__ import annotations

from cgauto.arena_opponent_opening_calibration import calibrate, commands, compare


def test_commands_ignore_messages_order_and_empty_suffix() -> None:
    assert commands(
        "MSG hello;TRAIN 1 2 0 2;MOVE 7 3 4;MOVE 7 9 9;\nMOVE 7 8 8\n"
    ) == commands(
        "MOVE 7 3 4;TRAIN 1 2 0 2"
    )


def test_compare_separates_opening_signature_from_exact_target() -> None:
    observed = {
        "command": "TRAIN 1 2 0 2;MOVE 1 3 4",
        "starter_id": 1,
    }
    result = compare(observed, "MOVE 1 9 9;TRAIN 1 2 0 2")

    assert result["opening_signature_exact"] is True
    assert result["starter_verb_exact"] is True
    assert result["starter_command_exact"] is False
    assert result["commands_exact"] is False


def test_calibration_ranks_better_signature_and_reports_repeatability() -> None:
    observed = {
        10: {
            "command": "TRAIN 1 2 0 2;MOVE 7 3 4",
            "starter_id": 7,
            "opponent": "x",
            "opponent_agent": 99,
        }
    }
    good = {(10, 1, "good"): "TRAIN 1 2 0 2;MOVE 7 8 8", (10, 1, "bad"): "WAIT"}
    changed = {(10, 1, "good"): "TRAIN 1 2 0 2;MOVE 7 3 4", (10, 1, "bad"): "WAIT"}

    result = calibrate(observed, [good, changed])

    assert result["agreement_ranking"][0] == "good"
    assert result["model_summary"]["good"]["opening_signature_exact"]["rate"] == 1
    assert result["model_opening_repeatability"]["good"]["exact_games"] == 0
    assert result["model_opening_repeatability"]["bad"]["exact_games"] == 1
