//! v1.59.0-ringfix3 — FIX3 (banana no-carry-in-advance / the backtracking fix) ISOLATED on
//! the AS-BUILT v1.56.0-ringfarm champion, scoped to the ring path (`ring_active`, i.e.
//! `plan.ring` non-empty — the only path any real game takes; see ringfarm.rs).
//!
//! v1.57.0-ringtune bundled this same FIX3 with FIX1 (E1: `plan.want_chopper` suppression)
//! and FIX2 (E2: diagonal-first `plant_cell` ordering), and that bundle reverted ~-2.4 in the
//! arena. This candidate extracts FIX3 ALONE: `suppress_ring_pick` here does NOT reference
//! `plan.want_chopper` at all (test 3 below is the guard proving that), and `plant_cell`
//! keeps ringfarm's existing nearest-first search (NOT FIX2's diagonal-first role_rank). See
//! data/candidates/v1.59.0-ringfix3/brief.md.
//!
//! FIX3 (user game-watch): the anti-pattern was PICK-from-tent then carry (sometimes
//! backtracking past a ripe banana) to a plant cell.
//!   (i)  the build-ring PICK only fires when the chosen plant cell is immediately
//!        actionable (<=2 steps from the troll's CURRENT position) — ring cells are already
//!        <=farm_r(2) of the tent by construction (compute_ring), so this is the missing
//!        "near the troll" half of "near the troll AND near the tent".
//!   (ii) harvesting a ripe fruit at/adjacent to the troll (band 75/52) now outranks the
//!        tent PICK — a harvested banana can be seeded/planted or banked exactly like a tent
//!        pick would, with zero extra travel, so preferring it strictly dominates.
//!
//! Shack at (3,2) in an open 8x5 room (identical geometry to ringfarm.rs), so all 8
//! Chebyshev-1 neighbours are walkable and the ring is the full 8: orthogonals
//! (3,1),(2,2),(4,2),(3,3); diagonals (2,1),(4,1),(2,3),(4,3).
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{compute_ring, Phase, Plan};
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

// ── FIX3(i): banana NO-CARRY-IN-ADVANCE — no PICK unless the plant is immediate ─────────────
#[test]
fn ringfix3_no_pick_when_plant_not_immediate() {
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
fn ringfix3_harvest_ripe_over_tent_pick() {
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

// ── Guard: isolated FIX3 must NOT depend on plan.want_chopper (the E1 term, stripped) ───────
#[test]
fn ringfix3_no_want_chopper_dependency() {
    // want_chopper = TRUE, an IMMEDIATE empty ring cell (the ring is entirely empty, so the
    // gatherer's own cell (2,2) is the nearest — d=0, well within RING_PICK_STEPS), tent
    // banana stock present, and NO ripe banana anywhere (state.trees is empty) so
    // harvest_beats_pick is false too. The v1.57.0-ringtune bundle ALSO suppressed the ring
    // PICK whenever `plan.want_chopper` (that was FIX1/E1, the prime suspect for the -2.4
    // revert). Isolated FIX3 must NOT carry that term — `suppress_ring_pick` here is
    // `ring_active && harvest_beats_pick` only — so with harvest_beats_pick false, the PICK
    // must STILL FIRE despite want_chopper=true. If this assertion fails (PICK suppressed),
    // the want_chopper term was left in by mistake.
    let mut st = base_state();
    st.my_inventory[3] = 3; // tent bananas
    let mut plan = base_plan(&st);
    plan.want_chopper = true;
    let cmds = assign(&st, &plan, &[gatherer(0, 2, 2)]);
    assert_eq!(
        cmds[&0], "PICK 0 BANANA",
        "isolated FIX3 must NOT depend on want_chopper (that was E1, deliberately stripped): {}",
        cmds[&0]
    );
}
