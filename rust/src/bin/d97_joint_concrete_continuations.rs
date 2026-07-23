//! Execute the immutable D97 joint concrete-job continuation manifest.

use std::collections::{BTreeMap, BTreeSet};
use std::fs::{File, OpenOptions};
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroDecisionStage, MacroOpponentMode,
    MacroSelectionBranch, MacroTerminal, PlantOwner, MACRO_ACTION_PLANES, MACRO_CELLS,
};

const OWNER_LABELS: [&str; 4] = ["natural", "own", "opponent", "ambiguous"];
const JOB_LABELS: [&str; 6] = ["idle", "bank", "fell", "harvest", "renew", "mine"];
const MANIFEST_HEADER: &str = "root_id\tmap_seed\tseat\topponent_index\topponent\tdecision_ordinal\tturn\troot_state_hash\troot_observation_hash\troot_candidate_count\tlive_own_crops\tfirst_worker_id\tfirst_worker_ordinal\tfirst_catalog_size\tfirst_catalog_hash\tteacher_second_worker_id\tteacher_second_worker_ordinal\tarm_kind\tarm_id\tfirst_label\tfirst_class\tfirst_action\tfirst_prior_rank\tfirst_job_kind\tfirst_owner\tfirst_target\tfirst_deposit_plum\tfirst_deposit_lemon\tfirst_deposit_apple\tfirst_deposit_iron\tsecond_state_hash\tsecond_observation_hash\tsecond_candidate_count\tsecond_worker_id\tsecond_worker_ordinal\tsecond_catalog_size\tsecond_catalog_hash\tsecond_label\tsecond_class\tsecond_action\tsecond_prior_rank\tsecond_job_kind\tsecond_owner\tsecond_target\tsecond_deposit_plum\tsecond_deposit_lemon\tsecond_deposit_apple\tsecond_deposit_iron";

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Debug, Eq, PartialEq)]
struct OptionChoice {
    label: String,
    class: String,
    action: i32,
    prior_rank: usize,
    teacher: bool,
    job_kind: usize,
    owner: Option<usize>,
    target: Option<i32>,
    predicted_deposit: [i32; 4],
}

#[derive(Clone, Debug)]
struct ManifestArm {
    row_index: usize,
    root_id: usize,
    task: Task,
    opponent_label: String,
    decision_ordinal: usize,
    turn: i32,
    root_state_hash: u64,
    root_observation_hash: u64,
    root_candidate_count: usize,
    live_own_crops: usize,
    first_worker_id: i32,
    first_worker_ordinal: usize,
    first_catalog_size: usize,
    first_catalog_hash: u64,
    teacher_second_worker_id: i32,
    teacher_second_worker_ordinal: usize,
    arm_kind: String,
    arm_id: String,
    first: OptionChoice,
    second_state_hash: u64,
    second_observation_hash: u64,
    second_candidate_count: usize,
    second_worker_id: i32,
    second_worker_ordinal: usize,
    second_catalog_size: usize,
    second_catalog_hash: u64,
    second: OptionChoice,
}

