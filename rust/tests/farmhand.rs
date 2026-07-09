//! v1.49.0-farmhand: re-arm the cheap third hand, but keep its fruit errands
//! local to the farm ring so it does not repeat the T-hand tourist path.
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{plan_with_meta, Meta, Phase, Plan};
use troll_farm::botmain::{bfs_distances, State, Tree, Troll};

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
    let st = base_state();
    Plan {
        shack: st.my_shack,
        farm_d: bfs_distances(&st.walkable, &[st.my_shack]),
        opp: st.opp_shack,
        have_iron: false,
        turns_rem: 250,
        n: 3,
        farm_now: 0,
        nchop: 1,
        spec: (2, 2, 0, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (1, 1, 1, 0),
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

fn farmhand(id: i32, x: i32, y: i32) -> Troll {
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

fn banana(x: i32, y: i32, size: i32, fruits: i32) -> Tree {
    Tree {
        tree_type: "BANANA".into(),
        x,
        y,
        size,
        health: 2 + size,
        fruits,
        cooldown: 0,
    }
}

// v1.49.0-farmhand was locally rejected; keep these as parked candidate checks.
#[ignore]
#[test]
fn tempo_wants_third_hand_again() {
    let mut st = base_state();
    st.turn = 50;
    st.my_inventory = [3, 3, 3, 0, 0, 0];
    let my = vec![starter(0, 1, 2), chopper(2, 4, 2)];

    let plan = plan_with_meta(&st, &my, Meta::Tempo);

    assert!(plan.want_feeder, "Tempo should re-arm the cheap farm hand");
    assert_eq!(plan.train_spec, (1, 1, 1, 0));
    assert!(
        plan.train_now,
        "fruit wallet should train the hand immediately"
    );
}

// v1.49.0-farmhand was locally rejected; keep these as parked candidate checks.
#[ignore]
#[test]
fn farmhand_takes_local_seed_tree_before_tent_stock() {
    let mut st = base_state();
    st.trees = vec![banana(2, 2, 4, 3)];
    st.my_inventory[3] = 5;
    let plan = base_plan();
    let my = vec![farmhand(4, 1, 2)];

    let cmds = assign(&st, &plan, &my);

    assert!(
        cmds[&4].contains("2 2"),
        "farmhand should take local seed fruit before tent stock: {}",
        cmds[&4]
    );
}

// v1.49.0-farmhand was locally rejected; keep these as parked candidate checks.
#[ignore]
#[test]
fn farmhand_uses_tent_stock_before_far_seed_tree() {
    let mut st = base_state();
    st.trees = vec![banana(4, 2, 4, 3)];
    st.my_inventory[3] = 5;
    let plan = base_plan();
    let my = vec![farmhand(4, 1, 2)];

    let cmds = assign(&st, &plan, &my);

    assert_eq!(
        cmds[&4], "PICK 4 BANANA",
        "farmhand must not cross the map for premium printer work: {}",
        cmds[&4]
    );
}

// v1.49.0-farmhand was locally rejected; keep these as parked candidate checks.
#[ignore]
#[test]
fn farmhand_skips_far_idle_fruit() {
    let mut st = base_state();
    st.trees = vec![banana(4, 2, 4, 3)];
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap;
    let my = vec![farmhand(4, 1, 2)];

    let cmds = assign(&st, &plan, &my);

    assert!(
        !cmds[&4].contains("4 2"),
        "farmhand idle-fruit must stay local, got: {}",
        cmds[&4]
    );
}
