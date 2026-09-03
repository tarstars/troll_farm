# Way B amendment 8 follow-through: widening the plan head requires widening the state it sees

- Author: `chatgpt_1`
- Date: 2026-08-29
- Scope: cross-interface design audit; no build, formal review verdict, dataset, training run, or platform action
- Main snapshot: `origin/main@0be986165256daa00d78175b7fdaa617df9ad121`
- Relevant decision: parent-card amendment 8, plan vocabulary 400 and per-candidate scorer

## Executive finding

The exact TRAIN census justifies abandoning the 144-way head: 267 of 1,725 teacher purchases lie outside it. The accepted 400-way empirical domain is coherent as a first teacher vocabulary.

The current amendment updates only target planes 60-63 and cost/deficit planes 64-71. That is insufficient. The same speed-4, carry-5 and chop-4 units appear in the ordinary board state after training, where multiple signed planes still clamp them to smaller values. The clone would therefore receive a faithful plan label but an aliased post-training state.

A second gap is architectural: the accepted per-candidate scorer includes “whether it matches the current target,” but the plan-phase state currently carries no previous target. `FullEnv::finish_turn` resets `main_plan` to 0; plan-phase planes 59-71 are therefore zero before the next plan decision. The stated feature is not computable from the current observation planes.

## 1. Every talent-bearing plane that must change

Accepted teacher domain:

```text
movement 1..4
carry    1..5
harvest  0..3
chop     0..4
```

The signed observation table currently uses the old delineate scales in these places.

### Per-unit talents

| planes | old scale | required scale |
|---|---:|---:|
| 18, 28 movement | 3 | 4 |
| 19, 29 carry capacity | 4 | 5 |
| 20, 30 harvest | 3 | 3 |
| 21, 31 chop | 3 | 4 |

### Per-resource cargo and free capacity

A carry-5 troll can hold five identical items, so these also alias today:

| planes | old scale | required scale |
|---|---:|---:|
| 22-27, 32-37 carried resource | 4 | 5 |
| 93, 95 total carried | 4 | 5 |
| 94, 96 free capacity | 4 | 5 |

### Current train target

The parent card already names these changes:

| planes | old | required |
|---|---:|---:|
| 60 movement | 3 | 4 |
| 61 carry | 4 | 5 |
| 62 harvest | 2 | 3 |
| 63 chop | 3 | 4 |

### Aggregate talent maxima and sums

| planes | old scale | required scale |
|---|---:|---:|
| 72, 80 movement max | 3 | 4 |
| 73, 81 carry max | 4 | 5 |
| 74, 82 harvest max | 3 | 3 |
| 75, 83 chop max | 3 | 4 |
| 76, 84 movement sum | 36 | 48 |
| 77, 85 carry sum | 48 | 60 |
| 78, 86 harvest sum | 36 | 36 |
| 79, 87 chop sum | 36 | 48 |

The sum scales assume the existing environment cap of twelve trolls. If that cap changes, the sums must derive from the same constant rather than repeat literals.

### Cost and deficit

The parent card changes 64-71 to scale 48. That is adequate for twelve existing trolls plus carry 5 squared (`12 + 25 = 37`) with margin, but the scale should be derived/documented from the accepted roster and talent domain rather than justified by the unexplained phrase “12 + 25 + margin.”

## 2. Required saturation controls

For each widened dimension, construct two otherwise identical states at the old and new maxima and require different bytes:

```text
movement 3 vs 4
carry 4 vs 5
chop 3 vs 4
cargo/free 4 vs 5
```

Check own and opponent per-cell planes, max planes, sum planes, train-target planes and both seats. A mutation that restores any old scale must fail.

The dataset census should additionally count command rows produced after an out-of-old-range unit exists. Those are the rows whose observations were previously aliased; TRAIN-event counts alone understate the effect.

## 3. “Matches current target” is not currently observable

The accepted scorer is described as receiving:

```text
pooled board features
+ candidate attributes
+ cost
+ deficit
+ affordable flag
+ whether it matches the current target
```

At the plan phase, however:

- the current implementation starts each turn with `main_plan = 0`;
- `finish_turn` resets `main_plan = 0`;
- planes 59-71 encode only the plan chosen **inside the current turn**, after the plan mini-step;
- the plan head runs before that choice.

Therefore “matches current target” cannot be computed from plan-phase planes. Calling the previous turn’s choice the current target requires persistent state that does not yet exist.

Choose one explicit contract:

### A. Persistent previous target

Add `previous_plan_target` per seat to the environment/reconstructed context. At plan phase, expose it to the candidate scorer as a candidate-equality bit; after selection, update it. Define reset rules on successful TRAIN, target becoming impossible, episode reset and STOP selection.

The replay dataset must derive the teacher’s previous target without leaking the next label. Hindsight “next TRAIN” is not evidence of what the teacher selected on the prior turn, so the clone cannot supervise this bit directly unless the target is a model-owned recurrent state.

### B. No previous-target feature in behavior cloning

Remove the feature from Phase 2 and add it only in PPO as model-owned state. This is simpler and honest: teacher replays expose commands and eventual TRAINs, not the teacher’s hidden per-turn target choice.

### C. Recurrent plan policy

Carry the prior selected plan through a recurrent state. This is broader and should not be smuggled into the current feed-forward checkpoint contract.

Recommendation: **B for the clone, A as explicit model/environment state for PPO only if plan churn is measured.** Do not populate the match bit from the hindsight label; that would trivially make every pre-TRAIN row “matches” and leak the target definition into its own feature.

## 4. STOP and plan-mask totality

The dataset builder’s current range-only `plan_index` has two silent failure modes:

1. A real teacher TRAIN `(1,1,0,0)` maps to index 0, which is also STOP.
2. A tuple inside the numeric ranges but excluded by the plan mask, such as `harvest > carry`, receives a label that the learner can never select.

The exact census must therefore report not only out-of-range tuples but **all labels that are not selectable under the final plan mask**. Index 0 is valid only for STOP metadata, never for a parsed TRAIN command. A parsed TRAIN that maps to zero or to a masked index must be named as OOV/unsupported and fail plan-shard acceptance.

Negative controls:

- inject `(1,1,0,0)`: it must not become STOP;
- inject `(1,1,2,1)`: it must be reported mask-incompatible;
- every accepted teacher tuple must round-trip tuple -> index -> tuple and have mask 1;
- STOP must round-trip as a distinct semantic token, not as a talent tuple.

## 5. Coordinated migration boundary

Amendment 8 changes all of the following together:

```text
TF_FULL_PLAN_SIZE 144 -> 400
plan tuple codec and mask
observation scales
per-candidate plan scorer
fake environment
PPO trainer and checkpoint keys
behavior-cloning trainer
compact-state dataset labels
Rust/Python inference/export path
```

Do not accept a mixed generation in which a 400-label dataset is fed to a 144-logit model, or a 400-way environment still emits old-scale observations. Add one schema/version constant returned by the Rust ABI and stored in every dataset/checkpoint. Loader mismatch must fail before training.

## Recommendation

Keep the 400-way empirical vocabulary and per-candidate scorer decision, subject to the full-census maximum. Amend the observation table and ABI generation as one versioned change. Treat the prior-target match feature as currently unobservable from teacher replays rather than manufacturing it from hindsight labels.
