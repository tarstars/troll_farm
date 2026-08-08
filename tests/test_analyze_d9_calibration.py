"""Tests for the D-9 calibration analysis (Phase 1, gate measurement repair).

The analysis decomposes D-9 episodes by clause over the parent-vs-parent floor
self-test. Its load-bearing claim is that D-9's `banana_before_train` proxy does
not measure TRAIN displacement, so the tests pin the arithmetic that claim rests
on and the invariant that makes the run interpretable.
"""
from __future__ import annotations

import json
import pathlib

import pytest

from cgauto import analyze_d9_calibration as d9

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
FLOOR = (REPO_ROOT / "local_claude_1" / "verification"
         / "local_claude_1-floor-selftest-result-2026-08-07.json")

# Clauses that compare candidate against parent, i.e. that actually observe
# displacement. `banana_before_train` is the unpaired proxy under test.
PAIRED_CLAUSES = {"train_late", "train_missing", "train_stats_differ"}


@pytest.fixture(scope="module")
def report():
    return d9.build_report(FLOOR)


@pytest.fixture(scope="module")
def floor_games():
    return json.loads(FLOOR.read_text(encoding="utf-8"))["games"]


def test_floor_run_is_parent_against_itself(report):
    # Displacement is zero by construction only if candidate == parent.
    assert report["is_parent_vs_parent"] is True
    assert report["games"] == 240


def test_every_d9_episode_is_the_unpaired_proxy(report):
    assert report["episodes_by_clause"] == {"banana_before_train": 196}
    assert report["affected_games"] == 74


def test_no_paired_displacement_clause_ever_fires(report):
    for clause in PAIRED_CLAUSES:
        assert report["episodes_by_clause"].get(clause, 0) == 0


def test_proxy_episodes_are_paired_pick_and_plant(report):
    # The resident's own shack-ring orchard: PICK a banana, PLANT it. A 1:1
    # split is the signature of designed behaviour, not of a defect.
    assert report["verbs"] == {"PICK": 98, "PLANT": 98}


def test_verdict_is_that_the_proxy_does_not_measure_displacement(report):
    assert report["verdict"] == "MISCALIBRATED_RETIRE_OR_REPAIR"
    assert report["measured_displacement_episodes"] == 0
    assert report["proxy_episodes"] == 196


def test_d9_is_the_dominant_floor_blocker(report):
    assert report["detector_totals"]["D-9"]["games"] == 74
    assert report["blocking_games"] == 118
    # 55, not 46: a game still blocks without D-9 if it carries any non-D-9
    # violation, INCLUDING detector-less P-tier ones (the floor has 30 P4 and
    # 4 P2). Counting only `detector_counts` undercounts. claude_1 caught this.
    assert report["blocking_games_without_d9"] == 55


def test_p_tier_violations_without_a_detector_are_counted(report, floor_games):
    # The regression guard for the 46-vs-55 error: these exist and must count.
    detectorless = [
        v for g in floor_games for v in (g.get("violations") or [])
        if v.get("detector") is None
    ]
    assert len(detectorless) == 34
    assert {v.get("property") for v in detectorless} == {"P4", "P2"}


def test_detectors_with_zero_evidence_are_reported_as_unproven(report):
    # "Never PASS on zero evidence": a detector that has never fired is
    # unproven, not passing.
    assert set(report["unproven_detectors"]) == {"D-2", "D-3", "D-7", "D-8"}


def test_report_is_pinned_to_its_input(report):
    assert report["source_sha256"] == d9.sha256_of(FLOOR)
    assert len(report["source_sha256"]) == 64
