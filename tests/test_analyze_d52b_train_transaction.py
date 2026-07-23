from cgauto.analyze_d52b_train_transaction import (
    partition_exact,
    repair_decision,
    target_summary,
)


def values(**overrides):
    base = {
        "attempts": 100,
        "successes": 20,
        "fail_shack_only": 40,
        "fail_budget_only": 20,
        "fail_both": 10,
        "fail_other": 10,
    }
    base.update(overrides)
    return base


def test_partition_is_mutually_exclusive_and_complete():
    assert partition_exact(values())
    assert not partition_exact(values(fail_other=9))


def test_union_rule_opens_combined_atomic_repair_at_exact_boundary():
    pooled = target_summary(
        values(
            successes=0,
            fail_shack_only=40,
            fail_budget_only=40,
            fail_both=0,
            fail_other=20,
        )
    )
    assert pooled["explained_union_failure_rate"] == 0.8
    assert repair_decision(pooled) == (
        "require atomic spawn evacuation and exact bill reservation"
    )


def test_more_than_twenty_percent_unexplained_requires_trace():
    pooled = target_summary(
        values(
            successes=0,
            fail_shack_only=79,
            fail_budget_only=0,
            fail_both=0,
            fail_other=21,
        )
    )
    assert repair_decision(pooled) == "freeze a turn-level trace before scheduler repair"


def test_single_cause_threshold_selects_narrow_atomic_invariant():
    pooled = target_summary(
        values(
            successes=0,
            fail_shack_only=80,
            fail_budget_only=0,
            fail_both=0,
            fail_other=20,
        )
    )
    assert repair_decision(pooled) == "require atomic spawn evacuation"
