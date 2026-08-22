#!/usr/bin/env python3
"""Dry-run verification of night_runner's owner-approved post-B5 decision tree.

Runs the REAL main() loop against synthetic completed states with the arena,
the submitter and git stubbed out, so every branch is exercised end to end
without touching the ladder or the remote. Also validates the generated owner
morning sheet with the REAL transport validators (inbox_sweep.validate_v2 plus
lint_outbox's four extra gates), because a message the runner cannot publish is
a message the owner never reads.

    python3 claude_1/night-tree/test_post_b5_tree.py     # exit 0 = all green
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import shutil
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, REPO / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


nr = _load("night_runner", "cgauto/night_runner.py")
import inbox_sweep          # noqa: E402
import lint_outbox          # noqa: E402


class Slept(Exception):
    """The loop reached its poll sleep — i.e. it is still running."""


def completed_state(diff: float, n: int = 5) -> dict:
    """A session-2 state with all 10 marks read, every pair equal to `diff`."""
    plan, reads, subs = [], [], []
    for i in range(1, n + 1):
        for arm, label in (("A", f"A{i}"), ("B", f"B{i}")):
            plan.append({"label": label, "arm": arm})
            subs.append({"at": f"2026-08-20T0{i}:00:00+00:00",
                         "id": 41000000 + len(subs), "arm": arm})
            score = 23.0 if arm == "A" else round(23.0 - diff, 2)
            reads.append({"label": label, "rank": 30, "total": 176,
                          "league": "Legend", "score": score,
                          "agent_id": "6600000", "battles": 160,
                          "read_at": "01:00:00Z"})
    return {"arms": {"A": {"label": "A challenger", "source": "a.rs",
                           "sha256": "a" * 64},
                     "B": {"label": "B champion", "source": "b.rs",
                           "sha256": "b" * 64}},
            "plan": plan, "submissions": subs, "reads": reads}


class Harness:
    """Runs main() with the arena, submitter, git and lint stubbed."""

    def __init__(self, state: dict, pending: bool = False, once: bool = True):
        # `pending`: the final mark is submitted but not yet read, so main()
        # takes the real read path and lands on the block-complete branch.
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="night-tree-"))
        self.state = state
        self.pending = pending          # True: last mark not yet read
        self.published: list[list[str]] = []
        self.commits: list[str] = []
        self.submits: list[dict] = []
        self.sheet_lint_rc = 0
        self.once = once
        self.slept = 0

    def run(self) -> dict:
        st = json.loads(json.dumps(self.state))
        dropped = None
        if self.pending:
            dropped = st["reads"][-1]
            st["reads"] = st["reads"][:-1]
        sp = self.tmp / "state.json"
        lg = self.tmp / "ledger.md"
        sp.write_text(json.dumps(st, indent=1))
        lg.write_text("# ledger\n")
        orig = {k: getattr(nr, k) for k in
                ("submit", "read_arena", "git_publish", "run", "utcnow")}

        def fake_submit(arm):
            self.submits.append(arm)
            return {"submission_id": 41999000 + len(self.submits),
                    "accepted": True}

        def fake_read():
            # the mature read of the pending mark, at its planned score
            return {"rank": 30, "total": 176, "league": "Legend",
                    "score": dropped["score"] if dropped else 23.0,
                    "agent_id": "6600001", "battles": 160,
                    "read_at": "01:20:00Z"}

        def fake_publish(paths, msg):
            self.published.append([str(p) for p in paths])
            self.commits.append(msg)

        class FakeProc:
            def __init__(self, rc): self.returncode = rc; self.stdout = ""; self.stderr = ""

        def fake_run(cmd, timeout=180):
            if "lint_outbox.py" in " ".join(cmd):
                return FakeProc(self.sheet_lint_rc)
            return FakeProc(0)

        nr.submit, nr.read_arena, nr.git_publish, nr.run = (
            fake_submit, fake_read, fake_publish, fake_run)
        argv = sys.argv[:]
        cwd = os.getcwd()
        os.chdir(self.tmp)
        sys.argv = ["night_runner.py", "--state", str(sp), "--ledger",
                    str(lg)] + (["--once"] if self.once else [])
        orig_sleep = nr.time.sleep

        def fake_sleep(_seconds):
            self.slept += 1
            raise Slept()

        nr.time.sleep = fake_sleep
        rc = None
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = nr.main()
        except Slept:
            rc = "slept"
        finally:
            nr.time.sleep = orig_sleep
            os.chdir(cwd)
            sys.argv = argv
            for k, v in orig.items():
                setattr(nr, k, v)
        return {"rc": rc, "state": json.loads(sp.read_text()),
                "ledger": lg.read_text(), "dir": self.tmp}

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestBranchFunction(unittest.TestCase):
    """The tree is one pure function; its boundaries are the whole ruling."""

    def test_boundaries(self):
        for mean, want in [(0.0, "session3"), (0.999, "session3"),
                           (1.0, "extension"), (1.3149, "extension"),
                           (1.315, "session3"), (2.0, "session3"),
                           (-1.2, "extension"), (-0.5, "session3"),
                           (-1.315, "session3")]:
            self.assertEqual(nr.post_b5_branch(mean), want, f"mean={mean}")

    def test_the_bar_follows_the_block_size(self):
        """Pre-registered: 1.315 at n=5, 0.930 at n=10 (ledger, both literals)."""
        self.assertEqual(nr.bar_for(5), 1.315)
        self.assertEqual(nr.bar_for(10), 0.930)
        self.assertAlmostEqual(nr.bar_for(5), 1.96 * 1.5 / 5 ** 0.5, places=3)
        self.assertAlmostEqual(nr.bar_for(10), 1.96 * 1.5 / 10 ** 0.5, places=3)

    def test_at_n10_the_band_is_empty_so_no_second_extension_fires(self):
        """bar(10) < floor, so every n=10 outcome is immaterial or a winner."""
        self.assertLess(nr.bar_for(10), nr.MATERIALITY_FLOOR)
        for mean in (0.5, 0.95, 1.0, 1.2, 1.5, -1.1, -0.99):
            self.assertEqual(nr.post_b5_branch(mean, 10), "session3", mean)

    def test_a_ten_pair_block_is_graded_against_its_own_bar(self):
        """The whole point: 1.0 is a WINNER at n=10 and was not at n=5."""
        st = completed_state(1.0, n=10)
        self.assertIn("WINNER: challenger", nr.verdict_block(st))
        self.assertIn("winner bar 0.93 (n=10)", nr.verdict_block(st))
        st5 = completed_state(1.0, n=5)
        self.assertIn("BETWEEN floor and bar", nr.verdict_block(st5))

    def test_band_matches_the_verdict_block_wording(self):
        """The tree and the printed verdict must never disagree."""
        for diff in (0.4, 1.2, 2.0):
            st = completed_state(diff)
            block = nr.verdict_block(st)
            stats = nr.pair_stats(st)
            branch = nr.post_b5_branch(stats["mean"], stats["n"])
            between = "BETWEEN floor and bar" in block
            self.assertEqual(between, branch == "extension", block)


class TestExtensionBranch(unittest.TestCase):
    def setUp(self):
        self.h = Harness(completed_state(1.2), pending=True)
        self.out = self.h.run()

    def tearDown(self):
        self.h.cleanup()

    def test_plan_extended_by_five_pairs_same_arms(self):
        plan = self.out["state"]["plan"]
        self.assertEqual(len(plan), 20)
        self.assertEqual([p["label"] for p in plan[10:]],
                         ["A6", "B6", "A7", "B7", "A8", "B8", "A9", "B9",
                          "A10", "B10"])
        self.assertEqual([p["arm"] for p in plan[10:]], list("ABABABABAB"))

    def test_next_arm_submitted_so_the_loop_can_continue(self):
        self.assertEqual(len(self.out["state"]["submissions"]), 11)
        self.assertEqual(self.out["state"]["submissions"][-1]["arm"], "A")
        self.assertEqual(len(self.h.submits), 1)
        self.assertEqual(self.h.submits[0]["sha256"], "a" * 64)

    def test_ledger_carries_verdict_then_extension_then_swap(self):
        led = self.out["ledger"]
        self.assertIn("BLOCK COMPLETE", led)
        self.assertIn("BETWEEN floor and bar", led)
        self.assertIn("EXTENSION FIRES", led)
        self.assertIn("A6..B10", led)
        self.assertIn("A6 swap", led)
        self.assertLess(led.index("BLOCK COMPLETE"), led.index("EXTENSION FIRES"))

    def test_no_session3_files_created(self):
        self.assertFalse((self.out["dir"] / nr.SESSION3_LEDGER).exists())
        self.assertFalse((self.out["dir"] / nr.SESSION3_STATE).exists())

    def test_commit_message_names_the_branch(self):
        self.assertIn("EXTENSION A6..B10", self.h.commits[-1])


class TestSession3Branch(unittest.TestCase):
    def setUp(self):
        self.h = Harness(completed_state(2.0), pending=True)   # winner
        self.out = self.h.run()
        self.s3 = json.loads(
            (self.out["dir"] / nr.SESSION3_STATE).read_text())

    def tearDown(self):
        self.h.cleanup()

    def test_session2_plan_untouched(self):
        self.assertEqual(len(self.out["state"]["plan"]), 10)
        self.assertEqual(len(self.out["state"]["submissions"]), 10)

    def test_fresh_state_is_a_five_pair_block_against_the_very_old_resident(self):
        self.assertEqual([p["label"] for p in self.s3["plan"]],
                         ["A1", "B1", "A2", "B2", "A3", "B3", "A4", "B4",
                          "A5", "B5"])
        self.assertEqual(self.s3["reads"], [])
        self.assertEqual(
            self.s3["arms"]["B"]["sha256"],
            "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29")
        self.assertEqual(
            self.s3["arms"]["B"]["source"],
            "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs")
        self.assertEqual(
            self.s3["arms"]["A"]["sha256"],
            "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0")

    def test_arm_A_submitted_at_once(self):
        self.assertEqual(len(self.h.submits), 1)
        self.assertEqual(self.h.submits[0]["sha256"][:8], "547fa706")
        self.assertEqual(len(self.s3["submissions"]), 1)
        self.assertEqual(self.s3["submissions"][0]["arm"], "A")

    def test_both_ledgers_are_honest_about_the_switch(self):
        self.assertIn("SESSION 3 OPENED", self.out["ledger"])
        self.assertIn("This ledger is closed", self.out["ledger"])
        new = (self.out["dir"] / nr.SESSION3_LEDGER).read_text()
        self.assertIn("very-old resident", new)
        self.assertIn("A1 swap", new)
        self.assertIn("no point band is claimed", new)
        self.assertIn("bar", new)

    def test_all_four_new_paths_are_published_in_one_commit(self):
        pub = " ".join(self.h.published[-1])
        for frag in ("state.json", "ledger.md", nr.SESSION3_STATE,
                     nr.SESSION3_LEDGER, "coordination/messages/local_claude_1"):
            self.assertIn(frag, pub)

    def test_the_arm_files_named_by_the_card_carry_those_digests(self):
        """Checked as committed blobs on the refs the runner checkout tracks —
        the runner submits from its own checkout, not from mine."""
        import hashlib
        import subprocess
        for ref in ("origin/main", "origin/agent/local_claude_1"):
            for arm in ("A", "B"):
                blob = subprocess.run(
                    ["git", "cat-file", "blob",
                     f"{ref}:{nr.SESSION3_ARMS[arm]['source']}"],
                    cwd=REPO, capture_output=True)
                self.assertEqual(blob.returncode, 0, f"{ref} {arm}")
                self.assertEqual(hashlib.sha256(blob.stdout).hexdigest(),
                                 nr.SESSION3_ARMS[arm]["sha256"],
                                 f"{ref} {arm}")


class TestSession3Continuation(unittest.TestCase):
    """The switch must keep ONE process running against the NEW files.

    Without the rebind the loop re-tests `reads >= plan` on the old, finished
    state, breaks, prints "block complete" and exits — systemd does not restart
    a clean exit, and session 3 would sit submitted and never read. That is the
    failure this test exists to catch.
    """

    def setUp(self):
        self.h = Harness(completed_state(2.0), pending=True, once=False)
        self.out = self.h.run()

    def tearDown(self):
        self.h.cleanup()

    def test_loop_continues_polling_after_the_switch(self):
        self.assertEqual(self.out["rc"], "slept")
        self.assertEqual(self.h.slept, 1)

    def test_it_is_polling_the_new_block_not_the_old_one(self):
        s3 = json.loads((self.out["dir"] / nr.SESSION3_STATE).read_text())
        self.assertEqual(len(s3["submissions"]), 1)
        self.assertEqual(s3["reads"], [])          # nothing read yet
        self.assertEqual(len(self.h.submits), 1)   # and nothing re-submitted


class TestMorningSheet(unittest.TestCase):
    """Published in EITHER branch, and it must survive the real validators."""

    def _sheet(self, diff):
        st = completed_state(diff)
        stats = nr.pair_stats(st)
        branch = nr.post_b5_branch(stats["mean"], stats["n"])
        return nr.morning_sheet(st, branch, "next step note")

    def test_transport_valid_in_both_branches(self):
        refs, per_path = inbox_sweep.scan_authoritative()
        for diff in (1.2, 2.0, 0.3):
            path, body = self._sheet(diff)
            msg = inbox_sweep.Message(path.as_posix(), "worktree", body)
            self.assertTrue(msg.is_v2)
            errs = inbox_sweep.validate_v2(
                msg, set(per_path), {}, set(refs), require_canonical=False)
            self.assertEqual(errs, [], f"diff={diff}: {errs}")
            published = lint_outbox.parse_published_messages(per_path)
            for gate in (lambda m: lint_outbox.wip_limit_errors(m, published, []),
                         lambda m: lint_outbox.evidence_gate_errors(m, set(refs)),
                         lambda m: lint_outbox.cross_task_reference_errors(m, published),
                         lint_outbox.deferral_shape_errors,
                         lambda m: lint_outbox.card_ack_errors(m, published)):
                self.assertEqual(gate(msg), [])

    def test_dual_format_legacy_bullets_present(self):
        _, body = self._sheet(1.2)
        self.assertIn("\n- To: user\n", body)
        self.assertIn("\n- Task: 20260819-osc031-forecast-fix-door1b\n", body)
        self.assertIn("- Requires acknowledgement: no", body)

    def test_filename_kind_matches_the_declared_type(self):
        path, body = self._sheet(1.2)
        self.assertTrue(path.name.endswith("-progress.md"))
        self.assertIn("type: progress", body)
        self.assertIn(f"message_id: {path.as_posix()}", body)
        self.assertNotIn("progress", inbox_sweep.ACK_REQUIRED_KINDS)

    def test_carries_the_verdict_the_composition_and_the_nine_costs(self):
        _, body = self._sheet(1.2)
        self.assertIn("Mean difference **+1.200**", body)
        self.assertIn("Composed distance +2.220**", body)   # 1.02 + 1.20
        for cost in ("m021s0", "m040s1?", "m063s1", "m078s1", "m090s1",
                     "m025s0", "m035s0", "m054s0", "m104s0"):
            self.assertIn(cost, body)
        self.assertIn("SE 0.949", body)     # planning: sqrt(2)*1.5/sqrt(5)
        self.assertIn("bar 1.315 at n=5", body)
        self.assertIn("evidence, not gold", body)

    def test_names_which_branch_fired(self):
        _, ext = self._sheet(1.2)
        self.assertIn("Branch: EXTENSION", ext)
        _, s3 = self._sheet(2.0)
        self.assertIn("Branch: SESSION3", s3)

    def test_a_lint_rejected_sheet_is_never_committed(self):
        h = Harness(completed_state(2.0), pending=True)
        h.sheet_lint_rc = 2
        out = h.run()
        pub = " ".join(h.published[-1])
        self.assertNotIn("coordination/messages", pub)
        self.assertIn("morning sheet NOT published as a message", out["ledger"])
        preserved = list(out["dir"].glob("REJECTED-*progress.md"))
        self.assertEqual(len(preserved), 1, "content must survive")
        h.cleanup()


class TestNoRegressionMidBlock(unittest.TestCase):
    """A mid-block read must behave exactly as it did before the tree."""

    def setUp(self):
        st = completed_state(1.2)
        st["reads"] = st["reads"][:4]
        st["submissions"] = st["submissions"][:5]
        self.h = Harness(st)
        self.out = self.h.run()

    def tearDown(self):
        self.h.cleanup()

    def test_read_recorded_and_next_arm_submitted_no_tree(self):
        self.assertEqual(len(self.out["state"]["reads"]), 5)
        self.assertEqual(len(self.out["state"]["submissions"]), 6)
        self.assertEqual(len(self.out["state"]["plan"]), 10)
        self.assertNotIn("BLOCK COMPLETE", self.out["ledger"])
        self.assertNotIn("EXTENSION", self.out["ledger"])
        self.assertNotIn("SESSION 3", self.out["ledger"])
        self.assertIn("; next arm submitted", self.h.commits[-1])

    def test_only_the_two_original_paths_published(self):
        self.assertEqual(len(self.h.published[-1]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
