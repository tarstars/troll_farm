#!/usr/bin/env python3
"""Measure live idle-harvest activation in controlled top-five games.

The supplied source must be the behavior-neutral stderr probe. Games use TestSession/play and
never replace the arena submission. One invocation is hard-capped at the field panel's 12-game
limit and stops immediately on any transport or degenerate-result error.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
import time

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from cgauto.field_panel import (  # noqa: E402
    MAX_BURST,
    PanelStop,
    TOP_FIVE,
    play,
    result_row,
    save,
)
from cgauto.idle_harvest_study import parse_probe_events  # noqa: E402


def stderr_text(result: dict) -> str:
    return "\n".join(
        str(frame.get("stderr") or "") for frame in result.get("frames", [])
    )


def telemetry_summary(result: dict) -> dict:
    raw = stderr_text(result)
    events = parse_probe_events(raw)
    counts = Counter(event["kind"] for event in events)
    return {
        "counts": {
            kind: counts.get(kind, 0) for kind in ("cand", "select", "orchard_force")
        },
        "select_turns": [event["turn"] for event in events if event["kind"] == "select"],
        "orchard_force_turns": [
            event["turn"] for event in events if event["kind"] == "orchard_force"
        ],
        "events": events,
        "stderr_bytes": len(raw.encode()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--games-per-opponent", type=int, default=1)
    parser.add_argument(
        "--opponents",
        default=",".join(TOP_FIVE),
        help=f"comma-separated names from: {', '.join(TOP_FIVE)}",
    )
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO / "data/panels/top5-idle-harvest-telemetry.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    names = [name.strip().lower() for name in args.opponents.split(",") if name.strip()]
    unknown = [name for name in names if name not in TOP_FIVE]
    if unknown:
        raise SystemExit(f"unknown opponent(s): {', '.join(unknown)}")
    if args.games_per_opponent < 1:
        raise SystemExit("--games-per-opponent must be positive")
    jobs = [
        {"repetition": repetition, "opponent": name, "opponent_agent": TOP_FIVE[name]}
        for repetition in range(args.games_per_opponent)
        for name in names
    ]
    if len(jobs) > MAX_BURST:
        raise SystemExit(
            f"refusing {len(jobs)} games in one burst (maximum {MAX_BURST}); split the run"
        )
    code = args.source.read_text()
    if len(code.encode()) > 100_000:
        raise SystemExit(f"probe source is {len(code.encode())} bytes (>100000)")

    now = datetime.now(timezone.utc)
    payload = {
        "schema": 1,
        "scope": "controlled TestSession/play activation telemetry; never arena-submitted",
        "started_at": now.isoformat(),
        "completed_at": None,
        "status": "running",
        "source": {
            "path": str(args.source),
            "bytes": len(code.encode()),
            "sha256": hashlib.sha256(code.encode()).hexdigest(),
        },
        "jobs": jobs,
        "rows": [],
        "stop_reason": None,
    }
    save(args.output, payload)
    print(f"field probe: {len(jobs)} controlled games -> {args.output}", flush=True)
    for index, job in enumerate(jobs, 1):
        print(
            f"game {index}/{len(jobs)}: probe vs {job['opponent']} "
            f"({job['opponent_agent']})",
            flush=True,
        )
        try:
            result = play(code, job["opponent_agent"])
        except PanelStop as error:
            payload["status"] = "stopped"
            payload["stop_reason"] = str(error)
            payload["completed_at"] = datetime.now(timezone.utc).isoformat()
            save(args.output, payload)
            print(f"STOP: {error}", file=sys.stderr)
            return 75
        row = result_row({**job, "bot": "probe"}, result)
        row["telemetry"] = telemetry_summary(result)
        payload["rows"].append(row)
        save(args.output, payload)
        counts = row["telemetry"]["counts"]
        print(
            f"  score {row['scores'][0]}-{row['scores'][1]} "
            f"select={counts['select']} orchard={counts['orchard_force']} "
            f"game={row['game_id']}",
            flush=True,
        )
        if index < len(jobs):
            time.sleep(args.sleep)

    payload["status"] = "complete"
    payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    aggregate = Counter()
    for row in payload["rows"]:
        aggregate.update(row["telemetry"]["counts"])
    payload["aggregate"] = {
        "games": len(payload["rows"]),
        "games_with_inner_selection": sum(
            row["telemetry"]["counts"]["select"] > 0 for row in payload["rows"]
        ),
        "games_with_orchard_force": sum(
            row["telemetry"]["counts"]["orchard_force"] > 0 for row in payload["rows"]
        ),
        "event_counts": {
            kind: aggregate.get(kind, 0) for kind in ("cand", "select", "orchard_force")
        },
    }
    save(args.output, payload)
    print(f"aggregate: {payload['aggregate']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
