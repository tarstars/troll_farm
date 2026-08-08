#!/usr/bin/env python3
"""The fifteen mandatory I-30 bite-tests (spec sec. 10).

Authoritative specification:
  chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md
  (on branch agent/chatgpt_1)

Every fixture runs through the real transcript/command parser
(`trace_detectors.TraceParser` / `CommandParser`), then the I-30 shadow
referee ledger, then the analyzer. Assertions are on exact integers, not on
"nonzero" statuses (spec sec. 10 closing sentence).

Run: python3 -m unittest test_i30_invariant -v
"""

from __future__ import annotations

import unittest

import i30_analyzer as an
import i30_fixtures as fx
import i30_ledger as ledger
import trace_detectors as td


def d6_count(record):
    """Real D-6 detector over the real parsed trace."""
    return td.detect_d6(record.trace)["count"]


class TestBite01ExactSelfPair(unittest.TestCase):
    """Spec sec. 10 negative control 1 / sec. 3 parent-vs-parent."""

    def test_every_delta_and_residual_is_zero(self):
        cand, par = fx.fixture_01_exact_self_pair()
        res = an.analyze_pair(cand, par, self_pair=True)

        self.assertTrue(res["pair_identity"]["valid"], res["pair_identity"])
        self.assertEqual(res["d_direct"], 0)
        self.assertEqual(res["d_schedule"], 0)
        self.assertEqual(res["d_unknown"], 0)
        self.assertEqual(res["d_train"], 0)
        self.assertEqual(res["d_opp"], 0)
        self.assertEqual(res["schedule_windfall"], 0)
        self.assertEqual(res["residual"], 0)
        self.assertEqual(res["candidate"]["residual"], 0)
        self.assertEqual(res["parent"]["residual"], 0)
        self.assertEqual(res["status"], an.NOT_APPLICABLE)

    def test_command_hashes_are_equal(self):
        cand, par = fx.fixture_01_exact_self_pair()
        self.assertEqual(cand.identity["command_stream_sha256"],
                         par.identity["command_stream_sha256"])
        self.assertEqual(cand.identity["initial_state_sha256"],
                         par.identity["initial_state_sha256"])


class TestBite02InertCandidate(unittest.TestCase):
    """Spec sec. 10 negative control 2."""

    def test_non_state_changing_diagnostic_moves_nothing(self):
        cand, par = fx.fixture_02_inert_candidate()
        res = an.analyze_pair(cand, par)

        self.assertNotEqual(cand.identity["command_stream_sha256"],
                            par.identity["command_stream_sha256"])
        for key in ("d_direct", "d_schedule", "d_unknown", "d_train", "d_opp",
                    "schedule_windfall", "residual", "d_terminal_turn"):
            self.assertEqual(res[key], 0, key)
        self.assertEqual(res["candidate"]["dep_natural"], 1)
        self.assertEqual(res["parent"]["dep_natural"], 1)


class TestBite03NoBananaActivation(unittest.TestCase):
    """Spec sec. 10 negative control 3 / sec. 4 / sec. 8."""

    def test_status_is_not_applicable_not_a_fabricated_pass(self):
        cand, par = fx.fixture_03_no_banana_activation()
        res = an.analyze_pair(cand, par)

        self.assertFalse(res["banana_active"])
        self.assertEqual(res["status"], an.NOT_APPLICABLE)
        self.assertNotEqual(res["status"], an.PASS)
        self.assertEqual(res["d_opp"], 0)
        self.assertEqual(res["schedule_windfall"], 0)
        self.assertEqual(res["residual"], 0)

    def test_claimed_but_unexercised_mechanism_is_unproven(self):
        cand, par = fx.fixture_03_no_banana_activation()
        res = an.analyze_pair(cand, par, banana_mechanism_claimed=True)
        self.assertEqual(res["status"], an.UNPROVEN)


