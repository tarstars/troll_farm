//! Shared-state terminal rollout study for resident versus worker-three continuation.
//!
//! Every scenario runs an exact resident prefix against one evaluation opponent, forks the
//! resulting state, and evaluates both frozen macro branches against all local opponent models.
//! Model compatibility is computed only from observable prefix state transitions.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::collections::{BTreeMap, BTreeSet, VecDeque};
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::{GameState, Plant as EnginePlant, Unit as EngineUnit};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_research::{
    resident_three_worker_commands_with_profile, NorxondorThreeWorkerSilver, ResidentFundingProfile,
};
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

type Factory = fn() -> Box<dyn Strategy>;

fn compact() -> Box<dyn Strategy> {
    Box::new(CompactGold::new())
}
fn gold() -> Box<dyn Strategy> {
    Box::new(GoldElite::new())
}
fn adaptive() -> Box<dyn Strategy> {
    Box::new(GoldElite::adaptive())
}
fn mybot() -> Box<dyn Strategy> {
    Box::new(MyBot::new())
}
fn printer() -> Box<dyn Strategy> {
    Box::new(PrinterBot::new())
}
fn scheduler() -> Box<dyn Strategy> {
    Box::new(SchedBot::new())
}
fn script() -> Box<dyn Strategy> {
    Box::new(ScriptBoss::new())
}
fn silver() -> Box<dyn Strategy> {
    Box::new(SilverBoss::new())
}

const MODELS: [(&str, Factory); 8] = [
    ("compact_gold", compact),
    ("gold_adaptive", adaptive),
    ("gold_elite", gold),
    ("mybot", mybot),
    ("printer_bot", printer),
    ("sched_bot", scheduler),
    ("script_boss", script),
    ("silver_boss", silver),
];

fn yamo_view(game: &GameState, player: usize) -> YamoState {
    let opponent = 1 - player;
    YamoState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect::<BTreeSet<_>>(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game
            .units
            .iter()
            .map(|unit| Unit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
                cell: unit.pos(),
                stats: Stats {
                    movement_speed: unit.ms,
                    carry_capacity: unit.cc,
                    harvest_power: unit.hp,
                    chop_power: unit.chop,
                },
                carry: unit.carry,
            })
            .collect(),
        plants: game
            .plants
            .iter()
            .map(|plant| Plant {
                kind: PlantKind::parse(&plant.plant_type).expect("known plant type"),
                cell: plant.pos(),
                size: plant.size,
                health: plant.health,
                fruits: plant.fruits,
                cooldown: plant.cooldown,
            })
            .collect(),
        scores: [game.scores[player], game.scores[opponent]],
        turn: game.turn,
        next_id: game.next_id,
        iron: game.iron.iter().copied().collect::<BTreeSet<_>>(),
        water: game.water.iter().copied().collect::<BTreeSet<_>>(),
    }
}

#[derive(Clone)]
struct Prefix {
    states: Vec<GameState>,
    our_commands: Vec<Vec<String>>,
    root: GameState,
}

fn apply_commands(game: &mut GameState, seat: usize, ours: &[String], theirs: &[String]) {
    if seat == 0 {
        step(game, ours, theirs);
    } else {
        step(game, theirs, ours);
    }
}

fn resident_prefix(seed: u64, seat: usize, actual_model: usize, decision_turn: i32) -> Prefix {
    let mut game = generate_bronze(seed);
    let mut resident = SecureOrchardBot::new();
    let opponent = MODELS[actual_model].1();
    let mut states = Vec::new();
    let mut our_commands = Vec::new();
    while game.turn < decision_turn {
        states.push(game.clone());
        let ours = resident.commands(&yamo_view(&game, seat));
        let theirs = opponent.decide(&game, 1 - seat);
        our_commands.push(ours.clone());
        apply_commands(&mut game, seat, &ours, &theirs);
    }
    Prefix {
        states,
        our_commands,
        root: game,
    }
}

fn warmed_resident(prefix: &Prefix, seat: usize) -> SecureOrchardBot {
    let mut resident = SecureOrchardBot::new();
    for state in &prefix.states {
        let _ = resident.commands(&yamo_view(state, seat));
    }
    resident
}

fn warmed_model(prefix: &Prefix, seat: usize, model: usize) -> Box<dyn Strategy> {
    let strategy = MODELS[model].1();
    for state in &prefix.states {
        let _ = strategy.decide(state, 1 - seat);
    }
    strategy
}

fn unit_map(game: &GameState) -> BTreeMap<i32, &EngineUnit> {
    game.units.iter().map(|unit| (unit.id, unit)).collect()
}

fn plant_map(game: &GameState) -> BTreeMap<(i32, i32, &str), &EnginePlant> {
    game.plants
        .iter()
        .map(|plant| ((plant.x, plant.y, plant.plant_type.as_str()), plant))
        .collect()
}

fn observable_distance(left: &GameState, right: &GameState) -> i64 {
    let mut distance = 0i64;
    distance += 1_000 * i64::from((left.next_id - right.next_id).abs());
    distance += 50 * i64::from((left.turn - right.turn).abs());
    for player in 0..2 {
        distance += 10 * i64::from((left.scores[player] - right.scores[player]).abs());
        for item in 0..6 {
            distance += 20
                * i64::from(
                    (left.inventories[player][item] - right.inventories[player][item]).abs(),
                );
        }
    }

    let left_units = unit_map(left);
    let right_units = unit_map(right);
    let unit_ids: BTreeSet<_> = left_units
        .keys()
        .chain(right_units.keys())
        .copied()
        .collect();
    for id in unit_ids {
        match (left_units.get(&id), right_units.get(&id)) {
            (Some(left), Some(right)) => {
                distance += 1_000 * i64::from((left.player - right.player).abs());
                distance += 100
                    * i64::from(
                        (left.ms - right.ms).abs()
                            + (left.cc - right.cc).abs()
                            + (left.hp - right.hp).abs()
                            + (left.chop - right.chop).abs(),
                    );
                distance += 5 * i64::from((left.x - right.x).abs() + (left.y - right.y).abs());
                distance += 20
                    * left
                        .carry
                        .iter()
                        .zip(right.carry.iter())
                        .map(|(a, b)| i64::from((a - b).abs()))
                        .sum::<i64>();
            }
            _ => distance += 2_000,
        }
    }

    let left_plants = plant_map(left);
    let right_plants = plant_map(right);
    let plant_keys: BTreeSet<_> = left_plants
        .keys()
        .chain(right_plants.keys())
        .copied()
        .collect();
    for key in plant_keys {
        match (left_plants.get(&key), right_plants.get(&key)) {
            (Some(left), Some(right)) => {
                distance += 5 * i64::from(
                    (left.size - right.size).abs()
                        + (left.health - right.health).abs()
                        + (left.fruits - right.fruits).abs()
                        + (left.cooldown - right.cooldown).abs(),
                );
            }
            _ => distance += 500,
        }
    }
    distance
}

fn compatibility(prefix: &Prefix, seat: usize, model: usize) -> (i64, usize) {
    let strategy = MODELS[model].1();
    let mut distance = 0;
    let mut exact = 0;
    for index in 0..prefix.states.len() {
        let state = &prefix.states[index];
        let theirs = strategy.decide(state, 1 - seat);
        let mut predicted = state.clone();
        apply_commands(&mut predicted, seat, &prefix.our_commands[index], &theirs);
        let actual_next = prefix.states.get(index + 1).unwrap_or(&prefix.root);
        let delta = observable_distance(&predicted, actual_next);
        distance += delta;
        exact += usize::from(delta == 0);
    }
    (distance, exact)
}

