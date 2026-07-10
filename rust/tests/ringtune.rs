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
    let opp_d = bfs_distances(&st.walkable, &[st.opp_shack]);
    let ring = compute_ring(&st.walkable, &farm_d, &None, st.my_shack, 2, &opp_d);
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

// ── FIX2 (E2): diagonal-priority placement ─────────────────────────────────────────────────
#[test]
fn ringtune_diagonal_planted_first() {
    // v1.58.0-trainfruit ADJUSTED this fixture (documented reason, per the brief): on this
    // exact open-room/shack/opp geometry, compute_ring's new training-corner carve-out now
    // claims the SW quadrant -- (3,3)=TrainLemon, (2,3)=TrainPlum, (2,2)=TrainApple (all 3
    // fully eligible, farthest total BFS distance from opp_shack (7,2) among the 4
    // candidate quadrants -- see the trainfruit_corner_is_compact test for the standalone
    // proof). The ORIGINAL test stood the carrier on (2,2), which is now a training cell,
    // not a banana ring slot -- so this fixture is now shifted to the SURVIVING orthogonal
    // (4,2)/diagonal (4,1) pair (the other two ring cells, (2,1) and (4,1)(4,3), are
    // untouched by the SW carve-out), preserving the EXACT original property under test:
    // a carrier standing on an orthogonal (d=0) must still MOVE to a farther-but-diagonal
    // empty cell, never plant in place.
    //
    // A carrier (carrying one banana -> exercises the plant band 88 directly, no PICK/harvest
    // interaction) stands ON the orthogonal ring cell (4,2). The ring is empty EXCEPT for a
    // tree on the diagonal (4,3), which BREAKS the (4,1)/(4,3) diagonal tie so exactly one
    // nearest empty diagonal, (4,1), remains -- a deterministic target (no tie_mix hashing in
    // the assertion). Empty ring cells reachable from (4,2): orthogonal (4,2) d=0, (3,1) d=2;
    // diagonal (4,1) d=1, (2,1) d=3 (training cells (2,2)/(2,3)/(3,3) excluded entirely).
    //   Pre-fix (nearest-only key): (4,2) at d=0 wins -> PLANT in place on the ORTHOGONAL.
    //   Post-fix (role_rank first): every diagonal outranks every orthogonal, and (4,1) is the
    //   uniquely nearest empty diagonal -> MOVE toward it. This is the E2 engine: build the
    //   diagonal ripe/seed cells before refilling orthogonals.
    let mut st = base_state();
    st.trees = vec![banana(4, 3, 2)]; // fruitless: breaks the (4,1)/(4,3) diagonal tie only
    let plan = base_plan(&st);
    // sanity: (4,1) diagonal and (4,2) orthogonal are both in the ring, untouched by the SW
    // training corner (documented above).
    assert!(plan.ring.contains(&((4, 1), RingRole::Diagonal)), "{:?}", plan.ring);
    assert!(plan.ring.contains(&((4, 2), RingRole::Orthogonal)), "{:?}", plan.ring);
    let cmds = assign(&st, &plan, &[carrier(0, 4, 2)]);
    assert_eq!(
        cmds[&0], "MOVE 0 4 1",
        "an empty diagonal (4,1) must be chosen before the orthogonal the carrier stands on: {}",
        cmds[&0]
    );
}

// ── FIX3(i): banana NO-CARRY-IN-ADVANCE — no PICK unless the plant is immediate ─────────────
#[test]
fn ringtune_no_pick_when_plant_not_immediate() {
    // A gatherer is shack-adjacent at (2,2), the tent holds bananas, but every ring cell is
    // treed EXCEPT the far diagonal (4,3) — d=3 from (2,2), outside the <=2-step immediacy
    // window (RING_PICK_STEPS). plant_cell resolves to (4,3) (the only empty cell). Pre-fix the
    // build-ring PICK fires whenever the ring has ANY empty cell -> "PICK 0 BANANA" (then the
    // troll would carry that banana 3 steps to plant it). Post-fix (FIX3(i)) the PICK is gated
    // on the chosen plant cell being <=2 steps away, so the gatherer does NOT PICK — no
    // carry-in-advance. The 7 filler bananas are fruitless (no harvest band competes).
    let mut st = base_state();
    st.my_inventory[3] = 3; // tent bananas
    st.trees = vec![
        banana(3, 1, 2),
        banana(2, 2, 2),
        banana(4, 2, 2),
        banana(3, 3, 2), // all four orthogonals
        banana(2, 1, 2),
        banana(4, 1, 2),
        banana(2, 3, 2), // three of four diagonals
                         // (4,3) left EMPTY — the only plantable cell, far (d=3) from the gatherer at (2,2)
    ];
    let plan = base_plan(&st);
    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert!(
        !cmds[&0].starts_with("PICK"),
        "no carry-in-advance: gatherer must NOT PICK a tent banana to haul 3 steps to the only \
         (far) empty ring cell: {}",
        cmds[&0]
    );
}

// ── FIX3(ii): prefer a ripe banana at/adjacent to the troll over a tent PICK ─────────────────
#[test]
fn ringtune_harvest_ripe_over_tent_pick() {
    // A gatherer at (2,2) (shack-adjacent) has: tent bananas, empty near ring cells (so pre-fix
    // the build-ring PICK would fire), and a RIPE banana one ortho-step away at (2,1). A
    // harvested banana seeds or banks with zero extra travel, so it must beat running a tent
    // errand — and this is exactly the "walked PAST ripe bananas to fetch tent stock" anti-
    // pattern the user watched. Pre-fix: PICK (78) beats the seed-move (52) -> "PICK 0 BANANA".
    // Post-fix (FIX3(ii)): the ring PICK is suppressed while a ripe banana is at/adjacent, so
    // the band-52 seed-move toward (2,1) wins -> the troll goes to harvest it, not PICK.
    let mut st = base_state();
    st.my_inventory[3] = 3; // tent bananas
    st.trees = vec![ripe_banana(2, 1)]; // ripe, one ortho-step from the gatherer at (2,2)
    let plan = base_plan(&st);
    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert_eq!(
        cmds[&0], "MOVE 0 2 1",
        "a ripe adjacent banana must be harvested (moved-to), not passed over to PICK tent stock: {}",
        cmds[&0]
    );
}
