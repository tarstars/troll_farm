//! v1.43.0-yield (design D2, user architecture request 2026-07-08): "picker stands on
//! the banana tree, picking fruits, and it blocks the way of the wood gatherer -- solve
//! it at the level of missions: urgency, blocking." A same-team STATIONARY troll
//! (CHOP/HARVEST/PLANT/MINE/PICK/DROP at its own cell) is a hard wall for landings
//! (engine fact, game/engine.rs apply_moves :204-280 -- `occupied` starts as all of that
//! player's positions and a stationary unit's cell never leaves it, no exception). That
//! can fully block a lower-ms mover with strictly more valuable work queued up behind it.
//! `planner::yield_pass` detects exactly that shape (after `assign` + the FIRST
//! `motion::solve_moves`) and, iff the blocked mover's assignment outranks its
//! blocker's, lets the blocker yield ONE turn (re-match to its own next-best candidate,
//! re-solve motion once more) -- see data/candidates/v1.43.0-yield/brief.md.
//!
//! Three tests:
//!   1. `yield_corridor` -- the livelock itself: a picker (band 38, PLUM) stationary
//!      mid-corridor fully blocks a full-bank chopper (band 80) behind it. Must FAIL
//!      pre-fix (yield_pass stub returns None; the corridor stays blocked).
//!   2. `no_yield_when_blocker_outranks` -- regression pin: swap which troll has the
//!      higher-value task (blocker now band 75, mover now band 38) -- no yield must
//!      fire. Must PASS both before AND after the fix (Test-B style, per
//!      tests/idlefruit.rs's precedent).
//!   3. `yield_single_round` -- bound: the blocked mover's blocker's OWN re-match target
//!      is occupied by a SECOND, unrelated stationary troll -- exactly one re-match is
//!      attempted this turn (telemetry: `planner::yields() == 1`), no cascade to a
//!      different teammate, mover remains blocked (accepted, not retried this turn).
//! [helpers copied VERBATIM from tests/idlefruit.rs / tests/pickloop.rs style]
use std::collections::HashSet;
use troll_farm::botmain::motion;
use troll_farm::botmain::planner::{assign, yield_pass, yields};
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{bfs_distances, Cell, State, Tree, Troll};

/// 1-wide horizontal corridor: shack (0,2) NOT walkable; (1,2)..=(n,2) walkable. (1,2) is
/// the shack's only ortho-neighbor, so it's the sole camp/bank cell -- the geometry every
/// test in this file relies on to make a mid-corridor stationary troll a HARD block (a
/// lower-ms mover behind it has no way around).
fn corridor_state(n: i32) -> State {
    let mut walkable: HashSet<Cell> = HashSet::new();
    for x in 1..=n {
        walkable.insert((x, 2));
    }
    State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (99, 2),
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

fn corridor_plan(walkable: &HashSet<Cell>) -> Plan {
    let farm_d = bfs_distances(walkable, &[(0, 2)]);
    Plan {
        shack: (0, 2),
        farm_d,
        opp: (99, 2),
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
    }
}

/// Pure (non-chopping) harvester, ms=1 -- the "picker" role.
fn starter(id: i32, x: i32, y: i32) -> Troll {
    Troll { id, x, y, movement_speed: 1, carry_capacity: 2, harvest_power: 1, chop_power: 0, carry: [0; 6] }
}
/// ms=1 full-of-wood chopper -- the "wood gatherer" role (band 80, full -> bank).
fn full_chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll { id, x, y, movement_speed: 1, carry_capacity: 2, harvest_power: 0, chop_power: 2, carry: [0, 0, 0, 0, 0, 2] }
}
fn plum(x: i32, y: i32, fruits: i32) -> Tree {
    Tree { tree_type: "PLUM".into(), x, y, size: 2, health: 4, fruits, cooldown: 0 }
}
fn banana(x: i32, y: i32, fruits: i32) -> Tree {
    Tree { tree_type: "BANANA".into(), x, y, size: 2, health: 4, fruits, cooldown: 0 }
}
/// ms=1 chopper with room to spare (not full) -- used as an UNRELATED stationary
/// obstacle (ChopHere) in yield_single_round; must never be touched by yield_pass.
fn idle_chopper(id: i32, x: i32, y: i32) -> Troll {
    Troll { id, x, y, movement_speed: 1, carry_capacity: 2, harvest_power: 0, chop_power: 2, carry: [0; 6] }
}

