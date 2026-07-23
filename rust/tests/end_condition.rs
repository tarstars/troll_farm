use std::collections::HashSet;
use troll_farm::game::engine::has_stalled;
use troll_farm::game::state::{Cell, GameState, Plant, Unit};

fn base_state() -> GameState {
    let mut walkable: HashSet<Cell> = HashSet::new();
    for x in 0..6 {
        for y in 0..4 {
            walkable.insert((x, y));
        }
    }
    GameState {
        width: 6,
        height: 4,
        walkable,
        shacks: [(0, 1), (5, 2)],
        inventories: [[0; 6]; 2],
        units: vec![
            Unit {
                id: 0,
                player: 0,
                x: 1,
                y: 1,
                ms: 1,
                cc: 1,
                hp: 1,
                chop: 0,
                carry: [0; 6],
            },
            Unit {
                id: 1,
                player: 1,
                x: 4,
                y: 2,
                ms: 1,
                cc: 1,
                hp: 1,
                chop: 0,
                carry: [0; 6],
            },
        ],
        plants: Vec::new(),
        scores: [0, 0],
        turn: 1,
        next_id: 2,
        iron: HashSet::new(),
        water: HashSet::new(),
    }
}

fn put_plant(game: &mut GameState, cell: Cell) {
    game.plants.push(Plant {
        plant_type: "BANANA".to_string(),
        x: cell.0,
        y: cell.1,
        size: 1,
        health: 3,
        fruits: 0,
        cooldown: 0,
    });
}

#[test]
fn no_plants_no_grace_ends_immediately() {
    let game = base_state();
    let mut counter = 0;
    assert!(has_stalled(&game, &mut counter));
}

#[test]
fn unit_on_tree_sets_walk_home_grace() {
    let mut game = base_state();
    put_plant(&mut game, (3, 2));
    game.units[0].x = 3;
    game.units[0].y = 2;
    let mut counter = 0;
    assert!(!has_stalled(&game, &mut counter));
    assert_eq!(counter, 10);

    game.plants.clear();
    game.inventories[0][0] = 1;
    game.inventories[1][0] = 1;
    for _ in 0..9 {
        assert!(!has_stalled(&game, &mut counter));
    }
    assert!(has_stalled(&game, &mut counter));
}

#[test]
fn mercy_ends_for_a_losing_stuck_player() {
    let mut game = base_state();
    game.inventories[0][3] = 2;
    game.scores = [2, 0];
    let mut counter = 5;
    assert!(has_stalled(&game, &mut counter));

    game.scores[1] = 10;
    let mut counter = 5;
    assert!(!has_stalled(&game, &mut counter));
}

#[test]
fn carried_iron_does_not_prevent_stuck_but_wood_does() {
    let mut iron_only = base_state();
    iron_only.units[0].carry[4] = 2;
    let mut counter = 5;
    assert!(has_stalled(&iron_only, &mut counter));

    let mut with_wood = base_state();
    with_wood.units[0].carry[5] = 1;
    let mut counter = 5;
    assert!(!has_stalled(&with_wood, &mut counter));
}
