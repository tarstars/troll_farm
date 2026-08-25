#!/usr/bin/env python3
"""C-5 evidence rows in the form G-0 Addenda A and B require — cells and targets, never an equality.

Addendum B (codex_1's §4.3 correction) binds G-1: a reversal is written from the ACTUAL cells and
targets read on the reversal turn, never from the false invariant "B stayed on M's old cell".
Addendum A binds the split: every C-5 positive names which side's target moved — the dancer's
(Theorem 2(a)) or the worker's (Theorem 2(b)).

So each row here carries, for the reversal at turn t':

    both units' cells at t'-1 and at t'      (from the referee trace, not from the payload)
    both units' chosen and wanted targets at t'-1 and t'   (from the v5 payload)
    which side's target moved between t'-1 and t'
    the branch letters on both turns

    python3 claude_1/cure2/c5_evidence.py OSC-006,OSC-007
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/narrate5"):
    sys.path.insert(0, str(REPO / _p))

import fixture_harness as fh          # noqa: E402
import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402
import narrate5 as n5                 # noqa: E402

ARM = HERE / "arm-instrument.rs"


def payload_rows(lines):
    """turn -> (units, meta) decoded from the wire; refuses anything off-grammar."""
    out = {}
    for index, line in enumerate(lines, 1):
        frags = n5.msg_fragments(line)
        if len(frags) != 1:
            raise SystemExit(f"turn {index}: {len(frags)} MSG fragments")
        turn, units, _order, _banner, meta = n5.decode(frags[0].strip())
        out[turn] = (units, meta)
    return out


def main() -> int:
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else ["OSC-006", "OSC-007"]
    cfg = json.loads(fh.CONFIG.read_text())
    sits = fh.load_situations(only)
    games = []
    with tempfile.TemporaryDirectory(prefix="cure2-c5-") as wd:
        binary = Path(wd) / "arm.bin"
        sh.compile_text(ARM.read_text(), binary, crate="cure2_c5_arm")
        import trace_detectors as td
        for sit in sits:
            spec = fh.spec_for(sit, cfg)
            ref = fp.make_referee(spec)
            transcript, commands = rt.run_binary_custom(binary, ref, int(cfg["turns"]))
            lines = commands.rstrip("\n").split("\n")
            trace = td.build_trace(transcript, commands)
            rows = payload_rows(lines)
            cells = {t: {u.id: tuple(u.cell) for u in trace.state(t).own_units()}
                     for t in range(1, min(trace.T, len(lines)) + 1)}
            swaps = [(t, sorted(i for i, u in rows[t][0].items() if u[2] == "S"),
                      sorted(i for i, u in rows[t][0].items() if u[2] == "X"))
                     for t in sorted(rows) if rows[t][1]["sw"]]
            events = []
            for turn, s_ids, x_ids in swaps:
                if len(s_ids) != 1 or len(x_ids) != 1:
                    events.append({"turn": turn, "ambiguous": True,
                                   "movers": s_ids, "displaced": x_ids})
                    continue
                mover, partner = s_ids[0], x_ids[0]
                prev = rows.get(turn - 1, ({}, {}))[0]
                here = rows[turn][0]
                events.append({
                    "turn": turn, "mover": mover, "displaced": partner,
                    "cells_before": {str(k): v for k, v in cells.get(turn - 1, {}).items()},
                    "cells_on_turn": {str(k): v for k, v in cells.get(turn, {}).items()},
                    "targets_before": {str(k): {"chosen": v[0], "want": v[1], "branch": v[2]}
                                       for k, v in prev.items()},
                    "targets_on_turn": {str(k): {"chosen": v[0], "want": v[1], "branch": v[2]}
                                        for k, v in here.items()},
                    "mover_target_moved": (mover in prev and prev[mover][0] != here[mover][0]),
                    "partner_target_moved": (partner in prev
                                             and prev[partner][0] != here[partner][0]),
                })
            pairs = {}
            for event in events:
                if event.get("ambiguous"):
                    continue
                key = tuple(sorted((event["mover"], event["displaced"])))
                pairs.setdefault(key, []).append(event["turn"])
            reversals = []
            for index in range(1, len(events)):
                a, b = events[index - 1], events[index]
                if a.get("ambiguous") or b.get("ambiguous"):
                    continue
                if sorted((a["mover"], a["displaced"])) != sorted((b["mover"], b["displaced"])):
                    continue
                gap = b["turn"] - a["turn"]
                if gap > 6:
                    continue
                # Addendum A's split, measured over the RIGHT window. Theorem 2 asks whether a
                # unit's goal moved between the FIRST exchange (when the worker stood still with
                # its goal on or at its work square) and the reversal — not between the two turns
                # either side of the reversal, where nothing need have changed at all.
                first_targets = a["targets_on_turn"]
                second_targets = b["targets_on_turn"]
                moved = {uid: (uid in first_targets and uid in second_targets
                               and first_targets[uid]["chosen"] != second_targets[uid]["chosen"])
                         for uid in map(str, sorted((a["mover"], a["displaced"])))}
                b["mover_target_moved_since_first"] = moved.get(str(b["mover"]))
                b["partner_target_moved_since_first"] = moved.get(str(b["displaced"]))
                b["targets_at_first_exchange"] = first_targets
                if b["partner_target_moved"] and not b["mover_target_moved"]:
                    side = "worker (Theorem 2(b): the standing unit's goal moved past its square)"
                elif b["mover_target_moved"] and not b["partner_target_moved"]:
                    side = "dancer (Theorem 2(a): the blocked unit's goal churned)"
                elif b["mover_target_moved"] and b["partner_target_moved"]:
                    side = "both targets moved"
                else:
                    side = "neither target moved"
                since_first = ("worker" if (b["partner_target_moved_since_first"]
                                            and not b["mover_target_moved_since_first"])
                               else "dancer" if (b["mover_target_moved_since_first"]
                                                 and not b["partner_target_moved_since_first"])
                               else "both" if b["partner_target_moved_since_first"]
                               else "neither")
                reversals.append({"first_turn": a["turn"], "second_turn": b["turn"], "gap": gap,
                                  "which_side_moved_since_first_exchange": since_first,
                                  "pair": sorted((a["mover"], a["displaced"])),
                                  "reversed_direction": b["mover"] == a["displaced"],
                                  "which_side_moved": side, "detail": b})
            games.append({"id": sit["id"], "exchanges": len(events),
                          "pairs": {f"{k[0]}-{k[1]}": v for k, v in pairs.items()},
                          "c5_reversals": reversals, "events": events})
            print(f"  {sit['id']}: {len(events)} exchanges, {len(reversals)} C-5 reversals")
            for row in reversals:
                print(f"    t{row['first_turn']}->t{row['second_turn']} gap {row['gap']} "
                      f"pair {row['pair']} reversed={row['reversed_direction']} — "
                      f"{row['which_side_moved']} | since the first exchange: "
                      f"{row['which_side_moved_since_first_exchange']}")

    out = HERE / "results" / "c5-evidence-fixtures.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "control": "C-5 evidence rows (Addenda A and B)",
        "task": "20260825-dance-cure-candidate-2-swap",
        "arm": str(ARM.relative_to(REPO)),
        "games": games,
    }, indent=2, sort_keys=True) + "\n")
    print(f"  -> {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
