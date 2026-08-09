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

import json
import os
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
        self.assertEqual(res["d_direct_net"], 0)
        self.assertEqual(res["d_schedule_net"], 0)
        self.assertEqual(res["d_unknown_net"], 0)
        self.assertEqual(res["d_train"], 0)
        self.assertEqual(res["d_opp"], 0)
        self.assertEqual(res["schedule_windfall_net"], 0)
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
        for key in ("d_direct_net", "d_schedule_net", "d_unknown_net",
                    "d_direct_gross", "d_production_gross", "d_train",
                    "d_opp", "schedule_windfall_net", "residual",
                    "d_terminal_turn"):
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
        self.assertEqual(res["schedule_windfall_net"], 0)
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

        self.assertEqual(res["d_direct_net"], 1)
        self.assertEqual(res["d_schedule_net"], 0)
        self.assertEqual(res["d_train"], 0)
        self.assertEqual(res["schedule_windfall_net"], 0)
        self.assertEqual(res["d_opp"], 1)
        self.assertEqual(res["d_unknown_net"], 0)
        self.assertEqual(res["residual"], 0)
        self.assertTrue(res["banana_active"])
        self.assertGreater(d6_count(cand), 0)


class TestBite05IndirectProductionOnly(unittest.TestCase):
    """Spec sec. 10 positive control 5 -- the D-6 blind spot."""

    def test_windfall_positive_while_d6_stays_zero(self):
        cand, par = fx.fixture_05_indirect_only()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["d_direct_net"], 0)
        self.assertEqual(res["d_train"], 0)
        self.assertEqual(res["d_opp"], 2)
        self.assertEqual(res["d_unknown_net"], 0)
        self.assertEqual(res["residual"], 0)
        self.assertEqual(d6_count(cand), 0)
        self.assertEqual(res["candidate"]["dep_opponent"], 3)
        # REVISION 3 (review I30R2-5). The parent's single banked apple came
        # out of the opponent's OPENING CARRY, so it is `baseline`, not
        # `natural`: revision 2 counted the opponent's own endowment as
        # natural production and netted it against the candidate's three
        # genuinely produced apples.
        self.assertEqual(res["parent"]["dep_baseline"], 1)
        self.assertEqual(res["parent"]["dep_natural"], 0)
        self.assertEqual(res["d_baseline_net"], -1)
        self.assertEqual(res["d_schedule_net"], 3)
        self.assertEqual(res["schedule_windfall_net"], 3)
        # ... and the exact identity still closes over all five classes
        self.assertEqual(res["d_opp"],
                         res["d_direct_net"] + res["d_schedule_net"]
                         + res["d_baseline_net"] + res["d_unknown_net"]
                         - res["d_train"])


class TestBite06NaturalOpportunity(unittest.TestCase):
    """Spec sec. 10 positive control 6."""

    def test_uncontested_natural_output_lands_in_d_schedule(self):
        cand, par = fx.fixture_06_natural_opportunity()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["d_direct_net"], 0)
        self.assertEqual(res["d_nbf_natural"], 1)
        self.assertEqual(res["d_nbf_opponent"], 0)
        self.assertEqual(res["d_schedule_net"], 1)
        self.assertEqual(res["schedule_windfall_net"], 1)
        self.assertEqual(res["d_opp"], 1)
        self.assertEqual(res["residual"], 0)


class TestBite07TrainSpendOffset(unittest.TestCase):
    """Spec sec. 10 positive control 7."""

    def test_train_bill_closes_the_identity_with_the_correct_sign(self):
        cand, par = fx.fixture_07_train_offset()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["candidate"]["gdep_total"],
                         res["parent"]["gdep_total"])
        self.assertEqual(res["d_direct_net"], 0)
        self.assertEqual(res["d_schedule_net"], 0)
        self.assertEqual(res["d_train"], 6)
        self.assertEqual(res["schedule_windfall_net"], -6)
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
        self.assertEqual(res["d_direct_net"], 1)
        self.assertEqual(res["d_schedule_net"], 2)
        self.assertEqual(res["schedule_windfall_net"], 2)
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
        self.assertEqual(res["d_direct_net"], 0)
        self.assertEqual(res["d_schedule_net"], 1)
        self.assertEqual(res["schedule_windfall_net"], 1)
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

        res = an.analyze_pair(cand, par)
        self.assertEqual(res["d_direct_net"], 0)
        self.assertEqual(res["d_nbf_opponent"], 2)
        self.assertEqual(res["d_nbf_natural"], -1)
        self.assertEqual(res["d_schedule_net"], 1)
        self.assertEqual(res["d_train"], 0)
        self.assertEqual(res["schedule_windfall_net"], 1)
        self.assertEqual(res["d_opp"], 1)
        self.assertEqual(res["d_unknown_net"], 0)
        self.assertEqual(res["residual"], 0)

    def test_i30_must_not_return_pass_under_a_bound_excluding_the_windfall(self):
        """REVISION 3 (review I30R2-1/2): the verdict is the AGGREGATE's.

        A pair is not a population, so the pair row is `MEASURED` and it is the
        aggregate -- over the population the bound names, with a verified
        owner decision -- that renders FAIL.
        """
        cand, par = fx.fixture_10_blind_spot()
        res = an.analyze_pair(cand, par, pair_id="bt10")
        self.assertEqual(res["status"], an.MEASURED)
        self.assertNotIn("bound", res)

        report = an.aggregate_report(
            [res], bound=fx.owner_verified_bound(),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        self.assertNotEqual(report["aggregate_status"], an.PASS)
        self.assertEqual(report["aggregate_status"], an.FAIL)
        self.assertEqual(report["bound_evaluation"]["metric_value_exact"], "1")


class TestBite11PairIdentityMismatch(unittest.TestCase):
    """Spec sec. 10 fail-closed control 11 / sec. 3."""

    def test_self_pair_hash_mismatch_is_gate_unready(self):
        cand, par = fx.fixture_11_hash_mismatch_self_pair()
        res = an.analyze_pair(cand, par, self_pair=True)

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
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["candidate"]["unknown_atoms"], 1)
        self.assertEqual(res["candidate"]["dep_unknown"], 1)
        self.assertEqual(res["d_unknown_net"], 1)
        self.assertEqual(res["residual"], 0)     # isolates the provenance path
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("unknown_provenance", res["unready_reasons"])
        self.assertNotEqual(res["status"], an.PASS)


