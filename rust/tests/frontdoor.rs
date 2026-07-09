//! v1.54.0-frontdoor: front-door farm placement (fix the shack-bridged farm_d).
//!
//! Root cause (user replay 895493013, Sasso_Stark; verified against code+replay): `farm_d`
//! is a BFS SEEDED AT THE SHACK CELL. The shack is impassable to trolls, but the BFS still
//! treats it as a zero-cost hub -- so on a map where the shack sits on a chokepoint (a lake
//! + boulders splitting the walkable area into two sides that are only connected via a long
//! real detour), cells on BOTH sides read farm_d<=2 even though they are 20+ REAL walking
//! steps apart. The plant/farm-membership filter then wrongly admits farm cells on both
//! sides, so the gatherer shuttles the whole detour every trip (263/300 turns in transit,
//! measured in the source replay).
//!
//! Fix model: `tactics::compute_door` chokepoint-gates a "front door" override -- BFS
//! distances from ONE walkable neighbor of the shack (farthest-viable-from-enemy among
//! candidates hosting >= MIN_FARM_CELLS) -- consumed by `tactics::farm_eligible` at the
//! farm/plant-membership call sites. `(None, None)` on every normal map: a proven no-op.
//!
//! Fixture: a shack straddling a vertical wall (x=5) with a single detour gap at the
//! bottom (5,10) -- west block x in 0..=4, east block x in 6..=10, both y in 0..=11. The
//! two walkable shack-neighbors (4,2) west / (6,2) east are the only door candidates; true
//! BFS distance between them is 18 (via the detour gap), far past CHOKE_THRESHOLD(8), while
//! the buggy shack-hub `farm_d` reads both as <=2 -- exactly the reported bug shape.
use std::collections::HashSet;
use troll_farm::botmain::planner::assign;
use troll_farm::botmain::tactics::{compute_door, farm_eligible, plan_with_meta, Meta};
use troll_farm::botmain::{State, Tree, Troll, BANANA};

const SHACK: (i32, i32) = (5, 2);
const WEST_DOOR: (i32, i32) = (4, 2);
const EAST_DOOR: (i32, i32) = (6, 2);
const GAP: (i32, i32) = (5, 10);

/// `west_full`: true builds a full 5-wide west room (viable -- plenty of cells within
/// radius 2 of the west door); false builds a single-file corridor at x=4 starting below
/// the door row (only 3 cells sit within radius 2 of the door -- fails MIN_FARM_CELLS, see
/// `door_viability_floor`). The east side is always a full 5-wide room.
fn frontdoor_walkable(west_full: bool) -> HashSet<(i32, i32)> {
    let mut w: HashSet<(i32, i32)> = HashSet::new();
    for x in 6..=10 {
        for y in 0..=11 {
            w.insert((x, y));
        }
    }
    if west_full {
        for x in 0..=4 {
            for y in 0..=11 {
                w.insert((x, y));
            }
        }
    } else {
        for y in 2..=11 {
            w.insert((4, y));
        }
    }
    w.insert(GAP);
    w.remove(&SHACK);
    w
}

