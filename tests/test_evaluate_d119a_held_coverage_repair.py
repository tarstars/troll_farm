from cgauto.evaluate_d119a_held_coverage_repair import (
    MAX_BLOCKS,
    coverage_only_failure,
    repair_decision,
)


def mechanics(*, coverage: bool, other: bool = True):
    return {
        "pass": coverage and other,
        "gates": {
            "supported_tasks_at_least_90pct": coverage,
            "zero_mechanical_failures": other,
        },
    }


def test_only_coverage_failure_can_open_next_block():
    failed = mechanics(coverage=False)
    assert coverage_only_failure(failed)
    assert repair_decision(failed, None, 1) == "collect_next_frozen_coverage_block_only"
    assert repair_decision(failed, None, MAX_BLOCKS) == (
        "close_after_exhausting_frozen_coverage_repair"
    )
    noncoverage = mechanics(coverage=True, other=False)
    assert not coverage_only_failure(noncoverage)
    assert repair_decision(noncoverage, None, 1) == (
        "close_on_noncoverage_mechanics_failure"
    )


def test_policy_is_terminal_once_mechanics_passes():
    passed = mechanics(coverage=True)
    assert repair_decision(passed, True, 1) == (
        "open_quantized_rust_parity_and_final_untouched_confirmation"
    )
    assert repair_decision(passed, False, 1) == "close_without_tuning_on_held"
