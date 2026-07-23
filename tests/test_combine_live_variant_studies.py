"""Tests for disjoint live-variant study combination."""

import pytest

from cgauto.combine_live_variant_studies import combine


def payload(seed: int, margin: float) -> dict:
    return {
        "sources": {"baseline": "base", "candidate": "candidate"},
        "seed_start": seed,
        "seeds": 1,
        "rows": [
            {
                "seed": seed,
                "candidate_paired_margin": margin,
                "candidate_wood_delta": 0,
                "command_delta": {},
            }
        ],
    }


def test_combine_sorts_rows_and_recomputes_aggregate() -> None:
    result = combine([payload(1, -2), payload(0, 4)])

    assert [row["seed"] for row in result["rows"]] == [0, 1]
    assert result["aggregate"]["candidate_mean_paired_margin"] == 1


def test_combine_rejects_overlapping_seeds() -> None:
    with pytest.raises(ValueError, match="overlap"):
        combine([payload(0, 1), payload(0, 2)])
