# Way B Phase 2 day-3 validity correction: zero-OOV is not a total-label pass, and seat swap changes the teacher

- Author: `chatgpt_1`
- Date: 2026-08-29
- Task: `20260829-nn-bot-way-b-dataset`
- Builder snapshot: `agent/claude_1@d5b9ab518616bea664d40ccaad171f5c8c66c08e`
- Main snapshot: `origin/main@8127ee78221a5b5e71515f4b652d8fc5e7b58e9d`
- Scope: read-only dataset/interface validation; no build, formal review verdict, shard generation, training run, or platform action

## Executive result

The day-3 work correctly reproduces the coordinator's 1,725-TRAIN census and migrates numeric plan indices to the 400-tuple box. It is not yet a valid training shard.

Three corrections are binding before the plan labels and augmentation can be accepted:

1. The guard returns success when 44 teacher TRAIN events are actions the final plan mask forbids.
2. The quoted “44 rows / 2.6% of plan labels” counts TRAIN events, not the hindsight-labelled turn rows actually sent to the loss.
3. `seat_swapped` flips only the row's seat and label while keeping the original absolute state and troll identity; it therefore supervises the teacher's action on the opponent's observation and fails the strict active-troll ownership check.

The independent storage correction also remains: dense observations are tens of gigabytes, not terabytes.

## 1. The total-label guard is fail-open on masked labels

`census_tables()` computes both:

```python
oov       # tuple outside the 400-value numeric box
forbidden # tuple inside the box but plan_mask_forbids(...)
```

It prints:

```text
OUT OF VOCABULARY: 0
tuples the card's mask forbids: 44 {'harvest>carry': 44}
```

but returns only:

```python
return sum(oov.values())
```

The CLI exits 0 whenever that return is zero. Thus the advertised “total-label guard” passes a dataset containing 44 teacher actions that the model is forbidden to select.

A label function is total only when every parsed teacher action maps to a selectable model action. The gate must fail on:

```text
numeric OOV
or mask-forbidden
or STOP collision
or unparsed/ambiguous command
```

until a signed canonicalization rule explicitly resolves that category.

## 2. Forty-four purchases are not forty-four plan rows

The 44 count comes from `*_turns.jsonl.gz` and counts successful TRAIN commands. The dataset creates one plan row on every turn and labels it with the next future TRAIN. In `rows_for_game`, `plan_mask_forbids` is evaluated inside the backward turn loop, so a single forbidden purchase can label many preceding turns.

Consequently this sentence in `DATASET-DAY3-2026-08-29.md` is not established:

```text
“drop the 44 rows — 2.6% of the plan labels”
```

`44 / 1,725` is 2.6% of TRAIN events, not of plan rows. The required decision denominator is:

```text
number of unaugmented hindsight plan rows whose next TRAIN is mask-forbidden
number of games affected
turn span before each such TRAIN
teacher split
```

The full builder already accumulates this quantity in `census["mask_forbids"]`; publish it over the exact 784-game replay set before choosing drop, canonicalize, or unmask.

## 3. Recommended ruling on `harvest > carry`

The game imposes no `harvest <= carry` rule, and 44 accepted teacher purchases violate it. The simplest faithful clone mask is to remove that restriction.

It is true that `harvest > carry` is mechanically dominated for a fixed unit: free capacity never exceeds carry capacity, so extra harvest power cannot collect more in one action and costs more apples. That supports an optional canonicalization:

```text
(speed, carry, harvest, chop)
-> (speed, carry, min(harvest, carry), chop)
```

But canonicalization is not a no-op for the plan task. It changes training cost, affordability turn, deficits in planes 68-71, and therefore every preceding hindsight target row. It must be a deliberate “clone capabilities, improve dominated purchases” design with its own before/after counts—not a silent mask repair.

Recommendation for Phase 2: remove `harvest > carry` from the mask, preserve the teacher action, and let PPO learn that it is expensive. Keep `harvest == 0 && chop == 0` masked under the empirical teacher vocabulary because the census finds no such purchase and those units can neither harvest nor chop. Treat real `(1,1,0,0)` as an unsupported TRAIN, never as STOP.

## 4. Seat-swap augmentation is invalid as implemented

Original rows are built for `teacher_seat` and store the original teacher troll id. `seat_swapped()` then does only:

```python
q = dict(r, seat=1-r["seat"], aug=1)
q["label"] = rotate_180(label)  # command rows
```

`turn_states` are not transformed or duplicated. The documentation says the loader will pass the flipped seat to the same `tf_full_obs_from_state` state.

That has two failures.

### Command rows

The active troll id still belongs to the original teacher seat. The accepted strict `tf_full_obs_from_state` contract requires the active troll to belong to the viewing seat. Passing the flipped seat must therefore fail. If a loader bypasses that validation, it trains an action for one player's troll on the other player's observation.

### Plan rows

There is no active troll to expose the mismatch. The flipped `seat` simply asks the builder for the original opponent's bank, units and score, while the label remains the teacher's next TRAIN. This is wrong supervision that can look structurally valid.

### Why the involution self-test proves too little

The test rotates a label twice and observes that it returns to the original. It never constructs a full state, never swaps player identities/inventories, never invokes the strict Rust builder, and never checks observation/label ownership. An invertible wrong transform remains wrong.

## 5. Correct alternatives for seat handling

### Preferred: no synthetic seat-swap rows

Use the teacher's actual absolute seat and rely on the signed player-relative observation builder. The network already sees either absolute seat in one canonical frame. Report the actual seat distribution and rebalance by game weights only if needed.

### Full state symmetry transform

If a synthetic mirror is retained, transform the entire example:

```text
rotate every coordinate inside w x h
swap player ids on units
swap the two inventories, scores and shacks
transform staged actions and command coordinates
set viewing seat to 1-teacher_seat
```

Under the player-relative builder, this full transform should produce a byte-identical canonical observation and the relative action label should generally remain identical—not receive a second rotation. That means it adds duplicate weight, not new geometry. Prove the claim with full-state bytes and command round trips before keeping it.

## 6. Storage arithmetic remains incorrect

The day-3 report repeats “~20 TB” for materialized planes. With about 800,000 unaugmented rows:

```text
800,000 * 25,168 bytes = 20.13 GB = 18.75 GiB
```

If augmentation doubles the rows, it is about 40.3 GB, still not terabytes. The host had about 111 GB free. Compact states may remain the better throughput choice, but the record and board must correct the unit error and the format must be selected by compression/loading versus batched Rust-generation benchmarks.

## Required controls

1. The census CLI exits nonzero with any mask-forbidden teacher tuple under the active mask.
2. Publish actual forbidden **plan-row** and affected-game counts, not only 44 TRAIN events.
3. Inject a numeric-in-range but masked label; shard acceptance fails.
4. Inject parsed `(1,1,0,0)`; it cannot become STOP.
5. For every unaugmented command row, the active troll belongs to `row.seat` and the encoded label is legal under the Rust mask.
6. For every synthetic augmented row, validate full-state ownership and compare the expected observation bytes; the current seat-only transform must be a negative control that fails.
7. Correct every 20-TB statement to the measured/estimated gigabyte quantity before choosing the storage format.

## Recommendation

Keep the 400-way box. Remove `harvest > carry` from the model mask for faithful behavior cloning, disable the current seat-swap augmentation, and run the full teacher set once without augmentation to measure actual row counts, mask totality and storage/loader costs. Reintroduce only a full-state symmetry transform if it produces a non-duplicate, valid training example.
