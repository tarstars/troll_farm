# D38 TRAIN-deficit complete-macro teacher — result (2026-07-21)

## Verdict

**Reject and close the deficit-only teacher before behavior cloning or PPO.** The two teacher runs
are byte-identical, but the policy loses **26.215 mean paired margin** to random, trains worker two
in only **37.50%**, misses the worker-three gate at **14.45%**, regresses seven of eight opponent
families, and violates the frozen deposit-prediction integrity check. No model, candidate,
TestSession, submission, or Arena action is authorized by D38.

## Accepted panel

All accepted rows were regenerated after the pre-data transactional scheduler correction recorded
in the protocol. Each arm contains the complete 16-seed x 2-seat x 8-opponent = **256-cell** grid
for official seeds 9,630,000--9,630,015. There are zero missing/duplicate keys, policy errors,
margin/return identity errors, invalid direct commands, provenance failures, worker-cap errors,
empty episodes, action-count errors, or runner decision loops.

Teacher replicas A and B are byte-identical:
`1f07779f6c3395a0e8b54a77b64145972bfcb0b5ecd4a03362a5803c2e2b363f`.

The initial random attempt exposed D37's discarded-command mutation bug at seed 9,630,006, seat 1,
`gold_adaptive`, turn 300. That attempt produced no control file; concurrent teacher rows were
invalidated. The executor now rolls back every nonfinished job mutation when a completion creates
a zero-time boundary, and the exact episode is a regression test. This correction changes
historical D37 executor hashes but is shared by every accepted D38 arm.

## Outcome

| metric | deficit teacher | random control | teacher minus random |
|---|---:|---:|---:|
| mean own score | 55.500 | 74.340 | -18.840 |
| mean opponent score | 209.656 | 202.281 | +7.375 |
| mean margin | -154.156 | -127.941 | **-26.215** |
| worker-two rate | 37.50% | 64.45% | -26.95 pp |
| worker-three rate | 14.45% | 7.03% | +7.42 pp |
| own renewable-crop rate | 85.94% | 98.44% | -12.50 pp |
| median non-idle jobs | 6 | 29 | -23 |
| catastrophes (margin <= -100) | 168 | 141 | +27 |
| negative-margin mass | 42,453 | 33,953 | +8,500 |

Only 65/256 paired cells improve, two tie, and 189 regress. Family paired-margin advantages are:

- `compact_gold` +9.563;
- `mybot` -13.094;
- `script_boss` -24.438;
- `silver_boss` -26.719;
- `legend_balanced` -30.531;
- `resident` -34.563;
- `gold_adaptive` -43.844; and
- `norx_native_three` -46.094.

Only one family is nonnegative and the minimum is -46.094, failing both family gates.

## Mechanism diagnosis

### 1. The dominant blocker is shack occupancy, not an expensive TRAIN bill

The exact initial-state audit accounts for the 37.50% worker-two rate without residual error.
Every game starts with the sole worker standing on its shack, where the referee forbids TRAIN.

- Ten of 16 maps already have enough inventory for producer `(2,2,1,1)`. Their resource deficit is
  zero, so the frozen teacher selects `IDLE_ONE_TURN`; the worker stays on the shack and **all
  160/160 opponent cells finish with one worker**.
- Six of 16 maps have a positive resource deficit. A resource job eventually moves the starter off
  the shack and **all 96/96 cells train worker two**.

Thus the teacher's rule “covered bill but not affordable => idle” confuses resource coverage with
the independent physical precondition that the spawn cell must be vacated.

### 2. Exact-deficit myopia destroys useful work while waiting

The teacher selects **55,873 idle jobs**, versus 1,122 for random. Its 160 one-worker episodes
average 269.2 idle jobs, only 3.48 non-idle jobs, and -215.87 margin. When a missing fruit is not
currently harvestable or an active job is expected to cover it, the controller refuses surplus
harvest, renewable supply, wood conversion, or positional work. The deficit rule therefore turns
temporary source unavailability into near-total inactivity.

The 37 episodes that do reach three workers have +69.97 mean margin and 75.30 mean non-idle jobs.
This is selection-biased rather than a causal estimate, but it reinforces that workforce growth is
valuable once the controller clears its structural blockers.

### 3. Full-vector deposit equality is invalid for persistent felling

The integrity gate records **120 teacher** and **36 random** deposit-prediction failures. A focused
trace finds every sampled mismatch in `FELL_BANK`. On seed 9,630,008, all 47 failures are wood-yield
changes: 35 predict one wood and deposit two; 12 predict two and deposit one. Plants can grow while
the worker travels/chops, and opponents can share or alter the eventual fell yield. Selection-time
wood is therefore not an exact future deposit. Wood is irrelevant to TRAIN, so future reservation
should validate only training-currency slots or use conservative yield bounds rather than asserting
full-vector equality.

## Frozen gates

Passed:

- byte-identical teacher repeat;
- renewable-crop rate >=60%; and
- median non-idle jobs >=4.

Failed:

- teacher and random integrity (deposit prediction mismatches);
- mean paired margin advantage >=+50;
- worker-two rate >=80%;
- worker-three rate >=15%;
- at least six nonnegative opponent families; and
- no opponent family below -10.

## Next hypothesis

D39 should remain coefficient-free but separate TRAIN's two prerequisite classes:

1. if the current free worker occupies the shack, assign the shortest legal non-idle job so its
   first command evacuates the spawn cell;
2. otherwise retain D38's exact outstanding-resource ordering;
3. validate deposit predictions only on PLUM/LEMON/APPLE/IRON, the slots that can fund TRAIN; and
4. compare the evacuation-aware teacher against both a same-seed D38 ablation and random on a fresh
   official panel.

This is a narrow structural correction, not PPO training and not a submission candidate.

## Reproducibility

- protocol: `4be0b6a53bf7f823fa1ca7be87f4c591258e445d4fd370206ed46842189a7df1`
- macro environment: `70d919022e8d221fdd840ccccf52a9081923a98c09ee8089702023c0cfd1a157`
- panel runner: `8dc033c86074c56fe791cc4eb2a69992a7db5dcc597589f01e3ab79c208c4094`
- analyzer: `a83b21d0057972dc233483bf07d0b74a015f9cc0d98b0d0b760855e247e03c74`
- analyzer tests: `a56c255adef211e61d86e41156a20601c1bfedb41f5758a7930119116743506b`
- random rows: `f9c8a70f3df8a630fb6cf33618a9a9272945ade60782c51f90f852141f98ab86`
- blocker audit: `af8a5588aacf2fbce4583e221e03cb8f0ebd761202cf34b4d5a29d562da532fb`
- analyzer JSON: `2bfb5b3443301482f40aa5ce0dd9aea7915eca7e4719d51fe69ab92bafa8ff6a`

Focused verification: eight Rust macro tests and five D38 analyzer tests pass. Existing unrelated
compiler warnings remain unchanged.
