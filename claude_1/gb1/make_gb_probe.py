#!/usr/bin/env python3
r"""G-b on real games — build the dual-variant probe from the source that PLAYED them.

Subject: `claude_1/narrate1/instrument-swap-r1-narrate-v2.rs`, the NARRATE v2 instrument that
played the 149 ladder games of agent `6652424`.  Its idle-regeneration fallback is
BYTE-IDENTICAL to the Phase 3b incumbent (REPLACE) body, so the states this bot naturally reached
are exactly the states Phase 3b's §5 asks about.

The probe carries BOTH ruled fallback bodies, literally, selected by a thread-local flag read at
the one site.  Design r2 §5 says "two separately named generator functions"; a flag on one
function is the same experiment with a stronger guarantee -- the other ~180 lines of
`main_candidates` cannot drift between the arms because there is only one copy.  This deviation is
declared, not hidden, and the probe-parity gate below is what makes it safe.

Emitted rows (the probe prints, the analyser classifies -- the Phase 3b convention):

    GBFALL turn=<t> unit=<id> carried=<n> out=<items> ret=<items>
    GBLIST turn=<t> unit=<id> base=<items> cand=<items>
    GBFORK turn=<t> base=<cmds> cand=<cmds> same=<bool>

`GBFALL` is the state of `out` at fallback entry and what the incumbent returns instead.
`GBLIST`/`GBFORK` are emitted only on turns carrying at least one `carried>0` fallback -- i.e.
candidate Delta-B turns -- and `GBFORK` is design §5 step 4 run for real: `select_recording` plus
`resolve_move_conflicts` over the SAME state with only the generator variant switched.

`--poison` builds the control arm: the EXTEND body additionally appends one candidate the REPLACE
body cannot produce.  On that arm `GBFORK same=false` MUST appear, or the fork is inert and every
`same=true` it prints is worthless.

Guards, all fail-closed: the subject digest is pinned; every anchor must match exactly once; and
everything outside `main_candidates` and `commands` must be byte-identical to the subject.

Run:  python3 claude_1/gb1/make_gb_probe.py [--poison] [--out PATH]
"""
from __future__ import annotations

import argparse, hashlib, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SUBJECT = REPO / "claude_1" / "narrate1" / "instrument-swap-r1-narrate-v2.rs"
SUBJECT_SHA = "aaebc503cc2660e9"   # sha256 prefix of the subject that played the 149 games

DUMP = ('.iter().map(|c|format!("{}|{:.6}|{:?}",c.command,c.score,c.target))'
        '.collect::<Vec<_>>().join("~")')

REC_ANCHOR = "        struct MoisanBot;\n"
REC_NEW = """        thread_local!{
            pub static GB_FALLBACK:std::cell::RefCell<Vec<(i32,i32,String,String)>> =std::cell::RefCell::new(Vec::new());
            pub static GB_EXTEND:std::cell::Cell<bool> =std::cell::Cell::new(false);
            }
        struct MoisanBot;
"""

FALL_OLD = """                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    return fallback;
                    }
"""

# The EXTEND body is the ruled Phase 3b snippet, verbatim.  POISON adds one candidate that the
# REPLACE arm cannot produce, so a fork that cannot see a difference is caught.
FALL_NEW_TMPL = """                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    GB_FALLBACK.with(|rec|rec.borrow_mut().push((unit.id,unit.total_carried(),
                        out%(DUMP)s,fallback%(DUMP)s)));
                    if GB_EXTEND.with(|flag|flag.get()){
                        out.extend(Self::idle_harvest_candidates(view,unit));
                        if unit.total_carried()>0{
                            out.extend(Self::bank_candidates(view,unit));
                            }
%(POISON)s                        return out;
                        }
                    return fallback;
                    }
"""

POISON = """                        out.push(Candidate{
                            command:format!("MOVE {} {} {}",unit.id,view.shacks[0].0,view.shacks[0].1),score:99999.0,target:Target::None,
                            });
"""

CMD_OLD = """                let mut by_id=BTreeMap::new();
                for unit in my_units{
"""
CMD_NEW = """                let build=|extend:bool|->BTreeMap<i32,Vec<Candidate>>{
                GB_EXTEND.with(|flag|flag.set(extend));
                let mut by_id=BTreeMap::new();
                for unit in my_units.iter().copied(){
"""

