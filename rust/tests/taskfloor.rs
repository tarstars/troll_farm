//! v1.55.0-taskfloor (user's task-manager reframe, 2026-07-09): `planner::candidates()` is
//! the TASK PRODUCER; a parked troll (band 10) is the producer handing over an empty pool,
//! not a troll that "failed to pick work." Telemetry (@TFASSIGN probe vs Crouistiti, agentId
//! 6479836) proved late-game trolls get band=park for up to 82 CONSECUTIVE turns even while
//! reachable trees/fruit/plant cells exist elsewhere on the map -- every existing band is
//! bounded (roam radius / own-half / starter_chop / hoard-threatened / ripe-only-fruit), so
//! once the local neighborhood is exhausted the pool underflows to PARK. Fix: candidates()
//! ALWAYS additionally emits "reach-work" -- the K nearest reachable productive opportunities
//! ANYWHERE on the map, no roam bound -- at three low bands strictly between park (10) and
//! anti-starvation (30/31): reach-chop (20), reach-harvest (18), reach-plant (16).
//! [helpers copied VERBATIM from tests/planner_tasks.rs / tests/race_check.rs]
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
        door: None,
        door_d: None,
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
fn taskfloor_idle_troll_gets_reachwork_not_park() {
    // Pre-fix RED: `plan.starter_chop=false` closes the non-chopper's chop-help/anti-
    // starvation fallback (bands 40/42/30/31, all nested under `starter_chop && chop_power>0`)
    // even though this troll HAS chop_power=1 -- and it isn't `is_chopper` (needs >=2) so
    // the is_chopper branch's own band 70/30 never applies either. Farm at cap kills the
    // printer bands (52/50/49); no funding deficit (base_plan defaults: want_chopper=
    // want_feeder=false) kills 60/58/65/64/63/45/44; harvest_power=0 kills 75/38; empty carry
    // kills 88; Tempo phase kills the Hoard-only band 62; empty carry + free_capacity>0 kills
    // 95/80. The ONLY reachable productive opportunity is a fellable wild banana far across
    // the map (manhattan 8 from the troll, well outside chop_r=5 and NOT own-half) -- every
    // existing band's gate excludes it, so pre-fix this troll's sole candidate is PARK (band
    // 10, target None). Post-fix, reach-chop (gated only on `chop_power>0`, ignoring
    // `starter_chop`) must find it and send the troll there instead.
    let mut st = base_state();
    st.trees = vec![banana(7, 4, 2)]; // size 2 = fell_ok (fell_size=2), far corner
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap; // printer bands closed
    plan.starter_chop = false; // closes 40/42/30/31 for this non-chopper troll
    let mut u = starter(0, 1, 2);
    u.harvest_power = 0; // no fruit-related bands relevant
    // chop_power stays at starter()'s default of 1: NOT is_chopper (needs >=2), but
    // reach-chop only needs chop_power>0.
    let cmds = assign(&st, &plan, &[u]);
    assert!(
        cmds[&0].contains("7 4"),
        "idle troll with a reachable fellable tree anywhere on the map should reach for it \
         instead of parking, got: {}",
        &cmds[&0]
    );
}

