//! Recurrent-ready masked q6 proposal environment for D108.

use std::collections::{BTreeMap, BTreeSet};
use std::sync::Arc;

use rayon::{prelude::*, ThreadPoolBuilder};

use crate::d41b_prior_kernel::exact_prior_order;
use crate::rl_macro::{
    CompleteMacroEnv, MacroCandidateObservation, MacroDecisionStage, MacroOpponentMode,
    MacroSelectionBranch, MacroTerminal, PlantOwner, MACRO_CANDIDATE_FEATURES, MACRO_CELLS,
    MACRO_HEIGHT, MACRO_TOTAL_TURNS, MACRO_WIDTH,
};

pub const Q6_EXPERTS: usize = 64;
pub const Q6_EXPERT_FEATURES: usize = 153;
pub const Q6_ACTIONS: usize = Q6_EXPERTS + 1;
pub const Q6_ACTION_FEATURES: usize = 379;
pub const Q6_STATE_FEATURES: usize = 64;
pub const Q6_INTERVENTION_BUDGET: u8 = 4;

const GLOBAL_FEATURES: usize = 56;
const SHARED_FEATURES: usize = 46;
const JOB_LABELS: [&str; 6] = ["idle", "bank", "fell", "harvest", "renew", "mine"];
const OWNER_LABELS: [&str; 4] = ["natural", "own", "opponent", "ambiguous"];

#[derive(Clone, Debug)]
struct OptionChoice {
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
    first: OptionChoice,
    second: OptionChoice,
    supporters: [bool; Q6_EXPERTS],
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
        let index = owner_index(*env.owners().get(&plant.pos()).expect("D108 provenance"));
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
        .expect("D108 worker ordinal")
}

fn one_hot_index(
    features: &[f32; MACRO_CANDIDATE_FEATURES],
    start: usize,
    count: usize,
) -> Option<usize> {
    let mut selected = None;
    for offset in 0..count {
        if features[start + offset] > 0.5 {
            if selected.is_some() {
                return None;
            }
            selected = Some(offset);
        }
    }
    selected
}

fn option_choice(
    observation: &MacroCandidateObservation,
    index: usize,
    prior_rank: usize,
    teacher: bool,
) -> OptionChoice {
    let features = &observation.features[index];
    let job_kind = one_hot_index(features, 20, 6).expect("D108 job one-hot");
    let owner = one_hot_index(features, 30, 4);
    let action = observation.actions[index] as usize;
    let target = (2..=5).contains(&job_kind).then_some(action % MACRO_CELLS);
    let deposit = std::array::from_fn(|slot| (features[34 + slot] * 10.0).round() as i32);
    OptionChoice {
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
    candidate: &[f32; MACRO_CANDIDATE_FEATURES],
    ordinal: usize,
    position: usize,
    remaining_budget: u32,
    prior_rank: usize,
    candidate_count: usize,
) -> [f32; Q6_EXPERT_FEATURES] {
    let mut result = [0.0f32; Q6_EXPERT_FEATURES];
    result[..GLOBAL_FEATURES].copy_from_slice(global);
    result[GLOBAL_FEATURES..GLOBAL_FEATURES + SHARED_FEATURES].copy_from_slice(shared);
    let candidate_start = GLOBAL_FEATURES + SHARED_FEATURES;
    result[candidate_start..candidate_start + MACRO_CANDIDATE_FEATURES].copy_from_slice(candidate);
    let ordinal_start = candidate_start + MACRO_CANDIDATE_FEATURES;
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
    expert: &[f32; Q6_EXPERT_FEATURES],
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
            .expect("D108 option action in observation");
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
    experts: &[[f32; Q6_EXPERT_FEATURES]],
) -> Option<Vec<Option<Proposal>>> {
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
            first: first_options[0].clone(),
            second: control_second_options[0].clone(),
            supporters: [false; Q6_EXPERTS],
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
            .expect("D108 expert first action must expose second worker");
        assert_eq!(preview.turn, env.state.turn);
        assert_eq!(preview.observation.branch, MacroSelectionBranch::Rate);
        let second_options = catalog(&preview.observation, preview.live_own_crops);
        let second = expert_choose(
            &preview.observation,
            &second_options,
            expert,
            global,
            &preview.shared_context,
            preview.worker_ordinal,
            1,
            4 - u32::from(!first.teacher),
        );
        let proposal = by_actions
            .entry((first.action, second.action))
            .or_insert_with(|| Proposal {
                first: first.clone(),
                second: second.clone(),
                supporters: [false; Q6_EXPERTS],
                first_candidate_count: observation.actions.len(),
                first_catalog_size: first_options.len(),
                second_candidate_count: preview.observation.actions.len(),
                second_catalog_size: second_options.len(),
                first_worker_ordinal: first_ordinal,
            });
        proposal.supporters[expert_index] = true;
    }
    let mut slots = vec![None; Q6_ACTIONS];
    for proposal in by_actions.into_values() {
        let slot = if proposal.nonteacher() == 0 {
            0
        } else {
            1 + proposal
                .supporters
                .iter()
                .position(|supported| *supported)
                .expect("D108 noncontrol proposal supporter")
        };
        assert!(slots[slot].is_none(), "D108 duplicate representative slot");
        slots[slot] = Some(proposal);
    }
    assert!(slots[0].is_some(), "D108 control proposal");
    Some(slots)
}

