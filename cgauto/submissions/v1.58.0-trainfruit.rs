#![allow(dead_code, unused)]
// CodinGame Spring Challenge 2026 - Troll Farm bot (Rust port of Python v0.7.1)
// Single-file submission. stdlib only.

use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};
use std::io::{self, BufRead, Write};

// ── constants ───────────────────────────────────────────────────────────────

const VERSION: &str = "1.58.0-trainfruit"; // base = v1.56.0-ringfarm (v1.57.0-ringtune's E1/E2/FIX3 tuning was arena-reverted ~-2.4, 2026-07-10). Adds a clustered training-fruit corner (lemon/plum/apple) to the tent ring: compute_ring carves an adaptive compact quadrant (2 orthogonals + 1 diagonal, farthest-from-opponent among fully-eligible corners, graceful degradation) out of the 8-cell ring; the corner is planted as FUNDING-class work (bands 56/54, below real funding fetches but above generic foraging) with an investment guard (never spends a seed the pending hand needs this turn). The other 5 ring cells stay the v1.56 banana scheme.
                                            // (the sequential cascade jobs.rs was REMOVED for submission size — 100 KB cap; it lives in
                                            // git history and in the frozen v1.26.0 artifacts for instant fallback)
mod state {
//! State layer (R3a): game-state types, item indices, and pure helpers shared by
//! every decider. Extracted VERBATIM from botmain.rs (only visibility added);
//! behavior equality is enforced by the black-box harness (src/bin/equality.rs).
use std::collections::{HashMap, HashSet, VecDeque};

pub const TOTAL_TURNS: i32 = 300;

// Item indices: PLUM=0, LEMON=1, APPLE=2, BANANA=3, IRON=4, WOOD=5
pub const PLUM: usize = 0;
pub const LEMON: usize = 1;
pub const APPLE: usize = 2;
pub const BANANA: usize = 3;
pub const IRON: usize = 4;
pub const WOOD: usize = 5;

// Base growth cooldown per tree type
pub fn plant_cooldown(t: &str) -> i32 {
    match t {
        "PLUM" => 8,
        "LEMON" => 8,
        "APPLE" => 9,
        "BANANA" => 6,
        _ => panic!("unknown plant: {}", t),
    }
}

pub fn water_boost(t: &str) -> i32 {
    match t {
        "PLUM" => 5,
        "LEMON" => 5,
        "APPLE" => 7,
        "BANANA" => 2,
        _ => panic!("unknown plant for water_boost: {}", t),
    }
}

// ── data structures ─────────────────────────────────────────────────────────

pub type Cell = (i32, i32);

#[derive(Clone)]
pub struct Troll {
    pub id: i32,
    pub x: i32,
    pub y: i32,
    pub movement_speed: i32,
    pub carry_capacity: i32,
    pub harvest_power: i32,
    pub chop_power: i32,
    pub carry: [i32; 6],
}

impl Troll {
    pub fn pos(&self) -> Cell {
        (self.x, self.y)
    }
    pub fn total_carried(&self) -> i32 {
        self.carry.iter().sum()
    }
    pub fn free_capacity(&self) -> i32 {
        self.carry_capacity - self.total_carried()
    }
    pub fn stats(&self) -> (i32, i32, i32, i32) {
        (
            self.movement_speed,
            self.carry_capacity,
            self.harvest_power,
            self.chop_power,
        )
    }
}

#[derive(Clone)]
pub struct Tree {
    pub tree_type: String, // "PLUM","LEMON","APPLE","BANANA"
    pub x: i32,
    pub y: i32,
    pub size: i32,
    pub health: i32,
    pub fruits: i32,
    pub cooldown: i32,
}

impl Tree {
    pub fn pos(&self) -> Cell {
        (self.x, self.y)
    }
}

pub struct State {
    pub walkable: HashSet<Cell>,
    pub my_shack: Cell,
    pub opp_shack: Cell,
    pub my_inventory: [i32; 6],
    pub opp_inventory: [i32; 6],
    pub trees: Vec<Tree>,
    pub my_trolls: Vec<Troll>,
    pub opp_trolls: Vec<Troll>,
    pub turn: i32,
    pub iron_cells: HashSet<Cell>,
    pub water_cells: HashSet<Cell>,
}

// ── geometry helpers ─────────────────────────────────────────────────────────

pub const NEIGHBORS: [(i32, i32); 4] = [(0, 1), (1, 0), (0, -1), (-1, 0)];

pub fn ortho_neighbors(cell: Cell) -> [Cell; 4] {
    let (x, y) = cell;
    [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
}

pub fn is_adjacent(a: Cell, b: Cell) -> bool {
    (a.0 - b.0).abs() + (a.1 - b.1).abs() == 1
}

// ── BFS ─────────────────────────────────────────────────────────────────────

pub fn bfs_distances(walkable: &HashSet<Cell>, sources: &[Cell]) -> HashMap<Cell, i32> {
    let mut dist: HashMap<Cell, i32> = HashMap::new();
    let mut queue: VecDeque<Cell> = VecDeque::new();
    for &cell in sources {
        if !dist.contains_key(&cell) {
            dist.insert(cell, 0);
            queue.push_back(cell);
        }
    }
    while let Some((x, y)) = queue.pop_front() {
        let d = dist[&(x, y)];
        for &(dx, dy) in &NEIGHBORS {
            let n = (x + dx, y + dy);
            if walkable.contains(&n) && !dist.contains_key(&n) {
                dist.insert(n, d + 1);
                queue.push_back(n);
            }
        }
    }
    dist
}

pub fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

// ── training cost ────────────────────────────────────────────────────────────

pub fn training_cost(n: i32, talents: (i32, i32, i32, i32)) -> [i32; 6] {
    let (ms, cc, hp, chop) = talents;
    let mut cost = [0i32; 6];
    cost[PLUM] = n + ms * ms;
    cost[LEMON] = n + cc * cc;
    cost[APPLE] = n + hp * hp;
    cost[IRON] = n + chop * chop;
    cost
}

pub fn afford_fruit_only(inv: &[i32; 6], cost: &[i32; 6]) -> bool {
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE]
}

pub fn mb_afford(inv: &[i32; 6], cost: &[i32; 6], have_iron: bool) -> bool {
    let iron_ok = !have_iron || inv[IRON] >= cost[IRON];
    inv[PLUM] >= cost[PLUM] && inv[LEMON] >= cost[LEMON] && inv[APPLE] >= cost[APPLE] && iron_ok
}

pub fn ge_fruit_ty(t: &str) -> Option<usize> {
    match t {
        "PLUM" => Some(0),
        "LEMON" => Some(1),
        "APPLE" => Some(2),
        "BANANA" => Some(3),
        _ => None,
    }
}

// ── R5.0: deterministic tie-break "spread" ──────────────────────────────────
// v1.20.0's HashSet iteration accidentally gave RANDOM-PER-GAME tie-breaking, which
// spread plant spots around the shack; the R1 lexicographic determinization clustered
// them (measured ~-0.5 arena vs same-hour baseline). These helpers restore the spread
// deterministically: a per-game salt from immutable map facts (STABLE WITHIN a game so
// tied targets never flap turn-to-turn) mixed with the cell -> a pseudo-random rank.

/// per-game-stable salt from immutable map facts (varies across maps/seats).
pub fn tie_salt(state: &State) -> u64 {
    let (sx, sy) = state.my_shack;
    let (ox, oy) = state.opp_shack;
    let mut h = 0x9E37_79B9_7F4A_7C15u64;
    for v in [
        sx as u64,
        sy as u64,
        ox as u64,
        oy as u64,
        state.walkable.len() as u64,
        state.water_cells.len() as u64,
        state.iron_cells.len() as u64,
    ] {
        h ^= v.wrapping_mul(0x0000_0100_0000_01B3);
        h = h.rotate_left(23).wrapping_mul(0xFF51_AFD7_ED55_8CCD);
    }
    h
}

/// mix a cell with the salt -> deterministic pseudo-random tie-break rank.
pub fn tie_mix(c: Cell, salt: u64) -> u64 {
    let mut h = salt
        ^ (c.0 as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15)
        ^ (c.1 as u64).wrapping_mul(0xC2B2_AE3D_27D4_EB4F);
    h ^= h >> 33;
    h = h.wrapping_mul(0xFF51_AFD7_ED55_8CCD);
    h ^= h >> 29;
    h
}

}
pub use state::*;
pub mod motion {
//! Motion layer (R3b): everything about *getting trolls where their job says without
//! wasting moves* — distinct camp-cell claiming for bank/park (v1.20.0, the #1 near-camp
//! block fix) and the anti-stall watchdog (sidestep after 2 stuck turns). Extracted
//! VERBATIM from decide_elite (closures → functions); behavior equality is enforced by
//! the black-box harness. The corridor tests (tests/motion_corridor.rs) pin the required
//! swap-pipeline behavior this layer must keep enabling.
use super::*;
use std::cell::RefCell;
use std::collections::{HashMap, HashSet};

thread_local! {
    // anti-stall watchdog (mirrors decide_rhea/RH_LASTPOS):
    // troll id -> (x, y, same-pos streak while MOVEing). Reset at turn 1.
    static GE_LASTPOS: RefCell<HashMap<i32, (i32, i32, u8)>> = RefCell::new(HashMap::new());
}

/// Turn-1 reset of the watchdog memory.
pub fn reset() {
    GE_LASTPOS.with(|m| m.borrow_mut().clear());
}

/// nearest UNCLAIMED walkable drop cell (& claim it) — trolls heading to the camp claim
/// DISTINCT shack-adjacent cells so they don't converge on one cell and block each other.
pub fn pick_camp_cell(
    state: &State,
    shack: Cell,
    d: &HashMap<Cell, i32>,
    claimed: &mut HashSet<Cell>,
) -> Cell {
    let free = ortho_neighbors(shack)
        .into_iter()
        .filter(|c| state.walkable.contains(c) && !claimed.contains(c))
        .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30));
    let cell = free
        .or_else(|| {
            // all camp cells claimed (rare): fall back to the nearest walkable one
            ortho_neighbors(shack)
                .into_iter()
                .filter(|c| state.walkable.contains(c))
                .min_by_key(|c| d.get(c).copied().unwrap_or(1 << 30))
        })
        .unwrap_or(shack);
    claimed.insert(cell);
    cell
}

/// DROP if shack-adjacent, else MOVE toward a claimed camp cell.
pub fn bank_cmd(
    state: &State,
    shack: Cell,
    u: &Troll,
    d: &HashMap<Cell, i32>,
    claimed: &mut HashSet<Cell>,
) -> String {
    if manhattan(u.pos(), shack) == 1 {
        format!("DROP {}", u.id)
    } else {
        let c = pick_camp_cell(state, shack, d, claimed);
        format!("MOVE {} {} {}", u.id, c.0, c.1)
    }
}

/// MOVE toward a claimed camp cell. `idle=true` (band-10 idle parking) additionally steps
/// back from a SCARCE camp — v1.41.0-nopickloop (user-observed): when the shack has <=2
/// walkable ortho-neighbors, an idle-parking troll piling onto the one or two cells a
/// banker actually needs blocks the bank. Prefer the nearest unclaimed, reachable
/// manhattan-2 ring cell instead (one step further out, out of the banker's way); fall
/// back to the normal camp-cell claim if no such cell is reachable/free (e.g. a true 1-2
/// cell dead end with nothing beyond it).
///
/// `idle=false` (the band-49 park-to-pick ERRAND, planner.rs `Kind::Park` with
/// `target: Some(shack)`) always takes the direct camp-cell approach and NEVER the ring-2
/// detour — reviewer-caught CRITICAL bug: the errand is GOAL-DIRECTED (it must reach
/// manhattan==1 to unlock band-50's PICK), but the ring-2 redirect has no convergence
/// guarantee toward that goal. `claimed` is a fresh `HashSet` every `assign()` call (see
/// planner.rs), so a redirected errand that reaches its own ring-2 cell sees, next turn,
/// that same cell as the nearest unclaimed manhattan-2 option (distance 0 from itself) and
/// reissues a MOVE to its own position forever — a permanent stall on scarce-camp maps that
/// the anti-stall watchdog can't catch (it only sidesteps a MOVE whose target differs from
/// the troll's current cell).
pub fn park_cmd(
    state: &State,
    shack: Cell,
    u: &Troll,
    d: &HashMap<Cell, i32>,
    claimed: &mut HashSet<Cell>,
    idle: bool,
) -> String {
    if idle {
        let camp_cells = ortho_neighbors(shack)
            .iter()
            .filter(|c| state.walkable.contains(*c))
            .count();
        if camp_cells <= 2 {
            let ring2 = state
                .walkable
                .iter()
                .filter(|c| manhattan(**c, shack) == 2 && !claimed.contains(*c))
                .filter_map(|c| d.get(c).map(|&dist| (*c, dist)))
                .min_by_key(|(c, dist)| (*dist, *c));
            if let Some((c, _)) = ring2 {
                claimed.insert(c);
                return format!("MOVE {} {} {}", u.id, c.0, c.1);
            }
        }
    }
    let c = pick_camp_cell(state, shack, d, claimed);
    format!("MOVE {} {} {}", u.id, c.0, c.1)
}

/// ANTI-STALL WATCHDOG: if a troll issued a MOVE but hasn't moved for 2+ consecutive
/// turns, it is self-blocked — sidestep to a free orthogonally-adjacent walkable cell.
/// This is the #1 arena loss cause (self-block stalls).
pub fn watchdog(state: &State, my: &[Troll], cmd_by_id: &mut HashMap<i32, String>) {
    GE_LASTPOS.with(|cell| {
        let mut m = cell.borrow_mut();
        for t in my {
            let cur = t.pos();
            let is_move = cmd_by_id
                .get(&t.id)
                .map_or(false, |c| c.starts_with("MOVE "));
            let entry = m.entry(t.id).or_insert((cur.0, cur.1, 0u8));
            let stuck = entry.0 == cur.0 && entry.1 == cur.1;
            entry.2 = if stuck && is_move {
                entry.2.saturating_add(1)
            } else {
                0
            };
            entry.0 = cur.0;
            entry.1 = cur.1;
            let streak = entry.2;
            if streak >= 2 && is_move {
                // parse the MOVE target; only sidestep if it isn't the cur cell
                let tgt = cmd_by_id.get(&t.id).and_then(|c| {
                    let p: Vec<&str> = c.split_whitespace().collect();
                    if p.len() == 4 {
                        Some((p[2].parse::<i32>().ok()?, p[3].parse::<i32>().ok()?))
                    } else {
                        None
                    }
                });
                if let Some((tx, ty)) = tgt {
                    if (tx, ty) != cur {
                        let mut cands: Vec<Cell> = Vec::new();
                        for nb in ortho_neighbors(cur) {
                            if state.walkable.contains(&nb) && !my.iter().any(|o| o.pos() == nb) {
                                cands.push(nb);
                            }
                        }
                        if !cands.is_empty() {
                            let pick = cands[(rh_rand() as usize) % cands.len()];
                            cmd_by_id.insert(t.id, format!("MOVE {} {} {}", t.id, pick.0, pick.1));
                            entry.2 = 0;
                        }
                    }
                }
            }
        }
    });
}

// ── R6a: JOINT MOVE SOLVER (the activity manager's motion stage) ────────────────
// The sequential cascade let iteration order + tie-breaks decide who moves where.
// This solver takes ALL movement intents (troll -> goal cell) and chooses this turn's
// landing cells JOINTLY: maximize total progress toward goals under the verified engine
// rules (final-cell conflicts; adjacent cross-steps SWAP; vacated-cell chains resolve;
// stationary teammates are hard obstacles). Design criterion: SHUFFLE INVARIANCE — the
// result is a function of the objective only (canonical candidate order + exhaustive
// joint search + total-order tie-break), never of input order.

