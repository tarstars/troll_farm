#!/usr/bin/env python3
r"""Phase 3b REACH on real games — build the dual-arm probe from the source that PLAYED them.

## The question this probe exists to answer

`local_claude_1`'s RULING (`20260823T131400Z`, `20260820-pair-selector-anti-benching`) charters
one targeted comparison and nothing else:

    on how many of the 2,903 nothing/nothing turns would the un-discarded options have given the
    troll something real to do?

NARRATE v3 measured, on 160 real ladder games of agent `6652642`, a joint table that sums exactly:
81,410 real/real, **2,903 nothing/nothing**, 615 nothing/real.  v3's `available` is computed from
the list that SURVIVES the idle-regeneration discard, so a troll robbed by the Phase 3b bug lands
in the 2,903, not in the 615.  This probe re-executes the same bot over the same states with the
ruled EXTEND body behind a flag and reads both arms' `available` and `chosen` per unit per turn.

## Subject

`claude_1/narrate3/instrument-swap-r1-narrate-v3.rs` — the NARRATE v3 instrument, sha256
`9a3e8758...`, byte-identical to the source submitted as `41182608` (agent `6652642`) that played
these 160 games.  Its idle-regeneration fallback is BYTE-IDENTICAL to the Phase 3b incumbent
(REPLACE) body, checked here against the Phase 3b probe builder's own constants, so the states
this bot naturally reached are exactly the states the ruling asks about.

## Emitted rows (the probe prints, the analyser classifies)

    RCHFALL turn=<t> unit=<id> carried=<n> out=<items> ret=<items>
    RCHROW  turn=<t> unit=<id> bavail=<target> bchosen=<target> cavail=<target> cchosen=<target>
    RCHSEL  turn=<t> base=<cmds> cand=<cmds> same=<bool>

`RCHROW` is emitted for **every live own unit on every turn**, from both arms over the identical
state.  `bavail`/`bchosen` are the base arm's `narrate_available` and `select_recording` reads —
the same two functions the live instrument used, so the base arm must REPRODUCE the telemetry
actually recorded on the wire.  That identity check is the control that makes the `c*` columns
worth reading.  `cavail`/`cchosen` are the same two reads on the EXTEND arm.

`--poison` builds the control arm: the EXTEND body additionally appends one candidate the REPLACE
body cannot produce.  On that arm the reach count MUST move and `RCHSEL same=false` MUST appear,
or the fork is inert.  `--null` builds the opposite control: the flag is read at the same site but
both bodies are the incumbent, so the reach count MUST be zero and every `RCHSEL` MUST say
`same=true`.  A measurement that cannot produce zero on a null fork is manufacturing differences.

Guards, all fail-closed: the subject digest is pinned; every anchor must match exactly once; the
two ruled bodies are checked against `make_phase3b_probe`'s constants rather than hand-copied; and
everything outside the four declared edits must be byte-identical to the subject.

Nothing here grades Phase 3b, claims progress, opens a gate, or takes any Arena action.

Run:  python3 claude_1/reach1/make_reach_probe.py [--poison|--null] [--out PATH]
"""
from __future__ import annotations

import argparse, hashlib, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SUBJECT = REPO / "claude_1" / "narrate3" / "instrument-swap-r1-narrate-v3.rs"
SUBJECT_SHA = "9a3e875823f3fc26"   # sha256 prefix of the source that played the 160 games

DUMP = ('.iter().map(|c|format!("{}|{:.6}|{:?}",c.command,c.score,c.target))'
        '.collect::<Vec<_>>().join("~")')

REC_ANCHOR = "        struct MoisanBot;\n"
REC_NEW = """        thread_local!{
            pub static RCH_FALLBACK:std::cell::RefCell<Vec<(i32,i32,String,String)>> =std::cell::RefCell::new(Vec::new());
            pub static RCH_EXTEND:std::cell::Cell<bool> =std::cell::Cell::new(false);
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

# The EXTEND body is the ruled Phase 3b snippet, verbatim.  POISON adds one candidate the REPLACE
# arm cannot produce.  NULL replaces the whole guarded body with the incumbent's, so the flag is
# read at the identical site and the arms are the same bot.
FALL_NEW_TMPL = """                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    RCH_FALLBACK.with(|rec|rec.borrow_mut().push((unit.id,unit.total_carried(),
                        out%(DUMP)s,fallback%(DUMP)s)));
                    if RCH_EXTEND.with(|flag|flag.get()){
%(ARM)s                        }
                    return fallback;
                    }
"""

ARM_HONEST = """                        out.extend(Self::idle_harvest_candidates(view,unit));
                        if unit.total_carried()>0{
                            out.extend(Self::bank_candidates(view,unit));
                            }
                        return out;
"""

ARM_POISON = """                        out.extend(Self::idle_harvest_candidates(view,unit));
                        if unit.total_carried()>0{
                            out.extend(Self::bank_candidates(view,unit));
                            }
                        out.push(Candidate{
                            command:format!("MOVE {} {} {}",unit.id,view.shacks[0].0,view.shacks[0].1),score:99999.0,target:Target::Cell(view.shacks[0]),
                            });
                        return out;
