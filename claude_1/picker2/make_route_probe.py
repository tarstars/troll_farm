#!/usr/bin/env python3
r"""Phase 3 step 2 — a GENERATOR probe: which route returned the anchor's length-1 candidate list.

Step 1 (`idle_shape.py`) settled *what*: on every idle turn of all four ruled fixtures, on both
bases, the anchor's list is exactly ONE entry — the `WAIT` that `main_candidates` and
`endgame_candidates` seed it with. It is never empty. So the question is which return path handed
back the seed untouched, and what the generator saw when it did.

`make_probe.py` taps the SELECTOR. This taps the GENERATOR, one function further up, and it prints
only — every row is an `eprintln!`, and the parity gate re-checks that against the uninstrumented
binary's command stream, exactly as gate 1 does.

    PS3FINAL unit=<id> turn=<t> n=<len> endgame=<b> early=<b> committed=<b> train_now=<b>
    PS3MAIN  unit=<id> turn=<t> carried=<n> free_cap=<n> safe_regen=<b> idle_regen=<b>
    PS3ROUTE unit=<id> turn=<t> fn=<main|endgame> route=<NAME> <k>=<v> ...

`PS3FINAL` is emitted at `by_id.insert` — after the post-hoc idle-harvest, PICK-retain and
shack-nudge edits — so `n` is the list the selector actually receives, and it must equal the
length step 1 read off the selector's own `PS2CAND` rows. That equality is the cross-check that
the two probes are looking at the same list; the reader fails rather than reporting a route if it
breaks.

The route names are the source's own return paths, not a taxonomy I invented:

  main:     SAFE_REGEN_BANK  FULL_BANK  IDLE_REGEN_FALLBACK  NOCHOP_BANK  CHOPS
  endgame:  PLANT_SITES  CARRIED_FRUIT_BANK  CARRIED_BANK  CHOP_CURRENT  CONVERSION_TAIL
  early:    EARLY_CARRY_BANK  EARLY_CHOP_FALLBACK  EARLY_GATHER

`commands()` picks its generator from FIVE branches, not two: `committed_regeneration` and
`endgame` route to `endgame_candidates`, the default routes to `main_candidates`, and `early`
(`!opening_abandoned && my_units.len()<2 && !train_now`) routes to `early_candidates`. Phase 3's
fixtures never entered the early branch inside their audited windows, so its five anchors named
every route those fixtures took and the omission was invisible. On the OSC-032/033 fixtures it is
not invisible: turns 1-34 of BOTH games are `early=true`, and all 34 produce a `PS3FINAL` with no
`PS3ROUTE` at all. Those are exactly the turns that left OSC-033 unable to name a non-idle route
and cost the G-1 package its per-fixture both-ways control (codex_1 review, 2026-08-21).

`EARLY_EDITS` closes that hole. It is applied PER SUBJECT, via `EXTRA_EDITS`, and only to
`door1-champion`. Applying it to the two p1p2 subjects would rewrite the probes and manifest that
task `20260820-pair-selector-anti-benching` already published and had accepted; a later task must
not silently mutate an earlier task's artifacts. So a bare run still reproduces the Phase-3
manifest and both p1p2 probes byte-identically, and `anchors` in each manifest entry records the
set that subject was actually built with rather than a global that no longer describes it.

Guards, all fail-closed: the subject digest must be in the allowlist, and every anchor must match
EXACTLY once — an anchor that matches twice is refused rather than applied to a guess.

Run:  python3 claude_1/picker2/make_route_probe.py
"""
import argparse, hashlib, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

