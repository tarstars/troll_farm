"""Tests for D68a's frozen consumed mechanism gate."""

from __future__ import annotations

from cgauto.analyze_d68a_bill_capitalization_portfolio import task_pass


def row(**changes: str) -> dict[str, str]:
    result = {
        "policy": "bill_portfolio",
        "prefix_seen": "1",
        "own_workers": "2",
        "first_worker_two_turn": "70",
        "forced_harvest_deposits": "2",
        "missing_bank_progress": "1",
        "own_created_crops": "3",
        "max_workers": "2",
        "invalid_direct_commands": "0",
        "provenance_failures": "0",
        "deposit_prediction_failures": "0",
        "formula_violations": "0",
        "carry_before_plant_violations": "0",
        "affordable_plant_violations": "0",
        "harvest_target_violations": "0",
        "interventions_after_worker_two": "0",
        "finite_state_failures": "0",
    }
    result.update(changes)
    return result


def test_task_pass_requires_worker_and_positive_missing_bank_progress() -> None:
    assert task_pass(row())
    assert not task_pass(row(own_workers="1", first_worker_two_turn="-1"))
    assert not task_pass(row(missing_bank_progress="0"))


def test_task_pass_rejects_any_policy_or_integrity_violation() -> None:
    assert not task_pass(row(formula_violations="1"))
    assert not task_pass(row(interventions_after_worker_two="1"))
    assert not task_pass(row(policy="d40_control"))
