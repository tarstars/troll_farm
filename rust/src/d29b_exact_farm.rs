// Source-compact specialization of OwnershipAwareFarm::new() for normalized
// live GameState input. Keep command behavior exact; omit research telemetry,
// the redundant GoldElite shadow, and write-only target memory.

use std::cell::RefCell;
use std::cmp::Ordering;
use std::collections::BTreeSet;

use crate::game::nav::{bfs_distances, manhattan, ortho_neighbors};
use crate::game::types::{Cell, GameState, Plant, PlantKind, Unit, BANANA};

const TOTAL_TURNS: i32 = 300;

#[derive(Default)]
struct History {
    initialized: bool,
    previous_plants: BTreeSet<Cell>,
    own_plant_attempts: BTreeSet<Cell>,
    opponent_crops: BTreeSet<Cell>,
}

#[derive(Clone, Copy)]
struct CycleValue {
    cell: Cell,
    own_wood: i32,
    denied_wood: i32,
    turns: i32,
}

impl CycleValue {
    fn rate_cmp(self, other: Self) -> Ordering {
        ((self.own_wood + self.denied_wood) * other.turns)
            .cmp(&((other.own_wood + other.denied_wood) * self.turns))
            .then_with(|| other.cell.cmp(&self.cell))
    }
}

pub struct ExactFarm {
    history: RefCell<History>,
}

impl ExactFarm {
    pub fn new() -> Self {
        Self {
            history: RefCell::new(History::default()),
        }
    }

    fn reconcile_provenance(&self, game: &GameState) {
        let current: BTreeSet<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .map(|plant| plant.cell)
            .collect();
        let mut history = self.history.borrow_mut();
        if game.turn == 1 {
            *history = History::default();
        }
        if history.initialized {
            let appeared: Vec<_> = current
                .difference(&history.previous_plants)
                .copied()
                .collect();
            for cell in appeared {
                if !history.own_plant_attempts.contains(&cell) {
                    history.opponent_crops.insert(cell);
                }
            }
            history.opponent_crops.retain(|cell| current.contains(cell));
        } else {
            history.initialized = true;
        }
        history.previous_plants = current;
        history.own_plant_attempts.clear();
    }

    fn remember_plant_attempts(&self, game: &GameState, commands: &[String]) {
        let mut attempts = Vec::new();
        for command in commands {
            let mut fields = command.split_whitespace();
            if fields.next() != Some("PLANT") {
                continue;
            }
            let Some(id) = fields.next().and_then(|value| value.parse::<i32>().ok()) else {
                continue;
            };
            if let Some(unit) = game
                .units
                .iter()
                .find(|unit| unit.id == id && unit.player == 0)
            {
                attempts.push(unit.cell);
            }
        }
        self.history
            .borrow_mut()
            .own_plant_attempts
            .extend(attempts);
    }

    fn ceil_div(value: i32, divisor: i32) -> i32 {
        (value + divisor.max(1) - 1) / divisor.max(1)
    }

    fn move_to(unit: &Unit, cell: Cell) -> String {
        format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
    }

    fn act(name: &str, unit: &Unit) -> String {
        format!("{} {}", name, unit.id)
    }

    fn home_distance(game: &GameState, cell: Cell) -> Option<i32> {
        let distances = bfs_distances(&game.walkable, &[cell]);
        ortho_neighbors(game.shacks[0])
            .into_iter()
            .filter(|drop| game.walkable.contains(drop))
            .filter_map(|drop| distances.get(&drop).copied())
            .min()
    }