class TestBite13NonzeroResidual(unittest.TestCase):
    """Spec sec. 10 fail-closed control 13 / sec. 6."""

    def test_nonzero_conservation_residual_is_gate_unready(self):
        cand, par = fx.fixture_13_nonzero_residual()
        res = an.analyze_pair(cand, par)

        self.assertEqual(res["candidate"]["residual"], 1)
        self.assertEqual(res["parent"]["residual"], 0)
        self.assertEqual(res["residual"], 1)
        self.assertEqual(res["d_unknown_net"], 0)    # isolates the conservation path
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("conservation_residual", res["unready_reasons"])
        # raw values are preserved even when the status is not PASS (sec. 8)
        self.assertEqual(res["d_opp"], 1)


class TestBite14AbsentBound(unittest.TestCase):
    """Spec sec. 10 fail-closed control 14 / sec. 8 / sec. 11.

    REVISION 3: every clause of this control moved to the aggregate, which is
    where a bound is now consumed (review I30R2-1).
    """

    def _report(self, **kw):
        cand, par = fx.fixture_05_indirect_only()
        row = an.analyze_pair(cand, par, pair_id="bt14")
        self.assertEqual(row["status"], an.MEASURED)
        return row, an.aggregate_report([row], observed_utc=fx.OBSERVED_UTC,
                                        **kw)

    def test_active_candidate_without_a_bound_is_gate_unready(self):
        row, report = self._report(bound=None)

        self.assertTrue(row["banana_active"])
        self.assertEqual(report["aggregate_sub_status"],
                         an.MEASURED_UNTHRESHOLDED)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertIn("absent_bound", report["aggregate_unready_reasons"])
        # raw values survive (sec. 8)
        self.assertEqual(row["schedule_windfall_net"], 3)

    def test_bound_without_a_verified_owner_decision_never_yields_pass(self):
        loose = dict(fx.TEST_BOUND_WINDFALL)
        loose["threshold"] = 100          # satisfied by windfall == 3
        _row, report = self._report(bound=an.Bound(loose),
                                    authority=fx.test_authority())
        self.assertNotEqual(report["aggregate_status"], an.PASS)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertIn("bound_not_owner_verified",
                      report["aggregate_unready_reasons"])

    def test_bound_hash_pin_mismatch_is_gate_unready(self):
        bound = an.Bound(fx.TEST_BOUND_WINDFALL, pinned_sha256="f" * 64)
        _row, report = self._report(bound=bound)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertIn("bound_hash_mismatch",
                      report["aggregate_unready_reasons"])


class TestBite15MutationBitesTheIndirectTerm(unittest.TestCase):
    """Spec sec. 10 fail-closed control 15.

    Deleting the indirect-production calculation must break bite-test 10's
    own assertions -- not a neighbouring check. D-6 is verified to be
    unchanged (still zero) across the mutation, so the flip is attributable
    to the I-30 schedule term alone.
    """

    def _verdict(self, cand, par):
        row = an.analyze_pair(cand, par, pair_id="bt15")
        report = an.aggregate_report(
            [row], bound=fx.owner_verified_bound(),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        return row, report["aggregate_status"]

    def test_removing_the_indirect_calculation_reopens_the_blind_spot(self):
        cand, par = fx.fixture_10_blind_spot()

        before, verdict = self._verdict(cand, par)
        self.assertEqual(before["schedule_windfall_net"], 1)
        self.assertEqual(verdict, an.FAIL)
        self.assertEqual(d6_count(cand), 0)

        original = an.compute_schedule_windfall_net
        try:
            an.compute_schedule_windfall_net = lambda d_schedule_net, d_train: 0
            after, mutated_verdict = self._verdict(cand, par)
        finally:
            an.compute_schedule_windfall_net = original

        self.assertEqual(after["schedule_windfall_net"], 0)
        self.assertNotEqual(mutated_verdict, an.FAIL)
        self.assertEqual(mutated_verdict, an.PASS)
        # the conservation residual is NOT what caught the mutation
        self.assertEqual(after["residual"], 0)
        # the neighbouring detector is unmoved
        self.assertEqual(d6_count(cand), 0)
        # and the un-mutated analyzer is restored
        self.assertEqual(self._verdict(cand, par)[1], an.FAIL)


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
        self.assertEqual(res["d_direct_net"], 4)
        self.assertEqual(res["d_schedule_net"], 4)
        self.assertEqual(res["schedule_windfall_net"], 4)
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
        self.assertEqual(run["gdep_natural"], 1)
        self.assertEqual(run["wdr_natural"], 1)
        self.assertEqual(run["net_bank_flow_natural"], 0)
        self.assertEqual(run["gdep_opponent"], 2)
        self.assertEqual(run["wdr_opponent"], 0)
        self.assertEqual(run["net_bank_flow_opponent"], 2)
        self.assertEqual(run["gdep_total"], 3)
        self.assertEqual(run["wdr_total"], 1)
        self.assertEqual(run["net_bank_flow_total"], 2)
        # the per-run conservation identity is on NET, so it closes here even
        # though gross deposits exceed the terminal-score change
        self.assertEqual(run["terminal_score"] - run["initial_score"], 2)
        self.assertEqual(run["residual"], 0)

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
                + res["d_baseline_net"] + res["d_unknown_net"]
                - res["d_train"], name)
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
        self.assertEqual(res["candidate"]["residual"], 0)
        self.assertEqual(res["candidate"]["gdep_total"], 1)
        self.assertEqual(res["candidate"]["net_bank_flow_total"], 0)
        self.assertNotEqual(res["d_production_gross"], res["d_schedule_net"])


