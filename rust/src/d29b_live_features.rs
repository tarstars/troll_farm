// Compact live D29b history and canonical spatial feature extraction.

use crate::game::types::{GameState, PlantKind};

pub const SCALAR_COUNT: usize = 426;
pub const PLANES: usize = 36;
pub const HEIGHT: usize = 11;
pub const WIDTH: usize = 22;
pub const AREA: usize = HEIGHT * WIDTH;
pub const GRID_COUNT: usize = PLANES * AREA;
const STATE_COUNT: usize = 86;
const MAP_COUNT: usize = 14;
const VELOCITY: [usize; 17] = [
    16, 38, 43, 44, 45, 47, 66, 71, 72, 74, 75, 76, 77, 82, 83, 84, 85,
];
const ITEM_ORDER: [usize; 6] = [2, 3, 4, 1, 0, 5];

fn manhattan(left: (i32, i32), right: (i32, i32)) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

#[derive(Clone, Copy, Default)]
struct UnitAggregate {
    carry: [i32; 6],
    sum: [i32; 4],
    maximum: [i32; 4],
    count: i32,
    own_distance: i32,
    other_distance: i32,
}

fn units(game: &GameState, player: usize) -> UnitAggregate {
    let mut result = UnitAggregate::default();
    for unit in game.units.iter().filter(|unit| unit.player == player) {
        result.count += 1;
        for item in 0..6 {
            result.carry[item] += unit.carry[item];
        }
        let values = [
            unit.stats.movement_speed,
            unit.stats.carry_capacity,
            unit.stats.harvest_power,
            unit.stats.chop_power,
        ];
        for index in 0..4 {
            result.sum[index] += values[index];
            result.maximum[index] = result.maximum[index].max(values[index]);
        }
        result.own_distance += manhattan(unit.cell, game.shacks[player]);
        result.other_distance += manhattan(unit.cell, game.shacks[1 - player]);
    }
    result
}

fn state(game: &GameState) -> [f32; STATE_COUNT] {
    // The frozen simulator corpus starts with scores=[0, 0] and updates them
    // after turn 1, while the live parser derives scores from initial stock.
    // Preserve the training representation at the only discrepant snapshot.
    let scores = if game.turn == 1 { [0, 0] } else { game.scores };
    let mut count = [0i32; 4];
    let mut size = [0i32; 4];
    let mut health = [0i32; 4];
    let mut fruits = [0i32; 4];
    let mut cooldown = 0i32;
    let mut closer = [0i32; 3];
    let mut near = [0i32; 2];
    let mut near_fruits = [0i32; 2];
    let mut ripe_closer = [0i32; 2];
    for plant in &game.plants {
        let kind = plant.kind.item_index();
        count[kind] += 1;
        size[kind] += plant.size;
        health[kind] += plant.health;
        fruits[kind] += plant.fruits;
        cooldown += plant.cooldown;
        let ours = manhattan(plant.cell, game.shacks[0]);
        let theirs = manhattan(plant.cell, game.shacks[1]);
        if ours < theirs {
            closer[0] += 1;
            ripe_closer[0] += i32::from(plant.fruits > 0);
        } else if theirs < ours {
            closer[1] += 1;
            ripe_closer[1] += i32::from(plant.fruits > 0);
        } else {
            closer[2] += 1;
        }
        if ours <= 3 {
            near[0] += 1;
            near_fruits[0] += plant.fruits;
        }
        if theirs <= 3 {
            near[1] += 1;
            near_fruits[1] += plant.fruits;
        }
    }
    let side = [units(game, 0), units(game, 1)];
    let inventory = &game.inventories;
    let mut output = [0.0f32; STATE_COUNT];
    let mut at = 0usize;
    let mut push = |value: i32| {
        output[at] = value as f32;
        at += 1;
    };
    for kind in [2, 3] {
        for value in [count[kind], fruits[kind], health[kind], size[kind]] {
            push(value);
        }
    }
    for value in closer {
        push(value);
    }
    for item in ITEM_ORDER {
        push(inventory[0][item] - inventory[1][item]);
    }
    for value in [count[1], fruits[1], health[1], size[1]] {
        push(value);
    }
    for item in ITEM_ORDER {
        push(side[0].carry[item]);
    }
    for value in [
        side[0].maximum[1],
        side[0].sum[1],
        side[0].maximum[3],
        side[0].sum[3],
        side[0].maximum[2],
        side[0].sum[2],
    ] {
        push(value);
    }
    for item in ITEM_ORDER {
        push(inventory[0][item]);
    }
    for value in [
        side[0].maximum[0],
        side[0].sum[0],
        side[0].other_distance,
        side[0].own_distance,
        scores[0],
        side[0].count,
        near[0],
        near_fruits[0],
        near[1],
        near_fruits[1],
    ] {
        push(value);
    }
    for item in ITEM_ORDER {
        push(side[1].carry[item]);
    }
    for value in [
        side[1].maximum[1],
        side[1].sum[1],
        side[1].maximum[3],
        side[1].sum[3],
        side[1].maximum[2],
        side[1].sum[2],
    ] {
        push(value);
    }
    for item in ITEM_ORDER {
        push(inventory[1][item]);
    }
    for value in [
        side[1].maximum[0],
        side[1].sum[0],
        side[1].other_distance,
        side[1].own_distance,
        scores[1],
        side[1].count,
        cooldown,
        fruits.iter().sum(),
        health.iter().sum(),
        size.iter().sum(),
        game.plants.len() as i32,
        count[0],
        fruits[0],
        health[0],
        size[0],
        ripe_closer[0],
        ripe_closer[1],
        scores[0] - scores[1],
        side[0].count - side[1].count,
    ] {
        push(value);
    }
    assert_eq!(at, STATE_COUNT);
    output
}

