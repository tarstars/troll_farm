#!/usr/bin/env python3
"""Check that the ladder resident's per-turn diagnostic line survives the platform intact.

Board row 0-3's data gate, and codex_1's condition on the champion+v6 instrument
(`20260826T150650Z`): the arm emits a payload of ~328 characters, longer than anything
in the collected corpus so far (127), so **decode one collected ladder game before
treating the telemetry as evidence**.

Read-only. Scans raw replays for games played by the given agent ids (our submissions),
pulls every `MSG` line our seat emitted, reports the payload-length distribution, and
decodes each payload with `claude_1/narrate6/narrate6.py` (v6) — reporting decode
failures and any sign of truncation (a payload that is not parseable *and* sits at the
maximum observed length is the truncation signature).

Usage:
  python3 local_claude_1/narrate/collected_payload_check.py --agents 6664057,6664418,6664787
  python3 local_claude_1/narrate/collected_payload_check.py --agents 6664057 --games data/raw/games --since 900000000
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]


def load_decoder():
    """Import narrate6 without requiring it to be on sys.path."""
    path = REPO / "claude_1" / "narrate6" / "narrate6.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("narrate6", path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # a decoder that will not import is itself the finding
        print(f"narrate6 failed to import: {exc}", file=sys.stderr)
        return None
    return module


def seat_of(replay: dict, agent_ids: set[int]) -> int | None:
    """Seat index of the first agent in `agent_ids`, from the replay's own agents array."""
    for agent in replay.get("agents") or []:
        if agent.get("agentId") in agent_ids:
            index = agent.get("index")
            return index if index is not None else agent.get("position")
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agents", required=True, help="comma-separated agent ids of our submissions")
    ap.add_argument("--games", default="/home/tarstars/prj/troll_farm/data/raw/games",
                    help="directory of raw replays (default: the collector's, in the main checkout — the worktree has none)")
    ap.add_argument("--since", type=int, default=0, help="only gameIds greater than this")
    ap.add_argument("--max-games", type=int, default=0, help="stop after N matching games (0 = all)")
    ap.add_argument("--out", default="", help="write the report as JSON here")
    args = ap.parse_args()

    agent_ids = {int(a) for a in args.agents.split(",") if a.strip()}
    games_dir = pathlib.Path(args.games)
    decoder = load_decoder()

    lengths: list[int] = []
    decode_fail: list[tuple[str, int, str]] = []
    matched: list[str] = []
    per_game: dict[str, dict] = {}
    scanned = 0

    for path in sorted(games_dir.glob("*.json")):
        gid = path.stem
        if args.since and gid.isdigit() and int(gid) <= args.since:
            continue
        scanned += 1
        try:
            replay = json.loads(path.read_text())
        except Exception:
            continue
        seat = seat_of(replay, agent_ids)
        if seat is None:
            continue
        matched.append(gid)
        game_lengths: list[int] = []
        game_fail = 0
        for frame in replay.get("frames") or []:
            if frame.get("agentId") != seat:
                continue
            stdout = frame.get("stdout") or ""
            for line in stdout.splitlines():
                # The decoder owns the wire syntax: it knows which `;`-separated fragments
                # are MSG tokens. Splitting the line here instead was wrong and produced
                # decode "failures" that were the harness's, not the platform's.
                fragments = (
                    decoder.msg_fragments(line)
                    if decoder is not None
                    else [f for f in line.split(";") if f.strip().startswith("MSG ")]
                )
                for fragment in fragments:
                    payload = fragment.strip()
                    game_lengths.append(len(payload))
                    lengths.append(len(payload))
                    if decoder is not None:
                        try:
                            decoder.decode(payload)
                        except Exception as exc:
                            game_fail += 1
                            if len(decode_fail) < 20:
                                decode_fail.append((gid, len(payload), f"{type(exc).__name__}: {exc}"))
        per_game[gid] = {
            "payloads": len(game_lengths),
            "max_len": max(game_lengths) if game_lengths else 0,
            "decode_failures": game_fail,
        }
        if args.max_games and len(matched) >= args.max_games:
            break

    report = {
        "games_scanned": scanned,
        "games_matched": len(matched),
        "agent_ids": sorted(agent_ids),
        "payload_lines": len(lengths),
        "payload_len_min": min(lengths) if lengths else 0,
        "payload_len_max": max(lengths) if lengths else 0,
        "payload_len_hist_top": collections.Counter(lengths).most_common(5),
        "decode_failures": len(decode_fail),
        "decode_failure_examples": decode_fail,
        "decoder": "narrate6" if decoder else "ABSENT (report is lengths only)",
        "truncation_suspected": bool(
            lengths
            and decode_fail
            and max(l for _, l, _ in decode_fail) == max(lengths)
        ),
        "per_game": per_game,
    }
    text = json.dumps(report, indent=2)
    if args.out:
        pathlib.Path(args.out).write_text(text + "\n")
    print(text if len(text) < 4000 else json.dumps({k: v for k, v in report.items() if k != "per_game"}, indent=2))
    return 0 if not report["truncation_suspected"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