/// Jointly choose this turn's MOVE landing cell per intent (troll id -> goal cell).
/// Returns id -> landing cell (may be the troll's own cell = effectively WAIT/stay).
pub fn solve_moves(state: &State, my: &[Troll], intents: &[(i32, Cell)]) -> HashMap<i32, Cell> {
    let moving: HashSet<i32> = intents.iter().map(|(id, _)| *id).collect();
    let stationary: HashSet<Cell> = my
        .iter()
        .filter(|t| !moving.contains(&t.id))
        .map(|t| t.pos())
        .collect();

    // canonical processing order: by troll id (input order must not matter)
    let mut intents: Vec<(i32, Cell)> = intents.to_vec();
    intents.sort();

    // per troll: candidate landing cells within movement range, canonical order
    let mut ids: Vec<i32> = Vec::new();
    let mut cands: Vec<Vec<(Cell, i32)>> = Vec::new(); // (landing, progress toward goal)
    for (id, goal) in &intents {
        let t = match my.iter().find(|t| t.id == *id) {
            Some(t) => t,
            None => continue,
        };
        let dg = bfs_distances(&state.walkable, &[*goal]);
        let dp = bfs_distances(&state.walkable, &[t.pos()]);
        let here = match dg.get(&t.pos()) {
            Some(&d) => d,
            None => {
                // goal unreachable: stay put (the watchdog / next replan handles it)
                ids.push(*id);
                cands.push(vec![(t.pos(), 0)]);
                continue;
            }
        };
        let mut cs: Vec<(Cell, i32)> = state
            .walkable
            .iter()
            .filter(|c| {
                dp.get(*c)
                    .map_or(false, |&d| d > 0 && d <= t.movement_speed)
            })
            .filter(|c| !stationary.contains(*c))
            .filter_map(|c| dg.get(c).map(|&d| (*c, here - d)))
            .filter(|(_, pr)| *pr >= 0) // progress or lateral sidestep; never retreat
            .collect();
        cs.push((t.pos(), 0)); // staying is always an option
        cs.sort_by_key(|(c, pr)| (-pr, *c)); // canonical: best progress, then cell order
        cs.truncate(8);
        ids.push(*id);
        cands.push(cs);
    }

    // exhaustive joint choice over ≤ 8^n combos (n ≤ ~4 trolls): maximize total progress;
    // validity = pairwise-distinct landing cells (swaps/chains through MOVING teammates are
    // legal under the engine; stationary cells were excluded above). Ties -> lexicographic
    // landing vector (one canonical rule; shuffle invariance holds).
    let n = ids.len();
    let mut best: Option<(i32, Vec<Cell>)> = None;
    let mut pick = vec![0usize; n];
    loop {
        let landing: Vec<Cell> = (0..n).map(|i| cands[i][pick[i]].0).collect();
        let distinct = {
            let mut s: Vec<Cell> = landing.clone();
            s.sort();
            s.windows(2).all(|w| w[0] != w[1])
        };
        if distinct {
            let total: i32 = (0..n).map(|i| cands[i][pick[i]].1).sum();
            let better = match &best {
                None => true,
                Some((bt, bl)) => total > *bt || (total == *bt && landing < *bl),
            };
            if better {
                best = Some((total, landing));
            }
        }
        // odometer over candidate indices
        let mut i = 0;
        loop {
            if i == n {
                break;
            }
            pick[i] += 1;
            if pick[i] < cands[i].len() {
                break;
            }
            pick[i] = 0;
            i += 1;
        }
        if i == n {
            break;
        }
        if n == 0 {
            break;
        }
    }

    let mut out = HashMap::new();
    if let Some((_, landing)) = best {
        for (i, id) in ids.iter().enumerate() {
            out.insert(*id, landing[i]);
        }
    }
    out
}

}
pub mod ownership {
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

fn classify_pressure(own_half_exposed: i32, created_exposed: i32, definite_opponent: bool) -> PressureState {
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
    let state_level = classify_pressure(own.own_half_exposed, own.created_exposed, definite_opponent);

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

}
pub mod planner {
//! L2 JOINT TASK ASSIGNMENT (R6b) — the activity manager's task stage.
//!
//! The sequential cascade (jobs.rs) let troll-id order decide contested resources: the
//! first troll `reserved` its target, later trolls avoided it. Here every troll's viable
//! tasks are enumerated as (target, value) CANDIDATES — the cascade's branch hierarchy
//! becomes value BANDS (spaced wider than any ETA, so each troll still prefers its higher
//! branch), ETA differentiates within a band — and the assignment is chosen JOINTLY:
//! exhaustive over per-troll top-K, maximizing total value, conflicting target claims
//! forbidden, canonical tie-break. SHUFFLE INVARIANCE: the plan depends on the objective,
//! never on troll/candidate iteration order.
use super::tactics::{farm_eligible, Phase, Plan, RingRole};
use super::*;
use std::cell::RefCell;
use std::collections::{HashMap, HashSet};

thread_local! {
    // last MoveTo target per troll (diagnostics: assignment-flap counter) + flap count
    static LAST_TGT: RefCell<HashMap<i32, Cell>> = RefCell::new(HashMap::new());
    static FLAPS: RefCell<u32> = RefCell::new(0);
}

/// Turn-1 reset of diagnostics.
pub fn reset() {
    LAST_TGT.with(|m| m.borrow_mut().clear());
    FLAPS.with(|f| *f.borrow_mut() = 0);
}

pub fn flaps() -> u32 {
    FLAPS.with(|f| *f.borrow())
}

const K: usize = 8; // per-troll candidate cap (bands make more irrelevant)
const BAND: i64 = 100_000; // > any ETA by orders of magnitude
                           // v1.28.1 STICKINESS: bonus for keeping last turn's target — the joint matcher re-plans
                           // globally every turn and small ETA shifts flipped assignments mid-travel (measured 16-36
                           // flaps/game = leaked steps, the v1.27 arena fade). Within-band (« BAND): stability never
                           // overrides the priority hierarchy, only breaks near-ties toward the current plan.
const STICKY: i64 = 6; // v1.28.3 sweep: residual flaps 2-21 at 3; absorb bigger ETA jitter
                       // v1.38.0-deny1 (A2 probe): bias the PRIMARY fell choice (bands 70/72 ONLY — not the
                       // anti-starvation fallback, not the starter's chop-help band) toward trees nearer the
                       // opponent's shack. Silver-era denial weighting toward the foe was the single biggest lever
                       // measured pre-planner (MB_DENIAL_W in botmain.rs); the R6b joint planner has carried weight
                       // 0 since it replaced that cascade. At DENY_W=0 every fell value is byte-identical to the
                       // pre-probe code (the subtracted term is `0 * x == 0`); DENY_W=1 only breaks near-ties and
                       // nudges marginal calls, « BAND — never overrides the priority hierarchy.
                       // v1.39.0-sharepen4: REVERTED — analyst b62c977 measured this candidate at ~17.0 (down from
                       // the 19.9-20.1 race-check band) and diagnosed a collision with the race check's own
                       // tie-breaking. Parked at 0 (byte-identical to pre-probe) pending a retest that doesn't fight
                       // RACE_SHARE_PEN; see tests/deny_probe.rs (its one test now requires DENY_W=1 and is ignored).
const DENY_W: i64 = 0; // A2 reverted — collided with the race check per analyst b62c977; knob kept at 0
                       // v1.36.0-race: mild discount for a JOINABLE contested tree (an enemy is already chopping it,
                       // but we can arrive before they finish) — the wood splits round-robin among cell-sharers
                       // (engine apply_chop), so a shared tree is worth slightly less than an uncontested one, but
                       // never enough to lose to a materially worse alternative. « BAND, like STICKY.
                       // v1.39.0-sharepen4: sweep 2 -> 4 per analyst (queue #1, b62c977) — the race check is the one
                       // mechanism that just gained +1.3 in the arena; the analyst's decoded losses show excessive
                       // trekking to contested trees when a free tree is only marginally farther away, so discount
                       // joinable contests harder.
const RACE_SHARE_PEN: i64 = 2; // sharepen4 kept-at-parity = INCONCLUSIVE under policy v2; champion (race) semantics = 2
// v1.53.0-pressurefarm (Task 2 Step 3): under Orange/Red observed pressure, a created/farm
// tree the ownership model marks not-safely-ours (plan.pressure.exposed_created_cells) gets
// a small within-band bump — raises it before less-urgent same-band work, never overrides
// the priority hierarchy (« BAND, same discipline as STICKY/DENY_W/RACE_SHARE_PEN above).
// Under Green/Yellow, exposed_created_cells is always empty (Yellow's own_half signal alone
// never implies created_exposed>0 — see ownership::classify_pressure), so this is always +0
// there: a proven no-op, not a static preference.
const PRESSURE_LIQ_BONUS: i64 = 4;
// v1.58.0-trainfruit: the training-corner PLANT/PICK bands. FUNDING-class (comparable to the
// 58-65 funding bands above) but strictly BELOW fund_lo(58) -- a real funding fetch for the
// CURRENTLY pending hand (which directly closes `need_fund` this instant) always wins over
// planting a NEW seed (a longer-horizon investment: tests/trainfruit.rs::
// trainfruit_band_ordering_does_not_displace_real_work part (a)); still strictly ABOVE the
// printer tier (52) so it beats generic foraging once real funding needs are satisfied. Both
// are also « the bank band (80) by construction (56 < 80), proven behaviorally by the same
// test's part (b): a full troll carrying a training seed is still banked, never diverted.
// PLANT (56) > PICK (54), mirroring 88 > 78's "plant what you already carry before fetching
// more" discipline.
const TRAIN_PLANT_BAND: i64 = 56; // plant an ALREADY-CARRIED training-fruit seed
const TRAIN_PICK_BAND: i64 = 54; // PICK a training-fruit seed from the tent (investment-guarded)

#[derive(Clone, Debug, PartialEq)]
enum Kind {
    Bank, // render via motion::bank_cmd (DROP if adjacent, else camp-cell MOVE)
    Park, // render via motion::park_cmd (target None = idle band-10, ring-2-aware;
    // target Some(shack) = band-49 park-to-pick errand, direct camp approach)
    ChopHere, // CHOP at current cell
    MoveTo,   // MOVE toward target (fell/fund/seed/mine-adjacent/plant travel)
    // PLANT <ty> at current cell. v1.58.0-trainfruit: generalized from a bare unit variant
    // (always "BANANA") to carry the item-type string, so the SAME banana band-88 code path
    // now also serves LEMON/PLUM/APPLE training-corner plants (see RingRole::train_fruit).
    PlantHere(&'static str),
    Harvest, // HARVEST at current cell
    Mine,    // MINE (adjacent to iron)
    // PICK <ty> (shack-adjacent). v1.58.0-trainfruit: same generalization as PlantHere.
    Pick(&'static str),
}

#[derive(Clone, Debug)]
struct Cand {
    kind: Kind,
    target: Option<Cell>, // claimed resource (tree/plant/iron-adj cell); None = un-contested
    value: i64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum ClaimClass {
    Cell,
    Fruit,
    Wood,
}

#[derive(Clone, Copy, Debug)]
struct ClaimInfo {
    class: ClaimClass,
    cell: Cell,
    steps: i64,
}

#[derive(Clone, Debug)]
struct Assignments {
    ids: Vec<i32>,
    cands: Vec<Vec<Cand>>,
    picks: Vec<usize>,
}

impl Assignments {
    fn idx(&self, id: i32) -> Option<usize> {
        self.ids.binary_search(&id).ok()
    }

    fn selected(&self, id: i32) -> Option<&Cand> {
        let i = self.idx(id)?;
        self.cands.get(i)?.get(self.picks[i])
    }

    fn selected_value(&self, id: i32) -> Option<i64> {
        self.selected(id).map(|c| c.value)
    }
}

fn eta(d: &HashMap<Cell, i32>, c: Cell, ms: i32) -> i64 {
    let dist = d.get(&c).copied().unwrap_or(1 << 20);
    ((dist + ms - 1) / ms.max(1)) as i64
}

fn value_band(value: i64) -> i64 {
    (value + BAND - 1) / BAND
}

fn claim_info(state: &State, c: &Cand, steps: i64) -> Option<ClaimInfo> {
    let cell = c.target?;
    let class = match c.kind {
        Kind::ChopHere => ClaimClass::Wood,
        Kind::Harvest => ClaimClass::Fruit,
        Kind::MoveTo => {
            let targets_tree = state.trees.iter().any(|p| p.pos() == cell);
            if targets_tree {
                match value_band(c.value) {
                    70 | 40 | 30 => ClaimClass::Wood,
                    63 | 62 | 58 | 52 | 44 | 38 => ClaimClass::Fruit,
                    _ => ClaimClass::Cell,
                }
            } else {
                ClaimClass::Cell
            }
        }
        Kind::Bank | Kind::Park | Kind::PlantHere(_) | Kind::Mine | Kind::Pick(_) => ClaimClass::Cell,
    };
    Some(ClaimInfo { class, cell, steps })
}

fn claims_conflict(a: ClaimInfo, b: ClaimInfo) -> bool {
    if a.cell != b.cell {
        return false;
    }
    match (a.class, b.class) {
        (ClaimClass::Fruit, ClaimClass::Wood) => a.steps >= b.steps,
        (ClaimClass::Wood, ClaimClass::Fruit) => b.steps >= a.steps,
        _ => true,
    }
}

/// candidates for one troll — a faithful transcription of the jobs.rs cascade into bands.
#[allow(clippy::too_many_lines)]
fn candidates(state: &State, plan: &Plan, my: &[Troll], u: &Troll, salt: u64) -> Vec<Cand> {
    let shack = plan.shack;
    let inv = &state.my_inventory;
    let d = bfs_distances(&state.walkable, &[u.pos()]);
    let ms = u.movement_speed;
    let is_chopper = u.chop_power >= 2;
    let mut out: Vec<Cand> = Vec::new();

    // B2 (Hoard): suppress felling except the denial emergency (an enemy troll within
    // map-distance 2 of the tree). Computed ONCE per candidates() call — a single multi-source
    // BFS from every opp troll, not a BFS per (enemy, tree) pair — and ONLY during Hoard, so
    // the Tempo path (the live meta) pays zero extra cost.
    let hoard = plan.phase == Phase::Hoard;
    let enemy_d: Option<HashMap<Cell, i32>> = if hoard {
        Some(bfs_distances(
            &state.walkable,
            &state.opp_trolls.iter().map(|e| e.pos()).collect::<Vec<_>>(),
        ))
    } else {
        None
    };
    let threatened = |pc: Cell| -> bool {
        enemy_d
            .as_ref()
            .map_or(false, |ed| ed.get(&pc).map_or(false, |&dd| dd <= 2))
    };

    // v1.56.0-ringfarm: the DIAGONAL ring cells are the protected ripe fruit/seed engine.
    // Computed ONCE (a ≤4-element set); consulted by fell_ok below, which gates every fell
    // band that must respect it — the chopper's 70/72 and the starter's chop-help 40/42.
    // Anti-starvation (30/31) deliberately does NOT consult fell_ok (it fells anything size≥1
    // as a last resort), exactly as it already ignores seed_cells — so a diagonal can still be
    // felled when the farm is otherwise dead, which is strictly better than parking.
    let diag_ring: HashSet<Cell> = plan
        .ring
        .iter()
        .filter(|(_, r)| *r == RingRole::Diagonal)
        .map(|(c, _)| *c)
        .collect();
    // v1.58.0-trainfruit: the up-to-3 training-corner cells (TrainLemon/TrainPlum/
    // TrainApple) are ALSO kept standing — same protection as the diagonal banana cells,
    // just a separate set (a different tree TYPE, so `fell_ok`'s farm_banana branch below
    // would otherwise treat a grown PLUM/LEMON/APPLE tree here as a plain size>=2 NATIVE
    // fell target once it reached fell_size, destroying the investment). Same exceptions
    // apply: released only in liquidation or under an active raid.
    let train_ring: HashSet<Cell> = plan
        .ring
        .iter()
        .filter(|(_, r)| r.train_fruit().is_some())
        .map(|(c, _)| *c)
        .collect();

    let fell_ok = |p: &Tree| -> bool {
        // v1.56.0-ringfarm: keep the diagonal ripe/seed engine STANDING — never a fell
        // candidate except the endgame (plan.liquidation) or an active raid (plan.raid).
        // Orthogonal ring cells are NOT here, so they stay fellable as farm bananas below.
        if diag_ring.contains(&p.pos()) && !plan.liquidation && !plan.raid {
            return false;
        }
        // v1.58.0-trainfruit: same protection, same exceptions, for the training corner.
        if train_ring.contains(&p.pos()) && !plan.liquidation && !plan.raid {
            return false;
        }
        // v1.53.0-pressurefarm (Task 2 Step 2): a protected seed tree stays protected UNLESS
        // the pressure governor has specifically released it (Orange/Red AND this exact
        // tree is definitively not ours — see ownership::Pressure::released_seed_cells's doc
        // comment for why the release check is per-tree, not the broader "exposed" set).
        // Under Green/Yellow/Orange-without-a-definite-loser, released_seed_cells is always
        // empty, so this is byte-identical to the pre-pressure check.
        if plan.seed_cells.contains(&p.pos()) && !plan.pressure.released_seed_cells.contains(&p.pos())
        {
            return false;
        }
        if plan.liquidation {
            return p.size >= 1;
        }
        let farm_banana = p.tree_type == "BANANA"
            && plan
                .farm_d
                .get(&p.pos())
                .map_or(false, |&fd| fd <= plan.farm_r);
        p.size
            >= if farm_banana {
                plan.farm_fell
            } else {
                plan.fell_size
            }
    };
    let own_half =
        |p: &Tree| plan.liquidation || manhattan(p.pos(), shack) <= manhattan(p.pos(), plan.opp);
    let within_roam = |p: &Tree| {
        plan.liquidation
            || plan
                .farm_d
                .get(&p.pos())
                .map_or(false, |&fd| fd <= plan.chop_r)
    };
    // v1.36.0-race (user replay finding): a tree an enemy is already chopping is a RACE.
    // If they fell it before we arrive, walking there donates the travel (skip). If we can
    // arrive in time, the wood SPLITS round-robin among cell-sharers (engine apply_chop) —
    // join, but discount the value by the shared payoff. Pure function of `state` (no
    // per-troll mutable state), so shuffle invariance holds; called once per candidate,
    // covers every fell-type push (bands 72/70, 42/40, 31/30) via this one helper.
    let race = |pc: Cell, our_eta: i64| -> Option<i64> {
        // returns None = doomed (skip candidate); Some(penalty) = value adjustment
        let occupant = state
            .opp_trolls
            .iter()
            .find(|e| e.pos() == pc && e.chop_power > 0);
        match occupant {
            None => Some(0),
            Some(e) => {
                let h = state
                    .trees
                    .iter()
                    .find(|p| p.pos() == pc)
                    .map(|p| p.health)
                    .unwrap_or(0) as i64;
                let their_turns = (h + e.chop_power as i64 - 1) / e.chop_power.max(1) as i64;
                if their_turns <= our_eta {
                    None // they finish first: doomed
                } else {
                    Some(RACE_SHARE_PEN) // joinable: shared wood, mild discount
                }
            }
        }
    };
    // v1.53.0-pressurefarm (Task 2 Step 3): see PRESSURE_LIQ_BONUS's doc comment above.
    //
    // Code review I1 (2026-07-09): `race_pen` must gate this too. PRESSURE_LIQ_BONUS (4) >
    // RACE_SHARE_PEN (2), so applying the bonus unconditionally on a joinable-contested tree
    // (race_pen == RACE_SHARE_PEN) would more than cancel that discount (net +2), REVERSING
    // the race check's tuned "don't over-trek to a shared/discounted tree" behavior into a
    // preference for it — the exact opposite of what v1.36.0-race earned its +1.3. A doomed
    // tree (race() returned None) never reaches here at all (every call site `continue`s on
    // None before computing race_pen or calling this), so the only two live values of
    // race_pen are 0 (no opponent occupant — genuinely non-contested) and RACE_SHARE_PEN (a
    // joinable race). Withholding the bonus whenever race_pen != 0 therefore fully preserves
    // it on every non-contested exposed tree (this behavior's primary job — raise exposed
    // farm trees so we fell them before the opponent arrives) while making a contested tree's
    // net adjustment exactly `-race_pen` either way, never a reversal.
    let pressure_bonus = |pc: Cell, race_pen: i64| -> i64 {
        if race_pen != 0 {
            return 0;
        }
        if plan.pressure.state >= ownership::PressureState::Orange
            && plan.pressure.exposed_created_cells.contains(&pc)
        {
            PRESSURE_LIQ_BONUS
        } else {
            0
        }
    };

    // plant-cell search (shared across bands 80/88/50/49): the best free base cell within
    // the farm radius, reachable from this troll. Computed ONCE, whenever there's farm room
    // (base_trees < farm_cap), for EVERY troll — chopper included; band 80 just below needs
    // the answer even though only a non-chopper carrying a banana can ever act on it — so
    // band 80 (full -> bank), band 88 (plant the carried banana) and the PICK/park-to-pick
    // bands (50/49, both in the STARTER branch further down) all agree on whether a banana
    // would even be usable.
    // v1.41.0-nopickloop (user-observed corridor livelock): on maps where water + the map
    // edge leave no reachable, tree-free, un-occupied cell within the farm radius (a
    // dead-end pocket, or a shack whose few walkable neighbors are all tree/troll-occupied),
    // the OLD code still issued PICK whenever the tent held a banana. The picked banana then
    // had nowhere to plant; band 80 (full->bank) was suppressed for a banana-carrying
    // starter expecting to plant it (gated on the tree-COUNT `base_trees < farm_cap`, not a
    // free-CELL check — the bug's heart), so the fallback band 10 banked it right back next
    // turn, and PICK fired again the turn after — an infinite PICK<->DROP loop that also
    // parked the starter on a scarce shack-adjacent cell the chopper needs for banking.
    // Gating bands 88/50/49 on `plant_cell.is_some()` fixed the PICK half; band 80 below,
    // gated the same way (reviewer MINOR fix), closes the other half — a carried banana with
    // nowhere reachable to plant is banked, not hoarded waiting for a spot that never opens.
    // v1.56.0-ringfarm: the ring IS the farm. In every real game `plan.ring` is the up-to-8
    // Chebyshev-1 tent cells (role-tagged, front-door-filtered — see tactics::compute_ring),
    // and the plant target is the nearest reachable EMPTY ring cell for THIS troll. plant_cell
    // becomes None once the ring is full, which caps the farm at the tight 8-ring (the proven
    // throughput lever: shortest possible bank trips — no scattered farm_cap=12 spread). On a
    // hand-built test Plan with `ring: vec![]` we fall back to the pre-ring farm_cap chooser,
    // so the legacy pick/plant/nopickloop/nanaflow tests keep their exact old semantics.
    // `ring_active` also raises the build-ring PICK bands (78/77) in the printer section below.
    let ring_active = !plan.ring.is_empty();
    // v1.58.0-trainfruit: the banana plant_cell chooser must never target a training-corner
    // cell (TrainLemon/TrainPlum/TrainApple) -- those are a different fruit's dedicated slot,
    // planted/picked by the separate training-fruit logic further down.
    let banana_ring_candidates: Vec<(Cell, RingRole)> = plan
        .ring
        .iter()
        .copied()
        .filter(|(_, role)| matches!(role, RingRole::Diagonal | RingRole::Orthogonal))
        .filter(|(c, _)| d.contains_key(c)) // reachable from this troll
        .filter(|(c, _)| !state.trees.iter().any(|p| p.pos() == *c)) // empty ring cell
        .filter(|(c, _)| !my.iter().any(|o| o.id != u.id && o.pos() == *c)) // not blocked by a teammate
        .collect();
    // nearest empty ring cell; canonical (dist, tie_mix) tie-break — the ring geometry
    // already fixes the roles (v1.56.0-ringfarm's original semantics: no diagonal-priority
    // -- v1.57.0-ringtune's FIX2 diagonal-first placement was arena-reverted at ~-2.4, see
    // docs/silver-experiment-log.md 2026-07-10, so this candidate is rebased on plain
    // v1.56.0-ringfarm, not the reverted tuning), so we just build the ring fastest (least
    // travel). v1.58.0-trainfruit: still consults `banana_ring_candidates` (not the raw
    // `plan.ring`) so a training-corner cell is never chosen as a banana plant target.
    let plant_cell: Option<Cell> = if ring_active {
        banana_ring_candidates
            .iter()
            .copied()
            .min_by_key(|(c, _)| (d[c], tie_mix(*c, salt)))
            .map(|(c, _)| c)
    } else if plan.base_trees < plan.farm_cap {
        state
            .walkable
            .iter()
            .filter(|c| {
                farm_eligible(&plan.farm_d, &plan.door_d, **c, plan.farm_r) && d.contains_key(*c)
            })
            .filter(|c| !state.trees.iter().any(|p| p.pos() == **c))
            .filter(|c| !my.iter().any(|o| o.id != u.id && o.pos() == **c))
            .min_by_key(|c| {
                let wet = state.water_cells.iter().any(|w| manhattan(*w, **c) == 1);
                // v1.37.0-nanaflow (user replay finding #3): DIAGONAL PLANT PLACEMENT. The
                // four cells orthogonally adjacent to the shack (farm_d==1) are the only
                // bank/DROP cells every hand's carry trip needs — planting there congests
                // banking, so penalize them (+3). The four diagonal-to-shack cells sit at
                // the same map-distance (2) but off that traffic path, so reward them (-1).
                let bank_adj = plan.farm_d.get(*c).copied() == Some(1);
                let (cx, cy) = **c;
                let diag = (cx - plan.shack.0).abs() == 1 && (cy - plan.shack.1).abs() == 1;
                let geo = (if bank_adj { 3 } else { 0 }) + (if diag { -1 } else { 0 });
                (d[*c] + if wet { 0 } else { 2 } + geo, tie_mix(**c, salt))
            })
            .copied()
    } else {
        None
    };

    // endgame banking (band 95): bank a carried load in time to score it
    if u.total_carried() > 0 {
        let d_home = ortho_neighbors(shack)
            .iter()
            .filter(|c| state.walkable.contains(*c))
            .filter_map(|c| d.get(c))
            .min()
            .copied()
            .unwrap_or(i32::MAX / 2);
        let e = ((d_home + ms - 1) / ms.max(1) + 1) as i64;
        if (plan.turns_rem as i64) <= e + 1 {
            out.push(Cand {
                kind: Kind::Bank,
                target: None,
                value: 95 * BAND - e,
            });
        }
    }
    // full -> bank (band 80) — reviewer MINOR fix: was `plan.base_trees < plan.farm_cap` (a
    // tree COUNT), now `plant_cell.is_some()` (an actual reachable free CELL), matching the
    // gate bands 88/50/49 already use. A carried banana with no plantable cell should be
    // banked, not held waiting for room that will never materialize.
    if u.free_capacity() == 0 && !(!is_chopper && u.carry[BANANA] > 0 && plant_cell.is_some()) {
        out.push(Cand {
            kind: Kind::Bank,
            target: None,
            value: 80 * BAND,
        });
    }

    if is_chopper {
        // fell targets (band 70): standing (CHOP now) or travel; value differentiates by
        // steps + chop-time exactly like the cascade's nearest_fell metric.
        for p in state
            .trees
            .iter()
            .filter(|p| fell_ok(p) && own_half(p) && within_roam(p))
        {
            let pc = p.pos();
            if !d.contains_key(&pc) {
                continue;
            }
            if hoard && !threatened(pc) {
                continue; // Hoard: no fells unless the tree is under denial threat
            }
            let steps = eta(&d, pc, ms);
            let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
            let race_pen = match race(pc, steps) {
                None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                Some(pen) => pen,
            };
            // A2 probe (DENY_W): trees closer to the opponent lose less -> rank higher.
            let deny_pen = DENY_W * (manhattan(pc, plan.opp) as i64 / 2);
            let pbonus = pressure_bonus(pc, race_pen);
            if pc == u.pos() {
                // standing on a fellable tree: FINISH IT (cascade branch order) — band 72
                // outranks every travel-fell so invested chops are never abandoned.
                out.push(Cand {
                    kind: Kind::ChopHere,
                    target: Some(pc),
                    value: 72 * BAND - chop_t - race_pen - deny_pen + pbonus,
                });
            } else {
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 70 * BAND - (steps + chop_t) - race_pen - deny_pen + pbonus,
                });
            }
        }
        // anti-starvation fell anything (band 30)
        for p in state.trees.iter().filter(|p| p.size >= 1) {
            let pc = p.pos();
            if !d.contains_key(&pc) {
                continue;
            }
            if hoard && !threatened(pc) {
                continue; // Hoard: no fells unless the tree is under denial threat
            }
            let steps = eta(&d, pc, ms);
            let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
            let race_pen = match race(pc, steps) {
                None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                Some(pen) => pen,
            };
            if pc == u.pos() {
                out.push(Cand {
                    kind: Kind::ChopHere,
                    target: Some(pc),
                    value: 31 * BAND - chop_t - race_pen,
                });
            } else {
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 30 * BAND - (steps + chop_t) - race_pen,
                });
            }
        }
        // partial bank / park (band 10)
        out.push(Cand {
            kind: if u.total_carried() > 0 {
                Kind::Bank
            } else {
                Kind::Park
            },
            target: None,
            value: 10 * BAND,
        });
    } else {
        // `plant_cell` is hoisted above (before band 95/80) so band 80 can share it too —
        // see its doc comment there. Bands 88 (below) and 50/49 (further down) just consume
        // it.
        // 1) plant carried banana (band 88) at the best free base cell
        if u.carry[BANANA] > 0 {
            if let Some(tc) = plant_cell {
                let kind = if u.pos() == tc {
                    Kind::PlantHere("BANANA")
                } else {
                    Kind::MoveTo
                };
                out.push(Cand {
                    kind,
                    target: Some(tc),
                    value: 88 * BAND - eta(&d, tc, ms),
                });
            }
        }
        // 3) standing on a ripe wanted fruit (band 75)
        if let Some(p) = state.trees.iter().find(|p| p.pos() == u.pos()) {
            if p.fruits > 0 && u.harvest_power > 0 && u.free_capacity() > 0 {
                let ty = ge_fruit_ty(&p.tree_type);
                let funding = plan.want_chopper || plan.want_feeder;
                let want = (funding && ty.map_or(false, |t| t < 3 && plan.need_fund[t]))
                    || (!plan.want_chopper
                        && (p.tree_type == "BANANA"
                            || (p.tree_type == "APPLE"
                                && state
                                    .water_cells
                                    .iter()
                                    .any(|w| manhattan(*w, p.pos()) == 1))))
                    || plan.phase == Phase::Hoard; // Hoard wants EVERYTHING ripe standing under foot too
                if want {
                    out.push(Cand {
                        kind: Kind::Harvest,
                        target: Some(u.pos()),
                        value: 75 * BAND,
                    });
                }
            }
        }
        // B2 (Hoard): wallet-building — travel to ANY ripe fruit tree. Fruit is points AND
        // wallet fuel during Hoard, so there is no per-type targeting like the funding/printer
        // bands below (those stay as-is; the matcher just takes the max of every band pushed).
        if plan.phase == Phase::Hoard {
            for p in state
                .trees
                .iter()
                .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()))
            {
                let pc = p.pos();
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 62 * BAND - eta(&d, pc, ms),
                });
            }
        }
        // 4) FUNDING (bands 60/58) — for the chopper OR a pending 3rd hand (R6b.2: the old
        // feeder never trained because post-funding nobody harvested plum/lemon/apple)
        if plan.want_chopper || plan.want_feeder {
            // v1.28.1: the chopper is EXISTENTIAL (60/58) but a 3rd hand is a LUXURY — its
            // funding (45/44) must never displace printer/seed work (50/48). The v1.28.0
            // regression: perpetual feeder-funding starved the farm on lemon-poor maps.
            let (fund_hi, fund_lo) = if plan.want_chopper {
                (60, 58)
            } else {
                (45, 44)
            };
            // Gatekeeper verdict #3 (post-b14ebc7) fixed two compounding defects in one change:
            // (a) BAND COLLISION — e09ac48 (iron, 64/63) and b14ebc7 (fruit, 63) independently
            // landed on the SAME band, 63, so a troll needing both at once (routine: the
            // ladder's last hand needs all four resources together) picked whichever was
            // physically closer instead of the scarcer one. Iron has no fruit-harvest
            // alternative (B2.1: "iron is scarce and un-substitutable") so it must win
            // unconditionally — bumped to 65/64, strictly above the fruit band (63).
            // (b) T_SWITCH CLIFF — all these bands were gated `phase == Phase::Hoard` only, so
            // at t=140 a nearly-complete wallet was abandoned instantly (funding fell to
            // fund_lo=44, below Printer's 48/50) and the ladder's last hand never trained
            // (chopper 1/14 games). The elevated bands extend through a grace window scoped to
            // `want_feeder` (the ladder is still incomplete) instead of Hoard alone — it covers
            // Hoard (want_feeder is true throughout the ladder) AND the Factory grace (want_feeder
            // stays true until the ladder finishes), self-extinguishing once the ladder completes
            // (n reaches GE_MAX_TROLLS).
            // v1.35.0 (T-hand): renamed `scale_funding` -> `ladder_funding` and DROPPED the
            // `plan.phase != Phase::Tempo` gate — the elevated funding stack now serves ANY
            // pending ladder hand, including Tempo's revived 3rd hand (GE_MAX_TROLLS 2->3), not
            // just Scale's Hoard/Factory ladder. Graceful: a MoveTo/Mine candidate only exists
            // where ripe deficit fruit / adjacent iron actually exists on the map, and
            // `want_feeder` self-extinguishes the instant the pending hand trains — so Tempo
            // degrades to today's champion behavior on any map where the wallet never fills.
            // The generic wallet band (62, ~line 207 above) is UNTOUCHED: it stays gated on
            // `plan.phase == Phase::Hoard` directly, never on this variable.
            let ladder_funding = plan.want_feeder;
            if plan.need_iron && u.chop_power > 0 {
                if state
                    .iron_cells
                    .iter()
                    .any(|ic| manhattan(u.pos(), *ic) == 1)
                {
                    let v = if ladder_funding { 65 } else { fund_hi };
                    out.push(Cand {
                        kind: Kind::Mine,
                        target: Some(u.pos()),
                        value: v * BAND,
                    });
                } else if let Some(c) = state
                    .iron_cells
                    .iter()
                    .flat_map(|ic| ortho_neighbors(*ic))
                    .filter(|c| d.contains_key(c))
                    .min_by_key(|c| (d[c], tie_mix(*c, salt)))
                {
                    let v = if ladder_funding { 64 } else { fund_hi };
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(c),
                        value: v * BAND - eta(&d, c, ms),
                    });
                }
            }
            // Deficit-fruit funding (PLUM/LEMON/APPLE): same grace window, one band below iron.
            let fruit_band = if ladder_funding { 63 } else { fund_lo };
            for p in state.trees.iter().filter(|p| {
                p.fruits > 0
                    && d.contains_key(&p.pos())
                    && ge_fruit_ty(&p.tree_type).map_or(false, |t| t < 3 && plan.need_fund[t])
            }) {
                let pc = p.pos();
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: fruit_band * BAND - eta(&d, pc, ms),
                });
            }
        }
        // 4.5) TRAINING-CORNER PLANT (bands 56/54) — v1.58.0-trainfruit (user's training-fruit
        // corner): grow our OWN lemon/plum/apple supply to fund training faster (attacks the
        // documented funding-stall/lemon-wall). Unlike the banana ring-build (78/77, suppressed
        // by FIX1 while want_chopper), this is NEVER suppressed by want_chopper — planting a
        // training-fruit tree IS funding work (v1.58.0-trainfruit brief's "timing" section:
        // "training corner -> chopper -> banana ring"); only the banana ring-build stays gated.
        // Two steps mirror the banana ring's plant(88)/pick(78) pair, at the lower funding-tier
        // bands TRAIN_PLANT_BAND/TRAIN_PICK_BAND (see their doc comment for the numeric proof).
        //
        // INVESTMENT GUARD: a PICK here spends 1 unit of PLUM/LEMON/APPLE from the TENT
        // inventory (into carry; PLANT then consumes the carry) — the SAME pool `cost`/
        // `need_fund` draw from. Only safe when no hand is currently pending (want_chopper and
        // want_feeder both false — nothing to starve) OR there is a genuine SURPLUS beyond the
        // pending hand's cost for that resource (`inv[idx] > plan.cost[idx]`: still affordable
        // to train even after this seed leaves the pool). This also defuses a same-turn
        // engine-order hazard: PICK resolves BEFORE TRAIN (engine order MOVE, HARVEST, PLANT,
        // CHOP, PICK, TRAIN, DROP, MINE), so an exactly-at-threshold PICK this turn would
        // invalidate a TRAIN this turn's `train_now` already committed to firing. Once a seed
        // is ALREADY carried (a prior turn's PICK, or an incidental harvest), planting it is
        // always safe — the resource already left the tent pool, so holding it hostage in
        // carry helps nothing (see tests/trainfruit.rs::trainfruit_train_now_over_plant_last_seed).
        let imminent_hand = plan.want_chopper || plan.want_feeder;
        for (cell, role) in plan.ring.iter().copied() {
            let (Some(idx), Some(fruit)) = (role.train_idx(), role.train_fruit()) else {
                continue; // a banana (Diagonal/Orthogonal) ring cell — not this troll's job here
            };
            if state.trees.iter().any(|p| p.pos() == cell) {
                continue; // already planted
            }
            if my.iter().any(|o| o.id != u.id && o.pos() == cell) {
                continue; // blocked by a teammate
            }
            if !d.contains_key(&cell) {
                continue; // unreachable from this troll
            }
            if u.carry[idx] > 0 {
                // already carrying the seed -> plant it (band 56)
                let kind = if u.pos() == cell {
                    Kind::PlantHere(fruit)
                } else {
                    Kind::MoveTo
                };
                out.push(Cand {
                    kind,
                    target: Some(cell),
                    value: TRAIN_PLANT_BAND * BAND - eta(&d, cell, ms),
                });
                continue;
            }
            let safe_to_invest = !imminent_hand || inv[idx] > plan.cost[idx];
            if !safe_to_invest || inv[idx] <= 0 || u.free_capacity() == 0 {
                continue;
            }
            // target = shack: dedupes the pick errand across multiple hands (R6b.2), same
            // convention as the banana build-ring PICK.
            if manhattan(u.pos(), shack) == 1 {
                out.push(Cand {
                    kind: Kind::Pick(fruit),
                    target: Some(shack),
                    value: TRAIN_PICK_BAND * BAND,
                });
            } else {
                out.push(Cand {
                    kind: Kind::Park,
                    target: Some(shack),
                    value: TRAIN_PICK_BAND * BAND - 1,
                });
            }
        }
        // 5) PRINTER (bands 52/50/49) — v1.37.0-nanaflow (user replay finding #2): TREE-FIRST.
        // Harvesting a ripe seed tree directly converts its fruit straight into a farm seed;
        // banked tent stock is just as harvestable a turn later. So a ripe seed tree now
        // outranks the tent unconditionally (band 52, the old `inv[BANANA] == 0` gate is
        // REMOVED — harvested even with tent stock on hand). PICK/park (50/49, unchanged) is
        // the fallback once no ripe seed tree is reachable; excess bananas accumulate in the
        // tent via the existing full->bank flow (1pt banked each, or 8pt later via plant->fell).
        //
        // v1.56.0-ringfarm: under the ring, AGGRESSIVELY harvest the diagonal ripe bananas
        // (the seed engine) — band 52 keeps firing even when the ring is nominally "full" (so
        // the harvest→tent→replant loop never stalls). The seed RESERVE is the tent itself:
        // harvested bananas bank there and are pulled back by build-ring PICK(78)+plant(88)
        // whenever a cut orthogonal opens a cell ("some seed" replants, "some into tent" as
        // points via full→bank). Eta-discount keeps this LOCAL — a ripe diagonal at map-dist 2
        // always beats a distant native, and while the ring is incomplete build-ring(78) > 52
        // suppresses foraging entirely. PICK/park stay gated on plant_cell (an empty ring cell).
        if ring_active || plan.base_trees < plan.farm_cap {
            for p in state.trees.iter().filter(|p| {
                p.fruits > 0
                    && d.contains_key(&p.pos())
                    && (p.tree_type == "BANANA"
                        || (p.tree_type == "APPLE"
                            && state
                                .water_cells
                                .iter()
                                .any(|w| manhattan(*w, p.pos()) == 1)))
            }) {
                let pc = p.pos();
                out.push(Cand {
                    kind: Kind::MoveTo,
                    target: Some(pc),
                    value: 52 * BAND - eta(&d, pc, ms),
                });
            }
            // v1.41.0-nopickloop: only PICK (or travel to pick) if a plantable cell
            // actually exists (plant_cell.is_some()) — picking a banana with nowhere to
            // plant it is pure waste that just re-parks the starter on a scarce cell.
            // v1.56.0-ringfarm: BUILD THE RING EARLY. While the ring has an empty cell
            // (plant_cell.is_some() under the ring path) and a banana is available, the
            // pick->plant loop must outrank distant foraging — so the PICK band rises to 78
            // (park-to-pick 77) instead of 50/49. Numeric ordering (BAND = 100_000, every eta
            // « BAND): plant 88 > full-bank 80 > build-ring PICK 78 > park-to-pick 77 >
            // standing-harvest 75 > seed-move/idle-fruit ≤ 52. So it strictly beats the
            // distant harvest(75)/seed-move(52) but NEVER banking(80/95) or a carried-banana
            // plant(88) — and it is gated on a reachable empty ring cell, so once the ring is
            // full PICK is not offered at all and harvest wins (cannot displace real work on a
            // built ring). Off the ring path (`ring: vec![]` tests) it stays 50/49.
            let pick_band: i64 = if ring_active { 78 } else { 50 };
            if inv[BANANA] > 0 && u.free_capacity() > 0 && plant_cell.is_some() {
                // target = shack: dedupes the pick errand across multiple hands (R6b.2)
                if manhattan(u.pos(), shack) == 1 {
                    out.push(Cand {
                        kind: Kind::Pick("BANANA"),
                        target: Some(shack),
                        value: pick_band * BAND,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::Park,
                        target: Some(shack),
                        value: pick_band * BAND - 1,
                    });
                }
            }
        }
        // 6) chop help (band 40) + anti-starvation (band 30)
        if plan.starter_chop && u.chop_power > 0 {
            for p in state
                .trees
                .iter()
                .filter(|p| fell_ok(p) && own_half(p) && within_roam(p))
            {
                if u.free_capacity() == 0 {
                    break;
                }
                let pc = p.pos();
                if !d.contains_key(&pc) {
                    continue;
                }
                if hoard && !threatened(pc) {
                    continue; // Hoard: no fells unless the tree is under denial threat
                }
                let steps = eta(&d, pc, ms);
                let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
                let race_pen = match race(pc, steps) {
                    None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                    Some(pen) => pen,
                };
                let pbonus = pressure_bonus(pc, race_pen);
                if pc == u.pos() {
                    out.push(Cand {
                        kind: Kind::ChopHere,
                        target: Some(pc),
                        value: 42 * BAND - chop_t - race_pen + pbonus,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(pc),
                        value: 40 * BAND - (steps + chop_t) - race_pen + pbonus,
                    });
                }
            }
            if u.free_capacity() > 0 {
                for p in state.trees.iter().filter(|p| p.size >= 1) {
                    let pc = p.pos();
                    if !d.contains_key(&pc) {
                        continue;
                    }
                    if hoard && !threatened(pc) {
                        continue; // Hoard: no fells unless the tree is under denial threat
                    }
                    let steps = eta(&d, pc, ms);
                    let chop_t =
                        ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
                    let race_pen = match race(pc, steps) {
                        None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                        Some(pen) => pen,
                    };
                    if pc == u.pos() {
                        out.push(Cand {
                            kind: Kind::ChopHere,
                            target: Some(pc),
                            value: 31 * BAND - chop_t - race_pen,
                        });
                    } else {
                        out.push(Cand {
                            kind: Kind::MoveTo,
                            target: Some(pc),
                            value: 30 * BAND - (steps + chop_t) - race_pen,
                        });
                    }
                }
            }
        }
        // 6.5) IDLE-FRUIT (band 38, design D1 — champion loss taxonomy 2026-07-08 morning,
        // docs/silver-experiment-log.md: 45% of all losses are opponents out-fruiting us,
        // HARVEST+DROP 91-307 vs our flat 20-90). Strictly ABOVE anti-starvation (31/30) —
        // never competes with keeping the wood supply alive — and strictly BELOW chop-help
        // (42/40) and every printer/funding band above it (52/50/49/48/45/44/63/64/65/60/58) —
        // this is the fix for the v1.24.0-fruitbank trap (arena -1.0), which ranked
        // fruit-chasing ABOVE chop-help and lost. Because every one of those higher bands
        // already claims its own trees first, band 38 only ever wins the joint assignment on
        // a turn where nothing more valuable was available — it converts an otherwise-idle
        // turn into fruit points and never displaces wood work, seed work, or funding. No
        // per-type/own-half/roam gating on purpose ("harvest ANY ripe fruit"); mirrors the
        // ChopHere/MoveTo split used by every other band in this function.
        if u.harvest_power > 0 && u.free_capacity() > 0 {
            for p in state
                .trees
                .iter()
                .filter(|p| p.fruits > 0 && d.contains_key(&p.pos()))
            {
                let pc = p.pos();
                let steps = eta(&d, pc, ms);
                // reviewer IMPORTANT follow-up: same race check every other tree-targeting band
                // uses (70/72, 40/42, 30/31) — an enemy chopper already standing on this tree
                // fells it before we arrive, so chasing it donates the travel just like the
                // wood-fell case (doomed-target chasing). Unlike those bands, a joinable race
                // (Some(pen)) does NOT subtract the share-penalty: sharing a cell with an enemy
                // CHOPPER while WE harvest fruit isn't a wood-split situation (apply_chop's
                // round-robin split is a wood-only mechanic) — Some(_) here only means "not
                // doomed"; a same-cell Harvest (steps=0) is never doomed in practice (their_turns
                // is 0 only if the tree's health is already 0, which cannot coexist with the
                // `p.fruits > 0` filter above), so this uniform pre-branch check costs it nothing.
                if race(pc, steps).is_none() {
                    continue; // doomed: they fell it before we arrive — skip, don't donate the travel
                }
                if pc == u.pos() {
                    out.push(Cand {
                        kind: Kind::Harvest,
                        target: Some(pc),
                        value: 38 * BAND,
                    });
                } else {
                    out.push(Cand {
                        kind: Kind::MoveTo,
                        target: Some(pc),
                        value: 38 * BAND - steps,
                    });
                }
            }
        }
        // fallback (band 10)
        out.push(Cand {
            kind: if u.total_carried() > 0 {
                Kind::Bank
            } else {
                Kind::Park
            },
            target: None,
            value: 10 * BAND,
        });
    }

    // stickiness: prefer last turn's target on near-ties (see STICKY)
    let last = LAST_TGT.with(|m| m.borrow().get(&u.id).copied());
    if let Some(lt) = last {
        for c in out.iter_mut() {
            if c.target == Some(lt) {
                c.value += STICKY;
            }
        }
    }
    // canonical order + cap: by (-value, target) — never by discovery order
    out.sort_by_key(|c| (-c.value, c.target));
    out.truncate(K);
    out
}

