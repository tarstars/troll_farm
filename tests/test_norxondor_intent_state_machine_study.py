from __future__ import annotations

from cgauto.norxondor_intent_state_machine_study import episode_rows


def row(turn: int, verb: str, intent: str | None = None) -> dict:
    return {
        "game_id": 11,
        "unit_id": 3,
        "ordinal": 1,
        "turn": turn,
        "verb": verb,
        "intent": intent,
        "features": {"phase": "01-05"},
    }


def test_episode_rows_predict_once_and_remember_previous_action() -> None:
    rows = [
        row(1, "HARVEST"),
        row(2, "MOVE", "GO_DROP"),
        row(3, "MOVE", "GO_DROP"),
        row(4, "DROP"),
        row(5, "MOVE", "GO_CHOP"),
    ]

    result = episode_rows(rows)

    assert len(result) == 2
    assert result[0]["label"] == "GO_DROP"
    assert result[0]["moves"] == 2
    assert result[0]["previous_action"] == "HARVEST"
    assert result[0]["features"]["previous_action"] == "HARVEST"
    assert result[1]["previous_action"] == "DROP"


def test_episode_rows_collapses_pick_and_plant_to_farm_history() -> None:
    rows = [row(1, "PLANT"), row(2, "MOVE", "GO_HARVEST")]

    result = episode_rows(rows)

    assert result[0]["previous_action"] == "FARM"
