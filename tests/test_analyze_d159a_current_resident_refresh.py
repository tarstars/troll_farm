from cgauto.analyze_d159a_current_resident_refresh import (
    bootstrap_mean_ci,
    early_lead_reversal,
    rank_attack_angles,
    tail_report,
)


def _row(game_id: int, margin: int, opponent: str, turn100_gap: int) -> dict:
    return {
        "game_id": game_id,
        "margin": margin,
        "opponent": opponent,
        "final": {"opponent": {"wood": 70 if margin <= -100 else 20}},
        "timeline": {
            "100": {
                "my": {"score": 50 + turn100_gap},
                "opponent": {"score": 50},
            }
        },
        "opponent_crop_summary": {
            "opponent_wood_collected": 30,
            "our_interception_rate": 0.25,
        },
    }


def test_tail_report_applies_all_four_replication_conditions() -> None:
    rows = [
        _row(1, -200, "a", 20),
        _row(2, -150, "b", 20),
        _row(3, -100, "c", 20),
    ] + [_row(game_id, 10, f"w{game_id}", 5) for game_id in range(4, 21)]
    report = tail_report(rows)
    assert report["frequency"] == 0.15
    assert report["negative_margin_mass_share"] == 1
    assert report["distinct_opponents"] == 3
    assert report["opponent_wood_gap_vs_noncatastrophic"] == 50
    assert report["signature_replicates"] is True


def test_early_lead_reversal_counts_only_positive_lead_losses() -> None:
    rows = [
        _row(1, -20, "a", 10),
        _row(2, -120, "b", 5),
        _row(3, -30, "c", -1),
        _row(4, 40, "d", 10),
    ]
    report = early_lead_reversal(rows)
    assert report["terminal_losses"] == 3
    assert report["reversals"] == 2
    assert report["catastrophic_reversals"] == 1
    assert report["share_of_losses"] == 2 / 3


def test_bootstrap_is_order_invariant_and_deterministic() -> None:
    rows = [_row(3, 30, "c", 1), _row(1, -10, "a", 1), _row(2, 5, "b", 1)]
    forward = bootstrap_mean_ci(rows, seed=9, replicates=200)
    reverse = bootstrap_mean_ci(list(reversed(rows)), seed=9, replicates=200)
    assert forward == reverse
    assert forward[0] <= 25 / 3 <= forward[1]


def test_attack_angles_follow_frozen_ranking_and_have_six_scores() -> None:
    angles = rank_attack_angles()
    assert len(angles) == 10
    assert angles[0]["angle"] == "field_native_bounded_midgame_probe_bank"
    assert [row["rank"] for row in angles] == list(range(1, 11))
    assert all(row["total"] == sum(row["scores"].values()) for row in angles)
    assert all(len(row["scores"]) == 6 for row in angles)
