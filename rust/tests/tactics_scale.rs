//! Task-4-review fix: `plan_with_meta` seam — real regression coverage for the tactics
//! Scale/Factory branch (phase schedule, farm_cap=20 under Factory, the SCALE_LADDER training
//! mapping). Before this seam, `GE_META` was a compile-time const read directly inside
//! `tactics::plan()`, so no integration test could drive the Scale/Factory path without either
//! editing the live constant (a real behavior change) or refactoring `plan()` to accept an
//! injected `Meta` — exactly what `plan_with_meta` provides, with zero effect on the live
//! `plan()` (which still reads `super::GE_META`, unchanged; proven by the flag-off equality gate
//! recorded in the report).
use std::collections::HashSet;
use troll_farm::botmain::tactics::{plan_with_meta, Meta, Phase};
use troll_farm::botmain::{State, Tree, Troll};

// [copied VERBATIM from tests/phase_hoard.rs]

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
fn tempo_plan_matches_tempo_semantics() {
    let st = base_state(); // turn: 50
    let my = vec![starter(0, 1, 2)];
    let plan = plan_with_meta(&st, &my, Meta::Tempo);
    assert_eq!(plan.phase, Phase::Tempo);
    assert_eq!(plan.farm_cap, 12);
    // want_chopper is whatever Tempo computes for this state — deliberately not asserted here.
}

#[test]
fn scale_hoard_plan() {
    let st = base_state(); // turn: 50
    let my = vec![starter(0, 1, 2)]; // n=1 (just the starter) -> ladder slot 0
    let plan = plan_with_meta(&st, &my, Meta::Scale);
    assert_eq!(plan.phase, Phase::Hoard);
    assert_eq!(plan.farm_cap, 12);
    assert_eq!(plan.want_chopper, false);
    assert_eq!(plan.train_spec, (1, 1, 1, 0));
}

#[test]
fn scale_factory_plan() {
    let mut st = base_state();
    st.turn = 200;
    let my = vec![starter(0, 1, 2)];
    let plan = plan_with_meta(&st, &my, Meta::Scale);
    assert_eq!(plan.phase, Phase::Factory);
    assert_eq!(plan.farm_cap, 20);
    assert_eq!(plan.want_chopper, false);
}

// v1.35.0 (T-hand): GE_MAX_TROLLS 2->3 re-arms the dormant feeder slot under Tempo itself
// (not just Scale). Three farm bananas at map-distance 2 from the shack (0,2) satisfy
// farm_now(2) >= GE_FEEDER_FARM(3); n=2 (starter + an already-trained chopper) satisfies
// n < GE_MAX_TROLLS(3); turn=50 satisfies turn >= GE_FEEDER_T. Under the OLD GE_MAX_TROLLS=2,
// n < GE_MAX_TROLLS is 2 < 2 = false, so want_feeder is unreachable whenever a chopper already
// exists (the chopper itself already brings n to 2) — the third hand never trains.
#[test]
fn tempo_wants_third_hand() {
    let mut st = base_state();
    st.trees = vec![banana(1, 1, 2), banana(1, 3, 2), banana(2, 2, 2)];
    st.turn = 50;
    let my = vec![starter(0, 1, 2), chopper(2, 4, 2)];
    let plan = plan_with_meta(&st, &my, Meta::Tempo);
    assert_eq!(plan.want_chopper, false, "a chopper already exists: {:?}", plan.want_chopper);
    assert_eq!(plan.want_feeder, true, "the third hand must be wanted");
    assert_eq!(plan.train_spec, (1, 1, 1, 0));
}
