//! Total-map value ownership diagnostic + pressure governor (v1.53.0-pressurefarm).
//!
//! `analyze`/`classify_tree`/`Ownership` below are the ORIGINAL DEBUG-only diagnostic
//! (unchanged): a rough, auditable ownership split from the live per-turn `State`, printed
//! only when `DEBUG` is enabled, never read by behavior.
//!
//! `assess`/`Pressure`/`PressureState` are the NEW pressure governor (Task 1): they DO feed
//! `tactics::plan_impl` every turn (unconditionally, not gated by DEBUG) so `Plan` can carry
//! a live pressure verdict into `planner.rs`. This is a deliberate, narrow exception to the
//! "diagnostic only" rule above — see docs/superpowers/plans/2026-07-09-pressurefarm-
//! ownership-score.md and docs/pressure-aware-farm.md. `assess` reuses the existing
//! `analyze`/`classify_tree`/`is_created_farm_tree` helpers verbatim (no behavior change to
//! them); it only adds a second, cheap pass over created-farm trees (bounded by farm size,
//! not map size) to classify which ones are exposed.
use super::tactics::Plan;
use super::*;
use std::cell::RefCell;
use std::collections::HashSet;

pub const OWN_MARGIN_TURNS: i32 = 3;
pub const OWN_FUTURE_SEED_VALUE: i32 = 1;
pub const OWN_CREATED_NEAR_TENT_R: i32 = 2;

const INF: i32 = 1_000_000;

