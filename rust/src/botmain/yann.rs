//! yannbot decider — reproduction of Yann Moisan's #3-Legend Troll Farm bot (2 trolls,
//! chop throughput + arrival simulation + training denial + game-end control).
//! Spec: `docs/superpowers/specs/2026-07-11-yannbot-design.md`. Postmortem (the design's
//! source, archived verbatim): `docs/reference/yann-moisan-postmortem-2026-05-26.txt`.
//!
//! ISOLATION: this module reads ONLY `super::state` (types/helpers shared by every
//! decider) — never `motion`, `ownership`, `planner`, or `tactics`. It is dead code until
//! a later task wires a dispatch; the champion decision path stays untouched.
//!
//! DETERMINISM: no `HashMap`/`HashSet` *iteration* in scoring paths (single-key lookups
//! are fine — e.g. `shack_dist(..).get(&cell)`); `state.trees` is a `Vec`, so scoring
//! walks iterate it directly for a stable, replay-safe order.
//!
//! TIE-BREAK CONVENTION (binding for every argmax/tie-break added to this module, even
//! before it is exercised): higher score wins; on an exact score tie, prefer the
//! lexicographically smaller command string.
use std::cell::RefCell;
use std::collections::HashMap;

use super::state::{
    bfs_distances, ortho_neighbors, plant_cooldown, water_boost, Cell, State, Tree, APPLE,
    BANANA, LEMON, PLUM, WOOD,
};

// ── tunables (G1-G5 sweep candidates from the spec's "reproduction gaps"; starting
// values, unmeasured — later tasks sweep these via playmatch/boss gate) ───────────────
const YD_W: f64 = 4.0; // G1 denial weight (sweep candidate)
const YF_T: i32 = 40; // G2 max turns to justify a 10-threshold stat
const YE_TREES: usize = 2; // G3 "trees almost gone"
const YE_TURN: i32 = 250; // endgame turn trigger (postmortem)
const Y_DROP: f64 = 8000.0; // postmortem priority stack
const Y_BANK: f64 = 7000.0;
const Y_TRAIN: f64 = 9000.0;

// ── memory: turn-1 typeToCut cache + funding target-spec cache, each memoized once
// they're first decided so later turns don't re-derive them ────────────────────────────
#[derive(Default)]
struct YMem {
    type_to_cut: Option<usize>,
    target_spec: Option<(i32, i32, i32, i32)>,
}

thread_local! {
    static MEM: RefCell<YMem> = RefCell::new(YMem::default());
}

/// Reset all decider memory (call once per fresh game/process, mirroring the champion's
/// `planner::reset`/`tactics::reset` pattern; tests call this between independent games
/// sharing a thread).
pub fn reset_mem() {
    MEM.with(|m| *m.borrow_mut() = YMem::default());
}

/// One scored candidate command for a single troll (later tasks populate/consume this).
pub struct Cand {
    pub cmd: String,
    pub score: f64,
    pub target: Option<Cell>,
}

/// Ceiling division for `travelTurns`/`chopTurns` from positive speeds/powers (the
/// postmortem's `math.ceil` for fractional turns). `b` must be positive.
pub fn ceil_div(a: i32, b: i32) -> i32 {
    debug_assert!(b > 0, "ceil_div: non-positive divisor {}", b);
    (a + b - 1) / b
}

/// Banked score: fruit sum (PLUM+LEMON+APPLE+BANANA) + 4x wood — mirrors the referee's
/// `Player.recomputeScore` (verified 2026-07-11: no planted-tree scoring).
pub fn my_score(state: &State) -> i32 {
    score_of(&state.my_inventory)
}

pub fn opp_score(state: &State) -> i32 {
    score_of(&state.opp_inventory)
}

fn score_of(inv: &[i32; 6]) -> i32 {
    inv[PLUM] + inv[LEMON] + inv[APPLE] + inv[BANANA] + 4 * inv[WOOD]
}

/// BFS distance from every walkable cell to `shack`: seed the *walkable* orthogonal
/// neighbors of `shack` at 0, run `bfs_distances`, then shift every resulting distance by
/// +1 — since the seeds are one step short of the shack itself, this turns "distance to
/// nearest shack-adjacent cell" into "distance to the shack", matching travel semantics.
/// Also seed the shack cell itself at 0 (a troll standing exactly on the shack, e.g. at
/// spawn, is at distance 0 even though the shack cell isn't walkable).
pub fn shack_dist(state: &State, shack: Cell) -> HashMap<Cell, i32> {
    let sources: Vec<Cell> = ortho_neighbors(shack)
        .into_iter()
        .filter(|c| state.walkable.contains(c))
        .collect();
    let mut dist = bfs_distances(&state.walkable, &sources);
    for v in dist.values_mut() {
        *v += 1;
    }
    dist.insert(shack, 0);
    dist
}

/// Turn-1 focus type: LEMON or PLUM item index, whichever type's trees sum to the
/// smaller total `shack_dist` from our shack (missing/unreachable trees — not present in
/// the BFS map — are skipped; a type with zero reachable trees sums to `i64::MAX`; an
/// exact tie favors LEMON via `<=`).
pub fn choose_type_to_cut(state: &State) -> usize {
    let dist = shack_dist(state, state.my_shack);
    let mut lemon_sum: i64 = 0;
    let mut lemon_seen = false;
    let mut plum_sum: i64 = 0;
    let mut plum_seen = false;
    for t in &state.trees {
        let d = match dist.get(&t.pos()) {
            Some(&d) => d as i64,
            None => continue, // unreachable tree: skip
        };
        match t.tree_type.as_str() {
            "LEMON" => {
                lemon_sum += d;
                lemon_seen = true;
            }
            "PLUM" => {
                plum_sum += d;
                plum_seen = true;
            }
            _ => {}
        }
    }
    let lemon_total = if lemon_seen { lemon_sum } else { i64::MAX };
    let plum_total = if plum_seen { plum_sum } else { i64::MAX };
    if lemon_total <= plum_total {
        LEMON
    } else {
        PLUM
    }
}

/// `plant_cooldown(ty)` minus `water_boost(ty)` when `t` is orthogonally adjacent to any
/// water cell, else the unmodified base cooldown.
pub fn effective_cd(state: &State, t: &Tree) -> i32 {
    let base = plant_cooldown(&t.tree_type);
    let watered = ortho_neighbors(t.pos())
        .iter()
        .any(|c| state.water_cells.contains(c));
    if watered {
        base - water_boost(&t.tree_type)
    } else {
        base
    }
}
