from __future__ import annotations

import numpy as np

from cgauto.rl_level6_env import (
    LEVEL6_OPPONENT_NAMES,
    Level6VecEnv,
    aggregate,
    level6_opponent,
)


def test_level6_opponent_assignment_is_deterministic_and_covers_every_mode() -> None:
    first = [level6_opponent(seed) for seed in range(500)]
    second = [level6_opponent(seed) for seed in range(500)]
    assert first == second
    assert {name for _, name in first} == set(LEVEL6_OPPONENT_NAMES)


def test_competitive_aggregate_tracks_opponent_and_recipe_buckets() -> None:
    rows = []
    for index in range(48):
        _, opponent = level6_opponent(index)
        margin = index % 3 - 1
        rows.append(
            {
                "opponent": opponent,
                "recipe_id": index % 8,
                "margin": margin,
                "own_score": 10 + margin,
                "opponent_score": 10,
                "training_completed": True,
                "created_crop": index % 2 == 0,
                "renewable_harvests": int(index % 4 == 0),
                "turn": 300,
                "return_margin_error": 0.0,
            }
        )
    report = aggregate(rows)
    assert report["episodes"] == 48
    assert report["terminal_turn_min"] == report["terminal_turn_max"] == 300
    assert sum(bucket["episodes"] for bucket in report["by_opponent"].values()) == 48
    assert sum(bucket["episodes"] for bucket in report["by_recipe"].values()) == 48


def test_level6_current_metadata_advances_and_preserves_seed() -> None:
    with Level6VecEnv(2, 1234, max_turns=30) as env:
        turns, phases, seeds = env.current_metadata()
        assert turns.tolist() == [0, 0]
        assert phases.tolist() == [0, 0]
        assert seeds.tolist() == [1234, 1235]

        env.step(env.teacher_actions())
        next_turns, next_phases, next_seeds = env.current_metadata()
        assert next_seeds.tolist() == [1234, 1235]
        assert np.all(next_turns >= turns)
        assert set(next_phases.tolist()) <= {0, 1}
