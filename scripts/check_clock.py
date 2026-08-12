#!/usr/bin/env python3
"""Fail (exit 2) when the newest commit on any ref is more than 1 hour in the future
relative to the system clock. Catches the fabricated-clock session class (a 2026-08-09
session that believed it was 2026-08-12). Run at session start; also part of
`coordctl doctor`."""
import argparse
import subprocess
import sys
from datetime import datetime, timezone

SKEW_LIMIT_S = 3600


def newest_commit_utc(repo):
    out = subprocess.run(
        ["git", "-C", repo, "for-each-ref", "--sort=-committerdate",
         "--count=1", "--format=%(committerdate:iso-strict)"],
        capture_output=True, text=True, check=True).stdout.strip()
    return datetime.fromisoformat(out).astimezone(timezone.utc)


def main(repo=".", now=None):
    now_dt = (now or (lambda: datetime.now(timezone.utc)))()
    newest = newest_commit_utc(repo)
    skew = (newest - now_dt).total_seconds()
    print(f"system now : {now_dt.isoformat()}")
    print(f"newest ref : {newest.isoformat()}")
    if skew > SKEW_LIMIT_S:
        print(f"CLOCK HAZARD: newest commit is {skew/3600:.1f} h in the FUTURE. "
              "Either the system clock is wrong or a session fabricated dates. "
              "Trust `git log`, fix the clock, do not stamp new artifacts until resolved.")
        return 2
    print("clock sane")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=".")
    sys.exit(main(repo=p.parse_args().repo))