fn frontdoor_state(west_full: bool, opp_shack: (i32, i32)) -> State {
    let mut walkable = frontdoor_walkable(west_full);
    walkable.remove(&opp_shack);
    State {
        walkable,
        my_shack: SHACK,
        opp_shack,
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

fn carrier(id: i32, x: i32, y: i32) -> Troll {
    let mut t = Troll {
        id,
        x,
        y,
        movement_speed: 1,
        carry_capacity: 3,
        harvest_power: 0,
        chop_power: 0,
        carry: [0; 6],
    };
    t.carry[BANANA] = 1;
    t
}

#[test]
fn frontdoor_sasso_straddle_fixed() {
    // enemy sits at the east edge -> "farthest from enemy among viable sides" must pick
    // the WEST door.
    let opp = (10, 2);
    let mut st = frontdoor_state(true, opp);
    st.trees = vec![banana(3, 2, 2), banana(7, 2, 2)];
    let plan = plan_with_meta(&st, &st.my_trolls, Meta::Tempo);

    // precondition: this is genuinely the reported bug shape -- the naive shack-hub
    // `farm_d <= farm_r` test admits the far-side cell.
    assert_eq!(
        plan.farm_d.get(&(7, 2)),
        Some(&2),
        "precondition: (7,2) must read farm_d<=2 via the shack-hub BFS (the bug)"
    );

    assert_eq!(
        plan.door,
        Some(WEST_DOOR),
        "must choose the west door (farther from the east-side enemy): {:?}",
        plan.door
    );
    assert!(
        farm_eligible(&plan.farm_d, &plan.door_d, (3, 2), plan.farm_r),
        "near-side cell must stay eligible"
    );
    assert!(
        !farm_eligible(&plan.farm_d, &plan.door_d, (7, 2), plan.farm_r),
        "far-side cell (farm_d<=2 but 18 real steps away) must NOT be eligible post-fix"
    );
    assert_eq!(
        plan.base_trees, 1,
        "only the reachable-side tree should count toward the farm (pre-fix this was 2): {:?}",
        plan.base_trees
    );

    // planner.rs consumption: a carrier with nowhere placed yet must only ever be routed
    // to plant on the WEST side -- the east cells aren't merely deprioritized, they are
    // excluded from the candidate pool entirely (door_d far past farm_r), so this holds
    // regardless of the plant_cell tie-break geometry terms.
    let cmds = assign(&st, &plan, &[carrier(0, 4, 2)]);
    let cmd = &cmds[&0];
    assert!(cmd.contains("PLANT") || cmd.starts_with("MOVE 0 "), "{}", cmd);
    if let Some(rest) = cmd.strip_prefix("MOVE 0 ") {
        let x: i32 = rest.split_whitespace().next().unwrap().parse().unwrap();
        assert!(x < 5, "carrier must never be routed east of the wall: {}", cmd);
    }
}

#[test]
fn frontdoor_open_map_noop() {
    // a plain open room -- no walls at all. Every shack-neighbor pair is close (a small
    // detour around the shack itself, not a real chokepoint), so this must be a total
    // no-op: door/door_d stay None and farm_eligible reduces to the exact pre-fix
    // `farm_d <= farm_r` test everywhere.
    let mut walkable: HashSet<(i32, i32)> = HashSet::new();
    for x in 0..16 {
        for y in 0..10 {
            walkable.insert((x, y));
        }
    }
    walkable.remove(&(8, 5));
    let st = State {
        walkable: walkable.clone(),
        my_shack: (8, 5),
        opp_shack: (15, 5),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 50,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    };
    let plan = plan_with_meta(&st, &st.my_trolls, Meta::Tempo);
    assert_eq!(plan.door, None, "open map must not select a door");
    assert!(plan.door_d.is_none(), "open map must not compute a door BFS");

    for &c in &walkable {
        let old = plan.farm_d.get(&c).map_or(false, |&d| d <= plan.farm_r);
        let new = farm_eligible(&plan.farm_d, &plan.door_d, c, plan.farm_r);
        assert_eq!(old, new, "eligible-set mismatch at {:?} on an open map", c);
    }

    // direct geometry check too (independent of the full Plan pipeline).
    let (door, door_d) = compute_door(&st);
    assert_eq!(door, None);
    assert!(door_d.is_none());

    // NOTE (flip-check, per the brief): manually replacing the
    // `if max_pair <= CHOKE_THRESHOLD` guard in `compute_door` with `if false` and
    // re-running this test makes it FAIL: `left: Some((7, 5)) right: None` -- with the
    // gate disabled, a door still gets chosen on this wide-open room (the opposite-corner
    // detour distance is small but nonzero), diverging from plain farm_d. This confirms
    // the guard is load-bearing, not a vacuous branch. Verified manually during
    // development (see the builder's report); the guard is restored in the committed
    // source below.
}

#[test]
fn door_farthest_from_enemy() {
    // both sides viable (full west + full east); the enemy's position alone must decide
    // which door wins, and flipping it must flip the choice.
    let st_east_enemy = frontdoor_state(true, (10, 2));
    let (door_a, _) = compute_door(&st_east_enemy);
    assert_eq!(
        door_a,
        Some(WEST_DOOR),
        "enemy on the east -> choose the farther (west) door: {:?}",
        door_a
    );

    let st_west_enemy = frontdoor_state(true, (0, 2));
    let (door_b, _) = compute_door(&st_west_enemy);
    assert_eq!(
        door_b,
        Some(EAST_DOOR),
        "flipping the enemy to the west must flip the chosen door to east: {:?}",
        door_b
    );
}

#[test]
fn door_viability_floor() {
    // west is now a single-file corridor: only 3 cells sit within farm_r(2) of the west
    // door (fails MIN_FARM_CELLS=4), even though it is still the farther side from the
    // (east-side) enemy. Must fall back to the nearer-but-viable east door instead of the
    // farther-but-cramped west one.
    let st = frontdoor_state(false, (10, 2));
    let (door, _) = compute_door(&st);
    assert_eq!(
        door,
        Some(EAST_DOOR),
        "the cramped far side must be rejected in favor of the viable near side: {:?}",
        door
    );
}

#[test]
fn frontdoor_determinism_hashset_reorder() {
    // build the identical logical map twice via two different HashSet insertion orders
    // and confirm the chosen door (and its BFS map) come out bit-for-bit identical -- the
    // new code must never let HashSet/HashMap's unspecified iteration order leak into the
    // decision (this codebase was burned by exactly this class of bug before; see
    // state.rs's tie_salt/tie_mix doc comments).
    let opp = (10, 2);

    // order A: the natural nested x-then-y insertion (frontdoor_walkable's own order).
    let st_a = frontdoor_state(true, opp);

    // order B: same logical cell set, inserted y-then-x and reversed.
    let mut walkable_b: HashSet<(i32, i32)> = HashSet::new();
    for y in (0..=11).rev() {
        for x in (6..=10).rev() {
            walkable_b.insert((x, y));
        }
    }
    for y in (0..=11).rev() {
        for x in (0..=4).rev() {
            walkable_b.insert((x, y));
        }
    }
    walkable_b.insert(GAP);
    walkable_b.remove(&SHACK);
    walkable_b.remove(&opp);
    let st_b = State {
        walkable: walkable_b,
        my_shack: SHACK,
        opp_shack: opp,
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees: vec![],
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 50,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    };
    assert_eq!(st_a.walkable, st_b.walkable, "sanity: same logical cell set");

    let (door_a, dd_a) = compute_door(&st_a);
    let (door_b, dd_b) = compute_door(&st_b);
    assert_eq!(
        door_a, door_b,
        "chosen door must not depend on HashSet insertion order"
    );
    assert_eq!(
        dd_a, dd_b,
        "door BFS map must not depend on HashSet insertion order"
    );
}
