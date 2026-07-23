# D99a pair-aware batch-action population — result

Date: 2026-07-22  
Verdict: **fail; pair activity is validated, from-scratch pair replacement is closed**

## Outcome

D99 is mechanically exact. Two independent 20-worker executions produced byte-identical
129 x 128 matrices, and their independent D40 baselines are byte-identical to the pre-change D98
reference baseline. Both zero policies reproduce every D40 terminal, action-plane, action-hash, and
state-hash field. All 16,512 committed-pair rows pass budget, pair/job/provenance, preview state,
worker, observation, catalog, legality, reward, crop-safety, transaction, and worker-cap checks.

Pair-aware scoring fixes D98's activity problem:

| Activity gate | D99 | Required | D98 same concept | Verdict |
|---|---:|---:|---:|---|
| Matched pairs changing >=50% of task hashes | 56/64 | >=56 | 52/64 | pass |
| Four-use policies spanning 3 jobs / 2 provenances | 48/64 | >=48 | 21/64 | pass |
| Four-use policies repeating in >=25% of tasks | 58/64 | >=48 | 59/64 | pass |
| Four-use policies joint in >=25% of tasks | 52/64 | >=48 | 23/64 at the easier 10% floor | pass |
| Four-use policies retaining worker three | 64/64 | >=56 | 64/64 | pass |
| Crop-safe policy-task rows | 16,512/16,512 | all | all | pass |
| Fixed mean-margin range | 23.844 | >=25 | 24.055 | fail |

The best fixed random pair policy is descriptive and unselectable. It gains only +2.102 over D40,
despite using all four jobs and three provenance classes. Broad action expression therefore does
not imply a useful fixed controller.

## Value and direct architecture result

| Headroom metric | Result | Required | Verdict |
|---|---:|---:|---|
| D99 four-use oracle gain over D40 | +41.570 | >=+50 | fail |
| Strict D40 improvements | 112/128 = 87.50% | >=85% | pass |
| Worst opponent-family gain | +22.062 | >=+15 | pass |
| Mean own / opponent delta | +25.227 / -16.344 | >=0 / <=0 | pass |
| Worker-three / crop rate | 89.84% / 100% | >=85% / 100% | pass |
| Increment beyond D99 one-use oracle | +2.672 | >=+10 | fail |
| Four-use oracle strictly beats one-use | 59/128 | >=32 | pass |
| Four policies with at least two strict wins | 35 | >=12 | pass |
| Selected rows with >=2 interventions | 92 | >=24 | pass |
| Selected rows with a joint pair | 80 | >=32 | pass |
| D99 minus same-task D98 four-use oracle | -17.133 | >=+5 | fail |

Mean margins are 43.773 for D40, 82.672 for the D99 one-use oracle, 85.344 for the D99 four-use
oracle, and 102.477 for the frozen same-task D98 four-use oracle. D99 beats D98 on only 44/128
task margins. Explicit pair interactions make joint behavior available but replace a stronger
independent decision surface; they do not add repeated value on their own.

## Decision and next hypothesis

Close the from-scratch D99 random pair population. Do not select a fixed policy, tune its random
scale, budget, pair catalog, feature count, or gates on seeds `9,822,000--9,822,007`, and do not
train PPO, CEM, imitation, or a larger pair scorer from it.

The next eligible test is a **strict-superset anchored residual**. Preserve each frozen D98
independent scorer and its exact decisions as an explicit parent. Add a sparse pair-interaction
residual that can propose an override but has an exact-zero variant reproducing the parent. The
population must include parent and residual rows on the same fresh tasks, so the only relevant
oracle is incremental residual value over its parent—not a new random population versus D40. This
separates “pair interaction adds information” from D99's confound of discarding the independently
useful surface.

## Reproducibility anchors

- protocol: `7263a04fdef43f0ecd4cdb74aa377c3417eafe81e03a591f459db539cdc519b8`;
- population matrix, both repeats:
  `2df668a0fb200984ad7e9acfe85c79812181de82af3968f24bc83f5dfb420c3a`;
- D99/D98 baseline:
  `f7fb67f60cfa1787e44bdcdec5a4dfff63566f1eecaeb1bf95186397f14a8951`;
- frozen D98 reference matrix:
  `991bf168ebd03f41a775d6739b18c25f0954b2b075a24c200c75d5e1919c809b`;
- analyzer: `ca90d2e4a4baefe275d9133c1b9aa82ef0860c924fd68fc16f869c667ddd455b`;
- result JSON: `62eec1ae3233e7bc12a832ae76f484105ee13e88475128793963cae25a398412`.

