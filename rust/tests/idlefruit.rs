//! v1.42.0-idlefruit (design D1, champion loss taxonomy 2026-07-08 morning,
//! docs/silver-experiment-log.md "## Champion loss taxonomy"): 45% of all champion arena
//! losses (HARVEST-ECONOMY + DUAL-ECONOMY, n=9/20, avg margin -63.9) are opponents
//! out-fruiting us -- HARVEST+DROP command counts of 91-307 vs our flat 20-90. The fix is a
//! new Tempo-phase STARTER band, sharpened by the controller against the v1.24.0-fruitbank
//! failure (arena -1.0, whose sin was ranking fruit-chasing ABOVE chop-help): band 38,
//! strictly above anti-starvation (31/30), strictly below chop-help (42/40) and every printer
//! band (52/50/49/48), so it converts ONLY otherwise-idle turns into fruit points and never
//! displaces wood work, seed work, or hand funding.
//! [helpers copied VERBATIM from tests/planner_tasks.rs, + a `plum` fruit-tree constructor]
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
fn plum(x: i32, y: i32, fruits: i32) -> Tree {
    Tree {
        tree_type: "PLUM".into(),
        x,
        y,
        size: 2,
        health: 4,
        fruits,
        cooldown: 0,
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

#[test]
fn idle_starter_harvests_fruit_instead_of_parking() {
    // Farm at cap (printer bands 52/50/49/88 all gated on `base_trees < farm_cap`; setting
    // base_trees == farm_cap kills them). No pending hand needs funding (want_chopper/
    // want_feeder both false, the base_plan() default), so the funding bands (60/58/65/64/63/
    // 45/44) never fire. This troll is a pure harvester (chop_power=0), so the chop-help +
    // anti-starvation block -- nested under `plan.starter_chop && u.chop_power > 0` for the
    // STARTER branch -- never fires either. A single ripe PLUM (fruits=2) sits at (4,2),
    // reachable, and the troll is NOT standing on it.
    //
    // Pre-fix: literally nothing claims the plum (no band even looks at a non-funding,
    // non-printer, non-Hoard fruit tree the troll isn't already standing on) -- only the
    // band-10 fallback (Park) survives. park_cmd's nearest-unclaimed-camp-cell search then
    // picks the troll's OWN current cell (already shack-adjacent, distance 0 from itself),
    // i.e. an effective no-op park. Post-fix: band 38 claims the plum and the troll moves to
    // harvest it -- an idle turn converted into a fruit point.
    let mut st = base_state();
    st.trees = vec![plum(4, 2, 2)];
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap; // farm at cap: printer bands gated off
    let mut u = starter(0, 1, 2);
    u.chop_power = 0; // no chop-help/anti-starvation candidates possible for this troll
    let cmds = assign(&st, &plan, &[u]);
    assert!(
        cmds[&0].contains("4 2"),
        "idle starter with a ripe fruit reachable and nothing better to do should go harvest it, got: {}",
        &cmds[&0]
    );
}

#[test]
fn fruit_never_displaces_chop_help() {
    // Regression pin for the v1.24.0-fruitbank trap (arena -1.0): fruit-chasing must NEVER
    // outrank chop-help -- that was precisely fruitbank's sin. Same construction as the idle
    // test above (farm at cap, no funding deficit, ripe plum at (4,2)), but this troll IS
    // chop-capable (chop_power=1, the starter() default) and there is a fellable own-half
    // banana at (3,2), within roam: map-distance 3 <= chop_r=5 (`within_roam`); manhattan to
    // our shack (3) <= manhattan to the opponent's (4) (`own_half`). Chop-help (band 42/40)
    // must win over the idle-fruit band (38) for the plum. This must PASS both BEFORE this
    // candidate's fix (band 38 doesn't exist yet, so chop-help is the only real candidate
    // anyway) and AFTER it (band 38 exists but chop-help still outranks it) -- a true
    // non-regression pin, not a RED/GREEN pair.
    let mut st = base_state();
    st.trees = vec![plum(4, 2, 2), banana(3, 2, 2)];
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap; // same farm-at-cap construction as the idle test
    let u = starter(0, 1, 2); // chop_power=1 (default): chop-help is available this time
    let cmds = assign(&st, &plan, &[u]);
    assert!(
        cmds[&0].contains("3 2"),
        "chop-help must win over the idle-fruit band, got: {}",
        &cmds[&0]
    );
    assert!(
        !cmds[&0].contains("4 2"),
        "must not divert to the plum ahead of chop-help, got: {}",
        &cmds[&0]
    );
}

#[test]
fn idle_troll_skips_doomed_fruit() {
    // Reviewer IMPORTANT follow-up (code review of this candidate): band 38 didn't consult
    // `race()`, so an idle troll could trek toward a fruit tree an enemy chopper fells before
    // arrival -- the same "doomed-target chasing" waste class tests/race_check.rs already closes
    // for the wood bands (70/72, 40/42, 30/31). Same construction as
    // idle_starter_harvests_fruit_instead_of_parking (farm at cap, no funding deficit, a
    // chop_power=0 starter so chop-help/anti-starvation never fire) plus an enemy chopper (see
    // race_check.rs's `chopper` construction) standing ON the ripe plum at (4,2): health 4,
    // chop_power 2 -> ceil(4/2) = 2 turns for them to fell it. Our troll starts at (1,2),
    // map-distance 3 away at movement_speed 1 -> our_eta = 3: they finish (turn 2) strictly
    // before we arrive (turn 3), so `race` returns None (doomed) and band 38 must skip this tree
    // entirely.
    //
    // PRE-FIX (hand-verified; the band-38 loop never called `race` at all): the plum
    // unconditionally emits a MoveTo candidate at `38*BAND - 3` -- the only real candidate this
    // troll has (chop-help/anti-starvation closed off by chop_power=0; funding/printer bands
    // closed off by farm-at-cap + no deficit) -- so it wins the joint assignment and
    // `cmds[&0]` contains "4 2", exactly like idle_starter_harvests_fruit_instead_of_parking's
    // pre-fix RED before band 38 existed at all. Confirmed by running this test against the
    // pre-fix tree: `cargo test --release --test idlefruit idle_troll_skips_doomed_fruit` FAILED
    // with `cmds[&0] == "MOVE 0 4 2"` (band 38's `eta(&d, pc, ms)`-only value, uncontested by any
    // race check, beats the band-10 Park fallback).
    let mut st = base_state();
    st.trees = vec![plum(4, 2, 2)];
    st.trees[0].health = 4; // enemy chop_power 2 fells it in ceil(4/2) = 2 turns
    st.opp_trolls = vec![chopper(9, 4, 2)]; // enemy standing ON the plum
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap; // farm at cap: printer bands gated off
    let mut u = starter(0, 1, 2); // map-distance 3 from (4,2), ms=1 -> our_eta = 3
    u.chop_power = 0; // no chop-help/anti-starvation candidates possible for this troll
    let cmds = assign(&st, &plan, &[u]);
    assert!(
        !cmds[&0].contains("4 2"),
        "doomed fruit (enemy fells it before our ETA) must be skipped, not chased, got: {}",
        &cmds[&0]
    );
}
