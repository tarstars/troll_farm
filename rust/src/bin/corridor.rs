//! Corridor unload experiment (user scenario 2026-07-06): a 1-cell-wide corridor to the camp,
//! N full trolls inside. Verify — against the REAL engine rules (via the sim's `step`) — whether a
//! simple "full → drop-cell, empty → exit" policy unloads efficiently by triggering SWAPs, or
//! whether it blocks and needs an explicit sequencer. This grounds the motion-solver design/tests.
use troll_farm::game::engine::{step, WOOD};
use troll_farm::game::state::{from_ascii, Unit};

fn main() {
    // shack0 at (0,0) [unwalkable]; corridor (1..5,0) walkable; shack1 at (6,0).
    let mut g = from_ascii(&["0.....1"]);
    let drop_cell = (1, 0); // the ONE shack-adjacent cell (manhattan 1 from shack0)
    let exit = (5, 0);
    // 3 full trolls (carry 2 wood each), lined up in the corridor, nearest first.
    g.units = vec![
        Unit {
            id: 0,
            player: 0,
            x: 1,
            y: 0,
            ms: 1,
            cc: 2,
            hp: 1,
            chop: 1,
            carry: [0, 0, 0, 0, 0, 2],
        },
        Unit {
            id: 2,
            player: 0,
            x: 2,
            y: 0,
            ms: 1,
            cc: 2,
            hp: 1,
            chop: 1,
            carry: [0, 0, 0, 0, 0, 2],
        },
        Unit {
            id: 4,
            player: 0,
            x: 3,
            y: 0,
            ms: 1,
            cc: 2,
            hp: 1,
            chop: 1,
            carry: [0, 0, 0, 0, 0, 2],
        },
    ];
    g.next_id = 5;
    let banked0 = |g: &troll_farm::game::state::GameState| g.inventories[0][WOOD];

    println!("corridor unload: 3 full trolls at (1,0)(2,0)(3,0), shack (0,0), drop-cell (1,0)");
    for t in 0..12 {
        // POLICY: full troll -> DROP if on drop-cell else MOVE to drop-cell; empty -> MOVE to exit.
        let mut cmds0 = Vec::new();
        let mut before = Vec::new();
        for u in g.units.iter().filter(|u| u.player == 0) {
            before.push((u.id, (u.x, u.y), u.carry[WOOD]));
            if u.carry[WOOD] > 0 {
                if (u.x, u.y) == drop_cell {
                    cmds0.push(format!("DROP {}", u.id));
                } else {
                    cmds0.push(format!("MOVE {} {} {}", u.id, drop_cell.0, drop_cell.1));
                }
            } else {
                cmds0.push(format!("MOVE {} {} {}", u.id, exit.0, exit.1));
            }
        }
        step(&mut g, &cmds0, &[]);
        // report
        let after: Vec<(i32, (i32, i32))> = g
            .units
            .iter()
            .filter(|u| u.player == 0)
            .map(|u| (u.id, (u.x, u.y)))
            .collect();
        let moved = before
            .iter()
            .filter(|(id, p, _)| {
                after
                    .iter()
                    .find(|(aid, _)| aid == id)
                    .map(|(_, ap)| ap != p)
                    .unwrap_or(false)
            })
            .count();
        let stuck = before
            .iter()
            .filter(|(id, p, c)| {
                *c > 0 // was carrying (intended to move to drop) or empty (intended exit)
                && after.iter().find(|(aid, _)| aid == id).map(|(_, ap)| ap == p).unwrap_or(false)
                && *p != drop_cell // being at the drop cell + dropping is not "stuck"
            })
            .count();
        println!(
            "t{:2}: {:30} banked={} moved={} stuck(full,not-dropping)={}",
            t,
            before
                .iter()
                .map(|(id, p, c)| format!(
                    "{}@{},{}{}",
                    id,
                    p.0,
                    p.1,
                    if *c > 0 { "*" } else { "" }
                ))
                .collect::<Vec<_>>()
                .join(" "),
            banked0(&g),
            moved,
            stuck
        );
        if banked0(&g) >= 6 {
            println!("ALL UNLOADED (6 wood) by end of t{} — {} turns", t, t + 1);
            break;
        }
    }
}
