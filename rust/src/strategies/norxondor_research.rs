//! Research-only Norxondor workforce ladder wrapped around two complete continuations.
//!
//! The TRAIN rule is replay-derived: at workforce size `n`, wait until a stage floor is
//! affordable, then buy the componentwise maximum affordable spec clamped by that stage's cap.
//! The wrappers remove every TRAIN command emitted by the continuation before adding this rule,
//! so local comparisons isolate the joint ladder/continuation behavior.

use super::compact_gold::CompactGold;
use super::silver_boss::SilverBoss;
use super::Strategy;
use crate::game::engine::{training_cost, APPLE, IRON, LEMON, PLUM};
use crate::game::state::{Cell, GameState, Unit};
use std::collections::{HashMap, HashSet, VecDeque};

type Spec = (i32, i32, i32, i32);

const BASES: [Spec; 4] = [(2, 2, 1, 1), (2, 3, 1, 2), (2, 3, 0, 3), (2, 4, 0, 3)];
const CAPS: [Spec; 4] = [(3, 3, 2, 2), (4, 5, 2, 2), (3, 3, 1, 3), (3, 4, 1, 3)];

fn stage_base(n: i32) -> Option<Spec> {
    if (1..=4).contains(&n) {
        Some(BASES[(n - 1) as usize])
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

fn affordable(inventory: &[i32; 6], cost: &[i32; 6], have_iron: bool) -> bool {
    inventory[PLUM] >= cost[PLUM]
        && inventory[LEMON] >= cost[LEMON]
        && inventory[APPLE] >= cost[APPLE]
        && (!have_iron || inventory[IRON] >= cost[IRON])
}

pub fn proposed_spec(n: i32, inventory: &[i32; 6], have_iron: bool) -> Option<Spec> {
    if !(1..=4).contains(&n) {
        return None;
    }
    let index = (n - 1) as usize;
    let base = BASES[index];
    if !affordable(inventory, &training_cost(n, base), have_iron) {
        return None;
    }
    let cap = CAPS[index];
    Some((
        integer_sqrt(inventory[PLUM] - n).min(cap.0),
        integer_sqrt(inventory[LEMON] - n).min(cap.1),
        integer_sqrt(inventory[APPLE] - n).min(cap.2),
        if have_iron {
            integer_sqrt(inventory[IRON] - n).min(cap.3)
        } else {
            cap.3
        },
    ))
}

fn override_training(mut commands: Vec<String>, game: &GameState, player: usize) -> Vec<String> {
    commands.retain(|command| !command.starts_with("TRAIN "));
    let n = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .count() as i32;
    if let Some(spec) = proposed_spec(n, &game.inventories[player], !game.iron.is_empty()) {
        commands.push(format!("TRAIN {} {} {} {}", spec.0, spec.1, spec.2, spec.3));
    }
    commands
}

fn manhattan(left: Cell, right: Cell) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn bfs(game: &GameState, source: Cell) -> HashMap<Cell, i32> {
    let mut distance = HashMap::from([(source, 0)]);
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

fn bank_command(unit: &Unit, shack: Cell) -> String {
    if manhattan(unit.pos(), shack) == 1 {
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

fn funding_command(game: &GameState, player: usize, unit: &Unit, n: i32) -> Option<String> {
    let base = stage_base(n)?;
    let cost = training_cost(n, base);
    let inventory = &game.inventories[player];
    let fruit_need = (PLUM..=APPLE)
        .map(|index| (cost[index] - inventory[index], index))
        .filter(|(deficit, _)| *deficit > 0)
        .max_by_key(|(deficit, index)| (*deficit, -(*index as i32)));
    let iron_need = !game.iron.is_empty() && inventory[IRON] < cost[IRON];

    if unit.total() > 0
        && (unit.free() == 0
            || fruit_need.is_some_and(|(_, index)| unit.carry[index] > 0)
            || (iron_need && unit.carry[IRON] > 0))
    {
        return Some(bank_command(unit, game.shacks[player]));
    }
    let distance = bfs(game, unit.pos());
    if let Some((_, index)) = fruit_need {
        let kind = ["PLUM", "LEMON", "APPLE"][index];
        let target = game
            .plants
            .iter()
            .filter(|plant| plant.plant_type == kind && distance.contains_key(&plant.pos()))
            .min_by_key(|plant| {
                (
                    i32::from(plant.fruits <= 0),
                    distance[&plant.pos()],
                    plant.cooldown,
                    plant.pos(),
                )
            })
            .map(|plant| plant.pos());
        if let Some(cell) = target {
            return Some(if cell == unit.pos() {
                format!("HARVEST {}", unit.id)
            } else {
                format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
            });
        }
    }
    if iron_need && unit.chop > 0 {
        if game
            .iron
            .iter()
            .any(|iron| manhattan(unit.pos(), *iron) == 1)
        {
            return Some(format!("MINE {}", unit.id));
        }
        if let Some(cell) = game
            .iron
            .iter()
            .flat_map(|iron| {
                [
                    (iron.0, iron.1 + 1),
                    (iron.0 + 1, iron.1),
                    (iron.0, iron.1 - 1),
                    (iron.0 - 1, iron.1),
                ]
            })
            .filter(|cell| distance.contains_key(cell))
            .min_by_key(|cell| (distance[cell], *cell))
        {
            return Some(format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
        }
    }
    (unit.total() > 0).then(|| bank_command(unit, game.shacks[player]))
}

fn ranked_funding_command(
    game: &GameState,
    player: usize,
    unit: &Unit,
    n: i32,
    rank: usize,
    reserved: &mut HashSet<Cell>,
) -> Option<String> {
    let base = stage_base(n)?;
    let cost = training_cost(n, base);
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
    if unit.total() > 0 && (unit.free() == 0 || unit.carry[resource] > 0) {
        return Some(bank_command(unit, game.shacks[player]));
    }

    let distance = bfs(game, unit.pos());
    if resource <= APPLE {
        let kind = ["PLUM", "LEMON", "APPLE"][resource];
        let target = game
            .plants
            .iter()
            .filter(|plant| plant.plant_type == kind && distance.contains_key(&plant.pos()))
            .filter(|plant| plant.pos() == unit.pos() || !reserved.contains(&plant.pos()))
            .min_by_key(|plant| {
                (
                    i32::from(plant.fruits <= 0),
                    distance[&plant.pos()],
                    plant.cooldown,
                    plant.pos(),
                )
            })
            .map(|plant| plant.pos());
        if let Some(cell) = target {
            reserved.insert(cell);
            return Some(if cell == unit.pos() {
                format!("HARVEST {}", unit.id)
            } else {
                format!("MOVE {} {} {}", unit.id, cell.0, cell.1)
            });
        }
    } else if resource == IRON && unit.chop > 0 {
        if game
            .iron
            .iter()
            .any(|iron| manhattan(unit.pos(), *iron) == 1)
        {
            reserved.insert(unit.pos());
            return Some(format!("MINE {}", unit.id));
        }
        if let Some(cell) = game
            .iron
            .iter()
            .flat_map(|iron| {
                [
                    (iron.0, iron.1 + 1),
                    (iron.0 + 1, iron.1),
                    (iron.0, iron.1 - 1),
                    (iron.0 - 1, iron.1),
                ]
            })
            .filter(|cell| distance.contains_key(cell) && !reserved.contains(cell))
            .min_by_key(|cell| (distance[cell], *cell))
        {
            reserved.insert(cell);
            return Some(format!("MOVE {} {} {}", unit.id, cell.0, cell.1));
        }
    }
    (unit.total() > 0).then(|| bank_command(unit, game.shacks[player]))
}

pub struct NorxondorCompact {
    continuation: CompactGold,
}

impl NorxondorCompact {
    pub fn new() -> Self {
        Self {
            continuation: CompactGold::new(),
        }
    }
}

impl Strategy for NorxondorCompact {
    fn name(&self) -> &str {
        "norx_compact"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        override_training(self.continuation.decide(game, player), game, player)
    }
}

pub struct NorxondorSilver {
    continuation: SilverBoss,
}

impl NorxondorSilver {
    pub fn new() -> Self {
        Self {
            continuation: SilverBoss::new(),
        }
    }
}

impl Strategy for NorxondorSilver {
    fn name(&self) -> &str {
        "norx_silver"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        override_training(self.continuation.decide(game, player), game, player)
    }
}

/// Silver continuation with one explicit ladder-funding role.
pub struct NorxondorFundedSilver {
    continuation: SilverBoss,
}

impl NorxondorFundedSilver {
    pub fn new() -> Self {
        Self {
            continuation: SilverBoss::new(),
        }
    }
}

impl Strategy for NorxondorFundedSilver {
    fn name(&self) -> &str {
        "norx_funded_silver"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let mut commands = self.continuation.decide(game, player);
        commands.retain(|command| !command.starts_with("TRAIN "));
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        let n = units.len() as i32;
        let proposed = proposed_spec(n, &game.inventories[player], !game.iron.is_empty());
        if proposed.is_none() {
            if let Some(unit) = units.iter().copied().find(|unit| unit.hp > 0) {
                if let Some(command) = funding_command(game, player, unit, n) {
                    replace_unit_command(&mut commands, unit.id, command);
                }
            }
        } else if let Some(unit) = units
            .iter()
            .copied()
            .find(|unit| unit.pos() == game.shacks[player])
        {
            if let Some(cell) = [
                (unit.x, unit.y + 1),
                (unit.x + 1, unit.y),
                (unit.x, unit.y - 1),
                (unit.x - 1, unit.y),
            ]
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
}

fn coordinated_commands_with_funders(
    mut commands: Vec<String>,
    game: &GameState,
    player: usize,
    keep_two_funders: bool,
    stop_at_three: bool,
    funder_count_override: Option<usize>,
    newest_first: bool,
) -> Vec<String> {
    commands.retain(|command| !command.starts_with("TRAIN "));
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect();
    units.sort_by_key(|unit| unit.id);
    let n = units.len() as i32;
    if stop_at_three && n >= 3 {
        return commands;
    }
    let proposed = proposed_spec(n, &game.inventories[player], !game.iron.is_empty());
    if proposed.is_none() {
        let funder_count = funder_count_override.unwrap_or_else(|| {
            if n == 2 || (keep_two_funders && n > 2) {
                2
            } else {
                1
            }
        });
        let mut reserved = HashSet::new();
        let mut funders: Vec<_> = units.iter().copied().filter(|unit| unit.hp > 0).collect();
        if newest_first {
            funders.reverse();
        }
        for (rank, unit) in funders.into_iter().take(funder_count).enumerate() {
            if let Some(command) =
                ranked_funding_command(game, player, unit, n, rank, &mut reserved)
            {
                replace_unit_command(&mut commands, unit.id, command);
            }
        }
    } else if let Some(unit) = units
        .iter()
        .copied()
        .find(|unit| unit.pos() == game.shacks[player])
    {
        if let Some(cell) = [
            (unit.x, unit.y + 1),
            (unit.x + 1, unit.y),
            (unit.x, unit.y - 1),
            (unit.x - 1, unit.y),
        ]
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

fn coordinated_commands(
    commands: Vec<String>,
    game: &GameState,
    player: usize,
    keep_two_funders: bool,
    stop_at_three: bool,
) -> Vec<String> {
    coordinated_commands_with_funders(
        commands,
        game,
        player,
        keep_two_funders,
        stop_at_three,
        None,
        false,
    )
}

fn coordinated_silver_commands(
    continuation: &SilverBoss,
    game: &GameState,
    player: usize,
    keep_two_funders: bool,
    stop_at_three: bool,
) -> Vec<String> {
    coordinated_commands(
        continuation.decide(game, player),
        game,
        player,
        keep_two_funders,
        stop_at_three,
    )
}

/// Apply the recovered two-funder/three-worker ladder to an arbitrary complete continuation.
/// Once three workers exist, the continuation keeps control and only further TRAINs are removed.
pub fn resident_three_worker_commands(
    commands: Vec<String>,
    game: &GameState,
    player: usize,
) -> Vec<String> {
    coordinated_commands(commands, game, player, false, true)
}

/// Research-only funding schedules for separating opening disruption from later role quality.
#[derive(Clone, Copy, Debug)]
pub enum ResidentFundingProfile {
    TwoOldest,
    OneOldest,
    OneNewest,
    DelayedTwo { start_turn: i32 },
    OldestThenTwo { switch_turn: i32 },
    NewestThenTwo { switch_turn: i32 },
}

/// Apply a specified funding coalition until worker three, then return complete control to the
/// supplied continuation. Every profile suppresses unrelated continuation TRAIN commands.
pub fn resident_three_worker_commands_with_profile(
    mut commands: Vec<String>,
    game: &GameState,
    player: usize,
    profile: ResidentFundingProfile,
) -> Vec<String> {
    commands.retain(|command| !command.starts_with("TRAIN "));
    let workers = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .count();
    if workers >= 3 {
        return commands;
    }
    let (funder_count, newest_first) = match profile {
        ResidentFundingProfile::TwoOldest => (2, false),
        ResidentFundingProfile::OneOldest => (1, false),
        ResidentFundingProfile::OneNewest => (1, true),
        ResidentFundingProfile::DelayedTwo { start_turn } => {
            if game.turn < start_turn {
                return commands;
            }
            (2, false)
        }
        ResidentFundingProfile::OldestThenTwo { switch_turn } => {
            (usize::from(game.turn >= switch_turn) + 1, false)
        }
        ResidentFundingProfile::NewestThenTwo { switch_turn } => {
            if game.turn >= switch_turn {
                (2, false)
            } else {
                (1, true)
            }
        }
    };
    coordinated_commands_with_funders(
        commands,
        game,
        player,
        false,
        true,
        Some(funder_count),
        newest_first,
    )
}

/// Silver continuation with two coordinated ladder-funding roles once two workers exist.
pub struct NorxondorCooperativeSilver {
    continuation: SilverBoss,
}

impl NorxondorCooperativeSilver {
    pub fn new() -> Self {
        Self {
            continuation: SilverBoss::new(),
        }
    }
}

impl Strategy for NorxondorCooperativeSilver {
    fn name(&self) -> &str {
        "norx_cooperative_silver"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        coordinated_silver_commands(&self.continuation, game, player, true, false)
    }
}

/// Two funders unlock worker three; one then returns to the continuation's denial role.
pub struct NorxondorSoftCooperativeSilver {
    continuation: SilverBoss,
}

impl NorxondorSoftCooperativeSilver {
    pub fn new() -> Self {
        Self {
            continuation: SilverBoss::new(),
        }
    }
}

impl Strategy for NorxondorSoftCooperativeSilver {
    fn name(&self) -> &str {
        "norx_soft_cooperative_silver"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        coordinated_silver_commands(&self.continuation, game, player, false, false)
    }
}

/// Cooperative funding ends once the third worker is trained.
pub struct NorxondorThreeWorkerSilver {
    continuation: SilverBoss,
}

impl NorxondorThreeWorkerSilver {
    pub fn new() -> Self {
        Self {
            continuation: SilverBoss::new(),
        }
    }
}

impl Strategy for NorxondorThreeWorkerSilver {
    fn name(&self) -> &str {
        "norx_three_worker_silver"
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        coordinated_silver_commands(&self.continuation, game, player, false, true)
    }
}
