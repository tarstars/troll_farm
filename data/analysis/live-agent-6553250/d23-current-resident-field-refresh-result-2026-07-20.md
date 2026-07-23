# D23 current-resident field refresh — result (2026-07-20)

## Outcome

The read-only refresh is complete and passes every frozen readiness gate.  The current exact
stable resident, agent `6561795`, was rank **34** at **23.05** when read.  All 80 requested finished
battles parsed, every row belongs to the expected agent, there were no fetch failures or unknown
replay-diff updates, and all terminal scores and effect telemetry are present.

The frozen branch rule selects a **coherent production/opening/workforce experiment**, not a new
tail-risk selector.  Catastrophes meet three of the four anti-compounding conditions but occur in
7/80 games (**8.75%**), just below the predeclared 10% threshold.  This is not evidence that the
tail disappeared: those seven games still carry **61.12%** of all negative-margin mass and retain
the same late opponent-compounding mechanism.

No candidate was constructed and no Arena action was taken.

## Field result

| Cohort | Games | Mean margin | Our score | Opponent score | Our workers | Opponent workers | Our plants | Opponent plants |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| All | 80 | +2.64 | 182.65 | 180.01 | 2.00 | 2.43 | 11.15 | 23.90 |
| Wins | 42 | +62.21 | 191.00 | 128.79 | 2.00 | 2.10 | 10.69 | 22.43 |
| Ordinary losses | 31 | -30.13 | 172.29 | 202.42 | 2.00 | 2.65 | 11.77 | 22.52 |
| Catastrophic losses | 7 | -209.71 | 178.43 | 388.14 | 2.00 | 3.43 | 11.14 | 38.86 |

The resident won 42, tied 0, and lost 38.  Its final production is unusually stable across
outcomes: own score varies from 172.29 in ordinary losses to 191.00 in wins, every cohort ends with
exactly two workers, and planting remains near eleven.  The outcome swing is overwhelmingly on the
opponent side.  Catastrophic opponents end with 388.14 score, 95.57 wood, 3.43 workers, 38.86
plants, and 69.57 harvested fruit.

## Analysis by abstraction level

### Ladder and measurement

The source identity is unchanged from the restored-resident observation: 62,725 bytes, SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`.  Its observed rank moved
from 41 at 22.49 to 34 at 23.05.  The older 80-game batch had +35.11 mean margin whereas the new
batch has +2.64.  Because maps and opponents are not paired, this difference is field-mixture
variation, not a policy effect.  Rank/score is the relevant external trend; batch margins diagnose
mechanisms rather than measure a causal improvement.

### Whole-game outcome

Ordinary losses are the larger count, but catastrophes dominate downside.  The seven catastrophic
games span five opponents, have 62.50 more opponent wood than non-catastrophic games, and account
for 61.12% of negative-margin mass.  Consequently an average-only objective can look acceptable
while leaving the ladder-limiting tail intact.

### Temporal dynamics

Both loss cohorts begin ahead.  In ordinary losses the resident leads 73.10 to 58.35 at turn 100,
then trails 133.61 to 141.70 at turn 200 and 202.47 to 247.07 at turn 300.  In catastrophic games
it leads 55.29 to 26.00 at turn 100 and 87.00 to 68.57 at turn 150, but trails 118.29 to 154.43 by
turn 200 and, among the five games reaching turn 300, 200.20 to 441.80.  The actionable boundary
is therefore a midgame transition after a viable opening, not a generic turn-one failure.

### Economy and workforce

The resident is a fixed two-worker, roughly eleven-plant economy.  Losing opponents scale to 2.65
workers in ordinary losses and 3.43 in catastrophes.  More importantly, their complete production
system scales with the workforce: catastrophic opponents create 38.86 crops and harvest 69.57
fruit.  This supports a joint policy-level intervention involving renewable supply, timing,
worker roles, and continuation targets.  It does **not** reopen isolated forced-TRAIN patches,
which prior experiments already rejected.

### Interaction and tail mechanism

Catastrophic opponents collect 78.14 wood from their own planted trees, 56.96 more than the
non-catastrophic cohort.  Although 38.43 of their 38.86 crops are within the resident's 20-turn
reach bound at birth, the resident contacts only 21.77%; its non-catastrophic interception rate is
47 percentage points.  The anti-compounding mechanism remains real, but prior crop-only patches
did not transfer strongly enough.  It should be evaluated as part of a complete continuation, not
retuned as another isolated priority coefficient.

### State selection and geometry

The best descriptive early rule, turn-100 opponent workers at least three and harvests at least
ten, finds 4/7 catastrophes among 13 selected games: 30.8% precision and 57.1% recall.  That is far
too weak for deployment.  Catastrophes also have fewer apple trees, a longer shack-door distance,
less affordable movement, and lower starting plum, but there are only seven positive rows.  These
features are contexts for prospective stratification, not a fitted opening selector.

### Project-level conclusion

The plateau is not a lack of small candidate ideas.  The project has already rejected direct extra
workers, fixed farm-first openings, early sparse selectors, crop-only denial, low-level resident
substitution, and end-to-end competitive PPO.  The missing abstraction is a **coherent macro
option** that keeps the resident's strong early lead but changes the entire midgame production and
interaction regime.  Before learning a selector, the option itself must prove robust terminal
value from shared phase-boundary states.

## Frozen decision and next experiment

D23 follows its predeclared rule and opens D24 on the structural branch:

1. retain the exact resident as the early-game control;
2. define a small library of complete, already-existing midgame continuations rather than unit
   command patches;
3. fork common simulator states at fixed midgame boundaries and run exact terminal rollouts under
   multiple opponent policies and both seats;
4. require at least one continuation to improve held-out mean and tail risk without a material
   worst-opponent regression before building any contextual selector; and
5. close the option family immediately if only an in-sample oracle, rather than a robust component,
   has value.

This experiment is deliberately distinct from the failed turn-3/5/10 worker-three selector: it
tests whole-policy continuation value after the observed reversal boundary.

## Evidence

- `d23-current-resident-field-refresh-protocol-2026-07-20.md`;
- `d23-current-resident-field-refresh-2026-07-20.json`;
- `recent-resident-restore-field-census-2026-07-19.json`;
- `recent_resident_field_census.py`.
