//! A2-0b legacy/referee resident calibration panel.
//!
//! This runner is intentionally separate from every frozen historical runner. It compares
//! the unchanged legacy engine with `game::a2_referee_parity`, while using the same frozen
//! resident and eight standing opponent families as D173b.

#[path = "../d171a_control_resident_snapshot.rs"]
mod control_resident;

use std::collections::BTreeMap;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::a2_referee_parity::{self, LegalityReport, MovementRngStats};
use troll_farm::game::engine::{has_stalled, step as legacy_step};
use troll_farm::game::official_mapgen::generate_official;
use troll_farm::game::state::GameState;
use troll_farm::rl_macro::{MacroOpponentMode, MACRO_TOTAL_TURNS};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::legend_field_proxy::{LegendFieldProxyV2, LegendFieldProxyV2Config};
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::norxondor_native::NorxondorNative;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;

const FNV_OFFSET: u64 = 14_695_981_039_346_656_037;
const CALIBRATION_START: i64 = 9_854_000;
const CALIBRATION_MAPS: i64 = 128;

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

#[derive(Clone, Copy)]
enum Mode {
    Legacy,
    Referee,
}

struct SideResult {
    done: bool,
    turn: i32,
    own_score: i32,
    opponent_score: i32,
    action_hash: u64,
    state_hash: u64,
    own_workers_final: usize,
    state_hashes: Vec<u64>,
    legality: LegalityReport,
    movement_rng: MovementRngStats,
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

fn play(mode: Mode, map_seed: i64, seat: usize, opponent_index: usize) -> SideResult {
    use control_resident::bot::Bot as _;

    let mut legacy_game = generate_official(map_seed);
    let mut referee_game = a2_referee_parity::generate_official(map_seed);
    let mut legacy_validator = a2_referee_parity::generate_official(map_seed);
    let mut ours = control_resident::bot::moisan::SecureOrchardBot::new();
    let mut theirs = Opponent::new(MacroOpponentMode::from_index(opponent_index));
    let mut turns_until_end = 0;
    let mut action_hash = FNV_OFFSET;
    let mut state_hashes = Vec::new();
    let mut done = false;

    let initial = match mode {
        Mode::Legacy => &legacy_game,
        Mode::Referee => &referee_game.game,
    };
    state_hashes.push(canonical_state_hash(initial));

    while !done {
        let game = match mode {
            Mode::Legacy => &legacy_game,
            Mode::Referee => &referee_game.game,
        };
        let opponent = 1 - seat;
        let ours_commands = ours.commands(&control_view(game, seat));
        let theirs_commands = theirs.commands(game, opponent);
        let commands = if seat == 0 {
            [ours_commands, theirs_commands]
        } else {
            [theirs_commands, ours_commands]
        };
        action_hash = hash_commands(action_hash, &commands);

        match mode {
            Mode::Legacy => {
                legacy_validator.game = legacy_game.clone();
                a2_referee_parity::step(
                    &mut legacy_validator,
                    &commands[0],
                    &commands[1],
                );
                legacy_step(&mut legacy_game, &commands[0], &commands[1]);
                state_hashes.push(canonical_state_hash(&legacy_game));
                done = legacy_game.turn > MACRO_TOTAL_TURNS
                    || has_stalled(&legacy_game, &mut turns_until_end);
            }
            Mode::Referee => {
                a2_referee_parity::step(&mut referee_game, &commands[0], &commands[1]);
                state_hashes.push(canonical_state_hash(&referee_game.game));
                done = referee_game.game.turn > MACRO_TOTAL_TURNS
                    || has_stalled(&referee_game.game, &mut turns_until_end);
            }
        }
    }

    let (game, legality, movement_rng) = match mode {
        Mode::Legacy => (
            legacy_game,
            legacy_validator.legality,
            legacy_validator.movement_rng,
        ),
        Mode::Referee => (
            referee_game.game,
            referee_game.legality,
            referee_game.movement_rng,
        ),
    };
    SideResult {
        done,
        turn: game.turn,
        own_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        action_hash,
        state_hash: canonical_state_hash(&game),
        own_workers_final: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        state_hashes,
        legality,
        movement_rng,
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
    legacy: SideResult,
    referee: SideResult,
    first_state_divergence_turn: Option<usize>,
}

fn first_divergence(left: &[u64], right: &[u64]) -> Option<usize> {
    let common = left.len().min(right.len());
    for index in 0..common {
        if left[index] != right[index] {
            return Some(index);
        }
    }
    (left.len() != right.len()).then_some(common)
}

fn run_task(task: Task) -> Row {
    let legacy = play(Mode::Legacy, task.map_seed, task.seat, task.opponent);
    let referee = play(Mode::Referee, task.map_seed, task.seat, task.opponent);
    let first_state_divergence_turn =
        first_divergence(&legacy.state_hashes, &referee.state_hashes);
    Row {
        task,
        legacy,
        referee,
        first_state_divergence_turn,
    }
}

fn reason_counts(report: &LegalityReport) -> String {
    report
        .reason_counts()
        .into_iter()
        .map(|(reason, count)| format!("{reason}={count}"))
        .collect::<Vec<_>>()
        .join(",")
}

fn first_issue(report: &LegalityReport) -> String {
    report
        .issues
        .first()
        .map(|issue| {
            format!(
                "t{}:p{}:{}:{}:{}",
                issue.turn, issue.player, issue.phase, issue.reason, issue.command
            )
            .replace(['\t', '\n', '\r'], " ")
        })
        .unwrap_or_default()
}

fn side_fields(side: &SideResult) -> Vec<String> {
    vec![
        u8::from(side.done).to_string(),
        side.turn.to_string(),
        side.own_score.to_string(),
        side.opponent_score.to_string(),
        (side.own_score - side.opponent_score).to_string(),
        side.action_hash.to_string(),
        side.state_hash.to_string(),
        side.own_workers_final.to_string(),
        side.legality.commands_checked.to_string(),
        side.legality.issue_count().to_string(),
        reason_counts(&side.legality),
        first_issue(&side.legality),
        side.movement_rng.draws.to_string(),
        side.movement_rng.tied_draws.to_string(),
    ]
}

fn write_rows(output: &str, rows: &[Row]) {
    let mut writer = BufWriter::new(File::create(output).expect("create A2-0b output"));
    let side_header = |prefix: &str| {
        [
            "done",
            "turn",
            "own_score",
            "opponent_score",
            "margin",
            "action_hash",
            "state_hash",
            "own_workers_final",
            "commands_checked",
            "legality_issues",
            "legality_reason_counts",
            "first_legality_issue",
            "movement_rng_draws",
            "movement_tied_draws",
        ]
        .iter()
        .map(|field| format!("{prefix}_{field}"))
        .collect::<Vec<_>>()
        .join("\t")
    };
    writeln!(
        writer,
        "map_seed\tseat\topponent_index\topponent\t{}\t{}\tfirst_state_divergence_turn",
        side_header("legacy"),
        side_header("referee"),
    )
    .expect("write A2-0b header");
    for row in rows {
        let mut fields = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            row.task.opponent.to_string(),
            MacroOpponentMode::from_index(row.task.opponent)
                .label()
                .to_owned(),
        ];
        fields.extend(side_fields(&row.legacy));
        fields.extend(side_fields(&row.referee));
        fields.push(
            row.first_state_divergence_turn
                .map(|turn| turn.to_string())
                .unwrap_or_default(),
        );
        writeln!(writer, "{}", fields.join("\t")).expect("write A2-0b row");
    }
}

fn parse<T: std::str::FromStr>(text: &str, what: &str) -> T {
    text.parse()
        .unwrap_or_else(|_| panic!("invalid {what}: {text}"))
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        5,
        "usage: a2_0b_referee_parity START_SEED MAPS OUTPUT THREADS"
    );
    let start_seed: i64 = parse(&args[1], "start seed");
    let maps: i64 = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    assert!(maps > 0 && threads > 0);
    assert!(
        start_seed >= CALIBRATION_START
            && start_seed + maps <= CALIBRATION_START + CALIBRATION_MAPS,
        "A2-0b is confined to the consumed D173b calibration range"
    );

