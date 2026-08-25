#!/usr/bin/env python3
r"""Attribute every residual PREDICT_TREE_NONE under the Door-1 candidate.

codex_1's rule: EVIDENCE_BASED iff the on-tree opponent chop-power sum is positive at the
rejection, otherwise UNEXPLAINED. Green is **zero UNEXPLAINED**, not zero rejections.

Their warning is the design constraint: the attribution must not "merely restate the candidate
branch". So the tap does NOT log the value `predicted_opp_chop` returned — it recomputes the
on-tree sum independently at the `return None` site, from `view.units`, and logs both. If the fix
is doing what it claims, the two agree; if they ever disagree, that is a finding, and the
comparison is only possible because the quantity is computed twice by different code.
"""
import hashlib, sys
from pathlib import Path

SUBJECT = Path(sys.argv[1]); OUT = Path(sys.argv[2]); SHA = sys.argv[3]

OLD = '''                    if opp_chop>0{
                        health-=opp_chop;
                        if health<=0{
                            return None;
                            }
                        }'''
NEW = '''                    if opp_chop>0{
                        health-=opp_chop;
                        if health<=0{
                            let attrib_on_tree:i32=view.units.iter().filter(|u|u.player==1&&u.cell==plant.cell).map(|u|u.stats.chop_power).sum();
                            eprintln!("ATTRIB turn={} cell={},{} opp_chop={} on_tree_recomputed={} verdict={}",view.turn,plant.cell.0,plant.cell.1,opp_chop,attrib_on_tree,if attrib_on_tree>0{"EVIDENCE_BASED"}else{"UNEXPLAINED"});
                            return None;
                            }
                        }'''


def main():
    src = SUBJECT.read_text()
    if hashlib.sha256(src.encode()).hexdigest() != SHA:
        print("REFUSING: subject digest differs"); return 1
    if src.count(OLD) != 1:
        print(f"REFUSING: anchor matched {src.count(OLD)} times"); return 1
    out = src.replace(OLD, NEW)
    stripped = "\n".join(l for l in out.splitlines()
                         if 'eprintln!("ATTRIB' not in l and "let attrib_on_tree:" not in l)
    if stripped != src.rstrip("\n"):
        print("REFUSING: probe changed the subject beyond its two declared lines"); return 1
    OUT.write_text(out); print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
