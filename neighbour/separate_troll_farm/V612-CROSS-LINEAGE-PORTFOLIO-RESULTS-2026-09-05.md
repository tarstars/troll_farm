# V612 cross-lineage frozen-panel portfolio bound -- 2026-09-05

## Verdict

The 40 distinct candidate behaviors already measured on the exact 192-row V468 field do not
support a credible selector. A perfect map-only portfolio, allowed to memorize all eight frozen
map seeds and offset checkpoint losses between maps, reaches only `+0.07/+5.58/+37.84` at turns
100, 200, and final. It misses the required `+40` final gain. Letting the oracle also memorize the
seat reaches `+0.02/+0.82/+44.36`, but this is a seven-lineage, frozen-panel lookup with essentially
no turn-100 margin. A leave-one-map-out selector trained on 69 observable initial-board features
scores `-4.67/-4.71/-0.37`. Existing-candidate selection is therefore closed as the next bot
architecture.

The strongest safer impossibility check agrees. A hindsight row oracle that may see the map,
seat, opponent family, and eventual outcome, but may choose a candidate only when that exact row
is nonnegative at all three checkpoints, gains `+25.55` final. It cannot reach `+40` even with
information unavailable to a submitted bot. No individual candidate passes the gate. There was
no new candidate, fresh panel, duel, packaging step, production change, or platform publication.

## Inventory and baseline lock

The inventory scanned every large TSV under the working tree and retained all 83 files containing
exactly 192 game rows. V610's frozen panel supplied the reference row set: maps 9,941,000 through
9,941,007, both seats, and the 12 fixed opponent families. A panel was admitted only when all row
keys and every immutable `baseline_*` score, resource metric, checkpoint, and full command stream
matched that reference. `baseline_divergent_command` was deliberately excluded because it is the
V468 command at a candidate-dependent divergence turn, not a baseline identity field.

The audit admitted 53 files. Full candidate-command fingerprints collapsed 13 archive or
behavioral duplicates, leaving 40 distinct behaviors. Of the other 30 files, 17 used a different
baseline, nine legacy V441--V454 files lacked turn-100/200 checkpoint columns, and four used a
different row set. Command-identical copies were also required to have identical candidate
measurements. The test suite locks trailer filtering, divergence-relative baseline handling,
baseline rejection, candidate deduplication, grouped sums, constrained optimization, feature
parsing, and held-out-score isolation.

## Individual frontier

The late economies are large, but all buy that score by abandoning V468's opening:

| candidate | turn 100 | turn 200 | final | gate |
|---|---:|---:|---:|---|
| V564 capacity-three dense worker | -68.75 | -27.80 | +171.47 | fail checkpoints |
| V546 dense source orchard | -72.90 | -33.27 | +131.23 | fail checkpoints |
| V545 pure repaired R1FA | -77.01 | -35.12 | +116.29 | fail checkpoints |
| V547 fund-before-hire | -53.98 | -53.62 | +111.56 | fail checkpoints |
| V567 capacity-two producer | -52.37 | -91.06 | +43.18 | fail checkpoints |
| V480 opening farm / third worker | -6.61 | -2.15 | +12.48 | fail checkpoints/final |
| V486 conservative historical arm | -4.42 | +2.36 | +5.49 | fail checkpoint/final |
| V490 conservative historical arm | -0.43 | -2.65 | +0.16 | fail checkpoints/final |
| V610 carry-three mature lane | -34.72 | -49.37 | -42.01 | fail |

The final-only ranking is misleading: V564 more than quadruples the required final gain, yet its
turn-100 loss alone is larger than the final gain the gate asks for. This early/late exchange is
shared by every high-scoring dense candidate.

## Selector bounds

Every selector includes exact V468 as a zero-delta fallback. “Final oracle” chooses the best final
candidate independently in each context and ignores checkpoints. “Checkpoint-safe” requires the
chosen candidate to be nonnegative at all three checkpoints inside every context. “Aggregate
constrained” permits losses in one context only when other contexts offset them, and exactly
maximizes final score subject to nonnegative aggregate turns 100 and 200.

| selector information | turn 100 | turn 200 | final | interpretation |
|---|---:|---:|---:|---|
| row final oracle | -68.66 | -15.38 | +206.30 | impossible hindsight, checkpoints ignored |
| row checkpoint-safe oracle | +3.95 | +12.25 | +25.55 | impossible hindsight, still below +40 |
| map final oracle | -69.68 | -28.63 | +178.68 | exact frozen-map lookup |
| map checkpoint-safe oracle | +2.33 | +6.76 | +14.25 | exact lookup, locally safe |
| map aggregate-constrained optimum | +0.07 | +5.58 | +37.84 | exact lookup, **below gate** |
| map + seat checkpoint-safe oracle | +2.60 | +7.85 | +14.23 | exact seat-oriented lookup |
| map + seat aggregate optimum | +0.02 | +0.82 | +44.36 | barely passes, lookup only |
| opponent-family checkpoint-safe oracle | +0.02 | +0.68 | +3.76 | opponent identity unavailable at start |
| seat-only aggregate optimum | +0.00 | +0.00 | +0.00 | always V468 |
| static-feature stump, leave one map out | -4.67 | -4.71 | -0.37 | observable and held out; fails |

