//! R6a joint move solver — the activity manager's motion stage (user directive:
//! coordination by joint planning, not iteration order). Tests pin:
//!   1. CORRIDOR EMERGENCE: the optimal 5-turn unload (drop, swap, drop, swap, drop)
//!      must EMERGE from the solver's objective — no hand-coded pipeline policy.
//!   2. SHUFFLE INVARIANCE: permuting intent order / troll list order must not change
//!      the plan (the objective decides, not the order).
//!   3. CROSSING: two trolls with opposing goals in a corridor swap instead of blocking.
use std::collections::{HashMap, HashSet};
use troll_farm::botmain::motion::solve_moves;
use troll_farm::botmain::{State, Troll};

fn corridor_state(n_walk: i32) -> State {
    // shack0 (0,0) unwalkable; corridor (1..=n_walk,0) walkable; shack1 beyond.
    let walkable: HashSet<(i32, i32)> = (1..=n_walk).map(|x| (x, 0)).collect();
    State {
        walkable,
        my_shack: (0, 0),
        opp_shack: (n_walk + 1, 0),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 1,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

fn troll(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 2,
        harvest_power: 1,
        chop_power: 1,
        carry: [0; 6],
    }
}

#[test]
fn corridor_unload_emerges_from_the_objective() {
    // 3 FULL trolls at (1,0)(2,0)(3,0); drop cell = (1,0) (shack-adjacent); exit = (6,0).
    // Policy layer: full troll ON the drop cell DROPs (stationary); everyone else MOVEs —
    // full toward the drop cell, empty toward the exit. The solver must pipeline via swaps:
    // drops complete on turns 1, 3, 5 (optimal).
    let st = corridor_state(6);
    let drop = (1, 0);
    let exit = (6, 0);
    let mut pos: HashMap<i32, (i32, i32)> = [(0, (1, 0)), (2, (2, 0)), (4, (3, 0))].into();
    let mut full: HashMap<i32, bool> = [(0, true), (2, true), (4, true)].into();
    let mut drops = 0;
    let mut turns = 0;
    for _ in 0..12 {
        turns += 1;
        let mut intents: Vec<(i32, (i32, i32))> = Vec::new();
        let mut dropping: Vec<i32> = Vec::new();
        for (&id, &p) in &pos {
            if full[&id] && p == drop {
                dropping.push(id); // DROP action: stationary this turn
            } else {
                intents.push((id, if full[&id] { drop } else { exit }));
            }
        }
        let my: Vec<Troll> = pos.iter().map(|(&id, &(x, y))| troll(id, x, y)).collect();
        let landing = solve_moves(&st, &my, &intents);
        // apply: dropping trolls stay + become empty; movers go to their landing cells
        for id in dropping {
            full.insert(id, false);
            drops += 1;
        }
        let finals: Vec<(i32, i32)> = landing.values().copied().collect();
        let mut sorted = finals.clone();
        sorted.sort();
        assert!(
            sorted.windows(2).all(|w| w[0] != w[1]),
            "solver emitted colliding landings"
        );
        for (id, c) in landing {
            pos.insert(id, c);
        }
        if drops == 3 {
            break;
        }
    }
    assert_eq!(
        turns, 5,
        "3-troll corridor unload must complete in the optimal 5 turns"
    );
}

#[test]
fn shuffle_invariance() {
    // open 5x3 room with a conflict: two trolls want the same corridor mouth.
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..5 {
        for y in 0..3 {
            walkable.insert((x, y));
        }
    }
    let mut st = corridor_state(1);
    st.walkable = walkable;
    let my = vec![troll(0, 0, 0), troll(2, 0, 2), troll(4, 2, 1)];
    let intents = vec![(0, (4, 1)), (2, (4, 1)), (4, (4, 1))];
    let base = solve_moves(&st, &my, &intents);
    for perm in [
        vec![(2, (4, 1)), (0, (4, 1)), (4, (4, 1))],
        vec![(4, (4, 1)), (2, (4, 1)), (0, (4, 1))],
    ] {
        let out = solve_moves(&st, &my, &perm);
        assert_eq!(base, out, "intent order changed the plan");
    }
    let my_shuffled = vec![troll(4, 2, 1), troll(0, 0, 0), troll(2, 0, 2)];
    let out = solve_moves(&st, &my_shuffled, &intents);
    assert_eq!(base, out, "troll list order changed the plan");
}

#[test]
fn crossing_trolls_swap_not_block() {
    // 1-wide corridor, two adjacent trolls with opposing goals: the joint optimum is the
    // SWAP (both progress); a sequential planner would block one of them.
    let st = corridor_state(6);
    let my = vec![troll(0, 3, 0), troll(2, 4, 0)];
    let intents = vec![(0, (6, 0)), (2, (1, 0))];
    let landing = solve_moves(&st, &my, &intents);
    assert_eq!(landing[&0], (4, 0), "troll 0 should advance into the swap");
    assert_eq!(landing[&2], (3, 0), "troll 2 should advance into the swap");
}
