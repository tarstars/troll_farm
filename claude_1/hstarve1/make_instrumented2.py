#!/usr/bin/env python3
"""H-STARVE-1 — build the INSTRUMENTED bot v2, LOGGING-POINT REPAIRED (diagnostics only).

Task `20260816-h-starve-1-standing-troll-audit`. This regenerates
`instrumented-hstarve2.rs` from the resident so the instrument is reproducible from a
byte-exact subject rather than hand-edited, and it fixes codex_1's pool-#2 blocker
(`codex_1/reviews/h-starve-1-pool1-revision-review-2026-08-17.md`):

> the `HS2` candidate summary is emitted inside the per-unit loop, but
> `force_unique_door_clear` runs afterward ... `HS2CHOSEN` is emitted immediately after
> `select()`, but `resolve_move_conflicts` runs afterward.

So the previous records could disagree with the selector's true input and with the
command actually emitted. The repair does not move the taps and lose the old view — it
**duplicates** them, which is what makes the two mutation paths observable:

| record          | emitted                                            | meaning                |
|-----------------|----------------------------------------------------|------------------------|
| `HS2PRE`        | in the per-unit loop, as before                     | generator output       |
| `HS2`           | after `force_unique_door_clear`, before `select()`  | selector's TRUE input  |
| `HS2CHOSENPRE`  | immediately after `select()`                        | selector's raw output  |
| `HS2CHOSEN`     | after `resolve_move_conflicts`                      | FINAL emitted command  |

`HS2` and `HS2CHOSEN` keep their names, so every downstream consumer that already parses
them is now reading the final stage by construction. `HS2PRE`/`HS2CHOSENPRE` exist so a
control can prove the mutation paths actually fire on the corpus — a gate that has never
been observed changing anything is not evidence (see `logging_taps_control.py`).

Per-unit context (cell, branch, endgame, committed) is stashed in `hs2_ctx` during the
loop because `by_id` is *moved into* `select()`, so the final tap must reconstruct the
labels it can no longer read off `unit`.

**This build only prints.** Every `eprintln!` goes to stderr; stdout — the command
protocol — is byte-identical to the delivered bot's, which `coverage.py::check_parity`
verifies against the uninstrumented run on all 34 situations rather than trusting it.
"""
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
OUT = REPO / "claude_1/hstarve1/instrumented-hstarve2.rs"
RESIDENT_SHA = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"

# 1. per-unit branch label + the context map the post-mutation tap needs
OLD_BRANCH = '''                let mut by_id=BTreeMap::new();
                for unit in my_units{
                    let committed_regeneration=self.regeneration_commitments.contains_key(&unit.id);
                    let mut candidates=if committed_regeneration{'''

NEW_BRANCH = '''                let mut by_id=BTreeMap::new();
                let mut hs2_ctx:BTreeMap<i32,(Cell,String,bool,bool)> =BTreeMap::new();
                for unit in my_units{
                    let committed_regeneration=self.regeneration_commitments.contains_key(&unit.id);
                    let hs2_branch=if committed_regeneration{"COMMITTED_REGEN"}
                        else if endgame&&self.persistent_regeneration&&Self::carried_fruit(unit).is_some(){"ENDGAME_CARRY"}
                        else if endgame{"ENDGAME"}
                        else if early{"EARLY"}else{"MAIN"};
                    let mut candidates=if committed_regeneration{'''

# 2. PRE record at the old tap point, plus the context stash
OLD_PRE = '''                    by_id.insert(unit.id,candidates);'''

NEW_PRE = '''                    {
                        let mut kinds:Vec<String> =Vec::new();
                        for candidate in candidates.iter(){
                            let verb=candidate.command.split_whitespace().next().unwrap_or("?");
                            kinds.push(verb.to_string());
                            }
                        eprintln!("HS2PRE turn={} unit={} cell={},{} branch={} endgame={} committed={} ncand={} kinds={}",
                            view.turn,unit.id,unit.cell.0,unit.cell.1,hs2_branch,endgame,committed_regeneration,
                            candidates.len(),kinds.join("|"));
                        hs2_ctx.insert(unit.id,(unit.cell,hs2_branch.to_string(),endgame,committed_regeneration));
                        }
                    by_id.insert(unit.id,candidates);'''

