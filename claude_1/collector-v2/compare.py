#!/usr/bin/env python3
"""B5 — parallel-run comparison (task `20260811-s3-collector-v2`).

Compares, over a date range, the game ids present in the bucket's daily manifests against a
game-id list exported from `project_host`, and reports what each side has that the other does
not.

Reference input (`--reference`): one game id per line, or a JSON array of ids, or JSONL rows
carrying a `game_id` field — all three are accepted because the coordinator's export format
was not fixed in the plan and guessing wrong would have blocked the tool on a formatting
detail. `--reference-label` records which population it actually is; the label is copied into
the output verbatim so a result can never be read as comparing something it did not.

`missing` (in the reference, absent from the bucket) is the number that matters for cut-over:
it is what the VM collector failed to capture. `extra` is not symmetric with it — the VM
collector runs at 05:47 and `project_host` at 05:17, and the cohorts are not identical, so
extra ids are expected and are reported, not flagged.

Reads the bucket and the reference; writes only the `--out` JSON.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s3client import S3Client, S3Error  # noqa: E402

MANIFEST_RE = re.compile(r"^games/manifest/daily-(\d{4}-\d{2}-\d{2})(?:\.rerun-(\d+))?\.jsonl$")


def parse_reference(text: str) -> list[int]:
    """Accept a JSON array, JSONL rows with `game_id`, or one id per line."""
    stripped = text.strip()
    if not stripped:
        return []
    if stripped.startswith("["):
        return [int(value) for value in json.loads(stripped)]
    ids: list[int] = []
    for line in stripped.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("{"):
            ids.append(int(json.loads(line)["game_id"]))
        else:
            ids.append(int(line))
    return ids


def dates_in_range(start: str, end: str) -> list[str]:
    first = dt.date.fromisoformat(start)
    last = dt.date.fromisoformat(end)
    if last < first:
        raise ValueError(f"end {end} precedes start {start}")
    return [(first + dt.timedelta(days=n)).isoformat()
            for n in range((last - first).days + 1)]


def bucket_ids(s3: S3Client, dates: list[str]) -> tuple[dict, list[dict]]:
    """Read every daily manifest for the range, INCLUDING `.rerun-N` ones.

    A day can legitimately span several objects: an interrupted or re-run collection writes
    `.rerun-N` rather than overwriting, so a reader that only looks at the plain key would
    under-count the day and report false 'missing' ids.
    """
    wanted = set(dates)
    per_date: dict[str, dict] = {date: {"ids": set(), "manifests": []} for date in dates}
    problems: list[dict] = []
    for row in s3.list_objects("games/manifest/"):
        match = MANIFEST_RE.match(row["key"])
        if not match or match.group(1) not in wanted:
            continue
        date = match.group(1)
        try:
            body = s3.get_object(row["key"]).decode()
        except S3Error as error:
            problems.append({"key": row["key"], "error": f"{error.code}: {error.s3_message}"})
            continue
        ids = {int(json.loads(line)["game_id"]) for line in body.splitlines() if line.strip()}
        per_date[date]["ids"].update(ids)
        per_date[date]["manifests"].append({"key": row["key"], "games": len(ids),
                                            "rerun": int(match.group(2) or 0)})
    return per_date, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="B5 parallel-run comparison")
    ap.add_argument("--out", required=True)
    ap.add_argument("--start", required=True, help="YYYY-MM-DD")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD")
    ap.add_argument("--reference", default=None,
                    help="path to the project_host id export; omit to report bucket-side only")
    ap.add_argument("--reference-label", default=None,
                    help="what the reference population actually is — copied into the output")
    ap.add_argument("--bucket", default="troll-farm-data")
    args = ap.parse_args(argv)

    dates = dates_in_range(args.start, args.end)
    s3 = S3Client(args.bucket)
    per_date, problems = bucket_ids(s3, dates)

    bucket_all: set[int] = set()
    days = []
    for date in dates:
        entry = per_date[date]
        bucket_all.update(entry["ids"])
        days.append({"date": date, "games": len(entry["ids"]),
                     "manifests": sorted(entry["manifests"], key=lambda m: m["rerun"])})

    report = {
        "check": "b5-parallel-run-comparison",
        "task_id": "20260811-s3-collector-v2",
        "range": {"start": args.start, "end": args.end, "days": len(dates)},
        "bucket": args.bucket,
        "bucket_games_total": len(bucket_all),
        "days": days,
        "manifest_read_problems": problems,
    }

    if args.reference:
        reference = set(parse_reference(Path(args.reference).read_text()))
        missing = sorted(reference - bucket_all)
        extra = sorted(bucket_all - reference)
        report.update({
            "reference_path": args.reference,
            "reference_label": args.reference_label or "UNLABELLED — provenance not stated",
            "reference_games_total": len(reference),
            "missing_from_bucket": missing,
            "missing_count": len(missing),
            "extra_in_bucket": extra[:500],
            "extra_count": len(extra),
            "verdict": "PARITY" if not missing else "GAPS",
        })
    else:
        report.update({
            "reference_path": None,
            "verdict": "NO_REFERENCE",
            "note": ("No project_host export was supplied, so this run reports the bucket side "
                     "only. It is NOT a parity result and must not be quoted as one."),
        })

    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    summary = {k: report[k] for k in ("verdict", "bucket_games_total", "range")}
    summary["days"] = [{d["date"]: d["games"]} for d in days]
    if args.reference:
        summary.update({"reference_games_total": report["reference_games_total"],
                        "missing_count": report["missing_count"],
                        "extra_count": report["extra_count"],
                        "reference_label": report["reference_label"]})
    print(json.dumps(summary, indent=2))
    return 0 if report["verdict"] in {"PARITY", "NO_REFERENCE"} else 1


if __name__ == "__main__":
    sys.exit(main())
