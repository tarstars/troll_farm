from cgauto.h4_opponent_bill_deniability_census import (
    classify_command,
    contribution_bounds,
    harvest_gains,
    remaining_supply_caps,
    same_turn_harvest_reduction,
    source_minimum_bill_contribution,
    strict_block,
)


def test_fungible_bank_preserves_starting_external_intervals():
    bounds = contribution_bounds(
        starting=7,
        external_supply_upper=18,
        bank=18,
        cost=18,
    )
    assert bounds == {
        "starting_bank_min": 0,
        "starting_bank_max": 7,
        "external_bank_min": 11,
        "external_bank_max": 18,
        "starting_bill_min": 0,
        "starting_bill_max": 7,
        "external_bill_min": 11,
        "external_bill_max": 18,
    }


def test_individual_source_is_not_mandatory_when_other_supply_covers_bank():
    assert (
        source_minimum_bill_contribution(
            starting=7,
            total_external_supply=18,
            source_amount=3,
            bank=18,
            cost=18,
        )
        == 0
    )


def test_prior_train_payments_tighten_both_conservative_supply_caps():
    caps = remaining_supply_caps(
        starting=7,
        total_external_supply=18,
        prior_train_cost=9,
        external_supply_before_prior_train=5,
    )
    assert caps == {
        "minimum_starting_spent_on_prior_trains": 4,
        "minimum_external_spent_on_prior_trains": 2,
        "remaining_starting_stock_upper": 3,
        "remaining_external_supply_upper": 16,
    }


def test_individual_source_becomes_mandatory_at_tight_supply():
    assert (
        source_minimum_bill_contribution(
            starting=2,
            total_external_supply=6,
            source_amount=4,
            bank=8,
            cost=7,
        )
        == 3
    )


def test_strict_block_must_exceed_original_bank_slack():
    assert strict_block(required_source_units=2, removable_units=2, bank_slack=1)
    assert not strict_block(
        required_source_units=2, removable_units=1, bank_slack=1
    )
    assert not strict_block(
        required_source_units=1, removable_units=3, bank_slack=1
    )


def test_harvest_round_robin_matches_referee_shape():
    units = [
        {"id": 10, "hp": 2, "cc": 3, "carry_total": 0},
        {"id": 20, "hp": 1, "cc": 2, "carry_total": 0},
    ]
    assert harvest_gains(3, units) == {10: 2, 20: 1}


def test_seat_zero_insert_can_reduce_seat_one_harvest():
    actual = {
        0: [],
        1: [{"id": 20, "hp": 2, "cc": 2, "carry_total": 0}],
    }
    candidate = {"id": 10, "hp": 1, "cc": 1, "carry_total": 0}
    assert (
        same_turn_harvest_reduction(
            fruits=2,
            opponent_player=1,
            resident_player=0,
            actual_harvesters=actual,
            candidate=candidate,
        )
        == 1
    )


def test_displacement_classes_do_not_claim_value():
    assert classify_command("WAIT") == "idle"
    assert classify_command("MOVE 3 5 7") == "movement"
    assert classify_command("DROP 3") == "banking_logistics"
    assert classify_command("CHOP 3") == "suppression"
    assert classify_command("HARVEST 3") == "production"
