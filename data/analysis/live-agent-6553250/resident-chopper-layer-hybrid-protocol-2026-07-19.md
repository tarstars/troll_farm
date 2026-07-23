# Resident chopper-layer hybrid — frozen protocol, 2026-07-19

## Question

Does the resident's complete pure-chopper command layer account for the reproductive suppression
that the productive farm loses, or does that advantage require the resident's full worker/economy
trajectory?

The preceding ownership-aware controller reduced adaptive-Gold successful plants by only 1.558
per game versus farm, while resident reduced them by 31.250. This experiment swaps a coherent
decision layer instead of inventing another crop-value coefficient.

## Fixed hybrid

Run three stateful controllers on every observed turn:

1. the exact `lean_m2c2h0k2` Gold farm, which supplies the actual training command and every
   starter/generalist command;
2. an independent identical Gold farm shadow, used only for base-command parity; and
3. the exact resident `SecureOrchardBot`, advanced on the same actual state.

After the farm's pure `2/2/0/2` chopper exists, replace that unit's complete base command with the
resident command for the same unit id. The replacement admits the resident's MOVE, CHOP, DROP,
MINE, PICK, HARVEST, or PLANT decision exactly as emitted. It never copies resident
TRAIN commands or commands for another unit. Before the pure chopper exists, and whenever the
resident emits no unit-specific command for it, preserve the farm command. No score, ETA, size,
turn, crop, opponent, or map threshold is added.

This is a research component swap, not a deployable architecture. It deliberately exposes any
coordination incompatibility between the farm starter and resident chopper; no collision repair is
allowed in this experiment.

## Data and integrity

- Consumed seeds 0--29: implementation integrity only. Require exact same-build farm-shadow
  parity, deterministic repeat-run byte identity, all games complete, at least 95% provenance,
  at least 400/480 substituted cells, and no invalid/panicking command stream.
- Discovery: fresh seeds 1780--1839, both seats, the same eight structural opponents; 960 common
  cells for resident, unchanged farm, and hybrid.
- Confirmation: seeds 1840--1899 remain unopened unless every discovery gate passes unchanged.
- Run with 20 workers. Report substitutions, first substitution, copied verb, opponent plant
  count, crop provenance, complete score/margin/wood, and worker count.

The previously reserved 1720--1779 block remains sealed with the closed ownership-aware formula
and is not reassigned.

## Discovery gates

All integrity checks must pass. Hybrid versus exact resident must then satisfy:

- mean margin delta at least +10 and 5%-trimmed mean at least +5;
- mean own-score delta at least +50 and mean own-wood delta at least +10;
- at least six of eight opponent mean margin deltas nonnegative;
- worst opponent mean margin delta at least -5; and
- adaptive-Gold mean margin delta nonnegative.

Mechanism preservation against unchanged farm on adaptive Gold additionally requires:

- mean own-score delta at least -30;
- mean opponent-score delta at most -50;
- mean opponent successful-plant delta at most -10; and
- mean opponent self-crop wood delta at most -20.

The mechanism floors ask the swapped chopper layer to recover roughly one third of the observed
31.25-plant and 57+-wood resident/farm reproductive gaps. They were fixed from the prior causal
decomposition, not from hybrid outcomes.

## Confirmation and stop rule

Confirmation repeats the exact controller and gates, with both mean and trimmed margin floors at
+10. Any failure closes the command-layer swap without copying only selected resident verbs,
adding collision rules, or tuning a switch threshold on consumed data. A pass authorizes only
distillation and field-prefix mechanism work; it does not authorize arena submission.
