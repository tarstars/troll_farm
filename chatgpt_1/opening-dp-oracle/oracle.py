"""Generic event-driven A*/dynamic-programming search.

The engine knows nothing about Troll Farm.  A problem supplies immutable states,
exact macro transitions, an admissible absolute lower bound, and a dominance
projection.  The search is an anytime branch-and-bound algorithm:

* a quick incumbent (for example the existing greedy/Monte-Carlo solver) gives
  an upper bound;
* A* explores only states whose lower bound can still beat that incumbent;
* Pareto dominance removes structurally equivalent states that arrive no
  earlier with no more useful resources;
* if the queue is exhausted, or its smallest lower bound reaches the incumbent,
  the returned sequence is certified optimal inside the supplied model.
"""
from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf
from typing import Generic, Hashable, Iterable, Optional, Protocol, Sequence, TypeVar

StateT = TypeVar("StateT", bound=Hashable)
ActionT = TypeVar("ActionT")


@dataclass(frozen=True)
class Transition(Generic[StateT, ActionT]):
    action: ActionT
    state: StateT


class SearchProblem(Protocol[StateT, ActionT]):
    """Contract required by :func:`astar_dp`.

    ``lower_bound`` returns an *absolute* earliest possible goal time, not a
    remaining duration.  It may be weak (even just ``elapsed(state)``), but it
    must never exceed the true best completion time reachable from the state.

    ``dominance_key`` must contain every structural fact whose difference could
    change future transitions.  ``resources`` contains the monotone quantities
    for which more is never worse when that key is equal.
    """

    def initial_state(self) -> StateT: ...

    def is_goal(self, state: StateT) -> bool: ...

    def elapsed(self, state: StateT) -> int: ...

    def lower_bound(self, state: StateT) -> float: ...

    def successors(self, state: StateT) -> Iterable[Transition[StateT, ActionT]]: ...

    def dominance_key(self, state: StateT) -> Hashable: ...

    def resources(self, state: StateT) -> Sequence[int]: ...


@dataclass(frozen=True)
class Incumbent(Generic[StateT, ActionT]):
    state: StateT
    actions: tuple[ActionT, ...]


@dataclass(frozen=True)
class SearchStats:
    expanded: int
    generated: int
    pruned_by_bound: int
    pruned_by_dominance: int
    stale_queue_entries: int
    peak_queue: int


@dataclass(frozen=True)
class SearchResult(Generic[StateT, ActionT]):
    found: bool
    proven_optimal: bool
    completion_time: Optional[int]
    lower_bound_at_stop: Optional[float]
    optimality_gap: Optional[float]
    actions: tuple[ActionT, ...]
    goal_state: Optional[StateT]
    stop_reason: str
    stats: SearchStats


@dataclass(frozen=True)
class _Label(Generic[StateT]):
    elapsed: int
    resources: tuple[int, ...]
    state: StateT


def _resource_ge(left: Sequence[int], right: Sequence[int]) -> bool:
    return len(left) == len(right) and all(a >= b for a, b in zip(left, right))


def _reconstruct(
    parent: dict[StateT, tuple[Optional[StateT], Optional[ActionT]]],
    state: StateT,
) -> tuple[ActionT, ...]:
    rev: list[ActionT] = []
    cur = state
    while True:
        prev, action = parent[cur]
        if prev is None:
            break
        assert action is not None
        rev.append(action)
        cur = prev
    rev.reverse()
    return tuple(rev)


