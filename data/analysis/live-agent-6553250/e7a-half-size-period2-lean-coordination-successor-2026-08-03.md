# E7a half-size period-2 / lean-coordination successor — 2026-08-03

Status: **SIZE PASS / SEMANTIC PASS / CONSUMED PASS / LIVE-PACKET PASS / FRESH GATE NOT YET LOCKED**

## Exact artifact

- Source: `local_codex_1/e7a-half-size-logical-simplification/focused-yamo-bank-convoy-period2-lean-coordination.rs`
- Bytes: **31,405**, five bytes below the 31,410-byte ceiling
- SHA-256: `9a202242afdac6ffbb463ac4caba1cc803376a90f37066767efabc5bb9584290`
- Exact E7a baseline: 62,820 bytes, SHA-256 `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- Logical reduction: 31,415 bytes, **50.007959%**
- Sacred resident: unchanged SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`

The generated source has no identifier-renaming map, compressed table, encoded program,
macro dispatcher, formatter pass, or whole-source whitespace transformation. It is obtained
by named item deletion and readable replacement. The lexical audit records 568 unique
baseline identifiers, 323 candidate identifiers, 299 preserved identifiers, and explicitly
attributes identifiers lost with the removed blocks. The manifest records
`renaming_mapping: null`.

## Why the previously fresh-qualified source was superseded

The 31,398-byte bank-convoy / spare-door source (`ec4b3140...`) passed the untouched
9,863,000--9,863,042 panel: mean paired margin +5.5465, bootstrap lower +1.2868,
catastrophes 33 -> 26, negative mass 6,493 -> 6,323, all six family means and both seats
positive, worker-two coverage 516/516, and no local period-2 episode >=6.

That source was nevertheless not Arena-ready. Teacher-forcing the exact 25 live E7a games
whose observed movement period-2 run was at least six exposed two defects:

1. Game 897830380 can put worker two, carrying BANANA, on the compact source's reserved
   orchard mother; reserved-cell filtering then leaves an empty action-pair set and the
   selector indexed element zero.
2. After an explicit two-WAIT fallback made the selector total, 10/25 live games still had
   candidate period-2 runs >=6, with a maximum of 31.

The earlier fresh pass remains valid evidence for the earlier exact hash, but cannot qualify
this distinct successor. Its 9,863,000--042 range is consumed and will not be reused.

## Logical repair and size funding

The repair keeps two stable action-slot history records. Before collision reservation, a
third consecutive A-B-A landing is converted to `WAIT`; the other worker is then resolved
normally. The direct over-ceiling implementation is 32,332 bytes and reduces the live
packet maximum period-2 run to two.

The 927-byte funding is ordinary logic deletion/simplification:

- remove the speculative same-item simultaneous-PICK stock reservation and its
  `picked_item` / `stock_compatible` helpers; workers already reserve distinct cells and an
  excess PICK is a legal no-op;
- collapse funded shack evacuation to the official invariant that every shack has a
  walkable door;
- remove the terminal occupied-door prefilter because the shared landing resolver already
  converts an occupied landing to WAIT;
- remove a redundant `plant.health <= 0` test because protocol plant rows contain only live
  trees.

An alternative 31,183-byte simple-clock arm was rejected before the full panel: its 16-game
motion discriminator lost 54.5625 mean margin, increased catastrophes 2 -> 5, and preserved
the first worker-two TRAIN in only 9/16 games. The selected source loses 5.125 on that
engineering discriminator, improves catastrophes 2 -> 1, preserves first TRAIN in 16/16,
and reduces maximum period-2 run 6 -> 2.

## Static and semantic evidence

`rustc --edition=2021 -O` succeeds. Empty input exits zero with zero stdout and stderr.
The exact semantic packet reports `SEMANTIC_FIXTURES_PASS` for ten fixtures, zero malformed
commands, and zero unexpected stderr. It covers the exact E7a PLUM/LEMON near-tie boundary,
exact worker-two bill and fallback choices, persistent wood banking, same-tree and same-cell
coordination, and the feasible/infeasible endgame conversion boundary.

## Consumed development panel

On seeds 9,854,000--9,854,042, both seats and six frozen opponent families, all 516 tasks
and every frozen gate pass:

- mean paired margin **+9.45349**, bootstrap 95% lower **+4.04264**;
- catastrophes **19 -> 13**, negative margin mass **4,138 -> 3,855**;
- family means: compact-gold +7.221, gold-adaptive +8.837, legend-balanced +8.116,
  mybot +9.593, norx-native-three +14.186, resident +8.767;
- seat means: seat 0 +14.023, seat 1 +4.884;
- worker-two coverage 516/516, median delay zero;
- period-2 episodes >=6: **115 -> 0**, candidate maximum three;
- latency p95 ratio 0.851, candidate maximum 1.876 ms;
- zero critical and unclassified failures.

The TSV SHA-256 is `f55004d788020baffa9e159bf7ae84b2afc451f4973793edd0a2b44a6cdbfadf`.
This panel is consumed development evidence, not a transfer verdict.

## Exact live counterexample packet

The read-only evaluator selects all 25 exact `6590141` / `41081503` games with an observed
period-2 run >=6 from the decoded audit, including required game 897832286. It fetches and
decodes replay state in memory without writing the raw cache. The exact candidate completes
7,234 command lines with zero stderr and zero unknown updates; 0/25 games have a candidate
period-2 run >=6 and the maximum is two. Verdict: `LIVE_PERIOD2_PACKET_PASS`.

## Evidence boundary and next action

This exact hash is development-qualified and closes the known live liveness packet. It has
not consumed a fresh panel. A new, collision-audited official-generator range and dedicated
no-range-argument launcher must be committed and pushed before it is opened exactly once.
No Arena action is allowed before that locked run passes every frozen gate and the promotion
preflight succeeds.
