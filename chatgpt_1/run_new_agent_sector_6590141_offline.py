#!/usr/bin/env python3
"""Run the frozen E7a live-sector analysis from the host's validated replay cache.

This is the preferred project-host path. It performs no network calls. Exact game IDs and the
one-submission identity gate come from the committed top-15 inventory; full game results come
from ``data/raw/games/<game_id>.json``. The compact output contract is shared with
:mod:`new_agent_sector_6590141_collect`.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from chatgpt_1 import new_agent_sector_6590141_collect as core

DEFAULT_INVENTORY = (
    ROOT
    / "data/analysis/live-agent-6553250"
    / "top15-public-battle-inventory-2026-08-02.json"
)
DEFAULT_RAW = ROOT / "data/raw/games"


def find_agent(inventory: dict[str, Any], agent_id: int) -> dict[str, Any]:
    matches = [row for row in inventory.get("agents") or [] if int(row["agent_id"]) == agent_id]
    if len(matches) != 1:
        raise ValueError(f"inventory has {len(matches)} rows for agent {agent_id}")
    return matches[0]


def normalized_game(path: Path) -> dict[str, Any]:
    game = json.loads(path.read_text(encoding="utf-8"))
    for agent in game.get("agents") or []:
        if agent.get("index") == 0:
            agent["index"] = "0"
    return game


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--csv", type=Path, default=core.DEFAULT_CSV)
    parser.add_argument("--json", type=Path, default=core.DEFAULT_JSON)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--bootstrap", type=int, default=100_000)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 16:
        raise SystemExit("--jobs must be in 1..16")

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    target = find_agent(inventory, core.AGENT_ID)
    submission_counts = {
        int(key): int(value)
        for key, value in (target.get("submission_id_counts") or {}).items()
    }
    expected = {core.SUBMISSION_ID: 160}
    if submission_counts != expected:
        raise RuntimeError(
            f"exact submission gate failed: {submission_counts}, expected {expected}"
        )
    game_ids = [int(value) for value in target.get("game_ids") or []]
    if len(game_ids) != 160 or len(set(game_ids)) != 160:
        raise RuntimeError(f"expected 160 unique game ids, got {len(game_ids)}")
    if int(target.get("finished") or -1) != 160:
        raise RuntimeError(f"inventory finished count is {target.get('finished')}, expected 160")

    raw_paths = {game_id: args.raw_dir / f"{game_id}.json" for game_id in game_ids}
    missing = [str(path) for path in raw_paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing {len(missing)} cached games; first: {missing[:5]}")

    ladder = {
        int(row["agent_id"]): {
            "rank": int(row.get("rank") or 0),
            "score": float(row.get("score") or 0.0),
            "pseudo": row.get("pseudo"),
        }
        for row in inventory.get("agents") or []
        if row.get("agent_id") is not None
    }
    game_cache = {game_id: normalized_game(path) for game_id, path in raw_paths.items()}

    def offline_post(service: str, payload: Any, retries: int = 4) -> Any:
        del retries
        if service != core.GAME_SERVICE:
            raise RuntimeError(f"offline extractor refuses service {service}")
        game_id = int(payload[0])
        if game_id not in game_cache:
            raise KeyError(f"game {game_id} not in exact inventory")
        return game_cache[game_id]

    core.post = offline_post
    parse = core.parser_module()
    metadata = [
        {
            "game_id": game_id,
            "done": True,
            "observed_order": order,
            "players": [],
        }
        for order, game_id in enumerate(game_ids)
    ]
    rows = []
    failures = []
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = {
            executor.submit(core.game_row, row, ladder, parse): row for row in metadata
        }
        for completed, future in enumerate(as_completed(futures), 1):
            meta = futures[future]
            try:
                rows.append(future.result())
            except Exception as error:
                failures.append({"game_id": meta["game_id"], "error": str(error)})
            if completed % 20 == 0 or completed == len(futures):
                print(f"processed {completed}/{len(futures)} cached games; failures={len(failures)}")
    if failures:
        raise RuntimeError(f"cached extraction failed closed: {failures[:10]}")
    if len(rows) != 160:
        raise RuntimeError(f"extracted {len(rows)} rows, expected 160")

    identity = {
        "listed": 160,
        "matching": 160,
        "matching_finished": 160,
        "matching_pending": 0,
        "unexpected": [],
        "response_sha256": None,
        "inventory_sha256": core.digest(inventory),
        "raw_cache": str(args.raw_dir.relative_to(ROOT)),
        "raw_cache_count": 160,
    }
    ladder_meta = {
        "available": True,
        "source": str(args.inventory.relative_to(ROOT)),
        "agent_count": len(ladder),
        "response_sha256": None,
    }
    report = core.build_report(rows, identity, ladder_meta, args.bootstrap)
    report["services"].update(
        {
            "mode": "offline_validated_cache",
            "network_calls": 0,
            "battle": None,
            "game": None,
            "leaderboard": None,
        }
    )
    core.write_csv(args.csv, rows)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"saved {len(rows)} cached games; selected={report['support']['selected_games']}; "
        f"overall mean={report['overall']['mean_margin']:+.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
