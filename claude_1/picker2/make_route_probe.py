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
    # The SAME champion source with the seven accepted anchors PLUS the clause tap, for task
    # 20260821-osc032-033-cause-attribution. It is a separate subject name rather than a flag on
    # `door1-champion` for exactly the reason the early anchors are per-subject: the predecessor
    # task published `routeprobe-door1-champion.rs` and its manifest and had them accepted, and a
    # later task must not mutate an earlier task's artifacts. With the new anchors "off" — i.e.
    # building `door1-champion` — the accepted probe and manifest reproduce byte-identically, and
    # `main --check-accepted` proves that rather than asserting it.
    "door1-clause": (REPO / "claude_1/chop4c/candidate-door1.rs", "base",
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

# ---- CLAUSE TAP (task 20260821-osc032-033-cause-attribution) ------------------------------------
# Champion-only, opt-in through a SEPARATE subject name (`door1-clause`) so the accepted
# `door1-champion` probe and its manifest keep reproducing byte-identically. Every edit below
# either splits a `||` guard into its two named halves, or turns an iterator chain into the same
# loop; no predicate is added, removed or reordered, and every row is an `eprintln!` that the
# parity gate re-checks against the uninstrumented champion's command stream.
#
# The contract the reader enforces (fail-closed): for one unit on one turn, a call to
# `chop_candidates` emits exactly ONE `PS4CHOPFN` row, and — when that row is `ENTERED` — exactly
# ONE `PS4CHOP` row per entry of `view.plants`, whose `clause` is the source's own rejecting
# condition or `ACCEPTED`. Same shape for `PS4HARVFN`/`PS4HARV`. A plant with no row, two rows,
# or a row on a call that never entered, fails the run instead of being reported.

CHOP_FN_OLD = '''            fn chop_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,)->Vec<Candidate>{
                let mut out=Vec::new();
                if unit.stats.chop_power<=0||unit.free_capacity()<=0{
                    return out;
                    }'''
# The canonical plant-state token, emitted on EVERY function row of both taps. `PS4STATE` is one
# `|`-joined record per entry of `view.plants`, in the source's own iteration order:
#   <x>,<y>:<KIND>:h<health>:s<size>:f<fruits>:cd<cooldown>
# It exists because equal plant COUNTS never established that the referee-side trace and the
# bot-side tap were looking at the same trees in the same state, and without that the oracle's
# eligible set and the generator's clause are two sentences about two different boards.
PS4_STATE_LET = '''                let ps4_recs:Vec<String> =view.plants.iter().map(|ps4_p|format!("{},{}:{}:h{}:s{}:f{}:cd{}",ps4_p.cell.0,ps4_p.cell.1,ps4_p.kind.as_str(),ps4_p.health,ps4_p.size,ps4_p.fruits,ps4_p.cooldown)).collect();
                let ps4_state=if ps4_recs.is_empty(){
                    "none".to_string()
                }
                else{
                    ps4_recs.join("|")
                }
                ;
'''

CHOP_FN_NEW = '''            fn chop_candidates(view:&GameState,unit:&Unit,type_to_cut:Option<PlantKind>,)->Vec<Candidate>{
                let mut out=Vec::new();
''' + PS4_STATE_LET + '''                if unit.stats.chop_power<=0{
                    eprintln!("PS4CHOPFN unit={} turn={} clause=FN_NO_CHOP_POWER chop_power={} free_cap={} plants={} unit_cell={},{} state={}",unit.id,view.turn,unit.stats.chop_power,unit.free_capacity(),view.plants.len(),unit.cell.0,unit.cell.1,ps4_state);
                    return out;
                    }
                if unit.free_capacity()<=0{
                    eprintln!("PS4CHOPFN unit={} turn={} clause=FN_NO_FREE_CAPACITY chop_power={} free_cap={} plants={} unit_cell={},{} state={}",unit.id,view.turn,unit.stats.chop_power,unit.free_capacity(),view.plants.len(),unit.cell.0,unit.cell.1,ps4_state);
                    return out;
                    }
                eprintln!("PS4CHOPFN unit={} turn={} clause=ENTERED chop_power={} free_cap={} plants={} unit_cell={},{} state={}",unit.id,view.turn,unit.stats.chop_power,unit.free_capacity(),view.plants.len(),unit.cell.0,unit.cell.1,ps4_state);'''

CHOP_LOOP_OLD = '''                for plant in&view.plants{
                    if plant.health<=0||!from_unit.contains_key(&plant.cell){
                        continue;
                        }
                    let travel_turns=Self::ceil_div(from_unit[&plant.cell],unit.stats.movement_speed);
                    let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{
                        continue;
                        }
                    ;
                    if predicted.size<=0||predicted.health<=0{
                        continue;
                        }
                    let return_turns=to_shack.get(&plant.cell).map(|d|Self::ceil_div(*d,unit.stats.movement_speed)).unwrap_or_else(||{
                        Self::ceil_div(manhattan(plant.cell,view.shacks[0]),unit.stats.movement_speed,)
                    }
                    );
                    let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{
                        continue;
                        }
                    ;
                    let turns=(travel_turns+chop_turns+return_turns+1).max(1);
                    if turns>TOTAL_TURNS-view.turn+1{
                        continue;
                        }
                    let wood=final_size.min(unit.free_capacity());
                    if wood<=0{
                        continue;
                        }'''
CHOP_LOOP_NEW = '''                for plant in&view.plants{
                    if plant.health<=0{
                        eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=PLANT_DEAD health={} size={} fruits={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),plant.health,plant.size,plant.fruits);
                        continue;
                        }
                    if !from_unit.contains_key(&plant.cell){
                        eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=UNREACHABLE_FROM_UNIT health={} size={} fruits={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),plant.health,plant.size,plant.fruits);
                        continue;
                        }
                    let travel_turns=Self::ceil_div(from_unit[&plant.cell],unit.stats.movement_speed);
                    let Some(predicted)=Self::predict_tree(view,plant,travel_turns)else{
                        eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=PREDICT_TREE_NONE travel={} opp_chop={} health={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),travel_turns,Self::predicted_opp_chop(view,plant),plant.health);
                        continue;
                        }
                    ;
                    if predicted.size<=0{
                        eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=PREDICTED_SIZE_NONPOSITIVE travel={} pred_size={} pred_health={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),travel_turns,predicted.size,predicted.health);
                        continue;
                        }
                    if predicted.health<=0{
                        eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=PREDICTED_HEALTH_NONPOSITIVE travel={} pred_size={} pred_health={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),travel_turns,predicted.size,predicted.health);
                        continue;
                        }
                    let return_turns=to_shack.get(&plant.cell).map(|d|Self::ceil_div(*d,unit.stats.movement_speed)).unwrap_or_else(||{
                        Self::ceil_div(manhattan(plant.cell,view.shacks[0]),unit.stats.movement_speed,)
                    }
                    );
                    let Some((chop_turns,final_size))=Self::chop_outcome(view,plant,predicted,unit.stats.chop_power)else{
                        eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=CHOP_OUTCOME_NONE travel={} pred_size={} pred_health={} chop_power={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),travel_turns,predicted.size,predicted.health,unit.stats.chop_power);
                        continue;
                        }
                    ;
                    let turns=(travel_turns+chop_turns+return_turns+1).max(1);
                    if turns>TOTAL_TURNS-view.turn+1{
                        eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=TRIP_LONGER_THAN_GAME trip={} turns_left={} travel={} chop_turns={} return={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),turns,TOTAL_TURNS-view.turn+1,travel_turns,chop_turns,return_turns);
                        continue;
                        }
                    let wood=final_size.min(unit.free_capacity());
                    if wood<=0{
                        eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=WOOD_NONPOSITIVE final_size={} free_cap={} trip={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),final_size,unit.free_capacity(),turns);
                        continue;
                        }
                    eprintln!("PS4CHOP unit={} turn={} plant={},{} kind={} clause=ACCEPTED wood={} trip={} travel={} chop_turns={} return={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),wood,turns,travel_turns,chop_turns,return_turns);'''

# The RETURNED LIST, read off `out` itself after the loop rather than off the loop's control
# flow. This is what makes the accepted side a per-plant measurement: `chops=` cardinality can
# survive while acceptance is attached to the wrong cell, so the reader joins the ordered target
# cells of the vector the generator actually returns against the ordered cells of its own
# `clause=ACCEPTED` rows. A pushed candidate with no ACCEPTED row, an ACCEPTED row on a plant that
# was never pushed, or the same count on different cells, all fail the run.
CHOP_TAIL_OLD = '''                    out.push(Candidate{
                        command,score,target:Target::Tree(plant.cell),
                    }
                    );
                    }
                out
            }'''
CHOP_TAIL_NEW = '''                    out.push(Candidate{
                        command,score,target:Target::Tree(plant.cell),
                    }
                    );
                    }
                for(ps4_i,ps4_c)in out.iter().enumerate(){
                    let ps4_t=match ps4_c.target{
                        Target::Tree(ps4_cell)=>format!("{},{}",ps4_cell.0,ps4_cell.1),_=>"NOT_A_TREE".to_string(),
                    }
                    ;
                    eprintln!("PS4CHOPOUT unit={} turn={} i={} target={} command={}",unit.id,view.turn,ps4_i,ps4_t,ps4_c.command.replace(' ',"_"));
                    }
                eprintln!("PS4CHOPLIST unit={} turn={} returned={}",unit.id,view.turn,out.len());
                out
            }'''

HARV_OLD = '''            fn idle_harvest_candidates(view:&GameState,unit:&Unit,)->Vec<Candidate>{
                if unit.total_carried()!=0||unit.stats.harvest_power<=0{
                    return Vec::new();
                    }
                let from_unit=bfs_distances(&view.walkable,&[unit.cell]);
                let shack_starts:Vec<Cell> =ortho_neighbors(view.shacks[0]).into_iter().filter(|cell|view.walkable.contains(cell)).collect();
                let to_shack=bfs_distances(&view.walkable,&shack_starts);
                let turns_left=TOTAL_TURNS-view.turn+1;
                view.plants.iter().filter(|plant|{
                    plant.health>0&&plant.fruits>0&&(unit.cell==plant.cell||!view.units.iter().any(|other|{
                        other.player==1&&other.cell==plant.cell&&other.total_carried()==0
                    }
                    ))&&from_unit.contains_key(&plant.cell)&&to_shack.contains_key(&plant.cell)
                }
                ).filter_map(|plant|{
                    let travel=MoisanBot::ceil_div(from_unit[&plant.cell],unit.stats.movement_speed);
                    let home=MoisanBot::ceil_div(to_shack[&plant.cell],unit.stats.movement_speed);
                    let trip=travel+1+home+1;
                    (trip<=turns_left).then(||Candidate{
                        command:if unit.cell==plant.cell{
                            format!("HARVEST {}",unit.id)
                        }
                        else{
                            format!("MOVE {} {} {}",unit.id,plant.cell.0,plant.cell.1)
                        }
                        ,score:1.0/trip.max(1)as f64,target:Target::Tree(plant.cell),
                    }
                    )
                }
                ).collect()
            }'''
HARV_NEW = '''            fn idle_harvest_candidates(view:&GameState,unit:&Unit,)->Vec<Candidate>{
''' + PS4_STATE_LET + '''                if unit.total_carried()!=0{
                    eprintln!("PS4HARVFN unit={} turn={} clause=FN_CARRYING carried={} harvest_power={} plants={} unit_cell={},{} state={}",unit.id,view.turn,unit.total_carried(),unit.stats.harvest_power,view.plants.len(),unit.cell.0,unit.cell.1,ps4_state);
                    return Vec::new();
                    }
                if unit.stats.harvest_power<=0{
                    eprintln!("PS4HARVFN unit={} turn={} clause=FN_NO_HARVEST_POWER carried=0 harvest_power={} plants={} unit_cell={},{} state={}",unit.id,view.turn,unit.stats.harvest_power,view.plants.len(),unit.cell.0,unit.cell.1,ps4_state);
                    return Vec::new();
                    }
                eprintln!("PS4HARVFN unit={} turn={} clause=ENTERED carried=0 harvest_power={} plants={} unit_cell={},{} state={}",unit.id,view.turn,unit.stats.harvest_power,view.plants.len(),unit.cell.0,unit.cell.1,ps4_state);
                let from_unit=bfs_distances(&view.walkable,&[unit.cell]);
                let shack_starts:Vec<Cell> =ortho_neighbors(view.shacks[0]).into_iter().filter(|cell|view.walkable.contains(cell)).collect();
                let to_shack=bfs_distances(&view.walkable,&shack_starts);
                let turns_left=TOTAL_TURNS-view.turn+1;
                let mut ps4_out:Vec<Candidate> =Vec::new();
                for plant in view.plants.iter(){
                    if !(plant.health>0){
                        eprintln!("PS4HARV unit={} turn={} plant={},{} kind={} clause=PLANT_DEAD health={} fruits={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),plant.health,plant.fruits);
                        continue;
                        }
                    if !(plant.fruits>0){
                        eprintln!("PS4HARV unit={} turn={} plant={},{} kind={} clause=NO_FRUITS health={} fruits={} cooldown={} size={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),plant.health,plant.fruits,plant.cooldown,plant.size);
                        continue;
                        }
                    if !(unit.cell==plant.cell||!view.units.iter().any(|other|{
                        other.player==1&&other.cell==plant.cell&&other.total_carried()==0
                    }
                    )){
                        eprintln!("PS4HARV unit={} turn={} plant={},{} kind={} clause=OPPONENT_EMPTY_HANDED_ON_CELL health={} fruits={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),plant.health,plant.fruits);
                        continue;
                        }
                    if !from_unit.contains_key(&plant.cell){
                        eprintln!("PS4HARV unit={} turn={} plant={},{} kind={} clause=UNREACHABLE_FROM_UNIT health={} fruits={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),plant.health,plant.fruits);
                        continue;
                        }
                    if !to_shack.contains_key(&plant.cell){
                        eprintln!("PS4HARV unit={} turn={} plant={},{} kind={} clause=NO_PATH_TO_SHACK_DOOR health={} fruits={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),plant.health,plant.fruits);
                        continue;
                        }
                    let travel=MoisanBot::ceil_div(from_unit[&plant.cell],unit.stats.movement_speed);
                    let home=MoisanBot::ceil_div(to_shack[&plant.cell],unit.stats.movement_speed);
                    let trip=travel+1+home+1;
                    if !(trip<=turns_left){
                        eprintln!("PS4HARV unit={} turn={} plant={},{} kind={} clause=TRIP_LONGER_THAN_GAME trip={} turns_left={} travel={} home={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),trip,turns_left,travel,home);
                        continue;
                        }
                    eprintln!("PS4HARV unit={} turn={} plant={},{} kind={} clause=ACCEPTED trip={} turns_left={} travel={} home={} fruits={}",unit.id,view.turn,plant.cell.0,plant.cell.1,plant.kind.as_str(),trip,turns_left,travel,home,plant.fruits);
                    ps4_out.push(Candidate{
                        command:if unit.cell==plant.cell{
                            format!("HARVEST {}",unit.id)
                        }
                        else{
                            format!("MOVE {} {} {}",unit.id,plant.cell.0,plant.cell.1)
                        }
                        ,score:1.0/trip.max(1)as f64,target:Target::Tree(plant.cell),
                    }
                    );
                    }
                for(ps4_i,ps4_c)in ps4_out.iter().enumerate(){
                    let ps4_t=match ps4_c.target{
                        Target::Tree(ps4_cell)=>format!("{},{}",ps4_cell.0,ps4_cell.1),_=>"NOT_A_TREE".to_string(),
                    }
                    ;
                    eprintln!("PS4HARVOUT unit={} turn={} i={} target={} command={}",unit.id,view.turn,ps4_i,ps4_t,ps4_c.command.replace(' ',"_"));
                    }
                eprintln!("PS4HARVLIST unit={} turn={} returned={}",unit.id,view.turn,ps4_out.len());
                ps4_out
            }'''

REPLANT_OLD = '''                if safe_regeneration&&carried==0&&view.turn>=100&&view.plants.len()<=2&&view.units.iter().filter(|unit|unit.player==0).count()>=2&&is_adjacent(unit.cell,view.shacks[0])&&view.plant_at(unit.cell).is_none(){'''
REPLANT_NEW = '''                let ps4_r1=safe_regeneration;
                let ps4_r2=carried==0;
                let ps4_r3=view.turn>=100;
                let ps4_r4=view.plants.len()<=2;
                let ps4_r5=view.units.iter().filter(|unit|unit.player==0).count()>=2;
                let ps4_r6=is_adjacent(unit.cell,view.shacks[0]);
                let ps4_r7=view.plant_at(unit.cell).is_none();
                eprintln!("PS4REPLANT unit={} turn={} c1_safe_regeneration={} c2_carried_zero={} c3_turn_ge_100={} c4_plants_le_2={} c5_own_units_ge_2={} c6_adjacent_shack={} c7_cell_free={} plants={} own_units={} all={}",unit.id,view.turn,ps4_r1,ps4_r2,ps4_r3,ps4_r4,ps4_r5,ps4_r6,ps4_r7,view.plants.len(),view.units.iter().filter(|unit|unit.player==0).count(),ps4_r1&&ps4_r2&&ps4_r3&&ps4_r4&&ps4_r5&&ps4_r6&&ps4_r7);
                if ps4_r1&&ps4_r2&&ps4_r3&&ps4_r4&&ps4_r5&&ps4_r6&&ps4_r7{'''

OPEN_OLD = '''                let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else(Self::fallback_second_troll);
                let train_now=!self.opening_abandoned&&MoisanBot::can_train(view,desired);'''
OPEN_NEW = '''                let desired=self.desired_second.map(|objective|objective.stats).unwrap_or_else(Self::fallback_second_troll);
                let train_now=!self.opening_abandoned&&MoisanBot::can_train(view,desired);
                let ps4_n=view.units.iter().filter(|unit|unit.player==0).count()as i32;
                let ps4_cost=training_cost(ps4_n,desired.tuple());
                eprintln!("PS4OPEN turn={} own_units={} opening_abandoned={} train_now={} can_train={} desired_second_set={} desired={},{},{},{} eta={} cost_plum={} cost_lemon={} cost_apple={} cost_iron={} inv_plum={} inv_lemon={} inv_apple={} inv_iron={} iron_on_map={} hard_train_turn={} require_preferred={}",view.turn,ps4_n,self.opening_abandoned,train_now,MoisanBot::can_train(view,desired),self.desired_second.is_some(),desired.movement_speed,desired.carry_capacity,desired.harvest_power,desired.chop_power,self.desired_second.map(|o|o.estimated_eta).unwrap_or(-1),ps4_cost[PLUM],ps4_cost[LEMON],ps4_cost[APPLE],ps4_cost[IRON],view.inventories[0][PLUM],view.inventories[0][LEMON],view.inventories[0][APPLE],view.inventories[0][IRON],!view.iron.is_empty(),self.opening_policy.hard_train_turn,self.opening_policy.require_preferred);'''

DEADLINE_OLD = '''                let Some(objective)=self.desired_second else{
                    self.opening_abandoned=true;
                    return;
                    }
                ;
                if Self::training_affordable(view,objective.stats){
                    return;
                    }'''
DEADLINE_NEW = '''                eprintln!("PS4DEADLINE turn={} event=REACHED hard_train_turn={} own_units={} require_preferred={}",view.turn,self.opening_policy.hard_train_turn,view.units.iter().filter(|unit|unit.player==0).count(),self.opening_policy.require_preferred);
                let Some(objective)=self.desired_second else{
                    eprintln!("PS4DEADLINE turn={} event=ABANDONED reason=NO_DESIRED_SECOND",view.turn);
                    self.opening_abandoned=true;
                    return;
                    }
                ;
                if Self::training_affordable(view,objective.stats){
                    eprintln!("PS4DEADLINE turn={} event=AFFORDABLE_KEPT",view.turn);
                    return;
                    }'''

DEADLINE2_OLD = '''                self.desired_second=Self::strongest_affordable(view,self.opening_policy);
                if self.desired_second.is_none(){
                    self.opening_abandoned=true;
                    }
                }'''
DEADLINE2_NEW = '''                self.desired_second=Self::strongest_affordable(view,self.opening_policy);
                if self.desired_second.is_none(){
                    eprintln!("PS4DEADLINE turn={} event=ABANDONED reason=NO_AFFORDABLE_OPTION",view.turn);
                    self.opening_abandoned=true;
                    }
                else{
                    eprintln!("PS4DEADLINE turn={} event=DOWNGRADED_TO_AFFORDABLE",view.turn);
                    }
                }'''

CLAUSE_EDITS = [("chop_candidates/fn-guard", CHOP_FN_OLD, CHOP_FN_NEW),
                ("chop_candidates/plant-loop", CHOP_LOOP_OLD, CHOP_LOOP_NEW),
                ("chop_candidates/returned-list", CHOP_TAIL_OLD, CHOP_TAIL_NEW),
                ("idle_harvest_candidates/whole-fn", HARV_OLD, HARV_NEW),
                ("main_candidates/replant-conjuncts", REPLANT_OLD, REPLANT_NEW),
                ("commands/opening-state", OPEN_OLD, OPEN_NEW),
                ("enforce_training_deadline/entry", DEADLINE_OLD, DEADLINE_NEW),
                ("enforce_training_deadline/abandon", DEADLINE2_OLD, DEADLINE2_NEW)]


# Per-subject additions. The five EDITS above are the accepted Phase-3 set and are applied to
# EVERY subject unchanged; only the champion gets the early anchors on top. See the module
# docstring for why this is per-subject rather than global.
EXTRA_EDITS = {"door1-champion": EARLY_EDITS,
               "door1-clause": EARLY_EDITS + CLAUSE_EDITS}

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
