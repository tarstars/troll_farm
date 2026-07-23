# D52a hybrid job-market workforce preflight — frozen protocol (2026-07-21)

## Question

D51 fails before its state trigger because field-supported V2 openings complete worker three in
only 27.48% of cells. D40 independently proves that worker funding succeeds when exact deficit
priority, shack evacuation, and work conservation are composed. D49 proves reservation order is
highly active but persistent predicted TRAIN deposits can become stale under opponent interaction.

D52a tests a new opponent scheduler that owns funding and production from turn one, replans every
turn from actual inventory, and assigns factorized producer/chopper roles to hybrid-capable workers.
This stage asks only whether it creates the required workforce/renewable mechanism broadly and
deterministically. It does not inspect field support or value.

## Frozen V3 scheduler

Create `LegendFieldProxyV3` with these invariant mechanics:

1. Worker two uses one of the two field-supported immediate specs: `hp2=(2,2,2,1)` or
   `balanced=(2,2,1,1)`.
2. Every later worker uses the replay-supported hybrid spec `(2,3,1,2)` and the policy stops at an
   exact cap of three or four workers.
3. The next TRAIN cost and its PLUM/LEMON/APPLE/IRON deficits are recomputed from current state on
   every turn. There is no persistent predicted deposit or reserved future inventory.
4. While a TRAIN bill is pending, up to two current workers are producer/funders; ordinary
   harvest, plant, bank, and fallback chop work continues rather than entering an exclusive
   funding mode.
5. After the workforce cap, exactly one or two producer slots are retained according to config.
   Producer slots go first to workers carrying fruit, standing on ripe crops, or nearest to ripe
   crops, with harvest power and unit ID as deterministic tie breaks. Other workers take the wood
   hub. Every role has the other hub as a work-conserving fallback when its preferred hub has no
   legal command.
6. Producer and wood commands, target reservation, farm-cap schedule, endgame banking, and exact
   TRAIN affordability reuse V2's current deterministic primitives. Commands are recomputed every
   referee turn, so opponent-altered resources are observed before the next reservation.

Cross first spec (`hp2`/`balanced`), workforce cap (3/4), and post-funding producer slots (1/2) for
exactly eight configs. No parameter, target rule, or worker spec may change after execution.

## Activation-only execution

Run exact `b100_e6` as player 0 against all eight V3 configs on the same 160 consumed exact maps:
1,280 cells. Run the complete matrix twice with 20 threads. Record the existing opening,
turn-50/turn-100/final, worker, plant, action, and terminal fields, but ignore score, distance,
coverage, opponent cohort, and field-support outcomes.

Inputs remain the observed/map SHA pair
`c94e3a188913b45c853242bb6a83e5d07f5726dea6c866a1cb1130450d5ae9bc` /
`d7e4419fad0594673c795e01b6db9b758d646b9b865f612910513f47ddc18ff0`.
The D51 accidental support JSON is quarantined and ineligible for any D52 choice.

## Gates

D52a passes only if:

1. both exact 160 x 8 grids are byte-identical and contain no missing checkpoint or terminal;
2. every first command contains the config's exact frozen TRAIN spec;
3. no cell exceeds its configured worker cap;
4. every config reaches worker two on at least 90% of maps;
5. every config reaches worker three on at least 55% of maps and aggregate worker-three rate is at
   least 70%;
6. each four-worker config reaches worker four on at least 5% of maps and their aggregate rate is
   at least 15%;
7. every config creates at least one successful crop on at least 90% of maps and aggregate crop
   rate is at least 95%; and
8. at least 50% of V3 cells differ in complete checkpoint/terminal signature from the corresponding
   V2 first-spec parent (`farm` form), proving the job market is not an inert rewrite.

## Decision rule

- **Pass:** freeze the eight configs and open a separate consumed-map support audit with unchanged
  legacy union/tolerances. No candidate conclusion follows.
- **Fail:** close this exact V3 job market before support. Use mechanism counters to localize
  funding, renewable supply, or role allocation, but do not tune a failed threshold on the same
  maps.

No fresh map, candidate, TestSession game, submission, Arena action, or resident change is
authorized.
