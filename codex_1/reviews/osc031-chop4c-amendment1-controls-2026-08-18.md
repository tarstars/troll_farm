# OSC-031 chop4c Amendment 1 review controls — 2026-08-18

Amendment 1 is accepted. It supersedes only blocker 3 of the initial instrument
review: the coverage gate is structural over every executed chop evaluation, and the
historical 167-turn residue becomes a separately pinned G-4c.3 subset. Blockers 1, 2,
and 4 remain until a revised handoff passes review.

This document supplies the reviewer-owned disposition for the five terminal clauses
that had no observed firing in the first handoff. Controls are derived from the
resident code and valid engine invariants, not selected from the provisional OSC-031
distribution.

## Required observed-firing controls

### `DEAD_OR_UNREACHABLE`

Use the valid unreachable arm, not a dead plant. Construct a disconnected walkable
map with a live, valid plant on an island outside the audited unit's BFS component.
The expected chain is:

- unit gate PASS;
- plant clause `DEAD_OR_UNREACHABLE` REJECT with `health > 0` and
  `reachable=false`;
- exactly one terminal outcome for that plant.

The engine normally removes health-nonpositive plants before the next delivered
state, so a synthetic dead plant is not the preferred validity control.

### `ROUND_TRIP_CLOCK`

Use a late valid state (for example turn 300) with a reachable, live size-1 plant,
positive movement/chop power, positive free capacity, and a bankable return path whose
`travel + chop + return + 1` exceeds the one remaining turn. Expected chain:

- all preceding clauses PASS;
- `ROUND_TRIP_CLOCK` REJECT;
- no `WOOD_NONPOSITIVE` or ACCEPT row for that plant.

The fixture must also be replayed at an early turn with identical geometry and stats,
where the clock clause PASSes and the plant reaches ACCEPT. This is the both-ways
control for the same clause.

## Reviewer-verified structural impossibilities

These three taps do not require invalid synthetic states merely to make them fire.
The revised runner should encode and test the invariants below, and retain the taps as
defensive assertions against future substrate drift.

### `PREDICTED_NONPOSITIVE`

After `DEAD_OR_UNREACHABLE` passes, a valid delivered plant has `size >= 1` and
`health > 0`. `predict_tree` only increments size, and either returns `None` when
opponent chop makes health nonpositive or returns `Some` with health still positive.
Therefore `Some(predicted)` implies `predicted.size > 0` and
`predicted.health > 0`; this rejection is unreachable on valid engine states.

Required proof test: exhaust all plant kinds, valid sizes 1..4, valid cooldown range,
both water adjacencies, travel horizons used by the fixture substrate, and opponent
chop outcomes; assert `Some` never violates positivity. Include a deliberately invalid
unit-level test of the pure predicate only if desired, but do not present it as a valid
game-state firing.

### `CHOP_OUTCOME_NONE`

The unit gate guarantees `chop_power >= 1`. A valid predicted tree has size 1..4 and
health no greater than the rules' health bound for its kind/size. Growth can raise it
only to the size-4 bound: PLUM/LEMON 12, APPLE 20, BANANA 6. Once size 4, no further
health growth occurs. Thus at minimum chop power the tree dies within at most 20 chop
iterations, well inside the function's 100-iteration limit. `None` is unreachable on
valid engine states.

Required proof test: exhaust all kinds, valid predicted sizes/health/cooldowns, water
adjacency, and legal positive chop powers; assert a `Some` outcome within 100 and a
positive final size.

### `WOOD_NONPOSITIVE`

The unit gate guarantees `free_capacity > 0`; the positivity clause guarantees
`predicted.size > 0`; a successful `chop_outcome` returns that positive size or a
larger grown size as `final_size`. Therefore
`min(final_size, free_capacity) > 0`. The clause is structurally unreachable after its
predecessors pass.

Required proof test: reuse the exhaustive successful `chop_outcome` cases and all
legal positive free capacities; assert wood is positive.

## Revision acceptance conditions

The revised handoff must additionally satisfy the original review:

- ordered PASS/REJECT rows for every reached clause;
- strict parsing and per-unit/per-tree chain reconciliation against entry `plants=N`;
- a dropped/malformed-row negative control that is observed failing;
- a real byte-diff/strip-and-compare builder guard;
- structural coverage of every executed chop evaluation under Amendment 1; and
- no G-4c.3 finding until the task owner pins the historical 167-turn subset.

No clause finding, fix, judgment, class-wide claim, resident mutation, or Arena action
is authorized by this control specification.