fn select_assignments(state: &State, plan: &Plan, my: &[Troll]) -> Assignments {
    let salt = tie_salt(state);
    let mut ids: Vec<i32> = my.iter().map(|t| t.id).collect();
    ids.sort();
    let trolls: Vec<&Troll> = ids
        .iter()
        .map(|id| my.iter().find(|t| t.id == *id).unwrap())
        .collect();
    let cands: Vec<Vec<Cand>> = trolls
        .iter()
        .map(|t| candidates(state, plan, my, t, salt))
        .collect();
    let claim_infos: Vec<Vec<Option<ClaimInfo>>> = trolls
        .iter()
        .zip(cands.iter())
        .map(|(t, cs)| {
            let d = bfs_distances(&state.walkable, &[t.pos()]);
            cs.iter()
                .map(|c| {
                    let steps = c.target.map_or(0, |tc| eta(&d, tc, t.movement_speed));
                    claim_info(state, c, steps)
                })
                .collect()
        })
        .collect();

    let n = ids.len();
    let mut best: Option<(i64, Vec<usize>)> = None;
    let mut pick = vec![0usize; n];
    if n > 0 {
        loop {
            let mut ok = true;
            for i in 0..n {
                for j in 0..i {
                    if let (Some(a), Some(b)) = (claim_infos[i][pick[i]], claim_infos[j][pick[j]]) {
                        if claims_conflict(a, b) {
                            ok = false;
                            break;
                        }
                    }
                }
                if !ok {
                    break;
                }
            }
            if ok {
                let total: i64 = (0..n).map(|i| cands[i][pick[i]].value).sum();
                let better = match &best {
                    None => true,
                    Some((bt, bp)) => total > *bt || (total == *bt && pick < *bp),
                };
                if better {
                    best = Some((total, pick.clone()));
                }
            }
            let mut i = 0;
            loop {
                if i == n {
                    break;
                }
                pick[i] += 1;
                if pick[i] < cands[i].len() {
                    break;
                }
                pick[i] = 0;
                i += 1;
            }
            if i == n {
                break;
            }
        }
    }

    Assignments {
        ids,
        cands,
        picks: best.map(|(_, picks)| picks).unwrap_or_default(),
    }
}

