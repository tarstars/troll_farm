# D34 official-map complete-architecture transfer census — result (2026-07-20)

## Verdict

**No frozen architecture qualifies; confirmation remains sealed.**  Exact official maps do not
remove the production/suppression tradeoff.  The ownership-aware two-worker farm is the strongest
local-margin witness, but its +138.427 own-score gain is accompanied by +91.088 opponent score and
a -24.383 regression against adaptive Gold.  It fails the frozen suppression and rich-opponent
gates and cannot be rehabilitated as a candidate.

D34 selects the next representation specified in the protocol: a **coherent joint
production/suppression scheduler**.  It must allocate complete persistent jobs and roles under a
dual-economy objective.  Worker-command transplants, crop-timing wrappers, phase handoffs, fixed
production pulses, and parameter tuning inside these closed witnesses remain ineligible.

No candidate was built, no controlled platform game or Arena submission occurred, and seeds
9,100,060--9,100,119 remain unopened.

## Integrity

- 60 exact official seeds, both seats, eight opponents, nine controllers;
- complete **8,640/8,640** full-game rows and 960/960 common scenarios;
- exact controller sets, official dimensions, within-seed map identity, and terminal-turn bounds;
- deterministic two-seed integrity run: 288 rows twice, byte-identical SHA-256
  `d1cc91cc27d0d407444e032cfedc44c5f0d5aeb37c7ea5d00a3d4e86b5143850`;
- 273 simultaneous same-cell planting contests retained as an explicitly unassigned telemetry
  category; D34a was written before any controller outcome summary was computed; and
- eight focused Rust runner tests and five Python analyzer tests pass.

## Frozen gate result

All deltas are paired to the exact resident on the same seed, seat, and opponent.  Confidence
intervals use the 60 seed means after averaging seats and opponents inside seed.

| Controller | Margin delta | 95% seed interval | Own score | Opponent score | Nonnegative opponents | Worst opponent | Promotion gates |
|---|---:|---:|---:|---:|---:|---:|---:|
| `ownership2` | **+47.340** | `[+30.784, +63.895]` | **+138.427** | **+91.088** | 7/8 | -24.383 | 8/11 |
| `private2` | +41.691 | `[+24.300, +59.081]` | +136.736 | +95.046 | 7/8 | -25.700 | 7/11 |
| `prefruit2` | -21.003 | `[-34.904, -7.102]` | +55.285 | +76.289 | 3/8 | -94.167 | 2/11 |
| `norx3` | -30.240 | `[-42.441, -18.038]` | -11.340 | +18.900 | 1/8 | -69.308 | 1/11 |
| `gold_adaptive` | -50.976 | `[-72.898, -29.054]` | +29.872 | +80.848 | 1/8 | -112.558 | 2/11 |
| `hybrid3` | -63.421 | `[-74.339, -52.502]` | -3.273 | +60.148 | 0/8 | -119.492 | 1/11 |
| `separated_denial` | -73.210 | `[-89.071, -57.350]` | +4.347 | +77.557 | 1/8 | -152.375 | 1/11 |
| `accumulate4` | -83.036 | `[-98.346, -67.727]` | -21.879 | +61.157 | 0/8 | -134.667 | 1/11 |

No non-resident controller passes all gates, so the preregistered confirmation block is not
opened.

## Analysis at different abstraction levels

### Map substrate

The productive result is not a one-seat artifact: `ownership2` gains +47.86 in seat zero and
+46.82 in seat one.  Its mean advantage is positive at every official height and rises from
+21.67 on height-eight maps to +74.27 on height-ten maps.  Height correlation with the 60 seed
effects is only +0.262 and initial-tree correlation is effectively zero, so a trivial geometry
selector cannot explain or capture the result.

Official-map fidelity changes magnitudes, but the old architectural ordering survives: coherent
two-worker farms produce, naive workforce scale does not, and hand-written denial destroys the
economy that funds it.  D33 therefore fixed a real evaluation defect without making the old
controllers strategically complete.

### Production

The resident averages 200.17 own score, 44.60 wood, 11.52 successful plants, and 2.00 maximum
workers.  `ownership2` averages 338.60 score, 81.58 wood, and 43.96 successful plants with the
same 1.99-worker mean.  Its advantage comes from renewable scheduling, not worker count.

