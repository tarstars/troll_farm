"""Tests for D64i frozen blocker classification."""

from __future__ import annotations

from cgauto.analyze_d64i_worker_two_tail import classify, vector


def trace(bank: int, carry: int, ripe: int, shack: int = 1) -> list[dict[str, str]]:
    return [
        {
            "bank_deficit_total": str(bank),
            "bank_carry_deficit_total": str(carry),
            "bank_carry_ripe_deficit_total": str(ripe),
            "shack_occupied": str(shack),
        }
    ]


def test_frozen_classification_precedence() -> None:
    assert classify(trace(0, 0, 0, shack=0)) == "transaction_or_shack"
    assert classify(trace(2, 0, 0)) == "deposit_materialization"
    assert classify(trace(2, 1, 0)) == "ripe_acquisition"
    assert classify(trace(2, 1, 1)) == "source_availability"


def test_vector_requires_six_coordinates() -> None:
    assert vector("1,2,3,4,5,6") == [1, 2, 3, 4, 5, 6]

