# Opponent-crop harvest-on-contact diagnostic — frozen protocol, 2026-07-19

## Hypothesis

The Phase 21 mechanism proved that provenance-aware priority can move our workers onto
opponent-created crops, but the normal economy candidate set contains only chop and bank actions.
Even the harvest-capable starter therefore CHOPs a ripe opponent crop when it reaches one.  A
single harvest before the ordinary chop loop could steal a seed, temporarily empty the crop, and
deny part of the opponent's compounding supply.

This is not a generic renewable-supply loop and not a retune of `b100_e6`.  It neither creates nor
protects our own mother tree.  The first possible intervention is a one-action, provenance-aware
rewrite only after the frozen policy has already placed an empty harvest-capable unit on a ripe
opponent crop and selected CHOP.

## Data and scope

Use all 160 consumed Phase 21 candidate replays identified by
`phase21-candidate-field-census-2026-07-19.json`.  Fetching game results is read-only.  These arena
games are diagnosis data and can never qualify a candidate.

For each opponent-created crop, reconstruct official pre-action states and effective unit
commands.  Record at most its first direct harvest-on-contact opportunity, defined by all of:

- our effective command is `CHOP` while standing on that crop;
- the crop is alive and has at least one visible fruit;
- the acting unit has positive harvest power and free carry capacity; and
- the crop was attributed exclusively to the opponent.

Record visible and collectable fruit, whether one harvest would empty the crop, the actual wood
gained by the displaced CHOP that turn, later opponent harvest activity, game outcome, opponent,
and player seat.  This exact-state diagnostic does not assume counterfactual routing.

## Frozen material-signature gate

A research prototype on already consumed generated seeds is permitted only if every check passes:

1. at least 80 distinct crops qualify across at least 30 games and 12 opponents;
2. the opportunities expose at least 80 immediately collectable fruit in total;
3. at least 40 opportunities would completely empty the crop;
4. at least 60 opportunities displace a CHOP that gained no wood on that turn;
5. at least 40 qualifying crops are later harvested by the opponent, accounting for at least 60
   opponent fruit in the replay; and
6. at least 25 qualifying crops occur in catastrophic games (final margin <= -100).

If any check fails, close harvest-on-contact and proceed to the bounded complete-economy policy
representation smoke.  Do not modify these thresholds after inspecting the result.

## Authorized follow-up after a pass

A pass authorizes only a research implementation and paired local tests on consumed generated
seeds 1300--1359.  The first prototype must:

- retain exact opponent-crop provenance and the exact `b100_e6` bonus/ETA settings;
- activate only when the ordinary selected action is CHOP on the currently occupied, ripe,
  opponent-created crop;
- harvest at most once per crop generation, only with empty cargo and positive harvest power;
- leave TRAIN, movement to the crop, target assignment, all non-crop work, and every opponent-crop
  threshold unchanged;
- compare exact resident, exact `b100_e6`, and the harvest residual on identical maps/opponents;
- open no new seed block, official holdout, candidate packaging, controlled platform game, or
  arena submission.

Even after a pass, implementation requires a separate prospective protocol before fresh data.
The prototype is rejected if it gains fruit but loses robust score or wood: denial must pay for
the displaced chop and banking detour.
