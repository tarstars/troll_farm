//! yannbot Task 5 funding-phase tests: choose_target_spec / est_gather_turns /
//! funding_candidates (TRAIN / deficit-gather / DROP), exercised through a minimal
//! all-walkable grid fixture built directly from `State`'s public fields — no dependency on
//! planner/tactics/ownership, mirroring yann.rs's own isolation (spec:
//! docs/superpowers/specs/2026-07-11-yannbot-design.md).
//!
//! Fixture helpers (`grid_state`, `mk_tree`) are copied verbatim from `tests/yann_core.rs`
//! per the task brief — integration test files can't share code with each other.
use std::collections::HashSet;
use troll_farm::botmain::yann::*;
use troll_farm::botmain::*;

// all-walkable w x h grid minus the two shack cells; empty everything else.
fn grid_state(w: i32, h: i32, my_shack: Cell, opp_shack: Cell) -> State {
    let mut walkable = HashSet::new();
    for x in 0..w {
        for y in 0..h {
            let c = (x, y);
            if c != my_shack && c != opp_shack {
                walkable.insert(c);
            }
        }
    }
    State {
        walkable,
        my_shack,
        opp_shack,
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: Vec::new(),
        my_trolls: Vec::new(),
        opp_trolls: Vec::new(),
        turn: 1,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

// size 2, health = base + slope*size (PLUM/LEMON base 4 slope 2 -> 8; APPLE 8/3 -> 14;
// BANANA 2/1 -> 4), fruits 0, cooldown 5.
fn mk_tree(ty: &str, x: i32, y: i32) -> Tree {
    let (base, slope) = match ty {
        "PLUM" | "LEMON" => (4, 2),
        "APPLE" => (8, 3),
        "BANANA" => (2, 1),
        _ => panic!("mk_tree: unknown type {}", ty),
    };
    let size = 2;
    Tree {
        tree_type: ty.to_string(),
        x,
        y,
        size,
        health: base + slope * size,
        fruits: 0,
        cooldown: 5,
    }
}

// the (1,1,1,1) starter troll (verified: "the (1,1,1,1) starter" — gold_elite.rs et al.),
// empty carry, at (x,y).
fn mk_starter(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 1,
        harvest_power: 1,
        chop_power: 1,
        carry: [0; 6],
    }
}

// ── choose_target_spec / est_gather_turns ───────────────────────────────────────

#[test]
fn thresholds_arithmetic_picks_stat_per_resource() {
    // start inventory [4,2,2,8,4,0] (PLUM/LEMON/APPLE/BANANA/IRON/WOOD); shack (0,2) on an
    // open 10x6 grid.
    // PLUM (fruited) at (2,2): shack_dist 2 (open grid = manhattan) -> round_trip =
    //   2*2+2 = 6; shortfall 10-4=6; yield min(hp=1,cc=1)=1 -> est = ceil_div(6,1)*6 = 36
    //   <= YF_T(40) -> stat 3.
    // LEMON (fruited) at (5,2): shack_dist 5 -> round_trip 12; shortfall 10-2=8; est =
    //   ceil_div(8,1)*12 = 96 > 40 -> stat 2.
    // IRON cell at (2,3): its nearest walkable ortho-neighbor is at shack_dist 2 (tied
    //   between (1,3) and (2,2) -- either way round_trip is 6, the tie is irrelevant here);
    //   shortfall 10-4=6; per-trip min(chop.max(1)=1, cc=1)=1 -> est = 36 <= 40 -> stat 3.
    // hp is always fixed at 1.
    let mut s = grid_state(10, 6, (0, 2), (9, 2));
    let mut plum = mk_tree("PLUM", 2, 2);
    plum.fruits = 3;
    s.trees.push(plum);
    let mut lemon = mk_tree("LEMON", 5, 2);
    lemon.fruits = 3;
    s.trees.push(lemon);
    s.iron_cells.insert((2, 3));
    s.walkable.remove(&(2, 3)); // iron cells are not walkable terrain (parse_grid: '.' xor '+')
    s.my_inventory = [4, 2, 2, 8, 4, 0];
    s.my_trolls.push(mk_starter(1, 1, 2));

    assert_eq!(choose_target_spec(&s), (3, 2, 1, 3));
}

#[test]
fn est_gather_turns_with_no_source_is_sentinel_and_defaults_to_stat_two() {
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    s.my_trolls.push(mk_starter(1, 1, 1));
    // no trees, no iron cells anywhere -> every resource is "unreachable".
    assert_eq!(est_gather_turns(&s, PLUM, 5), i32::MAX / 2);
    assert_eq!(est_gather_turns(&s, LEMON, 5), i32::MAX / 2);
    assert_eq!(est_gather_turns(&s, IRON, 5), i32::MAX / 2);
    // need <= 0 short-circuits to 0 turns regardless of source (trivially "gatherable").
    assert_eq!(est_gather_turns(&s, PLUM, 0), 0);
    assert_eq!(choose_target_spec(&s), (2, 2, 1, 2));
}

// ── funding_candidates: TRAIN ───────────────────────────────────────────────────

#[test]
fn train_candidate_gated_on_exact_affordability() {
    let spec = (3, 2, 1, 3);
    let mut s = grid_state(10, 6, (0, 2), (9, 2));
    s.iron_cells.insert((2, 3)); // have_iron = true, so mb_afford enforces the IRON slot
    s.walkable.remove(&(2, 3));
    let troll = mk_starter(1, 1, 2); // adjacent to shack, NOT on it
    s.my_trolls.push(troll.clone());

    // exact cost per the REAL engine formula: n = CURRENT troll count (1 here), matching
    // engine::apply_train's own `n` (verified by reading it — see the task report; NOT the
    // brief's literal `training_cost(2, spec)`). PLUM 1+9=10, LEMON 1+4=5, APPLE 1+1=2,
    // IRON 1+9=10.
    let cost = training_cost(1, spec);
    assert_eq!(cost, [10, 5, 2, 0, 10, 0]);

    s.my_inventory = cost;
    let cands = funding_candidates(&s, &troll, spec);
    let train = cands
        .iter()
        .find(|c| c.cmd == "TRAIN 3 2 1 3")
        .expect("expected a TRAIN candidate when exactly affordable");
    assert_eq!(train.score, 9000.0);
    assert_eq!(train.target, None);

    s.my_inventory[PLUM] = 9; // one short of the PLUM slot
    let cands2 = funding_candidates(&s, &troll, spec);
    assert!(!cands2.iter().any(|c| c.cmd.starts_with("TRAIN")));
}

#[test]
fn train_candidate_suppressed_when_shack_occupied_falls_back_to_move_off() {
    // engine::apply_train's real positional precondition (verified by reading it) is NOT
    // "troll adjacent to shack" -- it's "no unit stands on the shack cell" (the spawn
    // point), checked across ALL units. Put the funding troll exactly on the shack (as at
    // turn-1 spawn) while otherwise affordable, and expect TRAIN suppressed with a
    // move-off-the-shack fallback instead (score Y_TRAIN - 1 = 8999).
    let spec = (3, 2, 1, 3);
    let mut s = grid_state(10, 6, (0, 2), (9, 2));
    s.iron_cells.insert((2, 3));
    s.walkable.remove(&(2, 3));
    s.my_inventory = training_cost(1, spec);
    let troll = mk_starter(1, 0, 2); // exactly on my_shack (0,2)
    s.my_trolls.push(troll.clone());

    let cands = funding_candidates(&s, &troll, spec);
    assert!(!cands.iter().any(|c| c.cmd.starts_with("TRAIN")));
    let fallback = cands
        .iter()
        .find(|c| c.score == 8999.0)
        .expect("expected a move-off-shack fallback candidate");
    assert!(
        fallback.cmd.starts_with("MOVE 1 "),
        "fallback should move the blocking troll, got {}",
        fallback.cmd
    );
}

// ── funding_candidates: deficit gathering (HARVEST / MINE / MOVE) ──────────────────

#[test]
fn mine_candidate_requires_adjacency_and_iron_deficit() {
    let spec = (1, 1, 1, 2); // n=1 -> cost[IRON] = 1 + 2*2 = 5
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    s.iron_cells.insert((3, 1));
    s.walkable.remove(&(3, 1));
    let troll = mk_starter(1, 2, 1); // adjacent to iron (3,1): manhattan((2,1),(3,1)) == 1
    s.my_trolls.push(troll.clone());
    s.my_inventory = [0, 0, 0, 0, 0, 0]; // IRON deficient: 0 < 5

    let cands = funding_candidates(&s, &troll, spec);
    assert!(
        cands.iter().any(|c| c.cmd == "MINE 1"),
        "adjacent + needed should emit MINE"
    );

    // adjacent but NOT needed (inventory already covers the IRON cost) -> no MINE and no
    // iron-gathering MOVE either (the item is skipped as non-deficient entirely).
    let mut s_sated = grid_state(6, 4, (0, 1), (5, 1));
    s_sated.iron_cells.insert((3, 1));
    s_sated.walkable.remove(&(3, 1));
    s_sated.my_trolls.push(troll.clone());
    s_sated.my_inventory = [0, 0, 0, 0, 5, 0];
    let cands_sated = funding_candidates(&s_sated, &troll, spec);
    assert!(
        !cands_sated
            .iter()
            .any(|c| c.cmd == "MINE 1" || c.cmd == "MOVE 1 2 1"),
        "sated IRON should produce no mine/move-to-iron candidate"
    );

    // needed but NOT adjacent -> no MINE; falls back to MOVE toward the nearest access cell
    // (the walkable neighbor of (3,1) closest to the shack is (2,1) at shack_dist 2).
    let far_troll = mk_starter(1, 0, 3);
    s.my_trolls = vec![far_troll.clone()];
    let cands_far = funding_candidates(&s, &far_troll, spec);
    assert!(!cands_far.iter().any(|c| c.cmd == "MINE 1"));
    assert!(
        cands_far.iter().any(|c| c.cmd == "MOVE 1 2 1"),
        "not-adjacent-but-needed should MOVE toward the nearest iron access cell"
    );
}

#[test]
fn harvest_fires_when_standing_on_fruited_tree_else_moves_toward_it() {
    let spec = (3, 1, 1, 1); // n=1 -> cost[PLUM] = 1 + 3*3 = 10, deficient from 0
    let mut s = grid_state(8, 4, (0, 1), (7, 1));
    let mut plum = mk_tree("PLUM", 3, 1);
    plum.fruits = 2;
    s.trees.push(plum);
    let on_tree = mk_starter(1, 3, 1); // standing exactly on the plum tree
    s.my_trolls.push(on_tree.clone());
    s.my_inventory = [0, 0, 0, 0, 0, 0];

    let cands = funding_candidates(&s, &on_tree, spec);
    assert!(
        cands.iter().any(|c| c.cmd == "HARVEST 1"),
        "standing on a fruited needed tree should emit HARVEST"
    );

    let away = mk_starter(1, 0, 3); // not on any tree
    s.my_trolls = vec![away.clone()];
    let cands2 = funding_candidates(&s, &away, spec);
    assert!(!cands2.iter().any(|c| c.cmd == "HARVEST 1"));
    assert!(
        cands2.iter().any(|c| c.cmd == "MOVE 1 3 1"),
        "away from the tree should MOVE toward it instead"
    );
}

// ── funding_candidates: DROP ─────────────────────────────────────────────────────

#[test]
fn drop_fires_when_carrying_a_needed_item_adjacent_to_shack() {
    let spec = (2, 2, 1, 2); // n=1 -> cost PLUM=1+4=5, LEMON=1+4=5 (no iron cells -> ignored)
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    let mut troll = mk_starter(1, 1, 1); // adjacent to shack (0,1)
    troll.carry[PLUM] = 1; // carrying a still-deficient item
    s.my_trolls.push(troll.clone());
    s.my_inventory = [0, 0, 0, 0, 0, 0];

    let cands = funding_candidates(&s, &troll, spec);
    let drop = cands
        .iter()
        .find(|c| c.cmd == "DROP 1")
        .expect("expected a DROP candidate");
    assert_eq!(drop.score, 8000.0);
    assert_eq!(drop.target, Some((0, 1)));
}
