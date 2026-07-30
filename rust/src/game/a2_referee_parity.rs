//! Isolated referee-parity substrate for Architecture-2.
//!
//! Historical experiments keep using `engine` and `official_mapgen` unchanged. This
//! module preserves the post-map SHA1PRNG state and mirrors the referee's x-major/y-minor
//! movement candidate ordering.

use super::engine::{
    self, apply_drop, apply_harvest, apply_mine, apply_plant, apply_train, bfs_distances,
    recompute_scores, tick_plants,
};
use super::state::{Cell, GameState};
use std::collections::{BTreeMap, HashMap, HashSet};

use super::a2_continued_mapgen::{generate_official_with_rng, Sha1Prng};

pub const SUPPORTED_NONCRITICAL_REASONS: &[&str] = &[
    "unit_not_found",
    "unit_not_owned",
    "unit_already_used",
    "out_of_board",
    "invalid_skill",
    "cant_afford_train",
    "no_plant",
    "no_fruit",
    "no_capacity",
    "no_harvest",
    "invalid_plant",
    "no_grass",
    "existing_plant",
    "no_seeds",
    "no_chop",
    "out_of_stock",
    "no_shack",
    "nothing_to_drop",
    "no_iron",
    "move_blocked",
    "opponent_plant_blocking",
    "pick_stock_lost",
    "train_affordability_lost",
    "train_shack_blocked",
];

pub const KNOWN_CRITICAL_REASONS: &[&str] = &["unknown_command", "train_failed"];

pub fn is_supported_noncritical_reason(reason: &str) -> bool {
    SUPPORTED_NONCRITICAL_REASONS.contains(&reason)
}

pub fn is_known_critical_reason(reason: &str) -> bool {
    KNOWN_CRITICAL_REASONS.contains(&reason)
}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct MovementRngStats {
    pub draws: u64,
    pub tied_draws: u64,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct MoveSelection {
    pub cell: Cell,
    pub candidate_count: usize,
    pub drew_rng: bool,
}

#[derive(Clone, Debug)]
pub struct RefereeGame {
    pub game: GameState,
    random: Sha1Prng,
    pub movement_rng: MovementRngStats,
    pub legality: LegalityReport,
}

pub fn generate_official(seed: i64) -> RefereeGame {
    let (game, random) = generate_official_with_rng(seed);
    RefereeGame {
        game,
        random,
        movement_rng: MovementRngStats::default(),
        legality: LegalityReport::default(),
    }
}

fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

/// Source-shaped `Board.getNextCell`.
///
/// The direct-target fast path consumes no RNG. Every other selection calls
/// `nextInt(closest.size())`, including `nextInt(1)`.
pub fn select_next_cell(
    referee: &mut RefereeGame,
    current: Cell,
    target: Cell,
    speed: i32,
) -> MoveSelection {
    let game = &referee.game;
    let source_dist = bfs_distances(&game.walkable, &[current]);
    let mut target_dist = bfs_distances(&game.walkable, &[target]);

    if source_dist.get(&target).is_some_and(|distance| *distance <= speed) {
        return MoveSelection {
            cell: target,
            candidate_count: 1,
            drew_rng: false,
        };
    }

    if !source_dist.contains_key(&target) {
        let best = source_dist
            .keys()
            .map(|cell| manhattan(target, *cell))
            .min()
            .expect("current cell is always a BFS source");
        let mut closest_to_target = Vec::new();
        for x in 0..game.width {
            for y in 0..game.height {
                let cell = (x, y);
                if source_dist.contains_key(&cell) && manhattan(target, cell) == best {
                    closest_to_target.push(cell);
                }
            }
        }
        target_dist = bfs_distances(&game.walkable, &closest_to_target);
    }

    let mut closest = Vec::new();
    let mut best = game.width * game.height;
    for x in 0..game.width {
        for y in 0..game.height {
            let cell = (x, y);
            let Some(&source) = source_dist.get(&cell) else {
                continue;
            };
            if source > speed {
                continue;
            }
            let Some(&remaining) = target_dist.get(&cell) else {
                continue;
            };
            if remaining < best {
                best = remaining;
                closest.clear();
            }
            if remaining == best {
                closest.push(cell);
            }
        }
    }

    assert!(!closest.is_empty(), "referee movement candidate set is non-empty");
    let index = referee.random.next_int(closest.len() as i32) as usize;
    referee.movement_rng.draws += 1;
    if closest.len() > 1 {
        referee.movement_rng.tied_draws += 1;
    }
    MoveSelection {
        cell: closest[index],
        candidate_count: closest.len(),
        drew_rng: true,
    }
}

/// Apply already-resolved movement targets using `MoveTask.apply` collision semantics.
///
/// Movement targets must be resolved, in command parse order, with [`select_next_cell`]
/// before this function is called.
pub fn apply_resolved_moves(game: &mut GameState, intents: &HashMap<i32, Cell>) -> Vec<i32> {
    let mut blocked = Vec::new();
    for player in 0..2i32 {
        let player_unit_ids: Vec<i32> = game
            .units
            .iter()
            .filter(|unit| unit.player == player)
            .map(|unit| unit.id)
            .collect();
        let initial_positions: HashMap<i32, Cell> = game
            .units
            .iter()
            .filter(|unit| unit.player == player)
            .map(|unit| (unit.id, unit.pos()))
            .collect();
        let target: HashMap<i32, Cell> = player_unit_ids
            .iter()
            .map(|unit_id| {
                (
                    *unit_id,
                    intents
                        .get(unit_id)
                        .copied()
                        .unwrap_or(initial_positions[unit_id]),
                )
            })
            .collect();

        let mut occupied: HashSet<Cell> = player_unit_ids
            .iter()
            .map(|unit_id| initial_positions[unit_id])
            .collect();
        let mut movers: Vec<i32> = player_unit_ids
            .iter()
            .filter(|unit_id| target[unit_id] != initial_positions[unit_id])
            .copied()
            .collect();
        movers.sort_by(|left, right| right.cmp(left));

        let mut progress = true;
        let mut resolve_blocking = false;
        while progress {
            progress = false;
            let mut frequency: HashMap<Cell, i32> = HashMap::new();
            for unit_id in &movers {
                *frequency.entry(target[unit_id]).or_insert(0) += 1;
            }

            let mut moved = Vec::new();
            for unit_id in &movers {
                let destination = target[unit_id];
                let current = game
                    .units
                    .iter()
                    .find(|unit| unit.id == *unit_id)
                    .expect("known mover")
                    .pos();
                if (resolve_blocking || frequency[&destination] == 1)
                    && !occupied.contains(&destination)
                {
                    occupied.remove(&current);
                    occupied.insert(destination);
                    let unit = game
                        .units
                        .iter_mut()
                        .find(|unit| unit.id == *unit_id)
                        .expect("known mover");
                    unit.x = destination.0;
                    unit.y = destination.1;
                    moved.push(*unit_id);
                    progress = true;
                    resolve_blocking = false;
                }
            }
            movers.retain(|unit_id| !moved.contains(unit_id));
            if progress {
                continue;
            }

            let mover_at: HashMap<Cell, i32> = movers
                .iter()
                .map(|unit_id| {
                    let position = game
                        .units
                        .iter()
                        .find(|unit| unit.id == *unit_id)
                        .expect("known mover")
                        .pos();
                    (position, *unit_id)
                })
                .collect();
            let mut swap_resolved = false;
            'outer: for start in &movers {
                let mut path = vec![*start];
                loop {
                    let destination = target[path.last().expect("non-empty path")];
                    let Some(next) = mover_at.get(&destination).copied() else {
                        break;
                    };
                    if next == path[0] {
                        for unit_id in &path {
                            let destination = target[unit_id];
                            let unit = game
                                .units
                                .iter_mut()
                                .find(|unit| unit.id == *unit_id)
                                .expect("known mover");
                            unit.x = destination.0;
                            unit.y = destination.1;
                        }
                        movers.retain(|unit_id| !path.contains(unit_id));
                        progress = true;
                        swap_resolved = true;
                        break 'outer;
                    }
                    if path.contains(&next) {
                        break;
                    }
                    path.push(next);
                }
            }
            if !swap_resolved && !resolve_blocking {
                resolve_blocking = true;
                progress = true;
            }
        }
        blocked.extend(movers);
    }
    blocked
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct LegalityIssue {
    pub turn: i32,
    pub player: usize,
    pub phase: &'static str,
    pub reason: &'static str,
    pub critical: bool,
    pub command: String,
}

#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct LegalityReport {
    pub commands_checked: u64,
    pub issues: Vec<LegalityIssue>,
}