SUBJECTS = {
    "cureC-p1p2": (HERE / "candidate-cureC-p1p2.rs", "p1p2",
                   "d127cf861ad7f145e5693b0a595bcc8e3c870f424926b18bdbb3debec80b0412"),
    "door1-p1p2": (HERE / "candidate-door1-p1p2.rs", "p1p2",
                   "5e1f4df406480f678ff03677cdda0f69d510c5c94efe90d4f0a8231b70c3339e"),
    # The champion of record (Door-1 pure deletion, KEPT by the owner 2026-08-21)
    # with NO selector work on top. Added for task
    # 20260821-osc032-033-no-goal-instrument, whose charter is explicit that the
    # Phase-3 probes are to be pointed at new fixtures rather than reinvented.
    # All five anchors match it exactly once, unmodified — the same fail-closed
    # guard below proves that on every run.
    "door1-champion": (REPO / "claude_1/chop4c/candidate-door1.rs", "base",
                       "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"),
}
OUT_MANIFEST = HERE / "route-probe-manifest-2026-08-20.json"
# A bare run must keep reproducing the Phase-3 manifest BYTE-IDENTICALLY, so
# the champion subject is opt-in via --subject. Building it by default
# rewrites another task's published artifact, which I did once and reverted.
DEFAULT_SUBJECTS = ("cureC-p1p2", "door1-p1p2")

# ---- commands(): the list the selector actually receives, plus the branch predicates ----------
FINAL_OLD = '''                    by_id.insert(unit.id,candidates);'''
FINAL_NEW = '''                    eprintln!("PS3FINAL unit={} turn={} n={} endgame={} early={} committed={} train_now={}",unit.id,view.turn,candidates.len(),endgame,early,committed_regeneration,train_now);
                    by_id.insert(unit.id,candidates);'''

# ---- main_candidates ---------------------------------------------------------------------------
MAIN_ENTRY_OLD = '''                let mut out=vec![MoisanBot::wait()];
                let carried=unit.total_carried();
                if safe_regeneration&&Self::carried_fruit(unit).is_some(){
                    out.extend(Self::bank_candidates(view,unit));
                    return out;
                    }'''
MAIN_ENTRY_NEW = '''                let mut out=vec![MoisanBot::wait()];
                let carried=unit.total_carried();
                eprintln!("PS3MAIN unit={} turn={} carried={} free_cap={} safe_regen={} idle_regen={}",unit.id,view.turn,carried,unit.free_capacity(),safe_regeneration,idle_regeneration);
                if safe_regeneration&&Self::carried_fruit(unit).is_some(){
                    let ps3_bank=Self::bank_candidates(view,unit);
                    eprintln!("PS3ROUTE unit={} turn={} fn=main route=SAFE_REGEN_BANK bank={}",unit.id,view.turn,ps3_bank.len());
                    out.extend(ps3_bank);
                    return out;
                    }'''

MAIN_TAIL_OLD = '''                if unit.free_capacity()<=0{
                    out.extend(Self::bank_candidates(view,unit));
                    return out;
                    }
                let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    fallback.extend(Self::idle_harvest_candidates(view,unit));
                    if unit.total_carried()>0{
                        fallback.extend(Self::bank_candidates(view,unit));
                        }
                    return fallback;
                    }
                if chops.is_empty()&&carried>0{
                    out.extend(Self::bank_candidates(view,unit));
                    }
                else{
                    out.extend(chops);
                    }
                out'''
MAIN_TAIL_NEW = '''                if unit.free_capacity()<=0{
                    let ps3_bank=Self::bank_candidates(view,unit);
                    eprintln!("PS3ROUTE unit={} turn={} fn=main route=FULL_BANK bank={}",unit.id,view.turn,ps3_bank.len());
                    out.extend(ps3_bank);
                    return out;
                    }
                let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
                let ps3_nchops=chops.len();
                if idle_regeneration&&chops.is_empty(){
                    let mut fallback=vec![MoisanBot::wait()];
                    let ps3_idle=Self::idle_harvest_candidates(view,unit);
                    let ps3_nidle=ps3_idle.len();
                    fallback.extend(ps3_idle);
                    for ps3_c in out.iter().filter(|ps3_c|ps3_c.command!="WAIT"){
                        eprintln!("PS3DISCARD unit={} turn={} verb={} target={:?} score={:.6}",unit.id,view.turn,ps3_c.command.split(' ').next().unwrap_or("?"),ps3_c.target,ps3_c.score);
                        }
                    let mut ps3_nbank=0usize;
                    if unit.total_carried()>0{
                        let ps3_bank=Self::bank_candidates(view,unit);
                        ps3_nbank=ps3_bank.len();
                        fallback.extend(ps3_bank);
                        }
                    eprintln!("PS3ROUTE unit={} turn={} fn=main route=IDLE_REGEN_FALLBACK chops=0 idle_harvest={} bank={} n={} discarded={} discarded_real={}",unit.id,view.turn,ps3_nidle,ps3_nbank,fallback.len(),out.len(),out.iter().filter(|ps3_c|ps3_c.command!="WAIT").count());
                    return fallback;
                    }
                if chops.is_empty()&&carried>0{
                    let ps3_bank=Self::bank_candidates(view,unit);
                    eprintln!("PS3ROUTE unit={} turn={} fn=main route=NOCHOP_BANK chops=0 bank={}",unit.id,view.turn,ps3_bank.len());
                    out.extend(ps3_bank);
                    }
                else{
                    out.extend(chops);
                    eprintln!("PS3ROUTE unit={} turn={} fn=main route=CHOPS chops={} n={}",unit.id,view.turn,ps3_nchops,out.len());
                    }
                out'''

