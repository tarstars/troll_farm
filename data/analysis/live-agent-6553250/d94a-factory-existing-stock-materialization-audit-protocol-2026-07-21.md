# D94a factory existing-stock materialization audit — frozen protocol

Date: 2026-07-21  
Status: frozen before execution; telemetry-only, consumed maps

## Motivation

D93a proves that D89 never banks a third-worker bill. D55--D68 already close static source floors,
exact deficit-vector source building, fixed existing-source leases, single-source placement, and
late deposited-seed redundancy on the D40 substrate. The remaining narrower discriminator is
whether D89's board state already contains enough ripe non-BANANA fruit to materialize the bill,
so that a new bridge would need only harvest/bank existing fruit and mine IRON rather than invest
scarce currency into new sources.

This audit changes no command and uses only consumed maps `9,914,032--9,914,047`, both seats, all
eight opponents, with exact resident and D89 controls. Fresh maps, policy treatments, TRAIN,
source creation, and platform actions remain closed.

## Frozen accounting

At each two-worker pre-command state, use the balanced `(2,2,0,2)` bill from D93a. Available stock
for PLUM, LEMON, and APPLE is deposited bank + own carried units + all currently ripe board fruit
of that species. Available IRON is bank + own carried IRON; unmined terrain is not counted as
stock. Record:

- full post-stock affordability;
- fruit-only materializability, requiring all PLUM/LEMON/APPLE coordinates and more than 20 turns
  remaining, while allowing IRON to remain missing;
- first fruit-materializable turn and longest consecutive window;
- minimum simultaneous post-stock deficit and its exact vector/turn; and
- maximum observed available stock for each bill coordinate.

Counting all ripe board fruit is deliberately optimistic: a failure is a hard impossibility for a
pure existing-stock bridge, while a pass only permits a causal test and does not assume that every
fruit can be won or banked.

## Integrity gates

1. One-thread and 20-thread rows are byte-identical and contain 512 rows / 256 pairs.
2. Every field shared with D89 and D93 matches exactly, including action and state hashes.
3. Post-stock deficits are nonnegative, fruit-materializable turns are bounded by two-worker
   turns, and first/run counters are internally consistent.

## Warrant for a materialization treatment

A D94b existing-stock/mining bridge may be designed only if D89 satisfies all of:

1. at least 128/256 tasks have a fruit-materializable turn;
2. each opponent family has at least eight reached tasks;
3. median first materializable turn is at most 220;
4. at least half of reached tasks have a two-turn or longer window; and
5. at least 96 reached tasks reduce the optimistic post-stock vector to IRON-only at some state.

If this fails, do not add another source/materialization hand rule. Move to a complete opening
architecture learned or reconstructed from a diversified later-scaler rather than grafting worker
three onto yaichi's two-worker BANANA economy.