fn map(game: &GameState) -> [f32; MAP_COUNT] {
    let nearest = |kind: PlantKind, player: usize| {
        game.plants
            .iter()
            .filter(|plant| plant.kind == kind)
            .map(|plant| manhattan(plant.cell, game.shacks[player]))
            .min()
            .unwrap_or(99)
    };
    [
        nearest(PlantKind::Apple, 0),
        nearest(PlantKind::Apple, 1),
        nearest(PlantKind::Banana, 0),
        nearest(PlantKind::Banana, 1),
        game.height,
        game.iron.len() as i32,
        nearest(PlantKind::Lemon, 0),
        nearest(PlantKind::Lemon, 1),
        nearest(PlantKind::Plum, 0),
        nearest(PlantKind::Plum, 1),
        manhattan(game.shacks[0], game.shacks[1]),
        game.walkable.len() as i32,
        game.water.len() as i32,
        game.width,
    ]
    .map(|value| value as f32)
}

pub struct History {
    states: [Option<[f32; STATE_COUNT]>; 4],
    map: Option<[f32; MAP_COUNT]>,
}

impl History {
    pub fn new() -> Self {
        Self {
            states: [None; 4],
            map: None,
        }
    }

    pub fn observe(&mut self, game: &GameState) {
        let slot = match game.turn {
            1 => Some(0),
            25 => Some(1),
            50 => Some(2),
            75 => Some(3),
            _ => None,
        };
        if let Some(slot) = slot {
            self.states[slot] = Some(state(game));
            if slot == 0 {
                self.map = Some(map(game));
            }
        }
    }

    pub fn scalars(&self) -> Option<[f32; SCALAR_COUNT]> {
        let states = [
            self.states[0]?,
            self.states[1]?,
            self.states[2]?,
            self.states[3]?,
        ];
        let map = self.map?;
        let mut output = [0.0f32; SCALAR_COUNT];
        let mut at = 0usize;
        for (start, end) in [(0, 1), (0, 3), (1, 2), (2, 3)] {
            for index in VELOCITY {
                output[at] = states[end][index] - states[start][index];
                at += 1;
            }
        }
        for value in map {
            output[at] = value;
            at += 1;
        }
        for snapshot in states {
            for value in snapshot {
                output[at] = value;
                at += 1;
            }
        }
        assert_eq!(at, SCALAR_COUNT);
        Some(output)
    }
}

fn canonical(
    cell: (i32, i32),
    width: i32,
    height: i32,
    rotate: bool,
) -> (i32, i32) {
    if rotate {
        (width - 1 - cell.0, height - 1 - cell.1)
    } else {
        cell
    }
}

fn add(grid: &mut [i16; GRID_COUNT], channel: usize, cell: (i32, i32), value: i32) {
    let index = channel * AREA + cell.1 as usize * WIDTH + cell.0 as usize;
    grid[index] += value as i16;
}

pub fn spatial(game: &GameState) -> [i16; GRID_COUNT] {
    let rotate = game.shacks[0] > game.shacks[1];
    let cell = |value| canonical(value, game.width, game.height, rotate);
    let mut grid = [0i16; GRID_COUNT];
    for y in 0..game.height {
        for x in 0..game.width {
            add(&mut grid, 0, (x, y), 1);
        }
    }
    for &value in &game.walkable {
        add(&mut grid, 1, cell(value), 1);
    }
    for &value in &game.water {
        add(&mut grid, 2, cell(value), 1);
    }
    for &value in &game.iron {
        add(&mut grid, 3, cell(value), 1);
    }
    add(&mut grid, 4, cell(game.shacks[0]), 1);
    add(&mut grid, 5, cell(game.shacks[1]), 1);
    for plant in &game.plants {
        let channel = match plant.kind {
            PlantKind::Plum => 6,
            PlantKind::Lemon => 7,
            PlantKind::Apple => 8,
            PlantKind::Banana => 9,
        };
        let target = cell(plant.cell);
        for (offset, value) in [
            (channel, 1),
            (10, plant.size),
            (11, plant.health),
            (12, plant.fruits),
            (13, plant.cooldown),
        ] {
            add(&mut grid, offset, target, value);
        }
    }
    for unit in &game.units {
        let base = if unit.player == 0 { 14 } else { 25 };
        let target = cell(unit.cell);
        for (offset, value) in [
            (0, 1),
            (1, unit.stats.movement_speed),
            (2, unit.stats.carry_capacity),
            (3, unit.stats.harvest_power),
            (4, unit.stats.chop_power),
        ] {
            add(&mut grid, base + offset, target, value);
        }
        for item in 0..6 {
            add(&mut grid, base + 5 + item, target, unit.carry[item]);
        }
    }
    grid
}

pub fn spatial_hash(grid: &[i16; GRID_COUNT]) -> u64 {
    let mut hash = 0xcbf29ce484222325u64;
    for value in grid {
        for byte in value.to_le_bytes() {
            hash ^= u64::from(byte);
            hash = hash.wrapping_mul(0x100000001b3);
        }
    }
    hash
}
