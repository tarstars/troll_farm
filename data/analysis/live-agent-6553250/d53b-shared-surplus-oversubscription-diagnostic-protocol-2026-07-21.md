# D53b shared-surplus oversubscription diagnostic — frozen protocol (2026-07-21)

## Question

D53a's per-worker reservation removes every worker-two budget failure but leaves 168 budget-only
worker-three failures. Since one worker may PICK a TRAIN currency only when inventory is strictly
above the exact bill, can every residual failure be explained by multiple workers independently
spending the same shared surplus before TRAIN?

## Frozen telemetry replay

Keep the V4 strategy and eight configs byte-unchanged. Extend only the audit runner's cloned
pre-TRAIN simulation to record, by target workforce:

- total successful PLUM/LEMON/APPLE/IRON PICKs on failed TRAIN attempts;
- failed attempts containing at least two successful TRAIN-currency PICKs; and
- failed attempts where, for at least one resource, successful PICK count exceeds
  `max(inventory_before_PICK - exact_bill, 0)`.

Replay one exact 160 x 8 matrix with 20 threads on the same consumed maps. Excluding new telemetry,
all fields must reproduce D53a A exactly. Existing attempt/failure partitions must remain exact.
Score, support, distance, cohort, opponent, policy-value, and platform fields are ignored.

Frozen inputs:

- D53a A SHA-256
  `d378288dd24b992a027583ae6270fbff358311f34b8da666a5241880347c021b`;
- unchanged V4 strategy SHA-256
  `cf5cdb1df23033f88f465a8213d47b4291137c916d539f8861ba040f4363062a`;
- observed/map pair
  `c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
  `d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`.

## Decision rule

- If every budget-only worker-three/four failure has both at least two successful currency PICKs
  and at least one oversubscribed resource, D54 may introduce a shared per-turn PICK ledger that
  decrements surplus after each planned command.
- If any residual budget failure lacks that signature, freeze a turn-level command/state trace
  before changing allocation.

The diagnostic cannot promote a policy, reinterpret D53a's workforce counters, evaluate support,
or authorize a candidate, TestSession game, submission, Arena action, or resident change.