fn render_assignments(
    state: &State,
    plan: &Plan,
    my: &[Troll],
    assignments: &Assignments,
    update_last_target: bool,
) -> HashMap<i32, String> {
    // render (troll-id order; camp-cell claiming stays deterministic via claimed_drop)
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
    let mut claimed_drop: HashSet<Cell> = HashSet::new();
    if !assignments.picks.is_empty() {
        for (i, id) in assignments.ids.iter().enumerate() {
            let u = my.iter().find(|t| t.id == *id).unwrap();
            let d = bfs_distances(&state.walkable, &[u.pos()]);
            let c = &assignments.cands[i][assignments.picks[i]];
            if update_last_target {
                if let (Kind::MoveTo, Some(tc)) = (&c.kind, c.target) {
                    LAST_TGT.with(|m| {
                        let mut m = m.borrow_mut();
                        if let Some(prev) = m.get(id) {
                            if *prev != tc && u.pos() != *prev {
                                FLAPS.with(|f| *f.borrow_mut() += 1);
                            }
                        }
                        m.insert(*id, tc);
                    });
                } else {
                    LAST_TGT.with(|m| m.borrow_mut().remove(id));
                }
            }
            let cmd = match (&c.kind, c.target) {
                (Kind::Bank, _) => motion::bank_cmd(state, plan.shack, u, &d, &mut claimed_drop),
                // idle band-10 (target None) gets the ring-2-aware scarce-camp step-back;
                // the band-49 park-to-pick ERRAND (target Some(shack)) never does — it is
                // goal-directed (must reach manhattan==1 to unlock PICK) and the ring-2
                // redirect has no such convergence guarantee (reviewer CRITICAL fix, see
                // motion::park_cmd's doc comment).
                (Kind::Park, park_target) => motion::park_cmd(
                    state,
                    plan.shack,
                    u,
                    &d,
                    &mut claimed_drop,
                    park_target.is_none(),
                ),
                (Kind::ChopHere, _) => format!("CHOP {}", u.id),
                (Kind::PlantHere(ty), _) => format!("PLANT {} {}", u.id, ty),
                (Kind::Harvest, _) => format!("HARVEST {}", u.id),
                (Kind::Mine, _) => format!("MINE {}", u.id),
                (Kind::Pick(ty), _) => format!("PICK {} {}", u.id, ty),
                (Kind::MoveTo, Some(tc)) => format!("MOVE {} {} {}", u.id, tc.0, tc.1),
                (Kind::MoveTo, None) => format!("MOVE {} {} {}", u.id, plan.shack.0, plan.shack.1),
            };
            cmd_by_id.insert(*id, cmd);
        }
    }
    cmd_by_id
}

