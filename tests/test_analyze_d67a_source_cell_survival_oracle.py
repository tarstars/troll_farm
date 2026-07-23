"""Tests for D67a cell-survival success accounting."""

from __future__ import annotations

from cgauto.analyze_d67a_source_cell_survival_oracle import recompute_success


def row(**changes: str) -> dict[str, str]:
    result = {
        "pick_commands": "1",
        "plant_commands": "1",
        "harvest_commands": "2",
        "drop_commands": "1",
        "bank_delta": "1",
        "invalidated_delta": "0",
        "invalid_direct_delta": "0",
        "provenance_delta": "0",
        "deposit_prediction_delta": "0",
    }
    result.update(changes)
    return result


def test_success_requires_net_deposit_and_all_commands() -> None:
    assert recompute_success(row())
    assert not recompute_success(row(drop_commands="0"))
    assert not recompute_success(row(bank_delta="0"))
    assert not recompute_success(row(invalidated_delta="1"))
