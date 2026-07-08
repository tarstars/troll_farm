#![allow(dead_code, unused)]
// CodinGame Spring Challenge 2026 - Troll Farm bot (Rust port of Python v0.7.1)
// Single-file submission. stdlib only.

use std::collections::{HashMap, HashSet, VecDeque};
use std::io::{self, BufRead, Write};
use std::cell::RefCell;

// ── constants ───────────────────────────────────────────────────────────────

const VERSION: &str = "1.41.0-nopickloop"; // fix: no PICK without a reachable plant cell + scarce-camp parking (user-observed corridor livelock)
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
        (self.movement_speed, self.carry_capacity, self.harvest_power, self.chop_power)
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
        sx as u64, sy as u64, ox as u64, oy as u64,
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
        let camp_cells = ortho_neighbors(shack).iter().filter(|c| state.walkable.contains(*c)).count();
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
            let is_move = cmd_by_id.get(&t.id).map_or(false, |c| c.starts_with("MOVE "));
            let entry = m.entry(t.id).or_insert((cur.0, cur.1, 0u8));
            let stuck = entry.0 == cur.0 && entry.1 == cur.1;
            entry.2 = if stuck && is_move { entry.2.saturating_add(1) } else { 0 };
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
            .filter(|c| dp.get(*c).map_or(false, |&d| d > 0 && d <= t.movement_speed))
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
pub mod planner {
//! L2 JOINT TASK ASSIGNMENT (R6b) — the activity manager's task stage.
//!
//! The sequential cascade (jobs.rs) let troll-id order decide contested resources: the
//! first troll `reserved` its target, later trolls avoided it. Here every troll's viable
//! tasks are enumerated as (target, value) CANDIDATES — the cascade's branch hierarchy
//! becomes value BANDS (spaced wider than any ETA, so each troll still prefers its higher
//! branch), ETA differentiates within a band — and the assignment is chosen JOINTLY:
//! exhaustive over per-troll top-K, maximizing total value, same-target conflicts
//! forbidden, canonical tie-break. SHUFFLE INVARIANCE: the plan depends on the objective,
//! never on troll/candidate iteration order.
use super::tactics::{Phase, Plan};
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
const RACE_SHARE_PEN: i64 = 4; // sweep 2->4 per analyst; harder discount on joinable contests

#[derive(Clone, Debug, PartialEq)]
enum Kind {
    Bank,       // render via motion::bank_cmd (DROP if adjacent, else camp-cell MOVE)
    Park,       // render via motion::park_cmd (target None = idle band-10, ring-2-aware;
                // target Some(shack) = band-49 park-to-pick errand, direct camp approach)
    ChopHere,   // CHOP at current cell
    MoveTo,     // MOVE toward target (fell/fund/seed/mine-adjacent/plant travel)
    PlantHere,  // PLANT BANANA at current cell
    Harvest,    // HARVEST at current cell
    Mine,       // MINE (adjacent to iron)
    Pick,       // PICK BANANA (shack-adjacent)
}

#[derive(Clone, Debug)]
struct Cand {
    kind: Kind,
    target: Option<Cell>, // claimed resource (tree/plant/iron-adj cell); None = un-contested
    value: i64,
}

fn eta(d: &HashMap<Cell, i32>, c: Cell, ms: i32) -> i64 {
    let dist = d.get(&c).copied().unwrap_or(1 << 20);
    ((dist + ms - 1) / ms.max(1)) as i64
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
        enemy_d.as_ref().map_or(false, |ed| ed.get(&pc).map_or(false, |&dd| dd <= 2))
    };

    let fell_ok = |p: &Tree| -> bool {
        if plan.seed_cells.contains(&p.pos()) {
            return false;
        }
        if plan.liquidation {
            return p.size >= 1;
        }
        let farm_banana = p.tree_type == "BANANA" && plan.farm_d.get(&p.pos()).map_or(false, |&fd| fd <= plan.farm_r);
        p.size >= if farm_banana { plan.farm_fell } else { plan.fell_size }
    };
    let own_half =
        |p: &Tree| plan.liquidation || manhattan(p.pos(), shack) <= manhattan(p.pos(), plan.opp);
    let within_roam = |p: &Tree| plan.liquidation || plan.farm_d.get(&p.pos()).map_or(false, |&fd| fd <= plan.chop_r);

