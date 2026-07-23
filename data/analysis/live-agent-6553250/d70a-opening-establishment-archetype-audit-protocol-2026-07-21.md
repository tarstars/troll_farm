# D70a opening-establishment archetype audit protocol (2026-07-21)

## Question

Does the D69 later-scaler phase share one or two small, executable first-crop transactions that can
be tested as bounded opening prefixes returning to exact D40, or is first-crop behavior too
policy-specific to justify another hand-built treatment?

D70a is an outcome-blind behavior/geometry audit. It does not estimate value, replay recorded
commands as counterfactuals, train a policy, construct a candidate, or perform a platform action.

## Frozen population and inputs

Use the exact D69 rows and the same verified open D61p snapshot
`20260721T105508Z-d61p`. The primary population is the 46 D63 `later_scaler` appearances (16
discovery, 30 validation). Report the same measurements for the 104 eligible non-scalers as a
negative control. Preserve agent-held partitions and never read scores, ranks as outcomes, or any
confirmation product.

Require exact D69 identity, turns, first/second TRAIN turns, crop milestones, sole-creator
attribution, final inventories, and zero unknown replay updates.

## Frozen transaction reconstruction

For the first sole-created crop of each selected player, record only facts observable by its birth:

1. birth turn, fruit species, creator unit ID, worker ordinal/spec, and own worker count;
2. relation to worker-two creation: `crop_before_worker2`, `same_turn`, or
   `worker2_before_crop`;
3. seed provenance from the creator's most recent positive cargo acquisition of that species:
   `bank_pick`, `board_harvest`, or `unresolved`;
4. own/opponent shack-door distance, player-favored status, water adjacency, and whether the cell
   satisfies the broad D40 source domain (own distance < opponent distance and own distance <= 4);
5. first own renewable receipt from that generation, opponent contact, death, harvested units,
   and whether it yields a receipt before worker three; and
6. whether its species matches each predeclared coefficient-free rule: largest deposited fruit
   bank; largest nonnegative fruit surplus after reserving D40's fixed first-producer bill
   `[5 PLUM, 5 LEMON, 2 APPLE, 0 BANANA]` (falling back to largest bank); and BANANA when
   available, otherwise largest bank. Evaluate the bank in the state immediately before the seed
   acquisition; unresolved provenance uses the state immediately before crop birth. Ties use
   PLUM, LEMON, APPLE, BANANA order.

Same-turn receipt/planting is not sequential reinvestment. Ambiguous creations and unmatched
births cannot enter the archetype catalog.

## Frozen archetype catalog and nomination

An opening transaction is `early` when its crop is born by turn 10. Catalog signatures are the
Cartesian product of worker-two relation and seed provenance; species and cell geometry are
reported attributes, not extra signature degrees of freedom.

Sort signatures by descending minimum discovery/validation count, then total count, then label.
A signature is eligible only if it has:

- at least 3 discovery and 5 validation appearances;
- at least 2 source agents in each partition;
- at least 70% first-generation renewable-receipt-before-worker-three rate in each partition; and
- at least 70% broad-D40-source-domain placement in each partition.

Select at most the first two eligible signatures. The pair passes the coverage gate only if its
union covers at least 60% of all later scalers in each partition. Separately choose a deployable
species rule only if one predeclared rule matches at least 50% of nominated appearances in each
partition. Rank species rules by descending minimum partition match rate, then total matches, then
rule label. These are behavior-support gates, not value claims.

## Decision rule

- If transaction coverage and a species rule pass, freeze one fresh official-map causal preflight:
  exact D40 versus each nominated bounded prefix, with no parameter tuning after the first result.
- If transaction coverage passes but no species rule passes, the opening requires a learned or
  enumerated species choice; do not test a hand-picked source.
- If transaction coverage fails, close minimal hand-built opening establishment and move directly
  to a closed-loop opening policy portfolio.
- If integrity fails, repair attribution only and repeat unchanged.

Any later causal prefix must create at most one initial source, must return to exact D40 immediately
after the transaction, and must not reopen the rejected multi-worker farm-first or permanent
turn-75 farm controllers. D70 itself authorizes no fresh seed outcomes, PPO, TestSession, Arena,
submission, or resident replacement.
