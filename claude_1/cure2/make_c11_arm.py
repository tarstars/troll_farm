#!/usr/bin/env python3
"""Build the PRINT-ONLY C-11 arm that reports the `prev_cells` map READ on each turn.

`arm-c11.rs` = `arm-instrument.rs` + exactly ONE `eprintln!` and nothing else. G-0 §4.0 names
A-2 -- "`prev_cells` read on turn `t` equals the cells own units occupied on turn `t-1`, and is
absent for a unit not alive at `t-1`" -- as an assumption, and control C-11 must produce 100 %.
The v5 wire does not carry each unit's `prev_cells` read, so the read has to be printed at the
point of use; a wire extension would change the payload and cost the parity story.

  PREVREAD t=<turn> n=<entries> p=<id>:<x>,<y>;...   -- emitted at the top of
      `resolve_move_conflicts_hold`, BEFORE the loop that rewrites `*prev_cells` at its end, so
      the line is the value the swap predicate actually read on that turn.

Print-only is not asserted, it is GATED: `c11_prev_cells_check.py` refuses unless this arm's
stdout command stream is byte-identical to the instrument arm's on every game it runs.

    python3 claude_1/cure2/make_c11_arm.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "arm-instrument.rs"
OUT = HERE / "arm-c11.rs"

ANCHOR = ("                let swap_enabled=Self::SWAP_RULE_ENABLED&&"
          "!(Self::SWAP_P3_SCOPING_ENABLED&&orchard_inert.unwrap_or(false));\n")
LINE = ('                eprintln!("PREVREAD t={} n={} p={}",view.turn,prev_cells.len(),'
        'prev_cells.iter().map(|(id,cell)|format!("{}:{},{}",id,cell.0,cell.1))'
        '.collect::<Vec<String>>().join(";"));\n')


def main() -> int:
    text = SRC.read_text()
    if text.count(ANCHOR) != 1:
        print(f"anchor matched {text.count(ANCHOR)} times, refusing", file=sys.stderr)
        return 1
    text = text.replace(ANCHOR, LINE + ANCHOR)
    OUT.write_text(text)
    added = len(text.splitlines()) - len(SRC.read_text().splitlines())
    if added != 1:
        print(f"expected exactly 1 added line, got {added}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(text.encode()).hexdigest()
    (HERE / "arm-c11.rs.sha256").write_text(f"{digest}  arm-c11.rs\n")
    print(f"wrote {OUT.name}  +1 line  sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
