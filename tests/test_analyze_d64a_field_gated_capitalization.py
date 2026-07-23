"""Unit tests for D64a paired analysis primitives."""

from __future__ import annotations

from cgauto.analyze_d64a_field_gated_capitalization import oracle_report, paired_delta


def row(margin: int, own: int, opponent: int, action: str, action_hash: int) -> dict[str, str]:
    return {
        "margin": str(margin),
        "own_score": str(own),
        "opponent_score": str(opponent),
        "latched_action": action,
        "action_hash": str(action_hash),
    }


def test_paired_delta_preserves_own_and_opponent_signs() -> None:
    key = (9_830_000, 0, "resident")
    left = {key: row(12, 22, 10, "scale", 2)}
    right = {key: row(5, 20, 15, "scale", 1)}

    report = paired_delta(left, right, [key])

    assert report["mean_margin_delta"] == 7
    assert report["mean_own_score_delta"] == 2
    assert report["mean_opponent_score_delta"] == -5
    assert report["changed_action_hashes"] == 1


def test_oracle_uses_margin_then_score_ties_and_reports_selector_agreement() -> None:
    first = (9_830_000, 0, "resident")
    second = (9_830_000, 1, "resident")
    indexed = {
        "d40_control": {
            first: row(5, 20, 15, "scale", 1),
            second: row(7, 30, 23, "scale", 2),
        },
        "never_late_scale": {
            first: row(9, 20, 11, "suppress", 3),
            second: row(7, 31, 24, "suppress", 4),
        },
        "field_snapshot_gate": {
            first: row(9, 20, 11, "suppress", 3),
            second: row(7, 31, 24, "suppress", 4),
        },
    }

    report = oracle_report(indexed, [first, second])

    assert report["selection_counts"] == {"never_late_scale": 2}
    assert report["mean_margin_gain_vs_d40"] == 2
    assert report["strict_margin_improvements"] == 1
    assert report["field_selector_agreement_rate"] == 1.0

