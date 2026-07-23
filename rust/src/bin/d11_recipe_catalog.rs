//! Exact-engine full-game catalog for the eight fixed D11 worker recipes.
//!
//! The D11 live binary is exercised through the referee protocol.  Every
//! seed/seat/opponent cell is repeated for each recipe, so recipe comparisons
//! remain paired even when absolute local-opponent strength is uncalibrated.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{BufRead, BufReader, Read, Write};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step, WOOD};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::GameState;
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot as YamoBot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const RECIPES: [(i32, i32, i32, i32); 8] = [
    (1, 1, 1, 1),
    (1, 2, 1, 1),
    (2, 2, 1, 1),
    (2, 2, 2, 1),
    (1, 3, 0, 1),
    (1, 2, 0, 2),
    (2, 2, 0, 2),
    (2, 3, 1, 2),
];
const BASELINE_RECIPE: usize = 6;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum LayerMode {
    ActorFull,
    ResidentFull,
    ResidentActions,
    ResidentStarterActorSecond,
    ResidentThenActorAll,
    NativeResidentStarterActorSecond,
    NativeActorAll,
    NativeActorStarterResidentSecond,
    NativeSecondIdleOnly,
    NativeSecondCropLocal,
    NativeSecondProductiveLocal,
    NativeStarterCropLocal,
    NativeAllProductiveLocal,
}

impl LayerMode {
    fn label(self) -> &'static str {
        match self {
            Self::ActorFull => "actor_full",
            Self::ResidentFull => "resident_full",
            Self::ResidentActions => "resident_actions",
            Self::ResidentStarterActorSecond => "resident_starter_actor_second",
            Self::ResidentThenActorAll => "resident_then_actor_all",
            Self::NativeResidentStarterActorSecond => "native_resident_starter_actor_second",
            Self::NativeActorAll => "native_actor_all",
            Self::NativeActorStarterResidentSecond => "native_actor_starter_resident_second",
            Self::NativeSecondIdleOnly => "native_second_idle_only",
            Self::NativeSecondCropLocal => "native_second_crop_local",
            Self::NativeSecondProductiveLocal => "native_second_productive_local",
            Self::NativeStarterCropLocal => "native_starter_crop_local",
            Self::NativeAllProductiveLocal => "native_all_productive_local",
        }
    }
}

#[derive(Clone, Debug)]
struct PolicyDefinition {
    label: String,
    recipe: usize,
    fallback_turn: usize,
    layer: LayerMode,
    adopt_worker: bool,
}

fn layer_policy(label: &str) -> Result<PolicyDefinition, String> {
    let (layer, recipe, adopt_worker) = match label {
        "resident" => (LayerMode::ResidentFull, 6, false),
        "resident_actions_train6" => (LayerMode::ResidentActions, 6, false),
        "resident_actions_train7" => (LayerMode::ResidentActions, 7, false),
        "resident_starter_actor_second_train6" => (LayerMode::ResidentStarterActorSecond, 6, false),
        "resident_starter_actor_second_train7" => (LayerMode::ResidentStarterActorSecond, 7, false),
        "resident_then_actor_all_train6" => (LayerMode::ResidentThenActorAll, 6, false),
        "resident_then_actor_all_train7" => (LayerMode::ResidentThenActorAll, 7, false),
        "native_resident_starter_actor_second" => {
            (LayerMode::NativeResidentStarterActorSecond, 6, true)
        }
        "native_actor_all" => (LayerMode::NativeActorAll, 6, true),
        "native_actor_starter_resident_second" => {
            (LayerMode::NativeActorStarterResidentSecond, 6, true)
        }
        "native_second_idle_only" => (LayerMode::NativeSecondIdleOnly, 6, true),
        "native_second_crop_local" => (LayerMode::NativeSecondCropLocal, 6, true),
        "native_second_productive_local" => (LayerMode::NativeSecondProductiveLocal, 6, true),
        "native_starter_crop_local" => (LayerMode::NativeStarterCropLocal, 6, true),
        "native_all_productive_local" => (LayerMode::NativeAllProductiveLocal, 6, true),
        _ => return Err(format!("unknown layer policy {label:?}")),
    };
    Ok(PolicyDefinition {
        label: label.to_string(),
        recipe,
        fallback_turn: 0,
        layer,
        adopt_worker,
    })
}

const DEFAULT_OPPONENTS: [&str; 6] = [
    "resident",
    "gold_adaptive",
    "compact_gold",
    "norx_native_three",
    "legend_balanced",
    "mybot",
];

struct ProcessBot {
    child: Child,
    input: Option<ChildStdin>,
    output: BufReader<ChildStdout>,
}

impl ProcessBot {
    fn spawn(
        path: &str,
        recipe: usize,
        fallback_turn: usize,
        adopt_worker: bool,
    ) -> Result<Self, String> {
        let mut command = Command::new(path);
        command.arg("--recipe").arg(recipe.to_string());
        if fallback_turn > 0 {
            command
                .arg("--fallback")
                .arg(BASELINE_RECIPE.to_string())
                .arg(fallback_turn.to_string());
        }
        if adopt_worker {
            command.arg("--adopt-worker");
        }
        let mut child = command
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|error| format!("cannot spawn {path}: {error}"))?;
        let input = child.stdin.take().ok_or("child stdin")?;
        let output = child.stdout.take().ok_or("child stdout")?;
        Ok(Self {
            child,
            input: Some(input),
            output: BufReader::new(output),
        })
    }

    fn send(&mut self, text: &str) -> Result<(), String> {
        let input = self.input.as_mut().ok_or("closed child stdin")?;
        input
            .write_all(text.as_bytes())
            .map_err(|error| format!("write child input: {error}"))?;
        input
            .flush()
            .map_err(|error| format!("flush child input: {error}"))
    }

    fn receive(&mut self) -> Result<String, String> {
        let mut line = String::new();
        let bytes = self
            .output
            .read_line(&mut line)
            .map_err(|error| format!("read child output: {error}"))?;
        if bytes == 0 {
            return Err("child EOF".to_string());
        }
        Ok(line.trim_end_matches(['\n', '\r']).to_string())
    }

    fn finish(mut self) -> Result<(), String> {
        drop(self.input.take());
        let status = self
            .child
            .wait()
            .map_err(|error| format!("wait child: {error}"))?;
        let mut stderr = String::new();
        self.child
            .stderr
            .take()
            .ok_or("child stderr")?
            .read_to_string(&mut stderr)
            .map_err(|error| format!("read child stderr: {error}"))?;
        if !status.success() || !stderr.is_empty() {
            return Err(format!("child status={status}, stderr={stderr:?}"));
        }
        Ok(())
    }
}

