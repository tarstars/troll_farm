# D48a complete-policy economic-bonus surface — frozen preflight (2026-07-21)

## Question and scope

D46/D47 close permanent job-role overrides: maximum-chop felling is already implicit in D40, while
forcing the other workers onto renewable work loses 12.016 paired margin. D40's adaptive rate
comparison is therefore retained. Its remaining literal economic calibration is compact and
explicit:

`1000 * predicted_reward / predicted_eta`

plus 20,000 for opponent provenance, 10,000 for ambiguous provenance, 15,000 for `RENEW`, and
8,000 for `BANK`.

D48a asks whether three multiplicative scales on these actual formula terms provide an exact,
deterministic, active, safe, and outcome-sensitive surface. It reuses consumed D40 maps
9,670,000--9,670,003 only. No arm may be selected; no parameter fitting, fresh map, candidate,
TestSession, submission, or Arena action is allowed.

## Frozen policy family

At every non-`rate` decision choose exact D40. At a `rate` decision score every legal job as:

`base_rate + provenance_scale * provenance_bonus`

`          + renew_scale * renew_bonus + bank_scale * bank_bonus`.

The provenance scale jointly preserves the frozen 2:1 opponent/ambiguous relationship. Candidate
features reconstruct the exact integer predicted reward, ETA, job kind, and owner. Ties retain
exact D40 prior order, so scales `(1,1,1)` must reproduce D40 at every decision.

## Frozen perturbation catalog

Create exactly seven policies in this order:

1. `anchor`: `(1,1,1)`;
2. `provenance_zero`: `(0,1,1)`;
3. `provenance_double`: `(2,1,1)`;
4. `renew_zero`: `(1,0,1)`;
5. `renew_double`: `(1,2,1)`;
6. `bank_zero`: `(1,1,0)`; and
7. `bank_double`: `(1,1,2)`.

Write and hash the catalog before execution. Run all seven policies over four maps, both seats, and
all eight frozen macro opponents: 448 complete games. Repeat the exact matrix independently with
20 threads and sort rows by `(policy, map_seed, seat, opponent)`.

## Frozen gates

D48a passes only if all hold:

1. both 7 x 64 grids are complete, finite, and byte-identical;
2. `anchor` has exact parity with the corresponding D40 reference prefix in every terminal,
   action-plane, action-hash, and state-hash field;
3. every row has zero illegal-command, provenance, relevant-deposit-prediction, worker-cap,
   reward-identity, action-count, or decision-loop failure;
4. for each of provenance, renew, and bank, at least one zero/double direction changes action hash
   in 5%--95% of tasks, and at least four of all six directions lie in that corridor;
5. perturbation mean margins span at least 15 points and include at least one value above and one
   below the anchor mean;
6. at least four perturbations retain worker two in at least 90%, worker three in at least 50%, and
   crop creation in at least 60%; and
7. at least two of the three zero/double pairs differ in mean margin by at least two points.

## Decision rule

A conjunction pass opens a separately frozen D48b whole-game cross-entropy search on fresh common
maps. Its initial center is `(1,1,1)`, not a D48a arm; population, covariance, bounds, seed banks,
objective, racing, validation, and confirmation must be fixed before outcomes are opened. D48a
outcomes may not choose the initial mean, scale, bounds, or a coordinate subset.

A failure closes this exact three-scale surface. Do not add a phase/worker interaction, choose the
best descriptive arm, alter 0/2 perturbations, or fit on these consumed maps.
