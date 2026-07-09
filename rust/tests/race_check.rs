//! v1.36.0-race (user replay finding #1): DOOMED-TARGET RACE CHECK. A tree an enemy is
//! already standing on and chopping is a RACE: if they will fell it before we can arrive,
//! walking there donates the travel for nothing (skip the candidate entirely). If we can
//! arrive before they finish, the wood splits round-robin among cell-sharers (engine
//! apply_chop) — still worth joining, just discounted.
//! [helpers copied VERBATIM from tests/planner_tasks.rs]
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{State, Tree, Troll};

fn base_state() -> State {
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..8 {
        for y in 0..5 {
            walkable.insert((x, y));
        }
    }
    walkable.remove(&(0, 2)); // my shack cell (not walkable)
    State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (7, 2),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 50,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

fn base_plan() -> Plan {
    // farm_d: BFS map distances from the shack over the 8x5 open room (shack at (0,2))
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..8 {
        for y in 0..5 {
            walkable.insert((x, y));
        }
    }
    walkable.remove(&(0, 2));
    let farm_d = troll_farm::botmain::bfs_distances(&walkable, &[(0, 2)]);
    Plan {
        shack: (0, 2),
        farm_d,
        opp: (7, 2),
        have_iron: false,
        turns_rem: 250,
        n: 2,
        farm_now: 0,
        nchop: 1,
        spec: (2, 2, 0, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (2, 2, 0, 2),
        cost: [0; 6],
        train_now: false,
        need_iron: false,
        need_fund: [false; 3],
        farm_r: 2,
        farm_cap: 12,
        fell_size: 2,
        farm_fell: 2,
        chop_r: 5,
        starter_chop: true,
        liquidation: false,
        base_trees: 0,
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
        pressure: ownership::Pressure::default(),
    }
}

fn starter(id: i32, x: i32, y: i32) -> Troll {
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
fn chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 2,
        carry_capacity: 2,
        harvest_power: 0,
        chop_power: 2,
        carry: [0; 6],
    }
}
fn banana(x: i32, y: i32, size: i32) -> Tree {
    Tree {
        tree_type: "BANANA".into(),
        x,
        y,
        size,
        health: 2 + size,
        fruits: 0,
        cooldown: 0,
    }
}

#[test]
fn doomed_contested_tree_is_skipped() {
    // enemy stands ON the near tree (3,2) with health 2 left and chop_power 2 (chopper()'s
    // default) -> ceil(2/2) = 1 turn to fell it. We are at (1,2), map-distance 2 away with
    // ms=2 (chopper()'s default) -> our_eta = ceil(2/2) = 1 turn: they finish in the SAME
    // turn we'd arrive, so the race is lost (doomed) and this candidate must be skipped
    // entirely (in both the primary fell band and the anti-starvation fallback). A farther
    // free tree at (6,2) exists (no enemy on it) — we must go THERE instead.
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2), banana(6, 2, 2)]; // near contested, far free
    st.trees[0].health = 2; // enemy chop 2 fells it next turn
    st.opp_trolls = vec![chopper(9, 3, 2)]; // enemy ON (3,2)
    let my = vec![chopper(2, 1, 2)];
    let cmds = assign(&st, &base_plan(), &my);
    assert!(
        cmds[&2].contains("6 2"),
        "doomed race must be skipped: {}",
        &cmds[&2]
    );
    assert!(
        !cmds[&2].contains("3 2"),
        "must not target the doomed tree at all: {}",
        &cmds[&2]
    );
}

#[test]
fn winnable_contest_is_joined() {
    // enemy on the tree but it has lots of health (enemy chop_power reduced to 1, health 9)
    // -> ceil(9/1) = 9 turns for them to finish. We are at (1,2), map-distance 2 away with
    // ms=2 -> our_eta = 1 turn: we arrive long before they finish, so the race is WINNABLE —
    // join it (the discount is mild, never enough to lose to the much-farther alternative).
    let mut st = base_state();
    st.trees = vec![banana(3, 2, 2), banana(7, 2, 2)];
    st.trees[0].health = 9;
    let mut e = chopper(9, 3, 2);
    e.chop_power = 1;
    st.opp_trolls = vec![e];
    let my = vec![chopper(2, 1, 2)];
    let cmds = assign(&st, &base_plan(), &my);
    assert!(
        cmds[&2].contains("3 2"),
        "winnable contest should be joined: {}",
        &cmds[&2]
    );
}

#[test]
#[ignore] // sharepen4 inconclusive; PEN=2 champion semantics restored
fn share_pen_shifts_near_tie_to_free_tree() {
    // RACE_SHARE_PEN sweep (2 -> 4, v1.39.0-sharepen4, analyst b62c977 queue #1): a WINNABLE
    // contested tree (enemy on it, but plenty of health left so we arrive long before they
    // finish) sits at eta=1; a FREE tree of the same size (so the same chop_t) sits at eta=4.
    // DENY_W=0 in this candidate, so deny_pen=0 for both and the band-70 MoveTo values reduce
    // to `70*BAND - (steps + chop_t) - race_pen`:
    //   contested: 70*BAND - (1 + chop_t) - pen        free: 70*BAND - (4 + chop_t) - 0
    // At pen=2: contested = 70*BAND-3-chop_t-2, free = 70*BAND-4-chop_t -> contested wins by 1
    //   (excessive trekking PAST the free tree to reach a merely-discounted shared one).
    // At pen=4: contested = 70*BAND-3-chop_t-4, free = 70*BAND-4-chop_t -> free wins by 1.
    // Our chopper is slowed to ms=1 (movement_speed overridden) so the small 8x5 test grid can
    // still separate eta=1 from eta=4 with plain map-distance (dist 1 vs dist 4).
    troll_farm::botmain::planner::reset();
    let mut st = base_state();
    st.trees = vec![banana(2, 2, 2), banana(3, 4, 2)]; // [0] contested near (eta 1), [1] free far (eta 4)
    st.opp_trolls = vec![chopper(9, 2, 2)]; // enemy ON the near tree; health 4 left, their chop_power 2 -> 2 turns to fell (winnable: our_eta=1 < 2)
    let plan = base_plan();
    let my = Troll {
        movement_speed: 1,
        ..chopper(5, 1, 2)
    }; // slowed so eta 1 vs eta 4 separate cleanly on this grid
    let cmds = assign(&st, &plan, &[my]);
    assert!(
        cmds[&5].contains("3 4"),
        "RACE_SHARE_PEN=4 should discount the joinable contest enough to prefer the free tree at (3,4): got {}",
        &cmds[&5]
    );
    assert!(
        !cmds[&5].contains("2 2"),
        "must not still trek to the discounted contested tree: {}",
        &cmds[&5]
    );
}
