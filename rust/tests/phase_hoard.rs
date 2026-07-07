//! B2: Hoard suppresses felling except the denial emergency (enemy within map-dist 2).
use std::collections::HashSet;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{State, Tree, Troll};

// [copied VERBATIM from tests/planner_tasks.rs, except base_plan() sets phase: Phase::Hoard]

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
        phase: Phase::Hoard,
    }
}

fn starter(id: i32, x: i32, y: i32) -> Troll {
    Troll { id, x, y, movement_speed: 1, carry_capacity: 1, harvest_power: 1, chop_power: 1, carry: [0; 6] }
}
fn chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll { id, x, y, movement_speed: 2, carry_capacity: 2, harvest_power: 0, chop_power: 2, carry: [0; 6] }
}
fn banana(x: i32, y: i32, size: i32) -> Tree {
    Tree { tree_type: "BANANA".into(), x, y, size, health: 2 + size, fruits: 0, cooldown: 0 }
}

#[test]
fn hoard_suppresses_fells_without_threat() {
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2)];
    st.opp_trolls = vec![chopper(9, 6, 2)];
    let cmds = assign(&st, &base_plan(), &[starter(0, 1, 2), chopper(2, 4, 2)]);
    assert!(!cmds[&2].starts_with("CHOP") && !cmds[&2].contains("3 2"),
        "hoard must not fell an unthreatened tree: {}", &cmds[&2]);
}

#[test]
fn hoard_denial_emergency_fells_threatened_tree() {
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2)];
    st.opp_trolls = vec![chopper(9, 4, 2)]; // enemy 1 step from the tree
    let cmds = assign(&st, &base_plan(), &[starter(0, 1, 2), chopper(2, 4, 2)]);
    assert!(cmds[&2] == "CHOP 2" || cmds[&2].contains("3 2"),
        "threatened tree must be denial-felled: {}", &cmds[&2]);
}

// B2.1 gatekeeper fix (Scale meta, wood=0 in 12/12 games): during Hoard, the wallet band
// (62*BAND, any ripe fruit) unconditionally outranked iron-funding (fund_hi=45, since
// want_chopper is forced false under Scale) — so nobody ever mined, the ladder's chopper slot
// (cost[IRON]=7) never trained, and wood stayed 0 for the entire game in every sampled game.
// The starter must prefer mining iron it's already adjacent to over chasing a competing ripe
// fruit tree while the ladder is iron-short.
#[test]
fn hoard_mines_iron_when_ladder_is_iron_short() {
    let mut st = base_state();
    st.iron_cells.insert((3, 2));
    let mut b = banana(5, 2, 4);
    b.fruits = 3;
    st.trees = vec![b];
    let mut plan = base_plan();
    plan.phase = Phase::Hoard;
    plan.have_iron = true;
    plan.need_iron = true;
    plan.want_feeder = true;
    plan.cost = [3, 3, 3, 0, 7, 0];
    let cmds = assign(&st, &plan, &[starter(0, 2, 2)]);
    assert_eq!(
        cmds[&0], "MINE 0",
        "starter adjacent to iron must mine it over chasing a competing ripe fruit during Hoard: {}",
        &cmds[&0]
    );
}
