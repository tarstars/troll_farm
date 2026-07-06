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
