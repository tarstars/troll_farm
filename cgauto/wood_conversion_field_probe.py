#!/usr/bin/env python3
"""Collect behavior-neutral live wood-conversion telemetry in controlled games.

This uses ``TestSession/play`` only, is hard-capped at 12 games, and never submits code to the
arena.  The probe logs the live policy's selected tree state plus per-turn carried wood; this
module reconstructs fell yield and carry-capped loss from the next observed state.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import statistics
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

STATE_RE = re.compile(
    r"^@WC_STATE t=(\d+) u=(\d+) x=(-?\d+) y=(-?\d+) "
    r"cw=(-?\d+) free=(-?\d+) iw=(-?\d+)$"
)
SELECT_RE = re.compile(
    r"^@WC_SELECT t=(\d+) u=(\d+) op=(\S+) kind=(\S+) x=(-?\d+) y=(-?\d+) "
    r"size=(-?\d+) health=(-?\d+) fruits=(-?\d+) chop=(-?\d+) free=(-?\d+)$"
)
OVERRIDE_RE = re.compile(r"^@WC_OVERRIDE t=(\d+) u=(\d+) op=(\S+)$")
NEIGHBORS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def stderr_text(result: dict) -> str:
    return "\n".join(str(frame.get("stderr") or "") for frame in result.get("frames", []))


def parse_events(raw: str) -> list[dict]:
    events = []
    for line in raw.splitlines():
        line = line.strip()
        if match := STATE_RE.match(line):
            events.append(
                dict(
                    event="state",
                    turn=int(match[1]),
                    unit=int(match[2]),
                    x=int(match[3]),
                    y=int(match[4]),
                    carry_wood=int(match[5]),
                    free=int(match[6]),
                    inventory_wood=int(match[7]),
                )
            )
        elif match := SELECT_RE.match(line):
            events.append(
                dict(
                    event="select",
                    turn=int(match[1]),
                    unit=int(match[2]),
                    op=match[3],
                    kind=match[4],
                    x=int(match[5]),
                    y=int(match[6]),
                    size=int(match[7]),
                    health=int(match[8]),
                    fruits=int(match[9]),
                    chop=int(match[10]),
                    free=int(match[11]),
                )
            )
        elif match := OVERRIDE_RE.match(line):
            events.append(
                dict(
                    event="override",
                    turn=int(match[1]),
                    unit=int(match[2]),
                    op=match[3],
                )
            )
    return events


def static_geometry(result: dict) -> tuple[set[tuple[int, int]], tuple[int, int]] | None:
    frames = result.get("frames") or []
    if not frames:
        return None
    view = frames[0].get("view") or ""
    if "\n" not in view:
        return None
    try:
        payload = json.loads(view.split("\n", 1)[1])
        lines = payload["global"]["inputmodule"].split("\n")
        width, height = (int(value) for value in lines[0].split())
        rows = lines[1:]
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None
    if len(rows) != height or any(len(row) != width for row in rows):
        return None
    walkable = set()
    shack = None
    for y, row in enumerate(rows):
        for x, cell in enumerate(row):
            if cell == ".":
                walkable.add((x, y))
            elif cell == "0":
                shack = (x, y)
    return (walkable, shack) if shack is not None else None


def distance(walkable: set[tuple[int, int]], starts: list[tuple[int, int]], target: tuple[int, int]) -> int | None:
    queue = deque((cell, 0) for cell in starts)
    seen = set(starts)
    while queue:
        cell, steps = queue.popleft()
        if cell == target:
            return steps
        for dx, dy in NEIGHBORS:
            neighbor = (cell[0] + dx, cell[1] + dy)
            if neighbor in walkable and neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, steps + 1))
    return None


def mean_or_none(values: list[int | float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.mean(present) if present else None


def summarize_chops(chops: list[dict]) -> dict:
    def group(rows: list[dict]) -> dict:
        wood = sum(row["wood_gained"] for row in rows)
        return {
            "chop_actions": len(rows),
            "fells": sum(row["fell"] for row in rows),
            "wood_gained": wood,
            "wood_per_chop": wood / len(rows) if rows else None,
            "partial_fells": sum(row["partial_fell"] for row in rows),
            "wood_lost_to_carry": sum(row["wood_lost_to_carry"] for row in rows),
            "partial_cargo_fells": sum(row.get("partial_cargo_fell", False) for row in rows),
            "wood_recoverable_by_banking": sum(
                row.get("wood_recoverable_by_banking", 0) for row in rows
            ),
            "wood_unavoidable_at_capacity": sum(
                row.get("wood_unavoidable_at_capacity", 0) for row in rows
            ),
            "other_uncollected_wood": sum(
                row.get("other_uncollected_wood", 0) for row in rows
            ),
        }

    kinds = sorted({row["kind"] for row in chops})
    return {
        **group(chops),
        "by_kind": {kind: group([row for row in chops if row["kind"] == kind]) for kind in kinds},
    }


def telemetry_summary(result: dict) -> dict:
    raw = stderr_text(result)
    events = parse_events(raw)
    states = {
        (event["turn"], event["unit"]): event
        for event in events
        if event["event"] == "state"
    }
    overrides = {
        (event["turn"], event["unit"])
        for event in events
        if event["event"] == "override"
    }
    selections = [
        event
        for event in events
        if event["event"] == "select"
        and (event["turn"], event["unit"]) not in overrides
    ]

    geometry = static_geometry(result)
    doors = []
    if geometry:
        walkable, shack = geometry
        doors = [
            (shack[0] + dx, shack[1] + dy)
            for dx, dy in NEIGHBORS
            if (shack[0] + dx, shack[1] + dy) in walkable
        ]

    assignments = []
    last_target: dict[int, tuple[int, int]] = {}
    for event in selections:
        target = (event["x"], event["y"])
        if last_target.get(event["unit"]) == target:
            continue
        last_target[event["unit"]] = target
        state = states.get((event["turn"], event["unit"]))
        travel = home = None
        if geometry and state:
            travel = distance(geometry[0], [(state["x"], state["y"])], target)
            home = distance(geometry[0], [target], doors[0]) if len(doors) == 1 else None
            if len(doors) > 1:
                home = min(
                    (value for door in doors if (value := distance(geometry[0], [target], door)) is not None),
                    default=None,
                )
        assignments.append(
            {
                **event,
                "travel_cells": travel,
                "home_cells": home,
            }
        )

    chops = []
    capacities = {}
    for state in states.values():
        capacities[state["unit"]] = max(capacities.get(state["unit"], 0), state["free"])
    for event in selections:
        if event["op"].upper() != "CHOP":
            continue
        current = states.get((event["turn"], event["unit"]))
        following = states.get((event["turn"] + 1, event["unit"]))
        gained = 0
        if current and following:
            gained = max(0, following["carry_wood"] - current["carry_wood"])
        fell = gained > 0
        lost = max(0, event["size"] - gained) if fell else 0
        capacity = capacities.get(event["unit"], event["free"])
        recoverable = (
            max(0, min(event["size"], capacity) - min(event["size"], event["free"]))
            if fell
            else 0
        )
        unavoidable = max(0, event["size"] - capacity) if fell else 0
        other_uncollected = max(0, lost - recoverable - unavoidable)
        chops.append(
            {
                **event,
                "wood_gained": gained,
                "fell": fell,
                "partial_fell": fell and gained < event["size"],
                "wood_lost_to_carry": lost,
                "capacity": capacity,
                "partial_cargo_fell": fell and event["free"] < capacity,
                "wood_recoverable_by_banking": recoverable,
                "wood_unavoidable_at_capacity": unavoidable,
                "other_uncollected_wood": other_uncollected,
            }
        )

    inventory_by_turn = {}
    for state in states.values():
        inventory_by_turn[state["turn"]] = state["inventory_wood"]
    turns = sorted(inventory_by_turn)
    banked = sum(
        max(0, inventory_by_turn[next_turn] - inventory_by_turn[turn])
        for turn, next_turn in zip(turns, turns[1:])
    )
    assignment_by_kind = Counter(row["kind"] for row in assignments)
    return {
        "event_counts": dict(Counter(event["event"] for event in events)),
        "overrides": len(overrides),
        "chops": summarize_chops(chops),
        "assignments": {
            "count": len(assignments),
            "by_kind": dict(assignment_by_kind),
            "mean_initial_travel_cells": mean_or_none(
                [row["travel_cells"] for row in assignments]
            ),
            "mean_target_home_cells": mean_or_none([row["home_cells"] for row in assignments]),
        },
        "banked_wood_from_state_deltas": banked,
        "chop_rows": chops,
        "assignment_rows": assignments,
        "stderr_bytes": len(raw.encode()),
    }


def aggregate_rows(rows: list[dict]) -> dict:
    chops = [chop for row in rows for chop in row["telemetry"]["chop_rows"]]
    assignments = [
        assignment for row in rows for assignment in row["telemetry"]["assignment_rows"]
    ]
    return {
        "games": len(rows),
        "chops": summarize_chops(chops),
        "assignments": {
            "count": len(assignments),
            "by_kind": dict(Counter(row["kind"] for row in assignments)),
            "mean_initial_travel_cells": mean_or_none(
                [row["travel_cells"] for row in assignments]
            ),
            "mean_target_home_cells": mean_or_none([row["home_cells"] for row in assignments]),
        },
        "mean_score": mean_or_none([row["scores"][0] for row in rows]),
        "mean_wood": mean_or_none([row["wood"][0] for row in rows]),
        "wins": sum(row["win"] for row in rows),
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
        default=REPO / "data/panels/top5-wood-conversion-telemetry.json",
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
        raise SystemExit(f"refusing {len(jobs)} games in one burst (maximum {MAX_BURST})")
    code = args.source.read_text()
    if len(code.encode()) > 100_000:
        raise SystemExit(f"probe source is {len(code.encode())} bytes (>100000)")

    now = datetime.now(timezone.utc)
    payload = {
        "schema": 1,
        "scope": "controlled TestSession/play wood telemetry; never arena-submitted",
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
    print(f"wood probe: {len(jobs)} controlled games -> {args.output}", flush=True)
    for index, job in enumerate(jobs, 1):
        print(f"game {index}/{len(jobs)}: probe vs {job['opponent']}", flush=True)
        try:
            result = play(code, job["opponent_agent"])
        except PanelStop as error:
            payload.update(
                status="stopped",
                stop_reason=str(error),
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            save(args.output, payload)
            print(f"STOP: {error}", file=sys.stderr)
            return 75
        row = result_row({**job, "bot": "wood-probe"}, result)
        row["telemetry"] = telemetry_summary(result)
        payload["rows"].append(row)
        save(args.output, payload)
        chops = row["telemetry"]["chops"]
        print(
            f"  score {row['scores'][0]}-{row['scores'][1]} wood={row['wood'][0]} "
            f"chops={chops['chop_actions']} fell={chops['fells']} "
            f"yield={chops['wood_per_chop']} partial={chops['partial_fells']} "
            f"game={row['game_id']}",
            flush=True,
        )
        if index < len(jobs):
            time.sleep(args.sleep)

    payload["status"] = "complete"
    payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    payload["aggregate"] = aggregate_rows(payload["rows"])
    save(args.output, payload)
    print(json.dumps(payload["aggregate"], indent=1), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