#[derive(Clone, Copy)]
struct BranchResult {
    margin: i32,
    score: i32,
    workers: usize,
    second_worker_turn: i32,
    third_worker_turn: i32,
}

fn record_worker_turns(
    game: &GameState,
    seat: usize,
    second_worker_turn: &mut i32,
    third_worker_turn: &mut i32,
) {
    let workers = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == seat)
        .count();
    if *second_worker_turn < 0 && workers >= 2 {
        *second_worker_turn = game.turn;
    }
    if *third_worker_turn < 0 && workers >= 3 {
        *third_worker_turn = game.turn;
    }
}

fn rollout(prefix: &Prefix, seat: usize, model: usize, three_worker: bool) -> BranchResult {
    let mut game = prefix.root.clone();
    let mut resident = warmed_resident(prefix, seat);
    let alternative = NorxondorThreeWorkerSilver::new();
    let opposition = warmed_model(prefix, seat, model);
    let mut turns_until_end = 0;
    let mut second_worker_turn = -1;
    let mut third_worker_turn = -1;
    record_worker_turns(&game, seat, &mut second_worker_turn, &mut third_worker_turn);
    while game.turn <= 300 {
        let ours = if three_worker {
            alternative.decide(&game, seat)
        } else {
            resident.commands(&yamo_view(&game, seat))
        };
        let theirs = opposition.decide(&game, 1 - seat);
        apply_commands(&mut game, seat, &ours, &theirs);
        record_worker_turns(&game, seat, &mut second_worker_turn, &mut third_worker_turn);
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    BranchResult {
        margin: game.scores[seat] - game.scores[1 - seat],
        score: game.scores[seat],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        second_worker_turn,
        third_worker_turn,
    }
}

fn rollout_resident_three_worker(prefix: &Prefix, seat: usize, model: usize) -> BranchResult {
    rollout_resident_three_worker_with_profile(
        prefix,
        seat,
        model,
        ResidentFundingProfile::TwoOldest,
    )
}

fn rollout_resident_three_worker_with_profile(
    prefix: &Prefix,
    seat: usize,
    model: usize,
    funding_profile: ResidentFundingProfile,
) -> BranchResult {
    let mut game = prefix.root.clone();
    let mut resident = warmed_resident(prefix, seat);
    let opposition = warmed_model(prefix, seat, model);
    let mut turns_until_end = 0;
    let mut second_worker_turn = -1;
    let mut third_worker_turn = -1;
    record_worker_turns(&game, seat, &mut second_worker_turn, &mut third_worker_turn);
    while game.turn <= 300 {
        let commands = resident.commands(&yamo_view(&game, seat));
        let ours =
            resident_three_worker_commands_with_profile(commands, &game, seat, funding_profile);
        let theirs = opposition.decide(&game, 1 - seat);
        apply_commands(&mut game, seat, &ours, &theirs);
        record_worker_turns(&game, seat, &mut second_worker_turn, &mut third_worker_turn);
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    BranchResult {
        margin: game.scores[seat] - game.scores[1 - seat],
        score: game.scores[seat],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        second_worker_turn,
        third_worker_turn,
    }
}

#[derive(Clone, Copy)]
enum RoleController {
    Silver,
    Compact,
    Adaptive,
    CompactHarvestersSilverNewest,
    CompactStarterSilverNewest,
    CompactStarterSilverExtras,
    CompactHarvestersEnemyDoor,
    CompactHarvestersEnemyHalfLargest,
    CompactHarvestersEnemyHalfNearest,
    CompactHarvestersEnemyBanana,
    CompactHarvestersEnemyValue,
    CompactStarterEnemyDoorExtras,
    CompactStarterEnemyBananaExtras,
    CompactStarterEnemyValueExtras,
}

#[derive(Clone, Copy)]
enum RoleMask {
    Newest,
    Extras,
    Harvesters,
    Starter,
    All,
}

const ROLE_POLICIES: [(&str, RoleController, RoleMask); 26] = [
    ("silver_newest", RoleController::Silver, RoleMask::Newest),
    ("silver_extras", RoleController::Silver, RoleMask::Extras),
    (
        "silver_harvesters",
        RoleController::Silver,
        RoleMask::Harvesters,
    ),
    ("silver_starter", RoleController::Silver, RoleMask::Starter),
    ("silver_all", RoleController::Silver, RoleMask::All),
    ("compact_newest", RoleController::Compact, RoleMask::Newest),
    ("compact_extras", RoleController::Compact, RoleMask::Extras),
    (
        "compact_harvesters",
        RoleController::Compact,
        RoleMask::Harvesters,
    ),
    (
        "compact_starter",
        RoleController::Compact,
        RoleMask::Starter,
    ),
    ("compact_all", RoleController::Compact, RoleMask::All),
    (
        "adaptive_newest",
        RoleController::Adaptive,
        RoleMask::Newest,
    ),
    (
        "adaptive_extras",
        RoleController::Adaptive,
        RoleMask::Extras,
    ),
    (
        "adaptive_harvesters",
        RoleController::Adaptive,
        RoleMask::Harvesters,
    ),
    (
        "adaptive_starter",
        RoleController::Adaptive,
        RoleMask::Starter,
    ),
    ("adaptive_all", RoleController::Adaptive, RoleMask::All),
    (
        "compact_harvesters_silver_newest",
        RoleController::CompactHarvestersSilverNewest,
        RoleMask::All,
    ),
    (
        "compact_starter_silver_newest",
        RoleController::CompactStarterSilverNewest,
        RoleMask::All,
    ),
    (
        "compact_starter_silver_extras",
        RoleController::CompactStarterSilverExtras,
        RoleMask::All,
    ),
    (
        "compact_harvesters_enemy_door",
        RoleController::CompactHarvestersEnemyDoor,
        RoleMask::All,
    ),
    (
        "compact_harvesters_enemy_half_largest",
        RoleController::CompactHarvestersEnemyHalfLargest,
        RoleMask::All,
    ),
    (
        "compact_harvesters_enemy_half_nearest",
        RoleController::CompactHarvestersEnemyHalfNearest,
        RoleMask::All,
    ),
    (
        "compact_harvesters_enemy_banana",
        RoleController::CompactHarvestersEnemyBanana,
        RoleMask::All,
    ),
    (
        "compact_harvesters_enemy_value",
        RoleController::CompactHarvestersEnemyValue,
        RoleMask::All,
    ),
    (
        "compact_starter_enemy_door_extras",
        RoleController::CompactStarterEnemyDoorExtras,
        RoleMask::All,
    ),
    (
        "compact_starter_enemy_banana_extras",
        RoleController::CompactStarterEnemyBananaExtras,
        RoleMask::All,
    ),
    (
        "compact_starter_enemy_value_extras",
        RoleController::CompactStarterEnemyValueExtras,
        RoleMask::All,
    ),
];

const FUNDING_PROFILES: [(&str, ResidentFundingProfile); 10] = [
    ("two_oldest_t3", ResidentFundingProfile::TwoOldest),
    ("one_oldest_t3", ResidentFundingProfile::OneOldest),
    ("one_newest_t3", ResidentFundingProfile::OneNewest),
    (
        "two_oldest_t6",
        ResidentFundingProfile::DelayedTwo { start_turn: 6 },
    ),
    (
        "two_oldest_t10",
        ResidentFundingProfile::DelayedTwo { start_turn: 10 },
    ),
    (
        "two_oldest_t15",
        ResidentFundingProfile::DelayedTwo { start_turn: 15 },
    ),
    (
        "two_oldest_t20",
        ResidentFundingProfile::DelayedTwo { start_turn: 20 },
    ),
    (
        "one_oldest_then_two_t10",
        ResidentFundingProfile::OldestThenTwo { switch_turn: 10 },
    ),
    (
        "one_newest_then_two_t10",
        ResidentFundingProfile::NewestThenTwo { switch_turn: 10 },
    ),
    (
        "one_newest_then_two_t15",
        ResidentFundingProfile::NewestThenTwo { switch_turn: 15 },
    ),
];

#[derive(Clone, Copy)]
enum EnemyDenialTarget {
    Door,
    HalfLargest,
    HalfNearest,
    Banana,
    Value,
}

fn command_unit_id(command: &str) -> Option<i32> {
    let mut fields = command.split_whitespace();
    match fields.next()? {
        "MOVE" | "DROP" | "CHOP" | "HARVEST" | "MINE" | "PLANT" | "PICK" => {
            fields.next()?.parse::<i32>().ok()
        }
        _ => None,
    }
}

fn role_selected(unit: &EngineUnit, ordered_ids: &[i32], mask: RoleMask) -> bool {
    match mask {
        RoleMask::Newest => ordered_ids.last() == Some(&unit.id),
        RoleMask::Extras => ordered_ids.first() != Some(&unit.id),
        RoleMask::Harvesters => unit.hp > 0 && unit.chop < 2,
        RoleMask::Starter => ordered_ids.first() == Some(&unit.id),
        RoleMask::All => true,
    }
}

fn apply_role_commands(
    mut resident: Vec<String>,
    role_commands: Vec<String>,
    game: &GameState,
    seat: usize,
    mask: RoleMask,
) -> Vec<String> {
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == seat)
        .collect();
    units.sort_by_key(|unit| unit.id);
    let ordered_ids: Vec<_> = units.iter().map(|unit| unit.id).collect();
    let role_by_id: BTreeMap<_, _> = role_commands
        .into_iter()
        .filter_map(|command| command_unit_id(&command).map(|id| (id, command)))
        .collect();
    for unit in units {
        if role_selected(unit, &ordered_ids, mask) {
            if let Some(command) = role_by_id.get(&unit.id) {
                resident.retain(|candidate| command_unit_id(candidate) != Some(unit.id));
                resident.push(command.clone());
            }
        }
    }
    resident
}

fn engine_distances(game: &GameState, source: (i32, i32)) -> BTreeMap<(i32, i32), i32> {
    let mut distances = BTreeMap::from([(source, 0)]);
    let mut queue = VecDeque::from([source]);
    while let Some((x, y)) = queue.pop_front() {
        let next_distance = distances[&(x, y)] + 1;
        for (dx, dy) in [(0, 1), (1, 0), (0, -1), (-1, 0)] {
            let cell = (x + dx, y + dy);
            if game.walkable.contains(&cell) && !distances.contains_key(&cell) {
                distances.insert(cell, next_distance);
                queue.push_back(cell);
            }
        }
    }
    distances
}

fn enemy_denial_command(
    game: &GameState,
    seat: usize,
    unit: &EngineUnit,
    target: EnemyDenialTarget,
    reserved: &mut BTreeSet<(i32, i32)>,
) -> String {
    let own_shack = game.shacks[seat];
    let enemy_shack = game.shacks[1 - seat];
    if unit.free() == 0 {
        return if (unit.x - own_shack.0).abs() + (unit.y - own_shack.1).abs() == 1 {
            format!("DROP {}", unit.id)
        } else {
            format!("MOVE {} {} {}", unit.id, own_shack.0, own_shack.1)
        };
    }
    if game.plants.iter().any(|plant| plant.pos() == unit.pos()) && unit.chop > 0 {
        return format!("CHOP {}", unit.id);
    }
    let distances = engine_distances(game, unit.pos());
    let selected = game
        .plants
        .iter()
        .filter(|plant| distances.contains_key(&plant.pos()) && !reserved.contains(&plant.pos()))
        .min_by_key(|plant| {
            let enemy_distance = (plant.x - enemy_shack.0).abs() + (plant.y - enemy_shack.1).abs();
            let own_distance = (plant.x - own_shack.0).abs() + (plant.y - own_shack.1).abs();
            let travel = distances[&plant.pos()];
            match target {
                EnemyDenialTarget::Door => (enemy_distance, travel, -plant.size, plant.pos()),
                EnemyDenialTarget::HalfLargest => (
                    i32::from(enemy_distance > own_distance),
                    -plant.size,
                    travel,
                    plant.pos(),
                ),
                EnemyDenialTarget::HalfNearest => (
                    i32::from(enemy_distance > own_distance),
                    travel,
                    -plant.size,
                    plant.pos(),
                ),
                EnemyDenialTarget::Banana => (
                    i32::from(!(plant.plant_type == "BANANA" && enemy_distance <= 6)),
                    enemy_distance,
                    travel,
                    plant.pos(),
                ),
                EnemyDenialTarget::Value => (
                    travel + enemy_distance - 4 * plant.size,
                    enemy_distance,
                    -plant.size,
                    plant.pos(),
                ),
            }
        })
        .map(|plant| plant.pos());
    if let Some(cell) = selected {
        reserved.insert(cell);
    }
    selected.map_or_else(
        || format!("MOVE {} {} {}", unit.id, own_shack.0, own_shack.1),
        |cell| format!("MOVE {} {} {}", unit.id, cell.0, cell.1),
    )
}

fn rollout_resident_role(
    prefix: &Prefix,
    seat: usize,
    model: usize,
    controller: RoleController,
    mask: RoleMask,
) -> BranchResult {
    rollout_resident_role_with_profile(
        prefix,
        seat,
        model,
        controller,
        mask,
        ResidentFundingProfile::TwoOldest,
    )
}

fn rollout_resident_role_with_profile(
    prefix: &Prefix,
    seat: usize,
    model: usize,
    controller: RoleController,
    mask: RoleMask,
    funding_profile: ResidentFundingProfile,
) -> BranchResult {
    let mut game = prefix.root.clone();
    let mut resident = warmed_resident(prefix, seat);
    let (roles, enemy_denial): (
        Vec<(Box<dyn Strategy>, RoleMask)>,
        Option<(EnemyDenialTarget, RoleMask)>,
    ) = match controller {
        RoleController::Silver => (vec![(Box::new(SilverBoss::new()), mask)], None),
        RoleController::Compact => (vec![(Box::new(CompactGold::new()), mask)], None),
        RoleController::Adaptive => (vec![(Box::new(GoldElite::adaptive()), mask)], None),
        RoleController::CompactHarvestersSilverNewest => (
            vec![
                (Box::new(CompactGold::new()), RoleMask::Harvesters),
                (Box::new(SilverBoss::new()), RoleMask::Newest),
            ],
            None,
        ),
        RoleController::CompactStarterSilverNewest => (
            vec![
                (Box::new(CompactGold::new()), RoleMask::Starter),
                (Box::new(SilverBoss::new()), RoleMask::Newest),
            ],
            None,
        ),
        RoleController::CompactStarterSilverExtras => (
            vec![
                (Box::new(CompactGold::new()), RoleMask::Starter),
                (Box::new(SilverBoss::new()), RoleMask::Extras),
            ],
            None,
        ),
        RoleController::CompactHarvestersEnemyDoor => (
            vec![(Box::new(CompactGold::new()), RoleMask::Harvesters)],
            Some((EnemyDenialTarget::Door, RoleMask::Newest)),
        ),
        RoleController::CompactHarvestersEnemyHalfLargest => (
            vec![(Box::new(CompactGold::new()), RoleMask::Harvesters)],
            Some((EnemyDenialTarget::HalfLargest, RoleMask::Newest)),
        ),
        RoleController::CompactHarvestersEnemyHalfNearest => (
            vec![(Box::new(CompactGold::new()), RoleMask::Harvesters)],
            Some((EnemyDenialTarget::HalfNearest, RoleMask::Newest)),
        ),
        RoleController::CompactHarvestersEnemyBanana => (
            vec![(Box::new(CompactGold::new()), RoleMask::Harvesters)],
            Some((EnemyDenialTarget::Banana, RoleMask::Newest)),
        ),
        RoleController::CompactHarvestersEnemyValue => (
            vec![(Box::new(CompactGold::new()), RoleMask::Harvesters)],
            Some((EnemyDenialTarget::Value, RoleMask::Newest)),
        ),
        RoleController::CompactStarterEnemyDoorExtras => (
            vec![(Box::new(CompactGold::new()), RoleMask::Starter)],
            Some((EnemyDenialTarget::Door, RoleMask::Extras)),
        ),
        RoleController::CompactStarterEnemyBananaExtras => (
            vec![(Box::new(CompactGold::new()), RoleMask::Starter)],
            Some((EnemyDenialTarget::Banana, RoleMask::Extras)),
        ),
        RoleController::CompactStarterEnemyValueExtras => (
            vec![(Box::new(CompactGold::new()), RoleMask::Starter)],
            Some((EnemyDenialTarget::Value, RoleMask::Extras)),
        ),
    };
    for state in &prefix.states {
        for (role, _) in &roles {
            let _ = role.decide(state, seat);
        }
    }
    let opposition = warmed_model(prefix, seat, model);
    let mut turns_until_end = 0;
    let mut second_worker_turn = -1;
    let mut third_worker_turn = -1;
    record_worker_turns(&game, seat, &mut second_worker_turn, &mut third_worker_turn);
    while game.turn <= 300 {
        let resident_commands = resident.commands(&yamo_view(&game, seat));
        let mut ours = resident_three_worker_commands_with_profile(
            resident_commands,
            &game,
            seat,
            funding_profile,
        );
        let role_commands: Vec<_> = roles
            .iter()
            .map(|(role, role_mask)| (role.decide(&game, seat), *role_mask))
            .collect();
        let worker_count = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count();
        if worker_count >= 3 {
            for (commands, role_mask) in role_commands {
                ours = apply_role_commands(ours, commands, &game, seat, role_mask);
            }
            if let Some((target, denial_mask)) = enemy_denial {
                let mut units: Vec<_> = game
                    .units
                    .iter()
                    .filter(|unit| unit.player as usize == seat)
                    .collect();
                units.sort_by_key(|unit| unit.id);
                let ordered_ids: Vec<_> = units.iter().map(|unit| unit.id).collect();
                let mut reserved = BTreeSet::new();
                for unit in units {
                    if role_selected(unit, &ordered_ids, denial_mask) {
                        let command =
                            enemy_denial_command(&game, seat, unit, target, &mut reserved);
                        ours.retain(|candidate| command_unit_id(candidate) != Some(unit.id));
                        ours.push(command);
                    }
                }
            }
        }
        let theirs = opposition.decide(&game, 1 - seat);
        apply_commands(&mut game, seat, &ours, &theirs);
        record_worker_turns(&game, seat, &mut second_worker_turn, &mut third_worker_turn);
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    BranchResult {
        margin: game.scores[seat] - game.scores[1 - seat],
        score: game.scores[seat],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        second_worker_turn,
        third_worker_turn,
    }
}

const PARTIAL_HORIZONS: [usize; 7] = [20, 40, 80, 120, 160, 200, 240];

#[derive(Clone)]
struct PartialBranchResult {
    margins: [i32; PARTIAL_HORIZONS.len()],
    liquid_values: [i32; PARTIAL_HORIZONS.len()],
}

fn carried_score(game: &GameState, player: usize) -> i32 {
    game.units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .map(|unit| {
            unit.carry[0] + unit.carry[1] + unit.carry[2] + unit.carry[3] + 4 * unit.carry[5]
        })
        .sum()
}

fn liquid_margin(game: &GameState, seat: usize) -> i32 {
    game.scores[seat] - game.scores[1 - seat] + carried_score(game, seat)
        - carried_score(game, 1 - seat)
}

fn partial_rollout(
    prefix: &Prefix,
    seat: usize,
    model: usize,
    three_worker: bool,
) -> PartialBranchResult {
    let mut game = prefix.root.clone();
    let mut resident = warmed_resident(prefix, seat);
    let alternative = NorxondorThreeWorkerSilver::new();
    let opposition = warmed_model(prefix, seat, model);
    let mut turns_until_end = 0;
    let mut margins = [0; PARTIAL_HORIZONS.len()];
    let mut liquid_values = [0; PARTIAL_HORIZONS.len()];
    let mut completed = 0;
    for depth in 1..=PARTIAL_HORIZONS[PARTIAL_HORIZONS.len() - 1] {
        let ours = if three_worker {
            alternative.decide(&game, seat)
        } else {
            resident.commands(&yamo_view(&game, seat))
        };
        let theirs = opposition.decide(&game, 1 - seat);
        apply_commands(&mut game, seat, &ours, &theirs);
        if completed < PARTIAL_HORIZONS.len() && depth == PARTIAL_HORIZONS[completed] {
            margins[completed] = game.scores[seat] - game.scores[1 - seat];
            liquid_values[completed] = liquid_margin(&game, seat);
            completed += 1;
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    while completed < PARTIAL_HORIZONS.len() {
        margins[completed] = game.scores[seat] - game.scores[1 - seat];
        liquid_values[completed] = liquid_margin(&game, seat);
        completed += 1;
    }
    PartialBranchResult {
        margins,
        liquid_values,
    }
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
    actual_model: usize,
    decision_turn: i32,
}

struct ModelResult {
    model: usize,
    mismatch: i64,
    exact_prefix_transitions: usize,
    resident: BranchResult,
    three_worker: BranchResult,
}

struct ScenarioResult {
    task: Task,
    root_opponent_workers: usize,
    root_opponent_ms: i32,
    root_opponent_cc: i32,
    root_opponent_hp: i32,
    root_opponent_chop: i32,
    serial_prediction_us: u128,
    models: Vec<ModelResult>,
}

fn run_task(task: Task) -> ScenarioResult {
    let prefix = resident_prefix(task.seed, task.seat, task.actual_model, task.decision_turn);
    let mut opponent_units: Vec<_> = prefix
        .root
        .units
        .iter()
        .filter(|unit| unit.player as usize == 1 - task.seat)
        .collect();
    opponent_units.sort_by_key(|unit| unit.id);
    let newest = opponent_units.last().copied();
    let started = Instant::now();
    let models = (0..MODELS.len())
        .map(|model| {
            let (mismatch, exact_prefix_transitions) = compatibility(&prefix, task.seat, model);
            ModelResult {
                model,
                mismatch,
                exact_prefix_transitions,
                resident: rollout(&prefix, task.seat, model, false),
                three_worker: rollout(&prefix, task.seat, model, true),
            }
        })
        .collect();
    ScenarioResult {
        task,
        root_opponent_workers: opponent_units.len(),
        root_opponent_ms: newest.map_or(-1, |unit| unit.ms),
        root_opponent_cc: newest.map_or(-1, |unit| unit.cc),
        root_opponent_hp: newest.map_or(-1, |unit| unit.hp),
        root_opponent_chop: newest.map_or(-1, |unit| unit.chop),
        serial_prediction_us: started.elapsed().as_micros(),
        models,
    }
}

fn parse_turns(value: &str) -> Vec<i32> {
    let turns: BTreeSet<_> = value
        .split(',')
        .map(|field| field.parse::<i32>().expect("numeric decision turn"))
        .collect();
    assert!(turns.iter().all(|turn| (2..=100).contains(turn)));
    turns.into_iter().collect()
}

fn terminal_mode(args: &[String]) {
    let seeds = args
        .get(1)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(10);
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "norxondor-shared-state.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or_else(|| thread::available_parallelism().map_or(1, usize::from))
        .max(1);
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(300);
    let decision_turns = parse_turns(args.get(5).map_or("3,5,10", String::as_str));

    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            decision_turns
                .iter()
                .copied()
                .flat_map(move |decision_turn| {
                    (0..MODELS.len()).flat_map(move |actual_model| {
                        (0..2).map(move |seat| Task {
                            seed,
                            seat,
                            actual_model,
                            decision_turn,
                        })
                    })
                })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut scenarios = thread::scope(|scope| {
        let mut handles = Vec::new();
        for _ in 0..threads {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            handles.push(scope.spawn(move || {
                let mut local = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    local.push(run_task(tasks[index]));
                }
                local
            }));
        }
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("shared-state worker"))
            .collect::<Vec<_>>()
    });
    scenarios.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.decision_turn,
            row.task.actual_model,
            row.task.seat,
        )
    });

    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(
        writer,
        "seed\tseat\tdecision_turn\tactual_opponent\troot_opponent_workers\troot_opponent_ms\troot_opponent_cc\troot_opponent_hp\troot_opponent_chop\tmodel\tprefix_mismatch\texact_prefix_transitions\tprefix_transitions\tresident_margin\tthree_worker_margin\tmargin_delta\tresident_score\tthree_worker_score\tscore_delta\tresident_workers\tthree_worker_workers\tserial_prediction_us"
    )
    .expect("write header");
    for scenario in scenarios {
        for row in scenario.models {
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                scenario.task.seed,
                scenario.task.seat,
                scenario.task.decision_turn,
                MODELS[scenario.task.actual_model].0,
                scenario.root_opponent_workers,
                scenario.root_opponent_ms,
                scenario.root_opponent_cc,
                scenario.root_opponent_hp,
                scenario.root_opponent_chop,
                MODELS[row.model].0,
                row.mismatch,
                row.exact_prefix_transitions,
                scenario.task.decision_turn - 1,
                row.resident.margin,
                row.three_worker.margin,
                row.three_worker.margin - row.resident.margin,
                row.resident.score,
                row.three_worker.score,
                row.three_worker.score - row.resident.score,
                row.resident.workers,
                row.three_worker.workers,
                scenario.serial_prediction_us,
            )
            .expect("write row");
        }
    }
    eprintln!(
        "saved {} scenarios x {} models using {} threads to {}",
        tasks.len(),
        MODELS.len(),
        threads,
        output
    );
}

