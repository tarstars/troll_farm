# LegendFieldProxy v2 — frozen protocol, 2026-07-19

## Question

Does a replay-derived pair of continuous producer/funders plus a third chopper reproduce the rich
field trajectories that v1's global funding mode missed?

This remains opponent-model calibration on consumed maps, never candidate evaluation.

## Frozen v2 scheduler

All variants stop at exactly three workers and share this scheduler:

- Worker 0 (starter) and worker 1 continuously execute the fruit/farm hub.  They harvest ripe
  trees, bank full or next-TRAIN-useful cargo, PICK surplus banked seeds, and PLANT into a scheduled
  own-side standing farm target: 12 trees through turn 100, 18 through turn 200, then 24.
- Before worker 2 is affordable, the two producers bias distinct ripe/iron targets toward the
  largest remaining third-worker cost deficits, but they never suspend ordinary harvest/plant/
  bank cycles.
- Worker 2 executes the wood hub: harvest a fruited tree only if capable, otherwise repeat CHOP;
  bank when the next chop would fill it, then resume the nearest mature tree with opponent-
  proximity as the deterministic tie-break.
- In the `late_chop` variants, worker 1 changes from the producer hub to the wood hub at turn 150;
  in `farm` variants it remains a producer.
- Terminal cargo returns when remaining turns are travel time plus two.  Target reservation,
  farm geometry, referee, and absorbing-terminal handling match v1.

No exclusive funding mode, fourth worker, identity feature, future state, or target action count
is allowed.

## Frozen eight configs

Cross:

- immediate producer spec `hp2=(2,2,2,1)` or `balanced=(2,2,1,1)`;
- third chopper `cheap=(2,2,0,2)` or `strong=(3,4,1,3)`; and
- worker-1 late role `farm` or `late_chop`.

Labels are `legend_v2_<producer>_<chopper>_<late-role>`.  Do not alter specs, turn 150, farm
targets, or target priorities after execution.

## Data, selection, and gates

Use the same exact 160 maps, exact `b100_e6`, old-zoo union, referee instrumentation, frozen
80/80 SHA split, and rich target cohorts as v1.  Run 160 x 8 = 1,280 trajectories with 20 workers.
Select by rich discovery macro covers, full covers, normalized distance, then label.

Apply v1's confirmation gates unchanged:

1. exact unique 1,280-cell grid;
2. selected model macro-covers >=20% of nine rich confirmation games;
3. it fully covers at least one rich confirmation game;
4. overall macro support improves >=5 percentage points;
5. worker-rich macro support improves >=10 percentage points; and
6. catastrophic macro support improves >=10 percentage points.

Report trajectory residuals and the selected model's final worker distribution.

## Stop rule

- **Pass:** retain v2 as a field proxy, rerun global coverage, then rebuild the policy ambiguity
  set before any optimization.
- **Fail but cover one coherent named family:** split rich opponents into scheduler clusters and
  retain the covered family only; do not force a universal proxy.
- **Fail without family coverage:** close hand-built rich proxy scheduling and move to
  replay-conditioned trajectory resampling or per-opponent distilled simulators.

No fresh seeds, arena game, submission, candidate source, or resident change.
