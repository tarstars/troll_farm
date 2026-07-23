# D35c provenance-aware competitive-bundle oracle — result (2026-07-20)

## Verdict

**Provenance is causally useful, but one-shot bundles remain insufficient.**

The enriched hindsight oracle selects a competitive target bundle at 174/640
roots (27.19%).  Relative to the exact paired generic oracle, it adds **+7.798
seed-clustered margin**, removes **7.963 opponent score**, and changes own score
only -0.164.  The effect is positive on all 20 independent development seeds and
spans all eight opponent families.

It still fails the frozen representation gate.  Opponent reduction versus the
farm reaches **-13.906**, short of -20; opponent excess over the independent
resident remains **+88.194**, above +65; and incremental suppression versus the
generic oracle is -7.963, short of -10.  Confirmation seeds
9,300,010--9,300,029 remain unopened.  No policy, candidate, TestSession game,
submission, or Arena action follows.

## Integrity and support

- The final seed-9,300,000 row repeats are byte-identical at
  `3f557dfd429a4bc58665a70157058990267321bb740ad2e3494a94b0a56a28e9`;
  their scenario manifests are byte-identical at
  `25643ece9961cd27e10100a2fad0fabad1913226de40fe335ac3376e7b25acb3`.
- The initial outcome-blind row-count audit showed that ten seeds could not reach
  the preregistered 10,000/5,000 evidence floors.  D35c.1 added a disjoint fresh
  development block 9,300,040--049 before either oracle was computed; the
  original confirmation block stayed sealed and every value threshold stayed
  fixed.
- The final 20-seed matrix contains all 320 tasks, all 640 roots, 640 controls,
  12,376 generic bundles, and 8,443 competitive extension bundles.
- Exact attribution covers every live root cell.  There are zero prefix
  attribution failures, root cell mismatches, control mismatches, duplicate
  keys/options, collisions, invalid direct commands, inconsistent deltas, train
  successes, or branches above three workers.
- Competitive targets are exposed at 426 roots; all 426 expose an exclusive
  opponent `FELL_BANK` target and 204 expose an opponent
  `HARVEST_BANK`/`RENEW` target.  Every support gate passes.
- Thirteen focused Rust tests and five analyzer tests pass.

## Paired outcome

| Seed-clustered measure | Generic oracle | Provenance oracle | Increment |
|---|---:|---:|---:|
| Margin gain vs farm | +24.014 | **+31.813** | **+7.798** |
| Own-score delta vs farm | +18.070 | +17.906 | -0.164 |
| Opponent-score delta vs farm | -5.944 | **-13.906** | **-7.963** |
| Own-score delta vs resident | +162.423 | +162.259 | -0.164 |
| Opponent-score delta vs resident | +96.156 | **+88.194** | **-7.963** |

The incremental margin interval across the 20 seed means is
[+5.299,+10.298].  The incremental opponent-score interval is
[-11.312,-4.613].  Nineteen seed means reduce opponent score and one is +0.344;
all 20 margin means improve.  This is strong paired evidence that provenance is
a real state/action factor rather than an incidental label.

The enriched oracle is positive against every opponent family, from +23.263
margin against resident to +38.750 against Compact Gold.  It selects 185
exclusive opponent targets across 12 role tuples.  No ambiguous target is
selected; ambiguity is preserved and reported rather than reassigned.

## Frozen gates

Thirteen gates pass, including competitive activation, margin, own production,
resident-relative own score, opponent breadth, role/target breadth, catastrophe
frequency, and negative-margin mass.  Three fail:

| Failed gate | Result | Requirement |
|---|---:|---:|
| Opponent-score delta vs farm | **-13.906** | <=-20 |
| Opponent-score excess vs resident | **+88.194** | <=+65 |
| Incremental opponent suppression | **-7.963** | <=-10 |

Tail behavior improves: catastrophes are 5/640 for both generic and enriched
oracles versus 12/640 farm controls.  Negative-margin mass falls from 7,052 farm
to 3,981 generic and 3,600 enriched.  The rejection is specifically about
insufficient rival-loop suppression, not mean value or safety regression.

## Analysis by abstraction level

### Causal mechanism

Holding maps, roots, opponent prefixes, executor, continuation, and generic
options fixed, adding only attributed competitive targets buys nearly eight
opponent points at negligible own cost.  The D35b inference is confirmed:
creator provenance belongs in the target representation.

### Action horizon

The remaining gap is too large to plausibly be a target-ranking tie.  A single
bundle touches one or two rival crops, then returns permanently to the farm.
Even a terminal oracle cannot accumulate enough denial under that horizon.  The
failure localizes the next missing factor to **repeated job-boundary allocation**,
not more target slots or different ownership weights.

### Production/suppression frontier

The enriched oracle retains +162.26 own score over resident, leaving ample
economic headroom, but one intervention spends only 13.91 points on suppression.
This is not an inherent need to abandon production; it is an inability to
reallocate workers again after the first jobs finish.

### Workforce

Training was removed prospectively because D35b had zero successful or selected
train goals.  D35c's added value again comes entirely from the existing two
workers.  Worker three should remain outside the next discriminator until a
repeated two-worker scheduler establishes a renewable funding/denial trajectory.

### Learning boundary

The provenance factor now has a valid causal teacher signal, but fitting PPO to
one-shot labels would optimize a teacher known to miss the terminal target
region.  Learning remains premature.  The next upper bound must first validate
repeated decisions.

## Next experiment

D35d should evaluate a bounded **greedy repeated job-boundary oracle** on fresh
official seeds:

1. start from the same productive two-worker substrate at the first turn-50
   root;
2. enumerate the frozen D35c generic plus provenance catalog;
3. use exact terminal rollout only to choose the next complete bundle;
4. execute that bundle on the live branch, preserve provenance and opponent
   history, and replan when all assigned jobs end;
5. stop after a fixed small epoch cap or when control wins; and
6. compare one-shot, repeated, farm, and resident references on exact common
   tasks.

If repeated allocation closes the two suppression gates, the resulting epoch
states and choices become the first justified scheduler-learning dataset.  If
it fails, close this productive-farm substrate and move to a resident-based
joint objective.  Do not enlarge D35c's target quotas or retune its thresholds.

## Evidence and SHA-256

- protocol and D35c.1 amendment;
- runner wrapper and shared implementation child;
- analyzer and focused tests;
- two development TSV/manifest blocks, repeat artifacts, and JSON result.

- runner wrapper: `c9f3ce2f7f43e240a48e8381a2383cd47e8a6e1690215e9d80dc4dd66ded22b4`;
- implementation: `9babd0cc0be33a7facff72515a4596d5fee77c2a32098ea24678d56714c5aaa3`;
- analyzer: `20e71b18a1a0ec163980d823d9872d320a8e476d15a12742b2166e838be536c1`;
- development block A: `315dcffca7d66d8e2e4327b09cc82cd06c6399dab8f163a4e70942a383f76e2b`;
- development block B: `50bb90b7925f5f9b7cbfc0c108d97de38f4442bb9014af90c6915dd5db944ffa`;
- result JSON: `cdaa04f2fba0581e6520a7f74ef56d22abb784646ae32c6d6bf002e688b3d3a6`.