class TestBite04DirectTheftOnly(unittest.TestCase):
    """Spec sec. 10 positive control 4."""

    def test_d_direct_positive_windfall_zero_and_d6_exercises(self):
        cand, par = fx.fixture_04_direct_theft()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["d_direct"], 1)
        self.assertEqual(res["d_schedule"], 0)
        self.assertEqual(res["d_train"], 0)
        self.assertEqual(res["schedule_windfall"], 0)
        self.assertEqual(res["d_opp"], 1)
        self.assertEqual(res["d_unknown"], 0)
        self.assertEqual(res["residual"], 0)
        self.assertTrue(res["banana_active"])
        self.assertGreater(d6_count(cand), 0)


class TestBite05IndirectProductionOnly(unittest.TestCase):
    """Spec sec. 10 positive control 5 -- the D-6 blind spot."""

    def test_windfall_positive_while_d6_stays_zero(self):
        cand, par = fx.fixture_05_indirect_only()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["d_direct"], 0)
        self.assertEqual(res["d_schedule"], 2)
        self.assertEqual(res["d_train"], 0)
        self.assertEqual(res["schedule_windfall"], 2)
        self.assertEqual(res["d_opp"], 2)
        self.assertEqual(res["d_unknown"], 0)
        self.assertEqual(res["residual"], 0)
        self.assertEqual(d6_count(cand), 0)
        self.assertEqual(res["candidate"]["dep_opponent"], 3)
        self.assertEqual(res["parent"]["dep_natural"], 1)


class TestBite06NaturalOpportunity(unittest.TestCase):
    """Spec sec. 10 positive control 6."""

    def test_uncontested_natural_output_lands_in_d_schedule(self):
        cand, par = fx.fixture_06_natural_opportunity()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["d_direct"], 0)
        self.assertEqual(res["d_dep_natural"], 1)
        self.assertEqual(res["d_dep_opponent"], 0)
        self.assertEqual(res["d_schedule"], 1)
        self.assertEqual(res["schedule_windfall"], 1)
        self.assertEqual(res["d_opp"], 1)
        self.assertEqual(res["residual"], 0)


class TestBite07TrainSpendOffset(unittest.TestCase):
    """Spec sec. 10 positive control 7."""

    def test_train_bill_closes_the_identity_with_the_correct_sign(self):
        cand, par = fx.fixture_07_train_offset()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["candidate"]["dep_total"],
                         res["parent"]["dep_total"])
        self.assertEqual(res["d_direct"], 0)
        self.assertEqual(res["d_schedule"], 0)
        self.assertEqual(res["d_train"], 6)
        self.assertEqual(res["schedule_windfall"], -6)
        self.assertEqual(res["d_opp"], -6)
        self.assertEqual(res["residual"], 0)
        self.assertEqual(res["candidate"]["train_events"], 1)

    def test_training_cost_matches_the_engine_formula(self):
        # engine.rs training_cost: n + stat^2 in PLUM/LEMON/APPLE/IRON,
        # IRON only charged when the map has iron terrain.
        self.assertEqual(ledger.training_cost(1, (1, 1, 1, 1), False),
                         [2, 2, 2, 0, 0, 0])
        self.assertEqual(ledger.training_cost(1, (1, 1, 1, 1), True),
                         [2, 2, 2, 0, 2, 0])


class TestBite08MixedCargo(unittest.TestCase):
    """Spec sec. 10 positive control 8."""

    def test_each_source_class_in_one_drop_is_counted_exactly_once(self):
        cand, par = fx.fixture_08_mixed_cargo()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["candidate"]["dep_ours"], 1)
        self.assertEqual(res["candidate"]["dep_opponent"], 1)
        self.assertEqual(res["candidate"]["dep_natural"], 1)
        self.assertEqual(res["candidate"]["dep_unknown"], 0)
        self.assertEqual(res["candidate"]["drop_events"], 1)
        self.assertEqual(res["d_direct"], 1)
        self.assertEqual(res["d_schedule"], 2)
        self.assertEqual(res["schedule_windfall"], 2)
        self.assertEqual(res["d_opp"], 3)
        self.assertEqual(res["residual"], 0)