#[test]
fn taskfloor_never_displaces_real_work() {
    // The trap guard (Test-B style, mirrors D1/idle-fruit's fruit_never_displaces_chop_help
    // and pressurefarm.rs/frontdoor.rs's flip-check convention): anti-starvation (band 30,
    // the LOWEST real band and the one closest to reach-work's range) must always outrank
    // reach-chop, even when a reach-chop-eligible tree exists. Must PASS both pre- and
    // post-fix (pre-fix trivially, since reach-chop doesn't exist pre-fix).
    //
    // Two trees, both excluded from band 70 by geometry (own_half AND within_roam both
    // false -- far from our shack, close to the opponent's):
    //   Tree A (6,2): CLOSER to the troll (eta 1) -- seed-protected (`plan.seed_cells`), so
    //     `fell_ok` excludes it from reach-chop (and band 70) entirely, leaving ONLY its
    //     antistarv bid: 30*BAND - eta(1) - chop_t(2) - race_pen(0) = 30*BAND - 3.
    //   Tree B (6,4): FARTHER (eta 2), plain fellable -- gets its own (weaker) antistarv bid
    //     (30*BAND - 2 - 2 - 0 = 30*BAND - 4) AND a reach-chop bid (20*BAND - eta(2)).
    // Correct-code winner: tree A (30*BAND-3 = 2,999,997) beats tree B's antistarv
    // (2,999,996) and tree B's reach-chop bid (1,999,998) by close to a full BAND.
    let mut st = base_state();
    st.trees = vec![banana(6, 2, 2), banana(6, 4, 2)];
    let mut plan = base_plan();
    plan.seed_cells = [(6, 2)].into_iter().collect();
    let u = chopper(2, 5, 2);
    let cmds = assign(&st, &plan, &[u]);
    assert!(
        cmds[&2].contains("6 2"),
        "anti-starvation (band 30) must win over reach-chop's own bid, got: {}",
        &cmds[&2]
    );
    assert!(
        !cmds[&2].contains("6 4"),
        "must not divert to the farther reach-chop-eligible tree ahead of antistarv, got: {}",
        &cmds[&2]
    );

    // FLIP-CHECK (per the brief, mirrors frontdoor.rs/pressurefarm.rs's documented manual
    // verification): temporarily changing `REACH_CHOP_BAND` from 20 to 35 (i.e. ABOVE
    // anti-starvation's 30) in planner.rs and rerunning this exact test makes it FAIL --
    // confirmed manually during development: tree B's reach-chop value becomes
    // 35*BAND - 2 = 3,499,998, which now exceeds tree A's antistarv value (2,999,997), so
    // `cmds[&2]` becomes "MOVE 2 6 4" and both assertions above fail. Tree A stays excluded
    // from reach-chop throughout (seed-protected), so it can't also "win via its own inflated
    // bid" and mask the flip -- the divergent target is what makes this observable. Reverted
    // immediately after capturing the failure (see the builder report for the exact
    // transcript).
}

#[test]
fn taskfloor_two_idle_trolls_two_targets() {
    // Two idle trolls (no normal task: starter_chop=false closes chop-help/antistarv, farm
    // at cap closes the printer bands, no funding deficit, no fruit anywhere) + two reachable
    // fellable trees, symmetric distances (each troll closer to a different tree) -- the
    // joint matcher (already-existing claim-conflict + exhaustive top-K search) must spread
    // them onto DISTINCT targets, not converge both onto the same tree.
    let mut st = base_state();
    st.trees = vec![banana(7, 0, 2), banana(7, 4, 2)];
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap;
    plan.starter_chop = false;
    let mut u0 = starter(0, 1, 1); // manhattan 7 to (7,0), 9 to (7,4): nearer to (7,0)
    u0.harvest_power = 0;
    let mut u1 = starter(1, 1, 3); // manhattan 9 to (7,0), 7 to (7,4): nearer to (7,4)
    u1.harvest_power = 0;
    let cmds = assign(&st, &plan, &[u0, u1]);
    assert!(
        cmds[&0].contains("7 0"),
        "troll 0 should reach for the nearer tree (7,0), got: {}",
        &cmds[&0]
    );
    assert!(
        cmds[&1].contains("7 4"),
        "troll 1 should reach for the nearer tree (7,4), got: {}",
        &cmds[&1]
    );
    assert_ne!(
        cmds[&0], cmds[&1],
        "the two idle trolls must not converge on the identical target"
    );
}

