#!/usr/bin/env python3
r"""4c — build the CHOP-CLAUSE instrument from the byte-exact resident (diagnostics only).

Task `20260818-osc031-chop-clause-instrument`. The owner's question: in OSC-031 a chop-capable
troll rejected every tree every turn for 167 turns, and NOBODY KNOWS which clause said no.
Guessing was refused. This instrument makes the real bot name the clause itself.

THE CLAUSE LIST IS DERIVED FROM THE SUBJECT, NOT FROM MEMORY. `chop_candidates` (resident
`:582`) is a straight-line checklist; every `continue` is one clause, and there are exactly six,
plus a unit-level gate before the loop:

| id | site | test |
|----|------|------|
| `GATE_UNIT`             | :584 | `chop_power<=0 \|\| free_capacity<=0` — loop never runs |
| `DEAD_OR_UNREACHABLE`   | :592 | `plant.health<=0 \|\| !from_unit.contains_key(cell)` |
| `PREDICT_TREE_NONE`     | :596 | `predict_tree(...)` returned None |
| `PREDICTED_NONPOSITIVE` | :600 | `predicted.size<=0 \|\| predicted.health<=0` |
| `CHOP_OUTCOME_NONE`     | :607 | `chop_outcome(...)` returned None |
| `ROUND_TRIP_CLOCK`      | :612 | `turns > TOTAL_TURNS - view.turn + 1` |
| `WOOD_NONPOSITIVE`      | :616 | `final_size.min(free_capacity) <= 0` |
| `ACCEPT`                | :631 | candidate pushed |

**UNPRIVILEGED BY CONSTRUCTION.** The charter records my own suspicion — the tree-prediction
math — as an UNTESTED hypothesis that must not shape the taps. So every clause gets an identical
tap emitted at its own `continue`, including the two I privately expect never to fire
(`ROUND_TRIP_CLOCK`, `WOOD_NONPOSITIVE`). If my hypothesis is wrong, this instrument is what
says so; an instrument that only looks where its author already suspects cannot do that.

**LOGGED = EXECUTED.** Each tap sits immediately before its own `continue`, inside the loop, so a
row exists if and only if control reached that clause. No tap is sited where a later pass could
rewrite the decision — the pool-2 lesson that cost this project two days.

**PRINTS ONLY.** Every `eprintln!` goes to stderr; stdout stays byte-identical to the delivered
bot, which the G-4c.2 parity control verifies against an uninstrumented build rather than
trusting this sentence.
"""
import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
OUT = REPO / "claude_1/chop4c/instrumented-chop4c.rs"
RESIDENT_SHA = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"

# Each entry: (name, anchor, replacement). Anchors are taken verbatim from the resident; the
# builder refuses on any anchor that does not match EXACTLY once, because a silent second match
# instruments the wrong site — the same disease as a tap that logs the wrong stage.

# unit-level gate: the loop never runs, so no per-plant row would otherwise exist
GATE_OLD = '''                if unit.stats.chop_power<=0||unit.free_capacity()<=0{
                    return out;
                    }'''
GATE_NEW = '''                if unit.stats.chop_power<=0||unit.free_capacity()<=0{
                    eprintln!("C4C turn={} unit={} plant=-1 cell=-1,-1 clause=GATE_UNIT chop_power={} free_cap={}",view.turn,unit.id,unit.stats.chop_power,unit.free_capacity());
                    return out;
                    }
                eprintln!("C4CGATE turn={} unit={} plants={} chop_power={} free_cap={}",view.turn,unit.id,view.plants.len(),unit.stats.chop_power,unit.free_capacity());'''

C1_OLD = '''                for plant in&view.plants{
                    if plant.health<=0||!from_unit.contains_key(&plant.cell){
                        continue;
                        }'''
C1_NEW = '''                for(c4c_idx,plant)in view.plants.iter().enumerate(){
                    if plant.health<=0||!from_unit.contains_key(&plant.cell){
                        eprintln!("C4C turn={} unit={} plant={} cell={},{} clause=DEAD_OR_UNREACHABLE health={} reachable={}",view.turn,unit.id,c4c_idx,plant.cell.0,plant.cell.1,plant.health,from_unit.contains_key(&plant.cell));
                        continue;
                        }'''

C2_OLD = '''                    let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{
                        continue;
                        }
                    ;'''
C2_NEW = '''                    let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{
                        eprintln!("C4C turn={} unit={} plant={} cell={},{} clause=PREDICT_TREE_NONE travel_turns={} size={} health={}",view.turn,unit.id,c4c_idx,plant.cell.0,plant.cell.1,travel_turns,plant.size,plant.health);
                        continue;
                        }
                    ;'''

C3_OLD = '''                    if predicted.size<=0||predicted.health<=0{
                        continue;
                        }'''
C3_NEW = '''                    if predicted.size<=0||predicted.health<=0{
                        eprintln!("C4C turn={} unit={} plant={} cell={},{} clause=PREDICTED_NONPOSITIVE pred_size={} pred_health={} travel_turns={}",view.turn,unit.id,c4c_idx,plant.cell.0,plant.cell.1,predicted.size,predicted.health,travel_turns);
                        continue;
                        }'''

