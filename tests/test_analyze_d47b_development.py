import pytest

from cgauto.analyze_d47b_development import (
    TASKS,
    development_gates,
    normal_lower_bound,
    trimmed_mean,
)


def passing_metrics() -> dict:
    return {
        "tasks": TASKS,
        "changed_action_hash_rate": 0.5,
        "role_eligible_decisions": 1_024,
        "role_overrides": 512,
        "paired_mean_margin_delta": 8.0,
        "paired_trimmed_5pct_margin_delta": 5.0,
        "map_seed_normal_95pct_lower_bound": 3.01,
        "paired_mean_own_score_delta": 3.0,
        "paired_mean_opponent_score_delta": 0.0,
        "positive_opponent_families": 6,
        "worst_opponent_family_mean_margin_delta": -8.0,
        "worker_two_rate": 0.95,
        "worker_three_rate": 0.88,
        "crop_rate": 0.97,
        "candidate_catastrophes": 3,
        "control_catastrophes": 3,
        "candidate_negative_margin_mass": 100,
        "control_negative_margin_mass": 100,
    }


def test_trimmed_mean_removes_five_percent_from_each_tail() -> None:
    values = [-1_000] * 5 + [10] * 90 + [1_000] * 5
    assert trimmed_mean(values) == 10.0


def test_normal_lower_bound_uses_sample_standard_error() -> None:
    actual = normal_lower_bound([1.0, 3.0])
    assert actual == pytest.approx(2.0 - 1.96)


def test_development_gates_accept_exact_nonstrict_floors() -> None:
    gates = development_gates(
        passing_metrics(), repeat_byte_identical=True, integrity_failures=0
    )
    assert all(gates.values())


def test_development_gates_reject_strict_lower_bound_and_tail_regression() -> None:
    metrics = passing_metrics()
    metrics["map_seed_normal_95pct_lower_bound"] = 3.0
    metrics["candidate_negative_margin_mass"] = 101
    gates = development_gates(
        metrics, repeat_byte_identical=True, integrity_failures=0
    )
    assert not gates["map_seed_normal_lower_bound_above_3"]
    assert not gates["negative_margin_mass_not_increased"]
