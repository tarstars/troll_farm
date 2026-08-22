#!/usr/bin/env python3
"""Exit 2 unless the last 05:17 collector run both finished with exit=0 and is recent.
The collector (data/scripts/collect_wide_cron.sh) appends '<ISO-Z> ... exit=N' markers to
data/raw/collect_wide.log. Read-only; never touches data/raw/games/."""
import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MARK = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z).*exit=(\d+)")


def main(log_path="data/raw/collect_wide.log", now=None, max_age_h=48):
    now_dt = (now or (lambda: datetime.now(timezone.utc)))()
    p = Path(log_path)
    if not p.exists():
        print(f"CRON HAZARD: {p} does not exist"); return 2
    last = None
    for line in p.read_text(errors="replace").splitlines():
        m = MARK.search(line)
        if m:
            last = m
    if last is None:
        print(f"CRON HAZARD: no 'exit=N' marker found in {p}"); return 2
    ts = datetime.strptime(last.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    code = int(last.group(2))
    age_h = (now_dt - ts).total_seconds() / 3600
    print(f"last run: {last.group(1)} exit={code} age={age_h:.1f}h")
    if code != 0:
        print("CRON HAZARD: last collector run FAILED"); return 2
    if age_h > max_age_h:
        print(f"CRON HAZARD: last successful run older than {max_age_h}h"); return 2
    print("cron healthy")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="data/raw/collect_wide.log")
    sys.exit(main(log_path=ap.parse_args().log))
