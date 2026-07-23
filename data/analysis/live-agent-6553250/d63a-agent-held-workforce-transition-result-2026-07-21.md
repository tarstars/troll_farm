# D63a agent-held workforce-transition result (2026-07-21)

## Verdict

**The opening selector failed; the turn-100 selector passed.** Current top-policy workforce scale
is not transferable as a map/opening-only choice, but later third-worker creation is highly
predictable from a mature economy snapshot on agents excluded from model fitting.

This is a behavior-representation result, not evidence that adding a third worker improves score.
It opens one narrower offline ablation and does not authorize a candidate, confirmation access, or
any platform action.

## Integrity and population

D63a consumed only the 200 open selected-top-agent appearances from passed snapshot
`20260721T105508Z-d61p`. Each of 20 agents contributes exactly ten appearances. The frozen
identity-held split assigned all games from nine agents (90 rows) to discovery and all games from
eleven agents (110 rows) to validation. No agent identity, rank, name, outcome, final score, or
post-feature-time command entered either model.

All reconstructed state streams are exact, unknown diff updates are zero, and no sealed
confirmation product was enumerated or read.

## Behavior census

- 94/200 appearances (47.0%) create a third worker.
- 150 appearances reach turn 100 with exactly two workers, no earlier third worker, and at least
  150 game turns.
- 46/150 eligible appearances create a third worker after turn 100.
- The eligible discovery block contains 16 positives / 58 negatives; validation contains 30 / 46.
- Validation positives span seven agents and negatives span six, so the result is not supported by
  a single held-out policy.

## Frozen model results

| Model | Discovery AUC | Validation AUC | Validation balanced accuracy | Verdict |
|---|---:|---:|---:|---|
| Opening/map only | 0.830 | 0.479 | 0.503 | **Fail** |
| Turn-100 state | 1.000 | 0.970 | 0.783 | **Pass** |

At the fixed 0.5 threshold, the turn-100 validation confusion matrix is 17 true positives, 46
true negatives, zero false positives, and 13 false negatives. Its specificity is 1.000,
sensitivity 0.567, and Brier score 0.118. The model therefore transfers conservatively: it misses
some later scalers but does not call any held-agent non-scaler positive.

The opening model reverses from strong discovery ranking to below-random validation ranking. This
closes current opening geometry as a workforce-recipe selector; tuning its threshold cannot repair
the failed held-agent AUC.

## Mechanism at turn 100

The transferred signal is not a simple idle-bank threshold. In both partitions, later scalers have
less deposited score and wood at turn 100, but much more renewable activity:

| Turn-100 mean | Discovery later / no later | Validation later / no later |
|---|---:|---:|
| Own bank score | 39.25 / 49.10 | 28.53 / 55.48 |
| Own bank wood | 2.31 / 9.19 | 0.70 / 10.46 |
| Own successful plants | 12.06 / 7.26 | 8.57 / 7.57 |
| Own harvested amount | 31.44 / 8.74 | 24.83 / 10.52 |
| Own chops landed | 6.50 / 42.19 | 5.70 / 41.83 |
| Own dropped amount | 31.06 / 15.55 | 25.27 / 17.04 |
| Board plant count | 27.38 / 19.05 | 24.47 / 19.85 |
| Board fruit total | 68.31 / 44.41 | 60.37 / 46.11 |

Large standardized coefficients likewise combine renewable-flow state with worker recipe: harvest
skill, planted PLUM/LEMON, carried PLUM/LEMON, harvested amount, and live LEMON assets are positive;
chop-heavy history/specification is negative. This fits a crop-before-scale economy in which two
productive workers circulate fruit and fund the transaction, rather than workers waiting with a
static surplus.

## Post-result action semantics (descriptive only)

Among the 48 observed third-worker transactions after turn 100 in the broader D61p scheduler
census, 47 execute on the first affordable turn. None is funded by the bank already present at the
start of the affordability window; all 48 have two useful funding contributors. The added worker
is usually hybrid: 32/48 have both harvest and chop skill, ten are wood specialists, and six are
harvest specialists. Specifications are diverse, so the field evidence supports a semantic
capitalization option, not one universal fixed worker genome.

These figures were inspected after the D63a result and are not part of its frozen gate.

## Multilevel conclusion

1. **Opening level:** static geometry does not choose workforce scale across unseen policies.
2. **State level:** a mature turn-100 economy strongly predicts later scale across unseen policies.
3. **Mechanism level:** active renewable throughput, not stockpiled currency, is the dominant
   candidate mechanism.
4. **Action level:** scaling is an immediate, jointly funded transaction whose resulting role is
   usually hybrid but context-dependent.
5. **Controller level:** adding a thresholded `TRAIN` command to the resident remains invalid. The
   decision must live inside a complete controller that preserves crop creation, production work,
   bill funding, and role assignment.

## Decision

Freeze D63b as a no-new-data feature ablation on the 150 eligible rows. Compare the full D63a model
with (a) worker-recipe-only, (b) instantaneous economy without recipe/history, and (c) cumulative
economy flow without recipe/opening features. The cumulative-flow model is primary. If it transfers,
proceed to a prospective state-conditioned capitalization-value protocol. If only the recipe model
transfers, treat D63a as policy-recipe recognition. If only the combined model transfers, represent
the capitalization action as conditional on existing worker roles.

Do not create a candidate or run an active platform experiment from D63a alone.

## Reproducibility

```text
cc197a667ea0287b853ad95174305f2c81ccea51aa2ef29624a85e05b9dca4eb  d63a-agent-held-workforce-transition-protocol-2026-07-21.md
04c71a878440193b2b60c15db9d89853994afb09fa682f760961c0703d9ff9ae  cgauto/analyze_d63a_workforce_transition.py
58be23c7a7e6b5995bcaa5b7a209a412f7a06a0231b66a8c9eb83013b5a98ef2  d63a-agent-held-workforce-transition-2026-07-21.json
```

