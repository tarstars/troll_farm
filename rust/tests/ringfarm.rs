//! v1.56.0-ringfarm — the structured 8-cell tent-ring farm (user's farm-geometry scheme).
//!
//! DIAGONAL ring cells (Chebyshev-diagonal to the shack) = the ripe fruit/seed engine: kept
//! standing, felled ONLY in the endgame (`turns_rem <= GE_LIQ_T`) or under a raid (an enemy
//! troll within RING_RAID_R of the shack). ORTHOGONAL ring cells = the wood/cut cycle: felled
//! at `farm_fell` for wood, replanted. The ring IS the farm, built EARLY: while the ring has
//! empty cells and a banana is available, the pick->plant loop (build-ring band 78) outranks
//! distant foraging (harvest 75, seed-move 52) but never banking (80/95) or planting (88).
//!
//! Shack at (3,2) in an open 8x5 room, so all 8 Chebyshev-1 neighbours are walkable and the
//! ring is the full 8: orthogonals (3,1),(2,2),(4,2),(3,3); diagonals (2,1),(4,1),(2,3),(4,3).
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{compute_ring, plan_with_meta, Meta, Phase, Plan, RingRole};
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

/// A Plan carrying the REAL computed ring (via `compute_ring`) so tests exercise the true
/// geometry, with the rest hand-set (race_check/pressurefarm isolation style). farm_fell=2 is
/// the live champion value (tactics.rs `if econ_b {3} else {2}` with econ_b=false).
fn ring_plan(st: &State) -> Plan {
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

/// non-chopper hand, empty-handed (isolates PICK/harvest bands).
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

// ── Test 1: placement — orthogonal ring cells are valid plant targets (no longer avoided) ──
#[test]
fn ring_placement_diag_and_ortho() {
    // A carrier stands ON the orthogonal ring cell (4,2), carrying a banana; the ring is empty.
    // Post-fix: the ring IS the farm, so the nearest empty ring cell (its own cell (4,2), d=0)
    // is the plant target -> PLANT in place on the ORTHOGONAL cell. Pre-fix: the old plant_cell
    // chooser ranks by (map-dist + wet + geo) with geo = (bank_adj? +3) + (diag? -1), which
    // PENALISES the orthogonal bank cell (4,2) [+3] and REWARDS a diagonal like (4,1) [-1], so
    // the carrier walks off to plant a diagonal ("MOVE 0 4 1") instead of the orthogonal it
    // stands on -- exactly the "orthogonals avoided" behaviour this scheme replaces.
    let st = base_state();
    let plan = ring_plan(&st);
    assert!(
        plan.ring.contains(&((4, 2), RingRole::Orthogonal)),
        "sanity: (4,2) is an orthogonal ring cell: {:?}",
        plan.ring
    );
    let cmds = assign(&st, &plan, &[carrier(0, 4, 2)]);
    assert_eq!(
        cmds[&0], "PLANT 0 BANANA",
        "carrier on an empty orthogonal ring cell must plant it (orthogonals no longer avoided): {}",
        cmds[&0]
    );
}

// ── Test 2: build the ring EARLY, before distant foraging ──────────────────────────────────
#[test]
fn ring_built_before_distant_forage() {
    // Empty ring, tent holds banana seeds, and a distant ripe banana tree sits at (7,4). An
    // empty-handed gatherer stands shack-adjacent at (2,2) (an orthogonal ring cell). Post-fix:
    // build-ring PICK (band 78, ring incomplete + tent stock + a reachable empty ring cell)
    // outranks the distant-seed-move (band 52) -> "PICK 0 BANANA". Pre-fix: PICK is band 50,
    // below the distant seed-move (52*BAND - eta) -> the gatherer treks toward (7,4) instead.
    let mut st = base_state();
    st.my_inventory[3] = 3; // banked banana seeds in the tent
    st.trees = vec![ripe_banana(7, 4)]; // distant forage bait
    let plan = ring_plan(&st);
    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert_eq!(
        cmds[&0], "PICK 0 BANANA",
        "gatherer must build the local ring (PICK) instead of trekking to distant fruit: {}",
        cmds[&0]
    );
}

// ── Test 3: cut the orthogonal, KEEP the diagonal (no endgame, no raid) ────────────────────
#[test]
fn cut_orthogonal_keep_diagonal() {
    // A grown ring: orthogonal (4,2) and diagonal (2,1) both at fell-size (2 == farm_fell). A
    // chopper sits at (2,0), NEAREST to the diagonal (2,1). No endgame, no raid. Post-fix: the
    // diagonal is the protected ripe engine (not a fell candidate) -> the chopper must trek to
    // the ORTHOGONAL (4,2) instead. Pre-fix: both are plain farm bananas, so the chopper takes
    // the nearer diagonal (2,1) -- the behaviour this scheme forbids.
    let mut st = base_state();
    st.trees = vec![banana(4, 2, 2), banana(2, 1, 2)];
    let plan = ring_plan(&st);
    let cmds = assign(&st, &plan, &[chopper(2, 2, 0)]);
    assert!(
        cmds[&2].contains("4 2"),
        "chopper must cut the orthogonal ring cell (4,2): {}",
        cmds[&2]
    );
    assert!(
        !cmds[&2].contains("2 1"),
        "chopper must NOT fell the protected diagonal ring banana (2,1): {}",
        cmds[&2]
    );
}

// ── Test 4: endgame liquidation RELEASES the diagonal ──────────────────────────────────────
#[test]
fn diagonal_felled_in_endgame() {
    // Same grown ring, but liquidation (turns_rem <= GE_LIQ_T). The diagonal protection is
    // released -> the chopper takes the NEAREST fellable tree, the diagonal (2,1) at d=1, over
    // the farther orthogonal (4,2). Proves the endgame exception makes the diagonal a live
    // fell candidate.
    let mut st = base_state();
    st.trees = vec![banana(4, 2, 2), banana(2, 1, 2)];
    let mut plan = ring_plan(&st);
    plan.turns_rem = 30; // <= GE_LIQ_T (34)
    plan.liquidation = true;
    let cmds = assign(&st, &plan, &[chopper(2, 2, 0)]);
    assert!(
        cmds[&2].contains("2 1"),
        "endgame must release the diagonal for felling (nearest wins): {}",
        cmds[&2]
    );
}

// ── Test 5: an active raid RELEASES the diagonal ───────────────────────────────────────────
#[test]
fn diagonal_felled_under_raid() {
    // Same grown ring, no endgame, but an active raid (enemy within RING_RAID_R of the shack).
    // The diagonal protection is released defensively -> the chopper fells the nearest, the
    // diagonal (2,1). Contrast with cut_orthogonal_keep_diagonal (raid=false), which keeps it.
    let mut st = base_state();
    st.trees = vec![banana(4, 2, 2), banana(2, 1, 2)];
    st.opp_trolls = vec![chopper(9, 5, 2)]; // ~2 steps from the shack (within RING_RAID_R=4)
    let mut plan = ring_plan(&st);
    plan.raid = true;
    let cmds = assign(&st, &plan, &[chopper(2, 2, 0)]);
    assert!(
        cmds[&2].contains("2 1"),
        "an active raid must release the diagonal for defensive felling: {}",
        cmds[&2]
    );
}

// ── Test 6: the ring respects the front door on a chokepoint map ───────────────────────────
#[test]
fn ring_respects_frontdoor() {
    // Shack (5,2) straddles a vertical wall at x=5 (west block x0..=4, east block x6..=10, one
    // detour gap at the bottom). The enemy sits east, so the front door is the WEST neighbour
    // (4,2); `farm_eligible` then admits only the west-side ring cells. The east-side ring cells
    // ((6,1),(6,2),(6,3)) are 18 real steps away (door_d >> farm_r) and must be EXCLUDED -- no
    // straddle.
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..=4 {
        for y in 0..=6 {
            walkable.insert((x, y));
        }
    }
    for x in 6..=10 {
        for y in 0..=6 {
            walkable.insert((x, y));
        }
    }
    walkable.insert((5, 6)); // the single detour gap
    walkable.remove(&(5, 2)); // shack
    let opp = (10, 2);
    walkable.remove(&opp);
    let st = State {
        walkable,
        my_shack: (5, 2),
        opp_shack: opp,
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 60,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    };
    let plan = plan_with_meta(&st, &st.my_trolls, Meta::Tempo);
    assert_eq!(plan.door, Some((4, 2)), "sanity: west door chosen: {:?}", plan.door);
    let cells: Vec<(i32, i32)> = plan.ring.iter().map(|(c, _)| *c).collect();
    assert!(
        cells.contains(&(4, 2)),
        "the reachable-side orthogonal ring cell (4,2) must be in the ring: {:?}",
        cells
    );
    assert!(
        !cells.contains(&(6, 2)),
        "the far-side ring cell (6,2) must be excluded via farm_eligible: {:?}",
        cells
    );
    assert!(
        plan.ring.iter().all(|((x, _), _)| *x < 5),
        "no ring cell may straddle to the far side of the wall: {:?}",
        cells
    );
}

// ── Test 7: band-ordering proof — build-ring-pick(78) is strictly between harvest(75) and
//    full-bank(80)/plant(88), and only ever fires while the ring is INCOMPLETE ──────────────
#[test]
fn ring_band_ordering_proof() {
    // Numeric bands (BAND = 100_000; every eta on a reachable ring cell is < 10 << BAND):
    //   plant (carried banana)      88*BAND - eta      in (87*BAND, 88*BAND]
    //   full -> bank                80*BAND            (flat)
    //   build-ring PICK             78*BAND            (flat; at the shack, eta 0)
    //   build-ring park-to-pick     78*BAND - 1
    //   standing harvest (ripe)     75*BAND            (flat)
    //   seed-move / idle-fruit      <= 52*BAND - eta
    // So for EVERY eta: 88(plant) > 80(bank) > 78(pick) > 77(park-pick) > 75(harvest) > 52(...).
    // The raise is GATED on a reachable empty ring cell existing (ring incomplete), so once the
    // ring is full PICK is not even offered and harvest wins -- it can never displace real work
    // on a built ring.

    // (a) 78 > 75: a gatherer STANDING on a ripe banana at (2,2) (band-75 harvest available),
    // shack-adjacent, tent stock present, and 7 empty ring cells left -> build-ring PICK (78)
    // must beat harvesting in place (75). Pre-fix (PICK=50 < 75) it would HARVEST.
    let mut st = base_state();
    st.my_inventory[3] = 2;
    st.trees = vec![ripe_banana(2, 2)]; // on the gatherer's own orthogonal ring cell
    let plan = ring_plan(&st);
    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert_eq!(
        cmds[&0], "PICK 0 BANANA",
        "build-ring PICK (78) must outrank standing harvest (75) while the ring is incomplete: {}",
        cmds[&0]
    );

    // (b) 88 > 78: give the SAME troll a carried banana too (and tent stock, empty ring). The
    // carried-banana PLANT (88) must outrank build-ring PICK (78) -- a carried seed is placed
    // before fetching another.
    let mut st_b = base_state();
    st_b.my_inventory[3] = 2;
    let plan_b = ring_plan(&st_b);
    let mut c = carrier(0, 2, 2); // carrying a banana, on empty ring cell (2,2)
    c.harvest_power = 1;
    let cmds_b = assign(&st_b, &plan_b, &[c]);
    assert!(
        cmds_b[&0].starts_with("PLANT"),
        "carried-banana PLANT (88) must outrank build-ring PICK (78): {}",
        cmds_b[&0]
    );

    // (c) the guard: on a FULL ring (all 8 cells treed), build-ring PICK is not offered (no
    // empty ring cell) -> the gatherer standing on a ripe banana HARVESTS instead. Proves the
    // build-ring priority can never displace harvest once the ring is built.
    let mut st_c = base_state();
    st_c.my_inventory[3] = 2;
    st_c.trees = vec![
        ripe_banana(2, 2), // gatherer's cell (orthogonal)
        banana(3, 1, 2),
        banana(4, 2, 2),
        banana(3, 3, 2),
        banana(2, 1, 2),
        banana(4, 1, 2),
        banana(2, 3, 2),
        banana(4, 3, 2),
    ];
    let mut plan_c = ring_plan(&st_c);
    plan_c.base_trees = 8;
    let cmds_c = assign(&st_c, &plan_c, &[gatherer(0, 2, 2)]);
    assert_eq!(
        cmds_c[&0], "HARVEST 0",
        "on a FULL ring, build-ring must not fire; harvest (75) wins: {}",
        cmds_c[&0]
    );
}
