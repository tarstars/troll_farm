//! Submission-oriented port of the frozen `NorxondorThreeWorkerSilver` research policy.
//!
//! This module deliberately uses the verified standalone protocol types.  Its behavior is gated
//! against the library research strategy before any controlled field game.

use crate::game::rules::{training_cost, TOTAL_TURNS};
use crate::game::types::{Cell, GameState, PlantKind, Unit, APPLE, IRON, LEMON, PLUM};
use std::collections::{BTreeMap, BTreeSet, VecDeque};

type Spec = (i32, i32, i32, i32);

const MIN_TURNS_LEFT: i32 = 20;
const MAX_TROLLS: usize = 4;
const MAX_ORCHARD: usize = 2;
const CHOPPER_SPEC: Spec = (1, 2, 1, 2);
const N_CHOPPERS: i32 = 2;
const HARVESTERS: [Spec; 3] = [(2, 2, 2, 0), (1, 2, 2, 0), (1, 1, 1, 0)];
const BASES: [Spec; 4] = [(2, 2, 1, 1), (2, 3, 1, 2), (2, 3, 0, 3), (2, 4, 0, 3)];
const CAPS: [Spec; 4] = [(3, 3, 2, 2), (4, 5, 2, 2), (3, 3, 1, 3), (3, 4, 1, 3)];

fn envi(name: &str, default: i32) -> i32 {
    std::env::var(name)
        .ok()
        .and_then(|value| value.parse().ok())
        .unwrap_or(default)
}

fn env_spec(name: &str, default: Spec) -> Spec {
    if let Ok(value) = std::env::var(name) {
        let parts: Vec<i32> = value
            .split(',')
            .filter_map(|part| part.trim().parse().ok())
            .collect();
        if parts.len() == 4 {
            return (parts[0], parts[1], parts[2], parts[3]);
        }
    }
    default
}

fn manhattan(left: Cell, right: Cell) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn ortho(cell: Cell) -> [Cell; 4] {
    [
        (cell.0, cell.1 + 1),
        (cell.0 + 1, cell.1),
        (cell.0, cell.1 - 1),
        (cell.0 - 1, cell.1),
    ]
}

fn bfs(game: &GameState, source: Cell) -> BTreeMap<Cell, i32> {
    let mut distance = BTreeMap::from([(source, 0)]);
    let mut queue = VecDeque::from([source]);
    while let Some((x, y)) = queue.pop_front() {
        let next_distance = distance[&(x, y)] + 1;
        for (dx, dy) in [(0, 1), (1, 0), (0, -1), (-1, 0)] {
            let cell = (x + dx, y + dy);
            if game.walkable.contains(&cell) && !distance.contains_key(&cell) {
                distance.insert(cell, next_distance);
                queue.push_back(cell);
            }
        }
    }
    distance
}

fn affordable(inventory: &[i32; 6], cost: &[i32; 6], have_iron: bool) -> bool {
    inventory[PLUM] >= cost[PLUM]
        && inventory[LEMON] >= cost[LEMON]
        && inventory[APPLE] >= cost[APPLE]
        && (!have_iron || inventory[IRON] >= cost[IRON])
}

fn affordable_fruit(inventory: &[i32; 6], cost: &[i32; 6]) -> bool {
    inventory[PLUM] >= cost[PLUM]
        && inventory[LEMON] >= cost[LEMON]
        && inventory[APPLE] >= cost[APPLE]
}

fn stage_base(workers: i32) -> Option<Spec> {
    if (1..=4).contains(&workers) {
        Some(BASES[(workers - 1) as usize])
    } else {
        None
    }
}

fn integer_sqrt(value: i32) -> i32 {
    let mut root = 0;
    while (root + 1) * (root + 1) <= value.max(0) {
        root += 1;
    }
    root
}