impl LegalityReport {
    pub fn issue_count(&self) -> usize {
        self.issues.len()
    }

    pub fn issue_count_for_player(&self, player: usize) -> usize {
        self.issues
            .iter()
            .filter(|issue| issue.player == player)
            .count()
    }

    pub fn critical_issue_count(&self) -> usize {
        self.issues.iter().filter(|issue| issue.critical).count()
    }

    pub fn critical_issue_count_for_player(&self, player: usize) -> usize {
        self.issues
            .iter()
            .filter(|issue| issue.player == player && issue.critical)
            .count()
    }

    pub fn unclassified_issue_count(&self) -> usize {
        self.issues
            .iter()
            .filter(|issue| {
                !is_supported_noncritical_reason(issue.reason)
                    && !is_known_critical_reason(issue.reason)
            })
            .count()
    }

    pub fn reason_counts(&self) -> BTreeMap<&'static str, usize> {
        let mut counts = BTreeMap::new();
        for issue in &self.issues {
            *counts.entry(issue.reason).or_insert(0) += 1;
        }
        counts
    }

    pub fn reason_counts_for_player(
        &self,
        player: usize,
    ) -> BTreeMap<&'static str, usize> {
        let mut counts = BTreeMap::new();
        for issue in self.issues.iter().filter(|issue| issue.player == player) {
            *counts.entry(issue.reason).or_insert(0) += 1;
        }
        counts
    }

    pub fn phase_reason_counts(
        &self,
    ) -> BTreeMap<(&'static str, &'static str), usize> {
        let mut counts = BTreeMap::new();
        for issue in &self.issues {
            *counts.entry((issue.phase, issue.reason)).or_insert(0) += 1;
        }
        counts
    }

    pub fn phase_reason_counts_for_player(
        &self,
        player: usize,
    ) -> BTreeMap<(&'static str, &'static str), usize> {
        let mut counts = BTreeMap::new();
        for issue in self.issues.iter().filter(|issue| issue.player == player) {
            *counts.entry((issue.phase, issue.reason)).or_insert(0) += 1;
        }
        counts
    }
}

#[derive(Default)]
struct ParsedTurn {
    moves: HashMap<i32, Cell>,
    move_commands: HashMap<i32, String>,
    harvest: Vec<i32>,
    plant: Vec<(i32, String, String)>,
    chop: Vec<i32>,
    pick: Vec<(i32, String, String)>,
    train: Vec<((i32, i32, i32, i32), String)>,
    drop: Vec<i32>,
    mine: Vec<i32>,
}

