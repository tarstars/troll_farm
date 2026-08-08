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


# ==========================================================================
# Spec-author ruling: chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md
#
# D1 -- withdrawal accounting is accepted as a spec correction, but gross
#       deposits, bank withdrawals and net bank flow must be three separately
#       named quantities and every bound metric must say which it is.
# D5 -- a deterministic shadow ledger is permitted, but every attribution must
#       be uniquely derivable from the recorded state or become `unknown` and
#       force GATE_UNREADY. "A deterministic tie-break is not proof of
#       identifiability."
# ==========================================================================

RULING = "chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md"


class TestD1SchemaSeparatesGrossWithdrawalAndNet(unittest.TestCase):
    """Ruling D1: `DEP_*` must not be silently redefined as net."""

    def test_run_ledger_names_gross_withdrawal_and_net_separately(self):
        cand, _ = fx.fixture_09_longer_game()
        run = cand.ledger.to_json()
        for c in ledger.SOURCE_CLASSES:
            for prefix in ("gdep_", "wdr_", "net_bank_flow_"):
                self.assertIn(prefix + c, run,
                              "%s: run schema must expose %s%s" %
                              (RULING, prefix, c))
        # the frozen spec term `DEP_*` stays GROSS (ruling D1 change 1)
        for c in ledger.SOURCE_CLASSES:
            self.assertEqual(run["dep_" + c], run["gdep_" + c],
                             "dep_%s must remain gross, not net" % c)
        # and net is exactly gross minus withdrawals
        for c in ledger.SOURCE_CLASSES:
            self.assertEqual(run["net_bank_flow_" + c],
                             run["gdep_" + c] - run["wdr_" + c])
        # the un-suffixed net total is gone; both totals are explicit
        self.assertIn("gdep_total", run)
        self.assertIn("net_bank_flow_total", run)
        self.assertNotIn("dep_total", run)

    def test_run_ledger_exercises_a_real_withdrawal(self):
        # bite-test 9's opponent withdraws one banked natural apple
        run = fx.fixture_09_longer_game()[0].ledger.to_json()
        self.assertEqual(run["wdr_natural"], 1)
        self.assertEqual(run["gdep_natural"], 2)
        self.assertEqual(run["net_bank_flow_natural"], 1)

    def test_pair_result_exposes_net_and_gross_terms_separately(self):
        cand, par = fx.fixture_09_longer_game()
        res = an.analyze_pair(cand, par)
        for key in ("d_direct_net", "d_schedule_net", "d_unknown_net",
                    "schedule_windfall_net", "d_direct_gross",
                    "d_production_gross", "d_train", "d_opp"):
            self.assertIn(key, res, "%s: pair schema must expose %s"
                          % (RULING, key))
        for c in ledger.SOURCE_CLASSES:
            for prefix in ("d_gdep_", "d_wdr_", "d_nbf_"):
                self.assertIn(prefix + c, res)
        # the ambiguous unqualified names must be gone entirely
        for gone in ("d_direct", "d_schedule", "d_unknown",
                     "schedule_windfall"):
            self.assertNotIn(gone, res,
                             "%s: %r no longer states gross or net" %
                             (RULING, gone))

    def test_the_exact_identity_uses_net_bank_flow(self):
        # D_OPP = D_DIRECT_NET + D_SCHEDULE_NET + D_UNKNOWN_NET - D_TRAIN
        for name in ("fixture_04_direct_theft", "fixture_05_indirect_only",
                     "fixture_07_train_offset", "fixture_09_longer_game",
                     "fixture_10_blind_spot"):
            cand, par = getattr(fx, name)()
            res = an.analyze_pair(cand, par)
            self.assertEqual(
                res["d_opp"],
                res["d_direct_net"] + res["d_schedule_net"]
                + res["d_unknown_net"] - res["d_train"], name)
            self.assertEqual(res["residual"], 0, name)

    def test_result_schema_is_versioned_and_bumped(self):
        cand, par = fx.fixture_09_longer_game()
        res = an.analyze_pair(cand, par)
        self.assertGreaterEqual(res.get("schema_version", 0), 2,
                                "%s: the result schema must be versioned"
                                % RULING)
        self.assertEqual(res["candidate"].get("schema_version"),
                         res["schema_version"])
        report = an.aggregate_report([res])
        self.assertEqual(report.get("schema_version"), res["schema_version"])

    def test_gross_production_is_a_separate_mandatory_diagnostic(self):
        """Gross production rises while an equal withdrawal keeps score flat."""
        cand, par = fx.fixture_d1_gross_production_with_offsetting_withdrawal()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["candidate"]["identifiable"], True,
                         res["candidate"].get("ambiguities"))
        self.assertEqual(res["candidate"]["gdep_opponent"], 1)
        self.assertEqual(res["candidate"]["wdr_opponent"], 1)
        self.assertEqual(res["candidate"]["net_bank_flow_opponent"], 0)
        # gross says "the candidate expanded opponent production"
        self.assertEqual(res["d_production_gross"], 1)
        self.assertEqual(res["d_gdep_opponent"], 1)
        self.assertEqual(res["d_wdr_opponent"], 1)
        # net says "it contributed nothing to terminal bank score"
        self.assertEqual(res["d_schedule_net"], 0)
        self.assertEqual(res["schedule_windfall_net"], 0)
        self.assertEqual(res["d_opp"], 0)
        self.assertEqual(res["d_unknown_net"], 0)
        self.assertEqual(res["residual"], 0)
        self.assertNotEqual(res["d_production_gross"], res["d_schedule_net"])


