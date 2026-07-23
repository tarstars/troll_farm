from cgauto.critical_state_coverage import position_metrics, troll_action_count


def fixture_and_frame():
    fixture = {
        "game_id": 1,
        "n_turns": 10,
        "map": {"rows": ["0...1"]},
    }
    frame = {
        "resolved_turn": 8,
        "state": {
            "inventories": [[0] * 6, [0] * 6],
            "plants": [
                {"type": "BANANA", "x": 2, "y": 0, "size": 2, "health": 4, "fruits": 0}
            ],
            "units": [
                {"id": 0, "player": 0, "x": 2, "y": 0, "ms": 1, "cc": 2, "hp": 1, "chop": 2, "carry": [0] * 6},
                {"id": 1, "player": 1, "x": 3, "y": 0, "ms": 1, "cc": 1, "hp": 1, "chop": 1, "carry": [0] * 6},
            ],
        },
    }
    return fixture, frame


def test_action_count_includes_wait_moves_and_chop() -> None:
    fixture, frame = fixture_and_frame()

    count = troll_action_count(frame["state"], frame["state"]["units"][0], fixture["map"])

    assert count == 3  # WAIT, MOVE-to-shack, CHOP


def test_one_unit_per_side_is_in_documented_size_envelope() -> None:
    fixture, frame = fixture_and_frame()

    result = position_metrics(fixture, frame)

    assert result["units_by_side"] == [1, 1]
    assert result["horizon_to_observed_end"] == 2
    assert result["documented_size_envelope"] is True
