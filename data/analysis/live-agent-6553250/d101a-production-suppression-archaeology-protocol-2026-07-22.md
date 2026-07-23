# D101a top-policy production/suppression archaeology protocol

Frozen: 2026-07-22, before computing any D101 action-lineage result.  
Purpose: decide whether the next controller should schedule renewable production and
opponent-crop suppression as concurrent, worker-separated roles.

## Fixed input and population

Use only the manifest-verified open products of immutable snapshot
`20260721T105508Z-d61p`. Never open a `confirmation` product.

The actor population is fixed without outcomes:

- the ten source appearances of each snapshot rank 1--20 agent (`200` appearances);
- every open appearance of resident agent `6561795` (`165` appearances);
- top-policy cohort: ranks 1--5 (`50` appearances);
- reference cohort: ranks 6--20 (`150` appearances).

An actor/game occurrence may appear only once. Scores and margins are descriptive endpoints and
must not affect inclusion, lineage, cohort assignment, or any gate.

## Reconstruction

Decode every replay to exact per-turn states and reconstruct unit commands against state changes.
Track each plant generation independently: initial plants are `natural`; every later birth is
attributed to the actor, opponent, ambiguous, or unknown from the successful PLANT command. A
plant reborn on the same cell is a new generation.

For each actor occurrence record:

- crop births by origin and successful actor HARVEST/CHOP actions by origin;
- distinct opponent-created generations successfully chopped and their first-contact latency;
- successful PLANT, own-origin HARVEST, and opponent-origin CHOP by worker ordinal and workforce;
- final workers, training count, score, margin, and action timing;
- whether production and suppression overlap temporally.

The fixed game-level indicators are:

- `own_creation`: at least one successful actor PLANT;
- `own_reaping`: at least one successful HARVEST from an actor-created generation;
- `opponent_suppression`: at least one successful CHOP on an opponent-created generation;
- `creation_and_suppression`: both `own_creation` and `opponent_suppression`;
- `renewal_and_suppression`: both `own_reaping` and `opponent_suppression`;
- `role_separated`: in a multiworker game, one worker performs an own-loop action (successful
  actor PLANT or actor-origin HARVEST) and a distinct worker performs a successful opponent-origin
  CHOP;
- `strict_role_separated`: one worker both plants and reaps actor-origin crops while a distinct
  worker suppresses an opponent-created crop;
- `temporally_overlapped`: an opponent-origin CHOP occurs between the actor's first successful
  PLANT and last actor-origin HARVEST, inclusive.

## Frozen integrity gates

All must pass:

1. exactly 200 top-20 source appearances, exactly ten per source agent, 50 rank-1--5
   appearances, 150 rank-6--20 appearances, and 165 resident appearances;
2. all 365 actor/game occurrences are unique and none belongs to a sealed split;
3. decoded turn count equals trajectory turn count in every occurrence;
4. zero unknown state-diff updates, unknown or ambiguous crop births, unassigned cargo deltas,
   missing worker ordinals, or spawn/TRAIN disagreements;
5. one-worker and multiworker action attribution accounts for every successful actor material
   action used by the study;
6. one-process and twenty-process result rows are byte-identical.

Any integrity failure invalidates the study; it is not an unfavorable mechanism result.

## Frozen mechanism gates

For each rank-1--5 agent compute rates over its ten fixed appearances, except role separation,
whose denominator is that agent's multiworker appearances. An agent supports the architecture if
all four conditions hold:

1. `own_creation` in at least 80% of games;
2. `opponent_suppression` in at least 50% of games;
3. `creation_and_suppression` in at least 40% of games;
4. `role_separated` in at least 30% of multiworker games.

The architecture is warranted only if at least three of the five top agents support it. The
stricter renewal, temporal-overlap, generation-coverage, worker-ordinal, rank-6--20, resident, and
outcome summaries are diagnostic and may refine a later implementation, but may not rescue a
failed conjunction.

## Prospective decision

- If the conjunction passes, D102 may implement one coherent complete scheduler with explicit
  producer and suppressor ownership. It must preserve renewable work while allocating a distinct
  worker to opponent crops; a target bonus or isolated one-action override is ineligible.
- If it fails, close concurrent suppression as the next architecture. Use the replay evidence to
  choose between a production/capitalization scheduler and an online trajectory controller, but
  do not tune these gates or fit a selector on D101 outcomes.

D101 is read-only archaeology. It cannot nominate a resident, authorize a submission, expose the
sealed confirmation set, or reopen a closed D96--D100 representation.