class TestBite09LongerGameSchedule(unittest.TestCase):
    """Spec sec. 10 positive control 9."""

    def test_terminal_turn_delta_and_windfall_both_expose_it(self):
        cand, par = fx.fixture_09_longer_game()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["candidate"]["terminal_turn"], 12)
        self.assertEqual(res["parent"]["terminal_turn"], 5)
        self.assertEqual(res["d_terminal_turn"], 7)
        self.assertEqual(res["d_direct"], 0)
        self.assertEqual(res["d_schedule"], 1)
        self.assertEqual(res["schedule_windfall"], 1)
        self.assertEqual(res["d_opp"], 1)
        self.assertEqual(res["residual"], 0)
        # the opponent withdrew its own banked fruit to seed the extra cycle
        self.assertEqual(res["candidate"]["wdr_natural"], 1)


class TestBite10BlindSpotFixture(unittest.TestCase):
    """Spec sec. 10 positive control 10 -- the D89a-class blind spot."""

    def test_every_behavioural_detector_passes(self):
        cand, _ = fx.fixture_10_blind_spot()
        for res in td.run_all(cand.trace):
            self.assertEqual(res["verdict"], "PASS",
                             "%s: %r" % (res["detector"], res["episodes"]))

    def test_d6_is_zero_but_i30_sees_opponent_own_production(self):
        cand, par = fx.fixture_10_blind_spot()
        self.assertEqual(d6_count(cand), 0)

        res = an.analyze_pair(cand, par,
                              bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))
        self.assertEqual(res["d_direct"], 0)
        self.assertEqual(res["d_dep_opponent"], 2)
        self.assertEqual(res["d_dep_natural"], -1)
        self.assertEqual(res["d_schedule"], 1)
        self.assertEqual(res["d_train"], 0)
        self.assertEqual(res["schedule_windfall"], 1)
        self.assertEqual(res["d_opp"], 1)
        self.assertEqual(res["d_unknown"], 0)
        self.assertEqual(res["residual"], 0)

    def test_i30_must_not_return_pass_under_a_bound_excluding_the_windfall(self):
        cand, par = fx.fixture_10_blind_spot()
        res = an.analyze_pair(cand, par,
                              bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))
        self.assertNotEqual(res["status"], an.PASS)
        self.assertEqual(res["status"], an.FAIL)


class TestBite11PairIdentityMismatch(unittest.TestCase):
    """Spec sec. 10 fail-closed control 11 / sec. 3."""

    def test_self_pair_hash_mismatch_is_gate_unready(self):
        cand, par = fx.fixture_11_hash_mismatch_self_pair()
        res = an.analyze_pair(cand, par, self_pair=True,
                              bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))

        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertFalse(res["pair_identity"]["valid"])
        self.assertIn("bot_source_sha256", res["pair_identity"]["mismatched"])
        self.assertIn("pair_identity", res["unready_reasons"])
        # never silently dropped from the denominator (spec sec. 3)
        self.assertTrue(res["counted_in_denominator"])


class TestBite12UntaggedAtom(unittest.TestCase):
    """Spec sec. 10 fail-closed control 12 / sec. 5.2 / sec. 6."""

    def test_one_untagged_score_bearing_atom_is_gate_unready(self):
        cand, par = fx.fixture_12_untagged_atom()
        res = an.analyze_pair(cand, par,
                              bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))

        self.assertEqual(res["candidate"]["unknown_atoms"], 1)
        self.assertEqual(res["candidate"]["dep_unknown"], 1)
        self.assertEqual(res["d_unknown"], 1)
        self.assertEqual(res["residual"], 0)     # isolates the provenance path
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("unknown_provenance", res["unready_reasons"])
        self.assertNotEqual(res["status"], an.PASS)


class TestBite13NonzeroResidual(unittest.TestCase):
    """Spec sec. 10 fail-closed control 13 / sec. 6."""

    def test_nonzero_conservation_residual_is_gate_unready(self):
        cand, par = fx.fixture_13_nonzero_residual()
        res = an.analyze_pair(cand, par,
                              bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))

        self.assertEqual(res["candidate"]["residual"], 1)
        self.assertEqual(res["parent"]["residual"], 0)
        self.assertEqual(res["residual"], 1)
        self.assertEqual(res["d_unknown"], 0)    # isolates the conservation path
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("conservation_residual", res["unready_reasons"])
        # raw values are preserved even when the status is not PASS (sec. 8)
        self.assertEqual(res["d_opp"], 1)