#[test]
fn taskfloor_barren_map_parks() {
    // Truly barren reachable map: zero trees anywhere -> reach-chop/reach-harvest trivially
    // find nothing; empty carry means reach-plant's `u.carry[BANANA]>0` gate excludes it too
    // regardless of any free cell. The troll must still gracefully PARK -- reach-work only
    // ever fires when reachable work genuinely exists. Holds both pre- and post-fix (a
    // non-regression pin, not a RED/GREEN pair -- there is nothing for reach-work to find
    // here either way).
    let st = base_state(); // st.trees stays empty (default)
    let plan = base_plan();
    let u = starter(0, 1, 2);
    let cmds = assign(&st, &plan, &[u]);
    assert!(
        cmds[&0].starts_with("MOVE"),
        "a barren map should still gracefully park (a MOVE toward a camp cell), got: {}",
        &cmds[&0]
    );
    // Direct, non-string-based confirmation via the same telemetry counter the DEBUG probe
    // uses (@TFPARK in botmain.rs): exactly one troll parked this turn.
    assert_eq!(
        troll_farm::botmain::planner::park_count(),
        1,
        "the telemetry counter must record exactly one parked troll this turn"
    );
}

#[test]
fn taskfloor_reachchop_skips_doomed() {
    // Same "no normal task" construction as taskfloor_idle_troll_gets_reachwork_not_park
    // (starter_chop=false + farm at cap + harvest_power=0 closes every existing band), plus
    // race_check.rs's exact doomed-tree numbers: enemy chopper standing ON a near tree
    // (health 2, chop_power 2 -> ceil(2/2)=1 turn to fell) while we are 2 steps away at ms=1
    // -> our_eta=2: they finish strictly before we arrive (1<=2), so `race()` returns None
    // (doomed) and reach-chop must skip it entirely -- same discipline race_check.rs already
    // pins for bands 70/72/40/42/30/31. A farther FREE tree exists; the troll must reach for
    // that one instead of parking (reach-work's own fallback-of-a-fallback).
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2), banana(6, 2, 2)]; // [0] near+doomed, [1] far+free
    st.trees[0].health = 2; // enemy chop_power 2 fells it in ceil(2/2)=1 turn
    st.opp_trolls = vec![chopper(9, 3, 2)]; // enemy standing ON (3,2)
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap;
    plan.starter_chop = false;
    let mut u = starter(0, 1, 2); // distance 2 from (3,2), ms=1 -> our_eta=2; 1<=2 -> doomed
    u.harvest_power = 0;
    let cmds = assign(&st, &plan, &[u]);
    assert!(
        !cmds[&0].contains("3 2"),
        "doomed reach-chop target must be skipped, not chased, got: {}",
        &cmds[&0]
    );
    assert!(
        cmds[&0].contains("6 2"),
        "must fall back to the farther FREE tree instead of parking, got: {}",
        &cmds[&0]
    );
}

#[test]
fn taskfloor_reachchop_canonical_order_not_discovery_order() {
    // Determinism guard: 4 trees tied at the SAME distance (2) from the troll, more than
    // REACH_K(3) -- truncation must keep the (dist,cell)-smallest three, not "whichever
    // three were encountered first." Built in FORWARD and REVERSED Vec order; both must
    // produce the IDENTICAL result, and that result must target the lexicographically
    // smallest tied cell (2,2) -- not (4,0) or (6,2), which a discovery-order bug (e.g.
    // "take the first K seen during iteration") would produce depending on input order.
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap;
    plan.starter_chop = false;

    let forward = vec![
        banana(2, 2, 2),
        banana(4, 0, 2),
        banana(4, 4, 2),
        banana(6, 2, 2),
    ];
    let mut reversed = forward.clone();
    reversed.reverse();

    troll_farm::botmain::planner::reset();
    let mut u_a = starter(0, 4, 2);
    u_a.harvest_power = 0;
    let mut st_a = base_state();
    st_a.trees = forward;
    let cmds_a = assign(&st_a, &plan, &[u_a]);

    troll_farm::botmain::planner::reset();
    let mut u_b = starter(0, 4, 2);
    u_b.harvest_power = 0;
    let mut st_b = base_state();
    st_b.trees = reversed;
    let cmds_b = assign(&st_b, &plan, &[u_b]);

    assert_eq!(
        cmds_a, cmds_b,
        "forward vs reversed tree order must produce the identical plan"
    );
    assert!(
        cmds_a[&0].contains("2 2"),
        "the tied nearest trees must resolve to the lexicographically smallest cell (2,2), got: {}",
        &cmds_a[&0]
    );
}
