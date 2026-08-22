#!/usr/bin/env python3
"""Agent launcher — the no-LLM doorbell that STARTS agent sessions on work.

The wake-on-work design's launcher lane (doorbell spec 2026-08-19 + hybrid
redirect): a plain loop that polls git bytes, computes each configured agent's
WAKE SET with the SAME sweep tool the agents themselves trust (run as
a subprocess — never a reimplemented scan), and launches that agent's headless
session when, and only when, that set is non-empty and CHANGED since the last
wake. Zero LLM cost while idle; launches cost exactly the work they do.

The wake set is NOT the whole actionable queue (protocol §5.1, owner rule
2026-08-21). It is news from someone else: it excludes the agent's own standing
cards, cc-only mail, and courtesy receipts. Those stay in the agent's queue —
they are obligations, and an obligation is not news. Ringing on the full queue
made a blocked agent wake itself: its card could only be discharged by another
card, which re-entered its own set, which rang this bell. Measured 2026-08-21,
eight no-op wakes in 102 minutes.

Guards: per-agent wake cap per hour, per-agent single-flight lock (no second
session while one runs), quiet-period debounce (one wake per burst), a pause
file that stops all launches instantly, and an append-only JSONL wake log.
`--dry-run` = shadow mode: full logging, zero launches.

Config (JSON):
{
  "repo": "/path/to/clone",            # the launcher's own checkout
  "tick_seconds": 180,
  "quiet_seconds": 60,
  "pause_file": "LAUNCHER-PAUSED",      # relative to repo
  "state_dir": "/path/to/state",
  "agents": {
    "claude_1": {"enabled": true, "max_wakes_per_hour": 4,
                  "cwd": "/path/to/claude_1/worktree",
                  "command": ["claude", "-p", "<ritual prompt>"]},
    "codex_1":  {"enabled": false, ...}
  }
}
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time

SECTION_RE = re.compile(r"wake set \((\d+)\):")


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def log(state_dir: pathlib.Path, record: dict) -> None:
    record = {"at": utcnow().isoformat(timespec="seconds"), **record}
    with open(state_dir / "wake-log.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(record, flush=True)


def parse_wake_paths(text: str) -> list[str]:
    """Message paths under the sweep's `wake set` section (protocol §5.1).

    Pure text in, paths out, so the launcher's whole decision can be tested
    without git — reading the WRONG section is precisely the defect this
    replaced, and a defect in a section name is invisible until it costs a
    night of no-op wakes.
    """
    paths: list[str] = []
    take = False
    for line in text.splitlines():
        m = SECTION_RE.match(line.strip())
        if m is not None:
            take = int(m.group(1)) > 0
            continue
        if take:
            stripped = line.strip()
            if stripped.startswith("coordination/messages/"):
                paths.append(stripped.split()[0])
            elif not stripped:
                take = False
    return sorted(set(paths))


def wake_set(repo: pathlib.Path, agent: str) -> tuple[list[str], str]:
    """The agent's WAKE SET + a stable fingerprint, via the shared sweep run as
    a subprocess (shared-runners rule: never re-scan ourselves).

    Not the agent's whole queue: see the module docstring and protocol §5.1.

    The sweep reads `<agent>/inbox-seen.json` from the WORKTREE, so the
    launcher first materializes the agent's CURRENT seen-state from their own
    canonical remote ref — a stale local copy would report months of history
    as unseen (measured: 562 phantom items on first shadow run). The launcher
    must therefore run in its OWN dedicated clone, never in an agent's live
    worktree.
    """
    seen = subprocess.run(
        ["git", "show",
         f"refs/remotes/origin/agent/{agent}:{agent}/inbox-seen.json"],
        cwd=repo, capture_output=True, text=True)
    if seen.returncode == 0:
        dest = repo / agent / "inbox-seen.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(seen.stdout)
    proc = subprocess.run(
        [sys.executable, "scripts/inbox_sweep.py", "--me", agent],
        cwd=repo, capture_output=True, text=True, timeout=300)
    paths = parse_wake_paths(proc.stdout)
    fp = hashlib.sha256("\n".join(paths).encode()).hexdigest()[:16]
    return paths, fp


def under_cap(state: dict, agent: str, cap: int) -> bool:
    cutoff = utcnow() - dt.timedelta(hours=1)
    recent = [t for t in state.get("wakes", {}).get(agent, [])
              if dt.datetime.fromisoformat(t) > cutoff]
    state.setdefault("wakes", {})[agent] = recent
    return len(recent) < cap


def session_running(state_dir: pathlib.Path, agent: str) -> bool:
    pidfile = state_dir / f"{agent}.pid"
    if not pidfile.exists():
        return False
    try:
        pid = int(pidfile.read_text().strip())
        pathlib.Path(f"/proc/{pid}").stat()
        return True
    except (ValueError, FileNotFoundError):
        pidfile.unlink(missing_ok=True)
        return False


def launch(state_dir: pathlib.Path, agent: str, cfg: dict,
           paths: list[str]) -> int:
    logfile = open(state_dir / f"{agent}.session.log", "a")
    proc = subprocess.Popen(cfg["command"], cwd=cfg["cwd"],
                            stdout=logfile, stderr=subprocess.STDOUT)
    (state_dir / f"{agent}.pid").write_text(str(proc.pid))
    return proc.pid


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true",
                    help="shadow mode: log would-wakes, launch nothing")
    ap.add_argument("--once", action="store_true")
    args = ap.parse_args()
    cfg = json.loads(pathlib.Path(args.config).read_text())
    repo = pathlib.Path(cfg["repo"])
    state_dir = pathlib.Path(cfg["state_dir"])
    state_dir.mkdir(parents=True, exist_ok=True)
    state_file = state_dir / "launcher-state.json"
    state = (json.loads(state_file.read_text())
             if state_file.exists() else {"last_fp": {}, "wakes": {}})

    while True:
        if (repo / cfg.get("pause_file", "LAUNCHER-PAUSED")).exists():
            log(state_dir, {"event": "paused"})
            if args.once:
                return 0
            time.sleep(cfg.get("tick_seconds", 180))
            continue
        subprocess.run(["git", "fetch", "origin", "-q"], cwd=repo,
                       timeout=180)
        for agent, acfg in cfg["agents"].items():
            if not acfg.get("enabled"):
                continue
            paths, fp = wake_set(repo, agent)
            if not paths:
                state["last_fp"][agent] = ""
                continue
            if fp == state["last_fp"].get(agent):
                continue                      # same stale set, already woken
            if session_running(state_dir, agent):
                log(state_dir, {"event": "suppressed", "agent": agent,
                                "reason": "session running", "n": len(paths)})
                continue
            if not under_cap(state, agent, acfg.get("max_wakes_per_hour", 4)):
                log(state_dir, {"event": "suppressed", "agent": agent,
                                "reason": "wake cap", "n": len(paths)})
                continue
            # debounce: one wake per burst
            time.sleep(cfg.get("quiet_seconds", 60))
            subprocess.run(["git", "fetch", "origin", "-q"], cwd=repo,
                           timeout=180)
            paths, fp = wake_set(repo, agent)
            if not paths:
                continue
            if args.dry_run:
                log(state_dir, {"event": "would-wake", "agent": agent,
                                "n": len(paths), "paths": paths[:8]})
            else:
                pid = launch(state_dir, agent, acfg, paths)
                state["wakes"].setdefault(agent, []).append(
                    utcnow().isoformat(timespec="seconds"))
                log(state_dir, {"event": "wake", "agent": agent, "pid": pid,
                                "n": len(paths), "paths": paths[:8]})
            state["last_fp"][agent] = fp
        state_file.write_text(json.dumps(state, indent=1))
        if args.once:
            return 0
        time.sleep(cfg.get("tick_seconds", 180))


if __name__ == "__main__":
    sys.exit(main())