fn grid(game: &GameState, seat: usize) -> String {
    let rows: Vec<String> = (0..game.height)
        .map(|y| {
            (0..game.width)
                .map(|x| {
                    let cell = (x, y);
                    if cell == game.shacks[seat] {
                        '0'
                    } else if cell == game.shacks[1 - seat] {
                        '1'
                    } else if game.iron.contains(&cell) {
                        '+'
                    } else if game.water.contains(&cell) {
                        '~'
                    } else if game.walkable.contains(&cell) {
                        '.'
                    } else {
                        '#'
                    }
                })
                .collect()
        })
        .collect();
    format!("{} {}\n{}\n", game.width, game.height, rows.join("\n"))
}

fn turn_block(game: &GameState, seat: usize) -> String {
    let mut text = String::new();
    for player in [seat, 1 - seat] {
        let inv = game.inventories[player];
        text.push_str(&format!(
            "{} {} {} {} {} {}\n",
            inv[0], inv[1], inv[2], inv[3], inv[4], inv[5]
        ));
    }
    text.push_str(&format!("{}\n", game.plants.len()));
    for plant in &game.plants {
        text.push_str(&format!(
            "{} {} {} {} {} {} {}\n",
            plant.plant_type,
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown
        ));
    }
    text.push_str(&format!("{}\n", game.units.len()));
    for unit in &game.units {
        let relative_player = usize::from(unit.player as usize != seat);
        text.push_str(&format!(
            "{} {} {} {} {} {} {} {} {} {} {} {} {} {}\n",
            unit.id,
            relative_player,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
            unit.carry[0],
            unit.carry[1],
            unit.carry[2],
            unit.carry[3],
            unit.carry[4],
            unit.carry[5]
        ));
    }
    text
}

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

