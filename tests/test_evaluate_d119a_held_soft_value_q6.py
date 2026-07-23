from cgauto.evaluate_d119a_held_soft_value_q6 import held_admission


def passing_metrics():
    return {
        "mean_margin_delta": 2.0,
        "strict_improvement_rate": 0.40,
        "worst_family": -3.0,
        "positive_families": 6,
        "mean_own_score_delta": 0.0,
        "mean_opponent_score_delta": 1.0,
        "intervention_rate": 0.10,
        "crop_rate": 1.0,
        "worker_three_rate": 0.85,
        "control_worker_three_rate": 0.90,
    }


def test_held_admission_accepts_exact_boundaries():
    assert all(held_admission(passing_metrics()).values())


def test_held_admission_rejects_each_failed_boundary():
    failures = {
        "mean_margin_delta": 1.999,
        "strict_improvement_rate": 0.399,
        "worst_family": -3.001,
        "positive_families": 5,
        "intervention_rate": 0.851,
        "crop_rate": 0.999,
        "worker_three_rate": 0.849,
    }
    for field, value in failures.items():
        metrics = passing_metrics()
        metrics[field] = value
        assert not all(held_admission(metrics).values()), field

    directional = passing_metrics()
    directional["mean_own_score_delta"] = -0.001
    directional["mean_opponent_score_delta"] = 0.001
    assert not all(held_admission(directional).values())
