from __future__ import annotations

from cgauto.opponent_crop_field_activation import (
    active_opponent_crops,
    first_action_divergence,
    instrument_crop_probe,
    parse_probe_events,
    CANDIDATE,
)


def test_crop_probe_has_one_stdout_neutral_selection_site() -> None:
    source = CANDIDATE.read_text()
    probed = instrument_crop_probe(source)
    assert probed.count("@CROP_SELECT") == 1
    assert len(probed) > len(source)


def test_probe_event_parser_recovers_turn_cell_command_and_unit() -> None:
    events = parse_probe_events(
        "@CROP_SELECT t=41 cell=3,7 command=MOVE 12 3 7\nnoise\n"
    )
    assert events == [
        {
            "turn": 41,
            "cell": [3, 7],
            "command": "MOVE 12 3 7",
            "unit_id": 12,
        }
    ]


def test_first_divergence_ignores_message_only_changes() -> None:
    assert first_action_divergence(["MSG a;WAIT"], ["MSG b;WAIT"]) is None
    assert first_action_divergence(["WAIT", "CHOP 1"], ["WAIT", "WAIT"]) == 2


def test_active_crop_requires_observation_after_birth_and_before_death() -> None:
    row = {
        "opponent_crop_records": [
            {"cell": [2, 3], "birth_turn": 10, "death_turn": 14},
            {"cell": [4, 5], "birth_turn": 8, "death_turn": None},
        ]
    }
    assert active_opponent_crops(row, 10) == {(4, 5): row["opponent_crop_records"][1]}
    assert set(active_opponent_crops(row, 11)) == {(2, 3), (4, 5)}
    assert set(active_opponent_crops(row, 14)) == {(2, 3), (4, 5)}
    assert set(active_opponent_crops(row, 15)) == {(4, 5)}
