#!/usr/bin/env python3
"""T-1 stage 2 — the two protected behaviours must stay reachable.

Ruling `20260816T070640Z` grounds (iii): "the two protected behaviours stay provably intact —
add regression checks for both (:1016 door-clear idle branch still reachable; :1413 idle-harvest
still reachable), observed failing under the naive fix if cheap to demonstrate."

It is cheap: the naive fix is a one-token change, so there is no excuse for asserting instead of
demonstrating. Each check below is run against BOTH the delivered candidate and the naive control,
and is required to PASS on the first and FAIL on the second.

## What this checks, and what it does NOT

Both predicates gate on `candidate.target==Target::None`. A build that stops emitting
`Target::None` for WAIT makes both permanently false. These checks therefore verify the
**invariant those branches depend on** — that WAIT still carries `Target::None`, and that the two
call sites are unaltered.

**This is a source-level invariant check, not a runtime reachability proof.** It cannot tell you
the branches actually fired in a game; it tells you the patch has not removed the condition under
which they can. A runtime proof needs an instrumented build and is not in this increment. Stated
plainly rather than left for a reader to discover.
"""
import re, sys, hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CAND = REPO / "claude_1/t1/candidate-t1-occupancy.rs"
NAIVE = REPO / "claude_1/t1/candidate-t1-naive-BROKEN.rs"
RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"

WAIT_MARKER = 'command:"WAIT".to_string(),score:0.0,target:Target::None,'
DOOR_IDLE = ('let is_idle=!options.is_empty()&&options.iter().all('
             '|candidate|candidate.target==Target::None);')
ENDGAME_IDLE = 'candidates.iter().all(|candidate|candidate.target==Target::None)'


def invariants(text):
    """Reachability is a CONJUNCTION, and my first draft got this wrong.

    Checking that each branch's condition text is intact does not model the hazard: the naive
    fix leaves both texts untouched and still kills both branches, because it removes the only
    thing that can SATISFY them. A branch is reachable iff its condition is still there AND some
    candidate can still carry `Target::None`. So the marker is a conjunct of both, and the
    control breaks both reachability claims rather than neither.
    """
    marker = WAIT_MARKER in text
    return {
        "WAIT still carries Target::None (the idleness marker)": marker,
        ":1016 door-clear idle branch REACHABLE (condition + marker)":
            (DOOR_IDLE in text) and marker,
        ":1413 endgame idle-harvest REACHABLE (condition + marker)":
            (ENDGAME_IDLE in text) and marker,
    }


def main():
    cand, naive, res = CAND.read_text(), NAIVE.read_text(), RESIDENT.read_text()
    ok = True
    print("delivered candidate (option B) — every invariant must HOLD:")
    for name, held in invariants(cand).items():
        print(f"  {'OK  ' if held else 'BAD '} {name}")
        ok = ok and held

    print("\nnaive one-line fix (control) — every invariant must BREAK:")
    broke_any = False
    for name, held in invariants(naive).items():
        broken = not held
        print(f"  {'OK  ' if broken else 'BAD '} {name} -> {'broken' if broken else 'STILL HOLDS'}")
        broke_any = broke_any or broken
        if not broken:
            ok = False   # every reachability claim must fail under the naive fix
    if not broke_any:
        print("  BAD  the control broke NOTHING — it does not demonstrate the hazard")
        ok = False

    # the named predicate must actually be present and wired at both sites
    print("\noption B wiring:")
    wiring = {
        "named predicate free_of_idle_peer exists": "fn free_of_idle_peer(" in cand,
        "idle_peer_cells built from view.units": "fn idle_peer_cells(" in cand,
        "wired at the pair site": cand.count("Self::free_of_idle_peer(a.target") == 1,
        "wired at the greedy site": "Self::free_of_idle_peer(candidate.target,id,held)" in cand,
        "compatible() itself UNCHANGED": ("fn compatible(a:Target,b:Target)->bool{\n"
                                          "                if a==Target::None||b==Target::None{") in cand,
    }
    for name, held in wiring.items():
        print(f"  {'OK  ' if held else 'BAD '} {name}")
        ok = ok and held

    print("\nresident untouched:")
    same = hashlib.sha256(res.encode()).hexdigest() == (
        "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29")
    print(f"  {'OK  ' if same else 'BAD '} resident sha256 byte-exact")
    ok = ok and same

    print("\ninvariant check:", "PASS" if ok else "FAIL")
    print("\nLIMIT: source-level invariant check, NOT a runtime reachability proof. It shows the")
    print("patch has not removed the condition those branches need; it does not show they fired.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
