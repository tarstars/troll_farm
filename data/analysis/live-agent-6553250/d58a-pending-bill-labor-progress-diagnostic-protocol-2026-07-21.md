# D58a pending-bill labor/progress diagnostic — frozen protocol (2026-07-21)

## Question

V6 and V7 both create more correctly typed sources while completing fewer later-worker bills than
transaction-correct V5. Is the failed conversion caused by scarce two-worker time being moved from
harvest/bank capitalization into source investment and movement, or by a different exact bill
coordinate that never progresses?

This is telemetry-only diagnosis. It cannot revive V6/V7, change a policy, inspect score/support,
or authorize a candidate/platform action.

## Frozen telemetry

Without changing V5, V6, V7, candidate behavior, maps, or simulation order, instrument every turn
on which the modeled opponent has exactly two workers and the hybrid worker-three bill remains the
next target.

For each trajectory record:

1. pending turns and pending worker-turns;
2. issued worker-actions by mutually exclusive parsed class: MOVE, PICK, DROP, PLANT, HARVEST,
   MINE, CHOP, and IDLE;
3. the exact post-stock deficit vector before and after each non-completion turn, where stock is
   deposited inventory + all own carry + currently ripe matching fruit (IRON has no ripe stock);
4. counts of non-completion turns on which summed deficit decreases, stays equal, or increases,
   plus cumulative reduced and increased units;
5. for each action class, the number of observed pending turns and the subset followed by a summed
   deficit decrease or increase; and
6. initial, minimum, and last pre-completion deficit by PLUM, LEMON, APPLE, and IRON.

The completion turn counts toward labor allocation but is excluded from post-payment deficit
progress, because TRAIN consumes the bill. Parsed commands are counted whether or not their game
effect succeeds; existing event telemetry retains successful plants/harvests and exact TRAIN
outcomes. No score or reward enters any counter.

## Execution and integrity

Run unchanged V5, V6, and V7 catalogs once each on the same 160 consumed exact maps with 20
threads: 3,840 cells total. Require:

- exactly 160 x 8 unique complete rows per family;
- every pre-existing V5/V6/V7 field to match its pinned A matrix exactly after excluding only the
  new D58 columns;
- exact TRAIN-attempt partitions and the already-established worker-two counts; and
- pending action counts to sum exactly to pending worker-turns in every row.

The runner tests must cover deficit construction, mutually exclusive action counting, completion
exclusion, and per-class progress association.

## Analysis

For each family and separately for trajectories that do/do not reach worker three, report:

- pending turns and worker-turns;
- action-class shares;
- successful plant/harvest species totals;
- deficit-decrease/equal/increase rates and net cumulative unit progress;
- per-class next-state progress/regression rates; and
- initial-to-minimum and initial-to-last progress for each bill coordinate.

Use exact paired V5→V6 and V5→V7 differences on corresponding game/config cells. Report medians
and means; do not fit a model, threshold, or resource weight.

Frozen evidence includes V5 matrix SHA-256
`66f99af783e855fc64e48df3990bf04469fe1dea07798ede6b95a4fea17a1263`, V6 matrix SHA-256
`90ac87e0f5140192bafb346d161a116d84821fa317f3b6d30880acc9b443a912`, V7 matrix SHA-256
`58382e713123931f207d37c539bd96a7a7a9e53f1243f577ea88968ad14f7704`, D57 result SHA-256
`5f3ad4745d2012d40289733e007c0a909a29c75920122a38ddc0ede152959eda`, the observed/map pair
`c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
`d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`.

## Decision rule

- If V6/V7 shift labor toward PLANT/PICK/MOVE and reduce realized progress or capitalization
  relative to V5, close source investment while only two workers exist and select a separately
  frozen labor-preserving representation.
- If source policies improve exact-vector progress but fail at DROP/materialization, select a
  separately frozen materialization-first representation.
- If one coordinate remains dominant despite equal labor efficiency, select a diagnostic specific
  to access/travel for that coordinate—not another source floor.
- If integrity fails, repair telemetry only and reread no diagnostic outcome until it passes.

No new policy treatment, fresh map, candidate generation, TestSession game, submission, Arena
action, or resident change is authorized.