# ---- endgame_candidates -------------------------------------------------------------------------
EG_FRUIT_OLD = '''                    if out.len()>1{
                        return out;
                        }
                    out.extend(Self::bank_candidates(view,unit));
                    return out;
                    }
                if unit.total_carried()>0{
                    out.extend(Self::bank_candidates(view,unit));
                    return out;
                    }
                let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
                if let Some(mut current)=chops.iter().find(|candidate|candidate.command==format!("CHOP {}",unit.id)).cloned(){
                    current.score=10_000.0;
                    out.push(current);
                    return out;
                    }'''
EG_FRUIT_NEW = '''                    if out.len()>1{
                        eprintln!("PS3ROUTE unit={} turn={} fn=endgame route=PLANT_SITES n={}",unit.id,view.turn,out.len());
                        return out;
                        }
                    let ps3_bank=Self::bank_candidates(view,unit);
                    eprintln!("PS3ROUTE unit={} turn={} fn=endgame route=CARRIED_FRUIT_BANK bank={}",unit.id,view.turn,ps3_bank.len());
                    out.extend(ps3_bank);
                    return out;
                    }
                if unit.total_carried()>0{
                    let ps3_bank=Self::bank_candidates(view,unit);
                    eprintln!("PS3ROUTE unit={} turn={} fn=endgame route=CARRIED_BANK bank={}",unit.id,view.turn,ps3_bank.len());
                    out.extend(ps3_bank);
                    return out;
                    }
                let chops=Self::yamo_chop_candidates(view,unit,type_to_cut,opponent_eta_penalty,);
                let ps3_nchops=chops.len();
                if let Some(mut current)=chops.iter().find(|candidate|candidate.command==format!("CHOP {}",unit.id)).cloned(){
                    current.score=10_000.0;
                    out.push(current);
                    eprintln!("PS3ROUTE unit={} turn={} fn=endgame route=CHOP_CURRENT chops={} n={}",unit.id,view.turn,ps3_nchops,out.len());
                    return out;
                    }'''

EG_TAIL_OLD = '''                out.extend(chops);
                out
            }
            fn idle_harvest_candidates'''
EG_TAIL_NEW = '''                out.extend(chops);
                eprintln!("PS3ROUTE unit={} turn={} fn=endgame route=CONVERSION_TAIL chops={} n={}",unit.id,view.turn,ps3_nchops,out.len());
                out
            }
            fn idle_harvest_candidates'''

# ---- early_candidates: the fifth generator branch in commands(), untapped by Phase 3 ----------
EARLY_ENTRY_OLD = """            fn early_candidates(view:&GameState,unit:&Unit,desired:Stats)->Vec<Candidate>{
                let mut out=vec![Self::wait()];
                if Self::carrying_any(unit)||unit.free_capacity()<=0{
                    out.extend(Self::bank_candidates(view,unit));
                    return out;
                    }"""
EARLY_ENTRY_NEW = """            fn early_candidates(view:&GameState,unit:&Unit,desired:Stats)->Vec<Candidate>{
                let mut out=vec![Self::wait()];
                if Self::carrying_any(unit)||unit.free_capacity()<=0{
                    let ps3_bank=Self::bank_candidates(view,unit);
                    eprintln!("PS3ROUTE unit={} turn={} fn=early route=EARLY_CARRY_BANK bank={} n={}",unit.id,view.turn,ps3_bank.len(),out.len()+ps3_bank.len());
                    out.extend(ps3_bank);
                    return out;
                    }"""

