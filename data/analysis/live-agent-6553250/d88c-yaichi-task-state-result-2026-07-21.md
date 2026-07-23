# D88c yaichi task-state archaeology — result (2026-07-21)

## Decision

**Pass mechanism reconstruction and open a disabled-by-default D89 local challenger.**

D88b's original automated `reject_literal_task_imitation` is retained: its protocol mistakenly
asserted that the fixed 16-game validation block contained 12 renewable games when its already
known D86 labels contain ten. D88c conservatively requires all ten, preserving the original
absolute minimum and increasing the required success fraction to 100%. Both independently
generated aggregate inputs produce the same corrected pass.

## Integrity

Across 35 public games and 18,431 yaichi unit-turns, every turn contains one MSG payload, every
living unit has exactly one task segment, all 13 task states are recognized, and every state maps
to its allowed primitive command. Decoded turns and terminal scores are exact; malformed,
duplicate, foreign, unknown-diff, provenance-underflow, PLANT-lineage, and HARVEST-lineage counts
are all zero.

The one-process and 20-process canonical row files are byte-identical, SHA-256
`ade32a18ad4d3694d89916f3de571520984405f61d11b46a536acf987d23ad29`. The immutable D88b
aggregate SHA-256 is `0b02b7caa8d2a2a1b0e9b55ceb9f0942f0c19a087df3d753e57abf4439171df5`.
The corrected D88c JSON is also byte-identical across both inputs, SHA-256
`76cec767af97cf53c9e4976f7bd4aee3ad6f6c1b0e6556202b88bd5b8a335016`.

Analyzer SHA-256 is `85e62f7ccb3ac124dc6c0f19a03acf2f729df4b65c36fac8563a62b3ca7b35ee`;
the support correction SHA-256 is
`c8373c491c6fd3340c20440c7f02c15901cabab57097905d0629d48f904f600f`. Six focused tests pass.

## Held-out mechanism

The ten held-out strict-renewable games pass every corrected gate:

| Measure | Validation result | Gate |
|---|---:|---:|
| Bank bootstrap before maintenance | 10/10 | 10/10 |
| Complete ordered four-phase lifecycle | 10/10 | 10/10 |
| Starter plants from bank or own crops | 434/442 = 98.19% | >=80% |
| Own-crop tokens replanted by same worker | 358/363 = 98.62% | >=80% |
| Trained worker CHOP/DROP share | 1,540/1,540 = 100% | >=95% |
| Renewable games with trained HARVEST/PLANT | 0/10 | <=1 |

Consumed current games independently retain the same direction: 6/6 phase order, 90.11%
supported starter plants, 203/203 own-crop replants, and 100% trained-worker CHOP/DROP.

## Controller interpretation

The decisive behavior begins after—not before—the second worker appears. In every validation game,
the first bank PICK occurs one to three turns after training and the first bank-sourced PLANT
follows immediately. The starter consumes exactly the initial banked BANANA stock in the inspected
games, creating six to ten bootstrap crops. There is no map-only renewable-mode selection; the
strict renewable/nonrenewable label measures whether the same dynamic loop survives competition
long enough to compound.

All 442 held-out renewable starter crops are BANANA. Of 76 bank-sourced seedlings, 26 become seed
trees and produce 350/363 harvested own-crop fruits. Only four of 358 own-crop-sourced conversion
trees are ever harvested, producing the remaining 13 fruits. Yaichi itself chops 317/358 conversion
crops. Thus the loop is not a conventional orchard:

1. preserve a small bank-seeded reproductive reserve;
2. harvest one fruit at a time from that reserve;
3. replant essentially every fruit into the local conversion queue;
4. have the trained worker turn the queue into wood and bank it; and
5. replace the reproductive reserve only when needed.

The task grammar makes the loop explicit. Persistent `PLANT` intent spans PICK, HARVEST, and PLANT;
`PICK_SHACK` and `GET_SEED_TREE` acquire seed; `GO_PLANT` delivers it; and the second worker cycles
`CHOP_TRAVEL -> DO_CHOP -> RETURN -> DROP`. The median first harvest age is 33 turns, while the
median own-chop age is only ten turns. D87 failed because it connected a harvest to the conversion
half without building or protecting bank-seeded reproductive stock.

## Constraint on D89

D89 must preserve the resident's opening/training, activate from the observed second-worker state,
bootstrap from the initial banked BANANA stock, separate starter farming from trained-worker wood
logistics, protect at least one bank-seeded reserve crop, and replant harvested reserve fruit into
the wood-conversion queue. It must not revive a static map selector, single shared Apple mother,
late scarcity threshold, arbitrary fresh-harvest bridge, third worker, or retuning of consumed
farm experiments.

No submission or platform action is authorized.