class TestD1BoundMetricNamesStateGrossOrNet(unittest.TestCase):
    """Ruling D1 change 4: the unqualified name is no longer sufficient."""

    def _bound(self, metric):
        spec = dict(fx.TEST_BOUND_WINDFALL)
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

    def test_an_ambiguous_metric_makes_the_aggregate_gate_unready(self):
        """REVISION 3: a bound is consumed by the aggregate, not the pair."""
        cand, par = fx.fixture_05_indirect_only()
        row = an.analyze_pair(cand, par, pair_id="d1-ambiguous-metric")
        report = an.aggregate_report(
            [row], bound=self._bound("mean_schedule_windfall"),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertIn("bound_metric_ambiguous_gross_or_net",
                      report["aggregate_unready_reasons"])


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
        res = an.analyze_pair(cand, par)
        self.assert_fails_closed(res, "deposit_withdrawal_split")

        run = res["candidate"]
        # the old tie-break banked one `ours` atom and withdrew one `baseline`
        # atom. REVISION 3 (review I30R2-4): the split itself is not
        # identifiable, so the gross COUNTS are unobservable -- they are
        # `None` with a feasible interval, not a chosen endpoint.
        self.assertFalse(run["gross_identifiable"])
        for c in ledger.SOURCE_CLASSES:
            self.assertIsNone(run["gdep_" + c], c)
            self.assertIsNone(run["wdr_" + c], c)
        self.assertEqual(run["gdep_total_interval"], [0, 1])
        self.assertEqual(run["wdr_total_interval"], [0, 1])
        self.assertEqual(run["gdep_interval_ours"], [0, 1])
        self.assertEqual(run["wdr_interval_baseline"], [0, 1])
        # ... while the unknown mass cancels exactly, so the ruling's
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
        res = an.analyze_pair(cand, par)
        self.assert_fails_closed(res, "deposit_withdrawal_split")

        run = res["candidate"]
        # REVISION 3: two feasible splits (deposit 1 / deposit 2), so the
        # gross counts are an interval and every gross class term is `None`
        self.assertFalse(run["gross_identifiable"])
        self.assertIsNone(run["gdep_ours"])
        self.assertIsNone(run["gdep_natural"])
        self.assertIsNone(run["gdep_unknown"])
        self.assertEqual(run["gdep_total_interval"], [1, 2])
        self.assertEqual(run["wdr_total_interval"], [0, 1])
        self.assertEqual(run["net_bank_flow_total"], 1)
        self.assertEqual(res["residual"], 0)

    def test_deposit_unit_assignment_across_two_units_is_unknown(self):
        cand, par = fx.fixture_a2b_deposit_unit_assignment()
        res = an.analyze_pair(cand, par)
        self.assert_fails_closed(res, "deposit_unit_assignment")

        run = res["candidate"]
        # the deposit COUNT is forced (one banana); which unit's banana it was
        # is not, and the two units carry different classes
        self.assertEqual(run["gdep_ours"], 0)
        self.assertEqual(run["gdep_natural"], 0)
        self.assertEqual(run["gdep_unknown"], 1)
        self.assertEqual(run["net_bank_flow_unknown"], 1)
        self.assertEqual(res["residual"], 0)
        self.assertEqual(res["d_opp"], 1)

    def test_cancelling_unknown_deposit_and_withdrawal_still_fails_closed(self):
        """D_UNKNOWN_NET == 0 is not evidence of complete provenance."""
        cand, par = fx.fixture_a6_cancelling_unknown_flow()
        res = an.analyze_pair(cand, par)
        run = res["candidate"]

        # nothing here is ambiguous -- every allocation is forced
        self.assertEqual(run["identifiable"], True, run["ambiguities"])
        self.assertNotIn("non_identifiable_attribution",
                         res["unready_reasons"])
        # ... and the unknown mass cancels exactly
        self.assertEqual(run["gdep_unknown"], 1)
        self.assertEqual(run["wdr_unknown"], 1)
        self.assertEqual(run["net_bank_flow_unknown"], 0)
        self.assertEqual(res["d_unknown_net"], 0)
        self.assertEqual(res["d_unknown_gross"], 1)
        self.assertEqual(res["residual"], 0)
        self.assertEqual(res["d_opp"], 0)
        # so only the gross unknown-provenance clause can catch it
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("unknown_provenance", res["unready_reasons"])

    def test_a_plant_seed_at_a_bank_cell_does_not_trip_the_gate(self):
        """The fail-closed rule must not fire on an explained decrease."""
        cand, par = fx.fixture_a7_seed_and_deposit_at_one_bank_cell()
        res = an.analyze_pair(cand, par)
        run = res["candidate"]

        self.assertEqual(run["identifiable"], True, run["ambiguities"])
        self.assertEqual(run["plant_events"], 1)
        self.assertEqual(run["gdep_ours"], 1)
        self.assertEqual(run["gdep_unknown"], 0)
        self.assertEqual(run["unknown_atoms"], 0)
        self.assertEqual(res["d_direct_net"], 1)
        self.assertEqual(res["d_direct_gross"], 1)
        self.assertEqual(res["d_schedule_net"], 0)
        self.assertEqual(res["d_opp"], 1)
        self.assertEqual(res["residual"], 0)
        self.assertNotIn("non_identifiable_attribution",
                         res["unready_reasons"])
        self.assertNotIn("unknown_provenance", res["unready_reasons"])

    def test_class_swap_pair_is_indistinguishable_so_both_are_unknown(self):
        """Two hidden histories, one observable transition, two labels."""
        results = {}
        for order in ("ours_first", "opponent_first"):
            cand, par = fx.fixture_a3_class_swap(order)
            results[order] = an.analyze_pair(cand, par)

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
        res = an.analyze_pair(cand, par)
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
            res = an.analyze_pair(cand, par)
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
        before = an.analyze_pair(
            *fx.fixture_a1_same_turn_deposit_withdrawal())
        self.assertEqual(before["status"], an.GATE_UNREADY)

        saved = self._revert_tie_break()
        try:
            after = an.analyze_pair(
                *fx.fixture_a1_same_turn_deposit_withdrawal())
        finally:
            self._restore(saved)

        # the old behaviour: a confident, unprovable split. The withdrawn
        # atom is the opponent's OPENING BANK STOCK, so revision 3 charges it
        # to `baseline` where revision 2 charged it to `natural`
        # (review I30R2-5).
        self.assertEqual(after["candidate"]["gdep_ours"], 1)
        self.assertEqual(after["candidate"]["wdr_baseline"], 1)
        self.assertEqual(after["candidate"]["wdr_natural"], 0)
        self.assertEqual(after["d_direct_net"], 1)
        self.assertEqual(after["d_baseline_net"], -1)
        self.assertEqual(after["d_schedule_net"], 0)
        # with terminal score, net flow and residual all still correct
        self.assertEqual(after["d_opp"], 0)
        self.assertEqual(after["residual"], 0)
        self.assertNotIn("non_identifiable_attribution",
                         after["unready_reasons"])
        # and the fix is restored
        self.assertEqual(
            an.analyze_pair(
                *fx.fixture_a1_same_turn_deposit_withdrawal())["status"],
            an.GATE_UNREADY)

    def test_reverted_tie_break_reopens_the_class_swap(self):
        saved = self._revert_tie_break()
        try:
            a = an.analyze_pair(*fx.fixture_a3_class_swap("ours_first"))
            b = an.analyze_pair(*fx.fixture_a3_class_swap("opponent_first"))
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
        saved = self._revert_tie_break()
        try:
            after = an.analyze_pair(*fx.fixture_a2_multi_source_deposit())
        finally:
            self._restore(saved)
        self.assertEqual(after["candidate"]["gdep_ours"], 1)
        self.assertEqual(after["candidate"]["gdep_natural"], 1)
        self.assertEqual(after["candidate"]["gdep_unknown"], 0)
        self.assertEqual(after["residual"], 0)

    def test_reverted_tie_break_reopens_unit_assignment(self):
        saved = self._revert_tie_break()
        try:
            after = an.analyze_pair(
                *fx.fixture_a2b_deposit_unit_assignment())
        finally:
            self._restore(saved)
        # unit-id order silently declares the lower-id unit the depositor
        self.assertEqual(after["candidate"]["gdep_ours"], 1)
        self.assertEqual(after["candidate"]["gdep_unknown"], 0)
        self.assertEqual(after["candidate"]["lost_natural"], 1)
        self.assertEqual(after["d_direct_net"], 1)
        self.assertEqual(after["d_opp"], 1)
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
                 "fixture_a6_cancelling_unknown_flow",
                 "fixture_a7_seed_and_deposit_at_one_bank_cell",
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


class TestNoPassWithoutAVerifiedOwnerDecision(unittest.TestCase):
    """No PASS may be emitted without an owner decision that VERIFIES.

    Revision 3 (review I30R2-3): the decision is a blob on a pinned ref that
    names the bound and predates the observation, not a string in the bound.
    """

    def test_no_fixture_in_the_corpus_can_produce_pass(self):
        bound = an.Bound(fx.TEST_BOUND_WINDFALL)
        results = []
        for name in sorted(n for n in dir(fx) if n.startswith("fixture_")):
            cand, par = getattr(fx, name)()
            res = an.analyze_pair(cand, par,
                                  self_pair=name.startswith(("fixture_01",
                                                             "fixture_11")),
                                  pair_id=name)
            self.assertNotEqual(res["status"], an.PASS, name)
            self.assertNotEqual(res["status"], an.FAIL, name)
            results.append(res)
        report = an.aggregate_report(results, bound=bound,
                                     observed_utc=fx.OBSERVED_UTC)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertEqual(report["aggregate_sub_status"],
                         an.MEASURED_UNTHRESHOLDED)

    def test_the_production_corpus_is_gate_unready_end_to_end(self):
        """MEASURED: the shipped `main()` path, with the PRODUCTION authority.

        No owner decision exists on the authoritative ref, so the corpus this
        implementation actually emits can only be GATE_UNREADY.
        """
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            report_path = os.path.join(tmp, "report.json")
            self.assertEqual(
                an.main(["--report", report_path,
                         "--ledger-dir", os.path.join(tmp, "ledgers")]), 0)
            with open(report_path) as fh:
                report = json.load(fh)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertFalse(report["owner_decision"]["verified"])
        self.assertIn("owner_decision_unresolved",
                      report["owner_decision"]["reasons"])
        self.assertNotIn(an.PASS, report["statuses"])
        self.assertNotIn(an.FAIL, report["statuses"])


# ==========================================================================
# Revision 3 -- the ten blocking machine-contract defects of
#   chatgpt_1/i30-revision-2-review-2026-08-08.md
#   (sha256 2be671a34a24010d00d5f7fb8c1ce3953bffe6475bee86d05e32e2fed61abdbc,
#    blob at origin/agent/chatgpt_1)
#
# One RED class per defect. Each class fails BEFORE the revision-3
# implementation and passes after it; the recorded failing output is
# i30/red-evidence-r3-2026-08-09.txt.
# ==========================================================================

REVIEW = "chatgpt_1/i30-revision-2-review-2026-08-08.md"


def _rows(*names):
    """Analyzed rows for fixture names, with no bound anywhere (defect 1)."""
    out = []
    for name in names:
        cand, par = getattr(fx, name)()
        out.append(an.analyze_pair(cand, par, pair_id=name))
    return out


class TestR3D1BoundsAreEvaluatedOverTheirPopulation(unittest.TestCase):
    """I30R2-1: `mean_*` must be a population mean, evaluated once."""

    def test_analyze_pair_emits_no_value_verdict_at_all(self):
        cand, par = fx.fixture_05_indirect_only()
        res = an.analyze_pair(cand, par)
        # a pair is an accounting/evaluability row, never a value verdict
        self.assertEqual(res["status"], an.MEASURED, res.get("unready_reasons"))
        for gone in ("bound", "bound_metric_value", "bound_satisfied",
                     "sub_status"):
            self.assertNotIn(gone, res,
                             "%s: %r is an aggregate concern" % (REVIEW, gone))

    def test_analyze_pair_refuses_a_bound_argument(self):
        cand, par = fx.fixture_05_indirect_only()
        with self.assertRaises(TypeError):
            an.analyze_pair(cand, par, bound=an.Bound(fx.TEST_BOUND_WINDFALL))

    def test_the_population_named_by_the_bound_selects_the_rows(self):
        rows = _rows("fixture_03_no_banana_activation",
                     "fixture_05_indirect_only")
        for population, expected in (("all_pairs", 2), ("banana_active", 1)):
            spec = dict(fx.TEST_BOUND_WINDFALL, population=population)
            report = an.aggregate_report(rows, bound=an.Bound(spec))
            ev = report["bound_evaluation"]
            self.assertEqual(ev["population"], population)
            self.assertEqual(ev["population_pairs"], expected, population)

    def test_the_metric_is_the_exact_population_mean(self):
        # windfall_net: fixture_05 == 3, fixture_04 == 0 -> mean 3/2
        rows = _rows("fixture_05_indirect_only", "fixture_04_direct_theft")
        report = an.aggregate_report(
            rows, bound=an.Bound(dict(fx.TEST_BOUND_WINDFALL,
                                      population="all_pairs")))
        ev = report["bound_evaluation"]
        self.assertEqual(ev["metric"], "mean_schedule_windfall_net")
        self.assertEqual(ev["metric_value_exact"], "3/2")
        self.assertEqual(ev["metric_numerator"], 3)
        self.assertEqual(ev["metric_denominator"], 2)
        # ... and it is NOT any single pair's value
        self.assertNotIn(ev["metric_value_exact"], ("3", "0"))

    def test_an_unsupported_population_is_rejected_before_evaluation(self):
        bound = an.Bound(dict(fx.TEST_BOUND_WINDFALL, population="whatever"))
        self.assertFalse(bound.valid)
        self.assertIn("bound_population_unsupported", bound.invalid_reasons)

    def test_a_stale_bound_schema_version_is_rejected(self):
        bound = an.Bound(dict(fx.TEST_BOUND_WINDFALL, schema_version=1))
        self.assertFalse(bound.valid)
        self.assertIn("bound_schema_version_unsupported", bound.invalid_reasons)

    def test_a_per_pair_metric_name_may_not_masquerade_as_a_mean(self):
        # `max_per_pair_*` is a separate, separately named family
        self.assertIn("max_per_pair_schedule_windfall_net",
                      an.SUPPORTED_METRICS)
        self.assertEqual(an.SUPPORTED_METRICS[
            "max_per_pair_schedule_windfall_net"]["reducer"], "max")
        self.assertEqual(an.SUPPORTED_METRICS[
            "mean_schedule_windfall_net"]["reducer"], "mean")


class TestR3D2AggregateVerdictPrecedence(unittest.TestCase):
    """I30R2-2: `FAIL` and the empty corpus must never become `PASS`."""

    def test_an_empty_corpus_is_gate_unready(self):
        report = an.aggregate_report(
            [], bound=fx.owner_verified_bound(), authority=fx.test_authority(),
            observed_utc=fx.OBSERVED_UTC)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertIn("population_empty", report["aggregate_unready_reasons"])

    def test_a_failed_pair_row_propagates_to_aggregate_fail(self):
        rows = _rows("fixture_05_indirect_only")
        rows[0]["status"] = an.FAIL          # a pair-level hard limit
        # threshold 100 is SATISFIED, so only the pair row can fail the corpus
        report = an.aggregate_report(
            rows, bound=fx.owner_verified_bound(threshold=100),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        self.assertEqual(report["aggregate_status"], an.FAIL)
        self.assertEqual(report["aggregate_fail_reasons"], ["pair_fail"])

    def test_an_exceeded_owner_bound_is_exactly_fail(self):
        # every pair instrument-valid, one value condition violated
        rows = _rows("fixture_05_indirect_only")
        report = an.aggregate_report(
            rows, bound=fx.owner_verified_bound(),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        self.assertEqual([r["status"] for r in rows], [an.MEASURED])
        self.assertEqual(report["aggregate_status"], an.FAIL)
        self.assertIn("bound_exceeded", report["aggregate_fail_reasons"])

    def test_a_satisfied_owner_bound_is_pass(self):
        rows = _rows("fixture_05_indirect_only")
        report = an.aggregate_report(
            rows, bound=fx.owner_verified_bound(threshold=100),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        self.assertEqual(report["aggregate_status"], an.PASS)

    def test_one_unready_row_dominates_a_violated_bound(self):
        rows = _rows("fixture_05_indirect_only", "fixture_13_nonzero_residual")
        self.assertEqual(rows[1]["status"], an.GATE_UNREADY)
        report = an.aggregate_report(
            rows, bound=fx.owner_verified_bound(),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertIn("pair_gate_unready", report["aggregate_unready_reasons"])

    def test_the_old_blocking_only_rule_can_no_longer_pass_a_failed_corpus(self):
        rows = _rows("fixture_05_indirect_only")
        rows[0]["status"] = an.FAIL
        report = an.aggregate_report(
            rows, bound=fx.owner_verified_bound(threshold=100),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        self.assertNotEqual(report["aggregate_status"], an.PASS)
        self.assertEqual(report["aggregate_status"], an.FAIL)


class TestR3D3OwnerFreezeIsVerifiedNotDeclared(unittest.TestCase):
    """I30R2-3: a string may not manufacture authority."""

    def _report(self, bound, authority=None, observed_utc=None):
        return an.aggregate_report(_rows("fixture_05_indirect_only"),
                                   bound=bound, authority=authority,
                                   observed_utc=observed_utc)

    def test_the_self_declared_string_is_rejected_outright(self):
        bound = an.Bound(dict(fx.TEST_BOUND_WINDFALL,
                              provenance="owner_frozen"))
        self.assertFalse(bound.valid)
        self.assertIn("self_declared_owner_provenance_rejected",
                      bound.invalid_reasons)
        report = self._report(bound, fx.test_authority(), fx.OBSERVED_UTC)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)

    def test_without_an_authority_nothing_is_owner_frozen(self):
        report = self._report(fx.owner_verified_bound())
        self.assertFalse(report["owner_decision"]["verified"])
        self.assertIn("owner_authority_absent",
                      report["owner_decision"]["reasons"])
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)

    def test_the_blob_must_be_the_bytes_at_the_pinned_path(self):
        authority = fx.test_authority(corrupt=True)
        report = self._report(fx.owner_verified_bound(), authority,
                              fx.OBSERVED_UTC)
        self.assertIn("owner_decision_blob_mismatch",
                      report["owner_decision"]["reasons"])
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)

    def test_the_decision_must_pin_the_exact_bound_sha(self):
        # same authority, same decision pointer, but the bound was EDITED
        # after the decision was frozen
        bound = fx.tampered_bound(threshold=7)
        report = self._report(bound, fx.test_authority(), fx.OBSERVED_UTC)
        self.assertIn("owner_decision_bound_sha_mismatch",
                      report["owner_decision"]["reasons"])
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)

    def test_the_decision_must_predate_the_observation(self):
        report = self._report(fx.owner_verified_bound(), fx.test_authority(),
                              observed_utc="2020-01-01T00:00:00Z")
        self.assertIn("owner_decision_not_frozen_before_observation",
                      report["owner_decision"]["reasons"])
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)

    def test_the_decision_must_be_authored_by_the_authority(self):
        authority = fx.test_authority(authority_id="somebody-else")
        report = self._report(fx.owner_verified_bound(), authority,
                              fx.OBSERVED_UTC)
        self.assertIn("owner_decision_authority_mismatch",
                      report["owner_decision"]["reasons"])

    def test_an_unowned_bound_never_produces_a_production_fail(self):
        """The still-open D2/D3 deviation: an unratified threshold may not
        block a candidate."""
        report = self._report(an.Bound(fx.TEST_BOUND_WINDFALL))   # test_fixture
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertEqual(report["aggregate_sub_status"],
                         an.MEASURED_UNTHRESHOLDED)
        self.assertNotEqual(report["aggregate_status"], an.FAIL)
        # the arithmetic is still reported, explicitly as non-production
        self.assertEqual(report["unratified_bound_evaluation"]["status"],
                         an.NON_PRODUCTION_MEASUREMENT)
        self.assertFalse(
            report["unratified_bound_evaluation"]["bound_satisfied"])

    def test_the_git_ref_authority_resolves_a_real_frozen_blob(self):
        """MEASURED: the authority really reads a blob from a pinned ref."""
        authority = an.GitRefAuthority(fx.REPO_ROOT,
                                       "origin/agent/chatgpt_1", "chatgpt_1")
        blob = authority.resolve(REVIEW)
        self.assertIsNotNone(blob, "the review blob must resolve")
        self.assertEqual(
            ledger.sha256_bytes(blob),
            "2be671a34a24010d00d5f7fb8c1ce3953bffe6475bee86d05e32e2fed61abdbc")
        self.assertIsNone(authority.resolve("no/such/path.json"))

    def test_no_production_owner_decision_exists(self):
        """MEASURED: the production authority resolves nothing, so the
        production aggregate can only be GATE_UNREADY."""
        authority = an.production_authority(fx.REPO_ROOT)
        self.assertIsNone(authority.resolve(an.PRODUCTION_DECISION_PATH))
        report = self._report(fx.owner_verified_bound(), authority,
                              fx.OBSERVED_UTC)
        self.assertIn("owner_decision_unresolved",
                      report["owner_decision"]["reasons"])
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)


