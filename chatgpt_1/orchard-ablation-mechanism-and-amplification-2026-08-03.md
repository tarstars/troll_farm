# Orchard ablation postmortem: mechanism, confounding, and amplification

- Task: `20260803-orchard-ablation-causal-audit`
- Analyst: `chatgpt_1`
- Exact no-orchard identity: agent `6592097`, submission `41085842`
- Exact fresh orchard identity: agent `6592131`, submission `41086057`
- Historical orchard identity: agent `6590141`, submission `41081503`
- Platform mutation in this analysis: none

## Executive conclusion

The statement “removing the orchard moved the bot from rank 11 to rank 30” is not a valid estimate
of orchard value.

The historical orchard-enabled agent read 25.3/rank 12 in the 137-agent snapshot. The no-orchard
agent read 23.27/rank 34. But the exact same orchard-enabled source, resubmitted immediately after
the ablation, read only 23.56/rank 32. Therefore:

```text
historical orchard -> no orchard:       -2.03 score, -22 rank places
historical orchard -> same-source redo: -1.74 score, -20 rank places
fresh orchard -> fresh no-orchard:      +0.29 score,  +2 rank places for orchard
```

About 85.7% of the apparent score drop and 90.9% of the apparent rank drop reappeared with **zero
source change**. The large headline movement is predominantly an agent-reset, matchmaking, map and
opponent-sample effect. The source-consistent fresh comparison is only +0.29 rating and two places
for orchard, below the project's normal ±0.5--1 live-noise allowance.

This does not mean the orchard has no value. Independent controlled evidence says its value is
large **conditional on activation**, while live activation is sparse. The likely system is:

```text
rare qualifying maps × large conditional APPLE output × unstable Arena queue composition
```

The correct objective is to increase safe activation coverage or reduce the active orchard's
coordination cost. It is not to delete the orchard, release its worker globally, or create a broad
renewable farm.

## 1. Fresh-queue comparison

The reproducible checkpoint analyzer compares the two newly created 137-agent queues:

| metric | orchard | no orchard | orchard - no orchard |
|---|---:|---:|---:|
| games | 162 | 160 | +2 |
| Arena score | 23.56 | 23.27 | +0.29 |
| rank | 32 | 34 | -2, better |
| win rate | 57.41% | 56.88% | +0.53 pp |
| mean own score | 183.83 | 189.43 | -5.60 |
| mean opponent score | 174.02 | 178.86 | -4.84 |
| mean margin | +9.81 | +10.57 | -0.76 |
| catastrophe rate | 11.11% | 10.00% | +1.11 pp |
| negative-margin mass | 5,569 | 5,441 | +128 |

Raw game outcomes are nearly indistinguishable and, if anything, slightly favor no-orchard on
terminal margin and tails. Arena rating is not a direct transform of terminal margin and the two
queues contain different opponents and maps.

The exact opponent sets overlap only partially:

```text
common exact opponents: 35
opponent-set Jaccard:    0.427
orchard games on common opponents:    126
no-orchard games on common opponents: 128
```

After opponent standardization the sign is unstable:

| weighting | win-rate diff | own-score diff | opponent-score diff | margin diff |
|---|---:|---:|---:|---:|
| equal opponent | +0.07 pp | +5.96 | +13.48 | -7.52 |
| minimum common count | -1.12 pp | -0.04 | -2.25 | +2.21 |
| pooled common count | +1.63 pp | +0.62 | -5.60 | +6.22 |

An equal-opponent cluster bootstrap gives orchard-minus-no-orchard win-rate interval
`[-13.45 pp, +13.32 pp]` and margin interval `[-40.48, +24.31]`. There is no stable fresh-queue
outcome effect to explain as a two-rating-point mechanism, much less a 22-rank mechanism.

Reproducible outputs:

- `chatgpt_1/orchard_ablation_checkpoint_analysis.py`;
- `chatgpt_1/orchard-ablation-opponent-standardized-2026-08-03.json`;
- `chatgpt_1/orchard-ablation-opponent-standardized-2026-08-03.md`.

## 2. What the secure orchard actually does

The orchard is not a generic planting bonus. It is a narrowly gated base-side APPLE production
option.

### 2.1 Geometry gate

During initialization the wrapper requires, among other invariants:

- at least two usable own-shack doors;
- all natural trees reachable and median natural-tree return distance at least 8;
- an empty own door adjacent to water;
- that door at least 11 path cells from the enemy side;
- deterministic farthest-from-enemy then lexicographic mother selection.

### 2.2 Activation gate

Before turn 100, activation additionally requires:

