# Opening DP oracle — design note

## Decision

The existing opening solver is a useful candidate generator, but its result must be called **the best sequence found by its policy family**, not an optimum. It enumerates a fixed menu of second-troll talents, seed programmes, reserve rules and scoring knobs, evaluates them with a greedy dispatcher, then randomises only the best few plans. More rollouts explore that dispatcher more thoroughly; they do not recover a sequence the dispatcher cannot express.

The replacement proposed here is a hybrid:

1. run a cheap greedy or Monte-Carlo policy to obtain a feasible completion turn;
2. use that turn as an upper bound for an event-driven A* search;
3. memoise structurally equivalent states and retain only their non-dominated resource labels;
4. either exhaust every state that could beat the incumbent, obtaining an optimality certificate, or stop at a compute budget and report the surviving lower bound and the measured gap.

This prototype implements that machinery. It deliberately starts with a finite reduced opening model. It does **not** claim that the toy model is the referee.

## Why ordinary turn-by-turn dynamic programming is the wrong representation

A full opening state contains the turn, six banked resources, every troll's position, talents and cargo, every tree's size, health, fruits and cooldown, and simultaneous commands. Indexing a table by all of these dimensions would be larger than the reachable state graph and would spend most work on impossible combinations.

The opening nevertheless has a useful event structure. Most turns are deterministic walking, harvesting or mining inside a chosen job. Choices happen when:

- a worker becomes free;
- a delivery reaches the shack;
- a planted crop becomes ready;
- a training bill becomes affordable;
- a live target changes and invalidates a job.

The search should therefore branch on **macro-actions** and jump to the next event. The eventual referee adapter must still emit and replay every skipped command; event-driven means fewer branch points, not approximate game mechanics.

## Search state in the prototype

The reduced immutable state stores:

- current turn;
- four banked training resources: plum, lemon, apple and iron;
- every worker's talents, completion time of its current job, pending delivery and shack occupancy;
- finite wild sources and infinite iron sources;
- planted sources with their ready turn;
- how many times each bounded planting option has been used;
- whether TRAIN has already been used on the current turn.

The real adapter will need to replace the source abstraction with the exact live tree and map state. The generic A*/DP engine does not need to change.

## Transitions

The reduced model implements these event-level transitions:

- `FETCH resource amount from source`: reserve a finite source amount, make the worker busy for exact reduced-model travel/service/drop time, then deposit at the completion event;
- `PLANT`: spend one banked seed, schedule a future crop, and make the worker busy for pick/travel/plant/return time;
- `LEAVE`: move a newly spawned worker off the shack so a same-turn TRAIN can become legal;
- `TRAIN`: spend the real `n + talent^2` bill, add the new worker, and lock further training for that turn;
- `ADVANCE`: jump to the next delivery or crop-ready event and apply all simultaneous completions.

Workers are asynchronous. This is essential: independent per-worker greedy assignment can waste the only worker able to mine while another worker that could have harvested sits idle.

## A* bound

For the next training stage, the heuristic:

1. treats all pending deliveries and already scheduled crops as available immediately;
2. ignores source contention, travel start-up and crop growth;
3. lets every worker collect its best resource at its best service rate forever;
4. takes the maximum relaxed time over the resource deficits;
5. chooses the cheapest lower bound over the allowed next-troll specifications;
6. ignores all later training stages.

Every relaxation can only make completion earlier, so the result is an admissible lower bound. It is intentionally weak. A production oracle should add stronger admissible bounds, for example a relaxed worker-to-resource assignment and minimum shack-release time.

## Dynamic-programming dominance

States are grouped by a structural key containing the roster, pending jobs, source stock, future crop timing and current-turn training lock. Absolute event times are normalised relative to the current turn.

Within one such key, state A dominates state B when:

- A is no later than B; and
- A has at least as much of every banked resource.

B can then be discarded: it has the same future choices, starts no earlier and owns no useful advantage. The implementation removes labels dominated by a newly discovered state and ignores stale queued labels.

This rule is safe only for resources that are monotone under an equal structural key. The real adapter must not hide tree ownership, cargo, position, cooldown or an opponent-dependent fact inside the resource vector; those belong in the structural key.

## What the certificate means

Let `U` be the best feasible completion turn and `L` the smallest admissible lower bound remaining in the queue.

- If the queue is exhausted or `L >= U`, the sequence is optimal **inside the implemented model and action vocabulary**.
- If the expansion budget ends first, the solver reports `[L, U]`; the unknown optimum is inside that interval.
- A referee-level claim additionally requires replay of the chosen command sequence through `sim/engine.py`, and exact search needs an action vocabulary proven not to exclude a better legal sequence.

This distinction prevents “best rollout found” from silently becoming “optimal”.

## Reproducible examples

Two small deterministic cases are included as regression tests.

### Global worker assignment

The greedy policy sends a versatile worker to a nearby lemon source and leaves the harvest-only worker unable to help with iron. It trains at turn 9. A*/DP reserves the versatile worker for iron, gives lemons to the other worker and proves turn 6 optimal.

### Plant now or walk far

The greedy policy walks to a distant lemon source and trains at turn 13. A*/DP spends a lemon as a nearby seed, waits for the crop, harvests it and proves turn 10 optimal.

These examples are not game-strength evidence. They prove that the implementation can represent the two failure modes motivating it: joint allocation and delayed investment.

## Path to the real opening oracle

The safest integration order is:

1. **Fixed roster, idle opponent.** Adapt one real panel map and one exact target roster. Macro-actions must compile to command lists and every successor must be replayed through the existing fast world; every final sequence is independently replayed through `sim/engine.py`.
2. **Compare on the known misses.** Start with the 22 same-roster map-seats where the current rollout solver is later than orchard 6. Report current result, oracle result, lower bound and expansions. This quickly tests whether the greedy action vocabulary is the real limitation.
3. **Inventory and tree caps only by dominance proof.** Never clip resources merely because they exceed the immediate bill: a seed, a different roster or continuation value may make the excess useful.
4. **Full roster frontier.** Run one minimum-turn search per complete second/third-troll roster or carry the roster choice in state. Preserve non-dominated completion states; select among them only with the turn-300 continuation value.
5. **Online bounded search.** Use the same queue with a first-turn expansion/time budget. Return the best feasible sequence plus its lower-bound gap. Later turns validate tree existence, fruit count and plant cells, then repair from the live state.
6. **Opponent scenarios, not minimax first.** Re-run against recorded strong openings and mirrored openings. An opponent changes trees and intended plant cells; it does not block routes or deplete iron. Full adversarial minimax is unnecessary until scenario replanning is shown inadequate.

## Relationship to Stage 2A

This branch does not alter Claude's active rules-first controller. Stage 2A remains the fast field test of the two large measured defects: delayed second-troll training and one-item trips. The oracle is an independent instrument for Stage 2B. It should be used to quantify how many turns those rules leave on the table, not to delay their measurement.
