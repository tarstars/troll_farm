//! yannbot Task 6 tests: endgame_mode trigger boundaries, the new endgame PICK/PLANT
//! candidates inside `troll_candidates`, pair coordination + `decide_yann` assembly, the
//! funding-union mandate (Task-5-review carry-forward A), and a TRAIN regression for the
//! shack-occupancy mandate (carry-forward C). Fixture helpers (`grid_state`, `mk_tree`,
//! `mk_starter`) are copied verbatim from `tests/yann_core.rs` / `tests/yann_funding.rs`
//! per established precedent — integration test files can't share code with each other.
//! Spec: docs/superpowers/specs/2026-07-11-yannbot-design.md.
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

// the (1,1,1,1) starter troll (verified: "the (1,1,1,1) starter" -- gold_elite.rs et al.),
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

// a fully-custom troll (movement/carry/harvest/chop all controllable), empty carry.
fn mk_troll(id: i32, x: i32, y: i32, ms: i32, cc: i32, hp: i32, chop: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: ms,
        carry_capacity: cc,
        harvest_power: hp,
        chop_power: chop,
        carry: [0; 6],
    }
}

// APPLE tree, custom size, health 1 + cooldown 100 -- health 1 makes chop_t = ceil_div(1,
// chop_power) = 1 for any positive chop_power (an "instant chop"); cooldown 100 keeps it
// from growing within any small arrival window used by these fixtures. APPLE is never
// `choose_type_to_cut`'s result (LEMON/PLUM only), so it structurally never triggers the
// denial multiplier regardless of `ttc` -- keeping the throughput arithmetic clean.
fn mk_apple(x: i32, y: i32, size: i32) -> Tree {
    Tree {
        tree_type: "APPLE".to_string(),
        x,
        y,
        size,
        health: 1,
        fruits: 0,
        cooldown: 100,
    }
}

// ── endgame_mode trigger boundaries ─────────────────────────────────────────────

#[test]
fn endgame_trigger_boundaries() {
    // turn cutoff: 250 not yet endgame; 251 is -- regardless of trees/score (both tied).
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    s.turn = 250;
    assert_eq!(endgame_mode(&s), None);
    s.turn = 251;
    assert_eq!(endgame_mode(&s), Some(true)); // tied score (0==0) -> ahead via `>=`

    // trees/behind boundary; turn=1 so the turn cutoff never fires on its own.
    let mut s2 = grid_state(6, 4, (0, 1), (5, 1));
    s2.turn = 1;
    s2.trees.push(mk_tree("LEMON", 1, 1));
    s2.trees.push(mk_tree("LEMON", 2, 1));
    s2.trees.push(mk_tree("LEMON", 4, 1)); // 3 trees total
    s2.opp_inventory[WOOD] = 1; // opp_score 4 > my_score 0 -> behind
    assert_eq!(endgame_mode(&s2), None); // 3 trees > YE_TREES(2) -> trigger doesn't fire

    s2.trees.pop(); // now 2 trees, still behind
    assert_eq!(endgame_mode(&s2), Some(false)); // trees<=2 && behind -> endgame, behind

    s2.my_inventory[WOOD] = 5; // my_score 20 >= opp_score 4 -> now ahead
    assert_eq!(endgame_mode(&s2), None); // trees<=2 but NOT behind -> trigger doesn't fire
}

// ── pair coordination + decide_yann assembly ────────────────────────────────────