class TestR3D4AmbiguousGrossIsAnIntervalNotAPoint(unittest.TestCase):
    """I30R2-4: a deterministic endpoint of an interval is still a tie-break."""

    def test_the_ambiguous_split_reports_null_totals_and_the_interval(self):
        cand, _ = fx.fixture_a1_same_turn_deposit_withdrawal()
        run = cand.ledger.to_json()
        self.assertFalse(run["gross_identifiable"])
        self.assertIsNone(run["gdep_total"])
        self.assertIsNone(run["wdr_total"])
        self.assertEqual(run["gdep_total_interval"], [0, 1])
        self.assertEqual(run["wdr_total_interval"], [0, 1])
        for c in ledger.SOURCE_CLASSES:
            self.assertIsNone(run["gdep_" + c], c)
            self.assertIsNone(run["wdr_" + c], c)
            self.assertIsNone(run["dep_" + c], c)

    def test_net_bank_flow_stays_exact_under_the_same_ambiguity(self):
        cand, _ = fx.fixture_a1_same_turn_deposit_withdrawal()
        run = cand.ledger.to_json()
        self.assertEqual(run["net_bank_flow_total"], 0)
        self.assertEqual(run["residual"], 0)
        for c in ledger.SOURCE_CLASSES:
            self.assertIsInstance(run["net_bank_flow_" + c], int, c)

    def test_a_second_ambiguous_fixture_reports_its_own_interval(self):
        cand, _ = fx.fixture_a2_multi_source_deposit()
        run = cand.ledger.to_json()
        self.assertEqual(run["gdep_total_interval"], [1, 2])
        self.assertEqual(run["wdr_total_interval"], [0, 1])
        self.assertEqual(run["net_bank_flow_total"], 1)
        self.assertIsNone(run["gdep_total"])

    def test_pair_gross_deltas_are_null_when_either_side_is_ambiguous(self):
        cand, par = fx.fixture_a1_same_turn_deposit_withdrawal()
        res = an.analyze_pair(cand, par)
        for key in ("d_direct_gross", "d_production_gross", "d_unknown_gross"):
            self.assertIsNone(res[key], key)
        # the parent is static and neither feasible split moves an
        # opponent- or natural-classed atom, so PRODUCTION gross is exactly
        # zero on both sides even though the totals are not identifiable
        self.assertEqual(res["d_production_gross_interval"], [0, 0])
        self.assertEqual(res["d_direct_gross_interval"], [0, 1])
        self.assertEqual(res["status"], an.GATE_UNREADY)

    def test_the_aggregate_refuses_to_mean_a_non_identifiable_point(self):
        rows = _rows("fixture_a1_same_turn_deposit_withdrawal")
        report = an.aggregate_report(
            rows, bound=fx.owner_verified_bound(
                metric="mean_production_gross"),
            authority=fx.test_authority(), observed_utc=fx.OBSERVED_UTC)
        self.assertEqual(report["aggregate_status"], an.GATE_UNREADY)
        self.assertIsNone(report["bound_evaluation"]["metric_value_exact"])
        self.assertIn("metric_not_identifiable",
                      report["bound_evaluation"]["reasons"])

    def test_class_only_ambiguity_keeps_the_gross_counts_exact(self):
        """The class swap is undetermined in CLASS, not in COUNT."""
        cand, _ = fx.fixture_a3_class_swap("ours_first")
        run = cand.ledger.to_json()
        self.assertTrue(run["gross_identifiable"])
        self.assertEqual(run["gdep_total"], 1)
        self.assertEqual(run["gdep_unknown"], 1)
        self.assertEqual(run["gdep_ours"], 0)
        self.assertEqual(run["gdep_total_interval"], [1, 1])