struct PartialModelResult {
    model: usize,
    mismatch: i64,
    exact_prefix_transitions: usize,
    resident: PartialBranchResult,
    three_worker: PartialBranchResult,
}

struct PartialScenarioResult {
    task: Task,
    serial_prediction_us: u128,
    compatible_count: usize,
    models: Vec<PartialModelResult>,
}

fn run_partial_task(task: Task) -> PartialScenarioResult {
    let prefix = resident_prefix(task.seed, task.seat, task.actual_model, task.decision_turn);
    let compatibility_rows: Vec<_> = (0..MODELS.len())
        .map(|model| {
            let (mismatch, exact) = compatibility(&prefix, task.seat, model);
            (model, mismatch, exact)
        })
        .collect();
    let maximum_exact = compatibility_rows
        .iter()
        .map(|row| row.2)
        .max()
        .expect("model set");
    let started = Instant::now();
    let models: Vec<_> = compatibility_rows
        .into_iter()
        .filter(|row| row.2 == maximum_exact)
        .map(
            |(model, mismatch, exact_prefix_transitions)| PartialModelResult {
                model,
                mismatch,
                exact_prefix_transitions,
                resident: partial_rollout(&prefix, task.seat, model, false),
                three_worker: partial_rollout(&prefix, task.seat, model, true),
            },
        )
        .collect();
    PartialScenarioResult {
        task,
        serial_prediction_us: started.elapsed().as_micros(),
        compatible_count: models.len(),
        models,
    }
}