#[test]
fn pair_dedup_picks_true_max_when_best_tree_is_shared() {
    reset_mem();
    let mut s = grid_state(10, 6, (0, 2), (9, 2));
    // 3 APPLE trees (APPLE is never `choose_type_to_cut`'s result, so this fixture is
    // structurally immune to the denial multiplier -- every value below is exactly
    // wood/(travel+chop_t+ret), no adjustment). health=1 + chop_power=100 make chop_t =
    // ceil_div(1,100) = 1 for every tree; cooldown=100 means none of them grow within
    // these tiny travel windows (0-3 turns), so arrival size/health == starting.
    s.trees.push(mk_apple(2, 2, 4)); // tree_a: AT both trolls' shared start cell
    s.trees.push(mk_apple(1, 2, 4)); // tree_b: the unique cell 1 step from BOTH the
                                     // trolls' start and the shack (a "midpoint")
    s.trees.push(mk_apple(5, 2, 4)); // tree_c: a far, deliberately weak distractor
    s.my_trolls.push(mk_troll(1, 2, 2, 1, 10, 0, 100));
    s.my_trolls.push(mk_troll(2, 2, 2, 1, 10, 0, 100));

    // hand-computed (full derivation in the task report): tree_a value = wood(4) /
    // (travel0+chop_t1+ret2=3) = 4/3; tree_b value = 4/(travel1+chop_t1+ret1=3) = 4/3
    // (tied with a); tree_c value = 4/(travel3+chop_t1+ret5=9) = 4/9 (well under the
    // fallback park's fixed 1.0, never competitive). Both trolls are identically
    // positioned/statted, so each independently prefers tree_a -- but tree_a's cell can
    // only go to ONE of them. The true combined max is 4/3+4/3 = 8/3, achieved ONLY by
    // splitting across tree_a and tree_b (repeating either tree collides on its cell and
    // is forbidden). Of the two ways to split (troll 1 on tree_a / troll 2 on tree_b, or
    // the reverse), the canonical tie-break (lexicographically smaller concatenated
    // command) picks "CHOP 1" + "MOVE 2 1 2" over "MOVE 1 1 2" + "CHOP 2" ('C' < 'M').
    let cmds = decide_yann(&s);
    assert_eq!(cmds, vec!["CHOP 1".to_string(), "MOVE 2 1 2".to_string()]);
}

#[test]
fn decide_yann_is_deterministic_across_reset_games() {
    // reuses the tied-value fixture above (deliberately -- the exact-tie case is the one
    // most likely to expose nondeterministic tie-breaking).
    let build = || {
        let mut s = grid_state(10, 6, (0, 2), (9, 2));
        s.trees.push(mk_apple(2, 2, 4));
        s.trees.push(mk_apple(1, 2, 4));
        s.trees.push(mk_apple(5, 2, 4));
        s.my_trolls.push(mk_troll(1, 2, 2, 1, 10, 0, 100));
        s.my_trolls.push(mk_troll(2, 2, 2, 1, 10, 0, 100));
        s
    };
    reset_mem();
    let cmds1 = decide_yann(&build());
    reset_mem();
    let cmds2 = decide_yann(&build());
    assert_eq!(cmds1, cmds2);
}

// ── behind-endgame PICK / PLANT (troll_candidates) ──────────────────────────────

#[test]
fn behind_endgame_pick_prefers_cheapest_banana_first() {
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    s.turn = 251; // forces endgame via the turn cutoff regardless of tree count/score
    s.my_inventory = [1, 1, 1, 3, 0, 0]; // PLUM/LEMON/APPLE all banked too -- BANANA (the
                                         // brief's priority order) must still win.
    s.opp_inventory = [0, 0, 0, 0, 0, 10]; // opp_score 40 >> my_score 6 -> behind
    let troll = mk_starter(1, 1, 1); // adjacent to shack (0,1); empty carry, free_capacity 1>0
    s.my_trolls.push(troll.clone());
    let ctx = Ctx::build(&s);
    let cands = troll_candidates(&s, &troll, LEMON, false, &ctx);
    let pick = cands
        .iter()
        .find(|c| c.cmd == "PICK 1 BANANA")
        .expect("expected a PICK candidate for the cheapest (BANANA-first) banked fruit");
    assert_eq!(pick.score, 6000.0);
    assert!(
        !cands.iter().any(|c| c.cmd.starts_with("PICK 1 PLUM")
            || c.cmd.starts_with("PICK 1 LEMON")
            || c.cmd.starts_with("PICK 1 APPLE")),
        "only the cheapest (BANANA) banked fruit should be offered, not the others"
    );
}

