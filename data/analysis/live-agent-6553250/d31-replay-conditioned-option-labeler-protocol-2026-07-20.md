# D31 replay-conditioned official-root option labeler — protocol (2026-07-20)

## Question and sample boundary

Can a 50-turn continuation from an exact official turn-75 root, driven by the opponent's recorded
commands, reproduce the unchanged resident path closely enough to serve as a development
counterfactual labeler for resident versus cold farm?

Use exactly the same first 80 checkpoint rows consumed by D29c/D30.  Read official states through
turn 125 and recorded commands for turns 75--124.  Do not inspect checkpoint rows 81--171.  This is
a read-only development diagnostic and cannot reopen D29b, qualify a candidate, submit code, or
estimate an adaptive opponent response.

## Frozen branches

- **Control:** exact `SecureOrchardBot::new()`, warmed by calling it on official views for turns
  1--74, then run freely from the official turn-75 engine state.
- **Option:** cold exact `OwnershipAwareFarm::new()` from the same turn-75 state.
- **Opponent:** the normalized action commands actually recorded in the official game on turns
  75--124, applied independently to both branches.
- **Engine:** the existing replay-conformant Rust engine.  No state reset is allowed during the
  50-turn continuation.

The official turn-125 view is retained only to score control fidelity.  The option branch is never
compared with the observed resident outcome as if that were its counterfactual truth.

## Recorded fidelity measures

For each game record:

1. whether the warmed resident's turn-75 action vector exactly matches recorded resident actions;
2. exact resident-action agreement over all 50 free-running control turns and the exact-prefix
   length;
3. turn-125 equality for scores, inventories, unit economy, plants, unit positions, and full state;
4. absolute own/opponent score and margin error at turn 125;
5. mechanically applicable recorded-opponent action counts in both control and option branches;
6. fixed-action 50-turn control/option score and margin differences, descriptive only; and
7. all fetch, identity, replay-update, parser, and process failures.

Action vectors discard `MSG`, normalize numeric `PICK`/`PLANT` item IDs to names, preserve order,
and retain the referee's first-command-per-unit semantics.  Opponent applicability checks the
preconditions relevant to the recorded verb in the current branch state; it does not claim that
the opponent would have chosen that command after observing the branch.

## Frozen acceptance gates

The fixed-action labeler is technically eligible for a later prospective validation only if all
of these pass:

1. all 80 games are identity-clean, have at least 125 views, have 50 command pairs, and have zero
   unknown replay updates or process failures;
2. turn-75 warmed-resident action agreement is 80/80;
3. exact control action agreement is at least 95% of 4,000 turns and at least 60/80 games remain
   exact for all 50 turns;
4. at least 72/80 turn-125 control states are material-exact (scores, inventories, unit economy,
   and plants), at least 64/80 have exact unit positions, and at least 60/80 are fully exact;
5. mean absolute control error is at most two points for each player's score and three points for
   margin; and
6. recorded-opponent action applicability is at least 99% in control and 95% in the option branch.

These gates are conjunctive.  Failure closes recorded-command continuation as a D31 label source;
the descriptive branch deltas may not train or calibrate a selector.  Passing would establish only
fixed-action mechanical fidelity and would still require a separately frozen prospective suffix
test before labels could influence a candidate.

## Continuation rule

- **Pass:** diagnose value stability on this consumed prefix, freeze a label construction and
  validation rule, then inspect a disjoint suffix once.
- **Fail:** do not repair movement, relax thresholds, shorten the horizon, reset to official state,
  or select a favorable subset on these games.  Field-native causal labels then require controlled
  common-map A/B games against actual opponents; official-map synthetic continuations remain
  mechanism evidence only.
