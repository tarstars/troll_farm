# D75a two-batch option-sequence integrity result (2026-07-21)

## Verdict

**Quarantine before value and repair only the horizon predicate.** D75a's `turn < 300`
eligibility rule does not guarantee two executable batches. Three selected states occur at turn
299; all 16 sequences in each terminate after their first batch, producing exactly 48 second-reach
failures per matrix.

No sequence advantage, oracle, headroom gate, label, or candidate was computed. The only
authorized change is D75b's outcome-blind replacement of `turn < 300` with `turn < 299`; every
other arm, map, split, quota, threshold, and decision rule remains frozen.

## Evidence

Both 9,216-row matrices are byte-identical at SHA-256
`bbe39518fa83b81b8eaf38a9cc0a4a371cebb80a632b5796821bf161f295e4e6`.

- complete 576 x 16 grids, zero duplicates or missing rows;
- exact task, turn, feature-bit hash, and balanced replay reconstruction;
- zero command, provenance, deposit-prediction, crop, or reward-identity failures;
- 332/332 represented balanced tasks have consistent terminal continuations;
- 9,168/9,216 rows execute both batches;
- the 48 failures are exactly sample IDs 83, 223, and 423, all at turn 299;
- every failed arm terminates at turn 301 after its first requested mode;
- the repeats finish in 6:54.66 and 7:06.51 while sharing all 20 logical cores.

The failed condition is therefore neither nondeterminism nor option legality. It is a single
off-by-one horizon assumption in manifest eligibility.

## Repair

D75b preserves this result and its inputs immutably, excludes every state with `turn >= 299`, and
regenerates each late stratum by the same outcome-blind identity hash. D75a maps are not consumed
for value because analysis stopped at integrity.

## Artifacts

- protocol: `d75a-two-batch-option-sequence-protocol-2026-07-21.md`;
- manifest SHA-256:
  `9c9df68f166f3528bd9aa8e84c952a1502f37d96a32f736a8c31ebbafe29026f`;
- repeated matrices SHA-256:
  `bbe39518fa83b81b8eaf38a9cc0a4a371cebb80a632b5796821bf161f295e4e6`;
- quarantined machine result SHA-256:
  `17b9ff7353bd3ed1ea439c8daf9aab5c6e0e3acb89279870af132cd6f203a4e2`;
- repair protocol: `d75b-two-batch-option-sequence-repair-protocol-2026-07-21.md`.
