#!/usr/bin/env python3
"""Generate the ONE source of task `20260825-dance-cure-candidate-1-hold` from the champion base.

Three arms come from this one file and two compile-time flags (`build_arms.py`):

  instrument  HOLD=true  NARRATE=true   the real-game read; can never be champion
  candidate   HOLD=true  NARRATE=false  the score block and, if kept, the ladder
  rule-off    HOLD=false NARRATE=true   the parity reference (alpha gate)

## Why a generator rather than a hand-edited copy

Every edit below is an ANCHORED replacement that fails closed: each anchor must occur exactly
once in the base, and the block transplanted from the v3 instrument must be preceded by a proof
that the v3 instrument's base and THIS base carry the identical `select` block. A hand-edited
1,474-line copy cannot show either. If the base ever moves, this script stops rather than
producing a plausible file.

## What the hold rule is (construction ruling local_claude_1 20260825T085500Z)

The charter's single-pass pseudo-code is superseded. `resolve_move_conflicts_hold` runs the base
loop as PASS(K): the cells of the units in K are added to the INITIAL reserved set, so a holder's
square is protected BEFORE any mover can be granted it. K starts empty and grows by union with
the movers that chose to hold, until a pass adds nothing new. Only that final pass mutates
`blocked_turns` or emits telemetry. With the rule off, `H` is unreachable, PASS(EMPTY) is the base
loop verbatim, and exactly one pass runs -- that is what makes the alpha parity gate meaningful.

## The MSG hunk

Transplanted from `claude_1/narrate3/instrument-swap-r1-narrate-v3.rs` (the `select_recording`
block verbatim) WITHOUT the swap rule, which is retired and is not in this base at all. The
payload is v4: v3's `chosen/available` per unit plus `r=` (resolver branch) and `b=`
(blocked_turns, post-decision), and the three per-turn measurements the ruling requires --
`pz=` passes, `sp=` stale protections, `wc=` W-collisions.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BASE = REPO / "cgauto" / "submissions" / "candidate-door1-pure-deletion.rs"
BASE_SHA = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
V3 = REPO / "claude_1" / "narrate3" / "instrument-swap-r1-narrate-v3.rs"
V3_BASE = REPO / "cgauto" / "submissions" / "candidate-swap-r1.rs"
OUT = HERE / "cure1-hold-v4.rs"

SELECT_START = "            fn select(candidates_by_id"
SELECT_END = "            fn move_command(command:&str)"


class GenError(Exception):
    """Fail closed: a generator that guesses produces a file nobody can review."""


def replace_once(text: str, old: str, new: str, what: str) -> str:
    n = text.count(old)
    if n != 1:
        raise GenError(f"anchor {what!r} occurs {n} times, expected exactly 1")
    return text.replace(old, new)


def block(text: str, start: str, end: str, what: str) -> str:
    lines = text.split("\n")
    starts = [k for k, l in enumerate(lines) if l.startswith(start)]
    if len(starts) != 1:
        raise GenError(f"{what}: {len(starts)} start lines, expected 1")
    i = starts[0]
    ends = [k for k, l in enumerate(lines) if l.startswith(end) and k > i]
    if not ends:
        raise GenError(f"{what}: no end line after the start")
    return "\n".join(lines[i:ends[0]]) + "\n"


# --------------------------------------------------------------------------- the hold resolver
HOLD_RS = '''            // ---------------------------------------------------------------- Candidate 1
            // Task 20260825-dance-cure-candidate-1-hold. Compile-time flags; `build_arms.py`
            // rewrites exactly this line to make the three arms, and nothing else differs
            // between them.
            const HOLD_RULE_ENABLED:bool=true;const NARRATE_V4_ENABLED:bool=true;
            // The charter's bound W: at most this many CONSECUTIVE holds per unit. The next
            // block takes the regressive detour and resets the counter, so a hold can slow a
            // dance but can never park a troll.
            const HOLD_WINDOW:u8=2;
            // ONE PASS of the base resolver over the base mover order, with `hold_cells` added
            // to the INITIAL reserved set. The input slice is never mutated: a pass is a pure
            // function of (view, original commands, K), which is what lets it be re-run.
            //
            // Returns: the resolved commands, the per-unit branch code, the ids that chose to
            // hold, the mover count, and the W-collision count (a forced-WAIT mover whose own
            // cell was granted to somebody else -- the base's pre-existing exposure, measured
            // here and deliberately NOT repaired, per section 2 of the construction ruling).
            //
            // With hold_enabled=false and hold_cells empty this is the base loop verbatim: the
            // `H` arm is unreachable, so L and R both take the detour exactly as the base does.
            fn hold_pass(view:&GameState,original:&[String],priority_ids:&BTreeSet<i32>,forbidden_for_non_priority:&BTreeSet<Cell>,hold_cells:&BTreeSet<Cell>,hold_enabled:bool,counters:&BTreeMap<i32,u8>,)->(Vec<String>,BTreeMap<i32,char>,BTreeSet<i32>,u32,u32){
                let mut commands:Vec<String> =original.to_vec();
                let mut branch:BTreeMap<i32,char> =BTreeMap::new();
                let mut holders:BTreeSet<i32> =BTreeSet::new();
                let mut waiting_cells:BTreeSet<Cell> =BTreeSet::new();
                let mut granted:BTreeSet<Cell> =BTreeSet::new();
                let mut distance_cache:BTreeMap<Cell,BTreeMap<Cell,i32>> =BTreeMap::new();
                let command_by_id:BTreeMap<i32,usize> =commands.iter().enumerate().filter_map(|(index,command)|Self::move_command(command).map(|(id,_)|(id,index))).collect();
                let projections:Vec<(i32,usize,Cell,Cell,Cell)> =command_by_id.iter().filter_map(|(id,index)|{
                    let unit=view.unit(*id)?;
                    let(_,target)=Self::move_command(&commands[*index])?;
                    let landing=next_cell(&view.walkable,unit.cell,target,unit.stats.movement_speed);
                    Some((*id,*index,unit.cell,target,landing))
                }
                ).collect();
                let moving_ids:BTreeSet<i32> =projections.iter().filter(|(_,_,current,_,landing)|landing!=current).map(|(id,_,_,_,_)|*id).collect();
                let occupied_now:BTreeSet<Cell> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.cell).collect();
                let mut reserved:BTreeSet<Cell> =view.units.iter().filter(|unit|unit.player==0&&!moving_ids.contains(&unit.id)).map(|unit|unit.cell).collect();
                for cell in hold_cells{
                    reserved.insert(*cell);
                    }
                for(id,index,current,_,landing)in&projections{
                    if landing==current{
                        commands[*index]="WAIT".to_string();
                        // A self-targeting MOVE resolved to WAIT is W with the counter cleared
                        // (codex_1 definition 3). Its cell IS reserved: it is not in moving_ids.
                        branch.insert(*id,'W');
                        }
                    }
                let mut movers:Vec<(i32,usize,Cell,Cell)> =projections.into_iter().filter(|(_,_,current,_,landing)|landing!=current).map(|(id,index,_,target,landing)|(id,index,target,landing)).collect();
                movers.sort_by(|a,b|{
                    let a_priority=priority_ids.contains(&a.0);
                    let b_priority=priority_ids.contains(&b.0);
                    b_priority.cmp(&a_priority).then_with(||b.0.cmp(&a.0))
                }
                );
                let mover_count=movers.len() as u32;
                for(id,index,target,landing)in movers{
                    let Some(unit)=view.unit(id)else{
                        continue
                    }
                    ;
                    let landing_forbidden=!priority_ids.contains(&id)&&forbidden_for_non_priority.contains(&landing);
                    if!landing_forbidden&&!reserved.contains(&landing){
                        reserved.insert(landing);
                        granted.insert(landing);
                        commands[index]=format!("MOVE {} {} {}",id,landing.0,landing.1);
                        branch.insert(id,'P');
                        continue;
                        }
                    // Memoized per target within the turn. bfs_distances is pure, so this changes
                    // cost and nothing else; passes do not multiply BFS work.
                    let toward_goal=distance_cache.entry(target).or_insert_with(||bfs_distances(&view.walkable,&[target])).clone();
                    let detour=ortho_neighbors(unit.cell).into_iter().filter(|cell|view.walkable.contains(cell)).filter(|cell|!reserved.contains(cell)).filter(|cell|!occupied_now.contains(cell)).filter(|cell|{
                        priority_ids.contains(&id)||!forbidden_for_non_priority.contains(cell)
                    }
                    ).min_by_key(|cell|{
                        (toward_goal.get(cell).copied().unwrap_or_else(||manhattan(*cell,target)),*cell,)
                    }
                    );
                    // d_cur uses the detour key's OWN fallback (codex_1 definition 7), or L and H
                    // would be decided by comparing two different metrics.
                    let d_cur=toward_goal.get(&unit.cell).copied().unwrap_or_else(||manhattan(unit.cell,target));
                    match detour{
                        None=>{
                            // No legal detour: the base's forced WAIT, never a hold.
                            commands[index]="WAIT".to_string();
                            waiting_cells.insert(unit.cell);
                            branch.insert(id,'W');
                            }
                        Some(cell)=>{
                            let d_detour=toward_goal.get(&cell).copied().unwrap_or_else(||manhattan(cell,target));
                            if d_detour<=d_cur{
                                reserved.insert(cell);
                                granted.insert(cell);
                                commands[index]=format!("MOVE {} {} {}",id,cell.0,cell.1);
                                branch.insert(id,'L');
                                }
                            else if hold_enabled&&counters.get(&id).copied().unwrap_or(0)<Self::HOLD_WINDOW{
                                commands[index]="WAIT".to_string();
                                holders.insert(id);
                                branch.insert(id,'H');
                                }
                            else{
                                reserved.insert(cell);
                                granted.insert(cell);
                                commands[index]=format!("MOVE {} {} {}",id,cell.0,cell.1);
                                branch.insert(id,'R');
                                }
                            }
                        }
                    }
                let w_collisions=waiting_cells.iter().filter(|cell|granted.contains(cell)).count() as u32;
                (commands,branch,holders,mover_count,w_collisions)
            }
            // The stateful entry point, called from YamoBot::commands. The static entry points
            // above are byte-identical to the base and are not on this path (codex_1 def. 5).
            //
            // K starts empty and grows by union with each pass's holders; the first pass that
            // adds no new holder IS the accepted resolution. K is bounded by the mover count, so
            // at most movers+1 passes run -- the guard below can only fire if that reasoning is
            // wrong, and `pz` is published every turn so the panel can check it independently.
            fn resolve_move_conflicts_hold(view:&GameState,commands:&mut[String],blocked_turns:&mut BTreeMap<i32,u8>,hold_enabled:bool,branch_out:&mut BTreeMap<i32,char>,meta:&mut HoldMeta,){
                let original:Vec<String> =commands.to_vec();
                let priority_ids:BTreeSet<i32> =BTreeSet::new();
                let forbidden:BTreeSet<Cell> =BTreeSet::new();
                let mut k:BTreeSet<i32> =BTreeSet::new();
                let mut passes:u32=0;
                loop{
                    let hold_cells:BTreeSet<Cell> =k.iter().filter_map(|id|view.unit(*id).map(|unit|unit.cell)).collect();
                    let(out,mut branch,holders,mover_count,w_collisions)=Self::hold_pass(view,&original,&priority_ids,&forbidden,&hold_cells,hold_enabled,blocked_turns,);
                    passes+=1;
                    if!holders.is_subset(&k)&&passes<=mover_count+1{
                        for id in holders{
                            k.insert(id);
                            }
                        continue;
                        }
                    for(index,command)in out.into_iter().enumerate(){
                        commands[index]=command;
                        }
                    let live:BTreeSet<i32> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.id).collect();
                    for id in &live{
                        branch.entry(*id).or_insert('N');
                        }
                    blocked_turns.retain(|id,_|live.contains(id));
                    for id in &live{
                        if branch.get(id).copied().unwrap_or('N')=='H'{
                            let entry=blocked_turns.entry(*id).or_insert(0);
                            *entry=entry.saturating_add(1);
                            }
                        else{
                            blocked_turns.remove(id);
                            }
                        }
                    meta.passes=passes;
                    meta.movers=mover_count;
                    meta.w_collisions=w_collisions;
                    meta.stale_protections=k.iter().filter(|id|!holders.contains(id)).count() as u32;
                    *branch_out=branch;
                    return;
                    }
                }
'''

# ------------------------------------------------------------------------------- the v4 payload
NARRATE_RS = '''            // NARRATE v4 telemetry. v3's two reads are unchanged in name and meaning (the
            // tick-local map select_recording filled, and the unit-local best taken from the
            // candidate map BEFORE selection consumes it); v4 adds the resolver branch `r=` and
            // the post-decision counter `b=` per unit, and three per-turn measurements:
            //   pz= passes of the fixed point (1 whenever the rule is off)
            //   sp= stale protections: members of K* that did not hold in the final pass
            //   wc= W-collisions: forced-WAIT movers whose own cell was granted to another mover
            //       (the base's pre-existing exposure, measured, not repaired)
            // Reads only. Nothing here decides anything.
            fn narrate_target(target:Target)->String{
                match target{
                    Target::None=>"NONE".to_string(),
                    Target::Shack=>"SHACK".to_string(),
                    Target::Bank(cell)=>format!("BANK({},{})",cell.0,cell.1),
                    Target::Cell(cell)=>format!("CELL({},{})",cell.0,cell.1),
                    Target::Tree(cell)=>format!("TREE({},{})",cell.0,cell.1),
                }
                }
            // The unit-local best BEFORE joint pairing. `None` means the unit had no candidate
            // vector at all (ABSENT on the wire); `Some(Target::None)` means an explicit WAIT was
            // locally best. Same expression as select_recording's ids.len()==1 branch.
            fn narrate_available(by_id:&BTreeMap<i32,Vec<Candidate>>,)->BTreeMap<i32,Option<Target>>{
                let mut out:BTreeMap<i32,Option<Target>> =BTreeMap::new();
                for(id,candidates)in by_id{
                    out.insert(*id,candidates.iter().max_by(|a,b|a.score.total_cmp(&b.score)).map(|candidate|candidate.target),);
                    }
                out
            }
            fn narrate_message(view:&GameState,chosen:&BTreeMap<i32,Target>,available:&BTreeMap<i32,Option<Target>>,branch:&BTreeMap<i32,char>,counters:&BTreeMap<i32,u8>,meta:&HoldMeta,banner:Option<&str>,)->String{
                // Every live own unit exactly once, ids ascending, roster taken from the VIEW.
                let mut ids:Vec<i32> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.id).collect();
                ids.sort();
                let mut tokens:Vec<String> =vec![format!("NARRATE v4 t={}",view.turn)];
                for id in ids{
                    let target=chosen.get(&id).copied().unwrap_or(Target::None);
                    let want=match available.get(&id).copied().flatten(){
                        Some(target)=>Self::narrate_target(target),None=>"ABSENT".to_string(),
                    }
                    ;
                    let code=branch.get(&id).copied().unwrap_or('N');
                    let blocked=counters.get(&id).copied().unwrap_or(0);
                    tokens.push(format!("u{}={}/{}/r={}/b={}",id,Self::narrate_target(target),want,code,blocked));
                    }
                tokens.push(format!("pz={}",meta.passes));
                tokens.push(format!("sp={}",meta.stale_protections));
                tokens.push(format!("wc={}",meta.w_collisions));
                let body=tokens.join(" ");
                match banner{
                    Some(text)=>format!("MSG {} {}",text,body),
                    None=>format!("MSG {}",body),
                }
                }
'''


def main() -> int:
    base = BASE.read_text()
    digest = hashlib.sha256(base.encode()).hexdigest()
    if digest != BASE_SHA:
        raise GenError(f"base sha256 {digest} != chartered {BASE_SHA}")

    # Control BEFORE the transplant: the v3 instrument's own base and this base must carry the
    # identical `select` block, or the v3 hunk is not transplantable and must be re-derived.
    here_select = block(base, SELECT_START, SELECT_END, "door1 select")
    there_select = block(V3_BASE.read_text(), SELECT_START, SELECT_END, "swap-r1 select")
    if here_select != there_select:
        raise GenError("the v3 instrument's base and this base disagree on `select`; "
                       "the MSG hunk cannot be transplanted verbatim")
    v3_select = block(V3.read_text(), SELECT_START, SELECT_END, "v3 select_recording")
    if "select_recording" not in v3_select:
        raise GenError("the v3 block does not contain select_recording")
    text = replace_once(base, here_select, v3_select, "select block")

    # HoldMeta beside the YamoBot struct (module level: an impl block cannot hold a struct).
    text = replace_once(
        text,
        "        pub struct YamoBot{\n",
        "        #[derive(Clone,Copy,Debug,Default,Eq,PartialEq)]struct HoldMeta{\n"
        "            passes:u32,stale_protections:u32,w_collisions:u32,movers:u32,\n"
        "        }\n"
        "        pub struct YamoBot{\n",
        "YamoBot struct header")

    # The one new field, and its one initializer.
    text = replace_once(
        text,
        "regeneration_commitments:BTreeMap<i32,PlantKind>,opponent_eta_penalty:i32,",
        "regeneration_commitments:BTreeMap<i32,PlantKind>,opponent_eta_penalty:i32,"
        "blocked_turns:BTreeMap<i32,u8>,",
        "YamoBot field list")
    text = replace_once(
        text,
        "regeneration_commitments:BTreeMap::new(),opponent_eta_penalty:0,",
        "regeneration_commitments:BTreeMap::new(),opponent_eta_penalty:0,"
        "blocked_turns:BTreeMap::new(),",
        "YamoBot initializer")

    # The hold resolver, inserted ahead of the base's static entry points, which are untouched.
    text = replace_once(
        text,
        "            fn resolve_move_conflicts(view:&GameState,commands:&mut[String]){\n",
        HOLD_RS + "            fn resolve_move_conflicts(view:&GameState,commands:&mut[String]){\n",
        "static resolver entry point")

    # The v4 payload helpers go INSIDE `impl YamoBot` -- the same place the v3 instrument put its
    # own. `impl Bot for YamoBot` accepts only the trait's methods, so the anchor is the last
    # line of the inherent impl (`fn endgame`'s closing brace and the impl's own).
    text = replace_once(
        text,
        "            fn endgame(view:&GameState)->bool{\n"
        "                view.turn>250||(view.plants.len()<=4&&score(&view.inventories[0])<score(&view.inventories[1]))\n"
        "            }\n"
        "            }\n"
        "        impl Bot for YamoBot{\n",
        "            fn endgame(view:&GameState)->bool{\n"
        "                view.turn>250||(view.plants.len()<=4&&score(&view.inventories[0])<score(&view.inventories[1]))\n"
        "            }\n"
        + NARRATE_RS
        + "            }\n"
        "        impl Bot for YamoBot{\n",
        "inherent impl YamoBot tail")

    # The banner: with the payload on, it folds into the NARRATE line exactly as v3 did; with the
    # payload off, the base's own `MSG <announcement>` is pushed in the base's own position, so
    # the candidate arm is the base byte for byte.
    text = replace_once(
        text,
        "                if!self.announced{\n"
        "                    self.announced=true;\n"
        "                    out.push(format!(\"MSG {}\",self.announcement));\n"
        "                    }\n",
        "                let narrate_banner=if!self.announced{\n"
        "                    self.announced=true;\n"
        "                    if!MoisanBot::NARRATE_V4_ENABLED{\n"
        "                        out.push(format!(\"MSG {}\",self.announcement));\n"
        "                        }\n"
        "                    Some(self.announcement)\n"
        "                }\n"
        "                else{\n"
        "                    None\n"
        "                    }\n"
        "                ;\n",
        "announcement push")

    # The call site: the unit-local reads are captured from the exact map selection is about to
    # consume, and the resolver becomes the stateful one.
    text = replace_once(
        text,
        "                let mut selected=MoisanBot::select(by_id,&view.inventories[0]);\n"
        "                MoisanBot::resolve_move_conflicts(view,&mut selected);\n"
        "                self.remember_selected_regeneration(&selected);\n"
        "                out.extend(selected);\n",
        "                let narrate_available=Self::narrate_available(&by_id);\n"
        "                let mut narrate_chosen:BTreeMap<i32,Target> =BTreeMap::new();\n"
        "                let mut selected=MoisanBot::select_recording(by_id,&view.inventories[0],&mut narrate_chosen,);\n"
        "                let mut narrate_branch:BTreeMap<i32,char> =BTreeMap::new();\n"
        "                let mut narrate_meta=HoldMeta::default();\n"
        "                MoisanBot::resolve_move_conflicts_hold(view,&mut selected,&mut self.blocked_turns,MoisanBot::HOLD_RULE_ENABLED,&mut narrate_branch,&mut narrate_meta,);\n"
        "                self.remember_selected_regeneration(&selected);\n"
        "                out.extend(selected);\n"
        "                if MoisanBot::NARRATE_V4_ENABLED{\n"
        "                    // Exactly one MSG per turn, FIRST in the list. The empty-check below\n"
        "                    // runs on the gameplay tokens alone, so the payload can never\n"
        "                    // suppress the base's WAIT.\n"
        "                    out.insert(0,Self::narrate_message(view,&narrate_chosen,&narrate_available,&narrate_branch,&self.blocked_turns,&narrate_meta,narrate_banner),);\n"
        "                    }\n",
        "select/resolve call site")

    OUT.write_text(text)
    print(f"  wrote {OUT.relative_to(REPO)}  "
          f"{len(text.splitlines())} lines  sha256 {hashlib.sha256(text.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GenError as exc:
        print(f"GENERATOR REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
