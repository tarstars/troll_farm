from cgauto.train_d158a_group_robust_recurrent_q6_ppo import VARIANT_ORDER
from cgauto.analyze_d158a_group_robust_recurrent_q6_ppo import (
    confirmation_gates,
    select_candidate,
)


def candidate(variant, eligible, worst, mean, own, strict):
    return {
        "variant": variant,
        "eligible": eligible,
        "evaluation": {
            "summaries": {
                "final": {
                    "worst_family": worst,
                    "mean_margin_delta": mean,
                    "mean_own_score_delta": own,
                    "strict_improvement_rate": strict,
                }
            }
        },
    }


def test_d158_selection_uses_worst_family_before_mean():
    rows = [
        candidate(VARIANT_ORDER[0], True, -1, 5, 1, 0.5),
        candidate(VARIANT_ORDER[1], True, 0, 2, 0, 0.4),
        candidate(VARIANT_ORDER[2], False, 3, 8, 5, 0.8),
    ]
    assert select_candidate(rows)["variant"] == VARIANT_ORDER[1]


def test_d158_selection_stable_variant_order_breaks_full_tie():
    rows = [candidate(variant, True, 0, 2, 1, 0.4) for variant in VARIANT_ORDER]
    assert select_candidate(rows)["variant"] == VARIANT_ORDER[0]


def test_d158_confirmation_gate_accepts_qualified_metrics():
    base = {
        "tasks": 1024,
        "maximum_reward_identity_error": 0.0,
        "mechanical_failures": {
            "invalid_direct_commands": 0,
            "provenance_failures": 0,
            "deposit_prediction_failures": 0,
        },
        "crop_rate": 1.0,
        "worker_three_rate": 0.9,
    }
    summaries = {
        "control": {**base},
        "final": {
            **base,
            "mean_margin_delta": 2.0,
            "strict_improvement_rate": 0.4,
            "positive_families": 6,
            "worst_family": -3.0,
            "mean_own_score_delta": -1.0,
            "mean_opponent_score_delta": -2.0,
        },
    }
    gates = confirmation_gates(summaries, True)
    assert all(all(group.values()) for group in gates.values())