thread_local! {
    static INITIAL_TREES: RefCell<HashSet<(Cell, String)>> = RefCell::new(HashSet::new());
    static INITIAL_READY: RefCell<bool> = RefCell::new(false);
    static CFG_PRINTED: RefCell<bool> = RefCell::new(false);
    static PRESS_CFG_PRINTED: RefCell<bool> = RefCell::new(false);
}

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Ownership {
    pub total: i32,
    pub ours: i32,
    pub opp: i32,
    pub uncertain: i32,
    pub dead: i32,
    pub created_exposed: i32,
    pub own_half_exposed: i32,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Bucket {
    Ours,
    Opponent,
    Uncertain,
    Dead,
}

pub fn reset() {
    INITIAL_TREES.with(|s| s.borrow_mut().clear());
    INITIAL_READY.with(|r| *r.borrow_mut() = false);
    CFG_PRINTED.with(|p| *p.borrow_mut() = false);
    PRESS_CFG_PRINTED.with(|p| *p.borrow_mut() = false);
}

pub fn log(state: &State, plan: &Plan) {
    ensure_initial(state);
    if state.turn == 1 {
        CFG_PRINTED.with(|printed| {
            let mut printed = printed.borrow_mut();
            if !*printed {
                eprintln!(
                    "@TFOWNCFG margin={} future_seed={} created_near_tent_r={} farm_r={}",
                    OWN_MARGIN_TURNS, OWN_FUTURE_SEED_VALUE, OWN_CREATED_NEAR_TENT_R, plan.farm_r
                );
                *printed = true;
            }
        });
    }
    if !should_emit(state.turn) {
        return;
    }
    let own = analyze(state, plan);
    eprintln!(
        "@TFOWN t={} total={} ours={} opp={} uncertain={} dead={} created_exposed={} own_half_exposed={}",
        state.turn,
        own.total,
        own.ours,
        own.opp,
        own.uncertain,
        own.dead,
        own.created_exposed,
        own.own_half_exposed
    );
}

pub fn analyze(state: &State, plan: &Plan) -> Ownership {
    ensure_initial(state);

    let opp_d = bfs_distances(&state.walkable, &[state.opp_shack]);
    let mut out = Ownership::default();

    for tree in &state.trees {
        let value = tree_value(tree);
        if value <= 0 {
            continue;
        }

        let bucket = classify_tree(state, tree);
        out.total += value;
        match bucket {
            Bucket::Ours => out.ours += value,
            Bucket::Opponent => out.opp += value,
            Bucket::Uncertain => out.uncertain += value,
            Bucket::Dead => out.dead += value,
        }

        if is_created_farm_tree(tree, plan)
            && matches!(bucket, Bucket::Opponent | Bucket::Uncertain)
        {
            out.created_exposed += value;
        }
        if is_own_half(tree, plan, &opp_d) && !matches!(bucket, Bucket::Ours) {
            out.own_half_exposed += value;
        }
    }

    out
}

// ── Pressure governor (Task 0/1: score contract + live exposure to planning) ───────────

/// Green < Yellow < Orange < Red (declaration order = derived `Ord`): the farm-pressure
/// ladder from docs/pressure-aware-farm.md. Escalation is purely a function of the
/// OBSERVED `Ownership` buckets below — never turn number alone (static turn-only gates
/// are a proven dead end: earlyroam boss 0/8, lateseedhome -1.2).
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum PressureState {
    Green,
    Yellow,
    Orange,
    Red,
}

impl Default for PressureState {
    fn default() -> Self {
        PressureState::Green
    }
}

/// Compact pressure result consumed by `tactics::Plan` / `planner.rs`. `exposed_created_cells`
/// and `released_seed_cells` are POSITION sets (not iterated for ordering — only ever
/// `.contains()`-checked by callers, so HashSet's unspecified iteration order cannot leak
/// into emitted command order; see the determinism note on `assess` below).
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Pressure {
    pub own_half_exposed: i32,
    pub created_exposed: i32,
    pub pressure_score: i32,
    pub state: PressureState,
    /// Created/local farm trees (is_created_farm_tree) classified Opponent or Uncertain —
    /// "not safely ours". Drives Task 2 Step 3's liquidation-priority bonus.
    pub exposed_created_cells: HashSet<Cell>,
    /// Subset of `plan.seed_cells` that pressure has released from protection (Task 2 Step
    /// 2). Deliberately STRICTER than `exposed_created_cells`: only a seed tree that is
    /// ITSELF definitively opponent-bound (bucket == Opponent, not merely Uncertain)
    /// releases, and only once the aggregate state has escalated to Orange/Red — seed
    /// supply is the most dangerous lever in this codebase's history (arena deforestation
    /// stalls when the farm's seed source dies), so releasing it is conservative by design.
    pub released_seed_cells: HashSet<Cell>,
}

fn classify_pressure(
    own_half_exposed: i32,
    created_exposed: i32,
    definite_opponent: bool,
) -> PressureState {
    if created_exposed > 0 {
        if definite_opponent {
            PressureState::Red
        } else {
            PressureState::Orange
        }
    } else if own_half_exposed > 0 {
        PressureState::Yellow
    } else {
        PressureState::Green
    }
}

/// Computed ONCE per turn by `tactics::plan_impl` (never inside planner.rs's per-troll
/// `candidates()` hot loop — Task 1 Step 2). Calls the UNCHANGED `analyze` once, then a
/// second pass bounded by created-farm-tree count (not map size) to classify exposure and
/// find the Red trigger ("opponent ETA makes preserving nearby farm value worse than
/// conversion" == at least one created-exposed tree is DEFINITELY opponent-bound, i.e.
/// `Bucket::Opponent`, not just a close `Bucket::Uncertain` race).
///
/// Determinism: iterates `state.trees` (a `Vec`, stable order already) and inserts into
/// HashSets that are only ever `.contains()`-queried afterward (never iterated for ordered
/// output) — so HashSet's unspecified internal order cannot affect any emitted command.
pub fn assess(state: &State, plan: &Plan) -> Pressure {
    let own = analyze(state, plan);

    let mut exposed_created_cells: HashSet<Cell> = HashSet::new();
    let mut definite_opponent = false;
    for tree in &state.trees {
        if tree_value(tree) <= 0 || !is_created_farm_tree(tree, plan) {
            continue;
        }
        match classify_tree(state, tree) {
            Bucket::Opponent => {
                exposed_created_cells.insert(tree.pos());
                definite_opponent = true;
            }
            Bucket::Uncertain => {
                exposed_created_cells.insert(tree.pos());
            }
            Bucket::Ours | Bucket::Dead => {}
        }
    }

    let pressure_score = own.own_half_exposed + own.created_exposed;
    let state_level =
        classify_pressure(own.own_half_exposed, own.created_exposed, definite_opponent);

    // Task 2 Step 2 (seed-reserve release): conservative on purpose — see the doc comment
    // on `Pressure::released_seed_cells`. Gated on the AGGREGATE state (Orange/Red, the
    // plan's literal wording) as a belt-and-suspenders sanity check, even though in
    // practice a seed tree with bucket==Opponent already forces state_level to Red on its
    // own (a seed tree is always a created-farm tree).
    let released_seed_cells: HashSet<Cell> = if state_level >= PressureState::Orange {
        plan.seed_cells
            .iter()
            .filter(|&&pos| {
                state
                    .trees
                    .iter()
                    .find(|t| t.pos() == pos)
                    .map_or(false, |t| classify_tree(state, t) == Bucket::Opponent)
            })
            .copied()
            .collect()
    } else {
        HashSet::new()
    };

    Pressure {
        own_half_exposed: own.own_half_exposed,
        created_exposed: own.created_exposed,
        pressure_score,
        state: state_level,
        exposed_created_cells,
        released_seed_cells,
    }
}

/// DEBUG telemetry (Task 1 Step 4): @TFPRESSCFG once at turn 1 (constants, near the farm
/// constants per the plan), then @TFPRESS at the same cadence as @TFOWN. Reads Plan's
/// ALREADY-computed `pressure` field — no recomputation, unlike `log` above (which still
/// calls `analyze` fresh; the two numbers agree because nothing mutates state/plan between
/// `tactics::plan` returning and this DEBUG print).
pub fn log_pressure(state: &State, plan: &Plan) {
    if state.turn == 1 {
        PRESS_CFG_PRINTED.with(|printed| {
            let mut printed = printed.borrow_mut();
            if !*printed {
                eprintln!("@TFPRESSCFG farm_floor={}", GE_PRESSURE_FARM_FLOOR);
                *printed = true;
            }
        });
    }
    if !should_emit(state.turn) {
        return;
    }
    eprintln!(
        "@TFPRESS t={} own_half_exposed={} created_exposed={} pressure_score={} state={:?} exposed_n={} released_n={}",
        state.turn,
        plan.pressure.own_half_exposed,
        plan.pressure.created_exposed,
        plan.pressure.pressure_score,
        plan.pressure.state,
        plan.pressure.exposed_created_cells.len(),
        plan.pressure.released_seed_cells.len(),
    );
}

fn ensure_initial(state: &State) {
    INITIAL_READY.with(|ready| {
        if *ready.borrow() {
            return;
        }
        INITIAL_TREES.with(|s| {
            let mut s = s.borrow_mut();
            s.clear();
            for tree in &state.trees {
                s.insert((tree.pos(), tree.tree_type.clone()));
            }
        });
        *ready.borrow_mut() = true;
    });
}

fn should_emit(turn: i32) -> bool {
    turn == 75 || turn == 150 || turn == 225 || turn == TOTAL_TURNS || turn % 5 == 0
}

fn tree_value(tree: &Tree) -> i32 {
    let wood = 4 * tree.size.max(0);
    let fruit = tree.fruits.max(0);
    let future = if tree.fruits > 0 && (tree.tree_type == "BANANA" || tree.tree_type == "APPLE") {
        OWN_FUTURE_SEED_VALUE
    } else {
        0
    };
    wood + fruit + future
}

fn classify_tree(state: &State, tree: &Tree) -> Bucket {
    let my_eta = best_side_eta(state, &state.my_trolls, state.my_shack, tree);
    let opp_eta = best_side_eta(state, &state.opp_trolls, state.opp_shack, tree);
    let turns_rem = TOTAL_TURNS - state.turn + 1;

    if my_eta > turns_rem && opp_eta > turns_rem {
        return Bucket::Dead;
    }
    if my_eta + OWN_MARGIN_TURNS <= opp_eta {
        return Bucket::Ours;
    }
    if opp_eta + OWN_MARGIN_TURNS <= my_eta {
        return Bucket::Opponent;
    }
    Bucket::Uncertain
}

fn best_side_eta(state: &State, workers: &[Troll], shack: Cell, tree: &Tree) -> i32 {
    let bank_cells = bank_cells(state, shack);
    if bank_cells.is_empty() {
        return INF;
    }
    let tree_d = bfs_distances(&state.walkable, &[tree.pos()]);
    let tree_to_bank = min_dist(&tree_d, &bank_cells);
    if tree_to_bank >= INF {
        return INF;
    }

    let mut best = INF;
    for worker in workers {
        let ms = worker.movement_speed.max(1);
        let from_worker = bfs_distances(&state.walkable, &[worker.pos()]);
        let move_dist = from_worker.get(&tree.pos()).copied().unwrap_or(INF);
        if move_dist >= INF {
            continue;
        }
        let prebank = prebank_turns(worker, &from_worker, &bank_cells);
        let move_turns = div_ceil(move_dist, ms);
        let bank_turns = div_ceil(tree_to_bank, ms) + 1;

        if tree.size > 0 && worker.chop_power > 0 {
            let action_turns = div_ceil(tree.health.max(1), worker.chop_power.max(1));
            best = best.min(prebank + move_turns + action_turns + bank_turns);
        }
        if tree.fruits > 0 && worker.harvest_power > 0 {
            best = best.min(prebank + move_turns + 1 + bank_turns);
        }
    }
    best
}

fn prebank_turns(
    worker: &Troll,
    from_worker: &std::collections::HashMap<Cell, i32>,
    bank_cells: &[Cell],
) -> i32 {
    if worker.free_capacity() > 0 {
        return 0;
    }
    let d = min_dist(from_worker, bank_cells);
    if d >= INF {
        INF
    } else if d == 0 || is_any_near(worker.pos(), bank_cells) {
        1
    } else {
        div_ceil(d, worker.movement_speed.max(1)) + 1
    }
}

fn bank_cells(state: &State, shack: Cell) -> Vec<Cell> {
    let mut out: Vec<Cell> = ortho_neighbors(shack)
        .iter()
        .copied()
        .filter(|c| state.walkable.contains(c))
        .collect();
    if state.walkable.contains(&shack) {
        out.push(shack);
    }
    out
}

fn min_dist(d: &std::collections::HashMap<Cell, i32>, cells: &[Cell]) -> i32 {
    cells
        .iter()
        .filter_map(|c| d.get(c).copied())
        .min()
        .unwrap_or(INF)
}

fn is_any_near(cell: Cell, cells: &[Cell]) -> bool {
    cells.iter().any(|&c| manhattan(cell, c) <= 1)
}

fn div_ceil(n: i32, d: i32) -> i32 {
    if n <= 0 {
        0
    } else {
        (n + d - 1) / d.max(1)
    }
}

fn is_created_farm_tree(tree: &Tree, plan: &Plan) -> bool {
    if tree.tree_type != "BANANA" {
        return false;
    }
    let in_farm = plan
        .farm_d
        .get(&tree.pos())
        .map_or(false, |&d| d <= plan.farm_r);
    let near_tent = manhattan(tree.pos(), plan.shack) <= OWN_CREATED_NEAR_TENT_R;
    if !in_farm && !near_tent {
        return false;
    }
    INITIAL_TREES.with(|s| !s.borrow().contains(&(tree.pos(), tree.tree_type.clone())))
}

fn is_own_half(tree: &Tree, plan: &Plan, opp_d: &std::collections::HashMap<Cell, i32>) -> bool {
    let my = plan.farm_d.get(&tree.pos()).copied().unwrap_or(INF);
    let opp = opp_d.get(&tree.pos()).copied().unwrap_or(INF);
    my <= opp
}
