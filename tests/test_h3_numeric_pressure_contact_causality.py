import math

from cgauto.h3_numeric_pressure_contact_causality import (
    did_ratio_from_pairs,
    did_summary,
    distance,
    match_rows,
    risk_counts,
    smoothed_rate,
)


def test_risk_counts_contact_and_censoring():
    crops = [
        {"birth_turn": 5, "death_turn": 20, "first_our_contact_turn": 10},
        {"birth_turn": 8, "death_turn": 12, "first_our_contact_turn": None},
        {"birth_turn": 30, "death_turn": None, "first_our_contact_turn": None},
    ]
    assert risk_counts(crops, 6, 10, 40) == {"events": 1, "exposure": 8}
    assert risk_counts(crops, 11, 14, 40) == {"events": 0, "exposure": 2}


def test_contact_on_death_turn_is_retained():
    crops = [
        {"birth_turn": 5, "death_turn": 10, "first_our_contact_turn": 10},
    ]
    assert risk_counts(crops, 5, 10, 20) == {"events": 1, "exposure": 6}


def test_jeffreys_smoothing_is_finite():
    assert math.isclose(smoothed_rate({"events": 0, "exposure": 9}), 0.05)


def pair(s_pre, s_post, c_pre, c_post):
    return {
        "scaled_windows": {
            "pre": {"events": s_pre, "exposure": 100},
            "post": {"events": s_post, "exposure": 100},
        },
        "control_windows": {
            "pre": {"events": c_pre, "exposure": 100},
            "post": {"events": c_post, "exposure": 100},
        },
    }


def test_did_ratio_detects_unique_scaled_decline():
    value = did_ratio_from_pairs([pair(10, 5, 10, 10)])
    assert value < 0.55


def test_bootstrap_is_deterministic():
    pairs = [pair(10, 5, 10, 10), pair(8, 4, 9, 9)]
    left = did_summary(pairs, replicates=100, seed=7)
    right = did_summary(pairs, replicates=100, seed=7)
    assert left == right


def audit_row(game_id, seat, score, turns=300, anchor=100, value=0):
    opening = {
        "fruit_total": value,
        "tree_health_total": value,
        "tree_total": value,
        "shack_door_distance": value,
        "own_private_fruit": value,
        "opponent_private_fruit": value,
        "water_adjacent_cells": value,
    }
    return {
        "game_id": game_id,
        "seat": seat,
        "opponent_agent_id": game_id + 1000,
        "opponent_ladder_score": score,
        "turns": turns,
        "third_train_turn": anchor,
        "permanent_crossover_turn": 301,
        "opening": opening,
        "opponent_crop_records": [],
    }


def scaling():
    names = (
        "opponent_ladder_score",
        "fruit_total",
        "tree_health_total",
        "tree_total",
        "shack_door_distance",
        "own_private_fruit",
        "opponent_private_fruit",
        "water_adjacent_cells",
    )
    return {name: {"mean": 0.0, "sd": 1.0} for name in names}


def test_matching_uses_exact_seat_and_deterministic_game_id_tie():
    treated = audit_row(10, 1, 20.0)
    wrong_seat = audit_row(1, 0, 20.0)
    tie_high_id = audit_row(3, 1, 20.0)
    tie_low_id = audit_row(2, 1, 20.0)
    for row in (wrong_seat, tie_high_id, tie_low_id):
        row["third_train_turn"] = None
    pairs = match_rows(
        [treated], [wrong_seat, tie_high_id, tie_low_id], scaling()
    )
    assert pairs[0]["control_game_id"] == 2


def test_distance_uses_only_frozen_match_features():
    left = audit_row(1, 0, 20.0)
    right = audit_row(2, 0, 21.0)
    base = distance(left, right, scaling())
    right["margin"] = -9999
    right["won"] = False
    assert distance(left, right, scaling()) == base
