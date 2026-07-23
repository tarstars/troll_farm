from __future__ import annotations

from cgauto.d15_resident_residual_ppo_analysis import EVAL_START, EVAL_STOP, analyze_run
from cgauto.rl_resident_residual_env import OPPONENTS


def rows(delta: int, overrides: int) -> list[dict]:
    return [
        {
            "scenario": scenario,
            "map_seed": scenario // 12,
            "seat": (scenario // 6) % 2,
            "opponent": OPPONENTS[scenario % 6],
            "margin": 10 + delta,
            "wood_edge": 2 + delta,
            "overrides": overrides,
            "rejected_actions": 0,
        }
        for scenario in range(EVAL_START, EVAL_STOP)
    ]


def payload(delta: int, overrides: int) -> dict:
    return {
        "config": {
            "output_prefix": "fixture",
            "model_seed": 1,
            "keep_bias": 0.5,
            "parameter_count": 10,
            "total_transitions": 131_072,
        },
        "training_episodes": 20,
        "wall_seconds": 1,
        "logs": [{"global_step": 131_072}],
        "evaluation": {"rows": rows(delta, overrides)},
    }


def test_positive_paired_run_passes_signal_gate():
    baseline = {"rows": rows(0, 0)}
    result = analyze_run(payload(1, 1), baseline)

    assert result["signal_positive"] is True
    assert result["classification"] == "useful_signal"
    assert result["evaluation"]["map_margin_delta"]["mean"] == 1


def test_deterministic_keep_collapse_is_classified():
    baseline = {"rows": rows(0, 0)}
    result = analyze_run(payload(0, 0), baseline)

    assert result["signal_positive"] is False
    assert result["classification"] == "collapse_to_keep"
