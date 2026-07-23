//! Evaluate bounded whole-game controllers over the locked D106 q6 proposal bank.

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
    MACRO_HEIGHT, MACRO_TOTAL_TURNS, MACRO_WIDTH,
};

const EXPERT_FEATURES: usize = 153;
const CONTROLLER_FEATURES: usize = 379;
const GLOBAL_FEATURES: usize = 56;
const SHARED_FEATURES: usize = 46;
const CANDIDATE_FEATURES: usize = 44;
const EXPERTS: usize = 64;
const JOBS: usize = 4;
const OWNERS: usize = 4;
const OWNER_LABELS: [&str; OWNERS] = ["natural", "own", "opponent", "ambiguous"];
const JOB_LABELS: [&str; 6] = ["idle", "bank", "fell", "harvest", "renew", "mine"];

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ControllerKind {
    Zero,
    One,
    Four,
}

impl ControllerKind {
    fn label(self) -> &'static str {
        match self {
            Self::Zero => "zero",
            Self::One => "one",
            Self::Four => "four",
        }
    }
}

#[derive(Clone, Debug)]
struct Expert {
    label: String,
    weights: [f32; EXPERT_FEATURES],
    hash: u64,
}

#[derive(Clone, Debug)]
struct Controller {
    label: String,
    kind: ControllerKind,
    budget: u32,
    weights: [f32; CONTROLLER_FEATURES],
    hash: u64,
}

#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
struct Task {
    map_seed: i64,
    seat: usize,
    opponent: usize,
}

#[derive(Clone, Debug)]
struct OptionChoice {
    label: String,
    action: usize,
    prior_rank: usize,
    teacher: bool,
    job_kind: usize,
    owner: Option<usize>,
    target: Option<usize>,
    deposit: [i32; 4],
}

#[derive(Clone, Debug)]
struct Proposal {
    id: String,
    first: OptionChoice,
    second: OptionChoice,
    supporters: [bool; EXPERTS],
    first_candidate_count: usize,
    first_catalog_size: usize,
    second_candidate_count: usize,
    second_catalog_size: usize,
    first_worker_ordinal: usize,
}

impl Proposal {
    fn nonteacher(&self) -> usize {
        usize::from(!self.first.teacher) + usize::from(!self.second.teacher)
    }

    fn kind(&self) -> usize {
        match (self.first.teacher, self.second.teacher) {
            (true, true) => 0,
            (false, true) => 1,
            (true, false) => 2,
            (false, false) => 3,
        }
    }
}

#[derive(Clone, Copy, Debug, Default)]
struct ControllerStats {
    option_batches: u32,
    eligible_batches: u32,
    intervention_batches: u32,
    joint_batches: u32,
    single_first_batches: u32,
    single_second_batches: u32,
    nonkeep_assignments: u32,
    proposal_occurrences: u32,
    unique_proposals: u32,
    minimum_unique_proposals: u32,
    maximum_unique_proposals: u32,
    supporter_occurrences: u32,
    job_counts: [u32; JOBS],
    owner_counts: [u32; OWNERS],
    proposal_hash: u64,
    maximum_score_abs_bits: u32,
}

#[derive(Clone, Copy, Debug)]
struct Outcome {
    terminal: MacroTerminal,
    reward_identity_error: f32,
    terminal_live_own_plants: usize,
    action_planes: [u32; MACRO_ACTION_PLANES],
}