DOOR_OLD = """                if self.door_unblocking{
                    self.force_unique_door_clear(view,&mut by_id);
                    }
"""
DOOR_NEW = """                if self.door_unblocking{
                    self.force_unique_door_clear(view,&mut by_id);
                    }
                GB_EXTEND.with(|flag|flag.set(false));
                by_id
                };
                GB_FALLBACK.with(|rec|rec.borrow_mut().clear());
                let by_id=build(false);
                let gb_rows:Vec<(i32,i32,String,String)> =GB_FALLBACK.with(|rec|rec.borrow_mut().drain(..).collect());
                for row in &gb_rows{
                    eprintln!("GBFALL turn={} unit={} carried={} out={} ret={}",view.turn,row.0,row.1,row.2,row.3);
                    }
                if gb_rows.iter().any(|row|row.1>0){
                    let by_id_cand=build(true);
                    GB_FALLBACK.with(|rec|rec.borrow_mut().clear());
                    for(id,list)in by_id.iter(){
                        let base_items=list%(DUMP)s;
                        let cand_items=by_id_cand.get(id).map(|l|l%(DUMP)s).unwrap_or_default();
                        eprintln!("GBLIST turn={} unit={} base={} cand={}",view.turn,id,base_items,cand_items);
                        }
                    let mut gb_map_base:BTreeMap<i32,Target> =BTreeMap::new();
                    let mut gb_sel_base=MoisanBot::select_recording(by_id.clone(),&view.inventories[0],&mut gb_map_base);
                    MoisanBot::resolve_move_conflicts(view,&mut gb_sel_base);
                    let mut gb_map_cand:BTreeMap<i32,Target> =BTreeMap::new();
                    let mut gb_sel_cand=MoisanBot::select_recording(by_id_cand,&view.inventories[0],&mut gb_map_cand);
                    MoisanBot::resolve_move_conflicts(view,&mut gb_sel_cand);
                    eprintln!("GBFORK turn={} base={} cand={} same={}",view.turn,gb_sel_base.join(";"),gb_sel_cand.join(";"),gb_sel_base==gb_sel_cand);
                    }
""" % {"DUMP": DUMP}


class ProbeError(RuntimeError):
    """Fail-closed refusal."""


def once(text: str, needle: str, what: str) -> None:
    n = text.count(needle)
    if n != 1:
        raise ProbeError("anchor %s matches %d times, expected exactly 1" % (what, n))


def fn_span(text: str, head: str, tail: str) -> tuple[int, int]:
    once(text, head, "fn-head " + head[:40])
    once(text, tail, "fn-tail " + tail[:40])
    a = text.index(head)
    b = text.index(tail)
    if b <= a:
        raise ProbeError("function tail precedes head")
    return a, b


def check_ruled_bodies() -> None:
    """The two arms must be the RULED Phase 3b bodies, not paraphrases of them.

    Checked against the Phase 3b probe builder's own constants, so there is one source for the
    ruled text: the incumbent body byte-identically, and the EXTEND body line-for-line after the
    four spaces of extra indentation the flag guard adds.
    """
    sys.path.insert(0, str(REPO / "claude_1" / "picker3"))
    import make_phase3b_probe as p3b                      # noqa: PLC0415

    if FALL_OLD != p3b.BASE_OLD:
        raise ProbeError("the incumbent body is not the ruled Phase 3b REPLACE body")
    ruled = p3b.CAND_OLD.splitlines()[1:-1]
    mine_block = FALL_NEW_TMPL.split("if GB_EXTEND.with(|flag|flag.get()){")[1]
    mine = [line for line in mine_block.split("%(POISON)s")[0].splitlines() if line.strip()]
    mine.append(mine_block.split("%(POISON)s")[1].splitlines()[0])
    if [line[4:] for line in mine] != ruled:
        raise ProbeError("the EXTEND arm is not the ruled Phase 3b body:\n%r\n%r"
                         % ([line[4:] for line in mine], ruled))


def build(poison: bool) -> str:
    check_ruled_bodies()
    src = SUBJECT.read_text(encoding="utf-8")
    got = hashlib.sha256(SUBJECT.read_bytes()).hexdigest()[:16]
    if got != SUBJECT_SHA:
        raise ProbeError("subject digest %s != pinned %s; a drifted subject is refused"
                         % (got, SUBJECT_SHA))
    once(src, REC_ANCHOR, "MoisanBot struct")
    once(src, FALL_OLD, "idle-regeneration fallback")
    once(src, CMD_OLD, "by_id loop head")
    once(src, DOOR_OLD, "door-unblocking block")
    fall_new = FALL_NEW_TMPL % {"DUMP": DUMP, "POISON": POISON if poison else ""}
    out = src.replace(REC_ANCHOR, REC_NEW)
    out = out.replace(FALL_OLD, fall_new)
    out = out.replace(CMD_OLD, CMD_NEW)
    out = out.replace(DOOR_OLD, DOOR_NEW)

    # Confinement: everything outside main_candidates and commands() is byte-identical, apart from
    # the one declared thread_local block.
    strip = out.replace(REC_NEW, REC_ANCHOR).replace(fall_new, FALL_OLD)
    strip = strip.replace(CMD_NEW, CMD_OLD).replace(DOOR_NEW, DOOR_OLD)
    if strip != src:
        raise ProbeError("probe differs from the subject outside the three declared edits")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--poison", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    text = build(args.poison)
    dest = Path(args.out) if args.out else (
        HERE / ("probe-gb-poison.rs" if args.poison else "probe-gb.rs"))
    dest.write_text(text, encoding="utf-8")
    print("%s  sha256=%s  subject_sha256=%s" % (
        dest, hashlib.sha256(text.encode()).hexdigest()[:16],
        hashlib.sha256(SUBJECT.read_bytes()).hexdigest()[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