/// Run assign() -> build intents -> first solve_moves -> rewrite cmd_by_id, EXACTLY the
/// pipeline botmain.rs::decide_elite runs before calling yield_pass. Returns
/// (cmd_by_id, landing) as yield_pass receives them.
fn first_pass(st: &State, plan: &Plan, my: &[Troll]) -> (std::collections::HashMap<i32, String>, std::collections::HashMap<i32, Cell>) {
    let mut cmd_by_id = assign(st, plan, my);
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
    let landing = motion::solve_moves(st, my, &intents);
    for (id, cell) in &landing {
        let cur = my.iter().find(|t| t.id == *id).map(|t| t.pos());
        if cur != Some(*cell) {
            cmd_by_id.insert(*id, format!("MOVE {} {} {}", id, cell.0, cell.1));
        }
    }
    (cmd_by_id, landing)
}

#[test]
fn yield_corridor() {
    // Corridor (1,2)..(6,2), shack (0,2). S (id 1) stands at (3,2) on a ripe PLUM --
    // band 38 (idle-fruit), value 38*BAND, a pure non-move HARVEST. M (id 2, a chopper
    // full of wood) sits directly behind it at (4,2), ms=1 -- band 80 (full -> bank,
    // target = the sole camp cell (1,2)), value 80*BAND. M's only within-ms=1 landing
    // candidate is S's cell, which is a hard wall (engine fact) -- M is fully blocked
    // (zero progress) even though its task vastly outranks S's (80*BAND > 38*BAND).
    troll_farm::botmain::planner::reset();
    let mut st = corridor_state(6);
    st.trees = vec![plum(3, 2, 2)];
    let plan = corridor_plan(&st.walkable);
    let s = starter(1, 3, 2);
    let m = full_chopper(2, 4, 2);
    let my = vec![s, m];

    let (cmd_by_id, landing) = first_pass(&st, &plan, &my);
    // Pre-fix sanity (documented, not a separate assertion -- the RED run below shows
    // it): the picker blocks the chopper solid.
    assert_eq!(landing.get(&2), Some(&(4, 2)), "setup check: M must start fully blocked by S");
    assert_eq!(cmd_by_id[&1], "HARVEST 1", "setup check: S must start stationary-harvesting");

    let result = yield_pass(&st, &plan, &my, &cmd_by_id, &landing);
    assert!(
        result.is_some(),
        "expected a yield: M's full-bank task (80*BAND) outranks S's idle-fruit task (38*BAND)"
    );
    let (new_cmds, new_landing) = result.unwrap();
    assert_ne!(new_cmds[&1], "HARVEST 1", "S must yield off its cell, got: {}", &new_cmds[&1]);
    assert_ne!(
        new_landing.get(&2),
        Some(&(4, 2)),
        "M must advance once S yields, got landing {:?}",
        new_landing.get(&2)
    );
}

#[test]
fn no_yield_when_blocker_outranks() {
    // Regression pin (Test-B style, tests/idlefruit.rs precedent): SAME corridor and
    // adjacency, but roles/values swapped. S (id 1) at (3,2) stands on a ripe BANANA --
    // band 75 (a "wanted" fruit, value 75*BAND), still a pure non-move HARVEST. M (id 2)
    // is now a pure starter (no bank/chop task at all) chasing an idle-fruit PLUM at
    // (2,2), beyond S -- band 38 (value 38*BAND-ish). M is still fully blocked by S (its
    // only within-ms=1 landing candidate is S's cell), but this time value(S)=75*BAND >
    // value(M)=~38*BAND, so the yield policy (strict `>`) must NOT fire: S keeps
    // harvesting, M waits. Must pass whether or not yield_pass is implemented yet (a
    // stub that never yields trivially satisfies "no yield fired" too).
    troll_farm::botmain::planner::reset();
    let mut st = corridor_state(6);
    st.trees = vec![banana(3, 2, 2), plum(2, 2, 2)];
    let plan = corridor_plan(&st.walkable);
    let s = starter(1, 3, 2);
    let m = starter(2, 4, 2);
    let my = vec![s, m];

    let (cmd_by_id, landing) = first_pass(&st, &plan, &my);
    assert_eq!(landing.get(&2), Some(&(4, 2)), "setup check: M must start fully blocked by S");
    assert_eq!(cmd_by_id[&1], "HARVEST 1", "setup check: S must start stationary-harvesting");

    let result = yield_pass(&st, &plan, &my, &cmd_by_id, &landing);
    assert!(
        result.is_none(),
        "S's task (75*BAND) outranks M's (38*BAND-ish): no yield must fire, got {:?}",
        result
    );
}

