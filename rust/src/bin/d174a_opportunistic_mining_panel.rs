//! D174a opportunistic-mining fresh panel: paired CONTROL (frozen pre-fix resident,
//! byte-identical copy at `rust/src/d171a_control_resident_snapshot.rs`, reused unchanged
//! per the D174a protocol -- verified same SHA as the dev copy before this panel was built)
//! vs CANDIDATE (the dev copy `rust/src/bin/yamo_orchard_live.rs` at fix-applied time,
//! reused automatically via the existing `#[path]` library alias
//! `troll_farm::resident_policy`) across the fresh panel of 128 maps x 8 opponent families x
//! 2 seats declared in
//! data/analysis/live-agent-6553250/d174a-opportunistic-mining-protocol-2026-07-28.md.
//!
//! Opponent=Resident always instantiates from the CONTROL snapshot on both sides of a pair
//! (matching D171a's own convention), so a pair only ever differs in our own bot's code.
//!
//! Unlike D171a's oscillation breaker (a stateful arm/disarm memory), this fix -- both
//! Delta 1 (`opportunistic_mine_rewrite`, a post-selection command rewrite) and the
//! Phase-0 TRAIN-gate repair (one boolean clause deleted from `MoisanBot::can_train`) --
//! is stateless and recomputed fresh every turn, so "activated" is exactly "own commands
//! ever diverge between control and candidate" (no separate armed-tracker is needed; if
//! neither delta ever changes a turn's own commands, the two trajectories are
//! byte-identical from turn 1 to the end by induction: identical own commands ->
//! identical opponent inputs -> identical next state, every turn).
//!
//! This binary also emits full per-turn trajectories (own+opponent units, all plants, both
//! banks, both players' raw commands) as NDJSON, schema-compatible with
//! `cgauto/waste_sweep.build_decoded_game`'s `states`/`trajectory` parameters, so
//! `cgauto/analyze_d174a_opportunistic_mining.py` can run all six standing waste detectors
//! over both arms for the mechanism gate. CONTROL trajectories are always written; CANDIDATE
//! trajectories are written only for tasks where a divergence actually occurred (inactive
//! tasks are byte-identical to CONTROL by the argument above, so re-decoding them a second
//! time would only reproduce CONTROL's own counts).

#[path = "../d171a_control_resident_snapshot.rs"]
mod control_resident;

use std::fmt::Write as FmtWrite;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::official_mapgen::generate_official;
use troll_farm::game::state::{GameState, Plant, Unit};
use troll_farm::resident_policy;
use troll_farm::rl_macro::{MacroOpponentMode, MACRO_TOTAL_TURNS};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

const FNV_OFFSET: u64 = 14_695_981_039_346_656_037_u64;
const FRESH_START_SEED: i64 = 9_855_000;
const FRESH_MAP_COUNT: i64 = 128;

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
        hash = hash_i32(hash, unit.id);
        hash = hash_i32(hash, unit.player);
        hash = hash_i32(hash, unit.x);
        hash = hash_i32(hash, unit.y);
        hash = hash_i32(hash, unit.ms);
        hash = hash_i32(hash, unit.cc);
        hash = hash_i32(hash, unit.hp);
        hash = hash_i32(hash, unit.chop);
        for value in unit.carry {
            hash = hash_i32(hash, value);
        }
    }
    let mut plants: Vec<_> = game.plants.iter().collect();
    plants.sort_by_key(|plant| (plant.x, plant.y));
    for plant in plants {
        hash = fnv1a(hash, plant.plant_type.as_bytes());
        hash = hash_i32(hash, plant.x);
        hash = hash_i32(hash, plant.y);
        hash = hash_i32(hash, plant.size);
        hash = hash_i32(hash, plant.health);
        hash = hash_i32(hash, plant.fruits);
        hash = hash_i32(hash, plant.cooldown);
    }
    hash
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