#[derive(Clone, Copy, Debug)]
struct Outcome {
    terminal: MacroTerminal,
    reward_identity_error: f32,
    terminal_live_own_plants: usize,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

#[derive(Clone, Debug)]
struct ArmResult {
    arm: ManifestArm,
    outcome: Outcome,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
}

fn owner_index(label: &str) -> Option<usize> {
    (label != "none").then(|| {
        OWNER_LABELS
            .iter()
            .position(|candidate| *candidate == label)
            .unwrap_or_else(|| panic!("unknown D97 owner: {label}"))
    })
}

fn job_index(label: &str) -> usize {
    JOB_LABELS
        .iter()
        .position(|candidate| *candidate == label)
        .unwrap_or_else(|| panic!("unknown D97 job: {label}"))
}

fn parse_choice(fields: &[&str], start: usize) -> OptionChoice {
    let target = parse::<i32>(fields[start + 6], "D97 target");
    OptionChoice {
        label: fields[start].to_string(),
        class: fields[start + 1].to_string(),
        action: parse(fields[start + 2], "D97 action"),
        prior_rank: parse(fields[start + 3], "D97 prior rank"),
        teacher: fields[start + 1] == "keep",
        job_kind: job_index(fields[start + 4]),
        owner: owner_index(fields[start + 5]),
        target: (target >= 0).then_some(target),
        predicted_deposit: std::array::from_fn(|slot| {
            parse(fields[start + 7 + slot], "D97 predicted deposit")
        }),
    }
}

fn read_manifest(path: &str) -> Vec<ManifestArm> {
    let source = BufReader::new(File::open(path).expect("open D97 manifest"));
    let mut lines = source.lines();
    assert_eq!(
        lines.next().expect("D97 manifest header").unwrap(),
        MANIFEST_HEADER
    );
    let mut arms = Vec::new();
    for (row_index, line) in lines.enumerate() {
        let line = line.expect("read D97 manifest row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), 48, "malformed D97 manifest row");
        let opponent = parse(fields[3], "D97 opponent index");
        assert_eq!(MacroOpponentMode::from_index(opponent).label(), fields[4]);
        let arm_kind = fields[17].to_string();
        assert!(["control", "single_first", "single_second", "joint"].contains(&arm_kind.as_str()));
        let first = parse_choice(&fields, 19);
        let second = parse_choice(&fields, 37);
        assert_eq!(
            arm_kind.as_str(),
            match (first.teacher, second.teacher) {
                (true, true) => "control",
                (false, true) => "single_first",
                (true, false) => "single_second",
                (false, false) => "joint",
            }
        );
        arms.push(ManifestArm {
            row_index,
            root_id: parse(fields[0], "D97 root ID"),
            task: Task {
                map_seed: parse(fields[1], "D97 map seed"),
                seat: parse(fields[2], "D97 seat"),
                opponent,
            },
            opponent_label: fields[4].to_string(),
            decision_ordinal: parse(fields[5], "D97 decision ordinal"),
            turn: parse(fields[6], "D97 turn"),
            root_state_hash: parse(fields[7], "D97 root state hash"),
            root_observation_hash: parse(fields[8], "D97 root observation hash"),
            root_candidate_count: parse(fields[9], "D97 root candidate count"),
            live_own_crops: parse(fields[10], "D97 live own crops"),
            first_worker_id: parse(fields[11], "D97 first worker ID"),
            first_worker_ordinal: parse(fields[12], "D97 first worker ordinal"),
            first_catalog_size: parse(fields[13], "D97 first catalog size"),
            first_catalog_hash: parse(fields[14], "D97 first catalog hash"),
            teacher_second_worker_id: parse(fields[15], "D97 teacher second worker ID"),
            teacher_second_worker_ordinal: parse(fields[16], "D97 teacher second worker ordinal"),
            arm_kind,
            arm_id: fields[18].to_string(),
            first,
            second_state_hash: parse(fields[30], "D97 second state hash"),
            second_observation_hash: parse(fields[31], "D97 second observation hash"),
            second_candidate_count: parse(fields[32], "D97 second candidate count"),
            second_worker_id: parse(fields[33], "D97 second worker ID"),
            second_worker_ordinal: parse(fields[34], "D97 second worker ordinal"),
            second_catalog_size: parse(fields[35], "D97 second catalog size"),
            second_catalog_hash: parse(fields[36], "D97 second catalog hash"),
            second,
        });
    }
    assert!(!arms.is_empty(), "empty D97 manifest");
    assert_eq!(
        arms.len(),
        arms.iter()
            .map(|arm| arm.arm_id.as_str())
            .collect::<BTreeSet<_>>()
            .len(),
        "duplicate D97 manifest arm"
    );
    arms
}

fn make_env(task: Task) -> CompleteMacroEnv {
    CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    )
}

fn mix(hash: &mut u64, value: u64) {
    for byte in value.to_le_bytes() {
        *hash ^= u64::from(byte);
        *hash = hash.wrapping_mul(0x100000001b3);
    }
}

fn mix_bytes(hash: &mut u64, value: &[u8]) {
    for byte in value {
        *hash ^= u64::from(*byte);
        *hash = hash.wrapping_mul(0x100000001b3);
    }
}

fn observation_hash(observation: &MacroCandidateObservation) -> u64 {
    let mut hash = 0xcbf29ce484222325;
    mix(&mut hash, observation.branch as u64);
    mix(&mut hash, observation.teacher_index as u64);
    mix(&mut hash, observation.actions.len() as u64);
    for (action, features) in observation.actions.iter().zip(&observation.features) {
        mix(&mut hash, *action as u64);
        for feature in features {
            mix(&mut hash, u64::from(feature.to_bits()));
        }
    }
    hash
}

fn live_own_crops(env: &CompleteMacroEnv) -> usize {
    env.state
        .plants
        .iter()
        .filter(|plant| plant.health > 0)
        .filter(|plant| env.owners().get(&plant.pos()) == Some(&PlantOwner::Own))
        .count()
}

fn worker_ordinal(env: &CompleteMacroEnv, unit_id: i32) -> usize {
    let mut ids: Vec<_> = env
        .state
        .units
        .iter()
        .filter(|unit| unit.player as usize == env.seat)
        .map(|unit| unit.id)
        .collect();
    ids.sort_unstable();
    ids.iter()
        .position(|id| *id == unit_id)
        .expect("D97 current worker ordinal")
}

fn one_hot_index(features: &[f32; 44], start: usize, count: usize) -> Option<usize> {
    let selected: Vec<_> = (0..count)
        .filter(|offset| features[start + *offset] > 0.5)
        .collect();
    if selected.len() == 1 {
        Some(selected[0])
    } else {
        None
    }
}

fn choice(
    observation: &MacroCandidateObservation,
    index: usize,
    prior_rank: usize,
    teacher: bool,
) -> OptionChoice {
    let features = &observation.features[index];
    let job_kind = one_hot_index(features, 20, 6).expect("D97 worker job one-hot");
    let owner = one_hot_index(features, 30, 4);
    let targeted = (2..=5).contains(&job_kind);
    let action = observation.actions[index];
    let target = targeted.then_some(action.rem_euclid(MACRO_CELLS as i32));
    let predicted_deposit = std::array::from_fn(|slot| (features[34 + slot] * 10.0).round() as i32);
    let class = if teacher {
        "keep".to_string()
    } else if job_kind == 5 {
        "mine".to_string()
    } else {
        format!(
            "{}:{}",
            JOB_LABELS[job_kind],
            OWNER_LABELS[owner.expect("D97 crop job provenance")]
        )
    };
    OptionChoice {
        label: format!("{}@{}", class, action),
        class,
        action,
        prior_rank,
        teacher,
        job_kind,
        owner,
        target,
        predicted_deposit,
    }
}

fn catalog(observation: &MacroCandidateObservation, own_crops: usize) -> Vec<OptionChoice> {
    assert_eq!(observation.branch, MacroSelectionBranch::Rate);
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    assert_eq!(
        order[0], observation.teacher_index,
        "D97 exact teacher rank"
    );
    let mut result = vec![choice(observation, order[0], 0, true)];
    let mut classes = BTreeSet::new();
    for (rank, index) in order.into_iter().enumerate().skip(1) {
        let features = &observation.features[index];
        let Some(job_kind) = one_hot_index(features, 20, 6) else {
            continue;
        };
        if !(2..=5).contains(&job_kind) {
            continue;
        }
        let owner = one_hot_index(features, 30, 4);
        if job_kind != 5 && owner.is_none() {
            continue;
        }
        if job_kind == 2 && own_crops <= 1 && owner == Some(1) {
            continue;
        }
        let class = if job_kind == 5 {
            "mine".to_string()
        } else {
            format!("{}:{}", JOB_LABELS[job_kind], OWNER_LABELS[owner.unwrap()])
        };
        if classes.insert(class) {
            result.push(choice(observation, index, rank, false));
        }
    }
    result
}

fn catalog_hash(options: &[OptionChoice]) -> u64 {
    let mut hash = 0xcbf29ce484222325;
    mix(&mut hash, options.len() as u64);
    for option in options {
        mix_bytes(&mut hash, option.label.as_bytes());
        mix(&mut hash, option.action as u64);
        mix(&mut hash, option.prior_rank as u64);
        mix(&mut hash, option.job_kind as u64);
        mix(
            &mut hash,
            option.owner.map_or(u64::MAX, |owner| owner as u64),
        );
        mix(
            &mut hash,
            option.target.map_or(u64::MAX, |target| target as u64),
        );
        for value in option.predicted_deposit {
            mix(&mut hash, value as u64);
        }
    }
    hash
}

fn step(
    env: &mut CompleteMacroEnv,
    action: usize,
    action_planes: &mut [u32; MACRO_ACTION_PLANES],
) -> MacroTerminal {
    assert!(env.legal_actions().contains(&action), "D97 illegal action");
    action_planes[action / MACRO_CELLS] += 1;
    env.step(action)
}

fn finish(env: &CompleteMacroEnv, terminal: MacroTerminal, action_planes: [u32; 9]) -> Outcome {
    let reward_identity_error = [
        (terminal.own_return - terminal.own_score as f32 / 100.0).abs(),
        (terminal.opponent_return - terminal.opponent_score as f32 / 100.0).abs(),
        (terminal.margin_return - (terminal.own_score - terminal.opponent_score) as f32 / 100.0)
            .abs(),
    ]
    .into_iter()
    .fold(0.0f32, f32::max);
    Outcome {
        terminal,
        reward_identity_error,
        terminal_live_own_plants: live_own_crops(env),
        action_planes,
    }
}

fn baseline(task: Task) -> Outcome {
    let mut env = make_env(task);
    let mut planes = [0u32; MACRO_ACTION_PLANES];
    loop {
        let observation = env.candidate_observation();
        let terminal = step(
            &mut env,
            observation.actions[observation.teacher_index] as usize,
            &mut planes,
        );
        if terminal.done {
            return finish(&env, terminal, planes);
        }
    }
}

fn treatment(arm: &ManifestArm) -> Outcome {
    let mut env = make_env(arm.task);
    let mut planes = [0u32; MACRO_ACTION_PLANES];
    for _ in 0..arm.decision_ordinal {
        let observation = env.candidate_observation();
        let terminal = step(
            &mut env,
            observation.actions[observation.teacher_index] as usize,
            &mut planes,
        );
        assert!(!terminal.done, "D97 treatment ended before root");
    }
    let first_observation = env.candidate_observation();
    assert_eq!(env.stage(), MacroDecisionStage::Worker);
    assert_eq!(first_observation.branch, MacroSelectionBranch::Rate);
    assert_eq!(env.state.turn, arm.turn);
    assert_eq!(env.state_hash(), arm.root_state_hash);
    assert_eq!(
        observation_hash(&first_observation),
        arm.root_observation_hash
    );
    assert_eq!(first_observation.actions.len(), arm.root_candidate_count);
    assert_eq!(live_own_crops(&env), arm.live_own_crops);
    assert_eq!(env.current_unit_id(), Some(arm.first_worker_id));
    assert_eq!(
        worker_ordinal(&env, arm.first_worker_id),
        arm.first_worker_ordinal
    );
    let first_catalog = catalog(&first_observation, arm.live_own_crops);
    assert_eq!(first_catalog.len(), arm.first_catalog_size);
    assert_eq!(catalog_hash(&first_catalog), arm.first_catalog_hash);
    assert!(first_catalog.contains(&arm.first));

    let terminal = step(&mut env, arm.first.action as usize, &mut planes);
    assert!(!terminal.done, "D97 first arm action reached terminal");
    assert_eq!(env.state.turn, arm.turn);
    assert_eq!(env.stage(), MacroDecisionStage::Worker);
    let second_observation = env.candidate_observation();
    assert_eq!(second_observation.branch, MacroSelectionBranch::Rate);
    assert_eq!(env.state_hash(), arm.second_state_hash);
    assert_eq!(
        observation_hash(&second_observation),
        arm.second_observation_hash
    );
    assert_eq!(second_observation.actions.len(), arm.second_candidate_count);
    assert_eq!(env.current_unit_id(), Some(arm.second_worker_id));
    assert_eq!(
        worker_ordinal(&env, arm.second_worker_id),
        arm.second_worker_ordinal
    );
    if arm.first.teacher {
        assert_eq!(arm.second_worker_id, arm.teacher_second_worker_id);
        assert_eq!(arm.second_worker_ordinal, arm.teacher_second_worker_ordinal);
    }
    let second_catalog = catalog(&second_observation, live_own_crops(&env));
    assert_eq!(second_catalog.len(), arm.second_catalog_size);
    assert_eq!(catalog_hash(&second_catalog), arm.second_catalog_hash);
    assert!(second_catalog.contains(&arm.second));

    let mut terminal = step(&mut env, arm.second.action as usize, &mut planes);
    while !terminal.done {
        let observation = env.candidate_observation();
        terminal = step(
            &mut env,
            observation.actions[observation.teacher_index] as usize,
            &mut planes,
        );
    }
    finish(&env, terminal, planes)
}

fn parallel_baselines(tasks: &[Task], threads: usize) -> BTreeMap<Task, Outcome> {
    let tasks = Arc::new(tasks.to_vec());
    let next = Arc::new(AtomicUsize::new(0));
    let outcomes = Arc::new(Mutex::new(BTreeMap::new()));
    let handles: Vec<_> = (0..threads.min(tasks.len()))
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            let outcomes = Arc::clone(&outcomes);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(&task) = tasks.get(index) else {
                    break;
                };
                outcomes
                    .lock()
                    .expect("D97 baseline lock")
                    .insert(task, baseline(task));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D97 baseline worker");
    }
    Arc::try_unwrap(outcomes)
        .ok()
        .expect("sole D97 baselines")
        .into_inner()
        .expect("D97 baseline lock")
}

