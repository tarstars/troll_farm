//! v1.41.0-nopickloop — user-observed corridor livelock: on maps where water + the map
//! edge leave no reachable, tree-free, un-occupied cell within the farm radius, the OLD
//! planner still issued PICK whenever the tent held a banked banana (the printer's band
//! 50 only checked `inv[BANANA] > 0 && free_capacity() > 0`, never whether the banana
//! could ever be planted). The picked banana then had nowhere to go: band 80 (full ->
//! bank) is suppressed for a banana-carrying starter expecting to plant, so the fallback
//! band 10 banked it right back, and PICK fired again next turn -- an infinite PICK<->DROP
//! loop that also parks the starter on a scarce shack-adjacent cell the chopper needs for
//! banking. `base_trees < farm_cap` ("room" in the farm) is a TREE COUNT, not a free-CELL
//! check -- that mismatch is the bug's heart.
//!
//! This is not a new failure mode for this codebase: the older pre-R6b cascade
//! (`strategies/mybot.rs`, ~line 319) already hit and fixed the identical bug ("PICKing
//! without a plantable spot caused a PICK<->DROP livelock (cc1 starter, 130 turns in a
//! real arena game)") by computing the plantable spot once and gating both the PLANT and
//! PICK actions on it. The R6b joint planner (`botmain/planner.rs`) reintroduced the bug
//! because its band 50 (PICK) was never wired to the band-88 plant-cell search. This file
//! restores the same structural fix inside the new bands/Cand architecture.
//!
//! Four tests:
//!   A. `no_pick_without_reachable_plant_cell` -- the livelock itself: PICK must not fire
//!      when no reachable plant cell exists. Must FAIL pre-fix.
//!   B. `scarce_camp_park_leaves_drop_cell_free` -- the companion motion fix: idle-parking
//!      must not clog the one or two walkable cells next to a scarce-camp shack. Must FAIL
//!      pre-fix.
//!   C. `pick_stays_enabled_when_plant_cell_lies_beyond_a_tree` -- false-suppression guard:
//!      a real plant cell reachable only by a BFS path that runs through a tree-occupied
//!      cell must NOT be missed (trees are not walkability obstacles in this engine; only
//!      terrain is). Must PASS both before and after the fix (a non-regression pin).
//!   D. `errand_reaches_pick_on_scarce_map` -- reviewer CRITICAL: test B's ring-2 redirect
//!      must apply ONLY to band-10 idle parking, never to the band-49 park-to-pick ERRAND
//!      (`target: Some(shack)`), which is goal-directed and must reach manhattan==1 to ever
//!      unlock PICK. On a scarce-camp map, redirecting the errand through the ring-2 detour
//!      strands it: `claimed` resets every `assign()` call, so the redirected troll re-picks
//!      its OWN ring-2 cell every turn (distance 0 from itself) and reissues a self-target
//!      MOVE forever. Must FAIL pre-fix (stalls at the ring-2 cell within 12 simulated turns).
use std::collections::HashSet;
use troll_farm::botmain::motion;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{bfs_distances, State, Tree, Troll};

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

/// A pure (non-chopping) starter: chop_power=0 so no fell/chop-help band ever competes
/// with the plant/printer bands under test here.
fn pure_starter(id: i32, x: i32, y: i32, carry: [i32; 6]) -> Troll {
    Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 2,
        harvest_power: 1,
        chop_power: 0,
        carry,
    }
}

#[test]
fn no_pick_without_reachable_plant_cell() {
    // Corridor: shack (0,2); walkable ONLY {(1,2),(2,2)}, both occupied by a fruitless
    // banana tree. `base_trees` (2) < `farm_cap` (12) says there is "room" in the farm --
    // but every walkable cell in radius is tree-occupied, so the plant-cell search (farm_d
    // <= farm_r, reachable, tree-free, troll-free) finds NOTHING. base_trees counts TREES,
    // not free CELLS -- exactly the bug's heart.
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    walkable.insert((1, 2));
    walkable.insert((2, 2));
    let farm_d = bfs_distances(&walkable, &[(0, 2)]); // (1,2)->1, (2,2)->2

    let state = State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (7, 2),
        my_inventory: [0, 0, 0, 3, 0, 0], // 3 banked bananas in the tent
        opp_inventory: [0; 6],
        trees: vec![banana(1, 2, 2), banana(2, 2, 2)], // BOTH corridor cells tree-occupied
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 150,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    };
    let plan = Plan {
        shack: (0, 2),
        farm_d,
        opp: (7, 2),
        have_iron: false,
        turns_rem: 150,
        n: 1,
        farm_now: 2,
        nchop: 0,
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
        base_trees: 2,
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
    };
    // Standing at (1,2): shack-adjacent (manhattan 1), empty-handed, tent has bananas.
    let my = vec![pure_starter(0, 1, 2, [0; 6])];
    let cmds = assign(&state, &plan, &my);
    assert!(
        !cmds[&0].starts_with("PICK"),
        "must not PICK a banana with nowhere reachable to plant it: got {}",
        &cmds[&0]
    );
}