The exact map optimum exposes where its `+37.84` comes from:

| map | selected behavior | turn 100 | turn 200 | final |
|---:|---|---:|---:|---:|
| 9,941,000 | V610 | +12.00 | +29.83 | +40.00 |
| 9,941,001 | V490 | +0.00 | -1.17 | +2.08 |
| 9,941,002 | V486 | +1.83 | +8.38 | +8.04 |
| 9,941,003 | V480 | -6.96 | +6.58 | +42.12 |
| 9,941,004 | V566 | -11.12 | -6.71 | +193.29 |
| 9,941,005 | V490 | +0.00 | +1.50 | +4.00 |
| 9,941,006 | V490 | +0.00 | -1.79 | +0.88 |
| 9,941,007 | V486 | +4.83 | +8.04 | +12.33 |

V566's single-map `+193.29` late surplus carries most of this construction; five maps contribute
at most `+12.33`. The seat-aware optimum uses V479 twice, V486 four times, V490 four times, V566
three times, and V579, V591, and V610 once each. Besides being an exact frozen-key lookup, fitting
seven complete lineages inside the 100,000-unit submission limit is unproved and implausible.

## Observable feature stress

The pinned read-only official generator exported 69 numeric features for each map and seat: board
dimensions, shack coordinates and path length, obstacle counts, iron access, local grass, initial
inventory, and species-specific counts, sizes, fruit, maturity, distance, and proximity. The model
never received map seed, opponent family, or held-out outcomes. For each held-out map it searched
all one-threshold/two-candidate rules on the other seven maps under nonnegative training
checkpoints, then evaluated the frozen rule on both held-out seats and all opponents.

Training repeatedly chose local-grass thresholds between V473/V486 and V579. Those rules failed
out of sample: six of eight held-out maps lost at least one checkpoint, and map 9,941,006 alone
scored `-21.58/-47.96/-59.79`. The aggregate was `-4.67/-4.71/-0.37`. This is stronger evidence
than a fitted frozen-map threshold because feature search had many opportunities to find a simple
regime and still could not transfer across eight folds.

## Mechanism and next architecture

The panel has complementarity, but it is idiosyncratic complementarity. The favorable carry-three
bill exists only on map 9,941,000; the dense allocator's exceptional repayment is concentrated on
map 9,941,004; conservative arms provide single-digit offsets elsewhere. There is no common static
regime that turns an existing whole controller into a gate pass. More selector thresholds would
optimize the frozen maps rather than repair the bot.

The read-only neighbor remained at `370fa63c`. Its open champion-prefix orchard charter contributes
a genuinely different, mechanics-backed hypothesis, not a result copied into this project: after
the champion's own second hire, nearby wild trees disappear by about turn 75; a near mature banana
needs six chop-one turns for the same four wood that an apple needs twenty, and bananas are absent
from training bills. This differs from V597--V602, which stayed exact through turn 100 and then
serially injected individual seeds into already-coupled V468 actions. The next independent test is
therefore an exact-second-train prefix followed by an explicit, bounded **up-front banana reserve
establishment phase**: plant several near-bank bananas, return the axe to wild chopping while they
grow in parallel, then fell and bank them, with no third worker and an always-legal no-plant path.

## Reproduction and integrity

- analysis/test/static exporter: `analyze_v612_cross_lineage_portfolio.py`,
  `test_analyze_v612_cross_lineage_portfolio.py`, and `v612_static_map_features.rs`;
- focused tests: 7 passed;
- exporter release build passed; its output has 16 unique map-seat rows plus one header;
- complete machine-readable report, static features, and exact 192-row path inventory:
  `/data/separate_troll_farm-working/analysis/2026-09-05-v612-cross-lineage-portfolio/`;
- report/features/path-list SHA-256:
  `7c079203ff015dd4b79caadcd02ac7cebd516b380ea43f4c4ce7744c340c12ba` /
  `b3aa57749a2c3b0da961b152b226ebf8ae93512b260b7b494472ac122d40c31f` /
  `ab76c7cffde7e0ff3356f9f16b879f9d445fb381ed2fc2988d1dffff03bee1bd`;
- production remained unchanged: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`,
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`;
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`, with its pre-existing
  modified `data/processed/stats.json` and untracked
  `data/panels/top5-ab-20260902T115338Z.json` untouched.
