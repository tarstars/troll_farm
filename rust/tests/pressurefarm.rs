//! v1.53.0-pressurefarm: the ownership-pressure governor (docs/pressure-aware-farm.md,
//! docs/superpowers/plans/2026-07-09-pressurefarm-ownership-score.md, Tasks 0-2).
//!
//! Section A tests `ownership::assess` directly (Task 1's wiring: State -> Pressure),
//! mirroring tests/map_value_ownership.rs's helper style (a 1D line map; the two-call
//! INITIAL_TREES dance for "created" trees).
//!
//! Section B tests planner.rs's CONSUMPTION of a hand-set `plan.pressure` (Task 2's three
//! narrow behaviors), mirroring tests/race_check.rs's isolation style: Plan is built by
//! hand so each behavior is tested independent of Task 1's derivation logic.
use std::collections::HashSet;
use troll_farm::botmain::ownership::{self, Pressure, PressureState};
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{plan_with_meta, Meta, Phase, Plan};
use troll_farm::botmain::{bfs_distances, State, Tree, Troll, BANANA};

// ── Section A: ownership::assess wiring (Task 1) ────────────────────────────────────────

fn own_walk_line(max_x: i32) -> HashSet<(i32, i32)> {
    (0..=max_x).map(|x| (x, 0)).collect()
}

fn own_troll(id: i32, player_x: i32, hp: i32, chop: i32) -> Troll {
    Troll {
        id,
        x: player_x,
        y: 0,
        movement_speed: 1,
        carry_capacity: 3,
        harvest_power: hp,
        chop_power: chop,
        carry: [0; 6],
    }
}

fn own_banana(x: i32, size: i32, health: i32) -> Tree {
    Tree {
        tree_type: "BANANA".to_string(),
        x,
        y: 0,
        size,
        health,
        fruits: 0,
        cooldown: 0,
    }
}

fn own_plum(x: i32, size: i32, health: i32) -> Tree {
    Tree {
        tree_type: "PLUM".to_string(),
        x,
        y: 0,
        size,
        health,
        fruits: 0,
        cooldown: 0,
    }
}