struct Row {
    controller: usize,
    task: Task,
    outcome: Outcome,
    stats: ControllerStats,
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

fn float_hash(values: &[f32]) -> u64 {
    let mut hash = 0xcbf29ce484222325;
    for value in values {
        mix(&mut hash, u64::from(value.to_bits()));
    }
    hash
}

fn read_experts(path: &str) -> Vec<Expert> {
    let source = BufReader::new(File::open(path).expect("open D107 q6 population"));
    let mut lines = source.lines();
    let expected_header = ["policy", "kind", "budget"]
        .into_iter()
        .map(str::to_string)
        .chain((0..EXPERT_FEATURES).map(|index| format!("param_{index:03}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D107 q6 header").unwrap(),
        expected_header
    );
    let mut experts = Vec::new();
    for line in lines {
        let fields: Vec<_> = line
            .expect("read D107 q6 row")
            .split('\t')
            .map(str::to_string)
            .collect();
        assert_eq!(fields.len(), EXPERT_FEATURES + 3);
        if fields[1] != "four" {
            continue;
        }
        assert_eq!(parse::<u32>(&fields[2], "D107 q6 budget"), 4);
        let mut weights = [0.0f32; EXPERT_FEATURES];
        for (target, value) in weights.iter_mut().zip(&fields[3..]) {
            *target = parse(value, "D107 q6 weight");
            assert!(target.is_finite());
        }
        experts.push(Expert {
            label: fields[0].clone(),
            hash: float_hash(&weights),
            weights,
        });
    }
    assert_eq!(experts.len(), EXPERTS);
    for (index, expert) in experts.iter().enumerate() {
        assert_eq!(expert.label, format!("four_{index:02}"));
    }
    experts
}

fn read_controllers(path: &str) -> Vec<Controller> {
    let source = BufReader::new(File::open(path).expect("open D107 controller population"));
    let mut lines = source.lines();
    let expected_header = ["policy", "kind", "budget"]
        .into_iter()
        .map(str::to_string)
        .chain((0..CONTROLLER_FEATURES).map(|index| format!("param_{index:03}")))
        .collect::<Vec<_>>()
        .join("\t");
    assert_eq!(
        lines.next().expect("D107 controller header").unwrap(),
        expected_header
    );
    let mut controllers = Vec::new();
    for line in lines {
        let fields: Vec<_> = line
            .expect("read D107 controller row")
            .split('\t')
            .map(str::to_string)
            .collect();
        assert_eq!(fields.len(), CONTROLLER_FEATURES + 3);
        let kind = match fields[1].as_str() {
            "zero" => ControllerKind::Zero,
            "one" => ControllerKind::One,
            "four" => ControllerKind::Four,
            other => panic!("unknown D107 controller kind: {other}"),
        };
        let budget = parse(&fields[2], "D107 controller budget");
        assert_eq!(budget, if kind == ControllerKind::One { 1 } else { 4 });
        let mut weights = [0.0f32; CONTROLLER_FEATURES];
        for (target, value) in weights.iter_mut().zip(&fields[3..]) {
            *target = parse(value, "D107 controller weight");
            assert!(target.is_finite());
        }
        if kind == ControllerKind::Zero {
            assert!(weights.iter().all(|weight| *weight == 0.0));
        }
        controllers.push(Controller {
            label: fields[0].clone(),
            kind,
            budget,
            hash: float_hash(&weights),
            weights,
        });
    }
    assert_eq!(controllers.len(), 129);
    assert_eq!(controllers[0].label, "zero_control");
    for index in 0..64 {
        let one = &controllers[1 + 2 * index];
        let four = &controllers[2 + 2 * index];
        assert_eq!(one.label, format!("one_{index:02}"));
        assert_eq!(four.label, format!("four_{index:02}"));
        assert_eq!(one.weights, four.weights);
        assert_eq!(one.hash, four.hash);
    }
    controllers
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
        let index = owner_index(*env.owners().get(&plant.pos()).expect("D107 provenance"));
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
        .expect("D107 worker ordinal")
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

fn option_choice(
    observation: &MacroCandidateObservation,
    index: usize,
    prior_rank: usize,
    teacher: bool,
) -> OptionChoice {
    let features = &observation.features[index];
    let job_kind = one_hot_index(features, 20, 6).expect("D107 job one-hot");
    let owner = one_hot_index(features, 30, 4);
    let action = observation.actions[index] as usize;
    let target = (2..=5).contains(&job_kind).then_some(action % MACRO_CELLS);
    let deposit = std::array::from_fn(|slot| (features[34 + slot] * 10.0).round() as i32);
    let class = if teacher {
        "keep".to_string()
    } else if job_kind == 5 {
        "mine".to_string()
    } else {
        format!(
            "{}:{}",
            JOB_LABELS[job_kind],
            OWNER_LABELS[owner.expect("D107 target provenance")]
        )
    };
    OptionChoice {
        label: format!("{class}@{action}"),
        action,
        prior_rank,
        teacher,
        job_kind,
        owner,
        target,
        deposit,
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
    let mut result = vec![option_choice(observation, order[0], 0, true)];
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
            result.push(option_choice(observation, index, rank, false));
        }
    }
    result
}

#[allow(clippy::too_many_arguments)]
fn expert_features(
    global: &[f32; GLOBAL_FEATURES],
    shared: &[f32; SHARED_FEATURES],
    candidate: &[f32; CANDIDATE_FEATURES],
    ordinal: usize,
    position: usize,
    remaining_budget: u32,
    prior_rank: usize,
    candidate_count: usize,
) -> [f32; EXPERT_FEATURES] {
    let mut result = [0.0f32; EXPERT_FEATURES];
    result[..GLOBAL_FEATURES].copy_from_slice(global);
    result[GLOBAL_FEATURES..GLOBAL_FEATURES + SHARED_FEATURES].copy_from_slice(shared);
    let candidate_start = GLOBAL_FEATURES + SHARED_FEATURES;
    result[candidate_start..candidate_start + CANDIDATE_FEATURES].copy_from_slice(candidate);
    let ordinal_start = candidate_start + CANDIDATE_FEATURES;
    result[ordinal_start + ordinal] = 1.0;
    let position_start = ordinal_start + 3;
    result[position_start + position] = 1.0;
    result[position_start + 2] = remaining_budget as f32 / 4.0;
    result[position_start + 3] = prior_rank as f32 / candidate_count as f32;
    result
}

#[allow(clippy::too_many_arguments)]
fn expert_choose(
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
        let index = observation
            .actions
            .iter()
            .position(|action| *action as usize == option.action)
            .expect("D107 option action in observation");
        let features = expert_features(
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

fn proposals(
    env: &CompleteMacroEnv,
    observation: &MacroCandidateObservation,
    global: &[f32; GLOBAL_FEATURES],
    experts: &[Expert],
) -> Option<Vec<Proposal>> {
    let first_worker = env.current_unit_id()?;
    let first_ordinal = worker_ordinal(env, first_worker);
    let first_options = catalog(observation, live_own_crops(env));
    let first_shared = env.d42_shared_context();
    let control_preview = env.pair_branch_preview(first_options[0].action)?;
    if control_preview.turn != env.state.turn
        || control_preview.observation.branch != MacroSelectionBranch::Rate
    {
        return None;
    }
    let control_second_options =
        catalog(&control_preview.observation, control_preview.live_own_crops);
    let control_key = (first_options[0].action, control_second_options[0].action);
    let mut by_actions = BTreeMap::new();
    by_actions.insert(
        control_key,
        Proposal {
            id: format!(
                "{}__{}",
                first_options[0].label, control_second_options[0].label
            ),
            first: first_options[0].clone(),
            second: control_second_options[0].clone(),
            supporters: [false; EXPERTS],
            first_candidate_count: observation.actions.len(),
            first_catalog_size: first_options.len(),
            second_candidate_count: control_preview.observation.actions.len(),
            second_catalog_size: control_second_options.len(),
            first_worker_ordinal: first_ordinal,
        },
    );
    for (expert_index, expert) in experts.iter().enumerate() {
        let first = expert_choose(
            observation,
            &first_options,
            expert,
            global,
            &first_shared,
            first_ordinal,
            0,
            4,
        );
        let preview = env
            .pair_branch_preview(first.action)
            .expect("D107 expert first action must expose second worker");
        assert_eq!(preview.turn, env.state.turn);
        assert_eq!(preview.observation.branch, MacroSelectionBranch::Rate);
        let second_options = catalog(&preview.observation, preview.live_own_crops);
        let remaining_after_first = 4 - u32::from(!first.teacher);
        let second = expert_choose(
            &preview.observation,
            &second_options,
            expert,
            global,
            &preview.shared_context,
            preview.worker_ordinal,
            1,
            remaining_after_first,
        );
        let key = (first.action, second.action);
        let proposal = by_actions.entry(key).or_insert_with(|| Proposal {
            id: format!("{}__{}", first.label, second.label),
            first: first.clone(),
            second: second.clone(),
            supporters: [false; EXPERTS],
            first_candidate_count: observation.actions.len(),
            first_catalog_size: first_options.len(),
            second_candidate_count: preview.observation.actions.len(),
            second_catalog_size: second_options.len(),
            first_worker_ordinal: first_ordinal,
        });
        proposal.supporters[expert_index] = true;
    }
    Some(by_actions.into_values().collect())
}

fn push_one_hot(values: &mut Vec<f32>, selected: usize, count: usize) {
    values.extend((0..count).map(|index| f32::from(index == selected)));
}

fn raw_controller_features(
    proposal: &Proposal,
    env: &CompleteMacroEnv,
    decision_ordinal: usize,
) -> [f32; CONTROLLER_FEATURES] {
    let mut semantic = Vec::with_capacity(45);
    semantic.push(f32::from(proposal.nonteacher() > 0));
    push_one_hot(&mut semantic, proposal.kind(), 4);
    for option in [&proposal.first, &proposal.second] {
        let job = if option.teacher {
            0
        } else {
            option.job_kind - 1
        };
        push_one_hot(&mut semantic, job, 5);
    }
    for option in [&proposal.first, &proposal.second] {
        let owner = if option.teacher {
            0
        } else {
            option.owner.map_or(0, |owner| owner + 1)
        };
        push_one_hot(&mut semantic, owner, 5);
    }
    semantic.push(proposal.first.prior_rank as f32 / proposal.first_candidate_count.max(1) as f32);
    semantic
        .push(proposal.second.prior_rank as f32 / proposal.second_candidate_count.max(1) as f32);
    for option in [&proposal.first, &proposal.second] {
        if let Some(target) = option.target {
            semantic.push(1.0);
            semantic.push((target / MACRO_WIDTH) as f32 / (MACRO_HEIGHT - 1) as f32);
            semantic.push((target % MACRO_WIDTH) as f32 / (MACRO_WIDTH - 1) as f32);
        } else {
            semantic.extend([0.0; 3]);
        }
    }
    for option in [&proposal.first, &proposal.second] {
        semantic.extend(option.deposit.into_iter().map(|value| value as f32 / 10.0));
    }
    semantic.push(proposal.nonteacher() as f32 / 2.0);
    semantic.push(proposal.second_candidate_count as f32 / 100.0);
    semantic.push(proposal.second_catalog_size as f32 / 16.0);
    semantic
        .push(proposal.supporters.iter().filter(|value| **value).count() as f32 / EXPERTS as f32);
    assert_eq!(semantic.len(), 45);
    let context = [
        env.state.turn as f32 / 300.0,
        decision_ordinal as f32 / 200.0,
        live_own_crops(env) as f32 / 20.0,
        proposal.first_candidate_count as f32 / 100.0,
        proposal.first_catalog_size as f32 / 16.0,
        proposal.first_worker_ordinal as f32 / 2.0,
    ];
    let mut result = [0.0f32; CONTROLLER_FEATURES];
    result[..45].copy_from_slice(&semantic);
    for (index, supported) in proposal.supporters.iter().enumerate() {
        result[45 + index] = f32::from(*supported);
    }
    let mut offset = 109;
    for value in context {
        for semantic_value in &semantic {
            result[offset] = value * semantic_value;
            offset += 1;
        }
    }
    assert_eq!(offset, CONTROLLER_FEATURES);
    assert!(result.iter().all(|value| value.is_finite()));
    result
}

fn select_proposal(
    proposals: &[Proposal],
    env: &CompleteMacroEnv,
    decision_ordinal: usize,
    controller: &Controller,
) -> (Proposal, f32) {
    let control = proposals
        .iter()
        .find(|proposal| proposal.nonteacher() == 0)
        .expect("D107 exact control proposal");
    let control_features = raw_controller_features(control, env, decision_ordinal);
    let mut selected = control.clone();
    let mut best_score = 0.0f32;
    for proposal in proposals
        .iter()
        .filter(|proposal| proposal.nonteacher() > 0)
    {
        let features = raw_controller_features(proposal, env, decision_ordinal);
        let score: f32 = controller
            .weights
            .iter()
            .zip(features.iter().zip(control_features))
            .map(|(weight, (value, control))| weight * (value - control))
            .sum();
        assert!(score.is_finite());
        let better = score.total_cmp(&best_score).is_gt()
            || (score.total_cmp(&best_score).is_eq() && score > 0.0 && proposal.id < selected.id);
        if better {
            selected = proposal.clone();
            best_score = score;
        }
    }
    (selected, best_score)
}

fn step(
    env: &mut CompleteMacroEnv,
    action: usize,
    planes: &mut [u32; MACRO_ACTION_PLANES],
) -> MacroTerminal {
    assert!(env.legal_actions().contains(&action), "D107 illegal action");
    planes[action / MACRO_CELLS] += 1;
    env.step(action)
}

fn finish(env: &CompleteMacroEnv, terminal: MacroTerminal, planes: [u32; 9]) -> Outcome {
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

fn record_selected(stats: &mut ControllerStats, proposal: &Proposal) {
    stats.intervention_batches += 1;
    stats.nonkeep_assignments += proposal.nonteacher() as u32;
    match proposal.kind() {
        1 => stats.single_first_batches += 1,
        2 => stats.single_second_batches += 1,
        3 => stats.joint_batches += 1,
        _ => panic!("D107 selected control as intervention"),
    }
    for option in [&proposal.first, &proposal.second] {
        if option.teacher {
            continue;
        }
        stats.job_counts[option.job_kind - 2] += 1;
        if let Some(owner) = option.owner {
            stats.owner_counts[owner] += 1;
        }
    }
}

fn play(task: Task, controller_index: usize, controller: &Controller, experts: &[Expert]) -> Row {
    let mut env = make_env(task);
    let mut stats = ControllerStats {
        proposal_hash: 0xcbf29ce484222325,
        ..ControllerStats::default()
    };
    let mut planes = [0u32; MACRO_ACTION_PLANES];
    let mut global = [0.0f32; GLOBAL_FEATURES];
    let mut batch_considered = false;
    let mut decisions = 0usize;
    loop {
        decisions += 1;
        assert!(decisions <= 5_000, "D107 decision loop: {task:?}");
        let observation = env.candidate_observation();
        if env.stage() == MacroDecisionStage::Train {
            global = batch_features(&env, stats.option_batches);
            stats.option_batches += 1;
            batch_considered = false;
        }
        let eligible = !batch_considered
            && stats.intervention_batches < controller.budget
            && env.stage() == MacroDecisionStage::Worker
            && observation.branch == MacroSelectionBranch::Rate
            && live_own_crops(&env) > 0
            && env.state.turn <= MACRO_TOTAL_TURNS - 30;
        if eligible {
            if let Some(options) = proposals(&env, &observation, &global, experts) {
                batch_considered = true;
                stats.eligible_batches += 1;
                stats.unique_proposals += options.len() as u32;
                if stats.eligible_batches == 1 {
                    stats.minimum_unique_proposals = options.len() as u32;
                } else {
                    stats.minimum_unique_proposals =
                        stats.minimum_unique_proposals.min(options.len() as u32);
                }
                stats.maximum_unique_proposals =
                    stats.maximum_unique_proposals.max(options.len() as u32);
                stats.proposal_occurrences += EXPERTS as u32;
                stats.supporter_occurrences += options
                    .iter()
                    .map(|proposal| {
                        proposal.supporters.iter().filter(|value| **value).count() as u32
                    })
                    .sum::<u32>();
                let (selected, score) = select_proposal(&options, &env, decisions - 1, controller);
                stats.maximum_score_abs_bits =
                    stats.maximum_score_abs_bits.max(score.abs().to_bits());
                mix(&mut stats.proposal_hash, env.state.turn as u64);
                mix(&mut stats.proposal_hash, options.len() as u64);
                mix(&mut stats.proposal_hash, selected.first.action as u64);
                mix(&mut stats.proposal_hash, selected.second.action as u64);
                if selected.nonteacher() > 0 {
                    record_selected(&mut stats, &selected);
                }
                let first_turn = env.state.turn;
                let terminal = step(&mut env, selected.first.action, &mut planes);
                if terminal.done {
                    return Row {
                        controller: controller_index,
                        task,
                        outcome: finish(&env, terminal, planes),
                        stats,
                    };
                }
                decisions += 1;
                assert_eq!(env.state.turn, first_turn, "D107 pair crossed turn");
                assert_eq!(env.stage(), MacroDecisionStage::Worker);
                assert_eq!(
                    env.candidate_observation().branch,
                    MacroSelectionBranch::Rate
                );
                let terminal = step(&mut env, selected.second.action, &mut planes);
                if terminal.done {
                    return Row {
                        controller: controller_index,
                        task,
                        outcome: finish(&env, terminal, planes),
                        stats,
                    };
                }
                continue;
            }
        }
        let terminal = step(
            &mut env,
            observation.actions[observation.teacher_index] as usize,
            &mut planes,
        );
        if terminal.done {
            assert!(stats.intervention_batches <= controller.budget);
            return Row {
                controller: controller_index,
                task,
                outcome: finish(&env, terminal, planes),
                stats,
            };
        }
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
                    .expect("D107 baseline lock")
                    .insert(task, play_control(task));
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D107 baseline worker");
    }
    Arc::try_unwrap(outcomes)
        .ok()
        .expect("sole D107 baselines")
        .into_inner()
        .expect("D107 baseline lock")
}

fn parallel_rows(
    controllers: Arc<Vec<Controller>>,
    experts: Arc<Vec<Expert>>,
    tasks: &[Task],
    baselines: &BTreeMap<Task, Outcome>,
    threads: usize,
    controller_limit: usize,
) -> Vec<Row> {
    let work: Vec<_> = (0..controller_limit)
        .flat_map(|controller| tasks.iter().copied().map(move |task| (controller, task)))
        .collect();
    let work = Arc::new(work);
    let baselines = Arc::new(baselines.clone());
    let next = Arc::new(AtomicUsize::new(0));
    let rows = Arc::new(Mutex::new(Vec::with_capacity(work.len())));
    let handles: Vec<_> = (0..threads.min(work.len()))
        .map(|_| {
            let controllers = Arc::clone(&controllers);
            let experts = Arc::clone(&experts);
            let work = Arc::clone(&work);
            let baselines = Arc::clone(&baselines);
            let next = Arc::clone(&next);
            let rows = Arc::clone(&rows);
            thread::spawn(move || loop {
                let index = next.fetch_add(1, Ordering::Relaxed);
                let Some(&(controller, task)) = work.get(index) else {
                    break;
                };
                let row = play(task, controller, &controllers[controller], &experts);
                if controllers[controller].kind == ControllerKind::Zero {
                    let expected = baselines[&task];
                    assert_eq!(
                        row.outcome.terminal, expected.terminal,
                        "D107 zero terminal"
                    );
                    assert_eq!(
                        row.outcome.action_planes, expected.action_planes,
                        "D107 zero planes"
                    );
                }
                rows.lock().expect("D107 row lock").push(row);
            })
        })
        .collect();
    for handle in handles {
        handle.join().expect("D107 population worker");
    }
    let mut rows = Arc::try_unwrap(rows)
        .ok()
        .expect("sole D107 rows")
        .into_inner()
        .expect("D107 row lock");
    rows.sort_by_key(|row| {
        (
            controllers[row.controller].label.clone(),
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
        .expect("create D107 baselines");
    let mut writer = BufWriter::new(target);
    let mut header = vec!["map_seed", "seat", "opponent"];
    header.extend(terminal_header());
    writeln!(writer, "{}", header.join("\t")).expect("write D107 baseline header");
    for (task, outcome) in baselines {
        let mut columns = vec![
            task.map_seed.to_string(),
            task.seat.to_string(),
            MacroOpponentMode::from_index(task.opponent)
                .label()
                .to_string(),
        ];
        columns.extend(terminal_columns(*outcome));
        writeln!(writer, "{}", columns.join("\t")).expect("write D107 baseline");
    }
}

fn write_rows(path: &str, rows: &[Row], controllers: &[Controller], expert_bank_hash: u64) {
    let target = OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(path)
        .expect("create D107 rows");
    let mut writer = BufWriter::new(target);
    let mut header = vec!["map_seed", "seat", "opponent", "policy", "kind", "budget"];
    header.extend(terminal_header());
    header.extend([
        "option_batches",
        "eligible_batches",
        "intervention_batches",
        "joint_batches",
        "single_first_batches",
        "single_second_batches",
        "nonkeep_assignments",
        "proposal_occurrences",
        "unique_proposals",
        "minimum_unique_proposals",
        "maximum_unique_proposals",
        "supporter_occurrences",
        "concrete_fell",
        "concrete_harvest",
        "concrete_renew",
        "concrete_mine",
        "owner_natural",
        "owner_own",
        "owner_opponent",
        "owner_ambiguous",
        "proposal_hash",
        "maximum_score_abs_bits",
        "controller_hash",
        "expert_bank_hash",
    ]);
    writeln!(writer, "{}", header.join("\t")).expect("write D107 row header");
    for row in rows {
        let controller = &controllers[row.controller];
        let mut columns = vec![
            row.task.map_seed.to_string(),
            row.task.seat.to_string(),
            MacroOpponentMode::from_index(row.task.opponent)
                .label()
                .to_string(),
            controller.label.clone(),
            controller.kind.label().to_string(),
            controller.budget.to_string(),
        ];
        columns.extend(terminal_columns(row.outcome));
        columns.extend([
            row.stats.option_batches.to_string(),
            row.stats.eligible_batches.to_string(),
            row.stats.intervention_batches.to_string(),
            row.stats.joint_batches.to_string(),
            row.stats.single_first_batches.to_string(),
            row.stats.single_second_batches.to_string(),
            row.stats.nonkeep_assignments.to_string(),
            row.stats.proposal_occurrences.to_string(),
            row.stats.unique_proposals.to_string(),
            row.stats.minimum_unique_proposals.to_string(),
            row.stats.maximum_unique_proposals.to_string(),
            row.stats.supporter_occurrences.to_string(),
            row.stats.job_counts[0].to_string(),
            row.stats.job_counts[1].to_string(),
            row.stats.job_counts[2].to_string(),
            row.stats.job_counts[3].to_string(),
            row.stats.owner_counts[0].to_string(),
            row.stats.owner_counts[1].to_string(),
            row.stats.owner_counts[2].to_string(),
            row.stats.owner_counts[3].to_string(),
            row.stats.proposal_hash.to_string(),
            row.stats.maximum_score_abs_bits.to_string(),
            controller.hash.to_string(),
            expert_bank_hash.to_string(),
        ]);
        writeln!(writer, "{}", columns.join("\t")).expect("write D107 row");
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert!(
        args.len() == 8 || args.len() == 9,
        "usage: d107_q6_proposal_controller_population Q6_POPULATION CONTROLLERS START_SEED MAPS OUTPUT BASELINES THREADS [CONTROLLER_LIMIT]"
    );
    let experts = Arc::new(read_experts(&args[1]));
    let controllers = Arc::new(read_controllers(&args[2]));
    let start_seed: i64 = parse(&args[3], "D107 start seed");
    let maps: usize = parse(&args[4], "D107 maps");
    let threads: usize = parse(&args[7], "D107 threads");
    let controller_limit = args.get(8).map_or(controllers.len(), |value| {
        parse(value, "D107 controller limit")
    });
    assert!(maps > 0 && threads > 0);
    assert!((1..=controllers.len()).contains(&controller_limit));
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
    let rows = parallel_rows(
        Arc::clone(&controllers),
        Arc::clone(&experts),
        &tasks,
        &baselines,
        threads,
        controller_limit,
    );
    let population_seconds = population_started.elapsed().as_secs_f64();
    let expert_bank_hash = experts.iter().fold(0xcbf29ce484222325, |mut hash, expert| {
        mix(&mut hash, expert.hash);
        hash
    });
    write_baselines(&args[6], &baselines);
    write_rows(&args[5], &rows, &controllers, expert_bank_hash);
    eprintln!(
        "saved {} D107 baselines in {:.3}s and {} rows in {:.3}s ({:.3} episodes/s)",
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

    fn zero_controller() -> Controller {
        Controller {
            label: "zero_control".to_string(),
            kind: ControllerKind::Zero,
            budget: 4,
            weights: [0.0; CONTROLLER_FEATURES],
            hash: 0,
        }
    }

    #[test]
    fn controller_feature_layout_is_finite_and_complete() {
        let task = Task {
            map_seed: 9_828_000,
            seat: 0,
            opponent: 0,
        };
        let mut env = make_env(task);
        loop {
            let observation = env.candidate_observation();
            let teacher = observation.actions[observation.teacher_index] as usize;
            if env.stage() == MacroDecisionStage::Worker
                && observation.branch == MacroSelectionBranch::Rate
                && live_own_crops(&env) > 0
            {
                if let Some(preview) = env.pair_branch_preview(teacher) {
                    if preview.observation.branch == MacroSelectionBranch::Rate {
                        let first = catalog(&observation, live_own_crops(&env))[0].clone();
                        let second_options = catalog(&preview.observation, preview.live_own_crops);
                        let proposal = Proposal {
                            id: "control".to_string(),
                            first,
                            second: second_options[0].clone(),
                            supporters: [false; EXPERTS],
                            first_candidate_count: observation.actions.len(),
                            first_catalog_size: 1,
                            second_candidate_count: preview.observation.actions.len(),
                            second_catalog_size: second_options.len(),
                            first_worker_ordinal: worker_ordinal(
                                &env,
                                env.current_unit_id().unwrap(),
                            ),
                        };
                        let features = raw_controller_features(&proposal, &env, 0);
                        assert_eq!(features.len(), CONTROLLER_FEATURES);
                        assert!(features.iter().all(|value| value.is_finite()));
                        return;
                    }
                }
            }
            if env.step(teacher).done {
                panic!("D107 test did not reach pair boundary");
            }
        }
    }

    #[test]
    fn zero_controller_matches_exact_control() {
        let experts =
            read_experts("../data/analysis/live-agent-6553250/d105a-q6-expert-population.tsv");
        let task = Task {
            map_seed: 9_828_000,
            seat: 0,
            opponent: 0,
        };
        let control = play_control(task);
        let row = play(task, 0, &zero_controller(), &experts);
        assert_eq!(row.outcome.terminal, control.terminal);
        assert_eq!(row.outcome.action_planes, control.action_planes);
        assert_eq!(row.stats.intervention_batches, 0);
        assert!(row.stats.eligible_batches > 0);
        assert!(row.stats.minimum_unique_proposals > 0);
    }
}
