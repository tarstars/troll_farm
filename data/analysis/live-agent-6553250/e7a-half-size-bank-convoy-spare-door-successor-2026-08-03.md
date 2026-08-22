# E7a half-size bank-convoy / spare-door successor — 2026-08-03

Status: **DISTINCT SIZE PASS / SEMANTIC PASS / CONSUMED PASS / FRESH GATE LOCKING**

## Exact artifact

- Source: `local_codex_1/e7a-half-size-logical-simplification/focused-yamo-bank-convoy-spare-door-orchard.rs`
- Bytes: **31,398**, twelve bytes below the 31,410-byte ceiling
- SHA-256: `ec4b31408e963e0647d934e19bed7cc91d881f0a5d84717a295e3ad62426d9b2`
- Exact E7a baseline: 62,820 bytes, SHA-256 `97bfe71e...`
- Logical reduction: 31,422 bytes, **50.019102%**
- Sacred resident: unchanged SHA-256 `fff6669b...`

The source is generated from the exact baseline by named item deletion/replacement.  No
formatter, whole-source whitespace pass, identifier renamer, encoder, compressed table, or
macro dispatch was used.  The mechanical lexical audit finds 568 unique baseline identifiers,
326 candidate identifiers, and 303 preserved identifiers.  The 265 removed identifiers follow
the declared deleted/replaced items.  The 23 introduced identifiers are readable replacement
names such as `orchard_mother`, `orchard_command`, `fruit_kind`, `moves`, `needs`, and `stock`;
the manifest records no rename mapping.

## Why the first locked successor failed

The earlier 31,337-byte structural specialization was positive on its consumed panel but failed
the first fresh block because of two distinct implementation simplifications.

1. On root 9,854,062, seat 1 against compact-gold, both wood carriers emit `WAIT` from turns
   94--300.  The bank selector ranked remaining travel *turns*.  A faster rear worker therefore
   won the shared-door target, landed on the slower front carrier, and the conflict resolver
   pinned both.  Ranking wood carriers by remaining cells instead creates a front-to-back bank
   convoy while preserving persistent wood commitment.
2. On root 9,854,065 the live baseline creates and reaps an APPLE orchard on an empty home door
   while a different home door contains a natural tree.  The simplified source incorrectly
   disabled the orchard when *any* home door had a tree.  Broadly allowing mixed-door orchards
   was unsafe: consumed root 9,854,042 has only two doors and regressed by 116 mean margin.  The
   successor therefore preserves all-empty two-door orchards but allows a mixed-door orchard
   only with at least three home doors, leaving one spare route after the natural tree and chosen
   mother are accounted for.

These are categorical mechanics repairs, not threshold tuning.  The only additional deletion is
an impossible `plant.size <= 0` branch; live protocol plant rows have size at least one.

Rejected diagnostics support the narrow choice.  Restoring the full forecast was broadly harmful
on the rejected block (mean -5.576, lower -13.76, negative mass 5,522, 244 long period-2
episodes).  A broad door-harvest composition lost 29.29 mean with 42 catastrophes.  A fail-closed
APPLE lifecycle had positive mean but failed lower-bound and negative-mass gates.  Requiring three
doors for every orchard destroyed a valuable all-empty two-door case.  None was retained.

## Static and semantic evidence

Standalone optimized compilation succeeds; empty input exits zero with no stdout or stderr.
The exact semantic packet passes all ten fixtures with zero malformed commands and zero stderr:

- exact E7a focus below, at, and above the `PLUM - LEMON <= 8` boundary;
- exact-baseline worker-two bill and fallback choices;
- persistent wood banking (`MOVE`, `MOVE`, `DROP`);
- one live assignment per tree and one landing per cell;
- feasible turn-295 conversion retained and infeasible turn-296 conversion rejected.

The 16-game motion discriminator has candidate mean delta -4.5625, catastrophes 2 -> 1,
identical first training in 16/16, and maximum period-2 target run 6 -> 4.  It is an engineering
smoke, not value evidence.

## Consumed and prior-block diagnostics

On consumed seeds 9,854,000--042, both seats and six families (516 tasks), every frozen gate
passes:

- mean paired margin **+9.03295**, bootstrap lower **+3.78876**;
- catastrophes **19 -> 12**, negative mass **4,138 -> 3,853**;
- six/six family means and both seat means positive;
- worker-two coverage 516/516 with median delay zero;
- period-2 episodes >=6: **115 -> 0**, candidate maximum four;
- latency p95 ratio 0.845, candidate maximum 1.900 ms;
- zero critical and unclassified failures.

Replaying the already-opened, previously rejected seeds 9,854,043--085 is diagnostic only.  It
also passes now: mean **+9.07946**, lower **+1.05233**, catastrophes 19 -> 12, negative mass
4,385 -> 3,968, all families and seats positive, and no long period-2 episode.  This confirms
that the two observed mechanisms are closed, but it cannot serve as a new transfer gate because
the block was opened before this successor existed.

## New untouched gate boundary

The next one-shot gate reserves official-generator seeds **9,863,000--9,863,042**, 43 maps ×
both seats × six frozen families = 516 paired tasks.  Before reservation, exact seed-token scans
found no occurrence in live docs, coordination records, source scripts, or tracked history, and
no matching external artifact filename.  The range is outside all recorded consumed, reserved,
and sealed blocks, including 9,852,000--063, 9,854,000--127, 9,857,000--127,
9,858,000--031, 9,859,000--127, 9,860,000--511, 9,861,000 selection material, and sealed
9,862,000--063.

The dedicated launcher exposes no seed-range arguments and transforms the reviewed runner only
by replacing its two bounded range constants.  Compilation was checked without generating a map.
At this report point, **no seed in 9,863,000--042 has been generated or inspected**.  The range,
source, evaluator, runner transformation, thresholds, task count, families, seats, bootstrap
seed, and one-shot rule must be committed and pushed before execution.

## Evidence boundary

Consumed and prior-block results are development/diagnostic evidence.  The new block is an
untouched engineering transfer gate, not an Arena-rating predictor.  No Arena action is allowed
unless every frozen gate passes on the locked run and the exact live-counterexample liveness
packet remains clean.
