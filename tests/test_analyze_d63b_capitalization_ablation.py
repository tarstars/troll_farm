"""Tests for the frozen D63b capitalization-signal ablation."""

from __future__ import annotations

from cgauto.analyze_d63b_capitalization_ablation import (
    FLOW_EXACT,
    in_flow,
    in_recipe,
    in_snapshot,
    select_features,
)


def test_recipe_family_contains_specs_but_no_dynamic_economy() -> None:
    assert in_recipe("first_train_harvest")
    assert in_recipe("worker1_chop")
    assert in_recipe("workers_sum_harvest")
    assert not in_recipe("own_harvested_amount")
    assert not in_recipe("open_initial_wood")


def test_snapshot_family_is_instantaneous_and_excludes_history() -> None:
    assert in_snapshot("bank_score_gap")
    assert in_snapshot("own_bank_lemon")
    assert in_snapshot("opponent_carry_plum")
    assert in_snapshot("own_carrying_workers")
    assert in_snapshot("board_lemon_fruit")
    assert in_snapshot("opponent_worker_count")
    assert not in_snapshot("own_harvested_amount")
    assert not in_snapshot("own_successful_plants")
    assert not in_snapshot("worker1_harvest")
    assert not in_snapshot("open_tree_total")


def test_flow_family_adds_only_frozen_cumulative_events() -> None:
    for key in FLOW_EXACT:
        assert in_flow(key)
    assert in_flow("own_successful_plants")
    assert in_flow("opponent_successful_trains")
    assert in_flow("own_planted_lemon")
    assert in_flow("board_plant_count")
    assert not in_flow("first_train_turn")
    assert not in_flow("worker0_chop")
    assert not in_flow("open_initial_lemon")


def test_select_features_is_semantic_and_rejects_unknown_family() -> None:
    features = {
        "worker1_harvest": 3.0,
        "own_bank_lemon": 2.0,
        "own_harvested_amount": 9.0,
        "open_initial_lemon": 1.0,
    }
    assert select_features(features, "recipe") == {"worker1_harvest": 3.0}
    assert select_features(features, "snapshot") == {"own_bank_lemon": 2.0}
    assert select_features(features, "flow") == {
        "own_bank_lemon": 2.0,
        "own_harvested_amount": 9.0,
    }

