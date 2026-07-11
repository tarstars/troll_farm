//! yannbot Task 2 core tests: shack_dist / choose_type_to_cut / effective_cd, exercised
//! through a minimal all-walkable grid fixture built directly from `State`'s public
//! fields — no dependency on planner/tactics/ownership, mirroring yann.rs's own isolation
//! (spec: docs/superpowers/specs/2026-07-11-yannbot-design.md).
//!
//! NOTE: the task brief's Step-1 skeleton imports `troll_farm::botmain::state::*`, but
//! `botmain.rs` declares `mod state;` (private) and only re-exports its items via
//! `pub use state::*;` at the `botmain` level (verified: `botmain::state::*` fails to
//! compile from an external test crate with E0603 "module `state` is private" — every
//! existing integration test in this crate imports state types via
//! `troll_farm::botmain::{...}` instead, e.g. tests/frontdoor.rs, tests/threatfell.rs).
//! Adapted the import to `troll_farm::botmain::*` accordingly; the fixtures and every
//! hand-computed expectation below are unchanged from the brief.
use std::collections::HashSet;
use troll_farm::botmain::yann::*;
use troll_farm::botmain::*;

// all-walkable w x h grid minus the two shack cells; empty everything else.
fn grid_state(w: i32, h: i32, my_shack: Cell, opp_shack: Cell) -> State {
    let mut walkable = HashSet::new();
    for x in 0..w {
        for y in 0..h {
            let c = (x, y);
            if c != my_shack && c != opp_shack {
                walkable.insert(c);
            }
        }
    }
    State {
        walkable,
        my_shack,
        opp_shack,
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: Vec::new(),
        my_trolls: Vec::new(),
        opp_trolls: Vec::new(),
        turn: 1,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

// size 2, health = base + slope*size (PLUM/LEMON base 4 slope 2 -> 8; APPLE 8/3 -> 14;
// BANANA 2/1 -> 4), fruits 0, cooldown 5.
fn mk_tree(ty: &str, x: i32, y: i32) -> Tree {
    let (base, slope) = match ty {
        "PLUM" | "LEMON" => (4, 2),
        "APPLE" => (8, 3),
        "BANANA" => (2, 1),
        _ => panic!("mk_tree: unknown type {}", ty),
    };
    let size = 2;
    Tree {
        tree_type: ty.to_string(),
        x,
        y,
        size,
        health: base + slope * size,
        fruits: 0,
        cooldown: 5,
    }
}

#[test]
fn type_to_cut_prefers_nearer_cluster() {
    let mut s = grid_state(10, 5, (0, 2), (9, 2));
    // two lemons at dist 2 and 3; two plums at dist 5 and 6 (dist = manhattan here)
    s.trees.push(mk_tree("LEMON", 2, 2));
    s.trees.push(mk_tree("LEMON", 3, 2));
    s.trees.push(mk_tree("PLUM", 5, 2));
    s.trees.push(mk_tree("PLUM", 6, 2));
    assert_eq!(choose_type_to_cut(&s), LEMON);
    // move the plums adjacent -> PLUM wins
    s.trees[2].x = 1;
    s.trees[3].x = 1;
    s.trees[3].y = 1;
    assert_eq!(choose_type_to_cut(&s), PLUM);
}

#[test]
fn type_with_no_trees_never_chosen() {
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    s.trees.push(mk_tree("PLUM", 4, 1));
    assert_eq!(choose_type_to_cut(&s), PLUM);
}

#[test]
fn effective_cd_uses_water_adjacency() {
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    let t = mk_tree("BANANA", 3, 1);
    assert_eq!(effective_cd(&s, &t), 6);
    s.water_cells.insert((3, 2));
    assert_eq!(effective_cd(&s, &t), 4); // 6 - 2
}

#[test]
fn tree_grows_during_travel() {
    // banana s2 h4 cd2, base 6, no opp: t1 cd->1; t2 cd->0 grow s3 h5 cd=6; t3 cd->5
    assert_eq!(tree_at_arrival(2, 4, 2, 6, BANANA, 0, 3), Some((3, 5)));
}

#[test]
fn opponent_chopping_kills_before_arrival() {
    // banana s2 h4, opp chop 2: t1 h2; t2 h0 -> dead
    assert_eq!(tree_at_arrival(2, 4, 5, 6, BANANA, 2, 3), None);
}

#[test]
fn size_caps_at_four() {
    // lemon s4 h12 cd1 base8: t1 cd0 -> size stays 4 (no growth), cd resets
    assert_eq!(tree_at_arrival(4, 12, 1, 8, LEMON, 0, 2), Some((4, 12)));
}

#[test]
fn zero_travel_returns_current() {
    assert_eq!(tree_at_arrival(3, 9, 4, 8, PLUM, 5, 0), Some((3, 9)));
}
