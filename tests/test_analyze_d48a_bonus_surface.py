from cgauto.analyze_d48a_bonus_surface import COORDINATES, surface_metrics


def row(mean: float, change: float = 0.2, safe: bool = True) -> dict:
    return {
        "mean_margin": mean,
        "changed_action_hash_rate": change,
        "worker_two_rate": 1.0 if safe else 0.0,
        "worker_three_rate": 1.0 if safe else 0.0,
        "crop_rate": 1.0 if safe else 0.0,
    }


def test_surface_metrics_counts_coordinate_activation_and_direction() -> None:
    summaries = {"anchor": row(10.0, 0.0)}
    for index, coordinate in enumerate(COORDINATES):
        summaries[f"{coordinate}_zero"] = row(-10.0 - index)
        summaries[f"{coordinate}_double"] = row(20.0 + index)
    actual = surface_metrics(summaries)
    assert actual["perturbation_mean_range"] == 34.0
    assert actual["perturbations_above_anchor"] == 3
    assert actual["perturbations_below_anchor"] == 3
    assert len(actual["active_perturbations"]) == 6
    assert all(actual["coordinate_activation"].values())
    assert actual["directional_pairs_at_least_2"] == 3


def test_surface_metrics_requires_per_coordinate_activation() -> None:
    summaries = {"anchor": row(0.0, 0.0)}
    for coordinate in COORDINATES:
        summaries[f"{coordinate}_zero"] = row(-1.0)
        summaries[f"{coordinate}_double"] = row(1.0)
    summaries["bank_zero"] = row(-1.0, 0.0)
    summaries["bank_double"] = row(1.0, 1.0)
    actual = surface_metrics(summaries)
    assert not actual["coordinate_activation"]["bank"]
    assert actual["coordinate_activation"]["provenance"]
    assert actual["coordinate_activation"]["renew"]