fn parallel_arms(
    arms: &[ManifestArm],
    baselines: &BTreeMap<Task, Outcome>,
    threads: usize,
) -> Vec<ArmResult> {
    let arms = Arc::new(arms.to_vec());
    let baselines = Arc::new(baselines.clone());
    let next = Arc::new(AtomicUsize::new(0));
    let results = Arc::new(Mutex::new(Vec::with_capacity(arms.len())));
    let handles: Vec<_> = (0..threads.min(arms.len()))
        .map(|_| {
            let arms = Arc::clone(&arms);
            let baselines = Arc::clone(&baselines);
            let next = Arc::clone(&next);
            let results = Arc::clone(&results);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(arm) = arms.get(index) else {
                    break;
                };
                let outcome = treatment(arm);
                if arm.arm_kind == "control" {
                    let expected = baselines[&arm.task];
                    assert_eq!(outcome.terminal, expected.terminal, "D97 control terminal");
                    assert_eq!(
                        outcome.action_planes, expected.action_planes,
                        "D97 control action planes"
                    );
                    assert_eq!(
                        outcome.terminal_live_own_plants, expected.terminal_live_own_plants,
                        "D97 control live crops"
                    );
                }
                results.lock().expect("D97 result lock").push(ArmResult {
                    arm: arm.clone(),
                    outcome,
                });
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D97 arm worker");
    }
    let mut results = Arc::try_unwrap(results)
        .ok()
        .expect("sole D97 results")
        .into_inner()
        .expect("D97 result lock");
    results.sort_by_key(|result| result.arm.row_index);
    results
}

fn terminal_header() -> Vec<&'static str> {
    vec![
        "turn",
        "own_score",
        "opponent_score",
        "margin",
        "own_return",
        "opponent_return",
        "margin_return",
        "reward_identity_error",
        "own_workers",
        "opponent_workers",
        "successful_trains",
        "completed_jobs",
        "invalidated_jobs",
        "invalid_direct_commands",
        "provenance_failures",
        "deposit_prediction_failures",
        "selected_decisions",
        "selected_jobs",
        "selected_nonidle_jobs",
        "selected_renew_jobs",
        "own_created_crops",
        "opponent_created_crops",
        "ambiguous_created_crops",
        "own_owned_crop_harvest_units",
        "own_reinvested_crops",
        "action_hash",
        "state_hash",
        "terminal_live_own_plants",
        "train_none",
        "train_producer",
        "train_chopper",
        "idle",
        "bank",
        "fell_bank",
        "harvest_bank",
        "renew",
        "mine_bank",
    ]
}

