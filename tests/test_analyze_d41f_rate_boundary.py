from cgauto.analyze_d41f_rate_boundary import individual_gate, threshold_gate


def summary(samples=128, mean=6, positive=0.6, low=1):
    return {
        "margin_delta": {
            "samples": samples,
            "mean": mean,
            "positive_rate": positive,
            "normal_95_low": low,
        }
    }


def test_individual_bin_gate_requires_all_four_conditions():
    assert individual_gate(summary())["pass"]
    assert not individual_gate(summary(samples=127))["pass"]
    assert not individual_gate(summary(mean=4.9))["pass"]
    assert not individual_gate(summary(positive=0.549))["pass"]
    assert not individual_gate(summary(low=0))["pass"]


def row(delta, phase, opponent):
    return {
        "margin_delta": delta,
        "own_score_delta": delta,
        "opponent_score_delta": 0,
        "baseline_margin": 0,
        "treatment_margin": delta,
        "baseline_own_workers": 3,
        "treatment_own_workers": 3,
        "baseline_own_created_crops": 1,
        "treatment_own_created_crops": 1,
        "phase": phase,
        "opponent": opponent,
    }


def test_threshold_gate_checks_phase_breadth_and_integrity():
    opponents = [f"o{index}" for index in range(8)]
    rows = [
        row(10 if index % 5 else 0, "early" if index % 2 else "late", opponents[index % 8])
        for index in range(400)
    ]
    report = threshold_gate(rows, True)
    assert report["gates"]["at_least_384_rows"]
    assert report["gates"]["early_mean_at_least_8"]
    assert report["gates"]["late_mean_at_least_4"]
    assert report["gates"]["opponent_breadth"]
    assert report["pass"]
    assert not threshold_gate(rows, False)["pass"]
