#!/usr/bin/env python3
"""T-1 stage 2 — build the candidate bot: a NAMED occupancy check (ruled option B).

Ruling `local_claude_1` `20260816T070640Z`: leave `compatible()` and the `Target::None`
idleness marker untouched; add an explicit, named "peer-standing-on-target" occupancy check at
the pair/greedy sites.

## Why not the one-line fix (my blocker `20260816T070300Z`, upheld)

`Target::None` means TWO things in this bot:

- *"no spatial claim"* — read by `compatible()` (`:643-646`);
- *"this unit is idle"* — read by `is_idle` in the door-clearing layer (`:1016`) and by the
  endgame idle-harvest gate (`:1413`).

Giving WAIT a real target would fix the first and **silently disable both of the others**. This
patch therefore never touches the marker. `check_invariants.py` demonstrates the naive fix
breaking them, observed failing, before this one is trusted.

## What the patch does

1. Adds `idle_peer_cells(...)` — the named predicate. A unit is *idle* exactly as the rest of the
   bot already defines it (**every** candidate it has carries `Target::None`), and its cell is
   then a claimed square.
2. Threads the map into `select` from its single call site (`:1432`), where `view.units` is in
   scope.
3. Rejects, at BOTH the two-unit pair site and the greedy site, any candidate whose target cell
   is held by an *idle peer* (never by the unit itself).

The resident is never modified: this writes a new file.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
OUT = REPO / "claude_1/t1/candidate-t1-occupancy.rs"
NAIVE_OUT = REPO / "claude_1/t1/candidate-t1-naive-BROKEN.rs"

RESIDENT_SHA = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"

# --- the named predicate, inserted next to `compatible` ---------------------------------
PREDICATE = '''            fn idle_peer_cells(candidates_by_id:&BTreeMap<i32,Vec<Candidate>>,view:&GameState)->BTreeMap<Cell,i32>{
                let mut held=BTreeMap::new();
                for unit in view.units.iter().filter(|unit|unit.player==0){
                    let idle=match candidates_by_id.get(&unit.id){
                        Some(options)=>!options.is_empty()&&options.iter().all(|candidate|candidate.target==Target::None),
                        None=>true,
                    };
                    if idle{
                        held.insert(unit.cell,unit.id);
                        }
                    }
                held
                }
            fn target_cell_of(target:Target)->Option<Cell>{
                match target{
                    Target::Bank(cell)|Target::Cell(cell)|Target::Tree(cell)=>Some(cell),_=>None,
                }
                }
            fn free_of_idle_peer(target:Target,mover:i32,held:&BTreeMap<Cell,i32>)->bool{
                match Self::target_cell_of(target){
                    Some(cell)=>held.get(&cell).map(|holder|*holder==mover).unwrap_or(true),
                    None=>true,
                }
                }
'''


def patch(text: str) -> str:
    out = text

    # 1. insert the predicate immediately before `fn compatible`
    anchor = "            fn compatible(a:Target,b:Target)->bool{"
    assert out.count(anchor) == 1, "compatible anchor not unique"
    out = out.replace(anchor, PREDICATE + anchor)

    # 2. select() takes the occupancy map
    old_sig = ("            fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;\n"
               "            6],)->Vec<String>{")
    assert out.count(old_sig) == 1, "select signature not found"
    out = out.replace(old_sig,
                      "            fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;\n"
                      "            6],held:&BTreeMap<Cell,i32>,)->Vec<String>{")

    # 3. pair site: reject a candidate whose target is held by an idle peer
    old_pair = ("                            if!Self::compatible(a.target,b.target)"
                "||!Self::stock_compatible(a,b,inventory){")
    assert out.count(old_pair) == 1, "pair site not found"
    out = out.replace(old_pair,
                      "                            if!Self::compatible(a.target,b.target)"
                      "||!Self::stock_compatible(a,b,inventory)"
                      "||!Self::free_of_idle_peer(a.target,ids[0],held)"
                      "||!Self::free_of_idle_peer(b.target,ids[1],held){")

    # 4. greedy site
    old_greedy = ("                        used_targets.iter().all(|target|Self::compatible"
                  "(candidate.target,*target))&&")
    assert out.count(old_greedy) == 1, "greedy site not found"
    out = out.replace(old_greedy,
                      "                        used_targets.iter().all(|target|Self::compatible"
                      "(candidate.target,*target))&&Self::free_of_idle_peer(candidate.target,id,held)&&")

    # 5. call site: build the map and pass it
    old_call = "                let mut selected=MoisanBot::select(by_id,&view.inventories[0]);"
    assert out.count(old_call) == 1, "select call site not found"
    out = out.replace(old_call,
                      "                let held=MoisanBot::idle_peer_cells(&by_id,view);\n"
                      "                let mut selected=MoisanBot::select(by_id,&view.inventories[0],&held);")
    return out


def naive_patch(text: str) -> str:
    """The fix the task's wording invites and my blocker rejected. Built ONLY so the
    regression checks can be observed failing against it. Never a delivery candidate."""
    old = '                    command:"WAIT".to_string(),score:0.0,target:Target::None,'
    assert text.count(old) == 1
    return text.replace(
        old, '                    command:"WAIT".to_string(),score:0.0,target:Target::Cell(unit.cell),')


def main():
    src = RESIDENT.read_text()
    got = hashlib.sha256(src.encode()).hexdigest()
    if got != RESIDENT_SHA:
        print(f"REFUSING: resident sha256 {got[:16]}… != expected {RESIDENT_SHA[:16]}…")
        return 1
    OUT.write_text(patch(src))
    NAIVE_OUT.write_text(naive_patch(src))
    print(f"wrote {OUT.relative_to(REPO)}  sha256 "
          f"{hashlib.sha256(OUT.read_bytes()).hexdigest()[:16]}…")
    print(f"wrote {NAIVE_OUT.relative_to(REPO)} (control only, never a delivery candidate)")
    # the resident must be untouched by construction; verify rather than assert
    assert hashlib.sha256(RESIDENT.read_bytes()).hexdigest() == RESIDENT_SHA
    print("resident byte-exact after patching: verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
