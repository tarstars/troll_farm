# D59a completion-turn command-gate amendment (2026-07-21)

## Mechanical ambiguity

The first D59 analyzer invocation stopped the conjunction because aggregate two-worker telemetry
contained 202 PICK and 36 PLANT commands. Inspection of the frozen control flow identifies a gate
boundary mismatch: D58's `pending3_action_*` counters include the affordable TRAIN-completion turn,
but the D59 lease treatment is defined only while the bill is **not affordable**. On an affordable
turn V8 must leave the lease and reproduce exact V5 commands, which may PICK or PLANT surplus in
the same command bundle as TRAIN.

The focused affordable-bill unit test passes exact V5 equality, and every 308 worker-three TRAIN
attempt succeeds. Therefore the aggregate counter cannot test the stated non-affordable lease
invariant. This is telemetry ambiguity, not evidence that the lease branch issued PICK/PLANT.

## Frozen correction

Before interpreting any workforce, crop, labor, or transition field from the first analyzer
output:

1. retain the raw A/B matrices and first JSON as quarantined evidence;
2. add per-action completion-turn counters inside the existing D58 pending telemetry;
3. require completion action counts to sum to exactly two actions per successful worker-three
   completion turn;
4. apply the zero PICK/PLANT gate to
   `pending action count - completion-turn action count`; and
5. rerun unchanged V8 twice, requiring every prior D59 field to reproduce the original A matrix
   exactly after excluding only the new completion columns.

No strategy code, config, threshold, map, command, or outcome rule may change. The corrected result
must use a new path and pin this amendment. Only after all corrected mechanics pass may the already
frozen workforce conjunction be read.

## Quarantine evidence

- original A/B matrix SHA-256:
  `5ab3816fa573582cd69e940a83e8d1fd062ba4418fe39aca4c366d03ef943d43`;
- first analyzer JSON SHA-256:
  `7df86a1bd6dd2784df315d27300586f90d87cc6251031b0ed07875ed894ed897`;
- first analyzer source SHA-256:
  `9fc4cdbc6b5c88ee21e0e31184f2c34c449a04dd86bf946ecf8d52f47d93a293`;
- unchanged V8 strategy SHA-256:
  `8334d99b0dcb5d508c02329e91e68af0cccfb8115244249d2f227be8fb322a73`.
