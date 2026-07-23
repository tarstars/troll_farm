from __future__ import annotations

import collections

import numpy as np

from cgauto.analyze_level3_policy import (
    CELLS,
    d11_action_gate_thresholds,
    is_empty_seed_recovery_opportunity,
    is_justified_unripe_crop_wait,
    is_move_current,
    record_decision,
    recipe_recovery_gate,
    role_name,
    summarize_role,
)
from cgauto.rl_level1_env import OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH


def farmer_observation() -> np.ndarray:
    observation = np.zeros((OBS_CHANNELS, OBS_HEIGHT, OBS_WIDTH), dtype=np.uint8)
    observation[7, 3, 4] = 255
    observation[94, 0, 0] = 255
    observation[95, 0, 0] = 255
    return observation


def test_role_and_current_move_are_read_from_actor_observation() -> None:
    observation = farmer_observation()
    current_move = 3 * OBS_WIDTH + 4
    assert role_name(observation) == "farmer"
    assert is_move_current(observation, current_move)
    assert not is_move_current(observation, CELLS + current_move)


def test_only_farmer_wait_on_unripe_tracked_crop_is_exempt() -> None:
    observation = farmer_observation()
    action = 3 * OBS_WIDTH + 4
    observation[92, 0, 0] = 255
    observation[50, 3, 4] = 255
    assert is_justified_unripe_crop_wait(observation, action)
    observation[53, 3, 4] = 1
    assert not is_justified_unripe_crop_wait(observation, action)


def test_productive_rate_requires_exact_teacher_command() -> None:
    observation = farmer_observation()
    counter = collections.Counter()
    teacher = 8 * CELLS + 3 * OBS_WIDTH + 4
    wrong_cell_same_verb = 8 * CELLS + 3 * OBS_WIDTH + 5
    record_decision(counter, observation, wrong_cell_same_verb, teacher)
    summary = summarize_role(counter)
    assert summary["productive_opportunities"] == 1
    assert summary["productive_verb_choice_rate"] == 1.0
    assert summary["exact_productive_choice_rate"] == 0.0


def test_empty_seed_recovery_slice_requires_all_depleted_signals() -> None:
    observation = farmer_observation()
    assert is_empty_seed_recovery_opportunity(observation)
    observation[59, 0, 0] = 1
    assert not is_empty_seed_recovery_opportunity(observation)
    observation[59, 0, 0] = 0
    observation[71, 0, 0] = 1
    assert not is_empty_seed_recovery_opportunity(observation)
    observation[71, 0, 0] = 0
    observation[92, 0, 0] = 255
    assert not is_empty_seed_recovery_opportunity(observation)


def test_empty_seed_recovery_agreement_is_summarized_separately() -> None:
    observation = farmer_observation()
    counter = collections.Counter()
    teacher = 3 * OBS_WIDTH + 4
    record_decision(counter, observation, teacher, teacher)
    summary = summarize_role(counter)
    assert summary["empty_seed_recovery_opportunities"] == 1
    assert summary["empty_seed_recovery_exact_choice_rate"] == 1.0
    assert summary["empty_seed_recovery_verb_choice_rate"] == 1.0


def test_recipe_recovery_gate_only_checks_nonempty_recovery_slices() -> None:
    exact = {
        "empty_seed_recovery_opportunities": 10,
        "empty_seed_recovery_exact_choice_rate": 0.3,
    }
    empty = {
        "empty_seed_recovery_opportunities": 0,
        "empty_seed_recovery_exact_choice_rate": None,
    }
    by_recipe = {
        "0": {"roles": {"farmer": exact}},
        "1": {"roles": {"farmer": empty}},
    }
    assert recipe_recovery_gate(by_recipe, 0.3)
    assert not recipe_recovery_gate(by_recipe, 0.31)
    assert recipe_recovery_gate(by_recipe, None)


def test_d11_action_gate_profile_matches_frozen_protocol() -> None:
    assert d11_action_gate_thresholds() == {
        "minimum_role_rate": 0.55,
        "minimum_farmer_rate": 0.55,
        "minimum_chopper_rate": 0.90,
        "minimum_recipe_role_rate": None,
        "maximum_unjustified_waits": 3_000,
        "minimum_empty_seed_recovery_rate": 0.30,
        "minimum_empty_seed_recovery_verb_rate": 0.99,
        "minimum_recipe_empty_seed_recovery_rate": 0.10,
    }
