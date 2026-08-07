# Frozen protocol — E7a half-size logical simplification

Frozen on 2026-08-02 before source implementation.

## Objective and exact baseline

The owner requests a successor to the exact live E7a candidate that is at least 50% smaller
through removal or simplification of logic, while accepting a live rank change from 11 to no
worse than 15.

- Baseline source: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
- Baseline SHA-256: `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- Baseline bytes: 62,820
- Hard candidate ceiling: 31,410 bytes
- Arena baseline at 2026-08-02T19:52:10Z: exact agent `6590141`, submission `41081503`,
  score 25.26 (room display 25.3), rank 11/131
- Terminal live gate: exact recovered candidate rank <=15 after the registry's mature
  checkpoint; an initialization read cannot satisfy the gate

The previous N7 result remains correct: the four known dead development families are
already absent from the deploy. This task is a deliberate behavior/architecture
simplification, not dead-code cleanup and not permission to edit the sacred source.

## Non-obfuscation rule

The size reduction must be semantic and inspectable.

Allowed:

- delete a named live subsystem;
- replace a multi-mode subsystem with one readable policy;
- delete telemetry, compatibility APIs, or generality that the new standalone controller
  does not exercise;
- factor repeated logic into an ordinary named helper when that improves or preserves
  readability.

Forbidden:

- shorten existing identifiers merely to save bytes;
- remove whitespace/comments as the principal reduction mechanism;
- encode source or logic into compressed strings, generated tables, macros, or numeric
  dispatch whose principal purpose is size;
- change formatting/minification relative to the 62,820-byte baseline and credit those
  bytes toward the 50% target;
- copy another agent's source.

Every candidate manifest must list removed/replaced logical blocks and attribute gross
bytes to them. A mechanical token audit must report identifier changes; every changed or
removed identifier family must map to a declared logical deletion/replacement.

## Preserved core behavior

The integrated candidate must retain, in readable form:

1. exact protocol parsing and legal command emission;
2. BFS navigation on orthogonal walkable cells;
3. cargo-to-shack banking and a persistent commitment for wood already routed home;
4. training of a second worker without sacrificing its resource bill to denial;
5. the frozen E7a initial PLUM/LEMON near-tie rule (`PLUM-LEMON <= 8` when parent defaults
   to LEMON);
6. chop valuation that includes travel, chop and return feasibility;
7. a two-worker same-target/landing conflict guard;
8. terminal fruit-to-wood conversion only when the completed return fits before turn 300.

Everything else is eligible for deletion or replacement, including the general secure
orchard state machine, broad candidate API generality, exhaustive pair machinery,
multi-mode regeneration, redundant forecasts, and specialized door patterns, provided the
gates below pass.

## Stages

### Stage A — byte and behavior attribution

Create a readable temporary rendering of the exact candidate outside protected paths.
Inventory top-level types, functions and impl methods by source span. Join this inventory to
the 160 exact live E7a games where observable: activation counts, command counts, crop
effects, endgame conversions, liveness incidents and outcome association. Produce a ranked
removal/replacement ledger. Do not infer causal value from association.

### Stage B — named ablation arms

Build standalone, readable arms from the exact candidate without editing it:

- `ORCHARD_SIMPLE`: replace `SecureOrchardBot` with the inner controller plus a minimal
  one-seed rule or remove it if the size/value trade is superior;
- `OPENING_SIMPLE`: replace exhaustive second-worker specification/ETA generality with a
  small fixed or two-choice bill-preserving scheduler;
- `ASSIGN_SIMPLE`: replace general candidate-target Cartesian assignment with a two-worker
  reservation rule;
- `ENDGAME_SIMPLE`: retain only a bounded feasible plant/chop/bank conversion;
- `INTEGRATED_HALF`: combine the best live blocks until <=31,410 bytes.

Arms may be abandoned early when their achievable gross byte reduction is insufficient.

### Stage C — static and semantic gates

For every retained arm and the integrated candidate:

- standalone optimized compile succeeds;
- source size and SHA-256 recorded;
- empty input exits without stderr; malformed commands are never emitted in smoke runs;
- sacred source remains SHA-256
  `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
- exact E7a focus fixtures pass below, at, and above the distance threshold;
- training-bill priority, same-target exclusion, bank commitment and endgame deadline
  fixtures pass;
- the earlier live oscillation game `897832286` and every available >=6-turn period-2 E7a
  counterexample are included in a no-long-period-2 gate;
- p95 per-turn latency does not exceed the baseline by more than 20%, and maximum remains
  below the platform limit.

### Stage D — open closed-loop value gate

Use only already-open official maps and existing open opponent controllers. Run both seats
with exact seeds and continued referee semantics. The integrated candidate must:

- cover at least 512 paired tasks across at least six opponent families;
- have zero critical/unclassified referee failures and zero identity/source mismatches;
- lose no more than 0.50 paired mean margin versus E7a;
- have a game-cluster/bootstrap 95% lower bound above -2.0 margin;
- not increase catastrophes or negative-margin mass;
- be nonnegative in at least five of six family means and both seat means;
- train worker two in at least 95% of baseline-training games and never later by more than
  10 turns at the median;
- eliminate all >=6-turn period-2 episodes in the supported counterexample packet.

These are engineering qualification gates, not a claim that the local zoo predicts Arena
rating. Failure is preserved; no threshold tuning on the evaluated task set.

### Stage E — Arena

Only a candidate passing Stages A--D can enter the promotion runbook. Before submission:
verify exact bytes/SHA, controller exclusivity, baseline rank, browser/API identity, and
notify peers/user. Submit exactly once; never retry an ambiguous response. Record returned
submission and agent ids, exact-source recovery, runtime/identity health, initial landing,
and mature checkpoint.

Goal success requires both:

1. recovered exact Arena source size <=31,410 bytes; and
2. mature room rank <=15.

If rank is worse than 15, the goal remains active. A restore or another candidate is a new
serialized cycle; no automatic mutation is authorized by a failed checkpoint.

## Evidence boundary and stop rules

- Public replays and local panels are descriptive/engineering evidence, not causal Arena
  rating estimates.
- Do not read sealed maps or confirmation ranges.
- Do not reformat `rust/src/bin/` or `cgauto/`.
- Do not modify existing submissions, raw games, or collection jobs.
- A candidate over 31,410 bytes cannot qualify regardless of score.
- Cosmetic compression cannot qualify regardless of byte count.
