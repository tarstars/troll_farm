# D167a successor-job acquisition-path recovery — result

Date: 2026-07-27
Verdict: **BANK_SEED is FROZEN-ELIGIBLE** — the acquisition path behind the 135 local natural
PLANT returns and the 21 top-5 field PLANT-return cycles is overwhelmingly PICK-from-shack
(`BANK_SEED`), passing both the field and local gates cleanly.

## Reproducible execution

D167a extends D166's exact entry/return criteria byte-for-byte (new Rust bin
`d167a_successor_acquisition_path.rs`, which reproduces D166's `SuccessorAudit`/production/history
logic verbatim) and reuses the immutable D164 field snapshot and D166's own field cycle selection
(`extract_d166a_field_return_classes.py`, unchanged) via a new extractor
(`extract_d167a_field_acquisition_classes.py`). No platform, YT, sealed-map, candidate, resident, or
Arena action occurred.

- **Local**: the local summary reproduces D166 exactly on all 96 shared columns for all 1,024
  tasks (0 mismatches) — same 237 entries, same 135 natural PLANT returns, identical
  `entry_turn`/`selected_unit_id`/`prior_verb`/`natural_return_*` values — and reproduces D161 on
  every shared terminal/score/workforce/crop/hash field. One-thread wall time 105.70s; 20-thread
  11.68s (9.05×). Summary and per-event trace TSVs are each byte-identical between 1 and 20
  threads.
- **Field**: the extractor reproduces D166's cycle selection exactly — 21 top-5 and 28 rank-6-20
  PLANT-return cycles, same (actor, game) pairs. One-process wall time 20.13s; 20-process 2.96s
  (6.80×). JSONL output is byte-identical between `--jobs 1` and `--jobs 20`.
- All frozen integrity gates pass (see `integrity` in the result JSON): row counts exact,
  bytes identical both panels, `ledger_integrity_ok` true for all 135 local returns and all 49
  field cycles, zero provenance/ownership/history/restart/controller-command violations, zero
  ambiguous partial-spend attributions.
- The Rust suite for the new bin passes 10/10 (4 new ledger/classification tests plus the 3
  regression tests inherited unmodified from D162's frozen module plus 3 D167a-specific behavior
  tests), and the pre-existing D164/D165/D166 Python test suite is unaffected (10/10, unchanged
  since no D164–D166 file was modified).

## A methodological finding discovered during integrity verification

The protocol's integrity item 5 expected carried-seed-at-entry to be zero for field cycles too (by
analogy with D166's local 0/237 fact). It is not: in the field data, 22/49 (44.9%) of PLANT-return
cycles have the eventually-planted seed already in the worker's carry at the moment suppression
resolves — the worker acquires the fruit, *then* suppresses (sometimes an unrelated opponent crop)
while still carrying it, *then* walks on and plants it. A worked example (`gaha`, game 896636060):
turn 118 HARVEST from an **opponent**-owned PLUM (carry capacity 1, so this is the only thing held),
turn 119 CHOP (the suppression event), turns 120–122 MOVE, turn 123 PLANT — zero material waypoints
*after* suppression, yet the true source is unambiguously `OPPONENT_DERIVED`. A window restricted to
`(suppression_turn, return_turn]` cannot see this. The extractor was **repaired** (not the frozen
gates/thresholds) to walk the acquisition ledger over the worker's *entire* relevant history through
the return turn rather than assuming an empty start; this is a completeness fix to data recovery,
not a change to class definitions or thresholds. After the repair, `ledger_integrity_ok` holds for
all 49 field cycles (previously 2 were `EMPTY_LEDGER_INTEGRITY_FAILURE`). Local needed no equivalent
fix: the resident's own carried-seed-at-entry is independently reconfirmed exactly 0/1,024 here
(`ledger_entry_carry_nonzero` totals 0), consistent with D166 — the resident never carries a seed
into suppression, unlike nearly half the observed top-tier field episodes.

## Local class distribution (135 natural PLANT returns)

| Class | Count | Rate |
|---|---:|---:|
| **BANK_SEED** | **135** | **100.0%** |
| FIELD_FRUIT | 0 | 0.0% |
| OPPONENT_DERIVED | 0 | 0.0% |
| OTHER_MIXED | 0 | 0.0% |

Species planted: BANANA 63, APPLE 52, PLUM 12, LEMON 8. Median path length (suppression → return)
16 turns, matching D166's reported median latency exactly. `single_persistent_job` (zero idle turns)
holds in 106/135 (78.5%). 96/135 (71.1%) of these workers have harvest power 0 at entry — physically
incapable of HARVEST — which is mechanically sufficient (not merely correlated) to force BANK_SEED
for those; the remaining 39/135 have harvest power ≥1 yet the resident still overwhelmingly banks
and re-picks rather than reaching a live tree.

## Field class distribution

| Class | Top-5 (of 21) | Top-5 rate | Ranks 6–20 (of 28, descriptive) |
|---|---:|---:|---:|
| **BANK_SEED** | **15** | **71.4%** | 25 (89.3%) |
| FIELD_FRUIT | 1 | 4.8% | 2 (7.1%) |
| OPPONENT_DERIVED | 5 | 23.8% | 1 (3.6%) |
| OTHER_MIXED | 0 | 0.0% | 0 (0.0%) |

