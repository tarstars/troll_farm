# D57a exact post-stock deficit-vector preflight — result (2026-07-21)

## Verdict

**Reject the exact vector allocator before support and diagnose labor-time conversion.** V7 is
deterministic, highly active, transaction-correct, and exactly isolated from the worker-two layer,
but reaches worker three in only 272/1,280 cells (21.25%) and worker four in 2/640 eligible cells
(0.31%). Both are worse than V5's 324 and nine.

No score, support, candidate value, TestSession, submission, or Arena conclusion is opened.

## Integrity and invariance

- Both exact 160 x 8 matrices are complete and byte-identical.
- All 468 parent-conditioned opening TRAIN commands/specs match; cap violations are zero.
- Worker-two reach is exactly unchanged in every config: 130/160 for hp2 and 134/160 for balanced.
- Every TRAIN-attempt partition balances. Budget-inclusive and unexplained failures are zero.
- Worker three succeeds on all 272 attempts and worker four on both attempts; the allocator does not
  recreate the repaired transaction bug.
- V7 changes 988/1,280 complete trajectories relative to V5, so the branch is not inactive.
- The two runs complete in 18.56 s and 19.49 s at 19.59 and 19.58 effective CPU cores.
- Twelve strategy tests, twenty runner tests, and two D57 analyzer tests pass.

## Workforce result

| First worker | Worker 2 | Worker 3 |
|---|---:|---:|
| hp2 | 130/160 (81.25%) | 37/160 (23.13%) |
| balanced | 134/160 (83.75%) | 31/160 (19.38%) |

The cap and post-producer variants remain identical through worker three. The two hp2/max-four
configs each reach worker four once; neither balanced/max-four config does. Crops remain universal
and 1,056/1,280 signatures differ from the V2 parent, but all worker-two, worker-three, and
worker-four gates fail.

Against V5, V7 promotes 53 trajectories, demotes 110, and loses 59 workers net. Against V6 it
promotes 102, demotes 134, and loses 32 workers net. The policy is changing which maps complete the
bill rather than being uniformly dominated cell by cell, but its aggregate conversion is worse.

## Resource result on the frozen D55 blocked cohort

| Species | Successful-plant delta | Harvest delta |
|---|---:|---:|
| PLUM | +508 (+0.694/cell) | -711 (-0.971/cell) |
| LEMON | +1,464 (+2.000/cell) | +1,282 (+1.751/cell) |
| APPLE | -213 (-0.291/cell) | -2,538 (-3.467/cell) |
| BANANA | -2,628 (-3.590/cell) | -9,104 (-12.437/cell) |

The exact vector does broaden source construction beyond LEMON, but added sources do not imply
timely harvested/deposited currency. PLUM sources rise while PLUM harvest falls; LEMON harvest gains
are outweighed by large losses in the ordinary production loop. This is labor opportunity cost and
maturation timing, not another resource-identification error.

## Multilevel interpretation

- **Transaction:** remains solved. All later-worker TRAIN commands execute when issued.
- **State representation:** deposited + carry + ripe stock is sufficient to activate distinct
  PLUM/LEMON/IRON coordinate choices in tests and 77.19% of field trajectories.
- **Allocation:** assigning scarce producers to missing coordinates is not enough. A source-build
  action can increase future capacity while making no immediate bill progress, and repeated
  reassignment consumes the harvest/bank cycles that capitalize that source.
- **Workforce:** the binding event is still bill affordability, but D56-D57 show that more correctly
  typed trees alone can reduce it. The next diagnostic must measure pending-bill worker-turns,
  command mix, and realized coordinate progress over time rather than add another source rule.
- **Closed branch:** fixed LEMON floors and this exact post-stock allocator are both closed. Do not
  tune source floors, resource weights, producer counts, worker specs, or workforce thresholds from
  these consumed outcomes.

## Next constraint

D58 may add telemetry only and rerun unchanged V5/V6/V7 controls on the same maps. It should
partition worker-three pending time into source investment, harvest/mine, bank, movement, fallback,
and idle worker-turns; track the exact post-stock deficit vector before/after decisions; and report
which action classes produce durable bill progress. No new policy treatment is eligible until that
diagnostic identifies the failed conversion layer.

## Evidence

- protocol SHA-256:
  `8c45e8bf82b17130d1d2303d2bfad5a68dec2c0327fe8e2f7c09f662e02168f0`;
- repeated matrix SHA-256:
  `58382e713123931f207d37c539bd96a7a7a9e53f1243f577ea88968ad14f7704`;
- result SHA-256:
  `5f3ad4745d2012d40289733e007c0a909a29c75920122a38ddc0ede152959eda`;
- runner SHA-256:
  `b634af9d3cb3d2240c562a21ab3c6ab3f942f1ae9f8367642a2598a6cfccf552`;
- V7 strategy SHA-256:
  `394548bc6000826d1d2cdcc12cda1c696ad1c92ca15c525626d872e9c5448309`;
- analyzer SHA-256:
  `8e5cc85fce285817dcc32d0f77db8eef7d6bae799f11eb856d75ea126a3466ff`.