def astar_dp(
    problem: SearchProblem[StateT, ActionT],
    *,
    incumbent: Optional[Incumbent[StateT, ActionT]] = None,
    max_expansions: Optional[int] = None,
) -> SearchResult[StateT, ActionT]:
    """Run event-driven A* with Pareto-style dynamic-programming pruning.

    ``max_expansions=None`` asks for a proof.  A finite budget turns the same
    search into an anytime solver: it returns the best incumbent together with
    the smallest lower bound still alive, hence a measured optimality gap.
    """

    start = problem.initial_state()
    serial = count()
    queue: list[tuple[float, int, int, StateT]] = []
    parent: dict[StateT, tuple[Optional[StateT], Optional[ActionT]]] = {
        start: (None, None)
    }

    best_state: Optional[StateT] = None
    best_actions: tuple[ActionT, ...] = ()
    best_time = inf
    if incumbent is not None:
        if not problem.is_goal(incumbent.state):
            raise ValueError("incumbent state is not a goal")
        best_state = incumbent.state
        best_actions = incumbent.actions
        best_time = problem.elapsed(incumbent.state)

    # Each structural key owns a Pareto frontier of (time, monotone resources).
    frontiers: dict[Hashable, list[_Label[StateT]]] = {}
    active: set[StateT] = set()

    def insert_label(state: StateT) -> bool:
        key = problem.dominance_key(state)
        t = problem.elapsed(state)
        r = tuple(int(x) for x in problem.resources(state))
        labels = frontiers.setdefault(key, [])

        for label in labels:
            if label.elapsed <= t and _resource_ge(label.resources, r):
                return False

        kept: list[_Label[StateT]] = []
        for label in labels:
            if t <= label.elapsed and _resource_ge(r, label.resources):
                active.discard(label.state)
            else:
                kept.append(label)
        kept.append(_Label(t, r, state))
        frontiers[key] = kept
        active.add(state)
        return True

    start_lb = problem.lower_bound(start)
    if start_lb < best_time and insert_label(start):
        heappush(queue, (start_lb, problem.elapsed(start), next(serial), start))

    expanded = generated = 0
    pruned_bound = pruned_dom = stale = 0
    peak_queue = len(queue)
    stop_reason = "queue exhausted"
    lower_at_stop: Optional[float] = None

    while queue:
        lb, _, _, state = heappop(queue)
        if state not in active:
            stale += 1
            continue

        if lb >= best_time:
            # A feasible goal at ``best_time`` and no live state below it
            # pin both the global lower and upper bounds to the same value.
            lower_at_stop = float(best_time)
            stop_reason = "smallest live lower bound reached incumbent"
            break

        if problem.is_goal(state):
            t = problem.elapsed(state)
            if t < best_time:
                best_time = t
                best_state = state
                best_actions = _reconstruct(parent, state)
            continue

        if max_expansions is not None and expanded >= max_expansions:
            lower_at_stop = lb
            stop_reason = "expansion budget exhausted"
            # Put the state back conceptually: lb is the smallest unexpanded
            # live lower bound and therefore the correct certificate floor.
            break

        expanded += 1
        active.discard(state)

        for tr in problem.successors(state):
            generated += 1
            nxt = tr.state
            nxt_lb = problem.lower_bound(nxt)
            if nxt_lb >= best_time:
                pruned_bound += 1
                continue

            if problem.is_goal(nxt):
                t = problem.elapsed(nxt)
                if t < best_time:
                    parent[nxt] = (state, tr.action)
                    best_time = t
                    best_state = nxt
                    best_actions = _reconstruct(parent, nxt)
                continue

            if not insert_label(nxt):
                pruned_dom += 1
                continue
            parent[nxt] = (state, tr.action)
            heappush(queue, (nxt_lb, problem.elapsed(nxt), next(serial), nxt))
            peak_queue = max(peak_queue, len(queue))

    # If the loop drained naturally, there is no unexplored state below the
    # incumbent.  If there was no incumbent either, the model is infeasible.
    if not queue and lower_at_stop is None:
        lower_at_stop = float(best_time) if best_state is not None else None

    found = best_state is not None
    proven = found and stop_reason != "expansion budget exhausted"
    if found and lower_at_stop is not None:
        gap = max(0.0, float(best_time) - float(lower_at_stop))
    else:
        gap = None

    return SearchResult(
        found=found,
        proven_optimal=proven,
        completion_time=int(best_time) if found else None,
        lower_bound_at_stop=lower_at_stop,
        optimality_gap=gap,
        actions=best_actions,
        goal_state=best_state,
        stop_reason=stop_reason,
        stats=SearchStats(
            expanded=expanded,
            generated=generated,
            pruned_by_bound=pruned_bound,
            pruned_by_dominance=pruned_dom,
            stale_queue_entries=stale,
            peak_queue=peak_queue,
        ),
    )


def replay_actions(
    problem: SearchProblem[StateT, ActionT],
    actions: Sequence[ActionT],
) -> StateT:
    """Replay a returned sequence through the problem's own transition function.

    This is intentionally strict: each recorded action must identify exactly one
    successor.  It catches stale parent chains and action descriptions that are
    insufficient to reproduce a state transition.
    """
    state = problem.initial_state()
    for index, action in enumerate(actions):
        matches = [tr for tr in problem.successors(state) if tr.action == action]
        if len(matches) != 1:
            raise ValueError(
                f"action {index} has {len(matches)} matching successors: {action!r}"
            )
        state = matches[0].state
    return state
