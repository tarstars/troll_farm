//! v1.61.0-chopharvest (user idea, 2026-07-11): the ring's fruit bananas fill to the cap and
//! STALL when the gatherer is off foraging distant (the documented mid-game farm death). The
//! CHOPPER banks wood right next to the ring but never harvests -- pre-fix its spec is
//! `(2,3,0,2)` -> harvest_power=0, and every harvest band gates on `harvest_power>0`. This
//! candidate: (1) bump the chopper's harvest_power 0->1 (+1 apple training cost); (2) let the
//! chopper opportunistically harvest full/ripe bananas STRICTLY BELOW its felling (fell 70/72
//! always wins; harvest only fires when the chopper has no fell/anti-starvation work, mirroring
//! the STARTER's existing idle-fruit band 38 -- see "6.5) IDLE-FRUIT" in planner.rs::candidates).
//! See data/candidates/v1.61.0-chopharvest/brief.md.
//! [helpers copied VERBATIM in spirit from tests/idlefruit.rs / tests/race_check.rs]
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{self, Phase, Plan};
use troll_farm::botmain::{State, Tree, Troll, GE_SPEC};

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
    // farm_d: BFS map distances from the shack over the 8x5 open room (shack at (0,2)) --
    // identical geometry to tests/idlefruit.rs.
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
        spec: (2, 3, 1, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (2, 3, 1, 2),
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

/// The chopper, post-candidate spec: ms2/cc3/hp1/chop2 (matches GE_SPEC (2,3,1,2)).
/// `is_chopper` in planner.rs is `chop_power >= 2`, independent of harvest_power -- this troll
/// takes the `if is_chopper` branch of candidates() regardless of the hp value used here.
fn chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 2,
        carry_capacity: 3,
        harvest_power: 1,
        chop_power: 2,
        carry: [0; 6],
    }
}

/// starter: chop=1 (chop-capable but not is_chopper, which needs chop_power>=2), hp=1 --
/// already hp=1 pre-candidate (this GE_SPEC bump only touches the CHOPPER's spec).
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

/// A ripe/full banana that is NOT independently fellable -- size 0 fails both fell_ok
/// (needs size >= fell_size/farm_fell) and anti-starvation (needs size >= 1), so it only
/// ever contributes a harvest candidate. Isolates "is a harvest band offered at all" from
/// "which of two competing fell targets wins", matching the brief's opportunistic-harvest-only
/// framing (a banked-next-to, already-mature tree that has nothing left to fell).
fn ripe_banana(x: i32, y: i32, fruits: i32) -> Tree {
    Tree {
        tree_type: "BANANA".into(),
        x,
        y,
        size: 0,
        health: 0,
        fruits,
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

// ── 1) spec: chopper hp 0 -> 1 ────────────────────────────────────────────────────────────────
#[test]
fn chopharvest_spec_hp1() {
    assert_eq!(
        GE_SPEC,
        (2, 3, 1, 2),
        "the live chopper spec's harvest_power (3rd field) must be bumped 0->1 so it qualifies \
         for the opportunistic idle-fruit harvest band; got {:?}",
        GE_SPEC
    );
}

// ── 2) the core constraint: fell/chop always outranks harvest ───────────────────────────────
#[test]
fn chopharvest_fells_over_harvest() {
    // Chopper at (1,2). A fellable native tree at (3,2) (size 2, own-half, within roam) is the
    // ONLY real fell target. A ripe/full banana sits directly ADJACENT to the chopper at (2,2)
    // (distance 1 -- the cheapest, most tempting possible harvest, closer than the fell
    // target) but is non-fellable (size 0, see ripe_banana's doc comment). If harvest ever
    // outranked felling (e.g. bands 75/62 firing for the chopper, or this candidate's new band
    // valued >= 70), the chopper would divert to (2,2) instead of (3,2). It must not.
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2), ripe_banana(2, 2, 3)];
    let plan = base_plan();
    let cmds = assign(&st, &plan, &[chopper(0, 1, 2)]);
    assert!(
        cmds[&0].contains("3 2"),
        "felling must win over the adjacent ripe banana, got: {}",
        &cmds[&0]
    );
    assert!(
        !cmds[&0].starts_with("HARVEST"),
        "the chopper must not harvest while a fell target exists, got: {}",
        &cmds[&0]
    );
    assert!(
        !cmds[&0].contains("2 2"),
        "must not divert to the adjacent ripe banana ahead of felling, got: {}",
        &cmds[&0]
    );
}

// ── 3) the new capability: harvest when there is nothing to fell ────────────────────────────
#[test]
fn chopharvest_harvests_when_idle() {
    // Chopper STANDS on the only tree on the map: a ripe/full banana (size 0 -- no fell/
    // chop-help/anti-starvation candidate is possible; see ripe_banana's doc comment) with free
    // capacity. Pre-fix (hp=0 in the live spec; this test's chopper() fixture is hp=1
    // regardless -- the gate is the MISSING harvest band in the `is_chopper` branch, not the
    // spec constant) nothing claims it: is_chopper's branch only ever pushed fell(70/72),
    // anti-starvation(30/31) and the park/bank fallback(10) -- none apply here, so band-10
    // Park/Bank wins and the command is NOT a harvest. Post-fix the new band-38
    // opportunistic-harvest candidate claims it.
    let mut st = base_state();
    st.trees = vec![ripe_banana(2, 2, 3)];
    let plan = base_plan();
    let cmds = assign(&st, &plan, &[chopper(0, 2, 2)]);
    assert_eq!(
        cmds[&0], "HARVEST 0",
        "an idle chopper standing on a ripe/full banana with nothing to fell must harvest it, \
         got: {}",
        &cmds[&0]
    );
}

