from __future__ import annotations

from cgauto.opponent_specific_losses import (
    bootstrap_ci,
    holm_adjust,
    is_match,
    matched_null_p,
    residual_vectors,
    split_means,
)


def row(**overrides) -> dict:
    base = {
        "record_index": 1,
        "game_id": 100,
        "opponent_id": 1,
        "opponent_pseudo": "target",
        "seat": 0,
        "map_width": 16,
        "map_height": 8,
        "opponent_score": 22.0,
        "resident_score": 21.5,
        "initial_trees": 20,
        "margin": -20.0,
        "win": 0.0,
    }
    base.update(overrides)
    return base


def test_match_uses_only_frozen_pre_game_fields() -> None:
    target = row()
    control = row(opponent_id=2, opponent_pseudo="control", margin=999, win=1)
    assert is_match(target, control, {1}, {"target"}, 1.0)
    assert not is_match(
        target,
        row(opponent_id=2, opponent_pseudo="target"),
        {1},
        {"target"},
        1.0,
    )
    assert not is_match(
        target,
        row(opponent_id=2, opponent_pseudo="control", map_width=18),
        {1},
        {"target"},
        1.0,
    )
    assert not is_match(
        target,
        row(opponent_id=2, opponent_pseudo="control", opponent_score=23.01),
        {1},
        {"target"},
        1.0,
    )


def test_residuals_are_target_minus_own_control_mean() -> None:
    targets = [row(margin=-30, win=0), row(game_id=101, margin=10, win=1)]
    pools = [
        [row(margin=10, win=1), row(margin=20, win=1)],
        [row(margin=0, win=0), row(margin=20, win=1)],
    ]
    margins, wins = residual_vectors(targets, pools)
    assert margins == [-45, 0]
    assert wins == [-1, 0.5]


def test_holm_adjustment_is_monotone_in_sorted_p_order() -> None:
    adjusted = holm_adjust({10: 0.01, 20: 0.04, 30: 0.20})
    assert adjusted == {10: 0.03, 20: 0.08, 30: 0.20}


def test_bootstrap_and_null_are_seed_deterministic() -> None:
    assert bootstrap_ci([-30, -20, -10], 500, 9) == bootstrap_ci(
        [-30, -20, -10], 500, 9
    )
    pools = [
        [row(margin=-10), row(margin=10)],
        [row(margin=-20), row(margin=20)],
    ]
    assert matched_null_p(-25, pools, 500, 4) == matched_null_p(
        -25, pools, 500, 4
    )


def test_split_means_preserve_seat_and_chronology() -> None:
    rows = [
        row(game_id=1, seat=0),
        row(game_id=2, seat=1),
        row(game_id=3, seat=0),
        row(game_id=4, seat=1),
    ]
    result = split_means(rows, [-40, -30, -20, -10])
    assert result["seat"]["0"]["mean_margin_residual"] == -30
    assert result["seat"]["1"]["mean_margin_residual"] == -20
    assert result["chronological"]["early"]["mean_margin_residual"] == -35
    assert result["chronological"]["late"]["mean_margin_residual"] == -15
