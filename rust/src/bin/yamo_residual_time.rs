//! Research-only residual MOVE search around the actual Yamo/Orchard resident.

#[path = "yamo_orchard_live.rs"]
mod yamo;

// The standalone resident addresses these modules through `crate::`.
pub use yamo::{bot, game};

use std::cell::RefCell;
use std::collections::{BTreeSet, HashMap};
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::Instant;

use troll_farm::game::engine::{has_stalled, step, WOOD};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::{Cell, GameState, Unit as EngineUnit};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::residual_search::movement_candidates;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const OPPONENTS: [&str; 8] = [
    "compact_gold",
    "gold_adaptive",
    "gold_elite",
    "mybot",
    "printer_bot",
    "sched_bot",
    "script_boss",
    "silver_boss",
];
const START_TURN: i32 = 80;
const SHORT_HORIZON: usize = 4;
const LONG_HORIZON: usize = 16;
const FINALISTS: usize = 4;
const MAX_CANDIDATES: usize = 14;
const MINIMUM_GAIN: f64 = 5.0;
const COMMIT_TURNS: usize = 8;
const TOTAL_TURNS: i32 = 300;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum CandidateScope {
    AllMoves,
    BankOnly,
}

impl CandidateScope {
    fn parse(value: &str) -> Self {
        match value {
            "all-moves" => Self::AllMoves,
            "bank-only" => Self::BankOnly,
            _ => panic!("unknown residual scope {value}"),
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::AllMoves => "all_moves",
            Self::BankOnly => "bank_only",
        }
    }
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

fn opponent(model: usize) -> Box<dyn Strategy> {
    match model {
        0 => Box::new(CompactGold::new()),
        1 => Box::new(GoldElite::adaptive()),
        2 => Box::new(GoldElite::new()),
        3 => Box::new(MyBot::new()),
        4 => Box::new(PrinterBot::new()),
        5 => Box::new(SchedBot::new()),
        6 => Box::new(ScriptBoss::new()),
        7 => Box::new(SilverBoss::new()),
        _ => unreachable!(),
    }
}

#[derive(Clone, Copy)]
enum RolloutModel {
    Gold,
    Scheduler,
}

fn rollout_opponent(model: RolloutModel) -> Box<dyn Strategy> {
    match model {
        RolloutModel::Gold => Box::new(GoldElite::new()),
        RolloutModel::Scheduler => Box::new(SchedBot::new()),
    }
}

fn manhattan(a: Cell, b: Cell) -> i32 {
    (a.0 - b.0).abs() + (a.1 - b.1).abs()
}

fn command_unit_id(command: &str) -> Option<i32> {
    let mut fields = command.split_whitespace();
    match fields.next()? {
        "MOVE" | "HARVEST" | "CHOP" | "DROP" | "MINE" | "PLANT" | "PICK" => {
            fields.next()?.parse().ok()
        }
        _ => None,
    }
}

fn move_target(command: &str) -> Option<(i32, Cell)> {
    let fields: Vec<_> = command.split_whitespace().collect();
    if fields.len() != 4 || fields[0] != "MOVE" {
        return None;
    }
    Some((
        fields[1].parse().ok()?,
        (fields[2].parse().ok()?, fields[3].parse().ok()?),
    ))
}

fn changed_move_targets(candidate: &[String], baseline: &[String]) -> Vec<(i32, Cell)> {
    candidate
        .iter()
        .filter_map(|command| move_target(command))
        .filter(|(unit_id, target)| {
            baseline
                .iter()
                .filter_map(|command| move_target(command))
                .find_map(|(control_id, control_target)| {
                    (control_id == *unit_id).then_some(control_target)
                })
                != Some(*target)
        })
        .collect()
}

fn replace_unit_command(commands: &[String], unit_id: i32, replacement: String) -> Vec<String> {
    let mut result = commands.to_vec();
    if let Some(index) = result
        .iter()
        .position(|command| command_unit_id(command) == Some(unit_id))
    {
        result[index] = replacement;
    } else {
        result.push(replacement);
    }
    result
}

fn carried_value(unit: &EngineUnit) -> i32 {
    unit.carry[..WOOD].iter().sum::<i32>() + 4 * unit.carry[WOOD]
}

fn state_value(game: &GameState, player: usize) -> f64 {
    let carry = |side: usize| {
        game.units
            .iter()
            .filter(|unit| unit.player as usize == side)
            .map(carried_value)
            .sum::<i32>()
    };
    (game.scores[player] - game.scores[1 - player]) as f64
        + 0.75 * (carry(player) - carry(1 - player)) as f64
}

fn rollout_value(
    root: &GameState,
    player: usize,
    root_commands: &[String],
    baseline_commands: &[String],
    mut continuation: SecureOrchardBot,
    horizon: usize,
    model: RolloutModel,
) -> f64 {
    let mut game = root.clone();
    let opponent = rollout_opponent(model);
    let mut commitments: Vec<_> = changed_move_targets(root_commands, baseline_commands)
        .into_iter()
        .map(|(unit_id, target)| (unit_id, target))
        .collect();
    let mut turns_until_end = 0;
    let remaining = (TOTAL_TURNS - root.turn + 1).max(0) as usize;
    for depth in 0..horizon.min(remaining) {
        let mut ours = if depth == 0 {
            root_commands.to_vec()
        } else {
            continuation.commands(&yamo_view(&game, player))
        };
        if depth > 0 {
            commitments.retain(|(unit_id, target)| {
                if depth > COMMIT_TURNS {
                    return false;
                }
                let Some(unit) = game
                    .units
                    .iter()
                    .find(|unit| unit.id == *unit_id && unit.player as usize == player)
                else {
                    return false;
                };
                let continuation_is_move = ours
                    .iter()
                    .find(|command| command_unit_id(command) == Some(*unit_id))
                    .is_some_and(|command| command.starts_with("MOVE "));
                let reached = unit.pos() == *target
                    || (*target == game.shacks[player] && manhattan(unit.pos(), *target) <= 1);
                if reached || !continuation_is_move {
                    return false;
                }
                ours = replace_unit_command(
                    &ours,
                    *unit_id,
                    format!("MOVE {} {} {}", unit_id, target.0, target.1),
                );
                true
            });
        }
        let opposition = opponent.decide(&game, 1 - player);
        if player == 0 {
            step(&mut game, &ours, &opposition);
        } else {
            step(&mut game, &opposition, &ours);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    state_value(&game, player)
}

fn robust_choice(deltas: &[[f64; 2]]) -> usize {
    let mut best = 0usize;
    let mut best_key = (MINIMUM_GAIN, MINIMUM_GAIN);
    for (index, delta) in deltas.iter().enumerate().skip(1) {
        let robust = delta[0].min(delta[1]);
        let mean = 0.5 * (delta[0] + delta[1]);
        if robust >= MINIMUM_GAIN && (robust, mean) > best_key {
            best = index;
            best_key = (robust, mean);
        }
    }
    best
}

#[derive(Clone, Copy)]
struct Commitment {
    target: Cell,
    expires: i32,
}

#[derive(Clone)]
struct AcceptedEvent {
    turn: i32,
    unit_id: i32,
    stats: (i32, i32, i32, i32),
    from: Cell,
    baseline_target: Cell,
    chosen_target: Cell,
    target_kind: String,
    target_size: i32,
    target_health: i32,
    target_fruits: i32,
    gold_delta: f64,
    scheduler_delta: f64,
}

impl AcceptedEvent {
    fn encode(&self) -> String {
        format!(
            "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{:.3},{:.3}",
            self.turn,
            self.unit_id,
            self.stats.0,
            self.stats.1,
            self.stats.2,
            self.stats.3,
            self.from.0,
            self.from.1,
            self.baseline_target.0,
            self.baseline_target.1,
            self.chosen_target.0,
            self.chosen_target.1,
            self.target_kind,
            self.target_size,
            self.target_health,
            self.target_fruits,
            self.gold_delta,
            self.scheduler_delta,
        )
    }
}

#[derive(Clone, Default)]
struct Telemetry {
    searches: usize,
    accepted: usize,
    failed_targets: usize,
    decision_us: Vec<u64>,
    accepted_events: Vec<AcceptedEvent>,
}

struct ResidentResidualBot {
    baseline: RefCell<SecureOrchardBot>,
    commitments: RefCell<HashMap<i32, Commitment>>,
    failed_targets: RefCell<BTreeSet<(i32, Cell)>>,
    telemetry: RefCell<Telemetry>,
    scope: CandidateScope,
}

impl ResidentResidualBot {
    fn new(scope: CandidateScope) -> Self {
        Self {
            baseline: RefCell::new(SecureOrchardBot::new()),
            commitments: RefCell::new(HashMap::new()),
            failed_targets: RefCell::new(BTreeSet::new()),
            telemetry: RefCell::new(Telemetry::default()),
            scope,
        }
    }

    fn telemetry(&self) -> Telemetry {
        let mut telemetry = self.telemetry.borrow().clone();
        telemetry.failed_targets = self.failed_targets.borrow().len();
        telemetry
    }

    fn decide(&self, game: &GameState, player: usize) -> Vec<String> {
        let started = Instant::now();
        let commands = self.decide_inner(game, player);
        self.telemetry
            .borrow_mut()
            .decision_us
            .push(started.elapsed().as_micros() as u64);
        commands
    }

    fn decide_inner(&self, game: &GameState, player: usize) -> Vec<String> {
        let baseline = self
            .baseline
            .borrow_mut()
            .commands(&yamo_view(game, player));
        if game.turn == 1 {
            self.commitments.borrow_mut().clear();
            self.failed_targets.borrow_mut().clear();
        }
        let economy_ready = game
            .units
            .iter()
            .any(|unit| unit.player as usize == player && unit.chop > 0 && unit.hp == 0);
        if game.turn < START_TURN || !economy_ready {
            return baseline;
        }

        let mut committed = baseline.clone();
        let mut active = false;
        let mut ended = false;
        let mut newly_failed = Vec::new();
        self.commitments.borrow_mut().retain(|unit_id, commitment| {
            let Some(unit) = game.units.iter().find(|unit| unit.id == *unit_id) else {
                return false;
            };
            let baseline_is_move = baseline
                .iter()
                .find(|command| command_unit_id(command) == Some(*unit_id))
                .is_some_and(|command| command.starts_with("MOVE "));
            let reached = unit.pos() == commitment.target
                || (commitment.target == game.shacks[player]
                    && manhattan(unit.pos(), commitment.target) <= 1);
            if !baseline_is_move {
                ended = true;
                return false;
            }
            if game.turn > commitment.expires || reached {
                newly_failed.push((*unit_id, commitment.target));
                ended = true;
                return false;
            }
            committed = replace_unit_command(
                &committed,
                *unit_id,
                format!(
                    "MOVE {} {} {}",
                    unit_id, commitment.target.0, commitment.target.1
                ),
            );
            active = true;
            true
        });
        self.failed_targets.borrow_mut().extend(newly_failed);
        if active {
            return committed;
        }
        if ended {
            return baseline;
        }

        let mut all = movement_candidates(game, player, &baseline, MAX_CANDIDATES);
        if self.scope == CandidateScope::BankOnly {
            all.retain(|commands| {
                commands == &baseline
                    || changed_move_targets(commands, &baseline)
                        .iter()
                        .all(|(_, target)| *target == game.shacks[player])
            });
        }
        let failed = self.failed_targets.borrow();
        all.retain(|commands| {
            commands == &baseline
                || changed_move_targets(commands, &baseline)
                    .iter()
                    .all(|target| !failed.contains(target))
        });
        drop(failed);
        if all.len() <= 1 {
            return baseline;
        }
        self.telemetry.borrow_mut().searches += 1;
        let continuation = self.baseline.borrow().clone();
        let mut screened: Vec<(f64, usize)> = all
            .iter()
            .enumerate()
            .map(|(index, commands)| {
                (
                    rollout_value(
                        game,
                        player,
                        commands,
                        &baseline,
                        continuation.clone(),
                        SHORT_HORIZON,
                        RolloutModel::Gold,
                    ),
                    index,
                )
            })
            .collect();
        screened.sort_by(|left, right| {
            right
                .0
                .total_cmp(&left.0)
                .then_with(|| left.1.cmp(&right.1))
        });
        let mut finalists: Vec<_> = screened
            .iter()
            .take(FINALISTS)
            .map(|(_, index)| *index)
            .collect();
        if !finalists.contains(&0) {
            finalists.push(0);
        }
        finalists.sort_unstable();
        finalists.dedup();

        let baseline_values = [
            rollout_value(
                game,
                player,
                &baseline,
                &baseline,
                continuation.clone(),
                LONG_HORIZON,
                RolloutModel::Gold,
            ),
            rollout_value(
                game,
                player,
                &baseline,
                &baseline,
                continuation.clone(),
                LONG_HORIZON,
                RolloutModel::Scheduler,
            ),
        ];
        let mut deltas = vec![[f64::NEG_INFINITY; 2]; finalists.len()];
        for (slot, &index) in finalists.iter().enumerate() {
            if index == 0 {
                deltas[slot] = [0.0, 0.0];
                continue;
            }
            deltas[slot][0] = rollout_value(
                game,
                player,
                &all[index],
                &baseline,
                continuation.clone(),
                LONG_HORIZON,
                RolloutModel::Gold,
            ) - baseline_values[0];
            if deltas[slot][0] >= MINIMUM_GAIN {
                deltas[slot][1] = rollout_value(
                    game,
                    player,
                    &all[index],
                    &baseline,
                    continuation.clone(),
                    LONG_HORIZON,
                    RolloutModel::Scheduler,
                ) - baseline_values[1];
            }
        }
        let chosen_slot = robust_choice(&deltas);
        let chosen = finalists[chosen_slot];
        if chosen != 0 {
            let changed = changed_move_targets(&all[chosen], &baseline);
            let mut telemetry = self.telemetry.borrow_mut();
            telemetry.accepted += 1;
            for (unit_id, target) in &changed {
                let unit = game
                    .units
                    .iter()
                    .find(|unit| unit.id == *unit_id)
                    .expect("chosen unit");
                let baseline_target = baseline
                    .iter()
                    .filter_map(|command| move_target(command))
                    .find_map(|(id, cell)| (id == *unit_id).then_some(cell))
                    .expect("changed command has baseline MOVE");
                let plant = game.plants.iter().find(|plant| plant.pos() == *target);
                let target_kind = if let Some(plant) = plant {
                    format!("TREE_{}", plant.plant_type)
                } else if *target == game.shacks[player] {
                    "SHACK".to_string()
                } else if game.iron.contains(target) {
                    "IRON".to_string()
                } else {
                    "CELL".to_string()
                };
                telemetry.accepted_events.push(AcceptedEvent {
                    turn: game.turn,
                    unit_id: *unit_id,
                    stats: (unit.ms, unit.cc, unit.hp, unit.chop),
                    from: unit.pos(),
                    baseline_target,
                    chosen_target: *target,
                    target_kind,
                    target_size: plant.map_or(0, |plant| plant.size),
                    target_health: plant.map_or(0, |plant| plant.health),
                    target_fruits: plant.map_or(0, |plant| plant.fruits),
                    gold_delta: deltas[chosen_slot][0],
                    scheduler_delta: deltas[chosen_slot][1],
                });
            }
            drop(telemetry);
            for (unit_id, target) in changed {
                self.commitments.borrow_mut().insert(
                    unit_id,
                    Commitment {
                        target,
                        expires: game.turn + COMMIT_TURNS as i32,
                    },
                );
            }
        }
        all[chosen].clone()
    }
}

#[derive(Clone, Copy)]
struct Outcome {
    own_score: i32,
    opponent_score: i32,
    workers: usize,
    terminal_turn: i32,
}

fn control_game(initial: &GameState, seat: usize, model: usize) -> Outcome {
    let mut game = initial.clone();
    let mut ours = SecureOrchardBot::new();
    let theirs = opponent(model);
    let mut turns_until_end = 0;
    while game.turn <= TOTAL_TURNS {
        let commands = ours.commands(&yamo_view(&game, seat));
        let opposition = theirs.decide(&game, 1 - seat);
        if seat == 0 {
            step(&mut game, &commands, &opposition);
        } else {
            step(&mut game, &opposition, &commands);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    Outcome {
        own_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        terminal_turn: game.turn,
    }
}

fn candidate_game(
    initial: &GameState,
    seat: usize,
    model: usize,
    scope: CandidateScope,
) -> (Outcome, Telemetry) {
    let mut game = initial.clone();
    let ours = ResidentResidualBot::new(scope);
    let theirs = opponent(model);
    let mut turns_until_end = 0;
    while game.turn <= TOTAL_TURNS {
        let commands = ours.decide(&game, seat);
        let opposition = theirs.decide(&game, 1 - seat);
        if seat == 0 {
            step(&mut game, &commands, &opposition);
        } else {
            step(&mut game, &opposition, &commands);
        }
        if has_stalled(&game, &mut turns_until_end) {
            break;
        }
    }
    let outcome = Outcome {
        own_score: game.scores[seat],
        opponent_score: game.scores[1 - seat],
        workers: game
            .units
            .iter()
            .filter(|unit| unit.player as usize == seat)
            .count(),
        terminal_turn: game.turn,
    };
    (outcome, ours.telemetry())
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
    model: usize,
    scope: CandidateScope,
}

struct ResultRow {
    task: Task,
    control: Outcome,
    candidate: Outcome,
    telemetry: Telemetry,
    elapsed_us: u128,
}

fn run_task(task: Task) -> ResultRow {
    let started = Instant::now();
    let initial = generate_bronze(task.seed);
    let control = control_game(&initial, task.seat, task.model);
    let (candidate, telemetry) = candidate_game(&initial, task.seat, task.model, task.scope);
    ResultRow {
        task,
        control,
        candidate,
        telemetry,
        elapsed_us: started.elapsed().as_micros(),
    }
}

fn percentile(samples: &[u64], fraction: f64) -> u64 {
    samples[((samples.len() - 1) as f64 * fraction).round() as usize]
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let seeds = args
        .get(1)
        .and_then(|value| value.parse().ok())
        .unwrap_or(5);
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "yamo-residual-smoke.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(16)
        .max(1);
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse().ok())
        .unwrap_or(0);
    let scope = CandidateScope::parse(args.get(5).map_or("all-moves", String::as_str));
    let tasks: Vec<_> = (seed_start..seed_start + seeds)
        .flat_map(|seed| {
            (0..OPPONENTS.len()).flat_map(move |model| {
                (0..2).map(move |seat| Task {
                    seed,
                    seat,
                    model,
                    scope,
                })
            })
        })
        .collect();
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let mut rows = std::thread::scope(|scope| {
        let handles: Vec<_> = (0..threads)
            .map(|_| {
                let tasks = Arc::clone(&tasks);
                let next = Arc::clone(&next);
                scope.spawn(move || {
                    let mut local = Vec::new();
                    loop {
                        let index = next.fetch_add(1, Ordering::Relaxed);
                        if index >= tasks.len() {
                            break;
                        }
                        local.push(run_task(tasks[index]));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("residual worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| (row.task.seed, row.task.model, row.task.seat));
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create output"));
    writeln!(writer, "seed\tseat\topponent\tprofile\tcontrol_margin\tcandidate_margin\tmargin_delta\tcontrol_score\tcandidate_score\tscore_delta\tcontrol_opponent_score\tcandidate_opponent_score\tcontrol_workers\tcandidate_workers\tcontrol_terminal_turn\tcandidate_terminal_turn\tsearches\taccepted\tfailed_targets\tmean_decision_us\tp95_decision_us\tmax_decision_us\tover_50ms\taccepted_events\tdecision_samples_us\tscenario_elapsed_us").expect("write header");
    let mut all_samples = Vec::new();
    let mut accepted = 0usize;
    for row in rows {
        let mut samples = row.telemetry.decision_us.clone();
        samples.sort_unstable();
        let mean = samples.iter().sum::<u64>() as f64 / samples.len() as f64;
        let p95 = percentile(&samples, 0.95);
        let maximum = *samples.last().expect("decision samples");
        let over = samples.iter().filter(|sample| **sample > 50_000).count();
        all_samples.extend(samples.iter().copied());
        accepted += row.telemetry.accepted;
        let control_margin = row.control.own_score - row.control.opponent_score;
        let candidate_margin = row.candidate.own_score - row.candidate.opponent_score;
        let encoded = row
            .telemetry
            .decision_us
            .iter()
            .map(u64::to_string)
            .collect::<Vec<_>>()
            .join(",");
        let events = row
            .telemetry
            .accepted_events
            .iter()
            .map(AcceptedEvent::encode)
            .collect::<Vec<_>>()
            .join(";");
        writeln!(writer, "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.3}\t{}\t{}\t{}\t{}\t{}\t{}", row.task.seed, row.task.seat, OPPONENTS[row.task.model], row.task.scope.label(), control_margin, candidate_margin, candidate_margin-control_margin, row.control.own_score, row.candidate.own_score, row.candidate.own_score-row.control.own_score, row.control.opponent_score, row.candidate.opponent_score, row.control.workers, row.candidate.workers, row.control.terminal_turn, row.candidate.terminal_turn, row.telemetry.searches, row.telemetry.accepted, row.telemetry.failed_targets, mean, p95, maximum, over, events, encoded, row.elapsed_us).expect("write row");
    }
    all_samples.sort_unstable();
    eprintln!(
        "saved {} scenarios, {} accepted deviations, decision p95 {:.3} ms, max {:.3} ms to {}",
        tasks.len(),
        accepted,
        percentile(&all_samples, 0.95) as f64 / 1000.0,
        all_samples.last().copied().unwrap_or(0) as f64 / 1000.0,
        output,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn turn_one_is_exact_resident_control() {
        let game = generate_bronze(0);
        let residual = ResidentResidualBot::new(CandidateScope::AllMoves);
        let mut control = SecureOrchardBot::new();
        assert_eq!(
            residual.decide(&game, 0),
            control.commands(&yamo_view(&game, 0))
        );
    }

    #[test]
    fn movement_library_keeps_control_first_and_training_unchanged() {
        let game = generate_bronze(3);
        let mut control = SecureOrchardBot::new();
        let commands = control.commands(&yamo_view(&game, 0));
        let candidates = movement_candidates(&game, 0, &commands, MAX_CANDIDATES);
        assert_eq!(candidates[0], commands);
        let train = commands
            .iter()
            .find(|command| command.starts_with("TRAIN "));
        for candidate in candidates {
            assert_eq!(
                candidate
                    .iter()
                    .find(|command| command.starts_with("TRAIN ")),
                train
            );
        }
    }

    #[test]
    fn robust_choice_requires_both_models() {
        assert_eq!(robust_choice(&[[0.0, 0.0], [8.0, -1.0], [6.0, 7.0]]), 2);
        assert_eq!(robust_choice(&[[0.0, 0.0], [4.9, 20.0]]), 0);
    }
}
