//! SEARCH-based bot: greedy-1-ply with short forward rollouts.
//!
//! Each turn we enumerate a modest set of macro CANDIDATES — a (train decision,
//! role assignment) pair — then simulate each K turns forward with the REAL
//! engine `step()` (our validated forward model), running a fixed greedy
//! continuation policy for us and a greedy-chopper model for the opponent. We
//! score the terminal GameState (banked score + discounted carry + troll count)
//! and emit the first move of the best candidate.
//!
//! The forward model IS the engine, so the rollout is mechanically faithful; the
//! only approximations are (a) the opponent model and (b) our own continuation
//! policy for turns 1..K. Tunables are exposed via env vars for sweeps.
use std::collections::HashSet;

use super::Strategy;
use crate::game::engine::{step, training_cost, IRON, WOOD};
use crate::game::state::{Cell, GameState, Unit};

pub struct SearchBot;

// ── tunables (env, with defaults) ────────────────────────────────────────────
fn envi(name: &str, default: i32) -> i32 {
    std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(default)
}
fn envf(name: &str, default: f64) -> f64 {
    std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(default)
}

fn dist(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

/// A macro plan for one player: how many dedicated choppers, and whether the
/// remaining chop-capable trolls should mine iron (to fund the next chopper).
#[derive(Clone, Copy, Debug)]
struct Plan {
    choppers: i32,
    mine: bool,
}

// ── low-level command helpers ────────────────────────────────────────────────

fn bank(id: i32, pos: Cell, shack: Cell) -> String {
    if dist(pos, shack) == 1 {
        format!("DROP {}", id)
    } else {
        format!("MOVE {} {} {}", id, shack.0, shack.1)
    }
}

/// Walkable cell adjacent to the nearest iron deposit (where a troll must stand
/// to MINE), closest to `from`. None if no iron / no adjacent walkable cell.
fn nearest_iron_stand(game: &GameState, from: Cell, reserved: &HashSet<Cell>) -> Option<Cell> {
    let mut best: Option<(i32, Cell)> = None;
    for &(ix, iy) in &game.iron {
        for (dx, dy) in [(0, 1), (1, 0), (0, -1), (-1, 0)] {
            let c = (ix + dx, iy + dy);
            if !game.walkable.contains(&c) || reserved.contains(&c) {
                continue;
            }
            let d = dist(from, c);
            if best.map_or(true, |(bd, _)| d < bd) {
                best = Some((d, c));
            }
        }
    }
    best.map(|(_, c)| c)
}

/// Nearest tree (any) to `from`, skipping reserved cells. Tie-break: bigger size
/// first (more wood), then lexicographic.
fn nearest_tree(game: &GameState, from: Cell, reserved: &HashSet<Cell>) -> Option<Cell> {
    game.plants
        .iter()
        .filter(|p| !reserved.contains(&p.pos()))
        .min_by_key(|p| (dist(from, p.pos()), -p.size, p.x, p.y))
        .map(|p| p.pos())
}

/// Nearest FRUITED tree to `from`, skipping reserved.
fn nearest_fruited(game: &GameState, from: Cell, reserved: &HashSet<Cell>) -> Option<Cell> {
    game.plants
        .iter()
        .filter(|p| p.fruits > 0 && !reserved.contains(&p.pos()))
        .min_by_key(|p| (dist(from, p.pos()), p.x, p.y))
        .map(|p| p.pos())
}

// ── the greedy micro-policy that realises a Plan ─────────────────────────────

/// Produce this turn's commands for `player` given a role `plan` and an optional
/// TRAIN to attempt. Deterministic; used for both turn-0 emission and rollout.
fn plan_cmds(game: &GameState, player: usize, plan: Plan, train: Option<(i32, i32, i32, i32)>) -> Vec<String> {
    let shack = game.shacks[player];
    let mut mine: Vec<&Unit> = game.units.iter().filter(|u| u.player as usize == player).collect();
    mine.sort_by_key(|u| u.id);

    // Designate the `plan.choppers` strongest choppers (chop>=1) as fellers.
    let mut chop_capable: Vec<i32> = mine.iter().filter(|u| u.chop >= 1).map(|u| u.id).collect();
    chop_capable.sort_by_key(|&id| {
        let u = mine.iter().find(|u| u.id == id).unwrap();
        (-u.chop, id) // strongest chop first, then lowest id
    });
    let chopper_ids: HashSet<i32> = chop_capable.iter().take(plan.choppers as usize).copied().collect();

    let mut cmds = Vec::new();
    let mut reserved: HashSet<Cell> = HashSet::new();

    for u in &mine {
        let is_chopper = chopper_ids.contains(&u.id);

        // Full -> bank.
        if u.total() >= u.cc {
            cmds.push(bank(u.id, u.pos(), shack));
            continue;
        }

        // Standing on a plant -> act on it.
        if let Some(p) = game.plants.iter().find(|p| p.pos() == u.pos()) {
            if is_chopper && u.chop > 0 && u.free() > 0 {
                cmds.push(format!("CHOP {}", u.id));
                reserved.insert(u.pos());
                continue;
            }
            if !is_chopper && u.free() > 0 && p.fruits > 0 {
                cmds.push(format!("HARVEST {}", u.id));
                reserved.insert(u.pos());
                continue;
            }
        }

        // Chopper -> head to nearest tree and fell it.
        if is_chopper {
            if let Some(tp) = nearest_tree(game, u.pos(), &reserved) {
                reserved.insert(tp);
                cmds.push(if u.pos() == tp {
                    format!("CHOP {}", u.id)
                } else {
                    format!("MOVE {} {} {}", u.id, tp.0, tp.1)
                });
                continue;
            }
        }

        // Miner: a chop-capable non-chopper that mines to fund training.
        if plan.mine && u.chop >= 1 && !is_chopper && u.free() > 0 && !game.iron.is_empty() {
            // Already adjacent to iron -> MINE.
            let adj_iron = game
                .iron
                .iter()
                .any(|(ix, iy)| (u.x - ix).abs() + (u.y - iy).abs() == 1);
            if adj_iron {
                cmds.push(format!("MINE {}", u.id));
                continue;
            }
            if let Some(stand) = nearest_iron_stand(game, u.pos(), &reserved) {
                reserved.insert(stand);
                cmds.push(format!("MOVE {} {} {}", u.id, stand.0, stand.1));
                continue;
            }
        }

        // Harvester (default): nearest fruited tree.
        if let Some(tp) = nearest_fruited(game, u.pos(), &reserved) {
            reserved.insert(tp);
            cmds.push(if u.pos() == tp {
                format!("HARVEST {}", u.id)
            } else {
                format!("MOVE {} {} {}", u.id, tp.0, tp.1)
            });
            continue;
        }

        // Nothing to do: bank whatever we carry.
        if u.total() > 0 {
            cmds.push(bank(u.id, u.pos(), shack));
        }
    }

    // Train (only if the shack is clear so the command isn't wasted).
    if let Some(spec) = train {
        let occupied = mine.iter().any(|u| u.pos() == shack);
        if !occupied && affordable(game, player, spec) {
            cmds.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }
    }

    cmds
}

fn affordable(game: &GameState, player: usize, spec: (i32, i32, i32, i32)) -> bool {
    let n = game.units.iter().filter(|u| u.player as usize == player).count() as i32;
    let cost = training_cost(n, spec);
    let inv = &game.inventories[player];
    let pay: &[usize] = if !game.iron.is_empty() { &[0, 1, 2, 4] } else { &[0, 1, 2] };
    pay.iter().all(|&i| inv[i] >= cost[i])
}

fn max_chop(game: &GameState, player: usize) -> i32 {
    game.units.iter().filter(|u| u.player as usize == player).map(|u| u.chop).max().unwrap_or(0)
}

// ── default continuation TRAIN policy (used for rollout turns 1..K) ──────────

/// A reasonable "save for one strong chopper, then feed harvesters" build order,
/// used to continue rollouts. NOT the thing we search over (that's the turn-0
/// candidate); this just makes the rollout's future realistic.
fn auto_train(game: &GameState, player: usize) -> Option<(i32, i32, i32, i32)> {
    let n = game.units.iter().filter(|u| u.player as usize == player).count() as i32;
    let max_trolls = envi("SB_MAX_TROLLS", 5);
    if n >= max_trolls {
        return None;
    }
    // Near the end there's no time to recoup a training investment.
    if game.turn > envi("SB_TRAIN_CUTOFF", 280) {
        return None;
    }
    let strong = max_chop(game, player) >= 2;
    let has_iron = !game.iron.is_empty();
    let chopper: (i32, i32, i32, i32) = if has_iron { (2, 4, 2, 2) } else { (2, 4, 2, 0) };

    if n < 2 {
        // Get a second body cheaply.
        for spec in [(1, 2, 1, 0), (1, 1, 1, 0)] {
            if affordable(game, player, spec) {
                return Some(spec);
            }
        }
        return None;
    }
    if !strong {
        // SAVE for the one big chopper: only train it (don't dilute).
        if affordable(game, player, chopper) {
            return Some(chopper);
        }
        return None;
    }
    // Have a strong chopper: add economy harvesters.
    for spec in [(1, 3, 2, 0), (1, 2, 2, 0), (1, 2, 1, 0)] {
        if affordable(game, player, spec) {
            return Some(spec);
        }
    }
    None
}

// ── terminal evaluation ──────────────────────────────────────────────────────

fn carried_value(game: &GameState, player: usize) -> f64 {
    let iron_w = envf("SB_IRON_W", 1.0);
    let mut v = 0.0;
    for u in game.units.iter().filter(|u| u.player as usize == player) {
        // fruits (plum/lemon/apple/banana) are worth 1 pt each banked; wood 4.
        v += (u.carry[0] + u.carry[1] + u.carry[2] + u.carry[3]) as f64;
        v += 4.0 * u.carry[WOOD] as f64;
        v += iron_w * u.carry[IRON] as f64;
    }
    v
}

/// Long-term "economic potential" of a player's trolls. Training SPENDS banked
/// fruit (which is score), so a naive score-only eval treats training as pure
/// loss and the bot never expands. We credit each troll roughly at its
/// replacement value (base + carry-capacity + chop*wood-multiplier) so that
/// converting banked resources into a capable troll is ~score-neutral and the
/// short rollout can then tip it positive via the extra production. This is the
/// crux: a short horizon forces the eval to encode the long-term value that a
/// pure heuristic hard-codes.
fn troll_value(game: &GameState, player: usize) -> f64 {
    let base = envf("SB_TROLL_BASE", 4.0);
    let cc_w = envf("SB_CC_W", 3.0);
    let chop_w = envf("SB_CHOP_W", 8.0);
    let hp_w = envf("SB_HP_W", 1.0);
    game.units
        .iter()
        .filter(|u| u.player as usize == player)
        .map(|u| base + cc_w * u.cc as f64 + chop_w * u.chop as f64 + hp_w * u.hp as f64)
        .sum()
}

fn eval(game: &GameState, me: usize) -> f64 {
    let opp = 1 - me;
    let carry_w = envf("SB_CARRY_W", 0.5);

    let mut s = (game.scores[me] - game.scores[opp]) as f64;
    s += carry_w * (carried_value(game, me) - carried_value(game, opp));
    s += troll_value(game, me) - troll_value(game, opp);
    s
}

// ── rollout ──────────────────────────────────────────────────────────────────

/// Simulate `k` turns from a CLONE of `game`. Player `me` follows `my_plan`
/// (with `turn0_train` on the first turn, then `auto_train`); the opponent
/// follows a fixed greedy-chopper model. Returns the terminal eval for `me`.
fn rollout(
    game: &GameState,
    me: usize,
    my_plan: Plan,
    turn0_train: Option<(i32, i32, i32, i32)>,
    k: i32,
) -> f64 {
    let opp = 1 - me;
    let opp_plan = Plan { choppers: 1, mine: true }; // chopper-boss model
    let mut g = game.clone();
    let start = g.turn;
    let mut first = true;
    while g.turn < start + k && g.turn < 300 {
        let my_train = if first { turn0_train } else { auto_train(&g, me) };
        let my_cmds = plan_cmds(&g, me, my_plan, my_train);
        let opp_cmds = plan_cmds(&g, opp, opp_plan, auto_train(&g, opp));
        if me == 0 {
            step(&mut g, &my_cmds, &opp_cmds);
        } else {
            step(&mut g, &opp_cmds, &my_cmds);
        }
        first = false;
    }
    eval(&g, me)
}

// ── candidate enumeration ────────────────────────────────────────────────────

/// Curated TRAIN candidates for the turn-0 decision: None (save) plus a few
/// affordable specs spanning chopper / harvester / filler.
fn train_candidates(game: &GameState, player: usize) -> Vec<Option<(i32, i32, i32, i32)>> {
    let has_iron = !game.iron.is_empty();
    let specs: [(i32, i32, i32, i32); 6] = [
        if has_iron { (2, 4, 2, 2) } else { (2, 4, 2, 0) }, // big chopper (boss engine)
        if has_iron { (2, 2, 1, 2) } else { (2, 2, 1, 0) }, // fast cheap chopper
        (1, 3, 2, 0),                                       // strong harvester
        (1, 2, 2, 0),                                       // harvester
        (1, 2, 1, 0),                                       // filler
        (1, 1, 1, 0),                                       // cheapest body
    ];
    let cap = envi("SB_TRAIN_CAND", 3) as usize;
    let mut out: Vec<Option<(i32, i32, i32, i32)>> = vec![None];
    for s in specs {
        if out.len() > cap {
            break;
        }
        if affordable(game, player, s) {
            out.push(Some(s));
        }
    }
    out
}

fn role_candidates(game: &GameState, player: usize) -> Vec<Plan> {
    let chop_capable = game
        .units
        .iter()
        .filter(|u| u.player as usize == player && u.chop >= 1)
        .count() as i32;
    let max_ch = chop_capable.min(envi("SB_MAX_CHOPPERS", 2));
    let mut plans = Vec::new();
    for c in 0..=max_ch {
        plans.push(Plan { choppers: c, mine: false });
        // Mining only makes sense for a chop-capable troll that ISN'T chopping.
        if !game.iron.is_empty() && c < chop_capable {
            plans.push(Plan { choppers: c, mine: true });
        }
    }
    if plans.is_empty() {
        plans.push(Plan { choppers: 0, mine: false });
    }
    plans
}

impl Strategy for SearchBot {
    fn name(&self) -> &str {
        "search"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let k = envi("SB_K", 12);
        let trains = train_candidates(game, player);
        let roles = role_candidates(game, player);

        let mut best_score = f64::NEG_INFINITY;
        let mut best_role = roles[0];
        let mut best_train = trains[0];

        for &plan in &roles {
            for &train in &trains {
                let sc = rollout(game, player, plan, train, k);
                if sc > best_score {
                    best_score = sc;
                    best_role = plan;
                    best_train = train;
                }
            }
        }

        plan_cmds(game, player, best_role, best_train)
    }
}