fn move_intents(cmd_by_id: &HashMap<i32, String>) -> Vec<(i32, Cell)> {
    let mut intents: Vec<(i32, Cell)> = cmd_by_id
        .iter()
        .filter_map(|(id, c)| {
            let p: Vec<&str> = c.split_whitespace().collect();
            if p.len() == 4 && p[0] == "MOVE" {
                Some((*id, (p[2].parse().ok()?, p[3].parse().ok()?)))
            } else {
                None
            }
        })
        .collect();
    intents.sort();
    intents
}

fn pin_landing(my: &[Troll], cmd_by_id: &mut HashMap<i32, String>, landing: HashMap<i32, Cell>) {
    for (id, cell) in landing {
        let cur = my.iter().find(|t| t.id == id).map(|t| t.pos());
        if cur != Some(cell) {
            cmd_by_id.insert(id, format!("MOVE {} {} {}", id, cell.0, cell.1));
        }
    }
}

fn best_progress_without_stationary(
    state: &State,
    mover: &Troll,
    goal: Cell,
    stationary: &HashSet<Cell>,
) -> Option<i32> {
    let dg = bfs_distances(&state.walkable, &[goal]);
    let dp = bfs_distances(&state.walkable, &[mover.pos()]);
    let here = *dg.get(&mover.pos())?;
    let mut best = 0;
    for c in &state.walkable {
        if stationary.contains(c) {
            continue;
        }
        let Some(&from_here) = dp.get(c) else {
            continue;
        };
        if from_here == 0 || from_here > mover.movement_speed {
            continue;
        }
        let Some(&to_goal) = dg.get(c) else {
            continue;
        };
        let progress = here - to_goal;
        if progress >= 0 {
            best = best.max(progress);
        }
    }
    Some(best)
}

fn blocker_landing_progress(
    state: &State,
    mover: &Troll,
    goal: Cell,
    blocker_cell: Cell,
) -> Option<i32> {
    if !state.walkable.contains(&blocker_cell) {
        return None;
    }
    let dg = bfs_distances(&state.walkable, &[goal]);
    let dp = bfs_distances(&state.walkable, &[mover.pos()]);
    let here = *dg.get(&mover.pos())?;
    let from_here = *dp.get(&blocker_cell)?;
    if from_here == 0 || from_here > mover.movement_speed {
        return None;
    }
    let progress = here - *dg.get(&blocker_cell)?;
    (progress > 0).then_some(progress)
}

fn candidate_conflicts(
    assignments: &Assignments,
    blocker_idx: usize,
    target: Option<Cell>,
) -> bool {
    let Some(target) = target else {
        return false;
    };
    assignments.ids.iter().enumerate().any(|(i, _)| {
        i != blocker_idx && assignments.cands[i][assignments.picks[i]].target == Some(target)
    })
}

fn candidate_can_move_for_yield(plan: &Plan, u: &Troll, cand: &Cand) -> bool {
    match cand.kind {
        Kind::MoveTo | Kind::Park => true,
        Kind::Bank => manhattan(u.pos(), plan.shack) != 1,
        Kind::ChopHere | Kind::PlantHere(_) | Kind::Harvest | Kind::Mine | Kind::Pick(_) => false,
    }
}

fn reselect_blocker_for_yield(
    plan: &Plan,
    my: &[Troll],
    assignments: &mut Assignments,
    blocker_id: i32,
) -> bool {
    let Some(blocker_idx) = assignments.idx(blocker_id) else {
        return false;
    };
    let Some(u) = my.iter().find(|t| t.id == blocker_id) else {
        return false;
    };
    let old_pick = assignments.picks[blocker_idx];
    let old_target = assignments.cands[blocker_idx][old_pick].target;
    for new_pick in 0..assignments.cands[blocker_idx].len() {
        if new_pick == old_pick {
            continue;
        }
        let cand = &assignments.cands[blocker_idx][new_pick];
        if old_target.is_some() && cand.target == old_target {
            continue;
        }
        if candidate_conflicts(assignments, blocker_idx, cand.target) {
            continue;
        }
        if !candidate_can_move_for_yield(plan, u, cand) {
            continue;
        }
        assignments.picks[blocker_idx] = new_pick;
        return true;
    }
    false
}

fn yield_pass(
    state: &State,
    plan: &Plan,
    my: &[Troll],
    assignments: &mut Assignments,
    intents: &[(i32, Cell)],
    landing: &HashMap<i32, Cell>,
) -> bool {
    #[derive(Clone)]
    struct YieldCandidate {
        mover_id: i32,
        blocker_id: i32,
        mover_value: i64,
        blocker_value: i64,
    }

    let moving: HashSet<i32> = intents.iter().map(|(id, _)| *id).collect();
    let stationary_cells: HashSet<Cell> = my
        .iter()
        .filter(|t| !moving.contains(&t.id))
        .map(|t| t.pos())
        .collect();
    let stationary: Vec<&Troll> = my.iter().filter(|t| !moving.contains(&t.id)).collect();
    let mut pairs: Vec<YieldCandidate> = Vec::new();

    for (mover_id, goal) in intents {
        let Some(mover) = my.iter().find(|t| t.id == *mover_id) else {
            continue;
        };
        if landing.get(mover_id) != Some(&mover.pos()) {
            continue;
        }
        let Some(mover_value) = assignments.selected_value(*mover_id) else {
            continue;
        };
        let Some(normal_best) =
            best_progress_without_stationary(state, mover, *goal, &stationary_cells)
        else {
            continue;
        };
        if normal_best > 0 {
            continue;
        }
        for blocker in &stationary {
            let Some(blocker_value) = assignments.selected_value(blocker.id) else {
                continue;
            };
            if mover_value <= blocker_value {
                continue;
            }
            let Some(blocked_progress) =
                blocker_landing_progress(state, mover, *goal, blocker.pos())
            else {
                continue;
            };
            if blocked_progress > normal_best {
                pairs.push(YieldCandidate {
                    mover_id: *mover_id,
                    blocker_id: blocker.id,
                    mover_value,
                    blocker_value,
                });
            }
        }
    }

    pairs.sort_by_key(|p| (-p.mover_value, p.blocker_value, p.mover_id, p.blocker_id));
    for p in pairs {
        let mut trial = assignments.clone();
        if reselect_blocker_for_yield(plan, my, &mut trial, p.blocker_id) {
            *assignments = trial;
            if DEBUG {
                eprintln!(
                    "@TFYIELD t={} blocker={} mover={}",
                    state.turn, p.blocker_id, p.mover_id
                );
            }
            return true;
        }
    }
    false
}

/// Joint assignment: exhaustive over per-troll top-K candidates, maximize total value,
/// conflicting target claims forbidden, ties broken by the lexicographic pick vector.
pub fn assign(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let assignments = select_assignments(state, plan, my);
    render_assignments(state, plan, my, &assignments, true)
}

