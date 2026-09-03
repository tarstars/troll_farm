"""A finite event-driven Troll Farm opening model for the DP/A* oracle.

This is deliberately smaller than the referee.  It keeps the economic choices
that make the opening a scheduling problem:

* training bills use the real ``n + talent^2`` formula;
* workers have movement, carry, harvest and chop talents;
* wild sources are finite and iron may be infinite;
* workers execute asynchronous round trips, so two workers can collect in
  parallel;
* planting consumes a banked seed now and creates a future finite crop;
* a newly trained troll occupies the shack until assigned a job;
* only one TRAIN may happen in a turn.

The model is not presented as referee-exact.  Its purpose is to exercise and
validate the search machinery before a real-state adapter is attached.  Every
state is immutable and all transitions jump directly to the next decision or
completion event; walking turns are not branched individually.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import ceil, inf
from typing import Iterable, Sequence

from oracle import SearchProblem, Transition

PLUM, LEMON, APPLE, IRON = range(4)
RESOURCE_NAMES = ("PLUM", "LEMON", "APPLE", "IRON")


@dataclass(frozen=True, order=True)
class WorkerSpec:
    name: str
    movement: int
    capacity: int
    harvest: int
    chop: int

    def __post_init__(self) -> None:
        if min(self.movement, self.capacity) < 1:
            raise ValueError("movement and capacity must be positive")
        if min(self.harvest, self.chop) < 0:
            raise ValueError("harvest and chop must be non-negative")


@dataclass(frozen=True, order=True)
class WorkerState:
    spec: WorkerSpec
    free_at: int
    delivery_resource: int = -1
    delivery_amount: int = 0
    at_shack: bool = False

    def idle_at(self, now: int) -> bool:
        return self.free_at <= now and self.delivery_resource < 0


@dataclass(frozen=True, order=True)
class SourceState:
    label: str
    resource: int
    distance: int
    stock: int
    ready_at: int = -1
    crop_amount: int = 0
    infinite: bool = False

    def active_at(self, now: int) -> bool:
        return self.ready_at < 0 or self.ready_at <= now


@dataclass(frozen=True, order=True)
class PlantOption:
    label: str
    seed_resource: int
    distance: int
    growth_delay: int
    crop_amount: int = 3
    max_count: int = 1


@dataclass(frozen=True)
class OpeningState:
    now: int
    bank: tuple[int, int, int, int]
    workers: tuple[WorkerState, ...]
    sources: tuple[SourceState, ...]
    plants_used: tuple[int, ...]
    last_train_turn: int = -1


@dataclass(frozen=True)
class OpeningAction:
    kind: str
    worker: int | None = None
    label: str = ""
    resource: int = -1
    amount: int = 0
    duration: int = 0
    talents: WorkerSpec | None = None
    source: str = ""

    def __str__(self) -> str:
        if self.kind == "TRAIN":
            assert self.talents is not None
            return f"t={self.label}: TRAIN {self.talents.name}"
        if self.kind == "FETCH":
            return (
                f"t={self.label}: worker {self.worker} fetches {self.amount} "
                f"{RESOURCE_NAMES[self.resource]} from {self.source or '?'} "
                f"({self.duration} turns)"
            )
        if self.kind == "PLANT":
            return (
                f"t={self.label}: worker {self.worker} plants "
                f"{RESOURCE_NAMES[self.resource]} ({self.duration} turns away from work)"
            )
        if self.kind == "LEAVE":
            return f"t={self.label}: worker {self.worker} leaves the shack"
        if self.kind == "ADVANCE":
            return f"advance to turn {self.label}"
        return f"{self.kind} {self.label}"


@dataclass(frozen=True)
class OpeningProblem(SearchProblem[OpeningState, OpeningAction]):
    initial_bank_value: tuple[int, int, int, int]
    initial_workers_value: tuple[WorkerSpec, ...]
    initial_sources_value: tuple[SourceState, ...]
    training_stages: tuple[tuple[WorkerSpec, ...], ...]
    plant_options: tuple[PlantOption, ...] = ()
    start_turn: int = 1
    max_turn: int = 120

    def __post_init__(self) -> None:
        if len(self.initial_bank_value) != 4:
            raise ValueError("bank must have four resource counts")
        if not self.initial_workers_value:
            raise ValueError("at least one initial worker is required")
        if any(not stage for stage in self.training_stages):
            raise ValueError("every training stage needs at least one option")
        if self.max_turn < self.start_turn:
            raise ValueError("max_turn precedes start_turn")

    @property
    def initial_count(self) -> int:
        return len(self.initial_workers_value)

    @property
    def goal_count(self) -> int:
        return self.initial_count + len(self.training_stages)

    def initial_state(self) -> OpeningState:
        workers = tuple(
            WorkerState(
                spec=w,
                free_at=self.start_turn,
                at_shack=True,
            )
            for w in self.initial_workers_value
        )
        return OpeningState(
            now=self.start_turn,
            bank=self.initial_bank_value,
            workers=workers,
            sources=tuple(sorted(self.initial_sources_value)),
            plants_used=(0,) * len(self.plant_options),
        )

    def is_goal(self, state: OpeningState) -> bool:
        return len(state.workers) >= self.goal_count

    def elapsed(self, state: OpeningState) -> int:
        return state.now

    def current_stage(self, state: OpeningState) -> int:
        return len(state.workers) - self.initial_count

    @staticmethod
    def training_cost(n_existing: int, spec: WorkerSpec) -> tuple[int, int, int, int]:
        return (
            n_existing + spec.movement * spec.movement,
            n_existing + spec.capacity * spec.capacity,
            n_existing + spec.harvest * spec.harvest,
            n_existing + spec.chop * spec.chop,
        )

    def _affordable(self, state: OpeningState, spec: WorkerSpec) -> bool:
        cost = self.training_cost(len(state.workers), spec)
        return all(have >= need for have, need in zip(state.bank, cost))

    def _future_resource_cap(self, state: OpeningState) -> tuple[int, int, int, int]:
        """A finite cap that preserves every future bill and allowed planting seed."""
        stage = self.current_stage(state)
        cap = [0, 0, 0, 0]
        for offset, options in enumerate(self.training_stages[stage:], start=stage):
            n = self.initial_count + offset
            for r in range(4):
                cap[r] += max(self.training_cost(n, spec)[r] for spec in options)
        for i, option in enumerate(self.plant_options):
            cap[option.seed_resource] += option.max_count - state.plants_used[i]
        return tuple(cap)  # type: ignore[return-value]

    @staticmethod
    def _pending_resources(state: OpeningState) -> tuple[int, int, int, int]:
        out = [0, 0, 0, 0]
        for worker in state.workers:
            if worker.delivery_resource >= 0:
                out[worker.delivery_resource] += worker.delivery_amount
        return tuple(out)  # type: ignore[return-value]

    def lower_bound(self, state: OpeningState) -> float:
        """Optimistic absolute completion turn.

        The relaxation gives every pending delivery and every already scheduled
        crop immediately, ignores source contention and start-up travel, and lets
        all workers collect their best resource in parallel forever.  It is weak
        but admissible.
        """
        if self.is_goal(state):
            return float(state.now)
        if state.now > self.max_turn:
            return inf

        stage = self.current_stage(state)
        options = self.training_stages[stage]
        pending = self._pending_resources(state)
        optimistic_bank = [state.bank[r] + pending[r] for r in range(4)]
        for source in state.sources:
            if source.ready_at > state.now:
                optimistic_bank[source.resource] += source.crop_amount

        best = inf
        for spec in options:
            bill = self.training_cost(len(state.workers), spec)
            deficits = [max(0, bill[r] - optimistic_bank[r]) for r in range(4)]
            resource_times: list[int] = []
            feasible = True
            for resource, deficit in enumerate(deficits):
                if deficit == 0:
                    resource_times.append(0)
                    continue
                total_rate = 0.0
                possible = False
                for worker in state.workers:
                    rate = self._best_relaxed_rate(worker.spec, resource, state.sources)
                    if rate > 0:
                        possible = True
                        total_rate += rate
                if not possible:
                    # A permitted plant is also a path to the resource.  Ignore
                    # its seed and growth time in the relaxation.
                    if any(p.seed_resource == resource for p in self.plant_options):
                        total_rate = float(sum(max(w.spec.harvest, 1) for w in state.workers))
                        possible = True
                if not possible or total_rate <= 0:
                    feasible = False
                    break
                resource_times.append(ceil(deficit / total_rate))
            if feasible:
                best = min(best, state.now + max(resource_times, default=0))
        return float(best)

    @staticmethod
    def _best_relaxed_rate(
        worker: WorkerSpec,
        resource: int,
        sources: Sequence[SourceState],
    ) -> float:
        service = worker.chop if resource == IRON else worker.harvest
        if service <= 0:
            return 0.0
        best = 0.0
        for source in sources:
            if source.resource != resource:
                continue
            amount = worker.capacity if source.infinite else min(
                worker.capacity, max(source.stock, source.crop_amount)
            )
            if amount <= 0:
                continue
            # Dropping travel and readiness makes this an optimistic steady rate.
            best = max(best, min(worker.capacity, service, amount))
        return best

    def dominance_key(self, state: OpeningState):
        """Normalise absolute event times relative to ``now``.

        Equal keys have identical future choices.  Among them an earlier state
        with at least as much bank dominates a later poorer state.
        """
        workers = tuple(
            (
                w.spec,
                max(0, w.free_at - state.now),
                w.delivery_resource,
                w.delivery_amount,
                w.at_shack,
            )
            for w in state.workers
        )
        sources = tuple(
            (
                s.label,
                s.resource,
                s.distance,
                s.stock,
                -1 if s.ready_at < 0 else max(0, s.ready_at - state.now),
                s.crop_amount,
                s.infinite,
            )
            for s in state.sources
        )
        train_locked = state.last_train_turn == state.now
        return workers, sources, state.plants_used, train_locked

    def resources(self, state: OpeningState) -> Sequence[int]:
        return state.bank

    def successors(self, state: OpeningState) -> Iterable[Transition[OpeningState, OpeningAction]]:
        if self.is_goal(state) or state.now > self.max_turn:
            return ()

        out: list[Transition[OpeningState, OpeningAction]] = []
        stage = self.current_stage(state)

        # TRAIN is a shack command.  Only one can happen in a turn, and a troll
        # left on the shack blocks it.  Assigning that troll any job changes
        # ``at_shack`` immediately, modelling MOVE and TRAIN on the same turn.
        if stage < len(self.training_stages) and state.last_train_turn != state.now:
            if not any(w.at_shack for w in state.workers):
                for spec in self.training_stages[stage]:
                    if not self._affordable(state, spec):
                        continue
                    cost = self.training_cost(len(state.workers), spec)
                    bank = tuple(state.bank[r] - cost[r] for r in range(4))
                    worker = WorkerState(
                        spec=spec,
                        free_at=state.now + 1,
                        at_shack=True,
                    )
                    nxt = replace(
                        state,
                        bank=bank,  # type: ignore[arg-type]
                        workers=state.workers + (worker,),
                        last_train_turn=state.now,
                    )
                    out.append(
                        Transition(
                            OpeningAction(
                                kind="TRAIN",
                                label=str(state.now),
                                talents=spec,
                            ),
                            nxt,
                        )
                    )

        idle = [i for i, worker in enumerate(state.workers) if worker.idle_at(state.now)]
        if idle:
            # Canonical assignment order removes permutations of assigning the
            # same set of jobs to simultaneously idle workers.
            worker_index = idle[0]
            worker = state.workers[worker_index]
            out.extend(self._assignment_successors(state, worker_index, worker))

        # Waiting is meaningful only when an already scheduled event exists.
        advanced = self._advance_to_next_event(state)
        if advanced is not None:
            out.append(
                Transition(
                    OpeningAction(kind="ADVANCE", label=str(advanced.now)),
                    advanced,
                )
            )
        return tuple(out)

    def _assignment_successors(
        self,
        state: OpeningState,
        worker_index: int,
        worker: WorkerState,
    ) -> list[Transition[OpeningState, OpeningAction]]:
        out: list[Transition[OpeningState, OpeningAction]] = []
        caps = self._future_resource_cap(state)
        pending = self._pending_resources(state)

        if worker.at_shack:
            workers = list(state.workers)
            workers[worker_index] = replace(
                worker,
                free_at=state.now + 1,
                at_shack=False,
            )
            out.append(
                Transition(
                    OpeningAction(
                        kind="LEAVE",
                        worker=worker_index,
                        label=str(state.now),
                        duration=1,
                    ),
                    replace(state, workers=tuple(workers)),
                )
            )

        for source_index, source in enumerate(state.sources):
            if not source.active_at(state.now):
                continue
            if not source.infinite and source.stock <= 0:
                continue
            resource = source.resource
            useful = caps[resource] - state.bank[resource] - pending[resource]
            if useful <= 0:
                continue
            service = worker.spec.chop if resource == IRON else worker.spec.harvest
            if service <= 0:
                continue
            max_take = min(worker.spec.capacity, useful)
            if not source.infinite:
                max_take = min(max_take, source.stock)
            if max_take <= 0:
                continue

            # Keep all quantities where service duration changes, plus the
            # largest quantity.  Quantities with identical duration and less
            # delivery are strictly dominated.
            quantities: list[int] = []
            previous_service_turns = -1
            for amount in range(1, max_take + 1):
                service_turns = ceil(amount / service)
                if service_turns != previous_service_turns or amount == max_take:
                    quantities.append(amount)
                previous_service_turns = service_turns

            for amount in sorted(set(quantities)):
                travel = ceil(source.distance / worker.spec.movement)
                duration = travel + ceil(amount / service) + travel + 1
                workers = list(state.workers)
                workers[worker_index] = WorkerState(
                    spec=worker.spec,
                    free_at=state.now + duration,
                    delivery_resource=resource,
                    delivery_amount=amount,
                    at_shack=False,
                )
                sources = list(state.sources)
                if not source.infinite:
                    sources[source_index] = replace(source, stock=source.stock - amount)
                action = OpeningAction(
                    kind="FETCH",
                    worker=worker_index,
                    label=str(state.now),
                    resource=resource,
                    amount=amount,
                    duration=duration,
                    source=source.label,
                )
                out.append(
                    Transition(
                        action,
                        replace(
                            state,
                            workers=tuple(workers),
                            sources=tuple(sources),
                        ),
                    )
                )

        for option_index, option in enumerate(self.plant_options):
            used = state.plants_used[option_index]
            if used >= option.max_count:
                continue
            resource = option.seed_resource
            if state.bank[resource] <= 0:
                continue
            travel = ceil(option.distance / worker.spec.movement)
            worker_duration = 1 + travel + 1 + travel  # PICK, out, PLANT, return
            ready_at = state.now + 1 + travel + 1 + option.growth_delay
            bank = list(state.bank)
            bank[resource] -= 1
            workers = list(state.workers)
            workers[worker_index] = WorkerState(
                spec=worker.spec,
                free_at=state.now + worker_duration,
                at_shack=False,
            )
            plants_used = list(state.plants_used)
            plants_used[option_index] += 1
            source = SourceState(
                label=f"{option.label}#{used + 1}",
                resource=resource,
                distance=option.distance,
                stock=0,
                ready_at=ready_at,
                crop_amount=option.crop_amount,
            )
            out.append(
                Transition(
                    OpeningAction(
                        kind="PLANT",
                        worker=worker_index,
                        label=str(state.now),
                        resource=resource,
                        amount=1,
                        duration=worker_duration,
                    ),
                    replace(
                        state,
                        bank=tuple(bank),  # type: ignore[arg-type]
                        workers=tuple(workers),
                        sources=tuple(sorted(state.sources + (source,))),
                        plants_used=tuple(plants_used),
                    ),
                )
            )
        return out

    def _advance_to_next_event(self, state: OpeningState) -> OpeningState | None:
        times = [w.free_at for w in state.workers if w.free_at > state.now]
        times.extend(s.ready_at for s in state.sources if s.ready_at > state.now)
        if not times:
            return None
        next_time = min(times)
        if next_time > self.max_turn:
            return None

        bank = list(state.bank)
        workers: list[WorkerState] = []
        for worker in state.workers:
            if worker.free_at <= next_time and worker.delivery_resource >= 0:
                bank[worker.delivery_resource] += worker.delivery_amount
                workers.append(
                    WorkerState(
                        spec=worker.spec,
                        free_at=next_time,
                        at_shack=False,
                    )
                )
            else:
                workers.append(worker)

        sources: list[SourceState] = []
        for source in state.sources:
            if source.ready_at >= 0 and source.ready_at <= next_time:
                sources.append(
                    replace(
                        source,
                        stock=source.stock + source.crop_amount,
                        ready_at=-1,
                    )
                )
            else:
                sources.append(source)

        return replace(
            state,
            now=next_time,
            bank=tuple(bank),  # type: ignore[arg-type]
            workers=tuple(workers),
            sources=tuple(sources),
        )


def current_deficit(problem: OpeningProblem, state: OpeningState) -> tuple[int, int, int, int]:
    """Deficit of the cheapest currently available training option."""
    if problem.is_goal(state):
        return (0, 0, 0, 0)
    stage = problem.current_stage(state)
    bills = [
        problem.training_cost(len(state.workers), spec)
        for spec in problem.training_stages[stage]
    ]
    bill = min(
        bills,
        key=lambda b: sum(max(0, b[r] - state.bank[r]) for r in range(4)),
    )
    return tuple(max(0, bill[r] - state.bank[r]) for r in range(4))  # type: ignore[return-value]


def greedy_incumbent(problem: OpeningProblem, max_steps: int = 10_000):
    """Fast trial-and-error baseline used only as an A* upper bound.

    It always takes an available TRAIN; otherwise it assigns the first idle
    worker the fetch with the largest currently-needed delivery per turn.  It
    never plants unless no fetch helps.  The routine is intentionally simple:
    the exact search is expected to equal or beat it.
    """
    from oracle import Incumbent

    state = problem.initial_state()
    actions: list[OpeningAction] = []
    for _ in range(max_steps):
        if problem.is_goal(state):
            return Incumbent(state=state, actions=tuple(actions))
        successors = list(problem.successors(state))
        if not successors:
            return None

        trains = [tr for tr in successors if tr.action.kind == "TRAIN"]
        if trains:
            # Prefer the strongest affordable option.  This is a deliberately
            # local choice and can be worse for the next bill.
            chosen = max(
                trains,
                key=lambda tr: sum(
                    (
                        tr.action.talents.movement,
                        tr.action.talents.capacity,
                        tr.action.talents.harvest,
                        tr.action.talents.chop,
                    )
                )
                if tr.action.talents
                else 0,
            )
        else:
            deficit = current_deficit(problem, state)
            fetches = [tr for tr in successors if tr.action.kind == "FETCH"]
            helpful = [tr for tr in fetches if deficit[tr.action.resource] > 0]
            if helpful:
                chosen = max(
                    helpful,
                    key=lambda tr: (
                        min(tr.action.amount, deficit[tr.action.resource])
                        / max(tr.action.duration, 1),
                        tr.action.amount,
                    ),
                )
            else:
                leaves = [tr for tr in successors if tr.action.kind == "LEAVE"]
                advances = [tr for tr in successors if tr.action.kind == "ADVANCE"]
                plants = [tr for tr in successors if tr.action.kind == "PLANT"]
                chosen = (leaves or advances or plants)[0]
        actions.append(chosen.action)
        state = chosen.state
    return None


def hybrid_solve(problem: OpeningProblem, *, max_expansions: int | None = None):
    """Greedy trial first, then exact/anytime A* using it as the upper bound."""
    from oracle import astar_dp

    incumbent = greedy_incumbent(problem)
    return astar_dp(problem, incumbent=incumbent, max_expansions=max_expansions)


def global_assignment_problem() -> OpeningProblem:
    """Small case where independent greedy assignment is three turns late.

    The versatile worker can mine or harvest.  The second worker can only
    harvest.  A local greedy policy sends the versatile worker to the nearby
    lemon source and then has nobody able to mine in parallel.  The exact
    search reserves the versatile worker for iron and finishes at turn 6.
    """
    versatile = WorkerSpec("versatile", movement=2, capacity=2, harvest=2, chop=2)
    harvester = WorkerSpec("harvester", movement=1, capacity=2, harvest=1, chop=0)
    target = WorkerSpec("target", movement=1, capacity=1, harvest=0, chop=1)
    return OpeningProblem(
        initial_bank_value=(3, 1, 2, 1),
        initial_workers_value=(versatile, harvester),
        initial_sources_value=(
            SourceState("a-lemon", LEMON, distance=1, stock=2),
            SourceState("b-iron", IRON, distance=2, stock=0, infinite=True),
        ),
        training_stages=((target,),),
        max_turn=20,
    )


def plant_investment_problem() -> OpeningProblem:
    """Small case where spending a seed now beats a long wild-tree trip."""
    starter = WorkerSpec("starter", movement=1, capacity=3, harvest=3, chop=1)
    target = WorkerSpec("target", movement=1, capacity=1, harvest=0, chop=0)
    return OpeningProblem(
        initial_bank_value=(2, 1, 1, 1),
        initial_workers_value=(starter,),
        initial_sources_value=(
            SourceState("far-lemon", LEMON, distance=5, stock=3),
        ),
        training_stages=((target,),),
        plant_options=(
            PlantOption(
                "near-lemon",
                seed_resource=LEMON,
                distance=1,
                growth_delay=2,
                crop_amount=3,
                max_count=1,
            ),
        ),
        max_turn=20,
    )


def two_stage_problem() -> OpeningProblem:
    """A larger optional benchmark with a second-troll choice and planting."""
    starter = WorkerSpec("starter", movement=1, capacity=2, harvest=1, chop=1)
    cheap_gatherer = WorkerSpec(
        "cheap-gatherer", movement=1, capacity=3, harvest=2, chop=1
    )
    fast_expensive = WorkerSpec(
        "fast-expensive", movement=2, capacity=2, harvest=1, chop=2
    )
    target = WorkerSpec("target-chop2", movement=2, capacity=2, harvest=1, chop=2)
    return OpeningProblem(
        initial_bank_value=(8, 8, 5, 7),
        initial_workers_value=(starter,),
        initial_sources_value=(
            SourceState("near-plum", PLUM, distance=1, stock=6),
            SourceState("far-lemon", LEMON, distance=4, stock=7),
            SourceState("near-apple", APPLE, distance=2, stock=4),
            SourceState("iron", IRON, distance=2, stock=0, infinite=True),
        ),
        training_stages=(
            (cheap_gatherer, fast_expensive),
            (target,),
        ),
        plant_options=(
            PlantOption(
                "near-lemon-crop",
                seed_resource=LEMON,
                distance=1,
                growth_delay=4,
                crop_amount=3,
                max_count=1,
            ),
        ),
        max_turn=60,
    )