enum Opponent {
    Resident(SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Opponent {
    fn instantiate(label: &str) -> Result<Self, String> {
        let opponent = match label {
            "resident" => Self::Resident(SecureOrchardBot::new()),
            "gold_adaptive" => Self::Local(Box::new(GoldElite::adaptive())),
            "gold_elite" => Self::Local(Box::new(GoldElite::new())),
            "compact_gold" => Self::Local(Box::new(CompactGold::new())),
            "sched_bot" => Self::Local(Box::new(SchedBot::new())),
            "mybot" => Self::Local(Box::new(MyBot::new())),
            "norx_native_three" => Self::Local(Box::new(NorxondorNative::new(true))),
            "norx_native_full" => Self::Local(Box::new(NorxondorNative::new(false))),
            "legend_balanced" => Self::Local(Box::new(LegendFieldProxyV2::configured(
                LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                },
            ))),
            "legend_hp2" => Self::Local(Box::new(LegendFieldProxyV2::configured(
                LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 2, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                },
            ))),
            _ => return Err(format!("unknown opponent {label:?}")),
        };
        Ok(opponent)
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => bot.commands(&yamo_view(game, player)),
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

#[derive(Clone, Debug)]
struct Task {
    seed: u64,
    seat: usize,
    opponent: String,
    recipe: usize,
    fallback_turn: usize,
    policy: String,
    layer: LayerMode,
    adopt_worker: bool,
    collect_decisions: bool,
}

#[derive(Debug)]
struct DecisionRow {
    turn: i32,
    unit_id: i32,
    ordinal: usize,
    worker_count: usize,
    opponent_workers: usize,
    x: i32,
    y: i32,
    ms: i32,
    cc: i32,
    hp: i32,
    chop: i32,
    free: i32,
    carry: [i32; 6],
    inventory: [i32; 6],
    score: i32,
    opponent_score: i32,
    plants: usize,
    local_plant_type: String,
    local_plant_health: i32,
    local_plant_fruits: i32,
    near_home: bool,
    near_iron: bool,
    resident_command: String,
    actor_command: String,
    resident_target: Option<(i32, i32)>,
    actor_target: Option<(i32, i32)>,
    previous_verb: String,
    previous_target: Option<(i32, i32)>,
    exact_persistent: bool,
    verb_persistent: bool,
    target_persistent: bool,
    intent_age: usize,
    other_verb: String,
    other_target: Option<(i32, i32)>,
    paired_target_collision: bool,
    poi_move_targets: usize,
    local_productive_actions: usize,
    residual_options: usize,
    resident_directly_decodable: bool,
    state_fingerprint: u64,
}

#[derive(Clone, Debug)]
struct PreviousCommand {
    command: String,
    verb: String,
    target: Option<(i32, i32)>,
    age: usize,
}

#[derive(Debug)]
struct ResultRow {
    seed: u64,
    seat: usize,
    opponent: String,
    recipe: usize,
    fallback_turn: usize,
    policy: String,
    layer: LayerMode,
    adopt_worker: bool,
    score: i32,
    opponent_score: i32,
    wood: i32,
    opponent_wood: i32,
    terminal_turn: i32,
    workers: usize,
    opponent_workers: usize,
    trained_ms: i32,
    trained_cc: i32,
    trained_hp: i32,
    trained_chop: i32,
    train_commands: usize,
    plant_commands: usize,
    harvest_commands: usize,
    chop_commands: usize,
    drop_commands: usize,
    move_commands: usize,
    shadow_decisions: usize,
    exact_agreements: usize,
    verb_agreements: usize,
    resident_wait_actor_action: usize,
    actor_local_resident_transit: usize,
    overrides: usize,
    elapsed_us: u128,
    decisions: Vec<DecisionRow>,
}

fn parse_commands(line: &str) -> Result<Vec<String>, String> {
    if line.is_empty() {
        return Err("empty command line".to_string());
    }
    Ok(line.split(';').map(str::to_string).collect())
}

fn count_commands(commands: &[String], counts: &mut [usize; 6]) -> Result<(), String> {
    for command in commands {
        let verb = command.split_whitespace().next().ok_or("empty command")?;
        match verb {
            "TRAIN" => counts[0] += 1,
            "PLANT" => counts[1] += 1,
            "HARVEST" => counts[2] += 1,
            "CHOP" => counts[3] += 1,
            "DROP" => counts[4] += 1,
            "MOVE" => counts[5] += 1,
            "PICK" | "MINE" | "WAIT" | "MSG" => {}
            _ => return Err(format!("unknown command {command:?}")),
        }
    }
    Ok(())
}

fn per_unit_actions(commands: &[String], own_ids: &[i32]) -> BTreeMap<i32, String> {
    let mut actions = BTreeMap::new();
    let mut waits = 0usize;
    for command in commands {
        let fields: Vec<_> = command.split_whitespace().collect();
        match fields.first().copied() {
            Some("WAIT") => waits += 1,
            Some("MOVE" | "HARVEST" | "CHOP" | "DROP" | "MINE" | "PLANT" | "PICK") => {
                if let Some(id) = fields.get(1).and_then(|value| value.parse::<i32>().ok()) {
                    actions.insert(id, command.clone());
                }
            }
            _ => {}
        }
    }
    for &id in own_ids {
        if waits == 0 {
            break;
        }
        if let std::collections::btree_map::Entry::Vacant(entry) = actions.entry(id) {
            entry.insert("WAIT".to_string());
            waits -= 1;
        }
    }
    actions
}

fn verb(command: &str) -> &str {
    command.split_whitespace().next().unwrap_or("WAIT")
}

fn command_target(command: &str, current: (i32, i32)) -> Option<(i32, i32)> {
    let fields: Vec<_> = command.split_whitespace().collect();
    match fields.first().copied() {
        Some("MOVE") => Some((
            fields.get(2)?.parse::<i32>().ok()?,
            fields.get(3)?.parse::<i32>().ok()?,
        )),
        Some("HARVEST" | "CHOP" | "DROP" | "MINE" | "PLANT" | "PICK") => Some(current),
        _ => None,
    }
}

fn item_index(value: &str) -> Option<usize> {
    match value {
        "PLUM" => Some(0),
        "LEMON" => Some(1),
        "APPLE" => Some(2),
        "BANANA" => Some(3),
        _ => None,
    }
}

fn point_of_interest_targets(
    game: &GameState,
    current: (i32, i32),
    resident_target: Option<(i32, i32)>,
) -> BTreeSet<(i32, i32)> {
    let mut targets = BTreeSet::from([current, game.shacks[0], game.shacks[1]]);
    targets.extend(game.plants.iter().map(|plant| plant.pos()));
    targets.extend(game.units.iter().map(|unit| unit.pos()));
    targets.extend(game.walkable.iter().copied().filter(|&(x, y)| {
        [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]
            .into_iter()
            .any(|cell| game.iron.contains(&cell))
    }));
    if let Some(target) = resident_target {
        targets.insert(target);
    }
    targets
}

fn local_productive_action_count(game: &GameState, player: usize, unit_id: i32) -> usize {
    let Some(unit) = game.units.iter().find(|unit| unit.id == unit_id) else {
        return 0;
    };
    let current = unit.pos();
    let plant = game.plants.iter().find(|plant| plant.pos() == current);
    let near_home =
        (current.0 - game.shacks[player].0).abs() + (current.1 - game.shacks[player].1).abs() <= 1;
    let near_iron = [
        (current.0, current.1 + 1),
        (current.0 + 1, current.1),
        (current.0, current.1 - 1),
        (current.0 - 1, current.1),
    ]
    .into_iter()
    .any(|cell| game.iron.contains(&cell));
    let mut count = 0usize;
    count +=
        usize::from(plant.is_some_and(|plant| plant.fruits > 0) && unit.hp > 0 && unit.free() > 0);
    count += usize::from(plant.is_some() && unit.chop > 0);
    count += usize::from(near_home && unit.total() > 0);
    count += usize::from(near_iron && unit.chop > 0 && unit.free() > 0);
    if game.walkable.contains(&current) && plant.is_none() {
        count += (0..4).filter(|&item| unit.carry[item] > 0).count();
    }
    if near_home && unit.free() > 0 {
        count += (0..4)
            .filter(|&item| game.inventories[player][item] > 0)
            .count();
    }
    count
}

fn resident_directly_decodable(
    game: &GameState,
    player: usize,
    unit_id: i32,
    command: &str,
    poi_targets: &BTreeSet<(i32, i32)>,
) -> bool {
    let Some(unit) = game.units.iter().find(|unit| unit.id == unit_id) else {
        return false;
    };
    let current = unit.pos();
    let plant = game.plants.iter().find(|plant| plant.pos() == current);
    let near_home =
        (current.0 - game.shacks[player].0).abs() + (current.1 - game.shacks[player].1).abs() <= 1;
    let near_iron = [
        (current.0, current.1 + 1),
        (current.0 + 1, current.1),
        (current.0, current.1 - 1),
        (current.0 - 1, current.1),
    ]
    .into_iter()
    .any(|cell| game.iron.contains(&cell));
    let fields: Vec<_> = command.split_whitespace().collect();
    match fields.first().copied().unwrap_or("WAIT") {
        "WAIT" => true,
        "MOVE" => {
            command_target(command, current).is_some_and(|target| poi_targets.contains(&target))
        }
        "HARVEST" => plant.is_some_and(|plant| plant.fruits > 0) && unit.hp > 0 && unit.free() > 0,
        "CHOP" => plant.is_some() && unit.chop > 0,
        "DROP" => near_home && unit.total() > 0,
        "MINE" => near_iron && unit.chop > 0 && unit.free() > 0,
        "PLANT" => fields
            .get(2)
            .and_then(|value| item_index(value))
            .is_some_and(|item| {
                game.walkable.contains(&current) && plant.is_none() && unit.carry[item] > 0
            }),
        "PICK" => fields
            .get(2)
            .and_then(|value| item_index(value))
            .is_some_and(|item| near_home && unit.free() > 0 && game.inventories[player][item] > 0),
        _ => false,
    }
}

fn fnv1a64(text: &str) -> u64 {
    text.as_bytes()
        .iter()
        .fold(0xcbf29ce484222325u64, |hash, byte| {
            (hash ^ u64::from(*byte)).wrapping_mul(0x100000001b3)
        })
}

fn trajectory_decisions(
    game: &GameState,
    seat: usize,
    actor_commands: &[String],
    resident_commands: &[String],
    previous: &mut BTreeMap<i32, PreviousCommand>,
) -> Vec<DecisionRow> {
    let mut own_units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == seat)
        .collect();
    own_units.sort_by_key(|unit| unit.id);
    let actor_actions = per_unit_actions(
        actor_commands,
        &own_units.iter().map(|unit| unit.id).collect::<Vec<_>>(),
    );
    let resident_actions = per_unit_actions(
        resident_commands,
        &own_units.iter().map(|unit| unit.id).collect::<Vec<_>>(),
    );
    let opponent_workers = game.units.len() - own_units.len();
    let fingerprint = fnv1a64(&turn_block(game, seat));
    let mut rows = Vec::with_capacity(own_units.len());
    for (ordinal, unit) in own_units.iter().enumerate() {
        let resident_command = resident_actions
            .get(&unit.id)
            .cloned()
            .unwrap_or_else(|| "WAIT".to_string());
        let actor_command = actor_actions
            .get(&unit.id)
            .cloned()
            .unwrap_or_else(|| "WAIT".to_string());
        let resident_target = command_target(&resident_command, unit.pos());
        let actor_target = command_target(&actor_command, unit.pos());
        let prior = previous.get(&unit.id).cloned();
        let resident_verb = verb(&resident_command).to_string();
        let exact_persistent = prior
            .as_ref()
            .is_some_and(|prior| prior.command == resident_command);
        let verb_persistent = prior
            .as_ref()
            .is_some_and(|prior| prior.verb == resident_verb);
        let target_persistent = resident_target.is_some()
            && prior
                .as_ref()
                .is_some_and(|prior| prior.target == resident_target);
        let intent_age = if exact_persistent {
            prior.as_ref().map_or(1, |prior| prior.age + 1)
        } else {
            1
        };
        let other = own_units.iter().find(|other| other.id != unit.id);
        let other_command = other
            .and_then(|other| resident_actions.get(&other.id))
            .map_or("WAIT", String::as_str);
        let other_target = other.and_then(|other| command_target(other_command, other.pos()));
        let paired_target_collision = resident_target.is_some() && resident_target == other_target;
        let poi_targets = point_of_interest_targets(game, unit.pos(), resident_target);
        let local_productive_actions = local_productive_action_count(game, seat, unit.id);
        let local_plant = game.plants.iter().find(|plant| plant.pos() == unit.pos());
        let near_home =
            (unit.x - game.shacks[seat].0).abs() + (unit.y - game.shacks[seat].1).abs() <= 1;
        let near_iron = [
            (unit.x, unit.y + 1),
            (unit.x + 1, unit.y),
            (unit.x, unit.y - 1),
            (unit.x - 1, unit.y),
        ]
        .into_iter()
        .any(|cell| game.iron.contains(&cell));
        rows.push(DecisionRow {
            turn: game.turn,
            unit_id: unit.id,
            ordinal,
            worker_count: own_units.len(),
            opponent_workers,
            x: unit.x,
            y: unit.y,
            ms: unit.ms,
            cc: unit.cc,
            hp: unit.hp,
            chop: unit.chop,
            free: unit.free(),
            carry: unit.carry,
            inventory: game.inventories[seat],
            score: game.scores[seat],
            opponent_score: game.scores[1 - seat],
            plants: game.plants.len(),
            local_plant_type: local_plant
                .map_or("-", |plant| plant.plant_type.as_str())
                .to_string(),
            local_plant_health: local_plant.map_or(-1, |plant| plant.health),
            local_plant_fruits: local_plant.map_or(-1, |plant| plant.fruits),
            near_home,
            near_iron,
            resident_command: resident_command.clone(),
            actor_command,
            resident_target,
            actor_target,
            previous_verb: prior
                .as_ref()
                .map_or("-", |prior| prior.verb.as_str())
                .to_string(),
            previous_target: prior.as_ref().and_then(|prior| prior.target),
            exact_persistent,
            verb_persistent,
            target_persistent,
            intent_age,
            other_verb: verb(other_command).to_string(),
            other_target,
            paired_target_collision,
            poi_move_targets: poi_targets.len(),
            local_productive_actions,
            residual_options: poi_targets.len() + local_productive_actions,
            resident_directly_decodable: resident_directly_decodable(
                game,
                seat,
                unit.id,
                &resident_command,
                &poi_targets,
            ),
            state_fingerprint: fingerprint,
        });
        previous.insert(
            unit.id,
            PreviousCommand {
                command: resident_command,
                verb: resident_verb,
                target: resident_target,
                age: intent_age,
            },
        );
    }
    rows
}

fn actor_opportunity(resident: &str, actor: &str, crop_only: bool) -> bool {
    if !matches!(verb(resident), "MOVE" | "WAIT") {
        return false;
    }
    if crop_only {
        matches!(verb(actor), "PLANT" | "HARVEST" | "CHOP")
    } else {
        matches!(
            verb(actor),
            "PLANT" | "HARVEST" | "CHOP" | "DROP" | "MINE" | "PICK"
        )
    }
}

fn merge_layer_commands(
    layer: LayerMode,
    game: &GameState,
    seat: usize,
    actor: &[String],
    resident: &[String],
) -> Vec<String> {
    match layer {
        LayerMode::ActorFull => return actor.to_vec(),
        LayerMode::ResidentFull => return resident.to_vec(),
        _ => {}
    }
    let mut own_ids: Vec<i32> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == seat)
        .map(|unit| unit.id)
        .collect();
    own_ids.sort_unstable();
    let built = own_ids.len() >= 2;
    if !built
        && matches!(
            layer,
            LayerMode::NativeResidentStarterActorSecond
                | LayerMode::NativeActorAll
                | LayerMode::NativeActorStarterResidentSecond
                | LayerMode::NativeSecondIdleOnly
                | LayerMode::NativeSecondCropLocal
                | LayerMode::NativeSecondProductiveLocal
                | LayerMode::NativeStarterCropLocal
                | LayerMode::NativeAllProductiveLocal
        )
    {
        return resident.to_vec();
    }
    let actor_actions = per_unit_actions(actor, &own_ids);
    let resident_actions = per_unit_actions(resident, &own_ids);
    let mut merged: Vec<String> = actor
        .iter()
        .filter(|command| command.starts_with("TRAIN "))
        .cloned()
        .collect();
    for (ordinal, id) in own_ids.into_iter().enumerate() {
        let action = match layer {
            LayerMode::ResidentActions => resident_actions.get(&id),
            LayerMode::ResidentStarterActorSecond => {
                if ordinal == 0 {
                    resident_actions.get(&id)
                } else {
                    actor_actions.get(&id)
                }
            }
            LayerMode::ResidentThenActorAll => {
                if built {
                    actor_actions.get(&id)
                } else {
                    resident_actions.get(&id)
                }
            }
            LayerMode::NativeResidentStarterActorSecond => {
                if ordinal == 0 {
                    resident_actions.get(&id)
                } else {
                    actor_actions.get(&id)
                }
            }
            LayerMode::NativeActorAll => actor_actions.get(&id),
            LayerMode::NativeActorStarterResidentSecond => {
                if ordinal == 0 {
                    actor_actions.get(&id)
                } else {
                    resident_actions.get(&id)
                }
            }
            LayerMode::NativeSecondIdleOnly => {
                let resident = resident_actions.get(&id);
                let actor = actor_actions.get(&id);
                if ordinal > 0
                    && resident.map_or(true, |command| verb(command) == "WAIT")
                    && actor.is_some_and(|command| verb(command) != "WAIT")
                {
                    actor
                } else {
                    resident
                }
            }
            LayerMode::NativeSecondCropLocal => {
                let resident = resident_actions.get(&id);
                let actor = actor_actions.get(&id);
                if ordinal > 0
                    && actor.is_some_and(|actor| {
                        actor_opportunity(resident.map_or("WAIT", String::as_str), actor, true)
                    })
                {
                    actor
                } else {
                    resident
                }
            }
            LayerMode::NativeSecondProductiveLocal => {
                let resident = resident_actions.get(&id);
                let actor = actor_actions.get(&id);
                if ordinal > 0
                    && actor.is_some_and(|actor| {
                        actor_opportunity(resident.map_or("WAIT", String::as_str), actor, false)
                    })
                {
                    actor
                } else {
                    resident
                }
            }
            LayerMode::NativeStarterCropLocal => {
                let resident = resident_actions.get(&id);
                let actor = actor_actions.get(&id);
                if ordinal == 0
                    && actor.is_some_and(|actor| {
                        actor_opportunity(resident.map_or("WAIT", String::as_str), actor, true)
                    })
                {
                    actor
                } else {
                    resident
                }
            }
            LayerMode::NativeAllProductiveLocal => {
                let resident = resident_actions.get(&id);
                let actor = actor_actions.get(&id);
                if actor.is_some_and(|actor| {
                    actor_opportunity(resident.map_or("WAIT", String::as_str), actor, false)
                }) {
                    actor
                } else {
                    resident
                }
            }
            LayerMode::ActorFull | LayerMode::ResidentFull => unreachable!(),
        };
        merged.push(action.cloned().unwrap_or_else(|| "WAIT".to_string()));
    }
    merged
}

