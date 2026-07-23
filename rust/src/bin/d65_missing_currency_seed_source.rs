//! Prospectively test one deposited-seed source repair for D40's worker-two tail.

use std::cmp::Reverse;
use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::game::engine::{training_cost, IRON};
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroDecisionStage, MacroOpponentMode, MacroTerminal, MacroTrainGoal,
    PlantOwner, MACRO_ACTION_PLANES, MACRO_CELLS,
};

const CONSUMED_SEEDS: [i64; 2] = [9_830_002, 9_830_014];
const FRESH_START_SEED: i64 = 9_831_000;
const FRESH_MAPS: usize = 32;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
#[repr(usize)]
enum Policy {
    D40Control = 0,
    SeedSourceRepair = 1,
}

impl Policy {
    const ALL: [Self; 2] = [Self::D40Control, Self::SeedSourceRepair];

    fn label(self) -> &'static str {
        match self {
            Self::D40Control => "d40_control",
            Self::SeedSourceRepair => "seed_source_repair",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Scope {
    Consumed,
    Fresh,
}

impl Scope {
    fn parse(value: &str) -> Self {
        match value {
            "consumed" => Self::Consumed,
            "fresh" => Self::Fresh,
            other => panic!("invalid D65 scope {other:?}; expected consumed or fresh"),
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::Consumed => "consumed",
            Self::Fresh => "fresh",
        }
    }

    fn split(self, map_seed: i64) -> &'static str {
        match self {
            Self::Consumed => "consumed",
            Self::Fresh if map_seed < FRESH_START_SEED + 16 => "development",
            Self::Fresh => "validation",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Copy, Debug)]
struct Work {
    scope: Scope,
    policy: Policy,
    task: Task,
}

#[derive(Clone, Copy, Debug)]
struct SourceTelemetry {
    activations: u8,
    activation_species: [u8; 4],
    first_activation_turns: [i32; 4],
    first_activation_state_hash: u64,
    activation_hash: u64,
    pick_commands: u16,
    plant_commands: u16,
    bootstrap_failures: u16,
    source_job_failures: u16,
    bootstrap_after_worker_two: u16,
    first_worker_two_turn: i32,
    first_worker_three_turn: i32,
    max_workers: u8,
    finite_state_failures: u16,
}

impl SourceTelemetry {
    fn new(initial_workers: usize) -> Self {
        Self {
            activations: 0,
            activation_species: [0; 4],
            first_activation_turns: [-1; 4],
            first_activation_state_hash: 0,
            activation_hash: 0xcbf29ce484222325,
            pick_commands: 0,
            plant_commands: 0,
            bootstrap_failures: 0,
            source_job_failures: 0,
            bootstrap_after_worker_two: 0,
            first_worker_two_turn: -1,
            first_worker_three_turn: -1,
            max_workers: initial_workers as u8,
            finite_state_failures: 0,
        }
    }

    fn mix_activation(&mut self, value: u64) {
        for byte in value.to_le_bytes() {
            self.activation_hash ^= u64::from(byte);
            self.activation_hash = self.activation_hash.wrapping_mul(0x100000001b3);
        }
    }

    fn observe_workers(&mut self, env: &CompleteMacroEnv) {
        let workers = own_worker_count(env);
        self.max_workers = self.max_workers.max(workers as u8);
        if self.first_worker_two_turn < 0 && workers >= 2 {
            self.first_worker_two_turn = env.state.turn;
        }
        if self.first_worker_three_turn < 0 && workers >= 3 {
            self.first_worker_three_turn = env.state.turn;
        }
    }
}

#[derive(Clone, Debug)]
struct Row {
    scope: Scope,
    policy: Policy,
    task: Task,
    terminal: MacroTerminal,
    reward_identity_error: f32,
    telemetry: SourceTelemetry,
    terminal_live_own_plants: usize,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

fn own_worker_count(env: &CompleteMacroEnv) -> usize {
    env.state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .count()
}

fn live_own_plants(env: &CompleteMacroEnv) -> usize {
    env.state
        .plants
        .iter()
        .filter(|plant| plant.health > 0)
        .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
        .count()
}

fn fruit_index(name: &str) -> usize {
    match name {
        "PLUM" => 0,
        "LEMON" => 1,
        "APPLE" => 2,
        "BANANA" => 3,
        other => panic!("unknown D65 fruit {other}"),
    }
}

/// Return the frozen missing-fruit bootstrap, if the current boundary qualifies.
fn source_kind(env: &CompleteMacroEnv, bootstrapped: u8) -> Option<usize> {
    if env.stage() != MacroDecisionStage::Train
        || env.train_goal() != MacroTrainGoal::Producer
        || own_worker_count(env) != 1
    {
        return None;
    }
    let mut cost = training_cost(1, MacroTrainGoal::Producer.spec().expect("producer spec"));
    if env.state.iron.is_empty() {
        cost[IRON] = 0;
    }
    let bank = env.state.inventories[env.seat];
    if (0..6).all(|index| bank[index] >= cost[index]) {
        return None;
    }
    let mut stock = bank;
    for unit in env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
    {
        for (available, carried) in stock.iter_mut().zip(unit.carry) {
            *available = available.saturating_add(carried);
        }
    }
    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
        let kind = fruit_index(&plant.plant_type);
        stock[kind] = stock[kind].saturating_add(plant.fruits);
    }
    let deficit = std::array::from_fn::<_, 6, _>(|index| (cost[index] - stock[index]).max(0));
    (0..4)
        .filter(|kind| deficit[*kind] > 0 && bank[*kind] > 0 && bootstrapped & (1u8 << *kind) == 0)
        .max_by_key(|kind| (deficit[*kind], Reverse(*kind)))
}

fn play(work: Work) -> Row {
    let task = work.task;
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut terminal = MacroTerminal::default();
    let mut telemetry = SourceTelemetry::new(own_worker_count(&env));
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut bootstrapped = 0u8;
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D65 decision loop on {task:?}");

        if work.policy == Policy::SeedSourceRepair {
            if let Some(kind) = source_kind(&env, bootstrapped) {
                let workers_before = own_worker_count(&env);
                telemetry.bootstrap_after_worker_two = telemetry
                    .bootstrap_after_worker_two
                    .saturating_add(u16::from(workers_before >= 2));
                let state_hash = env.state_hash();
                let turn = env.state.turn;
                let crops_before = env
                    .state
                    .plants
                    .iter()
                    .filter(|plant| plant.health > 0)
                    .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
                    .count();
                let invalidated_before = terminal.invalidated_jobs;
                let invalid_direct_before = terminal.invalid_direct_commands;
                match env.install_bank_seed_source(kind) {
                    Some(outcome) => {
                        bootstrapped |= 1u8 << kind;
                        telemetry.activations = telemetry.activations.saturating_add(1);
                        telemetry.activation_species[kind] =
                            telemetry.activation_species[kind].saturating_add(1);
                        if telemetry.first_activation_turns[kind] < 0 {
                            telemetry.first_activation_turns[kind] = turn;
                        }
                        if telemetry.first_activation_state_hash == 0 {
                            telemetry.first_activation_state_hash = state_hash;
                        }
                        telemetry.mix_activation(state_hash);
                        telemetry.mix_activation(turn as u64);
                        telemetry.mix_activation(kind as u64);
                        telemetry.mix_activation(outcome.target.0 as u64);
                        telemetry.mix_activation(outcome.target.1 as u64);
                        telemetry.pick_commands = telemetry
                            .pick_commands
                            .saturating_add(outcome.pick_commands);
                        telemetry.plant_commands = telemetry
                            .plant_commands
                            .saturating_add(outcome.plant_commands);
                        action_planes[7] = action_planes[7].saturating_add(1);
                        terminal = outcome.terminal;
                        let crops_after = live_own_plants(&env);
                        telemetry.source_job_failures =
                            telemetry.source_job_failures.saturating_add(u16::from(
                                outcome.pick_commands != 1
                                    || outcome.plant_commands != 1
                                    || crops_after != crops_before + 1
                                    || terminal.invalidated_jobs != invalidated_before
                                    || terminal.invalid_direct_commands != invalid_direct_before
                                    || (!terminal.done
                                        && (env.stage() != MacroDecisionStage::Train
                                            || env.train_goal() != MacroTrainGoal::Producer)),
                            ));
                        telemetry.observe_workers(&env);
                    }
                    None => {
                        telemetry.bootstrap_failures =
                            telemetry.bootstrap_failures.saturating_add(1);
                    }
                }
                if terminal.done {
                    break;
                }
                if env.state.turn == last_turn {
                    stagnant += 1;
                } else {
                    last_turn = env.state.turn;
                    stagnant = 0;
                }
                assert!(stagnant <= 16, "D65 zero-time source loop on {task:?}");
                if bootstrapped & (1u8 << kind) != 0 {
                    continue;
                }
            }
        }

        let observation = env.candidate_observation();
        let action = observation.actions[observation.teacher_index] as usize;
        assert!(
            env.legal_actions().contains(&action),
            "D65 illegal D40 action on {task:?}"
        );
        action_planes[action / MACRO_CELLS] = action_planes[action / MACRO_CELLS].saturating_add(1);
        terminal = env.step(action);
        telemetry.observe_workers(&env);
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D65 zero-time loop on {task:?}");
    }
    let reward_identity_error = [
        (terminal.own_return - terminal.own_score as f32 / 100.0).abs(),
        (terminal.opponent_return - terminal.opponent_score as f32 / 100.0).abs(),
        (terminal.margin_return - (terminal.own_score - terminal.opponent_score) as f32 / 100.0)
            .abs(),
    ]
    .into_iter()
    .fold(0.0f32, f32::max);
    Row {
        scope: work.scope,
        policy: work.policy,
        task,
        terminal,
        reward_identity_error,
        telemetry,
        terminal_live_own_plants: live_own_plants(&env),
        action_planes,
    }
}

fn work_items(scope: Scope) -> Vec<Work> {
    let seeds: Vec<i64> = match scope {
        Scope::Consumed => CONSUMED_SEEDS.to_vec(),
        Scope::Fresh => (FRESH_START_SEED..FRESH_START_SEED + FRESH_MAPS as i64).collect(),
    };
    let opponents = match scope {
        Scope::Consumed => 1,
        Scope::Fresh => MacroOpponentMode::ALL.len(),
    };
    Policy::ALL
        .into_iter()
        .flat_map(|policy| {
            seeds.iter().copied().flat_map(move |map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..opponents).map(move |opponent| Work {
                        scope,
                        policy,
                        task: Task {
                            map_seed,
                            seat,
                            opponent,
                        },
                    })
                })
            })
        })
        .collect()
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        4,
        "usage: d65_missing_currency_seed_source consumed|fresh OUTPUT THREADS"
    );
    let scope = Scope::parse(&args[1]);
    let output = &args[2];
    let threads: usize = parse(&args[3], "threads");
    assert!(threads > 0);
    let work = Arc::new(work_items(scope));
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
                let Some(item) = work.get(index) else {
                    break;
                };
                rows.lock().expect("D65 row lock").push(play(*item));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D65 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D65 row owner")
        .into_inner()
        .expect("D65 row lock");
    rows.sort_by_key(|row| (row.policy, row.task));

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D65 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "scope\tmap_seed\tsplit\tseat\topponent\tpolicy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\tactivations\tactivation_plum\tactivation_lemon\tactivation_apple\tactivation_banana\tfirst_activation_plum_turn\tfirst_activation_lemon_turn\tfirst_activation_apple_turn\tfirst_activation_banana_turn\tfirst_activation_state_hash\tactivation_hash\tpick_commands\tplant_commands\tbootstrap_failures\tsource_job_failures\tbootstrap_after_worker_two\tfirst_worker_two_turn\tfirst_worker_three_turn\tmax_workers\tfinite_state_failures\tterminal_live_own_plants\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D65 header");
    for row in &rows {
        let terminal = row.terminal;
        let t = row.telemetry;
        let fields = vec![
            row.scope.label().to_string(),
            row.task.map_seed.to_string(),
            row.scope.split(row.task.map_seed).to_string(),
            row.task.seat.to_string(),
            MacroOpponentMode::from_index(row.task.opponent)
                .label()
                .to_string(),
            row.policy.label().to_string(),
            terminal.turn.to_string(),
            terminal.own_score.to_string(),
            terminal.opponent_score.to_string(),
            (terminal.own_score - terminal.opponent_score).to_string(),
            format!("{:.8}", terminal.own_return),
            format!("{:.8}", terminal.opponent_return),
            format!("{:.8}", terminal.margin_return),
            format!("{:.8}", row.reward_identity_error),
            terminal.own_workers.to_string(),
            terminal.opponent_workers.to_string(),
            terminal.successful_trains.to_string(),
            terminal.completed_jobs.to_string(),
            terminal.invalidated_jobs.to_string(),
            terminal.invalid_direct_commands.to_string(),
            terminal.provenance_failures.to_string(),
            terminal.deposit_prediction_failures.to_string(),
            terminal.selected_decisions.to_string(),
            terminal.selected_jobs.to_string(),
            terminal.selected_nonidle_jobs.to_string(),
            terminal.selected_renew_jobs.to_string(),
            terminal.own_created_crops.to_string(),
            terminal.opponent_created_crops.to_string(),
            terminal.ambiguous_created_crops.to_string(),
            terminal.action_hash.to_string(),
            terminal.state_hash.to_string(),
            t.activations.to_string(),
            t.activation_species[0].to_string(),
            t.activation_species[1].to_string(),
            t.activation_species[2].to_string(),
            t.activation_species[3].to_string(),
            t.first_activation_turns[0].to_string(),
            t.first_activation_turns[1].to_string(),
            t.first_activation_turns[2].to_string(),
            t.first_activation_turns[3].to_string(),
            t.first_activation_state_hash.to_string(),
            t.activation_hash.to_string(),
            t.pick_commands.to_string(),
            t.plant_commands.to_string(),
            t.bootstrap_failures.to_string(),
            t.source_job_failures.to_string(),
            t.bootstrap_after_worker_two.to_string(),
            t.first_worker_two_turn.to_string(),
            t.first_worker_three_turn.to_string(),
            t.max_workers.to_string(),
            t.finite_state_failures.to_string(),
            row.terminal_live_own_plants.to_string(),
            row.action_planes[0].to_string(),
            row.action_planes[1].to_string(),
            row.action_planes[2].to_string(),
            row.action_planes[3].to_string(),
            row.action_planes[4].to_string(),
            row.action_planes[5].to_string(),
            row.action_planes[6].to_string(),
            row.action_planes[7].to_string(),
            row.action_planes[8].to_string(),
        ];
        writeln!(writer, "{}", fields.join("\t")).expect("write D65 row");
    }
    writer.flush().expect("flush D65 output");
    eprintln!(
        "saved {} {} rows in {:.3}s with {} threads",
        rows.len(),
        scope.label(),
        started.elapsed().as_secs_f64(),
        threads.min(work.len()),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn consumed_missing_species_are_selected_by_frozen_rule() {
        for seed in CONSUMED_SEEDS {
            for seat in 0..2 {
                let mut env = CompleteMacroEnv::new(seed, seat, MacroOpponentMode::Resident);
                let train = env.candidate_observation();
                env.step(train.actions[train.teacher_index] as usize);
                let worker = env.candidate_observation();
                env.step(worker.actions[worker.teacher_index] as usize);
                assert_eq!(env.stage(), MacroDecisionStage::Train);
                assert_eq!(source_kind(&env, 0), Some(0));
            }
        }
    }

    #[test]
    fn control_and_repair_work_grids_are_frozen() {
        let consumed = work_items(Scope::Consumed);
        let fresh = work_items(Scope::Fresh);
        assert_eq!(consumed.len(), 8);
        assert_eq!(fresh.len(), 1_024);
        assert_eq!(
            fresh.first().expect("fresh first").task.map_seed,
            FRESH_START_SEED
        );
        assert_eq!(fresh.last().expect("fresh last").task.map_seed, 9_831_031);
    }

    #[test]
    fn one_consumed_repair_executes_only_valid_source_transactions() {
        let row = play(Work {
            scope: Scope::Consumed,
            policy: Policy::SeedSourceRepair,
            task: Task {
                map_seed: 9_830_002,
                seat: 0,
                opponent: 0,
            },
        });
        assert!(row.terminal.done);
        assert!(row.telemetry.activations >= 1);
        assert_eq!(row.telemetry.activation_species[0], 1);
        assert_eq!(
            row.telemetry.pick_commands,
            u16::from(row.telemetry.activations)
        );
        assert_eq!(
            row.telemetry.plant_commands,
            u16::from(row.telemetry.activations)
        );
        assert_eq!(row.telemetry.source_job_failures, 0);
        assert_eq!(row.terminal.invalid_direct_commands, 0);
        assert_eq!(row.terminal.provenance_failures, 0);
        assert!(row.terminal.own_created_crops > 0);
    }
}
