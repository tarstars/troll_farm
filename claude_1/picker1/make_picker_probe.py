#!/usr/bin/env python3
r"""20260820-pair-selector-anti-benching Phase 1 — build the PICKER PROBE (diagnostics only).

Subject: the Phase-1 pinned subject `cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs`
(SHA `ad3bfefe…`), per the charter. Never a delivery candidate.

## What the probe records, and why it is one scoring path

`select()` (:665-711) is the joint pairing. For the two-unit case it enumerates the full cross
product of the two units' candidate lists, drops a pair on `compatible(a.target,b.target)` or
`stock_compatible(a,b,inventory)`, and otherwise maximises `a.score + b.score`.

The probe prints, per turn: every candidate the generator offered each unit with its OWN score
and target, every pair the selector actually enumerated with the OUTCOME OF THE SELECTOR'S OWN
`compatible` / `stock_compatible` CALLS, the pair sum, and the pair that won. Nothing is
recomputed: the two predicate calls are hoisted into `let` bindings and the original `if` reads
those bindings, so the logged verdict is by construction the verdict the selector used. That is
the one-scoring-path rule — the standing lesson from the retracted proxies of 08-15→17.

`select()` has no view, so the turn number is tapped at the CALL SITE and every row that follows
a `PS1TURN` row belongs to that turn.

Rows (stderr only; stdout — the command protocol — is untouched and parity-checked):

    PS1TURN   turn=<t>
    PS1BRANCH n_ids=<k> arm=<EMPTY|SINGLE|PAIR|GREEDY>
    PS1CAND   unit=<id> idx=<i> score=<f> target=<Debug> cmd=<command>
    PS1PAIR   ai=<i> bi=<j> compat=<bool> stock=<bool> sum=<f>
    PS1WIN    ai=<i> bi=<j> sum=<f>            (PAIR arm found a pair)
    PS1NOPAIR                                   (PAIR arm found none -> falls through to GREEDY)
    PS1GREEDY unit=<id> idx=<i|NONE> cmd=<command>

Guards, same discipline as every instrument on this track: refuses on a wrong subject digest or a
non-unique anchor.
"""
import hashlib, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SUBJECT = REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs"
SUBJECT_SHA = "ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1"
OUT = REPO / "claude_1/picker1/probe-picker1.rs"

# --- 1. turn tap at the call site -------------------------------------------------------
OLD_TURN = '''                let mut selected=MoisanBot::select(by_id,&view.inventories[0]);'''
NEW_TURN = '''                eprintln!("PS1TURN turn={}",view.turn);
                let mut selected=MoisanBot::select(by_id,&view.inventories[0]);'''

# --- 2. candidate dump + arm marker at the top of select() ------------------------------
OLD_HEAD = '''                let ids:Vec<i32> =candidates_by_id.keys().copied().collect();
                if ids.is_empty(){'''
NEW_HEAD = '''                let ids:Vec<i32> =candidates_by_id.keys().copied().collect();
                eprintln!("PS1BRANCH n_ids={} arm={}",ids.len(),
                    if ids.is_empty(){"EMPTY"}else if ids.len()==1{"SINGLE"}
                    else if ids.len()==2{"PAIR"}else{"GREEDY"});
                for (ps1_uid,ps1_cands) in candidates_by_id.iter(){
                    for (ps1_i,ps1_c) in ps1_cands.iter().enumerate(){
                        eprintln!("PS1CAND unit={} idx={} score={:.6} target={:?} cmd={}",
                            ps1_uid,ps1_i,ps1_c.score,ps1_c.target,ps1_c.command);
                        }
                    }
                if ids.is_empty(){'''

# --- 3. pair enumeration: hoist the selector's own predicate calls and print them --------
OLD_PAIR = '''                    let mut best_pair=None;
                    for a in&candidates_by_id[&ids[0]]{
                        for b in&candidates_by_id[&ids[1]]{
                            if!Self::compatible(a.target,b.target)||!Self::stock_compatible(a,b,inventory){
                                continue;
                                }
                            let score=a.score+b.score;
                            if score>best_score{
                                best_score=score;
                                best_pair=Some((a.command.clone(),b.command.clone()));
                                }
                            }
                        }
                    if let Some((a,b))=best_pair{
                        return vec![a,b];
                        }'''
NEW_PAIR = '''                    let mut best_pair=None;
                    let mut ps1_best_idx=(usize::MAX,usize::MAX);
                    for (ps1_ai,a) in candidates_by_id[&ids[0]].iter().enumerate(){
                        for (ps1_bi,b) in candidates_by_id[&ids[1]].iter().enumerate(){
                            let ps1_compat=Self::compatible(a.target,b.target);
                            let ps1_stock=Self::stock_compatible(a,b,inventory);
                            eprintln!("PS1PAIR ai={} bi={} compat={} stock={} sum={:.6}",
                                ps1_ai,ps1_bi,ps1_compat,ps1_stock,a.score+b.score);
                            if!ps1_compat||!ps1_stock{
                                continue;
                                }
                            let score=a.score+b.score;
                            if score>best_score{
                                best_score=score;
                                best_pair=Some((a.command.clone(),b.command.clone()));
                                ps1_best_idx=(ps1_ai,ps1_bi);
                                }
                            }
                        }
                    if let Some((a,b))=best_pair{
                        eprintln!("PS1WIN ai={} bi={} sum={:.6}",ps1_best_idx.0,ps1_best_idx.1,best_score);
                        return vec![a,b];
                        }
                    eprintln!("PS1NOPAIR");'''

# --- 4. greedy arm ----------------------------------------------------------------------
OLD_GREEDY = '''                    used_targets.push(best.target);'''
NEW_GREEDY = '''                    eprintln!("PS1GREEDY unit={} cmd={}",id,best.command);
                    used_targets.push(best.target);'''


def patch(src, old, new, what):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"REFUSING: {what} anchor matched {n} times, want exactly 1")
    return src.replace(old, new)


def main():
    src = SUBJECT.read_text()
    got = hashlib.sha256(src.encode()).hexdigest()
    if got != SUBJECT_SHA:
        raise SystemExit(f"REFUSING: subject digest differs\n  want {SUBJECT_SHA}\n  got  {got}")
    out = src
    out = patch(out, OLD_TURN, NEW_TURN, "turn tap")
    out = patch(out, OLD_HEAD, NEW_HEAD, "select head")
    out = patch(out, OLD_PAIR, NEW_PAIR, "pair loop")
    out = patch(out, OLD_GREEDY, NEW_GREEDY, "greedy arm")
    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)}  sha256={hashlib.sha256(out.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