class TestR3D5BaselineStockIsNotProduction(unittest.TestCase):
    """I30R2-5: recycled initial stock may not masquerade as production."""

    def test_baseline_is_its_own_source_class(self):
        self.assertIn("baseline", ledger.SOURCE_CLASSES)
        self.assertNotIn("baseline", ledger.PRODUCTION_CLASSES)

    def test_initial_bank_and_carry_atoms_are_baseline_not_natural(self):
        cand, _ = fx.fixture_baseline_stock_recycling()
        run = cand.ledger.to_json()
        self.assertEqual(run["gdep_baseline"], 1)
        self.assertEqual(run["wdr_baseline"], 1)
        self.assertEqual(run["gdep_natural"], 0)
        self.assertEqual(run["gdep_opponent"], 0)

    def test_withdrawing_and_redepositing_baseline_stock_is_zero_production(self):
        cand, par = fx.fixture_baseline_stock_recycling()
        res = an.analyze_pair(cand, par)
        self.assertEqual(res["d_production_gross"], 0,
                         "%s: bank cycling is not production" % REVIEW)
        self.assertEqual(res["d_direct_gross"], 0)
        self.assertEqual(res["d_gdep_baseline"], 1)
        self.assertEqual(res["d_opp"], 0)

    def test_baseline_net_stays_inside_the_exact_identity(self):
        cand, par = fx.fixture_baseline_stock_recycling()
        res = an.analyze_pair(cand, par)
        self.assertEqual(
            res["d_opp"],
            res["d_direct_net"] + res["d_schedule_net"] + res["d_baseline_net"]
            + res["d_unknown_net"] - res["d_train"])
        self.assertEqual(res["residual"], 0)

    def test_schedule_net_excludes_baseline(self):
        cand, par = fx.fixture_baseline_stock_recycling()
        res = an.analyze_pair(cand, par)
        self.assertEqual(res["d_schedule_net"], 0)
        self.assertEqual(res["schedule_windfall_net"], 0)


