//! Reconstruct D98 expert proposals at the immutable D97 joint-assignment roots.

use std::collections::{BTreeMap, BTreeSet};
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Instant;

use troll_farm::d41b_prior_kernel::exact_prior_order;
use troll_farm::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroDecisionStage, MacroOpponentMode,
    MacroSelectionBranch, PlantOwner, MACRO_CELLS, MACRO_TOTAL_TURNS,
};

const FEATURES: usize = 153;
const GLOBAL_FEATURES: usize = 56;
const SHARED_FEATURES: usize = 46;
const CANDIDATE_FEATURES: usize = 44;
const ORDINALS: usize = 3;
const OWNER_LABELS: [&str; 4] = ["natural", "own", "opponent", "ambiguous"];
const JOB_LABELS: [&str; 6] = ["idle", "bank", "fell", "harvest", "renew", "mine"];

#[derive(Clone, Debug)]
struct Expert {
    label: String,
    weights: [f32; FEATURES],
    hash: u64,
}

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
    opponent_label: String,
    decision_ordinal: usize,
    turn: i32,
    state_hash: u64,
    observation_hash: u64,
    candidate_count: usize,
    live_own_crops: usize,
    first_worker_id: i32,
    first_worker_ordinal: usize,
    first_catalog_size: usize,
    first_catalog_hash: u64,
}

#[derive(Clone, Debug)]
struct ProposalRow {
    root: Root,
    expert_index: usize,
    expert_label: String,
    expert_hash: u64,
    global_hash: u64,
    first: OptionChoice,
    second: Option<OptionChoice>,
    second_state_hash: Option<u64>,
    second_observation_hash: Option<u64>,
    second_catalog_hash: Option<u64>,
    arm_kind: &'static str,
    arm_id: Option<String>,
    paired_boundary: bool,
}

