from cgauto.analyze_d107a_q6_bounded_online_controller_preflight import (
    analyze,
    choose_oracle,
    counter_violations,
)


def test_choose_oracle_uses_margin_then_lexical_policy():
    baseline = {"margin": "10"}
    rows = [
        {"policy": "four_02", "margin": "12"},
        {"policy": "four_01", "margin": "12"},
        {"policy": "four_00", "margin": "11"},
    ]
    label, row = choose_oracle(baseline, rows)
    assert label == "four_01"
    assert row["margin"] == "12"


def test_counter_reconciliation_accepts_exact_joint_and_single_counts():
    row = {
        "policy": "four_00", "kind": "four", "budget": "4", "map_seed": "1",
        "seat": "0", "opponent": "resident", "eligible_batches": "3",
        "intervention_batches": "2", "joint_batches": "1", "single_first_batches": "1",
        "single_second_batches": "0", "nonkeep_assignments": "3",
        "proposal_occurrences": "192", "unique_proposals": "40",
        "supporter_occurrences": "192", "concrete_fell": "1", "concrete_harvest": "1",
        "concrete_renew": "0", "concrete_mine": "1", "owner_natural": "1",
        "owner_own": "1", "owner_opponent": "0", "owner_ambiguous": "0",
    }
    assert counter_violations([row]) == []
    row["supporter_occurrences"] = "191"
    assert counter_violations([row])


def test_frozen_d107a_artifacts_pass_every_gate():
    result = analyze()
    assert result["integrity"]["pass"]
    assert result["activity"]["pass"]
    assert result["headroom"]["pass"]
    assert result["decision"] == "open_d108a_recurrent_masked_controller"