fn proposed_spec(workers: i32, inventory: &[i32; 6], have_iron: bool) -> Option<Spec> {
    if !(1..=4).contains(&workers) {
        return None;
    }
    let index = (workers - 1) as usize;
    let base = BASES[index];
    if !affordable(inventory, &training_cost(workers, base), have_iron) {
        return None;
    }
    let cap = CAPS[index];
    Some((
        integer_sqrt(inventory[PLUM] - workers).min(cap.0),
        integer_sqrt(inventory[LEMON] - workers).min(cap.1),
        integer_sqrt(inventory[APPLE] - workers).min(cap.2),
        if have_iron {
            integer_sqrt(inventory[IRON] - workers).min(cap.3)
        } else {
            cap.3
        },
    ))
}

struct SilverContinuation {
    memory: BTreeMap<i32, Cell>,
}

impl SilverContinuation {
    fn new() -> Self {
        Self {
            memory: BTreeMap::new(),
        }
    }

    fn decide(&mut self, game: &GameState, player: usize) -> Vec<String> {
        if game.turn == 1 {
            self.memory.clear();
        }
        let shack = game.shacks[player];
        let inventory = &game.inventories[player];
        let have_iron = !game.iron.is_empty();
        let mut units: Vec<&Unit> = game
            .units
            .iter()
            .filter(|unit| unit.player == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        let workers = units.len() as i32;

        let chopper_spec = env_spec("BOSS_CHOP", CHOPPER_SPEC);
        let want_chopper = (units
            .iter()
            .filter(|unit| unit.stats.chop_power >= 2)
            .count() as i32)
            < envi("BOSS_NCHOP", N_CHOPPERS);
        let train_now = if want_chopper
            && affordable(inventory, &training_cost(workers, chopper_spec), have_iron)
        {
            Some(chopper_spec)
        } else {
            HARVESTERS
                .iter()
                .copied()
                .find(|spec| affordable(inventory, &training_cost(workers, *spec), have_iron))
        };
        let need_iron = have_iron
            && want_chopper
            && inventory[IRON] < training_cost(workers, chopper_spec)[IRON]
            && affordable_fruit(inventory, &training_cost(workers, chopper_spec));

        let has_real_chopper = units.iter().any(|unit| unit.stats.chop_power >= 2);
        let bootstrap_id = if has_real_chopper {
            None
        } else {
            units
                .iter()
                .filter(|unit| unit.stats.chop_power >= 1)
                .max_by_key(|unit| (unit.stats.carry_capacity, -unit.id))
                .map(|unit| unit.id)
        };
        let is_chopper = |unit: &Unit| unit.stats.chop_power >= 2 || Some(unit.id) == bootstrap_id;

        let orchard = game
            .plants
            .iter()
            .filter(|plant| plant.kind == PlantKind::Plum && manhattan(plant.cell, shack) <= 3)
            .count();
        let need_index = (0..3usize).min_by_key(|index| inventory[*index]).unwrap();
        let need_kind = [PlantKind::Plum, PlantKind::Lemon, PlantKind::Apple][need_index];

        let mut reserved = BTreeSet::new();
        let mut command_by_id = BTreeMap::new();
        let mut actions = Vec::new();
        if game.turn == 1 {
            actions.push("MSG Eat your vegetables!".to_string());
        }

        for unit in &units {
            let chopper = is_chopper(unit);
            let distance = bfs(game, unit.cell);

            if unit.free_capacity() == 0 {
                self.memory.remove(&unit.id);
                if manhattan(unit.cell, shack) == 1 {
                    let on_tree = game.plants.iter().any(|plant| plant.cell == unit.cell);
                    if !chopper
                        && !on_tree
                        && orchard < MAX_ORCHARD
                        && unit.carry[PLUM] > 0
                        && game.walkable.contains(&unit.cell)
                    {
                        command_by_id.insert(unit.id, format!("PLANT {} PLUM", unit.id));
                    } else {
                        command_by_id.insert(unit.id, format!("DROP {}", unit.id));
                    }
                } else {
                    command_by_id
                        .insert(unit.id, format!("MOVE {} {} {}", unit.id, shack.0, shack.1));
                }
                continue;
            }

            if let Some(plant) = game.plants.iter().find(|plant| plant.cell == unit.cell) {
                if chopper && unit.stats.chop_power > 0 {
                    command_by_id.insert(unit.id, format!("CHOP {}", unit.id));
                    reserved.insert(unit.cell);
                    continue;
                }
                if plant.fruits > 0 && unit.stats.harvest_power > 0 && unit.free_capacity() > 0 {
                    command_by_id.insert(unit.id, format!("HARVEST {}", unit.id));
                    reserved.insert(unit.cell);
                    continue;
                }
            }

            if need_iron
                && chopper
                && unit.stats.chop_power > 0
                && game
                    .iron
                    .iter()
                    .any(|cell| manhattan(unit.cell, *cell) == 1)
            {
                command_by_id.insert(unit.id, format!("MINE {}", unit.id));
                continue;
            }

            let target = if chopper {
                let iron_cell = if need_iron {
                    game.iron
                        .iter()
                        .flat_map(|cell| ortho(*cell))
                        .filter(|cell| distance.contains_key(cell) && !reserved.contains(cell))
                        .min_by_key(|cell| (distance[cell], *cell))
                } else {
                    None
                };
                iron_cell.or_else(|| {
                    let opponent_shack = game.shacks[1 - player];
                    game.plants
                        .iter()
                        .filter(|plant| {
                            distance.contains_key(&plant.cell) && !reserved.contains(&plant.cell)
                        })
                        .min_by_key(|plant| {
                            (
                                distance[&plant.cell] + manhattan(plant.cell, opponent_shack)
                                    - 3 * plant.size,
                                -plant.size,
                                plant.cell,
                            )
                        })
                        .map(|plant| plant.cell)
                })
            } else {
                let sticky = self.memory.get(&unit.id).copied().filter(|cell| {
                    game.plants
                        .iter()
                        .any(|plant| plant.cell == *cell && plant.fruits > 0)
                        && !reserved.contains(cell)
                });
                let nearest_ripe = |kind: Option<PlantKind>| {
                    game.plants
                        .iter()
                        .filter(|plant| {
                            plant.fruits > 0
                                && !reserved.contains(&plant.cell)
                                && distance.contains_key(&plant.cell)
                        })
                        .filter(|plant| kind.map_or(true, |value| plant.kind == value))
                        .min_by_key(|plant| (distance[&plant.cell], plant.cell))
                        .map(|plant| plant.cell)
                };
                sticky
                    .or_else(|| nearest_ripe(Some(need_kind)))
                    .or_else(|| nearest_ripe(None))
            };

            match target {
                Some(cell) => {
                    reserved.insert(cell);
                    if !chopper {
                        self.memory.insert(unit.id, cell);
                    }
                    command_by_id
                        .insert(unit.id, format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
                }
                None => {
                    command_by_id
                        .insert(unit.id, format!("MOVE {} {} {}", unit.id, shack.0, shack.1));
                }
            }
        }

        actions.extend(command_by_id.into_values());
        if let Some(spec) = train_now {
            if units.len() < envi("BOSS_MAX", MAX_TROLLS as i32) as usize
                && TOTAL_TURNS - game.turn > MIN_TURNS_LEFT
                && !units.iter().any(|unit| unit.cell == shack)
            {
                actions.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
            }
        }
        if actions.is_empty() {
            actions.push("WAIT".to_string());
        }
        actions
    }
}

fn bank_command(unit: &Unit, shack: Cell) -> String {
    if manhattan(unit.cell, shack) == 1 {
        format!("DROP {}", unit.id)
    } else {
        format!("MOVE {} {} {}", unit.id, shack.0, shack.1)
    }
}

fn replace_unit_command(commands: &mut Vec<String>, unit_id: i32, replacement: String) {
    commands.retain(|command| {
        let fields: Vec<_> = command.split_whitespace().collect();
        if fields.first().is_some_and(|verb| *verb == "TRAIN") {
            return false;
        }
        fields.get(1).and_then(|value| value.parse::<i32>().ok()) != Some(unit_id)
    });
    commands.push(replacement);
}

fn ranked_funding_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    workers: i32,
    rank: usize,
    reserved: &mut BTreeSet<Cell>,
) -> Option<String> {
    let cost = training_cost(workers, stage_base(workers)?);
    let inventory = &game.inventories[player];
    let mut needs: Vec<_> = (PLUM..=APPLE)
        .map(|index| (cost[index] - inventory[index], index))
        .filter(|(deficit, _)| *deficit > 0)
        .collect();
    if !game.iron.is_empty() && inventory[IRON] < cost[IRON] {
        needs.push((cost[IRON] - inventory[IRON], IRON));
    }
    needs.sort_by_key(|(deficit, index)| (-*deficit, *index));
    let (_, resource) = *needs.get(rank.min(needs.len().saturating_sub(1)))?;
    if unit.total_carried() > 0 && (unit.free_capacity() == 0 || unit.carry[resource] > 0) {
        return Some(bank_command(unit, game.shacks[player]));
    }

    let distance = bfs(game, unit.cell);
    if resource <= APPLE {
        let kind = [PlantKind::Plum, PlantKind::Lemon, PlantKind::Apple][resource];
        if let Some(cell) = game
            .plants
            .iter()
            .filter(|plant| plant.kind == kind && distance.contains_key(&plant.cell))
            .filter(|plant| plant.cell == unit.cell || !reserved.contains(&plant.cell))
            .min_by_key(|plant| {
                (
                    i32::from(plant.fruits <= 0),
                    distance[&plant.cell],
                    plant.cooldown,
                    plant.cell,
                )
            })
            .map(|plant| plant.cell)
        {
            reserved.insert(cell);
            return Some(if cell == unit.cell {
                format!("HARVEST {}", unit.id)
            } else {
                format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
            });
        }
    } else if resource == IRON && unit.stats.chop_power > 0 {
        if game
            .iron
            .iter()
            .any(|cell| manhattan(unit.cell, *cell) == 1)
        {
            reserved.insert(unit.cell);
            return Some(format!("MINE {}", unit.id));
        }
        if let Some(cell) = game
            .iron
            .iter()
            .flat_map(|iron| ortho(*iron))
            .filter(|cell| distance.contains_key(cell) && !reserved.contains(cell))
            .min_by_key(|cell| (distance[cell], *cell))
        {
            reserved.insert(cell);
            return Some(format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
        }
    }
    (unit.total_carried() > 0).then(|| bank_command(unit, game.shacks[player]))
}

fn coordinated_three_worker_commands(
    mut commands: Vec<String>,
    game: &GameState,
    player: usize,
) -> Vec<String> {
    commands.retain(|command| !command.starts_with("TRAIN "));
    let mut units: Vec<&Unit> = game
        .units
        .iter()
        .filter(|unit| unit.player == player)
        .collect();
    units.sort_by_key(|unit| unit.id);
    let workers = units.len() as i32;
    if workers >= 3 {
        return commands;
    }

    let proposed = proposed_spec(workers, &game.inventories[player], !game.iron.is_empty());
    if proposed.is_none() {
        let funder_count = if workers == 2 { 2 } else { 1 };
        let mut reserved = BTreeSet::new();
        for (rank, unit) in units
            .iter()
            .copied()
            .filter(|unit| unit.stats.harvest_power > 0)
            .take(funder_count)
            .enumerate()
        {
            if let Some(command) =
                ranked_funding_command(game, player, unit, workers, rank, &mut reserved)
            {
                replace_unit_command(&mut commands, unit.id, command);
            }
        }
    } else if let Some(unit) = units
        .iter()
        .copied()
        .find(|unit| unit.cell == game.shacks[player])
    {
        if let Some(cell) = ortho(unit.cell)
            .into_iter()
            .find(|cell| game.walkable.contains(cell))
        {
            replace_unit_command(
                &mut commands,
                unit.id,
                format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
            );
        }
    }
    if let Some(spec) = proposed {
        commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
    }
    commands
}

pub struct NorxondorThreeWorkerBot {
    continuation: SilverContinuation,
}

impl NorxondorThreeWorkerBot {
    pub fn new() -> Self {
        Self {
            continuation: SilverContinuation::new(),
        }
    }

    pub fn commands(&mut self, game: &GameState) -> Vec<String> {
        let commands = self.continuation.decide(game, 0);
        coordinated_three_worker_commands(commands, game, 0)
    }
}
