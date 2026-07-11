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
use std::collections::{HashMap, HashSet};

use super::state::{
    bfs_distances, ge_fruit_ty, is_adjacent, mb_afford, ortho_neighbors, plant_cooldown,
    training_cost, water_boost, Cell, State, Tree, Troll, APPLE, BANANA, IRON, LEMON, PLUM, WOOD,
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
// Endgame extension: PICK+PLANT must outrank DROP(8000)/BANK(7000), or the picked fruit is
// instantly re-dropped at the shack and the extension plant never happens (reviewer-confirmed
// livelock, 1- and 2-troll: pair enumeration PLANT_A(8500)+DROP_B(8000) beats DROP_A+BANK_B).
const Y_PLANT: f64 = 8500.0;

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

/// Trees remaining, of any type -- the endgame's "trees almost gone" input (spec gap G3:
/// counts every tree regardless of type or size).
fn fellable_trees(state: &State) -> usize {
    state.trees.len()
}

/// Endgame trigger: `None` during the normal main-loop phase; `Some(ahead)` once either
/// the hard turn cutoff or the "trees nearly gone while behind" condition fires (the
/// postmortem's rule 5), where `ahead` reports whether we currently lead on score (a tie
/// counts as ahead -- `>=`, matching the brief's formula exactly). Pure function of
/// `state`, cheap (no BFS) -- safe to call as often as needed (`troll_candidates` and
/// `decide_yann` each call it independently rather than threading a shared value through,
/// since both derive it from the same `state` and can therefore never disagree).
pub fn endgame_mode(state: &State) -> Option<bool> {
    let trees_low = fellable_trees(state) <= YE_TREES;
    let behind = my_score(state) < opp_score(state);
    if state.turn > YE_TURN || (trees_low && behind) {
        Some(my_score(state) >= opp_score(state))
    } else {
        None
    }
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

/// Simulate `n` turns of a tree's life while a troll travels toward it, returning its
/// `(size, health)` on arrival — or `None` if it dies (health <= 0) before then. Each
/// turn: health -= `opp_chop` first (a tree that dies this turn never gets to grow, and
/// its death is checked immediately, before the cooldown tick); then cooldown -= 1; when
/// cooldown drops to <= 0, the tree grows (size += 1, health += slope) only if
/// `size < 4` (the cap), and the cooldown resets to `base_cd` regardless of whether the
/// cap suppressed growth. Fruit production is deliberately ignored — irrelevant to chop
/// value.
pub fn tree_at_arrival(
    size0: i32,
    health0: i32,
    cooldown0: i32,
    base_cd: i32,
    ty: usize,
    opp_chop: i32,
    n: i32,
) -> Option<(i32, i32)> {
    let slope = match ty {
        APPLE => 3,
        BANANA => 1,
        _ => 2,
    };
    let mut size = size0;
    let mut health = health0;
    let mut cooldown = cooldown0;
    for _ in 0..n {
        health -= opp_chop;
        if health <= 0 {
            return None;
        }
        cooldown -= 1;
        if cooldown <= 0 {
            if size < 4 {
                size += 1;
                health += slope;
            }
            cooldown = base_cd;
        }
    }
    Some((size, health))
}

// ── Task 4: main-loop candidates ────────────────────────────────────────────

/// Precomputed distance context for `troll_candidates`: both shacks' `shack_dist` maps
/// (Task-2 helper). INTERFACE CHOICE (documented per the task brief's either/or): the
/// brief's produced signature has no `Ctx` parameter, but offered adding one; this
/// implementation adds `ctx: &Ctx` to `troll_candidates` because the maps depend only on
/// `state` (not on which troll is being scored) — Task 6's `decide_yann` calls
/// `troll_candidates` once per troll (n<=2) each turn and can build one `Ctx` via
/// `Ctx::build` and share it across both calls instead of recomputing two BFS floods per
/// troll. This task's own tests build a fresh `Ctx` right before each call, which is
/// behaviorally identical to computing it inline — "once per `troll_candidates` call" —
/// just factored out so the sharing is available for free later.
pub struct Ctx {
    pub my_sd: HashMap<Cell, i32>,
    pub opp_sd: HashMap<Cell, i32>,
}

impl Ctx {
    pub fn build(state: &State) -> Self {
        Ctx {
            my_sd: shack_dist(state, state.my_shack),
            opp_sd: shack_dist(state, state.opp_shack),
        }
    }
}

/// Main-loop candidate generator for one troll, in priority order:
/// 1. DROP at our shack (score `Y_DROP`) when carrying anything and adjacent.
/// 2. Bank move (score `Y_BANK`) toward the nearest walkable shack-neighbor: normally
///    gated on being full; during the endgame (`endgame_mode(state).is_some()`), gated on
///    carrying ANYTHING instead (the postmortem's "bank-rush all carry").
/// 2b. Endgame + behind only (`endgame_mode(state) == Some(false)`): PICK the cheapest
///     banked fruit (BANANA, then APPLE, LEMON, PLUM — the postmortem's extend-the-game
///     move) once adjacent to the shack with room to carry it (score 6000, mirrors the
///     champion's PICK command shape — see `planner.rs`); once carrying it, PLANT (same
///     score) on the first free (walkable, unplanted) shack-neighbor cell in
///     `ortho_neighbors` order, MOVE-ing there first if not already standing on it —
///     spends a banked point to keep the game alive for a wood catch-up. Both are simply
///     absent (no candidate pushed) when there's nothing to pick/plant or no free cell.
/// 3. Chop / move-to-tree: dynamic throughput `value = wood / (travel + chop_t + ret)`
///    from the Task-3 arrival simulation, boosted by a proximity-to-opponent-shack
///    denial term on `ttc`-typed trees while the opponent has <= 2 trolls.
/// 4. Fallback park (epsilon score 0.001 — must sit BELOW all real chop throughput values, which are wood-per-turn ~0.05-0.67; always present): head for our shack's neighbor, or the
///    opponent's while `endgame_ahead` (contest their extension plants).
///
/// All MOVE-class targets are picked from a single per-troll BFS (`bfs_distances` from
/// `troll.pos()` alone) computed once at the top, per this module's determinism contract
/// (state.trees walked as a Vec; no HashMap/HashSet iteration — only single-key
/// `.get`/`.contains` lookups). `endgame_mode(state)` is recomputed fresh here (cheap, no
/// BFS) rather than threaded through as a parameter, so the pre-existing `endgame_ahead:
/// bool` parameter keeps its original Task-4 meaning (which shack to park near)
/// undisturbed — `decide_yann` derives both from the SAME `endgame_mode(state)` call, so
/// they can never disagree.
pub fn troll_candidates(
    state: &State,
    troll: &Troll,
    ttc: usize,
    endgame_ahead: bool,
    ctx: &Ctx,
) -> Vec<Cand> {
    let mut out = Vec::new();
    let pos = troll.pos();
    let dist_from_troll = bfs_distances(&state.walkable, &[pos]);
    let mode = endgame_mode(state);
    let in_endgame = mode.is_some();
    let behind = matches!(mode, Some(false));

    // 1. DROP: carrying anything, standing adjacent to our shack.
    if troll.total_carried() > 0 && is_adjacent(pos, state.my_shack) {
        out.push(Cand {
            cmd: format!("DROP {}", troll.id),
            score: Y_DROP,
            target: Some(state.my_shack),
        });
    }

    // 2. Bank move: normally requires being full; the endgame rushes home with ANY carry.
    let bank_ready = if in_endgame {
        troll.total_carried() > 0
    } else {
        troll.free_capacity() == 0
    };
    if bank_ready {
        if let Some(c) = nearest_shack_neighbor(&state.walkable, &dist_from_troll, state.my_shack) {
            out.push(Cand {
                cmd: format!("MOVE {} {} {}", troll.id, c.0, c.1),
                score: Y_BANK,
                target: Some(c),
            });
        }
    }

    // 2b. Endgame + behind: PICK the cheapest banked fruit, then PLANT it once carried.
    if behind {
        if is_adjacent(pos, state.my_shack) && troll.free_capacity() > 0 {
            if let Some(item) = [BANANA, APPLE, LEMON, PLUM]
                .iter()
                .copied()
                .find(|&it| state.my_inventory[it] > 0)
            {
                out.push(Cand {
                    cmd: format!("PICK {} {}", troll.id, fruit_name(item)),
                    score: Y_PLANT,
                    target: Some(state.my_shack),
                });
            }
        }
        if let Some(item) = [BANANA, APPLE, LEMON, PLUM]
            .iter()
            .copied()
            .find(|&it| troll.carry[it] > 0)
        {
            if let Some(cell) = first_free_plant_cell(state, state.my_shack) {
                let cmd = if pos == cell {
                    format!("PLANT {} {}", troll.id, fruit_name(item))
                } else {
                    format!("MOVE {} {} {}", troll.id, cell.0, cell.1)
                };
                out.push(Cand {
                    cmd,
                    score: Y_PLANT,
                    target: Some(cell),
                });
            }
        }
    }

    // 3. Chop / move-to-tree: dynamic throughput value with arrival simulation + denial.
    // chop_power <= 0 -> no chop candidates at all (skip the whole class).
    if troll.chop_power > 0 {
        let ms = troll.movement_speed;
        for t in &state.trees {
            let tpos = t.pos();
            let d = match dist_from_troll.get(&tpos) {
                Some(&d) => d,
                None => continue, // unreachable from the troll
            };
            let ty = match ge_fruit_ty(&t.tree_type) {
                Some(ty) => ty,
                None => continue, // unknown tree type (defensive; never real data)
            };
            let travel = ceil_div(d, ms);
            let opp_chop = state
                .opp_trolls
                .iter()
                .filter(|o| o.pos() == tpos)
                .map(|o| o.chop_power)
                .max()
                .unwrap_or(0);
            let base_cd = effective_cd(state, t);
            let (arrival_size, arrival_health) = match tree_at_arrival(
                t.size, t.health, t.cooldown, base_cd, ty, opp_chop, travel,
            ) {
                Some(v) => v,
                None => continue, // dies before arrival
            };
            let wood = arrival_size.min(troll.free_capacity());
            if wood <= 0 {
                continue;
            }
            let ret_d = match ctx.my_sd.get(&tpos) {
                Some(&r) => r,
                None => continue, // no path back to our shack from this tree
            };
            let chop_t = ceil_div(arrival_health, troll.chop_power);
            let ret = ceil_div(ret_d, ms);
            let denom = (travel + chop_t + ret).max(1);
            let mut value = wood as f64 / denom as f64;
            if ty == ttc && state.opp_trolls.len() <= 2 {
                // Denial: bias typeToCut trees toward the opponent's shack (their
                // training currency). A tree unreachable from the opponent's shack gets
                // an effectively-infinite distance, so the multiplier decays to ~1.0
                // (no boost) instead of panicking on a missing map entry.
                let opp_d = ctx.opp_sd.get(&tpos).copied().unwrap_or(i32::MAX / 2);
                value *= 1.0 + YD_W / (1.0 + opp_d as f64);
            }
            let cmd = if d == 0 {
                format!("CHOP {}", troll.id)
            } else {
                format!("MOVE {} {} {}", troll.id, tpos.0, tpos.1)
            };
            out.push(Cand {
                cmd,
                score: value,
                target: Some(tpos),
            });
        }
    }

    // 4. Fallback park: always present, last resort. Our shack while behind/neutral, the
    // opponent's while ahead in an endgame (contest extension plants).
    let park_shack = if endgame_ahead {
        state.opp_shack
    } else {
        state.my_shack
    };
    let park_target =
        nearest_shack_neighbor(&state.walkable, &dist_from_troll, park_shack).unwrap_or(pos); // no reachable shack-neighbor: degenerate MOVE-in-place
    out.push(Cand {
        cmd: format!("MOVE {} {} {}", troll.id, park_target.0, park_target.1),
        // Epsilon, NOT 1.0: chop throughput values are wood-per-turn (~0.05-0.67), so a
        // 1.0 park outranked ALL real chopping — the bot trained at ~t38 and then idled
        // 260 turns with zero CHOPs (found via command-stream capture vs WAIT, seed 3).
        score: 0.001,
        target: Some(park_target),
    });

    out
}

/// Walkable ortho-neighbor of `shack` with the smallest `dist_from_troll` (a per-troll
/// BFS map keyed by cell); non-walkable or unreachable neighbors are skipped. Ties favor
/// the lexicographically smaller cell (`(x, y)` tuple order, i.e. smaller `x` first, then
/// smaller `y`) — deterministic and independent of `ortho_neighbors`' fixed emission
/// order.
fn nearest_shack_neighbor(
    walkable: &HashSet<Cell>,
    dist_from_troll: &HashMap<Cell, i32>,
    shack: Cell,
) -> Option<Cell> {
    let mut best: Option<(i32, Cell)> = None;
    for n in ortho_neighbors(shack) {
        if !walkable.contains(&n) {
            continue;
        }
        let d = match dist_from_troll.get(&n) {
            Some(&d) => d,
            None => continue,
        };
        best = Some(match best {
            None => (d, n),
            Some((bd, bc)) => {
                if d < bd || (d == bd && n < bc) {
                    (d, n)
                } else {
                    (bd, bc)
                }
            }
        });
    }
    best.map(|(_, c)| c)
}

/// Item index -> the protocol's type-name string, for the 4 fruit types only (PICK/PLANT
/// never operate on IRON or WOOD). Panics on any other index — never real data, since
/// every caller in this module scans exactly `[BANANA, APPLE, LEMON, PLUM]`.
fn fruit_name(item: usize) -> &'static str {
    match item {
        PLUM => "PLUM",
        LEMON => "LEMON",
        APPLE => "APPLE",
        BANANA => "BANANA",
        _ => panic!("fruit_name: not a fruit index {}", item),
    }
}

/// First walkable orthogonal neighbor of `shack`, in fixed `ortho_neighbors` array order,
/// that hosts no existing tree ("no plant" — mirrors `engine::apply_plant`'s own
/// `plant_at_pos(...).is_some()` check, generalized here to "any tree at that cell" since
/// `state.trees` is our only planted-object list). `state.trees` is a `Vec`, scanned
/// directly (this module's determinism contract), and `ortho_neighbors` already returns a
/// fixed 4-element array — the whole scan is deterministic top-to-bottom.
fn first_free_plant_cell(state: &State, shack: Cell) -> Option<Cell> {
    ortho_neighbors(shack)
        .into_iter()
        .find(|c| state.walkable.contains(c) && !state.trees.iter().any(|t| t.pos() == *c))
}

// ── Task 5: funding phase — target spec + gather + TRAIN ───────────────────────

/// Nearest tree of `item`'s fruit type with `fruits > 0`, by distance-to-my-shack (`sd`, the
/// caller's precomputed `shack_dist` map). `state.trees` is a `Vec` so the scan itself is in
/// stable order; `min_by_key` is additionally a full, order-invariant reduction (the winner
/// depends only on the `(distance, cell)` key, never on scan order — the same reasoning
/// `shack_dist` already relies on for its `dist.values_mut()` pass, and the pattern the
/// champion's `planner.rs` uses for `iron_cells.iter().min_by_key(...)`). Ties favor the
/// lexicographically smaller cell (`Cell`'s default tuple `Ord`), matching
/// `nearest_shack_neighbor`'s convention.
fn nearest_fruited_tree(
    state: &State,
    sd: &HashMap<Cell, i32>,
    item: usize,
) -> Option<(Cell, i32)> {
    state
        .trees
        .iter()
        .filter(|t| t.fruits > 0 && ge_fruit_ty(&t.tree_type) == Some(item))
        .filter_map(|t| sd.get(&t.pos()).map(|&d| (t.pos(), d)))
        .min_by_key(|&(c, d)| (d, c))
}

/// Nearest walkable cell orthogonally adjacent to any `iron_cells` member, by distance-to-
/// my-shack. Same order-invariance argument as `nearest_fruited_tree` applies to the
/// `state.iron_cells.iter()` scan below (a full `min_by_key` reduction, never an order-
/// dependent early pick) — this deliberately mirrors the champion's own `planner.rs` pattern
/// (`iron_cells.iter().flat_map(|ic| ortho_neighbors(*ic)).min_by_key(...)`) rather than a
/// bespoke BFS-with-early-exit.
fn nearest_iron_access(state: &State, sd: &HashMap<Cell, i32>) -> Option<(Cell, i32)> {
    state
        .iron_cells
        .iter()
        .flat_map(|&ic| ortho_neighbors(ic))
        .filter(|c| state.walkable.contains(c))
        .filter_map(|c| sd.get(&c).map(|&d| (c, d)))
        .min_by_key(|&(c, d)| (d, c))
}

/// Estimated turns to gather `need` more of `item` (PLUM/LEMON/IRON only), assuming the
/// funding troll makes repeated round trips from the shack: nearest source (a fruit tree
/// with `fruits > 0`, or a walkable cell orthogonally adjacent to iron) via `shack_dist`;
/// per-trip yield from the "starter" troll's stats (`state.my_trolls[0]` — funding always
/// runs with exactly one troll, per the design: Task 6 only calls this class of function
/// while `my_trolls.len() < 2`); `round_trip = dist_to_source + dist_source_to_shack + 2`,
/// which — since both legs start/end at the shack — is `2 * dist + 2` (there, back, +2 for
/// the harvest/mine action and the drop). No source, no starter troll, or a non-positive
/// per-trip yield all fall back to the `i32::MAX / 2` sentinel: "unreachable within any
/// reasonable horizon" (this also sidesteps `i32` overflow that doubling a saturated
/// distance would otherwise risk).
pub fn est_gather_turns(state: &State, item: usize, need: i32) -> i32 {
    if need <= 0 {
        return 0;
    }
    let starter = match state.my_trolls.first() {
        Some(t) => t,
        None => return i32::MAX / 2,
    };
    let sd = shack_dist(state, state.my_shack);
    let (dist, per_trip) = if item == IRON {
        let per_trip = starter.chop_power.max(1).min(starter.carry_capacity);
        (nearest_iron_access(state, &sd).map(|(_, d)| d), per_trip)
    } else {
        let per_trip = starter.harvest_power.min(starter.carry_capacity);
        (
            nearest_fruited_tree(state, &sd, item).map(|(_, d)| d),
            per_trip,
        )
    };
    let dist = match dist {
        Some(d) => d,
        None => return i32::MAX / 2,
    };
    if per_trip <= 0 {
        return i32::MAX / 2;
    }
    let round_trip = dist * 2 + 2;
    ceil_div(need, per_trip) * round_trip
}

/// Per-resource funding target spec (PLUM→ms, LEMON→cc, IRON→chop): stat 3 if the shortfall
/// to 10 is gatherable within `YF_T` turns, else stat 2; hp fixed at 1 (2 apples — covered
/// by starting inventory, per the postmortem).
pub fn choose_target_spec(state: &State) -> (i32, i32, i32, i32) {
    let stat = |item: usize| {
        let need = (10 - state.my_inventory[item]).max(0);
        if est_gather_turns(state, item, need) <= YF_T {
            3
        } else {
            2
        }
    };
    (stat(PLUM), stat(LEMON), 1, stat(IRON))
}

/// Funding-phase candidate generator for the single pre-training troll, in priority order:
/// 1. TRAIN: fires when `spec`'s exact cost is affordable — `training_cost(n, spec)` with
///    `n = state.my_trolls.len()` (the CURRENT troll count). This matches
///    `engine::apply_train`'s own `n` exactly (verified by reading it) — NOT a literal
///    `training_cost(2, spec)` as the brief's interface text guessed; see the task report.
///    `engine::apply_train`'s only positional precondition is that no unit (mine or the
///    opponent's) stands on OUR shack cell (the new recruit's spawn point) — not an
///    adjacency requirement on the acting troll, as the brief hypothesized. When affordable
///    but blocked this way, fall back to moving this troll off the shack (score
///    `Y_TRAIN - 1.0`) so the recruit can spawn next turn.
/// 2. Deficit gathering (PLUM/LEMON/IRON only — "just enough resources": a non-needed type
///    is never gathered): one candidate per still-deficient item, score `5000 -
///    est_remaining_turns`. HARVEST when already standing on a fruited tree of that type;
///    MINE when already orthogonally adjacent to iron; else MOVE toward the nearest needed
///    source (the same shack-distance-nearest source `est_gather_turns` costed).
/// 3. DROP (score `Y_DROP`) when adjacent to our shack and carrying any still-deficient item.
pub fn funding_candidates(state: &State, troll: &Troll, spec: (i32, i32, i32, i32)) -> Vec<Cand> {
    let mut out = Vec::new();
    let pos = troll.pos();
    let n = state.my_trolls.len() as i32;
    let cost = training_cost(n, spec);
    let have_iron = !state.iron_cells.is_empty();

    // 1. TRAIN, or a move-off-shack fallback when a unit blocks the recruit's spawn cell.
    if mb_afford(&state.my_inventory, &cost, have_iron) {
        let shack_blocked = state.my_trolls.iter().any(|t| t.pos() == state.my_shack)
            || state.opp_trolls.iter().any(|t| t.pos() == state.my_shack);
        if !shack_blocked {
            out.push(Cand {
                cmd: format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3),
                score: Y_TRAIN,
                target: None,
            });
        } else {
            let dist_from_troll = bfs_distances(&state.walkable, &[pos]);
            if let Some(c) =
                nearest_shack_neighbor(&state.walkable, &dist_from_troll, state.my_shack)
            {
                out.push(Cand {
                    cmd: format!("MOVE {} {} {}", troll.id, c.0, c.1),
                    score: Y_TRAIN - 1.0,
                    target: Some(c),
                });
            }
        }
    }

    // 2. Deficit gathering: PLUM, LEMON, IRON only.
    let sd = shack_dist(state, state.my_shack);
    for &item in &[PLUM, LEMON, IRON] {
        let deficit = cost[item] - state.my_inventory[item];
        if deficit <= 0 {
            continue; // never gather a satisfied (or non-target) resource
        }
        let score = 5000.0 - est_gather_turns(state, item, deficit) as f64;
        if item == IRON {
            let adjacent_iron = troll.chop_power > 0
                && ortho_neighbors(pos)
                    .iter()
                    .any(|c| state.iron_cells.contains(c));
            if adjacent_iron {
                out.push(Cand {
                    cmd: format!("MINE {}", troll.id),
                    score,
                    target: Some(pos),
                });
                continue;
            }
        } else if troll.harvest_power > 0
            && state
                .trees
                .iter()
                .any(|t| t.pos() == pos && t.fruits > 0 && ge_fruit_ty(&t.tree_type) == Some(item))
        {
            out.push(Cand {
                cmd: format!("HARVEST {}", troll.id),
                score,
                target: Some(pos),
            });
            continue;
        }
        let target = if item == IRON {
            nearest_iron_access(state, &sd).map(|(c, _)| c)
        } else {
            nearest_fruited_tree(state, &sd, item).map(|(c, _)| c)
        };
        if let Some(c) = target {
            out.push(Cand {
                cmd: format!("MOVE {} {} {}", troll.id, c.0, c.1),
                score,
                target: Some(c),
            });
        }
    }

    // 3. DROP: adjacent to shack, carrying any still-deficient item.
    if is_adjacent(pos, state.my_shack) {
        let carrying_needed = [PLUM, LEMON, IRON]
            .iter()
            .any(|&item| troll.carry[item] > 0 && cost[item] > state.my_inventory[item]);
        if carrying_needed {
            out.push(Cand {
                cmd: format!("DROP {}", troll.id),
                score: Y_DROP,
                target: Some(state.my_shack),
            });
        }
    }

    out
}

