# LegendFieldProxy v1 — frozen protocol, 2026-07-19

## Question

Can a compact controller built specifically around the observed rich-opponent mechanism reproduce
held-out immediate four-worker farm+wood trajectories against exact `b100_e6`?

The controller is an opponent model only.  Its score against our candidate is irrelevant here,
and it cannot be submitted or used to modify the resident.

## Frozen causal grammar

Every variant is a complete deterministic policy with:

- at most four workers;
- an immediate harvest/chop-capable first worker;
- coordinated funding: while the next staged worker is unaffordable, current harvest-capable
  workers split the outstanding fruit/iron deficits, bank useful cargo, and preserve distinct
  targets;
- renewable production after funding: generalists harvest ripe trees for seeds, carry seeds to
  empty own-side farm cells, plant, fell mature trees, and bank full/late cargo;
- per-turn target reservation and shortest-path engine movement; and
- no access to arena opponent identity, replay labels, future state, or observed target metrics.

Freeze two staged worker ladders:

1. `hp2`: `(2,2,2,1)`, `(2,3,1,2)`, `(2,3,1,2)`;
2. `balanced`: `(2,2,1,1)`, `(2,3,1,2)`, `(2,3,1,2)`.

Cross each ladder with farmer-role counts 1 and 2, and fell-start turns 1 and 100: eight configs.
All other values are fixed: four-worker cap, farm radius 6, standing own-side farm cap 36, plant
the largest carried fruit stack with deterministic type ties, harvest before felling a fruited
tree, target mature trees by reachable distance then opponent proximity, and start terminal
banking when remaining turns are no more than travel time plus two.  Do not add or tune configs
after reading results.

## Inputs and execution

- Same exact 160 official maps, exact `b100_e6` player 0, old-zoo baseline, referee/event
  instrumentation, absorbing-terminal rule, feature tolerances, and SHA-256 80/80 split as the two
  preceding calibration experiments.
- Run 160 x 8 = 1,280 complete trajectories with 20 workers.
- Select on the 12 rich-immediate discovery games by more macro covers, more full covers, lower
  mean normalized macro distance, then lexicographic label.
- Evaluate only that unchanged representative on the nine rich-immediate confirmation games and
  as an incremental member of the old-zoo union across all confirmation cohorts.

## Frozen confirmation gates

The v1 representation passes only if all checks hold:

1. exact unique 160 x 8 grid with no missing checkpoint;
2. selected representative macro-covers at least 20% of rich-immediate confirmation games;
3. it fully covers at least one rich-immediate confirmation game;
4. adding it improves overall confirmation macro support by at least 5 percentage points;
5. it improves worker-rich confirmation macro support by at least 10 percentage points; and
6. it improves catastrophic confirmation macro support by at least 10 percentage points.

Report per-checkpoint signed/absolute residuals even on failure.  Do not relax the gate if the
proxy matches output but not opening or terminal behavior.

## Stop and continuation rules

- **Pass:** add only the selected proxy to the model-support audit, then check whether a second
  rich archetype is still needed before reopening policy optimization.
- **Fail with early fit and late underproduction:** close this fixed role-rotation grammar and
  reconstruct the late production scheduler from clustered arena action transitions rather than
  outcome-tuning more caps/turns.
- **Fail through turn 100:** close the staged funding/target logic itself and reconstruct separate
  opponent-specific rich families.

No fresh seeds, arena games, submissions, source packaging, or resident changes are authorized.