class TestD1BoundMetricNamesStateGrossOrNet(unittest.TestCase):
    """Ruling D1 change 4: the unqualified name is no longer sufficient."""

    def _bound(self, metric):
        spec = dict(fx.TEST_BOUND_ZERO_WINDFALL)
        spec["metric"] = metric
        return an.Bound(spec)

    def test_unqualified_metric_names_are_rejected(self):
        for metric in ("mean_schedule_windfall", "mean_d_direct",
                       "mean_d_schedule"):
            bound = self._bound(metric)
            self.assertFalse(bound.valid,
                             "%s: %r does not state gross or net"
                             % (RULING, metric))
            self.assertIn("bound_metric_ambiguous_gross_or_net",
                          bound.invalid_reasons, metric)

    def test_qualified_metric_names_are_accepted(self):
        for metric in ("mean_schedule_windfall_net", "mean_d_direct_net",
                       "mean_d_schedule_net", "mean_d_direct_gross",
                       "mean_production_gross", "mean_d_opp"):
            self.assertTrue(self._bound(metric).valid,
                            "%r must be a supported bound metric" % metric)

    def test_the_fixture_bound_uses_a_qualified_name(self):
        self.assertEqual(fx.TEST_BOUND_ZERO_WINDFALL["metric"],
                         "mean_schedule_windfall_net")

    def test_an_ambiguous_metric_makes_the_pair_gate_unready(self):
        cand, par = fx.fixture_05_indirect_only()
        res = an.analyze_pair(cand, par,
                              bound=self._bound("mean_schedule_windfall"))
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("bound_metric_ambiguous_gross_or_net",
                      res["unready_reasons"])