// ── Task 6: pair coordination + decide_yann assembly ────────────────────────────

/// Canonical single-list argmax (this module's tie-break convention, restated at the top
/// of the file): higher score wins; on an exact tie, the lexicographically smaller command
/// string wins. Every candidate list this module ever hands to this function is non-empty
/// (`troll_candidates` always includes the fallback park); panics otherwise, since that
/// would mean a troll has literally nothing to do — a bug elsewhere, not a real state.
fn argmax_cand(cands: &[Cand]) -> &Cand {
    let mut best: Option<&Cand> = None;
    for c in cands {
        best = Some(match best {
            None => c,
            Some(b) => {
                if c.score > b.score || (c.score == b.score && c.cmd < b.cmd) {
                    c
                } else {
                    b
                }
            }
        });
    }
    best.expect("candidate list must be non-empty")
}

/// Exact pair coordination for two trolls (the postmortem's rule 4): enumerate every `(a,
/// b)` with `a` from `a_list`, `b` from `b_list`, skip any pair that targets the same
/// non-`None` cell (`None` never collides, including with itself — "both-None allowed"),
/// maximize the summed score; ties broken by the concatenated command strings
/// (lexicographically smaller wins, this module's convention). Falls back to each list's
/// own independent `argmax_cand` (ignoring the dedup constraint) in the degenerate case
/// where every combination collides — this can only happen when both trolls' entire
/// candidate lists share a single common target (e.g., two identically-positioned trolls
/// with nothing but the fallback park, both parking on the same shack-neighbor cell);
/// never panics.
fn pair_argmax(a_list: &[Cand], b_list: &[Cand]) -> (String, String) {
    let mut best: Option<(f64, String, String, String)> = None; // (sum, tie-break key, a.cmd, b.cmd)
    for a in a_list {
        for b in b_list {
            if a.target.is_some() && a.target == b.target {
                continue;
            }
            let sum = a.score + b.score;
            let key = format!("{}{}", a.cmd, b.cmd);
            let better = match &best {
                None => true,
                Some((bs, bk, _, _)) => sum > *bs || (sum == *bs && key < *bk),
            };
            if better {
                best = Some((sum, key, a.cmd.clone(), b.cmd.clone()));
            }
        }
    }
    match best {
        Some((_, _, ac, bc)) => (ac, bc),
        None => (
            argmax_cand(a_list).cmd.clone(),
            argmax_cand(b_list).cmd.clone(),
        ),
    }
}

