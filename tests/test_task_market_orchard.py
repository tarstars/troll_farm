from cgauto.task_market_orchard import (
    inactive_identity,
    lower_quantile,
    orchard_timing_integrity,
    worst_fraction_mean,
)


def orchard_row(**overrides):
    row = {
        "seed": 1,
        "seat": 0,
        "opponent": "gold_adaptive",
        "orchard_activation_turn": 20,
        "orchard_seed_repaid_turn": 40,
        "orchard_market_turns": 50,
        "orchard_offers": 8,
        "orchard_selections": 3,
        "orchard_harvest_selections": 1,
        "orchard_first_selection_turn": 45,
        "orchard_forced_setup_actions": 21,
    }
    row.update(overrides)
    return row


def test_orchard_timing_accepts_ordered_market_telemetry():
    assert orchard_timing_integrity([orchard_row()])["passed"]


def test_orchard_timing_rejects_offer_before_repayment():
    result = orchard_timing_integrity(
        [
            orchard_row(
                orchard_activation_turn=-1,
                orchard_seed_repaid_turn=-1,
                orchard_market_turns=0,
                orchard_offers=1,
                orchard_selections=0,
                orchard_harvest_selections=0,
                orchard_first_selection_turn=-1,
                orchard_forced_setup_actions=0,
            )
        ]
    )
    assert not result["passed"]
    assert result["violations"][0][1] == "offer_before_repayment"


def test_lower_tail_helpers_use_frozen_lower_order_statistics():
    values = list(range(-20, 80))
    assert lower_quantile(values, 0.10) == -11
    assert worst_fraction_mean(values, 0.05) == -18


def test_inactive_identity_requires_exact_outcomes():
    fields = {
        "own_score": 10,
        "opponent_score": 8,
        "margin": 2,
        "own_inventory_wood": 2,
        "opponent_inventory_wood": 1,
        "workers": 2,
        "terminal_turn": 100,
        "own_successful_plants": 0,
        "opponent_successful_plants": 0,
        "ambiguous_births": 0,
        "total_chop_wood": 3,
        "assigned_chop_wood": 3,
        "own_from_natural": 3,
        "own_from_ours": 0,
        "own_from_opponent": 0,
        "own_from_unknown": 0,
        "opponent_from_natural": 0,
        "opponent_from_ours": 0,
        "opponent_from_opponent": 0,
        "opponent_from_unknown": 0,
        "terminal_plants": 4,
        "terminal_banana_plants": 0,
    }
    candidate = orchard_row(orchard_seed_repaid_turn=-1, **fields)
    resident = dict(candidate)
    pair = {"identity": (1, 0, "gold_adaptive"), "candidate": candidate, "resident": resident}
    assert inactive_identity([pair])["passed"]
    candidate["own_score"] += 1
    assert not inactive_identity([pair])["passed"]