fn near_shack(game: &GameState, player: usize, cell: Cell) -> bool {
    manhattan(game.shacks[player], cell) <= 1
}

fn plant_index(game: &GameState, cell: Cell) -> Option<usize> {
    game.plants.iter().position(|plant| plant.pos() == cell)
}

fn parse_decimal(token: &str, signed: bool) -> Option<i32> {
    let digits = if signed {
        token.strip_prefix('-').unwrap_or(token)
    } else {
        token
    };
    if digits.is_empty() || !digits.bytes().all(|byte| byte.is_ascii_digit()) {
        return None;
    }
    token.parse().ok()
}

fn parse_plant_item(token: &str) -> Result<usize, (&'static str, bool)> {
    match token.to_ascii_uppercase().as_str() {
        "PLUM" => Ok(engine::PLUM),
        "LEMON" => Ok(engine::LEMON),
        "APPLE" => Ok(engine::APPLE),
        "BANANA" => Ok(engine::BANANA),
        "IRON" | "WOOD" => Err(("invalid_plant", false)),
        _ if token.bytes().all(|byte| byte.is_ascii_digit() || byte == b'_') => {
            match token.parse::<i32>() {
                Ok(0..=3) => Ok(token.parse::<usize>().expect("small plant index")),
                Ok(_) => Err(("invalid_plant", false)),
                Err(_) => Err(("unknown_command", true)),
            }
        }
        _ => Err(("unknown_command", true)),
    }
}

fn record_issue(
    referee: &mut RefereeGame,
    player: usize,
    phase: &'static str,
    reason: &'static str,
    _critical_hint: bool,
    command: &str,
) {
    let critical = !is_supported_noncritical_reason(reason);
    referee.legality.issues.push(LegalityIssue {
        turn: referee.game.turn,
        player,
        phase,
        reason,
        critical,
        command: command.to_owned(),
    });
}

