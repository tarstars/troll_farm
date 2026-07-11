//! Pruned, sensible per-troll command enumeration — NOT all 8 compass directions, only moves
//! toward objects that matter (trees, the unit's own shack, iron cells), plus whichever of
//! CHOP/HARVEST/PLANT/MINE/PICK/DROP the engine's preconditions allow at the unit's CURRENT
//! cell. A unit issues exactly one command per turn (`game::engine::parse_cmds` keeps only the
//! first command seen per unit id), so MOVE and e.g. CHOP are alternatives here, never combined.

use std::collections::BTreeSet;

use crate::game::engine::{APPLE, BANANA, LEMON, PLUM};
use crate::game::state::{Cell, GameState, Unit};

/// The four plantable/harvestable fruit item slots (excludes IRON/WOOD, which are not seeds).
const FRUIT_TYPES: [(usize, &str); 4] = [
    (PLUM, "PLUM"),
    (LEMON, "LEMON"),
    (APPLE, "APPLE"),
    (BANANA, "BANANA"),
];

fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

/// All sensible commands a single unit could issue this turn: canonical (sorted, deduped via
/// BTreeSet), never the full 8-direction move fan.
pub fn troll_actions(state: &GameState, u: &Unit) -> Vec<String> {
    let mut acts: BTreeSet<String> = BTreeSet::new();
    let pos = u.pos();
    acts.insert(format!("WAIT {}", u.id));

    // MOVE toward every tree, the unit's own shack, and every iron cell — one MOVE per
    // distinct target; game::engine::next_cell resolves the actual reachable path at apply time.
    let mut targets: BTreeSet<Cell> = BTreeSet::new();
    for p in &state.plants {
        targets.insert(p.pos());
    }
    targets.insert(state.shacks[u.player as usize]);
    for &iron in &state.iron {
        targets.insert(iron);
    }
    for target in targets {
        if pos != target {
            acts.insert(format!("MOVE {} {} {}", u.id, target.0, target.1));
        }
    }

    // On a tree cell: CHOP and/or HARVEST when the engine's preconditions hold.
    if let Some(tree) = state.plants.iter().find(|p| p.pos() == pos) {
        if u.chop > 0 {
            acts.insert(format!("CHOP {}", u.id));
        }
        if u.hp > 0 && u.free() > 0 && tree.fruits > 0 {
            acts.insert(format!("HARVEST {}", u.id));
        }
    }

    // Near the unit's own shack (manhattan <= 1, matches engine::near_shack): PICK a carried-
    // home fruit out of the tent, or DROP whatever is currently carried.
    let player = u.player as usize;
    if manhattan(pos, state.shacks[player]) <= 1 {
        if u.free() > 0 {
            for &(idx, name) in &FRUIT_TYPES {
                if state.inventories[player][idx] > 0 {
                    acts.insert(format!("PICK {} {}", u.id, name));
                }
            }
        }
        if u.total() > 0 {
            acts.insert(format!("DROP {}", u.id));
        }
    }

    // On a walkable, plant-free cell while carrying a fruit/seed: PLANT it.
    if state.walkable.contains(&pos) && !state.plants.iter().any(|p| p.pos() == pos) {
        for &(idx, name) in &FRUIT_TYPES {
            if u.carry[idx] > 0 {
                acts.insert(format!("PLANT {} {}", u.id, name));
            }
        }
    }

    // Adjacent (manhattan == 1) to an iron cell: MINE.
    if u.chop > 0 && u.free() > 0 && state.iron.iter().any(|&i| manhattan(pos, i) == 1) {
        acts.insert(format!("MINE {}", u.id));
    }

    acts.into_iter().collect()
}

/// Cartesian product of `player`'s units' `troll_actions`, one command per unit: units taken in
/// id order, each unit's actions in their already-sorted order — canonical and deterministic.
pub fn joint_actions(state: &GameState, player: usize) -> Vec<Vec<String>> {
    let mut units: Vec<&Unit> = state
        .units
        .iter()
        .filter(|u| u.player as usize == player)
        .collect();
    units.sort_by_key(|u| u.id);

    let mut combos: Vec<Vec<String>> = vec![Vec::new()];
    for u in units {
        let acts = troll_actions(state, u);
        let mut next = Vec::with_capacity(combos.len() * acts.len().max(1));
        for combo in &combos {
            for a in &acts {
                let mut c = combo.clone();
                c.push(a.clone());
                next.push(c);
            }
        }
        combos = next;
    }
    combos
}
