#!/usr/bin/env python3
"""PRINT-ONLY probe arms for the Candidate 0 fallback clause.

Two arms, one line inserted into each, identical text in both:

    FBFIRE t=<turn> u=<unit> carried=<n> plants=<n> adj=<0|1> out=<len>
           ih=<len(idle_harvest)> bk=<len(bank)>

printed at the top of the `idle_regeneration && chops.is_empty()` fallback, i.e. on every turn on
which the clause fires, on BOTH arms, so "the fallback fired here" is a matched fact rather than an
inference.  `adj=1 && carried>0` is exactly the turn on which the arm's new guard SUPPRESSES the
second bank append (G-0 r2 section 4), so the suppression census is a projection of this one line.

Sources are the READABLE files, which are the same programs as the compacted panel arms:
compact(readable arm) == cgauto/submissions/candidate-0-regeneration-fallback.rs byte for byte, and
compact(readable champion) == compact(candidate-door1-pure-deletion.rs) byte for byte.

Print-only is GATED, not asserted: `probe_parity.py` requires each probe's stdout to be
byte-identical to its own non-probe arm's on every game it is read on.

    python3 claude_1/cure0/make_probe_arms.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

ARMS = {
    "fix": REPO / "readable" / "candidate-0-regeneration-fallback.rs",
    "base": REPO / "readable" / "door1-champion.rs",
}

ANCHOR = "                if idle_regeneration && chops.is_empty() {\n"
PRINT = ('                    eprintln!("FBFIRE t={} u={} carried={} plants={} adj={} out={} '
         'ih={} bk={}", view.turn, unit.id, unit.total_carried(), view.plants.len(), '
         'is_adjacent(unit.cell, view.shacks[0]) as i32, out.len(), '
         'Self::idle_harvest_candidates(view, unit).len(), '
         'Self::bank_candidates(view, unit).len());\n')


def main() -> int:
    for name, src in ARMS.items():
        text = src.read_text()
        if text.count(ANCHOR) != 1:
            print(f"{name}: anchor matched {text.count(ANCHOR)} times, refusing", file=sys.stderr)
            return 1
        out_text = text.replace(ANCHOR, ANCHOR + PRINT)
        added = len(out_text.splitlines()) - len(text.splitlines())
        if added != 1:
            print(f"{name}: expected 1 added line, got {added}", file=sys.stderr)
            return 1
        out = HERE / f"arm-{name}-probe.rs"
        out.write_text(out_text)
        digest = hashlib.sha256(out_text.encode()).hexdigest()
        (HERE / f"{out.name}.sha256").write_text(f"{digest}  {out.name}\n")
        print(f"wrote {out.name}  +{added} line  sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
