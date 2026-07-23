from cgauto.analyze_d47a_activation import TASKS, activation_gates, activation_metrics


def row(seed: int, action_hash: str, eligible: int, overrides: int) -> dict[str, str]:
    return {
        "map_seed": str(seed),
        "seat": "0",
        "opponent": "resident",
        "action_hash": action_hash,
        "role_eligible": str(eligible),
        "role_overrides": str(overrides),
    }


def test_activation_metrics_counts_decisions_and_changed_tasks() -> None:
    candidate = [row(1, "same", 300, 100), row(2, "changed", 250, 170)]
    control = {
        (1, 0, "resident"): row(1, "same", 0, 0),
        (2, 0, "resident"): row(2, "control", 0, 0),
    }
    actual = activation_metrics(candidate, control)
    assert actual["role_eligible_decisions"] == 550
    assert actual["role_overrides"] == 270
    assert actual["changed_action_hash_tasks"] == 1
    assert actual["changed_action_hash_rate"] == 0.5


def test_activation_gates_apply_frozen_conjunction() -> None:
    metrics: dict[str, int | float] = {
        "tasks": TASKS,
        "role_eligible_decisions": 512,
        "role_overrides": 256,
        "changed_action_hash_tasks": 64,
        "changed_action_hash_rate": 0.25,
    }
    assert all(
        activation_gates(
            metrics, repeat_byte_identical=True, integrity_failures=0
        ).values()
    )
    metrics["role_overrides"] = 255
    assert not activation_gates(
        metrics, repeat_byte_identical=True, integrity_failures=0
    )["at_least_256_role_overrides"]
