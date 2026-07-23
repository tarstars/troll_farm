# D59a materialization job-lease preflight — frozen protocol (2026-07-21)

## Question

D58 finds that targeted source investment adds pending worker-time, reduces capitalization share,
and lowers exact bill progress, while fixed-source MINE converts almost immediately. Can a natural
job-boundary lease preserve scarce two-worker labor long enough to materialize the existing
PLUM/LEMON/APPLE/IRON stock into the hybrid worker-three bill?

## Frozen V8 treatment

Create `LegendFieldProxyV8` with the same eight configs and exact V5 behavior outside the state
`current workers == 2`, worker three is allowed by the configured cap, and its hybrid bill is not
yet affordable. Opening, affordable-bill execution, post-worker-three behavior, specs, caps,
transaction reservation, and shared PICK ledger remain V5.

Inside that exact pending state:

1. recompute deposited bill deficits every turn;
2. any worker carrying items banks immediately by the unchanged shortest home command;
3. empty workers retain a lease `(resource, target)` until the deposited deficit closes, the target
   disappears, or the target job completes;
4. on a new lease boundary, order positive bill coordinates by descending deposited deficit then
   stable resource index, and assign distinct coordinates to workers in the unchanged V3 producer
   rank;
5. for fruit, target the nearest existing matching plant, preferring currently ripe plants before
   unripe plants; move to it, HARVEST when ripe and standing on it, and wait there when it is not
   ripe;
6. for IRON, target the nearest legal adjacent mining cell, move to it, and MINE when adjacent; and
7. if no matching existing source is reachable, issue no unit command for that worker rather than
   PLANT, PICK, CHOP, or switch to a different non-bill job mid-lease.

Clear leases when leaving the exact pending state. Reservation prevents two workers selecting the
same target. There is no turn horizon, travel weight, source floor, resource multiplier, outcome,
score, or opponent identity. The only persistence boundary is the validity/completion of the
assigned job.

Cross hp2/balanced first spec, cap three/four, and one/two retained post-workforce producers for
exactly eight V8 configs. No definition may change after execution.

## Verification before execution

Unit tests must prove:

- useful carried currency banks before any lease;
- two workers receive distinct existing source coordinates;
- a valid unripe target remains sticky across a changed nearer alternative and becomes HARVEST
  when ripe;
- PLANT and PICK are absent throughout the pending materialization branch; and
- affordable worker-three bills bypass leases and exactly match V5 commands, including TRAIN.

The runner must expose eight unique V8 configs, include V8 in stock-flow telemetry, and retain D58
pending-labor counters.

## Execution and gates

Run exact `b100_e6` as player 0 against all eight V8 configs on the same 160 consumed maps, twice
with 20 threads. Retain every D54 transaction gate and every original D52 workforce, crop,
activation, opening, cap, completeness, and repeat gate. Additionally require:

- worker-two reach exactly 130/160 for every hp2 config and 134/160 for every balanced config;
- zero pending worker-three PLANT commands and zero pending worker-three PICK commands; and
- exact pending action/progress partitions from D58.

Compare pending labor shares, net progress per worker-turn, and exact workforce transitions to V5
descriptively. Do not lower absolute workforce thresholds or select a config from consumed results.
Ignore score direction, support, distance, cohorts, opponent identity, policy value, and platform
outcomes.

Frozen evidence includes D58 result SHA-256
`c75325a23c37b042c109346b4145ef62eec29514de28e2004f3bbd6c008370c5`, D58 V5 matrix SHA-256
`a2f44c821b94382e5ba67f086977153903f9efd98b973e21271df3468b98c0f8`, D57 result SHA-256
`5f3ad4745d2012d40289733e007c0a909a29c75920122a38ddc0ede152959eda`, the observed/map pair
`c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
`d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`, and V2 parent SHA-256
`2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b`.

## Decision rule

- **Full pass:** freeze V8 and specify a separate consumed-map support audit.
- **Transaction, invariance, or pending-command-integrity fail:** reject before workforce
  interpretation and repair only the exact regression.
- **Broadly active but workforce fail:** close hand-designed source/materialization workforce jobs
  on this substrate and move to a different controller representation; do not tune leases,
  resource order, specs, caps, or gates.
- **Inactive:** trace lease validity/target availability only; do not read support/value.

No fresh map, candidate generation, TestSession game, submission, Arena action, or resident change
is authorized.
