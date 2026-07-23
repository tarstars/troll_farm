# Curriculum Level 3 independent confirmation result — 2026-07-19

## Verdict

Pass.  The independently seeded clone, PPO run, exact-bank functional evaluation, and strict
role-action audit all clear their frozen prospective gates.  Together with the seed-61 discovery
run, this accepts Curriculum Level 3: a learned two-role controller reliably trains a standard
chopper, operates the starter farmer and worker jointly, creates a BANANA crop, harvests renewable
supply, and earns the required post-training score on held-out maps.

This result accepts only the curriculum abstraction.  It does not change the resident, claim live
transfer, or authorize an Arena submission.

## Independent functional result

The deterministic seed-79 actor was evaluated once on exact seeds 2,013,000--2,014,999 (2,000
episodes, 240 referee turns).  The teacher and random-legal controls were generated and hashed on
the same bank before any confirmation learning labels were consumed.

| Metric | Confirmation PPO | Frozen gate | Margin |
|---|---:|---:|---:|
| Overall success | 1,989/2,000 (99.45%) | 85% | +14.45 pp |
| Nontrivial success | 1,407/1,415 (99.43%) | 80% | +19.43 pp |
| Worst height success | 99.20% | 70% | +29.20 pp |
| Tracked crop created | 99.50% | 88% | +11.50 pp |
| Renewable harvest | 99.80% | 85% | +14.80 pp |
| Advantage over random legal | +99.45 pp | diagnostic | — |
| Paired teacher median delay | 0 turns | <=30 | 30 turns |

The height buckets score 99.20% (8), 99.80% (9), 99.40% (10), and 99.40% (11).  Median
training/completion turns are 18/46 and median post-training score gain is 15.  The frozen teacher
scores 100% with median completion turn 46; random legal scores 0%, confirming that the bank is
both solvable and discriminative.

Stage A had already cleared its safety gate at one million decisions with 98.15% overall success.
The unchanged run completed four million decisions and improved by another 1.30 percentage points.

## Strict role-action audit

The independent audit replays the final checkpoint on the exact bank and scores exact spatial
commands only at post-training productive teacher opportunities.  Farmer waits on the tracked
unripe BANANA crop are exempt exactly as frozen in the protocol.

| Role/metric | Confirmation PPO | Frozen gate | Margin |
|---|---:|---:|---:|
| Chopper exact productive choice | 94.80% | >=60% | +34.80 pp |
| Farmer exact productive choice | 81.77% | >=60% | +21.77 pp |
| Chopper productive verb | 99.61% | diagnostic | — |
| Farmer productive verb | 94.14% | diagnostic | — |
| Combined unjustified current waits | 596 | <=20,000 | 19,404 |

There are 39,580 justified farmer waits on the tracked unripe crop.  They are excluded by the
precommitted exemption; no chopper waits are exempted.

## Reproduction comparison

| Metric | Discovery PPO | Confirmation PPO | Difference |
|---|---:|---:|---:|
| Overall success | 99.30% | 99.45% | +0.15 pp |
| Nontrivial success | 99.21% | 99.43% | +0.22 pp |
| Worst height success | 99.00% | 99.20% | +0.20 pp |
| Tracked crop created | 99.35% | 99.50% | +0.15 pp |
| Renewable harvest | 99.40% | 99.80% | +0.40 pp |
| Chopper exact productive choice | 95.43% | 94.80% | -0.63 pp |
| Farmer exact productive choice | 84.63% | 81.77% | -2.86 pp |
| Paired teacher median delay | 0 | 0 | 0 |

The two seeds agree at the behavior level despite disjoint model seeds, online streams, and exact
evaluation banks.  The modest action-agreement differences do not propagate into functional loss.
The useful conclusion is therefore not that this fixed recipe should be deployed, but that the
representation, masked actor, online teacher auxiliary, and PPO pipeline can learn a renewable
two-role economy reproducibly.

## Training observations

Across four million confirmation auxiliary labels, only 72 (0.0018%) were undefined because the
learner reached a state where the deterministic teacher command was illegal.  The frozen
legal-label rule skipped those rows; all valid labels remained, and all reported losses were
finite.  Wall time was 4,032.03 seconds and process CPU time was 56,266.56 seconds, equivalent to
69.77% of the 20-logical-CPU host.  Final evaluation processed 186,000 decisions in 17.20 seconds.

## Reproducibility anchors

- frozen confirmation protocol:
  `d0e0c35cd2b86b3f14d5ba3675541578dcb21aba77e5c44334be341dc753f74d`;
- teacher control:
  `c95c899c02d54359eee68d058bd775b0de0aff7efa92a6aaa2dce3e1ba984a5f`;
- random-legal control:
  `bd6e0bd54aba7fd86aefc35ddb630807a2c118420c17c2adb93ea8c023da6bbc`;
- independent clone checkpoint:
  `cbf7626290e1e64b583703da5397efb7db5b1bf76f86788a42716c37a6a61fbb`;
- final PPO checkpoint:
  `a0a0f4bd590175d45be4ec63a8394a47cbe475187d942906d4e01038a167b0df`;
- exact final evaluation:
  `9e32ac67602878642e302e4613e16f5ff490479ffb1d4bb80a5a36dc9d1ef45e`;
- full training summary:
  `a17212cb021e0cc6eec1294ed2c31d033aee256cd65ccff2312fd88a7fd14ffe`;
- strict action audit:
  `cbb25bda954820c0f3441658a37f1178336a37fee50e1ae5475ca2b54897e274`.

## Next experiment boundary

Do not tune Level 3 further: its residual failure rate is too small to be the current bottleneck.
The next curriculum should combine the already reproduced abstractions rather than add an opponent
simultaneously.  Randomize the requested first-worker recipe while retaining two-role renewable
operation and a waiting opponent.  This isolates whether one policy can condition economic
execution on a high-level recipe before opponent interaction introduces another source of error.
