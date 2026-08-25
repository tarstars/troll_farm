"""The owner-freeze chronology must be decided by history, not by argv.

`chatgpt_1`'s I-30 revision 3 review (`20260811T235000Z`), trust-root blocker 2:

    owner freeze chronology compares caller-supplied timestamp strings while
    reading a blob from moving `main`; it does not prove that the
    owner-decision commit existed before an immutable observation anchor.

Both halves were true. `verify_owner_decision` compared `frozen_utc` (from the
decision) against `observed_utc` (from `--observed-utc`), and the party being
checked supplied the second one — so any bound could be made to look
frozen-first. `PRODUCTION_AUTHORITY_REF` is `refs/remotes/origin/main`, a
pointer that moves, so resolving a blob through it said nothing about when the
decision existed.

An *anchored* authority now decides chronology by Git ancestry between the
commit that introduced the decision and an immutable observation anchor.
Ancestry rather than committer dates: a date in a Git object is metadata its
author writes and can set to anything; an ancestor edge cannot be forged
without rewriting the descendant.

These tests build a real repository so the ancestry is real, and they are
written to fail on the pre-repair analyzer.

Run:  python3 -m unittest test_i30_chronology_anchor
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i30_analyzer as an  # noqa: E402
import i30_fixtures as fx  # noqa: E402


def _git(repo, *args, **kw):
    return subprocess.run(["git", *args], cwd=repo, check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)


class ChronologyAnchor(unittest.TestCase):
    """A repo whose history is: [decision commit] -> [later commit].

    `earlier` predates the decision; `later` descends from it.
    """

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="i30-chronology-")
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        _git(self.repo, "init", "-q", "-b", "trunk")
        _git(self.repo, "config", "user.email", "i30@test")
        _git(self.repo, "config", "user.name", "i30 test")

        with open(os.path.join(self.repo, "seed.txt"), "w") as fh:
            fh.write("seed\n")
        _git(self.repo, "add", "seed.txt")
        _git(self.repo, "commit", "-qm", "before the decision")
        self.earlier = _git(self.repo, "rev-parse", "HEAD").stdout.decode().strip()

        # the decision the bound points at, byte-for-byte
        self.bound = fx.owner_verified_bound()
        path = self.bound.spec["owner_decision_path"]
        body_sha = path[len(fx.TEST_DECISION_PREFIX):-len(".json")]
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(fx._decision_bytes(body_sha))
        _git(self.repo, "add", path)
        _git(self.repo, "commit", "-qm", "owner freezes the bound")
        self.decision_commit = _git(self.repo, "rev-parse",
                                    "HEAD").stdout.decode().strip()

        with open(os.path.join(self.repo, "later.txt"), "w") as fh:
            fh.write("after\n")
        _git(self.repo, "add", "later.txt")
        _git(self.repo, "commit", "-qm", "results observed here")
        self.later = _git(self.repo, "rev-parse", "HEAD").stdout.decode().strip()

        self.authority = an.GitRefAuthority(self.repo, "trunk",
                                            fx.TEST_AUTHORITY_ID)

    def verify(self, **kw):
        kw.setdefault("observed_utc", fx.OBSERVED_UTC)
        return an.verify_owner_decision(self.bound, self.authority,
                                        kw.pop("observed_utc"), **kw)

    # -- control ---------------------------------------------------------
    def test_a_decision_that_precedes_the_observation_verifies(self):
        """Without this the refusals below could be refusing everything."""
        out = self.verify(observation_anchor=self.later)
        self.assertEqual(out["reasons"], [])
        self.assertTrue(out["verified"])
        self.assertEqual(out["chronology_basis"], "git_ancestry")
        self.assertEqual(out["decision_commit"], self.decision_commit)

    # -- the defect ------------------------------------------------------
    def test_a_decision_made_after_the_observation_is_refused(self):
        """The attack the old clause could not see: the bound is frozen after
        the results were observed. Ancestry catches it; two strings did not."""
        out = self.verify(observation_anchor=self.earlier)
        self.assertFalse(out["verified"])
        self.assertIn("owner_decision_not_ancestor_of_observation",
                      out["reasons"])

    def test_a_late_decision_cannot_be_rescued_by_a_generous_timestamp(self):
        """The heart of blocker 2: the caller supplies `observed_utc`, so under
        the old clause it could always be set late enough to pass. It must now
        buy nothing."""
        out = self.verify(observed_utc="2999-01-01T00:00:00Z",
                          observation_anchor=self.earlier)
        self.assertFalse(out["verified"],
                         "a caller-chosen timestamp must not decide chronology")
        self.assertIn("owner_decision_not_ancestor_of_observation",
                      out["reasons"])

    def test_an_anchored_authority_refuses_to_verify_without_an_anchor(self):
        """Fail closed: no silent fallback to the timestamps in production."""
        out = self.verify(observation_anchor=None)
        self.assertFalse(out["verified"])
        self.assertIn("observation_anchor_absent", out["reasons"])

    def test_an_unknown_anchor_is_refused_rather_than_assumed(self):
        out = self.verify(observation_anchor="0" * 40)
        self.assertFalse(out["verified"])
        self.assertIn("observation_anchor_unresolved", out["reasons"])

    # -- properties of the mechanism -------------------------------------
    def test_the_production_authority_is_anchored(self):
        """If this ever becomes False the whole clause degrades to the old
        caller-supplied comparison, silently."""
        prod = an.production_authority(self.repo)
        self.assertTrue(prod.anchored)
        self.assertTrue(an.GitRefAuthority.anchored)

    def test_a_fixture_authority_is_not_anchored_and_says_so(self):
        out = an.verify_owner_decision(self.bound, fx.test_authority(),
                                       fx.OBSERVED_UTC)
        self.assertEqual(out["chronology_basis"],
                         "declared_timestamps_unanchored")
        self.assertTrue(out["authority"]["anchored"] is False)

    def test_the_report_records_which_basis_decided_it(self):
        """A reader must never have to guess whether a verdict was anchored."""
        out = self.verify(observation_anchor=self.later)
        self.assertIn("chronology_basis", out)
        self.assertIn("observation_anchor", out)
        self.assertIn("decision_commit", out)


if __name__ == "__main__":
    unittest.main()
