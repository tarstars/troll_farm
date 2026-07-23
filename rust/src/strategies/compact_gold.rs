//! Fixed, deployment-oriented form of `GoldElite::new()` for opening rollouts.
//!
//! All environment knobs, alternate constructors, and state that is written but
//! never read have been removed.  The emitted commands intentionally match the
//! default GoldElite continuation.

use std::collections::{HashMap, HashSet, VecDeque};

use super::Strategy;
use crate::game::engine::{training_cost, BANANA, IRON};
use crate::game::state::{Cell, GameState, Plant, Unit};

const TOTAL_TURNS: i32 = 300;
const MIN_TURNS_LEFT: i32 = 20;
const SPEC: (i32, i32, i32, i32) = (2, 2, 0, 2);

#[derive(Clone, Copy)]
pub struct CompactGold;

impl CompactGold {
    pub fn new() -> Self {
        Self
    }
}

fn manh(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

fn ortho(cell: Cell) -> [Cell; 4] {
    [
        (cell.0, cell.1 + 1),
        (cell.0 + 1, cell.1),
        (cell.0, cell.1 - 1),
        (cell.0 - 1, cell.1),
    ]
}

fn bfs(walkable: &HashSet<Cell>, source: Cell) -> HashMap<Cell, i32> {
    let mut distance = HashMap::new();
    let mut queue = VecDeque::from([source]);
    distance.insert(source, 0);
    while let Some((x, y)) = queue.pop_front() {
        let next_distance = distance[&(x, y)] + 1;
        for (dx, dy) in [(0, 1), (1, 0), (0, -1), (-1, 0)] {
            let next = (x + dx, y + dy);
            if walkable.contains(&next) && !distance.contains_key(&next) {
                distance.insert(next, next_distance);
                queue.push_back(next);
            }
        }
    }
    distance
}

fn fruit_index(kind: &str) -> Option<usize> {
    match kind {
        "PLUM" => Some(0),
        "LEMON" => Some(1),
        "APPLE" => Some(2),
        "BANANA" => Some(3),
        _ => None,
    }
}

impl Strategy for CompactGold {
    fn name(&self) -> &str {
        "compact_gold"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let shack = game.shacks[player];
        let opposing_shack = game.shacks[1 - player];
        let inventory = &game.inventories[player];
        let turns_remaining = TOTAL_TURNS - game.turn + 1;
        let mut units: Vec<&Unit> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        let unit_count = units.len() as i32;
        let chopper_count = units.iter().filter(|unit| unit.chop >= 2).count() as i32;
        let want_train = unit_count < 2 && chopper_count < 1;
        let cost = training_cost(unit_count, SPEC);
        let affordable = inventory[0] >= cost[0]
            && inventory[1] >= cost[1]
            && inventory[2] >= cost[2]
            && (game.iron.is_empty() || inventory[IRON] >= cost[IRON]);
        let train_now = want_train && affordable;
        let need_iron = !game.iron.is_empty()
            && want_train
            && inventory[IRON] < cost[IRON]
            && inventory[0] >= cost[0]
            && inventory[1] >= cost[1]
            && inventory[2] >= cost[2];
        let need_fruit = [
            inventory[0] < cost[0],
            inventory[1] < cost[1],
            inventory[2] < cost[2],
        ];

        let liquidation = turns_remaining <= 34;
        let base_trees = game
            .plants
            .iter()
            .filter(|plant| manh(plant.pos(), shack) <= 3)
            .count();
        let mut protected_seeds = HashSet::new();
        if !liquidation {
            let mut bananas: Vec<&Plant> = game
                .plants
                .iter()
                .filter(|plant| plant.plant_type == "BANANA" && manh(plant.pos(), shack) <= 3)
                .collect();
            bananas.sort_by_key(|plant| {
                (
                    -plant.size,
                    -plant.fruits,
                    manh(plant.pos(), shack),
                    plant.pos(),
                )
            });
            protected_seeds.extend(bananas.into_iter().take(2).map(Plant::pos));
        }
        let fellable = |plant: &Plant| {
            !protected_seeds.contains(&plant.pos())
                && if liquidation {
                    plant.size >= 1
                } else {
                    plant.size >= 2
                }
        };
        let own_half = |plant: &Plant| {
            liquidation || manh(plant.pos(), shack) <= manh(plant.pos(), opposing_shack)
        };
        let within_roam = |plant: &Plant| liquidation || manh(plant.pos(), shack) <= 10;

        let mut reserved = HashSet::new();
        let mut commands = HashMap::new();
        for unit in &units {
            let distance = bfs(&game.walkable, unit.pos());
            let bank = |unit: &Unit| {
                if manh(unit.pos(), shack) == 1 {
                    format!("DROP {}", unit.id)
                } else {
                    let cell = ortho(shack)
                        .into_iter()
                        .filter(|cell| game.walkable.contains(cell))
                        .min_by_key(|cell| distance.get(cell).copied().unwrap_or(1 << 30))
                        .unwrap_or(shack);
                    format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                }
            };
            let park = |unit: &Unit| {
                let cell = ortho(shack)
                    .into_iter()
                    .filter(|cell| game.walkable.contains(cell))
                    .min_by_key(|cell| distance.get(cell).copied().unwrap_or(1 << 30))
                    .unwrap_or(shack);
                format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
            };

            if unit.total() > 0 {
                let home_distance = ortho(shack)
                    .iter()
                    .filter(|cell| game.walkable.contains(*cell))
                    .filter_map(|cell| distance.get(cell))
                    .min()
                    .copied()
                    .unwrap_or(i32::MAX / 2);
                let bank_eta = (home_distance + unit.ms - 1) / unit.ms.max(1) + 1;
                if turns_remaining <= bank_eta + 1 {
                    commands.insert(unit.id, bank(unit));
                    continue;
                }
            }

            let nearest_fell = |require_space: bool| {
                if require_space && unit.free() == 0 {
                    return None;
                }
                game.plants
                    .iter()
                    .filter(|plant| fellable(plant))
                    .filter(|plant| own_half(plant) && within_roam(plant))
                    .filter(|plant| {
                        distance.contains_key(&plant.pos()) && !reserved.contains(&plant.pos())
                    })
                    .min_by_key(|plant| {
                        let travel = (distance[&plant.pos()] + unit.ms - 1) / unit.ms.max(1);
                        let chop = (plant.health + unit.chop.max(1) - 1) / unit.chop.max(1);
                        (0, travel + chop, plant.pos())
                    })
                    .map(Plant::pos)
            };

            if unit.chop >= 2 && unit.hp == 0 {
                if unit.free() == 0 {
                    commands.insert(unit.id, bank(unit));
                    continue;
                }
                if game
                    .plants
                    .iter()
                    .find(|plant| plant.pos() == unit.pos())
                    .is_some_and(|plant| unit.chop > 0 && fellable(plant))
                {
                    commands.insert(unit.id, format!("CHOP {}", unit.id));
                    reserved.insert(unit.pos());
                    continue;
                }
                if let Some(cell) = nearest_fell(false) {
                    reserved.insert(cell);
                    commands.insert(unit.id, format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
                    continue;
                }
                if let Some(cell) = game
                    .plants
                    .iter()
                    .filter(|plant| {
                        plant.size >= 1
                            && distance.contains_key(&plant.pos())
                            && !reserved.contains(&plant.pos())
                    })
                    .min_by_key(|plant| {
                        let travel = (distance[&plant.pos()] + unit.ms - 1) / unit.ms.max(1);
                        let chop = (plant.health + unit.chop.max(1) - 1) / unit.chop.max(1);
                        (travel + chop, plant.pos())
                    })
                    .map(Plant::pos)
                {
                    let command = if unit.pos() == cell {
                        format!("CHOP {}", unit.id)
                    } else {
                        reserved.insert(cell);
                        format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                    };
                    commands.insert(unit.id, command);
                    continue;
                }
                commands.insert(
                    unit.id,
                    if unit.total() > 0 {
                        bank(unit)
                    } else {
                        park(unit)
                    },
                );
                continue;
            }

            let free_base = || {
                game.walkable
                    .iter()
                    .filter(|cell| manh(**cell, shack) <= 3 && distance.contains_key(*cell))
                    .filter(|cell| !game.plants.iter().any(|plant| plant.pos() == **cell))
                    .filter(|cell| {
                        !units
                            .iter()
                            .any(|other| other.id != unit.id && other.pos() == **cell)
                    })
                    .filter(|cell| !reserved.contains(*cell))
                    .min_by_key(|cell| {
                        let near_water = game.water.iter().any(|water| manh(*water, **cell) == 1);
                        (distance[*cell] + if near_water { 0 } else { 2 }, **cell)
                    })
                    .copied()
            };
            if unit.carry[BANANA] > 0 && base_trees < 12 {
                if let Some(cell) = free_base() {
                    reserved.insert(cell);
                    commands.insert(
                        unit.id,
                        if unit.pos() == cell {
                            format!("PLANT {} BANANA", unit.id)
                        } else {
                            format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                        },
                    );
                    continue;
                }
            }
            if unit.free() == 0 {
                commands.insert(unit.id, bank(unit));
                continue;
            }
            if let Some(plant) = game.plants.iter().find(|plant| plant.pos() == unit.pos()) {
                let wanted = if want_train {
                    fruit_index(&plant.plant_type)
                        .is_some_and(|index| index < 3 && need_fruit[index])
                } else {
                    plant.plant_type == "BANANA"
                        || (plant.plant_type == "APPLE"
                            && game
                                .water
                                .iter()
                                .any(|water| manh(*water, plant.pos()) == 1))
                };
                if plant.fruits > 0 && unit.hp > 0 && unit.free() > 0 && wanted {
                    commands.insert(unit.id, format!("HARVEST {}", unit.id));
                    reserved.insert(unit.pos());
                    continue;
                }
            }
            if want_train {
                if need_iron && unit.chop > 0 {
                    if game.iron.iter().any(|iron| manh(unit.pos(), *iron) == 1) {
                        commands.insert(unit.id, format!("MINE {}", unit.id));
                        continue;
                    }
                    if let Some(cell) = game
                        .iron
                        .iter()
                        .flat_map(|iron| ortho(*iron))
                        .filter(|cell| distance.contains_key(cell) && !reserved.contains(cell))
                        .min_by_key(|cell| (distance[cell], *cell))
                    {
                        reserved.insert(cell);
                        commands.insert(unit.id, format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
                        continue;
                    }
                }
                if let Some(cell) = game
                    .plants
                    .iter()
                    .filter(|plant| {
                        plant.fruits > 0
                            && distance.contains_key(&plant.pos())
                            && !reserved.contains(&plant.pos())
                    })
                    .filter(|plant| {
                        fruit_index(&plant.plant_type)
                            .is_some_and(|index| index < 3 && need_fruit[index])
                    })
                    .min_by_key(|plant| (distance[&plant.pos()], plant.pos()))
                    .map(Plant::pos)
                {
                    reserved.insert(cell);
                    commands.insert(unit.id, format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
                    continue;
                }
            }
            if base_trees < 12 {
                if manh(unit.pos(), shack) == 1 && inventory[BANANA] > 0 && unit.free() > 0 {
                    commands.insert(unit.id, format!("PICK {} BANANA", unit.id));
                    continue;
                }
                if inventory[BANANA] > 0 {
                    commands.insert(unit.id, park(unit));
                    continue;
                }
                if let Some(cell) = game
                    .plants
                    .iter()
                    .filter(|plant| {
                        plant.fruits > 0
                            && distance.contains_key(&plant.pos())
                            && !reserved.contains(&plant.pos())
                    })
                    .filter(|plant| {
                        plant.plant_type == "BANANA"
                            || (plant.plant_type == "APPLE"
                                && game
                                    .water
                                    .iter()
                                    .any(|water| manh(*water, plant.pos()) == 1))
                    })
                    .min_by_key(|plant| (distance[&plant.pos()], plant.pos()))
                    .map(Plant::pos)
                {
                    reserved.insert(cell);
                    commands.insert(unit.id, format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
                    continue;
                }
            }
            if unit.chop > 0 {
                if game
                    .plants
                    .iter()
                    .find(|plant| plant.pos() == unit.pos())
                    .is_some_and(fellable)
                {
                    commands.insert(unit.id, format!("CHOP {}", unit.id));
                    reserved.insert(unit.pos());
                    continue;
                }
                if let Some(cell) = nearest_fell(true) {
                    reserved.insert(cell);
                    commands.insert(unit.id, format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
                    continue;
                }
                if unit.free() > 0 {
                    if let Some(cell) = game
                        .plants
                        .iter()
                        .filter(|plant| {
                            plant.size >= 1
                                && distance.contains_key(&plant.pos())
                                && !reserved.contains(&plant.pos())
                        })
                        .min_by_key(|plant| {
                            let travel = (distance[&plant.pos()] + unit.ms - 1) / unit.ms.max(1);
                            let chop = (plant.health + unit.chop.max(1) - 1) / unit.chop.max(1);
                            (travel + chop, plant.pos())
                        })
                        .map(Plant::pos)
                    {
                        let command = if unit.pos() == cell {
                            format!("CHOP {}", unit.id)
                        } else {
                            reserved.insert(cell);
                            format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
                        };
                        commands.insert(unit.id, command);
                        continue;
                    }
                }
            }
            commands.insert(
                unit.id,
                if unit.total() > 0 {
                    bank(unit)
                } else {
                    park(unit)
                },
            );
        }

        let mut ids: Vec<_> = commands.keys().copied().collect();
        ids.sort_unstable();
        let mut actions: Vec<_> = ids
            .into_iter()
            .map(|id| commands.remove(&id).expect("known unit command"))
            .collect();
        if train_now
            && TOTAL_TURNS - game.turn > MIN_TURNS_LEFT
            && !units.iter().any(|unit| unit.pos() == shack)
        {
            actions.push(format!("TRAIN {} {} {} {}", SPEC.0, SPEC.1, SPEC.2, SPEC.3));
        }
        if actions.is_empty() {
            actions.push("WAIT".to_string());
        }
        actions
    }
}
