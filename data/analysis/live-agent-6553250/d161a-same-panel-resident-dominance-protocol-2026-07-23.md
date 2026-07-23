# D161a same-panel resident-dominance audit — frozen protocol

Date: 2026-07-23  
Status: frozen before simulating the resident on any D148 task

## Question

D158 was stopped because its q6 fallback was D40, which D102 measured `-48.396` mean margin behind
the exact live resident. D148's exact one-use plus priority-joint hindsight envelope adds `+41.213`
over D40, but those two numbers came from different task panels. D161 resolves the comparison on
one identical panel before any new environment, model fit, map, YT operation, or platform game.

The experiment asks only whether the existing q6 action grammar has enough *hindsight* terminal
headroom to dominate the exact resident. It does not ask whether that headroom is predictable.

## Frozen data and execution

- Reuse all 1,024 already-consumed D148 tasks: official maps `9,844,136--9,844,199`, both seats,
  and all eight frozen opponent families.
- Preserve D148's exact D40 control, exact best one-use arm, and deterministic selected priority
  pair. For tasks without a valid pair, use best one use. For a selected pair whose increment over
  best one use is nonpositive, use best one use. This exactly reconstructs D148's combined
  hindsight envelope.
- Run the unchanged D102 exact resident-versus-D40 harness on precisely those 1,024 tasks with one
  worker and 20 workers. Require byte-identical sorted TSVs.
- Require D102 D40 to equal the D148 baseline for every shared terminal, workforce, crop,
  mechanics, action-hash, and state-hash field before comparing value.
- Reconstruct every D148 selected pair from its manifest and population row; verify all target
  margins, active flags, one-use choices, and transfer aggregates against D148b.

No map in reserved range `9,844,200--9,844,215` may be generated, read, or named by a runner. No
platform or YT request is part of D161.

## Frozen comparisons

On every exact task report resident, D40, best one use, and the combined priority-joint envelope.
For each upper bound relative to resident report mean/median margin, own-score and opponent-score
deltas; strict improve/tie/regress rates; map-clustered 95% interval; all eight family means; four
consecutive 16-map block means; catastrophe count (`margin <= -100`); and negative-margin mass.

The combined envelope demonstrates resident-dominant action sufficiency only if all conditions
hold:

1. mean margin delta versus resident is at least `+5` and its map-clustered 95% lower bound is
   above zero;
2. at least 55% of tasks strictly improve and at most 35% regress;
3. at least six opponent-family means are positive and the worst family is at least `-5`;
4. all four 16-map blocks have positive mean delta;
5. mean own-score delta is nonnegative or mean opponent-score delta is nonpositive; and
6. catastrophe count and negative-margin mass do not exceed the exact resident.

Also report whether exact best one use alone passes the same conjunction. These are deliberately
high oracle gates: an unobservable per-task terminal oracle that only ties the resident is not a
credible substrate for a compact learned controller.

## Decision

- If the combined envelope fails, close the current q6/D40 action substrate for resident
  competition. Do not restart D158, enlarge its recurrent model, or build a D40-fallback candidate.
  The next representation must make exact resident KEEP/control native and add a genuinely new
  multi-turn action.
- If it passes, the action vocabulary has same-panel resident-relative headroom. D162 may then
  test learning with every gate and reward stated relative to exact resident; no D161 result alone
  opens reserved maps, a candidate, TestSession, submission, or Arena.

## Frozen inputs

- D148b result SHA-256:
  `df8c045096518762f9189238cf9bdf87113e1561a01c48baee410bc3cf2607c2`;
- D148 baselines:
  `68ff22a5de9ed07b2ff96170d9e1a8287061bb5f20612548e562975d7bd02e8b`;
- D148 population:
  `c02a607ca0b4f1084a541d03673c375a3f7238b2ccaf5911b3482e4ad6e8d162`;
- D148 manifest:
  `3e2845e1468401a1c05afa33ff0644b7ae1ed12363d1730d40cc2e1440759d81`;
- unchanged D102 runner:
  `3caa71e7077db212e67ed566af9cdf099d587112e9659f369f1e7df58770a319`.
