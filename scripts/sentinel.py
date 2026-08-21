#!/usr/bin/env python3
"""The blocking inbox sentinel: hang at zero token cost, exit when work arrives.

An agent starts `scripts/sentinel.py --me <agent>` in its session background as
the last action of a turn-cycle. The process blocks while nothing changes and
EXITS the moment that agent's actionable set GROWS, printing the triggering
message paths on stdout — the harness then re-invokes the agent, warm, with the
paths already named. No LLM runs while the inbox is quiet.

Exit codes ARE the interface:

  0  work: stdout carries the triggering paths, one per line (or a
     `transport: ...` line when what changed is that the transport broke)
  1  refused to start: a live sibling holds the pidfile; nothing was touched
  2  keepalive: --max-lifetime reached; the agent does a liveness sweep and
     restarts the sentinel
  3  transport trouble: N consecutive fetch-or-sweep failures; the agent
     reports it rather than guessing at stale state

Two rules are load-bearing and are enforced by tests, not by good intentions:

  * The actionability predicate is `inbox_sweep.actionable_set()` and nothing
    else. This tool never re-composes actionability from `scan_authoritative()`,
    raw message fields, sweep CLI output, git activity or process activity
    (codex_1's binding boundary, 2026-08-21). A second predicate that disagrees
    with the sweep is worse than none: it wakes agents for work the sweep does
    not show, or stays silent on work it does.
  * The sentinel is READ-ONLY on git and on inbox state: it fetches, and
    otherwise only reads. It never merges, never marks, never touches any
    agent's `inbox-seen.json`.

Manual: docs/sentinel.md. Charter:
coordination/tasks/20260819-sentinel-wake-on-work.md.
"""
from __future__ import annotations

import argparse
import atexit
import fcntl
import json
import os
import pathlib
import shutil
import signal
import subprocess
import sys
import time
from typing import Sequence

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from scripts import inbox_sweep  # noqa: E402

EXIT_WORK = 0
EXIT_REFUSED = 1
EXIT_KEEPALIVE = 2
EXIT_TRANSPORT = 3

DEFAULT_INTERVAL = 45.0
DEFAULT_METERED_INTERVAL = 600.0
DEFAULT_MAX_LIFETIME = 6 * 60 * 60.0
DEFAULT_MAX_FAILURES = 5

METERED_FLAG = "coordination/METERED-NETWORK"
OWNER = "user"


# ---------------------------------------------------------------------------
# The predicate — borrowed whole from the sweep, never re-implemented
# ---------------------------------------------------------------------------

def observe(me: str, root: pathlib.Path) -> inbox_sweep.SweepState:
    """One authoritative sweep state for `me`. Fetches nothing, writes nothing."""
    return inbox_sweep.actionable_set(me, root)


def snapshot(me: str, root: pathlib.Path) -> list[str]:
    """The agent's actionable set as paths: unread mail plus unacked obligations."""
    return observe(me, root).actionable_paths


def growth(baseline: Sequence[str], current: Sequence[str]) -> list[str]:
    """Paths actionable now that were not actionable at the baseline.

    Growth only. A set that SHRINKS (the agent acked something from another
    session) is not a wake, and re-wakes never fire for an item already in the
    baseline.
    """
    known = set(baseline)
    return sorted(path for path in current if path not in known)


def poll_interval(base: float, metered_flag: pathlib.Path, metered: float) -> float:
    """Back off to the metered interval while the mobile-internet flag file exists."""
    return metered if metered_flag.exists() else base


# ---------------------------------------------------------------------------
# Pidfile: one sentinel per agent per worktree
# ---------------------------------------------------------------------------

