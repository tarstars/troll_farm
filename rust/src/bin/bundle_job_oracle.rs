//! Offline terminal oracle for persistent resident-local job bundles.

#[path = "yamo_orchard_live.rs"]
mod yamo;

pub use yamo::{bot, game};

use std::collections::{BTreeMap, BTreeSet, HashSet};
use std::fs::File;
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use troll_farm::game::engine::{bfs_distances, has_stalled, step, WOOD};
use troll_farm::game::mapgen::generate_bronze;
use troll_farm::game::state::{Cell, GameState, Unit as EngineUnit};
use troll_farm::strategies::compact_gold::CompactGold;
use troll_farm::strategies::gold_elite::GoldElite;
use troll_farm::strategies::mybot::MyBot;
use troll_farm::strategies::printer_bot::PrinterBot;
use troll_farm::strategies::sched_bot::SchedBot;
use troll_farm::strategies::script_boss::ScriptBoss;
use troll_farm::strategies::silver_boss::SilverBoss;
use troll_farm::strategies::Strategy;
use yamo::bot::moisan::SecureOrchardBot;
use yamo::bot::Bot;
use yamo::game::{GameState as YamoState, Plant, PlantKind, Stats, Unit};

const TOTAL_TURNS: i32 = 300;
const CHECKPOINTS: [i32; 3] = [50, 100, 150];
const MAX_TARGETS_PER_KIND: usize = 5;
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

fn ceil_div(value: i32, divisor: i32) -> i32 {
    if divisor <= 0 {
        10_000
    } else {
        (value + divisor - 1) / divisor
    }
}

fn own_units(game: &GameState, player: usize) -> Vec<&EngineUnit> {
    let mut units: Vec<_> = game
        .units
        .iter()
        .filter(|unit| unit.player as usize == player)
        .collect();
    units.sort_by_key(|unit| unit.id);
    units
}

fn action_by_unit(game: &GameState, player: usize, commands: &[String]) -> BTreeMap<i32, String> {
    let ids: Vec<_> = own_units(game, player)
        .into_iter()
        .map(|unit| unit.id)
        .collect();
    commands
        .iter()
        .filter(|command| !command.starts_with("MSG ") && !command.starts_with("TRAIN "))
        .zip(ids)
        .map(|(command, id)| (id, command.clone()))
        .collect()
}

fn replace_unit_action(
    game: &GameState,
    player: usize,
    commands: &mut Vec<String>,
    unit_id: i32,
    replacement: String,
) -> bool {
    let ids: Vec<_> = own_units(game, player)
        .into_iter()
        .map(|unit| unit.id)
        .collect();
    let mut slot = 0usize;
    for command in commands.iter_mut() {
        if command.starts_with("MSG ") || command.starts_with("TRAIN ") {
            continue;
        }
        if ids.get(slot).copied() == Some(unit_id) {
            let changed = *command != replacement;
            *command = replacement;
            return changed;
        }
        slot += 1;
    }
    commands.push(replacement);
    true
}

