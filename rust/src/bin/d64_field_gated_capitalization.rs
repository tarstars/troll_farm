//! Prospectively test the D63b field-snapshot selector on D40 late capitalization.

use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::rl_macro::{
    macro_action, CompleteMacroEnv, MacroDecisionStage, MacroOpponentMode, MacroTerminal,
    PlantOwner, MACRO_ACTION_PLANES, MACRO_CELLS,
};

mod frozen_model {
    include!("../d64a_snapshot_model_generated.rs");
}

const START_SEED: i64 = 9_830_000;
const MAPS: usize = 16;
const POLICIES: usize = 4;

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
#[repr(usize)]
enum Policy {
    D40Control = 0,
    NeverLateScale = 1,
    FieldSnapshotGate = 2,
    InverseSnapshotGate = 3,
}

impl Policy {
    const ALL: [Self; POLICIES] = [
        Self::D40Control,
        Self::NeverLateScale,
        Self::FieldSnapshotGate,
        Self::InverseSnapshotGate,
    ];

    fn label(self) -> &'static str {
        match self {
            Self::D40Control => "d40_control",
            Self::NeverLateScale => "never_late_scale",
            Self::FieldSnapshotGate => "field_snapshot_gate",
            Self::InverseSnapshotGate => "inverse_snapshot_gate",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum Latch {
    Scale,
    Suppress,
}

impl Latch {
    fn label(self) -> &'static str {
        match self {
            Self::Scale => "scale",
            Self::Suppress => "suppress",
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
    policy: Policy,
    task: Task,
}

#[derive(Clone, Copy, Debug, Default)]
struct DecisionTelemetry {
    eligible: bool,
    turn: i32,
    state_hash: u64,
    logit: f64,
    probability: f64,
    rms_z: f64,
    within_support: bool,
    latch: Option<Latch>,
    overrides: u32,
    first_third_turn: i32,
    max_workers: u8,
    finite_feature_failures: u32,
    model_parity_failures: u32,
}

#[derive(Clone, Debug)]
struct Row {
    policy: Policy,
    task: Task,
    terminal: MacroTerminal,
    reward_identity_error: f32,
    decision: DecisionTelemetry,
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

fn item_index(name: &str) -> Option<usize> {
    match name {
        "plum" => Some(0),
        "lemon" => Some(1),
        "apple" => Some(2),
        "banana" => Some(3),
        "iron" => Some(4),
        "wood" => Some(5),
        _ => None,
    }
}

fn inventory_score(inventory: &[i32; 6]) -> i32 {
    inventory[..4].iter().sum::<i32>() + 4 * inventory[5]
}

fn snapshot_features(env: &CompleteMacroEnv) -> [f64; frozen_model::FEATURE_COUNT] {
    let own = env.seat;
    let opponent = 1 - own;
    let own_inventory = &env.state.inventories[own];
    let opponent_inventory = &env.state.inventories[opponent];
    let own_units: Vec<_> = env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == own)
        .collect();
    let opponent_units: Vec<_> = env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == opponent)
        .collect();
    let mut own_carry = [0i32; 6];
    let mut opponent_carry = [0i32; 6];
    for unit in &own_units {
        for (total, amount) in own_carry.iter_mut().zip(unit.carry) {
            *total += amount;
        }
    }
    for unit in &opponent_units {
        for (total, amount) in opponent_carry.iter_mut().zip(unit.carry) {
            *total += amount;
        }
    }
    let own_carrying = own_units
        .iter()
        .filter(|unit| unit.carry.iter().any(|amount| *amount > 0))
        .count();
    let opponent_carrying = opponent_units
        .iter()
        .filter(|unit| unit.carry.iter().any(|amount| *amount > 0))
        .count();

    let mut species_count = [0usize; 4];
    let mut species_fruit = [0i32; 4];
    let mut board_fruit = 0i32;
    let mut board_health = 0i32;
    let mut board_size = 0i32;
    let mut board_ripe = 0usize;
    let mut board_plants = 0usize;
    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
        let species = match plant.plant_type.as_str() {
            "PLUM" => 0,
            "LEMON" => 1,
            "APPLE" => 2,
            "BANANA" => 3,
            other => panic!("unknown D64 plant type {other}"),
        };
        species_count[species] += 1;
        species_fruit[species] += plant.fruits;
        board_fruit += plant.fruits;
        board_health += plant.health;
        board_size += plant.size;
        board_ripe += usize::from(plant.fruits > 0);
        board_plants += 1;
    }

    let board_value = |name: &str| -> Option<f64> {
        let value = match name {
            "board_apple_count" => species_count[2] as f64,
            "board_apple_fruit" => species_fruit[2] as f64,
            "board_banana_count" => species_count[3] as f64,
            "board_banana_fruit" => species_fruit[3] as f64,
            "board_fruit_total" => board_fruit as f64,
            "board_health_total" => board_health as f64,
            "board_lemon_count" => species_count[1] as f64,
            "board_lemon_fruit" => species_fruit[1] as f64,
            "board_plant_count" => board_plants as f64,
            "board_plum_count" => species_count[0] as f64,
            "board_plum_fruit" => species_fruit[0] as f64,
            "board_ripe_count" => board_ripe as f64,
            "board_size_total" => board_size as f64,
            _ => return None,
        };
        Some(value)
    };

    let mut values = [0.0f64; frozen_model::FEATURE_COUNT];
    for (index, name) in frozen_model::FEATURE_NAMES.iter().enumerate() {
        values[index] = if *name == "bank_score_gap" {
            (inventory_score(own_inventory) - inventory_score(opponent_inventory)) as f64
        } else if *name == "bank_wood_gap" {
            (own_inventory[5] - opponent_inventory[5]) as f64
        } else if *name == "own_carrying_workers" {
            own_carrying as f64
        } else if *name == "opponent_carrying_workers" {
            opponent_carrying as f64
        } else if *name == "opponent_worker_count" {
            opponent_units.len() as f64
        } else if *name == "own_bank_score" {
            inventory_score(own_inventory) as f64
        } else if *name == "opponent_bank_score" {
            inventory_score(opponent_inventory) as f64
        } else if let Some(value) = board_value(name) {
            value
        } else if let Some(item) = name.strip_prefix("own_bank_").and_then(item_index) {
            own_inventory[item] as f64
        } else if let Some(item) = name.strip_prefix("opponent_bank_").and_then(item_index) {
            opponent_inventory[item] as f64
        } else if let Some(item) = name.strip_prefix("own_carry_").and_then(item_index) {
            own_carry[item] as f64
        } else if let Some(item) = name.strip_prefix("opponent_carry_").and_then(item_index) {
            opponent_carry[item] as f64
        } else {
            panic!("unmapped D64 feature {name}")
        };
    }
    values
}

fn model_score(features: &[f64; frozen_model::FEATURE_COUNT]) -> (f64, f64, f64) {
    let mut logit = frozen_model::INTERCEPT;
    let mut sum_squared = 0.0f64;
    for index in 0..frozen_model::FEATURE_COUNT {
        let z = (features[index] - frozen_model::MEANS[index]) / frozen_model::SCALES[index];
        logit += frozen_model::COEFFICIENTS[index] * z;
        sum_squared += z * z;
    }
    let probability = 1.0 / (1.0 + (-logit.clamp(-40.0, 40.0)).exp());
    let rms_z = (sum_squared / frozen_model::FEATURE_COUNT as f64).sqrt();
    (logit, probability, rms_z)
}

fn policy_latch(policy: Policy, probability: f64) -> Latch {
    let predicted_scale = probability >= frozen_model::THRESHOLD;
    match policy {
        Policy::D40Control => Latch::Scale,
        Policy::NeverLateScale => Latch::Suppress,
        Policy::FieldSnapshotGate => {
            if predicted_scale {
                Latch::Scale
            } else {
                Latch::Suppress
            }
        }
        Policy::InverseSnapshotGate => {
            if predicted_scale {
                Latch::Suppress
            } else {
                Latch::Scale
            }
        }
    }
}

fn live_own_plants(env: &CompleteMacroEnv) -> usize {
    env.state
        .plants
        .iter()
        .filter(|plant| plant.health > 0)
        .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
        .count()
}

fn play(task: Task, policy: Policy) -> Row {
    let mut env = CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    );
    let mut terminal = MacroTerminal::default();
    let mut decision = DecisionTelemetry {
        turn: -1,
        probability: -1.0,
        logit: 0.0,
        rms_z: 0.0,
        first_third_turn: -1,
        max_workers: own_worker_count(&env) as u8,
        ..DecisionTelemetry::default()
    };
    let mut action_planes = [0u32; MACRO_ACTION_PLANES];
    let mut decisions = 0usize;
    let mut last_turn = env.state.turn;
    let mut stagnant = 0usize;
    while !terminal.done {
        decisions += 1;
        assert!(decisions <= 5_000, "D64 decision loop on {task:?}");
        let observation = env.candidate_observation();
        let workers_before = own_worker_count(&env);
        if decision.latch.is_none()
            && env.stage() == MacroDecisionStage::Train
            && env.state.turn >= 100
            && workers_before == 2
        {
            let features = snapshot_features(&env);
            decision.finite_feature_failures +=
                u32::from(features.iter().any(|value| !value.is_finite()));
            let (logit, probability, rms_z) = model_score(&features);
            decision.finite_feature_failures +=
                u32::from(!logit.is_finite() || !probability.is_finite() || !rms_z.is_finite());
            decision.eligible = true;
            decision.turn = env.state.turn;
            decision.state_hash = env.state_hash();
            decision.logit = logit;
            decision.probability = probability;
            decision.rms_z = rms_z;
            decision.within_support = rms_z <= frozen_model::SUPPORT_RADIUS_RMS_Z_P95;
            decision.latch = Some(policy_latch(policy, probability));
        }
        let teacher = observation.actions[observation.teacher_index] as usize;
        let action = if env.stage() == MacroDecisionStage::Train
            && workers_before == 2
            && decision.latch == Some(Latch::Suppress)
        {
            let no_train = macro_action(0, env.state.shacks[env.seat]);
            decision.overrides += u32::from(no_train != teacher);
            no_train
        } else {
            teacher
        };
        assert!(
            env.legal_actions().contains(&action),
            "D64 illegal action on {task:?}"
        );
        action_planes[action / MACRO_CELLS] += 1;
        terminal = env.step(action);
        let workers_after = own_worker_count(&env);
        decision.max_workers = decision.max_workers.max(workers_after as u8);
        if decision.first_third_turn < 0 && workers_after >= 3 {
            decision.first_third_turn = env.state.turn;
        }
        if env.state.turn == last_turn {
            stagnant += 1;
        } else {
            last_turn = env.state.turn;
            stagnant = 0;
        }
        assert!(stagnant <= 16, "D64 zero-time loop on {task:?}");
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
        policy,
        task,
        terminal,
        reward_identity_error,
        decision,
        terminal_live_own_plants: live_own_plants(&env),
        action_planes,
    }
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
        5,
        "usage: d64_field_gated_capitalization START_SEED MAPS OUTPUT THREADS"
    );
    let start_seed: i64 = parse(&args[1], "start seed");
    let maps: usize = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
    assert_eq!(start_seed, START_SEED, "D64 frozen seed start");
    assert_eq!(maps, MAPS, "D64 frozen map count");
    assert!(threads > 0);
    let work: Vec<_> = Policy::ALL
        .into_iter()
        .flat_map(|policy| {
            (start_seed..start_seed + maps as i64).flat_map(move |map_seed| {
                (0..2).flat_map(move |seat| {
                    (0..MacroOpponentMode::ALL.len()).map(move |opponent| Work {
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
                let Some(item) = work.get(index) else {
                    break;
                };
                rows.lock()
                    .expect("D64 row lock")
                    .push(play(item.task, item.policy));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D64 worker thread");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D64 row owner")
        .into_inner()
        .expect("D64 row lock");
    rows.sort_by_key(|row| (row.policy, row.task));

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D64 output without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "map_seed\tsplit\tseat\topponent\tpolicy\tturn\town_score\topponent_score\tmargin\town_return\topponent_return\tmargin_return\treward_identity_error\town_workers\topponent_workers\tsuccessful_trains\tcompleted_jobs\tinvalidated_jobs\tinvalid_direct_commands\tprovenance_failures\tdeposit_prediction_failures\tselected_decisions\tselected_jobs\tselected_nonidle_jobs\tselected_renew_jobs\town_created_crops\topponent_created_crops\tambiguous_created_crops\taction_hash\tstate_hash\teligible\tdecision_turn\tdecision_state_hash\tmodel_logit\tmodel_probability\trms_z\twithin_support\tlatched_action\toverrides\tfirst_third_turn\tmax_workers\tfinite_feature_failures\tmodel_parity_failures\tterminal_live_own_plants\ttrain_none\ttrain_producer\ttrain_chopper\tidle\tbank\tfell_bank\tharvest_bank\trenew\tmine_bank").expect("write D64 header");
    for row in &rows {
        let terminal = row.terminal;
        let split = if row.task.map_seed < START_SEED + 8 {
            "development"
        } else {
            "validation"
        };
        let latch = row.decision.latch.map(Latch::label).unwrap_or("none");
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.8}\t{:.8}\t{:.8}\t{:.8}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:.17}\t{:.17}\t{:.17}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.task.map_seed,
            split,
            row.task.seat,
            MacroOpponentMode::from_index(row.task.opponent).label(),
            row.policy.label(),
            terminal.turn,
            terminal.own_score,
            terminal.opponent_score,
            terminal.own_score - terminal.opponent_score,
            terminal.own_return,
            terminal.opponent_return,
            terminal.margin_return,
            row.reward_identity_error,
            terminal.own_workers,
            terminal.opponent_workers,
            terminal.successful_trains,
            terminal.completed_jobs,
            terminal.invalidated_jobs,
            terminal.invalid_direct_commands,
            terminal.provenance_failures,
            terminal.deposit_prediction_failures,
            terminal.selected_decisions,
            terminal.selected_jobs,
            terminal.selected_nonidle_jobs,
            terminal.selected_renew_jobs,
            terminal.own_created_crops,
            terminal.opponent_created_crops,
            terminal.ambiguous_created_crops,
            terminal.action_hash,
            terminal.state_hash,
            u8::from(row.decision.eligible),
            row.decision.turn,
            row.decision.state_hash,
            row.decision.logit,
            row.decision.probability,
            row.decision.rms_z,
            u8::from(row.decision.within_support),
            latch,
            row.decision.overrides,
            row.decision.first_third_turn,
            row.decision.max_workers,
            row.decision.finite_feature_failures,
            row.decision.model_parity_failures,
            row.terminal_live_own_plants,
            row.action_planes[0],
            row.action_planes[1],
            row.action_planes[2],
            row.action_planes[3],
            row.action_planes[4],
            row.action_planes[5],
            row.action_planes[6],
            row.action_planes[7],
            row.action_planes[8],
        )
        .expect("write D64 row");
    }
    writer.flush().expect("flush D64 output");
    eprintln!(
        "saved {} policies x {} maps x 16 tasks = {} rows in {:.3}s",
        POLICIES,
        maps,
        rows.len(),
        started.elapsed().as_secs_f64(),
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn generated_model_contract_is_complete_and_finite() {
        assert_eq!(frozen_model::FEATURE_NAMES.len(), 44);
        assert!(frozen_model::MEANS.iter().all(|value| value.is_finite()));
        assert!(frozen_model::SCALES.iter().all(|value| *value > 0.0));
        assert!(frozen_model::COEFFICIENTS
            .iter()
            .all(|value| value.is_finite()));
        assert_eq!(frozen_model::THRESHOLD, 0.5);
    }

    #[test]
    fn feature_extractor_maps_every_frozen_name() {
        let env = CompleteMacroEnv::new(START_SEED, 0, MacroOpponentMode::Resident);
        let features = snapshot_features(&env);
        assert_eq!(features.len(), 44);
        assert!(features.iter().all(|value| value.is_finite()));
        let (_, probability, rms_z) = model_score(&features);
        assert!((0.0..=1.0).contains(&probability));
        assert!(rms_z.is_finite());
    }

    #[test]
    fn field_and_inverse_latches_are_complements() {
        assert_eq!(policy_latch(Policy::FieldSnapshotGate, 0.5), Latch::Scale);
        assert_eq!(
            policy_latch(Policy::InverseSnapshotGate, 0.5),
            Latch::Suppress
        );
        assert_eq!(
            policy_latch(Policy::FieldSnapshotGate, 0.49),
            Latch::Suppress
        );
        assert_eq!(
            policy_latch(Policy::InverseSnapshotGate, 0.49),
            Latch::Scale
        );
    }

    #[test]
    fn pure_arm_actions_diverge_only_after_eligible_boundary() {
        let task = Task {
            map_seed: START_SEED,
            seat: 0,
            opponent: 0,
        };
        let scale = play(task, Policy::D40Control);
        let suppress = play(task, Policy::NeverLateScale);
        assert_eq!(scale.decision.eligible, suppress.decision.eligible);
        assert_eq!(scale.decision.turn, suppress.decision.turn);
        assert_eq!(scale.decision.state_hash, suppress.decision.state_hash);
        assert_eq!(scale.decision.probability, suppress.decision.probability);
    }
}