    fn cycle_value(
        game: &GameState,
        unit: &Unit,
        plant: &Plant,
        denial: bool,
    ) -> Option<CycleValue> {
        let distance = bfs_distances(&game.walkable, &[unit.cell]);
        let travel = Self::ceil_div(*distance.get(&plant.cell)?, unit.stats.movement_speed);
        let chop_turns = Self::ceil_div(plant.health, unit.stats.chop_power);
        let home = Self::ceil_div(
            Self::home_distance(game, plant.cell)?,
            unit.stats.movement_speed,
        );
        let turns = travel + chop_turns + home + 1;
        if turns > TOTAL_TURNS - game.turn + 1 {
            return None;
        }
        let own_wood = plant.size.min(unit.free_capacity()).max(0);
        if own_wood == 0 {
            return None;
        }
        let our_completion = travel + chop_turns;
        let denied_wood = if denial {
            game.units
                .iter()
                .filter(|enemy| {
                    enemy.player != 0
                        && enemy.stats.chop_power > 0
                        && enemy.free_capacity() > 0
                })
                .filter_map(|enemy| {
                    let distance = bfs_distances(&game.walkable, &[enemy.cell]);
                    let travel = Self::ceil_div(
                        *distance.get(&plant.cell)?,
                        enemy.stats.movement_speed,
                    );
                    let completion =
                        travel + Self::ceil_div(plant.health, enemy.stats.chop_power);
                    Some((completion, enemy.id, enemy.free_capacity()))
                })
                .min_by_key(|(completion, id, _)| (*completion, *id))
                .filter(|(completion, _, _)| our_completion < *completion)
                .map_or(0, |(_, _, free)| plant.size.min(free).max(0))
        } else {
            0
        };
        Some(CycleValue {
            cell: plant.cell,
            own_wood,
            denied_wood,
            turns,
        })
    }

