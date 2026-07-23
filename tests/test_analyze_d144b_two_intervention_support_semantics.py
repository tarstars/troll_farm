from cgauto.analyze_d144b_two_intervention_support_semantics import (
    repaired_support_mechanics,
)


def _baseline(seat, boundaries):
    return {
        "map_seed": "1",
        "seat": str(seat),
        "opponent": "resident",
        "boundary_count": str(boundaries),
        "own_score": "10",
        "opponent_score": "5",
        "margin": "5",
        "own_workers": "3",
        "successful_trains": "2",
        "own_created_crops": "1",
        "invalid_direct_commands": "0",
        "provenance_failures": "0",
        "deposit_prediction_failures": "0",
        "action_hash": "7",
        "state_hash": "8",
    }


def _original():
    return {
        "infrastructure": {"pass": True},
        "mechanics": {
            "exact_one_use": {"pass": True},
            "mc": {
                "gates": {
                    "complete_unique_episode_grid": True,
                    "at_least_40pct_double_episodes_reach_two_interventions": True,
                    "at_least_95pct_tasks_have_sampled_two_interventions": False,
                }
            },
        },
    }


def test_support_repair_requires_two_use_for_every_eligible_task():
    baselines = [_baseline(0, 2), _baseline(1, 0)]
    rows = [
        {
            **baselines[0],
            "mode": "double",
            "intervention_batches": "2",
            "margin_delta": "4",
            "task_index": "0",
        },
        {
            **baselines[1],
            "mode": "double",
            "intervention_batches": "0",
            "margin_delta": "0",
            "task_index": "1",
        },
    ]
    result = repaired_support_mechanics(_original(), rows, baselines)
    assert result["details"]["supported_tasks"] == 1
    assert result["details"]["tasks"] == 2
    assert result["details"]["supported_task_two_use_coverage"] == 1.0
    assert not result["gates"]["baseline_grid_is_complete"]


def test_support_repair_rejects_action_on_zero_boundary_task():
    baselines = [_baseline(index, 0) for index in range(128)]
    rows = []
    for index, baseline in enumerate(baselines):
        rows.append(
            {
                **baseline,
                "mode": "double",
                "intervention_batches": "0",
                "margin_delta": "0",
                "task_index": str(index),
            }
        )
    result = repaired_support_mechanics(_original(), rows, baselines)
    assert result["gates"]["unsupported_tasks_are_exact_forced_control"]
    rows[0]["intervention_batches"] = "1"
    assert not repaired_support_mechanics(_original(), rows, baselines)["gates"][
        "unsupported_tasks_are_exact_forced_control"
    ]
