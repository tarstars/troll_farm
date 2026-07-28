//! D171a oscillation-breaker fresh panel: paired CONTROL (frozen pre-fix resident,
//! `git show HEAD:rust/src/bin/yamo_orchard_live.rs` at the start of the D171a session,
//! byte-identical copy at `rust/src/d171a_control_resident_snapshot.rs`) vs CANDIDATE
//! (the dev copy `rust/src/bin/yamo_orchard_live.rs`, reused automatically via the
//! existing `#[path]` library alias `troll_farm::resident_policy`) across the fresh panel
//! of 128 maps x 8 opponent families x 2 seats declared in
//! data/analysis/live-agent-6553250/d171a-oscillation-breaker-protocol-2026-07-28.md.
//!
//! Opponent=Resident always instantiates from the CONTROL snapshot on both sides of a
//! pair, so a pair only ever differs in our own bot's code (paired = same
//! map/seat/opponent, opponent identity+behavior held constant).
//!
//! Each task plays two independent, fully deterministic games (control, candidate) from
//! the same seed. Because both are deterministic given identical inputs, the two
//! trajectories are provably byte-identical up to the first turn our own bot's emitted
//! command differs -- so a straightforward post-hoc, turn-indexed comparison of the two
//! independently-collected own-side command histories is equivalent to a live lockstep
//! comparison, without the complexity of interleaving two differently-typed bots in one
//! loop.

#[path = "../d171a_control_resident_snapshot.rs"]
mod control_resident;

use std::collections::BTreeMap;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step};
use troll_farm::game::official_mapgen::generate_official;
use troll_farm::game::state::{Cell, GameState};
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
const FRESH_START_SEED: i64 = 9_853_000;
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

/// Same predicate B3.2/B3.4 use: `positions[k]==positions[k-2] && positions[k]!=positions[k-1]`.
/// A "run" is a maximal streak of consecutive turns satisfying the predicate; `run_len` is
/// the count of turns the predicate holds within that streak (2 less than the streak's own
/// turn-duration, since the first two turns of any window establish history without yet
/// confirming a repeat -- matches the B3.4 table exactly, e.g. game 896350846: 133-turn
/// window, run_len_metric 131).
#[derive(Default)]
struct RunTracker {
    one_ago: Option<Cell>,
    two_ago: Option<Cell>,
    streak: u32,
    run_5_9: u32,
    run_ge10: u32,
    run_max: u32,
    ever_streak_ge3: bool,
}

impl RunTracker {
    fn close_streak(&mut self) {
        if self.streak >= 10 {
            self.run_ge10 += 1;
        } else if self.streak >= 5 {
            self.run_5_9 += 1;
        }
        self.run_max = self.run_max.max(self.streak);
        self.streak = 0;
    }

    fn observe(&mut self, current: Cell) {
        let is_reversal = self.two_ago == Some(current) && self.one_ago != Some(current);
        if is_reversal {
            self.streak = self.streak.saturating_add(1);
            if self.streak >= 3 {
                self.ever_streak_ge3 = true;
            }
        } else {
            self.close_streak();
        }
        self.two_ago = self.one_ago;
        self.one_ago = Some(current);
    }
}

#[derive(Default)]
struct RunSummary {
    run_5_9: u32,
    run_ge10: u32,
    run_max: u32,
    ever_streak_ge3: bool,
}

fn summarize_trackers(trackers: &BTreeMap<i32, RunTracker>) -> RunSummary {
    let mut summary = RunSummary::default();
    for tracker in trackers.values() {
        summary.run_5_9 += tracker.run_5_9;
        summary.run_ge10 += tracker.run_ge10;
        summary.run_max = summary.run_max.max(tracker.run_max);
        summary.ever_streak_ge3 |= tracker.ever_streak_ge3;
    }
    summary
}

/// Per-turn snapshot of which own unit ids currently have a confirmed reversal streak
/// >= 3 (the fix's own arm floor), tracked on this side's own trajectory.
type ArmedByTurn = Vec<(i32, Vec<i32>)>;

struct SideResult {
    done: bool,
    turn: i32,
    own_score: i32,
    opponent_score: i32,
    action_hash: u64,
    own_action_hash: u64,
    state_hash: u64,
    own_workers_final: usize,
    run: RunSummary,
    own_commands_by_turn: Vec<(i32, Vec<String>)>,
    armed_by_turn: ArmedByTurn,
}

/// Canonicalize a turn's own-side command list so equality is order-independent
/// (unit iteration order is already deterministic in practice, but this makes the
/// divergence check robust to that detail rather than relying on it).
fn own_command_snapshot(commands: &[String]) -> Vec<String> {
    let mut sorted: Vec<String> = commands.to_vec();
    sorted.sort();
    sorted
}

