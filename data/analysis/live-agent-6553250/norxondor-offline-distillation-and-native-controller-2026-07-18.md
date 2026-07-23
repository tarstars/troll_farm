# Norxondor offline distillation and native-controller verdict — 2026-07-18

## Decision

Do not build or submit a candidate from the current Norxondor reconstruction. The compact
supervised pieces fit comfortably, but the complete self-running controller does not reproduce
the replay state distribution and loses heavily against every opponent family. Direct online
Monte Carlo, trajectory value distillation, post-funding role repair, funding-timing changes, and
closed-loop native imitation are now separate measured failures rather than one unresolved idea.

The remaining positive signal is map geometry. On discovery seeds 322--401, a map-seat oracle
that selects worker three only when the second-worst opponent margin is positive chooses 19/160
groups. Expanded to opponent cells, it has 90.789% positive-margin precision, +7.697 mean margin,
+6.532 mean score, positive mean margin against all eight opponents, and a +1.300 worst-opponent
mean. The fitted map-only forest did not generalize, but only 19 positive groups were available.
The next experiment therefore scales this one representation before closing it.

The 62,725-byte resident, `cgauto/api_submit.py`, sealed map holdout, and arena were not changed.

## Results at different levels

### 1. Terminal option value

The exact resident and resident-plus-worker-three branches provide a useful offline teacher. A
per-cell hindsight oracle is strongly positive, but its label is opponent-dependent. Generic
trajectory forests were evaluated with contiguous blocked-seed and leave-one-opponent-family-out
folds at decision turns 3, 5, and 10.

| Prefix | Best blocked-seed precision | Selected cells | Margin delta | Score delta | Opponent-family precision | Verdict |
|---|---:|---:|---:|---:|---:|---|
| turn 3 | 79.22% | 154/1,280 | +5.702 | +5.595 | below gate | reject |
| turn 5 | 82.57% | 109/1,280 | +4.571 | +4.209 | below gate | reject |
| turn 10 | 91.43% | 70/1,280 | +3.948 | +2.937 | 73.08% | reject |

Turn 10 proves that more observation improves within-opponent prediction. It does not solve
transfer: leave-one-opponent-family-out precision misses the frozen 90% requirement by 16.92
points. No configuration passed both fold families, so no expression was frozen and no fresh
validation block was opened.

### 2. Map-only robust value

Removing opponent transitions and labeling each seed-seat group by its second-worst margin
changes the question from “will this branch win this modeled opponent?” to “is this map broadly
suitable for the worker-three economy?” On 80 seeds / 160 groups:

- 19 groups are lower-quartile positive;
- their expanded actual precision is 90.789%;
- the complete oracle policy gains +7.697 margin and +6.532 score;
- all eight opponent means are positive, with a +1.300 minimum;
- the best blocked-seed forest selects 72 cells at 59.722% actual precision and gains only +0.405
  margin / +0.007 score, so 0/10 configurations pass.

The oracle clears the whole-policy gate while the learner fails. With only 19 positive groups,
this is a sample-size/representation discriminator, not evidence for a candidate.

### 3. Funding and post-funding control

The recovered two-funder ladder makes worker three physically attainable. It does not by itself
define a robust economy.

- 26 fixed/adaptive post-funding role policies: 0 pass.
- 20 funding-profile × continuation policies: 0 pass.
- Best funding result, `two_oldest_t10__role_repair`: +48.213 margin, +73.963 score, 2.613 mean
  workers, and 7/8 nonnegative opponents, but -44.300 against Adaptive Gold.
- Worker three occurs in 61.25% of those cells at median turn 92. This is close to Norxondor's
  replay median near turn 101, so the missing mechanism is not merely a later `TRAIN` trigger.

The funding detour displaces productive work for roughly ninety turns, and the tested role
repairs do not recover that opportunity cost across opponents.

### 4. Compact policy representation

Source size is not the limiting factor.

- The compact categorical intent tree uses 107 nodes and an estimated 1,923-byte expression. It
  reaches 76.937% held-game accuracy, 0.530 macro F1, 75.456% worst-fold accuracy, and 0.502
  worst-fold macro F1.
- The CHOP selector retains its research gate with 128 nonzero weights.
- The HARVEST selector retains its research gate with 32 nonzero weights.

These components describe replay decisions under teacher states. They do not establish that the
same decisions regenerate those states.

### 5. Complete native controller

