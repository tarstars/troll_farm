# Pre-fruit reproductive interruption — frozen protocol, 2026-07-19

## Hypothesis

The complete farm loses to adaptive Gold because opponent-owned crops reproduce after turn 100.
Diverting the farm's empty pure chopper only when it can destroy an attributed opponent crop
before that crop's first fruit will suppress the next generation while retaining most private
production. This should recover materially more of the resident's adaptive-Gold advantage than
the rejected mature-tree current-cycle rate controller.

## Frozen controller

The base policy and shadow are the exact `lean_m2c2h0k2` complete farm. Plant ownership is inferred
causally from between-turn births and our previous PLANT attempts, using the already tested ledger.

On each turn, consider only our units with chop at least 2, harvest power 0, and empty total carry.
Consider only attributed opponent crops with zero fruit. Simulate the actual referee order from the
current state:

1. spend `ceil(distance / movement)` MOVE turns;
2. begin chopping on the following turn, or immediately when already on the crop;
3. after every action, tick crop cooldown, growth, health slope, and fruit using the engine's exact
   type and water rules; and
4. accept only if the crop dies before the tick that would create its first fruit.

Require at least one opponent harvest-capable unit to be able to reach the crop by that first-fruit
tick. Preserve a feasible committed target. Otherwise choose lexicographically by earliest first
fruit, earliest kill, then cell. Replace only that pure chopper's command with MOVE or CHOP. Never
divert a carrying unit, copy resident commands, add a learned coefficient, or modify training,
planting, harvesting, picking, dropping, or the starter's command.

Telemetry records attributed crops, changed activation turns, first activation, farm-shadow
mismatches, distinct targets that disappear before fruit, and targets observed fruiting after
selection. Inactive candidate cells must be exactly identical to the farm on all outcome and
provenance fields.

## Frozen partitions

- Integrity: consumed seeds 0--29, eight opponents, both seats; run the same executable twice.
- Discovery: fresh seeds 1900--1959, eight opponents, both seats.
- Confirmation: seeds 1960--2019, opened only if every discovery gate passes unchanged.

Each phase contains 960 scenarios per profile and compares exact resident, exact farm, and the
pre-fruit controller on a common grid. Use process-level parallel workers; sort output before
comparison.

Seeds 1840--1899 remain sealed for the closed resident-component protocol and are not reassigned.

## Integrity gates

All must pass:

- complete expected three-profile grid and all games complete;
- byte-identical repeated integrity TSV;
- at least 95% assigned chopped-wood provenance for every profile;
- zero base/shadow farm command mismatches; and
- exact farm identity for every inactive candidate cell.

The earlier historical aggregate is informational only because the deterministic engine repair is
already known to shift one 60-game mean by 0.333 point.

## Discovery gates

All must pass. Candidate minus resident across 960 cells:

- mean margin at least +10;
- 5% trimmed mean margin at least +5;
- mean own score at least +50;
- mean own inventory wood at least +10;
- nonnegative mean margin on at least six of eight opponents;
- worst opponent mean margin at least -5; and
- adaptive-Gold mean margin nonnegative.

Mechanism and opportunity-cost gates:

- at least 200 activated cells overall and 30 against adaptive Gold;
- at least 30 distinct selected targets disappear before fruit overall;
- against adaptive Gold, candidate minus farm opponent score at most -50,
  opponent successful plantings at most -10, and opponent self-crop wood at most -20; and
- against adaptive Gold, candidate minus farm own score at least -40.

These deliberately demand reproductive suppression rather than ordinary wood capture.

## Confirmation and stop rule

Confirmation repeats every gate on the sealed range, except the trimmed-mean floor rises to +10.
If discovery fails any gate, close this exact controller without threshold tuning and do not open
confirmation. If both phases pass, package it for source/runtime checks and a fresh official-prefix
field audit; do not submit directly.

