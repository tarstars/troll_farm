# D54a shared PICK-ledger workforce preflight — frozen protocol (2026-07-21)

## Question

D53b proves that every residual budget failure comes from two workers spending the same apparent
single-unit surplus. Does a shared command-planning inventory ledger complete the frozen workforce
ladder when added to the otherwise unchanged V4 scheduler?

## Frozen V5 treatment

Create `LegendFieldProxyV5` with the same eight configs and all V4 behavior. Add one invariant:

1. initialize a per-turn planning inventory from the current referee state;
2. generate workers in the existing deterministic unit order with the existing role/fallback
   logic and exact TRAIN bill;
3. whenever an accepted command is `PICK resource`, decrement that resource in the planning view
   before generating the next worker's command; and
4. do not mutate unit, plant, target, score, or actual referee state in the planning view.

This ledger covers BANANA as well as TRAIN currency so later PICK commands see the true remaining
inventory, but only the exact PLUM/LEMON/APPLE/IRON TRAIN bill remains reserved. Do not alter worker
specs, caps, producer quotas, role ranking/order, command fallbacks, target reservations, farm caps,
planting, banking, affordability, deficits, or shack behavior.

Cross hp2/balanced first spec, cap three/four, and one/two retained producers for exactly eight V5
configs. No parameter may change after execution.

## Execution and gates

Run exact `b100_e6` as player 0 against all eight V5 configs on the same 160 consumed maps, twice
with 20 threads. Apply the D52 opening amendment and all original D52 activation gates unchanged:

- exact byte-identical complete 160 x 8 repeats and parent-conditioned first TRAIN;
- zero cap violations;
- worker two: at least 90% in every config;
- worker three: at least 55% in every config and 70% aggregate;
- worker four: at least 5% in every max-four config and 15% aggregate;
- successful crop: at least 90% in every config and 95% aggregate; and
- at least 50% complete-signature change from the matching V2 farm parent.

Transaction gates remain:

- every attempt partition exact;
- zero budget-inclusive or unexplained TRAIN failures at targets two through four; and
- every failed target-three/four TRAIN, if any, shack-only.

Record all current telemetry but ignore score direction, support, distance, cohort, opponent
identity, policy value, and platform outcomes. Frozen evidence includes D53b result SHA-256
`bc980354842b0defc20206281318baea46950e9925c0f0612eb69c71fd68e8ae`, the observed/map pair
`c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
`d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`, and V2 parent SHA-256
`2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b`.

## Decision rule

- **Full pass:** freeze all eight V5 trajectories and specify a separate consumed-map support
  audit. No candidate conclusion follows.
- **Transaction pass but workforce fail:** shared spending is repaired; close transaction tuning
  and diagnose acquisition deficits from mechanism-only state traces.
- **Transaction fail:** trace the new exact cause before interpreting workforce.

No fresh map, candidate generation, TestSession game, submission, Arena action, or resident change
is authorized.
