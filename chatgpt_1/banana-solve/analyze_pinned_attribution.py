#!/usr/bin/env python3
"""Explain raw pinned fuzz blocks with parent/prefix evidence.

This is diagnostic only; it does not replace the coordinator-authorized panel.
For every raw blocking row it records:

* candidate/parent full command SHA and byte equality;
* the first command-line divergence;
* fresh parent detector results on the paired parent trace;
* whether every candidate detector episode is reproduced by the parent inside
  the aligned command prefix.

An episode is classified ``inherited_aligned_prefix`` only when its complete
turn interval ends before the first command divergence (or the streams are
fully byte-identical) and an equal parent detector episode exists. Everything
else remains ``candidate_or_post_divergence`` for the corrected standing gate.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("pinned_trace_detectors", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def first_divergence(candidate: str, parent: str) -> int | None:
    left = candidate.splitlines()
    right = parent.splitlines()
    for turn, (a, b) in enumerate(zip(left, right), start=1):
        if a != b:
            return turn
    if len(left) != len(right):
        return min(len(left), len(right)) + 1
    return None


def episode_key(episode: dict[str, Any]) -> str:
    return json.dumps(episode, sort_keys=True, separators=(",", ":"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-detectors", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--failures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    td = load_module(args.trace_detectors.resolve())
    panel = json.loads(args.result.read_text())
    rows = []
    for game in panel.get("games", []):
        if not game.get("block"):
            continue
        game_id = f"{game['map_id']}-s{game['seat']}"
        directory = args.failures / game_id
        cand_path = directory / "candidate-commands.txt"
        parent_path = directory / "parent-commands.txt"
        cand_transcript_path = directory / "candidate-transcript.txt"
        parent_transcript_path = directory / "parent-transcript.txt"
        if not all(path.exists() for path in (
            cand_path, parent_path, cand_transcript_path, parent_transcript_path
        )):
            rows.append({
                "game": game_id,
                "status": "missing_failure_artifacts",
                "violations": game.get("violations", []),
            })
            continue

        cand_bytes = cand_path.read_bytes()
        parent_bytes = parent_path.read_bytes()
        cand_text = cand_bytes.decode()
        parent_text = parent_bytes.decode()
        divergence = first_divergence(cand_text, parent_text)
        parent_trace = td.build_trace(
            parent_transcript_path.read_text(), parent_text
        )
        parent_results = {
            result["detector"]: result
            for result in td.run_all(parent_trace)
        }

        classified = []
        for violation in game.get("violations", []):
            detector = violation.get("detector")
            episodes = violation.get("episodes") or []
            parent_episodes = (
                parent_results.get(detector, {}).get("episodes", [])
                if detector else []
            )
            parent_keys = {episode_key(row) for row in parent_episodes}
            matches = [episode_key(row) in parent_keys for row in episodes]
            complete_prefix = bool(episodes) and all(
                divergence is None
                or int(row.get("turn_end", row.get("turn_start", 10**9))) < divergence
                for row in episodes
            )
            reproduced = bool(episodes) and all(matches)
            inherited = (cand_bytes == parent_bytes) or (
                complete_prefix and reproduced
            )
            classified.append({
                "property": violation.get("property"),
                "detector": detector,
                "count": violation.get("count"),
                "episodes": episodes,
                "parent_episodes": parent_episodes,
                "episode_parent_matches": matches,
                "complete_aligned_prefix": complete_prefix,
                "parent_reproduces": reproduced,
                "classification": (
                    "inherited_aligned_prefix"
                    if inherited
                    else "candidate_or_post_divergence"
                ),
            })

        rows.append({
            "game": game_id,
            "map_id": game.get("map_id"),
            "seat": game.get("seat"),
            "class": game.get("class"),
            "profile": game.get("profile"),
            "seed": game.get("seed"),
            "banana_active": game.get("banana_active"),
            "candidate_command_sha256": sha(cand_bytes),
            "parent_command_sha256": sha(parent_bytes),
            "command_streams_byte_equal": cand_bytes == parent_bytes,
            "first_command_divergence_turn": divergence,
            "violations": classified,
        })

    raw_blocks = len(rows)
    inherited_games = sum(
        bool(row.get("violations"))
        and all(
            violation.get("classification") == "inherited_aligned_prefix"
            for violation in row["violations"]
        )
        for row in rows
    )
    surviving = [
        row for row in rows
        if any(
            violation.get("classification") != "inherited_aligned_prefix"
            for violation in row.get("violations", [])
        )
    ]
    report = {
        "schema": "banana-r2-pinned-attribution-diagnostic/1",
        "raw_blocking_games": raw_blocks,
        "fully_inherited_games": inherited_games,
        "candidate_or_post_divergence_games": len(surviving),
        "surviving_game_ids": [row["game"] for row in surviving],
        "games": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        key: report[key]
        for key in (
            "raw_blocking_games",
            "fully_inherited_games",
            "candidate_or_post_divergence_games",
            "surviving_game_ids",
        )
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
