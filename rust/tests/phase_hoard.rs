//! B2: Hoard suppresses felling except the denial emergency (enemy within map-dist 2).
use std::collections::HashSet;
use troll_farm::botmain::ownership;
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
fn hoard_suppresses_fells_without_threat() {
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2)];
    st.opp_trolls = vec![chopper(9, 6, 2)];
    let cmds = assign(&st, &base_plan(), &[starter(0, 1, 2), chopper(2, 4, 2)]);
    assert!(
        !cmds[&2].starts_with("CHOP") && !cmds[&2].contains("3 2"),
        "hoard must not fell an unthreatened tree: {}",
        &cmds[&2]
    );
}

#[test]
fn hoard_denial_emergency_fells_threatened_tree() {
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2)];
    st.opp_trolls = vec![chopper(9, 4, 2)]; // enemy 1 step from the tree
    let cmds = assign(&st, &base_plan(), &[starter(0, 1, 2), chopper(2, 4, 2)]);
    assert!(
        cmds[&2] == "CHOP 2" || cmds[&2].contains("3 2"),
        "threatened tree must be denial-felled: {}",
        &cmds[&2]
    );
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

// Gatekeeper verdict #2 (post-e09ac48): e09ac48 fixed the wallet-vs-funding priority bug ONLY
// for iron (band 64/63). The identical bug still gates PLUM/LEMON/APPLE: need_fund's targeted
// candidate (planner.rs ~241-248, fund_lo=44*BAND under Scale) is still dominated by the generic
// Hoard wallet band (62*BAND, ANY ripe fruit) at planner.rs ~207-212, so a troll keeps grabbing
// nearby non-deficit fruit and never treks to the distant deficit type. 10/12 sampled games
// stalled on exactly this (chopper trained in only 2/12).
#[test]
fn hoard_targets_deficit_fruit_over_nearby_fruit() {
    let mut st = base_state();
    let mut nearby = banana(3, 2, 4);
    nearby.fruits = 3; // ripe, but BANANA is not a funding type (ge_fruit_ty >= 3)
    let distant = Tree {
        tree_type: "PLUM".into(),
        x: 6,
        y: 2,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    };
    st.trees = vec![nearby, distant];
    let mut plan = base_plan();
    plan.phase = Phase::Hoard;
    plan.want_feeder = true;
    plan.need_fund = [true, false, false]; // PLUM deficit
    plan.cost = [3, 3, 3, 0, 0, 0];
    plan.need_iron = false;
    let cmds = assign(&st, &plan, &[starter(0, 2, 2)]);
    assert!(
        cmds[&0].contains("6 2"),
        "starter must trek to the distant deficit PLUM, not the nearer non-funding BANANA: {}",
        &cmds[&0]
    );
}

// Gatekeeper verdict #3 (post-b14ebc7), defect (a) BAND COLLISION: e09ac48 (iron, 64/63) and
// b14ebc7 (fruit, 63) independently landed on the SAME band, 63, for their MoveTo candidates. A
// troll facing both an iron shortfall and a fruit shortfall at once (routine — the ladder's last
// hand needs all four resources simultaneously) now resolves the choice by raw travel distance,
// not priority: iron loses whenever the fruit happens to be closer. Iron has no fruit-harvest
// alternative (B2.1's own comment: "iron is scarce and un-substitutable") so it must win this
// race unconditionally — reproduced in 8/8 sampled games (iron short at t110 in all of them).
#[test]
fn hoard_iron_beats_deficit_fruit() {
    let mut st = base_state();
    st.iron_cells.insert((5, 2));
    let plum = Tree {
        tree_type: "PLUM".into(),
        x: 3,
        y: 2,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    };
    st.trees = vec![plum];
    let mut plan = base_plan();
    plan.phase = Phase::Hoard;
    plan.want_feeder = true;
    plan.need_iron = true;
    plan.need_fund = [true, false, false];
    plan.cost = [3, 3, 3, 0, 7, 0];
    plan.have_iron = true;
    let cmds = assign(&st, &plan, &[starter(0, 2, 2)]);
    assert!(
        (cmds[&0].contains("4 2")
            || cmds[&0].contains("5 1")
            || cmds[&0].contains("5 3")
            || cmds[&0].contains("6 2"))
            && !cmds[&0].contains("3 2"),
        "starter must head for iron (a cell adjacent to (5,2)), not the closer deficit PLUM: {}",
        &cmds[&0]
    );
}

// Gatekeeper verdict #3, defect (b) T_SWITCH CLIFF: every elevated Hoard funding band
// (62/63/64) is gated `plan.phase == Phase::Hoard` only, so at t=140 they all evaporate at once —
// even when the ladder's wallet is one resource-tick from complete, funding priority drops to
// fund_lo (44, under Scale's forced want_chopper=false), which sits below Printer (50/48). A
// nearly-finished wallet gets abandoned instantly and the ladder's last hand never trains
// (chopper trained in 1/14 sampled games). A short grace window past T_SWITCH — scoped to
// want_feeder (the ladder is still incomplete) — must keep targeted funding above Printer work.
#[test]
fn factory_grace_keeps_funding_until_ladder_done() {
    let mut st = base_state();
    let mut nearby = banana(3, 2, 4);
    nearby.fruits = 3; // ripe, non-funding type — competes via the Printer band (48)
    let distant = Tree {
        tree_type: "PLUM".into(),
        x: 6,
        y: 2,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    };
    st.trees = vec![nearby, distant];
    let mut plan = base_plan();
    plan.phase = Phase::Factory;
    plan.want_feeder = true; // ladder incomplete
    plan.need_iron = false;
    plan.need_fund = [true, false, false]; // PLUM deficit
    plan.cost = [3, 3, 3, 0, 7, 0];
    plan.have_iron = true;
    let cmds = assign(&st, &plan, &[starter(0, 2, 2)]);
    assert!(
        cmds[&0].contains("6 2"),
        "past T_SWITCH with the ladder still incomplete, funding must still outrank Printer work: {}",
        &cmds[&0]
    );
}

// v1.35.0 (T-hand): the funding stack (65/64 iron, 63 deficit-fruit) must serve ANY pending
// ladder hand, not just Scale's Hoard/Factory phases — Tempo's revived 3rd hand (GE_MAX_TROLLS
// 2->3, botmain.rs) needs the identical deficit-fruit priority the Scale ladder already has, or
// it stalls exactly like the pre-fix Scale ladder did (gatekeeper verdict #2: nearby non-funding
// fruit outranked the distant deficit type). Exact mirror of
// hoard_targets_deficit_fruit_over_nearby_fruit, except phase: Phase::Tempo instead of Hoard.
#[test]
fn tempo_ladder_funding_treks_to_deficit_fruit() {
    let mut st = base_state();
    let mut nearby = banana(3, 2, 4);
    nearby.fruits = 3; // ripe, but BANANA is not a funding type (ge_fruit_ty >= 3)
    let distant = Tree {
        tree_type: "PLUM".into(),
        x: 6,
        y: 2,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    };
    st.trees = vec![nearby, distant];
    let mut plan = base_plan();
    plan.phase = Phase::Tempo;
    plan.want_feeder = true;
    plan.need_fund = [true, false, false]; // PLUM deficit
    plan.cost = [3, 3, 3, 0, 0, 0];
    plan.need_iron = false;
    let cmds = assign(&st, &plan, &[starter(0, 2, 2)]);
    assert!(
        cmds[&0].contains("6 2"),
        "under Tempo, the pending 3rd hand must trek to the distant deficit PLUM too, not the nearer non-funding BANANA: {}",
        &cmds[&0]
    );
}
