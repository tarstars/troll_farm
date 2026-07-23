//! Generate the frozen outcome-blind D97 joint concrete-job arm manifest.

use std::collections::BTreeSet;
use std::fs::OpenOptions;
use std::io::{BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroDecisionStage, MacroOpponentMode,
    MacroSelectionBranch, PlantOwner, MACRO_CELLS, MACRO_TOTAL_TURNS,
};

const OWNER_LABELS: [&str; 4] = ["natural", "own", "opponent", "ambiguous"];
const JOB_LABELS: [&str; 6] = ["idle", "bank", "fell", "harvest", "renew", "mine"];

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
struct Root {
    root_id: usize,
    task: Task,
    decision_ordinal: usize,
    turn: i32,
    state_hash: u64,
    observation_hash: u64,
    candidate_count: usize,
    live_own_crops: usize,
    first_worker_id: i32,
    first_worker_ordinal: usize,
    first_catalog: Vec<OptionChoice>,
    first_catalog_hash: u64,
    teacher_second_worker_id: i32,
    teacher_second_worker_ordinal: usize,
}

#[derive(Clone, Debug)]
struct Arm {
    root: Root,
    kind: &'static str,
    arm_id: String,
    first: OptionChoice,
    second: OptionChoice,
    second_state_hash: u64,
    second_observation_hash: u64,
    second_candidate_count: usize,
    second_catalog_size: usize,
    second_catalog_hash: u64,
    second_worker_id: i32,
    second_worker_ordinal: usize,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
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
    let label = format!("{}@{}", class, action);
    OptionChoice {
        label,
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
        if !classes.insert(class) {
            continue;
        }
        result.push(choice(observation, index, rank, false));
    }
    assert_eq!(
        result.len(),
        result
            .iter()
            .map(|option| option.action)
            .collect::<BTreeSet<_>>()
            .len(),
        "D97 duplicate catalog action"
    );
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

fn find_root(task: Task, root_id: usize) -> Option<Root> {
    let mut env = make_env(task);
    for decision_ordinal in 0..5_000usize {
        let observation = env.candidate_observation();
        let teacher_action = observation.actions[observation.teacher_index] as usize;
        let turn = env.state.turn;
        let own_crops = live_own_crops(&env);
        let preliminary = env.stage() == MacroDecisionStage::Worker
            && observation.branch == MacroSelectionBranch::Rate
            && own_crops > 0
            && turn <= MACRO_TOTAL_TURNS - 30;
        let state_hash = env.state_hash();
        let first_worker_id = env.current_unit_id();
        let first_catalog = preliminary.then(|| catalog(&observation, own_crops));
        let first_observation_hash = observation_hash(&observation);
        let first_candidate_count = observation.actions.len();
        let terminal = env.step(teacher_action);
        if preliminary
            && !terminal.done
            && env.state.turn == turn
            && env.stage() == MacroDecisionStage::Worker
        {
            let second = env.candidate_observation();
            if second.branch == MacroSelectionBranch::Rate {
                let first_worker_id = first_worker_id.expect("D97 first root worker");
                let second_worker_id = env.current_unit_id().expect("D97 second root worker");
                let first_catalog = first_catalog.expect("D97 first root catalog");
                return Some(Root {
                    root_id,
                    task,
                    decision_ordinal,
                    turn,
                    state_hash,
                    observation_hash: first_observation_hash,
                    candidate_count: first_candidate_count,
                    live_own_crops: own_crops,
                    first_worker_id,
                    first_worker_ordinal: worker_ordinal_at_state(&env, first_worker_id),
                    first_catalog_hash: catalog_hash(&first_catalog),
                    first_catalog,
                    teacher_second_worker_id: second_worker_id,
                    teacher_second_worker_ordinal: worker_ordinal(&env, second_worker_id),
                });
            }
        }
        if terminal.done {
            return None;
        }
    }
    panic!("D97 decision loop while finding root: {task:?}")
}

// The first worker has already entered the active-job map when find_root checks the second stage,
// but stable ordinal depends only on the live unit ids and is therefore still recoverable.
fn worker_ordinal_at_state(env: &CompleteMacroEnv, unit_id: i32) -> usize {
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
        .expect("D97 prior worker remains live")
}

fn replay_root(root: &Root) -> CompleteMacroEnv {
    let mut env = make_env(root.task);
    for _ in 0..root.decision_ordinal {
        let observation = env.candidate_observation();
        let terminal = env.step(observation.actions[observation.teacher_index] as usize);
        assert!(!terminal.done, "D97 replay ended before root");
    }
    let observation = env.candidate_observation();
    assert_eq!(env.state.turn, root.turn, "D97 replay root turn");
    assert_eq!(env.state_hash(), root.state_hash, "D97 replay root state");
    assert_eq!(
        observation_hash(&observation),
        root.observation_hash,
        "D97 replay root observation"
    );
    assert_eq!(
        observation.actions.len(),
        root.candidate_count,
        "D97 replay root candidate count"
    );
    assert_eq!(
        env.current_unit_id(),
        Some(root.first_worker_id),
        "D97 replay first worker"
    );
    let reconstructed = catalog(&observation, root.live_own_crops);
    assert_eq!(
        reconstructed, root.first_catalog,
        "D97 replay first catalog"
    );
    env
}

fn task_arms(task: Task, root_id: usize) -> Vec<Arm> {
    let Some(root) = find_root(task, root_id) else {
        return Vec::new();
    };
    let mut arms = Vec::new();
    for first in &root.first_catalog {
        let mut env = replay_root(&root);
        let terminal = env.step(first.action as usize);
        if terminal.done || env.state.turn != root.turn || env.stage() != MacroDecisionStage::Worker
        {
            continue;
        }
        let second_observation = env.candidate_observation();
        if second_observation.branch != MacroSelectionBranch::Rate {
            continue;
        }
        let second_worker_id = env.current_unit_id().expect("D97 second arm worker");
        let second_worker_ordinal = worker_ordinal(&env, second_worker_id);
        let second_state_hash = env.state_hash();
        let second_observation_hash = observation_hash(&second_observation);
        let second_candidate_count = second_observation.actions.len();
        let second_catalog = catalog(&second_observation, live_own_crops(&env));
        let second_catalog_size = second_catalog.len();
        let second_catalog_hash = catalog_hash(&second_catalog);
        for second in second_catalog {
            let kind = match (first.teacher, second.teacher) {
                (true, true) => "control",
                (false, true) => "single_first",
                (true, false) => "single_second",
                (false, false) => "joint",
            };
            arms.push(Arm {
                root: root.clone(),
                kind,
                arm_id: format!("r{:04}__{}__{}", root.root_id, first.label, second.label),
                first: first.clone(),
                second,
                second_state_hash,
                second_observation_hash,
                second_candidate_count,
                second_catalog_size,
                second_catalog_hash,
                second_worker_id,
                second_worker_ordinal,
            });
        }
    }
    assert_eq!(
        arms.iter().filter(|arm| arm.kind == "control").count(),
        1,
        "D97 one control arm per root"
    );
    assert_eq!(
        arms.len(),
        arms.iter()
            .map(|arm| &arm.arm_id)
            .collect::<BTreeSet<_>>()
            .len(),
        "D97 duplicate arm id"
    );
    arms
}

fn option_columns(option: &OptionChoice) -> [String; 11] {
    [
        option.label.clone(),
        option.class.clone(),
        option.action.to_string(),
        option.prior_rank.to_string(),
        JOB_LABELS[option.job_kind].to_string(),
        option
            .owner
            .map_or("none", |owner| OWNER_LABELS[owner])
            .to_string(),
        option.target.map_or(-1, i32::from).to_string(),
        option.predicted_deposit[0].to_string(),
        option.predicted_deposit[1].to_string(),
        option.predicted_deposit[2].to_string(),
        option.predicted_deposit[3].to_string(),
    ]
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        5,
        "usage: d97_joint_concrete_manifest START_SEED MAPS OUTPUT THREADS"
    );
    let start_seed: i64 = parse(&args[1], "start seed");
    let maps: usize = parse(&args[2], "maps");
    let output = &args[3];
    let threads: usize = parse(&args[4], "threads");
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
    let tasks = Arc::new(tasks);
    let next = Arc::new(AtomicUsize::new(0));
    let arms = Arc::new(Mutex::new(Vec::new()));
    let started = Instant::now();
    let handles: Vec<_> = (0..threads.min(tasks.len()))
        .map(|_| {
            let tasks = Arc::clone(&tasks);
            let next = Arc::clone(&next);
            let arms = Arc::clone(&arms);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(&task) = tasks.get(index) else {
                    break;
                };
                let mut task_rows = task_arms(task, index);
                arms.lock()
                    .expect("D97 manifest row lock")
                    .append(&mut task_rows);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D97 manifest worker");
    }
    let mut arms = Arc::try_unwrap(arms)
        .ok()
        .expect("sole D97 manifest rows")
        .into_inner()
        .expect("D97 manifest row lock");
    arms.sort_by_key(|arm| {
        (
            arm.root.task,
            arm.root.root_id,
            arm.first.label.clone(),
            arm.second.label.clone(),
        )
    });

    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(output)
        .expect("create D97 manifest without overwrite");
    let mut writer = BufWriter::new(target);
    writeln!(writer, "root_id\tmap_seed\tseat\topponent_index\topponent\tdecision_ordinal\tturn\troot_state_hash\troot_observation_hash\troot_candidate_count\tlive_own_crops\tfirst_worker_id\tfirst_worker_ordinal\tfirst_catalog_size\tfirst_catalog_hash\tteacher_second_worker_id\tteacher_second_worker_ordinal\tarm_kind\tarm_id\tfirst_label\tfirst_class\tfirst_action\tfirst_prior_rank\tfirst_job_kind\tfirst_owner\tfirst_target\tfirst_deposit_plum\tfirst_deposit_lemon\tfirst_deposit_apple\tfirst_deposit_iron\tsecond_state_hash\tsecond_observation_hash\tsecond_candidate_count\tsecond_worker_id\tsecond_worker_ordinal\tsecond_catalog_size\tsecond_catalog_hash\tsecond_label\tsecond_class\tsecond_action\tsecond_prior_rank\tsecond_job_kind\tsecond_owner\tsecond_target\tsecond_deposit_plum\tsecond_deposit_lemon\tsecond_deposit_apple\tsecond_deposit_iron").expect("write D97 manifest header");
    for arm in &arms {
        let first = option_columns(&arm.first);
        let second = option_columns(&arm.second);
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            arm.root.root_id,
            arm.root.task.map_seed,
            arm.root.task.seat,
            arm.root.task.opponent,
            MacroOpponentMode::from_index(arm.root.task.opponent).label(),
            arm.root.decision_ordinal,
            arm.root.turn,
            arm.root.state_hash,
            arm.root.observation_hash,
            arm.root.candidate_count,
            arm.root.live_own_crops,
            arm.root.first_worker_id,
            arm.root.first_worker_ordinal,
            arm.root.first_catalog.len(),
            arm.root.first_catalog_hash,
            arm.root.teacher_second_worker_id,
            arm.root.teacher_second_worker_ordinal,
            arm.kind,
            arm.arm_id,
            first[0], first[1], first[2], first[3], first[4], first[5], first[6], first[7], first[8], first[9], first[10],
            arm.second_state_hash,
            arm.second_observation_hash,
            arm.second_candidate_count,
            arm.second_worker_id,
            arm.second_worker_ordinal,
            arm.second_catalog_size,
            arm.second_catalog_hash,
            second[0], second[1], second[2], second[3], second[4], second[5], second[6], second[7], second[8], second[9], second[10],
        )
        .expect("write D97 manifest row");
    }
    writer.flush().expect("flush D97 manifest");
    let roots = arms
        .iter()
        .map(|arm| arm.root.root_id)
        .collect::<BTreeSet<_>>()
        .len();
    eprintln!(
        "saved {roots} roots and {} arms in {:.3}s",
        arms.len(),
        started.elapsed().as_secs_f64()
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_task_manifest_is_deterministic_and_has_one_control() {
        let task = Task {
            map_seed: 9_820_000,
            seat: 0,
            opponent: 0,
        };
        let left = task_arms(task, 0);
        let right = task_arms(task, 0);
        assert_eq!(left.len(), right.len());
        assert!(!left.is_empty());
        assert_eq!(left.iter().filter(|arm| arm.kind == "control").count(), 1);
        assert_eq!(
            left.iter().map(|arm| &arm.arm_id).collect::<Vec<_>>(),
            right.iter().map(|arm| &arm.arm_id).collect::<Vec<_>>()
        );
    }
}
