#!/usr/bin/env python3
r"""Unified gate-1 probe: clause terminals and forecast attribution under ONE stable identity.

codex_1's requirement: the caller's terminal row and the forecast attribution must share a stable
evaluation identity so every `PREDICT_TREE_NONE` terminal joins to exactly one attribution
without ambiguity. Two separately-keyed streams cannot support that join, which is why the
previous inline attribution was refused.

Identity = `(call, plant)`, where `call` is the per-`chop_candidates` invocation counter and
`plant` the plant index in that invocation's loop. `chop_candidates` stashes both into statics
immediately before calling `predict_tree`; the attribution tap inside `predict_tree` reads them.
Single-threaded execution makes the stash exact, and the runner proves the join rather than
assuming it.

The attribution recomputes the on-tree opponent sum independently from `view.units` at the
rejection site — it does NOT echo what `predicted_opp_chop` returned, so the two derivations can
disagree, and on the cure-C subject they must.
"""
import hashlib, sys
from pathlib import Path

SUBJECT = Path(sys.argv[1]); OUT = Path(sys.argv[2]); SHA = sys.argv[3]

STATICS_OLD = '''        struct MoisanBot;'''
STATICS_NEW = '''        static C4C_CALLS:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
        static C4C_CUR_CALL:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
        static C4C_CUR_PLANT:std::sync::atomic::AtomicIsize=std::sync::atomic::AtomicIsize::new(-1);
        struct MoisanBot;'''

GATE_OLD = '''                let mut out=Vec::new();
                if unit.stats.chop_power<=0||unit.free_capacity()<=0{
                    return out;
                    }'''
GATE_NEW = '''                let mut out=Vec::new();
                let c4c_call=C4C_CALLS.fetch_add(1,std::sync::atomic::Ordering::Relaxed);
                if unit.stats.chop_power<=0||unit.free_capacity()<=0{
                    eprintln!("UGATE call={} turn={} unit={} plants=0 gate=REJECT",c4c_call,view.turn,unit.id);
                    return out;
                    }
                eprintln!("UGATE call={} turn={} unit={} plants={} gate=PASS",c4c_call,view.turn,unit.id,view.plants.len());'''

LOOP_OLD = '''                for plant in&view.plants{
                    if plant.health<=0||!from_unit.contains_key(&plant.cell){
                        continue;
                        }'''
LOOP_NEW = '''                for(c4c_idx,plant)in view.plants.iter().enumerate(){
                    if plant.health<=0||!from_unit.contains_key(&plant.cell){
                        eprintln!("UTERM call={} plant={} turn={} clause=DEAD_OR_UNREACHABLE",c4c_call,c4c_idx,view.turn);
                        continue;
                        }'''

PT_OLD = '''                    let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{
                        continue;
                        }
                    ;'''
# `USEQ2` is the sequence-2 ENTRY row, emitted immediately before the forecast call and under the
# same `(call, plant)` identity. It exists so the runner can OBSERVE how many evaluations entered
# the forecast instead of DEFINING that number as the sum of the two observed exits -- codex_1's
# second tautology finding (2026-08-19): the previous `seq2_rows` was assigned, never measured, so
# the identity it fed could not fail on real data. A distinct prefix (not `UTERM`) keeps it out of
# the terminal cross-sums, where an entry marker does not belong.
PT_NEW = '''                    C4C_CUR_CALL.store(c4c_call,std::sync::atomic::Ordering::Relaxed);
                    C4C_CUR_PLANT.store(c4c_idx as isize,std::sync::atomic::Ordering::Relaxed);
                    eprintln!("USEQ2 call={} plant={} turn={}",c4c_call,c4c_idx,view.turn);
                    let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{
                        eprintln!("UTERM call={} plant={} turn={} clause=PREDICT_TREE_NONE",c4c_call,c4c_idx,view.turn);
                        continue;
                        }
                    ;'''

ACCEPT_OLD = '''                    out.push(Candidate{
                        command,score,target:Target::Tree(plant.cell),
                    }
                    );'''
ACCEPT_NEW = '''                    eprintln!("UTERM call={} plant={} turn={} clause=ACCEPT",c4c_call,c4c_idx,view.turn);
                    out.push(Candidate{
                        command,score,target:Target::Tree(plant.cell),
                    }
                    );'''

ATTRIB_OLD = '''                    if opp_chop>0{
                        health-=opp_chop;
                        if health<=0{
                            return None;
                            }
                        }'''