#[test]
fn scarce_camp_park_leaves_drop_cell_free() {
    // Shack (0,2) has exactly ONE walkable ortho-neighbor: (1,2). Two more cells extend
    // the corridor -- (1,1) and (2,2) -- both manhattan-2 from the shack. A starter is
    // ALREADY parked at (2,2) (a fine, out-of-the-way spot); asking it to idle-park must
    // NOT walk it onto the sole scarce camp cell (1,2), which the chopper needs free to
    // bank into.
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    walkable.insert((1, 2));
    walkable.insert((1, 1));
    walkable.insert((2, 2));

    let state = State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (7, 2),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 150,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    };
    let starter = pure_starter(0, 2, 2, [0; 6]);
    let d = bfs_distances(&state.walkable, &[(2, 2)]); // (2,2)->0, (1,2)->1, (1,1)->2
    let mut claimed: HashSet<(i32, i32)> = HashSet::new();
    let cmd = motion::park_cmd(&state, (0, 2), &starter, &d, &mut claimed, true);
    assert_ne!(
        cmd, "MOVE 0 1 2",
        "idle park must not clog the sole scarce camp cell: got {}",
        cmd
    );
}

#[test]
fn pick_stays_enabled_when_plant_cell_lies_beyond_a_tree() {
    // False-suppression guard: the new gate must not treat tree-occupied cells as BFS
    // obstacles (they aren't -- only terrain gates `state.walkable`/`bfs_distances`, per
    // state.rs; `state.trees` never participates in reachability, only in filtering which
    // reachable cell is a valid PLANT destination). Linear corridor shack(0,2) -> (1,2) ->
    // (2,2) -> (3,2). Hand-computed distances (BFS == manhattan on this straight line):
    //   farm_d (from the shack):   (1,2)=1, (2,2)=2, (3,2)=3
    //   d      (from the starter at (1,2)): (1,2)=0, (2,2)=1, (3,2)=2
    // Trees occupy (1,2) [the starter's own cell] AND (2,2) [the mid-corridor cell] --
    // both fruitless bananas, so bands 52/75 stay silent. farm_r is widened to 3 (from the
    // live default of 2) so the corridor's 3rd cell is in-radius: this test targets the
    // gate's generic reachability behavior, not the live GE_FARM_R constant, and radius 2
    // cannot fit "tree-free start -> tree cell -> free target" (the target would sit at
    // farm_d 3, already outside a radius-2 farm). The ONLY walkable cell that is in-radius,
    // reachable, tree-free and troll-free is (3,2) -- and the ONLY path to it runs straight
    // through the tree-occupied (2,2). A search that wrongly treated tree cells as
    // obstacles would strand `d` at/before (1,2), see (3,2) as unreachable, return
    // plant_cell = None, and wrongly suppress PICK.
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    walkable.insert((1, 2));
    walkable.insert((2, 2));
    walkable.insert((3, 2));
    let farm_d = bfs_distances(&walkable, &[(0, 2)]);
    assert_eq!(farm_d[&(1, 2)], 1);
    assert_eq!(farm_d[&(2, 2)], 2);
    assert_eq!(farm_d[&(3, 2)], 3);

    let state = State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (7, 2),
        my_inventory: [0, 0, 0, 3, 0, 0], // 3 banked bananas
        opp_inventory: [0; 6],
        trees: vec![banana(1, 2, 2), banana(2, 2, 2)], // starter's own cell + the mid blocker
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 150,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    };
    let plan = Plan {
        shack: (0, 2),
        farm_d,
        opp: (7, 2),
        have_iron: false,
        turns_rem: 150,
        n: 1,
        farm_now: 2,
        nchop: 0,
        spec: (2, 2, 0, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (2, 2, 0, 2),
        cost: [0; 6],
        train_now: false,
        need_iron: false,
        need_fund: [false; 3],
        farm_r: 3, // widened -- see comment above
        farm_cap: 12,
        fell_size: 2,
        farm_fell: 2,
        chop_r: 5,
        starter_chop: true,
        liquidation: false,
        base_trees: 2,
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
    };
    let my = vec![pure_starter(0, 1, 2, [0; 6])];
    let cmds = assign(&state, &plan, &my);
    assert_eq!(
        cmds[&0], "PICK 0 BANANA",
        "a reachable plant cell exists beyond the mid-corridor tree; PICK must stay enabled: got {}",
        &cmds[&0]
    );
}

