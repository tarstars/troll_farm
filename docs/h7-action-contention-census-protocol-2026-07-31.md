# H7′ action-contention census protocol — 2026-07-31

## Question

Does the exact-resident D159 panel contain a material strong-opponent signature in the
cross-player action-contention mechanics that actually exist: simultaneous legal
HARVEST/CHOP, last-item duplication, combined-only tree kills, or an opponent action
making the exact tree named by a resident MOVE unavailable that turn?

This is a read-only premise audit. It cannot identify private intent and therefore never
calls observed behavior “deliberate.” Body-blocking, door camping, path denial, generic
opponent-crop scoring, contact coverage, travel efficiency, and harvest-before-chop are
excluded because their mechanic or intervention classes are already closed.

## Frozen population and cohorts

Use only the 200 exact resident games named in
`d159a-current-resident-all-finished-effect-refresh-raw.json`, SHA-256
`97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443`.
The accepted D159 result has SHA-256
`bd3fe4571aec423cdb57d514a2f610c0dcfe9845099b5500a6721e98d72965ac`
and records 200/200 exact identities and zero unknown diff updates. Read each named raw
game and processed trajectory in place; do not enumerate or open any other game.

Freeze rank cohorts from each manifest row:

- strong: opponent rank 1–20;
- middle, descriptive only: rank 21–40;
- comparator: rank 41 or worse.

Report games, turns, opponent identities, resident seats, and outcome/margin for all
cohorts. Do not substitute current ranks or scores.

## Exact event families

An issued unit command is assigned with the repository's existing referee-faithful
parser. Legality is evaluated from the exact pre-turn state.

1. `dual_harvest`: both players issue legal HARVEST on the same live tree in the same
   turn. Reproduce round-ordered awards from harvest power, capacity, and fruit count.
   `last_fruit_duplication` is the exact total award above the pre-turn fruit supply.
2. `dual_chop`: both players issue legal positive-power CHOP on the same tree in the
   same turn. Reproduce total damage, death, capacity-limited wood awards, and
   `last_wood_duplication`. A `combined_only_kill` requires neither player's damage to
   be lethal alone but their combined damage to be lethal.
3. `move_target_removed`: a unit issues a legal MOVE to the exact coordinate of a tree
   present at turn start, has positive capability and free capacity for its available
   resource, and reduces BFS distance toward that coordinate. The other player then
   legally removes the tree by CHOP in that turn. Count direction separately.
4. `move_target_depleted`: the same exact-target MOVE condition, but the other player
   legally HARVESTS the tree and the next decoded state contains that tree with zero
   fruit. Count direction separately.

Also report same-tree cross-player co-location and both players naming the same extant
tree in MOVE commands, but these are descriptive only. A target coordinate is evidence
of a race exposure, not proof of strategic intent or terminal waste.

For each causal family, the expected pre/post unit carries, tree survival/health/fruits,
and resource deltas must agree with decoded state. Later priority actions and the plant
tick must be included. Any mismatch is an integrity error rather than an event.

## Value and cohort summaries

Report per game and cohort:

- event-game prevalence and events per 1,000 decoded turns;
- distinct opponent identities and resident-seat coverage;
- duplicated fruit and wood, with direct score-equivalent ceiling
  `fruit + 4 × wood`;
- combined-only kills;
- resident-target and opponent-target removal/depletion races;
- outcome/margin associations as descriptive, never causal.

Compare strong versus comparator event-game prevalence with 10,000 deterministic
opponent-identity-cluster bootstrap replicates (seed 20260731). Preserve every sampled
identity's games and report the percentile 95% interval for the percentage-point
difference. Middle-cohort games do not enter that contrast.

## Integrity and materiality gates

All integrity gates must pass:

1. exact 200-game D159 ID set, manifest/result/source identity, file presence, and no
   duplicate IDs or outside reads;
2. all 200 games decode with zero unknown updates;
3. every accepted exact event passes legality and pre/post transition checks;
4. at least 30 strong and 40 comparator games, at least 10 identities per cohort, and
   both resident seats represented in each cohort;
5. deterministic repeated output.

Return `MATERIAL_STRONG_COHORT_SIGNATURE` only if all are true:

- at least 20/200 games and at least 8 opponent identities contain an exact primary
  event (`dual_harvest`, `dual_chop`, resident-target removal, or resident-target
  depletion);
- those exact primary events cover both resident seats;
- strong event-game prevalence exceeds comparator prevalence by at least 10 percentage
  points and the identity-cluster bootstrap 95% lower bound is greater than zero;
- at least one directly mechanical consequence exists: last-item duplication,
  combined-only kill, or exact resident-target removal/depletion.

These are premise/readiness gates only. Passing them does not establish intent, terminal
value, an intervention, or a candidate.

## Frozen verdicts

- `MATERIAL_STRONG_COHORT_SIGNATURE`: all integrity and materiality gates pass; request
  a separately frozen causal/value audit before any implementation.
- `NO_STRONG_COHORT_ACTION_CONTENTION_SIGNATURE`: integrity passes but at least one
  materiality gate fails; close H7′ without a controller or experiment.
- `UNIDENTIFIABLE`: exact replay observables cannot support the required event or cohort
  classification.

## Stop rules

Stop after analyzer/tests, compact JSON/report/manifest, canonical closeout, and peer
handoff. Do not fit a selector, tune a threshold, edit source/simulator/referee, open
maps or unlisted games, create a candidate, submit, or touch Arena.
