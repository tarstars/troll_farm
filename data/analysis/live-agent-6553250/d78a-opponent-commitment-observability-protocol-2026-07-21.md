# D78a opponent-commitment observability audit — frozen protocol (2026-07-21)

## Question

D73--D77 repeatedly find active policies during training but converge or transfer toward balanced.
D71's 72-feature controller sees aggregate inventories, workforce, provenance counts, and its own
source lifecycle, but it does not see a target plant's spatial condition or observable opponent
motion toward it. Does current-field state/history contain a held-opponent signal for imminent
attacks on resident-owned crops that the current controller interface omits?

D78a is a passive, behavior-only representation audit. It cannot claim counterfactual value,
select a policy, open the sealed D61p confirmation split, call TestSession, construct a submission,
or touch Arena.

## Frozen corpus and cohort

Use only the verified open products of immutable snapshot `20260721T105508Z-d61p`. Select every
open game containing stable resident agent `6561795`; the other player is the observed attacker.
Never read `processed/sealed_confirmation/` or any confirmation trajectory.

Group all submissions from one opponent account by `userId`. Assign an opponent account to
discovery when

`SHA256("d78-opponent:" + userId) mod 10 <= 5`,

and to validation otherwise. This partition is outcome-blind and keeps every game from one person
on one side of the fit/evaluation boundary.

## Frozen plant-turn rows and target

Reconstruct exact official states and crop provenance. Retain crops created solely by the resident.
For every turn `t` where such a crop is alive and `t + 8` is within the recorded game, retain the
row iff

`SHA256("d78-row:" + gameId + ":" + x + ":" + y + ":" + t) mod 2 == 0`.

This deterministic thinning is independent of commands and future outcomes. The binary target is
one iff the opponent lands at least one referee-confirmed CHOP on that exact crop during turns
`t+1..t+8`. Also report, but do not fit or gate, whether the opponent delivers the terminal chop in
that horizon.

Rows use state after resolved turn `t`. Historical inputs may inspect only states through `t`.
Future commands, future state, game outcome, score at game end, opponent identity/name/rank, map
seed, and replay split label are forbidden features.

## Frozen observation families

Fit the same L2-regularized logistic model (`lambda=1`, intercept unpenalized, 100 Newton steps) to
each nested feature family using discovery rows only.

### A. Aggregate

A D71-like nonspatial observation: current turn; both scores, workforce counts, deposited
inventories, and carried totals; board plant/fruit totals by species; resident/opponent aggregate
movement/carry/harvest/chop capacity; and resident/opponent worker occupancy counts. It contains no
target coordinates, target condition, unit-to-target distance, or temporal delta.

### B. Spatial snapshot

Aggregate plus target species, age, size, health, fruit, cooldown, normalized coordinates and
shack distances; current attacker/defender shortest path and ETA to the target; nearby/on-target
worker counts; and nearest chop/free-carry capability. It is fully observable from one turn.

### C. Observable history

Spatial snapshot plus six-turn deployable history: target health/fruit change over 1/3/6 turns;
attacker/defender distance change over 1/3/6 turns; number of approach steps; consecutive approach
streak; on-target/near-target exposure; nearest-worker identity persistence; and attacker wood-carry
change. No replay command string enters any feature.

Standardize from discovery means/scales only. Missing historical values use `-1` plus an explicit
missing indicator. Evaluate all three fixed fits on the held-opponent validation rows.

## Frozen integrity and support gates

All must hold before interpreting model quality:

1. every selected replay has exact final inventory, one decoded state per trajectory turn plus the
   initial state, and zero unknown diff updates;
2. every row references a live resident-only crop and obeys the deterministic hash rule;
3. discovery and validation each contain at least 2,000 rows and 100 positive rows;
4. each partition contains at least eight opponent accounts with a positive row and eight with a
   negative row;
5. all feature values and fitted probabilities are finite; and
6. no confirmation product is read.

## Frozen representation gates

Report ROC AUC, balanced accuracy at 0.5, Brier score, top-quintile precision/recall/lift, account
support, and the largest standardized coefficients.

Spatial snapshot adds material deployable signal only if, on held-opponent validation:

1. AUC is at least 0.75 and at least 0.05 above aggregate;
2. Brier score improves by at least 0.005 over aggregate; and
3. top-quintile lift is at least 2.0.

Observable history adds material signal only if, on held-opponent validation:

1. AUC is at least 0.80 and at least 0.03 above spatial snapshot;
2. Brier score improves by at least 0.003 over spatial snapshot;
3. top-quintile lift is at least 2.5; and
4. at least three of the ten largest absolute coefficients are history features.

These are representation gates, not policy-value gates.

## Decision rule

- **History passes:** the next controller interface is a target-conditioned job scorer with
  explicit opponent-motion/plant-damage memory, trained on fresh whole-game outcomes.
- **Spatial passes but history fails:** use a memoryless context-complete target/job scorer; do not
  add another recurrent state merely for opponent commitment.
- **Neither passes with full support:** missing opponent observability is not the current
  explanation. Change the job/action abstraction rather than enlarge state history.
- **Integrity/support failure:** quarantine performance and repair only the failing extraction or
  preserve the insufficient result. Do not alter horizon, thinning, partition, labels, or gates.

Regardless of outcome, D78 cannot create a candidate or authorize platform activity.
