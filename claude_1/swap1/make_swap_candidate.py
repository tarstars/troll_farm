#!/usr/bin/env python3
r"""G-1 build — cure alpha (rule R-1, own-troll swap / yield) at the transport level.

Task `20260821-swap-r1-cure`, gate **G-1**, built to the construction codex_1 ACCEPTED at
`coordination/messages/codex_1/20260821T101241Z-20260821-swap-r1-cure-g0-rev2-ack.md`
(design note: `claude_1/swap1/g0-design-swap-r1-2026-08-21.md`).

ONE generator, FOUR outputs, all from the same patch text:

- `cgauto/submissions/candidate-swap-r1.rs`   — the delivery candidate.
- `claude_1/swap1/probe-swap-r1.rs`           — candidate + instrumentation + a SHADOW copy of
  the BASE's own seam function, lifted verbatim out of the base file. The shadow lets every tick
  of every fixture be graded for inertness on the SAME input state (see below); it is read-only
  and the parity gate proves it (probe command stream must equal the candidate's).
- `claude_1/swap1/control-base.rs` / `control-swap-r1.rs` — the constructed-board controls. Same
  source, `main` replaced by a driver that builds a synthetic `GameState`, calls the seam
  directly and prints the resulting command vector. Base and candidate controls are compared
  byte-for-byte, which is what makes the T2b control (and the door control) an experiment rather
  than an assertion.

## Why a shadow, and not just "diff the two games"

Whole-game byte-identity is only evidence on a fixture where alpha NEVER fires: after the first
fire the two runs are different worlds and a later difference means nothing. The shadow closes
that hole. On every tick the probe runs the base's own function on a clone of the pre-resolve
command vector and the same `view`, and reports whether the two results agree. The G-1 claim
"non-firing ticks are byte-identical" is then measured on every tick of every fixture, including
ticks after a divergence, because both arms are evaluated on the SAME state.

## The builder's guards (house pattern, fail-closed)

1. Base digest verified against the pin before a byte is read for patching.
2. Every anchor must occur exactly once; zero or two is a hard error, never a guess.
3. Every edit confined to the seam region (`fn resolve_move_conflicts` .. `impl YamoBot{`).
   After patching, the text outside that region must be byte-identical to the base's. A patch
   that reaches wider is refused even if it would compile.
4. The base file is re-hashed after the run: the champion of record is never written.

Run:  python3 claude_1/swap1/make_swap_candidate.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

BASE = REPO / "cgauto/submissions/candidate-door1-pure-deletion.rs"
BASE_SHA = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"

# rev 1 (the accepted G-0 construction: yield path OR no-detour working-partner path) and
# rev 2 (codex_1's construction ruling 20260821T110533Z: P5, the yield path ONLY) are built by
# the SAME generator from the same patch text; only the fire predicate and the output names
# differ, so the two revisions cannot silently drift apart.
CANDIDATE = REPO / "cgauto/submissions/candidate-swap-r1.rs"
PROBE = HERE / "probe-swap-r1.rs"
CONTROL_BASE = HERE / "control-base.rs"
CONTROL_CAND = HERE / "control-swap-r1.rs"
MANIFEST = HERE / "build-manifest-2026-08-21.json"

CANDIDATE_R2 = REPO / "cgauto/submissions/candidate-swap-r1-rev2.rs"
PROBE_R2 = HERE / "probe-swap-r1-rev2.rs"
CONTROL_CAND_R2 = HERE / "control-swap-r1-rev2.rs"
MANIFEST_R2 = HERE / "build-manifest-rev2-2026-08-21.json"

# The rev-1 fire predicate, verbatim as it appears in PARTNER below, and its rev-2 replacement.
PREDICATE_R1 = "                        if yielding||detour.is_none(){"
PREDICATE_R2 = "                        if yielding{"

REGION_START = "            fn resolve_move_conflicts(view:&GameState,commands:&mut[String]){"
REGION_END = "        impl YamoBot{"

# ---------------------------------------------------------------------------------------
# the patch

HELPER = '''            fn swap_own_index(view:&GameState,commands:&[String])->Option<BTreeMap<i32,usize>>{
                let mut own_ids:Vec<i32> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.id).collect();
                own_ids.sort();
                if own_ids.len()!=commands.len(){
                    return None;
                    }
                let mut map=BTreeMap::new();
                for(index,id)in own_ids.iter().enumerate(){
                    if let Some((parsed,_))=Self::move_command(&commands[index]){
                        if parsed!=*id{
                            return None;
                            }
                        }
                    map.insert(*id,index);
                    }
                Some(map)
                }
'''

LOOP_ANCHOR = "                for(id,index,target,landing)in movers{"
LOOP_PREAMBLE = '''                let own_index=Self::swap_own_index(view,commands);
                let mut swapped_ids:BTreeSet<i32> =BTreeSet::new();
'''

TAIL_ANCHOR = """                    );
                    commands[index]=if let Some(cell)=detour{"""

PARTNER = '''                    );
                    let partner=own_index.as_ref().and_then(|own|{
                        if landing_forbidden{
                            return None;
                            }
                        let u=view.units.iter().find(|other|{
                            other.player==0&&other.cell==landing&&!moving_ids.contains(&other.id)&&!swapped_ids.contains(&other.id)
                        }
                        )?;
                        let legal=next_cell(&view.walkable,u.cell,unit.cell,u.stats.movement_speed)==unit.cell;
                        let free=!reserved.contains(&unit.cell);
                        let allowed=priority_ids.contains(&u.id)||!forbidden_for_non_priority.contains(&unit.cell);
                        if!(legal&&free&&allowed){
                            return None;
                            }
                        own.get(&u.id).map(|u_index|(u.id,*u_index))
                    }
                    );
                    if let Some((u_id,u_index))=partner{
                        let yielding=commands[u_index]=="WAIT";
                        if yielding||detour.is_none(){
{FIRE_ROW}                            reserved.insert(landing);
                            reserved.insert(unit.cell);
                            swapped_ids.insert(u_id);
                            commands[index]=format!("MOVE {} {} {}",id,landing.0,landing.1);
                            commands[u_index]=format!("MOVE {} {} {}",u_id,unit.cell.0,unit.cell.1);
                            continue;
                            }
                        }
                    commands[index]=if let Some(cell)=detour{'''

FIRE_ROW = ('                            eprintln!("SW1FIRE turn={} m={} u={} path={} '
            'detour_existed={} m_from={},{} m_to={},{} u_displaced={}",view.turn,id,u_id,'
            'if yielding{"YIELD"}else{"NODETOUR"},detour.is_some(),unit.cell.0,unit.cell.1,'
            'landing.0,landing.1,commands[u_index]);\n')

# The per-fire seam-fact row required by codex_1's remedy ruling
# (`codex_1/reviews/swap-r1-g1-remedy-ruling-2026-08-21.md`): the mover's FINAL target, the next
# cell from the landing toward that target, and whether that step vacates the partner's old cell.
# PROBE ONLY — it is appended to FIRE_ROW, which the delivery candidate never receives, so the
# candidate bytes are unchanged by this diagnostic (the build manifest is the check).
FIRE_ROW += ('                            eprintln!("SW1SEAM turn={} m={} u={} m_target={},{} '
             'next_from_landing={},{} vacates={} d_from={} d_landing={} target_is_landing={} '
             'u_cmd={}",view.turn,id,u_id,target.0,target.1,'
             'next_cell(&view.walkable,landing,target,unit.stats.movement_speed).0,'
             'next_cell(&view.walkable,landing,target,unit.stats.movement_speed).1,'
             'next_cell(&view.walkable,landing,target,unit.stats.movement_speed)!=landing,'
             'toward_goal.get(&unit.cell).copied().unwrap_or(-1),'
             'toward_goal.get(&landing).copied().unwrap_or(-1),'
             'target==landing,commands[u_index]);\n')


# ---------------------------------------------------------------------------------------
# PROBE-ONLY decline census — task `20260822-peek-planner-target-map`, the coordinator's card of
# 2026-08-22T19:29:45Z. The fire table records only turns where the trigger FIRED; a widened
# trigger fires where the current one DECLINES, and declines were logged nowhere. The two rows
# below log every own-unit collision the seam sees, fired or not, with the fields that say why it
# declined.
#
# Both rows are appended by `patch_probe` only, into the PATCHED seam — never the shadow copy of
# the base's seam, never the delivery candidate. Neither row reads or writes any state: each is a
# single `eprintln!`, so the candidate bytes and the probe's command stream are unchanged, and the
# existing probe-parity gate re-proves that before any row is read.
#
# TWO sites, because one cannot see everything:
#   * SW1COLL0 sits right after `landing_forbidden`, BEFORE the early `continue` that lets a mover
#     take an unreserved landing. `reserved` starts as the cells of own units that are NOT moving,
#     so a landing held by an own unit that is ITSELF moving is unreserved: that collision takes
#     the early exit and NEVER reaches the partner block. A census placed only at the partner
#     block would silently miss exactly that class, which is the kind of hole this programme has
#     paid for before.
#   * SW1COLL1 sits immediately before `let partner=`, where `detour` and `toward_goal` exist, so
#     it carries the same seam fields the fire rows carry.

COLL_EARLY_ANCHOR = ("                    let landing_forbidden=!priority_ids.contains(&id)"
                     "&&forbidden_for_non_priority.contains(&landing);\n")

COLL_EARLY_ROW = (
    '                    if let Some(occupant)=view.units.iter().find(|other|other.player==0&&other.cell==landing){\n'
    '                        let o_id=occupant.id;\n'
    '                        let o_idx=own_index.as_ref().and_then(|own|own.get(&o_id).copied());\n'
    '                        let o_cmd=o_idx.map(|i|commands[i].clone()).unwrap_or_else(||String::from("?"));\n'
    '                        eprintln!("SW1COLL0 turn={} m={} m_from={},{} landing={},{} m_target={},{} occupant={} occupant_is_mover={} occupant_already_swapped={} landing_reserved={} landing_forbidden={} index_ok={} early_take={} occupant_cmd={}",\n'
    '                            view.turn,id,unit.cell.0,unit.cell.1,landing.0,landing.1,target.0,target.1,\n'
    '                            o_id,moving_ids.contains(&o_id),swapped_ids.contains(&o_id),\n'
    '                            reserved.contains(&landing),landing_forbidden,o_idx.is_some(),\n'
    '                            !landing_forbidden&&!reserved.contains(&landing),o_cmd);\n'
    '                        }\n')

COLL_LATE_ANCHOR = "                    let partner=own_index.as_ref().and_then(|own|{\n"

COLL_LATE_ROW = (
    '                    if let Some(occupant)=view.units.iter().find(|other|other.player==0&&other.cell==landing){\n'
    '                        let o_id=occupant.id;\n'
    '                        let o_idx=own_index.as_ref().and_then(|own|own.get(&o_id).copied());\n'
    '                        let o_cmd=o_idx.map(|i|commands[i].clone()).unwrap_or_else(||String::from("?"));\n'
    '                        let o_legal=next_cell(&view.walkable,occupant.cell,unit.cell,occupant.stats.movement_speed)==unit.cell;\n'
    '                        let o_free=!reserved.contains(&unit.cell);\n'
    '                        let o_allowed=priority_ids.contains(&o_id)||!forbidden_for_non_priority.contains(&unit.cell);\n'
    '                        eprintln!("SW1COLL1 turn={} m={} m_from={},{} landing={},{} m_target={},{} occupant={} occupant_is_mover={} occupant_already_swapped={} landing_forbidden={} index_ok={} legal={} free={} allowed={} yielding={} detour_existed={} target_is_landing={} d_from={} d_landing={} occupant_cmd={}",\n'
    '                            view.turn,id,unit.cell.0,unit.cell.1,landing.0,landing.1,target.0,target.1,\n'
    '                            o_id,moving_ids.contains(&o_id),swapped_ids.contains(&o_id),\n'
    '                            landing_forbidden,o_idx.is_some(),o_legal,o_free,o_allowed,o_cmd=="WAIT",\n'
    '                            detour.is_some(),target==landing,\n'
    '                            toward_goal.get(&unit.cell).copied().unwrap_or(-1),\n'
    '                            toward_goal.get(&landing).copied().unwrap_or(-1),o_cmd);\n'
    '                        }\n')



def patch_candidate(base: str, predicate: str = PREDICATE_R1) -> str:
    out = base
    for anchor in (REGION_START, SEAM_HEAD, LOOP_ANCHOR, TAIL_ANCHOR):
        if out.count(anchor) != 1:
            raise SystemExit(f"anchor is not unique ({out.count(anchor)}x): {anchor[:60]!r}")
    out = out.replace(SEAM_HEAD, HELPER + SEAM_HEAD)
    out = out.replace(LOOP_ANCHOR, LOOP_PREAMBLE + LOOP_ANCHOR)
    out = out.replace(TAIL_ANCHOR, PARTNER.replace("{FIRE_ROW}", ""))
    if predicate != PREDICATE_R1:
        if out.count(PREDICATE_R1) != 1:
            raise SystemExit("the rev-1 fire predicate is not unique in the patched text")
        out = out.replace(PREDICATE_R1, predicate, 1)
    return out


# ---------------------------------------------------------------------------------------
# the probe: instrumentation + the base's own function, lifted verbatim as a shadow

SEAM_HEAD = ("            fn resolve_move_conflicts_with_priority_and_forbidden("
             "view:&GameState,commands:&mut[String],priority_ids:&BTreeSet<i32>,"
             "forbidden_for_non_priority:&BTreeSet<Cell>,){")


# ---------------------------------------------------------------------------------------
# REV 3 — PEEK (task `20260822-peek-planner-target-map`), built to codex_1's step-2 construction
# ruling (`peek-planner-target-map-construction-ruling-2026-08-22.md`, agent/codex_1@fc332164)
# as SCOPED by the step-2 scope ruling (`…-step2-scope-ruling-2026-08-22.md`, @9ac11dd0):
# BRANCH 1 — the fail-closed predicate stands and rev 3 is scoped to the 13 residual OSC-011
# re-swaps. It fires on NONE of the 15 corrected OSC-005/027 busy-blocker rows, by design.
#
# The predicate, from the ruling:
#   genuine mover pass-through, PLUS a partner target present in THIS `commands()` call, PLUS
#   that target different from BOTH the mover's final target AND the landing cell being taken.
#   Missing/`None` fails toward NOT displacing.
#
# It REPLACES rev 2's `yielding` clause rather than joining it: rev 2 fired whenever the partner
# was `WAIT`, which is exactly how the 13 re-swaps were produced (the displaced troll was idle for
# one tick and walked straight back). `_yielding` is still bound because the probe reports it.
#
# The value's lifetime, as ruled: a `BTreeMap<i32,Target>` created inside one `commands()` call,
# filled by the SAME selection that produced the commands, borrowed by the resolver, and dropped
# at the end of that call. It is never a field, never returned, never survives a turn.

SEAM_HEAD_R3 = SEAM_HEAD.replace(
    "forbidden_for_non_priority:&BTreeSet<Cell>,){",
    "forbidden_for_non_priority:&BTreeSet<Cell>,peek_targets:Option<&BTreeMap<i32,Target>>,){")

WRAPPER_OLD = """            fn resolve_move_conflicts_with_priority(view:&GameState,commands:&mut[String],priority_ids:&BTreeSet<i32>,){
                Self::resolve_move_conflicts_with_priority_and_forbidden(view,commands,priority_ids,&BTreeSet::new(),);
                }
"""

# every pre-existing entry point keeps its signature and passes `None`, so every caller that has
# no target map — the constructed-board controls included — is fail-closed by construction.
WRAPPER_NEW = """            fn resolve_move_conflicts_with_priority(view:&GameState,commands:&mut[String],priority_ids:&BTreeSet<i32>,){
                Self::resolve_move_conflicts_with_priority_and_forbidden(view,commands,priority_ids,&BTreeSet::new(),None,);
                }
            fn resolve_move_conflicts_with_peek(view:&GameState,commands:&mut[String],peek_targets:&BTreeMap<i32,Target>,){
                Self::resolve_move_conflicts_with_priority_and_forbidden(view,commands,&BTreeSet::new(),&BTreeSet::new(),Some(peek_targets),);
                }
"""

PEEK_HELPERS = """            fn peek_target_cell(view:&GameState,target:Target)->Option<Cell>{
                match target{
                    Target::None=>None,
                    Target::Shack=>Some(view.shacks[0]),
                    Target::Bank(cell)|Target::Cell(cell)|Target::Tree(cell)=>Some(cell),
                }
                }
            fn peek_swap_allowed(view:&GameState,peek_targets:Option<&BTreeMap<i32,Target>>,partner_id:i32,mover_target:Cell,landing:Cell,mover_speed:i32,)->bool{
                let Some(map)=peek_targets else{
                    return false
                }
                ;
                if mover_target==landing{
                    return false;
                    }
                if next_cell(&view.walkable,landing,mover_target,mover_speed)==landing{
                    return false;
                    }
                let Some(partner_target)=map.get(&partner_id).copied()else{
                    return false
                }
                ;
                let Some(partner_cell)=Self::peek_target_cell(view,partner_target)else{
                    return false
                }
                ;
                partner_cell!=mover_target&&partner_cell!=landing
                }
"""

YIELDING_OLD = '                        let yielding=commands[u_index]=="WAIT";\n'
YIELDING_R3 = '                        let _yielding=commands[u_index]=="WAIT";\n'

PREDICATE_R3 = ("                        if Self::peek_swap_allowed(view,peek_targets,u_id,target,"
                "landing,unit.stats.movement_speed){")

# out-of-region edits — PROPAGATION ONLY. Step 1's grant permits exactly this and nothing else:
# "A change outside `resolve_move_conflicts*` other than making that value reachable is out of
# scope." Every anchor must occur exactly once, and the builder re-derives the whole
# out-of-region diff and compares it line-for-line to the declared lists below.
SELECT_SIG_OLD = """            fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;
            6],)->Vec<String>{
"""
SELECT_SIG_NEW = """            fn select(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;
            6],)->Vec<String>{
                let mut peek_discarded:BTreeMap<i32,Target> =BTreeMap::new();
                Self::select_recording(candidates_by_id,inventory,&mut peek_discarded)
                }
            fn select_recording(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;
            6],peek_chosen:&mut BTreeMap<i32,Target>,)->Vec<String>{
"""

SELECT_ONE_OLD = """                    let best=candidates_by_id[&ids[0]].iter().max_by(|a,b|a.score.total_cmp(&b.score)).unwrap();
                    return vec![best.command.clone()];
"""
SELECT_ONE_NEW = """                    let best=candidates_by_id[&ids[0]].iter().max_by(|a,b|a.score.total_cmp(&b.score)).unwrap();
                    peek_chosen.insert(ids[0],best.target);
                    return vec![best.command.clone()];
"""

SELECT_PAIR_OLD = """                                best_pair=Some((a.command.clone(),b.command.clone()));
"""
SELECT_PAIR_NEW = """                                best_pair=Some((a.command.clone(),b.command.clone(),a.target,b.target,));
"""

SELECT_PAIR_RET_OLD = """                    if let Some((a,b))=best_pair{
                        return vec![a,b];
"""
SELECT_PAIR_RET_NEW = """                    if let Some((a,b,a_target,b_target))=best_pair{
                        peek_chosen.insert(ids[0],a_target);
                        peek_chosen.insert(ids[1],b_target);
                        return vec![a,b];
"""

SELECT_LOOP_OLD = """                    used_targets.push(best.target);
"""
SELECT_LOOP_NEW = """                    peek_chosen.insert(id,best.target);
                    used_targets.push(best.target);
"""

COMMANDS_OLD = """                let mut selected=MoisanBot::select(by_id,&view.inventories[0]);
                MoisanBot::resolve_move_conflicts(view,&mut selected);
"""
COMMANDS_NEW = """                let mut peek_targets:BTreeMap<i32,Target> =BTreeMap::new();
                let mut selected=MoisanBot::select_recording(by_id,&view.inventories[0],&mut peek_targets);
                MoisanBot::resolve_move_conflicts_with_peek(view,&mut selected,&peek_targets);
"""

PROPAGATION = (
    (SELECT_SIG_OLD, SELECT_SIG_NEW),
    (SELECT_ONE_OLD, SELECT_ONE_NEW),
    (SELECT_PAIR_OLD, SELECT_PAIR_NEW),
    (SELECT_PAIR_RET_OLD, SELECT_PAIR_RET_NEW),
    (SELECT_LOOP_OLD, SELECT_LOOP_NEW),
    (COMMANDS_OLD, COMMANDS_NEW),
)

# The complete set of lines the propagation may add and remove OUTSIDE the seam region. Guard 3
# cannot be "nothing changed outside the region" for rev 3, so it becomes "exactly this changed,
# and nothing else" — the same fail-closed shape, with the licence written down.
PROPAGATION_EXPECTED_ADDED = [
    "                let mut peek_discarded:BTreeMap<i32,Target> =BTreeMap::new();",
    "                Self::select_recording(candidates_by_id,inventory,&mut peek_discarded)",
    "                }",
    "            fn select_recording(candidates_by_id:BTreeMap<i32,Vec<Candidate>>,inventory:&[i32;",
    "            6],peek_chosen:&mut BTreeMap<i32,Target>,)->Vec<String>{",
    "                    peek_chosen.insert(ids[0],best.target);",
    "                                best_pair=Some((a.command.clone(),b.command.clone(),a.target,b.target,));",
    "                    if let Some((a,b,a_target,b_target))=best_pair{",
    "                        peek_chosen.insert(ids[0],a_target);",
    "                        peek_chosen.insert(ids[1],b_target);",
    "                    peek_chosen.insert(id,best.target);",
    "                let mut peek_targets:BTreeMap<i32,Target> =BTreeMap::new();",
    "                let mut selected=MoisanBot::select_recording(by_id,&view.inventories[0],&mut peek_targets);",
    "                MoisanBot::resolve_move_conflicts_with_peek(view,&mut selected,&peek_targets);",
]
PROPAGATION_EXPECTED_REMOVED = [
    "                                best_pair=Some((a.command.clone(),b.command.clone()));",
    "                    if let Some((a,b))=best_pair{",
    "                let mut selected=MoisanBot::select(by_id,&view.inventories[0]);",
    "                MoisanBot::resolve_move_conflicts(view,&mut selected);",
]

CANDIDATE_R3 = REPO / "cgauto/submissions/candidate-swap-r1-rev3.rs"
PROBE_R3 = HERE / "probe-swap-r1-rev3.rs"
CONTROL_CAND_R3 = HERE / "control-swap-r1-rev3.rs"
MANIFEST_R3 = HERE / "build-manifest-rev3-2026-08-22.json"

# probe-only: one row per partner encounter, whether or not the predicate admits it. This is the
# row that says WHY rev 3 declined, which is the whole reason the decline census had to exist.
PEEK_ROW = (
    '                        eprintln!("SW1PEEK turn={} m={} u={} map_present={} partner_target={} '
    'partner_cell={} mover_target={},{} landing={},{} passthrough={} allowed={} u_cmd={}",'
    'view.turn,id,u_id,peek_targets.is_some(),'
    'peek_targets.and_then(|map|map.get(&u_id)).map(|t|format!("{:?}",t)).unwrap_or_else(||String::from("ABSENT")),'
    'peek_targets.and_then(|map|map.get(&u_id).copied()).and_then(|t|Self::peek_target_cell(view,t))'
    '.map(|cell|format!("{},{}",cell.0,cell.1)).unwrap_or_else(||String::from("NONE")),'
    'target.0,target.1,landing.0,landing.1,'
    'target!=landing&&next_cell(&view.walkable,landing,target,unit.stats.movement_speed)!=landing,'
    'Self::peek_swap_allowed(view,peek_targets,u_id,target,landing,unit.stats.movement_speed),'
    'commands[u_index]);\n')

FIRE_ROW_R3 = FIRE_ROW.replace('if yielding{"YIELD"}else{"NODETOUR"}',
                               'if _yielding{"PEEK_WAIT"}else{"PEEK_BUSY"}')


def patch_rev3_seam(candidate: str) -> str:
    """The in-region half: the extra read-only parameter, the peek entry point, the helpers."""
    out = candidate
    for anchor in (SEAM_HEAD, WRAPPER_OLD, YIELDING_OLD, HELPER):
        if out.count(anchor) != 1:
            raise SystemExit(f"rev-3 seam anchor is not unique ({out.count(anchor)}x): "
                             f"{anchor[:60]!r}")
    out = out.replace(WRAPPER_OLD, WRAPPER_NEW, 1)
    out = out.replace(SEAM_HEAD, SEAM_HEAD_R3, 1)
    out = out.replace(YIELDING_OLD, YIELDING_R3, 1)
    out = out.replace(HELPER, PEEK_HELPERS + HELPER, 1)
    return out


def patch_rev3_propagation(candidate: str) -> str:
    """The out-of-region half: make the selected target reachable at the seam. Nothing else."""
    out = candidate
    for anchor, replacement in PROPAGATION:
        if out.count(anchor) != 1:
            raise SystemExit(f"rev-3 propagation anchor is not unique ({out.count(anchor)}x): "
                             f"{anchor[:60]!r}")
        out = out.replace(anchor, replacement, 1)
    return out


def seam_text(src: str) -> str:
    """The seam function's full text, from its signature to the end of its body."""
    start = src.index(SEAM_HEAD)
    end = src.index(REGION_END, start)
    body = src[start:end]
    # the impl's closing brace sits between the function and `impl YamoBot{`
    # rindex finds the IMPL's closing brace, which is not part of the function
    close = body.rindex("            }\n")
    return body[:close]


def shadow_from_base(base: str) -> str:
    """The BASE's seam, renamed. Not a re-implementation: the base's own bytes."""
    text = seam_text(base)
    return text.replace(SEAM_HEAD,
                        SEAM_HEAD.replace("fn resolve_move_conflicts_with_priority_and_forbidden(",
                                          "fn swap_shadow_base_resolve("), 1)


TURN_ROW = ('                eprintln!("SW1TURN turn={} enabled={} own_units={}",view.turn,'
            'own_index.is_some(),view.units.iter().filter(|unit|unit.player==0).count());\n')

SHADOW_CALL = '''                let swap_shadow_before:Vec<String> =commands.to_vec();
'''

SHADOW_TAIL = '''                let mut swap_shadow:Vec<String> =swap_shadow_before.clone();
                Self::swap_shadow_base_resolve(view,&mut swap_shadow,priority_ids,forbidden_for_non_priority,);
                eprintln!("SW1SHADOW turn={} identical={}",view.turn,swap_shadow.as_slice()==&commands[..]);
                if let Some(own)=own_index.as_ref(){
                    for(uid,index)in own{
                        eprintln!("SW1CMD turn={} id={} idx={} cmd={}",view.turn,uid,index,commands[*index]);
                        }
                    }
                }
'''


def partner_text(fire_row: str, predicate: str = PREDICATE_R1, rev3: bool = False) -> str:
    """The PARTNER block as it actually appears in a built artifact of this revision."""
    text = PARTNER.replace("{FIRE_ROW}", fire_row)
    if predicate != PREDICATE_R1:
        if text.count(PREDICATE_R1) != 1:
            raise SystemExit("the rev-1 fire predicate is not unique in PARTNER")
        text = text.replace(PREDICATE_R1, predicate, 1)
    if rev3:
        if text.count(YIELDING_OLD) != 1:
            raise SystemExit("the yielding binding is not unique in PARTNER")
        text = text.replace(YIELDING_OLD, YIELDING_R3, 1)
    return text


def patch_probe(base: str, candidate: str, predicate: str = PREDICATE_R1,
                rev3: bool = False) -> str:
    out = candidate
    seam_head = SEAM_HEAD_R3 if rev3 else SEAM_HEAD
    fire_row = FIRE_ROW_R3 if rev3 else FIRE_ROW
    # 1. the shadow copy of the base's own seam, inserted beside the helper
    out = out.replace(HELPER, shadow_from_base(base) + HELPER, 1)
    # 2. capture the pre-resolve command vector at the very top of the seam
    if out.count(seam_head) != 1:
        raise SystemExit("seam signature not unique in the candidate")
    out = out.replace(seam_head, seam_head + "\n" + SHADOW_CALL, 1)
    # 3. the per-turn row, after own_index exists
    out = out.replace(LOOP_PREAMBLE + LOOP_ANCHOR, LOOP_PREAMBLE + TURN_ROW + LOOP_ANCHOR, 1)
    # 4. the fire row, inside the fire branch and BEFORE the commands are rewritten
    fired = partner_text("", predicate, rev3)
    if out.count(fired) != 1:
        raise SystemExit("the fire branch is not unique in the candidate")
    out = out.replace(fired, partner_text(fire_row, predicate, rev3), 1)
    # 5. the shadow comparison and the final command dump, at the end of the seam body
    tail_anchor = """                    ;
                    }
                }
"""
    idx = out.index(partner_text(fire_row, predicate, rev3))
    rest = out[idx:]
    if rest.count(tail_anchor) < 1:
        raise SystemExit("seam tail anchor not found")
    rest = rest.replace(tail_anchor, """                    ;
                    }
""" + SHADOW_TAIL, 1)
    out = out[:idx] + rest
    # 6. the decline census (task 20260822-peek-planner-target-map). Both anchors occur TWICE in
    # the probe — once in the shadow copy of the base's seam, once in the patched seam — so the
    # edit is confined to the text at or after the PATCHED seam's signature, which is unique.
    seam_at = out.index(seam_head)
    head, tail = out[:seam_at], out[seam_at:]
    for anchor, row in ((COLL_EARLY_ANCHOR, COLL_EARLY_ROW), (COLL_LATE_ANCHOR, COLL_LATE_ROW)):
        if tail.count(anchor) != 1:
            raise SystemExit(f"decline-census anchor is not unique in the patched seam "
                             f"({tail.count(anchor)}x): {anchor[:60]!r}")
        tail = tail.replace(anchor, anchor + row, 1)
    out = head + tail
    # 7. rev 3 only: the per-encounter PEEK row, immediately after the partner binding, so a
    #    DECLINE carries the same fields a fire does and the two are gradable side by side.
    if rev3:
        if out.count(YIELDING_R3) != 1:
            raise SystemExit("the rev-3 partner binding is not unique in the probe")
        out = out.replace(YIELDING_R3, YIELDING_R3 + PEEK_ROW, 1)
    return out


# ---------------------------------------------------------------------------------------
# the constructed-board control driver

CONTROL_MAIN = r"""
fn main(){
    use crate::game::types::{
        Cell,GameState,Stats,Unit
    }
    ;
    use std::collections::BTreeSet;
    use std::io::Read;
    let mut input=String::new();
    std::io::stdin().read_to_string(&mut input).expect("read control board");
    let mut width=0;
    let mut height=0;
    let mut turn=1;
    let mut walkable:BTreeSet<Cell> =BTreeSet::new();
    let mut units:Vec<Unit> =Vec::new();
    let mut commands:Vec<String> =Vec::new();
    let mut priority:BTreeSet<i32> =BTreeSet::new();
    let mut forbidden:BTreeSet<Cell> =BTreeSet::new();
    for line in input.lines(){
        let line=line.trim();
        if line.is_empty(){
            continue;
            }
        let(key,rest)=line.split_once(':').expect("control row must be key: value");
        let rest=rest.trim();
        let nums=|text:&str|text.split_whitespace().map(|f|f.parse::<i32>().expect("int field")).collect::<Vec<i32>>();
        match key{
            "size"=>{
                let f=nums(rest);
                width=f[0];
                height=f[1];
                }
            "turn"=>turn=nums(rest)[0],
            "walkable"=>{
                for pair in nums(rest).chunks(2){
                    walkable.insert((pair[0],pair[1]));
                    }
                }
            "unit"=>{
                let f=nums(rest);
                units.push(Unit{
                    id:f[0],player:f[1] as usize,cell:(f[2],f[3]),stats:Stats{
                        movement_speed:f[4],carry_capacity:4,harvest_power:1,chop_power:1,
                    }
                    ,carry:[0;
                    6],
                }
                );
                }
            "cmd"=>commands.push(rest.to_string()),
            "priority"=>{
                for id in nums(rest){
                    priority.insert(id);
                    }
                }
            "forbidden"=>{
                for pair in nums(rest).chunks(2){
                    forbidden.insert((pair[0],pair[1]));
                    }
                }
            other=>panic!("unknown control key {}",other),
        }
        }
    let view=GameState{
        width,height,walkable,shacks:[(0,0),(0,0)],inventories:[[0;
        6],[0;
        6]],units,plants:Vec::new(),scores:[0,0],turn,next_id:99,iron:BTreeSet::new(),water:BTreeSet::new(),
    }
    ;
    crate::bot::moisan::swap_control_resolve(&view,&mut commands,&priority,&forbidden);
    println!("{}",commands.join(";"));
    }
"""

CONTROL_HOOK = """    pub fn swap_control_resolve(view:&crate::game::GameState,commands:&mut [String],priority_ids:&std::collections::BTreeSet<i32>,forbidden:&std::collections::BTreeSet<crate::game::types::Cell>,){
        MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(view,commands,priority_ids,forbidden,);
        }
"""

MAIN_HEAD = "fn main(){\n    let stdin=io::stdin();"


def control_from(src: str, rev3: bool = False) -> str:
    """Same source, `main` replaced by the constructed-board driver, plus a pub hook.

    The seam is a private associated fn, so the driver cannot reach it from the crate root; the
    hook is inserted INSIDE `pub mod moisan`, which is the only widening the control needs and
    which never travels into the delivery candidate.
    """
    anchor = "        impl YamoBot{"
    if src.count(anchor) != 1:
        raise SystemExit("YamoBot impl anchor not unique")
    hook = CONTROL_HOOK
    if rev3:
        # the control drives the seam with NO target map: `None` is the fail-closed value, so the
        # constructed-board control of rev 3 must reproduce the base's output exactly.
        hook = hook.replace("priority_ids,forbidden,);", "priority_ids,forbidden,None,);")
    out = src.replace(anchor, hook + anchor, 1)
    if out.count(MAIN_HEAD) != 1:
        raise SystemExit("main anchor not unique")
    idx = out.index(MAIN_HEAD)
    return out[:idx] + CONTROL_MAIN.strip() + "\n"


# ---------------------------------------------------------------------------------------
# rev-3 constructed-board controls WITH a target map.
#
# The plain rev-3 control passes `None` and therefore can only ever show the fail-closed side.
# A predicate that is only ever observed DECLINING is an untested branch — the exact defect class
# this programme has shipped before — so rev 3 gets a second driver that accepts the map:
#
#   peek: <id> <kind> <x> <y>     kind 0=None 1=Shack 2=Bank 3=Cell 4=Tree
#
# and a BASE twin with the same driver whose hook ignores the map entirely. Same board, same
# parser, same seam call; the only variable is whether the fact is there and what it says.
CONTROL_MAIN_PEEK = CONTROL_MAIN.replace(
    '''    let mut forbidden:BTreeSet<Cell> =BTreeSet::new();''',
    '''    let mut forbidden:BTreeSet<Cell> =BTreeSet::new();
    let mut peek:Vec<(i32,i32,i32,i32)> =Vec::new();''', 1).replace(
    '''            other=>panic!("unknown control key {}",other),''',
    '''            "peek"=>{
                let f=nums(rest);
                peek.push((f[0],f[1],f[2],f[3]));
                }
            other=>panic!("unknown control key {}",other),''', 1).replace(
    '''    crate::bot::moisan::swap_control_resolve(&view,&mut commands,&priority,&forbidden);''',
    '''    crate::bot::moisan::swap_control_resolve_peek(&view,&mut commands,&priority,&forbidden,&peek,);''', 1)

CONTROL_HOOK_PEEK_BASE = """    pub fn swap_control_resolve_peek(view:&crate::game::GameState,commands:&mut [String],priority_ids:&std::collections::BTreeSet<i32>,forbidden:&std::collections::BTreeSet<crate::game::types::Cell>,_peek:&[(i32,i32,i32,i32)],){
        MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(view,commands,priority_ids,forbidden,);
        }
"""

CONTROL_HOOK_PEEK_R3 = """    pub fn swap_control_resolve_peek(view:&crate::game::GameState,commands:&mut [String],priority_ids:&std::collections::BTreeSet<i32>,forbidden:&std::collections::BTreeSet<crate::game::types::Cell>,peek:&[(i32,i32,i32,i32)],){
        let mut map:std::collections::BTreeMap<i32,Target> =std::collections::BTreeMap::new();
        for(id,kind,x,y)in peek{
            let target=match kind{
                0=>Target::None,1=>Target::Shack,2=>Target::Bank((*x,*y)),3=>Target::Cell((*x,*y)),_=>Target::Tree((*x,*y)),
            }
            ;
            map.insert(*id,target);
            }
        MoisanBot::resolve_move_conflicts_with_priority_and_forbidden(view,commands,priority_ids,forbidden,Some(&map),);
        }
"""

CONTROL_BASE_PEEK_R3 = HERE / "control-base-peek-rev3.rs"
CONTROL_CAND_PEEK_R3 = HERE / "control-swap-r1-peek-rev3.rs"


def control_peek_from(src: str, hook: str) -> str:
    """The peek driver. Same shape as `control_from`, different hook and different `main`."""
    anchor = "        impl YamoBot{"
    if src.count(anchor) != 1:
        raise SystemExit("YamoBot impl anchor not unique")
    out = src.replace(anchor, hook + anchor, 1)
    if out.count(MAIN_HEAD) != 1:
        raise SystemExit("main anchor not unique")
    idx = out.index(MAIN_HEAD)
    return out[:idx] + CONTROL_MAIN_PEEK.strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="build cure alpha's artifacts")
    ap.add_argument("--rev3", action="store_true",
                    help="build PEEK rev 3 (task 20260822-peek-planner-target-map) to the -rev3 "
                         "output names; rev-1 and rev-2 outputs untouched")
    ap.add_argument("--rev2", action="store_true",
                    help="build the P5 (yield-path-only) revision codex_1 approved at "
                         "20260821T110533Z, to the -rev2 output names; rev-1 outputs untouched")
    args = ap.parse_args(argv)

    if args.rev2 and args.rev3:
        print("REFUSING: --rev2 and --rev3 build different candidates; pick one")
        return 1
    if args.rev3:
        predicate, candidate_path, probe_path = PREDICATE_R3, CANDIDATE_R3, PROBE_R3
        control_cand_path, manifest_path = CONTROL_CAND_R3, MANIFEST_R3
    elif args.rev2:
        predicate, candidate_path, probe_path = PREDICATE_R2, CANDIDATE_R2, PROBE_R2
        control_cand_path, manifest_path = CONTROL_CAND_R2, MANIFEST_R2
    else:
        predicate, candidate_path, probe_path = PREDICATE_R1, CANDIDATE, PROBE
        control_cand_path, manifest_path = CONTROL_CAND, MANIFEST

    base = BASE.read_text()
    got = hashlib.sha256(base.encode()).hexdigest()
    if got != BASE_SHA:
        print(f"REFUSING: base sha256 {got[:16]}… != champion of record {BASE_SHA[:16]}…")
        return 1

    candidate = patch_candidate(base, predicate)
    if args.rev3:
        candidate = patch_rev3_propagation(patch_rev3_seam(candidate))

    # guard 3: nothing outside the seam region changed
    def outside(text: str) -> tuple[str, str]:
        s = text.index("            fn resolve_move_conflicts(view:&GameState")
        e = text.index(REGION_END, s)
        return text[:s], text[e:]
    if args.rev3:
        # Guard 3, rev-3 form. PEEK cannot be built without making the selected target reachable,
        # which is out-of-region by construction and which step 1 grants in exactly one sentence.
        # So the guard is not "nothing changed" but "EXACTLY the declared lines changed": the
        # out-of-region diff is re-derived from the bytes and compared line-for-line to the
        # declaration. Any extra hunk — a mis-anchored replace, a stray edit — fails the build.
        import difflib
        added, removed = [], []
        for side in (0, 1):
            for line in difflib.unified_diff(outside(base)[side].splitlines(),
                                             outside(candidate)[side].splitlines(), n=0):
                if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
                    continue
                if line.startswith("+"):
                    added.append(line[1:])
                elif line.startswith("-"):
                    removed.append(line[1:])
        if sorted(added) != sorted(PROPAGATION_EXPECTED_ADDED) or \
                sorted(removed) != sorted(PROPAGATION_EXPECTED_REMOVED):
            print("REFUSING: the out-of-region diff is not the declared propagation")
            print("  unexpected added:   ", sorted(set(added) - set(PROPAGATION_EXPECTED_ADDED)))
            print("  unexpected removed: ", sorted(set(removed) - set(PROPAGATION_EXPECTED_REMOVED)))
            print("  declared but absent:", sorted(
                (set(PROPAGATION_EXPECTED_ADDED) - set(added))
                | (set(PROPAGATION_EXPECTED_REMOVED) - set(removed))))
            return 1
        print(f"rev 3 out-of-region diff is exactly the declared propagation "
              f"(+{len(added)} / -{len(removed)} lines): verified")
        # Guard 5, rev-3 form: reverse every declared edit and the rev-1 candidate must come back
        # byte for byte. That is what proves rev 3 is rev 1 PLUS the declared edits and nothing
        # else — including inside the seam region, where guard 3 cannot see.
        back = candidate
        for anchor, replacement in PROPAGATION:
            if back.count(replacement) != 1:
                print(f"REFUSING: reverse-apply found {back.count(replacement)} of a declared "
                      f"propagation replacement")
                return 1
            back = back.replace(replacement, anchor, 1)
        back = back.replace(PEEK_HELPERS, "", 1)
        back = back.replace(SEAM_HEAD_R3, SEAM_HEAD, 1)
        back = back.replace(WRAPPER_NEW, WRAPPER_OLD, 1)
        back = back.replace(YIELDING_R3, YIELDING_OLD, 1)
        back = back.replace(PREDICATE_R3, PREDICATE_R1, 1)
        if back != patch_candidate(base, PREDICATE_R1):
            print("REFUSING: rev 3 does not reverse to the rev-1 candidate")
            return 1
        print("rev 3 reverses to the rev-1 candidate byte for byte: verified")
    elif outside(candidate) != outside(base):
        print("REFUSING: the patch changed bytes OUTSIDE the seam region")
        return 1

    # guard 5 (rev 2 only): the ONLY difference from the rev-1 candidate is the fire predicate.
    if args.rev2:
        rev1 = patch_candidate(base, PREDICATE_R1)
        if candidate != rev1.replace(PREDICATE_R1, PREDICATE_R2, 1):
            print("REFUSING: rev 2 differs from rev 1 by more than the fire predicate")
            return 1
        print("rev 2 differs from rev 1 by exactly the fire predicate line: verified")

    probe = patch_probe(base, candidate, predicate, rev3=args.rev3)
    candidate_path.write_text(candidate)
    probe_path.write_text(probe)
    CONTROL_BASE.write_text(control_from(base))
    control_cand_path.write_text(control_from(candidate, rev3=args.rev3))
    if args.rev3:
        CONTROL_BASE_PEEK_R3.write_text(control_peek_from(base, CONTROL_HOOK_PEEK_BASE))
        CONTROL_CAND_PEEK_R3.write_text(control_peek_from(candidate, CONTROL_HOOK_PEEK_R3))

    manifest = {
        "task": "20260822-peek-planner-target-map" if args.rev3 else "20260821-swap-r1-cure",
        "gate": "G-1",
        "revision": 3 if args.rev3 else (2 if args.rev2 else 1),
        "fire_predicate": predicate.strip(),
        "base": {"path": str(BASE.relative_to(REPO)), "sha256": got},
        "outputs": {},
    }
    emitted = [candidate_path, probe_path, CONTROL_BASE, control_cand_path]
    if args.rev3:
        emitted += [CONTROL_BASE_PEEK_R3, CONTROL_CAND_PEEK_R3]
    for path in emitted:
        manifest["outputs"][str(path.relative_to(REPO))] = hashlib.sha256(
            path.read_bytes()).hexdigest()
        print(f"wrote {path.relative_to(REPO)}  sha256 "
              f"{manifest['outputs'][str(path.relative_to(REPO))][:16]}…")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
        print("INTEGRITY FAILURE: the base file was modified")
        return 1
    print("base byte-exact after patching: verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