Conversely, the nominally larger controllers fail to turn workforce into throughput.
`accumulate4` averages 3.50 workers but loses 21.88 own score versus resident; `hybrid3` averages
2.32 and loses 3.27.  This independently confirms that training capacity is downstream of a
productive scheduler, not a free source of strength.

### Opponent interaction

The farm's productivity creates a longer, richer shared game.  `ownership2` lets opponents add
91.09 score, 18.49 wood, and 1.06 successful plants relative to resident.  It remains locally
positive against seven opponents, but loses 24.38 against adaptive Gold.  Across the three rich
mechanism opponents its margin delta is +44.69 only because the weak native-three proxy is easy;
the same block's opponent-score delta is **+97.56**, far beyond the +10 gate.

This distinction matters: a positive aggregate margin against an uncalibrated mechanism panel is
not preservation of resident suppression.  D32's actual TestSession common-map farm diagnostic
was -42, +29, and -74 margin, mean -29.  D34 cannot override that field evidence; it explains which
local economic benefit failed to transfer.

### Denial opportunity cost

`prefruit2` is the cleanest causal bridge between production and denial.  Relative to its
`private2` parent it reduces opponent score by 18.757 and opponent wood by 2.878, but loses 81.451
own score and retains only 40.43% of the parent's gain over resident.  It also allows 2.401 more
opponent successful plants, so it does not extinguish the reproductive loop.  The resulting margin
is 62.694 points worse than the parent and 21.003 worse than resident.

Physical capacity separation is even weaker: it removes only 3.291 opponent score from adaptive
Gold's complete parent while retaining 14.55% of the parent's already-small own-score gain.  More
workers do not make denial free because their funding and routing consume the same productive
cycles.

### Tail and transfer

`ownership2` has 22 local catastrophes versus 34 resident catastrophes and negative-margin mass
8,016 versus 8,250.  This is useful mechanism evidence: the farm is not merely an average inflated
by easy wins.  It still fails the explicit opponent-suppression gate and contradicts the small
live common-map diagnostic.  The correct conclusion is an opponent-model/architecture transfer
gap, not permission to submit the farm.

The production/suppression Pareto frontier is exactly `resident`, `prefruit2`, and `ownership2`.
Every multi-worker witness is dominated.  The two nonresident frontier points expose a continuous
tradeoff but neither reaches the required region.

## Next experiment

D35 must test a **joint persistent-job scheduler interface** before another expensive PPO run.
The interface should:

1. make one joint allocation for all current workers at job boundaries rather than replace one
   primitive command;
2. expose renewable producer/funder, fell-and-bank, lineage-pressure, and later-training jobs;
3. retain job identity, target ownership, recent completion history, and the other workers'
   assignments in state;
4. value terminal own production and opponent renewable momentum separately; and
5. run from turn one on exact official maps against a field-shaped opponent mixture.

Its first discriminator is representation coverage and a closed-loop teacher/oracle upper bound,
not policy optimization.  It must prove that coordinated plans can preserve at least half of
`ownership2`'s production gain while bringing opponent score materially toward the resident before
PPO, distillation, packaging, TestSession, or Arena work is eligible.

## Reproducibility anchors

- protocol SHA-256:
  `fafd34f64dd6fce936fd708c8509fec57801d4f9a49d691fb8ab6b4f534c7dc4`;
- D34a amendment SHA-256:
  `ceb25035b96ee3a176bbe0d100892dbdeeedfb72d340ea8d51984e789b545bb6`;
- runner SHA-256:
  `115d1ed5187d19374639ba6f2671ee59d3a0e25172c04c5a7584f05950d2046b`;
- analyzer SHA-256:
  `0535bcf216ac6fe9fa9832ea1e56dc4730225afe019077d9afc85a8a5e76347e`;
- development TSV SHA-256:
  `a82df88cfbb39dbca071c5032018e1924e0bce056c5b8e1952f78df3478784ac`;
- development JSON SHA-256:
  `0cd39e9b9c93774ae2bc1b6543edf75d66ab820e83c406baaac45b5d367210bb`.

