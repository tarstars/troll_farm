"""What the runner must do when the block it is RUNNING completes.

Twice — 2026-08-21T20:29Z and 2026-08-22T16:04Z — the runner finished a session-3
block, wrote its verdict, and then re-opened an identical session 3 onto the very
files it was running: `open_session3()` rewrote the ledger with a fresh header, so
the final read row and the verdict block were erased BEFORE the commit that would
have published them. They exist in no commit; both verdicts had to be reconstructed
from the state JSON (`local_claude_1/door1-vs-old-block1-verdict-2026-08-22.md`,
`…-pooled-verdict-2026-08-22.md`). A real Arena submission fired each time.

The shipped post-B5 tests never caught it because they run main() against
tmp/state.json and tmp/ledger.md, which never alias SESSION3_STATE/SESSION3_LEDGER.
Session 2 lived on different paths; session 3 did not. These tests use the real
paths, which is the whole point.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]


def _load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, REPO / relpath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


nr = _load("night_runner", "cgauto/night_runner.py")

LEDGER_MARK = "(pretend: the real read log of the live ledger)"


class Slept(Exception):
    """main() reached its poll sleep — i.e. it is still looping."""


def completed_state(pair_diffs, arms=None):
    """A block with every mark submitted and all but the last read."""
    plan, reads, subs = [], [], []
    for i, d in enumerate(pair_diffs, start=1):
        for row in nr.ordered_pair(i):
            label = row["label"]
            plan.append(row)
            subs.append({"at": f"2026-08-22T0{i}:00:00+00:00",
                         "id": 41170000 + len(subs), "arm": row["arm"]})
            score = 23.0 if row["arm"] == "A" else round(23.0 - d, 2)
            reads.append({"label": label, "rank": 30, "total": 176,
                          "league": "Legend", "score": score,
                          "agent_id": "6640000", "battles": 160,
                          "read_at": "01:00:00Z"})
    dropped = reads.pop()
    return {"arms": json.loads(json.dumps(arms or nr.SESSION3_ARMS)),
            "plan": plan, "submissions": subs, "reads": reads}, dropped


def run_completion(tmp_path, pair_diffs, on_session3_paths, arms=None):
    """Drive the real main() to the block-complete branch. Nothing is submitted
    or pushed: the arena, the submitter, git and the lint are stubbed."""
    state, dropped = completed_state(pair_diffs, arms)
    if on_session3_paths:
        sp, lg = tmp_path / nr.SESSION3_STATE, tmp_path / nr.SESSION3_LEDGER
    else:
        sp, lg = tmp_path / "other-state.json", tmp_path / "other-ledger.md"
    sp.parent.mkdir(parents=True, exist_ok=True)
    lg.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(state, indent=1))
    lg.write_text(f"# ledger\n{LEDGER_MARK}\n")
    (tmp_path / nr.MSG_DIR).mkdir(parents=True, exist_ok=True)

    submits, commits = [], []
    orig = {k: getattr(nr, k) for k in ("submit", "read_arena", "git_publish", "run")}

    class FakeProc:
        returncode = 0
        stdout = stderr = ""

    nr.submit = lambda arm: (submits.append(arm),
                             {"submission_id": 41999000 + len(submits)})[1]
    nr.read_arena = lambda: {"rank": 30, "total": 176, "league": "Legend",
                             "score": dropped["score"], "agent_id": "6649999",
                             "battles": 160, "read_at": "20:29:00Z"}
    nr.git_publish = lambda paths, msg: commits.append(msg)
    nr.run = lambda cmd, timeout=180: FakeProc()
    orig_sleep = nr.time.sleep
    nr.time.sleep = lambda _s: (_ for _ in ()).throw(Slept())
    argv, cwd = sys.argv[:], os.getcwd()
    os.chdir(tmp_path)
    sys.argv = ["night_runner.py", "--state", str(sp.relative_to(tmp_path)),
                "--ledger", str(lg.relative_to(tmp_path))]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            rc = nr.main()
    except Slept:
        rc = "still-looping"
    finally:
        nr.time.sleep = orig_sleep
        os.chdir(cwd)
        sys.argv = argv
        for k, v in orig.items():
            setattr(nr, k, v)
    sheets = sorted((tmp_path / nr.MSG_DIR).glob("*.md"))
    return {"rc": rc, "submits": submits, "commits": commits,
            "ledger": lg.read_text(), "state": json.loads(sp.read_text()),
            "sheet": sheets[-1].read_text() if sheets else ""}


def test_completing_the_running_block_does_not_restart_it(tmp_path):
    """The defect, on the real paths: an immaterial finish must STOP."""
    out = run_completion(tmp_path, [0.0, 0.4, 1.9, -0.1, 0.5], on_session3_paths=True)

    assert out["submits"] == [], (
        "a fresh Arena submission fired after the block completed"
    )
    assert out["rc"] != "still-looping", "the runner kept looping after the block"


def test_the_completed_ledger_survives_with_its_verdict(tmp_path):
    """The read log and the verdict must reach the commit, not be overwritten."""
    out = run_completion(tmp_path, [0.0, 0.4, 1.9, -0.1, 0.5], on_session3_paths=True)

    assert LEDGER_MARK in out["ledger"], "the ledger was rewritten from scratch"
    assert "BLOCK COMPLETE" in out["ledger"], "the verdict block is missing"
    assert "IMMATERIAL" in out["ledger"]
    assert out["state"]["reads"], "the completed reads were discarded"


def test_a_winner_also_stops_rather_than_restarting(tmp_path):
    """Not only the immaterial branch: any non-extension finish stops."""
    out = run_completion(tmp_path, [2.0, 2.2, 1.9, 2.1, 2.4], on_session3_paths=True)

    assert out["submits"] == []
    assert LEDGER_MARK in out["ledger"]


def test_a_block_on_other_paths_still_opens_session_three(tmp_path):
    """The owner-approved tree is untouched where it was designed to fire."""
    out = run_completion(tmp_path, [0.0, 0.4, 1.9, -0.1, 0.5], on_session3_paths=False)

    assert len(out["submits"]) == 1, "session 3 no longer opens from a session-2 block"
    assert (tmp_path / nr.SESSION3_LEDGER).exists()


def test_the_extension_branch_is_untouched(tmp_path):
    """A mean between floor and bar still extends, on the running paths."""
    out = run_completion(tmp_path, [1.1, 1.1, 1.1, 1.1, 1.1], on_session3_paths=True)

    assert len(out["submits"]) == 1, "the extension no longer submits its next arm"
    assert "EXTENSION" in out["commits"][-1]
    assert LEDGER_MARK in out["ledger"]


def test_the_owner_sheet_names_the_arms_it_actually_measured(tmp_path):
    """The sheet was hard-titled 'session 2 … vs cure-C resident' on every run."""
    out = run_completion(tmp_path, [0.0, 0.4, 1.9, -0.1, 0.5], on_session3_paths=True)

    assert out["sheet"], "no owner sheet was produced"
    assert "cure-C resident" not in out["sheet"], (
        "the sheet named an arm this block did not measure"
    )
    assert "very-old resident" in out["sheet"]


def test_the_sheet_does_not_compose_a_direct_measurement_with_itself(tmp_path):
    """Adding night 1's +1.02 to a block that IS the direct comparison double-counts."""
    out = run_completion(tmp_path, [0.0, 0.4, 1.9, -0.1, 0.5], on_session3_paths=True)

    assert "Composed distance" not in out["sheet"], (
        "the sheet composed the direct two-generation measurement with night 1"
    )
