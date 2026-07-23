from __future__ import annotations

from cgauto.evaluate_d41b_exact_prior import (
    COMPARISON_FIELDS,
    RESIDUAL_PARAMETERS,
    compare_baseline,
    compare_repeats,
    summarize,
)


def terminal(task_index: int = 0) -> dict:
    row = {
        "task_index": task_index,
        "map_seed": 9_711_000,
        "seat": 0,
        "opponent": "resident",
        "own_score": 10,
        "opponent_score": 5,
        "margin": 5,
        "own_workers": 3,
        "successful_trains": 2,
        "own_created_crops": 1,
        "invalidated_jobs": 0,
        "invalid_direct_commands": 0,
        "provenance_failures": 0,
        "deposit_prediction_failures": 0,
        "action_hash": 11,
        "state_hash": 12,
    }
    return row


def test_residual_parameter_budget_is_frozen() -> None:
    assert RESIDUAL_PARAMETERS == 737


def test_terminal_comparisons_detect_exact_and_changed_hash() -> None:
    row = terminal()
    key = (row["map_seed"], row["seat"], row["opponent"])
    baseline = {key: {field: row[field] for field in COMPARISON_FIELDS}}
    assert compare_baseline([row], baseline)["exact"]
    changed = dict(row, action_hash=99)
    assert not compare_baseline([changed], baseline)["exact"]
    assert compare_repeats([row], [dict(row)])["exact"]
    assert not compare_repeats([row], [changed])["exact"]


def test_summary_preserves_integrity_and_workforce() -> None:
    result = summarize([terminal(), dict(terminal(1), own_workers=1)])
    assert result["worker_two_rate"] == 0.5
    assert result["worker_three_rate"] == 0.5
    assert result["maximum_workers"] == 3
    assert result["invalid_direct_commands"] == 0
