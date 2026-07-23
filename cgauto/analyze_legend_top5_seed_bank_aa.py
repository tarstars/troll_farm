#!/usr/bin/env python3
"""Validate deterministic A/A references for Legend top-five common-seed bank v1."""

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

from cgauto.analyze_testsession_common_seed_aa import (  # noqa: E402
    stdout_stream,
    stream_sha256,
)
from cgauto.arena_rollout_forensics import render_turn_one  # noqa: E402
from cgauto.enrich_panel import fetch_replay  # noqa: E402
from cgauto.field_panel import validate_seed_blocks  # noqa: E402


REPO = Path(__file__).resolve().parent.parent
DEFAULT_BANK = (
    REPO
    / "data/analysis/live-agent-6553250/legend-top5-common-seed-bank-v1.json"
)
DEFAULT_PANEL = (
    REPO / "data/panels/legend-top5-common-seed-bank-v1-aa-20260719.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "data/analysis/live-agent-6553250/"
    "legend-top5-common-seed-bank-aa-result-2026-07-19.json"
)
EXPECTED_SOURCE_SHA = "a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    parser.add_argument("--panel", type=Path, default=DEFAULT_PANEL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    bank_text = args.bank.read_text()
    blocks = validate_seed_blocks(json.loads(bank_text))
    bank_sha = hashlib.sha256(bank_text.encode()).hexdigest()
    panel = json.loads(args.panel.read_text())
    rows = panel.get("rows") or []
    sources = panel.get("sources") or {}
    expected_rows = len(blocks) * 2
    integrity = {
        "panel_complete": panel.get("status") == "complete",
        "ten_rows": len(rows) == expected_rows == 10,
        "bank_hash_exact": (panel.get("seed_bank") or {}).get("sha256") == bank_sha,
        "bank_blocks_exact": (panel.get("seed_bank") or {}).get("blocks") == blocks,
        "identical_exact_resident_sources": (
            set(sources) == {"baseline", "candidate"}
            and all(source.get("sha256") == EXPECTED_SOURCE_SHA for source in sources.values())
        ),
        "unique_game_ids": (
            len(rows) == expected_rows
            and len({row.get("game_id") for row in rows}) == expected_rows
        ),
        "zero_diagnostics": (
            len(rows) == expected_rows and all(not row.get("diagnostics") for row in rows)
        ),
    }
    if len(rows) != expected_rows or any(row.get("game_id") is None for row in rows):
        raise SystemExit(f"panel does not contain {expected_rows} completed game ids")

    with ThreadPoolExecutor(max_workers=5) as executor:
        games = list(executor.map(lambda row: fetch_replay(int(row["game_id"])), rows))

    per_block = []
    for index, block in enumerate(blocks):
        block_rows = rows[index * 2 : index * 2 + 2]
        block_games = games[index * 2 : index * 2 + 2]
        expected_options = f"seed={block['seed']}\n"
        turn_one = [render_turn_one(game, 0) for game in block_games]
        map_hashes = [hashlib.sha256(value.encode()).hexdigest() for value in turn_one]
        streams = [
            [stdout_stream(game.get("frames") or [], player) for player in (0, 1)]
            for game in block_games
        ]
        gates = {
            "row_identity_exact": (
                [row.get("bot") for row in block_rows] == ["baseline", "candidate"]
                and all(row.get("opponent") == block["opponent"] for row in block_rows)
                and all(
                    row.get("opponent_agent") == block["opponent_agent"]
                    for row in block_rows
                )
                and all(row.get("seed") == block["seed"] for row in block_rows)
            ),
            "exact_options_echo": all(
                game.get("refereeInput") == expected_options for game in block_games
            ),
            "turn_one_identical": turn_one[0] == turn_one[1],
            "scores_identical": block_rows[0].get("scores") == block_rows[1].get("scores"),
            "final_inventories_identical": (
                block_rows[0].get("inventories") == block_rows[1].get("inventories")
            ),
            "turn_counts_identical": (
                block_rows[0].get("turns") == block_rows[1].get("turns")
            ),
            "workforce_histories_identical": (
                block_rows[0].get("workforce") == block_rows[1].get("workforce")
            ),
            "player_0_stdout_identical": streams[0][0] == streams[1][0],
            "player_1_stdout_identical": streams[0][1] == streams[1][1],
        }
        per_block.append(
            {
                **block,
                "game_ids": [row["game_id"] for row in block_rows],
                "scores": block_rows[0]["scores"],
                "wood": block_rows[0]["wood"],
                "turns": block_rows[0]["turns"],
                "workforce": block_rows[0]["workforce"],
                "turn_one_bytes": [len(value.encode()) for value in turn_one],
                "turn_one_sha256": map_hashes,
                "stdout_frames": [
                    [len(stream) for stream in game_streams] for game_streams in streams
                ],
                "stdout_sha256": [
                    [stream_sha256(stream) for stream in game_streams]
                    for game_streams in streams
                ],
                "gates": gates,
                "pass": all(gates.values()),
            }
        )

    payload = {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "protocol": "legend-top5-common-seed-bank-aa-protocol-2026-07-19.md",
        "bank": str(args.bank),
        "bank_sha256": bank_sha,
        "panel": str(args.panel),
        "integrity": integrity,
        "per_block": per_block,
        "bank_validated": all(integrity.values()) and all(row["pass"] for row in per_block),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))
    return 0 if payload["bank_validated"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
