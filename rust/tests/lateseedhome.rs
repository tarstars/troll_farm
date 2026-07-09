//! v1.52.0-lateseedhome: after t150, when the live Tempo farm is below the seed-reserve
//! floor and tent bananas are already banked, restart the local plant loop before walking
//! to a remote ripe seed tree. Early tree-first behavior stays intact.
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{bfs_distances, State, Tree, Troll, BANANA};

fn base_state(turn: i32) -> State {
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
        turn,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

fn base_plan(st: &State) -> Plan {
    Plan {
        shack: st.my_shack,
        farm_d: bfs_distances(&st.walkable, &[st.my_shack]),
        opp: st.opp_shack,
        have_iron: false,
        turns_rem: 300 - st.turn + 1,
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

fn starter(id: i32, x: i32, y: i32) -> Troll {
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

fn ripe_banana(x: i32, y: i32) -> Tree {
    Tree {
        tree_type: "BANANA".into(),
        x,
        y,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    }
}

#[test]
#[ignore = "v1.52.0-lateseedhome arena-reverted; kept as parked candidate documentation"]
fn late_thin_farm_picks_tent_seed_before_remote_seed_tree() {
    let mut st = base_state(160);
    st.my_inventory[BANANA] = 5;
    st.trees = vec![ripe_banana(4, 2)];
    let plan = base_plan(&st);
    let cmds = assign(&st, &plan, &[starter(0, 1, 2)]);
    assert_eq!(
        cmds[&0], "PICK 0 BANANA",
        "late thin farm with tent seed should restart local planting, got {}",
        cmds[&0]
    );
}

#[test]
#[ignore = "v1.52.0-lateseedhome arena-reverted; kept as parked candidate documentation"]
fn early_seed_tree_still_outranks_tent_stock() {
    let mut st = base_state(100);
    st.my_inventory[BANANA] = 5;
    st.trees = vec![ripe_banana(4, 2)];
    let plan = base_plan(&st);
    let cmds = assign(&st, &plan, &[starter(0, 1, 2)]);
    assert!(
        cmds[&0].contains("4 2"),
        "pre-t150 tree-first seed rule should remain intact, got {}",
        cmds[&0]
    );
}

#[test]
#[ignore = "v1.52.0-lateseedhome arena-reverted; kept as parked candidate documentation"]
fn late_non_thin_farm_keeps_tree_first_seed_rule() {
    let mut st = base_state(160);
    st.my_inventory[BANANA] = 5;
    st.trees = vec![ripe_banana(4, 2)];
    let mut plan = base_plan(&st);
    plan.base_trees = 2;
    plan.farm_now = 2;
    let cmds = assign(&st, &plan, &[starter(0, 1, 2)]);
    assert!(
        cmds[&0].contains("4 2"),
        "late farm at reserve floor should still prefer the ripe seed tree, got {}",
        cmds[&0]
    );
}
