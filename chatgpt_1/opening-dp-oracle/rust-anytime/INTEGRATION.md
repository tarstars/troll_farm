# Integration path: reduced Rust search to the real bot

The search engine is implemented and measured. The remaining work is not a
language port; it is replacing the reduced scheduling model with a compact,
referee-backed real-map model and demonstrating that the resulting search adds
value inside the platform limits.

This document is deliberately a gate sequence. A positive result at one gate
does not silently prove the next one.

## 1. Keep the fast rule controller as the incumbent

The online planner must never be the only way to obtain an action.

On turn 1:

1. build the deterministic Stage 2A opening immediately;
2. store it as the incumbent;
3. run bounded search only as an improver;
4. replace the incumbent whenever a better complete, replay-valid plan appears;
5. stop at the internal deadline and emit the incumbent's first command.

On later turns:

1. compare the live board with the expected state of the stored plan;
2. follow the plan without a full search when the state matches;
3. perform a small repair when a target tree, fruit count, planting cell or
   previous command outcome differs;
4. fall back to the deterministic dispatcher if repair does not finish.

A timeout is therefore a quality event, not a legality failure.

## 2. Real-map adapter, fixed roster first

The first adapter should solve only one exact second/third-troll roster with an
idle opponent. It should reuse the repository's maintained Rust referee types
and mechanics rather than introduce another independent copy.

The search state must include every fact that changes future transitions:

- current turn and bank;
- each own troll's talents, position, cargo and current macro-job;
- exact relevant tree position, type, size, health, fruits and cooldown;
- ownership of planted trees;
- intended planting cells;
- the current-turn TRAIN lock and shack occupancy.

Map geometry and all-pairs distances are immutable and should be shared by
state ID, never cloned into each node.

Each macro-action must expand to ordinary referee commands. Event-driven search
may jump between choices internally, but it may not skip the exact commands or
tree ticks used to reach the next event.

## 3. First evidence set: the known misses

Start with the 22 same-roster panel map-seats where the current randomized
greedy search is later than orchard 6. They are the cheapest falsifier of the
hypothesis that action-sequence search matters.

For every map-seat, record:

```text
map hash and seat
fixed target roster
orchard 6 training turn
current rollout solver turn
rule-controller incumbent turn
bounded Rust result at each budget
best offline result
smallest surviving lower bound
number of expanded/generated/retained states
peak resident memory
returned command sequence digest
independent exact-referee replay result
```

A selected schedule is evidence only after an independent replay through
`sim/engine.py` or the maintained Rust engine reproduces its TRAIN turn,
talents, inventories, units, tree state and score.

## 4. Budget-quality curve

Measure, do not project, at least these internal budgets:

```text
5, 10, 25, 50, 100, 250, 500, 700 ms, and offline
```

The platform allows 1,000 ms on turn 1 and 50 ms later, but the internal search
budget must be smaller. Input parsing, incumbent construction, command
selection and destruction of search storage all consume time. The reduced CI
run overshot 25/50/100 ms requests by roughly 5/5/13 ms. The candidate needs a
quiet-host p99 certificate with a safety margin before it can be called safe.

Suggested initial experimental settings, not a certificate:

- turn 1 search budget: 650-700 ms;
- turn 1 retained-state cap: 200,000-250,000 compact nodes;
- later repair budget: no more than 20-25 ms;
- later repair frontier: a few thousand nodes, or a fixed-width beam;
- deterministic fallback selected before either deadline starts.

## 5. Memory representation for submission

The generic crate is readable laboratory code. The submitted form should be a
domain-specific implementation:

- immutable geometry and tree identities in one shared table;
- packed scalar state fields and small integer indices;
- a preallocated node arena;
- parent node ID plus compact action, not a cloned action vector per A* node;
- a binary heap of node IDs;
- hash-table entries keyed by a packed structural fingerprint;
- fixed-capacity Pareto labels where measurements justify the cap;
- no duplicated simulator, strings, heap-owned tree types or generic trait
  machinery in the compacted submission.

The crate's current state cap is a retained-node count, not a byte guarantee.
The real adapter must report both node count and peak resident memory.

## 6. From fixed roster to the roster frontier

After the fixed-roster adapter passes:

1. run one minimum-turn search for each selected full roster, or put roster
   choice into the state;
2. preserve non-dominated completion states rather than selecting one chop
   number early;
3. rank completion states with the turn-300 continuation value accepted in the
   Stage 2 design review;
4. add full tuples such as `(2,3,1,2)` and `(2,4,1,c)`, not only
   `(2,3,0,c)`.

Minimum training turn is exact only within one full roster. Comparing different
rosters is a continuation-value problem.

## 7. Opponent handling

Do not start with minimax. The opponent cannot block our path or consume a
finite iron stock. It can change tree availability and occupy a planned plant
cell with a tree.

Run the same planner against:

- an idle opponent;
- a mirrored strong opening;
- recorded openings of the top bots on the same maps.

Report the added delay, number of repairs, failed/short harvests and completion
turn distribution. Replanning from live state is the default response to
contestation.

## 8. Go/no-go conditions for embedding

Embed the planner in a candidate only when all of these are true:

- every returned real-map sequence passes independent exact-referee replay;
- the bounded search improves the deterministic incumbent on enough of the
  known-miss cases to justify its source and runtime cost;
- turn-1 p99, including setup and cleanup, stays below its safety budget;
- later-turn validation/repair p99 stays below its safety budget;
- peak memory is bounded under the largest observed frontier;
- the compacted candidate remains below the source-size limit;
- turning the planner off produces byte-identical parent commands;
- invalidated plans always fall back to a legal deterministic action.

If the oracle finds better sequences only after hundreds of thousands of
real-map states, retain it offline and distil its recurring decisions into
rules. Offline value is still useful even when the search itself does not ship.

## Current status

Implemented now:

- generic bounded A*/DP;
- safe greedy incumbent;
- deadline, expansion and node-count budgets;
- bounded beam fallback;
- strict replay;
- compact reduced model;
- tests and release/runtime measurements.

Not implemented in this change:

- real-map state adapter;
- exact command compiler against the maintained engine;
- the 22-map comparison;
- integration into the champion or Stage 2A candidate;
- source-size, real-map timing, field, ladder or Arena gates.

Keeping this boundary explicit prevents the reduced-model speed result from
being mistaken for a deployable bot result.
