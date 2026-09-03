//! Event-driven anytime A*/dynamic-programming search.
//!
//! The search has two operating modes:
//! * with unbounded limits it can close the frontier and certify an optimum
//!   inside the supplied model and action vocabulary;
//! * with a wall-clock/state budget it always keeps a feasible incumbent and
//!   returns it when the deadline is reached. If the exact queue reaches its
//!   state cap, a bounded beam search can use the remaining time without
//!   exceeding the configured number of retained states.

use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap, HashSet};
use std::fmt::Debug;
use std::hash::Hash;
use std::time::{Duration, Instant};

pub const INF_TURN: u16 = u16::MAX;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Transition<S, A> {
    pub action: A,
    pub state: S,
}

pub trait SearchProblem {
    type State: Clone + Debug + Eq + Hash;
    type Action: Clone + Debug + Eq;
    type StructuralKey: Clone + Eq + Hash;

    fn initial_state(&self) -> Self::State;
    fn is_goal(&self, state: &Self::State) -> bool;
    fn elapsed(&self, state: &Self::State) -> u16;

    /// Absolute earliest possible goal turn reachable from `state`.
    ///
    /// It may be weak, but must never be later than the true best completion
    /// turn reachable from the state.
    fn lower_bound(&self, state: &Self::State) -> u16;

    fn successors(
        &self,
        state: &Self::State,
        output: &mut Vec<Transition<Self::State, Self::Action>>,
    );

    /// Every fact that can change future transitions must be present here.
    fn structural_key(&self, state: &Self::State) -> Self::StructuralKey;

