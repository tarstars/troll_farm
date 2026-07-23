from __future__ import annotations

from cgauto.escdemon_training_trigger_study import (
    held_game_predictions,
    parse_train,
    study,
)


def test_parse_train_requires_complete_command() -> None:
    assert parse_train("TRAIN 2 3 0 1") == (2, 3, 0, 1)


def test_held_game_policy_selection_excludes_the_held_game() -> None:
    actual = {1: (1, 1, 0, 1), 2: (2, 2, 0, 2), 3: (3, 3, 0, 3)}
    grid = {
        "a": {1: actual[1], 2: actual[2], 3: (1, 1, 0, 1)},
        "b": {1: (3, 3, 0, 3), 2: actual[2], 3: actual[3]},
    }

    result = held_game_predictions(actual, grid, {1: 1, 2: 2, 3: 3})

    # Holding game 1 leaves policy b perfect on the other two games, so its deliberately wrong
    # game-1 prediction must be used.  A fit on all games would tie and choose policy a instead.
    assert result["predictions"]["1"] == [3, 3, 0, 3]


def test_study_passes_conditional_trigger_but_rejects_unstable_target_grid() -> None:
    actual = [(1, 1, 0, 1), (2, 2, 0, 2), (3, 3, 0, 3)]
    occurrences = []
    for game_id, spec in enumerate(actual, 1):
        occurrences.append(
            {
                "game_id": game_id,
                "agent_id": 7,
                "training_events": [
                    {
                        "turn": game_id,
                        "spec": list(spec),
                        "max_affordable_spec": [spec[0], spec[1], 2, spec[3]],
                        "first_affordable_turn": game_id,
                        "delay_after_affordable": 0,
                    }
                ],
            }
        )
    baseline = {game_id: spec for game_id, spec in enumerate(actual, 1)}
    grid = {
        "left": {1: actual[0], 2: actual[1], 3: actual[0]},
        "right": {1: actual[2], 2: actual[1], 3: actual[2]},
    }
    metadata = {policy: {} for policy in grid}

    result = study(
        {"occurrences": occurrences}, 7, baseline, "baseline", grid, metadata
    )

    assert result["conditional_trigger"]["gate"]["passed"] is True
    assert result["target_policy_grid"]["gate"]["passed"] is False
    assert result["decision"]["build_candidate"] is False
