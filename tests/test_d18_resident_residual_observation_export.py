from __future__ import annotations

import pytest

from cgauto.d18_resident_residual_observation_export import validate_contiguous


def rows(start: int = 120, scenarios: int = 3, samples: int = 2) -> list[dict]:
    return [
        {
            "scenario": scenario,
            "sample_slot": slot,
            "candidate_index": slot,
            "candidate_count": 100,
            "x": 1,
            "y": 2,
            "legal_actions": 3,
            "alternative_action": 100,
            "alternative_plane": 1,
        }
        for scenario in range(start, start + scenarios)
        for slot in range(samples)
    ]


def test_contiguous_block_schema() -> None:
    assert validate_contiguous(rows()) == (120, 123, 2)


def test_noncontiguous_scenarios_are_rejected() -> None:
    data = rows()
    data = [row for row in data if row["scenario"] != 121]
    with pytest.raises(ValueError, match="contiguous"):
        validate_contiguous(data)


def test_incomplete_sample_slots_are_rejected() -> None:
    data = rows()
    data[-1]["sample_slot"] = 0
    with pytest.raises(ValueError, match="sample slots"):
        validate_contiguous(data)