# 3. the two FINAL-stage taps
OLD_FINAL = '''                let mut selected=MoisanBot::select(by_id,&view.inventories[0]);
                MoisanBot::resolve_move_conflicts(view,&mut selected);'''

NEW_FINAL = '''                for(id,candidates)in by_id.iter(){
                    let mut kinds:Vec<String> =Vec::new();
                    for candidate in candidates.iter(){
                        let verb=candidate.command.split_whitespace().next().unwrap_or("?");
                        kinds.push(verb.to_string());
                        }
                    let(cell,branch,endgame_flag,committed_flag)=hs2_ctx.get(id).cloned().unwrap_or(((-1,-1),"NO_CONTEXT".to_string(),false,false));
                    eprintln!("HS2 turn={} unit={} cell={},{} branch={} endgame={} committed={} ncand={} kinds={}",
                        view.turn,id,cell.0,cell.1,branch,endgame_flag,committed_flag,
                        candidates.len(),kinds.join("|"));
                    }
                let mut selected=MoisanBot::select(by_id,&view.inventories[0]);
                eprintln!("HS2CHOSENPRE turn={} line={}",view.turn,selected.join(";"));
                MoisanBot::resolve_move_conflicts(view,&mut selected);
                eprintln!("HS2CHOSEN turn={} line={}",view.turn,selected.join(";"));'''

PATCHES = [
    ("branch label + hs2_ctx", OLD_BRANCH, NEW_BRANCH),
    ("HS2PRE tap + context stash", OLD_PRE, NEW_PRE),
    ("HS2 / HS2CHOSEN final taps", OLD_FINAL, NEW_FINAL),
]


def main():
    src = RESIDENT.read_text()
    digest = hashlib.sha256(src.encode()).hexdigest()
    if digest != RESIDENT_SHA:
        print(f"REFUSING: resident digest differs\n  want {RESIDENT_SHA}\n  got  {digest}")
        return 1

    out = src
    for name, old, new in PATCHES:
        # fail closed on a non-unique anchor: a silent second match would instrument the
        # wrong site, which is the same disease as a tap that logs the wrong stage.
        if out.count(old) != 1:
            print(f"REFUSING: anchor '{name}' matched {out.count(old)} times, want exactly 1")
            return 1
        out = out.replace(old, new)

    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}")

    # the instrument must add records and nothing else
    for record in ("HS2PRE turn=", "HS2 turn=", "HS2CHOSENPRE turn=", "HS2CHOSEN turn="):
        assert out.count(f'eprintln!("{record}') == 1, f"expected exactly one {record} tap"
    assert "MoisanBot::select(by_id" in out and "resolve_move_conflicts(view,&mut selected)" in out

    # the tap ORDER is the whole point of this revision — assert it positionally
    i_pre = out.index('eprintln!("HS2PRE turn=')
    i_door = out.index("self.force_unique_door_clear(view,&mut by_id);")
    i_final = out.index('eprintln!("HS2 turn=')
    i_select = out.index("MoisanBot::select(by_id,")
    i_chosen_pre = out.index('eprintln!("HS2CHOSENPRE turn=')
    i_resolve = out.index("MoisanBot::resolve_move_conflicts(view,&mut selected);")
    i_chosen = out.index('eprintln!("HS2CHOSEN turn=')
    i_extend = out.index("out.extend(selected);")
    order = [i_pre, i_door, i_final, i_select, i_chosen_pre, i_resolve, i_chosen, i_extend]
    assert order == sorted(order), f"tap order wrong: {order}"
    print("tap order verified: HS2PRE < door_clear < HS2 < select < HS2CHOSENPRE < resolve < HS2CHOSEN < emit")

    assert hashlib.sha256(RESIDENT.read_bytes()).hexdigest() == RESIDENT_SHA
    print("resident byte-exact after patching: verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
