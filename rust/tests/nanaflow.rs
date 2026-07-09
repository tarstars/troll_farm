//! v1.37.0-nanaflow (user replay findings #2+#3): BANANA TREE-FIRST harvesting + DIAGONAL
//! plant placement.
//! [helpers copied VERBATIM from tests/planner_tasks.rs]
//!
//! Finding #2: the printer used to PICK the tent (bands 50/49) before harvesting a ripe
//! seed tree (band 48, and only when the tent was already empty at that) — backwards. A
//! ripe tree now outranks the tent unconditionally (band 52, no inv[BANANA]==0 gate); the
//! tent becomes an accumulator, touched only once no ripe seed tree is reachable.
//!
//! Finding #3: the plant-cell chooser used to rank purely by map-distance, so it happily
//! planted on the four cells orthogonally adjacent to the shack — exactly the bank/DROP
//! cells every hand's carry trip needs. Diagonal-to-shack cells are the same map-distance
//! from the farm's edge but off that traffic path, so they should be preferred instead.
use std::collections::HashSet;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{State, Tree, Troll};

fn base_state() -> State {
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..8 {
        for y in 0..5 {
            walkable.insert((x, y));
        }
    }
    walkable.remove(&(0, 2)); // my shack cell (not walkable)
    State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (7, 2),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 50,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

fn base_plan() -> Plan {
    // farm_d: BFS map distances from the shack over the 8x5 open room (shack at (0,2))
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..8 {
        for y in 0..5 {
            walkable.insert((x, y));
        }
    }
    walkable.remove(&(0, 2));
    let farm_d = troll_farm::botmain::bfs_distances(&walkable, &[(0, 2)]);
    Plan {
        shack: (0, 2),
        farm_d,
        opp: (7, 2),
        have_iron: false,
        turns_rem: 250,
        n: 2,
        farm_now: 0,
        nchop: 1,
        spec: (2, 2, 0, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (2, 2, 0, 2),
        cost: [0; 6],
        train_now: false,
        need_iron: false,
        need_fund: [false; 3],
        farm_r: 2,
        farm_cap: 12,
        fell_size: 2,
        farm_fell: 2,
        chop_r: 5,
        starter_chop: true,
        liquidation: false,
        base_trees: 0,
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
    }
}

fn starter(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 1,
        harvest_power: 1,
        chop_power: 1,
        carry: [0; 6],
    }
}
fn banana(x: i32, y: i32, size: i32) -> Tree {
    Tree {
        tree_type: "BANANA".into(),
        x,
        y,
        size,
        health: 2 + size,
        fruits: 0,
        cooldown: 0,
    }
}

#[test]
fn ripe_seed_tree_outranks_banked_tent_stock() {
    // The tent already holds 5 banked bananas (BANANA=index 3) and a ripe banana tree
    // (fruits=3) sits at (4,2), well within the farm. The starter is shack-adjacent at
    // (1,2), free capacity 1. Pre-fix: PICK's band (50) beats nothing else, because the
    // seed-tree-seek band (48) is gated on inv[BANANA]==0 and the tent is non-empty — so
    // the starter emits "PICK 0 BANANA" and never even looks at the ripe tree. Post-fix:
    // the ripe tree's band (52, no gate) outranks PICK (50), so the starter heads for the
    // tree instead — the tent becomes a fallback the full->bank flow drains later.
    let mut st = base_state();
    let mut t = banana(4, 2, 4);
    t.fruits = 3;
    st.trees = vec![t];
    st.my_inventory[3] = 5; // banked bananas already sitting in the tent
    let plan = base_plan();
    let my = vec![starter(0, 1, 2)];
    let cmds = assign(&st, &plan, &my);
    assert!(
        cmds[&0].contains("4 2"),
        "starter should head for the ripe seed tree ahead of the tent: {}",
        &cmds[&0]
    );
}

#[test]
fn plant_prefers_diagonal_cell_over_orthogonal_bank_cell() {
    // Restrict the walkable farm to exactly two candidate plant cells so the new geometry
    // terms are isolated from any other tie: (1,2) is orthogonally adjacent to the shack
    // (farm_d==1 -- one of the four bank/DROP cells) and (1,1) is diagonal to the shack
    // (farm_d==2 -- off the bank-traffic path). The starter stands ON the shack cell so its
    // own travel distance to each candidate equals farm_d exactly (map-distance 1 vs 2).
    // Pre-fix: the chooser ranks by map-distance alone, so (1,2)'s distance-1 beats (1,1)'s
    // distance-2 and it plants on the bank cell. Post-fix: the +3 bank-adjacency penalty and
    // -1 diagonal bonus flip the ranking to (1,1).
    let mut st = base_state();
    st.walkable = [(1, 2), (1, 1)].into_iter().collect();
    let mut plan = base_plan();
    plan.farm_d = troll_farm::botmain::bfs_distances(&st.walkable, &[plan.shack]);
    let mut s = starter(0, 0, 2); // standing on the shack cell itself
    s.carry = [0, 0, 0, 1, 0, 0]; // carrying a banana seed to plant
    let my = vec![s];
    let cmds = assign(&st, &plan, &my);
    assert!(
        cmds[&0].contains("1 1"),
        "should prefer the diagonal cell, off the bank-traffic path: {}",
        &cmds[&0]
    );
    assert!(
        !cmds[&0].contains("MOVE 0 1 2"),
        "must not congest the orthogonal bank/DROP cell: {}",
        &cmds[&0]
    );
}
