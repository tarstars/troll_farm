//! v1.38.0-deny1 (A2 probe): DENIAL-WEIGHT bias in the chopper's PRIMARY fell choice (bands
//! 70/72 only). Historical basis: biasing the chopper's fell target toward the opponent's
//! shack (MB_DENIAL_W in botmain.rs's pre-planner deciders) was the single biggest lever of
//! the silver era; the R6b joint planner (planner.rs) has carried weight 0 since it replaced
//! the sequential cascade. This locks in the first slice: at a genuine ETA tie between two
//! equally-fellable, equally-far trees in OUR half, the planner must prefer the one CLOSER to
//! the opponent (the contestable, shared-map wood) over the one deeper in our own territory.
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
#[ignore] // A2 reverted; DENY_W parked at 0 (analyst b62c977) — this assertion requires DENY_W=1;
          // confirmed FAILING at DENY_W=0 (falls back to the lexicographic tie-break) before
          // being ignored, see data/candidates/v1.39.0-sharepen4/report.md
fn tied_eta_prefers_the_contested_tree() {
    // Two equal-size (size-2, health-4) fellable bananas, both in OUR half (own_half: manhattan
    // to our shack (0,2) <= manhattan to opp shack (7,2)) and both within farm/roam radius, so
    // BOTH clear every filter in the band-70 fell loop identically:
    //   (2,1) deep in our half:      manhattan to shack = 3, to opp = 6  (3 <= 6 -> own_half OK)
    //   (3,2) toward the middle:     manhattan to shack = 3, to opp = 4  (3 <= 4 -> own_half OK,
    //                                 but only just -- this is the CONTESTED one)
    // The chopper sits at (2,3): BFS map-distance (open room, only (0,2) is non-walkable, and
    // neither path needs to detour near it) is exactly 2 to EACH tree, so at ms=2 both get
    // eta=1 -- a genuine tie. Both trees are size-2 (chop_power=2 -> chop_t=2 for both) and
    // neither has an enemy standing on it (race_pen=0 for both). So every term the pre-fix
    // value formula used (70*BAND - steps - chop_t - race_pen) is IDENTICAL for both trees.
    //
    // Pre-fix, the tie is broken purely by the candidate sort key (-value, target): (2,1) <
    // (3,2) lexicographically, so the deep tree wins -- despite (3,2) being equally reachable
    // AND contestable. DENY_W biases toward the opponent, so the contested tree (3,2) must win
    // OUTRIGHT (a strictly higher value, not merely a tie-break artifact).
    troll_farm::botmain::planner::reset();
    let mut st = base_state();
    st.trees = vec![banana(2, 1, 2), banana(3, 2, 2)];
    let plan = base_plan();
    let my = vec![chopper(2, 2, 3)];
    let cmds = assign(&st, &plan, &my);
    assert_eq!(
        cmds[&2], "MOVE 2 3 2",
        "chopper should prefer the contested tree (3,2, nearer the opponent) over the deep tree (2,1): got {}",
        &cmds[&2]
    );
}