#[test]
fn yield_single_round() {
    // Bound: at most ONE (mover, blocker) pair is acted on per turn -- no cascade, even
    // when the chosen blocker's OWN re-match doesn't actually succeed.
    //
    // Corridor (1,2)..(4,2), a dead end (M has no OTHER direction at all). S2 (id 3) is
    // an UNRELATED stationary chopper (ChopHere on a fruitless banana -- so it never
    // competes for S1's fruit bands) at (2,2) -- exactly the cell S1's own next-best
    // candidate (Park's scarce-camp ring-2 redirect: the shack's only ortho-neighbor is
    // (1,2), so camp_cells=1 <= 2, and the only walkable manhattan-2 ring cell is (2,2))
    // wants to move to. S1 (id 1) stands on a ripe PLUM at (3,2) -- band 38, value
    // 38*BAND -- directly blocking M (id 2, a full-bank chopper at (4,2), ms=1, band 80,
    // value 80*BAND), exactly like yield_corridor. (M, S1) is detected and acted on
    // (M's task outranks S1's); S1 is re-matched to Park, which -- unaware of S2's
    // PHYSICAL occupancy, since park_cmd only tracks its own `claimed` bookkeeping, not
    // troll positions -- still targets (2,2). The re-solve then correctly refuses to let
    // S1 actually land there (S2 is genuinely stationary there), so S1 stays put and M
    // remains blocked -- but exactly ONE re-match was ATTEMPTED this turn
    // (yields()==1), S2's own assignment was never touched, and nothing loops or panics.
    troll_farm::botmain::planner::reset();
    let mut st = corridor_state(4);
    st.trees = vec![banana(2, 2, 0), plum(3, 2, 2)]; // S2's fruitless banana, S1's ripe plum
    let plan = corridor_plan(&st.walkable);
    let s2 = idle_chopper(3, 2, 2);
    let s1 = starter(1, 3, 2);
    let m = full_chopper(2, 4, 2);
    let my = vec![s2, s1, m];

    let (cmd_by_id, landing) = first_pass(&st, &plan, &my);
    assert_eq!(landing.get(&2), Some(&(4, 2)), "setup check: M must start fully blocked by S1");
    assert_eq!(cmd_by_id[&1], "HARVEST 1", "setup check: S1 must start stationary-harvesting");
    assert_eq!(cmd_by_id[&3], "CHOP 3", "setup check: S2 must start stationary-chopping");

    let result = yield_pass(&st, &plan, &my, &cmd_by_id, &landing);
    assert!(result.is_some(), "expected one yield attempt: M's task (80*BAND) outranks S1's (38*BAND)");
    let (new_cmds, new_landing) = result.unwrap();

    assert_eq!(yields(), 1, "exactly one yield must be attempted this turn, no cascade to S2");
    assert!(
        new_cmds[&1].starts_with("MOVE 1"),
        "S1 must have attempted to yield off its cell, got: {}",
        &new_cmds[&1]
    );
    assert_eq!(new_cmds[&3], "CHOP 3", "S2 must never be touched -- only one teammate yields per turn");
    assert_eq!(
        new_landing.get(&2),
        Some(&(4, 2)),
        "M remains blocked this turn (S1's own re-match target is itself occupied by S2) -- accepted, not retried until next turn's re-detection"
    );
}