class TestD5FailsClosedOnNonIdentifiableAttribution(unittest.TestCase):
    """Ruling D5: ambiguity must become `unknown`, never a tie-break answer."""

    def assert_fails_closed(self, res, reason):
        self.assertEqual(res["candidate"]["identifiable"], False)
        self.assertIn(reason,
                      [a["reason"] for a in res["candidate"]["ambiguities"]],
                      res["candidate"]["ambiguities"])
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("non_identifiable_attribution", res["unready_reasons"])
        self.assertNotEqual(res["status"], an.PASS)

    def test_same_turn_deposit_and_withdrawal_is_unknown(self):
        cand, par = fx.fixture_a1_same_turn_deposit_withdrawal()
        res = an.analyze_pair(cand, par,
                              bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))
        self.assert_fails_closed(res, "deposit_withdrawal_split")

        run = res["candidate"]
        # the old tie-break banked one `ours` atom and withdrew one `natural`
        # atom; neither claim is derivable, so both atoms are `unknown`
        self.assertEqual(run["gdep_ours"], 0)
        self.assertEqual(run["wdr_natural"], 0)
        self.assertEqual(run["gdep_unknown"], 1)
        self.assertEqual(run["wdr_unknown"], 1)
        # ... and the unknown mass cancels exactly, so the ruling's
        # "D_UNKNOWN_NET == 0 is not sufficient evidence" clause is what
        # carries the fail-closed signal here
        self.assertEqual(run["net_bank_flow_unknown"], 0)
        self.assertEqual(res["d_unknown_net"], 0)
        self.assertGreaterEqual(run["unknown_atoms"], 2)
        # every arithmetic check still passes -- only identifiability bites
        self.assertEqual(res["residual"], 0)
        self.assertEqual(res["d_opp"], 0)

    def test_multi_source_deposit_with_concurrent_withdrawal_is_unknown(self):
        cand, par = fx.fixture_a2_multi_source_deposit()
        res = an.analyze_pair(cand, par,
                              bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))
        self.assert_fails_closed(res, "deposit_withdrawal_split")

        run = res["candidate"]
        self.assertEqual(run["gdep_ours"], 0)
        self.assertEqual(run["gdep_natural"], 0)
        self.assertEqual(run["gdep_unknown"], 2)
        self.assertEqual(run["wdr_unknown"], 1)
        self.assertEqual(res["residual"], 0)

    def test_class_swap_pair_is_indistinguishable_so_both_are_unknown(self):
        """Two hidden histories, one observable transition, two labels."""
        results = {}
        for order in ("ours_first", "opponent_first"):
            cand, par = fx.fixture_a3_class_swap(order)
            results[order] = an.analyze_pair(
                cand, par, bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))

        a, b = results["ours_first"], results["opponent_first"]
        # the ambiguous transition is literally the same transcript text
        ca, cb = (fx.fixture_a3_class_swap("ours_first")[0],
                  fx.fixture_a3_class_swap("opponent_first")[0])
        self.assertEqual(ca.transcript_text.split("\n")[-16:],
                         cb.transcript_text.split("\n")[-16:])

        for order, res in results.items():
            self.assert_fails_closed(res, "class_composition")
            self.assertEqual(res["candidate"]["gdep_unknown"], 1, order)
            self.assertEqual(res["candidate"]["gdep_ours"], 0, order)
            self.assertEqual(res["candidate"]["gdep_opponent"], 0, order)
            self.assertEqual(res["d_opp"], 1, order)
            self.assertEqual(res["residual"], 0, order)

        # the two histories must now be reported identically -- the old FIFO
        # tie-break split them into direct vs schedule
        for key in ("d_direct_net", "d_schedule_net", "d_unknown_net",
                    "d_direct_gross", "d_production_gross"):
            self.assertEqual(a[key], b[key], key)

    def test_acquisition_on_a_dead_asset_cell_is_unknown(self):
        cand, par = fx.fixture_a4_dead_cell_acquisition()
        res = an.analyze_pair(cand, par,
                              bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))
        run = res["candidate"]
        self.assertEqual(run["gdep_natural"], 0,
                         "a dead asset must not launder a later atom")
        self.assertEqual(run["gdep_unknown"], 1)
        self.assertEqual(run["unknown_atoms"], 1)
        self.assertEqual(res["d_unknown_net"], 1)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("unknown_provenance", res["unready_reasons"])

    def test_absent_or_mixed_planter_occupancy_is_unknown(self):
        for mode in ("mixed", "absent"):
            cand, par = fx.fixture_a5_planter_occupancy(mode)
            res = an.analyze_pair(cand, par,
                                  bound=an.Bound(fx.TEST_BOUND_ZERO_WINDFALL))
            run = res["candidate"]
            self.assertEqual(run["gdep_ours"], 0, mode)
            self.assertEqual(run["gdep_opponent"], 0, mode)
            self.assertEqual(run["gdep_unknown"], 1, mode)
            self.assertEqual(res["d_unknown_net"], 1, mode)
            self.assertEqual(res["status"], an.GATE_UNREADY, mode)
            self.assertIn("unknown_provenance", res["unready_reasons"], mode)


