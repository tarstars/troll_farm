import numpy as np

from cgauto.train_d125a_fit_activity_calibrated_q6 import (
    activity_calibrated_offset,
    policy_evaluation_mechanics,
    validation_gates,
)


def test_activity_calibration_uses_task_maxima_and_forced_control_tasks():
    tasks = [(index, 0, "x") for index in range(5)]
    roots = [
        (tasks[0], 0),
        (tasks[0], 1),
        (tasks[1], 0),
        (tasks[2], 0),
        (tasks[3], 0),
    ]
    values = np.asarray([0.0, 4.0, 3.0, 2.0, 1.0], dtype=np.float32)
    offset, summary = activity_calibrated_offset(
        tasks, roots, values, target_activity=0.4
    )
    assert offset == 2.5
    assert summary["target_active_tasks"] == 2
    assert summary["achieved_active_tasks"] == 2


def test_policy_mechanics_treats_density_as_informational():
    mechanics = {
        "gates": {
            "supported_tasks_at_least_90pct": False,
            "at_least_600_roots": False,
            "at_least_6000_arms": False,
            "zero_mechanical_failures": True,
        },
        "details": {"tasks": 256},
    }
    result = policy_evaluation_mechanics(mechanics)
    assert result["pass"]
    assert not any(result["informational"].values())


def test_validation_gates_use_relative_crop_and_fold_safety():
    metrics = {
        "mean_margin_delta": 2.0,
        "strict_improvement_rate": 0.40,
        "worst_family": -3.0,
        "positive_families": 6,
        "mean_own_score_delta": 0.0,
        "mean_opponent_score_delta": 1.0,
        "intervention_rate": 0.85,
        "crop_rate": 0.99,
        "worker_three_rate": 0.85,
        "control_worker_three_rate": 0.90,
        "fold_mean_margin_delta": {"0": 0.0, "1": 0.1},
    }
    assert all(validation_gates(metrics, 0.99).values())
    metrics["fold_mean_margin_delta"]["1"] = -0.1
    assert not validation_gates(metrics, 0.99)["both_folds_nonnegative"]