fn nearest_door(game: &GameState, player: usize, from: Cell) -> Option<(Cell, i32)> {
    let distance = bfs_distances(&game.walkable, &[from]);
    let (sx, sy) = game.shacks[player];
    [(sx, sy + 1), (sx + 1, sy), (sx, sy - 1), (sx - 1, sy)]
        .into_iter()
        .filter(|cell| game.walkable.contains(cell))
        .filter_map(|cell| Some((cell, *distance.get(&cell)?)))
        .min_by_key(|(cell, cells)| (*cells, *cell))
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
enum JobKind {
    Bank,
    FellBank,
    HarvestBank,
}

impl JobKind {
    fn label(self) -> &'static str {
        match self {
            Self::Bank => "bank",
            Self::FellBank => "fell_bank",
            Self::HarvestBank => "harvest_bank",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct JobSpec {
    kind: JobKind,
    unit_id: i32,
    target: Option<Cell>,
    predicted_eta: i32,
    predicted_reward: i32,
}

fn jobs_for_unit(game: &GameState, player: usize, unit: &EngineUnit) -> Vec<JobSpec> {
    let from_unit = bfs_distances(&game.walkable, &[unit.pos()]);
    let mut jobs = Vec::new();
    if unit.total() > 0 {
        if let Some((_, distance)) = nearest_door(game, player, unit.pos()) {
            jobs.push(JobSpec {
                kind: JobKind::Bank,
                unit_id: unit.id,
                target: None,
                predicted_eta: ceil_div(distance, unit.ms) + 1,
                predicted_reward: unit.carry[..4].iter().sum::<i32>() + 4 * unit.carry[WOOD],
            });
        }
    }
    if unit.chop > 0 && unit.free() > 0 {
        let mut fell: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0)
            .filter_map(|plant| {
                let travel = ceil_div(*from_unit.get(&plant.pos())?, unit.ms);
                let chop = ceil_div(plant.health, unit.chop);
                let (_, bank_distance) = nearest_door(game, player, plant.pos())?;
                let bank = ceil_div(bank_distance, unit.ms) + 1;
                let reward = 4 * plant.size.min(unit.free());
                Some((travel + chop + bank, -reward, plant.pos(), reward))
            })
            .collect();
        fell.sort_unstable();
        jobs.extend(
            fell.into_iter()
                .take(MAX_TARGETS_PER_KIND)
                .map(|(eta, _, target, reward)| JobSpec {
                    kind: JobKind::FellBank,
                    unit_id: unit.id,
                    target: Some(target),
                    predicted_eta: eta,
                    predicted_reward: reward,
                }),
        );
    }
    if unit.hp > 0 && unit.free() > 0 {
        let mut harvest: Vec<_> = game
            .plants
            .iter()
            .filter(|plant| plant.health > 0 && plant.fruits > 0)
            .filter_map(|plant| {
                let travel = ceil_div(*from_unit.get(&plant.pos())?, unit.ms);
                let (_, bank_distance) = nearest_door(game, player, plant.pos())?;
                let bank = ceil_div(bank_distance, unit.ms) + 1;
                let reward = plant.fruits.min(unit.hp).min(unit.free());
                Some((travel + 1 + bank, -reward, plant.pos(), reward))
            })
            .collect();
        harvest.sort_unstable();
        jobs.extend(harvest.into_iter().take(MAX_TARGETS_PER_KIND).map(
            |(eta, _, target, reward)| JobSpec {
                kind: JobKind::HarvestBank,
                unit_id: unit.id,
                target: Some(target),
                predicted_eta: eta,
                predicted_reward: reward,
            },
        ));
    }
    jobs
}

fn root_jobs(game: &GameState, player: usize, baseline: &[String]) -> Vec<JobSpec> {
    let actions = action_by_unit(game, player, baseline);
    let eligible: HashSet<_> = actions
        .iter()
        .filter(|(_, command)| redirectable(command))
        .map(|(id, _)| *id)
        .collect();
    let mut jobs: Vec<_> = own_units(game, player)
        .into_iter()
        .filter(|unit| eligible.contains(&unit.id))
        .flat_map(|unit| jobs_for_unit(game, player, unit))
        .collect();
    jobs.sort_by_key(|job| {
        (
            job.unit_id,
            job.kind,
            job.predicted_eta,
            -job.predicted_reward,
            job.target,
        )
    });
    jobs.dedup_by_key(|job| (job.unit_id, job.kind, job.target));
    jobs
}

fn redirectable(command: &str) -> bool {
    command == "WAIT" || command.starts_with("MOVE ")
}

#[derive(Clone)]
struct Root {
    checkpoint: i32,
    game: GameState,
    bot: SecureOrchardBot,
    opponent_history: Vec<GameState>,
    stall_counter: i32,
    jobs: Vec<JobSpec>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum JobPhase {
    Acquire,
    Bank,
}

struct ActiveJob {
    spec: JobSpec,
    phase: JobPhase,
    initial_carry: [i32; 6],
}

impl ActiveJob {
    fn new(spec: JobSpec, game: &GameState) -> Self {
        let unit = game
            .units
            .iter()
            .find(|unit| unit.id == spec.unit_id)
            .expect("root job unit");
        Self {
            phase: if spec.kind == JobKind::Bank {
                JobPhase::Bank
            } else {
                JobPhase::Acquire
            },
            spec,
            initial_carry: unit.carry,
        }
    }

    fn acquired(&self, unit: &EngineUnit) -> bool {
        match self.spec.kind {
            JobKind::Bank => true,
            JobKind::FellBank => unit.carry[WOOD] > self.initial_carry[WOOD],
            JobKind::HarvestBank => {
                unit.carry[..4].iter().sum::<i32>() > self.initial_carry[..4].iter().sum::<i32>()
            }
        }
    }

    fn command(&mut self, game: &GameState, player: usize) -> Result<Option<String>, &'static str> {
        let Some(unit) = game.units.iter().find(|unit| unit.id == self.spec.unit_id) else {
            return Err("unit_missing");
        };
        if self.phase == JobPhase::Acquire && self.acquired(unit) {
            self.phase = JobPhase::Bank;
        }
        if self.phase == JobPhase::Bank {
            if unit.total() == 0 {
                return Ok(None);
            }
            let Some((door, _)) = nearest_door(game, player, unit.pos()) else {
                return Err("bank_unreachable");
            };
            return Ok(Some(if unit.pos() == door {
                format!("DROP {}", unit.id)
            } else {
                format!("MOVE {} {} {}", unit.id, door.0, door.1)
            }));
        }

        let target = self.spec.target.expect("acquisition target");
        let Some(plant) = game
            .plants
            .iter()
            .find(|plant| plant.pos() == target && plant.health > 0)
        else {
            return Err("target_missing");
        };
        if unit.pos() != target {
            if !bfs_distances(&game.walkable, &[unit.pos()]).contains_key(&target) {
                return Err("target_unreachable");
            }
            return Ok(Some(format!("MOVE {} {} {}", unit.id, target.0, target.1)));
        }
        match self.spec.kind {
            JobKind::FellBank if unit.chop > 0 && unit.free() > 0 => {
                Ok(Some(format!("CHOP {}", unit.id)))
            }
            JobKind::HarvestBank if unit.hp > 0 && unit.free() > 0 && plant.fruits > 0 => {
                Ok(Some(format!("HARVEST {}", unit.id)))
            }
            JobKind::HarvestBank => Err("fruit_unavailable"),
            JobKind::FellBank => Err("fell_capability_lost"),
            JobKind::Bank => unreachable!(),
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct Outcome {
    own_score: i32,
    opponent_score: i32,
    own_wood: i32,
    opponent_wood: i32,
    terminal_turn: i32,
}

impl Outcome {
    fn from_game(game: &GameState, player: usize) -> Self {
        Self {
            own_score: game.scores[player],
            opponent_score: game.scores[1 - player],
            own_wood: game.inventories[player][WOOD],
            opponent_wood: game.inventories[1 - player][WOOD],
            terminal_turn: game.turn,
        }
    }

    fn margin(self) -> i32 {
        self.own_score - self.opponent_score
    }
}

struct Simulation {
    outcome: Outcome,
    status: &'static str,
    overridden_actions: usize,
    job_end_turn: Option<i32>,
}

fn simulate(root: &Root, player: usize, model: usize, spec: Option<JobSpec>) -> Simulation {
    let mut game = root.game.clone();
    let mut bot = root.bot.clone();
    let opponent = opponent(model);
    // Several sparring strategies keep sticky targets behind RefCell. Replaying
    // their prior observations reconstructs the exact state they had at this
    // root without requiring clone support on the Strategy trait object.
    for historical in &root.opponent_history {
        let _ = opponent.decide(historical, 1 - player);
    }
    let mut stall_counter = root.stall_counter;
    let mut active = spec.map(|job| ActiveJob::new(job, &game));
    let mut status = if active.is_some() {
        "timeout"
    } else {
        "control"
    };
    let mut overridden_actions = 0usize;
    let mut job_end_turn = None;
    while game.turn <= TOTAL_TURNS {
        let mut ours = bot.commands(&yamo_view(&game, player));
        if let Some(job) = active.as_mut() {
            match job.command(&game, player) {
                Ok(Some(command)) => {
                    overridden_actions += usize::from(replace_unit_action(
                        &game,
                        player,
                        &mut ours,
                        job.spec.unit_id,
                        command,
                    ));
                }
                Ok(None) => {
                    status = "completed";
                    job_end_turn = Some(game.turn);
                    active = None;
                }
                Err(reason) => {
                    status = reason;
                    job_end_turn = Some(game.turn);
                    active = None;
                }
            }
        }
        let theirs = opponent.decide(&game, 1 - player);
        if player == 0 {
            step(&mut game, &ours, &theirs);
        } else {
            step(&mut game, &theirs, &ours);
        }
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }
    Simulation {
        outcome: Outcome::from_game(&game, player),
        status,
        overridden_actions,
        job_end_turn,
    }
}

#[derive(Clone, Copy)]
struct Task {
    seed: u64,
    seat: usize,
    model: usize,
}

struct Row {
    task: Task,
    checkpoint: i32,
    root_turn: i32,
    option: usize,
    spec: Option<JobSpec>,
    simulation: Simulation,
    control: Outcome,
    baseline: Outcome,
}

fn play_task(task: Task) -> Vec<Row> {
    let mut game = generate_bronze(task.seed);
    let mut resident = SecureOrchardBot::new();
    let opponent = opponent(task.model);
    let mut stall_counter = 0;
    let mut captured = [false; CHECKPOINTS.len()];
    let mut opponent_history = Vec::new();
    let mut roots = Vec::new();
    while game.turn <= TOTAL_TURNS {
        let before = resident.clone();
        let ours = resident.commands(&yamo_view(&game, task.seat));
        let eligible_root = action_by_unit(&game, task.seat, &ours)
            .values()
            .any(|command| redirectable(command));
        let jobs = root_jobs(&game, task.seat, &ours);
        for (index, checkpoint) in CHECKPOINTS.into_iter().enumerate() {
            if !captured[index] && game.turn >= checkpoint && eligible_root {
                captured[index] = true;
                roots.push(Root {
                    checkpoint,
                    game: game.clone(),
                    bot: before.clone(),
                    opponent_history: opponent_history.clone(),
                    stall_counter,
                    jobs: jobs.clone(),
                });
            }
        }
        let theirs = opponent.decide(&game, 1 - task.seat);
        opponent_history.push(game.clone());
        if task.seat == 0 {
            step(&mut game, &ours, &theirs);
        } else {
            step(&mut game, &theirs, &ours);
        }
        if has_stalled(&game, &mut stall_counter) {
            break;
        }
    }
    let baseline = Outcome::from_game(&game, task.seat);
    let mut rows = Vec::new();
    for root in roots {
        let control_simulation = simulate(&root, task.seat, task.model, None);
        let control = control_simulation.outcome;
        rows.push(Row {
            task,
            checkpoint: root.checkpoint,
            root_turn: root.game.turn,
            option: 0,
            spec: None,
            simulation: control_simulation,
            control,
            baseline,
        });
        for (index, spec) in root.jobs.iter().copied().enumerate() {
            rows.push(Row {
                task,
                checkpoint: root.checkpoint,
                root_turn: root.game.turn,
                option: index + 1,
                spec: Some(spec),
                simulation: simulate(&root, task.seat, task.model, Some(spec)),
                control,
                baseline,
            });
        }
    }
    rows
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    let seeds = args
        .get(1)
        .and_then(|value| value.parse().ok())
        .unwrap_or(10);
    let output = args
        .get(2)
        .cloned()
        .unwrap_or_else(|| "bundle-job-oracle.tsv".to_string());
    let threads = args
        .get(3)
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(20)
        .max(1);
    let seed_start = args
        .get(4)
        .and_then(|value| value.parse().ok())
        .unwrap_or(0);
    let mut task_rows = Vec::new();
    for seed in seed_start..seed_start + seeds {
        for model in 0..OPPONENTS.len() {
            for seat in 0..2 {
                task_rows.push(Task { seed, seat, model });
            }
        }
    }
    let tasks = Arc::new(task_rows);
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
                        local.extend(play_task(tasks[index]));
                    }
                    local
                })
            })
            .collect();
        handles
            .into_iter()
            .flat_map(|handle| handle.join().expect("bundle oracle worker"))
            .collect::<Vec<_>>()
    });
    rows.sort_by_key(|row| {
        (
            row.task.seed,
            row.task.model,
            row.task.seat,
            row.checkpoint,
            row.option,
        )
    });
    let mut writer = std::io::BufWriter::new(File::create(&output).expect("create oracle output"));
    writeln!(writer, "seed\tseat\topponent\tcheckpoint\troot_turn\toption\tjob_kind\tunit_id\ttarget_x\ttarget_y\tpredicted_eta\tpredicted_reward\tstatus\toverridden_actions\tjob_end_turn\town_score\topponent_score\tmargin\town_wood\topponent_wood\tterminal_turn\tmargin_delta\town_score_delta\topponent_score_delta\town_wood_delta\tcontrol_own_score\tcontrol_opponent_score\tcontrol_margin\tcontrol_own_wood\tcontrol_opponent_wood\tcontrol_terminal_turn\tbaseline_identity_match").expect("write header");
    for row in &rows {
        let (kind, unit, target, eta, reward) =
            row.spec.map_or(("control", -1, None, 0, 0), |spec| {
                (
                    spec.kind.label(),
                    spec.unit_id,
                    spec.target,
                    spec.predicted_eta,
                    spec.predicted_reward,
                )
            });
        let terminal = row.simulation.outcome;
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.seed,
            row.task.seat,
            OPPONENTS[row.task.model],
            row.checkpoint,
            row.root_turn,
            row.option,
            kind,
            unit,
            target.map_or(-1, |cell| cell.0),
            target.map_or(-1, |cell| cell.1),
            eta,
            reward,
            row.simulation.status,
            row.simulation.overridden_actions,
            row.simulation.job_end_turn.unwrap_or(-1),
            terminal.own_score,
            terminal.opponent_score,
            terminal.margin(),
            terminal.own_wood,
            terminal.opponent_wood,
            terminal.terminal_turn,
            terminal.margin() - row.control.margin(),
            terminal.own_score - row.control.own_score,
            terminal.opponent_score - row.control.opponent_score,
            terminal.own_wood - row.control.own_wood,
            row.control.own_score,
            row.control.opponent_score,
            row.control.margin(),
            row.control.own_wood,
            row.control.opponent_wood,
            row.control.terminal_turn,
            usize::from(row.control == row.baseline),
        )
        .expect("write oracle row");
    }
    eprintln!(
        "saved {} option rows from {} tasks to {}",
        rows.len(),
        tasks.len(),
        output
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn root_job_generation_is_deterministic_and_bounded() {
        let game = generate_bronze(0);
        let mut bot = SecureOrchardBot::new();
        let commands = bot.commands(&yamo_view(&game, 0));
        let first = root_jobs(&game, 0, &commands);
        let second = root_jobs(&game, 0, &commands);
        assert_eq!(first, second);
        assert!(first.len() <= own_units(&game, 0).len() * (2 * MAX_TARGETS_PER_KIND + 1));
    }

    #[test]
    fn control_branch_reproduces_uninterrupted_resident() {
        let rows = play_task(Task {
            seed: 0,
            seat: 0,
            model: 1,
        });
        assert!(!rows.is_empty());
        assert!(rows.iter().all(|row| row.control == row.baseline));
        assert!(rows
            .iter()
            .filter(|row| row.option == 0)
            .all(|row| row.simulation.status == "control"));
    }
}