fn terminal_columns(outcome: Outcome) -> Vec<String> {
    let terminal = outcome.terminal;
    let mut columns = vec![
        terminal.turn.to_string(),
        terminal.own_score.to_string(),
        terminal.opponent_score.to_string(),
        (terminal.own_score - terminal.opponent_score).to_string(),
        format!("{:.8}", terminal.own_return),
        format!("{:.8}", terminal.opponent_return),
        format!("{:.8}", terminal.margin_return),
        format!("{:.8}", outcome.reward_identity_error),
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
        terminal.own_owned_crop_harvest_units.to_string(),
        terminal.own_reinvested_crops.to_string(),
        terminal.action_hash.to_string(),
        terminal.state_hash.to_string(),
        outcome.terminal_live_own_plants.to_string(),
    ];
    columns.extend(
        outcome
            .action_planes
            .into_iter()
            .map(|value| value.to_string()),
    );
    columns
}

fn write_baselines(path: &str, outcomes: &BTreeMap<Task, Outcome>) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D97 baseline output");
    let mut writer = BufWriter::new(target);
    let mut header = vec!["map_seed", "seat", "opponent"];
    header.extend(terminal_header());
    writeln!(writer, "{}", header.join("\t")).expect("write D97 baseline header");
    for (task, outcome) in outcomes {
        let mut columns = vec![
            task.map_seed.to_string(),
            task.seat.to_string(),
            MacroOpponentMode::from_index(task.opponent)
                .label()
                .to_string(),
        ];
        columns.extend(terminal_columns(*outcome));
        writeln!(writer, "{}", columns.join("\t")).expect("write D97 baseline row");
    }
    writer.flush().expect("flush D97 baseline output");
}

