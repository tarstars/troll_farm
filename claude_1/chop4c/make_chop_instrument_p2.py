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
import sys as _sys
SUBJECT = Path(_sys.argv[1]) if len(_sys.argv) > 1 else None
RESIDENT = SUBJECT
OUT = Path(_sys.argv[2]) if len(_sys.argv) > 2 else REPO / "claude_1/chop4c/instr-p2.rs"
RESIDENT_SHA = _sys.argv[3] if len(_sys.argv) > 3 else None

# Each entry: (name, anchor, replacement). Anchors are taken verbatim from the resident; the
# builder refuses on any anchor that does not match EXACTLY once, because a silent second match
# instruments the wrong site — the same disease as a tap that logs the wrong stage.

# unit-level gate: the loop never runs, so no per-plant row would otherwise exist
GATE_OLD = '''                let mut out=Vec::new();
                if unit.stats.chop_power<=0||unit.free_capacity()<=0{
                    return out;
                    }'''
GATE_NEW = '''                let mut out=Vec::new();
                static C4C_CALLS:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
                let c4c_call=C4C_CALLS.fetch_add(1,std::sync::atomic::Ordering::Relaxed);
                if unit.stats.chop_power<=0||unit.free_capacity()<=0{
                    eprintln!("C4CV call={} turn={} unit={} plant=-1 seq=0 clause=GATE_UNIT verdict=REJECT chop_power={} free_cap={}",c4c_call,view.turn,unit.id,unit.stats.chop_power,unit.free_capacity());
                    eprintln!("C4CGATE call={} turn={} unit={} plants=0 gate=REJECT chop_power={} free_cap={}",c4c_call,view.turn,unit.id,unit.stats.chop_power,unit.free_capacity());
                    return out;
                    }
                eprintln!("C4CV call={} turn={} unit={} plant=-1 seq=0 clause=GATE_UNIT verdict=PASS chop_power={} free_cap={}",c4c_call,view.turn,unit.id,unit.stats.chop_power,unit.free_capacity());
                eprintln!("C4CGATE call={} turn={} unit={} plants={} gate=PASS chop_power={} free_cap={}",c4c_call,view.turn,unit.id,view.plants.len(),unit.stats.chop_power,unit.free_capacity());'''

C1_OLD = '''                for plant in&view.plants{
                    if plant.health<=0||!from_unit.contains_key(&plant.cell){
                        continue;
                        }'''
C1_NEW = '''                for(c4c_idx,plant)in view.plants.iter().enumerate(){
                    if plant.health<=0||!from_unit.contains_key(&plant.cell){
                        eprintln!("C4CV call={} turn={} unit={} plant={} seq=1 clause=DEAD_OR_UNREACHABLE verdict=REJECT health={} reachable={}",c4c_call,view.turn,unit.id,c4c_idx,plant.health,from_unit.contains_key(&plant.cell));
                        continue;
                        }
                    eprintln!("C4CV call={} turn={} unit={} plant={} seq=1 clause=DEAD_OR_UNREACHABLE verdict=PASS health={} reachable=true",c4c_call,view.turn,unit.id,c4c_idx,plant.health);'''

C2_OLD = '''                    let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{
                        continue;
                        }
                    ;'''
C2_NEW = '''                    let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{
                        eprintln!("C4CV call={} turn={} unit={} plant={} seq=2 clause=PREDICT_TREE_NONE verdict=REJECT travel_turns={} size={} health={}",c4c_call,view.turn,unit.id,c4c_idx,travel_turns,plant.size,plant.health);
                        continue;
                        }
                    ;
                    eprintln!("C4CV call={} turn={} unit={} plant={} seq=2 clause=PREDICT_TREE_NONE verdict=PASS travel_turns={} size={} health={}",c4c_call,view.turn,unit.id,c4c_idx,travel_turns,plant.size,plant.health);'''

C3_OLD = '''                    if predicted.size<=0||predicted.health<=0{
                        continue;
                        }'''
C3_NEW = '''                    if predicted.size<=0||predicted.health<=0{
                        eprintln!("C4CV call={} turn={} unit={} plant={} seq=3 clause=PREDICTED_NONPOSITIVE verdict=REJECT pred_size={} pred_health={}",c4c_call,view.turn,unit.id,c4c_idx,predicted.size,predicted.health);
                        continue;
                        }
                    eprintln!("C4CV call={} turn={} unit={} plant={} seq=3 clause=PREDICTED_NONPOSITIVE verdict=PASS pred_size={} pred_health={}",c4c_call,view.turn,unit.id,c4c_idx,predicted.size,predicted.health);'''

C4_OLD = '''                    let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{
                        continue;
                        }
                    ;'''
