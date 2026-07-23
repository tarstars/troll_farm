from cgauto.analyze_d46a_activation import TASKS, activation_gates, activation_metrics


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
    assert actual == {
        "tasks": 2,
        "role_eligible_decisions": 550,
        "role_overrides": 270,
        "changed_action_hash_tasks": 1,
        "changed_action_hash_rate": 0.5,
    }


def test_activation_gates_accept_frozen_thresholds_inclusively() -> None:
    metrics: dict[str, int | float] = {
        "tasks": TASKS,
        "role_eligible_decisions": 512,
        "role_overrides": 256,
        "changed_action_hash_tasks": 0,
        "changed_action_hash_rate": 0.20,
    }
    assert all(
        activation_gates(
            metrics, repeat_byte_identical=True, integrity_failures=0
        ).values()
    )
    metrics["changed_action_hash_rate"] = 0.90
    assert all(
        activation_gates(
            metrics, repeat_byte_identical=True, integrity_failures=0
        ).values()
    )


def test_activation_gates_reject_each_mechanical_failure() -> None:
    metrics: dict[str, int | float] = {
        "tasks": TASKS - 1,
        "role_eligible_decisions": 511,
        "role_overrides": 255,
        "changed_action_hash_tasks": 0,
        "changed_action_hash_rate": 0.91,
    }
    gates = activation_gates(
        metrics, repeat_byte_identical=False, integrity_failures=1
    )
    assert gates and not any(gates.values())
