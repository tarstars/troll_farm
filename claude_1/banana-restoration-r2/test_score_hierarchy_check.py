#!/usr/bin/env python3
"""Tests for score_hierarchy_check.

Run:  python3 -m unittest claude_1.banana-restoration-r2.test_score_hierarchy_check
or:   cd claude_1/banana-restoration-r2 && python3 -m unittest test_score_hierarchy_check -v

The integration tests against the real subject blob are skipped when the repository
is not reachable, so the unit tests remain runnable anywhere.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import score_hierarchy_check as shc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SUBJECT_REF = "origin/main:cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
SUBJECT_SHA = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"
LEDGER = Path(__file__).resolve().parent / "score-hierarchy-ledger.json"


def _subject_source() -> str | None:
    try:
        return shc.read_from_git(REPO_ROOT, SUBJECT_REF).decode()
    except (FileNotFoundError, OSError, subprocess.SubprocessError):
        return None


SUBJECT_SRC = _subject_source()


# ---------------------------------------------------------------------------


class TestBlanking(unittest.TestCase):
    def test_preserves_length_and_lines(self):
        src = 'let a = 1; // score: 999\nlet b = "score: 7";\n'
        out = shc.blank_comments_and_strings(src)
        self.assertEqual(len(out), len(src))
        self.assertEqual(out.count("\n"), src.count("\n"))

    def test_line_comment_body_removed(self):
        out = shc.blank_comments_and_strings("x; // score: 999\ny;")
        self.assertNotIn("score", out)
        self.assertTrue(out.startswith("x; //"))

    def test_nested_block_comment(self):
        out = shc.blank_comments_and_strings("a /* outer /* score = 1 */ still */ b")
        self.assertNotIn("score", out)
        self.assertIn("a ", out)
        self.assertIn(" b", out)

    def test_string_with_escape(self):
        out = shc.blank_comments_and_strings(r'let s = "a\" score = 2"; z;')
        self.assertNotIn("score", out)
        self.assertIn("z;", out)

    def test_raw_string(self):
        out = shc.blank_comments_and_strings('let s = r#"score = 3"#; z;')
        self.assertNotIn("score", out)
        self.assertIn("z;", out)

    def test_lifetime_not_treated_as_char_literal(self):
        src = "fn f<'a>(x: &'a str) -> &'a str { x }  let c = 'q'; score = 1;"
        out = shc.blank_comments_and_strings(src)
        # the lifetime must not swallow the rest of the line
        self.assertIn("score = 1;", out)
        self.assertIn("&'a str", out)


class TestCensus(unittest.TestCase):
    def test_matches_all_four_operators(self):
        src = "Candidate{score:1.0}\nlet score = 2.0;\nscore += 3.0;\nscore -= 4.0;\n"
        sites = shc.census(src)
        self.assertEqual([s.op for s in sites], [":", "=", "+=", "-="])
        self.assertEqual([s.line for s in sites], [1, 2, 3, 4])

    def test_ignores_prefixed_identifiers(self):
        src = "base_score: 1.0\nconversion_score = 2.0\nlet x = a.score == b.score;\n"
        self.assertEqual(shc.census(src), [])

    def test_field_access_is_a_site(self):
        # `.score =` is a genuine mutation site and must be caught (cf. R:1283).
        sites = shc.census("current.score = 10_000.0;")
        self.assertEqual(len(sites), 1)
        self.assertEqual(sites[0].op, "=")

    def test_ignores_comments_and_strings(self):
        src = '// score = 1\nlet s = "score = 2";\nscore = 3;\n'
        sites = shc.census(src)
        self.assertEqual([s.line for s in sites], [3])

    def test_fingerprint_is_line_number_independent(self):
        a = shc.census("score = 1.0;")[0]
        b = shc.census("\n\nscore  =  1.0;")[0]
        self.assertEqual(a.fingerprint(), b.fingerprint())
        self.assertNotEqual(a.line, b.line)


class TestCensusDiff(unittest.TestCase):
    def setUp(self):
        self.frozen = [s.as_dict() for s in shc.census("score = 1.0;\nscore = 2.0;\n")]

    def test_no_drift(self):
        cur = shc.census("score = 1.0;\nscore = 2.0;\n")
        d = shc.census_diff(cur, self.frozen)
        self.assertEqual(d, {"added": [], "removed": [], "moved": []})

    def test_added(self):
        cur = shc.census("score = 1.0;\nscore = 2.0;\nscore = 3.0;\n")
        d = shc.census_diff(cur, self.frozen)
        self.assertEqual(len(d["added"]), 1)
        self.assertEqual(d["removed"], [])

    def test_removed(self):
        cur = shc.census("score = 1.0;\n")
        d = shc.census_diff(cur, self.frozen)
        self.assertEqual(len(d["removed"]), 1)

    def test_pure_move_reported_separately(self):
        cur = shc.census("\nscore = 1.0;\nscore = 2.0;\n")
        d = shc.census_diff(cur, self.frozen)
        self.assertEqual(d["added"], [])
        self.assertEqual(d["removed"], [])
        self.assertEqual(len(d["moved"]), 2)


class TestCallSites(unittest.TestCase):
    def test_single_call_with_literal(self):
        src = (
            "fn iron_candidates(v:&G,u:&U,base_score:f64)->Vec<C>{ }\n"
            "out.extend(Self::iron_candidates(view,unit,6_100.0));\n"
        )
        rep = shc.call_sites(src, "iron_candidates")
        self.assertEqual(rep.definitions, [1])
        self.assertEqual([c.line for c in rep.calls], [2])
        self.assertEqual(rep.calls[0].literal_args, {2: "6_100.0"})
        self.assertTrue(rep.sound)
        self.assertEqual(rep.status, "OK")

    def test_bare_use_makes_it_inconclusive(self):
        src = "fn f(){}\nlet g = f;\nf();\n"
        rep = shc.call_sites(src, "f")
        self.assertEqual(rep.bare_uses, [2])
        self.assertFalse(rep.sound)
        self.assertEqual(rep.status, "INCONCLUSIVE")

    def test_nested_arguments_split_correctly(self):
        src = "fn f(){}\nf(g(1,2), 3.0, h(a,(b,c)));\n"
        rep = shc.call_sites(src, "f")
        self.assertEqual(rep.calls[0].args, ["g(1,2)", "3.0", "h(a,(b,c))"])
        self.assertEqual(rep.calls[0].literal_args, {1: "3.0"})

    def test_occurrence_in_comment_ignored(self):
        src = "fn f(){}\n// f(1.0);\nf(2.0);\n"
        rep = shc.call_sites(src, "f")
        self.assertEqual([c.line for c in rep.calls], [3])
        self.assertEqual(rep.bare_uses, [])

    def test_prefixed_identifier_not_matched(self):
        src = "fn f(){}\nmy_f(1.0);\nf_two(2.0);\n"
        rep = shc.call_sites(src, "f")
        self.assertEqual(rep.calls, [])
        self.assertEqual(rep.bare_uses, [])

    def test_literal_forms(self):
        src = "fn f(){}\nf(6_000.0, 42, 1e3, 7f64, x)\n"
        rep = shc.call_sites(src, "f")
        self.assertEqual(
            rep.calls[0].literal_args, {0: "6_000.0", 1: "42", 2: "1e3", 3: "7f64"}
        )


class TestInterval(unittest.TestCase):
    def test_parse_open_closed(self):
        i = shc.Interval.parse("(0, 2400]")
        self.assertEqual((i.lo, i.hi, i.lo_closed, i.hi_closed), (0.0, 2400.0, False, True))
        j = shc.Interval.parse("[2, inf)")
        self.assertEqual((j.lo, j.hi, j.lo_closed, j.hi_closed), (2.0, math.inf, True, False))

    def test_infinite_endpoint_is_open(self):
        self.assertFalse(shc.Interval.parse("[2, inf]").hi_closed)

    def test_add_sub(self):
        a = shc.Interval(1, 2)
        b = shc.Interval(10, 20)
        self.assertTrue((a + b).approx_equal(shc.Interval(11, 22)))
        self.assertTrue((a - b).approx_equal(shc.Interval(-19, -8)))

    def test_mul_signs(self):
        a = shc.Interval(-2, 3)
        b = shc.Interval(-5, 7)
        self.assertTrue((a * b).approx_equal(shc.Interval(-15, 21)))

    def test_reciprocal_of_unbounded(self):
        r = shc.Interval.parse("[2, inf)").reciprocal()
        self.assertTrue(r.approx_equal(shc.Interval(0.0, 0.5, False, True)))

    def test_reciprocal_spanning_zero_raises(self):
        with self.assertRaises(shc.IntervalError):
            shc.Interval(-1, 1).reciprocal()

    def test_division_openness_propagates(self):
        # 1000*[1,3] / [2,inf)  ==  (0, 1500]
        got = shc.Interval(1000, 3000) / shc.Interval.parse("[2, inf)")
        self.assertTrue(got.approx_equal(shc.Interval(0.0, 1500.0, False, True)))

    def test_imax_of_two_intervals(self):
        got = shc.Interval(0, 100).imax(shc.Interval(0, 83))
        self.assertTrue(got.approx_equal(shc.Interval(0, 100)))

    def test_clamp_low_dead_and_live(self):
        self.assertTrue(shc.Interval.parse("[2, inf)").clamp_low_is_dead(1))
        self.assertFalse(shc.Interval.parse("[0, 100]").clamp_low_is_dead(1))
        self.assertFalse(shc.Interval.parse("[-83, 100]").clamp_low_is_dead(0))

    def test_clamp_low_is_identity_when_dead(self):
        i = shc.Interval.parse("[2, inf)")
        self.assertTrue(i.clamp_low(1).approx_equal(i))

    def test_clamp_low_raises_floor_when_live(self):
        i = shc.Interval(-5, 10)
        self.assertTrue(i.clamp_low(0).approx_equal(shc.Interval(0, 10)))

    def test_empty_interval_rejected(self):
        with self.assertRaises(shc.IntervalError):
            shc.Interval(5, 4)


# ---------------------------------------------------------------------------
# Correction 5 (chatgpt_1 review B5): interval multiplication endpoint closure.
#
# The defect: ``Interval.__mul__`` closed a product endpoint only when EVERY
# attaining corner was closed (``all``).  An endpoint of a product is attained,
# and therefore included, when ANY attaining corner is included (``any``).  The
# same defect let a zero-width OPEN interval -- the empty set -- be constructed.
#
# Every test in this class FAILS under the pre-correction ``all`` implementation
# and is the mutation pin required by the revision task.
# ---------------------------------------------------------------------------


class TestIntervalMultiplicationEndpointClosure(unittest.TestCase):
    def test_lower_endpoint_closed_when_any_corner_attains_it_closed(self):
        # [0, 1] * (0, 1] == [0, 1].  0 is attained at the closed corner
        # (lo=0, hi=1) -> 0*1 = 0, so the lower endpoint is IN the product.
        # `all` marks it open because the corner (0, 0) is open.
        got = shc.Interval(0, 1, True, True) * shc.Interval(0, 1, False, True)
        self.assertTrue(got.approx_equal(shc.Interval(0, 1, True, True)), str(got))

    def test_upper_endpoint_closed_when_any_corner_attains_it_closed(self):
        # [-1, 0] * [-1, 0) : corners (1, closed), (0, open), (0, closed), (0, open).
        # hi = 1 closed; lo = 0 is attained closed at (0 * -1).
        got = shc.Interval(-1, 0, True, True) * shc.Interval(-1, 0, True, False)
        self.assertTrue(got.approx_equal(shc.Interval(0, 1, True, True)), str(got))

    def test_zero_point_times_open_interval_is_the_closed_point_zero(self):
        # The empty-interval half of B5: `all` yields (0, 0), an EMPTY set that
        # the constructor silently accepted, instead of the point {0}.
        got = shc.Interval.point(0) * shc.Interval(0, 1, False, True)
        self.assertTrue(got.approx_equal(shc.Interval.point(0)), str(got))

    def test_open_zero_endpoint_stays_open_when_no_corner_attains_it_closed(self):
        # Guard against over-correcting: (0, 1] * (0, 1] == (0, 1].
        got = shc.Interval(0, 1, False, True) * shc.Interval(0, 1, False, True)
        self.assertTrue(got.approx_equal(shc.Interval(0, 1, False, True)), str(got))

    def test_infinite_endpoint_product_stays_open(self):
        got = shc.Interval.parse("[2, inf)") * shc.Interval(1, 2, True, True)
        self.assertTrue(got.approx_equal(shc.Interval(2, math.inf, True, False)), str(got))

    def test_negative_span_product_closure(self):
        # [-2, 3] * (-5, 7]: lo = -10 attained only at the open corner (-5),
        # hi = 21 attained at a closed corner.
        got = shc.Interval(-2, 3, True, True) * shc.Interval(-5, 7, False, True)
        self.assertTrue(got.approx_equal(shc.Interval(-15, 21, False, True)), str(got))


class TestZeroWidthIntervalRejection(unittest.TestCase):
    def test_zero_width_open_open_is_empty_and_rejected(self):
        with self.assertRaises(shc.IntervalError):
            shc.Interval(0, 0, False, False)

    def test_zero_width_half_open_is_empty_and_rejected(self):
        with self.assertRaises(shc.IntervalError):
            shc.Interval(3, 3, True, False)
        with self.assertRaises(shc.IntervalError):
            shc.Interval(3, 3, False, True)

    def test_zero_width_open_interval_from_parse_is_rejected(self):
        with self.assertRaises(shc.IntervalError):
            shc.Interval.parse("(0, 0)")

    def test_zero_width_closed_interval_is_a_legal_point(self):
        self.assertTrue(shc.Interval(0, 0, True, True).approx_equal(shc.Interval.point(0)))


class TestEvalExpr(unittest.TestCase):
    def test_unbound_variable_raises(self):
        with self.assertRaises(shc.IntervalError):
            shc.eval_expr(["+", "x", 1], {})

    def test_substitute_inlines_derived(self):
        expr = shc.substitute(["/", 1000, "turns"], {"turns": ["max", ["+", "a", 1], 1]})
        self.assertEqual(expr, ["/", 1000, ["max", ["+", "a", 1], 1]])

    def test_variable_occurrence_counting(self):
        self.assertEqual(shc._vars_in(["-", "b", ["+", "t", ["max", "t", 0]]]),
                         ["b", "t", "t"])


class TestRangeModel(unittest.TestCase):
    CHOP = {
        "id": "T-CHOP",
        "site": "R:611",
        "expr": ["+", ["/", ["*", 1000, "wood"], "turns"],
                 ["/", 900, ["+", 1, "opponent_distance"]]],
        "attainable": "(0, 2400]",
        "derived": [{"name": "turns",
                     "expr": ["max", ["+", "travel_turns", "chop_turns", "return_turns", 1], 1]}],
        "inputs": {
            "travel_turns": {"range": "[0, inf)"},
            "chop_turns": {"range": "[1, 100]"},
            "return_turns": {"range": "[0, inf)"},
            "wood": {"range": "[1, 3]"},
            "opponent_distance": {"range": "[0, inf)"},
        },
        "clamps": [{"site": "R:611", "op": "max", "bound": 1, "expect": "DEAD",
                    "operand": ["+", "travel_turns", "chop_turns", "return_turns", 1]}],
    }

    def test_reproduces_2400_and_proves_clamp_dead(self):
        r = shc.range_model_report(self.CHOP)
        self.assertEqual(r["computed"], "(0, 2400]")
        self.assertTrue(r["agrees"])
        self.assertEqual(r["precision"], "NO_REPEATED_VARIABLE_INTERVAL_EVAL")
        self.assertEqual(r["clamps"][0]["verdict"], "DEAD")
        self.assertEqual(r["clamps"][0]["operand_range"], "[2, inf)")

    def test_dropping_the_producer_invariant_reproduces_the_manifest_error(self):
        """Regression test for the exact error the method exists to prevent.

        If ``chop_turns >= 1`` is NOT propagated (i.e. the auditor reads the
        syntactic ``.max(1)`` floor as attainable), ``turns`` becomes ``[1, inf)``
        and the computed bound inflates to the original manifest's ``3900``.

        Note what does NOT change: the clamp is reported DEAD either way, because
        the ``+ 1`` literal alone already forces ``turns >= 1``.  Clamp-deadness is
        therefore NOT the discriminator -- the propagated operand interval is.
        """
        bad = json.loads(json.dumps(self.CHOP))
        bad["inputs"]["chop_turns"]["range"] = "[0, 100]"
        bad.pop("attainable")
        r = shc.range_model_report(bad)
        self.assertEqual(r["computed"], "(0, 3900]")
        self.assertEqual(r["clamps"][0]["operand_range"], "[1, inf)")
        self.assertEqual(r["clamps"][0]["verdict"], "DEAD")

    def test_clamp_deadness_alone_is_not_the_discriminator(self):
        good = shc.range_model_report(self.CHOP)
        self.assertEqual(good["clamps"][0]["verdict"], "DEAD")
        self.assertEqual(good["clamps"][0]["operand_range"], "[2, inf)")
        self.assertEqual(good["computed"], "(0, 2400]")

    def test_mismatched_claim_fails(self):
        bad = json.loads(json.dumps(self.CHOP))
        bad["attainable"] = "(0, 3900]"
        self.assertFalse(shc.range_model_report(bad)["agrees"])

    def test_repeated_variable_is_flagged_over_approx(self):
        model = {
            "id": "T-FRUIT-NAIVE",
            "expr": ["-", 6000, ["+", "travel", ["max", ["-", "ticks", "travel"], 0]]],
            "inputs": {"travel": {"range": "[0, 83]"}, "ticks": {"range": "[0, 100]"}},
        }
        r = shc.range_model_report(model)
        self.assertEqual(r["precision"], "REPEATED_VARIABLE_OVER_APPROX")
        self.assertEqual(r["computed"], "[5817, 6000]")

    def test_single_occurrence_rewrite_is_tighter(self):
        model = {
            "id": "T-FRUIT-EXACT",
            "expr": ["-", 6000, ["max", "ticks", "travel"]],
            "inputs": {"travel": {"range": "[0, 83]"}, "ticks": {"range": "[0, 100]"}},
        }
        r = shc.range_model_report(model)
        self.assertEqual(r["precision"], "NO_REPEATED_VARIABLE_INTERVAL_EVAL")
        self.assertEqual(r["computed"], "[5900, 6000]")


# ---------------------------------------------------------------------------
# Correction 4 (chatgpt_1 review B4): `EXACT` is a lie by vocabulary.
#
# The machine status meant only "no variable token repeats in the expanded
# expression".  It did NOT mean the computed interval is the exact attainable
# set: inputs may be panel assumptions, variables may be correlated by state,
# integrality may remove endpoints, and the site may be unreachable.
# ---------------------------------------------------------------------------


class TestPrecisionVocabulary(unittest.TestCase):
    SINGLE = {
        "id": "T-SINGLE",
        "expr": ["-", 6000, ["max", "ticks", "travel"]],
        "inputs": {"travel": {"range": "[0, 83]", "method": "panel-bounded assumption"},
                   "ticks": {"range": "[0, 100]", "method": "producer-invariant"}},
    }
    REPEATED = {
        "id": "T-REPEATED",
        "expr": ["-", 6000, ["+", "travel", ["max", ["-", "ticks", "travel"], 0]]],
        "inputs": {"travel": {"range": "[0, 83]", "method": "producer-invariant"},
                   "ticks": {"range": "[0, 100]", "method": "producer-invariant"}},
    }

    def test_single_occurrence_status_is_not_named_exact(self):
        r = shc.range_model_report(self.SINGLE)
        self.assertEqual(r["precision"], "NO_REPEATED_VARIABLE_INTERVAL_EVAL")

    def test_repeated_variable_status_is_renamed(self):
        r = shc.range_model_report(self.REPEATED)
        self.assertEqual(r["precision"], "REPEATED_VARIABLE_OVER_APPROX")

    def test_the_token_EXACT_appears_nowhere_in_a_range_report(self):
        for model in (self.SINGLE, self.REPEATED):
            blob = json.dumps(shc.range_model_report(model))
            self.assertNotIn("EXACT", blob, model["id"])

    def test_report_separates_scope_assumption_reachability_and_witness(self):
        r = shc.range_model_report(self.SINGLE)
        for key in ("bound_scope", "assumption_status",
                    "reachability_status", "endpoint_witnessed"):
            self.assertIn(key, r)

    def test_bound_scope_states_upper_sound_lower_unwitnessed(self):
        r = shc.range_model_report(self.SINGLE)
        self.assertEqual(r["bound_scope"], "UPPER_BOUND_SOUND__LOWER_NOT_PROVED_ATTAINABLE")

    def test_assumption_status_flags_a_panel_bounded_input(self):
        r = shc.range_model_report(self.SINGLE)
        self.assertEqual(r["assumption_status"], "ASSUMPTION_DEPENDENT")
        self.assertIn("travel", r["assumption_inputs"])

    def test_assumption_status_clean_when_every_method_is_a_proof_method(self):
        r = shc.range_model_report(self.REPEATED)
        self.assertEqual(r["assumption_status"], "CITED_PROOF_METHODS_ONLY")
        self.assertEqual(r["assumption_inputs"], [])

    def test_reachability_and_witness_default_to_unproved(self):
        r = shc.range_model_report(self.SINGLE)
        self.assertEqual(r["reachability_status"], "UNPROVED")
        self.assertEqual(r["endpoint_witnessed"], "NONE")

    def test_ledger_may_declare_reachability_and_witness_explicitly(self):
        model = dict(self.SINGLE, reachability_status="SITE_GUARD_CHAIN_CITED",
                     endpoint_witnessed="UPPER")
        r = shc.range_model_report(model)
        self.assertEqual(r["reachability_status"], "SITE_GUARD_CHAIN_CITED")
        self.assertEqual(r["endpoint_witnessed"], "UPPER")


# ---------------------------------------------------------------------------
# Correction 6 (chatgpt_1 review B6): textual call-site evidence must not be
# labelled reachability evidence.
# ---------------------------------------------------------------------------


class TestCallSiteVerdictVocabulary(unittest.TestCase):
    SRC = "fn f(v:&G,b:f64){}\nlet c = Candidate{score:1.0};\nf(view, 6_000.0);\n"

    def _ledger(self, claim="one textual call site"):
        return {
            "subject": {"path": "x.rs", "sha256": shc.sha256_bytes(self.SRC.encode())},
            "census": [s.as_dict() for s in shc.census(self.SRC)],
            "bindings": [{"fn": "f", "arg_index": 1, "expect_calls": [3],
                          "expect_literal_args": ["6_000.0"], "claim": claim}],
            "range_models": [],
        }

    def test_one_call_literal_verdict_says_textual(self):
        led = self._ledger()
        rep = shc.run(led, self.SRC, led["subject"]["sha256"], None)
        self.assertEqual(rep["checks"]["bindings"][0]["verdict"],
                         "ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING")

    def test_multiple_call_verdict_says_textual(self):
        led = self._ledger()
        src = self.SRC + "f(view, 3_400.0);\n"
        rep = shc.run(led, src, led["subject"]["sha256"], None)
        self.assertEqual(rep["checks"]["bindings"][0]["verdict"],
                         "MULTIPLE_TEXTUAL_CALL_SITES")

    def test_binding_carries_an_explicit_unproved_reachability_status(self):
        led = self._ledger()
        rep = shc.run(led, self.SRC, led["subject"]["sha256"], None)
        self.assertEqual(rep["checks"]["bindings"][0]["reachability_status"], "UNPROVED")

    def test_validate_ledger_rejects_a_binding_claim_asserting_reachability(self):
        led = self._ledger(claim="one reachable call site, base_score bound to 6_000.0")
        problems = shc.validate_ledger(led)
        self.assertTrue(any("reachab" in p.lower() for p in problems), problems)

    def test_validate_ledger_accepts_a_textual_claim(self):
        led = self._ledger()
        problems = [p for p in shc.validate_ledger(led) if "reachab" in p.lower()]
        self.assertEqual(problems, [])

    def test_a_reachability_asserting_ledger_fails_the_run(self):
        led = self._ledger(claim="one reachable call site")
        rep = shc.run(led, self.SRC, led["subject"]["sha256"], None)
        self.assertFalse(rep["ok"])

    def test_generic_argument_over_split_fails_closed_on_arity(self):
        # Non-blocking review note 3: the splitter does not balance Rust angle
        # brackets, so a generic argument over-splits.  That must surface as a
        # ledger arity/expectation MISMATCH, never as a silent wrong answer.
        src = "fn f(v:&G,b:f64){}\nf(Vec::<A,B>::new(), 6_000.0);\n"
        rep = shc.call_sites(src, "f")
        self.assertGreater(len(rep.calls[0].args), 2)
        led = self._ledger()
        led["bindings"][0]["expect_calls"] = [2]
        out = shc.run(led, src, shc.sha256_bytes(src.encode()), None)
        self.assertFalse(out["checks"]["bindings"][0]["agrees"])


class TestRunDriver(unittest.TestCase):
    SRC = "fn f(v:&G,b:f64){}\nlet c = Candidate{score:1.0};\nf(view, 6_000.0);\n"

    def _ledger(self, src: str) -> dict:
        return {
            "subject": {"path": "x.rs", "sha256": shc.sha256_bytes(src.encode())},
            "census": [s.as_dict() for s in shc.census(src)],
            "bindings": [{"fn": "f", "arg_index": 1, "expect_calls": [3],
                          "expect_literal_args": ["6_000.0"]}],
            "range_models": [],
        }

    def test_clean_run_passes(self):
        led = self._ledger(self.SRC)
        rep = shc.run(led, self.SRC, shc.sha256_bytes(self.SRC.encode()), None)
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["checks"]["bindings"][0]["verdict"],
                         "ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING")

    def test_sha_divergence_fails(self):
        led = self._ledger(self.SRC)
        rep = shc.run(led, self.SRC, "deadbeef", None)
        self.assertFalse(rep["ok"])
        self.assertFalse(rep["checks"]["identity"]["match"])

    def test_new_score_site_fails_census(self):
        led = self._ledger(self.SRC)
        moved = self.SRC + "let d = Candidate{score:2.0};\n"
        rep = shc.run(led, moved, led["subject"]["sha256"], None)
        self.assertFalse(rep["ok"])
        self.assertEqual(len(rep["checks"]["census"]["diff"]["added"]), 1)

    def test_second_call_site_fails_binding(self):
        led = self._ledger(self.SRC)
        moved = self.SRC + "f(view, 3_400.0);\n"
        rep = shc.run(led, moved, led["subject"]["sha256"], None)
        self.assertFalse(rep["ok"])
        self.assertEqual(rep["checks"]["bindings"][0]["verdict"], "MULTIPLE_TEXTUAL_CALL_SITES")

    def test_format_report_does_not_crash(self):
        led = self._ledger(self.SRC)
        rep = shc.run(led, self.SRC, shc.sha256_bytes(self.SRC.encode()), None)
        self.assertIn("overall: PASS", shc.format_report(rep))


@unittest.skipUnless(SUBJECT_SRC is not None, "subject blob not reachable via git")
class TestAgainstRealSubject(unittest.TestCase):
    def test_subject_sha(self):
        self.assertEqual(shc.sha256_bytes(SUBJECT_SRC.encode()), SUBJECT_SHA)

    def test_ledger_passes_end_to_end(self):
        led = json.loads(LEDGER.read_text())
        rep = shc.run(led, SUBJECT_SRC, SUBJECT_SHA, None)
        self.assertTrue(rep["ok"], shc.format_report(rep))

    def test_band_parameter_bindings(self):
        fruit = shc.call_sites(SUBJECT_SRC, "fruit_candidates")
        iron = shc.call_sites(SUBJECT_SRC, "iron_candidates")
        self.assertTrue(fruit.sound and iron.sound)
        self.assertEqual([c.line for c in fruit.calls], [455])
        self.assertEqual([c.line for c in iron.calls], [448])
        self.assertEqual(fruit.calls[0].literal_args[3], "6_000.0")
        self.assertEqual(iron.calls[0].literal_args[2], "6_100.0")

    def test_chop_clamp_is_dead(self):
        led = json.loads(LEDGER.read_text())
        rm1 = next(m for m in led["range_models"] if m["id"] == "RM-1")
        r = shc.range_model_report(rm1)
        self.assertEqual(r["computed"], "(0, 2400]")
        self.assertEqual(r["clamps"][0]["verdict"], "DEAD")

    def test_census_has_no_drift(self):
        led = json.loads(LEDGER.read_text())
        diff = shc.census_diff(shc.census(SUBJECT_SRC), led["census"])
        self.assertEqual(diff, {"added": [], "removed": [], "moved": []})


if __name__ == "__main__":
    unittest.main()
