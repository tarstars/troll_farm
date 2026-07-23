"""Tests for live-agent loss signature helpers."""

from cgauto.live_loss_analysis import longest_harvest_drop_run, pattern_counts


def test_longest_harvest_drop_run_counts_alternating_cycles() -> None:
    actions = {
        5: "HARVEST",
        6: "DROP",
        7: "HARVEST",
        8: "DROP",
        9: "HARVEST",
        10: "DROP",
        20: "HARVEST",
        21: "DROP",
    }

    assert longest_harvest_drop_run(actions) == 3


def test_pattern_counts_handles_missing_end_curve() -> None:
    losses = [
        {
            "wood_gap_t100": 4,
            "wood_gap_t300": -2,
            "opp_planted": 30,
            "opp_harvested": 40,
            "opp_trained": 2,
            "opp_chops_landed": 70,
            "opp_wood": 80,
        },
        {
            "wood_gap_t100": 3,
            "wood_gap_t300": None,
            "opp_planted": 10,
            "opp_harvested": 10,
            "opp_trained": 1,
            "opp_chops_landed": 20,
            "opp_wood": 30,
        },
    ]

    result = pattern_counts(losses)

    assert result["wood_ahead_t100_then_behind_t300"] == {"count": 1, "games": 2}
    assert result["opponent_at_least_20_plants_and_20_harvested"]["count"] == 1