macro_rules! define_play_side {
    ($fn_name:ident, $resident_mod:path) => {
        fn $fn_name(map_seed: i64, seat: usize, opponent_index: usize) -> SideResult {
            use $resident_mod as res;
            use res::bot::Bot as _;

            let mut game = generate_official(map_seed);
            let mut ours = res::bot::moisan::SecureOrchardBot::new();
            let mut theirs = Opponent::new(MacroOpponentMode::from_index(opponent_index));
            let mut turns_until_end = 0i32;
            let mut action_hash = FNV_OFFSET;
            let mut own_action_hash = FNV_OFFSET;
            let mut trackers: BTreeMap<i32, RunTracker> = BTreeMap::new();
            let mut own_commands_by_turn: Vec<(i32, Vec<String>)> = Vec::new();
            let mut armed_by_turn: ArmedByTurn = Vec::new();
            let mut done = false;

            let debug = std::env::var("D171A_DEBUG").is_ok();
            while !done {
                for unit in game.units.iter().filter(|unit| unit.player as usize == seat) {
                    trackers.entry(unit.id).or_default().observe(unit.pos());
                }
                let armed_ids: Vec<i32> = trackers
                    .iter()
                    .filter(|(_, tracker)| tracker.streak >= 3)
                    .map(|(id, _)| *id)
                    .collect();
                if debug {
                    let positions: Vec<String> = game
                        .units
                        .iter()
                        .filter(|unit| unit.player as usize == seat)
                        .map(|unit| format!("{}@{:?}", unit.id, unit.pos()))
                        .collect();
                    eprintln!(
                        "[{}] turn={} pos={:?} armed={:?}",
                        stringify!($fn_name),
                        game.turn,
                        positions,
                        armed_ids
                    );
                }
                armed_by_turn.push((game.turn, armed_ids));

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
                if debug {
                    eprintln!("[{}] turn={} cmd={:?}", stringify!($fn_name), game.turn, ours_commands);
                }
                let theirs_commands = theirs.commands(&game, opponent);
                let commands = if seat == 0 {
                    [ours_commands.clone(), theirs_commands]
                } else {
                    [theirs_commands, ours_commands.clone()]
                };
                own_commands_by_turn.push((game.turn, own_command_snapshot(&ours_commands)));
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
                run: summarize_trackers(&trackers),
                own_commands_by_turn,
                armed_by_turn,
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
    purity_violation: bool,
    armed_unit_ids_at_divergence: String,
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
    run_5_9: u32,
    run_ge10: u32,
    run_max: u32,
    ever_streak_ge3: bool,
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
            run_5_9: side.run.run_5_9,
            run_ge10: side.run.run_ge10,
            run_max: side.run.run_max,
            ever_streak_ge3: side.run.ever_streak_ge3,
        }
    }
}

fn find_divergence(control: &SideResult, candidate: &SideResult) -> (Option<i32>, Vec<i32>) {
    let common = control
        .own_commands_by_turn
        .len()
        .min(candidate.own_commands_by_turn.len());
    for index in 0..common {
        let (turn_c, commands_c) = &control.own_commands_by_turn[index];
        let (_turn_d, commands_d) = &candidate.own_commands_by_turn[index];
        if commands_c != commands_d {
            let armed: Vec<i32> = control
                .armed_by_turn
                .get(index)
                .map(|(_, ids)| ids.clone())
                .unwrap_or_default();
            return (Some(*turn_c), armed);
        }
    }
    (None, vec![])
}

fn play(task: Task) -> Row {
    let control = play_control(task.map_seed, task.seat, task.opponent);
    let candidate = play_candidate(task.map_seed, task.seat, task.opponent);
    let (first_divergence_turn, armed_ids) = find_divergence(&control, &candidate);
    // Purity is only meaningful while both sides are still on the byte-identical
    // trajectory (see the first_action_divergence discipline in
    // cgauto/opponent_crop_field_activation.py -- states after the first divergence are
    // not a candidate rollout). It is a violation only if a divergence occurred with no
    // armed unit recorded on the control side that same turn (i.e. neither of our own
    // units had a confirmed >=3 reversal streak at that point) -- the structural
    // command-purity safety net inside the fix already guarantees per-unit isolation;
    // this is the external, empirical corroboration.
    let purity_violation = first_divergence_turn.is_some() && armed_ids.is_empty();
    let row_control = RowSide::from(&control);
    let row_candidate = RowSide::from(&candidate);
    Row {
        task,
        control: row_control,
        candidate: row_candidate,
        first_divergence_turn,
        purity_violation,
        armed_unit_ids_at_divergence: armed_ids
            .iter()
            .map(i32::to_string)
            .collect::<Vec<_>>()
            .join(","),
    }
}

fn write_rows(output: &str, rows: &[Row]) {
    let mut writer = BufWriter::new(File::create(output).expect("create D171a output"));
    writeln!(
        writer,
        "map_seed\tseat\topponent_index\topponent\t\
control_done\tcontrol_turn\tcontrol_own_score\tcontrol_opponent_score\tcontrol_margin\t\
control_action_hash\tcontrol_own_action_hash\tcontrol_state_hash\tcontrol_own_workers_final\t\
control_run_5_9\tcontrol_run_ge10\tcontrol_run_max\tcontrol_ever_streak_ge3\t\
candidate_done\tcandidate_turn\tcandidate_own_score\tcandidate_opponent_score\tcandidate_margin\t\
candidate_action_hash\tcandidate_own_action_hash\tcandidate_state_hash\tcandidate_own_workers_final\t\
candidate_run_5_9\tcandidate_run_ge10\tcandidate_run_max\t\
first_divergence_turn\tpurity_violation\tarmed_unit_ids_at_divergence"
    )
    .expect("write D171a header");
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
            row.control.run_5_9.to_string(),
            row.control.run_ge10.to_string(),
            row.control.run_max.to_string(),
            u8::from(row.control.ever_streak_ge3).to_string(),
            u8::from(row.candidate.done).to_string(),
            row.candidate.turn.to_string(),
            row.candidate.own_score.to_string(),
            row.candidate.opponent_score.to_string(),
            (row.candidate.own_score - row.candidate.opponent_score).to_string(),
            row.candidate.action_hash.to_string(),
            row.candidate.own_action_hash.to_string(),
            row.candidate.state_hash.to_string(),
            row.candidate.own_workers_final.to_string(),
            row.candidate.run_5_9.to_string(),
            row.candidate.run_ge10.to_string(),
            row.candidate.run_max.to_string(),
            row.first_divergence_turn
                .map(|turn| turn.to_string())
                .unwrap_or_default(),
            u8::from(row.purity_violation).to_string(),
            row.armed_unit_ids_at_divergence.clone(),
        ];
        writeln!(writer, "{}", values.join("\t")).expect("write D171a row");
    }
}