/// Assembly. 1) Pin memory once: `type_to_cut` and `target_spec` are computed and stored
/// TOGETHER the first time `type_to_cut` is `None`, then only ever read — never
/// recomputed (a Task-5-review fix: a mid-trip recompute of one without the other could
/// strand a carried item under a drifted spec). 2) Build the shared `Ctx` and the
/// endgame's `ahead` flag once. 3) Generate each troll's candidate list: `funding_candidates`
/// UNIONED with `troll_candidates` while `my_trolls.len() < 2` (so the bank-move/DROP
/// paths always exist even before the second troll is trained — another Task-5-review
/// fix), `troll_candidates` alone once there are 2. 4) Pick: one troll -> straight
/// argmax; two -> exact pair coordination (`pair_argmax`); anything else (0, or more than
/// 2 — never produced by this design's own play, defensive only) -> independent per-troll
/// argmax, never panicking. `my_trolls` is sorted by id first for a deterministic,
/// input-order-independent pairing (mirrors `decide_elite`'s own `my.sort_by_key(|t|
/// t.id)`).
pub fn decide_yann(state: &State) -> Vec<String> {
    let (ttc, spec) = MEM.with(|m| {
        let mut mem = m.borrow_mut();
        if mem.type_to_cut.is_none() {
            mem.type_to_cut = Some(choose_type_to_cut(state));
            mem.target_spec = Some(choose_target_spec(state));
        }
        (mem.type_to_cut.unwrap(), mem.target_spec.unwrap())
    });

    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);
    if my.is_empty() {
        return Vec::new();
    }

    let ctx = Ctx::build(state);
    let endgame_ahead = matches!(endgame_mode(state), Some(true));
    let funding = my.len() < 2;

    let lists: Vec<Vec<Cand>> = my
        .iter()
        .map(|t| {
            let mut cands = troll_candidates(state, t, ttc, endgame_ahead, &ctx);
            if funding {
                cands.extend(funding_candidates(state, t, spec));
            }
            cands
        })
        .collect();

    match lists.len() {
        1 => vec![argmax_cand(&lists[0]).cmd.clone()],
        2 => {
            let (a, b) = pair_argmax(&lists[0], &lists[1]);
            vec![a, b]
        }
        _ => lists.iter().map(|l| argmax_cand(l).cmd.clone()).collect(),
    }
}