- worker two already trained;
- the starter empty and standing at a shack door;
- at least one APPLE in the bank or starter carry;
- the mother unoccupied and unplanted;
- enemy chop ETA to the mother above the safety threshold;
- the other worker able to use an alternate door;
- reserving the starter does not concede a natural tree that the starter can beat the enemy to but
  the trained worker cannot.

The no-orchard ablation changes only this transition: it leaves `OrchardPhase::Dormant` forever.
Outside activation states it is exact pure-Yamo behavior. In a frozen 25-game replay packet,
24 games were command-identical and only game `897833045` diverged, first at turn 79 when the
orchard would activate.

### 2.3 Active policy

After activation, the starter is deliberately reserved:

```text
not at mother -> MOVE to mother
carrying      -> DROP
ripe fruit    -> HARVEST
otherwise     -> WAIT
```

The mother is an APPLE tree on a water-adjacent door. APPLE cooldown is 9 and water boost is 7, so
its effective production cooldown is 2. A one-capacity, one-harvest starter can alternate HARVEST
and DROP at the shack door at approximately the same cadence. What looks like idle reservation is
a saturated, almost travel-free production loop.

The other worker retains an alternate bank route and performs the ordinary wood/denial policy.
The orchard therefore creates a clean two-role economy:

```text
starter: safe renewable APPLE score and late option inventory
worker 2: wood, banking and denial
```

## 3. Evidence that the active orchard is valuable

Two results matter more than the unpaired Arena rank comparison.

### 3.1 Sparse but very large observed output

In the prior exact 160-game E7a corpus, own planted crops were reaped in only 11 games, but those
11 games yielded 1,168 fruit. The secure-orchard wrapper is therefore a sparse high-output module,
not a small ubiquitous bonus.

This also explains why two 160-game queues can disagree strongly: the number and quality of
orchard-eligible maps can vary materially, and Arena rating can weight wins against different
opponents very differently.

### 3.2 Controlled reallocation is decisively harmful

The task-market orchard experiment causally isolated 99 clean seed-repaid active cells and allowed
the reserved worker to return to general work. It lost **61.354 mean margin** in active cells:

```text
extra wood obtained:        +4.687
own-crop APPLE lost:       -81.727
active cells improving:      7 / 99
active cells regressing:    92 / 99
```

The mother is a saturated producer, not an idle reservation. Universal release, global task-market
exceptions and standalone release thresholds are closed.

This is the key answer to “why can the orchard matter?” Its value is the stream of safe APPLEs that
is destroyed when the starter is repurposed. The worker's apparent inactivity between visible
fruit actions is part of maintaining a two-turn harvest/deposit cadence and protecting the mother.

## 4. Why the historical Arena row looked much better

The evidence supports four contributors, in descending confidence.

### 4.1 Same-source queue variance dominates the headline

The identical orchard source changed from 25.3/rank 12 to 23.56/rank 32 after resubmission. This
alone accounts for most of the apparent ablation penalty.

### 4.2 Opponent mixture differs materially

Only 35 exact opponents appear in both fresh queues and opponent-set Jaccard is 0.427. Different
weightings of common opponents give orchard margin effects from -7.52 to +6.22. The current data do
not support one stable opponent-adjusted effect.

### 4.3 Orchard support is sparse

The previous corpus shows orchard-scale reaping in about 11/160 games. A difference of a few
eligible maps, or of which opponents occur on those maps, can move rating while barely changing
raw aggregate margin.

This is a plausible explanation, not yet a measured one for the fresh restore. The exact fresh
restore activation count and the no-orchard queue's counterfactual eligibility count still need a
replay-level join.

### 4.4 Rating rewards outcomes, not margin magnitude

No-orchard has slightly better raw terminal margins and tails but a lower rating. This is possible
because a narrow win against a stronger sampled opponent can be more useful to ladder placement
than a large win against a weak one, while catastrophic margin size itself is not the rating
objective. The repository has not reconstructed the exact Arena formula, so this remains a
qualitative boundary rather than a fitted rating model.

## 5. How to amplify the real orchard effect

### Rank 1: preserve the mother and reduce the other worker's banking cost

The orchard occupies one shack door permanently. Activation proves only that another door is
reachable; it does not prove that repeated cargo banking through that door is congestion-free.
The broader controller still exhibits long period-2 MOVE episodes.

The safest improvement is an **orchard-active alternate-door cargo commitment**:

1. freeze one alternate bank door at activation;
2. when worker 2 carries cargo and selects home, keep that door until successful DROP;
3. require monotonic BFS progress or an explicit wait-for-clear state;
4. forbid retargeting through the occupied mother door;
5. release the commitment only after DROP or verified door invalidation.

This preserves the 81.7-APPLE active value while attacking its main opportunity cost: one worker
must do all wood work through reduced bank geometry. It is also directly testable on public
period-2 and unbanked-cargo counterexamples.

