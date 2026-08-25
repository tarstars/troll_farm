#!/usr/bin/env python3
r"""G-4c.2 — the two OBSERVED FIRINGS, specified by codex_1.

  * `DEAD_OR_UNREACHABLE` — a live plant on a disconnected walkable island;
  * `ROUND_TRIP_CLOCK`    — one valid reachable state early (PASS/ACCEPT) and at turn 300 (REJECT).

Built from the ACCEPTED instrument (`instrumented-chop4c.rs`, frozen at G-4c.1), not from a
fresh copy, so the rows that appear are emitted by the very taps under review — an observed
firing produced by a different build would prove nothing about the instrument that will report
the distribution.

The states are synthetic (Amendment 1 permits it) but VALID: a 4x4 walkable grid with a
detached island cell for the first case, and one ordinary reachable tree evaluated at two turns
for the second. Only `view.turn` differs between the ROUND_TRIP_CLOCK pair, which is what makes
it a control rather than two unrelated observations.
"""
import hashlib, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
INSTR = REPO / "claude_1/chop4c/instrumented-chop4c.rs"
OUT = REPO / "claude_1/chop4c/firing-probe.rs"

ANCHOR = '''        struct MoisanBot;'''

PROBE = '''        struct MoisanBot;
//C4C_FIRING_BEGIN
        pub fn c4c_firing_probe(){
    use crate::game::types::*;
    use std::collections::BTreeSet;
    // island case: unit at (0,0) on a connected 3x3 block; the plant sits on (3,3), a walkable
    // cell with no walkable orthogonal neighbour, so BFS from the unit never reaches it.
    let mut walkable=BTreeSet::new();
    for x in 0..3{for y in 0..3{walkable.insert((x,y));}}
    walkable.insert((3,3));
    let unit=Unit{id:0,player:0,cell:(0,0),
        stats:Stats{movement_speed:1,carry_capacity:3,harvest_power:1,chop_power:1},
        carry:[0;ITEM_COUNT]};
    let island=Plant{kind:PlantKind::Apple,cell:(3,3),size:4,health:20,fruits:0,cooldown:0};
    let view=GameState{width:4,height:4,walkable:walkable.clone(),shacks:[(0,0),(2,2)],
        inventories:[[0;ITEM_COUNT];2],units:vec![unit.clone()],plants:vec![island],
        scores:[0,0],turn:1,next_id:5,iron:BTreeSet::new(),water:BTreeSet::new()};
    eprintln!("C4CFIRE case=DEAD_OR_UNREACHABLE_island");
    let _=MoisanBot::chop_candidates(&view,&unit,None);
    // clock case: ONE valid reachable state, evaluated at turn 1 and at turn 300. Only
    // view.turn differs, so any change in the terminal clause is caused by the clock alone.
    let near=Plant{kind:PlantKind::Apple,cell:(1,1),size:4,health:20,fruits:0,cooldown:0};
    let mut early=view.clone();
    early.plants=vec![near.clone()];
    early.turn=1;
    eprintln!("C4CFIRE case=ROUND_TRIP_CLOCK_early");
    let _=MoisanBot::chop_candidates(&early,&unit,None);
    let mut late=early.clone();
    late.turn=300;
    eprintln!("C4CFIRE case=ROUND_TRIP_CLOCK_turn300");
    let _=MoisanBot::chop_candidates(&late,&unit,None);
    }
//C4C_FIRING_END'''

OLD_ENTRY = '''fn main(){
    let stdin=io::stdin();'''
NEW_ENTRY = '''fn main(){
    if std::env::var("C4C_FIRING_PROBE").is_ok(){crate::bot::moisan::c4c_firing_probe();return;}
    let stdin=io::stdin();'''


def main():
    src = INSTR.read_text()
    if src.count(ANCHOR) != 1 or src.count(OLD_ENTRY) != 1:
        print("REFUSING: anchors not unique in the accepted instrument")
        return 1
    out = src.replace(ANCHOR, PROBE).replace(OLD_ENTRY, NEW_ENTRY)
    a = out.index("//C4C_FIRING_BEGIN\n")
    b = out.index("//C4C_FIRING_END") + len("//C4C_FIRING_END")
    stripped = (out[:a] + out[b:]).replace(
        '    if std::env::var("C4C_FIRING_PROBE").is_ok(){crate::bot::moisan::c4c_firing_probe();return;}\n', "")
    if stripped.replace("\n\n", "\n") != src.replace("\n\n", "\n"):
        print("REFUSING: firing probe changed the accepted instrument outside its additions")
        return 1
    OUT.write_text(out)
    print(f"wrote {OUT.relative_to(REPO)} (from accepted instrument "
          f"{hashlib.sha256(src.encode()).hexdigest()[:16]}…)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
