#!/usr/bin/env python3
"""Generate the ONE source of task `20260825-dance-cure-candidate-2-swap` from Candidate 1's base.

G-0 is `claude_1/cure2/definitions-g0-2026-08-25.md`, ruled DESIGN_ACCEPTED by codex_1 at
`coordination/messages/codex_1/20260825T165607Z-…-ack.md`. Nothing here invents policy: every
clause below is §2.3 of that file, in the same order, and every refusal counter is §6's grammar.

Base: `claude_1/cure1/cure1-hold-v4.rs` (`cc4b3087…`), whose own base is the champion
`cgauto/submissions/candidate-door1-pure-deletion.rs` (`547fa706…`). Candidate 1 is PARKED — its
hold rule is OFF in every Candidate 2 arm and its code is kept byte-for-byte.

Three arms come from this one file and ONE flag line (`build_arms.py`):

  instrument  SWAP=true  NARRATE=true   the G-2 read; can never be champion
  candidate   SWAP=true  NARRATE=false  the G-3 block, and the ladder if kept
  ruleoff     SWAP=false NARRATE=true   the alpha parity reference (control C-1)

Every edit is an ANCHORED replacement that must match exactly once; if the base moves, this
script stops rather than producing a plausible file.

## Construction notes that the G-1 report must carry (they are not in G-0)

1. **The slot map is verified, not merely counted.** G-0 clause 2 guards the positional command
   map on `commands.len() == own_unit_count`. This build ALSO cross-checks the positional map
   against `command_by_id` (the ids parsed out of the MOVE commands themselves): if any own unit
   with a parseable MOVE command sits at a different index than the positional map claims, the
   map is discarded and NO swap fires this turn (counted `sf=`). That is strictly fail-closed —
   it can only refuse swaps G-0 would have allowed, never fire one G-0 forbids.
2. **Refusal-counter order.** When more than one clause fails, exactly one counter is charged, in
   G-0's clause order: adjacency (`sn=`) before target-occupied (`so=`) before the slot guard
   (`sf=`). `d(L) < d(c)` failing charges nothing: it is not a refusal of a would-be cure, it is
   the case where "beyond" has no meaning (`next_cell` fell back off the BFS map).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
BASE = REPO / "claude_1" / "cure1" / "cure1-hold-v4.rs"
BASE_SHA = "cc4b308705883f10192065dd205a36eb78baee3c1068a0697131b791f3d46e9b"
CHAMPION_SHA = "547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0"
OUT = HERE / "cure2-swap-v5.rs"


class GenError(Exception):
    """Fail closed: a generator that guesses produces a file nobody can review."""


def replace_once(text: str, old: str, new: str, what: str) -> str:
    n = text.count(old)
    if n != 1:
        raise GenError(f"anchor {what!r} occurs {n} times, expected exactly 1")
    return text.replace(old, new)


# --------------------------------------------------------------------------- the flag block
FLAGS_OLD = "            const HOLD_RULE_ENABLED:bool=true;const NARRATE_V4_ENABLED:bool=true;"
FLAGS_NEW = """            const HOLD_RULE_ENABLED:bool=false;const NARRATE_V4_ENABLED:bool=false;
            // ---------------------------------------------------------------- Candidate 2
            // Task 20260825-dance-cure-candidate-2-swap, G-0 DESIGN_ACCEPTED by codex_1
            // 2026-08-25. Candidate 1 above is PARKED: its hold rule is off in every arm here and
            // its code is untouched, so `H` is unreachable and `blocked_turns` has no writer.
            //
            // SWAP_P3_SCOPING_ENABLED is rule R-B, adopted verbatim from Candidate 1: on a seat
            // view satisfying the orchard-eligibility predicate the exchange is inert for the
            // WHOLE game. Flipping THIS line alone is control C-16's red half.
            const SWAP_P3_SCOPING_ENABLED:bool=true;
            // `build_arms.py` rewrites exactly the line below to make the three arms, and nothing
            // else differs between them.
            const SWAP_RULE_ENABLED:bool=true;const NARRATE_V5_ENABLED:bool=true;"""

# --------------------------------------------------------------------------- HoldMeta
META_OLD = "            passes:u32,stale_protections:u32,w_collisions:u32,movers:u32,"
META_NEW = ("            passes:u32,stale_protections:u32,w_collisions:u32,movers:u32,"
            "swaps:u32,target_occupied:u32,non_adjacent:u32,slot_fail:u32,")

# --------------------------------------------------------------------------- hold_pass signature
SIG_OLD = ("counters:&BTreeMap<i32,u8>,prev_cells:&BTreeMap<i32,Cell>,)->"
           "(Vec<String>,BTreeMap<i32,char>,BTreeSet<i32>,u32,u32){")
SIG_NEW = ("counters:&BTreeMap<i32,u8>,prev_cells:&BTreeMap<i32,Cell>,swap_enabled:bool,)->"
           "(Vec<String>,BTreeMap<i32,char>,BTreeSet<i32>,u32,u32,[u32;4]){")

# --------------------------------------------------------------------------- per-pass locals
LOCALS_OLD = ("                let mut distance_cache:BTreeMap<Cell,BTreeMap<Cell,i32>> "
              "=BTreeMap::new();")
LOCALS_NEW = """                let mut distance_cache:BTreeMap<Cell,BTreeMap<Cell,i32>> =BTreeMap::new();
                // Candidate 2, per-pass locals. `displaced` is the set of partners already taken
                // as an exchange partner in THIS pass (G-0 clause 4); `swap_counts` is
                // [sw, so, sn, sf].
                let mut displaced:BTreeSet<i32> =BTreeSet::new();
                let mut swap_counts:[u32;4] =[0,0,0,0];"""

SLOT_OLD = ("""                let moving_ids:BTreeSet<i32> =projections.iter().filter(|(_,_,current,_,landing)|landing!=current).map(|(id,_,_,_,_)|*id).collect();
                let occupied_now:BTreeSet<Cell> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.cell).collect();
                let mut reserved:BTreeSet<Cell> =view.units.iter().filter(|unit|unit.player==0&&!moving_ids.contains(&unit.id)).map(|unit|unit.cell).collect();
                for cell in hold_cells{""")
SLOT_NEW = """                let moving_ids:BTreeSet<i32> =projections.iter().filter(|(_,_,current,_,landing)|landing!=current).map(|(id,_,_,_,_)|*id).collect();
                // Candidate 2, G-0 clause 2. `select_recording` emits exactly one command per own
                // unit, ids ascending, so command index k belongs to the k-th own id. That is a
                // POSITIONAL claim about another unit's command, so it is checked twice before it
                // is used: the arity must match, and every own unit whose command parses as a MOVE
                // must sit where the positional map says it does. Either check failing discards
                // the map and NO swap fires this turn (`sf=`).
                let mut own_ids:Vec<i32> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.id).collect();
                own_ids.sort();
                let slot_by_id:Option<BTreeMap<i32,usize>> =if!swap_enabled{
                    None
                }
                else if own_ids.len()!=commands.len(){
                    None
                }
                else{
                    let map:BTreeMap<i32,usize> =own_ids.iter().enumerate().map(|(slot,id)|(*id,slot)).collect();
                    if command_by_id.iter().all(|(id,index)|map.get(id)==Some(index)){
                        Some(map)
                    }
                    else{
                        None
                        }
                    }
                ;
                let occupied_now:BTreeSet<Cell> =view.units.iter().filter(|unit|unit.player==0).map(|unit|unit.cell).collect();
                let mut reserved:BTreeSet<Cell> =view.units.iter().filter(|unit|unit.player==0&&!moving_ids.contains(&unit.id)).map(|unit|unit.cell).collect();
                for cell in hold_cells{"""

# --------------------------------------------------------------------------- the predicate
FAST_OLD = """                    if!landing_forbidden&&!reserved.contains(&landing){
                        reserved.insert(landing);
                        granted.insert(landing);
                        commands[index]=format!("MOVE {} {} {}",id,landing.0,landing.1);
                        branch.insert(id,'P');
                        continue;
                        }"""
FAST_NEW = FAST_OLD + """
                    // ------------------------------------------------ Candidate 2: the exchange
                    // G-0 §2.3, clauses in order. Reached only when the landing is unavailable --
                    // exactly the turns that are L, R or W in the v4 grammar. No lock, no timer,
                    // no counter, no new memory: `prev_cells` is Candidate 1's, already written on
                    // every turn of every arm, and `displaced`/`slot_by_id` are per-pass locals.
                    if swap_enabled&&!landing_forbidden{
                        let partner=view.units.iter().find(|other|other.player==0&&other.id!=id&&other.cell==landing).map(|other|other.id);
                        // Clause 4: a STANDING own partner -- not a mover this pass, on that same
                        // cell last turn too, not already exchanged. An UNKNOWN previous cell
                        // fails CLOSED, exactly as Candidate 1's accepted R-A treatment.
                        let standing=match partner{
                            Some(other)=>!moving_ids.contains(&other)&&matches!(prev_cells.get(&other),Some(previous)if*previous==landing)&&!displaced.contains(&other),None=>false,
                        }
                        ;
                        if standing{
                            let other=partner.unwrap_or(id);
                            if!is_adjacent(unit.cell,landing){
                                // Clause 5: a landing two cells away (movement_speed >= 2) is
                                // EXCLUDED, not handled. G-0 edge case E-2.
                                swap_counts[2]+=1;
                                }
                            else if target==landing{
                                // Clause 6, first half: the teammate is ON the goal. Recorded and
                                // left to the planner, per the card.
                                swap_counts[1]+=1;
                                }
                            else{
                                match slot_by_id.as_ref().and_then(|map|map.get(&other).copied()){
                                    None=>{
                                        swap_counts[3]+=1;
                                        }
                                    Some(other_index)=>{
                                        // Clause 6, second half: the target lies strictly beyond
                                        // the landing. Each cell keyed by its OWN manhattan
                                        // fallback (codex_1 definition 7). Normally automatic --
                                        // L is the first step of a BFS path -- and it bites
                                        // exactly where `next_cell` fell back off the map, which
                                        // is where "beyond" is not meaningful. Not a refusal of a
                                        // would-be cure, so it charges no counter.
                                        let toward_goal=distance_cache.entry(target).or_insert_with(||bfs_distances(&view.walkable,&[target])).clone();
                                        let d_landing=toward_goal.get(&landing).copied().unwrap_or_else(||manhattan(landing,target));
                                        let d_here=toward_goal.get(&unit.cell).copied().unwrap_or_else(||manhattan(unit.cell,target));
                                        if d_landing<d_here{
                                            reserved.insert(landing);
                                            granted.insert(landing);
                                            reserved.insert(unit.cell);
                                            granted.insert(unit.cell);
                                            displaced.insert(other);
                                            commands[index]=format!("MOVE {} {} {}",id,landing.0,landing.1);
                                            commands[other_index]=format!("MOVE {} {} {}",other,unit.cell.0,unit.cell.1);
                                            branch.insert(id,'S');
                                            branch.insert(other,'X');
                                            swap_counts[0]+=1;
                                            continue;
                                            }
                                        }
                                }
                                }
                            }
                        }"""

# --------------------------------------------------------------------------- return + call site
RET_OLD = "                (commands,branch,holders,mover_count,w_collisions)"
RET_NEW = "                (commands,branch,holders,mover_count,w_collisions,swap_counts)"

CALL_OLD = ("                    let(out,mut branch,holders,mover_count,w_collisions)="
            "Self::hold_pass(view,&original,&priority_ids,&forbidden,&hold_cells,hold_enabled,"
            "blocked_turns,prev_cells,);")
CALL_NEW = ("                    let(out,mut branch,holders,mover_count,w_collisions,swap_counts)="
            "Self::hold_pass(view,&original,&priority_ids,&forbidden,&hold_cells,hold_enabled,"
            "blocked_turns,prev_cells,swap_enabled,);")

SCOPE_OLD = ("                let hold_enabled=hold_enabled&&"
             "!(Self::P3_SCOPING_ENABLED&&orchard_inert.unwrap_or(false));")
SCOPE_NEW = SCOPE_OLD + """
                // R-B for the exchange, evaluated from the SAME cached predicate: on an
                // orchard-eligible seat view the swap is inert for the whole game.
                let swap_enabled=Self::SWAP_RULE_ENABLED&&!(Self::SWAP_P3_SCOPING_ENABLED&&orchard_inert.unwrap_or(false));"""

METAW_OLD = ("                    meta.stale_protections=k.iter().filter(|id|"
             "!holders.contains(id)).count() as u32;")
METAW_NEW = METAW_OLD + """
                    meta.swaps=swap_counts[0];
                    meta.target_occupied=swap_counts[1];
                    meta.non_adjacent=swap_counts[2];
                    meta.slot_fail=swap_counts[3];"""

# --------------------------------------------------------------------------- telemetry v5
COMMENT_OLD = """            // NARRATE v4 telemetry. v3's two reads are unchanged in name and meaning (the
            // tick-local map select_recording filled, and the unit-local best taken from the
            // candidate map BEFORE selection consumes it); v4 adds the resolver branch `r=` and"""
COMMENT_NEW = """            // NARRATE v5 telemetry. v4's reads are unchanged in name and meaning; v5 adds the
            // four Candidate 2 per-turn fields sw=/so=/sn=/sf= and RETIRES `H`, which is
            // unreachable with the hold rule off. `b=` is kept in the shape for the decoder and is
            // identically 0 in every v5 arm (blocked_turns' only writer was H); control C-9
            // asserts both. v4's own words follow:
            // tick-local map select_recording filled, and the unit-local best taken from the
            // candidate map BEFORE selection consumes it); v4 adds the resolver branch `r=` and"""

HDR_OLD = 'vec![format!("NARRATE v4 t={}",view.turn)]'
HDR_NEW = 'vec![format!("NARRATE v5 t={}",view.turn)]'

WC_OLD = '                tokens.push(format!("wc={}",meta.w_collisions));'
WC_NEW = WC_OLD + """
                tokens.push(format!("sw={}",meta.swaps));
                tokens.push(format!("so={}",meta.target_occupied));
                tokens.push(format!("sn={}",meta.non_adjacent));
                tokens.push(format!("sf={}",meta.slot_fail));"""

BANNER_OLD = "                    if!MoisanBot::NARRATE_V4_ENABLED{"
BANNER_NEW = "                    if!MoisanBot::NARRATE_V5_ENABLED{"
EMIT_OLD = "                if MoisanBot::NARRATE_V4_ENABLED{"
EMIT_NEW = "                if MoisanBot::NARRATE_V5_ENABLED{"


def main() -> int:
    base = BASE.read_text()
    sha = hashlib.sha256(base.encode()).hexdigest()
    if sha != BASE_SHA:
        raise GenError(f"base {BASE} is {sha}, expected {BASE_SHA}")
    manifest = json.loads((REPO / "claude_1" / "cure1" / "arm-manifest.json").read_text())
    if manifest["source_sha256"] != BASE_SHA or manifest["base_sha256"] != CHAMPION_SHA:
        raise GenError("cure1's arm manifest does not pin this base to the champion")

    text = base
    for what, old, new in [
        ("flag block", FLAGS_OLD, FLAGS_NEW),
        ("HoldMeta fields", META_OLD, META_NEW),
        ("hold_pass signature", SIG_OLD, SIG_NEW),
        ("per-pass locals", LOCALS_OLD, LOCALS_NEW),
        ("slot map", SLOT_OLD, SLOT_NEW),
        ("the predicate", FAST_OLD, FAST_NEW),
        ("hold_pass return", RET_OLD, RET_NEW),
        ("hold_pass call site", CALL_OLD, CALL_NEW),
        ("R-B swap scoping", SCOPE_OLD, SCOPE_NEW),
        ("meta writeback", METAW_OLD, METAW_NEW),
        ("v5 telemetry comment", COMMENT_OLD, COMMENT_NEW),
        ("v5 header", HDR_OLD, HDR_NEW),
        ("v5 counters", WC_OLD, WC_NEW),
        ("banner flag", BANNER_OLD, BANNER_NEW),
        ("emit flag", EMIT_OLD, EMIT_NEW),
    ]:
        text = replace_once(text, old, new, what)

    if "NARRATE v4" in text:
        raise GenError("a v4 header survived the rewrite")
    if text.count("const SWAP_RULE_ENABLED:bool=true;const NARRATE_V5_ENABLED:bool=true;") != 1:
        raise GenError("the arm flag line is not unique")

    OUT.write_text(text)
    out_sha = hashlib.sha256(text.encode()).hexdigest()
    print(f"  base   {BASE.relative_to(REPO)}  sha256 {sha[:16]}")
    print(f"  source {OUT.relative_to(REPO)}  sha256 {out_sha[:16]}  "
          f"{len(text.splitlines())} lines")
    (HERE / "cure2-swap-v5.rs.sha256").write_text(f"{out_sha}  cure2-swap-v5.rs\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GenError as exc:
        print(f"GENERATION REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
