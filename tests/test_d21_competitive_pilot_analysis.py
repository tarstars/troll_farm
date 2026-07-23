from __future__ import annotations

from copy import deepcopy

from cgauto.d21_competitive_pilot_analysis import (
    VALIDATION_BASE,
    VALIDATION_EPISODES,
    analyze,
)
from cgauto.rl_level2_env import LEVEL2_RECIPE_NAMES, level2_recipe
from cgauto.rl_level6_env import aggregate, level6_opponent
from cgauto.train_d21_competitive_ppo import FROZEN, INITIAL_CHECKPOINT_SHA256


def evaluation(delta_by_opponent: dict[int, int], checkpoint_sha: str) -> dict:
    rows = []
    for seed in range(VALIDATION_BASE, VALIDATION_BASE + VALIDATION_EPISODES):
        opponent_id, opponent = level6_opponent(seed)
        recipe_id, target = level2_recipe(seed)
        margin = -5 + opponent_id + delta_by_opponent[opponent_id]
        rows.append(
            {
                "seed": seed,
                "opponent_id": opponent_id,
                "opponent": opponent,
                "recipe_id": recipe_id,
                "recipe_name": LEVEL2_RECIPE_NAMES[recipe_id],
                "target": list(target),
                "height": 10,
                "turn": 300,
                "return": margin / 100,
                "own_score": 200 + margin,
                "opponent_score": 200,
                "margin": margin,
                "return_margin_error": 0.0,
                "win": margin > 0,
                "training_turn": 10,
                "training_completed": True,
                "created_crop": True,
                "renewable_harvests": 1,
                "opponent_workers": 2,
                "opponent_created_crops": 1,
                "opponent_renewable_harvests": 1,
                "opponent_crop_destructions": 0,
            }
        )
    payload = {
        "policy": "actor",
        "seed_base": VALIDATION_BASE,
        "seed_stop_exclusive": VALIDATION_BASE + VALIDATION_EPISODES,
        "episodes": VALIDATION_EPISODES,
        "num_envs": 100,
        "max_turns": 300,
        "checkpoint_sha256": checkpoint_sha,
        "illegal_selected_actions": 0,
        "rows": rows,
    }
    payload["aggregate"] = aggregate(rows)
    return payload


def training() -> dict:
    config = {
        **FROZEN,
        "initial_checkpoint_sha256": INITIAL_CHECKPOINT_SHA256,
        "intermediate_evaluations": 0,
    }
    return {
        "config": config,
        "global_step": 1_000_000,
        "updates_completed": 100,
        "illegal_actor_actions": 0,
        "checkpoint_sha256": "final",
        "teacher_auxiliary": {"legal_rate": 1.0},
        "logs": [
            {"global_step": step, "loss": 0.1}
            for step in range(10_000, 1_000_001, 10_000)
        ],
    }


def test_passing_pilot_opens_exact_engine_qualification_only():
    initial = evaluation({opponent: 0 for opponent in range(6)}, INITIAL_CHECKPOINT_SHA256)
    final = evaluation({opponent: 10 for opponent in range(6)}, "final")

    result = analyze(initial, final, training())

    assert result["pilot_pass"] is True
    assert all(result["gates"].values())
    assert result["metrics"]["mean_margin_gain"] == 10


def test_large_single_opponent_regression_fails_conjunction():
    initial = evaluation({opponent: 0 for opponent in range(6)}, INITIAL_CHECKPOINT_SHA256)
    final = evaluation({0: -16, 1: 10, 2: 10, 3: 10, 4: 10, 5: 10}, "final")

    result = analyze(initial, final, training())

    assert result["pilot_pass"] is False
    assert result["gates"]["no_opponent_mean_regression_below_minus_15"] is False
