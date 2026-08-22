#!/usr/bin/env python3
r"""PEEK rev-3 constructed-board controls — with the target map actually supplied.

Task `20260822-peek-planner-target-map`, step 4 (G-1). The corpus sweep found rev 3 **inert**:
989 partner encounters, zero admitted. That number is only interpretable if the predicate can be
shown to fire at all — an alpha that can never fire declines everywhere, and "declines
everywhere" would be indistinguishable from a broken build. So every claim below comes as a
twin pair that differs in exactly one fact:

- the **fire** board must DIFFER from the base and emit both commands of the exchange;
- each **decline** board must be BYTE-IDENTICAL to the base.

Both arms run through `control-base-peek-rev3.rs` and `control-swap-r1-peek-rev3.rs`: the same
driver and the same parser, the base's hook ignoring the map and rev 3's building it. The only
variable is the predicate.

The board is a 6-cell corridor (0,0)..(5,0). Unit 0 is the mover at (0,0) heading for (3,0);
unit 2 stands on the landing (1,0) and is NOT moving. `commands` are pre-resolution, exactly as
`resolve_move_conflicts*` receives them.

Run:  python3 claude_1/peek/peek_controls.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1/banana-restoration-r2"))
import semantic_harness as sh  # noqa: E402

BASE_CTL = REPO / "claude_1/swap1/control-base-peek-rev3.rs"
CAND_CTL = REPO / "claude_1/swap1/control-swap-r1-peek-rev3.rs"
OUT = HERE / "g1-peek-controls-rev3-2026-08-22.json"

CORRIDOR = [(x, 0) for x in range(0, 6)]

# kind codes for the `peek:` row, matching the driver: 0=None 1=Shack 2=Bank 3=Cell 4=Tree
NONE, SHACK, BANK, CELL, TREE = 0, 1, 2, 3, 4


def board(*, mover_to=(3, 0), peek_rows=(), partner_cmd="WAIT"):
    rows = ["size: 6 1", "turn: 7",
            "walkable: " + " ".join(f"{x} {y}" for x, y in CORRIDOR),
            "unit: 0 0 0 0 1", "unit: 2 0 1 0 1",
            f"cmd: MOVE 0 {mover_to[0]} {mover_to[1]}", f"cmd: {partner_cmd}"]
    rows += [f"peek: {uid} {kind} {x} {y}" for uid, kind, x, y in peek_rows]
    return "\n".join(rows) + "\n"


CONTROLS = [
    {
        "name": "peek-fire-partner-target-elsewhere",
        "clause": "all three clauses satisfied",
        "why": "the partner is stationary, its selected target is (5,0) — neither the landing "
               "(1,0) nor the mover's target (3,0) — and the mover genuinely passes through. "
               "This is the ONLY shape rev 3 admits, and it must be shown admitting.",
        "board": board(peek_rows=[(2, CELL, 5, 0)]),
        "expect": "FIRE",
        "exchange": ["MOVE 0 1 0", "MOVE 2 0 0"],
    },
    {
        "name": "peek-decline-partner-target-is-the-landing",
        "clause": "partner target != landing",
        "why": "one fact changed from the fire twin: the partner's target is the contested cell "
               "itself. This is the standing-chopper shape — 29 of the corpus's 989 encounters.",
        "board": board(peek_rows=[(2, TREE, 1, 0)]),
        "expect": "IDENTICAL",
    },
    {
        "name": "peek-decline-partner-target-is-the-mover-target",
        "clause": "partner target != mover target",
        "why": "both units want (3,0). This is the OSC-006 dance the pass-through test alone "
               "could not tell from a real pass-through.",
        "board": board(peek_rows=[(2, CELL, 3, 0)]),
        "expect": "IDENTICAL",
    },
    {
        "name": "peek-decline-partner-target-none",
        "clause": "missing/None fails toward not displacing",
        "why": "the partner is WAIT and `Self::wait()` sets `target:Target::None`. 960 of the "
               "corpus's 989 encounters are this row, so this control is the corpus result.",
        "board": board(peek_rows=[(2, NONE, 0, 0)]),
        "expect": "IDENTICAL",
    },
    {
        "name": "peek-decline-partner-absent-from-map",
        "clause": "missing fails toward not displacing",
        "why": "no entry at all for the partner — the shape a stale or incomplete map produces. "
               "It must behave exactly like Target::None, not like an unconstrained fire.",
        "board": board(peek_rows=[(0, CELL, 3, 0)]),
        "expect": "IDENTICAL",
    },
    {
        "name": "peek-decline-empty-map",
        "clause": "missing fails toward not displacing",
        "why": "the map exists but is empty. Fail-closed must not depend on the map being absent.",
        "board": board(peek_rows=[]),
        "expect": "IDENTICAL",
    },
    {
        "name": "peek-decline-mover-arrives-and-stays",
        "clause": "genuine mover pass-through",
        "why": "same admitting partner target as the fire twin, but the mover's own target IS "
               "the landing, so it is not passing through — it is taking the cell to keep it.",
        "board": board(mover_to=(1, 0), peek_rows=[(2, CELL, 5, 0)]),
        "expect": "IDENTICAL",
    },
]


def run(binary: Path, board_text: str) -> str:
    done = subprocess.run([str(binary)], input=board_text, capture_output=True, text=True)
    if done.returncode:
        raise SystemExit(f"control driver failed: {done.stderr[:2000]}")
    return done.stdout.strip()


def main() -> int:
    results, ok = [], True
    with tempfile.TemporaryDirectory(prefix="peek-controls-") as wd:
        wd = Path(wd)
        base_bin, cand_bin = wd / "base.bin", wd / "cand.bin"
        sh.compile_text(BASE_CTL.read_text(), base_bin, crate="peek_control_base")
        sh.compile_text(CAND_CTL.read_text(), cand_bin, crate="peek_control_cand")
        for control in CONTROLS:
            base_out = run(base_bin, control["board"])
            cand_out = run(cand_bin, control["board"])
            identical = base_out == cand_out
            if control["expect"] == "IDENTICAL":
                good = identical
                detail = "byte-identical to the base" if good else "DIVERGED from the base"
            else:
                good = (not identical) and all(
                    c in cand_out.split(";") for c in control["exchange"])
                detail = ("the exchange was emitted" if good else
                          "expected the exchange and did not get it")
            ok &= good
            results.append({**{k: control[k] for k in ("name", "clause", "why", "expect")},
                            "base": base_out, "candidate": cand_out,
                            "status": "OK" if good else "FAILED", "detail": detail})
            print(f"  {'OK    ' if good else 'FAILED'} {control['name']:<44} "
                  f"base[{base_out}] cand[{cand_out}]")
    OUT.write_text(json.dumps({"task": "20260822-peek-planner-target-map", "gate": "G-1",
                               "revision": 3, "controls": results, "all_ok": ok}, indent=2) + "\n")
    print(f"\n  PEEK CONTROLS: {'ALL OK' if ok else 'A CONTROL FAILED'} -> {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
