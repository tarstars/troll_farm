//! Architecture-2 Phase-1 economy skeleton.
//!
//! This file is intentionally not registered in `game/mod.rs`: that file is part of the
//! frozen A2-0b dependency lock. The A2-1 runner includes this module with `#[path]`.

use std::collections::{BTreeMap, BTreeSet};

use troll_farm::game::engine::{
    bfs_distances, training_cost, APPLE, BANANA, IRON, LEMON, PLUM,
};
use troll_farm::game::state::{Cell, GameState, Unit};

const BILL_SPECIES: [usize; 3] = [PLUM, LEMON, APPLE];
const FRUIT_NAMES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "BANANA"];
const WORKER_SPEC: (i32, i32, i32, i32) = (1, 1, 1, 1);
const LATE_PLANT_START: i32 = 190;
const LIQUIDATE_START: i32 = 235;

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct EconomyMetrics {
    pub own_generations_created: u32,
    pub own_crop_harvested: [i32; 4],
    pub own_crop_banked: [i32; 4],
    pub own_crop_banked_available: [i32; 4],
    pub first_worker3_turn: Option<i32>,
    pub fruit_funded_worker3: bool,
    pub worker3_bill: Option<[i32; 6]>,
    pub worker3_bill_needs_owned_fruit: bool,
    pub mined_iron_roster2: i32,
    pub mined_iron_roster3plus: i32,
    pub iron_directed_moves: u32,
}

impl EconomyMetrics {
    pub fn own_bill_fruit_harvested(&self) -> i32 {
        BILL_SPECIES
            .iter()
            .map(|index| self.own_crop_harvested[*index])
            .sum()
    }

    pub fn own_bill_fruit_banked(&self) -> i32 {
        BILL_SPECIES
            .iter()
            .map(|index| self.own_crop_banked[*index])
            .sum()
    }
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct OwnedGeneration {
    plant_type: String,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct PlantJob {
    target: Cell,
    item: usize,
}

#[derive(Debug, Default)]
pub struct EconomySkeleton {
    player: Option<usize>,
    owned: BTreeMap<Cell, OwnedGeneration>,
    jobs: BTreeMap<i32, PlantJob>,
    owned_carry: BTreeMap<i32, [i32; 4]>,
    metrics: EconomyMetrics,
}

impl EconomySkeleton {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn metrics(&self) -> &EconomyMetrics {
        &self.metrics
    }

    fn bind_player(&mut self, player: usize) {
        match self.player {
            None => self.player = Some(player),
            Some(bound) => assert_eq!(bound, player, "A2 bot instance changed seats"),
        }
    }

    fn own_units<'a>(&self, game: &'a GameState, player: usize) -> Vec<&'a Unit> {
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        units
    }

    fn worker_count(&self, game: &GameState, player: usize) -> usize {
        game.units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .count()
    }

    fn near_shack(game: &GameState, player: usize, cell: Cell) -> bool {
        Self::manhattan(game.shacks[player], cell) <= 1
    }

    fn manhattan(left: Cell, right: Cell) -> i32 {
        (left.0 - right.0).abs() + (left.1 - right.1).abs()
    }

    fn affordable(game: &GameState, player: usize, spec: (i32, i32, i32, i32)) -> bool {
        let roster = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .count() as i32;
        let cost = training_cost(roster, spec);
        cost.iter()
            .enumerate()
            .all(|(index, amount)| game.inventories[player][index] >= *amount)
    }

    fn plant_index(name: &str) -> Option<usize> {
        match name {
            "PLUM" => Some(PLUM),
            "LEMON" => Some(LEMON),
            "APPLE" => Some(APPLE),
            "BANANA" => Some(BANANA),
            _ => None,
        }
    }

