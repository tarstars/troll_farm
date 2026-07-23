"""Tests for D72 recurrent-population analysis helpers."""

from __future__ import annotations

from cgauto.analyze_d72a_recurrent_opening_population import (
    compare_selections,
    crop_safe_oracle,
)


def row(
    policy: str,
    margin: int,
    own: int,
    opponent: int,
    *,
    crop: int = 1,
    seed_action: int = 0,
) -> dict[str, str]:
    return {
        "policy": policy,
        "family": "portfolio_rnn",
        "map_seed": "9804000",
        "seat": "0",
        "opponent": "resident",
        "margin": str(margin),
        "own_score": str(own),
        "opponent_score": str(opponent),
        "own_created_crops": str(crop),
        "action_seed_plum": str(seed_action),
        "action_seed_lemon": "0",
        "action_seed_apple": "0",
        "action_seed_banana": "0",
    }


def test_crop_safe_oracle_uses_frozen_tie_breaks_and_excludes_cropless() -> None:
    rows = [
        row("portfolio_rnn_00", 100, 120, 20, crop=0),
        row("portfolio_rnn_03", 10, 30, 20),
        row("portfolio_rnn_02", 10, 31, 21),
        row("portfolio_rnn_01", 10, 31, 21),
    ]
    selected = crop_safe_oracle(rows, "portfolio_rnn")
    assert next(iter(selected.values()))["policy"] == "portfolio_rnn_01"


def test_comparison_reports_margin_components_and_strict_rate() -> None:
    candidate = {
        (9804000, 0, "resident"): row("portfolio_rnn_00", 10, 15, 5),
        (9804001, 0, "resident"): {
            **row("portfolio_rnn_01", 0, 8, 8),
            "map_seed": "9804001",
        },
    }
    baseline = {
        (9804000, 0, "resident"): row("balanced", 4, 10, 6),
        (9804001, 0, "resident"): {
            **row("balanced", 0, 7, 7),
            "map_seed": "9804001",
        },
    }
    report = compare_selections(candidate, baseline)
    assert report["identity_exact"]
    assert report["mean_margin_delta"] == 3
    assert report["strict_improvement_rate"] == 0.5
    assert report["mean_own_score_delta"] == 3
    assert report["mean_opponent_score_delta"] == 0