struct ProfileResult {
    task: Task,
    compatible_count: usize,
    maximum_exact_prefix_transitions: usize,
    compatibility_us: u128,
    parallel_rollout_us: u128,
    total_prediction_us: u128,
    branch_elapsed_sum_us: u128,
    slowest_branch_us: u128,
    predicted_liquid_delta: f64,
    selected: bool,
}

fn median(values: &mut [i32]) -> f64 {
    values.sort_unstable();
    let midpoint = values.len() / 2;
    if values.len() % 2 == 0 {
        f64::from(values[midpoint - 1] + values[midpoint]) / 2.0
    } else {
        f64::from(values[midpoint])
    }
}

fn run_profile_task(task: Task) -> ProfileResult {
    let prefix = resident_prefix(task.seed, task.seat, task.actual_model, task.decision_turn);
    let prediction_started = Instant::now();
    let compatibility_rows: Vec<_> = (0..MODELS.len())
        .map(|model| {
            let (mismatch, exact) = compatibility(&prefix, task.seat, model);
            (model, mismatch, exact)
        })
        .collect();
    let maximum_exact = compatibility_rows
        .iter()
        .map(|row| row.2)
        .max()
        .expect("model set");
    let compatible_models: Vec<_> = compatibility_rows
        .into_iter()
        .filter(|row| row.2 == maximum_exact)
        .map(|row| row.0)
        .collect();
    let compatibility_us = prediction_started.elapsed().as_micros();

    let rollout_started = Instant::now();
    let branch_results = thread::scope(|scope| {
        let mut handles = Vec::new();
        for &model in &compatible_models {
            for three_worker in [false, true] {
                let prefix = &prefix;
                handles.push(scope.spawn(move || {
                    let started = Instant::now();
                    let result = partial_rollout(prefix, task.seat, model, three_worker);
                    (model, three_worker, result, started.elapsed().as_micros())
                }));
            }
        }
        handles
            .into_iter()
            .map(|handle| handle.join().expect("profile rollout worker"))
            .collect::<Vec<_>>()
    });
    let parallel_rollout_us = rollout_started.elapsed().as_micros();
    let branch_elapsed_sum_us = branch_results.iter().map(|row| row.3).sum();
    let slowest_branch_us = branch_results.iter().map(|row| row.3).max().unwrap_or(0);

    let mut resident_values = BTreeMap::new();
    let mut alternative_values = BTreeMap::new();
    for (model, three_worker, result, _) in branch_results {
        let value = result.liquid_values[PARTIAL_HORIZONS.len() - 1];
        if three_worker {
            alternative_values.insert(model, value);
        } else {
            resident_values.insert(model, value);
        }
    }
    let mut deltas: Vec<_> = compatible_models
        .iter()
        .map(|model| alternative_values[model] - resident_values[model])
        .collect();
    let predicted_liquid_delta = median(&mut deltas);
    let total_prediction_us = prediction_started.elapsed().as_micros();
    ProfileResult {
        task,
        compatible_count: compatible_models.len(),
        maximum_exact_prefix_transitions: maximum_exact,
        compatibility_us,
        parallel_rollout_us,
        total_prediction_us,
        branch_elapsed_sum_us,
        slowest_branch_us,
        predicted_liquid_delta,
        selected: predicted_liquid_delta > 20.0,
    }
}