/// Assignment plus the live L3 motion pass. This keeps all task economics in the
/// joint matcher, then lets one lower-value stationary teammate yield to an urgent
/// blocked mover before final MOVE landing cells are pinned.
pub fn assign_resolved(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let mut assignments = select_assignments(state, plan, my);
    let initial_cmds = render_assignments(state, plan, my, &assignments, false);
    let initial_intents = move_intents(&initial_cmds);
    let initial_landing = motion::solve_moves(state, my, &initial_intents);

    let yielded = yield_pass(
        state,
        plan,
        my,
        &mut assignments,
        &initial_intents,
        &initial_landing,
    );
    let mut cmd_by_id = render_assignments(state, plan, my, &assignments, true);
    let landing = if yielded {
        let intents = move_intents(&cmd_by_id);
        motion::solve_moves(state, my, &intents)
    } else {
        initial_landing
    };
    pin_landing(my, &mut cmd_by_id, landing);
    cmd_by_id
}

}
pub mod tactics {
//! Tactics layer (L1, R4): everything decided BEFORE any troll is looked at — the
//! turn-1 adaptive chopper spec, train gating, farm geometry/phase, and the seed
//! reserve. `Plan` is the explicit L1→L2 interface consumed by jobs::assign_all.
//! Bodies moved VERBATIM from decide_elite; equality enforced by the harness.
use super::*;
use std::cell::RefCell;
use std::collections::{HashMap, HashSet};

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Meta {
    Tempo,
    Scale,
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Phase {
    Tempo,
    Hoard,
    Factory,
}

/// v1.56.0-ringfarm (user's farm-geometry scheme): the two roles of an 8-cell tent ring.
/// DIAGONAL cells (Chebyshev-diagonal to the shack) are the ripe fruit/seed engine: planted,
/// kept standing, harvested aggressively, felled only in the endgame or under raid (see
/// `Plan::raid`). ORTHOGONAL cells (the shack's four ortho-neighbors) are the wood/cut cycle:
/// felled at `farm_fell`, replanted -- the chopper already stands there to bank, so cutting
/// them costs zero extra travel.
///
/// v1.58.0-trainfruit (user's training-fruit corner): up to 3 of the 8 ring cells are
/// carved out as a compact TRAINING CORNER -- one each of TrainLemon/TrainPlum/TrainApple,
/// chosen adaptively by `compute_ring` (see its corner-selection doc comment below). These
/// cells are KEPT STANDING (never a banana plant_cell target, never felled for wood -- see
/// planner.rs's fell_ok training-corner protection) and harvested for training fuel: their
/// fruit funds TRAIN's cost vector exactly like any other PLUM/LEMON/APPLE source (the
/// existing funding/harvest bands already treat any tree generically by `ge_fruit_ty`, so
/// no new harvest logic is needed -- only the PLANT/PICK side is new, see planner.rs).
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum RingRole {
    Diagonal,
    Orthogonal,
    TrainLemon,
    TrainPlum,
    TrainApple,
}

impl RingRole {
    /// The PLANT/PICK item-type string for a training-corner role; `None` for the two
    /// banana roles (Diagonal/Orthogonal never override the fruit type -- planner.rs's
    /// banana plant_cell chooser handles those, unchanged).
    pub fn train_fruit(self) -> Option<&'static str> {
        match self {
            RingRole::TrainLemon => Some("LEMON"),
            RingRole::TrainPlum => Some("PLUM"),
            RingRole::TrainApple => Some("APPLE"),
            RingRole::Diagonal | RingRole::Orthogonal => None,
        }
    }

    /// The `state::{PLUM,LEMON,APPLE}` inventory/carry index for a training role.
    pub fn train_idx(self) -> Option<usize> {
        match self {
            RingRole::TrainLemon => Some(LEMON),
            RingRole::TrainPlum => Some(PLUM),
            RingRole::TrainApple => Some(APPLE),
            RingRole::Diagonal | RingRole::Orthogonal => None,
        }
    }
}

/// Scale meta: hoard (no felling, bank the wallet) until T_SWITCH, then the factory.
// Swept down per gatekeeper verdict #4 — hoarding until t=140 cedes the shared map to
// deforesting opponents (opp wood 60.1 vs our 23.2 avg, boss avg score delta -169.0): 100 =
// the design spec's sweep floor (docs/superpowers/specs/2026-07-07-last-mile-and-basin-jump-
// design.md, "Risks": T_SWITCH sweeps down to 120/100 if Hoard loses the early race
// unrecoverably). Note: SCALE_MIN_TURN stays [10, 40, 110] unchanged — slot 2 (the ladder's
// only chop-capable hand) now has its min-turn gate (110) ABOVE T_SWITCH (100), so it becomes
// eligible only after Factory has already begun. This is intentional: `ladder_funding`
// (planner.rs; renamed from `scale_funding` in v1.35.0-thand) keeps the funding bands elevated
// through a grace window scoped to `want_feeder`, not `phase == Phase::Hoard` alone, so the
// ladder's tail still gets funded priority even though it crosses the Hoard->Factory boundary —
// and, as of v1.35.0, the same grace window now also serves Tempo's own pending 3rd hand.
pub const T_SWITCH: i32 = 100;

pub fn phase_for(meta: Meta, turn: i32) -> Phase {
    match meta {
        Meta::Tempo => Phase::Tempo,
        Meta::Scale => {
            if turn < T_SWITCH {
                Phase::Hoard
            } else {
                Phase::Factory
            }
        }
    }
}

thread_local! {
    // v1.7.0: the chopper spec chosen ONCE at turn 1 from the starting draw.
    static GE_CHOSEN_SPEC: RefCell<Option<(i32, i32, i32, i32)>> = RefCell::new(None);
}

/// Turn-1 reset of the committed spec.
pub fn reset() {
    GE_CHOSEN_SPEC.with(|c| *c.borrow_mut() = None);
}

pub struct Plan {
    pub shack: Cell,
    /// MAP distances from the shack (BFS) — farm membership and chopper roam use THIS,
    /// not manhattan (user-found bug vs biz1: manhattan ignores water, so the starter
    /// planted "nearby" cells that were a long walk around a lake).
    pub farm_d: std::collections::HashMap<Cell, i32>,
    pub opp: Cell,
    pub have_iron: bool,
    pub turns_rem: i32,
    pub n: i32,
    pub farm_now: usize,
    pub nchop: i32,
    pub spec: (i32, i32, i32, i32),
    pub want_chopper: bool,
    pub want_feeder: bool,
    pub train_spec: (i32, i32, i32, i32),
    pub cost: [i32; 6],
    pub train_now: bool,
    pub need_iron: bool,
    pub need_fund: [bool; 3],
    pub farm_r: i32,
    pub farm_cap: usize,
    pub fell_size: i32,
    pub farm_fell: i32,
    pub chop_r: i32,
    pub starter_chop: bool,
    pub liquidation: bool,
    pub base_trees: usize,
    pub seed_cells: HashSet<Cell>,
    pub phase: Phase,
    /// v1.53.0-pressurefarm (Task 1 Step 3): the live ownership-pressure verdict, computed
    /// ONCE per turn below (never recomputed in planner.rs's per-troll hot loop). Under
    /// `PressureState::Green` this is always the all-zero/empty default and every
    /// pressure-gated behavior in planner.rs is a proven no-op (see
    /// tests/pressurefarm.rs::pressure_green_is_noop).
    pub pressure: ownership::Pressure,
    /// v1.54.0-frontdoor: the chosen "front door" cell when the shack straddles a
    /// detected chokepoint (see `compute_door`); `None` on every normal map — a proven
    /// no-op (tests/frontdoor.rs::frontdoor_open_map_noop).
    pub door: Option<Cell>,
    /// BFS distances from `door` (`Some` iff `door` is `Some`). `farm_eligible` uses
    /// THIS instead of `farm_d` at the farm/plant-membership sites exactly when a
    /// chokepoint override is active; every OTHER use of `farm_d` (banking-adjacency,
    /// chop-roam) is untouched.
    pub door_d: Option<HashMap<Cell, i32>>,
    /// v1.56.0-ringfarm (user's farm-geometry scheme): the up-to-8-cell tent ring
    /// (Chebyshev-1 around the shack), each cell tagged Diagonal (ripe fruit/seed engine)
    /// or Orthogonal (wood/cut cycle), filtered to walkable + reachable + front-door-
    /// eligible (`farm_eligible`, so on a chokepoint map only the reachable-side ring cells
    /// count — composes with v1.54.0-frontdoor). EMPTY on a hand-built test Plan
    /// (`ring: vec![]`) → planner.rs falls back to the pre-ring farm_cap placement; non-empty
    /// in every real game (the shack always has walkable neighbours). See `compute_ring`.
    pub ring: Vec<(Cell, RingRole)>,
    /// v1.56.0-ringfarm: an opponent troll is within `RING_RAID_R` BFS map-distance of the
    /// shack — a raid threat that RELEASES the diagonal ring bananas for defensive felling
    /// (see planner.rs `fell_ok`). A deliberately simple LOCAL trigger, NOT the parked
    /// ownership/pressure governor (brief: "keep it simple/local").
    pub raid: bool,
}

// ── FRONT-DOOR FARM PLACEMENT (v1.54.0-frontdoor) ───────────────────────────────────────
// `farm_d` above is a BFS SEEDED AT THE SHACK CELL: the shack is impassable to trolls (they
// can never stand on / re-enter it), but the BFS still treats it as a zero-cost hub, so
// cells on OPPOSITE sides of a shack that straddles a chokepoint (lake + boulders, e.g. the
// Sasso map) both read farm_d<=2 even when they are 20+ REAL walking steps apart — one
// connected component, a DISTANCE bug, not a connectivity one (user replay 895493013,
// confirmed: farm_d(14,4)=1 but real dist (12,4)->(14,4)=24). The farm/plant-membership
// filter then wrongly admits cells on BOTH sides, so the gatherer shuttles the full detour
// every trip (263/300 turns in transit, measured).
//
// Fix: `compute_door` detects the straddle (chokepoint-gated) and, ONLY then, picks a
// single "front door" — the shack's walkable neighbor farthest (true BFS distance) from
// the OPPONENT shack among candidates VIABLE enough to host a farm. `farm_eligible` then
// resolves farm/plant membership through the door's BFS instead of the shack-hub `farm_d`.
// On every normal (non-chokepoint) map `compute_door` returns `(None, None)` and
// `farm_eligible` reduces to exactly today's `farm_d.get(pos) <= r` — a proven no-op (see
// tests/frontdoor.rs::frontdoor_open_map_noop). `farm_d` keeps ALL its other uses
// (banking-adjacency `farm_d==1` in planner.rs's plant_cell chooser, chop-roam `chop_r`)
// untouched — only the farm/plant-membership sites route through `farm_eligible`.
pub const MIN_FARM_CELLS: usize = 4; // a candidate door must host at least this many walkable cells within GE_FARM_R to be VIABLE
pub const CHOKE_THRESHOLD: i32 = 8; // max true pairwise distance between door candidates before we call it a chokepoint (open maps: ~4 via the small detour around the shack; Sasso: 24)

/// Chokepoint-gated front-door selection. Returns `(None, None)` on every normal map:
/// fewer than 2 walkable shack-neighbors (nothing to straddle), every candidate mutually
/// close (`<= CHOKE_THRESHOLD`), or no candidate is VIABLE (>= `MIN_FARM_CELLS` walkable
/// cells within `GE_FARM_R`). Otherwise picks the viable candidate maximizing true BFS
/// distance from `state.opp_shack` (farthest-from-enemy — the enemy must travel farther to
/// raid our crops), tie-broken lexicographically on the cell.
///
/// Determinism: `candidates` is an explicit sorted `Vec` (never a HashSet iterated for
/// order); the viable list is explicitly sorted on `(-opp_dist, door_cell)` before picking
/// index 0 — the result depends only on map geometry, never on HashSet/HashMap internal
/// iteration order (see tests/frontdoor.rs::frontdoor_determinism_hashset_reorder).
pub fn compute_door(state: &State) -> (Option<Cell>, Option<HashMap<Cell, i32>>) {
    let shack = state.my_shack;
    let mut candidates: Vec<Cell> = ortho_neighbors(shack)
        .into_iter()
        .filter(|c| state.walkable.contains(c))
        .collect();
    candidates.sort();
    if candidates.len() < 2 {
        return (None, None); // nothing to straddle
    }

    let dds: Vec<(Cell, HashMap<Cell, i32>)> = candidates
        .iter()
        .map(|&c| (c, bfs_distances(&state.walkable, &[c])))
        .collect();

    let mut max_pair = 0;
    for i in 0..dds.len() {
        for j in (i + 1)..dds.len() {
            let dist = dds[i].1.get(&dds[j].0).copied().unwrap_or(i32::MAX / 2);
            max_pair = max_pair.max(dist);
        }
    }
    if max_pair <= CHOKE_THRESHOLD {
        return (None, None); // open map: no-op
    }

    let opp_d = bfs_distances(&state.walkable, &[state.opp_shack]);
    let mut viable: Vec<(Cell, i32)> = Vec::new();
    for (door, dd) in &dds {
        let count = state
            .walkable
            .iter()
            .filter(|c| dd.get(c).map_or(false, |&d| d <= GE_FARM_R))
            .count();
        if count >= MIN_FARM_CELLS {
            viable.push((*door, opp_d.get(door).copied().unwrap_or(0)));
        }
    }
    if viable.is_empty() {
        return (None, None); // no side can host a farm: fall back to plain farm_d
    }
    viable.sort_by_key(|&(door, od)| (-od, door));
    let chosen = viable[0].0;
    let chosen_d = dds.into_iter().find(|(c, _)| *c == chosen).map(|(_, d)| d);
    (Some(chosen), chosen_d)
}

/// Farm/plant-cell eligibility at radius `r`: `farm_d <= r` on every normal map (byte-
/// identical to the pre-frontdoor test); `door_d <= r` when a chokepoint override is
/// active. The only call sites this replaces are farm/plant-membership tests (tactics.rs
/// farm_now/base_trees below, planner.rs's plant_cell chooser) — NOT `farm_d==1` banking-
/// adjacency or `chop_r` roam, which keep consulting `farm_d` directly.
pub fn farm_eligible(
    farm_d: &HashMap<Cell, i32>,
    door_d: &Option<HashMap<Cell, i32>>,
    pos: Cell,
    r: i32,
) -> bool {
    match door_d {
        Some(dd) => dd.get(&pos).map_or(false, |&d| d <= r),
        None => farm_d.get(&pos).map_or(false, |&d| d <= r),
    }
}

// ── RING FARM (v1.56.0-ringfarm) ────────────────────────────────────────────────────────
/// An opponent troll within this BFS map-distance of the shack = a raid threat that releases
/// the diagonal ring bananas for defensive felling (brief: propose R=4). BFS, not manhattan,
/// so walls between the enemy and the shack correctly de-escalate.
pub const RING_RAID_R: i32 = 4;

/// v1.58.0-trainfruit: the 4 candidate training-corner quadrants, fixed canonical order
/// (NE, SE, SW, NW). Each quadrant is 2 orthogonals + the 1 diagonal between them, offsets
/// relative to the shack, with a FIXED per-cell fruit assignment -- the user's own NE
/// example (`(0,-1)=lemon, (1,-1)=plum, (1,0)=apple`) rotated 90 degrees per quadrant
/// (first ortho in rotational order = LEMON, the diagonal = PLUM, second ortho = APPLE).
/// "The exact cell-to-fruit mapping doesn't matter much" (brief) -- this just fixes ONE
/// canonical choice so the result never depends on iteration order.
const TRAIN_QUADRANTS: [[(i32, i32, &str); 3]; 4] = [
    [(0, -1, "LEMON"), (1, -1, "PLUM"), (1, 0, "APPLE")], // NE
    [(1, 0, "LEMON"), (1, 1, "PLUM"), (0, 1, "APPLE")],   // SE
    [(0, 1, "LEMON"), (-1, 1, "PLUM"), (-1, 0, "APPLE")], // SW
    [(-1, 0, "LEMON"), (-1, -1, "PLUM"), (0, -1, "APPLE")], // NW
];

fn train_role(fruit: &str) -> RingRole {
    match fruit {
        "LEMON" => RingRole::TrainLemon,
        "PLUM" => RingRole::TrainPlum,
        "APPLE" => RingRole::TrainApple,
        _ => unreachable!("TRAIN_QUADRANTS only ever names LEMON/PLUM/APPLE"),
    }
}

/// The 8-cell tent ring: the Chebyshev-1 cells around `shack`, filtered to walkable +
/// reachable-from-the-shack + `farm_eligible` (so on a chokepoint map only the front-door
/// side counts — composes with v1.54.0-frontdoor), each tagged with its role. DIAGONAL =
/// `|dx|==1 && |dy|==1` (the ripe fruit/seed engine); ORTHOGONAL = the shack's ortho-
/// neighbours (the wood/cut cycle).
///
/// v1.58.0-trainfruit (user's training-fruit corner): AFTER the base 8-cell ring is
/// computed, up to 3 of those cells are retagged into a compact TRAINING CORNER (one each
/// of TrainLemon/TrainPlum/TrainApple) -- a compact quadrant of 2 orthogonals + the 1
/// diagonal between them (`TRAIN_QUADRANTS`). Adaptive selection: among the 4 candidate
/// quadrants, prefer the one with the MOST cells already present in the eligible ring (so a
/// blocked/unreachable cell never gets silently substituted for -- "degrade gracefully:
/// place as many training trees as there are compact eligible cells, never on a far cell");
/// ties broken by farthest total BFS distance from the opponent shack (`opp_d`, reusing the
/// v1.54.0-frontdoor "farthest from enemy" idea -- our crops should be the enemy's longest
/// walk), then by the quadrant's fixed canonical index (NE/SE/SW/NW). A quadrant with ZERO
/// eligible cells is not a candidate at all (no training corner if the ring itself is too
/// sparse). Only the cells that ARE present in the winning quadrant get retagged; a missing
/// cell simply has no training tree this game (its slot's fruit type is skipped, not
/// reassigned elsewhere). The other 5 (or more, in a degraded case) ring cells stay
/// Diagonal/Orthogonal (the v1.56/57 banana scheme), unchanged.
///
/// Determinism: candidate cells are generated in a fixed (dy, dx) nested order and the base
/// result is explicitly sorted by cell before the corner retag (which mutates roles
/// in-place, so the cell ordering is untouched); the quadrant search is a fixed-size
/// (4-element) array scan, never a HashSet/HashMap iteration — this codebase was burned by
/// exactly that class of bug (see state.rs's tie_salt/tie_mix and compute_door's
/// determinism note).
pub fn compute_ring(
    walkable: &HashSet<Cell>,
    farm_d: &HashMap<Cell, i32>,
    door_d: &Option<HashMap<Cell, i32>>,
    shack: Cell,
    farm_r: i32,
    opp_d: &HashMap<Cell, i32>,
) -> Vec<(Cell, RingRole)> {
    let (sx, sy) = shack;
    let mut out: Vec<(Cell, RingRole)> = Vec::new();
    for dy in -1..=1 {
        for dx in -1..=1 {
            if dx == 0 && dy == 0 {
                continue;
            }
            let c = (sx + dx, sy + dy);
            if !walkable.contains(&c) {
                continue; // rock / water / off-map neighbour
            }
            if !farm_d.contains_key(&c) {
                continue; // not reachable from the shack at all
            }
            if !farm_eligible(farm_d, door_d, c, farm_r) {
                continue; // far side of a chokepoint (frontdoor door_d excludes it)
            }
            let role = if dx.abs() == 1 && dy.abs() == 1 {
                RingRole::Diagonal
            } else {
                RingRole::Orthogonal
            };
            out.push((c, role));
        }
    }
    out.sort_by_key(|(c, _)| *c);

    // ── TRAINING CORNER (v1.58.0-trainfruit) ────────────────────────────────
    let eligible: HashSet<Cell> = out.iter().map(|(c, _)| *c).collect();
    // (-count, -dist_sum, quadrant_index): ascending sort picks the smallest tuple, i.e.
    // the MOST eligible cells, then the FARTHEST total opp distance, then the lowest
    // (most-canonical) quadrant index.
    let mut scored: Vec<(i32, i32, usize)> = Vec::new();
    for (qi, quad) in TRAIN_QUADRANTS.iter().enumerate() {
        let mut count = 0i32;
        let mut dist_sum = 0i32;
        for (dx, dy, _fruit) in quad.iter() {
            let cell = (sx + dx, sy + dy);
            if eligible.contains(&cell) {
                count += 1;
                dist_sum += opp_d.get(&cell).copied().unwrap_or(0);
            }
        }
        if count == 0 {
            continue; // not a candidate: this quadrant has nothing to build on
        }
        scored.push((-count, -dist_sum, qi));
    }
    scored.sort();
    if let Some(&(_, _, qi)) = scored.first() {
        for (dx, dy, fruit) in TRAIN_QUADRANTS[qi].iter() {
            let cell = (sx + dx, sy + dy);
            if let Some(entry) = out.iter_mut().find(|(c, _)| *c == cell) {
                entry.1 = train_role(fruit);
            }
        }
    }

    out
}

fn plan_impl(state: &State, my: &[Troll], meta: Meta) -> Plan {
    let farm_d = bfs_distances(&state.walkable, &[state.my_shack]);
    let (door, door_d) = compute_door(state);
    let shack = state.my_shack;
    let opp = state.opp_shack;
    let inv = &state.my_inventory;
    let have_iron = !state.iron_cells.is_empty();
    let turns_rem = TOTAL_TURNS - state.turn + 1;

    let n = my.len() as i32;

    // ── training: ONE chopper, EARLY, spec ADAPTED to the starting draw (v1.7.0) ──
    // Denial > production (proven 2026-07-05): the chopper must train at turn 1 so we win
    // the shared-tree race. cc=3 captures 3 wood/tree but its lemon cost (n+9=10) only fits
    // a rich starting draw; cc=2 (lemon n+4=5) trains at t1 on nearly any draw. So pick the
    // RICHEST chopper the turn-1 inventory can train IMMEDIATELY — cc=3 when the draw affords
    // it (production), else cc=2 (denial) — NEVER delay waiting to afford cc=3.
    let spec = GE_CHOSEN_SPEC.with(|c| {
        let mut c = c.borrow_mut();
        if c.is_none() {
            // v1.9.0 (data-driven vs 32 real Boss-5 games): pick EACH axis independently to
            // level 3 iff the turn-1 draw's binding resource already affords it — ms<-plum,
            // cc<-lemon, chop<-iron (each level-3 costs n+9). This (a) FIXES the v1.7.0 bug
            // where a plum/iron shortfall wrongly locked cc2 on a lemon-rich map (cc3 vs cc2
            // differ ONLY in lemon), and (b) adopts Boss 5's ms=3/chop=3 flexibility (faster
            // travel + faster felling = the sustained-throughput lever it beats us on). An axis
            // upgrades only when its resource is ALREADY >= n+9, so it never delays training
            // beyond the cc2 baseline (the upgrade is "free"). hp=0 (can't harvest, cheap).
            // ms/cc/chop upgrade to 3 when their resource is free (>=n+9), else 2. (v1.14.0's cc1
            // tier on lemon-poor maps was WORSE: 0/5 wood 40 — cc1 throughput too low even with
            // the tight farm's cheap banking. A late cc2 beats an early cc1.)
            let lvl = |res: usize| if inv[res] >= n + 9 { 3 } else { 2 };
            *c = Some((lvl(PLUM), lvl(LEMON), 0, lvl(IRON)));
        }
        c.unwrap()
    });
    let farm_now = state
        .trees
        .iter()
        .filter(|p| farm_eligible(&farm_d, &door_d, p.pos(), GE_FARM_R))
        .count();
    // v1.11.0: troll 2 = the CHOPPER (early, adaptive spec). troll 3 = a FEEDER (late): a cheap
    // hp>0/chop=0 harvester. Because decide_elite routes any chop<2 troll through the STARTER
    // (printer) branch, the feeder auto-plants bananas — a 2nd pair of hands keeping the farm
    // DENSE so the single chopper never travels/idles (travel is ~2.5x the felling = the real
    // Boss-5 throughput gap). This is the runninglvlan structure (starter+feeder+chopper) and
    // AVOIDS the 2-chopper starvation (validated: a 2nd chopper starves the 1-feeder farm).
    let nchop = my.iter().filter(|u| u.chop_power >= 2).count() as i32;
    // B2 (Scale ladder): under Meta::Scale, replace the adaptive chopper-training logic with a
    // FIXED HAND ladder — want_chopper forced false (the early adaptive t1 chopper is REPLACED
    // by the ladder itself: its final slot trains a real chopper `(2,2,0,2)` once n reaches 3
    // hands, gated at t>=110; Hoard banks the wallet with hands only before that). Troll count n
    // selects the next hand's spec/turn-gate from
    // SCALE_LADDER/SCALE_MIN_TURN, mapped onto the SAME Plan fields the Tempo path uses
    // (want_feeder/train_spec/cost/train_now/need_iron/need_fund) so planner.rs needs no new
    // fields — it already reads want_feeder to drive funding/printer work. The Tempo branch
    // below is BYTE-IDENTICAL to the pre-B2 code (equality-critical: GE_META stays Tempo live).
    let (want_chopper, want_feeder, train_spec, cost, train_now, need_iron, need_fund) = if meta
        == Meta::Scale
    {
        const SCALE_LADDER: [(i32, i32, i32, i32); 3] = [(1, 1, 1, 0), (1, 1, 1, 0), (2, 2, 0, 2)];
        const SCALE_MIN_TURN: [i32; 3] = [10, 40, 110];
        let slot = ((n - 1).max(0) as usize).min(2);
        let want_hand = n < 4 && state.turn >= SCALE_MIN_TURN[slot];
        let want_chopper = false;
        let want_feeder = want_hand;
        let train_spec = SCALE_LADDER[slot];
        let cost = training_cost(n, train_spec);
        let train_now = want_hand && mb_afford(inv, &cost, have_iron);
        // B2.1 gatekeeper fix: accumulate iron EARLY (all of Hoard), not only once slot 2 is
        // reached at t>=110 — 7 = the slot-2 chopper's iron cost (n=3 + chop^2=4). Iron income
        // is otherwise zero (nothing mines it) and the map's starting stock rarely reaches 7 by
        // t110, so the wallet must be pre-filled during Hoard or the ladder's only chop-capable
        // hand never trains (wood=0 the entire game, confirmed 12/12 in the gatekeeper report).
        let need_iron = have_iron && inv[IRON] < 7;
        let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];
        (
            want_chopper,
            want_feeder,
            train_spec,
            cost,
            train_now,
            need_iron,
            need_fund,
        )
    } else {
        let want_chopper = nchop == 0 && (state.turn >= GE_CHOP_DELAY || farm_now >= GE_CHOP_FARM);
        let want_feeder = nchop >= 1
            && n < GE_MAX_TROLLS
            && state.turn >= GE_FEEDER_T
            && farm_now >= GE_FEEDER_FARM;
        let train_spec = if want_chopper { spec } else { GE_FEEDER_SPEC };
        let cost = training_cost(n, train_spec);
        let train_now = (want_chopper || want_feeder) && mb_afford(inv, &cost, have_iron);
        let want_chopper = want_chopper; // (kept: need_iron/need_fund below key off the pending hand)
                                         // iron-gated: fruit is ready but we still lack the iron for the PENDING HAND — the
                                         // chopper OR the feeder. T-hand.1 (gatekeeper v1.35.0 verdict, fix a): this used to be
                                         // want_chopper-only, so iron mining stopped FOREVER the instant the chopper trained,
                                         // permanently starving any later pending hand of its flat cost[IRON]=n training cost
                                         // (every spec carries it) on every iron-bearing map — 12/12 sampled by the gatekeeper.
        let need_iron = have_iron
            && (want_chopper || want_feeder)
            && inv[IRON] < cost[IRON]
            && afford_fruit_only(inv, &cost);
        // which fruit types still block the pending hand (funding targets)
        let need_fund: [bool; 3] = [inv[0] < cost[0], inv[1] < cost[1], inv[2] < cost[2]];
        (
            want_chopper,
            want_feeder,
            train_spec,
            cost,
            train_now,
            need_iron,
            need_fund,
        )
    };

