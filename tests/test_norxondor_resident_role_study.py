from __future__ import annotations

import pytest

from cgauto.norxondor_resident_role_study import analyze, summarize_policy


def row(opponent: str, margin: int, score: int, workers: int = 3) -> dict:
    return {
        "seed": 1,
        "seat": 0,
        "decision_turn": 3,
        "actual_opponent": opponent,
        "policy": "policy",
        "resident_margin": 10,
        "policy_margin": 10 + margin,
        "margin_delta": margin,
        "resident_score": 20,
        "policy_score": 20 + score,
        "score_delta": score,
        "resident_workers": 2,
        "policy_workers": workers,
        "scenario_elapsed_us": 1,
    }


def test_policy_gate_requires_robust_opponent_means() -> None:
    rows = [row(f"opponent-{index}", 3, 4) for index in range(8)]
    assert summarize_policy(rows)["gate_passed"]
    rows[-1]["margin_delta"] = -6
    report = summarize_policy(rows)
    assert not report["gate_passed"]
    assert report["worst_opponent_margin_delta"] == -6


def test_analyze_rejects_duplicate_scenario_policy_rows() -> None:
    duplicate = row("opponent", 3, 4)
    with pytest.raises(ValueError, match="duplicate"):
        analyze([duplicate, duplicate.copy()])
