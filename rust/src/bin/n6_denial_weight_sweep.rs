//! N6 exact-resident denial-distance weight sweep on the A2 referee substrate.
//!
//! The three resident modules are generated from the sacred snapshot by
//! `cgauto/n6_denial_weight_sweep.py`; compile-time paths are mandatory so this runner
//! never edits or registers the resident source.

#[allow(dead_code, unused_imports)]
mod low_resident {
    include!(env!("N6_LOW_SOURCE"));
}
#[allow(dead_code, unused_imports)]
mod control_resident {
    include!(env!("N6_CONTROL_SOURCE"));
}
#[allow(dead_code, unused_imports)]
mod high_resident {
    include!(env!("N6_HIGH_SOURCE"));
}

use std::collections::BTreeMap;
use std::fmt::Write as FmtWrite;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::a2_referee_parity::{self, LegalityReport};
use troll_farm::game::engine::{bfs_distances, has_stalled};
use troll_farm::game::state::{GameState, Plant, Unit};
use troll_farm::rl_macro::{MacroOpponentMode, MACRO_TOTAL_TURNS};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{
    LegendFieldProxyV2, LegendFieldProxyV2Config,
};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

const FNV_OFFSET: u64 = 14_695_981_039_346_656_037;
const DEVELOPMENT_START: i64 = 9_858_000;
const DEVELOPMENT_MAPS: i64 = 32;
const CONFIRMATION_START: i64 = 9_859_000;
const CONFIRMATION_MAPS: i64 = 128;

fn fnv1a(mut hash: u64, bytes: &[u8]) -> u64 {
    for byte in bytes {
        hash ^= u64::from(*byte);
        hash = hash.wrapping_mul(1_099_511_628_211);
    }
    hash
}

fn hash_i32(hash: u64, value: i32) -> u64 {
    fnv1a(hash, &value.to_le_bytes())
}

fn canonical_state_hash(game: &GameState) -> u64 {
    let mut hash = FNV_OFFSET;
    for value in [game.width, game.height, game.turn, game.next_id] {
        hash = hash_i32(hash, value);
    }
    for cell in game.shacks {
        hash = hash_i32(hash, cell.0);
        hash = hash_i32(hash, cell.1);
    }
    for inventory in game.inventories {
        for value in inventory {
            hash = hash_i32(hash, value);
        }
    }
    for value in game.scores {
        hash = hash_i32(hash, value);
    }
    let mut units: Vec<_> = game.units.iter().collect();
    units.sort_by_key(|unit| unit.id);
    for unit in units {
        for value in [
            unit.id,
            unit.player,
            unit.x,
            unit.y,
            unit.ms,
            unit.cc,
            unit.hp,
            unit.chop,
        ] {
            hash = hash_i32(hash, value);
        }
        for value in unit.carry {
            hash = hash_i32(hash, value);
        }
    }
    let mut plants: Vec<_> = game.plants.iter().collect();
    plants.sort_by_key(|plant| (plant.x, plant.y));
    for plant in plants {
        hash = fnv1a(hash, plant.plant_type.as_bytes());
        for value in [
            plant.x,
            plant.y,
            plant.size,
            plant.health,
            plant.fruits,
            plant.cooldown,
        ] {
            hash = hash_i32(hash, value);
        }
    }
    hash
}

fn hash_commands(mut hash: u64, commands: &[Vec<String>; 2]) -> u64 {
    for (player, player_commands) in commands.iter().enumerate() {
        hash = fnv1a(hash, &[player as u8]);
        for command in player_commands {
            hash = fnv1a(hash, command.as_bytes());
            hash = fnv1a(hash, &[0]);
        }
        hash = fnv1a(hash, &[255]);
    }
    hash
}

