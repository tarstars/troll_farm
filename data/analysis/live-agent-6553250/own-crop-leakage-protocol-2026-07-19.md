# Resident own-crop leakage — frozen diagnostic protocol, 2026-07-19

## Question

Does the exact resident plant enough opponent-capturable supply that changing only the placement
of already-selected PLANT actions is a plausible baseline-preserving candidate?

This diagnostic uses the 131 consumed exact-resident Phase 21 control games.  It does not infer a
counterfactual outcome and cannot by itself authorize a submission.

## Frozen attribution

Decode all official turns with zero unknown state diffs.  Reuse the existing successful-plant
provenance logic with player roles inverted so that exclusively resident-created crops are the
unit of analysis.  Attribute each side's CHOP wood and HARVEST fruit, birth-time unit ETA, and
shack distance.

Classify crop geometry from shack distance at birth:

- `resident_favored`: resident distance is at least two cells shorter;
- `contested`: absolute distance difference is at most one; and
- `opponent_favored`: opponent distance is at least two cells shorter.

Report all games and separately wins, ordinary losses, and catastrophic losses.  Primary leakage
is opponent wood divided by total attributed wood from resident crops.  Also report opponent
contact/capture games, fruit leakage, and geometry-specific rates.

## Frozen eligibility gates

All must pass before a private-placement candidate is built:

1. all 131 fixed games fetch and decode, with no unknown updates and at least 500 exclusively
   resident-created crops;
2. opponents collect at least 15% of all attributed wood from resident crops;
3. catastrophic losses leak at least 8 opponent wood per game from resident crops;
4. opponent-favored/contested crops account for at least 60% of leaked opponent wood; and
5. at least 20 games contain opponent wood capture from a resident crop.

## Stop rule

- **Pass:** implement an exact-fallback placement residual that changes only a PLANT destination
  when an equally reachable resident-favored empty cell exists; audit first divergences on the
  official prefixes before any prospective transfer.
- **Fail:** own-crop placement is not a large enough field lever.  Do not tune distance cutoffs;
  move to a distinct provenance-aware denial mechanism.

No fresh game, submission, candidate source, or resident change is allowed.

