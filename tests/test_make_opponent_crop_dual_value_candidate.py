import pytest

from cgauto.make_opponent_crop_candidate import PARENT, RESIDENT_SLIM_SHA256, digest_text
from cgauto.make_opponent_crop_dual_value_candidate import make_candidate
from cgauto.slim_live_source import slim


def test_parent_still_rebuilds_exact_resident() -> None:
    assert digest_text(slim(PARENT.read_text())) == RESIDENT_SLIM_SHA256


def test_dual_value_candidate_contains_only_fixed_value_rule() -> None:
    candidate = make_candidate(PARENT.read_text())
    assert "candidate.score+=candidate.score" in candidate
    assert "candidate.score+=100.0" not in candidate
    assert "eta<=6" in candidate
    assert len(candidate.encode()) < 100_000


def test_generator_fails_closed_on_parent_drift() -> None:
    with pytest.raises(ValueError, match="full parent hash changed"):
        make_candidate(PARENT.read_text() + "\n")