fn parse<T: std::str::FromStr>(text: &str, what: &str) -> T {
    text.parse()
        .unwrap_or_else(|_| panic!("invalid {what}: {text}"))
}

fn main() {
    if let Ok(spec) = std::env::var("D171A_DEBUG_TASK") {
        let parts: Vec<i64> = spec.split(',').map(|p| p.parse().expect("seed,seat,opponent")).collect();
        let task = Task {
            map_seed: parts[0],
            seat: parts[1] as usize,
            opponent: parts[2] as usize,
        };
        let row = play(task);
        eprintln!(
            "control: done={} turn={} score={}/{} run5_9={} runge10={} runmax={}",
            row.control.done, row.control.turn, row.control.own_score, row.control.opponent_score,
            row.control.run_5_9, row.control.run_ge10, row.control.run_max
        );
        eprintln!(
            "candidate: done={} turn={} score={}/{} run5_9={} runge10={} runmax={}",
            row.candidate.done, row.candidate.turn, row.candidate.own_score, row.candidate.opponent_score,
            row.candidate.run_5_9, row.candidate.run_ge10, row.candidate.run_max
        );
        eprintln!(
            "first_divergence_turn={:?} purity_violation={} armed_at_divergence={}",
            row.first_divergence_turn, row.purity_violation, row.armed_unit_ids_at_divergence
        );
        return;
    }
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        5,
        "usage: d171a_oscillation_breaker_panel START_SEED MAPS OUTPUT THREADS"
    );
    let start_seed: i64 = parse(&args[1], "start seed");
    let maps: i64 = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    assert!(maps > 0 && threads > 0);
    assert!(
        start_seed >= FRESH_START_SEED && start_seed + maps <= FRESH_START_SEED + FRESH_MAP_COUNT,
        "D171a panel is confined to the declared fresh range 9,853,000-9,853,127"
    );

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
                let row = play(task);
                rows.lock().expect("D171a row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D171a worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D171a rows")
        .into_inner()
        .expect("D171a rows lock");
    rows.sort_by_key(|row| (row.task.map_seed, row.task.seat, row.task.opponent));
    write_rows(output, &rows);
    eprintln!(
        "saved {} D171a rows with {} workers in {:.3}s to {}",
        rows.len(),
        threads.min(work.len()),
        started.elapsed().as_secs_f64(),
        output,
    );
}