fn control_view(game: &GameState, player: usize) -> control_resident::game::GameState {
    let opponent = 1 - player;
    control_resident::game::GameState {
        width: game.width,
        height: game.height,
        walkable: game.walkable.iter().copied().collect(),
        shacks: [game.shacks[player], game.shacks[opponent]],
        inventories: [game.inventories[player], game.inventories[opponent]],
        units: game
            .units
            .iter()
            .map(|unit| control_resident::game::Unit {
                id: unit.id,
                player: usize::from(unit.player as usize != player),
                cell: unit.pos(),
                stats: control_resident::game::Stats {
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
            .map(|plant| control_resident::game::Plant {
                kind: control_resident::game::PlantKind::parse(&plant.plant_type)
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

/// Everything one turn boundary needs for the `waste_sweep` bridge: both players' units,
/// every live plant, and both banks. Captured once per turn (turn 0 = before any command).
struct StateSnapshot {
    units: Vec<Unit>,
    plants: Vec<Plant>,
    inventories: [[i32; 6]; 2],
}

impl StateSnapshot {
    fn capture(game: &GameState) -> Self {
        StateSnapshot {
            units: game.units.clone(),
            plants: game.plants.clone(),
            inventories: game.inventories,
        }
    }
}

/// Terrain is static for the whole game (`engine::step` never mutates
/// walkable/water/iron/shacks), so this is captured once from the initial `GameState` and
/// reused for every turn. Ascii convention matches `rust/src/game/state.rs::from_ascii` and
/// `cgauto/top_player_opening_analysis.terrain` exactly: '.' walkable, '~' water, '+' iron,
/// '0'/'1' shacks (not walkable), anything else (here just '#') an ordinary wall.
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
    own_action_hash: u64,
    state_hash: u64,
    own_workers_final: usize,
    own_commands_by_turn: Vec<(i32, Vec<String>)>,
    // Present only when trajectory dumping is requested for this call.
    map_rows: Vec<String>,
    states: Vec<StateSnapshot>,
    turn_commands: Vec<(Vec<String>, Vec<String>)>,
}

fn own_command_snapshot(commands: &[String]) -> Vec<String> {
    let mut sorted: Vec<String> = commands.to_vec();
    sorted.sort();
    sorted
}

macro_rules! define_play_side {
    ($fn_name:ident, $resident_mod:path) => {
        fn $fn_name(map_seed: i64, seat: usize, opponent_index: usize, dump: bool) -> SideResult {
            use $resident_mod as res;
            use res::bot::Bot as _;

            let mut game = generate_official(map_seed);
            let mut ours = res::bot::moisan::SecureOrchardBot::new();
            let mut theirs = Opponent::new(MacroOpponentMode::from_index(opponent_index));
            let mut turns_until_end = 0i32;
            let mut action_hash = FNV_OFFSET;
            let mut own_action_hash = FNV_OFFSET;
            let mut own_commands_by_turn: Vec<(i32, Vec<String>)> = Vec::new();
            let mut states: Vec<StateSnapshot> = Vec::new();
            let mut turn_commands: Vec<(Vec<String>, Vec<String>)> = Vec::new();
            let mut done = false;

            let map_rows = if dump { build_map_rows(&game) } else { Vec::new() };
            if dump {
                states.push(StateSnapshot::capture(&game));
            }
            while !done {
                let opponent = 1 - seat;
                let view = res::game::GameState {
                    width: game.width,
                    height: game.height,
                    walkable: game.walkable.iter().copied().collect(),
                    shacks: [game.shacks[seat], game.shacks[opponent]],
                    inventories: [game.inventories[seat], game.inventories[opponent]],
                    units: game
                        .units
                        .iter()
                        .map(|unit| res::game::Unit {
                            id: unit.id,
                            player: usize::from(unit.player as usize != seat),
                            cell: unit.pos(),
                            stats: res::game::Stats {
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
                        .map(|plant| res::game::Plant {
                            kind: res::game::PlantKind::parse(&plant.plant_type)
                                .expect("known plant type"),
                            cell: plant.pos(),
                            size: plant.size,
                            health: plant.health,
                            fruits: plant.fruits,
                            cooldown: plant.cooldown,
                        })
                        .collect(),
                    scores: [game.scores[seat], game.scores[opponent]],
                    turn: game.turn,
                    next_id: game.next_id,
                    iron: game.iron.iter().copied().collect(),
                    water: game.water.iter().copied().collect(),
                };
                let ours_commands = ours.commands(&view);
                let theirs_commands = theirs.commands(&game, opponent);
                let commands = if seat == 0 {
                    [ours_commands.clone(), theirs_commands]
                } else {
                    [theirs_commands, ours_commands.clone()]
                };
                own_commands_by_turn.push((game.turn, own_command_snapshot(&ours_commands)));
                if dump {
                    turn_commands.push((commands[0].clone(), commands[1].clone()));
                }
                for (player, player_commands) in commands.iter().enumerate() {
                    action_hash = fnv1a(action_hash, &[player as u8]);
                    for command in player_commands {
                        action_hash = fnv1a(action_hash, command.as_bytes());
                        action_hash = fnv1a(action_hash, &[0]);
                    }
                    action_hash = fnv1a(action_hash, &[255]);
                }
                for command in &ours_commands {
                    own_action_hash = fnv1a(own_action_hash, command.as_bytes());
                    own_action_hash = fnv1a(own_action_hash, &[0]);
                }
                own_action_hash = fnv1a(own_action_hash, &[255]);

                step(&mut game, &commands[0], &commands[1]);
                if dump {
                    states.push(StateSnapshot::capture(&game));
                }
                done = game.turn > MACRO_TOTAL_TURNS || has_stalled(&game, &mut turns_until_end);
            }

            SideResult {
                done,
                turn: game.turn,
                own_score: game.scores[seat],
                opponent_score: game.scores[1 - seat],
                action_hash,
                own_action_hash,
                state_hash: canonical_state_hash(&game),
                own_workers_final: game
                    .units
                    .iter()
                    .filter(|unit| unit.player as usize == seat)
                    .count(),
                own_commands_by_turn,
                map_rows,
                states,
                turn_commands,
            }
        }
    };
}

define_play_side!(play_control, control_resident);
define_play_side!(play_candidate, resident_policy);

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

struct Row {
    task: Task,
    control: RowSide,
    candidate: RowSide,
    first_divergence_turn: Option<i32>,
}

struct RowSide {
    done: bool,
    turn: i32,
    own_score: i32,
    opponent_score: i32,
    action_hash: u64,
    own_action_hash: u64,
    state_hash: u64,
    own_workers_final: usize,
}

impl From<&SideResult> for RowSide {
    fn from(side: &SideResult) -> Self {
        RowSide {
            done: side.done,
            turn: side.turn,
            own_score: side.own_score,
            opponent_score: side.opponent_score,
            action_hash: side.action_hash,
            own_action_hash: side.own_action_hash,
            state_hash: side.state_hash,
            own_workers_final: side.own_workers_final,
        }
    }
}

fn find_divergence(control: &SideResult, candidate: &SideResult) -> Option<i32> {
    let common = control
        .own_commands_by_turn
        .len()
        .min(candidate.own_commands_by_turn.len());
    for index in 0..common {
        let (turn_c, commands_c) = &control.own_commands_by_turn[index];
        let (_turn_d, commands_d) = &candidate.own_commands_by_turn[index];
        if commands_c != commands_d {
            return Some(*turn_c);
        }
    }
    None
}

// ---------------------------------------------------------------------------
// Minimal hand-rolled JSON (no serde in this crate); every string we emit is
// either a fixed vocabulary word (plant type) or a referee command built from
// ASCII verbs/ints/spaces, so escaping only needs to cover '"' and '\' defensively.
// ---------------------------------------------------------------------------

fn json_escape_into(buf: &mut String, s: &str) {
    buf.push('"');
    for ch in s.chars() {
        match ch {
            '"' => buf.push_str("\\\""),
            '\\' => buf.push_str("\\\\"),
            '\n' => buf.push_str("\\n"),
            _ => buf.push(ch),
        }
    }
    buf.push('"');
}

fn write_unit(buf: &mut String, unit: &Unit) {
    write!(
        buf,
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
    .expect("write unit");
}

fn write_plant(buf: &mut String, plant: &Plant) {
    buf.push('[');
    write!(buf, "{},{},", plant.x, plant.y).expect("write plant xy");
    json_escape_into(buf, &plant.plant_type);
    write!(
        buf,
        ",{},{},{},{}]",
        plant.size, plant.health, plant.fruits, plant.cooldown
    )
    .expect("write plant rest");
}

fn write_state(buf: &mut String, state: &StateSnapshot) {
    buf.push_str("{\"u\":[");
    for (index, unit) in state.units.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        write_unit(buf, unit);
    }
    buf.push_str("],\"p\":[");
    for (index, plant) in state.plants.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        write_plant(buf, plant);
    }
    write!(
        buf,
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
    .expect("write banks");
}

fn write_commands(buf: &mut String, commands: &[String]) {
    buf.push('[');
    for (index, command) in commands.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        json_escape_into(buf, command);
    }
    buf.push(']');
}

fn write_trajectory_line(
    task: &Task,
    arm: &str,
    side: &SideResult,
    own_score: i32,
    opponent_score: i32,
) -> String {
    let (score0, score1) = if task.seat == 0 {
        (own_score, opponent_score)
    } else {
        (opponent_score, own_score)
    };
    let mut buf = String::with_capacity(4096);
    write!(
        buf,
        "{{\"seed\":{},\"seat\":{},\"opp\":{},\"opp_name\":",
        task.map_seed, task.seat, task.opponent
    )
    .expect("write header");
    json_escape_into(&mut buf, MacroOpponentMode::from_index(task.opponent).label());
    write!(buf, ",\"arm\":").expect("write arm key");
    json_escape_into(&mut buf, arm);
    buf.push_str(",\"map_rows\":[");
    for (index, row) in side.map_rows.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        json_escape_into(&mut buf, row);
    }
    buf.push(']');
    write!(
        buf,
        ",\"turns\":{},\"scores\":[{},{}],\"states\":[",
        side.turn_commands.len(),
        score0,
        score1
    )
    .expect("write turns/scores");
    for (index, state) in side.states.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        write_state(&mut buf, state);
    }
    buf.push_str("],\"c0\":[");
    for (index, (c0, _)) in side.turn_commands.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        write_commands(&mut buf, c0);
    }
    buf.push_str("],\"c1\":[");
    for (index, (_, c1)) in side.turn_commands.iter().enumerate() {
        if index > 0 {
            buf.push(',');
        }
        write_commands(&mut buf, c1);
    }
    buf.push_str("]}\n");
    buf
}

fn play(
    task: Task,
    dump: bool,
    control_writer: Option<&Mutex<BufWriter<File>>>,
    candidate_writer: Option<&Mutex<BufWriter<File>>>,
) -> Row {
    let control = play_control(task.map_seed, task.seat, task.opponent, dump);
    let candidate = play_candidate(task.map_seed, task.seat, task.opponent, dump);
    let first_divergence_turn = find_divergence(&control, &candidate);
    if dump {
        if let Some(writer) = control_writer {
            let line = write_trajectory_line(
                &task,
                "control",
                &control,
                control.own_score,
                control.opponent_score,
            );
            writer.lock().expect("control ndjson lock").write_all(line.as_bytes()).expect("write control ndjson");
        }
        if first_divergence_turn.is_some() {
            if let Some(writer) = candidate_writer {
                let line = write_trajectory_line(
                    &task,
                    "candidate",
                    &candidate,
                    candidate.own_score,
                    candidate.opponent_score,
                );
                writer
                    .lock()
                    .expect("candidate ndjson lock")
                    .write_all(line.as_bytes())
                    .expect("write candidate ndjson");
            }
        }
    }
    Row {
        task,
        control: RowSide::from(&control),
        candidate: RowSide::from(&candidate),
        first_divergence_turn,
    }
}

fn write_rows(output: &str, rows: &[Row]) {
    let mut writer = BufWriter::new(File::create(output).expect("create D174a output"));
    writeln!(
        writer,
        "map_seed\tseat\topponent_index\topponent\t\
control_done\tcontrol_turn\tcontrol_own_score\tcontrol_opponent_score\tcontrol_margin\t\
control_action_hash\tcontrol_own_action_hash\tcontrol_state_hash\tcontrol_own_workers_final\t\
candidate_done\tcandidate_turn\tcandidate_own_score\tcandidate_opponent_score\tcandidate_margin\t\
candidate_action_hash\tcandidate_own_action_hash\tcandidate_state_hash\tcandidate_own_workers_final\t\
first_divergence_turn\tactivated"
    )
    .expect("write D174a header");
    for row in rows {
        let values = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            row.task.opponent.to_string(),
            MacroOpponentMode::from_index(row.task.opponent)
                .label()
                .to_string(),
            u8::from(row.control.done).to_string(),
            row.control.turn.to_string(),
            row.control.own_score.to_string(),
            row.control.opponent_score.to_string(),
            (row.control.own_score - row.control.opponent_score).to_string(),
            row.control.action_hash.to_string(),
            row.control.own_action_hash.to_string(),
            row.control.state_hash.to_string(),
            row.control.own_workers_final.to_string(),
            u8::from(row.candidate.done).to_string(),
            row.candidate.turn.to_string(),
            row.candidate.own_score.to_string(),
            row.candidate.opponent_score.to_string(),
            (row.candidate.own_score - row.candidate.opponent_score).to_string(),
            row.candidate.action_hash.to_string(),
            row.candidate.own_action_hash.to_string(),
            row.candidate.state_hash.to_string(),
            row.candidate.own_workers_final.to_string(),
            row.first_divergence_turn
                .map(|turn| turn.to_string())
                .unwrap_or_default(),
            u8::from(row.first_divergence_turn.is_some()).to_string(),
        ];
        writeln!(writer, "{}", values.join("\t")).expect("write D174a row");
    }
}

fn parse<T: std::str::FromStr>(text: &str, what: &str) -> T {
    text.parse()
        .unwrap_or_else(|_| panic!("invalid {what}: {text}"))
}

fn main() {
    if let Ok(spec) = std::env::var("D174A_DEBUG_TASK") {
        let parts: Vec<i64> = spec.split(',').map(|p| p.parse().expect("seed,seat,opponent")).collect();
        let task = Task {
            map_seed: parts[0],
            seat: parts[1] as usize,
            opponent: parts[2] as usize,
        };
        let row = play(task, false, None, None);
        eprintln!(
            "control: done={} turn={} score={}/{}",
            row.control.done, row.control.turn, row.control.own_score, row.control.opponent_score
        );
        eprintln!(
            "candidate: done={} turn={} score={}/{}",
            row.candidate.done, row.candidate.turn, row.candidate.own_score, row.candidate.opponent_score
        );
        eprintln!("first_divergence_turn={:?}", row.first_divergence_turn);
        return;
    }
    let args: Vec<_> = std::env::args().collect();
    assert!(
        args.len() == 5 || args.len() == 7,
        "usage: d174a_opportunistic_mining_panel START_SEED MAPS OUTPUT THREADS \
[TRAJ_CONTROL TRAJ_CANDIDATE]"
    );
    let start_seed: i64 = parse(&args[1], "start seed");
    let maps: i64 = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    assert!(maps > 0 && threads > 0);
    assert!(
        start_seed >= FRESH_START_SEED && start_seed + maps <= FRESH_START_SEED + FRESH_MAP_COUNT,
        "D174a panel is confined to the declared fresh range 9,855,000-9,855,127"
    );
    let dump = args.len() == 7;
    let control_writer: Option<Mutex<BufWriter<File>>> = if dump {
        Some(Mutex::new(BufWriter::new(
            File::create(&args[5]).expect("create control trajectory ndjson"),
        )))
    } else {
        None
    };
    let candidate_writer: Option<Mutex<BufWriter<File>>> = if dump {
        Some(Mutex::new(BufWriter::new(
            File::create(&args[6]).expect("create candidate trajectory ndjson"),
        )))
    } else {
        None
    };

    let work: Vec<Task> = (start_seed..start_seed + maps)
        .flat_map(|map_seed| {
            (0..2usize).flat_map(move |seat| {
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
    let rows: Arc<Mutex<Vec<Row>>> = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
    let control_writer = Arc::new(control_writer);
    let candidate_writer = Arc::new(candidate_writer);
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            let control_writer = Arc::clone(&control_writer);
            let candidate_writer = Arc::clone(&candidate_writer);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(task) = work.get(index).copied() else {
                    break;
                };
                let row = play(
                    task,
                    dump,
                    control_writer.as_ref().as_ref(),
                    candidate_writer.as_ref().as_ref(),
                );
                rows.lock().expect("D174a row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D174a worker thread");
    }
    if let Some(writer) = control_writer.as_ref() {
        writer.lock().expect("flush control ndjson").flush().expect("flush control ndjson");
    }
    if let Some(writer) = candidate_writer.as_ref() {
        writer.lock().expect("flush candidate ndjson").flush().expect("flush candidate ndjson");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D174a rows")
        .into_inner()
        .expect("D174a rows lock");
    rows.sort_by_key(|row| (row.task.map_seed, row.task.seat, row.task.opponent));
    let activated = rows.iter().filter(|row| row.first_divergence_turn.is_some()).count();
    write_rows(output, &rows);
    eprintln!(
        "saved {} D174a rows ({} activated) with {} workers in {:.3}s to {}",
        rows.len(),
        activated,
        threads.min(work.len()),
        started.elapsed().as_secs_f64(),
        output,
    );
}
