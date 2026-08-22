#!/usr/bin/env python3
r"""Phase 2 — ONE probe builder for BOTH arms (base and P1+P2 candidate), on BOTH bases.

Phase 1's probe could only instrument the unmodified pair loop. The Phase-2 gate needs the SAME
word `benched` measured on the candidate as on the base, or the fail-first claim is comparing two
different definitions. So this builder recognises either pair-loop shape — the incumbent loop or
the P1+P2 loop `make_pair_selector_candidate.py` emits — and taps it the same way:

    PS2TURN   turn=<t>
    PS2BRANCH n_ids=<k> arm=<EMPTY|SINGLE|PAIR|GREEDY>
    PS2CAND   unit=<id> idx=<i> score=<f> target=<Debug> cmd=<command>
    PS2PAIR   ai=<i> bi=<j> compat=<b> stock=<b> p1drop=<b> waits=<n> sum=<f>
    PS2WIN    ai=<i> bi=<j> sum=<f>
    PS2NOPAIR
    PS2GREEDY unit=<id> cmd=<command>

`p1drop` is `false` on every row of a base arm — the clause does not exist there — so one parser
and one classifier read both arms. On a candidate arm it is the selector's OWN `self_blocked`
call, hoisted into a `let` and read by the original `if`, exactly as `compat`/`stock` are. One
scoring path: no row recomputes anything.

Guards: the source digest must be in the allowlist; each anchor must match exactly once; and the
two pair-loop shapes must not BOTH match (an ambiguous subject is refused, not guessed at).

Run:  python3 claude_1/picker2/make_probe.py
"""
import hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

SUBJECTS = {
    "cureC-base": (REPO / "cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs",
                   "ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1"),
    "door1-base": (REPO / "claude_1/chop4c/candidate-door1.rs",
                   "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"),
    "cureC-p1p2": (HERE / "candidate-cureC-p1p2.rs", None),   # digest from the build manifest
    "door1-p1p2": (HERE / "candidate-door1-p1p2.rs", None),
}

OLD_TURN = '''                let mut selected=MoisanBot::select(by_id,&view.inventories[0]'''
NEW_TURN = '''                eprintln!("PS2TURN turn={}",view.turn);
                let mut selected=MoisanBot::select(by_id,&view.inventories[0]'''

OLD_HEAD = '''                let ids:Vec<i32> =candidates_by_id.keys().copied().collect();
                if ids.is_empty(){'''
NEW_HEAD = '''                let ids:Vec<i32> =candidates_by_id.keys().copied().collect();
                eprintln!("PS2BRANCH n_ids={} arm={}",ids.len(),
                    if ids.is_empty(){"EMPTY"}else if ids.len()==1{"SINGLE"}
                    else if ids.len()==2{"PAIR"}else{"GREEDY"});
                for (ps2_uid,ps2_cands) in candidates_by_id.iter(){
                    for (ps2_i,ps2_c) in ps2_cands.iter().enumerate(){
                        eprintln!("PS2CAND unit={} idx={} score={:.6} target={:?} cmd={}",
                            ps2_uid,ps2_i,ps2_c.score,ps2_c.target,ps2_c.command);
                        }
                    }
                if ids.is_empty(){'''

