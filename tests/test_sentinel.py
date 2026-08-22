"""Tests for the blocking inbox sentinel (scripts/sentinel.py).

Covers the charter's gate-2 control list from
coordination/tasks/20260819-sentinel-wake-on-work.md, each observed firing BOTH
ways where the charter names both directions:

  * a message pushed for the agent -> exit 0 with exactly the new paths;
  * a message for a DIFFERENT agent only -> keeps hanging (no exit 0);
  * keepalive timeout -> exit 2;
  * fetch failure injection -> exit 3 after N;
  * double start -> exit 1, first instance untouched;
  * seen-state byte-identical before/after a full run.

Plus the two rules the reviewer made binding: the sentinel consumes
`inbox_sweep.actionable_set()` and nothing else as its actionability predicate,
and it is READ-ONLY on git (a PATH shim records every git invocation the run
makes, and the test asserts the verb set).
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time

import pytest

from scripts import inbox_sweep, sentinel
from tests.test_inbox_sweep import (  # reuse the transport fixture verbatim
    COORDINATOR,
    ME,
    PEER,
    THIRD,
    TransportRepo,
    publish_deferral_card,
    publish_v2,
    repo,  # noqa: F401  (pytest fixture)
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "sentinel.py"

# The sentinel polls; tests must not. Small but not zero: a 0 interval would
# spin the CPU and hide ordering bugs behind luck.
TICK = "0.2"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def git_shim(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    """A PATH-front `git` that logs its argv and then execs the real git."""
    real_git = subprocess.run(
        ["/bin/bash", "-lc", "command -v git"], capture_output=True, text=True,
        check=True,
    ).stdout.strip()
    assert real_git
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    log = tmp_path / "git-calls.log"
    (shim_dir / "git").write_text(
        "#!/bin/bash\n"
        f'printf "%s\\n" "$*" >> {log}\n'
        f'exec {real_git} "$@"\n',
        encoding="utf-8",
    )
    (shim_dir / "git").chmod(0o755)
    return shim_dir, log


def start(repo: TransportRepo, *args: str, env: dict | None = None
          ) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [sys.executable, str(SCRIPT), "--me", ME, "--interval", TICK, *args],
        cwd=repo.work,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env or dict(os.environ),
    )


def run(repo: TransportRepo, *args: str, timeout: float = 60.0,
        env: dict | None = None) -> subprocess.CompletedProcess[str]:
    proc = start(repo, *args, env=env)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        raise AssertionError(f"sentinel did not exit; stdout={out!r} stderr={err!r}")
    return subprocess.CompletedProcess(proc.args, proc.returncode, out, err)


def pidfile(repo: TransportRepo) -> pathlib.Path:
    return repo.work / ME / ".sentinel.pid"


def is_ready(repo: TransportRepo) -> bool:
    """True once the sentinel has taken its pidfile AND its baseline snapshot.

    Publishing before the baseline is taken would fold the new message INTO the
    baseline, so every "work arrives" test must synchronize on this, not on the
    pidfile alone.
    """
    try:
        return json.loads(pidfile(repo).read_text(encoding="utf-8")).get("ready") is True
    except (OSError, ValueError):
        return False


def wait_for(predicate, timeout: float = 30.0, what: str = "condition") -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise AssertionError(f"timed out waiting for {what}")


# ---------------------------------------------------------------------------
# 1. work arrives -> exit 0 with exactly the triggering paths
# ---------------------------------------------------------------------------

def test_message_for_me_exits_0_with_exactly_the_new_paths(repo):
    proc = start(repo, "--max-lifetime", "60")
    try:
        wait_for(lambda: is_ready(repo), what="the sentinel baseline snapshot")
        path = publish_v2(repo, PEER, "20260821T100000Z", "task-a", "question")
        out, err = proc.communicate(timeout=60)
    except BaseException:
        proc.kill()
        raise
    assert proc.returncode == 0, f"stdout={out!r} stderr={err!r}"
    assert [line for line in out.splitlines() if line.strip()] == [path]


# ---------------------------------------------------------------------------
# 2. the negative control: traffic that is NOT my work must not wake me
# ---------------------------------------------------------------------------

def test_message_for_a_different_agent_keeps_hanging(repo):
    proc = start(repo, "--max-lifetime", "3")
    try:
        wait_for(lambda: is_ready(repo), what="the sentinel baseline snapshot")
        publish_v2(repo, PEER, "20260821T100100Z", "task-b", "question", to=THIRD)
        out, err = proc.communicate(timeout=60)
    except BaseException:
        proc.kill()
        raise
    assert proc.returncode == 2, f"woke on another agent's mail: {out!r} {err!r}"
    assert "coordination/messages" not in out


# ---------------------------------------------------------------------------
# 3. keepalive
# ---------------------------------------------------------------------------

def test_max_lifetime_exits_2_with_no_paths(repo):
    result = run(repo, "--max-lifetime", "2")
    assert result.returncode == 2, result.stderr
    assert "coordination/messages" not in result.stdout


# ---------------------------------------------------------------------------
# 4. fetch failure injection
# ---------------------------------------------------------------------------

def test_consecutive_fetch_failures_exit_3(repo):
    repo._git("remote", "set-url", "origin", str(repo.work / "does-not-exist"))
    result = run(repo, "--max-lifetime", "60", "--max-fetch-failures", "3")
    assert result.returncode == 3, f"stdout={result.stdout!r} stderr={result.stderr!r}"
    assert "fetch" in result.stderr


class _QuietState:
    """A sweep state with nothing to do — the only thing under test is counting."""

    actionable_paths: list[str] = []
    transport_broken = False


def test_failures_separated_by_a_success_do_not_add_up_to_the_exit_3_budget(
    tmp_path, monkeypatch
):
    """fail, succeed, fail, succeed, fail with a budget of two must NOT exit 3.

    Driven in-process with a scripted fetch outcome list rather than by wall
    clock: a timing test cannot tell "the counter reset" from "the second
    failure never happened", and a control that cannot fail is not a control.
    """
    outcomes = [False, True, False, True, False]
    seen: list[bool] = []

    def fake_fetch(_err):
        result = outcomes[len(seen)] if len(seen) < len(outcomes) else True
        seen.append(result)
        return result

    monkeypatch.setattr(sentinel, "_fetch", fake_fetch)
    monkeypatch.setattr(sentinel, "observe", lambda me, root: _QuietState())
    guard = sentinel.PidFile(tmp_path / ".sentinel.pid", ME, sys.stderr)

    code = sentinel.run(
        ME,
        tmp_path,
        interval=0.001,
        metered_interval=0.001,
        metered_flag=tmp_path / "absent",
        max_lifetime=0.4,
        max_failures=2,
        pidfile=guard,
        notify_mode=False,
        out=sys.stdout,
        err=sys.stderr,
    )
    assert len(seen) >= len(outcomes), "the scripted sequence never finished"
    assert code == sentinel.EXIT_KEEPALIVE, (
        "three non-consecutive failures spent a budget of two consecutive ones"
    )


# ---------------------------------------------------------------------------
# 5. double start
# ---------------------------------------------------------------------------

def test_second_start_is_refused_with_exit_1_and_leaves_the_first_running(repo):
    first = start(repo, "--max-lifetime", "20")
    try:
        wait_for(lambda: pidfile(repo).exists(),
                 what="the first sentinel to take its pidfile")
        second = run(repo, "--max-lifetime", "20")
        assert second.returncode == 1, second.stderr
        assert first.poll() is None, "the refusal disturbed the live sibling"
        assert pidfile(repo).exists()
    finally:
        first.kill()
        first.communicate()


def test_a_stale_pidfile_is_broken_with_a_log_line(repo):
    dead = subprocess.Popen([sys.executable, "-c", "pass"])
    dead.wait()
    stale = pidfile(repo)
    stale.parent.mkdir(parents=True, exist_ok=True)
    stale.write_text(
        json.dumps({"pid": dead.pid, "me": ME, "started_utc": "2026-08-21T00:00:00Z"}),
        encoding="utf-8",
    )
    result = run(repo, "--max-lifetime", "2")
    assert result.returncode == 2, result.stderr
    assert "stale pidfile" in result.stderr
    assert not stale.exists(), "the sentinel left its own pidfile behind"


# ---------------------------------------------------------------------------
# 6. read-only: seen-state untouched, and no mutating git verb ever issued
# ---------------------------------------------------------------------------

def test_seen_state_is_byte_identical_across_a_full_run(repo):
    publish_v2(repo, PEER, "20260821T100200Z", "task-c", "question")
    # 1 = the message still owes an ack; either way --mark has written the file,
    # which is the state this test then requires the sentinel not to disturb.
    marked = repo.sweep("--me", ME, "--mark")
    assert marked.returncode in (0, 1), marked.stdout
    before = repo.seen_file().read_bytes()
    result = run(repo, "--max-lifetime", "2")
    assert result.returncode == 2, result.stderr
    assert repo.seen_file().read_bytes() == before


def test_the_run_issues_only_read_only_git_verbs(repo, tmp_path):
    shim_dir, log = git_shim(tmp_path)
    env = dict(os.environ, PATH=f"{shim_dir}{os.pathsep}{os.environ['PATH']}")
    result = run(repo, "--max-lifetime", "2", env=env)
    assert result.returncode == 2, result.stderr
    verbs = {
        line.split()[0]
        for line in log.read_text(encoding="utf-8").splitlines()
        if line.split()
    }
    assert verbs <= {
        "rev-parse", "for-each-ref", "ls-tree", "cat-file", "merge-base", "fetch",
    }, f"sentinel issued a non-read-only git verb: {verbs}"


# ---------------------------------------------------------------------------
# 7. the predicate is inbox_sweep's, not a second copy
# ---------------------------------------------------------------------------

def test_snapshot_is_exactly_the_sweeps_actionable_paths(repo, monkeypatch):
    publish_v2(repo, PEER, "20260821T100300Z", "task-d", "question")
    publish_v2(repo, COORDINATOR, "20260821T100400Z", "task-e", "policy")
    monkeypatch.chdir(repo.work)
    root = repo.work
    assert sentinel.snapshot(ME, root) == inbox_sweep.actionable_set(ME, root).actionable_paths


def test_growth_is_computed_against_the_baseline_snapshot(repo, monkeypatch):
    first = publish_v2(repo, PEER, "20260821T100500Z", "task-f", "question")
    monkeypatch.chdir(repo.work)
    baseline = sentinel.snapshot(ME, repo.work)
    assert first in baseline
    second = publish_v2(repo, PEER, "20260821T100600Z", "task-g", "question")
    assert sentinel.growth(baseline, sentinel.snapshot(ME, repo.work)) == [second]


def test_a_shrinking_set_is_not_growth(repo, monkeypatch):
    publish_v2(repo, PEER, "20260821T100700Z", "task-h", "question")
    monkeypatch.chdir(repo.work)
    baseline = sentinel.snapshot(ME, repo.work)
    assert sentinel.growth(baseline, []) == []


def test_a_transport_that_breaks_while_hanging_wakes_the_agent(repo):
    """`is_actionable` is True on a broken transport, so the sentinel must wake.

    The collision below is on a message addressed to a THIRD agent: nothing in
    it is my mail, so only the transport break can be what wakes me.
    """
    proc = start(repo, "--max-lifetime", "20")
    try:
        wait_for(lambda: is_ready(repo), what="the sentinel baseline snapshot")
        collided = publish_v2(repo, PEER, "20260821T100900Z", "task-j", "question",
                              to=THIRD)
        repo.commit("agent/" + THIRD, {collided: "---\nschema_version: 2\n---\nother\n"})
        out, err = proc.communicate(timeout=60)
    except BaseException:
        proc.kill()
        raise
    assert proc.returncode == 0, f"stayed asleep on a broken transport: {out!r} {err!r}"
    assert "transport" in out


# ---------------------------------------------------------------------------
# 8. metered-network backoff
# ---------------------------------------------------------------------------

def test_metered_flag_file_backs_the_interval_off(tmp_path):
    flag = tmp_path / "METERED-NETWORK"
    assert sentinel.poll_interval(45.0, flag, 600.0) == 45.0
    flag.write_text("on\n", encoding="utf-8")
    assert sentinel.poll_interval(45.0, flag, 600.0) == 600.0


# ---------------------------------------------------------------------------
# 9. --notify never exits on work (owner channel; stub delivery)
# ---------------------------------------------------------------------------

def test_notify_mode_does_not_exit_on_work(repo, tmp_path):
    bin_dir = tmp_path / "notifybin"
    bin_dir.mkdir()
    log = tmp_path / "notified.log"
    (bin_dir / "notify-send").write_text(
        f'#!/bin/bash\nprintf "%s\\n" "$*" >> {log}\n', encoding="utf-8"
    )
    (bin_dir / "notify-send").chmod(0o755)
    env = dict(os.environ, PATH=f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    proc = start(repo, "--notify", "--max-lifetime", "4", env=env)
    try:
        wait_for(lambda: is_ready(repo), what="the sentinel baseline snapshot")
        publish_v2(repo, PEER, "20260821T100800Z", "task-i", "question", to="user")
        out, err = proc.communicate(timeout=60)
    except BaseException:
        proc.kill()
        raise
    assert proc.returncode == 2, f"notify mode exited on work: {out!r} {err!r}"
    wait_for(log.exists, timeout=1.0, what="a notify-send delivery")
    assert "20260821T100800Z" in log.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# The charter's element 3, end to end: my OWN deferral card must wake me
#
# codex_1 made this blocking in the card-2 review — the manual claimed the
# self-addressed DEFERRED card was in the actionable set while `actionable_set()`
# dropped all self-authored mail, and no test published one and observed a wake.
# The sentinel is deliberately not repaired here: it inherits whatever the
# shared predicate says, so this test passes only because the predicate was
# fixed.
# ---------------------------------------------------------------------------

def test_publishing_my_own_deferral_card_wakes_me(repo):
    proc = start(repo, "--max-lifetime", "60")
    try:
        wait_for(lambda: is_ready(repo), what="the sentinel baseline snapshot")
        card = publish_deferral_card(repo, ME, "20260821T110000Z", "task-deferred")
        out, err = proc.communicate(timeout=60)
    except BaseException:
        proc.kill()
        raise
    assert proc.returncode == 0, (
        f"my own deferral card did not wake me: stdout={out!r} stderr={err!r}"
    )
    assert [line for line in out.splitlines() if line.strip()] == [card]


def test_ordinary_self_mail_does_not_wake_me(repo):
    """The negative control: writing to myself is not how I create my own work."""
    proc = start(repo, "--max-lifetime", "3")
    try:
        wait_for(lambda: is_ready(repo), what="the sentinel baseline snapshot")
        publish_v2(
            repo, ME, "20260821T110100Z", "task-plain", "blocker",
            to=ME, requires_ack=True,
        )
        out, err = proc.communicate(timeout=60)
    except BaseException:
        proc.kill()
        raise
    assert proc.returncode == 2, f"woke on ordinary self-mail: {out!r} {err!r}"
    assert "coordination/messages" not in out


# ---------------------------------------------------------------------------
# The double-start race, actually raced
#
# `test_second_start_is_refused_...` waits until the first pidfile EXISTS before
# launching the second, so it proves sequential refusal and nothing about the
# charter's one-sentinel-per-agent exclusion. codex_1 made that blocking: the
# original acquire() was an exists/read/liveness check followed later by a
# write, and two starters that both got past the check before either wrote would
# both believe they held the file.
#
# Racing real interpreters cannot align: process startup jitter is milliseconds
# and the window is microseconds. Forking a warm interpreter and releasing every
# child from one barrier does align, and calls the production acquire() with no
# test hook in it. Losers must stay parked until the count is in, or a dead
# loser's pid would make its own pidfile look legitimately stale to the next
# child and manufacture a second winner.
# ---------------------------------------------------------------------------

RACERS = 32


def test_simultaneous_starters_leave_exactly_one_pidfile_owner(tmp_path):
    import io

    path = tmp_path / "agent" / ".sentinel.pid"
    ready_r, ready_w = os.pipe()
    go_r, go_w = os.pipe()
    result_r, result_w = os.pipe()
    finish_r, finish_w = os.pipe()

    children = []
    for _ in range(RACERS):
        pid = os.fork()
        if pid == 0:  # pragma: no cover - child branch
            outcome = b"E"
            try:
                os.write(ready_w, b"x")
                os.read(go_r, 1)
                won = sentinel.PidFile(path, "agent", io.StringIO()).acquire()
                outcome = b"W" if won else b"L"
            except BaseException:
                pass  # reported as E; a racer must never leave the parent hanging
            finally:
                try:
                    os.write(result_w, outcome)
                    os.read(finish_r, 1)  # stay alive so my pid stays live
                finally:
                    os._exit(0)
        children.append(pid)

    try:
        read_exactly(ready_r, RACERS)          # every child parked on the barrier
        os.write(go_w, b"x" * RACERS)          # released together
        outcomes = read_exactly(result_r, RACERS)
    finally:
        os.write(finish_w, b"x" * RACERS)
        for pid in children:
            os.waitpid(pid, 0)

    assert outcomes.count(b"E") == 0, (
        f"{outcomes.count(b'E')} of {RACERS} simultaneous starters crashed inside "
        "acquire()"
    )
    assert outcomes.count(b"W") == 1, (
        f"{outcomes.count(b'W')} of {RACERS} simultaneous starters each believed "
        "they held the pidfile"
    )
    assert outcomes.count(b"L") == RACERS - 1


def read_exactly(fd: int, count: int) -> bytes:
    buf = b""
    while len(buf) < count:
        chunk = os.read(fd, count - len(buf))
        assert chunk, "a racer died without reporting"
        buf += chunk
    return buf
