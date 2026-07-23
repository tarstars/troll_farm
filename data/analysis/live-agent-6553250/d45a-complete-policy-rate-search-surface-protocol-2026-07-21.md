# D45a complete-policy rate-search surface — frozen preflight (2026-07-21)

## Question and scope

D44a closes snapshot rank-zero/rank-one selection. D45 changes both optimization target and action
surface: whole-game terminal margin selects a compact policy that may choose among every legal rate
job, while D40's validated TRAIN, exact-deficit, and shack-evacuation mechanics remain fixed.

D45a asks only whether this parameterization is deterministic, exactly anchored at D40, causally
active, outcome-sensitive, and computationally usable. It reuses the first four consumed D40 maps
9,670,000--9,670,003. It may not select a parameter vector, fit a distribution, open a fresh map,
construct a candidate, invoke TestSession, submit, or act in Arena.

## Frozen inputs

- D40 protocol SHA-256:
  `5c0190f86fe88bbe869f45f530aaea960c8301572dae383f831ac674387fed82`;
- D40 exact result JSON SHA-256:
  `dab4bb75f7ad2af8a8e4d69828dd6b80954d897c7e03cfd089ef8a2edc012c65`;
- D40 A reference TSV SHA-256:
  `653dee375b1922bd43b74e6e9aa1b27503d8017350f3b8dcf3baed197827b8a5`;
- complete macro environment source SHA-256:
  `6e59965b6d020e9eb51cf41d0a12b72addf0cd776bf7c67a93ef055783788044`;
- exact prior source SHA-256:
  `632f1b2c99c18073c4cd956863fcaa4b7e9773dd69bb745fc18f062337130f62`.

## Frozen policy family

At every non-`rate` decision choose exact D40 rank zero. At a `rate` decision, compute exact D40
prior rank for all legal candidates and maximize

`-rank / max(candidate_count - 1, 1) + theta dot phi(candidate, state)`.

Stable ties prefer lower D40 rank and then lower action ID. The 32 finite features are:

1. six job-kind indicators (`idle`, `bank`, `fell`, `harvest`, `renew`, `mine`);
2. predicted ETA, reward, deficit reduction, and D40 rate value;
3. four plant-owner indicators;
4. four TRAIN-resource predicted deposits;
5. normalized action ID and plant-cell ID;
6. `(turn / 300 - 0.5) × job-kind` for all six kinds; and
7. `(worker_count / 3) × job-kind` for all six kinds.

Zero parameters must reproduce D40 exactly at every decision and terminal field. This is a
complete-policy direct-search surface, not a value predictor: parameters are judged only by whole
episodes.

## Frozen perturbation catalog

Create exactly 17 vectors in this order: `zero`, then plus/minus pairs for base `bank`, `fell`,
`harvest`, `renew`, `mine`, opponent-owner, turn×renew, and workers×fell. Base/job/owner amplitudes
are `0.05`; interaction amplitudes are `0.10`; every unlisted coordinate is zero. The catalog is
outcome-blind and must be written and hashed before execution.

Run all 17 vectors on four official maps, both seats, and all eight opponents: 1,088 complete
episodes. Run the exact matrix independently twice with 20 threads and write deterministic TSVs
sorted by `(genome, map_seed, seat, opponent)`.

## Frozen gates

The surface passes only if all hold:

1. both 17 × 64 grids are complete, finite, and byte-identical;
2. zero has exact parity with the corresponding 64-row D40 prefix for every terminal, action-plane,
   action-hash, and state-hash field;
3. every arm has zero illegal commands, provenance failures, deposit-prediction failures, worker
   overflow, or decision loops;
4. at least 12 of 16 perturbations change the action hash in at least 5% and at most 95% of tasks;
5. the range of perturbation mean margins is at least 15 points and contains values both above and
   below zero's mean (descriptive sensitivity only; neither side is selected);
6. at least eight perturbations retain worker-two >=90%, worker-three >=50%, and crop >=60%; and
7. at least four of the eight plus/minus semantic pairs differ in mean margin by at least two
   points, proving directional rather than hash-only sensitivity.

## Decision rule

A pass opens a separately frozen D45b cross-entropy search with new development maps, a fixed
population/generation budget, whole-game margin objective, exact D40 control, and untouched
validation/confirmation banks. D45a outcomes cannot choose the initial mean, covariance, feature
set, perturbation scale, or final vector.

A fail closes this 32-parameter surface. Diagnose parity, activation, outcome sensitivity, or
safety from the frozen matrix; do not add coordinates or change amplitudes on these maps.
