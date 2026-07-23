# Residual forward-search iteration — 2026-07-16

## Why the old RHEA plateaued

The fast forward engine is not the limiting resource: on the current host it executes about
4,558 bare 40-turn rollouts in a 45 ms budget. The old RHEA instead evaluates randomly mutated
three-task plans with a costly full continuation policy. It currently loses to `goldelite` by
-107 average with search disabled and -138 at a 30 ms search budget. More search makes it worse.

This iteration does not revive whole-plan random mutation. It treats the strongest stable local
policy as a control and searches only for a demonstrably better immediate deviation.

## Final architecture

1. `goldelite` supplies the actual baseline commands and remains the fallback.
2. GoldElite owns the strategic opening through turn 79 and until a chop-2 unit exists. Search
   starts only after the economy is established.
3. Candidate generation is structured and bounded: change one unit's immediate command to a
   small set of legal, role-preserving movement alternatives. Direct work such as `CHOP`,
   `HARVEST`, `PLANT`, `PICK`, and `DROP` is never interrupted.
4. All candidates receive a four-turn exact-referee rollout against the elite continuation model.
5. Only the top four candidates receive 16-turn exact-referee rollouts.
6. Finalists are evaluated against both elite and scheduler opponent continuations. A candidate
   rejected by Elite skips the Scheduler rollout because it cannot pass the conjunctive gate.
7. A deviation is emitted only when its value improvement over the baseline is at least the
   configured margin in every long-rollout scenario. Otherwise output is byte-for-byte baseline.
   The retained margin is +5.
8. An accepted target is held for at most eight turns and is modeled with exactly that commitment
   in the rollout. If it expires or reaches a target that does not unlock direct work, that
   `(unit, target)` option is suppressed for the rest of the game. This bounds false-positive cost
   and prevents receding-horizon rediscovery loops.
9. Rollouts are clamped at turn 300; they cannot value imaginary postgame actions.
10. Search never mutates the baseline source or writes to the arena.

This is model-predictive residual search, not classic MCTS. It deliberately spends simulations on
plausible disagreements with a strong policy rather than rediscovering the entire policy through
random trajectories.

The implementation is `rust/src/strategies/residual_search.rs`; `residual_study` performs paired,
both-seat evaluation and `residual_time` measures release-mode latency.

## Determinism and holdout discipline

- Seeds 0..199 were used for implementation diagnosis and discovery.
- Iteration 1 used seeds 20,000..20,199 once. It had a positive mean but a -346 minimum caused by
  rediscovering the same finite-horizon option every nine turns. That iteration was rejected.
- Iteration 2 used seeds 30,000..30,199 once. Failed-option suppression removed rediscovery, but a
  -182.5 minimum showed that a few opening deviations could still collapse the long-run economy.
  That iteration was rejected.
- The final phase-gated design was frozen before opening seeds 40,000..40,199. Those seeds were
  evaluated against all five opponents and were not used for tuning.
- Opponent diversity must include `goldelite`, `schedbot`, `mybot`, `silverboss`, and
  `scriptboss`, with both seats.
- Disabled search must reproduce `goldelite` exactly.
- Release-mode decision time must remain within the 50 ms turn budget, with a target p95 <=45 ms.
- A retained prototype needs nonnegative paired mean against every opponent, nonnegative overall
  trimmed mean, and no evidence that gains come only from one extreme map.

Deterministic tie-breaking was added to GoldElite and Scheduler choices. With `RS_ENABLE=0`, the
paired GoldElite delta was exactly zero on 500/500 seeds; enabled-search repeats were also exact.

## Final untouched holdout

Each row is 200 map seeds, both seats, and paired candidate-minus-control margin. `without best`
removes the largest delta, and `worst 10%` is the mean of the 20 lowest deltas.

| Opponent | Mean | Trimmed 5% | Without best | Worst 10% | W/T/L | Min | Max |
|---|---:|---:|---:|---:|---:|---:|---:|
| GoldElite | +20.900 | +20.778 | +20.691 | -4.675 | 186/2/12 | -29.5 | +62.5 |
| Scheduler | +16.215 | +16.008 | +15.603 | -24.225 | 160/3/37 | -78.0 | +138.0 |
| MyBot | +10.375 | +10.269 | +10.156 | -18.825 | 147/2/51 | -44.0 | +54.0 |
| SilverBoss | +14.920 | +14.961 | +14.678 | -14.350 | 165/5/30 | -41.5 | +63.0 |
| ScriptBoss | +17.120 | +17.897 | +16.791 | -26.225 | 162/2/36 | -67.0 | +82.5 |
| Equal-weight total | **+15.906** | **+15.983** | **+15.584** | **-17.660** | **820/14/166** | -78.0 | +138.0 |

All five opponent means, trimmed means, and without-best means are positive. The final design also
removed the structural tail: GoldElite's minimum improved from -346 in iteration 1 to -29.5, and
its worst-decile mean improved from -95.175 to -4.675.

## Runtime and disposition

The final isolated ten-game release timing sample covered 3,000 decisions: mean 10.05 ms,
p50 9.52 ms, p95 28.53 ms, p99 32.46 ms, and max 49.67 ms. No decision exceeded 50 ms.
The timing harness also reports per-game over-budget concentration so future runs cannot hide
deadline risk behind p95.

This is now a credible **controlled arena A/B candidate**, not an automatic replacement for the
live bot. No submission or arena write was performed in this iteration.

## Deployment correction — 2026-07-17

The performance result validates the residual architecture only against the local GoldElite
policy.  The actual Legend resident is Yamo/Orchard, so this implementation is **not** a valid
arena A/B artifact and must not replace the live fallback.  A source audit subsequently reduced
the promoted Yamo/Orchard stack from 90,547 to 62,725 behavior-identical bytes.  That creates
enough room for the 23,257-byte referee engine plus roughly 14 KB of specialized controller, but
the existing 23,210-byte residual controller still does not fit unchanged.  The next iteration
must port a compact residual around the promoted policy and repeat all holdout and timing gates.

## Compact workforce viability gate — 2026-07-17

The first promoted-policy follow-up isolated workforce expansion before porting the full search
layer.  Surplus-only duplicate and 2/2/0/2 third workers were command-identical to the parent on
200/200 discovery seeds: normal play never funded either.  Behavior-neutral telemetry over 400
sides found zero affordable windows even for `(1,1,0,1)`; its median best PLUM/LEMON/APPLE/IRON
deficit was `3/3/0/3`.

Letting only the starter collect for a 2/2/0/2 third worker lost -2.225 margin and -1.092 wood on
60 seeds while issuing zero extra TRAINs.  A turn-25-bounded `(1,1,0,1)` kill test reduced the
loss to -0.358/-0.058 but still issued zero extra TRAINs.  Workforce expansion is therefore
**rejected before holdout**.  The next compact residual must be renewal-only and TRAIN-free, with
payback bounded by the corrected stall horizon.  Full record:
`data/analysis/live-agent-6553250/compact-workforce-iteration-2026-07-17.md`.
