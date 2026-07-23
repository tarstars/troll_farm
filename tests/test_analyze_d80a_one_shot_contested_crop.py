from cgauto.analyze_d80a_one_shot_contested_crop import (
    activation_metrics,
    paired_value_metrics,
    stage_a_gates,
    stage_b_gates,
    task_key,
)


def row(
    task: int,
    policy: str,
    margin: int,
    intervention: int,
    opponent: str = "opponent",
) -> dict[str, str]:
    return {
        "map_seed": str(task),
        "seat": str(task % 2),
        "opponent": opponent,
        "policy": policy,
        "margin": str(margin),
        "own_score": str(100 + margin),
        "opponent_score": "100",
        "own_workers": "3",
        "own_created_crops": "1",
        "action_hash": f"{policy}-{task}" if intervention else f"control-{task}",
        "interventions": str(intervention),
        "challenger_rank": "1" if intervention else "-1",
        "challenger_plane": "5" if intervention else "-1",
    }


def test_activation_metrics_counts_only_intervened_tasks() -> None:
    control_rows = [row(task, "control", 0, 0) for task in range(40)]
    candidate_rows = [
        row(task, "candidate", 5, int(task < 32)) for task in range(40)
    ]
    control = {task_key(item): item for item in control_rows}
    candidate = {task_key(item): item for item in candidate_rows}
    actual = activation_metrics(control, candidate)
    assert actual["intervention_tasks"] == 32
    assert actual["changed_action_hash_tasks"] == 32
    assert actual["changed_action_hash_rate"] == 0.8


def test_stage_a_gate_requires_integrity_locality_and_breadth() -> None:
    audit = {
        "complete_repeats": True,
        "mechanics_and_numeric_failures": 0,
        "intervention_accounting_failures": 0,
        "nonintervention_parity_failures": 0,
    }
    activation = {
        "intervention_tasks": 100,
        "changed_action_hash_tasks": 100,
        "changed_action_hash_rate": 100 / 256,
        "active_seats": [0, 1],
        "active_opponents": [str(index) for index in range(6)],
        "challenger_ranks": [1, 2],
        "challenger_planes": [5, 7],
    }
    assert all(stage_a_gates(audit, activation).values())
    activation["changed_action_hash_tasks"] = 99
    assert not stage_a_gates(audit, activation)["intervention_equals_changed_task_count"]


def test_paired_value_and_stage_b_gates_capture_positive_safe_effect() -> None:
    control_rows = []
    candidate_rows = []
    opponents = [f"o{index}" for index in range(8)]
    for task in range(32):
        opponent = opponents[task % 8]
        control_rows.append(row(task, "control", -10, 0, opponent))
        candidate_rows.append(row(task, "candidate", 0, 1, opponent))
    control = {task_key(item): item for item in control_rows}
    candidate = {task_key(item): item for item in candidate_rows}
    actual = paired_value_metrics(control, candidate)
    assert actual["active_mean_margin_delta"] == 10
    assert actual["overall_mean_margin_delta"] == 10
    assert actual["active_strict_improvement_rate"] == 1
    assert all(stage_b_gates(actual).values())
