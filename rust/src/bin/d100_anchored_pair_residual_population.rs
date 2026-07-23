//! Evaluate the frozen D100 D98-anchored pair-residual population.

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
    MacroSelectionBranch, MacroTerminal, PlantOwner, MACRO_ACTION_PLANES, MACRO_CANDIDATE_FEATURES,
    MACRO_CELLS, MACRO_TOTAL_TURNS,
};

const PARENT_FEATURES: usize = 153;
const RESIDUAL_FEATURES: usize = 342;
const GLOBAL_FEATURES: usize = 56;
const SHARED_FEATURES: usize = 46;
const CANDIDATE_FEATURES: usize = MACRO_CANDIDATE_FEATURES;
const ORDINALS: usize = 3;
const PAIR_JOB_CLASSES: usize = 5;
const PAIR_OWNER_CLASSES: usize = 5;
const JOBS: usize = 4;
const OWNERS: usize = 4;
const OWNER_LABELS: [&str; OWNERS] = ["natural", "own", "opponent", "ambiguous"];
const JOB_LABELS: [&str; 6] = ["idle", "bank", "fell", "harvest", "renew", "mine"];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum PolicyKind {
    Control,
    Parent,
    ZeroResidual,
    RandomResidual,
}

impl PolicyKind {
    fn label(self) -> &'static str {
        match self {
            Self::Control => "control",
            Self::Parent => "parent",
            Self::ZeroResidual => "zero_residual",
            Self::RandomResidual => "random_residual",
        }
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum PairKind {
    Control,
    SingleFirst,
    SingleSecond,
    Joint,
}

impl PairKind {
    fn index(self) -> Option<usize> {
        match self {
            Self::Control => None,
            Self::SingleFirst => Some(0),
            Self::SingleSecond => Some(1),
            Self::Joint => Some(2),
        }
    }
}

#[derive(Clone, Debug)]
struct Policy {
    label: String,
    kind: PolicyKind,
    parent_label: String,
    parent_budget: u32,
    residual_budget: u32,
    parent_weights: [f32; PARENT_FEATURES],
    residual_weights: [f32; RESIDUAL_FEATURES],
    parent_hash: u64,
    residual_hash: u64,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Debug)]
struct CatalogOption {
    index: usize,
    action: usize,
    prior_rank: usize,
    teacher: bool,
    job_kind: usize,
    owner: Option<usize>,
}

#[derive(Clone, Debug)]
struct PairChoice {
    first: CatalogOption,
    second: CatalogOption,
    kind: PairKind,
    second_turn: i32,
    second_state_hash: u64,
    second_observation_hash: u64,
    second_catalog_hash: u64,
    second_worker_id: i32,
}

#[derive(Clone, Debug)]
struct PairEnumeration {
    parent: PairChoice,
    selected: PairChoice,
    pair_options: u32,
    single_first_options: u32,
    single_second_options: u32,
    joint_options: u32,
    safety_rejections: u32,
    catalog_hash: u64,
}

#[derive(Clone, Copy, Debug, Default)]
struct ResidualStats {
    option_batches: u32,
    eligible_pair_batches: u32,
    scored_assignments: u32,
    intervention_batches: u32,
    nonkeep_assignments: u32,
    joint_batches: u32,
    max_scored_per_batch: u32,
    residual_pair_evaluations: u32,
    residual_overrides: u32,
    residual_joint_overrides: u32,
    max_committed_actions: u32,
    safety_rejections: u32,
    pair_options: u32,
    single_first_options: u32,
    single_second_options: u32,
    joint_options: u32,
    override_control: u32,
    override_single_first: u32,
    override_single_second: u32,
    preview_validations: u32,
    override_job_counts: [u32; JOBS],
    override_owner_counts: [u32; OWNERS],
    pair_hash: u64,
}

