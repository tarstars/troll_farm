"""The audit's 47-branch tallies must be derived, and the check must be able to fail.

`chatgpt_1`'s bite-test audit r2 (blocker 5): the branch ledger and its headline
counts were hand-maintained. The audit calls them "counted from the table
above" — true when written, silently false after any edit.

`render_branch_ledger.py --check` closes that. These tests hold it to the
standard this suite already applies elsewhere: **the guard is demonstrated
failing on really-perturbed data, not asserted in prose.**

Run:  python3 -m unittest test_branch_ledger
"""
from __future__ import annotations

import copy
import json
import os
import unittest
from unittest import mock

import render_branch_ledger as rbl

HERE = os.path.dirname(os.path.abspath(__file__))


def _doc() -> dict:
    with open(rbl.LEDGER, encoding="utf-8") as fh:
        return json.load(fh)


class BranchLedger(unittest.TestCase):
    def test_the_ledger_holds_exactly_the_47_rows_the_audit_publishes(self):
        self.assertEqual(len(_doc()["branches"]), 47)

    def test_the_audit_prose_matches_the_derived_tallies(self):
        """Control: without this passing, the failure tests below prove nothing."""
        self.assertEqual(rbl.check(_doc()), 0)

    def test_every_row_classifies_on_all_four_axes(self):
        for b in _doc()["branches"]:
            for _, key, order in rbl.AXES:
                self.assertIn(b[key], order,
                              "%s: %s=%r is off its declared axis"
                              % (b["branch"][:40], key, b.get(key)))

    def test_check_fails_when_the_data_moves_away_from_the_prose(self):
        """Flip one row's implementation validity: 11/22 becomes 10/23 and the
        audit's published 11 `PINNED` / 22 `NO_FIXTURE` must stop matching."""
        doc = copy.deepcopy(_doc())
        row = next(b for b in doc["branches"] if b["impl_validity"] == "PINNED")
        row["impl_validity"] = "NO_FIXTURE"
        self.assertEqual(rbl.check(doc), 2,
                         "moving a row off PINNED must be caught")

    def test_check_fails_when_a_row_is_dropped(self):
        doc = copy.deepcopy(_doc())
        doc["branches"].pop()
        self.assertEqual(rbl.check(doc), 2,
                         "46 rows must not satisfy a '47 branch rows' claim")

    def test_check_fails_when_the_audit_prose_moves_away_from_the_data(self):
        """The other direction: the document drifts, the data does not."""
        with open(rbl.AUDIT, encoding="utf-8") as fh:
            text = fh.read()
        tampered = text.replace("12 `PINNED`", "13 `PINNED`", 1)
        self.assertNotEqual(tampered, text, "precondition: the tally is present")
        with mock.patch("builtins.open", mock.mock_open(read_data=tampered)):
            self.assertEqual(rbl.check(_doc_cached), 2)

    def test_an_axis_value_outside_its_declared_set_is_refused(self):
        doc = copy.deepcopy(_doc())
        doc["branches"][0]["truth_validity"] = "PROBABLY_FINE"
        with self.assertRaises(SystemExit):
            rbl.tallies(doc["branches"])

    def test_the_rendered_table_is_a_projection_not_a_transcription(self):
        out = rbl.render(_doc())
        self.assertIn("47 branch rows", out)
        self.assertIn("22 of 47 branches have no fixture at all", out)
        for b in _doc()["branches"]:
            self.assertIn(b["branch"], out)


# `check` re-reads the audit from disk, so the prose-drift test needs a doc
# captured before `open` is patched.
_doc_cached = _doc()


if __name__ == "__main__":
    unittest.main()
