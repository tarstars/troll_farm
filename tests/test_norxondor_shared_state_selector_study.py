from __future__ import annotations

from cgauto.norxondor_shared_state_selector_study import (
    aggregate,
    compatible,
    evaluate,
)


def model_row(model: str, actual: str, mismatch: int, delta: int) -> dict:
    return {
        "seed": 1,
        "seat": 0,
        "decision_turn": 3,
        "actual_opponent": actual,
        "model": model,
        "prefix_mismatch": mismatch,
        "exact_prefix_transitions": int(mismatch == 0),
        "margin_delta": delta,
        "score_delta": delta,
        "resident_margin": 10,
        "three_worker_margin": 10 + delta,
        "resident_score": 20,
        "three_worker_score": 20 + delta,
        "serial_prediction_us": 100,
    }


def test_compatibility_band_keeps_all_exact_ties() -> None:
    group = [
        model_row("actual", "actual", 0, 8),
        model_row("twin", "actual", 0, 6),
        model_row("far", "actual", 300, -9),
    ]

    assert {row["model"] for row in compatible(group, "band0")} == {
        "actual",
        "twin",
    }
    assert len(compatible(group, "band250")) == 2
    assert len(compatible(group, "band1000")) == 3


def test_lower_quartile_is_conservative_order_statistic() -> None:
    assert aggregate([-8, 1, 5, 9], "lower_quartile") == -8
    assert aggregate([-8, 1, 5, 9, 12], "lower_quartile") == 1


def test_evaluate_uses_actual_model_only_for_truth() -> None:
    group = [
        model_row("actual", "actual", 0, 8),
        model_row("twin", "actual", 0, 6),
        model_row("far", "actual", 300, -9),
    ]
    config = {
        "decision_turn": 3,
        "conditioning": "band0",
        "metric": "margin_delta",
        "aggregate": "minimum",
        "buffer": 5,
    }

    report = evaluate([group], config)

    assert report["selected_alternative"] == 1
    assert report["margin_delta_vs_resident"]["mean"] == 8
    assert report["actual_model_compatible_rate"] == 1
