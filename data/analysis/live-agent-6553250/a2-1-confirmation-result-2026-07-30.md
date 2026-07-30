# A2-1 confirmation — FAILED K1

The first new Architecture-2 policy establishes and reaps its own orchard, banks the
proceeds, and mines opportunistically, but does not convert that economy into worker 3
often enough. The locked confirmation reaches **582/2,048 = 28.418%** fruit-funded
worker 3 by post-step turn 110, below the frozen **40%** gate.

This is a clean scientific failure, not an execution or evaluator block. Per the charter's
amended K1, the Architecture-2 programme stops here. There is no candidate and no Arena
action.

## Lock and confirmation integrity

- implementation commit:
  `2357ec672c971a23f8225ce63f8f1ff4c9214913`;
- remotely published lock:
  `data/analysis/live-agent-6553250/a2-1-implementation-lock.json`;
- confirmation matrix: seeds `9,881,000–9,881,127` × two seats × eight families =
  2,048 tasks;
- terminal rows: 2,048/2,048;
- one-thread runtime: 149.187 seconds;
- 20-thread trajectory runtime: 17.892 seconds;
- one-thread and 20-thread TSVs are byte-identical, SHA-256
  `efd793552a9a535de94a9429eb73fc82db69e11eaf282e83a8ef5ccc2cffe2fa`;
- 2,048 trajectory records decode with exact coverage, SHA-256
  `bb20af96dc785bd3626e0996c035858bc8ba20ca1ba2c168053259541a47a4c2`;
- locked source, binary, A2-0b substrate, module registry, and resident hashes remained
  exact.

## Gate table

| gate | observed | verdict |
|---|---:|---|
| C1 exact terminal 128 × 2 × 8 matrix | 2,048/2,048 | PASS |
| C2 fruit-funded worker 3 by turn ≤110 | 582/2,048 = **28.418%**; floor 40% | **FAIL — K1** |
| C3 unambiguous own crop reap and bank | 128,979 harvested; 127,614 banked | PASS |
| C4 scaled opportunistic mining | 755 iron at roster 2; 840 at roster 3+; 0 iron moves | PASS |
| C5 policy command quality | 198/1,365,709 = 0.0145%; allowed reason only | PASS |
| C6 one/20-thread byte identity | same TSV SHA | PASS |
| C7 lock/range/task/fresh-instance integrity | exact | PASS |
| C8 all-six detector bridge | exact coverage; repeated failures 0 | PASS |

All 198 A2-owned issues are source-defined `opponent_plant_blocking` events in one
simultaneous-plant task. Critical and unclassified issues are zero globally. The
policy-owned issue-bearing task rate is 1/2,048.

## Mechanism and transfer

The 32-map development block narrowly passed at 206/512 = 40.234%; confirmation falls by
11.816 percentage points to 28.418%. This is not a single-family accident:

- family rates span only 27.344%–31.250%;
- seat 0: 26.953%;
- seat 1: 29.883%;
- 769 tasks eventually train worker 3, with median post-step turn 37, but only 582 do so
  by the deadline with prior unambiguous own-fruit banking;
- the conservative `bill_needs_owned_fruit` diagnostic is true in 542 tasks.

The scheduler therefore proves the individual operations and a partial economy, but the
fresh-block transfer rate is below the level needed to justify Phase 2.

## Detector and descriptive value record

All standing detectors executed:

| detector | episodes | flagged turns |
|---|---:|---:|
| door_queue | 82,420 | 84,459 |
| harvest_slack | 68,772 | 797,392 |
| idle_with_work | 266,535 | 598,806 |
| late_train_window | 185 | 3,881 |
| repeated_failed_command | 0 | 0 |
| unbanked_carry | 2,941 | 266,736 |

Phase 1 does not gate on value, but the descriptive result is also far from a candidate:
mean own score 93.14, mean opponent score 206.25, mean margin −113.11, 1,368
catastrophes, and 247,718 negative-margin mass.

## Verdict and stop rule

**FAILED_K1.** Stop Architecture-2 at Phase 1. Do not retune the crop-service threshold,
worker spec, deadline, planting catalog, or mining quota on these consumed ranges. A future
reopening would require an owner-authorized new programme, a materially different
closed-loop representation, a new protocol, and fresh ranges.

Canonical machine record:
`data/analysis/live-agent-6553250/a2-1-confirmation-result.json`, SHA-256
`78f62e1e09ad323f7aa6025b266a5a966714dbf2250a15bb7bc5f3c35eebf241`.
