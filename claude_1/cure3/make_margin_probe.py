#!/usr/bin/env python3
"""A PRINT-ONLY probe over the ACCEPTED instrument arm, to measure the joint margin `rho`.

codex_1's `20260826T071429Z` ruling requires, before any Candidate 3 code, the realised score
inputs and `rho` at every exchange of the six loop games, taken from the recorded states rather
than from a candidate run.  The recorded states in `claude_1/cure2/results/loop-anatomy.json` carry
the plants and the unit cells but not the map, the unit stats or the chop arithmetic, so the score
inputs cannot be read off that file.  They are therefore measured at the source that produced them:
two `eprintln!` lines inserted into `claude_1/cure2/arm-instrument.rs`, which is the arm the six
games were recorded with.

  CHOPIN t u cell tree travel chop ret turns wood score freecap
        every input of `chop_candidates`' score for every (unit, tree) pair it scores, so
        `K = chop + ret + 1`, the travel `Delta` and the wood `w` are measured, not modelled;
  CANDS t u n list
        the unit's final candidate list with the scores the selector actually compares, so the
        realised assignment can be reproduced instead of assumed.

No Candidate 3 code exists in this arm.  Print-only is GATED by `margin_probe.py`: the probe's
command stream must equal the plain instrument arm's on every game read, and the exchange turns
must reproduce the recorded ones.

    python3 claude_1/cure3/make_margin_probe.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SRC = REPO / "claude_1" / "cure2" / "arm-instrument.rs"
OUT = HERE / "arm-instrument-marginprobe.rs"

CHOP_ANCHOR = "                    let command=if plant.cell==unit.cell{\n"
CHOP_PRINT = ('                    eprintln!("CHOPIN t={} u={} cell={},{} tree={},{} travel={} '
              'chop={} ret={} turns={} wood={} score={} freecap={}",view.turn,unit.id,unit.cell.0,'
              'unit.cell.1,plant.cell.0,plant.cell.1,travel_turns,chop_turns,return_turns,turns,'
              'wood,score,unit.free_capacity());\n')

CANDS_ANCHOR = "                    by_id.insert(unit.id,candidates);\n"
CANDS_PRINT = ('                    eprintln!("CANDS t={} u={} n={} list={:?}",view.turn,unit.id,'
               'candidates.len(),candidates.iter().map(|c|(c.command.clone(),c.score))'
               '.collect::<Vec<_>>());\n')


def main() -> int:
    text = SRC.read_text()
    for anchor, printer, before in ((CHOP_ANCHOR, CHOP_PRINT, True),
                                    (CANDS_ANCHOR, CANDS_PRINT, True)):
        if text.count(anchor) != 1:
            print(f"anchor matched {text.count(anchor)} times, refusing:\n{anchor!r}",
                  file=sys.stderr)
            return 1
        text = text.replace(anchor, printer + anchor if before else anchor + printer)
    added = len(text.splitlines()) - len(SRC.read_text().splitlines())
    if added != 2:
        print(f"expected 2 added lines, got {added}", file=sys.stderr)
        return 1
    OUT.write_text(text)
    digest = hashlib.sha256(text.encode()).hexdigest()
    (HERE / f"{OUT.name}.sha256").write_text(f"{digest}  {OUT.name}\n")
    print(f"wrote {OUT.name}  +{added} lines  sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
