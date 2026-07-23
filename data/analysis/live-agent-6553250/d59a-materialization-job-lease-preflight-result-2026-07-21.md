# D59a materialization job-lease preflight — corrected result (2026-07-21)

## Verdict

**Close hand-designed source/materialization workforce jobs on this substrate.** The V8 lease is
deterministic, broadly active, transaction-correct, and more efficient at reducing the exact bill,
but it reaches worker three in only 308/1,280 cells (24.06%) versus V5's 324 (25.31%). Existing
sources are too sparse to keep both workers productive without the delayed source investment that
D56-D58 already rejected.

No support, score direction, candidate value, TestSession, submission, or Arena conclusion is
opened.

## Corrected mechanical gate

The first analyzer counted 202 PICK and 36 PLANT commands on affordable TRAIN-completion turns as
if they came from the non-affordable lease branch. Per the frozen design, V8 exits the lease on
those turns and exactly reproduces V5. The first JSON is quarantined.

A written amendment added completion-action counters without changing strategy or thresholds. The
corrected A/B runs reproduce every original D59 field exactly, all 616 completion-turn worker
actions partition exactly, and the 202 PICK/36 PLANT commands are entirely on completion turns.
The actual lease branch contains zero PICK and zero PLANT commands.

## Integrity

- Corrected exact 160 x 8 matrices are complete and byte-identical.
- All 468 parent-conditioned opening commands/specs match; cap violations are zero.
- Worker-two reach matches D54 exactly in every config.
- Every TRAIN and pending-progress partition is exact; budget-inclusive and unexplained TRAIN
  failures are zero.
- All 308 worker-three and five worker-four TRAIN attempts succeed.
- V8 changes 1,056/1,280 complete trajectories relative to V5.
- Corrected runs complete in 16.04 s and 16.95 s at about 19.15 effective CPU cores.
- Sixteen strategy tests, twenty-four runner tests, and one D59 analyzer test pass.

## Labor mechanism

| Policy | Worker 3 | Mean pending turns | Idle share | Capitalization share | Net units / worker-turn |
|---|---:|---:|---:|---:|---:|
| V5 | 324 | 175.00 | 0.01% | 33.02% | 0.00847 |
| V8 | 308 | **152.50** | **55.65%** | 6.82% | **0.01128** |

The natural-boundary lease raises exact progress efficiency by 33.14% and shortens pending time by
22.49 turns on average. It nearly closes IRON (mean final deficit 0.019 versus V5's 0.388) and
reduces LEMON to 1.769 versus 2.022 across all cells. However, when a required existing source does
not exist or is exhausted, the no-investment rule intentionally waits: 217,256 pending worker
actions are idle. Crop coverage falls from 100% to 956/1,280 (74.69%).

The transition is heterogeneous: V8 promotes 138 V5 trajectories and demotes 153, losing 20
workers net. hp2 improves worker-three reach slightly from 44/160 to 45/160 per config, while
balanced falls from 37/160 to 32/160. This is not an inert or universally dominated rule; it exposes
the structural tradeoff between current capitalization and future source availability.

## Workforce result

| First worker | Worker 2 | Worker 3 |
|---|---:|---:|
| hp2 | 130/160 (81.25%) | 45/160 (28.13%) |
| balanced | 134/160 (83.75%) | 32/160 (20.00%) |

Only hp2/max-four reaches worker four: three cells with one retained producer and two with two.
Every worker-two, worker-three, worker-four, and crop threshold remains below the frozen gate.

## Multilevel conclusion

- **Transaction:** solved and closed since D54.
- **Commodity identification:** solved enough to activate source changes, but source specialization
  and exact-vector allocation both reduce workforce.
- **Labor conversion:** materialization leases improve progress per action, proving that immediate
  banking/harvest/mining is useful, but cannot manufacture missing sources and therefore strand
  over half of scarce labor.
- **Representation limit:** a fixed hand rule must choose between delayed renewable investment and
  immediate bill materialization. D56-D59 cover both extremes and their exact vector/lease bridge;
  none approaches the absolute workforce gate.
- **Closure:** do not tune floors, leases, target order, producer counts, worker specs, or gates on
  these consumed maps. The next iteration must use a different controller representation that can
  optimize the investment/materialization sequence over whole-game return.

## Evidence

- protocol SHA-256:
  `79e35939cdffb71521e8d06e593fac2733d661389572d76e14a7d5020da4ce8b`;
- completion-turn amendment SHA-256:
  `705fa35e75c5235c09e8252c9fdcd4ada09e1fa9911dfd330e2dbe8fd86fea1f`;
- corrected repeated matrix SHA-256:
  `d89c34e653e9188cffcbbc3120c5353dfed091d146a0bf67c1c13e6a20030f0b`;
- corrected result SHA-256:
  `c2053064dc26f2bbaf73d4486238da2ab8d7cbcde4de334f2887c4fa6da4dc93`;
- runner SHA-256:
  `631ff64f65319762a12929f9f9708cd452e08d9d4117bf8aefb156af643fad9e`;
- V8 strategy SHA-256:
  `8334d99b0dcb5d508c02329e91e68af0cccfb8115244249d2f227be8fb322a73`;
- corrected analyzer SHA-256:
  `a081b89fec512f205b63709462a54dc5d3a7fe559b73214ce539117e014483a8`.
