use std::collections::HashSet;

use troll_farm::botmain::ownership;
use troll_farm::botmain::tactics::{Phase, Plan};
use troll_farm::botmain::{bfs_distances, Cell, State, Tree, Troll};

fn walk_line(max_x: i32) -> HashSet<Cell> {
    (0..=max_x).map(|x| (x, 0)).collect()
}

fn troll(id: i32, player_x: i32, hp: i32, chop: i32) -> Troll {
    Troll {
        id,
        x: player_x,
        y: 0,
        movement_speed: 1,
        carry_capacity: 3,
        harvest_power: hp,
        chop_power: chop,
        carry: [0; 6],
    }
}

fn banana(x: i32, size: i32, health: i32) -> Tree {
    Tree {
        tree_type: "BANANA".to_string(),
        x,
        y: 0,
        size,
        health,
        fruits: 0,
        cooldown: 0,
    }
}

fn state(turn: i32, trees: Vec<Tree>, my_trolls: Vec<Troll>, opp_trolls: Vec<Troll>) -> State {
    State {
        walkable: walk_line(6),
        my_shack: (0, 0),
        opp_shack: (6, 0),
        my_inventory: [0; 6],
        opp_inventory: [0; 6],
        trees,
        my_trolls,
        opp_trolls,
        turn,
        iron_cells: HashSet::new(),
        water_cells: HashSet::new(),
    }
}

fn plan(st: &State) -> Plan {
    let farm_d = bfs_distances(&st.walkable, &[st.my_shack]);
    Plan {
        shack: st.my_shack,
        farm_d,
        opp: st.opp_shack,
        have_iron: false,
        turns_rem: 300 - st.turn + 1,
        n: st.my_trolls.len() as i32,
        farm_now: st.trees.len(),
        nchop: 0,
        spec: (1, 1, 1, 1),
        want_chopper: false,
        want_feeder: false,
        train_spec: (1, 1, 1, 1),
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
        base_trees: st.trees.len(),
        seed_cells: HashSet::new(),
        phase: Phase::Tempo,
    }
}

#[test]
fn near_chopper_owns_tree_value() {
    ownership::reset();
    let st = state(
        75,
        vec![banana(1, 2, 4)],
        vec![troll(0, 1, 0, 2)],
        vec![troll(1, 6, 0, 1)],
    );
    let own = ownership::analyze(&st, &plan(&st));

    assert_eq!(own.total, 8);
    assert_eq!(own.ours, 8);
    assert_eq!(own.opp, 0);
    assert_eq!(own.uncertain, 0);
}

#[test]
fn created_farm_tree_exposed_when_only_opponent_can_convert() {
    ownership::reset();
    let initial = state(1, vec![], vec![troll(0, 0, 0, 0)], vec![troll(1, 6, 0, 0)]);
    let _ = ownership::analyze(&initial, &plan(&initial));

    let later = state(
        75,
        vec![banana(1, 2, 4)],
        vec![troll(0, 0, 0, 0)],
        vec![troll(1, 1, 0, 2)],
    );
    let own = ownership::analyze(&later, &plan(&later));

    assert_eq!(own.total, 8);
    assert_eq!(own.opp, 8);
    assert_eq!(own.created_exposed, 8);
    assert_eq!(own.own_half_exposed, 8);
}
