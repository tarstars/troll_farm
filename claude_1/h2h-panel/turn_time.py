#!/usr/bin/env python3
"""Per-turn wall time of one compiled bot inside the h2h referee, against the platform's budget.

Plain words for the owner
-------------------------
`h2h.py` only counts turns past 5 s. The platform's limit is 1000 ms on turn 1 and 50 ms on every
later turn (`docs/mechanics.md`). This script plays a few panel maps with the bot under test on
both seats against the champion of record, wraps every call to the bot's seat with a clock, and
prints the first-turn maximum and the warm median / p99 / maximum, so a bot's time budget is
reported before its 400-game run rather than assumed.

Use
---
    python3 claude_1/h2h-panel/turn_time.py --bot cgauto/submissions/candidate-nn-clone.rs --maps 3
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "local_claude_1" / "nn-bot"))

import bench                      # noqa: E402
import h2h                        # noqa: E402
import semantic_harness as sh     # noqa: E402

CHAMPION = REPO / "cgauto" / "submissions" / "candidate-champion-denial-off-v6-instrument.rs"
PANEL = HERE / "panel-200-seed1.jsonl"
FIRST_TURN_LIMIT_MS = 1000.0
TURN_LIMIT_MS = 50.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bot", type=Path, required=True)
    ap.add_argument("--opponent", type=Path, default=CHAMPION)
    ap.add_argument("--panel", type=Path, default=PANEL)
    ap.add_argument("--maps", type=int, default=3)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    plan = h2h.load_panel(args.panel, args.maps)
    samples: dict[str, list[float]] = {"first": [], "warm": []}
    watched: set[int] = set()
    original_turn = bench.BotProcess.turn

    def timed_turn(self, block: str) -> str:
        if id(self) not in watched:
            return original_turn(self, block)
        turn_no = getattr(self, "_tt_turn", 0) + 1
        self._tt_turn = turn_no
        t0 = time.perf_counter()
        out = original_turn(self, block)
        ms = (time.perf_counter() - t0) * 1000.0
        samples["first" if turn_no == 1 else "warm"].append(ms)
        return out

    original_init = bench.BotProcess.__init__

    def watched_init(self, binary, header):
        original_init(self, binary, header)
        if Path(binary).name == "bot.bin":
            watched.add(id(self))

    bench.BotProcess.turn = timed_turn
    bench.BotProcess.__init__ = watched_init

    with tempfile.TemporaryDirectory(prefix="turn-time-") as wd:
        policy_bin, bot_bin = Path(wd) / "policy.bin", Path(wd) / "bot.bin"
        sh.compile_text(args.opponent.read_text(), policy_bin, crate="tt_policy")
        sh.compile_text(args.bot.read_text(), bot_bin, crate="tt_bot")
        games = 0
        for rec, draw in plan:
            for policy_seat in (0, 1):
                h2h.play(rec, draw, policy_bin, bot_bin, policy_seat)
                games += 1

    warm = sorted(samples["warm"])
    first = samples["first"]
    p99 = warm[min(len(warm) - 1, int(round(0.99 * (len(warm) - 1))))] if warm else float("nan")
    report = {
        "bot": h2h.rel(args.bot),
        "bot_sha256": hashlib.sha256(args.bot.read_bytes()).hexdigest(),
        "opponent": h2h.rel(args.opponent),
        "games": games, "turns_timed": len(warm) + len(first),
        "first_turn_max_ms": round(max(first), 3) if first else None,
        "warm_median_ms": round(statistics.median(warm), 3) if warm else None,
        "warm_p99_ms": round(p99, 3),
        "warm_max_ms": round(warm[-1], 3) if warm else None,
        "warm_over_50ms": sum(1 for x in warm if x > TURN_LIMIT_MS),
        "platform_limits_ms": {"first_turn": FIRST_TURN_LIMIT_MS, "turn": TURN_LIMIT_MS},
        "note": "wall time around the pipe round-trip on this host, referee included in neither figure; "
                "the clock also counts the pipe and the host's load",
    }
    inside = (report["first_turn_max_ms"] or 0) <= FIRST_TURN_LIMIT_MS and report["warm_over_50ms"] == 0
    report["inside_platform_budget"] = inside
    print(json.dumps(report, indent=1))
    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=1) + "\n")
    return 0 if inside else 1


if __name__ == "__main__":
    sys.exit(main())
