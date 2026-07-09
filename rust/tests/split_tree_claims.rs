//! v1.46.0-splitclaims: a ripe tree can be both a fruit target and a wood target when
//! the fruit worker reaches it first. Same-resource tree claims remain exclusive.
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
    walkable.remove(&(0, 2));
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
        door: None,
        door_d: None,
        ring: vec![],
        raid: false,
    }
}

fn gatherer(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 1,
        harvest_power: 1,
        chop_power: 0,
        carry: [0; 6],
    }
}

fn slow_chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 2,
        harvest_power: 0,
        chop_power: 2,
        carry: [0; 6],
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

fn apple(x: i32, y: i32, fruits: i32) -> Tree {
    Tree {
        tree_type: "APPLE".into(),
        x,
        y,
        size: 2,
        health: 4,
        fruits,
        cooldown: 0,
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
fn gatherer_can_claim_near_apple_also_claimed_for_wood() {
    let mut st = base_state();
    st.trees = vec![apple(2, 2, 2), apple(5, 2, 2)];
    let plan = base_plan();
    let my = vec![gatherer(0, 1, 2), slow_chopper(2, 3, 1)];

    let cmds = assign(&st, &plan, &my);

    assert!(
        cmds[&0].contains("2 2"),
        "gatherer should take the adjacent apple instead of being forced to the far apple, got: {}",
        cmds[&0]
    );
    assert!(
        cmds[&2].contains("2 2"),
        "chopper should keep its wood claim on the same tree, got: {}",
        cmds[&2]
    );
}

#[test]
fn equal_eta_fruit_and_wood_claims_still_conflict() {
    let mut st = base_state();
    st.trees = vec![apple(2, 2, 2), apple(5, 2, 2)];
    let plan = base_plan();
    let my = vec![gatherer(0, 1, 2), slow_chopper(2, 3, 2)];

    let cmds = assign(&st, &plan, &my);

    assert!(
        !cmds[&0].contains("2 2"),
        "same-ETA fruit/wood claims should stay exclusive to avoid movement fights, got: {}",
        cmds[&0]
    );
}

#[test]
#[ignore = "v1.51.1-fruitstand local-rejected; keep as documentation for the closed stall mechanism"]
fn standing_fruit_claim_blocks_same_tree_wood_claim() {
    let mut st = base_state();
    st.trees = vec![apple(2, 2, 2), apple(5, 2, 2)];
    let plan = base_plan();
    let my = vec![gatherer(0, 2, 2), slow_chopper(2, 3, 2)];

    let cmds = assign(&st, &plan, &my);

    assert_eq!(
        cmds[&0], "HARVEST 0",
        "standing gatherer should keep the ripe fruit action, got: {}",
        cmds[&0]
    );
    assert!(
        !cmds[&2].contains("2 2"),
        "chopper must not target a ripe tree occupied by our fruit worker, got: {}",
        cmds[&2]
    );
}

#[test]
fn wood_claims_remain_exclusive() {
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2)];
    let plan = base_plan();
    let my = vec![starter(0, 2, 2), slow_chopper(2, 4, 2)];

    let cmds = assign(&st, &plan, &my);

    assert!(
        cmds[&2].contains("3 2"),
        "chopper should keep the fell target, got: {}",
        cmds[&2]
    );
    assert!(
        !cmds[&0].contains("3 2"),
        "starter chop-help must still not duplicate the wood target, got: {}",
        cmds[&0]
    );
}
