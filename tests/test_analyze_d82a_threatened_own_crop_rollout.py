from cgauto.analyze_d82a_threatened_own_crop_rollout import (
    ARMS,
    oracle_gates,
    safe_oracle_metrics,
    support_gates,
    support_metrics,
    task_key,
)


def row(task: int, arm: str, available: int, margin: int, opponent: str) -> dict[str, str]:
    return {
        "map_seed": str(task),
        "seat": str(task % 2),
        "opponent": opponent,
        "arm": arm,
        "root_seen": "1",
        "arm_available": str(1 if arm == "control" else available),
        "arm_prior_rank": "0" if arm == "control" else ("2" if available else "-1"),
        "margin": str(margin),
        "own_score": str(100 + margin),
        "opponent_score": "100",
        "own_workers": "3",
        "own_created_crops": "1",
    }


def test_support_is_semantic_and_nonsealing() -> None:
    opponents = [f"o{index}" for index in range(8)]
    by_arm = {arm: {} for arm in ARMS}
    for task in range(128):
        for arm in ARMS:
            item = row(task, arm, 1, 0, opponents[task % 8])
            by_arm[arm][task_key(item)] = item
    actual = support_metrics(by_arm)
    assert actual["rooted_tasks"] == 128
    assert actual["availability_by_semantic_arm"] == {
        "fell": 128,
        "harvest": 128,
        "renew": 128,
    }
    assert all(support_gates(actual).values())


def test_safe_oracle_respects_tie_priority_and_value() -> None:
    opponents = [f"o{index}" for index in range(8)]
    by_arm = {arm: {} for arm in ARMS}
    for task in range(512):
        margins = {
            "control": 0,
            "fell": 9,
            "harvest": 12 if task % 2 == 0 else 8,
            "renew": 8 if task % 2 == 0 else 12,
        }
        for arm in ARMS:
            item = row(task, arm, 1, margins[arm], opponents[task % 8])
            by_arm[arm][task_key(item)] = item
    actual = safe_oracle_metrics(by_arm)
    assert actual["mean_margin_gain"] == 12
    assert actual["selected_arm_counts"] == {"harvest": 256, "renew": 256}
    assert all(oracle_gates(actual).values())