### Rank 2: recover missed activations without lowering safety thresholds

Current activation waits until the starter is already empty at a door. A qualifying geometry can
be missed when the starter begins another long chop cycle and does not return before turn 100.

First run a near-miss census. For every game, record the earliest turn on which all static and
safety predicates hold, then identify the sole remaining blocker:

- no bank APPLE;
- starter carrying;
- starter away from a door;
- alternate worker route unavailable;
- contested-tree veto;
- enemy ETA veto;
- deadline.

Only if `starter-away` or `starter-carrying` dominates should a short activation commitment be
built: route the starter home on an already qualified geometry when predicted first mother receipt
exceeds the displaced current cycle. Do **not** lower enemy-distance, contested-tree, alternate-door
or turn-100 safety gates on the same data.

### Rank 3: capitalize only demonstrably stranded orchard APPLE

The orchard's output is valuable even as bank score. Endgame conversion is already active at scale,
so another broad plant loop is unwarranted. Measure terminal unused APPLE and conversion capacity
inside orchard-active games.

A candidate is justified only if many orchard APPLEs remain banked while a complete
plant--chop--return cycle was legal. Then add a bounded surplus rule:

```text
bank APPLE above protected reserve
AND complete conversion cycle fits
AND conversion does not displace a higher-value carried-wood deposit
```

APPLE should not receive unconditional conversion priority: its greater health can make it a slower
wood asset than other fruit species.

### Rank 4: refine activation by expected net value, prospectively

After the replay join, freeze a simple pre-command ROI calculation:

```text
expected mother receipts before horizon
- starter's displaced natural-tree/banking value
- alternate-door congestion cost
- enemy-loss risk
```

Use it to reject marginal current activations or admit only one predeclared near-boundary family.
Do not fit a flexible selector on the same 160 games. The existing static mother tie, universal
release, broad renewable loop and species-substitution branches are already closed.

## 6. Changes that should not be tried again

- **Do not globally release the orchard starter.** Controlled active loss is -61.354 margin.
- **Do not activate a broad farm earlier.** Farm-first orchard scale previously lost 97.57 score.
- **Do not create a broad renewable crop loop.** Tested renewable variants lose wood; ordinary
  resident planting is conversion-by-design.
- **Do not reverse or tune equal-best mother selection.** The exact tie reversal loses on both
  seats and all six opponent families.
- **Do not substitute PLUM/LEMON/BANANA for the APPLE mother globally.** Static species changes
  conflict with training currency and strand trees.
- **Do not call the 25.3-to-23.27 ladder change causal evidence.** Exact same-source resubmission
  reproduces 1.74 of the 2.03 score drop.

## 7. Required replay enrichment

For both fresh queues, publish one compact row per game containing:

- exact agent/submission, game, seat, opponent and opponent strength snapshot;
- map and turn-1 fingerprints;
- orchard static eligibility and each failed activation predicate;
- activation turn, chosen mother and first divergent command;
- mother PLANT, HARVEST and DROP successes;
- own-crop APPLE harvested and banked;
- starter reserved, WAIT, productive and off-mother turns;
- mother death/opponent contact;
- worker-2 bank target, bank ETA, blocked moves, period-2 turns and unbanked cargo;
- endgame conversions attributable to orchard APPLE;
- terminal own/opponent score and margin.

Raw frames remain in the existing cache/LFS packages. The compact table is sufficient for
mechanism and support analysis.

## 8. Prospective experiment

Use three exact arms:

```text
C0 = current E7a secure orchard
A1 = exact no-orchard ablation
C1 = C0 + alternate-door cargo commitment
```

Pair map, opponent and seat. Stratify before outcomes:

1. orchard activates under C0;
2. orchard is statically eligible but current activation is missed;
3. orchard ineligible, where C1 must remain command-identical to C0.

Primary gates:

- zero command divergence outside the declared orchard/alternate-bank sector;
- zero new mother loss or opponent take;
- orchard APPLE banked no lower than C0;
- worker-2 successful DROP count and bank latency improve;
- no new period-2 run of six or more turns;
- positive paired active-sector margin with root/opponent-cluster lower bound above zero;
- prevalence-weighted global gain above the Arena noise band before any submission.

Run exact deterministic common-seed opponent blocks first. Arena comparison is a final transfer
check, never the source of the causal estimate.

## Final disposition

```text
The 22-place drop is mostly not an orchard effect.
Fresh live evidence: orchard +0.29 score / 2 places, unresolved causally.
Controlled active-state evidence: orchard production is large and worker release is harmful.
Best amplification: keep the saturated APPLE mother and make worker-2 banking monotonic through an
alternate door; then measure and recover only safely missed activations.
```