fn shadow_metrics(
    game: &GameState,
    seat: usize,
    actor: &[String],
    resident: &[String],
    actual: &[String],
) -> [usize; 6] {
    let mut own_ids: Vec<i32> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == seat)
        .map(|unit| unit.id)
        .collect();
    own_ids.sort_unstable();
    if own_ids.len() < 2 {
        return [0; 6];
    }
    let actor_actions = per_unit_actions(actor, &own_ids);
    let resident_actions = per_unit_actions(resident, &own_ids);
    let actual_actions = per_unit_actions(actual, &own_ids);
    let mut metrics = [0usize; 6];
    for id in own_ids {
        let actor = actor_actions.get(&id).map_or("WAIT", String::as_str);
        let resident = resident_actions.get(&id).map_or("WAIT", String::as_str);
        let actual = actual_actions.get(&id).map_or("WAIT", String::as_str);
        metrics[0] += 1;
        metrics[1] += usize::from(actor == resident);
        metrics[2] += usize::from(verb(actor) == verb(resident));
        metrics[3] += usize::from(verb(resident) == "WAIT" && verb(actor) != "WAIT");
        metrics[4] += usize::from(actor_opportunity(resident, actor, false));
        metrics[5] += usize::from(actual != resident);
    }
    metrics
}

fn play(binary: &str, task: &Task) -> Result<ResultRow, String> {
    let started = Instant::now();
    let mut game = generate_bronze(task.seed);
    let mut actor = ProcessBot::spawn(binary, task.recipe, task.fallback_turn, task.adopt_worker)?;
    let mut opponent = Opponent::instantiate(&task.opponent)?;
    let mut resident_shadow = SecureOrchardBot::new();
    actor.send(&grid(&game, task.seat))?;
    let mut stall_counter = 0;
    let mut counts = [0usize; 6];
    let mut shadow = [0usize; 6];
    let mut previous_commands = BTreeMap::new();
    let mut decisions = Vec::new();
    while game.turn <= 300 {
        actor.send(&turn_block(&game, task.seat))?;
        let line = actor.receive()?;
        let actor_commands = parse_commands(&line)?;
        let resident_commands = if task.layer == LayerMode::ActorFull {
            Vec::new()
        } else {
            resident_shadow.commands(&yamo_view(&game, task.seat))
        };
        if task.collect_decisions && !resident_commands.is_empty() {
            decisions.extend(trajectory_decisions(
                &game,
                task.seat,
                &actor_commands,
                &resident_commands,
                &mut previous_commands,
            ));
        }
        let ours = merge_layer_commands(
            task.layer,
            &game,
            task.seat,
            &actor_commands,
            &resident_commands,
        );
        let turn_shadow =
            shadow_metrics(&game, task.seat, &actor_commands, &resident_commands, &ours);
        for index in 0..shadow.len() {
            shadow[index] += turn_shadow[index];
        }
        count_commands(&ours, &mut counts)?;
        let theirs = opponent.commands(&game, 1 - task.seat);
        if task.seat == 0 {
            step(&mut game, &ours, &theirs);
        } else {
            step(&mut game, &theirs, &ours);
        }
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }
    actor.finish()?;
    let mut own_units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == task.seat)
        .collect();
    own_units.sort_by_key(|unit| unit.id);
    let workers = own_units.len();
    let opponent_workers = game.units.len() - workers;
    let trained = own_units.get(1).copied();
    Ok(ResultRow {
        seed: task.seed,
        seat: task.seat,
        opponent: task.opponent.clone(),
        recipe: task.recipe,
        fallback_turn: task.fallback_turn,
        policy: task.policy.clone(),
        layer: task.layer,
        adopt_worker: task.adopt_worker,
        score: game.scores[task.seat],
        opponent_score: game.scores[1 - task.seat],
        wood: game.inventories[task.seat][WOOD],
        opponent_wood: game.inventories[1 - task.seat][WOOD],
        terminal_turn: game.turn,
        workers,
        opponent_workers,
        trained_ms: trained.map_or(-1, |unit| unit.ms),
        trained_cc: trained.map_or(-1, |unit| unit.cc),
        trained_hp: trained.map_or(-1, |unit| unit.hp),
        trained_chop: trained.map_or(-1, |unit| unit.chop),
        train_commands: counts[0],
        plant_commands: counts[1],
        harvest_commands: counts[2],
        chop_commands: counts[3],
        drop_commands: counts[4],
        move_commands: counts[5],
        shadow_decisions: shadow[0],
        exact_agreements: shadow[1],
        verb_agreements: shadow[2],
        resident_wait_actor_action: shadow[3],
        actor_local_resident_transit: shadow[4],
        overrides: shadow[5],
        elapsed_us: started.elapsed().as_micros(),
        decisions,
    })
}

