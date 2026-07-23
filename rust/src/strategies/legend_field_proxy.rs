//! Research-only proxy for worker-rich Legend farm/wood trajectories.
//!
//! This is an opponent-continuation model, not a candidate policy. It combines staged
//! harvest-capable training, coordinated funding, renewable planting, and rotating generalist
//! production roles so exact-map replay audits can test a missing field archetype.

use std::cell::RefCell;
use std::collections::{HashMap, HashSet, VecDeque};

use super::Strategy;
use crate::game::engine::{item_index, training_cost, APPLE, IRON, LEMON, MAX_FRUITS, PLUM, WOOD};
use crate::game::state::{Cell, GameState, Unit};

const TOTAL_TURNS: i32 = 300;
const FRUIT_NAMES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];
pub type Spec = (i32, i32, i32, i32);

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub struct LegendFieldProxyConfig {
    pub ladder: [Spec; 3],
    pub farmer_count: usize,
    pub fell_start: i32,
}

pub struct LegendFieldProxy {
    config: LegendFieldProxyConfig,
}

impl LegendFieldProxy {
    pub fn configured(config: LegendFieldProxyConfig) -> Self {
        Self { config }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub struct LegendFieldProxyV2Config {
    pub producer_spec: Spec,
    pub chopper_spec: Spec,
    pub late_chop: bool,
}

#[derive(Clone)]
pub struct LegendFieldProxyV2 {
    config: LegendFieldProxyV2Config,
}

impl LegendFieldProxyV2 {
    pub fn configured(config: LegendFieldProxyV2Config) -> Self {
        Self { config }
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub struct LegendFieldProxyV3Config {
    pub first_spec: Spec,
    pub max_workers: usize,
    pub post_producers: usize,
}

#[derive(Clone)]
pub struct LegendFieldProxyV3 {
    config: LegendFieldProxyV3Config,
}

impl LegendFieldProxyV3 {
    pub fn configured(config: LegendFieldProxyV3Config) -> Self {
        assert!(matches!(config.max_workers, 3 | 4));
        assert!(matches!(config.post_producers, 1 | 2));
        Self { config }
    }
}

#[derive(Clone)]
pub struct LegendFieldProxyV4 {
    config: LegendFieldProxyV3Config,
}

impl LegendFieldProxyV4 {
    pub fn configured(config: LegendFieldProxyV3Config) -> Self {
        assert!(matches!(config.max_workers, 3 | 4));
        assert!(matches!(config.post_producers, 1 | 2));
        Self { config }
    }
}

#[derive(Clone)]
pub struct LegendFieldProxyV5 {
    config: LegendFieldProxyV3Config,
}

impl LegendFieldProxyV5 {
    pub fn configured(config: LegendFieldProxyV3Config) -> Self {
        assert!(matches!(config.max_workers, 3 | 4));
        assert!(matches!(config.post_producers, 1 | 2));
        Self { config }
    }
}

#[derive(Clone)]
pub struct LegendFieldProxyV6 {
    config: LegendFieldProxyV3Config,
}

impl LegendFieldProxyV6 {
    pub fn configured(config: LegendFieldProxyV3Config) -> Self {
        assert!(matches!(config.max_workers, 3 | 4));
        assert!(matches!(config.post_producers, 1 | 2));
        Self { config }
    }
}

#[derive(Clone)]
pub struct LegendFieldProxyV7 {
    config: LegendFieldProxyV3Config,
}

impl LegendFieldProxyV7 {
    pub fn configured(config: LegendFieldProxyV3Config) -> Self {
        assert!(matches!(config.max_workers, 3 | 4));
        assert!(matches!(config.post_producers, 1 | 2));
        Self { config }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct MaterializationLease {
    resource: usize,
    target: Cell,
}

#[derive(Clone)]
pub struct LegendFieldProxyV8 {
    config: LegendFieldProxyV3Config,
    leases: RefCell<HashMap<i32, MaterializationLease>>,
}

impl LegendFieldProxyV8 {
    pub fn configured(config: LegendFieldProxyV3Config) -> Self {
        assert!(matches!(config.max_workers, 3 | 4));
        assert!(matches!(config.post_producers, 1 | 2));
        Self {
            config,
            leases: RefCell::new(HashMap::new()),
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

fn bfs(game: &GameState, source: Cell) -> HashMap<Cell, i32> {
    let mut distance = HashMap::from([(source, 0)]);
    let mut queue = VecDeque::from([source]);
    while let Some(cell) = queue.pop_front() {
        let next_distance = distance[&cell] + 1;
        for next in neighbors(cell) {
            if game.walkable.contains(&next) && !distance.contains_key(&next) {
                distance.insert(next, next_distance);
                queue.push_back(next);
            }
        }
    }
    distance
}

fn affordable(game: &GameState, player: usize, cost: &[i32; 6]) -> bool {
    let inventory = &game.inventories[player];
    inventory[PLUM] >= cost[PLUM]
        && inventory[LEMON] >= cost[LEMON]
        && inventory[APPLE] >= cost[APPLE]
        && (game.iron.is_empty() || inventory[IRON] >= cost[IRON])
}

fn drop_cell(game: &GameState, player: usize, distance: &HashMap<Cell, i32>) -> Cell {
    neighbors(game.shacks[player])
        .into_iter()
        .filter(|cell| game.walkable.contains(cell) && distance.contains_key(cell))
        .min_by_key(|cell| (distance[cell], *cell))
        .unwrap_or(game.shacks[player])
}

fn bank_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    distance: &HashMap<Cell, i32>,
) -> String {
    if manhattan(unit.pos(), game.shacks[player]) <= 1 {
        format!("DROP {}", unit.id)
    } else {
        let cell = drop_cell(game, player, distance);
        format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
    }
}

fn useful_funding_cargo(unit: &Unit, deficits: &[i32; 6]) -> bool {
    (PLUM..=APPLE).any(|index| deficits[index] > 0 && unit.carry[index] > 0)
        || (deficits[IRON] > 0 && unit.carry[IRON] > 0)
}

fn funding_target(
    game: &GameState,
    unit: &Unit,
    resource: usize,
    distance: &HashMap<Cell, i32>,
    reserved: &HashSet<Cell>,
) -> Option<Cell> {
    if resource <= APPLE {
        let kind = FRUIT_NAMES[resource];
        game.plants
            .iter()
            .filter(|plant| {
                plant.plant_type == kind
                    && plant.fruits > 0
                    && distance.contains_key(&plant.pos())
                    && (plant.pos() == unit.pos() || !reserved.contains(&plant.pos()))
            })
            .min_by_key(|plant| (distance[&plant.pos()], plant.cooldown, plant.pos()))
            .map(|plant| plant.pos())
    } else {
        game.iron
            .iter()
            .flat_map(|cell| neighbors(*cell))
            .filter(|cell| {
                game.walkable.contains(cell)
                    && distance.contains_key(cell)
                    && (*cell == unit.pos() || !reserved.contains(cell))
            })
            .min_by_key(|cell| (distance[cell], *cell))
    }
}

fn funding_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    deficits: &[i32; 6],
    assigned_resource: usize,
    reserved: &mut HashSet<Cell>,
) -> Option<String> {
    let distance = bfs(game, unit.pos());
    if unit.total() > 0 && (unit.free() == 0 || useful_funding_cargo(unit, deficits)) {
        return Some(bank_command(game, player, unit, &distance));
    }
    let target = funding_target(game, unit, assigned_resource, &distance, reserved)?;
    reserved.insert(target);
    if target == unit.pos() {
        if assigned_resource <= APPLE {
            Some(format!("HARVEST {}", unit.id))
        } else if game
            .iron
            .iter()
            .any(|cell| manhattan(*cell, unit.pos()) == 1)
        {
            Some(format!("MINE {}", unit.id))
        } else {
            None
        }
    } else {
        Some(format!("MOVE {} {} {}", unit.id, target.0, target.1))
    }
}

fn own_side(game: &GameState, player: usize, cell: Cell) -> bool {
    manhattan(cell, game.shacks[player]) <= manhattan(cell, game.shacks[1 - player])
}

fn standing_farm_trees(game: &GameState, player: usize, radius: i32) -> usize {
    game.plants
        .iter()
        .filter(|plant| {
            own_side(game, player, plant.pos())
                && manhattan(plant.pos(), game.shacks[player]) <= radius
        })
        .count()
}

fn standing_farm_kind(game: &GameState, player: usize, radius: i32, kind: &str) -> usize {
    game.plants
        .iter()
        .filter(|plant| {
            plant.plant_type == kind
                && own_side(game, player, plant.pos())
                && manhattan(plant.pos(), game.shacks[player]) <= radius
        })
        .count()
}

fn planting_target(
    game: &GameState,
    player: usize,
    unit: &Unit,
    distance: &HashMap<Cell, i32>,
    reserved: &HashSet<Cell>,
    farm_cap: usize,
    farm_radius: i32,
) -> Option<Cell> {
    if standing_farm_trees(game, player, farm_radius) >= farm_cap {
        return None;
    }
    game.walkable
        .iter()
        .filter(|cell| {
            own_side(game, player, **cell)
                && manhattan(**cell, game.shacks[player]) <= farm_radius
                && distance.contains_key(*cell)
                && !game.plants.iter().any(|plant| plant.pos() == **cell)
                && !game
                    .units
                    .iter()
                    .any(|other| other.pos() == **cell && other.id != unit.id)
                && !game.iron.contains(*cell)
                && !game.water.contains(*cell)
                && !reserved.contains(*cell)
        })
        .min_by_key(|cell| {
            (
                distance[*cell],
                manhattan(**cell, game.shacks[player]),
                **cell,
            )
        })
        .copied()
}

fn carried_seed(unit: &Unit) -> Option<usize> {
    (0..4)
        .filter(|index| unit.carry[*index] > 0)
        .max_by_key(|index| (unit.carry[*index], -(*index as i32)))
}

fn endgame_bank(
    game: &GameState,
    player: usize,
    unit: &Unit,
    distance: &HashMap<Cell, i32>,
) -> bool {
    if unit.total() == 0 {
        return false;
    }
    let home_distance = neighbors(game.shacks[player])
        .into_iter()
        .filter_map(|cell| distance.get(&cell))
        .min()
        .copied()
        .unwrap_or(0);
    let travel_turns = (home_distance + unit.ms - 1) / unit.ms.max(1) + 1;
    TOTAL_TURNS - game.turn + 1 <= travel_turns + 2
}

fn ripe_target(
    game: &GameState,
    unit: &Unit,
    distance: &HashMap<Cell, i32>,
    reserved: &HashSet<Cell>,
) -> Option<Cell> {
    game.plants
        .iter()
        .filter(|plant| {
            plant.fruits > 0
                && distance.contains_key(&plant.pos())
                && (plant.pos() == unit.pos() || !reserved.contains(&plant.pos()))
        })
        .min_by_key(|plant| (distance[&plant.pos()], plant.cooldown, plant.pos()))
        .map(|plant| plant.pos())
}

fn chop_target(
    game: &GameState,
    player: usize,
    unit: &Unit,
    distance: &HashMap<Cell, i32>,
    reserved: &HashSet<Cell>,
) -> Option<Cell> {
    game.plants
        .iter()
        .filter(|plant| {
            distance.contains_key(&plant.pos())
                && (plant.pos() == unit.pos() || !reserved.contains(&plant.pos()))
        })
        .min_by_key(|plant| {
            (
                i32::from(plant.size < 2),
                distance[&plant.pos()],
                manhattan(plant.pos(), game.shacks[1 - player]),
                plant.pos(),
            )
        })
        .map(|plant| plant.pos())
}

fn production_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    farmer: bool,
    fell_start: i32,
    reserved: &mut HashSet<Cell>,
) -> Option<String> {
    let distance = bfs(game, unit.pos());
    if endgame_bank(game, player, unit, &distance) {
        return Some(bank_command(game, player, unit, &distance));
    }

    if let Some(seed) = carried_seed(unit) {
        if let Some(target) = planting_target(game, player, unit, &distance, reserved, 36, 6) {
            reserved.insert(target);
            return Some(if target == unit.pos() {
                format!("PLANT {} {}", unit.id, FRUIT_NAMES[seed])
            } else {
                format!("MOVE {} {} {}", unit.id, target.0, target.1)
            });
        }
    }

    if unit.free() == 0 || (unit.carry[WOOD] > 0 && unit.free() <= unit.chop.max(1)) {
        return Some(bank_command(game, player, unit, &distance));
    }

    if let Some(plant) = game.plants.iter().find(|plant| plant.pos() == unit.pos()) {
        if plant.fruits > 0 && unit.hp > 0 {
            reserved.insert(unit.pos());
            return Some(format!("HARVEST {}", unit.id));
        }
        if game.turn >= fell_start && unit.chop > 0 {
            reserved.insert(unit.pos());
            return Some(format!("CHOP {}", unit.id));
        }
    }

    let farm_mode = farmer || game.turn < fell_start;
    let target = if farm_mode && unit.hp > 0 {
        ripe_target(game, unit, &distance, reserved)
            .or_else(|| chop_target(game, player, unit, &distance, reserved))
    } else {
        chop_target(game, player, unit, &distance, reserved)
            .or_else(|| ripe_target(game, unit, &distance, reserved))
    };
    if let Some(target) = target {
        reserved.insert(target);
        return Some(format!("MOVE {} {} {}", unit.id, target.0, target.1));
    }
    (unit.total() > 0).then(|| bank_command(game, player, unit, &distance))
}

fn v2_farm_cap(turn: i32) -> usize {
    if turn <= 100 {
        12
    } else if turn <= 200 {
        18
    } else {
        24
    }
}

fn v2_ripe_target(
    game: &GameState,
    unit: &Unit,
    distance: &HashMap<Cell, i32>,
    reserved: &HashSet<Cell>,
    preferred: Option<usize>,
) -> Option<Cell> {
    game.plants
        .iter()
        .filter(|plant| {
            plant.fruits > 0
                && distance.contains_key(&plant.pos())
                && (plant.pos() == unit.pos() || !reserved.contains(&plant.pos()))
        })
        .min_by_key(|plant| {
            let kind = FRUIT_NAMES
                .iter()
                .position(|name| *name == plant.plant_type)
                .unwrap_or(3);
            (
                i32::from(preferred.is_some_and(|resource| resource != kind)),
                distance[&plant.pos()],
                plant.cooldown,
                plant.pos(),
            )
        })
        .map(|plant| plant.pos())
}

fn v2_pick_seed(game: &GameState, player: usize, pending_cost: Option<&[i32; 6]>) -> Option<usize> {
    let inventory = &game.inventories[player];
    if inventory[3] > 0 {
        return Some(3);
    }
    (0..3)
        .filter(|index| {
            let reserved = pending_cost.map_or(0, |cost| cost[*index]);
            inventory[*index] > reserved
        })
        .max_by_key(|index| (inventory[*index], -(*index as i32)))
}

fn v2_producer_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    preferred: Option<usize>,
    deficits: &[i32; 6],
    pending_cost: Option<&[i32; 6]>,
    reserved: &mut HashSet<Cell>,
) -> Option<String> {
    let distance = bfs(game, unit.pos());
    if endgame_bank(game, player, unit, &distance) {
        return Some(bank_command(game, player, unit, &distance));
    }
    let farm_cap = v2_farm_cap(game.turn);
    let farm_needs_seed = standing_farm_trees(game, player, 6) < farm_cap;

    if unit.total() > 0 {
        if pending_cost.is_some() && useful_funding_cargo(unit, deficits) {
            return Some(bank_command(game, player, unit, &distance));
        }
        if let Some(seed) = carried_seed(unit) {
            let needed_for_train = pending_cost.is_some() && deficits[seed] > 0;
            if farm_needs_seed && !needed_for_train {
                if let Some(target) =
                    planting_target(game, player, unit, &distance, reserved, farm_cap, 6)
                {
                    reserved.insert(target);
                    return Some(if target == unit.pos() {
                        format!("PLANT {} {}", unit.id, FRUIT_NAMES[seed])
                    } else {
                        format!("MOVE {} {} {}", unit.id, target.0, target.1)
                    });
                }
            }
        }
        return Some(bank_command(game, player, unit, &distance));
    }

    if farm_needs_seed && manhattan(unit.pos(), game.shacks[player]) <= 1 {
        if let Some(seed) = v2_pick_seed(game, player, pending_cost) {
            return Some(format!("PICK {} {}", unit.id, FRUIT_NAMES[seed]));
        }
    }

    if let Some(plant) = game.plants.iter().find(|plant| plant.pos() == unit.pos()) {
        if plant.fruits > 0 && unit.hp > 0 {
            reserved.insert(unit.pos());
            return Some(format!("HARVEST {}", unit.id));
        }
    }

    if preferred == Some(IRON) && unit.chop > 0 {
        if game
            .iron
            .iter()
            .any(|cell| manhattan(*cell, unit.pos()) == 1)
        {
            reserved.insert(unit.pos());
            return Some(format!("MINE {}", unit.id));
        }
        if let Some(target) = funding_target(game, unit, IRON, &distance, reserved) {
            reserved.insert(target);
            return Some(format!("MOVE {} {} {}", unit.id, target.0, target.1));
        }
    }

    if let Some(target) = v2_ripe_target(game, unit, &distance, reserved, preferred) {
        reserved.insert(target);
        return Some(format!("MOVE {} {} {}", unit.id, target.0, target.1));
    }

    if farm_needs_seed && v2_pick_seed(game, player, pending_cost).is_some() {
        let target = drop_cell(game, player, &distance);
        return Some(format!("MOVE {} {} {}", unit.id, target.0, target.1));
    }
    None
}

fn v2_chopper_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    reserved: &mut HashSet<Cell>,
) -> Option<String> {
    let distance = bfs(game, unit.pos());
    if endgame_bank(game, player, unit, &distance) {
        return Some(bank_command(game, player, unit, &distance));
    }
    if unit.carry[..WOOD].iter().any(|value| *value > 0)
        || unit.free() == 0
        || (unit.carry[WOOD] > 0 && unit.free() < unit.chop.max(1))
    {
        return Some(bank_command(game, player, unit, &distance));
    }
    if let Some(plant) = game.plants.iter().find(|plant| plant.pos() == unit.pos()) {
        reserved.insert(unit.pos());
        if plant.fruits > 0 && unit.hp > 0 {
            return Some(format!("HARVEST {}", unit.id));
        }
        if unit.chop > 0 {
            return Some(format!("CHOP {}", unit.id));
        }
    }
    if let Some(target) = chop_target(game, player, unit, &distance, reserved) {
        reserved.insert(target);
        return Some(format!("MOVE {} {} {}", unit.id, target.0, target.1));
    }
    (unit.total() > 0).then(|| bank_command(game, player, unit, &distance))
}

impl Strategy for LegendFieldProxy {
    fn name(&self) -> &str {
        "legend_field_proxy"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        let workers = units.len();
        let next_spec = self.config.ladder.get(workers.saturating_sub(1)).copied();
        let next_cost = next_spec.map(|spec| training_cost(workers as i32, spec));
        let train_now = next_cost
            .as_ref()
            .is_some_and(|cost| affordable(game, player, cost));

        let mut reserved = HashSet::new();
        let mut commands = Vec::new();
        if let Some(cost) = next_cost.filter(|_| !train_now) {
            let inventory = &game.inventories[player];
            let mut deficits = [0; 6];
            for index in PLUM..=APPLE {
                deficits[index] = (cost[index] - inventory[index]).max(0);
            }
            if !game.iron.is_empty() {
                deficits[IRON] = (cost[IRON] - inventory[IRON]).max(0);
            }
            let mut needs: Vec<_> = (PLUM..=APPLE)
                .chain(std::iter::once(IRON))
                .filter(|index| deficits[*index] > 0)
                .collect();
            needs.sort_by_key(|index| (-deficits[*index], *index));
            for (ordinal, unit) in units.iter().enumerate() {
                let command = needs
                    .get(ordinal % needs.len().max(1))
                    .and_then(|resource| {
                        funding_command(game, player, unit, &deficits, *resource, &mut reserved)
                    })
                    .or_else(|| {
                        production_command(
                            game,
                            player,
                            unit,
                            ordinal < self.config.farmer_count,
                            self.config.fell_start,
                            &mut reserved,
                        )
                    });
                if let Some(command) = command {
                    commands.push(command);
                }
            }
        } else {
            for (ordinal, unit) in units.iter().enumerate() {
                if let Some(command) = production_command(
                    game,
                    player,
                    unit,
                    ordinal < self.config.farmer_count,
                    self.config.fell_start,
                    &mut reserved,
                ) {
                    commands.push(command);
                }
            }
        }
        if train_now {
            let spec = next_spec.expect("training spec");
            commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }
        commands
    }
}

impl Strategy for LegendFieldProxyV2 {
    fn name(&self) -> &str {
        "legend_field_proxy_v2"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        let workers = units.len();
        let next_spec = match workers {
            1 => Some(self.config.producer_spec),
            2 => Some(self.config.chopper_spec),
            _ => None,
        };
        let next_cost = next_spec.map(|spec| training_cost(workers as i32, spec));
        let train_now = next_cost
            .as_ref()
            .is_some_and(|cost| affordable(game, player, cost));
        let pending_cost = next_cost.as_ref().filter(|_| !train_now);
        let mut deficits = [0; 6];
        if let Some(cost) = pending_cost {
            for index in PLUM..=APPLE {
                deficits[index] = (cost[index] - game.inventories[player][index]).max(0);
            }
            if !game.iron.is_empty() {
                deficits[IRON] = (cost[IRON] - game.inventories[player][IRON]).max(0);
            }
        }
        let mut needs: Vec<_> = (PLUM..=APPLE)
            .chain(std::iter::once(IRON))
            .filter(|index| deficits[*index] > 0)
            .collect();
        needs.sort_by_key(|index| (-deficits[*index], *index));

        let mut reserved = HashSet::new();
        let mut commands = Vec::new();
        for (ordinal, unit) in units.iter().enumerate() {
            let wood_role =
                ordinal >= 2 || (ordinal == 1 && self.config.late_chop && game.turn >= 150);
            let command = if wood_role {
                v2_chopper_command(game, player, unit, &mut reserved)
            } else {
                let preferred = needs.get(ordinal % needs.len().max(1)).copied();
                v2_producer_command(
                    game,
                    player,
                    unit,
                    preferred,
                    &deficits,
                    pending_cost,
                    &mut reserved,
                )
            };
            if let Some(command) = command {
                commands.push(command);
            }
        }
        if train_now {
            let spec = next_spec.expect("v2 training spec");
            commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
        }
        commands
    }
}

fn v3_producer_priority(game: &GameState, unit: &Unit) -> (i32, i32, i32, i32, i32) {
    let carried_fruit: i32 = unit.carry[..WOOD].iter().sum();
    let standing_on_ripe = i32::from(
        game.plants
            .iter()
            .any(|plant| plant.pos() == unit.pos() && plant.fruits > 0),
    );
    let distance = bfs(game, unit.pos());
    let ripe_distance = v2_ripe_target(game, unit, &distance, &HashSet::new(), None)
        .and_then(|target| distance.get(&target).copied())
        .unwrap_or(i32::MAX / 4);
    (
        -carried_fruit,
        -standing_on_ripe,
        ripe_distance,
        -unit.hp,
        unit.id,
    )
}

fn v6_lemon_source_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    reserved: &mut HashSet<Cell>,
) -> Option<String> {
    let distance = bfs(game, unit.pos());
    if endgame_bank(game, player, unit, &distance) {
        return Some(bank_command(game, player, unit, &distance));
    }

    if unit.carry[LEMON] > 0 {
        let target = planting_target(
            game,
            player,
            unit,
            &distance,
            reserved,
            v2_farm_cap(game.turn),
            6,
        )?;
        reserved.insert(target);
        return Some(if target == unit.pos() {
            format!("PLANT {} LEMON", unit.id)
        } else {
            format!("MOVE {} {} {}", unit.id, target.0, target.1)
        });
    }

    if unit.total() > 0 {
        return None;
    }
    if manhattan(unit.pos(), game.shacks[player]) <= 1 && game.inventories[player][LEMON] > 0 {
        return Some(format!("PICK {} LEMON", unit.id));
    }
    if unit.hp <= 0 {
        return None;
    }
    let target = funding_target(game, unit, LEMON, &distance, reserved)?;
    reserved.insert(target);
    Some(if target == unit.pos() {
        format!("HARVEST {}", unit.id)
    } else {
        format!("MOVE {} {} {}", unit.id, target.0, target.1)
    })
}

fn post_stock_deficits(game: &GameState, player: usize, cost: &[i32; 6]) -> [i32; 6] {
    let mut available = game.inventories[player];
    for unit in game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
    {
        for resource in PLUM..=IRON {
            available[resource] += unit.carry[resource];
        }
    }
    for plant in &game.plants {
        if let Some(resource) = FRUIT_NAMES
            .iter()
            .position(|name| *name == plant.plant_type)
        {
            available[resource] += plant.fruits;
        }
    }

    let mut deficits = [0; 6];
    for resource in PLUM..=APPLE {
        deficits[resource] = (cost[resource] - available[resource]).max(0);
    }
    if !game.iron.is_empty() {
        deficits[IRON] = (cost[IRON] - available[IRON]).max(0);
    }
    deficits
}

fn v7_exact_coordinate_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    resource: usize,
    uncovered: i32,
    deposited_deficits: &[i32; 6],
    reserved: &mut HashSet<Cell>,
) -> Option<String> {
    let distance = bfs(game, unit.pos());
    if endgame_bank(game, player, unit, &distance) {
        return Some(bank_command(game, player, unit, &distance));
    }

    let source_gap = if resource <= APPLE {
        let required_sources = (uncovered + MAX_FRUITS - 1) / MAX_FRUITS;
        standing_farm_kind(game, player, 6, FRUIT_NAMES[resource]) < required_sources as usize
    } else {
        false
    };
    if source_gap && unit.carry[resource] > 0 {
        let target = planting_target(
            game,
            player,
            unit,
            &distance,
            reserved,
            v2_farm_cap(game.turn),
            6,
        )?;
        reserved.insert(target);
        return Some(if target == unit.pos() {
            format!("PLANT {} {}", unit.id, FRUIT_NAMES[resource])
        } else {
            format!("MOVE {} {} {}", unit.id, target.0, target.1)
        });
    }

    if unit.total() > 0 {
        return useful_funding_cargo(unit, deposited_deficits)
            .then(|| bank_command(game, player, unit, &distance));
    }
    if source_gap
        && manhattan(unit.pos(), game.shacks[player]) <= 1
        && game.inventories[player][resource] > 0
    {
        return Some(format!("PICK {} {}", unit.id, FRUIT_NAMES[resource]));
    }
    if resource <= APPLE && unit.hp <= 0 {
        return None;
    }
    funding_command(game, player, unit, deposited_deficits, resource, reserved)
}

fn v3_commands(
    config: LegendFieldProxyV3Config,
    game: &GameState,
    player: usize,
    reserve_affordable_bill: bool,
    shared_pick_ledger: bool,
    lemon_source_builder: bool,
    exact_deficit_vector: bool,
) -> Vec<String> {
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect();
    units.sort_by_key(|unit| unit.id);
    let workers = units.len();
    let next_spec = if workers == 1 {
        Some(config.first_spec)
    } else if workers < config.max_workers {
        Some((2, 3, 1, 2))
    } else {
        None
    };
    let next_cost = next_spec.map(|spec| training_cost(workers as i32, spec));
    let train_now = next_cost
        .as_ref()
        .is_some_and(|cost| affordable(game, player, cost));
    let pending_cost = next_cost.as_ref().filter(|_| !train_now);
    let producer_cost = if reserve_affordable_bill {
        next_cost.as_ref()
    } else {
        pending_cost
    };
    let mut deficits = [0; 6];
    if let Some(cost) = pending_cost {
        for index in PLUM..=APPLE {
            deficits[index] = (cost[index] - game.inventories[player][index]).max(0);
        }
        if !game.iron.is_empty() {
            deficits[IRON] = (cost[IRON] - game.inventories[player][IRON]).max(0);
        }
    }
    let mut needs: Vec<_> = (PLUM..=APPLE)
        .chain(std::iter::once(IRON))
        .filter(|index| deficits[*index] > 0)
        .collect();
    needs.sort_by_key(|index| (-deficits[*index], *index));

    let producer_quota = if pending_cost.is_some() {
        workers.min(2)
    } else {
        workers.min(config.post_producers)
    };
    let mut producer_rank = units.clone();
    producer_rank.sort_by_key(|unit| v3_producer_priority(game, unit));
    let producer_ids: HashSet<_> = producer_rank
        .iter()
        .take(producer_quota)
        .map(|unit| unit.id)
        .collect();
    let lemon_builder_id = if lemon_source_builder && workers >= 2 {
        pending_cost.and_then(|cost| {
            let lemon_floor = (cost[LEMON] + MAX_FRUITS - 1) / MAX_FRUITS;
            (standing_farm_kind(game, player, 6, FRUIT_NAMES[LEMON]) < lemon_floor as usize)
                .then(|| producer_rank.first().map(|unit| unit.id))
                .flatten()
        })
    } else {
        None
    };
    let vector_assignments: HashMap<_, _> = if exact_deficit_vector && workers >= 2 {
        pending_cost
            .map(|cost| {
                let uncovered = post_stock_deficits(game, player, cost);
                let mut resources: Vec<_> = (PLUM..=APPLE)
                    .chain(std::iter::once(IRON))
                    .filter(|resource| uncovered[*resource] > 0)
                    .collect();
                resources.sort_by_key(|resource| (-uncovered[*resource], *resource));
                producer_rank
                    .iter()
                    .take(producer_quota)
                    .zip(resources)
                    .map(|(unit, resource)| (unit.id, (resource, uncovered[resource])))
                    .collect()
            })
            .unwrap_or_default()
    } else {
        HashMap::new()
    };

    let mut reserved = HashSet::new();
    let mut commands = Vec::new();
    let mut planning_game = game.clone();
    let mut producer_ordinal = 0;
    for unit in units {
        let producer = producer_ids.contains(&unit.id);
        let preferred = needs.get(producer_ordinal % needs.len().max(1)).copied();
        if producer {
            producer_ordinal += 1;
        }
        let planning_view = if shared_pick_ledger {
            &planning_game
        } else {
            game
        };
        let source_command =
            if let Some((resource, uncovered)) = vector_assignments.get(&unit.id).copied() {
                v7_exact_coordinate_command(
                    planning_view,
                    player,
                    unit,
                    resource,
                    uncovered,
                    &deficits,
                    &mut reserved,
                )
            } else if lemon_builder_id == Some(unit.id) {
                v6_lemon_source_command(planning_view, player, unit, &mut reserved)
            } else {
                None
            };
        let command = if source_command.is_some() {
            source_command
        } else if producer {
            v2_producer_command(
                planning_view,
                player,
                unit,
                preferred,
                &deficits,
                producer_cost,
                &mut reserved,
            )
            .or_else(|| v2_chopper_command(planning_view, player, unit, &mut reserved))
        } else {
            v2_chopper_command(planning_view, player, unit, &mut reserved).or_else(|| {
                v2_producer_command(
                    planning_view,
                    player,
                    unit,
                    preferred,
                    &deficits,
                    producer_cost,
                    &mut reserved,
                )
            })
        };
        if shared_pick_ledger {
            if let Some(command) = command.as_deref() {
                let fields: Vec<_> = command.split_whitespace().collect();
                if fields.len() == 3 && fields[0] == "PICK" {
                    let resource = item_index(fields[2]);
                    assert!(
                        planning_game.inventories[player][resource] > 0,
                        "planned PICK must have inventory"
                    );
                    planning_game.inventories[player][resource] -= 1;
                }
            }
        }
        if let Some(command) = command {
            commands.push(command);
        }
    }
    if train_now {
        let spec = next_spec.expect("V3-V7 training spec");
        commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
    }
    commands
}

fn v8_materialization_target(
    game: &GameState,
    unit: &Unit,
    resource: usize,
    reserved: &HashSet<Cell>,
) -> Option<Cell> {
    let distance = bfs(game, unit.pos());
    if resource <= APPLE {
        game.plants
            .iter()
            .filter(|plant| {
                plant.plant_type == FRUIT_NAMES[resource]
                    && distance.contains_key(&plant.pos())
                    && !reserved.contains(&plant.pos())
            })
            .min_by_key(|plant| {
                (
                    i32::from(plant.fruits <= 0),
                    distance[&plant.pos()],
                    plant.cooldown,
                    plant.pos(),
                )
            })
            .map(|plant| plant.pos())
    } else {
        funding_target(game, unit, IRON, &distance, reserved)
    }
}

fn v8_lease_valid(game: &GameState, lease: MaterializationLease, deficits: &[i32; 6]) -> bool {
    if deficits[lease.resource] <= 0 {
        return false;
    }
    if lease.resource <= APPLE {
        game.plants.iter().any(|plant| {
            plant.pos() == lease.target && plant.plant_type == FRUIT_NAMES[lease.resource]
        })
    } else {
        game.walkable.contains(&lease.target)
            && game
                .iron
                .iter()
                .any(|cell| manhattan(*cell, lease.target) == 1)
    }
}

fn v8_lease_command(game: &GameState, unit: &Unit, lease: MaterializationLease) -> Option<String> {
    if unit.pos() != lease.target {
        return Some(format!(
            "MOVE {} {} {}",
            unit.id, lease.target.0, lease.target.1
        ));
    }
    if lease.resource <= APPLE {
        game.plants
            .iter()
            .find(|plant| plant.pos() == lease.target)
            .filter(|plant| plant.fruits > 0 && unit.hp > 0)
            .map(|_| format!("HARVEST {}", unit.id))
    } else if unit.chop > 0
        && game
            .iron
            .iter()
            .any(|cell| manhattan(*cell, unit.pos()) == 1)
    {
        Some(format!("MINE {}", unit.id))
    } else {
        None
    }
}

fn v8_commands(
    config: LegendFieldProxyV3Config,
    leases: &RefCell<HashMap<i32, MaterializationLease>>,
    game: &GameState,
    player: usize,
) -> Vec<String> {
    if game.turn == 1 {
        leases.borrow_mut().clear();
    }
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect();
    units.sort_by_key(|unit| unit.id);
    let workers = units.len();
    let next_cost = (workers == 2 && workers < config.max_workers)
        .then(|| training_cost(workers as i32, (2, 3, 1, 2)));
    let train_now = next_cost
        .as_ref()
        .is_some_and(|cost| affordable(game, player, cost));
    if next_cost.is_none() || train_now {
        leases.borrow_mut().clear();
        return v3_commands(config, game, player, true, true, false, false);
    }

    let cost = next_cost.expect("pending worker-three cost");
    let mut deficits = [0; 6];
    for resource in PLUM..=APPLE {
        deficits[resource] = (cost[resource] - game.inventories[player][resource]).max(0);
    }
    if !game.iron.is_empty() {
        deficits[IRON] = (cost[IRON] - game.inventories[player][IRON]).max(0);
    }
    let mut needs: Vec<_> = (PLUM..=APPLE)
        .chain(std::iter::once(IRON))
        .filter(|resource| deficits[*resource] > 0)
        .collect();
    needs.sort_by_key(|resource| (-deficits[*resource], *resource));

    let mut producer_rank = units.clone();
    producer_rank.sort_by_key(|unit| v3_producer_priority(game, unit));
    let old_leases = leases.borrow().clone();
    let mut next_leases = HashMap::new();
    let mut reserved_targets = HashSet::new();
    let mut leased_resources = HashSet::new();
    for unit in &producer_rank {
        let Some(lease) = old_leases.get(&unit.id).copied() else {
            continue;
        };
        if unit.total() == 0
            && v8_lease_valid(game, lease, &deficits)
            && !reserved_targets.contains(&lease.target)
            && !leased_resources.contains(&lease.resource)
        {
            reserved_targets.insert(lease.target);
            leased_resources.insert(lease.resource);
            next_leases.insert(unit.id, lease);
        }
    }
    for unit in &producer_rank {
        if unit.total() > 0 || next_leases.contains_key(&unit.id) {
            continue;
        }
        for resource in &needs {
            if leased_resources.contains(resource) {
                continue;
            }
            let Some(target) = v8_materialization_target(game, unit, *resource, &reserved_targets)
            else {
                continue;
            };
            let lease = MaterializationLease {
                resource: *resource,
                target,
            };
            reserved_targets.insert(target);
            leased_resources.insert(*resource);
            next_leases.insert(unit.id, lease);
            break;
        }
    }
    *leases.borrow_mut() = next_leases.clone();

    let mut commands = Vec::new();
    for unit in units {
        let command = if unit.total() > 0 {
            let distance = bfs(game, unit.pos());
            Some(bank_command(game, player, unit, &distance))
        } else {
            next_leases
                .get(&unit.id)
                .and_then(|lease| v8_lease_command(game, unit, *lease))
        };
        if let Some(command) = command {
            commands.push(command);
        }
    }
    commands
}

impl Strategy for LegendFieldProxyV3 {
    fn name(&self) -> &str {
        "legend_field_proxy_v3"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        v3_commands(self.config, game, player, false, false, false, false)
    }
}

impl Strategy for LegendFieldProxyV4 {
    fn name(&self) -> &str {
        "legend_field_proxy_v4"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        v3_commands(self.config, game, player, true, false, false, false)
    }
}

impl Strategy for LegendFieldProxyV5 {
    fn name(&self) -> &str {
        "legend_field_proxy_v5"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        v3_commands(self.config, game, player, true, true, false, false)
    }
}

impl Strategy for LegendFieldProxyV6 {
    fn name(&self) -> &str {
        "legend_field_proxy_v6"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        v3_commands(self.config, game, player, true, true, true, false)
    }
}

impl Strategy for LegendFieldProxyV7 {
    fn name(&self) -> &str {
        "legend_field_proxy_v7"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        v3_commands(self.config, game, player, true, true, false, true)
    }
}

impl Strategy for LegendFieldProxyV8 {
    fn name(&self) -> &str {
        "legend_field_proxy_v8"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        v8_commands(self.config, &self.leases, game, player)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::state::{Plant, Unit};

    fn state() -> GameState {
        GameState {
            width: 3,
            height: 3,
            walkable: (0..3).flat_map(|x| (0..3).map(move |y| (x, y))).collect(),
            shacks: [(0, 1), (2, 1)],
            inventories: [[20; 6], [0; 6]],
            units: vec![Unit {
                id: 0,
                player: 0,
                x: 1,
                y: 1,
                ms: 1,
                cc: 1,
                hp: 1,
                chop: 1,
                carry: [0; 6],
            }],
            plants: Vec::new(),
            scores: [0; 2],
            turn: 1,
            next_id: 1,
            iron: HashSet::new(),
            water: HashSet::new(),
        }
    }

    fn add_worker(game: &mut GameState, id: i32, x: i32, y: i32) {
        game.units.push(Unit {
            id,
            player: 0,
            x,
            y,
            ms: 2,
            cc: 3,
            hp: 1,
            chop: 2,
            carry: [0; 6],
        });
    }

    #[test]
    fn affordable_opening_emits_frozen_first_spec() {
        let config = LegendFieldProxyConfig {
            ladder: [(2, 2, 2, 1), (2, 3, 1, 2), (2, 3, 1, 2)],
            farmer_count: 2,
            fell_start: 100,
        };
        let commands = LegendFieldProxy::configured(config).decide(&state(), 0);
        assert!(commands.iter().any(|command| command == "TRAIN 2 2 2 1"));
    }

    #[test]
    fn v2_emits_producer_but_never_a_fourth_worker() {
        let config = LegendFieldProxyV2Config {
            producer_spec: (2, 2, 2, 1),
            chopper_spec: (2, 2, 0, 2),
            late_chop: false,
        };
        let policy = LegendFieldProxyV2::configured(config);
        let opening = policy.decide(&state(), 0);
        assert!(opening.iter().any(|command| command == "TRAIN 2 2 2 1"));

        let mut three = state();
        three.units.push(Unit {
            id: 1,
            player: 0,
            x: 1,
            y: 0,
            ms: 2,
            cc: 2,
            hp: 2,
            chop: 1,
            carry: [0; 6],
        });
        three.units.push(Unit {
            id: 2,
            player: 0,
            x: 1,
            y: 2,
            ms: 2,
            cc: 2,
            hp: 0,
            chop: 2,
            carry: [0; 6],
        });
        assert!(!policy
            .decide(&three, 0)
            .iter()
            .any(|command| command.starts_with("TRAIN ")));
    }

    #[test]
    fn v3_affordable_openings_emit_each_frozen_first_spec() {
        for first_spec in [(2, 2, 2, 1), (2, 2, 1, 1)] {
            let policy = LegendFieldProxyV3::configured(LegendFieldProxyV3Config {
                first_spec,
                max_workers: 3,
                post_producers: 1,
            });
            let expected = format!(
                "TRAIN {} {} {} {}",
                first_spec.0, first_spec.1, first_spec.2, first_spec.3
            );
            assert!(policy
                .decide(&state(), 0)
                .iter()
                .any(|command| command == &expected));
        }
    }

    #[test]
    fn v3_obeys_three_worker_cap_and_uses_hybrid_fourth_spec() {
        let mut three = state();
        add_worker(&mut three, 1, 1, 0);
        add_worker(&mut three, 2, 1, 2);

        let capped = LegendFieldProxyV3::configured(LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 1,
        });
        assert!(!capped
            .decide(&three, 0)
            .iter()
            .any(|command| command.starts_with("TRAIN ")));

        let four_worker = LegendFieldProxyV3::configured(LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 4,
            post_producers: 1,
        });
        assert!(four_worker
            .decide(&three, 0)
            .iter()
            .any(|command| command == "TRAIN 2 3 1 2"));
    }

    #[test]
    fn v4_reserves_exact_affordable_bill_while_v3_spends_it() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = training_cost(2, (2, 3, 1, 2));
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v3 = LegendFieldProxyV3::configured(config).decide(&two, 0);
        let v4 = LegendFieldProxyV4::configured(config).decide(&two, 0);
        assert!(v3.iter().any(|command| command.starts_with("PICK ")));
        assert!(!v4.iter().any(|command| command.starts_with("PICK ")));
        assert!(v3.iter().any(|command| command == "TRAIN 2 3 1 2"));
        assert!(v4.iter().any(|command| command == "TRAIN 2 3 1 2"));
    }

