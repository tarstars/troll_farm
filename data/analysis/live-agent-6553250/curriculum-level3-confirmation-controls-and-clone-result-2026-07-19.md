# Curriculum Level 3 confirmation controls and clone result — 2026-07-19

## Verdict

Pass.  The independently frozen bank is feasible and discriminative, and the complete seed-79
transfer clone reproduces the discovery clone on new labels and evaluation seeds.  The unchanged
confirmation PPO is authorized.  Level 3 and all live changes remain unauthorized.

## Frozen controls

Exact seeds 2,013,000--2,014,999 were evaluated before clone labels were consumed.

| Metric | Teacher | Random legal, RNG 79 |
|---|---:|---:|
| Overall success | 2,000/2,000 (100.00%) | 0/2,000 (0.00%) |
| Nontrivial success | 1,415/1,415 (100.00%) | 0/1,415 (0.00%) |
| Worst height success | 100.00% | 0.00% |
| Tracked crop created | 100.00% | 16.05% |
| Renewable harvest | 100.00% | 0.95% |
| Median training/completion turn | 18/46 | 1/n/a |
| Median score gain | 16 | 0 |

Teacher control hash:
`c95c899c02d54359eee68d058bd775b0de0aff7efa92a6aaa2dce3e1ba984a5f`.
Random control hash:
`bd6e0bd54aba7fd86aefc35ddb630807a2c118420c17c2adb93ea8c023da6bbc`.

## Independent clone

The clone initialized from the accepted Level-2 seed-67 checkpoint, used model/shuffle seed 79,
and consumed exactly 600,000 online teacher decisions beginning at stream 6,400,000.  All other
settings match discovery.

| Metric | Seed-79 clone | Frozen clone gate | Discovery clone |
|---|---:|---:|---:|
| Overall success | 1,905/2,000 (95.25%) | 75% | 95.20% |
| Nontrivial success | 93.99% | 70% | 95.12% |
| Worst height success | 94.60% | 65% | 94.01% |
| Tracked crop created | 95.65% | 80% | 95.40% |
| Renewable harvest | 96.15% | 70% | 96.35% |
| Paired teacher median delay | 0 turns | <=35 | 0 turns |

Median training/completion turns are 18/48 and median score gain is 16.  The final chunk reaches
97.10% teacher agreement.  Label counts again include 102,331 CHOP, 37,351 DROP, 22,010 HARVEST,
7,508 BANANA PLANT, and 7,515 BANANA PICK actions, independently ruling out MOVE-only collapse.

Wall time is 281.16 seconds, process CPU time 3,803.46 seconds, and aggregate host utilization
67.64% of 20 logical CPUs.

## Reproducibility anchors

- frozen confirmation protocol:
  `d0e0c35cd2b86b3f14d5ba3675541578dcb21aba77e5c44334be341dc753f74d`;
- accepted Level-2 initialization:
  `8a831f6f7878eef898af4377530c291e577cc58750860c20c89a9005a5e19926`;
- independent clone checkpoint:
  `cbf7626290e1e64b583703da5397efb7db5b1bf76f86788a42716c37a6a61fbb`;
- exact clone evaluation:
  `955df8ccc6563ab5e54e9807b30185e449478399667c7c64c272c71e436d05c1`;
- clone training summary:
  `3d6668ed4c9b8cc05697cf44d2e8c7ab1ec14b87cdfe433a4cc5f8c6f10ddbc1`;
- frozen behavior-clone source:
  `64bfa27908c72c577a61e82434c9e234c4cd902b8f2fea6afb703718dd2ed791`.

## Next eligible experiment

Initialize PPO from this exact clone and consume four million decisions beginning at stream
6,500,000 with model seed 79 and the frozen prospective bank.  Apply the unchanged Stage-A safety
stop, final confirmation thresholds, and strict role-action audit.