C4_OLD = '''                    let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{
                        continue;
                        }
                    ;'''
C4_NEW = '''                    let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{
                        eprintln!("C4C turn={} unit={} plant={} cell={},{} clause=CHOP_OUTCOME_NONE pred_size={} pred_health={} chop_power={}",view.turn,unit.id,c4c_idx,plant.cell.0,plant.cell.1,predicted.size,predicted.health,unit.stats.chop_power);
                        continue;
                        }
                    ;'''

C5_OLD = '''                    if turns>TOTAL_TURNS-view.turn+1{
                        continue;
                        }'''
C5_NEW = '''                    if turns>TOTAL_TURNS-view.turn+1{
                        eprintln!("C4C turn={} unit={} plant={} cell={},{} clause=ROUND_TRIP_CLOCK turns={} remaining={} travel={} chop={} ret={}",view.turn,unit.id,c4c_idx,plant.cell.0,plant.cell.1,turns,TOTAL_TURNS-view.turn+1,travel_turns,chop_turns,return_turns);
                        continue;
                        }'''

C6_OLD = '''                    let wood=final_size.min(unit.free_capacity());
                    if wood<=0{
                        continue;
                        }'''
C6_NEW = '''                    let wood=final_size.min(unit.free_capacity());
                    if wood<=0{
                        eprintln!("C4C turn={} unit={} plant={} cell={},{} clause=WOOD_NONPOSITIVE wood={} final_size={} free_cap={}",view.turn,unit.id,c4c_idx,plant.cell.0,plant.cell.1,wood,final_size,unit.free_capacity());
                        continue;
                        }'''

ACCEPT_OLD = '''                    out.push(Candidate{
                        command,score,target:Target::Tree(plant.cell),
                    }
                    );'''
ACCEPT_NEW = '''                    eprintln!("C4C turn={} unit={} plant={} cell={},{} clause=ACCEPT wood={} turns={} score={}",view.turn,unit.id,c4c_idx,plant.cell.0,plant.cell.1,wood,turns,score);
                    out.push(Candidate{
                        command,score,target:Target::Tree(plant.cell),
                    }
                    );'''

PATCHES = [
    ("GATE_UNIT + per-unit entry record", GATE_OLD, GATE_NEW),
    ("DEAD_OR_UNREACHABLE + plant index", C1_OLD, C1_NEW),
    ("PREDICT_TREE_NONE", C2_OLD, C2_NEW),
    ("PREDICTED_NONPOSITIVE", C3_OLD, C3_NEW),
    ("CHOP_OUTCOME_NONE", C4_OLD, C4_NEW),
    ("ROUND_TRIP_CLOCK", C5_OLD, C5_NEW),
    ("WOOD_NONPOSITIVE", C6_OLD, C6_NEW),
    ("ACCEPT", ACCEPT_OLD, ACCEPT_NEW),
]

# every clause the subject can reach; the sweep refuses on any name outside this set
CLAUSES = ["GATE_UNIT", "DEAD_OR_UNREACHABLE", "PREDICT_TREE_NONE", "PREDICTED_NONPOSITIVE",
           "CHOP_OUTCOME_NONE", "ROUND_TRIP_CLOCK", "WOOD_NONPOSITIVE", "ACCEPT"]


def main():
    src = RESIDENT.read_text()
    digest = hashlib.sha256(src.encode()).hexdigest()
    if digest != RESIDENT_SHA:
        print(f"REFUSING: resident digest differs\n  want {RESIDENT_SHA}\n  got  {digest}")
        return 1

    out = src
    for name, old, new in PATCHES:
        if out.count(old) != 1:
            print(f"REFUSING: anchor '{name}' matched {out.count(old)} times, want exactly 1")
            return 1
        out = out.replace(old, new)

    # STRUCTURAL GUARDS, because "it compiled and the numbers looked plausible" is how the
    # pool-3 table was confidently wrong for a day.
    for clause in CLAUSES:
        n = out.count(f"clause={clause} ")
        if n != 1:
            print(f"REFUSING: clause {clause} has {n} taps, want exactly 1")
            return 1

    # Every reject tap must sit INSIDE chop_candidates, before its own `continue`. If a tap
    # drifted outside the function the row would no longer mean "the bot executed this clause".
    fn_start = out.index("fn chop_candidates(")
    fn_end = out.index("fn wait()", fn_start)
    for clause in CLAUSES:
        pos = out.index(f"clause={clause} ")
        if not (fn_start < pos < fn_end):
            print(f"REFUSING: tap for {clause} is outside chop_candidates")
            return 1

    # the subject must be otherwise untouched: only eprintln lines and the enumerate() rebind
    added = [ln for ln in out.splitlines() if ln.strip() and ln not in src.splitlines()]
    non_log = [ln for ln in added if "eprintln!" not in ln]
    if [ln for ln in non_log if "c4c_idx,plant)in view.plants.iter().enumerate()" not in ln]:
        print(f"REFUSING: instrument changed non-logging source lines:\n  " +
              "\n  ".join(non_log[:5]))
        return 1

    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  {len(CLAUSES)} clause taps, all inside chop_candidates, all unprivileged")
    print(f"  sha256(instrument) = {hashlib.sha256(out.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