    #[test]
    fn v5_shared_pick_ledger_preserves_train_bill_across_workers() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = training_cost(2, (2, 3, 1, 2));
        two.inventories[0][LEMON] += 1;
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v4 = LegendFieldProxyV4::configured(config).decide(&two, 0);
        let v5 = LegendFieldProxyV5::configured(config).decide(&two, 0);
        assert_eq!(
            v4.iter()
                .filter(|command| command.as_str() == "PICK 0 LEMON"
                    || command.as_str() == "PICK 1 LEMON")
                .count(),
            2
        );
        assert_eq!(
            v5.iter()
                .filter(|command| command.as_str() == "PICK 0 LEMON"
                    || command.as_str() == "PICK 1 LEMON")
                .count(),
            1
        );

        let mut v4_state = two.clone();
        crate::game::engine::step(&mut v4_state, &v4, &[]);
        assert_eq!(
            v4_state
                .units
                .iter()
                .filter(|unit| unit.player == 0)
                .count(),
            2
        );
        let mut v5_state = two;
        crate::game::engine::step(&mut v5_state, &v5, &[]);
        assert_eq!(
            v5_state
                .units
                .iter()
                .filter(|unit| unit.player == 0)
                .count(),
            3
        );
    }

    #[test]
    fn v6_invests_one_deposited_lemon_while_v5_preserves_the_pending_bill() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = [0; 6];
        two.inventories[0][LEMON] = 1;
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v5 = LegendFieldProxyV5::configured(config).decide(&two, 0);
        let v6 = LegendFieldProxyV6::configured(config).decide(&two, 0);
        assert!(!v5
            .iter()
            .any(|command| command.starts_with("PICK ") && command.ends_with(" LEMON")));
        assert!(v6
            .iter()
            .any(|command| command.starts_with("PICK ") && command.ends_with(" LEMON")));
    }

    #[test]
    fn v6_plants_carried_lemon_while_v5_banks_it_for_the_pending_bill() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = [0; 6];
        two.units[0].carry[LEMON] = 1;
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v5 = LegendFieldProxyV5::configured(config).decide(&two, 0);
        let v6 = LegendFieldProxyV6::configured(config).decide(&two, 0);
        assert!(v5.iter().any(|command| command == "DROP 0"));
        assert!(v6.iter().any(|command| command == "PLANT 0 LEMON"));
    }

    #[test]
    fn v7_invests_a_plum_only_post_stock_deficit() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = training_cost(2, (2, 3, 1, 2));
        two.inventories[0][PLUM] = 1;
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v5 = LegendFieldProxyV5::configured(config).decide(&two, 0);
        let v7 = LegendFieldProxyV7::configured(config).decide(&two, 0);
        assert!(!v5.iter().any(|command| command.ends_with(" PLUM")));
        assert!(v7.iter().any(|command| command == "PICK 0 PLUM"));
    }

    #[test]
    fn v7_funds_an_iron_only_post_stock_deficit() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.iron.insert((1, 0));
        two.inventories[0] = training_cost(2, (2, 3, 1, 2));
        two.inventories[0][IRON] = 0;
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v7 = LegendFieldProxyV7::configured(config).decide(&two, 0);
        assert!(v7.iter().any(|command| command == "MINE 0"));
    }

    #[test]
    fn v7_assigns_two_ranked_producers_distinct_uncovered_coordinates() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = training_cost(2, (2, 3, 1, 2));
        two.inventories[0][PLUM] = 1;
        two.inventories[0][LEMON] = 1;
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v7 = LegendFieldProxyV7::configured(config).decide(&two, 0);
        assert!(v7.iter().any(|command| command == "PICK 0 LEMON"));
        assert!(v7.iter().any(|command| command == "PICK 1 PLUM"));
    }

    #[test]
    fn v7_disables_the_vector_for_an_affordable_bill() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = training_cost(2, (2, 3, 1, 2));
        two.inventories[0][LEMON] += 1;
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v5 = LegendFieldProxyV5::configured(config).decide(&two, 0);
        let v7 = LegendFieldProxyV7::configured(config).decide(&two, 0);
        assert_eq!(v7, v5);
        assert!(v7.iter().any(|command| command == "TRAIN 2 3 1 2"));
    }

    #[test]
    fn v8_banks_cargo_before_materialization_leases() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = [0; 6];
        two.units[0].carry[PLUM] = 1;
        let policy = LegendFieldProxyV8::configured(LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        });
        assert!(policy
            .decide(&two, 0)
            .iter()
            .any(|command| command == "DROP 0"));
    }

    #[test]
    fn v8_assigns_distinct_existing_bill_sources_without_pick_or_plant() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = [0; 6];
        two.plants = vec![
            Plant {
                plant_type: "LEMON".into(),
                x: 1,
                y: 1,
                size: 1,
                health: 2,
                fruits: 3,
                cooldown: 0,
            },
            Plant {
                plant_type: "PLUM".into(),
                x: 0,
                y: 0,
                size: 1,
                health: 2,
                fruits: 3,
                cooldown: 0,
            },
        ];
        let policy = LegendFieldProxyV8::configured(LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        });
        let commands = policy.decide(&two, 0);
        assert!(commands.iter().any(|command| command == "HARVEST 0"));
        assert!(commands.iter().any(|command| command == "HARVEST 1"));
        assert!(!commands
            .iter()
            .any(|command| command.starts_with("PICK ") || command.starts_with("PLANT ")));
    }

    #[test]
    fn v8_keeps_an_unripe_lease_until_it_becomes_harvestable() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = training_cost(2, (2, 3, 1, 2));
        two.inventories[0][LEMON] = 0;
        two.plants.push(Plant {
            plant_type: "LEMON".into(),
            x: 2,
            y: 2,
            size: 1,
            health: 2,
            fruits: 0,
            cooldown: 2,
        });
        let policy = LegendFieldProxyV8::configured(LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        });
        assert!(policy
            .decide(&two, 0)
            .iter()
            .any(|command| command == "MOVE 0 2 2"));

        two.turn = 2;
        two.plants.push(Plant {
            plant_type: "LEMON".into(),
            x: 1,
            y: 1,
            size: 1,
            health: 2,
            fruits: 3,
            cooldown: 0,
        });
        assert!(policy
            .decide(&two, 0)
            .iter()
            .any(|command| command == "MOVE 0 2 2"));

        two.turn = 3;
        two.units[0].x = 2;
        two.units[0].y = 2;
        two.plants[0].fruits = 1;
        assert!(policy
            .decide(&two, 0)
            .iter()
            .any(|command| command == "HARVEST 0"));
    }

    #[test]
    fn v8_affordable_bill_exactly_matches_v5_and_trains() {
        let mut two = state();
        add_worker(&mut two, 1, 0, 0);
        two.inventories[0] = training_cost(2, (2, 3, 1, 2));
        two.inventories[0][LEMON] += 1;
        let config = LegendFieldProxyV3Config {
            first_spec: (2, 2, 2, 1),
            max_workers: 3,
            post_producers: 2,
        };
        let v5 = LegendFieldProxyV5::configured(config).decide(&two, 0);
        let v8 = LegendFieldProxyV8::configured(config).decide(&two, 0);
        assert_eq!(v8, v5);
        assert!(v8.iter().any(|command| command == "TRAIN 2 3 1 2"));
    }
}
