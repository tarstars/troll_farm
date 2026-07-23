# D75b two-batch option-sequence horizon repair — frozen protocol (2026-07-21)

## Quarantined defect

D75a's manifest required `turn < 300` and claimed that this guaranteed two successive option
batches. The repeated 9,216-row matrices prove the boundary condition is off by one: three
selected states are at turn 299, and every one of their 16 arms terminates at turn 301 after the
first batch. This creates exactly 48 second-reach failures in each byte-identical matrix.

D75a result SHA-256 is
`17b9ff7353bd3ed1ea439c8daf9aab5c6e0e3acb89279870af132cd6f203a4e2`. Its value is quarantined
and was not computed. Commands, provenance, deposits, crops, reward identity, reconstruction,
grid completeness, and repeat identity all otherwise pass.

## Sole authorized repair

Repeat D75 unchanged except for the necessary manifest eligibility correction:

- replace `turn < 300` with **`turn < 299`**;
- regenerate the outcome-blind six-per-stratum manifest from the same fresh task bank, allowing
  the next smallest identity hashes to replace excluded turn-299 states; and
- require the repaired manifest and analyzer to reject every state with `turn >= 299`.

Maps, partitions, opponents, seats, phases, identity hashing, quota, 72 features, all 16 sequence
arms, renewable fallback, execution, telemetry, 20-thread byte repeat, causal summaries, every
headroom threshold, tie break, and decision rule remain exactly D75a. No D75a terminal score or
sequence value may affect replacement-state selection or any gate.

The unchanged runner is `rust/src/bin/d75_two_batch_option_sequences.rs`. D75b uses new immutable
manifest, matrix, timing, and result artifact names. If all integrity gates now pass, apply D75a's
frozen full and incremental headroom rules. If they do not, quarantine again and repair only the
newly observed mechanical defect.

No branch authorizes a selector, candidate, confirmation, submission, or platform action.
