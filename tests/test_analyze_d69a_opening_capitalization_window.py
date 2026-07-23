"""Tests for D69a's frozen phase-order audit."""

from __future__ import annotations

from cgauto.analyze_d69a_opening_capitalization_window import (
    phase_gate,
    phase_metrics,
    reconstruct_generations,
)


def unit(unit_id: int, player: int, carry: list[int] | None = None) -> dict:
    return {
        "id": unit_id,
        "player": player,
        "x": 0,
        "y": 0,
        "ms": 1,
        "cc": 2,
        "hp": 1,
        "chop": 1,
        "carry": list(carry or [0, 0, 0, 0, 0, 0]),
    }


def state(plants: list[dict], carry0: list[int] | None = None) -> dict:
    return {
        "plants": plants,
        "units": [unit(0, 0, carry0), unit(1, 1)],
        "inventories": [[0] * 6, [0] * 6],
    }


def plant(kind: str = "PLUM") -> dict:
    return {"x": 0, "y": 0, "type": kind, "fruits": 1, "health": 10, "size": 1}


def test_generation_reconstruction_requires_sole_creator_and_tracks_receipt() -> None:
    states = [
        state([]),
        state([plant()]),
        state([plant()], [1, 0, 0, 0, 0, 0]),
        state([]),
    ]
    trajectory = [
        {"commands0": "PLANT 0 PLUM", "commands1": "WAIT"},
        {"commands0": "HARVEST 0", "commands1": "WAIT"},
        {"commands0": "WAIT", "commands1": "CHOP 1"},
    ]

    records, integrity = reconstruct_generations(states, trajectory)
    metrics = phase_metrics(records, player=0, third_worker_turn=4, turns=3)

    assert integrity["births_without_matching_command"] == 0
    assert records[0]["creators"] == [0]
    assert records[0]["death_turn"] == 3
    assert metrics["first_owned_crop_turn"] == 1
    assert metrics["first_renewable_receipt_turn"] == 2
    assert metrics["own_renewable_units_harvested"] == 1
    assert metrics["opponent_destroyed_owned_generations"] == 1
    assert metrics["renewable_flow_net"] == 0


def test_same_turn_birth_after_receipt_does_not_count_as_reinvestment() -> None:
    records = [
        {
            "birth_turn": 2,
            "death_turn": None,
            "creators": [0],
            "contacts": [
                {
                    "turn": 5,
                    "player": 0,
                    "verb": "HARVEST",
                    "fruit_gained": 1,
                    "wood_gained": 0,
                }
            ],
        },
        {"birth_turn": 5, "death_turn": None, "creators": [0], "contacts": []},
        {"birth_turn": 6, "death_turn": None, "creators": [0], "contacts": []},
    ]

    metrics = phase_metrics(records, player=0, third_worker_turn=7, turns=10)

    assert metrics["first_renewable_receipt_turn"] == 5
    assert metrics["first_reinvestment_turn"] == 6
    assert metrics["reinvestment_before_third"] is True
    assert metrics["live_owned_generations_at_third"] == 3


def fixture_row(**changes) -> dict:
    row = {
        "agent_id": 1,
        "owned_crop_before_third": True,
        "renewable_receipt_before_third": True,
        "reinvestment_before_third": True,
        "live_owned_generations_at_third": 2,
        "third_worker_turn": 120,
        "owned_crop_by_100": True,
        "renewable_receipt_by_100": True,
        "reinvestment_by_100": True,
        "first_owned_crop_turn": 20,
        "first_renewable_receipt_turn": 50,
        "first_reinvestment_turn": 60,
        "first_opponent_contact_turn": None,
        "owned_seeds_invested": 2,
        "own_renewable_units_harvested": 3,
        "owned_generations_destroyed": 0,
        "opponent_destroyed_owned_generations": 0,
        "renewable_flow_net": 1,
    }
    row.update(changes)
    return row


def test_phase_gate_is_required_in_both_agent_partitions() -> None:
    later = {
        "discovery": [fixture_row() for _ in range(10)],
        "validation": [fixture_row() for _ in range(10)],
    }
    non_scaler = {
        "discovery": [fixture_row() for _ in range(10)],
        "validation": [fixture_row() for _ in range(10)],
    }
    assert phase_gate(later, non_scaler)["pass"]

    later["validation"] = [
        fixture_row(reinvestment_before_third=index < 4) for index in range(10)
    ]
    gate = phase_gate(later, non_scaler)
    assert not gate["pass"]
    assert not gate["partitions"]["validation"]["checks"][
        "later_scaler_reinvestment_before_third_at_least_0_50"
    ]
