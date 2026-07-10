//! v1.58.0-trainfruit — a clustered training-fruit corner (lemon/plum/apple) carved out of
//! the tent ring, planted early as FUNDING (grows our own training fuel, attacking the
//! documented funding-stall/lemon-wall). Base = v1.56.0-ringfarm (build-ring PICK 78 fires
//! whenever the ring has an empty cell, no want_chopper suppression, flat nearest-only
//! plant_cell placement) -- NOT v1.57.0-ringtune, whose E1/E2/FIX3 tuning was arena-reverted
//! at ~-2.4 on 2026-07-10 (see docs/silver-experiment-log.md). This file originally targeted
//! v1.57; three tests were adjusted when the base changed (documented at each site): the
//! reviewer-fix test was dropped (its bug requires v1.57's diagonal-priority, which doesn't
//! exist here), and trainfruit_corner_before_banana's premise was corrected (v1.56 has no
//! want_chopper suppression to prove coexistence with, for banana OR training-fruit).
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
use troll_farm::botmain::{bfs_distances, State, Tree, Troll, IRON, LEMON};

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

// NOTE: the brief's deferred v1.57 reviewer fix (FIX2 x FIX3(i): a far diagonal-priority
// plant_cell pick starving a nearer immediate cell of either role) is DROPPED here, not
// merely untested. v1.57.0-ringtune (which introduced FIX2's diagonal-priority placement,
// the only mechanism that fix's bug could occur in) was arena-reverted at ~-2.4 on
// 2026-07-10 (see docs/silver-experiment-log.md); this candidate is rebased on plain
// v1.56.0-ringfarm, whose plant_cell chooser is the original flat nearest-only
// `min_by_key((d, tie_mix))` (see planner.rs) — there is no diagonal-priority to ever
// prefer a far cell over a near one, so the bug this fix targeted cannot occur on this
// base. (An earlier revision of this file had a dedicated test here that passed against
// the rebased code, but only vacuously -- the flat nearest-only key trivially picks the
// nearest cell regardless of role, so the fix's own fallback logic was never exercised.
// Removed rather than kept as dead weight.)

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

