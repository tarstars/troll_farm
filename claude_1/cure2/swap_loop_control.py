#!/usr/bin/env python3
"""Controls C-5 and C-6 — the two counters that can stop Candidate 2, computed from the wire.

G-0 §8 and §9 pre-committed both, before any number existed:

  C-6  the same unordered pair exchanging on CONSECUTIVE turns  -> 0, and a positive count
       FALSIFIES Theorem 1 (the immediate back-swap is unrepresentable without a lock).
  C-5  the same unordered pair exchanging twice within 6 turns  -> 0, and any positive count is a
       pre-committed STOP AND ASK, reported with games, turns, ids and targets.

The input is the `census.swap_events` array of an alpha-parity/panel report: one entry per turn
that granted at least one exchange, carrying the `S` movers and the `X` displaced partners read
off the v5 payload. Pairing is unambiguous whenever a turn granted exactly one exchange; a turn
with two or more is reported as AMBIGUOUS and counted against the gate rather than guessed, since
the wire does not say which `S` went with which `X`.

    python3 claude_1/cure2/swap_loop_control.py claude_1/cure2/results/fixtures-instrument.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WINDOW = 6


def main() -> int:
    reports = [Path(a) for a in sys.argv[1:]] or [
        Path("claude_1/cure2/results/fixtures-instrument.json")]
    events, ambiguous = [], []
    for path in reports:
        census = json.loads(path.read_text())["census"]
        for event in census["swap_events"]:
            if len(event["movers"]) != 1 or len(event["displaced"]) != 1:
                ambiguous.append(event)
                continue
            events.append({"game": event["game"], "turn": event["turn"],
                           "mover": event["movers"][0], "displaced": event["displaced"][0]})

    by_pair: dict[tuple, list] = {}
    for event in events:
        key = (event["game"], tuple(sorted((event["mover"], event["displaced"]))))
        by_pair.setdefault(key, []).append(event)

    c5, c6 = [], []
    for (game, pair), rows in sorted(by_pair.items()):
        rows.sort(key=lambda r: r["turn"])
        for previous, current in zip(rows, rows[1:]):
            gap = current["turn"] - previous["turn"]
            record = {"game": game, "pair": list(pair), "first_turn": previous["turn"],
                      "second_turn": current["turn"], "gap": gap,
                      "first_mover": previous["mover"], "second_mover": current["mover"],
                      "reversed": current["mover"] == previous["displaced"]}
            if gap <= WINDOW:
                c5.append(record)
            if gap == 1:
                c6.append(record)

    report = {
        "control": "C-5 / C-6 swap-loop counters",
        "task": "20260825-dance-cure-candidate-2-swap",
        "window_turns": WINDOW,
        "inputs": [str(p) for p in reports],
        "exchanges": len(events),
        "ambiguous_turns": len(ambiguous),
        "c6_consecutive_turn_repeats": len(c6),
        "c6_verdict": "PASS" if not c6 and not ambiguous else "FAIL",
        "c6_meaning": ("0 == Theorem 1 survives its own falsifier on this corpus; a positive "
                       "count would mean the immediate back-swap IS representable"),
        "c5_repeats_within_window": len(c5),
        "c5_verdict": "PASS" if not c5 and not ambiguous else "STOP_AND_ASK",
        "c5_meaning": ("any positive count is the pre-committed stop: the rule is not looping "
                       "within a turn, it is looping across turns, and G-0 §10 says that is "
                       "reported and ruled on, never patched with a lock"),
        "c5_rows": c5,
        "c6_rows": c6,
        "ambiguous_rows": ambiguous,
        "pairs": {f"{game}:{pair[0]}-{pair[1]}": [r["turn"] for r in rows]
                  for (game, pair), rows in sorted(by_pair.items())},
    }
    out = Path("claude_1/cure2/results/swap-loop-control.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"  exchanges {len(events)}  ambiguous turns {len(ambiguous)}")
    print(f"  C-6 consecutive-turn repeats {len(c6)} -> {report['c6_verdict']}")
    print(f"  C-5 repeats within {WINDOW} turns {len(c5)} -> {report['c5_verdict']}")
    for row in c5:
        print(f"    {row['game']} pair {row['pair']} turns {row['first_turn']}->"
              f"{row['second_turn']} gap {row['gap']} reversed={row['reversed']}")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
