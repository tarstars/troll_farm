# D102a complete-macro resident transfer audit — frozen protocol

Frozen before implementing or executing the D102 runner on 2026-07-22.

## Question

D101 showed that the resident already creates crops and suppresses opponent crops, but almost never
harvests its own created crops and always spends its two-worker capacity on suppression. Top-three
agents normally establish renewable production, reach a larger workforce, and perform most
suppression after worker three exists.

Before designing another scheduler, test whether the exact D40 work-conserving complete-macro
teacher already contains that architecture and has merely never been compared directly with the
current stable resident. This is an architecture-transfer audit, not a learning experiment and not
a candidate qualification.

## Frozen implementations

- D40 controller: `CompleteMacroEnv::run_work_conserving_deficit_heuristic()` from
  `rust/src/rl_macro.rs`, pre-run SHA-256
  `1e3af47fe25184790763a7dbf11818944c583794303bb986f1db28708179a2e5`.
- Resident controller: `SecureOrchardBot::new()` from the embedded current policy
  `rust/src/bin/yamo_orchard_live.rs`, pre-run SHA-256
  `5ab7cbc03ce6df022023f40c9afa605e676ce2b006496350590aa2c2e25e9449`.
- Exact official local engine and official map generator already used by D40.
- No learned selector, hindsight selection, seed-specific rule, or parameter sweep is allowed.

The resident baseline runner may add measurement-only code. It must not alter either controller's
commands. Opponent trajectories may diverge after the two policies issue different commands;
"paired" therefore means the same map seed, seat, and deterministic opponent controller, not a
shared post-action trajectory.

## Population and execution

- Fresh official map seeds: `9_824_100` through `9_824_131` inclusive (32 maps).
- Seats: both 0 and 1.
- Opponents: all eight frozen `MacroOpponentMode::ALL` families:
  `resident`, `gold_adaptive`, `compact_gold`, `norx_native_three`, `legend_balanced`,
  `mybot`, `script_boss`, and `silver_boss`.
- Policies: exact D40 and exact current resident.
- Grid: 32 × 2 × 8 × 2 = 1,024 rows per run, or 512 paired task deltas.
- Repetitions: one process with one worker and one process with twenty workers. After sorting by
  `(map_seed, seat, opponent, policy)`, the TSV files must be byte-identical.
- This audit is local and open-data-only: no platform fetch, TestSession, submission, or resident
  mutation.

## Required telemetry

For both policies record terminal turn, own/opponent score and margin, own/opponent final workers,
maximum own workers, successful trains, own/opponent/ambiguous created crops, units harvested from
own-created crops, crops created after the first own-created-crop receipt, command/action hash,
canonical terminal state hash, provenance failures, terminal status, and elapsed time. D40's
existing job-integrity fields must also remain available.

Known same-kind simultaneous births are recorded separately as `joint_created_crops`; they are not
ambiguous because the exact referee merges the intents, creates one crop, and charges both planters.

## Integrity gates

All are mandatory.

1. Both runs contain the exact 1,024-row grid with no duplicates or missing cells.
2. The one-worker and twenty-worker TSVs are byte-identical.
3. Every episode terminates, score/margin/return identities are exact, and no row exceeds the
   official turn bound except the engine's established terminal step (`turn <= 301`).
4. Both policies have zero unresolved plant-provenance or ambiguous-birth failures.
5. D40 has zero invalid direct commands and deposit-prediction failures. Dynamic job invalidations
   remain telemetry but are not integrity failures: a target disappearing before a persistent job
   finishes is an expected scheduler boundary, not an invalid command.
6. D40 direct-run terminal/action/state telemetry agrees with the existing exact D40 API; the
   resident path uses the current embedded `SecureOrchardBot` without command rewriting.

Any integrity failure invalidates the value comparison.

## Mechanism gates

All are mandatory. Rates are episode rates over 512 tasks unless noted.

1. D40 creates at least one owned crop in at least 98% of tasks.
2. D40 harvests at least one unit from an owned crop in at least 75% of tasks.
3. D40 creates a later crop after an owned-crop receipt in at least 50% of tasks.
4. D40 reaches at least three workers in at least 85% of tasks and has mean final workforce at
   least 2.80.
5. Relative to the resident, D40 improves the own-crop-harvest episode rate by at least 50
   percentage points and mean final workforce by at least 0.70 workers.
