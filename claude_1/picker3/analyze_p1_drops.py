#!/usr/bin/env python3
r"""Phase 3a analysis — what P1's `self_blocked` veto did on the two named panel games.

Reads the selector-probe stderr produced by `panel_game_probe.py` (which gated it: parity with
the uninstrumented candidate, and row identity against the Phase-2 panel record) and, per turn,
answers one question with the source's own rows:

    Did P1 veto a pair, and if so, did the veto change which pair won -- and to what?

A veto is only *causal* on a turn if the vetoed pair outscored every surviving compatible /
stock-compatible pair.  A veto that removed an already-losing pair changed nothing and is
counted separately, because counting it as a cost would inflate the number.

Nothing here proposes a change to P1.  It measures what P1 did.

Run:  python3 claude_1/picker3/analyze_p1_drops.py
"""
from __future__ import annotations

import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from panel_game_probe import parse_turns  # noqa: E402

LOG = HERE / "probe-stderr.log"
OUT = HERE / "p1-drop-analysis-2026-08-21.json"

# (map, seat) -> the recorded window this game is being diagnosed for, and what fired there.
WINDOWS = {
    ("m004", 0): {"window": [42, 200], "recorded": "P3 (first divergence turn 42); candidate has "
                  "D-1 x1 and NO P4, the floor has D-1 x2 and P4 42-200"},
    ("m021", 1): {"window": [20, 106], "recorded": "P4 20-106 + flag r5-horizon on unit 2; the "
                  "floor has neither"},
}


def runs_of(turns):
    out, start, prev = [], None, None
    for t in turns:
        if start is None:
            start = prev = t
        elif t == prev + 1:
            prev = t
        else:
            out.append([start, prev]); start = prev = t
    if start is not None:
        out.append([start, prev])
    return out


def main():
    parts = re.split(r"^PS2GAME map=(\S+) seat=(\d+)$", LOG.read_text(), flags=re.M)
    games = {}
    for i in range(1, len(parts), 3):
        games[(parts[i], int(parts[i + 1]))] = parse_turns(parts[i + 2])

    result = {"source": str(LOG.name), "note": __doc__.strip().splitlines()[0], "games": {}}
    for key, meta in WINDOWS.items():
        if key not in games:
            raise SystemExit("no probe rows for %s seat %d" % key)
        turns = games[key]
        lo, hi = meta["window"]
        vetoed, causal, causal_to_allwait, inert = [], [], [], []
        for t in sorted(turns):
            pairs = turns[t]["pairs"]
            win = turns[t]["win"]
            dropped = [p for p in pairs if p["p1drop"]]
            if not dropped:
                continue
            vetoed.append(t)
            survivors = [p for p in pairs
                         if not p["p1drop"] and p["compat"] and p["stock"]]
            best_survivor = max((p["sum"] for p in survivors), default=None)
            best_dropped = max(p["sum"] for p in dropped)
            if best_survivor is not None and best_dropped > best_survivor:
                causal.append(t)
                if win is not None and win["sum"] == 0.0:
                    causal_to_allwait.append(t)
            else:
                inert.append(t)
        result["games"]["%s-s%d" % key] = {
            "recorded_finding": meta["recorded"],
            "window": meta["window"],
            "turns_total": len(turns),
            "turns_P1_vetoed_a_pair": len(vetoed),
            "turns_the_veto_changed_the_winner": len(causal),
            "turns_the_veto_changed_the_winner_inside_the_window":
                len([t for t in causal if lo <= t <= hi]),
            "of_those_the_selected_pair_scored_zero_both_units_WAIT":
                len([t for t in causal_to_allwait if lo <= t <= hi]),
            "turns_the_veto_removed_an_already_losing_pair": len(inert),
            "causal_turn_runs": runs_of([t for t in causal if lo <= t <= hi]),
        }
    OUT.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