fn parse_player(referee: &mut RefereeGame, player: usize, raw_commands: &[String]) -> ParsedTurn {
    let mut parsed = ParsedTurn::default();
    let mut used = HashSet::new();
    let commands: Vec<&str> = raw_commands
        .iter()
        .flat_map(|line| line.split(';'))
        .collect();

    for raw in commands {
        let command = raw.trim();
        if command.is_empty() {
            continue;
        }
        referee.legality.commands_checked += 1;
        let upper = command.to_ascii_uppercase();
        if upper == "WAIT" || upper.starts_with("MSG ") {
            continue;
        }
        let parts: Vec<&str> = command.split_whitespace().collect();
        let verb = parts[0].to_ascii_uppercase();

        if verb == "TRAIN" {
            if parts.len() != 5 {
                record_issue(
                    referee,
                    player,
                    "parse",
                    "unknown_command",
                    true,
                    command,
                );
                continue;
            }
            let talents: Option<Vec<i32>> = parts[1..]
                .iter()
                .map(|token| parse_decimal(token, false))
                .collect();
            let Some(talents) = talents else {
                record_issue(
                    referee,
                    player,
                    "parse",
                    "unknown_command",
                    true,
                    command,
                );
                continue;
            };
            let talents = (talents[0], talents[1], talents[2], talents[3]);
            let invalid_skill = talents.0 < 1
                || talents.0 > referee.game.width * referee.game.height
                || talents.1 < 0
                || talents.1 > 1_000
                || talents.2 < 0
                || talents.2 > 3
                || talents.3 < 0
                || talents.3 > 20;
            if invalid_skill {
                record_issue(
                    referee,
                    player,
                    "parse",
                    "invalid_skill",
                    false,
                    command,
                );
                continue;
            }
            let roster = referee
                .game
                .units
                .iter()
                .filter(|unit| unit.player as usize == player)
                .count() as i32;
            let cost = engine::training_cost(roster, talents);
            if cost
                .iter()
                .enumerate()
                .any(|(index, amount)| referee.game.inventories[player][index] < *amount)
            {
                record_issue(
                    referee,
                    player,
                    "parse",
                    "cant_afford_train",
                    false,
                    command,
                );
                continue;
            }
            parsed.train.push((talents, command.to_owned()));
            continue;
        }

        let expected_len = match verb.as_str() {
            "MOVE" => 4,
            "PLANT" | "PICK" => 3,
            "HARVEST" | "CHOP" | "DROP" | "MINE" => 2,
            _ => {
                record_issue(
                    referee,
                    player,
                    "parse",
                    "unknown_command",
                    true,
                    command,
                );
                continue;
            }
        };
        if parts.len() != expected_len {
            record_issue(
                referee,
                player,
                "parse",
                "unknown_command",
                true,
                command,
            );
            continue;
        }
        let Some(unit_id) = parse_decimal(parts[1], false) else {
            record_issue(
                referee,
                player,
                "parse",
                "unknown_command",
                true,
                command,
            );
            continue;
        };
        let Some(unit) = referee
            .game
            .units
            .iter()
            .find(|unit| unit.id == unit_id)
            .cloned()
        else {
            record_issue(
                referee,
                player,
                "parse",
                "unit_not_found",
                false,
                command,
            );
            continue;
        };
        if unit.player as usize != player {
            record_issue(
                referee,
                player,
                "parse",
                "unit_not_owned",
                false,
                command,
            );
            continue;
        }
        if !used.insert(unit_id) {
            record_issue(
                referee,
                player,
                "parse",
                "unit_already_used",
                false,
                command,
            );
            continue;
        }

        let first_error = match verb.as_str() {
            "MOVE" => {
                let x = parse_decimal(parts[2], true);
                let y = parse_decimal(parts[3], true);
                match (x, y) {
                    (Some(x), Some(y)) => {
                        if x < 0
                            || x >= referee.game.width
                            || y < 0
                            || y >= referee.game.height
                        {
                            Some(("out_of_board", false))
                        } else {
                            let selected =
                                select_next_cell(referee, unit.pos(), (x, y), unit.ms);
                            parsed.moves.insert(unit_id, selected.cell);
                            parsed
                                .move_commands
                                .insert(unit_id, command.to_owned());
                            None
                        }
                    }
                    _ => Some(("unknown_command", true)),
                }
            }
            "HARVEST" => match plant_index(&referee.game, unit.pos()) {
                None => Some(("no_plant", false)),
                Some(index) if referee.game.plants[index].fruits == 0 => {
                    Some(("no_fruit", false))
                }
                Some(_) if unit.free() == 0 => Some(("no_capacity", false)),
                Some(_) if unit.hp == 0 => Some(("no_harvest", false)),
                Some(_) => {
                    parsed.harvest.push(unit_id);
                    None
                }
            },
            "PLANT" => match parse_plant_item(parts[2]) {
                Err(error) => Some(error),
                Ok(_item) if !referee.game.walkable.contains(&unit.pos()) => {
                    Some(("no_grass", false))
                }
                Ok(_) if plant_index(&referee.game, unit.pos()).is_some() => {
                    Some(("existing_plant", false))
                }
                Ok(item) if unit.carry[item] == 0 => Some(("no_seeds", false)),
                Ok(_) => {
                    parsed.plant.push((
                        unit_id,
                        parts[2].to_ascii_uppercase(),
                        command.to_owned(),
                    ));
                    None
                }
            },
            "CHOP" => {
                if plant_index(&referee.game, unit.pos()).is_none() {
                    Some(("no_plant", false))
                } else if unit.chop == 0 {
                    Some(("no_chop", false))
                } else {
                    parsed.chop.push(unit_id);
                    None
                }
            }
            "PICK" => match parse_plant_item(parts[2]) {
                _ if unit.free() == 0 => Some(("no_capacity", false)),
                Err(error) => Some(error),
                Ok(item) if referee.game.inventories[player][item] == 0 => {
                    Some(("out_of_stock", false))
                }
                Ok(_) if !near_shack(&referee.game, player, unit.pos()) => {
                    Some(("no_shack", false))
                }
                Ok(_) => {
                    parsed.pick.push((
                        unit_id,
                        parts[2].to_ascii_uppercase(),
                        command.to_owned(),
                    ));
                    None
                }
            },
            "DROP" => {
                if unit.total() == 0 {
                    Some(("nothing_to_drop", false))
                } else if !near_shack(&referee.game, player, unit.pos()) {
                    Some(("no_shack", false))
                } else {
                    parsed.drop.push(unit_id);
                    None
                }
            }
            "MINE" => {
                let near_iron = referee
                    .game
                    .iron
                    .iter()
                    .any(|cell| manhattan(*cell, unit.pos()) == 1);
                if !near_iron {
                    Some(("no_iron", false))
                } else if unit.free() == 0 {
                    Some(("no_capacity", false))
                } else if unit.chop == 0 {
                    Some(("no_chop", false))
                } else {
                    parsed.mine.push(unit_id);
                    None
                }
            }
            _ => unreachable!("known unit command"),
        };
        if let Some((reason, critical)) = first_error {
            record_issue(
                referee,
                player,
                "parse",
                reason,
                critical,
                command,
            );
        }
    }
    parsed
}

fn apply_chop_on_existing_cells(
    game: &mut GameState,
    unit_ids: &[i32],
    allowed_cells: &HashSet<Cell>,
) {
    let mut cells: HashMap<Cell, Vec<i32>> = HashMap::new();
    for unit_id in unit_ids {
        if let Some(unit) = game.units.iter().find(|unit| unit.id == *unit_id) {
            if unit.chop > 0
                && allowed_cells.contains(&unit.pos())
                && plant_index(game, unit.pos()).is_some()
            {
                cells.entry(unit.pos()).or_default().push(*unit_id);
            }
        }
    }

    let mut dead = Vec::new();
    for (cell, choppers) in cells {
        let Some(index) = plant_index(game, cell) else {
            continue;
        };
        for unit_id in &choppers {
            let power = game
                .units
                .iter()
                .find(|unit| unit.id == *unit_id)
                .map(|unit| unit.chop)
                .unwrap_or(0);
            game.plants[index].health = (game.plants[index].health - power).max(0);
        }
        if game.plants[index].health <= 0 {
            let size = game.plants[index].size;
            let mut remaining = size;
            let mut round = 0;
            while round < size && remaining > 0 {
                for unit_id in &choppers {
                    let free = game
                        .units
                        .iter()
                        .find(|unit| unit.id == *unit_id)
                        .map(|unit| unit.free())
                        .unwrap_or(0);
                    if free > 0 {
                        if let Some(unit) =
                            game.units.iter_mut().find(|unit| unit.id == *unit_id)
                        {
                            unit.carry[engine::WOOD] += 1;
                            remaining -= 1;
                        }
                    }
                }
                round += 1;
            }
            dead.push(index);
        }
    }
    dead.sort_unstable();
    dead.dedup();
    for index in dead.into_iter().rev() {
        game.plants.remove(index);
    }
}

