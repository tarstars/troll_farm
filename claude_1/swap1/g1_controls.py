#!/usr/bin/env python3
r"""G-1 constructed controls — the branches no fixture is guaranteed to exercise.

Task `20260821-swap-r1-cure`, gate **G-1**. The design note (§7) commits to a constructed control
for every structural claim a whole-game sweep cannot be relied on to reach. Two of alpha's
conjuncts are of that kind:

- **T2b** (`!reserved.contains(&m.cell)`) fires only when an EARLIER accepted mover has already
  taken `m`'s own cell as its landing. That is codex_1's blocking finding G0-1; without a control
  it is an untested branch, which is the same defect class as an inert check.
- **T3's partner clause** (`m.cell` must not be forbidden to `U`) can never be reached in a live
  game on this base at all: the seam's only call site passes EMPTY `priority_ids` and EMPTY
  `forbidden_for_non_priority` (`candidate-door1-pure-deletion.rs:714-719,1432`). Stated plainly
  rather than left for a reviewer to discover: the door interaction is exercised HERE and nowhere
  else, and a fixture sweep reporting "no door interaction observed" is reporting on a branch the
  game cannot reach, not on a branch that works.

Also controlled: T2 (the exchange must be a legal single tick for `U`) and the fail-closed
positional map (§4).

## The shape of every control — and why each has a twin

A control that only shows alpha DECLINING proves nothing: an alpha that never fires declines
everywhere. So every board comes in a pair that differs in exactly the one fact the conjunct
tests:

- the **decline** twin must produce a command vector **byte-identical to the base's**;
- the **fire** twin, one fact changed, must **differ from the base** in exactly the two commands
  of the exchange.

Both twins run through `control-base.rs` and `control-swap-r1.rs`, which are the base and the
candidate with `main` replaced by a driver that constructs the board and calls the seam directly.
Same source, same function, same inputs: the only variable is alpha.

Run:  python3 claude_1/swap1/g1_controls.py
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

OUT = HERE / "g1-controls-2026-08-21.json"

CORRIDOR = [(x, 0) for x in range(0, 6)]


def board(units, commands, *, turn=7, walkable=CORRIDOR, priority=(), forbidden=()):
    rows = [f"size: {max(x for x, _ in walkable) + 1} 1", f"turn: {turn}",
            "walkable: " + " ".join(f"{x} {y}" for x, y in walkable)]
    for uid, player, cell, speed in units:
        rows.append(f"unit: {uid} {player} {cell[0]} {cell[1]} {speed}")
    rows += [f"cmd: {c}" for c in commands]
    if priority:
        rows.append("priority: " + " ".join(str(i) for i in priority))
    if forbidden:
        rows.append("forbidden: " + " ".join(f"{x} {y}" for x, y in forbidden))
    return "\n".join(rows) + "\n"


# --------------------------------------------------------------------------------------
# the controls. Each entry: (name, why, board, expectation)
#   expectation "IDENTICAL" -> alpha must decline; "EXCHANGE" -> alpha must fire and the
#   listed commands must appear.

CONTROLS = [
    {
        "name": "T2b-decline",
        "conjunct": "T2b",
        "why": ("an EARLIER accepted mover (id 3, sorted first on descending id) has already "
                "reserved (1,0) — m's own cell — as its landing, so the exchange would create a "
                "contested landing the engine would break on id. alpha must decline."),
        "board": board(
            units=[(1, 0, (2, 0), 1), (2, 0, (1, 0), 1), (3, 0, (0, 0), 1)],
            commands=["WAIT", "MOVE 2 3 0", "MOVE 3 1 0"]),
        "expect": "IDENTICAL",
    },
    {
        "name": "T2b-fire-twin",
        "conjunct": "T2b",
        "why": ("the same board with the earlier mover sent the other way, so (1,0) is NOT "
                "reserved. One fact changed; alpha must now fire. This is what makes the "
                "decline above evidence about T2b rather than about an inert alpha."),
        "board": board(
            units=[(1, 0, (2, 0), 1), (2, 0, (1, 0), 1), (3, 0, (5, 0), 1)],
            commands=["WAIT", "MOVE 2 3 0", "MOVE 3 5 0"]),
        "expect": "EXCHANGE",
        "exchange": ["MOVE 2 2 0", "MOVE 1 1 0"],
    },
    {
        "name": "T2-decline-speed",
        "conjunct": "T2",
        "why": ("m has movement_speed 2, so its landing (3,0) is two cells from its own cell "
                "(1,0); U at (3,0) has speed 1 and cannot reach (1,0) in one tick. A bare "
                "adjacency test would wave this through; next_cell rejects it."),
        "board": board(
            units=[(1, 0, (3, 0), 1), (2, 0, (1, 0), 2)],
            commands=["WAIT", "MOVE 2 5 0"]),
        "expect": "IDENTICAL",
    },
    {
        "name": "T2-fire-twin-speed",
        "conjunct": "T2",
        "why": ("the same board with U's speed raised to 2, which makes the exchange a legal "
                "single tick for U. Also the T4(a) demonstration: a detour DOES exist here "
                "((2,0) is free), and the ruled construction swaps anyway because U is idle."),
        "board": board(
            units=[(1, 0, (3, 0), 2), (2, 0, (1, 0), 2)],
            commands=["WAIT", "MOVE 2 5 0"]),
        "expect": "EXCHANGE",
        "exchange": ["MOVE 2 3 0", "MOVE 1 1 0"],
    },
    {
        "name": "T3-partner-forbidden-decline",
        "conjunct": "T3 (door unblocking)",
        "why": ("m.cell (1,0) is forbidden to non-priority units and U (id 1) is not a priority "
                "id, so the exchange would push U into a door cell it is forbidden to enter. "
                "The base never had to ask this because U was not moving; alpha makes it move, "
                "so alpha owes the check."),
        "board": board(
            units=[(1, 0, (2, 0), 1), (2, 0, (1, 0), 1)],
            commands=["WAIT", "MOVE 2 4 0"], priority=[2], forbidden=[(1, 0)]),
        "expect": "IDENTICAL",
    },
    {
        "name": "T3-partner-forbidden-fire-twin",
        "conjunct": "T3 (door unblocking)",
        "why": ("the same board with U also a priority id, which is exactly the fact the clause "
                "tests. alpha fires."),
        "board": board(
            units=[(1, 0, (2, 0), 1), (2, 0, (1, 0), 1)],
            commands=["WAIT", "MOVE 2 4 0"], priority=[1, 2], forbidden=[(1, 0)]),
        "expect": "EXCHANGE",
        "exchange": ["MOVE 2 2 0", "MOVE 1 1 0"],
    },
    {
        "name": "positional-map-count-mismatch",
        "conjunct": "§4 fail-closed positional map",
        "why": ("three own units, two commands: the one-command-per-unit invariant does not "
                "hold, so a positional map cannot be trusted and alpha disables itself for the "
                "tick. The board is otherwise the firing board."),
        "board": board(
            units=[(1, 0, (2, 0), 1), (2, 0, (1, 0), 1), (4, 0, (5, 0), 1)],
            commands=["WAIT", "MOVE 2 4 0"]),
        "expect": "IDENTICAL",
    },
    {
        "name": "positional-map-id-mismatch",
        "conjunct": "§4 fail-closed positional map",
        "why": ("the command count matches but a MOVE names an id that is not the "
                "positionally-derived one (slot 1 belongs to id 2 and carries `MOVE 4 …`), so "
                "the map disagrees with the ids alpha can actually read and alpha disables "
                "itself. A cure that rewrites the wrong troll's command is worse than no cure."),
        "board": board(
            units=[(1, 0, (2, 0), 1), (2, 0, (1, 0), 1), (4, 0, (5, 0), 1)],
            commands=["WAIT", "MOVE 4 4 0", "MOVE 2 4 0"]),
        "expect": "IDENTICAL",
    },
    {
        "name": "T1-enemy-blocker",
        "conjunct": "T1",
        "why": ("the blocker on the landing cell is an ENEMY unit. Enemies may share our cell, "
                "so they are never in `reserved` and the branch is not even reached — recorded "
                "as a control so the claim is measured rather than asserted."),
        "board": board(
            units=[(2, 0, (1, 0), 1), (9, 1, (2, 0), 1)],
            commands=["MOVE 2 4 0"]),
        "expect": "IDENTICAL",
    },
    {
        "name": "T4b-no-detour-working-partner",
        "conjunct": "T4(b)",
        "why": ("U is CHOPping, not idle, and m sits in a DEAD END at (0,0) with no detour. "
                "the OSC-005/027 shape: the exchange is the only resolution, and U's chop is "
                "displaced for the tick."),
        "board": board(
            units=[(1, 0, (1, 0), 1), (2, 0, (0, 0), 1)],
            commands=["CHOP 1", "MOVE 2 4 0"]),
        "expect": "EXCHANGE",
        "exchange": ["MOVE 2 1 0", "MOVE 1 0 0"],
    },
    {
        "name": "T4-working-partner-with-detour",
        "conjunct": "T4",
        "why": ("U is working (not idle) and a detour DOES exist (the dead end at (0,0) is "
                "widened by (0,1)). Neither T4 clause holds, so alpha must decline and the base's detour "
                "must stand. This is the boundary of the one declared behaviour change."),
        "board": board(
            units=[(1, 0, (1, 0), 1), (2, 0, (0, 0), 1)],
            commands=["CHOP 1", "MOVE 2 4 0"],
            walkable=CORRIDOR + [(0, 1), (1, 1)]),
        "expect": "IDENTICAL",
    },
]


def run(binary: Path, text: str) -> str:
    done = subprocess.run([str(binary)], input=text, text=True, capture_output=True, timeout=60)
    if done.returncode:
        raise SystemExit(f"control driver failed: {done.stderr[:2000]}")
    return done.stdout.strip()


def main() -> int:
    results, ok = [], True
    with tempfile.TemporaryDirectory(prefix="swap-controls-") as wd:
        wd = Path(wd)
        base_bin, cand_bin = wd / "base.bin", wd / "cand.bin"
        sh.compile_text((HERE / "control-base.rs").read_text(), base_bin, crate="swap_control_base")
        sh.compile_text((HERE / "control-swap-r1.rs").read_text(), cand_bin, crate="swap_control_cand")
        for control in CONTROLS:
            base_out = run(base_bin, control["board"])
            cand_out = run(cand_bin, control["board"])
            identical = base_out == cand_out
            if control["expect"] == "IDENTICAL":
                good = identical
                detail = "byte-identical to the base" if good else "DIVERGED from the base"
            else:
                good = (not identical) and all(c in cand_out.split(";") for c in control["exchange"])
                detail = ("exchange emitted" if good else
                          "expected the exchange and did not get it")
            ok &= good
            results.append({"name": control["name"], "conjunct": control["conjunct"],
                            "why": control["why"], "expect": control["expect"],
                            "base": base_out, "candidate": cand_out,
                            "status": "OK" if good else "FAILED", "detail": detail})
            print(f"  {'OK    ' if good else 'FAILED'} {control['name']:<38} "
                  f"base[{base_out}] cand[{cand_out}]")
    OUT.write_text(json.dumps({"task": "20260821-swap-r1-cure", "gate": "G-1",
                               "controls": results, "all_ok": ok}, indent=2) + "\n")
    print(f"\n  CONTROLS: {'ALL OK' if ok else 'A CONTROL FAILED'} -> {OUT.relative_to(REPO)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
