from __future__ import annotations

from cgauto.escdemon_tree_target_study import (
    accuracy,
    fit_ranker,
    ranker_predict,
)


def event(game_id: int, target: tuple[int, int]) -> dict:
    left = (0, 0)
    right = (1, 0)
    return {
        "game_id": game_id,
        "turn": 1,
        "ordinal": 1,
        "target": target,
        "candidates": [left, right],
        "features": {
            left: {"left": 1.0, "right": 0.0},
            right: {"left": 0.0, "right": 1.0},
        },
    }


def test_averaged_ranker_learns_repeated_pairwise_preference() -> None:
    events = [event(game_id, (1, 0)) for game_id in range(1, 5)]

    weights = fit_ranker(events, epochs=3)

    assert ranker_predict(weights, events[0]) == (1, 0)


def test_accuracy_counts_exact_coordinates() -> None:
    events = [event(1, (0, 0)), event(2, (1, 0))]
    result = accuracy(events, [(0, 0), (0, 0)])
    assert result == {"events": 2, "exact": 1, "accuracy": 0.5}