class TestR3D6ContentIdentityIsDerivedNotTrusted(unittest.TestCase):
    """I30R2-6: `setdefault` let a caller declare a false world."""

    def test_derived_hashes_are_never_overridden_by_the_caller(self):
        cand, _ = fx.fixture_01_exact_self_pair()
        lied = ledger.RunRecord(
            "liar", cand.transcript_text, cand.commands_text,
            identity=dict(cand.identity, map_sha256="f" * 64),
            execution=fx.execution_block(cand.commands_text))
        self.assertNotEqual(lied.identity["map_sha256"], "f" * 64)
        self.assertEqual(lied.identity["map_sha256"],
                         lied.derived_identity["map_sha256"])
        self.assertIn("map_sha256", lied.identity_pin_mismatches)

    def test_derived_and_externally_pinned_identity_are_separated(self):
        cand, _ = fx.fixture_01_exact_self_pair()
        self.assertEqual(sorted(cand.derived_identity),
                         ["command_stream_sha256", "initial_state_sha256",
                          "map_sha256", "transcript_sha256"])
        self.assertIn("engine_sha256", cand.pinned_identity)
        self.assertNotIn("engine_sha256", cand.derived_identity)

    def test_two_different_worlds_declaring_one_hash_are_gate_unready(self):
        cand, par = fx.fixture_lying_identity_pair()
        # both callers assert the same map/transcript hashes ...
        self.assertEqual(par.identity_pin_mismatches, [])
        self.assertNotEqual(cand.transcript_text, par.transcript_text)
        res = an.analyze_pair(cand, par, self_pair=True)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("identity_pin_mismatch", res["unready_reasons"])
        self.assertIn("transcript_sha256", cand.identity_pin_mismatches)

    def test_the_pair_check_compares_derived_content_not_declarations(self):
        cand, par = fx.fixture_lying_identity_pair()
        res = an.analyze_pair(cand, par, self_pair=True)
        self.assertFalse(res["pair_identity"]["valid"])
        self.assertIn("transcript_sha256", res["pair_identity"]["mismatched"])