/// Parse and execute one Legend turn with referee movement RNG and legality accounting.
pub fn step(referee: &mut RefereeGame, commands0: &[String], commands1: &[String]) {
    let parsed0 = parse_player(referee, 0, commands0);
    let parsed1 = parse_player(referee, 1, commands1);

    let mut moves = parsed0.moves.clone();
    moves.extend(parsed1.moves.iter());
    let blocked = apply_resolved_moves(&mut referee.game, &moves);
    for unit_id in blocked {
        let (player, command) = if let Some(command) = parsed0.move_commands.get(&unit_id) {
            (0, command)
        } else {
            (1, parsed1.move_commands.get(&unit_id).expect("blocked move command"))
        };
        record_issue(
            referee,
            player,
            "apply",
            "move_blocked",
            false,
            command,
        );
    }

    let mut harvest = parsed0.harvest;
    harvest.extend(parsed1.harvest);
    apply_harvest(&mut referee.game, &harvest);

    let choppable_cells: HashSet<Cell> =
        referee.game.plants.iter().map(|plant| plant.pos()).collect();
    let all_plants: Vec<(i32, String)> = parsed0
        .plant
        .iter()
        .chain(parsed1.plant.iter())
        .map(|(unit_id, plant_type, _)| (*unit_id, plant_type.clone()))
        .collect();
    let mut plant_types_by_cell: HashMap<Cell, HashSet<&str>> = HashMap::new();
    for (unit_id, plant_type, _) in parsed0.plant.iter().chain(parsed1.plant.iter()) {
        let cell = referee
            .game
            .units
            .iter()
            .find(|unit| unit.id == *unit_id)
            .expect("parsed planter")
            .pos();
        plant_types_by_cell
            .entry(cell)
            .or_default()
            .insert(plant_type.as_str());
    }
    for (unit_id, _, command) in parsed0.plant.iter().chain(parsed1.plant.iter()) {
        let unit = referee
            .game
            .units
            .iter()
            .find(|unit| unit.id == *unit_id)
            .expect("parsed planter");
        if plant_types_by_cell[&unit.pos()].len() > 1 {
            record_issue(
                referee,
                unit.player as usize,
                "apply",
                "opponent_plant_blocking",
                false,
                command,
            );
        }
    }
    apply_plant(&mut referee.game, &all_plants);

    let mut chop = parsed0.chop;
    chop.extend(parsed1.chop);
    apply_chop_on_existing_cells(&mut referee.game, &chop, &choppable_cells);

    for (player, picks) in [(0, parsed0.pick), (1, parsed1.pick)] {
        for (unit_id, item, command) in picks {
            let before = referee.game.inventories[player][engine::item_index(&item)];
            engine::apply_pick(&mut referee.game, &[(unit_id, item)]);
            if before == 0 {
                record_issue(
                    referee,
                    player,
                    "apply",
                    "pick_stock_lost",
                    false,
                    &command,
                );
            }
        }
    }

    for (player, trains) in [(0, parsed0.train), (1, parsed1.train)] {
        for (talents, command) in trains {
            let roster = referee
                .game
                .units
                .iter()
                .filter(|unit| unit.player as usize == player)
                .count();
            let cost = engine::training_cost(roster as i32, talents);
            let affordable = cost
                .iter()
                .enumerate()
                .all(|(index, amount)| referee.game.inventories[player][index] >= *amount);
            let shack_blocked = referee
                .game
                .units
                .iter()
                .any(|unit| unit.pos() == referee.game.shacks[player]);
            apply_train(&mut referee.game, player as i32, talents);
            let after = referee
                .game
                .units
                .iter()
                .filter(|unit| unit.player as usize == player)
                .count();
            if after == roster {
                let reason = if !affordable {
                    "train_affordability_lost"
                } else if shack_blocked {
                    "train_shack_blocked"
                } else {
                    "train_failed"
                };
                record_issue(referee, player, "apply", reason, false, &command);
            }
        }
    }

    let mut drop = parsed0.drop;
    drop.extend(parsed1.drop);
    apply_drop(&mut referee.game, &drop);

    let mut mine = parsed0.mine;
    mine.extend(parsed1.mine);
    apply_mine(&mut referee.game, &mine);

    tick_plants(&mut referee.game);
    recompute_scores(&mut referee.game);
    referee.game.turn += 1;
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::game::official_mapgen;
    use crate::game::state::{from_ascii, Plant, Unit};

    fn assert_same_state(left: &GameState, right: &GameState) {
        assert_eq!(left.width, right.width);
        assert_eq!(left.height, right.height);
        assert_eq!(left.walkable, right.walkable);
        assert_eq!(left.shacks, right.shacks);
        assert_eq!(left.inventories, right.inventories);
        assert_eq!(left.units, right.units);
        assert_eq!(left.plants, right.plants);
        assert_eq!(left.scores, right.scores);
        assert_eq!(left.turn, right.turn);
        assert_eq!(left.next_id, right.next_id);
        assert_eq!(left.iron, right.iron);
        assert_eq!(left.water, right.water);
    }

    #[test]
    fn continued_generator_is_field_identical_for_1024_seeds() {
        for seed in 9_900_000..9_901_024 {
            let continued = generate_official(seed);
            let historical = official_mapgen::generate_official(seed);
            assert_same_state(&continued.game, &historical);
        }
    }

    #[test]
    fn direct_target_consumes_no_rng() {
        let mut referee = generate_official(9_900_001);
        referee.game = from_ascii(&["0..1"]);
        let selected = select_next_cell(&mut referee, (0, 0), (1, 0), 1);
        assert_eq!(selected.cell, (1, 0));
        assert!(!selected.drew_rng);
        assert_eq!(referee.movement_rng, MovementRngStats::default());
    }

    #[test]
    fn unique_non_direct_target_consumes_bound_one_draw() {
        let mut referee = generate_official(9_900_002);
        referee.game = from_ascii(&["0..1"]);
        let mut expected_rng = referee.random.clone();
        assert_eq!(expected_rng.next_int(1), 0);
        let selected = select_next_cell(&mut referee, (0, 0), (2, 0), 1);
        assert_eq!(selected.cell, (1, 0));
        assert_eq!(selected.candidate_count, 1);
        assert!(selected.drew_rng);
        assert_eq!(
            referee.movement_rng,
            MovementRngStats {
                draws: 1,
                tied_draws: 0,
            }
        );
        for _ in 0..8 {
            assert_eq!(
                referee.random.next_int(10_000),
                expected_rng.next_int(10_000)
            );
        }
    }

    #[test]
    fn tied_candidates_follow_referee_x_major_y_minor_order() {
        let mut referee = generate_official(9_900_003);
        referee.game = from_ascii(&["0..", "...", "..1"]);
        let mut expected_rng = referee.random.clone();
        let expected_index = expected_rng.next_int(2) as usize;
        let selected = select_next_cell(&mut referee, (0, 0), (2, 2), 1);
        assert_eq!(selected.cell, [(0, 1), (1, 0)][expected_index]);
        assert_eq!(selected.candidate_count, 2);
        assert_eq!(
            referee.movement_rng,
            MovementRngStats {
                draws: 1,
                tied_draws: 1,
            }
        );
    }

    fn with_game(game: GameState) -> RefereeGame {
        let mut referee = generate_official(9_900_004);
        referee.game = game;
        referee.movement_rng = MovementRngStats::default();
        referee.legality = LegalityReport::default();
        referee
    }

    fn assert_single_issue(
        referee: &RefereeGame,
        player: usize,
        phase: &'static str,
        reason: &'static str,
        critical: bool,
    ) {
        assert_eq!(referee.legality.issue_count(), 1);
        let issue = &referee.legality.issues[0];
        assert_eq!(issue.player, player);
        assert_eq!(issue.phase, phase);
        assert_eq!(issue.reason, reason);
        assert_eq!(issue.critical, critical);
        assert_eq!(
            referee.legality.unclassified_issue_count(),
            usize::from(reason != "unknown_command" && reason != "train_failed" && critical)
        );
    }

    fn plum_tree(x: i32, y: i32, fruits: i32) -> Plant {
        Plant {
            plant_type: "PLUM".to_owned(),
            x,
            y,
            size: 1,
            health: engine::tree_health("PLUM", 1),
            fruits,
            cooldown: 5,
        }
    }

    fn second_player_zero_unit(game: &GameState) -> Unit {
        Unit {
            id: game.next_id,
            player: 0,
            x: 1,
            y: 0,
            ms: 1,
            cc: 1,
            hp: 1,
            chop: 0,
            carry: [0; 6],
        }
    }

    #[test]
    fn r1_error_taxonomy_is_frozen_and_unique() {
        assert_eq!(SUPPORTED_NONCRITICAL_REASONS.len(), 24);
        assert_eq!(
            SUPPORTED_NONCRITICAL_REASONS.iter().copied().collect::<HashSet<_>>().len(),
            SUPPORTED_NONCRITICAL_REASONS.len()
        );
        assert_eq!(KNOWN_CRITICAL_REASONS, ["unknown_command", "train_failed"]);
        assert!(SUPPORTED_NONCRITICAL_REASONS
            .iter()
            .all(|reason| !KNOWN_CRITICAL_REASONS.contains(reason)));
    }

    #[test]
    fn unit_lookup_reuse_and_bounds_failures_are_noncritical_and_do_not_execute() {
        let mut referee = with_game(from_ascii(&["0..1"]));
        let before = referee.game.units.clone();
        step(
            &mut referee,
            &["HARVEST 99".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "unit_not_found", false);
        assert_eq!(referee.game.units, before);
        assert_eq!(referee.game.turn, 2);

        let mut referee = with_game(from_ascii(&["0..1"]));
        let before = referee.game.units.clone();
        step(
            &mut referee,
            &["HARVEST 1".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "unit_not_owned", false);
        assert_eq!(referee.game.units, before);

        let mut referee = with_game(from_ascii(&["0..1"]));
        let before = referee.game.units.clone();
        step(
            &mut referee,
            &["MOVE 0 0 0".to_owned(), "HARVEST 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "unit_already_used", false);
        assert_eq!(referee.game.units, before);

        let mut referee = with_game(from_ascii(&["0..1"]));
        let before = referee.game.units.clone();
        step(
            &mut referee,
            &["MOVE 0 -1 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "out_of_board", false);
        assert_eq!(referee.game.units, before);
        assert_eq!(referee.movement_rng.draws, 0);
    }

    #[test]
    fn train_parse_failures_are_noncritical_and_do_not_create_a_unit() {
        let mut game = from_ascii(&["0.+1"]);
        game.inventories[0] = [100; 6];
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["TRAIN 0 1 1 1".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "invalid_skill", false);
        assert_eq!(
            referee
                .game
                .units
                .iter()
                .filter(|unit| unit.player == 0)
                .count(),
            1
        );

        let mut referee = with_game(from_ascii(&["0.+1"]));
        step(
            &mut referee,
            &["TRAIN 1 1 1 1".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "cant_afford_train", false);
        assert_eq!(
            referee
                .game
                .units
                .iter()
                .filter(|unit| unit.player == 0)
                .count(),
            1
        );
    }

    #[test]
    fn harvest_parse_failures_preserve_fruit_and_carry() {
        let mut referee = with_game(from_ascii(&["0..1"]));
        step(
            &mut referee,
            &["HARVEST 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_plant", false);
        assert_eq!(referee.game.units[0].total(), 0);

        let mut game = from_ascii(&["0..1"]);
        game.units[0].x = 1;
        game.plants.push(plum_tree(1, 0, 0));
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["HARVEST 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_fruit", false);
        assert_eq!(referee.game.units[0].total(), 0);
        assert_eq!(referee.game.plants[0].fruits, 0);
        assert_eq!(referee.game.plants[0].cooldown, 4);

        let mut game = from_ascii(&["0..1"]);
        game.units[0].x = 1;
        game.units[0].carry[engine::PLUM] = 1;
        game.plants.push(plum_tree(1, 0, 1));
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["HARVEST 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_capacity", false);
        assert_eq!(referee.game.units[0].carry[engine::PLUM], 1);
        assert_eq!(referee.game.plants[0].fruits, 1);

        let mut game = from_ascii(&["0..1"]);
        game.units[0].x = 1;
        game.units[0].hp = 0;
        game.plants.push(plum_tree(1, 0, 1));
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["HARVEST 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_harvest", false);
        assert_eq!(referee.game.units[0].total(), 0);
        assert_eq!(referee.game.plants[0].fruits, 1);
    }

    #[test]
    fn plant_parse_failures_preserve_seed_and_plant_state() {
        let mut game = from_ascii(&["0..1"]);
        game.units[0].carry[engine::IRON] = 1;
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["PLANT 0 IRON".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "invalid_plant", false);
        assert_eq!(referee.game.units[0].carry[engine::IRON], 1);
        assert!(referee.game.plants.is_empty());

        let mut game = from_ascii(&["0..1"]);
        game.units[0].carry[engine::PLUM] = 1;
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["PLANT 0 PLUM".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_grass", false);
        assert_eq!(referee.game.units[0].carry[engine::PLUM], 1);
        assert!(referee.game.plants.is_empty());

        let mut game = from_ascii(&["0..1"]);
        game.units[0].x = 1;
        game.units[0].carry[engine::PLUM] = 1;
        game.plants.push(plum_tree(1, 0, 0));
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["PLANT 0 PLUM".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "existing_plant", false);
        assert_eq!(referee.game.units[0].carry[engine::PLUM], 1);
        assert_eq!(referee.game.plants.len(), 1);

        let mut game = from_ascii(&["0..1"]);
        game.units[0].x = 1;
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["PLANT 0 PLUM".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_seeds", false);
        assert!(referee.game.plants.is_empty());
    }

    #[test]
    fn chop_pick_drop_and_mine_parse_failures_do_not_apply() {
        let mut game = from_ascii(&["0..1"]);
        game.units[0].x = 1;
        game.plants.push(plum_tree(1, 0, 0));
        let original_health = game.plants[0].health;
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["CHOP 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_chop", false);
        assert_eq!(referee.game.plants[0].health, original_health);

        let mut referee = with_game(from_ascii(&["0..1"]));
        step(
            &mut referee,
            &["PICK 0 PLUM".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "out_of_stock", false);
        assert_eq!(referee.game.units[0].total(), 0);

        let mut game = from_ascii(&["0...1"]);
        game.units[0].x = 2;
        game.inventories[0][engine::PLUM] = 1;
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["PICK 0 PLUM".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_shack", false);
        assert_eq!(referee.game.inventories[0][engine::PLUM], 1);
        assert_eq!(referee.game.units[0].total(), 0);

        let mut referee = with_game(from_ascii(&["0..1"]));
        step(
            &mut referee,
            &["DROP 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "nothing_to_drop", false);
        assert_eq!(referee.game.inventories[0], [0; 6]);

        let mut game = from_ascii(&["0..1"]);
        game.units[0].chop = 1;
        let mut referee = with_game(game);
        step(
            &mut referee,
            &["MINE 0".to_owned()],
            &["WAIT".to_owned()],
        );
        assert_single_issue(&referee, 0, "parse", "no_iron", false);
        assert_eq!(referee.game.units[0].carry[engine::IRON], 0);
    }

    #[test]
    fn blocked_move_is_noncritical_and_leaves_the_mover_in_place() {
        let mut game = from_ascii(&["0..1"]);
        let blocker = second_player_zero_unit(&game);
        game.next_id += 1;
        game.units.push(blocker);
        let before = game.units.clone();
        let mut referee = with_game(game);

        step(
            &mut referee,
            &["MOVE 0 1 0".to_owned()],
            &["WAIT".to_owned()],
        );

        assert_single_issue(&referee, 0, "apply", "move_blocked", false);
        assert_eq!(referee.game.units, before);
        assert_eq!(referee.movement_rng.draws, 0);
    }

    #[test]
    fn second_pick_loses_stock_at_apply_but_first_pick_still_executes() {
        let mut game = from_ascii(&["0..1"]);
        let picker = second_player_zero_unit(&game);
        game.next_id += 1;
        game.units.push(picker);
        game.inventories[0][engine::PLUM] = 1;
        let mut referee = with_game(game);

        step(
            &mut referee,
            &["PICK 0 PLUM".to_owned(), "PICK 2 PLUM".to_owned()],
            &["WAIT".to_owned()],
        );

        assert_single_issue(&referee, 0, "apply", "pick_stock_lost", false);
        assert_eq!(referee.game.inventories[0][engine::PLUM], 0);
        assert_eq!(referee.game.units[0].carry[engine::PLUM], 1);
        assert_eq!(referee.game.units[2].carry[engine::PLUM], 0);
    }

    #[test]
    fn occupied_shack_train_failure_is_noncritical_and_spends_nothing() {
        let mut game = from_ascii(&["0.+1"]);
        game.inventories[0] = [2, 2, 2, 0, 2, 0];
        let before = game.inventories[0];
        let mut referee = with_game(game);

        step(
            &mut referee,
            &["TRAIN 1 1 1 1".to_owned()],
            &["WAIT".to_owned()],
        );

        assert_single_issue(&referee, 0, "apply", "train_shack_blocked", false);
        assert_eq!(referee.game.inventories[0], before);
        assert_eq!(
            referee
                .game
                .units
                .iter()
                .filter(|unit| unit.player == 0)
                .count(),
            1
        );
    }

    #[test]
    fn defensive_and_future_failures_are_critical_by_construction() {
        let mut referee = with_game(from_ascii(&["0..1"]));
        record_issue(
            &mut referee,
            0,
            "apply",
            "train_failed",
            false,
            "TRAIN 1 1 1 1",
        );
        assert_single_issue(&referee, 0, "apply", "train_failed", true);
        assert_eq!(referee.legality.unclassified_issue_count(), 0);

        let mut referee = with_game(from_ascii(&["0..1"]));
        record_issue(
            &mut referee,
            1,
            "apply",
            "future_source_failure",
            false,
            "FUTURE",
        );
        assert_single_issue(
            &referee,
            1,
            "apply",
            "future_source_failure",
            true,
        );
        assert_eq!(referee.legality.unclassified_issue_count(), 1);
    }

    #[test]
    fn legal_move_vacates_shack_before_train() {
        let mut game = from_ascii(&["0.+1"]);
        game.inventories[0] = [2, 2, 2, 0, 2, 0];
        let mut referee = with_game(game);

        step(
            &mut referee,
            &["MOVE 0 1 0".to_owned(), "TRAIN 1 1 1 1".to_owned()],
            &["WAIT".to_owned()],
        );

        assert_eq!(referee.legality.issue_count(), 0);
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
    fn pick_can_make_a_parse_legal_train_fail_at_apply_time() {
        let mut game = from_ascii(&["0.+1"]);
        game.inventories[0] = [2, 2, 2, 0, 2, 0];
        let mut referee = with_game(game);

        step(
            &mut referee,
            &["PICK 0 PLUM".to_owned(), "TRAIN 1 1 1 1".to_owned()],
            &["WAIT".to_owned()],
        );

        assert_single_issue(
            &referee,
            0,
            "apply",
            "train_affordability_lost",
            false,
        );
        assert_eq!(
            referee
                .game
                .units
                .iter()
                .filter(|unit| unit.player == 0)
                .count(),
            1
        );
    }

    #[test]
    fn ownership_reuse_and_unknown_commands_are_reason_counted() {
        let mut referee = with_game(from_ascii(&["0..1"]));
        step(
            &mut referee,
            &[
                "HARVEST 0".to_owned(),
                "MOVE 0 1 0".to_owned(),
                "MOVE 1 1 0".to_owned(),
                "DANCE".to_owned(),
            ],
            &["WAIT".to_owned()],
        );

        assert_eq!(
            referee.legality.reason_counts(),
            BTreeMap::from([
                ("no_plant", 1),
                ("unit_already_used", 1),
                ("unit_not_owned", 1),
                ("unknown_command", 1),
            ])
        );
        assert_eq!(referee.legality.issue_count_for_player(0), 4);
        assert_eq!(referee.legality.issue_count_for_player(1), 0);
        assert_eq!(referee.legality.critical_issue_count(), 1);
        assert_eq!(referee.legality.critical_issue_count_for_player(0), 1);
        assert_eq!(referee.legality.unclassified_issue_count(), 0);
    }

    #[test]
    fn mixed_type_simultaneous_planting_is_an_apply_failure() {
        let mut game = from_ascii(&["0..1"]);
        game.units[0].x = 1;
        game.units[1].x = 1;
        game.units[0].carry[engine::PLUM] = 1;
        game.units[1].carry[engine::LEMON] = 1;
        let mut referee = with_game(game);

        step(
            &mut referee,
            &["PLANT 0 PLUM".to_owned()],
            &["PLANT 1 LEMON".to_owned()],
        );

        assert_eq!(
            referee.legality.reason_counts(),
            BTreeMap::from([("opponent_plant_blocking", 2)])
        );
        assert!(referee
            .legality
            .issues
            .iter()
            .all(|issue| !issue.critical && issue.phase == "apply"));
        assert_eq!(referee.legality.issue_count_for_player(0), 1);
        assert_eq!(referee.legality.issue_count_for_player(1), 1);
        assert_eq!(referee.legality.unclassified_issue_count(), 0);
        assert!(referee.game.plants.is_empty());
        assert_eq!(referee.game.units[0].carry[engine::PLUM], 1);
        assert_eq!(referee.game.units[1].carry[engine::LEMON], 1);
    }
}
