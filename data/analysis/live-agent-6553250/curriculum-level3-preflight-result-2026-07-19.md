# Curriculum Level 3 exact preflight result — 2026-07-19

## Verdict

Pass.  The frozen renewable two-troll environment is feasible across the exact 2,000-seed
preflight bank and remains strongly discriminative.  Behavior cloning from the accepted Level-2
checkpoint is authorized; PPO and any live transfer are not yet authorized.

## Frozen-bank results

The exact interval is seeds 2,009,000--2,010,999, with 2,000 episodes, 100 vector environments,
and a 240-referee-turn cap.

| Metric | Deterministic teacher | Random legal, RNG 71 | Teacher gate |
|---|---:|---:|---:|
| Overall success | 2,000/2,000 (100.00%) | 0/2,000 (0.00%) | >=98% |
| Nontrivial success | 1,415/1,415 (100.00%) | 0/1,415 (0.00%) | >=97% |
| Worst height success | 100.00% | 0.00% | >=95% |
| Tracked crop created | 100.00% | 16.60% | >=98% |
| Tracked crop later harvested | 100.00% | 1.40% | >=98% |
| Median training turn | 18 | 1 | diagnostic |
| Median successful completion turn | 47 | n/a | diagnostic |
| Median post-training score gain | 16 | 0 | required objective is 12 |

Every teacher height bucket (8, 9, 10, and 11) is 100%.  The random controller's early median
training turn reflects the 585 reset-affordable cases and does not indicate task progress: it
never meets the joint crop, harvest, and score objective.  Thus the task cannot be passed by the
automatic TRAIN transition alone.

## Reproducibility anchors

- teacher control:
  `curriculum-level3-teacher-2009000-2010999-exact.json`
  (`348b39db50907fc214a6af3a6555109fc736f64e5aca46b4926b60fea2037994`);
- random control:
  `curriculum-level3-random-2009000-2010999-exact.json`
  (`bbe8a17c42777b0c77a3c551fc2bd1bbae06f8d4c2fc7271c35fac48a3e49702`);
- frozen protocol:
  `curriculum-level3-renewable-protocol-2026-07-19.md`
  (`b43a586e2e8593b5044a219271721ece9c9d273f7cbf4d2b63d7cd86e59f896d`).

The teacher produced 170,800 sequential policy decisions at 63,687 decisions/s; random produced
647,300 at 72,832 decisions/s.  These controls were generated after the protocol was frozen and
before any Level-3 learning labels were consumed.

## Next eligible experiment

Initialize the 34,926-parameter spatial actor from the accepted seed-67 Level-2 confirmation
checkpoint and behavior-clone the Level-3 teacher for exactly 600,000 streamed decisions beginning
at seed 6,000,000.  Evaluate deterministically on this now-consumed preflight bank and apply the
frozen clone gate before generating the PPO prospective bank.
