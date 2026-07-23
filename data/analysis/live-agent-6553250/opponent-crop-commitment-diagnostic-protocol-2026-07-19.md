# Opponent-crop commitment diagnostic — frozen protocol, 2026-07-19

## Hypothesis

The arena candidate raises reachable opponent-created trees by only 100 score points on each turn.
It may select such a tree transiently, then allow ordinary candidate ordering to switch the unit
away before first contact.  If this is frequent and materially valuable to the opponent, a bounded
per-unit commitment could amplify provenance-aware denial without a stronger global bonus.

This is distinct from retuning `b100_e6`: the bonus and ETA remain fixed.  The proposed mechanism
would preserve a target already selected by the frozen policy for a short, cargo-safe episode.

## Data and scope

Use all 160 consumed Phase 21 candidate replays, identified by the immutable game IDs in
`phase21-candidate-field-census-2026-07-19.json`.  Fetching results is read-only.  These games are
diagnosis data and can never qualify a future candidate.

For each opponent-created crop, reconstruct official states and candidate commands.  A crop is
"selected" when one of our effective commands:

- MOVEs explicitly to its cell; or
- CHOPs/HARVESTs while the unit occupies its cell.

A selected crop is "abandoned" when it receives at least one such command but no later official
contact before it dies or the game ends.  Attribute its eventual opponent wood/fruit from referee
effects.  Player seats must be handled symmetrically.

## Frozen material-signature gate

Only a diagnostic pass permits a research prototype on already consumed local maps.  All checks
must pass:

1. at least 80 distinct opponent crops are selected across at least 20 games;
2. at least 15% of selected crops are abandoned before contact;
3. abandoned crops occur in at least 10 games and against at least eight opponents;
4. abandoned crops account for at least 10% of opponent wood collected from all selected crops;
5. at least 20 abandoned crops occur in catastrophic games (final margin <= -100).

If any check fails, close short commitment and move to the complete closed-loop economy direction.
Do not change thresholds after inspecting results.

## Authorized follow-up after a pass

A pass authorizes only a research implementation and smoke test on consumed generated seeds
1300--1359.  The first prototype must:

- retain exact `b100_e6` selection as the only way to create a commitment;
- clear on target death, cargo, loss of reachability, direct work, or after at most six turns;
- never alter TRAIN, DROP, PICK, PLANT, MINE, or HARVEST decisions;
- compare against exact resident and exact `b100_e6` on identical maps/opponents;
- open no new seed block, official holdout, candidate packaging, or arena action.

A separate prospective protocol is mandatory before any fresh data.
