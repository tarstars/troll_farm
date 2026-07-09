//! v1.50.1-latethreat: late observed enemy-near-own-tree raid response.
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{bfs_distances, State, Tree, Troll};

fn open_state() -> State {
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..16 {
        for y in 0..5 {
            walkable.insert((x, y));
        }
    }
    walkable.remove(&(0, 2));
    walkable.remove(&(15, 2));
    State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (15, 2),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 180,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

fn plan_for(st: &State) -> Plan {
    Plan {
        shack: st.my_shack,
        farm_d: bfs_distances(&st.walkable, &[st.my_shack]),
        opp: st.opp_shack,
        have_iron: false,
        turns_rem: 120,
        n: 2,
        farm_now: 0,
        nchop: 1,
        spec: (2, 3, 0, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (2, 3, 0, 2),
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
    }
}

fn troll(id: i32, x: i32, y: i32, ms: i32, cc: i32, hp: i32, chop: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: ms,
        carry_capacity: cc,
        harvest_power: hp,
        chop_power: chop,
        carry: [0; 6],
    }
}

fn chopper(id: i32, x: i32, y: i32) -> Troll {
    troll(id, x, y, 2, 3, 0, 2)
}

fn enemy_chopper(id: i32, x: i32, y: i32) -> Troll {
    troll(id, x, y, 2, 3, 0, 2)
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

// v1.50.1-latethreat was locally rejected; keep these as parked candidate checks.
#[ignore]
#[test]
fn enemy_near_own_tree_outranks_near_unthreatened_tree() {
    let mut st = open_state();
    st.trees = vec![banana(4, 2, 2), banana(7, 2, 2)];
    st.opp_trolls = vec![enemy_chopper(9, 7, 3)];
    let plan = plan_for(&st);
    let my = vec![chopper(2, 1, 2)];

    let cmds = assign(&st, &plan, &my);

    assert_eq!(
        cmds[&2], "MOVE 2 7 2",
        "threatened own-half tree should be defended: {}",
        cmds[&2]
    );
}

// v1.50.1-latethreat was locally rejected; keep these as parked candidate checks.
#[ignore]
#[test]
fn unthreatened_far_tree_stays_below_normal_roam_choice() {
    let mut st = open_state();
    st.trees = vec![banana(4, 2, 2), banana(7, 2, 2)];
    st.opp_trolls = vec![enemy_chopper(9, 13, 2)];
    let plan = plan_for(&st);
    let my = vec![chopper(2, 1, 2)];

    let cmds = assign(&st, &plan, &my);

    assert_eq!(
        cmds[&2], "MOVE 2 4 2",
        "without observed threat, the chopper should keep the normal roam target: {}",
        cmds[&2]
    );
}

// v1.50.1-latethreat was locally rejected; keep these as parked candidate checks.
#[ignore]
#[test]
fn early_threat_does_not_expand_roam() {
    let mut st = open_state();
    st.turn = 80;
    st.trees = vec![banana(4, 2, 2), banana(7, 2, 2)];
    st.opp_trolls = vec![enemy_chopper(9, 7, 3)];
    let plan = plan_for(&st);
    let my = vec![chopper(2, 1, 2)];

    let cmds = assign(&st, &plan, &my);

    assert_eq!(
        cmds[&2], "MOVE 2 4 2",
        "the threat response is late-only; early static widening already failed: {}",
        cmds[&2]
    );
}

// v1.50.1-latethreat was locally rejected; keep these as parked candidate checks.
#[ignore]
#[test]
fn doomed_occupied_threatened_tree_is_still_skipped() {
    let mut st = open_state();
    st.trees = vec![banana(4, 2, 2), banana(7, 2, 2)];
    st.opp_trolls = vec![enemy_chopper(9, 7, 2)];
    let plan = plan_for(&st);
    let my = vec![chopper(2, 1, 2)];

    let cmds = assign(&st, &plan, &my);

    assert_eq!(
        cmds[&2], "MOVE 2 4 2",
        "race() should still reject a tree the enemy finishes first: {}",
        cmds[&2]
    );
}