#[test]
fn behind_endgame_plant_on_first_free_shack_neighbor() {
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    s.turn = 251;
    s.opp_inventory = [0, 0, 0, 0, 0, 10]; // behind
                                           // ortho_neighbors((0,1)) = [(0,2),(1,1),(0,0),(-1,1)]; (0,2) is walkable and hosts no
                                           // tree -- the deterministic first free neighbor. Stand the troll exactly there so the
                                           // command is the literal PLANT (not a MOVE-toward-it; see the next test for that case).
    let mut troll = mk_starter(1, 0, 2);
    troll.carry[BANANA] = 1; // carrying a banana, as if it had just PICKed one
    s.my_trolls.push(troll.clone());
    let ctx = Ctx::build(&s);
    let cands = troll_candidates(&s, &troll, LEMON, false, &ctx);
    let plant = cands
        .iter()
        .find(|c| c.cmd == "PLANT 1 BANANA")
        .expect("expected a PLANT candidate at the first free shack-neighbor cell");
    assert_eq!(plant.score, 6000.0);
    assert_eq!(plant.target, Some((0, 2)));
}

#[test]
fn behind_endgame_plant_moves_toward_the_cell_first_when_not_yet_there() {
    let mut s = grid_state(6, 4, (0, 1), (5, 1));
    s.turn = 251;
    s.opp_inventory = [0, 0, 0, 0, 0, 10]; // behind
                                           // troll adjacent to the shack but NOT standing on the first free neighbor (0,2).
    let mut troll = mk_starter(1, 1, 1);
    troll.carry[BANANA] = 1;
    s.my_trolls.push(troll.clone());
    let ctx = Ctx::build(&s);
    let cands = troll_candidates(&s, &troll, LEMON, false, &ctx);
    let plant = cands
        .iter()
        .find(|c| c.target == Some((0, 2)) && c.score == 6000.0)
        .expect("expected a move-toward-the-plant-cell candidate");
    assert_eq!(plant.cmd, "MOVE 1 0 2");
}

// ── Mandatory A: funding-phase union with troll_candidates ──────────────────────

#[test]
fn funding_full_starter_bank_move_dominates() {
    reset_mem();
    let mut s = grid_state(20, 6, (0, 2), (19, 2));
    // a reachable, affordable-looking PLUM source so the funding side of the union
    // produces a concrete, competitive (~4850) score -- not a vacuous empty list -- and
    // the bank move (7000) must still dominate it.
    let mut plum = mk_tree("PLUM", 14, 2);
    plum.fruits = 5;
    s.trees.push(plum);
    let mut troll = mk_starter(1, 15, 2); // far from the shack (0,2), not adjacent
    troll.carry[WOOD] = 1; // full: free_capacity = cc(1) - 1 = 0
    s.my_trolls.push(troll);

    let cmds = decide_yann(&s);
    assert_eq!(cmds.len(), 1);
    assert_eq!(
        cmds[0], "MOVE 1 1 2",
        "expected the bank MOVE (score 7000, dominating the ~4850 funding score)"
    );
}

// ── Mandatory C: TRAIN shack-occupancy regression (opponent trolls too) ─────────

#[test]
fn train_suppressed_when_opponent_occupies_my_shack() {
    // engine::apply_train's real precondition is "no unit -- mine OR the opponent's --
    // stands on our shack cell" (verified in Task 5's report by reading engine.rs);
    // Task 5's code only checked `state.my_trolls`. Regression-guard the fix.
    let spec = (3, 2, 1, 3);
    let mut s = grid_state(10, 6, (0, 2), (9, 2));
    s.my_inventory = training_cost(1, spec); // exactly affordable
    let troll = mk_starter(1, 1, 2); // MY troll adjacent to the shack, NOT on it
    s.my_trolls.push(troll.clone());
    s.opp_trolls.push(mk_starter(99, 0, 2)); // an OPPONENT troll sitting on OUR shack cell

    let cands = funding_candidates(&s, &troll, spec);
    assert!(
        !cands.iter().any(|c| c.cmd.starts_with("TRAIN")),
        "TRAIN must be suppressed when an opponent troll occupies our shack cell"
    );
}
