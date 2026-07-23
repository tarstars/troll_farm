"""Tests for D78 opponent-commitment observability helpers."""

from __future__ import annotations

import numpy as np

from cgauto.analyze_d78a_opponent_commitment import (
    history_features,
    opponent_partition,
    retain_row,
    target_side_metrics,
    top_quintile,
)


def unit(unit_id: int, x: int, chop: int = 1, wood: int = 0) -> dict:
    return {
        "id": unit_id,
        "x": x,
        "y": 0,
        "player": 1,
        "ms": 1,
        "cc": 4,
        "hp": 1,
        "chop": chop,
        "carry": [0, 0, 0, 0, 0, wood],
    }


def state(turn: int, attack_x: int, health: int = 10, wood: int = 0) -> dict:
    return {
        "resolved_turn": turn,
        "inventories": [[0] * 6, [0] * 6],
        "units": [
            {
                **unit(0, 0),
                "player": 0,
            },
            unit(1, attack_x, wood=wood),
        ],
        "plants": [
            {
                "type": "LEMON",
                "x": 0,
                "y": 0,
                "stage": 3,
                "size": 3,
                "fruits": 1,
                "cooldown": 2,
                "health": health,
                "cooldown_effective": 2,
            }
        ],
    }


def test_partition_and_thinning_are_stable() -> None:
    assert opponent_partition(123) == opponent_partition(123)
    assert retain_row(999, (2, 3), 40) == retain_row(999, (2, 3), 40)
    assert {opponent_partition(value) for value in range(1, 100)} == {
        "discovery",
        "validation",
    }


def test_target_metrics_track_nearest_chop_capable_worker() -> None:
    distances = {(x, 0): x for x in range(8)}
    current = state(6, 2)
    values = target_side_metrics(current, 1, distances, require_chop=True)
    assert values["nearest_id"] == 1
    assert values["nearest_distance"] == 2
    assert values["nearest_eta"] == 2
    assert values["within_2"] == 1


def test_history_uses_only_past_and_records_approach_and_damage() -> None:
    states = [state(turn, 6 - turn, 10 if turn < 5 else 8) for turn in range(7)]
    record = {"cell": [0, 0], "birth_turn": 0, "type": "LEMON"}
    features = history_features(
        {}, states, 6, record, 0, 1, {(x, 0): x for x in range(8)}
    )
    assert features["hist_attack_approach_6"] == 6 / 50
    assert features["hist_health_loss_3"] == 2 / 20
    assert features["hist_attack_approach_steps_6"] == 1.0
    assert features["hist_attack_approach_streak"] == 1.0


def test_top_quintile_uses_exact_stable_row_count() -> None:
    labels = np.asarray([0, 1, 0, 1, 0, 0, 1, 0, 0, 0])
    probabilities = np.asarray([0.1, 0.9, 0.2, 0.8, 0.3, 0.4, 0.7, 0.6, 0.5, 0.0])
    report = top_quintile(labels, probabilities)
    assert report["rows"] == 2
    assert report["positive_rows"] == 2
    assert report["precision"] == 1.0
    assert report["lift"] == 1.0 / 0.3
