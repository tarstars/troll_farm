# D55a terminal TRAIN stock-flow diagnostic — frozen protocol (2026-07-21)

## Question

D54 makes every worker-three/four TRAIN attempt succeed, yet only 25.31% of cells reach worker
three. Is the missing bill primarily deposited but too late, carried but unbanked, available as
ripe fruit but unharvested, or absent from the renewable/source stock entirely? Which exact resource
dominates the remaining target-three deficit?

## Frozen telemetry replay

Keep the V5 strategy and all eight configs byte-unchanged. Add runner-only final telemetry for the
model player:

- current next-worker target and exact PLUM/LEMON/APPLE/IRON bill;
- deposited inventory and summed worker carry by those four resources;
- terminal standing-plant count and ripe-fruit stock by PLUM/LEMON/APPLE/BANANA;
- cumulative successful model PLANT and HARVEST yield by fruit species.

Replay one exact 160 x 8 matrix with 20 threads on the same consumed maps. Excluding new telemetry,
all fields must reproduce D54a A exactly. Existing transaction partitions must remain exact. Do not
read score, support, distance, cohort, opponent identity, candidate value, or platform outcomes.

For every below-cap cell, compute mutually exclusive terminal readiness:

1. **deposited-ready:** deposited inventory already covers the exact next bill;
2. **carry-closes:** deposited plus carried currency covers it;
3. **ripe-closes:** deposited plus carry plus currently ripe matching fruit covers it (IRON cannot
   be closed by fruit); or
4. **source-unresolved:** none of the above.

Report these categories separately for targets two, three, and four, and count positive deposited
deficits by resource. The binding diagnosis is target three.

Frozen inputs:

- D54a A SHA-256
  `66f99af783e855fc64e48df3990bf04469fe1dea07798ede6b95a4fea17a1263`;
- unchanged V5 strategy SHA-256
  `f5ec11f3ec8b480e82bbbc6c39e7caa77efdb2a678e0d5a190eaf0035c8e098d`;
- observed/map pair
  `c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
  `d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`.

## Decision rule

For target-three blocked cells:

- if one readiness category contains at least 50%, select its corresponding next mechanism:
  end-of-turn retry, explicit banking, ripe-harvest assignment, or renewable/source acquisition;
- otherwise select a factorized stock-flow allocator rather than a single-stage patch.

Within a selected source/acquisition branch, call a resource dominant only if its positive deposited
deficit appears in at least 70% of blocked target-three cells and exceeds the second resource by at
least 15 percentage points. A dominant resource permits one resource-specific prospective
mechanism; otherwise the next scheduler must retain the full exact deficit vector.

This diagnostic cannot change D54's verdict, tune the eight configs, evaluate support, or authorize
a candidate, TestSession game, submission, Arena action, or resident change.
