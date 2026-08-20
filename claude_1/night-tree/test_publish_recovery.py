#!/usr/bin/env python3
"""The publish path: the crash that killed the 2026-08-20 night at 15:06Z.

The runner appends to a ledger the coordinator also edits by hand. At 15:06Z
the A3 publish hit a non-fast-forward push, its single `pull --rebase` retry
conflicted on the ledger, the second push was still rejected, and the
RuntimeError went uncaught: the service died with a half-finished rebase in the
working tree and NO halt block in the ledger.

Two defences, tested here:
  1. `merge=union` on the night ledgers, so an append-vs-append conflict
     resolves itself. Verified against REAL git in a scratch repository,
     reproducing the exact 15:06Z collision.
  2. `git_publish` retries three times, aborts any rebase it cannot settle, and
     a publish failure now HALTs fail-closed instead of crashing.

    python3 claude_1/night-tree/test_publish_recovery.py
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]


def _load():
    spec = importlib.util.spec_from_file_location(
        "night_runner_pub", REPO / "cgauto/night_runner.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


nr = _load()


class FakeProc:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


class RecordingRun:
    """Stands in for night_runner.run, scripting return codes per git verb."""

    def __init__(self, script=None):
        self.calls: list[list[str]] = []
        self.script = script or {}

    def __call__(self, cmd, timeout=180):
        self.calls.append(cmd)
        key = " ".join(cmd[1:3]) if len(cmd) > 2 else " ".join(cmd[1:])
        seq = self.script.get(key)
        if isinstance(seq, list):
            return seq.pop(0) if seq else FakeProc(0)
        return seq or FakeProc(0)

    def verbs(self):
        return [" ".join(c[1:4]) for c in self.calls]


class TestGitPublishRetry(unittest.TestCase):
    def setUp(self):
        self.orig = nr.run

    def tearDown(self):
        nr.run = self.orig

    def test_happy_path_pushes_branch_then_main(self):
        rec = RecordingRun()
        nr.run = rec
        nr.git_publish([pathlib.Path("s.json")], "msg")
        self.assertIn("push origin agent/local_claude_1", rec.verbs())
        self.assertIn("push origin agent/local_claude_1:main", rec.verbs())
        self.assertNotIn("pull --rebase origin", rec.verbs())

    def test_one_rejected_push_is_rebased_and_retried(self):
        rec = RecordingRun({"push origin": [FakeProc(1, err="non-fast-forward"),
                                            FakeProc(0), FakeProc(0)]})
        nr.run = rec
        nr.git_publish([pathlib.Path("s.json")], "msg")
        self.assertIn("pull --rebase origin", rec.verbs())
        self.assertIn("push origin agent/local_claude_1:main", rec.verbs())

    def test_three_rejected_pushes_raise_and_never_touch_main(self):
        rec = RecordingRun({"push origin": [FakeProc(1)] * 4})
        nr.run = rec
        with self.assertRaises(RuntimeError) as ctx:
            nr.git_publish([pathlib.Path("s.json")], "msg")
        self.assertIn("3x", str(ctx.exception))
        self.assertNotIn("push origin agent/local_claude_1:main", rec.verbs())
        self.assertEqual(rec.verbs().count("push origin agent/local_claude_1"), 3)

    def test_an_unsettleable_rebase_is_aborted_not_left_behind(self):
        """The 15:06Z tree was left mid-rebase; that must never happen again."""
        rec = RecordingRun({"push origin": [FakeProc(1)] * 4,
                            "pull --rebase": FakeProc(1, out="CONFLICT")})
        nr.run = rec
        with self.assertRaises(RuntimeError) as ctx:
            nr.git_publish([pathlib.Path("s.json")], "msg")
        self.assertIn("rebase aborted", str(ctx.exception))
        self.assertIn("rebase --abort", " ".join(" ".join(c) for c in rec.calls))


class TestHaltOnPublishFailure(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="halt-"))
        self.orig = nr.run

    def tearDown(self):
        nr.run = self.orig
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_halt_writes_the_block_and_does_not_push_when_publishing_failed(self):
        rec = RecordingRun()
        nr.run = rec
        sp, lg = self.tmp / "s.json", self.tmp / "l.md"
        sp.write_text("{}")
        lg.write_text("# ledger\n")
        with self.assertRaises(SystemExit) as ctx:
            nr.halt(sp, lg, {}, "publish failed: boom", publish=False)
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("**HALT", lg.read_text())
        self.assertIn("publish failed: boom", lg.read_text())
        self.assertEqual(json.loads(sp.read_text())["halted"],
                         "publish failed: boom")
        self.assertEqual([c[1] for c in rec.calls], ["add", "commit"])

    def test_ordinary_halt_still_publishes(self):
        rec = RecordingRun()
        nr.run = rec
        sp, lg = self.tmp / "s.json", self.tmp / "l.md"
        sp.write_text("{}")
        lg.write_text("# ledger\n")
        with self.assertRaises(SystemExit):
            nr.halt(sp, lg, {}, "submit FAILED")
        self.assertIn("push origin agent/local_claude_1", rec.verbs())


class TestUnionMergeAgainstRealGit(unittest.TestCase):
    """Reproduce the 15:06Z collision in a scratch repo, with and without the
    union driver. A .gitattributes line nobody has seen resolve a real conflict
    is a claim, not a defence."""

    ROWS = ("| A3 | A | 13:08:47Z | 41167365 | 6642046 | 15:06:19Z | 160 | "
            "23.4 | 28/176 |\n- B3 swap 15:06:22Z: accepted (night_runner)\n")
    ADDENDUM = ("\n## PRE-REGISTERED ADDENDUM (owner-requested)\n\nThe verdict "
                "report additionally carries the composed comparison.\n")
    LEDGER = "local_claude_1/door1-night-2026-08-20.md"

    def _git(self, wd, *args, check=True):
        p = subprocess.run(["git", *args], cwd=wd, capture_output=True, text=True)
        if check:
            self.assertEqual(p.returncode, 0, f"{args}: {p.stderr}")
        return p

    def _collide(self, attributes: str):
        """Coordinator appends upstream, runner appends locally, runner rebases."""
        root = pathlib.Path(tempfile.mkdtemp(prefix="union-"))
        up, wk = root / "upstream", root / "work"
        self._git(root, "init", "-q", "--bare", str(up))
        self._git(root, "clone", "-q", str(up), str(wk))
        self._git(wk, "config", "user.email", "t@example.com")
        self._git(wk, "config", "user.name", "t")
        (wk / "local_claude_1").mkdir(parents=True)
        (wk / self.LEDGER).write_text("# ledger\n\n| A2 | ... |\n")
        if attributes:
            (wk / ".gitattributes").write_text(attributes)
            self._git(wk, "add", ".gitattributes")
        self._git(wk, "add", self.LEDGER)
        self._git(wk, "commit", "-qm", "base")
        self._git(wk, "push", "-q", "origin", "HEAD:refs/heads/main")
        self._git(root, "--git-dir", str(up), "symbolic-ref", "HEAD",
                  "refs/heads/main")

        # the coordinator, from a second clone: appends the addendum upstream
        co = root / "coord"
        self._git(root, "clone", "-q", str(up), str(co))
        self._git(co, "config", "user.email", "c@example.com")
        self._git(co, "config", "user.name", "c")
        (co / self.LEDGER).write_text((co / self.LEDGER).read_text() + self.ADDENDUM)
        self._git(co, "commit", "-qam", "addendum")
        self._git(co, "push", "-q", "origin", "HEAD:main")

        # the runner: appends its rows, commits, push is rejected, rebases
        (wk / self.LEDGER).write_text((wk / self.LEDGER).read_text() + self.ROWS)
        self._git(wk, "commit", "-qam", "A3 read")
        push = self._git(wk, "push", "origin", "HEAD:main", check=False)
        self.assertNotEqual(push.returncode, 0, "the collision must be real")
        pull = self._git(wk, "pull", "--rebase", "-q", "origin", "main", check=False)
        return root, wk, pull

    def test_without_the_union_driver_the_rebase_conflicts(self):
        root, wk, pull = self._collide(attributes="")
        try:
            self.assertNotEqual(pull.returncode, 0)
            self.assertIn("<<<<<<<", (wk / self.LEDGER).read_text())
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_with_the_union_driver_both_appends_survive(self):
        root, wk, pull = self._collide(
            attributes="local_claude_1/door1-night-*.md merge=union\n")
        try:
            self.assertEqual(pull.returncode, 0, pull.stdout + pull.stderr)
            body = (wk / self.LEDGER).read_text()
            self.assertNotIn("<<<<<<<", body)
            self.assertIn("PRE-REGISTERED ADDENDUM", body)   # coordinator's
            self.assertIn("| A3 |", body)                    # runner's
            self.assertIn("B3 swap", body)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_the_repo_actually_carries_those_attribute_lines(self):
        attrs = (REPO / ".gitattributes").read_text()
        self.assertIn("local_claude_1/door1-night-*.md merge=union", attrs)
        self.assertIn("local_claude_1/door1-vs-old-*.md merge=union", attrs)
        check = subprocess.run(
            ["git", "check-attr", "merge", "--",
             "local_claude_1/door1-vs-old-2026-08-20.md"],
            cwd=REPO, capture_output=True, text=True)
        self.assertIn("merge: union", check.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
