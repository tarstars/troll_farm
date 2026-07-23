from __future__ import annotations

from copy import deepcopy

from cgauto.d21_competitive_preflight_analysis import (
    EPISODES,
    SEED_BASE,
    analyze,
)
from cgauto.rl_level2_env import LEVEL2_RECIPE_NAMES, level2_recipe
from cgauto.rl_level6_env import aggregate, level6_opponent


def payload(policy: str, base_margin: int) -> dict:
    rows = []
    for offset, seed in enumerate(range(SEED_BASE, SEED_BASE + EPISODES)):
        opponent_id, opponent = level6_opponent(seed)
        recipe_id, target = level2_recipe(seed)
        margin = base_margin + opponent_id
        if policy == "actor" and offset == 0:
            margin = -1
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
    result = {
        "policy": policy,
        "seed_base": SEED_BASE,
        "seed_stop_exclusive": SEED_BASE + EPISODES,
        "episodes": EPISODES,
        "num_envs": 80,
        "max_turns": 300,
        "random_seed": 2101 if policy == "random" else None,
        "checkpoint_sha256": (
            "44c9a9ed3a232c01fccf9b99b16c3c785b26a1e2c656cb6c40674137138d8de6"
            if policy == "actor"
            else None
        ),
        "illegal_selected_actions": 0,
        "rows": rows,
    }
    result["aggregate"] = aggregate(rows)
    return result


def test_passing_fixture_opens_only_frozen_pilot():
    teacher = payload("teacher", 40)
    random = payload("random", -40)
    actor = payload("actor", 30)

    result = analyze(teacher, deepcopy(teacher), random, actor)

    assert result["preflight_pass"] is True
    assert all(result["gates"].values())
    assert result["authorization"] == "run the frozen local 1M-transition D21 PPO pilot only"


def test_illegal_action_closes_preflight():
    teacher = payload("teacher", 40)
    random = payload("random", -40)
    actor = payload("actor", 30)
    actor["illegal_selected_actions"] = 1

    result = analyze(teacher, deepcopy(teacher), random, actor)

    assert result["preflight_pass"] is False
    assert result["gates"]["no_illegal_selected_action"] is False