    /// Monotone resources used for Pareto dominance under an equal key.
    fn resources(&self, state: &Self::State) -> [u16; 4];
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct FeasiblePlan<S, A> {
    pub state: S,
    pub actions: Vec<A>,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum StopReason {
    Optimal,
    Infeasible,
    TimeBudget,
    ExpansionBudget,
    StateBudget,
    BeamTimeBudget,
    BeamRoundBudget,
    BeamExhausted,
}

#[derive(Clone, Debug)]
pub struct SearchLimits {
    pub wall_time: Option<Duration>,
    pub max_expansions: usize,
    pub max_states: usize,
    pub deadline_check_interval: usize,
    pub beam_width: usize,
    pub max_beam_rounds: usize,
}

impl SearchLimits {
    pub fn proof() -> Self {
        Self {
            wall_time: None,
            max_expansions: usize::MAX,
            max_states: usize::MAX,
            deadline_check_interval: 256,
            beam_width: 0,
            max_beam_rounds: 0,
        }
    }

    pub fn online(wall_time: Duration) -> Self {
        Self {
            wall_time: Some(wall_time),
            max_expansions: usize::MAX,
            max_states: 200_000,
            deadline_check_interval: 64,
            beam_width: 4_096,
            max_beam_rounds: 192,
        }
    }

    fn normalised(&self) -> Self {
        let mut value = self.clone();
        value.max_states = value.max_states.max(1);
        value.deadline_check_interval = value.deadline_check_interval.max(1);
        value
    }
}

#[derive(Clone, Debug, Default)]
pub struct SearchStats {
    pub astar_expanded: usize,
    pub astar_generated: usize,
    pub pruned_by_bound: usize,
    pub pruned_by_dominance: usize,
    pub stale_queue_entries: usize,
    pub astar_nodes: usize,
    pub astar_peak_queue: usize,
    pub beam_expanded: usize,
    pub beam_generated: usize,
    pub beam_peak_width: usize,
    pub elapsed: Duration,
}

#[derive(Clone, Debug)]
pub struct SearchResult<S, A> {
    pub plan: Option<FeasiblePlan<S, A>>,
    pub proven_optimal: bool,
    pub lower_bound_at_stop: Option<u16>,
    pub stop_reason: StopReason,
    pub used_beam_fallback: bool,
    pub stats: SearchStats,
}

impl<S, A> SearchResult<S, A> {
    pub fn completion_time<P>(&self, problem: &P) -> Option<u16>
    where
        P: SearchProblem<State = S, Action = A>,
    {
        self.plan.as_ref().map(|plan| problem.elapsed(&plan.state))
    }

    pub fn optimality_gap<P>(&self, problem: &P) -> Option<u16>
    where
        P: SearchProblem<State = S, Action = A>,
    {
        let upper = self.completion_time(problem)?;
        let lower = self.lower_bound_at_stop?;
        Some(upper.saturating_sub(lower))
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
struct QueueEntry {
    lower_bound: u16,
    elapsed: u16,
    serial: u64,
    node: usize,
}

impl Ord for QueueEntry {
    fn cmp(&self, other: &Self) -> Ordering {
        // BinaryHeap is a max-heap. Reverse every field so the smallest lower
        // bound, elapsed turn and serial number is popped first.
        other
            .lower_bound
            .cmp(&self.lower_bound)
            .then_with(|| other.elapsed.cmp(&self.elapsed))
            .then_with(|| other.serial.cmp(&self.serial))
    }
}

impl PartialOrd for QueueEntry {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

#[derive(Clone, Debug)]
struct Node<S, A> {
    state: S,
    parent: Option<usize>,
    action: Option<A>,
    queued: bool,
}

#[derive(Clone, Copy, Debug)]
struct Label {
    elapsed: u16,
    resources: [u16; 4],
    node: usize,
}

#[derive(Clone, Debug)]
struct CoreOutcome<S, A> {
    plan: Option<FeasiblePlan<S, A>>,
    proven_optimal: bool,
    lower_bound_at_stop: Option<u16>,
    stop_reason: StopReason,
    stats: SearchStats,
}

fn deadline_reached(deadline: Option<Instant>) -> bool {
    deadline.is_some_and(|at| Instant::now() >= at)
}

fn resource_ge(left: &[u16; 4], right: &[u16; 4]) -> bool {
    left.iter().zip(right.iter()).all(|(a, b)| a >= b)
}

fn reconstruct<S, A: Clone>(nodes: &[Node<S, A>], mut node: usize) -> Vec<A> {
    let mut reversed = Vec::new();
    while let Some(parent) = nodes[node].parent {
        reversed.push(
            nodes[node]
                .action
                .as_ref()
                .expect("non-root node must have an action")
                .clone(),
        );
        node = parent;
    }
    reversed.reverse();
    reversed
}

fn min_live_lower_bound<S, A>(
    heap: &BinaryHeap<QueueEntry>,
    nodes: &[Node<S, A>],
) -> Option<u16> {
    // Stale entries may sit at the top. Inspecting the heap is O(n), but this
    // happens only when stopping and keeps the certificate honest.
    heap.iter()
        .filter(|entry| nodes.get(entry.node).is_some_and(|node| node.queued))
        .map(|entry| entry.lower_bound)
        .min()
}

fn astar<P>(
    problem: &P,
    incumbent: Option<FeasiblePlan<P::State, P::Action>>,
    limits: &SearchLimits,
    deadline: Option<Instant>,
) -> CoreOutcome<P::State, P::Action>
where
    P: SearchProblem,
{
    let start = problem.initial_state();
    let start_lower = problem.lower_bound(&start);

    let mut best_plan = incumbent;
    if let Some(plan) = &best_plan {
        assert!(problem.is_goal(&plan.state), "incumbent must be a goal");
    }
    let mut best_time = best_plan
        .as_ref()
        .map(|plan| problem.elapsed(&plan.state))
        .unwrap_or(INF_TURN);

    if problem.is_goal(&start) {
        let completion = problem.elapsed(&start);
        return CoreOutcome {
            plan: Some(FeasiblePlan {
                state: start,
                actions: Vec::new(),
            }),
            proven_optimal: true,
            lower_bound_at_stop: Some(completion),
            stop_reason: StopReason::Optimal,
            stats: SearchStats::default(),
        };
    }

    if deadline_reached(deadline) {
        return CoreOutcome {
            plan: best_plan,
            proven_optimal: false,
            lower_bound_at_stop: (start_lower != INF_TURN).then_some(start_lower),
            stop_reason: StopReason::TimeBudget,
            stats: SearchStats::default(),
        };
    }

    if start_lower >= best_time {
        return CoreOutcome {
            plan: best_plan,
            proven_optimal: best_time != INF_TURN,
            lower_bound_at_stop: (best_time != INF_TURN).then_some(best_time),
            stop_reason: if best_time == INF_TURN {
                StopReason::Infeasible
            } else {
                StopReason::Optimal
            },
            stats: SearchStats::default(),
        };
    }

    if start_lower == INF_TURN {
        return CoreOutcome {
            plan: best_plan,
            proven_optimal: false,
            lower_bound_at_stop: None,
            stop_reason: StopReason::Infeasible,
            stats: SearchStats::default(),
        };
    }

    let mut nodes: Vec<Node<P::State, P::Action>> = Vec::new();
    let mut heap = BinaryHeap::new();
    let mut frontiers: HashMap<P::StructuralKey, Vec<Label>> = HashMap::new();
    let mut serial = 0_u64;

    let start_resources = problem.resources(&start);
    let start_key = problem.structural_key(&start);
    nodes.push(Node {
        state: start,
        parent: None,
        action: None,
        queued: true,
    });
    frontiers.entry(start_key).or_default().push(Label {
        elapsed: problem.elapsed(&nodes[0].state),
        resources: start_resources,
        node: 0,
    });
    heap.push(QueueEntry {
        lower_bound: start_lower,
        elapsed: problem.elapsed(&nodes[0].state),
        serial,
        node: 0,
    });
    serial += 1;

    let mut stats = SearchStats {
        astar_nodes: 1,
        astar_peak_queue: 1,
        ..SearchStats::default()
    };
    let mut stop_reason: Option<StopReason> = None;
    let mut lower_at_stop: Option<u16> = None;
    let mut successors = Vec::new();

    'search: loop {
        if heap.is_empty() {
            break;
        }

        if stats.astar_expanded >= limits.max_expansions {
            stop_reason = Some(StopReason::ExpansionBudget);
            lower_at_stop = min_live_lower_bound(&heap, &nodes);
            break;
        }
        if deadline_reached(deadline) {
            stop_reason = Some(StopReason::TimeBudget);
            lower_at_stop = min_live_lower_bound(&heap, &nodes);
            break;
        }

        let entry = heap.pop().expect("heap checked non-empty");
        if !nodes[entry.node].queued {
            stats.stale_queue_entries += 1;
            continue;
        }
        if entry.lower_bound >= best_time {
            stop_reason = Some(StopReason::Optimal);
            lower_at_stop = Some(best_time);
            break;
        }

        nodes[entry.node].queued = false;
        let state = nodes[entry.node].state.clone();
        stats.astar_expanded += 1;
        successors.clear();
        problem.successors(&state, &mut successors);

        for (successor_index, transition) in successors.drain(..).enumerate() {
            stats.astar_generated += 1;
            if successor_index % limits.deadline_check_interval == 0
                && deadline_reached(deadline)
            {
                stop_reason = Some(StopReason::TimeBudget);
                lower_at_stop = Some(
                    min_live_lower_bound(&heap, &nodes)
                        .unwrap_or(entry.lower_bound)
                        .min(entry.lower_bound),
                );
                break 'search;
            }

            let next = transition.state;
            let next_lower = problem.lower_bound(&next);
            if next_lower >= best_time {
                stats.pruned_by_bound += 1;
                continue;
            }

            if problem.is_goal(&next) {
                let completion = problem.elapsed(&next);
                if completion < best_time {
                    let mut actions = reconstruct(&nodes, entry.node);
                    actions.push(transition.action);
                    best_time = completion;
                    best_plan = Some(FeasiblePlan {
                        state: next,
                        actions,
                    });
                }
                continue;
            }

            let elapsed = problem.elapsed(&next);
            let resources = problem.resources(&next);
            let key = problem.structural_key(&next);

            let dominated = frontiers.get(&key).is_some_and(|labels| {
                labels.iter().any(|label| {
                    label.elapsed <= elapsed && resource_ge(&label.resources, &resources)
                })
            });
            if dominated {
                stats.pruned_by_dominance += 1;
                continue;
            }

            if nodes.len() >= limits.max_states {
                stop_reason = Some(StopReason::StateBudget);
                lower_at_stop = Some(
                    min_live_lower_bound(&heap, &nodes)
                        .unwrap_or(next_lower)
                        .min(entry.lower_bound)
                        .min(next_lower),
                );
                break 'search;
            }

            let labels = frontiers.entry(key).or_default();
            let mut kept = Vec::with_capacity(labels.len() + 1);
            for label in labels.drain(..) {
                if elapsed <= label.elapsed && resource_ge(&resources, &label.resources) {
                    if let Some(old) = nodes.get_mut(label.node) {
                        old.queued = false;
                    }
                } else {
                    kept.push(label);
                }
            }

            let node_id = nodes.len();
            nodes.push(Node {
                state: next,
                parent: Some(entry.node),
                action: Some(transition.action),
                queued: true,
            });
            kept.push(Label {
                elapsed,
                resources,
                node: node_id,
            });
            *labels = kept;

            heap.push(QueueEntry {
                lower_bound: next_lower,
                elapsed,
                serial,
                node: node_id,
            });
            serial += 1;
            stats.astar_nodes = nodes.len();
            stats.astar_peak_queue = stats.astar_peak_queue.max(heap.len());
        }
    }

    let reason = stop_reason.unwrap_or_else(|| {
        if best_plan.is_some() {
            StopReason::Optimal
        } else {
            StopReason::Infeasible
        }
    });
    let proven = reason == StopReason::Optimal && best_plan.is_some();
    if lower_at_stop.is_none() {
        lower_at_stop = if proven {
            Some(best_time)
        } else if reason == StopReason::Infeasible {
            None
        } else {
            min_live_lower_bound(&heap, &nodes)
        };
    }

    CoreOutcome {
        plan: best_plan,
        proven_optimal: proven,
        lower_bound_at_stop: lower_at_stop,
        stop_reason: reason,
        stats,
    }
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Ord, PartialOrd)]
struct BeamRank {
    lower_bound: u16,
    elapsed: u16,
    resource_penalty: u32,
    path_len: u16,
}

#[derive(Clone, Debug)]
struct BeamNode<S, A> {
    state: S,
    actions: Vec<A>,
}

#[derive(Clone, Debug)]
struct BeamEntry<S, A> {
    rank: BeamRank,
    serial: u64,
    node: BeamNode<S, A>,
}

impl<S, A> PartialEq for BeamEntry<S, A> {
    fn eq(&self, other: &Self) -> bool {
        self.rank == other.rank && self.serial == other.serial
    }
}

impl<S, A> Eq for BeamEntry<S, A> {}

impl<S, A> Ord for BeamEntry<S, A> {
    fn cmp(&self, other: &Self) -> Ordering {
        self.rank
            .cmp(&other.rank)
            .then_with(|| self.serial.cmp(&other.serial))
    }
}

impl<S, A> PartialOrd for BeamEntry<S, A> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

#[derive(Clone, Debug)]
struct BeamOutcome<S, A> {
    plan: Option<FeasiblePlan<S, A>>,
    stop_reason: StopReason,
    stats: SearchStats,
}

fn beam_rank<P: SearchProblem>(problem: &P, state: &P::State, path_len: usize) -> BeamRank {
    let resources = problem.resources(state);
    let resource_sum: u32 = resources.iter().map(|value| u32::from(*value)).sum();
    BeamRank {
        lower_bound: problem.lower_bound(state),
        elapsed: problem.elapsed(state),
        resource_penalty: u32::MAX - resource_sum,
        path_len: u16::try_from(path_len).unwrap_or(u16::MAX),
    }
}

fn beam_search<P>(
    problem: &P,
    incumbent: Option<FeasiblePlan<P::State, P::Action>>,
    limits: &SearchLimits,
    deadline: Option<Instant>,
) -> BeamOutcome<P::State, P::Action>
where
    P: SearchProblem,
{
    let width = limits.beam_width.min(limits.max_states / 2).max(1);
    let mut best_plan = incumbent;
    let mut best_time = best_plan
        .as_ref()
        .map(|plan| problem.elapsed(&plan.state))
        .unwrap_or(INF_TURN);
    let mut frontier = vec![BeamNode {
        state: problem.initial_state(),
        actions: Vec::new(),
    }];
    let mut stats = SearchStats {
        beam_peak_width: 1,
        ..SearchStats::default()
    };
    let mut successors = Vec::new();
    let mut serial = 0_u64;

    for _round in 0..limits.max_beam_rounds {
        if deadline_reached(deadline) {
            return BeamOutcome {
                plan: best_plan,
                stop_reason: StopReason::BeamTimeBudget,
                stats,
            };
        }
        if frontier.is_empty() {
            return BeamOutcome {
                plan: best_plan,
                stop_reason: StopReason::BeamExhausted,
                stats,
            };
        }

        let mut retained: BinaryHeap<BeamEntry<P::State, P::Action>> = BinaryHeap::new();
        for item in frontier.drain(..) {
            stats.beam_expanded += 1;
            successors.clear();
            problem.successors(&item.state, &mut successors);
            for transition in successors.drain(..) {
                stats.beam_generated += 1;
                if stats.beam_generated % limits.deadline_check_interval == 0
                    && deadline_reached(deadline)
                {
                    return BeamOutcome {
                        plan: best_plan,
                        stop_reason: StopReason::BeamTimeBudget,
                        stats,
                    };
                }

                let mut actions = item.actions.clone();
                actions.push(transition.action);
                if problem.is_goal(&transition.state) {
                    let completion = problem.elapsed(&transition.state);
                    if completion < best_time {
                        best_time = completion;
                        best_plan = Some(FeasiblePlan {
                            state: transition.state,
                            actions,
                        });
                    }
                    continue;
                }

                let rank = beam_rank(problem, &transition.state, actions.len());
                if rank.lower_bound >= best_time || rank.lower_bound == INF_TURN {
                    continue;
                }
                let candidate = BeamEntry {
                    rank,
                    serial,
                    node: BeamNode {
                        state: transition.state,
                        actions,
                    },
                };
                serial += 1;

                if retained.len() < width {
                    retained.push(candidate);
                } else if retained
                    .peek()
                    .is_some_and(|worst| candidate.rank < worst.rank)
                {
                    retained.pop();
                    retained.push(candidate);
                }
            }
        }

        let mut next: Vec<_> = retained.into_vec();
        next.sort_by(|left, right| {
            left.rank
                .cmp(&right.rank)
                .then_with(|| left.serial.cmp(&right.serial))
        });
        let mut seen = HashSet::with_capacity(next.len());
        frontier = next
            .into_iter()
            .filter_map(|entry| {
                if seen.insert(entry.node.state.clone()) {
                    Some(entry.node)
                } else {
                    None
                }
            })
            .take(width)
            .collect();
        stats.beam_peak_width = stats.beam_peak_width.max(frontier.len());
    }

    BeamOutcome {
        plan: best_plan,
        stop_reason: StopReason::BeamRoundBudget,
        stats,
    }
}

/// Run exact A*/DP until it proves the incumbent or reaches a budget. When the
/// state cap is hit, continue with a fixed-width beam using any wall time left.
pub fn search_anytime<P>(
    problem: &P,
    incumbent: Option<FeasiblePlan<P::State, P::Action>>,
    limits: SearchLimits,
) -> SearchResult<P::State, P::Action>
where
    P: SearchProblem,
{
    let limits = limits.normalised();
    let started = Instant::now();
    let deadline = limits
        .wall_time
        .and_then(|duration| started.checked_add(duration));
    let mut exact = astar(problem, incumbent, &limits, deadline);
    let mut used_beam = false;

    if exact.stop_reason == StopReason::StateBudget
        && limits.beam_width > 0
        && limits.max_states >= 2
        && limits.max_beam_rounds > 0
        && !deadline_reached(deadline)
    {
        // A*'s nodes and dominance table are dropped before beam_search starts,
        // so the two modes do not coexist in memory. Beam width is clamped to
        // half max_states because current and next frontiers coexist.
        let beam = beam_search(problem, exact.plan.clone(), &limits, deadline);
        exact.plan = beam.plan;
        exact.stop_reason = beam.stop_reason;
        exact.stats.beam_expanded += beam.stats.beam_expanded;
        exact.stats.beam_generated += beam.stats.beam_generated;
        exact.stats.beam_peak_width = exact
            .stats
            .beam_peak_width
            .max(beam.stats.beam_peak_width);
        exact.proven_optimal = false;
        used_beam = true;
    }

    exact.stats.elapsed = started.elapsed();
    SearchResult {
        plan: exact.plan,
        proven_optimal: exact.proven_optimal,
        lower_bound_at_stop: exact.lower_bound_at_stop,
        stop_reason: exact.stop_reason,
        used_beam_fallback: used_beam,
        stats: exact.stats,
    }
}

/// Replay a returned sequence through the problem's own transition function.
/// Every action must name exactly one successor.
pub fn replay_actions<P>(problem: &P, actions: &[P::Action]) -> Result<P::State, String>
where
    P: SearchProblem,
{
    let mut state = problem.initial_state();
    let mut successors = Vec::new();
    for (index, action) in actions.iter().enumerate() {
        successors.clear();
        problem.successors(&state, &mut successors);
        let mut matches = successors
            .drain(..)
            .filter(|transition| &transition.action == action);
        let first = matches
            .next()
            .ok_or_else(|| format!("action {index} has no matching successor: {action:?}"))?;
        if matches.next().is_some() {
            return Err(format!(
                "action {index} identifies more than one successor: {action:?}"
            ));
        }
        state = first.state;
    }
    Ok(state)
}
