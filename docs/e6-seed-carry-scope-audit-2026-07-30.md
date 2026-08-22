# E6 seed-carry decision scope audit

Date: 2026-07-30

## Registered premise

E6 says “which seed to carry and when to drop it” has never been examined as a decision
class.

## Frozen audit question

Do existing exact-resident and field records already identify, implement, and causally
price seed acquisition/carry timing and species choice strongly enough to bind E6?

This is a read-only scope audit. It may not create a controller, new seed range, source
variant, simulator batch, candidate, or Arena action.

## Decision rules

- `VOID_PREMISE_DUPLICATE` if existing work covers acquisition path, pre/post-carry
  timing, species selection, terminal displacement, both seats, and opponent breadth, and
  explicitly closes retuning.
- `NARROWED` only if an exact live decision remains outside those records and has a
  bounded action grammar not owned by N4 or prior rollout-option work.
- `OPEN` only if the “never examined” premise is substantially true.

## Evidence registry

- D167 acquisition-path protocol/result and B3.3 field re-powering.
- D168 bounded BANK_SEED protocol/lock/result and its tests.
- Phase 1–5 renewable/pre-seed closures.
- D89/D93 seed-factory and bridge failures where relevant.
- Current `docs/CONSTRAINTS.md`, `docs/BACKLOG.md`, and live ledger.

## Integrity

Quote exact recorded numbers and distinguish field description from causal local value.
Do not infer that a field motif is beneficial. Preserve D168's “timing, not action”
interpretation and the existing option-interface closure.
