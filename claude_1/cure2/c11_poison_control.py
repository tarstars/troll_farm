#!/usr/bin/env python3
"""C-11's poison control: make the memory stale on purpose and prove the checker screams.

C-11 reported 0 mismatches. That number means nothing unless a wrong `prev_cells` would have
produced a positive one, so this driver builds a POISON arm from `arm-c11.rs` whose only further
change is that the end-of-turn write is skipped on odd turns:

    if view.turn%2==0{ *prev_cells = <this turn's own cells>; }

so on every odd turn the map read is two turns old rather than one. The arm is otherwise the C-11
arm, printing the same `PREVREAD` lines, and it is run through the SAME comparison function
(`c11_prev_cells_check.check_game`) on the same fixtures. This control PASSES only when the
checker reports mismatches; a silent poison run means C-11 is an inert counter, exactly the
failure mode control C-7 exists to catch for C-5 and C-6.

The poison arm is NOT print-only -- a stale memory changes the swap predicate and therefore the
commands -- so G-A is not applied here and the arm is never a candidate for anything.

    python3 claude_1/cure2/c11_poison_control.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))
for _p in ("claude_1/t1", "claude_1/pipeline", "claude_1/banana-restoration-r2",
           "claude_1/narrate5"):
    sys.path.insert(0, str(REPO / _p))

import fixture_harness as fh          # noqa: E402
import fuzz_panel as fp               # noqa: E402
import regression_tests as rt         # noqa: E402
import semantic_harness as sh         # noqa: E402

import c11_prev_cells_check as c11    # noqa: E402

SRC = HERE / "arm-c11.rs"
OUT = HERE / "results" / "c11-poison-control.json"

ANCHOR = ("                    *prev_cells=view.units.iter().filter(|unit|unit.player==0)"
          ".map(|unit|(unit.id,unit.cell)).collect();\n")
POISON = ("                    if view.turn%2==0{*prev_cells=view.units.iter()"
          ".filter(|unit|unit.player==0).map(|unit|(unit.id,unit.cell)).collect();}\n")


def poison_source() -> str:
    text = SRC.read_text()
    if text.count(ANCHOR) != 1:
        raise c11.GateError(f"write anchor matched {text.count(ANCHOR)} times, refusing")
    out = text.replace(ANCHOR, POISON)
    if len(out.splitlines()) != len(text.splitlines()):
        raise c11.GateError("the poison edit changed the line count")
    return out


def main() -> int:
    source = poison_source()
    digest = hashlib.sha256(source.encode()).hexdigest()
    rows = []
    with tempfile.TemporaryDirectory(prefix="cure2-c11p-") as wd:
        binary = Path(wd) / "poison.bin"
        sh.compile_text(source, binary, crate="cure2_arm_c11_poison")
        cfg = json.loads(fh.CONFIG.read_text())
        for sit in fh.load_situations(None):
            spec = fh.spec_for(sit, cfg)
            transcript, cmds, err = c11.run_capturing(binary, fp.make_referee(spec),
                                                      int(cfg["turns"]))
            rows.append(c11.check_game(sit["id"], transcript, cmds, err))

    total = c11.totals(rows)
    fired = [r["game"] for r in rows if r["mismatches"]]
    result = {
        "control": "C-11 poison: prev_cells written only on even turns",
        "task": "20260825-dance-cure-candidate-2-swap",
        "poison_arm_sha256": digest,
        "poison_edit": "the end-of-turn *prev_cells write wrapped in `if view.turn%2==0`",
        "print_only": "NOT print-only by construction — a stale memory changes the commands",
        "fixtures": len(rows),
        "games_where_c11_fired": fired,
        "summary": {k: v for k, v in total.items() if not isinstance(v, list)},
        "example_mismatch": total["mismatch_rows"][0] if total["mismatch_rows"] else None,
        "verdict": ("PASS — the C-11 comparison detects a stale prev_cells"
                    if total["mismatches"] else
                    "FAIL — C-11 IS INERT: a two-turn-old memory passed the check"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=1))
    print(f"fired on {len(fired)} of {len(rows)} fixtures")
    print("verdict:", result["verdict"])
    print("wrote", OUT.relative_to(REPO))
    return 0 if total["mismatches"] else 1


if __name__ == "__main__":
    sys.exit(main())
