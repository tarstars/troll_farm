//! v1.58.0-trainfruit — a clustered training-fruit corner (lemon/plum/apple) carved out of
//! the v1.56/57 tent ring, planted early as FUNDING (grows our own training fuel, attacking
//! the documented funding-stall/lemon-wall). Builds on v1.57.0-ringtune (fund-first,
//! diagonal-priority, banana no-carry-in-advance).
//!
//! Shack at (3,2) in an open 8x5 room (identical geometry to ringfarm.rs/ringtune.rs), so all
//! 8 Chebyshev-1 neighbours are walkable and the base ring is the full 8: orthogonals
//! (3,1),(2,2),(4,2),(3,3); diagonals (2,1),(4,1),(2,3),(4,3). opp_shack at (7,2) (east) makes
//! the SW quadrant -- (3,3)=LEMON,(2,3)=PLUM,(2,2)=APPLE -- the farthest-from-opponent winner
//! on the fully open map (independently verified via a standalone BFS script, not just the
//! Rust implementation under test): SW/NW both score (count=3, dist_sum=18) vs NE/SE's
//! (count=3, dist_sum=12); SW wins the canonical-index tie-break (idx 2 < NW's idx 3).
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{compute_ring, Phase, Plan, RingRole};
use troll_farm::botmain::{bfs_distances, State, Tree, Troll, APPLE, LEMON, PLUM};

const SHACK: (i32, i32) = (3, 2);
const OPP: (i32, i32) = (7, 2);

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
        opp_shack: OPP,
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

