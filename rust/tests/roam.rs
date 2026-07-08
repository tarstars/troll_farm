//! Roam retest (v1.40.0-roam4, analyst b62c977 queue #2): GE_CHOP_R 5 -> 4. This drives the
//! REAL committed constant via `tactics::plan_with_meta(..., Meta::Tempo)` — the test-only seam
//! that calls `plan_impl` directly (GE_META is fixed at `Meta::Tempo` live, so this is exactly
//! what `tactics::plan()` computes) — rather than a hand-built `Plan` with a hardcoded `chop_r`
//! field, so this test is a genuine regression check tied to the constant, not just a check of
//! `planner::assign`'s generic roam-gating logic.
//!
//! `within_roam` gates the PRIMARY fell bands (70/72) on `farm_d(tree) <= chop_r`; `own_half`
//! gates them independently on raw manhattan distance (shack vs opp). The anti-starvation
//! fallback (band 30) has NEITHER gate (`p.size >= 1` only) — so a tree that drops out of band
//! 70 because of a tighter roam does not vanish, it falls to band 30, where it competes purely
//! on ETA with any other reachable fellable tree, including ones in the ENEMY half (own_half
//! only ever gates band 70/72, never the anti-starvation fallback).
//!
//! This test exploits exactly that seam: an our-half tree at roam-boundary distance 5
//! (own_half=true always; within_roam only when chop_r>=5) vs an enemy-half tree at distance 4
//! (own_half=false ALWAYS, independent of chop_r, so it is perpetually band-30-only). Under the
//! champion's roam=5 the our-half tree is band 70 and wins outright (BAND=100_000 dwarfs any ETA
//! difference); under roam=4 it drops to band 30 and loses the ETA race to the nearer enemy-half
//! tree. Verified must-FAIL-under-roam-5 by running this test before editing the constant (see
//! builder report for the transcript).
//!
//! [helpers copied VERBATIM from tests/planner_tasks.rs, per repo convention]
use std::collections::HashSet;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{plan_with_meta, Meta};
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

fn chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll { id, x, y, movement_speed: 2, carry_capacity: 2, harvest_power: 0, chop_power: 2, carry: [0; 6] }
}
fn banana(x: i32, y: i32, size: i32) -> Tree {
    Tree { tree_type: "BANANA".into(), x, y, size, health: 2 + size, fruits: 0, cooldown: 0 }
}

#[test]
#[ignore] // roam4 arena-reverted -3.6; tree restored to GE_CHOP_R=5
fn tight_roam_drops_boundary_tree_to_enemy_half_rival() {
    // Own-half fellable banana at (3,4): manhattan to shack (0,2) = 5, to opp (7,2) = 6 ->
    // own_half=true. farm_d (BFS from the shack; open 8x5 grid == manhattan here) = 5, so it is
    // within_roam only while chop_r >= 5.
    //
    // Enemy-half fellable banana at (4,2): manhattan to shack = 4, to opp = 3 -> own_half=FALSE
    // unconditionally (independent of chop_r) -> never eligible for band 70/72, only ever the
    // anti-starvation band 30.
    //
    // Chopper at (1,2) (shack-adjacent), movement_speed slowed 2->1 (struct-update over the
    // chopper() helper, same convention as tests/race_check.rs's share_pen test) so the two
    // map-distances (4 and 3) map directly to etas 4 and 3 without an integer-division tie (at
    // the helper's native ms=2 both etas round up to 2 and the test cannot distinguish them).
    // Both trees are size-2 bananas (identical health -> identical chop_t=2), so:
    //   - roam>=5: (3,4) gets a band-70 MoveTo (~6,999,994) that dwarfs any band-30 value
    //     (BAND=100_000) -> (3,4) wins outright regardless of the enemy-half tree.
    //   - roam=4: (3,4) drops to band-30 only (value 30*BAND-(4+2)=2,999,994); (4,2) is also
    //     band-30-only (value 30*BAND-(3+2)=2,999,995) -> (4,2) wins by 1 (ETA, not a
    //     lexicographic tie-break).
    let mut st = base_state();
    st.trees = vec![banana(3, 4, 2), banana(4, 2, 2)];
    let my = vec![Troll { movement_speed: 1, ..chopper(2, 1, 2) }];
    let plan = plan_with_meta(&st, &my, Meta::Tempo); // real GE_CHOP_R (and GE_FARM_R etc.)
    let cmds = assign(&st, &plan, &my);
    assert!(
        cmds[&2].contains("4 2"),
        "tightened roam (GE_CHOP_R=4) must send the chopper to the enemy-half tree at (4,2) \
         once the own-half tree at (3,4) falls outside roam: got {}",
        &cmds[&2]
    );
    assert!(
        !cmds[&2].contains("3 4"),
        "must not still target the own-half tree once it is outside the tightened roam: {}",
        &cmds[&2]
    );
}
