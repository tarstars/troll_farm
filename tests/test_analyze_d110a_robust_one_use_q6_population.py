from cgauto.analyze_d110a_robust_one_use_q6_population import (
    discovery_admission,
    held_value_gates,
    selected_population,
)
from cgauto.make_d110a_antithetic_q6_linear_population import population


def metrics():
    return {
        "mean_margin_delta": 2.5,
        "strict_improvement_rate": 0.45,
        "mean_own_score_delta": 1.0,
        "mean_opponent_score_delta": -1.5,
        "fold_mean_margin_delta": {"0": 2.0, "1": 3.0},
        "worst_family": -2.0,
        "positive_families": 6,
        "intervention_rate": 0.50,
        "crop_rate": 1.0,
        "worker_three_rate": 0.90,
    }


def test_discovery_and_held_gates_accept_robust_safe_policy():
    value = metrics()
    assert all(discovery_admission(value, 0.92).values())
    assert all(held_value_gates(value, 0.92).values())


def test_selected_population_moves_source_weights_to_first_pair():
    source = population()
    selected = selected_population(source, 17)
    assert selected[1]["parameters"] == source[1 + 2 * 17]["parameters"]
    assert selected[2]["parameters"] == selected[1]["parameters"]
    assert selected[1]["policy"] == "one_00"
    assert selected[2]["policy"] == "four_00"
