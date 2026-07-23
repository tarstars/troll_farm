# D65i planted-source survival audit protocol (2026-07-21)

## Question

Why do both seats of seed 9,830,002 remain at one worker after D65a validly plants the uncovered
PLUM and LEMON sources, while both seats of seed 9,830,014 capitalize after one PLUM source?

This is a consumed mechanism audit. It cannot change D65 behavior, select a source count, placement,
timing, or species order, open fresh seeds, construct a candidate, or authorize platform action.

## Frozen cohort and controller

Replay `seed_source_repair` exactly on both seats of seeds 9,830,002 and 9,830,014 against
`resident`. The source trigger, tie-break, target cell, one-seed PICK/PLANT transaction, and all
subsequent D40 choices are byte-for-byte the D65a policy. Run the complete four-task trace twice and
require byte identity. Final terminal/action/state fields must reproduce the frozen D65a repair
matrix exactly.

## Trace

At every macro boundary record:

- turn, stage, worker count, producer bill and bank/carry/ripe deficit;
- selected action plane, job kind/species/target/owner and whether it targets an installed source;
- before/after bank, carry, ripe fruit, live own plants by species, and ripe own plants by species;
- every installed source root's cell, presence, owner, size, health, fruit, and cooldown before and
  after the action;
- bootstrap species/target and cumulative source PICK/PLANT counts;
- cumulative train, crop, invalidation, direct-command, provenance, deposit-prediction, action,
  state, and trace hashes.

## Classification

For each installed source and task, distinguish these ordered mechanisms without changing policy:

1. **destroyed before ripe:** the root disappears without ever exposing fruit;
2. **ripe but unselected:** fruit appears but no D40 job targets that root before it disappears or
   terminal;
3. **selected then invalidated/contested:** a root-targeted job raises invalidation or fails to
   deposit its predicted bill currency;
4. **reinvested:** root fruit is consumed by RENEW without increasing deposited bill currency,
   while own source count grows;
5. **deposited but incomplete:** a root-targeted job increases bank currency but the full producer
   bill remains infeasible;
6. **capitalized:** source-derived activity is followed by successful worker-two TRAIN; or
7. **other:** none of the above is fully supported by the boundary trace.

Multiple source roots in one task may have different lifecycle classifications. Report task-level
capitalization separately from source-level mechanism.

## Gates and decision

Require byte-identical repeats, exact D65 terminal parity, exact state chains, one action row per
selected decision, and zero mechanical/provenance failures. If integrity passes and both failed
tasks share a mechanism absent from or resolved in both successful tasks, freeze one new causal
repair at that layer. If mechanisms differ, move to a broader bill-capitalization state machine.

Do not evaluate value, run D65 fresh matrices, or access TestSession, Arena, submissions, resident
replacement, or sealed confirmation data.