/// A Plan carrying the REAL computed ring (via `compute_ring`, including the v1.58.0
/// training-corner carve-out), rest hand-set — identical convention to ringtune.rs's
/// `base_plan`. want_chopper/want_feeder/need_fund/need_iron/cost default to the inert
/// (false/zero) champion baseline; individual tests override the fields they need.
fn train_plan(st: &State) -> Plan {
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

// ── Test: on a fully open map, the training corner claims exactly 3 cells (the SW quadrant),
//    the other 5 stay banana (3 diagonal + 2 orthogonal) ─────────────────────────────────────
#[test]
fn trainfruit_5_banana_cells() {
    let st = base_state();
    let plan = train_plan(&st);
    assert_eq!(plan.ring.len(), 8, "sanity: the full 8-cell ring: {:?}", plan.ring);

    let by_role = |role: RingRole| -> Vec<(i32, i32)> {
        plan.ring
            .iter()
            .filter(|(_, r)| *r == role)
            .map(|(c, _)| *c)
            .collect()
    };
    let training: Vec<(i32, i32)> = plan
        .ring
        .iter()
        .filter(|(_, r)| r.train_fruit().is_some())
        .map(|(c, _)| *c)
        .collect();
    assert_eq!(
        training.len(),
        3,
        "exactly 3 training-corner cells: {:?}",
        plan.ring
    );
    assert_eq!(by_role(RingRole::Diagonal).len(), 3, "{:?}", plan.ring);
    assert_eq!(by_role(RingRole::Orthogonal).len(), 2, "{:?}", plan.ring);

    // the specific SW-quadrant winner (farthest total BFS distance from opp_shack (7,2),
    // independently verified via a standalone BFS script -- see module doc comment).
    assert!(
        plan.ring.contains(&((3, 3), RingRole::TrainLemon)),
        "{:?}",
        plan.ring
    );
    assert!(
        plan.ring.contains(&((2, 3), RingRole::TrainPlum)),
        "{:?}",
        plan.ring
    );
    assert!(
        plan.ring.contains(&((2, 2), RingRole::TrainApple)),
        "{:?}",
        plan.ring
    );
    // the surviving 5 banana cells keep their original roles.
    assert!(plan.ring.contains(&((2, 1), RingRole::Diagonal)), "{:?}", plan.ring);
    assert!(plan.ring.contains(&((4, 1), RingRole::Diagonal)), "{:?}", plan.ring);
    assert!(plan.ring.contains(&((4, 3), RingRole::Diagonal)), "{:?}", plan.ring);
    assert!(plan.ring.contains(&((3, 1), RingRole::Orthogonal)), "{:?}", plan.ring);
    assert!(plan.ring.contains(&((4, 2), RingRole::Orthogonal)), "{:?}", plan.ring);
}

// ── Test: an obstructed ideal corner is never chosen; the corner-selection degrades to a
//    quadrant whose 3 cells are ALL farm_eligible ───────────────────────────────────────────
#[test]
fn trainfruit_corner_is_compact() {
    // Block (2,2) (a rock/water cell in the real game): removed from `walkable` entirely.
    // (2,2) is shared by BOTH the SW quadrant (the fully-open winner above) and the NW
    // quadrant, so blocking it degrades BOTH to only 2 eligible cells; NE and SE are
    // unaffected (still fully eligible, count=3) and NE wins on the canonical-index
    // tie-break (NE=idx0 < SE=idx1) -- independently verified via a standalone BFS script.
    let mut st = base_state();
    st.walkable.remove(&(2, 2));
    let plan = train_plan(&st);

    // (2,2) is not walkable at all -> excluded from the ring entirely (not even a banana
    // candidate), and NOT substituted for -- the brief's "never on a far cell" guarantee.
    assert!(
        !plan.ring.iter().any(|(c, _)| *c == (2, 2)),
        "blocked cell must not appear in the ring at all: {:?}",
        plan.ring
    );

    // the WINNING corner: NE, all 3 cells present and fully eligible.
    assert!(
        plan.ring.contains(&((3, 1), RingRole::TrainLemon)),
        "{:?}",
        plan.ring
    );
    assert!(
        plan.ring.contains(&((4, 1), RingRole::TrainPlum)),
        "{:?}",
        plan.ring
    );
    assert!(
        plan.ring.contains(&((4, 2), RingRole::TrainApple)),
        "{:?}",
        plan.ring
    );

    // the degraded corners (SW/NW, only 2 eligible cells each) are NOT chosen: their
    // surviving cells stay plain banana roles, not retagged as training.
    assert!(
        plan.ring.contains(&((2, 1), RingRole::Diagonal)),
        "NW's surviving cell must stay banana, not be force-fit into the training corner: {:?}",
        plan.ring
    );
    assert!(
        plan.ring.contains(&((2, 3), RingRole::Diagonal)),
        "SW's surviving cell must stay banana, not be force-fit into the training corner: {:?}",
        plan.ring
    );
    assert!(
        plan.ring.contains(&((3, 3), RingRole::Orthogonal)),
        "SW's surviving cell must stay banana, not be force-fit into the training corner: {:?}",
        plan.ring
    );
}

// ── Reviewer fix (deferred from v1.57, FIX2 x FIX3(i)): a far diagonal-priority pick must
//    not idle a builder standing on/near an immediate empty cell of either role ───────────────
#[test]
fn trainfruit_reviewer_fix_immediate_fallback_over_far_diagonal() {
    // Carrier stands on the orthogonal ring cell (4,2) (untouched by the SW training corner
    // — see trainfruit_5_banana_cells). Every ring cell is treed EXCEPT (4,1) [diagonal,
    // d=1, immediate] and (4,2) itself [orthogonal, d=0]; (4,3) is filled to break the
    // (4,1)/(4,3) diagonal tie the same way ringtune_diagonal_planted_first does. The
    // remaining diagonal (2,1) is left EMPTY too but is FAR (d=3, beyond RING_PICK_STEPS via
    // (4,2)) — so pre-fix, diagonal-priority (role_rank compared before distance) would still
    // consider (2,1) a candidate... but since (4,1) [also a diagonal] is CLOSER, (4,1) wins
    // the ORIGINAL min_by_key regardless of the reviewer fix. To isolate the fix, this test
    // instead fills every diagonal except the training corner's — i.e. we need the sole
    // remaining empty diagonal to be FAR, and a nearer orthogonal to be the true fallback. So:
    // fill (4,1) too, leaving (2,1) [diagonal, FAR, d=3] as the only empty diagonal, and
    // (4,2) [orthogonal, d=0, the carrier's own cell] as an empty orthogonal, with the carrier
    // EMPTY-HANDED (a gatherer, not a carrier) so band 78 (build-ring PICK) is the one at
    // stake, not band 88.
    //
    // Pre-fix: priority_pick = (2,1) (role_rank 0 beats every orthogonal regardless of
    // distance), d[(2,1)] = 3 > RING_PICK_STEPS(2) -> plant_immediate=false -> the build-ring
    // PICK is suppressed entirely -> the gatherer (standing on an empty, immediate, buildable
    // orthogonal!) has no ring-building move at all this turn -- it idles (band 10 park).
    // Post-fix: since (2,1) is far, fall back to the nearest IMMEDIATE cell of either role:
    // (4,2) itself (d=0) -> plant_cell=(4,2), immediate -> "PICK 0 BANANA" fires (the gatherer
    // is shack-adjacent: manhattan((4,2),(3,2))==1).
    let mut st = base_state();
    st.my_inventory[3] = 3; // tent bananas
    st.trees = vec![
        banana(4, 1, 2),
        banana(4, 3, 2), // both remaining non-corner diagonals filled
        banana(3, 1, 2), // the remaining non-corner orthogonal filled
        // training-corner cells (2,2)/(2,3)/(3,3) intentionally left untouched (irrelevant to
        // banana placement -- excluded from banana_ring_candidates regardless of tree
        // presence); (2,1) [diagonal, far, d=3] and (4,2) [orthogonal, d=0] are the only
        // EMPTY banana-role cells.
    ];
    let plan = train_plan(&st);
    // sanity: (2,1) is the far empty diagonal, (4,2) is the immediate empty orthogonal.
    assert!(plan.ring.contains(&((2, 1), RingRole::Diagonal)), "{:?}", plan.ring);
    assert!(plan.ring.contains(&((4, 2), RingRole::Orthogonal)), "{:?}", plan.ring);

    let cmds = assign(&st, &plan, &[gatherer(0, 4, 2)]);
    assert_eq!(
        cmds[&0], "PICK 0 BANANA",
        "reviewer fix: a far diagonal-priority pick must fall back to the immediate orthogonal \
         the gatherer stands on, not idle: {}",
        cmds[&0]
    );
}

// ── Test 1 (brief): training corner is planted during funding, not just banana ────────────
#[test]
fn trainfruit_corner_planted() {
    // Funding phase (want_chopper), empty training corner, LEMON seeds in the tent, no
    // surplus concern (cost=0 so the investment guard trivially passes). A gatherer stands
    // shack-adjacent; the training-corner cell (2,2)=TrainApple is the nearest EMPTY training
    // cell reachable... actually APPLE inventory is 0 here, so give inv[LEMON] instead and
    // check the (3,3)=TrainLemon cell. No banana in inventory, so band 78 can't fire, isolating
    // the new training-fruit PICK/PLANT bands.
    let mut st = base_state();
    st.my_inventory[LEMON] = 3;
    let mut plan = train_plan(&st);
    plan.want_chopper = true;
    plan.cost = [0; 6];
    plan.need_fund = [false; 3];

    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert!(
        cmds[&0].contains("LEMON"),
        "a training-fruit PICK/PLANT (or travel toward it) targeting LEMON must be offered \
         (not a vacuous non-banana idle/park): {}",
        cmds[&0]
    );
}

// ── Test 3 (brief): training corner is NOT suppressed by want_chopper; the banana ring IS ──
#[test]
fn trainfruit_corner_before_banana() {
    // Funding phase, BOTH a banana seed and a lemon seed in the tent, fully empty ring.
    // FIX1 (v1.57) suppresses the banana build-ring PICK during want_chopper; this candidate
    // must NOT suppress the training-fruit PICK the same way. A single gatherer can only take
    // one action, so this proves the priority ORDER: training-fruit must win over (or at
    // least not be blocked by) the same want_chopper gate that blocks banana.
    let mut st = base_state();
    st.my_inventory[3] = 3; // banana
    st.my_inventory[LEMON] = 3;
    let mut plan = train_plan(&st);
    plan.want_chopper = true;
    plan.cost = [0; 6];
    plan.need_fund = [false; 3];

    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert!(
        !cmds[&0].contains("BANANA"),
        "banana ring-build must stay suppressed during want_chopper (v1.57 FIX1): {}",
        cmds[&0]
    );
    assert!(
        cmds[&0].contains("LEMON"),
        "training-fruit build must NOT be suppressed during want_chopper: {}",
        cmds[&0]
    );
}

// ── Test 4 (brief): investment guard — train now, don't plant the last seed ────────────────
#[test]
fn trainfruit_train_now_over_plant_last_seed() {
    // want_chopper pending, cost[LEMON] == inv[LEMON] exactly (our LAST lemon would be
    // needed to train NOW) -- the training-fruit PICK must be suppressed (no surplus beyond
    // the pending hand's cost). The gatherer should fall through to something else (anything
    // that is NOT a LEMON pick/plant).
    let mut st = base_state();
    st.my_inventory[LEMON] = 5;
    let mut plan = train_plan(&st);
    plan.want_chopper = true;
    plan.cost = [0, 5, 0, 0, 0, 0]; // LEMON cost == inv[LEMON]: no surplus
    plan.need_fund = [false, false, false];

    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert!(
        !cmds[&0].contains("LEMON"),
        "must not plant/pick the last lemon when training needs it now (no surplus): {}",
        cmds[&0]
    );

    // guard against over-suppression: give a 1-unit surplus (6 vs cost 5) -> the PICK resumes.
    let mut st2 = base_state();
    st2.my_inventory[LEMON] = 6;
    let mut plan2 = train_plan(&st2);
    plan2.want_chopper = true;
    plan2.cost = [0, 5, 0, 0, 0, 0];
    plan2.need_fund = [false, false, false];
    let cmds2 = assign(&st2, &plan2, &[gatherer(0, 2, 2)]);
    assert!(
        cmds2[&0].contains("LEMON"),
        "a genuine surplus (inv > cost) must still be investable: {}",
        cmds2[&0]
    );
}

// ── Test 6 (brief): band-ordering proof — training-fruit can't displace real funding/chop ──
#[test]
fn trainfruit_band_ordering_does_not_displace_real_work() {
    // (a) a real funding fetch (a ripe, deficit PLUM tree, band 58/60) must win over an
    // available training-fruit plant opportunity for the SAME troll, even though both are
    // reachable. want_chopper + need_fund[PLUM] + a ripe plum at (5,2) (5 steps away, off the
    // ring) + a lemon seed available for the training corner (0 steps of travel penalty
    // difference would otherwise make the pick attractive) -- funding must still win.
    let mut st = base_state();
    st.my_inventory[LEMON] = 3;
    st.trees = vec![Tree {
        tree_type: "PLUM".into(),
        x: 5,
        y: 2,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    }];
    let mut plan = train_plan(&st);
    plan.want_chopper = true;
    plan.cost = [0; 6];
    plan.need_fund = [true, false, false]; // PLUM deficit
    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert_eq!(
        cmds[&0], "MOVE 0 5 2",
        "a real funding fetch (deficit PLUM) must outrank the training-fruit plant/pick: {}",
        cmds[&0]
    );

    // (b) banking must not be displaced: a FULL troll (free_capacity==0) already carrying a
    // training-fruit seed (not banana) must still be banked (band 80), never diverted to
    // plant it in the corner. Band 80's existing "carried banana with a plant spot" exemption
    // checks `carry[BANANA]` ONLY, so a lemon-carrying full troll gets no such exemption and
    // must fall through to the unconditional full->bank rule -- this is the direct "not above
    // banking" numeric guarantee the brief requires (TRAIN_PLANT_BAND(56) < the bank band(80)
    // by construction; this proves it behaviorally, not just by reading the constant).
    let st_b = base_state();
    let mut full_carrier = gatherer(0, 2, 2);
    full_carrier.carry[LEMON] = 1; // carry_capacity=1 (from `gatherer`) -> free_capacity()==0
    let plan_b = train_plan(&st_b);
    let cmds_b = assign(&st_b, &plan_b, &[full_carrier]);
    assert!(
        !cmds_b[&0].contains("PLANT") && !cmds_b[&0].contains("PICK"),
        "a full troll carrying a training-fruit seed must be banked, not diverted to plant it: {}",
        cmds_b[&0]
    );
}
