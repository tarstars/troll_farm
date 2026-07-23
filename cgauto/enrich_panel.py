#!/usr/bin/env python3
"""Enrich a completed controlled-game panel with authenticated replay traces.

``TestSession/play`` returns enough data to score a game, but older panel files may not retain
the command stream. Controlled game replays require the owning user id in the replay request.
This helper is read-only with respect to CodinGame and never submits code to the arena.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
import urllib.error
import urllib.request

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.field_panel import (
    MAX_BURST,
    command_metrics,
    cookie,
    final_inventory,
    runtime_diagnostics,
    save,
    trace_evidence,
    workforce_metrics,
)

REPLAY_URL = "https://www.codingame.com/services/gameResult/findByGameId"
USER_ID = 1302251


def fetch_replay(game_id: int) -> dict:
    request = urllib.request.Request(
        REPLAY_URL,
        data=json.dumps([game_id, USER_ID]).encode(),
        headers={
            "Content-Type": "application/json",
            "Cookie": cookie(),
            "User-Agent": "Mozilla/5.0",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        replay = json.loads(response.read().decode())
    if not isinstance(replay, dict) or not replay.get("frames"):
        raise RuntimeError(f"game {game_id}: replay has no frames")
    return replay


def enrich_row(row: dict, replay: dict) -> dict:
    frames = replay["frames"]
    scores = replay.get("scores")
    if scores is not None and list(scores) != row.get("scores"):
        raise RuntimeError(
            f"game {row.get('game_id')}: saved scores {row.get('scores')} != replay {scores}"
        )
    inventories = [final_inventory(frames, player) for player in (0, 1)]
    if row.get("inventories") and inventories != row["inventories"]:
        raise RuntimeError(f"game {row.get('game_id')}: final inventories changed")
    replay_trace = trace_evidence(replay)
    saved_trace = row.get("trace") or {}
    if saved_trace:
        saved_turn_one = (saved_trace.get("turn_one") or {}).get("sha256")
        replay_turn_one = (replay_trace.get("turn_one") or {}).get("sha256")
        if saved_turn_one != replay_turn_one:
            raise RuntimeError(f"game {row.get('game_id')}: turn-one trace changed")
        saved_stdout = [entry.get("sha256") for entry in saved_trace.get("stdout") or []]
        replay_stdout = [entry.get("sha256") for entry in replay_trace.get("stdout") or []]
        if saved_stdout != replay_stdout:
            raise RuntimeError(f"game {row.get('game_id')}: stdout trace changed")
    return {
        **row,
        "turns": max(0, sum(1 for frame in frames if frame.get("keyframe")) - 1),
        "commands": command_metrics(frames),
        "workforce": workforce_metrics(frames),
        "diagnostics": runtime_diagnostics(frames),
        "trace": replay_trace,
    }


def needs_enrichment(row: dict) -> bool:
    return (
        "commands" not in row
        or (row.get("workforce") or {}).get("source") != "referee_summary"
        or "training_turns" not in (row.get("workforce") or {})
        or ("trace" in row and not (row.get("trace") or {}).get("agents"))
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", type=Path)
    parser.add_argument("--sleep", type=float, default=0.35)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = json.loads(args.panel.read_text())
    rows = payload.get("rows") or []
    if len(rows) > MAX_BURST:
        raise SystemExit(f"refusing to enrich {len(rows)} rows (maximum {MAX_BURST})")
    pending = [row for row in rows if needs_enrichment(row)]
    if not pending:
        print(f"already enriched: {args.panel}")
        return 0

    payload["replay_enrichment"] = {
        "status": "running",
        "user_id": USER_ID,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "stop_reason": None,
    }
    save(args.panel, payload)
    for index, row in enumerate(rows):
        if not needs_enrichment(row):
            continue
        game_id = row.get("game_id")
        try:
            replay = fetch_replay(game_id)
            rows[index] = enrich_row(row, replay)
        except (OSError, ValueError, RuntimeError, urllib.error.HTTPError) as error:
            payload["replay_enrichment"].update(
                status="stopped",
                completed_at=datetime.now(timezone.utc).isoformat(),
                stop_reason=f"{type(error).__name__}: {str(error)[:200]}",
            )
            save(args.panel, payload)
            print(f"STOP: {error}", file=sys.stderr)
            return 75
        save(args.panel, payload)
        print(f"enriched game {game_id}", flush=True)
        if index + 1 < len(rows):
            time.sleep(args.sleep)

    payload["replay_enrichment"].update(
        status="complete",
        completed_at=datetime.now(timezone.utc).isoformat(),
    )
    save(args.panel, payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