    // ── farm config ─────────────────────────────────────────────────────────
    // v1.18.0: TURN-1 ADAPTIVE ECONOMY (committed via the draw-chosen spec, no mid-game switch).
    // High-draw map (spec chose cc>=3): economy B = BIG farm + size-3 fells (cc3 captures 3, chop3
    // fells size-3 in 2 chops; the cc3 banks-every-3 offsets the bigger farm's longer trips) — the
    // Boss-5 throughput economy. Low-draw map (cc2): economy A = the TIGHT farm (short bank trips,
    // fast size-2 maturation) that beats Boss 5 ~40%. Best of both, per the felling mechanics.
    let phase = phase_for(meta, state.turn);
    let econ_b = false; // econ B (big-farm size-3) arena-validated WORSE (135 vs 120) — the big farm cannot sustain size-3 maturation; pure tight-farm (A) is best
    let farm_r = if econ_b { 3 } else { GE_FARM_R };
    // B3 (Factory): once the Scale meta reaches Factory (post-T_SWITCH), the hoard-built wallet
    // funds a bigger farm — 20 slots instead of 12 — so the plant-and-fell loop has room to grow
    // with the trained hand ladder. Hoard/Tempo are unchanged (econ_b is a permanent `false`, so
    // they fall through to GE_FARM_MAX=12).
    let farm_cap = if phase == Phase::Factory {
        20
    } else if econ_b {
        20
    } else {
        GE_FARM_MAX
    };
    let fell_size = GE_FELL_SIZE; // NATIVE/contested trees: always size-2 = DENIAL
    let farm_fell = if econ_b { 3 } else { 2 }; // OUR farm bananas: size-3 in econ B, size-2 in A
    let chop_r = if econ_b { 10 } else { GE_CHOP_R }; // econ B roams a bigger farm; A stays tight
    let starter_chop = GE_STARTER_CHOP;
    let liquidation = turns_rem <= GE_LIQ_T;
    let base_trees = state
        .trees
        .iter()
        .filter(|p| farm_eligible(&farm_d, &door_d, p.pos(), farm_r))
        .count();

    // ── RING FARM geometry (v1.56.0-ringfarm) ───────────────────────────────
    // Computed ONCE per turn (borrows farm_d/door_d before they move into `provisional`).
    // Placement/fell/harvest in planner.rs consume it. `raid` = any opponent troll within
    // RING_RAID_R BFS map-distance of the shack (farm_d is the shack-seeded BFS; an
    // unreachable/walled-off enemy is never a raid).
    // v1.58.0-trainfruit: BFS from the opponent shack, for compute_ring's training-corner
    // "farthest from the enemy" tie-break (mirrors compute_door's own opp_d, computed
    // separately there since it's private to that function).
    let opp_d_ring = bfs_distances(&state.walkable, &[opp]);
    let ring = compute_ring(&state.walkable, &farm_d, &door_d, shack, farm_r, &opp_d_ring);
    let raid = state
        .opp_trolls
        .iter()
        .any(|e| farm_d.get(&e.pos()).map_or(false, |&d| d <= RING_RAID_R));

    // ── SEED SUSTAINABILITY (arena deforestation fix) ───────────────────────
    // Trees only fruit at MAX_SIZE(4); felling farm bananas at size 2 means they
    // NEVER fruit, so the seed supply drains -> the farm dies -> our half
    // deforests -> both trolls park (the decoded arena stall). Fix: keep the K
    // most-mature farm bananas as a permanent seed reserve the chopper won't fell.
    //
    // v1.56.0-ringfarm: when the ring is active (every real game), SKIP this generic reserve
    // entirely — the DIAGONAL ring cells are the protected seed engine now (planner.rs fell_ok
    // via `diag_ring`), a stronger and role-correct reserve. Keeping the generic "K most-mature
    // farm bananas" here would wrongly protect an ORTHOGONAL cut-cell whenever an orthogonal
    // happened to be the most mature, breaking the wood/cut cycle. Populated ONLY on the
    // `ring: vec![]` fallback (hand-built tests), where it preserves the exact pre-ring behaviour.
    let mut seed_cells: HashSet<Cell> = HashSet::new();
    if GE_SEED_RESERVE > 0 && !liquidation && ring.is_empty() {
        let mut fb: Vec<&Tree> = state
            .trees
            .iter()
            .filter(|p| {
                p.tree_type == "BANANA" && farm_d.get(&p.pos()).map_or(false, |&d| d <= farm_r)
            })
            .collect();
        fb.sort_by_key(|p| (-p.size, -p.fruits, manhattan(p.pos(), shack), p.pos()));
        for p in fb.into_iter().take(GE_SEED_RESERVE) {
            seed_cells.insert(p.pos());
        }
    }

    let provisional = Plan {
        shack,
        farm_d,
        opp,
        have_iron,
        turns_rem,
        n,
        farm_now,
        nchop,
        spec,
        want_chopper,
        want_feeder,
        train_spec,
        cost,
        train_now,
        need_iron,
        need_fund,
        farm_r,
        farm_cap,
        fell_size,
        farm_fell,
        chop_r,
        starter_chop,
        liquidation,
        base_trees,
        seed_cells,
        phase,
        pressure: ownership::Pressure::default(),
        door,
        door_d,
        ring,
        raid,
    };

    // ── PRESSURE GOVERNOR (v1.53.0-pressurefarm, Task 1 Step 2) ─────────────
    // ownership::assess only reads provisional.farm_d/farm_r/seed_cells (all already final
    // above) — the placeholder `pressure` field on `provisional` is never read by it, so
    // computing against the provisional Plan and overlaying the real pressure (plus its one
    // derived override, farm_cap) afterward is equality-safe. Computed exactly ONCE per
    // turn here — never inside planner.rs's per-troll candidates() hot loop.
    let pressure = ownership::assess(state, &provisional);
    // Task 2 Step 1 (dynamic farm cap): Orange+ pressure suppresses further expansion, but
    // NEVER below a small survival floor — a farm already at/under the floor keeps planting
    // regardless (the `.min` only ever shrinks the CEILING, it can't force liquidation). This
    // keeps Green/Yellow byte-identical (provisional.farm_cap is returned unchanged) and
    // avoids the "always smaller farm" static-control trap: the clamp only engages when
    // pressure is actually observed.
    //
    // Code review C2 (2026-07-09): re-gated from `>= Yellow` to `>= Orange`. Yellow only
    // requires `own_half_exposed > 0` (created_exposed == 0) — a signal that lights up from
    // static map geometry (any own-half tree we can't PROVE decisively ours) and is
    // near-permanent from ~turn 5 on real maps, independent of any real threat to farm value
    // WE created. Gating the clamp there collapsed farm_cap 12->4 for essentially the whole
    // game — exactly the "always smaller farm" nerf the paragraph above warns against, and a
    // throughput crater (dense-farm-never-idle is this bot's whole economic thesis). Orange
    // requires `created_exposed > 0` — a created/local farm tree the ownership model itself
    // marks not-safely-ours — which IS threat-discriminating (it needs the opponent's ETA to
    // actually contest a tree WE planted), matching this feature's own design intent (see
    // docs/pressure-aware-farm.md Task 0 Step 3, "Yellow: … pause expansion ONLY IF
    // created/local value exists") and data/analysis/map-value-ownership/report.md's
    // recommended trigger.
    //
    // Factory latent note (M1): under Phase::Factory the champion raises farm_cap to 20
    // (see the `phase == Phase::Factory` branch above); this clamp would override that down
    // to GE_PRESSURE_FARM_FLOOR if Orange+ pressure ever fires during Factory. Dormant today
    // (GE_META=Tempo, Factory unreachable) — flagged, not handled; no logic added here.
    let farm_cap = if pressure.state >= ownership::PressureState::Orange {
        provisional.farm_cap.min(GE_PRESSURE_FARM_FLOOR)
    } else {
        provisional.farm_cap
    };

    Plan {
        farm_cap,
        pressure,
        ..provisional
    }
}

pub fn plan(state: &State, my: &[Troll]) -> Plan {
    plan_impl(state, my, super::GE_META)
}

/// Test-only seam: drive `plan_impl` under an explicit `Meta` instead of the compile-time
/// `GE_META` const. Plain `pub` (not `cfg(test)`) because integration tests in `rust/tests/`
/// compile as a separate crate and can't see `cfg(test)` items; this is dead code in the arena
/// build, which the crate's `#![allow(dead_code, unused)]` already tolerates, and the bundler
/// carries it harmlessly (submission size gate is on the minified bytes, not source LOC).
pub fn plan_with_meta(state: &State, my: &[Troll], meta: Meta) -> Plan {
    plan_impl(state, my, meta)
}

}
// Flip to true for a SIM-FIDELITY validation run: echoes the full per-turn state
// to stderr (captured in the replay) so we can replay a real game through the sim
// and compare turn-by-turn. Off by default (no effect on play or stdout parity).
const DEBUG: bool = false;

// ── WOOD-RACE bot (v1.0) — beats the Silver Boss ~68% in the local sim ─────────
// Mirror of strategies::mybot (validated in the referee-faithful Rust sim). Strategy:
//   * GREEDY expansion to ~4 trolls (train the cheapest affordable troll each turn),
//     jumping the queue to build TWO fast (ms2,cc2,chop2) choppers as soon as afford-
//     able; the rest are speed harvesters. Mine iron to fund the choppers' chop cost.
//   * Choppers fell the best tree (close + big) with a DENIAL bias toward the foe's
//     shack -- felling starves the opponent's fruit while banking 4pt-each wood.
//   * Harvesters grab the NEAREST ripe fruit (max throughput) and seed a tiny base
//     plum orchard; everyone banks when full.
// The boss is a similar wood/denial bot; our edge is faster (ms2) choppers that win
// the race to contested trees + higher fruit throughput (nearest-ripe harvesting).
// Cheap pure chopper (ms1, cc2, hp0, chop2): swept best vs silver_boss at 87% (vs the
// old ms2 (2,2,1,2) at 81%). cc2 = 2 wood/fell is essential; dropping ms+hp saves plum
// +apple for a stronger economy while still winning the denial race (DW=3) + woodfarm.
// hp0 (was hp1): saves n+1 APPLE per chopper; the only loss is a rarely-reachable
// fruit-harvest fallback. Confirmed on BOTH boss models at 1000 seeds (2026-07-02):
// scriptboss 59.8→60.9% (margin +14.7→+18.2), silverboss 77.5→78.4% (+24.1→+26.9).
const MB_CHOPPER: (i32, i32, i32, i32) = (2, 3, 0, 3); // v1.12.0: cc3/chop3 SUPER-chopper (fell fast, bank every 3) — the nmahoude throughput lever
const MB_NCHOPPERS: i32 = 1; // ONE super-chopper; the other trolls are HARVESTERS that fund it + feed the farm
                             // chop1 harvesters (+n+1 iron each): every fruit troll can also FELL the base
                             // farm's young bananas (the "mower"). Blueprint from arena replays: 250-pt bots
                             // sustain 0.30 wood/turn vs our 0.07; fellers must live AT the farm, and the
                             // denial choppers can't. Both-model win at 1000 seeds: scriptboss 63.0->64.3%
                             // (margin +25.8->+31.6), silverboss 85.1->87.5% (+51.4->+54.1); wood 90->105.
const MB_HARVESTERS: [(i32, i32, i32, i32); 3] = [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)];
const MB_MAX_TROLLS: usize = 4;
const MB_MAX_ORCHARD: usize = 2;
const MB_MIN_TURNS_LEFT: i32 = 20;
// Denial-heavy chopper targeting (swept 2026-07-01 in the faithful sim): DW=3, WT=0
// lifts the bot from 67.6% -> 78.0% vs silver_boss. Our cheap fast choppers win the
// race to the BOSS's trees and starve its wood+fruit; biasing hard toward the enemy
// shack (and dropping the tree-size preference) is decisively better than balanced.
const MB_DENIAL_W: i32 = 0;
const MB_SIZE_W: i32 = 0;

