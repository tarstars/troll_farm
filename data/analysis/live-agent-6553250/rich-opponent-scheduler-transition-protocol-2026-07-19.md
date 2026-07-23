# Rich-opponent scheduler transition study — frozen protocol, 2026-07-19

## Question

What repeated late scheduler mechanism lets immediate worker-rich Legend opponents remain close
through turn 100 and then add roughly 300 score, 80 wood, and one to two workers beyond all local
proxy families?

This is observational replay reconstruction on consumed games.  It cannot estimate the causal
value of copying an action and cannot qualify a candidate.

## Immutable cohort and split

Use exactly the 21 old-zoo-uncovered games labeled
`rich3plus:farm_wood:train_now` in
`field-continuation-coverage-2026-07-19.json`.  Fetch their immutable results read-only and decode
the actual arena opponent, not our candidate.  Reuse the frozen SHA-256 assignment: 12 discovery,
9 confirmation.  Derive mechanism hypotheses only from discovery; confirmation reports the same
predefined statistics without changing categories or thresholds.

## Measurements

For each exact opponent trajectory:

1. successful TRAIN turn, workforce stage, spec, cost, starting-bank affordability, first
   affordable turn, and distinct funding contributors;
2. each worker's spawn turn/spec and issued MOVE/HARVEST/PLANT/CHOP/DROP/PICK/MINE actions in
   phases 1--50, 51--100, 101--150, 151--200, 201--250, and 251--300;
3. consecutive non-MOVE productive-action transitions per worker, especially
   HARVEST→PLANT, PLANT→HARVEST, PLANT→CHOP, CHOP→DROP, and DROP→HARVEST/CHOP;
4. multi-role workers: at least three issued HARVEST and three issued CHOP actions; and
5. referee-confirmed score, wood, workers, successful plants, harvested fruit, chops, and dropped
   items at turns 50, 100, 150, 200, 250, and final, plus interval increments/rates.

Integrity requires all 21 exact game IDs, decoded/command turn equality, no unknown diff update,
and every successful spawned worker matched to a TRAIN spec.  Referee-confirmed effects remain
the outcome source; issued commands describe scheduler intent only.

## Frozen replicated-mechanism tests

Report these four candidate mechanisms separately.  A mechanism is eligible for v2 only if its
check passes in both discovery and confirmation:

- **Front-loaded scale:** median third-worker spawn turn <=100 and at least 60% of games finish
  with four or more workers.
- **Coordinated later funding:** among successful TRAINs after the first, at least 50% have two or
  more distinct workers contributing a useful DROP or resource-gaining action since the previous
  TRAIN.
- **Hybrid workers:** at least 50% of trained workers have both harvest power and chop power, and
  at least 40% of workers with 50+ active turns meet the multi-role action definition.
- **Late renewable loop:** turns 101+ contribute at least 45% of final successful plants and at
  least 45% of final wood, while both HARVEST→PLANT and CHOP→DROP appear in at least 60% of games.

The thresholds are mechanism discriminators, not performance gates.  Multiple mechanisms may
pass or fail.

## Stop and continuation rules

- Encode only mechanisms that pass unchanged in both partitions into one frozen v2 scheduler.
- If no mechanism replicates, cluster the 21 games by opponent and scheduler signature; a single
  universal rich proxy is then rejected.
- Do not tune transition thresholds, map-specific labels, or action counts on confirmation.
- No generated seeds, arena games, submission, candidate packaging, or resident change.