fn write_arms(path: &str, results: &[ArmResult]) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D97 arm output");
    let mut writer = BufWriter::new(target);
    let mut header = vec![
        "map_seed",
        "seat",
        "opponent",
        "root_id",
        "arm_kind",
        "arm_id",
        "first_label",
        "first_class",
        "first_action",
        "second_label",
        "second_class",
        "second_action",
    ];
    header.extend(terminal_header());
    writeln!(writer, "{}", header.join("\t")).expect("write D97 arm header");
    for result in results {
        let arm = &result.arm;
        let mut columns = vec![
            arm.task.map_seed.to_string(),
            arm.task.seat.to_string(),
            arm.opponent_label.clone(),
            arm.root_id.to_string(),
            arm.arm_kind.clone(),
            arm.arm_id.clone(),
            arm.first.label.clone(),
            arm.first.class.clone(),
            arm.first.action.to_string(),
            arm.second.label.clone(),
            arm.second.class.clone(),
            arm.second.action.to_string(),
        ];
        columns.extend(terminal_columns(result.outcome));
        writeln!(writer, "{}", columns.join("\t")).expect("write D97 arm row");
    }
    writer.flush().expect("flush D97 arm output");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        7,
        "usage: d97_joint_concrete_continuations MANIFEST START_SEED MAPS ARM_OUTPUT BASELINE_OUTPUT THREADS"
    );
    let manifest = read_manifest(&args[1]);
    let start_seed: i64 = parse(&args[2], "D97 start seed");
    let maps: usize = parse(&args[3], "D97 maps");
    let threads: usize = parse(&args[6], "D97 threads");
    assert!(maps > 0 && threads > 0);
    let tasks: Vec<_> = (start_seed..start_seed + maps as i64)
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
    let task_set: BTreeSet<_> = tasks.iter().copied().collect();
    assert!(
        manifest.iter().all(|arm| task_set.contains(&arm.task)),
        "D97 manifest task outside frozen grid"
    );
    let started = Instant::now();
    let baselines = parallel_baselines(&tasks, threads);
    let baseline_seconds = started.elapsed().as_secs_f64();
    let arm_started = Instant::now();
    let results = parallel_arms(&manifest, &baselines, threads);
    let arm_seconds = arm_started.elapsed().as_secs_f64();
    write_baselines(&args[5], &baselines);
    write_arms(&args[4], &results);
    eprintln!(
        "saved {} baselines in {:.3}s and {} arms in {:.3}s ({:.3} arms/s)",
        baselines.len(),
        baseline_seconds,
        results.len(),
        arm_seconds,
        results.len() as f64 / arm_seconds,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exact_baseline_is_finite_and_accounted() {
        let outcome = baseline(Task {
            map_seed: 9_820_000,
            seat: 0,
            opponent: 0,
        });
        assert!(outcome.reward_identity_error <= 1.0e-4);
        assert_eq!(
            outcome.action_planes.iter().sum::<u32>(),
            outcome.terminal.selected_decisions
        );
        assert_eq!(
            outcome.terminal.own_score - outcome.terminal.opponent_score,
            (outcome.terminal.margin_return * 100.0).round() as i32
        );
    }
}
