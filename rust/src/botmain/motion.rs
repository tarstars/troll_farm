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

/// MOVE toward a claimed camp cell (idle parking).
pub fn park_cmd(
    state: &State,
    shack: Cell,
    u: &Troll,
    d: &HashMap<Cell, i32>,
    claimed: &mut HashSet<Cell>,
) -> String {
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