ATTRIB_NEW = '''                    if opp_chop>0{
                        health-=opp_chop;
                        if health<=0{
                            let ot:i32=view.units.iter().filter(|u|u.player==1&&u.cell==plant.cell).map(|u|u.stats.chop_power).sum();
                            eprintln!("UATTR call={} plant={} opp_chop={} on_tree_recomputed={} verdict={}",C4C_CUR_CALL.load(std::sync::atomic::Ordering::Relaxed),C4C_CUR_PLANT.load(std::sync::atomic::Ordering::Relaxed),opp_chop,ot,if ot>0{"EVIDENCE_BASED"}else{"UNEXPLAINED"});
                            return None;
                            }
                        }'''


# Every downstream exit, plus the sequence-2 PASS. Without these the chain cross-sum compares
# emitted rows against themselves and cannot see an evaluation vanish through an unlogged
# `continue` -- codex_1's tautology finding.
SEQ2PASS_NEW = PT_NEW + """
                    eprintln!("UTERM call={} plant={} turn={} clause=SEQ2_PASS",c4c_call,c4c_idx,view.turn);"""

D1_OLD = """                    if predicted.size<=0||predicted.health<=0{
                        continue;
                        }"""
D1_NEW = """                    if predicted.size<=0||predicted.health<=0{
                        eprintln!("UTERM call={} plant={} turn={} clause=PREDICTED_NONPOSITIVE",c4c_call,c4c_idx,view.turn);
                        continue;
                        }"""

D2_OLD = """                    let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{
                        continue;
                        }
                    ;"""
D2_NEW = """                    let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{
                        eprintln!("UTERM call={} plant={} turn={} clause=CHOP_OUTCOME_NONE",c4c_call,c4c_idx,view.turn);
                        continue;
                        }
                    ;"""

D3_OLD = """                    if turns>TOTAL_TURNS-view.turn+1{
                        continue;
                        }"""
D3_NEW = """                    if turns>TOTAL_TURNS-view.turn+1{
                        eprintln!("UTERM call={} plant={} turn={} clause=ROUND_TRIP_CLOCK",c4c_call,c4c_idx,view.turn);
                        continue;
                        }"""

D4_OLD = """                    let wood=final_size.min(unit.free_capacity());
                    if wood<=0{
                        continue;
                        }"""
D4_NEW = """                    let wood=final_size.min(unit.free_capacity());
                    if wood<=0{
                        eprintln!("UTERM call={} plant={} turn={} clause=WOOD_NONPOSITIVE",c4c_call,c4c_idx,view.turn);
                        continue;
                        }"""

PATCHES = [("statics", STATICS_OLD, STATICS_NEW), ("gate", GATE_OLD, GATE_NEW),
           ("loop", LOOP_OLD, LOOP_NEW), ("predict_tree call + seq2 pass", PT_OLD, SEQ2PASS_NEW),
           ("predicted nonpositive", D1_OLD, D1_NEW),
           ("chop outcome none", D2_OLD, D2_NEW),
           ("round trip clock", D3_OLD, D3_NEW),
           ("wood nonpositive", D4_OLD, D4_NEW),
           ("accept", ACCEPT_OLD, ACCEPT_NEW), ("attribution", ATTRIB_OLD, ATTRIB_NEW)]
ADDED_MARKERS = ("eprintln!(\"U", "let c4c_call=", "C4C_CUR_CALL.store", "C4C_CUR_PLANT.store",
                 "let ot:i32=", "static C4C_")


def main():
    src = SUBJECT.read_text()
    if hashlib.sha256(src.encode()).hexdigest() != SHA:
        print("REFUSING: subject digest differs"); return 1
    out = src
    for name, old, new in PATCHES:
        if out.count(old) != 1:
            print(f"REFUSING: anchor {name!r} matched {out.count(old)} times"); return 1
        out = out.replace(old, new)
    stripped = "\n".join(l for l in out.splitlines()
                         if not any(m in l for m in ADDED_MARKERS))
    canon = stripped.replace(
        "                for(c4c_idx,plant)in view.plants.iter().enumerate(){",
        "                for plant in&view.plants{")
    if canon != src.rstrip("\n"):
        print("REFUSING: probe changed the subject beyond logging + declared bookkeeping")
        return 1
    OUT.write_text(out)
    print(f"wrote {OUT}  sha256={hashlib.sha256(out.encode()).hexdigest()[:16]}…")
    return 0


if __name__ == "__main__":
    sys.exit(main())
