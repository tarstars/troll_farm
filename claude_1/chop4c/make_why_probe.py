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
RESIDENT = REPO / "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs"
OUT = REPO / "claude_1/chop4c/why-probe.rs"
RESIDENT_SHA = "98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29"

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
OPP_NEW = '''                if on_tree>0{
                    eprintln!("WHYOPP source=ON_TREE value={} cell={},{} health={}",on_tree,plant.cell.0,plant.cell.1,plant.health);
                    return on_tree;
                    }
                let expected=tree_health(plant.kind,plant.size);
                if plant.health<expected{
                    eprintln!("WHYOPP source=DAMAGED_FLAT1 value=1 cell={},{} health={} expected={}",plant.cell.0,plant.cell.1,plant.health,expected);
                    1
                }
                else{
                    eprintln!("WHYOPP source=NONE value=0 cell={},{} health={} expected={}",plant.cell.0,plant.cell.1,plant.health,expected);
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
NONE_NEW = '''                let mut hs_iter=0;
                for _ in 0..turns{
                    hs_iter+=1;
                    if opp_chop>0{
                        health-=opp_chop;
                        if health<=0{
                            eprintln!("WHY turn={} cell={},{} exit=NONE opp_chop={} start_health={} horizon={} died_at_iter={}",view.turn,plant.cell.0,plant.cell.1,opp_chop,plant.health,turns,hs_iter);
                            return None;
                            }
                        }'''

# 3. the Some exit, logged with equal fidelity
SOME_OLD = '''                Some(PredictedTree{
                    size,health,cooldown,
                }
                )
            }'''
SOME_NEW = '''                eprintln!("WHY turn={} cell={},{} exit=SOME opp_chop={} start_health={} horizon={} end_health={} end_size={}",view.turn,plant.cell.0,plant.cell.1,opp_chop,plant.health,turns,health,size);
                Some(PredictedTree{
                    size,health,cooldown,
                }
                )
            }'''

PATCHES = [("opp_chop provenance", OPP_OLD, OPP_NEW),
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
                         if 'eprintln!("WHY' not in l and "let mut hs_iter=0;" not in l
                         and "hs_iter+=1;" not in l)
    if stripped != src.rstrip("\n"):
        print("REFUSING: probe changed the subject beyond logging + the declared counter")
        return 1
    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}")
    print("  stripped probe == subject (logging + declared counter only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