BANK_SEED top-5 support: agents `delineate`, `gaha`, `norxondor_gorgonax`, `viewlagoon` (4/5 — all
except `MSz`, whose one PLANT-return cycle is FIELD_FRUIT); both seats present. Ranks 6–20 are
reported descriptively only (not part of the frozen gate) and independently show the same
dominance: BANK_SEED 25/28 (89.3%) across 9 distinct agents, both seats.

## Gate evaluation (frozen, rule 3)

**Field gate (top-5 PLANT returns only, 21 cycles):**

| Class | ≥60% rate | ≥4/5 agents | Both seats | Field gate |
|---|---:|---:|---:|---|
| **BANK_SEED** | 71.4% ✓ | 4/5 ✓ | ✓ | **PASS** |
| FIELD_FRUIT | 4.8% ✗ | 1/5 ✗ | ✗ | fail |
| OPPONENT_DERIVED | 23.8% ✗ | 3/5 ✗ | ✓ | fail |
| OTHER_MIXED | 0.0% ✗ | 0/5 ✗ | ✗ | fail |

**Local gate (≥90 of 135 natural PLANT returns):**

| Class | Count | Local gate |
|---|---:|---|
| **BANK_SEED** | **135** | **PASS** |
| FIELD_FRUIT | 0 | fail |
| OPPONENT_DERIVED | 0 | fail |
| OTHER_MIXED | 0 | fail |

**BANK_SEED is the only class passing both gates simultaneously.** No rescue, threshold
adjustment, or entry-condition change was made after seeing these numbers; the gates are exactly
those frozen in the protocol before this run.

## Verdict (frozen rule 3)

BANK_SEED (PICK a deposited seed from the shack, then PLANT) is **FROZEN-ELIGIBLE**: it clears the
field gate (≥60% of top-5 PLANT returns, ≥4/5 top agents, both seats) and the local gate (≥90/135).
This does not by itself authorize a hand-written D168 successor controller, a candidate, Arena, or
submission — per the protocol, freezing a D168 causal successor option would still require its own
resident-fallback causal test (activation, parity, mean value, own-score protection, family/seat
breadth, tail safety), exactly as D164→D165→D166's chain required at each step. D167a is a support
audit, not that test.

Two qualifications for whoever designs that test:
1. The acquisition is not "the worker's own dropped fruit specifically" — the shack pool is
   fungible; BANK_SEED only says the seed came from the deposited inventory, not which teammate or
   turn produced it.
2. Field OPPONENT_DERIVED (23.8% of top-5, both seats, 3/5 agents) is real and non-trivial —
   opportunistic carry-through-suppression from an opponent-owned tree — but it fails the field
   dominance threshold and has zero local support (0/135); it is closed as a distinct successor
   class by this run, not merged into BANK_SEED.

## Determinism

| Product | 1 unit | 20 units | SHA-256 match |
|---|---:|---:|---|
| Local summary TSV (1,024 rows) | 105.70s | 11.68s | ✓ `a2a3c6fe…759c` |
| Local event-trace TSV (6,445 rows) | (same run) | (same run) | ✓ `03ebd3e4…0994` |
| Field JSONL (49 rows) | 20.13s | 2.96s | ✓ `d2be0f43…82b5` |

All three determinism pairs are byte-identical (SHA-256 verified both directions), satisfying
frozen requirement 4.

## Reproducibility

- protocol: `037c25934de83fbc5ede010d6b8dba28973b4d8f68b9e06635b2a529955274e6`;
- lock: `2ae7cae9543b364298d0be104d127e261f73f83a746e730967c6ccb35ae4b377`;
- Rust runner (`rust/src/bin/d167a_successor_acquisition_path.rs`):
  `fdd0e985304e9fac8fc725c349141f472a941379eccfbd83b23b0497976a1032`;
- field extractor (`cgauto/extract_d167a_field_acquisition_classes.py`):
  `231ae0d9e71e793b576b8010b43508bbd088f47bac6067dc5f0ccd8292e3761c`;
- analyzer (`cgauto/analyze_d167a_successor_acquisition_path.py`):
  `ec5dfe09a9cf739823d2486768f37fd34b206ab88e311eeb651ba0728e21e39e`;
- local summary rows (jobs20, 1,024 rows): `a2a3c6fec2c87f740903ad875d8b2cb943a0120ac161ed4c928a34718e57759c`;
- local event-trace rows (jobs20, 6,445 rows): `03ebd3e410696a4650bc0f390912e64c84e5bd14473f86711e473ff2ee780994`;
- field rows (jobs20, 49 rows): `d2be0f43e7b3e5d696be8e1dfa254dfafbbbbd32b4082d19102d2414027782b5`;
- reference inputs: D161 `144d8f880be8eb58e19e1ef0a3547c04280dac8644340628b60101c1c47c988b`;
  D166a local `30d294bcaf620ddff3932e8d153b8315572b198192a9532d84e899ca44c16e9f`; D166a field
  `a6fe0d28199d2ad201fdaf75441bded0c50cc6de8c1e402479ad4769da990091` (all three unchanged from
  D166's own freeze, reverified byte-for-byte before this run).

Row counts: local 1,024 tasks / 237 entries / 135 natural PLANT returns; field 49 rows (21 top-5 +
28 rank-6-20); local event-trace 6,445 rows. Full machine-readable detail (per-class agent/seat
breakdowns, all integrity booleans, both determinism SHA pairs) is in
`d167a-successor-acquisition-path-result.json`.