#[derive(Clone, Copy, Debug)]
struct Outcome {
    terminal: MacroTerminal,
    reward_identity_error: f32,
    terminal_live_own_plants: usize,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

struct Row {
    policy: usize,
    task: Task,
    outcome: Outcome,
    stats: ResidualStats,
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

fn read_policies(path: &str) -> Vec<Policy> {
    let source = BufReader::new(File::open(path).expect("open D100 population"));
    let mut lines = source.lines();
    let expected_header = [
        "policy",
        "kind",
        "parent",
        "parent_budget",
        "residual_budget",
    ]
    .into_iter()
    .map(str::to_string)
    .chain((0..PARENT_FEATURES).map(|index| format!("parent_{index:03}")))
    .chain((0..RESIDUAL_FEATURES).map(|index| format!("residual_{index:03}")))
    .collect::<Vec<_>>()
    .join("\t");
    assert_eq!(
        lines.next().expect("D100 population header").unwrap(),
        expected_header
    );
    let mut policies = Vec::new();
    for line in lines {
        let line = line.expect("read D100 population row");
        let fields: Vec<_> = line.split('\t').collect();
        assert_eq!(fields.len(), PARENT_FEATURES + RESIDUAL_FEATURES + 5);
        let kind = match fields[1] {
            "control" => PolicyKind::Control,
            "parent" => PolicyKind::Parent,
            "zero_residual" => PolicyKind::ZeroResidual,
            "random_residual" => PolicyKind::RandomResidual,
            other => panic!("unknown D100 policy kind: {other}"),
        };
        let parent_budget = parse(fields[3], "D100 parent budget");
        let residual_budget = parse(fields[4], "D100 residual budget");
        let mut parent_weights = [0.0f32; PARENT_FEATURES];
        let mut residual_weights = [0.0f32; RESIDUAL_FEATURES];
        let mut parent_hash = 0xcbf29ce484222325;
        let mut residual_hash = 0xcbf29ce484222325;
        for (target, value) in parent_weights
            .iter_mut()
            .zip(&fields[5..5 + PARENT_FEATURES])
        {
            *target = parse(value, "D100 parent weight");
            assert!(target.is_finite());
            mix(&mut parent_hash, u64::from(target.to_bits()));
        }
        for (target, value) in residual_weights
            .iter_mut()
            .zip(&fields[5 + PARENT_FEATURES..])
        {
            *target = parse(value, "D100 residual weight");
            assert!(target.is_finite());
            mix(&mut residual_hash, u64::from(target.to_bits()));
        }
        policies.push(Policy {
            label: fields[0].to_string(),
            kind,
            parent_label: fields[2].to_string(),
            parent_budget,
            residual_budget,
            parent_weights,
            residual_weights,
            parent_hash,
            residual_hash,
        });
    }
    assert_eq!(policies.len(), 193);
    let control = &policies[0];
    assert_eq!(control.label, "d40_control");
    assert_eq!(control.kind, PolicyKind::Control);
    assert_eq!((control.parent_budget, control.residual_budget), (0, 0));
    assert!(control.parent_weights.iter().all(|weight| *weight == 0.0));
    assert!(control.residual_weights.iter().all(|weight| *weight == 0.0));
    for index in 0..64 {
        let parent = &policies[1 + 3 * index];
        let zero = &policies[2 + 3 * index];
        let random = &policies[3 + 3 * index];
        assert_eq!(parent.label, format!("parent_{index:02}"));
        assert_eq!(zero.label, format!("zero_{index:02}"));
        assert_eq!(random.label, format!("random_{index:02}"));
        assert_eq!(parent.kind, PolicyKind::Parent);
        assert_eq!(zero.kind, PolicyKind::ZeroResidual);
        assert_eq!(random.kind, PolicyKind::RandomResidual);
        assert_eq!(parent.parent_label, format!("four_{index:02}"));
        assert_eq!(parent.parent_label, zero.parent_label);
        assert_eq!(parent.parent_label, random.parent_label);
        assert_eq!(parent.parent_weights, zero.parent_weights);
        assert_eq!(parent.parent_weights, random.parent_weights);
        assert_eq!(parent.parent_hash, zero.parent_hash);
        assert_eq!(parent.parent_hash, random.parent_hash);
        assert_eq!(
            (
                parent.parent_budget,
                zero.parent_budget,
                random.parent_budget
            ),
            (4, 4, 4)
        );
        assert_eq!(
            (
                parent.residual_budget,
                zero.residual_budget,
                random.residual_budget
            ),
            (0, 1, 1)
        );
        assert!(parent.residual_weights.iter().all(|weight| *weight == 0.0));
        assert!(zero.residual_weights.iter().all(|weight| *weight == 0.0));
    }
    assert_eq!(
        policies
            .iter()
            .map(|policy| policy.label.as_str())
            .collect::<BTreeSet<_>>()
            .len(),
        policies.len()
    );
    policies
}

fn make_env(task: Task) -> CompleteMacroEnv {
    CompleteMacroEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
    )
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
        let index = owner_index(*env.owners().get(&plant.pos()).expect("D100 provenance"));
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
        .expect("D100 worker ordinal")
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

fn catalog(observation: &MacroCandidateObservation, own_crops: usize) -> (Vec<CatalogOption>, u32) {
    assert_eq!(observation.branch, MacroSelectionBranch::Rate);
    let order = exact_prior_order(
        &observation.features,
        &observation.actions,
        observation.branch as u8,
    );
    assert_eq!(order[0], observation.teacher_index);
    let teacher_features = &observation.features[order[0]];
    let teacher_kind = one_hot_index(teacher_features, 20, 6).expect("D100 teacher job kind");
    let mut result = vec![CatalogOption {
        index: order[0],
        action: observation.actions[order[0]] as usize,
        prior_rank: 0,
        teacher: true,
        job_kind: teacher_kind,
        owner: one_hot_index(teacher_features, 30, 4),
    }];
    let mut classes = BTreeSet::new();
    let mut rejected = 0u32;
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
            rejected += 1;
            continue;
        }
        let class = if job_kind == 5 {
            "mine".to_string()
        } else {
            format!("{}:{}", JOB_LABELS[job_kind], OWNER_LABELS[owner.unwrap()])
        };
        if classes.insert(class) {
            result.push(CatalogOption {
                index,
                action: observation.actions[index] as usize,
                prior_rank: rank,
                teacher: false,
                job_kind,
                owner,
            });
        }
    }
    (result, rejected)
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

fn catalog_hash(options: &[CatalogOption]) -> u64 {
    let mut hash = 0xcbf29ce484222325;
    mix(&mut hash, options.len() as u64);
    for option in options {
        mix(&mut hash, option.action as u64);
        mix(&mut hash, option.prior_rank as u64);
        mix(&mut hash, option.job_kind as u64);
        mix(
            &mut hash,
            option.owner.map_or(u64::MAX, |owner| owner as u64),
        );
        mix(&mut hash, option.teacher as u64);
    }
    hash
}

fn pair_kind(first: &CatalogOption, second: &CatalogOption) -> PairKind {
    match (first.teacher, second.teacher) {
        (true, true) => PairKind::Control,
        (false, true) => PairKind::SingleFirst,
        (true, false) => PairKind::SingleSecond,
        (false, false) => PairKind::Joint,
    }
}

fn pair_job_class(option: &CatalogOption) -> usize {
    if option.teacher {
        0
    } else {
        option.job_kind - 1
    }
}

fn pair_owner_class(option: &CatalogOption) -> usize {
    if option.teacher || option.job_kind == 5 {
        0
    } else {
        option.owner.expect("D100 non-mine pair owner") + 1
    }
}

#[allow(clippy::too_many_arguments)]
fn pair_embedding(
    global: &[f32; GLOBAL_FEATURES],
    first_shared: &[f32; SHARED_FEATURES],
    first_candidate: &[f32; CANDIDATE_FEATURES],
    second_shared: &[f32; SHARED_FEATURES],
    second_candidate: &[f32; CANDIDATE_FEATURES],
    first_ordinal: usize,
    second_ordinal: usize,
    kind: PairKind,
    first: &CatalogOption,
    second: &CatalogOption,
    remaining_budget: u32,
    first_candidate_count: usize,
    second_candidate_count: usize,
) -> [f32; RESIDUAL_FEATURES] {
    let mut result = [0.0f32; RESIDUAL_FEATURES];
    let mut start = 0usize;
    result[start..start + GLOBAL_FEATURES].copy_from_slice(global);
    start += GLOBAL_FEATURES;
    result[start..start + SHARED_FEATURES].copy_from_slice(first_shared);
    start += SHARED_FEATURES;
    result[start..start + CANDIDATE_FEATURES].copy_from_slice(first_candidate);
    start += CANDIDATE_FEATURES;
    result[start..start + SHARED_FEATURES].copy_from_slice(second_shared);
    start += SHARED_FEATURES;
    result[start..start + CANDIDATE_FEATURES].copy_from_slice(second_candidate);
    start += CANDIDATE_FEATURES;
    result[start + first_ordinal] = 1.0;
    start += ORDINALS;
    result[start + second_ordinal] = 1.0;
    start += ORDINALS;
    if let Some(index) = kind.index() {
        result[start + index] = 1.0;
    }
    start += 3;
    result[start + pair_job_class(first) * PAIR_JOB_CLASSES + pair_job_class(second)] = 1.0;
    start += PAIR_JOB_CLASSES * PAIR_JOB_CLASSES;
    result[start + pair_owner_class(first) * PAIR_OWNER_CLASSES + pair_owner_class(second)] = 1.0;
    start += PAIR_OWNER_CLASSES * PAIR_OWNER_CLASSES;
    result[start] = remaining_budget as f32 / 4.0;
    result[start + 1] = first.prior_rank as f32 / first_candidate_count as f32;
    result[start + 2] = second.prior_rank as f32 / second_candidate_count as f32;
    start += 3;
    for index in 0..CANDIDATE_FEATURES {
        result[start + index] = first_candidate[index] * second_candidate[index];
    }
    start += CANDIDATE_FEATURES;
    assert_eq!(start, RESIDUAL_FEATURES);
    assert!(result.iter().all(|value| value.is_finite()));
    result
}

fn individual_features(
    global: &[f32; GLOBAL_FEATURES],
    shared: &[f32; SHARED_FEATURES],
    candidate: &[f32; CANDIDATE_FEATURES],
    ordinal: usize,
    position: usize,
    remaining_budget: u32,
    prior_rank: usize,
    candidate_count: usize,
) -> [f32; PARENT_FEATURES] {
    let mut result = [0.0f32; PARENT_FEATURES];
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

fn dot<const N: usize>(weights: &[f32; N], features: &[f32; N]) -> f32 {
    weights
        .iter()
        .zip(features)
        .map(|(weight, feature)| weight * feature)
        .sum()
}

#[allow(clippy::too_many_arguments)]
fn choose_individual(
    observation: &MacroCandidateObservation,
    options: &[CatalogOption],
    weights: &[f32; PARENT_FEATURES],
    global: &[f32; GLOBAL_FEATURES],
    shared: &[f32; SHARED_FEATURES],
    ordinal: usize,
    position: usize,
    remaining_budget: u32,
) -> CatalogOption {
    let mut selected = options[0].clone();
    let mut best_score = 0.0f32;
    for option in options.iter().skip(1) {
        let features = individual_features(
            global,
            shared,
            &observation.features[option.index],
            ordinal,
            position,
            remaining_budget,
            option.prior_rank,
            observation.actions.len(),
        );
        let score = dot(weights, &features);
        assert!(score.is_finite());
        if score.total_cmp(&best_score).is_gt() {
            selected = option.clone();
            best_score = score;
        }
    }
    selected
}

fn choose_pair(
    env: &CompleteMacroEnv,
    observation: &MacroCandidateObservation,
    policy: &Policy,
    global: &[f32; GLOBAL_FEATURES],
    remaining_budget: u32,
) -> Option<PairEnumeration> {
    assert_eq!(env.stage(), MacroDecisionStage::Worker);
    assert_eq!(observation.branch, MacroSelectionBranch::Rate);
    let first_worker = env.current_unit_id().expect("D100 first pair worker");
    let first_ordinal = worker_ordinal(env, first_worker);
    let first_shared = env.d42_shared_context();
    let (first_catalog, first_rejected) = catalog(observation, live_own_crops(env));
    let first_catalog_hash = catalog_hash(&first_catalog);
    let parent_first = choose_individual(
        observation,
        &first_catalog,
        &policy.parent_weights,
        global,
        &first_shared,
        first_ordinal,
        0,
        remaining_budget,
    );
    let parent_preview = env.pair_branch_preview(parent_first.action)?;
    if parent_preview.observation.branch != MacroSelectionBranch::Rate {
        return None;
    }
    let (parent_second_catalog, _) =
        catalog(&parent_preview.observation, parent_preview.live_own_crops);
    let parent_remaining = remaining_budget.saturating_sub(u32::from(!parent_first.teacher));
    let parent_second = choose_individual(
        &parent_preview.observation,
        &parent_second_catalog,
        &policy.parent_weights,
        global,
        &parent_preview.shared_context,
        parent_preview.worker_ordinal,
        1,
        parent_remaining,
    );
    let parent_kind = pair_kind(&parent_first, &parent_second);
    let parent = PairChoice {
        first: parent_first,
        second: parent_second,
        kind: parent_kind,
        second_turn: parent_preview.turn,
        second_state_hash: parent_preview.state_hash,
        second_observation_hash: observation_hash(&parent_preview.observation),
        second_catalog_hash: catalog_hash(&parent_second_catalog),
        second_worker_id: parent_preview.worker_id,
    };
    let parent_embedding = pair_embedding(
        global,
        &first_shared,
        &observation.features[parent.first.index],
        &parent_preview.shared_context,
        &parent_preview.observation.features[parent.second.index],
        first_ordinal,
        parent_preview.worker_ordinal,
        parent.kind,
        &parent.first,
        &parent.second,
        remaining_budget,
        observation.actions.len(),
        parent_preview.observation.actions.len(),
    );
    let mut selected = parent.clone();
    let mut best_score = 0.0f32;
    let mut pair_options = 0u32;
    let mut single_first_options = 0u32;
    let mut single_second_options = 0u32;
    let mut joint_options = 0u32;
    let mut safety_rejections = first_rejected;
    let mut hash = 0xcbf29ce484222325;
    mix(&mut hash, env.state.turn as u64);
    mix(&mut hash, first_worker as u64);
    mix(&mut hash, observation_hash(observation));
    mix(&mut hash, first_catalog_hash);
    for first in &first_catalog {
        let Some(preview) = env.pair_branch_preview(first.action) else {
            continue;
        };
        if preview.observation.branch != MacroSelectionBranch::Rate {
            continue;
        }
        let (second_catalog, second_rejected) =
            catalog(&preview.observation, preview.live_own_crops);
        safety_rejections += second_rejected;
        let second_catalog_hash = catalog_hash(&second_catalog);
        let second_observation_hash = observation_hash(&preview.observation);
        mix(&mut hash, first.action as u64);
        mix(&mut hash, preview.state_hash);
        mix(&mut hash, second_observation_hash);
        mix(&mut hash, second_catalog_hash);
        for second in &second_catalog {
            let kind = pair_kind(first, second);
            pair_options += 1;
            match kind {
                PairKind::Control => {}
                PairKind::SingleFirst => single_first_options += 1,
                PairKind::SingleSecond => single_second_options += 1,
                PairKind::Joint => joint_options += 1,
            }
            mix(&mut hash, first.action as u64);
            mix(&mut hash, second.action as u64);
            mix(&mut hash, kind as u64);
            let choice = PairChoice {
                first: first.clone(),
                second: second.clone(),
                kind,
                second_turn: preview.turn,
                second_state_hash: preview.state_hash,
                second_observation_hash,
                second_catalog_hash,
                second_worker_id: preview.worker_id,
            };
            if choice.first.action == parent.first.action
                && choice.second.action == parent.second.action
            {
                continue;
            }
            let embedding = pair_embedding(
                global,
                &first_shared,
                &observation.features[first.index],
                &preview.shared_context,
                &preview.observation.features[second.index],
                first_ordinal,
                preview.worker_ordinal,
                kind,
                first,
                second,
                remaining_budget,
                observation.actions.len(),
                preview.observation.actions.len(),
            );
            let mut difference = [0.0f32; RESIDUAL_FEATURES];
            for index in 0..RESIDUAL_FEATURES {
                difference[index] = embedding[index] - parent_embedding[index];
            }
            let score = dot(&policy.residual_weights, &difference);
            assert!(score.is_finite());
            if score.total_cmp(&best_score).is_gt() {
                selected = choice;
                best_score = score;
            }
        }
    }
    Some(PairEnumeration {
        parent,
        selected,
        pair_options,
        single_first_options,
        single_second_options,
        joint_options,
        safety_rejections,
        catalog_hash: hash,
    })
}

fn record_override(stats: &mut ResidualStats, option: &CatalogOption) {
    if option.teacher {
        return;
    }
    stats.override_job_counts[option.job_kind - 2] += 1;
    if let Some(owner) = option.owner {
        stats.override_owner_counts[owner] += 1;
    }
}

fn step(
    env: &mut CompleteMacroEnv,
    action: usize,
    planes: &mut [u32; MACRO_ACTION_PLANES],
) -> MacroTerminal {
    assert!(env.legal_actions().contains(&action), "D100 illegal action");
    planes[action / MACRO_CELLS] += 1;
    env.step(action)
}

fn finish(
    env: &CompleteMacroEnv,
    terminal: MacroTerminal,
    planes: [u32; MACRO_ACTION_PLANES],
) -> Outcome {
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
        action_planes: planes,
    }
}

fn play_control(task: Task) -> Outcome {
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

fn finish_batch(stats: &mut ResidualStats, scored: u32, nonkeep: u32) {
    stats.max_scored_per_batch = stats.max_scored_per_batch.max(scored);
    if nonkeep >= 2 {
        stats.joint_batches += 1;
    }
}

fn play(task: Task, policy_index: usize, policy: &Policy) -> Row {
    let mut env = make_env(task);
    let mut stats = ResidualStats {
        pair_hash: 0xcbf29ce484222325,
        ..ResidualStats::default()
    };
    let mut planes = [0u32; MACRO_ACTION_PLANES];
    let mut global = [0.0f32; GLOBAL_FEATURES];
    let mut batch_open = false;
    let mut batch_scored = 0u32;
    let mut batch_nonkeep = 0u32;
    let mut pair_attempted = false;
    let mut pending: Option<PairChoice> = None;
    let mut decisions = 0usize;
    let terminal;
    loop {
        decisions += 1;
        assert!(decisions <= 5_000, "D100 decision loop: {task:?}");
        let observation = env.candidate_observation();
        if let Some(choice) = pending.take() {
            assert_eq!(
                env.stage(),
                MacroDecisionStage::Worker,
                "D100 pending stage"
            );
            assert_eq!(env.state.turn, choice.second_turn, "D100 pending turn");
            assert_eq!(
                env.state_hash(),
                choice.second_state_hash,
                "D100 pending state"
            );
            assert_eq!(
                env.current_unit_id(),
                Some(choice.second_worker_id),
                "D100 pending worker"
            );
            assert_eq!(
                observation_hash(&observation),
                choice.second_observation_hash,
                "D100 pending observation"
            );
            assert_eq!(observation.branch, MacroSelectionBranch::Rate);
            let (reconstructed, _) = catalog(&observation, live_own_crops(&env));
            assert_eq!(
                catalog_hash(&reconstructed),
                choice.second_catalog_hash,
                "D100 pending catalog"
            );
            assert!(
                reconstructed.iter().any(|option| {
                    option.action == choice.second.action
                        && option.teacher == choice.second.teacher
                        && option.job_kind == choice.second.job_kind
                        && option.owner == choice.second.owner
                }),
                "D100 pending option"
            );
            stats.preview_validations += 1;
            let result = step(&mut env, choice.second.action, &mut planes);
            if result.done {
                terminal = result;
                break;
            }
            continue;
        }
        if env.stage() == MacroDecisionStage::Train {
            if batch_open {
                finish_batch(&mut stats, batch_scored, batch_nonkeep);
            }
            global = batch_features(&env, stats.option_batches);
            stats.option_batches += 1;
            batch_open = true;
            batch_scored = 0;
            batch_nonkeep = 0;
            pair_attempted = false;
        }

        // Exact-zero residual evaluation is algebraically the parent choice. Execute the parent
        // path directly; the focused zero-residual pair test below proves the skipped dot-product
        // path selects that same pair.
        let residual_enabled = policy.kind == PolicyKind::RandomResidual;
        let can_attempt_pair = residual_enabled
            && stats.residual_overrides < policy.residual_budget
            && !pair_attempted
            && batch_scored == 0
            && env.stage() == MacroDecisionStage::Worker
            && observation.branch == MacroSelectionBranch::Rate
            && live_own_crops(&env) > 0
            && env.state.turn <= MACRO_TOTAL_TURNS - 30
            && stats.intervention_batches < policy.parent_budget;

        let mut committed = false;
        let action = if can_attempt_pair {
            pair_attempted = true;
            let remaining = policy.parent_budget - stats.intervention_batches;
            if let Some(enumeration) = choose_pair(&env, &observation, policy, &global, remaining) {
                stats.eligible_pair_batches += 1;
                stats.residual_pair_evaluations += 1;
                stats.scored_assignments += 2;
                batch_scored += 2;
                stats.max_committed_actions = stats.max_committed_actions.max(2);
                stats.safety_rejections += enumeration.safety_rejections;
                stats.pair_options += enumeration.pair_options;
                stats.single_first_options += enumeration.single_first_options;
                stats.single_second_options += enumeration.single_second_options;
                stats.joint_options += enumeration.joint_options;
                mix(&mut stats.pair_hash, enumeration.catalog_hash);
                mix(
                    &mut stats.pair_hash,
                    enumeration.selected.first.action as u64,
                );
                mix(
                    &mut stats.pair_hash,
                    enumeration.selected.second.action as u64,
                );
                let is_override = enumeration.selected.first.action
                    != enumeration.parent.first.action
                    || enumeration.selected.second.action != enumeration.parent.second.action;
                let selected = enumeration.selected;
                let nonkeep =
                    u32::from(!selected.first.teacher) + u32::from(!selected.second.teacher);
                if nonkeep > 0 {
                    if batch_nonkeep == 0 {
                        stats.intervention_batches += 1;
                    }
                    batch_nonkeep += nonkeep;
                    stats.nonkeep_assignments += nonkeep;
                }
                if is_override {
                    stats.residual_overrides += 1;
                    match selected.kind {
                        PairKind::Control => stats.override_control += 1,
                        PairKind::SingleFirst => stats.override_single_first += 1,
                        PairKind::SingleSecond => stats.override_single_second += 1,
                        PairKind::Joint => stats.residual_joint_overrides += 1,
                    }
                    record_override(&mut stats, &selected.first);
                    record_override(&mut stats, &selected.second);
                }
                let first_action = selected.first.action;
                pending = Some(selected);
                committed = true;
                first_action
            } else {
                observation.actions[observation.teacher_index] as usize
            }
        } else {
            observation.actions[observation.teacher_index] as usize
        };

        let action = if committed {
            action
        } else {
            let can_score = policy.kind != PolicyKind::Control
                && env.stage() == MacroDecisionStage::Worker
                && observation.branch == MacroSelectionBranch::Rate
                && batch_scored < 2
                && live_own_crops(&env) > 0
                && env.state.turn <= MACRO_TOTAL_TURNS - 30
                && (batch_nonkeep > 0 || stats.intervention_batches < policy.parent_budget);
            if can_score {
                let (options, rejected) = catalog(&observation, live_own_crops(&env));
                let remaining = policy
                    .parent_budget
                    .saturating_sub(stats.intervention_batches);
                let shared = env.d42_shared_context();
                let ordinal =
                    worker_ordinal(&env, env.current_unit_id().expect("D100 sequential worker"));
                let selected = choose_individual(
                    &observation,
                    &options,
                    &policy.parent_weights,
                    &global,
                    &shared,
                    ordinal,
                    batch_scored as usize,
                    remaining,
                );
                stats.safety_rejections += rejected;
                stats.scored_assignments += 1;
                batch_scored += 1;
                mix(&mut stats.pair_hash, catalog_hash(&options));
                mix(&mut stats.pair_hash, selected.action as u64);
                if !selected.teacher {
                    if batch_nonkeep == 0 {
                        stats.intervention_batches += 1;
                    }
                    batch_nonkeep += 1;
                    stats.nonkeep_assignments += 1;
                }
                selected.action
            } else {
                action
            }
        };
        let result = step(&mut env, action, &mut planes);
        if result.done {
            assert!(pending.is_none(), "D100 terminal with pending pair");
            terminal = result;
            break;
        }
    }
    if batch_open {
        finish_batch(&mut stats, batch_scored, batch_nonkeep);
    }
    assert!(pending.is_none());
    assert!(stats.intervention_batches <= policy.parent_budget);
    assert!(stats.residual_overrides <= policy.residual_budget);
    assert!(stats.max_scored_per_batch <= 2);
    assert!(stats.max_committed_actions <= 2);
    assert_eq!(stats.preview_validations, stats.residual_pair_evaluations);
    assert_eq!(
        stats.nonkeep_assignments,
        stats.intervention_batches + stats.joint_batches
    );
    Row {
        policy: policy_index,
        task,
        outcome: finish(&env, terminal, planes),
        stats,
    }
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
                    .expect("D100 baseline lock")
                    .insert(task, play_control(task));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D100 baseline worker");
    }
    Arc::try_unwrap(outcomes)
        .ok()
        .expect("sole D100 baselines")
        .into_inner()
        .expect("D100 baseline lock")
}

fn parallel_rows(
    policies: Arc<Vec<Policy>>,
    tasks: &[Task],
    baselines: &BTreeMap<Task, Outcome>,
    threads: usize,
) -> Vec<Row> {
    let work: Vec<_> = (0..policies.len())
        .flat_map(|policy| tasks.iter().copied().map(move |task| (policy, task)))
        .collect();
    let work = Arc::new(work);
    let baselines = Arc::new(baselines.clone());
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let policies = Arc::clone(&policies);
            let work = Arc::clone(&work);
            let baselines = Arc::clone(&baselines);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(&(policy, task)) = work.get(index) else {
                    break;
                };
                let row = play(task, policy, &policies[policy]);
                if policies[policy].kind == PolicyKind::Control {
                    let expected = baselines[&task];
                    assert_eq!(
                        row.outcome.terminal, expected.terminal,
                        "D100 control terminal"
                    );
                    assert_eq!(
                        row.outcome.action_planes, expected.action_planes,
                        "D100 control action planes"
                    );
                }
                rows.lock().expect("D100 row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D100 population worker");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D100 rows")
        .into_inner()
        .expect("D100 row lock");
    rows.sort_by_key(|row| {
        (
            policies[row.policy].label.clone(),
            row.task.map_seed,
            row.task.seat,
            row.task.opponent,
        )
    });
    rows
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
    let mut result = vec![
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
    result.extend(
        outcome
            .action_planes
            .into_iter()
            .map(|value| value.to_string()),
    );
    result
}

fn write_baselines(path: &str, baselines: &BTreeMap<Task, Outcome>) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D100 baseline output");
    let mut writer = BufWriter::new(target);
    let mut header = vec!["map_seed", "seat", "opponent"];
    header.extend(terminal_header());
    writeln!(writer, "{}", header.join("\t")).expect("write D100 baseline header");
    for (task, outcome) in baselines {
        let mut columns = vec![
            task.map_seed.to_string(),
            task.seat.to_string(),
            MacroOpponentMode::from_index(task.opponent)
                .label()
                .to_string(),
        ];
        columns.extend(terminal_columns(*outcome));
        writeln!(writer, "{}", columns.join("\t")).expect("write D100 baseline row");
    }
    writer.flush().expect("flush D100 baseline output");
}

fn write_rows(path: &str, rows: &[Row], policies: &[Policy]) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D100 population output");
    let mut writer = BufWriter::new(target);
    let mut header = vec![
        "map_seed",
        "seat",
        "opponent",
        "policy",
        "kind",
        "parent",
        "parent_budget",
        "residual_budget",
    ];
    header.extend(terminal_header());
    header.extend([
        "option_batches",
        "eligible_pair_batches",
        "scored_assignments",
        "intervention_batches",
        "nonkeep_assignments",
        "joint_batches",
        "max_scored_per_batch",
        "residual_pair_evaluations",
        "residual_overrides",
        "residual_joint_overrides",
        "max_committed_actions",
        "safety_rejections",
        "pair_options",
        "single_first_options",
        "single_second_options",
        "joint_options",
        "override_control",
        "override_single_first",
        "override_single_second",
        "preview_validations",
        "override_fell",
        "override_harvest",
        "override_renew",
        "override_mine",
        "override_owner_natural",
        "override_owner_own",
        "override_owner_opponent",
        "override_owner_ambiguous",
        "pair_hash",
        "parent_hash",
        "residual_hash",
    ]);
    writeln!(writer, "{}", header.join("\t")).expect("write D100 population header");
    for row in rows {
        let policy = &policies[row.policy];
        let mut columns = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            MacroOpponentMode::from_index(row.task.opponent)
                .label()
                .to_string(),
            policy.label.clone(),
            policy.kind.label().to_string(),
            policy.parent_label.clone(),
            policy.parent_budget.to_string(),
            policy.residual_budget.to_string(),
        ];
        columns.extend(terminal_columns(row.outcome));
        columns.extend([
            row.stats.option_batches.to_string(),
            row.stats.eligible_pair_batches.to_string(),
            row.stats.scored_assignments.to_string(),
            row.stats.intervention_batches.to_string(),
            row.stats.nonkeep_assignments.to_string(),
            row.stats.joint_batches.to_string(),
            row.stats.max_scored_per_batch.to_string(),
            row.stats.residual_pair_evaluations.to_string(),
            row.stats.residual_overrides.to_string(),
            row.stats.residual_joint_overrides.to_string(),
            row.stats.max_committed_actions.to_string(),
            row.stats.safety_rejections.to_string(),
            row.stats.pair_options.to_string(),
            row.stats.single_first_options.to_string(),
            row.stats.single_second_options.to_string(),
            row.stats.joint_options.to_string(),
            row.stats.override_control.to_string(),
            row.stats.override_single_first.to_string(),
            row.stats.override_single_second.to_string(),
            row.stats.preview_validations.to_string(),
            row.stats.override_job_counts[0].to_string(),
            row.stats.override_job_counts[1].to_string(),
            row.stats.override_job_counts[2].to_string(),
            row.stats.override_job_counts[3].to_string(),
            row.stats.override_owner_counts[0].to_string(),
            row.stats.override_owner_counts[1].to_string(),
            row.stats.override_owner_counts[2].to_string(),
            row.stats.override_owner_counts[3].to_string(),
            row.stats.pair_hash.to_string(),
            policy.parent_hash.to_string(),
            policy.residual_hash.to_string(),
        ]);
        writeln!(writer, "{}", columns.join("\t")).expect("write D100 population row");
    }
    writer.flush().expect("flush D100 population output");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(
        args.len(),
        7,
        "usage: d100_anchored_pair_residual_population POPULATION START_SEED MAPS OUTPUT BASELINE_OUTPUT THREADS"
    );
    let policies = Arc::new(read_policies(&args[1]));
    let start_seed: i64 = parse(&args[2], "D100 start seed");
    let maps: usize = parse(&args[3], "D100 maps");
    let threads: usize = parse(&args[6], "D100 threads");
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
    let started = Instant::now();
    let baselines = parallel_baselines(&tasks, threads);
    let baseline_seconds = started.elapsed().as_secs_f64();
    let population_started = Instant::now();
    let rows = parallel_rows(Arc::clone(&policies), &tasks, &baselines, threads);
    let population_seconds = population_started.elapsed().as_secs_f64();
    write_baselines(&args[5], &baselines);
    write_rows(&args[4], &rows, &policies);
    eprintln!(
        "saved {} baselines in {:.3}s and {} rows in {:.3}s ({:.3} episodes/s)",
        baselines.len(),
        baseline_seconds,
        rows.len(),
        population_seconds,
        rows.len() as f64 / population_seconds,
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_policy(kind: PolicyKind) -> Policy {
        Policy {
            label: kind.label().to_string(),
            kind,
            parent_label: if kind == PolicyKind::Control {
                "none".to_string()
            } else {
                "four_00".to_string()
            },
            parent_budget: if kind == PolicyKind::Control { 0 } else { 4 },
            residual_budget: if matches!(
                kind,
                PolicyKind::ZeroResidual | PolicyKind::RandomResidual
            ) {
                1
            } else {
                0
            },
            parent_weights: [0.0; PARENT_FEATURES],
            residual_weights: [0.0; RESIDUAL_FEATURES],
            parent_hash: 1,
            residual_hash: 1,
        }
    }

    #[test]
    fn pair_feature_layout_is_finite_and_complete() {
        let mut global = [0.0; GLOBAL_FEATURES];
        let mut first_shared = [0.0; SHARED_FEATURES];
        let mut first_candidate = [0.0; CANDIDATE_FEATURES];
        let mut second_shared = [0.0; SHARED_FEATURES];
        let mut second_candidate = [0.0; CANDIDATE_FEATURES];
        global[0] = 1.0;
        first_shared[0] = 2.0;
        first_candidate[0] = 3.0;
        second_shared[0] = 4.0;
        second_candidate[0] = 5.0;
        let first = CatalogOption {
            index: 0,
            action: 1,
            prior_rank: 7,
            teacher: false,
            job_kind: 2,
            owner: Some(1),
        };
        let second = CatalogOption {
            index: 0,
            action: 2,
            prior_rank: 11,
            teacher: false,
            job_kind: 4,
            owner: Some(2),
        };
        let features = pair_embedding(
            &global,
            &first_shared,
            &first_candidate,
            &second_shared,
            &second_candidate,
            2,
            1,
            PairKind::Joint,
            &first,
            &second,
            3,
            20,
            25,
        );
        assert!(features.iter().all(|value| value.is_finite()));
        assert_eq!(features[0], 1.0);
        assert_eq!(features[56], 2.0);
        assert_eq!(features[102], 3.0);
        assert_eq!(features[146], 4.0);
        assert_eq!(features[192], 5.0);
        assert_eq!(features[238], 1.0);
        assert_eq!(features[240], 1.0);
        assert_eq!(features[244], 1.0);
        assert_eq!(features[245 + 1 * 5 + 3], 1.0);
        assert_eq!(features[270 + 2 * 5 + 3], 1.0);
        assert_eq!(features[295], 0.75);
        assert_eq!(features[296], 0.35);
        assert_eq!(features[297], 0.44);
        assert_eq!(features[298], 15.0);
    }

    #[test]
    fn parent_feature_layout_is_finite_and_complete() {
        let mut global = [0.0; GLOBAL_FEATURES];
        let mut shared = [0.0; SHARED_FEATURES];
        let mut candidate = [0.0; CANDIDATE_FEATURES];
        global[0] = 1.0;
        shared[0] = 2.0;
        candidate[0] = 3.0;
        let features = individual_features(&global, &shared, &candidate, 2, 1, 3, 7, 20);
        assert!(features.iter().all(|value| value.is_finite()));
        assert_eq!(features[0], 1.0);
        assert_eq!(features[56], 2.0);
        assert_eq!(features[102], 3.0);
        assert_eq!(features[148], 1.0);
        assert_eq!(features[150], 1.0);
        assert_eq!(features[151], 0.75);
        assert_eq!(features[152], 0.35);
    }

    #[test]
    fn preview_matches_real_same_turn_assignment() {
        let task = Task {
            map_seed: 9_700_001,
            seat: 0,
            opponent: 0,
        };
        let mut env = make_env(task);
        for _ in 0..5_000 {
            let observation = env.candidate_observation();
            let teacher = observation.actions[observation.teacher_index] as usize;
            if env.stage() == MacroDecisionStage::Worker
                && observation.branch == MacroSelectionBranch::Rate
            {
                if let Some(preview) = env.pair_branch_preview(teacher) {
                    let turn = env.state.turn;
                    let terminal = env.step(teacher);
                    assert!(!terminal.done);
                    assert_eq!(env.state.turn, turn);
                    assert_eq!(env.state_hash(), preview.state_hash);
                    assert_eq!(env.current_unit_id(), Some(preview.worker_id));
                    let actual = env.candidate_observation();
                    assert_eq!(
                        observation_hash(&actual),
                        observation_hash(&preview.observation)
                    );
                    assert_eq!(env.d42_shared_context(), preview.shared_context);
                    return;
                }
            }
            let terminal = env.step(teacher);
            assert!(!terminal.done, "test task ended without pair preview");
        }
        panic!("test task did not expose pair preview");
    }

    #[test]
    fn control_matches_exact_d40() {
        let task = Task {
            map_seed: 9_700_002,
            seat: 1,
            opponent: 2,
        };
        let control = play_control(task);
        let row = play(task, 0, &test_policy(PolicyKind::Control));
        assert_eq!(row.outcome.terminal, control.terminal);
        assert_eq!(row.outcome.action_planes, control.action_planes);
        assert_eq!(row.stats.intervention_batches, 0);
        assert_eq!(row.stats.nonkeep_assignments, 0);
        assert_eq!(row.stats.joint_batches, 0);
        assert_eq!(row.stats.scored_assignments, 0);
    }

    #[test]
    fn zero_residual_matches_exact_parent() {
        let task = Task {
            map_seed: 9_700_003,
            seat: 0,
            opponent: 3,
        };
        let parent = play(task, 0, &test_policy(PolicyKind::Parent));
        let zero = play(task, 1, &test_policy(PolicyKind::ZeroResidual));
        assert_eq!(zero.outcome.terminal, parent.outcome.terminal);
        assert_eq!(zero.outcome.action_planes, parent.outcome.action_planes);
        assert_eq!(zero.stats.residual_overrides, 0);
        assert_eq!(zero.stats.residual_pair_evaluations, 0);
    }

    #[test]
    fn zero_residual_pair_choice_is_exact_parent_pair() {
        let task = Task {
            map_seed: 9_700_004,
            seat: 1,
            opponent: 4,
        };
        let mut env = make_env(task);
        let policy = test_policy(PolicyKind::ZeroResidual);
        let mut completed_batches = 0;
        for _ in 0..5_000 {
            let observation = env.candidate_observation();
            if env.stage() == MacroDecisionStage::Train {
                completed_batches += 1;
            }
            if env.stage() == MacroDecisionStage::Worker
                && observation.branch == MacroSelectionBranch::Rate
                && live_own_crops(&env) > 0
                && env.state.turn <= MACRO_TOTAL_TURNS - 30
            {
                let global = batch_features(&env, completed_batches);
                if let Some(enumeration) = choose_pair(&env, &observation, &policy, &global, 4) {
                    assert_eq!(
                        enumeration.selected.first.action,
                        enumeration.parent.first.action
                    );
                    assert_eq!(
                        enumeration.selected.second.action,
                        enumeration.parent.second.action
                    );
                    return;
                }
            }
            let action = observation.actions[observation.teacher_index] as usize;
            let terminal = env.step(action);
            assert!(!terminal.done, "test task ended without residual pair root");
        }
        panic!("test task did not expose residual pair root");
    }
}