class PidFile:
    """One sentinel per agent per worktree, enforced by the kernel.

    Ownership is an exclusive `flock` on the pidfile, NOT the file's existence.
    The first design checked `exists()`, read the recorded pid and tested its
    liveness, then wrote the file later; two starters that both got past the
    check before either wrote both believed they held it. Under a real barrier
    release that reproduced immediately — and worse, since every starter staged
    through the same `.pid.tmp` name, one starter's `replace()` pulled the
    temporary file out from under another and crashed it (codex_1's card-2
    review, blocking finding 2, 2026-08-21).

    `flock` has no window: the kernel grants it to exactly one holder and drops
    it when that process dies, however it dies, so an abandoned file needs no
    liveness heuristic and no unlink race to break. The lock lives on the INODE,
    which is why the payload is rewritten in place through the held descriptor
    and never staged-and-replaced: replacing the file would leave this process
    holding a lock on an unlinked inode while the next starter locked a brand
    new one.
    """

    def __init__(self, path: pathlib.Path, me: str, err) -> None:
        self.path = path
        self.me = me
        self.err = err
        self.held = False
        self._fd: int | None = None

    def acquire(self) -> bool:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o644)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            holder = self._read_pid()
            print(
                f"refusing to start: sentinel for {self.me} already running "
                f"as {'pid ' + str(holder) if holder is not None else 'an unreadable pid'} "
                f"({self.path})",
                file=self.err,
            )
            os.close(fd)
            return False
        # We hold the lock, so anything already in the file was left by a
        # process that is gone: say so rather than silently overwriting it.
        if os.fstat(fd).st_size > 0:
            holder = self._read_pid()
            print(
                f"stale pidfile broken: {self.path} named "
                f"{'pid ' + str(holder) if holder is not None else 'no readable pid'}, "
                "which is not running",
                file=self.err,
            )
        self._fd = fd
        self.held = True
        atexit.register(self.release)
        self._write(ready=False)
        return True

    def mark_ready(self) -> None:
        """Announce that the baseline snapshot is taken.

        Starters synchronize on this, not on mere existence: a message that
        lands between the pidfile and the baseline would be folded INTO the
        baseline and never wake anyone.
        """
        if self.held:
            self._write(ready=True)

    def _write(self, *, ready: bool) -> None:
        """Rewrite the payload in place — never replace the locked inode."""
        if self._fd is None:
            return
        payload = {
            "pid": os.getpid(),
            "me": self.me,
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ready": ready,
        }
        blob = (json.dumps(payload) + "\n").encode("utf-8")
        os.lseek(self._fd, 0, os.SEEK_SET)
        os.write(self._fd, blob)
        os.ftruncate(self._fd, len(blob))

    def _read_pid(self) -> int | None:
        try:
            return int(json.loads(self.path.read_text(encoding="utf-8"))["pid"])
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def release(self) -> None:
        if not self.held:
            return
        self.held = False
        try:
            if self._read_pid() == os.getpid():
                self.path.unlink()
        except OSError:
            pass
        finally:
            if self._fd is not None:
                try:
                    os.close(self._fd)   # drops the lock
                except OSError:
                    pass
                self._fd = None


# ---------------------------------------------------------------------------
# Owner channel (stub): notify, never wake, never interpret a body
# ---------------------------------------------------------------------------

def notify(paths: Sequence[str], err) -> None:
    """Deliver owner-addressed paths to the desktop channel, or log if absent.

    Deliberately dumb: the paths come from the sweep's own addressing fields and
    no message body is read. Filtering owner-DECISION content out of ordinary
    owner mail, and any channel other than notify-send, are owner activation
    items — see docs/sentinel.md.
    """
    body = "\n".join(paths)
    binary = shutil.which("notify-send")
    if binary is None:
        print(f"notify (no notify-send on PATH): {body}", file=err)
        return
    subprocess.run(
        [binary, "troll_farm: mail for the owner", body],
        check=False,
        capture_output=True,
    )


# ---------------------------------------------------------------------------
# The loop
# ---------------------------------------------------------------------------

def _fetch(err) -> bool:
    proc = inbox_sweep.run_git("fetch", "origin")
    if proc.returncode != 0:
        print(f"git fetch origin failed: {proc.stderr.strip()}", file=err)
        return False
    return True


