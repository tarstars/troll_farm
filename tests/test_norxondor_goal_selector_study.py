from __future__ import annotations

from cgauto.norxondor_goal_selector_study import (
    accuracy,
    episode_starts,
    truncate_weights,
)


def test_episode_starts_emits_only_first_move_in_each_run() -> None:
    base = {"game_id": 1, "unit_id": 2}
    rows = [
        {**base, "turn": 1, "verb": "MOVE"},
        {**base, "turn": 2, "verb": "MOVE"},
        {**base, "turn": 3, "verb": "CHOP"},
        {**base, "turn": 4, "verb": "MOVE"},
    ]

    result = episode_starts(rows)

    assert [row["turn"] for row in result] == [1, 4]


def test_accuracy_counts_missing_candidate_as_wrong() -> None:
    events = [{"target": (1, 1)}, {"target": (2, 2)}]

    result = accuracy(events, [(1, 1), None])

    assert result == {"events": 2, "exact": 1, "accuracy": 0.5}


def test_truncate_weights_uses_absolute_magnitude_and_stable_ties() -> None:
    weights = {"b": -3.0, "a": 3.0, "c": 2.0}
    assert truncate_weights(weights, 2) == {"a": 3.0, "b": -3.0}
