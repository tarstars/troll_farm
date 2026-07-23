# D28 resident handoff-state experiment — frozen protocol (2026-07-20)

## Question

At the exact D26 turn-150 handoff, can retaining resident controller state avoid the -20.649
margin cost of a cold restart without changing the farm interval or post-handoff resident policy?

Every branch uses the exact resident prefix through turn 74 and `ownership2` through turn 149.
The cutoff is fixed at turn 150 and may not be tuned.

## Branches

1. `resident`: warmed resident from turn 75 through terminal (control).
2. `farm`: `ownership2` from turn 75 through terminal (D24 parity control).
3. `cold`: `ownership2` through 149, then a new resident (D26 parity control).
4. `paused`: preserve the exact warmed turn-75 resident object without invoking it during the farm
   phase, then resume it at turn 150.
5. `shadow`: invoke the preserved resident on every observed farm state but discard its commands,
   then activate it at turn 150.

`paused` is directly implementable and remembers no phantom commands.  `shadow` distinguishes
stale state from continuously observed state, but is diagnostic: internal commitments may refer
to commands that were proposed but never executed.  It cannot authorize prospective testing or
candidateization until replaced by an actual-command observer.

## Data and integrity

- Outcome-blind smoke: seeds 0--4, both seats, all eight structural opponents, byte-identical
  repeat.
- Development: already-consumed seeds 50,000--50,119, both seats, all opponents.
- Prospective confirmation, only if `paused` passes: untouched seeds 52,000--52,059.
- Independent unit: map seed after averaging seats/opponents.

The runner records the turn-150 state and executed farm-prefix command hash for every farm branch.
Smoke/development readiness requires a complete grid, common turn-75 roots, exact equality of every turn-150 field
and farm-prefix hash across `farm`/`cold`/`paused`/`shadow`, clean terminal play, 100% control
parity with D24/D26 on consumed blocks, and >=20% terminal command divergence from `cold` for each
state-retaining branch.  A narrow prospective `resident`/`paused` run instead requires >=20%
divergence between those two reported branches; it must not compute the other outcomes.

## Frozen gates

For `paused` and `shadow`, report deltas against both `resident` and `cold`, seed-clustered 95%
intervals, all opponent means, catastrophe frequency, negative-margin mass, control-catastrophic
value, action/workforce telemetry, and the fraction executing both phases.

A branch demonstrates a useful handoff only if:

1. versus resident: mean margin >= +5, 5%-trimmed mean >= +3, and 95% lower bound > 0;
2. versus resident: own-score mean >= +5;
3. versus resident: >=6/8 opponent means nonnegative and worst mean >= -5;
4. versus resident: positive mean on resident-catastrophic cells;
5. terminal catastrophe frequency and negative-margin mass do not exceed resident;
6. versus cold: mean margin improvement >= +10 and 95% lower bound > 0; and
7. at least 95% of reached cells execute both farm and resident phases.

If `paused` passes, freeze it and run only `paused`/resident controls prospectively.  If it fails,
do not open prospective data.  A shadow-only pass authorizes an actual-command observation API on
the consumed block, not direct deployment.  If neither passes, classify the post-150 resident
policy itself—not initialization state—as the return problem and move to farm-preserving
suppression or planting exclusivity.

## Outputs

- runner: `rust/src/bin/d28_handoff_state.rs`;
- analyzer: `cgauto/d28_handoff_state_analysis.py`;
- smoke/development/optional confirmation TSV and JSON;
- result: `d28-resident-handoff-state-result-2026-07-20.md`.