fn parse<T: std::str::FromStr>(value: &str, label: &str) -> T {
    value
        .parse()
        .unwrap_or_else(|_| panic!("invalid {label}: {value:?}"))
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

fn float_hash(values: &[f32]) -> u64 {
    let mut hash = 0xcbf29ce484222325;
    mix(&mut hash, values.len() as u64);
    for value in values {
        mix(&mut hash, u64::from(value.to_bits()));
    }
    hash
}

fn read_experts(path: &str) -> Vec<Expert> {
    let source = BufReader::new(File::open(path).expect("open D104 D98 population"));
    let mut lines = source.lines();
    let expected_header = ["policy", "kind", "budget"]
        .into_iter()
        .map(str::to_string)
        .chain((0..FEATURES).map(|index| format!("param_{index:03}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D104 population header").unwrap(),
        expected_header
    );
    let mut experts = Vec::new();
    for line in lines {
        let line = line.expect("read D104 population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), FEATURES + 3);
        if fields[1] != "four" {
            continue;
        }
        assert_eq!(parse::<u32>(fields[2], "D104 expert budget"), 4);
        let mut weights = [0.0f32; FEATURES];
        let mut hash = 0xcbf29ce484222325;
        for (target, value) in weights.iter_mut().zip(&fields[3..]) {
            *target = parse(value, "D104 expert weight");
            assert!(target.is_finite());
            mix(&mut hash, u64::from(target.to_bits()));
        }
        experts.push(Expert {
            label: fields[0].to_string(),
            weights,
            hash,
        });
    }
    assert_eq!(experts.len(), 64);
    for (index, expert) in experts.iter().enumerate() {
        assert_eq!(expert.label, format!("four_{index:02}"));
    }
    experts
}

fn root_from_fields(fields: &[&str]) -> Root {
    assert!(fields.len() >= 48, "D104 short D97 manifest row");
    Root {
        root_id: parse(fields[0], "D104 root id"),
        task: Task {
            map_seed: parse(fields[1], "D104 map seed"),
            seat: parse(fields[2], "D104 seat"),
            opponent: parse(fields[3], "D104 opponent index"),
        },
        opponent_label: fields[4].to_string(),
        decision_ordinal: parse(fields[5], "D104 decision ordinal"),
        turn: parse(fields[6], "D104 turn"),
        state_hash: parse(fields[7], "D104 root state hash"),
        observation_hash: parse(fields[8], "D104 root observation hash"),
        candidate_count: parse(fields[9], "D104 root candidate count"),
        live_own_crops: parse(fields[10], "D104 live own crops"),
        first_worker_id: parse(fields[11], "D104 first worker id"),
        first_worker_ordinal: parse(fields[12], "D104 first worker ordinal"),
        first_catalog_size: parse(fields[13], "D104 first catalog size"),
        first_catalog_hash: parse(fields[14], "D104 first catalog hash"),
    }
}

fn same_root(left: &Root, right: &Root) -> bool {
    left.root_id == right.root_id
        && left.task == right.task
        && left.opponent_label == right.opponent_label
        && left.decision_ordinal == right.decision_ordinal
        && left.turn == right.turn
        && left.state_hash == right.state_hash
        && left.observation_hash == right.observation_hash
        && left.candidate_count == right.candidate_count
        && left.live_own_crops == right.live_own_crops
        && left.first_worker_id == right.first_worker_id
        && left.first_worker_ordinal == right.first_worker_ordinal
        && left.first_catalog_size == right.first_catalog_size
        && left.first_catalog_hash == right.first_catalog_hash
}

fn read_roots(path: &str) -> Vec<Root> {
    let source = BufReader::new(File::open(path).expect("open D104 D97 manifest"));
    let mut lines = source.lines();
    let header = lines.next().expect("D104 manifest header").unwrap();
    assert_eq!(header.split('\t').count(), 48);
    let mut roots = BTreeMap::new();
    for line in lines {
        let line = line.expect("read D104 manifest row");
        let fields: Vec<_> = line.split('\t').collect();
        let root = root_from_fields(&fields);
        if let Some(previous) = roots.get(&root.root_id) {
            assert!(
                same_root(previous, &root),
                "D104 inconsistent repeated root"
            );
        } else {
            roots.insert(root.root_id, root);
        }
    }
    let roots: Vec<_> = roots.into_values().collect();
    assert_eq!(roots.len(), 240);
    assert!(roots.iter().all(|root| root.root_id < 256));
    assert!(roots
        .windows(2)
        .all(|pair| pair[0].root_id < pair[1].root_id));
    roots
}

fn make_env(task: Task) -> CompleteMacroEnv {
    CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    )
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

fn owner_index(owner: PlantOwner) -> usize {
    match owner {
        PlantOwner::Natural => 0,
        PlantOwner::Own => 1,
        PlantOwner::Opponent => 2,
        PlantOwner::Ambiguous => 3,
    }
}

fn batch_features(env: &CompleteMacroEnv, completed_batches: u32) -> [f32; GLOBAL_FEATURES] {
    let own = env.seat;
    let opponent = 1 - own;
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
    let mut result = [0.0f32; GLOBAL_FEATURES];
    result[0] = 1.0;
    result[1] = env.state.turn as f32 / MACRO_TOTAL_TURNS as f32;
    result[2] = own_units.len() as f32 / 3.0;
    result[3] = opponent_units.len() as f32 / 3.0;
    result[4] = env.state.scores[own] as f32 / 400.0;
    result[5] = env.state.scores[opponent] as f32 / 400.0;
    result[6] = (env.state.scores[own] - env.state.scores[opponent]) as f32 / 400.0;
    for item in 0..6 {
        result[7 + item] = env.state.inventories[own][item] as f32 / 20.0;
        result[13 + item] = env.state.inventories[opponent][item] as f32 / 20.0;
        result[19 + item] =
            own_units.iter().map(|unit| unit.carry[item]).sum::<i32>() as f32 / 20.0;
        result[25 + item] = opponent_units
            .iter()
            .map(|unit| unit.carry[item])
            .sum::<i32>() as f32
            / 20.0;
    }
    let mut plant_counts = [0usize; 4];
    let mut fruit_counts = [0i32; 4];
    for plant in env.state.plants.iter().filter(|plant| plant.health > 0) {
        let index = owner_index(*env.owners().get(&plant.pos()).expect("D104 provenance"));
        plant_counts[index] += 1;
        fruit_counts[index] = fruit_counts[index].saturating_add(plant.fruits);
    }
    for index in 0..4 {
        result[31 + index] = plant_counts[index] as f32 / 20.0;
        result[35 + index] = fruit_counts[index] as f32 / 40.0;
    }
    result[39] = f32::from(plant_counts[1] > 0);
    result[40] = f32::from(plant_counts[2] > 0);
    result[41 + env.train_goal().action_plane()] = 1.0;
    if completed_batches > 0 {
        result[44] = 1.0;
    }
    result[48] = completed_batches as f32 / 100.0;
    result[52] = env.state.water.len() as f32 / MACRO_CELLS as f32;
    result[53] = env.state.walkable.len() as f32 / MACRO_CELLS as f32;
    result[54] = own_units.iter().map(|unit| unit.hp).sum::<i32>() as f32 / 12.0;
    result[55] = own_units.iter().map(|unit| unit.chop).sum::<i32>() as f32 / 12.0;
    assert!(result.iter().all(|value| value.is_finite()));
    result
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
        .expect("D104 current worker ordinal")
}

fn one_hot_index(
    features: &[f32; CANDIDATE_FEATURES],
    start: usize,
    count: usize,
) -> Option<usize> {
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
    let job_kind = one_hot_index(features, 20, 6).expect("D104 worker job one-hot");
    let owner = one_hot_index(features, 30, 4);
    let action = observation.actions[index];
    let target = (2..=5)
        .contains(&job_kind)
        .then_some(action.rem_euclid(MACRO_CELLS as i32));
    let predicted_deposit = std::array::from_fn(|slot| (features[34 + slot] * 10.0).round() as i32);
    let class = if teacher {
        "keep".to_string()
    } else if job_kind == 5 {
        "mine".to_string()
    } else {
        format!(
            "{}:{}",
            JOB_LABELS[job_kind],
            OWNER_LABELS[owner.expect("D104 crop job provenance")]
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
    assert_eq!(order[0], observation.teacher_index);
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
    assert_eq!(
        result.len(),
        result
            .iter()
            .map(|option| option.action)
            .collect::<BTreeSet<_>>()
            .len()
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

#[allow(clippy::too_many_arguments)]
fn score_features(
    global: &[f32; GLOBAL_FEATURES],
    shared: &[f32; SHARED_FEATURES],
    candidate: &[f32; CANDIDATE_FEATURES],
    ordinal: usize,
    position: usize,
    remaining_budget: u32,
    prior_rank: usize,
    candidate_count: usize,
) -> [f32; FEATURES] {
    let mut result = [0.0f32; FEATURES];
    result[..GLOBAL_FEATURES].copy_from_slice(global);
    result[GLOBAL_FEATURES..GLOBAL_FEATURES + SHARED_FEATURES].copy_from_slice(shared);
    let candidate_start = GLOBAL_FEATURES + SHARED_FEATURES;
    result[candidate_start..candidate_start + CANDIDATE_FEATURES].copy_from_slice(candidate);
    let ordinal_start = candidate_start + CANDIDATE_FEATURES;
    result[ordinal_start + ordinal] = 1.0;
    let position_start = ordinal_start + ORDINALS;
    result[position_start + position] = 1.0;
    result[position_start + 2] = remaining_budget as f32 / 4.0;
    result[position_start + 3] = prior_rank as f32 / candidate_count as f32;
    assert!(result.iter().all(|value| value.is_finite()));
    result
}

fn choose(
    observation: &MacroCandidateObservation,
    options: &[OptionChoice],
    expert: &Expert,
    global: &[f32; GLOBAL_FEATURES],
    shared: &[f32; SHARED_FEATURES],
    ordinal: usize,
    position: usize,
    remaining_budget: u32,
) -> OptionChoice {
    let mut selected = options[0].clone();
    let mut best_score = 0.0f32;
    for option in &options[1..] {
        // prior_rank is a rank, not an observation index. Locate by exact action.
        let index = observation
            .actions
            .iter()
            .position(|action| *action == option.action)
            .expect("D104 option action in observation");
        let features = score_features(
            global,
            shared,
            &observation.features[index],
            ordinal,
            position,
            remaining_budget,
            option.prior_rank,
            observation.actions.len(),
        );
        let score: f32 = expert
            .weights
            .iter()
            .zip(features)
            .map(|(weight, feature)| weight * feature)
            .sum();
        assert!(score.is_finite());
        if score.total_cmp(&best_score).is_gt() {
            selected = option.clone();
            best_score = score;
        }
    }
    selected
}

fn replay_root(root: &Root) -> (CompleteMacroEnv, [f32; GLOBAL_FEATURES]) {
    let mut env = make_env(root.task);
    let mut global = [0.0f32; GLOBAL_FEATURES];
    let mut completed_batches = 0u32;
    for _ in 0..root.decision_ordinal {
        let observation = env.candidate_observation();
        if env.stage() == MacroDecisionStage::Train {
            global = batch_features(&env, completed_batches);
            completed_batches += 1;
        }
        let terminal = env.step(observation.actions[observation.teacher_index] as usize);
        assert!(!terminal.done, "D104 replay ended before root");
    }
    let observation = env.candidate_observation();
    assert_eq!(env.state.turn, root.turn);
    assert_eq!(env.state_hash(), root.state_hash);
    assert_eq!(observation_hash(&observation), root.observation_hash);
    assert_eq!(observation.actions.len(), root.candidate_count);
    assert_eq!(env.current_unit_id(), Some(root.first_worker_id));
    assert_eq!(
        worker_ordinal(&env, root.first_worker_id),
        root.first_worker_ordinal
    );
    assert_eq!(live_own_crops(&env), root.live_own_crops);
    let first_catalog = catalog(&observation, root.live_own_crops);
    assert_eq!(first_catalog.len(), root.first_catalog_size);
    assert_eq!(catalog_hash(&first_catalog), root.first_catalog_hash);
    (env, global)
}

#[allow(clippy::too_many_arguments)]
fn proposal(
    root: &Root,
    expert_index: usize,
    expert: &Expert,
    env: &CompleteMacroEnv,
    global: &[f32; GLOBAL_FEATURES],
    first_observation: &MacroCandidateObservation,
    first_catalog: &[OptionChoice],
    first_shared: &[f32; SHARED_FEATURES],
) -> ProposalRow {
    let first = choose(
        first_observation,
        first_catalog,
        expert,
        global,
        first_shared,
        root.first_worker_ordinal,
        0,
        4,
    );
    let Some(preview) = env.pair_branch_preview(first.action as usize) else {
        return ProposalRow {
            root: root.clone(),
            expert_index,
            expert_label: expert.label.clone(),
            expert_hash: expert.hash,
            global_hash: float_hash(global),
            first,
            second: None,
            second_state_hash: None,
            second_observation_hash: None,
            second_catalog_hash: None,
            arm_kind: "unsupported",
            arm_id: None,
            paired_boundary: false,
        };
    };
    if preview.turn != root.turn || preview.observation.branch != MacroSelectionBranch::Rate {
        return ProposalRow {
            root: root.clone(),
            expert_index,
            expert_label: expert.label.clone(),
            expert_hash: expert.hash,
            global_hash: float_hash(global),
            first,
            second: None,
            second_state_hash: None,
            second_observation_hash: None,
            second_catalog_hash: None,
            arm_kind: "unsupported",
            arm_id: None,
            paired_boundary: false,
        };
    }
    let second_catalog = catalog(&preview.observation, preview.live_own_crops);
    let remaining = if first.teacher { 4 } else { 3 };
    let second = choose(
        &preview.observation,
        &second_catalog,
        expert,
        global,
        &preview.shared_context,
        preview.worker_ordinal,
        1,
        remaining,
    );
    let arm_kind = match (first.teacher, second.teacher) {
        (true, true) => "control",
        (false, true) => "single_first",
        (true, false) => "single_second",
        (false, false) => "joint",
    };
    let arm_id = format!("r{:04}__{}__{}", root.root_id, first.label, second.label);
    ProposalRow {
        root: root.clone(),
        expert_index,
        expert_label: expert.label.clone(),
        expert_hash: expert.hash,
        global_hash: float_hash(global),
        first,
        second: Some(second),
        second_state_hash: Some(preview.state_hash),
        second_observation_hash: Some(observation_hash(&preview.observation)),
        second_catalog_hash: Some(catalog_hash(&second_catalog)),
        arm_kind,
        arm_id: Some(arm_id),
        paired_boundary: true,
    }
}

fn parallel_rows(
    roots: Arc<Vec<Root>>,
    experts: Arc<Vec<Expert>>,
    workers: usize,
) -> Vec<ProposalRow> {
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(roots.len() * experts.len())));
    thread::scope(|scope| {
        for _ in 0..workers {
            let roots = Arc::clone(&roots);
            let experts = Arc::clone(&experts);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            scope.spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                if index >= roots.len() {
                    break;
                }
                let root = &roots[index];
                let (env, global) = replay_root(root);
                let first_observation = env.candidate_observation();
                let first_catalog = catalog(&first_observation, root.live_own_crops);
                let first_shared = env.d42_shared_context();
                let mut local = Vec::with_capacity(experts.len());
                for (expert_index, expert) in experts.iter().enumerate() {
                    local.push(proposal(
                        root,
                        expert_index,
                        expert,
                        &env,
                        &global,
                        &first_observation,
                        &first_catalog,
                        &first_shared,
                    ));
                }
                rows.lock().expect("D104 row lock").extend(local);
            });
        }
    });
    let mut rows = Arc::try_unwrap(rows)
        .expect("D104 row references")
        .into_inner()
        .expect("D104 row mutex");
    rows.sort_by_key(|row| (row.root.root_id, row.expert_index));
    assert_eq!(rows.len(), roots.len() * experts.len());
    rows
}

fn text<T: ToString>(value: Option<T>) -> String {
    value.map_or_else(String::new, |value| value.to_string())
}

fn write_rows(path: &str, rows: &[ProposalRow]) {
    let output = File::create(path).expect("create D104 output");
    let mut writer = BufWriter::new(output);
    writeln!(writer, "root_id\tmap_seed\tseat\topponent_index\topponent\tdecision_ordinal\tturn\troot_state_hash\texpert_index\texpert\texpert_hash\tglobal_feature_hash\tfirst_label\tfirst_class\tfirst_action\tfirst_teacher\tsecond_label\tsecond_class\tsecond_action\tsecond_teacher\tsecond_state_hash\tsecond_observation_hash\tsecond_catalog_hash\tarm_kind\tarm_id\tnonkeep_actions\tpaired_boundary").expect("write D104 header");
    for row in rows {
        let second = row.second.as_ref();
        let nonkeep = usize::from(!row.first.teacher)
            + usize::from(second.is_some_and(|option| !option.teacher));
        writeln!(
            writer,
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}",
            row.root.root_id,
            row.root.task.map_seed,
            row.root.task.seat,
            row.root.task.opponent,
            row.root.opponent_label,
            row.root.decision_ordinal,
            row.root.turn,
            row.root.state_hash,
            row.expert_index,
            row.expert_label,
            row.expert_hash,
            row.global_hash,
            row.first.label,
            row.first.class,
            row.first.action,
            u8::from(row.first.teacher),
            second.map_or("", |option| option.label.as_str()),
            second.map_or("", |option| option.class.as_str()),
            text(second.map(|option| option.action)),
            text(second.map(|option| u8::from(option.teacher))),
            text(row.second_state_hash),
            text(row.second_observation_hash),
            text(row.second_catalog_hash),
            row.arm_kind,
            row.arm_id.as_deref().unwrap_or(""),
            nonkeep,
            u8::from(row.paired_boundary),
        )
        .expect("write D104 row");
    }
    writer.flush().expect("flush D104 output");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        5,
        "usage: d104_d98_expert_proposal_coverage D98_POPULATION D97_MANIFEST OUTPUT WORKERS"
    );
    let experts = Arc::new(read_experts(&args[1]));
    let roots = Arc::new(read_roots(&args[2]));
    let workers: usize = parse(&args[4], "D104 workers");
    assert!(workers > 0);
    let started = Instant::now();
    let rows = parallel_rows(Arc::clone(&roots), Arc::clone(&experts), workers);
    let seconds = started.elapsed().as_secs_f64();
    write_rows(&args[3], &rows);
    eprintln!(
        "saved {} D104 expert proposals from {} roots in {:.3}s with {} workers",
        rows.len(),
        roots.len(),
        seconds,
        workers
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn score_feature_layout_is_finite_and_complete() {
        let features = score_features(&[0.25; 56], &[0.5; 46], &[0.75; 44], 2, 1, 3, 7, 10);
        assert_eq!(features.len(), FEATURES);
        assert!(features.iter().all(|value| value.is_finite()));
        assert_eq!(features[148], 1.0);
        assert_eq!(features[150], 1.0);
        assert_eq!(features[151], 0.75);
        assert_eq!(features[152], 0.7);
    }

    #[test]
    fn immutable_first_root_and_expert_reconstruct() {
        let experts = read_experts(
            "../data/analysis/live-agent-6553250/d98a-bounded-whole-game-joint-assignment-population.tsv",
        );
        let roots = read_roots(
            "../data/analysis/live-agent-6553250/d97a-d40-joint-concrete-job-manifest-9820000-9820015.tsv",
        );
        let root = &roots[0];
        let (env, global) = replay_root(root);
        let observation = env.candidate_observation();
        let first_catalog = catalog(&observation, root.live_own_crops);
        let shared = env.d42_shared_context();
        let row = proposal(
            root,
            0,
            &experts[0],
            &env,
            &global,
            &observation,
            &first_catalog,
            &shared,
        );
        assert_eq!(row.root.root_id, 0);
        assert_eq!(row.expert_label, "four_00");
        assert!(row.paired_boundary);
        assert!(row.arm_id.is_some());
    }
}