fn profile_mode(args: &[String]) {
    let seeds = args
        .get(2)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(5);
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "norxondor-parallel-profile.tsv".to_string());
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(302);
    let decision_turn = args
        .get(5)
        .and_then(|value| value.parse::<i32>().ok())
        .unwrap_or(3);
    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            (0..MODELS.len()).flat_map(move |actual_model| {
                (0..2).map(move |seat| Task {
                    seed,
                    seat,
                    actual_model,
                    decision_turn,
                })
            })
        })
        .collect();
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(
        writer,
        "seed\tseat\tdecision_turn\tactual_opponent\tcompatible_count\tmaximum_exact_prefix_transitions\tcompatibility_us\tparallel_rollout_us\ttotal_prediction_us\tbranch_elapsed_sum_us\tslowest_branch_us\tpredicted_liquid_delta\tselected"
    )
    .expect("write profile header");
    for (index, task) in tasks.iter().copied().enumerate() {
        let row = run_profile_task(task);
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.1}\t{}",
            row.task.seed,
            row.task.seat,
            row.task.decision_turn,
            MODELS[row.task.actual_model].0,
            row.compatible_count,
            row.maximum_exact_prefix_transitions,
            row.compatibility_us,
            row.parallel_rollout_us,
            row.total_prediction_us,
            row.branch_elapsed_sum_us,
            row.slowest_branch_us,
            row.predicted_liquid_delta,
            usize::from(row.selected),
        )
        .expect("write profile row");
        if (index + 1) % 16 == 0 {
            eprintln!("profiled {}/{} scenarios", index + 1, tasks.len());
        }
    }
    eprintln!("saved {} profile scenarios to {}", tasks.len(), output);
}