BASE_PAIR_OLD = '''                    let mut best_pair=None;
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
BASE_PAIR_NEW = '''                    let mut best_pair=None;
                    let mut ps2_best_idx=(usize::MAX,usize::MAX);
                    for (ps2_ai,a) in candidates_by_id[&ids[0]].iter().enumerate(){
                        for (ps2_bi,b) in candidates_by_id[&ids[1]].iter().enumerate(){
                            let ps2_compat=Self::compatible(a.target,b.target);
                            let ps2_stock=Self::stock_compatible(a,b,inventory);
                            eprintln!("PS2PAIR ai={} bi={} compat={} stock={} p1drop=false waits={} sum={:.6}",
                                ps2_ai,ps2_bi,ps2_compat,ps2_stock,
                                (a.command=="WAIT") as usize+(b.command=="WAIT") as usize,
                                a.score+b.score);
                            if!ps2_compat||!ps2_stock{
                                continue;
                                }
                            let score=a.score+b.score;
                            if score>best_score{
                                best_score=score;
                                best_pair=Some((a.command.clone(),b.command.clone()));
                                ps2_best_idx=(ps2_ai,ps2_bi);
                                }
                            }
                        }
                    if let Some((a,b))=best_pair{
                        eprintln!("PS2WIN ai={} bi={} sum={:.6}",ps2_best_idx.0,ps2_best_idx.1,best_score);
                        return vec![a,b];
                        }
                    eprintln!("PS2NOPAIR");'''

CAND_PAIR_OLD = '''                    let mut best_pair=None;
                    let mut best_waits=usize::MAX;
                    for a in&candidates_by_id[&ids[0]]{
                        for b in&candidates_by_id[&ids[1]]{
                            if!Self::compatible(a.target,b.target)||!Self::stock_compatible(a,b,inventory){
                                continue;
                                }
                            if Self::self_blocked(ids[0],a,ids[1],b,unit_cells){
                                continue;
                                }
                            let score=a.score+b.score;
                            let waits=Self::wait_count(a,b);
                            if score>best_score||(best_pair.is_some()&&score==best_score&&waits<best_waits){
                                best_score=score;
                                best_waits=waits;
                                best_pair=Some((a.command.clone(),b.command.clone()));
                                }
                            }
                        }
                    if let Some((a,b))=best_pair{
                        return vec![a,b];
                        }'''
CAND_PAIR_NEW = '''                    let mut best_pair=None;
                    let mut best_waits=usize::MAX;
                    let mut ps2_best_idx=(usize::MAX,usize::MAX);
                    for (ps2_ai,a) in candidates_by_id[&ids[0]].iter().enumerate(){
                        for (ps2_bi,b) in candidates_by_id[&ids[1]].iter().enumerate(){
                            let ps2_compat=Self::compatible(a.target,b.target);
                            let ps2_stock=Self::stock_compatible(a,b,inventory);
                            let ps2_drop=Self::self_blocked(ids[0],a,ids[1],b,unit_cells);
                            let waits=Self::wait_count(a,b);
                            eprintln!("PS2PAIR ai={} bi={} compat={} stock={} p1drop={} waits={} sum={:.6}",
                                ps2_ai,ps2_bi,ps2_compat,ps2_stock,ps2_drop,waits,a.score+b.score);
                            if!ps2_compat||!ps2_stock{
                                continue;
                                }
                            if ps2_drop{
                                continue;
                                }
                            let score=a.score+b.score;
                            if score>best_score||(best_pair.is_some()&&score==best_score&&waits<best_waits){
                                best_score=score;
                                best_waits=waits;
                                best_pair=Some((a.command.clone(),b.command.clone()));
                                ps2_best_idx=(ps2_ai,ps2_bi);
                                }
                            }
                        }
                    if let Some((a,b))=best_pair{
                        eprintln!("PS2WIN ai={} bi={} sum={:.6}",ps2_best_idx.0,ps2_best_idx.1,best_score);
                        return vec![a,b];
                        }
                    eprintln!("PS2NOPAIR");'''

OLD_GREEDY = '''                    used_targets.push(best.target);'''
NEW_GREEDY = '''                    eprintln!("PS2GREEDY unit={} cmd={}",id,best.command);
                    used_targets.push(best.target);'''


def patch(src, old, new, what):
    n = src.count(old)
    if n != 1:
        raise SystemExit(f"REFUSING: {what} anchor matched {n} times, want exactly 1")
    return src.replace(old, new)


def build(name):
    src_path, want = SUBJECTS[name]
    src = src_path.read_text()
    got = hashlib.sha256(src.encode()).hexdigest()
    if want is not None and got != want:
        raise SystemExit(f"REFUSING {name}: digest {got[:16]}… != allowlisted {want[:16]}…")
    if want is None:                       # candidates: digest must match the build manifest
        man = json.loads((HERE / "build-manifest-2026-08-20.json").read_text())
        base = name.split("-")[0]
        if got != man[base]["cand_sha256"]:
            raise SystemExit(f"REFUSING {name}: digest {got[:16]}… != build manifest "
                             f"{man[base]['cand_sha256'][:16]}… — rebuild before probing")
    has_base = src.count(BASE_PAIR_OLD)
    has_cand = src.count(CAND_PAIR_OLD)
    if has_base + has_cand != 1:
        raise SystemExit(f"REFUSING {name}: pair loop is ambiguous "
                         f"(base shape x{has_base}, P1+P2 shape x{has_cand})")
    out = patch(src, OLD_TURN, NEW_TURN, "turn tap")
    out = patch(out, OLD_HEAD, NEW_HEAD, "select head")
    if has_base:
        out = patch(out, BASE_PAIR_OLD, BASE_PAIR_NEW, "base pair loop")
    else:
        out = patch(out, CAND_PAIR_OLD, CAND_PAIR_NEW, "P1+P2 pair loop")
    out = patch(out, OLD_GREEDY, NEW_GREEDY, "greedy arm")
    dst = HERE / f"probe-{name}.rs"
    dst.write_text(out)
    return {"name": name, "source": str(src_path.relative_to(REPO)), "source_sha256": got,
            "arm": "base" if has_base else "p1p2", "probe": str(dst.relative_to(REPO)),
            "probe_sha256": hashlib.sha256(out.encode()).hexdigest()}


def main():
    man = {}
    for n in SUBJECTS:
        r = build(n)
        man[n] = r
        print(f"  {n:11} arm={r['arm']:5} {r['probe']}  sha256={r['probe_sha256'][:16]}…")
    (HERE / "probe-manifest-2026-08-20.json").write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
