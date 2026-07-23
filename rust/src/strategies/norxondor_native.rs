//! Research-only native reconstruction of Norxondor's intent/goal/workforce controller.

use super::norxondor_research::proposed_spec;
use super::Strategy;
use crate::game::engine::{training_cost, APPLE, BANANA, IRON, PLUM};
use crate::game::state::{Cell, GameState, Unit};
use std::cell::RefCell;
use std::cmp::Ordering;
use std::collections::{HashMap, HashSet, VecDeque};

const BASES: [(i32, i32, i32, i32); 4] = [(2, 2, 1, 1), (2, 3, 1, 2), (2, 3, 0, 3), (2, 4, 0, 3)];
const FRUIT_NAMES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Intent {
    Chop,
    Drop,
    Farm,
    Harvest,
    Mine,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum PreviousAction {
    Start,
    Chop,
    Drop,
    Farm,
    Harvest,
    Mine,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Role {
    Generalist,
    HarvestSpecialist,
    HybridChopper,
    WoodSpecialist,
    Carrier,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum CarryClass {
    Empty,
    Fruit,
    Iron,
    Wood,
    Mixed,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum OnCell {
    RipeTree,
    Tree,
    BankEdge,
    Open,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Phase {
    Opening,
    Early,
    Mid,
    MiddleLate,
    Late,
    End,
}

#[derive(Clone, Copy, Debug)]
struct Memory {
    previous: PreviousAction,
    intent: Option<Intent>,
    goal: Option<Cell>,
}

impl Default for Memory {
    fn default() -> Self {
        Self {
            previous: PreviousAction::Start,
            intent: None,
            goal: None,
        }
    }
}

fn manhattan(left: Cell, right: Cell) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn neighbors(cell: Cell) -> [Cell; 4] {
    [
        (cell.0, cell.1 + 1),
        (cell.0 + 1, cell.1),
        (cell.0, cell.1 - 1),
        (cell.0 - 1, cell.1),
    ]
}

fn bfs_sources(game: &GameState, sources: impl IntoIterator<Item = Cell>) -> HashMap<Cell, i32> {
    let mut distances = HashMap::new();
    let mut queue = VecDeque::new();
    for source in sources {
        if distances.insert(source, 0).is_none() {
            queue.push_back(source);
        }
    }
    while let Some(cell) = queue.pop_front() {
        let next_distance = distances[&cell] + 1;
        for next in neighbors(cell) {
            if game.walkable.contains(&next) && !distances.contains_key(&next) {
                distances.insert(next, next_distance);
                queue.push_back(next);
            }
        }
    }
    distances
}

fn bank_distances(game: &GameState, player: usize) -> HashMap<Cell, i32> {
    bfs_sources(
        game,
        neighbors(game.shacks[player])
            .into_iter()
            .filter(|cell| game.walkable.contains(cell)),
    )
}

fn phase(turn: i32) -> Phase {
    match turn {
        ..=5 => Phase::Opening,
        6..=25 => Phase::Early,
        26..=75 => Phase::Mid,
        76..=150 => Phase::MiddleLate,
        151..=250 => Phase::Late,
        _ => Phase::End,
    }
}

fn role(unit: &Unit) -> Role {
    if unit.chop >= 2 && unit.hp == 0 {
        Role::WoodSpecialist
    } else if unit.chop >= 2 && unit.hp > 0 {
        Role::HybridChopper
    } else if unit.hp >= 2 && unit.chop <= 1 {
        Role::HarvestSpecialist
    } else if unit.cc >= 3 && unit.hp <= 1 && unit.chop <= 1 {
        Role::Carrier
    } else {
        Role::Generalist
    }
}

fn carry_class(unit: &Unit) -> CarryClass {
    let fruit = unit.carry[..=BANANA].iter().any(|value| *value > 0);
    let iron = unit.carry[IRON] > 0;
    let wood = unit.carry[5] > 0;
    match usize::from(fruit) + usize::from(iron) + usize::from(wood) {
        0 => CarryClass::Empty,
        1 if fruit => CarryClass::Fruit,
        1 if iron => CarryClass::Iron,
        1 => CarryClass::Wood,
        _ => CarryClass::Mixed,
    }
}

fn on_cell(game: &GameState, player: usize, unit: &Unit) -> OnCell {
    if let Some(plant) = game.plants.iter().find(|plant| plant.pos() == unit.pos()) {
        if plant.fruits > 0 {
            OnCell::RipeTree
        } else {
            OnCell::Tree
        }
    } else if manhattan(unit.pos(), game.shacks[player]) <= 1 {
        OnCell::BankEdge
    } else {
        OnCell::Open
    }
}

fn distance_band(distance: i32, low: i32, high: i32) -> bool {
    (low..=high).contains(&distance)
}

/// Exact 107-node replay-distilled tree, simplified into equivalent readable branches.
fn predict_intent(
    game: &GameState,
    player: usize,
    unit: &Unit,
    ordinal: usize,
    previous: PreviousAction,
) -> Intent {
    let ordinal = ordinal.min(3);
    let unit_count = game
        .units
        .iter()
        .filter(|other| other.player as usize == player)
        .count()
        .min(4);
    let bank_distance = manhattan(unit.pos(), game.shacks[player]);
    let cell = on_cell(game, player, unit);
    let phase = phase(game.turn);
    let role = role(unit);
    let carry = carry_class(unit);
    let full = unit.total() >= unit.cc;

    if full {
        if bank_distance == 1 {
            return Intent::Farm;
        }
        if previous == PreviousAction::Harvest && ordinal == 0 {
            if bank_distance == 2 {
                return Intent::Drop;
            }
            if distance_band(bank_distance, 6, 9) {
                return Intent::Farm;
            }
            if unit_count == 4 || cell == OnCell::Tree {
                return Intent::Drop;
            }
            return Intent::Farm;
        }
        return Intent::Drop;
    }

    if cell == OnCell::Tree {
        if carry == CarryClass::Fruit {
            if previous == PreviousAction::Harvest {
                if ordinal == 3 {
                    return Intent::Harvest;
                }
                if distance_band(bank_distance, 3, 5) {
                    if role == Role::HarvestSpecialist {
                        return Intent::Farm;
                    }
                    return if unit_count == 2 {
                        Intent::Harvest
                    } else {
                        Intent::Farm
                    };
                }
                return Intent::Harvest;
            }
            if ordinal == 2 {
                return if bank_distance == 2 {
                    Intent::Harvest
                } else {
                    Intent::Farm
                };
            }
            return Intent::Farm;
        }
        if phase == Phase::End {
            return if ordinal == 3 {
                Intent::Farm
            } else {
                Intent::Chop
            };
        }
        if phase == Phase::Late {
            if unit_count == 4 {
                if previous == PreviousAction::Drop {
                    return if ordinal == 3 {
                        Intent::Chop
                    } else {
                        Intent::Harvest
                    };
                }
                return Intent::Chop;
            }
            if unit_count == 2 {
                return Intent::Harvest;
            }
            return if bank_distance == 2 {
                Intent::Chop
            } else {
                Intent::Harvest
            };
        }
        return if ordinal == 3 {
            Intent::Chop
        } else {
            Intent::Harvest
        };
    }

    if carry == CarryClass::Fruit {
        if bank_distance == 1 {
            return if unit_count == 3 {
                Intent::Farm
            } else {
                Intent::Harvest
            };
        }
        if phase == Phase::End {
            return Intent::Farm;
        }
        if unit_count == 2 && phase == Phase::MiddleLate {
            return Intent::Harvest;
        }
        return Intent::Farm;
    }

    if unit_count == 4 {
        if cell == OnCell::Open {
            if bank_distance >= 10 {
                return Intent::Chop;
            }
            if ordinal == 1 {
                return if role == Role::HarvestSpecialist {
                    Intent::Drop
                } else {
                    Intent::Chop
                };
            }
            return Intent::Drop;
        }
        if phase == Phase::MiddleLate {
            return if role == Role::WoodSpecialist {
                Intent::Chop
            } else {
                Intent::Harvest
            };
        }
        return Intent::Chop;
    }

    if unit_count == 3 {
        if phase == Phase::MiddleLate {
            if cell == OnCell::RipeTree {
                return if role == Role::HybridChopper {
                    Intent::Mine
                } else {
                    Intent::Harvest
                };
            }
            return if cell == OnCell::Open {
                Intent::Drop
            } else {
                Intent::Chop
            };
        }
        if role == Role::HybridChopper {
            return if carry == CarryClass::Empty {
                Intent::Chop
            } else {
                Intent::Drop
            };
        }
        return if bank_distance == 1 {
            Intent::Harvest
        } else {
            Intent::Chop
        };
    }

    if phase == Phase::Opening {
        if role == Role::HybridChopper {
            return Intent::Chop;
        }
        return if unit_count == 2 {
            Intent::Harvest
        } else {
            Intent::Farm
        };
    }
    if cell == OnCell::RipeTree {
        return if previous == PreviousAction::Drop {
            Intent::Harvest
        } else {
            Intent::Chop
        };
    }
    if cell == OnCell::Open {
        Intent::Drop
    } else {
        Intent::Harvest
    }
}

#[derive(Clone)]
struct TreeCandidate {
    cell: Cell,
    kind: String,
    travel: f64,
    home: f64,
    chops: f64,
    cycle: f64,
    efficiency: f64,
    health: f64,
    size: f64,
    fruits: f64,
    cooldown: f64,
    other_distance: f64,
    opponent_distance: f64,
    territory: f64,
    near_water: f64,
    ranks: [usize; 8],
}

fn ceil_div(left: i32, right: i32) -> i32 {
    (left + right - 1) / right.max(1)
}

fn build_tree_candidates(
    game: &GameState,
    player: usize,
    unit: &Unit,
    harvest: bool,
    reserved: &HashSet<Cell>,
) -> Vec<TreeCandidate> {
    let from_unit = bfs_sources(game, [unit.pos()]);
    let from_bank = bank_distances(game, player);
    let from_opponent_bank = bank_distances(game, 1 - player);
    let other_units: Vec<_> = game
        .units
        .iter()
        .filter(|other| other.player as usize == player && other.id != unit.id)
        .collect();
    let opponents: Vec<_> = game
        .units
        .iter()
        .filter(|other| other.player as usize != player)
        .collect();
    let mut plants: Vec<_> = game
        .plants
        .iter()
        .filter(|plant| !reserved.contains(&plant.pos()))
        .filter(|plant| !harvest || plant.fruits > 0)
        .filter(|plant| from_unit.contains_key(&plant.pos()))
        .collect();
    plants.sort_by_key(|plant| plant.pos());
    let free = unit.free().max(0);
    let mut candidates: Vec<_> = plants
        .into_iter()
        .map(|plant| {
            let unit_distance = from_unit[&plant.pos()];
            let bank_distance = *from_bank.get(&plant.pos()).unwrap_or(&99);
            let opponent_bank_distance = *from_opponent_bank.get(&plant.pos()).unwrap_or(&99);
            let travel = ceil_div(unit_distance, unit.ms);
            let home = ceil_div(bank_distance, unit.ms);
            let chops = ceil_div(plant.health, unit.chop.max(1));
            let cycle = travel + chops + home + 1;
            let wood = plant.size.min(free);
            TreeCandidate {
                cell: plant.pos(),
                kind: plant.plant_type.clone(),
                travel: travel as f64 / 10.0,
                home: home as f64 / 10.0,
                chops: chops as f64 / 20.0,
                cycle: cycle as f64 / 30.0,
                efficiency: wood as f64 / cycle.max(1) as f64,
                health: plant.health as f64 / 40.0,
                size: plant.size as f64 / 4.0,
                fruits: plant.fruits as f64 / 3.0,
                cooldown: plant.cooldown as f64 / 10.0,
                other_distance: other_units
                    .iter()
                    .map(|other| manhattan(other.pos(), plant.pos()))
                    .min()
                    .unwrap_or(20) as f64
                    / 20.0,
                opponent_distance: opponents
                    .iter()
                    .map(|other| manhattan(other.pos(), plant.pos()))
                    .min()
                    .unwrap_or(20) as f64
                    / 20.0,
                territory: (opponent_bank_distance - bank_distance) as f64 / 20.0,
                near_water: f64::from(
                    game.water
                        .iter()
                        .any(|water| manhattan(*water, plant.pos()) == 1),
                ),
                ranks: [0; 8],
            }
        })
        .collect();
    assign_ranks(&mut candidates);
    candidates
}

fn compare_cells(left: Cell, right: Cell) -> Ordering {
    left.cmp(&right)
}

fn assign_ranks(candidates: &mut [TreeCandidate]) {
    for ranker in 0..8 {
        let mut indexes: Vec<_> = (0..candidates.len()).collect();
        indexes.sort_by(|left, right| {
            let left = &candidates[*left];
            let right = &candidates[*right];
            let ordering = match ranker {
                0 => left.travel.total_cmp(&right.travel),
                1 => left.home.total_cmp(&right.home),
                2 => left.cycle.total_cmp(&right.cycle),
                3 => right.efficiency.total_cmp(&left.efficiency),
                4 => left.health.total_cmp(&right.health),
                5 => right.size.total_cmp(&left.size),
                6 => right.fruits.total_cmp(&left.fruits),
                _ => Ordering::Equal,
            };
            ordering.then_with(|| compare_cells(left.cell, right.cell))
        });
        for (rank, index) in indexes.into_iter().enumerate() {
            candidates[index].ranks[ranker] = rank + 1;
        }
    }
}

fn base_feature(candidate: &TreeCandidate, name: &str) -> f64 {
    match name {
        "bias" => 1.0,
        "travel" => candidate.travel,
        "home" => candidate.home,
        "chops" => candidate.chops,
        "cycle" => candidate.cycle,
        "efficiency" => candidate.efficiency,
        "health" => candidate.health,
        "size" => candidate.size,
        "fruits" => candidate.fruits,
        "cooldown" => candidate.cooldown,
        "other_distance" => candidate.other_distance,
        "opponent_distance" => candidate.opponent_distance,
        "territory" => candidate.territory,
        "near_water" => candidate.near_water,
        "unit_first" => f64::from(candidate.ranks[0] == 1),
        "unit_reciprocal_rank" => 1.0 / candidate.ranks[0] as f64,
        "bank_first" => f64::from(candidate.ranks[1] == 1),
        "bank_reciprocal_rank" => 1.0 / candidate.ranks[1] as f64,
        "cycle_first" => f64::from(candidate.ranks[2] == 1),
        "cycle_reciprocal_rank" => 1.0 / candidate.ranks[2] as f64,
        "efficiency_first" => f64::from(candidate.ranks[3] == 1),
        "efficiency_reciprocal_rank" => 1.0 / candidate.ranks[3] as f64,
        "health_first" => f64::from(candidate.ranks[4] == 1),
        "health_reciprocal_rank" => 1.0 / candidate.ranks[4] as f64,
        "size_first" => f64::from(candidate.ranks[5] == 1),
        "size_reciprocal_rank" => 1.0 / candidate.ranks[5] as f64,
        "fruits_first" => f64::from(candidate.ranks[6] == 1),
        "fruits_reciprocal_rank" => 1.0 / candidate.ranks[6] as f64,
        "input_first" => f64::from(candidate.ranks[7] == 1),
        "input_reciprocal_rank" => 1.0 / candidate.ranks[7] as f64,
        _ if name.starts_with("kind=") => f64::from(&name[5..] == candidate.kind),
        _ => 0.0,
    }
}

fn feature_value(candidate: &TreeCandidate, name: &str, ordinal: usize, turn: i32) -> f64 {
    if let Some((scope, base)) = name.split_once(':') {
        if let Some(number) = scope.strip_prefix("ordinal") {
            return if number.parse::<usize>().ok() == Some(ordinal) {
                base_feature(candidate, base)
            } else {
                0.0
            };
        }
        let active = match scope {
            "early" => turn <= 25,
            "mid" => (26..=100).contains(&turn),
            "late" => turn > 100,
            _ => false,
        };
        return if active {
            base_feature(candidate, base)
        } else {
            0.0
        };
    }
    base_feature(candidate, name)
}

fn tree_goal(
    game: &GameState,
    player: usize,
    unit: &Unit,
    ordinal: usize,
    intent: Intent,
    reserved: &HashSet<Cell>,
) -> Option<Cell> {
    let candidates = build_tree_candidates(game, player, unit, intent == Intent::Harvest, reserved);
    let weights = if intent == Intent::Harvest {
        HARVEST_WEIGHTS
    } else {
        CHOP_WEIGHTS
    };
    candidates
        .into_iter()
        .map(|candidate| {
            let score = weights
                .iter()
                .map(|(name, weight)| weight * feature_value(&candidate, name, ordinal, game.turn))
                .sum::<f64>();
            (score, candidate.cell)
        })
        .max_by(|left, right| {
            left.0
                .total_cmp(&right.0)
                .then_with(|| right.1.cmp(&left.1))
        })
        .map(|(_, cell)| cell)
}

fn next_fruit(game: &GameState, player: usize, workers: usize) -> usize {
    if (1..=4).contains(&workers) {
        let cost = training_cost(workers as i32, BASES[workers - 1]);
        (PLUM..=APPLE)
            .max_by_key(|index| {
                (
                    cost[*index] - game.inventories[player][*index],
                    -(*index as i32),
                )
            })
            .unwrap_or(PLUM)
    } else {
        (PLUM..=BANANA)
            .min_by_key(|index| (game.inventories[player][*index], *index))
            .unwrap_or(PLUM)
    }
}

fn carried_fruit(game: &GameState, player: usize, workers: usize, unit: &Unit) -> Option<usize> {
    let preferred = next_fruit(game, player, workers);
    (PLUM..=BANANA)
        .filter(|index| unit.carry[*index] > 0)
        .max_by_key(|index| {
            (
                i32::from(*index == preferred),
                unit.carry[*index],
                -(*index as i32),
            )
        })
}

fn available_pick_fruit(game: &GameState, player: usize, workers: usize) -> Option<usize> {
    let preferred = next_fruit(game, player, workers);
    (PLUM..=BANANA)
        .filter(|index| game.inventories[player][*index] > 0)
        .max_by_key(|index| {
            (
                i32::from(*index == preferred),
                -game.inventories[player][*index],
                -(*index as i32),
            )
        })
}

fn farm_goal(
    game: &GameState,
    player: usize,
    unit: &Unit,
    workers: usize,
    reserved: &HashSet<Cell>,
) -> Option<Cell> {
    let occupied: HashSet<_> = game
        .units
        .iter()
        .filter(|other| other.id != unit.id)
        .map(Unit::pos)
        .collect();
    let from_bank = bank_distances(game, player);
    let from_unit = bfs_sources(game, [unit.pos()]);
    let planting_cell = game
        .walkable
        .iter()
        .copied()
        .filter(|cell| from_bank.get(cell).is_some_and(|distance| *distance <= 3))
        .filter(|cell| from_unit.contains_key(cell))
        .filter(|cell| !reserved.contains(cell) && !occupied.contains(cell))
        .filter(|cell| !game.plants.iter().any(|plant| plant.pos() == *cell))
        .min_by_key(|cell| {
            let adjacent_tree = game
                .plants
                .iter()
                .any(|plant| manhattan(plant.pos(), *cell) == 1);
            let near_water = game.water.iter().any(|water| manhattan(*water, *cell) == 1);
            (
                i32::from(!adjacent_tree),
                i32::from(!near_water),
                from_unit[cell],
                from_bank[cell],
                *cell,
            )
        });
    if carried_fruit(game, player, workers, unit).is_some() {
        return planting_cell;
    }
    planting_cell?;
    available_pick_fruit(game, player, workers)?;
    neighbors(game.shacks[player])
        .into_iter()
        .filter(|cell| from_unit.contains_key(cell))
        .min_by_key(|cell| (from_unit[cell], *cell))
}

fn mine_goal(game: &GameState, unit: &Unit, reserved: &HashSet<Cell>) -> Option<Cell> {
    let distance = bfs_sources(game, [unit.pos()]);
    game.iron
        .iter()
        .flat_map(|iron| neighbors(*iron))
        .filter(|cell| distance.contains_key(cell) && !reserved.contains(cell))
        .min_by_key(|cell| (distance[cell], *cell))
}

fn select_goal(
    game: &GameState,
    player: usize,
    unit: &Unit,
    ordinal: usize,
    workers: usize,
    intent: Intent,
    reserved: &HashSet<Cell>,
) -> Option<Cell> {
    match intent {
        Intent::Drop => Some(game.shacks[player]),
        Intent::Farm => farm_goal(game, player, unit, workers, reserved),
        Intent::Harvest | Intent::Chop => tree_goal(game, player, unit, ordinal, intent, reserved),
        Intent::Mine => mine_goal(game, unit, reserved),
    }
}

fn command_for_goal(
    game: &GameState,
    player: usize,
    unit: &Unit,
    workers: usize,
    intent: Intent,
    goal: Cell,
) -> Option<(String, bool)> {
    match intent {
        Intent::Drop => Some((
            if manhattan(unit.pos(), game.shacks[player]) == 1 {
                format!("DROP {}", unit.id)
            } else {
                format!("MOVE {} {} {}", unit.id, goal.0, goal.1)
            },
            manhattan(unit.pos(), game.shacks[player]) == 1,
        )),
        Intent::Farm => {
            if let Some(index) = carried_fruit(game, player, workers, unit) {
                if unit.pos() == goal {
                    Some((format!("PLANT {} {}", unit.id, FRUIT_NAMES[index]), true))
                } else {
                    Some((format!("MOVE {} {} {}", unit.id, goal.0, goal.1), false))
                }
            } else if manhattan(unit.pos(), game.shacks[player]) == 1 {
                let index = available_pick_fruit(game, player, workers)?;
                Some((format!("PICK {} {}", unit.id, FRUIT_NAMES[index]), true))
            } else {
                Some((format!("MOVE {} {} {}", unit.id, goal.0, goal.1), false))
            }
        }
        Intent::Harvest => {
            let plant = game.plants.iter().find(|plant| plant.pos() == goal)?;
            if unit.pos() == goal && plant.fruits > 0 && unit.hp > 0 && unit.free() > 0 {
                Some((format!("HARVEST {}", unit.id), true))
            } else if plant.fruits > 0 {
                Some((format!("MOVE {} {} {}", unit.id, goal.0, goal.1), false))
            } else {
                None
            }
        }
        Intent::Chop => {
            game.plants.iter().find(|plant| plant.pos() == goal)?;
            if unit.pos() == goal && unit.chop > 0 && unit.free() > 0 {
                Some((format!("CHOP {}", unit.id), true))
            } else if unit.chop > 0 {
                Some((format!("MOVE {} {} {}", unit.id, goal.0, goal.1), false))
            } else {
                None
            }
        }
        Intent::Mine => {
            if game
                .iron
                .iter()
                .any(|iron| manhattan(*iron, unit.pos()) == 1)
                && unit.chop > 0
                && unit.free() > 0
            {
                Some((format!("MINE {}", unit.id), true))
            } else if unit.chop > 0 {
                Some((format!("MOVE {} {} {}", unit.id, goal.0, goal.1), false))
            } else {
                None
            }
        }
    }
}

fn completed_action(intent: Intent) -> PreviousAction {
    match intent {
        Intent::Chop => PreviousAction::Chop,
        Intent::Drop => PreviousAction::Drop,
        Intent::Farm => PreviousAction::Farm,
        Intent::Harvest => PreviousAction::Harvest,
        Intent::Mine => PreviousAction::Mine,
    }
}

fn stage_iron_need(game: &GameState, player: usize, workers: usize) -> bool {
    (1..=4).contains(&workers)
        && !game.iron.is_empty()
        && game.inventories[player][IRON] < training_cost(workers as i32, BASES[workers - 1])[IRON]
}

fn direct_action_continuation(
    game: &GameState,
    unit: &Unit,
    previous: PreviousAction,
    force_mine: bool,
) -> Option<String> {
    match previous {
        PreviousAction::Chop
            if !force_mine
                && unit.chop > 0
                && unit.free() > 0
                && game.plants.iter().any(|plant| plant.pos() == unit.pos()) =>
        {
            Some(format!("CHOP {}", unit.id))
        }
        PreviousAction::Harvest
            if !force_mine
                && unit.hp > 0
                && unit.free() > 0
                && game
                    .plants
                    .iter()
                    .any(|plant| plant.pos() == unit.pos() && plant.fruits > 0) =>
        {
            Some(format!("HARVEST {}", unit.id))
        }
        PreviousAction::Mine
            if force_mine
                && unit.chop > 0
                && unit.free() > 0
                && game
                    .iron
                    .iter()
                    .any(|iron| manhattan(*iron, unit.pos()) == 1) =>
        {
            Some(format!("MINE {}", unit.id))
        }
        _ => None,
    }
}

#[derive(Clone)]
pub struct NorxondorNative {
    memory: RefCell<HashMap<i32, Memory>>,
    stop_at_three: bool,
}

impl NorxondorNative {
    pub fn new(stop_at_three: bool) -> Self {
        Self {
            memory: RefCell::new(HashMap::new()),
            stop_at_three,
        }
    }
}

impl Strategy for NorxondorNative {
    fn name(&self) -> &str {
        if self.stop_at_three {
            "norx_native_three"
        } else {
            "norx_native_full"
        }
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        let alive: HashSet<_> = units.iter().map(|unit| unit.id).collect();
        let workers = units.len();
        let need_iron = stage_iron_need(game, player, workers);
        let miner_id = need_iron
            .then(|| {
                units
                    .iter()
                    .rev()
                    .find(|unit| unit.chop > 0)
                    .map(|unit| unit.id)
            })
            .flatten();
        let mut memory = self.memory.borrow_mut();
        memory.retain(|unit_id, _| alive.contains(unit_id));
        let mut reserved = HashSet::new();
        let mut commands = Vec::new();

        for (ordinal, unit) in units.into_iter().enumerate() {
            let mut state = memory.get(&unit.id).copied().unwrap_or_default();
            let forced_intent = (miner_id == Some(unit.id))
                .then_some(
                    if unit.free() == 0 || (unit.total() > 0 && unit.carry[IRON] == 0) {
                        Intent::Drop
                    } else {
                        Intent::Mine
                    },
                )
                .or_else(|| {
                    (state.previous == PreviousAction::Farm
                        && carried_fruit(game, player, workers, unit).is_some())
                    .then_some(Intent::Farm)
                });
            if forced_intent.is_some() && state.intent != forced_intent {
                state.intent = None;
                state.goal = None;
            }
            if let Some(candidate) =
                direct_action_continuation(game, unit, state.previous, miner_id == Some(unit.id))
            {
                commands.push(candidate);
                memory.insert(unit.id, state);
                continue;
            }
            let mut command = None;
            if let (Some(intent), Some(goal)) = (state.intent, state.goal) {
                if !reserved.contains(&goal) {
                    command = command_for_goal(game, player, unit, workers, intent, goal)
                        .map(|(command, completed)| (command, completed, intent, goal));
                }
            }
            if command.is_none() {
                state.intent = None;
                state.goal = None;
                let mut intent = forced_intent
                    .unwrap_or_else(|| predict_intent(game, player, unit, ordinal, state.previous));
                for _ in 0..3 {
                    if let Some(goal) =
                        select_goal(game, player, unit, ordinal, workers, intent, &reserved)
                    {
                        if let Some((candidate, completed)) =
                            command_for_goal(game, player, unit, workers, intent, goal)
                        {
                            command = Some((candidate, completed, intent, goal));
                            break;
                        }
                    }
                    intent = if unit.total() > 0 {
                        Intent::Drop
                    } else if unit.hp > 0 {
                        Intent::Harvest
                    } else {
                        Intent::Chop
                    };
                }
            }
            if let Some((candidate, completed, intent, goal)) = command {
                if completed {
                    state.previous = completed_action(intent);
                    state.intent = None;
                    state.goal = None;
                } else {
                    state.intent = Some(intent);
                    state.goal = Some(goal);
                    if intent != Intent::Drop {
                        reserved.insert(goal);
                    }
                }
                commands.push(candidate);
            }
            memory.insert(unit.id, state);
        }

        if !self.stop_at_three || workers < 3 {
            if let Some(spec) = proposed_spec(
                workers as i32,
                &game.inventories[player],
                !game.iron.is_empty(),
            ) {
                commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
            }
        }
        commands
    }
}

const CHOP_WEIGHTS: &[(&str, f64)] = &[
    ("late:health", 11.98746671597635),
    ("health", 11.384082840236722),
    ("efficiency", 10.485488417387533),
    ("efficiency_reciprocal_rank", 10.307771149359011),
    ("ordinal1:chops", -8.374785502958538),
    ("late:efficiency", 8.364550770008318),
    ("mid:cycle", -7.732682445759284),
    ("ordinal0:size", -7.381656804733728),
    ("ordinal2:territory", -7.378949704142077),
    ("ordinal2:efficiency_reciprocal_rank", 7.168219177397082),
    ("territory", -7.133091715976304),
    ("ordinal0:unit_first", -7.11353550295858),
    ("ordinal3:home", -7.061131656804653),
    ("ordinal2:fruits_first", 6.746819526627219),
    ("ordinal1:cycle", -6.663750000000009),
    ("early:travel", 6.53316568047357),
    ("ordinal2:other_distance", -6.480192307692178),
    ("home", -6.06637573964501),
    ("ordinal4:unit_first", 5.893934911242604),
    ("cycle_reciprocal_rank", -5.884843087245048),
    ("ordinal4:fruits_first", -5.764275147928994),
    ("ordinal3:chops", 5.510325443786812),
    ("kind=APPLE", -5.478106508875739),
    ("ordinal0:home", 5.4473742603550175),
    ("late:travel", -5.176035502958598),
    ("size", -5.120247781065089),
    ("mid:travel", -5.025976331360834),
    ("other_distance", 4.992385355029558),
    ("input_reciprocal_rank", -4.971481536598062),
    ("ordinal2:travel", -4.813912721893425),
    ("ordinal1:other_distance", 4.656061390532424),
    ("early:cycle", 4.637497534516943),
    ("ordinal4:fruits_reciprocal_rank", -4.625252661502421),
    ("ordinal0:fruits_first", 4.617307692307692),
    ("late:home", -4.59056952662725),
    ("opponent_distance", -4.535325443786986),
    ("ordinal1:efficiency", 4.5341568754525134),
    ("kind=BANANA", 4.447855029585799),
    ("ordinal3:health", 4.3921135355029035),
    ("ordinal2:cycle_reciprocal_rank", -4.313050120624802),
    ("ordinal1:health", 4.267052514792943),
    ("ordinal2:efficiency_first", -4.228550295857988),
    ("ordinal3:efficiency_reciprocal_rank", 4.203136859515748),
    ("ordinal0:other_distance", 4.195698964496935),
    ("efficiency_first", -4.159541420118344),
    ("ordinal3:health_first", -3.8882396449704144),
    ("ordinal1:home", -3.8646893491124223),
    ("ordinal1:fruits_reciprocal_rank", 3.798489236203668),
    ("health_first", -3.7909023668639055),
    ("mid:health", -3.757207840236814),
    ("ordinal4:unit_reciprocal_rank", -3.726002941974324),
    ("ordinal2:efficiency", 3.723555157931578),
    ("ordinal1:size_first", -3.682544378698225),
    ("travel", -3.668846153846156),
    ("ordinal0:kind=BANANA", 3.6483727810650888),
    ("ordinal3:size_first", -3.6401627218934913),
    ("ordinal1:unit_first", -3.5361686390532543),
    ("ordinal0:opponent_distance", -3.5220747041420144),
    ("ordinal3:cooldown", 3.3991198224851678),
    ("ordinal0:cycle", 3.3860749506904724),
    ("ordinal1:territory", -3.351279585798761),
    ("early:health", 3.153823964497045),
    ("ordinal2:size", 3.1241863905325444),
    ("ordinal0:territory", 3.109497041420088),
    ("ordinal3:unit_first", 3.0454142011834318),
    ("ordinal0:bank_reciprocal_rank", -3.0122288441004206),
    ("ordinal3:size_reciprocal_rank", 2.9488396840344184),
    ("ordinal0:cooldown", -2.939164201183476),
    ("ordinal3:fruits_first", -2.924112426035503),
    ("ordinal4:input_reciprocal_rank", 2.8653276093275486),
    ("ordinal0:size_first", 2.826183431952663),
    ("ordinal0:size_reciprocal_rank", -2.799293785736945),
    ("cycle", -2.7678574950690478),
    ("ordinal3:health_reciprocal_rank", -2.683227772077692),
    ("ordinal0:chops", 2.664859467455572),
    ("mid:efficiency", 2.6643129954236078),
    ("mid:home", -2.6390606508877514),
    ("ordinal1:cycle_first", -2.6053254437869824),
    ("ordinal3:input_reciprocal_rank", -2.6050159114128424),
    ("ordinal4:cycle_reciprocal_rank", -2.5549642521351457),
    ("ordinal1:bank_reciprocal_rank", -2.5005216023301378),
    ("mid:size", -2.4907359467455623),
    ("ordinal2:size_reciprocal_rank", -2.479846889104518),
    ("ordinal4:input_first", 2.4735207100591716),
    ("ordinal4:size_first", 2.4735207100591716),
    ("ordinal4:health", 2.472514792899413),
    ("ordinal1:cycle_reciprocal_rank", 2.4063525915706165),
    ("ordinal2:input_reciprocal_rank", -2.3720915741469697),
    ("ordinal2:bank_reciprocal_rank", 2.369777745080006),
    ("ordinal1:unit_reciprocal_rank", 2.363218033085115),
    ("bank_reciprocal_rank", -2.313626999813765),
    ("ordinal2:fruits", 2.308259368836311),
    ("early:size", -2.262647928994083),
    ("unit_first", -2.2568047337278108),
    ("ordinal0:kind=APPLE", -2.2085798816568047),
    ("ordinal2:fruits_reciprocal_rank", -2.206525663312752),
    ("ordinal3:kind=APPLE", -2.195931952662722),
    ("ordinal0:health_reciprocal_rank", 2.14605921144267),
    ("ordinal1:bank_first", 2.104733727810651),
    ("ordinal0:bank_first", 2.0831360946745563),
    ("ordinal4:size_reciprocal_rank", 2.060304490567979),
    ("unit_reciprocal_rank", 2.051537490872676),
    ("ordinal0:efficiency", 2.045512498849345),
    ("ordinal4:other_distance", 2.029619082840279),
    ("ordinal3:bank_first", -1.9720414201183432),
    ("ordinal2:health_reciprocal_rank", 1.9505858397076403),
    ("ordinal1:kind=LEMON", 1.944008875739645),
    ("ordinal1:kind=BANANA", -1.9266272189349112),
    ("ordinal0:unit_reciprocal_rank", 1.920880942770325),
    ("ordinal1:input_reciprocal_rank", -1.8945804561719342),
    ("mid:near_water", 1.8835059171597632),
    ("ordinal3:fruits_reciprocal_rank", 1.8640243001308057),
    ("ordinal2:cycle", -1.763530571992092),
    ("ordinal0:near_water", -1.7532544378698225),
    ("ordinal3:opponent_distance", -1.7355954142012673),
    ("ordinal0:input_first", -1.6924556213017752),
    ("ordinal4:cycle_first", 1.673224852071006),
    ("ordinal1:fruits_first", -1.6678254437869822),
    ("ordinal2:health_first", -1.625),
    ("ordinal4:efficiency_first", 1.5949704142011834),
    ("ordinal3:cycle", 1.5759763313609334),
    ("ordinal4:chops", 1.4952440828402982),
    ("ordinal4:fruits", -1.4556213017751367),
    ("input_first", 1.4504437869822486),
    ("late:near_water", -1.4330621301775148),
    ("ordinal4:health_reciprocal_rank", -1.4178424565572945),
    ("ordinal2:bank_first", -1.393491124260355),
    ("ordinal0:health", 1.332429733727786),
];

const HARVEST_WEIGHTS: &[(&str, f64)] = &[
    ("size", 16.18570801124385),
    ("ordinal2:home", -10.648021784961793),
    ("home", -8.685379479971857),
    ("ordinal1:size", 7.678135980323261),
    ("ordinal0:size", 7.443367884750527),
    ("late:travel", -7.24398805340833),
    ("mid:efficiency", -7.030005309747326),
    ("travel", -6.689775122979517),
    ("mid:size", 6.554778636683064),
    ("ordinal2:travel", -6.019722417428188),
    ("late:home", -5.908879128601566),
    ("ordinal0:home", 5.338998594518441),
    ("early:size", 4.959601194659171),
    ("ordinal2:cycle", -4.890988521901898),
    ("ordinal2:fruits", 4.711970016397323),
    ("late:size", 4.671328179901616),
    ("ordinal3:opponent_distance", -4.487647575545734),
    ("fruits", 4.429421410166395),
    ("ordinal1:health", -4.284804111033055),
    ("health_reciprocal_rank", -4.261162694697676),
    ("ordinal1:efficiency", -4.208244865534682),
    ("cycle", -4.079647458421214),
    ("ordinal2:input_first", -3.8376317638791284),
    ("input_first", -3.563281799016163),
    ("ordinal0:opponent_distance", 3.388406535488416),
    ("ordinal0:health_reciprocal_rank", -3.3670111070844477),
    ("ordinal2:fruits_first", 3.2862262825017567),
    ("ordinal2:health_first", -3.239002108222066),
    ("ordinal0:fruits", -3.1225931131412263),
    ("late:health", -3.1216136683064226),
    ("ordinal2:other_distance", 3.0413439915672464),
    ("ordinal3:bank_reciprocal_rank", -3.0212124914879652),
];

#[cfg(test)]
mod tests {
    use super::{
        direct_action_continuation, predict_intent, Intent, NorxondorNative, PreviousAction,
        CHOP_WEIGHTS, HARVEST_WEIGHTS,
    };
    use crate::game::mapgen::generate_bronze;
    use crate::strategies::Strategy;

    #[test]
    fn compact_rankers_match_the_frozen_weight_counts() {
        assert_eq!(CHOP_WEIGHTS.len(), 128);
        assert_eq!(HARVEST_WEIGHTS.len(), 32);
    }

    #[test]
    fn opening_generalist_starts_with_the_farm_intent() {
        let game = generate_bronze(0);
        let unit = game.units.iter().find(|unit| unit.player == 0).unwrap();
        assert_eq!(
            predict_intent(&game, 0, unit, 0, PreviousAction::Start),
            Intent::Farm
        );
    }

    #[test]
    fn native_controller_emits_a_command_for_the_starter() {
        let game = generate_bronze(0);
        let controller = NorxondorNative::new(false);
        let commands = controller.decide(&game, 0);
        assert!(commands.iter().any(|command| {
            command
                .split_whitespace()
                .nth(1)
                .and_then(|field| field.parse::<i32>().ok())
                == Some(game.units.iter().find(|unit| unit.player == 0).unwrap().id)
        }));
    }

    #[test]
    fn chop_action_persists_while_the_tree_and_capacity_remain() {
        let mut game = generate_bronze(0);
        let cell = game.plants[0].pos();
        let unit = game.units.iter_mut().find(|unit| unit.player == 0).unwrap();
        unit.x = cell.0;
        unit.y = cell.1;
        unit.chop = 1;
        let command = direct_action_continuation(
            &game,
            game.units.iter().find(|unit| unit.player == 0).unwrap(),
            PreviousAction::Chop,
            false,
        );
        assert_eq!(command, Some("CHOP 0".to_string()));
    }
}