thread_local! {
    // xorshift RNG for the watchdog sidestep — FIXED seed: fully deterministic
    // (sequence position is state-driven). Survivor of the RHEA machinery cut.
    static RH_RNG: RefCell<u64> = RefCell::new(0x9E3779B97F4A7C15);
}

fn rh_rand() -> u64 {
    RH_RNG.with(|rng| {
        let mut r = rng.borrow_mut();
        *r ^= *r << 13;
        *r ^= *r >> 7;
        *r ^= *r << 17;
        *r
    })
}

// (decide_sched, the RHEA fast engine + searcher, and the v1.0.x legacy deciders were
// REMOVED 2026-07-06 for the 100 KB submission cap — run() calls decide_elite only.
// Full history: git; frozen artifacts: cgauto/submissions/.)

// B1/B2: the meta selector consumed by tactics::phase_for. Tempo is the live meta
// (phase-inert: phase_for(Tempo, _) == Phase::Tempo always, so every phase-gated band in
// planner.rs/tactics.rs is a no-op) — Tempo is equality-proven byte-identical to the
// pre-phase champion. Scale (Hoard→Factory at T_SWITCH) now has real Hoard-phase behavior
// (fell suppression + denial exception + wallet band + training ladder) but is still not
// selected live. See rust/src/botmain/tactics.rs and planner.rs.
const GE_META: tactics::Meta = tactics::Meta::Tempo;
const GE_SPEC: (i32, i32, i32, i32) = (2, 3, 0, 2); // cc=3 chopper (Boss-5 mechanism: capture 3 wood/size-3 tree)
const GE_MAX_TROLLS: i32 = 2; // T-hand parked pending a better design; re-arm by setting 3
const GE_FEEDER_SPEC: (i32, i32, i32, i32) = (1, 1, 1, 0); // cheap hands: 3 plum/3 lemon/3 apple at n=2 (half the old feeder price)
const GE_FEEDER_T: i32 = 45; // T-hand: restored from 60 — 60 was a leftover from the v1.28.x farm-death era when GE_MAX_TROLLS=2 made this gate unreachable anyway (dormant 3rd hand); the funding fix (planner.rs ladder_funding) is what actually treats farm-death now, so the feeder can arm this early again
const GE_FEEDER_FARM: usize = 0; // T-hand.2: 1->0 — verdict-#2 catch-22: the hand rescues the dead farm; any farm precondition blocks the cure exactly when it's needed (fruit/iron wallets, need_fund/need_iron, are the real gates now). farm_now collapsed to literal 0 for 63-100% of sampled turns per game (8/8 boss games ended farm=0); one game had fruit+iron sufficient for 255 straight turns while farm sat at 0 the whole time and want_feeder still never became eligible under the old >=1 floor.
const GE_CHOP_DELAY: i32 = 0; // NO delay: train chopper early (denial > accumulation, proven 2026-07-05)
const GE_CHOP_FARM: usize = 3; // train as soon as affordable (early aggression, v1.4.5 regime)
const GE_FARM_R: i32 = 2; // v1.13.0: TIGHT farm hugging the shack — halves the chopper's bank-trip distance (the throughput bottleneck)
const GE_FARM_MAX: usize = 12; // v1.19.0: fill the radius-2 area (~12 cells) — more trees maturing in parallel = chopper idles less
const GE_FELL_SIZE: i32 = 2; // NATIVE/contested trees: fell at size 2 = DENIAL (grab before opponent)
const GE_CHOP_R: i32 = 5; // roam4 arena-REVERTED at -3.6 (2026-07-08); tree restored to champion semantics
const GE_LIQ_T: i32 = 34; // turns_rem <= this: fell anything reachable (A1 liq44 REJECTED by gatekeeper 2026-07-07)
const GE_STARTER_CHOP: bool = true; // let a chop-capable starter help fell
const GE_MIN_TURNS_LEFT: i32 = 20; // no training inside the last 20 turns
const GE_SEED_RESERVE: usize = 2; // protect K most-mature farm bananas as seed sources
const GE_FARM_FELL: i32 = 3; // OUR farm bananas: fell at size 3 = PRODUCTION (cc=3 captures all 3)
// v1.53.0-pressurefarm (Task 2 Step 1): under Yellow+ observed pressure, tactics::plan_impl
// clamps farm_cap down to this floor instead of GE_FARM_MAX — a small "keep some farm alive"
// bootstrap floor, not zero (an empty farm was the seedloop/fruitbank-era failure mode). A
// farm already below the floor keeps planting regardless of pressure (this is a CEILING that
// only ever shrinks room to expand further, never a mandate to shrink below where we are).
const GE_PRESSURE_FARM_FLOOR: usize = 4;

/// v1.4.0 live decider: the gold-elite pure-production strategy. The standalone
/// bot is always player 0 (my_trolls). A 1:1 port of GoldElite::decide with an
/// added turn-1 MSG and an anti-stall watchdog (below).
fn decide_elite(state: &State) -> Vec<String> {
    if state.turn == 1 {
        motion::reset();
        ownership::reset();
        tactics::reset();
        planner::reset();
    }
    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);

    // L1: tactical plan → L2: per-troll job assignment → L3: motion post-pass
    let plan = tactics::plan(state, &my);
    let mut cmd_by_id = planner::assign_resolved(state, &plan, &my);
    if DEBUG && state.turn % 5 == 0 {
        // v1.56.0-ringfarm: ring_n = ring cells this turn; ring_planted = ring cells hosting a
        // banana (the "bananas planted near the tent" the candidate gate measures by turn N).
        let ring_planted = plan
            .ring
            .iter()
            .filter(|(c, _)| {
                state
                    .trees
                    .iter()
                    .any(|p| p.pos() == *c && p.tree_type == "BANANA")
            })
            .count();
        eprintln!(
            "@TFFARM t={} farm={} seeds={} n={} flaps={} phase={:?} ring_n={} ring_planted={}",
            state.turn,
            plan.farm_now,
            state.my_inventory[BANANA],
            my.len(),
            planner::flaps(),
            plan.phase,
            plan.ring.len(),
            ring_planted
        );
    }
    if DEBUG {
        ownership::log(state, &plan);
        ownership::log_pressure(state, &plan);
    }

    // R6a/R6b feedback: planner::assign_resolved runs joint assignment, the first
    // motion solve, one bounded yield-to-urgent pass, and final MOVE landing pinning.
    // anti-stall watchdog (R3b: motion layer) — sidestep trolls self-blocked 2+ turns
    motion::watchdog(state, &my, &mut cmd_by_id);

    let mut actions: Vec<String> = Vec::new();
    if state.turn == 1 {
        actions.push(format!("MSG v{}", VERSION));
    }
    let mut ids: Vec<i32> = cmd_by_id.keys().copied().collect();
    ids.sort();
    for id in ids {
        actions.push(cmd_by_id[&id].clone());
    }

    if plan.train_now
        && TOTAL_TURNS - state.turn > GE_MIN_TURNS_LEFT
        && !my.iter().any(|u| u.pos() == plan.shack)
    {
        actions.push(format!(
            "TRAIN {} {} {} {}",
            plan.train_spec.0, plan.train_spec.1, plan.train_spec.2, plan.train_spec.3
        ));
    }

    if actions.is_empty() {
        actions.push("WAIT".into());
    }
    actions
}

// ── I/O parsing ───────────────────────────────────────────────────────────────

fn parse_grid(grid_lines: &[String]) -> (HashSet<Cell>, Cell, Cell, HashSet<Cell>, HashSet<Cell>) {
    let mut walkable = HashSet::new();
    let mut iron = HashSet::new();
    let mut water = HashSet::new();
    let mut my_shack = (0i32, 0i32);
    let mut opp_shack = (0i32, 0i32);
    for (y, line) in grid_lines.iter().enumerate() {
        for (x, ch) in line.chars().enumerate() {
            let cell = (x as i32, y as i32);
            match ch {
                '0' => my_shack = cell,
                '1' => opp_shack = cell,
                '.' => {
                    walkable.insert(cell);
                }
                '+' => {
                    iron.insert(cell);
                }
                '~' => {
                    water.insert(cell);
                }
                _ => {} // '#' and others are rocks
            }
        }
    }
    (walkable, my_shack, opp_shack, iron, water)
}

fn read_line(reader: &mut impl BufRead) -> Option<String> {
    let mut s = String::new();
    match reader.read_line(&mut s) {
        Ok(0) => None,
        Ok(_) => Some(s.trim_end_matches('\n').trim_end_matches('\r').to_string()),
        Err(_) => None,
    }
}

fn parse_turn(
    reader: &mut impl BufRead,
    walkable: &HashSet<Cell>,
    my_shack: Cell,
    opp_shack: Cell,
    turn: i32,
    iron_cells: &HashSet<Cell>,
    water_cells: &HashSet<Cell>,
) -> Option<State> {
    let inv0_line = read_line(reader)?;
    let my_inventory: Vec<i32> = inv0_line
        .split_whitespace()
        .map(|v| v.parse().unwrap())
        .collect();
    let inv1_line = read_line(reader)?;
    let opp_inventory: Vec<i32> = inv1_line
        .split_whitespace()
        .map(|v| v.parse().unwrap())
        .collect();

    let tree_count_line = read_line(reader)?;
    let tree_count: usize = tree_count_line.trim().parse().unwrap();
    let mut trees = Vec::with_capacity(tree_count);
    for _ in 0..tree_count {
        let line = read_line(reader)?;
        let parts: Vec<&str> = line.split_whitespace().collect();
        trees.push(Tree {
            tree_type: parts[0].to_string(),
            x: parts[1].parse().unwrap(),
            y: parts[2].parse().unwrap(),
            size: parts[3].parse().unwrap(),
            health: parts[4].parse().unwrap(),
            fruits: parts[5].parse().unwrap(),
            cooldown: parts[6].parse().unwrap(),
        });
    }

    let troll_count_line = read_line(reader)?;
    let troll_count: usize = troll_count_line.trim().parse().unwrap();
    let mut my_trolls = Vec::new();
    let mut opp_trolls = Vec::new();
    for _ in 0..troll_count {
        let line = read_line(reader)?;
        let f: Vec<i32> = line
            .split_whitespace()
            .map(|v| v.parse().unwrap())
            .collect();
        // id player x y ms cc hp chop carry[6]
        let troll = Troll {
            id: f[0],
            x: f[2],
            y: f[3],
            movement_speed: f[4],
            carry_capacity: f[5],
            harvest_power: f[6],
            chop_power: f[7],
            carry: [f[8], f[9], f[10], f[11], f[12], f[13]],
        };
        if f[1] == 0 {
            my_trolls.push(troll);
        } else {
            opp_trolls.push(troll);
        }
    }

    let my_inv: [i32; 6] = [
        my_inventory[0],
        my_inventory[1],
        my_inventory[2],
        my_inventory[3],
        my_inventory[4],
        my_inventory[5],
    ];
    let opp_inv: [i32; 6] = [
        opp_inventory[0],
        opp_inventory[1],
        opp_inventory[2],
        opp_inventory[3],
        opp_inventory[4],
        opp_inventory[5],
    ];

    Some(State {
        walkable: walkable.clone(),
        my_shack,
        opp_shack,
        my_inventory: my_inv,
        opp_inventory: opp_inv,
        trees,
        my_trolls,
        opp_trolls,
        turn,
        iron_cells: iron_cells.clone(),
        water_cells: water_cells.clone(),
    })
}

// ── main ──────────────────────────────────────────────────────────────────────

/// Echo per-turn state to stderr for sim validation (gated by DEBUG). At turn 1
/// it logs the map + full initial trees/trolls (to reconstruct the start); every
/// turn it logs a compact digest (both inventories + all troll positions) so a
/// captured game can be replayed through the sim and compared turn-by-turn.
fn debug_log(state: &State, grid: &[String], width: i32, height: i32) {
    if !DEBUG {
        return;
    }
    if state.turn == 1 {
        eprintln!("@TFMAP {} {}", width, height);
        for l in grid {
            eprintln!("@TFMAP {}", l.trim_end());
        }
        for t in &state.trees {
            eprintln!(
                "@TFI P {} {} {} {} {} {} {}",
                t.tree_type, t.x, t.y, t.size, t.health, t.fruits, t.cooldown
            );
        }
        for (pl, list) in [(0, &state.my_trolls), (1, &state.opp_trolls)] {
            for u in list {
                eprintln!(
                    "@TFI U {} {} {} {} {} {} {} {} {} {} {} {} {} {}",
                    u.id,
                    pl,
                    u.x,
                    u.y,
                    u.movement_speed,
                    u.carry_capacity,
                    u.harvest_power,
                    u.chop_power,
                    u.carry[0],
                    u.carry[1],
                    u.carry[2],
                    u.carry[3],
                    u.carry[4],
                    u.carry[5]
                );
            }
        }
    }
    let join = |a: &[i32; 6]| {
        a.iter()
            .map(|v| v.to_string())
            .collect::<Vec<_>>()
            .join(",")
    };
    let mut us = String::new();
    for u in &state.my_trolls {
        us.push_str(&format!("{},0,{},{};", u.id, u.x, u.y));
    }
    for u in &state.opp_trolls {
        us.push_str(&format!("{},1,{},{};", u.id, u.x, u.y));
    }
    eprintln!(
        "@TFD {} {} {} {}",
        state.turn,
        join(&state.my_inventory),
        join(&state.opp_inventory),
        us
    );

    // Compact per-turn SUMMARY (printed LAST so it's the console line that survives
    // truncation): both scores, tree count, and OPPONENT troll stats -- so we can read
    // the real Boss 4's composition (fruit vs wood) and troll build from one screenshot.
    let score = |inv: &[i32; 6]| inv[0] + inv[1] + inv[2] + inv[3] + 4 * inv[5];
    let opp_builds: Vec<String> = state
        .opp_trolls
        .iter()
        .map(|u| {
            format!(
                "{}:{}.{}.{}.{}",
                u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power
            )
        })
        .collect();
    let my_builds: Vec<String> = state
        .my_trolls
        .iter()
        .map(|u| {
            format!(
                "{}:{}.{}.{}.{}",
                u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power
            )
        })
        .collect();
    eprintln!(
        "@TFSUM t={} me={} opp={} trees={} myinv=[{}] oppinv=[{}] mybuilds={} oppbuilds={}",
        state.turn,
        score(&state.my_inventory),
        score(&state.opp_inventory),
        state.trees.len(),
        join(&state.my_inventory),
        join(&state.opp_inventory),
        my_builds.join(","),
        opp_builds.join(",")
    );
}

pub fn run() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut reader = io::BufReader::new(stdin.lock());
    let mut out = io::BufWriter::new(stdout.lock());

    // Read header: width height
    let header = match read_line(&mut reader) {
        Some(s) => s,
        None => return,
    };
    let mut hw = header.split_whitespace();
    let width: i32 = hw.next().unwrap().parse().unwrap();
    let height: i32 = hw.next().unwrap().parse().unwrap();

    let mut grid_lines = Vec::with_capacity(height as usize);
    for _ in 0..height {
        match read_line(&mut reader) {
            Some(line) => grid_lines.push(line),
            None => return,
        }
    }

    let (walkable, my_shack, opp_shack, iron_cells, water_cells) = parse_grid(&grid_lines);

    let mut turn = 0i32;
    loop {
        turn += 1;
        match parse_turn(
            &mut reader,
            &walkable,
            my_shack,
            opp_shack,
            turn,
            &iron_cells,
            &water_cells,
        ) {
            None => break,
            Some(state) => {
                debug_log(&state, &grid_lines, width, height);
                let cmds = decide_elite(&state);
                // @TFMOVE: motion-rule instrument (motion_analyze.py) — positions BEFORE
                // moving + intended MOVEs; block rate = intended-but-didn't-advance.
                if DEBUG {
                    let pos: Vec<String> = state
                        .my_trolls
                        .iter()
                        .map(|t| format!("{}@{},{}", t.id, t.x, t.y))
                        .collect();
                    let moves: Vec<String> = cmds
                        .iter()
                        .filter(|c| c.starts_with("MOVE "))
                        .cloned()
                        .collect();
                    eprintln!(
                        "@TFMOVE t={} pos=[{}] moves=[{}]",
                        state.turn,
                        pos.join(" "),
                        moves.join(" ")
                    );
                }
                writeln!(out, "{}", cmds.join(";")).unwrap();
                out.flush().unwrap();
            }
        }
    }
}


fn main() {
    run();
}
