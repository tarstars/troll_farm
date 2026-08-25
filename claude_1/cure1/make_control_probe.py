#!/usr/bin/env python3
"""Generate the **control probe**: the hold resolver driven directly over hand-built situations.

codex_1's six red/green controls, the charter's positive control and my own contention control are
all statements about the RESOLVER's branch transitions. Emergent play cannot be asked for a
specific transition on demand, so the probe calls `resolve_move_conflicts_hold` (and, for the
contention control, a single `hold_pass`) on constructed `GameState`s and prints, per turn, the
branch, the counter and the resulting command for every unit.

It is generated from `arm-instrument.rs` by ADDING a driver — no line of the resolver, the
selector or the telemetry is edited — and the driver lives inside `mod moisan` because
`MoisanBot` and the resolver are private to that module. `main` dispatches to it only when
`CURE1_CONTROL_PROBE=1` is set, so the probe binary still plays a normal game otherwise; the
probe's own parity control checks exactly that.

What the probe can and cannot say: it tests the resolver in isolation, so it proves the branch
transitions and the contention repair. It says nothing about whether those branches are reached in
real play — that is the panel's and G-2's job, and the report says so rather than letting a green
here stand in for a green there.

    python3 claude_1/cure1/make_control_probe.py
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SRC = HERE / "arm-instrument.rs"
OUT = HERE / "control-probe.rs"

ANCHOR_MAIN = """fn main(){
    let stdin=io::stdin();"""

DRIVER_ANCHOR = "        impl Bot for YamoBot{\n"

DRIVER = r'''        // ------------------------------------------------------- CONTROL PROBE (added, not edited)
        // Drives the hold resolver over hand-built situations. Prints one CTRL line per unit per
        // turn: the branch, the post-decision counter and the command the resolver produced.
        pub struct Cure1Probe;
        impl Cure1Probe{
            fn stats()->Stats{
                Stats{
                    movement_speed:1,carry_capacity:2,harvest_power:1,chop_power:1,
                }
                }
            fn unit(id:i32,cell:Cell)->Unit{
                Unit{
                    id,player:0,cell,stats:Self::stats(),carry:[0;6],
                }
                }
            fn view(walkable:&[Cell],units:Vec<Unit>,turn:i32)->GameState{
                GameState{
                    width:16,height:16,walkable:walkable.iter().copied().collect(),shacks:[(0,15),(15,0)],inventories:[[0;6],[0;6]],units,plants:Vec::new(),scores:[0,0],turn,next_id:100,iron:BTreeSet::new(),water:BTreeSet::new(),
                }
                }
            // One turn: resolve `commands` on `view` with the persistent counter map, and print.
            fn step(name:&str,turn:i32,view:&GameState,commands:&[String],counters:&mut BTreeMap<i32,u8>,prev_cells:&mut BTreeMap<i32,Cell>,hold:bool,)->Vec<String>{
                let mut resolved:Vec<String> =commands.to_vec();
                let mut branch:BTreeMap<i32,char> =BTreeMap::new();
                let mut meta=HoldMeta::default();
                // The probe never runs on a real map, so the orchard cache is seeded NOT-eligible
                // and R-B is inert here by construction: these controls are about R-A and the
                // fixed point. R-B has its own control, on the panel (revision_controls.py F2).
                let mut orchard_inert=Some(false);
                MoisanBot::resolve_move_conflicts_hold(view,&mut resolved,counters,prev_cells,&mut orchard_inert,hold,&mut branch,&mut meta,);
                for unit in view.units.iter().filter(|unit|unit.player==0){
                    let code=branch.get(&unit.id).copied().unwrap_or('N');
                    let b=counters.get(&unit.id).copied().unwrap_or(0);
                    let cmd=MoisanBot::move_command_index(commands,unit.id).map(|index|resolved[index].clone()).unwrap_or_else(||"<no command>".to_string());
                    println!("CTRL {} hold={} turn={} u{} cell={},{} r={} b={} cmd={} pz={} sp={} wc={}",name,hold,turn,unit.id,unit.cell.0,unit.cell.1,code,b,cmd,meta.passes,meta.stale_protections,meta.w_collisions);
                    }
                resolved
            }
            // Declare a blocker TRANSIENT for the next call: it is recorded as having stood
            // somewhere else last turn. Used only where the control is about a blocker that has
            // just arrived; a control about a PERMANENT blocker never calls this and lets the
            // resolver's own bookkeeping fill the map.
            fn arrived(prev_cells:&mut BTreeMap<i32,Cell>,id:i32,from:Cell){
                prev_cells.insert(id,from);
                }
            // The contention control needs the UNSEEDED single pass to be visible beside the
            // fixed point, because the claim is that the fixed point repairs what one pass does.
            fn one_pass(name:&str,view:&GameState,commands:&[String],prev_cells:&BTreeMap<i32,Cell>,hold:bool){
                let counters:BTreeMap<i32,u8> =BTreeMap::new();
                let(resolved,branch,holders,movers,w_collisions)=MoisanBot::hold_pass(view,commands,&BTreeSet::new(),&BTreeSet::new(),&BTreeSet::new(),hold,&counters,prev_cells,);
                for unit in view.units.iter().filter(|unit|unit.player==0){
                    let code=branch.get(&unit.id).copied().unwrap_or('N');
                    let cmd=MoisanBot::move_command_index(commands,unit.id).map(|index|resolved[index].clone()).unwrap_or_else(||"<no command>".to_string());
                    println!("PASS1 {} hold={} u{} cell={},{} r={} cmd={} holders={} movers={} wc={}",name,hold,unit.id,unit.cell.0,unit.cell.1,code,cmd,holders.len(),movers,w_collisions);
                    }
                }
            pub fn run(){
                // --- A: a one-wide corridor with a teammate that never moves. The blocked unit's
                // only free neighbour is the cell behind it, which is farther from the target:
                // the persistent regressive block of codex_1's control 1.
                let corridor:Vec<Cell> =vec![(0,0),(1,0),(2,0),(3,0)];
                for hold in [true,false]{
                    // A-permanent: the teammate NEVER moves. Under revision R-A this is exactly
                    // the case the hold must NOT take: the standing would be worthless, so the
                    // base's regressive detour is right and the branch must be R on every turn.
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    for turn in 1..=4{
                        let view=Self::view(&corridor,vec![Self::unit(5,(1,0)),Self::unit(3,(2,0))],turn);
                        let commands=vec![format!("MOVE 5 3 0"),"WAIT".to_string()];
                        Self::step("A-permanent-block",turn,&view,&commands,&mut counters,&mut prev,hold);
                        }
                    // A-transient: the SAME geometry with a blocker that arrived on (2,0) only
                    // last turn. This is codex_1's control 1 and it must still cycle
                    // H(b=1), H(b=2), R(b=0), H(b=1): the bound W is what stops a hold from
                    // becoming a parked troll, and the counter must reset on R.
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    for turn in 1..=4{
                        Self::arrived(&mut prev,3,(2,1));
                        let view=Self::view(&corridor,vec![Self::unit(5,(1,0)),Self::unit(3,(2,0))],turn);
                        let commands=vec![format!("MOVE 5 3 0"),"WAIT".to_string()];
                        Self::step("A-transient-block",turn,&view,&commands,&mut counters,&mut prev,hold);
                        }
                    }
                // --- B: after a prior hold, an IMPROVING detour must be taken as L with the
                // counter cleared. The counter is seeded, because the counter IS the state the
                // control is about.
                let bypass:Vec<Cell> =vec![(1,1),(2,1),(3,1),(1,0),(2,0),(3,0)];
                {
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    counters.insert(5,1);
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    Self::arrived(&mut prev,3,(0,1));
                    // The blocker sits on u5's PRIMARY landing (1,0); the free neighbour (2,1)
                    // is one step CLOSER to (3,0) than (1,1) is, so the improving arm is reached.
                    let view=Self::view(&bypass,vec![Self::unit(5,(1,1)),Self::unit(3,(1,0))],1);
                    let commands=vec!["MOVE 5 3 0".to_string(),"WAIT".to_string()];
                    Self::step("B-improving-detour",1,&view,&commands,&mut counters,&mut prev,true);
                    }
                // --- C: codex_1's "equal-distance detour" case, which CANNOT BE CONSTRUCTED.
                // On a 4-connected grid, BFS distances of adjacent cells differ by exactly one,
                // and a free orthogonal neighbour of a reachable cell is itself reachable, so the
                // fallback cannot apply to one side only. `toward_goal[detour] == d_cur` is
                // therefore unreachable and the predicate's `<=` is exactly `<`. The scenario is
                // run anyway and prints the sideways cell resolving as H (it is +1, not equal),
                // which is the demonstration.
                let square:Vec<Cell> =vec![(1,0),(1,1),(2,0),(2,1),(3,0),(3,1)];
                {
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    counters.insert(5,1);
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    Self::arrived(&mut prev,3,(2,1));
                    let view=Self::view(&square,vec![Self::unit(5,(1,0)),Self::unit(3,(2,0))],1);
                    let commands=vec!["MOVE 5 3 0".to_string(),"WAIT".to_string()];
                    Self::step("C-equal-detour-not-constructible",1,&view,&commands,&mut counters,&mut prev,true);
                    }
                // --- D: no legal detour after a prior hold is the base's forced WAIT, W0.
                let deadend:Vec<Cell> =vec![(0,0),(1,0),(2,0)];
                {
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    counters.insert(5,1);
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    let view=Self::view(&deadend,vec![Self::unit(5,(0,0)),Self::unit(3,(1,0))],1);
                    let commands=vec!["MOVE 5 2 0".to_string(),"WAIT".to_string()];
                    Self::step("D-no-detour",1,&view,&commands,&mut counters,&mut prev,true);
                    }
                // --- E: a FREE primary landing after a prior hold is P0.
                {
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    counters.insert(5,1);
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    let view=Self::view(&corridor,vec![Self::unit(5,(1,0))],1);
                    let commands=vec!["MOVE 5 3 0".to_string()];
                    Self::step("E-free-primary",1,&view,&commands,&mut counters,&mut prev,true);
                    }
                // --- F: a live own unit with no MOVE this turn is N0.
                {
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    counters.insert(5,1);
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    let view=Self::view(&corridor,vec![Self::unit(5,(1,0))],1);
                    let commands=vec!["HARVEST 5".to_string()];
                    Self::step("F-non-move",1,&view,&commands,&mut counters,&mut prev,true);
                    }
                // --- G: a self-targeting MOVE resolved to WAIT is W0.
                {
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    counters.insert(5,1);
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    let view=Self::view(&corridor,vec![Self::unit(5,(1,0))],1);
                    let commands=vec!["MOVE 5 1 0".to_string()];
                    Self::step("G-self-target",1,&view,&commands,&mut counters,&mut prev,true);
                    }
                // --- H: THE CONTENTION CONTROL. Movers are processed in DESCENDING id, so u9 is
                // resolved before u5. u9's landing is u5's cell, and u5 is about to hold. One
                // unseeded pass hands u5's square away while u5 stands on it; the fixed point
                // must not. Geometry: a corridor (0,0)..(3,0) with a stationary blocker at (3,0)
                // reachable only through it, and u9 behind u5.
                // (1,1) is u5's regressive escape, so u5 HOLDS rather than being forced to WAIT;
                // without it the situation is the base's forced-WAIT exposure instead, which is a
                // different control (and is what the first draft of this fixture measured).
                // u3 is declared to have ARRIVED on (2,0) last turn, because under revision R-A a
                // permanent blocker no longer produces a hold at all and the contention hazard is
                // about a unit that IS holding. The hazard itself is untouched by R-A.
                let lane:Vec<Cell> =vec![(0,0),(1,0),(2,0),(3,0),(1,1)];
                {
                    let view=Self::view(&lane,vec![Self::unit(9,(0,0)),Self::unit(5,(1,0)),Self::unit(3,(2,0))],1);
                    let commands=vec!["MOVE 9 1 0".to_string(),"MOVE 5 3 0".to_string(),"WAIT".to_string()];
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    Self::arrived(&mut prev,3,(2,1));
                    Self::one_pass("H-contention",&view,&commands,&prev,true);
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    Self::arrived(&mut prev,3,(2,1));
                    Self::step("H-contention",1,&view,&commands,&mut counters,&mut prev,1==1);
                    }
                // --- I: THE CHARTER'S POSITIVE CONTROL, rebuilt for revision R-A.
                // The as-built version used a teammate that simply stood on the cell for two
                // turns. R-A calls that a PERMANENT block and refuses to hold on it, so that
                // fixture would now measure nothing -- it is kept as A-permanent-block, where the
                // detour is the right answer. The transient block as it occurs in play is a
                // teammate that has just ARRIVED on the cell and is busy this turn (a non-MOVE
                // command, so its square is reserved), then leaves. u5 must hold instead of
                // stepping backwards, and must then walk FORWARD -- not stand.
                //
                // Note for the record, because it bounds what this rule can now do: with the base
                // resolver a blocker whose square is reserved is necessarily a NON-mover, and a
                // non-mover that stood on the same square last turn is permanent by R-A. So in
                // play the hold fires at most once per arrival, and the two-turn `W` bound is
                // reached only when the blocking square keeps being handed to a different mover.
                // A-transient-block exercises the counter's two-turn cycle by DECLARING the
                // blocker to have arrived on each turn; that is a statement about the counter, not
                // a claim that the sequence is common in play.
                let escape:Vec<Cell> =vec![(0,0),(1,0),(2,0),(3,0),(1,1)];
                for hold in [true,false]{
                    let mut counters:BTreeMap<i32,u8> =BTreeMap::new();
                    let mut prev:BTreeMap<i32,Cell> =BTreeMap::new();
                    Self::arrived(&mut prev,3,(2,1));
                    let mut cell=(1,0);
                    for turn in 1..=4{
                        let mut units=vec![Self::unit(5,cell)];
                        let mut commands=vec![format!("MOVE 5 3 0")];
                        if turn<2{
                            units.push(Self::unit(3,(2,0)));
                            commands.push("HARVEST 3".to_string());
                            }
                        let view=Self::view(&escape,units,turn);
                        let resolved=Self::step("I-positive",turn,&view,&commands,&mut counters,&mut prev,hold);
                        // Apply the movement the resolver produced, so the next turn sees it.
                        if let Some((_,landing))=MoisanBot::move_command(&resolved[0]){
                            cell=landing;
                            }
                        }
                    }
                }
            }
'''

# The one helper the driver needs that the base does not expose: the index of a unit's command.
HELPER_ANCHOR = "            fn move_command(command:&str)->Option<(i32,Cell)>{\n"
HELPER = """            // Added for the control probe: which slot in the command list belongs to a unit.
            // Reads through move_command, so it cannot disagree with the resolver about parsing.
            fn move_command_index(commands:&[String],id:i32)->Option<usize>{
                commands.iter().position(|command|Self::move_command(command).map(|(parsed,_)|parsed==id).unwrap_or(false))
                }
"""

MAIN_NEW = """fn main(){
    if std::env::var("CURE1_CONTROL_PROBE").as_deref()==Ok("1"){
        crate::bot::moisan::Cure1Probe::run();
        return;
        }
    let stdin=io::stdin();"""


def main() -> int:
    text = SRC.read_text()
    for anchor, count in ((ANCHOR_MAIN, 1), (DRIVER_ANCHOR, 1), (HELPER_ANCHOR, 1)):
        if text.count(anchor) != 1:
            print(f"REFUSED: anchor occurs {text.count(anchor)} times, expected 1")
            return 2
    text = text.replace(HELPER_ANCHOR, HELPER + HELPER_ANCHOR)
    text = text.replace(DRIVER_ANCHOR, DRIVER + DRIVER_ANCHOR)
    text = text.replace(ANCHOR_MAIN, MAIN_NEW)
    OUT.write_text(text)
    print(f"  wrote {OUT.name}  sha256 {hashlib.sha256(text.encode()).hexdigest()[:16]}")

    env = dict(__import__("os").environ)
    cargo = str(Path.home() / ".cargo" / "bin")
    if cargo not in env.get("PATH", ""):
        env["PATH"] = cargo + ":" + env.get("PATH", "")
    done = subprocess.run(["rustc", "--edition=2021", "-O", "-Awarnings", "--crate-name",
                           "cure1_control_probe", "-", "-o", str(HERE / "control-probe.bin")],
                          input=text, text=True, capture_output=True, timeout=300, env=env)
    if done.returncode:
        print(done.stderr[:4000])
        return 2
    print("  compiles")
    return 0


if __name__ == "__main__":
    sys.exit(main())
