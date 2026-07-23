from __future__ import annotations

from copy import deepcopy

import pytest

from cgauto.yamo_opponent_crop_priority_study import (
    analyze,
    selection_key,
    summarize_profile,
    trimmed_mean,
)


def row(seed: int, seat: int, opponent: str, profile: str = "b100_e6") -> dict:
    return {
        "seed": seed,
        "seat": seat,
        "opponent": opponent,
        "profile": profile,
        "bonus": 100,
        "eta_limit": 6,
        "start_turn": 1,
        "minimum_seen": 1,
        "control_margin": 0,
        "candidate_margin": 3,
        "margin_delta": 3,
        "control_score": 100,
        "candidate_score": 100,
        "score_delta": 0,
        "control_opponent_score": 100,
        "candidate_opponent_score": 96,
        "opponent_score_delta": -4,
        "control_wood": 20,
        "candidate_wood": 20,
        "wood_delta": 0,
        "control_opponent_wood": 20,
        "candidate_opponent_wood": 16,
        "opponent_wood_delta": -4,
        "control_workers": 1,
        "candidate_workers": 1,
        "control_terminal_turn": 301,
        "candidate_terminal_turn": 301,
        "crops_seen": 10,
        "crop_priority_selections": 1,
        "first_crop_priority_turn": 50,
        "crops_alive": 2,
        "divergence_turns": 1,
        "first_divergence_turn": 50,
    }


def passing_grid(profile: str = "b100_e6") -> list[dict]:
    return [
        row(seed, seat, f"opponent-{opponent}", profile)
        for seed in range(3)
        for seat in range(2)
        for opponent in range(8)
    ]


def test_trimmed_mean_removes_five_percent_from_each_tail() -> None:
    assert trimmed_mean([-100] + list(range(18)) + [100]) == 8.5


def test_complete_policy_gate_requires_opponent_score_suppression() -> None:
    rows = passing_grid()
    assert summarize_profile(rows)["gate_passed"]
    for item in rows:
        item["opponent_score_delta"] = -3
    report = summarize_profile(rows)
    assert not report["gate_passed"]
    assert not report["gate_checks"]["mean_opponent_score_delta"]


def test_selection_key_prefers_weaker_profile_after_equal_effects() -> None:
    weaker = summarize_profile(passing_grid())
    stronger_rows = passing_grid("b250_e6")
    for item in stronger_rows:
        item["bonus"] = 250
    stronger = summarize_profile(stronger_rows)
    assert selection_key(("b100_e6", weaker)) > selection_key(("b250_e6", stronger))


def test_analyze_selects_only_gate_eligible_profile() -> None:
    passing = passing_grid()
    failing = deepcopy(passing_grid("b250_e6"))
    for item in failing:
        item["bonus"] = 250
        item["margin_delta"] = 0
        item["candidate_margin"] = 0
    result = analyze(passing + failing)
    assert result["selected_profile"] == "b100_e6"
    assert result["eligible_profiles"] == ["b100_e6"]
    assert result["decision"]["run_unchanged_replication"]


def test_analyze_rejects_duplicate_cells() -> None:
    duplicate = row(1, 0, "opponent")
    with pytest.raises(ValueError, match="duplicate"):
        analyze([duplicate, duplicate.copy()])