macro_rules! define_view {
    ($function:ident, $module:ident) => {
        fn $function(game: &GameState, player: usize) -> $module::game::GameState {
            let opponent = 1 - player;
            $module::game::GameState {
                width: game.width,
                height: game.height,
                walkable: game.walkable.iter().copied().collect(),
                shacks: [game.shacks[player], game.shacks[opponent]],
                inventories: [game.inventories[player], game.inventories[opponent]],
                units: game
                    .units
                    .iter()
                    .map(|unit| $module::game::Unit {
                        id: unit.id,
                        player: usize::from(unit.player as usize != player),
                        cell: unit.pos(),
                        stats: $module::game::Stats {
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
                    .map(|plant| $module::game::Plant {
                        kind: $module::game::PlantKind::parse(&plant.plant_type)
                            .expect("known plant type"),
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
                iron: game.iron.iter().copied().collect(),
                water: game.water.iter().copied().collect(),
            }
        }
    };
}

define_view!(low_view, low_resident);
define_view!(control_view, control_resident);
define_view!(high_view, high_resident);

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum Arm {
    Control,
    Low,
    High,
}

impl Arm {
    fn label(self) -> &'static str {
        match self {
            Self::Control => "control",
            Self::Low => "low",
            Self::High => "high",
        }
    }
}

enum ArmBot {
    Low(low_resident::bot::moisan::SecureOrchardBot),
    Control(control_resident::bot::moisan::SecureOrchardBot),
    High(high_resident::bot::moisan::SecureOrchardBot),
}

impl ArmBot {
    fn new(arm: Arm) -> Self {
        match arm {
            Arm::Low => Self::Low(low_resident::bot::moisan::SecureOrchardBot::new()),
            Arm::Control => {
                Self::Control(control_resident::bot::moisan::SecureOrchardBot::new())
            }
            Arm::High => Self::High(high_resident::bot::moisan::SecureOrchardBot::new()),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Low(bot) => {
                use low_resident::bot::Bot as _;
                bot.commands(&low_view(game, player))
            }
            Self::Control(bot) => {
                use control_resident::bot::Bot as _;
                bot.commands(&control_view(game, player))
            }
            Self::High(bot) => {
                use high_resident::bot::Bot as _;
                bot.commands(&high_view(game, player))
            }
        }
    }
}

enum Opponent {
    Resident(control_resident::bot::moisan::SecureOrchardBot),
    Local(Box<dyn Strategy>),
}

impl Opponent {
    fn new(mode: MacroOpponentMode) -> Self {
        match mode {
            MacroOpponentMode::Resident => {
                Self::Resident(control_resident::bot::moisan::SecureOrchardBot::new())
            }
            MacroOpponentMode::GoldAdaptive => Self::Local(Box::new(GoldElite::adaptive())),
            MacroOpponentMode::CompactGold => Self::Local(Box::new(CompactGold::new())),
            MacroOpponentMode::NorxondorThree => {
                Self::Local(Box::new(NorxondorNative::new(true)))
            }
            MacroOpponentMode::LegendBalanced => Self::Local(Box::new(
                LegendFieldProxyV2::configured(LegendFieldProxyV2Config {
                    producer_spec: (2, 2, 1, 1),
                    chopper_spec: (2, 2, 0, 2),
                    late_chop: true,
                }),
            )),
            MacroOpponentMode::MyBot => Self::Local(Box::new(MyBot::new())),
            MacroOpponentMode::ScriptBoss => Self::Local(Box::new(ScriptBoss::new())),
            MacroOpponentMode::SilverBoss => Self::Local(Box::new(SilverBoss::new())),
        }
    }

    fn commands(&mut self, game: &GameState, player: usize) -> Vec<String> {
        match self {
            Self::Resident(bot) => {
                use control_resident::bot::Bot as _;
                bot.commands(&control_view(game, player))
            }
            Self::Local(strategy) => strategy.decide(game, player),
        }
    }
}

#[derive(Clone)]
struct StateSnapshot {
    units: Vec<Unit>,
    plants: Vec<Plant>,
    inventories: [[i32; 6]; 2],
}

impl StateSnapshot {
    fn capture(game: &GameState) -> Self {
        Self {
            units: game.units.clone(),
            plants: game.plants.clone(),
            inventories: game.inventories,
        }
    }
}

fn build_map_rows(game: &GameState) -> Vec<String> {
    (0..game.height)
        .map(|y| {
            (0..game.width)
                .map(|x| {
                    let cell = (x, y);
                    if game.shacks[0] == cell {
                        '0'
                    } else if game.shacks[1] == cell {
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
                .collect::<String>()
        })
        .collect()
}

struct SideResult {
    done: bool,
    turn: i32,
    own_score: i32,
    opponent_score: i32,
    action_hash: u64,
    state_hash: u64,
    legality: LegalityReport,
    map_rows: Vec<String>,
    states: Vec<StateSnapshot>,
    turn_commands: Vec<(Vec<String>, Vec<String>)>,
}

fn play(
    map_seed: i64,
    seat: usize,
    opponent_index: usize,
    arm: Arm,
    dump: bool,
) -> SideResult {
    let mut referee = a2_referee_parity::generate_official(map_seed);
    let mut ours = ArmBot::new(arm);
    let mut theirs = Opponent::new(MacroOpponentMode::from_index(opponent_index));
    let mut turns_until_end = 0;
    let mut action_hash = FNV_OFFSET;
    let mut states = Vec::new();
    let mut turn_commands = Vec::new();
    let map_rows = if dump {
        build_map_rows(&referee.game)
    } else {
        Vec::new()
    };
    if dump {
        states.push(StateSnapshot::capture(&referee.game));
    }
    let mut done = false;
    while !done {
        let opponent = 1 - seat;
        let ours_commands = ours.commands(&referee.game, seat);
        let theirs_commands = theirs.commands(&referee.game, opponent);
        let commands = if seat == 0 {
            [ours_commands, theirs_commands]
        } else {
            [theirs_commands, ours_commands]
        };
        action_hash = hash_commands(action_hash, &commands);
        if dump {
            turn_commands.push((commands[0].clone(), commands[1].clone()));
        }
        a2_referee_parity::step(&mut referee, &commands[0], &commands[1]);
        if dump {
            states.push(StateSnapshot::capture(&referee.game));
        }
        done = referee.game.turn > MACRO_TOTAL_TURNS
            || has_stalled(&referee.game, &mut turns_until_end);
    }
    SideResult {
        done,
        turn: referee.game.turn,
        own_score: referee.game.scores[seat],
        opponent_score: referee.game.scores[1 - seat],
        action_hash,
        state_hash: canonical_state_hash(&referee.game),
        legality: referee.legality,
        map_rows,
        states,
        turn_commands,
    }
}

fn ortho_neighbors(cell: (i32, i32)) -> [(i32, i32); 4] {
    [
        (cell.0, cell.1 + 1),
        (cell.0 + 1, cell.1),
        (cell.0, cell.1 - 1),
        (cell.0 - 1, cell.1),
    ]
}

fn focus_type(game: &GameState, seat: usize) -> String {
    let starts: Vec<_> = ortho_neighbors(game.shacks[seat])
        .into_iter()
        .filter(|cell| game.walkable.contains(cell))
        .collect();
    let distance = bfs_distances(&game.walkable, &starts);
    ["LEMON", "PLUM"]
        .into_iter()
        .min_by_key(|kind| {
            game.plants
                .iter()
                .filter(|plant| plant.plant_type == *kind)
                .map(|plant| distance.get(&plant.pos()).copied().unwrap_or(10_000))
                .sum::<i32>()
        })
        .unwrap_or("LEMON")
        .to_owned()
}

fn manhattan(left: (i32, i32), right: (i32, i32)) -> i32 {
    (left.0 - right.0).abs() + (left.1 - right.1).abs()
}

fn command_target(
    game: &GameState,
    seat: usize,
    command: &str,
) -> Option<(i32, i32)> {
    let fields: Vec<_> = command.split_whitespace().collect();
    match fields.as_slice() {
        [verb, _unit_id, x, y] if verb.eq_ignore_ascii_case("MOVE") => {
            Some((x.parse().ok()?, y.parse().ok()?))
        }
        [verb, unit_id] if verb.eq_ignore_ascii_case("CHOP") => {
            let id: i32 = unit_id.parse().ok()?;
            game.units
                .iter()
                .find(|unit| unit.id == id && unit.player as usize == seat)
                .map(|unit| unit.pos())
        }
        _ => None,
    }
}

fn focus_distance(
    game: &GameState,
    seat: usize,
    commands: &[String],
    focus: &str,
) -> Option<i32> {
    commands
        .iter()
        .flat_map(|line| line.split(';'))
        .filter_map(|command| command_target(game, seat, command.trim()))
        .filter(|cell| {
            game.plants
                .iter()
                .any(|plant| plant.pos() == *cell && plant.plant_type == focus)
        })
        .map(|cell| manhattan(cell, game.shacks[1 - seat]))
        .min()
}

#[derive(Default)]
struct Divergence {
    diverged: bool,
    turn: Option<i32>,
    common_state: bool,
    both_focus: bool,
    directional_comparable: bool,
    control_focus_distance: Option<i32>,
    candidate_focus_distance: Option<i32>,
    directional: bool,
    opponent_command_mismatch: bool,
}

fn first_divergence(
    map_seed: i64,
    seat: usize,
    opponent_index: usize,
    arm: Arm,
) -> Divergence {
    assert!(arm != Arm::Control);
    let mut control_referee = a2_referee_parity::generate_official(map_seed);
    let mut candidate_referee = a2_referee_parity::generate_official(map_seed);
    let focus = focus_type(&control_referee.game, seat);
    let mut control = ArmBot::new(Arm::Control);
    let mut candidate = ArmBot::new(arm);
    let mode = MacroOpponentMode::from_index(opponent_index);
    let mut control_opponent = Opponent::new(mode);
    let mut candidate_opponent = Opponent::new(mode);
    let mut control_until_end = 0;
    let mut candidate_until_end = 0;
    loop {
        let common_state =
            canonical_state_hash(&control_referee.game)
                == canonical_state_hash(&candidate_referee.game);
        if !common_state {
            return Divergence {
                common_state: false,
                ..Divergence::default()
            };
        }
        let opponent = 1 - seat;
        let control_commands = control.commands(&control_referee.game, seat);
        let candidate_commands = candidate.commands(&candidate_referee.game, seat);
        let control_opponent_commands =
            control_opponent.commands(&control_referee.game, opponent);
        let candidate_opponent_commands =
            candidate_opponent.commands(&candidate_referee.game, opponent);
        if control_opponent_commands != candidate_opponent_commands {
            return Divergence {
                common_state: true,
                opponent_command_mismatch: true,
                ..Divergence::default()
            };
        }
        if control_commands != candidate_commands {
            let control_distance =
                focus_distance(&control_referee.game, seat, &control_commands, &focus);
            let candidate_distance =
                focus_distance(&control_referee.game, seat, &candidate_commands, &focus);
            let both_focus = control_distance.is_some() && candidate_distance.is_some();
            let directional_comparable = control_distance.is_some()
                || candidate_distance.is_some();
            let directional = match (arm, control_distance, candidate_distance) {
                (Arm::High, None, Some(_)) => true,
                (Arm::High, Some(control_value), Some(candidate_value)) => {
                    candidate_value < control_value
                }
                (Arm::Low, Some(_), None) => true,
                (Arm::Low, Some(control_value), Some(candidate_value)) => {
                    candidate_value > control_value
                }
                _ => false,
            };
            return Divergence {
                diverged: true,
                turn: Some(control_referee.game.turn),
                common_state: true,
                both_focus,
                directional_comparable,
                control_focus_distance: control_distance,
                candidate_focus_distance: candidate_distance,
                directional,
                opponent_command_mismatch: false,
            };
        }
        let control_pair = if seat == 0 {
            [control_commands, control_opponent_commands]
        } else {
            [control_opponent_commands, control_commands]
        };
        let candidate_pair = if seat == 0 {
            [candidate_commands, candidate_opponent_commands]
        } else {
            [candidate_opponent_commands, candidate_commands]
        };
        a2_referee_parity::step(
            &mut control_referee,
            &control_pair[0],
            &control_pair[1],
        );
        a2_referee_parity::step(
            &mut candidate_referee,
            &candidate_pair[0],
            &candidate_pair[1],
        );
        let control_done = control_referee.game.turn > MACRO_TOTAL_TURNS
            || has_stalled(&control_referee.game, &mut control_until_end);
        let candidate_done = candidate_referee.game.turn > MACRO_TOTAL_TURNS
            || has_stalled(&candidate_referee.game, &mut candidate_until_end);
        if control_done || candidate_done {
            return Divergence {
                common_state: true,
                ..Divergence::default()
            };
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

struct Row {
    task: Task,
    arm: Arm,
    side: SideResult,
    divergence: Divergence,
}

fn json_escape_into(buffer: &mut String, text: &str) {
    buffer.push('"');
    for character in text.chars() {
        match character {
            '"' => buffer.push_str("\\\""),
            '\\' => buffer.push_str("\\\\"),
            '\n' => buffer.push_str("\\n"),
            '\r' => buffer.push_str("\\r"),
            '\t' => buffer.push_str("\\t"),
            _ => buffer.push(character),
        }
    }
    buffer.push('"');
}

fn write_unit(buffer: &mut String, unit: &Unit) {
    write!(
        buffer,
        "[{},{},{},{},{},{},{},{},{},{},{},{},{},{}]",
        unit.id,
        unit.player,
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
        unit.carry[5],
    )
    .expect("write N6 unit");
}

fn write_plant(buffer: &mut String, plant: &Plant) {
    buffer.push('[');
    write!(buffer, "{},{},", plant.x, plant.y).expect("write N6 plant position");
    json_escape_into(buffer, &plant.plant_type);
    write!(
        buffer,
        ",{},{},{},{}]",
        plant.size, plant.health, plant.fruits, plant.cooldown
    )
    .expect("write N6 plant");
}

fn write_state(buffer: &mut String, state: &StateSnapshot) {
    buffer.push_str("{\"u\":[");
    for (index, unit) in state.units.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_unit(buffer, unit);
    }
    buffer.push_str("],\"p\":[");
    for (index, plant) in state.plants.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_plant(buffer, plant);
    }
    write!(
        buffer,
        "],\"b\":[[{},{},{},{},{},{}],[{},{},{},{},{},{}]]}}",
        state.inventories[0][0],
        state.inventories[0][1],
        state.inventories[0][2],
        state.inventories[0][3],
        state.inventories[0][4],
        state.inventories[0][5],
        state.inventories[1][0],
        state.inventories[1][1],
        state.inventories[1][2],
        state.inventories[1][3],
        state.inventories[1][4],
        state.inventories[1][5],
    )
    .expect("write N6 inventory");
}

fn write_commands(buffer: &mut String, commands: &[String]) {
    buffer.push('[');
    for (index, command) in commands.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        json_escape_into(buffer, command);
    }
    buffer.push(']');
}

fn write_trajectory_line(task: &Task, arm: Arm, side: &SideResult) -> String {
    let (score0, score1) = if task.seat == 0 {
        (side.own_score, side.opponent_score)
    } else {
        (side.opponent_score, side.own_score)
    };
    let mut buffer = String::with_capacity(4096);
    write!(
        buffer,
        "{{\"seed\":{},\"seat\":{},\"opp\":{},\"opp_name\":",
        task.map_seed, task.seat, task.opponent
    )
    .expect("write N6 trajectory header");
    json_escape_into(
        &mut buffer,
        MacroOpponentMode::from_index(task.opponent).label(),
    );
    buffer.push_str(",\"arm\":");
    json_escape_into(&mut buffer, arm.label());
    buffer.push_str(",\"map_rows\":[");
    for (index, row) in side.map_rows.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        json_escape_into(&mut buffer, row);
    }
    write!(
        buffer,
        "],\"turns\":{},\"scores\":[{},{}],\"states\":[",
        side.turn_commands.len(),
        score0,
        score1
    )
    .expect("write N6 trajectory scores");
    for (index, state) in side.states.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_state(&mut buffer, state);
    }
    buffer.push_str("],\"c0\":[");
    for (index, (commands0, _)) in side.turn_commands.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_commands(&mut buffer, commands0);
    }
    buffer.push_str("],\"c1\":[");
    for (index, (_, commands1)) in side.turn_commands.iter().enumerate() {
        if index > 0 {
            buffer.push(',');
        }
        write_commands(&mut buffer, commands1);
    }
    buffer.push_str("]}\n");
    buffer
}

fn run_task(
    task: Task,
    arms: &[Arm],
    dump: bool,
    trajectory_writer: Option<&Mutex<BufWriter<File>>>,
) -> Vec<Row> {
    arms.iter()
        .copied()
        .map(|arm| {
            let divergence = if arm == Arm::Control {
                Divergence::default()
            } else {
                first_divergence(task.map_seed, task.seat, task.opponent, arm)
            };
            let mut side = play(task.map_seed, task.seat, task.opponent, arm, dump);
            if dump {
                trajectory_writer
                    .expect("N6 trajectory writer")
                    .lock()
                    .expect("N6 trajectory lock")
                    .write_all(write_trajectory_line(&task, arm, &side).as_bytes())
                    .expect("write N6 trajectory");
                side.map_rows.clear();
                side.states.clear();
                side.turn_commands.clear();
            }
            Row {
                task,
                arm,
                side,
                divergence,
            }
        })
        .collect()
}

fn reason_counts(report: &LegalityReport) -> String {
    report
        .reason_counts()
        .into_iter()
        .map(|(reason, count)| format!("{reason}={count}"))
        .collect::<Vec<_>>()
        .join(",")
}

fn optional_i32(value: Option<i32>) -> String {
    value.map(|item| item.to_string()).unwrap_or_default()
}

fn write_rows(output: &str, rows: &[Row]) {
    let mut writer = BufWriter::new(File::create(output).expect("create N6 output"));
    writeln!(
        writer,
        "map_seed\tseat\topponent_index\topponent\tarm\tdone\tturn\town_score\t\
         opponent_score\tmargin\taction_hash\tstate_hash\tcommands_checked\t\
         legality_issues\tcritical_issues\tunclassified_issues\tlegality_reason_counts\t\
         command_diverged\tfirst_divergence_turn\tfirst_divergence_common_state\t\
         first_both_focus\tfirst_directional_comparable\tfirst_control_focus_distance\t\
         first_candidate_focus_distance\tfirst_directional\t\
         opponent_command_mismatch"
    )
    .expect("write N6 header");
    for row in rows {
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t\
             {}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            row.arm.label(),
            u8::from(row.side.done),
            row.side.turn,
            row.side.own_score,
            row.side.opponent_score,
            row.side.own_score - row.side.opponent_score,
            row.side.action_hash,
            row.side.state_hash,
            row.side.legality.commands_checked,
            row.side.legality.issue_count(),
            row.side.legality.critical_issue_count(),
            row.side.legality.unclassified_issue_count(),
            reason_counts(&row.side.legality),
            u8::from(row.divergence.diverged),
            optional_i32(row.divergence.turn),
            u8::from(row.divergence.common_state),
            u8::from(row.divergence.both_focus),
            u8::from(row.divergence.directional_comparable),
            optional_i32(row.divergence.control_focus_distance),
            optional_i32(row.divergence.candidate_focus_distance),
            u8::from(row.divergence.directional),
            u8::from(row.divergence.opponent_command_mismatch),
        )
        .expect("write N6 row");
    }
}

fn parse<T: std::str::FromStr>(text: &str, what: &str) -> T {
    text.parse()
        .unwrap_or_else(|_| panic!("invalid {what}: {text}"))
}

fn selected_arms(mode: &str) -> Vec<Arm> {
    match mode {
        "all" => vec![Arm::Control, Arm::Low, Arm::High],
        "low" => vec![Arm::Control, Arm::Low],
        "high" => vec![Arm::Control, Arm::High],
        _ => panic!("arms must be all, low, or high"),
    }
}

fn range_allowed(start: i64, maps: i64, mode: &str) -> bool {
    let end = start.saturating_add(maps);
    let development =
        start >= DEVELOPMENT_START && end <= DEVELOPMENT_START + DEVELOPMENT_MAPS;
    let confirmation = start >= CONFIRMATION_START
        && end <= CONFIRMATION_START + CONFIRMATION_MAPS;
    development || (mode != "all" && confirmation)
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert!(
        args.len() == 6 || args.len() == 7,
        "usage: n6_denial_weight_sweep START_SEED MAPS OUTPUT THREADS ARMS [TRAJECTORIES]"
    );
    let start: i64 = parse(&args[1], "start seed");
    let maps: i64 = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    let mode = &args[5];
    assert!(maps > 0 && threads > 0);
    assert!(
        range_allowed(start, maps, mode),
        "N6 runner is confined to frozen development/confirmation ranges"
    );
    let dump = args.len() == 7;
    let trajectory_writer = if dump {
        Some(Mutex::new(BufWriter::new(
            File::create(&args[6]).expect("create N6 trajectory NDJSON"),
        )))
    } else {
        None
    };
    let arms = Arc::new(selected_arms(mode));
    let work: Vec<Task> = (start..start + maps)
        .flat_map(|map_seed| {
            (0..2).flat_map(move |seat| {
                (0..MacroOpponentMode::ALL.len()).map(move |opponent| Task {
                    map_seed,
                    seat,
                    opponent,
                })
            })
        })
        .collect();
    let work = Arc::new(work);
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::new()));
    let trajectory_writer = Arc::new(trajectory_writer);
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let arms = Arc::clone(&arms);
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            let trajectory_writer = Arc::clone(&trajectory_writer);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(task) = work.get(index).copied() else {
                    break;
                };
                rows.lock()
                    .expect("N6 rows lock")
                    .extend(run_task(
                        task,
                        &arms,
                        dump,
                        trajectory_writer.as_ref().as_ref(),
                    ));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("N6 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole N6 rows")
        .into_inner()
        .expect("N6 rows lock");
    rows.sort_by_key(|row| (row.task, row.arm));
    write_rows(output, &rows);
    let counts = rows.iter().fold(BTreeMap::new(), |mut counts, row| {
        *counts.entry(row.arm.label()).or_insert(0usize) += 1;
        counts
    });
    let critical: usize = rows
        .iter()
        .map(|row| row.side.legality.critical_issue_count())
        .sum();
    let unclassified: usize = rows
        .iter()
        .map(|row| row.side.legality.unclassified_issue_count())
        .sum();
    println!(
        "saved {} rows {:?} critical={} unclassified={} in {:.3}s to {}",
        rows.len(),
        counts,
        critical,
        unclassified,
        started.elapsed().as_secs_f64(),
        output,
    );
}
