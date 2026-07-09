//! R6b joint task assignment — tests: shuffle invariance, contested-resource resolution,
//! and priority sanity (the value bands must reproduce the cascade's hierarchy).
use std::collections::HashSet;
use troll_farm::botmain::ownership;
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
        pressure: ownership::Pressure::default(),
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
fn chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 2,
        carry_capacity: 2,
        harvest_power: 0,
        chop_power: 2,
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
fn shuffle_invariance() {
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2), banana(5, 1, 3)];
    let plan = base_plan();
    let a = vec![starter(0, 1, 2), chopper(2, 4, 2)];
    let b = vec![chopper(2, 4, 2), starter(0, 1, 2)];
    assert_eq!(
        assign(&st, &plan, &a),
        assign(&st, &plan, &b),
        "troll order changed the plan"
    );
}

#[test]
fn contested_tree_goes_to_the_better_troll_without_duplication() {
    // ONE fellable tree; both trolls chop-capable. The chopper's fell band (70) beats the
    // starter's chop-help band (40): the chopper takes it, the starter does NOT target it.
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2)];
    let plan = base_plan();
    let my = vec![starter(0, 2, 2), chopper(2, 4, 2)];
    let cmds = assign(&st, &plan, &my);
    let c2 = &cmds[&2];
    assert!(
        c2 == "MOVE 2 3 2" || c2 == "CHOP 2",
        "chopper should take the tree, got {c2}"
    );
    assert!(
        !cmds[&0].contains("3 2"),
        "starter must not target the same tree: {}",
        &cmds[&0]
    );
}

#[test]
fn priorities_hold() {
    // full chopper banks; starter carrying a banana plants it in the farm radius.
    let mut st = base_state();
    st.trees = vec![banana(5, 1, 2)];
    let plan = base_plan();
    let mut ch = chopper(2, 5, 2);
    ch.carry = [0, 0, 0, 0, 0, 2]; // full (cc=2)
    let mut s = starter(0, 1, 2);
    s.carry = [0, 0, 0, 1, 0, 0]; // carrying a banana (cc=1 -> full, but plant outranks bank)
    let my = vec![s, ch];
    let cmds = assign(&st, &plan, &my);
    assert!(
        cmds[&2].starts_with("DROP") || cmds[&2].starts_with("MOVE"),
        "full chopper should bank: {}",
        &cmds[&2]
    );
    assert!(
        cmds[&0].starts_with("PLANT") || cmds[&0].starts_with("MOVE"),
        "banana-carrying starter should plant: {}",
        &cmds[&0]
    );
    // and it must not be a DROP (banking the seed would be the old full->bank bug)
    assert!(
        !cmds[&0].starts_with("DROP"),
        "starter must plant, not bank the seed"
    );
}
