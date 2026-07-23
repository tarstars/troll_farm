# D98a bounded whole-game joint-assignment population — result

Date: 2026-07-21  
Verdict: **fail; close independent per-worker linear scoring on this interface**

## Outcome

D98 is mechanically valid and close to the requested whole-game headroom, but it does not pass the
frozen conjunction. Two independent 20-worker runs produced byte-identical 129 x 128 matrices and
byte-identical independent D40 baselines. The exact-zero policy reproduces every D40 terminal,
action-plane, action-hash, and state-hash field. Population reconstruction, matched one/four
weights, budgets, hashes, reward identities, worker caps, provenance, deposit prediction, catalog,
reservation, safety, and action accounting all pass.

The value result is strong but remains an upper bound:

| Metric | Result | Required | Verdict |
|---|---:|---:|---|
| Four-use oracle gain over D40 | +46.820 | >= +50 | fail |
| Strict D40 improvements | 126/128 = 98.44% | >= 85% | pass |
| Worst opponent-family gain | +22.438 | >= +15 | pass |
| Mean own / opponent delta | +28.516 / -18.305 | >= 0 / <= 0 | pass |
| Worker-three / crop rate | 86.72% / 100% | >= 85% / 100% | pass |
| Increment beyond one-use oracle | +9.453 | >= +10 | fail |
| Four-use oracle strictly beats one-use | 89/128 | >= 32 | pass |
| Four policies with at least two strict wins | 23 | >= 12 | pass |
| Selected rows with >=2 interventions | 124 | >= 24 | pass |
| Selected rows with a joint batch | 12 | >= 16 | fail |

The oracle mean margins are 33.281 for D40, 70.648 for one intervention, and 80.102 for four.
Selected four-use rows cover all four concrete jobs, natural/own/opponent provenance, both seats,
and all eight opponent families.

## Activity diagnosis

| Population gate | Result | Required | Verdict |
|---|---:|---:|---|
| Crops in every policy-task | 16,512/16,512 | all | pass |
| Four-use policies retaining worker three | 64/64 | >=56 | pass |
| Matched pairs changing at least half of hashes | 52/64 | >=56 | fail |
| Four-use policies spanning 3 jobs and 2 provenances | 21/64 | >=48 | fail |
| Four-use policies repeating in at least 25% of tasks | 59/64 | >=48 | pass |
| Four-use policies joint in at least 10% of tasks | 23/64 | >=32 | fail |
| Fixed mean-margin range | 24.055 | >=25 | fail |

The best fixed random policy is descriptive and unselectable. It gains only +3.188 over D40 and
collapses onto one class: all 330 interventions are `fell:natural`; it creates a joint batch in
only 4/128 tasks. This explains the population failures. A shared linear score applied independently
to each worker learns a stable class preference, not a coordinated assignment. D97's terminal
interaction exists, but D98's scorer cannot express the first/second option combination directly.

## Decision and next hypothesis

Close the D98 random initialization. Do not select a fixed arm, tune weight scale, budget, catalog,
or thresholds on seeds `9,821,000--9,821,007`, and do not start PPO, CEM, imitation, candidate
construction, TestSession, Arena, submission, or resident replacement from these rows.

The next eligible representation is a **pair-aware batch action**. At the first eligible Rate
worker it must enumerate collision-safe `(first option, second option)` assignments by applying
each first option to a cloned exact state, rebuilding the second catalog with updated reservations,
and scoring the pair as one choice. It then executes the committed pair and returns to exact D40.
This directly represents the D97 interaction that D98 missed. A fresh preregistered random-function
class on new maps must clear mechanics, broad joint activity, and incremental repeated headroom
before any learner opens.

## Reproducibility anchors

- protocol: `6573a30310a55db9808568b3f2f0d8e03eb8c9baafe3b54aea91a7d6d4c8bad7`;
- lock: `296580b68eda297722b023b9646dce2cfeed14948e642276030c7e3372136b17`;
- population run matrix (both repeats):
  `8eb2d8cc8c14752843c1fcfa46158bfb4af0641a39406248ffe026db89c38b20`;
- baseline matrix (both repeats):
  `2af1cd7d9aff430a1ae060042e0cbd0c7149fdb10a33df2f72572e4e06259cbf`;
- analyzer: `72d6644a2575852315c11f708ab504ab79dfc15800b79c37702ca570d984f10f`;
- result JSON: `daf9b4035559ca6e32c2d5704fab6a2e222064573042c1477291837e3c44d4fe`.