fn own_state(turn: i32, trees: Vec<Tree>, my_trolls: Vec<Troll>, opp_trolls: Vec<Troll>) -> State {
    State {
        walkable: own_walk_line(6),
        my_shack: (0, 0),
        opp_shack: (6, 0),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees,
        my_trolls,
        opp_trolls,
        turn,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

fn own_plan(st: &State) -> Plan {
    let farm_d = bfs_distances(&st.walkable, &[st.my_shack]);
    Plan {
        shack: st.my_shack,
        farm_d,
        opp: st.opp_shack,
        have_iron: false,
        turns_rem: 300 - st.turn + 1,
        n: st.my_trolls.len() as i32,
        farm_now: st.trees.len(),
        nchop: 0,
        spec: (1, 1, 1, 1),
        want_chopper: false,
        want_feeder: false,
        train_spec: (1, 1, 1, 1),
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
        base_trees: st.trees.len(),
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
        pressure: Pressure::default(),
    }
}

#[test]
fn assess_green_when_all_reachable_trees_are_ours() {
    // Mirrors map_value_ownership.rs::near_chopper_owns_tree_value (tree at (1,0), our
    // chopper adjacent-ish, opponent far weaker) -- that scenario already asserts
    // own.ours == total, own.opp == 0. Here we assert the DERIVED Pressure: no exposed
    // own-half value anywhere means Green, and both new cell sets stay empty.
    ownership::reset();
    let st = own_state(
        75,
        vec![own_banana(1, 2, 4)],
        vec![own_troll(0, 1, 0, 2)],
        vec![own_troll(1, 6, 0, 1)],
    );
    let pr = ownership::assess(&st, &own_plan(&st));

    assert_eq!(pr.own_half_exposed, 0, "{:?}", pr);
    assert_eq!(pr.created_exposed, 0, "{:?}", pr);
    assert_eq!(pr.pressure_score, 0, "{:?}", pr);
    assert_eq!(pr.state, PressureState::Green, "{:?}", pr);
    assert!(pr.exposed_created_cells.is_empty(), "{:?}", pr);
    assert!(pr.released_seed_cells.is_empty(), "{:?}", pr);
}

#[test]
fn assess_yellow_when_only_own_half_exposed() {
    // A PLUM tree (never a "created farm tree" -- is_created_farm_tree is BANANA-only) on
    // our half, contested by an opponent who can definitely beat us to it (our troll is
    // chop/harvest-incapable: chop=0,hp=0 -> my_eta stays INF). own_half_exposed rises but
    // created_exposed must stay exactly 0 -> Yellow, not Orange.
    ownership::reset();
    let st = own_state(
        75,
        vec![own_plum(1, 2, 4)],
        vec![own_troll(0, 0, 0, 0)],
        vec![own_troll(1, 1, 0, 2)],
    );
    let pr = ownership::assess(&st, &own_plan(&st));

    assert!(pr.own_half_exposed > 0, "{:?}", pr);
    assert_eq!(pr.created_exposed, 0, "{:?}", pr);
    assert_eq!(pr.state, PressureState::Yellow, "{:?}", pr);
    assert!(pr.exposed_created_cells.is_empty(), "{:?}", pr);

    // flip-check: adjacent LOWER state (Green) requires own_half_exposed == 0; confirm the
    // Green fixture above genuinely differs from this one (sanity, not a repeat assertion).
    assert_ne!(pr.state, PressureState::Green);
}

#[test]
fn assess_orange_when_created_tree_uncertain_and_seed_stays_protected() {
    // Two-call INITIAL_TREES dance (as in map_value_ownership.rs): seed an empty initial
    // snapshot, THEN introduce the banana so is_created_farm_tree sees it as planted, not
    // native. Chopper (us, chop=2) at the shack vs an opposing chopper (chop=2) STANDING on
    // the tree: engineered to an exact ETA tie (see design notes below) -> Bucket::Uncertain,
    // not a definite loss -> Orange, not Red. A seed_cells entry on this same tree must NOT
    // be released at Orange (only Red releases -- Pressure::released_seed_cells is
    // deliberately stricter than "merely uncertain").
    //
    // ETA arithmetic (own_plan's farm_r=2, shack=(0,0), opp_shack=(6,0), tree at (2,0)):
    //   ours:  move 2 (ms1) + chop ceil(4/2)=2 + bank(tree->our bank cell (1,0), dist 1)+1
    //          = 2+2+2 = 6
    //   theirs: move 0 (standing on it) + chop 2 + bank(tree->their bank cell (5,0), dist 3)+1
    //          = 0+2+4 = 6
    // Tied (6 == 6): neither side's ETA+margin(3) beats the other -> Uncertain.
    ownership::reset();
    let initial = own_state(1, vec![], vec![own_troll(0, 0, 0, 0)], vec![own_troll(1, 6, 0, 0)]);
    let _ = ownership::assess(&initial, &own_plan(&initial));

    let later = own_state(
        75,
        vec![own_banana(2, 2, 4)],
        vec![own_troll(0, 0, 0, 2)],
        vec![own_troll(1, 2, 0, 2)],
    );
    let mut p = own_plan(&later);
    p.seed_cells.insert((2, 0));
    let pr = ownership::assess(&later, &p);

    assert!(pr.created_exposed > 0, "{:?}", pr);
    assert_eq!(
        pr.state,
        PressureState::Orange,
        "a tied/uncertain race must not escalate to Red: {:?}",
        pr
    );
    assert!(pr.exposed_created_cells.contains(&(2, 0)), "{:?}", pr);
    assert!(
        pr.released_seed_cells.is_empty(),
        "Orange (merely uncertain) must not release the seed cell: {:?}",
        pr
    );
}

#[test]
fn assess_red_when_created_tree_definitely_opponent() {
    // Same construction as the Orange test, but OUR troll is chop-incapable (chop=0) ->
    // my_eta stays INF -> the opponent definitely wins (Bucket::Opponent, not Uncertain) ->
    // Red. The same seed_cells entry now DOES release.
    ownership::reset();
    let initial = own_state(1, vec![], vec![own_troll(0, 0, 0, 0)], vec![own_troll(1, 6, 0, 0)]);
    let _ = ownership::assess(&initial, &own_plan(&initial));

    let later = own_state(
        75,
        vec![own_banana(2, 2, 4)],
        vec![own_troll(0, 0, 0, 0)],
        vec![own_troll(1, 2, 0, 2)],
    );
    let mut p = own_plan(&later);
    p.seed_cells.insert((2, 0));
    let pr = ownership::assess(&later, &p);

    assert!(pr.created_exposed > 0, "{:?}", pr);
    assert_eq!(
        pr.state,
        PressureState::Red,
        "a definite opponent win must escalate to Red: {:?}",
        pr
    );
    assert!(pr.exposed_created_cells.contains(&(2, 0)), "{:?}", pr);
    assert!(
        pr.released_seed_cells.contains(&(2, 0)),
        "Red must release a seed cell that is itself Bucket::Opponent: {:?}",
        pr
    );
}

// ── Section B: planner.rs consuming plan.pressure (Task 2) ──────────────────────────────
// [scenario helpers in the style of tests/race_check.rs and tests/threatfell.rs]

fn base_state() -> State {
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..16 {
        for y in 0..5 {
            walkable.insert((x, y));
        }
    }
    walkable.remove(&(0, 2));
    State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (15, 2),
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
    let farm_d = bfs_distances(&st.walkable, &[st.my_shack]);
    Plan {
        shack: st.my_shack,
        farm_d,
        opp: st.opp_shack,
        have_iron: false,
        turns_rem: 250,
        n: 1,
        farm_now: 0,
        nchop: 0,
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
        pressure: Pressure::default(),
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

/// A non-chopper hand carrying one banana, otherwise idle (no chop/harvest candidates) --
/// isolates band 88 (plant) vs band 10-as-Bank (the pressure-suppressed fallback).
fn carrier(id: i32, x: i32, y: i32) -> Troll {
    let mut t = Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 3,
        harvest_power: 0,
        chop_power: 0,
        carry: [0; 6],
    };
    t.carry[BANANA] = 1;
    t
}

fn tree_at(x: i32, y: i32, size: i32) -> Tree {
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
fn pressure_green_is_noop() {
    // Regression guard: with Plan::pressure at its all-zero/empty Default (Green), every
    // pressure-gated behavior in planner.rs must reproduce exactly what the pre-pressure
    // code did. Three independent checks, one per Task-2 behavior:
    troll_farm::botmain::planner::reset();

    // (a) dynamic farm cap: base_trees above the pressure floor (4) but below the normal
    // cap (12) -- a carried banana must still PLANT, not get suppressed to a bank/DROP.
    troll_farm::botmain::planner::reset();
    let mut plan_a = base_plan();
    plan_a.base_trees = 5;
    let cmds = assign(&base_state(), &plan_a, &[carrier(0, 1, 2)]);
    assert_ne!(
        cmds[&0], "DROP 0",
        "Green must not suppress planting: {}",
        cmds[&0]
    );

    // (b) liquidation bonus: with no exposed_created_cells (Green's natural, consistent
    // state), the closer/cheaper tree must win over the farther one -- no bonus applied.
    troll_farm::botmain::planner::reset();
    let mut st_b = base_state();
    st_b.trees = vec![tree_at(3, 2, 2), tree_at(4, 2, 2)];
    let plan_b = base_plan();
    let cmds = assign(&st_b, &plan_b, &[chopper(2, 1, 2)]);
    assert!(
        cmds[&2].contains("3 2"),
        "Green must pick the naturally closer tree: {}",
        cmds[&2]
    );
    assert!(!cmds[&2].contains("4 2"), "{}", cmds[&2]);

    // (c) seed release: a protected seed tree stays protected -- the chopper standing on it
    // must walk away to the only OTHER fellable tree instead of chopping in place. The safe
    // tree sits WITHIN chop_r (5) so it gets a real band-70 candidacy (70*BAND-4) that
    // comfortably beats the seed tree's anti-starvation band-31 fallback (31*BAND-3) --
    // band 30/31 doesn't consult fell_ok/seed_cells at all (an existing, pre-pressure
    // property: anti-starvation is a last-resort catch-all), so a farther "safe" tree
    // outside roam would only ever reach band 30, which a standing ChopHere (31) always
    // beats regardless of seed protection -- not a useful discriminator for this test.
    troll_farm::botmain::planner::reset();
    let mut st_c = base_state();
    st_c.trees = vec![tree_at(2, 2, 4), tree_at(5, 2, 2)];
    let mut plan_c = base_plan();
    plan_c.seed_cells.insert((2, 2));
    let cmds = assign(&st_c, &plan_c, &[chopper(2, 2, 2)]);
    assert_eq!(
        cmds[&2], "MOVE 2 5 2",
        "Green must keep the seed tree protected: {}",
        cmds[&2]
    );
}

#[test]
fn yellow_suppresses_expansion() {
    // Yellow (own_half_exposed > 0) with the farm already above the survival floor: a
    // carried banana that WOULD plant at base is suppressed to a bank/DROP instead. The
    // farm_cap value here is what tactics::plan_impl computes (provisional.farm_cap.min(
    // GE_PRESSURE_FARM_FLOOR)) -- hand-set here to isolate planner.rs's consumption of it
    // from tactics.rs's derivation (covered separately by the assess_* tests above).
    troll_farm::botmain::planner::reset();
    let st = base_state();
    let mut plan = base_plan();
    plan.base_trees = 5; // > GE_PRESSURE_FARM_FLOOR (4)
    plan.farm_cap = 4; // what tactics.rs would clamp to under Yellow+
    plan.pressure = Pressure {
        own_half_exposed: 5,
        state: PressureState::Yellow,
        ..Pressure::default()
    };

    let cmds = assign(&st, &plan, &[carrier(0, 1, 2)]);
    assert_eq!(
        cmds[&0], "DROP 0",
        "Yellow with base_trees above the floor must suppress the plant: {}",
        cmds[&0]
    );

    // flip-check: adjacent LOWER state (Green) must NOT suppress under the identical
    // base_trees/scenario. Fresh planner::reset() so STICKY can't carry the previous call's
    // Bank/DROP pick forward (this troll id is reused across all three calls in this test).
    troll_farm::botmain::planner::reset();
    let mut plan_green = base_plan();
    plan_green.base_trees = 5;
    plan_green.farm_cap = 12; // Green: tactics.rs leaves farm_cap untouched
    let cmds = assign(&st, &plan_green, &[carrier(0, 1, 2)]);
    assert_ne!(
        cmds[&0], "DROP 0",
        "Green must not suppress the same scenario: {}",
        cmds[&0]
    );

    // a farm below the survival floor keeps planting even under Yellow.
    troll_farm::botmain::planner::reset();
    let mut plan_floor = base_plan();
    plan_floor.base_trees = 3; // < GE_PRESSURE_FARM_FLOOR (4)
    plan_floor.farm_cap = 4; // still clamped, but 3 < 4 so plant_cell exists
    plan_floor.pressure = Pressure {
        own_half_exposed: 5,
        state: PressureState::Yellow,
        ..Pressure::default()
    };
    let cmds = assign(&st, &plan_floor, &[carrier(0, 1, 2)]);
    assert_ne!(
        cmds[&0], "DROP 0",
        "a farm below the survival floor must keep planting even under Yellow: {}",
        cmds[&0]
    );
}

#[test]
fn orange_raises_local_liquidation() {
    // Two same-size farm trees; (4,2) is one MoveTo-eta step farther from the chopper than
    // (3,2) (eta 2 vs 1), so at parity (3,2) wins by 1 in-band point. Marking (4,2) as
    // pressure-exposed under Orange adds PRESSURE_LIQ_BONUS (4) -- net swing +3 -- so the
    // exposed, farther tree must now win. (3,2) is untouched (never in exposed_created_cells)
    // and its own eta/value never changes -- the flip is entirely (4,2)'s bonus.
    troll_farm::botmain::planner::reset();
    let mut st = base_state();
    st.trees = vec![tree_at(3, 2, 2), tree_at(4, 2, 2)];
    let mut plan = base_plan();
    plan.pressure = Pressure {
        created_exposed: 8,
        state: PressureState::Orange,
        exposed_created_cells: [(4, 2)].into_iter().collect(),
        ..Pressure::default()
    };

    let cmds = assign(&st, &plan, &[chopper(2, 1, 2)]);
    assert!(
        cmds[&2].contains("4 2"),
        "Orange must raise the exposed, farther tree above the naturally-closer one: {}",
        cmds[&2]
    );
    assert!(!cmds[&2].contains("3 2"), "{}", cmds[&2]);

    // flip-check: adjacent LOWER state (Yellow) must NOT apply the bonus even with the same
    // exposed_created_cells set populated -- proves the `state >= Orange` gate is load-
    // bearing on its own, not merely a proxy for "the set happens to be non-empty". Fresh
    // planner::reset() so STICKY can't keep the previous call's (4,2) pick alive on its own.
    troll_farm::botmain::planner::reset();
    plan.pressure.state = PressureState::Yellow;
    let cmds = assign(&st, &plan, &[chopper(2, 1, 2)]);
    assert!(
        cmds[&2].contains("3 2"),
        "Yellow must not apply the liquidation bonus: {}",
        cmds[&2]
    );
    assert!(!cmds[&2].contains("4 2"), "{}", cmds[&2]);
}

#[test]
fn red_releases_seed_reserve() {
    // A protected seed tree the chopper is standing on, plus a free tree within roam (see
    // pressure_green_is_noop's scenario (c) for why it must be within chop_r, not merely
    // "any other tree" -- outside roam it would only reach the weak anti-starvation band,
    // which the seed tree's OWN anti-starvation fallback already beats regardless of
    // fell_ok). Red releases the seed tree (it becomes fell_ok) -> ChopHere (band 72)
    // strictly outranks any MoveTo (a full BAND ahead), so the chopper stays and chops.
    // Orange (without a per-tree release) must leave it protected -> the chopper walks to
    // the only OTHER fellable tree instead.
    troll_farm::botmain::planner::reset();
    let mut st = base_state();
    st.trees = vec![tree_at(2, 2, 4), tree_at(5, 2, 2)];
    let mut plan = base_plan();
    plan.seed_cells.insert((2, 2));
    plan.pressure = Pressure {
        created_exposed: 16,
        state: PressureState::Red,
        exposed_created_cells: [(2, 2)].into_iter().collect(),
        released_seed_cells: [(2, 2)].into_iter().collect(),
        ..Pressure::default()
    };

    let cmds = assign(&st, &plan, &[chopper(2, 2, 2)]);
    assert_eq!(
        cmds[&2], "CHOP 2",
        "Red must release the seed tree so the chopper fells it in place: {}",
        cmds[&2]
    );

    // flip-check: adjacent LOWER state (Orange), same exposure, but NOT released (a merely
    // Uncertain seed tree stays protected -- see assess_orange_...-_seed_stays_protected).
    // Fresh planner::reset(): the first call's ChopHere pick doesn't set LAST_TGT (only
    // MoveTo does), so this is not strictly required here, but kept for uniformity/safety.
    troll_farm::botmain::planner::reset();
    plan.pressure.state = PressureState::Orange;
    plan.pressure.released_seed_cells = HashSet::new();
    let cmds = assign(&st, &plan, &[chopper(2, 2, 2)]);
    assert_eq!(
        cmds[&2], "MOVE 2 5 2",
        "Orange without a per-tree release must keep the seed tree protected: {}",
        cmds[&2]
    );
}

// ── Direct tactics::plan_impl test (Task 2 Step 1's actual implementation site) ─────────
// The planner-level `yellow_suppresses_expansion` test above hand-sets `plan.farm_cap` to
// isolate planner.rs's consumption of it from tactics.rs's derivation. This test drives the
// derivation itself: a real State/`plan_with_meta` call, checking the emitted `farm_cap`.

fn yellow_scenario(n_farm_trees: usize) -> State {
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..16 {
        for y in 0..5 {
            walkable.insert((x, y));
        }
    }
    walkable.remove(&(0, 2));
    // candidate farm positions, all within farm_d <= GE_FARM_R(2) of shack (0,2)
    let candidates = [(1, 2), (0, 1), (2, 2), (1, 1), (1, 3)];
    let mut trees: Vec<Tree> = candidates
        .iter()
        .take(n_farm_trees)
        .map(|&(x, y)| Tree {
            tree_type: "BANANA".into(),
            x,
            y,
            size: 1,
            health: 3,
            fruits: 0,
            cooldown: 0,
        })
        .collect();
    // a contested PLUM (never "created", is_created_farm_tree is BANANA-only) on our half
    // (closer to (0,2) than to opp_shack (15,2)), reachable only by the opponent -- our sole
    // troll is chop/harvest-incapable, so own_half_exposed > 0 with created_exposed == 0:
    // Yellow, not Orange, regardless of the farm-tree count above.
    trees.push(Tree {
        tree_type: "PLUM".into(),
        x: 5,
        y: 2,
        size: 2,
        health: 4,
        fruits: 0,
        cooldown: 0,
    });
    State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (15, 2),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees,
        my_trolls: vec![Troll {
            id: 0,
            x: 0,
            y: 1,
            movement_speed: 1,
            carry_capacity: 3,
            harvest_power: 0,
            chop_power: 0,
            carry: [0; 6],
        }],
        opp_trolls: vec![Troll {
            id: 1,
            x: 5,
            y: 2,
            movement_speed: 1,
            carry_capacity: 3,
            harvest_power: 0,
            chop_power: 2,
            carry: [0; 6],
        }],
        turn: 75,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

#[test]
fn tactics_farm_cap_floor_engages_under_yellow_but_not_below_floor() {
    // GE_PRESSURE_FARM_FLOOR is a private botmain.rs const; 4 is hardcoded here the same
    // way existing tests already hardcode GE_FARM_R=2 / GE_FARM_MAX=12 as literals rather
    // than importing crate-root consts into an external integration-test crate.
    ownership::reset();
    let st = yellow_scenario(5); // base_trees(5) > floor(4)
    let plan = plan_with_meta(&st, &st.my_trolls, Meta::Tempo);
    assert_eq!(
        plan.pressure.state,
        PressureState::Yellow,
        "{:?}",
        plan.pressure
    );
    assert_eq!(plan.base_trees, 5);
    assert_eq!(
        plan.farm_cap, 4,
        "Yellow with base_trees above the floor must clamp farm_cap to the floor, got {}",
        plan.farm_cap
    );

    // flip-check: a farm already below the floor (3 < 4) keeps its normal room to grow --
    // the clamp is a ceiling, never a mandate to shrink below where the farm already is.
    ownership::reset();
    let st_floor = yellow_scenario(3);
    let plan_floor = plan_with_meta(&st_floor, &st_floor.my_trolls, Meta::Tempo);
    assert_eq!(plan_floor.pressure.state, PressureState::Yellow);
    assert_eq!(plan_floor.base_trees, 3);
    assert!(
        plan_floor.base_trees < plan_floor.farm_cap,
        "a farm below the survival floor must still have plantable room: base_trees={} farm_cap={}",
        plan_floor.base_trees,
        plan_floor.farm_cap
    );
}