def run(
    me: str,
    root: pathlib.Path,
    *,
    interval: float,
    metered_interval: float,
    metered_flag: pathlib.Path,
    max_lifetime: float,
    max_failures: int,
    pidfile: PidFile,
    notify_mode: bool,
    out,
    err,
) -> int:
    subject = OWNER if notify_mode else me
    if not pidfile.acquire():
        return EXIT_REFUSED

    deadline = time.monotonic() + max_lifetime
    failures = 0
    baseline: list[str] | None = None
    baseline_broken = False

    while True:
        if baseline is not None:
            if not _sleep_until(
                min(
                    time.monotonic() + poll_interval(interval, metered_flag, metered_interval),
                    deadline,
                ),
                deadline,
            ):
                return EXIT_KEEPALIVE
            if not _fetch(err):
                failures += 1
                if failures >= max_failures:
                    print(
                        f"{failures} consecutive transport failures; "
                        "reporting instead of guessing at stale state",
                        file=err,
                    )
                    return EXIT_TRANSPORT
                continue

        try:
            state = observe(subject, root)
        except inbox_sweep.SweepFailure as exc:
            failures += 1
            print(f"sweep failed: {exc.detail}", file=err)
            if failures >= max_failures:
                return EXIT_TRANSPORT
            if baseline is None and not _sleep_until(
                time.monotonic() + poll_interval(interval, metered_flag, metered_interval),
                deadline,
            ):
                return EXIT_KEEPALIVE
            continue

        failures = 0
        current = state.actionable_paths
        if baseline is None:
            baseline = current
            baseline_broken = state.transport_broken
            pidfile.mark_ready()
            continue

        fresh = growth(baseline, current)
        if notify_mode:
            if fresh:
                notify(fresh, err)
                baseline = current
            continue

        if fresh:
            for path in fresh:
                print(path, file=out)
            out.flush()
            return EXIT_WORK

        if state.transport_broken and not baseline_broken:
            print(
                "transport: the sweep can no longer trust its own inbox state "
                "(collision, delivery or quarantine error) — run the sweep",
                file=out,
            )
            out.flush()
            return EXIT_WORK


def _sleep_until(wake: float, deadline: float) -> bool:
    """Sleep to `wake`, in slices, returning False if `deadline` passes first."""
    while True:
        now = time.monotonic()
        if now >= deadline:
            return False
        if now >= wake:
            return True
        time.sleep(min(0.05, wake - now, deadline - now))


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--me", required=True, help="my agent id, e.g. claude_1")
    ap.add_argument("--interval", type=float, default=DEFAULT_INTERVAL,
                    help="seconds between fetch+recompute ticks (default 45)")
    ap.add_argument("--metered-interval", type=float, default=DEFAULT_METERED_INTERVAL,
                    help="tick seconds while the metered-network flag file exists")
    ap.add_argument("--metered-flag", default=METERED_FLAG,
                    help=f"metered-network flag file, repo-relative (default {METERED_FLAG})")
    ap.add_argument("--max-lifetime", type=float, default=DEFAULT_MAX_LIFETIME,
                    help="seconds before the keepalive exit 2 (default 6 h)")
    ap.add_argument("--max-fetch-failures", type=int, default=DEFAULT_MAX_FAILURES,
                    help="consecutive transport failures before exit 3 (default 5)")
    ap.add_argument("--pidfile", default=None,
                    help="pidfile path (default <root>/<me>/.sentinel.pid)")
    ap.add_argument("--notify", action="store_true",
                    help="owner channel: notify on owner-addressed mail, never exit on work")
    args = ap.parse_args(argv)

    try:
        root = pathlib.Path(inbox_sweep.git("rev-parse", "--show-toplevel").strip())
    except inbox_sweep.GitError as exc:
        print(f"not inside a git repository: {exc}", file=sys.stderr)
        return EXIT_TRANSPORT
    os.chdir(root)

    pidfile_path = (
        pathlib.Path(args.pidfile) if args.pidfile else root / args.me / ".sentinel.pid"
    )
    guard = PidFile(pidfile_path, args.me, sys.stderr)

    def _bye(signum, _frame):
        guard.release()
        sys.exit(128 + signum)

    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, _bye)

    try:
        return run(
            args.me,
            root,
            interval=args.interval,
            metered_interval=args.metered_interval,
            metered_flag=root / args.metered_flag,
            max_lifetime=args.max_lifetime,
            max_failures=args.max_fetch_failures,
            pidfile=guard,
            notify_mode=args.notify,
            out=sys.stdout,
            err=sys.stderr,
        )
    finally:
        guard.release()


if __name__ == "__main__":
    raise SystemExit(main())