EARLY_TAIL_OLD = """                if out.len()==1{
                    out.extend(Self::chop_candidates(view,unit,None));
                    }
                out
            }
            fn fruit_candidates"""
EARLY_TAIL_NEW = """                if out.len()==1{
                    let ps3_chops=Self::chop_candidates(view,unit,None);
                    eprintln!("PS3ROUTE unit={} turn={} fn=early route=EARLY_CHOP_FALLBACK chops={} n={}",unit.id,view.turn,ps3_chops.len(),out.len()+ps3_chops.len());
                    out.extend(ps3_chops);
                    }
                else{
                    eprintln!("PS3ROUTE unit={} turn={} fn=early route=EARLY_GATHER n={}",unit.id,view.turn,out.len());
                    }
                out
            }
            fn fruit_candidates"""

EARLY_EDITS = [("early_candidates/entry", EARLY_ENTRY_OLD, EARLY_ENTRY_NEW),
               ("early_candidates/tail", EARLY_TAIL_OLD, EARLY_TAIL_NEW)]

# Per-subject additions. The five EDITS above are the accepted Phase-3 set and are applied to
# EVERY subject unchanged; only the champion gets the early anchors on top. See the module
# docstring for why this is per-subject rather than global.
EXTRA_EDITS = {"door1-champion": EARLY_EDITS}

EDITS = [("commands/by_id.insert", FINAL_OLD, FINAL_NEW),
         ("main_candidates/entry", MAIN_ENTRY_OLD, MAIN_ENTRY_NEW),
         ("main_candidates/tail", MAIN_TAIL_OLD, MAIN_TAIL_NEW),
         ("endgame_candidates/fruit+chop", EG_FRUIT_OLD, EG_FRUIT_NEW),
         ("endgame_candidates/tail", EG_TAIL_OLD, EG_TAIL_NEW)]


class BuildError(Exception):
    """An anchor that does not match exactly once. Refused, never guessed at."""


def build(name, path, arm, want_digest):
    src = path.read_text()
    got = hashlib.sha256(src.encode()).hexdigest()
    if got != want_digest:
        raise BuildError(f"{name}: digest {got} is not the allowlisted {want_digest}. The subject "
                         f"moved under the probe; refusing to instrument an unknown source.")
    edits = EDITS + EXTRA_EDITS.get(name, [])
    for label, old, new in edits:
        n = src.count(old)
        if n != 1:
            raise BuildError(f"{name}: anchor {label!r} matched {n} times, need exactly 1.")
        src = src.replace(old, new)
    out = HERE / f"routeprobe-{name}.rs"
    out.write_text(src)
    return {"name": name, "arm": arm, "source": str(path.relative_to(REPO)),
            "source_sha256": want_digest, "probe": str(out.relative_to(REPO)),
            "probe_sha256": hashlib.sha256(src.encode()).hexdigest(),
            "anchors": [l for l, _, _ in edits]}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--subject", action="append", default=[], metavar="NAME",
                    help="build only this subject; repeatable (default: all)")
    ap.add_argument("--manifest", default=str(OUT_MANIFEST), metavar="PATH",
                    help="where to write the manifest (default: the Phase-3 one)")
    args = ap.parse_args()
    wanted = args.subject or list(DEFAULT_SUBJECTS)
    unknown = [n for n in wanted if n not in SUBJECTS]
    if unknown:
        raise BuildError(f"unknown subject(s) {unknown!r}; known: {sorted(SUBJECTS)!r}")
    man = {}
    for name in wanted:
        path, arm, digest = SUBJECTS[name]
        man[name] = build(name, path, arm, digest)
        print(f"  built {man[name]['probe']}  "
              f"({len(man[name]['anchors'])} anchors, each matched once)")
    manifest = Path(args.manifest)
    manifest.write_text(json.dumps(man, indent=2, sort_keys=True) + "\n")
    print(f"wrote {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
