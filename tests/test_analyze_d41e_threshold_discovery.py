import math

from cgauto.analyze_d41e_threshold_discovery import analyze, select, stats


def row(branch, gap, turn, delta=1, *, seed=9_760_000, opponent="resident", cohort="residual_top"):
    return {
        "branch": branch,
        "residual_gap": gap,
        "turn": turn,
        "margin_delta": delta,
        "map_seed": seed,
        "opponent": opponent,
        "phase": "early" if turn < 100 else ("middle" if turn < 200 else "late"),
        "cohort": cohort,
    }


def test_rule_is_branch_phase_gap_gated_and_inclusive():
    assert select(row("evacuation", 0.020, 150))
    assert select(row("evacuation", 0.030, 150))
    assert not select(row("evacuation", 0.0199, 20))
    assert select(row("rate", 0.280, 99))
    assert select(row("rate", 0.340, 200))
    assert not select(row("rate", 0.300, 100))
    assert not select(row("rate", 0.300, 199))
    assert not select(row("train", 0.300, 20))
    assert not select(row("deficit", 0.300, 20))


def test_stats_reports_paired_distribution():
    report = stats([row("rate", 0.3, 20, value) for value in (-2, 0, 5, 9)])
    assert report["samples"] == 4
    assert report["mean"] == 3.0
    assert report["median"] == 2.5
    assert report["positive_rate"] == 0.5
    assert report["tie_rate"] == 0.25
    assert math.isfinite(report["normal_95_low"])


def test_analysis_keeps_groups_and_fails_small_synthetic_bank():
    rows = [
        row("evacuation", 0.025, 20, 10, seed=9_760_000 + index, opponent=f"o{index}")
        for index in range(8)
    ]
    rows += [row("rate", 0.3, 220, 12, seed=9_760_000 + index, opponent=f"o{index}") for index in range(8)]
    rows.append(row("rate", 0.3, 150, 1))
    report = analyze(rows)
    assert report["selected_samples"] == 16
    assert set(report["by_branch"]) == {"evacuation", "rate"}
    assert len(report["map_folds"]) == 8
    assert len(report["by_opponent"]) == 8
    assert report["gates"]["at_least_128_samples"] is False
    assert report["pass"] is False
