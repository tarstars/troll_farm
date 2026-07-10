//! v1.57.0-ringtune — three fixes to the AS-BUILT v1.56.0-ringfarm (code review E1/E2 +
//! a user game-watch finding), all scoped to the ring path (`ring_active`, i.e.
//! `plan.ring` non-empty — the only path any real game takes; see ringfarm.rs).
//!
//! FIX1 (E1): the build-ring PICK (band 78) must not outrank the funding bands (58-65)
//! while `plan.want_chopper` is true — fund the existential chopper first, THEN build the
//! ring. Only the tent-to-carry PICK/park-to-pick errand is suppressed; a banana already
//! in carry (band 88) still plants normally.
//!
//! FIX2 (E2): `plant_cell`'s nearest-empty-ring-cell search now prioritizes DIAGONAL ring
//! cells over ORTHOGONAL ones (role first, distance only breaks ties within a role) — the
//! pre-fix nearest-only key filled all four (map-distance-1) orthogonals before ever
//! touching a (map-distance-2, tent-impassable) diagonal, so the diagonal fruit/seed engine
//! (the scheme's whole point) was always built last.
//!
//! FIX3 (banana no-carry-in-advance, user game-watch): the anti-pattern was PICK-from-tent
//! then carry (sometimes backtracking past a ripe banana) to a plant cell.
//!   (i)  the build-ring PICK only fires when the chosen plant cell is immediately
//!        actionable (<=2 steps from the troll's CURRENT position) — ring cells are already
//!        <=farm_r(2) of the tent by construction (compute_ring), so this is the missing
//!        "near the troll" half of "near the troll AND near the tent".
//!   (ii) harvesting a ripe fruit the troll is standing on (band 75) now outranks the tent
//!        PICK — a harvested banana can be seeded/planted or banked exactly like a tent pick
//!        would, with zero extra travel, so preferring it strictly dominates.
//!
//! Shack at (3,2) in an open 8x5 room (identical geometry to ringfarm.rs), so all 8
//! Chebyshev-1 neighbours are walkable and the ring is the full 8: orthogonals
//! (3,1),(2,2),(4,2),(3,3); diagonals (2,1),(4,1),(2,3),(4,3).
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{compute_ring, Phase, Plan, RingRole};
use troll_farm::botmain::{bfs_distances, State, Tree, Troll};

const SHACK: (i32, i32) = (3, 2);

fn open_room() -> HashSet<(i32, i32)> {
    let mut w = HashSet::new();
    for x in 0..8 {
        for y in 0..5 {
            w.insert((x, y));
        }
    }
    w.remove(&SHACK); // shack cell impassable
    w
}

fn base_state() -> State {
    State {
        walkable: open_room(),
        my_shack: SHACK,
        opp_shack: (7, 2),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 60,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

/// A Plan carrying the REAL computed ring (via `compute_ring`), rest hand-set — identical
/// convention to ringfarm.rs's `ring_plan`. want_chopper/want_feeder/need_fund/need_iron
/// default to the inert (false) champion baseline; individual tests override the fields
/// they need to exercise.
fn base_plan(st: &State) -> Plan {
    let farm_d = bfs_distances(&st.walkable, &[st.my_shack]);
    let ring = compute_ring(&st.walkable, &farm_d, &None, st.my_shack, 2);
    Plan {
        shack: st.my_shack,
        farm_d,
        opp: st.opp_shack,
        have_iron: false,
        turns_rem: 240,
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
        ring,
        raid: false,
    }
}

/// non-chopper hand, empty-handed (isolates PICK/harvest/funding bands).
fn gatherer(id: i32, x: i32, y: i32) -> Troll {
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

/// non-chopper hand carrying one banana seed (isolates the plant band 88).
fn carrier(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 3,
        harvest_power: 0,
        chop_power: 0,
        carry: [0, 0, 0, 1, 0, 0],
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

fn ripe_plum(x: i32, y: i32) -> Tree {
    Tree {
        tree_type: "PLUM".into(),
        x,
        y,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    }
}

// ── FIX1 (E1): fund the chopper before building the ring ───────────────────────────────────
#[test]
fn ringtune_fund_chopper_before_ring() {
    // (a) want_chopper=true, empty ring (reachable, immediate ring cells everywhere), tent
    // stock present, and a ripe PLUM (a deficit-funding fruit type, need_fund[PLUM]=true)
    // reachable at (5,2) -- 5 steps away, outside the ring. Pre-fix, the build-ring PICK
    // (78) unconditionally outranks the funding band (58) so the gatherer would PICK the
    // tent banana instead of moving to fund the chopper. Post-fix (FIX1), want_chopper
    // suppresses the ring pick entirely -> the funding MoveTo wins.
    let mut st = base_state();
    st.my_inventory[3] = 3; // banked banana seeds in the tent
    st.trees = vec![ripe_plum(5, 2)];
    let mut plan = base_plan(&st);
    plan.want_chopper = true;
    plan.need_fund = [true, false, false]; // PLUM deficit
    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert_eq!(
        cmds[&0], "MOVE 0 5 2",
        "while want_chopper, funding must win over the build-ring PICK: {}",
        cmds[&0]
    );

    // (b) guard against over-suppression: once want_chopper is false, the ring pick
    // returns (same state, same reachable ring, same tent stock).
    let mut plan_b = base_plan(&st);
    plan_b.want_chopper = false;
    plan_b.need_fund = [true, false, false];
    let cmds_b = assign(&st, &plan_b, &[gatherer(0, 2, 2)]);
    assert_eq!(
        cmds_b[&0], "PICK 0 BANANA",
        "once want_chopper is false, the build-ring PICK must resume: {}",
        cmds_b[&0]
    );
}
