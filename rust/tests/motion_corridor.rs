//! Motion solver TDD — corridor unload (user scenario 2026-07-06).
//! A 1-cell-wide corridor to the camp with N full trolls. The motion policy must unload them
//! EFFICIENTLY by exploiting the engine's SWAP rule (empty troll heads out, full troll heads in →
//! they swap, pipelining the single drop-cell). Verified optimal for a 1-wide corridor.
//!
//! These tests pin the REQUIRED behavior (they exercise the sim `step`, whose move rules were
//! empirically confirmed vs the real engine: speed ≤ ms, and adjacent cross-steps swap). When the
//! real solver replaces the ad-hoc bank/park logic in decide_elite, it must keep these green.
use troll_farm::game::engine::{step, WOOD};
use troll_farm::game::state::{from_ascii, GameState, Unit};

/// Run the "full → drop-cell, empty → exit" corridor policy for `max_t` turns; return
/// (turns_until_all_unloaded, max_simultaneous_stuck-full-not-dropping).
fn run_corridor(
    g: &mut GameState,
    drop_cell: (i32, i32),
    exit: (i32, i32),
    full_wood: i32,
    max_t: i32,
) -> i32 {
    for t in 0..max_t {
        let mut cmds0 = Vec::new();
        for u in g.units.iter().filter(|u| u.player == 0) {
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
        step(g, &cmds0, &[]);
        if g.inventories[0][WOOD] >= full_wood {
            return t + 1;
        }
    }
    max_t + 1 // failed to unload within max_t
}

fn corridor_state(n: usize) -> GameState {
    // shack0 (0,0) unwalkable; corridor (1..6,0) walkable; shack1 (7,0).
    let mut g = from_ascii(&["0......1"]);
    g.units = (0..n)
        .map(|i| Unit {
            id: (i as i32) * 2,
            player: 0,
            x: 1 + i as i32,
            y: 0,
            ms: 1,
            cc: 2,
            hp: 1,
            chop: 1,
            carry: [0, 0, 0, 0, 0, 2],
        })
        .collect();
    g.next_id = (n as i32) * 2;
    g
}

#[test]
fn corridor_unloads_three_full_trolls_optimally() {
    // 3 full trolls (6 wood) in a 1-wide corridor unload in 5 turns via swaps (optimal:
    // drop, swap, drop, swap, drop). Regression guard: if the swap rule breaks or the policy
    // fails to head empties out, this jumps well past 5.
    let mut g = corridor_state(3);
    let turns = run_corridor(&mut g, (1, 0), (6, 0), 6, 12);
    assert_eq!(
        turns, 5,
        "3-troll corridor should unload in 5 turns (drop/swap pipeline)"
    );
}

#[test]
fn corridor_unloads_two_full_trolls() {
    // 2 full trolls: drop, swap, drop = 3 turns.
    let mut g = corridor_state(2);
    let turns = run_corridor(&mut g, (1, 0), (6, 0), 4, 12);
    assert_eq!(turns, 3, "2-troll corridor should unload in 3 turns");
}