// ── Test 3 (brief): training corner building is NOT gated on want_chopper ─────────────────
#[test]
fn trainfruit_corner_before_banana() {
    // Base = v1.56.0-ringfarm (v1.57.0-ringtune's E1/FIX1 want_chopper suppression of the
    // banana ring-build was arena-reverted at ~-2.4, see docs/silver-experiment-log.md
    // 2026-07-10 -- there is no want_chopper-based suppression mechanism on this base at
    // all, for banana OR training-fruit; band 78 (banana) simply outranks band 56/54
    // (training-fruit) whenever BOTH are simultaneously available, exactly as it outranks
    // every other sub-78 band). So the meaningful, base-appropriate property to prove is:
    // the training-fruit PLANT/PICK is NEVER gated on want_chopper -- it fires purely off
    // corner-cell availability + the investment guard, during funding exactly like any
    // other time. Isolate it by withholding banana stock entirely (so band 78 is not even
    // a candidate) and confirm the training-fruit action still fires while want_chopper.
    let mut st = base_state();
    st.my_inventory[LEMON] = 3; // no banana in the tent at all -- isolates the training path
    let mut plan = train_plan(&st);
    plan.want_chopper = true;
    plan.cost = [0; 6];
    plan.need_fund = [false; 3];

    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert!(
        cmds[&0].contains("LEMON"),
        "training-fruit build must fire during want_chopper (not gated on it at all): {}",
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

    // (b) banking must not be displaced BY A HIGHER-VALUE candidate for a resource that has
    // NOWHERE to go: a FULL troll (free_capacity==0) carrying a training-fruit seed whose
    // designated corner cell is UNAVAILABLE (all 3 corner cells already treed) must still be
    // banked (band 80) -- exactly the banana `plant_cell.is_some()` gate's logic, applied to
    // training fruit. This proves TRAIN_PLANT_BAND(56) never displaces banking(80) when
    // there's nothing plantable to displace it FOR.
    //
    // (Earlier revision of this test carried a lemon with an EMPTY, available corner cell and
    // asserted the command wasn't PLANT/PICK -- that passed, but for the wrong reason: once
    // band 80 correctly exempts a carried seed with a ready destination (the
    // trainfruit_full_carrier_walks_to_ready_corner fix below), the troll instead MOVEs
    // toward it, which also doesn't contain "PLANT"/"PICK" literally, making the old
    // assertion vacuous. Corrected to actually block the destination, isolating the
    // still-true "no plantable target -> bank" invariant.)
    let mut st_b = base_state();
    st_b.trees = vec![
        Tree { tree_type: "LEMON".into(), x: 3, y: 3, size: 1, health: 6, fruits: 0, cooldown: 0 },
        Tree { tree_type: "PLUM".into(), x: 2, y: 3, size: 1, health: 6, fruits: 0, cooldown: 0 },
        Tree { tree_type: "APPLE".into(), x: 2, y: 2, size: 1, health: 11, fruits: 0, cooldown: 0 },
    ]; // all 3 training-corner cells occupied -> no reachable destination for the carried lemon
    let mut full_carrier = gatherer(0, 3, 1); // (3,1): a plain Orthogonal cell, shack-adjacent (manhattan==1), untouched by the corner
    full_carrier.carry[LEMON] = 1; // carry_capacity=1 (from `gatherer`) -> free_capacity()==0
    let plan_b = train_plan(&st_b);
    let cmds_b = assign(&st_b, &plan_b, &[full_carrier]);
    assert_eq!(
        cmds_b[&0], "DROP 0",
        "a full troll carrying a training-fruit seed with NO available corner cell must bank \
         it (band 80), not hold it indefinitely: {}",
        cmds_b[&0]
    );
}

// ── Regression (bug found via local simulation, not a hand-built fixture): a full troll
//    carrying a training-fruit seed WITH a ready corner cell must WALK there, not bank ────────
#[test]
fn trainfruit_full_carrier_walks_to_ready_corner_instead_of_banking() {
    // The actual bug: band 80 (full->bank) originally only recognized a carried BANANA's
    // plant_cell exemption, never a carried training-fruit seed's. So a capacity-1 troll
    // that just PICKed a training seed (free_capacity instantly 0) would be banked the very
    // next turn by band 80 (80 > 56) -- discovered by running the real bot binary through
    // local simulated games (not caught by ANY hand-built fixture in this file, since they
    // all used a troll with enough spare capacity to dodge band 80 entirely): the bot's
    // actual command stream showed "PICK 0 APPLE" immediately followed by "DROP 0" on the
    // very next turn, every time, so the training-corner tree was NEVER ACTUALLY PLANTED in
    // 20/20 fresh local games pre-fix (0/20 planted a training-corner tree; 10/20 post-fix).
    let st = base_state();
    let mut full_carrier = gatherer(0, 2, 2); // stands on (2,2) = TrainApple, but carries LEMON
    full_carrier.carry[LEMON] = 1; // carry_capacity=1 -> free_capacity()==0 (mirrors the bug)
    let plan = train_plan(&st);
    let cmds = assign(&st, &plan, &[full_carrier]);
    assert_eq!(
        cmds[&0], "MOVE 0 3 3",
        "a full troll carrying a training-fruit seed with a READY corner cell ((3,3)=TrainLemon, \
         empty) must walk there to plant it, not bank the seed for a single point: {}",
        cmds[&0]
    );
}

// ── Regression (2nd bug found via the SAME local-simulation comparison): the pre-existing
//    deficit-fruit funding loop (bands 58-65) never branched on "standing here", and never
//    checked free_capacity -- a self-targeting MoveTo (no-op, forever) or a full troll being
//    lured onward to fruit it can't collect. v1.56.0-ringfarm essentially never triggers this
//    (it never grows PLUM/LEMON/APPLE near where the troll parks); the training corner
//    deliberately does, so THIS candidate hit it often enough to permanently strand the
//    chopper's funding on 34/60 paired local seeds (baseline: 0/60) before the fix ────────────
#[test]
fn trainfruit_funding_harvests_standing_deficit_fruit_not_self_move() {
    // Standing on a ripe DEFICIT fruit tree must HARVEST it in place, not emit a
    // self-targeting MoveTo (which never actually collects the fruit and repeats forever,
    // permanently blocking the very funding this band exists to serve).
    let mut st = base_state();
    st.trees = vec![Tree {
        tree_type: "PLUM".into(),
        x: 6,
        y: 3,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    }]; // off the ring entirely -- isolates the funding band from any ring interaction
    let mut plan = train_plan(&st);
    plan.want_chopper = true;
    plan.cost = [0; 6];
    plan.need_fund = [true, false, false]; // PLUM deficit
    let cmds = assign(&st, &plan, &[gatherer(0, 6, 3)]);
    assert_eq!(
        cmds[&0], "HARVEST 0",
        "standing on a ripe deficit fruit must harvest it in place, not self-move: {}",
        cmds[&0]
    );
}

#[test]
fn trainfruit_full_troll_not_lured_by_distant_deficit_fruit() {
    // A FULL troll (free_capacity==0, carrying IRON here -- deliberately neither banana nor
    // a training-fruit type, so neither band-80 exemption applies) must not be lured toward
    // a distant ripe DEFICIT fruit tree it cannot actually collect once it arrives (the
    // funding loop's MoveTo case never checked free_capacity pre-fix) -- band 80 (bank) must
    // win instead, exactly as it does for any other already-full troll.
    let mut st = base_state();
    st.trees = vec![Tree {
        tree_type: "PLUM".into(),
        x: 5,
        y: 2,
        size: 4,
        health: 6,
        fruits: 3,
        cooldown: 0,
    }]; // reachable but NOT at the troll's position
    let mut plan = train_plan(&st);
    plan.want_chopper = true;
    plan.cost = [0; 6];
    plan.need_fund = [true, false, false]; // PLUM deficit
    let mut full_gatherer = gatherer(0, 3, 1); // shack-adjacent (manhattan==1) -> DROP renders directly
    full_gatherer.carry[IRON] = 1; // capacity=1 -> free_capacity()==0; not banana/training-fruit
    let cmds = assign(&st, &plan, &[full_gatherer]);
    assert_eq!(
        cmds[&0], "DROP 0",
        "a full troll must not be lured toward a distant deficit fruit it cannot collect: {}",
        cmds[&0]
    );
}
