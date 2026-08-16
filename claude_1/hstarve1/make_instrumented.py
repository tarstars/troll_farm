#!/usr/bin/env python3
"""H-STARVE-1 — build the INSTRUMENTED bot (diagnostics only, never a delivery candidate).

Task `20260816-h-starve-1-standing-troll-audit`, claimed. Owner hypothesis: the real cost in the
long episodes is the PARKED troll, not the dancer; suspected mechanism = a stuck regeneration
commitment routing the unit to the endgame generator mid-game, leaving it with no candidates.

## The routing, read from the subject (:1396-1410)

```rust
let committed_regeneration = self.regeneration_commitments.contains_key(&unit.id);
let mut candidates = if committed_regeneration {
    Self::endgame_candidates(...)          // <-- taken regardless of whether it IS the endgame
} else if endgame && persistent_regeneration && carried_fruit.is_some() { main_candidates(...) }
else if endgame { endgame_candidates(...) }
else if early   { early_candidates(...) }
else            { main_candidates(...) }
```

`committed_regeneration` is the **first** arm and is **not conjoined with `endgame`**. So a unit
holding a regeneration commitment is fed the endgame generator at any turn. That is the mechanism
the owner suspects, and it is visible statically — but *visible* is not *witnessed*, which is what
this instrument is for.

**This build only prints.** Every `eprintln!` goes to stderr; stdout — the command protocol — is
byte-identical to the delivered bot's. `check_noninterference()` in the audit runner verifies that
against the uninstrumented run rather than trusting it.
"""
import hashlib, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
OUT = REPO / "claude_1/hstarve1/instrumented-hstarve1.rs"
RESIDENT_SHA = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"

OLD = '''                for unit in my_units{
                    let committed_regeneration=self.regeneration_commitments.contains_key(&unit.id);
                    let mut candidates=if committed_regeneration{'''

NEW = '''                for unit in my_units{
                    let committed_regeneration=self.regeneration_commitments.contains_key(&unit.id);
                    let hs1_branch=if committed_regeneration{"COMMITTED_REGEN"}
                        else if endgame&&self.persistent_regeneration&&Self::carried_fruit(unit).is_some(){"ENDGAME_CARRY"}
                        else if endgame{"ENDGAME"}
                        else if early{"EARLY"}else{"MAIN"};
                    let mut candidates=if committed_regeneration{'''

# after all post-processing, before insertion into by_id
OLD2 = '''                    by_id.insert(unit.id,candidates);'''
NEW2 = '''                    eprintln!("HS1 turn={} unit={} cell={},{} branch={} endgame={} committed={} n={} all_none={} carry={:?}",
                        view.turn,unit.id,unit.cell.0,unit.cell.1,hs1_branch,endgame,committed_regeneration,
                        candidates.len(),candidates.iter().all(|c|c.target==Target::None),unit.carry);
                    by_id.insert(unit.id,candidates);'''


def main():
    src = RESIDENT.read_text()
    if hashlib.sha256(src.encode()).hexdigest() != RESIDENT_SHA:
        print("REFUSING: resident digest differs")
        return 1
    if src.count(OLD) != 1:
        print("REFUSING: routing anchor not unique")
        return 1
    out = src.replace(OLD, NEW)
    if out.count(OLD2) != 1:
        print(f"REFUSING: by_id insert anchor count = {out.count(OLD2)}")
        return 1
    out = out.replace(OLD2, NEW2)
    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}")
    assert hashlib.sha256(RESIDENT.read_bytes()).hexdigest() == RESIDENT_SHA
    print("resident byte-exact after patching: verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
