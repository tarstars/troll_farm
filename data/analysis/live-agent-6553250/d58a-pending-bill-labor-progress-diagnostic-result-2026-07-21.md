# D58a pending-bill labor/progress diagnostic — result (2026-07-21)

## Verdict

**Close source investment while only two workers exist and advance to a labor-preserving
materialization representation.** Relative to transaction-correct V5, both V6 and V7 shift more
pending worker-time into MOVE/PICK/PLANT, less into DROP/HARVEST/MINE, and realize less net exact
bill progress per worker-turn. All three frozen decision predicates hold.

This is consumed-map telemetry only. It does not evaluate value/support or authorize a candidate,
TestSession, submission, or Arena action.

## Integrity

- Each diagnostic matrix contains 1,280 unique complete cells.
- Every pre-existing field matches its pinned V5/V6/V7 A matrix exactly; common-field mismatches
  are zero for all 3,840 cells.
- Pending action counts sum exactly to pending worker-turns in every row.
- Completion exclusion, progress partitions, minimum-vector ordering, worker-two invariance, and
  every TRAIN partition are exact with zero failures.
- Runs complete in 17.85--19.40 s at 19.49--19.67 effective CPU cores.
- Twenty-three runner tests and one diagnostic-analyzer test pass.

## Labor and progress

| Policy | Worker 3 | Pending worker-turns | MOVE+PICK+PLANT | DROP+HARVEST+MINE | Net units / worker-turn |
|---|---:|---:|---:|---:|---:|
| V5 | 324 | 447,992 | 66.94% | 33.02% | **0.00847** |
| V6 | 304 | 478,376 | 69.48% | 30.48% | 0.00759 |
| V7 | 272 | 465,800 | **69.91%** | **30.08%** | **0.00585** |

V6 adds 30,384 pending worker-turns versus V5, led by +22,522 MOVE, +7,668 PICK, and +2,260
PLANT actions while losing 3,840 HARVEST actions. V7 adds 17,808 worker-turns, +20,268 MOVE and
+5,488 PICK actions, while losing 7,002 HARVEST and 1,268 DROP actions. The source controllers
remain pending longer because their extra activity does not complete the bill faster.

## Action conversion

- MINE is the only near-immediate progress action: the next state reduces total deficit after
  98.77% of V5, 96.98% of V6, and 96.36% of V7 MINE-observed turns.
- V5 PLANT is followed by progress on 2.05% and regression on only 0.38% of observed turns because
  ordinary planting generally uses nonreserved stock.
- Targeted source PLANT is followed by regression on 8.63% of V6 and 7.14% of V7 observed turns,
  versus progress on 2.46% and 1.99%. It consumes a current bill unit before its future fruit cycle
  can repay it.
- MOVE dominates all policies (56.56--58.75% of worker-time) but is followed by immediate deficit
  progress on only 1.75--2.82% of observed turns. V6/V7 add roughly twenty thousand MOVE actions
  without improving completion.
- PICK preserves total post-stock quantity by moving a unit from deposit to carry; it is not
  capitalization. Its additional share therefore increases travel/banking work without making the
  bill affordable.

## Coordinate conversion

Among trajectories still blocked at worker two, terminal mean deficits are:

| Policy | PLUM | LEMON | APPLE | IRON |
|---|---:|---:|---:|---:|
| V5 | 1.142 | 3.536 | 0.000 | 0.678 |
| V6 | 1.154 | 3.654 | 0.000 | 0.622 |
| V7 | **1.883** | **4.434** | 0.031 | **0.020** |

V7's exact allocator nearly solves IRON because mining converts immediately, but its fruit
investment leaves larger PLUM and LEMON gaps than the V5 baseline. This cleanly separates two job
types: fixed-source extraction is productive; consuming currency to build a delayed renewable
source is not affordable with only two workers under this bill.

## Next constraint

D59 may test one coefficient-free materialization-first job lease while worker three is pending:
bank carried bill currency, keep each worker on a distinct currently existing fruit/IRON source
until harvest/mine completion or invalidation, and prohibit PLANT/PICK investment in that phase.
Outside the exact two-worker pending state, behavior must remain V5. The lease must be defined by
natural job boundaries, not a fitted turn horizon, distance weight, source floor, or resource
coefficient.

This is the last eligible interpretation of the D56-D58 source family. If labor-preserving leases
remain active but fail workforce, close source/materialization hand rules and move to a different
controller representation rather than tuning jobs on these maps.

## Evidence

- protocol SHA-256:
  `4e66064ecbb2d97c93ecb179fd3b9283b0c252417443cb4f1ec62b592e7ee99b`;
- V5/V6/V7 diagnostic matrix SHA-256:
  `a2f44c821b94382e5ba67f086977153903f9efd98b973e21271df3468b98c0f8`,
  `771638f409639d74294d0ef7812f328c694ef2a2c0667fbbafaaec526bd8bbdd`, and
  `bdd98ea34abd2208fb5c03c6c4f81dd3c1d8c89f0b55410ecc674e28602a3128`;
- result SHA-256:
  `c75325a23c37b042c109346b4145ef62eec29514de28e2004f3bbd6c008370c5`;
- runner SHA-256:
  `bbfd6a0732cf2d531d359247f33b41b508c9d37b71e46a7531a4f301aa45519d`;
- unchanged V7 strategy SHA-256:
  `394548bc6000826d1d2cdcc12cda1c696ad1c92ca15c525626d872e9c5448309`;
- analyzer SHA-256:
  `6ff54c06a4ade44e69787f9696891f050c0742a4e4e6fefef6743a68f8c9d1dc`.