C4_NEW = '''                    let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{
                        eprintln!("C4CV call={} turn={} unit={} plant={} seq=4 clause=CHOP_OUTCOME_NONE verdict=REJECT pred_size={} chop_power={}",c4c_call,view.turn,unit.id,c4c_idx,predicted.size,unit.stats.chop_power);
                        continue;
                        }
                    ;
                    eprintln!("C4CV call={} turn={} unit={} plant={} seq=4 clause=CHOP_OUTCOME_NONE verdict=PASS chop_turns={} final_size={}",c4c_call,view.turn,unit.id,c4c_idx,chop_turns,final_size);'''

C5_OLD = '''                    if turns>TOTAL_TURNS-view.turn+1{
                        continue;
                        }'''
C5_NEW = '''                    if turns>TOTAL_TURNS-view.turn+1{
                        eprintln!("C4CV call={} turn={} unit={} plant={} seq=5 clause=ROUND_TRIP_CLOCK verdict=REJECT turns={} remaining={}",c4c_call,view.turn,unit.id,c4c_idx,turns,TOTAL_TURNS-view.turn+1);
                        continue;
                        }
                    eprintln!("C4CV call={} turn={} unit={} plant={} seq=5 clause=ROUND_TRIP_CLOCK verdict=PASS turns={} remaining={}",c4c_call,view.turn,unit.id,c4c_idx,turns,TOTAL_TURNS-view.turn+1);'''

C6_OLD = '''                    let wood=final_size.min(unit.free_capacity());
                    if wood<=0{
                        continue;
                        }'''
C6_NEW = '''                    let wood=final_size.min(unit.free_capacity());
                    if wood<=0{
                        eprintln!("C4CV call={} turn={} unit={} plant={} seq=6 clause=WOOD_NONPOSITIVE verdict=REJECT wood={} final_size={}",c4c_call,view.turn,unit.id,c4c_idx,wood,final_size);
                        continue;
                        }
                    eprintln!("C4CV call={} turn={} unit={} plant={} seq=6 clause=WOOD_NONPOSITIVE verdict=PASS wood={} final_size={}",c4c_call,view.turn,unit.id,c4c_idx,wood,final_size);'''

ACCEPT_OLD = '''                    out.push(Candidate{
                        command,score,target:Target::Tree(plant.cell),
                    }
                    );'''
ACCEPT_NEW = '''                    eprintln!("C4CV call={} turn={} unit={} plant={} seq=7 clause=ACCEPT verdict=ACCEPT wood={} turns={} score={}",c4c_call,view.turn,unit.id,c4c_idx,wood,turns,score);
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
    if RESIDENT_SHA is not None and digest != RESIDENT_SHA:
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
    # Each clause must carry BOTH verdict rows (PASS and REJECT), except ACCEPT which is the
    # terminal row. codex_1 blocker 1: a terminal-decision logger cannot name a clause, because a
    # tree rejected at clause N leaves clauses 1..N-1 with no evidence they were even reached.
    for clause in CLAUSES:
        if clause == "ACCEPT":
            want = {"verdict=ACCEPT": 1}
        else:
            want = {"verdict=PASS": 1, "verdict=REJECT": 1}
        for verdict, n_want in want.items():
            n = sum(1 for ln in out.splitlines()
                    if f"clause={clause} " in ln and verdict in ln)
            if n != n_want:
                print(f"REFUSING: clause {clause} has {n} '{verdict}' taps, want {n_want}")
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

    # BLOCKER 4 REPAIR. The old guard asked "is each added line absent from the source's line
    # SET?" — which cannot see removals, reordering, multiplicity changes, or a behavioral line
    # that happens to duplicate an existing source line. A set-membership test standing in for a
    # diff is the same disease as a check that cannot fail. This is a real diff: strip every
    # logging line from the instrument and require what remains to be BYTE-IDENTICAL to the
    # subject, modulo the one declared structural edit (the enumerate() rebind).
    import difflib
    stripped = "\n".join(ln for ln in out.splitlines()
                           if "eprintln!(\"C4C" not in ln and "C4C_CALLS" not in ln
                           and "let c4c_call=" not in ln)
    canon = stripped.replace(
        "                for(c4c_idx,plant)in view.plants.iter().enumerate(){",
        "                for plant in&view.plants{")
    if canon != src.rstrip("\n"):
        d = list(difflib.unified_diff(src.rstrip("\n").splitlines(), canon.splitlines(),
                                      "resident", "instrument-minus-logging", lineterm="", n=1))
        print("REFUSING: instrument differs from the subject beyond logging + the declared "
              "enumerate() rebind:\n  " + "\n  ".join(d[:12]))
        return 1
    print("  non-logging diff: NONE (instrument minus logging == subject, modulo enumerate)")

    OUT.write_text(out)
    print(f"wrote {OUT}")
    print(f"  {len(CLAUSES)} clause taps, all inside chop_candidates, all unprivileged")
    print(f"  sha256(instrument) = {hashlib.sha256(out.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
