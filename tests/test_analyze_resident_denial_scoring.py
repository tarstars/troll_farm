"""Tests for the resident denial-scoring audit (2026-08-07).

The audit reimplements a slice of `rust/src/bin/yamo_orchard_live.rs` scoring in
Python so the denial bonus can be compared against the base wood-per-turn score
across worker classes. The danger is drift: a Python model that quietly stops
matching the Rust it claims to describe. The first test therefore re-reads the
constants out of the byte-sacred source itself and fails if they move.
"""
from __future__ import annotations

import pathlib

from cgauto import analyze_resident_denial_scoring as audit

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "rust" / "src" / "bin" / "yamo_orchard_live.rs"
SOURCE_SHA256 = "fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f"


def test_model_constants_still_match_the_rust_source():
    found = audit.source_constants(SOURCE)

    assert found["source_sha256"] == SOURCE_SHA256
    assert found["denial_bonus_numerator"] == 900.0
    assert found["base_score_numerator"] == 1000.0
    assert found["denial_gate_max_opponent_trolls"] == 2
    assert found["plum_lemon_health_base"] == 4
    assert found["plum_lemon_health_slope"] == 2


def test_plum_lemon_health_matches_published_replay_observations():
    # docs/mechanics.md: PLUM s1-4 = 6,8,10,12 (10/10 real-replay observations).
    assert [audit.tree_health(s) for s in (1, 2, 3, 4)] == [6, 8, 10, 12]


def test_denial_bonus_is_900_over_one_plus_manhattan_distance():
    assert audit.denial_bonus(0) == 900.0
    assert audit.denial_bonus(1) == 450.0
    assert audit.denial_bonus(29) == 30.0


def test_denial_bonus_is_zero_once_opponent_has_three_trolls():
    assert audit.denial_bonus(1, opponent_trolls=2) == 450.0
    assert audit.denial_bonus(1, opponent_trolls=3) == 0.0


def test_starter_size4_tree_costs_25_turns_for_one_wood():
    row = audit.evaluate(audit.STARTER, size=4, dist_unit=6, dist_shack=6)

    assert row["chop_turns"] == 12
    assert row["turns"] == 25
    assert row["wood"] == 1
    assert row["base_score"] == 40.0


def test_trained_worker_is_an_order_of_magnitude_more_efficient():
    starter = audit.evaluate(audit.STARTER, size=4, dist_unit=6, dist_shack=6)
    trained = audit.evaluate(audit.TRAINED, size=4, dist_unit=6, dist_shack=6)

    assert trained["turns"] == 9
    assert trained["wood"] == 3
    assert round(trained["base_score"], 1) == 333.3
    assert trained["base_score"] > 8 * starter["base_score"]


def test_bonus_dominates_the_starter_but_not_the_trained_worker():
    # The audit's central claim: the emergent division of labour.
    starter = audit.evaluate(audit.STARTER, size=4, dist_unit=6, dist_shack=6)
    trained = audit.evaluate(audit.TRAINED, size=4, dist_unit=6, dist_shack=6)

    # Starter: bonus outweighs pure wood efficiency well out into the map.
    assert audit.denial_bonus(10) / starter["base_score"] > 2.0
    assert audit.denial_bonus(20) / starter["base_score"] > 1.0
    # Trained: only decisive right next to the opponent shack.
    assert audit.denial_bonus(10) / trained["base_score"] < 0.3
    assert audit.denial_bonus(1) / trained["base_score"] > 1.0


def test_crossover_distance_is_reported_per_worker_class():
    # Distance at which the denial bonus stops outweighing the base score.
    assert audit.crossover_distance(audit.STARTER, size=4) == 21
    assert audit.crossover_distance(audit.TRAINED, size=4) == 1


def test_report_covers_both_classes_and_all_sizes():
    report = audit.build_report()

    assert report["source_sha256"] == SOURCE_SHA256
    assert {r["worker"] for r in report["rows"]} == {"starter", "trained"}
    assert sorted({r["size"] for r in report["rows"]}) == [1, 2, 3, 4]
    for row in report["rows"]:
        assert row["base_score"] > 0
        assert row["crossover_distance"] >= 0