    fn base_tree_target<'a>(game: &'a GameState, unit: &Unit, command: &str) -> Option<&'a Plant> {
        let fields: Vec<_> = command.split_whitespace().collect();
        let cell = match fields.as_slice() {
            ["CHOP", id] if id.parse::<i32>().ok() == Some(unit.id) => unit.cell,
            ["MOVE", id, x, y]
                if id.parse::<i32>().ok() == Some(unit.id)
                    && x.parse::<i32>().is_ok()
                    && y.parse::<i32>().is_ok() =>
            {
                (x.parse().ok()?, y.parse().ok()?)
            }
            _ => return None,
        };
        game.plants.iter().find(|plant| plant.cell == cell)
    }

    fn override_chopper(&self, game: &GameState, commands: &mut [String]) {
        let opponent_crops = self.history.borrow().opponent_crops.clone();
        if opponent_crops.is_empty() {
            return;
        }
        for command in commands {
            let Some(id) = command
                .split_whitespace()
                .nth(1)
                .and_then(|value| value.parse::<i32>().ok())
            else {
                continue;
            };
            let Some(unit) = game.units.iter().find(|unit| {
                unit.id == id
                    && unit.player == 0
                    && unit.stats.chop_power >= 2
                    && unit.stats.harvest_power == 0
                    && unit.free_capacity() > 0
            }) else {
                continue;
            };
            let Some(base_plant) = Self::base_tree_target(game, unit, command) else {
                continue;
            };
            let Some(base) = Self::cycle_value(game, unit, base_plant, false) else {
                continue;
            };
            let best = game
                .plants
                .iter()
                .filter(|plant| {
                    plant.size >= 2 && opponent_crops.contains(&plant.cell)
                })
                .filter_map(|plant| Self::cycle_value(game, unit, plant, true))
                .max_by(|left, right| left.rate_cmp(*right));
            let Some(best) = best.filter(|candidate| candidate.rate_cmp(base).is_gt()) else {
                continue;
            };
            if best.cell == base.cell {
                continue;
            }
            *command = if unit.cell == best.cell {
                Self::act("CHOP", unit)
            } else {
                Self::move_to(unit, best.cell)
            };
            return;
        }
    }

    fn base_commands(&self, game: &GameState) -> Vec<String> {
        let shack = game.shacks[0];
        let opponent_shack = game.shacks[1];
        let inventory = &game.inventories[0];
        let turns_remaining = TOTAL_TURNS - game.turn + 1;
        let mut units: Vec<_> = game.units.iter().filter(|unit| unit.player == 0).collect();
        units.sort_by_key(|unit| unit.id);
        let liquidation = turns_remaining <= 34;
        let base_trees = game
            .plants
            .iter()
            .filter(|plant| manhattan(plant.cell, shack) <= 3)
            .count();
        let mut seed_cells = BTreeSet::new();
        if !liquidation {
            let mut bananas: Vec<_> = game
                .plants
                .iter()
                .filter(|plant| {
                    plant.kind == PlantKind::Banana && manhattan(plant.cell, shack) <= 3
                })
                .collect();
            bananas.sort_by_key(|plant| {
                (
                    -plant.size,
                    -plant.fruits,
                    manhattan(plant.cell, shack),
                    plant.cell,
                )
            });
            seed_cells.extend(bananas.into_iter().take(2).map(|plant| plant.cell));
        }
        let fell_ok = |plant: &Plant| {
            !seed_cells.contains(&plant.cell)
                && plant.size >= if liquidation { 1 } else { 2 }
        };
        let own_half = |plant: &Plant| {
            liquidation
                || manhattan(plant.cell, shack) <= manhattan(plant.cell, opponent_shack)
        };
        let within_roam = |plant: &Plant| {
            liquidation || manhattan(plant.cell, shack) <= 10
        };
        let mut reserved = BTreeSet::new();
        let mut actions = Vec::new();

        for unit in &units {
            let distance = bfs_distances(&game.walkable, &[unit.cell]);
            let bank = || {
                if manhattan(unit.cell, shack) == 1 {
                    Self::act("DROP", unit)
                } else {
                    let cell = ortho_neighbors(shack)
                        .into_iter()
                        .filter(|cell| game.walkable.contains(cell))
                        .min_by_key(|cell| distance.get(cell).copied().unwrap_or(1 << 30))
                        .unwrap_or(shack);
                    Self::move_to(unit, cell)
                }
            };
            let park = || {
                let cell = ortho_neighbors(shack)
                    .into_iter()
                    .filter(|cell| game.walkable.contains(cell))
                    .min_by_key(|cell| distance.get(cell).copied().unwrap_or(1 << 30))
                    .unwrap_or(shack);
                Self::move_to(unit, cell)
            };
            if unit.total_carried() > 0 {
                let home = ortho_neighbors(shack)
                    .iter()
                    .filter(|cell| game.walkable.contains(*cell))
                    .filter_map(|cell| distance.get(cell))
                    .min()
                    .copied()
                    .unwrap_or(i32::MAX / 2);
                let eta = Self::ceil_div(home, unit.stats.movement_speed) + 1;
                if turns_remaining <= eta + 1 {
                    actions.push(bank());
                    continue;
                }
            }
            let nearest_fell = |free_needed: bool, reserved: &BTreeSet<Cell>| {
                if free_needed && unit.free_capacity() == 0 {
                    return None;
                }
                game.plants
                    .iter()
                    .filter(|plant| fell_ok(plant))
                    .filter(|plant| own_half(plant) && within_roam(plant))
                    .filter(|plant| {
                        distance.contains_key(&plant.cell) && !reserved.contains(&plant.cell)
                    })
                    .min_by_key(|plant| {
                        let steps = Self::ceil_div(
                            distance[&plant.cell],
                            unit.stats.movement_speed,
                        );
                        let chop = Self::ceil_div(plant.health, unit.stats.chop_power);
                        (steps + chop, plant.cell)
                    })
                    .map(|plant| plant.cell)
            };
            let is_chopper =
                unit.stats.chop_power >= 2 && unit.stats.harvest_power == 0;
            if is_chopper {
                if unit.free_capacity() == 0 {
                    actions.push(bank());
                    continue;
                }
                if let Some(plant) = game.plants.iter().find(|plant| plant.cell == unit.cell) {
                    if unit.stats.chop_power > 0 && fell_ok(plant) {
                        actions.push(Self::act("CHOP", unit));
                        reserved.insert(unit.cell);
                        continue;
                    }
                }
                if let Some(cell) = nearest_fell(false, &reserved) {
                    reserved.insert(cell);
                    actions.push(Self::move_to(unit, cell));
                    continue;
                }
                if let Some(cell) = game
                    .plants
                    .iter()
                    .filter(|plant| {
                        plant.size >= 1
                            && distance.contains_key(&plant.cell)
                            && !reserved.contains(&plant.cell)
                    })
                    .min_by_key(|plant| {
                        let steps = Self::ceil_div(
                            distance[&plant.cell],
                            unit.stats.movement_speed,
                        );
                        let chop = Self::ceil_div(plant.health, unit.stats.chop_power);
                        (steps + chop, plant.cell)
                    })
                    .map(|plant| plant.cell)
                {
                    if unit.cell == cell {
                        actions.push(Self::act("CHOP", unit));
                    } else {
                        reserved.insert(cell);
                        actions.push(Self::move_to(unit, cell));
                    }
                    continue;
                }
                actions.push(if unit.total_carried() > 0 { bank() } else { park() });
                continue;
            }

            let free_base = || {
                game.walkable
                    .iter()
                    .filter(|cell| {
                        manhattan(**cell, shack) <= 3 && distance.contains_key(*cell)
                    })
                    .filter(|cell| !game.plants.iter().any(|plant| plant.cell == **cell))
                    .filter(|cell| {
                        !units
                            .iter()
                            .any(|other| other.id != unit.id && other.cell == **cell)
                    })
                    .filter(|cell| !reserved.contains(*cell))
                    .min_by_key(|cell| {
                        let wet = game
                            .water
                            .iter()
                            .any(|water| manhattan(*water, **cell) == 1);
                        (distance[*cell] + if wet { 0 } else { 2 }, **cell)
                    })
                    .copied()
            };
            if unit.carry[BANANA] > 0 && base_trees < 12 {
                if let Some(cell) = free_base() {
                    reserved.insert(cell);
                    if unit.cell == cell {
                        actions.push(format!("PLANT {} BANANA", unit.id));
                    } else {
                        actions.push(Self::move_to(unit, cell));
                    }
                    continue;
                }
            }
            if unit.free_capacity() == 0 {
                actions.push(bank());
                continue;
            }
            if let Some(plant) = game.plants.iter().find(|plant| plant.cell == unit.cell) {
                if plant.fruits > 0
                    && unit.stats.harvest_power > 0
                    && unit.free_capacity() > 0
                {
                    let wanted = plant.kind == PlantKind::Banana
                        || (plant.kind == PlantKind::Apple
                            && game
                                .water
                                .iter()
                                .any(|water| manhattan(*water, plant.cell) == 1));
                    if wanted {
                        actions.push(Self::act("HARVEST", unit));
                        reserved.insert(unit.cell);
                        continue;
                    }
                }
            }
            if base_trees < 12 {
                if manhattan(unit.cell, shack) == 1
                    && inventory[BANANA] > 0
                    && unit.free_capacity() > 0
                {
                    actions.push(format!("PICK {} BANANA", unit.id));
                    continue;
                }
                if inventory[BANANA] > 0 {
                    actions.push(park());
                    continue;
                }
                if let Some(cell) = game
                    .plants
                    .iter()
                    .filter(|plant| {
                        plant.fruits > 0
                            && distance.contains_key(&plant.cell)
                            && !reserved.contains(&plant.cell)
                            && (plant.kind == PlantKind::Banana
                                || (plant.kind == PlantKind::Apple
                                    && game
                                        .water
                                        .iter()
                                        .any(|water| manhattan(*water, plant.cell) == 1)))
                    })
                    .min_by_key(|plant| (distance[&plant.cell], plant.cell))
                    .map(|plant| plant.cell)
                {
                    reserved.insert(cell);
                    actions.push(Self::move_to(unit, cell));
                    continue;
                }
            }
            if unit.stats.chop_power > 0 {
                if let Some(plant) = game.plants.iter().find(|plant| plant.cell == unit.cell) {
                    if fell_ok(plant) {
                        actions.push(Self::act("CHOP", unit));
                        reserved.insert(unit.cell);
                        continue;
                    }
                }
                if let Some(cell) = nearest_fell(true, &reserved) {
                    reserved.insert(cell);
                    actions.push(Self::move_to(unit, cell));
                    continue;
                }
                if unit.free_capacity() > 0 {
                    if let Some(cell) = game
                        .plants
                        .iter()
                        .filter(|plant| {
                            plant.size >= 1
                                && distance.contains_key(&plant.cell)
                                && !reserved.contains(&plant.cell)
                        })
                        .min_by_key(|plant| {
                            let steps = Self::ceil_div(
                                distance[&plant.cell],
                                unit.stats.movement_speed,
                            );
                            let chop =
                                Self::ceil_div(plant.health, unit.stats.chop_power);
                            (steps + chop, plant.cell)
                        })
                        .map(|plant| plant.cell)
                    {
                        if unit.cell == cell {
                            actions.push(Self::act("CHOP", unit));
                        } else {
                            reserved.insert(cell);
                            actions.push(Self::move_to(unit, cell));
                        }
                        continue;
                    }
                }
            }
            actions.push(if unit.total_carried() > 0 { bank() } else { park() });
        }

        actions
    }

    pub fn commands(&self, game: &GameState) -> Vec<String> {
        self.reconcile_provenance(game);
        let mut commands = self.base_commands(game);
        self.override_chopper(game, &mut commands);
        self.remember_plant_attempts(game, &commands);
        commands
    }
}
