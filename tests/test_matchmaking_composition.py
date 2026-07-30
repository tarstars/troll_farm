from __future__ import annotations

from cgauto.matchmaking_composition import (
    SCORE_BINS,
    block_bootstrap_ci,
    circular_shift_p,
    contrast,
    endpoints,
    js_divergence,
    score_bin,
    same_sign,
    synthetic_rows,
)


def test_endpoint_windows_exclude_middle() -> None:
    rows = synthetic_rows()
    early, late = endpoints(rows, 3)
    assert [row["game_id"] for row in early] == [100, 101, 102]
    assert [row["game_id"] for row in late] == [109, 110, 111]
    assert set(row["game_id"] for row in early).isdisjoint(
        row["game_id"] for row in late
    )


def test_contrast_is_late_minus_early() -> None:
    early, late = endpoints(synthetic_rows(), 3)
    result = contrast(early, late)
    assert result["mean_opponent_score"] == 9.0
    assert result["median_opponent_score"] == 9.0
    assert result["mean_opponent_minus_resident_gap"] == 9.0


def test_block_bootstrap_is_deterministic() -> None:
    early, late = endpoints(synthetic_rows(), 3)
    first = block_bootstrap_ci(
        early, late, reps=500, block_length=2, seed=123
    )
    second = block_bootstrap_ci(
        early, late, reps=500, block_length=2, seed=123
    )
    assert first == second
    assert first[0] <= 9.0 <= first[1]


def test_circular_shift_null_preserves_full_sequence() -> None:
    result = circular_shift_p(synthetic_rows(), 3)
    assert result["rotations"] == 12
    assert result["observed"] == 9.0
    assert result["null_min"] <= result["observed"] <= result["null_max"]
    assert 0 < result["two_sided_p"] <= 1


def test_score_bins_js_and_sign_helpers() -> None:
    labels = [label for label, _lower, _upper in SCORE_BINS]
    assert score_bin(19.99) == "lt_20"
    assert score_bin(20.0) == "20_to_lt_22"
    assert score_bin(26.0) == "ge_26"
    uniform = {label: 1 / len(labels) for label in labels}
    assert js_divergence(uniform, uniform) == 0.0
    assert same_sign(0.5, 1.0)
    assert not same_sign(-0.5, 1.0)
