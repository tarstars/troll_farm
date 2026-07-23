#!/usr/bin/env python3
"""Decide the frozen two-game TestSession common-seed A/A capability experiment."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cgauto.arena_rollout_forensics import render_turn_one  # noqa: E402
from cgauto.enrich_panel import fetch_replay  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
DEFAULT_PANEL = REPO / "data/panels/testsession-common-seed-aa-20260719.json"
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/testsession-common-seed-aa-result-2026-07-19.json"
)
EXPECTED_SOURCE_SHA = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"
EXPECTED_OPTIONS = "seed=-5687447269333978810\n"
EXPECTED_TURN_ONE_SHA = "e14d31e1cdb361ccfe50667ff2fb533d73af79c1ba78a079fffbd329262d0240"
EXPECTED_OPPONENT = 6479768


def stdout_stream(frames: list[dict], player: int) -> list[str]:
    """Return every non-null stdout frame in referee order for one player."""

    return [
        str(frame["stdout"])
        for frame in frames
        if frame.get("agentId") == player and frame.get("stdout") is not None
    ]


def stream_sha256(stream: list[str]) -> str:
    canonical = json.dumps(stream, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    panel = json.loads(args.panel.read_text())
    rows = panel.get("rows") or []
    sources = panel.get("sources") or {}
    jobs = panel.get("jobs") or []
    integrity = {
        "panel_complete": panel.get("status") == "complete",
        "two_rows": len(rows) == 2,
        "identical_exact_resident_sources": (
            set(sources) == {"baseline", "candidate"}
            and all(source.get("sha256") == EXPECTED_SOURCE_SHA for source in sources.values())
        ),
        "requested_options_exact": panel.get("requested_game_options") == EXPECTED_OPTIONS,
        "fixed_opponent_and_order": (
            len(jobs) == 2
            and [job.get("bot") for job in jobs] == ["baseline", "candidate"]
            and all(job.get("opponent_agent") == EXPECTED_OPPONENT for job in jobs)
        ),
        "unique_game_ids": len({row.get("game_id") for row in rows}) == 2,
        "zero_diagnostics": len(rows) == 2 and all(not row.get("diagnostics") for row in rows),
    }
    if len(rows) != 2 or any(row.get("game_id") is None for row in rows):
        raise SystemExit("panel does not contain two completed game ids")

    with ThreadPoolExecutor(max_workers=2) as executor:
        games = list(executor.map(lambda row: fetch_replay(int(row["game_id"])), rows))

    turn_one = [render_turn_one(game, 0) for game in games]
    turn_one_sha = [hashlib.sha256(value.encode()).hexdigest() for value in turn_one]
    streams = [
        [stdout_stream(game.get("frames") or [], player) for player in (0, 1)]
        for game in games
    ]
    stream_hashes = [
        [stream_sha256(stream) for stream in game_streams] for game_streams in streams
    ]

    map_control = {
        "responses_echo_requested_options": all(
            game.get("refereeInput") == EXPECTED_OPTIONS for game in games
        ),
        "turn_one_inputs_identical": turn_one[0] == turn_one[1],
        "turn_one_matches_prior_replay": all(
            digest == EXPECTED_TURN_ONE_SHA for digest in turn_one_sha
        ),
    }
    deterministic_outcome = {
        "scores_identical": rows[0].get("scores") == rows[1].get("scores"),
        "final_inventories_identical": (
            rows[0].get("inventories") == rows[1].get("inventories")
        ),
        "turn_counts_identical": rows[0].get("turns") == rows[1].get("turns"),
        "workforce_histories_identical": (
            rows[0].get("workforce") == rows[1].get("workforce")
        ),
        "player_0_stdout_identical": streams[0][0] == streams[1][0],
        "player_1_stdout_identical": streams[0][1] == streams[1][1],
    }
    gates = {
        "condition_1_complete_zero_diagnostics": (
            integrity["panel_complete"]
            and integrity["two_rows"]
            and integrity["zero_diagnostics"]
        ),
        "condition_2_exact_options_echo": map_control[
            "responses_echo_requested_options"
        ],
        "condition_3_identical_turn_one": map_control["turn_one_inputs_identical"],
        "condition_4_matches_frozen_prior_map": map_control[
            "turn_one_matches_prior_replay"
        ],
        "condition_5_full_determinism": all(deterministic_outcome.values()),
    }
    payload = {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "protocol": "testsession-common-seed-aa-protocol-2026-07-19.md",
        "panel": str(args.panel),
        "integrity": integrity,
        "requested_game_options": EXPECTED_OPTIONS,
        "game_ids": [row["game_id"] for row in rows],
        "turn_one_bytes": [len(value.encode()) for value in turn_one],
        "turn_one_sha256": turn_one_sha,
        "stdout_frames": [
            [len(stream) for stream in game_streams] for game_streams in streams
        ],
        "stdout_sha256": stream_hashes,
        "map_control": map_control,
        "deterministic_outcome": deterministic_outcome,
        "gates": gates,
        "common_seed_pairing_available": all(integrity.values()) and all(gates.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    return 0 if payload["common_seed_pairing_available"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