The research controller joined the exact workforce ladder, compact intent tree, persistent goals,
compact CHOP/HARVEST rankers, equivalent DROP/MINE endpoints, and deterministic planting. Four
targeted repairs added direct-work persistence, an explicit iron miner, and safer PICK/PLANT
commitment.

The best repaired full variant reaches 2.488 mean workers (13 one-worker, 22 two-worker, 38
three-worker, and 7 four-worker games), but still loses -172.663 paired margin and -97.263 paired
score versus resident continuation. Every opponent-family delta is strongly negative. Its mean
action mix remains far from the replay teacher: about 38 CHOP and 68 PICK actions per game versus
roughly 159 CHOP and 17 PICK in replay-derived targets.

This is autoregressive covariate shift. The classifier is accurate enough on visited teacher
states, but small goal errors change inventory, geometry, and later available actions. Further
manual action-count tuning would be imitation by outcome fitting, not a validated mechanism.

## What is now closed

| Attack angle | Evidence | Status |
|---|---|---|
| Online terminal Monte Carlo | strong teacher; 209 ms median / 279 ms p95 | closed by 50 ms limit |
| Generic turn-3/5/10 trajectory value model | no model passes both blocked-seed and opponent-family gates | closed for current features |
| Post-funding role reassignment | 0/26 policies robust | closed |
| Funding timing/profile | 0/20 policies robust | closed |
| Compact replay intent/goal encoding | compact components pass, complete controller collapses | closed as direct imitation |
| Map-only robust opening selector | strong oracle, 19 positive groups, learner fails | scale once, then decide |

## Phase-15 discovery expansion

Seeds **1000--1299** are designated as new discovery/training data before generation. They are
not validation or holdout data and may never be cited as such later. Seeds 402--999 remain
unopened by this phase, and the separate sealed official-map holdout remains sealed.

Protocol:

1. Generate turn-three exact terminal labels for resident continuation and the recovered
   worker-three continuation, both seats, and all eight local opponents: 4,800 opponent cells / 600
   map-seat groups.
2. Use only turn-one map geometry. No opponent identity, trajectory, embedded opponent model, or
   manual seed list may enter the features.
3. Keep the robust label fixed: the second-worst of eight opponent margin deltas must be positive.
4. Reuse the existing ten-configuration forest grid and contiguous blocked-seed evaluation.
5. Require at least 90% actual selected-cell precision, at least 5% selection, positive score and
   margin, at least five nonnegative opponent means, and worst opponent mean at least -5.
6. If no configuration passes, close map-only selection at this representation. If one passes,
   freeze its exact expression and protocol before designating any fresh validation range.
7. Do not build a candidate, open the sealed holdout, or write to the arena from discovery results.

### Result

The run produced the predeclared 4,800 cells / 600 groups exactly. There are 65 lower-quartile-
positive groups, so the positive sample grew from 19 to 65. The oracle remains valuable as a
policy (+4.591 margin, +3.993 score, all eight opponent means positive, +1.338 worst-opponent
mean), but its expanded positive-margin precision is 89.615%, just below the frozen 90% bar.

None of the ten map-only forests passes. The highest-ranked forest selects 408/4,800 cells at
47.059% actual precision, -0.277 margin, +0.562 score, only 3/8 nonnegative opponent means, and a
-3.562 worst-opponent mean. Increasing the group sample by 3.75× therefore does not repair the
learner; the original failure was not merely 19-positive-example variance.

**Verdict:** close map-only worker-three selection for the current geometry representation. Do
not expand the forest grid, pool the consumed ranges for more tuning, designate validation data,
build a candidate, or open the holdout.

## Evidence

- `norxondor-value-model-expanded-discovery-322-401-2026-07-18.json`
- `norxondor-value-model-turn5-expanded-discovery-322-401-2026-07-18.json`
- `norxondor-value-model-turn10-expanded-discovery-322-401-2026-07-18.json`
- `norxondor-robust-geometry-value-discovery-322-401-2026-07-18.json`
- `norxondor-resident-role-study-smoke-322-326-2026-07-18.json`
- `norxondor-resident-funding-study-smoke-322-326-2026-07-18.json`
- `norxondor-compact-intent-study-2026-07-18.json`
- `norxondor-goal-selector-study-2026-07-18.json`
- `norxondor-native-controller-repair4-322-326-2026-07-18.json`
- `norxondor-resident-three-worker-labels-expansion-1000-1299.tsv`
- `norxondor-robust-geometry-value-expansion-1000-1299-2026-07-18.json`