// ── 4) the starter must be untouched ─────────────────────────────────────────────────────────
#[test]
fn chopharvest_starter_unchanged() {
    // Same construction as tests/idlefruit.rs::idle_starter_harvests_fruit_instead_of_parking
    // (a known-good ringfix3-era pin): farm at cap (printer bands off), no funding deficit, a
    // ripe plum at (4,2), starter at (1,2) with chop_power=0 (isolates band 38 -- chop-help/
    // anti-starvation need chop_power>0). This candidate's ONLY code changes are (a) the
    // GE_SPEC constant, which this troll's hardcoded fixture does not read, and (b) new code
    // strictly inside the `if is_chopper` branch (chop_power>=2) -- this starter (chop_power=0)
    // never reaches it structurally. Command must be byte-identical to the ringfix3 baseline.
    let mut st = base_state();
    st.trees = vec![plum(4, 2, 2)];
    let mut plan = base_plan();
    plan.base_trees = plan.farm_cap; // farm at cap: printer bands gated off
    let mut u = starter(0, 1, 2);
    u.chop_power = 0; // no chop-help/anti-starvation candidates possible for this troll
    let cmds = assign(&st, &plan, &[u]);
    assert_eq!(
        cmds[&0], "MOVE 0 4 2",
        "the starter's idle-fruit behavior must be byte-identical to the ringfix3 baseline -- \
         the chopper-only harvest addition must not touch the non-chopper branch, got: {}",
        &cmds[&0]
    );
}

// ── 5) determinism: repeated calls (stand-in for the 8-seed self-equality freeze gate) ──────
#[test]
fn chopharvest_deterministic_across_repeated_calls() {
    // planner.rs's `salt` is derived deterministically from `state` (tie_salt), not an external
    // RNG seed, so there is no seed parameter to sweep at the `assign()` level -- the true
    // 8-seed self-determinism check is the freeze-stage `equality` binary harness (playing full
    // simulated games through the compiled bot over 8 seeds; see bundle.py/equality.rs docs).
    // This unit test is the closest in-crate proxy.
    //
    // reviewer CONFIRMED (hand-traced): a fixture with only ONE candidate per loop (one fell
    // target, one harvest target) can't actually exercise order-sensitivity -- each tree only
    // ever matches a single band's filter, and the final `out.sort_by_key` downstream is a true
    // total order on `(value, target)`, so reversing a 2-element input Vec is a no-op no matter
    // what. Fixed here: TWO ripe/full bananas, same distance (both map-distance 2, eta 1 step)
    // and same fruits (3, so identical `fullness_pen`), i.e. a GENUINE tie in the new band-38
    // loop's output value -- this is the file's own documented "SHUFFLE INVARIANCE" contract
    // (see the module doc comment at the top of planner.rs): which of two truly-tied candidates
    // wins must be decided by the canonical tie-break (`tie_mix`/salt), never by which one the
    // Vec iterator happened to visit first.
    let mut st = base_state();
    st.trees = vec![ripe_banana(2, 2, 3), ripe_banana(0, 1, 3)]; // both dist 2 from (1,2), fruits 3
    let plan = base_plan();
    let first = assign(&st, &plan, &[chopper(0, 1, 2)]);
    for _ in 0..8 {
        let again = assign(&st, &plan, &[chopper(0, 1, 2)]);
        assert_eq!(again, first, "assign() must be deterministic across repeated calls");
    }
    st.trees.reverse();
    let reversed = assign(&st, &plan, &[chopper(0, 1, 2)]);
    assert_eq!(
        reversed, first,
        "a genuine tie between two equal-value harvest targets must resolve the SAME way \
         regardless of candidate Vec order (canonical tie-break, not iteration order): {} vs {}",
        first[&0], reversed[&0]
    );
}

// ── 6) regression guard: the REAL live wiring, not just the constant ────────────────────────
#[test]
fn chopharvest_live_adaptive_spec_wires_ge_spec_hp() {
    // reviewer-caught gap: chopharvest_spec_hp1 only pins the raw GE_SPEC constant; every other
    // test above hardcodes its own chopper()/starter() Troll fixture directly, bypassing
    // `tactics::plan` entirely. NONE of them would have caught the actual critical bug found
    // while live-smoke-testing this candidate: `tactics.rs`'s turn-1 adaptive spec selector
    // (`GE_CHOSEN_SPEC`) used to hardcode hp as the bare literal `0`, completely independent of
    // GE_SPEC -- bumping only the constant was a proven arena no-op (a live Boss-5 game showed
    // `mybuilds=...,3:2.2.0.2`, hp still 0, even after the GE_SPEC bump landed). The fix wired
    // `GE_SPEC.2` into that selector (tactics.rs, `plan_impl`). This test drives the REAL
    // adaptive path end-to-end (a single starter, no chopper trained yet -> `want_chopper` under
    // the live Tempo meta) and pins `plan.spec.2 == 1` -- so a future revert to a hardcoded
    // literal at that call site fails a test instead of silently shipping a no-op again.
    tactics::reset();
    let mut st = base_state();
    st.my_inventory = [0; 6];
    let plan = tactics::plan(&st, &[starter(0, 1, 2)]);
    assert_eq!(
        plan.spec.2, 1,
        "the LIVE turn-1 adaptive chopper spec's hp field must resolve to GE_SPEC.2 (1), not a \
         stale hardcoded 0 -- got spec={:?}",
        plan.spec
    );
}