    // v1.36.0-race (user replay finding): a tree an enemy is already chopping is a RACE.
    // If they fell it before we arrive, walking there donates the travel (skip). If we can
    // arrive in time, the wood SPLITS round-robin among cell-sharers (engine apply_chop) —
    // join, but discount the value by the shared payoff. Pure function of `state` (no
    // per-troll mutable state), so shuffle invariance holds; called once per candidate,
    // covers every fell-type push (bands 72/70, 42/40, 31/30) via this one helper.
    let race = |pc: Cell, our_eta: i64| -> Option<i64> {
        // returns None = doomed (skip candidate); Some(penalty) = value adjustment
        let occupant = state.opp_trolls.iter().find(|e| e.pos() == pc && e.chop_power > 0);
        match occupant {
            None => Some(0),
            Some(e) => {
                let h = state.trees.iter().find(|p| p.pos() == pc).map(|p| p.health).unwrap_or(0) as i64;
                let their_turns = (h + e.chop_power as i64 - 1) / e.chop_power.max(1) as i64;
                if their_turns <= our_eta {
                    None // they finish first: doomed
                } else {
                    Some(RACE_SHARE_PEN) // joinable: shared wood, mild discount
                }
            }
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
    let plant_cell: Option<Cell> = if plan.base_trees < plan.farm_cap {
        state
            .walkable
            .iter()
            .filter(|c| plan.farm_d.get(*c).map_or(false, |&fd| fd <= plan.farm_r) && d.contains_key(*c))
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
            out.push(Cand { kind: Kind::Bank, target: None, value: 95 * BAND - e });
        }
    }
    // full -> bank (band 80) — reviewer MINOR fix: was `plan.base_trees < plan.farm_cap` (a
    // tree COUNT), now `plant_cell.is_some()` (an actual reachable free CELL), matching the
    // gate bands 88/50/49 already use. A carried banana with no plantable cell should be
    // banked, not held waiting for room that will never materialize.
    if u.free_capacity() == 0 && !(!is_chopper && u.carry[BANANA] > 0 && plant_cell.is_some())
    {
        out.push(Cand { kind: Kind::Bank, target: None, value: 80 * BAND });
    }

    if is_chopper {
        // fell targets (band 70): standing (CHOP now) or travel; value differentiates by
        // steps + chop-time exactly like the cascade's nearest_fell metric.
        for p in state.trees.iter().filter(|p| fell_ok(p) && own_half(p) && within_roam(p)) {
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
            if pc == u.pos() {
                // standing on a fellable tree: FINISH IT (cascade branch order) — band 72
                // outranks every travel-fell so invested chops are never abandoned.
                out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 72 * BAND - chop_t - race_pen - deny_pen });
            } else {
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 70 * BAND - (steps + chop_t) - race_pen - deny_pen });
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
                out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 31 * BAND - chop_t - race_pen });
            } else {
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 30 * BAND - (steps + chop_t) - race_pen });
            }
        }
        // partial bank / park (band 10)
        out.push(Cand {
            kind: if u.total_carried() > 0 { Kind::Bank } else { Kind::Park },
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
                let kind = if u.pos() == tc { Kind::PlantHere } else { Kind::MoveTo };
                out.push(Cand { kind, target: Some(tc), value: 88 * BAND - eta(&d, tc, ms) });
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
                                && state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1))))
                    || plan.phase == Phase::Hoard; // Hoard wants EVERYTHING ripe standing under foot too
                if want {
                    out.push(Cand { kind: Kind::Harvest, target: Some(u.pos()), value: 75 * BAND });
                }
            }
        }
        // B2 (Hoard): wallet-building — travel to ANY ripe fruit tree. Fruit is points AND
        // wallet fuel during Hoard, so there is no per-type targeting like the funding/printer
        // bands below (those stay as-is; the matcher just takes the max of every band pushed).
        if plan.phase == Phase::Hoard {
            for p in state.trees.iter().filter(|p| p.fruits > 0 && d.contains_key(&p.pos())) {
                let pc = p.pos();
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 62 * BAND - eta(&d, pc, ms) });
            }
        }
        // 4) FUNDING (bands 60/58) — for the chopper OR a pending 3rd hand (R6b.2: the old
        // feeder never trained because post-funding nobody harvested plum/lemon/apple)
        if plan.want_chopper || plan.want_feeder {
            // v1.28.1: the chopper is EXISTENTIAL (60/58) but a 3rd hand is a LUXURY — its
            // funding (45/44) must never displace printer/seed work (50/48). The v1.28.0
            // regression: perpetual feeder-funding starved the farm on lemon-poor maps.
            let (fund_hi, fund_lo) = if plan.want_chopper { (60, 58) } else { (45, 44) };
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
                if state.iron_cells.iter().any(|ic| manhattan(u.pos(), *ic) == 1) {
                    let v = if ladder_funding { 65 } else { fund_hi };
                    out.push(Cand { kind: Kind::Mine, target: Some(u.pos()), value: v * BAND });
                } else if let Some(c) = state
                    .iron_cells
                    .iter()
                    .flat_map(|ic| ortho_neighbors(*ic))
                    .filter(|c| d.contains_key(c))
                    .min_by_key(|c| (d[c], tie_mix(*c, salt)))
                {
                    let v = if ladder_funding { 64 } else { fund_hi };
                    out.push(Cand { kind: Kind::MoveTo, target: Some(c), value: v * BAND - eta(&d, c, ms) });
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
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: fruit_band * BAND - eta(&d, pc, ms) });
            }
        }
        // 5) PRINTER (bands 52/50/49) — v1.37.0-nanaflow (user replay finding #2): TREE-FIRST.
        // Harvesting a ripe seed tree directly converts its fruit straight into a farm seed;
        // banked tent stock is just as harvestable a turn later. So a ripe seed tree now
        // outranks the tent unconditionally (band 52, the old `inv[BANANA] == 0` gate is
        // REMOVED — harvested even with tent stock on hand). PICK/park (50/49, unchanged) is
        // the fallback once no ripe seed tree is reachable; excess bananas accumulate in the
        // tent via the existing full->bank flow (1pt banked each, or 8pt later via plant->fell).
        if plan.base_trees < plan.farm_cap {
            for p in state.trees.iter().filter(|p| {
                p.fruits > 0
                    && d.contains_key(&p.pos())
                    && (p.tree_type == "BANANA"
                        || (p.tree_type == "APPLE"
                            && state.water_cells.iter().any(|w| manhattan(*w, p.pos()) == 1)))
            }) {
                let pc = p.pos();
                out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 52 * BAND - eta(&d, pc, ms) });
            }
            // v1.41.0-nopickloop: only PICK (or travel to pick) if a plantable cell
            // actually exists (plant_cell.is_some()) — picking a banana with nowhere to
            // plant it is pure waste that just re-parks the starter on a scarce cell.
            if inv[BANANA] > 0 && u.free_capacity() > 0 && plant_cell.is_some() {
                // target = shack: dedupes the pick errand across multiple hands (R6b.2)
                if manhattan(u.pos(), shack) == 1 {
                    out.push(Cand { kind: Kind::Pick, target: Some(shack), value: 50 * BAND });
                } else {
                    out.push(Cand { kind: Kind::Park, target: Some(shack), value: 50 * BAND - 1 });
                }
            }
        }
        // 6) chop help (band 40) + anti-starvation (band 30)
        if plan.starter_chop && u.chop_power > 0 {
            for p in state.trees.iter().filter(|p| fell_ok(p) && own_half(p) && within_roam(p)) {
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
                if pc == u.pos() {
                    out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 42 * BAND - chop_t - race_pen });
                } else {
                    out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 40 * BAND - (steps + chop_t) - race_pen });
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
                    let chop_t = ((p.health + u.chop_power.max(1) - 1) / u.chop_power.max(1)) as i64;
                    let race_pen = match race(pc, steps) {
                        None => continue, // doomed: they fell it before we arrive — skip, don't donate the travel
                        Some(pen) => pen,
                    };
                    if pc == u.pos() {
                        out.push(Cand { kind: Kind::ChopHere, target: Some(pc), value: 31 * BAND - chop_t - race_pen });
                    } else {
                        out.push(Cand { kind: Kind::MoveTo, target: Some(pc), value: 30 * BAND - (steps + chop_t) - race_pen });
                    }
                }
            }
        }
        // fallback (band 10)
        out.push(Cand {
            kind: if u.total_carried() > 0 { Kind::Bank } else { Kind::Park },
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

/// Joint assignment: exhaustive over per-troll top-K candidates, maximize total value,
/// same-target conflicts forbidden, ties broken by the lexicographic pick vector.
pub fn assign(state: &State, plan: &Plan, my: &[Troll]) -> HashMap<i32, String> {
    let salt = tie_salt(state);
    let mut ids: Vec<i32> = my.iter().map(|t| t.id).collect();
    ids.sort();
    let trolls: Vec<&Troll> = ids.iter().map(|id| my.iter().find(|t| t.id == *id).unwrap()).collect();
    let cands: Vec<Vec<Cand>> = trolls.iter().map(|t| candidates(state, plan, my, t, salt)).collect();

    let n = ids.len();
    let mut best: Option<(i64, Vec<usize>)> = None;
    let mut pick = vec![0usize; n];
    if n > 0 {
        loop {
            let mut targets: Vec<Cell> = Vec::new();
            let mut ok = true;
            for i in 0..n {
                if let Some(t) = cands[i][pick[i]].target {
                    if targets.contains(&t) {
                        ok = false;
                        break;
                    }
                    targets.push(t);
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

    // render (troll-id order; camp-cell claiming stays deterministic via claimed_drop)
    let mut cmd_by_id: HashMap<i32, String> = HashMap::new();
    let mut claimed_drop: HashSet<Cell> = HashSet::new();
    if let Some((_, picks)) = best {
        for (i, id) in ids.iter().enumerate() {
            let u = trolls[i];
            let d = bfs_distances(&state.walkable, &[u.pos()]);
            let c = &cands[i][picks[i]];
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
            let cmd = match (&c.kind, c.target) {
                (Kind::Bank, _) => motion::bank_cmd(state, plan.shack, u, &d, &mut claimed_drop),
                // idle band-10 (target None) gets the ring-2-aware scarce-camp step-back;
                // the band-49 park-to-pick ERRAND (target Some(shack)) never does — it is
                // goal-directed (must reach manhattan==1 to unlock PICK) and the ring-2
                // redirect has no such convergence guarantee (reviewer CRITICAL fix, see
                // motion::park_cmd's doc comment).
                (Kind::Park, park_target) => {
                    motion::park_cmd(state, plan.shack, u, &d, &mut claimed_drop, park_target.is_none())
                }
                (Kind::ChopHere, _) => format!("CHOP {}", u.id),
                (Kind::PlantHere, _) => format!("PLANT {} BANANA", u.id),
                (Kind::Harvest, _) => format!("HARVEST {}", u.id),
                (Kind::Mine, _) => format!("MINE {}", u.id),
                (Kind::Pick, _) => format!("PICK {} BANANA", u.id),
                (Kind::MoveTo, Some(tc)) => format!("MOVE {} {} {}", u.id, tc.0, tc.1),
                (Kind::MoveTo, None) => format!("MOVE {} {} {}", u.id, plan.shack.0, plan.shack.1),
            };
            cmd_by_id.insert(*id, cmd);
        }
    }
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
use std::collections::HashSet;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Meta { Tempo, Scale }

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Phase { Tempo, Hoard, Factory }

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
            if turn < T_SWITCH { Phase::Hoard } else { Phase::Factory }
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
}

fn plan_impl(state: &State, my: &[Troll], meta: Meta) -> Plan {
    let farm_d = bfs_distances(&state.walkable, &[state.my_shack]);
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
        .filter(|p| farm_d.get(&p.pos()).map_or(false, |&d| d <= GE_FARM_R))
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
        (want_chopper, want_feeder, train_spec, cost, train_now, need_iron, need_fund)
    } else {
        let want_chopper =
            nchop == 0 && (state.turn >= GE_CHOP_DELAY || farm_now >= GE_CHOP_FARM);
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
        (want_chopper, want_feeder, train_spec, cost, train_now, need_iron, need_fund)
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
    let farm_cap = if phase == Phase::Factory { 20 } else if econ_b { 20 } else { GE_FARM_MAX };
    let fell_size = GE_FELL_SIZE; // NATIVE/contested trees: always size-2 = DENIAL
    let farm_fell = if econ_b { 3 } else { 2 }; // OUR farm bananas: size-3 in econ B, size-2 in A
    let chop_r = if econ_b { 10 } else { GE_CHOP_R }; // econ B roams a bigger farm; A stays tight
    let starter_chop = GE_STARTER_CHOP;
    let liquidation = turns_rem <= GE_LIQ_T;
    let base_trees = state.trees.iter().filter(|p| farm_d.get(&p.pos()).map_or(false, |&d| d <= farm_r)).count();

    // ── SEED SUSTAINABILITY (arena deforestation fix) ───────────────────────
    // Trees only fruit at MAX_SIZE(4); felling farm bananas at size 2 means they
    // NEVER fruit, so the seed supply drains -> the farm dies -> our half
    // deforests -> both trolls park (the decoded arena stall). Fix: keep the K
    // most-mature farm bananas as a permanent seed reserve the chopper won't
    // fell — they ripen, fruit, and the starter harvests their fruit for seeds.
    let mut seed_cells: HashSet<Cell> = HashSet::new();
    if GE_SEED_RESERVE > 0 && !liquidation {
        let mut fb: Vec<&Tree> = state
            .trees
            .iter()
            .filter(|p| p.tree_type == "BANANA" && farm_d.get(&p.pos()).map_or(false, |&d| d <= farm_r))
            .collect();
        fb.sort_by_key(|p| (-p.size, -p.fruits, manhattan(p.pos(), shack), p.pos()));
        for p in fb.into_iter().take(GE_SEED_RESERVE) {
            seed_cells.insert(p.pos());
        }
    }

    Plan {
        shack, farm_d, opp, have_iron, turns_rem, n, farm_now, nchop, spec, want_chopper,
        want_feeder, train_spec, cost, train_now, need_iron, need_fund, farm_r, farm_cap,
        fell_size, farm_fell, chop_r, starter_chop, liquidation, base_trees, seed_cells,
        phase,
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
const GE_MAX_TROLLS: i32 = 2; // T-hand parked pending its arena verdict; re-arm by setting 3
const GE_FEEDER_SPEC: (i32, i32, i32, i32) = (1, 1, 1, 0); // cheap hands: 3 plum/3 lemon/3 apple at n=2 (half the old feeder price)
const GE_FEEDER_T: i32 = 45; // T-hand: restored from 60 — 60 was a leftover from the v1.28.x farm-death era when GE_MAX_TROLLS=2 made this gate unreachable anyway (dormant 3rd hand); the funding fix (planner.rs ladder_funding) is what actually treats farm-death now, so the feeder can arm this early again
const GE_FEEDER_FARM: usize = 0; // T-hand.2: 1->0 — verdict-#2 catch-22: the hand rescues the dead farm; any farm precondition blocks the cure exactly when it's needed (fruit/iron wallets, need_fund/need_iron, are the real gates now). farm_now collapsed to literal 0 for 63-100% of sampled turns per game (8/8 boss games ended farm=0); one game had fruit+iron sufficient for 255 straight turns while farm sat at 0 the whole time and want_feeder still never became eligible under the old >=1 floor.
const GE_CHOP_DELAY: i32 = 0; // NO delay: train chopper early (denial > accumulation, proven 2026-07-05)
const GE_CHOP_FARM: usize = 3; // train as soon as affordable (early aggression, v1.4.5 regime)
const GE_FARM_R: i32 = 2; // v1.13.0: TIGHT farm hugging the shack — halves the chopper's bank-trip distance (the throughput bottleneck)
const GE_FARM_MAX: usize = 12; // v1.19.0: fill the radius-2 area (~12 cells) — more trees maturing in parallel = chopper idles less
const GE_FELL_SIZE: i32 = 2; // NATIVE/contested trees: fell at size 2 = DENIAL (grab before opponent)
const GE_CHOP_R: i32 = 4; // roam retest on the planner (travel-cut; cascade-era noise verdict doesn't transfer; analyst b62c977 queue #2)
const GE_LIQ_T: i32 = 34; // turns_rem <= this: fell anything reachable (A1 liq44 REJECTED by gatekeeper 2026-07-07)
const GE_STARTER_CHOP: bool = true; // let a chop-capable starter help fell
const GE_MIN_TURNS_LEFT: i32 = 20; // no training inside the last 20 turns
const GE_SEED_RESERVE: usize = 2; // protect K most-mature farm bananas as seed sources
const GE_FARM_FELL: i32 = 3; // OUR farm bananas: fell at size 3 = PRODUCTION (cc=3 captures all 3)



/// v1.4.0 live decider: the gold-elite pure-production strategy. The standalone
/// bot is always player 0 (my_trolls). A 1:1 port of GoldElite::decide with an
/// added turn-1 MSG and an anti-stall watchdog (below).
fn decide_elite(state: &State) -> Vec<String> {
    if state.turn == 1 {
        motion::reset();
        tactics::reset();
        planner::reset();
    }
    let mut my: Vec<Troll> = state.my_trolls.clone();
    my.sort_by_key(|t| t.id);

    // L1: tactical plan → L2: per-troll job assignment → L3: motion post-pass
    let plan = tactics::plan(state, &my);
    let mut cmd_by_id = planner::assign(state, &plan, &my);
    if DEBUG && state.turn % 5 == 0 {
        eprintln!(
            "@TFFARM t={} farm={} seeds={} n={} flaps={} phase={:?}",
            state.turn, plan.farm_now, state.my_inventory[BANANA], my.len(), planner::flaps(), plan.phase
        );
    }

    // R6a: JOINT MOVE RESOLUTION — the manager's motion stage. Collect every MOVE's goal,
    // choose all landing cells together (max total progress; swaps/chains exploited;
    // stationary teammates hard obstacles), and pin each MOVE to its landing cell. When
    // the joint optimum keeps a troll in place, the original MOVE is left as issued (the
    // engine blocks it harmlessly; the watchdog below still guards real stalls).
    let intents: Vec<(i32, Cell)> = cmd_by_id
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
    let landing = motion::solve_moves(state, &my, &intents);
    for (id, cell) in landing {
        let cur = my.iter().find(|t| t.id == id).map(|t| t.pos());
        if cur != Some(cell) {
            cmd_by_id.insert(id, format!("MOVE {} {} {}", id, cell.0, cell.1));
        }
    }
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
        actions.push(format!("TRAIN {} {} {} {}", plan.train_spec.0, plan.train_spec.1, plan.train_spec.2, plan.train_spec.3));
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
                '.' => { walkable.insert(cell); }
                '+' => { iron.insert(cell); }
                '~' => { water.insert(cell); }
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
    let my_inventory: Vec<i32> = inv0_line.split_whitespace()
        .map(|v| v.parse().unwrap())
        .collect();
    let inv1_line = read_line(reader)?;
    let opp_inventory: Vec<i32> = inv1_line.split_whitespace()
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
        let f: Vec<i32> = line.split_whitespace()
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

    let my_inv: [i32; 6] = [my_inventory[0], my_inventory[1], my_inventory[2],
                            my_inventory[3], my_inventory[4], my_inventory[5]];
    let opp_inv: [i32; 6] = [opp_inventory[0], opp_inventory[1], opp_inventory[2],
                             opp_inventory[3], opp_inventory[4], opp_inventory[5]];

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
                    u.id, pl, u.x, u.y, u.movement_speed, u.carry_capacity,
                    u.harvest_power, u.chop_power, u.carry[0], u.carry[1],
                    u.carry[2], u.carry[3], u.carry[4], u.carry[5]
                );
            }
        }
    }
    let join = |a: &[i32; 6]| a.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(",");
    let mut us = String::new();
    for u in &state.my_trolls {
        us.push_str(&format!("{},0,{},{};", u.id, u.x, u.y));
    }
    for u in &state.opp_trolls {
        us.push_str(&format!("{},1,{},{};", u.id, u.x, u.y));
    }
    eprintln!("@TFD {} {} {} {}", state.turn, join(&state.my_inventory), join(&state.opp_inventory), us);

    // Compact per-turn SUMMARY (printed LAST so it's the console line that survives
    // truncation): both scores, tree count, and OPPONENT troll stats -- so we can read
    // the real Boss 4's composition (fruit vs wood) and troll build from one screenshot.
    let score = |inv: &[i32; 6]| inv[0] + inv[1] + inv[2] + inv[3] + 4 * inv[5];
    let opp_builds: Vec<String> = state
        .opp_trolls
        .iter()
        .map(|u| format!("{}:{}.{}.{}.{}", u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power))
        .collect();
    let my_builds: Vec<String> = state
        .my_trolls
        .iter()
        .map(|u| format!("{}:{}.{}.{}.{}", u.id, u.movement_speed, u.carry_capacity, u.harvest_power, u.chop_power))
        .collect();
    eprintln!(
        "@TFSUM t={} me={} opp={} trees={} myinv=[{}] oppinv=[{}] mybuilds={} oppbuilds={}",
        state.turn, score(&state.my_inventory), score(&state.opp_inventory), state.trees.len(),
        join(&state.my_inventory), join(&state.opp_inventory),
        my_builds.join(","), opp_builds.join(",")
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
        match parse_turn(&mut reader, &walkable, my_shack, opp_shack, turn, &iron_cells, &water_cells) {
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
                    let moves: Vec<String> =
                        cmds.iter().filter(|c| c.starts_with("MOVE ")).cloned().collect();
                    eprintln!("@TFMOVE t={} pos=[{}] moves=[{}]", state.turn, pos.join(" "), moves.join(" "));
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