fn parse_opponents(value: Option<&String>) -> Result<Vec<String>, String> {
    let opponents: Vec<String> = value.map_or_else(
        || DEFAULT_OPPONENTS.iter().map(ToString::to_string).collect(),
        |raw| {
            raw.split(',')
                .filter(|label| !label.is_empty())
                .map(ToString::to_string)
                .collect()
        },
    );
    if opponents.is_empty() {
        return Err("opponent list is empty".to_string());
    }
    for label in &opponents {
        Opponent::instantiate(label)?;
    }
    Ok(opponents)
}

fn write_rows(path: &str, rows: &[ResultRow]) -> Result<(), String> {
    let mut output = std::io::BufWriter::new(
        File::create(path).map_err(|error| format!("create {path}: {error}"))?,
    );
    writeln!(
        output,
        "seed\tseat\topponent\tpolicy\tlayer\tadopt_worker\trecipe\tfallback_turn\tms\tcc\thp\tchop\tscore\topponent_score\tmargin\twood\topponent_wood\twood_edge\tterminal_turn\tworkers\topponent_workers\ttrained_ms\ttrained_cc\ttrained_hp\ttrained_chop\ttrain_commands\tplant_commands\tharvest_commands\tchop_commands\tdrop_commands\tmove_commands\tshadow_decisions\texact_agreements\tverb_agreements\tresident_wait_actor_action\tactor_local_resident_transit\toverrides\telapsed_us"
    )
    .map_err(|error| format!("write header: {error}"))?;
    for row in rows {
        let spec = RECIPES[row.recipe];
        writeln!(
            output,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.seed,
            row.seat,
            row.opponent,
            row.policy,
            row.layer.label(),
            usize::from(row.adopt_worker),
            row.recipe,
            row.fallback_turn,
            spec.0,
            spec.1,
            spec.2,
            spec.3,
            row.score,
            row.opponent_score,
            row.score - row.opponent_score,
            row.wood,
            row.opponent_wood,
            row.wood - row.opponent_wood,
            row.terminal_turn,
            row.workers,
            row.opponent_workers,
            row.trained_ms,
            row.trained_cc,
            row.trained_hp,
            row.trained_chop,
            row.train_commands,
            row.plant_commands,
            row.harvest_commands,
            row.chop_commands,
            row.drop_commands,
            row.move_commands,
            row.shadow_decisions,
            row.exact_agreements,
            row.verb_agreements,
            row.resident_wait_actor_action,
            row.actor_local_resident_transit,
            row.overrides,
            row.elapsed_us,
        )
        .map_err(|error| format!("write row: {error}"))?;
    }
    output
        .flush()
        .map_err(|error| format!("flush {path}: {error}"))
}