#[test]
fn errand_reaches_pick_on_scarce_map() {
    // Reviewer CRITICAL: motion::park_cmd's ring-2 scarce-camp redirect (test B, above) must
    // apply ONLY to band-10 IDLE parking (`Kind::Park, target: None`), never to the band-49
    // park-to-pick ERRAND (`Kind::Park, target: Some(shack)`). The errand is GOAL-DIRECTED --
    // it exists only to close the manhattan distance to 1 so band-50's PICK can fire next --
    // but the ring-2 redirect has no such convergence guarantee. `claimed` is a fresh HashSet
    // every `assign()` call (planner.rs), so a redirected errand that reaches its own ring-2
    // cell sees, next turn, that very cell as the nearest unclaimed manhattan-2 option
    // (distance 0 from itself) and reissues a MOVE to its own position forever -- a permanent
    // stall the anti-stall watchdog can't catch (it only sidesteps a MOVE whose target
    // differs from the troll's current cell).
    //
    // Shack (0,2) has exactly ONE walkable ortho-neighbor, (1,2) -- camp_cells=1 <= 2, so the
    // scarce-camp branch is live. A corridor extends it: {(1,2),(2,2),(3,2),(4,2),(5,2)}, no
    // trees anywhere (the plant-cell gate stays open on every in-range cell regardless of
    // where the starter stands), tent holds 1 banana, and a pure (chop_power=0) starter
    // begins at the far end (5,2) -- 5 cells from the shack, so it must actually travel the
    // errand rather than start already adjacent.
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 1..=5 {
        walkable.insert((x, 2));
    }
    let farm_d = bfs_distances(&walkable, &[(0, 2)]);

    let state = State {
        walkable,
        my_shack: (0, 2),
        opp_shack: (99, 99),
        my_inventory: [0, 0, 0, 1, 0, 0], // 1 banked banana in the tent
        opp_inventory: [0; 6],
        trees: vec![], // no trees: the plant-cell gate stays open everywhere in range
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 150,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    };
    let plan = Plan {
        shack: (0, 2),
        farm_d,
        opp: (99, 99),
        have_iron: false,
        turns_rem: 150,
        n: 1,
        farm_now: 0,
        nchop: 0,
        spec: (2, 2, 0, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (2, 2, 0, 2),
        cost: [0; 6],
        train_now: false,
        need_iron: false,
        need_fund: [false; 3],
        farm_r: 5, // covers the whole corridor -- the plant-cell gate must stay open
        farm_cap: 12,
        fell_size: 2,
        farm_fell: 2,
        chop_r: 5,
        starter_chop: true,
        liquidation: false,
        base_trees: 0, // 0 < farm_cap: "room" in the farm -- the gate the printer bands key off
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
    };
    let mut my = vec![pure_starter(0, 5, 2, [0; 6])];

    let mut reached = false;
    for turn in 0..12 {
        let cmds = assign(&state, &plan, &my);
        let cmd = cmds[&0].clone();
        if cmd.starts_with("PICK") {
            reached = true;
            break;
        }
        // Parse "MOVE <id> <x> <y>" and teleport the lone starter there (single troll, no
        // conflicts) -- a stand-in for the engine's move resolution, per the prescribed
        // simplified multi-turn harness.
        let parts: Vec<&str> = cmd.split_whitespace().collect();
        assert_eq!(
            parts.len(),
            4,
            "turn {turn}: expected a MOVE command, got {cmd:?}"
        );
        assert_eq!(
            parts[0], "MOVE",
            "turn {turn}: expected a MOVE command, got {cmd:?}"
        );
        let tx: i32 = parts[2].parse().expect("MOVE x");
        let ty: i32 = parts[3].parse().expect("MOVE y");
        my[0].x = tx;
        my[0].y = ty;
    }
    assert!(
        reached,
        "the park-to-pick errand must reach PICK within 12 turns; starter stalled at {:?}",
        my[0].pos()
    );
}
