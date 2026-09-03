//! Compact reduced opening model used to validate the online Rust search.
//!
//! This is intentionally not the full referee. It keeps the scheduling
//! choices that defeated the independent greedy dispatcher: real training
//! bills, asynchronous workers, finite fruit, infinite iron, planting and
//! delayed crops, shack release, and one TRAIN per turn.

use crate::search::{
    search_anytime, FeasiblePlan, SearchLimits, SearchProblem, SearchResult, Transition, INF_TURN,
};

pub const PLUM: usize = 0;
pub const LEMON: usize = 1;
pub const APPLE: usize = 2;
pub const IRON: usize = 3;
pub const RESOURCE_NAMES: [&str; 4] = ["PLUM", "LEMON", "APPLE", "IRON"];

const NO_RESOURCE: u8 = u8::MAX;
const NO_EVENT: u16 = u16::MAX;

fn ceil_div(value: u16, divisor: u16) -> u16 {
    debug_assert!(divisor > 0);
    value / divisor + u16::from(value % divisor != 0)
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
pub struct WorkerSpec {
    pub name: &'static str,
    pub movement: u8,
    pub capacity: u8,
    pub harvest: u8,
    pub chop: u8,
}

impl WorkerSpec {
    pub const fn new(
        name: &'static str,
        movement: u8,
        capacity: u8,
        harvest: u8,
        chop: u8,
    ) -> Self {
        Self {
            name,
            movement,
            capacity,
            harvest,
            chop,
        }
    }

    fn strength(self) -> u16 {
        u16::from(self.movement)
            + u16::from(self.capacity)
            + u16::from(self.harvest)
            + u16::from(self.chop)
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
pub struct WorkerState {
    pub spec: u8,
    pub free_at: u16,
    pub delivery_resource: u8,
    pub delivery_amount: u16,
    pub at_shack: bool,
}

impl WorkerState {
    fn idle_at(self, now: u16) -> bool {
        self.free_at <= now && self.delivery_resource == NO_RESOURCE
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
pub struct SourceState {
    pub id: u16,
    pub resource: u8,
    pub distance: u8,
    pub stock: u16,
    pub ready_at: u16,
    pub crop_amount: u8,
    pub infinite: bool,
}

impl SourceState {
    pub const fn finite(id: u16, resource: usize, distance: u8, stock: u16) -> Self {
        Self {
            id,
            resource: resource as u8,
            distance,
            stock,
            ready_at: NO_EVENT,
            crop_amount: 0,
            infinite: false,
        }
    }

    pub const fn infinite(id: u16, resource: usize, distance: u8) -> Self {
        Self {
            id,
            resource: resource as u8,
            distance,
            stock: 0,
            ready_at: NO_EVENT,
            crop_amount: 0,
            infinite: true,
        }
    }

    fn active_at(self, now: u16) -> bool {
        self.ready_at == NO_EVENT || self.ready_at <= now
    }
}

#[derive(Clone, Copy, Debug, Eq, Hash, Ord, PartialEq, PartialOrd)]
pub struct PlantOption {
    pub id: u8,
    pub seed_resource: u8,
    pub distance: u8,
    pub growth_delay: u16,
    pub crop_amount: u8,
    pub max_count: u8,
}

impl PlantOption {
    pub const fn new(
        id: u8,
        seed_resource: usize,
        distance: u8,
        growth_delay: u16,
        crop_amount: u8,
        max_count: u8,
    ) -> Self {
        Self {
            id,
            seed_resource: seed_resource as u8,
            distance,
            growth_delay,
            crop_amount,
            max_count,
        }
    }
}

#[derive(Clone, Debug, Eq, Hash, PartialEq)]
pub struct OpeningState {
    pub now: u16,
    pub bank: [u16; 4],
    pub workers: Vec<WorkerState>,
    pub sources: Vec<SourceState>,
    pub plants_used: Vec<u8>,
    pub last_train_turn: u16,
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub enum OpeningAction {
    Train {
        at: u16,
        spec: u8,
    },
    Fetch {
        at: u16,
        worker: u8,
        source: u16,
        resource: u8,
        amount: u16,
        duration: u16,
    },
    Plant {
        at: u16,
        worker: u8,
        option: u8,
        resource: u8,
        duration: u16,
    },
    Leave {
        at: u16,
        worker: u8,
    },
    Advance {
        to: u16,
    },
}

impl OpeningAction {
    pub fn describe(self, problem: &OpeningProblem) -> String {
        match self {
            Self::Train { at, spec } => {
                format!("t={at}: TRAIN {}", problem.specs[usize::from(spec)].name)
            }
            Self::Fetch {
                at,
                worker,
                source,
                resource,
                amount,
                duration,
            } => format!(
                "t={at}: worker {worker} fetches {amount} {} from source {source} ({duration} turns)",
                RESOURCE_NAMES[usize::from(resource)]
            ),
            Self::Plant {
                at,
                worker,
                option,
                resource,
                duration,
            } => format!(
                "t={at}: worker {worker} plants option {option} {} ({duration} turns away from work)",
                RESOURCE_NAMES[usize::from(resource)]
            ),
            Self::Leave { at, worker } => {
                format!("t={at}: worker {worker} leaves the shack")
            }
            Self::Advance { to } => format!("advance to turn {to}"),
        }
    }
}

#[derive(Clone, Debug, Eq, Hash, PartialEq)]
pub struct StructuralKey {
    workers: Vec<WorkerKey>,
    sources: Vec<SourceKey>,
    plants_used: Vec<u8>,
    train_locked: bool,
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct WorkerKey {
    spec: u8,
    free_delay: u16,
    delivery_resource: u8,
    delivery_amount: u16,
    at_shack: bool,
}

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
struct SourceKey {
    id: u16,
    resource: u8,
    distance: u8,
    stock: u16,
    ready_delay: u16,
    crop_amount: u8,
    infinite: bool,
}

#[derive(Clone, Debug)]
pub struct OpeningProblem {
    pub specs: Vec<WorkerSpec>,
    pub initial_bank: [u16; 4],
    pub initial_workers: Vec<u8>,
    pub initial_sources: Vec<SourceState>,
    pub training_stages: Vec<Vec<u8>>,
    pub plant_options: Vec<PlantOption>,
    pub start_turn: u16,
    pub max_turn: u16,
}

impl OpeningProblem {
    pub fn validate(&self) -> Result<(), String> {
        if self.initial_workers.is_empty() {
            return Err("at least one initial worker is required".into());
        }
        if self.max_turn < self.start_turn {
            return Err("max_turn precedes start_turn".into());
        }
        if self.training_stages.iter().any(Vec::is_empty) {
            return Err("every training stage needs at least one option".into());
        }
        for &spec in self
            .initial_workers
            .iter()
            .chain(self.training_stages.iter().flatten())
        {
            if usize::from(spec) >= self.specs.len() {
                return Err(format!("unknown worker spec {spec}"));
            }
            let value = self.specs[usize::from(spec)];
            if value.movement == 0 || value.capacity == 0 {
                return Err(format!("worker {} has zero movement/capacity", value.name));
            }
        }
        for (index, option) in self.plant_options.iter().enumerate() {
            if usize::from(option.id) != index {
                return Err("plant option ids must be dense and ordered".into());
            }
            if usize::from(option.seed_resource) >= 4 {
                return Err("plant option has invalid resource".into());
            }
        }
        Ok(())
    }

    pub fn initial_count(&self) -> usize {
        self.initial_workers.len()
    }

    pub fn goal_count(&self) -> usize {
        self.initial_count() + self.training_stages.len()
    }

    pub fn current_stage(&self, state: &OpeningState) -> usize {
        state.workers.len() - self.initial_count()
    }

    pub fn training_cost(&self, n_existing: usize, spec_id: u8) -> [u16; 4] {
        let spec = self.specs[usize::from(spec_id)];
        let n = u16::try_from(n_existing).expect("opening roster fits u16");
        [
            n + u16::from(spec.movement).pow(2),
            n + u16::from(spec.capacity).pow(2),
            n + u16::from(spec.harvest).pow(2),
            n + u16::from(spec.chop).pow(2),
        ]
    }

    fn affordable(&self, state: &OpeningState, spec_id: u8) -> bool {
        let cost = self.training_cost(state.workers.len(), spec_id);
        state
            .bank
            .iter()
            .zip(cost.iter())
            .all(|(have, need)| have >= need)
    }

    fn pending_resources(&self, state: &OpeningState) -> [u16; 4] {
        let mut pending = [0_u16; 4];
        for worker in &state.workers {
            if worker.delivery_resource != NO_RESOURCE {
                let resource = usize::from(worker.delivery_resource);
                pending[resource] = pending[resource].saturating_add(worker.delivery_amount);
            }
        }
        pending
    }

    fn future_resource_cap(&self, state: &OpeningState) -> [u16; 4] {
        let stage = self.current_stage(state);
        let mut cap = [0_u16; 4];
        for (offset, options) in self.training_stages[stage..].iter().enumerate() {
            let n = self.initial_count() + stage + offset;
            for resource in 0..4 {
                let largest = options
                    .iter()
                    .map(|&spec| self.training_cost(n, spec)[resource])
                    .max()
                    .unwrap_or(0);
                cap[resource] = cap[resource].saturating_add(largest);
            }
        }
        for (index, option) in self.plant_options.iter().enumerate() {
            let remaining = option.max_count.saturating_sub(state.plants_used[index]);
            let resource = usize::from(option.seed_resource);
            cap[resource] = cap[resource].saturating_add(u16::from(remaining));
        }
        cap
    }

    fn best_relaxed_rate(
        &self,
        worker: WorkerSpec,
        resource: usize,
        sources: &[SourceState],
    ) -> u16 {
        let service = if resource == IRON {
            worker.chop
        } else {
            worker.harvest
        };
        if service == 0 {
            return 0;
        }
        let mut best = 0_u16;
        for source in sources {
            if usize::from(source.resource) != resource {
                continue;
            }
            let amount = if source.infinite {
                u16::from(worker.capacity)
            } else {
                u16::from(worker.capacity).min(source.stock.max(u16::from(source.crop_amount)))
            };
            if amount == 0 {
                continue;
            }
            best = best.max(
                u16::from(worker.capacity)
                    .min(u16::from(service))
                    .min(amount),
            );
        }
        best
    }

    fn assignment_successors(
        &self,
        state: &OpeningState,
        worker_index: usize,
        worker: WorkerState,
        output: &mut Vec<Transition<OpeningState, OpeningAction>>,
    ) {
        let caps = self.future_resource_cap(state);
        let pending = self.pending_resources(state);

        if worker.at_shack {
            let mut next = state.clone();
            next.workers[worker_index] = WorkerState {
                free_at: state.now.saturating_add(1),
                at_shack: false,
                ..worker
            };
            output.push(Transition {
                action: OpeningAction::Leave {
                    at: state.now,
                    worker: worker_index as u8,
                },
                state: next,
            });
        }

        for source_index in 0..state.sources.len() {
            let source = state.sources[source_index];
            if !source.active_at(state.now) || (!source.infinite && source.stock == 0) {
                continue;
            }
            let resource = usize::from(source.resource);
            let useful = caps[resource]
                .saturating_sub(state.bank[resource])
                .saturating_sub(pending[resource]);
            if useful == 0 {
                continue;
            }
            let spec = self.specs[usize::from(worker.spec)];
            let service = if resource == IRON {
                spec.chop
            } else {
                spec.harvest
            };
            if service == 0 {
                continue;
            }

            let mut max_take = u16::from(spec.capacity).min(useful);
            if !source.infinite {
                max_take = max_take.min(source.stock);
            }
            if max_take == 0 {
                continue;
            }

            let mut quantities = Vec::new();
            let mut previous_service_turns = 0_u16;
            for amount in 1..=max_take {
                let service_turns = ceil_div(amount, u16::from(service));
                if service_turns != previous_service_turns || amount == max_take {
                    quantities.push(amount);
                }
                previous_service_turns = service_turns;
            }
            quantities.sort_unstable();
            quantities.dedup();

            for amount in quantities {
                let travel = ceil_div(u16::from(source.distance), u16::from(spec.movement));
                let duration = travel
                    .saturating_add(ceil_div(amount, u16::from(service)))
                    .saturating_add(travel)
                    .saturating_add(1);
                let mut next = state.clone();
                next.workers[worker_index] = WorkerState {
                    spec: worker.spec,
                    free_at: state.now.saturating_add(duration),
                    delivery_resource: source.resource,
                    delivery_amount: amount,
                    at_shack: false,
                };
                if !source.infinite {
                    next.sources[source_index].stock -= amount;
                }
                output.push(Transition {
                    action: OpeningAction::Fetch {
                        at: state.now,
                        worker: worker_index as u8,
                        source: source.id,
                        resource: source.resource,
                        amount,
                        duration,
                    },
                    state: next,
                });
            }
        }

        for (option_index, option) in self.plant_options.iter().copied().enumerate() {
            let used = state.plants_used[option_index];
            let resource = usize::from(option.seed_resource);
            if used >= option.max_count || state.bank[resource] == 0 {
                continue;
            }
            let spec = self.specs[usize::from(worker.spec)];
            let travel = ceil_div(u16::from(option.distance), u16::from(spec.movement));
            let worker_duration = 1_u16
                .saturating_add(travel)
                .saturating_add(1)
                .saturating_add(travel);
            let ready_at = state
                .now
                .saturating_add(1)
                .saturating_add(travel)
                .saturating_add(1)
                .saturating_add(option.growth_delay);
            let mut next = state.clone();
            next.bank[resource] -= 1;
            next.workers[worker_index] = WorkerState {
                spec: worker.spec,
                free_at: state.now.saturating_add(worker_duration),
                delivery_resource: NO_RESOURCE,
                delivery_amount: 0,
                at_shack: false,
            };
            next.plants_used[option_index] += 1;
            let source_id = 0x8000_u16
                .saturating_add(u16::from(option.id) * 256)
                .saturating_add(u16::from(used) + 1);
            next.sources.push(SourceState {
                id: source_id,
                resource: option.seed_resource,
                distance: option.distance,
                stock: 0,
                ready_at,
                crop_amount: option.crop_amount,
                infinite: false,
            });
            next.sources.sort_unstable();
            output.push(Transition {
                action: OpeningAction::Plant {
                    at: state.now,
                    worker: worker_index as u8,
                    option: option.id,
                    resource: option.seed_resource,
                    duration: worker_duration,
                },
                state: next,
            });
        }
    }

    fn advance_to_next_event(&self, state: &OpeningState) -> Option<OpeningState> {
        let worker_time = state
            .workers
            .iter()
            .filter_map(|worker| (worker.free_at > state.now).then_some(worker.free_at))
            .min();
        let source_time = state
            .sources
            .iter()
            .filter_map(|source| {
                (source.ready_at != NO_EVENT && source.ready_at > state.now)
                    .then_some(source.ready_at)
            })
            .min();
        let next_time = match (worker_time, source_time) {
            (Some(left), Some(right)) => left.min(right),
            (Some(value), None) | (None, Some(value)) => value,
            (None, None) => return None,
        };
        if next_time > self.max_turn {
            return None;
        }

        let mut next = state.clone();
        next.now = next_time;
        for worker in &mut next.workers {
            if worker.free_at <= next_time && worker.delivery_resource != NO_RESOURCE {
                let resource = usize::from(worker.delivery_resource);
                next.bank[resource] = next.bank[resource].saturating_add(worker.delivery_amount);
                worker.free_at = next_time;
                worker.delivery_resource = NO_RESOURCE;
                worker.delivery_amount = 0;
                worker.at_shack = false;
            }
        }
        for source in &mut next.sources {
            if source.ready_at != NO_EVENT && source.ready_at <= next_time {
                source.stock = source.stock.saturating_add(u16::from(source.crop_amount));
                source.ready_at = NO_EVENT;
            }
        }
        Some(next)
    }

    pub fn current_deficit(&self, state: &OpeningState) -> [u16; 4] {
        if self.is_goal(state) {
            return [0; 4];
        }
        let stage = self.current_stage(state);
        let bill = self.training_stages[stage]
            .iter()
            .map(|&spec| self.training_cost(state.workers.len(), spec))
            .min_by_key(|candidate| {
                (0..4)
                    .map(|resource| candidate[resource].saturating_sub(state.bank[resource]))
                    .sum::<u16>()
            })
            .expect("stage has options");
        std::array::from_fn(|resource| bill[resource].saturating_sub(state.bank[resource]))
    }

    pub fn greedy_incumbent(
        &self,
        max_steps: usize,
    ) -> Option<FeasiblePlan<OpeningState, OpeningAction>> {
        let mut state = self.initial_state();
        let mut actions = Vec::new();
        let mut successors = Vec::new();

        for _ in 0..max_steps {
            if self.is_goal(&state) {
                return Some(FeasiblePlan { state, actions });
            }
            successors.clear();
            self.successors(&state, &mut successors);
            if successors.is_empty() {
                return None;
            }

            let chosen = successors
                .iter()
                .enumerate()
                .filter_map(|(index, transition)| match transition.action {
                    OpeningAction::Train { spec, .. } => {
                        Some((index, self.specs[usize::from(spec)].strength()))
                    }
                    _ => None,
                })
                .max_by_key(|(_, strength)| *strength)
                .map(|(index, _)| index)
                .or_else(|| {
                    let deficit = self.current_deficit(&state);
                    successors
                        .iter()
                        .enumerate()
                        .filter_map(|(index, transition)| match transition.action {
                            OpeningAction::Fetch {
                                resource,
                                amount,
                                duration,
                                ..
                            } if deficit[usize::from(resource)] > 0 => Some((
                                index,
                                amount.min(deficit[usize::from(resource)]),
                                duration,
                                amount,
                            )),
                            _ => None,
                        })
                        .max_by(|left, right| {
                            let left_score = u32::from(left.1) * u32::from(right.2.max(1));
                            let right_score = u32::from(right.1) * u32::from(left.2.max(1));
                            left_score
                                .cmp(&right_score)
                                .then_with(|| left.3.cmp(&right.3))
                                // Python max keeps the first exact tie. Prefer the
                                // smaller successor index to preserve that behavior.
                                .then_with(|| right.0.cmp(&left.0))
                        })
                        .map(|value| value.0)
                })
                .or_else(|| {
                    successors.iter().position(|transition| {
                        matches!(transition.action, OpeningAction::Leave { .. })
                    })
                })
                .or_else(|| {
                    successors.iter().position(|transition| {
                        matches!(transition.action, OpeningAction::Advance { .. })
                    })
                })
                .or_else(|| {
                    successors.iter().position(|transition| {
                        matches!(transition.action, OpeningAction::Plant { .. })
                    })
                })?;

            let transition = successors.swap_remove(chosen);
            actions.push(transition.action);
            state = transition.state;
        }
        None
    }

    pub fn hybrid_solve(&self, limits: SearchLimits) -> SearchResult<OpeningState, OpeningAction> {
        let incumbent = self.greedy_incumbent(10_000);
        search_anytime(self, incumbent, limits)
    }
}

impl SearchProblem for OpeningProblem {
    type State = OpeningState;
    type Action = OpeningAction;
    type StructuralKey = StructuralKey;

    fn initial_state(&self) -> Self::State {
        let mut sources = self.initial_sources.clone();
        sources.sort_unstable();
        OpeningState {
            now: self.start_turn,
            bank: self.initial_bank,
            workers: self
                .initial_workers
                .iter()
                .map(|&spec| WorkerState {
                    spec,
                    free_at: self.start_turn,
                    delivery_resource: NO_RESOURCE,
                    delivery_amount: 0,
                    at_shack: true,
                })
                .collect(),
            sources,
            plants_used: vec![0; self.plant_options.len()],
            last_train_turn: NO_EVENT,
        }
    }

    fn is_goal(&self, state: &Self::State) -> bool {
        state.workers.len() >= self.goal_count()
    }

    fn elapsed(&self, state: &Self::State) -> u16 {
        state.now
    }

    fn lower_bound(&self, state: &Self::State) -> u16 {
        if self.is_goal(state) {
            return state.now;
        }
        if state.now > self.max_turn {
            return INF_TURN;
        }

        let stage = self.current_stage(state);
        let pending = self.pending_resources(state);
        let mut optimistic_bank: [u16; 4] =
            std::array::from_fn(|resource| state.bank[resource].saturating_add(pending[resource]));
        for source in &state.sources {
            if source.ready_at != NO_EVENT && source.ready_at > state.now {
                let resource = usize::from(source.resource);
                optimistic_bank[resource] =
                    optimistic_bank[resource].saturating_add(u16::from(source.crop_amount));
            }
        }

        let mut best = INF_TURN;
        for &spec_id in &self.training_stages[stage] {
            let bill = self.training_cost(state.workers.len(), spec_id);
            let deficits: [u16; 4] = std::array::from_fn(|resource| {
                bill[resource].saturating_sub(optimistic_bank[resource])
            });
            let mut feasible = true;
            let mut slowest = 0_u16;

            for resource in 0..4 {
                let deficit = deficits[resource];
                if deficit == 0 {
                    continue;
                }
                let mut total_rate = 0_u16;
                for worker in &state.workers {
                    total_rate = total_rate.saturating_add(self.best_relaxed_rate(
                        self.specs[usize::from(worker.spec)],
                        resource,
                        &state.sources,
                    ));
                }
                if total_rate == 0
                    && self
                        .plant_options
                        .iter()
                        .any(|option| usize::from(option.seed_resource) == resource)
                {
                    total_rate = state
                        .workers
                        .iter()
                        .map(|worker| {
                            u16::from(self.specs[usize::from(worker.spec)].harvest.max(1))
                        })
                        .sum();
                }
                if total_rate == 0 {
                    feasible = false;
                    break;
                }
                slowest = slowest.max(ceil_div(deficit, total_rate));
            }
            if feasible {
                best = best.min(state.now.saturating_add(slowest));
            }
        }
        best
    }

    fn successors(
        &self,
        state: &Self::State,
        output: &mut Vec<Transition<Self::State, Self::Action>>,
    ) {
        output.clear();
        if self.is_goal(state) || state.now > self.max_turn {
            return;
        }

        let stage = self.current_stage(state);
        if stage < self.training_stages.len()
            && state.last_train_turn != state.now
            && !state.workers.iter().any(|worker| worker.at_shack)
        {
            for &spec_id in &self.training_stages[stage] {
                if !self.affordable(state, spec_id) {
                    continue;
                }
                let cost = self.training_cost(state.workers.len(), spec_id);
                let mut next = state.clone();
                for resource in 0..4 {
                    next.bank[resource] -= cost[resource];
                }
                next.workers.push(WorkerState {
                    spec: spec_id,
                    free_at: state.now.saturating_add(1),
                    delivery_resource: NO_RESOURCE,
                    delivery_amount: 0,
                    at_shack: true,
                });
                next.last_train_turn = state.now;
                output.push(Transition {
                    action: OpeningAction::Train {
                        at: state.now,
                        spec: spec_id,
                    },
                    state: next,
                });
            }
        }

        if let Some((worker_index, &worker)) = state
            .workers
            .iter()
            .enumerate()
            .find(|(_, worker)| worker.idle_at(state.now))
        {
            self.assignment_successors(state, worker_index, worker, output);
        }

        if let Some(next) = self.advance_to_next_event(state) {
            output.push(Transition {
                action: OpeningAction::Advance { to: next.now },
                state: next,
            });
        }
    }

    fn structural_key(&self, state: &Self::State) -> Self::StructuralKey {
        StructuralKey {
            workers: state
                .workers
                .iter()
                .map(|worker| WorkerKey {
                    spec: worker.spec,
                    free_delay: worker.free_at.saturating_sub(state.now),
                    delivery_resource: worker.delivery_resource,
                    delivery_amount: worker.delivery_amount,
                    at_shack: worker.at_shack,
                })
                .collect(),
            sources: state
                .sources
                .iter()
                .map(|source| SourceKey {
                    id: source.id,
                    resource: source.resource,
                    distance: source.distance,
                    stock: source.stock,
                    ready_delay: if source.ready_at == NO_EVENT {
                        NO_EVENT
                    } else {
                        source.ready_at.saturating_sub(state.now)
                    },
                    crop_amount: source.crop_amount,
                    infinite: source.infinite,
                })
                .collect(),
            plants_used: state.plants_used.clone(),
            train_locked: state.last_train_turn == state.now,
        }
    }

    fn resources(&self, state: &Self::State) -> [u16; 4] {
        state.bank
    }
}

pub fn global_assignment_problem() -> OpeningProblem {
    let specs = vec![
        WorkerSpec::new("versatile", 2, 2, 2, 2),
        WorkerSpec::new("harvester", 1, 2, 1, 0),
        WorkerSpec::new("target", 1, 1, 0, 1),
    ];
    OpeningProblem {
        specs,
        initial_bank: [3, 1, 2, 1],
        initial_workers: vec![0, 1],
        initial_sources: vec![
            SourceState::finite(0, LEMON, 1, 2),
            SourceState::infinite(1, IRON, 2),
        ],
        training_stages: vec![vec![2]],
        plant_options: Vec::new(),
        start_turn: 1,
        max_turn: 20,
    }
}

pub fn plant_investment_problem() -> OpeningProblem {
    let specs = vec![
        WorkerSpec::new("starter", 1, 3, 3, 1),
        WorkerSpec::new("target", 1, 1, 0, 0),
    ];
    OpeningProblem {
        specs,
        initial_bank: [2, 1, 1, 1],
        initial_workers: vec![0],
        initial_sources: vec![SourceState::finite(0, LEMON, 5, 3)],
        training_stages: vec![vec![1]],
        plant_options: vec![PlantOption::new(0, LEMON, 1, 2, 3, 1)],
        start_turn: 1,
        max_turn: 20,
    }
}

pub fn two_stage_problem() -> OpeningProblem {
    let specs = vec![
        WorkerSpec::new("starter", 1, 2, 1, 1),
        WorkerSpec::new("cheap-gatherer", 1, 3, 2, 1),
        WorkerSpec::new("fast-expensive", 2, 2, 1, 2),
        WorkerSpec::new("target-chop2", 2, 2, 1, 2),
    ];
    OpeningProblem {
        specs,
        initial_bank: [8, 8, 5, 7],
        initial_workers: vec![0],
        initial_sources: vec![
            SourceState::finite(0, PLUM, 1, 6),
            SourceState::finite(1, LEMON, 4, 7),
            SourceState::finite(2, APPLE, 2, 4),
            SourceState::infinite(3, IRON, 2),
        ],
        training_stages: vec![vec![1, 2], vec![3]],
        plant_options: vec![PlantOption::new(0, LEMON, 1, 4, 3, 1)],
        start_turn: 1,
        max_turn: 60,
    }
}

pub fn infeasible_problem() -> OpeningProblem {
    let specs = vec![
        WorkerSpec::new("starter", 1, 1, 1, 0),
        WorkerSpec::new("target", 1, 1, 0, 0),
    ];
    OpeningProblem {
        specs,
        initial_bank: [2, 0, 1, 1],
        initial_workers: vec![0],
        initial_sources: vec![
            SourceState::finite(0, PLUM, 1, 3),
            SourceState::finite(1, APPLE, 1, 3),
        ],
        training_stages: vec![vec![1]],
        plant_options: Vec::new(),
        start_turn: 1,
        max_turn: 20,
    }
}
