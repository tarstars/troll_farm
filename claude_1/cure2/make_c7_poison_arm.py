#!/usr/bin/env python3
"""Build the C-7 POISON arm `arm-c7poison.rs` -- the exchange predicate gutted to
"swap on every block" -- against which controls C-5 and C-6 must fire LOUDLY.

G-0 §9 lists C-7 as the inertness control for the two swap-loop counters. C-5 (the same
unordered pair exchanging twice within 6 turns) and C-6 (the same pair on CONSECUTIVE turns)
are only evidence if a bot that DOES loop makes them move. On the candidate arm C-6 is 0; a
zero from a counter that cannot count is worth nothing.

What is DELETED from `arm-instrument.rs`, and nothing else:

  P1  clause 4's STANDING memory -- `matches!(prev_cells.get(&other), Some(p) if *p == landing)`.
      This is the ONLY cross-turn memory in the predicate and the only thing that can stop an
      immediate back-swap: a unit displaced on turn t is, on turn t+1, standing on a cell it did
      not occupy at t-1, so the real rule refuses to exchange with it. Deleting it is precisely
      the poison C-6 exists to catch.
  P2  clause 5's adjacency test (`is_adjacent`) -- a landing two cells away now exchanges.
  P3  clause 6, both halves -- the teammate-on-the-goal skip and the strictly-beyond BFS test.
      Every blocked landing with an own occupant now exchanges regardless of progress.

What is RETAINED, and why -- these are NOT part of the loop question:

  R1  `!moving_ids.contains(&other)` and `!displaced.contains(&other)`. Both are per-pass locals
      with no memory across turns, so neither can suppress a back-swap on the NEXT turn, which
      is what C-5/C-6 count. They are kept because without them one pass can rewrite the same
      unit's command twice; the run would then measure a malformed command stream rather than a
      loop, and the pairing gate (G-P) would abort instead of reporting a fire.
  R2  the positional `slot_by_id` map. It is the mechanism that writes the partner's command,
      not a test of whether to exchange.

    python3 claude_1/cure2/make_c7_poison_arm.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "arm-instrument.rs"
OUT = HERE / "arm-c7poison.rs"

STANDING_OLD = ("                            Some(other)=>!moving_ids.contains(&other)&&"
                "matches!(prev_cells.get(&other),Some(previous)if*previous==landing)&&"
                "!displaced.contains(&other),None=>false,\n")
STANDING_NEW = ("                            // C-7 POISON P1: clause 4's `prev_cells` standing\n"
                "                            // memory is DELETED. Any own occupant of the\n"
                "                            // landing is now an exchange partner.\n"
                "                            Some(other)=>!moving_ids.contains(&other)&&"
                "!displaced.contains(&other),None=>false,\n")

TESTS_OLD = "".join(Path(__file__).parent.joinpath("arm-instrument.rs").read_text()
                    .splitlines(keepends=True)[935:977])

TESTS_NEW = """                            // C-7 POISON P2/P3: clause 5's adjacency test and BOTH halves
                            // of clause 6 (teammate-on-goal, strictly-beyond) are DELETED. The
                            // slot map survives because it writes the partner's command; it is
                            // mechanism, not predicate.
                            match slot_by_id.as_ref().and_then(|map|map.get(&other).copied()){
                                None=>{
                                    swap_counts[3]+=1;
                                    }
                                Some(other_index)=>{
                                    reserved.insert(landing);
                                    granted.insert(landing);
                                    reserved.insert(unit.cell);
                                    granted.insert(unit.cell);
                                    displaced.insert(other);
                                    commands[index]=format!("MOVE {} {} {}",id,landing.0,landing.1);
                                    commands[other_index]=format!("MOVE {} {} {}",other,unit.cell.0,unit.cell.1);
                                    branch.insert(id,'S');
                                    branch.insert(other,'X');
                                    swap_counts[0]+=1;
                                    continue;
                                    }
                            }
"""


def main() -> int:
    text = SRC.read_text()
    if not TESTS_OLD.lstrip().startswith("if!is_adjacent(unit.cell,landing){"):
        print(f"clause-5/6 block anchor moved: {TESTS_OLD[:80]!r}", file=sys.stderr)
        return 1
    for name, old in (("standing", STANDING_OLD), ("clause 5/6", TESTS_OLD)):
        if text.count(old) != 1:
            print(f"{name} anchor matched {text.count(old)} times, refusing", file=sys.stderr)
            return 1
    text = text.replace(STANDING_OLD, STANDING_NEW).replace(TESTS_OLD, TESTS_NEW)
    OUT.write_text(text)
    digest = hashlib.sha256(text.encode()).hexdigest()
    (HERE / "arm-c7poison.rs.sha256").write_text(f"{digest}  arm-c7poison.rs\n")
    src_lines = SRC.read_text().splitlines()
    out_lines = text.splitlines()
    print(f"wrote {OUT.name}  {len(src_lines)} -> {len(out_lines)} lines  sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
