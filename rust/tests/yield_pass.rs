//! v1.43.0-yield: one low-value stationary teammate may step aside for a
//! higher-value mover, but the pass is strict-value and single-round.
use std::collections::HashSet;
use troll_farm::botmain::ownership;
use troll_farm::botmain::planner::assign_resolved;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{bfs_distances, State, Tree, Troll, WOOD};

fn corridor_state(walkable: HashSet<(i32, i32)>, trees: Vec<Tree>) -> State {
    State {
        walkable,
        my_shack: (0, 0),
        opp_shack: (5, 5),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees,
        my_trolls: vec![],
        opp_trolls: vec![],
        turn: 80,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

fn plan_for(walkable: &HashSet<(i32, i32)>) -> Plan {
    Plan {
        shack: (0, 0),
        farm_d: bfs_distances(walkable, &[(0, 0)]),
        opp: (5, 5),
        have_iron: false,
        turns_rem: 220,
        n: 2,
        farm_now: 0,
        nchop: 1,
        spec: (2, 3, 0, 2),
        want_chopper: false,
        want_feeder: false,
        train_spec: (2, 3, 0, 2),
        cost: [0; 6],
        train_now: false,
        need_iron: false,
        need_fund: [false; 3],
        farm_r: 2,
        farm_cap: 12,
        fell_size: 2,
        farm_fell: 3,
        chop_r: 5,
        starter_chop: true,
        liquidation: false,
        base_trees: 0,
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
        pressure: ownership::Pressure::default(),
        door: None,
        door_d: None,
    }
}

fn starter(id: i32, x: i32, y: i32) -> Troll {
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

fn ripe_banana(x: i32, y: i32) -> Tree {
    Tree {
        tree_type: "BANANA".into(),
        x,
        y,
        size: 2,
        health: 4,
        fruits: 1,
        cooldown: 0,
    }
}

#[test]
fn yield_corridor_full_banker_displaces_lower_value_harvest() {
    let walkable: HashSet<(i32, i32)> = [(1, 0), (2, 0)].into();
    let st = corridor_state(walkable.clone(), vec![ripe_banana(1, 0)]);
    let plan = plan_for(&walkable);
    let blocker = starter(0, 1, 0);
    let mut mover = chopper(2, 2, 0);
    mover.carry[WOOD] = 2;

    let cmds = assign_resolved(&st, &plan, &[blocker, mover]);

    assert_eq!(
        cmds[&0], "MOVE 0 2 0",
        "lower-value harvester should yield into the vacated corridor cell"
    );
    assert_eq!(
        cmds[&2], "MOVE 2 1 0",
        "full banker should advance onto the drop cell"
    );
}

#[test]
fn no_yield_when_stationary_task_outranks_mover() {
    let walkable: HashSet<(i32, i32)> = [(1, 0), (2, 0)].into();
    let st = corridor_state(walkable.clone(), vec![ripe_banana(1, 0)]);
    let plan = plan_for(&walkable);
    let blocker = starter(0, 1, 0);
    let mut mover = starter(2, 2, 0);
    mover.carry[WOOD] = 1;

    let cmds = assign_resolved(&st, &plan, &[blocker, mover]);

    assert_eq!(
        cmds[&0], "HARVEST 0",
        "higher-value harvest should keep its stationary action"
    );
    assert_eq!(
        cmds[&2], "MOVE 2 1 0",
        "lower-value partial banker still asks for the blocked drop cell"
    );
}

#[test]
fn yield_single_round_only_one_independent_blocker_moves() {
    let walkable: HashSet<(i32, i32)> = [(1, 0), (2, 0), (0, 1), (0, 2)].into();
    let st = corridor_state(walkable.clone(), vec![ripe_banana(1, 0), ripe_banana(0, 1)]);
    let plan = plan_for(&walkable);
    let blocker_a = starter(0, 1, 0);
    let blocker_b = starter(4, 0, 1);
    let mut mover_a = chopper(2, 2, 0);
    let mut mover_b = chopper(6, 0, 2);
    mover_a.carry[WOOD] = 2;
    mover_b.carry[WOOD] = 2;

    let cmds = assign_resolved(&st, &plan, &[blocker_a, mover_a, blocker_b, mover_b]);

    assert_eq!(
        cmds[&0], "MOVE 0 2 0",
        "lowest-id eligible blocker should be the single yield"
    );
    assert_eq!(
        cmds[&2], "MOVE 2 1 0",
        "the yielded corridor should advance"
    );
    assert_eq!(
        cmds[&4], "HARVEST 4",
        "second eligible blocker must not cascade-yield this turn"
    );
    assert_eq!(
        cmds[&6], "MOVE 6 0 1",
        "second mover remains blocked until a later turn"
    );
}
