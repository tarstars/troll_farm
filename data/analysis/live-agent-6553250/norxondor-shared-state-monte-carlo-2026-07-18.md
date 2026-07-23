# Norxondor shared-state Monte Carlo — Phase 11

## Verdict

The shared-state experiment separated an algorithmic success from a deployment failure.

- The frozen terminal rollout teacher is strong and repeats on a disjoint seed block: **+26.081
  mean margin** and **+15.194 mean score** versus resident, with positive mean margin against all
  eight opponents and no selected losing cell.
- A 240-turn liquid-value approximation retains **89.19%** of that margin gain and remains
  positive against all eight opponents, but its unchanged validation precision is **88.33%**,
  below the frozen 90% safety gate.
- Inner-parallel execution is still far outside the platform budget: **209.487 ms median, 279.460
  ms p95**, and **0/80** profiled decisions at or below 50 ms.
- Compact tree, deployable forest, and raw-signature distillation do not meet the precision gate.

No online prototype, candidate, sealed holdout, submission, or arena action follows. The exact
62,725-byte resident remains unchanged.

## Protocol

Both complete branches were forked from the same exact-engine state after the resident had played
the first two turns. The alternatives were:

1. the exact resident continuation;
2. the frozen Norxondor exact-three-worker continuation.

For each cell, all eight local opponent models replayed the observed prefix. Selection could use
only observable transition agreement; actual opponent identity was retained solely as evaluation
truth. Discovery used seeds 302--311 and validation used 312--321, both seats, and all eight actual
opponents: 160 cells per block. The previously sealed map holdout was not read.

## Terminal teacher

The discovery rule was frozen as:

> At turn 3, retain the models with the maximum number of exact observed prefix transitions and
> choose worker-three only when the minimum terminal margin delta across that set is positive.

| Measure | Discovery 302--311 | Validation 312--321 |
|---|---:|---:|
| Selected cells | 69/160 | 72/160 |
| Selection precision | 100% | 100% |
| Mean margin delta | +30.281 | +26.081 |
| Mean score delta | +17.838 | +15.194 |
| Nonnegative opponent means | 8/8 | 8/8 |
| Worst opponent mean margin | +14.700 | +12.000 |
| Mean compatible models | 1.613 | 1.575 |
| Actual model retained | 100% | 100% |

This proves that the macro branch and early-transition conditioning contain real local value. It
does not make the full terminal simulator deployable: the original sequential terminal prediction
took roughly 4.3 seconds per cell under the sweep workload.

## Horizon study

No partial configuration through 120 turns passed. The first discovery pass appeared only at 240
turns, using median compatible-model liquid-margin delta greater than 20. Liquid margin contains
only banked score and directly carried score value; it adds no invented worker or asset bonus.

| Measure | Discovery 302--311 | Unchanged validation 312--321 |
|---|---:|---:|
| Selected cells | 61/160 | 60/160 |
| Selection precision | 93.44% | 88.33% |
| Mean margin delta | +29.488 | +23.263 |
| Mean score delta | +15.950 | +10.375 |
| Nonnegative opponent means | 8/8 | 8/8 |
| Worst opponent mean margin | +9.500 | +10.650 |
| Terminal-teacher margin retained | — | 89.19% |

The complete-policy outcome gate passes, but the separately frozen 90% selection-precision gate
does not. The buffer was not relaxed after seeing validation.

## Distillation attempts

- A seven-leaf single tree reached 81.08% imitation precision on seeds 312--321. Its selected
  policy was locally profitable (+10.556 margin / +13.206 score), but it failed the precision gate.
- A precision-first ExtraTrees-style audit used all 320 consumed cells and 93 deployable features,
  excluding opponent-model mismatch and compatibility features. None of the tested configurations
  reached 90% blocked-seed precision while selecting at least 5% of cells.
- The only conservative raw opening signature discovered on the first block transferred only
  +1.213 margin / +1.444 score, below the +2 policy gate.

These failures are consistent with sample scarcity and missing generic trajectory features, not
with absence of a branch-value signal.

## Parallel latency

The frozen 240-turn calculation was profiled on 80 already-consumed discovery cells. Prefix
compatibility ran serially; resident and worker-three rollouts for every retained model ran
concurrently. Thread creation and joining were included.

| Measure | Median | p95 |
|---|---:|---:|
| Compatibility | 1.557 ms | 3.051 ms |
| Parallel rollouts | 207.872 ms | 278.014 ms |
| Total prediction | 209.487 ms | 279.460 ms |

The median parallel speedup over summed branch elapsed time was 1.82x, but even the fastest total
decision was 124.152 ms. Direct online Monte Carlo therefore needs more than a 5.5x p95 reduction,
and its fastest observed case still needs a 2.5x reduction. Simulator micro-optimization is not
the next move.

## Phase 12

Preserve the useful teacher but move all expensive simulation offline:

1. generate a substantially larger exact resident-versus-worker-three outcome dataset with only
   the two actual branches per cell;
2. add directly observable turn-1-to-turn-3 trajectory features—unit positions, movement,
   inventory changes, worker stats, and carries—without opponent labels or embedded models;
3. require both blocked-seed and leave-one-opponent-out precision of at least 90%, at least 5%
   selection, and the existing paired policy gates;
4. freeze a compact expression before opening any new validation block, then measure its source
   bytes and runtime inside the exact resident;
5. keep the current sealed holdout and arena untouched unless the integrated compact controller
   passes unchanged.

## Evidence

- `norxondor-shared-state-discovery-study-302-311-2026-07-18.json`
- `norxondor-shared-state-validation-study-312-321-2026-07-18.json`
- `norxondor-partial-rollout-extended-study-2026-07-18.json`
- `norxondor-shared-state-distillation-2026-07-18.json`
- `norxondor-shared-state-forest-study-2026-07-18.json`
- `norxondor-parallel-latency-study-302-306-2026-07-18.json`

