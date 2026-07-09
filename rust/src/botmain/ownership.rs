//! DEBUG-only total-map value ownership diagnostic.
//!
//! This module computes a rough, auditable ownership split from the live per-turn
//! `State`. It must not feed decisions back into planner behavior; callers only
//! print the result when `DEBUG` is enabled.
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
