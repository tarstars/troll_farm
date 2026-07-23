from cgauto.analyze_d49a_activation import TASKS, activation_gates, activation_metrics


def row(seed: int, action_hash: str, eligible: int, promotions: int) -> dict[str, str]:
    return {
        "map_seed": str(seed),
        "seat": "0",
        "opponent": "resident",
        "action_hash": action_hash,
        "order_eligible": str(eligible),
        "order_promotions": str(promotions),
    }


def test_activation_metrics_counts_suffixes_promotions_and_changes() -> None:
    candidate = [row(1, "same", 200, 80), row(2, "changed", 100, 60)]
    control = {
        (1, 0, "resident"): row(1, "same", 0, 0),
        (2, 0, "resident"): row(2, "control", 0, 0),
    }
    actual = activation_metrics(candidate, control)
    assert actual["order_eligible_suffixes"] == 300
    assert actual["order_promotions"] == 140
    assert actual["changed_action_hash_tasks"] == 1
    assert actual["changed_action_hash_rate"] == 0.5


def test_activation_gates_apply_frozen_thresholds() -> None:
    metrics: dict[str, int | float] = {
        "tasks": TASKS,
        "order_eligible_suffixes": 256,
        "order_promotions": 128,
        "changed_action_hash_tasks": 64,
        "changed_action_hash_rate": 0.25,
    }
    assert all(
        activation_gates(
            metrics, repeat_byte_identical=True, integrity_failures=0
        ).values()
    )
    metrics["order_promotions"] = 127
    assert not activation_gates(
        metrics, repeat_byte_identical=True, integrity_failures=0
    )["at_least_128_order_promotions"]
