from cgauto.analyze_d81a_contested_action_set_rollout import (
    ARMS,
    oracle_gates,
    safe_oracle_metrics,
    support_gates,
    support_metrics,
    task_key,
)


def row(task: int, arm: str, available: int, margin: int, opponent: str) -> dict[str, str]:
    rank = ARMS.index(arm)
    return {
        "map_seed": str(task),
        "seat": str(task % 2),
        "opponent": opponent,
        "arm": arm,
        "root_seen": "1",
        "arm_available": str(1 if arm == "control" else available),
        "arm_action_plane": "5" if arm != "control" and available else "3",
        "arm_rank": str(rank),
        "interventions": str(int(arm != "control" and available)),
        "margin": str(margin),
        "own_score": str(100 + margin),
        "opponent_score": "100",
        "own_workers": "3",
        "own_created_crops": "1",
    }


def test_support_metrics_count_available_rank_arms() -> None:
    opponents = [f"o{index}" for index in range(8)]
    by_arm = {arm: {} for arm in ARMS}
    for task in range(80):
        opponent = opponents[task % 8]
        for arm in ARMS:
            item = row(task, arm, 1, 0, opponent)
            by_arm[arm][task_key(item)] = item
    actual = support_metrics(by_arm)
    assert actual["rooted_tasks"] == 80
    assert actual["available_noncontrol_arms"] == 240
    assert actual["availability_by_rank"] == {"rank_1": 80, "rank_2": 80, "rank_3": 80}


def test_support_gate_conjunction() -> None:
    audit = {
        "complete_repeats": True,
        "mechanics_and_numeric_failures": 0,
        "root_identity_failures": 0,
        "arm_accounting_failures": 0,
        "unavailable_parity_failures": 0,
        "available_hash_failures": 0,
    }
    support = {
        "rooted_tasks": 224,
        "available_noncontrol_arms": 400,
        "availability_by_rank": {"rank_1": 64, "rank_2": 64, "rank_3": 64},
        "available_seats": [0, 1],
        "available_opponents": [f"o{index}" for index in range(8)],
        "available_action_planes": [5, 7],
    }
    assert all(support_gates(audit, support).values())


def test_safe_oracle_selects_profitable_safe_ranks() -> None:
    opponents = [f"o{index}" for index in range(8)]
    by_arm = {arm: {} for arm in ARMS}
    for task in range(32):
        opponent = opponents[task % 8]
        margins = {"control": 0, "rank_1": 20, "rank_2": 15, "rank_3": 10}
        for arm in ARMS:
            item = row(task, arm, 1, margins[arm], opponent)
            by_arm[arm][task_key(item)] = item
    actual = safe_oracle_metrics(by_arm)
    assert actual["mean_margin_gain"] == 20
    assert actual["rooted_strict_improvement_rate"] == 1
    assert actual["selected_arm_counts"] == {"rank_1": 32}
    assert not oracle_gates(actual)["two_strict_noncontrol_ranks_selected_at_least_8"]
