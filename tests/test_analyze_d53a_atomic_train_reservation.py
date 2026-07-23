from cgauto.analyze_d53a_atomic_train_reservation import (
    CONFIGS,
    MODELS,
    transaction_gates,
)


def target(attempts=10, successes=10, **overrides):
    values = {
        "attempts": attempts,
        "successes": successes,
        "fail_shack_only": 0,
        "fail_budget_only": 0,
        "fail_both": 0,
        "fail_other": 0,
        "failures": attempts - successes,
        "budget_inclusive": 0,
    }
    values.update(overrides)
    return values


def test_frozen_v4_catalog_crosses_the_same_eight_configs():
    assert len(MODELS) == 8
    assert len(set(MODELS)) == 8
    assert all(label.startswith("legend_v4_") for label in MODELS)
    assert {config["max_workers"] for config in CONFIGS.values()} == {3, 4}


def test_transaction_gates_accept_shack_only_failure():
    by_target = {
        "2": target(attempts=11, successes=10, fail_shack_only=1, failures=1),
        "3": target(),
        "4": target(),
    }
    assert all(transaction_gates(by_target, 0).values())


def test_transaction_gates_reject_one_budget_or_unexplained_failure():
    by_target = {str(level): target() for level in (2, 3, 4)}
    by_target["3"] = target(
        attempts=11,
        successes=10,
        fail_budget_only=1,
        failures=1,
        budget_inclusive=1,
    )
    gates = transaction_gates(by_target, 0)
    assert not gates["zero_budget_inclusive_train_failures"]
    assert not gates["target_three_four_failures_are_shack_only"]

    by_target = {str(level): target() for level in (2, 3, 4)}
    by_target["4"] = target(
        attempts=11,
        successes=10,
        fail_other=1,
        failures=1,
    )
    gates = transaction_gates(by_target, 0)
    assert not gates["zero_unexplained_train_failures"]
