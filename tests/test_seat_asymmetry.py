from __future__ import annotations

import statistics

from cgauto.seat_asymmetry import (
    cluster_bootstrap_ci,
    cluster_sign_flip_p,
    fixed_effect_sensitivity,
    is_match,
    leave_one_cluster_out,
    matched_targets,
    same_sign,
    synthetic_rows,
)


def test_exact_matching_uses_opposite_seat_and_pre_outcome_fields() -> None:
    rows = synthetic_rows()
    target = next(row for row in rows if row["seat"] == 1)
    valid = next(
        row
        for row in rows
        if row["seat"] == 0 and row["opponent_id"] == target["opponent_id"]
    )
    assert is_match(
        target,
        valid,
        target_seat=1,
        identity_mode="exact",
        opponent_score_band=1.0,
    )
    wrong_identity = dict(valid, opponent_id=999)
    wrong_seat = dict(valid, seat=1)
    wrong_map = dict(valid, map_width=99)
    assert not is_match(
        target,
        wrong_identity,
        target_seat=1,
        identity_mode="exact",
        opponent_score_band=1.0,
    )
    assert not is_match(
        target,
        wrong_seat,
        target_seat=1,
        identity_mode="exact",
        opponent_score_band=1.0,
    )
    assert not is_match(
        target,
        wrong_map,
        target_seat=1,
        identity_mode="exact",
        opponent_score_band=1.0,
    )


def test_primary_and_reverse_orientation_agree() -> None:
    rows = synthetic_rows()
    primary, unsupported = matched_targets(rows, target_seat=1)
    reverse, reverse_unsupported = matched_targets(rows, target_seat=0)
    assert not unsupported and not reverse_unsupported
    assert statistics.mean(row["margin_residual"] for row in primary) == -30.0
    assert -statistics.mean(row["margin_residual"] for row in reverse) == -30.0


def test_cluster_resampling_is_deterministic() -> None:
    matched, _ = matched_targets(synthetic_rows(), target_seat=1)
    first_ci = cluster_bootstrap_ci(
        matched, field="margin_residual", reps=500, seed=123
    )
    second_ci = cluster_bootstrap_ci(
        matched, field="margin_residual", reps=500, seed=123
    )
    first_p = cluster_sign_flip_p(
        matched, field="margin_residual", reps=500, seed=456
    )
    second_p = cluster_sign_flip_p(
        matched, field="margin_residual", reps=500, seed=456
    )
    assert first_ci == second_ci == (-30.0, -30.0)
    assert first_p == second_p
    assert 0 < first_p <= 1


def test_leave_one_cluster_out_preserves_direction() -> None:
    matched, _ = matched_targets(synthetic_rows(), target_seat=1)
    estimates = leave_one_cluster_out(matched)
    assert len(estimates) == 3
    assert all(row["margin_difference"] == -30.0 for row in estimates)
    assert all(same_sign(row["margin_difference"], -30.0) for row in estimates)


def test_fixed_effect_sensitivity_has_seat_1_minus_seat_0_orientation() -> None:
    result = fixed_effect_sensitivity(synthetic_rows())
    assert result["identities"] == 3
    assert result["identity_equal_margin_difference"] == -30.0
    assert result["game_weighted_margin_difference"] == -30.0
