from __future__ import annotations

import pytest

from cgauto.make_opponent_crop_candidate import (
    make_candidate,
    PARENT,
    RESIDENT_SLIM_SHA256,
)
from cgauto.make_opponent_crop_candidate import digest_text
from cgauto.slim_live_source import slim


def test_parent_still_rebuilds_exact_resident_before_candidateization() -> None:
    parent = PARENT.read_text()
    assert digest_text(slim(parent)) == RESIDENT_SLIM_SHA256


def test_candidate_contains_only_the_fixed_crop_treatment_and_fits() -> None:
    candidate = make_candidate(PARENT.read_text())
    assert len(candidate.encode()) < 100_000
    assert candidate.count("fn reconcile_opponent_crops(") == 1
    assert candidate.count("fn apply_opponent_crop_priority(") == 1
    assert candidate.count("if eta<=6{candidate.score+=100.0;}") == 1
    assert "opponent_crop_bonus" not in candidate
    assert "opponent_crop_eta_limit" not in candidate


def test_candidate_transform_refuses_parent_drift() -> None:
    with pytest.raises(ValueError, match="parent hash changed"):
        make_candidate(PARENT.read_text() + "\n")
