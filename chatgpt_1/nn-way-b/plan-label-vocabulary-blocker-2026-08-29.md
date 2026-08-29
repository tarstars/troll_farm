# Way B Phase 2 blocker: the chosen teacher population contains TRAIN labels outside the 144-way head

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: read-only dataset/interface finding; no build, formal review verdict, experiment, training run, or platform action
- Main snapshot: `origin/main@448dc8e19b4144abb7663c845a778d2d960b5037`
- Task: `20260829-nn-bot-way-b-dataset`
- Status: **plan-label pilot must report and resolve out-of-vocabulary labels before writing training shards**

## Finding

The parent card combines two individually reasonable choices that are incompatible as written:

1. Use delineate's 144-way train-plan head, whose talent domain is exactly:

```text
movement 1..3
carry    1..4
harvest  0..2
chop     0..3
```

2. Clone plan actions from all four reconstructed top players, including Bubaptik.

The selected Bubaptik proxy routinely trains movement-4 trolls. Those actions have no index in the 144-way head. Its observation also clips movement 4 to the same byte as movement 3 because the signed movement scales are 3.

This is not a hypothetical old-lineage corner. It is the measured plan of the newest and most-played Bubaptik proxy used by the reconstruction package.

## Exact record

`local_claude_1/reconstructions/sources/delineate-gist.github.com-2026-05-25.md` states that delineate deliberately restricted its plan head to 1-3 / 1-4 / 0-2 / 0-3, yielding 144 logits.

The parent card `coordination/tasks/20260829-nn-bot-way-b.md` adopts that exact 144-way head and also names delineate, norxondor, MSz and Bubaptik as the dataset teachers.

`local_claude_1/reconstructions/Bubaptik/ALGORITHM.md` identifies the newest proxy as agent `6568138`, 191 games / 192 seats, and reports 422 successful TRAINs. Its measured later-worker target is:

```text
4 3 h c
```

The same report gives:

- troll 3: 147 purchases, of which 27 use the speed-1 fallback — therefore **120 measured speed-4 labels**;
- troll 4: 77 purchases, of which 19 use the speed-1 fallback — therefore **58 measured speed-4 labels**;
- troll 5: 12 purchases, not needed for the lower bound;
- harvest can rise beyond 1 and the report explicitly allows 2-3 when apples permit.

Thus **at least 178 successful TRAIN actions in this one selected teacher are outside the movement domain**, before examining troll 5 or any harvest-3 label. The exact full-teacher histogram still needs to be generated from the dataset inputs; 178 is a demonstrated lower bound, not the final OOV count.

## Why the impact exceeds 178 rows

The dataset contract does not label only the TRAIN turn. It creates one plan row on every turn, labelled with the talents of the player's **next** TRAIN, or STOP/0 if no later TRAIN exists.

A single future speed-4 purchase therefore makes every preceding plan row back to the previous purchase carry an unrepresentable label. Silently dropping only the TRAIN event does not repair the supervision.

## Observation aliasing

The signed planes use scale 3 for individual/max movement and scale 36 for the sum of up to twelve movement-3 trolls. A movement-4 unit is quantized with clamping and becomes indistinguishable from movement 3 in:

- own/opponent per-cell movement planes 18 and 28;
- own/opponent maximum movement planes 72 and 80;
- train-target movement plane 60;
- aggregate sums 76 and 84 can also saturate earlier than their documented domain.

So even if Bubaptik's speed-4 plan rows were removed, its post-training command rows would still be represented under a false talent observation.

## Unsafe implicit repairs

The following must be rejected unless separately designed and measured:

- map movement 4 to movement 3;
- map an unknown plan to STOP/0;
- drop only the TRAIN turn while keeping earlier hindsight-labelled plan rows;
- keep command rows after a speed-4/hp-3 unit appears while silently clipping its attributes;
- expand the head but leave planes/scales/export/runtime at the old domain.

Each creates internally consistent shards whose labels no longer mean the teacher's action.

## Required pre-shard census

Before the pilot's plan rows are accepted, enumerate every successful TRAIN in the exact selected 784-game teacher package and publish:

```text
player
talent tuple
count of TRAIN events
count of plan rows hindsight-labelled with that tuple
whether the tuple is in the current 144-way vocabulary
first and last game/turn examples
```

Also enumerate every state containing a unit whose movement, carry, harvest or chop lies outside the signed observation scale, and count the affected command rows.

The census must fail closed on any tuple that cannot be encoded. It must not coerce before counting.

## Design choices

### Choice A — preserve delineate's exact 144-way architecture

Then the clone is not a four-player clone as currently described. Plan supervision must exclude teachers/segments with out-of-domain targets, and command supervision must exclude or explicitly remodel states with out-of-scale units. The report must name the retained teachers and denominators.

The cleanest A is likely: use delineate-compatible teachers for the plan head; treat Bubaptik as a later evaluation/opponent source, not a plan teacher. This preserves the copied architecture but sacrifices a material top-player strategy.

### Choice B — represent the selected teachers faithfully

Widen the plan representation and all dependent interfaces. A simple full observed range suggested by the current record is at least movement 1-4, carry 1-4, harvest 0-3, chop 0-3, plus an explicit STOP action. A flat Cartesian head would be 256 talent tuples before masking, plus STOP; a per-candidate shared MLP, as delineate actually used, avoids treating width as a fixed semantic constraint.

Before freezing 257 or any other count, use the exact census: the referee parser/local engine do not enforce the delineate caps, so empirical teacher support—not an assumed maximum—must define the required domain.

Choice B also requires updated observation scales, codec/masks, checkpoint schema, trainer, exporter and future Rust inference path. It is an architecture amendment, not a dataset-only patch.

### Choice C — factorized or candidate-list plan head

Predict STOP plus separate talent components, or score a dynamically enumerated candidate list. This handles unseen combinations better but changes the learning problem and needs its own masking/loss/export design. It should not be smuggled into the pilot.

## Recommendation

Pause only the **plan-label shard**. Continue exact command-label extraction and the bench repairs.

Run the OOV census first, then obtain one explicit coordinator/owner design ruling:

```text
A: exact delineate 144-way head, narrower teacher population
or
B/C: faithful four-teacher vocabulary, amended architecture
```

Do not train a plan head until the label function is total over its declared training population and the observation planes distinguish every retained teacher talent.