6. Resident instrumentation reproduces the known architecture: it creates an owned crop in at
   least 98% of tasks and finishes with exactly two workers in at least 90% of tasks.

## Value and robustness gates

All are mandatory. Deltas are `D40 - resident` on the 512 paired task cells.

1. Mean margin delta is at least +15 points.
2. Symmetric 5% trimmed mean margin delta is at least +10 points.
3. A map-clustered normal 95% lower confidence bound for mean margin delta is above zero. Compute
   one mean delta per map over its 16 seat/opponent cells, then `mean - 1.96 * sample_sd / sqrt(32)`.
4. At least six of eight opponent-family mean margin deltas are positive and the worst family mean
   is at least -5 points.
5. Mean own-score delta is at least +20 and mean opponent-score delta is at most +10.
6. Strict task improvement rate is at least 55%; strict regression rate is at most 35%.
7. The mean of the worst 10% paired margin deltas is at least -10 points.
8. D40's negative-margin episode rate and catastrophic-margin (`margin <= -100`) rate may each
   exceed the resident by no more than two percentage points.

## Decision rule

- **Pass:** every integrity, mechanism, and value/robustness gate passes. Open D102b to measure
  compact-source/deployment feasibility and identify the smallest faithful D40 scheduler. Do not
  submit from D102a alone.
- **Mechanism pass, value fail:** D40 is useful as a behavior teacher but not a wholesale resident
  replacement. Extract role-transition supervision from its trajectories; do not package it.
- **Mechanism fail:** close D40 as an explanation of the public top-three architecture and design a
  genuinely role-persistent whole-policy controller.
- **Integrity fail:** repair measurement only, rerun the exact frozen panel, and do not interpret
  outcomes from the failed run.

## Pre-execution measurement amendment

This amendment was made before the 32-map panel and changes no mechanism or value threshold.

The first instrumentation smoke used seed `9_824_000` only. It exposed that the initially written
integrity gate incorrectly classified `invalidated_jobs` as command-integrity failures. The frozen
historical D40 baseline independently contains 898 expected target-disappearance invalidations in
256 clean episodes (211 nonzero episodes, maximum 17), while having exactly zero invalid direct
commands, provenance failures, and deposit-prediction failures. Therefore the correction above
removes only `invalidated_jobs` from the zero-error conjunction. The smoke output is excluded and
the full panel moves to wholly unobserved seeds `9_824_100..9_824_131`.

Audit trail before this amendment:

- original protocol SHA-256:
  `0912abb52e1cfdc094c90a0a5d209f4fe53822980fe4088bfc25781f0c8314f7`
- one-map smoke TSV SHA-256:
  `08a51c60caa89ace8ac0dd3748174f71ca04f1a68aab226d817762ed3840463c`
- runner SHA-256 at smoke:
  `a6116265f1190f8d2443c6004d3a0d8097872eff8f76a365d12ebec5b949797e`
- historical D40 TSV:
  `d40-macro-work-conserving-preflight-a-9670000-9670015.tsv`

### Attribution repair after the first full measurement pass

The first full pass was correctly rejected by the frozen integrity rule before value
interpretation. Exactly two mirrored resident-versus-resident task cells on map `9_824_115`
contained two same-kind simultaneous PLANT merges each. The first runner labeled these four known
joint births `ambiguous`, although the exact referee's `apply_plant` rule deterministically merges
same-kind intents and charges both planters. Both policies otherwise had zero provenance failures;
D40 had zero ambiguous births.

The measurement repair adds a `Joint` provenance state and a `joint_created_crops` column. Joint
crops count as neither exclusively own nor exclusively opponent, so own-crop mechanism metrics are
unchanged. Commands, engine states, scores, all frozen mechanism/value gates, seeds, and task cells
remain unchanged. The exact 1-worker and 20-worker panels must now be rerun and byte-identical.

Audit trail for the rejected first full pass:

- both rejected TSVs SHA-256:
  `2475443052d7d2bb447c54b814c2d46f1a8cc8bff0084f419e80f3bbf79f89a2`
- runner before joint-provenance repair SHA-256:
  `3fdedbfacd49a6e29a6917af9109da3e98eb3f90eebe18913cd8096a5b6be8c7`
- runner after joint-provenance repair SHA-256:
  `3caa71e7077db212e67ed566af9cdf099d587112e9659f369f1e7df58770a319`
