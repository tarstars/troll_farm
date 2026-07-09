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
use troll_farm::botmain::{State, Tree, Troll, IRON};

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
// (not just Scale). ONE farm banana at map-distance 2 from the shack (0,2) gives farm_now=1;
// n=2 (starter + an already-trained chopper) satisfies n < GE_MAX_TROLLS(3); turn=50 satisfies
// turn >= GE_FEEDER_T. T-hand.1 (gatekeeper v1.35.0 verdict, fix b): the hand's whole design
// thesis is that it REVIVES a dying farm (farm sits at 0-1 after t45 in half the real boss
// games sampled), so gating it on farm_now >= GE_FEEDER_FARM(3) blocked the cure whenever the
// disease (a thin farm) was actually present. GE_FEEDER_FARM dropped 3->1 fixes this: a single
// surviving farm banana is enough to justify sending a planter. Under the OLD GE_FEEDER_FARM=3,
// farm_now(1) >= 3 is false, so want_feeder is unreachable here — this pins fix (b).
// parked after v1.49.0-farmhand local reject; re-enable only for a new GE_MAX_TROLLS>=3 candidate
#[ignore]
#[test]
fn tempo_wants_third_hand() {
    let mut st = base_state();
    st.trees = vec![banana(1, 1, 2)];
    st.turn = 50;
    let my = vec![starter(0, 1, 2), chopper(2, 4, 2)];
    let plan = plan_with_meta(&st, &my, Meta::Tempo);
    assert_eq!(plan.farm_now, 1, "sanity: exactly one farm banana in range");
    assert_eq!(
        plan.want_chopper, false,
        "a chopper already exists: {:?}",
        plan.want_chopper
    );
    assert_eq!(
        plan.want_feeder, true,
        "the third hand must be wanted even with a thin farm"
    );
    assert_eq!(plan.train_spec, (1, 1, 1, 0));
}

// Non-regression companion: the original 3-banana construction (farm_now=3, comfortably above
// the new GE_FEEDER_FARM=1 gate) must still want the third hand after the gate drops.
// parked after v1.49.0-farmhand local reject; re-enable only for a new GE_MAX_TROLLS>=3 candidate
#[ignore]
#[test]
fn tempo_wants_third_hand_farm3() {
    let mut st = base_state();
    st.trees = vec![banana(1, 1, 2), banana(1, 3, 2), banana(2, 2, 2)];
    st.turn = 50;
    let my = vec![starter(0, 1, 2), chopper(2, 4, 2)];
    let plan = plan_with_meta(&st, &my, Meta::Tempo);
    assert_eq!(plan.farm_now, 3, "sanity: three farm bananas in range");
    assert_eq!(
        plan.want_chopper, false,
        "a chopper already exists: {:?}",
        plan.want_chopper
    );
    assert_eq!(plan.want_feeder, true, "the third hand must be wanted");
    assert_eq!(plan.train_spec, (1, 1, 1, 0));
}

// T-hand.1 (gatekeeper v1.35.0 verdict, fix a): need_iron (tactics.rs) was gated on
// want_chopper ALONE, so once the chopper trained, iron mining stopped FOREVER — starving any
// later pending hand of its flat cost[IRON]=n training cost on every iron-bearing map (12/12
// sampled by the gatekeeper). Same construction as tempo_wants_third_hand_farm3 (farm_now=3,
// starter+chopper, want_feeder already true) but with iron present on the map and the wallet
// set so ONLY iron blocks training: at n=2, GE_FEEDER_SPEC=(1,1,1,0) costs
// training_cost(2,(1,1,1,0)) = [2+1,2+1,2+1,0,2+0*0,0] = [3,3,3,0,2,0] (PLUM,LEMON,APPLE,
// BANANA,IRON,WOOD) — inventory [5,5,5,0,0,0] clears every fruit leg (5>=3) but iron sits at
// 0 < 2. Under the current want_chopper-only gate, need_iron is false here (no chopper is
// wanted — the pending hand is the FEEDER), so the elevated ladder_funding iron bands
// (planner.rs 65/64) never fire and the hand is permanently unfunded.
// parked after v1.49.0-farmhand local reject; re-enable only for a new GE_MAX_TROLLS>=3 candidate
#[ignore]
#[test]
fn tempo_hand_iron_funding_after_chopper() {
    let mut st = base_state();
    st.trees = vec![banana(1, 1, 2), banana(1, 3, 2), banana(2, 2, 2)];
    st.turn = 50;
    st.iron_cells.insert((5, 2));
    st.my_inventory = [5, 5, 5, 0, 0, 0];
    let my = vec![starter(0, 1, 2), chopper(2, 4, 2)];
    let plan = plan_with_meta(&st, &my, Meta::Tempo);
    assert_eq!(
        plan.want_feeder, true,
        "the pending hand must still be wanted"
    );
    assert_eq!(
        plan.cost[IRON], 2,
        "sanity: the feeder spec costs n=2 iron here"
    );
    assert_eq!(
        plan.need_iron, true,
        "iron funding must be requested for the pending hand"
    );
    assert_eq!(plan.train_now, false, "cannot train yet: iron unaffordable");
}

// T-hand.2 (gatekeeper v1.35.0 verdict #2): farm_now collapses to literal ZERO for most of
// every real boss game sampled (63-100% of turns per game; 8/8 games ended with farm=0) — not
// merely "thin". Game 895413149 isolated the catch-22 cleanly: fruit+iron cleared the feeder's
// full cost for 255 straight turns (t45-t300) while farm sat at 0 the ENTIRE game, so
// want_feeder never once became eligible under GE_FEEDER_FARM=1 — the hand exists specifically
// to rescue a dead farm, so any nonzero floor blocks the cure exactly when it's needed. Same
// construction as tempo_wants_third_hand (one starter + one already-trained chopper, turn=50)
// but with ZERO farm bananas anywhere (farm_now=0). Under the OLD GE_FEEDER_FARM=1,
// farm_now(0) >= 1 is false, so want_feeder is unreachable here — this pins fix (b) of T-hand.2.
// parked after v1.49.0-farmhand local reject; re-enable only for a new GE_MAX_TROLLS>=3 candidate
#[ignore]
#[test]
fn tempo_wants_third_hand_dead_farm() {
    let mut st = base_state();
    st.trees = vec![];
    st.turn = 50;
    let my = vec![starter(0, 1, 2), chopper(2, 4, 2)];
    let plan = plan_with_meta(&st, &my, Meta::Tempo);
    assert_eq!(plan.farm_now, 0, "sanity: zero farm bananas in range");
    assert_eq!(
        plan.want_chopper, false,
        "a chopper already exists: {:?}",
        plan.want_chopper
    );
    assert_eq!(
        plan.want_feeder, true,
        "the third hand must be wanted even with a dead farm"
    );
}