const TRAJECTORY_UNIT_SLOTS: usize = 3;
const RESOURCE_NAMES: [&str; 6] = ["plum", "lemon", "apple", "banana", "iron", "wood"];

fn snapshot_feature_names(snapshot: usize) -> Vec<String> {
    let prefix = format!("s{snapshot}");
    let mut names = vec![
        format!("{prefix}_turn"),
        format!("{prefix}_own_score"),
        format!("{prefix}_opp_score"),
        format!("{prefix}_next_id"),
        format!("{prefix}_own_units"),
        format!("{prefix}_opp_units"),
    ];
    for perspective in ["own", "opp"] {
        for resource in RESOURCE_NAMES {
            names.push(format!("{prefix}_{perspective}_inventory_{resource}"));
        }
        for resource in RESOURCE_NAMES {
            names.push(format!("{prefix}_{perspective}_carried_{resource}"));
        }
    }
    for perspective in ["own", "opp"] {
        for slot in 0..TRAJECTORY_UNIT_SLOTS {
            for field in [
                "present",
                "x_from_own_shack",
                "y_from_own_shack",
                "distance_to_own_shack",
                "distance_to_opp_shack",
                "ms",
                "cc",
                "hp",
                "chop",
                "carry_total",
                "carry_plum",
                "carry_lemon",
                "carry_apple",
                "carry_banana",
                "carry_iron",
                "carry_wood",
            ] {
                names.push(format!("{prefix}_{perspective}_u{slot}_{field}"));
            }
        }
    }
    names
}

fn snapshot_features(game: &GameState, seat: usize) -> Vec<i32> {
    let opponent = 1 - seat;
    let mut values = vec![
        game.turn,
        game.scores[seat],
        game.scores[opponent],
        game.next_id,
        game.units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count() as i32,
        game.units
            .iter()
            .filter(|unit| unit.player as usize == opponent)
            .count() as i32,
    ];
    for player in [seat, opponent] {
        values.extend(game.inventories[player]);
        for resource in 0..RESOURCE_NAMES.len() {
            values.push(
                game.units
                    .iter()
                    .filter(|unit| unit.player as usize == player)
                    .map(|unit| unit.carry[resource])
                    .sum(),
            );
        }
    }
    for player in [seat, opponent] {
        let mut units: Vec<_> = game
            .units
            .iter()
            .filter(|unit| unit.player as usize == player)
            .collect();
        units.sort_by_key(|unit| unit.id);
        for slot in 0..TRAJECTORY_UNIT_SLOTS {
            if let Some(unit) = units.get(slot) {
                let own_shack = game.shacks[seat];
                let opp_shack = game.shacks[opponent];
                values.extend([
                    1,
                    unit.x - own_shack.0,
                    unit.y - own_shack.1,
                    (unit.x - own_shack.0).abs() + (unit.y - own_shack.1).abs(),
                    (unit.x - opp_shack.0).abs() + (unit.y - opp_shack.1).abs(),
                    unit.ms,
                    unit.cc,
                    unit.hp,
                    unit.chop,
                    unit.total(),
                ]);
                values.extend(unit.carry);
            } else {
                values.extend([0, -99, -99, 99, 99, -1, -1, -1, -1, 0]);
                values.extend([0; RESOURCE_NAMES.len()]);
            }
        }
    }
    values
}

struct LabelResult {
    task: Task,
    trajectory: Vec<i32>,
    resident: BranchResult,
    three_worker: BranchResult,
    branch_elapsed_us: u128,
}

fn run_label_task(task: Task, resident_continuation: bool) -> LabelResult {
    let prefix = resident_prefix(task.seed, task.seat, task.actual_model, task.decision_turn);
    let mut trajectory = Vec::new();
    for state in prefix.states.iter().chain(std::iter::once(&prefix.root)) {
        trajectory.extend(snapshot_features(state, task.seat));
    }
    let started = Instant::now();
    let resident = rollout(&prefix, task.seat, task.actual_model, false);
    let three_worker = if resident_continuation {
        rollout_resident_three_worker(&prefix, task.seat, task.actual_model)
    } else {
        rollout(&prefix, task.seat, task.actual_model, true)
    };
    LabelResult {
        task,
        trajectory,
        resident,
        three_worker,
        branch_elapsed_us: started.elapsed().as_micros(),
    }
}

