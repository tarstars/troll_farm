# Complete-economy supply ownership diagnostic — frozen protocol, 2026-07-19

## Question

The top complete-economy genome adds 46.45 own wood but also 59.97 opponent wood against adaptive
Gold, losing 47.93 margin relative to resident.  Is that counterexample caused primarily by
adaptive Gold converting trees that **we planted**, or by a broader trajectory change in which
both sides accelerate their own/natural supply?

This distinction precedes implementation.  Direct capture supports an access-control/private-farm
grammar.  Mutual acceleration instead calls for opponent-relative supply throttling or earlier
liquidation; making already-near-shack cells marginally more private would not address it.

## Fixed diagnostic

- Use only the already consumed complete-economy discovery seeds 0--29, both seats, against
  `GoldElite::adaptive()`: 60 common cells.
- Replay exact resident and the fixed top genome `lean_m2c2h0k2` on each initial state.
- Attribute every newly successful planted cell to the issuing side by comparing pre/post-step
  plant sets and successful PLANT attempts.
- Attribute positive worker wood-carry deltas on effective CHOP commands to the tree provenance at
  the worker's pre-step cell: natural, resident-created, or opponent-created.
- Record trees created, wood captured by creator and rival, unassigned wood, scores, inventories,
  and terminal turn.  Simultaneous/ambiguous effects remain unassigned rather than guessed.
- This is diagnosis on consumed local maps.  It cannot select a candidate, open confirmation
  seeds, or authorize an arena write.

## Integrity gates

1. exactly 60 resident and 60 farm rows on the same seed/seat grid;
2. all games finish under the corrected terminal rule without panic;
3. at least 95% of positive CHOP wood-carry deltas receive a known tree provenance;
4. candidate and opponent successful plant attribution has no multiply claimed birth cell.

## Causal branch rule

Call the failure **direct supply capture** only if all integrity gates pass and both:

- at least 50% of the farm-induced opponent wood-carry increase over resident is wood obtained from
  farm-controller-created trees; and
- adaptive Gold captures at least 20% of all wood obtained from farm-controller-created trees.

Otherwise close private placement as the primary explanation and classify the residual from the
measured decomposition: opponent-created supply, natural supply, or attribution remainder.  Do not
tune the 50%/20% thresholds or the farm radius on these games.

## Next move

- **Direct capture passes:** design a new private-supply grammar with a path-distance ownership
  constraint before any outcome sweep.
- **Direct capture fails:** design opponent-relative supply throttling/liquidation; retain the
  productive controller only as a diagnostic substrate, not a candidate.
