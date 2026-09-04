#!/usr/bin/env python3
"""Gate 2: does the referee agree with the mechanics the parent card sec 4 states as given?

The card hands five mechanics over "for free -- do not re-derive these", all of them upstream
of any orchard value number. I do not take them on trust, because the whole point of a second
implementation is that a shared wrong premise reproduces perfectly. Each case below is played
through `fuzz_panel.FuzzReferee` on a tiny hand-built map with a scripted command line, and the
expected value is hand-computed from the card's text -- never from the referee's constants.

A disagreement here is a finding and gets reported as one.

    python3 claude_1/orchard-repro/mechanics_check.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "claude_1" / "pipeline"))

import fuzz_panel as fp             # noqa: E402

# A 9x5 pen in the harness's own map legend ('.' land, '~' water, '0'/'1' the two shacks).
# Column 8 is water so the water-boost cases have a wet cell to plant beside.
ROWS = [
    "........~",
    ".0.....1~",
    "........~",
    "........~",
    "........~",
]


def pen(units, plants=None, inv=None):
    u = {}
    for uid, (cell, extra) in units.items():
        u[uid] = {"player": 0, "cell": cell, "speed": 1, "cap": 1, "harvest": 1,
                  "chop": 1, "carry": [0] * 6}
        u[uid].update(extra)
    u[9] = {"player": 1, "cell": (0, 4), "speed": 1, "cap": 1, "harvest": 1, "chop": 1,
            "carry": [0] * 6}
    ref = fp.FuzzReferee(list(ROWS), list(inv or [0] * 6), dict(plants or {}), u, "harvester")
    ref.opp_inv = [0] * 6
    return ref


def turns(ref, lines):
    """Play a fixed script. The opponent line is empty: this is a mechanics pen, not a game,
    and the card's standing prohibition on modelling the opponent as idle is about VALUE
    experiments, not about a two-cell health check."""
    for line in lines:
        ref.apply(line)
        ref.grow()
    return ref


CASES = []


def case(fn):
    CASES.append(fn)
    return fn


@case
def c1_size4_tree_is_sixteen_points():
    """Card: 'A mature size-4 tree is 16 points, not 4' -- felling yields plant.size logs at
    WOOD_POINTS 4 each. Hand-computed: fell a size-4 banana, bank it, expect own score +16."""
    # The chopper stands ON the tree: `_apply_chop` reads `u["cell"]` and asks whether a plant
    # is at that cell (engine.rs::apply_chop_on_cells). Chopping is not an adjacent action.
    ref = pen({0: ((2, 1), {"chop": 99, "cap": 9})},
              plants={(2, 1): {"kind": "BANANA", "size": 4, "health": 1, "fruits": 0, "cd": 9}})
    turns(ref, ["CHOP 0", "MOVE 0 1 1", "DROP 0"])
    got = sum(ref.inv[0:4]) + 4 * ref.inv[5]
    return {"case": "a felled size-4 tree banks 16 points", "expected": 16, "got": got,
            "wood_banked": ref.inv[5], "verdict": "AGREES" if got == 16 else "DISAGREES"}


@case
def c2_health_at_maturity_by_species():
    """Card: 'banana 6, plum 12, lemon 12, apple 20' at maturity. Hand-computed from the card's
    own formula base + 4*slope with base 2/4/4/8 and slope 1/2/2/3 -- but READ OFF THE REFEREE
    by growing a freshly planted tree to size 4 and asking its health, not by re-evaluating the
    formula in Python."""
    want = {"BANANA": 6, "PLUM": 12, "LEMON": 12, "APPLE": 20}
    got = {}
    for kind in want:
        carry = [0] * 6
        carry[fp.ITEM_INDEX[kind]] = 1
        ref = pen({0: ((3, 3), {"carry": carry})})
        script = ["PLANT 0 %s" % kind] + [""] * 200          # 200 idle turns: grow to size 4
        turns(ref, script)
        tree = ref.plants.get((3, 3))
        got[kind] = None if tree is None else (tree["size"], tree["health"])
    ok = all(got[k] is not None and got[k][0] == 4 and got[k][1] == want[k] for k in want)
    return {"case": "health at maturity by species (size 4)", "expected": want,
            "got": {k: (v and v[1]) for k, v in got.items()},
            "sizes": {k: (v and v[0]) for k, v in got.items()},
            "verdict": "AGREES" if ok else "DISAGREES"}


@case
def c3_chop_turns_to_fell_a_mature_tree():
    """Card: 'a chop-1 troll fells a banana in 6 turns against an apple's 20'. Hand-computed:
    a mature tree's health is its maturity health, one chop-1 troll removes 1 per turn, so the
    turn count equals the maturity health. Played, not asserted."""
    want = {"BANANA": 6, "PLUM": 12, "LEMON": 12, "APPLE": 20}
    got = {}
    for kind in want:
        health = want[kind]
        ref = pen({0: ((2, 1), {"chop": 1, "cap": 99})},
                  plants={(2, 1): {"kind": kind, "size": 4, "health": health,
                                   "fruits": 0, "cd": 99}})
        n = 0
        while (2, 1) in ref.plants and n < 60:
            ref.apply("CHOP 0")
            ref.grow()
            n += 1
        got[kind] = n if (2, 1) not in ref.plants else None
    ok = got == want
    return {"case": "chop-1 turns to fell a mature tree", "expected": want, "got": got,
            "verdict": "AGREES" if ok else "DISAGREES"}


@case
def c4_a_troll_plants_under_itself():
    """NOT a card claim -- a mechanic I had to establish myself, and it corrects my own
    pre-registration. `PLANT` takes no cell (engine arity 3: PLANT <uid> <KIND>); the tree
    appears at the planter's OWN cell, and the only occupancy that blocks it is an existing
    TREE, not the troll standing there. My published action vocabulary wrote `PLANT <cell>`,
    which is not a command this engine has. Recorded here as the corrected form."""
    carry = [0] * 6
    carry[fp.ITEM_INDEX["BANANA"]] = 1
    ref = pen({0: ((3, 3), {"carry": list(carry)})})
    turns(ref, ["PLANT 0 BANANA"])
    planted_under = (3, 3) in ref.plants
    # and the same command onto a cell that already holds a tree must be refused
    ref2 = pen({0: ((3, 3), {"carry": list(carry)})},
               plants={(3, 3): {"kind": "PLUM", "size": 2, "health": 8, "fruits": 0, "cd": 3}})
    turns(ref2, ["PLANT 0 BANANA"])
    refused = ref2.plants[(3, 3)]["kind"] == "PLUM" and ref2.units[0]["carry"][
        fp.ITEM_INDEX["BANANA"]] == 1
    ok = planted_under and refused
    return {"case": "PLANT places the tree at the planter's own cell; only a tree blocks it",
            "expected": {"plants_under_itself": True, "refused_on_occupied_cell": True},
            "got": {"plants_under_itself": planted_under, "refused_on_occupied_cell": refused},
            "verdict": "AGREES" if ok else "DISAGREES"}


@case
def c5_first_fruit_beside_water_and_inland():
    """Card: 'plum and lemon ~12 turns beside water against 32 inland; apple 8 against 36;
    banana 16 against 24.' Read as the turns from PLANT to the first fruit. Played on the pen:
    (7,2) is orthogonally beside the water column, (3,3) is inland."""
    want_wet = {"PLUM": 12, "LEMON": 12, "APPLE": 8, "BANANA": 16}
    want_dry = {"PLUM": 32, "LEMON": 32, "APPLE": 36, "BANANA": 24}
    got = {}
    for kind in want_wet:
        for label, cell in (("wet", (7, 2)), ("dry", (3, 3))):
            carry = [0] * 6
            carry[fp.ITEM_INDEX[kind]] = 1
            ref = pen({0: (cell, {"carry": carry})})
            # Counting convention, stated because it is where an off-by-one lives: the PLANT
            # turn is turn 0, and n counts the growth ticks AFTER it. The tree appears at size
            # 0 and the planting turn's own tick takes it to size 1, so that tick belongs to
            # the plant, not to the wait.
            ref.apply("PLANT 0 %s" % kind)
            ref.grow()
            n = 0
            while n < 200 and ref.plants[cell]["fruits"] == 0:
                ref.apply("")
                ref.grow()
                n += 1
            got[(kind, label)] = n
    exp = {}
    for k in want_wet:
        exp[k] = {"wet": want_wet[k], "dry": want_dry[k]}
    obs = {k: {"wet": got[(k, "wet")], "dry": got[(k, "dry")]} for k in want_wet}
    ok = obs == exp
    return {"case": "turns from PLANT to first fruit, beside water and inland",
            "expected": exp, "got": obs,
            "verdict": "AGREES" if ok else "DISAGREES"}


def main() -> int:
    results = [fn() for fn in CASES]
    for r in results:
        print("  %-10s %s" % (r["verdict"], r["case"]))
        if r["verdict"] != "AGREES":
            print("      expected %s" % json.dumps(r["expected"], sort_keys=True))
            print("      got      %s" % json.dumps(r["got"], sort_keys=True))
    agree = sum(1 for r in results if r["verdict"] == "AGREES")
    report = {
        "what": "gate 2: the referee against the mechanics the parent card sec 4 gives for free",
        "referee_sha256": fp.referee_sha256(),
        "cases": len(results), "agreeing": agree, "results": results,
        "status": "PASS" if agree == len(results) else "MIXED",
    }
    out = HERE / "results" / "mechanics-check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print("\n  %s  the referee agrees with %d of %d stated mechanics  -> %s"
          % (report["status"], agree, len(results), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