fn push_one_hot(values: &mut Vec<f32>, selected: usize, count: usize) {
    values.extend((0..count).map(|index| f32::from(index == selected)));
}

fn raw_action_features(
    proposal: &Proposal,
    env: &CompleteMacroEnv,
    decision_ordinal: usize,
) -> [f32; Q6_ACTION_FEATURES] {
    let mut semantic = Vec::with_capacity(45);
    semantic.push(f32::from(proposal.nonteacher() > 0));
    push_one_hot(&mut semantic, proposal.kind(), 4);
    for option in [&proposal.first, &proposal.second] {
        push_one_hot(
            &mut semantic,
            if option.teacher {
                0
            } else {
                option.job_kind - 1
            },
            5,
        );
    }
    for option in [&proposal.first, &proposal.second] {
        push_one_hot(
            &mut semantic,
            if option.teacher {
                0
            } else {
                option.owner.map_or(0, |owner| owner + 1)
            },
            5,
        );
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
    semantic.push(
        proposal
            .supporters
            .iter()
            .filter(|supported| **supported)
            .count() as f32
            / 64.0,
    );
    assert_eq!(semantic.len(), 45);
    let context = [
        env.state.turn as f32 / 300.0,
        decision_ordinal as f32 / 200.0,
        live_own_crops(env) as f32 / 20.0,
        proposal.first_candidate_count as f32 / 100.0,
        proposal.first_catalog_size as f32 / 16.0,
        proposal.first_worker_ordinal as f32 / 2.0,
    ];
    let mut result = [0.0f32; Q6_ACTION_FEATURES];
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
    assert_eq!(offset, Q6_ACTION_FEATURES);
    result
}

fn run_control(map_seed: i64, seat: usize, opponent: MacroOpponentMode) -> MacroTerminal {
    let mut env = CompleteMacroEnv::new(map_seed, seat, opponent);
    loop {
        let action = env.work_conserving_deficit_heuristic_action();
        let terminal = env.step(action);
        if terminal.done {
            return terminal;
        }
    }
}

struct Q6Step {
    terminal: Option<MacroTerminal>,
    reward: f32,
}

#[derive(Clone)]
pub struct Q6ProposalEnv {
    env: CompleteMacroEnv,
    experts: Arc<Vec<[f32; Q6_EXPERT_FEATURES]>>,
    baseline: MacroTerminal,
    global: [f32; GLOBAL_FEATURES],
    completed_batches: u32,
    batch_considered: bool,
    decision_ordinal: usize,
    boundary_decisions: u16,
    interventions: u8,
    joint_batches: u16,
    noncontrol_assignments: u16,
    previous_kind: usize,
    cached: Option<Vec<Option<Proposal>>>,
    pending_terminal: Option<MacroTerminal>,
}

impl Q6ProposalEnv {
    pub fn new(
        map_seed: i64,
        seat: usize,
        opponent: MacroOpponentMode,
        experts: Arc<Vec<[f32; Q6_EXPERT_FEATURES]>>,
        baseline: MacroTerminal,
    ) -> Self {
        let mut result = Self {
            env: CompleteMacroEnv::new(map_seed, seat, opponent),
            experts,
            baseline,
            global: [0.0; GLOBAL_FEATURES],
            completed_batches: 0,
            batch_considered: false,
            decision_ordinal: 0,
            boundary_decisions: 0,
            interventions: 0,
            joint_batches: 0,
            noncontrol_assignments: 0,
            previous_kind: 0,
            cached: None,
            pending_terminal: None,
        };
        result.pending_terminal = result.advance_to_boundary();
        result
    }

    fn advance_to_boundary(&mut self) -> Option<MacroTerminal> {
        loop {
            let observation = self.env.candidate_observation();
            if self.env.stage() == MacroDecisionStage::Train {
                self.global = batch_features(&self.env, self.completed_batches);
                self.completed_batches += 1;
                self.batch_considered = false;
            }
            let eligible = !self.batch_considered
                && self.interventions < Q6_INTERVENTION_BUDGET
                && self.env.stage() == MacroDecisionStage::Worker
                && observation.branch == MacroSelectionBranch::Rate
                && live_own_crops(&self.env) > 0
                && self.env.state.turn <= MACRO_TOTAL_TURNS - 30;
            if eligible {
                if let Some(options) =
                    proposals(&self.env, &observation, &self.global, &self.experts)
                {
                    self.cached = Some(options);
                    self.boundary_decisions = self.boundary_decisions.saturating_add(1);
                    return None;
                }
            }
            let action = observation.actions[observation.teacher_index] as usize;
            let terminal = self.env.step(action);
            self.decision_ordinal += 1;
            if terminal.done {
                return Some(terminal);
            }
        }
    }

    fn state_features(&self) -> [f32; Q6_STATE_FEATURES] {
        let mut result = [0.0f32; Q6_STATE_FEATURES];
        if self.cached.is_none() {
            return result;
        }
        result[..GLOBAL_FEATURES].copy_from_slice(&self.global);
        result[56] = self.env.state.turn as f32 / MACRO_TOTAL_TURNS as f32;
        result[57] = self.boundary_decisions as f32 / 100.0;
        result[58] = live_own_crops(&self.env) as f32 / 20.0;
        result[59] =
            (Q6_INTERVENTION_BUDGET - self.interventions) as f32 / Q6_INTERVENTION_BUDGET as f32;
        result[60 + self.previous_kind] = 1.0;
        assert!(result.iter().all(|value| value.is_finite()));
        result
    }

    fn observe(&mut self, state: &mut [f32], action_features: &mut [f32], mask: &mut [u8]) {
        assert_eq!(state.len(), Q6_STATE_FEATURES);
        assert_eq!(action_features.len(), Q6_ACTIONS * Q6_ACTION_FEATURES);
        assert_eq!(mask.len(), Q6_ACTIONS);
        state.copy_from_slice(&self.state_features());
        action_features.fill(0.0);
        mask.fill(0);
        mask[0] = 1;
        let Some(options) = &self.cached else {
            return;
        };
        let control = options[0].as_ref().expect("D108 cached control");
        let control_features = raw_action_features(control, &self.env, self.decision_ordinal);
        for (slot, proposal) in options.iter().enumerate().skip(1) {
            let Some(proposal) = proposal else {
                continue;
            };
            mask[slot] = 1;
            let raw = raw_action_features(proposal, &self.env, self.decision_ordinal);
            let offset = slot * Q6_ACTION_FEATURES;
            for index in 0..Q6_ACTION_FEATURES {
                action_features[offset + index] = raw[index] - control_features[index];
            }
        }
        assert!(action_features.iter().all(|value| value.is_finite()));
    }

    fn paired_reward(&self, terminal: MacroTerminal) -> f32 {
        let margin = terminal.own_score - terminal.opponent_score;
        let baseline_margin = self.baseline.own_score - self.baseline.opponent_score;
        (margin - baseline_margin) as f32 / 100.0
    }

    fn step(&mut self, action: usize) -> Q6Step {
        assert!(action < Q6_ACTIONS);
        if let Some(terminal) = self.pending_terminal.take() {
            assert_eq!(action, 0, "D108 terminal-only observation requires control");
            return Q6Step {
                terminal: Some(terminal),
                reward: self.paired_reward(terminal),
            };
        }
        let options = self.cached.take().expect("D108 step without boundary");
        let proposal = options[action]
            .clone()
            .unwrap_or_else(|| panic!("D108 selected masked proposal {action}"));
        let kind = proposal.kind();
        if kind > 0 {
            self.interventions += 1;
            self.noncontrol_assignments = self
                .noncontrol_assignments
                .saturating_add(proposal.nonteacher() as u16);
            if kind == 3 {
                self.joint_batches = self.joint_batches.saturating_add(1);
            }
        }
        self.previous_kind = kind;
        self.batch_considered = true;
        let first = self.env.step(proposal.first.action);
        self.decision_ordinal += 1;
        assert!(!first.done, "D108 paired first action terminated");
        let second = self.env.step(proposal.second.action);
        self.decision_ordinal += 1;
        if second.done {
            return Q6Step {
                terminal: Some(second),
                reward: self.paired_reward(second),
            };
        }
        let terminal = self.advance_to_boundary();
        Q6Step {
            reward: terminal.map_or(0.0, |value| self.paired_reward(value)),
            terminal,
        }
    }
}

/// A deterministic offline task for the D112 q6 counterfactual teacher.
#[derive(Clone, Copy, Debug, Eq, Ord, PartialEq, PartialOrd)]
pub struct Q6TeacherTask {
    pub map_seed: i64,
    pub seat: usize,
    pub opponent: usize,
}

/// Exact D40 outcome and q6-boundary coverage for one teacher task.
#[derive(Clone, Copy, Debug)]
pub struct Q6TeacherBaseline {
    pub task: Q6TeacherTask,
    pub boundary_count: u16,
    pub terminal: MacroTerminal,
}

/// One exact one-deviation continuation from a D40 q6 boundary.
#[derive(Clone, Debug)]
pub struct Q6TeacherArm {
    pub task: Q6TeacherTask,
    pub boundary_index: u16,
    pub baseline_boundary_count: u16,
    pub decision_ordinal: usize,
    pub turn: u16,
    pub root_state_hash: u64,
    pub proposal_count: u8,
    pub slot: u8,
    pub kind: u8,
    pub nonteacher: u8,
    pub first_action: usize,
    pub second_action: usize,
    pub first_teacher: bool,
    pub second_teacher: bool,
    pub first_job_kind: usize,
    pub second_job_kind: usize,
    pub first_owner: Option<usize>,
    pub second_owner: Option<usize>,
    pub first_prior_rank: usize,
    pub second_prior_rank: usize,
    pub first_target: Option<usize>,
    pub second_target: Option<usize>,
    pub supporter_count: u8,
    pub state_features: [f32; Q6_STATE_FEATURES],
    pub action_features: [f32; Q6_ACTION_FEATURES],
    pub paired_gain: f32,
    pub intervention_batches: u8,
    pub encountered_boundaries: u16,
    pub joint_batches: u16,
    pub noncontrol_assignments: u16,
    pub terminal: MacroTerminal,
}

/// Complete, deterministically ordered D112 teacher dataset.
pub struct Q6TeacherDataset {
    pub baselines: Vec<Q6TeacherBaseline>,
    pub arms: Vec<Q6TeacherArm>,
}

#[derive(Clone, Debug)]
struct Q6TeacherProposal {
    slot: usize,
    proposal: Proposal,
    action_features: [f32; Q6_ACTION_FEATURES],
}

struct Q6TeacherRoot {
    task_index: usize,
    boundary_index: u16,
    decision_ordinal: usize,
    turn: u16,
    state_hash: u64,
    proposal_count: u8,
    state_features: [f32; Q6_STATE_FEATURES],
    proposals: Vec<Q6TeacherProposal>,
    snapshot: Q6ProposalEnv,
}

fn q6_teacher_roots(
    task_index: usize,
    task: Q6TeacherTask,
    experts: Arc<Vec<[f32; Q6_EXPERT_FEATURES]>>,
    baseline: MacroTerminal,
) -> Vec<Q6TeacherRoot> {
    let mut env = Q6ProposalEnv::new(
        task.map_seed,
        task.seat,
        MacroOpponentMode::from_index(task.opponent),
        experts,
        baseline,
    );
    let mut roots = Vec::new();
    loop {
        if env.cached.is_none() {
            let terminal = env
                .step(0)
                .terminal
                .expect("D112 terminal-only control continuation");
            assert_eq!(terminal, baseline, "D112 empty control trace");
            break;
        }

        let mut state_features = [0.0f32; Q6_STATE_FEATURES];
        let mut all_action_features = vec![0.0f32; Q6_ACTIONS * Q6_ACTION_FEATURES];
        let mut mask = [0u8; Q6_ACTIONS];
        env.observe(&mut state_features, &mut all_action_features, &mut mask);
        let proposal_count = mask.iter().filter(|value| **value == 1).count();
        assert!(proposal_count >= 2, "D112 boundary without noncontrol arm");
        let cached = env.cached.as_ref().expect("D112 cached proposals");
        let mut root_proposals = Vec::with_capacity(proposal_count - 1);
        for (slot, proposal) in cached.iter().enumerate().skip(1) {
            let Some(proposal) = proposal else {
                assert_eq!(mask[slot], 0, "D112 masked slot mismatch");
                continue;
            };
            assert_eq!(mask[slot], 1, "D112 live slot mismatch");
            assert!(proposal.nonteacher() > 0, "D112 noncontrol slot");
            let offset = slot * Q6_ACTION_FEATURES;
            let action_features: [f32; Q6_ACTION_FEATURES] = all_action_features
                [offset..offset + Q6_ACTION_FEATURES]
                .try_into()
                .expect("D112 action feature width");
            assert!(action_features.iter().all(|value| value.is_finite()));
            root_proposals.push(Q6TeacherProposal {
                slot,
                proposal: proposal.clone(),
                action_features,
            });
        }
        assert_eq!(root_proposals.len() + 1, proposal_count);
        roots.push(Q6TeacherRoot {
            task_index,
            boundary_index: roots.len() as u16,
            decision_ordinal: env.decision_ordinal,
            turn: env.env.state.turn as u16,
            state_hash: env.env.state_hash(),
            proposal_count: proposal_count as u8,
            state_features,
            proposals: root_proposals,
            snapshot: env.clone(),
        });

        if let Some(terminal) = env.step(0).terminal {
            assert_eq!(terminal, baseline, "D112 final control continuation");
            break;
        }
    }
    assert_eq!(roots.len(), env.boundary_decisions as usize);
    roots
}

fn q6_teacher_arm(
    root: &Q6TeacherRoot,
    arm_index: usize,
    tasks: &[Q6TeacherTask],
    baselines: &[MacroTerminal],
    baseline_boundary_count: u16,
) -> Q6TeacherArm {
    let task = tasks[root.task_index];
    let baseline = baselines[root.task_index];
    let arm = &root.proposals[arm_index];
    let mut env = root.snapshot.clone();
    assert_eq!(env.decision_ordinal, root.decision_ordinal);
    assert_eq!(env.env.state.turn as u16, root.turn);
    assert_eq!(env.env.state_hash(), root.state_hash);

    let mut state_features = [0.0f32; Q6_STATE_FEATURES];
    let mut all_action_features = vec![0.0f32; Q6_ACTIONS * Q6_ACTION_FEATURES];
    let mut mask = [0u8; Q6_ACTIONS];
    env.observe(&mut state_features, &mut all_action_features, &mut mask);
    assert_eq!(state_features, root.state_features);
    assert_eq!(
        mask.iter().filter(|value| **value == 1).count(),
        root.proposal_count as usize
    );
    assert_eq!(mask[arm.slot], 1);
    let offset = arm.slot * Q6_ACTION_FEATURES;
    assert_eq!(
        &all_action_features[offset..offset + Q6_ACTION_FEATURES],
        arm.action_features.as_slice()
    );

    let mut step = env.step(arm.slot);
    while step.terminal.is_none() {
        assert!(env.cached.is_some(), "D112 continuation lost boundary");
        step = env.step(0);
    }
    let terminal = step.terminal.expect("D112 arm terminal");
    let proposal = &arm.proposal;
    assert_eq!(env.interventions, 1);
    assert_eq!(env.noncontrol_assignments, proposal.nonteacher() as u16);
    assert_eq!(env.joint_batches, u16::from(proposal.kind() == 3));
    assert_eq!(
        step.reward,
        (terminal.own_score - terminal.opponent_score - baseline.own_score
            + baseline.opponent_score) as f32
            / 100.0
    );

    Q6TeacherArm {
        task,
        boundary_index: root.boundary_index,
        baseline_boundary_count,
        decision_ordinal: root.decision_ordinal,
        turn: root.turn,
        root_state_hash: root.state_hash,
        proposal_count: root.proposal_count,
        slot: arm.slot as u8,
        kind: proposal.kind() as u8,
        nonteacher: proposal.nonteacher() as u8,
        first_action: proposal.first.action,
        second_action: proposal.second.action,
        first_teacher: proposal.first.teacher,
        second_teacher: proposal.second.teacher,
        first_job_kind: proposal.first.job_kind,
        second_job_kind: proposal.second.job_kind,
        first_owner: proposal.first.owner,
        second_owner: proposal.second.owner,
        first_prior_rank: proposal.first.prior_rank,
        second_prior_rank: proposal.second.prior_rank,
        first_target: proposal.first.target,
        second_target: proposal.second.target,
        supporter_count: proposal
            .supporters
            .iter()
            .filter(|supported| **supported)
            .count() as u8,
        state_features: root.state_features,
        action_features: arm.action_features,
        paired_gain: step.reward,
        intervention_batches: env.interventions,
        encountered_boundaries: env.boundary_decisions,
        joint_batches: env.joint_batches,
        noncontrol_assignments: env.noncontrol_assignments,
        terminal,
    }
}

/// Enumerate every D40 q6 boundary and evaluate every deduplicated noncontrol
/// proposal with exactly one intervention followed by D40. This function is
/// offline-only; submitted agents never call it.
pub fn collect_q6_teacher_dataset(
    start_seed: i64,
    maps: usize,
    experts: Vec<[f32; Q6_EXPERT_FEATURES]>,
    threads: usize,
) -> Q6TeacherDataset {
    assert!(start_seed != 0 && maps > 0 && threads > 0);
    assert_eq!(experts.len(), Q6_EXPERTS);
    assert!(experts.iter().flatten().all(|value| value.is_finite()));
    let tasks: Vec<_> = (start_seed..start_seed + maps as i64)
        .flat_map(|map_seed| {
            (0..2).flat_map(move |seat| {
                (0..MacroOpponentMode::ALL.len()).map(move |opponent| Q6TeacherTask {
                    map_seed,
                    seat,
                    opponent,
                })
            })
        })
        .collect();
    let experts = Arc::new(experts);
    let pool = ThreadPoolBuilder::new()
        .num_threads(threads)
        .thread_name(|index| format!("d112-q6-{index}"))
        .build()
        .expect("D112 thread pool");
    let terminals: Vec<_> = pool.install(|| {
        tasks
            .par_iter()
            .map(|task| {
                run_control(
                    task.map_seed,
                    task.seat,
                    MacroOpponentMode::from_index(task.opponent),
                )
            })
            .collect()
    });
    let nested_roots: Vec<Vec<Q6TeacherRoot>> = pool.install(|| {
        tasks
            .par_iter()
            .enumerate()
            .map(|(task_index, task)| {
                q6_teacher_roots(
                    task_index,
                    *task,
                    Arc::clone(&experts),
                    terminals[task_index],
                )
            })
            .collect()
    });
    let boundary_counts: Vec<_> = nested_roots
        .iter()
        .map(|roots| roots.len() as u16)
        .collect();
    let roots: Vec<_> = nested_roots.into_iter().flatten().collect();
    let nested_arms: Vec<Vec<Q6TeacherArm>> = pool.install(|| {
        roots
            .into_par_iter()
            .map(|root| {
                (0..root.proposals.len())
                    .map(|arm_index| {
                        q6_teacher_arm(
                            &root,
                            arm_index,
                            &tasks,
                            &terminals,
                            boundary_counts[root.task_index],
                        )
                    })
                    .collect()
            })
            .collect()
    });
    let arms = nested_arms.into_iter().flatten().collect();
    let baselines = tasks
        .iter()
        .zip(&terminals)
        .zip(&boundary_counts)
        .map(|((task, terminal), boundary_count)| Q6TeacherBaseline {
            task: *task,
            boundary_count: *boundary_count,
            terminal: *terminal,
        })
        .collect();
    Q6TeacherDataset { baselines, arms }
}

struct Q6Slot {
    task_index: u64,
    env: Q6ProposalEnv,
}

#[repr(C)]
#[derive(Clone, Copy, Debug, Default)]
pub struct Q6ProposalTerminal {
    pub done: u8,
    pub seat: u8,
    pub opponent: u8,
    pub own_workers: u8,
    pub map_seed: i64,
    pub task_index: u64,
    pub own_score: i32,
    pub opponent_score: i32,
    pub baseline_own_score: i32,
    pub baseline_opponent_score: i32,
    pub successful_trains: u8,
    pub intervention_batches: u8,
    pub boundary_decisions: u16,
    pub joint_batches: u16,
    pub noncontrol_assignments: u16,
    pub own_created_crops: u16,
    pub invalid_direct_commands: u16,
    pub provenance_failures: u16,
    pub deposit_prediction_failures: u16,
    pub invalidated_jobs: u16,
    pub action_hash: u64,
    pub state_hash: u64,
}

pub struct Q6ProposalBatch {
    slots: Vec<Q6Slot>,
    experts: Arc<Vec<[f32; Q6_EXPERT_FEATURES]>>,
    baselines: Arc<Vec<MacroTerminal>>,
    seed_base: i64,
    map_pool: usize,
    next_task_index: u64,
}

impl Q6ProposalBatch {
    fn task(seed_base: i64, map_pool: usize, task_index: u64) -> (i64, usize, usize) {
        let per_map = 2 * MacroOpponentMode::ALL.len() as u64;
        let scenario = task_index % (map_pool as u64 * per_map);
        let within = scenario % per_map;
        (
            seed_base + (scenario / per_map) as i64,
            (within / MacroOpponentMode::ALL.len() as u64) as usize,
            (within % MacroOpponentMode::ALL.len() as u64) as usize,
        )
    }

    fn make_slot(
        seed_base: i64,
        map_pool: usize,
        task_index: u64,
        experts: Arc<Vec<[f32; Q6_EXPERT_FEATURES]>>,
        baselines: Arc<Vec<MacroTerminal>>,
    ) -> Q6Slot {
        let (map_seed, seat, opponent) = Self::task(seed_base, map_pool, task_index);
        let baseline = baselines[task_index as usize % baselines.len()];
        Q6Slot {
            task_index,
            env: Q6ProposalEnv::new(
                map_seed,
                seat,
                MacroOpponentMode::from_index(opponent),
                experts,
                baseline,
            ),
        }
    }

    pub fn new(
        num_envs: usize,
        seed_base: i64,
        map_pool: usize,
        experts: Vec<[f32; Q6_EXPERT_FEATURES]>,
    ) -> Self {
        assert!(num_envs > 0);
        assert!(map_pool > 0);
        assert_eq!(experts.len(), Q6_EXPERTS);
        assert!(experts.iter().flatten().all(|value| value.is_finite()));
        let experts = Arc::new(experts);
        let pool_tasks = map_pool * 2 * MacroOpponentMode::ALL.len();
        let baselines: Vec<_> = (0..pool_tasks)
            .into_par_iter()
            .map(|task_index| {
                let (map_seed, seat, opponent) = Self::task(seed_base, map_pool, task_index as u64);
                run_control(map_seed, seat, MacroOpponentMode::from_index(opponent))
            })
            .collect();
        let baselines = Arc::new(baselines);
        let slots = (0..num_envs)
            .into_par_iter()
            .map(|task_index| {
                Self::make_slot(
                    seed_base,
                    map_pool,
                    task_index as u64,
                    Arc::clone(&experts),
                    Arc::clone(&baselines),
                )
            })
            .collect();
        Self {
            slots,
            experts,
            baselines,
            seed_base,
            map_pool,
            next_task_index: num_envs as u64,
        }
    }

    pub fn len(&self) -> usize {
        self.slots.len()
    }

    pub fn observe(&mut self, state: &mut [f32], action_features: &mut [f32], masks: &mut [u8]) {
        assert_eq!(state.len(), self.len() * Q6_STATE_FEATURES);
        assert_eq!(
            action_features.len(),
            self.len() * Q6_ACTIONS * Q6_ACTION_FEATURES
        );
        assert_eq!(masks.len(), self.len() * Q6_ACTIONS);
        self.slots
            .par_iter_mut()
            .zip(state.par_chunks_mut(Q6_STATE_FEATURES))
            .zip(action_features.par_chunks_mut(Q6_ACTIONS * Q6_ACTION_FEATURES))
            .zip(masks.par_chunks_mut(Q6_ACTIONS))
            .for_each(|(((slot, state), action_features), mask)| {
                slot.env.observe(state, action_features, mask);
            });
    }

    pub fn step(
        &mut self,
        selected: &[i32],
        rewards: &mut [f32],
        terminals: &mut [Q6ProposalTerminal],
    ) {
        assert_eq!(selected.len(), self.len());
        assert_eq!(rewards.len(), self.len());
        assert_eq!(terminals.len(), self.len());
        terminals.fill(Q6ProposalTerminal::default());
        let results: Vec<_> = self
            .slots
            .par_iter_mut()
            .zip(selected.par_iter())
            .map(|(slot, action)| slot.env.step(*action as usize))
            .collect();
        let mut resets = Vec::new();
        for (index, result) in results.into_iter().enumerate() {
            rewards[index] = result.reward;
            let Some(terminal) = result.terminal else {
                continue;
            };
            let slot = &self.slots[index];
            terminals[index] = Q6ProposalTerminal {
                done: 1,
                seat: slot.env.env.seat as u8,
                opponent: slot.env.env.opponent_mode.id(),
                own_workers: terminal.own_workers,
                map_seed: slot.env.env.map_seed,
                task_index: slot.task_index,
                own_score: terminal.own_score,
                opponent_score: terminal.opponent_score,
                baseline_own_score: slot.env.baseline.own_score,
                baseline_opponent_score: slot.env.baseline.opponent_score,
                successful_trains: terminal.successful_trains,
                intervention_batches: slot.env.interventions,
                boundary_decisions: slot.env.boundary_decisions,
                joint_batches: slot.env.joint_batches,
                noncontrol_assignments: slot.env.noncontrol_assignments,
                own_created_crops: terminal.own_created_crops,
                invalid_direct_commands: terminal.invalid_direct_commands,
                provenance_failures: terminal.provenance_failures,
                deposit_prediction_failures: terminal.deposit_prediction_failures,
                invalidated_jobs: terminal.invalidated_jobs,
                action_hash: terminal.action_hash,
                state_hash: terminal.state_hash,
            };
            resets.push((index, self.next_task_index));
            self.next_task_index += 1;
        }
        let replacements: Vec<_> = resets
            .par_iter()
            .map(|(index, task_index)| {
                (
                    *index,
                    Self::make_slot(
                        self.seed_base,
                        self.map_pool,
                        *task_index,
                        Arc::clone(&self.experts),
                        Arc::clone(&self.baselines),
                    ),
                )
            })
            .collect();
        for (index, slot) in replacements {
            self.slots[index] = slot;
        }
    }
}

#[no_mangle]
pub extern "C" fn tf_q6_state_features() -> usize {
    Q6_STATE_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_q6_actions() -> usize {
    Q6_ACTIONS
}

#[no_mangle]
pub extern "C" fn tf_q6_action_features() -> usize {
    Q6_ACTION_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_q6_expert_features() -> usize {
    Q6_EXPERT_FEATURES
}

#[no_mangle]
pub extern "C" fn tf_q6_terminal_size() -> usize {
    std::mem::size_of::<Q6ProposalTerminal>()
}

#[no_mangle]
pub unsafe extern "C" fn tf_q6_create(
    num_envs: usize,
    seed_base: i64,
    map_pool: usize,
    expert_weights: *const f32,
    expert_values: usize,
) -> *mut Q6ProposalBatch {
    if num_envs == 0
        || seed_base == 0
        || map_pool == 0
        || expert_weights.is_null()
        || expert_values != Q6_EXPERTS * Q6_EXPERT_FEATURES
    {
        return std::ptr::null_mut();
    }
    let values = std::slice::from_raw_parts(expert_weights, expert_values);
    if !values.iter().all(|value| value.is_finite()) {
        return std::ptr::null_mut();
    }
    let experts = values
        .chunks_exact(Q6_EXPERT_FEATURES)
        .map(|chunk| chunk.try_into().expect("D108 expert width"))
        .collect();
    Box::into_raw(Box::new(Q6ProposalBatch::new(
        num_envs, seed_base, map_pool, experts,
    )))
}

#[no_mangle]
pub unsafe extern "C" fn tf_q6_destroy(handle: *mut Q6ProposalBatch) {
    if !handle.is_null() {
        drop(Box::from_raw(handle));
    }
}

#[no_mangle]
pub unsafe extern "C" fn tf_q6_observe(
    handle: *mut Q6ProposalBatch,
    state: *mut f32,
    action_features: *mut f32,
    masks: *mut u8,
) -> i32 {
    if handle.is_null() || state.is_null() || action_features.is_null() || masks.is_null() {
        return -1;
    }
    let batch = &mut *handle;
    batch.observe(
        std::slice::from_raw_parts_mut(state, batch.len() * Q6_STATE_FEATURES),
        std::slice::from_raw_parts_mut(
            action_features,
            batch.len() * Q6_ACTIONS * Q6_ACTION_FEATURES,
        ),
        std::slice::from_raw_parts_mut(masks, batch.len() * Q6_ACTIONS),
    );
    0
}

#[no_mangle]
pub unsafe extern "C" fn tf_q6_step(
    handle: *mut Q6ProposalBatch,
    selected: *const i32,
    state: *mut f32,
    action_features: *mut f32,
    masks: *mut u8,
    rewards: *mut f32,
    terminals: *mut Q6ProposalTerminal,
) -> i32 {
    if handle.is_null()
        || selected.is_null()
        || state.is_null()
        || action_features.is_null()
        || masks.is_null()
        || rewards.is_null()
        || terminals.is_null()
    {
        return -1;
    }
    let batch = &mut *handle;
    batch.step(
        std::slice::from_raw_parts(selected, batch.len()),
        std::slice::from_raw_parts_mut(rewards, batch.len()),
        std::slice::from_raw_parts_mut(terminals, batch.len()),
    );
    tf_q6_observe(handle, state, action_features, masks)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn experts() -> Arc<Vec<[f32; Q6_EXPERT_FEATURES]>> {
        let source =
            include_str!("../../data/analysis/live-agent-6553250/d105a-q6-expert-population.tsv");
        let mut rows = Vec::new();
        for line in source.lines().skip(1) {
            let fields: Vec<_> = line.split('\t').collect();
            if fields[1] != "four" {
                continue;
            }
            let values: Vec<f32> = fields[3..]
                .iter()
                .map(|value| value.parse().unwrap())
                .collect();
            rows.push(values.try_into().unwrap());
        }
        assert_eq!(rows.len(), Q6_EXPERTS);
        Arc::new(rows)
    }

    #[test]
    fn action_zero_exactly_reproduces_paired_d40() {
        let baseline = run_control(9_829_000, 0, MacroOpponentMode::Resident);
        let mut env = Q6ProposalEnv::new(
            9_829_000,
            0,
            MacroOpponentMode::Resident,
            experts(),
            baseline,
        );
        let terminal = loop {
            let step = env.step(0);
            if let Some(terminal) = step.terminal {
                assert_eq!(step.reward, 0.0);
                break terminal;
            }
        };
        assert_eq!(terminal, env.baseline);
        assert_eq!(env.interventions, 0);
        assert!(env.boundary_decisions > 0);
    }

    #[test]
    fn observation_is_masked_finite_and_control_relative() {
        let baseline = run_control(9_829_000, 0, MacroOpponentMode::Resident);
        let mut env = Q6ProposalEnv::new(
            9_829_000,
            0,
            MacroOpponentMode::Resident,
            experts(),
            baseline,
        );
        let mut state = [0.0f32; Q6_STATE_FEATURES];
        let mut action_features = vec![0.0f32; Q6_ACTIONS * Q6_ACTION_FEATURES];
        let mut mask = [0u8; Q6_ACTIONS];
        env.observe(&mut state, &mut action_features, &mut mask);
        assert_eq!(mask[0], 1);
        assert!(mask.iter().filter(|value| **value == 1).count() >= 7);
        assert!(action_features[..Q6_ACTION_FEATURES]
            .iter()
            .all(|value| *value == 0.0));
        assert!(state.iter().all(|value| value.is_finite()));
        assert!(action_features.iter().all(|value| value.is_finite()));
    }

    #[test]
    fn dense_teacher_replays_one_exact_noncontrol_arm() {
        let task = Q6TeacherTask {
            map_seed: 9_829_000,
            seat: 0,
            opponent: MacroOpponentMode::Resident as usize,
        };
        let baseline = run_control(
            task.map_seed,
            task.seat,
            MacroOpponentMode::from_index(task.opponent),
        );
        let expert_bank = experts();
        let roots = q6_teacher_roots(0, task, Arc::clone(&expert_bank), baseline);
        assert!(!roots.is_empty());
        assert!(!roots[0].proposals.is_empty());
        let row = q6_teacher_arm(&roots[0], 0, &[task], &[baseline], roots.len() as u16);
        assert_eq!(row.intervention_batches, 1);
        assert_eq!(row.noncontrol_assignments, row.nonteacher as u16);
        assert_eq!(row.joint_batches, u16::from(row.kind == 3));
        assert!(row.action_features.iter().any(|value| *value != 0.0));
        assert!(row.action_features.iter().all(|value| value.is_finite()));
        assert_eq!(
            row.paired_gain,
            (row.terminal.own_score - row.terminal.opponent_score - baseline.own_score
                + baseline.opponent_score) as f32
                / 100.0
        );
    }
}
