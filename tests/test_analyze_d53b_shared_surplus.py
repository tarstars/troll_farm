from cgauto.analyze_d53b_shared_surplus import oversubscription_gates


def test_exact_oversubscription_signature_passes():
    gates = oversubscription_gates(
        common_mismatches=0,
        partition_failures=0,
        budget_failures=168,
        failed_currency_picks=336,
        multi_pick_failures=168,
        oversubscribed_failures=168,
    )
    assert all(gates.values())


def test_any_unexplained_budget_failure_blocks_shared_ledger():
    gates = oversubscription_gates(
        common_mismatches=0,
        partition_failures=0,
        budget_failures=168,
        failed_currency_picks=335,
        multi_pick_failures=167,
        oversubscribed_failures=167,
    )
    assert not gates[
        "every_binding_budget_failure_has_multiple_currency_picks"
    ]
    assert not gates[
        "every_binding_budget_failure_oversubscribes_a_resource"
    ]


def test_zero_failures_cannot_vacuously_authorize_repair():
    gates = oversubscription_gates(
        common_mismatches=0,
        partition_failures=0,
        budget_failures=0,
        failed_currency_picks=0,
        multi_pick_failures=0,
        oversubscribed_failures=0,
    )
    assert not gates["binding_budget_failures_are_present"]
