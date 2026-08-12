"""Tests for the mechanical idle-harvest diagnostic transform.

Owner ruling 2026-08-11 (B7/2a): the seal asserting that ``instrument()`` attaches
to the CURRENT live source was retired. The live file was replaced on 2026-07-29 by
the platform recovery and no longer contains the probe's anchors, so ``instrument()``
now correctly refuses it (the refuse-drift test below covers that behavior). The
minified-source seal still binds: ``instrument_minified`` remains load-bearing for
cgauto/secure_orchard_conversion_{replication,audit}.py against the frozen
submission copy, which still carries the anchors.
"""

from pathlib import Path

import pytest

from cgauto.make_idle_harvest_probe import instrument, instrument_minified

REPO = Path(__file__).resolve().parent.parent
LIVE_MIN = REPO / "cgauto" / "submissions" / "agent-6553250-yamo-orchard-live.min.rs"


def test_probe_refuses_source_drift() -> None:
    with pytest.raises(RuntimeError, match="instrumentation anchor"):
        instrument("fn main() {}")


def test_minified_probe_stays_under_submission_size_and_keeps_live_policy() -> None:
    probed = instrument_minified(LIVE_MIN.read_text())

    assert len(probed.encode()) < 100_000
    assert probed.count("@IH_CAND") == 1
    assert probed.count("@IH_SELECT") == 1
    assert probed.count("@IH_ORCHARD_FORCE") == 1
    assert "YamoBot::tuned_carry_regeneration_transit_idle_harvest()" in probed