fn labels_mode(args: &[String], resident_continuation: bool) {
    let seeds = args
        .get(2)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(40);
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "norxondor-value-labels.tsv".to_string());
    let threads = args
        .get(4)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or_else(|| thread::available_parallelism().map_or(1, usize::from))
        .max(1);
    let seed_start = args
        .get(5)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(322);
    let decision_turn = args
        .get(6)
        .and_then(|value| value.parse::<i32>().ok())
        .unwrap_or(3);
    assert!(
        (3..=10).contains(&decision_turn),
        "trajectory schema supports decision turns three through ten"
    );
    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            (0..MODELS.len()).flat_map(move |actual_model| {
                (0..2).map(move |seat| Task {
                    seed,
                    seat,
                    actual_model,
                    decision_turn,
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = thread::scope(|scope| {
        let mut handles = Vec::new();
        for _ in 0..threads {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            handles.push(scope.spawn(move || {
                let mut local = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    local.push(run_label_task(tasks[index], resident_continuation));
                }
                local
            }));
        }
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("label worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| (row.task.seed, row.task.actual_model, row.task.seat));

    let feature_names: Vec<_> = (0..decision_turn as usize)
        .flat_map(snapshot_feature_names)
        .collect();
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    write!(writer, "seed\tseat\tdecision_turn\tactual_opponent").expect("write label header");
    for name in &feature_names {
        write!(writer, "\t{name}").expect("write feature header");
    }
    writeln!(
        writer,
        "\tresident_margin\tthree_worker_margin\tmargin_delta\tresident_score\tthree_worker_score\tscore_delta\tresident_workers\tthree_worker_workers\tbranch_elapsed_us"
    )
    .expect("finish label header");
    for row in rows {
        assert_eq!(row.trajectory.len(), feature_names.len());
        write!(
            writer,
            "{}\t{}\t{}\t{}",
            row.task.seed, row.task.seat, row.task.decision_turn, MODELS[row.task.actual_model].0,
        )
        .expect("write label prefix");
        for value in row.trajectory {
            write!(writer, "\t{value}").expect("write trajectory feature");
        }
        writeln!(
            writer,
            "\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.resident.margin,
            row.three_worker.margin,
            row.three_worker.margin - row.resident.margin,
            row.resident.score,
            row.three_worker.score,
            row.three_worker.score - row.resident.score,
            row.resident.workers,
            row.three_worker.workers,
            row.branch_elapsed_us,
        )
        .expect("write label outcome");
    }
    eprintln!(
        "saved {} {} label scenarios x {} trajectory features using {} threads to {}",
        tasks.len(),
        if resident_continuation {
            "resident-continuation"
        } else {
            "silver-continuation"
        },
        feature_names.len(),
        threads,
        output
    );
}

struct RoleSweepResult {
    task: Task,
    resident: BranchResult,
    roles: Vec<BranchResult>,
    elapsed_us: u128,
}

fn run_role_sweep_task(task: Task) -> RoleSweepResult {
    let prefix = resident_prefix(task.seed, task.seat, task.actual_model, task.decision_turn);
    let started = Instant::now();
    let resident = rollout(&prefix, task.seat, task.actual_model, false);
    let roles = ROLE_POLICIES
        .iter()
        .map(|(_, controller, mask)| {
            rollout_resident_role(&prefix, task.seat, task.actual_model, *controller, *mask)
        })
        .collect();
    RoleSweepResult {
        task,
        resident,
        roles,
        elapsed_us: started.elapsed().as_micros(),
    }
}

fn role_sweep_mode(args: &[String]) {
    let seeds = args
        .get(2)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(20);
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "norxondor-resident-role-sweep.tsv".to_string());
    let threads = args
        .get(4)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or_else(|| thread::available_parallelism().map_or(1, usize::from))
        .max(1);
    let seed_start = args
        .get(5)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(322);
    let decision_turn = args
        .get(6)
        .and_then(|value| value.parse::<i32>().ok())
        .unwrap_or(3);
    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            (0..MODELS.len()).flat_map(move |actual_model| {
                (0..2).map(move |seat| Task {
                    seed,
                    seat,
                    actual_model,
                    decision_turn,
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = thread::scope(|scope| {
        let mut handles = Vec::new();
        for _ in 0..threads {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            handles.push(scope.spawn(move || {
                let mut local = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    local.push(run_role_sweep_task(tasks[index]));
                }
                local
            }));
        }
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("role sweep worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| (row.task.seed, row.task.actual_model, row.task.seat));
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(
        writer,
        "seed\tseat\tdecision_turn\tactual_opponent\tpolicy\tresident_margin\tpolicy_margin\tmargin_delta\tresident_score\tpolicy_score\tscore_delta\tresident_workers\tpolicy_workers\tresident_second_worker_turn\tpolicy_second_worker_turn\tresident_third_worker_turn\tpolicy_third_worker_turn\tscenario_elapsed_us"
    )
    .expect("write role sweep header");
    for row in rows {
        for (index, result) in row.roles.into_iter().enumerate() {
            writeln!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                row.task.seed,
                row.task.seat,
                row.task.decision_turn,
                MODELS[row.task.actual_model].0,
                ROLE_POLICIES[index].0,
                row.resident.margin,
                result.margin,
                result.margin - row.resident.margin,
                row.resident.score,
                result.score,
                result.score - row.resident.score,
                row.resident.workers,
                result.workers,
                row.resident.second_worker_turn,
                result.second_worker_turn,
                row.resident.third_worker_turn,
                result.third_worker_turn,
                row.elapsed_us,
            )
            .expect("write role sweep row");
        }
    }
    eprintln!(
        "saved {} scenarios x {} resident role policies using {} threads to {}",
        tasks.len(),
        ROLE_POLICIES.len(),
        threads,
        output
    );
}

struct FundingSweepResult {
    task: Task,
    resident: BranchResult,
    branches: Vec<(BranchResult, BranchResult)>,
    elapsed_us: u128,
}

fn run_funding_sweep_task(task: Task) -> FundingSweepResult {
    let prefix = resident_prefix(task.seed, task.seat, task.actual_model, task.decision_turn);
    let started = Instant::now();
    let resident = rollout(&prefix, task.seat, task.actual_model, false);
    let branches = FUNDING_PROFILES
        .iter()
        .map(|(_, profile)| {
            (
                rollout_resident_three_worker_with_profile(
                    &prefix,
                    task.seat,
                    task.actual_model,
                    *profile,
                ),
                rollout_resident_role_with_profile(
                    &prefix,
                    task.seat,
                    task.actual_model,
                    RoleController::CompactStarterEnemyValueExtras,
                    RoleMask::All,
                    *profile,
                ),
            )
        })
        .collect();
    FundingSweepResult {
        task,
        resident,
        branches,
        elapsed_us: started.elapsed().as_micros(),
    }
}

fn funding_sweep_mode(args: &[String]) {
    let seeds = args
        .get(2)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(5);
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "norxondor-resident-funding-sweep.tsv".to_string());
    let threads = args
        .get(4)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or_else(|| thread::available_parallelism().map_or(1, usize::from))
        .max(1);
    let seed_start = args
        .get(5)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(322);
    let decision_turn = args
        .get(6)
        .and_then(|value| value.parse::<i32>().ok())
        .unwrap_or(3);
    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            (0..MODELS.len()).flat_map(move |actual_model| {
                (0..2).map(move |seat| Task {
                    seed,
                    seat,
                    actual_model,
                    decision_turn,
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = thread::scope(|scope| {
        let mut handles = Vec::new();
        for _ in 0..threads {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            handles.push(scope.spawn(move || {
                let mut local = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    local.push(run_funding_sweep_task(tasks[index]));
                }
                local
            }));
        }
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("funding sweep worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| (row.task.seed, row.task.actual_model, row.task.seat));
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(
        writer,
        "seed\tseat\tdecision_turn\tactual_opponent\tpolicy\tresident_margin\tpolicy_margin\tmargin_delta\tresident_score\tpolicy_score\tscore_delta\tresident_workers\tpolicy_workers\tresident_second_worker_turn\tpolicy_second_worker_turn\tresident_third_worker_turn\tpolicy_third_worker_turn\tscenario_elapsed_us"
    )
    .expect("write funding sweep header");
    for row in rows {
        for (index, (plain, repaired)) in row.branches.into_iter().enumerate() {
            for (continuation, result) in
                [("resident_continuation", plain), ("role_repair", repaired)]
            {
                writeln!(
                    writer,
                    "{}\t{}\t{}\t{}\t{}__{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                    row.task.seed,
                    row.task.seat,
                    row.task.decision_turn,
                    MODELS[row.task.actual_model].0,
                    FUNDING_PROFILES[index].0,
                    continuation,
                    row.resident.margin,
                    result.margin,
                    result.margin - row.resident.margin,
                    row.resident.score,
                    result.score,
                    result.score - row.resident.score,
                    row.resident.workers,
                    result.workers,
                    row.resident.second_worker_turn,
                    result.second_worker_turn,
                    row.resident.third_worker_turn,
                    result.third_worker_turn,
                    row.elapsed_us,
                )
                .expect("write funding sweep row");
            }
        }
    }
    eprintln!(
        "saved {} scenarios x {} funding policies using {} threads to {}",
        tasks.len(),
        FUNDING_PROFILES.len() * 2,
        threads,
        output
    );
}

fn partial_mode(args: &[String]) {
    let seeds = args
        .get(2)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(10);
    let output = args
        .get(3)
        .cloned()
        .unwrap_or_else(|| "norxondor-partial-state.tsv".to_string());
    let threads = args
        .get(4)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or_else(|| thread::available_parallelism().map_or(1, usize::from))
        .max(1);
    let seed_start = args
        .get(5)
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(302);
    let decision_turn = args
        .get(6)
        .and_then(|value| value.parse::<i32>().ok())
        .unwrap_or(3);
    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            (0..MODELS.len()).flat_map(move |actual_model| {
                (0..2).map(move |seat| Task {
                    seed,
                    seat,
                    actual_model,
                    decision_turn,
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut scenarios = thread::scope(|scope| {
        let mut handles = Vec::new();
        for _ in 0..threads {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            handles.push(scope.spawn(move || {
                let mut local = Vec::new();
                loop {
                    let index = next.fetch_add(1, Ordering::Relaxed);
                    if index >= tasks.len() {
                        break;
                    }
                    local.push(run_partial_task(tasks[index]));
                }
                local
            }));
        }
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("partial shared-state worker"))
            .collect::<Vec<_>>()
    });
    scenarios.sort_by_key(|row| (row.task.seed, row.task.actual_model, row.task.seat));
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    write!(
        writer,
        "seed\tseat\tdecision_turn\tactual_opponent\tmodel\tprefix_mismatch\texact_prefix_transitions\tcompatible_count\tserial_prediction_us"
    )
    .expect("write header prefix");
    for horizon in PARTIAL_HORIZONS {
        write!(
            writer,
            "\tresident_margin_h{horizon}\tthree_worker_margin_h{horizon}\tmargin_delta_h{horizon}\tresident_liquid_h{horizon}\tthree_worker_liquid_h{horizon}\tliquid_delta_h{horizon}"
        )
        .expect("write horizon header");
    }
    writeln!(writer).expect("finish header");
    for scenario in scenarios {
        for row in scenario.models {
            write!(
                writer,
                "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
                scenario.task.seed,
                scenario.task.seat,
                scenario.task.decision_turn,
                MODELS[scenario.task.actual_model].0,
                MODELS[row.model].0,
                row.mismatch,
                row.exact_prefix_transitions,
                scenario.compatible_count,
                scenario.serial_prediction_us,
            )
            .expect("write row prefix");
            for index in 0..PARTIAL_HORIZONS.len() {
                write!(
                    writer,
                    "\t{}\t{}\t{}\t{}\t{}\t{}",
                    row.resident.margins[index],
                    row.three_worker.margins[index],
                    row.three_worker.margins[index] - row.resident.margins[index],
                    row.resident.liquid_values[index],
                    row.three_worker.liquid_values[index],
                    row.three_worker.liquid_values[index] - row.resident.liquid_values[index],
                )
                .expect("write horizon row");
            }
            writeln!(writer).expect("finish row");
        }
    }
    eprintln!(
        "saved {} partial scenarios using {} threads to {}",
        tasks.len(),
        threads,
        output
    );
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("partial") => partial_mode(&args),
        Some("profile") => profile_mode(&args),
        Some("labels") => labels_mode(&args, false),
        Some("resident-labels") => labels_mode(&args, true),
        Some("resident-role-sweep") => role_sweep_mode(&args),
        Some("resident-funding-sweep") => funding_sweep_mode(&args),
        _ => terminal_mode(&args),
    }
}

#[cfg(test)]
mod tests {
    use super::{
        command_unit_id, liquid_margin, median, observable_distance, parse_turns, resident_prefix,
    };

    #[test]
    fn turn_parser_sorts_and_deduplicates() {
        assert_eq!(parse_turns("10,3,5,3"), vec![3, 5, 10]);
    }

    #[test]
    fn identical_states_have_zero_observable_distance() {
        let prefix = resident_prefix(0, 0, 0, 3);
        assert_eq!(observable_distance(&prefix.root, &prefix.root.clone()), 0);
        assert_eq!(prefix.states.len(), 2);
    }

    #[test]
    fn liquid_margin_equals_score_when_nobody_carries() {
        let prefix = resident_prefix(0, 0, 0, 3);
        let expected = prefix.root.scores[0] - prefix.root.scores[1];
        assert_eq!(liquid_margin(&prefix.root, 0), expected);
    }

    #[test]
    fn median_handles_even_and_odd_model_sets() {
        assert_eq!(median(&mut [1, 9, 5]), 5.0);
        assert_eq!(median(&mut [9, 1, 5, 3]), 4.0);
    }

    #[test]
    fn trajectory_feature_names_match_values() {
        let prefix = resident_prefix(0, 1, 0, 3);
        for (index, state) in prefix
            .states
            .iter()
            .chain(std::iter::once(&prefix.root))
            .enumerate()
        {
            let names = super::snapshot_feature_names(index);
            let values = super::snapshot_features(state, 1);
            assert_eq!(names.len(), values.len());
            assert_eq!(names.len(), 126);
        }
    }

    #[test]
    fn role_command_parser_ignores_train_and_messages() {
        assert_eq!(command_unit_id("MOVE 7 3 4"), Some(7));
        assert_eq!(command_unit_id("TRAIN 2 2 1 1"), None);
        assert_eq!(command_unit_id("MSG hello"), None);
    }
}
