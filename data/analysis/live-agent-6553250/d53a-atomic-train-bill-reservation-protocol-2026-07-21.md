# D53a atomic TRAIN-bill reservation — frozen protocol (2026-07-21)

## Question

D52b attributes all 5,142 failed worker-three/four TRAIN attempts to a preceding PICK spending
required currency; none involve the shack and none are unexplained. Does preserving the exact
current TRAIN bill through same-turn role commands allow the otherwise unchanged procedural job
market to complete the frozen workforce ladder broadly?

## Frozen V4 treatment

Create `LegendFieldProxyV4` with the same eight configs and behavior as D52a V3, except for one
transactional invariant:

- whenever a next worker exists, pass its exact current `training_cost` into the producer command
  as reserved inventory even when the controller also emits TRAIN on that turn;
- `v2_pick_seed` may still PICK BANANA or any PLUM/LEMON/APPLE strictly above that resource's bill;
  it may not consume the exact bill before TRAIN resolves.

Do not alter affordability, deficit calculation, first/later worker specs, workforce caps,
producer quotas, role ranking, target reservation/order, farm caps, planting, fallback behavior,
endgame banking, or shack behavior. In particular, the 468 opening shack failures are not repaired:
they eventually recover and are outside D52b's binding worker-three/four cause.

Cross hp2/balanced first spec, cap three/four, and one/two post-funding producers for exactly eight
V4 configs. No parameter may change after execution.

## Execution and gates

Run exact `b100_e6` as player 0 against all eight V4 configs on the same 160 consumed exact maps,
twice with 20 threads. Apply the D52 opening-affordability amendment and all original D52a gates:

1. exact byte-identical complete 160 x 8 repeats;
2. exact V2-parent-conditioned first TRAIN presence/spec;
3. zero worker-cap violations;
4. every config reaches worker two on at least 90% of maps;
5. every config reaches worker three on at least 55%, with at least 70% aggregate;
6. every max-four config reaches worker four on at least 5%, with at least 15% aggregate;
7. every config creates a successful crop on at least 90%, with at least 95% aggregate; and
8. at least 50% of cells differ in complete checkpoint/terminal signature from the corresponding
   V2 farm parent.

Add these D53 transaction gates:

9. every TRAIN attempt partition is exact;
10. there are zero budget-inclusive or unexplained failed TRAIN attempts at targets two through
    four; and
11. every failed target-three/four TRAIN, if any, is shack-only. No new cause may replace PICK.

Record all existing fields and D52b telemetry, but ignore score direction, support, distance,
cohorts, opponent identity, and policy value. Frozen source/data evidence includes D52b result
SHA-256 `9b4913fd19b243f4b37bbdf558901dd822e9d329e0b2457ca9ed62cde4cc69e6`,
the observed/map pair
`c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
`d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`, and V2 parent SHA-256
`2a3150540d8b6b563d778ff0a3cca2e0d68c52bb130145030a71a896c2fe073b`.

## Decision rule

- **Pass:** freeze all eight V4 trajectories and open a separately specified consumed-map opponent
  support audit. No candidate or platform conclusion follows.
- **Transaction pass but workforce fail:** the currency bug is repaired but funding acquisition is
  still insufficient; localize deficits without changing this result's parameters.
- **Transaction fail:** close the implementation and diagnose the new exact cause before any
  workforce or support interpretation.

No fresh map, candidate generation, TestSession game, submission, Arena action, or resident change
is authorized.
