from __future__ import annotations

import statistics

from cgauto.game_length_effects import (
    cluster_bootstrap_ci,
    is_control,
    leave_one_pseudo_out,
    matched_null_p,
    matched_targets,
    same_sign,
    split_summaries,
    synthetic_rows,
)


def test_primary_control_is_shorter_other_lineage_and_pre_outcome_matched() -> None:
    rows = synthetic_rows()
    target = next(row for row in rows if row["turns"] == 300)
    valid = next(
        row
        for row in rows
        if row["turns"] < 300
        and row["opponent_pseudo"] != target["opponent_pseudo"]
        and row["seat"] == target["seat"]
    )
    assert is_control(
        target,
        valid,
        identity_mode="exclude_pseudo",
        opponent_score_band=1.0,
        min_control_turns=None,
    )
    assert not is_control(
        target,
        dict(valid, turns=300),
        identity_mode="exclude_pseudo",
        opponent_score_band=1.0,
        min_control_turns=None,
    )
    assert not is_control(
        target,
        dict(valid, opponent_pseudo=target["opponent_pseudo"]),
        identity_mode="exclude_pseudo",
        opponent_score_band=1.0,
        min_control_turns=None,
    )


def test_matched_residual_is_cap_minus_shorter() -> None:
    matched, unsupported = matched_targets(synthetic_rows())
    assert not unsupported
    assert len(matched) == 6
    assert statistics.mean(row["margin_residual"] for row in matched) == -45.0
    assert statistics.mean(row["win_residual"] for row in matched) == -1.0


def test_cluster_bootstrap_and_null_are_deterministic() -> None:
    matched, _ = matched_targets(synthetic_rows())
    first_ci = cluster_bootstrap_ci(
        matched, field="margin_residual", reps=500, seed=123
    )
    second_ci = cluster_bootstrap_ci(
        matched, field="margin_residual", reps=500, seed=123
    )
    first_p = matched_null_p(matched, reps=500, seed=456)
    second_p = matched_null_p(matched, reps=500, seed=456)
    assert first_ci == second_ci == (-45.0, -45.0)
    assert first_p == second_p
    assert 0 < first_p <= 1


def test_splits_and_leave_one_lineage_preserve_direction() -> None:
    matched, _ = matched_targets(synthetic_rows())
    splits = split_summaries(matched)
    assert splits["seats"]["0"]["margin_residual"] == -45.0
    assert splits["seats"]["1"]["margin_residual"] == -45.0
    estimates = leave_one_pseudo_out(matched)
    assert len(estimates) == 3
    assert all(row["margin_residual"] == -45.0 for row in estimates)


def test_same_sign_rejects_zero_and_reversal() -> None:
    assert same_sign(-1.0, -2.0)
    assert same_sign(1.0, 2.0)
    assert not same_sign(-1.0, 2.0)
    assert not same_sign(0.0, 2.0)
