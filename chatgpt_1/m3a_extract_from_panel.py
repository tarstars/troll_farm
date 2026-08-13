#!/usr/bin/env python3
"""Extract and freeze the D-1 situation ledger from the committed panel JSON.

This implementation intentionally reads only the named base panel artifact. It
does not import or compare against another agent's M3a library.

Counting rules:
- episode: one object in a violation whose detector is exactly "D-1";
- situation: one game row keyed by (map_id, seat, attempt) with >=1 D-1 episode;
- terminal: turn_end - turn_start + 1 >= 62 states.

The panel summary has no per-turn command stream or entry-state snapshot, so the
blocking peer's activity is recorded as UNRESOLVED_FROM_BASE_PANEL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

PANEL_PATH = Path(
    "local_claude_1/verification/"
    "readable-no-orchard-oscillation-2026-08-08.json"
)
PANEL_COMMIT = "66fd9e3ab78b82d0d8ed12df7e571615a999c0bd"
PANEL_GIT_BLOB = "71f8b1b342df52a4b5e0ed5891e902874ef4c249"
CANDIDATE_PATH = (
    "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
)
CANDIDATE_SHA256 = (
    "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"
)
DETECTOR_PATH = "claude_1/banana-restoration-r2/trace_detectors.py"
DETECTOR_SHA256 = (
    "59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209"
)

EXPECTED_EPISODES = 34
EXPECTED_SITUATIONS = 32
EXPECTED_TERMINAL_EPISODES = 20
EXPECTED_TERMINAL_SITUATIONS = 19
EXPECTED_LEDGER_SHA256 = (
    "8e05b8aeb9fa90449819558f2c638a358f9c8667c35ea28d2fc2788b02fffc5d"
)


class ExtractionError(RuntimeError):
    """The source panel no longer matches the frozen D-1 extraction."""


def _episode_record(game: dict[str, Any], episode: dict[str, Any]) -> dict[str, Any]:
    required = ("unit", "cells", "k", "turn_start", "turn_end")
    missing = [key for key in required if key not in episode]
    if missing:
        raise ExtractionError(
            f"{game.get('map_id')} seat {game.get('seat')}: "
            f"D-1 episode missing {missing}"
        )
    cells = episode["cells"]
    if (
        not isinstance(cells, list)
        or len(cells) != 2
        or any(not isinstance(cell, list) or len(cell) != 2 for cell in cells)
    ):
        raise ExtractionError(
            f"{game.get('map_id')} seat {game.get('seat')}: invalid D-1 cells"
        )
    turn_start = int(episode["turn_start"])
    turn_end = int(episode["turn_end"])
    if turn_end < turn_start:
        raise ExtractionError(
            f"{game.get('map_id')} seat {game.get('seat')}: reversed D-1 window"
        )
    return {
        "map_id": str(game["map_id"]),
        "seat": int(game["seat"]),
        "attempt": int(game["attempt"]),
        "seed": int(game["seed"]),
        "map_class": str(game["class"]),
        "opponent_profile": str(game["profile"]),
        "unit": int(episode["unit"]),
        "cells": [[int(v) for v in cell] for cell in cells],
        "k": int(episode["k"]),
        "turn_start": turn_start,
        "turn_end": turn_end,
    }


def extract_episode_ledger(panel: dict[str, Any]) -> list[dict[str, Any]]:
    games = panel.get("games")
    if not isinstance(games, list):
        raise ExtractionError("panel.games must be a list")

    ledger: list[dict[str, Any]] = []
    for game in games:
        for violation in game.get("violations", []):
            if violation.get("detector") != "D-1":
                continue
            episodes = violation.get("episodes")
            if not isinstance(episodes, list):
                raise ExtractionError(
                    f"{game.get('map_id')} seat {game.get('seat')}: "
                    "D-1 episodes must be a list"
                )
            declared = violation.get("count")
            if declared != len(episodes):
                raise ExtractionError(
                    f"{game.get('map_id')} seat {game.get('seat')}: "
                    f"D-1 count={declared!r}, episodes={len(episodes)}"
                )
            ledger.extend(_episode_record(game, episode) for episode in episodes)

    return sorted(
        ledger,
        key=lambda row: (
            row["map_id"],
            row["seat"],
            row["attempt"],
            row["turn_start"],
            row["unit"],
            row["cells"],
        ),
    )


def canonical_ledger_sha256(ledger: list[dict[str, Any]]) -> str:
    payload = json.dumps(
        ledger, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_library(panel: dict[str, Any]) -> dict[str, Any]:
    ledger = extract_episode_ledger(panel)
    situations: dict[tuple[str, int, int], dict[str, Any]] = {}

    for row in ledger:
        key = (row["map_id"], row["seat"], row["attempt"])
        situation = situations.setdefault(
            key,
            {
                "situation_id": f"{row['map_id']}-s{row['seat']}-a{row['attempt']}",
                "map_id": row["map_id"],
                "seat": row["seat"],
                "attempt": row["attempt"],
                "seed": row["seed"],
                "map_class": row["map_class"],
                "opponent_profile": row["opponent_profile"],
                "replay_status": "REQUIRES_DETERMINISTIC_REEXECUTION",
                "episodes": [],
            },
        )
        identity = (
            situation["seed"],
            situation["map_class"],
            situation["opponent_profile"],
        )
        expected_identity = (row["seed"], row["map_class"], row["opponent_profile"])
        if identity != expected_identity:
            raise ExtractionError(f"inconsistent game identity for {key}")

        state_count = row["turn_end"] - row["turn_start"] + 1
        situation["episodes"].append(
            {
                "unit": row["unit"],
                "cells": row["cells"],
                "k": row["k"],
                "turn_start": row["turn_start"],
                "turn_end": row["turn_end"],
                "state_count": state_count,
                "terminal_ge_62_states": state_count >= 62,
                "blocking_peer_activity": "UNRESOLVED_FROM_BASE_PANEL",
            }
        )

    terminal_episodes = sum(
        episode["terminal_ge_62_states"]
        for situation in situations.values()
        for episode in situation["episodes"]
    )
    terminal_situations = sum(
        any(ep["terminal_ge_62_states"] for ep in situation["episodes"])
        for situation in situations.values()
    )

    return {
        "schema": "troll-farm-m3a-panel-extraction/v1",
        "created_by": "chatgpt_1",
        "independence": "CONTAMINATED_BY_PRIOR_HANDOFF_EXPOSURE",
        "counting_rule": {
            "episode": (
                "One object in a violation where detector == 'D-1', "
                "counted with multiplicity."
            ),
            "situation": (
                "One game row identified by (map_id, seat, attempt) "
                "containing at least one D-1 episode."
            ),
            "terminal": "turn_end - turn_start + 1 >= 62.",
        },
        "source": {
            "panel_path": str(PANEL_PATH),
            "panel_commit": PANEL_COMMIT,
            "panel_git_blob": PANEL_GIT_BLOB,
            "candidate_path": CANDIDATE_PATH,
            "candidate_sha256": CANDIDATE_SHA256,
            "detector_contract_path": DETECTOR_PATH,
            "detector_contract_sha256": DETECTOR_SHA256,
        },
        "summary": {
            "situations": len(situations),
            "episodes": len(ledger),
            "terminal_episodes_ge_62_states": terminal_episodes,
            "terminal_situations": terminal_situations,
            "idle_blocker_claim_status": "UNRESOLVED_FROM_BASE_PANEL",
            "episode_ledger_sha256": canonical_ledger_sha256(ledger),
        },
        "replay_limit": (
            "The panel row has no entry-state snapshot or command stream; "
            "identity and windows are frozen, but exact entry state must be "
            "regenerated by executing the pinned candidate on the pinned panel recipe."
        ),
        "situations": [situations[key] for key in sorted(situations)],
    }


def validate(library: dict[str, Any], panel: dict[str, Any]) -> None:
    summary = library["summary"]
    expected = {
        "episodes": EXPECTED_EPISODES,
        "situations": EXPECTED_SITUATIONS,
        "terminal_episodes_ge_62_states": EXPECTED_TERMINAL_EPISODES,
        "terminal_situations": EXPECTED_TERMINAL_SITUATIONS,
        "episode_ledger_sha256": EXPECTED_LEDGER_SHA256,
    }
    actual = {key: summary.get(key) for key in expected}
    if actual != expected:
        raise ExtractionError(
            "frozen D-1 extraction changed:\n"
            f"expected={json.dumps(expected, sort_keys=True)}\n"
            f"actual={json.dumps(actual, sort_keys=True)}"
        )

    stats = panel.get("stats", {})
    if stats.get("games") != 240:
        raise ExtractionError(f"expected a 240-game panel, got {stats.get('games')!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=PANEL_PATH)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail unless counts and canonical episode ledger match the frozen extraction",
    )
    args = parser.parse_args()

    panel = json.loads(args.input.read_text(encoding="utf-8"))
    library = build_library(panel)
    if args.check:
        validate(library, panel)

    text = json.dumps(library, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
