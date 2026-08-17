#!/usr/bin/env python3
"""Print the iteration pool status computed from coordination/ITERATION.md.

The pool file is the direction artifact (owner decision 2026-08-17); this tool
makes its state COMPUTED rather than maintained: `Pool: N/M done`, the open
items with their assignees, and the newest progress-log line. Automation over
vigilance — the same reason the outbox lint exists.

Usage:
    python3 scripts/pool_status.py            # human summary
    python3 scripts/pool_status.py --check    # exit 1 if the file is missing
                                              # or has zero pool items

Exit status: 0 normally; 1 with --check when the pool is absent or empty.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

ITEM_RE = re.compile(r"^- \[(?P<done>[ xX])\] (?P<num>\d+)\. (?P<title>.+)$")


def repo_root() -> pathlib.Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if out.returncode != 0:
        print("not inside a git repository", file=sys.stderr)
        sys.exit(1)
    return pathlib.Path(out.stdout.strip())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit 1 when the pool file is missing or empty")
    ap.add_argument("--file", default="coordination/ITERATION.md",
                    help="pool file path relative to the repo root")
    args = ap.parse_args()

    path = repo_root() / args.file
    if not path.is_file():
        print(f"pool file missing: {args.file}")
        return 1 if args.check else 0

    items: list[tuple[bool, str, str]] = []
    log_line = ""
    in_log = False
    for line in path.read_text(encoding="utf-8").splitlines():
        m = ITEM_RE.match(line)
        if m:
            items.append((m["done"].lower() == "x", m["num"], m["title"].strip()))
            continue
        if line.startswith("## Progress log"):
            in_log = True
            continue
        if in_log and not log_line and line.startswith("- "):
            log_line = line[2:].strip()

    if not items:
        print(f"pool file has no items: {args.file}")
        return 1 if args.check else 0

    done = sum(1 for d, _, _ in items if d)
    print(f"Pool: {done}/{len(items)} done")
    for d, num, title in items:
        if not d:
            print(f"  open {num}. {title}")
    if log_line:
        print(f"latest: {log_line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