fn write_decisions(path: &str, rows: &[ResultRow]) -> Result<usize, String> {
    let mut output = std::io::BufWriter::new(
        File::create(path).map_err(|error| format!("create {path}: {error}"))?,
    );
    writeln!(
        output,
        "seed\tseat\topponent\tpolicy\tturn\tunit_id\tordinal\tworker_count\topponent_workers\tx\ty\tms\tcc\thp\tchop\tfree\tcarry0\tcarry1\tcarry2\tcarry3\tcarry4\tcarry5\tinv0\tinv1\tinv2\tinv3\tinv4\tinv5\tscore\topponent_score\tplants\tlocal_plant_type\tlocal_plant_health\tlocal_plant_fruits\tnear_home\tnear_iron\tresident_command\tresident_verb\tactor_command\tactor_verb\tresident_target_x\tresident_target_y\tactor_target_x\tactor_target_y\tprevious_verb\tprevious_target_x\tprevious_target_y\texact_persistent\tverb_persistent\ttarget_persistent\tintent_age\tother_verb\tother_target_x\tother_target_y\tpaired_target_collision\tpoi_move_targets\tlocal_productive_actions\tresidual_options\tresident_directly_decodable\tstate_fingerprint\tterminal_margin\tterminal_wood_edge\tterminal_turn"
    )
    .map_err(|error| format!("write decision header: {error}"))?;
    let mut count = 0usize;
    for game in rows {
        for row in &game.decisions {
            let (resident_target_x, resident_target_y) = row.resident_target.unwrap_or((-1, -1));
            let (actor_target_x, actor_target_y) = row.actor_target.unwrap_or((-1, -1));
            let (previous_target_x, previous_target_y) = row.previous_target.unwrap_or((-1, -1));
            let (other_target_x, other_target_y) = row.other_target.unwrap_or((-1, -1));
            let mut fields = vec![
                game.seed.to_string(),
                game.seat.to_string(),
                game.opponent.clone(),
                game.policy.clone(),
                row.turn.to_string(),
                row.unit_id.to_string(),
                row.ordinal.to_string(),
                row.worker_count.to_string(),
                row.opponent_workers.to_string(),
                row.x.to_string(),
                row.y.to_string(),
                row.ms.to_string(),
                row.cc.to_string(),
                row.hp.to_string(),
                row.chop.to_string(),
                row.free.to_string(),
            ];
            fields.extend(row.carry.iter().map(ToString::to_string));
            fields.extend(row.inventory.iter().map(ToString::to_string));
            fields.extend([
                row.score.to_string(),
                row.opponent_score.to_string(),
                row.plants.to_string(),
                row.local_plant_type.clone(),
                row.local_plant_health.to_string(),
                row.local_plant_fruits.to_string(),
                usize::from(row.near_home).to_string(),
                usize::from(row.near_iron).to_string(),
                row.resident_command.clone(),
                verb(&row.resident_command).to_string(),
                row.actor_command.clone(),
                verb(&row.actor_command).to_string(),
                resident_target_x.to_string(),
                resident_target_y.to_string(),
                actor_target_x.to_string(),
                actor_target_y.to_string(),
                row.previous_verb.clone(),
                previous_target_x.to_string(),
                previous_target_y.to_string(),
                usize::from(row.exact_persistent).to_string(),
                usize::from(row.verb_persistent).to_string(),
                usize::from(row.target_persistent).to_string(),
                row.intent_age.to_string(),
                row.other_verb.clone(),
                other_target_x.to_string(),
                other_target_y.to_string(),
                usize::from(row.paired_target_collision).to_string(),
                row.poi_move_targets.to_string(),
                row.local_productive_actions.to_string(),
                row.residual_options.to_string(),
                usize::from(row.resident_directly_decodable).to_string(),
                format!("{:016x}", row.state_fingerprint),
                (game.score - game.opponent_score).to_string(),
                (game.wood - game.opponent_wood).to_string(),
                game.terminal_turn.to_string(),
            ]);
            writeln!(output, "{}", fields.join("\t"))
                .map_err(|error| format!("write decision row: {error}"))?;
            count += 1;
        }
    }
    output
        .flush()
        .map_err(|error| format!("flush {path}: {error}"))?;
    Ok(count)
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 5 {
        return Err(
            "usage: d11_recipe_catalog <live-binary> <output.tsv> <seed-start> <seed-count> [threads] [opponents-csv] [fallback-turns-csv|recipes:CSV|layers:CSV] [decisions:PATH]"
                .to_string(),
        );
    }
    if args.len() > 9 {
        return Err("too many arguments".to_string());
    }
    let binary = args[1].clone();
    let output = args[2].clone();
    let seed_start = args[3]
        .parse::<u64>()
        .map_err(|_| "invalid seed-start".to_string())?;
    let seed_count = args[4]
        .parse::<u64>()
        .map_err(|_| "invalid seed-count".to_string())?;
    if seed_count == 0 {
        return Err("seed-count must be positive".to_string());
    }
    let threads = args
        .get(5)
        .map(|value| value.parse::<usize>())
        .transpose()
        .map_err(|_| "invalid threads".to_string())?
        .unwrap_or(16)
        .clamp(1, 64);
    let opponents = parse_opponents(args.get(6))?;
    let policies: Vec<PolicyDefinition> = if let Some(raw) = args.get(7) {
        if let Some(labels) = raw.strip_prefix("layers:") {
            let definitions: Vec<_> = labels
                .split(',')
                .map(layer_policy)
                .collect::<Result<_, _>>()?;
            if definitions.is_empty() {
                return Err("layer policy list is empty".to_string());
            }
            definitions
        } else if let Some(values) = raw.strip_prefix("recipes:") {
            let recipes: Vec<usize> = values
                .split(',')
                .map(|value| value.parse::<usize>())
                .collect::<Result<_, _>>()
                .map_err(|_| "invalid recipes CSV".to_string())?;
            if recipes.is_empty() || recipes.iter().any(|&recipe| recipe >= RECIPES.len()) {
                return Err("recipes must be IDs 0 through 7".to_string());
            }
            recipes
                .into_iter()
                .map(|recipe| PolicyDefinition {
                    label: format!("recipe{recipe}"),
                    recipe,
                    fallback_turn: 0,
                    layer: LayerMode::ActorFull,
                    adopt_worker: false,
                })
                .collect()
        } else {
            let turns: Vec<usize> = raw
                .split(',')
                .map(|value| value.parse::<usize>())
                .collect::<Result<_, _>>()
                .map_err(|_| "invalid fallback-turns-csv".to_string())?;
            if turns.is_empty() || turns.contains(&0) {
                return Err("fallback turns must be positive".to_string());
            }
            turns
                .into_iter()
                .map(|turn| PolicyDefinition {
                    label: format!("recipe7_fallback{turn}"),
                    recipe: 7,
                    fallback_turn: turn,
                    layer: LayerMode::ActorFull,
                    adopt_worker: false,
                })
                .collect()
        }
    } else {
        (0..RECIPES.len())
            .map(|recipe| PolicyDefinition {
                label: format!("recipe{recipe}"),
                recipe,
                fallback_turn: 0,
                layer: LayerMode::ActorFull,
                adopt_worker: false,
            })
            .collect()
    };
    let decision_output = args
        .get(8)
        .map(|raw| {
            raw.strip_prefix("decisions:")
                .filter(|path| !path.is_empty())
                .map(ToString::to_string)
                .ok_or_else(|| "decision output must be decisions:PATH".to_string())
        })
        .transpose()?;
    let collect_decisions = decision_output.is_some();
    let policy_catalog = &policies;
    let tasks: Vec<Task> = (seed_start..seed_start + seed_count)
        .flat_map(|seed| {
            opponents.iter().cloned().flat_map(move |opponent| {
                (0..2).flat_map(move |seat| {
                    let opponent = opponent.clone();
                    policy_catalog.iter().cloned().map(move |policy| Task {
                        seed,
                        seat,
                        opponent: opponent.clone(),
                        recipe: policy.recipe,
                        fallback_turn: policy.fallback_turn,
                        policy: policy.label,
                        layer: policy.layer,
                        adopt_worker: policy.adopt_worker,
                        collect_decisions,
                    })
                })
            })
        })
        .collect();
    let total = tasks.len();
    let completed = Arc::new(AtomicUsize::new(0));
    let chunk_size = total.div_ceil(threads);
    let groups = std::thread::scope(|scope| {
        let handles: Vec<_> = tasks
            .chunks(chunk_size)
            .map(|chunk| {
                let completed = Arc::clone(&completed);
                let binary = &binary;
                scope.spawn(move || {
                    let mut rows = Vec::with_capacity(chunk.len());
                    for task in chunk {
                        let row = play(binary, task).map_err(|error| {
                            format!(
                                "seed={} seat={} opponent={} policy={} recipe={} fallback_turn={} adopt_worker={}: {error}",
                                task.seed,
                                task.seat,
                                task.opponent,
                                task.policy,
                                task.recipe,
                                task.fallback_turn,
                                task.adopt_worker
                            )
                        })?;
                        rows.push(row);
                        let done = completed.fetch_add(1, Ordering::Relaxed) + 1;
                        if done % 32 == 0 || done == total {
                            eprintln!("completed {done}/{total} games");
                        }
                    }
                    Ok::<_, String>(rows)
                })
            })
            .collect();
        handles
            .into_iter()
            .map(|handle| {
                handle
                    .join()
                    .map_err(|_| "worker thread panicked".to_string())?
            })
            .collect::<Result<Vec<_>, String>>()
    })?;
    let mut rows: Vec<ResultRow> = groups.into_iter().flatten().collect();
    rows.sort_by(|left, right| {
        (
            left.seed,
            &left.opponent,
            left.seat,
            &left.policy,
            left.recipe,
            left.fallback_turn,
        )
            .cmp(&(
                right.seed,
                &right.opponent,
                right.seat,
                &right.policy,
                right.recipe,
                right.fallback_turn,
            ))
    });
    write_rows(&output, &rows)?;
    if let Some(path) = decision_output {
        let decisions = write_decisions(&path, &rows)?;
        eprintln!("wrote {decisions} resident decision rows to {path}");
    }
    eprintln!(
        "wrote {} paired recipe games for {} seeds and {} opponents to {}",
        rows.len(),
        seed_count,
        opponents.len(),
        output
    );
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("d11_recipe_catalog: {error}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frozen_recipe_catalog_is_unique() {
        let unique: BTreeSet<_> = RECIPES.into_iter().collect();
        assert_eq!(RECIPES.len(), 8);
        assert_eq!(unique.len(), RECIPES.len());
        assert_eq!(RECIPES[6], (2, 2, 0, 2));
    }

    #[test]
    fn default_opponents_all_instantiate() {
        for label in DEFAULT_OPPONENTS {
            Opponent::instantiate(label).expect("known default opponent");
        }
    }

    #[test]
    fn native_layer_policies_enable_worker_adoption() {
        for label in [
            "native_resident_starter_actor_second",
            "native_actor_all",
            "native_actor_starter_resident_second",
        ] {
            let policy = layer_policy(label).expect("known native layer");
            assert!(policy.adopt_worker);
            assert_eq!(policy.fallback_turn, 0);
        }
        assert!(!layer_policy("resident").unwrap().adopt_worker);
    }
}