class TestBite14AbsentBound(unittest.TestCase):
    """Spec sec. 10 fail-closed control 14 / sec. 8 / sec. 11."""

    def test_active_candidate_without_a_bound_is_gate_unready(self):
        cand, par = fx.fixture_05_indirect_only()
        res = an.analyze_pair(cand, par, bound=None)

        self.assertTrue(res["banana_active"])
        self.assertEqual(res["sub_status"], an.MEASURED_UNTHRESHOLDED)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertNotEqual(res["status"], an.PASS)
        self.assertIn("absent_bound", res["unready_reasons"])
        # raw values survive (sec. 8)
        self.assertEqual(res["schedule_windfall"], 2)

    def test_bound_without_owner_freeze_never_yields_pass(self):
        cand, par = fx.fixture_05_indirect_only()
        loose = dict(fx.TEST_BOUND_ZERO_WINDFALL)
        loose["threshold"] = 100          # satisfied by windfall == 2
        res = an.analyze_pair(cand, par, bound=an.Bound(loose))
        self.assertNotEqual(res["status"], an.PASS)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("bound_not_owner_frozen", res["unready_reasons"])

    def test_bound_hash_pin_mismatch_is_gate_unready(self):
        cand, par = fx.fixture_05_indirect_only()
        bound = an.Bound(fx.TEST_BOUND_ZERO_WINDFALL,
                         pinned_sha256="f" * 64)
        res = an.analyze_pair(cand, par, bound=bound)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("bound_hash_mismatch", res["unready_reasons"])


class TestBite15MutationBitesTheIndirectTerm(unittest.TestCase):
    """Spec sec. 10 fail-closed control 15.

    Deleting the indirect-production calculation must break bite-test 10's
    own assertions -- not a neighbouring check. D-6 is verified to be
    unchanged (still zero) across the mutation, so the flip is attributable
    to the I-30 schedule term alone.
    """

    def test_removing_the_indirect_calculation_reopens_the_blind_spot(self):
        cand, par = fx.fixture_10_blind_spot()
        bound = an.Bound(fx.TEST_BOUND_ZERO_WINDFALL)

        before = an.analyze_pair(cand, par, bound=bound)
        self.assertEqual(before["schedule_windfall"], 1)
        self.assertEqual(before["status"], an.FAIL)
        self.assertEqual(d6_count(cand), 0)

        original = an.compute_schedule_windfall
        try:
            an.compute_schedule_windfall = lambda d_schedule, d_train: 0
            after = an.analyze_pair(cand, par, bound=bound)
        finally:
            an.compute_schedule_windfall = original

        self.assertEqual(after["schedule_windfall"], 0)
        self.assertNotEqual(after["status"], an.FAIL)
        # the conservation residual is NOT what caught the mutation
        self.assertEqual(after["residual"], 0)
        # the neighbouring detector is unmoved
        self.assertEqual(d6_count(cand), 0)
        # and the un-mutated analyzer is restored
        self.assertEqual(an.analyze_pair(cand, par, bound=bound)["status"],
                         an.FAIL)


class TestSupplementaryWoodChopCoverage(unittest.TestCase):
    """NOT one of the fifteen mandated bite-tests.

    The fifteen never deposit WOOD, so the frozen `WOOD=4` score weight
    (spec sec. 5.1) and the CHOP inheritance rule (spec sec. 5.2, "Wood from
    CHOP inherits the chopped asset's creator class") would otherwise be live
    but wholly unexercised. A mutation sweep confirmed that flipping the WOOD
    weight to 1 survived all fifteen; it does not survive this.
    """

    def test_chopped_wood_carries_its_asset_class_at_weight_four(self):
        cand, par = fx.fixture_s1_wood_chop()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["candidate"]["chop_events"], 2)
        self.assertEqual(res["candidate"]["dep_natural"], 4)
        self.assertEqual(res["candidate"]["dep_ours"], 4)
        self.assertEqual(res["d_direct"], 4)
        self.assertEqual(res["d_schedule"], 4)
        self.assertEqual(res["schedule_windfall"], 4)
        self.assertEqual(res["d_opp"], 8)
        self.assertEqual(res["residual"], 0)


if __name__ == "__main__":
    unittest.main()