    let work: Vec<Task> = (start_seed..start_seed + maps)
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
    let rows = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let work = Arc::clone(&work);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(task) = work.get(index).copied() else {
                    break;
                };
                rows.lock()
                    .expect("A2-0b row lock")
                    .push(run_task(task));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("A2-0b worker thread");
    }

    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole A2-0b rows")
        .into_inner()
        .expect("A2-0b rows lock");
    rows.sort_by_key(|row| row.task);
    write_rows(output, &rows);

    let legacy_issues: usize = rows
        .iter()
        .map(|row| row.legacy.legality.issue_count())
        .sum();
    let referee_issues: usize = rows
        .iter()
        .map(|row| row.referee.legality.issue_count())
        .sum();
    let divergences = rows
        .iter()
        .filter(|row| row.first_state_divergence_turn.is_some())
        .count();
    let reason_totals = |legacy: bool| {
        let mut totals = BTreeMap::new();
        for row in &rows {
            let report = if legacy {
                &row.legacy.legality
            } else {
                &row.referee.legality
            };
            for (reason, count) in report.reason_counts() {
                *totals.entry(reason).or_insert(0usize) += count;
            }
        }
        totals
    };
    eprintln!(
        "saved {} A2-0b rows with {} workers in {:.3}s; divergences={}; \
legacy_issues={} {:?}; referee_issues={} {:?}",
        rows.len(),
        threads.min(work.len()),
        started.elapsed().as_secs_f64(),
        divergences,
        legacy_issues,
        reason_totals(true),
        referee_issues,
        reason_totals(false),
    );
}