class TestR3D7ActivationCoversEveryFrozenCause(unittest.TestCase):
    """I30R2-7: an incomplete detector may not fabricate NOT_APPLICABLE."""

    def test_the_contract_enumerates_every_frozen_cause(self):
        self.assertEqual(sorted(an.ACTIVATION_CAUSES),
                         sorted(["banana_command", "own_banana_plant",
                                 "banana_harvest", "banana_chop",
                                 "banana_banking", "controller_state",
                                 "integration_seam"]))
        self.assertGreaterEqual(an.ACTIVATION_CONTRACT_VERSION, 2)

    def test_each_frozen_cause_has_an_activating_fixture(self):
        for cause, name in fx.ACTIVATION_CAUSE_FIXTURES.items():
            cand, par = getattr(fx, name)()
            act = an.detect_activation(cand, par)
            self.assertTrue(act["banana_active"], cause)
            self.assertIn(cause, act["activation_causes"], cause)

    def test_state_events_not_command_strings_carry_the_evidence(self):
        cand, par = getattr(fx, fx.ACTIVATION_CAUSE_FIXTURES["banana_harvest"])()
        act = an.detect_activation(cand, par)
        self.assertEqual(act["banana_command_delta"], [])
        self.assertTrue(act["banana_harvest_delta"])

    def test_an_unrelated_command_divergence_is_not_activation(self):
        cand, par = fx.fixture_03_no_banana_activation()
        act = an.detect_activation(cand, par)
        self.assertEqual(act["activation_causes"], [])
        self.assertIsNotNone(act["first_divergence_turn"])
        self.assertEqual(an.analyze_pair(cand, par)["status"],
                         an.NOT_APPLICABLE)

    def test_a_claimed_telemetry_mechanism_without_telemetry_is_unready(self):
        cand, par = fx.fixture_claimed_controller_state_without_telemetry()
        res = an.analyze_pair(cand, par)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("activation_telemetry_unbound", res["unready_reasons"])
        self.assertNotEqual(res["status"], an.NOT_APPLICABLE)


