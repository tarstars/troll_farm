#!/usr/bin/env python3
r"""Phase 1 — make `predict_tree` say WHY it answers "nothing there".

Task `20260818-osc031-forecast-defect-fix`, chartered by the owner's DEFECT ruling.

`predict_tree` has **exactly one** `return None`, at the opponent-damage guard, so the probe's
job is not to find which exit fires but to measure WHY that guard fires, per evaluation:

  * where `opp_chop` came from — `predicted_opp_chop` has two sources: the **on-tree sum** of
    opponent chop power, or a **flat 1 when the tree is merely damaged** (`health < expected`)
    with no opponent present at all;
  * the health it started from, the loop iteration at which health reached <= 0, and the
    forecast horizon (`turns`) that allowed the loop to run that far.

UNPRIVILEGED: both the None exit and the Some exit are logged with the same fidelity, and the
`opp_chop` provenance is logged for every evaluation, not only the failing ones. The 4c discipline
applies unchanged — logged = executed, stdout untouched, parity verified before any row counts.
"""
import hashlib, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
RESIDENT = REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs"  # cure C: the resident since the owner KEEP
OUT = REPO / "claude_1/chop4c/predicate-probe.rs"
RESIDENT_SHA = "ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1"

# 1. provenance inside predicted_opp_chop — which of the two sources supplied the value
OPP_OLD = '''                if on_tree>0{
                    return on_tree;
                    }
                let expected=tree_health(plant.kind,plant.size);
                if plant.health<expected{
                    1
                }
                else{
                    0
                }
                }'''
OPP_NEW = '''                let c4c_adjacent:i32=view.units.iter().filter(|unit|unit.player==1&&is_adjacent(unit.cell,plant.cell)).map(|unit|unit.stats.chop_power).sum();
                let c4c_inreach:i32=view.units.iter().filter(|unit|unit.player==1&&bfs_distances(&view.walkable,&[unit.cell]).get(&plant.cell).map(|d|*d<=unit.stats.movement_speed.max(1)).unwrap_or(false)).map(|unit|unit.stats.chop_power).sum();
                let c4c_damaged=plant.health<tree_health(plant.kind,plant.size);
                eprintln!("PRED eval={} cell={},{} on_tree={} adjacent={} inreach={} damaged={} health={}",C4C_EVAL.load(std::sync::atomic::Ordering::Relaxed).saturating_sub(1),plant.cell.0,plant.cell.1,on_tree,c4c_adjacent,c4c_inreach,c4c_damaged,plant.health);
                if on_tree>0{
                    return on_tree;
                    }
                let expected=tree_health(plant.kind,plant.size);
                if plant.health<expected{
                    1
                }
                else{
                    0
                }
                }'''

# 2. the single None exit, with the iteration index and the state that produced it
NONE_OLD = '''                for _ in 0..turns{
                    if opp_chop>0{
                        health-=opp_chop;
                        if health<=0{
                            return None;
                            }
                        }'''
PT_ENTRY_OLD = '''                let mut size=plant.size;
                let mut health=plant.health;'''
PT_ENTRY_NEW = '''                let c4c_eval=C4C_EVAL.fetch_add(1,std::sync::atomic::Ordering::Relaxed);
                let mut size=plant.size;
                let mut health=plant.health;'''

NONE_NEW = '''                let mut hs_iter=0;
                for _ in 0..turns{
                    hs_iter+=1;
                    if opp_chop>0{
                        health-=opp_chop;
                        if health<=0{
                            eprintln!("WHY eval={} turn={} cell={},{} exit=NONE opp_chop={} start_health={} horizon={} died_at_iter={}",c4c_eval,view.turn,plant.cell.0,plant.cell.1,opp_chop,plant.health,turns,hs_iter);
                            return None;
                            }
                        }'''

# 3. the Some exit, logged with equal fidelity
SOME_OLD = '''                Some(PredictedTree{
                    size,health,cooldown,
                }
                )
            }'''
SOME_NEW = '''                eprintln!("WHY eval={} turn={} cell={},{} exit=SOME opp_chop={} start_health={} horizon={} end_health={} end_size={}",c4c_eval,view.turn,plant.cell.0,plant.cell.1,opp_chop,plant.health,turns,health,size);
                Some(PredictedTree{
                    size,health,cooldown,
                }
                )
            }'''

STATIC_OLD = '''        struct MoisanBot;'''
STATIC_NEW = '''        static C4C_EVAL:std::sync::atomic::AtomicUsize=std::sync::atomic::AtomicUsize::new(0);
        struct MoisanBot;'''

PATCHES = [("eval-id static", STATIC_OLD, STATIC_NEW),
           ("predicate measurement", OPP_OLD, OPP_NEW),
           ("eval-id counter", PT_ENTRY_OLD, PT_ENTRY_NEW),
           ("None exit", NONE_OLD, NONE_NEW),
           ("Some exit", SOME_OLD, SOME_NEW)]


def main():
    src = RESIDENT.read_text()
    if hashlib.sha256(src.encode()).hexdigest() != RESIDENT_SHA:
        print("REFUSING: resident digest differs")
        return 1
    out = src
    for name, old, new in PATCHES:
        if out.count(old) != 1:
            print(f"REFUSING: anchor '{name}' matched {out.count(old)} times, want 1")
            return 1
        out = out.replace(old, new)
    # only logging + the declared iteration counter may differ from the subject
    stripped = "\n".join(l for l in out.splitlines()
                         if 'eprintln!("WHY' not in l and 'eprintln!("PRED' not in l
                         and "let mut hs_iter=0;" not in l and "hs_iter+=1;" not in l
                         and "let c4c_adjacent:" not in l and "let c4c_inreach:" not in l
                         and "let c4c_damaged=" not in l and "C4C_EVAL" not in l and "let c4c_eval=" not in l)
    if stripped != src.rstrip("\n"):
        print("REFUSING: probe changed the subject beyond logging + the declared counter")
        return 1
    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}")
    print("  stripped probe == subject (logging + declared counter only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
