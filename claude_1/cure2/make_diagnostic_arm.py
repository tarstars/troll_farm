#!/usr/bin/env python3
"""Build the PRINT-ONLY diagnostic arm that answers the coordinator's clause-6 question.

`arm-diagnostic.rs` = `arm-instrument.rs` + three `eprintln!` lines and nothing else. It exists to
measure, at the predicate itself, the three cells the question asks about:

  SWAPDIAG t m c T L b adj teq   -- every turn a STANDING own partner was found on the landing:
                                    the mover `m`, its cell `c`, the predicate's target `T`, the
                                    landing `L`, the partner `b`, whether `c` and `L` are adjacent,
                                    and whether `T == L` (clause 6, first half).
  SWAPDIST t m b dl dh           -- the two distances clause 6's second half compares.
  SWAPFIRE t m b                 -- the exchange actually granted.

Print-only is not asserted, it is GATED: `swap_target_probe.py` refuses unless this arm's stdout
command stream is byte-identical to the instrument arm's on every game it runs.

    python3 claude_1/cure2/make_diagnostic_arm.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "arm-instrument.rs"
OUT = HERE / "arm-diagnostic.rs"

EDITS = [
    ("                        if standing{\n"
     "                            let other=partner.unwrap_or(id);\n",
     "                        if standing{\n"
     "                            let other=partner.unwrap_or(id);\n"
     '                            eprintln!("SWAPDIAG t={} m={} c={},{} T={},{} L={},{} b={} adj={} teq={}",view.turn,id,unit.cell.0,unit.cell.1,target.0,target.1,landing.0,landing.1,other,is_adjacent(unit.cell,landing) as i32,(target==landing) as i32);\n'),
    ("                                        if d_landing<d_here{\n",
     '                                        eprintln!("SWAPDIST t={} m={} b={} dl={} dh={}",view.turn,id,other,d_landing,d_here);\n'
     "                                        if d_landing<d_here{\n"),
    ("                                            swap_counts[0]+=1;\n",
     '                                            eprintln!("SWAPFIRE t={} m={} b={}",view.turn,id,other);\n'
     "                                            swap_counts[0]+=1;\n"),
]


def main() -> int:
    text = SRC.read_text()
    for old, new in EDITS:
        if text.count(old) != 1:
            print(f"anchor matched {text.count(old)} times, refusing:\n{old!r}", file=sys.stderr)
            return 1
        text = text.replace(old, new)
    OUT.write_text(text)
    added = len(text.splitlines()) - len(SRC.read_text().splitlines())
    if added != 3:
        print(f"expected exactly 3 added lines, got {added}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(text.encode()).hexdigest()
    (HERE / "arm-diagnostic.rs.sha256").write_text(f"{digest}  arm-diagnostic.rs\n")
    print(f"wrote {OUT.name}  +3 lines  sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