class TestR3D8CommandExecutionValidityGate(unittest.TestCase):
    """I30R2-8: the panel referee silently discarded TRAIN and MINE."""

    def test_a_record_without_an_execution_block_is_unready(self):
        cand, par = fx.fixture_05_indirect_only()
        bare = ledger.RunRecord("bare", cand.transcript_text,
                                cand.commands_text, identity=cand.identity)
        self.assertFalse(bare.execution.valid)
        self.assertIn("execution_validity_absent", bare.execution.reasons)
        res = an.analyze_pair(bare, par)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("input_execution_validity", res["unready_reasons"])

    def test_the_discarded_train_trace_is_rejected(self):
        """The m040 class: 182 emitted TRAIN commands, zero spawns, and a
        referee whose verb manifest never implemented TRAIN."""
        cand, par = fx.fixture_m040_discarded_train()
        self.assertGreaterEqual(
            cand.execution.to_json()["commands_emitted"]
            - cand.execution.to_json()["commands_executed"], 1)
        res = an.analyze_pair(cand, par)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("input_execution_validity", res["unready_reasons"])
        self.assertIn("commands_emitted_not_all_executed",
                      res["candidate_execution"]["reasons"])
        self.assertIn("verb_outside_referee_manifest",
                      res["candidate_execution"]["reasons"])

    def test_the_gate_runs_before_any_ledger_analysis(self):
        cand, par = fx.fixture_m040_discarded_train()
        res = an.analyze_pair(cand, par)
        self.assertIsNone(res["candidate"])
        self.assertIsNone(res["schedule_windfall_net"])
        self.assertTrue(res["counted_in_denominator"])

    def test_an_unsupported_command_event_is_rejected(self):
        cand, par = fx.fixture_unsupported_command_event()
        res = an.analyze_pair(cand, par)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("unsupported_command_events",
                      res["candidate_execution"]["reasons"])

    def test_the_referee_and_engine_identity_must_match_across_the_pair(self):
        cand, par = fx.fixture_referee_version_skew()
        res = an.analyze_pair(cand, par)
        self.assertEqual(res["status"], an.GATE_UNREADY)
        self.assertIn("referee_sha256", res["pair_identity"]["mismatched"])

    def test_the_execution_flag_is_the_harness_declaration_not_an_inference(self):
        block = fx.execution_block("WAIT\n")
        for field in ("execution_status", "commands_emitted",
                      "commands_executed", "unsupported_command_events",
                      "malformed_command_events", "verb_manifest",
                      "verb_manifest_sha256", "referee_sha256",
                      "engine_sha256", "instrument_version",
                      "corpus_version"):
            self.assertIn(field, block, field)


class TestR3D9ProvenanceClosureAndRawLedgers(unittest.TestCase):
    """I30R2-9: a reviewer must be able to reproduce an attribution."""

    def test_the_manifest_closes_over_every_input_class(self):
        manifest = an.provenance_manifest(fx.REPO_ROOT)
        for key in ("i30_ledger.py", "i30_analyzer.py", "i30_fixtures.py",
                    "test_i30_invariant.py", "trace_detectors.py",
                    "spec:chatgpt_1/schedule-opponent-production-invariant"
                    "-spec-2026-08-08.md",
                    "ruling:chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md",
                    "review:" + REVIEW,
                    "engine:rust/src/game/engine.rs",
                    "python_version", "platform", "command_protocol_sha256"):
            self.assertIn(key, manifest, key)
        self.assertEqual(
            manifest["ruling:chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md"],
            "4439b38b7d645aedca36e347387976032331184e582986e38b25985ae641ef5e")
        self.assertEqual(manifest["engine:rust/src/game/engine.rs"],
                         "7c240abfcfdf678993960fe73440735a19f934596c9651bdf"
                         "915e2902f78fb05")

    def test_each_pair_binds_its_raw_ledger_hash(self):
        rows = _rows("fixture_05_indirect_only")
        self.assertEqual(rows[0]["candidate_ledger_sha256"],
                         ledger.sha256_text(ledger.canonical_json(
                             rows[0]["candidate"])))
        self.assertIn("parent_ledger_sha256", rows[0])

    def test_the_aggregate_binds_every_per_pair_result_hash(self):
        rows = _rows("fixture_05_indirect_only",
                     "fixture_06_natural_opportunity")
        report = an.aggregate_report(rows)
        self.assertEqual(len(report["pair_result_sha256"]), 2)
        for row in rows:
            self.assertIn(row["pair_id"], report["pair_result_sha256"])

    def test_raw_ledgers_are_written_with_immutable_paths_and_shas(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            report = an.main(["--report", os.path.join(tmp, "r.json"),
                              "--ledger-dir", os.path.join(tmp, "ledgers")])
            self.assertEqual(report, 0)
            with open(os.path.join(tmp, "r.json")) as fh:
                out = json.load(fh)
        entries = out["raw_ledger_index"]
        self.assertTrue(entries)
        for run_id, entry in entries.items():
            self.assertTrue(entry["path"].endswith(".json"), run_id)
            self.assertEqual(len(entry["sha256"]), 64, run_id)


class TestR3D10MutationRunnerIsReproducible(unittest.TestCase):
    """I30R2-10: a text report is not an executable mutation experiment."""

    RUNNER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "i30", "i30_mutation_runner.py")
    MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "i30", "mutation-manifest-r3-2026-08-09.json")

    def test_the_runner_and_the_patch_manifest_are_committed(self):
        self.assertTrue(os.path.exists(self.RUNNER), self.RUNNER)
        self.assertTrue(os.path.exists(self.MANIFEST), self.MANIFEST)

    def test_every_mutation_declares_an_exact_preimage_and_replacement(self):
        with open(self.MANIFEST) as fh:
            manifest = json.load(fh)
        self.assertGreaterEqual(len(manifest["mutations"]), 10)
        for m in manifest["mutations"]:
            for field in ("id", "defect", "target", "preimage", "replacement",
                          "expected_catcher"):
                self.assertIn(field, m, m.get("id"))
            self.assertNotEqual(m["preimage"], m["replacement"], m["id"])

    def test_every_preimage_occurs_exactly_once_in_its_target(self):
        with open(self.MANIFEST) as fh:
            manifest = json.load(fh)
        here = os.path.dirname(os.path.abspath(__file__))
        for m in manifest["mutations"]:
            for patch in [m] + list(m.get("extra_patches", [])):
                with open(os.path.join(here, patch["target"])) as fh:
                    text = fh.read()
                self.assertEqual(text.count(patch["preimage"]), 1,
                                 "%s: preimage must be unique in %s"
                                 % (m["id"], patch["target"]))

    def test_the_manifest_pins_the_sha_of_every_mutated_file(self):
        with open(self.MANIFEST) as fh:
            manifest = json.load(fh)
        here = os.path.dirname(os.path.abspath(__file__))
        for target, sha in manifest["target_sha256"].items():
            with open(os.path.join(here, target), "rb") as fh:
                self.assertEqual(ledger.sha256_bytes(fh.read()), sha, target)

if __name__ == "__main__":
    unittest.main()
