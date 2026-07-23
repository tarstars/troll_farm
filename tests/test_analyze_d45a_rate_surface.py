from cgauto.analyze_d45a_rate_surface import PAIRS, gate_metrics


def row(mean: float, change: float = 0.2, safe: bool = True) -> dict:
    return {
        "mean_margin": mean,
        "changed_action_hash_rate": change,
        "worker_two_rate": 1.0 if safe else 0.0,
        "worker_three_rate": 1.0 if safe else 0.0,
        "crop_rate": 1.0 if safe else 0.0,
    }


def test_gate_metrics_counts_surface_properties() -> None:
    summaries = {"zero": row(10.0, 0.0)}
    for index, name in enumerate(PAIRS):
        summaries[f"{name}_plus"] = row(20.0 + index)
        summaries[f"{name}_minus"] = row(-10.0 - index)
    actual = gate_metrics(summaries)
    assert actual["perturbation_mean_range"] == 44.0
    assert actual["perturbations_above_zero"] == 8
    assert actual["perturbations_below_zero"] == 8
    assert len(actual["active_perturbations"]) == 16
    assert len(actual["safe_perturbations"]) == 16
    assert actual["directional_pairs_at_least_2"] == 8


def test_gate_metrics_excludes_zero_from_activation_and_safety() -> None:
    summaries = {"zero": row(0.0, 0.0)}
    for name in PAIRS:
        summaries[f"{name}_plus"] = row(1.0, 0.0, False)
        summaries[f"{name}_minus"] = row(-1.0, 1.0, False)
    actual = gate_metrics(summaries)
    assert actual["active_perturbations"] == []
    assert actual["safe_perturbations"] == []
