#!/usr/bin/env python3
r"""Card `20260822-alpha-progress-regrade` — run the adapter over alpha's changed games.

Grades EVERY base-arm D-1 episode and P4 violation of the games alpha actually changed, with the
accepted two-clause predicate, and prints the per-event table and the restated headline.

Scope, per the card: alpha left **210 of 240 panel games byte-identical**, so only the changed
games can carry a healed event. The 210 are NOT re-graded; they are used once, as a control
(`--controls` in `panel_adapter_controls.py`).

Run:  python3 claude_1/regrade3/panel_regrade.py
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import panel_progress_adapter as A  # noqa: E402

BUCKETS = ["HEALED_WITH_PROGRESS", "QUIET_BUT_STALLED", "WINDOW_ABSENT", "STILL_FIRING"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate-games", default=str(A.CANDIDATE_PACKET))
    ap.add_argument("--floor-games", default=str(A.FLOOR_PACKET))
    ap.add_argument("--json", default=str(HERE / "alpha-progress-regrade-2026-08-22.json"))
    args = ap.parse_args(argv)

    cand_rows, floor_rows = A.load_panels(Path(args.candidate_games), Path(args.floor_games))
    print(f"GATE M re-run: PASS — {len(cand_rows)} (map, seat) games matched on the base arm")

    changed = [k for k in sorted(cand_rows)
               if cand_rows[k]["artifacts"]["candidate_commands"]
               != cand_rows[k]["artifacts"]["parent_commands"]]
    print(f"changed games (command stream differs from the base): {len(changed)} of "
          f"{len(cand_rows)}")

    events = []
    for key in changed:
        events += A.grade_game(key[0], key[1], cand_rows[key], floor_rows[key], arm="candidate")

    by_shape = collections.defaultdict(collections.Counter)
    for e in events:
        by_shape[e["shape"]][e["bucket"]] += 1

    healed_shape = {s: c["HEALED_WITH_PROGRESS"] + c["QUIET_BUT_STALLED"] for s, c in
                    by_shape.items()}

    import hashlib
    prov = {name: {"path": str(path),
                   "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
            for name, path in (("candidate_panel", args.candidate_games),
                               ("floor_panel", args.floor_games))}

    out = {
        "card": "20260822-alpha-progress-regrade",
        "packet_provenance": prov,
        "packet_provenance_note": (
            "Both packets are SCRATCH under /tmp and will not survive a reboot. They are the "
            "retained traces of the 2026-08-21 rev-2 panel run and are pinned here by sha256 so "
            "a re-run can be proven identical rather than assumed. Rebuild command is in "
            "claude_1/swap1/g2-report-rev2-2026-08-21.md (~15 s wall per arm)."),
        "graded_against": "cure alpha rev 2, matched 240-game panel (task 20260821-swap-r1-cure)",
        "predicate": "claude_1/t1/fixture_harness.py:grade — imported, not copied, not modified",
        "panel_games": len(cand_rows),
        "changed_games": len(changed),
        "changed_game_keys": [{"map_id": k[0], "seat": k[1]} for k in changed],
        "buckets_by_shape": {s: dict(c) for s, c in sorted(by_shape.items())},
        "events": events,
    }
    Path(args.json).write_text(json.dumps(out, indent=2) + "\n")

    print("\n  per-event buckets, over the base events of the changed games:")
    for shape in sorted(by_shape):
        c = by_shape[shape]
        print(f"    {shape:4s}  " + "  ".join(f"{b}={c[b]}" for b in BUCKETS)
              + f"   (detector-silent = {healed_shape[shape]})")
    print(f"\n  -> {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
