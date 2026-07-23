from cgauto.analyze_d32_deterministic_field_option_ab import (
    first_difference_turn,
    normalized_action_stream,
    value_summary,
)


def test_normalized_action_stream_ignores_messages_and_normalizes_items() -> None:
    assert normalized_action_stream(
        ["MSG one;PICK 7 3\n", "PLANT 7 0;MOVE 8 2 3\n"]
    ) == [["PICK 7 BANANA"], ["PLANT 7 PLUM", "MOVE 8 2 3"]]


def test_first_difference_turn_is_one_indexed_and_handles_length() -> None:
    left = [["WAIT"], ["MOVE 0 1 1"], ["WAIT"]]
    assert first_difference_turn(left, left) is None
    assert first_difference_turn(left, [["WAIT"], ["MOVE 0 2 1"], ["WAIT"]]) == 2
    assert first_difference_turn(left, left[:2]) == 3


def test_value_summary_implements_frozen_conjunction() -> None:
    passing = [
        {"delta": {"margin": 30, "own_score": 20}},
        {"delta": {"margin": 10, "own_score": 0}},
        {"delta": {"margin": -10, "own_score": -5}},
    ]
    failing = [
        {"delta": {"margin": 30, "own_score": 20}},
        {"delta": {"margin": -21, "own_score": 0}},
        {"delta": {"margin": 20, "own_score": -40}},
    ]

    assert value_summary(passing)["pass"] is True
    result = value_summary(failing)
    assert result["pass"] is False
    assert result["gates"]["no_margin_delta_below_minus_20"] is False