class TestD5MutationRevertedTieBreakIsCaught(unittest.TestCase):
    """Ruling D5: prove the adversarial fixtures bite the identifiability fix.

    A fixture that passes whether or not the fix is present proves nothing.
    Each identifiability decision is a named module-level predicate; reverting
    it to the old unconditional deterministic tie-break must make every
    adversarial fixture stop failing closed and start attributing mass.
    """

    HOOKS = ("split_is_identifiable", "partial_take_is_identifiable",
             "assignment_is_identifiable")

    def test_the_identifiability_hooks_exist(self):
        for name in self.HOOKS:
            self.assertTrue(hasattr(ledger, name),
                            "%s: missing identifiability predicate %r"
                            % (RULING, name))

    def _revert_tie_break(self):
        saved = {}
        for name in self.HOOKS:
            self.assertTrue(hasattr(ledger, name), name)
            saved[name] = getattr(ledger, name)
            setattr(ledger, name, lambda *a, **k: True)
        return saved

    def _restore(self, saved):
        for name, fn in saved.items():
            setattr(ledger, name, fn)

    def test_reverted_tie_break_reopens_same_turn_misattribution(self):
        bound = an.Bound(fx.TEST_BOUND_ZERO_WINDFALL)
        before = an.analyze_pair(*fx.fixture_a1_same_turn_deposit_withdrawal(),
                                 bound=bound)
        self.assertEqual(before["status"], an.GATE_UNREADY)

        saved = self._revert_tie_break()
        try:
            after = an.analyze_pair(
                *fx.fixture_a1_same_turn_deposit_withdrawal(), bound=bound)
        finally:
            self._restore(saved)

        # the old behaviour: a confident, unprovable split
        self.assertEqual(after["candidate"]["gdep_ours"], 1)
        self.assertEqual(after["candidate"]["wdr_natural"], 1)
        self.assertEqual(after["d_direct_net"], 1)
        self.assertEqual(after["d_schedule_net"], -1)
        # with terminal score, net flow and residual all still correct
        self.assertEqual(after["d_opp"], 0)
        self.assertEqual(after["residual"], 0)
        self.assertNotIn("non_identifiable_attribution",
                         after["unready_reasons"])
        # and the fix is restored
        self.assertEqual(
            an.analyze_pair(*fx.fixture_a1_same_turn_deposit_withdrawal(),
                            bound=bound)["status"], an.GATE_UNREADY)

    def test_reverted_tie_break_reopens_the_class_swap(self):
        bound = an.Bound(fx.TEST_BOUND_ZERO_WINDFALL)
        saved = self._revert_tie_break()
        try:
            a = an.analyze_pair(*fx.fixture_a3_class_swap("ours_first"),
                                bound=bound)
            b = an.analyze_pair(*fx.fixture_a3_class_swap("opponent_first"),
                                bound=bound)
        finally:
            self._restore(saved)

        # identical observable transition, identical score, identical
        # residual -- but the tie-break moves mass between the two terms
        self.assertEqual(a["d_opp"], b["d_opp"])
        self.assertEqual(a["residual"], b["residual"])
        self.assertEqual(a["d_direct_net"], 1)
        self.assertEqual(b["d_direct_net"], 0)
        self.assertEqual(a["d_schedule_net"], 0)
        self.assertEqual(b["d_schedule_net"], 1)

    def test_reverted_tie_break_reopens_multi_source_attribution(self):
        bound = an.Bound(fx.TEST_BOUND_ZERO_WINDFALL)
        saved = self._revert_tie_break()
        try:
            after = an.analyze_pair(*fx.fixture_a2_multi_source_deposit(),
                                    bound=bound)
        finally:
            self._restore(saved)
        self.assertEqual(after["candidate"]["gdep_ours"], 1)
        self.assertEqual(after["candidate"]["gdep_natural"], 1)
        self.assertEqual(after["candidate"]["gdep_unknown"], 0)
        self.assertEqual(after["residual"], 0)

    def test_the_valid_fixtures_are_unaffected_by_the_hooks(self):
        """The fix must not fire on the fifteen -- otherwise it proves nothing.

        If reverting the tie-break changed a valid fixture's numbers, the
        adversarial fixtures could be passing for an unrelated reason.
        """
        names = ("fixture_04_direct_theft", "fixture_05_indirect_only",
                 "fixture_06_natural_opportunity", "fixture_07_train_offset",
                 "fixture_08_mixed_cargo", "fixture_09_longer_game",
                 "fixture_10_blind_spot", "fixture_s1_wood_chop",
                 "fixture_d1_gross_production_with_offsetting_withdrawal")
        before = {n: an.analyze_pair(*getattr(fx, n)()) for n in names}
        saved = self._revert_tie_break()
        try:
            after = {n: an.analyze_pair(*getattr(fx, n)()) for n in names}
        finally:
            self._restore(saved)
        for n in names:
            for key in ("d_direct_net", "d_schedule_net", "d_unknown_net",
                        "d_direct_gross", "d_production_gross", "d_opp",
                        "residual"):
                self.assertEqual(before[n][key], after[n][key],
                                 "%s.%s" % (n, key))
            self.assertEqual(before[n]["candidate"]["identifiable"], True, n)


class TestNoPassWithoutAnOwnerFrozenBound(unittest.TestCase):
    """Ruling: no PASS may be emitted without `provenance == owner_frozen`."""

    def test_no_fixture_in_the_corpus_can_produce_pass(self):
        bound = an.Bound(fx.TEST_BOUND_ZERO_WINDFALL)
        self.assertNotEqual(bound.provenance, "owner_frozen")
        results = []
        for name in sorted(n for n in dir(fx) if n.startswith("fixture_")):
            cand, par = getattr(fx, name)()
            res = an.analyze_pair(cand, par, bound=bound,
                                  self_pair=name.startswith(("fixture_01",
                                                             "fixture_11")),
                                  pair_id=name)
            self.assertNotEqual(res["status"], an.PASS, name)
            results.append(res)
        report = an.aggregate_report(results, bound=bound)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)


if __name__ == "__main__":
    unittest.main()