"""

ARM_NULL = """                        return fallback;
"""

CMD_OLD = """                let mut by_id=BTreeMap::new();
                for unit in my_units{
"""
CMD_NEW = """                let build=|extend:bool|->BTreeMap<i32,Vec<Candidate>>{
                RCH_EXTEND.with(|flag|flag.set(extend));
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
                RCH_EXTEND.with(|flag|flag.set(false));
                by_id
                };
                RCH_FALLBACK.with(|rec|rec.borrow_mut().clear());
                let by_id=build(false);
                for row in RCH_FALLBACK.with(|rec|rec.borrow_mut().drain(..).collect::<Vec<_>>()){
                    eprintln!("RCHFALL turn={} unit={} carried={} out={} ret={}",view.turn,row.0,row.1,row.2,row.3);
                    }
                let by_id_cand=build(true);
                RCH_FALLBACK.with(|rec|rec.borrow_mut().clear());
                {
                    let rch_av_base=Self::narrate_available(&by_id);
                    let rch_av_cand=Self::narrate_available(&by_id_cand);
                    let mut rch_ch_base:BTreeMap<i32,Target> =BTreeMap::new();
                    let mut rch_sel_base=MoisanBot::select_recording(by_id.clone(),&view.inventories[0],&mut rch_ch_base);
                    MoisanBot::resolve_move_conflicts(view,&mut rch_sel_base);
                    let mut rch_ch_cand:BTreeMap<i32,Target> =BTreeMap::new();
                    let mut rch_sel_cand=MoisanBot::select_recording(by_id_cand,&view.inventories[0],&mut rch_ch_cand);
                    MoisanBot::resolve_move_conflicts(view,&mut rch_sel_cand);
                    let mut rch_ids:Vec<i32> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.id).collect();
                    rch_ids.sort();
                    for id in rch_ids{
                        let bavail=match rch_av_base.get(&id).copied().flatten(){
                            Some(target)=>Self::narrate_target(target),None=>"ABSENT".to_string(),
                        };
                        let cavail=match rch_av_cand.get(&id).copied().flatten(){
                            Some(target)=>Self::narrate_target(target),None=>"ABSENT".to_string(),
                        };
                        let bchosen=Self::narrate_target(rch_ch_base.get(&id).copied().unwrap_or(Target::None));
                        let cchosen=Self::narrate_target(rch_ch_cand.get(&id).copied().unwrap_or(Target::None));
                        eprintln!("RCHROW turn={} unit={} bavail={} bchosen={} cavail={} cchosen={}",view.turn,id,bavail,bchosen,cavail,cchosen);
                        }
                    eprintln!("RCHSEL turn={} base={} cand={} same={}",view.turn,rch_sel_base.join(";"),rch_sel_cand.join(";"),rch_sel_base==rch_sel_cand);
                    }
"""


class ProbeError(RuntimeError):
    """Fail-closed refusal."""


def once(text: str, needle: str, what: str) -> None:
    n = text.count(needle)
    if n != 1:
        raise ProbeError("anchor %s matches %d times, expected exactly 1" % (what, n))


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
    mine = [line[4:] for line in ARM_HONEST.splitlines()]
    if mine != ruled:
        raise ProbeError("the EXTEND arm is not the ruled Phase 3b body:\n%r\n%r" % (mine, ruled))


def build(arm: str) -> str:
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
    body = {"honest": ARM_HONEST, "poison": ARM_POISON, "null": ARM_NULL}[arm]
    fall_new = FALL_NEW_TMPL % {"DUMP": DUMP, "ARM": body}
    out = src.replace(REC_ANCHOR, REC_NEW)
    out = out.replace(FALL_OLD, fall_new)
    out = out.replace(CMD_OLD, CMD_NEW)
    out = out.replace(DOOR_OLD, DOOR_NEW)

    # Confinement: everything outside main_candidates and commands() is byte-identical, apart from
    # the one declared thread_local block.
    strip = out.replace(REC_NEW, REC_ANCHOR).replace(fall_new, FALL_OLD)
    strip = strip.replace(CMD_NEW, CMD_OLD).replace(DOOR_NEW, DOOR_OLD)
    if strip != src:
        raise ProbeError("probe differs from the subject outside the four declared edits")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--poison", action="store_true")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    if args.poison and args.null:
        raise SystemExit("--poison and --null are exclusive")
    arm = "poison" if args.poison else "null" if args.null else "honest"
    text = build(arm)
    dest = Path(args.out) if args.out else (HERE / ("probe-reach-%s.rs" % arm))
    dest.write_text(text, encoding="utf-8")
    print("%s  arm=%s  sha256=%s  subject_sha256=%s" % (
        dest, arm, hashlib.sha256(text.encode()).hexdigest()[:16],
        hashlib.sha256(SUBJECT.read_bytes()).hexdigest()[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