    fn plant_at<'a>(game: &'a GameState, cell: Cell) -> Option<&'a troll_farm::game::state::Plant> {
        game.plants.iter().find(|plant| plant.pos() == cell)
    }

    fn adjacent_to_water(game: &GameState, cell: Cell) -> bool {
        game.water
            .iter()
            .any(|water| Self::manhattan(*water, cell) == 1)
    }

    fn shack_doors(game: &GameState, player: usize) -> Vec<Cell> {
        let (x, y) = game.shacks[player];
        let mut doors: Vec<_> = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
            .into_iter()
            .filter(|cell| game.walkable.contains(cell))
            .collect();
        doors.sort_unstable();
        doors
    }

    fn evacuation_target(
        &self,
        game: &GameState,
        player: usize,
        unit_id: i32,
        reserved: &BTreeSet<Cell>,
    ) -> Option<Cell> {
        Self::shack_doors(game, player).into_iter().find(|cell| {
            !reserved.contains(cell)
                && !game
                    .units
                    .iter()
                    .any(|unit| unit.id != unit_id && unit.player as usize == player && unit.pos() == *cell)
            })
    }

    fn move_command(
        game: &GameState,
        player: usize,
        unit: &Unit,
        goal: Cell,
        reserved_moves: &mut BTreeSet<Cell>,
    ) -> Option<String> {
        let goal_sources = if game.walkable.contains(&goal) {
            vec![goal]
        } else if goal == game.shacks[player] {
            Self::shack_doors(game, player)
        } else {
            let reachable = bfs_distances(&game.walkable, &[unit.pos()]);
            let best = reachable
                .keys()
                .map(|cell| Self::manhattan(*cell, goal))
                .min()?;
            reachable
                .keys()
                .filter(|cell| Self::manhattan(**cell, goal) == best)
                .copied()
                .collect()
        };
        let goal_dist = bfs_distances(&game.walkable, &goal_sources);
        let (x, y) = unit.pos();
        let occupied: BTreeSet<_> = game
            .units
            .iter()
            .filter(|other| {
                other.player as usize == player && other.id != unit.id
            })
            .map(Unit::pos)
            .collect();
        let target = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
            .into_iter()
            .filter(|cell| game.walkable.contains(cell))
            .filter(|cell| !occupied.contains(cell))
            .filter(|cell| !reserved_moves.contains(cell))
            .filter_map(|cell| Some((goal_dist.get(&cell).copied()?, cell)))
            .min()
            .map(|(_, cell)| cell)?;
        reserved_moves.insert(target);
        Some(format!("MOVE {} {} {}", unit.id, target.0, target.1))
    }

    fn target_cell(
        &self,
        game: &GameState,
        player: usize,
        from: Cell,
        reserved: &BTreeSet<Cell>,
    ) -> Option<Cell> {
        let from_dist = bfs_distances(&game.walkable, &[from]);
        let shack_sources = Self::shack_doors(game, player);
        let shack_dist = bfs_distances(&game.walkable, &shack_sources);
        game.walkable
            .iter()
            .filter(|cell| from_dist.contains_key(*cell))
            .filter(|cell| !reserved.contains(*cell))
            .filter(|cell| Self::plant_at(game, **cell).is_none())
            .filter(|cell| !game.units.iter().any(|unit| unit.pos() == **cell))
            .min_by_key(|cell| {
                (
                    u8::from(!Self::adjacent_to_water(game, **cell)),
                    shack_dist.get(*cell).copied().unwrap_or(10_000),
                    from_dist.get(*cell).copied().unwrap_or(10_000),
                    **cell,
                )
            })
            .copied()
    }

    fn nearest_ripe_plant(
        &self,
        game: &GameState,
        from: Cell,
        reserved: &BTreeSet<Cell>,
    ) -> Option<Cell> {
        let distances = bfs_distances(&game.walkable, &[from]);
        game.plants
            .iter()
            .filter(|plant| plant.fruits > 0)
            .filter(|plant| !reserved.contains(&plant.pos()))
            .filter_map(|plant| {
                let cell = plant.pos();
                Some((
                    u8::from(!self.owned.contains_key(&cell)),
                    distances.get(&cell).copied()?,
                    cell,
                ))
            })
            .min()
            .map(|(_, _, cell)| cell)
    }

    fn nearest_owned_crop(
        &self,
        game: &GameState,
        from: Cell,
        reserved: &BTreeSet<Cell>,
    ) -> Option<Cell> {
        let distances = bfs_distances(&game.walkable, &[from]);
        self.owned
            .keys()
            .filter(|cell| !reserved.contains(*cell))
            .filter_map(|cell| {
                let plant = Self::plant_at(game, *cell)?;
                Some((
                    distances.get(cell).copied()?,
                    plant.cooldown,
                    *cell,
                ))
            })
            .min()
            .map(|(_, _, cell)| cell)
    }

    fn nearest_chop_target(
        &self,
        game: &GameState,
        from: Cell,
        include_owned: bool,
    ) -> Option<Cell> {
        let distances = bfs_distances(&game.walkable, &[from]);
        game.plants
            .iter()
            .filter(|plant| include_owned || !self.owned.contains_key(&plant.pos()))
            .filter_map(|plant| {
                let cell = plant.pos();
                Some((distances.get(&cell).copied()?, cell))
            })
            .min()
            .map(|(_, cell)| cell)
    }

    fn clean_state(&mut self, game: &GameState, player: usize) {
        self.owned.retain(|cell, generation| {
            Self::plant_at(game, *cell)
                .is_some_and(|plant| plant.plant_type == generation.plant_type)
        });
        let unit_ids: BTreeSet<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .map(|unit| unit.id)
            .collect();
        self.jobs.retain(|unit_id, job| {
            unit_ids.contains(unit_id)
                && Self::plant_at(game, job.target).is_none()
                && game.walkable.contains(&job.target)
        });
        self.owned_carry
            .retain(|unit_id, _| unit_ids.contains(unit_id));
        if game.turn >= LIQUIDATE_START {
            self.jobs.clear();
        }
    }

    fn desired_species(&self, game: &GameState, roster: usize) -> Vec<(usize, usize)> {
        if game.turn >= LIQUIDATE_START {
            return Vec::new();
        }
        if game.turn >= LATE_PLANT_START {
            return vec![(BANANA, 4)];
        }
        let per_bill_species = if roster >= 3 { 2 } else { 1 };
        BILL_SPECIES
            .iter()
            .map(|item| (*item, per_bill_species))
            .collect()
    }

    fn live_and_planned_count(&self, item: usize) -> usize {
        let live = self
            .owned
            .values()
            .filter(|generation| Self::plant_index(&generation.plant_type) == Some(item))
            .count();
        let planned = self.jobs.values().filter(|job| job.item == item).count();
        live + planned
    }

    fn choose_job_species(
        &self,
        game: &GameState,
        player: usize,
        roster: usize,
        reserved_inventory: &[i32; 6],
    ) -> Option<usize> {
        self.desired_species(game, roster)
            .into_iter()
            .filter(|(item, desired)| {
                self.live_and_planned_count(*item) < *desired
                    && reserved_inventory[*item] > 0
            })
            .min_by_key(|(item, desired)| {
                (
                    self.live_and_planned_count(*item) * 100 / (*desired).max(1),
                    game.inventories[player][*item],
                    *item,
                )
            })
            .map(|(item, _)| item)
    }

    fn command_for_job(
        &self,
        game: &GameState,
        player: usize,
        unit: &Unit,
        job: &PlantJob,
        inventory: &mut [i32; 6],
        reserved_moves: &mut BTreeSet<Cell>,
    ) -> Option<String> {
        if unit.carry[job.item] > 0 {
            if unit.pos() == job.target {
                if Self::plant_at(game, job.target).is_none()
                    && game.walkable.contains(&job.target)
                {
                    return Some(format!(
                        "PLANT {} {}",
                        unit.id, FRUIT_NAMES[job.item]
                    ));
                }
                return None;
            }
            return Self::move_command(
                game,
                player,
                unit,
                job.target,
                reserved_moves,
            );
        }
        if unit.total() > 0 {
            return None;
        }
        if Self::near_shack(game, player, unit.pos()) && inventory[job.item] > 0 {
            inventory[job.item] -= 1;
            return Some(format!("PICK {} {}", unit.id, FRUIT_NAMES[job.item]));
        }
        Self::move_command(
            game,
            player,
            unit,
            game.shacks[player],
            reserved_moves,
        )
    }

    /// Return this turn's deterministic command list.
    pub fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        self.bind_player(player);
        self.clean_state(game, player);
        let units: Vec<Unit> = self
            .own_units(game, player)
            .into_iter()
            .cloned()
            .collect();
        let roster = units.len();
        let mut commands = Vec::new();
        let mut used = BTreeSet::new();
        let mut reserved_cells: BTreeSet<Cell> =
            self.jobs.values().map(|job| job.target).collect();
        let mut reserved_moves = BTreeSet::new();
        let mut reserved_service = BTreeSet::new();
        let mut inventory = game.inventories[player];

        let train_worker2 = roster == 1 && Self::affordable(game, player, WORKER_SPEC);
        let train_worker3 = roster == 2
            && self.metrics.own_bill_fruit_banked() > 0
            && Self::affordable(game, player, WORKER_SPEC);
        let train_now = train_worker2 || train_worker3;
        let mut train_legal_after_moves = train_now;

        if train_now {
            for unit in &units {
                if unit.pos() != game.shacks[player] {
                    continue;
                }
                let Some(target) =
                    self.evacuation_target(game, player, unit.id, &reserved_cells)
                else {
                    train_legal_after_moves = false;
                    break;
                };
                commands.push(format!("MOVE {} {} {}", unit.id, target.0, target.1));
                used.insert(unit.id);
                reserved_cells.insert(target);
                reserved_moves.insert(target);
            }
            if train_legal_after_moves {
                commands.push(format!(
                    "TRAIN {} {} {} {}",
                    WORKER_SPEC.0, WORKER_SPEC.1, WORKER_SPEC.2, WORKER_SPEC.3
                ));
            }
        }

        for unit in &units {
            if used.contains(&unit.id) {
                continue;
            }

            if unit.total() > 0 {
                if let Some(job) = self.jobs.get(&unit.id) {
                    if unit.carry[job.item] > 0 {
                        if let Some(command) =
                            self.command_for_job(
                                game,
                                player,
                                unit,
                                job,
                                &mut inventory,
                                &mut reserved_moves,
                            )
                        {
                            commands.push(command);
                        }
                        continue;
                    }
                }
                if Self::near_shack(game, player, unit.pos()) {
                    commands.push(format!("DROP {}", unit.id));
                } else {
                    if let Some(command) = Self::move_command(
                        game,
                        player,
                        unit,
                        game.shacks[player],
                        &mut reserved_moves,
                    ) {
                        commands.push(command);
                    }
                }
                continue;
            }

            if let Some(plant) = Self::plant_at(game, unit.pos()) {
                if plant.fruits > 0 && unit.hp > 0 {
                    commands.push(format!("HARVEST {}", unit.id));
                    continue;
                }
                if game.turn >= LIQUIDATE_START && unit.chop > 0 {
                    commands.push(format!("CHOP {}", unit.id));
                    continue;
                }
            }

            let near_iron = game
                .iron
                .iter()
                .any(|cell| Self::manhattan(*cell, unit.pos()) == 1);
            let mining_quota_open = (roster == 2
                && self.metrics.mined_iron_roster2 == 0)
                || (roster >= 3 && self.metrics.mined_iron_roster3plus < 3);
            if near_iron
                && mining_quota_open
                && unit.chop > 0
                && unit.free() > 0
            {
                commands.push(format!("MINE {}", unit.id));
                continue;
            }

            if let Some(job) = self.jobs.get(&unit.id) {
                if !train_now {
                    if let Some(command) =
                        self.command_for_job(
                            game,
                            player,
                            unit,
                            job,
                            &mut inventory,
                            &mut reserved_moves,
                        )
                    {
                        commands.push(command);
                    }
                    continue;
                }
            }

            if !train_now {
                if let Some(item) =
                    self.choose_job_species(game, player, roster, &inventory)
                {
                    if let Some(target) =
                        self.target_cell(game, player, unit.pos(), &reserved_cells)
                    {
                        self.jobs.insert(unit.id, PlantJob { target, item });
                        reserved_cells.insert(target);
                        let job = self.jobs.get(&unit.id).expect("inserted A2 plant job");
                        if let Some(command) =
                            self.command_for_job(
                                game,
                                player,
                                unit,
                                job,
                                &mut inventory,
                                &mut reserved_moves,
                            )
                        {
                            commands.push(command);
                        }
                        continue;
                    }
                }
            }

            if let Some(target) =
                self.nearest_ripe_plant(game, unit.pos(), &reserved_service)
            {
                reserved_service.insert(target);
                if target == unit.pos() && unit.hp > 0 {
                    commands.push(format!("HARVEST {}", unit.id));
                } else if let Some(command) = Self::move_command(
                    game,
                    player,
                    unit,
                    target,
                    &mut reserved_moves,
                ) {
                    commands.push(command);
                }
                continue;
            }

            if roster < 3 && game.turn <= 110 {
                if let Some(target) =
                    self.nearest_owned_crop(game, unit.pos(), &reserved_service)
                {
                    reserved_service.insert(target);
                    if target != unit.pos() {
                        if let Some(command) = Self::move_command(
                            game,
                            player,
                            unit,
                            target,
                            &mut reserved_moves,
                        ) {
                            commands.push(command);
                        }
                    }
                    continue;
                }
            }

            let allow_owned_chop = game.turn >= LIQUIDATE_START;
            if let Some(target) = self.nearest_chop_target(game, unit.pos(), allow_owned_chop)
            {
                if target == unit.pos() && unit.chop > 0 {
                    commands.push(format!("CHOP {}", unit.id));
                } else if let Some(command) = Self::move_command(
                    game,
                    player,
                    unit,
                    target,
                    &mut reserved_moves,
                ) {
                    commands.push(command);
                }
            }
        }
        commands
    }

    fn command_parts(commands: &[String]) -> Vec<Vec<String>> {
        commands
            .iter()
            .flat_map(|line| line.split(';'))
            .map(|command| {
                command
                    .split_whitespace()
                    .map(|token| token.to_ascii_uppercase())
                    .collect::<Vec<_>>()
            })
            .filter(|parts| !parts.is_empty())
            .collect()
    }

    fn unit_by_id(game: &GameState, unit_id: i32) -> Option<&Unit> {
        game.units.iter().find(|unit| unit.id == unit_id)
    }

    fn opponent_plant_cells(
        before: &GameState,
        opponent: usize,
        commands: &[String],
    ) -> BTreeSet<Cell> {
        Self::command_parts(commands)
            .into_iter()
            .filter(|parts| parts.first().map(String::as_str) == Some("PLANT"))
            .filter_map(|parts| {
                let unit_id = parts.get(1)?.parse::<i32>().ok()?;
                let unit = Self::unit_by_id(before, unit_id)?;
                (unit.player as usize == opponent).then_some(unit.pos())
            })
            .collect()
    }

    /// Reconcile successful commands against the referee's before/after states.
    pub fn observe_transition(
        &mut self,
        before: &GameState,
        after: &GameState,
        player: usize,
        own_commands: &[String],
        opponent_commands: &[String],
    ) {
        self.bind_player(player);
        let roster_before = self.worker_count(before, player);
        let roster_after = self.worker_count(after, player);
        let opponent_plant_cells =
            Self::opponent_plant_cells(before, 1 - player, opponent_commands);
        let parts = Self::command_parts(own_commands);

        for action in &parts {
            let Some(verb) = action.first().map(String::as_str) else {
                continue;
            };
            if verb == "TRAIN" {
                continue;
            }
            let Some(unit_id) = action.get(1).and_then(|token| token.parse::<i32>().ok())
            else {
                continue;
            };
            let Some(before_unit) = Self::unit_by_id(before, unit_id) else {
                continue;
            };
            let Some(after_unit) = Self::unit_by_id(after, unit_id) else {
                continue;
            };
            if before_unit.player as usize != player {
                continue;
            }

            match verb {
                "HARVEST" => {
                    let cell = before_unit.pos();
                    let Some(generation) = self.owned.get(&cell) else {
                        continue;
                    };
                    let Some(item) = Self::plant_index(&generation.plant_type) else {
                        continue;
                    };
                    let gained = (after_unit.carry[item] - before_unit.carry[item]).max(0);
                    if gained > 0 {
                        self.metrics.own_crop_harvested[item] += gained;
                        self.owned_carry.entry(unit_id).or_insert([0; 4])[item] += gained;
                    }
                }
                "PLANT" => {
                    let Some(item_name) = action.get(2) else {
                        continue;
                    };
                    let Some(item) = Self::plant_index(item_name) else {
                        continue;
                    };
                    let spent = (before_unit.carry[item] - after_unit.carry[item]).max(0);
                    if spent > 0 {
                        let provenance = self.owned_carry.entry(unit_id).or_insert([0; 4]);
                        provenance[item] -= provenance[item].min(spent);
                    }
                    let cell = before_unit.pos();
                    let created = Self::plant_at(before, cell).is_none()
                        && Self::plant_at(after, cell)
                            .is_some_and(|plant| plant.plant_type == *item_name);
                    if created && !opponent_plant_cells.contains(&cell) {
                        self.owned.insert(
                            cell,
                            OwnedGeneration {
                                plant_type: item_name.clone(),
                            },
                        );
                        self.metrics.own_generations_created += 1;
                    }
                    if created {
                        self.jobs.remove(&unit_id);
                    }
                }
                "PICK" => {
                    let Some(item_name) = action.get(2) else {
                        continue;
                    };
                    let Some(item) = Self::plant_index(item_name) else {
                        continue;
                    };
                    let gained = (after_unit.carry[item] - before_unit.carry[item]).max(0);
                    if gained > 0 {
                        let non_owned =
                            before.inventories[player][item]
                                - self.metrics.own_crop_banked_available[item];
                        let owned_pick = (gained - non_owned.max(0)).max(0).min(
                            self.metrics.own_crop_banked_available[item],
                        );
                        if owned_pick > 0 {
                            self.metrics.own_crop_banked_available[item] -= owned_pick;
                            self.owned_carry.entry(unit_id).or_insert([0; 4])[item] +=
                                owned_pick;
                        }
                    }
                }
                "DROP" => {
                    let provenance = self.owned_carry.entry(unit_id).or_insert([0; 4]);
                    for item in 0..4 {
                        let dropped =
                            (before_unit.carry[item] - after_unit.carry[item]).max(0);
                        let owned = provenance[item].min(dropped);
                        provenance[item] -= owned;
                        self.metrics.own_crop_banked[item] += owned;
                        self.metrics.own_crop_banked_available[item] += owned;
                    }
                }
                "MINE" => {
                    let gained =
                        (after_unit.carry[IRON] - before_unit.carry[IRON]).max(0);
                    if gained > 0 {
                        if roster_after >= 3 {
                            self.metrics.mined_iron_roster3plus += gained;
                        } else if roster_after >= 2 {
                            self.metrics.mined_iron_roster2 += gained;
                        }
                    }
                }
                _ => {}
            }
        }

        if roster_before == 2 && roster_after == 3 {
            let train = parts
                .iter()
                .find(|action| action.first().map(String::as_str) == Some("TRAIN"));
            if let Some(action) = train {
                let talents: Option<Vec<i32>> = action
                    .iter()
                    .skip(1)
                    .take(4)
                    .map(|token| token.parse::<i32>().ok())
                    .collect();
                if let Some(talents) = talents {
                    let spec = (talents[0], talents[1], talents[2], talents[3]);
                    let cost = training_cost(2, spec);
                    let mut needs_owned = false;
                    for item in BILL_SPECIES {
                        let available_owned =
                            self.metrics.own_crop_banked_available[item].max(0);
                        let non_owned =
                            (before.inventories[player][item] - available_owned).max(0);
                        needs_owned |= cost[item] > non_owned;
                        let owned_used = (cost[item] - non_owned)
                            .max(0)
                            .min(available_owned);
                        self.metrics.own_crop_banked_available[item] -= owned_used;
                    }
                    self.metrics.first_worker3_turn = Some(after.turn);
                    self.metrics.fruit_funded_worker3 =
                        after.turn <= 110 && self.metrics.own_bill_fruit_banked() > 0;
                    self.metrics.worker3_bill = Some(cost);
                    self.metrics.worker3_bill_needs_owned_fruit = needs_owned;
                }
            }
        }

        self.owned.retain(|cell, generation| {
            Self::plant_at(after, *cell)
                .is_some_and(|plant| plant.plant_type == generation.plant_type)
        });
        self.clean_state(after, player);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use troll_farm::game::a2_referee_parity;
    use troll_farm::game::state::{from_ascii_with_talents, Plant};

    fn simple_game() -> GameState {
        let mut game = from_ascii_with_talents(
            &[
                "#######",
                "#0...1#",
                "#..~..#",
                "#.....#",
                "#######",
            ],
            (1, 1, 1, 1),
        );
        game.inventories = [[8, 8, 8, 8, 8, 0], [8, 8, 8, 8, 8, 0]];
        game
    }

    #[test]
    fn opening_vacates_then_trains_worker_two() {
        let mut bot = EconomySkeleton::new();
        let game = simple_game();
        let commands = bot.commands(&game, 0);
        assert!(commands.iter().any(|command| command.starts_with("MOVE 0 ")));
        assert!(commands.iter().any(|command| command == "TRAIN 1 1 1 1"));
        let mut referee = a2_referee_parity::generate_official(9_880_000);
        referee.game = game;
        let before = referee.game.clone();
        a2_referee_parity::step(&mut referee, &commands, &[]);
        bot.observe_transition(&before, &referee.game, 0, &commands, &[]);
        assert_eq!(
            referee
                .game
                .units
                .iter()
                .filter(|unit| unit.player == 0)
                .count(),
            2
        );
    }

    #[test]
    fn own_generation_harvest_and_drop_are_credited() {
        let mut bot = EconomySkeleton::new();
        let mut before = simple_game();
        before.units[0].x = 2;
        before.units[0].y = 1;
        before.units[0].carry[PLUM] = 1;
        let mut after_plant = before.clone();
        after_plant.units[0].carry[PLUM] = 0;
        after_plant.plants.push(Plant {
            plant_type: "PLUM".to_owned(),
            x: 2,
            y: 1,
            size: 1,
            health: 6,
            fruits: 0,
            cooldown: 3,
        });
        bot.observe_transition(
            &before,
            &after_plant,
            0,
            &["PLANT 0 PLUM".to_owned()],
            &[],
        );
        assert_eq!(bot.metrics().own_generations_created, 1);

        let mut before_harvest = after_plant.clone();
        before_harvest.plants[0].fruits = 1;
        let mut after_harvest = before_harvest.clone();
        after_harvest.plants[0].fruits = 0;
        after_harvest.units[0].carry[PLUM] = 1;
        bot.observe_transition(
            &before_harvest,
            &after_harvest,
            0,
            &["HARVEST 0".to_owned()],
            &[],
        );
        assert_eq!(bot.metrics().own_crop_harvested[PLUM], 1);

        let before_drop = after_harvest;
        let mut after_drop = before_drop.clone();
        after_drop.units[0].x = 2;
        after_drop.units[0].y = 1;
        after_drop.units[0].carry[PLUM] = 0;
        after_drop.inventories[0][PLUM] += 1;
        bot.observe_transition(
            &before_drop,
            &after_drop,
            0,
            &["DROP 0".to_owned()],
            &[],
        );
        assert_eq!(bot.metrics().own_crop_banked[PLUM], 1);
    }

    #[test]
    fn ambiguous_joint_plant_is_not_owned() {
        let mut bot = EconomySkeleton::new();
        let mut before = simple_game();
        before.units[0].x = 2;
        before.units[0].y = 1;
        before.units[0].carry[PLUM] = 1;
        before.units[1].x = 2;
        before.units[1].y = 1;
        before.units[1].carry[PLUM] = 1;
        let mut after = before.clone();
        after.units[0].carry[PLUM] = 0;
        after.units[1].carry[PLUM] = 0;
        after.plants.push(Plant {
            plant_type: "PLUM".to_owned(),
            x: 2,
            y: 1,
            size: 1,
            health: 6,
            fruits: 0,
            cooldown: 3,
        });
        bot.observe_transition(
            &before,
            &after,
            0,
            &["PLANT 0 PLUM".to_owned()],
            &["PLANT 1 PLUM".to_owned()],
        );
        assert_eq!(bot.metrics().own_generations_created, 0);
    }

    #[test]
    fn policy_never_creates_iron_directed_moves() {
        let mut bot = EconomySkeleton::new();
        let mut game = simple_game();
        game.iron.insert((3, 3));
        let _ = bot.commands(&game, 0);
        assert_eq!(bot.metrics().iron_directed_moves, 0);
    }
}
